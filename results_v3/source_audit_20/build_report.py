"""Validate the manual audit and export evidence without modifying frozen inputs."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def csv_file(name, rows):
    with (HERE / name).open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def build():
    paired_path = REPO / 'results_v3/deepeval_20/paired_cases.json'
    pairs = read(paired_path)
    manifest = read(paired_path.with_name('selection_manifest.json'))
    digest = hashlib.sha256(json.dumps(pairs, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert digest == manifest['pairs_sha256'], 'Frozen pairs changed'
    for path, expected in manifest['source_sha256'].items():
        assert sha(REPO / path) == expected, f'Frozen source changed: {path}'
    annotations = read(HERE / 'reviewed_annotations.json')
    index = {c['case_id']: c for c in read(HERE / 'indexed_inputs.json')}
    judges = read(REPO / 'results_v3/deepeval_20/judgments/a6bb10a9fde5e2b4/scores.json')
    assert len(judges) == len({(r['case_id'],r['model'],r['metric']) for r in judges}) == 80
    ids = [c['case_id'] for c in pairs]
    assert [c['case_id'] for c in annotations] == ids == manifest['case_ids']
    by_id = {c['case_id']: c for c in pairs}
    probes, findings, concerns, cases = [], [], [], []
    for c in annotations:
        cid = c['case_id']
        raw = by_id[cid]
        assert index[cid]['note'] == raw['input']
        assert len(c['probes']) == 8
        leaves = {m:{r['id']:r for r in v['leaves']} for m,v in index[cid]['models'].items()}
        def quote(text):
            assert text and text in raw['input'], (cid, text)
            return dict(text=text, start=raw['input'].index(text), end=raw['input'].index(text)+len(text))
        def evidence(text, model):
            source = raw[{'baseline':'baseline_output','finetuned':'finetuned_output','reference':'expected_output'}[model]]
            if text.startswith('@'):
                assert text[1:] in source, (cid,model,text)
                return [dict(raw_excerpt=text[1:])]
            rows = [leaves[model][token] for token in text.split()]
            assert rows
            return rows
        checked = dict(case_id=cid, source_note_sha256=hashlib.sha256(raw['input'].encode()).hexdigest(),
                       probes=[], findings=[], reference_review=[], judge_review=[],
                       judge_reasons=[r for r in judges if r['case_id']==cid])
        # Full judge format_metrics contain copies of raw outputs; store concise reasons.
        checked['judge_reasons'] = [{k:r[k] for k in ['model','metric','score','reason']} for r in checked['judge_reasons']]
        for n,(field,description,q,b,f) in enumerate(c['probes'],1):
            item = dict(probe_id=f'{cid}:P{n:02}',field=field,description=description,source=quote(q),outcomes={})
            for model,value in [('baseline',b),('finetuned',f)]:
                status = value.split(':',1)[0]
                assert status in {'S','P','C','X','O','A'}
                refs = [] if status=='O' else evidence(value.split(':',1)[1], model)
                item['outcomes'][model] = dict(status=status,evidence=refs)
                probes.append(dict(case_id=cid,probe_id=item['probe_id'],group='demographic' if field in {'age','sex'} else 'clinical',
                                   field=field,fact=description,source_quote=q,model=model,status=status,
                                   evidence=value,evidence_detail=json.dumps(refs,ensure_ascii=False)))
            checked['probes'].append(item)
        for n,(model,category,ev,q,explanation) in enumerate(c['findings'],1):
            refs=evidence(ev,model)
            item=dict(finding_id=f'{cid}:M{n:02}',model=model,category=category,evidence=refs,source=quote(q),explanation=explanation)
            checked['findings'].append(item)
            findings.append(dict(case_id=cid,finding_id=item['finding_id'],model=model,category=category,source_quote=q,
                                 evidence=ev,evidence_detail=json.dumps(refs,ensure_ascii=False),explanation=explanation))
        for kind in ['reference_review','judge_review']:
            for row in c[kind]:
                category = row[0]
                q,explanation = row[-2:]
                item=dict(category=category,source=quote(q),explanation=explanation)
                classification = ''
                if kind=='reference_review':
                    classification = ('clear_discrepancy' if category in {'timing_loss','linkage','causal_certainty'} else
                                      'omission' if category in {'omission','reference_omission'} else
                                      'annotation_policy' if category=='entity_assignment' else 'temporal_or_causal_ambiguity')
                    item['classification']=classification
                if kind=='reference_review': item['evidence']=evidence(row[1],'reference')
                checked[kind].append(item)
                concerns.append(dict(case_id=cid,kind=kind,category=category,classification=classification,source_quote=q,explanation=explanation))
        cases.append(checked)
    def counts(rows, keys):
        groups=defaultdict(list)
        for r in rows: groups[tuple(r[k] for k in keys)].append(r)
        return [dict(zip(keys,k),rows=len(v),affected_cases=len({r['case_id'] for r in v})) for k,v in sorted(groups.items())]
    summary=dict(cases=len(cases),unique_probes=len(probes)//2,model_probe_outcomes=len(probes),
                 probe_outcomes=counts(probes,['group','model','status']),by_field=counts(probes,['field','model','status']),
                 findings=len(findings),findings_by_category=counts(findings,['model','category']),
                 reference_concerns=counts([r for r in concerns if r['kind']=='reference_review'],['category']),
                 reference_classifications=counts([r for r in concerns if r['kind']=='reference_review'],['classification']),
                 judge_concerns=counts([r for r in concerns if r['kind']=='judge_review'],['category']))
    policy = ('Assistant source-consistency audit, not clinician adjudication. Eight selected diagnostic probes per case; '
              'not exhaustive source or output claim inventories and not precision/recall. Demographics separated from clinical content. '
              'S=unambiguous supported fact, including explicitly identified events in history/discharge or neutral prose; '
              'P=readable fact with inappropriate clinical role (e.g. finding as surgery, outcome as treatment reaction); '
              'C=wrong value/entity/event/time/negation relation without a correct version of that same probed relation; '
              'X=correct and incompatible versions of the probed fact coexist; O=probed fact absent from all readable raw text; '
              'A=partial or ambiguous evidence. Synonymous headings, nested history and surgery/test dual use alone are not semantic errors. '
              'Probe labels concern the named subclaim, not all adjacent details; findings capture independent errors. '
              'Read malformed prefixes and arrays without repairing predictions or changing existing format scores. '
              'Absence of a reference/judge concern is not certification. Categories are diagnostic primary labels, not severity scores. '
              'Reference timing/causal/policy concerns and judge policy sensitivity are not all confirmed errors.')
    save('audit.json',dict(status='complete_assistant_source_consistency_review',policy=policy,summary=summary,cases=cases))
    save('summary.json',summary)
    csv_file('probes.csv',probes)
    csv_file('findings.csv',findings)
    csv_file('reference_and_judge_concerns.csv',concerns)
    csv_file('field_outcomes.csv',summary['by_field'])
    lines=['# Evidence ledger: all 20 cases','',policy,'',
           'Evidence IDs resolve to `indexed_inputs.json`; complete resolved evidence and exact quote offsets are in `audit.json`. '
           'Original raw outputs are in `../deepeval_20/paired_cases.json`. See `REPORT.md` for interpretation.','']
    def cell(text): return str(text).replace('|','\\|').replace('\n','<br>')
    for c in annotations:
        lines += [f"## {c['case_id']}",'','| Field / probe | Source quote | Baseline | Fine-tuned |','| --- | --- | --- | --- |']
        for field,description,q,b,f in c['probes']: lines.append('| '+' | '.join(map(cell,[field+': '+description,q,b,f]))+' |')
        for key in ['findings','reference_review','judge_review']:
            lines += ['',f'### {key.replace("_"," ").title()}','']
            for row in c[key]:
                if key=='findings': model,category,ev,q,explanation=row; label=f'{model} / {category} / {ev}'
                elif key=='reference_review': category,ev,q,explanation=row; label=f'{category} / {ev}'
                else: category,q,explanation=row; label=category
                lines += [f'- **{label}**: {explanation} Source: “{q}”']
            if not c[key]: lines += ['No additional concern recorded; this is not an exhaustive certification.']
        lines += ['']
    (HERE/'CASE_LEDGER.md').write_text('\n'.join(lines),encoding='utf-8')
    checks = dict(status='passed',cases=20,probes=160,paired_outcomes=320,
                  all_source_quotes_exact=True,all_evidence_ids_and_raw_excerpts_resolved=True,
                  indexed_notes_match_frozen_notes=True,pairs_hash_matches_manifest=True,
                  frozen_source_files_verified=len(manifest['source_sha256']),saved_judgments=80,
                  semantic_review='All 20 manually inspected against supplied notes/raw outputs; reconciliation_log.json records draft corrections. Not independent clinical adjudication.',
                  input_sha256={str(p.relative_to(REPO)).replace('\\','/'):sha(p) for p in [paired_path,HERE/'annotations.json',HERE/'indexed_inputs.json',HERE/'reviewed_annotations.json']},
                  new_inference_calls=0,new_training_runs=0)
    save('validation_checks.json',checks)
    save('progress.json',dict(status='complete_assistant_source_consistency_review',reviewed_cases=20,total_cases=20,
                             probe_count=160,finding_count=len(findings),remaining_ids=[],
                             semantic_annotation_validation=checks['semantic_review'],new_judge_calls=0,new_training_runs=0))
    print(f"Validated {len(cases)} cases, {len(probes)//2} paired probes, {len(findings)} findings; all frozen hashes and evidence checks passed.")

if __name__=='__main__':
    build()
