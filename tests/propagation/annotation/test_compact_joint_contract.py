from tests.propagation.annotation.helpers import prepare_material
"""Focused regressions for the single-IR semantics and request reading view."""
from copy import deepcopy

import pytest
from pydantic import TypeAdapter, ValidationError

from skillflow.propagation.contracts.evidence import SpecEvidence
from skillflow.propagation.contracts.specs import (
    EffectSpec, RawEffectSpec, RawIRSemantics, iter_spec_evidence,
)
from skillflow.propagation.contracts.paths import (
    semantics_path, processing_segment_path, split_semantics_path,
    element_scope_path, compiled_event_position,
)
from skillflow.propagation.material import (
    model_material, evidence_reference, compact_schema,
)
from tests.propagation.annotation.helpers import graph, source_bundle, valid_raw_response


def material():
    return prepare_material(source_bundle(), graph())


def evidence():
    return {"rule_id": "EM01", "reason": "The identified contract default is applicable."}


def operation():
    return {"op": "compute", "inputs": [], "dependencies": [], "output": "out",
            "evidences": [evidence()]}


def test_event_occurrence_owns_its_effect_evidence():
    event = {"effect": "transform", "atomic_ops": [operation()], "evidences": [evidence()]}
    assert EffectSpec.model_validate(event).effect == "transform"
    with pytest.raises(ValidationError, match="own evidence"):
        EffectSpec.model_validate({key: value for key, value in event.items() if key != "evidences"})
    with pytest.raises(ValidationError):
        RawEffectSpec.model_validate({**event, "effect": "model_observe"})
    with pytest.raises(ValidationError):
        EffectSpec.model_validate({**event, "effect_index": 0})


def test_null_effect_does_not_claim_nonempty_effect_evidence():
    event = EffectSpec.model_validate({"effect": None, "evidences": [], "atomic_ops": [operation()]})
    assert "evidences" not in event.model_dump(mode="json")
    with pytest.raises(ValidationError, match="null-effect"):
        EffectSpec.model_validate({"effect": None, "evidences": [evidence()], "atomic_ops": [operation()]})


def test_empty_ir_requires_explicit_inapplicability_and_operator_coverage():
    value = {"operator": [], "operator_evidences": [{**evidence(), "value": None}],
             "order": "fixed", "events": [], "output_bindings": [], "sensitivity": []}
    with pytest.raises(ValidationError, match="empty_effect_evidences"):
        RawIRSemantics.model_validate(value)
    value["empty_effect_evidences"] = [evidence()]
    assert RawIRSemantics.model_validate(value).operator == []
    with pytest.raises(ValidationError, match="operator evidence"):
        RawIRSemantics.model_validate({**value, "operator": ["llm"]})
    with pytest.raises(ValidationError):
        RawIRSemantics.model_validate({**value, "roles": []})


def test_no_parallel_effect_list_or_legacy_evidence_fields():
    for legacy in ({"basis": "runtime_contract"}, {"quote": "text"}, {"effect_index": 0}):
        with pytest.raises(ValidationError):
            TypeAdapter(SpecEvidence).validate_python({**evidence(), **legacy})


def test_reference_registry_categories_are_not_inferred_from_prefixes():
    prepared = material()
    assert evidence_reference({"target": {"path": []}, "reason": "graph"}, prepared)["kind"] == "cfg"
    assert evidence_reference(evidence(), prepared)["kind"] == "runtime_contract"
    for old in ({"ref_id": "EM01", "reason": "old"}, {"rule_id": "REP01", "reason": "old"}):
        with pytest.raises(ValueError): evidence_reference(old, prepared)
    with pytest.raises(ValueError, match="does not exist"):
        evidence_reference({"rule_id": "EM999", "reason": "invented"}, prepared)


def test_short_view_has_one_source_copy_and_complete_cfg_targets():
    prepared = prepare_material(source_bundle("a\r\nb\n"), graph(), user_request="keep b")
    view = model_material(prepared)
    assert set(view) == {"source", "cfg", "runtime_contract", "user_request", "task"}
    assert set(prepared) == {"version", "source", "cfg", "runtime_contract", "user_request", "task"}
    assert "".join(view["source"]["files"][0]["lines"]) == "a\r\nb\n"
    assert {f["file"] for f in view["source"]["files"]} == {"skill/SKILL.md"}
    assert view["user_request"] == "keep b"
    assert all("sha256" not in f for f in view["source"]["files"])


