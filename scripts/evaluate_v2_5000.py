"""Freeze and judge the 100 full-v2 pairs: exactly 400 resumable Luna measurements."""
import argparse
import csv
import hashlib
import importlib.metadata
import os
from pathlib import Path

from scripts.phase_results import ROOT, digest, read_json
from scripts.run_deepeval import atomic_json, evaluate, run_lock
from scripts.source_grounded_rubric import METRIC_STEPS, VERSION


def prepare(root=ROOT):
    root = Path(root)
    result = root / "results_v2_5000"
    contract = read_json(result / "baseline/comparison_contract.json")
    prepared = root / "prepared_clinical_dataset" / contract["dataset_version"]
    manifest = read_json(prepared / "manifest.json")
    import json
    rows = [json.loads(x) for x in (prepared / "validation.jsonl").read_text(encoding="utf-8").split("\n") if x.strip()]
    frozen = [json.loads(x) for x in (root / "prepared_clinical_dataset/e80798edebe5aba5/validation.jsonl").read_text(encoding="utf-8").split("\n") if x.strip()]
    assert len(rows) == 100 and manifest["counts"] == dict(train=5000, validation=100)
    assert [(r["case_id"], r["note"], r["source_sha256"]) for r in rows] == [(r["case_id"], r["note"], r["source_sha256"]) for r in frozen]
    assert digest(rows) == manifest["split_sha256"]["validation"] == contract["validation_sha256"]
    assert manifest["split_sha256"]["train"] == contract["train_sha256"]
    assert [r["case_id"] for r in rows] == contract["case_ids"]
    assert digest([r["prompt_text"] for r in rows]) == contract["prompt_sha256"]
    assert read_json(result / "finetuned_v2_5000/comparison_contract.json") == contract
    run = read_json(result / "finetuned_v2_5000/run_config.json")
    assert run["train_examples"] == 5000 and run["num_train_epochs"] == 3
    assert run["comparison_contract_sha256"] == digest(contract)
    training = read_json(result / "finetuned_v2_5000/metrics.json")
    assert training["train"]["epoch"] == 3.0
    outputs, flags, sources = {}, {}, []
    for model, folder in (("baseline", result / "baseline/gen_rp_1.08"),
                          ("finetuned", result / "comparison/finetuned__gen_rp_1.08")):
        outputs[model] = read_json(folder / "generations.json")
        with (folder / "per_case.csv").open(encoding="utf-8", newline="") as handle:
            scores = list(csv.DictReader(handle))
        flags[model] = {r["case_id"]: r for r in scores}
        assert len(scores) == 100 and set(flags[model]) == set(outputs[model]) == set(contract["case_ids"])
        for row in rows:
            score = flags[model][row["case_id"]]
            assert score["reference"] == row["reference"] and score["generated"] == outputs[model][row["case_id"]]
        sources += [folder / "generations.json", folder / "per_case.csv"]
    pairs = [dict(case_id=r["case_id"], input=r["note"], expected_output=r["reference"],
                  baseline_output=outputs["baseline"][r["case_id"]], finetuned_output=outputs["finetuned"][r["case_id"]],
                  format_metrics={m: flags[m][r["case_id"]] for m in flags}) for r in rows]
    selection = dict(experiment="v2_full_schema_5000", dataset_version=contract["dataset_version"],
                     selected_cases=100, paired_test_cases=200, planned_metric_measurements=400,
                     case_ids=contract["case_ids"], comparison_contract_sha256=digest(contract),
                     pairs_sha256=digest(pairs), rubric_version=VERSION, metric_steps=METRIC_STEPS,
                     evaluation_scope="Unchanged v3 source rubric for comparability; full-v2 reference checklist. Full-schema F1 is a separate measure.",
                     source_sha256={str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    directory = result / "deepeval_100"
    directory.mkdir(exist_ok=True)
    for filename, value in (("selection_manifest.json", selection), ("paired_cases.json", pairs)):
        path = directory / filename
        if path.exists() and read_json(path) != value:
            raise ValueError("Frozen evaluation inputs changed; refusing to reuse scores")
        if not path.exists():
            atomic_json(path, value)
    return directory, selection, pairs


def run(root=ROOT, execute=False, backend="codex", model=None):
    directory, selection, pairs = prepare(root)
    if not execute:
        print("Prepared 100 paired cases / 400 measurements; no judge calls.")
        return directory
    os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
    os.environ["DEEPEVAL_DISABLE_DOTENV"] = "1"
    version = importlib.metadata.version("deepeval")
    if version != "4.3.4":
        raise RuntimeError("Use the isolated requirements-deepeval.txt environment")
    if backend == "codex":
        from scripts.codex_deepeval_judge import CodexJudge
        model = model or "gpt-6-luna"
        config = dict(model=model, timeout_seconds=300)
        judge = CodexJudge(model, timeout=300)
        score_normalization = "No CLI token logprobs"
        resume_cmd = ".venv/deepeval-tools/Scripts/python.exe -u -m scripts.evaluate_v2_5000 --run"
    elif backend == "gemini":
        from dotenv import load_dotenv
        load_dotenv(Path(root) / ".env.local")
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("Set GEMINI_API_KEY in .env.local or the process environment.")
        from deepeval.models import GeminiModel
        model = model or "gemini-4-hydrogen"
        config = dict(model=model)
        judge = GeminiModel(model=model, api_key=key, temperature=0, use_vertexai=False)
        score_normalization = "DeepEval provider behavior"
        resume_cmd = f".venv/deepeval-tools/Scripts/python.exe -u -m scripts.evaluate_v2_5000 --run --backend gemini --model {model}"
    else:
        raise ValueError("Supported backends: codex, gemini")
    contract = dict(selection_sha256=digest(selection), pairs_sha256=digest(pairs), backend=backend,
                    model=model, deepeval_version=version, metric_steps=METRIC_STEPS,
                    rubric_version=VERSION, evaluation_params=["input", "actual_output", "expected_output"],
                    truth_source="input clinical note", reference_role="fallible full-schema v2 checklist",
                    score_normalization=score_normalization)
    out = directory / "judgments" / digest(contract)[:16]
    out.mkdir(parents=True, exist_ok=True)
    with run_lock(out):
        path = out / "run_contract.json"
        if path.exists() and read_json(path) != contract:
            raise ValueError("Judge contract changed")
        if not path.exists():
            atomic_json(path, contract)
        resume = str(Path(__file__).relative_to(ROOT)).replace("\\", "/")
        atomic_json(directory / "execution.json", dict(resume_command=resume_cmd,
                                                     runner=resume, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
        return evaluate(out, pairs, selection, contract, judge, config, backend, True, False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Execute the authorized 400 judgments; resumes saved keys")
    parser.add_argument("--backend", choices=("codex", "gemini"), default="codex")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()
    run(execute=args.run, backend=args.backend, model=args.model)
