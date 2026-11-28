"""Continue only the transport-affected cases in the closed Semia comparison."""

import argparse
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
import itertools
import json
import os
from pathlib import Path
import time
from unittest.mock import patch

import prepare
import run


ROOT = run.COMPARISON / "runs/semia"
PARENT = ROOT / "semia-audit-01"
RECOVERY = ROOT / "semia-recovery-01"
PREPARATION = ROOT / "complete-source-01/manifest.json"
STRONG = run.COMPARISON / "runs/strong-model/direct-audit-01/manifest.json"
DIAGNOSTICS = run.COMPARISON / "reports/audit-01/runtime-diagnostics.json"
TRANSPORT_ERROR = "LlmSynthesisError: Semia CLI request failed"
RECOVERY_DISABLED_FEATURE = "unbounded_connection_retries"
ROUTING_MESSAGES = {
    "workspace routing discovery failed": "workspace_routing_discovery_failed",
    "workspace routing discovery timed out": "workspace_routing_discovery_timed_out",
}
EXPECTED_FAILURES = {
    "workspace_routing_discovery_failed": 264,
    "workspace_routing_discovery_timed_out": 16,
    "native_deadline_without_terminal_turn": 2,
}
PROFILE = (
    "model", "reasoning_effort", "provider", "cli_executable", "cli_sha256", "disabled_features",
    "enabled_isolation_features", "detector", "recommendation_status", "synthesis_iterations",
    "structural_retries", "provider_retries", "request_timeout_seconds",
    "max_native_starts_per_case", "experiment_deadline_seconds", "workers",
)


def pin(path):
    return {"path": path.relative_to(run.COMPARISON).as_posix(), "sha256": prepare.sha256(path)}


def terminal_events(path):
    failures = []
    completed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "turn.failed":
            error = event.get("error")
            failures.append(error.get("message") if isinstance(error, dict) else None)
        elif event.get("type") == "turn.completed":
            completed += 1
    return failures, completed


def parent_requests(case_dir, result):
    evidence = []
    for path in sorted((case_dir / "requests").glob("*/request.json")):
        row = prepare.read_json(path)
        event_file = path.with_name("events.jsonl")
        response_file = path.with_name("response.txt")
        terminal, completed = terminal_events(event_file)
        if not row["native_start"] or not row["complete_source_fence_verified"] or row["tool_events"]:
            raise ValueError(f"Parent transport record inconsistent: {path.parent.name}")
        item = {"request": pin(path), "events": pin(event_file), "stderr": pin(path.with_name("stderr.txt"))}
        if row["returncode"] == 0 and row["usage"] is not None:
            if completed != 1 or terminal or response_file.stat().st_size == 0:
                raise ValueError(f"Parent success lacks a visible response: {path.parent.name}")
            item["response"] = pin(response_file)
            if item["response"]["sha256"] != row["response_sha256"]:
                raise ValueError(f"Parent response digest mismatch: {path.parent.name}")
            cause = "visible_answer"
        else:
            if (row["returncode"] != 1 or row["usage"] is not None or completed
                    or (response_file.is_file() and response_file.stat().st_size > 0)):
                raise ValueError(f"Parent routing failure is ambiguous: {path.parent.name}")
            if row.get("timed_out") and not terminal:
                cause = "native_deadline_without_terminal_turn"
            elif len(terminal) == 1 and terminal[0] in ROUTING_MESSAGES:
                cause = ROUTING_MESSAGES[terminal[0]]
            else:
                raise ValueError(f"Parent failure does not match routing evidence: {path.parent.name}")
        evidence.append({**item, "outcome": cause})
    if len(evidence) != result["native_starts"]:
        raise ValueError(f"Parent native start count mismatch: {case_dir.name}")
    return evidence


