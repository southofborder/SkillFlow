"""Lossless review display and material-bound, finite structural correction.

Display transforms preserve complete source and contract inputs. The correction
strategy permits existing conflict-connected records and known missing slots;
it never supplies semantic decisions or bypasses the final whole validator.
Unrecognized or ambiguous scopes retain the existing correction strategy.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy

from skillflow.common.prompt_format import compact_json
from skillflow.common.source_evidence import _json_object
from skillflow.common.recording import canonical_sha256
from skillflow.common.structural_correction import correction_base_prompt
from skillflow.common.validation import structural_error, diagnostic_materials
from .review_display import (
    DISPLAY_IDENTITY, display_instructions, expand_review_payload, pack_review_payload,
    _shared_values,
)


IDENTITY = "skillflow-review-correction-display-v1"
INPUT_MARKER = "\nINPUT_JSON\n"
SOURCE_MARKER = "\nCOMPLETE SOURCE\n"
NOTICE = (
    "\nJOINT CORRECTION MATERIAL\n"
    "The single INPUT_JSON retains every original logical review input at its original key and adds "
    "correction (the complete previous candidate or selected records and all displayed diagnostics). "
    "Existing target paths still refer to the original logical inputs; diagnostic and record paths "
    "refer to the candidate, never to physical shared-value definitions. Apply the correction response "
    "format stated above. COMPLETE SOURCE is unchanged.\n"
)


def _parts(prompt):
    """Recognize only the renderer's JSON boundary, not markers in source text."""
    try:
        start = prompt.index(INPUT_MARKER) + len(INPUT_MARKER)
        prefix = prompt[:start - len(INPUT_MARKER)]
        if "\nRESPONSE FORMAT\n" not in prefix:
            return None
        _, length = json.JSONDecoder().raw_decode(prompt[start:])
        payload = _json_object(prompt[start:start + length])
        suffix = prompt[start + length:]
        if not suffix.startswith(SOURCE_MARKER):
            return None
        if payload.get("format") == DISPLAY_IDENTITY:
            payload = expand_review_payload(payload)
        if (not isinstance(payload, dict)
                or not {"task", "cfg", "annotation", "availability"} <= payload.keys()):
            return None
        return prefix, payload, suffix
    except (ValueError, TypeError, RecursionError):
        return None


def _correction_tables(payload):
    """Use the existing column-table grammar for correction record arrays.

    Inventory tables retain their original locations. Only the added correction
    subtree gains generic tables; arbitrary original annotation layout is not
    repacked. Column order and absent-versus-null fields stay exact.
    """
    columns, shapes = [], {}
    markers = {"$ref", "$rows", "$literal_object"}

    def encode(value, path=()):
        inventory = (path == ("input_contract_inventory", "obligations")
            or len(path) == 4 and path[:2] == ("input_contract_inventory", "obligations")
            and type(path[2]) is int and path[3] == "scopes")
        if isinstance(value, list):
            if ((inventory or path[:1] == ("correction",)) and len(value) > 1
                    and all(isinstance(row, dict) for row in value)):
                rows = []
                for i, record in enumerate(value):
                    shape = tuple(record)
                    if shape not in shapes:
                        shapes[shape] = len(columns)
                        columns.append(list(shape))
                    rows.append([shapes[shape], *[
                        encode(item, (*path, i, key)) for key, item in record.items()]])
                return {"$rows": rows}
            return [encode(item, (*path, i)) for i, item in enumerate(value)]
        if isinstance(value, dict):
            if markers.intersection(value):
                return {"$literal_object": [[key, encode(item, (*path, key))] for key, item in value.items()]}
            return {key: encode(item, (*path, key)) for key, item in value.items()}
        return value

    prepared = encode(payload)
    shared, definitions = _shared_values(prepared)
    choices = [{"format": DISPLAY_IDENTITY, "record_columns": columns,
                "shared_values": values, "payload": value}
               for value, values in ((prepared, {}), (shared, definitions))]
    return min(choices, key=lambda value: len(compact_json(value)))


