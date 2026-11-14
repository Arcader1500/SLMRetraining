# Gemma clinical fine-tuning: complete session handoff

Updated: 13 November 2026. Workspace: `C:/Users/atharva.bedekar/PycharmProjects/SLMRetraining`.

## 1. Objective and current decision

The user's objective is to learn and demonstrate **fine-tuning a small Gemma model on a suitable task**, with a reproducible before/after evaluation. The objective is not to spend indefinitely tuning prompts until an untrained model can handle this particular dataset. Changing the dataset or narrowing the use case is acceptable if the evidence supports it.

The current experiment uses `google/gemma-3-270m-it` to turn clinical case notes into a relatively large, nested JSON report. Although the original notebooks call this SOAP summarization, the actual target is a clinical extraction schema, not simply four Subjective/Objective/Assessment/Plan sections.

Two LoRA pilots and their controlled comparisons are complete. Fine-tuning improved extraction and formatting substantially over the original model, but the second, longer run did not improve generated-report quality over the first. Repetition, malformed JSON, omissions, and incorrect field assignments remain.

**Current position:** preserve both pilots, treat pilot 1 as the stronger checkpoint on the existing 10-case development comparison, and do not launch a longer run unchanged. The last proposed next steps were to audit target repetition/duplication and test a separately recorded repetition-reduction decoding experiment. Neither has been executed yet. Do not declare the model or dataset categorically unsuitable from this small experiment.

## 2. User preferences and operating environment

- Use **Jupyter notebooks** for preparation, audits, training, and comparisons.
- User executes model-backed work manually through **VS Code connected to a Google Colab GPU runtime**, then downloads artifacts into this workspace for analysis.
- Local VS Code Explorer files and the remote Colab kernel filesystem are separate. Paths in executed cells refer to the kernel machine.
- Upload complete data/model folders using VS Code Explorer's **Upload to Colab**, selecting the notebook's server and `/content`. Download result archives before resetting the runtime.
- CPU is sufficient for tokenizer/data audits and preparation; practical model inference/training uses a GPU.
- Hugging Face access requires accepting Gemma's license with the same HF account that owns the read token. HF and Colab authenticate separately. Use `HF_TOKEN`, cached HF login, or a hidden `getpass` prompt inside the remote kernel.
- No paid judge is used in the current prepared-data workflow. No Gemini API key is required for it.
- User reported approximately 380 Colab compute units and a T4 rate of 1.15 units/hour. These were reported at the time, not a current remaining balance.
- Do not expose credentials or include them in notebooks or reports. Clinical text is present in saved data and generation artifacts.

## 3. Model, dataset, and pinned revisions

| Item | Value |
|---|---|
| Model | `google/gemma-3-270m-it` |
| Model revision | `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3` |
| Dataset | `AmareshHebbar/clinical-summarizer-sft` |
| Dataset revision | `4ca20e0a38cc9235045c973b5503d49952fd1fac` |
| Prepared dataset version | `900825a06d38a006` |
| Seed | 42 |
| Prepared training rows | 1,325 |
| Frozen evaluation rows | 10 |
| Prepared maximum allowed sequence | 4,096 tokens |
| Actual longest prepared training row | 1,949 tokens |
| Actual mean prepared training length | 1,211.06 tokens |
| Actual longest prepared validation row | 1,382 tokens |

Dataset top-level fields:

`visit motivation`, `admission`, `patient information`, `patient medical history`, `surgeries`, `symptoms`, `medical examinations`, `diagnosis tests`, `treatments`, `discharge`.

The schema mixes objects and arrays, with many nested fields and the string `"None"` for unavailable information.

## 4. Initial baseline failure and investigation

The first Colab evaluation selected 50 validation examples and generated with FP16 on CUDA, greedy decoding, and `max_new_tokens=512`.

Artifacts: [baseline_evaluation/](./baseline_evaluation/) and historical [baseline_evaluation.ipynb](./baseline_evaluation.ipynb).

Findings:

