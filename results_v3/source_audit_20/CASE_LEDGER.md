# Evidence ledger: all 20 cases

Assistant source-consistency audit, not clinician adjudication. Eight selected diagnostic probes per case; not exhaustive source or output claim inventories and not precision/recall. Demographics separated from clinical content. S=unambiguous supported fact, including explicitly identified events in history/discharge or neutral prose; P=readable fact with inappropriate clinical role (e.g. finding as surgery, outcome as treatment reaction); C=wrong value/entity/event/time/negation relation without a correct version of that same probed relation; X=correct and incompatible versions of the probed fact coexist; O=probed fact absent from all readable raw text; A=partial or ambiguous evidence. Synonymous headings, nested history and surgery/test dual use alone are not semantic errors. Probe labels concern the named subclaim, not all adjacent details; findings capture independent errors. Read malformed prefixes and arrays without repairing predictions or changing existing format scores. Absence of a reference/judge concern is not certification. Categories are diagnostic primary labels, not severity scores. Reference timing/causal/policy concerns and judge policy sensitivity are not all confirmed errors.

Evidence IDs resolve to `indexed_inputs.json`; complete resolved evidence and exact quote offsets are in `audit.json`. Original raw outputs are in `../deepeval_20/paired_cases.json`. See `REPORT.md` for interpretation.

## validation:593

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age nine | A 9-year-old girl | X:B03 B07 B10 B14 | S:F03 |
| sex: Female patient | A 9-year-old girl | X:B04 B08 B15 | S:F04 |
| procedure: Closed reduction and percutaneous pin fixation | closed reduction of the fracture and percutaneous pin fixation | S:B13 | A:F05 F27 |
| investigation: Gartland IIIB fracture on X-ray | An X-ray documented a Gartland IIIB fracture | P:B12 | S:F22 |
| investigation: Distal brachial occlusion on DSA | showing occlusion of the distal brachial artery | S:B20 B24 | C:F10 |
| treatment: 3 x 28 mm BVS released | A 3 × 28 mm BVS | O | O |
| outcome: Regular radial/ulnar pulse after intervention | A regular sphygmic pulse appeared on radial and ulnar arteries. | O | P:F34 F36 |
| treatment: Posterior splint after surgery | The arm was maintained with a 130° posterior splint for 40 days after surgery | O | O |

### Findings

- **baseline / unsupported / B06 B07 B08**: Adds vasculitis and a one-year-old male admission unrelated to the supplied case. Source: “A 9-year-old girl”
- **baseline / linkage / B18 B22 B26**: Turns order/numerical information into operation times, including wire size 0.014 as a time. Source: “two 0.014ʺ guide wires”
- **finetuned / assertion_status / F09 F10**: Lists the absent hypothetical drainable hematoma as an operation and invents a cause for non-identification. The wording retains not identified, so this is an event-status/role error rather than a simple positive assertion. Source: “an external hematoma compressing the artery, that could have been drained cutting lacertus fibrosus, was not identified”
- **finetuned / chronology / F28**: Adds one hour post-surgery to the absence of pulses; one hour in the source is admission delay. Source: “At the end of the procedure, the arterial pulses did not reappear.”
- **finetuned / placement / F11 F12 F30**: Ultrasound is listed as surgery and DSA as a dosage. Source: “digital subtraction angiography (DSA) was performed”

### Reference Review

- **temporal_ambiguity / R11**: Reference stores admission delay as symptom time; this does not establish exact symptom-onset time. Source: “She was admitted 1 h after the event complaining of severe pain”

### Judge Review

- **overstated_contradiction**: The judge treats absent pulses after fracture fixation and later regular pulses as a contradiction. They are sequential outcomes around different interventions; the real output defect is missing the stent and adding unsupported timing. Source: “The final angiography confirmed correct positioning and patency of the stent with restoration of distal flow”

## validation:1351

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age forty | A 40-year-old Caucasian woman | S:B03 | S:F03 |
| sex: Female patient | A 40-year-old Caucasian woman | X:B01 B04 | S:F04 |
| history: Long respiratory/allergy history | a long history of respiratory symptoms and allergies | P:B06 | O |
| treatment: Symptoms persisted after antibiotics | When her cough and other symptoms persisted | O | O |
| symptom: Exertional palpitations | occasional palpitations with exertion | S:B07 B17 | S:F09 |
| investigation: PFO on echocardiography | interatrial shunt consistent with a patent foramen ovale (PFO) | O | S:F22 |
| investigation: Most right pulmonary venous return drains to IVC | The majority of the right lung pulmonary venous return was to the inferior vena cava via the scimitar vein. | O | O |
| investigation: No murmurs | she did not have any murmurs | O | S:F20 |

### Findings

- **baseline / placement / B04**: Stores ethnicity as sex; age/sex/history are scattered through repeated admissions. Source: “A 40-year-old Caucasian woman”
- **baseline / placement / B13 B20**: Medication and chamber dilation are assigned to surgery fields. Source: “She was treated with a course of antibiotics for a presumed pneumonia.”
- **finetuned / placement / F10 F13**: Names an examination and an anatomic border as symptoms. Source: “a chest X-ray was performed”
- **finetuned / unsupported / F16**: Assigns dyspnea to left chest without source localization. Source: “worsening shortness of breath over the past year”
- **finetuned / linkage / F08**: Attaches the one-year dyspnea history to the combined fever/chills/wheeze/cough entry. Source: “worsening shortness of breath over the past year”

### Reference Review

- **timing_loss / R09**: Reference calls dyspnea occasional, transferring the qualifier from palpitations and losing the stated one-year worsening history. Source: “worsening shortness of breath over the past year and occasional palpitations with exertion”

### Judge Review

- **false_unsupported**: The baseline judge calls welding exposure unsupported. Occupation is explicit; a causal exposure claim would require more, but the generated leaf says welding by profession. Source: “She was a welder by profession”
- **false_unsupported**: The fine-tuned judge calls presumed-pneumonia context unsupported. It is explicit in the note, although it is a poor replacement for the full respiratory/allergy history. Source: “She was treated with a course of antibiotics for a presumed pneumonia.”

