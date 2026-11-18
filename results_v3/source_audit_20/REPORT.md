# Source-grounded audit of the frozen 20 cases

Completed 18 November 2026. All 20 supplied notes, references, baseline outputs,
fine-tuned outputs and saved judge reasons were inspected. This is an assistant
source-consistency review, not clinician adjudication. Original predictions,
references and scores remain unchanged. No new inference or training ran.

Fine-tuning extracts more usable content and organizes it better, but still
mixes drugs, doses, tests, outcomes and time points. Reference defects and
reference-only judging explain some penalties; they do not explain away the
verified model errors. The evidence supports a mixed improvement, not a reliable
numerical estimate of clinical accuracy.

## Scope and counting policy

Eight selected probes per case cover age, sex and six clinical facts: **160 probes
and 320 paired outcomes**. Selection was diagnostic and partly informed by
observed failures. These are not exhaustive or representative inventories of
source facts or generated claims. Some probes contain related components rather
than atomic facts. Counts are not precision, recall, population error rates or
replacement DeepEval scores. No significance claim is made from this sample.

`S` means the named fact is supported with its clinical role preserved. Explicit
events in history, discharge or neutral prose count outside a preferred schema
slot. `P` means readable content has an inappropriate role, such as a finding
called surgery. `C` means wrong value/relationship, `X` means correct and
incompatible versions coexist, `O` means absent from all readable output, and
`A` means partial or ambiguous evidence. Correct subclaims can coexist with
independent errors in adjacent fields. Malformed output is read without repair;
existing whole-object format scores remain unchanged.

| Outcome | Baseline clinical /120 | Fine-tuned clinical /120 | Baseline demographics /40 | Fine-tuned demographics /40 |
| --- | ---: | ---: | ---: | ---: |
| Supported (S) | 46 | 60 | 27 | 38 |
| Inappropriate role (P) | 13 | 4 | 0 | 0 |
| Wrong value/relation (C) | 6 | 14 | 2 | 1 |
| Mixed correct/inconsistent (X) | 3 | 4 | 9 | 0 |
| Omitted (O) | 50 | 35 | 1 | 1 |
| Partial/ambiguous (A) | 2 | 3 | 1 | 0 |

Among clinical probes, 23 baseline omissions become supported facts. Nine
baseline supported facts become omissions and four become wrong-value/relation
outcomes. More incorrect expressed facts alongside fewer omissions is compatible
with a model extracting more while still struggling with event binding. It does
not establish worse precision without a full claim inventory.

## Counts by clinical field

Each cell is **S / P / C / X / O / A**, in that order. Fields describe probe
content, not exact JSON paths. Machine-readable field counts and affected cases
are in `field_outcomes.csv`; all probe evidence is in `probes.csv` and `audit.json`.

| Field | Baseline | Fine-tuned |
| --- | --- | --- |
| Admission | 1 / 0 / 0 / 0 / 1 / 0 | 0 / 1 / 0 / 1 / 0 / 0 |
| History | 11 / 3 / 0 / 0 / 1 / 0 | 10 / 0 / 1 / 0 / 3 / 1 |
| Investigation | 9 / 5 / 1 / 0 / 16 / 1 | 18 / 0 / 4 / 1 / 9 / 0 |
| Procedure | 7 / 0 / 1 / 2 / 4 / 1 | 5 / 0 / 1 / 1 / 6 / 2 |
| Symptom | 7 / 3 / 3 / 0 / 1 / 0 | 9 / 1 / 0 / 0 / 4 / 0 |
| Treatment | 10 / 2 / 1 / 1 / 19 / 0 | 13 / 1 / 7 / 1 / 11 / 0 |
| Outcome | 1 / 0 / 0 / 0 / 3 / 0 | 2 / 1 / 0 / 0 / 1 / 0 |
| Discharge | 0 / 0 / 0 / 0 / 2 / 0 | 2 / 0 / 0 / 0 / 0 / 0 |
| Chronology | 0 / 0 / 0 / 0 / 2 / 0 | 0 / 0 / 1 / 0 / 1 / 0 |
| Visit purpose | 0 / 0 / 0 / 0 / 1 / 0 | 1 / 0 / 0 / 0 / 0 / 0 |

