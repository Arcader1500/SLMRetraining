"""Measure mechanical field loss from v2 to v3; no claim of clinical correctness."""
import csv
import json
import re
from collections import Counter,defaultdict

from scripts.audit_training_data import DATA,OUT,prepare,write,leaves
from scripts.phase_results import ROOT,read_json,digest
from scripts.prepare_v3_dataset import project,SCHEMA


def analyze():
    _,sample=prepare()
    oldroot=ROOT/'prepared_clinical_dataset/eeff5efa1619f198'
    oldrows=[json.loads(s) for s in (oldroot/'train.jsonl').read_text(encoding='utf-8').splitlines()]
    newrows=[json.loads(s) for s in (DATA/'train.jsonl').read_text(encoding='utf-8').splitlines()]
    assert digest(oldrows)==read_json(oldroot/'manifest.json')['split_sha256']['train']
    assert digest(newrows)==read_json(DATA/'manifest.json')['split_sha256']['train']
    old={r['case_id']:r for r in oldrows}
    by_field=defaultdict(list); drops=[]
    for row in newrows:
        previous=old[row['case_id']]
        assert previous['note']==row['note']
        before,after=json.loads(previous['reference']),json.loads(row['reference'])
        assert project(before)==after
        retained=[' '.join(str(v['value']).casefold().split()) for v in leaves(after)]
        for section,entries in before.items():
            entries=entries if isinstance(entries,list) else [entries] if isinstance(entries,dict) else []
            for i,entry in enumerate(entries):
                for key,value in entry.items():
                    if key in SCHEMA[section]: continue
                    normalized=' '.join(str(value).casefold().split())
                    pattern=r'(?<!\w)'+re.escape(normalized)+r'(?!\w)'
                    absent=bool(normalized) and not any(re.search(pattern,text) for text in retained)
                    item=dict(case_id=row['case_id'],section=section,entry_index=i,dropped_key=key,
                              value=value,not_found_verbatim_in_retained_values=absent)
                    drops.append(item);by_field[(section,key)].append(item)
    summary=dict(training_rows=len(newrows),all_v3_labels_match_literal_v2_projection=True,
                 dropped_field_occurrences=len(drops),affected_cases=len({r['case_id'] for r in drops}),
                 not_found_verbatim_occurrences=sum(r['not_found_verbatim_in_retained_values'] for r in drops),
                 fields=[dict(section=k[0],dropped_key=k[1],occurrences=len(v),affected_cases=len({r['case_id'] for r in v}),
                              not_found_verbatim_occurrences=sum(r['not_found_verbatim_in_retained_values'] for r in v)) for k,v in sorted(by_field.items())],
                 limitation='Mechanical field drops and normalized exact-text searches only; some content survives by paraphrase or elsewhere. Old synthetic fields may be unsupported. Counts are not clinical omission rates.')
    write(OUT/'projection_analysis.json',summary)
    selected={r['case_id'] for r in sample}
    write(OUT/'sample_projection_drops.json',[r for r in drops if r['case_id'] in selected])
    with (OUT/'projection_fields.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summary['fields'][0]));writer.writeheader();writer.writerows(summary['fields'])
    print(json.dumps(summary,indent=2))


if __name__=='__main__': analyze()
