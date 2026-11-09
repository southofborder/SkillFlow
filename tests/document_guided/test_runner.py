"""Small full-chain checks with injected responses and the real analysis backend."""
from copy import deepcopy

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.propagation.annotation.binding_examples import sink_demand_examples
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.task.runner import load_task_run


def _fixture():
    """Use an existing independent example, preserving its complete relationships."""
    example = deepcopy(sink_demand_examples()[0])
    block = example["cfg"]["blocks"]["sample"]
    candidate = {"entry_block_ref": "sample", "blocks": [{
        "block_ref": "sample", "block_name": block["block_name"],
        "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
        "instructions": [{"instruction_ref": ir["id"],
                           **{key: value for key, value in ir.items() if key != "id"}}
                          for ir in block["instructions"]]}], "edges": []}
    compiled = compile_candidate(candidate)
    assert compiled.ok
    example["annotation"]["ir_semantics"] = {
        current.id: example["annotation"]["ir_semantics"][original["id"]]
        for original, current in zip(block["instructions"], compiled.cfg.blocks["block_001"].instructions)
    }
    return example, candidate


@pytest.fixture(autouse=True)
def stable_offline_producer(monkeypatch):
    from tests.document_guided.test_parallel_runner import freeze_producer
    freeze_producer(monkeypatch)