Investigation extraction supplies the largest supported-probe increase. Treatment
omissions decrease, but wrong treatment relations increase from one to seven.
Procedure and history retention do not show the same consistent improvement.

The ledger has **104 diagnostic findings**: 51 baseline and 53 fine-tuned,
affecting all 20 cases for each model. A finding can bundle related errors,
overlap a probe or cover several leaves. Counts are not severity weighted or
exhaustive. Omissions are primarily recorded through probes.

| Primary category | Baseline findings (cases) | Fine-tuned findings (cases) |
| --- | ---: | ---: |
| Drug/test/event/value linkage | 11 (9) | 20 (14) |
| Unsupported addition | 15 (12) | 8 (8) |
| Inappropriate clinical role | 9 (7) | 7 (7) |
| Chronology | 4 (4) | 7 (7) |
| Assertion/event status | 2 (2) | 6 (6) |
| Contradiction | 3 (3) | 1 (1) |
| Negation | 2 (2) | 0 (0) |
| Entity assignment | 2 (2) | 0 (0) |
| Repetition | 1 (1) | 3 (3) |
| Unsupported truncated-source completion | 1 (1) | 1 (1) |
| Unclosed source-copy output | 1 (1) | 0 (0) |

Case counts overlap. Zero means no finding recorded in that category, not proof
that the failure never occurs.

## Concrete failure mechanisms

- **Drug–dose and response binding:** In 302, dosulepin produces recovery at
  “150 mg daily, but developed sweating as a side effect.” Fine-tuned output
  transfers the dose/benefit and sweating to methysergide. In 1722 the note says
  “Dasatinib 50 mg daily was started”; output assigns it imatinib's 800 mg dose.
- **Test–result binding:** In 412, “The CT scan demonstrated plate and cage
  dislodgement” becomes an MRI result. In 1630, wedge-resection melanoma/mutation
  results become PET/CT findings. In 128, a refused CT biopsy receives the
  performed VATS biopsy's tissue-staining results.
- **Event status and time:** In 1628, “he opted to undergo surgery at our
  institution” becomes surgery already performed at an 11-year interval. In 337,
  the old reduction's twenty-year interval moves to the current mastectomy. In
  1241, “Forty-eight hours after the initiation of target therapy, the patient
  was afebrile” becomes five weeks.
- **Repetition and incomplete coverage:** Fine-tuned 1953, 1133 and 435 loop
  symptoms/tests until malformed truncation. Readable prefixes retain facts,
  but later fields disappear. On these 20 cases fine-tuned raw-valid JSON is
  17/20 and schema validity after established processing is 15/20; baseline is
  zero for both. The formatting gain is real, but insufficient.

The [case ledger](CASE_LEDGER.md) covers every case with exact source quotes and
baseline/fine-tuned evidence IDs. `audit.json` resolves IDs into paths and values
and includes saved judge reasons. Unsupported-addition findings cite relevant
context; their absence determination comes from the whole supplied note, not
from any single quote proving a universal negative.

## Reference and judge effects

There are **23 reference concerns across 18 cases**: three clear discrepancies,
six omissions, one entity-ownership annotation-policy issue, and thirteen
temporal/causal ambiguities (the last group affects twelve cases). They are not
23 established gold-label errors. Clear discrepancies concern transferred
dyspnea wording in 1351, surgical recovery assigned to later medication in 113,
and upgrading “most likely from imatinib” to a certain drug cause in 1722.

Policy questions include maternal caesarean delivery under infant surgeries
(1812), proposed lipofilling under treatment/reaction (337), and a discharge
field when the visible source truncates before disposition (1241). References
omit real transfusion counts (1133), unnamed clinic medication (128), and
documented histories. These require annotation decisions rather than automatic
clinical penalties against models that retain supported information.

