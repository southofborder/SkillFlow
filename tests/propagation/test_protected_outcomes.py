"""A conditional public value and its memory travel together through dispatch."""

import pytest

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, inp, instruction, literal, local, result,
)
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data.summary import content_options
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.solver import propagate


def protected_call(choice=None):
    source = ("Parse a value and report the result on success. Record a distinct cache marker before "
              "returning or raising, then read it only on the selected branch.")
    call = instruction("ir_call", "parse", [literal(choice)])
    call["outputs"] = [result(name) for name in ("parsed", "error", "completed")]
    fixture = _fixture("protected_call", source, source, [call,
        instruction("ir_route", "dispatch", [result("completed")])], {})
    ev = [evidence()]
    def segment(ops):
        return {"mode": "local", "returns": [], "ops": ops}

    def write(marker):
        return segment([{"op": "write", "mode": "replace", "may": True,
                         "target": "cache", "input": {"kind": "literal", "value": marker}}])

    cases = [
        {"name": "normal", "phase": "normal", "disposition": "return", "condition": "parse returns",
         "segments": [write("normal")], "yield": {"kind": "literal", "value": 7}},
        {"name": "raised", "phase": "local_error", "disposition": "throw", "condition": "parse raises",
         "segments": [write("raised")], "raise": local("__raised__")},
    ]
    if choice is not None:
        for index, case in enumerate(cases):
            case["guard"] = {"input_index": 0, "path": [], "tests": [{"kind": "equals", "value": True}],
                             "outcome": index}
    specs = {
        "ir_call": {"evidences": ev, "segments": [{"kind": "cases", "cases": cases,
            "outcome": {"completion_index": 2, "return_index": 0, "exception_index": 1}}]},
        "ir_route": {"evidences": ev, "segments": [segment([{"op": "branch", "predicate": "selector",
            "input": inp(), "selector": {"path": [], "tests": [{"kind": "equals", "value": True}], "outcome": 0},
            "true_target": "normal", "false_target": "raised"}])]},
    }
    for block, value in (("normal", "parsed"), ("raised", "error")):
        checkout = "ir_read_" + block
        finish = "ir_end_" + block
        fixture["cfg"]["blocks"][block] = {"block_id": block, "block_name": block,
            "instructions": [instruction(checkout, "read", [result(value)], block + "_marker"),
                             instruction(finish, "return", [result(block + "_marker")])]}
        fixture["cfg"]["edges"].append({"source_block_id": "sample", "target_block_id": block,
                                         "condition_text": "parse " + block})
        specs[checkout] = {"evidences": ev, "segments": [segment([
            {"op": "read", "location": "cache", "output": "marker"}])],
            "output_bindings": [{"output_index": 0, "value": local("marker")}]}
        specs[finish] = {"evidences": ev}
    material = example_material(fixture)
    wire = {"outcome": "completed", "ir_semantics": specs, "realizations": [{"requirement_id": "R1"}],
            "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_call", "side": "output",
                "index": 2}, "preserve": "value", "reason": source}],
            "locations": {"cache": {"kind": "runtime_context", "name": "cache", "evidences": ev}}}
    return material, wire


def use_outcome_dispatch(material, wire):
    producer, terminator = material["cfg"]["blocks"]["sample"]["instructions"]
    producer["outputs"].pop()
    terminator["inputs"] = []
    terminator["metadata"]["outcome_dispatch"] = {"producer": producer["id"], "on_return": "normal", "on_throw": "raised"}
    del wire["ir_semantics"]["ir_call"]["segments"][0]["outcome"]["completion_index"]
    wire["ir_semantics"]["ir_route"] = {"evidences": [evidence()]}
    wire["demands"][0]["target"] = {"instruction_id": "ir_read_normal", "side": "output", "index": 0}


