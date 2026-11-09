"""Partial review repairs concrete upstream defects, without resampling gaps.

Injected findings exercise routing; they are not independent semantic gold.
All completions are supplied by the existing offline fragment Harness.
"""
from copy import deepcopy
import json

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.propagation.annotation.loading import load_annotation_run
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


@pytest.fixture(autouse=True)
def offline_producer_and_certificate(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def malformed(harness, stage, prompt, response):
    """Record deliberately malformed fragments, including their one correction."""
    with harness.lock:
        harness.attempts[stage] = harness.attempts.get(stage, 0) + 1
        harness.calls.append(stage)
        harness.prompts[stage] = prompt
    return deepcopy(response)


class InitiallyBlocked(Harness):
    def complete(self, stage, prompt):
        if stage == "task-correspondence":
            # No identifiable realization record can be salvaged. The legal
            # partial review still sees the available source, Task and CFG.
            return malformed(self, stage, prompt, {"realizations": "invalid"})
        answer = super().complete(stage, prompt)
        if stage == "graph" and "cfg" in self.domains:
            answer["blocks"][0]["instructions"][0]["opcode"] = "store_label"
        if stage == "review" and "cfg" in self.domains:
            for finding in answer["findings"]:
                if finding["domain"] == "cfg":
                    finding["explanation"] = "The source displays the label, but the CFG describes storing it."
                    finding["suggestion"] = "Restore the source-supported display action and rebuild its dependents."
        return answer


def stop_before_backend(state):
    if state["stage"] == "propagation":
        raise KeyboardInterrupt("Inspect the repaired bundle before the independently checked backend")


@pytest.mark.parametrize("domain,count,closure", [
    ("cfg", 13, {"revision-graph", "revision-processing", "revision-task-correspondence",
                  "revision-sensitivity", "revision/review"}),
    ("task", 11, {"revision/task", "revision-task-correspondence", "revision/review"}),
])
def test_partial_review_upstream_finding_uses_one_real_dependency_repair(tmp_path, domain, count, closure):
    harness = InitiallyBlocked(tmp_path / "run", domains=(domain,))
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
    assert result["repair_used"], result
    assert result["status"] == "interrupted" and result["stage"] == "propagation", result
    assert result["selected_annotation"] == "revision/annotation"
    assert result["annotation_review"] == "review_passed"
    assert len(harness.calls) == result["counts"]["logical_calls"] == count
    assert {stage for stage in harness.calls if stage.startswith("revision")} == closure
    assert harness.calls.count("task-correspondence") == 2
    assert harness.calls.count("revision-task-correspondence") == 1
    assert "annotation" not in harness.calls and "revision-annotation" not in harness.calls
    assert not (harness.directory / "annotation/manifest.json").exists()
    first_review = read(harness.directory / "review/inputs.json")
    assert first_review["annotation"] is None and not first_review["availability"]["annotation"]
    assert first_review["stage_failures"]["task-correspondence"]["status"] == "structural_failure"
    selection = read(harness.directory / "selection.json")
    assert selection["annotation"]["path"] == "revision/annotation/manifest.json"
    assert selection["task"]["path"] == ("revision/task/task.json" if domain == "task" else "task/task.json")
    assert selection["cfg"]["path"] == ("graph/revision.json" if domain == "cfg" else "graph/initial.json")
    accepted = load_annotation_run(harness.directory / "revision/annotation")
    assert accepted["material"]["cfg"] == read(harness.directory / "graph/selected.json")["cfg"]
    assert accepted["raw_annotation"]["task_revision_id"] == accepted["task"]["task_sha256"]
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == count
    assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts.get("revision/task", "")
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["revision-task-correspondence"]


def test_fragment_shape_failure_with_empty_partial_review_does_not_resample(tmp_path):
    harness = InitiallyBlocked(tmp_path / "run")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and not result["repair_used"], result
    assert len(harness.calls) == result["counts"]["logical_calls"] == 8
    assert result["counts"]["structural_corrections"] == 1
    assert not any(stage.startswith("revision") for stage in harness.calls)
    assert result["selected_annotation"] is None
    assert not (harness.directory / "annotation/manifest.json").exists()
    assert not (harness.directory / "propagation").exists()
    assert runner.replay(harness.directory) == result


def test_known_processing_gap_with_empty_findings_has_seven_calls_and_no_quality_retry(tmp_path):
    from tests.document_guided.test_parallel_recovery import prepared_harness
    harness = prepared_harness(tmp_path, processing_gap=True)
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "partial" and result["diagnostic_only"], result
    assert not result["repair_used"]
    assert len(harness.calls) == result["counts"]["logical_calls"] == 7
    assert result["counts"]["structural_corrections"] == 0
    assert not any(stage.startswith("revision") for stage in harness.calls)
    material = read(harness.directory / "review/inputs.json")
    assert material["processing_gaps"] and material["partial"]
    assert read(harness.directory / "review/result.json")["review"]["findings"] == []
    assert runner.replay(harness.directory) == result


def test_task_repair_does_not_retry_an_unchanged_failed_sensitivity_fragment(tmp_path):
    class FailedIndependentFragment(Harness):
        def complete(self, stage, prompt):
            if stage == "sensitivity":
                return malformed(self, stage, prompt, {"declarations": "invalid"})
            return super().complete(stage, prompt)
    harness = FailedIndependentFragment(tmp_path / "run", domains=("task",))
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["repair_used"], result
    assert result["status"] == "failed" and result["selected_annotation"] is None, result
    assert harness.calls.count("sensitivity") == 2
    assert "revision-sensitivity" not in harness.calls
    assert "annotation" not in harness.calls and "revision-annotation" not in harness.calls
    assert {stage for stage in harness.calls if stage.startswith("revision")} == {
        "revision/task", "revision-task-correspondence", "revision/review"}
    assert len(harness.calls) == result["counts"]["logical_calls"] == 11
    revised_review = read(harness.directory / "revision/review/inputs.json")
    assert revised_review["annotation"] is None
    assert revised_review["stage_failures"]["sensitivity"]["status"] == "structural_failure"
    assert not (harness.directory / "annotation/manifest.json").exists()
    assert not (harness.directory / "revision/annotation/manifest.json").exists()
    assert runner.replay(harness.directory) == result


def test_source_supported_missing_sensitivity_finding_repairs_only_failed_owner(tmp_path):
    class MissingSensitivity(Harness):
        def complete(self, stage, prompt):
            if stage == "sensitivity":
                return malformed(self, stage, prompt, {"declarations": "invalid"})
            answer = super().complete(stage, prompt)
            if stage == "review":
                answer["findings"] = [{"domain": "annotation", "target_ids": ["stage:sensitivity"],
                    "explanation": "The source explicitly identifies the original label as sensitive location information, but its declaration is absent from the available analysis.",
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}],
                    "suggestion": "Declare the existing local label using its original sensitivity statement."}]
            return answer
    harness = MissingSensitivity(tmp_path / "run")
    harness.example["source"] = harness.example["source"].rstrip() + (
        "\nThe original label is sensitive location information.")
    identity = next(iter(harness.fragments["processing"]["ir_semantics"]))
    harness.fragments["sensitivity"]["declarations"] = [{"instruction_id": identity,
        "value": {"kind": "local", "name": "label"}, "label": "location information",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}]}]
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
    assert result["status"] == "interrupted" and result["repair_used"], result
    assert result["selected_annotation"] == "revision/annotation"
    assert len(harness.calls) == result["counts"]["logical_calls"] == 10
    assert harness.calls.count("sensitivity") == 2
    assert {stage for stage in harness.calls if stage.startswith("revision")} == {
        "revision-sensitivity", "revision/review"}
    assert not (harness.directory / "annotation/manifest.json").exists()
    material = read(harness.directory / "review/inputs.json")
    assert material["annotation"] is None and not material["availability"]["annotation"]
    assert set(material["fragments"]) == {"processing", "task-correspondence"}
    assert material["fragments"]["processing"] == harness.fragments["processing"]
    initial = read(harness.directory / "review/result.json")
    assert initial["review"]["findings"][0]["owner"] == "sensitivity"
    revised = read(harness.directory / "revision/review/inputs.json")
    assert revised["annotation"] is not None and revised["fragments"] == {}
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 10


