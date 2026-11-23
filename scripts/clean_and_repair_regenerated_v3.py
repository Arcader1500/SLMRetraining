"""Deterministic hygiene cleaning and targeted Gemini repair for v3_regenerated_gemini_3_8_flash."""
import argparse
import concurrent.futures
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.phase_results import ROOT
from scripts.prepare_v2_dataset import DICT_KEYS, LIST_KEYS, MISSING_TOKENS, STRING_KEYS
from scripts.prepare_v3_dataset import SCHEMA, schema_valid
from scripts.regenerate_v3_labels_batch import (
    DEFAULT_MODEL,
    DEFAULT_OUT_DIR,
    DEFAULT_SOURCE_DIR,
    get_gemini_client,
    load_source_rows,
    now_str,
)

EXTRA_MISSING_TOKENS = set(MISSING_TOKENS) | {
    "n/a",
    "na",
    "not specified",
    "not mentioned",
    "unspecified",
    "not applicable",
    "patient name",
}

REPAIR_SYSTEM_PROMPT = (
    "You are a precise clinical information extraction system. Extract ONLY clinical facts "
    "explicitly stated in the supplied clinical note into one JSON object matching the schema.\n\n"
    "Strict rules:\n"
    "1. Source authority: Use ONLY facts explicitly stated in the note. Never infer missing facts, "
    "standard care, or outside knowledge. Never emit placeholder text (e.g., 'N/A', 'None', 'unknown', 'not specified').\n"
    "2. Cut-off notes: If a sentence or note is truncated/cut off mid-thought, extract only facts "
    "established before the cut-off. NEVER complete or guess truncated words, units, procedures, or outcomes.\n"
    "3. Clinical roles & required pairings:\n"
    "   - admission: Populate ONLY when the note explicitly indicates an inpatient hospital admission (require 'reason').\n"
    "   - surgeries: Performed surgical/operative procedures only (require 'Type'; include 'time' and 'details' when stated).\n"
    "   - symptoms: Require 'name of symptom'. CRITICAL NEGATION RULE: When a symptom is explicitly denied/absent in the note "
    "(e.g., 'no fever, chest tightness, or weight loss'), either prefix 'name of symptom' with 'no ' (e.g., 'no fever') "
    "OR explicitly state 'absent' / 'denied' in 'details'. NEVER list a denied symptom as an affirmative symptom without negation.\n"
    "   - medical examinations: Physical exams and vital signs. Every entry MUST include BOTH 'name' AND 'result'.\n"
    "   - diagnosis tests: Imaging, labs, pathology, and diagnostic procedures. Every entry MUST include BOTH 'test' (concise test name only) "
    "AND 'result' (the findings/values). NEVER stuff findings into 'test' and never emit a test without its result.\n"
    "   - treatments: Medications, therapies, and planned/refused procedures (require 'name'; fold frequency/duration into 'dosage' or 'time'; "
    "fold planned/refused status into 'reaction to treatment').\n"
    "   - patient medical history: Distinguish the patient's own history from family/maternal history.\n"
    "4. No synonym lists or billing codes: Write concise, direct clinical strings. NEVER output slash-separated synonym variants "
    "(e.g., 'test A / test B / test C'), CPT billing codes, or internal commentary.\n"
    "5. Schema rules: Include all 10 top-level keys. Use [] for empty arrays, {} for empty objects, "
    "and \"None\" only for absent visit motivation. Omit missing optional inner fields; do not repeat identical entries."
)


