"""Full-schema v2 cleaning, 5,000 training rows and the frozen v3 100 notes."""
import importlib.metadata
import json
import os
import random
from collections import Counter
from pathlib import Path

from scripts.prepare_v2_dataset import (
    DATASET_ID, DATASET_REVISION, MODEL_ID, MODEL_REVISION,
    MAX_SEQUENCE_LENGTH, FORMAT_INSTRUCTION_V2, clean_reference_v2, digest,
)

POINTER = "latest_v2_5000.json"


def prepare_row(example, split, index, tokenizer):
    """Use the original v2 prompt, full target, token boundary and acceptance rules."""
    messages = example["messages"]
    if [m["role"] for m in messages] not in (
        ["system", "user", "assistant"], ["system", "user", "model"]
    ):
        raise ValueError("Expected a single system/user/assistant conversation")
    system, note, raw = [m["content"] for m in messages]
    if not all(isinstance(v, str) and v.strip() for v in (system, note, raw)):
        raise ValueError("Empty or nontext conversation content")
    answer, repair = clean_reference_v2(raw)
    instruction = system.strip() + "\n\n" + FORMAT_INSTRUCTION_V2
    user = [{"role": "user", "content": instruction + "\n\n" + note}]
    prompt = tokenizer.apply_chat_template(user, tokenize=False, add_generation_prompt=True)
    text = tokenizer.apply_chat_template(user + [{"role": "assistant", "content": answer}], tokenize=False)
    if not text.startswith(prompt + answer):
        raise RuntimeError("Unexpected tokenizer template boundary")
    enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > len(prompt) and b > a]
    if not positions or enc["offset_mapping"][positions[0]][0] < len(prompt):
        raise RuntimeError("Assistant boundary shares a prompt token")
    ids, first = enc["input_ids"], positions[0]
    if len(ids) > MAX_SEQUENCE_LENGTH:
        raise ValueError(f"Complete sequence too long: {len(ids)}")
    return dict(case_id=f"{split}:{index}", source_split=split, source_index=index,
                source_sha256=digest(messages), note_sha256=digest(" ".join(note.casefold().split())),
                repair=repair, system=instruction, note=note, reference=answer,
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": note},
                          {"role": "assistant", "content": answer}], prompt_text=prompt, text=text,
                input_ids=ids, attention_mask=[1]*len(ids), labels=[-100]*first+ids[first:],
                prompt_tokens=first, total_tokens=len(ids), supervised_tokens=len(ids)-first)


def extend_training(original, candidates, excluded_hashes, target=5000):
    """Preserve original rows and consume a frozen candidate order without quality pruning."""
    rows = list(original)
    seen = {r["note_sha256"] for r in rows}
    if len(seen) != len(rows) or seen & excluded_hashes:
        raise ValueError("Original training rows are duplicated or overlap validation")
    logs = []
    for index, build in candidates:
        if len(rows) == target:
            break
        try:
            row = build()
            if row["note_sha256"] in excluded_hashes:
                raise ValueError("Normalized note overlaps validation")
            if row["note_sha256"] in seen:
                raise ValueError("Duplicate normalized training note")
            rows.append(row)
            seen.add(row["note_sha256"])
            logs.append(dict(source_index=index, status="accepted", detail=row["repair"]))
        except (ValueError, KeyError, TypeError) as exc:
            logs.append(dict(source_index=index, status="rejected", detail=str(exc)))
        if len(logs) % 250 == 0:
            print(f"Additional candidates checked: {len(logs)}; training rows: {len(rows)}", flush=True)
    if len(rows) != target:
        raise ValueError(f"Only {len(rows)} eligible rows; exactly {target} required")
    return rows, logs


