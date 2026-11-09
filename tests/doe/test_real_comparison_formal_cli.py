"""Prospective formal guards using fictional temporary inputs; zero target calls."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import threading

import pytest

from tools.doe.real_comparison import formal_cli as formal
from tools.doe.real_comparison import formal_cli_metrics as accounting
from tools.doe.real_comparison import execution as native
from tools.doe.real_comparison import cli_adapter_v3 as cli
from tools.doe.real_comparison.artifacts import seal_candidate
from tools.doe.real_comparison.inputs import render_direct, render_review
from tools.doe.real_comparison.protocol import canonical_hash, sha256, utc_now, write_json


@pytest.fixture(autouse=True)
def forbid_target_launch(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline formal tests must never start a subprocess or target")
    monkeypatch.setattr(cli.subprocess, "Popen", forbidden)


@pytest.fixture
def cohort(tmp_path):
    run = tmp_path / "fictional-formal"
    cases = [{"case_id": f"real-{i:03d}", "canonical_id": f"synthetic/case-{i}",
              "source_sha256": str(i) * 64} for i in range(1, 31)]
    write_json(run / "selection.json", {"selected": cases[:24], "reserves": cases[24:]})
    for case in cases:
        path = run / "cases" / case["case_id"]
        (path / "source").mkdir(parents=True)
        (path / "source/SKILL.md").write_bytes(b"# Fictional Skill\nReturn the declared label.\n")
        (path / "source-bundle.txt").write_text('Frozen source with literal {source_bundle}; user quotation: "原文".\n', encoding="utf-8")
    (run / "prompts").mkdir()
    for method in ("audit", "chain"):
        (run / "prompts" / (method + ".txt")).write_text(method + "\n{source_bundle}", encoding="utf-8")
    (run / "prompts/review.txt").write_text("Original task:\n{original_task}\nExact R1:\n{original_answer}", encoding="utf-8")
    schedule = native.prepare_schedule(run, cases[:24])
    (run / "prepared-prompts").mkdir()
    for item in schedule["main"]:
        if item["method"] != "skillflow":
            (run / "prepared-prompts" / (item["workflow_id"] + ".txt")).write_bytes(
                render_direct(run, item["case_id"], item["method"]).encode("utf-8"))
    return run, schedule


def register(run, item):
    directory = native._workflow(run, item["workflow_id"])
    write_json(directory / "registration.json", {**item, "mode": "formal", "runtime": cli.EXPECTED,
        "transport": cli.TRANSPORT, "source_path": str((run / "cases" / item["case_id"] / "source").resolve())})
    write_json(directory / "state.json", {"started_at": utc_now()})
    return directory


def request(run, item, *, number=1, dispatched=False, started=False, response_id=None, accepted=False, tokens=10):
    identity = f"{item['workflow_id']}_q{number:03d}"
    path = run / "mailbox/requests" / identity
    write_json(path / "request.json", {"request_id": identity, "workflow_id": item["workflow_id"],
        "created_at": utc_now(), "mode": "formal"})
    if dispatched:
        write_json(path / "dispatch.json", {"dispatched_at": utc_now()})
    if started:
        write_json(path / "cli/process-start.json", {"actual_cli_process_started": True, "pid": 123})
    if response_id:
        counters = {key: tokens for key in cli.TOKEN_FIELDS}
        write_json(path / "receipt.json", {"usage_verified": True, "protocol_status": "conformant",
            "usage": {"by_response_id": {response_id: counters}, "totals": counters}})
        write_json(path / "response.json", {"accepted": accepted})
    return path


def test_complete_fixed_schedule_and_exact_multilingual_materials(cohort):
    run, schedule = cohort
    _, verified = formal._schedule(run)
    assert verified == schedule
    assert len(schedule["main"]) == 216 and len(schedule["reviews"]) == 48
    a = render_direct(run, "real-001", "audit")
    assert '{source_bundle}; user quotation: "原文"' in a
    for repeat in (1, 2, 3):
        assert (run / "prepared-prompts" / f"real-001_audit_r{repeat}.txt").read_bytes() == a.encode("utf-8")


@pytest.mark.parametrize("change", ("source", "prompt", "r2_review", "missing_result"))
def test_schedule_rejects_any_fixed_identity_or_prompt_drift(cohort, change):
    run, schedule = cohort
    if change == "source":
        schedule["main"][0]["source_sha256"] = "changed"
    elif change == "r2_review":
        schedule["reviews"][0]["original_workflow_id"] = schedule["reviews"][0]["original_workflow_id"].replace("_r1", "_r2")
    elif change == "missing_result":
        schedule["main"].pop()
    else:
        (run / "prepared-prompts/real-001_audit_r1.txt").write_text("Clipped material", encoding="utf-8")
    write_json(run / "schedule.json", schedule)
    with pytest.raises(native.ExecutionStop):
        formal._schedule(run)


def test_calibration_authorization_never_authorizes_formal(tmp_path):
    bindings = {"source": "exact", "reference": "exact", "production": "exact"}
    proposal = tmp_path / "fictional-proposal.json"
    decision = tmp_path / "fictional-calibration-adoption.json"
    write_json(proposal, {"schema_version": formal.PROPOSAL_SCHEMA, "protocol": formal.effective_policy(), "bindings": bindings})
    write_json(decision, {"schema_version": formal.calibration.AUTHORIZATION_SCHEMA, "state": "adopted",
        "user_authorized": True, "calibration_only": True, "formal_dispatch_permitted": False})
    with pytest.raises(native.ExecutionStop, match="calibration authorization is insufficient"):
        formal._authorization(decision, proposal, bindings)


@pytest.mark.parametrize("field", ("source", "reference", "production", "runtime", "prompt"))
def test_formal_authorization_binds_exact_final_identity_before_creation(tmp_path, field):
    bindings = {k: "exact" for k in ("source", "reference", "production", "runtime", "prompt")}
    proposal, decision = tmp_path / "proposal.json", tmp_path / "decision.json"
    write_json(proposal, {"schema_version": formal.PROPOSAL_SCHEMA, "protocol": formal.effective_policy(), "bindings": bindings})
    write_json(decision, {"schema_version": formal.AUTHORIZATION_SCHEMA, "state": "adopted", "user_authorized": True,
        "formal_dispatch_permitted": True, "calibration_only": False, "automatic_retry": False,
        "proposal_sha256": sha256(proposal), "bindings_sha256": canonical_hash(bindings),
        "user_confirmation": {"quotation": "Fictional unit-test consent only", "conversation_reference": "synthetic-test"}})
    altered = {**bindings, field: "different"}
    with pytest.raises(native.ExecutionStop, match="exact final"):
        formal._authorization(decision, proposal, altered)


def test_real_interrupted_state_is_blocked_without_creating_run_or_lock(tmp_path):
    long_run = formal.ROOT / "experiments/doe/runs/real-same-model-long-v2-20261020-1340Z"
    calibration = formal.ROOT / "experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z"
    if not long_run.exists() or not calibration.exists():
        pytest.skip("Local-only interrupted records are not part of every checkout")
    args = dict(cohort_run=long_run, reference_workspace=long_run, calibration_run=calibration,
        protocol_proposal=tmp_path / "absent-proposal.json", decision_record=tmp_path / "absent-decision.json",
        executable=tmp_path / "absent.exe")
    result = formal.inspect_readiness(**args)
    assert result["ready"] is False and result["model_calls"] == 0
    assert any("stopped calibration" in reason for reason in result["reasons"])
    target = tmp_path / "never-created"
    with pytest.raises((OSError, ValueError, native.ExecutionStop)):
        formal.prepare_formal_run(target, **args)
    assert not target.exists()
    calls = []
    with pytest.raises((OSError, ValueError, native.ExecutionStop)):
        formal.dispatch_next_once(calibration, process_factory=lambda *a, **k: calls.append(a))
    assert calls == []


def test_stopped_or_fabricated_calibration_never_opens_gate(tmp_path, monkeypatch):
    cal = tmp_path / "fictional-calibration"
    write_json(cal / "dispatch-stop.json", {"automatic_retry": False})
    monkeypatch.setattr(formal.calibration, "verify_run", lambda p: pytest.fail("Stopped calibration must reject first"))
    with pytest.raises(native.ExecutionStop, match="stopped calibration"):
        formal._calibration_evidence(cal)
    (cal / "dispatch-stop.json").unlink()
    monkeypatch.setattr(formal.calibration, "verify_run", lambda p: {})
    monkeypatch.setattr(formal.calibration, "summarize_calibrations", lambda p: {"status": "passed", "runtime": cli.EXPECTED})
    with pytest.raises(native.ExecutionStop, match="three complete"):
        formal._calibration_evidence(cal)


@pytest.fixture
def binding_materials(cohort, tmp_path, monkeypatch):
    run, _ = cohort
    epoch = tmp_path / "fictional-reference-epoch"
    selection = formal.read(run / "selection.json")
    for case in selection["selected"] + selection["reserves"]:
        case.update(source_tree_sha256="fictional-tree", bundle_sha256="fictional-bundle")
        write_json(epoch / "references" / (case["case_id"] + ".json"), {"fictional": True})
    write_json(run / "selection.json", selection)
    write_json(epoch / "selection.json", selection)
    for path in (run / "preparation-freeze.json", epoch / "reference-epoch-freeze.json", epoch / "reference-freeze.json"):
        write_json(path, {"fictional": True})
    write_json(epoch / "reference-epoch-origin.json", {"parent_preparation": str(run), "corpus_root": str(tmp_path)})
    approved = [{"case_id": c["case_id"], "canonical_id": c["canonical_id"], "source_sha256": c["source_sha256"],
        "source_tree_sha256": c["source_tree_sha256"], "source_bundle_sha256": c["bundle_sha256"],
        "reference_sha256": sha256(epoch / "references" / (c["case_id"] + ".json"))} for c in selection["selected"] + selection["reserves"]]
    write_json(epoch / "approved-source-set.json", {"cases": approved})
    status = {"integrity": "verified", "cases": 30, "complete_draft_schema_and_quotes": 30,
              "reference_epoch_sealed": True, "actual_active_confirmations": 60, "actual_roster_imported": True}
    monkeypatch.setattr(formal, "verify_preparation", lambda *a: {"status": "passed"})
    monkeypatch.setattr(formal.reference_epoch, "current_selection_binding", lambda *a: {"fictional": True})
    monkeypatch.setattr(formal.reference_epoch, "verify_reference_epoch", lambda *a: status)
    monkeypatch.setattr(formal, "_calibration_evidence", lambda *a: {"production_implementation": {}})
    import skillflow.common.recording as recording
    monkeypatch.setattr(recording, "implementation_provenance", lambda: {})
    exe = tmp_path / "never-executed.exe"
    exe.write_bytes(b"Fictional binary bytes, never executed")
    monkeypatch.setattr(cli, "PINNED_EXECUTABLE_SHA256", sha256(exe))
    return run, epoch, exe, status


@pytest.mark.parametrize("field,value", (("cases", 29), ("complete_draft_schema_and_quotes", 29),
    ("reference_epoch_sealed", False), ("actual_active_confirmations", 59), ("actual_roster_imported", False)))
def test_missing_current_reference_and_actual_confirmation_blocks_binding(binding_materials, field, value):
    run, epoch, exe, status = binding_materials
    status[field] = value
    with pytest.raises(native.ExecutionStop, match="Thirty complete"):
        formal.inspect_bindings(cohort_run=run, reference_workspace=epoch, calibration_run=run.parent / "cal", executable=exe)


@pytest.mark.parametrize("change", ("reference", "source", "selection", "production", "executable"))
def test_exact_source_reference_and_runtime_binding_mismatches_fail(binding_materials, monkeypatch, change):
    run, epoch, exe, _ = binding_materials
    if change == "reference":
        write_json(epoch / "references/real-001.json", {"changed_reference": True})
    elif change == "source":
        approved = formal.read(epoch / "approved-source-set.json")
        approved["cases"][0]["source_sha256"] = "different"
        write_json(epoch / "approved-source-set.json", approved)
    elif change == "selection":
        altered = formal.read(epoch / "selection.json")
        altered["reserves"].reverse()
        write_json(epoch / "selection.json", altered)
    elif change == "production":
        monkeypatch.setattr(formal, "_calibration_evidence", lambda *a: {"production_implementation": {"different": True}})
    else:
        exe.write_bytes(b"Changed executable")
    with pytest.raises(native.ExecutionStop):
        formal.inspect_bindings(cohort_run=run, reference_workspace=epoch, calibration_run=run.parent / "cal", executable=exe)


def test_gate_rechecks_exact_implementation_and_approval_before_dispatch(binding_materials, monkeypatch):
    run, epoch, exe, _ = binding_materials
    bindings = formal.inspect_bindings(cohort_run=run, reference_workspace=epoch, calibration_run=run.parent / "cal", executable=exe)
    write_json(run / "authorization/proposal.json", {"schema_version": formal.PROPOSAL_SCHEMA,
        "protocol": formal.effective_policy(), "bindings": bindings})
    proposal = run / "authorization/proposal.json"
    write_json(run / "authorization/adoption.json", {"schema_version": formal.AUTHORIZATION_SCHEMA,
        "state": "adopted", "user_authorized": True, "formal_dispatch_permitted": True, "calibration_only": False,
        "automatic_retry": False, "proposal_sha256": sha256(proposal), "bindings_sha256": canonical_hash(bindings),
        "user_confirmation": {"quotation": "Fictional unit-test consent only", "conversation_reference": "synthetic-test"}})
    write_json(run / "materials-freeze.json", {"files": {}})
    write_json(run / "formal-gate.json", {"schema_version": formal.SCHEMA, "state": "approved", "automatic_retry": False,
        "bindings": bindings, "materials_freeze_sha256": sha256(run / "materials-freeze.json"),
        "proposal_sha256": sha256(proposal), "adoption_sha256": sha256(run / "authorization/adoption.json")})
    monkeypatch.setattr(formal, "verify_human_reference_freeze", lambda *a: {})
    monkeypatch.setattr(native, "verify_production_code", lambda *a: {})
    assert formal.verify_formal_gate(run)
    changed = deepcopy(bindings)
    changed["implementation_files"]["tools/doe/real_comparison/formal_cli.py"] = "changed"
    monkeypatch.setattr(formal, "inspect_bindings", lambda **kwargs: changed)
    calls = []
    with pytest.raises(native.ExecutionStop, match="authority changed"):
        formal.dispatch_next_once(run, process_factory=lambda *a, **k: calls.append(a))
    assert not (run / "dispatcher.lock").exists() and calls == []


@pytest.mark.parametrize("field,value", (("runtime_expectation", {"model": "wrong"}),
    ("expected_cli_version", "different"), ("base_instructions_sha256", "different"),
    ("developer_segment_sha256", [["different"]]), ("stdin_sha256", "different")))
def test_exact_launch_runtime_and_harness_drift_fail_replay(tmp_path, field, value):
    directory = tmp_path / "fictional-request"
    directory.mkdir()
    core = "Preserve full original CRLF input.\r\nReturn one final answer."
    delivery = native.ENVELOPE.replace("{core}", core)
    (directory / "core-prompt.txt").write_bytes(core.encode("utf-8"))
    (directory / "prompt.txt").write_bytes(delivery.encode("utf-8"))
    launch = {"command": cli.command(tmp_path / "fictional.exe", directory / "cli"),
        "stdin_file": str(directory / "prompt.txt"), "stdin_sha256": cli.digest(delivery), "runtime_expectation": cli.EXPECTED,
        "output_dir": str(directory / "cli"), "empty_workdir": str(directory.parents[2] / "empty-cwd" / directory.name),
        "expected_cli_version": cli.PINNED_VERSION, "executable_sha256": cli.PINNED_EXECUTABLE_SHA256,
        "base_instructions_sha256": cli.PINNED_BASE_INSTRUCTIONS_SHA256,
        "developer_segment_sha256": [list(p) for p in cli.PINNED_DEVELOPER_SEGMENTS]}
    write_json(directory / "request.json", {"core_sha256": cli.digest(core), "delivery_sha256": cli.digest(delivery)})
    write_json(directory / "dispatch.json", {"command": launch["command"]})
    write_json(directory / "receipt.json", {"stdin_sha256": cli.digest(delivery)})
    write_json(directory / "response.json", {})
    launch[field] = value
    write_json(directory / "cli/launch.json", launch)
    with pytest.raises(native.ExecutionStop, match="launch/process binding changed"):
        formal._replay_request(directory)


@pytest.mark.parametrize("existing", ("same", "inside", "ancestor", "existing"))
def test_formal_preparation_rejects_overlapping_or_existing_paths(cohort, tmp_path, existing):
    run = cohort[0]
    target = {"same": run, "inside": run / "child", "ancestor": run.parent, "existing": tmp_path / "existing"}[existing]
    if existing == "existing":
        target.mkdir()
    with pytest.raises(native.ExecutionStop, match="nonoverlapping|already exist"):
        formal.prepare_formal_run(target, cohort_run=run, reference_workspace=tmp_path / "epoch",
            calibration_run=tmp_path / "cal", protocol_proposal=tmp_path / "proposal", decision_record=tmp_path / "decision", executable=tmp_path / "exe")


def test_missing_r1_remains_unreviewable_without_queue_or_substitution(cohort, monkeypatch):
    run, schedule = cohort
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    item = schedule["reviews"][0]
    result = formal.run_planned_workflow(run, item["workflow_id"])
    assert result["status"] == "not_reviewable" and result["attempts"] == 0
    assert not (run / "mailbox").exists()


def test_fixed_review_binds_exact_original_only_and_preserves_literal_source(cohort):
    run, schedule = cohort
    item = schedule["reviews"][0]
    original_item = formal._planned(run, item["original_workflow_id"])
    directory = register(run, original_item)
    answer = "Exact original {original_answer}; quoted user input 原文."
    (directory / "answer.txt").write_bytes(answer.encode("utf-8"))
    sealed = seal_candidate(run, original_item["workflow_id"])
    write_json(directory / "result.json", {"status": "complete", "answer_sha256": cli.digest(answer), **sealed})
    review = register(run, item)
    write_json(review / "original.json", {"original_workflow_id": item["original_workflow_id"], "answer_sha256": cli.digest(answer)})
    prompt = render_review(run, item["case_id"], item["method"], answer)
    formal._verify_prompt(run, formal._registration(run, item["workflow_id"]), prompt)
    for forbidden in ("REFERENCE_SENTINEL", "SCORE_SENTINEL", "REVIEWER_ADVICE_SENTINEL"):
        with pytest.raises(native.ExecutionStop, match="complete direct/review prompt"):
            formal._verify_prompt(run, formal._registration(run, item["workflow_id"]), prompt + forbidden)
    (directory / "answer.txt").write_text("Changed original", encoding="utf-8")
    with pytest.raises(native.ExecutionStop, match="changed"):
        formal._review_original(run, item)


def test_request_counter_distinguishes_queue_dispatch_process_response_and_acceptance(cohort):
    run, schedule = cohort
    item = schedule["main"][0]
    request(run, item, number=1)
    request(run, item, number=2, dispatched=True)
    request(run, item, number=3, dispatched=True, started=True)
    request(run, item, number=4, dispatched=True, started=True, response_id="shared-id", accepted=True)
    request(run, item, number=5, dispatched=True, started=True, response_id="shared-id", accepted=False)
    ledger = accounting.build_cost_ledger(run)
    assert ledger["counts"] == {"queued": 5, "dispatch_attempted": 4, "actual_cli_process_started": 3,
                                "attributed_response": 2, "accepted": 1}
    usage = ledger["formal_target_usage"]
    assert usage["response_count"] == 1 and usage["totals"]["total_tokens"] is None
    assert len(usage["missing_requests"]) == 2 and usage["reused_response_ids"] == ["shared-id"]
    assert len(usage["unknown_process_start_requests"]) == 1
    assert ledger["planned_results"] == 264 and ledger["all_planned_in_denominator"]


@pytest.mark.parametrize("kind", ("zero", "unknown", "tokens", "requests", "time"))
def test_budget_uses_actual_processes_and_unknown_usage_fail_closed(cohort, monkeypatch, kind):
    run, schedule = cohort
    item = schedule["main"][0]
    directory = register(run, item)
    if kind == "zero":
        path = request(run, item, dispatched=True)
        write_json(path / "cli/process-result.json", {"status": "prelaunch_error", "actual_cli_process_started": False})
        usage = accounting.usage_summary(run)
        assert usage["actual_cli_processes"] == 0 and usage["totals"]["total_tokens"] == 0
        return
    if kind == "time":
        write_json(directory / "state.json", {"started_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()})
    elif kind == "unknown":
        path = request(run, item, dispatched=True, started=True)
        write_json(path / "response.json", {"accepted": True})
    elif kind == "tokens":
        request(run, item, dispatched=True, started=True, response_id="one", accepted=True, tokens=8000000)
    else:
        monkeypatch.setitem(formal.LIMITS, "actual_cli_requests", 1)
        request(run, item, dispatched=True, started=True, response_id="one", accepted=True)
    with pytest.raises(native.ExecutionStop, match={"unknown": "Unknown", "tokens": "eight-million", "requests": "64 actual", "time": "six-hour"}[kind]):
        formal._budget(run, item["workflow_id"], dispatching=True)


def test_native_worker_uses_unchanged_fresh_pipeline_for_each_repeat(cohort, monkeypatch):
    run, schedule = cohort
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    calls = []
    def pipeline(source, attempt, client, *, renderer=None):
        calls.append((source, attempt, client))
        (attempt / "report.md").write_text("Synthetic native output", encoding="utf-8")
        return {"status": "diagnostic", "analysis": {"stage": "finished"}}
    monkeypatch.setattr(native, "_native_pipeline", pipeline)
    for repeat in (1, 2, 3):
        result = formal.run_planned_workflow(run, f"real-001_skillflow_r{repeat}")
        assert result["graph_reused"] is False and result["native_core_modified"] is False
    assert len({id(c[2]) for c in calls}) == 3 and len({c[1] for c in calls}) == 3
    assert all(c[0] == run / "cases/real-001/source" for c in calls)
    assert not (run / "mailbox").exists()


def test_oversize_delivery_is_never_clipped_or_published(cohort, monkeypatch):
    run, schedule = cohort
    item = next(i for i in schedule["main"] if i["method"] == "skillflow")
    register(run, item)
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    client = formal.FormalCliClient(run, item["workflow_id"], token_counter=lambda p: 300001)
    with pytest.raises(native.ExecutionStop, match="clipping is forbidden"):
        client.complete("Complete native prompt")
    assert not (run / "mailbox").exists()


def test_dispatch_prelaunch_failure_records_attempt_but_zero_actual_processes(cohort, monkeypatch):
    run, schedule = cohort
    item = schedule["main"][0]
    register(run, item)
    path = request(run, item)
    (path / "prompt.txt").write_text("Fictional complete delivery", encoding="utf-8")
    fake = {"command": ["never-executed"], "executable_sha256": "test", "stdin_sha256": "test"}
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {"bindings": {"executable": "never-executed"}})
    monkeypatch.setattr(formal, "authorize_dispatch", lambda *a, **k: {"request_id": path.name,
        "workflow_id": item["workflow_id"], "delivery_sha256": "test"})
    monkeypatch.setattr(cli, "prepare_launch", lambda *a, **k: fake)
    monkeypatch.setattr(cli, "execute_launch", lambda *a, **k: (_ for _ in ()).throw(ValueError("Fictional prelaunch drift")))
    calls = []
    result = formal.dispatch_next_once(run, process_factory=lambda *a, **k: calls.append(a))
    assert result["status"] == "stopped" and result["actual_cli_process_started"] is False and calls == []
    assert (run / "dispatch-stop.json").exists()
    ledger = accounting.build_cost_ledger(run)
    assert ledger["counts"]["dispatch_attempted"] == 1 and ledger["counts"]["actual_cli_process_started"] == 0
    assert ledger["formal_target_usage"]["totals"]["total_tokens"] == 0


def test_global_stop_closes_all264_and_closed_outputs_prevent_generation(cohort, monkeypatch):
    run, _ = cohort
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    write_json(run / "dispatch-stop.json", {"reason": "Synthetic prelaunch stop", "automatic_retry": False})
    freeze = formal.close_outputs(run)
    assert freeze["planned_results"] == 264
    results = list((run / "workflows").glob("*/result.json"))
    assert len(results) == 264 and all(formal.read(p)["status"] == "failed" for p in results)
    assert formal.close_outputs(run) == freeze
    assert accounting.build_cost_ledger(run)["counts"]["actual_cli_process_started"] == 0


def test_closure_rejects_active_work_and_outstanding_process(cohort, monkeypatch):
    run, schedule = cohort
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    item = schedule["main"][0]
    directory = register(run, item)
    write_json(run / "dispatch-stop.json", {"reason": "Synthetic stop"})
    write_json(directory / "result.json", {"status": "interrupted"})
    with pytest.raises(native.ExecutionStop, match="resumable"):
        formal.close_outputs(run)
    path = request(run, item, dispatched=True, started=True)
    write_json(path / "stop.json", {"reason": "Still lacks terminal process proof"})
    with pytest.raises(native.ExecutionStop, match="terminal supervision"):
        formal.close_outputs(run)


def test_replay_of_missing_gate_returns_failure_with_zero_calls(tmp_path):
    result = formal.replay_formal(tmp_path)
    assert result["status"] == "failed" and result["model_calls"] == 0
    assert result["actual_cli_processes_started_by_replay"] == 0


def test_replay_rejects_reused_actual_session_or_response_identity(cohort, monkeypatch):
    run, schedule = cohort
    item = next(i for i in schedule["main"] if i["method"] == "skillflow")
    register(run, item)
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    for number in (1, 2):
        path = request(run, item, number=number, dispatched=True, started=True, response_id="same-response", accepted=True)
        core = "Complete fixed synthetic stage prompt"
        delivery = native.ENVELOPE.replace("{core}", core)
        (path / "core-prompt.txt").write_bytes(core.encode("utf-8"))
        (path / "prompt.txt").write_bytes(delivery.encode("utf-8"))
        record = formal.read(path / "request.json")
        record.update(core_sha256=cli.digest(core), delivery_sha256=cli.digest(delivery), runtime=cli.EXPECTED, transport=cli.TRANSPORT)
        write_json(path / "request.json", record)
    monkeypatch.setattr(formal, "_replay_request", lambda path: {
        "cli_session_id": "same-session", "usage": {"by_response_id": {"same-response": {}}}})
    replay = formal.replay_formal(run)
    assert replay["status"] == "failed" and replay["model_calls"] == 0
    assert any("reused CLI session or response" in e["reason"] for e in replay["errors"])


@pytest.mark.parametrize("boundary", ("tokens", "elapsed"))
def test_accepted_final_response_survives_stop_further_dispatch_budget_boundary(cohort, monkeypatch, boundary):
    run, schedule = cohort
    item = next(i for i in schedule["main"] if i["method"] == "skillflow")
    directory = register(run, item)
    gate_checks = []
    def gate(*args, generation=True):
        gate_checks.append(generation)
        if generation and (run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("Budget forbids further generation")
        return {}
    monkeypatch.setattr(formal, "verify_formal_gate", gate)
    monkeypatch.setattr(formal, "_replay_request", lambda p: {"usage_verified": True})
    answer = "Accepted final semantic-stage answer remains the exact candidate."
    def accept_then_stop(seconds):
        path = next((run / "mailbox/requests").iterdir())
        write_json(path / "dispatch.json", {"dispatched_at": utc_now()})
        write_json(path / "cli/process-start.json", {"actual_cli_process_started": True})
        counters = {key: 8000001 if boundary == "tokens" else 10 for key in cli.TOKEN_FIELDS}
        write_json(path / "receipt.json", {"usage_verified": True, "usage": {
            "by_response_id": {"synthetic-final-response": counters}, "totals": counters}})
        write_json(path / "response.json", {"accepted": True, "answer": answer, "answer_sha256": cli.digest(answer)})
        if boundary == "elapsed":
            write_json(directory / "state.json", {"started_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()})
        with pytest.raises(native.ExecutionStop):
            formal._budget(run, item["workflow_id"])
        formal._stop(run, path.name, "Synthetic stop-further-dispatch budget boundary")
    monkeypatch.setattr(formal.time, "sleep", accept_then_stop)
    client = formal.FormalCliClient(run, item["workflow_id"], token_counter=lambda text: 10)
    assert client.complete("Complete final production stage prompt") == answer
    assert gate_checks[-1] is False
    with pytest.raises(native.ExecutionStop, match="further generation"):
        client.complete("A forbidden next semantic request")
    assert len(list((run / "mailbox/requests").iterdir())) == 1


@pytest.mark.parametrize("inflight", (False, True))
def test_existing_global_stop_terminalizes_only_own_unlaunched_queue(cohort, monkeypatch, inflight):
    run, schedule = cohort
    item = next(i for i in schedule["main"] if i["method"] == "audit")
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    def another_request_stops_run(seconds):
        path = next((run / "mailbox/requests").iterdir())
        if inflight:
            write_json(path / "dispatch.json", {"dispatched_at": utc_now()})
            write_json(path / "cli/process-start.json", {"actual_cli_process_started": True})
        write_json(run / "dispatch-stop.json", {"reason": "Another synthetic request closed dispatch", "automatic_retry": False})
    monkeypatch.setattr(formal.time, "sleep", another_request_stops_run)
    result = formal.run_planned_workflow(run, item["workflow_id"], token_counter=lambda p: 10)
    path = next((run / "mailbox/requests").iterdir())
    assert result["status"] == "failed" and not (path / "response.json").exists()
    assert not (path / "cli/process-result.json").exists()
    assert formal.read(run / "dispatch-stop.json")["reason"] == "Another synthetic request closed dispatch"
    if inflight:
        assert not (path / "stop.json").exists()
        with pytest.raises(native.ExecutionStop, match="actual process without terminal"):
            formal.close_outputs(run)
    else:
        assert (path / "stop.json").exists() and not (path / "cli/process-start.json").exists()
        assert formal.close_outputs(run)["planned_results"] == 264
        assert accounting.usage_summary(run)["totals"]["total_tokens"] == 0


def activate_fictional_grading_epoch(run):
    epoch = run / "corrigenda/fictional/workspace"
    write_json(run / "output-freeze.json", {"fictional_closed_target_cohort": True})
    write_json(epoch / "output-freeze.json", formal.read(run / "output-freeze.json"))
    write_json(epoch / "grading-epoch.json", {"epoch_id": "fictional-epoch", "logical_study_root": str(run.resolve())})
    activation = run / "corrigenda/fictional/activation.json"
    write_json(activation, {"epoch_id": "fictional-epoch", "workspace": epoch.relative_to(run).as_posix(),
        "target_output_freeze_sha256": sha256(run / "output-freeze.json")})
    write_json(run / "active-grading-epoch.json", {"epoch_id": "fictional-epoch",
        "activation_record": activation.relative_to(run).as_posix(), "activation_sha256": sha256(activation)})
    return epoch


@pytest.mark.parametrize("from_epoch", (False, True))
def test_report_efficiency_uses_active_grading_scores_not_stale_original(cohort, monkeypatch, from_epoch):
    from tools.doe.real_comparison import results, efficiency, corrigenda
    run, _ = cohort
    epoch = activate_fictional_grading_epoch(run)
    write_json(run / "scores.json", {"marker": "stale-original-scores"})
    monkeypatch.setattr(formal, "verify_formal_gate", lambda *a, **k: {})
    monkeypatch.setattr(results, "verify_output_freeze", lambda *a: {})
    monkeypatch.setattr(formal, "replay_formal", lambda *a: {"status": "verified", "model_calls": 0})
    def score_original_target_with_current_reference(path):
        assert Path(path) == run
        grading = corrigenda.resolve_grading_run(path)
        write_json(grading / "scores.json", {"marker": "current-grading-scores", "rows": []})
        return {"marker": "current-grading-scores"}
    monkeypatch.setattr(results, "aggregate_scores", score_original_target_with_current_reference)
    monkeypatch.setattr(formal, "build_cost_ledger", lambda *a: {"formal_target_usage": {"synthetic": True}})
    monkeypatch.setattr(efficiency, "efficiency_comparisons", lambda scores, costs: {"used_scores": scores["marker"]})
    report = formal.report(epoch if from_epoch else run)
    assert report["efficiency"]["used_scores"] == "current-grading-scores"
    assert report["target_run"] == str(run) and report["grading_run"] == str(epoch)
    assert formal.read(run / "scores.json")["marker"] == "stale-original-scores"


def test_cost_uses_original_targets_and_current_grading_humans_once(cohort, monkeypatch):
    from tools.doe.real_comparison import corrigenda
    run, schedule = cohort
    epoch = activate_fictional_grading_epoch(run)
    item = schedule["main"][0]
    request(run, item, dispatched=True, started=True, response_id="original-target-response", accepted=True, tokens=10)
    request(epoch, item, dispatched=True, started=True, response_id="copied-target-response", accepted=True, tokens=999)
    write_json(epoch / "human-roster.json", {"fictional_marker": "Routing test only"})
    monkeypatch.setattr(accounting, "human_cost_summary", lambda path: {"observed_grading_run": str(path)})
    monkeypatch.setattr(corrigenda, "lineage_human_cost", lambda path: {"deduplicated_target_root": str(path)})
    costs = accounting.build_cost_ledger(epoch)
    assert costs["human_cost"]["observed_grading_run"] == str(epoch)
    assert costs["grading_epoch_human_work_history"]["deduplicated_target_root"] == str(run)
    assert costs["counts"]["actual_cli_process_started"] == 1
    assert costs["formal_target_usage"]["totals"]["total_tokens"] == 10
    assert "copied-target-response" not in costs["formal_target_usage"]["by_response_id"]
