"""Resume source-grounded training-label review in an isolated v2 run."""
import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pydantic import BaseModel
from typing import Literal

from scripts.audit_training_data import prepare, resolve_source_quotes, rubric, validate
from scripts.phase_results import digest, read_json
from scripts.run_deepeval import atomic_json, run_lock

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results_v3/training_audit_100/continuation_v2'
PILOT_RUN = ROOT / 'results_v3/training_audit_100/judgments/e1a7efa71d6b7cf2'
CALIBRATION_IDS = ('train:119', 'train:1052', 'train:24', 'train:1453')
APPENDIX = '''CALIBRATION APPENDIX:
- Read the complete note and complete label before deciding an item is absent.
- Ordinary history, including negative history and prior procedures, is valid in physiological context.
- Put personal and family history only in /patient medical history/physiological context; there is no history or family-history leaf under patient information.
- Preserve unusual medication doses when the source states them; this is source consistency, not medical correction.
- Treatment dosage may preserve source-stated dose, route, and frequency; treatment time may preserve duration, sequence, and course timing.
- Diagnosis-test results may preserve the source-stated diagnostic conclusion; symptom details may preserve modifiers and context.
- An emergency-department presentation does not by itself establish inpatient admission.
- Broad normal-examination wording may have scope ambiguity when abnormal measurements are separately represented.
- An extra low-value normal finding alone is not a material omission or clear error.
- A response recorded after combination therapy does not automatically claim independent causation by each drug.
- Distinguish material source-supported omissions from incidental detail; only map omissions to an existing schema path supported by the source.
- If an explanation says the label is source-supported or identifies no discrepancy, do not emit it as a finding.
- Attribute possible findings as projection_loss, inherited, or uncertain; attribution is a reviewer judgment, not a mechanical restoration rule.'''
SECOND_PASS_INSTRUCTION = ('Independently inspect the complete source note and complete label, every candidate claim, and all projection drops. '
                           'Return one disposition for every candidate finding and add any material source-supported omissions missed. '
                           'Use confirmed, downgraded, or rejected; attribute each as projection_loss, inherited, or uncertain. '
                           'Use exact note quotes and valid existing schema paths. Projection drops are leads, not restoration instructions. '
                           'Candidate indices are 1-based: enumerate the first candidate as 1 and include every integer 1 through N exactly once. '
                           'For each candidate, disposition field_path must remain the candidate path; use explanation to justify rejection or downgrade. '
                           'Do not return supported_checks. Added findings must be material and source-grounded, not incidental normal details.')


def append_calibration_policy(base):
    return base + '\n\n' + APPENDIX


class Check(BaseModel):
    field_path: str
    label_excerpt: str
    source_quote: str
    explanation: str


class Finding(Check):
    category: Literal['unsupported_addition', 'wrong_linkage_value', 'chronology', 'negation_uncertainty', 'event_status', 'inappropriate_role', 'omission', 'repetition']
    classification: Literal['clear_error', 'material_omission', 'policy_ambiguity']


class Review(BaseModel):
    decision: Literal['issues_found', 'no_material_issue_found', 'uncertain']
    supported_checks: list[Check]
    findings: list[Finding]
    summary: str


class Disposition(BaseModel):
    candidate_index: int
    disposition: Literal['confirmed', 'downgraded', 'rejected']
    attribution: Literal['projection_loss', 'inherited', 'uncertain']
    explanation: str
    source_quote: str
    field_path: str


class SourceFinding(BaseModel):
    field_path: str
    label_excerpt: str
    source_quote: str
    explanation: str
    category: Literal['unsupported_addition', 'wrong_linkage_value', 'chronology', 'negation_uncertainty', 'event_status', 'inappropriate_role', 'omission', 'repetition']
    classification: Literal['clear_error', 'material_omission', 'policy_ambiguity']
    disposition: Literal['confirmed', 'downgraded', 'rejected']
    attribution: Literal['projection_loss', 'inherited', 'uncertain']


class SourceReview(BaseModel):
    candidate_dispositions: list[Disposition]
    added_findings: list[SourceFinding]
    summary: str


