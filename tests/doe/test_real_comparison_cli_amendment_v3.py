"""Isolated v3 orchestration checks with fictional receipts and processes only."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import threading
import time

import pytest

from tools.doe.real_comparison import cli_adapter_v3 as adapter
from tools.doe.real_comparison import cli_amendment_v3 as amendment
from tools.doe.real_comparison import execution as native
from tools.doe.real_comparison.protocol import prepare_protocol, sha256, write_json


@pytest.fixture
def prepared_run(tmp_path, monkeypatch):
    previous = tmp_path / "historical-v1"
    prepare_protocol(previous)
    write_json(previous / "evaluation-rules-freeze.json", {"files": {}, "implementation_files": {}})
    write_json(previous / "mailbox/retained-failure.json", {"status": "delivery_violation", "usage": None})
    write_json(previous / "transport-inspection/proposed-cli-probe/receipt.json", {"status": "feasibility_only"})
    write_json(previous / "approvals/do-not-import.json", {"fictional_marker": "Never an attestation"})
    write_json(previous / "selection.json", {"fictional_marker": "Never a v2 cohort"})
    baseline = tmp_path / "baseline"
    for name in amendment.CALIBRATION:
        source = baseline / name / "SKILL.md"
        source.parent.mkdir(parents=True)
        source.write_text("# Synthetic source\nPreserve the quoted input 原文 and source/file.txt.\n", encoding="utf-8")
    monkeypatch.setattr(amendment, "CALIBRATION_SOURCE_ROOT", baseline)
    monkeypatch.setattr(native, "_calibration_source", lambda p: Path(p).name)
    monkeypatch.setattr(native, "verify_evaluation_rules", lambda p: {})
    monkeypatch.setattr(native, "verify_production_code", lambda p: {})

    def snapshot(run):
        write_json(Path(run) / "production-code-freeze.json", {"files": {}, "fictional": True}, immutable=True)

    monkeypatch.setattr(native, "snapshot_production_code", snapshot)
    executable = tmp_path / "fictional-codex.exe"
    executable.write_bytes(b"A fictional binary, never executed.")
    monkeypatch.setattr(adapter, "PINNED_EXECUTABLE_SHA256", sha256(executable))
    monkeypatch.setattr(adapter, "PINNED_BASE_INSTRUCTIONS_SHA256", adapter.digest("Synthetic common base."))
    monkeypatch.setattr(adapter, "PINNED_DEVELOPER_SEGMENTS", ((adapter.digest("Synthetic common developer."),),))
    prior = tmp_path / "historical-cli-v2"
    write_json(prior / "cli-protocol.json", {"schema_version": "skillflow-real-comparison-cli-v2"})
    write_json(prior / "dispatch-stop.json", {"automatic_retry": False,
        "reason": "Fictional retained v2 protocol failure; never reclassified."})
    write_json(prior / "retained-failure.json", {"protocol_status": "violated", "fictional": True})
    proposal = tmp_path / "synthetic-v3-proposal.json"
    write_json(proposal, {"state": "fictional_test_only", "option": amendment.OPTION})
    monkeypatch.setattr(amendment, "PROPOSAL_SHA256", sha256(proposal))
    monkeypatch.setattr(amendment, "PRIOR_DISPATCH_STOP_SHA256", sha256(prior / "dispatch-stop.json"))
    decision = tmp_path / "adoption.json"
    write_json(decision, {"schema_version": amendment.AUTHORIZATION_SCHEMA,
        "state": "adopted", "user_authorized": True, "selected_option": amendment.OPTION,
        "proposal_sha256": sha256(proposal),
        "prior_dispatch_stop_sha256": sha256(prior / "dispatch-stop.json"),
        "calibration_only": True, "formal_dispatch_permitted": False, "automatic_retry": False,
        "user_confirmation": {"quotation": "Fictional unit-test authorization, never real consent.",
                              "conversation_reference": "synthetic-test-only"}})
    before = {str(p): sha256(p) for p in previous.rglob("*") if p.is_file()}
    run = tmp_path / "calibration-cli-v3-fictional"
    result = amendment.prepare_calibration_run(run, original_run=previous, prior_cli_run=prior,
        proposal=proposal, decision_record=decision, executable=executable)

    def forbid_process(*args, **kwargs):
        pytest.fail("A calibration unit test attempted a real subprocess or target request")

    monkeypatch.setattr(adapter.subprocess, "Popen", forbid_process)
    return run, previous, result, before, tmp_path / "sessions"


def test_fresh_run_preserves_history_without_importing_formal_materials_or_human_records(prepared_run):
    run, previous, result, before, _ = prepared_run
    assert result["status"] == "prepared_calibration_only" and result["formal_requests"] == 0
    assert len(result["cases"]) == 3
    assert {p["case_id"] for p in result["cases"]} == set(amendment.CALIBRATION)
    assert len({p["workflow_id"] for p in result["cases"]}) == 3
    assert all(p["from_source"] and not p["graph_reuse"] for p in result["cases"])
    assert {str(p): sha256(p) for p in previous.rglob("*") if p.is_file()} == before
    assert (run / "inherited-v1/protocol.json").read_bytes() == (previous / "protocol.json").read_bytes()
    assert amendment.read(run / "cli-protocol.json")["runtime"]["transport"] == adapter.TRANSPORT
    assert not any((run / name).exists() for name in ("selection.json", "cases", "approvals", "mailbox"))
    assert amendment.verify_run(run)
    saved = amendment.read(run / "amendment.json")
    prior = Path(saved["prior_cli_run"])
    assert {p.relative_to(prior).as_posix(): sha256(p) for p in prior.rglob("*") if p.is_file()} == saved["preserved_v2_files"]
    assert amendment.read(prior / "retained-failure.json")["protocol_status"] == "violated"
    assert all(item["workflow_id"].startswith("calibration_cli_v3_") for item in result["cases"])
    assert saved["prior_failure_reclassified"] is False and saved["automatic_retry"] is False
    with pytest.raises(native.ExecutionStop, match="existing"):
        amendment.prepare_calibration_run(run, original_run=previous,
            prior_cli_run=amendment.read(run / "amendment.json")["prior_cli_run"],
            proposal=run / "authorization/cli-v3-proposal.json",
            decision_record=run / "authorization/adoption.json", executable=amendment.read(run / "amendment.json")["executable"])


@pytest.mark.parametrize("field,value", [
    ("schema_version", "skillflow-real-comparison-cli-v2"),
    ("selected_option", "B_two_catalog_inventory_normalization"),
    ("proposal_sha256", "0" * 64), ("prior_dispatch_stop_sha256", "0" * 64),
    ("user_authorized", False), ("calibration_only", False),
    ("formal_dispatch_permitted", True), ("automatic_retry", True),
    ("user_confirmation", {}),
])
def test_new_hash_bound_explicit_authorization_is_required_before_run_creation(prepared_run, field, value):
    run, previous = prepared_run[:2]
    saved = amendment.read(run / "amendment.json")
    decision = amendment.read(run / "authorization/adoption.json")
    decision[field] = value
    invalid = run.parent / "fictional-invalid-authorization.json"
    write_json(invalid, decision)
    candidate = run.parent / "must-not-be-prepared"
    with pytest.raises(native.ExecutionStop, match="authorization|confirmation"):
        amendment.prepare_calibration_run(candidate, original_run=previous,
            prior_cli_run=saved["prior_cli_run"], proposal=run / "authorization/cli-v3-proposal.json",
            decision_record=invalid, executable=saved["executable"])
    assert not candidate.exists()


def test_old_v2_adoption_and_unbound_proposal_cannot_authorize_v3(prepared_run):
    run, previous = prepared_run[:2]
    saved = amendment.read(run / "amendment.json")
    old = run.parent / "fictional-v2-adoption.json"
    write_json(old, {"state": "adopted", "user_authorized": True})
    candidate = run.parent / "not-authorized-v3"
    common = {"original_run": previous, "prior_cli_run": saved["prior_cli_run"],
              "proposal": run / "authorization/cli-v3-proposal.json", "executable": saved["executable"]}
    with pytest.raises(native.ExecutionStop, match="new explicit"):
        amendment.prepare_calibration_run(candidate, decision_record=old, **common)
    altered = run.parent / "unbound-proposal.json"
    altered.write_text('{"fictional":"changed proposal"}', encoding="utf-8")
    common["proposal"] = altered
    with pytest.raises(native.ExecutionStop, match="proposal differs"):
        amendment.prepare_calibration_run(candidate, decision_record=run / "authorization/adoption.json", **common)
    assert not candidate.exists()


def test_prior_failure_or_history_mutation_closes_verification_without_dispatch(prepared_run):
    run = prepared_run[0]
    prior = Path(amendment.read(run / "amendment.json")["prior_cli_run"])
    retained = prior / "retained-failure.json"
    retained.write_text('{"protocol_status":"conformant"}', encoding="utf-8")
    with pytest.raises(native.ExecutionStop, match="historical file changed"):
        amendment.verify_run(run)
    assert not (run / "mailbox").exists()


def test_preserved_v2_module_bytes_remain_exact_and_no_normalization_is_enabled():
    for relative, expected in amendment.PRESERVED_V2_MODULES.items():
        assert sha256(amendment.ROOT / relative) == expected
    runtime = amendment.effective_policy()["runtime"]
    assert runtime["inventory_normalization"] is False
    assert runtime["harness_policy"] == amendment.OPTION
    assert amendment.effective_policy()["run_scope"]["formal_dispatch"] == "permanently_forbidden"


def _request(run, *, mode="calibration", workflow_id=None, sequence=1):
    item = amendment.read(run / "calibration-plan.json")["cases"][0]
    workflow_id = workflow_id or item["workflow_id"]
    workflow = native._workflow(run, workflow_id)
    write_json(workflow / "registration.json", {**item, "mode": "calibration", "source_path": str(run / item["source_path"])})
    if not (workflow / "state.json").exists():
        write_json(workflow / "state.json", {"started_at": amendment.utc_now()})
    directory = run / "mailbox/requests" / f"{workflow_id}_q{sequence:03d}"
    core = "Read this synthetic source quotation 原文 from source/file.txt."
    delivery = native.ENVELOPE.replace("{core}", core)
    directory.mkdir(parents=True)
    (directory / "core-prompt.txt").write_bytes(core.encode("utf-8"))
    (directory / "prompt.txt").write_bytes(delivery.encode("utf-8"))
    record = {"request_id": directory.name, "workflow_id": workflow_id, "mode": mode,
        "core_sha256": adapter.digest(core), "delivery_sha256": adapter.digest(delivery),
        "reference_tokens": 100, "transport": adapter.TRANSPORT}
    write_json(directory / "request.json", record)
    return directory, record


def test_formal_requests_are_permanently_forbidden_even_with_fictional_gate_flags(prepared_run):
    run = prepared_run[0]
    directory, request = _request(run, mode="formal")
    write_json(run / "gate.json", {"state": "approved", "human_attestations": []})
    with pytest.raises(native.ExecutionStop, match="permanently forbidden"):
        amendment.authorize_dispatch(run, request["request_id"])
    assert not (directory / "dispatch.json").exists()


def test_changed_complete_prompt_is_preserved_and_closes_dispatch_without_a_process(prepared_run):
    run = prepared_run[0]
    directory, request = _request(run)
    (directory / "prompt.txt").write_bytes(b"A changed incomplete delivery.")
    with pytest.raises(native.ExecutionStop, match="changed"):
        amendment.dispatch_next_once(run)
    assert (directory / "stop.json").exists() and (run / "dispatch-stop.json").exists()
    assert not (directory / "cli").exists()
    assert amendment.dispatch_next_once(run)["status"] == "dispatch_closed"


def test_versioned_adapter_or_input_drift_is_rejected(prepared_run):
    run = prepared_run[0]
    item = amendment.read(run / "calibration-plan.json")["cases"][0]
    (run / item["source_path"] / "SKILL.md").write_text("Changed source.", encoding="utf-8")
    with pytest.raises(native.ExecutionStop, match="changed"):
        amendment.verify_run(run)


def test_six_hour_and_64_actual_request_caps_stop_dispatch(prepared_run):
    run = prepared_run[0]
    directory, request = _request(run)
    workflow_id = request["workflow_id"]
    state = native._workflow(run, workflow_id) / "state.json"
    write_json(state, {"started_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()})
    with pytest.raises(native.ExecutionStop, match="six-hour"):
        amendment._budget(run, workflow_id, dispatching=True)
    write_json(state, {"started_at": amendment.utc_now()})
    for index in range(1, 65):
        path = run / "mailbox/requests" / f"{workflow_id}_q{index:03d}"
        if index > 1:
            _, _ = _request(run, workflow_id=workflow_id, sequence=index)
        write_json(path / "dispatch.json", {"dispatched_at": amendment.utc_now()})
    with pytest.raises(native.ExecutionStop, match="64 actual CLI"):
        amendment._budget(run, workflow_id, dispatching=True)


@pytest.mark.parametrize("change,expected", [("tokens", "eight-million"), ("unknown", "Unknown"),
                                          ("hung", "45-minute"), ("outstanding", "unresolved")])
def test_reported_token_unknown_usage_and_outstanding_limits_fail_closed(prepared_run, change, expected):
    run = prepared_run[0]
    directory, request = _request(run)
    write_json(directory / "dispatch.json", {"dispatched_at":
        (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat() if change == "hung" else amendment.utc_now()})
    if change in {"tokens", "unknown"}:
        counters = {key: 0 for key in adapter.TOKEN_FIELDS}
        counters.update(input_tokens=7999999, output_tokens=1, total_tokens=8000000 if change == "tokens" else None)
        write_json(directory / "receipt.json", {"protocol_status": "conformant", "configuration_verified": True,
            "provider_verified": True, "usage_verified": True, "usage": {"by_response_id": {"fictional-budget-response": counters}}})
        write_json(directory / "response.json", {"accepted": True})
    with pytest.raises(native.ExecutionStop, match=expected):
        amendment._budget(run, request["workflow_id"], dispatching=True)


def test_complete_reference_token_limit_rejects_without_clipping_or_queueing(prepared_run):
    run = prepared_run[0]
    item = amendment.read(run / "calibration-plan.json")["cases"][0]
    client = amendment.CliMailboxClient(run, item["workflow_id"], token_counter=lambda p: 300001)
    with pytest.raises(native.ExecutionStop, match="300,000"):
        client.complete("A complete synthetic source quotation 原文 that must never be clipped.")
    assert not (run / "mailbox").exists()


def _environment(cwd):
    date = datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    return (f"<environment_context>\n  <cwd>{cwd}</cwd>\n  <shell>powershell</shell>\n"
        f"  <current_date>{date}</current_date>\n  <timezone>Asia/Shanghai</timezone>\n"
        f"  <filesystem><workspace_roots><root>{cwd}</root></workspace_roots>"
        '<permission_profile type="managed"><file_system type="restricted"><entry access="read">'
        "<special>:root</special></entry></file_system></permission_profile></filesystem>\n</environment_context>")


def fake_process_factory(sessions, *, unknown_usage=False):
    launches = []

    def spawn(command, *, cwd, stdin, stdout, stderr):
        number = len(launches) + 1
        session, turn, response, final = (f"fictional-session-{number}", f"fictional-turn-{number}",
            f"fictional-response-{number}", f"fictional-final-{number}")
        launches.append(command)
        output = Path(command[command.index("--output-last-message") + 1])

        class Process:
            pid = 1000 + number
            returncode = None

            def communicate(self, input=None, timeout=None):
                answer = '{"synthetic_observation":"All supplied source references are preserved."}'
                def row(kind, **payload):
                    return {"type": kind, "payload": payload}
                def message(role, text, identifier, **fields):
                    return row("response_item", type="message", id=identifier, role=role,
                        content=[{"type": "output_text" if role == "assistant" else "input_text", "text": text}], **fields)
                usage = {key: 0 for key in adapter.TOKEN_FIELDS}
                usage.update(input_tokens=10, output_tokens=3, total_tokens=None if unknown_usage else 13)
                rows = [row("session_meta", id=session, session_id=session, source="exec", originator="codex_exec",
                    cli_version=adapter.PINNED_VERSION, model_provider="openai", cwd=str(cwd),
                    base_instructions={"text": "Synthetic common base."}),
                    row("event_msg", type="task_started", turn_id=turn, root_turn_id=turn, started_at=1,
                        turn_attribution={"turn_id": turn, "root_turn_id": turn, "turn_trigger": "exec"}),
                    message("developer", "Synthetic common developer.", "fictional-developer"),
                    message("user", _environment(cwd), "fictional-environment"),
                    row("turn_context", turn_id=turn, root_turn_id=turn, model="gpt-6.1-sol", effort="max",
                        cwd=str(cwd), approval_policy="never", sandbox_policy={"type": "read-only"}),
                    message("user", input.decode("utf-8"), "fictional-task"),
                    row("event_msg", type="item_completed", thread_id=session, turn_id=turn,
                        item={"type": "UserMessage", "id": "fictional-user-event", "content": [{"type": "text", "text": input.decode("utf-8")}]}),
                    row("event_msg", type="item_completed", thread_id=session, turn_id=turn,
                        item={"type": "AgentMessage", "id": final, "phase": "final_answer", "content": [{"type": "Text", "text": answer}]}),
                    message("assistant", answer, final, phase="final_answer", status="completed"),
                    row("token_usage_record", thread_id=session, session_id=session, turn_id=turn,
                        root_turn_id=turn, response_id=response, usage=usage),
                    row("event_msg", type="task_complete", turn_id=turn, root_turn_id=turn,
                        started_at=1, completed_at=2, duration_ms=1000, time_to_first_token_ms=100)]
                sessions.mkdir(exist_ok=True)
                (sessions / f"rollout-{session}.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
                output.write_bytes(answer.encode("utf-8"))
                for record in [{"type": "thread.started", "thread_id": session}, {"type": "turn.started"},
                    {"type": "item.completed", "item": {"type": "agent_message", "text": answer}}, {"type": "turn.completed"}]:
                    stdout.write((json.dumps(record) + "\n").encode("utf-8"))
                stdout.flush()
                self.returncode = 0

        return Process()

    return spawn, launches


def test_full_worker_mailbox_process_receipt_and_native_result_use_new_identities(prepared_run, monkeypatch):
    run, _, _, _, sessions = prepared_run
    native_calls = []

    def synthetic_native(source, attempt, client, *, renderer=None):
        native_calls.append((source, attempt))
        answer = client.complete("Synthetic native core preserving source quotation 原文 from source/file.txt.")
        (attempt / "report.md").write_text(answer, encoding="utf-8")
        return {"status": "complete", "stage": "finished", "selected_graph": "native_last_valid_cfg",
                "graph": {"synthetic_graph_decision": "retained"},
                "analysis": {"stage": "finished", "status": "complete"}}

    monkeypatch.setattr(native, "_native_pipeline", synthetic_native)
    results = []
    spawn, launches = fake_process_factory(sessions)
    for index, case in enumerate(amendment.CALIBRATION, 1):
        worker = threading.Thread(target=lambda case=case: results.append(amendment.run_calibration_worker(run, case, token_counter=lambda p: 100)))
        worker.start()
        deadline = time.monotonic() + 10
        while not amendment.pending_requests(run) and time.monotonic() < deadline:
            time.sleep(.01)
        response = amendment.dispatch_next_once(run, sessions_dir=sessions, popen=spawn)
        worker.join(timeout=10)
        assert not worker.is_alive() and len(results) == len(native_calls) == len(launches) == index
        assert response["status"] == "accepted" and response["formal_requests"] == 0
        assert response["cli_session_id"] == f"fictional-session-{index}"
        assert response["response_ids"] == [f"fictional-response-{index}"]
        assert results[-1]["status"] == "complete" and results[-1]["usage"]["totals"]["total_tokens"] == 13
        assert results[-1]["graph_reused"] is False and results[-1]["native_core_modified"] is False
    directory = native._requests(run)[0][0]
    assert amendment.read(directory / "dispatch.json")["collaboration_spawn"] is False
    assert (directory / "cli/process-start.json").exists()
    assert amendment.dispatch_next_once(run, sessions_dir=sessions, popen=spawn)["status"] == "no_pending_request"
    with pytest.raises(native.ExecutionStop, match="retried"):
        amendment.run_calibration_worker(run, "gh-fix-ci", token_counter=lambda p: 100)
    assert amendment.summarize_calibrations(run)["status"] == "incomplete"
    from skillflow.graph.feedback import runner as graph_runner
    from skillflow import pipeline
    monkeypatch.setattr(graph_runner, "replay_run", lambda p: {"synthetic_graph_decision": "retained"})
    monkeypatch.setattr(pipeline, "replay_analysis", lambda p: {"stage": "finished", "status": "complete"})
    before = {p: p.read_bytes() for p, _ in native._requests(run) for p in (p / "response.json",)}
    replay = amendment.replay_calibrations(run)
    assert replay["status"] == "passed" and replay["model_calls"] == replay["actual_cli_requests"] == 0
    assert amendment.summarize_calibrations(run)["status"] == "passed_engineering_only"
    assert {p: p.read_bytes() for p in before} == before
    assert len(launches) == 3
    response_path = native._requests(run)[0][0] / "response.json"
    changed = amendment.read(response_path)
    changed["answer"] += " Changed after import."
    write_json(response_path, changed)
    assert amendment.replay_calibrations(run)["status"] == "failed"


def test_unknown_actual_usage_retains_failed_request_and_stops_all_future_dispatch(prepared_run):
    run, _, _, _, sessions = prepared_run
    directory, request = _request(run)
    spawn, launches = fake_process_factory(sessions, unknown_usage=True)
    response = amendment.dispatch_next_once(run, sessions_dir=sessions, popen=spawn)
    assert response["status"] == "stopped" and len(launches) == 1
    assert response["usage"]["totals"]["total_tokens"] is None
    assert (directory / "receipt.json").exists() and (directory / "response.json").exists()
    assert amendment.read(directory / "response.json")["accepted"] is False
    assert (run / "dispatch-stop.json").exists()
    assert amendment.dispatch_next_once(run, popen=spawn)["status"] == "dispatch_closed"
    assert len(launches) == 1


def test_dispatch_lock_prevents_two_supervisors_from_launching_one_request(prepared_run):
    run = prepared_run[0]
    _request(run)
    (run / "dispatcher.lock").write_text("Fictional competing supervisor.", encoding="utf-8")
    with pytest.raises(native.ExecutionStop, match="Another dispatcher"):
        amendment.dispatch_next_once(run)
