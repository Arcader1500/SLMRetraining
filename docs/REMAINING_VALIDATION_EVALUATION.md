# Source-grounded evaluation of the remaining 80 validation cases

**Completed:** all 320 additional Luna judgments are saved and verified. The run
hit a usage limit after 38 saved measurements and successfully resumed without
repeating completed keys. No cases or failed calls were replaced with zeroes.

| Source-grounded metric | Baseline, new 80 | Fine-tuned, new 80 | Baseline, all 100 | Fine-tuned, all 100 | Paired gain, all 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Source fidelity | 0.39375 | 0.53000 | 0.386 | 0.516 | +0.130 |
| Source coverage | 0.41625 | 0.51000 | 0.407 | 0.502 | +0.095 |

The final combined evaluation covers all **100 saved development cases and 400
metric measurements**. The original 20 source-rubric cases and their scores were
reused unchanged. Results are in
`results_v3/deepeval_remaining80/judgments/16727c1bd7aaf775/`, including the 80-case
summary/paired CSV and combined 100-case scores, summary and paired CSV.
`completion_checks.json` verifies all keys, means/deltas and frozen inputs.
The run is no longer active; `progress.json` records 320 saved and zero pending.

The user authorized **320 additional metric judgments** with `gpt-6-luna`:
80 previously unevaluated validation cases, both saved model outputs, and two
metrics per output. These cases are the exact complement of the original 20
within the frozen 100-case development set. No quality/JSON-validity filtering
or resampling is performed. Training-data auditing is a separate task.

The rubric is the unchanged `source_grounded_v2`: Source fidelity and Source
coverage. Each metric receives the clinical note, saved prediction and synthetic
reference. The note is authoritative; the reference is secondary. DeepEval stays
at 4.3.4, the judge stays GPT-6 Luna, and Gemini remains disabled. No extraction
inference, training or label repairs are involved.

## Resume after interruption or usage-limit refill

Run the same command from the repository root:

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.run_deepeval --remaining-validation --source-grounded --run --backend codex
```

No settings changes are needed: this batch's `judge_settings.json` already enables
the authorized Codex evaluation. Each invocation verifies the frozen cases,
rubric contract and existing records before continuing.

The score/reason record is flushed to disk and atomically replaced after each
judgment. Completed `(case ID, baseline/fine-tuned, metric)` keys are skipped on
restart. Only a judgment interrupted **before** its successful checkpoint may
need repeating. An incomplete `.pending` file is never treated as a saved score.
An OS file lock prevents two evaluators from overwriting the same run and is
automatically released when a process exits or crashes.

Quota/provider failures stop the run; they are not scored as zero or retried in
a loop. Restart the command after access is available. Ctrl+C also preserves
completed records. A forced process kill may leave `progress.json` saying
`running`; the score checkpoint is authoritative and progress is reconstructed
on the next invocation. No automatic post-refill scheduling is configured.

## Saved artifacts

Under `results_v3/deepeval_remaining80/`:

- `selection_manifest.json`: all 80 IDs, excluded original 20 IDs, all 100 IDs,
  source hashes, original-run score hash and exact rubric.
- `paired_cases.json`: verbatim notes, references, baseline/fine-tuned predictions
  and saved format flags.
- `progress.json`: saved/remaining counts out of 320, complete-case counts,
  current/pending judgment keys, failure category and resume command. Overall
  source-rubric progress includes the original 80 judgments, for a total of 400.
- `judgments/<contract-hash>/scores.json`: authoritative completed judgments,
  including scores, reasons and original format flags.
- `judgments/<contract-hash>/progress.json`: run-specific progress mirror.
- `judgments/<contract-hash>/execution_history.json`: restart times and source
  code hashes for each invocation.

After all 320 judgments finish, the run writes `summary.json` and
`paired_comparison.csv` for the new 80 cases, plus `combined_scores_100.json` and
`combined_summary_100.json` combining the preserved 20-case source-rubric run
with the new 80. No new judging of the original 20 is needed. The older
reference-only rubric remains separate and is never included in this aggregate.

The original source-rubric scores remain in
`results_v3/deepeval_20/judgments/d44ef976ae8d9310/` and are never overwritten.
The HTML report currently documents that completed 20-case evaluation; partial
remaining-80 results are not presented as completed 100-case findings.

## Verification and interpretation

Nine offline tests pass, including exact-complement selection, note inclusion,
provider gating and a simulated usage-limit interruption/resume with no repeated
completed keys, plus reuse of the original 80 scores in the 400-result aggregate.
Every restart checks score ranges, nonempty reasons, unique keys
and equality of saved output-format flags with frozen inputs.

Check saved progress and frozen-input integrity without running a judge:

```powershell
.venv/Scripts/python.exe -m scripts.check_remaining_validation
```

These are source-consistency LLM rubric judgments, not clinician adjudication,
exhaustive claim-level precision/recall or calibrated clinical accuracy. The
original 20 informed rubric development, so keep their provenance distinct from
the remaining 80 when interpreting the final aggregate.