## validation:113

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age forty-four | A 44-year-old female | S:B06 | S:F03 |
| sex: Female patient | A 44-year-old female | S:B07 | S:F04 |
| history: DM is part of the clinical context | since 2013 and was diagnosed as DM | O | S:F02 |
| investigation: Tumor markers not elevated | Her serum carcinoembryonic antigen and carbohydrate antigen 19-9 were not elevated | S:B30 | S:F17 |
| procedure: Hepatic medial segmentectomy and cholecystectomy | hepatic medial segmentectomy and cholecystectomy were performed | O | S:F05 |
| treatment: Postoperative tacrolimus 5 mg/day | tacrolimus 5 mg/day and prednisone 20 mg/day | O | O |
| treatment: Postoperative prednisone 20 mg/day | tacrolimus 5 mg/day and prednisone 20 mg/day | O | C:F28 F29 |
| discharge: Discharge on postoperative day 23 | The patient was discharged on postoperative day 23. | O | S:F31 |

### Findings

- **baseline / unsupported / B15**: Invents a 2020 surgery date. Source: “since 2013 and was diagnosed as DM”
- **baseline / linkage / B37 B39**: Converts immunostain labels and polarities to grades 19 and 20. Source: “CK7 (+), CK 19 (+), and CK 20 (–)”
- **baseline / linkage / B27**: Lists enhanced CT and ultrasound results as Elevated, losing the lesion findings; the separately recorded negative tumor markers are correct. Source: “Her serum carcinoembryonic antigen and carbohydrate antigen 19-9 were not elevated”
- **finetuned / linkage / F28 F29**: Assigns tacrolimus dose to prednisone. Source: “tacrolimus 5 mg/day and prednisone 20 mg/day”
- **finetuned / unsupported / F12 F13**: Adds neurological/CNS symptoms not stated. Source: “dry cough, myalgia, and arthralgia”

### Reference Review

- **temporal_ambiguity / R09**: Reference attaches since 2013 to the later cough/pyrexia/arthralgia group; pyrexia is described at recurrence, not explicitly in the initial 2013 group. Source: “dry cough, myalgia, and arthralgia since 2013”
- **linkage / R27**: Reference associates uncomplicated surgical recovery with postoperative medication response, although recovery is stated before transfer for that medication. Source: “made a satisfactory recovery with no postoperative complications and was transferred”

### Judge Review

- **misread_output**: The fine-tuned fidelity reason claims elevated tumor markers, but F17 correctly says Not elevated. The dose and unsupported neurological symptoms remain genuine errors. Source: “Her serum carcinoembryonic antigen and carbohydrate antigen 19-9 were not elevated”

## validation:937

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age sixty-six | A 66-year-old male | S:B06 | S:F03 |
| sex: Male patient | A 66-year-old male | S:B07 | S:F04 |
| history: Diabetes, hypercholesterolemia and hypertension | history of diabetes, hypercholesterolemia and hypertension | S:B08 | S:F05 |
| investigation: Normal baseline ECG | The baseline electrocardiography [] and cardiac examination were normal. | O | S:F10 |
| investigation: No hypokinesis on echocardiography | Echocardiography revealed no hypo kinesis of all ventricular walls | O | X:F09 F14 |
| investigation: EF 70 percent | ejection fraction of 70% | O | S:F14 |
| investigation: No significant cardiac biomarker alterations | did not show any significant alterations of cardiac biomarkers | S:B04 | S:F16 |
| procedure: Percutaneous LAD revascularization | the patient was subjected to percutaneous revascularization of the LAD | O | S:F19 |

### Findings

- **baseline / unsupported / B10**: Replaces the actual intervention with Craniovascularization. Source: “percutaneous revascularization of the LAD”
- **baseline / placement / B13 B17 B21**: Represents coronary anatomy/imaging as symptom entries and MSCT as a dose. Source: “coronary computed tomography”
- **finetuned / assertion_status / F09 F14**: Creates a positive hypokinesis symptom despite a negative echo finding elsewhere in the same output. Source: “no hypo kinesis of all ventricular walls”
- **finetuned / chronology / F08**: Moves the CT timing onto the presenting chest pain. Source: “A 64-slice coronary computed tomography (MSCT, GE, USA) was performed two days after admission”
- **finetuned / linkage / F20**: Uses the pre-procedure coronary lesion as the reaction to revascularization. Source: “There was a severe calcified, diffuse lesion in the proximal and middle LAD”

### Reference Review

No additional concern recorded; this is not an exhaustive certification.

### Judge Review

- **false_unsupported**: The baseline judge calls stable-angina context unsupported; the note explicitly considers probable stable angina, although the output drops the uncertainty. Source: “He was considered with probably stable angina.”
- **false_unsupported**: The fine-tuned judge calls extra coronary anatomy unsupported because it is absent from the reference. Much of that anatomy is in the source; misclassification and any altered anatomy should be assessed separately. Source: “The distal LCX proceeded into the left posterior atrioventricular groove”
- **misread_output**: Fine-tuned fidelity says revascularization is under treatment reaction, but it is the treatment name; the preprocedure lesion used as reaction remains wrong. Source: “the patient was subjected to percutaneous revascularization of the LAD”

## validation:1953

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age seventy-six | A 76-year-old woman | S:B07 | S:F03 |
| sex: Female patient | A 76-year-old woman | S:B08 | S:F04 |
| history: No prior ischemic heart disease or heart failure | without histories of cardiovascular risks such as ischemic heart disease and heart failure | S:B09 | S:F05 |
| symptom: Squeezing character of chest pain | Her chest pain was characterized by a squeezing sensation | S:B17 | O |
| symptom: Chest pain lasts less than half an hour | lasted for less than half an hour | S:B16 B17 | S:F08 |
| investigation: Blood pressure 110/60 | initial blood pressure was 110/60 mm Hg | P:B21 B24 | O |
| investigation: ST depression V5/V6 and LVH | ST depression in leads V5 and V6 and left ventricular hypertrophy | P:B32 B35 | O |
| investigation: No significant coronary luminal stenosis | No significant luminal stenosis was observed in both the left and right coronary arteries. | O | O |

### Findings

