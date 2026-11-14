# Clinical JSON Extraction Fine-Tuning Briefing (`gemma-3-270m-it`)

> **Status:** Complete. All three runs (`01_baseline_eval.ipynb`, `02_finetune.ipynb`, `03_eval_and_compare.ipynb`) completed on remote Colab Tesla T4 (`v2-t4`), with saved cell outputs stored locally inside each notebook and artifacts archived under [results_v2/](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/results_v2/).

---

## 1. Project Goal
Fine-tune a compact `270M`-parameter instruction model (`google/gemma-3-270m-it`) to convert unstructured clinical notes into **strict, machine-parseable clinical JSON** across 10 canonical medical sections—without markdown fences, duplicate keys, missing-value bloat, or degenerative decoding loops—and demonstrate clear, reproducible end-to-end improvements over the un-tuned base model on a frozen held-out validation set.

---

## 2. Base Model & Runtime Precision
- **Base model:** `google/gemma-3-270m-it`
- **Pinned Hugging Face revision:** `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3`
- **Hardware:** Remote Google Colab **Tesla T4** (`15 GiB` VRAM)
- **Precision (`dtype`):** **`float32` (FP32)** throughout both training and inference.
  - *Why FP32 instead of FP16/BF16 on T4?* On Turing (`sm_75`), Gemma-3 does not support native BF16 and FP16 triggers activation overflow (`inf`/`nan` logits during generation and backward passes). FP32 fits comfortably within T4 VRAM at `270M` scale (`~8.34 GiB` peak backward VRAM even without gradient checkpointing on the longest `1,651`-token training example).
- **Pinned software stack:** `transformers==4.57.6`, `peft==0.18.1`, `datasets==4.8.5`, `accelerate==1.15.0`, `torch==2.14.1+cu130`.

---

## 3. Source Dataset & Audit Findings (Why Cleaning Was Necessary)
- **Source Hugging Face dataset:** `AmareshHebbar/clinical-summarizer-sft`
- **Pinned dataset revision:** `4ca20e0a38cc9235045c973b5503d49952fd1fac`
- **Initial (`v1` / `900825a06d38a006`) audit findings:**
  1. **Training targets had no literal infinite loops** (`0/1,325` exact duplicate array entries in `train.jsonl`), proving Phase 0 `pilot_02` loops were **greedy decoding (`rp=1.00`) attractors** rather than memorized loop targets.
  2. **Heavy `"None"` placeholder bloat:** `54.3%` of leaf values in `v1` targets were `"None"` placeholders (`avg 79.5` leaves per example), wasting over half of supervised cross-entropy tokens and generation steps on empty scaffolding.
  3. **Four conflicting empty-section encodings** in `v1` references:
     - List sections (`admission`, `surgeries`, `symptoms`, `medical examinations`, `diagnosis tests`, `treatments`) appeared as `[]`, `[all-None dict]`, `"None"` string (`25` `admission`, `22` `surgeries`, `6` `symptoms`, `2` `medical examinations`, `15` `diagnosis tests`, `60` `treatments` rows in `train.jsonl`), or mixed dicts.
     - `discharge` appeared as `"None"` (`33` rows) instead of `{}` (`1,292` rows).
     - Training on contradictory empty schemas caused structural drift and lowered `exact_key_match`.
  4. **Phase 1 decoding ablation proof (`decoding_ablation_10` on 10 frozen `v1` cases):**
     - Switching `pilot_02` (`166` steps, `eval_loss=0.3793`) from pure greedy `rp=1.00` to **generated-only repetition penalty `gen_rp=1.08`** (penalizing only post-prompt generated tokens so note terms are untouched) jumped raw JSON validity from `5/10` → **`9/10`**, cut budget-hit (`2048`-token) loops from `4/10` → **`0/10`**, and raised exact-value F1 from `0.1034` → **`0.1798`** (`58/353` matched facts vs `pilot_01` `34/353` / `0.1187` and `base @ 1.00` `1/353` / `0.0031`).
     - Higher penalty (`gen_rp=1.15`) broke JSON structure (`6/10` valid, `0.0800` F1), establishing `1.08` as the sweet spot.

---

## 4. Dataset `v2` (`eeff5efa1619f198`) Cleaning & Splitting Pipeline
Generated deterministically via [scripts/prepare_v2_dataset.py](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/scripts/prepare_v2_dataset.py) while preserving `v1` (`prepared_clinical_dataset/900825a06d38a006/`) untouched.

