"""Finite forward may propagation with explicit generation-feedback rejection."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import json

from skill_ir.data import DataRegistry
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.recording import canonical_sha256
from skill_ir.security_profile.models import AnnotationPayload, SCHEMA_VERSION as PROFILE_VERSION
from .interpreter import (
    PendingValue, PropagationLimitError, TransferInterpreter, join_states, mapping, plain, static_key,
)
from .models import FlowLocation, FlowState
from .records import PropagationRecords, cfg_sha256, _validate_annotation
from .specs import validate_specs, value_refs


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
    uncertain_irs = {u.instruction_id for u in annotation.unresolved if u.field == "effects"}
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
        for ir in cfg["blocks"][block]["instructions"]:
            ops = [(e, o, op) for e, event in enumerate(annotation.transfer_specs[ir["id"]].events)
                   for o, op in enumerate(event.atomic_ops)]
            uncertain = ir["id"] in uncertain_irs
            if uncertain:
                for e, o, op in ops:
                    if op.op == "write" and op.mode != "delete":
                        for loc in interpreter.aliases(interpreter.locations[op.target]):
                            state.setdefault(loc, set()).add(static_key(ir["id"], e, o))
            for e, o, op in ops:
                snapshots[(ir["id"], e, o)] = {loc: set(defs) for loc, defs in state.items()}
                if op.op == "write":
                    target = interpreter.locations[op.target]
                    for loc in interpreter.aliases(target):
                        weak = uncertain or loc != target or target.name.startswith("symbolic:")
                        if op.mode == "delete":
                            if not weak:
                                state.pop(loc, None)
                        elif weak:
                            state.setdefault(loc, set()).add(static_key(ir["id"], e, o))
                        else:
                            state[loc] = {static_key(ir["id"], e, o)}
            snapshots[(ir["id"], -1, -1)] = {loc: set(defs) for loc, defs in state.items()}
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
        instructions = [ir for b in sorted(blocks) for ir in cfg["blocks"][b]["instructions"]]
        nodes, edges, generators, positions, locals_ = set(), {}, set(), {}, {}

        def edge(a, b):
            nodes.update([a, b])
            edges.setdefault(a, set()).add(b)

        for ir in instructions:
            for e, event in enumerate(annotation.transfer_specs[ir["id"]].events):
                for o, operation in enumerate(event.atomic_ops):
                    if hasattr(operation, "output"):
                        locals_[(ir["id"], operation.output)] = static_key(ir["id"], e, o)
        for ir in instructions:
            spec = annotation.transfer_specs[ir["id"]]
            for e, event in enumerate(spec.events):
                for o, operation in enumerate(event.atomic_ops):
                    op = plain(operation)
                    node = static_key(ir["id"], e, o)
                    nodes.add(node)
                    positions[node] = {"instruction_id": ir["id"], "event_index": e, "op_index": o}
                    memory = memory_inputs[(ir["id"], e, o)]
                    dependencies = set().union(*(_references(ref, ir, locals_, interpreter, memory)
                                                  for ref in value_refs(operation)))
                    if op["op"] == "read":
                        dependencies.update(set().union(*(memory.get(loc, set())
                                            for loc in interpreter.aliases(interpreter.locations[op["location"]]))))
                    if op["op"] == "write" and op["mode"] == "append":
                        dependencies.update(set().union(*(memory.get(loc, set())
                                            for loc in interpreter.aliases(interpreter.locations[op["target"]]))))
                        generators.add(node)
                    if op["op"] in {"receive", "select_part", "exclude_parts", "update_fields", "build", "compute"}:
                        generators.add(node)
                    for source in dependencies:
                        edge(source, node)
            for binding in spec.output_bindings:
                target = "result:" + ir["outputs"][binding.output_index]["identifier"]
                for source in _references(binding.value, ir, locals_, interpreter, memory_inputs[(ir["id"], -1, -1)]):
                    edge(source, target)
        for component in _scc(nodes, edges):
            if (len(component) > 1 or any(n in edges.get(n, ()) for n in component)) and component & generators:
                findings.append({
                    "code": "unsupported_feedback", "blocks": sorted(blocks),
                    "operations": [positions[n] for n in sorted(component) if n in positions],
                    "reason": "循环含生成数据的反馈依赖；本版不将无限版本压入同一身份。",
                })
    return findings


def _seed_state(cfg, annotation, interpreter, registry, supplied):
    state = mapping(supplied) if supplied is not None else {}
    locations = interpreter.initial_locations()
    for location in sorted(locations, key=lambda loc: (loc.kind, loc.name)):
        # An explicitly supplied full seed state is authoritative, including absence.
        if supplied is not None or location in state:
            continue
        data = registry.register_source(static_key("initial", location.kind, location.name),
                                        acquired_from=f"{location.kind}:{location.name}")
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
    interpreter = TransferInterpreter(cfg, payload, registry, max_variants=max_variants)
    seed = _seed_state(cfg, annotation, interpreter, registry, initial_state)
    initial_data = registry.to_dict()
    records = PropagationRecords(cfg, annotation, registry, profile_schema_version=PROFILE_VERSION,
                                 annotation_cfg_sha256=cfg_sha256(cfg),
                                 initial_data=initial_data, initial_state=seed)
    roots, reachable, predecessors, successors = _graph(cfg)
    coverage = {ir_id: "not_reached" for ir_id in instructions}
    diagnostics = _generation_feedback(cfg, annotation, interpreter, reachable, roots, predecessors, successors)
    result = PropagationResult("unsupported_feedback" if diagnostics else "complete", registry, records, coverage,
                               diagnostics, {"block_evaluations": 0, "data_count": len(registry)},
                               initial_data, seed.model_dump(mode="json"))
    if diagnostics:
        for b in reachable:
            for ir in cfg["blocks"][b]["instructions"]:
                coverage[ir["id"]] = "not_solved"
        return result
    block_out, evaluated, pending_errors, block_records = {}, set(), {}, {}
    block_diagnostics = {}
    queue = deque(sorted(roots))
    queued = set(queue)
    try:
        while queue:
            block_id = queue.popleft() if schedule == "fifo" else queue.pop()
            queued.remove(block_id)
            before_revision = registry.revision
            states = [block_out[p] for p in sorted(predecessors[block_id]) if p in block_out]
            if block_id in roots:
                states.append(mapping(seed))
            state = join_states(states)
            block_records[block_id] = {}
            block_diagnostics[block_id] = []
            complete_block = True
            block_instructions = cfg["blocks"][block_id]["instructions"]
            for ir in block_instructions:
                coverage[ir["id"]] = "not_solved"
                pending_errors.pop(ir["id"], None)
            for ir in block_instructions:
                try:
                    record = interpreter.evaluate(ir, annotation.transfer_specs[ir["id"]], FlowState.from_mapping(state))
                    block_records[block_id][ir["id"]] = record
                    state = mapping(record.exit_state)
                    coverage[ir["id"]] = "processed"
                except PendingValue as error:
                    coverage[ir["id"]] = "unresolved_binding"
                    pending_errors[ir["id"]] = str(error)
                    # Missing operands are not an identity transfer: executing a
                    # later read would incorrectly reuse content a pending write
                    # should replace. Wait before publishing this block's OUT.
                    complete_block = False
                    break
                finally:
                    block_diagnostics[block_id].extend(interpreter.last_diagnostics)
            changed = complete_block and (block_id not in block_out or block_out[block_id] != state)
            evaluated.add(block_id)
            if complete_block:
                block_out[block_id] = state
            result.stats["block_evaluations"] += 1
            next_blocks = successors[block_id] if changed else set()
            if registry.revision != before_revision:
                next_blocks = next_blocks | evaluated
            for block in sorted(next_blocks):
                if block not in queued:
                    queued.add(block)
                    queue.append(block)
        if pending_errors:
            result.status = "incomplete"
            result.diagnostics.extend({"code": "unresolved_binding", "instruction_id": ir,
                                       "reason": error} for ir, error in sorted(pending_errors.items()))
    except PropagationLimitError as error:
        result.status = "resource_limit"
        result.diagnostics.append({"code": "resource_limit", "reason": str(error)})
    except (ValueError, KeyError) as error:
        result.status = "execution_error"
        result.diagnostics.append({"code": "execution_error", "reason": f"{type(error).__name__}: {error}"})
    for block_id in sorted(block_records):
        for ir_id, record in block_records[block_id].items():
            records.put(ir_id, record)
    # Only the latest evaluation of each block contributes diagnostics. Worklist
    # iterations are analysis attempts, not additional occurrences of a finding.
    result.diagnostics.extend(item for block in sorted(block_diagnostics)
                              for item in block_diagnostics[block])
    result.stats["data_count"] = len(registry)
    result.stats["record_count"] = len(records)
    result.stats["description_revision"] = registry.revision
    if annotation.unresolved:
        result.diagnostics.append({"code": "annotation_unresolved", "reason": "保留标注未决项；传播完成不表示未决已解决。",
                                   "items": payload["unresolved"]})
    records.validate()
    return result