- **baseline / unsupported / B06 B11**: Adds prescribed medication without a documented treatment and assigns it to surgery. Source: “without histories of cardiovascular risks such as ischemic heart disease and heart failure and use of medications”
- **baseline / unsupported / B17**: Adds Seated to the symptom context. Duration and non-exertional character themselves are supported. Source: “unrelated to exercise”
- **baseline / placement / B21 B25 B29 B32**: Vital signs, examination findings and ECG are presented as symptoms. Source: “Electrocardiography revealed”
- **finetuned / unsupported / F09**: Invents seizures as the details of chest pain. Source: “Her chest pain was characterized by a squeezing sensation”
- **finetuned / repetition / F06 F07 F09**: Unparsed output repeats chest-pain entries 79 times and the seizure detail 78 times, losing the examination/test sections. Source: “was referred to our hospital because of chest pain”

### Reference Review

- **reference_omission / R08**: Reference retains squeezing character but omits explicit non-exertional character and duration despite retained symptom fields being able to express them. Source: “unrelated to exercise and lasted for less than half an hour”

### Judge Review

No additional concern recorded; this is not an exhaustive certification.

## validation:1812

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Infant patient, not mother age | A male infant | X:B01 B03 B07 | S:F03 |
| sex: Male infant | A male infant | S:B04 | S:F04 |
| investigation: FVIII less than 0.01 U/mL | a FVIII level was ordered, which was very low at <0.01 U/mL | A:B20 B21 B22 | S:F11 F12 |
| treatment: Packed red cells 20 cc/kg | a transfusion of 20 cc/kg of O Rh-negative packed red cells | O | O |
| treatment: Initial recombinant FVIII 50 U/kg | initially treated with 50 U/kg of recombinant FVIII | S:B24 | S:F21 |
| treatment: Repeat FVIII adjusted to 100 percent | His repeat doses were adjusted to bring his FVIII level to 100%. | O | O |
| investigation: CT shows extensive subgaleal hematoma | CT) scan of the head revealed a large subgaleal hematoma | O | S:F14 |
| discharge: Discharged at one week after resolution on imaging | The infant was discharged at 1 week of age following a repeat head imaging confirming complete resolution | O | S:F22 |

### Findings

- **baseline / entity_assignment / B03 B07**: Uses maternal age 26 and repeat-CBC delay 12 as patient ages. Source: “born via repeat caesarean section to a healthy 26-year-old woman”
- **baseline / chronology / @"time": 1 week**: Places pallor/tachycardia and fluid-wave findings at one week rather than before the scheduled repeat CBC. Source: “Prior to the next blood test”
- **baseline / linkage / B18 B19 B20 B21 B22**: Calls the abnormal repeat CBC normal and combines FVIII and CT labels/results. Source: “a hemoglobin level of 7.6 g/dL”
- **finetuned / linkage / F19 F21**: Places FVIII therapy under packed-cell transfusion reaction, losing a separate drug-dose event. Source: “initially treated with 50 U/kg of recombinant FVIII”
- **finetuned / chronology / F05 F06**: The pallor/tachycardia symptom is paired with an initial-examination localized-hematoma detail; the later deterioration is not clearly distinguished. Source: “Prior to the next blood test”

### Reference Review

- **entity_assignment / R06 R07**: Lists maternal caesarean delivery under infant surgeries; birth context and maternal surgery should be distinguished in annotation rules. Source: “was born via repeat caesarean section to a healthy 26-year-old woman”
- **temporal_ambiguity / R11**: Attaches later fluid-wave progression to the initial localized-hematoma symptom without explicit timing separation. Source: “His examination now revealed a large palpable fluid wave”

### Judge Review

- **questionable_omission**: Judge counts lack of a caesarean surgery entry as an infant-model omission. The reference itself conflates maternal surgery with infant history; treat as annotation-policy issue. Source: “was born via repeat caesarean section to a healthy 26-year-old woman”

## validation:1630

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age seventy | A 70-year-old white man | S:B15 | S:F03 |
| sex: Male patient | A 70-year-old white man | S:B16 | S:F04 |
| history: Metastatic melanoma two years ago | metastatic melanoma initially diagnosed 2 years ago | S:B48 | S:F05 |
| symptom: Joint symptoms progressed over four months | Over the next 4 months, his symptoms progressed | P:B08 B20 | O |
| treatment: Ibuprofen initially gave mild improvement | He initially took ibuprofen 800 mg three times daily with some mild improvement | S:B29 B32 | C:F09 F27 |
| procedure: Prior Mohs procedure | he had a Mohs procedure with negative margins | S:B12 B49 | S:F05 |
| treatment: Nivolumab plus ipilimumab followed by colitis hospitalization | After the second cycle of his immunotherapy he developed severe non-infectious colitis requiring hospitalization. | O | O |
| treatment: Later single-agent nivolumab 240 mg | Single agent immunotherapy with nivolumab (240 mg every 2 weeks) | O | P:F22 F24 |

### Findings

- **baseline / unsupported / B37**: Replaces nivolumab with Levodopa while retaining immunotherapy dose/schedule. Source: “Dual therapy nivolumab”
- **baseline / placement / B08 B20 B33**: Symptom progression is called surgery and morning stiffness is medication. Source: “his symptoms progressed to include both knees, both feet, and both hands”
- **finetuned / linkage / F16 F20**: Assigns tissue/mutation findings to PET/CT; the source PET/CT finding is nodules with FDG uptake. Source: “Wedge resection of the right lower lobe revealed metastatic melanoma with wild type BRAF and no C-KIT mutations.”
- **finetuned / unsupported / F17 F18 F30**: Adds Echolithogram and epidural steroid, neither stated in this note. Source: “Wedge resection of the right lower lobe”
- **finetuned / contradiction / F09 F27**: Reverses initial ibuprofen benefit to no relief and adds a 1.5-year response interval. Source: “with some mild improvement, but at the time of presentation, it offered no relief”
- **finetuned / placement / F21 F23 F28**: Immunotherapy appears as a diagnostic test, while stiffness appears as a treatment. Source: “Single agent immunotherapy with nivolumab”

### Reference Review

- **truncated_source_inference / R25**: Reference completes the truncated relative time as before current presentation. Plausible, but the supplied text does not contain the endpoint. Source: “was started 4 months before”

### Judge Review

- **false_omission**: The fine-tuned reason says expected surgeries are omitted. F05 explicitly names Mohs and wedge resection in history; this is section placement, not absent procedure content. Source: “Wedge resection of the right lower lobe revealed metastatic melanoma”

