"""Reviewed semantic transfer, without changing actual forward observations."""
from __future__ import annotations

from copy import deepcopy

from skillflow.common.recording import canonical_sha256


def prefix(a, b):
    return len(a) <= len(b) and all(x == y or x == {"kind": "each"} and type(y) is int
        or y == {"kind": "each"} and type(x) is int
        or x == {"kind": "each"} and isinstance(y, dict) and y.get("kind") == "element"
        or y == {"kind": "each"} and isinstance(x, dict) and x.get("kind") == "element" for x, y in zip(a, b))


def covers(a, b):
    return len(a) <= len(b) and all(x == y or x == {"kind": "each"}
        and (type(y) is int or isinstance(y, dict) and y.get("kind") == "element") for x, y in zip(a, b))


def overlaps(a, b):
    return prefix(a, b) or prefix(b, a)


def selector(need):
    return {"property": need["property"],
            "path": ([{"kind": "each"}] if need.get("each") else []) + list(need.get("path", []))}


class InputContracts:
    """Resolve only checks bound to the selected source and annotation."""

    def __init__(self, engine, receipt=None, *, archived_v12=False, archived_v13=False, archived_v14=False):
        self.engine = engine
        self.entries = {(row["instruction_id"], tuple(row["raw_path"])): row
                        for row in engine.compiled.get("input_contracts", [])}
        self.receipt = None
        self.checks = {}
        self.scopes = {}
        self.obligations = {}
        self.obligation_checks = {}
        if receipt is not None:
            from .input_contract_review import checked_input_contract_review
            from skillflow.propagation.contracts.joint import joint_source_files
            self.receipt = checked_input_contract_review(receipt,
                files=joint_source_files(engine.annotation["material"]), cfg=engine.index.cfg,
                annotation=engine.annotation, archived_v12=archived_v12, archived_v13=archived_v13, archived_v14=archived_v14)
            self.checks = {row["contract_id"]: row for row in self.receipt["checks"] if row["contract_id"] is not None}
            self.obligation_checks = {row["obligation_id"]: row for row in self.receipt["checks"]}
            self.obligations = {(row["instruction_id"], tuple(row["raw_path"])): row
                                for row in self.receipt["review_core"]["inventory"]["obligations"]}
            from .input_contract_review import reviewed_contract_scopes
            self.scopes = {entry["id"]: reviewed_contract_scopes(self.receipt, entry["id"])
                           for entry in self.entries.values()}

    def entry(self, key):
        info = self.engine.ops[key]
        return self.entries.get((info["position"]["instruction_id"], info["raw_op"]))

    def accepted(self, entry):
        return bool(entry and self.checks.get(entry["id"], {}).get("status") == "accepted"
                    and self.reviewed(entry)["available"])

    def reviewed(self, entry):
        return self.scopes.get((entry or {}).get("id"), {"available": False})

    def _gap(self, entry, key, output, reason, *, row=None, code="input_contract_unavailable",
             information=None, decision=None, no_inputs=False):
        info = self.engine.ops[key]
        obligation = self.obligations.get((info["position"]["instruction_id"], info["raw_op"]), {})
        pointer = (entry or obligation).get("raw_pointer", "/ir_semantics/" + info["position"]["instruction_id"])
        gap = (decision or {}).get("gap") or (row or {}).get("gap", {})
        excluded = [r["path"] for r in (row or {}).get("required", []) if r["property"] == "value"]
        excluded += [r["information"]["path"] for r in (row or {}).get("unresolved_ranges", [])
                     if r["information"]["property"] == "value"]
        return {"code": code, "reason": reason,
            "missing": gap.get("missing", "A reviewed transfer for this exact output information."),
            "resolution": gap.get("resolution", "Supply and review the missing output-to-input relationship."),
            "pointer": pointer, "output": deepcopy(output),
            "input_index": None if row is None else row["input_index"],
            "property": (information or {}).get("property", "value"),
            "path": deepcopy((information or {}).get("path", [])),
            "excluded_paths": [] if information is not None else deepcopy(excluded),
            "no_inputs": no_inputs,
            "contract_id": None if entry is None else entry["id"],
            "scope_id": (decision or {}).get("scope_id"),
            "information_bound": bool(information is not None and decision
                                      and decision["status"] == "accepted"),
            "evidences": deepcopy(gap.get("evidences") or (decision or {}).get("evidences", []))}

    def _rules(self, entry, output, exclusions):
        contract = entry["contract"]
        if entry["kind"] == "tool":
            return [contract]
        rules = {canonical_sha256(row["output"]): row for row in contract["rules"]}
        exact = rules.get(canonical_sha256(output))
        if exact is not None and not exclusions:
            return [exact]
        parts = contract.get("output_parts")
        if output == {"property": "value", "path": []} and parts:
            selected = []
            for part in parts:
                if any(covers(excluded, part["path"]) for excluded in exclusions):
                    continue
                # A partial exclusion inside a component needs its own rule.
                if any(overlaps(part["path"], excluded) for excluded in exclusions):
                    return None
                selected.append(rules[canonical_sha256(part)])
            return selected
        return None

    def transfer(self, key, need):
        entry, output = self.entry(key), selector(need)
        result = {"requirements": [], "gaps": [], "contract_ids": []}
        from .review_barriers import operation_barriers, barrier_reason
        barriers = operation_barriers(self.engine, key)
        if barriers:
            result["gaps"] = [self._gap(entry, key, output, barrier_reason(barrier),
                code="input_contract_review_transfer") for barrier in barriers]
            return result
        reviewed = self.reviewed(entry)
        if not reviewed["available"]:
            info = self.engine.ops[key]
            obligation = self.obligations.get((info["position"]["instruction_id"], info["raw_op"]), {})
            check = self.checks.get(entry["id"], {}) if entry else self.obligation_checks.get(obligation.get("id"), {})
            reason = (check.get("reason") or "The selected operation has no accepted input-requirement review.")
            result["gaps"].append(self._gap(entry, key, output, reason,
                code="input_contract_rejected" if check.get("status") == "rejected" else "input_contract_unavailable"))
            return result
        result["contract_ids"] = [entry["id"]]
        exclusions = ([([{ "kind": "each"}] if need.get("each") else []) + p
                       for p in need.get("excluded_paths", [])])
        rules = self._rules(entry, output, exclusions)
        if rules is None:
            result["gaps"].append(self._gap(entry, key, output,
                "No rule covers output selector " + str(output) + " with exclusions " + str(exclusions)
                + "; provide an exact rule or a reviewed exhaustive output decomposition.", code="input_contract_output_gap"))
            return result
        requirements = {}
        def review_gap(decision, *, row=None, information=None, no_inputs=False):
            if decision["status"] == "accepted":
                return False
            result["gaps"].append(self._gap(entry, key, output, decision["reason"], row=row,
                information=information, decision=decision, no_inputs=no_inputs,
                code="input_contract_rejected" if decision["status"] == "rejected" else "input_contract_review_gap"))
            return True

        whole = output == {"property": "value", "path": []}
        used_parts = whole and entry["kind"] == "compute" and (exclusions or not any(
            rule["output"] == output for rule in entry["contract"]["rules"]))
        if used_parts and reviewed.get("output_parts"):
            review_gap(reviewed["output_parts"]["decision"], no_inputs=True)
        reviewed_rules = {canonical_sha256(rule["output"]): rule for rule in reviewed.get("rules", [])}
        for rule in rules:
            checked = (reviewed if entry["kind"] == "tool" else reviewed_rules[canonical_sha256(rule["output"])])
            review_gap(checked["interface_decision"] if entry["kind"] == "tool" else checked["decision"],
                       no_inputs=True)
            checked_inputs = {row["input_index"]: row for row in checked["inputs"]}
            for row in rule["inputs"]:
                checked_row = checked_inputs[row["input_index"]]
                for barrier in operation_barriers(self.engine, key, role="argument", slot=row["input_index"]):
                    if barrier.get("range"):
                        information = barrier["range"]["information"]
                        result["gaps"].append(self._gap(entry, key, output, barrier_reason(barrier),
                            row=row, information=information, code="input_contract_review_range"))
                for wanted_row in checked_row["required"]:
                    wanted = wanted_row["information"]
                    if review_gap(wanted_row["decision"], row=row, information=wanted):
                        continue
                    value = {"input_index": row["input_index"], **deepcopy(wanted)}
                    requirements[canonical_sha256(value)] = value
                for uncertain in checked_row.get("unresolved_ranges", []):
                    if not review_gap(uncertain["decision"], row=row, information=uncertain["information"]):
                        authored = uncertain["authored_gap"]
                        result["gaps"].append(self._gap(entry, key, output, authored["reason"],
                            row={**row, "gap": authored}, information=uncertain["information"],
                            decision=uncertain["decision"], code="input_contract_semantic_gap"))
                remainder_gap = review_gap(checked_row["remainder"]["decision"], row=row)
                if not remainder_gap and row["remainder"] == "unresolved":
                    gap = self._gap(entry, key, output, row["gap"]["reason"], row=row,
                                    decision=checked_row["remainder"]["decision"], code="input_contract_semantic_gap")
                    result["gaps"].append(gap)
        result["requirements"] = [requirements[k] for k in sorted(requirements)]
        return result

    def influenced_outputs(self, key, input_slot, path):
        """Return complete affected output selectors, or None for a real gap."""
        from .review_barriers import operation_barriers
        if operation_barriers(self.engine, key, role="argument", slot=input_slot, information={"property": "value", "path": path}):
            return None
        entry = self.entry(key)
        reviewed = self.reviewed(entry)
        if not reviewed["available"]:
            return None
        contract = entry["contract"]
        from .sensitivity_engine import demand_overlap

        def intersects(information, *, excluded=(), certified=True):
            return demand_overlap({"property": "value", "path": path, "excluded_paths": []},
                {**information, "each": False, "excluded_paths": list(excluded),
                 "conservative": not certified}) != "none"

        def row_influence(row):
            changed = False
            accounted = []
            for required in row["required"]:
                information = required["information"]
                if information["property"] == "value":
                    accounted.append(information["path"])
                if intersects(information, certified=required["decision"]["status"] == "accepted"):
                    if required["decision"]["status"] != "accepted":
                        return None
                    changed = True
            for uncertain in row.get("unresolved_ranges", []):
                information = uncertain["information"]
                if information["property"] == "value":
                    accounted.append(information["path"])
                if intersects(information, certified=uncertain["decision"]["status"] == "accepted"):
                    return None
            remainder = row["remainder"]
            if (remainder["decision"]["status"] != "accepted" or remainder["authored"]["status"] == "unresolved"):
                if intersects({"property": "value", "path": []}, excluded=accounted):
                    return None
            return changed

        if entry["kind"] == "tool":
            affected = row_influence(next(r for r in reviewed["inputs"] if r["input_index"] == input_slot))
            return (None if affected is None else [{"property": "value", "path": []}] if affected else [])
        rules = {canonical_sha256(rule["output"]): rule for rule in reviewed["rules"]}
        parts = contract.get("output_parts")
        whole = rules.get(canonical_sha256({"property": "value", "path": []}))
        if parts and reviewed["output_parts"]["decision"]["status"] != "accepted":
            # The listed fields do not establish complete output coverage. A
            # separate whole-output rule can still provide that relationship.
            selected = [whole] if whole is not None else None
        else:
            selected = [rules[canonical_sha256(part)] for part in parts] if parts else ([whole] if whole else None)
        if selected is None:
            return None
        outputs = {}
        for rule in selected:
            row = next(r for r in rule["inputs"] if r["input_index"] == input_slot)
            affected = row_influence(row)
            if affected is None or affected:
                # A local uncertain relation can affect this exact output;
                # it does not implicate the operation's independent outputs.
                outputs[canonical_sha256(rule["output"])] = deepcopy(rule["output"])
        return [outputs[k] for k in sorted(outputs)]

    def references(self, key):
        entry = self.entry(key)
        return [entry["id"]] if self.reviewed(entry)["available"] else []