def build_strict_response_schema():
    """Enforce required identity & result keys on list items so tests/exams never drop results or emit empty dicts."""
    return {
        "type": "OBJECT",
        "required": list(SCHEMA.keys()),
        "properties": {
            "visit motivation": {"type": "STRING"},
            "admission": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["reason"],
                    "properties": {"reason": {"type": "STRING"}},
                },
            },
            "patient information": {
                "type": "OBJECT",
                "properties": {"age": {"type": "STRING"}, "sex": {"type": "STRING"}},
            },
            "patient medical history": {
                "type": "OBJECT",
                "properties": {"physiological context": {"type": "STRING"}},
            },
            "surgeries": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["Type"],
                    "properties": {
                        "Type": {"type": "STRING"},
                        "time": {"type": "STRING"},
                        "details": {"type": "STRING"},
                    },
                },
            },
            "symptoms": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["name of symptom"],
                    "properties": {
                        "name of symptom": {"type": "STRING"},
                        "location": {"type": "STRING"},
                        "time": {"type": "STRING"},
                        "details": {"type": "STRING"},
                    },
                },
            },
            "medical examinations": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["name", "result"],
                    "properties": {"name": {"type": "STRING"}, "result": {"type": "STRING"}},
                },
            },
            "diagnosis tests": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["test", "result"],
                    "properties": {"test": {"type": "STRING"}, "result": {"type": "STRING"}},
                },
            },
            "treatments": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "STRING"},
                        "dosage": {"type": "STRING"},
                        "time": {"type": "STRING"},
                        "reaction to treatment": {"type": "STRING"},
                    },
                },
            },
            "discharge": {
                "type": "OBJECT",
                "properties": {"discharge summary": {"type": "STRING"}},
            },
        },
    }


def is_placeholder_scalar(val):
    if val is None:
        return True
    norm = " ".join(str(val).strip().casefold().split())
    return norm in EXTRA_MISSING_TOKENS


def deterministic_clean_v3_obj(obj: dict) -> tuple[dict, list[str]]:
    """Strip empty strings, placeholders, empty dicts, and duplicate list items while preserving 30-path schema."""
    repairs = []
    cleaned = {}
    for parent, allowed_fields in SCHEMA.items():
        val = obj.get(parent)
        if parent == "visit motivation":
            if not isinstance(val, str) or is_placeholder_scalar(val):
                if val != "None":
                    repairs.append("normalized_empty_visit_motivation_to_None")
                cleaned[parent] = "None"
            else:
                cleaned[parent] = val.strip()
        elif parent in DICT_KEYS:
            if not isinstance(val, dict):
                cleaned[parent] = {}
            else:
                d = {}
                for k in allowed_fields:
                    if k in val and isinstance(val[k], str):
                        v_str = val[k].strip()
                        if is_placeholder_scalar(v_str):
                            repairs.append(f"stripped_placeholder_{parent}.{k}")
                        else:
                            d[k] = v_str
                cleaned[parent] = d
        elif parent in LIST_KEYS:
            if not isinstance(val, list):
                cleaned[parent] = []
            else:
                items = []
                seen_sigs = set()
                for item in val:
                    if not isinstance(item, dict):
                        continue
                    d = {}
                    for k in allowed_fields:
                        if k in item and isinstance(item[k], str):
                            v_str = item[k].strip()
                            if is_placeholder_scalar(v_str):
                                repairs.append(f"stripped_placeholder_{parent}.{k}")
                            else:
                                d[k] = v_str
                    if not d:
                        repairs.append(f"removed_empty_dict_in_{parent}")
                        continue
                    sig = json.dumps(d, ensure_ascii=False, sort_keys=True)
                    if sig in seen_sigs:
                        repairs.append(f"deduped_item_in_{parent}")
                        continue
                    seen_sigs.add(sig)
                    items.append(d)
                cleaned[parent] = items
    assert schema_valid(cleaned), "Cleaned object failed schema_valid"
    return cleaned, repairs


SELFTALK_PATTERNS = re.compile(
    r"(_placeholder_|_fix:|keep_strict_|shortened to:|all relevant codes combined:|result\s*=\s*\"|Findings:\s*.*\s*result details:)",
    re.IGNORECASE,
)


