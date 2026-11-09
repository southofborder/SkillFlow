"""Deterministic abstract operations, never execution of Skill code or opcodes."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
import json

from skillflow.propagation.data import DataPart
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import DataConflictError
from skillflow.propagation.data import Dependency
from skillflow.propagation.data import FieldUpdatesContent
from skillflow.propagation.data import KnownPartsContent
from skillflow.propagation.data import LiteralContent
from skillflow.propagation.data import OpaqueContent
from skillflow.propagation.data import Origin
from skillflow.propagation.data import WholeExceptContent
from skillflow.propagation.data import SubsetViewContent
from skillflow.propagation.data import MappedCollectionContent, MappedMember
from skillflow.propagation.data import SelectionContent, AccumulatedCollectionContent, LoopSummaryContent
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
from skillflow.propagation.models import OperationAlternative
from skillflow.propagation.contracts.specs import IRSemantics
from skillflow.propagation.contracts.specs import value_refs
from skillflow.propagation.contracts.specs import iter_effect_events
from skillflow.propagation.contracts.specs import iter_scoped_events
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.contracts.uses import active_value_uses

class PendingValue(ValueError):
    """No current candidate, not an unknown external source or an empty value."""


class UnsupportedLoopDomain(PendingValue):
    """A typed loop operand cannot be represented; only this path is cut."""


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
    def __init__(self, cfg, annotation, registry: DataRegistry, *, max_variants=100000, typed_specs=None):
        self.cfg = cfg
        self.annotation = annotation
        self.registry = registry
        self.max_variants = max_variants
        self.compatible_candidates = 0
        self._last_diagnostics = []
        self._step_diagnostics = []
        self._request_pairs = {}
        self.predecessor_states = {}
        self.current_block = None
        self.active_predecessor = None
        self.loop_backedge_available = False
        # The solver supplies its already validated specifications. Direct
        # interpreter callers cross this boundary once, never once per value.
        self.specs = (dict(typed_specs) if typed_specs is not None else {
            identity: spec if isinstance(spec, IRSemantics) else IRSemantics.model_validate(spec)
            for identity, spec in annotation["ir_semantics"].items()
        })
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

    def prepare_member_metadata(self):
        """Prepare the finite member inventory before descriptor reads begin.

        Region/dominator metadata is assigned by the solver first. Operations
        never change this inventory during a worklist pass, so a new member
        fact cannot silently introduce a previously unobserved control source.
        """
        registry = self.registry
        if not hasattr(registry, "member_sources"):
            return
        scopes, sources = {}, {}
        for block in self.cfg["blocks"].values():
            for ir in block["instructions"]:
                spec = self.specs.get(ir["id"])
                if spec is None:
                    continue
                for event_index, _, event in iter_scoped_events(spec):
                    for op_index, operation in enumerate(event.atomic_ops):
                        if operation.op != "member":
                            continue
                        scope = static_key(self.rule_identity, ir["id"], event_index, op_index, "member")
                        scopes[scope] = registry.regions.get(ir["id"], ir["id"])
                        sources[scope] = {"ir": ir["id"], "local": operation.output, "results": [
                            ir["outputs"][binding.output_index]["identifier"] for binding in spec.output_bindings
                            if plain(binding.value) == {"kind": "local", "name": operation.output}]}
        registry.member_scopes = scopes
        registry.member_sources = sources

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
        from skillflow.propagation.contracts.limitations import unmodeled_ids
        unmodeled = unmodeled_ids(self.annotation)
        for block in self.cfg["blocks"].values():
            for ir in block["instructions"]:
                if ir["id"] in unmodeled:
                    continue
                typed_spec = self.specs[ir["id"]]
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
                        for use in active_value_uses(operation, ir):
                            locations.update(self.referenced_context_locations(ir, use.value))
                for binding in typed_spec.output_bindings:
                    locations.update(self.referenced_context_locations(ir, binding.value))
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
                ids = self._use_aliases(ids, ir, self._entry_state, locals_, [ir["id"], "input-use", index])
            self._entry_inputs[index] = ids
        return self._entry_inputs[index]

    def _use_aliases(self, identities, ir, state, locals_, position):
        """A stored value keeps its creation provenance in a current-use view.

        Creation member A does not prohibit using the same handle in member B.
        This view is not a new acquisition, copy of credentials, or cache model.
        """
        if not hasattr(self.registry, "facts"):
            return identities
        contexts = self._ambient_bindings(ir, state, locals_)
        values = set()
        for identity in identities:
            creation = self.registry.bindings(identity)
            if not creation:
                values.add(identity)
                continue
            for context in contexts:
                carried = self.registry.carried_bindings(identity)
                for key, value in context.items():
                    if key in carried and carried[key] != value:
                        carried["unresolved:" + key.removeprefix("incoming:")] = "multiple_generations"
                    else:
                        carried[key] = value
                values.add(self._result([position, "stored-use"], [identity], SelectionContent(base=identity, path=[]), bindings=carried))
        return frozenset(values)

    def _tuples(self, inputs):
        """Join compatible candidates before applying the relation budget.

        The slot order and repeated references remain intact. A raw Cartesian
        product is neither materialized nor charged before member/predecessor
        constraints remove impossible combinations.
        """
        groups = [frozenset(ids) for ids in inputs]
        if any(not group for group in groups):
            return iter(())
        identities = set().union(*groups) if groups else set()
        bindings = {identity: dict(self.registry.bindings(identity))
                    if hasattr(self.registry, "bindings") else {} for identity in identities}
        indexes = []
        for group in groups:
            axes = {}
            for identity in group:
                for axis, selector in bindings[identity].items():
                    axes.setdefault(axis, {}).setdefault(selector, set()).add(identity)
            indexes.append({axis: (group - set().union(*choices.values()), choices)
                            for axis, choices in axes.items()})
        order = sorted(range(len(groups)), key=lambda index: (len(groups[index]), index))
        selected, results = [None] * len(groups), []

        def compatible(index, context):
            allowed = groups[index]
            for axis, selector in context.items():
                if axis in indexes[index]:
                    unbound, choices = indexes[index][axis]
                    allowed = allowed & (unbound | choices.get(selector, set()))
                    if not allowed:
                        break
            return allowed

        def visit(depth, context):
            if depth == len(order):
                args = tuple(selected)
                choices = {identity: bindings[identity] for identity in args}
                for identity, bound in choices.items():
                    for axis in (key.removeprefix("unresolved:") for key in bound if key.startswith("unresolved:")):
                        # Check only complete compatible tuples: an impossible
                        # later operand must not turn a discarded prefix into
                        # a spurious unsupported-correlation diagnostic.
                        if any(other != identity and ("incoming:" + axis in values or "unresolved:" + axis in values)
                               for other, values in choices.items()):
                            raise UnsupportedLoopDomain("Unresolved carried-value correlation across multiple generations; no input tuple was guessed")
                results.append(args)
                self.compatible_candidates += 1
                if len(results) > self.max_variants:
                    raise PropagationLimitError(f"compatible candidate relation exceeds {self.max_variants}")
                return
            index = order[depth]
            for identity in sorted(compatible(index, context)):
                combined = {**context, **bindings[identity]}
                if all(compatible(later, combined) for later in order[depth + 1:]):
                    selected[index] = identity
                    visit(depth + 1, combined)

        visit(0, {})
        return iter(sorted(results))

    def _ambient_bindings(self, ir, state, locals_):
        """Control occurrence is not a request argument or plaintext source."""
        if not hasattr(self.registry, "member_sources"):
            return [{}]
        registry = self.registry
        contexts = [{}]
        current = self.current_block
        for scope, source in sorted(registry.member_sources.items()):
            owner = registry.member_scopes.get(scope)
            if owner in registry.region_blocks and current not in registry.region_blocks[owner]:
                continue
            source_block = registry.ir_blocks.get(source["ir"])
            if source_block not in registry.dominators.get(current, {current}):
                continue
            if source["ir"] == ir["id"]:
                values = locals_.get(source["local"], frozenset())
            else:
                if source_block == current and registry.ir_orders[source["ir"]] >= registry.ir_orders[ir["id"]]:
                    continue
                values = frozenset().union(*(state.get(FlowLocation(kind="result", name=name), frozenset()) for name in source["results"]))
            if not values:
                continue
            candidates = []
            for context in contexts:
                for identity in sorted(values):
                    binding = registry.bindings(identity)
                    if all(key not in context or context[key] == value for key, value in binding.items()):
                        candidates.append({**context, **binding})
            unique = {canonical_sha256(value): value for value in candidates}
            contexts = [unique[key] for key in sorted(unique)]
            if len(contexts) > self.max_variants:
                raise PropagationLimitError("member control contexts exceed configured resource budget")
        return contexts

    def _contexts_for(self, args, ambient):
        bindings = self.registry.combine_bindings(args) if hasattr(self.registry, "combine_bindings") else {}
        if bindings is None:
            return []
        return [{**context, **bindings} for context in ambient
                if all(key not in context or context[key] == value for key, value in bindings.items())]

    def _result(self, position, inputs, content, *, relations=None, acquired_from=None, bindings=None):
        if hasattr(self.registry, "facts") and isinstance(position, list) and len(position) == 4 and position[2] == "collect":
            # Collection candidates are equation inputs, never dynamic sites.
            position = position[:3]
        relations = relations if relations is not None else ["derived"] * len(inputs)
        deps = []
        for data_id, relation in zip(inputs, relations):
            if not any(d.data == data_id and d.relation == relation for d in deps):
                deps.append(Dependency(data=data_id, relation=relation))
        origin = Origin(at=str(position), acquired_from=acquired_from, inputs=list(inputs), dependencies=deps)
        if hasattr(self.registry, "scope_for"):
            scope = self.registry.scope_for(position, inputs)
            if scope is not None or bindings:
                return self.registry.family(scope or "correlated:" + str(self.current_block),
                    position, inputs, content, origin, bindings=bindings).id
        return self.registry.create_result(
            static_key(self.rule_identity, position, list(inputs)), content=content,
            origin=origin,
        ).id

    def _require_collection_operand(self, identity, seen=frozenset()):
        """Reject known noncollections without demanding a known member set.

        This is filter semantics formerly checked by the whole registry audit.
        Query only the selected descriptor and its structural bases; opaque or
        recursive summaries remain unknown, not an empty or invalid collection.
        """
        if identity in seen:
            return
        from skillflow.propagation.data.summary import content_options
        values = content_options(self.registry, identity, seen)
        for content in values:
            form = content["form"]
            invalid = ((form == "literal" and type(content["value"]) is not list)
                or (form == "known_parts" and any(type(part["path"][0]) is str for part in content["parts"]))
                or (form == "field_updates" and any(type(part["path"][0]) is str for part in content["updates"])))
            if invalid:
                raise DataConflictError("subset_view requires a collection, not a known object or scalar")
            if form in {"whole_except", "subset_view", "field_updates"}:
                self._require_collection_operand(content["base"], seen | {identity})

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

    def execute(self, ir, event_index, op_index, operation, state, locals_, *, uncertain=False, body_event_index=None, request_inputs=None, member_token=None):
        self._step_diagnostics = []
        op = plain(operation)
        pos = ([ir["id"], event_index, op_index] if body_event_index is None
               else [ir["id"], event_index, "body", body_event_index, op_index])
        if member_token is not None:
            pos = [*pos, "member", member_token]
        kind = op["op"]
        ambient = self._ambient_bindings(ir, state, locals_)
        if hasattr(self.registry, "current_position"):
            self.registry.current_position = pos
        members, when_input_index, build_variants = None, None, None
        if kind == "merge":
            inputs = []
            saved_entry, saved_inputs = self._entry_state, self._entry_inputs
            for item in op["incoming"]:
                incoming = (self.predecessor_states.get(item["predecessor"])
                            if self.active_predecessor is None or self.active_predecessor == item["predecessor"] else None)
                if incoming is None:
                    inputs.append(frozenset())
                    continue
                self._entry_state, self._entry_inputs = incoming, {}
                inputs.append(self.resolve(item["value"], ir, incoming, locals_, [pos, item["predecessor"]]))
            self._entry_state, self._entry_inputs = saved_entry, saved_inputs
        elif kind == "build":
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
        if kind != "merge" and any(not ids for ids in inputs):
            raise PendingValue(f"{pos}: input has no available data candidates")
        outputs = set()
        output_inputs = {}

        def add_output(identity, selected_inputs):
            outputs.add(identity)
            output_inputs.setdefault(identity, set()).add(tuple(sorted(selected_inputs.items())))

        endpoints, changes, alternatives, branch_targets = [], [], [], []
        if kind == "merge":
            for index, values in enumerate(inputs):
                for identity in sorted(values):
                    carried = (hasattr(self.registry, "aggregate_bindings")
                               and self.registry.regions.get(ir["id"]) == self.current_block)
                    bindings = (self.registry.carried_bindings(identity, region=self.current_block) if carried
                                else dict(self.registry.bindings(identity)) if hasattr(self.registry, "bindings") else {})
                    bindings["predecessor:" + str(self.current_block)] = op["incoming"][index]["predecessor"]
                    value = self._result([pos, "carried-use"] if carried else pos,
                                         [identity], SelectionContent(base=identity, path=[]), bindings=bindings)
                    outputs.add(value)
                    slots = [frozenset([identity]) if i == index else frozenset() for i in range(len(inputs))]
                    alternatives.append(OperationAlternative(inputs=slots, outputs=[frozenset([value])], bindings=bindings))
        elif kind == "member":
            scope = static_key(self.rule_identity, ir["id"], event_index, op_index, "member")
            for collection in sorted(inputs[0]):
                try:
                    entries = self.registry.resolve_iteration_entries(collection, scope)
                except DataReferenceError as error:
                    raise UnsupportedLoopDomain("Unsupported collection domain: " + str(error)) from error
                for entry in entries:
                    selector = plain(entry.selector)
                    source_key = (self.registry.family_producer(collection)
                                  if hasattr(self.registry, "family_producer") else collection)
                    for context in self._contexts_for([collection], ambient):
                        bindings = {**context, scope: static_key(source_key, selector)}
                        value = self._result(pos, [entry.element.id], SelectionContent(base=collection, path=[entry.selector]), bindings=bindings)
                        outputs.add(value)
                        alternatives.append(OperationAlternative(inputs=[frozenset([collection])], outputs=[frozenset([value])], bindings=bindings))
        elif kind == "branch":
            from skillflow.propagation.loop_guards import guard_values
            valid, invalid = set(), []
            for identity in sorted(inputs[0]):
                try:
                    truths = guard_values(self.registry, [identity], op["predicate"],
                                          traversal_exit=self.loop_backedge_available)
                except ValueError as error:
                    invalid.append(str(error))
                    continue
                targets = sorted({op["true_target"] if truth else op["false_target"] for truth in truths})
                for bindings in self._contexts_for([identity], ambient):
                    valid.add(identity)
                    alternatives.append(OperationAlternative(inputs=[frozenset([identity])], bindings=bindings, branch_targets=targets))
            if not valid:
                raise UnsupportedLoopDomain("Unsupported typed guard domain: " + "; ".join(sorted(set(invalid))))
            if invalid:
                self._step_diagnostics.append({"code": "unresolved_path", "instruction_id": ir["id"],
                    "reason": "Unsupported typed guard candidates were not routed: " + "; ".join(sorted(set(invalid)))})
            inputs = [frozenset(valid)]
            branch_targets = sorted({target for candidate in alternatives for target in candidate.branch_targets})
        elif kind == "append":
            for args in self._tuples(inputs):
                aggregate = self.registry.aggregate_bindings(pos, args) if hasattr(self.registry, "aggregate_bindings") else None
                value = self._result(pos, args, AccumulatedCollectionContent(base=args[0], added=args[1], mode=op["mode"]), bindings=aggregate)
                outputs.add(value)
                bindings = self.registry.combine_bindings(args) if hasattr(self.registry, "combine_bindings") else {}
                alternatives.append(OperationAlternative(inputs=[frozenset([a]) for a in args], outputs=[frozenset([value])], bindings=bindings))
        elif kind == "read":
            location = self.locations[op["location"]]
            endpoints.append(location)
            outputs.update(self._use_aliases(self.read_location(location, state), ir, state, locals_, [pos, "read-use"]))
        elif kind == "receive":
            location = self.locations[op["location"]]
            endpoints.append(location)
            for args in self._tuples(inputs):
                for context in self._contexts_for(args, ambient):
                    add_output(self._result(pos, args, OpaqueContent(), relations=["possible"] * len(args),
                        acquired_from=f"{location.kind}:{location.name}", bindings=context), dict(enumerate(args)))
        elif kind == "deliver":
            endpoints.append(self.locations[op["target"]])
        elif kind == "write":
            location = self.locations[op["target"]]
            endpoints.append(location)
            targets = self.aliases(location)
            for target in targets:
                before = state.get(target, frozenset())
                weak = op.get("may", False) or uncertain or target != location or location.name.startswith("symbolic:")
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
                    candidates = (self.registry.project(base, op["path"], pos)
                                  if hasattr(self.registry, "project") else self.registry.resolve_part_candidates(base, op["path"]))
                    for value in candidates:
                        add_output(value.id, {0: base})
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
                self._require_collection_operand(args[0])
                add_output(self._result(pos, args, SubsetViewContent(base=args[0], predicate=op["predicate"])), dict(enumerate(args)))
        elif kind == "exclude_parts":
            for args in self._tuples(inputs):
                add_output(self._result(pos, args, WholeExceptContent(base=args[0], excluded_parts=op["paths"])), dict(enumerate(args)))
        elif kind == "update_fields":
            for args in self._tuples(inputs):
                updates = [DataPart(path=item["path"], data=data_id)
                           for item, data_id in zip(op["updates"], args[1:])]
                add_output(self._result(pos, args, FieldUpdatesContent(base=args[0], updates=updates)), dict(enumerate(args)))
        elif kind == "build":
            for args, content, shape in build_variants:
                selected, cursor = {}, 0
                for index, member in enumerate(members):
                    if member.when_input_index is not None:
                        selected[member.when_input_index] = args[cursor]
                        cursor += 1
                    if op["parts"][index]["path"] in shape:
                        selected[member.value_input_index] = args[cursor]
                        cursor += 1
                add_output(self._result([pos, "members", shape], args, content), selected)
        elif kind == "compute":
            for args in self._tuples(inputs):
                add_output(self._result(pos, args, OpaqueContent(), relations=op["dependencies"]), dict(enumerate(args)))
        else:
            raise ValueError(f"unsupported abstract operation: {kind}")
        resolved_outputs = []
        if "output" in op:
            if not outputs:
                raise PendingValue(f"{pos}: output has no candidates (not an opaque source)")
            locals_[op["output"]] = frozenset(outputs)
            resolved_outputs = [frozenset(outputs)]
        if not alternatives and kind != "branch":
            for args in self._tuples(inputs):
                for bindings in self._contexts_for(args, ambient):
                    paired = frozenset(identity for identity in outputs
                        if (identity not in output_inputs or any(
                            all(args[index] == value for index, value in relation)
                            for relation in output_inputs[identity]))
                        and (not hasattr(self.registry, "bindings") or all(
                            key not in bindings or bindings[key] == value
                            for key, value in self.registry.bindings(identity).items())))
                    alternatives.append(OperationAlternative(inputs=[frozenset([item]) for item in args],
                        outputs=[paired] if "output" in op else [], bindings=bindings))
        if hasattr(self.registry, "facts") and kind != "branch" and not alternatives:
            raise PendingValue(f"{pos}: no compatible loop occurrence supplies this operation")
        return AtomicOpRecord(op=kind, inputs=inputs, outputs=resolved_outputs,
                              endpoints=endpoints, changes=changes,
                              members=members, when_input_index=when_input_index, may_state=op.get("may", False),
                              alternatives=alternatives, branch_targets=branch_targets)

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
        return EffectEvent(effect=event.effect, atomic_ops=operations, case=event.case,
                           requires_completion=event.requires_completion)

    def _for_each(self, ir, event_index, event, state, locals_, *, uncertain):
        collections = self.resolve(event.collection, ir, state, locals_,
                                   [ir["id"], event_index, "collection"])
        if not collections:
            raise PendingValue(f"{ir['id']}/{event_index}: collection has no available candidates")
        instances, diagnostics, output_ids, state_candidates = [], [], set(), []
        scope = static_key(self.rule_identity, ir["id"], event_index, "element")
        for collection in sorted(collections):
            members = {}
            # Unknown collections have one scoped representative. Known finite
            # lists retain each real member; an explicit empty list has none.
            entries = self.registry.resolve_iteration_entries(collection, scope)
            repeated = len({entry.element.id for entry in entries}) != len(entries)
            for entry in entries:
                element = entry.element
                scoped_locals = {**locals_, event.item: frozenset([element.id])}
                selector = (entry.selector.model_dump(mode="json")
                            if hasattr(entry.selector, "model_dump") else entry.selector)
                collection_site = (self.registry.family_producer(collection)
                    if hasattr(self.registry, "family_producer") else collection)
                member_token = static_key(scope, collection_site, selector)
                outcomes = self._arrangements(ir, event.body, dict(state), scoped_locals,
                                              uncertain=uncertain, outer_event=event_index,
                                              member_token=member_token)
                if not outcomes:
                    raise PendingValue(f"{ir['id']}/{event_index}: member scope cannot resolve its body")
                for final_state, final_locals, records, found in outcomes:
                    if final_state != state:
                        writes = [op for op in records.values() if op.op == "write"]
                        if any(not op.may_state for op in writes):
                            raise ValueError("for_each body must not update shared state outside a may summary")
                        state_candidates.append(final_state)
                    body = [self._effect_record(ir, body_event,
                            [records[(b, o)] for o in range(len(body_event.atomic_ops))])
                            for b, body_event in enumerate(event.body)]
                    yielded = frozenset()
                    if event.yield_value is not None:
                        yielded = self.resolve(event.yield_value, ir, final_state, final_locals,
                                               [ir["id"], event_index, "yield", member_token])
                        if not yielded:
                            raise PendingValue("for_each yield has no available member candidates")
                        identity = (entry.selector, element.id)
                        members.setdefault(identity, set()).update(yielded)
                    instances.append(ForEachInstance(collection=collection, element=element.id, body=body,
                        **({"selector": entry.selector} if event.output is not None or repeated else {}),
                        **({"yielded": yielded} if event.output is not None else {})))
                    diagnostics.extend(found)
            if event.output is not None:
                content = MappedCollectionContent(base=collection, scope=scope, members=[
                    MappedMember(selector=selector, element=element, values=sorted(values))
                    for (selector, element), values in members.items()])
                # The source collection controls membership, not copied payload.
                yielded_ids = sorted({value for member in content.members for value in member.values})
                output_ids.add(self._result([ir["id"], event_index, "collect", collection], yielded_ids, content))
        if event.output is not None:
            locals_[event.output] = frozenset(output_ids)
        # Join possible local effects only after the scope. Members do not read
        # a previous member's abstract post-state, and empty scopes have none.
        if state_candidates:
            state.update(join_states([dict(state), *state_candidates]))
        # Keep each complete scoped arrangement. Unioning each argument across
        # members would fabricate cross-member recipient/payload combinations.
        unique = {canonical_sha256(item.model_dump(mode="json")): item for item in instances}
        return ForEachRecord(kind="for_each", collections=collections,
                             instances=[unique[key] for key in sorted(unique)], outputs=frozenset(output_ids),
                             completion_groups=event.completion_groups,
                             requires_completion=event.requires_completion), diagnostics

    def _arrangements(self, ir, events, state, locals_, *, uncertain, outer_event=None, member_token=None):
        from skillflow.propagation.contracts.specs import schedule_dependencies
        dependencies = schedule_dependencies(self._current_spec, outer_event=outer_event)
        atoms = [(e, -1, event) if getattr(event, "kind", None) == "for_each" else (e, o, op)
                 for e, event in enumerate(events)
                 for o, op in ([(-1, event)] if getattr(event, "kind", None) == "for_each"
                               else enumerate(event.atomic_ops) if event.atomic_ops else [(-2, event)])]
        outcomes = []
        group_atoms, returning_cases = {}, {}
        for e, o, _ in atoms:
            case = getattr(events[e], "case", None)
            if case is not None:
                group_atoms.setdefault(case.group, set()).add((e, o))
                if case.disposition == "return":
                    returning_cases.setdefault(case.group, set()).add(case.id)

        def visit(current, local_values, done, records, diagnostics, case_bases, case_states):
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
                bases, branch_states = dict(case_bases), dict(case_states)
                case = getattr(events[e], "case", None)
                if case is not None:
                    bases.setdefault(case.group, dict(current))
                    next_state = dict(branch_states.get(case.id, bases[case.group]))
                try:
                    if o == -2:
                        rec, found = None, []
                    elif o == -1:
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
                                            request_inputs=request_inputs, member_token=member_token)
                        found = self._step_diagnostics
                    if case is not None:
                        branch_states[case.id] = dict(next_state)
                        next_state = join_states([current, next_state])
                        if group_atoms[case.group] <= done | {(e, o)}:
                            # Retain failure-prefix records, but never publish
                            # thrown-only changes as a normal continuation.
                            next_state = join_states(branch_states[identity]
                                for identity in sorted(returning_cases[case.group]))
                    visit(next_state, next_locals, done | {(e, o)},
                          {**records, (e, o): rec}, [*diagnostics, *found], bases, branch_states)
                except PendingValue as error:
                    if isinstance(error, UnsupportedLoopDomain):
                        self._unsupported_loop = error
                    self._failed_diagnostics.extend([*diagnostics, *self._step_diagnostics])
                if not uncertain:
                    break
        visit(state, locals_, set(), {}, [], {}, {})
        return outcomes

    @staticmethod
    def _merge_operations(variants):
        if len(variants) == 1:
            return variants[0]
        data = variants[0].model_dump(mode="python")
        data["branch_targets"] = sorted({target for item in variants for target in item.branch_targets})
        alternatives = {canonical_sha256(item.model_dump(mode="json")): item
                        for variant in variants for item in variant.alternatives}
        data["alternatives"] = [alternatives[item] for item in sorted(alternatives)]
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
        self._unsupported_loop = None
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
            if self._unsupported_loop is not None:
                raise self._unsupported_loop
            raise PendingValue(f"{ir['id']}: references cannot be resolved in any supported ordering")
        result_events = []
        for e, event in enumerate(typed_spec.events):
            if getattr(event, "kind", None) == "for_each":
                unique = {canonical_sha256(instance.model_dump(mode="json")): instance
                          for outcome in outcomes for instance in outcome[1][(e, -1)].instances}
                collections = frozenset().union(*(outcome[1][(e, -1)].collections for outcome in outcomes))
                result_events.append(ForEachRecord(kind="for_each", collections=collections,
                                                  instances=[unique[key] for key in sorted(unique)],
                    completion_groups=event.completion_groups, requires_completion=event.requires_completion,
                    outputs=frozenset().union(*(outcome[1][(e, -1)].outputs for outcome in outcomes))))
            else:
                records = [self._merge_operations([out[1][(e, o)] for out in outcomes])
                           for o in range(len(event.atomic_ops))]
                result_events.append(self._effect_record(ir, event, records))
        return IRFlowRecord(order=typed_spec.order, precedence=typed_spec.precedence, entry_state=entry_state,
                            exit_state=FlowState.from_mapping(join_states(out[0] for out in outcomes)),
                            events=result_events)
