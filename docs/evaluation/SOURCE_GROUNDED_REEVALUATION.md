# Source-grounded reevaluation of the frozen 20 cases

The user authorized reevaluating the same baseline and fine-tuned predictions
using fidelity and coverage against the supplied clinical notes. This changes
the judge rubric, not the extraction models or their saved generations.

**Completed 18 November 2026:** all 20 paired cases, 40 saved outputs and 80
judgments with `gpt-6-luna`. Scores are on a 0-1 rubric scale.

| Updated metric | Baseline | Fine-tuned | Mean paired difference |
| --- | ---: | ---: | ---: |
| Source fidelity | 0.355 | 0.460 | +0.105 |
| Source coverage | 0.370 | 0.470 | +0.100 |

For each metric, fine-tuned scores are higher on 13 cases, equal on six and lower
on one. The original reference-only scores remain 0.335/0.375 for fidelity and
0.410/0.455 for coverage. Different truth sources and rubric instructions make
between-rubric score changes unsuitable as additional model-improvement claims.

Verification passed: all 80 unique score keys and case IDs, recomputed means and
paired deltas, unchanged frozen inputs and original scores, and six offline
tests. Headless Chrome checks passed at desktop and 390px mobile widths, including
both rubric tables and exact per-case saved reasons, with no page errors or
external requests. The [updated HTML report](../Clinical_Extraction_Phases_1_and_2.html)
contains both runs and the reliability notes below.

## Protocol

- Frozen pairs: `results_v3/deepeval_20/paired_cases.json`, same seed-42 IDs and
  exact notes, references and raw outputs as the original evaluation.
- Judge: authenticated Codex CLI, `gpt-6-luna`, DeepEval 4.3.4. Gemini remains
  disabled. No extraction inference, retraining or output repair.
- New version: `source_grounded_v2`; full instructions are in
  [source_grounded_rubric.py](../../scripts/source_grounded_rubric.py) and the saved
  run contract. All three evaluation parameters are explicitly included:
  `input`, `actual_output`, `expected_output`.
- Two metrics, now named **Source fidelity** and **Source coverage** to identify
  their authority. Source fidelity assesses expressed assertions; Source
  coverage assesses retention of material schema-relevant source facts. Reference
  concerns appear in reasons, rather than becoming a third score. Syntax/schema
  metrics remain separate.
- The note is authoritative. The synthetic reference is a fallible secondary
  checklist. Preserve drug-dose-response and test-result relations, patient versus
  relative context, negation, uncertainty, event status and time. Do not invent
  doses or complete truncated text. Read malformed prefixes and arrays without
  repairing predictions. Explicit facts in history/discharge or neutral prose
  retain credit; clinical role changes remain errors.
- Reasons request source/output excerpts, explicit error categories and reference
  concerns. Each G-Eval result is checkpointed. The underlying 0-10 rubric score
  is normalized to 0-1 by DeepEval; CLI token-probability weighting is unavailable.
  These are rubric scores, not exhaustive claim precision/recall.

The original reference-only run is preserved at
`results_v3/deepeval_20/judgments/a6bb10a9fde5e2b4/`. The updated run is
`results_v3/deepeval_20/judgments/d44ef976ae8d9310/`. The frozen selection
manifest retains its original reference-only preparation instructions; the new
run contract records the new instructions and the hash of those same pairs.

## Execution and verification

Current maintenance note: the historical checker below now detects a runner-source hash mismatch because later remaining-80 checkpoint/resume changes superseded the code used for this run. Original run provenance and scores remain unchanged. See the [current handoff](../SESSION_HANDOFF.md) and [full-100 evaluation](REMAINING_VALIDATION_EVALUATION.md).

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.run_deepeval --run --backend codex --source-grounded
.venv/Scripts/python.exe -m scripts.check_source_grounded_evaluation results_v3/deepeval_20/judgments/d44ef976ae8d9310
.venv/Scripts/python.exe -m scripts.build_phase_visualizer
.venv/deepeval-tools/Scripts/python.exe -m scripts.check_phase_visualizer
```

Execution still requires `run_judge=true`; Gemini is never enabled automatically.
The original default command retains the original rubric. Changing rubric
instructions creates a different contract hash and cannot resume this run's
scores silently.

`execution_provenance.json` records the CLI/Python versions, command and source
hashes. `completion_checks.json` verifies all 80 unique results, all 20 case IDs,
saved format flags, aggregate means/deltas, original-score preservation and frozen
input hashes. The HTML embeds both rubric runs, individual scores/reasons and
their full instructions. It makes no external requests.

## Interpretation and judge limitations

Comparisons between baseline and fine-tuned predictions **within** a rubric are
paired. Changes **between** rubrics are changes in assessment, not additional
fine-tuning improvement. The same 20 cases were already audited and informed this
rubric; they are development/calibration cases, not a new unseen validation set.

Source-note access removes a reference-only information restriction but does not
establish judge reliability. A non-exhaustive spot-check identified residual
reference-reading mistakes: baseline 593 fidelity says the reference omits restored
flow, though its treatment response includes it; fine-tuned 113 coverage says the
reference omits prednisone 20 mg/day, though that dose is explicit. Some fidelity
reasons also discuss omissions despite the rubric assigning those to coverage.
Reasons alone cannot establish how much this influenced scores. Evidence is in
the run's `quality_notes.json` and displayed in the HTML. Scores remain unmodified.

No clinician calibration, exhaustive assertion inventory, significance claim or
new clinical accuracy estimate is provided by this reevaluation.