def build_plan():
    prepare.verify_runtime()
    strong, cohort_sha, cases = run.preflight(PREPARATION, STRONG)
    original = prepare.read_json(PARENT / "manifest.json")
    terminal = prepare.read_json(PARENT / "summary.json")
    diagnostics = prepare.read_json(DIAGNOSTICS)
    if diagnostics["semia_terminal_summary"] != pin(PARENT / "summary.json"):
        raise ValueError("Parent terminal summary differs from closed audit evidence")
    if (
        terminal["finished_cases"] != 100 or terminal["not_run"] != 0
        or terminal["status"] != "partial" or len(terminal["cases"]) != 100
        or original["run_id"] != PARENT.name or original["method"] != "semia"
        or original["cohort_sha256"] != cohort_sha or original["cases"] != cases
        or original["runner_sha256"] != prepare.sha256(Path(run.__file__))
        or original["preparation_manifest_sha256"] != prepare.sha256(PREPARATION)
        or original["strong_transport_manifest_sha256"] != prepare.sha256(STRONG)
        or any(original[name] != strong[name] for name in PROFILE[:7])
        or original["workers"] != 2 or original["max_native_starts_per_case"] != run.NATIVE_START_CAP
        or original["request_timeout_seconds"] != run.REQUEST_TIMEOUT_SECONDS
    ):
        raise ValueError("Parent run, transport or prepared cohort identity mismatch")
    parent_results = {row["case_id"]: row for row in terminal["cases"]}
    selected, excluded, failures = [], [], Counter()
    for case in cases:
        case_id = case["case_id"]
        case_dir = PARENT / "cases" / case_id
        result_path = case_dir / "result.json"
        result = prepare.read_json(result_path)
        if result != parent_results[case_id] or result["package_bytes_sha256"] != case["package_bytes_sha256"]:
            raise ValueError(f"Parent result mismatch: {case_id}")
        if result.get("error") != TRANSPORT_ERROR:
            excluded.append({"case_id": case_id, "status": result["status"], "parent_result": pin(result_path)})
            continue
        evidence = parent_requests(case_dir, result)
        observed = Counter(row["outcome"] for row in evidence)
        visible = observed.pop("visible_answer", 0)
        checks = sorted((case_dir / "raw/validations").glob("*.json"))
        if (
            result["status"] != "failed" or result["synthesis_status"] != "failed"
            or result["detection_status"] != "not_run" or result["validation_count"] != visible
            or len(checks) != visible or any(prepare.read_json(path)["payload"]["program_valid"] for path in checks)
            or result["native_starts_without_usage"] != 3 or sum(observed.values()) != 3
        ):
            raise ValueError(f"Parent case is not an exact routing-affected member: {case_id}")
        failures.update(observed)
        selected.append({
            **case, "parent_result_sha256": prepare.sha256(result_path),
            "parent_result": pin(result_path), "parent_visible_responses": visible, "parent_receipts": evidence,
            "parent_rejected_validations": [pin(path) for path in checks],
        })
    affected_shape = Counter(row["parent_visible_responses"] for row in selected)
    if affected_shape != {0: 92, 1: 1, 3: 1} or len(excluded) != 6 or failures != EXPECTED_FAILURES:
        raise ValueError("Recovery selection differs from the closed scope of 94 cases")
    recovery_strong = {
        **strong, "disabled_features": [*strong["disabled_features"], RECOVERY_DISABLED_FEATURE],
    }
    # Stage the first originally unanswered affected case, then preserve the original relative order.
    staged_index = next(index for index, row in enumerate(selected) if row["parent_visible_responses"] == 0)
    selected.insert(0, selected.pop(staged_index))
    plan = {
        "schema": "semia-transport-recovery-v1", "method": "semia", "variant": original["variant"],
        "run_id": RECOVERY.name, "parent_run_id": PARENT.name, "cohort_sha256": cohort_sha,
        "upstream_commit": original["upstream_commit"], "parent_manifest_sha256": prepare.sha256(PARENT / "manifest.json"),
        "parent_summary_sha256": prepare.sha256(PARENT / "summary.json"),
        "historical_diagnostics": pin(DIAGNOSTICS), "preparation_manifest": pin(PREPARATION),
        "strong_transport_manifest": pin(STRONG), "native_runner_sha256": original["runner_sha256"],
        "recovery_runner_sha256": prepare.sha256(Path(__file__)),
        "case_count": len(selected), "selection": "parent_terminal_cli_transport_failure_only",
        "parent_failure_counts": dict(failures),
        "parent_cases_by_visible_responses": {str(count): cases for count, cases in affected_shape.items()},
        **{name: original[name] for name in PROFILE},
        "disabled_features": recovery_strong["disabled_features"],
        "transport_repair": {
            "disable_cli_feature": RECOVERY_DISABLED_FEATURE,
            "route_outage_stops_before_provider_retry": True,
        },
        "cases": selected, "excluded_cases": excluded,
    }
    return plan, recovery_strong


def current_results(plan):
    results = {}
    for case in plan["cases"]:
        case_id = case["case_id"]
        folder = RECOVERY / "cases" / case_id
        path = folder / "result.json"
        if path.is_file():
            result = prepare.read_json(path)
            if (
                result["case_id"] != case_id or result["package_bytes_sha256"] != case["package_bytes_sha256"]
                or result["status"] not in {"completed", "partial", "failed"}
                or not (RECOVERY / "claims" / f"{case_id}.json").is_file()
            ):
                raise ValueError(f"Recovery result does not match its case claim: {case_id}")
            results[case_id] = result
    return results


