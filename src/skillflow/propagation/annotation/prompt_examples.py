"""Small executable teaching cases, authored independently of evaluated Skills.

The full candidates are offline fixtures, not model answers or semantic gold
standards. Only compact source/operation contrasts enter production prompts.
"""
from __future__ import annotations

from copy import deepcopy

from .binding_examples import (
    _fixture, example_material, goal, inp, instruction, literal,
    local, result, segment, semantics,
)


def evidence():
    return {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "The synthetic source specifies this relationship."}


def _operation(example, identity):
    return example["annotation"]["ir_semantics"][identity]["events"][0]["events"][0]["atomic_ops"][0]


def _finish(example, *, gap=None):
    raw = example["annotation"]
    raw["task_revision_id"] = example_material(example)["task"]["task_sha256"]
    raw["realizations"] = [{"requirement_id": "R1", "status": "partial" if gap else "expressed",
        "bindings": [], "gaps": [{"reason": gap, "evidences": [evidence()]}] if gap else []}]
    return example


def prompt_examples():
    """Three complete positive fixtures with structurally legal contrasts."""
    filtering = {"op": "filter_items", "input": inp(), "predicate": "ready is true", "output": "ready_slots",
        "expression": {"expression": {"op": "eq", "left": {"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["ready"]},
                                    "right": {"op": "literal", "value": True}}, "evidences": [evidence()]},
        "demands": [goal({"kind": "output"}, "shape")]}
    count = {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "slot_count",
        "expression": {"expression": {"op": "count", "arg": {"op": "ref", "value": inp()}}, "evidences": [evidence()]}}
    comparison = {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "above_two",
        "expression": {"expression": {"op": "gt", "left": {"op": "ref", "value": inp()},
                        "right": {"op": "literal", "value": 2}}, "evidences": [evidence()]},
        "demands": [goal({"kind": "output"}, "truth")]}
    ex = _fixture("selection_count_boolean", "A selected collection is not a Boolean or a requirement for every member field.",
        "The agent runtime keeps calibration slots whose ready flag is true, counts the retained slots, and internally returns that count and whether it exceeds two. Unselected slots are excluded from the count.",
        [instruction("ir_slot_filter", "retain_ready", [literal([{"ready": True, "serial": "A-8"}, {"ready": False, "serial": "B-9"}])], "ready_slots"),
         instruction("ir_slot_count", "count_slots", [result("ready_slots")], "slot_count"),
         instruction("ir_slot_test", "compare_count", [result("slot_count")], "above_two"),
         instruction("ir_slot_return", "return", [result("slot_count"), result("above_two")])],
        {"ir_slot_filter": semantics([segment([filtering])], "ready_slots"),
         "ir_slot_count": semantics([segment([count])], "slot_count"),
         "ir_slot_test": semantics([segment([comparison])], "above_two"), "ir_slot_return": semantics()})
    ex["annotation"]["demands"] = [goal({"instruction_id": "ir_slot_return", "side": "input", "index": 0})]
    _finish(ex)
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_slot_filter"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [
        goal({"kind": "output"}, "value"), goal({"kind": "output"}, "truth")]
    ex["show"] = {"filter": _operation(ex, "ir_slot_filter"), "count_expression": count["expression"], "boolean_expression": comparison["expression"],
        "avoid": "Both filter self/truth and output/truth target the collection, not its predicate. shape and the attached expression preserve selection; downstream fields and count remain separate. Explicit complete-object requirements may use value."}
    ex["placements"] = {"filter": ["ir_slot_filter", "events", 0, "events", 0, "atomic_ops", 0],
        "count_expression": ["ir_slot_count", "events", 0, "events", 0, "atomic_ops", 0, "expression"],
        "boolean_expression": ["ir_slot_test", "events", 0, "events", 0, "atomic_ops", 0, "expression"]}
    cases = [ex]

    source = ("The agent runtime submits the unchanged calibration amplitude and channel to the device interface twice in order. "
              "Both submissions use the same values; deployment is unspecified. The interface label is not a transmitted parameter.")
    specs, instructions, deliveries = {}, [], []
    for identity, inputs, slots in (
        ("ir_device_first", [literal("west"), literal("device interface"), literal(2.5)], (2, 0)),
        ("ir_device_second", [literal(2.5), literal("device interface"), literal("west")], (0, 2))):
        delivery = {"op": "deliver", "target": "device", "inputs": [inp(index) for index in slots],
            "demands": [goal({"kind": "self"}, "action")] + [goal({"kind": "input", "index": slot}, expected=inp(index)) for slot, index in enumerate(slots)]}
        processing = segment([delivery], None)
        processing["events"][0].pop("evidences")
        specs[identity] = semantics([processing])
        specs[identity]["empty_effect_evidences"] = [evidence()]
        instructions.append(instruction(identity, "submit_calibration", inputs))
        deliveries.append(delivery)
    instructions.append(instruction("ir_device_return", "return", []))
    specs["ir_device_return"] = semantics()
    ex = _fixture("repeated_arguments", "Each required submission needs its own input demands; operation slots differ from IR operand indexes.", source, instructions, specs)
    ex["annotation"]["locations"] = {"device": {"kind": "tool", "name": "device interface", "operand_refs": [], "access_scope": "recipient", "retention": None}}
    ex["annotation"]["location_evidences"] = {"device": [evidence()]}
    _finish(ex)
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_device_second"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [goal({"kind": "self"}, "action")]
    ex["show"] = {"first_ir": ex["annotation"]["ir_semantics"]["ir_device_first"],
        "second_submission": _operation(ex, "ir_device_second"),
        "avoid": "self/action does not preserve arguments; equal values in the first submission do not seed the second. A genuinely argument-free action needs no invented payload."}
    ex["placements"] = {"first_ir": ["ir_device_first"],
        "second_submission": ["ir_device_second", "events", 0, "events", 0, "atomic_ops", 0]}
    cases.append(ex)

    producer = {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "rating"}
    save = {"op": "write", "mode": "append", "target": "ledger", "input": inp(1),
        "demands": [goal({"kind": "self"}, "action"), goal({"kind": "input", "index": 0}, expected=inp(1))]}
    ex = _fixture("opaque_rating_save", "An open encoding alone is not a missing requirement; preserve the abstract result-to-write relation.",
        "The agent runtime computes a calibration rating from the supplied waveform by an unspecified procedure and appends that resulting rating to the persistent calibration ledger. The storage encoding is unspecified.",
        [instruction("ir_rating_compute", "rate_waveform", [literal([0.1, 0.3, 0.2])], "rating"),
         instruction("ir_rating_save", "append_rating", [literal("calibration ledger"), result("rating")]),
         instruction("ir_rating_return", "return", [])],
        {"ir_rating_compute": semantics([segment([producer])], "rating"), "ir_rating_save": semantics([segment([save], "fs_write")]), "ir_rating_return": semantics()})
    ex["annotation"]["locations"] = {"ledger": {"kind": "storage", "name": "calibration ledger", "operand_refs": [], "access_scope": "task", "retention": "persistent"}}
    ex["annotation"]["location_evidences"] = {"ledger": [evidence()]}
    _finish(ex)
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_rating_save"]["events"][0]["events"][0]["atomic_ops"][0]["demands"] = [goal({"kind": "self"}, "action")]
    ex["show"] = {"save": _operation(ex, "ir_rating_save"), "realization": ex["annotation"]["realizations"][0],
        "avoid": "Preserve this append's rating input, not prior ledger contents. Open encoding alone adds no gap. A separately required but unrepresented format restriction needs an evidenced gap without erasing supported content demands."}
    ex["placements"] = {"save": ["ir_rating_save", "events", 0, "events", 0, "atomic_ops", 0],
        "realization": ["realizations", 0]}
    cases.append(ex)
    return cases


