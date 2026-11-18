"""Assistant source review of the ten-case pilot; preserve all judge flags."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'judgments/e1a7efa71d6b7cf2'
samples={r['case_id']:r for r in json.loads((ROOT/'sample.json').read_text(encoding='utf-8'))}
reviews=json.loads((RUN/'reviews.json').read_text(encoding='utf-8'))
assert len(reviews)==10
decisions={
 'train:983':[
  ('confirmed_omission','The explicit 4 kg weight-loss amount is absent. Current weight is not required as a separate demographic schema field; the confirmed issue is the lost weight-loss magnitude.'),
  ('policy_ambiguity','Exudative effusion is preserved. Whether no further differentiation warrants inclusion is an optional-detail/coverage decision, not a demonstrated false label.')],
 'train:119':[
  ('rejected','The 20g methotrexate dose is explicitly source-stated. Source consistency does not authorize medical correction; the judge itself says there is no discrepancy.')],
 'train:1239':[
  ('policy_ambiguity','Culture identification immediately precedes admission for workup. Causal admission wording is inferred but plausible; downgrade from clear error.'),
  ('policy_ambiguity','Persistent fever occurred during postoperative IV antibiotics and irrigation. The response field needs contextual qualification; it does not explicitly claim ciprofloxacin alone caused fever.'),
  ('confirmed_omission','Every-12-hours ciprofloxacin frequency is source-stated and absent from retained dosage/time fields.')],
 'train:1045':[],
 'train:1052':[
  ('rejected','The canonical patient medical history.physiological context field intentionally holds broad history. No previous facial trauma is valid history here.'),
  ('rejected','Nonpalpable regional lymph nodes is explicitly present in source and label. The judge explanation and summary contradict its clear-error classification.')],
 'train:1453':[
  ('policy_ambiguity','Both drugs were part of chemotherapy. Listing a shared remission under both is ambiguous about combination response, not proof of unsupported single-drug causation.'),
  ('policy_ambiguity','Same shared-regimen attribution concern; this is not a second confirmed drug error.')],
 'train:24':[
  ('confirmed_event_status','Under the explicit-admission policy, ED presentation alone does not establish inpatient admission. This is unsupported event-role labeling, not proof the patient was never admitted.'),
  ('confirmed_omission','Pleuritic/positional aggravating and relieving factors are explicitly stated and absent from the symptom details.'),
  ('rejected','Shared onset while lying in bed is already partially preserved. Treat residual chest-pain detail under the confirmed modifier omission, not a separate allocation defect.'),
  ('rejected','The prothrombin mutation is explicitly retained in history. The judge itself calls this supported and says its own finding is not a discrepancy.')],
 'train:1108':[
  ('policy_ambiguity','Broad normal physical examination can be read as otherwise normal because abnormal BP is separately explicit. Qualify scope; do not count as a definite contradiction.')],
 'train:177':[
  ('confirmed_omission','Ectopic pancreas and uninvolved margins are explicit before the cutoff. The final diagnosis and margin status are missing from retained pathology result.')],
 'train:676':[
  ('confirmed_omission','Angiography explicitly confirms AEF; the retained result gives measurements without the confirmed diagnosis.')],
}
adjudications=[]
for row in reviews:
    cid=row['case_id']; findings=row['review']['findings']; verdicts=decisions[cid]
    assert len(findings)==len(verdicts)
    adjudications.append(dict(case_id=cid,group=row['group'],reviewer='assistant source-consistency review, not clinician adjudication',
                             findings=[dict(candidate_index=i,verdict=v,explanation=e,original_finding=f) for i,(f,(v,e)) in enumerate(zip(findings,verdicts),1)]))

additional=[]
def add(cid,path,quote,explanation,origin):
    assert quote in samples[cid]['note']
    additional.append(dict(case_id=cid,field_path=path,source_quote=quote,category='omission',
                           verdict='confirmed_omission',explanation=explanation,origin=origin))

add('train:119','/treatments','methylprednisolone 500 mg IV for 3 days, tablet prednisone 25mg BD, tablet aspirin 75 mg OD, tablet methotrexate 20g weekly, capsule gabapentin 75 mg BD, tablet folic acid 5 mg OD, and tablet atorvastatin 20 mg HS',
    'Seven medication frequencies and the methylprednisolone route/duration are absent. Existing dosage/time strings can retain them without adding schema paths. This is one bundled regimen-coverage finding, not seven independent error counts.','v2 treatments.frequency dropped by projection')
add('train:1052','/treatments','Postoperatively, the patient received systemic antibiotic, analgesic, and mouthwash for 7 days.',
    'Explicit seven-day postoperative treatment duration is absent.','v2 treatments.duration dropped by projection')
add('train:1052','/diagnosis tests','sufficiently supportive of the working diagnosis of peripheral osteoma',
    'Imaging features survive but the source-qualified working diagnosis is absent. Retain working status rather than turning it into a definitive diagnosis.','v2 diagnosis tests.condition dropped by projection')
add('train:1453','/treatments','S-1 50 mg, twice daily for 3 consecutive weeks, followed by a 2-week rest period',
    'S-1 frequency and cycle schedule are absent despite the retained starting date and dose.','v2 treatments.frequency dropped by projection')
add('train:1453','/treatments','He continued to take S-1 and the other drugs for about 1 week from the start of the renal insufficiency.',
    'Continuation of medication after renal insufficiency is an explicit material treatment timeline absent from the retained label.','v2 treatments.details dropped by projection')

counts=Counter(f['verdict'] for r in adjudications for f in r['findings'])
confirmed=[dict(case_id=r['case_id'],**f) for r in adjudications for f in r['findings'] if f['verdict'].startswith('confirmed')]
summary=dict(assistant_reviewed_cases=10,random_cases=5,targeted_cases=5,model_candidate_findings=sum(counts.values()),
             candidate_verdicts=dict(counts),additional_assistant_findings=len(additional),
             confirmed_diagnostic_findings=len(confirmed)+len(additional),
             cases_with_confirmed_issue=len({f['case_id'] for f in confirmed+additional}),
             remaining_semantic_review_cases=90,
             limitation='Selected initial pilot, not a prevalence estimate or exhaustive claim inventory; candidate findings are not confirmed without source review.')
payload=dict(status='initial_ten_case_pilot_review_complete',run_id=RUN.name,summary=summary,adjudications=adjudications,additional_findings=additional)
(ROOT/'pilot_adjudications.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
rows=[dict(case_id=r['case_id'],candidate_index=f['candidate_index'],verdict=f['verdict'],field_path=f['original_finding']['field_path'],source_quote=f['original_finding']['source_quote'],label_excerpt=f['original_finding']['label_excerpt'],explanation=f['explanation']) for r in adjudications for f in r['findings']]
rows += [dict(case_id=f['case_id'],candidate_index='assistant_added',verdict=f['verdict'],field_path=f['field_path'],source_quote=f['source_quote'],label_excerpt='',explanation=f['explanation']) for f in additional]
with (ROOT/'pilot_review.csv').open('w',newline='',encoding='utf-8-sig') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps(summary,indent=2))