@pytest.mark.parametrize("review_status", ["completed", "structural_failure"])
def test_program_assembly_diagnostic_continuation_and_zero_call_replay(tmp_path, monkeypatch, review_status):
    from tests.document_guided.test_parallel_runner import Harness
    class ReviewedHarness(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "review" and review_status == "structural_failure":
                return {"outcome": "completed"}  # Missing required findings, twice.
            return answer
    harness = ReviewedHarness(tmp_path / "run", final_failure=review_status == "structural_failure")
    harness.prepare(tmp_path / "package")
    if review_status == "structural_failure":
        monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == ("complete" if review_status == "completed" else "partial"), result
    assert result["diagnostic_only"] == (review_status == "structural_failure")
    count = 7 if review_status == "completed" else 8
    assert result["counts"]["logical_calls"] == len(harness.calls) == count
    assert "annotation" not in harness.calls
    assert result["counts"]["structural_corrections"] == (review_status == "structural_failure")
    assert not result["repair_used"]
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert (harness.directory / "propagation/data.json").is_file()
    if review_status == "completed":
        certificate = read(harness.directory / "graph/initial/controlled.json")["certificate"]
        assert certificate["status"] == "verified"
        assert certificate["checks"]["actual_text_parsed"]
    saved = {str(path.relative_to(harness.directory)): path.read_bytes()
             for path in harness.directory.rglob("response.json")}
    def forbidden(*args, **kwargs):
        raise AssertionError("Accepted answers and replay must not create a model client")
    assert runner.run(harness.directory, client_factory=forbidden) == result
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == count
    assert saved == {str(path.relative_to(harness.directory)): path.read_bytes()
                     for path in harness.directory.rglob("response.json")}


def _check_repair_route(tmp_path, repair_domain, monkeypatch):
    from tests.document_guided.test_parallel_runner import Harness
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = Harness(tmp_path / "run", domains=(repair_domain,))
    harness.prepare(tmp_path / "package")
    def stop_before_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Focused routing test stops before the independently checked backend")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
    assert result["status"] == "interrupted", result
    assert result["stage"] == "propagation" and result["repair_used"]
    assert result["selected_annotation"] == "revision/annotation"
    assert result["annotation_review"] == "review_passed"
    assert len(harness.calls) == result["counts"]["logical_calls"] == (10 if repair_domain == "task" else 11)
    assert result["counts"]["structural_corrections"] == 0
    for name in ("processing", "sensitivity"):
        assert harness.calls.count(name) == 1
        assert ("revision-" + name in harness.calls) == (repair_domain == "annotation")
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["task-correspondence"]
    if repair_domain == "task":
        assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision/task"]
        assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["revision/task"]
        assert "station-west" not in harness.prompts["revision/task"]
        assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision-task-correspondence"]
        assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["revision-task-correspondence"]
        old = load_task_run(harness.directory / "task")["task"]
        new = load_task_run(harness.directory / "revision/task")["task"]
        assert old["task_sha256"] != new["task_sha256"]
        assert load_annotation_run(harness.directory / "revision/annotation")["task"] == new
    else:
        assert "revision-task-correspondence" in harness.calls
        assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision-processing"]
        assert '"source_rechecks"' in harness.prompts["revision-processing"]
    assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision/review"]


def test_processing_repair_rebuilds_only_downstream_fragments_and_rereview_isolated(tmp_path, monkeypatch):
    _check_repair_route(tmp_path, "annotation", monkeypatch)


def test_task_revision_reuses_processing_sensitivity_and_keeps_source_only_revision(tmp_path, monkeypatch):
    _check_repair_route(tmp_path, "task", monkeypatch)


@pytest.mark.parametrize("error_name", ["InputTooLarge", "ModelRequestFailure"])
def test_recorded_review_request_failure_keeps_compiled_doe_and_replays(tmp_path, monkeypatch, error_name):
    from skillflow.common.llm import request_errors
    from tests.document_guided.test_parallel_runner import Harness
    error_type = getattr(request_errors, error_name)

    class RequestFailureHarness(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "review":
                raise error_type("Injected confirmed request failure without a complete answer")
            return answer

    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = RequestFailureHarness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial", result
    assert result["diagnostic_only"] and result["annotation_review"] == "incomplete"
    assert result["graph_review"] == "incomplete" and not result["repair_used"]
    assert any(error_name in text and "remains unreviewed" in text for text in result["limitations"])
    assert result["selected_annotation"] == "annotation"
    assert result["stages"]["review"]["status"] == "request_failure"
    assert not any(row["status"] == "running" for row in result["stages"].values())
    assert (harness.directory / "propagation/data.json").is_file()
    assert (harness.directory / "doe/doe-result.json").is_file()
    reviewed = read(harness.directory / "review/result.json")
    assert reviewed["review"] is None and reviewed["diagnostic_only"]
    assert read(harness.directory / "review/execution-boundary.json")["kind"] == "finished"
    assert len(harness.calls) == result["counts"]["logical_calls"] == 7
    manifest = read(harness.directory / "manifest.json")
    assert manifest["identity"] == "skillflow-document-guided-run-v9"
    assert manifest["policy"]["review_protocol"] == "compact-v1"
    assert manifest["policy"]["review_request_failure"] == "diagnostic_continue"
    assert read(harness.directory / "review/inputs.json")["prompt_view"] == "compact-v1"
    assert (harness.directory / "report.md").read_text(encoding="utf-8").startswith("# Document-guided analysis")
    saved_calls = {str(path.relative_to(harness.directory)): path.read_bytes()
                   for path in harness.directory.rglob("call.json")}
    assert runner.replay(harness.directory) == result
    assert runner.run(harness.directory, client_factory=lambda *args: pytest.fail("Replay created a client")) == result
    assert len(harness.calls) == 7
    assert saved_calls == {str(path.relative_to(harness.directory)): path.read_bytes()
                           for path in harness.directory.rglob("call.json")}


def test_review_request_failure_cannot_fabricate_missing_annotation(tmp_path, monkeypatch):
    from skillflow.common.llm.request_errors import ModelRequestFailure
    from tests.document_guided.test_parallel_runner import Harness

    class MissingAnnotationHarness(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "review":
                raise ModelRequestFailure("Injected ended request without an answer")
            return answer

    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = MissingAnnotationHarness(tmp_path / "run", annotation_failure=True)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["selected_annotation"] is None
    assert result["stages"]["review"]["status"] == "request_failure"
    assert result["diagnostic_only"] and not result["repair_used"]
    assert not (harness.directory / "propagation").exists()
    assert not (harness.directory / "doe").exists()
    count = len(harness.calls)
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == count


def test_failed_rereview_keeps_one_repair_and_prior_issues_unconfirmed(tmp_path, monkeypatch):
    from skillflow.common.llm.request_errors import ModelRequestFailure
    from tests.document_guided.test_parallel_runner import Harness

    class RereviewFailureHarness(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "revision/review":
                raise ModelRequestFailure("Injected re-review request failure")
            return answer

    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = RereviewFailureHarness(tmp_path / "run", domains=("task",))
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial", result
    assert result["diagnostic_only"] and result["repair_used"]
    assert result["selected_annotation"] == "revision/annotation"
    assert result["annotation_review"] == "incomplete"
    assert result["repair_review"] == {"status": "unconfirmed", "prior_review": "review/result.json",
        "rereview": "revision/review/result.json", "prior_finding_count": 1}
    assert any("not marked resolved" in text for text in result["limitations"])
    assert len(read(harness.directory / "review/result.json")["review"]["findings"]) == 1
    assert read(harness.directory / "revision/review/result.json")["review"] is None
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert harness.calls.count("revision/task") == 1
    assert harness.calls.count("revision/review") == 1
    assert len(harness.calls) == result["counts"]["logical_calls"] == 10
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 10


@pytest.mark.parametrize("error_type", [KeyboardInterrupt, RuntimeError])
def test_review_stop_and_integrity_errors_are_terminal_with_original_replay_identity(tmp_path, monkeypatch, error_type):
    from tests.document_guided.test_parallel_runner import Harness

    class StoppedHarness(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "review":
                raise error_type("Injected review stop, not a delivery failure")
            return answer

    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    harness = StoppedHarness(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    interrupted = error_type is KeyboardInterrupt
    assert result["status"] == ("interrupted" if interrupted else "failed")
    assert result["stages"]["review"]["status"] == ("interrupted" if interrupted else "failed")
    assert not any(row["status"] == "running" for row in result["stages"].values())
    assert not (harness.directory / "propagation").exists()
    assert not (harness.directory / "doe").exists()
    if not interrupted:
        assert result["reason"] == "RuntimeError: Injected review stop, not a delivery failure"
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7
