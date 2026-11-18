# Training-label audit: initial pilot completed

The full 100-case semantic audit is **not complete**. A frozen training-only
sample contains 50 random cases and 50 targeted cases. The initial ten cases
(five from each arm) have model candidate reviews plus assistant source review.
No audit process is currently running; 90 cases remain for semantic review.

Read [REPORT.md](REPORT.md) for the findings and next priorities.

- `structural_scan.json`: all 1,325 training examples, schema/mask/duplicate and
  exact train/development overlap checks.
- `selection_manifest.json`, `sample.json`: reproducible 100-case selection,
  original notes, unchanged labels, leaf paths, screening signals and hashes.
- `projection_analysis.json`, `projection_fields.csv`: mechanical v2-to-v3 field
  drops across all 1,325 examples. These are not clinical error counts.
- `sample_projection_drops.json`: dropped field values for the selected 100.
- `judgments/e1a7efa71d6b7cf2/`: frozen GPT-6 Luna audit contract and ten candidate
  reviews; candidate CSV, original response/rejected-evidence files where saved.
- `pilot_adjudications.json`, `pilot_review.csv`: dispositions of all 17 model
  flags plus five assistant-added omissions. Original model flags are preserved.
- `validation_checks.json`: evidence, source hashes and count checks.

Review records are assistant/model source-consistency judgments, not clinician
adjudication. Exact evidence checks do not establish semantic correctness.
The mixed random/targeted pilot must not be interpreted as a dataset error rate.

`review_initial_pilot.py` rebuilds the saved adjudication sidecars. Running
`python -m scripts.audit_training_data` prepares/revalidates without inference.
The explicit `--run --limit 10` flag was used for the initial model pilot; a
larger limit runs additional cases and incurs additional judge calls. The
runner checkpoints accepted cases and never changes training labels. Its
instructions are frozen in each run contract. Changes to the annotation policy
produce a new contract rather than silently reusing old judgments.
