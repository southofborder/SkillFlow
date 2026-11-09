"""Reuse checked processing without changing case/member identities or diagnostics."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import annotation_wire as flat
from skillflow.document_guided.fragments import assemble_fragments, split_fragments, validate_fragment
from skillflow.propagation.annotation.binding_examples import evidence
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate
from tests.document_guided.test_case_summaries import case_fixture, local
from tests.document_guided.test_fragment_diagnostic_aggregation import case_inputs, declaration


def _many_declarations(count):
    return {"declarations": [declaration(
        case_path=["segments", 0, "cases", 0], label=f"Source-supported category {index}")
        for index in range(count)]}


@pytest.mark.parametrize("count", [1, 13, 40])
def test_case_declaration_count_does_not_repeat_processing_expansion(monkeypatch, count):
    material, parts = case_inputs()
    sensitivity = _many_declarations(count)
    before = deepcopy((parts, sensitivity))
    source_only = {key: value for key, value in material.items() if key != "task"}
    expand, calls = flat._expand, []

    def counted(*args, **kwargs):
        calls.append(kwargs.get("processing_only", False))
        return expand(*args, **kwargs)

    monkeypatch.setattr(flat, "_expand", counted)
    assert validate_fragment("sensitivity", sensitivity, source_only, parts["processing"]) == sensitivity
    assert calls == [True]
    assert (parts, sensitivity) == before


def test_assembly_reuses_one_checked_base_and_keeps_full_compilation(monkeypatch):
    material, parts = case_inputs()
    sensitivity = _many_declarations(13)
    before = deepcopy((parts, sensitivity))
    expand, calls = flat._expand, []

    def counted(*args, **kwargs):
        calls.append(kwargs.get("processing_only", False))
        return expand(*args, **kwargs)

    monkeypatch.setattr(flat, "_expand", counted)
    assembled = assemble_fragments(parts["processing"], parts["task-correspondence"], sensitivity, material)
    # One checked processing base, one mapping check, one complete compilation.
    assert calls == [True, False, False]
    monkeypatch.setattr(flat, "_expand", expand)
    assert flat.compile_flat_response(assembled[0], material) == assembled
    assert (parts, sensitivity) == before


@pytest.mark.parametrize("scope", ["case_value", "summary_alias"])
def test_shared_member_projection_matches_full_expansion(scope):
    material, wire = case_fixture(state=False)
    processing = split_fragments(wire)["processing"]
    scopes = flat._processing_expansion(
        {"outcome": "completed", "realizations": [], **processing}, material)[3]
    item = {"value": local("reply" if scope == "case_value" else "member_result"),
            "label": "Private result", "evidences": [evidence()]}
    if scope == "case_value":
        item["case_path"] = ["segments", 0, "body", 0, "cases", 0]
    before = deepcopy((processing, scopes, item))
    assert flat._project_expanded_sensitivity(scopes, "ir_call", ["segments", 0], item) == \
        flat.project_sensitivity(processing, "ir_call", ["segments", 0], item, material)
    assert (processing, scopes, item) == before


def test_case_member_assembly_preserves_occurrences_local_returns_and_output_versions():
    material, wire = case_fixture(state=False)
    parts = split_fragments(wire)
    sensitivity = {"declarations": [{"instruction_id": "ir_call", "scope_path": ["segments", 0],
        "case_path": ["segments", 0, "body", 0, "cases", 0],
        "value": local("reply"), "label": "Private result", "evidences": [evidence()]}]}
    assembled = assemble_fragments(parts["processing"], parts["task-correspondence"], sensitivity, material)
    independently_compiled = flat.compile_flat_response(assembled[0], material)
    assert assembled == independently_compiled
    solved = propagate(material["cfg"], to_payload(assembled[2]))
    assert solved.status == "complete"
    loop = solved.records.get("ir_call").events[0]
    assert {member.selector for member in loop.instances} == {0, 1}
    responses = [next(iter(op.outputs[0])) for member in loop.instances for event in member.body
                 for op in event.atomic_ops if event.case.phase == "normal" and op.op == "receive"]
    assert len(set(responses)) == 2
    assert all(event.effect != "model_observe" for member in loop.instances for event in member.body)
    assert all(len(member.yielded) == 2 for member in loop.instances)
    solved.records.validate(require_complete=True)


def test_shared_projection_keeps_case_scope_errors_and_good_siblings():
    material, wire = case_fixture(state=False)
    parts = split_fragments(wire)
    valid = {"instruction_id": "ir_call", "scope_path": ["segments", 0],
        "case_path": ["segments", 0, "body", 0, "cases", 0],
        "value": local("reply"), "label": "Private result"}
    wrong_scope = {**valid, "scope_path": []}
    missing_case = {**valid, "case_path": ["segments", 0, "body", 0, "cases", 99]}
    candidate = {"declarations": [wrong_scope, valid, missing_case]}
    before = deepcopy(candidate)
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", candidate, material, parts["processing"])
    errors = caught.value.diagnostics
    assert {int(item["path"].split("/")[2]) for item in errors} == {0, 2}
    assert {(item["path"], item["code"]) for item in errors} == {
        ("/declarations/0", "schema"), ("/declarations/2/case_path", "case_reference")}
    assert candidate == before


def test_reuse_does_not_cross_separate_validation_calls():
    material, parts = case_inputs()
    sensitivity = _many_declarations(1)
    assert validate_fragment("sensitivity", sensitivity, material, parts["processing"]) == sensitivity
    changed = deepcopy(parts["processing"])
    changed["ir_semantics"]["ir_call"]["segments"][0]["cases"][0]["segments"][0]["ops"][0]["location"] = "absent"
    with pytest.raises(StructuralValidationError):
        validate_fragment("sensitivity", sensitivity, material, changed)
