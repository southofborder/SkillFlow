"""Offline integrity and actual-demand checks for the small online pilot."""
from copy import deepcopy
import json
import re

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import Task
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt as review_prompt
from skillflow.propagation.review.services import validate_response as validate_review
from skillflow.propagation.solver import propagate
from tools.doe.endpoint_validation_fixtures import endpoint_validation_fixtures


@pytest.fixture(scope="module")
def fixtures():
    return endpoint_validation_fixtures()


def solve(example):
    checked, compiled, mapping = compile_response(example["reference"], example["material"])
    forward = propagate(example["material"]["cfg"], to_payload(compiled))
    assert forward.status == "complete", forward.diagnostics
    facts = materials_from_result(forward, material=example["material"], raw_annotation=checked,
                                  compiled_annotation=compiled, mapping=mapping)
    engine = DemandEngine(facts, Task.model_validate(example["material"]["task"]), facts.annotation,
        joint_demands(facts.annotation), build_demand_target_index(facts.cfg, checked))
    answer = engine.solve()
    assert answer == engine.solve(queue_order="lifo")
    return engine, answer


def find_example(fixtures, name):
    return next(example for example in fixtures if example["name"] == name)


def test_four_independent_frozen_candidates_compile_without_mutation(fixtures):
    assert len(fixtures) == 4
    assert [example["stage"] for example in fixtures].count("annotation") == 2
    assert [example["stage"] for example in fixtures].count("review") == 2
    before = canonical_sha256(fixtures)
    for example in fixtures:
        checked, _, _ = compile_response(example["reference"], example["material"])
        assert checked["task_revision_id"] == example["material"]["task"]["task_sha256"]
        if example["stage"] == "review":
            prepared = prepare_review_material(example["material"], example["reference"])
            validate_review(example["reference_response"], prepared)
    assert canonical_sha256(fixtures) == before
    assert canonical_sha256(endpoint_validation_fixtures()) == before


def test_actual_prompts_are_english_and_exclude_external_acceptance(fixtures):
    for example in fixtures:
        material = example["material"] if example["stage"] == "annotation" else prepare_review_material(example["material"], example["reference"])
        prompt = (annotation_prompt if example["stage"] == "annotation" else review_prompt)(material)
        assert not re.search(r"[\u4e00-\u9fff]", prompt)
        section = re.search(
            r"<!-- SKILLFLOW_PROMPT:INPUT:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:INPUT:END -->", prompt, re.S).group(1)
        actual_input = json.JSONDecoder().raw_decode(section[section.index("{"):])[0]
        serialized = json.dumps(actual_input)
        assert not any('"' + key + '"' in serialized for key in (
            "reference_response", "semantic_checks", "expected_findings", "expected_relations"))
        source = json.dumps(example["material"]["source"])
        assert not any(word in source for word in ("calibration_packet", "badge", "offset", "loan_form", "parking_envelope"))


def test_endpoint_reference_retains_distinct_receiver_and_append_demands(fixtures):
    engine, answer = solve(find_example(fixtures, "annotation_ceramic_dispatch"))
    assert answer["status"] == "complete"
    receiver_rows = []
    for sink in answer["sinks"]:
        if sink["boundary"]["sink_type"] not in {"external_tool", "storage_write"}:
            continue
        rows = [answer["derivations"][key] for key in sink["demanded_information"] + sink["conservative_retention"]]
        direct = [row for row in rows if row["node"]["kind"] == "op_input" and not row["conservative"] and row["property"] == "value"]
        receiver_rows.extend(direct)
    assert receiver_rows
    by_target = {}
    for row in receiver_rows:
        operation = engine.ops[row["node"]["operation_id"]]
        by_target.setdefault(operation["spec"]["target"], set()).add(tuple(row["path"]))
    assert by_target == {"stamp": {()}, "dispatch": {("glaze",), ("batches",)}, "ledger": {()}}
    read_spec = find_example(fixtures, "annotation_ceramic_dispatch")["reference"]["ir_semantics"]["ir_batch_read"]
    assert not read_spec["events"][0]["events"][0]["atomic_ops"][0].get("demands")


def test_whole_value_opaque_and_true_return_are_legitimate_controls(fixtures):
    for name in ("annotation_folio_return", "review_custody_release"):
        engine, answer = solve(find_example(fixtures, name))
        assert answer["status"] == "complete"
        tools = [sink for sink in answer["sinks"] if sink["boundary"]["sink_type"] == "external_tool"]
        assert tools
        assert any(answer["derivations"][key]["property"] == "value" and answer["derivations"][key]["path"] == []
                   for sink in tools for key in sink["demanded_information"])
    negative = find_example(fixtures, "review_voucher_delivery")
    engine, answer = solve(negative)
    tool_sink = next(sink for sink in answer["sinks"] if sink["boundary"]["sink_type"] == "external_tool")
    endpoint = [answer["derivations"][key] for key in tool_sink["demanded_information"] + tool_sink["conservative_retention"]
                if answer["derivations"][key]["node"]["kind"] == "op_input"]
    assert endpoint and {row["property"] for row in endpoint} == {"shape"}
    assert not any(row["property"] == "value" for row in endpoint)


def test_negative_review_uses_real_goal_and_parent_but_real_cfg_evidence(fixtures):
    example = find_example(fixtures, "review_voucher_delivery")
    material = prepare_review_material(example["material"], example["reference"])
    response = example["reference_response"]
    assert len(response["findings"]) == 2
    assert all(item["domain"] == "annotation" for item in response["findings"])
    assert response["requirement_checks"][0]["finding_indexes"] == [0, 1]
    issue_goals = [item for item in response["declaration_checks"] if item["status"] == "issue"]
    assert [item["raw_pointer"] for item in issue_goals] == [example["expected_relations"]["broad_read_goal"]]
    assert all(item["finding_indexes"] == [] for item in response["declaration_checks"] if item["status"] == "accepted")
    malformed = deepcopy(response)
    malformed["findings"][1]["evidences"][1]["target"] = {
        "instruction_id": "ir_voucher_send", "path": ["events", 1, "events", 0, "atomic_ops", 0]}
    with pytest.raises(StructuralValidationError) as error:
        validate_review(malformed, material)
    assert any(diagnostic["path"] == "/findings/1/evidences/1/target" for diagnostic in error.value.diagnostics)
