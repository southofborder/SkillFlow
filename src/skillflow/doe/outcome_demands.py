"""Demand transfers through one recorded protected-call outcome."""

from collections import defaultdict

from skillflow.propagation.loop_domain import key as producer_key
from skillflow.propagation.selectors import consistent_bindings


NO_RECORDED_CONTROL_OUTCOME = "No recorded protected outcome establishes this control path."


def outcome_dispatches(instructions):
    return {ir["metadata"]["outcome_dispatch"]["producer"]: ir["id"]
            for ir in instructions.values() if "outcome_dispatch" in ir.get("metadata", {})}


def output_slots(binding):
    return {binding[field]: role for field, role in (
        ("completion_index", "completion"), ("return_index", "return"), ("exception_index", "throw"))
        if binding.get(field) is not None}


def intrinsic_exception(ref):
    return ref == {"kind": "local", "name": "__raised__"}


def _route(data, identity):
    item = data[identity]
    content = item["content"]
    scope = content.get("scope", "")
    if content["form"] != "loop_summary" or not scope.startswith("selector-route:"):
        return identity, content.get("bindings", {})
    base = scope.removeprefix("selector-route:")
    expected_site = producer_key(["selector-route", base])
    variants = content["variants"]
    bindings = content["bindings"]
    if (base in data and content.get("producer") == expected_site and item["origin"].get("at") == expected_site
            and item["origin"].get("inputs") == [base] and consistent_bindings(bindings) and variants
            and all(variant["inputs"] == [base]
                    and variant["content"] == {"form": "selection", "base": base, "path": []} for variant in variants)):
        return base, bindings
    return identity, content.get("bindings", {})


class OutcomeDemands:
    def __init__(self, engine):
        self.engine = engine
        self.slots, self.rows, self.cases = {}, defaultdict(list), {}
        self.dispatches = outcome_dispatches(getattr(engine.index, "instructions", {}))
        self.operations = defaultdict(list)
        for ir, spec in engine.compiled["ir_semantics"].items():
            for binding in spec.get("outcome_bindings", []):
                for slot, role in output_slots(binding).items():
                    self.slots[(ir, slot)] = (binding, role)
                for event in spec["events"]:
                    case = event.get("case")
                    if case and case["group"] == binding["group"]:
                        self.cases[(ir, case["group"], case["id"])] = case
            for row in engine.index.records.get(ir, {}).get("outcomes", []):
                self.rows[(ir, row["group"])].append(row)
        for key, op in engine.ops.items():
            case = op.get("case")
            if case and op["scope"] is None and not op["generated"]:
                self.operations[(op["position"]["instruction_id"], case["group"], case["id"])].append(key)

    def candidates(self, ir, slot):
        binding, role = self.slots[(ir, slot)]
        declarations = {case["case_id"]: case for case in binding["cases"]}
        for row in self.rows[(ir, binding["group"])]:
            declaration = declarations[row["case_id"]]
            if role == "completion" or role == declaration["disposition"]:
                yield row, declaration, row["completion"] if role == "completion" else row["values"]

    def selected(self, ir, slot, information):
        selected = set(information.get("outcome_data_ids", []))
        return [(row, declaration, values) for row, declaration, values in self.candidates(ir, slot)
                if values and (not selected or selected.intersection(values))]

    def matching_versions(self, consumers, candidates):
        """Accept version identity or an exact, field-preserving typed-route view."""
        return self.partition_versions(consumers, candidates)[0]

    def partition_versions(self, consumers, candidates):
        """Separate exact producer matches from consumed versions without a proven origin."""
        data = self.engine.index.data
        candidates = set(candidates)
        routes = defaultdict(list)
        for candidate in candidates:
            base, bindings = _route(data, candidate)
            routes[base].append((candidate, bindings))
        matched, untraceable = set(), set()
        for consumer in consumers:
            if consumer in candidates:
                matched.add(consumer)
                continue
            base, bindings = _route(data, consumer)
            possible = [candidate for candidate, prior in routes[base]
                        if all(bindings.get(axis) == value for axis, value in prior.items())]
            if base != consumer and len(possible) == 1:
                matched.add(possible[0])
                continue
            untraceable.add(consumer)
        return sorted(matched), untraceable

    def unavailable(self, ir, requirement, parent, reason):
        from .demand_engine import need

        engine = self.engine
        diagnostic = engine.diagnostic("unavailable_outcome_dependency", reason, ir, requirement, affected=[ir])
        for node in self.declared_inputs(ir):
            engine.emit(node, need(), requirement, "outcome_gap:" + diagnostic, parent, True)

    def transfer(self, ir, slot, information, requirement, parent, conservative):
        from .demand_engine import need

        engine = self.engine
        binding, role = self.slots[(ir, slot)]
        candidates = self.selected(ir, slot, information)
        information = {key: value for key, value in information.items() if key != "outcome_data_ids"}
        for row, declaration, values in candidates:
            coordinate = (ir, row["group"], row["case_id"])
            guard = self.cases[coordinate].get("guard")
            exact_guard = guard and row["selectors"] and engine._case_control(
                ir, guard, requirement, parent, conservative, data_ids=row["selectors"])
            if not exact_guard and (role == "completion" or len(binding["cases"]) > 1):
                self._uncertain(coordinate, requirement, parent,
                    "Preserving this outcome requires a completion decision whose selector is not established.")

            if role == "completion":
                continue
            value = declaration["value"]
            if intrinsic_exception(value):
                self._uncertain(coordinate, requirement, parent,
                    "The actual raised value is recorded, but its requested fields have no exact transfer.")
                continue
            if not engine.emit_ref(value, ir, None, information, requirement, "protected_outcome_value",
                                   parent, conservative, data_ids=values):
                self._uncertain(coordinate, requirement, parent,
                    "The recorded outcome value has no matching scoped producer.")
            else:
                engine._public_return_observers(ir, value, information, requirement, parent, conservative,
                                                case_id=row["case_id"], data_ids=values)

        if not candidates:
            self.unavailable(ir, requirement, parent,
                             "The requested protected outcome has no matching recorded version.")

    def declared_inputs(self, ir):
        engine = self.engine
        return [engine.node_at("ir_input", ir, slot=slot) for slot, operand in
                enumerate(engine.index.instructions[ir]["inputs"]) if operand["type"] != "literal"]

    def routed_choices(self, producer, target_block):
        terminator = self.dispatches.get(producer)
        recorded = self.engine.index.records.get(terminator, {}).get("outcome_routes", [])
        for route in recorded:
            if target_block in self.engine.index.reachable[route["target"]]:
                group = route["group"]
                coordinate = producer, group, route["case_id"]
                for trace in self.rows[(producer, group)]:
                    if trace["case_id"] == route["case_id"]:
                        yield coordinate, self.cases[coordinate].get("guard"), trace

    def dispatch_controls(self, producer, target_block, requirement, parent, conservative):
        engine = self.engine
        relevant = list(self.routed_choices(producer, target_block))
        if not relevant:
            self.unavailable(producer, requirement, parent, NO_RECORDED_CONTROL_OUTCOME)
            return
        for coordinate, guard, trace in relevant:
            if guard is not None and engine._case_control(producer, guard, requirement, parent, conservative,
                    rule="outcome_dispatch_selector", data_ids=trace["selectors"]):
                continue
            self._uncertain(coordinate, requirement, parent,
                "The routed case is known, but its cause has no source-backed selector.")

    def possible_inputs(self, coordinate):
        engine = self.engine
        ir, _, _ = coordinate
        operations = self.operations[coordinate]
        if not operations:
            return self.declared_inputs(ir)
        return [engine.node_at("op_input", ir, operation, slot)
                for operation in operations for slot in engine.slots(operation)]

    def _uncertain(self, coordinate, requirement, parent, reason):
        from .demand_engine import need

        engine = self.engine
        ir, _, case = coordinate
        diagnostic = engine.diagnostic("unresolved_outcome_dependency",
            f"{reason} Case {case} at instruction {ir}.", ir, requirement, affected=[ir])
        for node in self.possible_inputs(coordinate):
            engine.emit(node, need(), requirement, "outcome_gap:" + diagnostic, parent, True)


