"""Retry failed cases from failures.jsonl via Gemini Batch API and merge into regenerated splits."""
import argparse
import json
import time
from pathlib import Path

from scripts.phase_results import read_json
from scripts.prepare_v3_dataset import schema_valid
from scripts.regenerate_v3_labels_batch import (
    DEFAULT_MODEL,
    DEFAULT_OUT_DIR,
    DEFAULT_SOURCE_DIR,
    REGENERATION_SYSTEM_PROMPT,
    build_response_schema,
    extract_text_from_response,
    get_gemini_client,
    load_source_rows,
    now_str,
)

RETRY_SYSTEM_PROMPT = (
    REGENERATION_SYSTEM_PROMPT
    + "\n6. Concise paraphrasing: Summarize clinical facts concisely in your own words rather than copying long verbatim sentences from the note."
)
DEFAULT_RETRY_POLL_SECONDS = 300  # 5 minutes (119-case batch)


def load_accepted_by_split(out_dir: Path):
    accepted = {"train": {}, "validation": {}}
    for split in ("train", "validation"):
        path = out_dir / f"regenerated_{split}.jsonl"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                accepted[split][row["case_id"]] = row
    return accepted


def get_missing_rows(source_dir: Path, out_dir: Path):
    accepted = load_accepted_by_split(out_dir)
    all_accepted_ids = set(accepted["train"]) | set(accepted["validation"])
    source_rows = load_source_rows(source_dir)
    missing = [(split, row) for split, row in source_rows if row["case_id"] not in all_accepted_ids]
    return missing, accepted, source_rows


def assemble_retry_jsonl(source_dir: Path, out_dir: Path, max_output_tokens: int = 16384, thinking_budget: int | None = 1024):
    missing, accepted, _ = get_missing_rows(source_dir, out_dir)
    requests_path = out_dir / "retry_batch_requests.jsonl"
    response_schema = build_response_schema()
    split_counts = {"train": 0, "validation": 0}

    with requests_path.open("w", encoding="utf-8") as handle:
        for split, row in missing:
            split_counts[split] += 1
            gen_cfg = {
                "temperature": 0.0,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            }
            if thinking_budget is not None:
                gen_cfg["thinking_config"] = {"thinking_budget": thinking_budget}
            entry = {
                "key": row["case_id"],
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": f"Clinical note:\n{row['note']}"}]}],
                    "system_instruction": {"parts": [{"text": RETRY_SYSTEM_PROMPT}]},
                    "generation_config": gen_cfg,
                },
            }
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "requests_path": requests_path,
        "missing_total": len(missing),
        "split_counts": split_counts,
        "already_accepted": {"train": len(accepted["train"]), "validation": len(accepted["validation"])},
        "max_output_tokens": max_output_tokens,
        "thinking_budget": thinking_budget,
    }


def dry_run(source_dir: Path, out_dir: Path, model: str, max_output_tokens: int, thinking_budget: int | None):
    info = assemble_retry_jsonl(source_dir, out_dir, max_output_tokens=max_output_tokens, thinking_budget=thinking_budget)
    print("=== DRY RUN: Retry Batch Assembly ===")
    print(f"Model            : {model}")
    print(f"Already accepted : train={info['already_accepted']['train']}/1325, validation={info['already_accepted']['validation']}/100")
    print(f"Missing to retry : train={info['split_counts']['train']}, validation={info['split_counts']['validation']}, total={info['missing_total']}")
    print(f"max_output_tokens: {info['max_output_tokens']} | thinking_budget: {info['thinking_budget']}")
    print(f"Output JSONL     : {info['requests_path']}")
    return info


def save_retry_job_state(job_path: Path, batch_job, model: str):
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