## validation:1388

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age fifty-four | A 54-year-old Caucasian male | S:B03 | S:F03 |
| sex: Male patient | A 54-year-old Caucasian male | X:B04 B07 | S:F04 |
| history: Prior astrocytoma treated with chemoradiation | anaplastic astrocytoma previously treated with chemoradiation | S:B05 | S:F05 |
| admission: Hemorrhage prompted admission | intraparenchymal hemorrhage for which the patient was admitted | O | X:F02 F17 |
| symptom: Two seizure-like episodes that morning | two seizure-like episodes earlier that morning | S:@two seizure-like episodes earlier that morning | S:F01 F06 |
| investigation: Doppler pseudoaneurysm with bidirectional flow | left anterior temporal scalp with bidirectional flow | O | S:F22 |
| treatment: Discharged on seizure prophylaxis | discharged on seizure prophylaxis | O | S:F25 |
| chronology: Increasing pain four days after discharge | Four days following discharge, the patient represented with complaints of increasing pain | O | O |

### Findings

- **baseline / placement / B04 B06**: Uses ethnicity as sex and chemoradiation as surgery. Male is present in contextual text. Source: “A 54-year-old Caucasian male”
- **baseline / repetition / @"surgeries": ["chemoradiation", "chemoradiation"**: Loops historical chemoradiation until the unparsed output is truncated. Source: “previously treated with chemoradiation”
- **finetuned / linkage / F02 F17**: Main admission reason becomes scalp bulge, while CT result elsewhere correctly links hemorrhage to admission. Source: “intraparenchymal hemorrhage for which the patient was admitted”
- **finetuned / linkage / F23 F24**: Historical cancer treatment becomes a current treatment with no focal deficits as its response. Source: “previously treated with chemoradiation”

### Reference Review

- **causal_overstatement / R32**: The reference treatment-response field associates stable discharge with prophylaxis but the note does not attribute absence of deficits/pain to its effect. Source: “The patient was subsequently discharged on seizure prophylaxis in stable condition”

### Judge Review

- **false_unsupported**: The fine-tuned judge calls parking-lot chronology unsupported; the parking-lot second episode is explicit. Source: “the second episode, which occurred in the parking lot of the emergency department”

## validation:128

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age forty-two | A 42 year-old woman | S:B03 | S:F03 |
| sex: Female patient | A 42 year-old woman | S:B04 | S:F04 |
| symptom: Dry cough for ten months | intermittent dry cough of ten months duration | O | S:F01 F07 |
| symptom: No fever or dyspnea on exertion | No fever, chest tightness, bone pain, anorexia, dyspnea on exertion or body weight loss | S:B02 B05 | S:F08 |
| procedure: CT-guided biopsy refused | A CT-guided biopsy was recommended but the patient refused to undergo this procedure. | X:B12 B26 B18 | C:F19 F20 |
| procedure: VATS biopsy performed | A biopsy through video-assisted thoracoscopic surgery (VATS) was then indicated | O | S:F28 F29 |
| investigation: Plasma-cell kappa-positive/lambda-negative pathology belongs to VATS tissue | These tumor cells stained positively for kappa light chains | C:B15 B18 B26 | C:F19 F20 |
| investigation: Bronchoscopy no endobronchial lesion | a bronchoscopic examination revealed no endobronchial lesion or abnormal secretions | S:B09 | S:F24 |

### Findings

- **baseline / assertion_status / B12 B26 B27**: Correct refusal appears in an admission fragment, but CT biopsy is also listed as performed treatment with VATS incision details. Source: “the patient refused to undergo this procedure”
- **baseline / linkage / B15 B18**: Attributes tissue staining/pathology to bronchoscopy as well as CT biopsy rather than the performed VATS wedge biopsy. Source: “microscopic examination showed a solid mass made up mostly of plasma cells”
- **baseline / unsupported / B17 B21**: Invents 15-minute and 10-minute procedure durations. Source: “A 3 cm working incision and a 1 cm scope port”
- **finetuned / assertion_status / F19 F20**: Attaches positive tumor stains to refused CT biopsy. Source: “the patient refused to undergo this procedure”
- **finetuned / unsupported / F32**: Invents a medicine name Mucine oil; only unnamed medicines are given in the source. Source: “She took some medicines at a local clinic to control her cough.”
- **finetuned / placement / F10 F12 F15 F17**: Uses admission timing as location and diagnostic procedures as symptoms. Source: “A pulmonary function test showed a mild restrictive ventilatory defect.”

### Reference Review

- **reference_omission / @"treatments":[]**: Empty treatments excludes a documented unnamed medicine course; lack of drug name should not imply no treatment. Source: “She took some medicines at a local clinic to control her cough.”
- **temporal_ambiguity / R02**: Reference promotes a temporal presentation detail to admission reason; plausible but no explicit causal admission statement is supplied. Source: “blood-tinged sputum appeared one month prior to hospital admission”

### Judge Review

- **reference_absence_not_falsehood**: Expected empty treatments should not make all local-clinic medication mentions false. The invented Mucine oil identity remains unsupported. Source: “She took some medicines at a local clinic to control her cough.”

## validation:725

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age nine | B is a 9-year-old African boy | S:B07 | S:F03 |
| sex: Male patient | B is a 9-year-old African boy | S:B08 | S:F04 |
| history: Born at term after normal pregnancy | born at term after a normal pregnancy | P:B09 B10 | S:F05 |
| investigation: ENT and audiometry no abnormality | ENT) exploration and audiometry were performed at the age of 4 years old without any abnormalities | P:B20 B21 | O |
| treatment: Risperidone 2 mg/day ineffective | Risperidone was initiated at 2 mg/day but without any efficacy. | O | O |
| investigation: Extensive screen found no organic cause | no organic cause was retrieved | O | S:F17 F18 |
| treatment: Aripiprazole 15 mg/day | Aripiprazole was introduced at 15 mg/day | S:B32 B33 | S:F19 F20 |
| treatment: Combination poorly tolerated with sedation and worse psychosis | severe sedation and a worsening of delusions and hallucinations | P:B24 | S:F23 |

### Findings

