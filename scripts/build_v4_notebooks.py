"""Build isolated notebooks and frozen baseline for the v4 (ca7b6e90c1019441) regenerated-label SFT run."""
import copy
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

from scripts.prepare_v3_dataset import SCHEMA, DICT_KEYS, schema_valid

ROOT = Path(__file__).resolve().parents[1]

TOP_LEVEL_KEYS = (
    "visit motivation", "admission", "patient information", "patient medical history",
    "surgeries", "symptoms", "medical examinations", "diagnosis tests", "treatments", "discharge",
)
MISSING_VALUES = ("", "none", "null", "unknown", "not provided")

FROZEN_20_CASES = [
    "validation:593",
    "validation:1351",
    "validation:113",
    "validation:937",
    "validation:1953",
    "validation:1812",
    "validation:1630",
    "validation:1388",
    "validation:128",
    "validation:725",
    "validation:302",
    "validation:1241",
    "validation:412",
    "validation:2654",
    "validation:1133",
    "validation:1628",
    "validation:1722",
    "validation:2890",
    "validation:435",
    "validation:337",
]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonstandard JSON constant: " + value)


def load_object(text, strict=True):
    obj = json.loads(
        text, strict=strict, object_pairs_hook=no_duplicate_keys, parse_constant=reject_constant
    )
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object")
    return obj


def strip_fences(text):
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        return re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)[:-3].strip()
    return text


def facts(value, path=""):
    result = Counter()
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(facts(child, f"{path}.{key}" if path else key))
    elif isinstance(value, list):
        for child in value:
            result.update(facts(child, path))
    elif value is not None:
        normalized = " ".join(str(value).casefold().split())
        if normalized not in MISSING_VALUES:
            result[(path, normalized)] += 1
    return result


def facts_by_path(value, path=""):
    result = {}
    for (p, v), cnt in facts(value, path).items():
        result.setdefault(p, []).extend([v] * cnt)
    return result


def key_paths(value, prefix=""):
    result = set()
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            result.add(path)
            result.update(key_paths(child, path))
    elif isinstance(value, list):
        for child in value:
            result.update(key_paths(child, prefix))
    return result


def _token_f1(a_str, b_str):
    ta = Counter(re.findall(r"[a-z0-9]+", a_str.casefold()))
    tb = Counter(re.findall(r"[a-z0-9]+", b_str.casefold()))
    na, nb = sum(ta.values()), sum(tb.values())
    if not na or not nb:
        return 0.0
    ov = sum((ta & tb).values())
    return (2.0 * ov) / (na + nb)


def soft_fact_scores(expected_obj, actual_obj):
    if actual_obj is None:
        return 0.0, 0.0, 0.0
    exp_map = facts_by_path(expected_obj)
    act_map = facts_by_path(actual_obj)
    n_exp = sum(len(v) for v in exp_map.values())
    n_act = sum(len(v) for v in act_map.values())
    if not n_exp or not n_act:
        return 0.0, 0.0, 0.0
    total_sim = 0.0
    for path, exp_vals in exp_map.items():
        act_vals = act_map.get(path, [])
        if not act_vals:
            continue
        pairs = []
        for i, ev in enumerate(exp_vals):
            for j, av in enumerate(act_vals):
                s = 1.0 if ev == av else _token_f1(ev, av)
                if s > 0:
                    pairs.append((s, i, j))
        pairs.sort(reverse=True)
        used_e, used_a = set(), set()
        for s, i, j in pairs:
            if i not in used_e and j not in used_a:
                used_e.add(i)
                used_a.add(j)
                total_sim += s
    prec = total_sim / n_act
    rec = total_sim / n_exp
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return prec, rec, f1


def count_duplicate_array_items(text):
    try:
        obj = load_object(strip_fences(text))
    except ValueError:
        return None
    dups = 0

    def walk(node):
        nonlocal dups
        if isinstance(node, list):
            seen = set()
            for item in node:
                key = json.dumps(item, ensure_ascii=False, sort_keys=True)
                if key in seen:
                    dups += 1
                seen.add(key)
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(obj)
    return dups