def build_dataset(root=Path("prepared_clinical_dataset")):
    from datasets import Dataset, DatasetDict, load_dataset
    from transformers import AutoTokenizer
    from huggingface_hub import get_token
    from scripts.prepare_v3_dataset import project

    root = Path(root)
    if (root / POINTER).exists():
        out = root / json.loads((root / POINTER).read_text())["version"]
        manifest = json.loads((out / "manifest.json").read_text())
        for split, sha in manifest["split_sha256"].items():
            assert digest([json.loads(x) for x in (out / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()]) == sha
        print("Reusing frozen prepared run:", out, flush=True)
        return out
    original = [json.loads(x) for x in (root / "eeff5efa1619f198/train.jsonl").read_text(encoding="utf-8").splitlines()]
    old_manifest = json.loads((root / "eeff5efa1619f198/manifest.json").read_text())
    assert len(original) == 1325 and digest(original) == old_manifest["split_sha256"]["train"]
    frozen = [json.loads(x) for x in (root / "e80798edebe5aba5/validation.jsonl").read_text(encoding="utf-8").splitlines()]
    frozen_manifest = json.loads((root / "e80798edebe5aba5/manifest.json").read_text())
    assert len(frozen) == 100 and digest(frozen) == frozen_manifest["split_sha256"]["validation"]
    token = os.environ.get("HF_TOKEN") or get_token()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, token=token, use_fast=True)
    raw_validation = load_dataset(DATASET_ID, revision=DATASET_REVISION, split="validation", token=token)
    raw_train = load_dataset(DATASET_ID, revision=DATASET_REVISION, split="train", token=token)
    validation = []
    for old in frozen:
        row = prepare_row(raw_validation[old["source_index"]], "validation", old["source_index"], tokenizer)
        assert all(row[k] == old[k] for k in ("case_id", "note", "note_sha256", "source_sha256"))
        assert project(json.loads(row["reference"])) == json.loads(old["reference"])
        validation.append(row)
    # Match original v2 eligibility and cross-split exclusion without introducing
    # a new clinical filter. Always protect the frozen development notes too.
    excluded = {r["note_sha256"] for r in validation}
    for index, example in enumerate(raw_validation):
        try:
            excluded.add(prepare_row(example, "validation", index, tokenizer)["note_sha256"])
        except (ValueError, KeyError, TypeError):
            continue
    indices = list(range(1500, len(raw_train)))
    random.Random(42).shuffle(indices)
    candidates = ((i, lambda i=i: prepare_row(raw_train[i], "train", i, tokenizer)) for i in indices)
    train, logs = extend_training(original, candidates, excluded)
    # Exact tokenizer/preparation equivalence for the original rows; never rewrite them.
    for old in original:
        assert prepare_row(raw_train[old["source_index"]], "train", old["source_index"], tokenizer) == old
    splits = dict(train=train, validation=validation)
    cfg = dict(old_manifest["config"], experiment="v2_full_schema_5000", candidate_train_rows=len(raw_train),
               eval_cases=100, transformers=importlib.metadata.version("transformers"),
               datasets=importlib.metadata.version("datasets"),
               training_selection="Preserve original 1325; seeded shuffle of indices >=1500 until 5000 accepted",
               validation_selection="Exact ordered v3 100 IDs and notes; original full v2 targets and prompts",
               excluded_overlap="Eligible normalized validation notes and frozen 100; no near-duplicate/patient grouping established")
    hashes = {s: digest(rows) for s, rows in splits.items()}
    version = digest(dict(config=cfg, splits=hashes))[:16]
    out = root / version
    out.mkdir(exist_ok=False)
    DatasetDict({s: Dataset.from_list(rows) for s, rows in splits.items()}).save_to_disk(str(out / "dataset"))
    for split, rows in splits.items():
        (out / f"{split}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows), encoding="utf-8")
    manifest = dict(version=version, config=cfg, split_sha256=hashes,
                    counts={s: len(rows) for s, rows in splits.items()}, original_train_rows=1325,
                    original_v2_train_sha256=digest(original), frozen_v3_validation_sha256=digest(frozen),
                    case_ids=[r["case_id"] for r in validation],
                    preparation_status_counts=dict(Counter(r["status"] for r in logs)),
                    lengths={s: dict(max=max(r["total_tokens"] for r in rows),
                                    mean=sum(r["total_tokens"] for r in rows)/len(rows),
                                    mean_supervised=sum(r["supervised_tokens"] for r in rows)/len(rows),
                                    total_supervised=sum(r["supervised_tokens"] for r in rows)) for s, rows in splits.items()})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "preparation_log.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
    (root / POINTER).write_text(json.dumps(dict(version=version)), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    return out


if __name__ == "__main__":
    build_dataset()
