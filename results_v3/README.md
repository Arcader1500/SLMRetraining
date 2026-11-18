# V3 result artifacts

The 1,325-example reduced-schema run and all 100 source-rubric case evaluations are complete. The training audit remains partial. See the [run catalog](../docs/experiments/RUN_CATALOG.md).

| Category | Artifacts |
| --- | --- |
| Frozen baseline | [baseline/](baseline/): selection, contract, predictions, diagnostics, scores |
| Training | [finetuned_v3/](finetuned_v3/): adapter, checks, configuration, loss logs, metrics |
| Generation comparison | [comparison/](comparison/): case/aggregate scores, showcase, schema violations, completion checks |
| Reference-only judge | [a6bb10a9fde5e2b4](deepeval_20/judgments/a6bb10a9fde5e2b4/): 20 cases, 80 measurements |
| Source judge, first 20 | [d44ef976ae8d9310](deepeval_20/judgments/d44ef976ae8d9310/): 80 measurements, source rubric, quality notes |
| Source judge, remaining 80 / combined 100 | [16727c1bd7aaf775](deepeval_remaining80/judgments/16727c1bd7aaf775/): 320 new measurements, combined 400-measurement summary |
| Source consistency audit | [source_audit_20/REPORT.md](source_audit_20/REPORT.md): complete diagnostic review |
| Training-label audit | [training_audit_100/REPORT.md](training_audit_100/REPORT.md): all-row structural/projection checks, 10 of 100 semantic reviews |
| Execution evidence | Root progress/status JSON, runner logs, stage-local provenance |
| Transfer snapshots | Root ZIP files, including `clinical_v3_paused.zip`; historical downloads |

Use stage-local checks and summaries for current outcomes. Generation-stage `experiment_status.json` has `llm_evaluation=false` from before the separate judge runs. Earlier paused/progress snapshots remain evidence. Predictions, labels and scores were not regenerated during organization. Evidence-specific report builders stay beside their inputs because they resolve paths relative to their own directory.
