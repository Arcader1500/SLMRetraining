"""Verify a completed source-rubric run against its frozen inputs and old run."""
import argparse
import hashlib
import math
from collections import Counter
from pathlib import Path

from scripts.phase_results import ROOT, digest, read_json
from scripts.source_grounded_rubric import METRIC_STEPS, VERSION


def check(directory):
    directory = Path(directory)
    contract = read_json(directory / 'run_contract.json')
    provenance = read_json(directory / 'execution_provenance.json')
    summary = read_json(directory / 'summary.json')
    scores = read_json(directory / 'scores.json')
    frozen = ROOT / 'results_v3/deepeval_20'
    selection = read_json(frozen / 'selection_manifest.json')
    pairs = read_json(frozen / 'paired_cases.json')
    assert contract['rubric_version'] == summary['rubric_version'] == VERSION
    assert contract['metric_steps'] == METRIC_STEPS
    assert contract['evaluation_params'] == ['input', 'actual_output', 'expected_output']
    assert directory.name == digest(contract)[:16]
    assert contract['selection_sha256'] == digest(selection)
    assert contract['pairs_sha256'] == selection['pairs_sha256'] == digest(pairs)
    assert [p['case_id'] for p in pairs] == selection['case_ids']
    for path, expected in {**selection['source_sha256'], **provenance['source_sha256']}.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    old = frozen / 'judgments/a6bb10a9fde5e2b4'
    assert hashlib.sha256((old / 'scores.json').read_bytes()).hexdigest() == read_json(old / 'completion_checks.json')['scores_sha256']
    assert not read_json(frozen / 'judge_settings.json')['judges']['gemini']['enabled']
    expected = {(p['case_id'], m, metric) for p in pairs for m in ['baseline', 'finetuned'] for metric in METRIC_STEPS}
    keyed = {(r['case_id'],r['model'],r['metric']):r for r in scores}
    assert len(scores) == len(keyed) == 80 and set(keyed) == expected
    by_id = {p['case_id']:p for p in pairs}
    for row in scores:
        assert math.isfinite(row['score']) and 0 <= row['score'] <= 1
        assert row['reason'].strip()
        assert row['format_metrics'] == by_id[row['case_id']]['format_metrics'][row['model']]
    outcomes = {}
    for metric in METRIC_STEPS:
        for model in ['baseline','finetuned']:
            mean = sum(keyed[(p['case_id'],model,metric)]['score'] for p in pairs)/20
            assert math.isclose(mean,summary['mean_scores'][metric][model],abs_tol=1e-12)
        deltas = [keyed[(p['case_id'],'finetuned',metric)]['score']-keyed[(p['case_id'],'baseline',metric)]['score'] for p in pairs]
        assert math.isclose(sum(deltas)/20,summary['mean_paired_deltas'][metric],abs_tol=1e-12)
        outcomes[metric] = dict(Counter('finetuned_higher' if d>0 else 'baseline_higher' if d<0 else 'equal' for d in deltas))
    assert summary['complete'] and summary['measurements']==80
    result = dict(complete=True,rubric_version=VERSION,model=contract['model'],cases=20,
                  paired_outputs=40,metric_measurements=80,unique_records=80,
                  means_and_paired_deltas_verified=True,frozen_inputs_unchanged=True,
                  old_scores_unchanged=True,note_in_evaluation_params=True,
                  gemini_enabled=False,paired_outcomes=outcomes,
                  scores_sha256=hashlib.sha256((directory/'scores.json').read_bytes()).hexdigest(),
                  limitation='Rubric-based LLM assessment, not clinician calibration or an exhaustive claim inventory; reasons require review.')
    import json
    (directory / 'completion_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    check(parser.parse_args().directory)
