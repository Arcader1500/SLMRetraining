"""Prepare cleaned & schema-normalized clinical dataset v2 (preserving v1)."""

import hashlib
import importlib.metadata
import json
import os
import random
import re
from collections import Counter
from pathlib import Path

MODEL_ID = "google/gemma-3-270m-it"
MODEL_REVISION = "ac82b4e820549b854eebf28ce6dedaf9fdfa17b3"
DATASET_ID = "AmareshHebbar/clinical-summarizer-sft"
DATASET_REVISION = "4ca20e0a38cc9235045c973b5503d49952fd1fac"
N_TRAIN_ROWS = 1500
N_EVAL_CASES = 30
SEED = 42
MAX_SEQUENCE_LENGTH = 4096

TOP_LEVEL_KEYS = (
    "visit motivation",
    "admission",
    "patient information",
    "patient medical history",
    "surgeries",
    "symptoms",
    "medical examinations",
    "diagnosis tests",
    "treatments",
    "discharge",
)
STRING_KEYS = ("visit motivation",)
DICT_KEYS = ("patient information", "patient medical history", "discharge")
LIST_KEYS = (
    "admission",
    "surgeries",
    "symptoms",
    "medical examinations",
    "diagnosis tests",
    "treatments",
)

FORMAT_INSTRUCTION_V2 = (
    "Extract the clinical facts stated in the note into one JSON object. "
    "Return JSON only, without markdown or commentary. Use these exact top-level fields: "
    + ", ".join(TOP_LEVEL_KEYS)
    + ". For absent information, omit inner subfields, use [] for empty list sections "
    "(admission, surgeries, symptoms, medical examinations, diagnosis tests, treatments), "
    "use {} for empty object sections (patient information, patient medical history, discharge), "
    'and use "None" only for an absent visit motivation. '
    "Do not invent facts or repeat identical entries."
)

MISSING_TOKENS = ("", "none", "null", "unknown", "not provided")


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonstandard JSON constant: " + value)