- **baseline / contradiction / B13 B15**: Rapid onset of skills reverses developmental delay, although another field retains delay. Source: “He quickly presented a delay in language and motor skills.”
- **baseline / unsupported / B04 B34**: Adds two-hour timing to medication/admission events. Source: “Aripiprazole was introduced at 15 mg/day”
- **baseline / truncated_completion / B25 B36**: Completes the truncated concentration unit as ng/day. Source: “overdose at 835 ng/”
- **finetuned / truncated_completion / F25**: Completes the truncated concentration unit as ng/mL; plausible medically but unsupported by the supplied text. Source: “overdose at 835 ng/”
- **finetuned / placement / F24 F25**: Creates the laboratory plasma level as a separate treatment item. Source: “The aripiprazole plasma level showed an overdose”

### Reference Review

- **causal_overstatement / R23**: Reference assigns sedation/worsening solely to levomepromazine although the source describes combination intolerance and an aripiprazole overdose. Source: “Aripiprazole was introduced at 15 mg/day and associated with levomepromazine”

### Judge Review

- **false_unsupported**: The fine-tuned judge calls neglect/violence and academic history unsupported; those facts are explicit in the note, though the current admission reason is still misassigned. Source: “due to severe physical and psychological violence within the family and severe neglected care”
- **false_unsupported**: The baseline judge calls foster-care/family-history details invented; B05/B12 have direct support. Some other history values remain wrong. Source: “His family background is marked with a psychotic disorder in one first-degree relative.”

## validation:302

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age fifty-two | A 52-year-old married woman | A:B09 | S:F03 |
| sex: Female patient | A 52-year-old married woman | X:B04 B07 | S:F04 |
| treatment: Dosulepin 150 mg | dosulepin (previously called dothiepin) and she recovered with a dose of 150 mg daily | S:B12 | S:F19 F20 |
| treatment: Sweating associated with dosulepin | she recovered with a dose of 150 mg daily, but developed sweating as a side effect | S:B12 | C:F06 F07 |
| treatment: Amitriptyline associated with racing heart | amitriptyline, but she complained of a racing heart while taking it | S:B15 | X:F09 F10 F25 |
| treatment: Mirtazapine titrated 15 to 45 mg | She was started on mirtazapine and the dose was increased from 15 to 45 mg nocte. | O | S:F18 |
| treatment: Venlafaxine XL 75 mg | venlafaxine XL 75 mg nocte | S:B16 | S:F26 F27 |
| treatment: Lofepramine 140 mg | lofepramine 140 mg nocte | O | S:F29 F30 |

### Findings

- **baseline / entity_assignment / B05 B06 B07 B08**: Turns mother/sister history into patient admissions and adds male sex and numeric ages unrelated to those relatives. Source: “the patient's mother had been hospitalized thrice”
- **baseline / placement / B12 B14 B15 B16**: Medication histories are entire admission reasons rather than treatment events. Source: “She was treated with dosulepin”
- **finetuned / linkage / F06 F07 F22 F20**: Transfers dosulepin sweating and dose/benefit to methysergide. Source: “she recovered with a dose of 150 mg daily, but developed sweating as a side effect”
- **finetuned / linkage / F09 F10 F25**: Gives racing heart to dosulepin in symptoms while also correctly associating it with amitriptyline in treatment. Source: “amitriptyline, but she complained of a racing heart while taking it”
- **finetuned / unsupported / F24 F12**: Dopamine is not an amitriptyline dose; mouth pain is not stated anywhere in the note. Source: “A neurologist thought her migraine might respond to amitriptyline”

### Reference Review

- **reference_omission / R04**: History retains only migraine and omits the main recurrent depressive disorder and extensive family history, though the retained physiological-context field could contain them. Source: “was suffering from recurrent depressive disorder”

### Judge Review

- **reference_absence_not_falsehood**: Judge labels depressive-disorder history wrong because the reference history only says migraine; it is source-supported, although the output also loses/misplaces other history. Source: “was suffering from recurrent depressive disorder”
- **placement_sensitivity**: Coverage judge recognizes mirtazapine in symptom details and penalizes placement. Under this audit policy the explicit drug/titration subclaim survives; this is policy sensitivity, not a false-omission judge error. Source: “She was started on mirtazapine and the dose was increased from 15 to 45 mg nocte.”

## validation:1241

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age seventy-two | A 72-year-old man | X:B03 B07 | S:F03 |
| sex: Male patient | A 72-year-old man | S:B04 | S:F04 |
| admission: Balance disorder prompted admission | was admitted to another hospital due to a balance disorder | S:B01 B02 | P:F01 F02 |
| history: Bullous pemphigoid and monoclonal antibody history | history of bullous pemphigoid treated with a monoclonal antibody | S:B05 | O |
| treatment: Ampicillin 3 g | ampicillin 3 g/6 h | O | S:F20 |
| treatment: TMP/SMX 160/800 mg | Trimethoprim/sulfamethoxazole 160/800 mg/8 h was added. | O | C:F22 F23 |
| chronology: Afebrile after 48 hours of target therapy | Forty-eight hours after the initiation of target therapy, the patient was afebrile. | O | C:F21 |
| investigation: Tissue PCR identifies Listeria DNA | using PCR identified Listeria monocytogenes DNA | O | S:F17 F18 |

### Findings

- **baseline / placement / B06 B08 B10 B12**: Examination, imaging and blood-culture facts are encoded as separate admission reasons. Source: “his blood cultures grew Listeria monocytogenes”
- **baseline / placement / B07**: Repeats a history sentence in age fields. Source: “history of bullous pemphigoid”
- **finetuned / linkage / F23**: TMP/SMX dosage is replaced with the names of three different antibiotics. Source: “Trimethoprim/sulfamethoxazole 160/800 mg/8 h was added.”
- **finetuned / chronology / F07 F21 F24**: Shifts the 20-day deterioration and TMP/SMX addition anchor from treatment to CT, and the afebrile response from 48 hours to five weeks. Source: “Twenty days later, he showed progressive clinical and neurologic deterioration”
- **finetuned / placement / F06**: Uses lesion hemisphere as the location of the combined hallucination/disinhibition/hemiplegia symptom group. Source: “left hemiplegia with no sensory deficits”

### Reference Review

- **discharge_scope / R38**: The supplied note ends before completing the patient disposition; the reference labels a treatment-course summary as discharge without documented discharge. The improvement itself is stated earlier. Source: “Trimethoprim/sulfamethoxazole therapy was discontinued, and the patient was”
- **causal_overstatement / R37**: Lesion reduction occurred during combined therapy; reference places it under TMP/SMX response. This is causal attribution ambiguity, not proof of a false outcome or claim of sole causation. Source: “Ampicillin, gentamicin, and vancomycin therapy was stopped while trimethoprim/sulfamethoxazole therapy was continued.”

