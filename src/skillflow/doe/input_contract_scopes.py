"""Finite source-review obligations and scopes, derived without Task demands."""
from __future__ import annotations

from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.references import target_key


def _identity(prefix, value):
    return prefix + canonical_sha256(value)[:20]


def input_contract_review_inventory(*, cfg, raw_annotation, compiled, mapping=None):
    """Derive required attachments and review coordinates from selected material."""
    if cfg is None or raw_annotation is None or compiled is None:
        return {"available": False, "obligations": [], "contracts": [], "projections": []}
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.input_requirements import expected_input_contract_obligations
    targets = build_demand_target_index(cfg, raw_annotation)
    exact = {target_key(row["target"]) for row in compiled.get("expressions", [])}
    obligations = expected_input_contract_obligations(targets, compiled["locations"], exact_expression_targets=exact)
    entries = {(row["kind"], row["instruction_id"], tuple(row["raw_path"])): row
               for row in compiled.get("input_contracts", [])}
    if len(entries) != len(compiled.get("input_contracts", [])):
        raise ValueError("Input contracts repeat an actual operation")
    used, contracts = set(), []
    for obligation in obligations:
        entry = entries.get((obligation["kind"], obligation["instruction_id"], tuple(obligation["raw_path"])))
        if obligation.get("contract_id") != (entry or {}).get("id"):
            raise ValueError("Expected input contract differs from the selected compiled attachment")
        obligation["contract_id"] = (entry or {}).get("id")
        if entry is not None:
            used.add(entry["id"])
        contracts.append(_contract_layout(obligation, entry))
    if used != {row["id"] for row in entries.values()}:
        raise ValueError("A supplied input contract is outside the expected operation inventory")
    projections = _projection_inventory(obligations, entries)
    return {"available": True, "obligations": obligations, "contracts": contracts, "projections": projections}


def _contract_layout(obligation, entry):
    result = {"obligation_id": obligation["id"], "contract_id": (entry or {}).get("id"),
              "kind": obligation["kind"], "scopes": [], "rules": [], "inputs": [], "output_parts": None}

    def scope(kind, coordinates, **description):
        identity = _identity("input_review_scope_", [obligation["id"], (entry or {}).get("id"), kind, coordinates])
        result["scopes"].append({"id": identity, "kind": kind, **deepcopy(description)})
        return identity

    if entry is None:
        result["missing_scope_id"] = scope("missing_attachment", [])
        return result
    contract = entry["contract"]

    def inputs(rows, rule_index=None, output=None):
        value = []
        for row in rows:
            index = row["input_index"]
            description = {"input_index": index, **({"output": output} if output is not None else {})}
            required = []
            for number, information in enumerate(row["required"]):
                effective = ([{"property": "presence", "path": information["path"], "when": "always"},
                              {"property": information["property"], "path": information["path"], "when": "present"}]
                             if information.get("if_present") else None)
                reference = scope("required", [rule_index, index, number], **description,
                                  information=information, **({"effective": effective} if effective else {}))
                required.append({"information": deepcopy(information), "scope_id": reference})
            unknown = []
            for number, gap in enumerate(row.get("unresolved_ranges", [])):
                reference = scope("unresolved_range", [rule_index, index, number], **description,
                                  information=gap["information"])
                unknown.append({"information": deepcopy(gap["information"]), "authored_gap": deepcopy(gap["gap"]),
                                "scope_id": reference})
            reference = scope("remainder", [rule_index, index], **description)
            value.append({"input_index": index, "required": required, "unresolved_ranges": unknown,
                          "remainder": {"authored": {"status": row["remainder"], "reason": row["reason"],
                              **({"gap": deepcopy(row["gap"])} if row.get("gap") is not None else {})}, "scope_id": reference}})
        return value

    if entry["kind"] == "compute":
        for number, rule in enumerate(contract["rules"]):
            result["rules"].append({"output": deepcopy(rule["output"]),
                "scope_id": scope("rule", [number], output=rule["output"]),
                "inputs": inputs(rule["inputs"], number, rule["output"])})
        if contract.get("output_parts") is not None:
            result["output_parts"] = {"parts": deepcopy(contract["output_parts"]),
                "scope_id": scope("output_parts", [], parts=contract["output_parts"])}
    else:
        result["interface_scope_id"] = scope("interface", [])
        result["inputs"] = inputs(contract["inputs"])
    return result