def max_word_5gram_repeat(text):
    words = re.findall(r"\S+", text.lower())
    if len(words) < 5:
        return 0
    counts = Counter(tuple(words[i : i + 5]) for i in range(len(words) - 4))
    return max(counts.values()) if counts else 0


def evaluate_output(text, reference):
    expected = load_object(reference)
    raw_valid = True
    try:
        load_object(text)
    except ValueError:
        raw_valid = False
    try:
        actual = load_object(strip_fences(text))
        error = None
    except ValueError as exc:
        actual, error = None, str(exc)
    expected_facts = facts(expected)
    actual_facts = facts(actual)
    matches = sum((expected_facts & actual_facts).values())
    n_actual, n_expected = sum(actual_facts.values()), sum(expected_facts.values())
    precision = matches / n_actual if n_actual else 0.0
    recall = matches / n_expected if n_expected else 0.0
    soft_p, soft_r, soft_f1 = soft_fact_scores(expected, actual)
    return {
        "empty": not text.strip(),
        "raw_json_object_valid": raw_valid,
        "json_object_valid_after_fence_removal": actual is not None,
        "parse_error": error,
        "allowed_schema_valid": schema_valid(actual),
        "raw_allowed_schema_valid": raw_valid and schema_valid(actual),
        "exact_top_level_keys": actual is not None and set(actual.keys()) == set(TOP_LEVEL_KEYS),
        "exact_key_match": actual is not None and key_paths(actual) == key_paths(expected),
        "nonmissing_generated_values": n_actual,
        "reference_values": n_expected,
        "matched_values": matches,
        "placeholder_only": actual is not None and n_actual == 0,
        "value_precision": precision,
        "value_recall": recall,
        "value_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "soft_value_precision": soft_p,
        "soft_value_recall": soft_r,
        "soft_value_f1": soft_f1,
        "duplicate_array_items": count_duplicate_array_items(text),
        "max_5gram_repeat": max_word_5gram_repeat(text),
    }


def score_run_records(cases, outputs, diagnostics):
    import pandas as pd

    records = []
    for case in cases:
        key = case["case_id"]
        text = outputs[key]
        records.append({
            "case_id": key,
            **evaluate_output(text, case["reference"]),
            "reached_budget": bool(diagnostics[key].get("reached_budget")),
            "generated_tokens": int(diagnostics[key]["generated_tokens"]),
            "generated": text,
            "reference": case["reference"],
        })
    frame = pd.DataFrame(records)
    summary = {"selected_cases": len(cases), "evaluated_cases": len(records)}
    for name in (
        "empty", "raw_json_object_valid", "json_object_valid_after_fence_removal",
        "exact_top_level_keys", "allowed_schema_valid", "raw_allowed_schema_valid",
        "exact_key_match", "placeholder_only", "reached_budget",
    ):
        summary[name + "_cases"] = int(frame[name].sum())
    for name in (
        "value_precision", "value_recall", "value_f1",
        "soft_value_precision", "soft_value_recall", "soft_value_f1",
    ):
        summary["mean_" + name] = float(frame[name].mean())
    for key, col in (
        ("matched_values", "matched_values"),
        ("reference_values", "reference_values"),
        ("generated_values", "nonmissing_generated_values"),
    ):
        summary[key] = int(frame[col].sum())
    summary["mean_generated_tokens"] = float(frame["generated_tokens"].mean())
    summary["max_5gram_repeat_ge_3_cases"] = int((frame["max_5gram_repeat"] >= 3).sum())
    return frame, summary


