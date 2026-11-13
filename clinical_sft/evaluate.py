"""Generate baseline and adapter responses on the same frozen held-out notes."""

import argparse
import importlib.metadata
from pathlib import Path

from .common import (file_hash, load_model, prompt_messages, read_json,
                     score_response, verify_data, write_json)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("runs/clinical_data"))
    parser.add_argument("--adapter", type=Path, default=Path("runs/clinical_pilot/adapter"))
    parser.add_argument("--output", type=Path, default=Path("runs/clinical_comparison"))
    parser.add_argument("--max-new-tokens", type=int, default=2048)
    parser.add_argument("--precision", choices=("auto", "fp32", "bf16"), default="auto")
    args = parser.parse_args()
    if args.max_new_tokens <= 0:
        parser.error("Token budget must be positive")

    import torch
    from peft import PeftModel
    from transformers import AutoTokenizer, set_seed

    manifest = verify_data(args.data)
    run = read_json(args.adapter.parent / "run_config.json")
    if run["manifest_sha256"] != file_hash(args.data / "manifest.json") or run["dry_run"]:
        raise ValueError("Adapter run does not match these prepared data")
    tokenizer = AutoTokenizer.from_pretrained(manifest["model"], revision=manifest["model_revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    cases = read_json(args.data / "validation_cases.json")
    set_seed(manifest["seed"])
    model, runtime = load_model(manifest, args.precision)
    model.config.use_cache = True
    args.output.mkdir(parents=True, exist_ok=True)
    config = {"manifest_sha256": file_hash(args.data / "manifest.json"),
              "adapter_files": {p.name: file_hash(p) for p in args.adapter.iterdir() if p.is_file()},
              "max_new_tokens": args.max_new_tokens, "do_sample": False, "runtime": runtime,
              "versions": {name: importlib.metadata.version(name)
                           for name in ("torch", "transformers", "peft", "datasets", "accelerate")}}
    config_path = args.output / "evaluation_config.json"
    if config_path.exists() and read_json(config_path) != config:
        raise ValueError("Evaluation configuration changed; use a new output directory")
    write_json(config_path, config)
    summaries = {}
    for name in ("baseline", "finetuned"):
        if name == "finetuned":
            model = PeftModel.from_pretrained(model, args.adapter)
        model.eval()
        path = args.output / f"{name}.json"
        results = read_json(path) if path.exists() else {}
        for case in cases:
            key = str(case["index"])
            if key in results:
                continue
            prompt = tokenizer.apply_chat_template(prompt_messages(case["system"], case["note"]),
                                                   tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, add_special_tokens=False, return_tensors="pt").to(model.device)
            prompt_length = inputs.input_ids.shape[1]
            if prompt_length + args.max_new_tokens > model.config.max_position_embeddings:
                raise ValueError(f"Row {key}: prompt plus output budget exceeds model context")
            with torch.inference_mode():
                logits = model(**inputs).logits[:, -1, :]
                if not torch.isfinite(logits).all():
                    raise RuntimeError(f"{name} row {key}: non-finite first-token logits")
                del logits
                generated = model.generate(**inputs, max_new_tokens=args.max_new_tokens,
                                           do_sample=False, pad_token_id=tokenizer.pad_token_id)
            ids = generated[0, prompt_length:].tolist()
            response = tokenizer.decode(ids, skip_special_tokens=True)
            results[key] = {"output": response, "raw_output": tokenizer.decode(ids, skip_special_tokens=False),
                            "token_ids": ids, "generated_tokens": len(ids), "empty": not response.strip(),
                            "hit_token_limit": len(ids) >= args.max_new_tokens,
                            "metrics": score_response(response, case["reference"])}
            write_json(path, results)
            print(name, key, results[key]["metrics"], flush=True)
        selected = [results[str(c["index"])] for c in cases]
        summaries[name] = {"cases": len(selected),
                           "empty_cases": sum(r["empty"] for r in selected),
                           "token_limit_cases": sum(r["hit_token_limit"] for r in selected),
                           "valid_json_cases": sum(r["metrics"]["valid_json"] for r in selected),
                           "exact_key_match_cases": sum(r["metrics"]["exact_key_match"] for r in selected)}
        for metric in ("value_precision", "value_recall", "value_f1"):
            summaries[name]["mean_" + metric] = sum(r["metrics"][metric] for r in selected) / len(selected)
        write_json(args.output / "summary.json", summaries)
    print(summaries)


if __name__ == "__main__":
    main()