### Judge Review

No additional concern recorded; this is not an exhaustive certification.

## validation:412

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 63 | A 63-year-old man | S:B08 | S:F03 |
| sex: Male | A 63-year-old man | S:B09 | S:F04 |
| investigation: MRI increased intramedullary signal | increased intramedullary signal intensity on T2 weighted magnetic resonance imaging | O | C:F16 F17 |
| investigation: CT plate and cage dislodgement | The CT scan demonstrated plate and cage dislodgement | P:B26 B27 | C:F16 F17 |
| symptom: Right hand weakness three weeks after operation | Three weeks postoperation, there was a sudden onset of right hand weakness | C:B15 B16 B17 | S:F12 F13 F14 |
| treatment: Halo traction before surgery | halo traction prior to surgery | S:B12 B13 | S:F02 F18 |
| procedure: Revision at three months | At three months postoperation, the patient opted to undergo revision surgery | S:B34 B36 B38 | O |
| outcome: Ambulation at discharge | he was able to ambulate at discharge | S:B24 | S:F07 |

### Findings

- **baseline / unsupported / B06**: Adds hydroceles as an admission reason. Source: “A 63-year-old man”
- **baseline / negation / B22 B23**: Lists dysphagia as a positive symptom. Source: “There was no dysphagia”
- **baseline / unsupported / B28 B29**: Invents 100mg dose for a halo-vest. Source: “halo-vest for immobilization”
- **baseline / linkage / B15 B16**: Assigns right hand weakness to left shoulder/arm. Source: “sudden onset of right hand weakness”
- **finetuned / chronology / F10**: Times presenting weakness before the accident. Source: “He presented with marked left paraparesis”
- **finetuned / linkage / F16 F17**: Attributes CT dislodgement and postoperative function to MRI. Source: “The CT scan demonstrated plate and cage dislodgement”
- **finetuned / linkage / F18 F19**: Assigns the later halo-vest response to earlier halo traction. Source: “He was then put into a halo-vest for immobilization”

### Reference Review

No additional concern recorded; this is not an exhaustive certification.

### Judge Review

- **reference_only_penalty**: Fine-tuned fidelity criticizes uneventful course, ambulation and collar because absent from reference; all are explicit in source. Source: “The surgery went smoothly and the hospitalization was uneventful.”
- **source_supported**: Halo traction is an explicit admission purpose; calling it an unsupported admission reason is unwarranted. Source: “the patient was admitted to the intensive care unit for halo traction prior to surgery”

## validation:2654

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 70 | 70-year-old man | S:@70-year-old man | S:F03 |
| sex: Male | 70-year-old man | S:@70-year-old man | S:F04 |
| history: Prior gastrectomy for cancer | history of gastrectomy for gastric cancer | S:@history of gastrectomy for gastric cancer | S:F05 |
| symptom: Asymptomatic | An asymptomatic | S:@asymptomatic | O |
| investigation: KD diameter 53 mm on CT | was 53 mm | S:@was 53 mm | S:F07 F08 |
| investigation: Normal cardiac function on echo | echocardiography revealed normal cardiac function | S:@echocardiography revealed normal cardiac function | O |
| procedure: LCA to LSCA bypass with 7-mm graft | the LCA to LSCA bypass was performed using a 7-mm expanded polytetrafluoroethylene graft | S:@the LCA to LSCA bypass was performed using a 7-mm expanded polytetrafluoroethylene graft | O |
| procedure: 16-mm plug placement | a 16-mm Amplatzer vascular plug II | S:@a 16-mm Amplatzer vascular plug II | O |

### Findings

- **baseline / format_copy / @"visit motivation": " asymptomatic**: Unclosed visit-motivation string copies most of the note; readable facts survive but structured extraction fails. Source: “An asymptomatic 70-year-old man”
- **finetuned / linkage / F07 F08**: Assigns coronary angiography result to CT. Source: “Preoperative coronary angiography revealed no significant coronary artery disease”
- **finetuned / linkage / F06**: Adds right ventricular (LV) embolization and clipping of the LV vent tube; source describes vent insertion and LSCA embolization. Source: “left ventricular (LV) vent tube via the right pulmonary vein”
- **finetuned / unsupported / F06**: Completes the truncated ascending-aorta text as clipping to prevent steal; the source describes intercostal arteries being clipped. Source: “The ascending”

### Reference Review

- **temporal_status / R05 R07**: Reference includes completed descending-aorta replacement; visible note establishes planning and operative steps but truncates before explicit completion. Source: “we planned hybrid repair”

### Judge Review

- **source_supported**: Detected diagnoses in visit motivation are source-supported; gastrectomy in medical history preserves historical context. Source: “KD and ALSA detected on follow-up computed tomography (CT)”
- **overbroad_criticism**: Many operative details called unsupported are explicit; isolate invented ventricular/clipping relations instead. Source: “Right lateral thoracotomy was performed through the fourth intercostal space”

## validation:1133

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 16 | A 16-year-old girl | S:B03 | S:F02 |
| sex: Female | A 16-year-old girl | X:B04 B19 | S:F03 |
| history: Known sickle cell disease | known case of sickle cell disease | S:B05 | S:F04 |
| treatment: Four blood transfusions | blood transfusion four times | X:B06 B07 B08 | S:F04 |
| symptom: Joint pains | Patient also complained of joint pains | C:B11 B12 B14 B15 | S:F07 F08 |
| investigation: Mucosal pallor and smooth tongue | including mucosal pallor and abnormalities of tongue morphology | S:B17 B18 | S:F16 F17 |
| investigation: Electrophoresis HbS and HbF | Hemoglobin electrophoresis revealed HbS and HbF | O | S:F20 F21 |
| treatment: Chemotherapy helps control condition | condition was under control because of blood transfusion and chemotherapy | O | O |

### Findings