def next_cases(samples, done):
    random_rows = [s for s in samples if s['group'] == 'random']
    targeted_rows = [s for s in samples if s['group'] == 'targeted']
    ordered = [sample for pair in zip(random_rows, targeted_rows) for sample in pair]
    return [sample for sample in ordered if sample['case_id'] not in done]


def validate_source_review(review, sample, candidate=None):
    leaf_paths = {leaf['path'] for leaf in sample['leaves']}
    parents = {'/' + key for key in json.loads(sample['reference'])}
    findings = review['added_findings']
    for row in findings:
        assert row['source_quote'] and row['source_quote'] in sample['note']
        if row['field_path'] in leaf_paths:
            assert row['label_excerpt'] and row['label_excerpt'] in next(
                str(leaf['value']) for leaf in sample['leaves'] if leaf['path'] == row['field_path'])
        else:
            assert row['classification'] == 'material_omission'
            assert row['field_path'] in parents and row['label_excerpt'] == ''
    for row in review['candidate_dispositions']:
        assert row['source_quote'] and row['source_quote'] in sample['note']
        assert row['field_path'] in leaf_paths | parents
    if candidate is not None:
        assert {row['candidate_index'] for row in review['candidate_dispositions']} == set(range(1, len(candidate['findings']) + 1))
        assert len(review['candidate_dispositions']) == len(candidate['findings'])
        for row in review['candidate_dispositions']:
            assert row['field_path'] == candidate['findings'][row['candidate_index'] - 1]['field_path']
    return True


def contract(samples, instruction, source_instruction):
    source_hashes = {s['case_id']: hashlib.sha256((s['note'] + '\0' + s['reference']).encode()).hexdigest() for s in samples}
    schema = {'candidate_review': Review.model_json_schema(), 'source_review': SourceReview.model_json_schema()}
    payload = dict(version='training_label_audit_v2', model='gpt-6-luna', backend='codex exec',
                   selection_sha256=digest(read_json(ROOT/'results_v3/training_audit_100/selection_manifest.json')),
                   instructions=instruction, second_pass_instruction=source_instruction, response_schemas=schema,
                   prompt_sha256=hashlib.sha256(instruction.encode()).hexdigest(), schema_sha256=digest(schema),
                   projection_drops_sha256=digest(read_json(ROOT/'results_v3/training_audit_100/sample_projection_drops.json')),
                   runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), input_sha256=source_hashes,
                   protocol='continuation_v2/PROTOCOL.md',
                   status='calibration_required_before_bulk', concurrency=3,
                   execution_order='alternate random and targeted sample order; exclude the ten v1 pilot reviews')
    payload['run_id'] = digest(payload)[:16]
    return payload


def prompt_for(sample, instruction, candidate=None):
    prompt = (instruction + '\n\nSOURCE NOTE:\n' + sample['note'] + '\n\nTRAINING LABEL:\n' +
              sample['reference'] + '\n\nLABEL LEAF PATHS:\n' + json.dumps(sample['leaves'], ensure_ascii=False))
    if candidate is not None:
        drops = [r for r in read_json(ROOT/'results_v3/training_audit_100/sample_projection_drops.json') if r['case_id'] == sample['case_id']]
        prompt += ('\n\nFIRST-PASS CANDIDATE REVIEW (untrusted candidate claims):\n' + json.dumps(candidate, ensure_ascii=False) +
                   '\n\nV2 PROJECTION DROPS FOR THIS CASE (evidence to inspect, not automatic restoration):\n' + json.dumps(drops, ensure_ascii=False) +
                   '\nFor each disposition include candidate_index, disposition, attribution, exact source_quote, field_path and explanation. '
                   'For added findings provide exact evidence, disposition and attribution.')
    return prompt


def get_judge():
    os.environ['DEEPEVAL_TELEMETRY_OPT_OUT'] = 'YES'
    os.environ['DEEPEVAL_DISABLE_DOTENV'] = '1'
    from scripts.codex_deepeval_judge import CodexJudge
    return CodexJudge('gpt-6-luna', timeout=300)


