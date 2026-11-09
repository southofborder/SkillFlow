"""Sequential controller tests use fictional workers and zero model requests."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import time

import pytest

from tools.doe.real_comparison import calibration_supervisor as supervisor
from tools.doe.real_comparison.protocol import write_json


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    run = tmp_path / "fictional-v3-run"
    cases = [{"case_id": name, "workflow_id": "synthetic_" + name.replace("-", "_"),
        "source_sha256": "fictional-source-" + name, "method": "skillflow", "mode": "calibration"}
        for name in supervisor.CASES]
    write_json(run / "calibration-plan.json", {"calibration_only": True, "cases": cases})
    write_json(run / "cli-protocol-freeze.json", {"fictional": True})
    write_json(run / "amendment.json", {"fictional": True})
    monkeypatch.setattr(supervisor.core, "verify_run", lambda path: {})
    monkeypatch.setattr(supervisor.core, "_budget", lambda *a, **k: None)
    calls = {"dispatch": [], "popen": [], "replay": [], "summary": []}
    monkeypatch.setattr(supervisor.core, "replay_calibrations", lambda p: calls["replay"].append(p) or {"status": "passed", "model_calls": 0})
    monkeypatch.setattr(supervisor.core, "summarize_calibrations", lambda p: calls["summary"].append(p) or {"status": "passed_engineering_only", "formal_requests": 0})

    def forbid_process(*a, **k):
        pytest.fail("A controller test attempted a real local process or model request")
    monkeypatch.setattr(supervisor.subprocess, "Popen", forbid_process)

    def register(item):
        workflow = supervisor.core.native._workflow(run, item["workflow_id"])
        write_json(workflow / "registration.json", item)
        write_json(workflow / "state.json", {"started_at": supervisor.utc_now()})
        return workflow

    def queue(item, index=1, dispatched=False):
        directory = run / "mailbox/requests" / f"{item['workflow_id']}_q{index:03d}"
        write_json(directory / "request.json", {"request_id": directory.name, "workflow_id": item["workflow_id"], "mode": "calibration"})
        if dispatched:
            write_json(directory / "dispatch.json", {"dispatched_at": supervisor.utc_now()})
        return directory

    def accept(directory):
        write_json(directory / "receipt.json", {"protocol_status": "conformant", "configuration_verified": True,
            "provider_verified": True, "usage_verified": True})
        write_json(directory / "response.json", {"accepted": True})

    def finish(item, status="complete"):
        path = supervisor.core.native._workflow(run, item["workflow_id"])
        write_json(path / "result.json", {"status": status, "native": {"analysis": {"stage": "finished" if status == "complete" else "graph"}},
            "timing": {"workflow_elapsed_seconds": 1}})

    register(cases[0])
    supervisor.prepare_controller(run, existing_worker_session=69874, existing_dispatcher_session=61464)
    return run, cases, calls, register, queue, accept, finish


def test_adopts_any_active_first_sequence_and_launches_later_workers_once_in_separate_processes(scenario, monkeypatch):
    run, cases, calls, register, queue, accept, finish = scenario
    existing = queue(cases[0], 7, dispatched=True)
    (run / "dispatcher.lock").write_text(supervisor.utc_now(), encoding="utf-8")
    state = {"external_finished": False}

    def tick(seconds):
        assert seconds <= 30
        assert not calls["popen"] and not calls["dispatch"]
        assert (run / "dispatcher.lock").exists()
        accept(existing)
        (run / "dispatcher.lock").unlink()
        queue(cases[0], 8)
        state["external_finished"] = True

    def dispatch(path):
        assert state["external_finished"] and not (run / "dispatcher.lock").exists()
        pending = supervisor.core.pending_requests(run)
        assert len(pending) == 1
        request = pending[0]
        calls["dispatch"].append(request["request_id"])
        directory = run / "mailbox/requests" / request["request_id"]
        write_json(directory / "dispatch.json", {"dispatched_at": supervisor.utc_now()})
        accept(directory)
        item = next(item for item in cases if item["workflow_id"] == request["workflow_id"])
        finish(item)
        return {"status": "accepted", "request_id": request["request_id"], "response_ids": ["fictional-response"]}

    def popen(command, **kwargs):
        case = command[-1]
        assert case != "gh-fix-ci"
        assert kwargs["stdin"] == subprocess.DEVNULL
        calls["popen"].append(case)
        item = next(item for item in cases if item["case_id"] == case)
        register(item); queue(item)
        kwargs["stdout"].write(b"Synthetic local worker started.\n"); kwargs["stdout"].flush()

        class Process:
            pid = 9000 + len(calls["popen"])
            def poll(self):
                return 0 if (supervisor.core.native._workflow(run, item["workflow_id"]) / "result.json").exists() else None
            def wait(self, timeout):
                assert self.poll() == 0
                return 0
        return Process()

    monkeypatch.setattr(supervisor.core, "dispatch_next_once", dispatch)
    result = supervisor.run_controller(run, popen=popen, sleep=tick)
    assert result["status"] == "complete_engineering_only"
    assert result["completed_cases"] == list(supervisor.CASES)
    assert calls["popen"] == ["netlify-deploy", "transcribe"]
    assert calls["dispatch"] == ["synthetic_gh_fix_ci_q008", "synthetic_netlify_deploy_q001", "synthetic_transcribe_q001"]
    assert len(calls["replay"]) == len(calls["summary"]) == 1
    assert result["worker_processes_started"] == 2 and result["existing_first_worker_restarted"] is False
    for name in calls["popen"]:
        assert (run / "controller/workers" / name / "stdout.txt").is_file()
        assert (run / "controller/workers" / name / "stderr.txt").is_file()
        assert (run / "controller/workers" / name / "process-result.json").is_file()
    assert not (run / "controller/controller-stop.json").exists()
    assert supervisor.run_controller(run) == result
    assert len(calls["replay"]) == len(calls["summary"]) == 1


@pytest.mark.parametrize("failure,expected", [("global", "global_actual_request_stop"),
    ("native", "native_workflow_failed"), ("request_timeout", "request_45_minute_limit"),
    ("workflow_timeout", "workflow_six_hour_limit"), ("receipt", "actual_response_rejected")])
def test_failure_stops_later_cases_with_distinct_controller_record_and_one_finalization(scenario, failure, expected):
    run, cases, calls, register, queue, accept, finish = scenario
    if failure == "global":
        write_json(run / "dispatch-stop.json", {"reason": "Fictional retained core failure."})
    elif failure == "native":
        finish(cases[0], "failed")
    elif failure == "request_timeout":
        directory = queue(cases[0], 9, dispatched=True)
        write_json(directory / "dispatch.json", {"dispatched_at": (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()})
    elif failure == "workflow_timeout":
        workflow = supervisor.core.native._workflow(run, cases[0]["workflow_id"])
        write_json(workflow / "state.json", {"started_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()})
    else:
        directory = queue(cases[0], dispatched=True)
        write_json(directory / "receipt.json", {"protocol_status": "violated", "usage_verified": False})
        write_json(directory / "response.json", {"accepted": False})
    old_stop = (run / "dispatch-stop.json").read_bytes() if (run / "dispatch-stop.json").exists() else None
    result = supervisor.run_controller(run)
    assert result["status"] == "stopped" and result["controller_stop"]["code"] == expected
    assert result["worker_processes_started"] == 0
    assert len(calls["replay"]) == len(calls["summary"]) == 1
    assert (run / "controller/controller-stop.json").exists()
    assert ((run / "dispatch-stop.json").read_bytes() if (run / "dispatch-stop.json").exists() else None) == old_stop


def test_native_worker_process_exit_is_not_retried_and_transcribe_never_starts(scenario):
    run, cases, calls, register, queue, accept, finish = scenario
    finish(cases[0])
    def popen(command, **kwargs):
        calls["popen"].append(command[-1])
        class Process:
            pid = 9901
            def poll(self): return 7
        return Process()
    result = supervisor.run_controller(run, popen=popen)
    assert result["controller_stop"]["code"] == "worker_exited_without_result"
    assert calls["popen"] == ["netlify-deploy"] and not calls["dispatch"]
    assert len(calls["replay"]) == len(calls["summary"]) == 1


def test_two_controllers_cannot_adopt_or_dispatch_the_same_run(scenario):
    run = scenario[0]
    (run / "controller/controller.lock").write_text("Fictional existing controller.", encoding="utf-8")
    with pytest.raises(supervisor.ControllerStop, match="Another controller"):
        supervisor.run_controller(run)
    assert not scenario[2]["replay"] and not scenario[2]["dispatch"]


def test_controller_plan_drift_is_rejected_before_any_worker_or_model_request(scenario):
    run = scenario[0]
    plan = read_plan = supervisor.read(run / "controller/plan.json")
    plan["cases"][1]["worker_command"].append("--unexpected")
    write_json(run / "controller/plan.json", plan)
    with pytest.raises(supervisor.ControllerStop, match="plan changed"):
        supervisor.run_controller(run)
    assert not scenario[2]["popen"] and not scenario[2]["replay"]


def test_dispatcher_race_is_waited_without_duplicate_or_replacement_request(scenario, monkeypatch):
    run, cases, calls, register, queue, accept, finish = scenario
    directory = queue(cases[0], 11)
    def dispatch(path):
        calls["dispatch"].append(directory.name)
        (run / "dispatcher.lock").write_text(supervisor.utc_now(), encoding="utf-8")
        raise supervisor.core.native.ExecutionStop("Another dispatcher is active; no duplicate CLI launch was made")
    def tick(seconds):
        accept(directory); finish(cases[0], "failed")
        (run / "dispatcher.lock").unlink()
    monkeypatch.setattr(supervisor.core, "dispatch_next_once", dispatch)
    result = supervisor.run_controller(run, sleep=tick)
    assert result["controller_stop"]["code"] == "native_workflow_failed"
    assert calls["dispatch"] == [directory.name] and not calls["popen"]
    events = [json.loads(line) for line in (run / "controller/events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sum(event["event"] == "external_dispatcher_won_lock" for event in events) == 1
