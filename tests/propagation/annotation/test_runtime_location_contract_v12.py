"""Finite runtime vocabulary and explicit address identity, without model calls."""
from copy import deepcopy
import json

import pytest
from pydantic import TypeAdapter

from skillflow.document_guided.annotation_wire import FlatAtomicOp, FlatLocation
from skillflow.propagation.contracts.locations import address_is_unknown, locations_may_alias
from skillflow.propagation.contracts.profiles import AnnotationResponse
from skillflow.propagation.contracts.demand import DemandExpression
from skillflow.propagation.contracts.runtime_contract import runtime_contract, validate_runtime_contract
from skillflow.propagation.contracts.specs import AtomicOp, RawAtomicOp, LocationSpec


SOURCE = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
          "reason": "The source selects this address from the caller."}


def location(**changes):
    return {"kind": "runtime_context", "name": "protected_call.exception", "operand_refs": [],
            "access_scope": "task", "retention": "task", **changes}


@pytest.mark.parametrize("kind", ["runtime_context", "storage", "remote", "tool", "model_context", "user"])
def test_location_names_do_not_infer_aliases(kind):
    exact = {"kind": kind, "name": "symbolic:unknown payload", "address_kind": "identified"}
    unrelated = {"kind": kind, "name": "caller.argument"}
    assert not address_is_unknown(exact)
    assert not locations_may_alias(exact, unrelated)
    assert locations_may_alias(exact, dict(exact))


@pytest.mark.parametrize("cls", [LocationSpec, FlatLocation])
def test_ambiguous_legacy_names_are_rejected_without_reinterpretation(cls):
    value = location(name="symbolic:old source")
    if cls is FlatLocation:
        value["evidences"] = [SOURCE]
    with pytest.raises(ValueError, match="requires explicit address_kind"):
        cls.model_validate(value)
    value["address_kind"] = "identified"
    checked = cls.model_validate(value)
    assert checked.model_dump(mode="json")["address_kind"] == "identified"
    assert cls.model_validate(checked.model_dump(mode="json")) == checked


@pytest.mark.parametrize("change", [
    {"address_kind": "unknown"}, {"address_kind": True},
    {"address_kind": "unidentified"},
    {"address_kind": "unidentified", "address_reason": " "},
    {"address_kind": "identified", "address_reason": "Content is unknown"},
])
def test_address_policy_requires_typed_specific_uncertainty(change):
    with pytest.raises(ValueError):
        LocationSpec.model_validate(location(**change))


def test_unidentified_address_needs_physical_evidence_and_roundtrips():
    value = location(address_kind="unidentified", address_reason="The caller supplies the storage key.")
    with pytest.raises(ValueError, match="physical source evidence"):
        FlatLocation.model_validate({**value, "evidences": [{"rule_id": "EM08"}]})
    checked = FlatLocation.model_validate({**value, "evidences": [SOURCE]})
    encoded = checked.model_dump(mode="json")
    assert encoded["address_kind"] == "unidentified"
    assert encoded["address_reason"] == value["address_reason"]
    assert address_is_unknown(LocationSpec.model_validate({k: v for k, v in encoded.items() if k != "evidences"}))


def test_unidentified_aliases_are_symmetric_and_kind_scoped():
    unknown = location(address_kind="unidentified", address_reason="A runtime-selected context key.")
    exact = location(name="caller.urls")
    other = {**exact, "kind": "storage"}
    assert locations_may_alias(exact, unknown)
    assert locations_may_alias(unknown, exact)
    assert not locations_may_alias(unknown, other)


def test_location_schema_exposes_explicit_policy_and_known_default():
    for cls in [LocationSpec, FlatLocation]:
        props = cls.model_json_schema()["properties"]
        assert props["address_kind"]["enum"] == ["identified", "unidentified"]
        assert props["address_kind"]["default"] == "identified"
        assert "address_reason" in props
    # Exact ordinary declarations retain the compact public representation.
    assert "address_kind" not in LocationSpec.model_validate(location()).model_dump(mode="json")