def compact_review_correction(base_prompt, fallback, context):
    """Choose the shorter complete presentation without dropping any content.

    The fallback is the existing whole-candidate or existing-record correction.
    Source bytes, instruction/schema text and logical correction values remain
    intact. Exact sharing may span the original material and correction packet.
    """
    base = correction_base_prompt(base_prompt)
    parts = _parts(base)
    serialized = compact_json(context)
    if (parts is None or not fallback.startswith(base) or not fallback.endswith(serialized)
            or len(fallback) < len(base) + len(serialized)):
        return fallback
    prefix, inputs, source = parts
    if "correction" in inputs:
        return fallback
    instructions = fallback[len(base):len(fallback) - len(serialized)]
    logical = {**inputs, "correction": context}
    packed = min((pack_review_payload(logical), _correction_tables(logical)),
                 key=lambda value: len(compact_json(value)))
    if compact_json(expand_review_payload(packed)) != compact_json(logical):
        raise ValueError("Review correction display changed its complete logical payload")
    legend = "" if display_instructions() in prefix else "\n" + display_instructions()
    candidate = (prefix + instructions + NOTICE + legend + INPUT_MARKER
                 + compact_json(packed) + source)
    return min((fallback, candidate), key=len)


TABLES = ("findings", "input_contract_checks", "input_projection_checks", "source_input_findings")
SCOPE_IDENTITY = "skillflow-review-correction-scope-v2"
_MISSING_PREFIX = "Input-contract review must cover every expected obligation exactly once; missing "


def complete_review_candidate(value):
    """A complete returned envelope may still contain invalid or missing rows."""
    return (isinstance(value, dict) and set(value) - {"gap_checks"} == {"outcome", *TABLES}
            and value["outcome"] == "completed" and all(isinstance(value[key], list) for key in TABLES)
            and isinstance(value.get("gap_checks", []), list))


def _record_path(path, candidate):
    match = re.match(r"^/(findings|input_contract_checks|gap_checks)/(0|[1-9][0-9]*)(?:/|$)", path)
    if match is None or int(match[2]) >= len(candidate.get(match[1], [])):
        return None
    return "/" + match[1] + "/" + match[2]


def _overlapping_obligations(finding, targets):
    if not isinstance(finding, dict) or finding.get("domain") not in {"cfg", "annotation"}:
        return set()
    domain = finding["domain"]
    actuals = finding.get("target_ids")
    if not isinstance(actuals, list) or any(not isinstance(value, str) for value in actuals):
        return set()
    actuals = [value for value in actuals if value.startswith(domain + ":")
               or domain == "annotation" and value.startswith("fragment:processing:")]
    return {identity for identity, protected in targets.items() if any(
        actual == target or actual.startswith(target + "/") or target.startswith(actual + "/")
        for actual in actuals for target in protected)}


