"""Reduced-schema pilot: preserve the frozen 1,325 training cases, rebuild prompts."""
import copy
import importlib.metadata
import json
import os
import random
from collections import Counter
from pathlib import Path

from scripts.prepare_v2_dataset import (
    DATASET_ID, DATASET_REVISION, MODEL_ID, MODEL_REVISION, MAX_SEQUENCE_LENGTH,
    TOP_LEVEL_KEYS, DICT_KEYS, LIST_KEYS, clean_reference_v2, digest, load_object,
)

SCHEMA = {
    "visit motivation": [], "admission": ["reason"],
    "patient information": ["age", "sex"],
    "patient medical history": ["physiological context"],
    "surgeries": ["Type", "time", "details"],
    "symptoms": ["name of symptom", "location", "time", "details"],
    "medical examinations": ["name", "result"],
    "diagnosis tests": ["test", "result"],
    "treatments": ["name", "dosage", "time", "reaction to treatment"],
    "discharge": ["discharge summary"],
}
INSTRUCTION = (
    "Extract only clinical facts explicitly stated in the supplied note into one JSON object. "
    "Return JSON only, without markdown or commentary. Preserve negation, uncertainty, "
    "historical versus current events, and which findings or doses belong to each event or drug. "
    "Do not infer missing facts or complete cut-off text. Include all ten top-level fields. "
    "The allowed fields and types are: visit motivation is a string; "
    + "; ".join(f"{k} is {'an object' if k in DICT_KEYS else 'an array of objects'} "
                f"with optional fields {', '.join(v)}" for k, v in SCHEMA.items() if v)
    + '. Use [] for empty arrays, {} for empty objects, and "None" for absent visit motivation. '
    "Omit missing inner fields. Do not add other keys or repeat identical entries.\n\nClinical note:\n"
)


def schema_valid(obj):
    if not isinstance(obj, dict) or set(obj) != set(SCHEMA):
        return False
    if not isinstance(obj["visit motivation"], str):
        return False
    for parent, fields in SCHEMA.items():
        if parent == "visit motivation":
            continue
        value = obj[parent]
        if parent in DICT_KEYS:
            if not isinstance(value, dict):
                return False
            entries = [value]
        else:
            if not isinstance(value, list):
                return False
            entries = value
        for entry in entries:
            if not isinstance(entry, dict) or not set(entry) <= set(fields):
                return False
            if any(isinstance(v, (list, dict)) or v is None for v in entry.values()):
                return False
    return True


def project(obj):
    result = {}
    for parent, fields in SCHEMA.items():
        value = obj[parent]
        if parent == "visit motivation":
            result[parent] = value
        elif parent in DICT_KEYS:
            result[parent] = {k: value[k] for k in fields if k in value}
        else:
            if not all(isinstance(item, dict) for item in value):
                raise ValueError(f"Nonobject entry: {parent}")
            # Preserve separate events even if dropping fields makes them identical.
            result[parent] = [selected for item in value
                              if (selected := {k: item[k] for k in fields if k in item})]
    if not schema_valid(result):
        raise ValueError("Projected reference violates allowed keys/types")
    return result


def rebuild(row, tokenizer):
    row = copy.deepcopy(row)
    answer = json.dumps(project(load_object(row["reference"])), ensure_ascii=False, separators=(",", ":"))
    messages = [{"role": "user", "content": INSTRUCTION + row["note"]}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    text = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": answer}], tokenize=False)
    assert text.startswith(prompt + answer)
    enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > len(prompt) and b > a]
    assert positions and enc["offset_mapping"][positions[0]][0] >= len(prompt)
    ids, first = enc["input_ids"], positions[0]
    if len(ids) > MAX_SEQUENCE_LENGTH:
        raise ValueError("Complete sequence exceeds context budget")
    row.update(reference=answer, system=INSTRUCTION, prompt_text=prompt, text=text,
               messages=[{"role": "system", "content": INSTRUCTION}, {"role": "user", "content": row["note"]},
                         {"role": "assistant", "content": answer}],
               input_ids=ids, attention_mask=[1]*len(ids), labels=[-100]*first+ids[first:],
               prompt_tokens=first, total_tokens=len(ids), supervised_tokens=len(ids)-first)
    return row


def self_checks():
    assert len(SCHEMA) + sum(map(len, SCHEMA.values())) == 30
    obj = {k: ("None" if k == "visit motivation" else {} if k in DICT_KEYS else []) for k in SCHEMA}
    obj["symptoms"] = [{"name of symptom": "No fever", "intensity": "absent"}, {"intensity": "mild"}]
    obj["treatments"] = [{"dosage": "5 mg", "frequency": "daily"}, {"dosage": "5 mg", "frequency": "weekly"}]
    original = copy.deepcopy(obj)
    projected = project(obj)
    assert obj == original and projected["symptoms"] == [{"name of symptom": "No fever"}]
    assert len(projected["treatments"]) == 2
    assert not schema_valid({**projected, "extra": {}})
    assert not schema_valid({**projected, "treatments": [{"name": {"bad": "nested"}}]})
    print("v3 projection self-checks passed")