def check_semantic_hygiene_defects(obj: dict, note: str = "") -> list[str]:
    """Return list of structural/semantic defects that require re-prompting the teacher."""
    reasons = []

    # 1. Check for model self-talk, slash synonym loops, or extreme single-leaf bloat
    for parent, allowed_fields in SCHEMA.items():
        val = obj.get(parent)
        entries = [val] if isinstance(val, dict) else (val if isinstance(val, list) else [])
        if parent == "visit motivation" and isinstance(val, str):
            entries = [{"visit motivation": val}]
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            for k, v in entry.items():
                if not isinstance(v, str):
                    continue
                if SELFTALK_PATTERNS.search(v):
                    reasons.append(f"selftalk_in_{parent}[{idx}].{k}")
                # Check slash-separated synonym stuffing (e.g. "A / B / C / D" with spaces around slashes)
                if v.count(" / ") >= 3 or v.count("/") >= 8:
                    reasons.append(f"slash_synonym_loop_in_{parent}[{idx}].{k}")
                # Check excessive leaf length in test/name/time/age/sex fields
                if k in ("test", "name", "Type", "name of symptom", "time", "location", "age", "sex") and len(v) > 220:
                    reasons.append(f"overlong_identifier_field_{parent}[{idx}].{k}_len_{len(v)}")
                elif len(v) > 1200:
                    reasons.append(f"extreme_leaf_length_{parent}[{idx}].{k}_len_{len(v)}")

    # 2. Check for diagnosis tests or medical examinations missing result or test/name
    for idx, item in enumerate(obj.get("diagnosis tests", [])):
        if "test" not in item or "result" not in item:
            reasons.append(f"missing_test_or_result_in_diagnosis_tests[{idx}]")
    for idx, item in enumerate(obj.get("medical examinations", [])):
        if "name" not in item or "result" not in item:
            reasons.append(f"missing_name_or_result_in_medical_examinations[{idx}]")

    # 3. Check for surgeries/symptoms/treatments/admission missing their primary identifier key
    for sec, id_key in [("admission", "reason"), ("surgeries", "Type"), ("symptoms", "name of symptom"), ("treatments", "name")]:
        for idx, item in enumerate(obj.get(sec, [])):
            if id_key not in item:
                reasons.append(f"missing_{id_key}_in_{sec}[{idx}]")

    # 4. Check for unnegated symptom explosion from "No A, B, C, or D" sentences in the note
    if note:
        neg_lists = re.findall(r"\b(?:[Nn]o|[Dd]enied|[Ww]ithout|[Aa]bsence of)\s+([A-Za-z0-9\s,\-]{15,140}?)(?:\.|;|\n)", note)
        if neg_lists:
            neg_clause_text = " ".join(neg_lists).casefold()
            unnegated_hits = 0
            for item in obj.get("symptoms", []):
                sname = item.get("name of symptom", "").strip().casefold()
                sdet = item.get("details", "").strip().casefold()
                if not sname or len(sname) < 4:
                    continue
                has_neg_marker = any(w in sname or w in sdet for w in ("no ", "not ", "none", "absent", "denied", "negative", "without", "free of"))
                if not has_neg_marker and re.search(r"\b" + re.escape(sname) + r"\b", neg_clause_text):
                    # Verify it isn't also positively affirmed elsewhere in the note
                    note_without_neg = note.casefold()
                    for nl in neg_lists:
                        note_without_neg = note_without_neg.replace(nl.casefold(), "")
                    if not re.search(r"\b" + re.escape(sname) + r"\b", note_without_neg):
                        unnegated_hits += 1
            if unnegated_hits >= 2:
                reasons.append(f"unnegated_symptom_decomposition_hits_{unnegated_hits}")

    return reasons


def load_jsonl(path: Path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def repair_single_case(client, model: str, strict_schema: dict, row: dict, defect_reasons: list[str], max_retries: int = 3):
    from google.genai import types

    cid = row["case_id"]
    note = row["note"]
    user_prompt = (
        f"Clinical note:\n{note}\n\n"
        f"(Verification note: ensure every 'diagnosis tests' item has both a concise 'test' name and a 'result', "
        f"every 'medical examinations' item has both 'name' and 'result', preserve negation on denied symptoms, "
        f"and never output slash-separated synonym lists.)"
    )

    for attempt in range(1, max_retries + 1):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=REPAIR_SYSTEM_PROMPT,
                    temperature=0.0,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                    response_schema=strict_schema,
                    thinking_config=types.ThinkingConfig(thinking_budget=512),
                ),
            )
            text = resp.text or ""
            if not text.strip():
                raise ValueError("Empty response text")
            raw_obj = json.loads(text)
            cleaned_obj, _ = deterministic_clean_v3_obj(raw_obj)
            new_defects = check_semantic_hygiene_defects(cleaned_obj, note)
            if new_defects:
                # If only a mildly long identifier (>220 but <350 chars) remains on a complex test, allow on final attempt
                severe = [d for d in new_defects if not d.startswith("overlong_identifier_field_")]
                if severe or attempt < max_retries:
                    raise ValueError(f"Still has defects: {new_defects}")
            return cid, json.dumps(cleaned_obj, ensure_ascii=False, separators=(",", ":")), None
        except Exception as exc:
            if attempt == max_retries:
                return cid, None, str(exc)
            time.sleep(1.5 * attempt)
    return cid, None, "Exhausted retries"


