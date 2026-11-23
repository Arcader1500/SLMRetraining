# Side-by-Side Showcase (`gen_rp_1.08`)

## validation:1180
- **Base:** raw_valid=False, exact_F1=0.000, soft_F1=0.028, toks=597
- **Fine-tuned v2:** raw_valid=True, exact_keys=False, exact_F1=0.551, soft_F1=0.659, toks=574

**Clinical Note (excerpt):**
```
A 48-year-old male weighing 60 kg presented to surgery outdoor with chief complaint of progressive swelling in the right side of the neck since last 3 months following trauma. The swelling was initially of small size which gradually progressed to the current size. On the basis of clinical finding and radiological report, it was diagnosed as subclavian artery aneurysm and surgical intervention was advised. The patient also had a history of angina 4 months back for which he was hospitalized and treated. He was advised tablet aspirin 75 mg and tablet clopidogrel 75 mg once daily on a regular basi...
```
**Reference JSON:**
```json
{"visit motivation":"Progressive swelling in the right side of the neck since last 3 months following trauma","admission":[{"reason":"Diagnosed subclavian artery aneurysm"}],"patient information":{"age":"48","sex":"male","weight":"60 kg"},"patient medical history":{"physiological context":"History of angina 4 months back, hospitalized and treated"},"surgeries":[{"reason":"Subclavian artery aneurysm","Type":"Surgical intervention was advised","details":"RA with CEA was planned as the anesthetic technique due to poor cardiac functional status"}],"symptoms":[{"name of symptom":"Swelling","location":"Right side of the neck","time":"Last 3 months","temporalisation":"Progressive","details":"Initially small size, gradually progressed to current size"}],"medical examinations":[{"name":"Local examination","result":"Mass around 3 cm × 3 cm × 4 cm, diffuse, pulsatile, soft in consistency, and mobile"},{"name":"Two-dimensional echocardiography","result":"Ejection fraction of around 30% with mild left ventricular hypokinesia and grade 2 diastolic dysfunction"}],"diagnosis tests":[{"test":"Magnetic resonance imaging angiography of the neck","result":"Aneurysm of subclavian artery, 1 cm lateral t
```
**Base Output:**
```
```json
{
  "visit motivation": "Patient presented with progressive swelling in the right side of the neck since last 3 months following trauma.",
  "admission": {
    "date": "2024-10-27",
    "location": "Outdoor",
    "description": "Patient presents to surgery outdoors with chief complaint of progressive swelling in the right side of the neck since last 3 months following trauma."
  },
  "surgery": {
    "date": "2024-10-28",
    "location": "Surgery outdoor",
    "description": "Patient underwent surgery outdoors with chief complaint of progressive swelling in the right side of the neck since last 3 months following trauma."
  },
  "symptoms": {
    "description": "The swelling was initially of small size which gradually progressed to the current size. On the basis of clinical finding and radiological report, it was diagnosed as subclavian artery aneurysm and surgical intervention w
```
**Fine-Tuned v2 Output:**
```json
{"visit motivation":"Progressive swelling in the right side of the neck following trauma","admission":[{"reason":"Subclavian artery aneurysm and surgical intervention"}],"patient information":{"age":"48","sex":"male","weight":"60 kg"},"patient medical history":{"physiological context":"History of angina 4 months back for which he was hospitalized and treated"},"surgeries":[{"reason":"Subclavian artery aneurysm","Type":"Surgical intervention","details":"Surgery was advised due to poor cardiac functional status of the patient"}],"symptoms":[{"name of symptom":"Swelling","intensity of symptom":"Initial size of small size, gradually progressed to current size","location":"Right side of the neck","time":"Last 3 months","temporalisation":"Progressive","details":"Initially of small size, later to the current size"}],"medical examinations":[{"name":"Local examination","result":"Mass around 3 cm × 3 cm × 4 cm, diffuse, pulsatile, soft in consistency, and mobile"},{"name":"Magnetic resonance imaging angiography","result":"Aneurysm of subclavian artery, 1 cm lateral to the origin of internal carotid artery"},{"name":"Two-dimensional echocardiography","result":"Ejection fraction of around 30% 
```

## validation:937
- **Base:** raw_valid=False, exact_F1=0.000, soft_F1=0.000, toks=334
- **Fine-tuned v2:** raw_valid=True, exact_keys=False, exact_F1=0.519, soft_F1=0.597, toks=248

**Clinical Note (excerpt):**
```
A 66-year-old male with history of diabetes, hypercholesterolemia and hypertension was referred to our heart center complaining of acute chest pain. The baseline electrocardiography [] and cardiac examination were normal. Echocardiography revealed no hypo kinesis of all ventricular walls with ejection fraction of 70%. Laboratory tests did not show any significant alterations of cardiac biomarkers. He was considered with probably stable angina.
A 64-slice coronary computed tomography (MSCT, GE, USA) was performed two days after admission, which revealed an absence of the right coronary ostium w...
```
**Reference JSON:**
```json
{"visit motivation":"Complaining of acute chest pain","admission":[{"reason":"Acute chest pain","date":"Two days before the 64-slice coronary computed tomography (MSCT) was performed","care center details":"Heart center"}],"patient information":{"age":"66","sex":"Male"},"patient medical history":{"physiological context":"History of diabetes, hypercholesterolemia and hypertension"},"surgeries":[{"reason":"Coronary disease and SCA","Type":"Percutaneous revascularization of the LAD","details":"Following a written informed consent"}],"symptoms":[{"name of symptom":"Acute chest pain","location":"Chest"}],"medical examinations":[{"name":"Baseline electrocardiography","result":"Normal"},{"name":"Cardiac examination","result":"Normal"},{"name":"Echocardiography","result":"No hypo kinesis of all ventricular walls with ejection fraction of 70%"},{"name":"Laboratory tests","result":"No significant alterations of cardiac biomarkers"}],"diagnosis tests":[{"test":"64-slice coronary computed tomography (MSCT)","result":"Absence of the right coronary ostium with an isolated single left coronary artery, severe calcified, diffuse lesion in the proximal and middle LAD","condition":"Coronary disease a
```
**Base Output:**
```
```json
{
  "visit motivation": "Patient was referred to our heart center for acute chest pain.",
  "admission": {
    "date": "2023-10-27",
    "reason": "Patient presents with acute chest pain. Baseline ECG and cardiac examination were normal.",
    "medications": [],
    "symptoms": [],
    "medical examinations": [],
    "diagnosis tests": [],
    "treatments": []
  },
  "symptoms": [
    "Acute chest pain",
    "Cardiac discomfort",
    "Elevated troponin levels",
    "Pulmonary edema"
  ],
  "medical history": [
    "History of diabetes mellitus, hypercholesterolemia, and hypertension.",
    "Past surgeries (e.g., coronary artery disease, myocardial infarction)",
    "Recent medications (e.g., antihypertensives, antiarrhythmics)"
  ],
  "surgery": [
    "Coronary angiography",
    "Percutaneous revascularization of the LAD"
  ],
  "symptoms": [
    "Severe calcified, diffuse lesion
```
**Fine-Tuned v2 Output:**
```json
{"visit motivation":"Acute chest pain","admission":[{"reason":"Acute chest pain"}],"patient information":{"age":"66","sex":"male"},"patient medical history":{"physiological context":"History of diabetes, hypercholesterolemia and hypertension"},"surgeries":[{"reason":"Coronary disease and SCA","Type":"Percutaneous revascularization of the LAD","time":"Eight days after admission","details":"The patient underwent this procedure due to severe calcified, diffuse lesion in the proximal and middle LAD."}],"symptoms":[{"name of symptom":"Acute chest pain","location":"Chest","details":"Patient was referred to heart center for acute chest pain."}],"medical examinations":[{"name":"Echocardiography","result":"No hypo kinesis of all ventricular walls with ejection fraction of 70%"},{"name":"Cardiac examination","result":"Normal"},{"name":"Laboratory tests","result":"Did not show any significant alterations of cardiac biomarkers"}],"diagnosis tests":[{"test":"Coronary angiogram","severity":"Severe","result":"Confirmed coronary disease and SCA","condition":"Coronary disease and SCA","details":"Performed eight days after admission, following a written informed consent."}],"treatments":[],"discharg
```

## validation:294
- **Base:** raw_valid=False, exact_F1=0.032, soft_F1=0.054, toks=995
- **Fine-tuned v2:** raw_valid=True, exact_keys=False, exact_F1=0.240, soft_F1=0.447, toks=439

**Clinical Note (excerpt):**
```
A 16-year-old female patient reported with the chief complaint of apparent delay of the exfoliation of the upper right deciduous tooth. The clinical history did not reveal any systemic pathology associated with it. Intraoral examination revealed the presence of retained right maxillary deciduous central incisor (51), the absence of the corresponding tooth, i.e. right maxillary permanent central incisor (11), with the contralateral tooth already erupted. An intraoral periapical radiograph was obtained, which revealed the presence of a radio-opaque tooth-like structure in the apical region of 51...
```
**Reference JSON:**
```json
{"visit motivation":"Apparent delay of the exfoliation of the upper right deciduous tooth","admission":[],"patient information":{"age":"16","sex":"Female"},"patient medical history":{"physiological context":"No systemic pathology associated with the chief complaint"},"surgeries":[{"reason":"Excision of odontoma","Type":"Surgical excision","outcome":"Uncomplicated healing, sutures removed on the 7th day after surgery","details":"Surgical excision of the odontoma was done under local anesthesia.\nA full-thickness mucoperiosteal flap was reflected.\nThe layer of bone overlying the calcified mass was removed and the calcified tooth-like structure was excised without disturbing the underlying impacted right maxillary permanent central incisor and was sent for histopathologic examinations.\nThorough curettage was performed in the area and radiographs were taken before the closure of the flap.\nThe area was irrigated with normal saline and the lingual button was bonded onto the labial surface of the impacted tooth and ligature wire was tightly secured to it; the flap was then sutured back in position.\nAfter flap closure, the ligature wire was tightly secured to the arch wire to apply tra
```
**Base Output:**
```
```json
{
  "visit motivation": "Patient presented with a concerning delay in the exfoliation of the upper right deciduous tooth.",
  "admission": {
    "admission_date": "2023-10-27",
    "admission_reason": "Chief complaint of apparent delay of the exfoliation of the upper right deciduous tooth."
  },
  "patient information": {
    "patient_name": "Patient Name",
    "gender": "Female",
    "age": 16,
    "height": "55 cm",
    "weight": "140 kg",
    "eye color": "Blue",
    "teeth": [
      {
        "tooth_number": "1",
        "location": "Right maxillary central incisor (51)",
        "description": "Right maxillary permanent central incisor (11)",
        "location_details": "Left maxillary permanent central incisor (11)",
        "path_of_eruption": "Impeded by radio-opaque tooth-like structure in the apical region of 51 and an impacted permanent right maxillary central incisor 
```
**Fine-Tuned v2 Output:**
```json
{"visit motivation":"Apparent delay of the exfoliation of the upper right deciduous tooth","admission":[],"patient information":{"age":"16","sex":"Female"},"patient medical history":{},"surgeries":[{"reason":"Exfoliation of the upper right deciduous tooth","Type":"Surgical excision of the odontoma","outcome":"Uneventful healing with sutures removed and ligature wire tightly secured","details":"Full-thickness mucoperiosteal flap from the right maxillary permanent canine to the left maxillary permanent canine was reflected.\nA thorough curettage was performed in the area, radiographs taken before closure, and a complete blood investigation was carried out."}],"symptoms":[{"name of symptom":"Delayed exfoliation","location":"Upper right deciduous tooth","time":"Not specified","details":"The clinical history did not reveal any systemic pathology associated with it"}],"medical examinations":[{"name":"Intraoral examination","result":"Presence of retained right maxillary deciduous central incisor (51), absence of the corresponding tooth, i.e., right maxillary permanent central incisor (11) with the contralateral tooth already erupted"},{"name":"Intraoral periapical radiograph","result":"Ra
```

## validation:1351
- **Base:** raw_valid=False, exact_F1=0.000, soft_F1=0.021, toks=178
- **Fine-tuned v2:** raw_valid=False, exact_keys=False, exact_F1=0.000, soft_F1=0.000, toks=2048

**Clinical Note (excerpt):**
```
A 40-year-old Caucasian woman presented to her primary physician with recurrent fevers, chills, wheezing, and cough. She was a welder by profession and had a long history of respiratory symptoms and allergies. She was treated with a course of antibiotics for a presumed pneumonia. When her cough and other symptoms persisted, a chest X-ray was performed and showed a curvilinear abnormality alongside her right heart border consistent with scimitar syndrome (). Upon further review of history, the patient endorsed worsening shortness of breath over the past year and occasional palpitations with exe...
```
**Reference JSON:**
```json
{"visit motivation":"Recurrent fevers, chills, wheezing, and cough","admission":[],"patient information":{"age":"40","sex":"Woman","ethnicity":"Caucasian","occupation":"Welder"},"patient medical history":{"physiological context":"Long history of respiratory symptoms and allergies","allergies":"Asthma/allergy episodes"},"surgeries":[],"symptoms":[{"name of symptom":"Cough","time":"Persistent","details":"Symptoms persisted after a course of antibiotics for presumed pneumonia"},{"name of symptom":"Shortness of breath","intensity of symptom":"Worsening over the past year","time":"Occasional","temporalisation":"With exertion","behaviours affecting the symptom":"Exertion","details":"Denied symptoms with normal activity"},{"name of symptom":"Palpitations","intensity of symptom":"Occasional","time":"With exertion","behaviours affecting the symptom":"Exertion"}],"medical examinations":[{"name":"Physical exam","result":"Normal jugular venous pressure (JVP), parasternal heave, non-localized apex, normal heart sounds, no murmurs"}],"diagnosis tests":[{"test":"Chest X-ray","result":"Curvilinear abnormality alongside right heart border consistent with scimitar syndrome","condition":"Scimitar syn
```
**Base Output:**
```
```json
{
  "visit motivation": "A 40-year-old Caucasian woman presented to her primary physician with recurrent fevers, chills, wheezing, and cough.",
  "admission": "She was a welder by profession and had a long history of respiratory symptoms and allergies.",
  "surgery": "A course of antibiotics for a presumed pneumonia.",
  "symptoms": "Repeated chest X-ray findings showing a curvilinear abnormality alongside right heart border consistent with scimitar syndrome.",
  "medical examinations": "Normal jugular venous pressure (JVP).",
  "diagnosis tests": "A sigmoid murmur.",
  "treatments": "Antibiotics for pneumonia.",
  "discharge": "Chest X-ray showed a curvilinear abnormality alongside right heart border consistent with scimitar syndrome."
}
```
```
**Fine-Tuned v2 Output:**
```json
{"visit motivation":"Recurrent fevers, chills, wheezing, and cough","admission":[],"patient information":{"age":"40","sex":"Woman","ethnicity":"Caucasian"},"patient medical history":{"physiological context":"Long history of respiratory symptoms, allergies, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections, asthma/allergy episodes, recurrent pulmonary infections,
```
