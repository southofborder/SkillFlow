"""Read-only forward effects of a boundary-local field exclusion.

The worklist describes possible change, not hypothetical replacement Data or
positive preservation demands. An intersecting influence is not necessity.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from .material import _id
from .constraint_results import ConstraintSupport
from .sensitivity_engine import prefix as _prefix, covers
from skillflow.common.source_evidence import resolve_pointer
from skillflow.propagation.contracts.references import target_key


def _overlap(a, b):
    return _prefix(a, b) or _prefix(b, a)


class ForwardInfluence:
    """Follow symbolic uses, compiler observation links and reaching writes."""
    def __init__(self, engine):
        self.engine = engine
        self.edges = defaultdict(set)
        self.member_sources = defaultdict(set)
        self.incomplete = False
        self._setup()

    def _resolve(self, ref, ir, scope=None):
        # Resolution may register a literal node, but never creates Data.
        before = set(self.engine.diagnostics)
        result = self.engine.resolve(ref, ir, scope)
        if not result or set(self.engine.diagnostics) != before:
            self.incomplete = True
        return result

    def _setup(self):
        e = self.engine
        for key, info in e.ops.items():
            ir = info["position"]["instruction_id"]
            for slot, (ref, _) in e.slots(key).items():
                target = e.node_at("op_input", ir, key, slot)
                for source in self._resolve(ref, ir, info["scope"]):
                    self.edges[source].add(target)
        for ir, spec in e.compiled["ir_semantics"].items():
            for binding in spec["output_bindings"]:
                target = e.node_at("ir_output", ir, slot=binding["output_index"])
                for source in self._resolve(binding["value"], ir):
                    self.edges[source].add(target)
        # Raw templates exist even when the current collection has no instance.
        # A changed collection can create occurrences absent from actual records.
        for ir, spec in e.raw["ir_semantics"].items():
            for index, event in enumerate(spec["events"]):
                if event.get("kind") == "for_each":
                    for source in self._resolve(event["collection"], ir):
                        self.member_sources[source].add((ir, index))
        for ir, instruction in e.index.instructions.items():
            for slot, operand in enumerate(instruction["inputs"]):
                if operand["type"] == "result":
                    producer, output = e.definitions[operand["identifier"]]
                    source = e.node_at("ir_output", producer, slot=output)
                    self.edges[source].add(e.node_at("ir_input", ir, slot=slot))
        for (_, _, _), node in e.elements.items():
            meta = e.nodes[node]
            for source in self._resolve(meta["reference"], meta["instruction_id"]):
                self.edges[source].add(node)

    def run(self, operation, slot, path, *, queue_order="fifo"):
        e, rows, queue = self.engine, {}, deque()
        affected, instructions, behavior, control_instructions, missing = set(), set(), set(), set(), self.incomplete
        changed_scopes = set()
        ir = e.ops[operation]["position"]["instruction_id"]
        initial = e.node_at("op_input", ir, operation, slot)

        def emit(node, changed, rule, parent=None):
            nonlocal missing
            if node is None:
                missing = True
                return
            # Finite static paths; widen rather than truncate an unbounded path.
            if len(changed) > e.path_budget:
                changed, rule = [], "range_widening"
            identity = _id("change_", [operation, slot, path, node, changed])
            if identity not in rows:
                rows[identity] = {"node": node, "path": deepcopy(changed), "rule": rule, "parents": []}
                queue.append(identity)
            else:
                rows[identity]["rule"] = min(rows[identity]["rule"], rule)
            if parent is not None and parent != identity:
                rows[identity]["parents"] = sorted(set(rows[identity]["parents"]) | {parent})

        def output(key, changed, parent, rule):
            info = e.ops[key]
            if "output" in info["spec"]:
                emit(e.node_at("op_output", info["position"]["instruction_id"], key, 0), changed, rule, parent)

        def whole_operation(key, parent, rule):
            affected.add(key)
            behavior.add(key)
            for position in e.slots(key):
                emit(e.node_at("op_input", e.ops[key]["position"]["instruction_id"], key, position), [], rule, parent)
            output(key, [], parent, rule)

        emit(initial, list(path), "boundary_input_change")
        while queue:
            identity = queue.popleft() if queue_order == "fifo" else queue.pop()
            row = rows[identity]
            node, changed = e.nodes[row["node"]], row["path"]
            if row["node"] in self.member_sources:
                changed_scopes.update(self.member_sources[row["node"]])
                # V1 cannot reconstruct changed member identities or lengths
                # from the baseline instances. Preserve this explicit gap.
                missing = True
            for target in sorted(self.edges.get(row["node"], ())):
                emit(target, changed, "symbolic_use", identity)
            kind, key, current_ir = node["kind"], node["operation_id"], node["instruction_id"]
            if current_ir is not None:
                instructions.add(current_ir)
            if kind == "element":
                # Membership/shape can change. Never pair this with another element.
                for other, info in e.ops.items():
                    if info["position"]["instruction_id"] == current_ir and info["scope"] == tuple(node["scope"]):
                        whole_operation(other, identity, "element_membership")
            if kind == "ir_input":
                instruction = e.index.instructions[current_ir]
                if instruction["opcode"] == "dispatch":
                    block = e.index.ir_block[current_ir]
                    descendants = e.index.reachable[block]
                    control_instructions.update(i for i, b in e.index.ir_block.items() if b in descendants)
                    for other, info in e.ops.items():
                        if e.index.ir_block[info["position"]["instruction_id"]] in descendants:
                            whole_operation(other, identity, "changed_control")
            if kind != "op_input":
                continue
            affected.add(key)
            info, input_slot = e.ops[key], node["slot"]
            if e.slots(key).get(input_slot, (None, None))[1] == "control":
                behavior.add(key)
            spec, record = info["spec"], info["record"]
            op = spec["op"]
            if op == "select_part":
                selected = spec["path"]
                if _overlap(changed, selected):
                    output(key, changed[len(selected):] if _prefix(selected, changed) else [], identity, "selected_change")
            elif op == "exclude_parts":
                if not any(covers(p, changed) for p in spec["paths"]):
                    output(key, changed, identity, "remaining_change")
            elif op == "update_fields":
                if input_slot == 0:
                    if not any(covers(u["path"], changed) for u in spec["updates"]):
                        output(key, changed, identity, "unchanged_fields")
                else:
                    output(key, spec["updates"][input_slot - 1]["path"] + changed, identity, "replacement_change")
            elif op == "build":
                for member in record["members"]:
                    if member["value_input_index"] == input_slot:
                        output(key, member["path"] + changed, identity, "member_change")
                    if member["when_input_index"] == input_slot:
                        output(key, member["path"], identity, "member_presence_change")
            elif op in {"compute", "filter_items", "receive"}:
                output(key, [], identity, "conservative_processing_change")
            elif op == "read":
                output(key, changed, identity, "read_change")
            elif op == "write":
                for link in e.index.links.values():
                    if link["kind"] == "saved_read" and link["source"] == key:
                        affected.add(link["target"])
                        output(link["target"], changed if spec["mode"] == "replace" else [], identity, "reaching_write_change")
                location = e.compiled["locations"][spec["target"]]
                for target_ir, reaching in e.index.entry_writes.items():
                    if key not in reaching.get((location["kind"], location["name"]), set()):
                        continue
                    for operand in location["operand_refs"]:
                        if operand["instruction_id"] == target_ir and operand["side"] == "input":
                            emit(e.node_at("ir_input", target_ir, slot=operand["index"]),
                                 changed if spec["mode"] == "replace" else [], "saved_operand_change", identity)
            elif op == "deliver" and info["generated"]:
                ref = e.slots(key).get(input_slot)
                source_nodes = set(self._resolve(ref[0], current_ir, info["scope"])) if ref else set()
                for other, consumer in e.ops.items():
                    if (consumer["generated"] or consumer["mode"] == "local"
                        or consumer["position"]["instruction_id"] != current_ir
                        or consumer["scope"] != info["scope"] or consumer["segment"] != info["segment"]):
                        continue
                    for consumer_slot, (value, _) in e.slots(other).items():
                        if source_nodes.intersection(self._resolve(value, current_ir, consumer["scope"])):
                            emit(e.node_at("op_input", current_ir, other, consumer_slot), changed,
                                 "model_processing_change", identity)
                if info["return_observation"]:
                    for binding in e.compiled["ir_semantics"][current_ir]["output_bindings"]:
                        if source_nodes.intersection(self._resolve(binding["value"], current_ir)):
                            emit(e.node_at("ir_output", current_ir, slot=binding["output_index"]), changed,
                                 "returned_observation_change", identity)
            elif op == "deliver":
                paired = [link["target"] for link in e.index.links.values()
                          if link["kind"] == "request_response" and link["source"] == key]
                for receipt in paired:
                    affected.add(receipt)
                    output(receipt, [], identity, "request_response_change")
                target = e.compiled["locations"][spec["target"]]
                # No response record does not certify isolation of an opaque boundary.
                if not paired and target["kind"] in {"tool", "remote"}:
                    missing = True
            if len(rows) > 100000:
                missing = True
                break
        return {"steps": {k: rows[k] for k in sorted(rows)}, "affected": affected, "instructions": instructions,
                "behavior": behavior, "control_instructions": control_instructions,
                "changed_scopes": changed_scopes,
                "complete": not (missing or self.incomplete), "root": initial}


class ConstraintAnalysis:
    def __init__(self, engine):
        from .constraint_engine import ConstraintEngine
        self.engine = engine
        self.checker = ConstraintEngine(engine)
        self.checks = self.checker.check()
        self.preservation, self.influence, self.cache = {}, {}, {}
        self.forward = None

    def evaluate(self, operation, slot, data_id, path):
        """Return references and a gate, never alter a positive task demand."""
        if not self.checks:
            return [], True
        cache_key = _id("candidate_", [operation, slot, data_id, path])
        if cache_key not in self.cache:
            if self.forward is None:
                self.forward = ForwardInfluence(self.engine)
            self.cache[cache_key] = self.forward.run(operation, slot, path)
        closure = self.cache[cache_key]
        self.influence.update(closure["steps"])
        refs = []
        for constraint_id, check in sorted(self.checks.items()):
            preserved, rule = False, "not_established"
            reason = "A complete preservation argument has not been established; this does not prove necessity or a violation."
            complete_scope = self.checker.complete_scope(constraint_id)
            info = self.engine.ops[operation]
            declaration = resolve_pointer(self.engine.raw, check["raw_pointer"])
            protected_ir = set()
            conditions = set()
            if check["kind"] != "forbid_information":
                for field in ("events", "before", "after", "triggers"):
                    protected_ir.update(ref["instruction_id"] for ref in declaration.get(field, [])
                                        if "operation_path" not in ref)
                for field in ("condition", "success"):
                    ref = declaration.get(field)
                    if ref:
                        entry = self.engine.targets.get(target_key(ref), {})
                        owner = entry.get("instruction_id")
                        if owner is not None:
                            conditions.add(owner)
            # Structural checks quantify over all controls, not just baseline values.
            if complete_scope and check["structural"] and info["scope"] is None and not closure["changed_scopes"]:
                preserved, rule = True, "structural"
                reason = "The complete structural check is independent of affected value and guard choices; event identity and task scope remain fixed."
            elif complete_scope and closure["complete"]:
                relevant = set(check["operations"])
                other = closure["affected"] - {operation}
                if (check["kind"] == "forbid_information" and not other
                    and info["spec"]["op"] == "deliver" and not info["generated"]):
                    preserved, rule = True, "terminal_subset"
                    reason = "This terminal delivery only loses content; its complete modeled effects introduce no later content or behavior change. Baseline findings remain visible."
                elif check["kind"] != "forbid_information" and (
                    not closure["behavior"].intersection(relevant)
                    and not closure["control_instructions"].intersection(protected_ir)
                    and not closure["instructions"].intersection(conditions)):
                    preserved, rule = True, "no_influence"
                    reason = "The complete change closure cannot alter relevant event occurrence, ordering, scope or evaluated condition. Payload changes are not automatically event changes."
                elif check["kind"] == "forbid_information" and not closure["affected"].intersection(relevant):
                    preserved, rule = True, "no_influence"
                    reason = "The complete forward influence closure is disjoint from the constraint's applicable events and checked observations."
            if not preserved and closure["changed_scopes"]:
                reason += " The changed collection may create or change member occurrences; baseline instances do not certify their absence or identity."
            row = {"constraint_id": constraint_id, "operation_id": operation, "input_index": slot,
                "data_id": data_id, "path": deepcopy(path), "preserved": preserved, "rule": rule,
                "reason": reason, "influence_refs": sorted(closure["steps"]) if rule != "structural" else []}
            identity = _id("preservation_", [constraint_id, operation, slot, data_id, path])
            self.preservation[identity] = row
            refs.append(identity)
        return refs, all(self.preservation[key]["preserved"] for key in refs)

    def to_dict(self):
        used = {i for row in self.preservation.values() for i in row["influence_refs"]}
        return ConstraintSupport.model_validate({"checks": self.checks,
            "preservation": {k: self.preservation[k] for k in sorted(self.preservation)},
            "influence": {k: {**self.influence[k], "node": deepcopy(self.engine.nodes[self.influence[k]["node"]])}
                          for k in sorted(used)}}).model_dump(mode="json")
