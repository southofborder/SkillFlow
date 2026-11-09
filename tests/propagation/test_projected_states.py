"""Projection retains future computations, relation controls and evidence."""
from copy import deepcopy

from skillflow.propagation.contracts.specs import IRSemantics
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.liveness import calculate_liveness
from skillflow.propagation.loop_domain import LoopFactRegistry
from skillflow.propagation.models import FlowLocation


EVIDENCE = [{"target": {"path": []}, "reason": "An authored projection regression."}]


def location(name, kind="result"):
    return FlowLocation(kind=kind, name=name)


def ref(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"kind": "literal", "value": value}


def ir(identity, inputs=(), outputs=()):
    return {"id": identity, "inputs": [value if isinstance(value, dict) else
            {"type": "result", "identifier": value} for value in inputs],
            "outputs": [{"type": "result", "identifier": value} for value in outputs]}


def spec(operations=(), outputs=(), *, events=None, order="fixed"):
    if events is None:
        events = [{"effect": None, "atomic_ops": [
            {**operation, "evidences": EVIDENCE} for operation in operations]}] if operations else []
    return IRSemantics.model_validate({"operator": [],
        "operator_evidences": [{**EVIDENCE[0], "value": None}], "order": order, "precedence": [],
        "events": events, "output_bindings": [{"output_index": index, "value": value,
            "evidences": EVIDENCE} for index, value in enumerate(outputs)]})


def prepare(blocks, specs, edges=(), locations=None, *, regions=None, dominators=None):
    cfg = {"blocks": {name: {"instructions": values} for name, values in blocks.items()}}
    annotation = {"locations": locations or {}, "ir_semantics": {
        identity: value.model_dump(mode="json") for identity, value in specs.items()}}
    registry = LoopFactRegistry(DataRegistry("projected-state-test"), {})
    registry.ir_blocks = {value["id"]: name for name, values in blocks.items() for value in values}
    registry.ir_orders = {value["id"]: index for values in blocks.values() for index, value in enumerate(values)}
    registry.dominators = dominators or {name: {name} for name in blocks}
    registry.regions = regions or {}
    registry.region_blocks = {owner: set(blocks) for owner in registry.regions.values()}
    engine = TransferInterpreter(cfg, annotation, registry, typed_specs=specs)
    engine.prepare_member_metadata()
    successors = {name: set() for name in blocks}
    for source, target in edges:
        successors[source].add(target)
    return engine, calculate_liveness(cfg, annotation, engine, successors)


def test_dead_result_drops_after_its_own_output_evidence():
    blocks = {"entry": [ir("seed", outputs=("old", "used")), ir("middle"), ir("send", ("used",))]}
    specs = {"seed": spec(outputs=(literal("discarded"), literal("retained"))),
             "middle": spec(), "send": spec()}
    _, live = prepare(blocks, specs)
    assert location("old") in live.after["seed"]
    assert location("old") not in live.before["middle"]
    assert location("used") in live.before["middle"]
    assert location("used") in live.before["send"]  # Public operand, even without an atomic use.
    assert live.block_in["entry"] == frozenset()


def test_projection_preserves_each_rows_versions_and_reachable_empty_state():
    _, live = prepare({"b": [ir("noop")]}, {"noop": spec()})
    first = {location("x"): frozenset({"version_a"}), location("dead"): frozenset({"old"})}
    second = {location("x"): frozenset({"version_b"})}
    assert live.project(first, {location("x")}) == {location("x"): frozenset({"version_a"})}
    assert live.project(second, {location("x")}) == {location("x"): frozenset({"version_b"})}
    assert live.project(first, set()) == {}
    assert location("dead") in first


def test_branch_condition_survives_later_ir_until_block_routing():
    blocks = {"b": [ir("guard", ("condition",)), ir("tail")],
              "yes": [ir("yes")], "no": [ir("no")]}
    specs = {"guard": spec([{"op": "branch", "input": ref(), "predicate": "truthy",
                               "true_target": "yes", "false_target": "no"}]),
             "tail": spec(), "yes": spec(), "no": spec()}
    _, live = prepare(blocks, specs, [("b", "yes"), ("b", "no")])
    assert location("condition") in live.after["tail"]
    assert location("condition") in live.before["tail"]
    assert location("condition") not in live.block_in["yes"]


