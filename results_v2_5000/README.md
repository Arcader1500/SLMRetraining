# Full-schema v2 / 5,000-example results

Training completed on 19 November 2026 and stopped after local artifact
verification, as requested. The recovery T4 runtime has been released.

| Setting/result | Value |
| --- | --- |
| Prepared dataset | `3f8f10951130896b` |
| Training / development | 5,000 / same frozen 100 notes |
| Schema | Full original v2; no child-field projection or label repair |
| Training | Three epochs, global step 1,875 |
| Epoch 1 development loss | 0.4979258776 |
| Epoch 2 development loss | 0.4614775777 |
| Epoch 3 / best development loss | **0.4552387595** |
| Selected checkpoint | `checkpoint-1875` |
| Recovery | Original runtime disappeared for unknown reasons; resumed from locally saved step 625 |
| Baseline generations | 100 complete and preserved |
| Fresh adapter generations | 100 complete |

The selected adapter and tokenizer are in [finetuned_v2_5000/adapter](finetuned_v2_5000/adapter/).
Training metrics, complete resumed loss history, configuration and memory/mask
checks are in [finetuned_v2_5000](finetuned_v2_5000/). Local optimizer/model/RNG
checkpoints 625, 1250 and 1875 remain available under its `checkpoints/` directory.
The notebook with real execution counts and outputs is
[02_finetune.ipynb](../notebooks/v2_5000/02_finetune.ipynb).

[Completion checks](training_completion_checks.json) verify all 39 downloaded
artifact hashes, all 252 finite adapter tensors, exact adapter equality with the
selected checkpoint, three epochs/global step 1875, baseline preservation and
an error-free executed notebook. [The transport manifest](training_artifact_sha256.json)
records file hashes. The final ZIP is retained at local ignored path
`.venv/v2_5000_transfer/training_final.zip`, SHA-256
`4e16de32dbc03d7fca72ef16d628c1eefb69fab3f4080e672550a27e5ff86e89`.

The original run's checkpoint/loss history was preserved across recovery.
`metrics.json` is the unmodified Trainer output. Its `train_runtime` measures the
resumed segment, and its returned `train_loss` uses resume accounting rather
than an aggregate numerator for all 1,875 steps; do not report it as the complete
run's average training loss. The epoch development losses above remain the
checkpoint-selection measurements. Loss across different schemas is not a
controlled quality comparison.

See the [experiment protocol](../docs/experiments/FULL_SCHEMA_V2_5000_RUN.md)
and [session/recovery history](../docs/experiments/V2_5000_SESSION_HANDOFF.md).

## Frozen 100-case generation comparison

Both sets of outputs are verified locally. The Colab generation runtime was
released after export on 20 November 2026.

| Metric | Base | V2 / 5,000 adapter |
| --- | ---: | ---: |
| Raw-valid JSON objects | 0/100 | 96/100 |
| Valid JSON after removing fences | 62/100 | 96/100 |
| Exact top-level key match | 1/100 | 96/100 |
| Mean strict reference F1 | 0.52% | 24.79% |
| Mean soft reference F1 | 1.47% | 40.67% |
| Cases hitting the token budget | 11 | 3 |

Local rescoring reproduced the saved per-case and aggregate results for both
models. The [comparison summary](comparison/summary_comparison.csv),
[case comparison](comparison/case_comparison.csv), [verification checks](generation_completion_checks.json),
and [executed notebook](../notebooks/v2_5000/03_eval_and_compare.ipynb) are saved.
F1 measures agreement with the full-schema reference labels.

## Source-grounded Gemini 4 Hydrogen evaluation

All 400 judgments are complete. Local DeepEval used `gemini-4-hydrogen`
(`backend: gemini`) and the existing `source_grounded_v2` rubric on both saved
outputs for each frozen case (`run_id`: `8993a8dd5f5f3a18`).

| Metric | Base mean | Adapter mean | Paired gain | 95% paired BCa CI (100k) | Adapter wins / ties / losses |
| --- | ---: | ---: | ---: | --- | ---: |
| Source fidelity | 0.386 | 0.539 | +0.153 | [+0.115, +0.190] | 68 / 21 / 11 |
| Source coverage | 0.412 | 0.550 | +0.138 | [+0.101, +0.175] | 69 / 17 / 14 |

The run's
[summary](deepeval_100/judgments/8993a8dd5f5f3a18/summary.json),
[paired comparison](deepeval_100/judgments/8993a8dd5f5f3a18/paired_comparison.csv),
and [scores and reasons](deepeval_100/judgments/8993a8dd5f5f3a18/scores.json)
are saved locally.

## Source-grounded Luna evaluation

All 400 judgments are complete. Local DeepEval 4.3.4 used `gpt-6-luna` and the
existing `source_grounded_v2` rubric on both saved outputs for each frozen case.

| Metric | Base mean | Adapter mean | Paired gain | Adapter wins / ties / losses |
| --- | ---: | ---: | ---: | ---: |
| Source fidelity | 0.409 | 0.517 | +0.108 | 63 / 24 / 13 |
| Source coverage | 0.450 | 0.526 | +0.076 | 57 / 20 / 23 |

These scores represent Luna's assessment of source consistency. The run's
[summary](deepeval_100/judgments/c53d6fbd06d96102/summary.json),
[paired comparison](deepeval_100/judgments/c53d6fbd06d96102/paired_comparison.csv),
[scores and reasons](deepeval_100/judgments/c53d6fbd06d96102/scores.json), and
[completion checks](deepeval_100/judgments/c53d6fbd06d96102/completion_checks.json)
are saved locally. Verification matched all 400 unique score keys, the frozen
inputs, the 200 CSV rows, and the recomputed means and paired gains.