def pending_ids(plan, results):
    return [row["case_id"] for row in plan["cases"] if row["case_id"] not in results
            and not (RECOVERY / "claims" / f"{row['case_id']}.json").exists()]


def save_summary(plan, results, status, gate, started, prior_seconds=0):
    pending = pending_ids(plan, results)
    usage, counts = Counter(), Counter()
    for row in results.values():
        usage.update(row["known_usage_by_field"])
        counts[row["status"]] += 1
    row = {
        "status": status, "planned": plan["case_count"], "finished_cases": len(results),
        "not_run": len(pending), "pending_case_ids": pending,
        "claimed_unclosed_case_ids": [case["case_id"] for case in plan["cases"]
                                      if case["case_id"] not in results and case["case_id"] not in pending],
        "case_status_counts": dict(counts), "route_gate": gate,
        "native_starts": sum(result["native_starts"] for result in results.values()),
        "native_starts_without_usage": sum(result["native_starts_without_usage"] for result in results.values()),
        "known_usage_by_field": dict(usage), "elapsed_seconds": prior_seconds + time.monotonic() - started,
        "updated_at": run.STRONG["stamp"](), "cases": list(results.values()),
    }
    run.STRONG["save"](RECOVERY / "summary.json", row)


def reserve(case_id, controller):
    path = RECOVERY / "claims" / f"{case_id}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump({"case_id": case_id, "controller": controller, "claimed_at": run.STRONG["stamp"]()}, handle)


def route_failure(path, row):
    if not row.get("native_start") or (row.get("returncode") in {0, None} and not row.get("timed_out")):
        return None
    response = path.with_name("response.txt")
    if response.is_file() and response.stat().st_size > 0:
        return None
    events = path.with_name("events.jsonl")
    terminal, completed = terminal_events(events) if events.is_file() else ([], 0)
    if not completed:
        if len(terminal) == 1 and terminal[0] in ROUTING_MESSAGES:
            return ROUTING_MESSAGES[terminal[0]]
        if row.get("timed_out") and not terminal:
            return "native_deadline_without_terminal_turn"
    return None


class RecoveryTransport(run.Transport):
    def __call__(self, root, prompt, model):
        from semia_cli.llm_config import LlmSynthesisConfigError, LlmSynthesisError

        before = len(self.calls)
        try:
            return super().__call__(root, prompt, model)
        except LlmSynthesisConfigError:
            raise
        except LlmSynthesisError as error:
            if len(self.calls) > before:
                row = self.calls[-1]
                path = self.folder / "requests" / row["call"] / "request.json"
                reason = route_failure(path, row)
                if reason:
                    row["recovery_transport_stop"] = reason
                    run.STRONG["save"](path, row)
                    raise LlmSynthesisConfigError(f"Semia recovery transport stopped: {reason}") from error
            raise


def run_case(case, strong):
    with patch.object(run, "Transport", RecoveryTransport):
        return run.run_case(RECOVERY, case, strong)


def route_gate(result):
    """A visible native answer establishes delivery even if SDL later fails validation."""
    case_id = result["case_id"]
    request_paths = sorted((RECOVERY / "cases" / case_id / "requests").glob("*/request.json"))
    observed = 0
    routing_failures = Counter()
    protocol_errors = 0
    for path in request_paths:
        row = prepare.read_json(path)
        response = path.with_name("response.txt")
        if row.get("tool_events") or not row.get("complete_source_fence_verified"):
            protocol_errors += 1
        if row.get("returncode") == 0 and response.is_file() and response.stat().st_size > 0:
            terminal, completed = terminal_events(path.with_name("events.jsonl"))
            if not terminal and completed == 1 and row.get("response_sha256") == prepare.sha256(response):
                observed += 1
        reason = row.get("recovery_transport_stop")
        if reason:
            routing_failures[reason] += 1
    status = "passed"
    if protocol_errors or (observed == 0 and not result["native_starts"]):
        status = "blocked_protocol"
    elif routing_failures or not observed or result.get("error") == TRANSPORT_ERROR:
        status = "blocked_routing"
    return {"case_id": case_id, "status": status, "visible_responses": observed,
            "routing_failures": dict(routing_failures), "protocol_errors": protocol_errors}


def dispatch(plan, strong, resume):
    manifest_path = RECOVERY / "manifest.json"
    if not manifest_path.is_file() or prepare.read_json(manifest_path) != plan:
        raise ValueError("Recovery plan missing or changed; use --prepare-only first")
    lock = RECOVERY / "controller.lock"
    with lock.open("x", encoding="utf-8") as handle:
        json.dump({"pid": os.getpid(), "acquired_at": run.STRONG["stamp"]()}, handle)
    try:
        return control(plan, strong, resume)
    finally:
        lock.unlink()


