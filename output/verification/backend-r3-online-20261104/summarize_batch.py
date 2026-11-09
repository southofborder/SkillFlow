"""Aggregate four closed reports and public receipts; no models or backend execution."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path

VERIFY = Path(__file__).resolve().parent
ROOT = VERIFY.parents[2]
CASES = ("ga4", "001", "010", "013")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    reports, starts, ends, public_ids = [], [], [], []
    tokens = Counter()
    groups = defaultdict(Counter)
    for case in CASES:
        run = ROOT / "experiments/doe/runs" / f"document-guided-{case}-backend-r3-high-20261104-132226"
        if not (run / "controller-finished.json").is_file() or not (run / "assessment.en.md").is_file():
            raise ValueError(f"Closed report unavailable for {case}")
        report = read(run / "run-summary.json")
        metrics = read(run / "metrics.json")
        analysis = read(run / "analysis-finished.json")
        end = read(run / "controller-finished.json")
        starts.append(datetime.fromisoformat(analysis["started_at"]))
        ends.append(datetime.fromisoformat(end["finished_at"]))
        reports.append(report)
        for row in metrics["requests"]:
            tokens.update({k: row.get("complete_token_usage", {}).get(k, 0) for k in ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens")})
            for turn in row.get("public_turns", []):
                if turn.get("accepted_final_associated"):
                    public_ids.append((row.get("thread_id"), turn.get("turn_id"), turn.get("order")))
        for category, values in report["transport"]["call_group_costs"].items():
            groups[category].update(values)
    if len(set(public_ids)) != len(public_ids) or any(x[0] is None for x in public_ids):
        raise ValueError("Public identity reconciliation requires manual review")
    expected = {k: sum(r["transport"]["known_token_usage"].get(k, 0) for r in reports) for k in tokens}
    if dict(tokens) != expected:
        raise ValueError("Per-request totals disagree with saved aggregate counters")
    controller_sum = sum(r["timing"]["controller_wall_seconds"] for r in reports)
    batch = {
        "identity": "backend-r3-four-case-online-assessment-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "all_controllers_closed": True,
        "all_sole_replays_matched": all(r["timing"]["replay"]["status"] == "matched" for r in reports),
        "source_audit_authority": "Independent assistant source criteria, not human gold",
        "cases": [{"case_id": r["case_id"], "run": r["run_directory"], "report": r["report"], "summary": str(Path(r["run_directory"]) / "run-summary.json"), "status": r["analysis"]["status"], "assessment": r["assessment"], "propagation": r["propagation"], "doe": r["doe"], "transport": r["transport"], "timing": r["timing"]} for r in reports],
        "cost": {
            "native_starts": sum(r["transport"]["native_process_starts"] for r in reports),
            "logical_requests": sum(r["transport"]["logical_requests"] for r in reports),
            "call_group_costs": {k: dict(v) for k, v in groups.items()},
            "known_public_tokens": dict(tokens),
            "complete_usage_requests": sum(r["transport"]["complete_usage_requests"] for r in reports),
            "partial_usage_requests": sum(r["transport"]["partial_usage_requests"] for r in reports),
            "unknown_usage_requests": sum(r["transport"]["unknown_usage_requests"] for r in reports),
            "network_extra_attempts": sum(r["transport"]["network_retry_attempts"] for r in reports),
            "inputs_rejected_before_start": sum(r["transport"]["inputs_rejected_before_start"] for r in reports),
            "unique_public_thread_turn_or_order_identities": len(set(public_ids)),
            "duplicate_public_identities": 0,
            "provider_http_attempts": None,
            "unreported_internal_failed_attempt_usage": None,
            "audit_assistant_usage": None,
            "currency": None,
            "analysis_seconds_sum": sum(r["timing"]["analysis_seconds"] for r in reports),
            "replay_seconds_sum": sum(r["timing"]["replay"]["elapsed_seconds"] for r in reports),
            "controller_wall_seconds_sum": controller_sum,
            "sequence_seconds_with_gaps": (max(ends) - min(starts)).total_seconds(),
            "inter_controller_gap_seconds": (max(ends) - min(starts)).total_seconds() - controller_sum,
            "replay_new_native_starts": sum(r["timing"]["replay"]["new_native_markers"] for r in reports),
            "all_implementation_checks_unchanged": all(r["implementation_check"]["unchanged"] for r in reports),
            "scope": "Target calls only, including corrections and shared repairs. Cached input is a subset. Component and parallel-stage times are nonadditive. Audit work is not folded into target totals."
        },
        "comparison": {r["case_id"]: r["comparison_v8"] for r in reports},
        "limitations": [
            "Generated-IR coverage and source-site coverage are different measures.",
            "No generic accuracy, precision, recall, stability or direct-GPT advantage follows from one fresh generation per case.",
            "Replay matching is saved-material reproducibility, not an independent generation or a source-correctness proof.",
            "Paused v9 and separate exhausted offline r2 benchmarks are not completed online cases in this batch.",
            "GA4 never entered propagation or DOE; its shorter failure cannot establish backend acceleration."
        ],
        "delivery_status": "report_prepared"
    }
    (VERIFY / "four-run-summary.json").write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(batch["cost"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
