"""Executable compact-format examples and coverage of exposed structural rules."""
import ast
import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import annotation_wire as flat
from skillflow.document_guided.cfg_wire import CFGWire, CFG_RULES, normalize_cfg_wire
from skillflow.document_guided.fragments import (
    FRAGMENT_RULES, assemble_fragments, fragment_adapter, fragment_contract_rules,
    fragment_correction_strategy, validate_fragment,
)
from skillflow.document_guided.interface_examples import (
    example_cfg, example_fragments, example_material, loop_operation_examples, phase_examples,
)
from tests.document_guided.test_annotation_wire import sample


def test_eight_actual_v7_empty_case_failures_have_a_valid_no_new_operation_form():
    path = Path(__file__).parents[1] / "fixtures/ga4_boundary_cases/v7_empty_case_segments.json"
    records = json.loads(path.read_text(encoding="utf-8"))["records"]
    assert len(records) == 8
    for record in records:
        before = deepcopy(record["case"])
        with pytest.raises(ValidationError, match="processing requires operations"):
            flat.FlatCase.model_validate(before)
        corrected = deepcopy(before)
        corrected["segments"] = [segment for segment in corrected["segments"]
                                  if segment.get("ops") or segment.get("returns")]
        assert corrected["segments"] == []
        flat.FlatCase.model_validate(corrected)
        assert corrected["yield"] == before["yield"]
        assert record["case"] == before


def test_case_union_reports_only_its_actual_empty_segment_error():
    material, wire = sample()
    wire["ir_semantics"]["ir_call"]["segments"] = [{"kind": "cases", "output": "chosen", "cases": [
        {"name": "supplied", "phase": "normal", "disposition": "return", "condition": "A value was supplied.",
         "segments": [{"mode": "local", "returns": []}], "yield": {"kind": "input", "index": 0}}]}]
    with pytest.raises(StructuralValidationError) as caught:
        flat._parse(wire)
    rows = caught.value.diagnostics
    assert len(rows) == 1, rows
    assert rows[0]["path"] == "/ir_semantics/ir_call/segments/0/cases/0/segments/0"
    assert "processing requires operations" in rows[0]["message"]
    assert "for_each" not in str(rows)


def test_nearest_applicable_expression_evidence_skips_cfg_only_parent():
    material, wire = sample()
    source = deepcopy(wire["ir_semantics"]["ir_return"]["evidences"])
    cfg = [{"target": {"instruction_id": "ir_return", "path": []}}]
    wire["ir_semantics"]["ir_return"]["segments"] = [{"evidences": cfg, "ops": [
        {"op": "compute", "inputs": [{"kind": "input", "index": 0}], "output": "present", "evidences": cfg,
         "expression": {"expression": {"op": "present", "arg": {"op": "ref", "value": {"kind": "input", "index": 0}}}}}]}]
    normalized = flat.normalize_flat_annotation(wire, material)
    op = normalized["ir_semantics"]["ir_return"]["events"][0]["events"][0]["atomic_ops"][0]
    assert op["expression"]["evidences"] == source
    wire["ir_semantics"]["ir_return"]["segments"][0]["ops"][0]["expression"]["evidences"] = cfg
    with pytest.raises(StructuralValidationError, match="source"):
        flat.normalize_flat_annotation(wire, material)


@pytest.mark.parametrize("operand", [
    {"type": "result"}, {"type": "context_key", "identifier": ""},
    {"type": "external_resource", "identifier": "tool", "literal_value": None},
    {"type": "literal", "identifier": "invented", "literal_value": 3},
    {"type": "literal"},
])
def test_cfg_operand_variants_expose_actual_forbidden_and_required_fields(operand):
    value = example_cfg()
    value["blocks"][0]["instructions"][0]["inputs"] = [operand]
    with pytest.raises(ValidationError):
        CFGWire.model_validate(value)


def test_literal_null_is_a_value_and_program_owned_fields_stay_absent():
    value = example_cfg()
    value["blocks"][0]["instructions"][0]["inputs"] = [{"type": "literal", "literal_value": None}]
    normalized = normalize_cfg_wire(value)
    assert normalized["blocks"][0]["instructions"][0]["inputs"][0]["literal_value"] is None
    schema = str(CFGWire.model_json_schema())
    assert "semantic_name" not in schema and "instruction_ref" not in schema


def test_replacement_slot_is_stable_but_invalid_target_reference_can_be_corrected():
    material, wire = sample()
    from skillflow.document_guided.fragments import split_fragments
    processing = split_fragments(wire)["processing"]
    original = {"declarations": [{"instruction_id": "missing", "value": {"kind": "input", "index": 0},
                                  "label": "Credential", "evidences": wire["ir_semantics"]["ir_call"]["evidences"]}]}
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", original, material, processing)
    strategy = fragment_correction_strategy("sensitivity")
    from skillflow.common.prompt_format import compact_json
    strategy.build_prompt("Declare sensitivity.", compact_json(original), caught.value.diagnostics)
    corrected = {**original["declarations"][0], "instruction_id": "ir_call"}
    merged = strategy.merge(compact_json(original), compact_json({"replacements": [
        {"record_id": "/declarations/0", "value": corrected}]}))
    assert validate_fragment("sensitivity", merged, material, processing) == merged
    assert original["declarations"][0]["instruction_id"] == "missing"
    with pytest.raises(StructuralValidationError, match="identity"):
        strategy.merge(compact_json(original), compact_json({"replacements": [
            {"record_id": "/declarations/1", "value": corrected}]}))


