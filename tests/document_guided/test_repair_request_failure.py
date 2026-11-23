"""A failed delivery cannot replace a previously reviewed complete bundle."""
from copy import deepcopy
import json

import pytest

from skillflow.common.llm.request_errors import InputTooLarge, ModelRequestFailure
from skillflow.common.recording import SavedCallFailure
from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from tests.document_guided.test_parallel_runner import Harness, freeze_producer, prompt_scope


@pytest.fixture(autouse=True)
def stable_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


class RequestFailureHarness(Harness):
    def __init__(self, *args, failed_stage="revision-processing", error_type=ModelRequestFailure, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed_stage, self.error_type = failed_stage, error_type
        self.prior_selection = self.prior_review = None

    @staticmethod
    def _slot_plan(prompt, label):
        return prompt_scope(prompt)

    def complete(self, stage, prompt):
        answer = super().complete(stage, prompt)
        if stage == self.failed_stage:
            selection = self.directory / "selection.json"
            review = self.directory / "review/result.json"
            self.prior_selection = selection.read_bytes() if selection.exists() else None
            self.prior_review = review.read_bytes() if review.exists() else None
            raise self.error_type("Injected confirmed-ended request without a complete answer")
        if stage == "review":
            for finding in answer["findings"]:
                if finding["domain"] == "cfg":
                    finding["target_ids"] = ["cfg:/blocks/block_001/instructions/0/constraints"]
                if finding["domain"] == "annotation":
                    finding["target_ids"] = ["annotation:/ir_semantics/ir_001"]
        if stage == "revision-graph":
            plan = self._slot_plan(prompt, "AUTHORIZED GRAPH SLOTS")
            slot, = plan["slots"].values()
            assert slot["path"][-1] == "constraints" and slot["old_value"] == []
            return {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"],
                "value": ["Preserve the original input in this synthetic repair fixture."]}]}
        if stage == "revision-processing":
            plan = self._slot_plan(prompt, "PROCESSING REVISION SLOTS")
            return {"coverage_slots": [{"instruction_id": ir, "modeled": deepcopy(
                self.fragments["processing"]["ir_semantics"][ir])} for ir in plan["slots"]]}
        if stage == "revision-sensitivity":
            plan = self._slot_plan(prompt, "SENSITIVITY REVISION SLOTS")
            return {"slots": [{"instruction_id": ir, "declarations": slot["prior_entry_labels"]}
                              for ir, slot in plan["slots"].items()]}
        return answer


@pytest.mark.parametrize("failed_stage,calls", [
    ("revision/task", 11),
    ("revision-graph", 9), ("revision-processing", 10),
    ("revision-task-correspondence", 12), ("revision-sensitivity", 12),
])
@pytest.mark.parametrize("error_type", [ModelRequestFailure, InputTooLarge])
def test_delivery_failure_preserves_original_bundle_review_and_zero_call_replay(
        tmp_path, failed_stage, calls, error_type):
    harness = RequestFailureHarness(tmp_path / "run", domains=("task", "cfg"),
        failed_stage=failed_stage, error_type=error_type)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial", result
    assert result["selected_annotation"] == "annotation"
    assert result["repair_used"] and result["diagnostic_only"]
    assert result["annotation_review"] == result["graph_review"] == "incomplete"
    assert result["stages"][failed_stage]["status"] == "request_failure"
    assert result["stages"]["revision/review"]["status"] == "skipped"
    assert result["repair_review"]["rereview"] is None
    assert result["repair_review"]["prior_finding_count"] == 2
    assert (harness.directory / "selection.json").read_bytes() == harness.prior_selection
    assert (harness.directory / "review/result.json").read_bytes() == harness.prior_review
    selection = read(harness.directory / "selection.json")
    assert "revision" not in str(selection)
    assert (harness.directory / "audit/input-contract-review.json").is_file()
    assert (harness.directory / "propagation/data.json").is_file()
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert not (harness.directory / "revision/review").exists()
    assert not any(row["status"] == "running" for row in result["stages"].values())
    assert len(harness.calls) == result["counts"]["logical_calls"] == calls
    assert result["counts"]["structural_corrections"] == 0
    assert "revision/review" not in harness.calls
    before = {str(path.relative_to(harness.directory)): path.read_bytes()
              for path in harness.directory.rglob("call.json")}
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == calls
    assert before == {str(path.relative_to(harness.directory)): path.read_bytes()
                      for path in harness.directory.rglob("call.json")}