def build_dataset(root=Path("prepared_clinical_dataset")):
    from datasets import Dataset, DatasetDict, load_dataset
    from transformers import AutoTokenizer
    from huggingface_hub import get_token
    self_checks()
    frozen = root / "eeff5efa1619f198"
    old_manifest = json.loads((frozen / "manifest.json").read_text())
    old = {s: [json.loads(x) for x in (frozen / f"{s}.jsonl").read_text(encoding="utf-8").splitlines()]
           for s in ("train", "validation")}
    for s in old:
        assert digest(old[s]) == old_manifest["split_sha256"][s]
    token = os.environ.get("HF_TOKEN") or get_token()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, token=token, use_fast=True)
    train = [rebuild(r, tokenizer) for r in old["train"]]
    assert len(train) == 1325
    excluded_notes = {r["note_sha256"] for r in train + old["validation"]}
    excluded_ids = {r["case_id"] for r in old["validation"]}
    raw = load_dataset(DATASET_ID, revision=DATASET_REVISION, split="validation", token=token)
    pool, logs, seen = [], [], set()
    for i, record in enumerate(raw):
        try:
            messages = record["messages"]
            if [m["role"] for m in messages] not in (["system", "user", "assistant"], ["system", "user", "model"]):
                raise ValueError("Invalid conversation roles")
            if not all(isinstance(m["content"], str) and m["content"].strip() for m in messages):
                raise ValueError("Empty conversation")
            note = messages[1]["content"]
            sha = digest(" ".join(note.casefold().split()))
            cid = f"validation:{i}"
            if sha in excluded_notes or sha in seen or cid in excluded_ids:
                raise ValueError("Duplicate note or previously inspected development case")
            ref, repair = clean_reference_v2(messages[2]["content"])
            row = rebuild(dict(case_id=cid, source_split="validation", source_index=i,
                               source_sha256=digest(messages), note_sha256=sha, repair=repair,
                               note=note, reference=ref), tokenizer)
            seen.add(sha)
            pool.append(row)
        except (ValueError, TypeError, KeyError) as exc:
            logs.append({"source_index": i, "reason": str(exc)})
    validation = random.Random(42).sample(pool, 100)
    assert not {r["note_sha256"] for r in train} & {r["note_sha256"] for r in validation}
    splits = {"train": train, "validation": validation}
    cfg = dict(schema_version=3, schema=SCHEMA, model=MODEL_ID, model_revision=MODEL_REVISION,
               dataset=DATASET_ID, dataset_revision=DATASET_REVISION, seed=42,
               max_sequence_length=MAX_SEQUENCE_LENGTH, format_instruction=INSTRUCTION,
               transformers=importlib.metadata.version("transformers"), datasets=importlib.metadata.version("datasets"),
               source_v2_version=frozen.name, projected_collisions="preserve separate entries",
               missing_identifier_policy="retain verbatim; audit counts", loss="assistant and closing tokens only",
               evaluation_role="development; synthetic references, no clinician adjudication",
               leakage_limits="Normalized exact notes checked against train and prior dev; near duplicates/patient overlap/test not established")
    hashes = {s: digest(rows) for s, rows in splits.items()}
    version = digest({"config": cfg, "splits": hashes})[:16]
    out = root / version
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    DatasetDict({s: Dataset.from_list(rows) for s, rows in splits.items()}).save_to_disk(str(out / "dataset"))
    for s, rows in splits.items():
        (out / f"{s}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows), encoding="utf-8")
    manifest = dict(version=version, config=cfg, split_sha256=hashes, counts={s: len(v) for s,v in splits.items()},
                    eligible_validation_pool=len(pool), validation_rejections=len(logs),
                    lengths={s: dict(max=max(r["total_tokens"] for r in rows),
                                     mean=sum(r["total_tokens"] for r in rows)/len(rows),
                                     mean_supervised=sum(r["supervised_tokens"] for r in rows)/len(rows)) for s,rows in splits.items()})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out / "preparation_log.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
    audit = {}
    identifiers = {"surgeries": "Type", "symptoms": "name of symptom", "diagnosis tests": "test",
                   "treatments": "name", "medical examinations": "name"}
    for s, rows in splits.items():
        counts = Counter()
        for r in rows:
            obj = json.loads(r["reference"])
            for parent, key in identifiers.items():
                counts[parent + "_unnamed_entries"] += sum(key not in item for item in obj[parent])
            for parent in LIST_KEYS:
                sigs = [digest(item) for item in obj[parent]]
                counts["projected_duplicate_entries"] += len(sigs)-len(set(sigs))
        audit[s] = dict(counts)
    (out / "projection_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    sample = random.Random(42).sample(train, 12)
    (out / "reference_review_sample.json").write_text(json.dumps([{k:r[k] for k in ("case_id","note","reference")} for r in sample], ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "latest_v3.json").write_text(json.dumps({"version": version}), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    print("Projection audit:", audit, flush=True)
    return out


if __name__ == "__main__":
    build_dataset()
