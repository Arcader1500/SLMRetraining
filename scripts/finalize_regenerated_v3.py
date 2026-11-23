"""Finalize v3_regenerated_gemini_3_8_flash:
1. Fix narrow-scope unnegated symptoms (stopping at contrast/verb boundaries like 'but', 'although', 'with', 'apart from').
2. Unify negated symptom representation so 'name of symptom' never states a denied symptom as a bare affirmative noun, and strip 'time': 'no'.
3. Repair validation:106's missing diagnosis test result via Gemini 3.8 Flash.
4. Run full 1,425-row verification and write final_verification_report.json.
"""
import json
import re
from collections import Counter
from pathlib import Path

from scripts.clean_and_repair_regenerated_v3 import (
    REPAIR_SYSTEM_PROMPT,
    build_strict_response_schema,
    check_semantic_hygiene_defects,
    deterministic_clean_v3_obj,
    load_jsonl,
)
from scripts.phase_results import ROOT
from scripts.prepare_v3_dataset import SCHEMA, schema_valid
from scripts.regenerate_v3_labels_batch import DEFAULT_MODEL, DEFAULT_OUT_DIR, get_gemini_client, now_str

NEG_MARKERS = ("no ", "not ", "none", "absent", "denied", "denies", "negative", "without", "free of", "absence of", "ruled out", "asymptomatic")
PURE_NEG_VALUES = {"no", "none", "absent", "denied", "not observed", "not present", "negative", "nil", "no history", "no difficulty"}

# Stop negation clause at contrast words or presentation verbs
CLAUSE_BOUNDARY = re.compile(
    r"\b(?:but|although|though|however|while|whereas|apart from|except|with history of|with complaints of|with a chief complaint of|came to|presented|visited|was admitted|complained of|complaining of|endorsed|experienced|reported|developed|showed|revealed|demonstrated)\b|[.;:\n]",
    re.IGNORECASE,
)
NEG_CUE_START = re.compile(
    r"\b(?:no|denied|denies|without|negative for|absence of|free of|free from|ruled out)\s+",
    re.IGNORECASE,
)


def extract_true_negated_spans(note: str) -> list[str]:
    """Extract narrow text spans governed by a negation cue, stopping at the first contrast/presentation boundary."""
    spans = []
    for m in NEG_CUE_START.finditer(note):
        start = m.end()
        tail = note[start : start + 160]
        b = CLAUSE_BOUNDARY.search(tail)
        span = tail[: b.start()] if b else tail
        span = span.strip()
        # Exclude medical history / comorbidity phrases that aren't symptom lists
        if span.casefold().startswith(("past medical history", "prior medical history", "significant history", "any co-morbid", "co-morbid", "family history", "known history of")):
            continue
        if len(span) >= 3:
            spans.append(span)
    return spans


def has_neg_word(text: str) -> bool:
    t = text.strip().casefold()
    if t in PURE_NEG_VALUES:
        return True
    return any(t.startswith(m) or f" {m.strip()}" in f" {t}" for m in NEG_MARKERS)


def normalize_and_fix_symptoms(obj: dict, note: str) -> tuple[dict, list[str]]:
    """Enforce single unified negation convention on symptoms and catch narrow-scope unnegated symptoms."""
    changes = []
    neg_spans = extract_true_negated_spans(note)
    neg_spans_low = " ; ".join(neg_spans).casefold()
    note_low = note.casefold()

    # Build note text with true negated spans removed, to check if a symptom is positively affirmed elsewhere
    note_without_neg = note_low
    for sp in neg_spans:
        note_without_neg = note_without_neg.replace(sp.casefold(), " ")

    new_symptoms = []
    seen_sigs = set()
    for idx, item in enumerate(obj.get("symptoms", [])):
        item = dict(item)
        sname = item.get("name of symptom", "").strip()
        sdet = item.get("details", "").strip()
        stime = item.get("time", "").strip()

        if not sname:
            continue

        # 1. If time is literally "no" or "none" (like train:884), move negation to name/details and delete time
        if stime.casefold() in {"no", "none", "absent", "denied"}:
            del item["time"]
            if not has_neg_word(sname):
                sname = f"no {sname}"
                item["name of symptom"] = sname
            changes.append(f"fixed_misplaced_negation_in_time:{sname}")

        # 2. Check if details indicates pure negation ("no", "denied", "absent", "not observed", etc.)
        # Unified convention: ensure `name of symptom` itself starts with "no " (unless it already has a negation marker)
        # so that `name of symptom` is NEVER a bare affirmative symptom name when the symptom was actually denied!
        name_is_neg = has_neg_word(sname)
        det_is_neg = has_neg_word(sdet)

        if det_is_neg and not name_is_neg:
            # Check if details is purely a negation marker (e.g. "no", "denied", "absent", "not observed", "no history", "no difficulty")
            if sdet.casefold() in PURE_NEG_VALUES or sdet.casefold().startswith(("no ", "denied", "absent", "not observed", "negative")):
                sname = f"no {sname}"
                item["name of symptom"] = sname
                name_is_neg = True
                changes.append(f"unified_negation_prefix_from_details:{sname}")

        # 3. Check if an unnegated symptom appears inside a true narrow negation span in the note and is NOT affirmed elsewhere
        if not name_is_neg and not det_is_neg and len(sname) >= 4 and neg_spans_low:
            sname_low = sname.casefold()
            if re.search(r"\b" + re.escape(sname_low) + r"\b", neg_spans_low):
                if not re.search(r"\b" + re.escape(sname_low) + r"\b", note_without_neg):
                    sname = f"no {sname}"
                    item["name of symptom"] = sname
                    changes.append(f"repaired_narrow_scope_unnegated_symptom:{sname}")

        sig = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if sig not in seen_sigs:
            seen_sigs.add(sig)
            new_symptoms.append(item)

    obj["symptoms"] = new_symptoms
    return obj, changes


