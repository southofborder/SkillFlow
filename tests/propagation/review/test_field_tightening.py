"""The compact request remains resolvable and cannot hide occurrence evidence."""
from copy import deepcopy
import json
import pytest
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.annotation.requests import build_repair_context, repair_prompt_payload
from tests.propagation.review.test_core import fixture, one_issue


def test_review_projects_candidate_references_without_repeating_subtrees():
    base, raw = fixture()
    checked = prepare_review_material(base, raw)
    before = deepcopy(checked)
    sent = json.JSONDecoder().raw_decode(build_prompt(checked).split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n")[1])[0]
    assert sent["raw_annotation"] == checked["raw_annotation"]
    assert sent["raw_annotation"] == checked["raw_annotation"]
    assert sent["target_index"] == {target["id"]: {target["kind"]: target["pointer"]} for target in checked["target_index"]}
    assert not {"source_index", "graph_index", "instruction_index", "task_targets", "semantic_context"} & sent.keys()
    assert checked == before


def test_raw_finding_has_no_id_but_normalized_identity_is_checked():
    prepared = prepare_review_material(*fixture())
    raw = one_issue(prepared)
    normalized = validate_response(raw, prepared).model_dump(mode="json")
    assert normalized["findings"][0]["id"] == "F001"
    assert "id" not in raw["findings"][0]
    assert validate_response(normalized, prepared, normalized=True).model_dump(mode="json") == normalized
    with pytest.raises(ValueError):
        validate_response(normalized, prepared)
    normalized["findings"][0]["id"] = "F002"
    with pytest.raises(ValueError):
        validate_response(normalized, prepared, normalized=True)


def test_repair_retains_original_once_and_target_addresses_without_value_copies():
    base, raw = fixture()
    prepared = prepare_review_material(base, raw)
    original = prepared["raw_annotation"]
    review = validate_response(one_issue(prepared), prepared).model_dump(mode="json")
    context = build_repair_context(base, original, prepared, review)
    sent = repair_prompt_payload(base, context)
    assert "review_material" not in sent and "identities" not in sent
    assert all("value" not in target for finding in sent["resolved_targets"] for target in finding["targets"])
    assert any("value" in target for finding in context["resolved_targets"] for target in finding["targets"])
    assert sent["previous_raw_annotation"] == original


def test_repair_retains_referenced_compiled_observation_that_is_absent_from_raw():
    base, raw = fixture()
    prepared = prepare_review_material(base, raw)
    issue = one_issue(prepared)
    observation = prepared["observations"][0]
    issue["findings"][0]["target_ids"].append(observation["id"])
    review = validate_response(issue, prepared).model_dump(mode="json")
    context = build_repair_context(base, prepared["raw_annotation"], prepared, review)
    sent = repair_prompt_payload(base, context)
    annotation, generated, *related = sent["resolved_targets"][0]["targets"]
    assert "value" not in annotation
    assert generated["kind"] == "observation"
    assert generated["value"] == observation
    ids = {target["id"] for target in sent["resolved_targets"][0]["targets"]}
    assert {observation["raw_target_id"], observation["processing_target_id"],
            *observation["scope_target_ids"]} <= ids
    assert all("value" not in target for target in related)
    assert "observations" not in sent and "review_material" not in sent
