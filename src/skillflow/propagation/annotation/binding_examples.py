"""Independent executable binding lessons, never derived from evaluated Skills.

Full fixtures support compilation tests. The prompt includes only the relevant
bindings and their small CFG context, not seven complete annotation responses.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib

from skillflow.common.source_evidence import _digest
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.references import cfg_target_from_path


def evidence():
    return {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "This independent source supports the illustrated relationship; a valid reference does not prove the same interpretation for another task."}


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def instruction(identity, opcode, inputs, output=None):
    return {"id": identity, "opcode": opcode, "inputs": inputs,
            "outputs": [] if output is None else [{"type": "result", "identifier": output}],
            "constraints": [], "metadata": {}}


def literal(value):
    return {"type": "literal", "literal_value": value}


def result(name):
    return {"type": "result", "identifier": name}


def segment(operations, effect="transform"):
    return {"kind": "processing", "mode": "default", "returns": [], "evidences": [evidence()],
            "events": [{"effect": effect, "evidences": [evidence()],
                        "atomic_ops": [{**op, "evidences": [evidence()]} for op in operations]}]}


def semantics(events=(), output=None):
    value = {"operator": ["agent_runtime"], "operator_evidences": [{"value": "agent_runtime", **evidence()}],
             "order": "fixed", "events": list(events), "sensitivity": [],
             "output_bindings": [] if output is None else [{"output_index": 0, "value": local(output), "evidences": [evidence()]}]}
    if not events:
        value["empty_effect_evidences"] = [evidence()]
    return value


def goal(target, preserve="value", **extra):
    return {"requirement_id": "R1", "target": target, "preserve": preserve,
            "reason": "Preserve only this value, condition or action required by the source.", **extra}


def _fixture(name, lesson, source, instructions, specs):
    graph = {"entry_block_id": "sample", "constraints": [], "edges": [], "declared_context_keys": [],
             "blocks": {"sample": {"block_id": "sample", "block_name": "Independent binding example",
                                     "instructions": instructions, "constraints": [], "data_source_kind": None}}}
    task_candidate = {"purpose": {"text": source, "evidences": [evidence()]},
            "requirements": [{"id": "R1", "text": source, "evidences": [evidence()]}],
            "source_accounting": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "disposition": "requirement", "requirement_ids": ["R1"], "issue_ids": [], "reason": "The complete source obligation of this independent synthetic example."}], "issues": []}
    raw = {"outcome": "completed", "task_revision_id": "pending-example-material", "realizations": [],
           "demands": [], "expressions": [], "ir_semantics": specs, "locations": {}, "location_evidences": {}}
    return {"name": name, "lesson": lesson, "source": source, "cfg": graph, "annotation": raw, "task_candidate": task_candidate, "show": {}}


def example_material(example):
    text = example["source"]
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": text, "sha256": digest}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": digest}])}
    from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files
    task = validate_task_candidate(example["task_candidate"], source_files=task_source_files(source),
                                   source_sha256=source["source_sha256"], basis="declared_skill")
    return prepare_material(source, example["cfg"], task_baseline=task)


def _target(example, pointer):
    current = example["cfg"]
    path = []
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        part = int(token) if isinstance(current, list) else token
        path.append(part)
        current = current[part]
    return cfg_target_from_path(example["cfg"], path)


def _top_goal(example, pointer, preserve="value"):
    return {"requirement_id": "R1", "target": _target(example, pointer), "preserve": preserve,
            "reason": "This target is the actual CFG value position that the source requires preserving."}


def binding_examples():
    examples = []
    selector = {"op": "select_part", "input": inp(), "path": ["label"], "output": "label_value"}
    first = instruction("ir_sample_pick", "extract_label", [literal({"label": "calibration-A"})], "chosen_label")
    ret = instruction("ir_sample_return", "return", [result("chosen_label")])
    base_specs = {"ir_sample_pick": semantics([segment([selector])], "label_value"), "ir_sample_return": semantics()}
    ex = _fixture("operand_object", "A value goal selects the operand object, never its identifier string. A Task binding may still point to descriptive metadata.",
                  "The agent runtime returns the original calibration label internally.", [first, ret], deepcopy(base_specs))
    ex["annotation"]["demands"] = [_top_goal(ex, "/blocks/sample/instructions/0/outputs/0")]
    ex["show"] = {"demands": ex["annotation"]["demands"]}
    examples.append(ex)

    ex = _fixture("return_input", "An ordinary return has a real input and no public output. Bind its input without adding a delivery.",
                  "The agent runtime returns the unchanged calibration label internally.", [deepcopy(first), deepcopy(ret)], deepcopy(base_specs))
    ex["annotation"]["demands"] = [_top_goal(ex, "/blocks/sample/instructions/1/inputs/0")]
    ex["show"] = {"demands": ex["annotation"]["demands"], "return_semantics": ex["annotation"]["ir_semantics"]["ir_sample_return"]}
    examples.append(ex)

    count = {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "slot_count",
             "expression": {"expression": {"op": "count", "arg": {"op": "ref", "value": inp()}}, "evidences": [evidence()]},
             "demands": [goal({"kind": "output"})]}
    ex = _fixture("operation_expression", "An operation expression wraps its AST and evidence. Its goal is attached to the operation output; do not repeat it on the ordinary CFG instruction.",
                  "The agent runtime counts the calibration slots and returns that count internally.",
                  [instruction("ir_sample_count", "count_slots", [literal(["left", "right"])], "counted"), instruction("ir_sample_return", "return", [result("counted")])],
                  {"ir_sample_count": semantics([segment([count])], "slot_count"), "ir_sample_return": semantics()})
    ex["show"] = {"atomic_op": ex["annotation"]["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]}
    examples.append(ex)

    test = {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "is_warm",
            "expression": {"expression": {"op": "gt", "left": {"op": "ref", "value": inp()}, "right": {"op": "literal", "value": 18}}, "evidences": [evidence()]}}
    ex = _fixture("dispatch_scope", "The edge uses the source dispatch input. An already Boolean result is ref(input[0]), not present(input[0]); a local from the previous IR is out of scope.",
                  "The agent runtime tests whether the calibration temperature exceeds 18, then returns that Boolean along the matching branch.",
                  [instruction("ir_sample_test", "test_temperature", [literal(22)], "warm"), instruction("ir_sample_gate", "dispatch", [result("warm")])],
                  {"ir_sample_test": semantics([segment([test])], "is_warm"), "ir_sample_gate": semantics()})
    for block_id, value in (("warm_branch", True), ("cool_branch", False)):
        ir_id = "ir_sample_" + block_id
        ex["cfg"]["blocks"][block_id] = {"block_id": block_id, "block_name": block_id,
            "instructions": [instruction(ir_id, "return", [literal(value)])], "constraints": [], "data_source_kind": None}
        ex["annotation"]["ir_semantics"][ir_id] = semantics()
        ex["cfg"]["edges"].append({"source_block_id": "sample", "target_block_id": block_id,
                                    "condition_text": "warm is " + str(value).lower()})
    ex["annotation"]["expressions"] = [{"target": _target(ex, "/edges/0/condition_text"),
        "expression": {"op": "ref", "value": inp()}, "evidences": [evidence()]}]
    ex["annotation"]["demands"] = [_top_goal(ex, "/blocks/sample/instructions/1/inputs/0", "truth")]
    ex["show"] = {"expressions": ex["annotation"]["expressions"]}
    examples.append(ex)

    delivery = {"op": "deliver", "inputs": [inp(2)], "target": "display",
                "demands": [goal({"kind": "input", "index": 0}, expected=inp(2))]}
    ex = _fixture("two_input_coordinates", "ValueRef input[2] is the IR operand. The attached target input[0] is this delivery's first parameter. They deliberately have different indexes.",
                  "The agent runtime displays only the third supplied calibration value unchanged to the user.",
                  [instruction("ir_sample_display", "display_calibration", [literal("blue"), literal(7), literal("stable")]), instruction("ir_sample_return", "return", [])],
                  {"ir_sample_display": semantics([segment([delivery], "user_output")]), "ir_sample_return": semantics()})
    ex["annotation"]["locations"] = {"display": {"kind": "user", "name": "calibration display", "operand_refs": [], "access_scope": "recipient", "retention": None}}
    ex["annotation"]["location_evidences"] = {"display": [evidence()]}
    ex["show"] = {"atomic_op": ex["annotation"]["ir_semantics"]["ir_sample_display"]["events"][0]["events"][0]["atomic_ops"][0]}
    examples.append(ex)

    filtering = {"op": "filter_items", "input": inp(), "predicate": "calibrated is true", "output": "retained",
                 "expression": {"expression": {"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["calibrated"]}, "evidences": [evidence()]}}
    ex = _fixture("cross_ir_value", "A filter expression is attached to filter_items. The next IR consumes its public result through its own input, never the previous IR's retained local.",
                  "The agent runtime keeps calibrated readings unchanged, then counts and internally returns the number of retained readings.",
                  [instruction("ir_sample_filter", "keep_calibrated", [literal([{"calibrated": True}])], "kept_readings"),
                   instruction("ir_sample_count", "count_readings", [result("kept_readings")], "counted"), instruction("ir_sample_return", "return", [result("counted")])],
                  {"ir_sample_filter": semantics([segment([filtering])], "retained"), "ir_sample_count": semantics([segment([deepcopy(count)])], "slot_count"), "ir_sample_return": semantics()})
    ex["show"] = {"first_operation": ex["annotation"]["ir_semantics"]["ir_sample_filter"]["events"][0]["events"][0]["atomic_ops"][0],
                  "next_operation": ex["annotation"]["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]}
    examples.append(ex)

    member_selector = {**selector, "input": local("reading")}
    member_delivery = {"op": "deliver", "inputs": [local("label_value")], "target": "display",
                       "demands": [goal({"kind": "input", "index": 0}, expected=local("reading"), expected_path=["label"])]}
    scope = {"kind": "for_each", "collection": inp(), "item": "reading", "sensitivity": [], "evidences": [evidence()],
             "body": [segment([member_selector]), segment([member_delivery], "user_output")]}
    ex = _fixture("member_scope", "The field and delivery share one element local inside the scope. No body local escapes to a public IR output or another IR.",
                  "The agent runtime displays each calibration reading's original label to the user, without exporting a collection result.",
                  [instruction("ir_sample_members", "display_labels", [literal([{"label": "north"}])]), instruction("ir_sample_return", "return", [])],
                  {"ir_sample_members": semantics([scope]), "ir_sample_return": semantics()})
    ex["annotation"]["locations"] = deepcopy(examples[4]["annotation"]["locations"])
    ex["annotation"]["location_evidences"] = {"display": [evidence()]}
    ex["show"] = {"for_each": scope}
    examples.append(ex)
    for example in examples:
        task = example_material(example)["task"]
        example["annotation"]["task_revision_id"] = task["task_sha256"]
        example["annotation"]["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
    return examples


def prompt_binding_examples():
    """Independent lessons with direct CFG references, no address directory."""
    return [{"case": ex["name"], "rule": ex["lesson"], "source": ex["source"],
             "cfg": ex["cfg"], "correct_binding": ex["show"]}
            for ex in binding_examples()]


def sink_demand_examples():
    """Executable endpoint lessons with semantically deficient, legal contrasts.

    The contrasts are claims for independent semantic review, not structural
    errors to auto-correct. Every source and CFG here is independently synthetic.
    """
    examples = []

    def finish(example, location):
        example["annotation"]["locations"] = {"endpoint": location}
        example["annotation"]["location_evidences"] = {"endpoint": [evidence()]}
        example["annotation"]["task_revision_id"] = example_material(example)["task"]["task_sha256"]
        example["annotation"]["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
        return example

    user = {"kind": "user", "name": "instrument display", "operand_refs": [],
            "access_scope": "recipient", "retention": None}
    selector = {"op": "select_part", "input": inp(), "path": ["label"], "output": "label"}
    display = {"op": "deliver", "inputs": [local("label")], "target": "endpoint",
               "demands": [goal({"kind": "input", "index": 0}, expected=inp(), expected_path=["label"])]}
    ex = _fixture("field_delivery_endpoint", "A required displayed field is grounded at deliver input[0]; its producer alone is insufficient.",
        "The agent runtime displays the supplied calibration object's original label, without changing it.",
        [instruction("ir_calibration_display", "display_label", [literal({"label": "station-west", "tolerance": 4})]),
         instruction("ir_calibration_return", "return", [])],
        {"ir_calibration_display": semantics([segment([selector]), segment([display], "user_output")]),
         "ir_calibration_return": semantics()})
    finish(ex, user)
    deficient = deepcopy(ex["annotation"])
    ops = deficient["ir_semantics"]["ir_calibration_display"]["events"]
    ops[0]["events"][0]["atomic_ops"][0]["demands"] = [goal({"kind": "output"}, expected=inp(), expected_path=["label"])]
    ops[1]["events"][0]["atomic_ops"][0].pop("demands")
    ex["contrast"] = deficient
    ex["show"] = {"producer": selector, "endpoint": display,
        "insufficient": "Only select_part.output has a seed; this does not flow forward into the display's input demand."}
    examples.append(ex)

    save = {"op": "write", "mode": "append", "target": "endpoint", "input": inp(),
            "demands": [goal({"kind": "self"}, preserve="action"), goal({"kind": "input", "index": 0}, expected=inp())]}
    ex = _fixture("save_content_endpoint", "Preserve both the append action and its newly appended measurement value, not the previous notebook contents.",
        "The agent runtime appends the supplied measurement value unchanged to the instrument notebook.",
        [instruction("ir_instrument_save", "append_measurement", [literal(17.25)]), instruction("ir_instrument_return", "return", [])],
        {"ir_instrument_save": semantics([segment([save], "fs_write")]), "ir_instrument_return": semantics()})
    finish(ex, {"kind": "storage", "name": "instrument notebook", "operand_refs": [], "access_scope": "task", "retention": "persistent"})
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_instrument_save"]["events"][0]["events"][0]["atomic_ops"][0]["demands"].pop()
    ex["show"] = {"endpoint": save, "insufficient": "Keeping only self/action preserves the append behavior, not the specified measurement content."}
    examples.append(ex)

    packet = {"op": "build", "container": "object", "output": "packet", "parts": [
        {"path": ["reading"], "value": inp(0)},
        {"path": ["unit"], "value": inp(1), "when": inp(2)}]}
    delivery = {"op": "deliver", "target": "endpoint", "inputs": [local("packet")], "demands": [
        goal({"kind": "input", "index": 0}, path=["reading"], expected=inp(0)),
        goal({"kind": "input", "index": 0}, path=["unit"], expected=inp(1))]}
    acquire = {"op": "receive", "location": "endpoint", "inputs": [local("packet")], "output": "reply",
               "demands": [goal({"kind": "output"})]}
    interaction = segment([delivery, acquire], None)
    interaction["events"][0].pop("evidences")
    ex = _fixture("conditional_request_endpoint", "Demand the original packet fields at the delivery slot; member guards retain optional inclusion, and reply-driven conservative request retention is separate.",
        "The agent runtime sends a device packet containing the supplied reading unchanged and the original unit only when its supplied Boolean flag is true, then acquires and internally returns the device reply.",
        [instruction("ir_instrument_packet", "device_exchange", [literal(5.5), literal("volts"), literal(True)], "device_reply"),
         instruction("ir_instrument_return", "return", [result("device_reply")])],
        {"ir_instrument_packet": semantics([segment([packet]), interaction], "reply"), "ir_instrument_return": semantics()})
    finish(ex, {"kind": "tool", "name": "instrument interface", "operand_refs": [], "access_scope": "recipient", "retention": None})
    ex["contrast"] = deepcopy(ex["annotation"])
    ex["contrast"]["ir_semantics"]["ir_instrument_packet"]["events"][1]["events"][0]["atomic_ops"][0].pop("demands")
    ex["show"] = {"constructor": packet, "endpoint": delivery, "acquisition": acquire,
        "insufficient": "A demanded reply can conservatively retain its request, but this does not explicitly preserve the packet's required field-original relationships. The Boolean control is not a packet member."}
    examples.append(ex)

    whole = {"op": "deliver", "target": "endpoint", "inputs": [inp()],
             "demands": [goal({"kind": "input", "index": 0})]}
    ex = _fixture("genuine_whole_delivery", "An explicitly required entire object remains a legitimate whole-value demand without a redundant expected.",
        "The agent runtime displays the complete supplied calibration certificate unchanged.",
        [instruction("ir_certificate_display", "display_certificate", [literal({"issuer": "lab", "grade": "A"})]), instruction("ir_certificate_return", "return", [])],
        {"ir_certificate_display": semantics([segment([whole], "user_output")]), "ir_certificate_return": semantics()})
    finish(ex, user)
    ex["show"] = {"endpoint": whole}
    examples.append(ex)

    pulse = {"op": "deliver", "target": "endpoint", "inputs": [], "demands": [goal({"kind": "self"}, "action")]}
    internal = segment([pulse], None)
    internal["events"][0].pop("evidences")
    ex = _fixture("pure_action_no_payload", "A genuinely argument-free action is expressed by its action goal; do not invent a value obligation.",
        "The agent runtime invokes the task-internal indicator's argument-free pulse interface.",
        [instruction("ir_indicator_pulse", "pulse_indicator", []), instruction("ir_indicator_return", "return", [])],
        {"ir_indicator_pulse": semantics([internal]), "ir_indicator_return": semantics()})
    ex["annotation"]["ir_semantics"]["ir_indicator_pulse"]["empty_effect_evidences"] = [evidence()]
    finish(ex, {"kind": "tool", "name": "internal indicator", "operand_refs": [], "access_scope": "task", "retention": None})
    ex["show"] = {"endpoint": pulse}
    examples.append(ex)

    opaque = {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "assessment"}
    ex = _fixture("opaque_result_return", "A demanded opaque result legitimately retains conservative input dependencies; return uses its actual CFG input and needs no redundant expected.",
        "The agent runtime computes an assessment by an unspecified procedure from the supplied instrument record and returns that assessment internally.",
        [instruction("ir_assessment", "assess_record", [literal({"measurement": 2.4, "channel": "north"})], "assessment"),
         instruction("ir_assessment_return", "return", [result("assessment")])],
        {"ir_assessment": semantics([segment([opaque])], "assessment"), "ir_assessment_return": semantics()})
    ex["annotation"]["task_revision_id"] = example_material(ex)["task"]["task_sha256"]
    ex["annotation"]["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
    ex["annotation"]["demands"] = [_top_goal(ex, "/blocks/sample/instructions/1/inputs/0")]
    ex["show"] = {"producer": opaque, "return_demand": ex["annotation"]["demands"][0]}
    examples.append(ex)
    return examples


def prompt_sink_demand_examples():
    """Small source/operation lessons shared by annotator and independent review."""
    return [{"case": ex["name"], "source": ex["source"], "rule": ex["lesson"], **ex["show"]}
            for ex in sink_demand_examples()]
