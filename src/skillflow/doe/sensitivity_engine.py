"""Read-only content tracking and property-aware sink comparisons.

Content edges carry original information. Dependency edges carry influence.
They are deliberately distinct, including when both lead to the same sink.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.conditions import payload_input_indices
from skillflow.propagation.data import is_definitely_empty_collection
from skillflow.propagation.contracts.paths import semantics_path, element_scope_path
from .material import _id


def _step_matches(left, right):
    if left == right:
        return True
    if isinstance(left, dict) and left.get("kind") == "each":
        return type(right) is int or isinstance(right, dict) and right.get("kind") in {"each", "element"}
    if isinstance(right, dict) and right.get("kind") == "each":
        return type(left) is int or isinstance(left, dict) and left.get("kind") in {"each", "element"}
    return False


def prefix(left, right):
    """Symbolic each matches an element or index, never a field named '*'."""
    return len(left) <= len(right) and all(_step_matches(a, b) for a, b in zip(left, right))


def covers(left, right):
    """One symbolic member is not the same range as every possible member."""
    return len(left) <= len(right) and all(a == b or isinstance(a, dict) and a.get("kind") == "each"
        and (type(b) is int or isinstance(b, dict) and b.get("kind") in {"each", "element"})
        for a, b in zip(left, right))


def _paths(values):
    return [value for _, value in sorted({canonical_sha256(p): deepcopy(p) for p in values}.items())]


def dominates(left, right):
    """Drop redundant routes of one declaration, never merge declarations."""
    ranks = {"direct": 0, "derived": 1, "possible": 2}
    if left["declaration_id"] != right["declaration_id"] or left["property"] != right["property"]:
        return False
    if ranks[left["relation"]] > ranks[right["relation"]] or not covers(left["path"], right["path"]):
        return False
    if left["path"] == right["path"] and left["excluded_paths"] == right["excluded_paths"]:
        return True
    return not any(prefix(p, right["path"]) or prefix(right["path"], p) for p in left["excluded_paths"])


def cut(signal, excluded):
    """Remove a content range without reviving it through a provenance edge."""
    if any(covers(p, signal["path"]) for p in excluded):
        return None
    result = deepcopy(signal)
    result["excluded_paths"] = _paths([*signal["excluded_paths"],
        *(p for p in excluded if prefix(signal["path"], p))])
    return result


def select(signal, path):
    """Project a range into an existing part; no Data is allocated or refined."""
    if any(covers(p, path) for p in signal["excluded_paths"]):
        return None
    if prefix(path, signal["path"]):
        result = deepcopy(signal)
        result["path"] = signal["path"][len(path):]
    elif prefix(signal["path"], path):
        # A structure-only annotation is about that structure, not every value
        # reachable from it. A whole-value declaration does cover its parts.
        if signal["property"] != "value":
            return None
        result = deepcopy(signal)
        result["path"] = []
        # A sensitive document is not evidence that every proper subfield is
        # independently sensitive. Keep a candidate, not copied plaintext.
        result["relation"] = "possible"
    else:
        return None
    result["excluded_paths"] = _paths([p[len(path):] for p in signal["excluded_paths"] if prefix(path, p)])
    return result


def embed(signal, path):
    return {**deepcopy(signal), "path": [*deepcopy(path), *signal["path"]],
            "excluded_paths": [[*deepcopy(path), *p] for p in signal["excluded_paths"]]}


def _demand_range(demand):
    start = [{"kind": "each"}] if demand["each"] else []
    return [*start, *demand["path"]], [[*start, *p] for p in demand["excluded_paths"]]


def demand_overlap(signal, demand):
    """Return preservation of this property, a structural restriction, or none.

    Conservative dependencies retain the affected range regardless of a narrow
    property spelling. A scalar truth requirement is not a license to invent a
    new classifier. Structure/presence do not automatically demand field values.
    """
    path, exclusions = _demand_range(demand)
    sensitive = signal["path"]
    if any(covers(p, sensitive) for p in exclusions):
        return "none"
    if any(covers(p, path) for p in signal["excluded_paths"]):
        return "none"
    if not (prefix(path, sensitive) or prefix(sensitive, path)):
        return "none"
    if demand["conservative"]:
        return "retain"
    prop, wanted = signal["property"], demand["property"]
    if wanted == "value":
        return "retain"
    if wanted == "action":
        return "none"
    if wanted == prop:
        return "retain"
    if wanted == "truth":
        return "retain"  # Existing computation still consumes its operand.
    if prop in {"presence", "cardinality", "shape"}:
        # Do not invent an independence rule between structural observations.
        return "retain"
    return "structure"


def range_presence(data, data_id, path, seen=None):
    """Known absence is not an opaque remainder. Never allocate a missing part."""
    if not path:
        return "present"
    seen = set() if seen is None else set(seen)
    key = (data_id, canonical_sha256(path))
    if key in seen:
        return "unknown"
    seen.add(key)
    content = data[data_id]["content"]
    form = content["form"]
    if isinstance(path[0], dict) and path[0].get("kind") == "each" and is_definitely_empty_collection(data, data_id):
        return "empty"
    if form == "literal":
        def literal(value, steps):
            if not steps:
                return "present"
            step, remaining = steps[0], steps[1:]
            if isinstance(step, dict):
                if type(value) is not list:
                    return "invalid"
                statuses = [literal(child, remaining) for child in value]
                if not statuses or all(status == "empty" for status in statuses):
                    return "empty"
                return "present" if "present" in statuses else "absent"
            if type(step) is str and type(value) is dict:
                return literal(value[step], remaining) if step in value else "absent"
            if type(step) is int and type(value) is list:
                return literal(value[step], remaining) if step < len(value) else "absent"
            return "invalid"
        return literal(content["value"], path)
    if form == "whole_except":
        if any(covers(excluded, path) for excluded in content["excluded_parts"]):
            return "absent"
        return range_presence(data, content["base"], path, seen)
    if form == "field_updates":
        for update in content["updates"]:
            if covers(update["path"], path):
                return range_presence(data, update["data"], path[len(update["path"]):], seen)
        if any(covers(path, update["path"]) for update in content["updates"]):
            return "present"
        return range_presence(data, content["base"], path, seen)
    if form == "subset_view":
        # Selection can be empty. Presence in a source is at most possible in
        # the subset, while a field impossible in every source cannot appear.
        source = range_presence(data, content["base"], path, seen)
        return source if source in {"absent", "invalid", "empty"} else "unknown"
    if form == "known_parts":
        statuses = []
        for part in content["parts"]:
            if prefix(part["path"], path):
                statuses.append(range_presence(data, part["data"], path[len(part["path"]):], seen))
            elif prefix(path, part["path"]):
                statuses.append("present")
        if "present" in statuses:
            return "present"
        if "unknown" in statuses:
            return "unknown"
        if "invalid" in statuses:
            return "invalid"
        if statuses and all(status == "empty" for status in statuses):
            return "empty"
        if statuses or content["parts_complete"]:
            return "absent"
    return "unknown"


def _expression_uses(expression, property="value", path=None):
    """Use the already validated expression vocabulary, not opcode names."""
    path = [] if path is None else path
    op = expression["op"]
    if op == "ref":
        return [(expression["value"], {"property": property, "path": path})]
    if op == "literal":
        return []
    if op == "field":
        return _expression_uses(expression["arg"], property, expression["path"] + path)
    if op in {"present", "count", "not"}:
        return _expression_uses(expression["arg"], {"present": "presence", "count": "cardinality", "not": "truth"}[op])
    if op in {"and", "or"}:
        return [use for argument in expression["args"] for use in _expression_uses(argument, "truth")]
    return [use for side in ("left", "right") for use in _expression_uses(expression[side])]


def _expression_influence(signal, uses):
    """Count/presence never manufacture a dependency on member field values."""
    for use in uses:
        path = use["path"]
        if any(covers(p, path) for p in signal["excluded_paths"]):
            continue
        if not (prefix(path, signal["path"]) or prefix(signal["path"], path)):
            continue
        if use["property"] in {"cardinality", "presence", "shape"}:
            if signal["property"] == use["property"] and signal["path"] == path:
                return True
            if signal["property"] == "value" and len(signal["path"]) > len(path):
                continue
            if use["property"] == "presence" and signal["property"] == "value" and signal["path"] == path:
                continue
        return True
    return False


class SensitivityEngine:
    def __init__(self, demand_engine, demand_result, declarations):
        self.engine, self.demand = demand_engine, demand_result
        self.data, self.declarations = demand_engine.index.data, declarations
        self.rows, self.by_data, self.edges = {}, defaultdict(set), defaultdict(list)
        self.queue, self.diagnostics, self.resolved = deque(), {}, set()
        self.path_budget = 2 + sum(len(p.get("path", [])) for d in self.data.values()
            for p in [*d["content"].get("parts", []), *d["content"].get("updates", [])])
        self.path_budget += sum(len(d["declaration"]["path"]) for d in declarations.values())
        self._edges()

    def diagnostic(self, code, reason, ir=None, op=None, blocking=True):
        row = {"code": code, "reason": reason, "instruction_id": ir,
               "operation_id": op, "blocking": blocking}
        identity = _id("sensitivity_diagnostic_", row)
        self.diagnostics[identity] = {"id": identity, **row}
        return identity

    def _edges(self):
        expression_inputs = {}
        for key, operation in self.engine.ops.items():
            spec, record = operation["spec"], operation["record"]
            expression = self.engine.expressions.get((operation["position"]["instruction_id"], operation["raw_op"]))
            if spec["op"] == "compute" and expression is not None:
                requirements = defaultdict(list)
                for ref, needed in _expression_uses(expression):
                    for slot, (actual, role) in self.engine.slots(key).items():
                        if actual == ref:
                            for data_id in record["inputs"][slot]:
                                requirements[data_id].append(needed)
                for slot in record["outputs"]:
                    for output in slot:
                        expression_inputs[output] = requirements
            if spec["op"] == "build":
                for member in record["members"]:
                    guard = member["when_input_index"]
                    if guard is None:
                        continue
                    for source in record["inputs"][guard]:
                        for slot in record["outputs"]:
                            for target in slot:
                                if source in self.data[target]["origin"]["inputs"]:
                                    self.edges[source].append((target, "conditional_membership", member["path"]))
        for identity, data in self.data.items():
            content, origin = data["content"], data["origin"]
            form = content["form"]
            if form == "known_parts":
                for part in content["parts"]:
                    self.edges[identity].append((part["data"], "select", part["path"]))
                    self.edges[part["data"]].append((identity, "embed", part["path"]))
            elif form in {"whole_except", "field_updates", "subset_view"}:
                removed = content.get("excluded_parts", [p["path"] for p in content.get("updates", [])])
                self.edges[content["base"]].append((identity, "subset" if form == "subset_view" else "cut", removed))
                for part in content.get("updates", []):
                    self.edges[part["data"]].append((identity, "embed", part["path"]))
            if origin.get("part_of"):
                self.edges[origin["part_of"]].append((identity, "select", origin["path"]))
                self.edges[identity].append((origin["part_of"], "embed", origin["path"]))
            # Explicit structure above is authoritative about retained content.
            # Refining an opaque acquired/computed value into open known parts
            # does not remove its original influence. Closed constructions and
            # explicit exclusions/updates still use their content edges only.
            # Acquisition influence does not imply copied request plaintext.
            if (form == "opaque" or form == "known_parts" and not content["parts_complete"]) and not origin.get("part_of"):
                for dependency in origin.get("dependencies", []):
                    requirements = expression_inputs[identity].get(dependency["data"], []) if identity in expression_inputs else None
                    self.edges[dependency["data"]].append((identity, dependency["relation"], requirements))

    def emit(self, data_id, signal, rule, parent=None):
        signal = {k: deepcopy(signal[k]) for k in ("declaration_id", "label", "property", "path", "excluded_paths", "relation")}
        if len(signal["path"]) > self.path_budget:
            self.diagnostic("sensitivity_path_limit", "A recursive content path cannot be represented precisely; its influence is retained.")
            signal.update(path=[], excluded_paths=[], relation="possible")
        identity = _id("sensitivity_", [data_id, signal])
        if identity in self.rows:
            row = self.rows[identity]
            row["rules"] = sorted(set(row["rules"]) | {rule})
            if parent and parent != identity:
                row["parents"] = sorted(set(row["parents"]) | {parent})
            return
        if any(dominates(self.rows[old], signal) for old in self.by_data[data_id]):
            return
        self.rows[identity] = {"id": identity, "data_id": data_id, **signal,
                               "rules": [rule], "parents": [parent] if parent and parent != identity else []}
        self.by_data[data_id].add(identity)
        self.queue.append(identity)

    def _scopes(self, declaration):
        path = declaration["scope_path"]
        if not path:
            return [None]
        ir = declaration["instruction_id"]
        result = set()
        # Map raw foreach positions to compiled scope instances. Different
        # instances stay distinct; their recipient and body are never crossed.
        for operation in self.engine.ops.values():
            if operation["position"]["instruction_id"] == ir and operation["scope"] is not None:
                if tuple(operation["segment"][:len(path)]) == tuple(path):
                    result.add(operation["scope"])
        return sorted(result)

    def _empty_scope(self, declaration):
        """Use verified compilation coordinates, not missing locals, as proof."""
        path, ir = declaration["scope_path"], declaration["instruction_id"]
        if not path:
            return False
        prefix_path = semantics_path(ir, *path, "body")
        event_indices = {scope[1] for m in self.engine.annotation["mapping"]["events"]
            if m["instruction_id"] == ir and m["raw_path"][:len(prefix_path)] == prefix_path
            and (scope := element_scope_path(m["compiled_path"])) is not None}
        record = self.engine.facts.records.get(ir)
        if record is None or len(event_indices) != 1:
            return False
        event = record["events"][next(iter(event_indices))]
        return (event.get("kind") == "for_each" and bool(event["collections"])
            and not event["instances"]
            and all(is_definitely_empty_collection(self.data, value) for value in event["collections"]))

    def seed(self):
        for identity, row in self.declarations.items():
            declaration = row["declaration"]
            if sum(isinstance(step, dict) and step.get("kind") == "each" for step in declaration["path"]) > 1:
                self.diagnostic("unsupported_sensitivity_scope", "Nested each sensitivity ranges are outside the supported single member scope.", row["instruction_id"])
                continue
            refs = set()
            for scope in self._scopes(row):
                for node in self.engine.resolve(declaration["value"], row["instruction_id"], scope):
                    refs.update(self.engine.nodes[node]["data_ids"])
            if not refs:
                if self._empty_scope(row):
                    self.resolved.add(identity)
                    continue
                self.diagnostic("unresolved_sensitivity_reference", "A declared sensitive value has no resolved Data candidate.", row["instruction_id"])
                continue
            absent = False
            for data_id in refs:
                presence = range_presence(self.data, data_id, declaration["path"])
                if presence == "empty":
                    continue  # A quantified range has no members, not a missing value.
                valid_absence = (presence == "absent" and declaration["property"] == "presence" and declaration["path"]
                    and type(declaration["path"][-1]) in {str, int}
                    and range_presence(self.data, data_id, declaration["path"][:-1]) not in {"absent", "invalid"})
                if presence in {"absent", "invalid"} and not valid_absence:
                    self.diagnostic("absent_sensitive_range", "The declared range is absent from resolved Data " + data_id + "; no sensitive content is manufactured.", row["instruction_id"])
                    absent = True
                    continue
                self.emit(data_id, {"declaration_id": identity, "label": declaration["label"],
                    "property": declaration["property"], "path": declaration["path"],
                    "excluded_paths": [], "relation": "direct"}, "explicit_declaration")
            if not absent:
                self.resolved.add(identity)

    def track(self):
        self.seed()
        while self.queue:
            identity = self.queue.popleft()
            row = self.rows[identity]
            for target, relation, parameter in self.edges[row["data_id"]]:
                if relation == "select":
                    signal = select(row, parameter)
                elif relation == "embed":
                    signal = embed(row, parameter)
                elif relation == "cut":
                    signal = cut(row, parameter)
                elif relation == "subset":
                    signal = deepcopy(row)
                    if not signal["path"]:
                        signal["relation"] = "possible"
                    # A filtered collection preserves members, not index identity.
                    if signal["path"] and type(signal["path"][0]) is int:
                        signal["path"][0] = {"kind": "each"}
                        signal["relation"] = "possible"
                    # A removed member index cannot be identified after a
                    # filter, but an excluded field of every member remains so.
                    if any(p and type(p[0]) is int for p in signal["excluded_paths"]):
                        signal["excluded_paths"] = [p for p in signal["excluded_paths"] if not p or type(p[0]) is not int]
                        signal["relation"] = "possible"
                elif relation == "conditional_membership":
                    signal = deepcopy(row)
                    # The guard influences inclusion. This is not a claim that
                    # the guard value was copied into the object, or a new
                    # independent declaration that presence is sensitive.
                    signal.update(path=parameter, excluded_paths=[], relation="possible" if row["relation"] == "possible" else "derived")
                else:
                    if parameter is not None and not _expression_influence(row, parameter):
                        continue
                    signal = deepcopy(row)
                    signal.update(path=[], excluded_paths=[], relation="possible" if "possible" in (relation, row["relation"]) else "derived")
                if signal is not None:
                    self.emit(target, signal, "supported_expression_" + relation if parameter is not None and relation in {"derived", "possible"} else relation, identity)

    @staticmethod
    def _compare(signal, demands, limits):
        overlap = [(identity, demand_overlap(signal, demand)) for identity, demand in demands]
        if any(kind == "retain" for _, kind in overlap):
            return "no_excess_established", "A task-preservation demand retains this information property or conservatively retains the overlapping range. This is not irreplacability.", overlap
        if limits:
            return "no_excess_established", "Relevant analysis limitations prevent a supported excess conclusion; missing demands are not evidence of removable content.", overlap
        if signal["relation"] != "direct":
            return "possible_excess", "Only a derived or possible relation to declared sensitive information is established. This does not establish the original sensitive value as payload content or independently establish that this subpart is sensitive.", overlap
        if not demands:
            return "no_excess_established", "No positive task-preservation demand was established for this payload slot. Absence of a demand is not a deletion certificate.", overlap
        if any(kind == "structure" for _, kind in overlap):
            return "no_excess_established", "The current demand preserves presence or collection structure. Removing the field or element is not supported; reducing its value needs a property-preserving representation.", overlap
        if not signal["path"] or signal["property"] != "value" or type(signal["path"][-1]) is not str or signal["excluded_paths"]:
            return "no_excess_established", "The declaration describes a whole, member or structural information range. No supported disjoint field-value reduction has been established.", overlap
        return "excess_supported", "The declared field value is directly present at this boundary and is disjoint from all applicable task-preservation demands under the supported relations. Preserve every demanded field, structure and condition; this does not remove the whole action.", overlap

    def solve(self):
        from .constraint_preservation import ConstraintAnalysis
        constraints = ConstraintAnalysis(self.engine)
        self.track()
        for diagnostic in self.demand["diagnostics"]:
            self.diagnostics[diagnostic["id"]] = {k: diagnostic[k] for k in
                ("id", "code", "reason", "instruction_id", "operation_id", "blocking")}
        sinks, used_sensitivity, used_demands = [], set(), set()
        for sink in self.demand["sinks"]:
            relevant = set(self.engine.index.slice(sink["boundary"])["usage_context"]["instructions"])
            relevant.update(self.engine.ops[key]["position"]["instruction_id"] for key in
                self.engine.index.slice(sink["boundary"])["backward_slice"]["operations"])
            limits = sorted(set(sink["limitations"]) | {identity for identity, diagnostic in self.diagnostics.items()
                if diagnostic["blocking"] and (diagnostic["instruction_id"] is None or diagnostic["instruction_id"] in relevant)})
            reviews = []
            for payload in sink["actual_payload"]:
                key = payload["operation_id"]
                record = self.engine.ops[key]["record"]
                for slot in payload_input_indices(record):
                    demands = [(identity, self.demand["derivations"][identity]) for identity in
                        [*sink["demanded_information"], *sink["conservative_retention"]]
                        if self.demand["derivations"][identity]["node"]["kind"] == "op_input"
                        and self.demand["derivations"][identity]["node"]["operation_id"] == key
                        and self.demand["derivations"][identity]["node"]["slot"] == slot]
                    for data_id in record["inputs"][slot]:
                        candidates = []
                        for identity in sorted(self.by_data[data_id]):
                            row = self.rows[identity]
                            if any(other != identity and dominates(self.rows[other], row)
                                   and (not dominates(row, self.rows[other]) or other < identity)
                                   for other in self.by_data[data_id]):
                                continue
                            candidates.append(identity)
                        for identity in candidates:
                            signal = self.rows[identity]
                            conclusion, reason, overlaps = self._compare(signal, demands, limits)
                            constraint_refs = []
                            if conclusion == "excess_supported":
                                constraint_refs, preserved = constraints.evaluate(key, slot, data_id, signal["path"])
                                if not preserved:
                                    conclusion = "no_excess_established"
                                    reason = "Task demands permit this field reduction, but preservation of every applicable constraint has not been established. This is not a necessity or violation proof."
                            row = {"operation_id": key, "input_index": slot,
                                   "derivation_id": identity, "conclusion": conclusion, "reason": reason,
                                   "demand_refs": sorted(d for d, _ in overlaps),
                                   "constraint_refs": constraint_refs,
                                   "reduction": {"kind": "exclude_field", "path": deepcopy(signal["path"])} if conclusion == "excess_supported" else None}
                            reviews.append({"id": _id("data_review_", [sink["id"], key, slot, identity]), **row})
                            used_sensitivity.add(identity)
                            used_demands.update(row["demand_refs"])
            sinks.append({k: deepcopy(sink[k]) for k in ("id", "boundary", "actual_payload", "related_requirements")} | {"limitations": limits, "data_reviews": reviews})
        def closure(ids, records):
            todo = list(ids)
            while todo:
                for parent in records[todo.pop()]["parents"]:
                    if parent not in ids:
                        ids.add(parent)
                        todo.append(parent)
            return {k: {field: deepcopy(value) for field, value in records[k].items()
                        if field != "id"} for k in sorted(ids)}
        partial = (self.demand["status"] == "partial" or any(d["blocking"] for d in self.diagnostics.values())
                   or any(c["status"] == "not_established" for c in constraints.checks.values()))
        return {"schema_version": "skillflow-sensitivity-review-v4", "status": "partial" if partial else "complete",
            "sinks": sinks, "derivations": {"sensitivity": closure(used_sensitivity, self.rows),
                "demand": closure(used_demands, self.demand["derivations"])},
            "constraints": constraints.to_dict(),
            "diagnostics": [self.diagnostics[k] for k in sorted(self.diagnostics)],
            "coverage": {"declared_scopes": len({canonical_sha256([r["instruction_id"], r["scope_path"]]) for r in self.declarations.values()}),
                "declarations": len(self.declarations), "resolved_declarations": len(self.resolved),
                "sinks": len(sinks), "expected_sinks": len(self.engine.facts.sinks),
                "sensitivity_basis": "declared_ranges_only", "demand_status": self.demand["status"]}}
