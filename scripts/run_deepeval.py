"""Explicit opt-in judge execution; sequential, checkpointed, same 20 paired cases."""
import argparse
import csv
import importlib.metadata
import json
import math
import os
import hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from scripts.phase_results import digest, read_json
from scripts.prepare_deepeval import DEFAULT_OUTPUT, REMAINING_OUTPUT, METRIC_STEPS, prepare, prepare_remaining


def atomic_json(path, value):
    pending = path.with_suffix('.pending')
    with pending.open('w',encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    pending.replace(path)


@contextmanager
def run_lock(directory):
    """OS lock releases on interruption/crash; a stale filename never blocks resume."""
    with (directory/'run.lock').open('a+b') as handle:
        if handle.tell()==0:
            handle.write(b'0');handle.flush()
        handle.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            raise RuntimeError('Another evaluator is writing this run; do not start a second writer.') from None
        try:
            yield
        finally:
            handle.seek(0)
            if os.name=='nt': msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
            else: fcntl.flock(handle,fcntl.LOCK_UN)


def save_progress(out, pairs, records, metric_names, status, remaining_validation, current=None, failure=None):
    keys={(r['case_id'],r['model'],r['metric']) for r in records}
    pending=[dict(case_id=p['case_id'],model=model,metric=metric) for p in pairs
             for model in ('baseline','finetuned') for metric in metric_names
             if (p['case_id'],model,metric) not in keys]
    per_case={p['case_id']:sum(r['case_id']==p['case_id'] for r in records) for p in pairs}
    progress=dict(status=status,updated_at_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),run_id=out.name,
                  selected_cases=len(pairs),expected_measurements=len(pairs)*2*len(metric_names),
                  saved_measurements=len(records),remaining_measurements=len(pending),
                  complete_cases=sum(v==2*len(metric_names) for v in per_case.values()),per_case_saved=per_case,
                  current_judgment=current,pending_judgments=pending,
                  resume_command=('.venv/deepeval-tools/Scripts/python.exe -u -m scripts.run_deepeval --remaining-validation --source-grounded --run --backend codex'
                                  if remaining_validation else None),failure_kind=failure,
                  restart_note='Completed scores are skipped. Only a judgment interrupted before its checkpoint may be repeated.')
    if remaining_validation:
        progress.update(previous_measurements=80,overall_saved_measurements=80+len(records),overall_expected_measurements=400)
    atomic_json(out/'progress.json',progress)
    atomic_json(out.parent.parent/'progress.json',progress)


def create_metrics(judge, source_grounded=False):
    from deepeval.metrics import GEval
    from deepeval.test_case import SingleTurnParams
    steps_by_metric = METRIC_STEPS
    params = [SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT]
    if source_grounded:
        from scripts.source_grounded_rubric import METRIC_STEPS as source_steps
        steps_by_metric = source_steps
        params = [SingleTurnParams.INPUT] + params
    return [GEval(name=name, evaluation_steps=steps,
                  evaluation_params=params,
                  model=judge, threshold=None, async_mode=False)
            for name, steps in steps_by_metric.items()]


def check_backend(settings, backend, directory):
    config = settings["judges"][backend]
    if not config["enabled"]:
        raise ValueError(f"{backend} is disabled in judge_settings.json. No judge calls were made.")
    if backend == "gemini" and config.get("requires_completed_codex_run"):
        complete = []
        for path in Path(directory).glob("judgments/*/summary.json"):
            summary = read_json(path)
            if summary.get("backend") == "codex" and summary.get("complete"):
                complete.append(path)
        if not complete:
            raise ValueError("Complete the Codex run on this frozen sample before enabling Gemini.")
    return config


