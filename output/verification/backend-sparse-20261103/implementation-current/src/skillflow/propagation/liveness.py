"""Static state projection for propagation, independent of Task necessity.

Locations remain live for future operations, routing, and public operand/state
change evidence. Registry Data and operation records are never pruned here.
Projection removes only state bindings; it does not join distinct relation rows.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from skillflow.propagation.contracts.specs import iter_scoped_events
from skillflow.propagation.contracts.uses import active_value_uses
from skillflow.propagation.models import FlowLocation


@dataclass(frozen=True)
class StateLiveness:
    block_in: dict[str, frozenset[FlowLocation]]
    before: dict[str, frozenset[FlowLocation]]
    after: dict[str, frozenset[FlowLocation]]

    @staticmethod
    def project(state, locations):
        """Keep a row's own versions; an empty projected row is reachable."""
        return {location: identities for location, identities in state.items()
                if location in locations and identities}


def _operand_locations(ir, side, index, interpreter):
    operand = ir.get(side + "s", [])[index]
    if operand["type"] == "literal":
        return set()
    if operand["type"] == "result":
        return {FlowLocation(kind="result", name=operand["identifier"])}
    locations = set(interpreter.operand_locations.get((ir["id"], side, index), ()))
    if operand["type"] == "context_key" and side == "input":
        locations.update(interpreter.context_locations(ir, index))
    return {alias for location in locations for alias in interpreter.aliases(location)}


def _ref_locations(ref, ir, interpreter):
    kind = ref.kind
    if kind == "input":
        return _operand_locations(ir, "input", ref.index, interpreter)
    if kind == "alternatives":
        return set().union(*(_ref_locations(child, ir, interpreter) for child in ref.items))
    return set()


def _ambient_locations(ir, block_id, interpreter):
    """Match the interpreter's implicit dominating member-control reads."""
    registry = interpreter.registry
    locations = set()
    for scope, source in getattr(registry, "member_sources", {}).items():
        owner = registry.member_scopes.get(scope)
        if owner in registry.region_blocks and block_id not in registry.region_blocks[owner]:
            continue
        source_block = registry.ir_blocks.get(source["ir"])
        if source_block not in registry.dominators.get(block_id, {block_id}):
            continue
        if source["ir"] == ir["id"]:
            # Same-IR controls are local values, not an incoming state read.
            continue
        if source_block == block_id and registry.ir_orders[source["ir"]] >= registry.ir_orders[ir["id"]]:
            continue
        locations.update(FlowLocation(kind="result", name=name) for name in source["results"])
    return locations


def _route_location(operation, ir, spec):
    """The condition binding must survive until block-level guard routing."""
    ref = operation.input
    if ref.kind == "input":
        operand = ir.get("inputs", [])[ref.index]
        kind = {"result": "result", "context_key": "runtime_context"}.get(operand["type"])
        return {FlowLocation(kind=kind, name=operand["identifier"])} if kind else set()
    if ref.kind == "local":
        return {FlowLocation(kind="result", name=ir["outputs"][binding.output_index]["identifier"])
                for binding in spec.output_bindings
                if binding.value.kind == "local" and binding.value.name == ref.name}
    return set()


def calculate_liveness(cfg, annotation, interpreter, successors):
    """Calculate all future computation/evidence uses on the finite CFG.

    Specifications are the interpreter's once-validated compiled objects.
    Only unconditional, exact strong writes and public result assignments can
    kill bindings. Conditional cases, may writes, aliases and partial orders
    conservatively retain the incoming version. No Task fields are inspected.
    """
    uses, definitions, exit_evidence, routing = {}, {}, {}, {}
    for block_id, block in cfg["blocks"].items():
        routing[block_id] = set()
        for ir in block["instructions"]:
            identity = ir["id"]
            read = set().union(*(_operand_locations(ir, "input", index, interpreter)
                                 for index in range(len(ir.get("inputs", [])))))
            retained = set().union(*(_operand_locations(ir, "output", index, interpreter)
                                     for index in range(len(ir.get("outputs", [])))))
            defined = set()
            spec = interpreter.specs.get(identity)
            if spec is not None:
                read.update(_ambient_locations(ir, block_id, interpreter))
                for binding in spec.output_bindings:
                    read.update(_ref_locations(binding.value, ir, interpreter))
                    operand = ir["outputs"][binding.output_index]
                    if operand["type"] == "result":
                        defined.add(FlowLocation(kind="result", name=operand["identifier"]))
                for event in spec.events:
                    if getattr(event, "kind", None) == "for_each":
                        read.update(_ref_locations(event.collection, ir, interpreter))
                        if event.yield_value is not None:
                            read.update(_ref_locations(event.yield_value, ir, interpreter))
                for _, body_index, event in iter_scoped_events(spec):
                    for operation in event.atomic_ops:
                        for use in active_value_uses(operation, ir):
                            read.update(_ref_locations(use.value, ir, interpreter))
                        if operation.op == "read":
                            read.update(interpreter.aliases(interpreter.locations[operation.location]))
                        elif operation.op == "write":
                            target = interpreter.locations[operation.target]
                            aliases = set(interpreter.aliases(target))
                            # Before/after are published evidence even for a
                            # definite overwrite/delete with no future read.
                            read.update(aliases)
                            retained.update(aliases)
                            if (body_index is None and event.case is None and spec.order == "fixed"
                                    and not operation.may and not target.name.startswith("symbolic:")
                                    and operation.mode in {"replace", "delete"}):
                                defined.add(target)
                        elif operation.op == "branch":
                            routing[block_id].update(_route_location(operation, ir, spec))
            uses[identity], definitions[identity], exit_evidence[identity] = read, defined, retained

    blocks = cfg["blocks"]
    block_in = {block: frozenset() for block in blocks}
    before, after = {}, {}
    predecessors = {block: set() for block in blocks}
    for source, targets in successors.items():
        for target in targets:
            predecessors[target].add(source)
    queue, queued = deque(reversed(list(blocks))), set(blocks)
    while queue:
        block_id = queue.popleft()
        queued.remove(block_id)
        live = set(routing[block_id])
        for target in successors.get(block_id, ()):
            live.update(block_in[target])
        for ir in reversed(blocks[block_id]["instructions"]):
            identity = ir["id"]
            live.update(exit_evidence[identity])
            after[identity] = frozenset(live)
            live = uses[identity] | (live - definitions[identity])
            before[identity] = frozenset(live)
        incoming = frozenset(live)
        if incoming != block_in[block_id]:
            block_in[block_id] = incoming
            for predecessor in sorted(predecessors[block_id]):
                if predecessor not in queued:
                    queued.add(predecessor)
                    queue.append(predecessor)
    return StateLiveness(block_in=block_in, before=before, after=after)
