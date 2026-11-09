"""Zero-call closure of the October24 remaining-output transport epoch.

This verifies byte/protocol evidence only. It performs no semantic scoring,
does not accept rejected outputs, and never starts or resumes a model request.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from types import SimpleNamespace

from . import direct_continuation_v2 as driver
from . import direct_closure as previous
from . import exploratory_cli as base
from .formal_cli import tree_hashes
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-direct-remaining-output-closure-v2"
TERMINAL = {"complete", "failed", "protocol_aborted", "not_reviewable"}
# Reuse the reviewed saved-byte inspector, supplying only the new transport.
# This private namespace never writes to the historical module's globals.
inspect_new_request = driver.injected(previous.inspect_new_request,
    base=SimpleNamespace(**{**vars(base), "cli": driver.transport}))


def require_workflow_set(run, rows):
    driver.require({p.name for p in (run / "workflows").iterdir()}
                   == {item["workflow_id"] for item in rows},
                   "The exact planned workflow-directory set must remain unchanged")


def require_request_disposition(result, queries, reports):
    if queries:
        driver.require(len(queries) == 1 and queries[0].name == "q001"
                       and result.get("attempts") == 1
                       and result["status"] in {"complete", "failed"},
                       "A launched direct workflow must preserve its sole original q001")
    if result["status"] == "failed":
        driver.require(not any(x.get("accepted") for x in reports) or result.get("candidate_seal_error"),
                       "An accepted answer cannot silently become a failed workflow")


def verify(run_dir):
    run = Path(run_dir).resolve()
    manifest = driver.verify(run, generation=False)
    driver.require((run / "controller-finished.json").exists(), "The single controller must finish before closure")
    driver.require((run / "dispatch-stop.json").exists(), "This stopped epoch must retain its global stop")
    lineage = driver.read(run / "remaining-output-lineage.json")
    donor = Path(lineage["donor_run"])
    donor_seal = driver.verify_donor(donor)
    driver.require(sha256(donor / "output-freeze.json") == lineage["donor_output_freeze_sha256"]
        and sha256(donor / "freeze.json") == lineage["donor_input_freeze_sha256"], "Donor authority changed")
    imported = {x["workflow_id"]: x for x in lineage["retained_workflows"]}
    allowed = set(lineage["new_workflow_ids"])
    rows = base.planned(run)
    require_workflow_set(run, rows)
    reports, statuses, session_ids, response_ids = [], Counter(), set(), set()
    actual_starts = new_starts = 0
    for item in rows:
        wid = item["workflow_id"]
        directory = run / "workflows" / wid
        result = driver.read(directory / "result.json")
        driver.require(result.get("workflow_id") == wid and result.get("status") in TERMINAL
                       and not result.get("native") and item["method"] in {"audit", "chain"},
                       "Every planned direct identity must retain its genuine terminal outcome")
        statuses[result["status"]] += 1
        queries = base.requests(run, wid)
        if wid in imported:
            origin = imported[wid]
            prefix = "workflows/" + wid + "/"
            expected = {name[len(prefix):]: digest for name, digest in donor_seal["files"].items()
                        if name.startswith(prefix)}
            driver.require(expected == origin["files"] == tree_hashes(directory)
                           == tree_hashes(donor / "workflows" / wid), "An imported success/failure changed")
            driver.require(result["status"] == origin["status"], "Imported terminal disposition changed")
        else:
            driver.require(wid in allowed, "An unplanned identity entered generation")
        request_reports = []
        for query in queries:
            start = query / "cli/process-start.json"
            started = start.exists() and driver.read(start).get("actual_cli_process_started") is True
            actual_starts += int(started)
            new_starts += int(started and wid in allowed)
            if wid in allowed:
                report = inspect_new_request(run, item, query, manifest)
            else:
                receipt = driver.read(query / "receipt.json")
                response = driver.read(query / "response.json")
                driver.require(sha256(receipt["raw_receipt_path"]) == receipt["raw_receipt_sha256"],
                               "The original imported raw receipt changed")
                report = {"request": query.relative_to(run).as_posix(), "accepted": response["accepted"],
                    "usage_known": receipt.get("usage_verified") is True,
                    "session_id": receipt.get("cli_session_id"),
                    "response_ids": sorted(receipt.get("usage", {}).get("by_response_id", {})),
                    "origin": "byte_identical_sealed_donor_not_a_new_call"}
            if report.get("session_id"):
                driver.require(report["session_id"] not in session_ids, "A request reused a CLI session")
                session_ids.add(report["session_id"])
            driver.require(not response_ids.intersection(report["response_ids"]), "A response ID was reused")
            response_ids.update(report["response_ids"])
            reports.append(report)
            request_reports.append(report)
        require_request_disposition(result, queries, request_reports)
        if result["status"] == "complete":
            base.verify_candidate(run, wid, result)
            previous.verify_complete_answer_binding(run, directory, result, request_reports)
        if not queries:
            driver.require(result.get("attempts", 0) == 0 and result["status"] in {"protocol_aborted", "not_reviewable"},
                           "A no-call record must remain a genuine unlaunched outcome")
    driver.require(len(rows) == 192, "The full direct denominator must remain192")
    return {"schema_version": SCHEMA, "verified_at": utc_now(), "model_calls": 0,
        "planned_outputs": 192, "terminal_statuses": dict(statuses), "imported_workflows": len(imported),
        "new_actual_starts": new_starts, "actual_starts_including_imports": actual_starts,
        "unique_cli_sessions": len(session_ids), "unique_reported_response_ids": len(response_ids),
        "donor_run": str(donor), "donor_output_freeze_sha256": sha256(donor / "output-freeze.json"),
        "source_input_freeze_sha256": sha256(run / "freeze.json"),
        "request_reports": reports, "usage_including_original_imported_calls": base.usage(run),
        "global_stop_preserved": (run / "dispatch-stop.json").exists(),
        "semantic_scoring_performed": False, "same_epoch_three_way_comparison_completed": False,
        "scope": "Engineering closure only. Every rejected full answer, historical timeout, unlaunched outcome and unknown usage remains unchanged. Imported calls are original costs."}


def close(run_dir):
    run = Path(run_dir).resolve()
    for name in ("output-freeze.json", "lineage-verification-v2.json", "summary.json"):
        driver.require(not (run / name).exists(), "Closure never replaces existing evidence")
    before = tree_hashes(run)
    result = verify(run)
    driver.require(tree_hashes(run) == before, "Zero-call replay changed generation bytes")
    write_json(run / "lineage-verification-v2.json", result, immutable=True)
    provenance = {"schema_version": SCHEMA, "verifier_path": Path(__file__).relative_to(base.ROOT).as_posix(),
        "verifier_sha256": sha256(__file__), "verification_sha256": sha256(run / "lineage-verification-v2.json"),
        "donor_output_freeze_sha256": result["donor_output_freeze_sha256"], "model_calls": 0}
    summary = driver.summary(run)
    summary["closure_lineage"] = provenance
    write_json(run / "summary.json", summary, immutable=True)
    write_json(run / "output-freeze.json", {"schema_version": SCHEMA, "closed_at": utc_now(),
        "planned_outputs": 192, "files": {"workflows/" + k: v for k, v in tree_hashes(run / "workflows").items()},
        "closure_lineage": provenance, "summary_sha256": sha256(run / "summary.json"),
        "failed_results_remain_in_denominator": True, "all_planned_answers_completed": False}, immutable=True)
    return {"status": "terminal_outputs_sealed", "model_calls": 0, "all_planned_answers_completed": False,
            "output_freeze_sha256": sha256(run / "output-freeze.json"), "terminal_statuses": result["terminal_statuses"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "close"))
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    result = close(args.run_dir) if args.command == "close" else verify(args.run_dir)
    print(json.dumps({k: v for k, v in result.items() if k not in {"request_reports", "usage_including_original_imported_calls"}}, indent=2))


if __name__ == "__main__":
    main()
