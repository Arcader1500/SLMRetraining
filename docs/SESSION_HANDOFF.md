# Current session handoff

## V2 / 5,000 generation and LLM evaluations complete

Updated 23 November 2026. The checkpoint-1875 adapter ran on all 100 frozen
validation cases. The base and adapter generations, diagnostics, comparison
scores, and executed notebook are verified locally. The Colab T4 was released.

- **Gemini 4 Hydrogen evaluation (`8993a8dd5f5f3a18`):** All 400 local
  `gemini-4-hydrogen` judgments under the `source_grounded_v2` rubric are saved
  in [summary.json](../results_v2_5000/deepeval_100/judgments/8993a8dd5f5f3a18/summary.json)
  and [paired_comparison.csv](../results_v2_5000/deepeval_100/judgments/8993a8dd5f5f3a18/paired_comparison.csv).
  Mean source fidelity rose from **0.386 to 0.539** (`+0.153`, 68W / 21T / 11L;
  100k paired BCa 95% CI `[+0.115, +0.190]`) and mean source coverage rose from
  **0.412 to 0.550** (`+0.138`, 69W / 17T / 14L; 95% BCa CI `[+0.101, +0.175]`).
- **Earlier GPT-6 Luna evaluation (`c53d6fbd06d96102`):** All 400 local
  `gpt-6-luna` judgments remain preserved under `c53d6fbd06d96102` (fidelity
  `0.409 -> 0.517`, coverage `0.450 -> 0.526`). See the
  [completion checks](../results_v2_5000/deepeval_100/judgments/c53d6fbd06d96102/completion_checks.json).
- **Overview report:** [SLM_Clinical_Extraction_Overview.html](SLM_Clinical_Extraction_Overview.html)
  now reports the Gemini 4 Hydrogen numbers for `Full · 5,000` alongside a
  tabbed 100-case Paired Bootstrap 95% CI comparison for both runs.

See the [results](../results_v2_5000/README.md) and the
[experiment handoff](experiments/V2_5000_SESSION_HANDOFF.md).

Updated 19 November 2026. This supersedes the [archived handoff history](../archive/docs/handoffs/SESSION_HANDOFF_2026-11-18.md).

## Training-label audit complete

The frozen 100-case training audit is complete. Read the [completion report](../results_v3/training_audit_100/continuation_v2/REPORT.md), [case ledger](../results_v3/training_audit_100/continuation_v2/combined_case_ledger.json), and [parent disagreements](../results_v3/training_audit_100/continuation_v2/parent_disagreements.json). The preserved ten-case pilot remains v1; the other 90 cases have candidate and source reviews under continuation `e9661baa03dbd81d` using Codex exec and Luna subagents. Four calibration replays are separate from the 100-case count.

All 22 independent integrity checks passed, including 63 preserved-file hashes and exact review evidence; eight focused tests passed. Audit processes have exited. No additional model calls are needed for this sample. No label repair or training ran. Model-retained findings remain diagnostic records, not clinical truth or a prevalence estimate. One source review used a Luna collaboration subagent and is labeled separately from CodexJudge output.

The [earlier continuation brief](data/TRAINING_LABEL_AUDIT_HANDOFF.md) is historical context; its ten-complete/ninety-remaining status has been superseded.

## Current state

- **V3 generation complete:** 100 paired development cases, base versus FP32 LoRA Gemma 270M. Three epochs, 498 steps; checkpoint 498 selected by development loss. Dataset `e80798edebe5aba5`, 1,325 training rows, ten parents and twenty child paths.
- **Source-rubric evaluation complete:** all 100 cases, 400 unique measurements with `gpt-6-luna`. Fidelity 0.386 to 0.516 (+0.130); coverage 0.407 to 0.502 (+0.095). No further inference is needed.
- **Paired confidence intervals calculated:** 100,000 paired case BCa bootstrap resamples, seed 42. All-100 fidelity gain +0.130, 95% CI [+0.100, +0.156]; coverage +0.095, CI [+0.065, +0.122]. Wins/ties/losses are 76/15/9 and 65/25/10. Remaining-80 sensitivity intervals are also positive: fidelity [+0.105, +0.165], coverage [+0.06375, +0.12375]. These condition on saved judge scores and case-independence assumptions, not clinical truth or judge rerun variability. No new inference/training. Three focused tests passed; saved score/CSV consistency and unchanged hashes verified.
- **20-case source audit complete:** [report](../results_v3/source_audit_20/REPORT.md) and [case ledger](../results_v3/source_audit_20/CASE_LEDGER.md).
- **Training audit complete:** structure/projection checked on all 1,325 rows; the frozen 100-case sample has source-consistency reviews. The original ten retain assistant pilot adjudications; the remaining 90 have Luna candidate/source reviews. See the [completion report](../results_v3/training_audit_100/continuation_v2/REPORT.md). Parent source checks and disagreements remain separate from raw model counts.
- The full-schema v2/5,000 run and its 100-case generation comparison are recorded above. The training-label audit produced no replacement labels.