- **baseline / linkage / B06 B07 B08**: Mixes three hospitalizations and four transfusions. Source: “hospitalized thrice and had been given blood transfusion four times”
- **baseline / linkage / B11 B12 B14 B15**: Places joint pain in upper/lower lip. Source: “Patient also complained of joint pains”
- **baseline / contradiction / B19**: Adds an inconsistent male admission. Source: “A 16-year-old girl”
- **finetuned / assertion_status / F05 F06**: Calls an oral finding a surgery. Source: “the child had root stump of 26”
- **finetuned / repetition / F20 F21**: Loops electrophoresis until malformed truncation; repeats add no new coverage. Source: “Hemoglobin electrophoresis revealed HbS and HbF”

### Reference Review

- **omission / R05**: Reference omits hospitalization and transfusion counts. Source: “hospitalized thrice and had been given blood transfusion four times”

### Judge Review

- **source_supported**: Both fidelity reasons and baseline coverage call transfusion history invented; it is explicit. Count mixing in baseline remains a real error. Source: “blood transfusion four times”

## validation:1628

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 68 | A 68-year-old man | C:B09 | S:F03 |
| sex: Male | A 68-year-old man | O | S:F04 |
| history: Arch replacement at 56 | At 56 years of age, the patient had undergone a total arch replacement | P:B03 | S:F05 F06 F07 |
| symptom: Hoarseness at presentation | expressed hoarseness in his voice | S:B16 | S:F11 F13 |
| investigation: CT giant pseudoaneurysm | showed a giant pseudoaneurysm at the site of the island reconstruction 11 years later | O | O |
| investigation: Normal sinus rhythm on ECG | An electrocardiogram showed normal sinus rhythm | O | O |
| investigation: Chest X-ray arch/diaphragm changes | A chest X-ray revealed enlargement of the left 1st arch and elevation of the left diaphragm | O | O |
| treatment: Current surgery chosen, not yet shown performed | he opted to undergo surgery at our institution | C:B04 B05 B20 B21 | C:F08 F09 F10 |

### Findings

- **baseline / linkage / B09 B10**: Uses height as age 168 and weight as height 71. Source: “168 cm in height and weighed 71 kg”
- **baseline / chronology / B20 B21**: Invents procedure at two weeks; source supplies no such interval. Source: “he opted to undergo surgery at our institution”
- **finetuned / assertion_status / F08 F09 F10**: Converts current decision for surgery into completed surgery at the 11-year CT interval. Source: “he opted to undergo surgery at our institution”
- **finetuned / linkage / F19 F20**: Treats earlier outside-hospital inoperability as a response to current surgery. Source: “determined to be inoperable by the other hospital”

### Reference Review

- **temporal_status / R24**: Generic Surgery lacks planned/decided status; note has not established a performed current operation. Source: “he opted to undergo surgery at our institution”

### Judge Review

- **source_supported**: Baseline graft details are source-supported, despite fidelity calling them unsupported. Source: “a 30-mm synthetic vascular graft with one branch”
- **source_supported**: Scar is explicit; placement in symptom details can be criticized separately from its truth. Source: “The patient had a median sternotomy scar.”

## validation:1722

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 75 | 75-year-old white female | S:B14 | S:F03 |
| sex: Female | 75-year-old white female | S:B15 | S:F04 |
| history: Refractory CML diagnosed 2004 | refractory CML, diagnosed in 2004 | S:B16 | S:F05 |
| treatment: Bosutinib 300mg daily for five years | currently on bosutinib 300 mg daily for 5 years | S:B94 | O |
| treatment: Nilotinib 400mg | nilotinib 400 mg | O | S:F21 F22 |
| treatment: Dasatinib retrial 50mg daily | Dasatinib 50 mg daily was started | O | C:F23 F24 |
| procedure: Pericardial window January 2012 | underwent a pericardial window placement in the same month | X:B77 B78 B88 B89 | O |
| investigation: Negative mutational analysis | Follow-up with mutational analysis was negative | S:B35 B36 | S:F16 F17 |

### Findings

- **baseline / unsupported / B27 B30 B65 B68**: Adds fatigue, headache and mitochondrial analysis/mitochondophagy. Source: “She developed a cough relieved by steroids”
- **baseline / chronology / B88 B89**: Places pericardial window in 1998 in follow-up. Source: “in January of 2012”
- **finetuned / linkage / F18 F19**: Uses Biotin as imatinib dosage. Source: “imatinib 800 mg, which was subsequently lowered to 600 mg a day”
- **finetuned / linkage / F23 F24**: Assigns imatinib 800mg dose to dasatinib. Source: “Dasatinib 50 mg daily was started”
- **finetuned / linkage / F29 F31**: Assigns later dasatinib cough/steroid response to hydroxyurea. Source: “Dasatinib 50 mg daily was started”
- **finetuned / placement / F09 F10**: Calls biopsy a symptom. Source: “Subsequent bone marrow aspirate and biopsy were diagnostic for CML”

### Reference Review

- **causal_certainty / R23**: Reference says imatinib caused the effusions; source only says most likely. Source: “most likely from imatinib”

### Judge Review

- **source_supported**: Fine-tuned biopsy result is explicit; it is not incorrect merely because it occupies examinations. Source: “A bone marrow biopsy done in January of 2012 showed chronic-phase CML.”
- **source_supported**: White female descriptor is in source; including race in sex violates field policy rather than fabricating demographics. Source: “75-year-old white female”

## validation:2890

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 73 | A 73-year-old man | S:B03 | S:F03 |
| sex: Male | A 73-year-old man | X:B04 B07 | S:F04 |
| history: Myeloma, diabetes and coronary disease | multiple myeloma after chemotherapy, diabetes, and coronary artery disease | S:B05 | O |
| procedure: ORIF performed | the following day for open reduction and internal fixation | S:@the following day for open reduction and internal fixation | S:F05 |
| treatment: Knee immobilizer for three weeks | knee immobilizer to be worn at all times for 3 weeks | S:@knee immobilizer to be worn at all times for 3 weeks | S:F06 |
| investigation: Abnormal labs | Several of these laboratory values were found to be abnormal | S:@Several of these laboratory values were found to be abnormal | S:F11 F12 |
| symptom: Quadriceps atrophy at eight weeks | he did have notable quadriceps atrophy | C:B16 | P:F15 |
| outcome: Skilled nursing disposition on day five | discharged to a skilled nursing facility on postoperative day 5 | O | S:F16 |

### Findings

