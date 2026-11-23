# Continuation audit protocol v2

This run-specific appendix calibrates review of the remaining frozen training sample. Annotation policy v1, source data, labels, sample manifest, and pilot records remain unchanged. Reviews assess consistency with the supplied note and do not establish clinical truth. Candidate Luna findings and second-pass Luna review are model reviews, not clinician adjudication or independent parent adjudication.

## Decision rules

- Audit every label leaf and the whole note. A quote proves that words occur, not that the interpretation is correct. Findings must identify a material discrepancy, expressible omission, or genuine policy ambiguity. Do not duplicate one omission across overlapping paths.
- `patient medical history.physiological context` is a broad canonical history string. Explicit patient history belongs there even when it is not a physiological measurement (train:1052, “no previous facial trauma”); reject the pilot flag. Check the complete label before reporting omission: train:24 retains “prothrombin G20210A mutation.”
- Assign a shared response to a multi-drug regimen when the note describes combination chemotherapy and shared remission. Repetition under component drugs is attribution ambiguity, not clear unsupported causality (train:1453). Preserve per-drug attributes only when linked by the note.
- Emergency department presentation alone does not establish inpatient admission. If the label asserts admission while the note only says “presented to the emergency department,” flag unsupported event status (train:24). Do not infer that no admission occurred. In train:1239, admission to the general ward is explicit; attributing its reason to the preceding culture is ambiguous, not an established error.
- Material omissions are explicit, salient facts expressible in an existing path that change the extracted account: quantified symptom magnitude/modifiers; medication schedule, route or duration; qualified working diagnosis; pathology conclusion/margins; or explicit test confirmation. Do not count low-value incidental detail or bundled attributes as independent errors. Never complete text beyond a source cutoff (train:177).
- Broad normal-examination wording alongside a separately documented abnormal measurement is a scope ambiguity unless the note clearly includes that measurement in the purported normal finding (train:1108). Preserve qualifiers and uncertainty.

## Existing-path mapping

Use only the frozen 30 paths. Keep relationships together in concise strings: treatment `dosage` may carry dose, route, and frequency (“400 mg IV every 12 hours”); treatment `time` may carry sequence and course duration (“postoperatively for 7 days”); diagnosis-test `result` may carry result, condition, and qualification (“imaging features supportive of a working diagnosis”); symptom `details` may carry location, quality, triggers, relief, and material shared onset. Verify every proposed attribute against the note and preserve negation, uncertainty, actor, status, chronology, and drug/test linkage. Do not force every phrase into a label, blindly concatenate v2 values, or count projection loss alone as a defect.

## Calibration fixtures

| Case | Source and label evidence | Disposition |
|---|---|---|
| train:983 | “weight loss by 4 kg”; `/symptoms/3/time` says “Last three months” | Confirm missing magnitude; timeframe does not preserve it. |
| train:119 | “tablet methotrexate 20g weekly”; treatment dosage contains “20g” | Reject dose flag; source consistency does not medically correct source text. |
| train:1239 | “admitted to the general ward for further workup”; admission reason names culture and workup | Admission is supported; causal reason is ambiguous. Ciprofloxacin frequency is a separate omission. |
| train:1052 | “no previous facial trauma”; history field includes that phrase | Reject history flag. “for 7 days” and “working diagnosis” are supported omissions. |
| train:1453 | “six cycles of chemotherapy and showed a partial clinical remission”; response repeated under both drugs | Regimen attribution ambiguity, not two causal errors. S-1 schedule is an omission. |
| train:24 | “presented to the emergency department”; admission asserted; chest pain modifiers absent from `/symptoms/0/details` | Unsupported admission assertion and material symptom-detail omission. Reject retained-mutation and represented-onset flags. |
| train:1108 | Normal examination language while elevated BP is separately recorded | Scope ambiguity; no contradiction without explicit overlap. |
| train:177 | “Histopathological analysis confirmed an ectopic pancreas”; note ends “15 mm in” | Confirm pathology omission; do not complete cutoff. |
| train:676 | “This finding confirmed the diagnosis of AEF”; angiography result lists measurements | Confirm omitted diagnostic confirmation. |

These fixtures preserve pilot dispositions as calibration examples, not ground truth. Any disagreement in later work belongs in a separately versioned review with evidence and rationale.
