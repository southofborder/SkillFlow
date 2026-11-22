"""Independent unknown values stay separate; actual unknown addresses may alias."""
from copy import deepcopy

import pytest

from skillflow.propagation import FlowLocation, FlowState, propagate
from skillflow.propagation.data import DataRegistry, LiteralContent, DataReferenceError
from skillflow.propagation.interpreter import TransferInterpreter
from tests.propagation.test_solver import annotation_for, instruction, operand, input_ref, local, literal


def loc(name, kind="runtime_context"):
    return FlowLocation(kind=kind, name=name)


def source_linear(instructions, plans, locations):
    blocks, edges = {}, []
    for index, ir in enumerate(instructions):
        name = f"b{index}"
        block = {"block_id": name, "block_name": name,
                 "instructions": [ir, instruction(f"end{index}", opcode="dispatch" if index + 1 < len(instructions) else "return")]}
        if any(value["type"] == "context_key" for value in ir["inputs"]):
            block["data_source_kind"] = "context"
        blocks[name] = block
        if index:
            edges.append({"source_block_id": f"b{index - 1}", "target_block_id": name})
    cfg = {"entry_block_id": "b0", "blocks": blocks, "edges": edges,
           "declared_context_keys": [v["identifier"] for ir in instructions for v in ir["inputs"] if v["type"] == "context_key"]}
    return annotation_for(cfg, plans, locations)


def exception_and_urls(*, name="protected_call.exception", address_kind="identified"):
    cfg, annotation = source_linear([
        instruction("read_exception", outputs=["E"]),
        instruction("inspect_exception", [operand("E")], ["field"]),
        instruction("copy_urls", [operand("caller.urls", "context_key")], ["U"]),
        instruction("map_urls", [operand("U")], ["M"]),
    ], {
        "read_exception": (["context_read"], [(0, [{"op": "read", "location": "error", "output": "e"}])], [local("e")]),
        "inspect_exception": (["transform"], [(0, [{"op": "select_part", "input": input_ref(), "path": ["metrics"], "output": "m"}])], [local("m")]),
        "copy_urls": ([], [], [input_ref()]),
        "map_urls": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref()], "dependencies": ["possible"], "output": "mapped"}])], [local("mapped")]),
    }, {"error": ("runtime_context", "protected_call.exception")})
    annotation["locations"]["error"].update(name=name, address_kind=address_kind)
    if address_kind == "unidentified":
        annotation["locations"]["error"]["address_reason"] = "This fixture explicitly selects an unknown context address."
    spec = annotation["ir_semantics"]["ir_map_urls"]
    evidence = deepcopy(spec["events"][0]["evidences"])
    spec["events"] = [{"kind": "for_each", "collection": input_ref(), "item": "url", "evidences": evidence,
        "body": [{"effect": "transform", "evidences": evidence,
            "atomic_ops": [{"op": "compute", "inputs": [local("url")], "dependencies": ["possible"],
                            "output": "path", "evidences": evidence}]}],
        "yield": local("path"), "output": "mapped"}]
    registry = DataRegistry("runtime-address-locality")
    urls = registry.register_source("urls", acquired_from="runtime_context:caller.urls", content=LiteralContent(value=["/a", "/a"]))
    error = registry.register_source("error", acquired_from="runtime_context:" + name)
    state = FlowState.from_mapping({loc("caller.urls"): frozenset([urls.id]), loc(name): frozenset([error.id])})
    return cfg, annotation, registry, state, urls.id, error.id


@pytest.mark.parametrize("name", ["protected_call.exception", "symbolic:unknown exception content"])
@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_unknown_exception_payload_does_not_contaminate_independent_urls(name, schedule):
    cfg, annotation, registry, state, urls, error = exception_and_urls(name=name)
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state, schedule=schedule)
    assert result.status == "complete"
    copied = result.records.get("ir_copy_urls").exit_state.get(loc("U", "result"))
    assert copied == frozenset([urls]) and error not in copied
    loop = result.records.get("ir_map_urls").events[0]
    assert len(loop.instances) == 2
    # The observed exception remains a real read and its probed field remains
    # represented; isolating its address must not erase its observations.
    read = result.records.get("ir_read_exception").events[0].atomic_ops[0]
    assert read.outputs == [frozenset([error])]
    assert result.registry.get(error).content.parts[0].path == ["metrics"]
    assert result.registry.get(urls).content == LiteralContent(value=["/a", "/a"])


def test_real_unidentified_runtime_address_includes_implicit_context_slots():
    cfg, annotation, registry, state, urls, error = exception_and_urls(address_kind="unidentified")
    engine = TransferInterpreter(cfg, annotation, registry)
    address = engine.locations["error"]
    assert engine.is_unknown_address(address)
    assert loc("caller.urls") in engine.aliases(address)
    assert address in engine.aliases(loc("caller.urls"))
    mapping = {row.location: row.data_ids for row in state.bindings}
    assert engine.read_location(address, mapping) == frozenset([urls, error])
    assert engine.read_location(loc("caller.urls"), mapping) == frozenset([urls, error])


@pytest.mark.parametrize("mode", ["replace", "delete"])
def test_unknown_address_writes_remain_weak_for_implicit_caller_slots(mode):
    cfg, annotation = source_linear([
        instruction("unknown_write"),
        instruction("copy", [operand("caller.value", "context_key")], ["out"]),
    ], {"unknown_write": (["context_write"], [(0, [{"op": "write", "target": "dynamic", "mode": mode,
             **({"input": literal("new")} if mode == "replace" else {})}])], []),
        "copy": ([], [], [input_ref()])}, {"dynamic": ("runtime_context", "selected-address")})
    annotation["locations"]["dynamic"].update(address_kind="unidentified", address_reason="A caller-selected address can equal caller.value.")
    registry = DataRegistry("unknown-write")
    original = registry.register_source("value", acquired_from="runtime_context:caller.value")
    state = FlowState.from_mapping({loc("caller.value"): frozenset([original.id])})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.status == "complete"
    copied = result.records.get("ir_copy").exit_state.get(loc("out", "result"))
    assert original.id in copied
    changes = result.records.get("ir_unknown_write").events[0].atomic_ops[0].changes
    assert next(x for x in changes if x.location == loc("caller.value")).update == "weak"
    assert len(copied) == (2 if mode == "replace" else 1)


def test_same_spelling_other_address_kind_does_not_alias():
    cfg, annotation, registry, _, _, _ = exception_and_urls(address_kind="unidentified")
    engine = TransferInterpreter(cfg, annotation, registry)
    assert loc("protected_call.exception", "storage") not in engine.aliases(engine.locations["error"])


def test_identified_source_with_object_content_keeps_strict_collection_guard():
    registry = DataRegistry("not-an-array")
    obj = registry.register_source("object", acquired_from="runtime_context:known-object")
    registry.resolve_part(obj.id, ["field"])
    with pytest.raises(DataReferenceError, match="object fields cannot be treated"):
        registry.resolve_iteration_entries(obj.id, "member-scope")