def test_reference_expansion_is_deterministic_and_does_not_rewrite_literals():
    from skillflow.propagation.contracts.references import resolve_cfg_target
    prepared = material()
    target = {"instruction_id": "ir_read", "side": "output", "index": 0}
    assert resolve_cfg_target(target, prepared["cfg"]) == resolve_cfg_target(deepcopy(target), prepared["cfg"])
    with pytest.raises(ValueError):
        resolve_cfg_target({"path": ["blocks", "entry", "instructions", 0, "outputs", 0]}, prepared["cfg"])


def test_candidate_projection_roundtrip_preserves_claims_and_literal_reference_keys():
    from skillflow.propagation.annotation.services import compile_response
    prepared = material()
    raw = valid_raw_response(prepared)
    operation = raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]
    literal = {"target_id": "t0001", "ref_id": "g_0001"}
    operation["inputs"] = [{"kind": "literal", "value": literal}]
    normalized, _, _ = compile_response(raw, prepared)
    assert normalized["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]["inputs"][0]["value"] == literal


def test_evidence_resolution_serializes_only_the_requested_cfg_subtree(monkeypatch):
    import skillflow.propagation.material as module
    prepared = material()
    calls = []
    original = module.json.dumps
    def counted(value, **kwargs):
        calls.append(value)
        return original(value, **kwargs)
    monkeypatch.setattr(module.json, "dumps", counted)
    entry = evidence_reference({"target": {"instruction_id": "ir_read", "path": []}, "reason": "One claim."}, prepared)
    assert entry["kind"] == "cfg"
    assert len(calls) == 1 and calls[0]["id"] == "ir_read"


def test_compact_schema_retains_real_title_properties_and_literal_objects():
    source = {"title": "A schema", "type": "object", "properties": {
        "title": {"title": "Display label", "type": "string"},
        "value": {"const": {"title": "literal data"}},
    }, "required": ["title"]}
    compact = compact_schema(source)
    assert "title" not in compact
    assert compact["properties"]["title"] == {"type": "string"}
    assert compact["properties"]["value"]["const"] == {"title": "literal data"}
    assert compact["required"] == ["title"]


def test_semantics_paths_keep_processing_and_element_scope():
    path = semantics_path("ir", "events", 2, "body", 1, "events", 0, "atomic_ops", 3)
    assert split_semantics_path(path) == ("ir", path[2:])
    assert processing_segment_path(path) == semantics_path("ir", "events", 2, "body", 1)
    assert element_scope_path(path) == ["events", 2]
    assert compiled_event_position(semantics_path("ir", "events", 2, "body", 1)) == (2, 1)
    with pytest.raises(ValueError):
        split_semantics_path(["transfer_specs", "ir", "events", 0])


def test_compile_short_references_and_generated_goal_identity():
    from skillflow.propagation.annotation.services import compile_response
    prepared = material()
    raw = valid_raw_response(prepared)
    goal_target = {"instruction_id": "ir_return", "side": "input", "index": 0}
    raw["demands"] = [{"requirement_id": "R001", "target": goal_target, "preserve": "value", "reason": "Preserve the real result."}]
    raw["realizations"][0].update(status="expressed", gaps=[])
    normalized, compiled, mapping = compile_response(raw, prepared)
    assert normalized["demands"][0]["target"] == goal_target
    assert "id" not in normalized["demands"][0]
    assert compiled["demands"][0]["id"].startswith("goal_")
    assert compile_response(normalized, prepared) == (normalized, compiled, mapping)


def test_local_mode_cannot_use_only_a_default_rule_as_mechanism():
    from skillflow.propagation.annotation.services import validate_raw_response
    prepared = material()
    raw = valid_raw_response(prepared)
    raw["ir_semantics"]["ir_read"]["events"][0]["evidences"] = [evidence()]
    with pytest.raises(ValueError, match="source or CFG mechanism"):
        validate_raw_response(raw, prepared)


def test_compiled_observation_removes_only_compiled_empty_effect_claim():
    from skillflow.propagation.annotation.services import compile_response
    prepared = material()
    raw = valid_raw_response(prepared)
    spec = raw["ir_semantics"]["ir_filter"]
    segment = spec["events"][0]
    segment["mode"] = "default"
    event = segment["events"][0]
    event["effect"] = None
    event.pop("evidences")
    event["atomic_ops"][0]["dependencies"] = ["possible"]
    spec["empty_effect_evidences"] = [evidence()]
    original, compiled, _ = compile_response(raw, prepared)
    assert "empty_effect_evidences" in original["ir_semantics"]["ir_filter"]
    assert "empty_effect_evidences" not in compiled["ir_semantics"]["ir_filter"]
    assert compiled["ir_semantics"]["ir_filter"]["events"][0]["effect"] == "model_observe"
