"""One exact policy for source-reviewed, unavailable semantic stages.

These targets name failure evidence, never an accepted Task, CFG or fragment.
The caller owns artifact verification; this module verifies its self-contained
bindings without reading files or repairing any failed candidate.
"""
from copy import deepcopy
import re

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer, _json_object
from skillflow.common.validation import structural_error


ARCHIVED_IDENTITY = "skillflow-failed-stage-review-targets-v1"
IDENTITY = "skillflow-failed-stage-review-targets-v2"
EVIDENCE_IDENTITY = "skillflow-failed-stage-material-v1"
POLICY = {
    "task": {"domain": "task", "accepted_object": "task", "requires_evidence": True},
    "flow": {"domain": "cfg", "accepted_object": None, "requires_evidence": True},
    "graph": {"domain": "cfg", "accepted_object": "cfg", "requires_evidence": True},
    "processing": {"domain": "annotation", "owner": "processing", "requires_evidence": False},
    "task-correspondence": {"domain": "annotation", "owner": "task-correspondence", "requires_evidence": False},
    "sensitivity": {"domain": "annotation", "owner": "sensitivity", "requires_evidence": False},
}
FAILURE_STATUSES = frozenset({"structural_failure", "semantic_failure"})


def _checked_evidence(evidence, *, stage, failure, source_sha256):
    if (not isinstance(evidence, dict) or evidence.get("identity") != EVIDENCE_IDENTITY
            or evidence.get("stage") != stage or evidence.get("status") != failure.get("status")
            or evidence.get("source_sha256") != source_sha256
            or not isinstance(evidence.get("material"), dict)
            or evidence.get("material_sha256") != canonical_sha256(evidence["material"])):
        raise ValueError("Failed-stage review evidence does not match its actual stage, status, source or material")


def failed_stage_inventory(*, files, failures, collections, fragments, identity=IDENTITY):
    """Derive all permitted exact IDs and explicit unavailable-stage reasons."""
    source_sha256 = canonical_sha256(files)
    targets, unavailable = [], []
    for stage, failure in sorted(failures.items()):
        policy = POLICY.get(stage)
        reason = None
        if policy is None:
            reason = "No failed-stage review target policy exists for this exact stage name."
        elif failure.get("status") not in FAILURE_STATUSES:
            reason = "Only actual structural or semantic stage failures have review targets; skipped, partial, request and execution failures do not."
        elif policy.get("accepted_object") and collections.get(policy["accepted_object"]) is not None:
            reason = "The corresponding accepted object is available; review that actual object instead."
        elif policy.get("owner") and (collections.get("annotation") is not None or stage in fragments):
            reason = "The corresponding annotation or fragment is available; review that actual object instead."
        evidence = failure.get("evidence")
        if policy is not None and evidence is not None:
            _checked_evidence(evidence, stage=stage, failure=failure, source_sha256=source_sha256)
        if reason is None and policy["requires_evidence"] and evidence is None:
            reason = "This upstream failure lacks bound original-stage material; no failed candidate or target is inferred."
        if reason is not None:
            unavailable.append({"stage": stage, "reason": reason})
            continue
        target = {"id": "stage:" + stage, "domain": policy["domain"], "kind": "stage_failures",
                  "pointer": json_pointer(stage), "stage": stage, "requires_source": True,
                  "binding": {"identity": identity, "source_sha256": source_sha256,
                              "failure_sha256": canonical_sha256(failure)}}
        if "owner" in policy:
            target["owner"] = policy["owner"]
        targets.append(target)
        if stage == "graph" and identity == IDENTITY and evidence:
            from .failed_graph_targets import failed_graph_targets
            targets.extend(failed_graph_targets(evidence["material"], target))
    return {"identity": identity, "source_sha256": source_sha256,
            "targets": targets, "unavailable": unavailable}


def inventory_for_material(material):
    recorded = material.get("failed_stage_targets", {}).get("identity")
    return failed_stage_inventory(files=material["files"], failures=material["stage_failures"],
        collections={key: material.get(key) for key in ("task", "cfg", "annotation")},
        fragments=material.get("fragments", {}), identity=ARCHIVED_IDENTITY if recorded == ARCHIVED_IDENTITY else IDENTITY)


