"""Publish summaries from closed saved records, without analysis or model calls."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    prepared = read(BASE / "prepared-run.json")
    run = Path(prepared["run_directory"])
    finished = read(run / "controller-finished.json")
    replay = read(run / "replay-check.json")
    unchanged = read(run / "implementation-check.json")
    result = read(run / "result.json")
    metrics = read(run / "metrics.json")
    demand = read(run / "doe/audit/demand-support.json")
    doe = read(run / "doe/doe-result.json")
    review = read(run / "review/result.json")
    receipt = read(run / "audit/input-contract-review.json")
    assessments = demand["input_assessments"]
    ranges = [item for row in assessments for item in row["ranges"]]
    comparisons = [item for sink in doe["sinks"] for item in sink["data_reviews"]]
    assert finished["status"] == result["status"] == "partial"
    assert replay["status"] == "matched" and replay["new_native_markers"] == 0
    assert unchanged["unchanged"]
    assert metrics["native_process_starts"] == 9
    assert metrics["known_token_usage"]["total_tokens"] == 1641287
    assert dict(Counter(row["status"] for row in ranges)) == {"unresolved": 3171, "required": 1100}
    assert len(assessments) == 1509 and len(comparisons) == 83
    assert all(item["conclusion"] == "no_excess_established" and item["reduction"] is None for item in comparisons)
    assert review["status"] == "request_failure" and review["error_type"] == "InputTooLarge"
    evidence = ["assessment.en.md", "assessment.zh.md", "closed-cost-provenance.en.md",
        "cost-provenance-audit/ga4-20261112T124850198832Z.json", "cost-provenance-audit/review-input-rejection-audit.json",
        "source-audit/source-boundary-inventory.json", "source-audit/selected-assembly-source-audit.json",
        "source-audit/propagation-source-audit.json", "source-audit/saved-backend-source-audit.json"]
    hashes = {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in evidence}
    summary = {
        "schema_version": "skillflow-ga4-corrected-online-summary-v1",
        "status": "closed_partial", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run), "implementation_sha256": prepared["implementation_sha256"],
        "source_sha256": prepared["source_sha256"], "source_files": 16,
        "configuration": read(run / "run-protocol.json"), "controller": finished,
        "stages": result["stages"], "review_failure": review["reason"],
        "review": {"source_review_complete": False, "obligations": 344, "contracts": 344, "checks": 0,
            "typed_source_input_findings": 0, "zero_findings_mean_no_error": False},
        "propagation": {"generated_ir": 563, "processed": 553, "unmodeled": 1, "blocked": 9,
            "processed_does_not_imply_all_alternatives_succeeded": True},
        "source_site_coverage": {"api_sites": 13, "api_sites_with_records": 13,
            "save_sites": 25, "save_sites_with_records": 24,
            "persistent_write_records_at_internal_save_sites": 0, "explicit_loop_sites": 3},
        "input_assessments": {"records": len(assessments), "ranges": len(ranges),
            "range_statuses": dict(Counter(row["status"] for row in ranges)),
            "coverage": dict(Counter(row["coverage"] for row in assessments)),
            "records_with_unresolved": sum(any(item["status"] == "unresolved" for item in row["ranges"]) for row in assessments),
            "reviewed_black_box_necessity_established": False},
        "doe": {"status": doe["status"], "sinks": len(doe["sinks"]), "comparisons": len(comparisons),
            "conclusions": dict(Counter(row["conclusion"] for row in comparisons)), "reductions": 0,
            "coverage": doe["coverage"], "diagnostic_codes": dict(Counter(row["code"] for row in doe["diagnostics"]))},
        "cost": {"native_starts": 9, "normal_starts": 6, "structural_correction_starts": 3,
            "semantic_repair_starts": 0, "outer_retry_starts": 0, "prestart_rejections": 1,
            "transport_logical_requests": 10, "complete_public_usage_requests": 9,
            "known_public_usage": metrics["known_token_usage"], "unknown_final_usage_requests": 0,
            "provider_http_attempts": None, "unreported_internal_attempt_usage": None, "monetary_cost": None},
        "interrupted_predecessor": {"run_directory": read(run / "run-protocol.json")["interrupted_run_reference_only"],
            "status": "aborted_by_user_after_network_outage", "native_starts": 4, "known_tokens": 306246,
            "unknown_final_usage_requests": 1, "replay": "not_started_due_to_user_cancellation"},
        "combined_november_12_attempts": {"native_starts": 13, "known_tokens": 1947533,
            "unknown_final_usage_requests": 1, "replacement_only": False, "november_11_batch_included": False},
        "replay": replay, "implementation_check": unchanged, "evidence_sha256": hashes,
        "next_action": "No additional model run, replay, probe or implementation change was made or authorized by this closure."
    }
    write(BASE / "run-summary.json", summary)
    state = read(BASE / "continuation-state.json")
    state.update(status="closed_and_delivered", outcome="partial", controller_finished=finished,
        replay=replay, reports={"english": "assessment.en.md", "chinese": "assessment.zh.md", "summary": "run-summary.json"},
        instructions="This sole replacement and its sole zero-call replay are closed. Preserve all records. Do not restart, resume, replay again, execute Skills, add probes or launch another run without a new user instruction.")
    write(BASE / "continuation-state.json", state)
    header = """Latest GA4 replacement CLOSED (2026-11-12): the user-confirmed network-outage attempt 174538 was stopped and preserved (4 native starts, 306246 known tokens plus one unknown request; no replay). The explicitly requested replacement document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209 and its sole zero-call replay are now CLOSED. Result partial: source review was rejected before native start because 1079505 characters exceeded the 1048576 adapter limit; no semantic repair or completed contract review. Propagation processed 553/563 IR (1 unmodeled, 9 blocked); 1509 input assessments contain 1100 required and 3171 unresolved ranges, zero deletable. DOE has 83 no_excess_established comparisons and no reductions. Actual replacement cost: 9 confirmed native starts and 1641287 known public tokens; provider-internal unreported usage remains unknown. Sole replay matched with zero new starts; implementation remained 796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa. Read output/verification/online-ga4-input-necessity-corrected-r2-20261112/assessment.en.md, assessment.zh.md and run-summary.json. All launch/replay authorizations above are consumed. Do not launch again, resume old processes, replay historical runs, execute Skills, add probes/resampling, change implementation or import staged-worktree code without new user instructions. Older launch notes below are consumed history.\n\n"""
    path = PROJECT / "AGENTS.md"
    path.write_text(header + path.read_text(encoding="utf-8"), encoding="utf-8")
    path = PROJECT / "docs/current-version.md"
    text = path.read_text(encoding="utf-8")
    start, end = text.index("Current online validation (2026-11-12):"), text.index("Documentation updated")
    block = """Latest online validation (2026-11-12): the replacement GA4 run and its sole
