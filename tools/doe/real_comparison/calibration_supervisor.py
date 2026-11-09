"""Sequential local controller for the already authorized CLI-v3 calibrations.

Importing this module starts nothing. A separate preparation freezes this
controller's own plan without changing the core protocol. The first existing
worker/dispatcher are adopted, never relaunched. Only the unchanged v3
dispatch_next_once may issue a semantic request.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from . import cli_amendment_v3 as core
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-cli-v3-calibration-controller-v1"
CASES = ("gh-fix-ci", "netlify-deploy", "transcribe")
ROOT = Path(__file__).resolve().parents[3]


class ControllerStop(RuntimeError):
    def __init__(self, code, reason):
        super().__init__(reason)
        self.code = code


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def worker_command(run_dir, case_id):
    return [str(Path(sys.executable).resolve()), "-u", "-m",
        "tools.doe.real_comparison.cli_amendment_v3", "worker", "--run-dir",
        str(Path(run_dir).resolve()), "--case-id", case_id]


def prepare_controller(run_dir, *, existing_worker_session, existing_dispatcher_session):
    """Freeze a controller plan only; never starts a worker or target process."""
    run = Path(run_dir).resolve()
    core.verify_run(run)
    records = core.read(run / "calibration-plan.json")["cases"]
    if [r["case_id"] for r in records] != list(CASES):
        raise ControllerStop("plan_mismatch", "The controller accepts only the three unchanged ordered native calibrations")
    if any(type(value) is not int or value <= 0 for value in (existing_worker_session, existing_dispatcher_session)):
        raise ControllerStop("adoption_identity_missing", "The adopted root-owned exec sessions must be explicitly identified")
    first = core.native._workflow(run, records[0]["workflow_id"])
    if not (first / "registration.json").is_file() or not (first / "state.json").is_file():
        raise ControllerStop("existing_worker_missing", "The first native worker must already be registered; it will never be started here")
    for record in records[1:]:
        if core.native._workflow(run, record["workflow_id"]).exists():
            raise ControllerStop("future_worker_exists", "A later calibration workflow already exists; automatic restart or replacement is forbidden")
    directory = run / "controller"
    if directory.exists():
        raise ControllerStop("controller_plan_exists", "A controller directory already exists; preserve it for explicit investigation")
    plan = {"schema_version": SCHEMA, "calibration_only": True, "created_at": utc_now(),
        "controller_implementation": str(Path(__file__).resolve()), "controller_sha256": sha256(__file__),
        "core_protocol_freeze_sha256": sha256(run / "cli-protocol-freeze.json"),
        "core_calibration_plan_sha256": sha256(run / "calibration-plan.json"),
        "core_amendment_sha256": sha256(run / "amendment.json"),
        "python_executable": str(Path(sys.executable).resolve()), "python_executable_sha256": sha256(sys.executable),
        "working_directory": str(ROOT), "cases": [
            {**record, "worker_policy": "adopt_existing_without_restart" if index == 0 else "launch_once_separate_process",
             "worker_command": None if index == 0 else worker_command(run, record["case_id"])}
            for index, record in enumerate(records)],
        "existing_worker_exec_session": existing_worker_session,
        "existing_dispatcher_exec_session": existing_dispatcher_session,
        "existing_output_retention": "The root-owned exec sessions retain their streams; this controller cannot retroactively redirect an existing process.",
        "dispatch_api": "tools.doe.real_comparison.cli_amendment_v3.dispatch_next_once",
        "dispatch_parallelism": 1, "automatic_worker_retry": False, "automatic_request_retry": False,
        "core_budget_or_protocol_changes": False, "finalization": "One zero-model replay followed by one summary, including after failure."}
    write_json(directory / "plan.json", plan, immutable=True)
    write_json(directory / "plan-freeze.json", {"schema_version": SCHEMA,
        "plan_sha256": sha256(directory / "plan.json"), "controller_sha256": sha256(__file__)}, immutable=True)
    return {"status": "controller_prepared_no_process_started", "plan": str(directory / "plan.json"),
            "controller_sha256": sha256(__file__), "model_calls": 0, "worker_processes_started": 0}


def verify_controller(run_dir):
    run = Path(run_dir).resolve()
    core.verify_run(run)
    plan, freeze = read(run / "controller/plan.json"), read(run / "controller/plan-freeze.json")
    if (plan.get("schema_version") != SCHEMA or plan.get("calibration_only") is not True
            or freeze.get("plan_sha256") != sha256(run / "controller/plan.json")
            or freeze.get("controller_sha256") != sha256(__file__) or plan.get("controller_sha256") != sha256(__file__)):
        raise ControllerStop("controller_binding_changed", "The separately frozen controller implementation or plan changed")
    bindings = {"core_protocol_freeze_sha256": "cli-protocol-freeze.json",
        "core_calibration_plan_sha256": "calibration-plan.json", "core_amendment_sha256": "amendment.json"}
    if any(plan.get(key) != sha256(run / path) for key, path in bindings.items()):
        raise ControllerStop("core_binding_changed", "The controller's unchanged CLI-v3 run binding changed")
    if (plan["python_executable"] != str(Path(sys.executable).resolve())
            or plan["python_executable_sha256"] != sha256(sys.executable)):
        raise ControllerStop("worker_interpreter_changed", "The planned local worker interpreter changed")
    return plan


def _event(run, event, **fields):
    # Never serialize visible answers, prompts, raw receipts or reasoning here.
    record = {"at": utc_now(), "event": event, **fields}
    with (Path(run) / "controller/events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


@contextmanager
def _lock(run):
    path = Path(run) / "controller/controller.lock"
    try:
        stream = path.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise ControllerStop("controller_already_active", "Another controller or an interrupted controller lock exists; no duplicate process was started") from error
    try:
        stream.write(utc_now()); stream.close()
        yield
    finally:
        path.unlink(missing_ok=True)


def _guards(run, item, *, now):
    run = Path(run)
    if (run / "dispatch-stop.json").exists():
        raise ControllerStop("global_actual_request_stop", "The unchanged CLI-v3 dispatcher retained a failed or unaccountable actual request")
    workflow = core.native._workflow(run, item["workflow_id"])
    result = workflow / "result.json"
    if (workflow / "state.json").exists() and not result.exists():
        if now - core.native._seconds(read(workflow / "state.json")["started_at"]) >= core.LIMITS["workflow_seconds"]:
            raise ControllerStop("workflow_six_hour_limit", "The active native workflow reached its unchanged six-hour elapsed limit")
        core._budget(run, item["workflow_id"])
    outstanding = []
    for directory, request in core.native._requests(run):
        if request.get("mode") != "calibration":
            raise ControllerStop("unexpected_formal_request", "A calibration-only controller cannot service a formal request")
        if (directory / "stop.json").exists():
            raise ControllerStop("retained_request_stop", "A retained request stop forbids further controller dispatch")
        if (directory / "response.json").exists():
            if core._assess(directory) != "conformant":
                raise ControllerStop("actual_response_rejected", "A retained actual response failed protocol, runtime or usage verification")
        elif (directory / "dispatch.json").exists():
            dispatched = read(directory / "dispatch.json")
            if now - core.native._seconds(dispatched["dispatched_at"]) >= core.LIMITS["outstanding_request_seconds"]:
                raise ControllerStop("request_45_minute_limit", "An existing actual request reached the unchanged 45-minute outstanding limit; its dispatcher owns process termination")
            outstanding.append(request["request_id"])
    if len(outstanding) > 1:
        raise ControllerStop("parallel_actual_requests", "More than one actual CLI request is outstanding")
    lock = run / "dispatcher.lock"
    if lock.exists() and not outstanding:
        if now - lock.stat().st_mtime >= core.LIMITS["outstanding_request_seconds"]:
            raise ControllerStop("stale_dispatcher_lock", "An existing dispatcher lock reached the outstanding limit; it was preserved and not removed")
    return outstanding


def _launch_worker(run, item, *, popen):
    workflow = core.native._workflow(run, item["workflow_id"])
    directory = Path(run) / "controller/workers" / item["case_id"]
    if workflow.exists() or directory.exists():
        raise ControllerStop("worker_reuse_forbidden", "A later worker identity or launch record already exists; no retry was attempted")
    directory.mkdir(parents=True)
    command = worker_command(run, item["case_id"])
    if command != item["worker_command"]:
        raise ControllerStop("worker_command_changed", "The exact local worker command differs from the separately frozen controller plan")
    write_json(directory / "launch-intent.json", {"command": command, "cwd": str(ROOT),
        "at": utc_now(), "worker_process_only": True, "model_request": False}, immutable=True)
    stdout, stderr = (directory / "stdout.txt").open("xb"), (directory / "stderr.txt").open("xb")
    try:
        process = popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        write_json(directory / "process-start.json", {"pid": process.pid, "at": utc_now(),
            "worker_process_only": True, "model_request": False}, immutable=True)
        _event(run, "worker_started", case_id=item["case_id"], workflow_id=item["workflow_id"], pid=process.pid)
        return {"process": process, "stdout": stdout, "stderr": stderr, "directory": directory,
                "case_id": item["case_id"], "closed": False, "launched_monotonic": time.monotonic()}
    except BaseException:
        stdout.close(); stderr.close()
        raise


def _close_worker(handle, *, stop=False):
    if handle is None or handle["closed"]:
        return
    process = handle["process"]
    termination = None
    try:
        if process.poll() is None:
            try:
                process.wait(timeout=5 if stop else 30)
            except subprocess.TimeoutExpired:
                if not stop:
                    raise ControllerStop("worker_did_not_exit", "A finished native worker did not exit within its local process-close window")
                process.terminate(); termination = "terminated_owned_worker"
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5); termination = "killed_owned_worker"
    finally:
        if process.poll() is not None:
            handle["stdout"].close(); handle["stderr"].close(); handle["closed"] = True
            write_json(handle["directory"] / "process-result.json", {"returncode": process.poll(),
                "at": utc_now(), "termination": termination, "stdout_sha256": sha256(handle["directory"] / "stdout.txt"),
                "stderr_sha256": sha256(handle["directory"] / "stderr.txt")}, immutable=True)


def run_controller(run_dir, *, poll_seconds=1., popen=None, sleep=time.sleep, now=time.time):
    """Adopt case one, service exact requests sequentially, launch cases two/three once.

    Worker Popen calls are separate local processes. This controller never calls
    the native worker in a thread and never launches or replaces the first one.
    """
    if not 0 < poll_seconds <= 30:
        raise ValueError("Controller polling must be positive and at most 30 seconds")
    run = Path(run_dir).resolve()
    plan = verify_controller(run)
    if (run / "controller/result.json").exists():
        return read(run / "controller/result.json")
    with _lock(run):
        handles, completed, stop, replay, summary = [], [], None, None, None
        _event(run, "controller_started", existing_worker_exec_session=plan["existing_worker_exec_session"],
            existing_dispatcher_exec_session=plan["existing_dispatcher_exec_session"])
        try:
            for index, item in enumerate(plan["cases"]):
                verify_controller(run)
                _guards(run, item, now=now())
                handle = None
                if index == 0:
                    _event(run, "existing_worker_adopted", case_id=item["case_id"], workflow_id=item["workflow_id"],
                        exec_session=plan["existing_worker_exec_session"], restarted=False)
                else:
                    handle = _launch_worker(run, item, popen=popen or subprocess.Popen)
                    handles.append(handle)
                workflow = core.native._workflow(run, item["workflow_id"])
                while True:
                    outstanding = _guards(run, item, now=now())
                    result_path = workflow / "result.json"
                    if result_path.exists():
                        result = read(result_path)
                        if (result.get("status") not in {"complete", "diagnostic"}
                                or result.get("native", {}).get("analysis", {}).get("stage") != "finished"):
                            raise ControllerStop("native_workflow_failed", "A native workflow did not reach its finished stage; later calibration cases will not start")
                        elapsed = result.get("timing", {}).get("workflow_elapsed_seconds")
                        if type(elapsed) in (int, float) and elapsed >= core.LIMITS["workflow_seconds"]:
                            raise ControllerStop("workflow_six_hour_limit", "The finished native workflow exhausted the unchanged six-hour elapsed limit")
                        if outstanding or (run / "dispatcher.lock").exists():
                            sleep(poll_seconds)
                            continue
                        _close_worker(handle)
                        if handle is not None and handle["process"].poll() != 0:
                            raise ControllerStop("worker_process_failed", "The local native worker exited unsuccessfully; no later case will start")
                        completed.append(item["case_id"])
                        _event(run, "native_workflow_finished", case_id=item["case_id"], status=result["status"],
                            result_sha256=sha256(result_path))
                        break
                    if handle is not None:
                        if handle["process"].poll() is not None:
                            raise ControllerStop("worker_exited_without_result", "A local worker exited before committing its terminal result")
                        if not (workflow / "state.json").exists() and time.monotonic() - handle["launched_monotonic"] >= 60:
                            raise ControllerStop("worker_registration_missing", "A launched local worker did not register; its launch is retained without retry")
                    if outstanding or (run / "dispatcher.lock").exists():
                        sleep(poll_seconds)
                        continue
                    pending = core.pending_requests(run)
                    if pending:
                        if any(request["workflow_id"] != item["workflow_id"] for request in pending):
                            raise ControllerStop("unexpected_pending_workflow", "A pending request belongs to a different sequential workflow")
                        _event(run, "dispatch_requested", case_id=item["case_id"], request_id=pending[0]["request_id"])
                        try:
                            response = core.dispatch_next_once(run)
                        except core.native.ExecutionStop as error:
                            if (run / "dispatcher.lock").exists() and "Another dispatcher" in str(error):
                                _event(run, "external_dispatcher_won_lock", case_id=item["case_id"])
                                sleep(poll_seconds)
                                continue
                            raise
                        _event(run, "dispatch_returned", case_id=item["case_id"], status=response.get("status"),
                            request_id=response.get("request_id"), cli_session_id=response.get("cli_session_id"),
                            response_ids=response.get("response_ids", []))
                        if response.get("status") not in {"accepted", "no_pending_request"}:
                            raise ControllerStop("actual_dispatch_stopped", "The unchanged dispatcher stopped after an actual request; no retry or later case is permitted")
                    else:
                        sleep(poll_seconds)
        except BaseException as error:
            stop = {"code": error.code if isinstance(error, ControllerStop) else "controller_exception",
                "reason": f"{type(error).__name__}: {error}", "at": utc_now(), "completed_cases": completed,
                "core_dispatch_stop_present": (run / "dispatch-stop.json").exists(),
                "automatic_retry": False, "core_protocol_modified": False}
            write_json(run / "controller/controller-stop.json", stop, immutable=True)
            _event(run, "controller_stopped", code=stop["code"], completed_cases=completed)
        finally:
            for handle in handles:
                try:
                    _close_worker(handle, stop=True)
                except Exception as error:
                    _event(run, "owned_worker_close_failed", case_id=handle["case_id"], error_type=type(error).__name__)
            # An externally owned first worker is never killed or restarted.
            # The core dispatcher retains its own process timeout/termination.
            try:
                replay = core.replay_calibrations(run)
            except Exception as error:
                replay = {"status": "failed", "error": f"{type(error).__name__}: {error}", "model_calls": 0}
            write_json(run / "controller/final-replay.json", replay, immutable=True)
            try:
                summary = core.summarize_calibrations(run)
            except Exception as error:
                summary = {"status": "failed", "error": f"{type(error).__name__}: {error}", "formal_requests": 0}
            write_json(run / "controller/final-summary.json", summary, immutable=True)
        success = stop is None and len(completed) == 3 and replay.get("status") == "passed" and summary.get("status") == "passed_engineering_only"
        if not success and stop is None:
            stop = {"code": "engineering_replay_or_summary_failed", "reason": "All native cases ended but final engineering replay/summary did not pass",
                "at": utc_now(), "automatic_retry": False, "core_protocol_modified": False}
            write_json(run / "controller/controller-stop.json", stop, immutable=True)
        result = {"schema_version": SCHEMA, "status": "complete_engineering_only" if success else "stopped",
            "completed_cases": completed, "controller_stop": stop, "final_replay_status": replay.get("status"),
            "final_summary_status": summary.get("status"), "worker_processes_started": len(handles),
            "existing_first_worker_restarted": False, "formal_requests": 0, "semantic_accuracy": "not_evaluated"}
        write_json(run / "controller/result.json", result, immutable=True)
        _event(run, "controller_finished", status=result["status"], completed_cases=completed)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "run"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--existing-worker-session", type=int)
    parser.add_argument("--existing-dispatcher-session", type=int)
    parser.add_argument("--poll-seconds", type=float, default=1.)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare_controller(args.run_dir, existing_worker_session=args.existing_worker_session,
            existing_dispatcher_session=args.existing_dispatcher_session)
    elif args.command == "verify":
        verify_controller(args.run_dir)
        result = {"status": "controller_verified_no_process_started", "model_calls": 0}
    else:
        result = run_controller(args.run_dir, poll_seconds=args.poll_seconds)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
