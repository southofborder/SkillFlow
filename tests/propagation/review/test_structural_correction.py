"""Mechanical corrections never consume the one semantic replacement."""
import json
from threading import Event

import pytest

from skillflow.common.recording import read_json
from skillflow.common.structural_correction import CORRECTION_MARKER, ResponseChain
from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.review import runner, services, refinement
from tests.propagation.review.test_runner import prepared, ReviewClient, response_for, forbidden
from tests.propagation.review.test_refinement import prepared as prepared_refinement, SequenceReview, Repair


def test_repeated_structural_error_exceeds_previous_budget_then_replays(tmp_path, monkeypatch):
    directory, _, _ = prepared(tmp_path)
    count = 0
    def candidate(response, material):
        nonlocal count
        count += 1
        if count <= 5:
            response["reviewed_ir_ids"].pop()
        return response
    client = ReviewClient(candidate)
    result = runner.run_review(directory, client=client)
    assert result["status"] == "complete", result
    assert result["counts"]["logical_calls"] == 6
    assert result["counts"]["stage_calls"] == 1
    assert result["counts"]["structural_corrections"] == 5
    assert result["response_chain"]["accepted_call"] == "calls/review/a006"
    assert all(prompt.count(CORRECTION_MARKER) == 1 for prompt in client.prompts[1:])
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    assert runner.replay_run(directory) == result
    assert runner.load_review_run(directory)["result"] == result


def test_all_review_and_repair_responses_correct_without_extra_semantic_round(tmp_path):
    directory, _, raw = prepared_refinement(tmp_path)
    review = SequenceReview(["bad", "bad", "issue", "bad", "bad", "issue"])
    repair = Repair(raw, mode="bad")
    result = refinement.run_refinement(directory, review_client=review, repair_client=repair)
    assert result["status"] == "repair_limit", result
    assert result["counts"]["logical_calls"] == 8
    assert result["counts"]["stage_calls"] == 3
    assert result["counts"]["structural_corrections"] == 5
    assert result["selected"] == "repair"
    assert len(repair.prompts) == 2
    assert refinement.replay_refinement(directory) == result


@pytest.mark.parametrize("name", ["request.json", "validation.json", "response.json"])
def test_prior_invalid_attempt_remains_bound_after_final_acceptance(tmp_path, name):
    directory, _, _ = prepared(tmp_path)
    first = True
    def candidate(response, material):
        nonlocal first
        if first:
            first = False
            return "invalid"
        return response
    result = runner.run_review(directory, client=ReviewClient(candidate))
    assert result["status"] == "complete", result
    path = directory / "calls/review/a001" / name
    value = read_json(path)
    value = {**value, "tampered": True} if isinstance(value, dict) else "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        runner.load_review_run(directory)


def test_interruption_after_diagnostic_does_not_repeat_first_request(tmp_path, monkeypatch):
    directory, _, _ = prepared(tmp_path)
    stop = Event()
    original = ResponseChain._validation
    def after_validation(self, call_dir, row, status, **extra):
        outcome = original(self, call_dir, row, status, **extra)
        if status == "structural_invalid":
            stop.set()
        return outcome
    monkeypatch.setattr(ResponseChain, "_validation", after_validation)
    bad = ReviewClient(lambda response, material: "invalid")
    result = runner.run_review(directory, client=bad, stop_event=stop)
    assert result["status"] == "interrupted", result
    assert len(bad.prompts) == 1
    assert runner.replay_run(directory) == result
    monkeypatch.setattr(ResponseChain, "_validation", original)
    stop.clear()
    good = ReviewClient()
    resumed = runner.run_review(directory, client=good, stop_event=stop)
    assert resumed["status"] == "complete", resumed
    assert len(good.prompts) == 1
    assert resumed["counts"]["logical_calls"] == 2


def test_unexpected_validator_error_stops_without_model_correction(tmp_path, monkeypatch):
    directory, _, _ = prepared(tmp_path)
    def broken(*args, **kwargs):
        raise RuntimeError("implementation fault")
    monkeypatch.setattr(runner, "validate_response", broken)
    client = ReviewClient()
    result = runner.run_review(directory, client=client)
    assert result["status"] == "execution_error"
    assert len(client.prompts) == 1
    assert result["counts"]["structural_corrections"] == 0


def test_typed_review_diagnostics_aggregate_independent_reference_errors():
    from tests.propagation.review.test_core import fixture
    from skillflow.propagation.review.material import prepare_review_material
    material = prepare_review_material(*fixture())
    response = response_for(material, finding=True)
    response["reviewed_ir_ids"].pop()
    response["findings"][0]["target_ids"] = ["missing"]
    response["findings"][0]["evidences"] = [{"rule_id": "absent", "reason": "source"}]
    with pytest.raises(StructuralValidationError) as captured:
        services.validate_response(response, material)
    assert {row["code"] for row in captured.value.diagnostics} == {
        "review_coverage", "review_target", "evidence_rule"}
    assert next(row for row in captured.value.diagnostics if row["code"] == "evidence_rule")["path"] == (
        "/findings/0/evidences/0/rule_id")


