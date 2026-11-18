"""Read-only checkpoint verification for the resumable remaining-80 evaluation."""
import hashlib
import json
import math

from scripts.phase_results import digest, read_json, ROOT
from scripts.prepare_deepeval import REMAINING_OUTPUT, DEFAULT_OUTPUT, prepare_remaining
from scripts.source_grounded_rubric import METRIC_STEPS, VERSION


def check():
    manifest,pairs=prepare_remaining()
    progress=read_json(REMAINING_OUTPUT/'progress.json')
    out=REMAINING_OUTPUT/'judgments'/progress['run_id']
    contract=read_json(out/'run_contract.json')
    scores=read_json(out/'scores.json')
    expected={(p['case_id'],m,metric) for p in pairs for m in ('baseline','finetuned') for metric in METRIC_STEPS}
    keyed={(r['case_id'],r['model'],r['metric']):r for r in scores}
    assert len(keyed)==len(scores) and set(keyed)<=expected
    assert len(expected)==320
    assert contract['model']=='gpt-6-luna' and contract['rubric_version']==VERSION
    assert contract['metric_steps']==METRIC_STEPS and contract['evaluation_params']==['input','actual_output','expected_output']
    assert contract['pairs_sha256']==digest(pairs)==manifest['pairs_sha256']
    assert contract['selection_sha256']==digest(manifest) and digest(contract)[:16]==out.name
    by_id={p['case_id']:p for p in pairs}
    for r in scores:
        assert math.isfinite(r['score']) and 0<=r['score']<=1 and r['reason'].strip()
        assert r['format_metrics']==by_id[r['case_id']]['format_metrics'][r['model']]
    for path,expected_hash in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected_hash,path
    oldpath=DEFAULT_OUTPUT/'judgments'/manifest['previous_run_id']/'scores.json'
    assert hashlib.sha256(oldpath.read_bytes()).hexdigest()==manifest['previous_scores_sha256']
    assert not read_json(REMAINING_OUTPUT/'judge_settings.json')['judges']['gemini']['enabled']
    # A running writer can advance after progress is read; scores are authoritative.
    assert progress['saved_measurements']<=len(scores)
    if len(scores)==320 and (out/'summary.json').exists():
        summary=read_json(out/'summary.json')
        for metric in METRIC_STEPS:
            for model in ('baseline','finetuned'):
                mean=sum(r['score'] for r in scores if r['metric']==metric and r['model']==model)/80
                assert math.isclose(mean,summary['mean_scores'][metric][model],abs_tol=1e-12)
        if (out/'combined_scores_100.json').exists():
            combined=read_json(out/'combined_scores_100.json')
            assert combined[:80]==read_json(oldpath) and combined[80:]==scores and len(combined)==400
    result=dict(status='checkpoint_verified',run_id=out.name,saved_measurements=len(scores),
                remaining_measurements=320-len(scores),overall_source_measurements=80+len(scores),
                original_twenty_scores_unchanged=True,frozen_inputs_and_rubric_verified=True,
                unique_score_keys=True,gemini_enabled=False,complete=len(scores)==320)
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__': check()
