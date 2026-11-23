"""Assemble, submit, poll, and validate Gemini Batch API regeneration for v3 (1,325 train + 100 val)."""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.phase_results import ROOT, read_json
from scripts.prepare_v3_dataset import SCHEMA, schema_valid

DEFAULT_SOURCE_DIR = ROOT / "prepared_clinical_dataset" / "e80798edebe5aba5"
DEFAULT_OUT_DIR = ROOT / "prepared_clinical_dataset" / "v3_regenerated_gemini_3_8_flash"
DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_POLL_SECONDS = 1800  # 30 minutes

REGENERATION_SYSTEM_PROMPT = (
    "You are a precise clinical information extraction system. Extract ONLY clinical facts "
    "explicitly stated in the supplied clinical note into one JSON object matching the schema.\n\n"
    "Strict rules:\n"
    "1. Source authority: Use ONLY facts explicitly stated in the note. Never infer missing facts, "
    "standard care, or outside knowledge. Never emit placeholder text (e.g., 'N/A', 'None', 'Patient Name').\n"
    "2. Cut-off notes: If a sentence or note is truncated/cut off mid-thought, extract only facts "
    "established before the cut-off. NEVER complete or guess truncated words, units, procedures, or outcomes.\n"
    "3. Clinical roles:\n"
    "   - admission: Populate ONLY when the note explicitly indicates an inpatient hospital admission "
    "(not an outpatient/clinic visit, ED visit without admission, or distant past event).\n"
    "   - surgeries: Performed surgical/operative procedures only (use Type, time, details; include status if needed).\n"
    "   - treatments: Medications, therapies, and discussed/planned/non-surgical procedures "
    "(fold frequency/duration into dosage or time; fold status like planned/refused into name or reaction to treatment).\n"
    "   - patient medical history: Distinguish the patient's own history from family/maternal history.\n"
    "4. Linkage & negation: Keep exact drug-dose-time-reaction and test-result pairings intact. "
    "Preserve explicit negations (e.g., 'no fever', 'negative for...') and uncertainty ('suspected', 'possible').\n"
    "5. Schema rules: Include all 10 top-level keys. Use [] for empty arrays, {} for empty objects, "
    "and \"None\" only for absent visit motivation. Omit missing inner fields; do not add extra keys or duplicate identical items."
)


def build_response_schema():
    """Return a Gemini-compatible JSON Schema dict for the 30-path v3 schema."""
    return {
        "type": "OBJECT",
        "required": list(SCHEMA.keys()),
        "properties": {
            "visit motivation": {"type": "STRING"},
            "admission": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
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
                    "properties": {"name": {"type": "STRING"}, "result": {"type": "STRING"}},
                },
            },
            "diagnosis tests": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {"test": {"type": "STRING"}, "result": {"type": "STRING"}},
                },
            },
            "treatments": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
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


def load_source_rows(source_dir: Path):
    rows = []
    for split in ("train", "validation"):
        path = source_dir / f"{split}.jsonl"
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                rows.append((split, row))
    return rows


def assemble_batch_jsonl(source_dir: Path, out_dir: Path, max_output_tokens: int = 4096):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_source_rows(source_dir)
    response_schema = build_response_schema()
    requests_path = out_dir / "batch_requests.jsonl"

    seen_keys = set()
    total_chars = 0
    split_counts = {"train": 0, "validation": 0}
    sample_request = None

    with requests_path.open("w", encoding="utf-8") as handle:
        for split, row in rows:
            case_id = row["case_id"]
            if case_id in seen_keys:
                raise ValueError(f"Duplicate case_id: {case_id}")
            seen_keys.add(case_id)
            split_counts[split] += 1

            user_text = f"Clinical note:\n{row['note']}"
            total_chars += len(REGENERATION_SYSTEM_PROMPT) + len(user_text)

            entry = {
                "key": case_id,
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": user_text}]}],
                    "system_instruction": {"parts": [{"text": REGENERATION_SYSTEM_PROMPT}]},
                    "generation_config": {
                        "temperature": 0.0,
                        "max_output_tokens": max_output_tokens,
                        "response_mime_type": "application/json",
                        "response_schema": response_schema,
                    },
                },
            }
            if sample_request is None:
                sample_request = entry
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "requests_path": requests_path,
        "total_requests": len(rows),
        "split_counts": split_counts,
        "approx_input_tokens": int(total_chars / 4),
        "file_size_mb": round(requests_path.stat().st_size / (1024 * 1024), 2),
        "sample_key": sample_request["key"] if sample_request else None,
    }


