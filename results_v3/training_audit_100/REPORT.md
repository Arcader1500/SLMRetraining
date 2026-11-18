# Initial training-data audit, 18 November 2026

The first training-audit stage is complete: structural and projection checks on
all 1,325 saved training examples, a frozen 100-case sample, and ten cases with
both candidate model review and assistant review against the source. **Ninety
sampled cases have not yet received semantic review.** No background audit is
running. Original labels, datasets, adapters and evaluation artifacts are intact.

## Improvement and remaining uncertainty

The source-grounded evaluation shows a positive development-set improvement:
fidelity 0.355 to 0.460 and coverage 0.370 to 0.470, on the same 20 cases. This
supports continuing the project; it does not establish clinical reliability or
identify the cause of each remaining model error. The training audit examines
supervision separately from judge reliability and model capacity.

## Dataset-wide structural checks

All 1,325 training labels satisfy the 30-path schema. All supervised-token masks
have the saved prompt masked and the saved assistant tokens supervised. There
are 1,325 unique saved normalized-note hashes, zero exact normalized-note overlaps
with the 100 current development cases, and no exact duplicate entries within
projected arrays. These checks do not rule out near duplicates, patient overlap,
or problems in the upstream test split.

1,206 notes lack terminal punctuation. Several end visibly mid-sentence. This is
a screening cue, **not** a confirmed count of truncated notes. Labels must not
complete unavailable source outcomes, dispositions, units or time points.

## Important finding: source-supported information was discarded during projection

Every current label exactly matches the literal projection of its saved v2
predecessor. The reduced schema discarded entire fields, including information
that could fit inside retained string values. This was part of schema reduction,
not evidence of accidental dataset corruption. The audit establishes specific
source-supported omissions in the pilot; it does not establish that all dropped
synthetic fields are correct or clinically necessary.

| Dropped v2 field | Field occurrences | Affected training cases |
| --- | ---: | ---: |
| Treatment frequency | 418 | 285 |
| Treatment duration | 311 | 240 |
| Diagnostic-test condition | 1,624 | 1,034 |
| Diagnostic-test details | 1,060 | 772 |
| Symptom aggravating/relieving behaviours | 384 | 338 |
| Treatment details | 872 | 678 |

These are **mechanical field-drop counts**, not confirmed clinical omission
rates. Some information survives elsewhere or by paraphrase. Full counts and
conservative normalized exact-text searches are saved in `projection_analysis.json`.

Source-checked examples:

- **train:119:** the note explicitly lists methylprednisolone “500 mg IV for
  3 days,” prednisone “25mg BD,” and other treatment schedules. V2 stored them in
  `frequency`; v3 retains dose numbers and removes the schedules. The 20g
  methotrexate value is stated in the note and is not a source-consistency error.
- **train:1239:** ciprofloxacin is “400 mg every 12 hours.” The current label keeps
  400 mg; v2's frequency value was removed.
- **train:1052:** the note gives postoperative medication “for 7 days.” V2 stored
  this in `duration`; v3 removes it. Its working diagnosis of peripheral osteoma
  was also stored in a removed diagnostic `condition` field.
- **train:177:** the note explicitly says histopathology “confirmed an ectopic
  pancreas” and that the tumour did not involve resection margins. V2 stored
  these under `condition` and `details`. The current retained pathology result
  gives specimen dimensions and appearance, losing diagnosis and margin status.
- **train:1453:** S-1's twice-daily, three-week-on/two-week-off schedule and its
  continuation after renal insufficiency were retained in v2's `frequency` and
  `details`, both removed from v3.

This provides a concrete supervision problem to address before simply increasing
data size. It does **not** prove these omissions caused a particular model error;
that requires a controlled original-versus-reviewed-label experiment.

## Ten-case pilot and judge reliability

The sample uses seed 42: 50 random training cases, then 50 nonoverlapping targeted
cases, ten each for drug/dose complexity, investigations, chronology,
negation/event status and long targets. Execution alternated the two arms. The
initial pilot comprises five random and five targeted cases, each inspected
against its full supplied note and label.

GPT-6 Luna produced 17 candidate findings. Assistant review classified:

| Disposition | Candidate findings |
| --- | ---: |
| Confirmed source-consistency issues under the stated policy | 6 |
| Annotation/causal/coverage ambiguities | 6 |
| Rejected judge flags | 5 |

Five additional material omissions were identified during assistant review,
giving 11 diagnostic findings across eight pilot cases. These are neither
exhaustive atomic counts nor a training-set defect prevalence estimate. Several
findings bundle related attributes. The explicit-admission rule determines one
confirmed event-role issue: ED presentation alone does not establish an inpatient
admission. It does not prove the patient was never admitted.

Rejected flags include a source-stated methotrexate dose, normal lymph-node
findings already present in both texts, a mutation already retained in history,
and valid history stored in the canonical `physiological context` field. Some
judge explanations explicitly said the fact was supported while still emitting
an error-category record. A mechanical quote match does not catch that semantic
contradiction. Shared-regimen response fields were downgraded from claimed
single-drug errors to causal/annotation ambiguities.

One copied source excerpt abbreviated “intravenous (IV)” as “IV.” Its unique
contiguous token span was recovered from the original note, ignoring only
parentheses/whitespace. All signs, units, words and ordering stayed fixed. The
original rejected response and the span-repair record are retained. Current
evidence quotes all occur exactly in source notes. No prediction or label was
repaired by this mechanism.

## Next work

1. Clarify that medical history's `physiological context` is a broad history field;
   do not flag source-supported contents because of that field's name. Calibrate
   the auditor against the rejected and ambiguous pilot flags before applying
   its categories in bulk. Never equate a candidate flag with a confirmed error.
2. Specify semantic preservation within the **existing 30 paths**: drug frequency
   and route can accompany dose in `dosage`, duration/course anchors in `time`,
   diagnostic condition and qualification in test `result`, and symptom modifiers
   in `details`. This is a proposed mapping policy, not an implemented label edit.
3. Continue source review of the other 90 sampled cases, keeping random and
   targeted results separate. Inspect source-supported field drops and inherited
   synthetic ambiguities before retaining or rewriting them.
4. Build a separately versioned reviewed-label subset, then compare training on
   the same case IDs with the existing labels versus reviewed labels. Keep the
   model, rank, schema and decoding fixed. Do not train on audited development
   cases, and do not generate additional synthetic clinical notes at this stage.

No new training, extraction inference, replacement labels or synthetic clinical
notes were generated. The only new model inference was the ten-case label-audit
pilot, including an evidence-validation retry. This is assistant source review,
not clinician adjudication or clinical verification of the source itself.
