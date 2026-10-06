"""Deterministic abstract operations, never execution of Skill code or opcodes."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
import json

from pydantic import TypeAdapter

from skillflow.propagation.data import DataPart
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import Dependency
from skillflow.propagation.data import FieldUpdatesContent
from skillflow.propagation.data import KnownPartsContent
from skillflow.propagation.data import LiteralContent
from skillflow.propagation.data import OpaqueContent
from skillflow.propagation.data import Origin
from skillflow.propagation.data import WholeExceptContent
from skillflow.propagation.data import SubsetViewContent
from skillflow.propagation.data.registry import DataReferenceError
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.models import AtomicOpRecord
from skillflow.propagation.models import EffectEvent
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.models import FlowState
from skillflow.propagation.models import IRFlowRecord
from skillflow.propagation.models import StateChange
from skillflow.propagation.models import ForEachRecord
from skillflow.propagation.models import ForEachInstance
from skillflow.propagation.models import BuildMemberRecord
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.contracts.specs import IRTransferSpec
from skillflow.propagation.contracts.specs import value_refs
from skillflow.propagation.contracts.specs import iter_effect_events
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.contracts.uses import active_value_uses

_ATOMIC_SPEC = TypeAdapter(AtomicOp)


class PendingValue(ValueError):
    """No current candidate, not an unknown external source or an empty value."""


class PropagationLimitError(RuntimeError):
    """Explicit resource failure, never a successful truncated solution."""


def plain(value):
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def mapping(state: FlowState) -> dict[FlowLocation, frozenset[str]]:
    return {b.location: b.data_ids for b in state.bindings}


def join_states(states):
    joined = {}
    for state in states:
        for location, ids in state.items():
            joined[location] = joined.get(location, frozenset()) | ids
    return {loc: ids for loc, ids in joined.items() if ids}


def static_key(*parts):
    return "transfer:" + json.dumps(parts, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


class TransferInterpreter:
    def __init__(self, cfg, annotation, registry: DataRegistry, *, max_variants=100000):
        self.cfg = cfg
        self.annotation = annotation
        self.registry = registry
        self.max_variants = max_variants
        self._last_diagnostics = []
        self._step_diagnostics = []
        self._request_pairs = {}
        # A caller may intentionally reuse a registry namespace across runs.
        # Different frozen rules must still never refine an older result ID.
        self.rule_identity = canonical_sha256({"cfg": cfg, "annotation": annotation})
        self.locations = {
            name: FlowLocation(kind=loc["kind"], name=loc["name"])
            for name, loc in annotation["locations"].items()
        }
        self.operand_locations = {}
        for name, loc in annotation["locations"].items():
            for ref in loc["operand_refs"]:
                key = (ref["instruction_id"], ref["side"], ref["index"])
                self.operand_locations.setdefault(key, set()).add(self.locations[name])

    @property
    def last_diagnostics(self):
        """Detached diagnostics for the latest IR evaluation, never an iteration log."""
        return deepcopy(self._last_diagnostics)

    def aliases(self, location):
        symbolic = location.name.startswith("symbolic:")
        return sorted({location, *(
            loc for loc in self.locations.values()
            if loc.kind == location.kind and (symbolic or loc.name.startswith("symbolic:"))
        )}, key=lambda loc: (loc.kind, loc.name))

    def read_location(self, location, state):
        return frozenset().union(*(state.get(loc, frozenset()) for loc in self.aliases(location)))

    def context_locations(self, ir, index):
        """Resolve the same declared value locations for seeds, reads and cycles.

        A location anchor associates the operand's value, not a containing
        object's provenance. Container reads instead name the location directly.
        """
        operand = ir.get("inputs", [])[index]
        if operand["type"] != "context_key":
            return set()
        return set(self.operand_locations.get((ir["id"], "input", index), {
            FlowLocation(kind="runtime_context", name=operand["identifier"])
        }))

    def referenced_context_locations(self, ir, ref):
        ref = plain(ref)
        if ref["kind"] == "input":
            return self.context_locations(ir, ref["index"])
        if ref["kind"] == "alternatives":
            return set().union(*(self.referenced_context_locations(ir, child) for child in ref["items"]))
        return set()

    def initial_locations(self):
        """Only explicit reads/appends and actually used context values seed Data.

        Declaring an operand or a tool boundary alone never allocates content.
        """
        locations = set()
        for block in self.cfg["blocks"].values():
            for ir in block["instructions"]:
                spec = self.annotation["transfer_specs"][ir["id"]]
                typed_spec = IRTransferSpec.model_validate(spec)
                for event in typed_spec.events:
                    if getattr(event, "kind", None) == "for_each":
                        locations.update(self.referenced_context_locations(ir, event.collection))
                for event in iter_effect_events(typed_spec):
                    for operation in event.atomic_ops:
                        op = plain(operation)
                        if op["op"] == "read":
                            locations.add(self.locations[op["location"]])
                        elif op["op"] == "write" and op["mode"] == "append":
                            locations.add(self.locations[op["target"]])
                        for use in active_value_uses(_ATOMIC_SPEC.validate_python(op), ir):
                            locations.update(self.referenced_context_locations(ir, use.value))
                for binding in spec["output_bindings"]:
                    locations.update(self.referenced_context_locations(ir, binding["value"]))
        return locations

    def literal(self, value, position):
        return self.registry.create_result(
            static_key(self.rule_identity, "literal", position), content=LiteralContent(value=value),
            origin=Origin(at=str(position)),
        ).id

    def resolve(self, ref, ir, state, locals_, position):
        ref = plain(ref)
        kind = ref["kind"]
        if kind == "literal":
            return frozenset([self.literal(ref["value"], position)])
        if kind == "local":
            return locals_.get(ref["name"], frozenset())
        if kind == "alternatives":
            return frozenset().union(*(
                self.resolve(item, ir, state, locals_, [position, i])
                for i, item in enumerate(ref["items"])
            ))
        # IR operands denote entry values. A later shared-state read must be
        # an explicit read operation; re-resolving input(context_key) against
        # mutable stage state would silently change versions under one symbol.
        index = ref["index"]
        if self._entry_instruction != ir["id"]:
            raise ValueError("input references require the current IR entry snapshot")
        if index not in self._entry_inputs:
            operand = ir.get("inputs", [])[index]
            if operand["type"] == "literal":
                ids = frozenset([self.literal(operand.get("literal_value"), [ir["id"], "input", index])])
            elif operand["type"] == "result":
                ids = self._entry_state.get(FlowLocation(kind="result", name=operand["identifier"]), frozenset())
            elif operand["type"] == "external_resource":
                raise ValueError("resource identity is not a data payload; use an evidenced literal or read")
            else:
                ids = frozenset().union(*(self.read_location(loc, self._entry_state)
                                         for loc in self.context_locations(ir, index)))
            self._entry_inputs[index] = ids
        return self._entry_inputs[index]

    def _tuples(self, inputs):
        count = 1
        for ids in inputs:
            count *= len(ids)
        if count > self.max_variants:
            raise PropagationLimitError(f"candidate product {count} exceeds {self.max_variants}")
        return product(*(sorted(ids) for ids in inputs))

    def _result(self, position, inputs, content, *, relations=None, acquired_from=None):
        relations = relations if relations is not None else ["derived"] * len(inputs)
        deps = []
        for data_id, relation in zip(inputs, relations):
            if not any(d.data == data_id and d.relation == relation for d in deps):
                deps.append(Dependency(data=data_id, relation=relation))
        return self.registry.create_result(
            static_key(self.rule_identity, position, list(inputs)), content=content,
            origin=Origin(at=str(position), acquired_from=acquired_from, inputs=list(inputs),
                          dependencies=deps),
        ).id

    def _build_candidates(self, ir, op, state, locals_, pos):
        """Resolve controls first and retain correlated inclusion shapes."""
        inputs, members, groups, slots = [], [], [], []
        guard_values = {}
        for i, member in enumerate(op["parts"]):
            guard = member.get("when")
            guard_index = None
            group = None
            if guard is not None:
                guard_key = canonical_sha256(guard)
                if guard_key not in guard_values:
                    # A repeated symbolic condition is evaluated once for this
                    # construction, including alternatives containing literals.
                    # Parameter slots still repeat its same candidate set.
                    guard_values[guard_key] = self.resolve(guard, ir, state, locals_, [pos, "condition", guard_key])
                ids = guard_values[guard_key]
                if not ids:
                    raise PendingValue(f"{pos}: member[{i}] condition has no candidates")
                truths = guard_truths(self.registry, ids)
                guard_index = len(inputs)
                inputs.append(ids)
                if ids not in groups:
                    groups.append(ids)
                group = groups.index(ids)
            else:
                truths = frozenset([True])
            value_index = None
            if True in truths:
                ids = self.resolve(member["value"], ir, state, locals_, [pos, "member", i, "value"])
                if not ids:
                    raise PendingValue(f"{pos}: possibly included member[{i}] has no value candidates")
                value_index = len(inputs)
                inputs.append(ids)
            members.append(BuildMemberRecord(path=member["path"], value_input_index=value_index,
                                             when_input_index=guard_index))
            slots.append(group)
        options = [[(data_id, truth) for data_id in sorted(ids)
                    for truth in sorted(guard_truths(self.registry, [data_id]))] for ids in groups]
        count = 1
        for choices in options:
            count *= len(choices)
        if count > self.max_variants:
            raise PropagationLimitError(f"condition candidate product {count} exceeds {self.max_variants}")
        variants = []
        for assignment in product(*options):
            chosen_truths = {}
            for data_id, truth in assignment:
                if data_id in chosen_truths and chosen_truths[data_id] != truth:
                    break
                chosen_truths[data_id] = truth
            else:
                selected = [i for i, group in enumerate(slots)
                            if group is None or assignment[group][1]]
                value_slots = [members[i].value_input_index for i in selected]
                for values in self._tuples([inputs[index] for index in value_slots]):
                    chosen_values = dict(zip(selected, values))
                    args = []
                    for i, member in enumerate(members):
                        if slots[i] is not None:
                            args.append(assignment[slots[i]][0])
                        if i in chosen_values:
                            args.append(chosen_values[i])
                    content = (KnownPartsContent(parts=[DataPart(path=op["parts"][i]["path"], data=chosen_values[i])
                                                        for i in selected], parts_complete=True)
                               if selected else LiteralContent(value=[] if op["container"] == "list" else {}))
                    shape = [op["parts"][i]["path"] for i in selected]
                    variants.append((args, content, shape))
                    if len(variants) > self.max_variants:
                        raise PropagationLimitError("conditional build variants exceed configured resource limit")
        return inputs, members, variants

    def execute(self, ir, event_index, op_index, operation, state, locals_, *, uncertain=False, body_event_index=None, request_inputs=None):
        self._step_diagnostics = []
        op = plain(operation)
        pos = ([ir["id"], event_index, op_index] if body_event_index is None
               else [ir["id"], event_index, "body", body_event_index, op_index])
        kind = op["op"]
        members, when_input_index, build_variants = None, None, None
        if kind == "build":
            inputs, members, build_variants = self._build_candidates(ir, op, state, locals_, pos)
        elif kind == "deliver" and op.get("when") is not None:
            guard = self.resolve(op["when"], ir, state, locals_, [pos, "when"])
            if not guard:
                raise PendingValue(f"{pos}: observation condition has no candidates")
            inputs = ([self.resolve(ref, ir, state, locals_, [pos, "input", i])
                       for i, ref in enumerate(op["inputs"])] if True in guard_truths(self.registry, guard) else [])
            when_input_index = len(inputs)
            inputs.append(guard)
        elif kind == "receive" and request_inputs is not None:
            # These are the actual previously delivered versions, not a second
            # symbolic read or a newly allocated literal at the receive site.
            inputs = list(request_inputs)
        else:
            refs = [plain(r) for r in value_refs(operation)]
            inputs = [self.resolve(r, ir, state, locals_, [pos, "input", i]) for i, r in enumerate(refs)]
        if any(not ids for ids in inputs):
            raise PendingValue(f"{pos}: input has no available data candidates")
        outputs = set()
        endpoints, changes = [], []
        if kind == "read":
            location = self.locations[op["location"]]
            endpoints.append(location)
            outputs.update(self.read_location(location, state))
        elif kind == "receive":
            location = self.locations[op["location"]]
            endpoints.append(location)
            for args in self._tuples(inputs):
                outputs.add(self._result(pos, args, OpaqueContent(), relations=["possible"] * len(args),
                                         acquired_from=f"{location.kind}:{location.name}"))
        elif kind == "deliver":
            endpoints.append(self.locations[op["target"]])
        elif kind == "write":
            location = self.locations[op["target"]]
            endpoints.append(location)
            targets = self.aliases(location)
            for target in targets:
                before = state.get(target, frozenset())
                weak = uncertain or target != location or location.name.startswith("symbolic:")
                if op["mode"] == "delete":
                    after = before if weak else frozenset()
                elif op["mode"] == "replace":
                    after = inputs[0] | before if weak else inputs[0]
                else:
                    old = before
                    if not old:
                        # Initial sources are seeded once. Absence after an explicit
                        # seed/deletion cannot resurrect a hypothetical old file.
                        raise PendingValue(f"{pos}: append target has no prior content candidates")
                    appended = frozenset(self._result([pos, "append", target.kind, target.name], args,
                                                     OpaqueContent())
                                          for args in self._tuples([old, inputs[0]]))
                    after = appended | before if weak else appended
                if after:
                    state[target] = after
                else:
                    state.pop(target, None)
                changes.append(StateChange(location=target, before=before, after=after,
                                           update="weak" if weak else ("delete" if op["mode"] == "delete" else "strong")))
        elif kind == "select_part":
            for base in sorted(inputs[0]):
                try:
                    outputs.add(self.registry.resolve_part(base, op["path"]).id)
                except DataReferenceError as error:
                    self._step_diagnostics.append({
                        "code": "missing_part", "instruction_id": ir["id"],
                        "event_index": event_index, "op_index": op_index,
                        "data_id": base, "reason": str(error),
                    })
                    if body_event_index is not None:
                        self._step_diagnostics[-1]["body_event_index"] = body_event_index
        elif kind == "filter_items":
            for args in self._tuples(inputs):
                outputs.add(self._result(pos, args, SubsetViewContent(base=args[0], predicate=op["predicate"])))
        elif kind == "exclude_parts":
            for args in self._tuples(inputs):
                outputs.add(self._result(pos, args, WholeExceptContent(base=args[0], excluded_parts=op["paths"])))
        elif kind == "update_fields":
            for args in self._tuples(inputs):
                updates = [DataPart(path=item["path"], data=data_id)
                           for item, data_id in zip(op["updates"], args[1:])]
                outputs.add(self._result(pos, args, FieldUpdatesContent(base=args[0], updates=updates)))
        elif kind == "build":
            for args, content, shape in build_variants:
                outputs.add(self._result([pos, "members", shape], args, content))
        elif kind == "compute":
            for args in self._tuples(inputs):
                outputs.add(self._result(pos, args, OpaqueContent(), relations=op["dependencies"]))
        else:
            raise ValueError(f"unsupported abstract operation: {kind}")
        resolved_outputs = []
        if "output" in op:
            if not outputs:
                raise PendingValue(f"{pos}: output has no candidates (not an opaque source)")
            locals_[op["output"]] = frozenset(outputs)
            resolved_outputs = [frozenset(outputs)]
        return AtomicOpRecord(op=kind, inputs=inputs, outputs=resolved_outputs,
                              endpoints=endpoints, changes=changes,
                              members=members, when_input_index=when_input_index)

    def bind_outputs(self, ir, spec, state, locals_):
        for binding in spec["output_bindings"]:
            index = binding["output_index"]
            ids = self.resolve(binding["value"], ir, state, locals_, [ir["id"], "output", index])
            if not ids:
                raise PendingValue(f"{ir['id']}: output[{index}] has no available data candidates")
            operand = ir["outputs"][index]
            # Public result registration is not a shared-context write.
            if operand["type"] != "result":
                raise ValueError("output_bindings only registers actual result operands")
            state[FlowLocation(kind="result", name=operand["identifier"])] = ids

    def _effect_record(self, ir, event, operations):
        index = event.effect_index
        effects = self.annotation["profiles"][ir["id"]]["effects"]
        return EffectEvent(effect=None if index is None else effects[index], atomic_ops=operations)

    def _for_each(self, ir, event_index, event, state, locals_, *, uncertain):
        collections = self.resolve(event.collection, ir, state, locals_,
                                   [ir["id"], event_index, "collection"])
        if not collections:
            raise PendingValue(f"{ir['id']}/{event_index}: collection has no available candidates")
        instances, diagnostics = [], []
        scope = static_key(self.rule_identity, ir["id"], event_index, "element")
        for collection in sorted(collections):
            # Unknown collections have one scoped representative. Known finite
            # lists retain each real member; an explicit empty list has none.
            for element in self.registry.resolve_elements(collection, scope):
                scoped_locals = {**locals_, event.item: frozenset([element.id])}
                outcomes = self._arrangements(ir, event.body, dict(state), scoped_locals,
                                              uncertain=uncertain, outer_event=event_index)
                if not outcomes:
                    raise PendingValue(f"{ir['id']}/{event_index}: member scope cannot resolve its body")
                for final_state, _, records, found in outcomes:
                    if final_state != state:
                        raise ValueError("for_each body must not update shared state")
                    body = [self._effect_record(ir, body_event,
                            [records[(b, o)] for o in range(len(body_event.atomic_ops))])
                            for b, body_event in enumerate(event.body)]
                    instances.append(ForEachInstance(collection=collection, element=element.id, body=body))
                    diagnostics.extend(found)
        # Keep each complete scoped arrangement. Unioning each argument across
        # members would fabricate cross-member recipient/payload combinations.
        unique = {canonical_sha256(item.model_dump(mode="json")): item for item in instances}
        return ForEachRecord(kind="for_each", collections=collections,
                             instances=[unique[key] for key in sorted(unique)]), diagnostics

    def _arrangements(self, ir, events, state, locals_, *, uncertain, outer_event=None):
        from skillflow.propagation.contracts.specs import schedule_dependencies
        dependencies = schedule_dependencies(self._current_spec, outer_event=outer_event)
        atoms = [(e, -1, event) if getattr(event, "kind", None) == "for_each" else (e, o, op)
                 for e, event in enumerate(events)
                 for o, op in ([(-1, event)] if getattr(event, "kind", None) == "for_each"
                               else enumerate(event.atomic_ops))]
        outcomes = []

        def visit(current, local_values, done, records, diagnostics):
            self._attempts += 1
            if self._attempts > self.max_variants:
                raise PropagationLimitError("partial-order arrangements exceed configured resource limit")
            if len(done) == len(atoms):
                outcomes.append((current, local_values, records, diagnostics))
                return
            for ordinal, (e, o, op) in enumerate(atoms):
                if (e, o) in done or not dependencies.get((e, o), set()) <= done:
                    continue
                if not uncertain and len(done) != ordinal:
                    continue
                next_state, next_locals = dict(current), dict(local_values)
                try:
                    if o == -1:
                        rec, found = self._for_each(ir, e, op, next_state, next_locals, uncertain=uncertain)
                    else:
                        coordinate = (e, None, o) if outer_event is None else (outer_event, e, o)
                        request = self._request_pairs.get(coordinate)
                        request_inputs = None
                        if request is not None:
                            key = (request[0], request[2]) if outer_event is None else (request[1], request[2])
                            if key not in records:
                                raise PendingValue("matched request delivery has not been evaluated")
                            request_inputs = records[key].inputs
                        rec = self.execute(ir, e if outer_event is None else outer_event, o, op,
                                           next_state, next_locals, uncertain=uncertain,
                                           body_event_index=e if outer_event is not None else None,
                                           request_inputs=request_inputs)
                        found = self._step_diagnostics
                    visit(next_state, next_locals, done | {(e, o)},
                          {**records, (e, o): rec}, [*diagnostics, *found])
                except PendingValue:
                    self._failed_diagnostics.extend([*diagnostics, *self._step_diagnostics])
                if not uncertain:
                    break
        visit(state, locals_, set(), {}, [])
        return outcomes

    @staticmethod
    def _merge_operations(variants):
        data = variants[0].model_dump(mode="python")
        if data["op"] == "build":
            merged_inputs, merged_members = [], []
            for index, member in enumerate(variants[0].members):
                row = {"path": member.path, "when_input_index": None, "value_input_index": None}
                for field in ("when_input_index", "value_input_index"):
                    values = [variant.inputs[slot] for variant in variants
                              for slot in [getattr(variant.members[index], field)] if slot is not None]
                    if values:
                        row[field] = len(merged_inputs)
                        merged_inputs.append(frozenset().union(*values))
                merged_members.append(row)
            data["inputs"], data["members"] = merged_inputs, merged_members
        elif any(variant.when_input_index is not None for variant in variants):
            payload_count = max(len(v.inputs) - 1 for v in variants)
            data["inputs"] = [frozenset().union(*(v.inputs[index] for v in variants if index < len(v.inputs) - 1))
                              for index in range(payload_count)]
            data["when_input_index"] = payload_count
            data["inputs"].append(frozenset().union(*(v.inputs[v.when_input_index] for v in variants)))
        else:
            data["inputs"] = [frozenset().union(*(v.inputs[index] for v in variants))
                              for index in range(len(data["inputs"]))]
        for side in ("outputs",):
            data[side] = [frozenset().union(*(getattr(v, side)[i] for v in variants))
                          for i in range(len(data[side]))]
        for i, change in enumerate(data["changes"]):
            for side in ("before", "after"):
                change[side] = frozenset().union(*(getattr(v.changes[i], side) for v in variants))
        return AtomicOpRecord.model_validate(data)

    def evaluate(self, ir, typed_spec, entry_state):
        self._last_diagnostics = []
        self._failed_diagnostics = []
        self._attempts = 0
        spec = plain(typed_spec)
        self._current_spec = typed_spec
        from skillflow.propagation.contracts.uses import request_pairs
        self._request_pairs = request_pairs(typed_spec)
        self._entry_instruction = ir["id"]
        self._entry_state = mapping(entry_state)
        self._entry_inputs = {}
        uncertain = typed_spec.order == "partial"
        outcomes = []
        try:
            arrangements = self._arrangements(ir, typed_spec.events, mapping(entry_state), {}, uncertain=uncertain)
            for state, locals_, records, diagnostics in arrangements:
                try:
                    self.bind_outputs(ir, spec, state, locals_)
                except PendingValue:
                    self._failed_diagnostics.extend(diagnostics)
                else:
                    outcomes.append((state, records, diagnostics))
        finally:
            findings = ([item for outcome in outcomes for item in outcome[2]]
                        if outcomes else self._failed_diagnostics)
            unique = {json.dumps(item, ensure_ascii=True, sort_keys=True): item for item in findings}
            self._last_diagnostics = [unique[key] for key in sorted(unique)]
        if not outcomes:
            raise PendingValue(f"{ir['id']}: references cannot be resolved in any supported ordering")
        result_events = []
        for e, event in enumerate(typed_spec.events):
            if getattr(event, "kind", None) == "for_each":
                unique = {canonical_sha256(instance.model_dump(mode="json")): instance
                          for outcome in outcomes for instance in outcome[1][(e, -1)].instances}
                collections = frozenset().union(*(outcome[1][(e, -1)].collections for outcome in outcomes))
                result_events.append(ForEachRecord(kind="for_each", collections=collections,
                                                  instances=[unique[key] for key in sorted(unique)]))
            else:
                records = [self._merge_operations([out[1][(e, o)] for out in outcomes])
                           for o in range(len(event.atomic_ops))]
                result_events.append(self._effect_record(ir, event, records))
        return IRFlowRecord(order=typed_spec.order, precedence=typed_spec.precedence, entry_state=entry_state,
                            exit_state=FlowState.from_mapping(join_states(out[0] for out in outcomes)),
                            events=result_events)