def run(directory=DEFAULT_OUTPUT, backend=None, execute=False, source_grounded=False, remaining_validation=False):
    if remaining_validation and not source_grounded:
        raise ValueError('Remaining validation cases require --source-grounded; rubric changes are not allowed.')
    manifest, pairs = prepare_remaining(directory) if remaining_validation else prepare(directory)
    settings = read_json(Path(directory) / "judge_settings.json")
    backend = backend or settings["default_backend"]
    if not execute or not settings["run_judge"]:
        print("Prepared only. Judge execution is off; no model calls made.")
        return None
    config = check_backend(settings, backend, directory)
    if remaining_validation and (backend!='codex' or config['model']!='gpt-6-luna'):
        raise ValueError('The authorized remaining-case run requires Codex gpt-6-luna; no fallback.')
    # Import only after opt-in; no Confident AI login/upload or telemetry is needed.
    os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
    os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
    version = importlib.metadata.version("deepeval")
    if version != "4.3.4":
        raise RuntimeError("Install requirements-deepeval.txt in a separate environment.")
    if backend == "codex":
        from scripts.codex_deepeval_judge import CodexJudge
        judge = CodexJudge(config["model"], timeout=config["timeout_seconds"])
    elif backend == "gemini":
        key = os.environ.get(config["api_key_env"])
        if not key:
            raise RuntimeError("Set GOOGLE_API_KEY in the kernel/process environment; do not paste it into a notebook.")
        from deepeval.models import GeminiModel
        judge = GeminiModel(model=config["model"], api_key=key, temperature=0, use_vertexai=False)
    else:
        raise ValueError("Supported judges: codex, gemini")
    steps_by_metric = METRIC_STEPS
    if source_grounded:
        from scripts.source_grounded_rubric import METRIC_STEPS as source_steps, VERSION
        steps_by_metric = source_steps
    contract = {"selection_sha256": digest(manifest), "backend": backend, "model": config["model"],
                "deepeval_version": version, "metric_steps": steps_by_metric,
                "score_normalization": "No CLI token logprobs" if backend == "codex" else "DeepEval provider behavior"}
    if source_grounded:
        contract.update(rubric_version=VERSION, evaluation_params=["input", "actual_output", "expected_output"],
                        truth_source="input clinical note", reference_role="fallible secondary checklist",
                        pairs_sha256=digest(pairs))
    out = Path(directory) / "judgments" / digest(contract)[:16]
    out.mkdir(parents=True, exist_ok=True)
    with run_lock(out):
        contract_path = out / 'run_contract.json'
        if contract_path.exists() and read_json(contract_path) != contract:
            raise ValueError('Judge run contract changed')
        if not contract_path.exists(): atomic_json(contract_path,contract)
        return evaluate(out, pairs, manifest, contract, judge, config, backend, source_grounded, remaining_validation)


