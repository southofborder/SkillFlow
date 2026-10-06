"""Deterministic abstract operations, never execution of Skill code or opcodes."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
import json

from pydantic import TypeAdapter

from skill_ir.data import (
    DataPart, DataRegistry, Dependency, FieldUpdatesContent, KnownPartsContent,
    LiteralContent, OpaqueContent, Origin, WholeExceptContent,
)
from skill_ir.data.registry import DataReferenceError
from skill_ir.recording import canonical_sha256
from .models import (
    AtomicOpRecord, EffectEvent, FlowLocation, FlowState, IRFlowRecord,
    StateChange,
)
from .specs import AtomicOp, value_refs

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
                for event in spec["events"]:
                    for op in event["atomic_ops"]:
                        if op["op"] == "read":
                            locations.add(self.locations[op["location"]])
                        elif op["op"] == "write" and op["mode"] == "append":
                            locations.add(self.locations[op["target"]])
                        for ref in value_refs(_ATOMIC_SPEC.validate_python(op)):
                            locations.update(self.referenced_context_locations(ir, ref))
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
        operand = ir.get("inputs", [])[ref["index"]]
        if operand["type"] == "literal":
            return frozenset([self.literal(operand.get("literal_value"), [ir["id"], "input", ref["index"]])])
        if operand["type"] == "result":
            return state.get(FlowLocation(kind="result", name=operand["identifier"]), frozenset())
        if operand["type"] == "external_resource":
            raise ValueError("resource identity is not a data payload; use an evidenced literal or read")
        locations = self.context_locations(ir, ref["index"])
        return frozenset().union(*(self.read_location(loc, state) for loc in locations))

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

    def execute(self, ir, event_index, op_index, operation, state, locals_, *, uncertain=False):
        self._step_diagnostics = []
        op = plain(operation)
        pos = [ir["id"], event_index, op_index]
        refs = [plain(r) for r in value_refs(operation)]
        inputs = [self.resolve(r, ir, state, locals_, [pos, "input", i]) for i, r in enumerate(refs)]
        if any(not ids for ids in inputs):
            raise PendingValue(f"{pos}: input has no available data candidates")
        outputs = set()
        endpoints, changes = [], []
        kind = op["op"]
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
        elif kind == "exclude_parts":
            for args in self._tuples(inputs):
                outputs.add(self._result(pos, args, WholeExceptContent(base=args[0], excluded_parts=op["paths"])))
        elif kind == "update_fields":
            for args in self._tuples(inputs):
                updates = [DataPart(path=item["path"], data=data_id)
                           for item, data_id in zip(op["updates"], args[1:])]
                outputs.add(self._result(pos, args, FieldUpdatesContent(base=args[0], updates=updates)))
        elif kind == "build":
            for args in self._tuples(inputs):
                content = (KnownPartsContent(parts=[DataPart(path=item["path"], data=value)
                                                   for item, value in zip(op["parts"], args)], parts_complete=True)
                           if args else LiteralContent(value=[] if op["container"] == "list" else {}))
                outputs.add(self._result(pos, args, content))
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
                              endpoints=endpoints, changes=changes)

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

    def evaluate(self, ir, typed_spec, entry_state):
        self._last_diagnostics = []
        spec = plain(typed_spec)
        events = typed_spec.events
        effects = self.annotation["profiles"][ir["id"]]["effects"]
        uncertain = any(u["instruction_id"] == ir["id"] and u["field"] == "effects"
                        for u in self.annotation["unresolved"])
        atoms = [(e, o, op) for e, event in enumerate(events) for o, op in enumerate(event.atomic_ops)]
        outcomes = []
        failed_diagnostics = []
        attempts = 0

        def visit(state, locals_, done, records, diagnostics):
            nonlocal attempts
            attempts += 1
            if attempts > self.max_variants:
                raise PropagationLimitError("uncertain-order arrangements exceed configured resource limit")
            if len(done) == len(atoms):
                self.bind_outputs(ir, spec, state, locals_)
                outcomes.append((state, records, diagnostics))
                return
            for e, o, op in atoms:
                if (e, o) in done or (o and (e, o - 1) not in done):
                    continue
                if not uncertain and len(done) != atoms.index((e, o, op)):
                    continue
                next_state, next_locals = dict(state), dict(locals_)
                try:
                    rec = self.execute(ir, e, o, op, next_state, next_locals, uncertain=uncertain)
                except PendingValue:
                    failed_diagnostics.extend([*diagnostics, *self._step_diagnostics])
                else:
                    step_diagnostics = [*diagnostics, *self._step_diagnostics]
                    try:
                        visit(next_state, next_locals, done | {(e, o)},
                              {**records, (e, o): rec}, step_diagnostics)
                    except PendingValue:
                        failed_diagnostics.extend(step_diagnostics)
                if not uncertain:
                    break
            if not outcomes and not any((e, o) not in done and (o == 0 or (e, o - 1) in done)
                                         for e, o, _ in atoms):
                raise PendingValue(f"{ir['id']}: no ready operation")

        try:
            visit(mapping(entry_state), {}, set(), {}, [])
        finally:
            findings = ([item for outcome in outcomes for item in outcome[2]]
                        if outcomes else failed_diagnostics)
            unique = {json.dumps(item, ensure_ascii=True, sort_keys=True): item for item in findings}
            self._last_diagnostics = [unique[key] for key in sorted(unique)]
        if not outcomes:
            raise PendingValue(f"{ir['id']}: references cannot be resolved in any supported ordering")
        result_events = []
        for e, event in enumerate(events):
            records = []
            for o, _ in enumerate(event.atomic_ops):
                variants = [out[1][(e, o)] for out in outcomes]
                data = variants[0].model_dump(mode="python")
                for side in ("inputs", "outputs"):
                    data[side] = [frozenset().union(*(getattr(v, side)[i] for v in variants))
                                  for i in range(len(data[side]))]
                for i, change in enumerate(data["changes"]):
                    for side in ("before", "after"):
                        change[side] = frozenset().union(*(getattr(v.changes[i], side) for v in variants))
                records.append(AtomicOpRecord.model_validate(data))
            index = event.effect_index
            result_events.append(EffectEvent(effect=None if index is None else effects[index],
                                             atomic_ops=records))
        return IRFlowRecord(entry_state=entry_state,
                            exit_state=FlowState.from_mapping(join_states(out[0] for out in outcomes)),
                            events=result_events)
