"""Locate processing coverage errors and merge only their authorized owners."""
from collections import defaultdict
from copy import deepcopy
import re

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer, resolve_pointer
from skillflow.common.validation import structural_error


VERSION = "finite-processing-slots-v1"


def gap_positions(value):
    """Unmodeled claims choose an IR's representation; precision gaps do not."""
    positions = defaultdict(list)
    rows = value.get("processing_gaps", [])
    if isinstance(rows, list):
        for index, row in enumerate(rows):
            if isinstance(row, dict) and row.get("unmodeled") is True and isinstance(row.get("instruction_id"), str):
                positions[row["instruction_id"]].append(index)
    return positions


def coverage_diagnostics(value, expected, *, fixed_unmodeled=()):
    specs = value.get("ir_semantics", {})
    positions = gap_positions(value)
    if not isinstance(specs, dict):
        # No claim of individual omissions is possible within a malformed table.
        return []
    fixed = set(fixed_unmodeled)
    diagnostics = []
    for ir in sorted(expected):
        modeled, unmodeled = ir in specs, ir in positions or ir in fixed
        if modeled == unmodeled:
            problem = "conflict" if modeled else "missing"
            diagnostics.extend(structural_error("instruction_coverage", json_pointer("ir_semantics", ir),
                ("This CFG instruction is both modeled and explicitly unmodeled." if modeled else
                 "This CFG instruction has neither modeled semantics nor an explicit unmodeled gap."),
                coverage_slot={"instruction_id": ir, "problem": problem,
                    "gap_paths": [json_pointer("processing_gaps", index) for index in positions[ir]],
                    "fixed_unmodeled": ir in fixed}).diagnostics)
    for ir in sorted(set(specs) - expected):
        diagnostics.extend(structural_error("processing_instruction", json_pointer("ir_semantics", ir),
            "Modeled semantics must refer to an actual CFG instruction.").diagnostics)
    for ir in sorted(set(positions) - expected):
        for index in positions[ir]:
            diagnostics.extend(structural_error("processing_instruction", json_pointer("processing_gaps", index, "instruction_id"),
                "An unmodeled gap must refer to an actual CFG instruction.").diagnostics)
    return diagnostics


def _owns(pointer, path):
    return path == pointer or path.startswith(pointer + "/")


def _field_slot(candidate, owner, row):
    """Limit explicitly field-local repairs to their exact typed write site."""
    path = row["path"]
    if not owner.startswith("/ir_semantics/") or path == owner:
        return None
    relative = path[len(owner):]
    local_field = (
        row["code"] == "validate_ref" and re.fullmatch(r"/output_bindings/\d+/value", relative)
        or row["code"] == "mechanism_evidence_reference" and path.endswith("/evidences")
        or row["code"] == "input_contract_required" and path.endswith("/input_contract")
    )
    if not local_field:
        return None
    parent, name = path.rsplit("/", 1)
    try:
        container = resolve_pointer(candidate, parent)
    except ValueError:
        return None
    if not isinstance(container, dict):
        return None
    slot = {"record_id": owner, "present": name in container}
    if name in container:
        slot["value"] = container[name]
    return slot


def correction_scope(candidate, diagnostics, records):
    """Authorize by exact original record coordinates or a checked CFG IR slot."""
    scoped, reserved = {}, set()
    specs = candidate.get("ir_semantics", {})
    positions = gap_positions(candidate)
    if isinstance(specs, dict):
        for row in diagnostics:
            slot = row.get("context", {}).get("coverage_slot")
            if row["code"] != "instruction_coverage" or not isinstance(slot, dict):
                continue
            ir = slot.get("instruction_id")
            if not isinstance(ir, str) or row["path"] != json_pointer("ir_semantics", ir):
                continue
            gap_paths = [json_pointer("processing_gaps", index) for index in positions[ir]]
            conflict = ir in specs and bool(gap_paths or slot.get("fixed_unmodeled"))
            missing = ir not in specs and not gap_paths and not slot.get("fixed_unmodeled")
            if ((slot.get("problem") == "conflict" and conflict or slot.get("problem") == "missing" and missing)
                    and slot.get("gap_paths") == gap_paths and not slot.get("fixed_unmodeled")):
                scoped[ir] = {"problem": slot["problem"], "modeled": specs.get(ir),
                    "unmodeled_gaps": {pointer: records[pointer] for pointer in gap_paths}}
                reserved.update([row["path"], *gap_paths])
    selected, field_slots, read_only = {}, {}, {}
    for key, value in records.items():
        if key in reserved:
            continue
        owned = [row for row in diagnostics if _owns(key, row["path"])]
        if not owned:
            continue
        fields = {row["path"]: _field_slot(candidate, key, row) for row in owned}
        if all(slot is not None for slot in fields.values()):
            field_slots.update(fields)
            read_only[key] = value
        else:
            selected[key] = value
    return {"candidate_sha256": canonical_sha256(candidate), "records": selected,
        "coverage_slots": scoped, "field_slots": field_slots, "read_only_records": read_only}


def remove_coverage_claims(candidate, instruction_ids):
    """Remove both dispositions of exact ambiguous slots, preserving other rows."""
    if not instruction_ids:
        return
    for ir in instruction_ids:
        candidate.get("ir_semantics", {}).pop(ir, None)
    _remove_unmodeled(candidate, instruction_ids)


def _remove_unmodeled(candidate, instruction_ids):
    if isinstance(candidate.get("processing_gaps"), list):
        candidate["processing_gaps"] = [gap for gap in candidate["processing_gaps"] if not (
            isinstance(gap, dict) and gap.get("unmodeled") is True and gap.get("instruction_id") in instruction_ids)]