def compact_prompt_examples():
    """Complete typed subobjects with explicit outer context, never field-stripped."""
    return [{"case": row["name"], "source": row["source"], "rule": row["lesson"],
             "context": {"file": "skill/SKILL.md", "line": 1, "requirement_id": "R1",
                 "ir_inputs": {ir["id"]: ir["inputs"] for ir in row["cfg"]["blocks"]["sample"]["instructions"]
                               if ir["id"] in {path[0] for path in row["placements"].values()}},
                 "placements": row["placements"]},
             "fragments": deepcopy(row["show"])} for row in prompt_examples()]


def endpoint_example():
    """One full acquisition-to-receiver lesson and a structurally legal contrast."""
    source = (
        "The agent runtime reads calibration_packet from session context and sends a calibration record to the calibration interface. "
        "The record carries badge unchanged and offset unchanged only when the packet's Boolean adjustment is true. "
        "badge is a private personnel identifier; the packet also contains internal_note. "
        "The interface deployment is unspecified. Return internally.")
    read = {"op": "read", "location": "session_packet", "output": "packet"}
    operations = [{"op": "select_part", "input": inp(), "path": [field], "output": field}
                  for field in ("badge", "offset", "adjustment")]
    build = {"op": "build", "container": "object", "output": "calibration_record",
             "parts": [{"path": ["badge"], "value": local("badge")},
                       {"path": ["offset"], "value": local("offset"), "when": local("adjustment")}]}
    operations.append(build)
    delivery = {"op": "deliver", "target": "calibration_interface", "inputs": [local("calibration_record")],
        "demands": [goal({"kind": "self"}, "action", reason="Preserve the specified interface call."),
            goal({"kind": "input", "index": 0}, path=["badge"], expected=inp(), expected_path=["badge"],
                 reason="Preserve the original badge at this receiving slot."),
            goal({"kind": "input", "index": 0}, path=["offset"],
                 reason="Preserve offset at this receiving slot when included; existing select_part/build retain its original value and build.when controls its consumption.")],
        "evidences": [evidence()]}
    processing = segment(operations)
    processing["events"].append({"effect": None, "atomic_ops": [delivery]})
    ex = _fixture("packet_receiver_content", "Read scope and upstream construction do not establish receiver content demands.", source,
        [instruction("ir_packet_read", "read_packet", [{"type": "context_key", "identifier": "calibration_packet"}], "packet"),
         instruction("ir_packet_send", "prepare_and_submit", [result("packet")]),
         instruction("ir_packet_return", "return", [])],
        {"ir_packet_read": semantics([segment([read], "context_read")], "packet"),
         "ir_packet_send": semantics([processing]), "ir_packet_return": semantics()})
    ex["cfg"]["declared_context_keys"] = ["calibration_packet"]
    # Context acquisition has its own source block under the unchanged CFG
    # contract; the terminator is real graph structure, not a transfer step.
    read_ir = ex["cfg"]["blocks"]["sample"]["instructions"].pop(0)
    ex["cfg"]["entry_block_id"] = "acquire"
    ex["cfg"]["blocks"]["acquire"] = {"block_id": "acquire", "block_name": "Packet acquisition",
        "constraints": [], "data_source_kind": "context",
        "instructions": [read_ir, instruction("ir_packet_dispatch", "dispatch", [])]}
    ex["cfg"]["edges"] = [{"source_block_id": "acquire", "target_block_id": "sample", "condition_text": None}]
    ex["annotation"]["ir_semantics"]["ir_packet_dispatch"] = semantics()
    requirement = "Send a calibration record containing the original badge and the original offset exactly when adjustment is true."
    ex["task_candidate"]["purpose"]["text"] = requirement
    ex["task_candidate"]["requirements"][0]["text"] = requirement
    ex["task_candidate"]["source_accounting"][0]["reason"] = (
        "The line specifies the required submission; acquisition, private-field context and internal return describe its implementation.")
    raw = ex["annotation"]
    raw["locations"] = {
        "session_packet": {"kind": "runtime_context", "name": "calibration_packet", "operand_refs": [
            {"instruction_id": "ir_packet_read", "side": "input", "index": 0}], "access_scope": "task", "retention": "task"},
        "calibration_interface": {"kind": "tool", "name": "calibration interface", "operand_refs": [],
            "access_scope": "recipient", "retention": None}}
    raw["location_evidences"] = {name: [evidence()] for name in raw["locations"]}
    raw["ir_semantics"]["ir_packet_read"]["sensitivity"] = [{"value": local("packet"), "path": ["badge"],
        "property": "value", "label": "personal_identifier", "evidences": [evidence()]}]
    _finish(ex)
    raw["realizations"][0]["bindings"] = [{"target": {"instruction_id": "ir_packet_send", "path": []},
        "reason": "The submission binds each required original field at the actual receiving input, with the offset condition in build."}]
    prefix = ["ir_semantics", "ir_packet_send", "events", 0, "events"]
    ex["positions"] = {
        "read": ["ir_semantics", "ir_packet_read", "events", 0, "events", 0, "atomic_ops", 0],
        **{f"select_{field}": prefix + [0, "atomic_ops", index]
           for index, field in enumerate(("badge", "offset", "adjustment"))},
        "build": prefix + [0, "atomic_ops", 3], "deliver": prefix + [1, "atomic_ops", 0]}
    contrast = deepcopy(raw)
    def at(candidate, name):
        node = candidate
        for part in ex["positions"][name]:
            node = node[part]
        return node
    at(contrast, "read")["demands"] = [goal({"kind": "output"}, "value",
        reason="Preserve the complete acquired packet for preparing the record.")]
    at(contrast, "build")["demands"] = [
        goal({"kind": "input", "index": 0}, reason="Preserve badge while constructing the record."),
        goal({"kind": "input", "index": 1}, "truth", reason="Preserve the offset inclusion condition."),
        goal({"kind": "input", "index": 2}, reason="Preserve offset while constructing the record.")]
    at(contrast, "deliver")["demands"] = [deepcopy(delivery["demands"][0]),
        goal({"kind": "input", "index": 0}, "shape", reason="Preserve the submitted record's members and structure.")]
    ex["contrast"] = contrast
    ex["show"] = {"build_slots": [
        {"slot": 0, "role": "value", "value": local("badge")},
        {"slot": 1, "role": "control", "value": local("adjustment")},
        {"slot": 2, "role": "value", "value": local("offset")}],
        "delivery_slot": {"slot": 0, "value": local("calibration_record")},
        "rule": "The positive response keeps the acquired packet whole, but seeds badge/offset value at deliver input 0 and their paths. No whole read seed is needed. badge expected refers to the enclosing IR packet. offset retains its original value through select_part/build and omits redundant expected: that independent source seed does not inherit build.when, which controls member consumption.",
        "contrast": "A whole read-output value seed is too broad for this Task. Content seeds on build plus deliver action/shape remain insufficient at the receiver: shape is not badge/offset value. This does not invalidate build demands for a separately required construction result."}
    return ex


def endpoint_example_context():
    """Frozen public context sufficient to validate the displayed full response."""
    material = example_material(endpoint_example())
    return {name: material[name] for name in ("source", "cfg", "task")}


def coordinate_examples():
    """A complete positional operation; the full endpoint lesson covers build."""
    delivery = {"op": "deliver", "target": "display", "inputs": [inp(2)],
        "demands": [goal({"kind": "input", "index": 0}, expected=inp(2))], "evidences": [evidence()]}
    return [
        {"case": "calibration_display", "source": "Display only the third supplied calibration value unchanged.",
         "cfg_inputs": ["blue", 7, "stable"], "operation": delivery,
         "resolved_slots": [{"slot": 0, "role": "value", "value": inp(2)}],
         "review_rule": "Operation input[0] selects IR input[2]. target input[2] names no delivery slot. expected checks the required original relation; it does not alter delivery."},
    ]