@pytest.mark.parametrize("owner,count,closure", [
    ("sensitivity", 9, {"revision-sensitivity", "revision/review"}),
    ("task-correspondence", 9, {"revision-task-correspondence", "revision/review"}),
    ("processing", 11, {"revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"}),
])
def test_annotation_owner_repairs_only_its_dependency_closure(tmp_path, owner, count, closure):
    class OwnedFinding(Harness):
        def complete(self, stage, prompt):
            answer = super().complete(stage, prompt)
            if stage == "review":
                if owner == "sensitivity":
                    declaration = self.fragments["sensitivity"]["declarations"][0]
                    pointer = "/ir_semantics/" + declaration["instruction_id"] + "/sensitivity/0"
                else:
                    pointer = "/realizations/0" if owner == "task-correspondence" else ""
                answer["findings"] = [{"domain": "annotation", "target_ids": ["annotation:" + pointer],
                    "explanation": "OWNER_SPECIFIC_REVIEW_CANARY: injected isolated routing exercise.",
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
                    "suggestion": "Correct the source-supported declaration in its actual owner."}]
            return answer
    harness = OwnedFinding(tmp_path / "run")
    if owner == "sensitivity":
        from tests.document_guided.test_parallel_recovery import add_synthetic_sensitivity
        add_synthetic_sensitivity(harness, "Synthetic label sensitivity for routing")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
    assert result["status"] == "interrupted" and result["repair_used"], result
    assert result["selected_annotation"] == "revision/annotation"
    assert len(harness.calls) == result["counts"]["logical_calls"] == count
    assert {stage for stage in harness.calls if stage.startswith("revision")} == closure
    initial_review = read(harness.directory / "review/result.json")["review"]
    assert initial_review["findings"][0]["owner"] == owner
    for stage in closure - {"revision/review"}:
        prompt = harness.prompts[stage]
        assert "OWNER_SPECIFIC_REVIEW_CANARY" not in prompt
        context = json.loads(prompt.split("SOURCE REVIEW REPAIR\n", 1)[1].split(
            "\n\nGLOBAL REQUIREMENTS AND LIMITATIONS", 1)[0])
        assert bool(context["source_rechecks"]) == (stage == "revision-" + owner)
        for recheck in context["source_rechecks"]:
            assert set(recheck) == {"target_ids", "source_refs"}
    assert "OWNER_SPECIFIC_REVIEW_CANARY" not in harness.prompts["revision/review"]
    assert runner.replay(harness.directory) == result
