"""Endpoint lessons remain executable examples, not semantic auto-repair rules."""
from copy import deepcopy
import json

import pytest

from skillflow.propagation.annotation.binding_examples import (
    example_material, prompt_sink_demand_examples, sink_demand_examples,
)
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.prompts import REPAIR_INSTRUCTIONS
from skillflow.propagation.annotation.prompt_examples import compact_prompt_examples
from skillflow.propagation.contracts.format_instructions import format_instructions
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt as review_prompt
from skillflow.propagation.review.services import review_annotation
from tests.propagation.review.test_core import empty_response


@pytest.mark.parametrize("index", range(6))
def test_independent_endpoint_and_exception_lessons_compile_without_mutation(index):
    example = sink_demand_examples()[index]
    before = deepcopy(example)
    material = example_material(example)
    raw, compiled, mapping = compile_response(example["annotation"], material)
    assert compiled["demands"]
    assert mapping["events"]
    assert raw["task_revision_id"] == material["task"]["task_sha256"]
    assert before == example


@pytest.mark.parametrize("index", range(3))
def test_semantically_missing_payload_seeds_are_not_auto_added_or_schema_errors(index):
    example = sink_demand_examples()[index]
    material = example_material(example)
    before = deepcopy(example)
    raw, deficient, _ = compile_response(example["contrast"], material)
    _, complete, _ = compile_response(example["annotation"], material)
    assert len(complete["demands"]) > len(deficient["demands"]) or index == 0
    assert example == before
    def seed_count(node):
        if isinstance(node, dict):
            return len(node.get("demands", [])) + sum(seed_count(value) for key, value in node.items() if key != "demands")
        if isinstance(node, list):
            return sum(seed_count(value) for value in node)
        return 0
    assert seed_count(raw) == seed_count(example["contrast"]) == len(deficient["demands"])
    if index == 0:
        # A producer-output seed remains distinct from the actual receiving slot.
        assert deficient["demands"][0]["target"] != complete["demands"][0]["target"]
    if index == 1:
        assert {goal["preserve"] for goal in deficient["demands"]} == {"action"}
        assert {goal["preserve"] for goal in complete["demands"]} == {"action", "value"}


@pytest.mark.parametrize("index", range(3))
def test_missing_seed_finding_uses_requirement_axis_and_annotation_parent(index):
    example = sink_demand_examples()[index]
    material = example_material(example)
    prepared = prepare_review_material(material, example["contrast"])
    parent = next(item for item in prepared["target_index"]
                  if item["kind"] == "annotation" and item["pointer"] == "/realizations/0")
    response = empty_response(prepared)
    response["requirement_checks"][0].update(status="issue", finding_indexes=[0])
    response["findings"] = [{"domain": "annotation", "target_ids": [parent["id"]],
        "explanation": "Task要求具体交付或保存内容，但当前只约束生产结果或动作，缺少实际边界载荷需求。",
        "suggestion": "保留固定Task，将其内容关系落实到相应交付或写入输入槽位；不扩大到全部载荷。",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "独立合成原文要求保持交付或保存的具体内容。"}]}]
    calls = []

    class Client:
        def complete(self, prompt):
            calls.append(prompt)
            return deepcopy(response)

    accepted = review_annotation(material, example["contrast"], client=Client())
    assert len(calls) == 1
    assert accepted.findings[0].domain == "annotation"
    assert accepted.findings[0].task_objection is None
    assert accepted.requirement_checks[0].finding_ids == ["F001"]
    assert all(item.status == "accepted" for item in accepted.declaration_checks)


def test_shared_rules_and_compact_lessons_reach_annotation_and_review_once():
    from skillflow.propagation.review.prompts import review_examples
    from skillflow.propagation.annotation.prompt_examples import coordinate_examples
    example = sink_demand_examples()[0]
    material = example_material(example)
    annotation = annotation_prompt(material)
    review = review_prompt(prepare_review_material(material, example["annotation"]))
    lessons = compact_prompt_examples()
    for prompt in (annotation, review):
        assert prompt.count("ENDPOINT DEMANDS.") == 1
        assert prompt.count("ENDPOINT EXCEPTIONS.") == 1
        coordinates = json.JSONDecoder().raw_decode(prompt.split("\nCOORDINATE_EXAMPLES\n", 1)[1])[0]
        assert coordinates == coordinate_examples()
    annotation_lessons = json.JSONDecoder().raw_decode(annotation.split("\nBINDING_EXAMPLES\n", 1)[1])[0]
    review_lessons = json.JSONDecoder().raw_decode(review.split("\nREVIEW_EXAMPLES\n", 1)[1])[0]
    assert annotation_lessons == lessons
    assert review_lessons == review_examples() and review_lessons != annotation_lessons
    assert all(not {"cfg", "annotation", "contrast", "task_candidate"} & row.keys() for row in lessons)
    serialized = json.dumps(lessons)
    for excluded in ("FAST_KEY", "notify.send", "access_token", "from_date", "source_id", "opted_out", "ir_001", "ir_013"):
        assert excluded not in serialized
    assert "Policies support sensitivity" not in review
    assert "shared endpoint rules" in REPAIR_INSTRUCTIONS
    assert "without redundant expected" in format_instructions()
    assert "Check missing demands, not only declaration_index" in review
