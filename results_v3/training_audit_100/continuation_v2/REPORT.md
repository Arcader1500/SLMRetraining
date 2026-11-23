# Completed 100-case training-label audit

Completed 19 November 2026. The frozen sample has **100 training cases: 50 random and 50 targeted**. The ten-case pilot is preserved unchanged; all remaining 90 cases now have candidate and source reviews. No labels, training data, adapters, predictions or development scores were changed. No training or validation judging ran.

The audit establishes concrete supervision gaps, including source-supported information lost during schema projection. It also demonstrates that even two agreeing Luna passes can make mistakes. **The retained model findings are diagnostic screening records, not adjudicated clinical defects or a training-set error rate.**

## Scope and execution

- Original pilot: ten cases under v1, with the saved assistant dispositions of 17 flags plus five added omissions. These remain historical v1 results.
- Continuation: 90 cases (45 random, 45 targeted), run `e9661baa03dbd81d`, `gpt-6-luna` through authenticated `codex exec`. Each received a separate source pass; that pass starts fresh but sees the candidate review and projection drops, so it is not blinded and its errors may correlate with the candidate reviewer.
- Accepted source reviews: 89 through Codex CLI (72 ordinary execution records and 17 supplemental corrections), plus one explicitly identified Luna collaboration source review with file tools, `train:248`. That exception is not represented as an unchanged CodexJudge response.
- Four pilot cases were replayed for calibration: train:119, 1052, 24 and 1453. They are excluded from the 90-case continuation counts. The original policy file and 30-path schema are unchanged; calibration is a run-specific appendix.
- Parent source inspection covered 14 additional full notes and labels, including the first ten remaining cases, selected timing/linkage claims and train:901. A Luna subagent separately checked all 27 continuation claims which the source pass retained as clear errors. This is not exhaustive parent re-adjudication of all continuation findings and is not clinician review.

[Protocol](PROTOCOL.md), [pilot calibration](CALIBRATION_REVIEW.md), [calibration examination](CALIBRATION_EXAMINATION.md), and [frozen execution contract](e9661baa03dbd81d/run_contract.json) record the boundaries. Earlier failed calibration evidence is preserved separately and excluded from continuation results.

## Descriptive continuation results

These counts concern only the **90 new cases**. A confirmed disposition means the second reviewer retained a candidate; it does not mean the parent or a clinician confirmed it. Several findings bundle attributes, and others overlap. Screening is capped at six first-pass findings per case and is not an exhaustive claim inventory.

| Record | Random arm | Targeted arm |
| --- | ---: | ---: |
| Cases reviewed | 45 | 45 |
| First-pass candidate flags | 109 | 117 |
| Candidates retained by source reviewer | 74 | 83 |
| Candidates downgraded to ambiguity | 14 | 16 |
| Candidates rejected | 21 | 18 |
| Added second-pass candidate records, including rejected/ambiguous records | 108 | 107 |
| Retained material-omission records | 162 | 170 |
| Retained clear-error records before later source checks | 16 | 11 |

The combined ledger also retains the pilot's 11 diagnostic findings across eight cases. Do not pool arms or protocols into a training-set prevalence estimate. In particular, the broad omission screen produces retained findings in every random case; this is not evidence that all training labels are clinically defective. Materiality, duplication and reviewer mistakes remain substantive limitations.

[Combined summary](combined_summary.json), [100-case ledger](combined_case_ledger.json), and [findings CSV](findings.csv) expose the underlying counts. Those exports preserve raw source-pass classifications. Later disagreements live in separate sidecars rather than silently changing those records.

## Source-verified supervision gaps

The parent verified nine illustrative dropped attributes across seven additional cases against source, v2 field drops and the complete v3 label. These are examples, not an atomic error denominator:

| Case | Source-supported content lost | Existing-schema preservation proposal |
| --- | --- | --- |
| train:1480 | Earlier ambulance pulse and systolic pressure | Examination result with the en-route anchor, separate from arrival measurements |
| train:263 | Prednisone daily frequency and five-day course | Dosage and time, attached to prednisone |
| train:1298 | MRI differential for the carotid-space mass | Test result retaining differential status |
| train:333 | Death reported after salvage treatment | Course outcome in the existing summary, without inventing a discharge event |
| train:783 | Imaging consistent with glomus vagale | Qualified diagnostic interpretation in the MRI result |
| train:725 | Unbearable severity and nightly timing two hours after sleep | Symptom details/time, separate from the later postpartum pattern |
| train:1184 | Ibuprofen frequency range | Dosage alongside the retained 800 mg |