def merge_slots(candidate, correction, scope, *, validate_gap):
    """Apply typed occurrence changes; the caller still validates the whole result."""
    records, slots, field_slots = scope["records"], scope["coverage_slots"], scope["field_slots"]
    if (canonical_sha256(candidate) != scope["candidate_sha256"]
            or not correction or not set(correction) <= {"replacements", "coverage_slots", "fields"}):
        raise structural_error("processing_correction_scope", "", "Return only authorized corrections for the exact prior candidate.")
    for key in correction:
        if not isinstance(correction[key], list):
            raise structural_error("processing_correction_shape", json_pointer(key), "Correction tables must be arrays.")
    result, seen = deepcopy(candidate), set()
    for index, row in enumerate(correction.get("replacements", [])):
        if not isinstance(row, dict) or set(row) != {"record_id", "value"}:
            raise structural_error("record_replacement", json_pointer("replacements", index), "A replacement requires record_id and value.")
        pointer = row["record_id"]
        if not isinstance(pointer, str) or pointer not in records or pointer in seen:
            raise structural_error("record_identity", json_pointer("replacements", index, "record_id"),
                "Use each authorized existing identity (record_id) at most once.")
        seen.add(pointer)
        parent, token = pointer.rsplit("/", 1)
        container = resolve_pointer(result, parent)
        key = int(token) if isinstance(container, list) else token.replace("~1", "/").replace("~0", "~")
        updated = row["value"]
        if parent == "/processing_gaps" and isinstance(updated, dict) and updated.get("unmodeled") is True:
            previous = records[pointer]
            if not (isinstance(previous, dict) and previous.get("unmodeled") is True
                    and updated.get("instruction_id") == previous.get("instruction_id")):
                raise structural_error("processing_coverage_ownership", json_pointer("replacements", index),
                    "Changing an IR's modeled/unmodeled disposition requires an authorized coverage slot.")
        container[key] = deepcopy(updated)
    for index, row in enumerate(correction.get("fields", [])):
        if not isinstance(row, dict) or set(row) != {"path", "value"}:
            raise structural_error("processing_field_shape", json_pointer("fields", index), "A field correction requires path and value.")
        path = row["path"]
        if not isinstance(path, str) or path not in field_slots or path in seen:
            raise structural_error("processing_field_identity", json_pointer("fields", index, "path"),
                "Use each authorized field path at most once.")
        seen.add(path)
        parent, name = path.rsplit("/", 1)
        resolve_pointer(result, parent)[name] = deepcopy(row["value"])
    supplied, replacements, keep_modeled, keep_unmodeled = set(), [], set(), set()
    for index, row in enumerate(correction.get("coverage_slots", [])):
        pointer = json_pointer("coverage_slots", index)
        if (not isinstance(row, dict) or len(row) != 2 or "instruction_id" not in row
                or not ({"modeled", "unmodeled_gaps", "keep"} & set(row))):
            raise structural_error("processing_coverage_shape", pointer,
                "A coverage slot requires instruction_id and exactly one of modeled, unmodeled_gaps, or keep.")
        ir = row["instruction_id"]
        if not isinstance(ir, str) or ir not in slots or ir in supplied:
            raise structural_error("processing_coverage_identity", pointer + "/instruction_id",
                "Use each authorized CFG instruction_id at most once.")
        supplied.add(ir)
        if "keep" in row:
            if row["keep"] == "modeled" and ir in candidate.get("ir_semantics", {}):
                keep_modeled.add(ir)
            elif row["keep"] == "unmodeled" and slots[ir]["unmodeled_gaps"]:
                keep_unmodeled.add(ir)
            else:
                raise structural_error("processing_coverage_ownership", pointer + "/keep",
                    "The exact chosen modeled or unmodeled record must already exist.")
            continue
        if "modeled" in row and not isinstance(row["modeled"], dict):
            raise structural_error("processing_coverage_shape", pointer + "/modeled", "Modeled semantics must be an object.")
        if "unmodeled_gaps" in row:
            gaps = row["unmodeled_gaps"]
            if not isinstance(gaps, list) or not gaps:
                raise structural_error("processing_coverage_shape", pointer + "/unmodeled_gaps", "Supply at least one concrete source-backed gap.")
            for gap_index, gap in enumerate(gaps):
                if not isinstance(gap, dict) or gap.get("instruction_id") != ir or gap.get("unmodeled") is not True:
                    raise structural_error("processing_coverage_ownership", pointer + f"/unmodeled_gaps/{gap_index}",
                        "Every supplied gap must explicitly mark this exact instruction unmodeled.")
                validate_gap(gap, pointer + f"/unmodeled_gaps/{gap_index}")
            if not isinstance(candidate.get("processing_gaps", []), list):
                raise structural_error("processing_coverage_shape", pointer,
                    "The existing processing_gaps table is malformed; a slot cannot replace its container.")
        replacements.append(row)
    for ir in keep_unmodeled:
        result["ir_semantics"].pop(ir, None)
    _remove_unmodeled(result, keep_modeled)
    remove_coverage_claims(result, supplied - keep_modeled - keep_unmodeled)
    for row in replacements:
        if "modeled" in row:
            result.setdefault("ir_semantics", {})[row["instruction_id"]] = deepcopy(row["modeled"])
        else:
            result.setdefault("processing_gaps", []).extend(deepcopy(row["unmodeled_gaps"]))
    return result