There are **29 judge concerns across 18 cases**, including supported details
criticized as additions, output misreadings, role-policy sensitivity and
overbroad reasoning. These are concern records, not 29 wrong scores or an
estimate of judge error rate. The frozen contract asks for reference agreement;
many source-supported additions can therefore receive a contract-consistent
penalty. That penalty must not be called clinical hallucination. Other concerns
are actual reading errors: the 113 fine-tuned tumor-marker result says “Not
elevated,” and 2890 baseline surgery timing survives inside an array.

Supported details criticized by the judge include welding occupation (1351),
the parking-lot second seizure (1388), neglect and family psychiatric history
(725), four transfusions (1133), operative details (2654), uneventful postoperative
course (412), and height/weight/BMI values (337). Some outputs still misassign
these details; source presence and clinical role need separate assessment.

Original mean reference fidelity (0.335 to 0.375) and coverage (0.410 to 0.455)
remain reference-agreement measurements. This audit explains their limits; it
does not recalibrate or replace them with a new score.

## Actionable priorities and controlled next experiments

1. **Fix annotation policy and supervision first.** Specify patient versus
   relative/birth context, planned/refused/performed events, repeated drug
   courses, inferred versus explicit responses, and truncated notes. Preserve
   uncertainty and unknown doses. Keep the ten parents and 30-path schema;
   retain audit evidence in sidecars. Inspect separate training examples for
   these mechanisms before expanding the dataset.
2. **Prepare reviewed training examples and separate evaluation cases.** Target
   drug–dose–response pairs, test–result pairs, timeline anchors and negative or
   proposed events. Review full-case labels so fixing one relationship does not
   silently create other omissions. New training examples must come from the
   training split; never train on these audited 20 development cases. Measure
   field coverage and incorrect relations separately.
3. **Isolate label quality before capacity.** Compare original versus reviewed
   labels on the same training IDs/count, holding base model, rank, prompt and
   decoding fixed. Record revised annotation rules as a new protocol. A separately
   versioned source-grounded evaluation can accompany frozen reference metrics;
   do not silently repair their references or present development tuning as
   held-out validation.
4. **Then isolate data size, model size and rank.** A 1,325 versus ~5,000 accepted
   examples comparison should hold annotation policy, model and decoding fixed.
   The discussed ~0.5B candidate is a separate experiment with ordinary LoRA
   r=16 and its own base baseline. Test r=32 separately with alpha/r scaling
   held constant, and recheck sequence lengths and GPU memory. These are
   proposed experiments; none was launched or shown superior by this audit.
5. **Measure looping separately.** Inspect duplicate targets, target lengths and
   termination examples in training data before changing decoding. If decoding
   is tested, change one setting on the same held-out cases. Do not trim repeated
   predictions and count the repaired result as valid model output.

This audit establishes failure patterns but cannot uniquely attribute their
cause to synthetic labels, training coverage, capacity, rank or decoding.

## Artifacts and verification

`audit.json`, `reviewed_annotations.json`, `probes.csv`, `findings.csv`,
`reference_and_judge_concerns.csv`, `field_outcomes.csv`, `summary.json` and
`CASE_LEDGER.md` contain the completed review. Original `annotations.json` and
`indexed_inputs.json` are preserved. `reconciliation_log.json` records corrections
and withdrawn draft criticisms.

```powershell
.venv/Scripts/python.exe results_v3/source_audit_20/complete_annotations.py
.venv/Scripts/python.exe results_v3/source_audit_20/build_report.py
```

The builder checks all 20 IDs, eight probes per case, every exact source quote,
every model/reference evidence ID and raw excerpt, indexed-note identities,
the paired-data hash, ten frozen upstream source-file hashes and 80 unique saved
judgment keys. `validation_checks.json` records provenance. Passing mechanical
checks does not independently establish semantic or clinical correctness.
