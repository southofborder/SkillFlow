"""Finite backward demands over verified operations, not global Data reachability.

The receiver of a value matters. Provenance is explanatory and never provides
an additional input channel. Rules preserve current supported relationships;
they neither execute a reduced Skill nor establish global irreplacability.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from pydantic import TypeAdapter

from skillflow.propagation.contracts.references import target_key
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.contracts.paths import split_semantics_path, processing_segment_path
from skillflow.propagation.contracts.uses import value_uses
from skillflow.propagation.conditions import payload_inputs, guard_truths, validate_record_consumption
from skillflow.propagation.contracts.limitations import processing_impacts, diagnostic_applies
from .material import _Index, _id, payload_alternatives
from . import selector_demands

EXACT_INFORMATION_BOUND_RULES = frozenset({
    "actual_operand", "cfg_result_use", "incoming_value", "public_result",
    "public_return_boundary", "processing_boundary", "selected_path", "remaining_content",
    "unchanged_content", "updated_value", "constructed_member", "expression_reference",
    "reviewed_input_contract", "reviewed_optional_input_presence", "same_element",
})


def _walk(value, path):
    for part in path:
        value = value[part]
    return value


def _prefix(a, b):
    return len(a) <= len(b) and a == b[:len(a)]


def _may_prefix(a, b):
    """Each member marker overlaps the corresponding numeric coordinate."""
    marker = {"kind": "each"}
    return len(a) <= len(b) and all(x == y or (x == marker and type(y) is int)
        or (y == marker and type(x) is int) for x, y in zip(a, b))


def _covers_prefix(a, b):
    marker = {"kind": "each"}
    return len(a) <= len(b) and all(x == y or (x == marker and type(y) is int)
                                   for x, y in zip(a, b))


def need(property="value", path=(), *, each=False, excluded=()):
    exclusions = {canonical_sha256(p): list(p) for p in excluded}
    return {"property": property, "path": list(path), "each": each,
            "excluded_paths": [exclusions[k] for k in sorted(exclusions)]}


def _full_path(n):
    return ([{"kind": "each"}] if n["each"] else []) + list(n["path"])


def _canonical_need(n):
    """Keep legacy root-each records while retaining a real field prefix."""
    n = deepcopy(n)
    if (not n["each"] and n["path"] and n["path"][0] == {"kind": "each"}
            and all(p and p[0] == {"kind": "each"} for p in n["excluded_paths"])):
        n["each"], n["path"] = True, n["path"][1:]
        n["excluded_paths"] = [p[1:] for p in n["excluded_paths"]]
    return n


def _prepend_need(n, path):
    prefix = list(path)
    marker = [{"kind": "each"}] if n["each"] else []
    return _canonical_need({**n, "path": prefix + marker + n["path"], "each": False,
        "excluded_paths": [prefix + marker + p for p in n["excluded_paths"]]})


def _expanded_need(n):
    """Use one current-root coordinate frame during transfer rules."""
    marker = [{"kind": "each"}] if n["each"] else []
    return {**n, "path": marker + n["path"], "each": False,
            "excluded_paths": [marker + p for p in n["excluded_paths"]]}


def _below(exclusions, path):
    """Exclusions use the current node's root, never a mix of two frames."""
    return [p[len(path):] for p in exclusions if _may_prefix(path, p)]


