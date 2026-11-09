"""Actual case coordinates survive assembly, sparse review and owner routing."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import assemble_fragments, split_fragments
from skillflow.document_guided.runner import _fragment_repair_findings
from skillflow.document_guided.source_review import prepare_review_material, validate_source_review
from skillflow.propagation.contracts.task import task_source_files
from tests.document_guided.test_case_summaries import case_fixture, local


def reviewed_cases(*, partial=False):
    material, wire = case_fixture(state=False)
    normal = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][0]["segments"][0]
    normal.pop("returns")
    normal["mode"] = "default"
    fragments = split_fragments(wire)
    fragments["task-correspondence"]["operation_demands"] = [{
        "instruction_id": "ir_call", "operation_path": ["segments", 0, "body", 0, "cases", 0, "segments", 0, "ops", 0],
        "demands": [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value", "reason": "Return the source-supported response."}]}]
    fragments["sensitivity"] = {"declarations": [{"instruction_id": "ir_call", "scope_path": ["segments", 0],
        "case_path": ["segments", 0, "body", 0, "cases", 0], "value": local("reply"), "label": "Private report"}]}
    kwargs = {"files": task_source_files(material["source"]), "task": material["task"],
              "cfg": material["cfg"], "generation": "fragment-v1"}
    if partial:
        return prepare_review_material(**kwargs, fragments=fragments, partial=True)
    annotation, _, compiled, mapping = assemble_fragments(fragments["processing"],
        fragments["task-correspondence"], fragments["sensitivity"], material)
    return prepare_review_material(**kwargs, annotation=annotation, compiled=compiled, mapping=mapping)


def finding(target):
    return {"domain": "annotation", "target_ids": [target], "explanation": "Recheck the declared source relationship.",
            "source_refs": [], "suggestion": "Preserve the correct source-supported relationship."}


def test_assembled_nested_case_targets_route_to_actual_semantic_owners():
    material = reviewed_cases()
    operation = "annotation:/ir_semantics/ir_call/segments/0/body/0/cases/0/segments/0/ops/0"
    sensitive = "annotation:/ir_semantics/ir_call/segments/0/sensitivity/0"
    targets = {row["id"]: row for row in material["target_index"]}
    expected = {operation: "processing", operation + "/demands/0": "task-correspondence", sensitive: "sensitivity"}
    for identity, owner in expected.items():
        assert targets[identity]["owner"] == owner
    assert not any("/case_path" in identity for identity in targets)
    assert material["annotation"]["ir_semantics"]["ir_call"]["segments"][0]["sensitivity"][0]["case_path"]
    review = validate_source_review({"outcome": "completed", "findings": [finding(target) for target in expected]}, material)
    for (target, owner), checked in zip(expected.items(), review["findings"]):
        assert checked["owner"] == owner
        selected = _fragment_repair_findings(review, owner)
        assert selected == [{"target_ids": [target], "source_refs": []}]
        assert "explanation" not in selected[0]
    bad = finding(sensitive)
    bad["owner"] = "processing"
    with pytest.raises(StructuralValidationError, match="owner"):
        validate_source_review({"outcome": "completed", "findings": [bad]}, material)


def test_case_compiler_observation_targets_keep_actual_wire_coordinates():
    material = reviewed_cases()
    observations = material["observations"]
    assert observations
    assert any("/cases/0/segments/0/ops/0" in row["wire_pointer"] for row in observations)
    targets = {row["id"]: row for row in material["target_index"]}
    assert all(targets[f"observations:/{index}"]["owner"] == "processing" for index in range(len(observations)))
    review = validate_source_review({"outcome": "completed", "findings": [finding("observations:/0")]}, material)
    assert review["findings"][0]["owner"] == "processing"


def test_partial_case_fragments_are_reviewable_without_an_annotation():
    material = reviewed_cases(partial=True)
    before = deepcopy(material)
    expected = {
        "fragment:processing:/ir_semantics/ir_call/segments/0/body/0/cases/0/segments/0/ops/0": "processing",
        "fragment:task-correspondence:/operation_demands/0": "task-correspondence",
        "fragment:sensitivity:/declarations/0": "sensitivity",
    }
    targets = {row["id"]: row for row in material["target_index"]}
    assert material["annotation"] is None
    assert not any("/case_path" in identity for identity in targets)
    review = validate_source_review({"outcome": "completed", "findings": [finding(target) for target in expected]}, material)
    assert [row["owner"] for row in review["findings"]] == list(expected.values())
    assert material == before