@pytest.mark.parametrize("domain", ["task", "annotation"])
@pytest.mark.parametrize("known_kind", [None, "task", "annotation"])
def test_domain_compatibility_waits_for_all_target_references(domain, known_kind):
    from tests.propagation.review.test_four_axes import goal_material, task_issue
    material = goal_material()
    response = task_issue(material)
    finding = response["findings"][0]
    if domain == "annotation":
        finding.update(domain="annotation", task_objection=None)
    finding["target_ids"] = ["missing"]
    if known_kind is not None:
        finding["target_ids"].append(next(row["id"] for row in material["target_index"]
                                           if row["kind"] == known_kind))
    with pytest.raises(StructuralValidationError) as captured:
        services.validate_response(response, material)
    assert [(row["code"], row["path"]) for row in captured.value.diagnostics] == [
        ("review_target", "/findings/0/target_ids/0")]


@pytest.mark.parametrize("domain,wrong_kind,code", [
    ("task", "annotation", "task_finding_target"),
    ("annotation", "task", "annotation_finding_target"),
])
def test_known_targets_still_enforce_finding_domain(domain, wrong_kind, code):
    from tests.propagation.review.test_four_axes import goal_material, task_issue
    material = goal_material()
    response = task_issue(material)
    finding = response["findings"][0]
    if domain == "annotation":
        finding.update(domain="annotation", task_objection=None)
    finding["target_ids"] = [next(row["id"] for row in material["target_index"] if row["kind"] == wrong_kind)]
    with pytest.raises(StructuralValidationError) as captured:
        services.validate_response(response, material)
    assert [(row["code"], row["path"]) for row in captured.value.diagnostics] == [
        (code, "/findings/0/target_ids")]


def test_unknown_target_does_not_hide_independent_task_objection_errors():
    from tests.propagation.review.test_four_axes import goal_material, task_issue
    material = goal_material()
    response = task_issue(material)
    finding = response["findings"][0]
    finding["target_ids"] = ["missing"]
    finding["task_objection"]["requirement_ids"] = ["unknown_requirement"]
    finding["task_objection"]["source_spans"][0]["file"] = "skill/absent.txt"
    with pytest.raises(StructuralValidationError) as captured:
        services.validate_response(response, material)
    assert {row["code"] for row in captured.value.diagnostics} == {
        "review_target", "task_objection_requirement", "task_objection_source"}


def test_failure_branch_is_corrected_only_until_its_references_are_valid():
    from skillflow.common.semantic_failure import SemanticFailure
    from tests.propagation.review.test_core import fixture, cannot_assess
    from tests.propagation.review.test_runner import material_from_prompt
    class Failure:
        calls = 0
        def complete(self, prompt):
            self.calls += 1
            material = material_from_prompt(prompt)
            response = cannot_assess(material)
            if self.calls == 1:
                response["failure"]["target_ids"] = ["not_a_target"]
            return response
    client = Failure()
    with pytest.raises(SemanticFailure):
        services.review_annotation(*fixture(), client=client)
    assert client.calls == 2


@pytest.mark.parametrize("prior_invalid", [False, True])
def test_local_provider_failure_replays_prepared_chain_and_rejects_tampering(tmp_path, monkeypatch, prior_invalid):
    directory, _, _ = prepared(tmp_path)
    if prior_invalid:
        stop = Event()
        original = ResponseChain._validation
        def after_validation(self, call_dir, row, status, **extra):
            outcome = original(self, call_dir, row, status, **extra)
            if status == "structural_invalid":
                stop.set()
            return outcome
        monkeypatch.setattr(ResponseChain, "_validation", after_validation)
        prior = runner.run_review(directory, client=ReviewClient(lambda response, material: "invalid"), stop_event=stop)
        assert prior["status"] == "interrupted"
        monkeypatch.setattr(ResponseChain, "_validation", original)
    def unavailable(*args, **kwargs):
        raise ValueError("credential configuration unavailable")
    monkeypatch.setattr(runner, "streaming_factory", unavailable)
    result = runner.run_review(directory)
    assert result["status"] == "execution_error", result
    assert result["counts"]["logical_calls"] == int(prior_invalid)
    assert result["response_chain"]["attempts"][-1]["status"] == "pending"
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.replay_run(directory) == result
    assert runner.load_review_run(directory)["result"] == result
    path = directory / ("calls/review/a002/request.json" if prior_invalid else "calls/review/a001/request.json")
    value = read_json(path)
    value["prompt_sha256"] = "0" * 64
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        runner.load_review_run(directory)
