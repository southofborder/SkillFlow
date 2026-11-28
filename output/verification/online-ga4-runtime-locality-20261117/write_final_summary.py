"""Assemble reporting metadata from closed receipts; no project execution."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OFFLINE = ROOT / "output/verification/runtime-locality-20261117"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value, fresh=False):
    with path.open("x" if fresh else "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    prepared = read(BASE / "prepared-run.json")
    run = Path(prepared["run_directory"])
    finished = read(run / "controller-finished.json")
    integrity = read(BASE / "final-integrity.json")
    audit = read(BASE / "final-backend-source-audit.json")
    accounting = read(run / "restart-accounting.json")
    result = read(run / "result.json")
    if not integrity["integrity_passed"] or finished["replay"]["status"] != "matched":
        raise ValueError("Expected matched terminal receipts and unchanged material")
    if audit["demand"]["range_statuses"] != {"required": 497, "unresolved": 3078, "deletable": 0}:
        raise ValueError("Demand counts differ from the independently audited final result")
    evidence_names = ["final-integrity.json", "process-closure-observation.json",
        "final-backend-source-audit.json", "final-cost-provenance.json",
        "source-review-input-v12-audit.json", "source-review-a001-correction-audit.json",
        "source-review-merge-repair-audit.json", "processing-a002-retention-audit.json",
        "correction-finding-origin-audit.json", "runtime-locality-passive-code-review.json",
        "task-revision-audit.json", "graph-terminal-deadline-20261117T151035Z.json"]
    evidence = {name: sha(BASE / name) for name in evidence_names}
    evidence.update({f"{run.relative_to(ROOT).as_posix()}/{name}": digest
        for name, digest in integrity["critical_artifacts_sha256"].items()})
    evidence["output/verification/runtime-locality-20261117/offline-acceptance.json"] = sha(OFFLINE / "offline-acceptance.json")
    demand = audit["demand"]
    global_codes = Counter(item["code"] for item in demand["global_blocking_diagnostics"])
    summary = {
        "identity": "skillflow-runtime-locality-closure-report-v1",
        "status": "closed_partial", "run_directory": str(run),
        "parent_run": accounting["parent_run"], "implementation_sha256": prepared["implementation_sha256"],
        "complete_source_files": 16, "inherited_bound_files": 58,
        "selected_cfg": {"origin": "inherited_initial", "blocks": 215, "ir": 489, "edges": 192, "byte_identical": True},
        "selected_task_requirements": 49, "unselected_revised_task_requirements": 60,
        "policy": {"normal_stages": 7, "inherited_initial_stages": 3, "fresh_normal_requests": 4,
            "workers": 2, "corrections_per_stage": 1, "shared_repair_rounds": 1,
            "native_timeout_seconds": 2700, "native_extra_transient_attempts": 2},
        "stages": result["stages"], "shared_repair_used": result["repair_used"],
        "review": {"obligations": 528, "scopes": 1735,
            "check_statuses": audit["review"]["check_statuses"], "scope_statuses": audit["review"]["scope_statuses"],
            "initial_delivery_characters": 897755, "correction_delivery_characters": 926267,
            "adapter_limit_characters": 1048576, "allowed_existing_records": 25,
            "changed_checks": 21, "preserved_checks": 507, "preserved_original_findings": 19,
            "inserted_records": 0, "unresolved_findings": 44,
            "status": audit["review"]["status"], "source_review_complete": audit["review"]["source_review_complete"],
            "core_partial": audit["review"]["core_partial"], "demand_receipt_matches": audit["review"]["demand_receipt_matches"]},
        "processing": {"retained_modeled_ir": 484, "source_unmodeled_ir": 4, "validation_isolated_ir": 1,
            "compute_contracts": 89, "nonempty_output_selectors_in_contracts": 0,
            "preexisting_masked_resource_binding_error": "ir_001",
            "new_reply_to_date_range_binding_errors_after_full_correction": 19},
        "propagation": {"status": audit["propagation"]["status"], "coverage": audit["propagation"]["coverage_counts"],
            "typed_operation_fault_count": audit["propagation"]["typed_operation_fault_count"],
            "missing_part_ir": ["ir_457", "ir_459"], "online_typed_failure_isolation_exercised": False},
        "source_boundary_record_reach": audit["source_boundary_counts"],
        "source_boundary_caveat": "Record reach only; unresolved receiver and other source-semantic findings prevent full correctness claims. No Skill execution.",
        "input_assessments": {"rows": demand["assessments"], "node_kinds": demand["assessment_node_kinds"],
            "coverage": demand["assessment_coverage"], "ranges": {**demand["range_statuses"], "deletable": 0},
            "modifications": demand["non_null_modifications"], "global_blocking_diagnostics": dict(global_codes),
            "global_blocking_count": demand["global_blocking_count"], "output_contract_gap_count": len(demand["output_contract_gaps"]),
            "output_contract_gap_ir_count": demand["output_contract_gap_ir_count"],
            "output_gap_nonempty_path_count": demand["output_gap_nonempty_path_count"],
            "output_gap_selector_properties": demand["output_gap_selector_properties"],
            "required_caveat": "Positive task derivations under retained limitations, not fully certified task behavior."},
        "doe": {"status": audit["doe"]["status"], "sinks": audit["doe"]["sink_count"],
            "comparison_conclusions": audit["doe"]["comparison_conclusions"], "reductions": 0},
        "cost": {"new_native_starts": 10, "new_normal_starts": 4, "new_structural_correction_starts": 4,
            "shared_repair_starts": 2, "new_logical_calls": accounting["new_logical_calls"],
            "recorded_logical_calls_including_inherited": accounting["recorded_logical_calls_including_inherited"],
            "inherited_logical_calls": 3, "known_usage_requests": 9, "unknown_usage_requests": 1,
            "known_public_input_tokens": 2013741, "known_public_output_tokens": 213192,
            "known_public_total_tokens": 2226933, "inherited_tokens_excluded": 303082,
            "outer_retries": 0, "unreported_provider_usage": "unknown"},
        "network_and_deadline": {"failed_stage": "revision-graph", "process_status": "timeout",
            "native_elapsed_seconds": 2700.032429, "graph_delivery_characters": 432728,
            "complete_graph_output_characters": None, "primary_sampling_retry_lines": 15,
            "overlapping_public_reconnect_notices": 11,
            "http_body_error_intervals_seconds": [902.606046, 901.878152],
            "specific_15_minute_timer_cause": "not_established", "pure_model_generation_seconds": None},
        "analysis_seconds": finished["analysis_seconds"], "replay": finished["replay"],
        "controller_finished_at": finished["finished_at"],
        "all_recorded_pids_absent": integrity["all_recorded_pids_absent"], "recorded_pid_count": len(integrity["recorded_pids"]),
        "runtime_pins": integrity["runtime_pins"], "historical_pins": integrity["historical_pins"],
        "offline_acceptance": {"distinct_latest_passed": 6023, "skipped": 3, "unresolved_failures": 0,
            "whole_repository_or_one_all_green_execution": False},
        "followup_proposals_implemented": False, "static_failed_action_risk_reproduced": False,
        "authorization_consumed": True, "no_further_run_or_replay_started": True, "evidence_sha256": evidence}
    write(BASE / "run-summary.json", summary, fresh=True)
    for directory in (BASE, OFFLINE):
        state = read(directory / "continuation-state.json")
        state.update(status="closed_partial", updated_at=datetime.now(timezone.utc).isoformat(),
            pending=[], authorization_consumed=True, analysis_status="partial", replay=finished["replay"],
            reports_directory=str(BASE), final_summary_sha256=sha(BASE / "run-summary.json"),
            instructions="Sole authorized new GA4 and sole zero-call replay are CLOSED. Preserve reports, raw failures and frozen implementation. No restart, extra replay, Skill execution, probes, resampling, historical mutation, staged import or proposal implementation without new user instruction.")
        write(directory / "continuation-state.json", state)
    print(json.dumps({"status": summary["status"], "summary_sha256": sha(BASE / "run-summary.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
