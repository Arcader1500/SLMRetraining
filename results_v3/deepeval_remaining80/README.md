# Remaining validation evaluation: 80 cases, 320 new judgments

**Complete:** 320/320 new judgments, zero pending. The combined evaluation has
400 judgments on all 100 saved validation cases. Source fidelity is 0.386 baseline
versus 0.516 fine-tuned; source coverage is 0.407 versus 0.502. The original
20-case scores are unchanged. The interrupted run resumed from 38 saved results.
See `judgments/16727c1bd7aaf775/combined_summary_100.json`,
`combined_paired_comparison_100.csv` and `completion_checks.json` in that folder.

**Read `progress.json` for current status and counts.** Saved scores are in
`judgments/16727c1bd7aaf775/scores.json`. The initial 20-case source-rubric run is
preserved separately and is not rerun. Overall completion is 100 cases and 400
source-rubric judgments; older reference-only results are a separate protocol.

Resume after interruption or refill:

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.run_deepeval --remaining-validation --source-grounded --run --backend codex
```

Every successfully checkpointed key is skipped. A judgment interrupted before
its checkpoint may repeat. Errors stop the run and do not become zero scores.
No automatic quota polling, scheduling, Gemini fallback, training or output
regeneration is enabled. Do not start a second writer or remove checkpoint files.

Verify saved results without inference:

```powershell
.venv/Scripts/python.exe -m scripts.check_remaining_validation
```

See [the protocol](../../docs/evaluation/REMAINING_VALIDATION_EVALUATION.md) for immutable
selection/rubric provenance, atomic checkpoint behavior and final combined files.