def dry_run(source_dir: Path, out_dir: Path, model: str):
    info = assemble_batch_jsonl(source_dir, out_dir)
    print("=== DRY RUN: Gemini Batch Request Assembly ===")
    print(f"Source dataset : {source_dir}")
    print(f"Target model   : {model}")
    print(f"Output JSONL   : {info['requests_path']} ({info['file_size_mb']} MB)")
    print(f"Request counts : train={info['split_counts']['train']}, validation={info['split_counts']['validation']}, total={info['total_requests']}")
    print(f"Est. input tok : ~{info['approx_input_tokens']:,} tokens (chars/4 rough estimate, excluding schema overhead)")
    assert info["split_counts"] == {"train": 1325, "validation": 100}, f"Unexpected counts: {info['split_counts']}"
    # Validate every JSONL line parses cleanly
    with info["requests_path"].open(encoding="utf-8") as handle:
        for idx, line in enumerate(handle, 1):
            obj = json.loads(line)
            assert "key" in obj and "request" in obj, f"Line {idx} missing key/request"
    print("Dry run checks PASSED: 1,425 valid JSONL requests ready.")
    return info


def get_gemini_client():
    from dotenv import load_dotenv
    from google import genai

    load_dotenv(ROOT / ".env.local")
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in .env.local or the process environment.")
    return genai.Client(api_key=key)


def now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def save_job_state(job_path: Path, batch_job, model: str):
    state_name = getattr(batch_job.state, "name", str(batch_job.state))
    payload = {
        "job_name": batch_job.name,
        "model": model,
        "state": state_name,
        "updated_at_utc": now_str(),
        "dest_file": getattr(getattr(batch_job, "dest", None), "file_name", None),
        "error": str(getattr(batch_job, "error", None)) if getattr(batch_job, "error", None) else None,
    }
    job_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return state_name


def extract_text_from_response(resp_obj):
    candidates = resp_obj.get("candidates") or []
    if not candidates:
        return None, "No candidates in response"
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    if not text.strip():
        return None, f"Empty text (finishReason={candidates[0].get('finishReason')})"
    return text, None


