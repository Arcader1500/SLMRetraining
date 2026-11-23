# Training-label audit: 100-case source review complete

All 100 frozen training cases now have source-consistency reviews: 50 random and 50 targeted. The original ten-case pilot is preserved; 90 continuation cases have Luna candidate/source reviews, with reviewer provenance recorded. No audit process is active and no labels or training changed.

Read the [completion report](continuation_v2/REPORT.md), [case ledger](continuation_v2/combined_case_ledger.json), [findings CSV](continuation_v2/findings.csv), [parent disagreements](continuation_v2/parent_disagreements.json) and [independent verification](continuation_v2/verification.json). All 22 integrity checks and eight focused tests passed. Raw model-retained findings are not clinical adjudication or prevalence estimates.

The [initial report](REPORT.md) and files below preserve the pilot and dataset-wide checks.

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
