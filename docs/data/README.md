# Datasets, cleaning and schema projection

Source: `AmareshHebbar/clinical-summarizer-sft`, revision `4ca20e0a38cc9235045c973b5503d49952fd1fac`: 24,000 training, 3,000 validation and 3,000 test records. Stored targets are ten-section JSON despite the inherited SOAP instruction. No official test evaluation is recorded.

## Frozen versions

| Version | Directory | Train / development | Purpose |
| --- | --- | ---: | --- |
| V1 | [900825a06d38a006](../../prepared_clinical_dataset/900825a06d38a006/) | 1,325 / 10 | Historical pilots |
| V2 | [eeff5efa1619f198](../../prepared_clinical_dataset/eeff5efa1619f198/) | 1,325 / 30 | Cleaned full schema |
| V3 | [e80798edebe5aba5](../../prepared_clinical_dataset/e80798edebe5aba5/) | 1,325 / 100 | Current reduced schema and rebuilt prompts |

`latest.json`, `latest_v2.json` and `latest_v3.json` are version-specific pointers. The unqualified pointer still identifies v1; use `latest_v3.json` for v3. Each version contains JSONL, a saved DatasetDict and a manifest. Cleaning/rejection logs and projection audits belong alongside their dataset, not in a separate mutable clean copy.

## Cleaning stages

[V2 preparation](../../scripts/prepare_v2_dataset.py) inspects the first 1,500 training candidates. It conservatively escapes literal control characters, rejects unresolved/ambiguous JSON, duplicate keys and invalid schemas, removes placeholder/scaffolding values, normalizes allowed shapes and removes exact normalized-note duplicates within/across splits. It accepts 1,325 training rows. Full prompt-plus-answer sequences must fit the limit; targets are not silently truncated. The [historical briefing](../../archive/docs/v2/TRAINING_AND_EVAL_BRIEFING.md) records detailed rules and counts.

[V3 preparation](../../scripts/prepare_v3_dataset.py) retains training IDs and notes, projects labels to ten parent paths plus twenty child paths, and rebuilds prompts/masks. Retained values stay verbatim; entries emptied by projection are dropped. Distinct events remain separate even if projected values coincide. The seeded 100-case development selection excludes the old 30 and comes from 2,803 eligible candidates. The manifest, `projection_audit.json`, `preparation_log.json` and `reference_review_sample.json` record decisions. Exact allowed keys are in `SCHEMA` and the saved manifest; see the [current protocol](../experiments/REDUCED_SCHEMA_1325_RUN.md).

## Quality and provenance

Cleaning fixes representation; it does not certify clinical facts or reconstruct cut-off notes. Current labels match literal v2 projection, which can lose supported schedules and diagnoses. The [training audit](../../results_v3/training_audit_100/REPORT.md) separates mechanical drops from verified omissions. No semantic label repair has occurred.

Exact normalized-note train/development overlap is zero; near duplicates, patient overlap and official-test separation are not established. Keep audited development cases out of training. Corrections require new versioned labels/contracts.

Manifest split hashes are canonical parsed-row digests, not JSONL byte hashes. Other provenance records store byte hashes. Preserve both paths and contents of frozen artifacts.
