# Clinical extraction annotation policy, audit version 1

The supplied note is the sole authority for source consistency. This policy
clarifies review of the existing ten-section, 30-path extraction schema; it does
not change frozen training labels, development references or model outputs.

| Topic | Rule |
| --- | --- |
| Missing information | Leave missing names, doses, dates and outcomes unspecified. Do not supply standard care or outside medical knowledge. |
| Cut-off notes | Retain only facts established before the cutoff. Do not finish a unit, procedure, response or disposition because it appears likely. A punctuation heuristic is only a screening signal. |
| Patient and relatives | Distinguish the patient's facts from maternal, family and other-person facts. Delivery may appear as birth history; do not assert the infant underwent the mother's operation. |
| Clinical roles | Admission requires evidence of admission, not merely an outpatient visit or diagnosis. Distinguish symptoms, investigation findings, procedures and therapies. Synonymous headings or explicit historical procedures in history are not automatically semantic errors. |
| Procedure status | Preserve discussed/planned, refused, attempted, performed and completed status. If the schema lacks a status key, put the qualification in existing Type/details fields. Never add a schema key. |
| Treatment courses | Preserve drug-dose-frequency-time-response associations for each course. Do not transfer a dose or reaction to the next drug in the note. Repeated courses are separate events when their attributes differ. |
| Investigations | Preserve which test produced each result, including pathology versus imaging. A refused biopsy cannot have a tissue result from another procedure. Surgery/test dual use can be legitimate. |
| Negation and uncertainty | Preserve absent findings and possible/probable attribution. Do not upgrade temporal sequence into a certain causal treatment response. |
| Timing | Distinguish symptom onset, presentation, investigation, treatment, follow-up and discharge. Retain anchors rather than moving an interval between events. |
| Coverage | Retain material facts expressible in the schema, including important negatives, relevant history, treatment dose/response and disposition. Missing low-value incidental detail alone is not a material defect. Explicit facts elsewhere in an appropriate narrative role retain semantic credit. |
| Redundancy | Exact duplicate projected entries are structural redundancy, not independent clinical events or independent factual errors. Preserve genuinely different events. |
| Disposition | A course summary is not proof of discharge. Require explicit disposition evidence before asserting a discharge event or destination. |

Review records separate **clear source/label discrepancies**, **material
omissions**, and **annotation-policy/temporal/causal ambiguities**. Automated judge
findings remain candidates until checked; an exact quote confirms its existence,
not its interpretation. A judge's no-issue decision is not certification.

New reviews and evidence live in sidecars. Any later replacement labels must be
separately versioned and evaluated on separate cases. The audited development
cases must never be added to training. Clinician adjudication remains distinct
from assistant/model source-consistency review.