def review_correction_scope(candidate, diagnostics, material):
    """Derive finite editing permissions from this exact returned candidate.

    Missing identities come from the program inventory, never error-message
    parsing or a model assertion. Target overlap closes both sides of a possible
    finding/check conflict, including currently invalid and not-yet-authored
    checks. Unknown/global defects keep the complete-response fallback.
    """
    evidence = {"identity": SCOPE_IDENTITY, "candidate_sha256": canonical_sha256(candidate),
        "material_sha256": canonical_sha256(material), "diagnostics_sha256": canonical_sha256(diagnostics)}

    def full(reason):
        return {"mode": "full", "reason": reason, "evidence": evidence}

    if not complete_review_candidate(candidate):
        return full("A malformed review envelope requires a complete replacement.")
    expected = material["input_contract_inventory"]["obligations"]
    expected_ids = [row["id"] for row in expected]
    if len(set(expected_ids)) != len(expected_ids):
        return full("The program obligation inventory has ambiguous identities.")
    checks = candidate["input_contract_checks"]
    present = [row.get("obligation_id") if isinstance(row, dict) else None for row in checks]
    if (any(not isinstance(identity, str) or identity not in expected_ids for identity in present)
            or len(set(present)) != len(present)):
        return full("Unknown, absent or duplicate authored obligation identities require a complete replacement.")
    missing = [identity for identity in expected_ids if identity not in set(present)]
    gap_ids = {row["id"] for row in material.get("processing_gap_inventory", [])}
    supplied_gaps = [row.get("gap_id") if isinstance(row, dict) else None for row in candidate.get("gap_checks", [])]
    if any(not isinstance(k, str) or k not in gap_ids for k in supplied_gaps) or len(set(supplied_gaps)) != len(supplied_gaps):
        return full("Unknown or duplicate whole-instruction gap check identities require a complete replacement.")
    missing_gaps = sorted(gap_ids - set(supplied_gaps))
    if not missing and not any(row.get("code") in {"input_contract_review_conflict", "processing_gap_review"} for row in diagnostics):
        return full("No missing obligation or cross-record conflict requires the finite-slot correction protocol; retain the existing correction strategy.")
    check_paths = {identity: f"/input_contract_checks/{index}" for index, identity in enumerate(present)}
    selected, coverage = set(), 0
    for row in diagnostics:
        if row.get("code") == "processing_gap_review" and row.get("path") == "/gap_checks":
            continue
        if row.get("code") == "review_coverage" and row.get("path") == "/input_contract_checks":
            coverage += 1
            continue
        path = _record_path(row.get("path", ""), candidate)
        if path is None:
            return full("A diagnostic has no supported existing finding/check record owner.")
        selected.add(path)
        if row.get("code") == "input_contract_review_conflict":
            context = row.get("context", {})
            finding = candidate["findings"][int(path.rsplit("/", 1)[1])] if path.startswith("/findings/") else None
            linked = context.get("conflicting_checks")
            if (not isinstance(finding, dict) or context.get("target_ids") != finding.get("target_ids")
                    or not isinstance(linked, list) or not linked):
                return full("A conflict diagnostic lacks exact finding/check ownership.")
            for pair in linked:
                if (not isinstance(pair, dict) or pair.get("record_path") != check_paths.get(pair.get("obligation_id"))):
                    return full("A conflict diagnostic refers to another candidate or obligation.")
                selected.add(pair["record_path"])
    if coverage != len(missing):
        return full("Missing-check coverage diagnostics do not match the current finite inventory.")
    if not selected and not missing and not missing_gaps:
        return full("No finite correction scope was established.")
    linked = {f"/findings/{i}": _overlapping_obligations(row, material["input_contract_targets"])
              for i, row in enumerate(candidate["findings"])}
    obligations = set(missing) | {identity for identity, path in check_paths.items() if path in selected}
    while True:
        before = (set(selected), set(obligations))
        for path, identities in linked.items():
            if path in selected or identities & obligations:
                selected.add(path)
                obligations.update(identities)
        selected.update(check_paths[identity] for identity in obligations if identity in check_paths)
        if before == (selected, obligations):
            break
    records = {}
    for path in sorted(selected):
        table, index = path[1:].split("/")
        records[path] = deepcopy(candidate[table][int(index)])
    evidence.update(inventory_sha256=canonical_sha256(expected),
        records_sha256=canonical_sha256(records), missing_obligation_ids=missing,
        dependency_obligation_ids=sorted(obligations),
        retained_record_counts={table: len(candidate[table]) - sum(path.startswith("/" + table + "/")
                                      for path in records) for table in TABLES})
    if gap_ids:
        evidence["missing_gap_ids"] = missing_gaps
    return {"mode": "records", "records": records, "missing_obligation_ids": missing, "evidence": evidence}