def process_results(client, batch_job, source_dir: Path, out_dir: Path):
    dest_file = getattr(getattr(batch_job, "dest", None), "file_name", None)
    if not dest_file:
        raise RuntimeError("Batch job succeeded but dest.file_name is missing.")

    print(f"[{now_str()}] Downloading batch results from {dest_file} ...", flush=True)
    raw_bytes = client.files.download(file=dest_file)
    responses_path = out_dir / "batch_responses.jsonl"
    responses_path.write_bytes(raw_bytes)

    parsed_by_key = {}
    failures = []
    with responses_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            key = item.get("key")
            if item.get("error"):
                failures.append({"case_id": key, "stage": "api_error", "error": item["error"]})
                continue
            text, err = extract_text_from_response(item.get("response") or {})
            if err:
                failures.append({"case_id": key, "stage": "empty_response", "error": err})
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                failures.append({"case_id": key, "stage": "json_decode", "error": str(exc), "raw": text[:500]})
                continue
            if not schema_valid(obj):
                failures.append({"case_id": key, "stage": "schema_valid", "error": "Failed 30-path schema_valid", "raw": text[:500]})
                continue
            parsed_by_key[key] = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    rows = load_source_rows(source_dir)
    out_files = {
        "train": (out_dir / "regenerated_train.jsonl").open("w", encoding="utf-8"),
        "validation": (out_dir / "regenerated_validation.jsonl").open("w", encoding="utf-8"),
    }
    accepted = {"train": 0, "validation": 0}
    try:
        for split, row in rows:
            cid = row["case_id"]
            if cid not in parsed_by_key:
                if not any(f["case_id"] == cid for f in failures):
                    failures.append({"case_id": cid, "stage": "missing", "error": "Key absent from batch output"})
                continue
            new_row = {
                "case_id": cid,
                "source_split": row.get("source_split", split),
                "source_index": row.get("source_index"),
                "source_sha256": row.get("source_sha256"),
                "note_sha256": row.get("note_sha256"),
                "note": row["note"],
                "reference": parsed_by_key[cid],
                "old_reference": row["reference"],
            }
            out_files[split].write(json.dumps(new_row, ensure_ascii=False) + "\n")
            accepted[split] += 1
    finally:
        for f in out_files.values():
            f.close()

    (out_dir / "failures.jsonl").write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in failures) + ("\n" if failures else ""),
        encoding="utf-8",
    )
    summary = {
        "completed_at_utc": now_str(),
        "job_name": batch_job.name,
        "accepted": accepted,
        "failures_count": len(failures),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[{now_str()}] Done! Accepted: train={accepted['train']}/1325, validation={accepted['validation']}/100, failures={len(failures)}", flush=True)
    print(f"Saved outputs to: {out_dir}", flush=True)


def run_pipeline(source_dir: Path, out_dir: Path, model: str, poll_seconds: int, resume: bool):
    from google.genai import types

    client = get_gemini_client()
    job_path = out_dir / "batch_job.json"

    if resume:
        if not job_path.exists():
            raise FileNotFoundError(f"No {job_path} found to resume.")
        job_name = read_json(job_path)["job_name"]
        batch_job = client.batches.get(name=job_name)
        print(f"[{now_str()}] Resumed polling existing batch job: {batch_job.name}", flush=True)
    else:
        info = dry_run(source_dir, out_dir, model)
        print(f"[{now_str()}] Uploading {info['requests_path']} ...", flush=True)
        uploaded = client.files.upload(
            file=str(info["requests_path"]),
            config=types.UploadFileConfig(display_name="v3-1425-label-regen-requests", mime_type="jsonl"),
        )
        print(f"[{now_str()}] Uploaded file: {uploaded.name}. Creating batch job on {model} ...", flush=True)
        batch_job = client.batches.create(
            model=model,
            src=uploaded.name,
            config=types.CreateBatchJobConfig(display_name="v3-1425-label-regen"),
        )
        state = save_job_state(job_path, batch_job, model)
        print(f"[{now_str()}] Batch started! Job name: {batch_job.name} | Initial state: {state}", flush=True)

    terminal_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        state = save_job_state(job_path, batch_job, model)
        stats = getattr(batch_job, "completion_stats", None) or getattr(batch_job, "batch_stats", None)
        stats_msg = f" | stats={stats}" if stats else ""
        print(f"[{now_str()}] Poll result -> job={batch_job.name} | state={state}{stats_msg}", flush=True)
        if state in terminal_states:
            break
        print(f"[{now_str()}] Sleeping {poll_seconds}s ({poll_seconds // 60} min) before next poll...", flush=True)
        time.sleep(poll_seconds)
        batch_job = client.batches.get(name=batch_job.name)

    if state != "JOB_STATE_SUCCEEDED":
        raise RuntimeError(f"Batch job ended in state {state}: {getattr(batch_job, 'error', None)}")

    process_results(client, batch_job, source_dir, out_dir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_SECONDS, help="Seconds between polls (default 1800 = 30 min)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Assemble and validate JSONL without submitting")
    group.add_argument("--run", action="store_true", help="Run dry-run checks, submit batch, and poll until completion")
    group.add_argument("--resume", action="store_true", help="Resume polling an already-submitted batch_job.json")
    args = parser.parse_args()

    if args.run or args.resume:
        run_pipeline(args.source_dir, args.out_dir, args.model, args.poll_interval, resume=args.resume)
    else:
        dry_run(args.source_dir, args.out_dir, args.model)


if __name__ == "__main__":
    main()
