"""Forward may propagation with finite loop equations and immutable publication."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
import json

from skillflow.propagation.data import DataRegistry
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.selectors import compatible_bindings
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_VERSION
from skillflow.propagation.interpreter import PendingValue
from skillflow.propagation.interpreter import PropagationLimitError
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.interpreter import join_states
from skillflow.propagation.interpreter import mapping
from skillflow.propagation.interpreter import plain
from skillflow.propagation.interpreter import static_key
from skillflow.propagation.models import FlowState, FlowLocation
from skillflow.propagation.models import IRFlowRecord, ForEachRecord, OutcomeRouteRecord
from skillflow.propagation.records import PropagationRecords
from skillflow.propagation.records import cfg_sha256
from skillflow.propagation.records import _validate_annotation
from skillflow.propagation.contracts.specs import validate_specs
from skillflow.propagation.contracts.specs import state_write_target
from skillflow.propagation.contracts.specs import value_refs
from skillflow.propagation.contracts.specs import iter_scoped_events
from skillflow.propagation.contracts.specs import precedence_closure
from skillflow.propagation.contracts.limitations import unmodeled_ids, reachable_instructions
from skillflow.propagation.execution_errors import OperationExecutionError
from skillflow.propagation.failure_scope import FailureRow, row_failure_key, dependencies, poison, reconvergences


@dataclass
class PropagationResult:
    status: str
    registry: DataRegistry
    records: PropagationRecords
    coverage: dict[str, str]
    diagnostics: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    initial_data: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)


def _join_ir_records(variants):
    """Join boundary facts while retaining complete paired operation alternatives."""
    if len(variants) == 1:
        return variants[0]
    first = variants[0]
    events = []
    for index, event in enumerate(first.events):
        items = [record.events[index] for record in variants]
        if isinstance(event, ForEachRecord):
            instances = {canonical_sha256(instance.model_dump(mode="json")): instance
                         for item in items for instance in item.instances}
            events.append(event.model_copy(update={
                "instances": [instances[key] for key in sorted(instances)],
                "collections": frozenset().union(*(item.collections for item in items)),
                "outputs": frozenset().union(*(item.outputs for item in items))}))
        else:
            events.append(event.model_copy(update={"atomic_ops": [TransferInterpreter._merge_operations(
                [item.atomic_ops[position] for item in items]) for position in range(len(event.atomic_ops))]}))
    traces = {canonical_sha256(plain(row)): row for record in variants for row in record.outcomes}
    routes = {(row.group, row.case_id, row.target): row for record in variants for row in record.outcome_routes}
    return IRFlowRecord(order=first.order, precedence=first.precedence,
        entry_state=FlowState.from_mapping(join_states(mapping(record.entry_state) for record in variants)),
        exit_state=FlowState.from_mapping(join_states(mapping(record.exit_state) for record in variants)), events=events,
        outcomes=[traces[key] for key in sorted(traces)], outcome_routes=[routes[key] for key in sorted(routes)])


def _guard_operand_origin(ir, spec, record, event_index, op_index):
    """Prove a local field guard reads a particular immutable result version."""
    ref = plain(spec.events[event_index].atomic_ops[op_index])["input"]
    if ref["kind"] != "local":
        return None
    # A condition can alias an unrelated Data object with the same content.
    # Follow the typed producer and its recorded paired inputs, not content.
    preceding = [(e, o, plain(op)) for e, event in enumerate(spec.events[:event_index+1])
                 for o, op in enumerate(getattr(event, "atomic_ops", [])) if (e, o) < (event_index, op_index)]
    for e, index, producer in reversed(preceding):
        if producer.get("output") != ref["name"]:
            continue
        if producer["op"] != "select_part" or producer["input"]["kind"] != "input":
            return None
        operand = ir["inputs"][producer["input"]["index"]]
        if operand["type"] != "result":
            return None
        actual = record.events[e].atomic_ops[index]
        return FlowLocation(kind="result", name=operand["identifier"]), actual.alternatives
    return None


def _guarded_outgoing(state, successors, decisions, registry, max_variants):
    """Route only the member/operand candidates admitted by each typed guard."""
    routes = [(target, state) for target in successors]
    for ir, spec, record, event_index, op_index, operation in decisions:
        raw = plain(spec.events[event_index].atomic_ops[op_index])
        ref, condition_location = raw["input"], None
        if ref["kind"] == "input":
            operand = ir["inputs"][ref["index"]]
            # A context operand can alias several runtime locations and was
            # evaluated at IR entry. It does not prove a block-exit version.
            if operand["type"] == "result":
                condition_location = FlowLocation(kind="result", name=operand["identifier"])
        elif ref["kind"] == "local":
            for binding in spec.output_bindings:
                if plain(binding.value) == ref:
                    condition_location = FlowLocation(kind="result", name=ir["outputs"][binding.output_index]["identifier"])
        origin = _guard_operand_origin(ir, spec, record, event_index, op_index)
        selected = {}
        for target, before in routes:
            for alternative in operation.alternatives:
                if target not in alternative.branch_targets:
                    continue
                roots_by_origin = None
                if origin is not None:
                    pairs = [row for row in origin[1] if row.outputs[0] & alternative.inputs[0]
                             and compatible_bindings(alternative.bindings, row.bindings)]
                    # The producing result may be dead on this edge; absence
                    # is no reason to reject a route.
                    if pairs and origin[0] in before:
                        roots_by_origin = frozenset(identity for row in pairs for identity in row.inputs[0])
                after = {}
                for location, values in before.items():
                    # Stored versions survive other members. Their creation
                    # context is preserved by a read/use alias, not a filter.
                    compatible = (values if location.kind != "result" else frozenset(
                        identity for identity in values if compatible_bindings(alternative.bindings, registry.bindings(identity))))
                    if location == condition_location:
                        roots = set()
                        pending = list(alternative.inputs[0])
                        while pending:
                            identity = pending.pop()
                            if identity in roots:
                                continue
                            roots.add(identity)
                            content = plain(registry.get(identity).content)
                            options = ([item["content"] for item in content["variants"]]
                                       if content["form"] == "loop_summary" else [content])
                            pending.extend(item["base"] for item in options
                                           if item["form"] == "selection" and not item["path"])
                        compatible &= roots
                    if roots_by_origin is not None and location == origin[0]:
                        compatible &= roots_by_origin
                    if raw.get("selector") and location.kind == "result" and any(
                            axis.startswith(("selector:", "python-handler:")) for axis in alternative.bindings):
                        from skillflow.propagation.selectors import routed_identity
                        compatible = frozenset(routed_identity(registry, identity, alternative.bindings)
                            if identity in alternative.inputs[0] or (
                                roots_by_origin is not None and location == origin[0] and identity in roots_by_origin)
                            else identity for identity in compatible)
                    if compatible:
                        after[location] = compatible
                if ((condition_location in before and condition_location not in after)
                        or (roots_by_origin is not None and origin[0] not in after)):
                    continue
                key = (target, tuple(sorted((location.kind, location.name, tuple(sorted(values))) for location, values in after.items())))
                selected[key] = (target, after)
        routes = list(selected.values())
        if len(routes) > max_variants:
            raise PropagationLimitError("typed guard route count exceeds the relation budget")
    return routes


def _scc(nodes, adjacency):
    """Iterative Kosaraju, also safe for large straight-line generated graphs."""
    seen, order = set(), []
    for start in sorted(nodes):
        if start in seen:
            continue
        stack = [(start, False)]
        while stack:
            node, finish = stack.pop()
            if finish:
                order.append(node)
            elif node not in seen:
                seen.add(node)
                stack.append((node, True))
                stack.extend((child, False) for child in sorted(adjacency.get(node, ()), reverse=True)
                             if child not in seen)
    reverse = {node: set() for node in nodes}
    for node, children in adjacency.items():
        for child in children:
            reverse.setdefault(child, set()).add(node)
    seen = set()
    result = []
    for start in reversed(order):
        if start in seen:
            continue
        component, stack = set(), [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            component.add(node)
            stack.extend(reverse.get(node, ()))
        result.append(component)
    return result


def _graph(cfg):
    predecessors = {block: set() for block in cfg["blocks"]}
    successors = {block: set() for block in cfg["blocks"]}
    for edge in cfg["edges"]:
        a, b = edge["source_block_id"], edge["target_block_id"]
        successors[a].add(b)
        predecessors[b].add(a)
    roots = {block for block, pred in predecessors.items() if not pred} | {cfg["entry_block_id"]}
    reachable, pending = set(), list(roots)
    while pending:
        node = pending.pop()
        if node not in reachable:
            reachable.add(node)
            pending.extend(successors[node])
    return roots, reachable, predecessors, successors


def _references(ref, ir, local_nodes, interpreter, memory):
    ref = plain(ref)
    if ref["kind"] == "literal":
        return set()
    if ref["kind"] == "local":
        return {local_nodes[(ir["id"], ref["name"])]}
    if ref["kind"] == "alternatives":
        return set().union(*(_references(r, ir, local_nodes, interpreter, memory) for r in ref["items"]))
    operand = ir.get("inputs", [])[ref["index"]]
    if operand["type"] == "result":
        return {"result:" + operand["identifier"]}
    if operand["type"] == "context_key":
        locs = interpreter.context_locations(ir, ref["index"])
        return set().union(*(memory.get(loc, set())
                             for location in locs for loc in interpreter.aliases(location)))
    return set()


def _reaching_memory(cfg, annotation, interpreter, reachable, roots, predecessors, successors):
    """Finite reaching definitions, retaining definite overwrite/deletion kills.

    A shared location is not one timeless node: resets before reads can break a
    data feedback cycle even while the control-flow loop remains present.
    """
    locations = interpreter.initial_locations()
    seed = {loc: {"initial:" + static_key(loc.kind, loc.name)} for loc in locations}
    out, snapshots, evaluated = {}, {}, set()
    queue, queued = deque(sorted(roots)), set(roots)
    unmodeled = unmodeled_ids(annotation)
    while queue:
        block = queue.popleft()
        queued.remove(block)
        incoming = [out[p] for p in predecessors[block] if p in out]
        if block in roots:
            incoming.append(seed)
        state = {}
        for prior in incoming:
            for loc, definitions in prior.items():
                state.setdefault(loc, set()).update(definitions)
        complete = True
        for ir in cfg["blocks"][block]["instructions"]:
            if ir["id"] in unmodeled:
                complete = False
                break
            ops = [(e, b, o, op) for e, b, event in iter_scoped_events(annotation.ir_semantics[ir["id"]])
                   for o, op in enumerate(event.atomic_ops)]
            spec = annotation.ir_semantics[ir["id"]]
            uncertain = spec.order == "partial"
            base_state = {loc: set(defs) for loc, defs in state.items()}
            snapshots[(ir["id"], "entry")] = base_state
            closure = precedence_closure(spec)
            seen_events = set()
            for e, b, o, op in ops:
                if uncertain:
                    # Weak partial-order memory retains entry candidates and
                    # only writes that can precede this operation. The same
                    # compiled constraints drive concrete candidate scheduling.
                    visible = {loc: set(defs) for loc, defs in base_state.items()}
                    for we, wb, wo, write in ops:
                        target_id = state_write_target(write)
                        if target_id and getattr(write, "mode", None) != "delete" and (we, wb, wo) != (e, b, o) and (we, wb, wo) not in closure[(e, b, o)]:
                            for loc in interpreter.aliases(interpreter.locations[target_id]):
                                visible.setdefault(loc, set()).add(static_key(ir["id"], we, wb, wo))
                else:
                    visible = {loc: set(defs) for loc, defs in state.items()}
                snapshots[(ir["id"], e, b, o)] = visible
                if e not in seen_events:
                    snapshots[(ir["id"], e, None, -1)] = visible
                    seen_events.add(e)
                target_id = state_write_target(op)
                if target_id:
                    target = interpreter.locations[target_id]
                    for loc in interpreter.aliases(target):
                        weak = uncertain or op.op == "placeholder" or op.may or loc != target or interpreter.is_unknown_address(target)
                        if getattr(op, "mode", None) == "delete":
                            if not weak:
                                state.pop(loc, None)
                        elif weak:
                            state.setdefault(loc, set()).add(static_key(ir["id"], e, b, o))
                        else:
                            state[loc] = {static_key(ir["id"], e, b, o)}
            snapshots[(ir["id"], -1, -1)] = {loc: set(defs) for loc, defs in state.items()}
        if not complete:
            continue
        changed = block not in evaluated or out.get(block) != state
        evaluated.add(block)
        out[block] = state
        if changed:
            for nxt in sorted(successors[block] & reachable):
                if nxt not in queued:
                    queued.add(nxt)
                    queue.append(nxt)
    return snapshots


def _generation_feedback(cfg, annotation, interpreter, reachable, roots, predecessors, successors):
    """Find generation on value-feedback cycles inside CFG cycles.

    Shared-state dependencies include possible aliases; a straight-line read /
    write is never rejected solely because it has a memory dependence.
    """
    findings = []
    memory_inputs = _reaching_memory(cfg, annotation, interpreter, reachable, roots, predecessors, successors)
    for blocks in _scc(reachable, {b: successors[b] & reachable for b in reachable}):
        if len(blocks) == 1 and next(iter(blocks)) not in successors[next(iter(blocks))]:
            continue
        instructions = [ir for b in sorted(blocks) for ir in cfg["blocks"][b]["instructions"]
                        if (ir["id"], "entry") in memory_inputs]
        nodes, edges, generators, positions, locals_ = set(), {}, set(), {}, {}

        def edge(a, b):
            nodes.update([a, b])
            edges.setdefault(a, set()).add(b)

        scoped_locals = {}
        for ir in instructions:
            spec = annotation.ir_semantics[ir["id"]]
            for e, b, event in iter_scoped_events(spec):
                for o, operation in enumerate(event.atomic_ops):
                    if getattr(operation, "output", None) is not None:
                        target_map = locals_ if b is None else scoped_locals.setdefault((ir["id"], e), {})
                        target_map[(ir["id"], operation.output)] = static_key(ir["id"], e, b, o)
            for e, event in enumerate(spec.events):
                if getattr(event, "kind", None) == "for_each":
                    scoped_locals.setdefault((ir["id"], e), {})[(ir["id"], event.item)] = static_key(ir["id"], e, "element")
                    if event.output is not None:
                        locals_[(ir["id"], event.output)] = static_key(ir["id"], e, "collection")
        for ir in instructions:
            spec = annotation.ir_semantics[ir["id"]]
            for e, event in enumerate(spec.events):
                if getattr(event, "kind", None) == "for_each":
                    node = static_key(ir["id"], e, "element")
                    nodes.add(node)
                    generators.add(node)
                    positions[node] = {"instruction_id": ir["id"], "event_index": e, "scope": "element"}
                    memory = memory_inputs[(ir["id"], e, None, -1)]
                    for source in _references(event.collection, ir, locals_, interpreter, memory_inputs[(ir["id"], "entry")]):
                        edge(source, node)
                    if event.output is not None:
                        collected = locals_[(ir["id"], event.output)]
                        generators.add(collected)
                        positions[collected] = {"instruction_id": ir["id"], "event_index": e, "scope": "element"}
                        edge(node, collected)
                        active = {**locals_, **scoped_locals[(ir["id"], e)]}
                        for source in _references(event.yield_value, ir, active, interpreter,
                                                  memory_inputs[(ir["id"], "entry")]):
                            edge(source, collected)
            for e, b, event in iter_scoped_events(spec):
                active_locals = locals_ if b is None else {**locals_, **scoped_locals[(ir["id"], e)]}
                for o, operation in enumerate(event.atomic_ops):
                    op = plain(operation)
                    node = static_key(ir["id"], e, b, o)
                    nodes.add(node)
                    positions[node] = {"instruction_id": ir["id"], "event_index": e, "op_index": o}
                    if b is not None:
                        positions[node]["body_event_index"] = b
                    memory = memory_inputs[(ir["id"], e, b, o)]
                    from skillflow.propagation.contracts.uses import active_value_uses
                    dependencies = set().union(*(_references(use.value, ir, active_locals, interpreter, memory_inputs[(ir["id"], "entry")])
                                                  for use in active_value_uses(operation, ir)))
                    if op["op"] == "read":
                        dependencies.update(set().union(*(memory.get(loc, set())
                                            for loc in interpreter.aliases(interpreter.locations[op["location"]]))))
                    if op["op"] == "write" and op["mode"] == "append":
                        dependencies.update(set().union(*(memory.get(loc, set())
                                            for loc in interpreter.aliases(interpreter.locations[op["target"]]))))
                        generators.add(node)
                    if op["op"] in {"receive", "select_part", "exclude_parts", "update_fields", "build", "compute", "filter_items", "placeholder"}:
                        generators.add(node)
                    for source in dependencies:
                        edge(source, node)
            for binding in spec.output_bindings:
                target = "result:" + ir["outputs"][binding.output_index]["identifier"]
                for source in _references(binding.value, ir, locals_, interpreter, memory_inputs[(ir["id"], "entry")]):
                    edge(source, target)
        for component in _scc(nodes, edges):
            if (len(component) > 1 or any(n in edges.get(n, ()) for n in component)) and component & generators:
                findings.append({
                    "code": "unsupported_feedback", "blocks": sorted(blocks),
                    "operations": [positions[n] for n in sorted(component) if n in positions],
                    "reason": "The loop contains feedback dependencies that generate data; this version does not collapse infinitely many versions into one identity.",
                })
    return findings


def _seed_state(cfg, annotation, interpreter, registry, supplied):
    state = mapping(supplied) if supplied is not None else {}
    locations = interpreter.initial_locations()
    optional = set()
    if supplied is None:
        for block in cfg["blocks"].values():
            if block.get("data_source_kind") == "context":
                ir = block["instructions"][0]
                for index in ir.get("metadata", {}).get("optional_context_inputs", []):
                    optional.update(interpreter.context_locations(ir, index))
    for location in sorted(locations, key=lambda loc: (loc.kind, loc.name)):
        # An explicitly supplied full seed state is authoritative, including absence.
        if supplied is not None or location in state:
            continue
        at = static_key("optional entry", location.kind, location.name) if location in optional else None
        data = registry.register_source(static_key("initial", location.kind, location.name),
                                        acquired_from=f"{location.kind}:{location.name}", at=at)
        state[location] = frozenset([data.id])
    known = {item["data"]["id"] for item in registry.to_dict()["records"]}
    for ids in state.values():
        if not ids <= known:
            raise ValueError("initial state references unknown Data")
    return FlowState.from_mapping(state)


def propagate(cfg, annotation, *, initial_registry=None, initial_state=None,
              schedule="fifo", max_variants=100000):
    """Compute static may-records. Invalid inputs raise; solve limitations are results.

    No online clients are imported. Source Data is cloned and never mutated.
    ``complete`` means convergence within this domain, not semantic correctness.
    """
    if schedule not in {"fifo", "lifo"}:
        raise ValueError("schedule must be fifo or lifo")
    if type(max_variants) is not int or max_variants < 1:
        raise ValueError("max_variants must be a positive integer")
    if isinstance(cfg, ControlFlowGraph):
        cfg.validate_integrity()
        cfg = json.loads(cfg.to_json())
    else:
        graph = ControlFlowGraph.model_validate(cfg)
        graph.validate_integrity()
        cfg = json.loads(graph.to_json())
    annotation = AnnotationPayload.model_validate(plain(annotation))
    validate_specs(cfg, annotation)
    payload = annotation.model_dump(mode="json")
    instructions = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    _validate_annotation(payload, set(instructions))
    registry = (DataRegistry.from_dict(initial_registry.to_dict()) if initial_registry is not None
                else DataRegistry("propagation:" + canonical_sha256({"cfg": cfg, "annotation": payload})))
    if initial_state is not None:
        initial_state = FlowState.model_validate(plain(initial_state))
    roots, reachable, predecessors, successors = _graph(cfg)
    loop_scopes = {}
    for component in _scc(reachable, successors):
        if len(component) > 1 or any(node in successors[node] for node in component):
            scope = "loop:" + canonical_sha256(sorted(component))
            loop_scopes.update({ir["id"]: scope for node in component for ir in cfg["blocks"][node]["instructions"]})
    has_loop_ops = any(op.op in {"merge", "member", "branch", "append"}
        for spec in annotation.ir_semantics.values() for _, _, event in iter_scoped_events(spec) for op in event.atomic_ops)
    guarded_cases = any(event.case and event.case.guard for spec in annotation.ir_semantics.values()
                        for _, _, event in iter_scoped_events(spec))
    optional_arguments = any(ir.get("metadata", {}).get("optional_context_inputs") for ir in instructions.values())
    if loop_scopes or has_loop_ops or guarded_cases or optional_arguments:
        from skillflow.propagation.loop_domain import LoopFactRegistry
        registry = LoopFactRegistry(registry, loop_scopes)
        registry.max_facts = max_variants
    registry.enable_computation()
    interpreter = TransferInterpreter(cfg, payload, registry, max_variants=max_variants,
                                      typed_specs=annotation.ir_semantics)
    seed = _seed_state(cfg, annotation, interpreter, registry, initial_state)
    initial_data = registry.to_dict()
    records = PropagationRecords.from_computation(cfg, payload, registry, profile_schema_version=PROFILE_VERSION,
                                 annotation_cfg_sha256=cfg_sha256(cfg),
                                 initial_data=initial_data, initial_state=seed)
    coverage = {ir_id: "not_reached" for ir_id in instructions}
    result = PropagationResult("complete", registry, records, coverage,
                               [], {"block_evaluations": 0, "partition_evaluations": 0,
                                    "data_count": len(registry)},
                               initial_data, seed.model_dump(mode="json"))
    dominators = {node: ({node} if node in roots else set(reachable)) for node in reachable}
    while True:
        updated = {node: ({node} if node in roots else {node} | set.intersection(
            *(dominators[pred] for pred in predecessors[node] & reachable))) for node in reachable}
        if updated == dominators:
            break
        dominators = updated
    if hasattr(registry, "regions"):
        regions = {}
        for source in reachable:
            for header in successors[source]:
                if header not in dominators[source]:
                    continue
                nodes, pending = {header, source}, ([] if source == header else [source])
                while pending:
                    node = pending.pop()
                    for prior in predecessors[node]:
                        if prior not in nodes:
                            nodes.add(prior)
                            pending.append(prior)
                regions.setdefault(header, set()).update(nodes)
        for block in reachable:
            owners = [(len(nodes), header) for header, nodes in regions.items() if block in nodes]
            if owners:
                owner = min(owners)[1]
                registry.regions.update({ir["id"]: owner for ir in cfg["blocks"][block]["instructions"]})
        registry.region_blocks = regions
        registry.dominators = dominators
        registry.ir_blocks = {ir["id"]: block for block, value in cfg["blocks"].items() for ir in value["instructions"]}
        registry.ir_orders = {ir["id"]: index for value in cfg["blocks"].values() for index, ir in enumerate(value["instructions"])}
    interpreter.prepare_member_metadata()
    from skillflow.propagation.liveness import calculate_liveness
    live = calculate_liveness(cfg, annotation, interpreter, successors)
    return _solve_relations(cfg, annotation, interpreter, registry, result, seed,
                            roots, predecessors, successors, dominators, live,
                            schedule=schedule, max_variants=max_variants)


def _row_key(state):
    """A relation row, never a pointwise union of unrelated alternatives."""
    return (tuple(sorted((loc.kind, loc.name, tuple(sorted(ids)))
                         for loc, ids in state.items() if ids)), *row_failure_key(state))


def _solve_relations(cfg, annotation, interpreter, registry, result, seed,
                     roots, predecessors, successors, dominators, live, *,
                     schedule, max_variants):
    """Solve current edge relations using read-dependent partition work items.

    Facts are shared by static identity; execution rows retain tuple relations.
    A partition owns only its current records and outgoing contribution. Replacing
    that contribution also retracts obsolete routes, without deleting Data history.
    """
    instructions = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    has_merge = {block: any(op.op == "merge"
        for ir in value["instructions"] if ir["id"] in annotation.ir_semantics
        for _, _, event in iter_scoped_events(annotation.ir_semantics[ir["id"]])
        for op in event.atomic_ops) for block, value in cfg["blocks"].items()}
    unmodeled = unmodeled_ids(annotation)
    inputs, outcomes, subscriptions = {}, {}, {}
    block_parts, readers = defaultdict(set), defaultdict(set)
    edge_out = {}
    queue, queued = deque(), set()
    refresh_queue, refresh_queued = deque(), set()
    # Only cyclic components need to discard self-supported old rows when a
    # contribution shrinks, including an internal gate. This is reconstruction;
    # immutable Data and the finite family history remain untouched.
    cyclic_components = {min(component): frozenset(component)
        for component in _scc(set(cfg["blocks"]), successors)
        if len(component) > 1 or any(block in successors[block] for block in component)}
    cyclic_owner = {block: owner for owner, component in cyclic_components.items() for block in component}
    rebuild_queue, rebuild_queued = deque(), set()
    rebuilding = set()
    fault_evidence = {}
    control_joins = reconvergences(successors)
    stats = result.stats
    stats.update(max_active_relation_rows=0, max_partition_rows=0,
                 max_edge_relation_rows=0, max_block_relation_rows=0,
                 block_relation_row_maxima={}, projected_locations_removed=0,
                 dependency_wakeups=0, edge_wakeups=0, removed_partitions=0,
                 scc_rebuilds=0, registry_changed_keys=0, block_evaluation_counts={})

    def project(state, keep):
        value = (state if isinstance(state, FailureRow) else FailureRow(state)).project(keep)
        stats["projected_locations_removed"] += len(state) - len(value)
        return value

    def enqueue(part, reason):
        if part in inputs and part not in queued:
            queued.add(part)
            queue.append(part)
            stats[reason] += 1

    def refresh_later(block):
        if block not in refresh_queued:
            refresh_queued.add(block)
            refresh_queue.append(block)

    def detach(part):
        for key in subscriptions.pop(part, {}):
            readers[key].discard(part)
            if not readers[key]:
                del readers[key]

    def replace_edge(source, target, rows):
        edge = (source, target)
        previous = edge_out.get(edge, {})
        if rows == previous:
            return
        if rows:
            edge_out[edge] = rows
        else:
            edge_out.pop(edge, None)
        owner = cyclic_owner.get(target)
        if (owner is not None and previous.keys() - rows.keys()
                and owner not in rebuild_queued and owner not in rebuilding):
            rebuild_queued.add(owner)
            rebuild_queue.append(owner)
        refresh_later(target)

    def rebuild_component(owner):
        component = cyclic_components[owner]
        stats["scc_rebuilds"] += 1
        rebuilding.add(owner)
        try:
            for block in sorted(component):
                for part in block_parts[block]:
                    inputs.pop(part, None)
                    outcomes.pop(part, None)
                    detach(part)
                    queued.discard(part)
                    stats["removed_partitions"] += 1
                block_parts[block] = set()
            # External incoming rows and root seeds are the only starting support.
            # Clearing this component cannot recursively schedule itself, while
            # withdrawn output to another SCC can invalidate that component.
            for source in sorted(component):
                for target in sorted(successors[source]):
                    replace_edge(source, target, {})
            for block in sorted(component):
                refresh_later(block)
        finally:
            rebuilding.remove(owner)

    def publish(block):
        combined = defaultdict(dict)
        for part in block_parts[block]:
            for target, rows in outcomes.get(part, {}).get("outgoing", {}).items():
                combined[target].update(rows)
        for target in successors[block]:
            rows = combined.get(target, {})
            if len(rows) > max_variants:
                raise PropagationLimitError("incoming state relation exceeds configured resource budget")
            stats["max_edge_relation_rows"] = max(stats["max_edge_relation_rows"], len(rows))
            replace_edge(block, target, rows)

    def partition_key(block, predecessor, state):
        footprint = ()
        if hasattr(registry, "bindings"):
            footprint = tuple(sorted({tuple(sorted(registry.bindings(identity).items()))
                                      for ids in state.values() for identity in ids}))
        return (block, predecessor if has_merge[block] else None,
                predecessor is not None and block in dominators[predecessor], footprint)

    def refresh(block):
        grouped = defaultdict(dict)
        for predecessor in sorted(predecessors[block]):
            for state in edge_out.get((predecessor, block), {}).values():
                row = project(state, live.block_in[block])
                grouped[partition_key(block, predecessor, row)][_row_key(row)] = row
        if block in roots:
            row = project(mapping(seed), live.block_in[block])
            grouped[partition_key(block, None, row)][_row_key(row)] = row
        old = block_parts[block]
        for part in old - grouped.keys():
            inputs.pop(part, None)
            outcomes.pop(part, None)
            detach(part)
            queued.discard(part)
            stats["removed_partitions"] += 1
        block_parts[block] = set(grouped)
        for part, rows in grouped.items():
            if rows != inputs.get(part):
                inputs[part] = rows
                enqueue(part, "edge_wakeups")
        stats["max_active_relation_rows"] = max(stats["max_active_relation_rows"],
                                                 sum(len(rows) for rows in inputs.values()))
        block_rows = sum(len(inputs[part]) for part in block_parts[block])
        stats["max_block_relation_rows"] = max(stats["max_block_relation_rows"], block_rows)
        maxima = stats["block_relation_row_maxima"]
        maxima[block] = max(maxima.get(block, 0), block_rows)
        publish(block)

    def evaluate(part):
        block, predecessor, backedge, _ = part
        rows = inputs[part]
        stats["max_partition_rows"] = max(stats["max_partition_rows"], len(rows))
        current = {"records": {}, "outgoing": defaultdict(dict), "failed": {},
                   "attempted": set(), "unmodeled": set(), "diagnostics": [],
                   "errors": set(), "blocked": defaultdict(set)}
        candidates = defaultdict(list)
        with registry.observe_reads() as observed:
            try:
                interpreter.current_block = block
                instructions = cfg["blocks"][block]["instructions"]
                dispatch = instructions[-1].get("metadata", {}).get("outcome_dispatch") if instructions else None
                paths = deque((0, rows[key], FailureRow(rows[key], unavailable=rows[key].unavailable,
                    controls={cause: join for cause, join in rows[key].controls.items() if join != block}),
                    set(successors[block]), [], None) for key in sorted(rows))
                while paths:
                    start, incoming, state, allowed, decisions, selected_route = paths.popleft()
                    # Only merge uses predecessor snapshots. Its selected row is
                    # authoritative; no joined sibling row may replace it.
                    interpreter.predecessor_states = ({predecessor: incoming}
                                                       if predecessor is not None else {})
                    interpreter.active_predecessor = predecessor
                    interpreter.loop_backedge_available = backedge
                    complete = True
                    for index in range(start, len(instructions)):
                        ir = instructions[index]
                        identity = ir["id"]
                        current["attempted"].add(identity)
                        if identity in unmodeled:
                            current["unmodeled"].add(identity)
                            complete = False
                            break
                        evaluated = False
                        attempt_diagnostics = None
                        try:
                            if dispatch is not None and index == len(instructions) - 1 and selected_route is None:
                                raise PendingValue(f"{identity}: its protected producer has no established outcome")
                            state = project(state, live.before[identity])
                            spec = annotation.ir_semantics[identity]
                            reads, writes, clears, evidence_reads, controls = dependencies(
                                ir, spec, interpreter, block, predecessor, state)
                            causes = set(state.controls) | set().union(
                                *(state.unavailable.get(loc, ()) for loc in reads))
                            if causes:
                                current["blocked"][identity].update(causes)
                                poison(state, writes, causes)
                                if controls:
                                    for cause in causes:
                                        state.controls.setdefault(cause, control_joins[block])
                                state = project(state, live.after[identity])
                                continue
                            # Old state is evidence even when a definite overwrite
                            # does not consume it. Keep that limitation local while
                            # allowing the new independently known value onward.
                            evidence_causes = set().union(*(state.unavailable.get(loc, ()) for loc in evidence_reads))
                            with registry._transaction():
                                evaluated = True
                                try:
                                    record = interpreter.evaluate(ir, spec, FlowState.from_mapping(state))
                                except (PendingValue, OperationExecutionError, PropagationLimitError):
                                    attempt_diagnostics = interpreter.last_diagnostics
                                    for diagnostic in attempt_diagnostics:
                                        if diagnostic["code"] == "missing_part":
                                            diagnostic["observed_data"] = plain(registry.get(diagnostic["data_id"]))
                                    raise
                            current["blocked"][identity].update(evidence_causes)
                            state = state.with_state(mapping(record.exit_state))
                            for loc in clears:
                                state.unavailable.pop(loc, None)
                            state = project(state, live.after[identity])
                            record = record.model_copy(update={"exit_state": FlowState.from_mapping(state)})
                            if selected_route is not None and index == len(instructions) - 1:
                                record = record.model_copy(update={"outcome_routes": [selected_route]})
                                allowed &= {selected_route.target}
                            candidates[identity].append(record)
                            for event_index, event in enumerate(record.events):
                                if hasattr(event, "atomic_ops"):
                                    for op_index, op in enumerate(event.atomic_ops):
                                        if op.op == "branch" and not op.skipped_case_inputs:
                                            allowed &= set(op.branch_targets)
                                            decisions.append((ir, annotation.ir_semantics[identity], record,
                                                              event_index, op_index, op))
                            if record.outcomes:
                                # Only the public record is joined. The next IR
                                # runs with the full memory of one outcome.
                                next_rows = {}
                                dispositions = {case.case_id: case.disposition for binding in spec.outcome_bindings
                                                for case in binding.cases}
                                for exit_row, trace in interpreter.outcome_states:
                                    row = project(state.with_state(exit_row), live.after[identity])
                                    route = None
                                    if dispatch is not None and dispatch["producer"] == identity:
                                        target = dispatch["on_" + dispositions[trace.case_id]]
                                        route = OutcomeRouteRecord(group=trace.group, case_id=trace.case_id, target=target)
                                    key = (_row_key(row), trace.case_id if route is not None else None)
                                    next_rows[key] = row, route
                                if len(paths) + len(next_rows) > max_variants:
                                    raise PropagationLimitError("outcome state relation exceeds configured resource budget")
                                for row, route in next_rows.values():
                                    paths.append((index + 1, incoming, row, set(allowed), list(decisions), route))
                                complete = False
                                break
                        except OperationExecutionError as error:
                            diagnostic = error.diagnostic
                            cause = canonical_sha256(diagnostic)
                            fault_evidence[cause] = diagnostic
                            current["errors"].add(cause)
                            current["blocked"][identity].add(cause)
                            poison(state, writes, {cause})
                            if controls:
                                state.controls[cause] = control_joins[block]
                            state = project(state, live.after[identity])
                        except PendingValue as error:
                            current["failed"][identity] = str(error)
                            complete = False
                            break
                        finally:
                            if evaluated:
                                current["diagnostics"].extend(interpreter.last_diagnostics
                                    if attempt_diagnostics is None else attempt_diagnostics)
                    if complete:
                        for target, guarded in _guarded_outgoing(state, allowed, decisions, registry, max_variants):
                            projected = project(state.with_state(guarded), live.block_in[target])
                            current["outgoing"][target][_row_key(projected)] = projected
            finally:
                current["records"] = {ir: _join_ir_records(values) for ir, values in candidates.items()}
                outcomes[part] = current
                detach(part)
                subscriptions[part] = dict(observed)
                for key in observed:
                    readers[key].add(part)
                stats["partition_evaluations"] += 1
                stats["block_evaluations"] += 1
                counts = stats["block_evaluation_counts"]
                counts[block] = counts.get(block, 0) + 1
        # First-read versions catch a later mutation in this same attempt.
        changed = registry.take_changes()
        stats["registry_changed_keys"] += len(changed)
        for key in changed:
            for consumer in tuple(readers.get(key, ())):
                if subscriptions[consumer][key] != registry.key_version(key):
                    enqueue(consumer, "dependency_wakeups")
        publish(block)

    registry.take_changes()  # Initial seeds have no previous consumers.
    for block in sorted(roots):
        refresh_later(block)
    try:
        while queue or refresh_queue or rebuild_queue:
            while refresh_queue or rebuild_queue:
                if rebuild_queue:
                    owner = rebuild_queue.popleft()
                    rebuild_queued.remove(owner)
                    rebuild_component(owner)
                else:
                    block = refresh_queue.popleft()
                    refresh_queued.remove(block)
                    refresh(block)
            if not queue:
                continue
            part = queue.popleft() if schedule == "fifo" else queue.pop()
            if part not in queued:
                continue
            queued.remove(part)
            if part in inputs:
                evaluate(part)
    except PropagationLimitError as error:
        result.status = "resource_limit"
        result.diagnostics.append({"code": "resource_limit", "reason": str(error)})
    candidates, failures, stopped = defaultdict(list), {}, set()
    error_scopes = defaultdict(set)
    for part in sorted(outcomes, key=repr):
        item = outcomes[part]
        for ir in item["attempted"]:
            result.coverage[ir] = "not_solved"
        for ir, record in item["records"].items():
            candidates[ir].append(record)
        failures.update(item["failed"])
        stopped.update(item["unmodeled"])
        for cause in item["errors"]:
            error_scopes[cause].add(fault_evidence[cause]["instruction_id"])
        for ir, causes in item["blocked"].items():
            for cause in causes:
                error_scopes[cause].add(ir)
        result.diagnostics.extend(item["diagnostics"])
    for ir, variants in candidates.items():
        result.coverage[ir] = "processed_with_placeholder" if any(row.used_placeholder() for row in variants) else "processed"
    for cause, affected in sorted(error_scopes.items()):
        diagnostic = fault_evidence[cause]
        result.diagnostics.append({**diagnostic, "affected_instruction_ids": sorted(affected)})
        for ir in affected - candidates.keys():
            result.coverage[ir] = ("execution_error" if ir == diagnostic["instruction_id"] else "blocked")
    for ir, error in sorted(failures.items()):
        code = "unresolved_path" if ir in candidates else "unresolved_binding"
        if ir not in candidates:
            result.coverage[ir] = "unresolved_binding"
        result.diagnostics.append({"code": code, "instruction_id": ir,
            "reason": "A predecessor path could not resolve its inputs: " + error})
    for ir in sorted(stopped):
        result.coverage[ir] = "unmodeled"
        result.diagnostics.append({"code": "unmodeled_processing", "instruction_id": ir,
            "reason": "Explicitly unmodeled processing stops this block before evaluation and OUT publication; prior records remain available."})
    for source in stopped | failures.keys():
        for ir in reachable_instructions(cfg, source):
            if result.coverage[ir] in {"not_reached", "not_solved"}:
                result.coverage[ir] = "blocked"
    if result.status == "complete" and (failures or stopped or error_scopes or "processed_with_placeholder" in result.coverage.values() or any(
            item["code"] == "unresolved_path" for item in result.diagnostics)):
        result.status = "incomplete"
    # Absence of a worklist visit is not a path exclusion proof. Recompute
    # admitted paths from the actual successful guard records, even on abort.
    from skillflow.propagation.loop_guards import admitted_instructions
    uncertain = set().union(*error_scopes.values()) | failures.keys()
    uncertain.update(item["instruction_id"] for item in result.diagnostics if item["code"] == "unresolved_path")
    admitted = admitted_instructions(cfg, interpreter.annotation,
        {ir: _join_ir_records(values) for ir, values in candidates.items() if ir not in uncertain}, registry)
    for ir, state in result.coverage.items():
        if state == "not_reached":
            result.coverage[ir] = "infeasible" if ir not in admitted else "not_solved"
    stats["description_revision"] = registry.revision
    if hasattr(registry, "seal"):
        stats["loop_families"] = len(registry.facts)
        stats["loop_relation_facts"] = sum(len(item["variants"]) for item in registry.facts.values())
        registry = registry.seal()
        result.registry = registry
    result.records = PropagationRecords.from_computation(cfg, interpreter.annotation, registry,
        profile_schema_version=PROFILE_VERSION, annotation_cfg_sha256=cfg_sha256(cfg),
        initial_data=result.initial_data, initial_state=seed)
    for ir, values in sorted(candidates.items()):
        result.records.put_computed(ir, _join_ir_records(values))
    stats["data_count"] = len(registry)
    stats["record_count"] = len(result.records)
    stats["compatible_candidates"] = getattr(interpreter, "compatible_candidates", 0)
    result.records.check_references()
    return result
