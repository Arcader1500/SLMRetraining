"""Read the frozen notebook results without loading a model or training stack."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASES = {
    "phase1": ("results_v2", "finetuned_v2", "eeff5efa1619f198", "Original child schema"),
    "phase2": ("results_v3", "finetuned_v3", "e80798edebe5aba5", "30 paths: 10 parents + 20 children"),
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_phase(phase, root=ROOT):
    result_name, adapter, version, schema_label = PHASES[phase]
    result = root / result_name
    prepared = root / "prepared_clinical_dataset" / version
    contract = read_json(result / "baseline/comparison_contract.json")
    manifest = read_json(prepared / "manifest.json")
    rows = [json.loads(line) for line in (prepared / "validation.jsonl").read_text(encoding="utf-8").splitlines()]
    assert digest(rows) == manifest["split_sha256"]["validation"] == contract["validation_sha256"]
    assert manifest["split_sha256"]["train"] == contract["train_sha256"]
    assert contract["dataset_version"] == version
    assert [r["case_id"] for r in rows] == contract["case_ids"]
    assert digest([r["prompt_text"] for r in rows]) == contract["prompt_sha256"]
    selection = read_json(result / "baseline/selection.json")
    assert selection == [{k: r[k] for k in ("case_id", "note", "reference", "prompt_text")} for r in rows]
    sources = [result / "baseline/comparison_contract.json", result / "baseline/selection.json"]
    outputs, metrics = {}, {}
    for model, folder in (
        ("baseline", result / "baseline/gen_rp_1.08"),
        ("finetuned", result / "comparison/finetuned__gen_rp_1.08"),
    ):
        outputs[model] = read_json(folder / "generations.json")
        with (folder / "per_case.csv").open(encoding="utf-8", newline="") as handle:
            metrics[model] = {r["case_id"]: r for r in csv.DictReader(handle)}
        assert set(outputs[model]) == set(metrics[model]) == set(contract["case_ids"])
        assert all(metrics[model][r["case_id"]]["reference"] == r["reference"] for r in rows)
        assert all(metrics[model][cid]["generated"] == text for cid, text in outputs[model].items())
        sources += [folder / "generations.json", folder / "per_case.csv"]
    cases = [{"case_id": r["case_id"], "note": r["note"], "reference": r["reference"],
              "baseline": outputs["baseline"][r["case_id"]], "finetuned": outputs["finetuned"][r["case_id"]],
              "metrics": {m: metrics[m][r["case_id"]] for m in metrics}} for r in rows]
    summaries_path = result / "comparison/summary_comparison.json"
    log_path = result / adapter / "training_log.json"
    log = read_json(log_path)
    validation = {e["step"]: {"step": e["step"], "loss": e["eval_loss"]} for e in log if "eval_loss" in e}
    sources += [summaries_path, log_path, prepared / "manifest.json", prepared / "validation.jsonl"]
    return {
        "id": phase, "label": "Phase 1" if phase == "phase1" else "Phase 2", "schema": schema_label,
        "dataset_version": version, "contract": contract, "cases": cases,
        "summaries": read_json(summaries_path), "counts": manifest["counts"],
        "lengths": manifest["lengths"], "training": read_json(result / adapter / "metrics.json"),
        "memory": read_json(result / adapter / "model_checks.json"),
        "loss": {"training": [{"step": e["step"], "loss": e["loss"]} for e in log if "loss" in e],
                 "validation": list(validation.values())},
        "source_sha256": {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    }
