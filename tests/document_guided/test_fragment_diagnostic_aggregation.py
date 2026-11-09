"""One correction sees independently checkable siblings at original coordinates."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory
from skillflow.common.structural_correction import ResponseChain
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import (
    assemble_fragments, fragment_correction_strategy, split_fragments, validate_fragment,
)
from skillflow.document_guided.online import CONFIG
from tests.document_guided.test_annotation_wire import sample


def inputs():
    material, wire = sample()
    return material, split_fragments(wire)


def declaration(**changes):
    return {"instruction_id": "ir_call", "value": {"kind": "local", "name": "reply"},
            "label": "Credential", **changes}


def test_invalid_sensitivity_scope_does_not_mask_other_references_or_evidence():
    material, fragments = inputs()
    p = fragments["processing"]
    bad_citation = deepcopy(p["ir_semantics"]["ir_call"]["evidences"][0])
    bad_citation["file"] = "skill/not-in-source.md"
    candidate = {"declarations": [
        declaration(scope_path=["segments", 0, "body", 0]),
        declaration(value={"kind": "local", "name": "never_defined"}),
        declaration(instruction_id="ir_absent", evidences=[bad_citation]),
        declaration(evidences=[bad_citation]),
        declaration(),
    ]}
    before = deepcopy(candidate)
    source_only = {key: value for key, value in material.items() if key != "task"}
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", candidate, source_only, p)
    rows = caught.value.diagnostics
    assert {0, 1, 2, 3} <= {int(row["path"].split("/")[2]) for row in rows}
    assert not any(row["path"].startswith("/declarations/4") for row in rows)
    assert all(row["context"]["fragment"] == "sensitivity" for row in rows)
    assert all(row["context"]["record_id"].startswith("/declarations/") for row in rows)
    assert any(row["path"] == "/declarations/2/instruction_id" and row["context"]["current"] == "ir_absent" for row in rows)
    assert candidate == before


@pytest.mark.parametrize("bad_record", [None, 4, {"instruction_id": "ir_call", "scope_path": 7}])
def test_malformed_sibling_does_not_crash_or_hide_valid_record_reference(bad_record):
    material, fragments = inputs()
    candidate = {"declarations": [bad_record, declaration(value={"kind": "input", "index": 300})]}
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", candidate, material, fragments["processing"])
    paths = [row["path"] for row in caught.value.diagnostics]
    assert any(path.startswith("/declarations/0") for path in paths)
    assert any(path.startswith("/declarations/1") for path in paths)


def test_processing_schema_error_does_not_mask_independent_local_reference():
    material, fragments = inputs()
    candidate = fragments["processing"]
    candidate["ir_semantics"]["ir_call"]["unexpected_model_field"] = "invalid"
    candidate["ir_semantics"]["ir_return"]["segments"] = [{"ops": [
        {"op": "compute", "inputs": [{"kind": "local", "name": "missing"}], "output": "result"}]}]
    before = deepcopy(candidate)
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", candidate, material)
    paths = [row["path"] for row in caught.value.diagnostics]
    assert any(path.startswith("/ir_semantics/ir_call") for path in paths)
    assert any(path.startswith("/ir_semantics/ir_return") for path in paths)
    assert candidate == before
    assert "processing_gaps" not in candidate


def test_correspondence_schema_error_does_not_mask_independent_operation_references():
    material, fragments = inputs()
    candidate = fragments["task-correspondence"]
    valid = deepcopy(candidate["operation_demands"][0])
    candidate["operation_demands"] = [
        {**valid, "demands": []},
        {**valid, "operation_path": ["segments", 0, "ops", 99]},
        {**valid, "instruction_id": "ir_absent"},
        valid,
    ]
    before = deepcopy(candidate)
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("task-correspondence", candidate, material, fragments["processing"])
    paths = [row["path"] for row in caught.value.diagnostics]
    assert any(path.startswith("/operation_demands/0") for path in paths)
    assert "/operation_demands/1/operation_path" in paths
    assert "/operation_demands/2/operation_path" in paths
    assert not any(path.startswith("/operation_demands/3") for path in paths)
    assert candidate == before


def test_single_record_correction_receives_all_errors_and_preserves_good_record(tmp_path):
    material, fragments = inputs()
    good = declaration(label="Public")
    candidate = {"declarations": [declaration(scope_path=["bad"]),
        declaration(value={"kind": "local", "name": "absent"}), good]}
    replacements = {"replacements": [
        {"record_id": "/declarations/0", "value": declaration()},
        {"record_id": "/declarations/1", "value": declaration(label="Personal")} ]}
    replies = [json.dumps(candidate), json.dumps(replacements)]
    prompts = []

    class Client:
        def complete(self, prompt):
            prompts.append(prompt)
            return replies.pop(0)

    args = dict(prefix="calls", base_prompt="Declare source-supported sensitivity.",
        request_kind="sensitivity_fragment", config=CONFIG, writer=ArtifactWriter(()),
        validate=lambda raw: validate_fragment("sensitivity", raw, material, fragments["processing"]),
        max_corrections=1)
    result = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("sensitivity"),
        client_factory=injected_factory(Client())).run()
    assert result["declarations"][2] == good
    assert len(prompts) == 2
    assert '"/declarations/0"' in prompts[1] and '"/declarations/1"' in prompts[1]
    replay = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("sensitivity"),
        client_factory=None).run()
    assert replay == result
    assert len(prompts) == 2


def case_inputs():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    child = deepcopy(spec["segments"][0])
    spec["segments"] = [{"kind": "cases", "output": "chosen_reply", "cases": [{
        "name": "normal", "phase": "normal", "disposition": "return", "condition": "The protected call returns normally.",
        "segments": [child], "yield": {"kind": "local", "name": "reply"}}]}]
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "chosen_reply"}
    return material, split_fragments(wire)


def test_case_fragments_keep_operation_ownership_and_refer_to_program_lowered_values():
    material, fragments = case_inputs()
    p, m = fragments["processing"], fragments["task-correspondence"]
    assert m["operation_demands"][0]["operation_path"] == ["segments", 0, "cases", 0, "segments", 0, "ops", 0]
    s = {"declarations": [declaration(case_path=["segments", 0, "cases", 0]),
        declaration(value={"kind": "local", "name": "chosen_reply"}, label="Personal")]}
    before = deepcopy((p, m, s))
    source_only = {key: value for key, value in material.items() if key != "task"}
    assert validate_fragment("sensitivity", s, source_only, p) == s
    saved, backend, compiled, mapping = assemble_fragments(p, m, s, material)
    assert (p, m, s) == before
    assert backend["ir_semantics"]["ir_call"]["sensitivity"][0]["value"]["name"].endswith("__reply")
    assert "case_path" not in backend["ir_semantics"]["ir_call"]["sensitivity"][0]
    assert saved["ir_semantics"]["ir_call"]["sensitivity"][0]["case_path"] == ["segments", 0, "cases", 0]
    assert compiled["demands"] and mapping["fragment_paths"]


def test_case_processing_forbids_hidden_demands_inside_nested_segments():
    material, fragments = case_inputs()
    p = fragments["processing"]
    op = p["ir_semantics"]["ir_call"]["segments"][0]["cases"][0]["segments"][0]["ops"][0]
    op["demands"] = fragments["task-correspondence"]["operation_demands"][0]["demands"]
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", p, material)
    assert any(row["path"].endswith("/demands") for row in caught.value.diagnostics)


def test_sensitivity_cannot_address_another_occurrence_scope_by_case_path():
    material, fragments = inputs()
    s = {"declarations": [declaration(case_path=["segments", 0, "body", 0, "cases", 0]) ]}
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", s, material, fragments["processing"])
    assert any(row["path"].startswith("/declarations/0") for row in caught.value.diagnostics)


def test_explicit_null_case_path_matches_omission():
    material, fragments = inputs()
    candidate = {"declarations": [declaration(case_path=None)]}
    assert validate_fragment("sensitivity", candidate, material, fragments["processing"]) == candidate
