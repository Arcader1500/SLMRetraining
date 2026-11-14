# SLMRetraining — Clinical JSON Extraction Fine-Tuning

Fine-tuning `google/gemma-3-270m-it` with FP32 LoRA (`r=16`, `α=32`) to convert unstructured clinical notes into **strict, machine-parseable 10-section clinical JSON**—with reproducible dataset cleaning, frozen validation contracts, and before/after evaluation.

> **Interactive report:** Open [`docs/clinical_sft_process_and_results.html`](./docs/clinical_sft_process_and_results.html) in any browser for the full process walkthrough, loss curve, 4-way benchmark, and per-case explorer.  
> **Detailed technical briefing:** [`docs/TRAINING_AND_EVAL_BRIEFING.md`](./docs/TRAINING_AND_EVAL_BRIEFING.md).

---

## Key Results (`v2` 30-Case Frozen Validation Set)

| Model | Decoding | Raw JSON Valid | Exact 10/10 Top-Level Keys | Strict Value F1 | Soft Value F1 | Budget Hits (`2048`) | Mean Tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| `google/gemma-3-270m-it` (base) | `rp_1.00` (greedy) | `0 / 30` (0.0%) | `0 / 30` (0.0%) | `0.51%` | `0.87%` | `10 / 30` | `1,240.3` |
| `google/gemma-3-270m-it` (base) | `gen_rp_1.08` | `0 / 30` (0.0%) | `0 / 30` (0.0%) | `0.49%` | `2.09%` | `2 / 30` | `764.8` |
| **`finetuned_v2`** (3 epochs) | `rp_1.00` (greedy) | `25 / 30` (83.3%) | `25 / 30` (83.3%) | `18.02%` | `29.61%` | `3 / 30` | `667.3` |
| **`finetuned_v2`** (3 epochs) | **`gen_rp_1.08`** | **`28 / 30` (93.3%)** | **`28 / 30` (93.3%)** | **`18.93%`** | **`30.74%`** | **`2 / 30`** | **`604.9`** |

- **Precision & hardware:** `float32` (FP32) on Google Colab Tesla T4 (`15 GiB` VRAM; `~8.34 GiB` peak backward VRAM). FP16 triggers activation overflow on Gemma-3 on Turing (`sm_75`).
- **Decoding:** `GeneratedOnlyRepetitionPenalty(1.08)` penalizes only post-prompt generated tokens, preventing repetition loops without distorting clinical terms in the source note.

---

## Repository Structure

```text
SLMRetraining/
├── notebooks/                          # Active v2 Colab notebook pipeline
│   ├── 01_baseline_eval.ipynb          # Base model inference & contract creation
│   ├── 02_finetune.ipynb               # 3-epoch FP32 LoRA training
│   └── 03_eval_and_compare.ipynb       # Fine-tuned eval & 4-way comparison
├── scripts/
│   └── prepare_v2_dataset.py           # Deterministic v2 dataset cleaning & splitting
├── clinical_sft/                       # Standalone CLI pipeline package
│   ├── common.py
│   ├── prepare.py
│   ├── train.py
│   └── evaluate.py
├── prepared_clinical_dataset/          # Frozen dataset splits (v1 & v2)
│   ├── 900825a06d38a006/               # v1 dataset
│   └── eeff5efa1619f198/               # v2 cleaned dataset (1,325 train / 30 val)
├── results_v2/                         # Saved v2 artifacts (baseline, adapter, comparison)
├── docs/                               # Documentation & interactive HTML dashboard
│   ├── clinical_sft_process_and_results.html
│   ├── TRAINING_AND_EVAL_BRIEFING.md
│   ├── CLINICAL_PIPELINE.md
│   └── SESSION_HANDOFF.md
├── tests/                              # Unit tests (no GPU or downloads required)
├── archive/                            # Legacy v1 notebooks & Phase 0/1 runs
├── pyproject.toml
└── requirements-clinical.txt
```

---

## How to Run

Two independent pipelines exist in this repository. **Do not mix artifacts** between the Notebook pipeline and the CLI pipeline—their dataset formats and protocols differ.

### Prerequisites
- Hugging Face account with accepted **Gemma** license (`google/gemma-3-270m-it`) and a read token (`HF_TOKEN` or `hf auth login`).
- A CUDA GPU (e.g., Google Colab Tesla T4) for model inference and training.

---

### Option A: Colab Notebook Pipeline (`v2` — Primary)

1. **Prepare the `v2` dataset locally (CPU-only):**
   ```bash
   python scripts/prepare_v2_dataset.py
   ```
   Outputs the deterministic `v2` split (`1,325` train / `30` validation) under `prepared_clinical_dataset/eeff5efa1619f198/`.

2. **Run the notebooks in order on a Colab GPU runtime:**
   Upload `prepared_clinical_dataset/eeff5efa1619f198/` (or its zip) to `/content` on the Colab runtime, then execute:
   1. [`notebooks/01_baseline_eval.ipynb`](./notebooks/01_baseline_eval.ipynb) — Evaluates the base model under `rp_1.00` and `gen_rp_1.08` and writes `comparison_contract.json`.
   2. [`notebooks/02_finetune.ipynb`](./notebooks/02_finetune.ipynb) — Runs 3-epoch FP32 LoRA training (`498` steps) and saves the best adapter (`checkpoint-498`).
   3. [`notebooks/03_eval_and_compare.ipynb`](./notebooks/03_eval_and_compare.ipynb) — Evaluates the fine-tuned adapter against the frozen baseline contract and generates `summary_comparison.csv`, `case_comparison.csv`, and `showcase_examples.md`.

---

### Option B: CLI Pipeline (`clinical_sft`)

Use a separate Python 3.12 or 3.13 environment (or a fresh Colab runtime) with `requirements-clinical.txt`:

```bash
python -m pip install -r requirements-clinical.txt
hf auth login
```

Run from the project root:

```bash
# 1. Prepare and freeze dataset
python -m clinical_sft.prepare --train-rows 1500 --eval-cases 10 --max-length 4096

# 2. Dry-run label & initial-loss check (no optimizer steps)
python -m clinical_sft.train --dry-run --output runs/clinical_label_check

# 3. Train a 60-step LoRA pilot
python -m clinical_sft.train --steps 60 --output runs/clinical_pilot

# 4. Evaluate base vs adapter
python -m clinical_sft.evaluate --adapter runs/clinical_pilot/adapter
```

See [`docs/CLINICAL_PIPELINE.md`](./docs/CLINICAL_PIPELINE.md) for full CLI flags, precision behavior, and output details.

---

## Local Tests

Run the unit test suite (requires no GPU, model weights, or network downloads):

```bash
python -m unittest discover -s tests -v
```
