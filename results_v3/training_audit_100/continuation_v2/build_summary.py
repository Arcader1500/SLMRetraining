"""Build descriptive audit sidecars from preserved pilot and completed continuation."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def build(run):
    root = Path(__file__).resolve().parents[3]
    audit = root / 'results_v3/training_audit_100'
    load = lambda path: json.loads(path.read_text(encoding='utf-8'))
    sample = load(audit / 'sample.json')
    pilot = load(audit / 'pilot_adjudications.json')
    old = load(audit / 'judgments/e1a7efa71d6b7cf2/reviews.json')
    new = load(run / 'bulk.json')
    old_ids = {r['case_id'] for r in old}
    assert len(new) == 90 and len({r['case_id'] for r in new}) == 90
    assert {r['case_id'] for r in new} == {s['case_id'] for s in sample} - old_ids
    findings, ledger = [], []
    for row in pilot['adjudications']:
        for f in row['findings']:
            verdict = f['verdict']
            disposition = 'rejected' if verdict == 'rejected' else 'downgraded' if verdict == 'policy_ambiguity' else 'confirmed'
            findings.append(dict(case_id=row['case_id'], group=row['group'], protocol='pilot_v1',
                origin='candidate', index=f['candidate_index'], disposition=disposition,
                classification='policy_ambiguity' if disposition == 'downgraded' else f['original_finding']['classification'],
                category=f['original_finding']['category'], attribution='not_recoded',
                field_path=f['original_finding']['field_path'], source_quote=f['original_finding']['source_quote'],
                label_excerpt=f['original_finding']['label_excerpt'], explanation=f['explanation']))
    by_id = {r['case_id']: r for r in sample}
    new_by_id = {r['case_id']: r for r in new}
    for i, f in enumerate(pilot['additional_findings'], 1):
        findings.append(dict(case_id=f['case_id'], group=by_id[f['case_id']]['group'], protocol='pilot_v1',
            origin='assistant_added', index=i, disposition='confirmed', classification='material_omission',
            category=f['category'], attribution=f['origin'], field_path=f['field_path'],
            source_quote=f['source_quote'], label_excerpt='', explanation=f['explanation']))
    for row in new:
        for d in row['source_review']['candidate_dispositions']:
            f = row['review']['findings'][d['candidate_index'] - 1]
            findings.append(dict(case_id=row['case_id'], group=row['group'], protocol='continuation_v2',
                origin='candidate', index=d['candidate_index'], disposition=d['disposition'],
                classification='policy_ambiguity' if d['disposition'] == 'downgraded' else f['classification'],
                category=f['category'], attribution=d['attribution'], field_path=d['field_path'],
                source_quote=d['source_quote'], label_excerpt=f['label_excerpt'], explanation=d['explanation']))
        for i, f in enumerate(row['source_review']['added_findings'], 1):
            findings.append(dict(case_id=row['case_id'], group=row['group'], protocol='continuation_v2',
                origin='second_pass_added', index=i, disposition=f['disposition'],
                classification='policy_ambiguity' if f['disposition'] == 'downgraded' else f['classification'],
                category=f['category'], attribution=f['attribution'], field_path=f['field_path'],
                source_quote=f['source_quote'], label_excerpt=f['label_excerpt'], explanation=f['explanation']))
    for s in sample:
        fs = [f for f in findings if f['case_id'] == s['case_id']]
        issues = [f for f in fs if f['disposition'] == 'confirmed' and f['classification'] != 'policy_ambiguity']
        ledger.append(dict(case_id=s['case_id'], group=s['group'], selection_reason=s['selection_reason'],
            protocol='pilot_v1' if s['case_id'] in old_ids else 'continuation_v2',
            review_kind='saved assistant source review' if s['case_id'] in old_ids else new_by_id[s['case_id']].get('source_review_reviewer', 'Luna candidate plus separate Luna source pass'),
            diagnostic_issues=len(issues), ambiguity_records=sum(f['classification'] == 'policy_ambiguity' and f['disposition'] != 'rejected' for f in fs),
            rejected_records=sum(f['disposition'] == 'rejected' for f in fs)))
    assert len(ledger) == len({r['case_id'] for r in ledger}) == 100
    pilot_issues = [f for f in findings if f['protocol'] == 'pilot_v1' and f['disposition'] == 'confirmed' and f['classification'] != 'policy_ambiguity']
    assert len(pilot_issues) == 11 and len({f['case_id'] for f in pilot_issues}) == 8
    summary = dict(status='100_case_source_consistency_audit_complete', selected_cases=100,
        pilot_cases=10, continuation_cases=90, continuation_run_id=run.name,
        continuation_review_methods=dict(Counter(r.get('source_review_reviewer', 'Luna CodexJudge source pass') for r in new)),
        interpretation='Descriptive diagnostic findings; protocols and reviewer types differ. No pooled training-set prevalence or clinical validity claim.',
        by_group={})
    for group in ('random', 'targeted'):
        ls = [r for r in ledger if r['group'] == group]
        fs = [f for f in findings if f['group'] == group]
        issues = [f for f in fs if f['disposition'] == 'confirmed' and f['classification'] != 'policy_ambiguity']
        summary['by_group'][group] = dict(cases=len(ls), cases_with_diagnostic_issue=sum(bool(r['diagnostic_issues']) for r in ls),
            diagnostic_findings=len(issues), classifications=dict(Counter(f['classification'] for f in issues)),
            candidate_dispositions=dict(Counter(f['disposition'] for f in fs if f['origin'] == 'candidate')),
            diagnostic_attributions=dict(Counter(f['attribution'] for f in issues)),
            ambiguity_records=sum(r['ambiguity_records'] for r in ls), rejected_records=sum(r['rejected_records'] for r in ls))
    for name, value in [('combined_case_ledger.json', ledger), ('combined_summary.json', summary)]:
        (audit / 'continuation_v2' / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    with (audit / 'continuation_v2/findings.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(findings[0]))
        writer.writeheader()
        writer.writerows(findings)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    build(parser.parse_args().run_dir)