def run_clean_and_repair(out_dir: Path, model: str, workers: int = 12, dry_run_only: bool = False):
    splits = {
        "train": load_jsonl(out_dir / "regenerated_train.jsonl"),
        "validation": load_jsonl(out_dir / "regenerated_validation.jsonl"),
    }

    deterministic_repairs_count = 0
    cases_with_deterministic_repairs = 0
    flagged_for_reprompt = []

    for split, rows in splits.items():
        for r in rows:
            obj = json.loads(r["reference"])
            cleaned_obj, d_repairs = deterministic_clean_v3_obj(obj)
            if d_repairs:
                deterministic_repairs_count += len(d_repairs)
                cases_with_deterministic_repairs += 1
                r["reference"] = json.dumps(cleaned_obj, ensure_ascii=False, separators=(",", ":"))
            defects = check_semantic_hygiene_defects(cleaned_obj, r["note"])
            if defects:
                flagged_for_reprompt.append((split, r, defects))

    print(
        f"[{now_str()}] Deterministic clean pass: fixed {deterministic_repairs_count} leaf/list defects across {cases_with_deterministic_repairs} cases.",
        flush=True,
    )
    print(
        f"[{now_str()}] Cases flagged for targeted strict-schema re-generation: {len(flagged_for_reprompt)} "
        f"(train={sum(1 for s, _, _ in flagged_for_reprompt if s == 'train')}, "
        f"val={sum(1 for s, _, _ in flagged_for_reprompt if s == 'validation')})",
        flush=True,
    )

    if dry_run_only:
        return

    client = get_gemini_client()
    strict_schema = build_strict_response_schema()

    repaired_by_cid = {}
    failed_repairs = []

    if flagged_for_reprompt:
        print(f"[{now_str()}] Running parallel targeted repair with {workers} workers on {model} ...", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(repair_single_case, client, model, strict_schema, r, defects): (split, r["case_id"], defects)
                for split, r, defects in flagged_for_reprompt
            }
            done_cnt = 0
            for fut in concurrent.futures.as_completed(futures):
                split, cid, defects = futures[fut]
                done_cnt += 1
                _, new_ref, err = fut.result()
                if new_ref is not None:
                    repaired_by_cid[cid] = new_ref
                else:
                    failed_repairs.append({"case_id": cid, "split": split, "defects": defects, "error": err})
                if done_cnt % 25 == 0 or done_cnt == len(flagged_for_reprompt):
                    print(
                        f"[{now_str()}] Progress: {done_cnt}/{len(flagged_for_reprompt)} | repaired={len(repaired_by_cid)} | failed={len(failed_repairs)}",
                        flush=True,
                    )

    # Save cleaned + repaired rows back to regenerated_train.jsonl and regenerated_validation.jsonl
    remaining_defects_after = []
    for split, rows in splits.items():
        out_path = out_dir / f"regenerated_{split}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for r in rows:
                cid = r["case_id"]
                if cid in repaired_by_cid:
                    r["reference"] = repaired_by_cid[cid]
                # Final deterministic pass
                final_obj, _ = deterministic_clean_v3_obj(json.loads(r["reference"]))
                r["reference"] = json.dumps(final_obj, ensure_ascii=False, separators=(",", ":"))
                rem = check_semantic_hygiene_defects(final_obj, r["note"])
                if rem:
                    remaining_defects_after.append({"case_id": cid, "defects": rem})
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    report = {
        "completed_at_utc": now_str(),
        "model": model,
        "deterministic_repairs_count": deterministic_repairs_count,
        "cases_with_deterministic_repairs": cases_with_deterministic_repairs,
        "cases_flagged_for_reprompt": len(flagged_for_reprompt),
        "cases_successfully_repaired": len(repaired_by_cid),
        "failed_repairs_count": len(failed_repairs),
        "failed_repairs": failed_repairs,
        "remaining_defects_after_count": len(remaining_defects_after),
        "remaining_defects_after": remaining_defects_after[:25],
    }
    report_path = out_dir / "clean_and_repair_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{now_str()}] Wrote repair report to {report_path}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_clean_and_repair(args.out_dir, args.model, workers=args.workers, dry_run_only=args.dry_run)


if __name__ == "__main__":
    main()
