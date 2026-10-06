"""Explicit, reproducible repair request context; never a hidden prompt suffix."""
from __future__ import annotations

from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.material import checked_material

REPAIR_CONTEXT_VERSION = "skillflow-annotation-repair-context-v1"


def build_repair_context(material, previous_raw_annotation, review_material, review_response):
    from skillflow.propagation.review.material import prepare_review_material
    from skillflow.propagation.review.material import checked_review_material
    from skillflow.propagation.review.services import validate_response
    from skillflow.propagation.review.services import resolve_findings

    material = checked_material(material)
    checked_review = checked_review_material(review_material)
    expected = prepare_review_material(material, previous_raw_annotation)
    if checked_review != expected:
        raise ValueError("Repair review does not refer to the actual previous annotation and material")
    if hasattr(review_response, "model_dump"):
        review_response = review_response.model_dump(mode="json")
    parsed = validate_response(review_response, checked_review)
    if not parsed.findings:
        raise ValueError("An annotation repair requires concrete reviewed issues")
    response = parsed.model_dump(mode="json")
    resolved = resolve_findings(parsed, checked_review)
    return {
        "version": REPAIR_CONTEXT_VERSION,
        "previous_raw_annotation": deepcopy(previous_raw_annotation),
        "review_material": checked_review,
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
    rebuilt = build_repair_context(material, context["previous_raw_annotation"],
                                   context["review_material"], context["review_response"])
    if context != rebuilt:
        raise ValueError("Annotation repair context or resolved review targets changed")
    return rebuilt


def repair_prompt_payload(material, context):
    checked = validate_repair_context(material, context)
    if checked is None:
        return None
    # Full review input is frozen for audit, but is not redundantly sent to the
    # repair model. Current source/CFG/contracts are already in INPUT_JSON.
    return {key: checked[key] for key in
            ("previous_raw_annotation", "review_response", "resolved_targets", "identities")}
