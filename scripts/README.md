# Script index

Run modules from the repository root (`python -m scripts.<name>`). Execution sources retain their paths/bytes because saved provenance hashes them.

| Category | Modules / files |
| --- | --- |
| Dataset cleaning | `prepare_v2_dataset.py` (historical preparation/shared helpers), `prepare_v3_dataset.py` (current projection/prompts) |
| Saved experiment loading | `phase_results.py` |
| Judge selection/execution | `prepare_deepeval.py`, `run_deepeval.py`, `codex_deepeval_judge.py`, `source_grounded_rubric.py` |
| Training-label audit | `audit_training_data.py`, `analyze_training_projection.py` |
| Offline evidence checks | `check_remaining_validation.py`, `check_source_grounded_evaluation.py` |
| HTML report | `build_phase_visualizer.py`, `phase_visualizer.html`, `check_phase_visualizer.py` (Playwright) |
| Remote notebooks | `run_colab_notebook.py` |

Judge runners prepare/check inputs by default; `--run` explicitly enables inference. Completed evaluation needs no more calls. Gemini remains disabled. Report rebuilding and some checkers write outputs; inspect changes afterward.

The [clinical_sft package](../clinical_sft/) is a separate CLI format. Small evidence-specific builders under `results_v3/source_audit_20/` and `results_v3/training_audit_100/` stay with their inputs.