def merge_retry_results(client, batch_job, source_dir: Path, out_dir: Path):
    dest_file = getattr(getattr(batch_job, "dest", None), "file_name", None)
    if not dest_file:
        raise RuntimeError("Retry batch job succeeded but dest.file_name is missing.")

    print(f"[{now_str()}] Downloading retry results from {dest_file} ...", flush=True)
    raw_bytes = client.files.download(file=dest_file)
    responses_path = out_dir / "retry_batch_responses.jsonl"
    responses_path.write_bytes(raw_bytes)

    newly_parsed = {}
    remaining_failures = []
    with responses_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            key = item.get("key")
            if item.get("error"):
                remaining_failures.append({"case_id": key, "stage": "api_error", "error": item["error"]})
                continue
            text, err = extract_text_from_response(item.get("response") or {})
            if err:
                remaining_failures.append({"case_id": key, "stage": "empty_response", "error": err})
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                remaining_failures.append({"case_id": key, "stage": "json_decode", "error": str(exc), "raw": text[:500]})
                continue
            if not schema_valid(obj):
                remaining_failures.append({"case_id": key, "stage": "schema_valid", "error": "Failed 30-path schema_valid", "raw": text[:500]})
                continue
            newly_parsed[key] = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    _, accepted, source_rows = get_missing_rows(source_dir, out_dir)
    merged_counts = {"train": 0, "validation": 0}
    out_files = {
        "train": (out_dir / "regenerated_train.jsonl").open("w", encoding="utf-8"),
        "validation": (out_dir / "regenerated_validation.jsonl").open("w", encoding="utf-8"),
    }
    try:
        for split, row in source_rows:
            cid = row["case_id"]
            if cid in accepted[split]:
                out_files[split].write(json.dumps(accepted[split][cid], ensure_ascii=False) + "\n")
                merged_counts[split] += 1
            elif cid in newly_parsed:
                new_row = {
                    "case_id": cid,
                    "source_split": row.get("source_split", split),
                    "source_index": row.get("source_index"),
                    "source_sha256": row.get("source_sha256"),
                    "note_sha256": row.get("note_sha256"),
                    "note": row["note"],
                    "reference": newly_parsed[cid],
                    "old_reference": row["reference"],
                }
                out_files[split].write(json.dumps(new_row, ensure_ascii=False) + "\n")
                merged_counts[split] += 1
            elif not any(f["case_id"] == cid for f in remaining_failures):
                remaining_failures.append({"case_id": cid, "stage": "missing", "error": "Key absent from retry output"})
    finally:
        for f in out_files.values():
            f.close()

    (out_dir / "failures.jsonl").write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in remaining_failures) + ("\n" if remaining_failures else ""),
        encoding="utf-8",
    )
    summary = {
        "completed_at_utc": now_str(),
        "retry_job_name": batch_job.name,
        "accepted": merged_counts,
        "newly_recovered": len(newly_parsed),
        "failures_count": len(remaining_failures),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"[{now_str()}] Merge complete! Recovered {len(newly_parsed)} cases. "
        f"Totals: train={merged_counts['train']}/1325, validation={merged_counts['validation']}/100, remaining_failures={len(remaining_failures)}",
        flush=True,
    )


def run_retry_pipeline(source_dir: Path, out_dir: Path, model: str, poll_seconds: int, max_output_tokens: int, thinking_budget: int | None, resume: bool):
    from google.genai import types

    client = get_gemini_client()
    job_path = out_dir / "retry_batch_job.json"

    if resume:
        if not job_path.exists():
            raise FileNotFoundError(f"No {job_path} found to resume.")
        job_name = read_json(job_path)["job_name"]
        batch_job = client.batches.get(name=job_name)
        print(f"[{now_str()}] Resumed polling retry batch job: {batch_job.name}", flush=True)
    else:
        info = dry_run(source_dir, out_dir, model, max_output_tokens, thinking_budget)
        if info["missing_total"] == 0:
            print("No missing/failed cases left to retry.")
            return
        print(f"[{now_str()}] Uploading {info['requests_path']} ...", flush=True)
        uploaded = client.files.upload(
            file=str(info["requests_path"]),
            config=types.UploadFileConfig(display_name="v3-retry-failures-requests", mime_type="jsonl"),
        )
        print(f"[{now_str()}] Uploaded file: {uploaded.name}. Creating retry batch job on {model} ...", flush=True)
        batch_job = client.batches.create(
            model=model,
            src=uploaded.name,
            config=types.CreateBatchJobConfig(display_name="v3-retry-failures"),
        )
        state = save_retry_job_state(job_path, batch_job, model)
        print(f"[{now_str()}] Retry batch started! Job name: {batch_job.name} | Initial state: {state}", flush=True)

    terminal_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        state = save_retry_job_state(job_path, batch_job, model)
        stats = getattr(batch_job, "completion_stats", None) or getattr(batch_job, "batch_stats", None)
        stats_msg = f" | stats={stats}" if stats else ""
        print(f"[{now_str()}] Poll result -> job={batch_job.name} | state={state}{stats_msg}", flush=True)
        if state in terminal_states:
            break
        print(f"[{now_str()}] Sleeping {poll_seconds}s ({poll_seconds // 60} min) before next poll...", flush=True)
        time.sleep(poll_seconds)
        batch_job = client.batches.get(name=batch_job.name)

    if state != "JOB_STATE_SUCCEEDED":
        raise RuntimeError(f"Retry batch job ended in state {state}: {getattr(batch_job, 'error', None)}")

    merge_retry_results(client, batch_job, source_dir, out_dir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-output-tokens", type=int, default=16384)
    parser.add_argument("--thinking-budget", type=int, default=1024, help="Cap thinking tokens so JSON isn't truncated")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_RETRY_POLL_SECONDS, help="Seconds between polls (default 300 = 5 min)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Assemble retry JSONL without submitting")
    group.add_argument("--run", action="store_true", help="Submit retry batch, poll, and merge into regenerated splits")
    group.add_argument("--resume", action="store_true", help="Resume polling retry_batch_job.json")
    args = parser.parse_args()

    if args.run or args.resume:
        run_retry_pipeline(args.source_dir, args.out_dir, args.model, args.poll_interval, args.max_output_tokens, args.thinking_budget, resume=args.resume)
    else:
        dry_run(args.source_dir, args.out_dir, args.model, args.max_output_tokens, args.thinking_budget)


if __name__ == "__main__":
    main()
