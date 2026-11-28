"""Carry an objection only while its exact selected record and inputs remain the same."""
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import resolve_pointer, validate_source_ref
from .fragment_revision import _changed_instructions, _data_consumers, _downstream


def _pointer(target):
    for prefix in ("annotation:", "fragment:processing:"):
        if target.startswith(prefix):
            return target[len(prefix):]
    return ""


def _record_owner(target):
    parts = _pointer(target).split("/")
    if len(parts) >= 3 and parts[1] == "ir_semantics":
        return parts[2].replace("~1", "/").replace("~0", "~")
    return None


def retained_source_rechecks(review, before, after):
    """Rebind retained processing rows to the revised bundle, without copying review prose."""
    if not review or not all({"processing", "graph", "annotation"} <= pieces.keys() for pieces in (before, after)):
        return []
    old_cfg, cfg = before["graph"]["value"], after["graph"]["value"]
    previous, selected = (p["processing"]["value"] for p in (before, after))
    old_annotation, annotation = (p["annotation"]["value"]["wire_annotation"] for p in (before, after))
    old_rows, rows = previous["ir_semantics"], selected["ir_semantics"]
    changed = _changed_instructions(old_cfg, cfg)
    changed.update(ir for ir in old_rows.keys() | rows.keys() if old_rows.get(ir) != rows.get(ir))
    changed = _downstream(_data_consumers(old_cfg, cfg), changed)
    retained = []
    for finding in review.get("findings", []):
        if finding.get("domain") != "annotation" or finding.get("owner", "processing") != "processing":
            continue
        # Gap, capability and ingress checks have their own finite inventories in the new review.
        if (finding.get("input_projection_scope_ids") or finding.get("gap_id")
                or finding.get("sensitivity_entry_gap_id")):
            continue
        targets = finding["target_ids"]
        # An assembled review indexes the wire annotation, including demand
        # and sensitivity overlays. Processing fragments only identify owners.
        if any(not target.startswith("annotation:") for target in targets):
            continue
        owners = {_record_owner(target) for target in targets}
        if None in owners or not owners or not owners <= rows.keys() or changed.intersection(owners):
            continue
        try:
            bound = {target: canonical_sha256(resolve_pointer(annotation, _pointer(target)))
                     for target in targets}
            old_bound = {target: canonical_sha256(resolve_pointer(old_annotation, _pointer(target)))
                         for target in targets}
        except ValueError:
            continue
        if old_bound != bound:
            continue
        row = {"targets": bound, "source_refs": deepcopy(finding["source_refs"])}
        if finding.get("affected_ranges"):
            row["affected_ranges"] = deepcopy(finding["affected_ranges"])
        if finding.get("input_contract_obligation_id"):
            row["obligation_id"] = finding["input_contract_obligation_id"]
        else:
            # Retain the original scope and evidence. The old prose is referenced
            # in the immutable source review, and is never injected into a new prompt.
            row["finding_id"] = finding["id"]
        if row not in retained:
            retained.append(row)
    return retained


def checked_retention_targets(rechecks, material):
    targets = {row["id"] for row in material["target_index"]}
    annotation = material["annotation"]
    for row in rechecks:
        if (set(row) - {"affected_ranges"} not in ({"targets", "source_refs", "obligation_id"},
                                                   {"targets", "source_refs", "finding_id"})
                or not row["targets"] or not row["source_refs"]):
            raise ValueError("A retained source objection needs its exact target and source evidence.")
        for target, digest in row["targets"].items():
            if target not in targets or _record_owner(target) is None:
                raise ValueError("Retained review target is absent from the selected annotation.")
            if canonical_sha256(resolve_pointer(annotation, _pointer(target))) != digest:
                raise ValueError("Retained review target differs from the selected value.")
        for ref in row["source_refs"]:
            validate_source_ref(ref, material["files"])
    return deepcopy(rechecks)


def pending_retention_findings(material, checks, findings):
    """A fresh source-backed decision on the same obligation can discharge a prior challenge."""
    accepted = {c["obligation_id"] for c in checks if c["status"] == "accepted" and c.get("evidences")}
    reported = {f["input_contract_obligation_id"] for f in findings if f.get("input_contract_obligation_id")}
    issued = []
    for row in material.get("revision_rechecks", []):
        obligation = row.get("obligation_id")
        if obligation in accepted or obligation in reported:
            continue
        targets = list(row["targets"])
        if not obligation and any(targets == f.get("target_ids") and row["source_refs"] == f.get("source_refs")
                                  and row.get("affected_ranges") == f.get("affected_ranges") for f in findings):
            continue
        issued.append({"domain": "annotation", "owner": "processing", "target_ids": targets,
            "explanation": "The revised bundle retains the previously challenged processing relation at "
                           + ", ".join(targets) + ". Its source-backed resolution is still open.",
            "source_refs": deepcopy(row["source_refs"]),
            "suggestion": "Recheck the unchanged operation and its consumers against the cited source.",
            **({"affected_ranges": deepcopy(row["affected_ranges"])} if row.get("affected_ranges") else {}),
            **({"input_contract_obligation_id": obligation} if obligation else {})})
    return issued
