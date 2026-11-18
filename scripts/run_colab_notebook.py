"""Run on Colab as a background process; checkpoint real cell outputs to disk.

Uses nbclient's documented cell hooks:
https://nbclient.readthedocs.io/en/latest/client.html
"""
import json
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main():
    source = Path(sys.argv[1]).resolve()
    output = source.with_stem(source.stem + "_output")
    status = source.with_suffix(".status.json")
    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    state = {"notebook": source.name, "state": "running", "started": time.time(),
             "completed_code_cells": [], "current_cell": None}

    def save():
        pending = output.with_suffix(".pending")
        nbformat.write(notebook, pending)
        pending.replace(output)
        pending_status = status.with_suffix(".pending")
        pending_status.write_text(json.dumps(state, indent=2), encoding="utf-8")
        pending_status.replace(status)

    def starting(cell, cell_index, **kwargs):
        state["current_cell"] = cell_index
        save()

    def completed(cell, cell_index, execute_reply, **kwargs):
        state["completed_code_cells"].append(cell_index)
        save()

    save()
    client = NotebookClient(notebook, timeout=None, kernel_name="python3",
                            resources={"metadata": {"path": str(Path.cwd())}},
                            on_cell_execute=starting, on_cell_executed=completed)
    try:
        client.execute()
        state["state"] = "complete"
    except Exception as exc:
        state["state"] = "failed"
        state["error_type"] = type(exc).__name__
        raise
    finally:
        state["finished"] = time.time()
        save()


if __name__ == "__main__":
    main()
