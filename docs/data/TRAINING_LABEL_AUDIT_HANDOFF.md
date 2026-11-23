# Training-label audit: detailed continuation brief

> Superseded status: the 100-case audit was completed on 19 November 2026 using Codex exec and Luna subagents. Read the [completion report](../../results_v3/training_audit_100/continuation_v2/REPORT.md), [100-case ledger](../../results_v3/training_audit_100/continuation_v2/combined_case_ledger.json) and [verification](../../results_v3/training_audit_100/continuation_v2/verification.json). No audit process is active; no labels or training changed. The remaining text preserves the earlier ten-case continuation brief as execution history.

Updated 19 November 2026. Workspace: `C:/Users/atharva.bedekar/PycharmProjects/SLMRetraining`.

This is the starting brief for a fresh chat resuming the **training-label audit**.
The present turn only documents the work; it does not launch further reviews,
change labels or start training. The full 100-case semantic audit is incomplete.

## Objective and current boundary

Determine whether training supervision contains unsupported assertions, wrong
drug/test/event relationships, material omissions or ambiguous annotation rules.
Separate problems inherited from synthetic annotations from information lost in
schema projection and from mistakes made by the audit judge. Establish a
source-grounded annotation/mapping policy before constructing replacement labels.

| Work | Saved status |
| --- | --- |
| Structural checks on training data | All 1,325 rows checked |
| V2-to-v3 projection analysis | All 1,325 labels checked; all match literal projection |
| Frozen semantic-audit sample | 100 training cases: 50 random and 50 targeted |
| Candidate model reviews | 10 cases, GPT-6 Luna |
| Assistant source review | Those same 10 cases, five from each arm |
| Remaining semantic reviews | 90 cases: 45 random and 45 targeted |
| Label repair, replacement training set, retraining | Not performed |

No training-audit process was started by this handoff turn. Saved progress says
no active audit process. The validation evaluation is already complete and must
not be confused with these 90 unfinished **training** reviews.

## Why this is the next task

The saved 100-case source-grounded evaluation of the Gemma 270M baseline and
fine-tuned v3 model is complete: 400 Luna judgments. Fidelity increased from
0.386 to 0.516; coverage from 0.407 to 0.502. The paired mean gains have 95% BCa
bootstrap intervals of [+0.100, +0.156] and [+0.065, +0.122], respectively.
The conclusion remains positive on the 80 cases not used to develop the rubric.

These are improvements in saved judge assessments, not clinical validation or
proof that every case improved. They support investigating remaining supervision
problems. They do not identify the cause of individual model failures. Do not
rerun validation judging merely to resume this audit. See the
[evaluation protocol/results](../evaluation/REMAINING_VALIDATION_EVALUATION.md)
and [paired-interval analysis](../../results_v3/paired_confidence_intervals/REPORT.md).

The completed [20-case model-output source audit](../../results_v3/source_audit_20/REPORT.md)
identified drug-dose-response mixing, test-result mixing, chronology errors,
planned/refused/performed event confusion, omissions and repetition. Those are
diagnostic targets for inspecting training labels; they are not established
training-label error rates or proof that label problems caused model errors.

## Authoritative data and schema

Use these existing local artifacts, preserving their contents:

- [V3 train JSONL](../../prepared_clinical_dataset/e80798edebe5aba5/train.jsonl),
  [development JSONL](../../prepared_clinical_dataset/e80798edebe5aba5/validation.jsonl)
  and [manifest](../../prepared_clinical_dataset/e80798edebe5aba5/manifest.json).
- [V2 train JSONL](../../prepared_clinical_dataset/eeff5efa1619f198/train.jsonl)
  for locating attributes removed by projection. V2 and v3 retain the same
  training IDs and source notes; their output labels differ.
- [Dataset guide](README.md) for provenance, cleaning and hash conventions.
  `latest_v3.json` identifies v3; the unqualified `latest.json` still identifies v1.

Source dataset: `AmareshHebbar/clinical-summarizer-sft`, pinned revision
`4ca20e0a38cc9235045c973b5503d49952fd1fac`. Training preparation accepted 1,325
rows from the first 1,500 candidates, rather than auditing all 24,000 upstream
training examples. References are synthetic annotations, not independent clinical
gold. The supplied note is the authority for source consistency, but the note
itself is not medically verified by this task.

Keep **all ten parents and only 30 distinct schema paths**: ten parent paths plus
twenty child paths. Multiple array entries do not create additional schema paths.

