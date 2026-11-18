# Notebook workflows

| Location | Workflow |
| --- | --- |
| [v3_1325/](v3_1325/) | Current: `00_prepare`, `01_baseline_eval`, `02_finetune`, `03_eval_and_compare`, `04_deepeval_paired_20` |
| Root notebooks `01` through `03` | Historical full-schema v2 baseline, training and comparison |
| [archive/legacy_notebooks/](../archive/legacy_notebooks/) | Earlier pilots |

Canonical v3 notebooks contain executed outputs. `_output.ipynb` siblings and ZIP files are execution/download snapshots. Preserve outputs/counts. Notebook 04 records the original reference-only run; later source-rubric judging ran through the CLI.

Use the [v3 protocol](../docs/experiments/REDUCED_SCHEMA_1325_RUN.md) and notebook setup cells. Colab paths are remote: results under `/content/results_v3`, helpers/data under `/content/clinical_v3`. Do not mix v2/v3 or standalone CLI contracts. Cleanup requires no notebook reruns.
