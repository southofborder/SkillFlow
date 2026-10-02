"""Stage wiring for the new from-source feedback and annotation experiment."""
from copy import deepcopy
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.inputs.snapshot import freeze_input, read_snapshot
from skill_ir.recording import canonical_sha256, read_json
from skill_ir.semantic_contract import contract_binding
from security_profile.helpers import graph

SCRIPT = Path(__file__).resolve().parents[2] / "experiments/security_profile/tools/run_full_pipeline.py"


@pytest.fixture(scope="module")
def driver():
    spec = importlib.util.spec_from_file_location("test_full_pipeline_driver", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def plan(driver):
    return driver.build_plan()


@pytest.fixture
def wired(driver, plan, monkeypatch):
    import skill_ir.feedback.runner as feedback_runner
    import skill_ir.security_profile.runner as annotation_runner
    import skill_ir.recording as recording
    executed, annotated, clients = [], [], []
    behavior = {"status": "audit_passed", "graph": graph(), "revision": 0}
    monkeypatch.setattr(driver, "build_plan", lambda: plan[:2])
    monkeypatch.setattr(driver, "_renderer_identity", lambda renderer: {"path": "test-printer", "sha256": "test"})

    def refine(source, *, run_dir, **kwargs):
        executed.append((source, run_dir, kwargs))
        if not (run_dir / "inputs").exists():
            freeze_input(source, run_dir, ArtifactWriter(()))
        _, bundle, _ = read_snapshot(run_dir)
        current = deepcopy(behavior["graph"])
        revision = behavior["revision"]
        rounds = [] if current is None else [{"revision": revision,
            "graph_sha256": canonical_sha256(current), "structural": {"status": "passed"}}]
        if behavior["status"] == "extraction_error" and current is not None:
            rounds.append({"revision": revision + 1, "graph_sha256": None, "structural": None})
        value = {"status": behavior["status"], "reason": "fixture stop", "last_valid_cfg": current,
                 "representation_summary": {"represented_ids": ["semantic-item"], "conservative_ids": []},
                 "source_sha256": bundle["source_sha256"], "rounds": rounds,
                 "counts": {"extraction_logical_calls": 1, "audit_logical_calls": 1,
                            "audit_execution_calls": 1, "audit_execution_retries": 0,
                            "semantic_revisions": revision, "structural_repairs": 0,
                            "http_attempts": 2, "http_retries": 0, "http_attempts_observed": True}}
        ArtifactWriter(()).json(run_dir / "manifest.json", {"initial_analysis": kwargs["initial_analysis"]})
        ArtifactWriter(()).json(run_dir / "result.json", value)
        if behavior.get("stop"):
            kwargs["stop_event"].set()
        return value

    def annotate(run_dir, **kwargs):
        annotated.append((run_dir, kwargs))
        value = {"status": "complete", "reason": "", "profiles": {"ir_read": {}},
                 "counts": {"logical_calls": 1, "http_attempts": 1, "http_retries": 0,
                            "http_attempts_observed": True}}
        ArtifactWriter(()).json(run_dir / "result.json", value)
        return value

    def factory(config, *, env_file=None):
        clients.append((config, env_file))
        return object(), ()

    monkeypatch.setattr(feedback_runner, "refine_skill", refine)
    monkeypatch.setattr(feedback_runner, "replay_run", lambda run_dir, **kwargs: read_json(run_dir / "result.json"))
    monkeypatch.setattr(annotation_runner, "run_annotation", annotate)
    monkeypatch.setattr(annotation_runner, "replay_run", lambda run_dir: read_json(run_dir / "result.json"))
    monkeypatch.setattr(recording, "streaming_factory", factory)
    return SimpleNamespace(behavior=behavior, executed=executed, annotated=annotated, clients=clients)


def test_pinned_source_plan_discards_baseline_graph_identity(driver, plan):
    assert len(plan) == 30
    cases = [driver._source_case(item) for item in plan]
    assert [case["case_id"] for case in cases] == [f"{i:03}" for i in range(1, 31)]
    assert all("cfg" not in case and "analysis_path" not in case and "repetition" not in case for case in cases)
    assert driver.LIMITS["logical_calls_total"] == 630
    assert driver.LIMITS["execution_calls_total"] == 870


def test_new_timeout_does_not_rewrite_historical_baseline_config(driver):
    assert driver.public_config()["timeout_ms"] == 600000
    assert driver._sources.public_config()["timeout_ms"] == 180000
    assert driver.public_config()["model"] == "deepseek-v4-flash"
    assert "response_format" not in driver.public_config()
    assert driver._sources.public_config()["response_format"] == "json_object"


def test_from_source_stage_order_no_initial_graph_and_exact_source_binding(driver, wired, tmp_path):
    result = driver.execute(tmp_path / "live", workers=1)
    assert result["schema_version"] == 10
    assert result["profile_schema_version"] == "security-profile-v10"
    assert result["contract_sha256"] == contract_binding()["contract_sha256"]
    manifest = read_json(tmp_path / "live/manifest.json")
    assert manifest["profile_schema_version"] == "security-profile-v10"
    assert manifest["contract_version"] == contract_binding()["contract_version"]
    assert result["summary"]["feedback_statuses"] == {"audit_passed": 2}
    assert result["summary"]["annotation_statuses"] == {"complete": 2}
    for item in result["cases"].values():
        assert item["selection"]["representation_summary"] == {"represented_ids": ["semantic-item"], "conservative_ids": []}
        assert "precision_summary" not in item["selection"]
    assert len(wired.executed) == len(wired.annotated) == 2
    assert len(wired.clients) == 2
    assert "response_format" not in wired.clients[0][0]
    assert wired.clients[1][0]["response_format"] == "json_object"
    assert manifest["config"] == wired.clients[0][0]
    assert manifest["annotation_config"] == wired.clients[1][0]
    for (source, feedback_dir, args), (annotation_dir, annotation_args) in zip(wired.executed, wired.annotated):
        assert args["initial_analysis"] is None
        assert args["max_semantic_revisions"] == args["max_structural_repairs"] == 3
        assert args["max_audit_execution_retries"] == 2
        assert args["extraction_factory"] is args["audit_factory"]
        assert args["extraction_factory"] is not annotation_args["client_factory"]
        assert "response_format" not in args["config"]
        assert annotation_args["config"]["response_format"] == "json_object"
        assert source != feedback_dir
        assert annotation_dir.parent == feedback_dir.parent
        binding = read_json(feedback_dir.parent / "source-binding.json")
        assert binding["status"] == "passed"
        material = read_json(annotation_dir / "inputs/material.json")
        assert material["source"] == read_json(feedback_dir / "inputs/source.json")
        assert material["cfg"] == wired.behavior["graph"]
    assert result["summary"]["counts"]["total_logical_calls"] == 6
    assert result["summary"]["counts"]["total_execution_calls"] == 6


def test_same_outer_batch_version_rejects_old_profile_contract(driver, wired, tmp_path):
    directory = tmp_path / "legacy-profile"
    directory.mkdir()
    ArtifactWriter(()).json(directory / "manifest.json", {
        "schema_version": 8, "identity": driver.IDENTITY,
        "profile_schema_version": "security-profile-v2", "workers": 1,
    })
    with pytest.raises(ValueError, match="Unsupported full pipeline run version"):
        driver.execute(directory, mode="replay")
    assert not wired.executed and not wired.annotated


def test_last_valid_graph_after_later_failure_is_annotated_without_false_pass(driver, wired, tmp_path):
    wired.behavior.update(status="extraction_error", revision=1)
    result = driver.execute(tmp_path / "partial", workers=1)
    for item in result["cases"].values():
        assert item["selection"]["revision"] == 1
        assert item["selection"]["feedback_status"] == "extraction_error"
        assert item["selection"]["auditor_passed"] is False
        assert item["annotation"]["status"] == "complete"


def test_same_graph_in_several_rounds_uses_latest_structural_round(driver):
    current = graph()
    digest = canonical_sha256(current)
    selected = driver._selection({"last_valid_cfg": current, "status": "revision_limit", "source_sha256": "source",
        "rounds": [{"revision": i, "graph_sha256": digest, "structural": {"status": "passed"}} for i in range(4)]})
    assert selected["revision"] == 3 and not selected["auditor_passed"]
    with pytest.raises(ValueError, match="no matching"):
        driver._selection({"last_valid_cfg": current, "rounds": []})


def test_no_valid_graph_does_not_fall_back_or_call_annotation(driver, wired, tmp_path):
    wired.behavior.update(status="extraction_error", graph=None)
    result = driver.execute(tmp_path / "no-graph", workers=1)
    assert not wired.annotated
    assert result["summary"]["annotation_statuses"] == {"not_run": 2}
    for item in result["cases"].values():
        assert item["selection"] is None
        assert "不回退" in item["annotation"]["reason"]


def test_interrupt_blocks_annotation_and_further_case_submission(driver, wired, tmp_path):
    wired.behavior.update(status="interrupted", stop=True)
    live = driver.execute(tmp_path / "interrupted", workers=1)
    assert len(wired.executed) == 1 and not wired.annotated
    replayed = driver.execute(tmp_path / "interrupted", mode="replay")
    assert replayed["cases"] == live["cases"]
    assert replayed["summary"] == live["summary"]


def test_other_case_interrupt_after_feedback_before_annotation_replays_same_boundary(driver, wired, tmp_path):
    wired.behavior.update(status="audit_passed", stop=True)
    directory = tmp_path / "between-stages"
    live = driver.execute(directory, workers=1)
    assert live["cases"]["001"]["feedback"]["status"] == "audit_passed"
    assert not wired.annotated
    assert (directory / "cases/001/execution-boundary.json").exists()
    replayed = driver.execute(directory, mode="replay")
    assert replayed["cases"] == live["cases"]


def test_started_case_missing_feedback_manifest_refuses_replay(driver, wired, tmp_path):
    directory = tmp_path / "deleted-manifest"
    driver.execute(directory, workers=1)
    (directory / "cases/001/feedback/manifest.json").unlink()
    with pytest.raises(ValueError, match="replay differs"):
        driver.execute(directory, mode="replay")


def test_resume_after_between_stage_interruption_clears_old_boundary(driver, wired, tmp_path):
    directory = tmp_path / "resume-boundary"
    wired.behavior.update(status="audit_passed", stop=True)
    stopped = driver.execute(directory, workers=1)
    assert stopped["cases"]["001"]["annotation"]["status"] == "not_run"
    wired.behavior.update(stop=False)
    resumed = driver.execute(directory, workers=1)
    assert resumed["cases"]["001"]["annotation"]["status"] == "complete"
    assert read_json(directory / "cases/001/execution-boundary.json")["kind"] == "none"
    replayed = driver.execute(directory, mode="replay")
    assert replayed["cases"] == resumed["cases"]


def test_replay_no_factory_config_or_network_and_same_selection(driver, wired, tmp_path, monkeypatch):
    import skill_ir.recording as recording
    import socket
    directory = tmp_path / "replay"
    live = driver.execute(directory, workers=1)
    def reject(*args, **kwargs):
        raise AssertionError("offline dependency attempted")
    monkeypatch.setattr(recording, "streaming_factory", reject)
    monkeypatch.setattr(driver, "public_config", reject)
    monkeypatch.setattr(socket.socket, "connect", reject)
    replayed = driver.execute(directory, mode="replay")
    assert replayed["cases"] == live["cases"]
    assert replayed["summary"] == live["summary"]
    assert len(wired.clients) == 2


def test_stage_source_mismatch_blocks_annotation(driver, wired, tmp_path, monkeypatch):
    original = driver._source_binding
    def changed(feedback, annotation, case):
        case = deepcopy(case)
        case["source_inventory"]["SKILL.md"]["sha256"] = "changed"
        return original(feedback, annotation, case)
    monkeypatch.setattr(driver, "_source_binding", changed)
    result = driver.execute(tmp_path / "mismatch", workers=1)
    assert not wired.annotated
    assert result["summary"]["annotation_statuses"] == {"execution_error": 2}
    assert all("inventory" in row["scheduler_error"]["message"] for row in result["cases"].values())


def test_selection_tampering_rejected_on_replay(driver, wired, tmp_path):
    directory = tmp_path / "tampered"
    driver.execute(directory, workers=1)
    path = directory / "cases/001/selection.json"
    value = read_json(path)
    value["revision"] = 99
    ArtifactWriter(()).json(path, value)
    with pytest.raises(ValueError, match="replay differs"):
        driver.execute(directory, mode="replay")


@pytest.mark.parametrize("workers", [0, 9, True, "3"])
def test_worker_validation(driver, tmp_path, workers):
    with pytest.raises(ValueError, match="workers"):
        driver.execute(tmp_path / "invalid", workers=workers)


@pytest.mark.parametrize("version", [1, 2, 3, 4])
def test_replay_refuses_env_file_and_old_batch_identity(driver, wired, tmp_path, version):
    with pytest.raises(ValueError, match="environment"):
        driver.execute(tmp_path / "none", mode="replay", env_file=tmp_path / ".env")
    directory = tmp_path / "old"
    directory.mkdir()
    ArtifactWriter(()).json(directory / "manifest.json", {"identity": "old", "workers": 1})
    with pytest.raises(ValueError, match="Unsupported full pipeline run version"):
        driver.execute(directory, workers=1, renderer="fake")
    with pytest.raises(ValueError, match="Unsupported full pipeline run version"):
        driver.execute(directory, mode="replay")
    ArtifactWriter(()).json(directory / "manifest.json", {
        "schema_version": version, "identity": f"skill-ir-full-feedback-security-profile-review30-v{version}", "workers": 1})
    with pytest.raises(ValueError, match="Unsupported full pipeline run version"):
        driver.execute(directory, workers=1, renderer="fake")


def test_per_case_call_budget_is_enforced(driver):
    with pytest.raises(AssertionError, match="budget"):
        driver._counts({"counts": {"extraction_logical_calls": 17}}, {"status": "not_run", "counts": {}})


def test_audit_execution_retries_are_separate_from_logical_rounds_and_bounded(driver):
    counts = driver._counts({"status": "audit_passed", "counts": {
        "extraction_logical_calls": 1, "audit_logical_calls": 1,
        "audit_execution_calls": 3, "audit_execution_retries": 2}},
        {"status": "complete", "counts": {"logical_calls": 1}})
    assert counts["total_logical_calls"] == 3
    assert counts["total_execution_calls"] == 5
    with pytest.raises(AssertionError, match="budget"):
        driver._counts({"status": "audit_error", "counts": {"audit_execution_calls": 13}},
                       {"status": "not_run", "counts": {}})


def test_unknown_http_attempts_do_not_break_case_or_become_confirmed_zero(driver):
    counts = driver._counts({"status": "extraction_error", "counts": {"http_attempts": None}},
                            {"status": "not_run", "counts": {}})
    assert counts["http_attempts"] is None
    assert counts["total_logical_calls"] is None
    summary = driver._summary({"001": {"counts": counts, "feedback": {"status": "extraction_error"},
        "annotation": {"status": "not_run"}, "selection": None}})
    assert summary["unavailable_count_cases"] == ["001"]


def test_unexpected_final_case_failure_does_not_stop_other_cases(driver, wired, tmp_path, monkeypatch):
    original = driver._case
    def fails(directory, case, **kwargs):
        if case["case_id"] == "001":
            raise OSError("simulated final persistence failure")
        return original(directory, case, **kwargs)
    monkeypatch.setattr(driver, "_case", fails)
    result = driver.execute(tmp_path / "local-error", workers=1)
    assert result["cases"]["001"]["scheduler_error"]["phase"] == "scheduler"
    assert result["cases"]["001"]["counts"]["total_logical_calls"] is None
    assert result["cases"]["002"]["annotation"]["status"] == "complete"
