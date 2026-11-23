# Calibration examination

The parent reviewed the four calibration cases before bulk execution. These are
model-review calibration examples, not new cases among the remaining 90.

- `train:119`: preserve the unusual source-stated dose; reject the unsupported
  admission finding. Candidate omission attribution remains a model claim.
- `train:1052`: reject the ordinary-history role flag. Extra incidental normal
  detail alone is not material.
- `train:24`: the emergency-department presentation does not establish
  inpatient admission; retain the material symptom-modifier omission.
- `train:1453`: combination response is not evidence of independent causation
  by each drug; the corrected candidate review passes this calibration gate.

The independent second-pass model also proposed additional omissions and
projection-loss attributions. Those are model claims requiring source review;
projection-drop presence does not establish that a value is missing or that the
loss was caused by projection. The source reviewer must read the full label and
note and use only existing schema paths. This is not clinician adjudication.

One `train:119` source response required a supplemental correction because two
bounded responses invented schema paths for omissions. Both original responses,
the corrective instruction/hash sidecar, and the accepted raw response are
preserved in the run directory.