@pytest.mark.parametrize("error_type", [RuntimeError, KeyboardInterrupt])
@pytest.mark.parametrize("failed_stage,domains", [
    ("revision-processing", ("annotation",)), ("revision/task", ("task",)),
])
def test_unknown_process_integrity_or_user_stop_remains_terminal(tmp_path, error_type, failed_stage, domains):
    harness = RequestFailureHarness(tmp_path / "run", domains=domains,
        failed_stage=failed_stage, error_type=error_type)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == ("interrupted" if error_type is KeyboardInterrupt else "failed")
    assert not (harness.directory / "propagation").exists()
    assert not (harness.directory / "doe").exists()
    assert runner.replay(harness.directory) == result


def test_task_delivery_with_failed_recording_remains_terminal(tmp_path):
    def failed_record(message):
        error = ModelRequestFailure(message)
        error.recording_failed = True
        error.recording_errors = [{"error_type": "OSError", "error": "Injected failed persistence"}]
        return error
    harness = RequestFailureHarness(tmp_path / "run", domains=("task",),
        failed_stage="revision/task", error_type=failed_record)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed"
    assert result["stages"]["revision/task"]["status"] == "failed"
    assert not (harness.directory / "doe").exists()
    assert runner.replay(harness.directory) == result


def test_initial_request_failure_remains_terminal(tmp_path):
    harness = RequestFailureHarness(tmp_path / "run", failed_stage="processing")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["selected_annotation"] is None
    assert not (harness.directory / "doe").exists()
    assert not result["repair_used"]
    assert runner.replay(harness.directory) == result


@pytest.mark.parametrize("failed_stage", ["revision-processing", "revision/task"])
def test_repair_failure_without_original_annotation_cannot_make_a_bundle(tmp_path, failed_stage):
    harness = RequestFailureHarness(tmp_path / "run", domains=("task", "cfg"),
        annotation_failure=True, failed_stage=failed_stage)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["selected_annotation"] is None
    assert result["repair_used"]
    assert result["stages"][failed_stage]["status"] == "failed"
    assert not (harness.directory / "doe").exists()
    assert runner.replay(harness.directory) == result


def test_interruption_after_retaining_original_bundle_replays_failed_stage(tmp_path):
    harness = RequestFailureHarness(tmp_path / "run", domains=("annotation",))
    harness.prepare(tmp_path / "package")
    def stop_at_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Injected user interruption after repair delivery failure")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_at_backend)
    assert result["status"] == "interrupted"
    assert result["selected_annotation"] == "annotation"
    assert result["stages"]["revision-processing"]["status"] == "request_failure"
    assert runner.replay(harness.directory) == result


@pytest.mark.parametrize("error", [
    ValueError("unknown"), RuntimeError("unknown native state"),
    SavedCallFailure("RuntimeError", "unknown"),
    SavedCallFailure("InputTooLarge", "recording failure", record={"recording_failed": True}),
])
def test_only_confirmed_request_failures_are_eligible(error):
    assert not runner._confirmed_request_failure(error)
    typed = ModelRequestFailure("ended")
    typed.recording_failed = True
    assert not runner._confirmed_request_failure(typed)


def test_request_failure_policy_does_not_raise_budgets():
    assert runner.POLICY["normal_semantic_calls"] == 7
    assert runner.POLICY["workers"] == 2
    assert runner.POLICY["semantic_repairs"] == runner.POLICY["structural_corrections"] == 1
    assert runner.POLICY["repair_request_failure"] == "retain_original_bound_bundle_v1"
