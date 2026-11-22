"""Backwards protection for a required action with no established occurrence.

These are conservative obligations over checked declarations. The trace never
creates an operation record, supplies an argument, or says the action ran.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import TypeAdapter

from skillflow.propagation.contracts.demand import goal_target_capability
from skillflow.propagation.contracts.locations import locations_may_alias
from skillflow.propagation.contracts.paths import split_semantics_path
from skillflow.propagation.contracts.specs import (
    ForEachSpec, IRSemantics, operation_items, precedence_edges,
)
from skillflow.propagation.contracts.uses import active_value_uses, static_condition
from skillflow.propagation.contracts.values import ValueRef

from .demand_engine import _expanded_need, _prepend_need, need

_VALUE = TypeAdapter(ValueRef)


class UnavailableDependencies:
    def __init__(self, engine):
        self.engine = engine
        self.index = engine.index
        self.compiled = engine.compiled
        self.faults = {}
        for item in self.index.diagnostics:
            if item["code"] not in {"operation_execution_error", "unresolved_path", "unresolved_binding"}:
                continue
            coords = item.get("affected_instruction_ids", [item.get("instruction_id")])
            for ir in filter(None, coords):
                self.faults.setdefault(ir, []).append(item)
        self._mapped_events = {}
        for row in engine.annotation["mapping"]["events"]:
            if row["kind"] != "observation" and row["raw_atomic_range"] is not None:
                owner, raw = split_semantics_path(row["raw_path"])
                _, compiled = split_semantics_path(row["compiled_path"])
                start, end = row["raw_atomic_range"]
                for offset in range(end - start):
                    self._mapped_events[(owner, (*raw, "atomic_ops", start + offset))] = (
                        compiled[1], compiled[3] if len(compiled) > 2 else None, offset)
        # Keep caches on this invocation; a review must not retain other runs.
        self._semantics = lru_cache(maxsize=None)(self._semantics)

    def _semantics(self, ir):
        raw = self.compiled["ir_semantics"].get(ir)
        if raw is None:
            return {}, {}, {}, set()
        spec = IRSemantics.model_validate(raw)
        operations = operation_items(spec)
        membership = {i: event for i, event in enumerate(spec.events) if isinstance(event, ForEachSpec)}
        definitions = {(event if body is not None else None, op.output): ("operation", key)
                       for key, op in operations.items() for event, body, _ in [key]
                       if getattr(op, "output", None) is not None}
        for event, collection in membership.items():
            definitions[(event, collection.item)] = ("item", event)
            if collection.output is not None:
                definitions[(None, collection.output)] = ("collection", event)
        return operations, membership, definitions, precedence_edges(spec)

    def has_incomplete_execution(self, ir):
        return self.index.coverage[ir] != "processed" or ir in self.faults

    def evidence(self, goal, target):
        ir = target.get("instruction_id")
        if (goal["preserve"] != "action" or ir is None or self.index.coverage[ir] == "infeasible"
                or goal_target_capability(target, "action") is None):
            return None
        problem = self._action_problem(ir)
        if problem is None:
            return None
        target_path = target.get("operation_raw_path", target.get("raw_path", []))
        return {"code": "unavailable_required_action", "reason":
                f"Required action {goal['id']} at {ir} {target_path!r} has an unestablished occurrence: "
                + problem + " Preserve its declared dependency ranges until a valid occurrence or a verified exclusion resolves the goal.",
                "instruction_id": ir, "requirement_id": goal["requirement_id"],
                "operation_id": None, "blocking": True}

    def _action_problem(self, ir):
        row = self.faults.get(ir, [])
        if row:
            points = sorted({self._fault_point(item) for item in row})
            return "Checked propagation reports " + "; ".join(points) + "."
        state = self.index.coverage[ir]
        if state != "processed":
            return f"Checked propagation coverage for this instruction is {state}; no complete occurrence covers the goal."
        return None

    @staticmethod
    def _fault_point(item):
        ir = item.get("instruction_id") or "the goal instruction"
        if item["code"] == "operation_execution_error":
            position = f"{ir}/events/{item['event_index']}"
            if item.get("body_event_index") is not None:
                position += f"/body/{item['body_event_index']}"
            position += "/collection" if item.get("op_index") is None else f"/atomic_ops/{item['op_index']}"
            return f"{item['error_type']} at {position}: {item['reason']}"
        return f"{item['code']} at {ir}: {item['reason']}"

    def action(self, ir, target, requirement, parent):
        operation_path = tuple(target.get("operation_raw_path", target.get("raw_path", [])))
        coordinate = self._mapped_events.get((ir, operation_path))
        if target["kind"] == "instruction":
            # An IR-level goal can include any declared operand, independently
            # of the effects that a failed forward attempt happened to record.
            self._all_inputs(ir, requirement, parent)
            for coordinate in self._semantics(ir)[0]:
                self._operation(ir, coordinate, None, requirement, parent, frozenset())
        else:
            if coordinate is None:
                raise ValueError("Unavailable action target has no checked compilation coordinate")
            self._operation(ir, coordinate, None, requirement, parent, frozenset())
        for fault in self.faults.get(ir, []):
            if fault["code"] != "operation_execution_error":
                continue
            source = fault["instruction_id"]
            coordinate = (fault["event_index"], fault.get("body_event_index"), fault.get("op_index"))
            if coordinate[2] is None:
                loop = self._semantics(source)[1][coordinate[0]]
                self._reference(loop.collection, source, None, need(), requirement, parent, frozenset())
            else:
                self._operation(source, coordinate, None, requirement, parent, frozenset())

    def output(self, ir, binding, wanted, requirement, parent):
        if binding is None:
            self._all_inputs(ir, requirement, parent)
            return
        self._reference(_VALUE.validate_python(binding["value"]), ir, None,
                        wanted, requirement, parent, frozenset())

    def _input(self, ir, slot, wanted, requirement, parent):
        self.engine.emit(self.engine.node_at("ir_input", ir, slot=slot), wanted, requirement,
                         "declared_unavailable_operand", parent, True)

    def _all_inputs(self, ir, requirement, parent):
        for slot in range(len(self.index.instructions[ir]["inputs"])):
            self._input(ir, slot, need(), requirement, parent)

    def _reference(self, ref, ir, scope, wanted, requirement, parent, visited):
        if ref.kind == "input":
            self._input(ir, ref.index, wanted, requirement, parent)
        elif ref.kind == "alternatives":
            for child in ref.items:
                self._reference(child, ir, scope, wanted, requirement, parent, visited)
        elif ref.kind == "local":
            _, membership, definitions, _ = self._semantics(ir)
            origin = definitions.get((scope, ref.name), definitions.get((None, ref.name)))
            if origin is None:
                self._all_inputs(ir, requirement, parent)
                return
            kind, coordinate = origin
            if kind == "operation":
                self._operation(ir, coordinate, wanted, requirement, parent, visited)
            else:
                collection = membership[coordinate]
                self._reference(collection.collection, ir, None, need("shape"), requirement, parent, visited)
                if kind == "item":
                    self._reference(collection.collection, ir, None, _prepend_need(wanted, [{"kind": "each"}]),
                                    requirement, parent, visited)
                elif collection.yield_value is not None:
                    expanded = _expanded_need(wanted)
                    path = expanded["path"]
                    if path or expanded["property"] not in {"presence", "cardinality"}:
                        member = need(expanded["property"], path[1:]) if path else need()
                        self._reference(collection.yield_value, ir, coordinate, member,
                                        requirement, parent, visited)

    def _operation(self, ir, coordinate, wanted, requirement, parent, visited):
        identity = (ir, coordinate)
        if identity in visited:
            return
        visited = visited | {identity}
        operations, loops, _, _ = self._semantics(ir)
        op = operations[coordinate]
        event, body, _ = coordinate
        scope = event if body is not None else None
        if scope is not None:
            self._reference(loops[scope].collection, ir, None, need("shape"), requirement, parent, visited)
        location = self.compiled["locations"].get(getattr(op, "target", getattr(op, "location", None)))
        if location is not None:
            for operand in location["operand_refs"]:
                if operand["instruction_id"] == ir and operand["side"] == "input":
                    self._input(ir, operand["index"], need(), requirement, parent)
            if op.op == "read" or op.op == "write" and op.mode == "append":
                self._location(ir, coordinate, location, wanted or need(), requirement, parent, visited)
        instruction = self.index.instructions[ir]
        if op.op == "select_part":
            self._reference(op.input, ir, scope, _prepend_need(wanted or need(), op.path),
                            requirement, parent, visited)
            return
        if op.op == "branch":
            self._reference(op.input, ir, scope, need("truth" if op.predicate == "truthy" else "cardinality"),
                            requirement, parent, visited)
            return
        for use in active_value_uses(op, instruction):
            if use.role == "control" and static_condition(use.value, instruction) is not None:
                continue
            passthrough = op.op == "merge" or op.op == "write" and op.mode == "replace"
            transferred = (need("truth") if use.role == "control" else wanted
                           if passthrough and wanted is not None else need())
            self._reference(use.value, ir, scope, transferred, requirement, parent, visited)

    def context_operand(self, ir, slot, wanted, requirement, parent):
        operand = self.index.instructions[ir]["inputs"][slot]
        if operand["type"] != "context_key":
            return
        declarations = self.compiled["locations"].values()
        reference = {"instruction_id": ir, "side": "input", "index": slot}
        locations = [value for value in declarations if reference in value["operand_refs"]]
        if not locations:
            # Match interpreter.context_locations: an unanchored context key
            # denotes its exact implicit address, not every runtime value.
            name = operand["identifier"]
            locations = [value for value in declarations if value["kind"] == "runtime_context" and value["name"] == name]
            if not locations:
                locations = [{"kind": "runtime_context", "name": name, "address_kind": "identified"}]
        for location in locations:
            self._location(ir, None, location, wanted, requirement, parent, frozenset())

    def _location(self, ir, coordinate, location, wanted, requirement, parent, visited):
        """Trace recorded reaching writes and only possibly preceding typed writes."""
        for (kind, name), writes in self.index.entry_writes.get(ir, {}).items():
            if not locations_may_alias(location, {"kind": kind, "name": name, "address_kind": "identified"}):
                continue
            for key in sorted(writes):
                spec = self.engine.ops[key]["spec"]
                if spec["mode"] != "delete":
                    self.engine.input(key, 0, wanted if spec["mode"] == "replace" else need(), requirement,
                                      "declared_unavailable_reaching_write", parent, True)
        for source in self.index.instructions:
            if self.index.coverage[source] == "infeasible":
                continue
            same_occurrence = source == ir and coordinate is not None
            if not same_occurrence and (not self.has_incomplete_execution(source)
                                        or not self.index.ir_may_before(source, ir)):
                continue
            operations, _, _, precedence = self._semantics(source)
            downstream = {}
            for before, after in precedence:
                downstream.setdefault(before, set()).add(after)
            definitely_after = self.index._closure([coordinate], downstream) if same_occurrence else set()
            for point, write in operations.items():
                if (point not in definitely_after and write.op == "write" and write.mode != "delete"
                        and locations_may_alias(location, self.compiled["locations"][write.target])):
                    self._operation(source, point, wanted, requirement, parent, visited)
