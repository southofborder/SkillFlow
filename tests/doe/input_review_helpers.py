"""Explicit synthetic decisions for the current finite review protocol."""
from copy import deepcopy
import json


def review_prompt_payload(prompt):
    """Decode the explicit display generation used by this injected client."""
    from skillflow.document_guided.review_display import DISPLAY_IDENTITY, expand_review_payload
    payload = json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n", 1)[1])[0]
    if payload.get("format") == DISPLAY_IDENTITY:
        return expand_review_payload(payload)
    return payload


def checks_for_inventory(inventory, evidences, *, status="accepted"):
    checks = []
    layouts = {row["obligation_id"]: row for row in inventory.get("contracts", [])}
    for row in inventory["obligations"]:
        scopes = row.get("scopes", layouts.get(row["id"], {}).get("scopes", []))
        effective = "rejected" if row["contract_id"] is None else status
        check = {"obligation_id": row["id"], "contract_id": row["contract_id"], "status": effective,
                 "reason": "The synthetic source specifies this exact input relation and excluded information.",
                 "evidences": deepcopy(evidences), "scope_checks": []}
        if effective != "accepted":
            group = {"scope_ids": [scope["id"] for scope in scopes], "status": effective,
                     "reason": "The synthetic source does not establish the represented field dependency.",
                     "evidences": deepcopy(evidences)}
            if effective == "unresolved":
                group["gap"] = {"code": "ambiguous_semantics",
                    "reason": "The fallback choice between primary and secondary labels is unspecified.",
                    "missing": "Whether an absent primary label selects the secondary label.",
                    "resolution": "Specify the label selection when the primary field is absent.",
                    "evidences": deepcopy(evidences)}
            check["scope_checks"] = [group]
        checks.append(check)
    return checks


def projection_checks(inventory, evidences):
    return [{"scope_ids": [row["id"] for row in inventory["projections"]], "status": "accepted",
             "reason": "The synthetic interface supports selecting the exact returned ranges independently.",
             "evidences": deepcopy(evidences)}] if inventory["projections"] else []


def retained_gap_checks(material, cited):
    return {"gap_checks": [{"gap_id": row["id"], "disposition": "retain",
        **({"masked_boundary": "none", "cfg_action_missing": False} if row.get("kind") == "placeholder" else {}),
        "reason": "The fixture provides no implementation for the source action at " + row["instruction_id"] + ".",
        "affected": "The caller cannot determine the return or effect at " + row["instruction_id"] + ".",
        "source_refs": [{key: value for key, value in cited[0].items() if key != "reason"}]}
        for row in material.get("processing_gap_inventory", [])]} if material.get("processing_gap_inventory") else {}


def source_review_response(material, findings):
    """Explicit current fixture response, keeping representation objections local."""
    inventory = material["input_contract_inventory"]
    cited = [{"file": next(iter(material["files"])), "start_line": 1, "end_line": 1,
              "reason": "The synthetic review rechecks this source-defined operation relationship."}]
    accepted = checks_for_inventory(inventory, cited)
    rejected = {row["obligation_id"]: row for row in checks_for_inventory(inventory, cited, status="rejected")}
    for index, check in enumerate(accepted):
        protected = material["input_contract_targets"].get(check["obligation_id"], [])
        if any(actual == target or actual.startswith(target + "/") or target.startswith(actual + "/")
               for finding in findings for actual in finding["target_ids"] for target in protected):
            accepted[index] = rejected[check["obligation_id"]]
    return {**retained_gap_checks(material, cited), "outcome": "completed", "findings": deepcopy(findings), "input_contract_checks": accepted,
            "input_projection_checks": projection_checks(inventory, cited), "source_input_findings": []}


def accepted_prompt_review(prompt, *, evidences=None):
    payload = review_prompt_payload(prompt)
    inventory = payload["input_contract_inventory"]
    cited = deepcopy(evidences) if evidences is not None else [
        {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
         "reason": "The authored synthetic source specifies these exact input relationships."}]
    return {**retained_gap_checks(payload, cited), "outcome": "completed", "findings": [], "input_contract_checks": checks_for_inventory(inventory, cited),
            "input_projection_checks": projection_checks(inventory, cited), "source_input_findings": []}
