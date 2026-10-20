"""Missing receiver seeds are reviewed semantically under an immutable Task.

Injected findings exercise validated coordinates and repair routing. They do
not claim that a model detects these omissions, nor add a structural oracle.
"""
from copy import deepcopy
import json

import pytest

from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.models import task_objections
from skillflow.propagation.review.refinement import refine_annotation
from skillflow.propagation.review.services import validate_response
from tests.doe.test_sink_payload_seeds import (
    boundary_rows, declared_goal, label_operations, solve_fixture,
    synthetic_fixture,
)
from tests.propagation.review.test_core import empty_response


def missing_payload_finding(prepared, *, parent="/realizations/0"):
    response = empty_response(prepared)
    index = prepared["target_index"]
    target_id = (next(identity for identity, row in index.items() if row.get("annotation") == parent)
        if isinstance(index, dict) else next(row["id"] for row in index
            if row["kind"] == "annotation" and row["pointer"] == parent))
    response["findings"] = [{"domain": "annotation", "target_ids": [target_id],
        "explanation": "任务规定接收方取得字段原值，但候选未在交付输入建立对应内容需求；上游结果需求不能证明接收方需求已经表达。",
        "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                       "reason": "独立合成源文明确指定 label 接收方及 display 字段原值。"}],
        "suggestion": "保持封存任务不变，在实际交付参数槽位补齐内容需求，保留字段身份。"}]
    response["requirement_checks"][0].update(status="issue", finding_indexes=[0],
        reason="已检查要求缺失的需求种子，而不只检查现有 goals。")
    return response


@pytest.mark.parametrize("producer_seed", [False, True])
@pytest.mark.parametrize("parent", ["/realizations/0", "/ir_semantics/ir_format/events/1"])
def test_structurally_valid_omission_has_a_checked_annotation_finding(producer_seed, parent):
    material, raw, facts = synthetic_fixture(label_operations(producer_seed=producer_seed))
    before = deepcopy((material, raw))
    # Both absence and an upstream-only seed are mechanically representable.
    assert compile_response(raw, material)[0] == raw
    prepared = prepare_review_material(material, raw)
    assert len(prepared["declaration_index"]) == int(producer_seed)
    response = validate_response(missing_payload_finding(prepared, parent=parent), prepared)
    assert response.requirement_checks[0].finding_ids == ["F001"]
    assert task_objections(response) == []
    assert response.findings[0].domain == "annotation"
    assert all(check.status == "accepted" for check in response.declaration_checks)
    assert (material, raw) == before
    _, solved = solve_fixture((material, raw, facts))
    assert not boundary_rows(solved)


def test_missing_payload_routes_once_to_fixed_task_annotation_repair_and_rereview():
    original = synthetic_fixture(label_operations(producer_seed=True))
    repaired = synthetic_fixture(label_operations(producer_seed=True, receiver_seed=True))
    material, raw, _ = original
    assert material == repaired[0]
    initial_bytes = deepcopy((material, raw))
    review_prompts, repair_prompts = [], []

    class Review:
        def complete(self, prompt):
            review_prompts.append(prompt)
            current = json.JSONDecoder().raw_decode(prompt.split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n", 1)[1])[0]
            return missing_payload_finding(current) if len(review_prompts) == 1 else empty_response(current)

    class Repair:
        def complete(self, prompt):
            repair_prompts.append(prompt)
            return deepcopy(repaired[1])

    class ForbiddenTaskRevision:
        def complete(self, prompt):
            raise AssertionError("A valid Task must not be revised for an annotation omission")

    result = refine_annotation(material, raw, review_client=Review(), repair_client=Repair(),
                               task_repair_client=ForbiddenTaskRevision())
    assert result["status"] == "review_passed", result["reason"]
    assert result["selected"] == "repair"
    assert result["task_revision"] is None
    assert result["counts"]["logical_calls"] == 3 and result["counts"]["structural_corrections"] == 0
    assert len(review_prompts) == 2 and len(repair_prompts) == 1
    assert result["material"]["task"] == material["task"]
    assert result["raw_annotation"] == repaired[1]
    assert initial_bytes == (material, raw)
    first, final = [json.JSONDecoder().raw_decode(prompt.split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n", 1)[1])[0] for prompt in review_prompts]
    assert first["task"] == final["task"]
    assert first["source"] == final["source"]
    assert first["cfg"] == final["cfg"] == material["cfg"]
    assert final["raw_annotation"] == repaired[1]
    assert not {"repair_context", "review_response", "resolved_targets"} & final.keys()
    assert "REPAIR_CONTEXT" in repair_prompts[0]
    assert "task_revision_id" in repair_prompts[0]
    _, before = solve_fixture(original)
    _, after = solve_fixture(repaired)
    assert not boundary_rows(before)
    assert boundary_rows(after)
    assert {row["node"]["slot"] for row in boundary_rows(after)} == {0}


def test_save_action_only_is_structurally_legal_and_semantically_reviewable():
    from skillflow.propagation.annotation.binding_examples import inp, local
    fixture = synthetic_fixture([
        {"op": "select_part", "input": inp(), "path": ["display"], "output": "formatted"},
        {"op": "write", "mode": "append", "target": "journal", "input": local("formatted"),
         "demands": [declared_goal("self", preserve="action")]}])
    material, raw, _ = fixture
    review = prepare_review_material(material, raw)
    response = missing_payload_finding(review)
    finding = response["findings"][0]
    finding["explanation"] = "任务要求保存指定内容，但 action 仅保持保存发生，不能替代写入载荷需求。"
    finding["suggestion"] = "在追加操作的实际输入上保持新写入值；不要把旧文件整体变成需求。"
    accepted = validate_response(response, review)
    assert accepted.requirement_checks[0].status == "issue"
    assert accepted.declaration_checks[0].status == "accepted"  # The action itself is legal.
    assert task_objections(accepted) == []
    _, solved = solve_fixture(fixture)
    assert boundary_rows(solved, "storage_write", node_kind="action")
    assert not boundary_rows(solved, "storage_write")
