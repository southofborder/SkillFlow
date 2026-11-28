"""Bind the closed run's passive reports and update mutable navigation state.

No model, validator, renderer, backend, Skill, process control or replay call.
Original run, acceptance, failure and audit artifacts are read-only.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
OFFLINE = PROJECT / "output/verification/processing-timeout-20261116"


def read(path):
    return json.loads(path.read_bytes().decode("utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusive(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def mutable(path, value):
    # Keep the pre-closeout state as evidence of previously published progress.
    backup = VERIFY / ("pre-closeout-" + path.parent.name + "-" + path.name)
    with backup.open("xb") as handle:
        handle.write(path.read_bytes())
    temporary = path.with_suffix(".closeout.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    summary_path = VERIFY / "run-summary.json"
    if summary_path.exists():
        raise RuntimeError("Final summary already exists; do not reseal or rerun")
    prepared = read(VERIFY / "prepared-run.json")
    run = Path(prepared["run_directory"]).resolve()
    if run != PROJECT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414":
        raise RuntimeError("Unexpected run namespace")
    cost = read(VERIFY / "final-cost-provenance.json")
    coverage = read(VERIFY / "final-source-coverage.json")
    acceptance = read(OFFLINE / "offline-acceptance.json")
    result = read(run / "result.json")
    finished = read(run / "controller-finished.json")
    process_check = read(VERIFY / "root-process-exit-check.json")
    replay = read(run / "replay-check.json")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    protocol = read(run / "run-protocol.json")
    if not cost["final"] or cost["issues"] or cost["warnings"]:
        raise RuntimeError("Final cost audit has unresolved issues")
    if (result["status"], result["stage"], result["selected_annotation"], result["repair_used"]) != ("failed", "processing", None, False):
        raise RuntimeError("Unexpected final stage/selection")
    if replay["status"] != "matched" or replay["new_native_markers"] != 0:
        raise RuntimeError("The sole replay did not match without new starts")
    if not finished["native_exits"]["all_attempt_exits_confirmed"] or not process_check["all_recorded_process_ids_absent"]:
        raise RuntimeError("Process closure is not established")
    if acceptance["status"] != "passed" or acceptance["passed"] != 788 or acceptance["unresolved_failures"]:
        raise RuntimeError("Offline acceptance differs")
    if protocol["implementation_sha256"] != acceptance["implementation_sha256"]:
        raise RuntimeError("Online implementation differs from acceptance")
    changed = [name for name, digest in snapshot["files"].items() if sha(PROJECT / name) != digest]
    for field in ("cli_executable", "renderer_executable", "python_executable"):
        if sha(Path(protocol[field])) != protocol[field + "_sha256"]:
            changed.append(field)
    for name, field in (("controller.py", "controller_sha256"), ("local_timing.py", "local_timing_sha256")):
        if sha(run / name) != snapshot[field]:
            changed.append(name)
    if changed:
        raise RuntimeError("Frozen files changed: " + repr(changed))
    counts, usage = cost["counts"], cost["known_public_usage"]
    if (counts["native_process_starts"], counts["normal_confirmed_starts"], counts["structural_correction_confirmed_starts"],
            counts["semantic_repair_confirmed_starts"], counts["network_retry_confirmed_starts"]) != (6, 4, 2, 0, 0):
        raise RuntimeError("Unexpected actual call inventory")
    if usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"] or usage["total_tokens"] != 670215:
        raise RuntimeError("Public usage arithmetic differs")
    relative_reports = [
        "assessment.en.md", "assessment.zh.md", "followup-plan.zh.md",
        "final-cost-provenance.en.md", "final-cost-provenance.json", "final-cost-provenance-closeout.json",
        "final-source-coverage.en.md", "final-source-coverage.json", "root-process-exit-check.json",
        "processing-final-assessment.en.md", "processing-final-receipt-bindings.json",
        "processing-result-followup-proposal.en.md", "processing-pair-diagnostic-followup.en.md",
        "processing-initial-response-audit.en.md", "processing-initial-rejected-pair-forensics.json",
        "processing-initial-correction-codec-size.json", "graph-correction-and-processing-input.en.md",
        "graph-correction-and-processing-input-accepted.json", "source-physical-inventory.json",
        "graph-correction-preliminary.en.md", "graph-correction-dependency-context.json",
        "passive-audit-v14-reconciliation.json", "finalize_assessment.py",
    ]
    references = [VERIFY / name for name in relative_reports]
    references += [run / name for name in (
        "run-protocol.json", "result.json", "controller-started.json", "controller-finished.json",
        "analysis-finished.json", "replay-started.json", "replay-check.json", "native-exit-check.json",
        "implementation-check.json", "implementation-snapshot/snapshot.json", "audit/fatal-semantic-frontier.json")]
    references += [OFFLINE / "offline-acceptance.json", OFFLINE / "scoped-regression-final.xml",
                   OFFLINE / "timeout-evidence.json", OFFLINE / "timeout-evidence.en.md",
                   PROJECT / "docs/doe/processing-timeout.md", PROJECT / "docs/doe/processing-timeout.zh.md",
                   PROJECT / "docs/current-version.md", PROJECT / "AGENTS.md"]
    now = datetime.now(timezone.utc).isoformat()
    summary = {
        "identity": "skillflow-processing-timeout-assessment-v1", "created_at": now,
        "status": "closed_failed_initial_processing", "run_directory": str(run),
        "implementation_sha256": protocol["implementation_sha256"], "source_sha256": protocol["source_sha256"],
        "source_files": 16, "source_utf8_bytes": 155170,
        "configured_runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
        "returned_model": cost["returned_model"],
        "policy": {"normal_semantic_requests": 7, "workers": 2, "structural_corrections_per_stage": 1,
                   "shared_semantic_repairs": 1, "native_timeout_seconds": 2700, "extra_eligible_outer_transient_attempts": 2},
        "offline": {"passed": 788, "failed": 0, "skipped": 0, "whole_repository_execution": False,
                    "receipt": "output/verification/processing-timeout-20261116/scoped-regression-final.xml"},
        "actual_counts": counts, "known_public_usage": usage,
        "usage_limit": "Failed-request/provider-internal unreported usage and billing remain unknown; subsets are not additional tokens.",
        "analysis_seconds": finished["analysis_seconds"], "analysis_result": result,
        "replay": replay, "native_exits": finished["native_exits"], "recorded_process_ids_absent": process_check,
        "available_generated_material": coverage["available_generated_material"],
        "unavailable_results": coverage["unavailable_results"],
        "input_presentation": {
            "initial_prompt_characters": 425423, "same_material_plain_prompt_characters": 486361,
            "reduction_characters": 60938, "reduction_percent": 60938 / 486361 * 100,
            "logical_payload_characters": 252386, "shared_body_characters": 190095,
            "complete_source_retained": True, "logical_expansion_exact": True,
            "existing_source_duplicate_script_content_copies": 294,
            "correction_prompt_characters": 675293, "initial_delivery_characters": 425635,
            "correction_delivery_characters": 675505,
            "notice": "Character-only same-material accounting; no token, output-compression or latency improvement established."},
        "output_representation": {
            "initial_raw_answer_characters": 212300, "strict_rejection": "duplicate JSON member: shared_values",
            "table_entry_counts": [266, 310], "overlapping_names": 241, "unequal_exact_overlapping_values": 81,
            "static_prompt_gap": "Codec name pattern v(?:0|[1-9][0-9]*) was not explicit in prompts; raw tables used mnemonic names.",
            "accepted_expanded_size": None, "accepted_processing": False, "correction_complete_answer": False},
        "network": {"sampling_retry_records": 3, "overlapping_stdout_notices": 2,
                    "auxiliary_model_refresh_timeout_lines": 12, "reported_sampling_backoff_seconds": 1.375,
                    "time_apportionment": None, "ttft": None, "pure_generation_seconds": None,
                    "fixed_idle_timeout_established": False},
        "requests": [{key: row[key] for key in (
            "request", "stage", "category", "logical_attempt_index", "process", "delivery",
            "native_answer_available", "usage_completeness", "complete_token_usage", "sampling_retries")}
            for row in cost["requests"]],
        "provenance": cost["provenance"], "final_direct_frozen_file_check": {"files": len(snapshot["files"]), "changed": changed},
        "followup": {"status": "proposal_only_not_implemented", "path": "followup-plan.zh.md",
                     "priorities": ["complete shared-wire prompt grammar and one final table guidance",
                                    "bounded noncanonicalizing pair diagnostics within existing correction",
                                    "causal graph diagnostics and actual dependency repair closure",
                                    "separate evidence for transport and source-semantic limitations"]},
        "authorization": {"new_runs_started": 1, "sole_zero_call_replay_completed": True, "consumed": True,
                          "additional_runs_or_replays": 0, "skills_executed": 0, "historical_replays": 0},
        "evidence_sha256": {path.relative_to(PROJECT).as_posix(): sha(path) for path in references},
    }
    exclusive(summary_path, summary)
    online_state = read(VERIFY / "continuation-state.json")
    online_state.update(status="closed_reported", updated_at=now, analysis_status="failed",
        failure_stage="initial_processing_structural_correction", replay=replay,
        native_process_starts=6, known_public_tokens=670215, failed_request_usage="unknown",
        selected_annotation=None, downstream_analysis="not_run", authorization_consumed=True,
        run_summary="run-summary.json", assessments=["assessment.en.md", "assessment.zh.md"],
        proposal="followup-plan.zh.md", all_recorded_processes_exited=True,
        instructions="The sole fresh GA4 and sole zero-call replay are closed. Preserve raw/frozen artifacts. Do not restart, resume, replay again, execute Skills, add probes/cases/resampling or import staged-worktree code. Followup is proposal-only; no further implementation or model run is authorized by the consumed launch notes.")
    mutable(VERIFY / "continuation-state.json", online_state)
    offline_state = read(OFFLINE / "continuation-state.json")
    offline_state.update(status="offline_accepted_sole_new_ga4_and_replay_closed", updated_at=now,
        pending=[], online_preparation_status="closed_single_dispatch_single_replay",
        latest_broad_receipt={"path": "scoped-regression-final.xml", "passed": 788, "failed": 0, "skipped": 0,
                              "note": "Final affected-scope execution; not a whole-repository execution. Earlier failures preserved."},
        online_result="failed_initial_processing_correction_native_timeout", replay=replay,
        online_summary="output/verification/online-ga4-processing-timeout-20261116/run-summary.json",
        followup_proposal="output/verification/online-ga4-processing-timeout-20261116/followup-plan.zh.md",
        authorization_consumed=True)
    offline_state["implemented"] = [
        "complete processing input sharing", "strict self-contained processing output sharing",
        "passive public-event interval telemetry", "confirmed shared-repair failure retains entire original bound bundle",
        "bound concurrent fatal semantic frontier replay", "consistent saved Task interruption classification"]
    mutable(OFFLINE / "continuation-state.json", offline_state)
    exclusive(VERIFY / "report-closeout.json", {
        "closed_at": now, "run_summary_sha256": sha(summary_path),
        "online_state_sha256": sha(VERIFY / "continuation-state.json"),
        "offline_state_sha256": sha(OFFLINE / "continuation-state.json"),
        "frozen_files_changed": [], "new_model_calls": 0, "new_replays": 0,
        "report_binding_count": len(references), "authorization_consumed": True,
    })
    print(json.dumps({"status": summary["status"], "summary": str(summary_path),
                      "native_starts": 6, "known_public_tokens": 670215, "replay": replay,
                      "frozen_files_checked": len(snapshot["files"]), "report_bindings": len(references)}))


if __name__ == "__main__":
    main()
