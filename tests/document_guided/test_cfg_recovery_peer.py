"""Independent failed-rebuild frontier checks using only fresh injected fixtures."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event
import json

import pytest

from skillflow.common.llm.request_errors import ModelRequestFailure
from skillflow.common.recording import canonical_sha256, read_json
from skillflow.common.upstream import make_run_reference
from skillflow.document_guided import runner
from skillflow.document_guided.failed_stage_material import capture_failed_stage
from skillflow.document_guided.online import file_reference, seal
from tests.document_guided.test_cfg_recovery_integration import RecoveryHarness
from tests.document_guided.test_parallel_runner import freeze_producer


@pytest.fixture(autouse=True)
def producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


class FatalRecoveryHarness(RecoveryHarness):
    def __init__(self, directory, *, ordering, stopping):
        super().__init__(directory, task_finding=True)
        self.ordering, self.stopping = ordering, stopping
        self.task_observed_complete = Event()

    def complete(self, stage, prompt):
        answer = super().complete(stage, prompt)
        if stage == "revision/task":
            if self.ordering == "task_before_graph_owner":
                raise ModelRequestFailure("Injected Task request ended before graph preparation")
            if self.ordering == "graph_before_task_complete":
                assert self.stopping.wait(10), "Task sibling did not observe recorded fatal stop"
        if stage == "revision-graph":
            if self.ordering == "graph_after_task_complete":
                assert self.task_observed_complete.wait(10), "Task completion was not observed"
            raise ModelRequestFailure("Injected required graph request ended without a response")
        return answer

    def progress(self, state):
        if state["stages"].get("revision/task", {}).get("status") == "complete":
            self.task_observed_complete.set()


def run_fatal(tmp_path, monkeypatch, ordering):
    stopping = Event()
    monkeypatch.setattr(runner, "Event", lambda: stopping)
    if ordering == "task_before_graph_owner":
        class OrderedPool(ThreadPoolExecutor):
            constructed = 0
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                type(self).constructed += 1
                self.phase = type(self).constructed
            def submit(self, fn, key):
                if self.phase == 2 and key == "graph":
                    def after_primary_failure():
                        assert stopping.wait(10), "Primary Task failure did not stop the phase"
                        return fn(key)
                    return super().submit(after_primary_failure)
                return super().submit(fn, key)
        monkeypatch.setattr(runner, "ThreadPoolExecutor", OrderedPool)
    harness = FatalRecoveryHarness(tmp_path / "run", ordering=ordering, stopping=stopping)
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=harness.progress)
    assert result["status"] == "failed" and result["repair_used"], result
    assert result["selected_annotation"] is None
    assert result["stages"]["graph"]["status"] == "structural_failure"
    assert read_json(harness.directory / "audit/shared-repair-decision.json")["mode"] == "missing_cfg_slots"
    assert "fatal_frontier_error" not in result, result
    assert result.get("fatal_frontier")
    assert not (harness.directory / "selection.json").exists()
    assert not (harness.directory / "propagation").exists() and not (harness.directory / "doe").exists()
    if ordering == "task_before_graph_owner":
        assert result["stage"] == "revision/task"
        assert not (harness.directory / "steps/revision-graph/manifest.json").exists()
        assert "revision-graph" not in harness.calls
    else:
        assert result["stage"] == "revision-graph"
    monkeypatch.setattr(runner, "Event", Event)
    monkeypatch.setattr(runner, "ThreadPoolExecutor", ThreadPoolExecutor)
    return harness, result


@pytest.mark.parametrize("ordering", ["task_before_graph_owner", "graph_after_task_complete", "graph_before_task_complete"])
def test_missing_cfg_request_failure_preserves_actual_frontier_and_zero_call_replay(tmp_path, monkeypatch, ordering):
    harness, result = run_fatal(tmp_path, monkeypatch, ordering)
    before = {p.relative_to(harness.directory).as_posix(): p.read_bytes()
              for p in harness.directory.rglob("*.json")}
    calls = len(harness.calls)
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == calls
    assert before == {p.relative_to(harness.directory).as_posix(): p.read_bytes()
                      for p in harness.directory.rglob("*.json")}


@pytest.mark.parametrize("artifact", ["audit/failed-stages/graph.json", "audit/shared-repair-decision.json"])
@pytest.mark.parametrize("change", ["missing", "changed"])
def test_fatal_recovery_without_graph_owner_still_binds_admission_and_failed_material(
        tmp_path, monkeypatch, artifact, change):
    harness, _ = run_fatal(tmp_path, monkeypatch, "task_before_graph_owner")
    path = harness.directory / artifact
    if change == "missing":
        path.unlink()
    else:
        value = read_json(path)
        value["peer_tamper"] = "must not escape fatal-frontier verification"
        path.write_text(json.dumps(value), encoding="utf-8")
    before = len(harness.calls)
    with pytest.raises((ValueError, FileNotFoundError)):
        runner.replay(harness.directory)
    assert len(harness.calls) == before


@pytest.mark.parametrize("artifact", ["response.json", "merged-candidate.json", "validation.json", "request.json", "transport.json"])
def test_failed_material_capture_requires_all_original_call_evidence(tmp_path, monkeypatch, artifact):
    harness, _ = run_fatal(tmp_path, monkeypatch, "task_before_graph_owner")
    material = read_json(harness.directory / "review/inputs.json")
    failure = material["stage_failures"]["graph"]
    path = harness.directory / "steps/graph/calls/a002" / artifact
    assert path.is_file()
    if artifact == "transport.json":
        path.unlink()
    else:
        value = read_json(path)
        value["peer_tamper"] = "does not belong to the rejected request"
        path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError)):
        capture_failed_stage(harness.directory, stage="graph", attempt="graph",
                             files=material["files"], failure=failure)


@pytest.mark.parametrize("change", ["source_files", "source_owner", "stage_kind", "dependency_owner", "call_order", "rehashed_transport"])
def test_capture_rejects_wrong_owner_source_call_and_detached_completed_transport(tmp_path, monkeypatch, change):
    harness, _ = run_fatal(tmp_path, monkeypatch, "task_before_graph_owner")
    run = harness.directory
    review = read_json(run / "review/inputs.json")
    files, failure = deepcopy(review["files"]), review["stage_failures"]["graph"]
    owner = run / "steps/graph"
    if change == "source_files":
        files["skill/SKILL.md"] += "different source"
    elif change in {"source_owner", "stage_kind", "dependency_owner"}:
        manifest = read_json(owner / "manifest.json")
        if change == "source_owner":
            other = RecoveryHarness(tmp_path / "other-run")
            other.prepare(tmp_path / "other-source")
            manifest["context"]["source_owner"] = make_run_reference(owner, other.directory / "source")
        elif change == "stage_kind":
            manifest["kind"] = "processing_fragment"
        else:
            manifest["dependencies"][1] = file_reference(owner, run / "task/task.json")
        manifest.pop("manifest_sha256")
        (owner / "manifest.json").write_text(json.dumps(seal(manifest)), encoding="utf-8")
    elif change == "call_order":
        chain = read_json(owner / "calls/chain.json")
        chain["attempts"][-1]["call"] = "calls/a001"
        (owner / "calls/chain.json").write_text(json.dumps(chain), encoding="utf-8")
        outcome = read_json(owner / "result.json")
        outcome["response_chain_sha256"] = canonical_sha256(chain)
        (owner / "result.json").write_text(json.dumps(outcome), encoding="utf-8")
    else:
        path = owner / "calls/a002/transport.json"
        trace = read_json(path)
        trace[0]["response"] = {"different": "completed response"}
        trace[0].pop("record_sha256")
        trace[0]["record_sha256"] = canonical_sha256(trace[0])
        path.write_text(json.dumps(trace), encoding="utf-8")
    with pytest.raises(ValueError):
        capture_failed_stage(run, stage="graph", attempt="graph", files=files, failure=failure)
