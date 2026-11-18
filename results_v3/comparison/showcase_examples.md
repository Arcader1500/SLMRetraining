# Side-by-Side Showcase (`gen_rp_1.08`)

## validation:106
- **Base:** raw_valid=False, exact_F1=0.000, soft_F1=0.000, toks=480
- **Fine-tuned v3:** raw_valid=True, exact_keys=False, exact_F1=0.545, soft_F1=0.661, toks=386

**Clinical Note (excerpt):**
```
A 65-year-old white male patient, a chronic smoker, with no prior medical history, was admitted to the emergency department for palpitations and epigastralgia. He stated that he had been experiencing these symptoms for the previous two weeks, but they became more severe and prolonged on the day of admission.
Clinical examination showed a heart rate at 198 bpm, blood pressure was 130/60 mmHg with oxygen saturation was 95% on room air. A per-critical electrocardiogram (EKG) revealed a broad-complex tachycardia consisting with ventricular tachycardia t at a rate of 198 bpm (). Cardiac auscultatio...
```
**Reference JSON:**
```json
{"visit motivation":"palpitations and epigastralgia","admission":[{"reason":"palpitations and epigastralgia becoming more severe and prolonged"}],"patient information":{"age":"65","sex":"male"},"patient medical history":{"physiological context":"chronic smoker, no prior medical history"},"surgeries":[{"Type":"coronary stent implantation"}],"symptoms":[{"name of symptom":"palpitations","time":"previous two weeks"},{"name of symptom":"epigastralgia","time":"previous two weeks"}],"medical examinations":[{"name":"clinical examination","result":"heart rate at 198 bpm, blood pressure was 130/60 mmHg, oxygen saturation was 95% on room air"},{"name":"per-critical electrocardiogram (EKG)","result":"broad-complex tachycardia consistent with ventricular tachycardia at a rate of 198 bpm"},{"name":"EKG after cardioversion","result":"necrotic Q waves in the inferior leads and negative T waves in the lateral leads"},{"name":"transthoracic echocardiography","result":"ischemic heart disease, left ventricular ejection fraction of 50%, akinesia of the basal segments of the anterolateral and inferolateral walls, minimal mitral regurgitation, large cavity (30 × 21 mm in diameter) adjacent to the mitral
```
**Base Output:**
```
```json
{
  "visit motivation": "a chronic smoker",
  "admission": [
    {
      "reason": "existing symptoms",
      "age": 65,
      "sex": "male",
      "physiological context": "chronic smoker"
    },
    {
      "reason": "past two weeks of symptoms",
      "age": 2 weeks,
      "sex": "female",
      "physiological context": "chronic smoker"
    },
    {
      "reason": "became more severe and prolonged on the day of admission",
      "age": 65,
      "sex": "male",
      "physiological context": "chronic smoker"
    },
    {
      "reason": "altered state of consciousness",
      "age": 65,
      "sex": "male",
      "physiological context": "chronic smoker"
    },
    {
      "reason": "external electric shock at 150 J",
      "age": 65,
      "sex": "male",
      "physiological context": "chronic smoker"
    },
    {
      "reason": "immediate restoration of sinus rhythm at 70 b
```
**Fine-Tuned v3 Output:**
```json
{"visit motivation":"Palpitations and epigastralgia","admission":[{"reason":"Occurred on the day of admission"}],"patient information":{"age":"65","sex":"Male"},"patient medical history":{"physiological context":"Chronic smoker"},"surgeries":[],"symptoms":[{"name of symptom":"Palpitations","time":"Previous two weeks"},{"name of symptom":"Epigastralgia","location":"Epidermoid surface, left side of abdomen","details":"Symptoms were prolonged for a few minutes"}],"medical examinations":[{"name":"Clinical examination","result":"Heart rate at 198 bpm, blood pressure was 130/60 mmHg with oxygen saturation was 95% on room air"},{"name":"Per-critical electrocardiogram (EKG)","result":"Broad-complex tachycardia consisting with ventricular tachycardia t at a rate of 198 bpm"},{"name":"Cardiac auscultation","result":"Difficult due to rapid rhythm"},{"name":"Transthoracic echocardiography","result":"Ischemic heart disease, with a left ventricular ejection fraction of 50%, akinesia of the basal segments of the anterolateral and inferolateral walls, and minimal mitral regurgitation"},{"name":"Abdominal view","result":"Large cavity adjacent to the mitral valve communicating with the left ventricl
```

## validation:2438
- **Base:** raw_valid=False, exact_F1=0.087, soft_F1=0.209, toks=1136
- **Fine-tuned v3:** raw_valid=True, exact_keys=False, exact_F1=0.525, soft_F1=0.590, toks=424

**Clinical Note (excerpt):**
```
We present the case of a 51-year-old Caucasian woman with a four-year history of recurrent, right-sided facial pain, in the distribution of all three branches of the trigeminal nerve. These episodes occurred on average two to three times per week and were characterised by brief episodes of unilateral right-sided sharp lancinating pain, lasting on average less than one minute and predominantly affecting the maxillary and mandibular divisions of the trigeminal nerve, although occasionally involving all three branches. Attacks were typically triggered by such actions as washing her face or smilin...
```
**Reference JSON:**
```json
{"visit motivation":"None","admission":[],"patient information":{"age":"51","sex":"Female"},"patient medical history":{"physiological context":"Four-year history of recurrent, right-sided facial pain"},"surgeries":[{"Type":"Decompressive surgery","time":"Nine months after the initial onset of her symptoms"},{"Type":"Radiofrequency ablation","time":"14 months after the decompressive surgery"}],"symptoms":[{"name of symptom":"Facial pain","location":"Right-sided, in the distribution of all three branches of the trigeminal nerve, predominantly affecting the maxillary and mandibular divisions","time":"Episodes occurred on average two to three times per week","details":"No associated headaches or visual disturbance"}],"medical examinations":[{"name":"Neurological and dental examinations","result":"Normal"},{"name":"Computed axial tomography scan of brain and sinuses","result":"Normal"},{"name":"Routine blood tests","result":"Normal"}],"diagnosis tests":[],"treatments":[{"name":"Gabapentin","dosage":"Up to 1200 mg daily","reaction to treatment":"No significant benefit"},{"name":"Carbamazepine","dosage":"Up to 800 mg daily","reaction to treatment":"No significant benefit"},{"name":"Dothie
```
**Base Output:**
```
```json
{
  "visit motivation": "a 51-year-old Caucasian woman with a four-year history of recurrent, right-sided facial pain, in the distribution of all three branches of the trigeminal nerve.",
  "admission": [
    {
      "reason": "acute onset of acute facial pain",
      "dosage": "up to 1200 mg daily",
      "duration": "two to three times per week",
      "details": "brief episodes of unilateral right-sided sharp lancinating pain, lasting on average less than one minute and predominantly affecting the maxillary and mandibular divisions of the trigeminal nerve, although occasionally involving all three branches."
    },
    {
      "reason": "initial treatment with gabapentin (up to 1200 mg daily)",
      "dosage": "up to 800 mg daily",
      "duration": "without significant benefit",
      "details": "carbamazepine (up to 800 mg daily)"
    },
    {
      "reason": "neurosurgical 
```
**Fine-Tuned v3 Output:**
```json
{"visit motivation":"Recurrent, right-sided facial pain","admission":[{"reason":"Recurrent, right-sided facial pain"}],"patient information":{"age":"51","sex":"Female"},"patient medical history":{"physiological context":"Four-year history of recurrent, right-sided facial pain"},"surgeries":[{"Type":"Decompression of right trigeminal nerve","time":"Initially started with gabapentin and later with pregabalin and numesulide","details":"Surgery involved decompression of her right trigeminal nerve nine months after the initial onset of symptoms"},{"Type":"Radiofrequency ablation","time":"14 months after the decompressive surgery","details":"Resulted in some permanent numbness in her right infra-orbital area but no pain relief"}],"symptoms":[{"name of symptom":"Facial pain","location":"Right side","time":"Occurred on average two to three times per week","details":"No associated headaches or visual disturbance"},{"name of symptom":"Pain","location":"Facial region","time":"Occurred on average two to three times per week","details":"No other features associated with these attacks"},{"name of symptom":"Numbness","location":"Right infra-orbital area","time":"At this stage","details":"Not reli
```

## validation:239
- **Base:** raw_valid=False, exact_F1=0.042, soft_F1=0.099, toks=1216
- **Fine-tuned v3:** raw_valid=True, exact_keys=False, exact_F1=0.255, soft_F1=0.454, toks=414

**Clinical Note (excerpt):**
```
In this article, we report a case of a 29-year-old female who presented with worsening complaints of neck stiffness and pain over a period of 2 weeks. The patient recounted that the pain and tightness was only on the right side of her neck, radiating to the back of her head. It was worse with movement and progressed to the point where the pain limited her range of motion, causing her to present to the hospital. Shortly before this, she had been diagnosed with chronic serous otitis media associated with hearing loss, for which she had tympanostomy tubes placed. Following the surgery, she develo...
```
**Reference JSON:**
```json
{"visit motivation":"Worsening complaints of neck stiffness and pain","admission":[{"reason":"Worsening neck stiffness and pain, and chronic serous otitis media with complications"}],"patient information":{"age":"29","sex":"Female"},"patient medical history":{"physiological context":"Chronic serous otitis media associated with hearing loss"},"surgeries":[{"Type":"Tympanostomy tubes placement","time":"Shortly before current presentation"},{"Type":"Right mastoidectomy with right middle ear exploration"}],"symptoms":[{"name of symptom":"Neck stiffness and pain","location":"Right side of neck, radiating to the back of her head","time":"Over a period of 2 weeks","details":"Pain limited her range of motion"},{"name of symptom":"Malodorous drainage from the ear","location":"Ear","time":"Following tympanostomy tube placement surgery","details":"Despite treatment with otic drops"}],"medical examinations":[{"name":"Computed tomography scan","result":"Concerning for acute right mastoiditis, with erosion of the skull and the first cervical vertebra"},{"name":"Magnetic resonance imaging brain and C-spine","result":"Showed mass-like enhancement of the tegmen tympani and reactive dural changes"}]
```
**Base Output:**
```
```json
{
  "visit motivation": "acute right mastoiditis",
  "admission": [
    {
      "reason": "acute right mastoiditis",
      "dosage": "otic drops",
      "time": "2 weeks",
      "details": "severe pain, tightness on right side of neck, worsening with movement and progression to the hospital."
    },
    {
      "reason": "chronic serous otitis media associated with hearing loss",
      "dosage": "tympanostomy tubes",
      "time": "surgery",
      "details": "malodorous drainage from ear, continued up to current presentation."
    }
  ],
  "patient information": {
    "age": "29",
    "sex": "female",
    "medical history": {
      "physiological context": "unremarkable",
      "specific details": "Denied dizziness, headache, vision changes, dysphagia, or other facial pain."
    },
    "surgical history": {
      "type": "surgery",
      "time": "surgery",
      "details": "right
```
**Fine-Tuned v3 Output:**
```json
{"visit motivation":"Worsening complaints of neck stiffness and pain over a period of 2 weeks","admission":[{"reason":"Diagnosed with chronic serous otitis media associated with hearing loss"}],"patient information":{"age":"29","sex":"Female"},"patient medical history":{"physiological context":"Chronic serous otitis media associated with hearing loss, tympanostomy tubes placed"},"surgeries":[{"Type":"Right mastoidectomy with right middle ear exploration","details":"Surgical pathology samples returned positive for histiocyte proliferation in a background of eosinophilic and lymphoplasmacytic inflammation consistent with Langerhans cell histiocytosis (LCH)"}],"symptoms":[{"name of symptom":"Neck stiffness and pain","location":"Neck","time":"Over a period of 2 weeks","details":"Pain and tightness on the right side of her neck, radiating to the back of her head"},{"name of symptom":"Mouth breathing","location":"Mouth","time":"Over a period of 2 weeks","details":"Presented to the hospital after diagnosis"}],"medical examinations":[{"name":"Initial computed tomography scan","result":"Erosion of the skull and the first cervical vertebra"},{"name":"Neurosurgery and ENT (ear, nose, and thro
```

## validation:1990
- **Base:** raw_valid=False, exact_F1=0.000, soft_F1=0.000, toks=1079
- **Fine-tuned v3:** raw_valid=False, exact_keys=False, exact_F1=0.000, soft_F1=0.000, toks=268

**Clinical Note (excerpt):**
```
A 48-year-old female presented with swelling in the frontal region of the skull since 2 years and another swelling in parieto-occipital region since 4 months. Both the swellings over skull have been painless and gradually progressive in size, thus the delay in presentation. No significant past medical history. On examination, swelling in frontal region measured 18 cm in sagital and 13 cm in coronal directions and 7 cm in vertical dimension. The veins over swelling were distended and it was pulsatile in nature, firm in consistency and fixed to skull. The skin over the swelling was stretched but...
```
**Reference JSON:**
```json
{"visit motivation":"Swelling in the frontal and parieto-occipital regions of the skull","admission":[],"patient information":{"age":"48","sex":"Female"},"patient medical history":{"physiological context":"No significant past medical history"},"surgeries":[],"symptoms":[{"name of symptom":"Swelling","location":"Frontal region and parieto-occipital region of the skull","time":"Frontal region since 2 years, parieto-occipital region since 4 months","details":"Painless, swelling in frontal region measured 18 cm in sagital and 13 cm in coronal directions and 7 cm in vertical dimension, veins over swelling were distended, pulsatile, firm in consistency and fixed to skull, skin over the swelling was stretched, left orbit appeared distorted by the swelling but vision was normal, second swelling in parieto-occipital region right side measured 3×4 cm, pulsatile and firm in consistency, thyroid swelling mainly in right lobe around 3×2 cm, firm and not associated with any pressure symptoms"}],"medical examinations":[{"name":"General physical, systemic, and neurological examination","result":"Normal"}],"diagnosis tests":[{"test":"Routine blood tests and thyroid function tests","result":"Normal"
```
**Base Output:**
```
```json
{
  "visit motivation": "Patient presented with swelling in the frontal region of the skull since 2 years and another swelling in parieto-occipital region since 4 months.",
  "admission": [
    {
      "reason": "Swelling in frontal region",
      "details": "18 cm in sagital and 13 cm in coronal directions, 7 cm in vertical dimension."
    },
    {
      "reason": "Swelling in parieto-occipital region right side",
      "details": "3×4 cm pulsatile in nature, firm in consistency, fixed to skull."
    }
  ],
  "patient information": {
    "age": "48",
    "sex": "Female",
    "medical history": {
      "physiological context": "Swelling in frontal region measured 18 cm in sagital and 13 cm in coronal directions and 7 cm in vertical dimension. The veins over swelling were distended and it was pulsatile in nature, firm in consistency and fixed to skull. The skin over the swelling w
```
**Fine-Tuned v3 Output:**
```json
{"visit motivation":"Swelling in the frontal region of the skull","admission":[],"patient information":{"age":"48","sex":"Female"},"patient medical history":{},"surgeries":[],"symptoms":[{"name of symptom":"Swelling","location":"Frontal region of the skull","time":"Since 2 years","details":"Swelling over skull, painless and gradually progressive in size"}],"medical examinations":[{"name":"Physical examination","result":"Swelling in frontal region measuring 18 cm in sagital and 13 cm in coronal directions, distended veins over swelling, pulsatile skin, stretched skin, normal skin, distorted left orbit"},{"name":"Thyroid function test","result":"Normal"},{"name":"Routine blood tests","result":"Normal"},{"name":"Ultrasound study of neck","result":"2 × 1.5 cm neoplastic solid nodule in right lobe of thyroid, firm and not associated with any pressure symptoms"},{"name":"Contrast enhanced computed tomography (CT)","result":"13 × 18 cm size expansile osteolytic lesion in the fronto-parietal region on both right and left sides of anterior half of skull, extending intracranialy, causing compression of underlying fronto-parietal lobes on both sides"},{"name":"Fine needle aspiration cytology 
```