def checked_stage_target(identity, material, target):
    """Reject stale or fabricated target rows against current bound evidence."""
    stage = identity.partition("/")[0].removeprefix("stage:")
    failure = material["stage_failures"].get(stage)
    saved_inventory = material.get("failed_stage_targets", {})
    policy = saved_inventory.get("identity") if isinstance(saved_inventory, dict) else None
    expected_inventory = failed_stage_inventory(files=material["files"],
        failures={} if stage not in POLICY or failure is None else {stage: failure},
        collections={key: material.get(key) for key in ("task", "cfg", "annotation")},
        fragments=material.get("fragments", {}), identity=ARCHIVED_IDENTITY if policy == ARCHIVED_IDENTITY else IDENTITY)
    expected = next((row for row in expected_inventory["targets"] if row["id"] == identity), None)
    saved = (next((row for row in saved_inventory.get("targets", []) if row.get("id") == identity), None)
             if policy in {IDENTITY, ARCHIVED_IDENTITY}
             and saved_inventory.get("source_sha256") == expected_inventory["source_sha256"] else None)
    if expected is None or target != expected or saved != expected:
        raise ValueError("Failed-stage review target is absent, stale or not bound to the actual failure material")
    return deepcopy(expected)


def target_correction_context(identity, material, *, domain=None):
    """Expose exact permitted targets, never invent an alias or semantic parent."""
    targets = material["target_index"]
    # The complete draft index already accompanies the request. Include only
    # the named block's sites in an individual correction diagnostic.
    parts = identity.split("/")
    draft_block = "/".join(parts[:3]) if parts[:2] == ["stage:graph", "blocks"] and len(parts) >= 3 else None
    stages = [{key: deepcopy(row[key]) for key in ("id", "domain", "stage", "owner") if key in row}
              for row in targets if row.get("kind") == "stage_failures" and (
                  "/" not in row["id"] or draft_block and (row["id"] == draft_block or row["id"].startswith(draft_block + "/")))]
    roots = [row["id"] for row in targets if row.get("pointer") == "" and row.get("domain") == domain]
    compatible = [row for row in targets if row.get("domain") == domain]
    return {"requested_domain": domain, "allowed_failed_stage_targets": stages,
            "available_domain_roots": roots,
            "correction_scope": "same_domain_target" if compatible else "unrepresentable_domain",
            "preserve_original_allegation": True,
            "target_policy": IDENTITY,
            "notice": "Use only an actual same-domain target justified by the source. Never guess aliases, move a CFG allegation to Task, or delete an allegation merely to pass validation. An unavailable domain remains explicit review evidence, not an accepted candidate."}


def correction_guard(candidate, diagnostics, correction):
    """Keep an unrepresentable allegation explicit for strict local isolation.

    Only diagnostics that establish an absent same-domain target activate this
    guard. Ordinary corrections remain free to fix actual same-domain targets.
    Keeping the original record does not accept it: the full validator still
    rejects it, and terminal isolation preserves its independent valid siblings.
    """
    original, response = _json_object(candidate), _json_object(correction)
    findings = original.get("findings")
    if not isinstance(findings, list):
        return
    guarded = {}
    for row in diagnostics:
        context = row.get("context", {})
        match = re.match(r"^/findings/(0|[1-9][0-9]*)/target_ids(?:/|$)", row.get("path", ""))
        if (match is None or context.get("correction_scope") != "unrepresentable_domain"
                or context.get("target_policy") not in {IDENTITY, ARCHIVED_IDENTITY}):
            continue
        index = int(match[1])
        if (index < len(findings) and isinstance(findings[index], dict)
                and findings[index].get("domain") == context.get("requested_domain")):
            guarded[f"/findings/{index}"] = findings[index]
    if not guarded:
        return

    def reject(path):
        raise structural_error("review_target_unrepresentable", path,
            "No actual same-domain target exists for this recorded allegation. Preserve the original record for explicit isolation; do not delete it or retarget unrelated content.",
            original_record=guarded[path], preserve_original_allegation=True, target_policy=IDENTITY)

    if set(response) == {"replacements"} and isinstance(response["replacements"], list):
        for replacement in response["replacements"]:
            if isinstance(replacement, dict) and replacement.get("record_id") in guarded:
                path = replacement["record_id"]
                if replacement.get("value") != guarded[path]:
                    reject(path)
    elif isinstance(response.get("findings"), list):
        for path, finding in guarded.items():
            if finding not in response["findings"]:
                reject(path)


GUIDANCE = (
    "FAILED-STAGE TARGET POLICY\n"
    "failed_stage_targets.targets lists every permitted failed-stage ID, exact domain and optional annotation owner. "
    "Use only those listed IDs; a key in stage_failures alone does not authorize a target. An empty list permits no "
    "stage target. Do not invent stage:cfg, rename stage:graph, or infer a target for a skipped stage. These targets "
    "locate source-bound failure evidence, never an accepted Task, CFG or fragment. A finding needs a concrete "
    "source-supported semantic omission or defect and original source_refs; repeating a mechanical failure, "
    "requesting another sample or treating failed material as validated is insufficient. Domain and owner must "
    "match the listed policy. Failed Task findings still use finite source-only task_objection; unknown requirement "
    "IDs cannot be invented. No valid same-domain target means the allegation cannot be made executable by "
    "retargeting unrelated Task content or silently deleting it.\n"
)