def test_runtime_inventory_exactly_covers_supported_operation_schemas():
    inventory = runtime_contract()["operation_contract"]
    rows = inventory["rows"]
    assert all(len(row) == len(inventory["columns"]) for row in rows)
    assert len({row[0] for row in rows}) == len(rows)
    names = {row[0] for row in rows if row[1] == "atomic"}
    for annotation in [AtomicOp, RawAtomicOp]:
        assert names == set(TypeAdapter(annotation).json_schema()["discriminator"]["mapping"])
    wire = {row[0] for row in rows if row[1] in {"atomic", "wire"}}
    assert wire == set(TypeAdapter(FlatAtomicOp).json_schema()["discriminator"]["mapping"])
    assert {row[0] for row in rows if row[1] == "structure"} == {"processing", "for_each", "cases"}
    assert set(inventory["common"]) == {"evidence", "failure", "schema", "selectors"}
    assert "different order or overlapping domains" in inventory["common"]["selectors"]
    historical = runtime_contract(version="skillflow-abstract-runtime-v12")["operation_contract"]
    assert set(historical["common"]) == {"evidence", "failure", "schema"}
    assert set(inventory["expression_operators"]) == set(TypeAdapter(DemandExpression).json_schema()["discriminator"]["mapping"])
    assert all(all(isinstance(cell, str) and cell.strip() for cell in row) for row in rows)
    assert len(json.dumps(inventory, ensure_ascii=False, separators=(",", ":"))) < 6500


@pytest.mark.parametrize("kind", ["identified", "unidentified"])
def test_compilation_preserves_declared_address_policy_and_source_provenance(kind):
    from tests.document_guided.test_annotation_wire import sample
    from skillflow.document_guided.annotation_wire import compile_flat_response
    material, wire = sample()
    declaration = wire["locations"]["service"]
    declaration.update(name="symbolic:literal source label", address_kind=kind)
    if kind == "unidentified":
        declaration["address_reason"] = "The cited caller selects the target identity."
    before = deepcopy(wire)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    assert saved == wire == before
    for candidate in [raw, compiled]:
        assert candidate["locations"]["service"]["address_kind"] == kind
        assert candidate["location_evidences"]["service"] == declaration["evidences"]
    assert raw["locations"]["service"].get("address_reason") == declaration.get("address_reason")
    assert mapping["wire_paths"]["/locations/service"] == "/locations/service"


@pytest.mark.parametrize("change", [
    lambda x: x.update(version="skillflow-abstract-runtime-v11"),
    lambda x: x.pop("operation_contract"),
    lambda x: x["operation_contract"]["rows"].pop(),
    lambda x: x["operation_contract"]["rows"][0].__setitem__(4, "all inputs alias"),
    lambda x: x["operation_contract"]["common"].update(failure="ignore errors"),
])
def test_old_or_incomplete_runtime_inventory_cannot_be_substituted(change):
    current = runtime_contract()
    changed = deepcopy(current)
    change(changed)
    with pytest.raises(ValueError, match="identity mismatch"):
        validate_runtime_contract(changed)
    assert validate_runtime_contract(current) == current


def test_response_requires_address_evidence_after_flat_compilation():
    # Exercise the response-level provenance obligation independently of the
    # compact wire validator, using an otherwise valid authored response.
    from tests.propagation.annotation.helpers import material, valid_response
    prepared = material()
    value = valid_response(prepared)
    key = next(iter(value["locations"]))
    value["locations"][key].update(address_kind="unidentified", address_reason="The source selects a runtime address.")
    value["location_evidences"][key] = [{"rule_id": "EM08", "reason": "This is only a default rule."}]
    with pytest.raises(ValueError, match="physical source evidence"):
        AnnotationResponse.model_validate(value)
