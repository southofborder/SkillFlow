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
    if kind in {"cfg", "processing"}:
        payload["aligned_boundary_examples"] = alignment_examples()
    return "VALIDATED FORMAT EXAMPLE (synthetic; names and citations are not target evidence)\n" + compact_json(payload)


def alignment_examples():
    """Small connected pairs, rather than another disconnected operation catalog.

    Numbering mirrors the public graph compiler and is checked by compilation
    tests. These examples run no compiler or validator while preparing a prompt.
    """
    def result(name):
        return {"type": "result", "identifier": name}

    def literal(value):
        return {"type": "literal", "literal_value": value}

    def inp(index=0):
        return {"kind": "input", "index": index}

    def ir(opcode, inputs=(), output=None):
        value = {"opcode": opcode}
        if inputs:
            value["inputs"] = list(inputs)
        if output is not None:
            value["outputs"] = [result(output)]
        return value

    def spec(ops=(), output=None):
        value = {"evidences": [deepcopy(EVIDENCE)]}
        if ops:
            value["segments"] = [{"mode": "local", "returns": [], "ops": list(ops)}]
        if output is not None:
            value["output_bindings"] = [{"output_index": 0, "value": output}]
        return value

    def pair(source, blocks, edges, specifications, locations=None):
        # Only demonstration coordinates change. Real prompt responses use the
        # supplied current CFG's IDs, never infer them from this example.
        refs = {block["block_ref"]: f"block_{index + 1:03d}" for index, block in enumerate(blocks)}
        for item in specifications:
            for segment in item.get("segments", []):
                for operation in segment["ops"]:
                    if operation["op"] == "branch":
                        for key in ("true_target", "false_target"):
                            operation[key] = refs[operation[key]]
        return {"source": source, "cfg": {"entry_block_ref": blocks[0]["block_ref"], "blocks": blocks,
                    "edges": [{"source_block_ref": a, "target_block_ref": b} for a, b in edges]},
                "processing": {"locations": locations or {}, "ir_semantics": {
                    f"ir_{index + 1:03d}": value for index, value in enumerate(specifications)}}}

    service = {"service": {"kind": "tool", "name": "Service", "evidences": [deepcopy(EVIDENCE)]}}
    call = {"op": "call", "location": "service", "inputs": [inp()], "output": "response"}
    caller = pair("Acquire request from context; helper(request) calls Service(request) and returns its actual response.", [
        {"block_ref": "entry", "data_source_kind": "context", "instructions": [
            ir("acquire_request", [{"type": "context_key", "identifier": "request"}], "request_value"), ir("dispatch")]},
        {"block_ref": "caller", "instructions": [ir("helper_call", [result("request_value")], "reply"), ir("return", [result("reply")])]}],
        [("entry", "caller")], [
            spec([{"op": "read", "location": "request", "output": "acquired"}], {"kind": "local", "name": "acquired"}),
            spec(), spec([deepcopy(call)], {"kind": "local", "name": "response"}), spec()],
        {**deepcopy(service), "request": {"kind": "runtime_context", "name": "request", "access_scope": "task",
            "retention": "task", "evidences": [deepcopy(EVIDENCE)]}})
    traversal = pair("For each URL in ['same','same'], call Service(URL); return the original URL list after traversal.", [
        {"block_ref": "entry", "instructions": [ir("urls", [literal(["same", "same"])], "urls"), ir("dispatch")]},
        {"block_ref": "head", "instructions": [ir("dispatch", [result("urls")])]},
        {"block_ref": "body", "instructions": [ir("current_member", [result("urls")], "url"),
            ir("fetch", [result("url")], "reply"), ir("dispatch")]},
        {"block_ref": "exit", "instructions": [ir("return", [result("urls")])]}],
        [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")], [
            spec(output=inp()), spec(), spec([{"op": "branch", "input": inp(), "predicate": "has_member",
                "true_target": "body", "false_target": "exit"}]),
            spec([{"op": "member", "input": inp(), "output": "element"}], {"kind": "local", "name": "element"}),
            spec([deepcopy(call)], {"kind": "local", "name": "response"}), spec(), spec()], deepcopy(service))
    binary = pair("Given ready=false and retry=true, return 'ready' if ready, else 'retry' if retry, else 'stop'.", [
        {"block_ref": "ready_check", "instructions": [ir("dispatch", [literal(False)])]},
        {"block_ref": "retry_check", "instructions": [ir("dispatch", [literal(True)])]},
        {"block_ref": "ready", "instructions": [ir("return", [literal("ready")])]},
        {"block_ref": "retry", "instructions": [ir("return", [literal("retry")])]},
        {"block_ref": "stop", "instructions": [ir("return", [literal("stop")])]}],
        [("ready_check", "ready"), ("ready_check", "retry_check"), ("retry_check", "retry"), ("retry_check", "stop")], [
            spec([{"op": "branch", "input": inp(), "predicate": "truthy", "true_target": "ready", "false_target": "retry_check"}]),
            spec([{"op": "branch", "input": inp(), "predicate": "truthy", "true_target": "retry", "false_target": "stop"}]),
            spec(), spec(), spec()])
    return {"caller_boundary": caller, "guard_then_member": traversal, "binary_outcome_routing": binary}


def example_material():
    """Offline fixture for validating the exact prompt records, not a model call."""
    from skillflow.propagation.annotation.binding_examples import _fixture, example_material as prepare, instruction, literal, result
    return prepare(_fixture("compact-interface", "Yield an existing value without a fake operation.", SOURCE,
        [instruction("ir_call", "get_replies", [literal(["a", "a"]), literal("cached")], "replies"),
         instruction("ir_return", "return", [result("replies")])], {}))