- **baseline / contradiction / B07**: Patient information says Female while admission says Male. Source: “A 73-year-old man”
- **baseline / unsupported / B10 B12**: Invents 1000mg daily dose and no reaction observed. Source: “started on calcium and vitamin D supplements”
- **baseline / negation / B16**: Denies significant atrophy. Source: “he did have notable quadriceps atrophy”
- **finetuned / linkage / F15**: Makes later imaging and atrophy a supplement reaction; the note states follow-up observations without that causal claim. Source: “At his 8-week postoperative appointment”
- **finetuned / chronology / F02**: Reverses fall and fracture ordering in admission wording. Source: “fracture after sustaining a mechanical ground level fall”

### Reference Review

- **omission / R19 R20**: Reference omits explicit immobilizer duration; source supports it. Source: “knee immobilizer to be worn at all times for 3 weeks”

### Judge Review

- **reference_only_penalty**: Fine-tuned fidelity calls immobilizer duration, lab specifics and follow-up unsupported although all are explicit. Source: “knee immobilizer to be worn at all times for 3 weeks”
- **missed_readable_evidence**: Baseline surgery timing survives in a Symptoms array; judge says omitted. Source: “the following day for open reduction and internal fixation”

## validation:435

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 28 | A 28-year-old female | S:B11 | S:F03 |
| sex: Female | A 28-year-old female | S:B12 | S:F04 |
| visit: Psychiatric diagnosis/treatment visit | came to our department for psychiatric diagnosis and treatment | O | S:F01 |
| history: OCD diagnosis age 26 | diagnosed with OCD in a psychiatric hospital at the age of 26 | S:B10 | A:F02 F09 |
| symptom: Obsessive words and images | words rape, crematorium, neck hanging, unhappy, death, die, and kill | P:B17 | S:F05 F07 |
| symptom: Repeating different to erase images | erase the words and images by repeating the word different | P:B20 | O |
| treatment: Aripiprazole and fluvoxamine | Treatment with aripiprazole and fluvoxamine was initiated | O | O |
| outcome: Six months counseling without relief | received psychoanalytic counseling from a psychiatrist for 6 months, but she did not experience relief | O | O |

### Findings

- **baseline / unsupported / B14**: Adds depression, anxiety-disorder and eating-disorder history. Source: “She was diagnosed with OCD”
- **baseline / assertion_status / B15 B16 B17**: Converts symptom evolution into surgery. Source: “After four months, she began to think”
- **baseline / linkage / B18 B19 B20**: Confuses self-directed mental rituals with the six-month professional counseling. Source: “She tried to counteract these obsessive-compulsive thoughts”
- **finetuned / unsupported / F07**: Expands obsessive content with invented words and people, including reminiscerated and children. Source: “the face of an acquaintance”
- **finetuned / repetition / @'things', 'places', 'things', 'places'**: Repeated objects/things/places consumes output budget and leaves malformed output without treatment sections. Source: “She was”

### Reference Review

- **causal_ambiguity / R06 R07**: No relief is explicitly tied to counseling; avoid labeling aripiprazole/fluvoxamine drug failure as certain. Source: “received psychoanalytic counseling from a psychiatrist for 6 months, but she did not experience relief”
- **omission / R04 R05**: Reference leaves medical history empty despite explicit prior OCD diagnosis. Source: “diagnosed with OCD in a psychiatric hospital at the age of 26”

### Judge Review

- **source_supported**: Fine-tuned visit motivation is an explicit source paraphrase, despite judge calling it wrong. Source: “came to our department for psychiatric diagnosis and treatment”
- **source_supported**: Pregnancy context is explicit; broad timing of all later obsessions to pregnancy remains uncertain. Source: “health of her fetus during pregnancy”

## validation:337

| Field / probe | Source quote | Baseline | Fine-tuned |
| --- | --- | --- | --- |
| age: Age 63 | Sixty-three-year-old woman | C:B08 | C:F02 |
| sex: Female | Sixty-three-year-old woman | S:B09 | O |
| history: Breast reduction twenty years ago | inferior pedicle breast reduction surgery performed 20 years ago | S:B12 | C:F03 F04 |
| procedure: Left nipple-sparing mastectomy | left nipple-sparing mastectomy through her previous vertical limb | S:B18 | X:F03 F04 F05 |
| procedure: Implant exchange twelve weeks later | Twelve weeks later, we exchange her tissue expander | C:B51 B53 B54 | O |
| procedure: Contralateral reduction 300g | contralateral reduction of 300 g | O | O |
| procedure: LICAP flap reconstruction | The LICAP flap was chosen to reconstruct the upper pole of the left breast | A:B41 | A:F06 F07 |
| treatment: Lipofilling discussed, not performed | We discussed multiple sessions of lipofilling | P:B40 | C:F08 F09 |

### Findings

- **baseline / linkage / B08**: Uses height 69 as patient age instead of 63. Source: “She is 69 inches tall”
- **baseline / unsupported / B19 B21 B23 B24 B26 B27 B32 B33**: Invents swelling, pain, discoloration and lumps with weekly timelines. Source: “significant size asymmetry between the breasts”
- **baseline / unsupported / B35 B38 B39**: Invents chest X-ray, breast ultrasound and biopsy. Source: “An intraoperative photograph is shown”
- **baseline / chronology / B48 B54**: Invents week-six and week-seven treatment timelines. Source: “Twelve weeks later”
- **finetuned / linkage / F02**: Places supported height/weight/BMI in age field, leaving real age absent. Source: “She is 69 inches tall with a weight of 215 pounds”
- **finetuned / chronology / F03 F04**: Assigns twenty-year interval from earlier reduction to current mastectomy. Source: “inferior pedicle breast reduction surgery performed 20 years ago”
- **finetuned / assertion_status / F08 F09**: Lists proposed lipofilling and presents preexisting asymmetry as its reaction. Source: “We discussed multiple sessions of lipofilling”

### Reference Review

- **temporal_status / R16 R17**: Reference treatment/reaction pairing can imply performed lipofilling, though it was discussed as an alternative. Source: “We discussed multiple sessions of lipofilling”

### Judge Review

- **source_supported**: Judge calls height, weight and BMI invented; values are explicit, but their use in age is a true role error. Source: “She is 69 inches tall with a weight of 215 pounds and a corresponding BMI of 31.8 kg/m2.”