## Read next

| Topic | Starting point |
| --- | --- |
| Experiment, schema and generation | [V3 protocol](experiments/REDUCED_SCHEMA_1325_RUN.md) |
| Run history | [Run catalog](experiments/RUN_CATALOG.md) |
| Full source-rubric results | [100-case evaluation](evaluation/REMAINING_VALIDATION_EVALUATION.md) |
| Paired confidence intervals | [Analysis report](../results_v3/paired_confidence_intervals/REPORT.md) |
| Earlier rubric change and judge limits | [20-case reevaluation](evaluation/SOURCE_GROUNDED_REEVALUATION.md) |
| Data versions and cleaning | [Dataset guide](data/README.md) |
| Completed training-label audit | [Report and verification](../results_v3/training_audit_100/continuation_v2/REPORT.md) |
| Review policy | [Annotation policy](CLINICAL_ANNOTATION_POLICY.md) |
| Saved artifacts | [V3 index](../results_v3/README.md) |

The [interactive HTML](Clinical_Extraction_Phases_1_and_2.html) compares v2/v3 generation and the two 20-case judge rubrics. It predates the full-100 source evaluation; use the combined saved summary for those results. `experiment_status.json` records the generation stage; its `llm_evaluation=false` predates the separate judge runs.

## Remaining research work

The run-specific calibration clarifies broad history, admission, combination response and materiality; the 100-case audit is complete. Resolve documented reviewer disagreements and prepare a source-verified correction proposal within the existing 30 paths before creating separately versioned replacement labels. Labels still match literal v2-to-v3 projection; the audit verifies concrete losses of schedules, diagnostic qualifiers and other supported details. Do not blindly restore v2 values, add schema paths or silently repair frozen labels.

A larger data-size experiment or model/rank change remains proposed work. Preserve current schema, prompts, development cases and decoding for controlled comparisons; record steps, supervised tokens and runtime. V2 and v3 use different schemas/prompts/cases, so their F1 difference does not isolate a single intervention.

## Working constraints

Preserve v1/v2/v3 data, adapters, predictions, references, scores, hashes and contracts. Keep audited development cases out of training. Do not launch training or judge calls for repository maintenance (`gemini-4-hydrogen` was used only for the completed `v2_5000` evaluation `8993a8dd5f5f3a18`). Prior handoffs record the user's preference against a code-review workflow for these iterations.

Use FP32 on T4; earlier FP16 runs overflowed. Reproduction needs the recorded runtime stack rather than blindly syncing the newer lockfile. Frozen paths and several execution-source hashes are checked by existing validators; retain them.

Current docs are grouped into guides, experiments, evaluation and data. Older v2 reports, schema-planning evidence and the verbose handoff live in the [archive](../archive/README.md).

Reproduce the confidence intervals with `.venv/statistics-tools/Scripts/python.exe -m scripts.calculate_paired_confidence_intervals`. Isolated dependencies are pinned in `requirements-statistics.txt`; training and judge environments were not changed. `analysis.json` records hashes, software versions, percentile/paired-t checks and supplementary two-metric Bonferroni intervals. The new analysis has not been committed.

## Cleanup verification

All 22 offline tests passed in the isolated DeepEval environment, and the remaining-80 verifier confirmed all 400 combined source measurements and frozen inputs. Local Markdown links were checked after relocation. No model inference or training ran.

The older `check_source_grounded_evaluation` command currently fails its historical `scripts/run_deepeval.py` byte-hash assertion: the runner was subsequently extended for remaining-80 checkpoint/resume support. This cleanup does not change Python sources or rewrite historical provenance to hide that mismatch. Use the remaining-80 checker for current completed-run integrity; retain the old provenance as execution history.
