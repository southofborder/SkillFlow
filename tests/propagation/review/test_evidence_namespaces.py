"""Candidate targets and CFG citations stay distinct, with auditable correction.

These fixtures exercise mechanical reference validity, not semantic support.
"""
from copy import deepcopy
import json
from threading import Event

import pytest

from skillflow.common.recording import read_json
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import ResponseChain, correction_prompt
from skillflow.common.validation import StructuralValidationError, diagnostic_materials
from skillflow.propagation.contracts.references import CFG_TARGET, cfg_instructions
from skillflow.propagation.review import runner, services
from skillflow.propagation.review.material import prepare_review_material
from tests.propagation.review.test_core import fixture, cannot_assess
from tests.propagation.review.test_runner import ReviewClient, response_for, forbidden


def prepared_material(*, metadata_events=False):
    material, raw = fixture()
    if metadata_events:
        cfg_instructions(material["cfg"])["ir_read"]["metadata"]["events"] = ["a real CFG metadata value"]
    return prepare_review_material(material, raw)


def response_with_targets(material, targets):
    response = response_for(material, finding=True)
    response["findings"][0]["evidences"] = [
        {"target": deepcopy(target), "reason": "This fixture checks reference resolution only."}
        for target in targets]
    return response


def errors(response, material):
    with pytest.raises(StructuralValidationError) as caught:
        services.validate_response(response, material)
    return caught.value.diagnostics


def correction_context(response, diagnostics):
    prompt = correction_prompt("Frozen source and current review format.", response, diagnostics)
    return json.loads(prompt.split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])


@pytest.mark.parametrize("target", [
    {"instruction_id": "ir_read", "path": ["events", 0, "atomic_ops", 0]},
    {"instruction_id": "absent_instruction", "path": []},
    {"instruction_id": "ir_read", "side": "input", "index": 100},
    {"instruction_id": "ir_read", "path": ["metadata", "nested", "0"]},
])
def test_cfg_resolution_failures_keep_typed_child_path_and_current_target(target):
    material = prepared_material()
    response = response_with_targets(material, [target])
    original = deepcopy(response)
    rows = errors(response, material)
    assert len(rows) == 1
    row = rows[0]
    assert (row["code"], row["path"]) == ("evidence_target", "/findings/0/evidences/0/target")
    assert row["context"]["current"] == target
    schema = CFG_TARGET.json_schema()
    expected = [{key: value for key, value in schema["$defs"][alternative["$ref"].rsplit("/", 1)[-1]].items()
                 if key not in {"title", "description"}} for alternative in schema["anyOf"]]
    assert row["context"]["allowed_forms"] == expected
    assert len(expected) == 4
    assert "resolves only against the supplied cfg" in row["context"]["format_example"]
    assert "sealed Task, candidate annotations or compiled observations" in row["context"]["format_example"]
    assert response == original
    materials = diagnostic_materials(rows)
    assert materials["raw_diagnostics"] == [{
        "code": "evidence_target", "path": "/findings/0/evidences/0/target", "message": row["message"]}]
    assert materials["diagnostic_mapping"] == [{"raw_index": 0, "diagnostic_index": 0,
                                                "candidate_path": row["path"]}]
    shown = correction_context(response, rows)
    assert shown["protocol"] == "skillflow-structural-correction-v5"
    assert shown["candidate"] == original
    assert len(shown["format_examples"]) == 1
    assert "raw_diagnostics" not in json.dumps(shown)


def test_independent_bad_cfg_citations_share_one_current_family_hint():
    material = prepared_material()
    response = response_with_targets(material, [
        {"instruction_id": "ir_read", "path": ["events", 0]},
        {"instruction_id": "ir_filter", "path": ["events", 0, "atomic_ops", 0]},
    ])
    rows = errors(response, material)
    assert [row["path"] for row in rows] == [f"/findings/0/evidences/{index}/target" for index in range(2)]
    shown = correction_context(response, rows)
    assert len(shown["format_examples"]) == 1
    assert [row["context"]["format_example_index"] for row in shown["diagnostics"]] == [0, 0]
    assert len(diagnostic_materials(rows)["raw_diagnostics"]) == 2


@pytest.mark.parametrize("target", [
    {"instruction_id": "ir_read", "side": "input", "index": 0},
    {"instruction_id": "ir_read", "path": ["metadata", "events", 0]},
    {"path": ["constraints", 0]},
])
def test_actual_cfg_paths_remain_valid_including_metadata_named_events(target):
    material = prepared_material(metadata_events=True)
    response = response_with_targets(material, [target])
    validated = services.validate_response(response, material)
    assert validated.findings[0].evidences[0].target.model_dump(mode="json") == target


def test_source_only_evidence_does_not_require_a_cfg_citation():
    material = prepared_material()
    response = response_for(material, finding=True)
    evidence = {"file": "skill/SKILL.md", "start_line": 3, "end_line": 3,
                "reason": "The frozen source provides this location."}
    response["findings"][0]["evidences"] = [evidence]
    assert services.validate_response(response, material).findings[0].evidences[0].model_dump(mode="json") == evidence