### Deterministic Cleaning Rules Applied (`clean_reference_v2`)
1. **Safe syntax normalization only:** Strip outer markdown fences if present; escape unescaped control characters (`strict=False` fallback only); reject duplicate JSON keys, `NaN`/`Infinity`, non-dict roots, or unexpected top-level keys (`no_duplicate_keys`, `reject_constant`).
2. **Canonical 10 top-level schema keys enforced:**
   - **String section:** `visit motivation` → string value, or `"None"` if absent.
   - **Object sections (`DICT_KEYS`):** `patient information`, `patient medical history`, `discharge` → `{}` when empty; omit inner missing subfields.
   - **List sections (`LIST_KEYS`):** `admission`, `surgeries`, `symptoms`, `medical examinations`, `diagnosis tests`, `treatments` → `[]` when empty; omit inner missing subfields inside each item; drop empty `[all-None]` dummy items; deduplicate exact identical array entries while preserving order.
3. **Missing scalar definition:** Normalized whitespace casefolded values in `("", "none", "null", "unknown", "not provided")` or JSON `null` are treated as missing. Every accepted row must retain at least one non-missing clinical value.
4. **Updated prompt alignment (`FORMAT_INSTRUCTION_V2`):** Explicitly instructs the model to emit the 10 exact top-level fields, omit absent inner subfields, use `[]` / `{}` for empty sections, and reserve `"None"` only for absent `visit motivation`.
5. **Strict prompt/target label masking & dedupe:** Deduplicates normalized notes within splits and removes cross-split overlap (`107` excluded cross-split duplicates); sets `labels = -100` on all prompt tokens so loss trains strictly on assistant JSON + end-of-turn tokens.

### Exact Sample Counts & Cleaning Impact (`manifest.json`)
| Metric | Value (`v2` / `eeff5efa1619f198`) | Comparison vs `v1` (`900825a06d38a006`) |
|---|---|---|
| Candidate training rows scanned | `1,500` | Same (`1,500`) |
| **Final clean training samples** | **`1,325`** | Same (`1,325`) after `seed=42` & cross-split dedupe |
| Eligible validation pool | `2,834` | Same (`2,834` from `3,000` raw val rows) |
| **Held-out validation eval samples** | **`30`** (`seed=42`) | Expanded **3×** (up from `10`) for lower metric variance |
| Log summary (`train` + `val` pool) | `4,266` accepted, `234` rejected, `107` cross-split excluded | — |
| Control-char/fence repairs in saved split | `1,018` none, `337` escaped control chars | — |
| **Target JSON character reduction** | **`32.6%` shorter** across accepted pool | (`v1` train avg `79.5` leaves → `36.5` leaves, `-54.1%`) |
| **Train sequence lengths (tokens)** | Mean **`1,055.3`** (mean supervised `487.7`), max **`1,651`** | Down from mean `1,211.1`, max `1,949` (`-298` max toks) |
| **Validation sequence lengths (tokens)** | Mean **`1,061.9`** (mean supervised `491.8`), max **`1,271`** | Down from mean `1,207.0`, max `1,382` |
| Split SHA-256 (`train` / `validation`) | `f3bc7f7bfdc3fbec...` / `5a5f86399b90ade8...` | Independently frozen |

---

