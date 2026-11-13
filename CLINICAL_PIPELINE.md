# Clinical JSON fine-tuning pilot

Run these commands from the project root in a **separate Python 3.12 or 3.13 environment**, or a fresh Colab runtime. The existing project/lockfile has a different dependency stack; use the dedicated requirements below rather than `uv sync`. A GPU is needed for a practical training run. Preparation only downloads the tokenizer and dataset.

```bash
python -m pip install -r requirements-clinical.txt
hf auth login
```

Use a read token from the Hugging Face account that accepted the Gemma model license. `HF_TOKEN` in the remote runtime also works. No Google API key is used. In VS Code with Colab, run commands on the remote runtime, for example `!python -m clinical_sft.prepare` in a cell. Upload the `clinical_sft/` package and run from its parent directory; a locally visible workspace is not automatically on the Colab filesystem.

## 1. Prepare the data

```bash
python -m clinical_sft.prepare --train-rows 1500 --eval-cases 10 --max-length 4096
```

The script inspects the first 1,500 training rows, not 1,500 accepted examples. It freezes dataset/model revisions (reusing `baseline_evaluation/generation_config.json` if available), escapes literal control characters in JSON strings, and rejects unresolved syntax, duplicate keys, non-finite constants, unexpected top-level schemas, and targets without any non-placeholder values. It does not infer or rewrite medical facts. It canonicalizes valid targets to compact JSON, so token lengths will differ from the original audit.

It folds the system instruction into the user turn and adds the same short JSON instruction in training and evaluation. It does not include a placeholder-filled schema. Assistant labels include the entire answer and its turn terminator; prompt/padding labels are `-100`. Oversized examples are rejected, never truncated or packed. Note duplicates are removed within/across train and validation. This exact-note check does not detect paraphrased duplicates or patient-level overlap.

Validation is a deterministic seed-42 selection of 10 usable rows from the dataset's validation split, independent of training. This is a **new comparison protocol**, not the original baseline selection/prompt. Evaluate both base model and adapter with the provided evaluation script.

Outputs: `runs/clinical_data/manifest.json`, clean cases, tokenized examples, and a rejection report. These files contain clinical text. Keep the frozen directory unchanged for comparison; preparation refuses to overwrite a nonempty directory.

## 2. Check actual labels and initial loss

```bash
python -m clinical_sft.train --dry-run --output runs/clinical_label_check
```

Inspect `label_checks.json`: decoded labels should start with the answer JSON and end with its turn terminator, with no user note included. This also loads the model and verifies a finite initial loss. It takes **no optimizer steps**; it does not establish that backward/training memory will fit.

## 3. Train a pilot

```bash
python -m clinical_sft.train --steps 60 --output runs/clinical_pilot
```

This uses LoRA rank 16, batch size 1, gradient accumulation 8, gradient checkpointing, and assistant-only loss. Sixty steps is a pilot, not a convergence claim. Training uses Transformers `Trainer` with explicit precomputed labels, avoiding TRL version-specific preprocessing. It saves an adapter, versions/configuration, training logs, and held-out loss. Validation loss is measured on the same small evaluation set; reserve a separate test set if using it for repeated tuning decisions.

`--precision auto` selects native BF16 on supported CUDA GPUs and FP32 otherwise. It never selects FP16. T4 uses FP32, which may be slower and require more memory. If training runs out of memory, choose a capable GPU or prepare a new dataset directory at a shorter context and inspect the rejection report; do not silently truncate targets. Interrupted training is not resumed automatically; use a new output directory for a new run. There are no periodic adapter checkpoints in this short pilot.

## 4. Compare before and after

```bash
python -m clinical_sft.evaluate --adapter runs/clinical_pilot/adapter
```

Both models receive the same held-out notes, prompt, greedy decoding, precision, and 2,048-token output budget. Per-case outputs/raw token IDs are saved after every case; rerunning the identical evaluation resumes from saved cases. Configuration/data/adapter changes require a new output directory.

Inspect `runs/clinical_comparison/summary.json`, `baseline.json`, and `finetuned.json`. Metrics include JSON validity after removing Markdown fences, key match, empty/truncated responses, and precision/recall/F1 of non-placeholder field/value pairs. All-`None` objects get zero fact score. Values compare case-insensitively with normalized whitespace; array order and duplicate values are ignored. Exact values penalize correct paraphrases, and comparison to references does not establish source faithfulness or clinical accuracy. Manually inspect outputs against their source notes before judging success. There are no paid judge calls.

## Local checks

```bash
python -m unittest discover -s tests -v
```

The tests use no ML dependencies or downloads. They cover conservative JSON repair, rejected ambiguous JSON, assistant boundaries, padding/EOS labels, and field-aware scoring. They do not substitute for the model-backed dry run.