def evaluate(out, pairs, manifest, contract, judge, config, backend, source_grounded, remaining_validation):
    steps_by_metric=contract['metric_steps']
    version=contract['deepeval_version']
    if remaining_validation:
        provenance_path=out/'execution_history.json'
        history=read_json(provenance_path) if provenance_path.exists() else []
        history.append(dict(started_at_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),
                            model=config['model'],rubric_version=contract['rubric_version'],
                            source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                           [Path(__file__),Path(__file__).with_name('codex_deepeval_judge.py'),Path(__file__).with_name('source_grounded_rubric.py')]}))
        atomic_json(provenance_path,history)
    records_path = out / "scores.json"
    records = read_json(records_path) if records_path.exists() else []
    expected_keys = {(p["case_id"], model, metric) for p in pairs for model in ("baseline", "finetuned") for metric in steps_by_metric}
    completed = {(r["case_id"], r["model"], r["metric"]) for r in records}
    if len(completed) != len(records) or not completed <= expected_keys:
        raise ValueError("Invalid checkpoint records")
    by_id={p['case_id']:p for p in pairs}
    for row in records:
        if (not math.isfinite(row['score']) or not 0<=row['score']<=1 or not row['reason'].strip()
                or row['format_metrics']!=by_id[row['case_id']]['format_metrics'][row['model']]):
            raise ValueError('Checkpoint content or saved output flags do not match frozen inputs')
    if (out/'summary.json').exists() and read_json(out/'summary.json').get('complete') and completed!=expected_keys:
        raise ValueError('Completed summary exists but score records are missing; restore checkpoint before proceeding')
    if not records_path.exists(): atomic_json(records_path,records)
    save_progress(out,pairs,records,steps_by_metric,'running',remaining_validation)
    from deepeval.test_case import LLMTestCase
    try:
        for index, pair in enumerate(pairs):
            # Alternate model order to reduce systematic order effects; fresh metric per output.
            models = ('baseline','finetuned') if index % 2 == 0 else ('finetuned','baseline')
            for model in models:
                test_case = LLMTestCase(input=pair['input'],expected_output=pair['expected_output'],
                                        actual_output=pair[model+'_output'])
                for metric in create_metrics(judge,source_grounded=source_grounded):
                    key = (pair['case_id'],model,metric.name)
                    if key in completed:
                        continue
                    save_progress(out,pairs,records,steps_by_metric,'running',remaining_validation,
                                  current=dict(case_id=pair['case_id'],model=model,metric=metric.name))
                    metric.measure(test_case,_show_indicator=False)
                    score = float(metric.score)
                    if not math.isfinite(score) or not 0<=score<=1:
                        raise ValueError('Judge returned a nonfinite/out-of-range score')
                    if not metric.reason or not metric.reason.strip():
                        raise ValueError('Judge returned an empty reason')
                    records.append(dict(case_id=pair['case_id'],model=model,metric=metric.name,
                                        score=score,reason=metric.reason,format_metrics=pair['format_metrics'][model]))
                    atomic_json(records_path,records)
                    completed.add(key)
                    save_progress(out,pairs,records,steps_by_metric,'running',remaining_validation)
                    print(f'Saved {len(records)}/{len(expected_keys)} metric measurements',flush=True)
    except (Exception,KeyboardInterrupt) as exc:
        # The score checkpoint is authoritative if interruption occurs between state writes.
        records=read_json(records_path)
        kind=getattr(exc,'kind','user_interrupt' if isinstance(exc,KeyboardInterrupt) else type(exc).__name__)
        save_progress(out,pairs,records,steps_by_metric,'interrupted',remaining_validation,failure=kind)
        print(f'Stopped ({kind}); {len(records)}/{len(expected_keys)} judgments safely saved. Resume with the command in progress.json.',flush=True)
        raise
    comparison = []
    for pair in pairs:
        for metric in steps_by_metric:
            scores = {r["model"]: r["score"] for r in records if r["case_id"] == pair["case_id"] and r["metric"] == metric}
            comparison.append({"case_id": pair["case_id"], "metric": metric, **scores,
                               "finetuned_minus_baseline": scores["finetuned"] - scores["baseline"]})
    with (out / "paired_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparison[0]))
        writer.writeheader()
        writer.writerows(comparison)
    summary = {"complete": completed == expected_keys, "backend": backend, "model": config["model"],
               "selected_cases": len(pairs), "paired_test_cases": len(pairs) * 2,
               "measurements": len(records), "mean_scores": {
                   metric: {model: sum(r["score"] for r in records if r["metric"] == metric and r["model"] == model) / len(pairs)
                            for model in ("baseline", "finetuned")} for metric in steps_by_metric},
               "mean_paired_deltas": {metric: sum(r["finetuned_minus_baseline"] for r in comparison if r["metric"] == metric) / len(pairs)
                                      for metric in steps_by_metric}}
    if source_grounded:
        summary.update(rubric_version=contract['rubric_version'], truth_source="input clinical note", run_id=out.name)
    atomic_json(out/'summary.json',summary)
    save_progress(out,pairs,records,steps_by_metric,'complete',remaining_validation)
    if remaining_validation:
        combine_all_validation(out,manifest,records,steps_by_metric)
    return out


def combine_all_validation(out, manifest, records, metric_names):
    from scripts.prepare_deepeval import DEFAULT_OUTPUT
    previous=DEFAULT_OUTPUT/'judgments'/manifest['previous_run_id']
    raw=(previous/'scores.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==manifest['previous_scores_sha256']
    scores=json.loads(raw)+records
    expected={(cid,model,metric) for cid in manifest['all_validation_case_ids'] for model in ('baseline','finetuned') for metric in metric_names}
    assert len(scores)==400 and {(r['case_id'],r['model'],r['metric']) for r in scores}==expected
    means={metric:{model:sum(r['score'] for r in scores if r['metric']==metric and r['model']==model)/100 for model in ('baseline','finetuned')} for metric in metric_names}
    atomic_json(out/'combined_scores_100.json',scores)
    atomic_json(out/'combined_summary_100.json',dict(complete=True,selected_cases=100,measurements=400,
                model='gpt-6-luna',rubric_version=manifest['rubric_version'],source_runs=[previous.name,out.name],
                mean_scores=means,mean_paired_deltas={m:s['finetuned']-s['baseline'] for m,s in means.items()}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--backend", choices=("codex", "gemini"))
    parser.add_argument("--run", action="store_true", help="Also requires run_judge=true in settings")
    parser.add_argument("--source-grounded", action="store_true", help="Use versioned source-note fidelity/coverage")
    parser.add_argument('--remaining-validation',action='store_true',help='Evaluate only the 80 validation cases excluded from the completed 20-case sample')
    args = parser.parse_args()
    directory=args.directory or (REMAINING_OUTPUT if args.remaining_validation else DEFAULT_OUTPUT)
    run(directory, args.backend, execute=args.run, source_grounded=args.source_grounded,remaining_validation=args.remaining_validation)
