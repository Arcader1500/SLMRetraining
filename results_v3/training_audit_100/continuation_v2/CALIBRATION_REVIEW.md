# Pilot calibration review

This note records calibration against the ten saved pilot cases and adjudications. It is run-specific guidance for continuation v2. It does not alter policy v1, pilot judgments, or labels. The source note is the authority only for source consistency; neither the note nor this review is clinical validation.

## Independent checkpoints against saved dispositions

| Case | Check against source and whole label | Alignment |
|---|---|---|
| train:983 | The note states “weight loss by 4 kg”; symptom time preserves “Last three months,” but not magnitude. Pleural “Exudative effusion” is already present. | Agree: magnitude omission confirmed; further differentiation is policy ambiguity. |
| train:119 | The note explicitly says “tablet methotrexate 20g weekly”; label dosage includes “20g.” | Agree: reject source-error claim; schedule loss is a separate mapping issue. |
| train:1239 | The note explicitly says “admitted to the general ward for further workup.” Ciprofloxacin is “400 mg every 12 hours.” | Agree: admission exists, reason linkage is ambiguous; frequency omission confirmed. Fever during the postoperative course does not prove ciprofloxacin alone caused it. |
| train:1045 | Pilot adjudication found no material discrepancy among its candidate flags. | Retain “no material issue established”; not exhaustive certification. |
| train:1052 | “No previous facial trauma” is present in the broad history value; “nonpalpable regional lymph nodes” appears in both note and label. The note also says antibiotics etc. “for 7 days” and imaging “supportive of the working diagnosis.” | Agree: reject history and lymph-node flags; confirm duration and qualified working-diagnosis omissions. |
| train:1453 | “Partial clinical remission” follows six cycles of chemotherapy involving both drugs. The note states S-1 frequency/cycle and continued use after renal insufficiency. | Agree: shared regimen response is ambiguous, not separate single-drug causality; schedule and continuation timeline are omissions. |
| train:24 | Note says “presented to the emergency department”; it does not establish admission. It states substernal, radiating, pleuritic/positional pain and relief; the label retains the prothrombin mutation. | Agree: unsupported admission assertion and symptom detail omission; reject mutation and duplicate onset flags. |
| train:1108 | Normal exam wording coexists with separately recorded elevated blood pressure; scope is unclear. | Agree: ambiguity, not definite contradiction. |
| train:177 | Before the cutoff, pathology says “confirmed an ectopic pancreas” and “The tumour did not involve the resection margins”; note then ends mid-sentence. | Agree: confirm diagnosis/margin omission; infer nothing after cutoff. |
| train:676 | Source says “This finding confirmed the diagnosis of AEF”; retained angiography result gives measurements only. | Agree: material test-result omission. |

The saved pilot ledger remains authoritative for its 17 candidate dispositions and assistant-added findings. This calibration check finds no reason to revise those records. Agreement is a source-evidence cross-check, not a second adjudication authority.

## Calibration emphasis

The main candidate-review failure was semantic inconsistency: a quoted fact could be supported while its category called it erroneous. Review the entire label, then test linkage and role. Quotes are necessary evidence, not sufficient proof. Keep source-supported but debatable interpretation as ambiguity; distinguish unsupported label assertions from facts the note affirmatively disproves. Count bundled omissions once at the appropriate section when several associated attributes form one regimen or finding.

Broad history is intentionally represented by the existing physiological-context string. Admission requires explicit admission evidence. A shared regimen outcome stays attached to the regimen unless the note attributes it to a component. Materiality depends on information value and existing-schema expressibility, not merely whether the phrase is absent. Preserve truncation boundaries and do not fill in missing text.

Candidate Luna output and any second Luna pass remain model-generated evidence. Human/parent review should resolve flags against note and whole label and record separate versioned dispositions; clinician review would be required for clinical validity claims.