def test_source_rule_and_cfg_errors_remain_distinct_without_dependent_errors():
    material = prepared_material()
    response = response_with_targets(material, [{"instruction_id": "ir_read", "path": ["events", 0]}])
    response["findings"][0]["evidences"].extend([
        {"file": "skill/absent.md", "start_line": 1, "end_line": 1, "reason": "Missing file fixture."},
        {"file": "skill/SKILL.md", "start_line": 100, "end_line": 100, "reason": "Out-of-range fixture."},
        {"rule_id": "absent_rule", "reason": "Missing rule fixture."},
    ])
    rows = errors(response, material)
    assert [(row["code"], row["path"]) for row in rows] == [
        ("evidence_target", "/findings/0/evidences/0/target"),
        ("evidence_file", "/findings/0/evidences/1/file"),
        ("evidence_span", "/findings/0/evidences/2"),
        ("evidence_rule", "/findings/0/evidences/3/rule_id"),
    ]
    assert all("format_example" not in row.get("context", {}) for row in rows[1:])


def test_cannot_assess_checks_cfg_namespace_then_remains_a_terminal_failure():
    material = prepared_material()
    response = cannot_assess(material)
    original = deepcopy(response)
    response["failure"]["evidences"] = [{"target": {"instruction_id": "ir_read", "path": ["events", 0]},
                                        "reason": "The fixture uses an annotation coordinate as a CFG citation."}]
    row = errors(response, material)[0]
    assert (row["code"], row["path"]) == ("evidence_target", "/failure/evidences/0/target")
    with pytest.raises(SemanticFailure) as caught:
        services.validate_response(original, material)
    assert caught.value.failure == original["failure"]


@pytest.mark.parametrize("error_class", [ValueError, RuntimeError])
def test_untyped_evidence_implementation_failures_do_not_enter_correction(error_class, monkeypatch):
    original, raw = fixture()
    client = ReviewClient(lambda response, material: response_for(material, finding=True))
    def broken(*args, **kwargs):
        raise error_class("Unexpected evidence implementation failure")
    monkeypatch.setattr(services, "check_review_evidence", broken)
    with pytest.raises(error_class, match="Unexpected evidence implementation failure") as caught:
        services.review_annotation(original, raw, client=client)
    assert not isinstance(caught.value, StructuralValidationError)
    assert len(client.prompts) == 1


def prepare_authored_run(tmp_path):
    original, raw = fixture()
    directory = tmp_path / "review"
    runner.prepare_candidate_run(original, raw, run_dir=directory,
                                 provenance={"kind": "explicit_test_fixture"})
    return directory


def invalid_namespace(response, material):
    return response_with_targets(material, [{"instruction_id": "ir_read", "path": ["events", 0]}])


def test_namespace_diagnostic_resume_replay_and_raw_candidate_preservation(tmp_path, monkeypatch):
    directory = prepare_authored_run(tmp_path)
    stop = Event()
    original_validation = ResponseChain._validation
    def after_validation(self, call_dir, row, status, **extra):
        outcome = original_validation(self, call_dir, row, status, **extra)
        if status == "structural_invalid":
            stop.set()
        return outcome
    monkeypatch.setattr(ResponseChain, "_validation", after_validation)
    bad = ReviewClient(invalid_namespace)
    first = runner.run_review(directory, client=bad, stop_event=stop)
    assert first["status"] == "interrupted"
    assert len(bad.prompts) == 1
    first_call = directory / "calls/review/a001"
    frozen = {path.name: path.read_bytes() for path in first_call.iterdir() if path.is_file()}
    candidate = read_json(first_call / "response.json")
    assert candidate["findings"][0]["evidences"][0]["target"]["path"] == ["events", 0]
    assert runner.replay_run(directory) == first
    monkeypatch.setattr(ResponseChain, "_validation", original_validation)
    stop.clear()
    good = ReviewClient()
    final = runner.run_review(directory, client=good, stop_event=stop)
    assert final["status"] == "complete"
    assert final["counts"]["logical_calls"] == 2
    assert final["counts"]["structural_corrections"] == 1
    assert len(good.prompts) == 1
    context = json.loads(good.prompts[0].split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
    assert context["candidate"] == candidate
    assert context["diagnostics"][0]["path"] == "/findings/0/evidences/0/target"
    assert len(context["format_examples"]) == 1
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    monkeypatch.setattr(runner, "streaming_factory", forbidden)
    assert runner.run_review(directory, client_factory=forbidden) == final
    assert runner.replay_run(directory) == final
    assert frozen == {path.name: path.read_bytes() for path in first_call.iterdir() if path.is_file()}


@pytest.mark.parametrize("field", ["current", "allowed_forms", "format_example"])
def test_namespace_diagnostic_receipt_tampering_is_rejected(tmp_path, field):
    directory = prepare_authored_run(tmp_path)
    count = 0
    def candidate(response, material):
        nonlocal count
        count += 1
        return invalid_namespace(response, material) if count == 1 else response
    result = runner.run_review(directory, client=ReviewClient(candidate))
    assert result["status"] == "complete"
    path = directory / "calls/review/a001/validation.json"
    receipt = read_json(path)
    receipt["diagnostics"][0]["context"][field] = "tampered"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError):
        runner.load_review_run(directory)