## 5. Tuned Training & Decoding Choices
- **Decoding protocol (validated in Phase 1 & evaluated in both notebooks):**
  - Compare `rp_1.00` (pure greedy `do_sample=False`) vs `gen_rp_1.08` (`GeneratedOnlyRepetitionPenalty(1.08, prompt_length)`, penalizing only post-prompt tokens so clinical entities in the source note aren't penalized).
  - Kept `max_new_tokens=2048` and `dtype=float32`.
- **Fine-tuning recipe (`02_finetune.ipynb`, 3 epochs on `1,325` cleaned `v2` rows):**
  - LoRA `r=16`, `lora_alpha=32`, `lora_dropout=0.05`, all 7 attention + MLP linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
  - `per_device_train_batch_size=1`, `gradient_accumulation_steps=8` (effective batch `8`, `~498` optimizer steps across `3` epochs).
  - `learning_rate=2e-4`, `lr_scheduler_type="cosine"`, `warmup_ratio=0.08`, `weight_decay=0.01`, `max_grad_norm=1.0`.
  - **`gradient_checkpointing=False`**: Benchmarked empirically on `v2-t4` longest `1,651`-token row (`8.34 GiB` peak VRAM out of `15 GiB`, vs `5.95 GiB` with checkpointing), delivering a **4× speedup** (`0.90s/microstep` vs `3.66s/microstep`) with identical FP32 math.
  - Epoch-end evaluation & best-checkpoint selection (`eval_strategy="epoch"`, `save_strategy="epoch"`, `load_best_model_at_end=True`, `metric_for_best_model="eval_loss"`), guarded by `FiniteLossTrainer`.

## 6. Three-Epoch Fine-Tuning Run (`02_finetune.ipynb` on `Tesla T4`)

- **Run:** `finetuned_v2` ([results_v2/finetuned_v2/](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/results_v2/finetuned_v2/))
- **Training samples:** `1,325` (`v2` train split, SHA-256 `f3bc7f7bfdc3fbec...`), validated on `30` held-out cases (`min_supervised_tokens`: `59` train / `355` val)
- **Pre-flight forward/backward check (`train:64`, `1,651` tokens):** Initial loss `1.7577`, finite gradients verified, peak VRAM `8.338 GiB` on `Tesla T4`
- **Training runtime:** `2,419.11s` (`40.32 min`, `1.643 samples/s`, `498` optimizer steps across `3.0` epochs)
- **Final train loss (running average):** `0.5991`

### Loss Curve & Checkpoint Selection (`training_log.json` / `metrics.json`)

| Milestone | Step | Epoch | Train Loss | Validation `eval_loss` | Learning Rate |
|---|---:|---:|---:|---:|---:|
| Initial sanity check (`train:64`) | 0 | 0.00 | `1.7577` | — | — |
| Early warmup | 10 | 0.06 | `1.7043` | — | `4.50e-05` |
| End of Epoch 1 checkpoint | 166 | 1.00 | `0.6224` *(step 160)* | `0.5574` | `1.68e-04` *(step 160)* |
| End of Epoch 2 checkpoint | 332 | 2.00 | `0.5249` *(step 330)* | `0.5192` | `6.00e-05` *(step 330)* |
| **End of Epoch 3 (`best_model_checkpoint`)** | **498** | **3.00** | `0.5023` *(step 490)* | **`0.5119`** | `1.90e-07` *(step 490)* |

Validation loss decreased monotonically across all three epochs (`0.5574 → 0.5192 → 0.5119`) with no overfitting, selecting `checkpoint-498` as the best adapter.

---

## 7. Baseline vs Fine-Tuned Evaluation (`v2` 30-Case Validation Set)

Full 4-way evaluation from [results_v2/comparison/summary_comparison.csv](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/results_v2/comparison/summary_comparison.csv):

| Model | Decoding | Raw JSON Valid | Valid (Fence-Stripped) | Exact Top-Level Keys (10/10) | Exact Key Match | Budget Hits (`2048`) | Matched / Ref (Gen) | Strict Value F1 | Soft Value F1 | Mean Tokens | `5-gram ≥ 3` |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| `base` | `rp_1.00` | 0/30 (0.0%) | 6/30 (20.0%) | 0/30 (0.0%) | 0/30 | 10/30 | 4 / 1,082 (129) | 0.51% | 0.87% | 1,240.3 | 26/30 |
| `finetuned_v2` | `rp_1.00` | **25/30 (83.3%)** | 25/30 (83.3%) | **25/30 (83.3%)** | 0/30 | 3/30 | 193 / 1,082 (916) | **18.02%** | **29.61%** | 667.3 | 21/30 |
| `base` | `gen_rp_1.08` | 0/30 (0.0%) | 22/30 (73.3%) | 0/30 (0.0%) | 0/30 | 2/30 | 4 / 1,082 (509) | 0.49% | 2.09% | 764.8 | 21/30 |
| **`finetuned_v2`** | **`gen_rp_1.08`** | **28/30 (93.3%)** | **28/30 (93.3%)** | **28/30 (93.3%)** | 0/30 | **2/30** | **198 / 1,082 (1,001)** | **18.93%** | **30.74%** | **604.9** | **18/30** |

### Key Takeaways (`base | gen_rp_1.08` vs `finetuned_v2 | gen_rp_1.08`)
1. **Format & Schema Mastery (`0/30 → 28/30`):** The base model never emitted raw JSON (`0/30` without markdown fence stripping) and never produced the 10 canonical top-level clinical keys (`0/30`), instead inventing fields like `admission_date`, `surgery_status`, or `handoff`. After 3-epoch `v2` LoRA training, **`28/30` (`93.3%`)** parsed as valid raw JSON with **all 10 canonical top-level keys (`28/30`)**.
2. **Per-Case Consistency & Clean Failure Modes:** Under `gen_rp_1.08`, `finetuned_v2` outperformed `base` on **`28/30` cases** for both strict F1 and soft F1 (`median 500` generated tokens; max `1,062` tokens across all 28 valid cases). The only 2 invalid outputs (`validation:2335` and `validation:1913`) both ran into the `2,048`-token truncation limit (`ft_reached_budget=True`); zero finished generations failed syntax or schema checks.
3. **Massive Extraction Gain (`0.49% → 18.93%` Strict F1 / `2.09% → 30.74%` Soft F1):** Exact extracted fact matches rose **49.5×** (`4 → 198` out of `1,082` reference facts; recall `20.08%`, precision `18.88%`, soft recall `32.33%`, soft precision `30.80%`).
4. **Why `exact_key_match` stayed `0/30`:** Under `v2` omitted-null normalization, exact nested key-path equality requires predicting the exact same subset of optional leaf keys (e.g., `details`, `time`, `temporalisation`) as the annotator across every section and array item simultaneously.

---

## 8. Qualitative Side-by-Side Showcase (`gen_rp_1.08`)

Generated directly in [results_v2/comparison/showcase_examples.md](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/results_v2/comparison/showcase_examples.md):

### 1. Best Improvement: `validation:1161` (49-year-old male, solitary fibrous tumor)
- **`base` (`gen_rp_1.08`):** `raw_valid=False` (markdown-fenced), `exact_keys=False`, **Strict F1 = `0.000`**, **Soft F1 = `0.038`**, `904` tokens. Hallucinated top-level keys `"surgery"`, `"consolidation"`, `"preoperative"`, `"resection"`, `"treatment"` and fabricated ISO dates (`"admission_date": "2023-10-27"`).
- **`finetuned_v2` (`gen_rp_1.08`):** `raw_valid=True`, `exact_top_level_keys=True`, **Strict F1 = `0.508`**, **Soft F1 = `0.566`**, `426` tokens. Correctly extracted structured `patient information` (`{"age":"49","sex":"male"}`), empty `patient medical history` (`{}`), `surgeries` (`"reason":"Solitary fibrous tumor"`, `"Type":"Resection of the tumor with single-operation-incision thoracoscopy"`), `symptoms`, `medical examinations`, and `diagnosis tests`.

### 2. Solid Structured Extraction: `validation:2761` (75-year-old woman, morpheaform plaque)
- **`base` (`gen_rp_1.08`):** `raw_valid=False`, `exact_keys=False`, **Strict F1 = `0.000`**, **Soft F1 = `0.039`**, `233` tokens. Collapsed all medical sections as flat string fields nested inside `"admission": {...}` plus an unrequested `"handoff"` key.
- **`finetuned_v2` (`gen_rp_1.08`):** `raw_valid=True`, `exact_top_level_keys=True`, **Strict F1 = `0.308`**, **Soft F1 = `0.411`**, `564` tokens (`12` exact matches vs `0`). Properly structured `symptoms`, `medical examinations`, `diagnosis tests`, `treatments` (`Oral indomethacin`, `Topical clobetas`), and `{}` `discharge`.

### 3. Complex Emergency Presentation: `validation:2538` (24-year-old male, posterior fossa lesion & EVD)
- **`base` (`gen_rp_1.08`):** `raw_valid=False`, **Strict F1 = `0.000`**, **Soft F1 = `0.000`**, `544` tokens (fabricated `"admission_date": "2024-10-27"`).
- **`finetuned_v2` (`gen_rp_1.08`):** `raw_valid=True`, `exact_top_level_keys=True`, **Strict F1 = `0.189`**, **Soft F1 = `0.327`**, `500` tokens. Captured `visit motivation` (`"Altered conscious level"`), `patient information` (`24` / `male`), and emergency EVD insertion details.

### 4. Remaining Failure Mode: `validation:1913` (67-year-old teacher, CML & pleural effusion)
- **`finetuned_v2` (`gen_rp_1.08`):** `raw_valid=False` (`Unterminated string`), **Strict F1 = `0.000`**, `2,048` tokens (`ft_reached_budget=True`). Began with accurate structured extraction (`visit motivation`, `patient information`, `symptoms`, `diagnosis tests`, `treatments`) before running out of the `2,048`-token budget mid-object on a dense multi-line clinical history.

---

## 9. Deliverable Map
- [01_baseline_eval.ipynb](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/01_baseline_eval.ipynb) — Baseline inference & evaluation on `v2` (`base` with `rp_1.00` and `gen_rp_1.08`), with saved cell outputs.
- [02_finetune.ipynb](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/02_finetune.ipynb) — 3-epoch FP32 LoRA fine-tuning on cleaned `v2`, with saved milestone/VRAM/epoch outputs.
- [03_eval_and_compare.ipynb](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/03_eval_and_compare.ipynb) — Fine-tuned evaluation, 4-way Base vs Fine-Tuned table, and side-by-side showcase, with saved cell outputs.
- [prepared_clinical_dataset/eeff5efa1619f198/](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/prepared_clinical_dataset/eeff5efa1619f198/) — Frozen `v2` dataset (`1,325` train / `30` val).
- [results_v2/](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/results_v2/) — Downloaded `baseline/`, `finetuned_v2/` (best `checkpoint-498` adapter + logs), and `comparison/` (`summary_comparison.csv`, `case_comparison.csv`, `showcase_examples.md`).
- [archive/](file:///c:/Users/atharva.bedekar/PycharmProjects/SLMRetraining/archive/) — Preserved Phase 0/1 runs and legacy notebooks.
