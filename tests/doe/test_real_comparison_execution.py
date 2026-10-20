"""Engineering checks use synthetic replies and make zero model calls."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import threading
from unittest.mock import patch

import pytest

from tools.doe.real_comparison import execution as x
from tools.doe.real_comparison.protocol import prepare_protocol, sha256, write_json


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source(tmp_path):
    path = tmp_path / "source"
    path.mkdir(exist_ok=True)
    (path / "SKILL.md").write_text("# Real input boundary\nKeep original 引用 exactly.\n", encoding="utf-8")
    return path


def case_records():
    return [{"case_id": f"c{i:02d}", "source_sha256": f"source-{i}"} for i in range(24)]


def fake_gate(run):
    prepare_protocol(run)
    x.snapshot_production_code(run)
    selected = case_records()
    reserves = [{"case_id": f"r{i}", "source_sha256": f"reserve-{i}"} for i in range(6)]
    write_json(run / "selection.json", {"selected": selected, "reserves": reserves})
    write_json(run / "materials-freeze.json", {"files": {}})
    refs = [{**c, "state": "approved", "reference_sha256": "ref-" + c["case_id"]} for c in selected + reserves]
    write_json(run / "references.json", {"references": refs})
    write_json(run / "reference-freeze.json", {"files": {"references.json": sha256(run / "references.json")}})
    write_json(run / "calibration.json", {"status": "passed", "runtime": x.EXPECTED, "cases": list(x.CALIBRATION)})
    write_json(run / "human-roster.json", {"reviewers": [{"reviewer_id": p, "role": "reference_verifier", "human": True,
               "declared_at": "2026-10-20T00:00:00+00:00"} for p in ("human-a", "human-b")]})
    attestations = [{"case_id": c["case_id"], "source_sha256": c["source_sha256"], "reference_sha256": c["reference_sha256"],
                    "reviewer_id": p, "role": "reference_verifier", "human": True, "approved": True,
                    "attestation_id": p + c["case_id"], "attested_at": "2026-10-20T01:00:00+00:00",
                    "confirmation": "I personally verified this source reference."} for c in refs for p in ("human-a", "human-b")]
    imported = []
    for i, attestation in enumerate(attestations):
        path = run / "approvals/submissions" / f"{i}.json"
        write_json(path, attestation)
        imported.append({"path": path.relative_to(run).as_posix(), "sha256": sha256(path),
                         "import_source": "human_user_submission", "case_id": attestation["case_id"],
                         "reviewer_id": attestation["reviewer_id"]})
    write_json(run / "approvals/import-manifest.json", {"records": imported})
    gate = {"schema_version": x.SCHEMA, "state": "approved", "human_attestations": attestations}
    for key, name in (("selection_sha256", "selection.json"), ("protocol_freeze_sha256", "protocol-freeze.json"),
                      ("materials_sha256", "materials-freeze.json"), ("reference_freeze_sha256", "reference-freeze.json"),
                      ("calibration_sha256", "calibration.json"), ("production_code_freeze_sha256", "production-code-freeze.json")):
        gate[key] = sha256(run / name)
    write_json(run / "gate.json", gate)
    return gate


def workflow(run, name="w", mode="calibration"):
    path = run / "workflows" / name
    write_json(path / "state.json", {"started_at": x.utc_now()})
    write_json(path / "registration.json", {"mode": mode, "source_path": "unused"})
    return path


def request(run, name="w", index=1, *, counters=None, accepted=True, dispatched=True):
    identifier = f"{name}_q{index:03d}"
    directory = run / "mailbox/requests" / identifier
    directory.mkdir(parents=True)
    core, delivery = "Core 原文", x.ENVELOPE.replace("{core}", "Core 原文")
    (directory / "core-prompt.txt").write_text(core, encoding="utf-8", newline="")
    (directory / "prompt.txt").write_text(delivery, encoding="utf-8", newline="")
    write_json(directory / "request.json", {"request_id": identifier, "workflow_id": name, "mode": "calibration",
               "core_sha256": x._digest(core), "delivery_sha256": x._digest(delivery)})
    if dispatched:
        write_json(directory / "dispatch.json", {"dispatched_at": x.utc_now(), "agent_session_id": identifier,
                   "protocol_conformant": True})
        write_json(directory / "response.json", {"accepted": accepted, "answer": "Visible reply", "answer_sha256": x._digest("Visible reply")})
        if counters is not None:
            write_json(directory / "receipt.json", {"usage": {"by_response_id": counters}})
    return directory


def counters(total=10):
    return {"input_tokens": 8, "cached_input_tokens": 0, "cache_write_input_tokens": 0,
            "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": total}


def test_schedule_is_fixed_balanced_and_prespecifies_only_repeat_one_reviews(tmp_path):
    result = x.prepare_schedule(tmp_path, case_records())
    assert len(result["main"]) == 216 and len(result["reviews"]) == 48
    assert len({r["workflow_id"] for r in result["main"] + result["reviews"]}) == 264
    assert all(r["repeat"] == 1 and r["method"] != "skillflow" and r["user_request"] is None for r in result["reviews"])
    assert x.prepare_schedule(tmp_path, case_records()) == result
    with pytest.raises(ValueError, match="Immutable"):
        x.prepare_schedule(tmp_path, case_records(), seed=1)
    positions = {m: [0, 0, 0] for m in x.METHODS}
    for i, item in enumerate(result["main"]):
        positions[item["method"]][i % 3] += 1
    assert all(v == [24, 24, 24] for v in positions.values())


def test_formal_gate_never_accepts_assistant_flags_or_changed_references(tmp_path):
    gate = fake_gate(tmp_path)
    assert x.verify_gate(tmp_path) == gate
    record = read(tmp_path / "approvals/import-manifest.json")
    record["records"][0]["import_source"] = "assistant_draft"
    write_json(tmp_path / "approvals/import-manifest.json", record)
    with pytest.raises(x.ExecutionStop, match="human submission"):
        x.verify_gate(tmp_path)
    fake_gate(tmp_path)
    write_json(tmp_path / "references.json", {"references": []})
    with pytest.raises(x.ExecutionStop, match="changed"):
        x.verify_gate(tmp_path)


def test_formal_gate_requires_two_distinct_rostered_humans_per_case(tmp_path):
    gate = fake_gate(tmp_path)
    gate["human_attestations"][1]["reviewer_id"] = "human-a"
    imported = read(tmp_path / "approvals/import-manifest.json")
    item = imported["records"][1]
    write_json(tmp_path / item["path"], gate["human_attestations"][1])
    item.update(sha256=sha256(tmp_path / item["path"]), reviewer_id="human-a")
    write_json(tmp_path / "approvals/import-manifest.json", imported)
    write_json(tmp_path / "gate.json", gate)
    with pytest.raises(x.ExecutionStop, match="two distinct"):
        x.verify_gate(tmp_path)


def test_usage_deduplicates_response_id_and_keeps_unknown(tmp_path):
    workflow(tmp_path)
    request(tmp_path, index=1, counters={"resp": counters()})
    request(tmp_path, index=2, counters={"resp": counters()})
    assert x.usage_summary(tmp_path)["totals"]["total_tokens"] == 10
    request(tmp_path, index=3, counters={"other": counters(None)})
    assert x.usage_summary(tmp_path)["totals"]["total_tokens"] is None
    with pytest.raises(x.ExecutionStop, match="Unknown"):
        x._budget(tmp_path, "w", dispatching=True)


def test_conflicting_response_usage_is_unknown_and_blocks_dispatch(tmp_path):
    workflow(tmp_path)
    request(tmp_path, index=1, counters={"resp": counters(10)})
    request(tmp_path, index=2, counters={"resp": counters(11)})
    summary = x.usage_summary(tmp_path)
    assert summary["conflicting_response_ids"] == ["resp"]
    assert all(value is None for value in summary["totals"].values())
    with pytest.raises(x.ExecutionStop, match="Conflicting"):
        x._budget(tmp_path, "w", dispatching=True)


def test_frozen_evaluation_rules_and_driver_drift_block_formal_gate(tmp_path):
    (tmp_path / "rules.md").write_text("Preserve the common primary endpoint.", encoding="utf-8")
    relative = "tools/doe/real_comparison/execution.py"
    implementation = Path(x.__file__)
    seal = {"files": {"rules.md": sha256(tmp_path / "rules.md")},
            "implementation_files": {relative: sha256(implementation)}}
    write_json(tmp_path / "evaluation-rules-freeze.json", seal)
    assert x.verify_evaluation_rules(tmp_path) == seal
    seal["implementation_files"][relative] = "0" * 64
    write_json(tmp_path / "evaluation-rules-freeze.json", seal)
    with pytest.raises(x.ExecutionStop, match="implementation changed"):
        x.verify_evaluation_rules(tmp_path)
    (tmp_path / "rules.md").write_text("Changed rule", encoding="utf-8")
    with pytest.raises(x.ExecutionStop, match="sealed experiment file changed"):
        x.verify_evaluation_rules(tmp_path)


def test_budget_counts_actual_dispatches_not_queued_and_stops_at_reported_limit(tmp_path):
    workflow(tmp_path)
    request(tmp_path, counters={"resp": counters(8_000_001)})
    request(tmp_path, index=2, dispatched=False)
    with pytest.raises(x.ExecutionStop, match="eight-million"):
        x._budget(tmp_path, "w", dispatching=True)
    assert len(x.pending_requests(tmp_path)) == 1
    assert x.replay_execution(tmp_path)["actual_child_requests"] == 1


def test_outstanding_request_has_timeout_and_no_automatic_resend(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, dispatched=True)
    (directory / "response.json").unlink()
    old = datetime.now(timezone.utc) - timedelta(minutes=46)
    write_json(directory / "dispatch.json", {"dispatched_at": old.isoformat(), "protocol_conformant": True})
    with pytest.raises(x.ExecutionStop, match="45-minute"):
        x._budget(tmp_path, "w")
    assert x.pending_requests(tmp_path) == []


def test_mailbox_resume_reuses_exact_answer_and_rejects_prompt_change(tmp_path):
    workflow(tmp_path)
    request(tmp_path, counters={"resp": counters()})
    client = x.MailboxClient(tmp_path, "w", mode="calibration", token_counter=lambda _: 1)
    assert client.complete("Core 原文") == "Visible reply"
    assert len(x._requests(tmp_path)) == 1
    changed = x.MailboxClient(tmp_path, "w", mode="calibration", token_counter=lambda _: 1)
    with pytest.raises(x.ExecutionStop, match="differs"):
        changed.complete("Core changed")


def test_delivery_guard_does_not_clip_or_queue(tmp_path):
    workflow(tmp_path)
    client = x.MailboxClient(tmp_path, "w", mode="calibration", token_counter=lambda _: 300001)
    with pytest.raises(x.ExecutionStop, match="no clipping"):
        client.complete("Genuine source 内容")
    assert x._requests(tmp_path) == []


def test_native_composition_rebuilds_graph_and_injects_every_stage(tmp_path):
    src = source(tmp_path)
    stage, calls = tmp_path / "attempt", []
    stage.mkdir()
    def graph(source_path, **kwargs):
        calls.append(("graph", source_path, kwargs))
        assert kwargs["initial_analysis"] is None and kwargs["config"] == {}
        assert kwargs["extraction_factory"] is kwargs["audit_factory"]
        return {"last_valid_cfg": {"native": "graph"}, "passed_cfg": None}
    def prepare(source_path, selected, **kwargs):
        calls.append(("prepare", source_path, kwargs))
        assert read(selected) == {"cfg": {"native": "graph"}}
        assert kwargs["user_request"] is None and kwargs["config"] == {}
    def run(directory, **kwargs):
        calls.append(("analysis", directory, kwargs))
        factories = [kwargs[k] for k in ("client_factory", "review_client_factory", "repair_client_factory",
                     "task_client_factory", "task_repair_client_factory")]
        assert all(f is factories[0] for f in factories)
        return {"status": "diagnostic", "stage": "finished"}
    with patch("skillflow.graph.feedback.runner.refine_skill", graph), patch("skillflow.pipeline.prepare_analysis_run", prepare), patch("skillflow.pipeline.run_analysis", run):
        result = x._native_pipeline(src, stage, type("Client", (), {"complete": lambda self, p: "unused"})())
    assert [c[0] for c in calls] == ["graph", "prepare", "analysis"]
    assert result["selected_graph"] == "native_last_valid_cfg" and result["status"] == "diagnostic"


def test_provider_mismatch_is_preserved_but_never_accepted(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, dispatched=False)
    write_json(directory / "dispatch.json", {"agent_session_id": "child", "protocol_conformant": True})
    parsed = {"observed_configuration": [{"model_provider": "other"}], "protocol_status": "conformant",
              "configuration_verified": True, "completed": True, "usage": {"by_response_id": {"resp": counters()}}}
    with patch("tools.doe.direct_baseline.parse_receipt", return_value=("Visible answer", parsed)):
        result = x.import_response(tmp_path, "w_q001", receipt_path="unused")
    assert result["accepted"] is False and result["answer"] == "Visible answer"
    assert read(directory / "receipt.json")["provider_verified"] is False
    assert x.usage_summary(tmp_path)["totals"]["total_tokens"] == 10


def test_review_binding_never_selects_a_different_repeat_or_source(tmp_path):
    item = {"workflow_id": "c_audit_r1_review", "original_workflow_id": "c_audit_r1", "kind": "review",
            "case_id": "c", "source_sha256": "s", "method": "audit", "repeat": 1}
    original = tmp_path / "workflows/c_audit_r1"
    write_json(original / "registration.json", {**item, "kind": "main"})
    assert x._validate_review(tmp_path, item, "c_audit_r1") is None
    with pytest.raises(x.ExecutionStop, match="prespecified"):
        x._validate_review(tmp_path, item, "c_audit_r2")
    write_json(original / "registration.json", {**item, "kind": "main", "source_sha256": "other"})
    with pytest.raises(x.ExecutionStop, match="does not match"):
        x._validate_review(tmp_path, item, "c_audit_r1")


def test_fresh_spawn_protocol_violations_remain_actual_calls(tmp_path):
    workflow(tmp_path)
    request(tmp_path, dispatched=False)
    with patch.object(x, "_calibration_source", return_value="transcribe"):
        result = x.mark_dispatched(tmp_path, "w_q001", agent_name="/root/child", agent_session_id="child",
                 root_session_id="root", spawn_call_id="call", fork_turns="all")
    assert result["protocol_conformant"] is False
    assert x.replay_execution(tmp_path)["actual_child_requests"] == 1


def test_new_worker_queues_full_core_and_waits_for_one_imported_reply(tmp_path):
    workflow(tmp_path)
    client = x.MailboxClient(tmp_path, "w", mode="calibration", token_counter=lambda _: 1, poll_seconds=0.001)
    returned = []
    worker = threading.Thread(target=lambda: returned.append(client.complete("Exact {core} 原文")))
    worker.start()
    for _ in range(1000):
        pending = x.pending_requests(tmp_path)
        if pending:
            break
        threading.Event().wait(0.001)
    directory = Path(pending[0]["request_dir"])
    assert "Exact {core} 原文" in (directory / "prompt.txt").read_text(encoding="utf-8")
    write_json(directory / "response.json", {"accepted": True, "answer": "Answer", "answer_sha256": x._digest("Answer")})
    worker.join(timeout=2)
    assert returned == ["Answer"] and not worker.is_alive()


def test_disclosed_actual_delivery_mismatch_overrides_optimistic_dispatch_flag(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, counters={"r": counters()})
    write_json(directory / "delivery-violation.json", {"status": "violated", "reason": "Source code was changed during manual embedding."})
    before = (directory / "dispatch.json").read_bytes()
    result = x.replay_execution(tmp_path)
    assert result["byte_integrity"]["status"] == "passed"
    assert result["protocol_conformance"]["status"] == "violated" and result["status"] == "failed"
    assert (directory / "dispatch.json").read_bytes() == before
    assert list((directory / "protocol-assessments").glob("*.json"))
    client = x.MailboxClient(tmp_path, "w", mode="calibration", token_counter=lambda _: 1)
    with pytest.raises(x.ExecutionStop, match="protocol violation"):
        client.complete("Core 原文")


def test_mark_dispatched_never_calls_disclosed_mismatch_conformant(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, dispatched=False)
    with patch.object(x, "_calibration_source", return_value="transcribe"):
        saved = x.mark_dispatched(tmp_path, "w_q001", agent_name="child", agent_session_id="child", spawn_call_id="call",
                                  root_session_id="root", fork_turns="none", actual_spawn={"delivery_integrity": "violated"})
    assert saved["protocol_conformant"] is False
    assert x.assess_request_protocol(directory)["status"] == "violated"


def test_replay_missing_usage_is_incomplete_and_kept_separate_from_byte_integrity(tmp_path):
    workflow(tmp_path)
    request(tmp_path)
    replay = x.replay_execution(tmp_path)
    assert replay["byte_integrity"]["status"] == "passed"
    assert replay["usage_completeness"]["status"] == "unknown"
    assert replay["status"] == "incomplete"
    assert replay["usage"]["totals"]["total_tokens"] is None


def parsed_receipt(provider="openai"):
    return {"observed_configuration": [{"model_provider": provider}], "protocol_status": "conformant",
            "configuration_verified": True, "completed": True, "usage": {"by_response_id": {"r": counters()}},
            "receipt_sha256": "exact-receipt"}


def test_exact_response_import_is_idempotent_and_does_not_rewrite_timestamp(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, dispatched=False)
    write_json(directory / "dispatch.json", {"agent_session_id": "child", "protocol_conformant": True})
    with patch("tools.doe.direct_baseline.parse_receipt", side_effect=lambda *a, **k: ("Answer", parsed_receipt())):
        first = x.import_response(tmp_path, "w_q001", receipt_path="exact")
        saved = (directory / "response.json").read_bytes()
        second = x.import_response(tmp_path, "w_q001", receipt_path="exact")
    assert first == second and (directory / "response.json").read_bytes() == saved
    assert first["accepted"] is True


def test_import_records_rejection_for_disclosed_source_mismatch(tmp_path):
    workflow(tmp_path)
    directory = request(tmp_path, dispatched=False)
    write_json(directory / "dispatch.json", {"agent_session_id": "child", "protocol_conformant": True,
               "actual_spawn": {"delivery_integrity": "violated"}})
    with patch("tools.doe.direct_baseline.parse_receipt", side_effect=lambda *a, **k: ("Answer", parsed_receipt())):
        first = x.import_response(tmp_path, "w_q001", receipt_path="exact")
        second = x.import_response(tmp_path, "w_q001", receipt_path="exact")
    assert first == second and first["accepted"] is False and first["answer"] == "Answer"
    assert x.replay_execution(tmp_path)["status"] == "failed"


def test_main_and_review_prompts_require_exact_frozen_rendering(tmp_path):
    from tools.doe.real_comparison.inputs import render_direct, render_review
    (tmp_path / "prompts").mkdir()
    (tmp_path / "cases/c").mkdir(parents=True)
    (tmp_path / "cases/c/source-bundle.txt").write_text("Original {source_bundle} 原文", encoding="utf-8")
    (tmp_path / "prompts/audit.txt").write_text("RULES {user_request}\nSOURCE {source_bundle}", encoding="utf-8")
    (tmp_path / "prompts/review.txt").write_text("{original_task}\n{original_answer}", encoding="utf-8")
    main = {"kind": "main", "method": "audit", "case_id": "c", "repeat": 1, "source_sha256": "s"}
    exact = render_direct(tmp_path, "c", "audit")
    x._verify_formal_direct_prompt(tmp_path, main, exact)
    with pytest.raises(x.ExecutionStop, match="exact frozen"):
        x._verify_formal_direct_prompt(tmp_path, main, exact + "\nUnfrozen extra rule")
    original = tmp_path / "workflows/c_audit_r1"
    write_json(original / "registration.json", main)
    (original / "answer.txt").write_text("Exact first answer", encoding="utf-8")
    write_json(original / "result.json", {"answer_sha256": sha256(original / "answer.txt")})
    review = {**main, "kind": "review", "original_workflow_id": "c_audit_r1"}
    expected = render_review(tmp_path, "c", "audit", "Exact first answer")
    x._verify_formal_direct_prompt(tmp_path, review, expected)
    with pytest.raises(x.ExecutionStop, match="exact frozen"):
        x._verify_formal_direct_prompt(tmp_path, review, expected + "\nScoring hint")


def test_production_code_freeze_fails_closed_on_concurrent_semantic_change(tmp_path):
    x.snapshot_production_code(tmp_path)
    from skillflow.common.recording import implementation_provenance
    changed = implementation_provenance()
    one = next(iter(changed["files"]))
    changed["files"][one] = "different"
    with patch("skillflow.common.recording.implementation_provenance", return_value=changed):
        with pytest.raises(x.ExecutionStop, match="production semantic code differs"):
            x.verify_production_code(tmp_path)


def test_gate_builder_refuses_failed_calibration_without_writing_approval(tmp_path):
    fake_gate(tmp_path)
    (tmp_path / "gate.json").unlink()
    write_json(tmp_path / "calibration.json", {"status": "failed", "runtime": x.EXPECTED, "cases": list(x.CALIBRATION)})
    with pytest.raises(x.ExecutionStop, match="calibrations must pass"):
        x.build_formal_gate(tmp_path)
    assert not (tmp_path / "gate.json").exists()


def test_output_freeze_blocks_all_formal_regeneration_before_reading_inputs(tmp_path):
    write_json(tmp_path / "output-freeze.json", {"frozen": True})
    with pytest.raises(x.ExecutionStop, match="regeneration is forbidden"):
        x.run_workflow(tmp_path, "c_audit_r1", source_path="unread", prompt="unread")
    client = x.MailboxClient(tmp_path, "c_audit_r1", token_counter=lambda _: 1)
    with pytest.raises(x.ExecutionStop, match="regeneration is forbidden"):
        client.complete("unread")
    assert not (tmp_path / "workflows").exists()


def test_not_reviewable_terminal_timing_includes_existing_workflow_wait(tmp_path):
    item = {"workflow_id": "c_audit_r1_review", "original_workflow_id": "c_audit_r1", "kind": "review",
            "case_id": "c", "source_sha256": "s", "method": "audit", "repeat": 1}
    write_json(tmp_path / "schedule.json", {"main": [], "reviews": [item]})
    write_json(tmp_path / "workflows/c_audit_r1/registration.json", {**item, "kind": "main"})
    started = (datetime.now(timezone.utc) - timedelta(seconds=61)).isoformat()
    write_json(tmp_path / "workflows/c_audit_r1_review/state.json", {"started_at": started})
    with patch.object(x, "verify_gate", return_value={}), patch("skillflow.common.inputs.snapshot.inspect_input", return_value=(None, None, {"source_sha256": "s"})):
        result = x.run_workflow(tmp_path, item["workflow_id"], source_path="unused", original_workflow_id="c_audit_r1")
    assert result["status"] == "not_reviewable" and result["finished_at"]
    assert result["timing"]["workflow_elapsed_seconds"] >= 61
    assert x._requests(tmp_path) == []