| Parent | Allowed children |
| --- | --- |
| visit motivation | String value, no children |
| admission | reason |
| patient information | age, sex |
| patient medical history | physiological context |
| surgeries | Type, time, details |
| symptoms | name of symptom, location, time, details |
| medical examinations | name, result |
| diagnosis tests | test, result |
| treatments | name, dosage, time, reaction to treatment |
| discharge | discharge summary |

Exact implementation: [prepare_v3_dataset.py](../../scripts/prepare_v3_dataset.py).
Use the coherent v3 extraction instruction, not the older contradictory SOAP
wording. Audit evidence belongs in sidecars, not new model-output keys.

## Dataset-wide findings already established

All 1,325 v3 labels satisfy the schema and have consistent saved supervised-token
masks. There are 1,325 unique saved normalized-note hashes, no exact normalized
overlap with the current 100 development notes, and no exact duplicate entries
within projected arrays. Near duplicates, patient overlap and official-test
separation have not been established.

1,206 notes lack terminal punctuation, and several visibly stop mid-sentence.
This heuristic is **not** a confirmed truncation count. Never finish unavailable
units, outcomes, time points, procedures or dispositions because they seem likely.

Every v3 label matches literal projection of its v2 predecessor. Projection drops
entire fields without folding their values into remaining strings. Some dropped
content is source-supported and still expressible inside the retained schema.
This was part of schema reduction, not evidence that preparation accidentally
loaded the wrong labels.

| Dropped v2 field | Occurrences | Affected cases |
| --- | ---: | ---: |
| treatments.frequency | 418 | 285 |
| treatments.duration | 311 | 240 |
| diagnosis tests.condition | 1,624 | 1,034 |
| diagnosis tests.details | 1,060 | 772 |
| symptoms.behaviours affecting the symptom | 384 | 338 |
| treatments.details | 872 | 678 |

These are mechanical field-drop counts, **not clinical omission/error rates**.
Some information survives elsewhere or by paraphrase; some older synthetic
values may themselves be unsupported. Do not blindly restore every v2 field.

## Frozen sample and reviewed cases

Sample root: [training_audit_100](../../results_v3/training_audit_100/).
[selection_manifest.json](../../results_v3/training_audit_100/selection_manifest.json)
freezes the 100 IDs and hashes; do not resample. Seed is 42. The targeted arm
excludes the random arm and chooses ten cases per mechanism using deterministic
round-robin ranking: drug/dose complexity, investigations, chronology,
negation/event status, and long targets. These are heuristic selections, not
confirmed failures. Do not pool the two arms to estimate training-set prevalence.

`sample.json` stores random cases first and targeted cases second. Actual model
execution interleaves the two arms. The completed pilot is:

| Order | Case | Arm | Important review point |
| ---: | --- | --- | --- |
| 1 | train:983 | Random | Four-kilogram weight-loss magnitude omitted; whether pleural-fluid nondifferentiation is material is a policy question |
| 2 | train:119 | Targeted: drug/dose | Source-supported medication schedules lost from frequency fields; source-stated methotrexate 20g is not a source-consistency error |
| 3 | train:1239 | Random | Ciprofloxacin every-12-hours frequency lost; admission-cause and antibiotic-response wording are ambiguous rather than established clear errors |
| 4 | train:1045 | Targeted: investigations | No material source-consistency issue established in this pilot; this is not exhaustive certification |
| 5 | train:1052 | Random | Seven-day postoperative duration and source-qualified working diagnosis lost; normal lymph-node findings and valid historical context were wrongly flagged |
| 6 | train:1453 | Targeted: chronology | S-1 schedule and continuation after renal insufficiency lost; shared chemotherapy remission under two drugs is a causal-policy ambiguity |
| 7 | train:24 | Random | Missing chest-pain modifiers; ED presentation does not establish inpatient admission under the stated policy; retained mutation was wrongly flagged |
| 8 | train:1108 | Targeted: negation/status | Broad normal-examination wording alongside separately recorded abnormal BP needs scope qualification, not an automatic contradiction label |
| 9 | train:177 | Random | Final ectopic-pancreas diagnosis and uninvolved margins lost from pathology condition/details before the note cutoff |
| 10 | train:676 | Targeted: long target | Explicit angiographic confirmation of AEF omitted from retained result |

