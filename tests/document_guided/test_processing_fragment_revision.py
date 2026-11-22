"""A semantic repair can only change the processing slots it was given."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragment_revision import (
    merge_processing_revision, merge_sensitivity_revision, processing_scope, sensitivity_scope,
)
from skillflow.document_guided.fragments import validate_fragment
from skillflow.propagation.contracts.limitations import validation_gap
from tests.document_guided.test_processing_finite_slots import inputs


def test_revision_follows_real_data_consumers_and_keeps_independent_records():
    material, prior, _ = inputs()
    old = material["cfg"]
    new = deepcopy(old)
    block = next(iter(new["blocks"].values()))
    block["instructions"][0]["inputs"][0]["literal_value"] = "changed query"
    # This old IR and its private gap disappear because the accepted new CFG
    # no longer contains their owner.
    block["instructions"] = [ir for ir in block["instructions"] if ir["id"] != "ir_unfilled"]
    prior["processing_gaps"].append({**prior["processing_gaps"][0], "instruction_id": "ir_unfilled"})
    findings = [{"target_ids": ["fragment:processing:/ir_semantics/ir_other_call/output_bindings/0",
                                "annotation:/locations/service"]}]
    scope = processing_scope(old, new, findings, prior)
    assert set(scope["slots"]) == {"ir_call", "ir_return", "ir_other_call"}
    assert scope["removed_instruction_ids"] == ["ir_unfilled"]
    assert scope["unresolved_targets"] == ["annotation:/locations/service"]
    assert scope["slots"]["ir_call"]["changed_cfg"] and not scope["slots"]["ir_return"]["changed_cfg"]

    patches = {"coverage_slots": [{"instruction_id": ir, **({"keep": "modeled"} if ir != "ir_call" else
        {"modeled": prior["ir_semantics"][ir]})} for ir in scope["slots"]]}
    wrong = deepcopy(patches)
    wrong["coverage_slots"][0] = {"instruction_id": "ir_call", "keep": "modeled"}
    with pytest.raises(StructuralValidationError, match="changed CFG slot"):
        merge_processing_revision(prior, scope, wrong)
    merged = merge_processing_revision(prior, scope, patches)
    assert merged["locations"] == prior["locations"]
    assert merged["ir_semantics"]["ir_unaffected"] == prior["ir_semantics"]["ir_unaffected"]
    assert not any(gap["instruction_id"] == "ir_unfilled" for gap in merged["processing_gaps"])
    assert set(merged["ir_semantics"]) == set(prior["ir_semantics"]) - {"ir_unfilled"}
    assert validate_fragment("processing", merged, {**material, "cfg": new}) == merged


def test_scoped_revision_requires_each_slot_and_rejects_unrelated_patch_or_stale_material():
    material, prior, _ = inputs()
    cfg = material["cfg"]
    findings = [{"target_ids": ["annotation:/ir_semantics/ir_call/output_bindings/0"]}]
    scope = processing_scope(cfg, cfg, findings, prior)
    assert set(scope["slots"]) == {"ir_call"}
    with pytest.raises(StructuralValidationError) as incomplete:
        merge_processing_revision(prior, scope, {"coverage_slots": []})
    assert [row["path"] for row in incomplete.value.diagnostics] == ["/ir_semantics/ir_call"]
    for patch in ({"coverage_slots": [{"instruction_id": "ir_unaffected", "keep": "modeled"}]},
                  {"coverage_slots": [], "locations": {}},
                  {"coverage_slots": [{"instruction_id": "ir_call", "keep": "modeled"}] * 2}):
        with pytest.raises(StructuralValidationError):
            merge_processing_revision(prior, scope, patch)
    with pytest.raises(ValueError, match="exact prior"):
        merge_processing_revision({**prior, "processing_gaps": []}, scope, {"coverage_slots": []})


def test_revision_keeps_only_unaffected_validation_gaps_and_refuses_changed_shared_location():
    material, prior, _ = inputs()
    old = material["cfg"]
    path = {"instruction_id": "ir_call", "side": "input", "index": 0}
    prior["locations"]["service"]["operand_refs"] = [path]
    new = deepcopy(old)
    next(iter(new["blocks"].values()))["instructions"][0]["inputs"][0]["literal_value"] = "different address"
    assert processing_scope(old, new, [], prior) is None
    prior["locations"]["service"].pop("operand_refs")
    gap = lambda ir: validation_gap(ir, [{"code": "example", "path": "/", "message": "A recorded validation barrier."}])
    fixed = [gap("ir_call"), gap("ir_unaffected")]
    scope = processing_scope(old, new, [], prior, validation_gaps=fixed)
    assert scope["retained_validation_gaps"] == [fixed[-1]]


def test_revision_can_keep_one_existing_source_gap_without_inventing_an_ir_record():
    material, prior, _ = inputs()
    cfg = material["cfg"]
    del prior["ir_semantics"]["ir_return"]
    prior["processing_gaps"][0]["unmodeled"] = True
    scope = processing_scope(cfg, cfg, [{"target_ids": ["annotation:/processing_gaps/0"]}], prior)
    patch = {"coverage_slots": [{"instruction_id": "ir_return", "keep": "unmodeled"}]}
    assert merge_processing_revision(prior, scope, patch) == prior


def _declaration(ir):
    return {"instruction_id": ir, "label": "Report", "value": {"kind": "local", "name": "reply"}}


def test_sensitivity_reuses_unchanged_declarations_and_asks_only_changed_or_reviewed_ir():
    material, old, _ = inputs()
    cfg = material["cfg"]
    prior = {"declarations": [_declaration(ir) for ir in ("ir_call", "ir_unaffected", "ir_unfilled")]}
    assert validate_fragment("sensitivity", prior, material, old) == prior
    no_change = sensitivity_scope(cfg, cfg, old, old, [], prior)
    assert no_change["slots"] == {} and merge_sensitivity_revision(prior, no_change, {"slots": []}) == prior

    new = deepcopy(old)
    new["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["output"] = "renamed_reply"
    new["ir_semantics"]["ir_call"]["output_bindings"][0]["value"]["name"] = "renamed_reply"
    del new["ir_semantics"]["ir_unfilled"]
    new["processing_gaps"].append({**new["processing_gaps"][0], "instruction_id": "ir_unfilled", "unmodeled": True})
    findings = [{"domain": "annotation", "owner": "sensitivity",
        "target_ids": ["annotation:/ir_semantics/ir_other_call/sensitivity"]}]
    scope = sensitivity_scope(cfg, cfg, old, new, findings, prior)
    assert set(scope["slots"]) == {"ir_call", "ir_other_call", "ir_return"}
    assert scope["removed_instruction_ids"] == ["ir_unfilled"]
    fixed = _declaration("ir_call")
    fixed["value"]["name"] = "renamed_reply"
    expected = {"declarations": [fixed, prior["declarations"][1], _declaration("ir_other_call")]}
    patch = {"slots": [{"instruction_id": "ir_call", "declarations": [fixed]},
                       {"instruction_id": "ir_other_call", "declarations": [_declaration("ir_other_call")]},
                       {"instruction_id": "ir_return", "declarations": []}]}
    actual = merge_sensitivity_revision(prior, scope, patch)
    assert actual == expected
    assert validate_fragment("sensitivity", actual, material, new) == expected

    for record in ({"instruction_id": "ir_unaffected", "declarations": []},
                   {"instruction_id": "ir_call", "declarations": [_declaration("ir_unaffected")]},
                   patch["slots"][0]):
        with pytest.raises(StructuralValidationError):
            merge_sensitivity_revision(prior, scope, {"slots": [*patch["slots"], record]})


def test_sensitivity_read_is_tied_to_possible_written_location():
    material, old, _ = inputs()
    cfg = material["cfg"]
    for location in ("first", "second"):
        old["locations"][location] = {"kind": "storage", "name": location}
    def declare(ir, operation):
        old["ir_semantics"][ir]["segments"] = [{"ops": [operation]}]
    declare("ir_call", {"op": "write", "target": "first", "input": {"kind": "input", "index": 0}})
    declare("ir_other_call", {"op": "read", "location": "first", "output": "reply"})
    declare("ir_unaffected", {"op": "read", "location": "second", "output": "reply"})
    new = deepcopy(old)
    new["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["input"] = {"kind": "literal", "value": "new write"}
    scope = sensitivity_scope(cfg, cfg, old, new, [], {"declarations": []})
    assert "ir_other_call" in scope["slots"]
    assert "ir_unaffected" not in scope["slots"]