def control(plan, strong, resume):
    started = time.monotonic()
    prior = prepare.read_json(RECOVERY / "summary.json")
    attempts = RECOVERY / "controllers"
    prior_controllers = list(attempts.glob("controller-*.json"))
    if not resume and (prior["status"] != "prepared" or prior_controllers):
        raise ValueError("Initial recovery dispatch already consumed")
    if resume and prior["status"] not in {"paused_routing", "paused_controller"}:
        raise ValueError("Recovery can resume only from a paused controller state")
    results = current_results(plan)
    pending = pending_ids(plan, results)
    if len(results) + len(pending) != plan["case_count"]:
        raise ValueError("A claimed case has no terminal receipt; retain it for manual reconciliation")
    if not pending:
        return 0
    prior_seconds = prior["elapsed_seconds"] if resume else 0
    controller = f"controller-{len(prior_controllers) + 1:02d}"
    started_path = attempts / f"{controller}.json"
    with started_path.open("x", encoding="utf-8") as handle:
        json.dump({"pid": os.getpid(), "asserted_at": run.STRONG["stamp"](), "resume": resume,
                   "staged_case": pending[0]}, handle)
    by_id = {case["case_id"]: case for case in plan["cases"]}
    todo = iter(pending)
    gate = {"status": "pending", "case_id": pending[0]}
    blocked = False
    save_summary(plan, results, "running", gate, started, prior_seconds)

    def launch(pool, case_id):
        reserve(case_id, controller)
        return pool.submit(run_case, by_id[case_id], strong)

    try:
        with ProcessPoolExecutor(max_workers=plan["workers"], initializer=run.worker_setup,
                                 initargs=(RECOVERY / "isolated", strong)) as pool:
            staged = next(todo)
            results[staged] = launch(pool, staged).result()
            gate = route_gate(results[staged])
            blocked = gate["status"] != "passed"
            save_summary(plan, results, "running", gate, started, prior_seconds)
            active = {} if blocked else {
                launch(pool, case_id): case_id for case_id in itertools.islice(todo, plan["workers"])
            }
            while active:
                done, _ = wait(active, return_when=FIRST_COMPLETED)
                for task in done:
                    case_id = active.pop(task)
                    result = task.result()
                    results[case_id] = result
                    decision = route_gate(result)
                    if not blocked and decision["status"] != "passed":
                        gate, blocked = decision, True
                save_summary(plan, results, "running", gate, started, prior_seconds)
                if not blocked:
                    for case_id in itertools.islice(todo, plan["workers"] - len(active)):
                        active[launch(pool, case_id)] = case_id
    except Exception:
        results = current_results(plan)
        save_summary(plan, results, "paused_controller", gate, started, prior_seconds)
        raise
    if len(results) == plan["case_count"]:
        status = "completed" if all(row["status"] == "completed" for row in results.values()) else "partial"
    elif gate["status"] == "blocked_protocol":
        status = "paused_controller"
    else:
        status = "paused_routing"
    save_summary(plan, results, status, gate, started, prior_seconds)
    print(json.dumps({"status": status, "finished_cases": len(results), "pending": len(pending_ids(plan, results)),
                      "route_gate": gate}, ensure_ascii=False))
    return 0 if status == "completed" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare-only", action="store_true", help="Verify and freeze the 94-case plan without calls")
    action.add_argument("--run", action="store_true", help="Dispatch the first staged case and the bounded batch")
    action.add_argument("--resume", action="store_true", help="After routing review, start only unclaimed cases")
    options = parser.parse_args()
    plan, strong = build_plan()
    if options.prepare_only:
        manifest = RECOVERY / "manifest.json"
        if RECOVERY.exists():
            if prepare.read_json(manifest) != plan:
                raise ValueError("Existing recovery manifest is different")
            status = "verified_existing"
        else:
            started = time.monotonic()
            RECOVERY.mkdir(exist_ok=False)
            for name in ("isolated", "claims", "controllers"):
                (RECOVERY / name).mkdir()
            run.STRONG["save"](manifest, plan)
            save_summary(plan, {}, "prepared", {"status": "not_run"}, started)
            status = "prepared"
        print(json.dumps({"status": status, "case_count": len(plan["cases"]),
                          "first_case": plan["cases"][0]["case_id"], "native_starts": 0}))
        return 0
    return dispatch(plan, strong, options.resume)


if __name__ == "__main__":
    raise SystemExit(main())