@pytest.mark.parametrize("falsey", [None, False, 0, "", [], {}])
def test_disposition_routes_falsey_returns_and_exception_memory_without_a_completion_port(falsey):
    material, wire = protected_call()
    use_outcome_dispatch(material, wire)
    wire["ir_semantics"]["ir_call"]["segments"][0]["cases"][0]["yield"]["value"] = falsey
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    solved.records.validate()
    records = solved.records.records_dict()
    call = records["ir_call"]
    assert all("completion" not in trace for trace in call["outcomes"])
    assert all("completion" not in str(item["data"]["origin"]["at"]) for item in solved.registry.to_dict()["records"])
    observed = records["ir_route"]["outcome_routes"]
    assert {route["target"] for route in observed} == {"normal", "raised"}
    for block in ("normal", "raised"):
        cache = solved.records.get("ir_read_" + block).entry_state.get(FlowLocation(kind="runtime_context", name="cache"))
        assert {v["value"] for identity in cache for v in content_options(solved.registry, identity)
                if v["form"] == "literal"} == {block}
    from skillflow.propagation.records import PropagationRecords, PropagationRecordError
    args = dict(cfg=material["cfg"], annotation=to_payload(compiled), data_registry=solved.registry,
                initial_data=solved.initial_data, initial_state=solved.initial_state)
    restored = PropagationRecords.from_records(records, **args)
    assert restored.records_dict() == records
    observed.pop()
    with pytest.raises(PropagationRecordError, match="feasible case records"):
        PropagationRecords.from_records(records, **args)


def test_zero_payload_cases_keep_distinct_routes_even_with_identical_state():
    material, wire = protected_call()
    use_outcome_dispatch(material, wire)
    producer, _ = material["cfg"]["blocks"]["sample"]["instructions"]
    producer["outputs"] = []
    group = wire["ir_semantics"]["ir_call"]["segments"][0]
    group["outcome"] = {}
    for case in group["cases"]:
        case.pop("yield", None)
        case.pop("raise", None)
        case["segments"] = []
    for target in ("normal", "raised"):
        material["cfg"]["blocks"][target]["instructions"][0]["inputs"] = []
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    assert {row.target for row in solved.records.get("ir_route").outcome_routes} == {"normal", "raised"}
    assert all(not row.values and not row.completion for row in solved.records.get("ir_call").outcomes)


def test_unrouted_missing_completion_and_simultaneous_payload_guard_are_rejected():
    from skillflow.common.validation import StructuralValidationError
    material, wire = protected_call()
    use_outcome_dispatch(material, wire)
    terminator = material["cfg"]["blocks"]["sample"]["instructions"][-1]
    wire["ir_semantics"]["ir_route"]["segments"] = protected_call()[1]["ir_semantics"]["ir_route"]["segments"]
    terminator["inputs"] = [result("parsed")]
    with pytest.raises(StructuralValidationError, match="outcome dispatch"):
        compile_flat_response(wire, material)
    del wire["ir_semantics"]["ir_route"]["segments"]
    del terminator["metadata"]["outcome_dispatch"]
    with pytest.raises(StructuralValidationError, match="without a completion port"):
        compile_flat_response(wire, material)


@pytest.mark.parametrize(("choice", "reached"), [(True, {"normal"}), (False, {"raised"}),
                                                   (None, {"normal", "raised"})])
def test_protected_invocation_routes_whole_state_and_only_available_slots(choice, reached):
    material, wire = protected_call(choice)
    _, _, compiled, _ = compile_flat_response(wire, material)
    runs = [propagate(material["cfg"], to_payload(compiled), schedule=order) for order in ("fifo", "lifo")]
    assert runs[0].records.records_dict() == runs[1].records.records_dict()
    solved = runs[0]
    assert solved.status == "complete", solved.diagnostics
    solved.records.validate()
    call = solved.records.get("ir_call")
    assert len(call.outcomes) == len(reached)
    for block, result_name in (("normal", "parsed"), ("raised", "error")):
        ident = "ir_read_" + block
        if block not in reached:
            assert solved.coverage[ident] == "infeasible"
            assert call.exit_state.get(FlowLocation(kind="result", name=result_name)) is None
            continue
        record = solved.records.get(ident)
        cache = record.entry_state.get(FlowLocation(kind="runtime_context", name="cache"))
        markers = {option["value"] for identity in cache for option in content_options(solved.registry, identity)
                   if option["form"] == "literal"}
        assert markers == {block}
        values = record.entry_state.get(FlowLocation(kind="result", name=result_name))
        assert values == call.exit_state.get(FlowLocation(kind="result", name=result_name))
        if block == "raised":
            assert all(option["form"] == "opaque" for identity in values
                       for option in content_options(solved.registry, identity))


