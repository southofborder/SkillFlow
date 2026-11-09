"""Offline scoped unknowns preserve real prefix facts and independent DOE work."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.limitations import (
    ProcessingGap, validation_gap, processing_impacts, gap_id, diagnostic_applies,
)
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.specs import validate_specs
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.solver import propagate
from skillflow.propagation.report import build_view
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.demand_results import validate_result_references
from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from tests.propagation.annotation.helpers import source_bundle, graph, valid_raw_response
from tests.doe.helpers import source_task


SOURCE = ("# Scoped static fixture\n"
          "Read the local configuration.\n"
          "One branch updates cache with an unsupported mechanism, then reads and publishes cache.\n"
          "An independent branch asks a model for the document body and returns that body.\n"
          "Configuration and cache token fields are confidential.\n")
CITATION = {"file": "skill/SKILL.md", "start_line": 3, "end_line": 3,
            "reason": "The synthetic source explicitly identifies the cache branch and its stated mechanism."}


def instruction(name, inputs=(), outputs=(), opcode="operation"):
    return {"id": name, "opcode": opcode, "inputs": list(inputs), "outputs": list(outputs),
            "constraints": [], "metadata": {}}


def result(name):
    return {"type": "result", "identifier": name}


def local(name):
    return {"kind": "local", "name": name}


def inp(index=0):
    return {"kind": "input", "index": index}


def segment(effect, op):
    evidence = {"file": "skill/SKILL.md", "start_line": 3, "end_line": 4,
                "reason": "The fixture declares the read or delivery explicitly."}
    return {"kind": "processing", "mode": "local", "returns": [], "evidences": [evidence],
            "events": [{"effect": effect, "evidences": [evidence], "atomic_ops": [{**op, "evidences": [evidence]}]}]}


def authored(*, shared_cache=False, gap=True, precision=False, validation=False, constraint=False):
    cfg = graph()
    read, filtered, returned = cfg["blocks"]["entry"]["instructions"]
    cfg["constraints"] = []
    cfg["blocks"]["entry"]["block_name"] = "Read configuration"
    dispatch = instruction("ir_dispatch", [{"type": "literal", "literal_value": True}], opcode="dispatch")
    cfg["blocks"]["entry"]["instructions"] = [read, dispatch]
    unknown = instruction("ir_unknown", [result("result_config")], [result("result_unknown")])
    late = instruction("ir_late", outputs=[result("result_late")])
    late_return = instruction("ir_late_return", [result("result_late")], opcode="return")
    if shared_cache:
        filtered["inputs"] = [result("result_cache")]
    for name, instructions in (("unknown", [unknown, late, late_return]), ("independent", [filtered, returned])):
        cfg["blocks"][name] = {"block_id": name, "block_name": name, "instructions": instructions,
                                "constraints": [], "data_source_kind": None}
    if shared_cache:
        cfg["blocks"]["independent"]["instructions"].insert(0, instruction("ir_cache", outputs=[result("result_cache")]))
    cfg["edges"] = [{"source_block_id": "entry", "target_block_id": name, "condition_text": None}
                    for name in ("unknown", "independent")]
    source_text = (SOURCE if gap and not precision else SOURCE.replace(
        "updates cache with an unsupported mechanism", "copies configuration unchanged"))
    if constraint:
        source_text = source_text.replace("asks a model", "asks a model at most once")
    source = source_bundle(source_text)
    evidence = {**CITATION, "start_line": 4, "end_line": 4,
                "reason": "The source requires the independent document body."}
    task = source_task(source, {"purpose": {"text": "Return the stated document body.", "evidences": [evidence]},
        "requirements": [{"id": "R", "text": "Return the document body after at most one model use." if constraint else "Return the document body.", "evidences": [evidence]}], "issues": []})
    material = prepare_material(source, cfg, task_baseline=task)
    raw = valid_raw_response(material)
    raw["realizations"] = [{"requirement_id": "R", "status": "expressed", "bindings": [], "gaps": []}]
    if constraint:
        raw["realizations"][0]["constraints"] = [{"kind": "at_most", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_filter", "path": []}], "limit": 1, "unit": "attempt"}]
    raw["demands"] = [{"requirement_id": "R", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
                       "preserve": "value", "reason": "Keep the explicitly required body."}]
    selected = raw["ir_semantics"]["ir_filter"]
    selected["operator"] = ["llm"]
    selected["operator_evidences"] = [{"value": "llm", "target": {"instruction_id": "ir_filter", "path": []},
                                          "reason": "The fixture source explicitly asks a model."}]
    selected["events"][0]["mode"] = "model"
    selected["events"][0]["events"][0]["atomic_ops"] = [
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "body", "evidences": [evidence]}]
    selected["output_bindings"][0]["value"] = local("body")
    selected["sensitivity"] = [{"value": inp(), "path": ["token"], "label": "credential", "evidences": [{
        **CITATION, "start_line": 5, "end_line": 5, "reason": "The source declares token confidentiality."}]}]
    cache_refs = []
    raw["locations"].update(cache={"kind": "runtime_context", "name": "cache", "operand_refs": cache_refs,
                                    "access_scope": "task", "retention": "task"},
                            user={"kind": "user", "name": "user", "operand_refs": [], "access_scope": "recipient", "retention": None})
    raw["location_evidences"].update(cache=[CITATION], user=[evidence])
    raw["ir_semantics"]["ir_late"].update(events=[segment("context_read", {"op": "read", "location": "cache", "output": "old"})],
        output_bindings=[{"output_index": 0, "value": local("old"), "evidences": [evidence]}])
    raw["ir_semantics"]["ir_late"].pop("empty_effect_evidences", None)
    if shared_cache:
        raw["ir_semantics"]["ir_cache"].update(events=[segment("context_read", {"op": "read", "location": "cache", "output": "cached"})],
            output_bindings=[{"output_index": 0, "value": local("cached"), "evidences": [evidence]}])
        raw["ir_semantics"]["ir_cache"].pop("empty_effect_evidences", None)
    raw["ir_semantics"]["ir_late_return"].update(events=[segment("user_output", {"op": "deliver", "inputs": [inp()], "target": "user"})])
    raw["ir_semantics"]["ir_late_return"].pop("empty_effect_evidences", None)
    if gap:
        ir = "ir_filter" if precision else "ir_unknown"
        item = {"instruction_id": ir, "reason": "The source mechanism has an unsupported relation.",
                "evidences": [evidence if precision else CITATION], "unmodeled": not precision, "outputs": [0],
                "locations": [] if precision else ["cache"]}
        if validation:
            item = validation_gap(ir, [{"code": "fixture_schema", "path": "/semantics/ir_filter",
                                       "message": "The fixture semantic fragment has an invalid field."}], unmodeled=not precision)
        raw["processing_gaps"] = [item]
        if not precision:
            raw["ir_semantics"].pop("ir_unknown")
    return material, deepcopy(raw)


def analyze(**options):
    material, raw = authored(**options)
    raw, compiled, mapping = compile_response(raw, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled, mapping=mapping)
    review = prepare_sensitivity_review(facts, annotation=facts.annotation)
    return material, raw, compiled, solved, facts, review


def model_rows(review):
    return [row for sink in review.to_dict()["sinks"] if sink["boundary"]["instruction_id"] == "ir_filter"
            for row in sink["data_reviews"]]


def test_unmodeled_barrier_preserves_prefix_and_independent_positive_doe_without_stale_cache_read():
    _, _, _, solved, facts, review = analyze()
    assert solved.status == "incomplete"
    assert solved.coverage == {"ir_read": "processed", "ir_dispatch": "processed", "ir_unknown": "unmodeled", "ir_late": "blocked",
                              "ir_late_return": "blocked", "ir_filter": "processed", "ir_return": "processed"}
    assert set(facts.records) == {"ir_read", "ir_dispatch", "ir_filter", "ir_return"}
    assert model_rows(review) and {row["conclusion"] for row in model_rows(review)} == {"excess_supported"}
    assert not any(binding["location"]["name"] == "result_unknown" for record in facts.records.values()
                   for binding in record["exit_state"]["bindings"])
    assert all(row["instruction_id"] != "ir_late_return" for row in facts.sinks)
    assert any(row["boundary"]["instruction_id"] == "ir_late_return" and row["status"] == "unresolved"
               for row in facts.boundary_coverage)
    view = build_view(facts)
    assert view["processing_gaps"] and view["boundary_coverage"] == facts.boundary_coverage
    assert review.to_dict()["status"] == "partial"
    assert [row["instruction_id"] for row in review.to_dict()["coverage"]["unresolved_boundaries"]] == ["ir_late_return"]


def test_unknown_named_location_blocks_sibling_reader_even_without_cfg_path_from_unknown_branch():
    _, _, _, _, facts, review = analyze(shared_cache=True)
    assert model_rows(review) and {row["conclusion"] for row in model_rows(review)} == {"no_excess_established"}
    assert all(row["reduction"] is None and "unresolved" in row["reason"] for row in model_rows(review))
    limit = next(row for row in review.to_dict()["diagnostics"] if row["code"] == "processing_gap")
    assert "ir_filter" in limit["affected_instruction_ids"]
    assert "ir_read" not in limit["affected_instruction_ids"]
    assert facts.coverage["ir_filter"] == "processed"  # A possible old-state candidate is not certified complete.


@pytest.mark.parametrize("validation", [False, True])
def test_precision_limitation_retains_known_operations_but_never_certifies_the_affected_comparison(validation):
    _, raw, _, solved, _, review = analyze(precision=True, validation=validation)
    assert solved.status == "complete"
    assert set(solved.records.records_dict()) == set(solved.coverage)
    assert model_rows(review) and all(row["conclusion"] == "no_excess_established" for row in model_rows(review))
    assert raw["processing_gaps"][0]["unmodeled"] is False


def test_validation_barrier_has_real_program_errors_and_no_invented_source_or_output():
    _, raw, _, solved, _, review = analyze(validation=True)
    gap = raw["processing_gaps"][0]
    assert gap["origin"] == "validation" and not gap["evidences"] and gap["validation_errors"]
    assert solved.coverage["ir_unknown"] == "unmodeled"
    assert all(row["conclusion"] == "excess_supported" for row in model_rows(review))
    with pytest.raises(ValidationError):
        ProcessingGap.model_validate({**gap, "validation_errors": []})


def test_missing_semantics_requires_explicit_unmodeled_coverage_and_cannot_also_have_a_spec():
    material, raw = authored()
    absent = deepcopy(raw)
    absent.pop("processing_gaps")
    with pytest.raises(StructuralValidationError, match="Every actual IR"):
        compile_response(absent, material)
    overlap = deepcopy(raw)
    overlap["ir_semantics"]["ir_unknown"] = deepcopy(authored(gap=False)[1]["ir_semantics"]["ir_unknown"])
    with pytest.raises(StructuralValidationError, match="Every actual IR"):
        compile_response(overlap, material)
    with pytest.raises(ValidationError):
        ProcessingGap.model_validate({"instruction_id": "ir_unknown", "reason": "Unsupported.", "evidences": []})


def test_bad_gap_source_reference_or_output_footprint_is_rejected():
    material, raw = authored()
    raw["processing_gaps"][0]["outputs"] = [99]
    with pytest.raises(StructuralValidationError, match="absent CFG output"):
        compile_response(raw, material)
    raw["processing_gaps"][0]["outputs"] = [0]
    raw["processing_gaps"][0]["evidences"][0]["end_line"] = 999
    with pytest.raises(StructuralValidationError):
        compile_response(raw, material)


def test_saved_scoped_coverage_cannot_be_dropped_or_narrowed_to_make_affected_sink_excess():
    _, raw, _, _, facts, review = analyze(shared_cache=True)
    demand = review.demand_dict()
    targets = build_demand_target_index(facts.cfg, raw)
    assert validate_result_references(demand, facts, targets) == demand
    changed = deepcopy(demand)
    gap = next(row for row in changed["diagnostics"] if row["code"] == "processing_gap")
    gap["affected_instruction_ids"] = ["ir_unknown"]
    with pytest.raises(ValueError, match="dependency closure"):
        validate_result_references(changed, facts, targets)
    changed = deepcopy(demand)
    changed["coverage"].pop("unresolved_boundaries")
    with pytest.raises(ValueError, match="unresolved boundary coverage"):
        validate_result_references(changed, facts, targets)
    changed = deepcopy(review.to_dict())
    next(row for row in changed["diagnostics"] if row["code"] == "processing_gap")["affected_instruction_ids"] = ["ir_unknown"]
    with pytest.raises(ValueError):
        validate_sensitivity_result(changed, facts=facts, annotation=facts.annotation, demand_result=demand)


def test_program_scope_default_and_sparse_output_closure_do_not_cross_independent_outputs():
    material, raw = authored(precision=True)
    _, compiled, _ = compile_response(raw, material)
    footprint = processing_impacts(material["cfg"], compiled)
    gap = compiled["processing_gaps"][0]
    assert footprint[gap_id(gap)] == ["ir_filter", "ir_return"]
    assert not diagnostic_applies({"affected_instruction_ids": footprint[gap_id(gap)]}, ["ir_read"])
    assert diagnostic_applies({"instruction_id": None}, ["ir_read"])  # Existing global Task gap policy.
    default = deepcopy(compiled)
    default["processing_gaps"][0].update(outputs=[], locations=[])
    assert processing_impacts(material["cfg"], default)


def test_no_gap_payload_keeps_legacy_shape():
    material, raw = authored(gap=False)
    _, compiled, _ = compile_response(raw, material)
    payload = to_payload(compiled)
    assert "processing_gaps" not in payload
    assert "processing_gaps" not in AnnotationPayload.model_validate(payload).model_dump(mode="json")
    validate_specs(material["cfg"], payload)


def test_constraint_path_stops_at_unknown_instruction_instead_of_counting_an_empty_action_sequence():
    _, _, _, _, _, review = analyze(constraint=True)
    checks = review.to_dict()["constraints"]["checks"]
    assert checks and {row["status"] for row in checks.values()} == {"not_established"}
    assert all("unevaluated instruction" in " ".join(row["reasons"]).lower() for row in checks.values())


def test_explicit_control_limitation_blocks_all_declared_descendants_without_task_gap_fabrication():
    material, raw = authored(precision=True)
    raw["processing_gaps"][0].update(instruction_id="ir_dispatch", outputs=[], control=True)
    raw, compiled, mapping = compile_response(raw, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"
    facts = materials_from_result(solved, material=material, raw_annotation=raw, compiled_annotation=compiled, mapping=mapping)
    review = prepare_sensitivity_review(facts, annotation=facts.annotation)
    assert model_rows(review) and all(row["conclusion"] == "no_excess_established" for row in model_rows(review))
    assert all(row["code"] != "requirement_expression_gap" for row in review.to_dict()["diagnostics"])


def test_output_uncertainty_reaches_named_writes_and_their_sibling_readers():
    material, raw = authored(precision=True, shared_cache=True)
    _, compiled, _ = compile_response(raw, material)
    # A separate declared write is a genuine value-use edge; closure does not
    # need to manufacture a result or execute the synthetic source to see it.
    compiled["ir_semantics"]["ir_filter"]["events"].append({"effect": "context_write", "evidences": [],
        "atomic_ops": [{"op": "write", "target": "cache", "mode": "replace", "input": local("body"), "evidences": []}]})
    impact = next(iter(processing_impacts(material["cfg"], compiled).values()))
    assert {"ir_filter", "ir_return", "ir_cache", "ir_late", "ir_late_return"} <= set(impact)