class DemandEngine:
    def __init__(self, facts, task, annotation, candidate, targets, *, input_contract_review=None, archived_v12=False):
        self._archive_validation = archived_v12
        self.facts, self.task, self.annotation = facts, task, annotation
        self.candidate, self.targets = candidate, targets
        self.index = _Index(facts)
        self.raw = annotation["raw_annotation"]
        self.compiled = annotation["compiled_annotation"]
        self._operand_locations = defaultdict(set)
        for location in self.compiled["locations"].values():
            for ref in location["operand_refs"]:
                self._operand_locations[(ref["instruction_id"], ref["side"], ref["index"])].add(
                    (location["kind"], location["name"]))
        if not archived_v12:
            # The forward interpreter resolves an unanchored context_key to
            # its own runtime_context address. Preserve that recorded argument
            # version in the corresponding demand and sensitivity operand.
            for ir, instruction in self.index.instructions.items():
                for slot, operand in enumerate(instruction["inputs"]):
                    if operand["type"] == "context_key":
                        self._operand_locations.setdefault((ir, "input", slot), {("runtime_context", operand["identifier"])})
        self.nodes, self.ops, self.raw_ops = {}, {}, defaultdict(list)
        self.locals, self.elements = {}, {}
        self.derivations, self.queue, self.diagnostics = {}, deque(), {}
        self.expressions, self.bound_goals = {}, set()
        self.unavailable_actions = {}
        self._active_seed = None
        self.realizations = {r["requirement_id"]: deepcopy(r) for r in self.compiled["realizations"]}
        self.observers = defaultdict(list)
        self.definitions = {out["identifier"]: (ir_id, i) for ir_id, ir in self.index.instructions.items()
                            for i, out in enumerate(ir["outputs"])}
        self.path_budget = 1 + max((len(g.get("path", [])) for g in candidate["goals"]), default=0)
        self._setup()
        self.selector_sources = selector_demands.sources(self)
        self.path_budget += sum(len(entry["guard"]["path"]) for entry in self.selector_sources.values())
        from .unavailable_actions import UnavailableDependencies
        self.unavailable_dependencies = UnavailableDependencies(self)
        from .input_contracts import InputContracts
        self.contracts = InputContracts(self, input_contract_review, archived_v12=archived_v12)
        from .source_input_findings import SourceInputMismatchIndex
        self.source_input_mismatches = SourceInputMismatchIndex(self.contracts.receipt)
        from .review_barriers import ReviewValidationBarriers
        self.review_validation_barriers = ReviewValidationBarriers(self.contracts.receipt)
        for entry in self.compiled.get("input_contracts", []):
            contract = entry["contract"]
            rules = contract.get("rules", [contract])
            for rule in rules:
                self.path_budget += len(rule.get("output", {}).get("path", []))
                self.path_budget += sum(len(wanted["path"]) for row in rule["inputs"] for wanted in row["required"])
                self.path_budget += sum(len(item["information"]["path"]) for row in rule["inputs"]
                                        for item in row.get("unresolved_ranges", []))

    def diagnostic(self, code, reason, ir=None, requirement=None, operation=None, *, blocking=True, affected=None):
        value = {"code": code, "reason": reason, "instruction_id": ir,
                 "requirement_id": requirement, "operation_id": operation, "blocking": blocking}
        if affected is not None:
            value["affected_instruction_ids"] = sorted(set(affected))
        key = _id("diagnostic_", value)
        self.diagnostics[key] = {"id": key, **value}
        return key

    def node(self, kind, *, ir=None, op=None, slot=None, data=(), **extra):
        identity = {"kind": kind, "instruction_id": ir, "operation_id": op, "slot": slot, **extra}
        key = _id("node_", identity)
        value = {**identity, "data_ids": sorted(set(data))}
        if key in self.nodes and self.nodes[key] != value:
            raise ValueError("Demand node identity conflict")
        self.nodes[key] = value
        return key

    def _setup(self):
        mappings = {(m["instruction_id"], tuple(split_semantics_path(m["compiled_path"])[1])): m
                    for m in self.annotation["mapping"]["events"]}
        adapter = TypeAdapter(AtomicOp)
        for key in self.index.sort_ops(self.index.operations):
            operation = self.index.operations[key]
            pos = operation["position"]
            ir = pos["instruction_id"]
            eventpath = ["events", pos["event_index"]]
            if pos["body_event_index"] is not None:
                eventpath += ["body", pos["body_event_index"]]
            spec = _walk(self.compiled["ir_semantics"][ir], eventpath)["atomic_ops"][pos["op_index"]]
            mapping = mappings.get((ir, tuple(eventpath)))
            if mapping is None:
                raise ValueError("Missing compilation mapping for demand operation")
            raw_ir, rawpath = split_semantics_path(mapping["raw_path"])
            segment_ir, segment = split_semantics_path(processing_segment_path(mapping["raw_path"]))
            if raw_ir != ir or segment_ir != ir:
                raise ValueError("Compilation mapping belongs to another instruction")
            rawop = None
            if mapping["kind"] != "observation":
                rawop = tuple(rawpath + ["atomic_ops", mapping["raw_atomic_range"][0] + pos["op_index"]])
            scope = (pos["event_index"], pos["instance_index"]) if pos["body_event_index"] is not None else None
            info = {**operation, "key": key, "spec": spec, "typed": adapter.validate_python(spec),
                    "segment": tuple(segment), "scope": scope, "raw_op": rawop,
                    "mode": mapping["mode"], "generated": mapping["kind"] == "observation",
                    "return_observation": mapping["kind"] == "observation" and rawpath[-1] == "returns"}
            if info["record"]["op"] != spec["op"]:
                raise ValueError("Recorded operation differs from compiled specification")
            validate_record_consumption(info["record"], self.index.data)
            expected_outputs = 1 if "output" in spec else 0
            if len(info["record"]["outputs"]) != expected_outputs:
                raise ValueError("Demand recorded output arity differs from specification")
            if spec["op"] == "build":
                if [m["path"] for m in info["record"]["members"]] != [m["path"] for m in spec["parts"]]:
                    raise ValueError("Demand constructed member paths differ")
                if any((m["when_input_index"] is None) != (s.get("when") is None)
                       for m, s in zip(info["record"]["members"], spec["parts"])):
                    raise ValueError("Demand constructed member conditions differ")
            elif spec.get("when") is not None:
                record = info["record"]
                guard = record.get("when_input_index")
                if guard is None:
                    raise ValueError("Demand conditional observation lacks its control input")
                active = True in guard_truths(self.index.data, record["inputs"][guard])
                if len(record["inputs"]) != 1 + (len(spec["inputs"]) if active else 0):
                    raise ValueError("Demand conditional observation consumption differs")
            elif len(info["record"]["inputs"]) != len(value_uses(info["typed"])):
                raise ValueError("Demand recorded input arity differs from specification")
            boundary_id = spec.get("location", spec.get("target"))
            if boundary_id is not None:
                boundary = self.compiled["locations"][boundary_id]
                if info["record"]["endpoints"] != [{k: boundary[k] for k in ("kind", "name")}]:
                    raise ValueError("Demand endpoint differs from compiled specification")
            self.ops[key] = info
            if rawop is not None:
                self.raw_ops[(ir, rawop)].append(key)
            if info["generated"]:
                self.observers[(ir, scope, info["segment"])].append(key)
            for slot, ids in enumerate(info["record"]["inputs"]):
                self.node("op_input", ir=ir, op=key, slot=slot, data=ids)
            for slot, ids in enumerate(info["record"]["outputs"]):
                output = self.node("op_output", ir=ir, op=key, slot=slot, data=ids)
                self.locals[(ir, scope, spec["output"])] = output
            for path in [spec.get("path", []), *spec.get("paths", []),
                         *(m["path"] for m in spec.get("parts", [])),
                         *(m["path"] for m in spec.get("updates", []))]:
                self.path_budget += len(path)
        for scope in self.index.scopes.values():
            ir = scope["instruction_id"]
            sid = (scope["event_index"], scope["instance_index"])
            spec = self.compiled["ir_semantics"][ir]["events"][scope["event_index"]]
            n = self.node("element", ir=ir, data=[scope["element"]], scope=list(sid),
                          collection=scope["collection"], reference=spec["collection"])
            self.elements[(ir, sid, spec["item"])] = n
        for ir, spec in self.compiled["ir_semantics"].items():
            record = self.index.records.get(ir, {})
            for event_index, event in enumerate(spec["events"]):
                if event.get("kind") == "for_each" and event.get("output") is not None:
                    recorded = record.get("events", [])
                    if event_index >= len(recorded):
                        # A declared collection is not an evaluated collection.
                        # Do not create a node which claims a recorded member
                        # scope and then fails the public result validator.
                        if self.index.coverage.get(ir) != "infeasible":
                            self.diagnostic("missing_collection_record",
                                "A declared collection output has no evaluated member scope; its payload and cardinality remain unresolved.", ir)
                        continue
                    if recorded[event_index].get("kind") != "for_each":
                        raise ValueError("Declared collection output differs from its recorded event kind")
                    outputs = recorded[event_index].get("outputs", [])
                    n = self.node("collection_output", ir=ir, data=outputs, event_index=event_index,
                                  reference=event["collection"], yield_reference=event["yield"])
                    self.locals[(ir, None, event["output"])] = n
                    self.path_budget += 1
        for ir, instruction in self.index.instructions.items():
            for side in ("inputs", "outputs"):
                for i, operand in enumerate(instruction[side]):
                    ids = self._operand_data(ir, i, side)
                    self.node("ir_input" if side == "inputs" else "ir_output", ir=ir, slot=i, data=ids)
        for supplement in self.candidate["expressions"]:
            target = self.targets[target_key(supplement["target"])]
            self.expressions[(target.get("instruction_id"), tuple(target["raw_path"]))] = supplement["expression"]

    def _contract_transfer(self, operation, n, requirement, parent, conservative=False):
        """Apply accepted semantic rules; gaps retain only named input ranges."""
        info = self.ops[operation]
        ir = info["position"]["instruction_id"]
        action_rule = "reviewed_input_contract"
        if n.get("selector_ref") and n["property"] == "truth" and info["spec"]["op"] == "compute":
            selector = self.selector_sources[n["selector_ref"]]
            # A rule for an opaque result's value is sufficient to preserve the decision.
            # Its individual inputs need not all affect this specific later classification.
            n = need("value", n["path"], each=n["each"], excluded=n["excluded_paths"])
            result = self.contracts.transfer(operation, n)
            if result["requirements"]:
                marker = self.diagnostic("selector_transfer_gap",
                    f"Reviewed compute at {ir} specifies inputs for the output value at {n['path']}. "
                    + selector_demands.reason(selector)
                    + " A predicate-specific relationship is needed to establish which of those inputs affect this decision.",
                    ir, requirement, operation, blocking=False)
                action_rule, conservative = "selector_gap:" + marker, True
        else:
            result = self.contracts.transfer(operation, n)
        for row in result["requirements"]:
            from .sensitivity_engine import range_presence
            values = info["record"]["inputs"][row["input_index"]]
            if row.get("if_present"):
                self.input(operation, row["input_index"], need("presence", row["path"]),
                           requirement, "reviewed_optional_input_presence" if action_rule == "reviewed_input_contract" else action_rule,
                           parent, conservative)
                if values and all(range_presence(self.index.data, value, row["path"]) in {"absent", "empty"} for value in values):
                    continue
            if row["property"] != "presence" and row["path"] and values:
                missing = [value for value in values if range_presence(self.index.data, value, row["path"]) == "absent"]
                invalid = [value for value in values if range_presence(self.index.data, value, row["path"]) == "invalid"]
                if missing and not row.get("if_present"):
                    self.diagnostic("input_contract_missing_input",
                        "The required input field " + str(row["path"]) + " is absent in recorded candidates "
                        + str(missing) + "; the declared output cannot be justified from that input. Contract: "
                        + str(result["contract_ids"]) + ". Correct the input binding or the source output specification.",
                        ir, requirement, operation, affected=[ir])
                if invalid:
                    self.diagnostic("input_contract_wrong_input",
                        "The required field selector " + str(row["path"]) + " is invalid for recorded input candidates "
                        + str(invalid) + "; correct the input type or source-backed field relation. Contract: "
                        + str(result["contract_ids"]) + ".", ir, requirement, operation, affected=[ir])
            self.input(operation, row["input_index"], need(row["property"], row["path"]),
                       requirement, action_rule, parent, conservative)
        for gap in result["gaps"]:
            reason = (gap["reason"] + " Output: " + str(gap["output"]) + "; contract: " + gap["pointer"]
                      + "; missing relationship: " + gap["missing"]
                      + "; required resolution: " + gap["resolution"]
                      + "; review scope: " + str(gap.get("scope_id")))
            diagnostic = self.diagnostic(gap["code"], reason, ir, requirement, operation, affected=[ir])
            if gap["no_inputs"]:
                continue
            slots = self.slots(operation) if gap["input_index"] is None else [gap["input_index"]]
            for slot in slots:
                self.input(operation, slot, need(gap["property"], gap["path"], excluded=gap["excluded_paths"]), requirement,
                           "input_contract_gap:" + diagnostic, parent, True,
                           information_bound=gap["information_bound"])
        return result

    def _review_validation_errors(self, key, node, information, requirement, conservative):
        """Retain affected real inputs without treating invalid findings as facts."""
        from .review_barriers import operation_barriers, barrier_diagnostic
        meta = self.nodes[node]
        operation = meta["operation_id"]
        if operation is None or meta["kind"] not in {"action", "op_output"}:
            return False
        barriers = operation_barriers(self, operation)
        for barrier in barriers:
            diagnostic = barrier_diagnostic(self, barrier, meta["instruction_id"], operation, requirement)
            rule = "input_contract_gap:" + diagnostic
            self.emit(node, information, requirement, rule, key, True)
            # The invalid record does not establish a narrower field relation.
            # Preserve every real operand even when an earlier gap already
            # made the arriving output demand conservative.
            for slot in self.slots(operation):
                self.input(operation, slot, need(), requirement, rule, key, True)
        return bool(barriers) and not conservative

    def _source_input_errors(self, key, node, information, requirement, conservative):
        """Record known native-output errors without inventing corrected inputs."""
        from .input_contracts import selector, overlaps, covers
        meta = self.nodes[node]
        operation = meta["operation_id"]
        if operation is None or meta["kind"] not in {"action", "op_output"}:
            return False
        info = self.ops[operation]
        wanted = selector(information)
        exclusions = [([{"kind": "each"}] if information.get("each") else []) + path
                      for path in information.get("excluded_paths", [])]
        matched = []
        for finding in self.source_input_mismatches.for_operation(meta["instruction_id"], list(info["raw_op"])):
            for impact in finding["impacts"]:
                if impact["kind"] == "action":
                    applies = meta["kind"] == "action"
                else:
                    applies = (meta["kind"] == "op_output" and overlaps(wanted["path"], impact["path"])
                        and not any(covers(path, impact["path"]) or covers(path, wanted["path"])
                                    for path in exclusions)
                        and (impact["property"] == "value"
                             or wanted["property"] == "value" and covers(wanted["path"], impact["path"])
                             or wanted["property"] == impact["property"] and len(wanted["path"]) == len(impact["path"])))
                if applies:
                    matched.append(finding)
                    break
        for finding in matched:
            diagnostic = self.diagnostic("input_contract_source_" + finding["kind"],
                "Known source input error " + finding["id"] + ": " + finding["reason"]
                + " Affected native demand: " + str(wanted)
                + ". The actual input is preserved; no missing or corrected value is synthesized.",
                meta["instruction_id"], requirement, operation, affected=[meta["instruction_id"]])
            self.emit(node, information, requirement, "input_contract_gap:" + diagnostic, key, True)
        # A conservative counterpart has a distinct identity. Process the real
        # dependencies through it rather than mutating an existing derivation.
        return bool(matched) and not conservative

    def _location_identity_inputs(self, operation, requirement, parent, conservative):
        """Retain exact CFG operands bound to a required boundary's location."""
        info = self.ops[operation]
        ir = info["position"]["instruction_id"]
        spec = info["spec"]
        location = self.compiled["locations"].get(spec.get("target", spec.get("location")), {})
        for reference in location.get("operand_refs", []):
            if reference["instruction_id"] == ir and reference["side"] == "input":
                self.emit(self.node_at("ir_input", ir, slot=reference["index"]), need(), requirement,
                          "required_location_identity", parent, conservative)

    def _operand_data(self, ir, index, side):
        operand = self.index.instructions[ir][side][index]
        if operand["type"] == "literal":
            return []
        if operand["type"] == "result":
            locations = [("result", operand["identifier"])]
        else:
            locations = self._operand_locations.get((ir, "input" if side == "inputs" else "output", index), ())
        state = self.index.state_bindings.get((ir, "entry" if side == "inputs" else "exit"), {})
        return {data_id for location in locations for data_id in state.get(location, ())}

    def node_at(self, kind, ir=None, op=None, slot=None):
        return next((k for k, v in self.nodes.items() if v["kind"] == kind and v["instruction_id"] == ir
                     and v["operation_id"] == op and v["slot"] == slot), None)

    def resolve(self, ref, ir, scope=None):
        if ref["kind"] == "input":
            n = self.node_at("ir_input", ir, slot=ref["index"])
            if n is None:
                raise ValueError("Demand reference input is outside CFG")
            return [n]
        if ref["kind"] == "local":
            key = (ir, scope, ref["name"])
            n = self.elements.get(key) or self.locals.get(key) or self.locals.get((ir, None, ref["name"]))
            if n is None:
                # Raw scope validity was checked before solving. A valid
                # producer can nevertheless be absent in partial forward facts.
                self.diagnostic("missing_local_record", "No resolved producer record is available for local " + ref["name"] + ".", ir)
                return []
            return [n]
        if ref["kind"] == "alternatives":
            return sorted({n for item in ref["items"] for n in self.resolve(item, ir, scope)})
        return [self.node("literal", ir=ir, value=deepcopy(ref["value"]))]

    def slots(self, key):
        """Map real recorded slots to their symbolic uses, including guards."""
        info = self.ops[key]
        op, record = info["spec"], info["record"]
        if op["op"] == "build":
            result = {}
            for member, row in zip(op["parts"], record["members"]):
                if row["when_input_index"] is not None:
                    result[row["when_input_index"]] = (member["when"], "control")
                if row["value_input_index"] is not None:
                    result[row["value_input_index"]] = (member["value"], "value")
            return result
        if op.get("when") is not None:
            guard = record["when_input_index"]
            return {**{i: (ref, "value") for i, ref in enumerate(op["inputs"][:guard])},
                    guard: (op["when"], "control")}
        uses = value_uses(info["typed"])
        result = {}
        for i, use in enumerate(uses):
            if i < len(record["inputs"]):
                result[i] = (use.value.model_dump(mode="json"), use.role)
        return result

    def emit(self, node, n, req, rule, parent=None, conservative=False, *, information_bound=None):
        if node is None:
            self.diagnostic("missing_binding", "No existing operation or value binding can carry this demand.", requirement=req)
            return
        n = _canonical_need(n)
        if n.get("selector_ref") and rule not in selector_demands.ROOT_RULES | selector_demands.COPY_RULES:
            entry = self.selector_sources[n["selector_ref"]]
            marker = self.diagnostic("selector_transfer_gap", f"The transfer {rule} does not prove how to preserve "
                            + selector_demands.reason(entry) + " Provide the relationship for this operand.",
                            ir=self.nodes[node]["instruction_id"], requirement=req, blocking=False)
            n = {**n, "property": "value"}
            del n["selector_ref"]
            rule = "selector_gap:" + marker
            conservative = True
        # Uncertain necessity can still have a reviewed upper bound on the
        # information property. Carry that bound only through exact transfers;
        # an unrelated weak/opaque dependency must not inherit certification.
        if information_bound is None:
            information_bound = bool(conservative and parent and rule in EXACT_INFORMATION_BOUND_RULES
                and self.derivations[parent].get("information_bound", False))
        information_bound = bool(conservative and information_bound)
        if len(n["path"]) > self.path_budget:
            n, conservative = need(), True
            information_bound = False
            self.diagnostic("path_widening", "Recursive access paths were conservatively retained as a whole value.",
                            ir=self.nodes[node]["instruction_id"], requirement=req, blocking=False)
        seed = self.derivations[parent]["seed_goal_id"] if parent is not None else self._active_seed
        if seed is None:
            raise ValueError("Every demand derivation requires an originating seed goal")
        key = _id("demand_", [node, n, req, seed, conservative, information_bound])
        if key in self.derivations:
            row = self.derivations[key]
            row["rules"] = sorted(set(row["rules"]) | {rule})
            if parent and parent != key:
                row["parents"] = sorted(set(row["parents"]) | {parent})
            return
        self.derivations[key] = {"id": key, "node": deepcopy(self.nodes[node]),
                                 **n, "requirement_id": req, "seed_goal_id": seed, "conservative": conservative,
                                 "rules": [rule], "parents": [parent] if parent and parent != key else []}
        if information_bound:
            self.derivations[key]["information_bound"] = True
        self.queue.append((key, node, n, req, conservative, seed))

    def emit_ref(self, ref, ir, scope, n, req, rule, parent=None, conservative=False):
        def protect_choices(value):
            if value["kind"] == "alternatives":
                guard = value.get("guard")
                if guard:
                    self._case_control(ir, guard, req, parent, conservative)
                for item in value["items"]:
                    protect_choices(item)
        protect_choices(ref)
        nodes = self.resolve(ref, ir, scope)
        for node in nodes:
            self.emit(node, n, req, rule, parent, conservative or len(nodes) > 1)

    def _selector_need(self, ir, operand, guard):
        return {**need(selector_demands.control_property(guard), guard["path"]),
                "selector_ref": selector_demands.reference(ir, operand, guard)}

    def _case_control(self, ir, guard, requirement, parent, conservative, rule="typed_case_selector"):
        slot = guard["input_index"]
        self.emit(self.node_at("ir_input", ir, slot=slot),
                  self._selector_need(ir, {"kind": "input", "index": slot}, guard),
                  requirement, rule, parent, conservative)

    def input(self, key, slot, n, req, rule, parent, conservative=False, *, information_bound=None):
        self.emit(self.node_at("op_input", self.ops[key]["position"]["instruction_id"], key, slot),
                  n, req, rule, parent, conservative, information_bound=information_bound)

    def _observe(self, source, ir, scope, segment, n, req, parent, conservative):
        """Attach only observations emitted for the same real processing segment."""
        for key in self.observers[(ir, scope, segment)]:
            for slot, (ref, role) in self.slots(key).items():
                if role == "control":
                    continue
                if source in self.resolve(ref, ir, scope):
                    self.input(key, slot, n, req, "processing_boundary", parent, conservative)

    def _controls(self, ir, req, parent):
        """Retain actual branch operands controlling a task-related position.

        Text conditions are not parsed. Keeping their declared operands is a
        conservative dependence, never a field-level Boolean proof.
        """
        demand = self.derivations[parent]
        unestablished = demand["conservative"] and demand["seed_goal_id"] in self.unavailable_actions
        target_block = self.index.ir_block[ir]
        for block, successors in self.index.successors.items():
            if len(successors) < 2 or not any(target_block in self.index.reachable[s] for s in successors):
                continue
            instructions = self.index.cfg["blocks"][block]["instructions"]
            if not instructions:
                continue
            control = instructions[-1]
            expressions = [expr for (owner, path), expr in self.expressions.items()
                           if owner == control["id"] and path and path[0] != "events"]
            if expressions:
                for expression in expressions:
                    self._control_expression(expression, control["id"], need("truth"), req, parent, unestablished)
                continue
            branches = [info for info in self.ops.values() if info["position"]["instruction_id"] == control["id"]
                        and info["spec"]["op"] == "branch"]
            if branches:
                for info in branches:
                    selector = info["spec"].get("selector")
                    if selector:
                        self.input(info["key"], 0, self._selector_need(control["id"], info["spec"]["input"], selector),
                                   req, "typed_control_operand", parent, unestablished)
                        continue
                    prop = "truth" if info["spec"]["predicate"] == "truthy" else "cardinality"
                    self.emit_ref(info["spec"]["input"], control["id"], info["scope"], need(prop), req,
                                  "typed_control_operand", parent, unestablished)
                continue
            for i, operand in enumerate(control["inputs"]):
                if operand["type"] not in {"literal", "external_resource"}:
                    self.emit(self.node_at("ir_input", control["id"], slot=i), need(), req,
                              "control_operands_retained", parent, True)

    def _control_expression(self, expr, ir, n, req, parent, conservative=False):
        op = expr["op"]
        if op == "ref":
            self.emit_ref(expr["value"], ir, None, n, req, "structured_control", parent, conservative)
        elif op == "literal":
            return
        elif op == "field":
            self._control_expression(expr["arg"], ir, _prepend_need(n, expr["path"]), req, parent, conservative)
        elif op in {"present", "count", "not"}:
            self._control_expression(expr["arg"], ir, need({"present": "presence", "count": "cardinality", "not": "truth"}[op]), req, parent, conservative)
        else:
            for arg in expr["args"] if op in {"and", "or"} else [expr["left"], expr["right"]]:
                self._control_expression(arg, ir, need("truth" if op in {"and", "or"} else "value"), req, parent, conservative)

    def expression(self, expr, info, n, req, parent, conservative=False, *, each=False):
        op = expr["op"]
        ir, scope = info["position"]["instruction_id"], info["scope"]
        if op == "ref":
            demand = {**n, "each": n["each"] or each}
            sources = self.resolve(expr["value"], ir, scope)
            # Route through actual operand slots when available so boundary
            # obligations are not lost by jumping straight to producers.
            matched = False
            for slot, (ref, _) in self.slots(info["key"]).items():
                if set(sources) == set(self.resolve(ref, ir, scope)):
                    self.input(info["key"], slot, demand, req, "expression_reference", parent, conservative)
                    matched = True
            if not matched:
                raise ValueError("Expression refers to a value not consumed by its operation")
        elif op == "literal":
            return
        elif op == "field":
            self.expression(expr["arg"], info, _prepend_need(n, expr["path"]),
                            req, parent, conservative, each=each)
        elif op == "present":
            self.expression(expr["arg"], info, need("presence"), req, parent, conservative, each=each)
        elif op == "count":
            self.expression(expr["arg"], info, need("cardinality"), req, parent, conservative, each=each)
        elif op == "not":
            self.expression(expr["arg"], info, need("truth"), req, parent, conservative, each=each)
        else:
            children = expr["args"] if op in {"and", "or"} else [expr["left"], expr["right"]]
            prop = "truth" if op in {"and", "or"} else "value"
            for child in children:
                self.expression(child, info, need(prop), req, parent, conservative, each=each)

    def _target_ops(self, target):
        ir, path = target.get("instruction_id"), tuple(target.get("operation_raw_path", target.get("raw_path", [])))
        if target["kind"] in {"input_use", "local_output"} and "operation_raw_path" not in target:
            path = path[:-2] if target["kind"] == "input_use" else path[:-1]
        return self.raw_ops.get((ir, path), [])

    def seed(self):
        from skillflow.propagation.contracts.demand import goal_target_capability
        requirement_ids = {r.id for r in self.task.requirements}
        goal_ids_by_requirement = defaultdict(set)
        for goal in self.candidate["goals"]:
            req, prop = goal["requirement_id"], goal["preserve"]
            goal_ids_by_requirement[req].add(goal["id"])
            self._active_seed = goal["id"]
            target = self.targets[target_key(goal["target"])]
            ir = target.get("instruction_id")
            if goal_target_capability(target, prop) is None:
                self.diagnostic("unbound_goal", "The selected target cannot carry this executable preservation property.", ir, req)
                continue
            if ir and self.index.coverage.get(ir) == "infeasible":
                # The checked propagation result proves this path inactive.
                # Keep its declared goal but do not look for a nonexistent
                # producer or claim its Task requirement has been fulfilled.
                self.diagnostic("inactive_goal", "This goal targets an instruction excluded by verified path conditions; no demand is seeded on this path.",
                                ir, req, blocking=False)
                continue
            goal_path = goal.get("path", [])
            each = bool(goal_path and isinstance(goal_path[0], dict) and goal_path[0].get("kind") == "each")
            n = need(prop, goal_path[1:] if each else goal_path, each=each)
            keys = self._target_ops(target)
            if prop == "action" and ir:
                evidence = self.unavailable_dependencies.evidence(goal, target)
                if evidence is not None:
                    diagnostic = self.diagnostic(evidence["code"], evidence["reason"], ir, req)
                    self.unavailable_actions[goal["id"]] = target
                    self.emit(self.node("action", ir=ir), n, req,
                              "unavailable_dependency:" + diagnostic, conservative=True)
                    if not keys:
                        continue
                elif target["kind"] != "instruction" and not keys:
                    self.diagnostic("inactive_goal", "The instruction was evaluated with no active occurrence of this selected operation. No action demand is seeded for the excluded occurrence.",
                                    ir, req, blocking=False)
                    continue
            if keys:
                self.bound_goals.add(req)
                for key in keys:
                    info = self.ops[key]
                    if prop == "action":
                        action = self.node("action", ir=ir, op=key)
                        self.emit(action, need("action"), req, "task_action")
                        continue
                    if target["kind"] == "local_output" or target["kind"] == "operation":
                        node = self.node_at("op_output", ir, key, 0)
                    elif target["kind"] == "input_use":
                        raw_use = value_uses(info["typed"])[target["slot"]]
                        if info["spec"]["op"] == "build":
                            row = info["record"]["members"][raw_use.member_index]
                            actual_slot = row["when_input_index"] if raw_use.role == "control" else row["value_input_index"]
                        else:
                            actual_slot = target["slot"]
                        slots = [] if actual_slot is None else [actual_slot]
                        if not slots:
                            # A definitively omitted conditional value has no
                            # input slot. Its guard still belongs to the build.
                            continue
                        node = self.node_at("op_input", ir, key, slots[0])
                    else:
                        node = None
                    if goal.get("expected") is not None:
                        self._seed_expected(goal, info, node, n)
                    else:
                        self.emit(node, n, req, "task_value")
                continue
            if target["kind"] in {"input", "output"} and ir:
                slot = int(target["raw_path"][-1])
                node = self.node_at("ir_input" if target["kind"] == "input" else "ir_output", ir, slot=slot)
                if goal.get("expected") is not None:
                    self._seed_expected(goal, {"position": {"instruction_id": ir}, "scope": None, "key": None}, node, n)
                else:
                    self.emit(node, n, req, "task_operand")
                self.bound_goals.add(req)
            elif target["kind"] == "output_binding" and ir:
                output = target["output_index"]
                node = self.node_at("ir_output", ir, slot=output)
                if goal.get("expected") is not None:
                    self._seed_expected(goal, {"position": {"instruction_id": ir}, "scope": None, "key": None}, node, n)
                else:
                    self.emit(node, n, req, "task_output_binding")
                self.bound_goals.add(req)
            elif prop == "action" and ir:
                self.emit(self.node("action", ir=ir), n, req, "task_action")
                self.bound_goals.add(req)
            else:
                self.diagnostic("unbound_goal", "The selected target cannot carry this executable preservation property.", ir, req)
        for req in sorted(requirement_ids):
            realization = self.realizations.get(req)
            if realization is None:
                raise ValueError("A Task requirement has no explicit realization record: " + req)
            if realization["status"] != "expressed" or realization["gaps"]:
                # Model bindings alone cannot certify a local scope. Unknown
                # effects (including order/count/prohibition gaps) are global.
                self.diagnostic("requirement_expression_gap",
                    "This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.",
                    requirement=req)
            goals = goal_ids_by_requirement[req]
            only_located_failures = bool(goals) and goals <= self.unavailable_actions.keys()
            if req not in self.bound_goals and not realization.get("constraints") and not only_located_failures:
                self.diagnostic("unbound_requirement", "No applicable demand goal is available; this does not mean the requirement can be omitted.", requirement=req)
        for issue in self.task.issues:
            if issue.resolution == "unresolved":
                self.diagnostic("task_source_issue", "The source retains an unresolved task ambiguity or conflict: " + issue.reason)
        self._active_seed = None

    def _seed_expected(self, goal, info, node, n):
        """Do not seed a wrong whole actual argument as an exact task value."""
        req, ir = goal["requirement_id"], info["position"]["instruction_id"]
        expected_nodes = self.resolve(goal["expected"], ir, info["scope"])
        expected_path = goal.get("expected_path", [])
        actual_ids = set(self.nodes[node]["data_ids"]) if node else set()
        sources = {d for src in expected_nodes for d in self.nodes[src]["data_ids"]}
        actual_path = None
        expected_relations = set().union(*(self._relation(src, expected_path) for src in expected_nodes))
        n = _expanded_need(n)
        actual_relations = self._relation(node, n["path"]) if node else set()
        if actual_relations and actual_relations == expected_relations:
            actual_path = n["path"]
        elif actual_ids and actual_ids <= sources:
            actual_path = expected_path + n["path"]
            self.diagnostic("expected_relation_projection", "The actual argument is the containing value, while the Task requires an original field. The field demand does not establish that the current argument already has the required identity.",
                            ir, req, info["key"])
        elif actual_ids:
            matches = [self._part_of(d, sources, expected_path) for d in actual_ids]
            if all(matches):
                actual_path = n["path"]
        if actual_path is not None:
            self.emit(node, {**n, "path": actual_path}, req, "task_expected_relation")
        else:
            self.diagnostic("expected_relation_mismatch", "The actual value does not establish the Task's expected original-value relation.", ir, req, info["key"])
        for source in expected_nodes:
            self.emit(source, {**n, "path": expected_path, "excluded_paths": []}, req, "required_original_value")

    def _relation(self, node, path, seen=None):
        """Normalize exact symbolic copies/selections, without evaluating Data.

        This is an original-value correspondence check, not an input channel or
        an opaque-function equivalence proof. Optional absent members add no
        false value relationship; their presence is handled by build rules.
        """
        if node is None:
            return set()
        seen = set() if seen is None else set(seen)
        identity = (node, canonical_sha256(path))
        if identity in seen:
            return {identity}
        seen.add(identity)
        meta = self.nodes[node]
        ir, op_key = meta["instruction_id"], meta["operation_id"]
        kind = meta["kind"]
        if kind == "ir_input":
            operand = self.index.instructions[ir]["inputs"][meta["slot"]]
            if operand["type"] == "result":
                producer, slot = self.definitions[operand["identifier"]]
                return self._relation(self.node_at("ir_output", producer, slot=slot), path, seen)
        elif kind == "ir_output":
            binding = next((b for b in self.compiled["ir_semantics"].get(ir, {}).get("output_bindings", []) if b["output_index"] == meta["slot"]), None)
            if binding:
                return set().union(*(self._relation(n, path, seen) for n in self.resolve(binding["value"], ir)))
        elif kind == "op_input":
            info = self.ops[op_key]
            ref = self.slots(op_key)[meta["slot"]][0]
            return set().union(*(self._relation(n, path, seen) for n in self.resolve(ref, ir, info["scope"])))
        elif kind == "op_output":
            info = self.ops[op_key]
            op = info["spec"]
            refs = []
            if op["op"] == "select_part":
                refs = [(op["input"], op["path"] + path)]
            elif op["op"] == "build" and path:
                refs = [(m["value"], path[len(m["path"]):]) for m in op["parts"] if _may_prefix(m["path"], path)]
            elif op["op"] == "exclude_parts" and not any(_prefix(p, path) for p in op["paths"]):
                if path:
                    refs = [(op["input"], path)]
            elif op["op"] == "update_fields" and path:
                refs = [(m["value"], path[len(m["path"]):]) for m in op["updates"] if _prefix(m["path"], path)]
                if not refs and not any(_prefix(path, m["path"]) for m in op["updates"]):
                    refs = [(op["input"], path)]
            if refs:
                return set().union(*(self._relation(n, p, seen) for ref, p in refs for n in self.resolve(ref, ir, info["scope"])))
        return {identity}

    def _part_of(self, data_id, bases, path, seen=None):
        # Content/part identity is used for checking an expected relation only;
        # it never creates a producer or a receiver input channel.
        seen = set() if seen is None else seen
        if data_id in seen:
            return False
        seen.add(data_id)
        if not path and data_id in bases:
            return True
        data = self.index.data[data_id]
        origin = data["origin"]
        parent, subpath = origin.get("part_of"), origin.get("path")
        if parent and subpath and len(subpath) <= len(path) and subpath == path[-len(subpath):]:
            return self._part_of(parent, bases, path[:-len(subpath)], seen)
        return False

    def step(self, key, node, n, req, conservative, seed):
        self._active_seed = seed
        meta = self.nodes[node]
        kind, ir, op_key = meta["kind"], meta["instruction_id"], meta["operation_id"]
        if op_key and kind in {"action", "op_output", "op_input"}:
            guard = (self.ops[op_key].get("case") or {}).get("guard")
            if guard:
                self._case_control(ir, guard, req, key, conservative)
        if ir:
            self._controls(ir, req, key)
        if self._review_validation_errors(key, node, n, req, conservative):
            return
        if self._source_input_errors(key, node, n, req, conservative):
            return
        if op_key is not None and kind in {"action", "op_output"}:
            self._location_identity_inputs(op_key, req, key, conservative)
        if kind == "literal":
            return
        if kind == "element":
            from .sensitivity_engine import unstable_collection_offsets
            instance = self.index.records[ir]["events"][meta["scope"][0]]["instances"][meta["scope"][1]]
            selected = instance.get("selector")
            member = selected if type(selected) is int and not unstable_collection_offsets(self.index.data, meta["collection"]) else {"kind": "each"}
            self.emit_ref(meta["reference"], ir, None, _prepend_need(n, [member]), req, "same_element", key, conservative)
            self.emit_ref(meta["reference"], ir, None, need("shape"), req, "iteration_shape", key, conservative)
            return
        if kind == "collection_output":
            n = _expanded_need(n)
            # A map preserves membership/count, not the source members' contents.
            collection_need = need(n["property"] if not n["path"] and not n["each"]
                                   and n["property"] in {"presence", "cardinality"} else "shape")
            self.emit_ref(meta["reference"], ir, None, collection_need, req, "map_membership", key, conservative)
            if not n["path"] and not n["each"] and n["property"] in {"presence", "cardinality"}:
                return
            events = self.index.records.get(ir, {}).get("events", [])
            if meta["event_index"] >= len(events):
                self.diagnostic("missing_collection_record", "A demanded collection has no evaluated yield record; no member values are supplied.", ir, req)
                return
            event = events[meta["event_index"]]
            for number, instance in enumerate(event.get("instances", [])):
                selected = instance.get("selector")
                from .sensitivity_engine import unstable_collection_offsets
                filtered = unstable_collection_offsets(self.index.data, instance["collection"])
                demand = n
                member_selected = bool(n["path"] and n["path"][0] == {"kind": "each"})
                if n["path"] and (type(n["path"][0]) is int or member_selected):
                    if not filtered and type(selected) is int and selected != n["path"][0]:
                        if not member_selected:
                            continue
                    member_path = [selected if type(selected) is int and not filtered else {"kind": "each"}]
                    if any(_covers_prefix(p, member_path) for p in n["excluded_paths"]):
                        continue
                    exclusions = [p for p in n["excluded_paths"] if not (
                        member_path == [{"kind": "each"}] and p and type(p[0]) is int)]
                    demand = {**n, "path": n["path"][1:],
                              "excluded_paths": _below(exclusions, member_path)}
                scope = (meta["event_index"], number)
                yielded = set(instance.get("yielded", []))
                for source in self.resolve(meta["yield_reference"], ir, scope):
                    ids = set(self.nodes[source]["data_ids"])
                    if not ids or ids & yielded:
                        self.emit(source, demand, req, "map_yield", key,
                                  conservative or (filtered or type(selected) is not int) and bool(n["path"])
                                  and (not member_selected or exclusions != n["excluded_paths"]))
            return
        if kind == "ir_input":
            operand = self.index.instructions[ir]["inputs"][meta["slot"]]
            if operand["type"] == "result":
                definition, index = self.definitions[operand["identifier"]]
                self.emit(self.node_at("ir_output", definition, slot=index), n, req, "cfg_result_use", key, conservative)
            elif operand["type"] not in {"literal", "external_resource"}:
                if seed in self.unavailable_actions and conservative:
                    self.unavailable_dependencies.context_operand(ir, meta["slot"], n, req, key)
                    return
                locations = [(loc["kind"], loc["name"]) for loc in self.compiled["locations"].values()
                             if {"instruction_id": ir, "side": "input", "index": meta["slot"]} in loc["operand_refs"]]
                for location in locations:
                    for write in self.index.entry_writes.get(ir, {}).get(location, set()):
                        info = self.ops[write]
                        if info["spec"]["mode"] != "delete":
                            stored = self.index.written_values(write, location)
                            if not stored.intersection(meta["data_ids"]):
                                continue
                            weak = any(c["update"] == "weak" for c in info["record"]["changes"])
                            self.input(write, 0, n if info["spec"]["mode"] == "replace" else need(), req,
                                       "context_reaching_write", key, conservative or weak or info["spec"]["mode"] == "append")
                            if info["spec"]["mode"] == "append":
                                self.diagnostic("append_prior_content", "A required context append includes prior content; only its added payload is attached to the save sink.", ir, req, write)
            return
        if kind == "ir_output":
            binding = next((b for b in self.compiled["ir_semantics"].get(ir, {}).get("output_bindings", []) if b["output_index"] == meta["slot"]), None)
            if (seed in self.unavailable_actions and conservative
                    and self.unavailable_dependencies.has_incomplete_execution(ir)):
                self.unavailable_dependencies.output(ir, binding, n, req, key)
                if not meta["data_ids"]:
                    return
            if binding is None:
                self.diagnostic("missing_output_binding", "A required public result has no transfer binding.", ir, req)
            else:
                self.emit_ref(binding["value"], ir, None, n, req, "public_result", key, conservative)
                # A local segment can return an unchanged IR input, with no
                # local producer node. Its declared return boundary must not
                # disappear merely because the public binding is a copy.
                sources = set(self.resolve(binding["value"], ir))
                for observer, info in self.ops.items():
                    if info["position"]["instruction_id"] != ir or not info["return_observation"] or info["scope"] is not None:
                        continue
                    for slot, (ref, role) in self.slots(observer).items():
                        if role == "value" and sources.intersection(self.resolve(ref, ir)):
                            self.input(observer, slot, n, req, "public_return_boundary", key, conservative)
            return
        if kind == "action":
            if not op_key and conservative and seed in self.unavailable_actions:
                self.unavailable_dependencies.action(ir, self.unavailable_actions[seed], req, key)
            if op_key:
                info = self.ops[op_key]
                contract = self.contracts.entry(op_key)
                boundary = self.compiled["locations"].get(info["spec"].get("target"), {})
                if contract is not None:
                    self._contract_transfer(op_key, need() if contract["kind"] == "compute" else need("action"), req, key, conservative)
                elif (info["spec"]["op"] == "deliver" and not info["generated"]
                      and boundary.get("kind") in {"tool", "remote"} and self.slots(op_key)):
                    self._contract_transfer(op_key, need("action"), req, key, conservative)
            if op_key and self.ops[op_key]["scope"] is not None:
                info = self.ops[op_key]
                collection = self.compiled["ir_semantics"][ir]["events"][info["scope"][0]]["collection"]
                self.emit_ref(collection, ir, None, need("shape"), req, "required_iteration", key, conservative)
            return
        info = {**self.ops[op_key], "key": op_key}
        scope = info["scope"]
        if kind == "op_input":
            ref, role = self.slots(op_key)[meta["slot"]]
            for source in self.resolve(ref, ir, scope):
                self.emit(source, n, req, "actual_operand", key, conservative)
                if not info["generated"] and info["mode"] != "local":
                    self._observe(source, ir, scope, info["segment"], n, req, key, conservative)
            # Retain an observation's guard separately from its payload.
            if info["spec"].get("when") is not None and role != "control":
                for slot, (_, slot_role) in self.slots(op_key).items():
                    if slot_role == "control":
                        self.input(op_key, slot, need("truth"), req, "conditional_observation", key, conservative)
            return
        # A required acquired/returned value traverses its real observation;
        # internal local inputs do not inherit a return observation by Data ID.
        self._observe(node, ir, scope, info["segment"], n, req, key, conservative)
        op = info["spec"]
        operation = op["op"]
        expression = self.expressions.get((ir, info["raw_op"]))
        if operation == "merge":
            for slot in self.slots(op_key):
                if info["record"]["inputs"][slot]:
                    self.input(op_key, slot, n, req, "incoming_value", key, conservative)
        elif operation == "member":
            self.input(op_key, 0, _prepend_need(n, [{"kind": "each"}]), req, "loop_member", key, conservative)
            self.input(op_key, 0, need("shape"), req, "loop_membership", key, conservative)
        elif operation == "append":
            self._append(info, n, req, key, conservative)
        elif operation == "select_part":
            self.input(op_key, 0, _prepend_need(n, op["path"]),
                       req, "selected_path", key, conservative)
        elif operation == "exclude_parts":
            n = _expanded_need(n)
            if any(_covers_prefix(p, n["path"]) for p in op["paths"]):
                self.diagnostic("excluded_requirement", "A required path has been explicitly removed.", ir, req, op_key)
            else:
                self.input(op_key, 0, {**n, "excluded_paths": n["excluded_paths"] + op["paths"]}, req, "remaining_content", key, conservative)
        elif operation == "update_fields":
            n = _expanded_need(n)
            handled = False
            for slot, update in enumerate(op["updates"], 1):
                path = update["path"]
                if any(_covers_prefix(p, path) for p in n["excluded_paths"]):
                    continue
                if _may_prefix(path, n["path"]):
                    self.input(op_key, slot, {**n, "path": n["path"][len(path):],
                                             "excluded_paths": _below(n["excluded_paths"], path)}, req, "updated_value", key, conservative)
                    handled = handled or _covers_prefix(path, n["path"])
                elif _may_prefix(n["path"], path):
                    if not n.get("selector_ref"):
                        self.input(op_key, slot, need(excluded=_below(n["excluded_paths"], path)), req, "updated_descendant", key, conservative)
            if not handled:
                self.input(op_key, 0, {**n, "excluded_paths": n["excluded_paths"] + [x["path"] for x in op["updates"]]}, req,
                           "unchanged_content", key, conservative)
        elif operation == "build":
            self._build(info, n, req, key, conservative)
        elif operation == "filter_items":
            self.input(op_key, 0, n, req, "selected_members", key, conservative)
            self.input(op_key, 0, need("shape"), req, "filter_shape", key, conservative)
            if expression:
                self.expression(expression, info, need("truth"), req, key, conservative, each=True)
            else:
                self.input(op_key, 0, need(each=True), req, "opaque_predicate", key, True)
        elif operation == "compute":
            if expression:
                self.expression(expression, info, n, req, key, conservative)
            else:
                self._contract_transfer(op_key, n, req, key, conservative)
        elif operation == "receive":
            has_contract = self.contracts.entry(op_key) is not None
            if has_contract or self.slots(op_key):
                self._contract_transfer(op_key, n, req, key, conservative)
            for link in self.index.links.values():
                if link["kind"] == "request_response" and link["target"] == op_key:
                    request = link["source"]
                    self.emit(self.node("action", ir=ir, op=request), need("action"), req, "required_acquisition", key, conservative)
        elif operation == "read":
            for link in self.index.links.values():
                if link["kind"] == "saved_read" and link["target"] == op_key:
                    write = link["source"]
                    mode = self.ops[write]["spec"]["mode"]
                    if mode == "append":
                        self.input(write, 0, need(), req, "append_dependency", key, True)
                        self.diagnostic("append_prior_content", "Required appended storage also depends on prior content; only the current payload is this sink's exposure.", ir, req, write)
                    elif mode != "delete":
                        weak = any(c["update"] == "weak" for c in self.ops[write]["record"]["changes"])
                        self.input(write, 0, n, req, "reaching_write", key, conservative or weak)

    def _append(self, info, n, req, parent, conservative):
        """Demand the selected old or contributed member, never all payloads."""
        from .constraint_control import collection_size
        n = _expanded_need(n)
        old_ids = info["record"]["inputs"][0]
        sizes = {collection_size(self.index.data, value) for value in old_ids}
        size = next(iter(sizes)) if len(sizes) == 1 else None
        path = n["path"]
        key = info["key"]
        if not path and n["property"] in {"presence", "cardinality", "shape"}:
            self.input(key, 0, n, req, "accumulation_structure", parent, conservative)
            if info["spec"]["mode"] == "items":
                self.input(key, 1, n, req, "contribution_structure", parent, conservative)
            return
        selected = path[0] if path else None
        known_index = type(selected) is int and size is not None
        if not known_index or selected < size:
            self.input(key, 0, n, req, "accumulated_content", parent, conservative)
        if known_index and selected < size:
            return
        marker = selected if known_index else {"kind": "each"}
        if info["spec"]["mode"] == "item":
            if known_index and selected != size:
                return
            if any(_covers_prefix(p, [marker]) for p in n["excluded_paths"]):
                return
            self.input(key, 1, {**n, "path": path[1:] if path else [],
                "excluded_paths": _below(n["excluded_paths"], [marker])},
                req, "accumulation_yield", parent, conservative or type(selected) is int and size is None)
        else:
            suffix = path[1:] if path else []
            shifted = [selected - size, *suffix] if known_index else ([{"kind": "each"}, *suffix] if path else [])
            # Unknown prior length cannot justify translating concrete output
            # exclusions into a particular contribution's local index.
            excluded = [[p[0] - size, *p[1:]] for p in n["excluded_paths"]
                if p and type(p[0]) is int and p[0] >= size] if size is not None else [
                    p for p in n["excluded_paths"] if p and p[0] == {"kind": "each"}]
            self.input(key, 1, {**n, "path": shifted, "excluded_paths": excluded},
                req, "accumulation_items", parent, conservative or type(selected) is int and size is None)

    def _build(self, info, n, req, parent, conservative):
        n = _expanded_need(n)
        if n.get("selector_ref") and not n["path"]:
            return  # build fixes the root container kind even when all conditional fields are absent.
        for member, row in zip(info["spec"]["parts"], info["record"]["members"]):
            path = member["path"]
            if n["path"] and not (_may_prefix(path, n["path"]) or _may_prefix(n["path"], path)):
                continue
            if any(_covers_prefix(p, path) for p in n["excluded_paths"]):
                continue
            if row["when_input_index"] is not None:
                self.input(info["key"], row["when_input_index"], need("truth"), req, "member_presence", parent, conservative)
            slot = row["value_input_index"]
            if slot is None:
                continue
            # The built container's membership is known from its members, but
            # a member's nested membership/size still depends on the value.
            # In particular count(build({rows: x}).rows) needs count(x).
            inside_member = _may_prefix(path, n["path"])
            if n.get("selector_ref") and not inside_member:
                continue  # Conditional membership above is sufficient for a constructed prefix.
            if n["property"] == "presence" and (not inside_member or path == n["path"]):
                continue
            if n["property"] in {"cardinality", "shape"} and not inside_member:
                continue
            remainder = n["path"][len(path):] if inside_member else []
            self.input(info["key"], slot, {**n, "path": remainder,
                                          "excluded_paths": _below(n["excluded_paths"], path)},
                       req, "constructed_member", parent, conservative)

    def solve(self, *, queue_order="fifo"):
        if self._archive_validation:
            raise ValueError("Historical DOE input is for persisted-result validation only")
        if queue_order not in {"fifo", "lifo"}:
            raise ValueError("Unsupported demand queue order")
        self.seed()
        while self.queue:
            args = self.queue.popleft() if queue_order == "fifo" else self.queue.pop()
            self.step(*args)
        for d in self.index.diagnostics:
            self.diagnostic("upstream_diagnostic", d.get("reason", str(d)), d.get("instruction_id"),
                            affected=d.get("affected_instruction_ids"))
        for ir, state in self.index.coverage.items():
            if state not in {"processed", "infeasible"}:
                self.diagnostic("upstream_coverage", "Upstream propagation has not established this instruction's execution; coverage: " + state + ".", ir)
        impacts = processing_impacts(self.index.cfg, self.compiled)
        for gap in self.compiled.get("processing_gaps", []):
            if self.index.coverage[gap["instruction_id"]] == "infeasible":
                continue
            from skillflow.propagation.contracts.limitations import gap_id
            identity = gap_id(gap)
            self.diagnostic("processing_gap", identity + ": " + gap["reason"], gap["instruction_id"],
                            affected=impacts[identity])
        sinks = self._sinks()
        from .input_assessments import build_input_assessments
        input_assessments, input_findings = build_input_assessments(self)
        from skillflow.propagation.facts import declared_boundary_coverage
        unresolved = [row["boundary"] for row in declared_boundary_coverage(self.compiled, self.index.sinks, self.index.coverage)
                      if row["status"] == "unresolved"]
        return {"schema_version": "skillflow-demand-v13",
                "status": "partial" if any(d["blocking"] for d in self.diagnostics.values()) else "complete",
                "goals": deepcopy(self.candidate["goals"]),
                "traceability": self._traceability(),
                "derivations": {k: {field: deepcopy(value) for field, value in self.derivations[k].items()
                                    if field != "id"} for k in sorted(self.derivations)},
                "sinks": sinks,
                "input_assessments": input_assessments,
                "input_findings": input_findings,
                "input_contract_review_sha256": (self.contracts.receipt or {}).get("receipt_sha256"),
                "diagnostics": [self.diagnostics[k] for k in sorted(self.diagnostics)],
                "coverage": {"requirements": {r.id: {
                    **{k: deepcopy(v) for k, v in self.realizations[r.id].items() if k != "constraints"},
                    "goal_ids": [g["id"] for g in self.candidate["goals"] if g["requirement_id"] == r.id],
                    "constraint_ids": [c["constraint_id"] for c in self.annotation["mapping"]["constraints"]
                                       if c["requirement_id"] == r.id],
                    "has_applicable_goal": r.id in self.bound_goals} for r in self.task.requirements},
                             "sinks": len(sinks), "expected_sinks": len(self.index.sinks),
                             **({"unresolved_boundaries": unresolved} if unresolved else {}),
                             "upstream": deepcopy(self.index.coverage)}}

    def _traceability(self):
        """Generated linkage; no model-authored duplicate requirement prose."""
        mappings = {row["goal_id"]: row for row in self.annotation["mapping"]["goals"]}
        canonical_goals = {goal["id"]: goal for goal in self.compiled["demands"]}
        rows = []
        for requirement in self.task.requirements:
            req = requirement.id
            seeds = []
            for goal in self.candidate["goals"]:
                if goal["requirement_id"] != req:
                    continue
                seed = goal["id"]
                mapping = mappings.get(seed) if canonical_goals.get(seed) == goal else None
                if mapping is None:
                    # Explicit offline candidate can differ from model demands.
                    raw_pointer = None
                else:
                    raw_pointer = mapping["raw_pointer"]
                derivations = sorted(k for k, d in self.derivations.items() if d["seed_goal_id"] == seed)
                seeds.append({"goal_id": seed, "raw_pointer": raw_pointer, "derivation_ids": derivations})
            rows.append({"requirement_id": req,
                "seeds": seeds})
        return {"task_ref": deepcopy(self.compiled["task_ref"]), "requirements": rows}

    def _sinks(self):
        result = []
        for boundary in self.index.sinks:
            keys = self.index.sink_operations(boundary)
            ids = [k for k, d in self.derivations.items() if d["node"]["operation_id"] in keys
                   and d["node"]["kind"] in {"op_input", "action"}]
            payload = [{"operation_id": k, "position": self.ops[k]["position"],
                        "inputs": deepcopy(payload_inputs(self.ops[k]["record"])),
                        **({"alternatives": payload_alternatives(self.ops[k]["record"])}
                           if self.ops[k]["record"].get("alternatives") else {})} for k in keys]
            sliced = self.index.slice(boundary)
            relevant = set(sliced["usage_context"]["instructions"])
            relevant.update(self.ops[k]["position"]["instruction_id"] for k in sliced["backward_slice"]["operations"])
            from .input_assessments import applicable_contract_diagnostics
            contract_limits = applicable_contract_diagnostics(self.derivations, ids)
            limits = sorted(k for k, d in self.diagnostics.items() if d["blocking"] and (
                k in contract_limits if d["code"].startswith("input_contract_") else diagnostic_applies(d, relevant,
                            scoped_instructions=sliced["usage_context"]["instructions"])))
            established = [k for k in ids if not self.derivations[k]["conservative"]]
            conservative = [k for k in ids if self.derivations[k]["conservative"]]
            ranges = []
            for op_key in keys:
                record = self.ops[op_key]["record"]
                guard = record.get("when_input_index")
                for slot, data_ids in enumerate(record["inputs"]):
                    if slot == guard:
                        continue
                    demands = [self.derivations[k] for k in ids if self.derivations[k]["node"]["kind"] == "op_input"
                               and self.derivations[k]["node"]["operation_id"] == op_key and self.derivations[k]["node"]["slot"] == slot]
                    if not demands:
                        ranges.append({"operation_id": op_key, "input_index": slot, "data_ids": data_ids,
                                       "description": "No payload demand was established at this boundary; this is not a deletion certificate.",
                                       "scope": "whole_slot"})
                    elif not any(d["property"] == "value" and not d["path"] and not d["excluded_paths"] for d in demands):
                        ranges.append({"operation_id": op_key, "input_index": slot, "data_ids": data_ids,
                                       "description": "Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.",
                                       "scope": "outside_listed_properties"})
            result.append({"id": _id("sink_", boundary), "boundary": deepcopy(boundary),
                           "actual_payload": payload,
                           "related_requirements": sorted({self.derivations[k]["requirement_id"] for k in ids}),
                           "demanded_information": sorted(established), "conservative_retention": sorted(conservative),
                           "unestablished_ranges": ranges, "limitations": limits})
        return sorted(result, key=lambda s: s["id"])