def validate_selected_versions(derivations, engine):
    """Recheck a saved subset against the consuming CFG operand or case evidence."""
    for item in derivations.values():
        if not item.get("outcome_data_ids"):
            continue
        node = item["node"]
        ir, slot = node["instruction_id"], node["slot"]
        selected = set(item["outcome_data_ids"])
        parents = [derivations[key] for key in item["parents"]]
        actual_node = engine.node_at(node["kind"], ir, slot=slot)
        if actual_node is None or engine.nodes[actual_node] != node:
            raise ValueError("Outcome demand operand differs from recorded Data bindings")
        if node["kind"] == "ir_output":
            if (ir, slot) not in engine.outcomes.slots or "cfg_result_use" not in item["rules"]:
                raise ValueError("Outcome result selection has no protected output binding")
            expected = node["data_ids"]
            for parent in parents:
                source = parent["node"]
                if source["kind"] == "ir_input":
                    operand = engine.index.instructions[source["instruction_id"]]["inputs"][source["slot"]]
                    if operand["type"] == "result" and engine.definitions[operand["identifier"]] == (ir, slot):
                        uses = parent.get("outcome_data_ids", source["data_ids"])
                        if selected == set(engine.outcomes.matching_versions(uses, expected)):
                            break
            else:
                raise ValueError("Outcome result selection differs from the consuming operand")
        else:
            for parent in parents:
                source = parent["node"]
                if "outcome_dispatch_selector" in item["rules"] and source["instruction_id"] in engine.index.ir_block:
                    from .selector_demands import reference
                    target_block = engine.index.ir_block[source["instruction_id"]]
                    if any(guard and guard["input_index"] == slot
                           and item.get("selector_ref") == reference(ir, {"kind": "input", "index": slot}, guard)
                           and selected == set(trace["selectors"]).intersection(node["data_ids"])
                           for _, guard, trace in engine.outcomes.routed_choices(ir, target_block)):
                        break
                parent_slot = source["slot"]
                if source["kind"] != "ir_output" or source["instruction_id"] != ir or (ir, parent_slot) not in engine.outcomes.slots:
                    continue
                for row, declaration, versions in engine.outcomes.selected(ir, parent_slot, parent):
                    case = engine.outcomes.cases[(ir, row["group"], row["case_id"])]
                    if ("typed_case_selector" in item["rules"] and case.get("guard", {}).get("input_index") == slot
                            and selected == set(row["selectors"]).intersection(node["data_ids"])):
                        break
                    value = declaration.get("value")
                    if ("protected_outcome_value" in item["rules"] and value and not intrinsic_exception(value)
                            and actual_node in engine.resolve(value, ir)
                            and selected == set(versions).intersection(node["data_ids"])):
                        break
                else:
                    continue
                break
            else:
                raise ValueError("Outcome input selection has no matching recorded case evidence")
