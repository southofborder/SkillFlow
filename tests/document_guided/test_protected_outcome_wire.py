"""Protected cases bind existing CFG ports without manufacturing an error packet."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import split_fragments, validate_fragment, assemble_fragments
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import validate_raw_response
from skillflow.document_guided.entry_transfers import entry_binding_errors
from skillflow.document_guided.action_bindings import action_coordinates, checked_action_bindings
from tests.document_guided.test_optional_case_segments import existing_value_fixture


def fixture():
    material, wire, summary = existing_value_fixture(False)
    cfg = deepcopy(material["cfg"])
    call = next(ir for b in cfg["blocks"].values() for ir in b["instructions"] if ir["id"] == "ir_call")
    call["outputs"].extend([{"type": "result", "identifier": name} for name in ("error", "completed")])
    material = prepare_material(material["source"], cfg, task_baseline=material["task"])
    summary.pop("output")
    summary["outcome"] = {"return_index": 0, "exception_index": 1, "completion_index": 2}
    summary["cases"][1]["raise"] = {"kind": "local", "name": "__raised__"}
    wire["ir_semantics"]["ir_call"]["output_bindings"] = []
    return material, wire, summary


def test_outcome_ports_lower_and_compile_in_both_full_and_fragment_routes():
    material, wire, _ = fixture()
    before = deepcopy(wire)
    _, raw, compiled, mapping = compile_flat_response(wire, material)
    original = raw["ir_semantics"]["ir_call"]["outcome_bindings"][0]
    binding = compiled["ir_semantics"]["ir_call"]["outcome_bindings"][0]
    assert binding == original
    assert binding["return_index"] == 0 and binding["exception_index"] == 1 and binding["completion_index"] == 2
    assert binding["cases"][1]["value"] == {"kind": "local", "name": "__raised__"}
    assert {e["case"]["id"] for e in compiled["ir_semantics"]["ir_call"]["events"]} == {
        c["case_id"] for c in binding["cases"]}
    pieces = split_fragments(wire)
    source_only = {k: v for k, v in material.items() if k != "task"}
    assert validate_fragment("processing", pieces["processing"], source_only) == pieces["processing"]
    _, _, fragment_compiled, _ = assemble_fragments(pieces["processing"], pieces["task-correspondence"],
                                                 pieces["sensitivity"], material)
    assert fragment_compiled["ir_semantics"]["ir_call"]["outcome_bindings"] == [binding]
    assert wire == before


@pytest.mark.parametrize("fault", ["duplicate", "range", "ordinary", "raise-return", "yield-throw", "raised-yield", "not-final", "partial", "nested"])
def test_invalid_protected_contracts_remain_structural(fault):
    material, wire, summary = fixture()
    record = wire["ir_semantics"]["ir_call"]
    if fault == "duplicate": summary["outcome"]["completion_index"] = 0
    elif fault == "range": summary["outcome"]["completion_index"] = 7
    elif fault == "ordinary": record["output_bindings"] = [{"output_index": 0, "value": {"kind": "input", "index": 0}}]
    elif fault == "raise-return": summary["cases"][0]["raise"] = {"kind": "input", "index": 0}
    elif fault == "yield-throw": summary["cases"][1]["yield"] = {"kind": "input", "index": 0}
    elif fault == "raised-yield": summary["cases"][0]["yield"] = {"kind": "local", "name": "__raised__"}
    elif fault == "not-final": record["segments"].append({"mode": "local", "returns": [{"kind": "input", "index": 0}]})
    elif fault == "partial": record["order"] = "partial"
    else:
        record["segments"] = [{"kind": "for_each", "collection": {"kind": "input", "index": 0}, "item": "x", "body": [summary]}]
    with pytest.raises(StructuralValidationError): compile_flat_response(wire, material)


@pytest.mark.parametrize("disposition", ["return", "throw"])
def test_single_outcome_does_not_require_an_opposite_port(disposition):
    material, wire, summary = fixture()
    summary["cases"] = [case for case in summary["cases"] if case["disposition"] == disposition]
    summary["outcome"].pop("exception_index" if disposition == "return" else "return_index")
    summary["outcome"].update(completion_index=1, **{"return_index" if disposition == "return" else "exception_index": 0})
    cfg = deepcopy(material["cfg"])
    for block in cfg["blocks"].values():
        for ir in block["instructions"]:
            if ir["id"] == "ir_call":
                ir["outputs"] = [{"type": "result", "identifier": name}
                                 for name in ("value" if disposition == "return" else "error", "completed")]
            elif ir["id"] == "ir_return":
                ir["inputs"] = []
    material = prepare_material(material["source"], cfg, task_baseline=material["task"])
    _, _, compiled, _ = compile_flat_response(wire, material)
    binding = compiled["ir_semantics"]["ir_call"]["outcome_bindings"][0]
    assert {c["disposition"] for c in binding["cases"]} == {disposition}


def case_local_raw():
    material, wire, summary = fixture()
    normal = summary["cases"][0]
    normal["segments"] = [{"mode": "local", "returns": [], "ops": [{"op": "compute",
        "inputs": [{"kind": "input", "index": 0}], "output": "kept",
        "expression": {"expression": {"op": "ref", "value": {"kind": "input", "index": 0}}}}]}]
    normal["yield"] = {"kind": "local", "name": "kept"}
    _, raw, _, _ = compile_flat_response(wire, material)
    return material, raw


def test_direct_raw_cannot_export_case_only_local_as_unconditional_output():
    material, raw = case_local_raw()
    cfg = deepcopy(material["cfg"])
    next(ir for b in cfg["blocks"].values() for ir in b["instructions"] if ir["id"] == "ir_call")["outputs"].append(
        {"type": "result", "identifier": "invalid_unconditional"})
    material = prepare_material(material["source"], cfg, task_baseline=material["task"])
    spec = raw["ir_semantics"]["ir_call"]
    value = spec["outcome_bindings"][0]["cases"][0]["value"]
    spec["output_bindings"].append({"output_index": 3, "value": value,
                                   "evidences": spec["outcome_bindings"][0]["cases"][0]["evidences"]})
    with pytest.raises(StructuralValidationError, match="case-only"):
        validate_raw_response(raw, material)


def test_direct_raw_protected_sibling_cannot_consume_normal_case_local():
    material, raw = case_local_raw()
    spec = raw["ir_semantics"]["ir_call"]
    value = spec["outcome_bindings"][0]["cases"][0]["value"]
    normal_op = deepcopy(spec["events"][0]["events"][0]["atomic_ops"][0])
    normal_op.update(inputs=[value], output="sibling_read")
    normal_op["expression"]["expression"] = {"op": "ref", "value": value}
    spec["events"][1]["events"][0]["atomic_ops"] = [normal_op]
    with pytest.raises(StructuralValidationError, match="another case"):
        validate_raw_response(raw, material)


def test_entry_snapshot_can_bind_a_protected_return_without_a_fake_operation():
    spec = {"segments": [{"kind": "cases", "outcome": {"return_index": 0, "completion_index": 1},
        "cases": [{"name": "received", "phase": "normal", "disposition": "return",
                   "condition": "The entry argument is available.", "segments": [],
                   "yield": {"kind": "input", "index": 0}}]}], "output_bindings": []}
    ir = {"id": "entry", "inputs": [{"type": "context_key", "identifier": "arg"},
                                    {"type": "context_key", "identifier": "other"}]}
    ports = [{"input_index": 0, "output_index": 0, "owner": "source entry", "parameter": "arg", "optional": False}]
    assert entry_binding_errors(ir, ports, spec, {}) == []
    spec["segments"][0]["cases"][0]["yield"]["index"] = 1
    assert entry_binding_errors(ir, ports, spec, {})


def test_protected_outcome_cannot_join_actions_from_different_owners():
    material, wire, _ = fixture()
    record = wire["ir_semantics"]["ir_call"]
    from skillflow.propagation.annotation.binding_examples import evidence
    citation = evidence()
    at = {key: citation[key] for key in ("file", "start_line", "end_line")}
    record["source_actions"] = [{"ref": name, "kind": "local preparation", "role": "value", "source": at}
                                for name in ("protected", "unrelated")]
    coords = [list(path) for path, _ in action_coordinates(record)]
    stolen = coords.pop(1)
    record["action_bindings"] = {"protected": coords, "unrelated": [stolen]}
    with pytest.raises(StructuralValidationError, match="same source action"):
        checked_action_bindings(wire, material)


def test_process_exit_is_owned_by_its_existing_terminator_without_fake_call():
    material, wire, _ = fixture()
    from skillflow.propagation.annotation.binding_examples import evidence
    citation = evidence()
    at = {key: citation[key] for key in ("file", "start_line", "end_line")}
    record = wire["ir_semantics"]["ir_return"]
    record["source_actions"] = [{"ref": "exit", "kind": "source process termination", "role": "other", "source": at}]
    record["action_bindings"] = {"exit": [["terminator"]]}
    checked = checked_action_bindings(wire, material)
    assert checked["ir_return"]["bindings"] == {"exit": [["terminator"]]}
    record["action_bindings"]["exit"] = [["segments", 0, "ops", 0]]
    with pytest.raises(StructuralValidationError):
        checked_action_bindings(wire, material)