def test_local_branch_output_is_kept_for_routing_without_a_future_reader():
    blocks = {"b": [ir("guard", outputs=("condition",)), ir("tail")], "exit": [ir("exit")]}
    specs = {"guard": spec([{"op": "compute", "inputs": [literal(True)],
                              "dependencies": ["possible"], "output": "condition"},
                             {"op": "branch", "input": local("condition"), "predicate": "truthy",
                              "true_target": "exit", "false_target": "exit"}], [local("condition")]),
             "tail": spec(), "exit": spec()}
    _, live = prepare(blocks, specs, [("b", "exit")])
    assert location("condition") in live.after["tail"]
    assert location("condition") not in live.before["guard"]


def test_reads_and_write_evidence_keep_symbolic_aliases_and_prior_versions():
    locations = {name: {"kind": "storage", "name": name, "operand_refs": []}
                 for name in ("cache", "symbolic:file")}
    blocks = {"b": [ir("read"), ir("append"), ir("delete"), ir("tail")]}
    specs = {"read": spec([{"op": "read", "location": "cache", "output": "read"}]),
             "append": spec([{"op": "write", "target": "cache", "mode": "append", "input": literal("value")}]),
             "delete": spec([{"op": "write", "target": "cache", "mode": "delete"}]), "tail": spec()}
    _, live = prepare(blocks, specs, locations=locations)
    expected = {location("cache", "storage"), location("symbolic:file", "storage")}
    assert expected <= live.before["read"]
    assert expected <= live.before["append"]
    assert expected <= live.before["delete"]
    assert expected <= live.after["delete"]
    assert not expected & live.before["tail"]


def test_context_input_evidence_uses_declared_location_anchors():
    inputs = [{"type": "context_key", "identifier": "input_name"}]
    locations = {"actual": {"kind": "storage", "name": "actual", "operand_refs": [
        {"instruction_id": "read", "side": "input", "index": 0}]}}
    _, live = prepare({"b": [ir("read", inputs)]}, {"read": spec()}, locations=locations)
    assert location("actual", "storage") in live.before["read"]
    assert location("input_name", "runtime_context") not in live.before["read"]


def test_member_inventory_is_static_and_ambient_control_is_live_without_explicit_use():
    blocks = {"body": [ir("member", ("items",), ("row",)), ir("observe"), ir("tail")],
              "outside": [ir("outside")]}
    specs = {"member": spec([{"op": "member", "input": ref(), "output": "row"}], [local("row")]),
             "observe": spec([{"op": "compute", "inputs": [literal(1)],
                                "dependencies": ["possible"], "output": "constant"}]),
             "tail": spec(), "outside": spec()}
    engine, live = prepare(blocks, specs, regions={"member": "body", "observe": "body", "tail": "body"})
    inventory = deepcopy(engine.registry.member_sources)
    assert len(inventory) == 1
    assert location("row") in live.before["observe"]
    assert location("row") not in live.before["member"]
    assert location("row") not in live.before["outside"]
    engine.prepare_member_metadata()
    assert engine.registry.member_sources == inventory


def test_backedge_keeps_future_merge_inputs_while_irrelevant_values_die():
    blocks = {"head": [ir("merge", ("initial", "next"), ("acc",))],
              "body": [ir("advance", ("acc",), ("next", "discarded"))]}
    specs = {"merge": spec([{"op": "merge", "incoming": [
        {"predecessor": "entry", "value": ref()}, {"predecessor": "body", "value": ref(1)}],
        "output": "selected"}], [local("selected")]),
        "advance": spec(outputs=[ref(), literal("unused")])}
    _, live = prepare(blocks, specs, [("head", "body"), ("body", "head")])
    assert location("next") in live.block_in["head"]
    assert location("acc") in live.block_in["body"]
    assert location("discarded") in live.after["advance"]
    assert location("discarded") not in live.block_in["head"]
