"""Seal passive reports for the closed sole run; never run analysis or replay."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

PROJECT = Path("D:/Projects/SkillFlow")
OUT = Path(__file__).resolve().parent
OFFLINE = PROJECT / "output/verification/source-review-locality-20261113"
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"
COST = OUT / "cost-provenance-audit/ga4-20261113T162801663200Z.json"
SHA = "ae3df129739a9471521b8b19be65faa8e085f1e92efcacaac1e0c5e3d42f3cbb"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def update_state(path, changes):
    value = read(path)
    value.update(changes)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if (OUT / "run-summary.json").exists():
        raise RuntimeError("Closure summary already exists; do not reseal this run")
    result = read(RUN / "result.json")
    finished = read(RUN / "controller-finished.json")
    replay = read(RUN / "replay-check.json")
    frozen = read(RUN / "implementation-check.json")
    cost = read(COST)
    source = read(OUT / "final-source-coverage.json")
    acceptance = read(OFFLINE / "offline-acceptance.json")
    protocol = read(RUN / "run-protocol.json")
    assert result["status"] == finished["status"] == "failed"
    assert result["stage"] == "revision-processing"
    assert finished["controller_error"] is None
    assert replay["status"] == "matched" and replay["new_native_markers"] == 0
    assert frozen["unchanged"] and frozen["implementation_sha256"] == SHA
    assert cost["final_observation"] and not cost["issues"] and not cost["warnings"]
    assert cost["counts"]["native_process_starts"] == 15
    assert cost["counts"]["complete_usage_requests"] == 14
    assert cost["counts"]["unknown_usage_requests"] == 1
    assert cost["counts"]["network_retry_attempts"] == 0
    assert cost["known_public_usage"]["total_tokens"] == 2862874
    assert cost["closure"]["independent_process_observation"]["remaining_recorded_processes"] == 0
    assert source["counts"]["selected_cfg_ir"] == 679
    assert source["counts"]["revised_candidate_cfg_ir"] == 770
    assert source["counts"]["propagation_processed_ir"] is None
    assert acceptance["passed"] == 886 and acceptance["unresolved_failures"] == 0

    pins = read(RUN / "implementation-snapshot/snapshot.json")
    changed = [name for name, expected in pins["files"].items()
               if not (PROJECT / name).is_file() or digest(PROJECT / name) != expected]
    assert not changed, changed
    for key in ("cli_executable", "renderer_executable", "python_executable"):
        assert digest(Path(protocol[key])) == protocol[key + "_sha256"]
    for name, key in (("controller.py", "controller_sha256"), ("local_timing.py", "local_timing_sha256")):
        assert digest(RUN / name) == pins[key]

    prior = PROJECT / "experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242"
    historical_expected = read(OFFLINE / "preserved-artifact-hashes.json")
    historical_changes = [name for name, expected in historical_expected.items()
                          if digest(prior / name) != expected]
    assert not historical_changes, historical_changes
    now = datetime.now(timezone.utc).isoformat()
    write_new(OUT / "historical-preservation-final.json", {
        "checked_at": now, "run_directory": str(prior),
        "checked_files": len(historical_expected), "changed_files": historical_changes,
        "basis_file": str(OFFLINE / "preserved-artifact-hashes.json"),
        "basis_sha256": digest(OFFLINE / "preserved-artifact-hashes.json"),
        "action": "Read-only hashing; no historical validator, backend, model or replay",
    })
    evidence = [
        OUT / "assessment.en.md", OUT / "assessment.zh.md", COST,
        OUT / "final-cost-provenance.en.md", OUT / "final-source-coverage.json",
        OUT / "final-source-coverage.en.md", OUT / "final-review-audit.json",
        OUT / "final-review-audit.en.md", OUT / "review-delivery-audit.json",
        OUT / "initial-review-correction-audit.json", OUT / "final-initial-review-audit.json",
        OUT / "initial-review-backend-boundary-audit.json",
        OFFLINE / "offline-acceptance.json", OFFLINE / "locator-diagnosis.json",
        RUN / "result.json", RUN / "selection.json", RUN / "controller-finished.json",
        RUN / "replay-check.json", RUN / "implementation-check.json",
    ]
    summary = {
        "version": "skillflow-source-review-locality-closure-v1", "sealed_at": now,
        "status": "closed_failed_before_propagation", "case_id": "ga4",
        "run_directory": RUN.relative_to(PROJECT).as_posix(),
        "implementation_sha256": SHA, "implementation_unchanged": True,
        "offline_acceptance": {
            "distinct_latest_scoped_passes": 886, "unresolved_failures": 0,
            "whole_repository_all_green": False, "single_all_green_scoped_execution": False,
            "initial_final_scope_passed": 885, "initial_final_scope_failed": 1,
            "test_only_corrective_passes": 24, "production_changed_after_acceptance": False,
        },
        "configuration": {"model": "gpt-6.1-sol", "effort": "high", "provider": "openai",
                          "normal_requests": 7, "workers": 2, "shared_repair_rounds": 1,
                          "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700},
        "outcome": {
            "analysis_status": result["status"], "failed_stage": result["stage"],
            "reason": result["reason"], "terminal_cause": "native_process_timeout",
            "timeout_elapsed_seconds": 2700.03195959999,
            "network_interruptions_preceded_timeout": True,
            "exclusive_network_causation_established": False,
            "propagation_ran": False, "doe_ran": False,
            "propagation_processed_ir": None, "input_assessment_count": None,
            "deletable_input_count": None, "doe_comparison_count": None,
            "new_deletable_original_input_established": False,
            "final_input_contract_receipt_created": False,
        },
        "source": {"files": 16, "bytes": 155170, "sha256": protocol["source_sha256"],
                   "all_files_unchanged": True, "truncated": False},
        "representation": source["counts"],
        "initial_review": {
            "status": "partial", "accepted_call": None,
            "whole_response_accepted": False, "physical_obligations": 275, "inventory_scopes": 928,
            "candidate_records": 290, "valid_records": 289, "invalid_records": 1,
            "retained_check_rows": 274, "usable_checks": 273,
            "coverage": {"validated": 273, "invalid": 1, "blocked": 1},
            "usable_scopes": {"total": 922, "accepted": 880, "rejected": 36, "unresolved": 6},
            "validation_barriers": 1, "barrier_instruction_ids": ["ir_260"],
            "barrier_operation_references": 2, "quarantined_obligations": 2,
            "quarantined_scopes": 6, "ordinary_repair_findings": 14,
            "derived_repair_findings": 35, "total_repair_findings": 49,
            "repair_routed": True, "revised_material_reviewed": False,
            "retained_source_input_findings": 1,
            "semantic_caveat": "The valid limit locator coexists with rejected receiver interface scopes; locator validation does not prove full operation faithfulness or semantic truth.",
        },
        "delivery": {"limit_codepoints": 1048576, "initial_codepoints": 864947,
                     "correction_codepoints": 988098, "source_and_inventory_exactly_preserved": True,
                     "same_initial_material_compact_v1_codepoints": 2146076,
                     "normal_shared_saving_codepoints": 1281129,
                     "input_rejections": 0},
        "cost": {"counts": cost["counts"], "known_public_usage": cost["known_public_usage"],
                 "unknown_usage_requests": 1, "full_provider_usage_known": False,
                 "provider_billing_cost": None, "returned_model_metadata_available": False,
                 "notice": "Cached input and reasoning output are subsets; internal stderr and stdout retry surfaces overlap. Unknown usage is not zero."},
        "lifecycle": {"analysis_seconds": finished["analysis_seconds"],
                      "controller_finished_at": finished["finished_at"], "replay": replay,
                      "remaining_recorded_processes": 0, "maximum_new_runs": 1,
                      "fresh_runs_started": 1, "authorization_consumed": True,
                      "remaining_authorized_runs": 0, "remaining_authorized_replays": 0},
        "preservation": {"current_pins_checked": len(pins["files"]),
                         "current_changed_pins": [], "prior_artifacts_checked": len(historical_expected),
                         "prior_artifacts_changed": [], "skill_executed": False,
                         "historical_analysis_or_replay_invoked": False},
        "evidence_sha256": {path.relative_to(PROJECT).as_posix(): digest(path) for path in evidence},
    }
    write_new(OUT / "run-summary.json", summary)

    closed_note = (
        "Strict source-review locality CLOSED (2026-11-14): general locator/schema, correction and strict local-isolation fixes are offline accepted at implementation ae3df129739a9471521b8b19be65faa8e085f1e92efcacaac1e0c5e3d42f3cbb; 886 distinct latest scoped tests pass, zero unresolved failures, not one whole-repository all-green execution. The sole fresh GA4 document-guided-ga4-source-review-locality-high-20261113-203902 and its sole zero-call replay are CLOSED. Initial partial review retained 273 usable checks/922 scopes while quarantining two paired obligations/six scopes at ir_260, then routed 49 findings into the existing shared repair. Complete review deliveries 864947/988098 characters preserved all source/contracts. Revision-processing hit the 2700-second native timeout; no propagation, final input assessments or DOE ran. Final selected CFG is initial679IR; revised770IR remains unselected. Actual15 native starts=7normal+5corrections+3stage requests in one repair round; 2862874 known public tokens plus unknown failed-request usage, outer retries0. Replay matched60.492s/0new starts; implementation/source/executables unchanged and all recorded processes exited. Read output/verification/online-ga4-source-review-locality-20261113/assessment.en.md, assessment.zh.md and run-summary.json. This sole launch/replay authorization is consumed. Do not restart, resume old processes, replay again, execute Skills, add probes/cases/resampling, migrate frozen artifacts or import staged-worktree code. Earlier preparation and active notes below are consumed history.\n\n"
    )
    agents_path = PROJECT / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8")
    assert not agents_text.startswith("Strict source-review locality CLOSED (2026-11-14)")
    agents_path.write_text(closed_note + agents_text, encoding="utf-8")
    update_state(OUT / "continuation-state.json", {
        "status": "closed_failed_before_propagation", "closed_at": finished["finished_at"],
        "native_starts": 15, "known_public_tokens": 2862874, "unknown_usage_requests": 1,
        "replay": replay, "implementation_unchanged": True,
        "reports": ["assessment.en.md", "assessment.zh.md", "run-summary.json"],
        "remaining_authorized_runs": 0, "remaining_authorized_replays": 0,
        "instructions": "Closed and reported. Preserve raw failures and historical artifacts. Do not dispatch again, resume old runs/processes, replay again, execute Skills or add probes/cases. No new analysis is authorized by this closure.",
    })
    update_state(OFFLINE / "continuation-state.json", {
        "status": "complete_offline_and_single_online_attempt_closed",
        "initial_launch_snapshot_starts": 2, "model_starts": 15,
        "closed_at": finished["finished_at"],
        "next_step": "Work and reporting complete. Sole fresh GA4 failed in revision-processing before propagation/DOE; sole zero-call replay matched. Preserve evidence; no remaining launch or replay authorization.",
        "online_summary": str((OUT / "run-summary.json").relative_to(PROJECT)),
        "live_counts_reference": "The final online run-summary.json replaces the initial launch snapshot; observation is terminal.",
    })
    # Only documentation and continuation/report files were written; check the
    # production pins again without importing or executing project code.
    assert all(digest(PROJECT / name) == expected for name, expected in pins["files"].items())
    assert all(digest(prior / name) == expected for name, expected in historical_expected.items())
    write_new(OUT / "report-check.json", {
        "checked_at": datetime.now(timezone.utc).isoformat(), "status": "passed",
        "action": "Passive final report consistency, pinned-file and historical hash checks only",
        "run_summary_sha256": digest(OUT / "run-summary.json"),
        "implementation_sha256": SHA, "production_pins_unchanged": True,
        "historical_artifacts_unchanged": True, "new_model_calls": 0,
        "new_backend_calls": 0, "new_replays": 0,
        "evidence_files_checked": len(evidence),
    })
    print(json.dumps({"status": "closed_and_reported", "run_summary": str(OUT / "run-summary.json"),
                      "native_starts": 15, "known_public_tokens": 2862874,
                      "replay": replay, "pins_checked": len(pins["files"])}))


if __name__ == "__main__":
    main()
