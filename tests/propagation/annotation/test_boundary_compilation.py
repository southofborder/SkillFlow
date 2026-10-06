"""Observation compilation owns sink identity, without another model call."""
from copy import deepcopy

import pytest

from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.compiler import COMPILER_VERSION
from skillflow.propagation.annotation.services import validate_compiled_response
from skillflow.propagation.annotation.services import to_payload
from tests.propagation.annotation.helpers import material, valid_raw_response


def default_read():
    prepared = material()
    response = valid_raw_response(prepared)
    response["transfer_specs"]["ir_read"]["events"][0]["mode"] = "default"
    return prepared, response


def test_generated_observation_carries_fixed_attributes_and_sink_without_role_rewrite():
    prepared, raw = default_read()
    before = deepcopy(raw)
    checked, compiled, mapping = compile_response(raw, prepared)
    assert checked == before and raw == before
    assert COMPILER_VERSION == "skillflow-processing-compiler-v4"
    assert mapping["schema_version"] == "skillflow-processing-compilation-v4"
    sink = compiled["sink_boundaries"]
    assert len(sink) == 1 and sink[0]["instruction_id"] == "ir_read"
    assert sink[0]["sink_type"] == "model_observe" and sink[0]["exposure_level"] == 2
    assert compiled["locations"][sink[0]["target"]]["access_scope"] == "recipient"
    assert compiled["locations"][sink[0]["target"]]["retention"] is None
    assert compiled["profiles"]["ir_read"]["roles"] == raw["profiles"]["ir_read"]["roles"] == ["source"]
    assert to_payload(compiled)["sink_boundaries"] == sink


@pytest.mark.parametrize("mutation", [
    lambda value: value["sink_boundaries"].clear(),
    lambda value: value["sink_boundaries"][0].update(target="ir_read_boundary_0"),
    lambda value: value["sink_boundaries"][0].update(exposure_level=3),
    lambda value: value["sink_boundaries"].append(deepcopy(value["sink_boundaries"][0])),
])
def test_compiled_sink_table_is_not_trusted_as_free_form_input(mutation):
    prepared, raw = default_read()
    compiled = compile_response(raw, prepared)[1]
    mutation(compiled)
    with pytest.raises(ValueError):
        validate_compiled_response(compiled, prepared)


def test_existing_model_identity_with_conflicting_attributes_is_not_overwritten():
    prepared, raw = default_read()
    raw["locations"]["known_model"] = {"kind": "model_context", "name": "当前模型处理上下文",
        "operand_refs": [], "access_scope": "public", "retention": None}
    raw["location_evidences"]["known_model"] = deepcopy(raw["location_evidences"]["ir_read_boundary_0"])
    before = deepcopy(raw)
    with pytest.raises(ValueError, match="attributes conflict"):
        compile_response(raw, prepared)
    assert raw == before
