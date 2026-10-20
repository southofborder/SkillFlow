"""Finite forward constraint checks over immutable, already indexed DOE facts.

This module does not seed demands, change Data, execute a reduced Skill, or
interpret source prose. A reported violation is a static possibility, never
an execution observation. Structural guarantees deliberately ignore values.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from skillflow.propagation.conditions import payload_input_indices
from skillflow.propagation.contracts.references import target_key
from .constraint_control import BooleanFacts, ConstraintCapability, ConstraintLimit, collection_size
from .constraint_ranges import ContentRanges, range_presence


class _Limit(ConstraintLimit):
    pass


def _template(info):
    position = info["position"]
    return position["event_index"], position.get("body_event_index"), position["op_index"]


class ConstraintEngine:
    def __init__(self, engine, *, max_states=20000):
        self.engine, self.max_states = engine, max_states
        self.cfg, self.data = engine.facts.cfg, engine.index.data
        self.booleans = BooleanFacts(engine, max_options=max_states)
        self.constraints = {}
        self.incomplete_scope = set()
        self._checks = None
        from skillflow.propagation.contracts.constraints import constraint_mapping
        mapping = constraint_mapping(engine.raw, engine.compiled["task_ref"])
        by_pointer = {row["raw_pointer"]: row for row in mapping}
        for index, realization in enumerate(engine.compiled["realizations"]):
            for number, constraint in enumerate(realization.get("constraints", [])):
                pointer = f"/realizations/{index}/constraints/{number}"
                identity = by_pointer[pointer]["constraint_id"]
                self.constraints[identity] = {**deepcopy(constraint),
                    "requirement_id": realization["requirement_id"], "raw_pointer": pointer}
        self.by_ir = defaultdict(list)
        for key, info in engine.ops.items():
            self.by_ir[info["position"]["instruction_id"]].append(key)
        self.edges = defaultdict(list)
        for number, edge in enumerate(self.cfg["edges"]):
            self.edges[edge["source_block_id"]].append((number, edge))
        self._reachable = set()
        pending = [self.cfg["entry_block_id"]]
        while pending:
            block = pending.pop()
            if block not in self._reachable:
                self._reachable.add(block)
                pending.extend(edge["target_block_id"] for _, edge in self.edges[block])

    def complete_scope(self, constraint_id):
        if self._checks is None:
            self.check()
        return constraint_id not in self.incomplete_scope

    def _scope_match(self, info, scope):
        if scope["kind"] == "task":
            return True
        return (info["position"]["instruction_id"] == scope["instruction_id"]
                and info.get("scope") is not None
                and tuple(info.get("segment", ())[:2]) == tuple(scope["scope_path"]))

    def _matches(self, refs, *, key=None, instruction=None):
        for ref in refs or []:
            if "operation_path" in ref:
                if key is not None:
                    info = self.engine.ops[key]
                    if (info["position"]["instruction_id"] == ref["instruction_id"]
                            and info.get("raw_op") is not None
                            and tuple(info["raw_op"]) == tuple(ref["operation_path"])):
                        return True
            elif instruction == ref["instruction_id"]:
                return True
        return False

    def _reference_ops(self, refs, *, observations=False):
        found = set()
        for ref in refs or []:
            for key in self.by_ir[ref["instruction_id"]]:
                if "operation_path" not in ref or self._matches([ref], key=key):
                    found.add(key)
                elif observations and self.engine.ops[key].get("generated"):
                    info = self.engine.ops[key]
                    position = info["position"]
                    compiled = ["ir_semantics", ref["instruction_id"], "events", position["event_index"]]
                    if position.get("body_event_index") is not None:
                        compiled += ["body", position["body_event_index"]]
                    for row in self.engine.annotation["mapping"]["events"]:
                        if row["kind"] != "observation" or row["compiled_path"] != compiled:
                            continue
                        raw = row["raw_path"][2:]
                        bounds = row.get("raw_atomic_range")
                        operation = ref["operation_path"]
                        if (bounds and operation[:-2] == raw and operation[-2] == "atomic_ops"
                                and bounds[0] <= operation[-1] < bounds[1]):
                            found.add(key)
        return found

    def resolve_operations(self, constraint):
        if isinstance(constraint, str):
            constraint = self.constraints[constraint]
        if constraint["kind"] == "forbid_information":
            found = set(self.engine.ops) if constraint.get("events") is None else self._reference_ops(constraint["events"], observations=True)
            selected = set()
            for key in found:
                info = self.engine.ops[key]
                if info["spec"]["op"] not in {"deliver", "write"} or not self._scope_match(info, constraint["scope"]):
                    continue
                location_id = info["spec"].get("target")
                location = self.engine.compiled["locations"].get(location_id)
                if location is None:
                    continue
                receiver = constraint["receivers"]
                if (receiver["kind"] == "all" or receiver["kind"] == "locations" and location_id in receiver["ids"]
                        or receiver["kind"] == "kind" and location["kind"] == receiver["value"]):
                    selected.add(key)
            return selected
        refs = [*constraint.get("events", []), *constraint.get("before", []),
                *constraint.get("after", []), *constraint.get("triggers", [])]
        return {key for key in self._reference_ops(refs) if self._scope_match(self.engine.ops[key], constraint["scope"])}

    def _validate_scope(self, identity, constraint):
        if sum(isinstance(step, dict) for step in constraint.get("path", [])) > 1:
            self._uncheckable = True
            self._reasons.add("Nested collection quantification is outside the supported original-content fragment.")
        refs = [*(constraint.get("events", []) or []), *constraint.get("before", []),
                *constraint.get("after", []), *constraint.get("triggers", [])]
        # Reference validation is repeated defensively for authored offline
        # materials. A missing match must never silently become vacuous success.
        for ref in refs:
            if target_key(ref) not in self.engine.targets:
                self.incomplete_scope.add(identity)
                self._reasons.add("An event reference has no validated graph or raw-operation target.")
        for block in self._reachable:
            for ir in self.cfg["blocks"][block]["instructions"]:
                if self.engine.facts.coverage.get(ir["id"]) != "processed":
                    self.incomplete_scope.add(identity)
                    self._reasons.add("A task-entry-reachable instruction lacks complete propagation facts.")
        scope = constraint["scope"]
        if scope["kind"] == "element":
            raw_ir = self.engine.raw["ir_semantics"].get(scope["instruction_id"], {})
            try:
                event = raw_ir["events"][scope["scope_path"][1]]
                if event.get("kind") != "for_each":
                    raise KeyError("not a member scope")
            except (KeyError, IndexError, TypeError):
                self.incomplete_scope.add(identity)
                self._reasons.add("The declared element scope has no existing single-level for_each.")
            if any("operation_path" not in ref for ref in refs):
                self._uncheckable = True
                self._reasons.add("Per-element event occurrences require operation bindings, not a whole instruction.")
            owners = [block for block, value in self.cfg["blocks"].items()
                      if any(ir["id"] == scope["instruction_id"] for ir in value["instructions"])]
            if any(self._can_reach(edge["target_block_id"], block)
                   for block in owners for _, edge in self.edges[block]):
                self._uncheckable = True
                self._reasons.add("Repeated CFG visits to one element scope require persistent member identity; no fresh member reset is inferred.")

    def _tick(self):
        self._work += 1
        if self._work > self.max_states:
            raise _Limit("Constraint checking exceeded its finite resource limit; the explored prefix is incomplete.")

    def _expression(self, target):
        result = self.booleans.location(target)
        if result is None:
            self._uncheckable = True
            self._reasons.add("The condition has no existing supported expression at its referenced location.")
        return result

    def _condition(self, target, scope, cube, trace):
        located = self._expression(target)
        if located is None:
            return [(False, dict(cube)), (True, dict(cube))]
        expression, ir, entry = located
        path = entry["raw_path"]
        local_scope = scope if path and path[0] == "events" and "body" in path else None
        if local_scope is None and path and path[0] == "events" and "body" in path:
            self._uncheckable = True
            self._reasons.add("The condition's element evaluation cannot be matched to this occurrence.")
            return [(False, dict(cube)), (True, dict(cube))]
        if not self.booleans.available(expression, ir, local_scope, trace):
            self._uncheckable = True
            self._reasons.add("The condition requires a value version not established before this event occurrence.")
            return [(False, dict(cube)), (True, dict(cube))]
        return self.booleans.options(expression, ir, local_scope, cube)

    def _event(self, constraint, monitor, cube, trace, *, key=None, instruction=None, structural=False):
        if key is not None:
            info = self.engine.ops[key]
            if not self._scope_match(info, constraint["scope"]):
                return [(monitor, cube, trace + (key,))]
            self._seen_operations.add(key)
            scope = info.get("scope")
        else:
            scope = None
            trace = trace + ("@instruction:" + instruction,)
            if constraint["scope"]["kind"] == "element":
                return [(monitor, cube, trace)]
        kind = constraint["kind"]
        selected = self._matches(constraint.get("events", []), key=key, instruction=instruction)
        occurrence_trace = trace + ((key,) if key is not None else ())
        if kind == "only_if" and selected:
            states = self._condition(constraint["condition"], scope, cube, trace)
            for truth, facts in states:
                if not truth:
                    self._bad = True
                    self._witness = self._witness or occurrence_trace
            return [(monitor, facts, occurrence_trace) for _, facts in states]
        if kind == "at_most" and selected:
            if constraint["unit"] == "success":
                states = [(False, cube), (True, cube)] if structural else self._condition(constraint["success"], scope, cube, occurrence_trace)
            else:
                states = [(True, cube)]
            result = []
            for success, facts in states:
                count = min(constraint["limit"] + 1, monitor + int(success))
                if count > constraint["limit"]:
                    self._bad = True
                    self._witness = self._witness or occurrence_trace
                result.append((count, facts, occurrence_trace))
            return result
        if kind == "requires_prior":
            after = self._matches(constraint["after"], key=key, instruction=instruction)
            before = self._matches(constraint["before"], key=key, instruction=instruction)
            if constraint["matching"] == "request":
                if (after or before) and key is None:
                    self._uncheckable = True
                    self._reasons.add("Request matching requires operation occurrences with an existing request/response association.")
                    return [(monitor, cube, occurrence_trace)]
                if after:
                    pairs = self._request_pairs.get(key, set())
                    if len(pairs) != 1:
                        self._uncheckable = True
                        self._reasons.add("Request matching requires an existing unambiguous request/response association for every later occurrence.")
                    else:
                        bit = self._request_bits.get(next(iter(pairs)), 0)
                        if not bit or not monitor & bit:
                            self._bad = True
                            self._witness = self._witness or occurrence_trace
                return [(monitor | self._request_bits.get(key, 0) if before else monitor, cube, occurrence_trace)]
            if after and not monitor:
                self._bad = True
                self._witness = self._witness or occurrence_trace
            return [(int(bool(monitor or before)), cube, occurrence_trace)]
        if kind == "forbid_after":
            trigger = self._matches(constraint["triggers"], key=key, instruction=instruction)
            if selected and monitor:
                self._bad = True
                self._witness = self._witness or occurrence_trace
            return [(int(bool(monitor or trigger)), cube, occurrence_trace)]
        return [(monitor, cube, occurrence_trace)]

    def _operation(self, constraint, key, state, structural):
        monitor, cube, trace = state
        info = self.engine.ops[key]
        guard = info["spec"].get("when")
        if guard is None:
            active = [(True, cube)]
        elif structural:
            active = [(False, cube), (True, cube)]
        else:
            active = self.booleans.options({"op": "ref", "value": guard},
                info["position"]["instruction_id"], info.get("scope"), cube)
        result = []
        for enabled, facts in active:
            if enabled:
                result.extend(self._event(constraint, monitor, facts, trace, key=key, structural=structural))
            else:
                result.append((monitor, facts, trace))
        return result

    @staticmethod
    def _dependencies(spec, outer=None):
        atoms, dependencies = [], defaultdict(set)
        events = spec["events"] if outer is None else spec["events"][outer]["body"]
        for e, event in enumerate(events):
            if event.get("kind") == "for_each":
                atoms.append((e, -1))
            else:
                for o in range(len(event["atomic_ops"])):
                    atoms.append((e, o))
                    if o:
                        dependencies[(e, o)].add((e, o - 1))
        def project(position):
            e, b, o = position["event_index"], position.get("body_event_index"), position["op_index"]
            return ((e, -1) if b is not None else (e, o)) if outer is None else ((b, o) if e == outer and b is not None else None)
        for edge in spec.get("precedence", []):
            a, b = project(edge["before"]), project(edge["after"])
            if a is not None and b is not None and a != b:
                dependencies[b].add(a)
        if spec["order"] == "fixed":
            for a, b in zip(atoms, atoms[1:]):
                dependencies[b].add(a)
        return atoms, dependencies

    def _schedule(self, constraint, ir, initial, structural, *, outer=None, instance=None):
        spec = self.engine.compiled["ir_semantics"][ir]
        atoms, dependencies = self._dependencies(spec, outer)
        lookup = {}
        for key in self.by_ir[ir]:
            pos = self.engine.ops[key]["position"]
            if outer is None and pos.get("body_event_index") is None:
                lookup[(pos["event_index"], pos["op_index"])] = key
            elif outer == pos["event_index"] and pos.get("instance_index") == instance and pos.get("body_event_index") is not None:
                lookup[(pos["body_event_index"], pos["op_index"])] = key
        if outer is not None:
            initial = (initial[0], initial[1], initial[2] + ("@scope:" + ir + ":" + repr((outer, instance)),))
        pending = [(frozenset(), *initial)]
        visited, outcomes = set(), []
        while pending:
            done, monitor, cube, trace = pending.pop()
            identity = (done, monitor, tuple(sorted(cube.items())), tuple(dict.fromkeys(reversed(trace))))
            if identity in visited:
                continue
            visited.add(identity)
            self._tick()
            if len(done) == len(atoms):
                outcomes.append((monitor, cube, trace))
                continue
            ready = [atom for atom in atoms if atom not in done and dependencies[atom] <= done]
            if not ready:
                self._uncheckable = True
                self._reasons.add("The local precedence relation has no complete supported arrangement.")
            for atom in ready:
                if atom[1] == -1:
                    following = self._foreach(constraint, ir, atom[0], (monitor, cube, trace), structural)
                elif atom not in lookup:
                    self.incomplete_scope.add(self._identity)
                    self._reasons.add("A declared primitive operation has no indexed propagation record.")
                    following = [(monitor, cube, trace)]
                else:
                    following = self._operation(constraint, lookup[atom], (monitor, cube, trace), structural)
                pending.extend((done | {atom}, *state) for state in following)
        return outcomes

    def _foreach(self, constraint, ir, event, initial, structural):
        record = self.engine.facts.records[ir]["events"][event]
        instances = record.get("instances", [])
        relevant = [key for key in self.resolve_operations(constraint)
                    if self.engine.ops[key]["position"]["instruction_id"] == ir
                    and self.engine.ops[key]["position"]["event_index"] == event
                    and self.engine.ops[key].get("scope") is not None]
        per_element = constraint["scope"]["kind"] == "element" and bool(relevant)
        if constraint["scope"]["kind"] == "task" and constraint["kind"] in {"requires_prior", "forbid_after"} and relevant:
            self._uncheckable = True
            self._reasons.add("Task-wide ordering across member occurrences is outside the supported element-local fragment.")
        if per_element:
            sizes = {collection_size(self.data, identity) for identity in record["collections"]}
            if not instances and sizes != {0}:
                self.incomplete_scope.add(self._identity)
                self._reasons.add("The element scope has no complete indexed member-body arrangement.")
            for number in range(len(instances)):
                self._schedule(constraint, ir, (0, dict(initial[1]), initial[2]), structural, outer=event, instance=number)
            return [initial]
        sizes = {collection_size(self.data, identity) for identity in record["collections"]}
        if None in sizes:
            if relevant and constraint["kind"] == "at_most":
                self._uncheckable = True
                self._reasons.add("Unknown collection multiplicity prevents an exact task-wide occurrence bound.")
                sizes.discard(None)
                sizes.update((0, constraint["limit"] + 1))
            else:
                sizes.discard(None)
                sizes.update((0, 1))
        outcomes = []
        for size in sizes:
            states = [initial]
            for _ in range(size):
                next_states = []
                for state in states:
                    for number in range(len(instances)):
                        next_states.extend(self._schedule(constraint, ir, state, structural, outer=event, instance=number))
                states = self._unique(next_states)
                if not states:
                    self.incomplete_scope.add(self._identity)
                    self._reasons.add("The collection has no complete indexed member-body arrangement.")
                    break
            outcomes.extend(states)
        return self._unique(outcomes)

    @staticmethod
    def _unique(states):
        unique = {}
        for monitor, cube, trace in states:
            unique.setdefault((monitor, tuple(sorted(cube.items())), tuple(dict.fromkeys(reversed(trace)))), (monitor, cube, trace))
        return list(unique.values())

    def _edge_states(self, number, edge, cube, structural):
        if structural:
            return [dict(cube)]
        located = None
        for target in ({"path": ["edges", number]}, {"path": ["edges", number, "condition_text"]}):
            located = self.booleans.location(target)
            if located is not None:
                break
        if located is None:
            # A missing predicate is nondeterministic. This over-approximation
            # may establish safety, but never establishes edge feasibility.
            return [dict(cube)]
        expression, ir, _ = located
        return [facts for truth, facts in self.booleans.options(expression, ir, None, cube) if truth]

    def _walk(self, constraint, *, structural=False):
        self._work, self._bad, self._witness, self._seen_operations = 0, False, (), set()
        pending = deque([(self.cfg["entry_block_id"], 0, 0, {}, ())])
        visited = set()
        while pending:
            block, offset, monitor, cube, trace = pending.popleft()
            identity = (block, offset, monitor, tuple(sorted(cube.items())), tuple(dict.fromkeys(reversed(trace))))
            if identity in visited:
                continue
            visited.add(identity)
            self._tick()
            instructions = self.cfg["blocks"][block]["instructions"]
            if offset == len(instructions):
                for number, edge in self.edges[block]:
                    for facts in self._edge_states(number, edge, cube, structural):
                        target = edge["target_block_id"]
                        # Forget correlations on every cyclic transition. It
                        # cannot manufacture a stable value across iterations.
                        cyclic = target == block or self._can_reach(target, block)
                        pending.append((target, 0, monitor, {} if cyclic else facts, trace))
                continue
            ir = instructions[offset]["id"]
            states = self._event(constraint, monitor, cube, trace, instruction=ir, structural=structural)
            for state in states:
                for result in self._schedule(constraint, ir, state, structural):
                    pending.append((block, offset + 1, *result))
        return self._bad, list(self._witness), set(self._seen_operations)

    def _can_reach(self, source, target):
        seen, pending = set(), [source]
        while pending:
            block = pending.pop()
            if block == target:
                return True
            if block not in seen:
                seen.add(block)
                pending.extend(edge["target_block_id"] for _, edge in self.edges[block])
        return False

    def _information(self, constraint, reachable):
        source = constraint["source"]
        scopes = [None]
        if source["scope_path"]:
            scopes = sorted({info["scope"] for info in self.engine.ops.values()
                if info["position"]["instruction_id"] == source["instruction_id"]
                and info.get("scope") is not None and tuple(info.get("segment", ())[:2]) == tuple(source["scope_path"])})
        sources = set().union(*(self.booleans.ref_ids(source["value"], source["instruction_id"], scope) for scope in scopes))
        selected = self.resolve_operations(constraint) & reachable
        if not selected:
            return False, []
        if not sources:
            self.incomplete_scope.add(self._identity)
            self._reasons.add("The prohibited source has no resolved value candidates in its declared scope.")
            return False, []
        if any(range_presence(self.data, identity, constraint.get("path", [])) == "invalid" for identity in sources):
            self._reasons.add("The prohibited range is invalid for a resolved source value.")
        signals = ContentRanges(self.data, max_states=self.max_states).track(sources, constraint.get("path", []))
        direct, possible, witness = False, False, []
        for key in sorted(selected):
            record = self.engine.ops[key]["record"]
            for slot in payload_input_indices(record):
                for value in record["inputs"][slot]:
                    for signal in signals.get(value, []):
                        if range_presence(self.data, value, signal["path"]) in {"absent", "empty", "invalid"}:
                            continue
                        if signal["relation"] == "direct":
                            direct = True
                        else:
                            possible = True
                        if key not in witness:
                            witness.append(key)
        if direct:
            self._reasons.add("Declared original content has a direct route to an applicable payload candidate; this is not an observed execution.")
        elif possible:
            self._reasons.add("Only possible or derived influence reaches an applicable payload candidate; original plaintext inclusion is not established.")
        return direct or possible, witness

    def _prepare_request_matching(self, constraint):
        self._request_bits, self._request_pairs = {}, defaultdict(set)
        if constraint.get("matching") != "request":
            return
        for number, key in enumerate(sorted(self._reference_ops(constraint["before"]))):
            self._request_bits[key] = 1 << number
        for link in self.engine.index.links.values():
            if link["kind"] == "request_response":
                self._request_pairs[link["target"]].add(link["source"])
        for key in self.resolve_operations(constraint):
            ir = self.engine.ops[key]["position"]["instruction_id"]
            for block, value in self.cfg["blocks"].items():
                if (any(row["id"] == ir for row in value["instructions"])
                        and any(self._can_reach(edge["target_block_id"], block) for _, edge in self.edges[block])):
                    self._uncheckable = True
                    self._reasons.add("Request matching across repeated CFG occurrences requires an invocation identity beyond the supported static pair.")

    def _validate_count_units(self, constraint):
        if constraint["kind"] != "at_most":
            return
        bindings = [self._reference_ops([ref]) for ref in constraint["events"]]
        for link in self.engine.index.links.values():
            if link["kind"] != "request_response":
                continue
            left = {i for i, keys in enumerate(bindings) if link["source"] in keys}
            right = {i for i, keys in enumerate(bindings) if link["target"] in keys}
            if left and right and not left & right:
                self._uncheckable = True
                self._reasons.add("Distinct count selectors overlap one matched request/response invocation; a supported single occurrence unit is required.")

    def _cardinality_dependent(self, constraint):
        """A task count through members needs the collection's baseline value."""
        return (constraint["kind"] == "at_most" and constraint["scope"]["kind"] == "task"
                and (any(self.engine.ops[key].get("scope") is not None
                         for key in self.resolve_operations(constraint))
                     or any("body" in ref.get("operation_path", [])
                            for ref in constraint["events"])))

    def check(self):
        if self._checks is not None:
            return deepcopy(self._checks)
        results = {}
        for identity, constraint in self.constraints.items():
            self._reasons, self._uncheckable, self._identity = set(), False, identity
            self._validate_scope(identity, constraint)
            self._prepare_request_matching(constraint)
            self._validate_count_units(constraint)
            operations = self.resolve_operations(constraint)
            bad, witness, structural = False, [], False
            try:
                bad, witness, reached = self._walk(constraint)
                if constraint["kind"] == "forbid_information":
                    bad, witness = self._information(constraint, reached)
                baseline_reasons = set(self._reasons)
                if not bad and not baseline_reasons and identity not in self.incomplete_scope and constraint["kind"] in {"at_most", "requires_prior", "forbid_after"} and constraint.get("matching") != "request" and not self._cardinality_dependent(constraint):
                    all_path_bad, _, _ = self._walk(constraint, structural=True)
                    structural = not all_path_bad and not self._reasons
                    self._reasons = baseline_reasons
            except ConstraintCapability as error:
                self._uncheckable = True
                self._reasons.add(str(error))
            # Scope defects are never converted into an empty-domain guarantee.
            if identity in self.incomplete_scope or self._uncheckable:
                status = "not_established"
            elif bad:
                status = "potential_violation"
            elif self._reasons:
                status = "not_established"
            else:
                status = "satisfied"
            if not self._reasons:
                self._reasons.add("All supported task-entry behaviors satisfy this constraint within the declared static model." if status == "satisfied"
                    else "A permitted abstract behavior violates the constraint; feasibility and actual execution are not asserted.")
            results[identity] = {"requirement_id": constraint["requirement_id"],
                "raw_pointer": constraint["raw_pointer"], "kind": constraint["kind"], "status": status,
                "operations": sorted(operations), "reasons": sorted(self._reasons),
                "witness": [key for key in dict.fromkeys(witness) if key in self.engine.ops],
                "structural": structural and status == "satisfied"}
        self._checks = results
        return deepcopy(results)
