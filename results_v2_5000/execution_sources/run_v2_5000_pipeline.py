"""Execute the four experiment notebooks in separate kernels on the Colab VM."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    credential = Path("/content/.clinical_v2_5000_hf_token")
    if credential.exists():
        os.environ["HF_TOKEN"] = credential.read_text().strip()
        credential.unlink()
    result = root / "results_v2_5000"
    result.mkdir(exist_ok=True)
    state_path = result / "pipeline_status.json"
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    completed = previous.get("completed", [])
    for stage in ("00_prepare_dataset", "01_baseline_eval", "02_finetune", "03_eval_and_compare"):
        if stage in completed:
            continue
        state = dict(stage=stage, status="running", completed=completed,
                     updated_at_utc=datetime.now(timezone.utc).isoformat())
        state_path.write_text(json.dumps(state, indent=2))
        with (result / (stage + ".log")).open("a", encoding="utf-8") as log:
            process = subprocess.run([sys.executable, "-u", "scripts/run_colab_notebook.py",
                                      f"notebooks/v2_5000/{stage}.ipynb"], stdout=log, stderr=subprocess.STDOUT)
        if process.returncode:
            state.update(status="failed", returncode=process.returncode)
            state_path.write_text(json.dumps(state, indent=2))
            raise SystemExit(process.returncode)
        completed.append(stage)
    state_path.write_text(json.dumps(dict(status="generation_complete", completed=completed,
                                        updated_at_utc=datetime.now(timezone.utc).isoformat()), indent=2))


if __name__ == "__main__":
    main()
