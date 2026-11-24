"""Source-review obligations for every submitted whole-instruction gap."""
from collections import defaultdict
from copy import deepcopy
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from skillflow.common.recording import canonical_sha256
from .graph_facts import source_action_role
from skillflow.propagation.contracts.input_requirements import unspecific_gap_reason
from skillflow.common.source_evidence import json_pointer, SourceRef, StrictRecord, Text, validate_source_ref


class GapCheck(StrictRecord):
    gap_id: Text
    disposition: Literal["retain", "decompose"]
    reason: Text
    affected: Text
    source_refs: list[SourceRef] = Field(min_length=1)
    supported_action: Text | None = None
    masked_boundary: Literal["none", "call", "receive", "read", "write", "deliver", "branch", "loop"] | None = None
    cfg_action_missing: bool | None = None

    @model_validator(mode="after")
    def actionable(self):
        if unspecific_gap_reason(self.reason) or unspecific_gap_reason(self.affected):
            raise ValueError("Specify the source relation and affected behavior. Generic opacity cannot justify a gap.")
        if (self.disposition == "decompose") != (self.supported_action is not None):
            raise ValueError("A decompose decision must name the supported operation or local placeholder.")
        return self


def _placeholders(record, base=()):
    # Only visit operation containers. Literal data can contain arbitrary
    # "op" and "events" keys without representing executable processing.
    for field in ("segments", "cases", "body", "events", "ops", "atomic_ops"):
        rows = record.get(field, [])
        if not isinstance(rows, list):
            continue
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            path = (*base, field, i)
            if field in {"ops", "atomic_ops"}:
                if row.get("op") == "placeholder":
                    yield path, row
            else:
                yield from _placeholders(row, path)


def gap_inventory(material):
    gaps = material.get("processing_gaps", [])
    form = material.get("annotation") or material.get("fragments", {}).get("processing") or {}
    visible = {row["id"] for row in material.get("target_index", [])}
    selected = "target_index" not in material
    cfg = material.get("cfg") or {}
    cfg_sites = {op["id"]: ("cfg:" + json_pointer("blocks", block, "instructions", i), op)
                 for block, value in cfg.get("blocks", {}).items() for i, op in enumerate(value["instructions"])}
    table = []
    for i, gap in enumerate(gaps):
        if not gap.get("unmodeled"):
            continue
        owner = gap["instruction_id"]
        candidates = [f"annotation:/processing_gaps/{i}", f"fragment:processing:/processing_gaps/{i}"]
        target = (candidates[0] if selected and i < len(form.get("processing_gaps", [])) else
                  next((ref for ref in candidates if ref in visible), None))
        if target is None:
            # Validator quarantine is reviewed at its actual program-owned gap.
            for prefix in ("annotation:/_validation_gaps", "fragment:processing:/_validation_gaps"):
                for n, row in enumerate((material.get("annotation") or {}).get("_validation_gaps", [])):
                    if row.get("instruction_id") == owner and (selected or f"{prefix}/{n}" in visible):
                        target = f"{prefix}/{n}"
                        break
                if target:
                    break
        table.append({"id": f"gap_{i}_" + canonical_sha256(gap)[:16], "gap_index": i,
                      "instruction_id": owner, "target_id": target})
    for owner, record in form.get("ir_semantics", {}).items():
        cfg_target, instruction = cfg_sites.get(owner, (None, {}))
        actions = instruction.get("metadata", {}).get("source_actions", [])
        if not isinstance(record, dict):
            continue
        bindings = record.get("action_bindings") or {}
        for path, op in _placeholders(record):
            pointer = json_pointer("ir_semantics", owner, *path)
            targets = ["annotation:" + pointer, "fragment:processing:" + pointer]
            target = targets[0] if selected else next((item for item in targets if item in visible), None)
            attached = actions if len(actions) == 1 else [
                action for action in actions if list(path) in bindings.get(action["ref"], [])]
            if not actions:
                attached = [{"kind": instruction.get("opcode")}]
            roles = sorted({role for action in attached if (role := source_action_role(action))})
            table.append({"id": "placeholder_" + canonical_sha256([owner, path, op])[:24],
                          "kind": "placeholder", "instruction_id": owner, "target_id": target,
                          "cfg_target": cfg_target, "cfg_roles": roles})
    return table