def load_object(text, strict=True):
    obj = json.loads(
        text,
        strict=strict,
        object_pairs_hook=no_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object")
    return obj


def is_missing_scalar(value):
    if value is None:
        return True
    if isinstance(value, (dict, list)):
        return False
    return " ".join(str(value).casefold().split()) in MISSING_TOKENS


def clean_node(value):
    """Strip missing leaves/dicts recursively and deduplicate list items preserving order."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            cleaned = clean_node(v)
            if cleaned is not None:
                out[k] = cleaned
        return out or None
    if isinstance(value, list):
        out = []
        seen = set()
        for item in value:
            cleaned = clean_node(item)
            if cleaned is None:
                continue
            sig = json.dumps(cleaned, ensure_ascii=False, sort_keys=True)
            if sig not in seen:
                seen.add(sig)
                out.append(cleaned)
        return out or None
    return None if is_missing_scalar(value) else value


def has_nonmissing_value(value):
    if isinstance(value, dict):
        return any(has_nonmissing_value(v) for v in value.values())
    if isinstance(value, list):
        return any(has_nonmissing_value(v) for v in value)
    return not is_missing_scalar(value)


def clean_reference_v2(raw):
    """Parse raw clinical JSON safely, normalize empty-section shapes, and strip missing leaves."""
    text = raw.strip()
    fenced = text.startswith("```") and text.endswith("```")
    if fenced:
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)[:-3].strip()
    try:
        obj = load_object(text)
        repair = "removed_markdown_fence" if fenced else "none"
    except ValueError:
        obj = load_object(text, strict=False)
        repair = "escaped_control_characters" + ("_and_removed_fence" if fenced else "")
    if set(obj) != set(TOP_LEVEL_KEYS):
        raise ValueError("Unexpected top-level schema")

    compacted = {}
    for key in TOP_LEVEL_KEYS:
        val = obj[key]
        if key in STRING_KEYS:
            cleaned = clean_node(val)
            if cleaned is None:
                compacted[key] = "None"
            elif isinstance(cleaned, (str, int, float, bool)):
                compacted[key] = str(cleaned)
            else:
                raise ValueError(f"Expected scalar for {key}, got {type(cleaned).__name__}")
        elif key in DICT_KEYS:
            if is_missing_scalar(val):
                compacted[key] = {}
            elif isinstance(val, dict):
                compacted[key] = clean_node(val) or {}
            else:
                raise ValueError(f"Expected dict or missing for {key}, got {type(val).__name__}")
        elif key in LIST_KEYS:
            if is_missing_scalar(val):
                compacted[key] = []
            elif isinstance(val, list):
                compacted[key] = clean_node(val) or []
            elif isinstance(val, dict):
                cleaned = clean_node(val)
                compacted[key] = [cleaned] if cleaned else []
            else:
                raise ValueError(f"Expected list or missing for {key}, got {type(val).__name__}")

    if not has_nonmissing_value(compacted):
        raise ValueError("Reference contains no nonmissing values")
    canonical = json.dumps(compacted, ensure_ascii=False, separators=(",", ":"))
    assert load_object(canonical) == compacted
    return canonical, repair


def run_self_checks():
    raw_sample = json.dumps(
        {
            "visit motivation": "chest pain",
            "admission": [{"reason": "None", "date": "None"}],
            "patient information": {"age": "54", "sex": "Male", "ethnicity": "None"},
            "patient medical history": {"allergies": "None"},
            "surgeries": "None",
            "symptoms": [{"name": "chest pain"}, {"name": "chest pain"}],
            "medical examinations": [],
            "diagnosis tests": [{"test": "ECG", "result": "normal", "severity": "None"}],
            "treatments": "None",
            "discharge": "None",
        }
    )
    cleaned_s, repair = clean_reference_v2(raw_sample)
    assert repair == "none"
    parsed = json.loads(cleaned_s)
    assert parsed["admission"] == []
    assert parsed["surgeries"] == []
    assert parsed["patient medical history"] == {}
    assert parsed["discharge"] == {}
    assert parsed["patient information"] == {"age": "54", "sex": "Male"}
    assert parsed["symptoms"] == [{"name": "chest pain"}]
    assert parsed["diagnosis tests"] == [{"test": "ECG", "result": "normal"}]
    for invalid in ('{"x": 1,}', '{"x":1,"x":2}', '{"x":NaN}', "[]"):
        try:
            clean_reference_v2(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid JSON was accepted")
    print("clean_reference_v2 self-checks passed.")


def build_dataset(output_root=Path("prepared_clinical_dataset")):
    import pandas as pd
    from datasets import Dataset, DatasetDict, load_dataset
    from huggingface_hub import get_token
    from transformers import AutoTokenizer

    run_self_checks()
    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        raise RuntimeError("Missing HF token.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, token=token, use_fast=True)
    assert tokenizer.is_fast
    raw_train = load_dataset(DATASET_ID, revision=DATASET_REVISION, split=f"train[:{N_TRAIN_ROWS}]", token=token)
    raw_eval = load_dataset(DATASET_ID, revision=DATASET_REVISION, split="validation", token=token)

    logs = []
    comp_stats = {"orig_chars": 0, "clean_chars": 0, "rows": 0}

    def prepare_row(example, split, index):
        messages = example["messages"]
        if [m["role"] for m in messages] not in (
            ["system", "user", "assistant"],
            ["system", "user", "model"],
        ):
            raise ValueError("Expected a single system/user/assistant conversation")
        system, note, raw_answer = [m["content"] for m in messages]
        if not all(isinstance(x, str) and x.strip() for x in (system, note, raw_answer)):
            raise ValueError("Empty or nontext conversation content")
        answer, repair = clean_reference_v2(raw_answer)
        instruction = system.strip() + "\n\n" + FORMAT_INSTRUCTION_V2
        user = [{"role": "user", "content": instruction + "\n\n" + note}]
        prompt = tokenizer.apply_chat_template(user, tokenize=False, add_generation_prompt=True)
        text = tokenizer.apply_chat_template(
            user + [{"role": "assistant", "content": answer}], tokenize=False
        )
        if not text.startswith(prompt + answer):
            raise RuntimeError("Unexpected tokenizer template boundary")
        enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
        positions = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > len(prompt) and b > a]
        if not positions or enc["offset_mapping"][positions[0]][0] < len(prompt):
            raise RuntimeError("Assistant boundary shares a prompt token")
        first_answer = positions[0]
        ids = enc["input_ids"]
        if len(ids) > MAX_SEQUENCE_LENGTH:
            raise ValueError(f"Complete sequence too long: {len(ids)}")
        labels = [-100] * first_answer + ids[first_answer:]
        assert len(labels) == len(ids) and any(v != -100 for v in labels[1:])
        comp_stats["orig_chars"] += len(raw_answer.strip())
        comp_stats["clean_chars"] += len(answer)
        comp_stats["rows"] += 1
        return {
            "case_id": f"{split}:{index}",
            "source_split": split,
            "source_index": index,
            "source_sha256": digest(messages),
            "note_sha256": digest(" ".join(note.casefold().split())),
            "repair": repair,
            "system": instruction,
            "note": note,
            "reference": answer,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": note},
                {"role": "assistant", "content": answer},
            ],
            "prompt_text": prompt,
            "text": text,
            "input_ids": ids,
            "attention_mask": [1] * len(ids),
            "labels": labels,
            "prompt_tokens": first_answer,
            "total_tokens": len(ids),
            "supervised_tokens": len(ids) - first_answer,
        }

    def prepare_split(raw, name):
        result, seen = [], set()
        for i, example in enumerate(raw):
            try:
                row = prepare_row(example, name, i)
                if row["note_sha256"] in seen:
                    raise ValueError("Duplicate normalized note within split")
                seen.add(row["note_sha256"])
                result.append(row)
                logs.append({"split": name, "source_index": i, "status": "accepted", "detail": row["repair"]})
            except (ValueError, KeyError, TypeError) as exc:
                logs.append({"split": name, "source_index": i, "status": "rejected", "detail": str(exc)})
            if (i + 1) % 250 == 0:
                print(f"{name}: {i + 1}/{len(raw)} checked; {len(result)} eligible", flush=True)
        return result

    train_rows = prepare_split(raw_train, "train")
    eval_pool = prepare_split(raw_eval, "validation")
    eval_hashes = {r["note_sha256"] for r in eval_pool}
    for row in train_rows:
        if row["note_sha256"] in eval_hashes:
            logs.append(
                {
                    "split": "train",
                    "source_index": row["source_index"],
                    "status": "excluded_cross_split_duplicate",
                    "detail": "Note appears in validation",
                }
            )
    train_rows = [r for r in train_rows if r["note_sha256"] not in eval_hashes]
    assert train_rows and len(eval_pool) >= N_EVAL_CASES
    eval_rows = random.Random(SEED).sample(eval_pool, N_EVAL_CASES)
    assert not ({r["note_sha256"] for r in train_rows} & {r["note_sha256"] for r in eval_rows})

    prepared = DatasetDict({"train": Dataset.from_list(train_rows), "validation": Dataset.from_list(eval_rows)})
    config = {
        "schema_version": 2,
        "cleaning": "strip_missing_leaves_unify_empty_types_dedupe_arrays",
        "model": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "dataset": DATASET_ID,
        "dataset_revision": DATASET_REVISION,
        "candidate_train_rows": N_TRAIN_ROWS,
        "eval_cases": N_EVAL_CASES,
        "seed": SEED,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "format_instruction": FORMAT_INSTRUCTION_V2,
        "transformers": importlib.metadata.version("transformers"),
        "datasets": importlib.metadata.version("datasets"),
        "tokenizer_add_special_tokens": False,
        "loss": "assistant and closing tokens only",
    }
    content_hashes = {split: digest(prepared[split].to_list()) for split in prepared}
    version = digest({"config": config, "splits": content_hashes})[:16]
    manifest = {
        "version": version,
        "config": config,
        "split_sha256": content_hashes,
        "counts": {split: len(prepared[split]) for split in prepared},
        "eligible_validation_pool": len(eval_pool),
        "repair_counts_saved": dict(Counter(r["repair"] for r in train_rows + eval_rows)),
        "log_status_counts": dict(Counter(r["status"] for r in logs)),
        "cleaning_char_reduction_pct": round(
            (1 - comp_stats["clean_chars"] / comp_stats["orig_chars"]) * 100, 2
        ),
        "lengths": {
            split: {
                "max": max(prepared[split]["total_tokens"]),
                "mean": sum(prepared[split]["total_tokens"]) / len(prepared[split]),
                "mean_supervised": sum(prepared[split]["supervised_tokens"]) / len(prepared[split]),
            }
            for split in prepared
        },
    }

    output_dir = output_root / version
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        prepared.save_to_disk(str(output_dir / "dataset"))
        for split in prepared:
            prepared[split].to_json(str(output_dir / f"{split}.jsonl"), force_ascii=False)
        pd.DataFrame(logs).to_csv(output_dir / "preparation_log.csv", index=False)
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output_root / "latest_v2.json").write_text(json.dumps({"version": version}, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    return output_dir


if __name__ == "__main__":
    build_dataset()
