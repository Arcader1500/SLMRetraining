"""Offline integrity checks for the final continuation-v2 training audit."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "results_v3/training_audit_100"
CONT = AUDIT / "continuation_v2"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True, help="Final bulk run directory")
    args = ap.parse_args()
    run = args.run_dir.resolve()
    errors, checks = [], []

    def check(name, ok, detail=""):
        checks.append({"check": name, "passed": bool(ok), "detail": detail})
        if not ok:
            errors.append(name + (": " + detail if detail else ""))

    baseline = read(CONT / "preservation_baseline.json")
    changed = [p for p, digest in baseline.items() if not (ROOT / p).is_file() or sha(ROOT / p) != digest]
    check("preserved_hashes", not changed, ", ".join(changed))

    manifest, samples = read(AUDIT / "selection_manifest.json"), read(AUDIT / "sample.json")
    from scripts.phase_results import digest
    from scripts.audit_training_data import validate
    from scripts.continue_training_audit import Review, SourceReview, validate_source_review, contract as make_contract
    check("frozen_sample_digest", digest(samples) == manifest["sample_sha256"])
    ids = [x["case_id"] for x in samples]
    check("frozen_100_unique_and_arms", len(ids) == len(set(ids)) == 100 and
          sum(x["group"] == "random" for x in samples) == 50 and sum(x["group"] == "targeted" for x in samples) == 50)
    pilot = read(AUDIT / "judgments/e1a7efa71d6b7cf2/reviews.json")
    old_ids = {x["case_id"] for x in pilot}
    check("pilot_10_unchanged", len(old_ids) == 10 and old_ids.issubset(set(ids)))
    check("final_run_path", run.is_dir())

    contracts = list(CONT.glob("*/run_contract.json"))
    contracts = [p for p in contracts if p.parent == run]
    if not contracts:
        errors.append("final run_contract.json missing")
        contract = {}
    else:
        contract = read(contracts[0])
    check("run_contract_present", bool(contract))
    instruction = contract.get("instructions", "")
    source_instruction = contract.get("second_pass_instruction", "")
    expected_contract = make_contract(samples, instruction, source_instruction)
    for key in ("input_sha256", "prompt_sha256", "schema_sha256", "projection_drops_sha256", "selection_sha256"):
        check("contract_" + key, contract.get(key) == expected_contract.get(key), key)
    base_contract = dict(contract); run_id = base_contract.pop("run_id", None)
    check("contract_run_id", run_id == digest(base_contract)[:16])
    check("contract_response_schema", contract.get("response_schemas") == expected_contract.get("response_schemas"))
    bulk_path = run / "bulk.json"
    rows = read(bulk_path) if bulk_path.exists() else []
    sample_by_id = {x["case_id"]: x for x in samples}
    candidate_by_id = {x["case_id"]: x for x in rows if "review" in x}
    source_by_id = {x["case_id"]: x for x in rows if "source_review" in x}
    expected = set(ids) - old_ids
    check("exact_90_nonpilot_ids", len(rows)==90 and len(candidate_by_id)==90 and len(source_by_id)==90 and
          set(candidate_by_id)==expected and set(source_by_id)==expected,
          f"rows={len(rows)}, candidate={len(candidate_by_id)}, source={len(source_by_id)}, expected={len(expected)}")
    try:
        from scripts.audit_training_data import validate as validate_candidate
        for case_id in sorted(set(candidate_by_id) & expected):
            Review.model_validate(candidate_by_id[case_id]["review"])
            validate_candidate(candidate_by_id[case_id]["review"], sample_by_id[case_id])
        check("candidate_schema_and_quotes", True)
    except Exception as exc:
        check("candidate_schema_and_quotes", False, str(exc))
    try:
        for case_id in sorted(set(source_by_id) & set(candidate_by_id) & expected):
            SourceReview.model_validate(source_by_id[case_id]["source_review"])
            validate_source_review(source_by_id[case_id]["source_review"], sample_by_id[case_id], candidate_by_id[case_id]["review"])
        check("source_review_validation", True)
    except Exception as exc:
        check("source_review_validation", False, str(exc))

    dispositions = [d for row in rows for d in row.get("source_review", {}).get("candidate_dispositions", [])]
    keys = [(row["case_id"], d["candidate_index"]) for row in rows for d in row.get("source_review", {}).get("candidate_dispositions", [])]
    check("unique_complete_dispositions", len(keys) == len(set(keys)) and all(
        sorted(d["candidate_index"] for d in row.get("source_review", {}).get("candidate_dispositions", [])) == list(range(1, len(row.get("review", {}).get("findings", [])) + 1)) for row in rows if row["case_id"] in expected))
    check("exact_evidence_quotes", all(d.get("source_quote") and d["source_quote"] in sample_by_id[cid]["note"]
          for row in rows for cid in [row["case_id"]] for d in row.get("source_review", {}).get("candidate_dispositions", []) + row.get("source_review", {}).get("added_findings", []) if cid in sample_by_id))

    ledger, csv_path = CONT / "combined_case_ledger.json", CONT / "findings.csv"
    optional_missing = []
    if ledger.exists():
        l=read(ledger); check("ledger_100_ids", len(l)==100 and len({x['case_id'] for x in l})==100 and {x['case_id'] for x in l}==set(ids))
    else: optional_missing.append(ledger.name)
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig",newline="") as f: csv_rows=list(csv.DictReader(f))
        raw_counts={}
        for row in rows:
            for d in row.get("source_review",{}).get("candidate_dispositions",[]):
                idx=d["candidate_index"]; f=row["review"]["findings"][idx-1]
                k=(row["case_id"],"continuation_v2","candidate",idx,d["disposition"],"policy_ambiguity" if d["disposition"]=="downgraded" else f["classification"])
                raw_counts[k]=raw_counts.get(k,0)+1
            for finding in row.get("source_review",{}).get("added_findings",[]):
                idx=row["source_review"]["added_findings"].index(finding)+1
                k=(row["case_id"],"continuation_v2","second_pass_added",idx,finding["disposition"],"policy_ambiguity" if finding["disposition"]=="downgraded" else finding["classification"])
                raw_counts[k]=raw_counts.get(k,0)+1
        pilot=read(AUDIT/"pilot_adjudications.json")
        pilot_candidate=sum(len(x['findings']) for x in pilot['adjudications']); pilot_added=len(pilot['additional_findings'])
        check("pilot_csv_record_counts",sum(1 for x in csv_rows if x['protocol']=='pilot_v1' and x['origin']=='candidate')==pilot_candidate and sum(1 for x in csv_rows if x['protocol']=='pilot_v1' and x['origin']=='assistant_added')==pilot_added)
        csv_counts={}
        for finding in csv_rows:
            if finding.get('protocol')=='continuation_v2':
                k=(finding['case_id'],finding['protocol'],finding['origin'],int(finding['index']),finding['disposition'],finding['classification']); csv_counts[k]=csv_counts.get(k,0)+1
        check("findings_csv_consistency",raw_counts==csv_counts)
    else: optional_missing.append(csv_path.name)
    summary_path=CONT/"combined_summary.json"
    if summary_path.exists():
        summary=read(summary_path); check("combined_summary_run_id",summary.get('continuation_run_id')==run.name and summary.get('continuation_cases')==90)
    else: optional_missing.append(summary_path.name)
    report = {"run_dir": str(run), "passed": not errors, "checks": checks,
              "optional_artifacts_not_checked": optional_missing, "errors": errors}
    (CONT / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
