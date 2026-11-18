# Current session handoff

Updated 18 November 2026. This supersedes the [archived handoff history](../archive/docs/handoffs/SESSION_HANDOFF_2026-11-18.md).

## Current state

- **V3 generation complete:** 100 paired development cases, base versus FP32 LoRA Gemma 270M. Three epochs, 498 steps; checkpoint 498 selected by development loss. Dataset `e80798edebe5aba5`, 1,325 training rows, ten parents and twenty child paths.
- **Source-rubric evaluation complete:** all 100 cases, 400 unique measurements with `gpt-6-luna`. Fidelity 0.386 to 0.516 (+0.130); coverage 0.407 to 0.502 (+0.095). No further inference is needed.
- **20-case source audit complete:** [report](../results_v3/source_audit_20/REPORT.md) and [case ledger](../results_v3/source_audit_20/CASE_LEDGER.md).
- **Training audit partial:** structure/projection checked on all 1,325 rows; 10 of 100 sampled rows have candidate and assistant source review. Ninety semantic reviews remain. See the [training audit report](../results_v3/training_audit_100/REPORT.md).
- No training-label repair or 5,000-example run has occurred. The recorded Colab runtime was released; the prior session left no evaluation or audit process running.

## Read next

| Topic | Starting point |
| --- | --- |
| Experiment, schema and generation | [V3 protocol](experiments/REDUCED_SCHEMA_1325_RUN.md) |
| Run history | [Run catalog](experiments/RUN_CATALOG.md) |
| Full source-rubric results | [100-case evaluation](evaluation/REMAINING_VALIDATION_EVALUATION.md) |
| Earlier rubric change and judge limits | [20-case reevaluation](evaluation/SOURCE_GROUNDED_REEVALUATION.md) |
| Data versions and cleaning | [Dataset guide](data/README.md) |
| Review policy | [Annotation policy](CLINICAL_ANNOTATION_POLICY.md) |
| Saved artifacts | [V3 index](../results_v3/README.md) |

The [interactive HTML](Clinical_Extraction_Phases_1_and_2.html) compares v2/v3 generation and the two 20-case judge rubrics. It predates the full-100 source evaluation; use the combined saved summary for those results. `experiment_status.json` records the generation stage; its `llm_evaluation=false` predates the separate judge runs.

## Remaining research work

Clarify broad history-field semantics and calibrate the training auditor before completing the remaining 90 reviews. Labels exactly match literal v2-to-v3 projection; removed frequency, duration and diagnostic fields can discard supported information. Define source-verified folding into existing allowed strings before creating separately versioned replacement labels. Do not add schema paths or silently repair frozen labels.

A larger data-size experiment or model/rank change remains proposed work. Preserve current schema, prompts, development cases and decoding for controlled comparisons; record steps, supervised tokens and runtime. V2 and v3 use different schemas/prompts/cases, so their F1 difference does not isolate a single intervention.

## Working constraints

Preserve v1/v2/v3 data, adapters, predictions, references, scores, hashes and contracts. Keep audited development cases out of training. Gemini stays disabled; do not launch training or judge calls for repository maintenance. Prior handoffs record the user's preference against a code-review workflow for these iterations.

Use FP32 on T4; earlier FP16 runs overflowed. Reproduction needs the recorded runtime stack rather than blindly syncing the newer lockfile. Frozen paths and several execution-source hashes are checked by existing validators; retain them.

Current docs are grouped into guides, experiments, evaluation and data. Older v2 reports, schema-planning evidence and the verbose handoff live in the [archive](../archive/README.md).

## Cleanup verification

All 22 offline tests passed in the isolated DeepEval environment, and the remaining-80 verifier confirmed all 400 combined source measurements and frozen inputs. Local Markdown links were checked after relocation. No model inference or training ran.

The older `check_source_grounded_evaluation` command currently fails its historical `scripts/run_deepeval.py` byte-hash assertion: the runner was subsequently extended for remaining-80 checkpoint/resume support. This cleanup does not change Python sources or rewrite historical provenance to hide that mismatch. Use the remaining-80 checker for current completed-run integrity; retain the old provenance as execution history.