def find_schema_violations(cases, outputs):
    violations = []
    for case in cases:
        cid = case["case_id"]
        text = outputs[cid]
        try:
            obj = load_object(strip_fences(text))
        except ValueError as exc:
            violations.append({"case_id": cid, "parse_valid": False, "issues": [str(exc)]})
            continue
        if schema_valid(obj):
            continue
        issues = []
        missing_top = [k for k in SCHEMA if k not in obj]
        extra_top = [k for k in obj if k not in SCHEMA]
        if missing_top:
            issues.append(f"missing top-level keys: {missing_top}")
        if extra_top:
            issues.append(f"disallowed top-level keys: {extra_top}")
        for parent, allowed_fields in SCHEMA.items():
            if parent not in obj:
                continue
            val = obj[parent]
            if parent == "visit motivation":
                if not isinstance(val, str):
                    issues.append(f"visit motivation is {type(val).__name__}, expected str")
            elif parent in DICT_KEYS:
                if not isinstance(val, dict):
                    issues.append(f"{parent} is {type(val).__name__}, expected dict")
                else:
                    for k, v in val.items():
                        if k not in allowed_fields:
                            issues.append(f"{parent}: disallowed key {k}")
                        if isinstance(v, (list, dict)) or v is None:
                            issues.append(f"{parent}.{k}: non-scalar or null value")
            else:
                if not isinstance(val, list):
                    issues.append(f"{parent} is {type(val).__name__}, expected list")
                else:
                    for idx, entry in enumerate(val):
                        if not isinstance(entry, dict):
                            issues.append(f"{parent}[{idx}]: non-object entry")
                        else:
                            for k, v in entry.items():
                                if k not in allowed_fields:
                                    issues.append(f"{parent}[{idx}]: disallowed key {k}")
                                if isinstance(v, (list, dict)) or v is None:
                                    issues.append(f"{parent}[{idx}].{k}: non-scalar or null value")
        violations.append({"case_id": cid, "parse_valid": True, "issues": issues})
    return violations


