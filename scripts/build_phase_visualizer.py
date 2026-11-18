"""Generate the standalone report from saved artifacts, never hand-copied scores."""
import json

from scripts.phase_results import ROOT, load_phase, read_json
from scripts.prepare_deepeval import prepare


def build():
    selection, _ = prepare()
    phases = [load_phase(name) for name in ("phase1", "phase2")]
    judge_root = ROOT / "results_v3/deepeval_20"
    runs = []
    for path in sorted(judge_root.glob("judgments/*/summary.json")):
        summary = read_json(path)
        if not summary.get("complete"):
            continue
        contract = read_json(path.with_name("run_contract.json"))
        scores = read_json(path.with_name("scores.json"))
        assert len(scores) == len({(r['case_id'], r['model'], r['metric']) for r in scores}) == 80
        assert {r['case_id'] for r in scores} == set(selection['case_ids'])
        runs.append({**summary, "run_id": path.parent.name,
                     "rubric_version": contract.get("rubric_version", "reference_only_v1"),
                     "metric_steps": contract['metric_steps'],
                     "scores": [{k: r[k] for k in ('case_id', 'model', 'metric', 'score', 'reason')} for r in scores]})
        quality = path.with_name('quality_notes.json')
        if quality.exists():
            runs[-1]['quality_notes'] = read_json(quality)
    data = {"phases": phases, "judge_selection": selection,
            "judge_runs": runs,
            "judge_settings": read_json(judge_root / "judge_settings.json")}
    # Embedded data must not be able to close the application/json script element.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (ROOT / "scripts/phase_visualizer.html").read_text(encoding="utf-8")
    assert template.count("__REPORT_DATA__") == 1
    output = ROOT / "docs/Clinical_Extraction_Phases_1_and_2.html"
    output.write_text(template.replace("__REPORT_DATA__", payload), encoding="utf-8")
    print(f"Saved {output.name}: {len(phases[0]['cases'])} + {len(phases[1]['cases'])} cases; 20 paired DeepEval selections")
    return output


if __name__ == "__main__":
    build()
