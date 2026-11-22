"""Concrete all-input edit coordinates, property-aware recipes and retrieval limits."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_results import validate_result_references
from skillflow.doe.input_locations import assessed_modification, record_use_suffix
from skillflow.doe.input_report import render_input_edits
from tests.doe.test_demand_engine import fixture, inp, literal, evidence
from tests.doe.test_reviewed_input_necessity import compute, rule, row, solve, assessed, operation_key, receipt


def test_nonsensitive_whole_slot_and_remainder_have_distinct_real_edit_recipes():
    def source_evidence(prepared, raw, ev):
        raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]["evidences"] = [evidence()]
    values = fixture([compute([inp(), literal({"extra": 3})], [rule([], [row(0, ["body"]), row(1)])])], custom=source_evidence)
    engine, result = solve(values)
    key = operation_key(engine)
    whole = assessed(result, key, 1)
    decision = next(r for r in whole["ranges"] if r["status"] == "deletable")
    assert decision["modification"]["kind"] == "remove_input"
    assert whole["location"]["raw_annotation_sites"][0]["pointer"].endswith("/atomic_ops/0/inputs/1")
    assert whole["location"]["source_resolution"] in {"direct_span", "inherited_span"}
    assert all(set(s) == {"file", "start_line", "end_line", "evidence_origin"} for s in whole["location"]["source_spans"])
    retained = assessed(result, key, 0)
    remainder = next(r for r in retained["ranges"] if r["status"] == "deletable" and r["excluded_paths"])
    assert remainder["modification"]["kind"] == "keep_ranges"
    assert remainder["modification"]["retained_information"] == [{"property": "value", "path": ["body"], "excluded_paths": []}]
    html = render_input_edits(result["input_assessments"])
    assert "remove_input" in html and "keep_ranges" in html and "Actual locations" in html
    assert "skill/SKILL.md" in html and "/atomic_ops/0/inputs/1" in html


@pytest.mark.parametrize("tamper", ["cfg", "source", "recipe", "wire"])
def test_saved_edit_recipes_and_locations_are_rederived_from_bound_material(tamper):
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    _, result = solve(values)
    changed = deepcopy(result)
    item = next(a for a in changed["input_assessments"] if a["node_kind"] == "op_input"
                and any(r["status"] == "deletable" for r in a["ranges"]))
    if tamper == "cfg":
        item["location"]["cfg_pointer"] += "/invented"
    elif tamper == "source":
        item["location"]["source_spans"].append({"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "evidence_origin": "direct"})
    elif tamper == "wire":
        item["location"]["wire_annotation_sites"].append({"pointer": "/invented", "role": "actual_input"})
    else:
        next(r for r in item["ranges"] if r["status"] == "deletable")["modification"]["kind"] = "remove_input"
    with pytest.raises(ValueError, match="modification or location"):
        validate_result_references(changed, values[0], values[3], input_contract_review=receipt(values))


def test_field_and_member_edits_do_not_alias_whole_slot_removal_or_reindex_arrays():
    assessment = {"node_kind": "op_input", "ranges": []}
    deletion = {"status": "deletable", "path": ["extra"], "excluded_paths": []}
    assert assessed_modification(assessment, deletion)[0]["kind"] == "exclude_field"
    for path in ([0], [{"kind": "each"}]):
        edit, limit = assessed_modification(assessment, {**deletion, "path": path})
        assert edit is None and "reindexing" in limit
    complement = {**deletion, "path": [], "excluded_paths": [[2, "name"]]}
    edit, limit = assessed_modification(assessment, complement)
    assert edit is None and "cardinality" in limit
    assessment["ranges"] = [{"status": "required", "property": "cardinality", "path": [], "excluded_paths": []}]
    assert assessed_modification(assessment, complement)[0]["retained_information"][0]["property"] == "cardinality"


def test_conditional_member_locations_follow_recorded_slot_mapping():
    op = {"op": "build", "parts": [{"when": literal(False), "value": literal("inactive")}, {"value": literal("kept")}]}
    record = {"members": [{"when_input_index": 0, "value_input_index": None}, {"when_input_index": None, "value_input_index": 1}]}
    assert record_use_suffix(op, record, 0) == ["parts", 0, "when"]
    assert record_use_suffix(op, record, 1) == ["parts", 1, "value"]
    assert record_use_suffix({"op": "deliver", "inputs": [literal("absent payload")], "when": literal(False)},
                             {"when_input_index": 0}, 0) == ["when"]


def test_field_name_literal_without_metadata_binding_is_local_unresolved_not_deletable():
    def extra_input(cfg):
        ir = next(i for b in cfg["blocks"].values() for i in b["instructions"] if i["id"] == "ir_filter")
        ir["inputs"].append({"type": "literal", "literal_value": "body"})
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "answer"}], graph_change=extra_input)
    _, result = solve(values)
    item = next(a for a in result["input_assessments"] if a["node_kind"] == "ir_input"
                and a["instruction_id"] == "ir_filter" and a["input_index"] == 1)
    assert {r["status"] for r in item["ranges"]} == {"unresolved"}
    assert "operand-to-location/path/selector" in item["ranges"][0]["reason"]
    assert item["location"]["cfg_pointer"].endswith("/inputs/1")
    assert not any(d["code"] == "input_metadata_binding" for d in result["diagnostics"])


@pytest.mark.parametrize("binding", [True, False])
def test_read_resource_identity_is_retained_only_through_exact_location_binding(binding):
    def location_binding(prepared, raw, ev):
        if not binding:
            for location in raw["locations"].values():
                location["operand_refs"] = [r for r in location["operand_refs"] if r["instruction_id"] != "ir_read"]
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "answer"}], custom=location_binding)
    _, result = solve(values)
    item = next(a for a in result["input_assessments"] if a["node_kind"] == "ir_input" and a["instruction_id"] == "ir_read")
    assert not any(r["status"] == "deletable" for r in item["ranges"])
    assert {r["status"] for r in item["ranges"]} == ({"required"} if binding else {"unresolved"})
    if binding:
        assert any("required_location_identity" in r["reason"] for r in item["ranges"])
        assert item["location"]["metadata_binding_sites"]


def flat_values(*, projection=False, output_path=("items",)):
    from tests.document_guided.test_input_contract_completeness import call_sample
    from skillflow.document_guided.annotation_wire import compile_flat_response
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.annotation.binding_examples import evidence
    from skillflow.propagation.solver import propagate
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.contracts.task import Task
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    material, wire = call_sample()
    call = wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]
    call["demands"][0]["path"] = list(output_path)
    if projection:
        call["input_contract"]["acquisition_projections"] = [{"selection_input_index": 0,
            "selection_parameter_path": ["fields"], "returned_range": {"property": "value", "path": ["items"]},
            "reason": "The source interface permits selecting the exact items range through the optional fields parameter.",
            "evidences": [evidence()]}]
    _, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    return (facts, Task.model_validate(material["task"]), facts.annotation,
            build_demand_target_index(facts.cfg, raw)), wire


@pytest.mark.parametrize("projection,output_path,selected", [(False, ("items",), False),
    (True, ("items",), True), (True, ("items", "title"), False)])
def test_acquisition_projection_requires_exact_reviewed_pair_range_and_real_request_operand(projection, output_path, selected):
    from skillflow.doe.sensitivity_material import joint_demands
    values, wire = flat_values(projection=projection, output_path=output_path)
    before = deepcopy((values[0].records, wire))
    _, result = solve(values, requested=joint_demands(values[2]))
    acquired = next(a for a in result["input_assessments"] if a["node_kind"] == "acquisition_output")
    relation = acquired["retrieval_projection"]
    assert relation["status"] == ("established" if projection else "unestablished")
    if projection:
        capability = relation["capabilities"][0]
        assert (capability["selected_supported_range"] is not None) == selected
        assert capability["request_operand_location"]["pointer"].endswith("/inputs/0")
        assert capability["selection_parameter_path"] == ["fields"]
        assert capability["response"]["raw_path"] != capability["request"]["raw_path"]
    for decision in acquired["ranges"]:
        if decision["status"] == "deletable" and decision["modification"]:
            assert decision["modification"]["kind"] == "omit_result_range_at_use"
    assert (values[0].records, wire) == before