def main():
    out_dir = DEFAULT_OUT_DIR
    splits = {
        "train": load_jsonl(out_dir / "regenerated_train.jsonl"),
        "validation": load_jsonl(out_dir / "regenerated_validation.jsonl"),
    }

    # Check if any case still has missing_test_or_result or missing_name_or_result (e.g. validation:106)
    client = None
    strict_schema = build_strict_response_schema()

    total_symptom_changes = Counter()
    cases_modified = 0
    reprompted_cases = []

    for split, rows in splits.items():
        for r in rows:
            cid = r["case_id"]
            note = r["note"]
            obj = json.loads(r["reference"])

            # Check if test/exam result is missing (like validation:106)
            needs_api = any("test" not in x or "result" not in x for x in obj.get("diagnosis tests", [])) or any(
                "name" not in x or "result" not in x for x in obj.get("medical examinations", [])
            )
            if needs_api:
                if client is None:
                    client = get_gemini_client()
                from google.genai import types

                resp = client.models.generate_content(
                    model=DEFAULT_MODEL,
                    contents=f"Clinical note:\n{note}",
                    config=types.GenerateContentConfig(
                        system_instruction=REPAIR_SYSTEM_PROMPT,
                        temperature=0.0,
                        max_output_tokens=8192,
                        response_mime_type="application/json",
                        response_schema=strict_schema,
                        thinking_config=types.ThinkingConfig(thinking_budget=512),
                    ),
                )
                obj = json.loads(resp.text)
                reprompted_cases.append(cid)

            obj, _ = deterministic_clean_v3_obj(obj)
            obj, sym_changes = normalize_and_fix_symptoms(obj, note)
            obj, _ = deterministic_clean_v3_obj(obj)

            if sym_changes or cid in reprompted_cases:
                cases_modified += 1
                for c in sym_changes:
                    kind = c.split(":")[0]
                    total_symptom_changes[kind] += 1

            assert schema_valid(obj), f"{cid} failed schema_valid"
            r["reference"] = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

        # Write back
        out_path = out_dir / f"regenerated_{split}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Final verification across all 1,425 rows
    remaining_issues = []
    neg_convention_after = Counter()
    for split, rows in splits.items():
        for r in rows:
            cid = r["case_id"]
            obj = json.loads(r["reference"])
            # Check structural/test/selftalk defects (ignoring the old overly broad regex)
            defects = [
                d
                for d in check_semantic_hygiene_defects(obj, "")
                if not d.startswith("overlong_identifier_field_")
            ]
            if defects:
                remaining_issues.append({"case_id": cid, "defects": defects})

            # Check narrow-scope unnegated symptoms
            neg_spans = extract_true_negated_spans(r["note"])
            neg_spans_low = " ; ".join(neg_spans).casefold()
            note_without_neg = r["note"].casefold()
            for sp in neg_spans:
                note_without_neg = note_without_neg.replace(sp.casefold(), " ")

            for s in obj.get("symptoms", []):
                sn = s.get("name of symptom", "").strip()
                sd = s.get("details", "").strip()
                n_neg = has_neg_word(sn)
                d_neg = has_neg_word(sd)
                if n_neg or d_neg:
                    if n_neg and not d_neg:
                        neg_convention_after["negation_in_name_only"] += 1
                    elif n_neg and d_neg:
                        neg_convention_after["negation_in_both_name_and_details"] += 1
                    else:
                        neg_convention_after["negation_in_details_qualifier"] += 1
                elif len(sn) >= 4 and neg_spans_low:
                    if re.search(r"\b" + re.escape(sn.casefold()) + r"\b", neg_spans_low) and not re.search(
                        r"\b" + re.escape(sn.casefold()) + r"\b", note_without_neg
                    ):
                        remaining_issues.append({"case_id": cid, "defects": [f"narrow_unnegated_symptom:{sn}"]})

    summary = {
        "completed_at_utc": now_str(),
        "total_rows_verified": sum(len(v) for v in splits.values()),
        "split_counts": {k: len(v) for k, v in splits.items()},
        "reprompted_cases": reprompted_cases,
        "cases_with_symptom_negation_normalization": cases_modified,
        "symptom_normalization_counts": dict(total_symptom_changes),
        "negation_convention_after": dict(neg_convention_after),
        "remaining_severe_issues_count": len(remaining_issues),
        "remaining_severe_issues": remaining_issues[:20],
    }
    report_path = out_dir / "final_verification_report.json"
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
