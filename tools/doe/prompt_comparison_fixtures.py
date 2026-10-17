"""Held-out synthetic comparison cases, separate from teaching examples.

References are assistant-authored evaluation claims, never transmitted to the
annotator. They are independent of the three real Skills and differ in topology
and requirement combinations from production prompt lessons.
"""
from copy import deepcopy

from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, goal, inp, instruction, literal, local,
    result, segment, semantics,
)


def _finish(example, *, gap=None):
    raw = example["annotation"]
    raw["task_revision_id"] = example_material(example)["task"]["task_sha256"]
    raw["realizations"] = [{"requirement_id": "R1", "status": "partial" if gap else "expressed", "bindings": [],
                            "gaps": [{"reason": gap, "evidences": [evidence()]}] if gap else []}]
    return example


def evaluation_fixtures():
    select = {"op": "select_part", "input": inp(0), "path": ["bins"], "output": "bins"}
    filtering = {"op": "filter_items", "input": local("bins"), "predicate": "open is true and load is below seven", "output": "usable",
        "expression": {"expression": {"op": "and", "args": [
            {"op": "eq", "left": {"op": "field", "arg": {"op": "ref", "value": local("bins")}, "path": ["open"]}, "right": {"op": "literal", "value": True}},
            {"op": "lt", "left": {"op": "field", "arg": {"op": "ref", "value": local("bins")}, "path": ["load"]}, "right": {"op": "literal", "value": 7}}]}, "evidences": [evidence()]},
        "demands": [goal({"kind": "output"}, "shape")]}
    counting = {"op": "compute", "inputs": [local("usable")], "dependencies": ["derived"], "output": "capacity",
        "expression": {"expression": {"op": "count", "arg": {"op": "ref", "value": local("usable")}}, "evidences": [evidence()]}}
    test = {"op": "compute", "inputs": [local("capacity")], "dependencies": ["derived"], "output": "empty",
        "expression": {"expression": {"op": "eq", "left": {"op": "ref", "value": local("capacity")}, "right": {"op": "literal", "value": 0}}, "evidences": [evidence()]}}
    build = {"op": "build", "container": "object", "parts": [{"path": ["capacity"], "value": local("capacity")}, {"path": ["empty"], "value": local("empty")}], "output": "overview"}
    ex = _fixture("capacity_overview", "Nested collection extraction, a two-field predicate, count and Boolean are composed into a returned object.",
        "For the pallet capacity survey, take bins from the supplied inventory envelope. Keep only bins with open equal to true and load below seven. Return an object containing capacity, the retained-bin count, and empty, whether that count is zero. Bin contents are not part of the returned overview.",
        [instruction("ir_inventory_overview", "prepare_overview", [literal({"bins": [{"open": True, "load": 3, "batch_label": "ZK-22"}]})], "overview"),
         instruction("ir_inventory_finish", "return", [result("overview")])],
        {"ir_inventory_overview": semantics([segment([select, filtering, counting, test, build])], "overview"), "ir_inventory_finish": semantics()})
    ex["annotation"]["demands"] = [goal({"instruction_id": "ir_inventory_finish", "side": "input", "index": 0})]
    _finish(ex)
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_inventory_overview"]["events"][0]["events"][0]["atomic_ops"][1]["demands"] = [goal({"kind": "output"}, "value"), goal({"kind": "output"}, "truth")]
    cases = [ex]

    select = {"op": "select_part", "input": inp(1), "path": ["asset_tag"], "output": "tag"}
    first = {"op": "deliver", "target": "register", "inputs": [local("tag"), inp(2)], "demands": [
        goal({"kind": "self"}, "action"), goal({"kind": "input", "index": 0}, expected=inp(1), expected_path=["asset_tag"]),
        goal({"kind": "input", "index": 1}, expected=inp(2))]}
    second = {"op": "deliver", "target": "register", "inputs": [inp(2), inp(0)], "demands": [
        goal({"kind": "self"}, "action"), goal({"kind": "input", "index": 0}, expected=inp(2)), goal({"kind": "input", "index": 1}, expected=inp(0))]}
    first_event, second_event = segment([first], None), segment([second], None)
    first_event["events"][0].pop("evidences")
    second_event["events"][0].pop("evidences")
    ex = _fixture("repeat_registration", "A public original-field result is reused at a second explicit delivery with distinct IR and operation coordinates.",
        "Register the parcel's original asset_tag with the registry interface using registration class inbound. Then register the same asset_tag a second time using registration class verified. Perform both registrations in that order. Deployment of the registry interface is not specified; the parcel's other fields are not registration arguments.",
        [instruction("ir_register_inbound", "register_tag", [literal("registry interface"), literal({"asset_tag": "PK-440", "packing_note": "fold top"}), literal("inbound")], "original_tag"),
         instruction("ir_register_verified", "register_tag", [literal("verified"), literal("registry interface"), result("original_tag")]),
         instruction("ir_registry_finish", "return", [])],
        {"ir_register_inbound": semantics([segment([select]), first_event], "tag"), "ir_register_verified": semantics([second_event]), "ir_registry_finish": semantics()})
    ex["annotation"]["ir_semantics"]["ir_register_verified"]["empty_effect_evidences"] = [evidence()]
    ex["annotation"]["locations"] = {"register": {"kind": "tool", "name": "registry interface", "operand_refs": [], "access_scope": "recipient", "retention": None}}
    ex["annotation"]["location_evidences"] = {"register": [evidence()]}
    _finish(ex)
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_register_verified"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [goal({"kind": "self"}, "action")]
    cases.append(ex)

    producer = {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "diagnosis"}
    save = {"op": "write", "mode": "replace", "target": "worksheet", "input": inp(1), "demands": [
        goal({"kind": "self"}, "action"), goal({"kind": "input", "index": 0}, expected=inp(1))]}
    echo = {"op": "deliver", "target": "console", "inputs": [inp(1)], "demands": [goal({"kind": "input", "index": 0}, expected=inp(1))]}
    local_computation = segment([producer])
    local_computation.update(mode="local", returns=[local("diagnosis")])
    ex = _fixture("opaque_diagnosis_save", "An isolated opaque producer returns one abstract result, which is saved and displayed without inferring an encoding.",
        "A local diagnostic module processes the supplied acoustic trace internally and returns only its diagnosis to the agent. Replace the diagnostic worksheet with that diagnosis and display the same diagnosis to the operator. The diagnostic computation and worksheet encoding are unspecified.",
        [instruction("ir_acoustic_diagnose", "diagnose_trace", [literal([0.7, 0.5, 0.9])], "diagnosis"),
         instruction("ir_worksheet_save", "save_and_display", [literal("diagnostic worksheet"), result("diagnosis")]), instruction("ir_diagnosis_finish", "return", [])],
        {"ir_acoustic_diagnose": semantics([local_computation], "diagnosis"),
         "ir_worksheet_save": semantics([segment([save], "fs_write"), segment([echo], "user_output")]), "ir_diagnosis_finish": semantics()})
    ex["annotation"]["locations"] = {"worksheet": {"kind": "storage", "name": "diagnostic worksheet", "operand_refs": [], "access_scope": "task", "retention": "persistent"},
        "console": {"kind": "user", "name": "operator console", "operand_refs": [], "access_scope": "recipient", "retention": None}}
    ex["annotation"]["location_evidences"] = {name: [evidence()] for name in ex["annotation"]["locations"]}
    _finish(ex, gap="The abstract diagnosis can be preserved at the storage and display boundaries; the source leaves the diagnostic algorithm and worksheet encoding unspecified, so this limitation is retained.")
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_worksheet_save"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [goal({"kind": "self"}, "action")]
    cases.append(ex)
    return cases