In unchanged execution order, the next cases are `train:1480` (random),
`train:263` (drug/dose), `train:1298` (random), `train:149` (investigations),
`train:1220` (random), `train:333` (chronology), `train:783` (random),
`train:725` (negation/status), `train:1184` (random), `train:940` (long target).
All remaining IDs are saved in `progress.json`; its list uses sample storage
order and should not be mistaken for the interleaved execution order.

## Pilot decisions and evidence

Saved model run: `judgments/e1a7efa71d6b7cf2/`, model `gpt-6-luna`.
All ten cases received candidate review and subsequent assistant source review.
Of 17 candidate flags, **six were confirmed**, **six downgraded to policy
ambiguity**, and **five rejected**. Assistant review found five additional
omissions, yielding 11 diagnostic findings across eight pilot cases. Several
findings bundle related attributes; these are not exhaustive atomic denominators
or a clinical defect rate. Assistant confirmation is not clinician adjudication.

Important false-flag patterns to fix before scaling:

- A finding can quote supported text and even say it is supported while still
  carrying an error category. Exact substring validation does not catch this.
- `patient medical history.physiological context` is the canonical broad history
  field; its name must not cause rejection of ordinary history such as absent
  prior facial trauma.
- The label already contains the nonpalpable lymph-node finding and prothrombin
  mutation flagged as errors. Inspect the entire label, not isolated leaves.
- Do not medically correct a source-stated dose when auditing source fidelity.
  If source quality itself needs review, keep that distinct from a label error.
- A shared outcome of combination therapy placed under its constituent drugs
  requires attribution-policy review; it does not automatically assert that each
  drug alone caused that outcome.

Authoritative dispositions are in `pilot_adjudications.json` and
`pilot_review.csv`. Preserve the raw candidate flags. The original pilot report
still quotes the earlier 20-case evaluation; current full-100 results and paired
intervals are the values above. That historical paragraph is not an audit reset.

## Artifact map

All paths below are relative to `results_v3/training_audit_100/`.

| File | Purpose |
| --- | --- |
| README.md, REPORT.md | Initial audit status and findings |
| structural_scan.json | Dataset-wide representation/mask/overlap checks |
| selection_manifest.json, sample.json | Frozen sample, original notes/labels, group, heuristics and JSON-pointer leaf paths |
| projection_analysis.json, projection_fields.csv | All-training projection counts; exact-text absence is not semantic absence |
| sample_projection_drops.json | Dropped v2 field values for the selected 100 |
| progress.json | Saved ten-case screening/review summary and remaining IDs |
| judgments/e1a7efa71d6b7cf2/run_contract.json | Frozen pilot prompt, policy snapshot, response schema, model and selection digest |
| judgments/e1a7efa71d6b7cf2/reviews.json | Ten accepted candidate-review objects; primary checkpoint for that run |
| judgments/e1a7efa71d6b7cf2/candidate_findings.csv | Raw model flags, not confirmed errors |
| pilot_adjudications.json, pilot_review.csv | All 17 dispositions plus five assistant-added omissions |
| review_initial_pilot.py | Rebuilds the manually encoded initial-ten review sidecars; it is not a generic reviewer for future cases |
| validation_checks.json | Previously checked quote/path evidence, sample/source hashes and counts |

The model schema asks for three to five supported checks and at most six
candidate findings per case. Categories include unsupported addition, wrong
linkage/value, chronology, negation/uncertainty, event status, inappropriate role,
omission and repetition. Classification distinguishes clear errors, material
omissions and policy ambiguities. This capped screening is not exhaustive.

`validate()` checks exact source substrings and label excerpts at provided leaf
paths, or an appropriate section path for an omission. One failed excerpt was
recovered from a unique contiguous source-token span, ignoring **only**
parentheses/whitespace. Signs, units, negation, words and order remain fixed.
Raw rejected evidence and `evidence_span_repairs` are retained. This is evidence
span recovery, not source/model/label repair or permission for broad fuzzy matching.

## Scripts, commands and restart pitfalls

- [audit_training_data.py](../../scripts/audit_training_data.py): prepares the
  selection, screens structure, builds the label-audit prompt, executes Luna
  reviews and exports candidates. It does not rewrite labels.
- [analyze_training_projection.py](../../scripts/analyze_training_projection.py):
  verifies v2/v3 correspondence and measures removed fields.
- [test_training_audit.py](../../tests/test_training_audit.py): three focused tests
  for deterministic training-only sampling, evidence rejection and safe quote-span
  recovery. They passed previously; do not claim tests were rerun by this brief.