def check_gaps(candidate, inventory, files):
    rows = candidate.get("gap_checks", [])
    expected = {row["id"]: row for row in inventory}
    valid, errors, findings = [], [], []
    seen = defaultdict(list)
    def error(path, reason):
        errors.append({"code": "processing_gap_review", "path": path, "message": reason})
    if not isinstance(rows, list):
        error("/gap_checks", "Supply the source-review decisions as an array.")
        rows = []
    for i, row in enumerate(rows):
        path = f"/gap_checks/{i}"
        key = row.get("gap_id") if isinstance(row, dict) else None
        if isinstance(key, str) and key in expected:
            seen[key].append(i)
        try:
            check = GapCheck.model_validate(row).model_dump(mode="json", exclude_none=True)
            if check["gap_id"] not in expected:
                raise ValueError("Unknown whole-instruction gap identity")
            subject = expected[check["gap_id"]]
            placeholder = subject.get("kind") == "placeholder"
            if placeholder and not ("masked_boundary" in check and "cfg_action_missing" in check):
                raise ValueError("Every placeholder decision requires masked_boundary and cfg_action_missing.")
            if not placeholder and ("masked_boundary" in check or "cfg_action_missing" in check):
                raise ValueError("Remove masked_boundary and cfg_action_missing from this whole-instruction gap.")
            if placeholder:
                masked = check["masked_boundary"]
                if masked == "none" and check["cfg_action_missing"]:
                    raise ValueError("Identify the actual omitted boundary before challenging the CFG.")
                if masked != "none" and check["disposition"] != "decompose":
                    raise ValueError("A placeholder masking a known boundary needs a source-backed repair.")
                if (masked != "none" and subject["cfg_roles"] and masked not in subject["cfg_roles"]
                        and not check["cfg_action_missing"]):
                    raise ValueError("The independent source boundary contradicts the bound CFG role; flag both owners.")
                if check["cfg_action_missing"] and subject.get("cfg_target") is None:
                    raise ValueError("The submitted graph correction has no real instruction target.")
            for ref in check["source_refs"]:
                validate_source_ref(ref, files)
            valid.append((i, check))
        except (ValueError, TypeError, ValidationError) as exc:
            error(path, str(exc))
    for key in expected:
        if not seen[key]:
            error("/gap_checks", "Missing whole-instruction source review for " + key)
        elif len(seen[key]) > 1:
            for i in seen[key]:
                error(f"/gap_checks/{i}", "Duplicate source review for " + key)
    usable = []
    for i, check in valid:
        ref = expected[check["gap_id"]]
        if len(seen[check["gap_id"]]) != 1:
            continue
        if check["disposition"] == "decompose":
            if ref["target_id"] is None:
                error(f"/gap_checks/{i}", "The supported action has no writable processing source-review target.")
                continue
            findings.append({"domain": "annotation", "owner": "processing", "target_ids": [ref["target_id"]],
                "explanation": check["reason"] + " Affected scope: " + check["affected"],
                "suggestion": check["supported_action"], "source_refs": deepcopy(check["source_refs"])})
            if check.get("cfg_action_missing"):
                findings.append({"domain": "cfg", "required_graph_edit": "action_inventory", "target_ids": [ref["cfg_target"]],
                    "explanation": "Missing or misclassified source boundary " + check["masked_boundary"] + ". " + check["reason"],
                    "suggestion": check["supported_action"], "source_refs": deepcopy(check["source_refs"])})
        usable.append(check)
    return usable, findings, errors
