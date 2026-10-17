"""Explicit, reproducible repair request context; never a hidden prompt suffix."""
from __future__ import annotations

from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.material import checked_material

REPAIR_CONTEXT_VERSION = "skillflow-annotation-repair-context-v2"


def build_repair_context(material, previous_raw_annotation, review_material, review_response):
    from skillflow.propagation.review.material import prepare_review_material
    from skillflow.propagation.review.material import checked_review_material
    from skillflow.propagation.review.services import validate_response
    from skillflow.propagation.review.services import resolve_findings

    material = checked_material(material)
    checked_review = checked_review_material(review_material)
    expected = prepare_review_material(material, previous_raw_annotation)
    if canonical_sha256(checked_review) != canonical_sha256(expected):
        raise ValueError("Repair review does not refer to the actual previous annotation and material")
    if hasattr(review_response, "model_dump"):
        review_response = review_response.model_dump(mode="json")
    parsed = validate_response(review_response, checked_review, normalized=True)
    if not parsed.findings:
        raise ValueError("An annotation repair requires concrete reviewed issues")
    response = parsed.model_dump(mode="json")
    resolved = resolve_findings(parsed, checked_review)
    return {
        "version": REPAIR_CONTEXT_VERSION,
        "previous_raw_annotation": deepcopy(previous_raw_annotation),
        "review_response": response,
        "resolved_targets": resolved,
        "identities": {
            "material_sha256": canonical_sha256(material),
            "previous_raw_sha256": canonical_sha256(previous_raw_annotation),
            "review_material_sha256": canonical_sha256(checked_review),
            "review_response_sha256": canonical_sha256(response),
            "resolved_targets_sha256": canonical_sha256(resolved),
        },
    }


def validate_repair_context(material, context):
    if context is None:
        return None
    if type(context) is not dict or context.get("version") != REPAIR_CONTEXT_VERSION:
        raise ValueError("Unsupported annotation repair context")
    from skillflow.propagation.review.material import prepare_review_material
    rebuilt = build_repair_context(material, context["previous_raw_annotation"],
        prepare_review_material(material, context["previous_raw_annotation"]), context["review_response"])
    if canonical_sha256(context) != canonical_sha256(rebuilt):
        raise ValueError("Annotation repair context or resolved review targets changed")
    return rebuilt


def repair_prompt_payload(material, context):
    checked = validate_repair_context(material, context)
    if checked is None:
        return None
    # Reconstruct coordinates from the shared input owner and original candidate;
    # neither the audit context nor the request carries another source/CFG copy.
    from skillflow.propagation.review.material import resolve_targets, prepare_review_material

    review_material = prepare_review_material(material, checked["previous_raw_annotation"])
    targets = []
    for finding in checked["resolved_targets"]:
        rows = {target["id"]: target for target in finding["targets"]}
        for target in finding["targets"]:
            if target["kind"] == "observation":
                observation = target["value"]
                references = [observation["raw_target_id"], observation["processing_target_id"],
                              *observation["scope_target_ids"]]
                for related in resolve_targets(references, review_material):
                    rows.setdefault(related["id"], related)
        targets.append({"id": finding["id"], "targets": [
            {key: deepcopy(value) for key, value in target.items()
             if key != "value" or target["kind"] == "observation"}
            for target in rows.values()]})
    return {
        "previous_raw_annotation": deepcopy(checked["previous_raw_annotation"]),
        "review_response": deepcopy(checked["review_response"]),
        "resolved_targets": targets,
    }


def repair_context_from_upstream(upstream_run, material):
    """Rebuild feedback from its explicit owner and fixed initial-review stage."""
    from skillflow.common.upstream import checked_run_path
    from skillflow.propagation.review.refinement import load_refinement_inputs
    from skillflow.propagation.review.runner import load_review_run

    owner = checked_run_path(upstream_run)
    original = load_refinement_inputs(owner)
    if canonical_sha256(original["material"]) != canonical_sha256(material):
        raise ValueError("Repair material differs from its refinement owner")
    reviewed = load_review_run(owner / "initial-review")
    if reviewed["result"]["status"] != "complete":
        raise ValueError("Repair requires a validated completed initial review")
    return build_repair_context(material, original["raw_annotation"],
        reviewed["material"], reviewed["result"]["review"])


def load_repair_context(run_dir, *, material=None, manifest=None):
    """Load no feedback copy: verify the owner, rebuild, and check the saved digest."""
    from skillflow.common.upstream import checked_run_path, resolve_run_reference
    from skillflow.propagation.annotation.inputs import read_component, load_prepared_material

    directory = checked_run_path(run_dir)
    manifest = read_component(directory / "manifest.json") if manifest is None else manifest
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if canonical_sha256(unsigned) != manifest.get("manifest_sha256"):
        raise ValueError("Annotation manifest identity differs")
    if (directory / "inputs/repair-context.json").exists():
        raise ValueError("Repair context must not duplicate its canonical owner")
    if manifest.get("request_kind") == "base":
        context = None
    elif manifest.get("request_kind") == "repair":
        if manifest.get("upstream") is None:
            raise ValueError("Persistent repair requires an explicit refinement owner")
        material = load_prepared_material(directory) if material is None else material
        context = repair_context_from_upstream(resolve_run_reference(directory, manifest["upstream"]), material)
    else:
        raise ValueError("Unknown annotation request kind")
    if canonical_sha256(context) != manifest.get("repair_context_sha256"):
        raise ValueError("Annotation repair request identity differs")
    return context
