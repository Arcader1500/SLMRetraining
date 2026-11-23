"""Package the cleaned and verified v3_regenerated_gemini_3_8_flash labels into a versioned prepared dataset (preserving v1/v2/v3)."""
import copy
import importlib.metadata
import json
from pathlib import Path

from scripts.phase_results import ROOT
from scripts.prepare_v2_dataset import (
    DATASET_ID,
    DATASET_REVISION,
    MAX_SEQUENCE_LENGTH,
    MODEL_ID,
    MODEL_REVISION,
    digest,
    load_object,
)
from scripts.prepare_v3_dataset import INSTRUCTION, SCHEMA, schema_valid


def encode_regenerated_row(base_row: dict, new_reference_str: str, tokenizer) -> dict:
    row = copy.deepcopy(base_row)
    obj = load_object(new_reference_str)
    if not schema_valid(obj):
        raise ValueError(f"{row['case_id']} violates 30-path schema_valid")
    answer = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    messages = [{"role": "user", "content": INSTRUCTION + row["note"]}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    text = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": answer}], tokenize=False)
    if not text.startswith(prompt + answer):
        raise RuntimeError(f"Unexpected tokenizer template boundary on {row['case_id']}")
    enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > len(prompt) and b > a]
    if not positions or enc["offset_mapping"][positions[0]][0] < len(prompt):
        raise RuntimeError(f"Assistant boundary shares a prompt token on {row['case_id']}")
    ids, first = enc["input_ids"], positions[0]
    if len(ids) > MAX_SEQUENCE_LENGTH:
        raise ValueError(f"Complete sequence exceeds context budget on {row['case_id']}: {len(ids)}")
    labels = [-100] * first + ids[first:]
    assert len(labels) == len(ids) and any(v != -100 for v in labels[1:])
    row.update(
        reference=answer,
        system=INSTRUCTION,
        prompt_text=prompt,
        text=text,
        messages=[
            {"role": "system", "content": INSTRUCTION},
            {"role": "user", "content": row["note"]},
            {"role": "assistant", "content": answer},
        ],
        input_ids=ids,
        attention_mask=[1] * len(ids),
        labels=labels,
        prompt_tokens=first,
        total_tokens=len(ids),
        supervised_tokens=len(ids) - first,
    )
    return row


def build_packaged_dataset(
    root: Path = ROOT / "prepared_clinical_dataset",
    regen_dir: Path = ROOT / "prepared_clinical_dataset" / "v3_regenerated_gemini_3_8_flash",
):
    from datasets import Dataset, DatasetDict
    from transformers import AutoTokenizer

    frozen_v3 = root / "e80798edebe5aba5"
    old_manifest = json.loads((frozen_v3 / "manifest.json").read_text(encoding="utf-8"))
    old_splits = {
        s: [json.loads(line) for line in (frozen_v3 / f"{s}.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
        for s in ("train", "validation")
    }
    for s in ("train", "validation"):
        assert digest(old_splits[s]) == old_manifest["split_sha256"][s], f"Frozen v3 {s} hash mismatch"

    regen_splits = {
        s: {
            r["case_id"]: r
            for r in (
                json.loads(line)
                for line in (regen_dir / f"regenerated_{s}.jsonl").read_text(encoding="utf-8").split("\n")
                if line.strip()
            )
        }
        for s in ("train", "validation")
    }
    assert len(regen_splits["train"]) == 1325 and len(regen_splits["validation"]) == 100

    # Load local fast tokenizer saved in results_v3/finetuned_v3/adapter (exact same Gemma-3 270M IT rev)
    tok_path = ROOT / "results_v3" / "finetuned_v3" / "adapter"
    tokenizer = AutoTokenizer.from_pretrained(str(tok_path), use_fast=True)
    assert tokenizer.is_fast

    packaged_splits = {}
    for s in ("train", "validation"):
        rows = []
        for base_row in old_splits[s]:
            cid = base_row["case_id"]
            if cid not in regen_splits[s]:
                raise KeyError(f"Missing {cid} in regenerated_{s}.jsonl")
            reg_row = regen_splits[s][cid]
            assert reg_row["note_sha256"] == base_row["note_sha256"], f"note_sha256 mismatch on {cid}"
            rows.append(encode_regenerated_row(base_row, reg_row["reference"], tokenizer))
        packaged_splits[s] = rows

    assert not ({r["note_sha256"] for r in packaged_splits["train"]} & {r["note_sha256"] for r in packaged_splits["validation"]})

    cfg = {
        "schema_version": 3,
        "label_version": "v3_regenerated_gemini_3_8_flash_cleaned",
        "schema": SCHEMA,
        "model": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "dataset": DATASET_ID,
        "dataset_revision": DATASET_REVISION,
        "seed": 42,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "format_instruction": INSTRUCTION,
        "transformers": importlib.metadata.version("transformers"),
        "datasets": importlib.metadata.version("datasets"),
        "source_v3_version": frozen_v3.name,
        "teacher_model": "gemini-3.8-flash",
        "cleaning_and_verification": "deterministic_clean_v3_obj + targeted_strict_schema_repair_304_cases + unified_narrow_scope_symptom_negation",
        "loss": "assistant and closing tokens only",
        "evaluation_role": "development; source-grounded regenerated references, verified programmatic hygiene",
        "leakage_limits": "Exact same 1,325 train IDs and 100 validation IDs/order as e80798edebe5aba5; zero normalized exact-note overlap",
    }
    hashes = {s: digest(rows) for s, rows in packaged_splits.items()}
    version = digest({"config": cfg, "splits": hashes})[:16]
    out_dir = root / version
    out_dir.mkdir(parents=True, exist_ok=True)

    DatasetDict({s: Dataset.from_list(rows) for s, rows in packaged_splits.items()}).save_to_disk(str(out_dir / "dataset"))
    for s, rows in packaged_splits.items():
        (out_dir / f"{s}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )

    manifest = {
        "version": version,
        "config": cfg,
        "split_sha256": hashes,
        "counts": {s: len(v) for s, v in packaged_splits.items()},
        "lengths": {
            s: {
                "max": max(r["total_tokens"] for r in rows),
                "mean": sum(r["total_tokens"] for r in rows) / len(rows),
                "mean_supervised": sum(r["supervised_tokens"] for r in rows) / len(rows),
                "max_supervised": max(r["supervised_tokens"] for r in rows),
            }
            for s, rows in packaged_splits.items()
        },
        "total_supervised_tokens_per_epoch": sum(r["supervised_tokens"] for r in packaged_splits["train"]),
        "total_supervised_tokens_3_epochs": 3 * sum(r["supervised_tokens"] for r in packaged_splits["train"]),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (regen_dir / "packaged_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (root / "latest_v3_regenerated.json").write_text(json.dumps({"version": version}, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    return out_dir


if __name__ == "__main__":
    build_packaged_dataset()
