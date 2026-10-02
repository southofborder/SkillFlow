"""Execution, transport, isolation and offline replay of the single-task runner.

Synthetic responses exercise record contracts, not semantic correctness. The real
Lean renderer is used: conversion tests separately exercise its adversarial input.
"""
from copy import deepcopy
import json
from threading import Event
from pathlib import Path
import pytest

from skill_ir.backtrace import runner
from skill_ir.backtrace.evaluation import compare_expectation
from skill_ir.semantic_contract import CONTRACT_VERSION, contract_binding


def answer(prompt):
    payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
    originals = {f["path"]: f["content"].splitlines() for f in payload["source_files"]}
    source_refs = [{"unit_id": u["id"], "file": u["file"], "start_line": u["start_line"],
                    "end_line": u["end_line"], "quote": "\n".join(originals[u["file"]][u["start_line"]-1:u["end_line"]])} for u in payload["source_units"]]
    controlled = payload["required_coverage"]["reviewed_controlled_unit_ids"]
    return {"schema_version": 5, "outcome": "completed", "contract_version": CONTRACT_VERSION,
            "findings": [{"id": "finding_1", "kind": "semantic", "status": "represented",
             "source_requirement": "仅用于执行协议测试的原文引用，不是语义答案。",
             "actual_representation": "仅用于执行协议测试的受控记录引用。", "reason": "工程测试引用输入。",
             "source_refs": source_refs, "controlled_refs": [{"unit_id": key} for key in controlled],
             "basis": ["explicit_graph"], "suggestions": []}],
            "reviewed_source_unit_ids": payload["required_coverage"]["reviewed_source_unit_ids"],
            "reviewed_controlled_unit_ids": controlled, "notes": []}


class FakeFactory:
    def __init__(self, fail_at=None, malformed_at=None, secret=""):
        self.prompts, self.fail_at, self.malformed_at, self.secret = [], fail_at, malformed_at, secret

    def __call__(self, writer, checkpoint):
        factory = self
        class Client:
            def complete(self, prompt):
                factory.prompts.append(prompt)
                if len(factory.prompts) == factory.fail_at:
                    checkpoint([{"status": "error", "prompt": prompt, "error": factory.secret,
                                 "http_attempts": [{"http_status": 200, "stream": {"outcome": "incomplete"}}]}])
                    raise RuntimeError("incomplete accepted response " + factory.secret)
                response = "invalid JSON" if len(factory.prompts) == factory.malformed_at else answer(prompt)
                checkpoint([{"status": "complete", "prompt": prompt, "response": response,
                             "returned_model": "fake-model", "usage": {"total_tokens": 10},
                             "http_attempts": [{"http_status": 200}]}])
                return response
        return Client()


@pytest.fixture
def prepared(tmp_path):
    directory = tmp_path / "run"
    runner.prepare_run(directory, review30=False)
    return directory


def no_network(*args, **kwargs):
    pytest.fail("offline replay must not create an API client")


def test_prepare_bound_inputs_and_single_task_inventory(prepared):
    manifest = runner.verify_run(prepared, live=True)
    assert manifest["schema_version"] == 5
    assert all(manifest[key] == value for key, value in contract_binding().items())
    assert manifest["planned_logical_calls"] == 5
    assert [c["case_id"] for c in manifest["cases"]] == list(runner.CASE_IDS)
    assert all(c["fidelity_status"] == "passed" for c in manifest["cases"])
    assert len(list((prepared / "inputs").rglob("controlled.json"))) == 5
    assert not (prepared / "calls").exists()
    for path in (prepared / "inputs").rglob("*"):
        if path.is_file():
            raw = path.read_text(encoding="utf-8")
            assert not any(marker in raw for marker in ("gold-r0", "oracle_key", "expected_findings"))
    (prepared / "inputs/c01/cfg.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Prepared input changed"):
        runner.verify_run(prepared, live=False)