def _diagnostic_display(diagnostics, missing, inventory_ids):
    """Group repeated missing-coverage wording with an exact inverse mapping."""
    known = {canonical_sha256({"code": "review_coverage", "path": "/input_contract_checks",
        "message": _MISSING_PREFIX + identity}): identity for identity in missing}
    records, indices, identities = [], [], []
    positions = {identity: index for index, identity in enumerate(inventory_ids)}
    for index, row in enumerate(diagnostics):
        identity = known.get(canonical_sha256(row))
        if identity is None:
            records.append({"index": index, "diagnostic": deepcopy(row)})
        else:
            indices.append(index)
            identities.append(identity)
    display = {"records": records, "missing_coverage": {"indices": indices,
        "obligation_indices": [positions[identity] for identity in identities],
        "inventory_path": "/input_contract_inventory/obligations", "code": "review_coverage", "path": "/input_contract_checks",
        "message_prefix": _MISSING_PREFIX}}
    restored = {row["index"]: row["diagnostic"] for row in records}
    restored.update({index: {"code": "review_coverage", "path": "/input_contract_checks",
        "message": _MISSING_PREFIX + inventory_ids[position]} for index, position in zip(
            indices, display["missing_coverage"]["obligation_indices"])})
    if [restored[index] for index in range(len(diagnostics))] != diagnostics:
        raise ValueError("Review correction diagnostic display changed original errors")
    return display if len(compact_json(display)) < len(compact_json(diagnostics)) else diagnostics


