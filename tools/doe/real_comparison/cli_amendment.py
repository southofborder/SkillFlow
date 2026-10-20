"""Adopted v2 CLI engineering calibrations in a separate, permanently nonformal run.

The historical collaboration protocol is retained as provenance. The effective
CLI protocol below governs transport. No flag or imported human record can open
formal dispatch in this calibration-only run; a new cohort needs a separate gate.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import time

from . import execution as native
from . import cli_adapter as cli
from .protocol import canonical_hash, policy, sha256, utc_now, write_json

SCHEMA = cli.SCHEMA
ROOT = Path(__file__).resolve().parents[3]
CALIBRATION = native.CALIBRATION
CALIBRATION_SOURCE_ROOT = ROOT / "experiments/corpus/semantics_review/inputs/upstream"
LIMITS = {"actual_cli_requests": 64, "reported_total_tokens": 8000000,
          "workflow_seconds": 21600, "outstanding_request_seconds": 2700,
          "delivered_reference_tokens": 300000}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def effective_policy():
    result = policy()
    result["schema_version"] = SCHEMA
    result["runtime"] = {"transport": cli.TRANSPORT, **cli.EXPECTED,
        "fresh_process_per_semantic_request": True, "stdin_exact_complete_material": True,
        "empty_working_directory": True, "ignore_user_config": True, "ignore_rules": True,
        "tools": False, "delegation": False, "follow_up_hints": False,
        "resume": False, "fork": False, "prior_turns": False, "retrieval": False,
        "hard_sandbox": False, "configuration_verification": "actual_persisted_exec_receipt",
        "visible_input_verification": "exact_task_and_pinned_common_harness_plus_one_environment_context",
        "all_methods_and_direct_reviews_same_transport": True,
        "cli_version": cli.PINNED_VERSION, "executable_sha256": cli.PINNED_EXECUTABLE_SHA256}
    result["budget"] = {**LIMITS, "unknown_usage": "retain_unknown_and_stop_all_further_dispatch",
        "token_stop": "after_receipt_before_next_dispatch", "truncate_source_or_requests": False,
        "automatic_adapter_retry": False, "replacement_requests": False}
    result["protocol_precedence"] = "This effective CLI protocol governs transport; inherited v1 collaboration policy is historical provenance only. All unaffected comparative and human rules are retained."
    result["run_scope"] = {"calibration_only": True, "formal_dispatch": "permanently_forbidden",
        "calibration_semantic_accuracy": "not_evaluated",
        "future_formal_cohort": "Requires a separately prepared long-source cohort, materials, references, actual human confirmations and formal gate; no v1 case approvals are inherited."}
    return result


def _copy_exact(source, target):
    source, target = Path(source), Path(target)
    if source.is_symlink() or not source.is_file():
        raise native.ExecutionStop("A frozen input is missing or is a symlink")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha256(target) != sha256(source):
            raise native.ExecutionStop("An immutable inherited input differs")
    else:
        shutil.copyfile(source, target)


def prepare_calibration_run(run_dir, *, original_run, decision_record, executable):
    """Prepare three fresh from-source workflows, without dispatch or human import.

    decision_record is the supervising chat's explicit user-adoption record. It
    must already exist. This function preserves its bytes and never manufactures
    a user statement, reference confirmation or approval.
    """
    run, previous, decision = Path(run_dir).resolve(), Path(original_run).resolve(), Path(decision_record).resolve()
    if run == previous or run.is_relative_to(previous):
        raise native.ExecutionStop("A v2 calibration run must be separate from every frozen v1 artifact")
    if run.exists():
        raise native.ExecutionStop("A fresh calibration run cannot reuse an existing directory")
    adoption = read(decision)
    if adoption.get("state") != "adopted" or adoption.get("user_authorized") is not True:
        raise native.ExecutionStop("An explicit adopted user-authorization record is required")
    if sha256(executable) != cli.PINNED_EXECUTABLE_SHA256:
        raise native.ExecutionStop("The adopted CLI executable hash differs from the feasibility executable")
    native._verify_file_seal(previous, "protocol-freeze.json")
    native.verify_evaluation_rules(previous)
    native.verify_production_code(previous)
    run.mkdir(parents=True)
    inherited = {}
    for name in ("protocol.json", "protocol-freeze.json", "rubric.md", "evaluation-rules-freeze.json",
                 "evaluation-rules-supplement-v1.md", "grading-contract.json", "common-runtime-contract.json", "common-assumptions.md"):
        path = previous / name
        if path.is_file():
            target = run / "inherited-v1" / name
            _copy_exact(path, target)
            inherited[target.relative_to(run).as_posix()] = sha256(target)
    _copy_exact(decision, run / "authorization/adoption.json")
    historical = []
    for name, classification in (("mailbox", "original_stopped_collaboration_calibration"),
                                 ("workflows/calibration_gh_fix_ci", "original_stopped_native_worker"),
                                 ("transport-inspection/proposed-cli-probe", "successful_feasibility_only")):
        paths = sorted(p for p in (previous / name).rglob("*") if p.is_file())
        historical.append({"classification": classification, "source_directory": str(previous / name),
                           "files": {p.relative_to(previous).as_posix(): sha256(p) for p in paths},
                           "imported_as_target_or_calibration_response": False})
    amendment = {"schema_version": SCHEMA, "state": "adopted", "created_at": utc_now(),
        "calibration_only": True, "formal_dispatch_permitted": False,
        "authorization_path": "authorization/adoption.json", "authorization_sha256": sha256(decision),
        "original_run": str(previous), "original_protocol_sha256": sha256(previous / "protocol.json"),
        "original_evaluation_freeze_sha256": sha256(previous / "evaluation-rules-freeze.json"),
        "inherited_files": inherited, "historical_evidence": historical,
        "effective_transport_protocol": "cli-protocol.json", "runtime": cli.EXPECTED,
        "executable": str(Path(executable).resolve()), "executable_sha256": sha256(executable),
        "precedence": effective_policy()["protocol_precedence"],
        "legacy_materials_or_approvals_imported": False, "earlier_attempts_replaced": False}
    write_json(run / "amendment.json", amendment, immutable=True)
    write_json(run / "cli-protocol.json", effective_policy(), immutable=True)
    native.snapshot_production_code(run)
    files, cases = {}, []
    for name in CALIBRATION:
        original = CALIBRATION_SOURCE_ROOT / name
        native._calibration_source(original)
        target = run / "calibration-inputs" / name
        for source in sorted(original.rglob("*")):
            if source.is_file():
                destination = target / source.relative_to(original)
                _copy_exact(source, destination)
                files[destination.relative_to(run).as_posix()] = sha256(destination)
        from skillflow.common.inputs.snapshot import inspect_input
        cases.append({"case_id": name, "workflow_id": "calibration_cli_v2_" + name.replace("-", "_") + "_" + native._name(run.name),
            "source_path": target.relative_to(run).as_posix(), "source_sha256": inspect_input(target)[2]["source_sha256"],
            "method": "skillflow", "mode": "calibration", "kind": "calibration", "repeat": 0,
            "source_origin": str(original), "from_source": True, "graph_reuse": False,
            "semantic_repair_policy": "Unchanged native policy; at most one downstream semantic repair round."})
    write_json(run / "calibration-inputs-freeze.json", {"schema_version": SCHEMA, "files": files}, immutable=True)
    write_json(run / "calibration-plan.json", {"schema_version": SCHEMA, "calibration_only": True, "cases": cases,
        "scope": "Three complete native from-source engineering workflows, with fresh request identities. Semantic correctness is not an engineering gate."}, immutable=True)
    implementation_files = {p.relative_to(ROOT).as_posix(): sha256(p) for p in (
        Path(__file__), Path(cli.__file__))}
    seal_names = ("amendment.json", "authorization/adoption.json", "cli-protocol.json",
        "calibration-plan.json", "calibration-inputs-freeze.json", "production-code-freeze.json")
    write_json(run / "cli-protocol-freeze.json", {"schema_version": SCHEMA,
        "files": {**{n: sha256(run / n) for n in seal_names}, **inherited},
        "implementation_files": implementation_files,
        "effective_policy_sha256": canonical_hash(effective_policy()), "calibration_only": True}, immutable=True)
    verify_run(run)
    return {"schema_version": SCHEMA, "status": "prepared_calibration_only", "run_dir": str(run),
            "calibration_only": True, "formal_requests": 0, "actual_cli_requests": 0, "cases": cases}


def verify_run(run_dir):
    run = Path(run_dir).resolve()
    seal = native._verify_file_seal(run, "cli-protocol-freeze.json")
    if seal.get("calibration_only") is not True or read(run / "amendment.json").get("calibration_only") is not True:
        raise native.ExecutionStop("The calibration-only run binding is absent")
    if read(run / "cli-protocol.json") != effective_policy():
        raise native.ExecutionStop("The effective CLI protocol differs from its approved implementation")
    for relative, wanted in seal["implementation_files"].items():
        if sha256(ROOT / relative) != wanted:
            raise native.ExecutionStop("The versioned CLI adapter changed after its freeze")
    amendment = read(run / "amendment.json")
    previous = Path(amendment["original_run"])
    if sha256(previous / "evaluation-rules-freeze.json") != amendment["original_evaluation_freeze_sha256"]:
        raise native.ExecutionStop("The original evaluation freeze changed")
    for entry in amendment["historical_evidence"]:
        for relative, expected in entry["files"].items():
            if sha256(previous / relative) != expected:
                raise native.ExecutionStop("A preserved historical attempt changed")
    native.verify_evaluation_rules(previous)
    native.verify_production_code(run)
    native._verify_file_seal(run, "calibration-inputs-freeze.json")
    if sha256(amendment["executable"]) != amendment["executable_sha256"]:
        raise native.ExecutionStop("The inspected executable changed")
    return seal


def pending_requests(run_dir):
    return [r for p, r in native._requests(run_dir) if not any((p / n).exists()
        for n in ("dispatch.json", "response.json", "stop.json"))]


def _assess(directory):
    directory = Path(directory)
    if not (directory / "receipt.json").exists() or not (directory / "response.json").exists():
        return "unverified"
    receipt, response = read(directory / "receipt.json"), read(directory / "response.json")
    return "conformant" if (receipt.get("protocol_status") == "conformant"
        and receipt.get("configuration_verified") is True and receipt.get("provider_verified") is True
        and receipt.get("usage_verified") is True and response.get("accepted") is True) else "violated"


def _budget(run_dir, workflow_id, *, dispatching=False, now=None):
    run = Path(run_dir)
    now = time.time() if now is None else now
    state = read(native._workflow(run, workflow_id) / "state.json")
    if now - native._seconds(state["started_at"]) >= LIMITS["workflow_seconds"]:
        raise native.ExecutionStop("The six-hour native workflow budget is exhausted")
    requests = native._requests(run, workflow_id)
    dispatched = [p for p, r in requests if (p / "dispatch.json").exists()]
    if dispatching and len(dispatched) >= LIMITS["actual_cli_requests"]:
        raise native.ExecutionStop("The 64 actual CLI-request workflow budget is exhausted")
    for directory in dispatched:
        if _assess(directory) == "violated":
            raise native.ExecutionStop("A prior CLI response failed protocol, configuration or usage verification")
        if not (directory / "response.json").exists():
            if now - native._seconds(read(directory / "dispatch.json")["dispatched_at"]) >= LIMITS["outstanding_request_seconds"]:
                raise native.ExecutionStop("A CLI request exceeded the 45-minute outstanding limit")
            if dispatching:
                raise native.ExecutionStop("A prior actual CLI request remains unresolved")
    summary = native.usage_summary(run, workflow_id)
    if summary["conflicting_response_ids"]:
        raise native.ExecutionStop("Conflicting per-response usage forbids dispatch")
    if dispatched and (summary["missing_requests"] or any(v is None for v in summary["totals"].values())):
        if dispatching or all((p / "response.json").exists() for p in dispatched):
            raise native.ExecutionStop("Unknown per-response usage forbids dispatch")
    total = summary["totals"]["total_tokens"]
    if total is not None and total >= LIMITS["reported_total_tokens"]:
        raise native.ExecutionStop("The reported eight-million-token native workflow budget is exhausted")


def authorize_dispatch(run_dir, request_id):
    run = Path(run_dir).resolve()
    verify_run(run)
    if (run / "dispatch-stop.json").exists():
        raise native.ExecutionStop("All further CLI dispatch is closed by a retained failed or unaccountable request")
    directory = run / "mailbox/requests" / native._name(request_id)
    request = read(directory / "request.json")
    if request.get("mode") != "calibration":
        raise native.ExecutionStop("Formal dispatch is permanently forbidden in this calibration-only run")
    if any((directory / n).exists() for n in ("dispatch.json", "response.json", "stop.json")):
        raise native.ExecutionStop("A CLI request cannot be dispatched or replaced twice")
    if sha256(directory / "prompt.txt") != request["delivery_sha256"] or sha256(directory / "core-prompt.txt") != request["core_sha256"]:
        raise native.ExecutionStop("The exact complete queued material changed")
    core = (directory / "core-prompt.txt").read_text(encoding="utf-8")
    if (directory / "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8"):
        raise native.ExecutionStop("The exact native core was not preserved in the delivered envelope")
    if request["reference_tokens"] > LIMITS["delivered_reference_tokens"]:
        raise native.ExecutionStop("The complete request exceeds 300,000 reference tokens; clipping is forbidden")
    registration = read(native._workflow(run, request["workflow_id"]) / "registration.json")
    plan = read(run / "calibration-plan.json")["cases"]
    match = [p for p in plan if p["workflow_id"] == request["workflow_id"]]
    if (len(match) != 1 or registration.get("mode") != "calibration" or request.get("transport") != cli.TRANSPORT
            or registration["source_sha256"] != match[0]["source_sha256"] or registration["method"] != "skillflow"):
        raise native.ExecutionStop("Only the three frozen native calibration workflows may dispatch")
    native._calibration_source(registration["source_path"])
    for other, _ in native._requests(run):
        if (other / "dispatch.json").exists():
            if _assess(other) == "violated":
                raise native.ExecutionStop("A previous CLI calibration request failed; all further dispatch is stopped")
            if not (other / "response.json").exists():
                raise native.ExecutionStop("Another actual CLI request remains unresolved")
    _budget(run, request["workflow_id"], dispatching=True)
    return {"authorized": True, "request_id": request_id, "transport": cli.TRANSPORT,
            "prompt_sha256": request["delivery_sha256"], "runtime": cli.EXPECTED, "calibration_only": True}


@contextmanager
def _dispatch_lock(run):
    lock = Path(run) / "dispatcher.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise native.ExecutionStop("Another dispatcher is active; no duplicate CLI launch was made") from error
    try:
        stream.write(utc_now())
        stream.close()
        yield
    finally:
        lock.unlink(missing_ok=True)


def dispatch_next_once(run_dir, *, sessions_dir=None, popen=None):
    """Execute one already queued calibration request; never loop or retry.

    Run this supervisor alongside run_calibration_worker in separate processes.
    A bad actual request is preserved and permanently closes the run's dispatcher.
    """
    from tools.doe.direct_baseline import DEFAULT_SESSIONS, find_receipt
    run = Path(run_dir).resolve()
    with _dispatch_lock(run):
        if (run / "dispatch-stop.json").exists():
            return {"status": "dispatch_closed", "actual_cli_requests": 0,
                    "reason": read(run / "dispatch-stop.json")["reason"]}
        pending = pending_requests(run)
        if not pending:
            return {"status": "no_pending_request", "actual_cli_requests": 0}
        request = pending[0]
        request_id, workflow_id = request["request_id"], request["workflow_id"]
        directory = run / "mailbox/requests" / request_id
        try:
            authorize_dispatch(run, request_id)
        except Exception as error:
            write_json(directory / "stop.json", {"reason": f"Predispatch validation stopped: {type(error).__name__}: {error}",
                "stopped_at": utc_now(), "actual_cli_process_started": False}, immutable=True)
            write_json(run / "dispatch-stop.json", {"request_id": request_id, "stopped_at": utc_now(),
                "reason": "Predispatch validation failed; the failed request is retained without retry.",
                "violations": [str(error)], "automatic_retry": False}, immutable=True)
            raise
        cwd = run / "empty-cwd" / request_id
        cwd.mkdir(parents=True, exist_ok=False)
        amendment = read(run / "amendment.json")
        prepared = cli.prepare_launch(amendment["executable"], directory / "prompt.txt", directory / "cli", cwd)
        write_json(directory / "dispatch.json", {"schema_version": SCHEMA, "transport": cli.TRANSPORT,
            "request_id": request_id, "dispatched_at": utc_now(), "planned_prompt_sha256": request["delivery_sha256"],
            "command": prepared["command"], "executable_sha256": prepared["executable_sha256"],
            "actual_process_evidence": "cli/process-start.json", "protocol_conformant": True,
            "configuration_verified": False, "collaboration_spawn": False, "calibration_only": True}, immutable=True)
        state = read(native._workflow(run, workflow_id) / "state.json")
        remaining = LIMITS["workflow_seconds"] - (time.time() - native._seconds(state["started_at"]))
        try:
            process = cli.execute_launch(prepared, timeout_seconds=min(LIMITS["outstanding_request_seconds"], remaining), popen=popen)
        except Exception as error:
            # A changed launch can fail before Popen. Preserve the attempted
            # dispatch without claiming that a process or target call occurred.
            output = directory / "cli"
            output.mkdir(exist_ok=True)
            for name in ("stdout.jsonl", "stderr.txt"):
                (output / name).touch(exist_ok=True)
            process = {"schema_version": SCHEMA, "status": "prelaunch_error", "returncode": None,
                "error": f"{type(error).__name__}: {error}", "finished_at": utc_now(), "supervisor_waits": [],
                "supervisor_elapsed_seconds": 0., "actual_cli_process_started": False, "retries": 0}
            write_json(output / "process-result.json", process, immutable=True)
        answer, receipt = None, {"schema_version": SCHEMA, "transport": cli.TRANSPORT,
            "protocol_status": "unverified", "configuration_verified": False, "provider_verified": False,
            "usage_verified": False, "completed": False, "usage": {"by_response_id": {},
                "totals": {key: None for key in cli.TOKEN_FIELDS}}, "violations": []}
        try:
            session_id = cli.session_from_stdout(directory / "cli/stdout.jsonl")
            raw_receipt = find_receipt(session_id, sessions_dir or DEFAULT_SESSIONS)
            answer, receipt = cli.inspect_receipt(raw_receipt, session_id, prepared,
                stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            receipt["raw_receipt_path"] = str(raw_receipt.resolve())
            used = [read(p / "receipt.json").get("cli_session_id") for p, _ in native._requests(run)
                    if (p / "receipt.json").exists()]
            if session_id in used:
                receipt["violations"].append("The actual CLI exec session was reused")
            prior_response_ids = {identity for p, _ in native._requests(run) if (p / "receipt.json").exists()
                for identity in read(p / "receipt.json").get("usage", {}).get("by_response_id", {})}
            if prior_response_ids.intersection(receipt["usage"]["by_response_id"]):
                receipt["violations"].append("A response identity was reused by a different actual CLI request")
        except Exception as error:
            receipt["violations"].append(f"Actual receipt inspection failed: {type(error).__name__}: {error}")
        if process["status"] != "process_exited" or process["returncode"] != 0:
            receipt["violations"].append("The actual CLI process failed, timed out or did not exit successfully")
        receipt.update(request_id=request_id, process_result_sha256=sha256(directory / "cli/process-result.json"),
            stdout_sha256=sha256(directory / "cli/stdout.jsonl"), stdin_sha256=prepared["stdin_sha256"],
            executable_sha256=prepared["executable_sha256"], supervisor_wait_seconds=process["supervisor_elapsed_seconds"])
        if receipt["violations"]:
            receipt["protocol_status"] = "violated"
        accepted = (receipt.get("protocol_status") == "conformant" and receipt.get("usage_verified") is True
                    and receipt.get("configuration_verified") is True and receipt.get("provider_verified") is True
                    and receipt.get("completed") is True and answer is not None)
        write_json(directory / "receipt.json", receipt, immutable=True)
        response = {"request_id": request_id, "accepted": accepted, "answer": answer,
            "answer_sha256": cli.digest(answer) if answer is not None else None, "imported_at": utc_now()}
        write_json(directory / "response.json", response, immutable=True)
        if not accepted:
            write_json(run / "dispatch-stop.json", {"request_id": request_id, "stopped_at": utc_now(),
                "reason": "A failed, nonconforming or unaccountable actual CLI request forbids every further dispatch.",
                "violations": receipt["violations"], "automatic_retry": False}, immutable=True)
        return {"request_id": request_id, "status": "accepted" if accepted else "stopped",
                "cli_session_id": receipt.get("cli_session_id"), "response_ids": list(receipt["usage"]["by_response_id"]),
                "usage": receipt["usage"], "actual_cli_process_started": process["actual_cli_process_started"],
                "formal_requests": 0, "violations": receipt["violations"]}


class CliMailboxClient:
    """The unchanged native injected-client contract with truthful CLI requests."""
    def __init__(self, run_dir, workflow_id, *, token_counter=native.reference_tokens, stop_event=None, poll_seconds=.5):
        self.run, self.workflow_id, self.counter = Path(run_dir), workflow_id, token_counter
        self.stop_event, self.poll_seconds, self.cursor, self.wait_seconds = stop_event, poll_seconds, 0, 0.

    def complete(self, prompt):
        if not isinstance(prompt, str):
            raise TypeError("The native semantic prompt must be text")
        verify_run(self.run)
        delivery = native.ENVELOPE.replace("{core}", prompt)
        tokens = self.counter(delivery)
        if tokens > LIMITS["delivered_reference_tokens"]:
            raise native.ExecutionStop("The complete delivery exceeds 300,000 reference tokens; clipping is forbidden")
        self.cursor += 1
        request_id = f"{self.workflow_id}_q{self.cursor:03d}"
        directory = self.run / "mailbox/requests" / request_id
        if directory.exists():
            raise native.ExecutionStop("A calibration request identity cannot be reused or replayed as a fresh run")
        _budget(self.run, self.workflow_id, dispatching=True)
        if (self.run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A retained actual-request failure stopped this calibration run")
        directory.mkdir(parents=True)
        (directory / "prompt.txt").write_bytes(delivery.encode("utf-8"))
        (directory / "core-prompt.txt").write_bytes(prompt.encode("utf-8"))
        write_json(directory / "request.json", {"schema_version": SCHEMA, "request_id": request_id,
            "workflow_id": self.workflow_id, "sequence": self.cursor, "mode": "calibration", "created_at": utc_now(),
            "core_sha256": cli.digest(prompt), "delivery_sha256": cli.digest(delivery), "reference_tokens": tokens,
            "runtime": cli.EXPECTED, "transport": cli.TRANSPORT, "calibration_only": True,
            "configuration_verified": False, "collaboration_spawn": False}, immutable=True)
        start = time.perf_counter()
        try:
            while not (directory / "response.json").exists():
                if self.stop_event is not None and self.stop_event.is_set():
                    raise KeyboardInterrupt("The native calibration worker was interrupted; the exact pending request is retained")
                if (directory / "stop.json").exists():
                    raise native.ExecutionStop(read(directory / "stop.json")["reason"])
                if (self.run / "dispatch-stop.json").exists():
                    raise native.ExecutionStop("The CLI calibration dispatcher stopped after a retained failed request")
                _budget(self.run, self.workflow_id)
                time.sleep(self.poll_seconds)
            response = read(directory / "response.json")
            if _assess(directory) != "conformant":
                raise native.ExecutionStop("The actual CLI response failed protocol, runtime, delivery or usage verification")
            if response["answer_sha256"] != cli.digest(response["answer"]):
                raise native.ExecutionStop("The imported visible CLI answer changed")
            return response["answer"]
        finally:
            self.wait_seconds += time.perf_counter() - start


def run_calibration_worker(run_dir, case_id, *, renderer=None, stop_event=None, token_counter=native.reference_tokens):
    """Run one full current native pipeline from a frozen familiar source package."""
    run = Path(run_dir).resolve()
    verify_run(run)
    matches = [p for p in read(run / "calibration-plan.json")["cases"] if p["case_id"] == case_id]
    if len(matches) != 1 or case_id not in CALIBRATION:
        raise native.ExecutionStop("Only the three familiar frozen native calibration cases are allowed")
    item = matches[0]
    workflow, source = native._workflow(run, item["workflow_id"]), run / item["source_path"]
    if workflow.exists():
        raise native.ExecutionStop("A full native engineering calibration cannot be automatically retried or replaced")
    workflow.mkdir(parents=True)
    write_json(workflow / "registration.json", {**item, "source_path": str(source.resolve()),
        "runtime": cli.EXPECTED, "transport": cli.TRANSPORT, "calibration_only": True,
        "production_api_config": {}, "configuration_verified": False}, immutable=True)
    write_json(workflow / "state.json", {"started_at": utc_now()}, immutable=True)
    attempt = workflow / "attempts/001"
    attempt.mkdir(parents=True)
    client = CliMailboxClient(run, item["workflow_id"], token_counter=token_counter, stop_event=stop_event)
    start = time.perf_counter()
    result = {"schema_version": SCHEMA, "workflow_id": item["workflow_id"], "status": "failed",
              "calibration_only": True, "formal_requests": 0, "answer_sha256": None,
              "artifact_root": attempt.relative_to(run).as_posix()}
    try:
        native._calibration_source(source)
        _budget(run, item["workflow_id"])
        result["native"] = native._native_pipeline(source, attempt, client, renderer=renderer)
        result["status"] = result["native"]["status"]
    except KeyboardInterrupt as error:
        result.update(status="interrupted", reason=str(error))
    except Exception as error:
        result.update(status="failed", reason=f"{type(error).__name__}: {error}")
    try:
        verify_run(run)
        from .artifacts import seal_candidate
        result.update(seal_candidate(run, item["workflow_id"], artifact_root=result["artifact_root"]))
    except Exception as error:
        result.update(status="failed", candidate_seal_error=f"{type(error).__name__}: {error}")
    elapsed, finished = time.perf_counter() - start, utc_now()
    result.update(finished_at=finished, usage=native.usage_summary(run, item["workflow_id"]),
        timing={"attempt_elapsed_seconds": elapsed, "mailbox_wait_seconds": client.wait_seconds,
            "workflow_elapsed_seconds": max(0., native._seconds(finished) - native._seconds(read(workflow / "state.json")["started_at"])),
            "local_processing_seconds": max(0., elapsed - client.wait_seconds)},
        semantic_accuracy="not_evaluated", native_core_modified=False, graph_reused=False, attempts=1)
    write_json(attempt / "worker-result.json", result, immutable=True)
    write_json(workflow / "result.json", result, immutable=True)
    return result


def summarize_calibrations(run_dir):
    run = Path(run_dir).resolve()
    verify_run(run)
    outcomes = []
    for item in read(run / "calibration-plan.json")["cases"]:
        path = native._workflow(run, item["workflow_id"]) / "result.json"
        saved = read(path) if path.exists() else {}
        outcomes.append({"case_id": item["case_id"], "workflow_id": item["workflow_id"],
            "status": saved.get("status", "not_finished"),
            "native_terminal_stage": saved.get("native", {}).get("analysis", {}).get("stage"),
            "result_sha256": sha256(path) if path.exists() else None})
    requests = native._requests(run)
    usage = native.usage_summary(run)
    all_complete = all(o["status"] in {"complete", "diagnostic"} and o["native_terminal_stage"] == "finished" for o in outcomes)
    protocol_ok = bool(requests) and all(_assess(p) == "conformant" for p, _ in requests)
    replay = read(run / "replay/summary.json") if (run / "replay/summary.json").exists() else {}
    replay_ok = replay.get("status") == "passed" and all((run / path).is_file()
        and sha256(run / path) == expected for path, expected in replay.get("bindings", {}).items())
    status = "passed_engineering_only" if all_complete and protocol_ok and replay_ok and not (run / "dispatch-stop.json").exists() else "stopped" if (run / "dispatch-stop.json").exists() else "incomplete"
    return {"schema_version": SCHEMA, "status": status, "cases": outcomes, "runtime": cli.EXPECTED,
        "calibration_only": True, "formal_requests": 0,
        "actual_cli_requests": sum((p / "cli/process-start.json").exists() for p, _ in requests),
        "dispatch_attempts": sum((p / "dispatch.json").exists() for p, _ in requests),
        "protocol_conformance": "conformant" if protocol_ok else "unverified_or_violated",
        "usage": usage, "replay_status": replay.get("status", "not_performed"),
        "semantic_accuracy": "not_evaluated", "human_reference_gate_opened": False}


def replay_calibrations(run_dir, *, include_native=True):
    """Recheck saved CLI evidence and deterministic native replay with zero calls.

    Never dispatches a process or reuses an answer to start a new workflow. The
    original native outputs remain the candidate; replay products are evidence.
    """
    run = Path(run_dir).resolve()
    verify_run(run)
    errors, request_replays, native_replays, bindings = [], [], [], {}
    for directory, request in native._requests(run):
        bindings[str((directory / "request.json").relative_to(run))] = sha256(directory / "request.json")
        try:
            core = (directory / "core-prompt.txt").read_text(encoding="utf-8")
            if (sha256(directory / "core-prompt.txt") != request["core_sha256"]
                    or sha256(directory / "prompt.txt") != request["delivery_sha256"]
                    or (directory / "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8")):
                raise native.ExecutionStop("The exact full native request material changed")
            if not (directory / "response.json").exists():
                request_replays.append({"request_id": request["request_id"], "status": "not_finished"})
                continue
            response, saved = read(directory / "response.json"), read(directory / "receipt.json")
            if not saved.get("raw_receipt_path") or not saved.get("cli_session_id"):
                raise native.ExecutionStop("The actual CLI receipt remains unknown")
            prepared = read(directory / "cli/launch.json")
            answer, fresh = cli.inspect_receipt(saved["raw_receipt_path"], saved["cli_session_id"], prepared,
                stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            if any(saved.get(key) != value for key, value in fresh.items()):
                raise native.ExecutionStop("Allowlisted actual CLI receipt facts differ on replay")
            if response["answer"] != answer or response["answer_sha256"] != (cli.digest(answer) if answer is not None else None):
                raise native.ExecutionStop("The exact saved visible answer changed")
            if _assess(directory) != "conformant":
                raise native.ExecutionStop("The retained actual request is not protocol conformant")
            if (read(directory / "dispatch.json")["command"] != prepared["command"]
                    or prepared["command"] != cli.command(prepared["command"][0], directory / "cli")
                    or saved["process_result_sha256"] != sha256(directory / "cli/process-result.json")
                    or saved["stdout_sha256"] != sha256(directory / "cli/stdout.jsonl")):
                raise native.ExecutionStop("The exact CLI launch/process binding changed")
            request_replays.append({"request_id": request["request_id"], "status": "matched"})
            for name in ("dispatch.json", "response.json", "receipt.json", "cli/launch.json", "cli/process-result.json"):
                bindings[(directory / name).relative_to(run).as_posix()] = sha256(directory / name)
        except Exception as error:
            errors.append({"request_id": request["request_id"], "reason": f"{type(error).__name__}: {error}"})
    for item in read(run / "calibration-plan.json")["cases"]:
        workflow = native._workflow(run, item["workflow_id"])
        if not (workflow / "result.json").exists():
            native_replays.append({"case_id": item["case_id"], "status": "not_finished"})
            continue
        try:
            saved = read(workflow / "result.json")
            bindings[(workflow / "result.json").relative_to(run).as_posix()] = sha256(workflow / "result.json")
            from .artifacts import verify_candidate
            verify_candidate(run, item["workflow_id"], saved)
            if include_native:
                from skillflow.graph.feedback.runner import replay_run
                from skillflow.pipeline import replay_analysis
                attempt = run / saved["artifact_root"]
                graph = replay_run(attempt / "graph")
                analysis = replay_analysis(attempt / "analysis")
                if graph != saved["native"]["graph"] or analysis != saved["native"]["analysis"]:
                    raise native.ExecutionStop("The deterministic native stage decisions differ on replay")
            native_replays.append({"case_id": item["case_id"], "status": "matched" if include_native else "not_requested"})
        except Exception as error:
            errors.append({"case_id": item["case_id"], "reason": f"{type(error).__name__}: {error}"})
    complete = (bool(request_replays) and all(r["status"] == "matched" for r in request_replays)
                and len(native_replays) == 3 and all(r["status"] == "matched" for r in native_replays))
    result = {"schema_version": SCHEMA, "status": "failed" if errors else "passed" if complete else "incomplete",
        "request_replays": request_replays, "native_replays": native_replays, "errors": errors,
        "bindings": bindings, "model_calls": 0, "actual_cli_requests": 0, "semantic_accuracy": "not_evaluated"}
    # A content-addressed assessment retains earlier failed/incomplete replays.
    write_json(run / "replay/assessments" / (canonical_hash(result) + ".json"), result, immutable=True)
    write_json(run / "replay/summary.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "worker", "pending", "dispatch-next", "verify", "summary", "replay"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--original-run")
    parser.add_argument("--decision-record")
    parser.add_argument("--executable")
    parser.add_argument("--case-id", choices=CALIBRATION)
    parser.add_argument("--sessions-dir")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        if not all((args.original_run, args.decision_record, args.executable)):
            parser.error("prepare requires --original-run, --decision-record and --executable")
        result = prepare_calibration_run(args.run_dir, original_run=args.original_run,
            decision_record=args.decision_record, executable=args.executable)
    elif args.command == "worker":
        if not args.case_id:
            parser.error("worker requires --case-id")
        result = run_calibration_worker(args.run_dir, args.case_id)
        result = {k: v for k, v in result.items() if k != "native"}
    elif args.command == "pending":
        result = pending_requests(args.run_dir)
    elif args.command == "dispatch-next":
        result = dispatch_next_once(args.run_dir, sessions_dir=args.sessions_dir)
    elif args.command == "summary":
        result = summarize_calibrations(args.run_dir)
    elif args.command == "replay":
        result = replay_calibrations(args.run_dir)
    else:
        verify_run(args.run_dir)
        result = {"status": "verified", "calibration_only": True, "model_calls": 0}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
