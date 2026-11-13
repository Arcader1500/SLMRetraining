"""Download, conservatively clean, and tokenize complete train/validation pairs."""

import argparse
from collections import Counter
import json
from pathlib import Path
import random

from .common import (DATASET_ID, MODEL_ID, FORMAT_INSTRUCTION, clean_reference,
                     clinical_values, encode_example, file_hash, read_json, write_json)

REQUIRED_KEYS = {"visit motivation", "admission", "patient information", "patient medical history",
                 "surgeries", "symptoms", "medical examinations", "diagnosis tests", "treatments", "discharge"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runs/clinical_data"))
    parser.add_argument("--train-rows", type=int, default=1500, help="Number of raw training rows to inspect")
    parser.add_argument("--eval-cases", type=int, default=10)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--experiment-config", type=Path,
                        default=Path("baseline_evaluation/generation_config.json"))
    args = parser.parse_args()
    if min(args.train_rows, args.eval_cases, args.max_length) <= 0:
        parser.error("Row counts and maximum length must be positive")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output directory is nonempty; choose a new path")

    from datasets import load_dataset
    from huggingface_hub import HfApi
    from transformers import AutoConfig, AutoTokenizer

    saved = read_json(args.experiment_config) if args.experiment_config.exists() else {}
    if saved.get("model", MODEL_ID) != MODEL_ID:
        raise ValueError("Experiment config uses a different model")
    api = HfApi()
    model_revision = saved.get("model_revision") or api.model_info(MODEL_ID).sha
    dataset_revision = saved.get("dataset_revision") or api.dataset_info(DATASET_ID).sha
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=model_revision, use_fast=True)
    model_config = AutoConfig.from_pretrained(MODEL_ID, revision=model_revision)
    if args.max_length > model_config.max_position_embeddings:
        raise ValueError("Requested training length exceeds the model context")
    args.output.mkdir(parents=True, exist_ok=True)
    rejected, statuses, seen = [], Counter(), set()
    outputs = {}
    for split in ("train", "validation"):
        print(f"Loading {split} at {dataset_revision}", flush=True)
        dataset = load_dataset(DATASET_ID, revision=dataset_revision,
                               split=f"train[:{args.train_rows}]" if split == "train" else split)
        indices = list(range(len(dataset)))
        if split == "validation":
            random.Random(args.seed).shuffle(indices)
        accepted, encoded_rows = [], []
        for count, index in enumerate(indices):
            try:
                messages = dataset[index]["messages"]
                if [m["role"] for m in messages] not in (
                    ["system", "user", "assistant"], ["system", "user", "model"]):
                    raise ValueError("Unexpected message roles")
                system, note, original = [m["content"] for m in messages]
                if not all(isinstance(t, str) and t.strip() for t in (system, note, original)):
                    raise ValueError("Empty or non-string message")
                reference, status = clean_reference(original)
                obj = json.loads(reference)
                if set(obj) != REQUIRED_KEYS:
                    raise ValueError("Reference top-level keys differ from the clinical schema")
                if not clinical_values(obj):
                    raise ValueError("Reference has no non-placeholder values")
                note_key = " ".join(note.casefold().split())
                if note_key in seen:
                    raise ValueError("Duplicate note within or across train/validation")
                case = {"index": index, "system": system, "note": note,
                        "reference": reference, "reference_status": status}
                encoded = encode_example(tokenizer, case)
                if len(encoded["input_ids"]) > args.max_length:
                    raise ValueError(f"Complete pair exceeds {args.max_length} tokens")
                case["tokens"] = len(encoded["input_ids"])
                accepted.append(case)
                encoded_rows.append(encoded)
                seen.add(note_key)
                statuses[f"{split}:{status}"] += 1
            except ValueError as exc:
                rejected.append({"split": split, "index": index, "reason": str(exc)})
            if (count + 1) % 100 == 0:
                print(f"{split}: inspected {count + 1}, kept {len(accepted)}", flush=True)
            if split == "validation" and len(accepted) == args.eval_cases:
                break
        if not accepted or (split == "validation" and len(accepted) < args.eval_cases):
            raise ValueError(f"Insufficient usable {split} rows")
        write_json(args.output / f"{split}_cases.json", accepted)
        write_json(args.output / f"{split}_tokens.json", encoded_rows)
        outputs[split] = len(accepted)
    write_json(args.output / "rejected.json", rejected)
    manifest = {"model": MODEL_ID, "model_revision": model_revision,
                "dataset": DATASET_ID, "dataset_revision": dataset_revision,
                "max_length": args.max_length, "seed": args.seed,
                "format_instruction": FORMAT_INSTRUCTION, "counts": outputs,
                "reference_statuses": dict(statuses), "rejected": len(rejected),
                "rejection_reasons": dict(Counter(r["reason"] for r in rejected)),
                "files": {p.name: file_hash(p) for p in args.output.glob("*.json")}}
    write_json(args.output / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