class ReviewCorrectionStrategy:
    """One source/material-bound correction; the ordinary validator stays final."""

    def __init__(self, material, fallback):
        self.material = deepcopy(material)
        self.fallback = fallback
        self.identity = fallback.identity + ":finite-obligation-slots-v2"
        self.scope = None
        self.diagnostics = None

    def build_prompt(self, base_prompt, candidate, diagnostics):
        self.diagnostics = deepcopy(diagnostics)
        try:
            parsed = _json_object(candidate)
        except (ValueError, TypeError):
            self.scope = None
            return self.fallback.build_prompt(base_prompt, candidate, diagnostics)
        self.scope = review_correction_scope(parsed, diagnostics, self.material)
        if self.scope["mode"] != "records":
            return self.fallback.build_prompt(base_prompt, candidate, diagnostics)
        shown = diagnostic_materials(diagnostics)["diagnostics"]
        inventory_ids = [row["id"] for row in self.material["input_contract_inventory"]["obligations"]]
        positions = {identity: index for index, identity in enumerate(inventory_ids)}
        evidence = {key: deepcopy(value) for key, value in self.scope["evidence"].items()
                    if key not in {"missing_obligation_ids", "dependency_obligation_ids"}}
        evidence.update(scope_sha256=canonical_sha256(self.scope["evidence"]),
            dependency_obligation_indices=[positions[identity] for identity in self.scope["evidence"]["dependency_obligation_ids"]])
        context = {"record_ids": list(self.scope["records"]), "records": list(self.scope["records"].values()),
            "insertion_obligation_indices": [positions[identity] for identity in self.scope["missing_obligation_ids"]],
            "diagnostics": _diagnostic_display(shown, self.scope["missing_obligation_ids"], inventory_ids),
            "scope": evidence}
        instruction = ("\nFINITE REVIEW CORRECTION\n"
            'Return only {"replacements":[{"record_id":"<supplied existing path>","value":<complete record>}],'
            '"insertions":[<complete input_contract_check>]}. '
            "The parallel record_ids and records arrays pair each existing logical record path with its complete value. "
            "Replace only supplied records. Each existing check keeps its obligation_id; all its fields may be corrected. "
            "insertion_obligation_indices are zero-based indices into the complete input_contract_inventory.obligations array. "
            "Insert exactly one check for each listed inventory slot, using that entry's existing id as obligation_id in the new record. "
            "Do not invent IDs, delete records, replace whole tables or add findings outside existing slots. "
            "Unlisted original review records remain byte-for-byte logical values and are reused; the complete prior answer is retained in the audit. "
            "The supplied records include the actual target-overlap closure of findings and affected checks, so either side of a conflict can be corrected. "
            "Complete source, annotation and every contract/obligation remain in the original input. Look up insertion obligations there; absence of a prior check is not an accepted or unresolved judgment. "
            "A diagnostics missing_coverage table represents one original error per paired diagnostic index/obligation index: read the existing inventory entry's id and append it to message_prefix, retaining code and path. Other indexed diagnostic records are unchanged. "
            "Do not silence a source-supported allegation to pass validation. Every scope, source reference, exact inventory and conflict is validated again on the complete merged result.\n")
        if self.scope["evidence"].get("missing_gap_ids"):
            instruction += "Insert one complete gap check with gap_id for every missing_gap_ids entry in scope.\n"
        fallback = correction_base_prompt(base_prompt) + instruction + compact_json(context)
        return compact_review_correction(base_prompt, fallback, context)

    def merge(self, candidate, correction):
        if self.scope is None or self.scope["mode"] != "records":
            return self.fallback.merge(candidate, correction)
        original, changed = _json_object(candidate), _json_object(correction)
        if review_correction_scope(original, self.diagnostics, self.material) != self.scope:
            raise structural_error("review_correction_identity", "", "Finite review correction scope belongs to another candidate or material")
        from .failed_stage_targets import correction_guard
        # The guard accepts the replacement-only view; insertion cannot erase
        # or retarget an existing unrepresentable finding.
        correction_guard(original, self.diagnostics, {"replacements": changed.get("replacements")})
        if set(changed) != {"replacements", "insertions"} or any(not isinstance(changed[key], list) for key in changed):
            raise structural_error("review_correction_envelope", "", "Finite review correction requires exactly replacements and insertions arrays")
        result, used = deepcopy(original), set()
        for index, row in enumerate(changed["replacements"]):
            path = row.get("record_id") if isinstance(row, dict) else None
            if (not isinstance(row, dict) or set(row) != {"record_id", "value"}
                    or not isinstance(path, str) or path not in self.scope["records"] or path in used):
                raise structural_error("review_correction_record", f"/replacements/{index}", "Replace a supplied existing record once using its complete value")
            table, position = path[1:].split("/")
            if table == "input_contract_checks" and (not isinstance(row["value"], dict)
                    or row["value"].get("obligation_id") != original[table][int(position)]["obligation_id"]):
                raise structural_error("review_correction_obligation", f"/replacements/{index}/value", "An existing check must retain its exact obligation identity")
            if table == "gap_checks" and (not isinstance(row["value"], dict)
                    or row["value"].get("gap_id") != original[table][int(position)]["gap_id"]):
                raise structural_error("review_correction_gap", f"/replacements/{index}/value", "An existing gap decision must retain its exact gap identity.")
            result[table][int(position)] = deepcopy(row["value"])
            used.add(path)
        inserted = set()
        for index, row in enumerate(changed["insertions"]):
            if isinstance(row, dict) and "gap_id" in row:
                identity = row["gap_id"]
                if identity not in self.scope["evidence"].get("missing_gap_ids", []) or identity in inserted:
                    raise structural_error("review_correction_gap", f"/insertions/{index}", "Insert each supplied missing gap decision at most once.")
                inserted.add(identity)
                result.setdefault("gap_checks", []).append(deepcopy(row))
                continue
            identity = row.get("obligation_id") if isinstance(row, dict) else None
            if identity not in self.scope["missing_obligation_ids"] or identity in inserted:
                raise structural_error("review_correction_insertion", f"/insertions/{index}", "Insert each supplied missing obligation at most once; existing or invented IDs are forbidden")
            inserted.add(identity)
            result["input_contract_checks"].append(deepcopy(row))
        return result