zero-call replay are closed. The result is **partial**: source review exceeded
the adapter input cap before model launch; propagation processed 553/563 IR,
and no deletable input or DOE reduction was established. Replay matched with
zero new native starts; accepted implementation remained unchanged.
See the [English assessment](../output/verification/online-ga4-input-necessity-corrected-r2-20261112/assessment.en.md),
[Chinese assessment](../output/verification/online-ga4-input-necessity-corrected-r2-20261112/assessment.zh.md), and
[machine-readable summary](../output/verification/online-ga4-input-necessity-corrected-r2-20261112/run-summary.json).
The preceding network-outage attempt was stopped at the user's request and
preserved separately. Both attempts' authorizations are consumed.

"""
    text = text[:start] + block + text[end:]
    text = text.replace("Documentation updated 2026-11-11.", "Documentation updated 2026-11-12.", 1)
    text = text.replace("Latest closed real validation: **input-necessity, 2026-11-11**. Its original\nevidence is separate from subsequent offline corrections.",
        "Latest closed real validation: **corrected input-necessity GA4, 2026-11-12**. Earlier batch evidence remains separate.", 1)
    text = text.replace("These corrections have offline evidence only. No second real batch is authorized.",
        "These corrections also have the separate partial November 12 GA4 evidence described above. No further real run is authorized.")
    path.write_text(text, encoding="utf-8")
    path = PROJECT / "docs/research-chat-handoff.md"
    text = path.read_text(encoding="utf-8")
    title, body = text.split("\n", 1)
    note = """Current status (2026-11-12): the fresh corrected GA4 replacement and its sole
zero-call replay are closed, with partial diagnostic results and no deletable
input established. Source review hit the adapter input cap before native launch.
See [Current version](current-version.md) and
`output/verification/online-ga4-input-necessity-corrected-r2-20261112/`.
The earlier user-confirmed network-outage attempt remains separately aborted;
neither attempt may be resumed or replayed again. No new model/Skill run, probe,
implementation change or staged-worktree import is authorized by this closure.

"""
    path.write_text(title + "\n\n" + note + body.lstrip(), encoding="utf-8")
    broken = []
    for name in ("assessment.en.md", "assessment.zh.md"):
        for target in re.findall(r"\]\(([^)]+)\)", (BASE / name).read_text(encoding="utf-8")):
            if "://" not in target and not (BASE / target).is_file():
                broken.append({"file": name, "target": target})
    assert not broken, broken
    write(BASE / "delivery-verification.json", {"status": "passed", "report_links_valid": True,
        "saved_counts_verified": True, "replay": replay, "implementation_unchanged": True,
        "source_model_execution": False, "additional_analysis_runs": 0,
        "run_summary_sha256": hashlib.sha256((BASE / "run-summary.json").read_bytes()).hexdigest()})
    print(json.dumps({"status": "closed_and_delivered", "outcome": "partial", "report_links_valid": True}))


if __name__ == "__main__":
    main()