def test_exactly_five_calls_isolated_payload_and_offline_replay(prepared, monkeypatch):
    factory = FakeFactory()
    result = runner.execute_run(prepared, client_factory=factory, workers=1)
    assert len(factory.prompts) == result["recorded_logical_calls"] == 5
    assert result["execution_status"] == "complete", result["stages"]
    assert set(result["stages"]) == set(runner.CASE_IDS)
    allowed = {"source_files", "source_line_index", "source_units", "controlled_text", "controlled_units", "required_coverage"}
    for prompt in factory.prompts:
        payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
        assert set(payload) == allowed
        assert '"graph_refs"' not in json.dumps(payload)
        assert not {"case_id", "oracle_key", "expected_findings", "variant", "graph"}.intersection(payload)
    hashes = {str(p): runner.sha_file(p) for p in (prepared / "calls").rglob("*") if p.is_file()}
    from skill_ir.backtrace import __main__ as cli
    monkeypatch.setattr(cli, "streaming_factory", no_network)
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    assert replay["evaluation"] == result["evaluation"]
    assert hashes == {str(p): runner.sha_file(p) for p in (prepared / "calls").rglob("*") if p.is_file()}
    resumed = runner.execute_run(prepared, client_factory=no_network, workers=1)
    assert resumed["stages"] == result["stages"]
    assert cli.main(["replay", "--run-dir", str(prepared)]) == 0
    assert hashes == {str(p): runner.sha_file(p) for p in (prepared / "calls").rglob("*") if p.is_file()}
    assert len(list((prepared / "suggestions").glob("*.md"))) == 5


@pytest.mark.parametrize("malformed", [False, True])
def test_case_failure_continues_and_accepted_response_is_never_resent(prepared, malformed):
    secret = "test-credential-removed-7654"
    factory = FakeFactory(fail_at=None if malformed else 2, malformed_at=2 if malformed else None, secret=secret)
    result = runner.execute_run(prepared, client_factory=factory, secrets=(secret,), workers=1)
    assert len(factory.prompts) == 5
    assert result["stages"]["c02"]["status"] == "execution_error"
    assert all(result["stages"][c]["status"] == "complete" for c in ("c01", "c03", "c04", "c05"))
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, secrets=(secret,), workers=1)
    assert replay["stages"] == result["stages"]
    for path in prepared.rglob("*"):
        if path.is_file():
            assert secret.encode() not in path.read_bytes()


def test_interruption_starts_no_calls(prepared):
    stopped = Event(); stopped.set()
    result = runner.execute_run(prepared, client_factory=no_network, workers=1, stop_event=stopped)
    assert result["execution_status"] == "interrupted"
    assert result["recorded_logical_calls"] == 0
    assert all(s["status"] == "blocked" for s in result["stages"].values())
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    assert replay["execution_status"] == "interrupted"
    assert replay["recorded_execution_calls"] == 0