def _projection_inventory(obligations, entries):
    groups = {}
    for row in obligations:
        if row["kind"] == "tool" and row.get("request_pair_id") is not None:
            groups.setdefault(row["request_pair_id"], []).append(row)
    result, seen = [], set()
    for obligation in obligations:
        entry = entries.get((obligation["kind"], obligation["instruction_id"], tuple(obligation["raw_path"])))
        capabilities = (entry or {}).get("contract", {}).get("acquisition_projections", [])
        if not capabilities:
            continue
        pair_id = obligation.get("request_pair_id")
        if pair_id in seen:
            continue
        seen.add(pair_id)
        pair = groups.get(pair_id, [])
        requests = [row for row in pair if row.get("operation") == "deliver"]
        responses = [row for row in pair if row.get("operation") == "receive"]
        if len(requests) != 1 or len(responses) != 1:
            raise ValueError("Acquisition projection requires one exact request-response pair")
        request, response = requests[0], responses[0]
        pair_entries = [entries[(row["kind"], row["instruction_id"], tuple(row["raw_path"]))] for row in pair]
        if any(row["contract"].get("acquisition_projections", []) != capabilities for row in pair_entries):
            raise ValueError("Paired acquisition projection claims differ")
        for number, capability in enumerate(capabilities):
            identity = _identity("input_projection_", [pair_id, number, capability])
            result.append({"id": identity, "scope_id": identity, "request_pair_id": pair_id, "capability_index": number,
                "contract_ids": sorted(row["id"] for row in pair_entries),
                "request": {"instruction_id": request["instruction_id"], "raw_path": deepcopy(request["raw_path"])},
                "response": {"instruction_id": response["instruction_id"], "raw_path": deepcopy(response["raw_path"])},
                "capability": deepcopy(capability)})
    return sorted(result, key=lambda row: row["id"])


def compact_review_inventory(inventory, target_ids):
    """Coordinates and effective semantics only; contract bodies stay in annotation."""
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    obligations = []
    for row in inventory["obligations"]:
        layout = layouts[row["id"]]
        obligations.append({"id": row["id"], "kind": row["kind"], "contract_id": row["contract_id"],
            "target_id": target_ids[row["id"]], "attachment": row["attachment"], "input_count": row["input_count"],
            "scopes": deepcopy(layout["scopes"])})
    projections = [{"id": row["id"], "contract_ids": row["contract_ids"], "request": row["request"],
                    "response": row["response"], "capability_index": row["capability_index"]}
                   for row in inventory["projections"]]
    return {"available": inventory["available"], "obligations": obligations, "projections": projections}


def reviewed_contract_scopes(receipt, contract_id):
    core = (receipt or {}).get("review_core", {})
    layout = next((row for row in core.get("inventory", {}).get("contracts", [])
                   if row["contract_id"] == contract_id), None)
    if (layout is None or core.get("status") not in {"complete", "partial"}
            or layout["obligation_id"] in core.get("blocked_obligation_ids", [])):
        return {"available": False, "contract_id": contract_id}
    decisions = core.get("scope_decisions", {})
    if any(row["id"] not in decisions for row in layout["scopes"]):
        return {"available": False, "contract_id": contract_id}

    def project(value):
        if isinstance(value, list):
            return [project(row) for row in value]
        if not isinstance(value, dict):
            return deepcopy(value)
        result = {key: project(row) for key, row in value.items() if key not in {"scopes", "scope_id", "interface_scope_id"}}
        if "scope_id" in value:
            result["decision"] = deepcopy(decisions[value["scope_id"]])
        if "interface_scope_id" in value:
            result["interface_decision"] = deepcopy(decisions[value["interface_scope_id"]])
        return result
    return {"available": True, **project(layout)}


def reviewed_acquisition_projections(receipt, request_instruction_id, request_raw_path,
                                    response_instruction_id, response_raw_path):
    core = (receipt or {}).get("review_core", {})
    if core.get("status") not in {"complete", "partial"}:
        return []
    result = []
    for row in core.get("inventory", {}).get("projections", []):
        if row["id"] in core.get("blocked_projection_ids", []):
            continue
        if (row["request"] == {"instruction_id": request_instruction_id, "raw_path": list(request_raw_path)}
                and row["response"] == {"instruction_id": response_instruction_id, "raw_path": list(response_raw_path)}):
            decision = core.get("projection_decisions", {}).get(row["scope_id"])
            if decision is not None:
                result.append({**deepcopy(row), "decision": deepcopy(decision)})
    return result