@pytest.mark.parametrize(("phase", "count_send", "count_receive"), [
    ("pre_request_error", 0, 0), ("post_request_error", 1, 0), ("normal", 1, 1)])
@pytest.mark.parametrize("direct", [False, True])
def test_delivery_and_response_are_separate_effects_of_the_selected_case(phase, count_send, count_receive, direct):
    from tests.document_guided.test_case_summaries import tool_contract
    material, wire = protected_call(phase == "normal")
    if direct:
        use_outcome_dispatch(material, wire)
    group = wire["ir_semantics"]["ir_call"]["segments"][0]
    normal, raised = group["cases"]
    contract = tool_contract([[]])
    request = {"op": "deliver", "target": "service", "inputs": [inp()], "input_contract": contract}
    call = {"op": "call", "location": "service", "inputs": [inp()], "output": "reply",
            "input_contract": contract}
    normal["segments"] = [{"mode": "local", "returns": [], "ops": [call]}]
    normal["yield"] = local("reply")
    raised["phase"] = "post_request_error" if phase == "post_request_error" else "pre_request_error"
    raised["segments"] = ([{"mode": "local", "returns": [], "ops": [request]}]
                          if phase == "post_request_error" else [])
    wire["locations"]["service"] = {"kind": "remote", "name": "Search service", "evidences": [evidence()]}
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    record = solved.records.get("ir_call")
    actual_effects = [event.effect for event in record.events
                      if any(not op.skipped_case_inputs for op in event.atomic_ops)]
    assert actual_effects.count("net_send") == count_send
    assert actual_effects.count("net_receive") == count_receive
    assert solved.coverage["ir_end_" + ("normal" if count_receive else "raised")] == "processed"


def test_loop_members_keep_their_exception_and_selector_versions():
    from copy import deepcopy
    material, wire = protected_call(True)
    cfg = material["cfg"]
    template = cfg["blocks"]["sample"]
    specs = wire["ir_semantics"]
    value = {"kind": "literal", "value": [True, False, False]}
    def add(ir, operations=(), outputs=()):
        specs[ir] = {"evidences": [evidence()],
            "segments": [{"mode": "local", "returns": [], "ops": list(operations)}] if operations else [],
            "output_bindings": [{"output_index": i, "value": ref} for i, ref in enumerate(outputs)]}

    def block(name, instructions):
        cfg["blocks"][name] = {**deepcopy(template), "block_id": name, "block_name": name,
                               "instructions": instructions}

    cfg["entry_block_id"] = "seed"
    block("seed", [instruction("ir_seed", "load", [], "items"), instruction("ir_start", "dispatch", [])])
    add("ir_seed", outputs=[value])
    add("ir_start")
    block("head", [instruction("ir_guard", "dispatch", [result("items")])])
    add("ir_guard", [{"op": "branch", "predicate": "has_member", "input": inp(),
                      "true_target": "sample", "false_target": "done"}])
    block("done", [instruction("ir_done", "return", [])])
    add("ir_done")
    template["instructions"][0]["inputs"] = [result("item")]
    template["instructions"].insert(0, instruction("ir_member", "next", [result("items")], "item"))
    add("ir_member", [{"op": "member", "input": inp(), "output": "selected"}], [local("selected")])
    for branch in ("normal", "raised"):
        cfg["blocks"][branch]["instructions"][-1]["opcode"] = "dispatch"
    cfg["edges"].extend({"source_block_id": src, "target_block_id": dst} for src, dst in [
        ("seed", "head"), ("head", "sample"), ("head", "done"), ("normal", "head"), ("raised", "head")])
    _, _, compiled, _ = compile_flat_response(wire, material)
    results = [propagate(cfg, to_payload(compiled), schedule=s) for s in ("fifo", "lifo")]
    assert results[0].records.records_dict() == results[1].records.records_dict()
    solved = results[0]
    assert solved.status == "complete", solved.diagnostics
    rows = solved.records.get("ir_call").outcomes
    assert len(rows) == 3
    errors = set()
    for row in rows:
        source = next(iter(row.selectors))
        flag = next(iter(row.completion))
        assert content_options(solved.registry, flag) == content_options(solved.registry, source)
        if not content_options(solved.registry, flag)[0]["value"]:
            errors.update(row.values)
    assert len(errors) == 2