@pytest.mark.parametrize("version", [1, 2, 3])
def test_old_version_rejected_without_migration(tmp_path, version):
    (tmp_path / "manifest.json").write_text(json.dumps({"schema_version": version}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported run version"):
        runner.verify_run(tmp_path, live=False)
    assert json.loads((tmp_path / "manifest.json").read_text())["schema_version"] == version


def test_old_suite_is_not_kept_as_an_alias(tmp_path):
    with pytest.raises(ValueError, match="Unknown audit suite"):
        runner.prepare_run(tmp_path / "old", suite="semantics-v3-seven", review30=False)
    assert not (tmp_path / "old").exists()


def test_stored_response_or_transport_tampering_is_execution_error(prepared):
    runner.execute_run(prepared, client_factory=FakeFactory(), workers=1)
    path = prepared / "calls/c03/a001/call.json"
    call = runner.read_json(path); call["response"]["notes"] = ["tampered"]
    path.write_text(json.dumps(call), encoding="utf-8")
    result = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert result["stages"]["c03"]["status"] == "execution_error"
    assert "digest mismatch" in result["stages"]["c03"]["error"]
    path = prepared / "calls/c04/a001/transport.json"
    transport = runner.read_json(path); transport[0]["returned_model"] = "changed"
    path.write_text(json.dumps(transport), encoding="utf-8")
    result = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert result["stages"]["c04"]["status"] == "execution_error"
    assert next(c for c in result["calls"] if c["case_id"] == "c04")["trace_integrity_error"]


def test_conversion_recheck_failure_does_not_reach_model(prepared, monkeypatch):
    from skill_ir.backtrace import controlled
    original = controlled.verify_controlled
    count = 0
    def check(document, **kwargs):
        nonlocal count
        count += 1
        if count == 2:
            raise ValueError("invalid controlled certificate")
        return original(document, **kwargs)
    monkeypatch.setattr(controlled, "verify_controlled", check)
    factory = FakeFactory()
    result = runner.execute_run(prepared, client_factory=factory, workers=1)
    assert len(factory.prompts) == 4
    assert result["stages"]["c02"]["status"] == "execution_error"
    assert result["conversion"]["c02"] == "failed"


@pytest.mark.parametrize("relative,content", [("calls/c02/a001/call.json", "{"),
                                            ("calls/c02/a001/transport.json", "{}"),
                                            ("calls/c02/a001/call.json", "{}")])
def test_corrupt_records_still_produce_a_report_for_other_cases(prepared, relative, content):
    runner.execute_run(prepared, client_factory=FakeFactory(), workers=1)
    (prepared / relative).write_text(content, encoding="utf-8")
    result = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert result["stages"]["c02"]["status"] == "execution_error"
    assert result["stages"]["c05"]["status"] == "complete"
    assert (prepared / "replay/report.md").is_file()


def test_oracle_matching_is_only_a_candidate_and_failure_not_a_miss():
    expected = {"oracle_finding_id": "external", "acceptable_statuses": ["omitted"],
                "graph_refs": ["/blocks/b/instructions"], "source_refs": []}
    assert compare_expectation(expected, {"status": "execution_error"})["status"] == "execution_error"
    record = {"status": "complete", "result": {"findings": [{"id": "f", "status": "omitted",
              "graph_refs": ["/blocks/b"], "source_refs": []}]}}
    assert compare_expectation(expected, record)["status"] == "candidate_match"


def test_removed_runtime_roles_and_exporter_are_absent():
    package = Path(runner.__file__).parent
    assert not (package / "structured.py").exists()
    assert not (runner.EXPERIMENT_ROOT / "tools/export_diagnostics.py").exists()
    removed = ("def requirements_prompt", "def narrative_prompt", "def source_graph_prompt", "def graph_retelling_prompt",
               "def extract_requirements", "def generate_narrative", "def audit_source_graph", "def audit_graph_retelling",
               "class RequirementSet", "class Retelling", '"planned_logical_calls": 21')
    for path in package.glob("*.py"):
        content = path.read_text(encoding="utf-8")
        assert not any(token in content for token in removed), path


def test_seven_suite_uses_independent_frozen_sources_and_exactly_seven_calls(tmp_path):
    directory = tmp_path / "seven"
    manifest = runner.prepare_run(directory, suite="semantics-v5-seven", review30=False)
    assert manifest["planned_logical_calls"] == 7
    assert manifest["config"]["timeout_ms"] == 600000
    assert manifest["cases"][5]["selection"]["sample_index"] == "001"
    assert manifest["cases"][6]["selection"]["sample_index"] == "010"
    assert manifest["cases"][5]["source_sha256"] != manifest["source_sha256"]
    factory = FakeFactory()
    result = runner.execute_run(directory, client_factory=factory, workers=1)
    assert len(factory.prompts) == result["recorded_logical_calls"] == result["recorded_execution_calls"] == 7
    assert result["execution_status"] == "complete", result["stages"]
    for case, prompt in zip(manifest["cases"], factory.prompts, strict=True):
        payload = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
        source = runner.read_json(directory / "inputs" / case["case_id"] / "source.json")
        assert payload["source_files"] == [{key: item[key] for key in ("path", "content")} for item in source["files"]]
        assert not {"oracle_key", "case_id", "selection", "previous_audit", "graph"}.intersection(payload)
    assert result["evaluation"]["cases"]["c06"]["evaluation_status"] == "assistant_review_required"
    replay = runner.execute_run(directory, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    assert replay["evaluation"] == result["evaluation"]
    report = (directory / "report.md").read_text(encoding="utf-8")
    assert "保留项" in report and CONTRACT_VERSION in report
    assert "七类检查记录" not in report and "精确保留" not in report
    assert result["schema_version"] == 5
    summary = result["stages"]["c01"]["result"]["representation_summary"]
    assert summary == {"represented_ids": ["finding_1"], "conservative_ids": []}


def test_terminal_transport_retry_is_bounded_recorded_and_replayed(prepared, monkeypatch):
    from skill_ir import audit_execution
    monkeypatch.setattr(audit_execution, "retry_delay_ms", lambda _: 0)
    factory = FakeFactory()
    original_factory = factory.__call__
    attempts = []

    def failing_factory(writer, checkpoint):
        delegate = original_factory(writer, checkpoint)
        class Client:
            def complete(self, prompt):
                attempts.append(prompt)
                if len(attempts) == 1:
                    checkpoint([{"status": "error", "prompt": prompt, "error": "timed out",
                                 "error_type": "TimeoutError", "http_attempts": [{"status": "error"}]}])
                    raise TimeoutError("timed out")
                return delegate.complete(prompt)
        return Client()

    result = runner.execute_run(prepared, client_factory=failing_factory, workers=1)
    assert result["execution_status"] == "complete", result["stages"]
    assert result["recorded_logical_calls"] == 5
    assert result["recorded_execution_calls"] == 6
    assert result["audit_execution_retries"] == 1
    assert attempts[0] == attempts[1]
    decisions = result["stages"]["c01"]["audit_executions"]
    assert [decision["status"] for decision in decisions] == ["error", "complete"]
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    resumed = runner.execute_run(prepared, client_factory=no_network, workers=1)
    assert resumed["stages"] == result["stages"]


def test_accepted_response_then_interrupt_does_not_resend(prepared):
    factory = FakeFactory()
    original_factory = factory.__call__
    attempted = []
    def interrupted_factory(writer, checkpoint):
        delegate = original_factory(writer, checkpoint)
        class Client:
            def complete(self, prompt):
                response = delegate.complete(prompt)
                attempted.append(prompt)
                raise KeyboardInterrupt("stopped after accepted response")
        return Client()
    result = runner.execute_run(prepared, client_factory=interrupted_factory, workers=1)
    assert result["execution_status"] == "interrupted"
    assert len(attempted) == result["recorded_logical_calls"] == 1
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    remaining = FakeFactory()
    resumed = runner.execute_run(prepared, client_factory=remaining, workers=1)
    assert resumed["execution_status"] == "complete", resumed["stages"]
    assert len(remaining.prompts) == 4
    assert resumed["recorded_execution_calls"] == 5
    replay_resumed = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay_resumed["stages"] == resumed["stages"]


def test_contract_or_retry_policy_cannot_be_changed_after_prepare(prepared):
    path = prepared / "manifest.json"
    manifest = runner.read_json(path)
    manifest["policy"]["max_audit_execution_retries"] = 5
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="manifest digest mismatch"):
        runner.verify_run(prepared, live=True)


@pytest.mark.parametrize("live", [False, True])
def test_implementation_identity_mismatch_rejects_both_resume_and_replay(prepared, monkeypatch, live):
    identity = runner.implementation_provenance()
    identity["sha256"] = "0" * 64
    monkeypatch.setattr(runner, "implementation_provenance", lambda: identity)
    with pytest.raises(ValueError, match="Implementation changed"):
        runner.verify_run(prepared, live=live)


def test_conservative_report_preserves_rule_candidates_and_lost_precision():
    from skill_ir.backtrace.report import render_suggestions
    finding = {"id": "kept_candidates", "kind": "semantic", "status": "represented",
               "source_requirement": "使用实际分支结果", "actual_representation": "两个候选结果",
               "reason": "候选均有源文和分支依据", "source_refs": [], "controlled_refs": [],
               "graph_refs": ["/blocks/b/instructions/0/inputs"], "suggestions": [],
               "conservative": {"rule_id": "DEP-MERGE", "candidate_fact_ids": ["a", "b"],
                                "lost_distinctions": ["尚未区分路径与选中结果"], "reason": "分支合流候选",
                                "graph_refs": ["/blocks/b/instructions/0/inputs/0", "/blocks/b/instructions/0/inputs/1"]}}
    report = render_suggestions("example", {"status": "complete", "result": {"findings": [finding]}})
    assert all(text in report for text in ("DEP-MERGE", "a, b", "尚未区分路径与选中结果", "保守保留"))
    assert "精确保留" not in report and "核对类别" not in report


def test_semantic_failure_report_cannot_look_like_no_findings():
    from skill_ir.backtrace.report import render_suggestions
    report = render_suggestions("example", {"status": "semantic_failure", "reason": "源文要求相互冲突。"})
    assert "源文要求相互冲突" in report
    assert "模型没有报告业务差异" not in report


def test_parallel_interruption_replays_other_already_accepted_case_independently(prepared):
    from skill_ir.backtrace.prompts import source_controlled_prompt
    stopped, first_started, second_started = Event(), Event(), Event()
    prompts = {
        source_controlled_prompt(runner.read_json(prepared / "inputs" / key / "source.json"),
                                 runner.read_json(prepared / "inputs" / key / "controlled.json")): key
        for key in runner.CASE_IDS
    }
    observed = []

    def factory(writer, checkpoint):
        class Client:
            def complete(self, prompt):
                key = prompts[prompt]
                observed.append(key)
                if key == "c01":
                    first_started.set()
                    assert second_started.wait(15), "second request must already be in flight"
                elif key == "c02":
                    second_started.set()
                    assert first_started.wait(15)
                    assert stopped.wait(15), "first worker must record the interruption before second completes"
                else:
                    pytest.fail("a new request started after interruption")
                response = answer(prompt)
                checkpoint([{"status": "complete", "prompt": prompt, "response": response,
                             "returned_model": "fake-model", "usage": {}, "http_attempts": [{"http_status": 200}]}])
                if key == "c01":
                    raise KeyboardInterrupt("first case interrupted after acceptance")
                return response
        return Client()

    result = runner.execute_run(prepared, client_factory=factory, workers=2, stop_event=stopped)
    assert sorted(observed) == ["c01", "c02"]
    assert result["stages"]["c01"]["status"] == "interrupted"
    assert result["stages"]["c02"]["status"] == "complete"
    assert all(result["stages"][key]["status"] == "blocked" for key in ("c03", "c04", "c05"))
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == result["stages"]
    assert replay["execution_status"] == result["execution_status"] == "interrupted"
    assert replay["recorded_execution_calls"] == 2


def test_invalid_complete_response_consumed_after_interrupt_remains_execution_error_in_replay(prepared):
    def interrupted_factory(writer, checkpoint):
        class Client:
            def complete(self, prompt):
                checkpoint([{"status": "complete", "prompt": prompt, "response": "invalid JSON",
                             "returned_model": "fake-model", "usage": {}, "http_attempts": [{"http_status": 200}]}])
                raise KeyboardInterrupt("accepted invalid response then interrupted")
        return Client()

    interrupted = runner.execute_run(prepared, client_factory=interrupted_factory, workers=1)
    assert interrupted["stages"]["c01"]["status"] == "interrupted"
    remaining = FakeFactory()
    resumed = runner.execute_run(prepared, client_factory=remaining, workers=1)
    assert len(remaining.prompts) == 4
    assert resumed["stages"]["c01"]["status"] == "execution_error"
    assert resumed["recorded_execution_calls"] == 5
    assert runner.read_json(prepared / "boundaries/c01.json")["pending"] is False
    replay = runner.execute_run(prepared, replay=True, client_factory=no_network, workers=1)
    assert replay["stages"] == resumed["stages"]
    assert replay["execution_status"] == resumed["execution_status"] == "completed_with_errors"


def test_execution_boundary_is_bound_and_tampering_rejected(prepared):
    stopped = Event(); stopped.set()
    runner.execute_run(prepared, client_factory=no_network, workers=1, stop_event=stopped)
    path = prepared / "execution-state.json"
    state = runner.read_json(path)
    state["not_started_case_ids"] = []
    path.write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises(ValueError, match="Execution boundary digest mismatch"):
        runner.execute_run(prepared, replay=True, client_factory=no_network)
