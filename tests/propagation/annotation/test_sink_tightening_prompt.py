"""The annotation contract exposes parameters, not guessed transports or guards."""
import json
import re

import pytest
from pydantic import ValidationError

from skillflow.propagation.review.prompts import INSTRUCTIONS as REVIEW_INSTRUCTIONS
from skillflow.propagation.contracts.specs import BuildOp
from skillflow.propagation.contracts.specs import RawDeliverOp
from skillflow.propagation.contracts.runtime_contract import execution_model
from skillflow.propagation.contracts.representation_contract import representation_contract
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.annotation.prompts import INSTRUCTIONS
from skillflow.propagation.annotation.prompts import response_format_example
from skillflow.propagation.annotation.services import validate_response
from tests.propagation.annotation.helpers import material, valid_raw_response


def evidence():
    return {"basis": "source", "ref_id": "s_example", "quote": "original value",
            "reason": "原字段值与布尔控制分开，不将控制加入载荷。"}


def test_network_and_optional_request_decisions_are_shared_english_contracts():
    rules = {item["id"]: item["text"] for item in execution_model()["rules"]}
    assert "source, code, or interface establishes network transport" in rules["EM06"]
    assert "Conditions are control inputs, not request contents" in rules["EM14"]
    assert "actual input bindings" in rules["EM15"]
    assert "exactly the same ordered symbolic request references" in rules["EM15"]
    assert "sending verbs, recipient identifiers, executor labels" in INSTRUCTIONS
    assert "tool/recipient/null" in INSTRUCTIONS and "communication mechanism" in INSTRUCTIONS
    assert "has_since is not a member or delivered parameter" in INSTRUCTIONS
    assert "Both the actual deliver" in INSTRUCTIONS
    assert "never replace both with one opaque result" in INSTRUCTIONS
    assert "one syntactically complete JSON object with no trailing tokens" in INSTRUCTIONS
    assert "original field value separately" in REVIEW_INSTRUCTIONS
    assert "actual transport evidence" in REVIEW_INSTRUCTIONS
    assert not re.search(r"[\u3400-\u9fff]", INSTRUCTIONS + REVIEW_INSTRUCTIONS)
    assert all(not re.search(r"[\u3400-\u9fff]", rule) for rule in rules.values())
    assert {rule["id"] for rule in representation_contract()["rules"]} >= {"REP08", "REP09"}


def test_raw_schema_exposes_build_condition_but_not_observation_guard_or_sink_list():
    schema = RawAnnotationResponse.model_json_schema()
    assert "when" in schema["$defs"]["BuildMember"]["properties"]
    assert "when" not in schema["$defs"]["RawDeliverOp"]["properties"]
    assert "sink_boundaries" not in schema["properties"]
    assert "effect_index" in schema["$defs"]["RawEffectSpec"]["properties"]
    with pytest.raises(ValidationError):
        RawDeliverOp.model_validate({"op": "deliver", "inputs": [], "target": "tool",
            "when": {"kind": "literal", "value": False}, "evidences": [evidence()]})


def test_build_members_are_distinct_from_update_members_and_keep_original_refs():
    operation = BuildOp.model_validate({"op": "build", "container": "object", "parts": [
        {"path": ["query"], "value": {"kind": "input", "index": 0}},
        {"path": ["since"], "value": {"kind": "input", "index": 1},
         "when": {"kind": "input", "index": 2}},
    ], "output": "request", "evidences": [evidence()]})
    assert operation.parts[1].value.index == 1
    assert operation.parts[1].when.index == 2
    assert operation.parts[0].when is None
    from skillflow.propagation.contracts.specs import FieldValue
    with pytest.raises(ValidationError):
        FieldValue.model_validate({"path": ["since"], "value": {"kind": "input", "index": 1},
                                   "when": {"kind": "input", "index": 2}})


def test_complete_extra_brace_is_not_repaired_or_accepted_by_annotation_parser():
    prepared = material()
    encoded = json.dumps(valid_raw_response(prepared), ensure_ascii=False)
    with pytest.raises(ValueError):
        validate_response(encoded + "}", prepared)
    RawAnnotationResponse.model_validate(response_format_example())
