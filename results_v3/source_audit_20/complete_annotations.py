"""Complete the manually reviewed diagnostic ledger; original drafts stay intact."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
drafts = json.loads((ROOT / 'annotations.json').read_text(encoding='utf-8'))
added = []

def case(number, probes, findings, reference=(), judge=()):
    added.append(dict(case_id=f'validation:{number}', probes=probes, findings=findings,
                      reference_review=list(reference), judge_review=list(judge)))

case(412, [
 ['age','Age 63','A 63-year-old man','S:B08','S:F03'],
 ['sex','Male','A 63-year-old man','S:B09','S:F04'],
 ['investigation','MRI increased intramedullary signal','increased intramedullary signal intensity on T2 weighted magnetic resonance imaging','O','C:F16 F17'],
 ['investigation','CT plate and cage dislodgement','The CT scan demonstrated plate and cage dislodgement','P:B26 B27','C:F16 F17'],
 ['symptom','Right hand weakness three weeks after operation','Three weeks postoperation, there was a sudden onset of right hand weakness','C:B15 B16 B17','S:F12 F13 F14'],
 ['treatment','Halo traction before surgery','halo traction prior to surgery','S:B12 B13','S:F02 F18'],
 ['procedure','Revision at three months','At three months postoperation, the patient opted to undergo revision surgery','S:B34 B36 B38','O'],
 ['outcome','Ambulation at discharge','he was able to ambulate at discharge','S:B24','S:F07'],
], [
 ['baseline','unsupported','B06','A 63-year-old man','Adds hydroceles as an admission reason.'],
 ['baseline','negation','B22 B23','There was no dysphagia','Lists dysphagia as a positive symptom.'],
 ['baseline','unsupported','B28 B29','halo-vest for immobilization','Invents 100mg dose for a halo-vest.'],
 ['baseline','linkage','B15 B16','sudden onset of right hand weakness','Assigns right hand weakness to left shoulder/arm.'],
 ['finetuned','chronology','F10','He presented with marked left paraparesis','Times presenting weakness before the accident.'],
 ['finetuned','linkage','F16 F17','The CT scan demonstrated plate and cage dislodgement','Attributes CT dislodgement and postoperative function to MRI.'],
 ['finetuned','linkage','F18 F19','He was then put into a halo-vest for immobilization','Assigns the later halo-vest response to earlier halo traction.'],
], [], [
 ['reference_only_penalty','The surgery went smoothly and the hospitalization was uneventful.','Fine-tuned fidelity criticizes uneventful course, ambulation and collar because absent from reference; all are explicit in source.'],
 ['source_supported','the patient was admitted to the intensive care unit for halo traction prior to surgery','Halo traction is an explicit admission purpose; calling it an unsupported admission reason is unwarranted.'],
])

case(2654, [
 ['age','Age 70','70-year-old man','S:@70-year-old man','S:F03'],
 ['sex','Male','70-year-old man','S:@70-year-old man','S:F04'],
 ['history','Prior gastrectomy for cancer','history of gastrectomy for gastric cancer','S:@history of gastrectomy for gastric cancer','S:F05'],
 ['symptom','Asymptomatic','An asymptomatic','S:@asymptomatic','O'],
 ['investigation','KD diameter 53 mm on CT','was 53 mm','S:@was 53 mm','S:F07 F08'],
 ['investigation','Normal cardiac function on echo','echocardiography revealed normal cardiac function','S:@echocardiography revealed normal cardiac function','O'],
 ['procedure','LCA to LSCA bypass with 7-mm graft','the LCA to LSCA bypass was performed using a 7-mm expanded polytetrafluoroethylene graft','S:@the LCA to LSCA bypass was performed using a 7-mm expanded polytetrafluoroethylene graft','O'],
 ['procedure','16-mm plug placement','a 16-mm Amplatzer vascular plug II','S:@a 16-mm Amplatzer vascular plug II','O'],
], [
 ['baseline','format_copy','@"visit motivation": " asymptomatic','An asymptomatic 70-year-old man','Unclosed visit-motivation string copies most of the note; readable facts survive but structured extraction fails.'],
 ['finetuned','linkage','F07 F08','Preoperative coronary angiography revealed no significant coronary artery disease','Assigns coronary angiography result to CT.'],
 ['finetuned','linkage','F06','left ventricular (LV) vent tube via the right pulmonary vein','Adds right ventricular (LV) embolization and clipping of the LV vent tube; source describes vent insertion and LSCA embolization.'],
 ['finetuned','unsupported','F06','The ascending','Completes the truncated ascending-aorta text as clipping to prevent steal; the source describes intercostal arteries being clipped.'],
], [
 ['temporal_status','R05 R07','we planned hybrid repair','Reference includes completed descending-aorta replacement; visible note establishes planning and operative steps but truncates before explicit completion.'],
], [
 ['source_supported','KD and ALSA detected on follow-up computed tomography (CT)','Detected diagnoses in visit motivation are source-supported; gastrectomy in medical history preserves historical context.'],
 ['overbroad_criticism','Right lateral thoracotomy was performed through the fourth intercostal space','Many operative details called unsupported are explicit; isolate invented ventricular/clipping relations instead.'],
])

case(1133, [
 ['age','Age 16','A 16-year-old girl','S:B03','S:F02'],
 ['sex','Female','A 16-year-old girl','X:B04 B19','S:F03'],
 ['history','Known sickle cell disease','known case of sickle cell disease','S:B05','S:F04'],
 ['treatment','Four blood transfusions','blood transfusion four times','X:B06 B07 B08','S:F04'],
 ['symptom','Joint pains','Patient also complained of joint pains','C:B11 B12 B14 B15','S:F07 F08'],
 ['investigation','Mucosal pallor and smooth tongue','including mucosal pallor and abnormalities of tongue morphology','S:B17 B18','S:F16 F17'],
 ['investigation','Electrophoresis HbS and HbF','Hemoglobin electrophoresis revealed HbS and HbF','O','S:F20 F21'],
 ['treatment','Chemotherapy helps control condition','condition was under control because of blood transfusion and chemotherapy','O','O'],
], [
 ['baseline','linkage','B06 B07 B08','hospitalized thrice and had been given blood transfusion four times','Mixes three hospitalizations and four transfusions.'],
 ['baseline','linkage','B11 B12 B14 B15','Patient also complained of joint pains','Places joint pain in upper/lower lip.'],
 ['baseline','contradiction','B19','A 16-year-old girl','Adds an inconsistent male admission.'],
 ['finetuned','assertion_status','F05 F06','the child had root stump of 26','Calls an oral finding a surgery.'],
 ['finetuned','repetition','F20 F21','Hemoglobin electrophoresis revealed HbS and HbF','Loops electrophoresis until malformed truncation; repeats add no new coverage.'],
], [
 ['omission','R05','hospitalized thrice and had been given blood transfusion four times','Reference omits hospitalization and transfusion counts.'],
], [
 ['source_supported','blood transfusion four times','Both fidelity reasons and baseline coverage call transfusion history invented; it is explicit. Count mixing in baseline remains a real error.'],
])

case(1628, [
 ['age','Age 68','A 68-year-old man','C:B09','S:F03'],
 ['sex','Male','A 68-year-old man','O','S:F04'],
 ['history','Arch replacement at 56','At 56 years of age, the patient had undergone a total arch replacement','P:B03','S:F05 F06 F07'],
 ['symptom','Hoarseness at presentation','expressed hoarseness in his voice','S:B16','S:F11 F13'],
 ['investigation','CT giant pseudoaneurysm','showed a giant pseudoaneurysm at the site of the island reconstruction 11 years later','O','O'],
 ['investigation','Normal sinus rhythm on ECG','An electrocardiogram showed normal sinus rhythm','O','O'],
 ['investigation','Chest X-ray arch/diaphragm changes','A chest X-ray revealed enlargement of the left 1st arch and elevation of the left diaphragm','O','O'],
 ['treatment','Current surgery chosen, not yet shown performed','he opted to undergo surgery at our institution','C:B04 B05 B20 B21','C:F08 F09 F10'],
], [
 ['baseline','linkage','B09 B10','168 cm in height and weighed 71 kg','Uses height as age 168 and weight as height 71.'],
 ['baseline','chronology','B20 B21','he opted to undergo surgery at our institution','Invents procedure at two weeks; source supplies no such interval.'],
 ['finetuned','assertion_status','F08 F09 F10','he opted to undergo surgery at our institution','Converts current decision for surgery into completed surgery at the 11-year CT interval.'],
 ['finetuned','linkage','F19 F20','determined to be inoperable by the other hospital','Treats earlier outside-hospital inoperability as a response to current surgery.'],
], [
 ['temporal_status','R24','he opted to undergo surgery at our institution','Generic Surgery lacks planned/decided status; note has not established a performed current operation.'],
], [
 ['source_supported','a 30-mm synthetic vascular graft with one branch','Baseline graft details are source-supported, despite fidelity calling them unsupported.'],
 ['source_supported','The patient had a median sternotomy scar.','Scar is explicit; placement in symptom details can be criticized separately from its truth.'],
])

case(1722, [
 ['age','Age 75','75-year-old white female','S:B14','S:F03'],
 ['sex','Female','75-year-old white female','S:B15','S:F04'],
 ['history','Refractory CML diagnosed 2004','refractory CML, diagnosed in 2004','S:B16','S:F05'],
 ['treatment','Bosutinib 300mg daily for five years','currently on bosutinib 300 mg daily for 5 years','S:B94','O'],
 ['treatment','Nilotinib 400mg','nilotinib 400 mg','O','S:F21 F22'],
 ['treatment','Dasatinib retrial 50mg daily','Dasatinib 50 mg daily was started','O','C:F23 F24'],
 ['procedure','Pericardial window January 2012','underwent a pericardial window placement in the same month','X:B77 B78 B88 B89','O'],
 ['investigation','Negative mutational analysis','Follow-up with mutational analysis was negative','S:B35 B36','S:F16 F17'],
], [
 ['baseline','unsupported','B27 B30 B65 B68','She developed a cough relieved by steroids','Adds fatigue, headache and mitochondrial analysis/mitochondophagy.'],
 ['baseline','chronology','B88 B89','in January of 2012','Places pericardial window in 1998 in follow-up.'],
 ['finetuned','linkage','F18 F19','imatinib 800 mg, which was subsequently lowered to 600 mg a day','Uses Biotin as imatinib dosage.'],
 ['finetuned','linkage','F23 F24','Dasatinib 50 mg daily was started','Assigns imatinib 800mg dose to dasatinib.'],
 ['finetuned','linkage','F29 F31','Dasatinib 50 mg daily was started','Assigns later dasatinib cough/steroid response to hydroxyurea.'],
 ['finetuned','placement','F09 F10','Subsequent bone marrow aspirate and biopsy were diagnostic for CML','Calls biopsy a symptom.'],
], [
 ['causal_certainty','R23','most likely from imatinib','Reference says imatinib caused the effusions; source only says most likely.'],
], [
 ['source_supported','A bone marrow biopsy done in January of 2012 showed chronic-phase CML.','Fine-tuned biopsy result is explicit; it is not incorrect merely because it occupies examinations.'],
 ['source_supported','75-year-old white female','White female descriptor is in source; including race in sex violates field policy rather than fabricating demographics.'],
])

case(2890, [
 ['age','Age 73','A 73-year-old man','S:B03','S:F03'],
 ['sex','Male','A 73-year-old man','X:B04 B07','S:F04'],
 ['history','Myeloma, diabetes and coronary disease','multiple myeloma after chemotherapy, diabetes, and coronary artery disease','S:B05','O'],
 ['procedure','ORIF following day','the following day for open reduction and internal fixation','S:@the following day for open reduction and internal fixation','S:F05'],
 ['treatment','Knee immobilizer for three weeks','knee immobilizer to be worn at all times for 3 weeks','S:@knee immobilizer to be worn at all times for 3 weeks','S:F06'],
 ['investigation','Abnormal labs','Several of these laboratory values were found to be abnormal','S:@Several of these laboratory values were found to be abnormal','S:F11 F12'],
 ['symptom','Quadriceps atrophy at eight weeks','he did have notable quadriceps atrophy','C:B16','P:F15'],
 ['outcome','Skilled nursing disposition on day five','discharged to a skilled nursing facility on postoperative day 5','O','S:F16'],
], [
 ['baseline','contradiction','B07','A 73-year-old man','Patient information says Female while admission says Male.'],
 ['baseline','unsupported','B10 B12','started on calcium and vitamin D supplements','Invents 1000mg daily dose and no reaction observed.'],
 ['baseline','negation','B16','he did have notable quadriceps atrophy','Denies significant atrophy.'],
 ['finetuned','linkage','F15','At his 8-week postoperative appointment','Makes later imaging and atrophy a supplement reaction; the note states follow-up observations without that causal claim.'],
 ['finetuned','chronology','F02','fracture after sustaining a mechanical ground level fall','Reverses fall and fracture ordering in admission wording.'],
], [
 ['omission','R19 R20','knee immobilizer to be worn at all times for 3 weeks','Reference omits explicit immobilizer duration; source supports it.'],
], [
 ['reference_only_penalty','knee immobilizer to be worn at all times for 3 weeks','Fine-tuned fidelity calls immobilizer duration, lab specifics and follow-up unsupported although all are explicit.'],
 ['missed_readable_evidence','the following day for open reduction and internal fixation','Baseline surgery timing survives in a Symptoms array; judge says omitted.'],
])

case(435, [
 ['age','Age 28','A 28-year-old female','S:B11','S:F03'],
 ['sex','Female','A 28-year-old female','S:B12','S:F04'],
 ['visit','Psychiatric diagnosis/treatment visit','came to our department for psychiatric diagnosis and treatment','O','S:F01'],
 ['history','OCD diagnosis age 26','diagnosed with OCD in a psychiatric hospital at the age of 26','S:B10','A:F02 F09'],
 ['symptom','Obsessive words and images','words rape, crematorium, neck hanging, unhappy, death, die, and kill','P:B17','S:F05 F07'],
 ['symptom','Repeating different to erase images','erase the words and images by repeating the word different','P:B20','O'],
 ['treatment','Aripiprazole and fluvoxamine','Treatment with aripiprazole and fluvoxamine was initiated','O','O'],
 ['outcome','Six months counseling without relief','received psychoanalytic counseling from a psychiatrist for 6 months, but she did not experience relief','O','O'],
], [
 ['baseline','unsupported','B14','She was diagnosed with OCD','Adds depression, anxiety-disorder and eating-disorder history.'],
 ['baseline','assertion_status','B15 B16 B17','After four months, she began to think','Converts symptom evolution into surgery.'],
 ['baseline','linkage','B18 B19 B20','She tried to counteract these obsessive-compulsive thoughts','Confuses self-directed mental rituals with the six-month professional counseling.'],
 ['finetuned','unsupported','F07','the face of an acquaintance','Expands obsessive content with invented words and people, including reminiscerated and children.'],
 ['finetuned','repetition','@\u0027things\u0027, \u0027places\u0027, \u0027things\u0027, \u0027places\u0027','She was','Repeated objects/things/places consumes output budget and leaves malformed output without treatment sections.'],
], [
 ['causal_ambiguity','R06 R07','received psychoanalytic counseling from a psychiatrist for 6 months, but she did not experience relief','No relief is explicitly tied to counseling; avoid labeling aripiprazole/fluvoxamine drug failure as certain.'],
 ['omission','R04 R05','diagnosed with OCD in a psychiatric hospital at the age of 26','Reference leaves medical history empty despite explicit prior OCD diagnosis.'],
], [
 ['source_supported','came to our department for psychiatric diagnosis and treatment','Fine-tuned visit motivation is an explicit source paraphrase, despite judge calling it wrong.'],
 ['source_supported','health of her fetus during pregnancy','Pregnancy context is explicit; broad timing of all later obsessions to pregnancy remains uncertain.'],
])

case(337, [
 ['age','Age 63','Sixty-three-year-old woman','C:B08','C:F02'],
 ['sex','Female','Sixty-three-year-old woman','S:B09','O'],
 ['history','Breast reduction twenty years ago','inferior pedicle breast reduction surgery performed 20 years ago','S:B12','C:F03 F04'],
 ['procedure','Left nipple-sparing mastectomy','left nipple-sparing mastectomy through her previous vertical limb','S:B18','X:F03 F04 F05'],
 ['procedure','Implant exchange twelve weeks later','Twelve weeks later, we exchange her tissue expander','C:B51 B53 B54','O'],
 ['procedure','Contralateral reduction 300g','contralateral reduction of 300 g','O','O'],
 ['procedure','LICAP flap reconstruction','The LICAP flap was chosen to reconstruct the upper pole of the left breast','P:B41','P:F06 F07'],
 ['treatment','Lipofilling discussed, not performed','We discussed multiple sessions of lipofilling','P:B40','C:F08 F09'],
], [
 ['baseline','linkage','B08','She is 69 inches tall','Uses height 69 as patient age instead of 63.'],
 ['baseline','unsupported','B19 B21 B23 B24 B26 B27 B32 B33','significant size asymmetry between the breasts','Invents swelling, pain, discoloration and lumps with weekly timelines.'],
 ['baseline','unsupported','B35 B38 B39','An intraoperative photograph is shown','Invents chest X-ray, breast ultrasound and biopsy.'],
 ['baseline','chronology','B48 B54','Twelve weeks later','Invents week-six and week-seven treatment timelines.'],
 ['finetuned','linkage','F02','She is 69 inches tall with a weight of 215 pounds','Places supported height/weight/BMI in age field, leaving real age absent.'],
 ['finetuned','chronology','F03 F04','inferior pedicle breast reduction surgery performed 20 years ago','Assigns twenty-year interval from earlier reduction to current mastectomy.'],
 ['finetuned','assertion_status','F08 F09','We discussed multiple sessions of lipofilling','Lists proposed lipofilling and presents preexisting asymmetry as its reaction.'],
], [
 ['temporal_status','R16 R17','We discussed multiple sessions of lipofilling','Reference treatment/reaction pairing can imply performed lipofilling, though it was discussed as an alternative.'],
], [
 ['source_supported','She is 69 inches tall with a weight of 215 pounds and a corresponding BMI of 31.8 kg/m2.','Judge calls height, weight and BMI invented; values are explicit, but their use in age is a true role error.'],
])

if __name__ == '__main__':
    reviews = drafts + added
    changes = []
    def outcome(number, index, model, value, reason):
        row = next(c for c in reviews if c['case_id'] == f'validation:{number}')['probes'][index]
        col = 3 if model == 'baseline' else 4
        changes.append(dict(case_id=f'validation:{number}', probe=index+1, model=model,
                            before=row[col], after=value, reason=reason))
        row[col] = value
    outcome(593,0,'baseline','X:B03 B07 B10 B14','Correct age nine coexists with one and a delay used as age.')
    outcome(593,1,'baseline','X:B04 B08 B15','Correct female coexists with an invented male admission.')
    outcome(593,2,'finetuned','A:F05 F27','Closed reduction is explicit; puncture fixation is an unclear rendering of percutaneous pin fixation.')
    outcome(593,4,'finetuned','C:F10','Occlusion text is present, but attached to non-identification of hypothetical hematoma, without DSA attribution.')
    outcome(1351,0,'baseline','S:B03','Age is correct in admission context; no contradictory numeric age.')
    outcome(1351,1,'baseline','X:B01 B04','Woman in visit text coexists with ethnicity used as sex.')
    outcome(1351,4,'baseline','S:B07 B17','Admission prose explicitly describes palpitations with exertion.')
    outcome(1351,4,'finetuned','S:F09','Symptom details explicitly preserve exertional palpitations.')
    outcome(113,2,'finetuned','S:F02','DM clinical context survives in admission reason.')
    outcome(937,2,'baseline','S:B08','Medical history nested under patient information still identifies historical conditions.')
    outcome(937,3,'finetuned','S:F10','Baseline normal ECG remains explicitly identified in symptom details.')
    outcome(937,6,'baseline','S:B04','Negative biomarker assertion is explicit; added admission role is a separate placement concern.')
    outcome(1812,0,'baseline','X:B01 B03 B07','Visit identifies infant; explicit age fields incorrectly use maternal age and repeat-test delay.')
    outcome(1812,7,'baseline','O','One-week resolution imaging is present, but discharge event itself is absent.')
    outcome(1812,4,'baseline','S:B24','Dosage string explicitly names recombinant FVIII and 50 U/kg, despite wrong event name/time elsewhere.')
    outcome(1812,4,'finetuned','S:F21','Reaction prose explicitly says initially treated with 50 U/kg recombinant FVIII; parent relation is separately flagged.')
    outcome(1388,1,'baseline','X:B04 B07','Male in contextual text conflicts with ethnicity in sex field.')
    outcome(1388,4,'baseline','S:@two seizure-like episodes earlier that morning','Nested symptoms array preserves the seizure event with its correct role.')
    outcome(128,0,'baseline','S:B03','Correct patient age within admission details; schema placement alone is separate.')
    outcome(128,1,'baseline','S:B04','Correct sex within admission details.')
    outcome(128,3,'baseline','S:B02 B05','Explicit negative symptom prose preserves negation.')
    outcome(128,5,'finetuned','S:F28 F29','VATS biopsy is accurately named in diagnosis tests; surgery/test dual use is acceptable.')
    outcome(128,7,'baseline','S:B09','Bronchoscopy and negative result explicitly paired in prose.')
    outcome(302,0,'baseline','A:B09','Age 52 occurs in relative-history admissions; patient assignment is unclear, not a clean match.')
    outcome(302,2,'baseline','S:B12','Explicit was treated with dosulepin prose preserves this drug/dose subclaim.')
    outcome(302,3,'baseline','S:B12','Same sentence explicitly links sweating to dosulepin.')
    outcome(302,4,'baseline','S:B15','Prose explicitly links amitriptyline to racing heart.')
    outcome(302,6,'baseline','S:B16','Prose explicitly preserves venlafaxine XL 75mg.')
    outcome(302,5,'finetuned','S:F18','Symptom details explicitly state mirtazapine and its titration; no changed event role for this subclaim.')
    outcome(1241,0,'baseline','X:B03 B07','Correct age 72 coexists with history sentences in age fields.')
    outcome(1241,1,'baseline','S:B04','Correct sex in admission context.')
    outcome(1241,3,'baseline','S:B05','Historical disease and antibody treatment explicit in physiological context.')
    outcome(1241,2,'finetuned','P:F01 F02','Correct balance-disorder motivation remains, but admission reason substitutes hemiplegia; no explicit denial of balance disorder.')
    outcome(337,6,'baseline','A:B41','Generic autologous reconstruction in test field does not clearly preserve LICAP choice and upper-pole reconstruction.')
    outcome(337,6,'finetuned','A:F06 F07','Flap dissection survives as photograph finding, but LICAP choice and reconstruction target are not explicit.')
    # Narrow the probe to the event, leaving missing timing for the case narrative.
    next(c for c in reviews if c['case_id']=='validation:2890')['probes'][3][1]='ORIF performed'
    # These draft explanations overstated what the saved judge actually said.
    c = next(c for c in reviews if c['case_id']=='validation:1388')
    c['judge_review'] = [r for r in c['judge_review'] if r[0] != 'internal_inconsistency']
    changes.append(dict(case_id=c['case_id'], reason='Removed draft claim that judge conflated doubled mass with four-day return; saved reasons do not establish that criticism.'))
    c = next(c for c in reviews if c['case_id']=='validation:302')
    c['judge_review'][1] = ['placement_sensitivity',c['judge_review'][1][1],
        'Coverage judge recognizes mirtazapine in symptom details and penalizes placement. Under this audit policy the explicit drug/titration subclaim survives; this is policy sensitivity, not a false-omission judge error.']
    c = next(c for c in reviews if c['case_id']=='validation:1241')
    c['reference_review'][1][3] = 'Lesion reduction occurred during combined therapy; reference places it under TMP/SMX response. This is causal attribution ambiguity, not proof of a false outcome or claim of sole causation.'
    # Add an actual misreading observed during the full reason check.
    next(c for c in reviews if c['case_id']=='validation:937')['judge_review'].append(
        ['misread_output','the patient was subjected to percutaneous revascularization of the LAD',
         'Fine-tuned fidelity says revascularization is under treatment reaction, but it is the treatment name; the preprocedure lesion used as reaction remains wrong.'])
    (ROOT / 'reconciliation_log.json').write_text(json.dumps(changes, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    (ROOT / 'reviewed_annotations.json').write_text(json.dumps(reviews, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Saved {len(drafts) + len(added)} case reviews (semantic reconciliation follows).')
