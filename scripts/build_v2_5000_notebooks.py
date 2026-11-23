"""Derive isolated full-schema notebooks from the preserved v2 implementation."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cell(kind, source):
    result = dict(cell_type=kind, metadata={}, source=source.splitlines(keepends=True))
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def build(root=ROOT):
    destination = root / "notebooks/v2_5000"
    destination.mkdir(parents=True, exist_ok=True)
    install = '%pip install -q "transformers==4.57.6" "datasets==4.8.5" "peft==0.18.1" "accelerate==1.15.0" pandas huggingface_hub nbclient nbformat\n'
    prepare = dict(nbformat=4, nbformat_minor=5,
                   metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3")),
                   cells=[cell("markdown", "# Full-schema v2: 5,000 training / frozen 100 development notes\nNo child-field pruning or clinical label repair. Preserve v2 cleaning and prompting."),
                          cell("code", install), cell("code", "from scripts.prepare_v2_5000_dataset import build_dataset\nprepared_dir = build_dataset()\n")])
    (destination / "00_prepare_dataset.ipynb").write_text(json.dumps(prepare, indent=1), encoding="utf-8")
    for name in ("01_baseline_eval", "02_finetune", "03_eval_and_compare"):
        notebook = copy.deepcopy(json.loads((root / "notebooks" / (name + ".ipynb")).read_text(encoding="utf-8")))
        for c in notebook["cells"]:
            source = "".join(c["source"])
            source = source.replace("results_v2", "results_v2_5000").replace("finetuned_v2", "finetuned_v2_5000")
            source = source.replace("latest_v2.json", "latest_v2_5000.json")
            source = source.replace('(Path("/content/results_v2_5000") if Path("/content").is_dir() else Path("results_v2_5000"))', 'Path("results_v2_5000")')
            if c["cell_type"] == "code":
                if source.startswith("%pip install"):
                    source = install
                source = source.replace('(OUTPUT_ROOT / "comparison_contract.json").write_text',
                    'if (OUTPUT_ROOT / "comparison_contract.json").exists():\n'
                    '    assert json.loads((OUTPUT_ROOT / "comparison_contract.json").read_text(encoding="utf-8")) == contract, "Baseline contract changed; refusing cached generations"\n'
                    '(OUTPUT_ROOT / "comparison_contract.json").write_text')
                source = source.replace('    {"tag": "rp_1.00", "repetition_penalty": 1.0, "generated_only": False},\n', "")
                source = source.replace('GRADIENT_CHECKPOINTING = False  # Verified 8.34 GiB peak on 1651-tok longest row on T4 (15 GiB), 4x faster',
                                        'GRADIENT_CHECKPOINTING = False  # Recheck the actual new longest row below.')
                source = source.replace('result = trainer.train()',
                    'from transformers.trainer_utils import get_last_checkpoint\n'
                    'last_checkpoint = get_last_checkpoint(str(OUTPUT_DIR / "checkpoints")) if (OUTPUT_DIR / "checkpoints").exists() else None\n'
                    'result = trainer.train(resume_from_checkpoint=last_checkpoint)\n'
                    'assert trainer.state.global_step == 1875 and trainer.state.epoch == 3.0')
                # Keep resumable optimizer checkpoints until downloaded and verified.
                source = source.replace('    shutil.rmtree(OUTPUT_DIR / "checkpoints")', '    print("Retaining resumable checkpoints until local archival is verified.")')
                source = source.replace('trainer = FiniteLossTrainer(',
                    'from transformers import TrainerCallback\n'
                    'class SaveLiveLog(TrainerCallback):\n'
                    '    def on_log(self, args, state, control, **kwargs):\n'
                    '        pending = OUTPUT_DIR / "training_log.pending"\n'
                    '        pending.write_text(json.dumps(state.log_history, indent=2), encoding="utf-8")\n'
                    '        pending.replace(OUTPUT_DIR / "training_log.json")\n\n'
                    'trainer = FiniteLossTrainer(')
                source = source.replace('model=model, args=args, data_collator=collate, train_dataset=train_data, eval_dataset=eval_data',
                                        'model=model, args=args, data_collator=collate, train_dataset=train_data, eval_dataset=eval_data, callbacks=[SaveLiveLog()]')
                if 'loss = model(**batch).loss' in source:
                    start = source.index('loss = model(**batch).loss')
                    end = source.index('model_check = {', start)
                    source = source[:start] + '''def backward_check():
    loss = model(**batch).loss
    assert torch.isfinite(loss), "Non-finite initial loss"
    loss.backward()
    grads = [p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
    assert grads and all(bool(torch.isfinite(g).all()) for g in grads), "Non-finite gradients"
    return loss, grads

try:
    loss, grads = backward_check()
except torch.cuda.OutOfMemoryError:
    model.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    GRADIENT_CHECKPOINTING = True
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    torch.cuda.reset_peak_memory_stats()
    loss, grads = backward_check()
''' + source[end:]
                c.update(outputs=[], execution_count=None)
                # Compile transformed Python without executing imports or training.
                if not source.startswith("%"):
                    compile(source, str(destination / (name + ".ipynb")), "exec")
            c["source"] = source.splitlines(keepends=True)
        (destination / (name + ".ipynb")).write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    print("Created notebooks:", destination)


if __name__ == "__main__":
    build()
