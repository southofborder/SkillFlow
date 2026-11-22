"""Unavailable values travel with execution rows, never as invented Data."""
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.contracts.specs import iter_scoped_events
from skillflow.propagation.contracts.uses import active_value_uses
from skillflow.propagation.liveness import _ambient_locations, _operand_locations, _ref_locations


class FailureRow(dict):
    def __init__(self, state=(), *, unavailable=None, controls=None):
        super().__init__(state)
        self.unavailable = dict(unavailable or {})
        self.controls = dict(controls or {})

    def __eq__(self, other):
        return (dict.__eq__(self, other) and self.unavailable == getattr(other, "unavailable", {})
                and self.controls == getattr(other, "controls", {}))

    def __ne__(self, other):
        return not self == other

    def project(self, keep):
        return FailureRow({loc: ids for loc, ids in self.items() if loc in keep and ids},
            unavailable={loc: causes for loc, causes in self.unavailable.items() if loc in keep},
            controls=self.controls)

    def with_state(self, state):
        return FailureRow(state, unavailable=self.unavailable, controls=self.controls)


def row_failure_key(state):
    return (tuple(sorted((loc.kind, loc.name, tuple(sorted(causes)))
                         for loc, causes in getattr(state, "unavailable", {}).items())),
            tuple(sorted((cause, join or "") for cause, join in getattr(state, "controls", {}).items())))


def dependencies(ir, spec, interpreter, block, predecessor, state):
    """Read actual declared uses; a strong overwrite does not read old content."""
    reads = set(_ambient_locations(ir, block, interpreter))
    writes, clears, state_evidence = set(), set(), set()
    controls = ir["opcode"] == "dispatch"
    def false_guard(ref):
        if ref is None:
            return False
        if ref.kind == "literal":
            return ref.value is False
        if ref.kind == "alternatives":
            return bool(ref.items) and all(false_guard(child) for child in ref.items)
        if ref.kind != "input":
            return False
        locations = _operand_locations(ir, "input", ref.index, interpreter)
        if not locations or any(loc in state.unavailable for loc in locations):
            return False
        ids = set().union(*(state.get(loc, ()) for loc in locations))
        if not ids:
            return False
        # Only direct concrete Boolean candidates establish absence of use.
        # Opaque values and relations are never evaluated as Python truthiness.
        contents = [interpreter.registry.get(identity).content for identity in ids]
        return all(content.form == "literal" and content.value is False for content in contents)
    for binding in spec.output_bindings:
        reads.update(_ref_locations(binding.value, ir, interpreter))
        operand = ir["outputs"][binding.output_index]
        location = FlowLocation(kind="result", name=operand["identifier"])
        writes.add(location)
        clears.add(location)
    for event in spec.events:
        if getattr(event, "kind", None) == "for_each":
            reads.update(_ref_locations(event.collection, ir, interpreter))
            if event.yield_value is not None:
                reads.update(_ref_locations(event.yield_value, ir, interpreter))
    for _, body, event in iter_scoped_events(spec):
        for op in event.atomic_ops:
            if op.op == "merge" and predecessor is not None:
                for incoming in op.incoming:
                    if incoming.predecessor == predecessor:
                        reads.update(_ref_locations(incoming.value, ir, interpreter))
            else:
                for use in active_value_uses(op, ir):
                    if use.role != "control" and false_guard(use.when):
                        continue
                    reads.update(_ref_locations(use.value, ir, interpreter))
            if op.op == "read":
                reads.update(interpreter.aliases(interpreter.locations[op.location]))
            elif op.op == "write":
                target = interpreter.locations[op.target]
                aliases = set(interpreter.aliases(target))
                writes.update(aliases)
                state_evidence.update(aliases)
                strong = (body is None and event.case is None and spec.order == "fixed"
                          and not op.may and not interpreter.is_unknown_address(target)
                          and op.mode in {"replace", "delete"})
                if strong:
                    clears.add(target)
                    reads.update(aliases - {target})
                else:
                    reads.update(aliases)
            elif op.op == "branch":
                controls = True
    return reads, writes, clears, state_evidence, controls


def poison(row, locations, causes):
    for loc in locations:
        row.pop(loc, None)
        row.unavailable[loc] = row.unavailable.get(loc, frozenset()) | frozenset(causes)


def reconvergences(successors):
    """Only a finite, common postdominator discharges unknown branch control.

    Cycles with no guaranteed finite exit have no discharge proof.
    """
    nodes = set(successors)
    # A node is safe only when every successor has an established finite exit.
    terminating = {node for node in nodes if not successors[node]}
    while True:
        grown = terminating | {node for node in nodes if successors[node] <= terminating}
        if grown == terminating:
            break
        terminating = grown
    post = {node: ({node} if not successors[node] else set(terminating)) for node in terminating}
    while True:
        updated = {node: ({node} if not successors[node] else {node} | set.intersection(
            *(post[child] for child in successors[node]))) for node in terminating}
        if updated == post:
            break
        post = updated
    result = {}
    for node, targets in successors.items():
        if not targets or not targets <= terminating:
            result[node] = None
            continue
        common = set.intersection(*(post[target] for target in targets))
        nearest = [candidate for candidate in common if common <= post[candidate]]
        result[node] = nearest[0] if len(nearest) == 1 else None
    return result