def validated_call(judge, prompt, schema, sample, kind, candidate=None, raw_path=None, rejected_path=None):
    response = judge.generate(prompt, schema).model_dump()
    raw_path = attempt_path(raw_path) if raw_path else None
    rejected_path = attempt_path(rejected_path) if rejected_path else None
    if raw_path:
        atomic_json(raw_path, dict(initial=response))
    repairs = resolve_source_quotes(response, sample) if kind == 'candidate' else resolve_source_review_quotes(response, sample)
    try:
        if kind == 'candidate':
            validate(response, sample)
        else:
            repairs += resolve_source_review_quotes(response, sample)
            validate_source_review(response, sample, candidate)
    except (AssertionError, KeyError, StopIteration) as exc:
        rejected = dict(response=response, error=str(exc))
        if rejected_path:
            atomic_json(rejected_path, rejected)
        retry_prompt = prompt + '\n\nYour prior response failed exact evidence validation (' + str(exc) + '). Correct it using only the supplied strings; return the complete response.'
        response = judge.generate(retry_prompt, schema).model_dump()
        if raw_path:
            atomic_json(raw_path, dict(initial=rejected['response'], retry=response))
        repairs += resolve_source_quotes(response, sample) if kind == 'candidate' else []
        if kind == 'candidate':
            validate(response, sample)
        else:
            repairs += resolve_source_review_quotes(response, sample)
            validate_source_review(response, sample, candidate)
        return dict(response=response, repairs=repairs, rejected=rejected, retry_prompt=retry_prompt)
    return dict(response=response, repairs=repairs)


def attempt_path(path):
    if not path.exists():
        return path
    index = 2
    while path.with_name(path.stem + f'_attempt{index}' + path.suffix).exists():
        index += 1
    return path.with_name(path.stem + f'_attempt{index}' + path.suffix)


def resolve_source_review_quotes(review, sample):
    temporary = {'supported_checks': review['candidate_dispositions'], 'findings': review['added_findings']}
    return resolve_source_quotes(temporary, sample)


def source_review_instruction(candidate_instruction):
    policy = candidate_instruction.split('\n\nANNOTATION POLICY:\n', 1)[1]
    return SECOND_PASS_INSTRUCTION + '\n\nCALIBRATION APPENDIX:\n' + APPENDIX.split('CALIBRATION APPENDIX:\n', 1)[1] + '\n\nANNOTATION POLICY:\n' + policy


def source_prompt_for(sample, instruction, candidate):
    drops = [r for r in read_json(ROOT/'results_v3/training_audit_100/sample_projection_drops.json') if r['case_id'] == sample['case_id']]
    return (instruction + '\n\nSOURCE NOTE:\n' + sample['note'] + '\n\nCOMPLETE TRAINING LABEL:\n' + sample['reference'] +
            '\n\nLABEL LEAF PATHS:\n' + json.dumps(sample['leaves'], ensure_ascii=False) +
            '\n\nFIRST-PASS CANDIDATE FINDINGS (claims to independently check):\n' + json.dumps(candidate, ensure_ascii=False) +
            '\n\nV2 PROJECTION DROPS FOR THIS CASE (leads, never automatic restoration):\n' + json.dumps(drops, ensure_ascii=False))