def test_exact_prompt_examples_validate_assemble_and_propagate_without_observing_local_replies():
    fragments, material = example_fragments(), example_material()
    for kind, fragment in fragments.items():
        fragment_adapter(kind).validate_python(fragment)
        assert '"response"' in phase_examples(kind)
    normalize_cfg_wire(example_cfg())
    _, _, compiled, _ = assemble_fragments(fragments["processing"], fragments["task-correspondence"],
                                          fragments["sensitivity"], material)
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.solver import propagate
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    loop = solved.records.get("ir_call").events[0]
    assert len(loop.instances) == 2
    assert all(instance.yielded for instance in loop.instances)
    assert not any(event.effect == "model_observe" for instance in loop.instances for event in instance.body)
    assert any(event.case is not None and not event.atomic_ops for instance in loop.instances for event in instance.body)


# This inventory covers custom diagnostic families in the three interface
# modules. JSON shape/enum/required rules come directly from the actual schema;
# backend rule families are covered by the short phase descriptions and their
# existing compiler/propagation tests. This table is documentation coverage,
# not a new validation language.
DIAGNOSTIC_RULES = {
    "case_reference": "sensitivity_scope", "evidence_inheritance": "evidence_inheritance",
    "evidence_kind": "evidence_inheritance", "expression_input": "expression_target",
    "expression_target_capability": "expression_target", "local_returns": "local_returns",
    "mechanism_evidence_reference": "evidence_inheritance", "operation_phase": "operation_reference",
    "operation_reference": "operation_reference", "program_owned": "request_pair",
    "operation_demand_duplicate": "operation_reference", "operation_demands_duplicate": "operation_reference",
    "sensitivity_duplicate": "sensitivity_value", "sensitivity_scope": "sensitivity_scope",
    "dispatch_inputs": "dispatch_inputs", "external_acquisition_inputs": "external_acquisition_inputs",
    "binary_dispatch": "binary_dispatch",
}
CORRECTION_OR_JSON = {"json_format", "correction_candidate", "correction_json", "record_identity", "record_replacement"}


def test_every_interface_custom_diagnostic_has_a_visible_rule_or_correction_contract():
    from skillflow.document_guided import fragments, cfg_wire
    exposed = set(CFG_RULES) | {key for rules in FRAGMENT_RULES.values() for key in rules}
    assert set(DIAGNOSTIC_RULES.values()) <= exposed
    for module in (flat, fragments, cfg_wire):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        codes = {call.args[0].value for call in ast.walk(tree) if isinstance(call, ast.Call)
                 and isinstance(call.func, ast.Name) and call.func.id in {"structural_error", "error"}
                 and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)}
        assert codes <= set(DIAGNOSTIC_RULES) | CORRECTION_OR_JSON
    for kind, rules in FRAGMENT_RULES.items():
        text = fragment_contract_rules(kind)
        assert all(name in text and description in text for name, description in rules.items())


def test_format_rules_remain_phase_scoped_and_no_internal_bookkeeping_returns():
    assert "SEALED_TASK" not in phase_examples("sensitivity")
    assert "realization_coverage" not in fragment_contract_rules("sensitivity")
    for kind in ("processing", "task-correspondence", "sensitivity"):
        schema = str(fragment_adapter(kind).json_schema())
        for field in ("request_id", "operator_evidences", "empty_effect_evidences", "loop_id"):
            assert field not in schema


def test_all_published_loop_operation_examples_validate_and_compile_with_actual_cfg_edges():
    # Reuse the same source projection as the integration test, without another
    # propagation/replay run or a second fixture implementation.
    from tests.document_guided.test_ga4_explicit_loops import batch_projection
    material, wire = batch_projection(["https://a.example", "https://a.example"])
    identifiers = {"merge": "ir_merge", "member": "ir_member", "branch": "ir_guard", "append": "ir_append"}
    for kind, record in loop_operation_examples().items():
        wire["ir_semantics"][identifiers[kind]]["segments"][0]["ops"] = [record["operation"]]
    saved, _, compiled, _ = flat.compile_flat_response(wire, material)
    assert all(identifiers[kind] in compiled["ir_semantics"] for kind in identifiers)
    assert saved["ir_semantics"]["ir_merge"]["segments"][0]["ops"][0]["incoming"][0]["predecessor"] == "entry"
    for change, diagnostic in (("predecessor", "incoming CFG block"), ("target", "outgoing CFG successors")):
        bad = deepcopy(wire)
        if change == "predecessor":
            bad["ir_semantics"]["ir_merge"]["segments"][0]["ops"][0]["incoming"][0]["predecessor"] = "absent"
        else:
            bad["ir_semantics"]["ir_guard"]["segments"][0]["ops"][0]["false_target"] = "absent"
        with pytest.raises(StructuralValidationError, match=diagnostic):
            flat.compile_flat_response(bad, material)
