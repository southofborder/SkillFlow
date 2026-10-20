"""Specific repair guidance and source restrictions are semantic review duties.

These local synthetic fixtures are not production teaching data or model
accuracy measurements. Mechanical acceptance never establishes semantic truth.
"""
from copy import deepcopy
import json
import re

import pytest

from skillflow.common.source_evidence import resolve_pointer
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, goal, inp, instruction, literal, local,
    result, segment, semantics,
)
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.requests import build_repair_context
from skillflow.propagation.material import evidence_reference
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.models import task_objections
from skillflow.propagation.review.services import validate_response
from tests.propagation.review.test_core import empty_response
from tests.propagation.review.test_endpoint_review_example import rendered_lesson


def _operations(raw):
    def visit(node, pointer=""):
        if isinstance(node, dict):
            if "op" in node:
                yield pointer, node
            for key, value in node.items():
                yield from visit(value, pointer + "/" + str(key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from visit(value, pointer + "/" + str(index))
    return list(visit(raw))


def _blank_review(material):
    response = empty_response(material)
    for axis in ("source_checks", "requirement_checks", "declaration_checks"):
        for row in response[axis]:
            row["reason"] = "This injected check records inspection, not semantic proof."
    return response


def _restriction_fixture():
    """The implementation excludes a private field, but Task loses its ban."""
    source = (
        "Display the stencil's original caption and return that caption internally.\n"
        "Never display archive_pin; archive_pin is a private archive credential."
    )
    pick = {"op": "select_part", "input": inp(), "path": ["caption"], "output": "caption"}
    deliver = {"op": "deliver", "target": "board", "inputs": [local("caption")],
        "demands": [goal({"kind": "self"}, "action"),
                    goal({"kind": "input", "index": 0}, expected=inp(), expected_path=["caption"])]}
    example = _fixture("stencil_archive_restriction", "An excluded credential is still a Task restriction.",
        source,
        [instruction("ir_stencil_display", "display_caption", [literal({"caption": "Ready", "archive_pin": "private"})], "caption"),
         instruction("ir_stencil_return", "return", [result("caption")])],
        {"ir_stencil_display": semantics([segment([pick]), segment([deliver], "user_output")], "caption"),
         "ir_stencil_return": semantics()})
    candidate = example["task_candidate"]
    positive = "Display the original caption and return that caption internally."
    candidate["purpose"]["text"] = positive
    candidate["requirements"][0]["text"] = positive
    candidate["source_accounting"].append({"file": "skill/SKILL.md", "start_line": 2, "end_line": 2,
        "disposition": "supporting_context", "requirement_ids": [], "issue_ids": [],
        "reason": "This injected candidate incorrectly treats the private-field restriction as background."})
    raw = example["annotation"]
    raw["locations"] = {"board": {"kind": "user", "name": "stencil board", "operand_refs": [],
                                    "access_scope": "recipient", "retention": None}}
    raw["location_evidences"] = {"board": [evidence()]}
    raw["ir_semantics"]["ir_stencil_display"]["sensitivity"] = [
        {"value": inp(), "path": ["archive_pin"], "property": "value", "label": "credential",
         "evidences": [{"file": "skill/SKILL.md", "start_line": 2, "end_line": 2,
                        "reason": "The source identifies this field as a private credential."}]}]
    raw["demands"] = [goal({"instruction_id": "ir_stencil_return", "side": "input", "index": 0})]
    raw["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
    material = example_material(example)
    raw["task_revision_id"] = material["task"]["task_sha256"]
    return example, material, raw


def _task_omission_review(prepared):
    response = _blank_review(prepared)
    source_row = response["source_checks"][0]
    source_row.update(status="issue", finding_indexes=[0],
        reason="The second source line imposes an explicit exclusion that the sealed Task omits.")
    target = next(row for row in prepared["target_index"] if row["kind"] == "task" and row["pointer"] == "/requirements")
    span = {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}
    response["findings"] = [{"domain": "task", "target_ids": [target["id"]],
        "explanation": "The sealed Task does not preserve the explicit prohibition. Correct selection and a credential declaration do not replace that task obligation.",
        "evidences": [{**span, "reason": "The source explicitly forbids displaying the credential."}],
        "suggestion": "Restore the explicit exclusion as a Task restriction; do not create a positive demand for the credential.",
        "task_objection": {"code": "missing_requirement", "source_spans": [span], "requirement_ids": []}}]
    return response


def test_rendered_complete_lesson_identifies_only_the_concrete_redundant_content_demands():
    _, lesson, _, review = rendered_lesson()
    raw = lesson["context"]["raw_annotation"]
    build_pointer, build = next(row for row in _operations(raw) if row[1]["op"] == "build")
    deliver_pointer, _ = next(row for row in _operations(raw) if row[1]["op"] == "deliver")
    value_pointers = [f"{build_pointer}/demands/{index}" for index, demand in enumerate(build["demands"])
                      if demand["preserve"] == "value"]
    control_pointers = [f"{build_pointer}/demands/{index}" for index, demand in enumerate(build["demands"])
                        if demand["preserve"] == "truth"]
    targets = {row["pointer"]: row["id"] for row in review["target_index"] if row["kind"] == "annotation"}
    suggestion = lesson["response"]["findings"][1]["suggestion"]
    assert len(value_pointers) == 2 and len(control_pointers) == 1
    assert all(pointer in suggestion or targets[pointer] in suggestion for pointer in value_pointers)
    assert all(pointer not in suggestion and targets[pointer] not in suggestion for pointer in control_pointers)
    assert deliver_pointer in suggestion or targets[deliver_pointer] in suggestion
    assert "do not retain their upstream copies" in suggestion
    for pointer in value_pointers:
        assert pointer in {row["raw_pointer"] for row in review["declaration_index"]}
        assert resolve_pointer(raw, pointer)["preserve"] == "value"
    assert validate_response(lesson["response"], review).findings[1].domain == "annotation"


def test_prompt_retains_seven_sections_without_evaluated_skill_answers():
    prompt, _, _, _ = rendered_lesson()
    sections = re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->", prompt)
    assert sections == ["AUTHORITY", "INPUT", "FORMAT", "WORKFLOW", "RULES", "EXAMPLES", "SELF_CHECK"]
    assert prompt.count("\nREVIEW_EXAMPLES\n") == 1
    assert prompt.count("CHECK KEYS (exact; no additional fields)") == 1
    assert all(token not in prompt for token in ("FAST_KEY", "access_token", "notify.send", "from_date"))
    assert "Explicit source prohibitions must remain in Task even when implementation excludes the information or sensitivity labels exist" in prompt
    assert "private/sensitive wording alone is not a prohibition" in prompt
    assert "Its evidence reason must state only the resolved graph fact" in prompt
    assert "do not preserve the named redundant demands or duplicate them" in prompt


def test_concrete_demand_ids_are_resolvable_in_the_actual_sent_repair_context():
    _, lesson, material, review = rendered_lesson()
    accepted = validate_response(lesson["response"], review)
    finding = accepted.findings[1]
    named_ids = set(re.findall(r"\bann_\d+\b", finding.suggestion))
    assert named_ids and named_ids <= set(finding.target_ids)
    context = build_repair_context(material, review["raw_annotation"], review, accepted)
    sent = annotation_prompt(material, repair_context=context)
    payload = json.JSONDecoder().raw_decode(sent.split("\nREPAIR_CONTEXT\n", 1)[1])[0]
    targets = {row["id"]: row for group in payload["resolved_targets"] for row in group["targets"]}
    originals = {row["id"]: row for row in review["target_index"]}
    for identity in named_ids:
        assert identity in targets
        assert targets[identity]["pointer"] == originals[identity]["pointer"]
        assert resolve_pointer(payload["previous_raw_annotation"], targets[identity]["pointer"]) == resolve_pointer(
            review["raw_annotation"], originals[identity]["pointer"])
    demand_ids = [identity for identity in named_ids if "/demands/" in targets[identity]["pointer"]]
    assert len(demand_ids) == 2
    assert all(resolve_pointer(review["raw_annotation"], targets[identity]["pointer"])["preserve"] == "value"
               for identity in demand_ids)


def test_task_omission_remains_a_source_only_task_objection_despite_correct_exclusion():
    _, material, raw = _restriction_fixture()
    before = deepcopy((material, raw))
    _, compiled, _ = compile_response(raw, material)
    prepared = prepare_review_material(material, raw)
    response = validate_response(_task_omission_review(prepared), prepared)
    assert len(response.findings) == 1 and response.findings[0].domain == "task"
    objections = task_objections(response)
    assert objections == [{"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}], "requirement_ids": []}]
    assert set(objections[0]) == {"code", "source_spans", "requirement_ids"}
    assert "archive_pin" not in str(objections)
    assert (material, raw) == before
    # The existing implementation selects only caption. The negative obligation
    # does not become a demand to read or deliver the prohibited credential.
    assert not any("archive_pin" in str(goal) for goal in compiled["demands"])
    assert prepared["raw_annotation"]["ir_semantics"]["ir_stencil_display"]["sensitivity"]


def test_missing_semantic_finding_can_pass_reference_validation_without_being_proven_correct():
    _, material, raw = _restriction_fixture()
    prepared = prepare_review_material(material, raw)
    assert validate_response(_blank_review(prepared), prepared).findings == []
    assert validate_response(_task_omission_review(prepared), prepared).findings


def test_independent_internal_return_and_receiver_content_demands_are_both_retained():
    _, material, raw = _restriction_fixture()
    checked, compiled, mapping = compile_response(raw, material)
    pointers = {item["raw_pointer"] for item in mapping["goals"]}
    assert "/demands/0" in pointers
    return_goal = next(goal for goal in checked["demands"]
                       if goal["target"].get("instruction_id") == "ir_stencil_return")
    assert return_goal["target"] == {"instruction_id": "ir_stencil_return", "side": "input", "index": 0}
    assert any("/atomic_ops/0/demands/1" in pointer for pointer in pointers)
    assert len(compiled["demands"]) == 3


@pytest.mark.parametrize("overclaim", [False, True])
def test_real_cfg_metadata_with_annotation_like_names_is_valid_but_reason_truth_is_not_mechanical(overclaim):
    example, _, raw = _restriction_fixture()
    metadata = {"events": [{"atomic_ops": ["declared-description"]}], "demands": "graph documentation"}
    example["cfg"]["blocks"]["sample"]["instructions"][0]["metadata"] = metadata
    material = example_material(example)
    raw["task_revision_id"] = material["task"]["task_sha256"]
    prepared = prepare_review_material(material, raw)
    response = _blank_review(prepared)
    target = next(row for row in prepared["target_index"]
                  if row["kind"] == "annotation" and row["pointer"] == "/ir_semantics/ir_stencil_display")
    evidence = {"target": {"instruction_id": "ir_stencil_display",
                          "path": ["metadata", "events", 0, "atomic_ops", 0]},
                "reason": ("This graph metadata proves which candidate demands are present."
                           if overclaim else "This graph metadata contains the declared descriptive marker.")}
    response["findings"] = [{"domain": "annotation", "target_ids": [target["id"]],
        "explanation": "This injected finding illustrates evidence-reference validation, not a semantic conclusion.",
        "evidences": [evidence], "suggestion": "Inspect the candidate using its review target, without inferring candidate facts from graph metadata."}]
    checked = validate_response(response, prepared)
    assert evidence_reference(evidence, material)["text"] == '"declared-description"'
    assert checked.findings[0].evidences[0].reason == evidence["reason"]
    # Both reasons remain mechanically accepted: truthful interpretation is a
    # review responsibility, not an invented keyword-based program check.
