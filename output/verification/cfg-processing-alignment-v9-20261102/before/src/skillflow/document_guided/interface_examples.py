"""Small executable interface examples; never additional target material.

These are ordinary JSON records, validated by the same validators in tests.
They introduce neither a second validator nor a new instruction language.
"""
from copy import deepcopy

from skillflow.common.prompt_format import compact_json


SOURCE = (
    "For each requested URL, use the supplied cached reply when available; otherwise call Service with that URL. "
    "Return the reply list preserving repeated URLs. Cached replies may contain credentials."
)
EVIDENCE = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}
CALL_PATH = ["segments", 0, "body", 0, "cases", 1, "segments", 0, "ops", 0]


def example_fragments():
    processing = {
        "locations": {"service": {"kind": "tool", "name": "Service", "evidences": [deepcopy(EVIDENCE)]}},
        "ir_semantics": {
            "ir_call": {
                "evidences": [deepcopy(EVIDENCE)],
                "segments": [{"kind": "for_each", "collection": {"kind": "input", "index": 0}, "item": "url",
                    "body": [{"kind": "cases", "output": "chosen", "cases": [
                        {"name": "cached", "phase": "normal", "disposition": "return",
                         "condition": "The supplied cached reply is available.", "segments": [],
                         "yield": {"kind": "input", "index": 1}},
                        {"name": "requested", "phase": "normal", "disposition": "return",
                         "condition": "No cached reply is available; the call returns normally.",
                         "segments": [{"mode": "local", "returns": [], "ops": [
                             {"op": "call", "location": "service", "inputs": [{"kind": "local", "name": "url"}],
                              "output": "reply"}]}], "yield": {"kind": "local", "name": "reply"}}]}],
                    "yield": {"kind": "local", "name": "chosen"}, "output": "replies"}],
                "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "replies"}}]},
            "ir_return": {"evidences": [deepcopy(EVIDENCE)]}}}
    mapping = {"realizations": [{"requirement_id": "R1"}], "demands": [
        {"requirement_id": "R1", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
         "preserve": "value", "reason": "The source requires the full reply list, including cached candidates and repeats."}],
        "operation_demands": [
        {"instruction_id": "ir_call", "operation_path": list(CALL_PATH), "demands": [
            {"requirement_id": "R1", "target": {"kind": "self"}, "preserve": "action",
             "reason": "The source requires the fallback request when a cached reply is unavailable."},
            {"requirement_id": "R1", "target": {"kind": "input", "index": 0}, "preserve": "value",
             "reason": "That request must use this occurrence's original URL."}]}]}
    sensitivity = {"declarations": [{"instruction_id": "ir_call", "scope_path": ["segments", 0],
        "case_path": ["segments", 0, "body", 0, "cases", 0],
        "value": {"kind": "input", "index": 1}, "label": "Credential"}]}
    return {"processing": processing, "task-correspondence": mapping, "sensitivity": sensitivity}


def example_cfg():
    return {"entry_block_ref": "entry", "blocks": [{"block_ref": "entry", "instructions": [
        {"opcode": "get_replies", "inputs": [{"type": "literal", "literal_value": ["a", "a"]},
            {"type": "literal", "literal_value": "cached"}],
         "outputs": [{"type": "result", "identifier": "replies"}]},
        {"opcode": "return", "inputs": [{"type": "result", "identifier": "replies"}]}]}]}


def loop_operation_examples():
    """Existing op variants, with the CFG/operand context needed to interpret them."""
    return {
        "merge": {"context": "Header incoming blocks are entry/body; input 0 is the initial collection and input 1 its backedge update.",
            "operation": {"op": "merge", "incoming": [
                {"predecessor": "entry", "value": {"kind": "input", "index": 0}},
                {"predecessor": "body", "value": {"kind": "input", "index": 1}}], "output": "selected"}},
        "member": {"context": "Inside the loop body, input 0 is its source collection.",
            "operation": {"op": "member", "input": {"kind": "input", "index": 0}, "output": "row"}},
        "branch": {"context": "The header terminator receives the source collection; its actual successors are body/exit.",
            "operation": {"op": "branch", "input": {"kind": "input", "index": 0}, "predicate": "has_member",
                "true_target": "body", "false_target": "exit"}},
        "append": {"context": "Input 0 is the accumulated collection; input 1 is this member's response.",
            "operation": {"op": "append", "input": {"kind": "input", "index": 0},
                "value": {"kind": "input", "index": 1}, "mode": "item", "output": "collected"}},
    }


def phase_examples(kind):
    """Pure, bounded prompt text; ownership and context are explicit."""
    if kind == "cfg":
        response, context = example_cfg(), {"source": SOURCE}
    else:
        kind = "task-correspondence" if kind == "mapping" else kind
        response = example_fragments()[kind]
        context = {"source": SOURCE, "instructions": {
            "ir_call": {"inputs": [["a", "a"], "cached"], "outputs": ["replies"]},
            "ir_return": {"inputs": ["replies"], "outputs": []}}}
        if kind == "task-correspondence":
            context["task_requirement"] = {"id": "R1", "text": "Return the reply list preserving repeated URLs."}
            context["existing_call_path"] = list(CALL_PATH)
        elif kind == "sensitivity":
            context["existing_cases"] = {"scope": ["segments", 0], "cached": ["segments", 0, "body", 0, "cases", 0]}
    payload = {"context": context, "response": response}
    if kind == "processing":
        payload["additional_operation_forms"] = loop_operation_examples()
    return "VALIDATED FORMAT EXAMPLE (synthetic; names and citations are not target evidence)\n" + compact_json(payload)


def example_material():
    """Offline fixture for validating the exact prompt records, not a model call."""
    from skillflow.propagation.annotation.binding_examples import _fixture, example_material as prepare, instruction, literal, result
    return prepare(_fixture("compact-interface", "Yield an existing value without a fake operation.", SOURCE,
        [instruction("ir_call", "get_replies", [literal(["a", "a"]), literal("cached")], "replies"),
         instruction("ir_return", "return", [result("replies")])], {}))