def prepare_baseline(root=ROOT):
    """Populate results_v4/baseline from frozen results_v3/baseline since prompts and model are identical."""
    pointer = json.loads((root / "prepared_clinical_dataset/latest_v3_regenerated.json").read_text(encoding="utf-8"))
    version = pointer["version"]
    prepared_dir = root / "prepared_clinical_dataset" / version
    manifest = json.loads((prepared_dir / "manifest.json").read_text(encoding="utf-8"))
    val_rows = [json.loads(line) for line in (prepared_dir / "validation.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
    train_rows = [json.loads(line) for line in (prepared_dir / "train.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
    assert digest(train_rows) == manifest["split_sha256"]["train"]
    assert digest(val_rows) == manifest["split_sha256"]["validation"]

    v3_contract = json.loads((root / "results_v3/baseline/comparison_contract.json").read_text(encoding="utf-8"))
    assert [c["case_id"] for c in val_rows] == v3_contract["case_ids"]
    assert digest([c["prompt_text"] for c in val_rows]) == v3_contract["prompt_sha256"]

    v3_val_rows = [json.loads(line) for line in (root / "prepared_clinical_dataset/e80798edebe5aba5/validation.jsonl").read_text(encoding="utf-8").split("\n") if line.strip()]
    assert [(r["case_id"], r["note"], r["prompt_text"]) for r in val_rows] == [(r["case_id"], r["note"], r["prompt_text"]) for r in v3_val_rows]

    baseline_dir = root / "results_v4/baseline"
    cond_dir = baseline_dir / "gen_rp_1.08"
    cond_dir.mkdir(parents=True, exist_ok=True)

    contract = copy.deepcopy(v3_contract)
    contract["dataset_version"] = version
    contract["train_sha256"] = manifest["split_sha256"]["train"]
    contract["validation_sha256"] = manifest["split_sha256"]["validation"]
    (baseline_dir / "comparison_contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")

    selection = [{"case_id": c["case_id"], "note": c["note"], "reference": c["reference"], "prompt_text": c["prompt_text"]} for c in val_rows]
    (baseline_dir / "selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding="utf-8")

    # Copy exact base model generations & diagnostics (prompts, seed, model revision, and decoding are 100% identical)
    shutil.copy2(root / "results_v3/baseline/gen_rp_1.08/generations.json", cond_dir / "generations.json")
    shutil.copy2(root / "results_v3/baseline/gen_rp_1.08/generation_diagnostics.json", cond_dir / "generation_diagnostics.json")

    gens = json.loads((cond_dir / "generations.json").read_text(encoding="utf-8"))
    diags = json.loads((cond_dir / "generation_diagnostics.json").read_text(encoding="utf-8"))
    df, summary = score_run_records(val_rows, gens, diags)
    df.to_csv(cond_dir / "per_case.csv", index=False)
    (cond_dir / "aggregate.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_row = [{"model": "base", "decoding": "gen_rp_1.08", **summary}]
    import pandas as pd
    pd.DataFrame(summary_row).to_csv(baseline_dir / "summary_metrics.csv", index=False)
    (baseline_dir / "summary_metrics.json").write_text(json.dumps(summary_row, indent=2), encoding="utf-8")
    return contract


def cell(kind, source):
    result = dict(cell_type=kind, metadata={}, source=source.splitlines(keepends=True))
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def build_notebooks(root=ROOT):
    destination = root / "notebooks/v4_1325"
    destination.mkdir(parents=True, exist_ok=True)
    install = '%pip install -q "transformers==4.57.6" "datasets==4.8.5" "peft==0.18.1" "accelerate==1.15.0" pandas huggingface_hub nbclient nbformat\n'

    # 1. Build 01_baseline_eval.ipynb (verifies cached baseline outputs under contract)
    nb01 = copy.deepcopy(json.loads((root / "notebooks/v3_1325/01_baseline_eval.ipynb").read_text(encoding="utf-8")))
    for c in nb01["cells"]:
        src = "".join(c["source"])
        src = src.replace("/content/clinical_v3", "/content/clinical_v4")
        src = src.replace("/content/results_v3", "/content/clinical_v4/results_v4")
        src = src.replace("results_v3", "results_v4")
        src = src.replace("latest_v3.json", "latest_v3_regenerated.json")
        if c["cell_type"] == "code":
            if src.startswith("%pip install"):
                src = install
            # Remove strict transformers/datasets version equality against manifest prepare environment (5.22.2 vs 4.57.6 runtime)
            src = re.sub(
                r'for package in \("transformers", "datasets"\):\n\s+assert importlib\.metadata\.version\(package\) == cfg\[package\], \(\n\s+f"\{package\} mismatch: \{importlib\.metadata\.version\(package\)\} vs \{cfg\[package\]\}"\n\s+\)',
                'assert importlib.metadata.version("transformers") == "4.57.6"',
                src,
            )
            c.update(outputs=[], execution_count=None)
            if not src.startswith("%"):
                compile(src, str(destination / "01_baseline_eval.ipynb"), "exec")
        c["source"] = src.splitlines(keepends=True)
    (destination / "01_baseline_eval.ipynb").write_text(json.dumps(nb01, indent=1, ensure_ascii=False), encoding="utf-8")

    # 2. Build 02_finetune.ipynb (exact v3 LoRA recipe + SaveLiveLog + checkpoint retention + backward OOM guard)
    nb02 = copy.deepcopy(json.loads((root / "notebooks/v3_1325/02_finetune.ipynb").read_text(encoding="utf-8")))
    for c in nb02["cells"]:
        src = "".join(c["source"])
        src = src.replace("/content/clinical_v3", "/content/clinical_v4")
        src = src.replace("/content/results_v3", "/content/clinical_v4/results_v4")
        src = src.replace("results_v3", "results_v4")
        src = src.replace("finetuned_v3", "finetuned_v4")
        src = src.replace("latest_v3.json", "latest_v3_regenerated.json")
        if c["cell_type"] == "code":
            if src.startswith("%pip install"):
                src = install
            if "loss = model(**batch).loss" in src:
                start = src.index("loss = model(**batch).loss")
                end = src.index("model_check = {", start)
                src = (
                    src[:start]
                    + """def backward_check():
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
"""
                    + src[end:]
                )
            src = src.replace("save_total_limit=2,", "save_total_limit=3,")
            src = src.replace(
                "class SaveProgress(TrainerCallback):",
                """class SaveLiveLog(TrainerCallback):
    def on_log(self, args, state, control, **kwargs):
        pending = OUTPUT_DIR / "training_log.pending"
        pending.write_text(json.dumps(state.log_history, indent=2), encoding="utf-8")
        pending.replace(OUTPUT_DIR / "training_log.json")

class SaveProgress(TrainerCallback):""",
            )
            src = src.replace("callbacks=[SaveProgress()],", "callbacks=[SaveProgress(), SaveLiveLog()],")
            src = src.replace(
                "result = trainer.train()",
                """from transformers.trainer_utils import get_last_checkpoint
last_checkpoint = get_last_checkpoint(str(OUTPUT_DIR / "checkpoints")) if (OUTPUT_DIR / "checkpoints").exists() else None
result = trainer.train(resume_from_checkpoint=last_checkpoint)
assert trainer.state.global_step == 498 and trainer.state.epoch == 3.0""",
            )
            src = src.replace(
                '    shutil.rmtree(OUTPUT_DIR / "checkpoints")',
                '    print("Retaining resumable checkpoints (166, 332, 498) until local archival is verified.")',
            )
            c.update(outputs=[], execution_count=None)
            if not src.startswith("%"):
                compile(src, str(destination / "02_finetune.ipynb"), "exec")
        c["source"] = src.splitlines(keepends=True)
    (destination / "02_finetune.ipynb").write_text(json.dumps(nb02, indent=1, ensure_ascii=False), encoding="utf-8")

    # 3. Build 03_eval_and_compare.ipynb (all existing 100-case steps + 20-case gen_rp_1.00 on both old v3 and new v4 adapters)
    nb03 = copy.deepcopy(json.loads((root / "notebooks/v3_1325/03_eval_and_compare.ipynb").read_text(encoding="utf-8")))
    for c in nb03["cells"]:
        src = "".join(c["source"])
        src = src.replace("/content/clinical_v3", "/content/clinical_v4")
        src = src.replace("/content/results_v3", "/content/clinical_v4/results_v4")
        src = src.replace("results_v3", "results_v4")
        src = src.replace("finetuned_v3", "finetuned_v4")
        src = src.replace("latest_v3.json", "latest_v3_regenerated.json")
        if c["cell_type"] == "code":
            if src.startswith("%pip install"):
                src = install
            c.update(outputs=[], execution_count=None)
            if not src.startswith("%"):
                compile(src, str(destination / "03_eval_and_compare.ipynb"), "exec")
        c["source"] = src.splitlines(keepends=True)

    # Append the 20-case gen_rp_1.00 decoding ablation cells for both old v3 and new v4 adapters
    ablation_md = """## 20-Case `gen_rp_1.00` (with budget-loop fallback) Decoding Evaluation on Old V3 and New V4 Adapters
Evaluates greedy decoding (`repetition_penalty=1.00`, retrying with generated-only `1.08` only if a case hits the `2,048`-token budget loop) on the exact 20 frozen audit/judge cases (`FROZEN_20_CASES`) for both:
1. **`finetuned_v3` (`e80798edebe5aba5` adapter)**
2. **`finetuned_v4` (`ca7b6e90c1019441` regenerated-label adapter)**

Also computes a unified 20-case comparison table across `base`, `finetuned_v3`, and `finetuned_v4` under both `gen_rp_1.08` and `gen_rp_1.00_fb1.08`, scored against both the regenerated `v4` references and the original `v3` references, plus schema violations for `finetuned_v4`."""

    ablation_code = """FROZEN_20_CASES = [
    "validation:593", "validation:1351", "validation:113", "validation:937", "validation:1953",
    "validation:1812", "validation:1630", "validation:1388", "validation:128", "validation:725",
    "validation:302", "validation:1241", "validation:412", "validation:2654", "validation:1133",
    "validation:1628", "validation:1722", "validation:2890", "validation:435", "validation:337",
]
cases_by_id = {c["case_id"]: c for c in cases}
cases_20 = [cases_by_id[cid] for cid in FROZEN_20_CASES]
assert len(cases_20) == 20

# Also load original v3 validation references and cached v3 gen_rp_1.08 predictions for 20-case 4-way comparison
v3_val_path = PREPARED_ROOT / "e80798edebe5aba5" / "validation.jsonl"
v3_refs_by_id = {
    row["case_id"]: row["reference"]
    for line in v3_val_path.read_text(encoding="utf-8").split("\\n") if line.strip()
    for row in [json.loads(line)]
}
cases_20_v3_ref = [{**c, "reference": v3_refs_by_id[c["case_id"]]} for c in cases_20]
cases_100_v3_ref = [{**c, "reference": v3_refs_by_id[c["case_id"]]} for c in cases]

OLD_V3_ADAPTER_DIR = runtime_path("results_v3/finetuned_v3", "adapter/adapter_config.json")
OLD_V3_GEN_108_DIR = runtime_path("results_v3/comparison/finetuned__gen_rp_1.08", "generations.json")

ADAPTERS_20 = [
    ("finetuned_v3", OLD_V3_ADAPTER_DIR / "adapter", OUTPUT_DIR / "finetuned_v3__gen_rp_1.00_20"),
    ("finetuned_v4", FINETUNE_DIR / "adapter", OUTPUT_DIR / "finetuned_v4__gen_rp_1.00_20"),
]

for adapter_label, adapter_path, out_20_dir in ADAPTERS_20:
    out_20_dir.mkdir(parents=True, exist_ok=True)
    gen_path = out_20_dir / "generations.json"
    diag_path = out_20_dir / "generation_diagnostics.json"
    raw_rp1_path = out_20_dir / "raw_rp1_generations.json"
    generations = json.loads(gen_path.read_text(encoding="utf-8")) if gen_path.exists() else {}
    diagnostics = json.loads(diag_path.read_text(encoding="utf-8")) if diag_path.exists() else {}
    raw_rp1_gens = json.loads(raw_rp1_path.read_text(encoding="utf-8")) if raw_rp1_path.exists() else {}

    pending_cases = [c for c in cases_20 if not (generations.get(c["case_id"], "").strip() and c["case_id"] in diagnostics)]
    if pending_cases:
        random.seed(SEED)
        torch.manual_seed(SEED)
        base_m = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REVISION, token=token, dtype=dtype).to(device)
        peft_m = PeftModel.from_pretrained(base_m, str(adapter_path), is_trainable=False).eval()
        eos = peft_m.generation_config.eos_token_id
        eos_ids = eos if isinstance(eos, list) else [eos]
        started = time.monotonic()
        for case in cases_20:
            key = case["case_id"]
            if generations.get(key, "").strip() and key in diagnostics:
                continue
            inputs = tokenizer(case["prompt_text"], return_tensors="pt", add_special_tokens=False).to(device)
            n_prompt = inputs.input_ids.shape[1]
            with torch.inference_mode():
                logits = peft_m(**inputs, logits_to_keep=1).logits[:, -1, :]
                finite = bool(torch.isfinite(logits).all().item())
                del logits
                if not finite:
                    raise RuntimeError(f"{adapter_label}/gen_rp_1.00/{key}: non-finite first-token logits")
                gen_kwargs = {"max_new_tokens": MAX_NEW_TOKENS, "do_sample": False, "pad_token_id": pad_id}
                generated = peft_m.generate(**inputs, **gen_kwargs)
                ids_rp1 = generated[0, n_prompt:].tolist()
                text_rp1 = tokenizer.decode(ids_rp1, skip_special_tokens=True)
                raw_rp1_gens[key] = text_rp1
                raw_rp1_path.write_text(json.dumps(raw_rp1_gens, ensure_ascii=False, indent=2), encoding="utf-8")

                hit_budget_rp1 = len(ids_rp1) >= MAX_NEW_TOKENS
                fallback_triggered = False
                final_ids = ids_rp1
                final_text = text_rp1
                if hit_budget_rp1:
                    fallback_triggered = True
                    fb_kwargs = {
                        "max_new_tokens": MAX_NEW_TOKENS,
                        "do_sample": False,
                        "pad_token_id": pad_id,
                        "logits_processor": LogitsProcessorList([GeneratedOnlyRepetitionPenalty(1.08, n_prompt)]),
                    }
                    generated_fb = peft_m.generate(**inputs, **fb_kwargs)
                    final_ids = generated_fb[0, n_prompt:].tolist()
                    final_text = tokenizer.decode(final_ids, skip_special_tokens=True)

            diagnostics[key] = {
                "prompt_tokens": n_prompt,
                "rp1_generated_tokens": len(ids_rp1),
                "rp1_reached_budget": hit_budget_rp1,
                "fallback_to_gen_rp_1.08_triggered": fallback_triggered,
                "generated_tokens": len(final_ids),
                "finite_first_token_logits": finite,
                "empty_output": not final_text.strip(),
                "reached_budget": len(final_ids) >= MAX_NEW_TOKENS,
                "ended_with_eos": bool(final_ids) and final_ids[-1] in eos_ids,
            }
            diag_path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
            generations[key] = final_text
            gen_path.write_text(json.dumps(generations, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{adapter_label} | gen_rp_1.00_20] {len(generations)}/20 {key}: rp1_toks={len(ids_rp1)}, fallback={fallback_triggered}, final_toks={len(final_ids)} ({time.monotonic()-started:.1f}s)", flush=True)
        del peft_m, base_m
        if device == "cuda":
            torch.cuda.empty_cache()

# Score 20-case runs and full 100-case cross-reference comparisons
from scripts.build_v4_notebooks import find_schema_violations

v4_108_dir = OUTPUT_DIR / "finetuned__gen_rp_1.08"
v4_108_gens = json.loads((v4_108_dir / "generations.json").read_text(encoding="utf-8"))
v4_108_diags = json.loads((v4_108_dir / "generation_diagnostics.json").read_text(encoding="utf-8"))

v3_108_gens = json.loads((OLD_V3_GEN_108_DIR / "generations.json").read_text(encoding="utf-8"))
v3_108_diags = json.loads((OLD_V3_GEN_108_DIR / "generation_diagnostics.json").read_text(encoding="utf-8"))

base_108_gens = json.loads((BASELINE_DIR / "gen_rp_1.08/generations.json").read_text(encoding="utf-8"))
base_108_diags = json.loads((BASELINE_DIR / "gen_rp_1.08/generation_diagnostics.json").read_text(encoding="utf-8"))

# Save schema_violations.json for finetuned_v4 (100 cases)
v4_violations = find_schema_violations(cases, v4_108_gens)
(OUTPUT_DIR / "schema_violations.json").write_text(json.dumps(v4_violations, indent=2), encoding="utf-8")

# Also score 100-case finetuned_v3 on v4 references and finetuned_v4 on v3 references for complete controlled comparison
all_100_rows = []
for ref_label, ref_cases in (("v4_regenerated_ref", cases), ("v3_original_ref", cases_100_v3_ref)):
    for m_label, dec_label, g_map, d_map in (
        ("base", "gen_rp_1.08", base_108_gens, base_108_diags),
        ("finetuned_v3", "gen_rp_1.08", v3_108_gens, v3_108_diags),
        ("finetuned_v4", "gen_rp_1.08", v4_108_gens, v4_108_diags),
    ):
        _, s_100 = score_run(ref_cases, g_map, d_map)
        all_100_rows.append({"reference_set": ref_label, "model": m_label, "decoding": dec_label, **s_100})
pd.DataFrame(all_100_rows).to_csv(OUTPUT_DIR / "summary_100_cross_reference.csv", index=False)
(OUTPUT_DIR / "summary_100_cross_reference.json").write_text(json.dumps(all_100_rows, indent=2), encoding="utf-8")

# Score all 20-case runs (base@1.08, v3@1.08, v3@1.00_raw, v3@1.00_fb1.08, v4@1.08, v4@1.00_raw, v4@1.00_fb1.08)
v3_rp1_dir = OUTPUT_DIR / "finetuned_v3__gen_rp_1.00_20"
v4_rp1_dir = OUTPUT_DIR / "finetuned_v4__gen_rp_1.00_20"

v3_rp1_fb_gens = json.loads((v3_rp1_dir / "generations.json").read_text(encoding="utf-8"))
v3_rp1_raw_gens = json.loads((v3_rp1_dir / "raw_rp1_generations.json").read_text(encoding="utf-8"))
v3_rp1_diags = json.loads((v3_rp1_dir / "generation_diagnostics.json").read_text(encoding="utf-8"))
v3_rp1_raw_diags = {k: {**v, "generated_tokens": v["rp1_generated_tokens"], "reached_budget": v["rp1_reached_budget"]} for k, v in v3_rp1_diags.items()}

v4_rp1_fb_gens = json.loads((v4_rp1_dir / "generations.json").read_text(encoding="utf-8"))
v4_rp1_raw_gens = json.loads((v4_rp1_dir / "raw_rp1_generations.json").read_text(encoding="utf-8"))
v4_rp1_diags = json.loads((v4_rp1_dir / "generation_diagnostics.json").read_text(encoding="utf-8"))
v4_rp1_raw_diags = {k: {**v, "generated_tokens": v["rp1_generated_tokens"], "reached_budget": v["rp1_reached_budget"]} for k, v in v4_rp1_diags.items()}

# Save per_case.csv and aggregate.json inside each 20-case folder (against v4 regenerated references)
for folder, g_map, d_map in ((v3_rp1_dir, v3_rp1_fb_gens, v3_rp1_diags), (v4_rp1_dir, v4_rp1_fb_gens, v4_rp1_diags)):
    df_20, sum_20 = score_run(cases_20, g_map, d_map)
    sum_20["fallback_triggered_cases"] = sum(1 for c in cases_20 if d_map[c["case_id"]].get("fallback_to_gen_rp_1.08_triggered"))
    df_20.to_csv(folder / "per_case.csv", index=False)
    (folder / "aggregate.json").write_text(json.dumps(sum_20, indent=2), encoding="utf-8")

ablation_20_rows = []
for ref_label, ref_cases_20 in (("v4_regenerated_ref", cases_20), ("v3_original_ref", cases_20_v3_ref)):
    for m_label, dec_label, g_map, d_map, fb_count in (
        ("base", "gen_rp_1.08", base_108_gens, base_108_diags, 0),
        ("finetuned_v3", "gen_rp_1.08", v3_108_gens, v3_108_diags, 0),
        ("finetuned_v3", "gen_rp_1.00_raw", v3_rp1_raw_gens, v3_rp1_raw_diags, 0),
        ("finetuned_v3", "gen_rp_1.00_fb1.08", v3_rp1_fb_gens, v3_rp1_diags, sum(1 for c in cases_20 if v3_rp1_diags[c["case_id"]].get("fallback_to_gen_rp_1.08_triggered"))),
        ("finetuned_v4", "gen_rp_1.08", v4_108_gens, v4_108_diags, 0),
        ("finetuned_v4", "gen_rp_1.00_raw", v4_rp1_raw_gens, v4_rp1_raw_diags, 0),
        ("finetuned_v4", "gen_rp_1.00_fb1.08", v4_rp1_fb_gens, v4_rp1_diags, sum(1 for c in cases_20 if v4_rp1_diags[c["case_id"]].get("fallback_to_gen_rp_1.08_triggered"))),
    ):
        _, s_20 = score_run(ref_cases_20, g_map, d_map)
        s_20["fallback_triggered_cases"] = fb_count
        ablation_20_rows.append({"reference_set": ref_label, "model": m_label, "decoding": dec_label, **s_20})

ablation_20_df = pd.DataFrame(ablation_20_rows)
ablation_20_df.to_csv(OUTPUT_DIR / "ablation_20_decoding_comparison.csv", index=False)
(OUTPUT_DIR / "ablation_20_decoding_comparison.json").write_text(json.dumps(ablation_20_rows, indent=2), encoding="utf-8")
display(ablation_20_df)

# Refresh comparison.zip archive so it includes the 20-case gen_rp_1.00 folders and cross-reference tables
archive = shutil.make_archive(str(OUTPUT_DIR.resolve()), "zip", root_dir=OUTPUT_DIR.parent, base_dir=OUTPUT_DIR.name)
print("Updated comparison archive with 20-case gen_rp_1.00 ablation:", archive, flush=True)
"""
    compile(ablation_code, str(destination / "03_eval_and_compare.ipynb"), "exec")
    nb03["cells"].append(cell("markdown", ablation_md))
    nb03["cells"].append(cell("code", ablation_code))
    (destination / "03_eval_and_compare.ipynb").write_text(json.dumps(nb03, indent=1, ensure_ascii=False), encoding="utf-8")
    return destination


def main():
    contract = prepare_baseline(ROOT)
    destination = build_notebooks(ROOT)
    print(f"Prepared results_v4/baseline (version={contract['dataset_version']}) and notebooks at {destination}")


if __name__ == "__main__":
    main()