[Source/projection evidence](source_verified_projection_examples.json) contains the exact note quotes and actual dropped v2 fields. [Parent spot review](parent_spot_review.json) records broader coverage checks. The earlier pilot additionally established schedule, pathology and symptom-modifier losses. This supports source-verified folding into retained strings; it does not justify blindly restoring every v2 value or adding schema paths.

All 1,325 labels still match literal v2 projection. Retained false assertions and omitted qualifiers must be traced case by case. The source review's `projection_loss`, `inherited` and `uncertain` attributions are model judgments; the aggregate attribution counts are not independently established causal counts.

## Reviewer errors and unresolved semantics

The second pass rejected 39 of 226 continuation candidate flags and downgraded 30. False flags still include explanations saying the content is supported while assigning an error category. Exact quote/path validation cannot detect that contradiction.

Parent source checks rejected the subagent claim that train:149 lacked the fetal renal finding: it is explicitly retained. Train:940's planned-but-not-completed cystgastrostomy is qualified in the treatment entry and is not listed in its surgery array. Train:1220 already retains splenomegaly in symptoms and examination; repeating it in the imaging result is not an established material omission.

[Parent disagreements](parent_disagreements.json) downgrade two timing claims retained as clear errors by both CLI passes and the source-review subagent: train:877's medication resumption versus discharge, and train:710's approximate age-16 irrigation start. These are plausible narrative sequences with insufficiently explicit timing. The same sidecar records an additional unresolved negation-scope issue in train:1065: the awkward source sentence about nodal disease should not silently become a definitive negative. No outside medical staging interpretation was used to repair it.

[Clear-error source review](CLEAR_ERROR_SOURCE_REVIEW.json) covers all 27 retained continuation clear-error claims. Its independent review downgraded two more claims (train:539 timing and train:150 linkage); earlier agreements for train:877/710 remain preserved alongside the parent's superseding ambiguity decisions. Thus raw clear-error totals must not be quoted as final adjudicated errors.

Broad history belongs in physiological context. Combination-treatment response does not establish single-drug causation. Admission requires admission evidence; a visit alone is insufficient. Cut-off notes must not be completed. Important coverage, source quality and clinical significance still require further adjudication.

## Verification and restart evidence

- Eight focused offline tests passed: frozen sampling, quote rejection, restricted span recovery, calibration, interleaved resume and candidate disposition coverage. [Test evidence](test_evidence.json).
- Independent offline verification passed **all 22 checks**: 63 preservation-baseline byte hashes, frozen sample/arms, pilot integrity, contract/input/prompt/schema hashes, exact 90-case continuation coverage, review schemas/quotes/dispositions, the 100-ID ledger, CSV and summary consistency. [Verification](verification.json).
- Initial bulk processing had 21 case-level evidence failures. Rejected responses, raw attempts and supplemental corrective instructions remain preserved; none was accepted by weakening validation. [Initial errors](e9661baa03dbd81d/bulk_initial_errors.json). Final coverage is 90/90 and there are no unresolved execution errors.
- Accepted cases are checkpointed; one OS writer lock protects the checkpoint. Supplemental reviews were stored separately and merged only after the main writer released its lock. Temporary-directory/permission failures and the earlier failed contract are historical execution evidence. Temporary directories are ignored by Git.
- All audit subprocesses have exited and no audit writer remains active. No commit or push was made. Pre-existing uncommitted statistics work is preserved.

Rebuild exports with:

```powershell
.venv/Scripts/python.exe results_v3/training_audit_100/continuation_v2/build_summary.py --run-dir results_v3/training_audit_100/continuation_v2/e9661baa03dbd81d
.venv/deepeval-tools/Scripts/python.exe results_v3/training_audit_100/continuation_v2/verify_results.py --run-dir results_v3/training_audit_100/continuation_v2/e9661baa03dbd81d
```

These commands perform no model inference. The frozen runner can resume its saved phase, but no further audit calls are needed for this sample. Supplemental execution provenance remains part of reproducing this completed run.

## Next research step

Prepare a separately versioned correction proposal for source-verified training cases, applying the same 30 paths and explicit relationship/status/coverage rules. Resolve the documented disagreements before treating model-retained flags as corrections. A later controlled comparison should keep training IDs/count, model, rank, prompts/schema and decoding fixed while changing labels. This audit does not show that corrected labels improve the model. This audit did not create a replacement-label set or launch retraining or a 5,000-example run. Separate concurrent workspace work is outside this audit.
