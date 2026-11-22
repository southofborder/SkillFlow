"""Correspondence repairs cannot replace another Task requirement's goals."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragment_revision import correspondence_scope, merge_correspondence_revision
from skillflow.document_guided.fragments import validate_fragment
from skillflow.propagation.contracts.task import Task
from tests.document_guided.test_fragments import fixture


def _seal(task):
    body = {key: value for key, value in task.items() if key != "task_sha256"}
    return Task.model_validate({**body, "task_sha256": canonical_sha256(body)}).model_dump(mode="json")


def inputs():
    material, _, fragments = fixture()
    task = deepcopy(material["task"])
    task["requirements"].append({**task["requirements"][0], "id": "R2", "text": "Keep the second requirement independently."})
    task = _seal(task)
    fragment = fragments["task-correspondence"]
    fragment["realizations"].append({"requirement_id": "R2"})
    groups = fragment["operation_demands"]
    groups[0]["demands"].append({**groups[0]["demands"][0], "requirement_id": "R2", "reason": "Keep the independent response."})
    return {**material, "task": task}, fragments["processing"], fragment


def test_operation_demand_target_only_owns_the_reviewed_requirement():
    material, processing, prior = inputs()
    cfg, task = material["cfg"], material["task"]
    target = "annotation:/ir_semantics/ir_call/segments/0/ops/0/demands/1"
    findings = [{"domain": "annotation", "owner": "task-correspondence", "target_ids": [target]}]
    scope = correspondence_scope(cfg, cfg, processing, processing, task, task, findings, prior)
    assert set(scope["slots"]) == {"R2"}
    assert scope["slots"]["R2"]["source_rechecks"][0]["target_id"] == target
    assert merge_correspondence_revision(prior, scope, {"slots": [{"requirement_id": "R2", "keep": True}]}) == prior

    group = deepcopy(prior["operation_demands"][0])
    group["demands"] = [{**group["demands"][1], "reason": "Keep only this reviewed relation."}]
    patch = {"slots": [{"requirement_id": "R2", "realization": {"requirement_id": "R2"},
                         "demands": [], "operation_demands": [group]}]}
    result = merge_correspondence_revision(prior, scope, patch)
    assert result["operation_demands"][0]["demands"] == [prior["operation_demands"][0]["demands"][0], group["demands"][0]]
    assert validate_fragment("task-correspondence", result, material, processing) == result

    group["demands"].append(prior["operation_demands"][0]["demands"][0])
    with pytest.raises(StructuralValidationError, match="exact requirement"):
        merge_correspondence_revision(prior, scope, patch)


def test_task_item_change_under_same_cfg_cannot_keep_old_record_without_review():
    material, processing, prior = inputs()
    cfg, task = material["cfg"], material["task"]
    changed_task = {**task, "requirements": [{**task["requirements"][0], "id": "R3"}, task["requirements"][1]]}
    changed_task = _seal(changed_task)
    scope = correspondence_scope(cfg, cfg, processing, processing, task, changed_task, [], prior)
    assert scope["removed_requirement_ids"] == ["R1"] and set(scope["slots"]) == {"R3"}
    with pytest.raises(StructuralValidationError):
        merge_correspondence_revision(prior, scope, {"slots": [{"requirement_id": "R3", "keep": True}]})
    result = merge_correspondence_revision(prior, scope, {"slots": [{"requirement_id": "R3",
        "realization": {"requirement_id": "R3", "gaps": [{"reason": "No confirmed mapping for this requirement.",
            "evidences": changed_task["requirements"][0]["evidences"]}]}, "demands": [], "operation_demands": []}]})
    assert result["operation_demands"][0]["demands"] == [prior["operation_demands"][0]["demands"][1]]
    assert {row["requirement_id"] for row in result["realizations"]} == {"R2", "R3"}
    assert validate_fragment("task-correspondence", result, {**material, "task": changed_task}, processing) == result


def test_wider_or_changed_dependencies_require_a_fresh_correspondence():
    material, processing, prior = inputs()
    cfg, task = material["cfg"], material["task"]
    assert correspondence_scope(cfg, cfg, processing, processing, task, task, [], prior)["slots"] == {}
    altered = deepcopy(processing)
    altered["ir_semantics"]["ir_call"]["order"] = "partial"
    assert correspondence_scope(cfg, cfg, processing, altered, task, task, [], prior) is None
    finding = {"domain": "annotation", "owner": "task-correspondence", "target_ids": ["annotation:/demands"]}
    assert correspondence_scope(cfg, cfg, processing, processing, task, task, [finding], prior) is None