1. **All 50 saved generations were empty strings**, not merely malformed JSON. The JSON parser correctly rejected them.
2. CUDA model loading unconditionally used FP16. Known Gemma FP16 empty-output reports made numerical precision the leading hypothesis. The original run did not retain raw token IDs or logit diagnostics, so the exact cause was not isolated experimentally.
3. The dataset's original instruction only requested a structured SOAP summary. It did not explicitly request JSON or supply a schema.
4. Resume logic skipped any existing output key, including empty strings. Rerunning could silently preserve every failed generation.
5. Aggregate counting treated empty strings as completed generations.
6. The 512-token generation budget was later shown to be far too short for most reference answers.

Relevant primary-source issue consulted: [Transformers Gemma FP16 empty-output report](https://github.com/huggingface/transformers/issues/36822). This supports a hypothesis; it is not proof of the cause for this exact model/run.

### Second historical diagnostic baseline

The notebook was updated to default to 10 cases, avoid FP16, explicitly request JSON with a full placeholder-filled schema, use a 2,048-token output budget, and retain diagnostics. These outputs are at the **top level** of [baseline_evaluation_diagnostic_10/](./baseline_evaluation_diagnostic_10/).

Results:

- 10/10 nonempty responses; first-token logits finite.
- Saved runtime reported BF16 on Tesla T4. Do not infer native T4 BF16 acceleration from this: later workflows deliberately use FP32.
- 5/10 parseable JSON after stripping Markdown fences.
- 3/10 exact reference key matches.
- 5/10 hit the 2,048-token budget.
- Four of the five valid reports consisted entirely of `"None"`; the fifth had only one other value, a generic statement that no motivation was supplied.
- Failed reports repeated approximately 47?50 admission entries until truncation.

Conclusion: the placeholder-filled schema encouraged copying rather than clinical extraction. Increasing the output budget alone would prolong repetition. These historical diagnostic outputs are **not** the baseline used for the pilot comparisons.

The user corrected the direction: assess fine-tuning suitability rather than making the base model pass through prompt work alone.

## 5. Training-token and truncation audit

Created [training_token_audit.ipynb](./training_token_audit.ipynb). User ran it and downloaded [training_token_audit/](./training_token_audit/), including [summary.json](./training_token_audit/summary.json).

This was tokenizer-only analysis of the original first 1,500 training rows, reproducing the original training role folding and default text tokenization. It did not load model weights, run inference, or train.

Original training configuration in [main.ipynb](./main.ipynb) used `max_seq_length=512`.

### Raw, pre-cleaning length results

| Length | Median | 95th percentile | Maximum |
|---|---:|---:|---:|
| Prompt | 444 | 472 | 513 |
| Assistant answer | 974 | 1,358.25 | 2,037 |
| Complete conversation | 1,421.5 | 1,813.25 | 2,512 |

Mean prompt length: 444.5 tokens. Mean answer length: 1,002.58 tokens.

| Context limit | Complete conversations | Complete answer content | Answer tokens retained overall |
|---|---:|---:|---:|
| 512 | 0/1,500 | 0/1,500 | 6.73% |
| 1,024 | 13/1,500 | 13/1,500 | 57.72% |
| 2,048 | 1,483/1,500 | 1,485/1,500 | 99.85% |
| 4,096 | 1,500/1,500 | 1,500/1,500 | 100% |
| 8,192 | 1,500/1,500 | 1,500/1,500 | 100% |

At 512, 1 example retained no answer supervision and 1,499 retained only part of the answer. The first three examples retained 77/826, 66/983, and 37/1,305 answer tokens respectively. Roughly **93.3% of target tokens were removed** overall.

Complete answer content and complete conversation differ because closing turn tokens may still be cut.

Only 7/1,500 raw reference answers, including closing tokens, fit a 512-token inference output budget. All 1,500 fit a 2,048-token output budget. That says nothing about whether generated text will loop.

The original default tokenizer path added one extra special token compared with explicit `add_special_tokens=False` on already chat-formatted text. The prepared workflow avoids adding special tokens twice.

### Raw target JSON defects

387/1,500 references (25.8%) failed strict JSON parsing:

- 361: invalid control characters in strings.
- 24: delimiter errors.
- 2: trailing commas.

Thus both sequence truncation and target formatting were demonstrable problems before assessing the model's learning ability.

The audit's counts modeled tokenization/truncation, not actual TRL labels. The later saved-label checks and forward/backward test addressed that gap.

The user also experienced a 45-minute delay during the audit workflow. The saved notebook only showed package installation output, not tokenization progress; no exact live-process cause was established. Avoid attributing this to 1,500 model inferences: there were none. Progress/stage messages and nonquiet installation output were added during troubleshooting; inspect the current notebook rather than assuming every later saved copy retains those changes.

## 6. Dataset preparation and saved artifact

Created and ran [prepare_clinical_dataset.ipynb](./prepare_clinical_dataset.ipynb).

Canonical artifact: [prepared_clinical_dataset/900825a06d38a006/](./prepared_clinical_dataset/900825a06d38a006/).

Important files:

- [manifest.json](./prepared_clinical_dataset/900825a06d38a006/manifest.json)
- [train.jsonl](./prepared_clinical_dataset/900825a06d38a006/train.jsonl)
- [validation.jsonl](./prepared_clinical_dataset/900825a06d38a006/validation.jsonl)
- [preparation_log.csv](./prepared_clinical_dataset/900825a06d38a006/preparation_log.csv)
- Saved Hugging Face DatasetDict under [dataset/](./prepared_clinical_dataset/900825a06d38a006/dataset/)
- [latest.json](./prepared_clinical_dataset/latest.json) points to the version, but comparisons/training should use the version in the frozen baseline contract.

Preparation behavior:

- Inspects the first 1,500 training rows and all 3,000 validation rows.
- Validates single-turn system/user/assistant conversations.
- Parses targets with duplicate-key and nonstandard-constant rejection.
- Conservatively tolerates unescaped control characters, then serializes to strict compact JSON; optional Markdown fences can be removed.
- Does **not** guess missing commas/braces or use an LLM to rewrite medical facts.
- Rejects unresolved syntax, unexpected top-level fields, placeholder-only targets, empty content, and overlength complete sequences.
- Removes exact normalized-note duplicates within splits and excludes training notes appearing anywhere in the eligible validation pool.
- Does not detect near duplicates or patient-level overlap.
- Adds one short JSON extraction instruction listing top-level fields, without a placeholder-filled schema.
- Uses the **same stored prompt text** for baseline and adapter evaluation.
- Saves `messages`, `prompt_text`, compact `reference`, complete formatted `text`, source identities/hashes, token counts, `input_ids`, `attention_mask`, and `labels`.
- Labels mask prompt tokens with `-100` and supervise the full assistant answer plus closing tokens. No silent truncation or packing.

Counts verified from preparation logs:

- Training: 1,432 eligible after initial checks; 68 rejected.
- Then 107 training examples excluded for cross-split normalized-note duplication.
- Final training set: **1,325**.
- Validation: 2,834 eligible; 166 rejected; seed-42 sample of **10** saved for evaluation.
- Across the final 1,335 saved examples: 1,006 required no JSON repair and 329 had control characters escaped.

Compact serialization and the revised prompt change token lengths. Do not confuse the prepared maximum of 1,949 training tokens with the raw audit maximum of 2,512.

## 7. Frozen prepared baseline and comparison protocol

Notebook: [prepared_baseline_evaluation.ipynb](./prepared_baseline_evaluation.ipynb).

Actual downloaded baseline directory, despite the historical parent name:

[baseline_evaluation_diagnostic_10/900825a06d38a006_353c8393d011/](./baseline_evaluation_diagnostic_10/900825a06d38a006_353c8393d011/).

This **numbered subdirectory** is the authoritative baseline for pilots 1 and 2. Do not mix it with the historical diagnostic files at the parent directory's top level.

Contract: [comparison_contract.json](./baseline_evaluation_diagnostic_10/900825a06d38a006_353c8393d011/comparison_contract.json).

Frozen settings:

- Original base checkpoint and tokenizer at the pinned revision.
- Exact same 10 stored validation notes, references, and full prompts.
- Greedy decoding: `do_sample=False`.
- FP32 inference.
- `max_new_tokens=2048`.
- `add_special_tokens=False` for stored chat-formatted prompts.
- Seed 42; metrics version 1.
- Transformers 4.57.6; Torch `2.14.1+cu130`.
- Diagnostics include raw IDs, special-token-visible decoding, first-token logit finiteness, token counts, budget hits, and EOS endings.
- Empty/nonfinite generations stop the run and are retried; completed cases can resume.

Frozen case IDs:

```text
validation:2761
validation:465
validation:105
validation:1161
validation:1030
validation:935
validation:583
validation:428
validation:2926
validation:2336
```

Key hashes:

```text
train split:
1c270692d1ab82cde939941400e61b744a19b9a0f52ca6684a0a3e8c7920bf19
validation split:
dc3e8a315a88322fb583a28319f0a4e894729a4a70820da86ec91e1a0df0dc7a
prompt list:
27473a3daf3f9b00f4e40176586211f1425dd09350fe5f783375564ed0488d43
comparison contract:
353c8393d011c896475fba14db6d2751a609da0c8f957616f401e7ce21899db9
```

### Metrics and their limitations

- Raw JSON-object validity and validity after removing enclosing Markdown fences are separate.
- Duplicate object keys are rejected, not silently overwritten.
- Exact key match compares recursive reference key paths; it is not a complete JSON-schema/type validator.
- Field/value matching normalizes case and whitespace and ignores array order. Array items are represented as a **multiset**, so repeated values can reduce precision.
- Missing-value placeholders are excluded. Schema words and `"None"` do not earn fact matches.
- Invalid JSON receives zero extracted-value matches; this combines formatting and extraction performance.
- Mean precision/recall/F1 are **macro averages over the 10 cases**. Aggregate matched/reference/generated counts are also saved; they are not interchangeable with the macro percentages.
- Correct paraphrases may fail exact matching. Matching a reference does not prove source faithfulness, and reference validity does not prove reference truth.
- No paid LLM judge is active.

## 8. Pilot checks before training

Notebook: [train_prepared_clinical.ipynb](./train_prepared_clinical.ipynb).

Initial run used `RUN_TRAINING=False`, `CHECK_BACKWARD=True`.

Artifacts: [pilot_01_checks/](./pilot_01_checks/).

Verified:

- All 1,335 prepared training/validation examples have consistent lengths and complete assistant-only labels.
- First three decoded supervised sequences exactly match complete reference answers plus `<end_of_turn>\n`.
- Frozen dataset, prompt, and comparison hashes match the baseline.
- Longest training row `train:64`, 1,949 tokens, passed forward/backward checks.
- Initial loss: 1.7252361774 on that longest row.
- Gradients finite; no optimizer step taken in the check run.
- Peak allocated GPU memory: about 6.83 GiB on Tesla T4, FP32. This was a smoke-check allocation, not a full training-memory guarantee.

A notebook compatibility bug was found and fixed: Hugging Face Datasets returned a `Column`, which JSON hashing could not serialize. The validation prompt and case-ID columns are now converted with `list(...)` before hashing/comparison. Frozen hashes and samples were unchanged.

## 9. Shared training setup

Both pilots are **fresh runs from the original base checkpoint**, not pilot 2 continuing pilot 1's adapter.

- Transformers `Trainer` with explicit saved tokens/labels; no TRL preprocessing.
- LoRA rank 16, alpha 32, dropout 0.05, no bias.
- Target modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`.
- Batch size 1; gradient accumulation 8.
- Learning rate 0.0002, warmup ratio 0.1, Trainer's default learning-rate schedule.
- FP32; FP16 disabled.
- Gradient checkpointing, `use_reentrant=False`; model KV cache disabled during training.
- Assistant-only loss using saved labels; dynamic right padding masks labels with `-100`.
- No packing, no answer truncation, no added special tokens.
- Seed/data seed 42.
- Finite-loss checks in Trainer.
- No periodic adapter checkpoints or automatic resume. A failed/restarted training attempt needs a new run directory.

Recorded package stack: Torch `2.14.1+cu130`, Transformers 4.57.6, Datasets 4.8.5, PEFT 0.18.1, Accelerate 1.15.0.

## 10. Pilot 1: 60 steps

Artifacts: [pilot_01/](./pilot_01/); adapter under [adapter/](./pilot_01/adapter/).

- 60 optimizer steps; 0.362264 epochs (about 480 training examples with batch/accumulation settings).
- Training runtime: 451.0154 seconds, approximately 7.5 minutes.
- Mean train loss across run: 0.7632016664.
- First 10 logged step losses averaged 1.55683; last 10 averaged 0.50458.
- Validation loss: 0.4451568723.
- All 60 logged losses and gradient norms finite.
- Adapter weights saved successfully, approximately 15.2 MB.

Comparison notebook: [compare_pilot_clinical.ipynb](./compare_pilot_clinical.ipynb).

Actual output path preserves the user's spelling:

[pilot_01_comparision/900825a06d38a006_2860de5a2cce/](./pilot_01_comparision/900825a06d38a006_2860de5a2cce/).

It ran only 10 adapter inference cases, reusing saved original baseline outputs. Verified adapter hash:

```text
17473347c104cba99e317f3dc34a9512473c6bac9ebc0a51dddc55754746dbfa
```

Pilot 1 improved real extraction as well as formatting. Example: generated visit motivation `Acute pain of the left mandible`, with nested structures closer to the target schema. However, clear facts were still omitted: a note explicitly described a 45-year-old male, while generated age was `"None"`.

Four parsing failures remained: two multiple-object outputs (`Extra data`), one duplicate-key output, and one symptom-repetition loop ending at the token budget.

## 11. Pilot 2: 166 steps / one epoch

Artifacts: [pilot_02/](./pilot_02/); adapter under [adapter/](./pilot_02/adapter/).

Only run name and training step count were intentionally changed from pilot 1. Increasing total steps also changes the schedule/warmup trajectory; this is not literally the same first 60 updates followed by another 106.

- 166 optimizer steps; reported epoch exactly 1.0.
- Training runtime: 1,255.8338 seconds, approximately 20.9 minutes.
- Mean train loss: 0.5905310614.
- First 10 logged losses averaged 1.69208; last 10 averaged 0.44819.
- Validation loss: 0.3793311715.
- All 166 logged losses and gradient norms finite.

Comparison output:

[pilot_02_comparision/900825a06d38a006_9102ae51256b/](./pilot_02_comparision/900825a06d38a006_9102ae51256b/).

Verified adapter hash:

```text
2404da6507ece5d23b42adeb46c0c29946ce820cb7f323455dc26d69b5aafff3
```

Both pilot comparisons verified the same contract hash, baseline output/diagnostic hashes, and metric-source hash. Each comparison was checked against its actual saved adapter weights.

## 12. Before/after results

| Metric | Prepared baseline | Pilot 1: 60 steps | Pilot 2: 166 steps |
|---|---:|---:|---:|
| Cases | 10 | 10 | 10 |
| Empty outputs | 0 | 0 | 0 |
| Raw JSON object valid | 0 | 6 | 5 |
| Valid after fence removal | 4 | 6 | 5 |
| Exact reference key match | 0 | 2 | 2 |
| Placeholder-only valid outputs | 0 | 0 | 0 |
| Output budget reached | 3 | 1 | 4 |
| Mean exact-value precision | 0.67% | 16.63% | 12.55% |
| Mean exact-value recall | 0.20% | 9.64% | 9.72% |
| Mean exact-value F1 | 0.31% | 11.87% | 10.34% |
| Matched reference values | 1 | 34 | 33 |
| Reference values | 353 | 353 | 353 |
| Parsed nonmissing generated values | 57 | 124 | 156 |
| Teacher-forced validation loss | Not measured on full set | 0.4452 | 0.3793 |

Do not compare the longest-single-example initial loss 1.7252 to the whole-validation loss as if they were the same evaluation.

### Per-case F1 and parse changes, pilot 1 to pilot 2

| Case | Pilot 1 valid | Pilot 2 valid | Pilot 1 F1 | Pilot 2 F1 |
|---|---|---|---:|---:|
| validation:2761 | Yes | Yes | 0.182 | 0.208 |
| validation:465 | No | No | 0 | 0 |
| validation:105 | No | Yes | 0 | 0.176 |
| validation:1161 | Yes | No | 0.279 | 0 |
| validation:1030 | Yes | No | 0.238 | 0 |
| validation:935 | Yes | Yes | 0.169 | 0.187 |
| validation:583 | No | Yes | 0 | 0.176 |
| validation:428 | Yes | No | 0.119 | 0 |
| validation:2926 | Yes | No | 0.200 | 0 |
| validation:2336 | No | Yes | 0 | 0.286 |

Four previously valid reports regressed to invalid; three previously invalid reports became valid. This is not uniform degradation across all examples.

Pilot 2 failures:

- `validation:465`: repeated abdominal-pain symptom entries until the 2,048-token limit.
- `validation:1030`: repeated `no history of swelling, pain or paresthesia` inside a string until cutoff.
- `validation:428`: repeated examination entries until cutoff.
- `validation:2926`: budget exhausted within a long field; incomplete JSON.
- `validation:1161`: delimiter error, despite ending before the token budget.

## 13. What the evidence says about Gemma and this dataset

### Established

- Empty output was a runtime/protocol problem, not evidence that the dataset intrinsically produced no text. The FP32 prepared workflow produces nonempty text reliably in the tested cases.
- Original 512-token training was demonstrably unsuitable for full targets. The corrected saved-token workflow retains complete answers.
- The raw dataset contains substantial JSON syntax defects and exact-note cross-split duplication. These required preparation before meaningful training comparisons.
- Gemma 270M can learn useful parts of this task: field structure, raw JSON output, and source-specific values improved after fine-tuning.
- The full task is computationally feasible for this pilot on T4 FP32 at batch size 1 with checkpointing. Both training runs completed.
- One epoch lowered teacher-forced loss but did not improve this small set's free-generation metrics over the shorter pilot.
- Repetition and malformed generated JSON remain major failure modes. More output tokens alone do not solve loops.

### Not established

- That Gemma 270M can never perform this use case well.
- That the dataset must be abandoned.
- That more training caused classical overfitting; two runs, one seed, and 10 cases cannot diagnose that confidently.
- That the low exact-value F1 is a clinical accuracy percentage or that every unmatched value is false.
- That syntactically cleaned references are clinically complete/correct or fully supported by the source note.
- That repetition comes from duplicated targets; a focused repetition audit has not yet been done.
- That any checkpoint is clinically reliable or ready for deployment.

Potential complexity issues remain: long nested JSON, many missing-value fields, variable-length arrays, and clinical reasoning/extraction requirements are demanding for a 270M model. These are plausible contributors, not isolated experimental conclusions.

## 14. Latest recommended next steps

Do not rerun historical baselines, regenerate prepared data, or overwrite the frozen comparison set just to start the next chat.

1. **Audit the prepared training references for repetition and redundancy.** Distinguish exact duplicate array entries, excessive placeholders, repetitive phrases, inconsistent field assignments, and possible unsupported target content. Start with the saved JSONL; this does not need a GPU. Report findings before changing data.
2. **Separate decoding problems from model learning.** Consider a controlled repetition-reduction decoding experiment on both saved adapters. Record the exact settings as a new protocol and preserve all old results. Do not silently alter the original contract or repair generated JSON into passing scores. Include the original base model if making new before/after claims under changed decoding.
3. Inspect generated reports against source notes, including invalid outputs that get zero value score, to distinguish extraction progress from formatting failure.
4. If evaluating another dataset/use case, make that an explicit experiment with clear short targets, a new preparation version, and its own baseline. Narrow clinical extraction or another small-model-appropriate task remains acceptable to the user.
5. Before making a strong suitability claim, use more held-out examples and reserve an untouched test set if repeatedly tuning on these 10 validation cases.

No pilot 3, decoding experiment, target-repetition audit, or replacement-dataset selection has been completed.

## 15. GPU/cost discussion

User asked whether a better GPU would help. Answer: likely yes, particularly native BF16 training on suitable hardware, but no actual cross-GPU benchmark was run.

Current notebook forces FP32. Merely selecting another GPU does not configure BF16. Never reintroduce FP16 as the T4 fallback. If training precision changes, record it; retain the original FP32 protocol when comparing against the frozen generation baseline, or explicitly create a new common evaluation protocol.

At the user's reported 1.15 units/hour, measured training alone cost approximately 0.144 units for pilot 1 and 0.401 units for pilot 2. These estimates exclude downloads, checks, inference, and runtime idle time. No fixed current rate for another GPU was asserted. Compare measured runtime times the rate displayed for the allocated Colab server.

## 16. Repository map and cautions for the next chat

Primary notebook workflow:

1. [training_token_audit.ipynb](./training_token_audit.ipynb) ? historical raw token audit.
2. [prepare_clinical_dataset.ipynb](./prepare_clinical_dataset.ipynb) ? saved cleaned/tokenized dataset.
3. [prepared_baseline_evaluation.ipynb](./prepared_baseline_evaluation.ipynb) ? authoritative pretraining comparison protocol.
4. [train_prepared_clinical.ipynb](./train_prepared_clinical.ipynb) ? checks and configurable pilot training.
5. [compare_pilot_clinical.ipynb](./compare_pilot_clinical.ipynb) ? adapter comparison against saved baseline.
6. [README.md](./README.md) ? workflow overview.

The notebooks' current configurable defaults may reflect the user's latest pilot 2 edits. Inspect `RUN_NAME`, `MAX_STEPS`, `PILOT_DIR`, `BASELINE_DIR`, and output roots before rerunning. Do not assume a file named `compare_pilot_clinical` still points to pilot 1.

Historical experiments:

- [baseline_evaluation.ipynb](./baseline_evaluation.ipynb)
- [baseline_evaluation/](./baseline_evaluation/)
- Top-level diagnostic files in [baseline_evaluation_diagnostic_10/](./baseline_evaluation_diagnostic_10/)
- [main.ipynb](./main.ipynb): old 512-token recipe, not connected to the notebook-prepared data. Do not use unchanged.
- [fine_tune_gemma3.ipynb](./fine_tune_gemma3.ipynb): separate Alpaca demonstration; not the clinical pilot.

A **separate command-line pipeline** exists in [clinical_sft/](./clinical_sft/), documented in [CLINICAL_PIPELINE.md](./CLINICAL_PIPELINE.md), with [requirements-clinical.txt](./requirements-clinical.txt) and [tests/](./tests/). It has a different preparation/artifact protocol. Do not interchange its data format or reported metrics with the notebook workflow. This session's two measured pilots use the notebook workflow.

Project [pyproject.toml](./pyproject.toml) and [uv.lock](./uv.lock) describe a different/newer dependency stack. The notebooks install their own recorded experimental dependencies. Avoid blindly replacing that environment with `uv sync` during reproduction.

Downloaded folders intentionally retain the user's `comparision` spelling; notebook defaults may use `comparison`. Actual paths above are authoritative.

### Verification already performed

Local verification included notebook Python compilation; conservative-repair checks on synthetic and 50 saved references; label/padding/context-boundary tests; saved label invariants on all 1,335 examples; reproduced/fixed Column serialization; matching raw references and closing tokens in label previews; hashes of frozen datasets/prompts/contracts/adapter weights; all training loss/gradient logs finite; and recomputation of original baseline metrics using the reused comparison metric code.

User executed the GPU-backed checks, both training runs, and both adapter comparisons. Neither pilot relies merely on local syntax checks for its completion claim. No further experiment has been run since pilot 2 analysis.

## 17. Suggested opening instruction for the fresh chat

> Read SESSION_HANDOFF.md and inspect the referenced pilot 1/pilot 2 comparison artifacts. We are evaluating whether Gemma 3 270M can be fine-tuned for a suitable use case, not trying indefinitely to make an untrained model pass this dataset. Keep workflows in Jupyter notebooks. Two clinical JSON LoRA pilots are complete; pilot 1 currently performs better on free generation than pilot 2 despite pilot 2 having lower validation loss. Start by auditing the saved prepared targets for repetition/redundancy and explain what the evidence suggests before proposing more training or a new dataset. Preserve the frozen comparison protocol and all existing artifacts.
