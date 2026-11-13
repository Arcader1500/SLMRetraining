"""Verify answer labels and run a small LoRA fine-tuning pilot."""

import argparse
import importlib.metadata
from pathlib import Path

from .common import file_hash, load_model, pad_examples, read_json, verify_data, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("runs/clinical_data"))
    parser.add_argument("--output", type=Path, default=Path("runs/clinical_pilot"))
    parser.add_argument("--steps", type=int, default=60)
    parser.add_argument("--accumulation", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--precision", choices=("auto", "fp32", "bf16"), default="auto")
    parser.add_argument("--dry-run", action="store_true", help="Inspect labels and check finite loss; no optimizer steps")
    args = parser.parse_args()
    if min(args.steps, args.accumulation, args.learning_rate) <= 0:
        parser.error("Steps, accumulation, and learning rate must be positive")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output is nonempty; use a new path")

    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoTokenizer, Trainer, TrainingArguments, set_seed

    manifest = verify_data(args.data)
    set_seed(manifest["seed"])
    tokenizer = AutoTokenizer.from_pretrained(manifest["model"], revision=manifest["model_revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    examples = read_json(args.data / "train_tokens.json")
    validation = read_json(args.data / "validation_tokens.json")
    for row in examples + validation:
        ids, labels = row["input_ids"], row["labels"]
        if len(ids) != len(labels) or len(ids) > manifest["max_length"]:
            raise ValueError("Bad lengths in prepared examples")
        first = next((i for i, label in enumerate(labels) if label != -100), len(labels))
        if first == 0 or first == len(labels) or labels[first:] != ids[first:]:
            raise ValueError("Expected masked prompt and complete assistant labels")
    args.output.mkdir(parents=True, exist_ok=True)

    def collate(features):
        return {key: torch.tensor(value, dtype=torch.long)
                for key, value in pad_examples(features, tokenizer.pad_token_id).items()}

    previews = []
    for index, row in enumerate(examples[:3]):
        batch = collate([row])
        active = batch["labels"][0] != -100
        previews.append({"index": index, "input_tokens": len(row["input_ids"]),
                         "active_labels": int(active.sum()),
                         "decoded_labels": tokenizer.decode(batch["labels"][0][active].tolist(),
                                                             skip_special_tokens=False)})
    write_json(args.output / "label_checks.json", previews)
    model, runtime = load_model(manifest, args.precision)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(
        task_type=TaskType.CAUSAL_LM, r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    batch = {key: value.to(model.device) for key, value in collate([examples[0]]).items()}
    model.eval()
    with torch.no_grad():
        loss = model(**batch).loss
    if not torch.isfinite(loss):
        raise RuntimeError("Initial loss is not finite; training stopped")
    run_config = {"manifest_sha256": file_hash(args.data / "manifest.json"),
                  "model": manifest["model"], "model_revision": manifest["model_revision"],
                  "steps": args.steps, "gradient_accumulation": args.accumulation,
                  "learning_rate": args.learning_rate, "runtime": runtime,
                  "initial_loss": loss.item(), "dry_run": args.dry_run,
                  "versions": {name: importlib.metadata.version(name)
                               for name in ("torch", "transformers", "peft", "datasets", "accelerate")}}
    write_json(args.output / "run_config.json", run_config)
    print("Label checks saved; initial loss:", loss.item(), "runtime:", runtime, flush=True)
    del batch, loss
    if args.dry_run:
        print("Dry run complete. Use a different output directory for training.")
        return
    training_args = TrainingArguments(
        output_dir=str(args.output), per_device_train_batch_size=1,
        per_device_eval_batch_size=1, gradient_accumulation_steps=args.accumulation,
        max_steps=args.steps, learning_rate=args.learning_rate, warmup_ratio=0.1,
        gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False},
        bf16=runtime["dtype"] == "torch.bfloat16", fp16=False,
        logging_steps=1, logging_nan_inf_filter=False, save_strategy="no", report_to="none",
        seed=manifest["seed"], data_seed=manifest["seed"], label_names=["labels"],
        remove_unused_columns=False)
    class FiniteLossTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            result = super().compute_loss(model, inputs, return_outputs=return_outputs, **kwargs)
            loss = result[0] if return_outputs else result
            if not torch.isfinite(loss).all():
                raise RuntimeError("Non-finite loss; stopped before backward/optimizer update")
            return result

    trainer = FiniteLossTrainer(model=model, args=training_args, data_collator=collate,
                               train_dataset=Dataset.from_list(examples), eval_dataset=Dataset.from_list(validation))
    result = trainer.train()
    metrics = {"train": result.metrics, "validation": trainer.evaluate()}
    trainer.save_model(str(args.output / "adapter"))
    tokenizer.save_pretrained(args.output / "adapter")
    write_json(args.output / "metrics.json", metrics)
    write_json(args.output / "training_log.json", trainer.state.log_history)
    print("Saved adapter and training metrics to", args.output)


if __name__ == "__main__":
    main()