Preparation and tests without model inference (these can refresh derived sidecars):

```powershell
.venv/Scripts/python.exe -m scripts.audit_training_data
.venv/Scripts/python.exe -m scripts.analyze_training_projection
.venv/Scripts/python.exe -m unittest tests.test_training_audit -v
```

The pilot's execution command was:

```powershell
.venv/deepeval-tools/Scripts/python.exe -u -m scripts.audit_training_data --run --limit 10
```

`--limit` means the total interleaved prefix to consider, **not that many new
reviews**. With an identical complete contract, `--limit 100` considers the whole
sample and skips the ten cached cases. The default limit is 100, so do not run
`--run` casually. There is no separate `run_judge` settings switch for this script.

Before a bulk run, compare the current prompt/policy/schema contract with the
saved one. As checked during preparation of this brief, current `rubric()` text
matches the pilot instructions. Editing the annotation policy, prompt, response
schema or model changes the hashed run directory. A newly calibrated audit will
then **not automatically inherit the pilot's ten cached reviews**. Preserve old
evidence, explicitly decide which pilot cases need recalibration and record the
new protocol/contract. Do not silently mark old reviews as new-protocol results.

The training auditor is less robust than the separately improved validation
runner: it atomically replaces `reviews.json` after each accepted case, but has
no OS writer lock, no per-case progress export, no explicit fsync and no
quota-failure progress handler. A failure can leave `progress.json` or candidate
CSVs behind the accepted reviews. Recover from the actual run's `reviews.json`,
not a stale summary, and never run two writers concurrently. Improve this before
an interruption-prone bulk audit if needed; do not assume validation-run resume
guarantees automatically apply to the training script.

`review_initial_pilot.py` asserts exactly ten pilot cases. Do not rerun it against
a now-expanded `reviews.json` or overwrite the pilot adjudications to fit a new
run. Add separately versioned review records for additional cases.

## Suggested order for the fresh chat

1. Read this brief, the policy and pilot adjudications; verify the saved ten-case
   checkpoint and frozen sample before making new calls. Use source notes to
   resolve disputed flags, not the model's category field alone.
2. Clarify broad history-field semantics, combination-treatment attribution,
   admission evidence and what counts as a material omission. Calibrate an
   amended auditor on known supported, erroneous and ambiguous pilot examples.
   Preserve version 1 and record new-contract boundaries.
3. Define source-verified preservation **within the existing 30 paths**: frequency
   and route can accompany dose in `dosage`; duration/course anchors in `time`;
   diagnostic condition/status/qualifiers in test `result`; symptom modifiers in
   `details`; relevant historical context in the existing history string. These
   are proposals, not an implemented mapping or universal blind concatenation.
4. Continue the remaining 90 source reviews, keeping random and targeted summaries
   separate. Track raw flags, accepted findings, rejected flags, policy ambiguity,
   unsupported inherited labels and verified projection losses separately. Review
   both hallucinated assertions and important source facts missing from the label.
5. Only after the audit/policy is ready, prepare a separately versioned reviewed
   subset and concrete correction proposal. A later controlled experiment should
   compare original versus reviewed labels on the **same training IDs/count**,
   with model, rank, prompt/schema and decoding held fixed as appropriate and
   all protocol changes recorded. It has not been launched or approved by this
   documentation request.

Do not start a 5,000-example run, change model/rank/adapter type, generate new
clinical notes or retrain merely because these options were previously discussed.
Do not add audited development cases to training or repair frozen development
references silently. A full case can contain correct labels alongside omissions;
do not discard it solely because the judge emits a flag.

## Workspace and operating constraints

Preserve all original data, adapters, outputs, scores, selection manifests and
contracts. The annotation policy stays at [its existing path](../CLINICAL_ANNOTATION_POLICY.md)
because the auditor reads it into the prompt. Frozen files and several execution
sources have byte hashes; `.gitattributes` preserves experiment bytes. An older
validation checker fails its historical runner-source hash after legitimate
runner changes; do not falsify old provenance to hide that difference.

Gemini remains disabled. No code-review workflow should be invoked for these
fine-tuning iterations, per the user's established preference. No token/key
files should enter artifacts. Current statistics additions and this handoff are
uncommitted; preserve that work and do not infer a new commit/push request.

The next chat should resume this audit from its saved state. No further audit
inference or source-label modifications were performed while writing this brief.