def run(phase, limit=None, concurrency=3):
    selection, samples = prepare()
    base_instruction = rubric()
    instruction = append_calibration_policy(base_instruction)
    source_instruction = source_review_instruction(instruction)
    contract_data = contract(samples, instruction, source_instruction)
    out = OUT / contract_data['run_id']
    out.mkdir(parents=True, exist_ok=True)
    if (out/'run_contract.json').exists():
        assert read_json(out/'run_contract.json') == contract_data
    else:
        atomic_json(out/'run_contract.json', contract_data)
    sample_by_id = {s['case_id']: s for s in samples}
    phase_path = out / (phase + '.json')
    with run_lock(out):
        records = read_json(phase_path) if phase_path.exists() else []
        candidate_checkpoint = out / (phase + '.candidate_checkpoint.json')
        candidates = read_json(candidate_checkpoint) if candidate_checkpoint.exists() else []
        for entry in candidates:
            if not any(row['case_id'] == entry['case_id'] for row in records):
                records.append(entry)
        allowed = set(CALIBRATION_IDS) if phase == 'calibration' else {s['case_id'] for s in samples}
        ids = [r.get('case_id') for r in records]
        if len(ids) != len(set(ids)) or not set(ids) <= allowed:
            raise ValueError(f'Malformed or duplicate {phase} checkpoint')
        for entry in records:
            sample = sample_by_id[entry['case_id']]
            Review.model_validate(entry['review'])
            validate(entry['review'], sample)
            if 'source_review' in entry:
                SourceReview.model_validate(entry['source_review'])
                resolve_source_review_quotes(entry['source_review'], sample)
                validate_source_review(entry['source_review'], sample, entry['review'])
        done = {r['case_id'] for r in records if 'source_review' in r}
        if phase == 'calibration':
            pending = [sample_by_id[x] for x in CALIBRATION_IDS if x not in done]
        else:
            if not (out/'calibration.json').exists() or len(read_json(out/'calibration.json')) != len(CALIBRATION_IDS):
                raise RuntimeError('Calibration must complete and receive parent examination before --phase bulk.')
            pending = next_cases(samples, done | {s['case_id'] for s in samples if s['case_id'] in CALIBRATION_IDS or s['case_id'] in {r['case_id'] for r in read_json(PILOT_RUN/'reviews.json')}})
        if limit is not None:
            pending = pending[:limit]
        judge = get_judge()
        errors = []
        for offset in range(0, len(pending), concurrency):
            batch = pending[offset:offset+concurrency]
            cached = {row['case_id']: row for row in records}
            candidate_futures = {}
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                for sample in batch:
                    if sample['case_id'] not in cached:
                        stem = sample['case_id'].replace(':', '_')
                        candidate_futures[pool.submit(validated_call, judge, prompt_for(sample, instruction), Review,
                            sample, 'candidate', None, out/(stem+'_candidate_raw.json'), out/(stem+'_candidate_rejected.json'))] = sample
                for future in as_completed(candidate_futures):
                    sample = candidate_futures[future]
                    try:
                        entry = next((r for r in records if r['case_id'] == sample['case_id']), None)
                        if entry is None:
                            candidate = future.result()
                            entry = dict(case_id=sample['case_id'], group=sample['group'], review=candidate['response'], evidence_span_repairs=candidate['repairs'])
                            records = [r for r in records if r['case_id'] != sample['case_id']] + [entry]
                            atomic_json(candidate_checkpoint, records)
                    except Exception as exc:
                        errors.append(dict(case_id=sample['case_id'], error=type(exc).__name__, detail=str(exc)))
            source_futures = {}
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                for sample in batch:
                    entry = next((r for r in records if r['case_id'] == sample['case_id']), None)
                    if entry is None or 'source_review' in entry:
                        continue
                    stem = sample['case_id'].replace(':', '_')
                    source_futures[pool.submit(validated_call, judge, source_prompt_for(sample, source_instruction, entry['review']),
                        SourceReview, sample, 'source', entry['review'], out/(stem+'_source_raw.json'),
                        out/(stem+'_source_rejected.json'))] = sample
                for future in as_completed(source_futures):
                    sample = source_futures[future]
                    try:
                        entry = next(r for r in records if r['case_id'] == sample['case_id'])
                        source_result = future.result()
                        entry['source_review'] = source_result['response']
                        entry['source_evidence_span_repairs'] = source_result['repairs']
                        records = [r for r in records if r['case_id'] != sample['case_id']] + [entry]
                        atomic_json(phase_path, records)
                    except Exception as exc:
                        errors.append(dict(case_id=sample['case_id'], error=type(exc).__name__, detail=str(exc)))
            atomic_json(out/(phase+'_errors.json'), errors)
            completed = sum('source_review' in r for r in records)
            expected = len(CALIBRATION_IDS) if phase == 'calibration' else 90
            atomic_json(out/(phase+'_progress.json'), dict(phase=phase, expected=expected, completed=completed,
                candidate_checkpointed=sum('source_review' not in r for r in records), remaining=max(0, expected-completed), errors=len(errors)))
            print(f'{phase}: checkpointed {len(records)} cases; remaining {len(pending)-offset-len(batch)}', flush=True)
        if errors:
            raise RuntimeError(f'{len(errors)} review(s) incomplete; see {out/(phase + "_errors.json")} and resume the phase')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['calibration', 'bulk'], required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--concurrency', choices=[1, 2, 3], type=int, default=3)
    args = parser.parse_args()
    print(run(args.phase, args.limit, args.concurrency))
