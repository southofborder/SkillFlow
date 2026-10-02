"""One injected review call, strict references and real quotations; no repair."""

from __future__ import annotations

from typing import Any, Protocol

from skill_ir.security_profile.evidence import check_evidence
from skill_ir.source_evidence import _exact, _json_object
from skill_ir.semantic_failure import SemanticFailure

from .material import checked_review_material, prepare_review_material, resolve_targets
from .models import ReviewResponse, CannotAssessResponse, RESPONSE_ADAPTER
from .prompts import build_prompt


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> Any: ...


def validate_response(raw: Any, material: dict[str, Any]) -> ReviewResponse:
    material = checked_review_material(material)
    response = RESPONSE_ADAPTER.validate_python(_json_object(raw))
    if isinstance(response, CannotAssessResponse):
        resolve_targets(response.failure.target_ids, material)
        for evidence in response.failure.evidences:
            check_evidence(evidence.model_dump(mode="json"), material)
        raise SemanticFailure(response.failure.model_dump(mode="json"))
    _exact(response.reviewed_ir_ids, set(material["instruction_index"]), "reviewed IR coverage")
    for finding in response.findings:
        resolve_targets(finding.target_ids, material)
        for evidence in finding.evidences:
            check_evidence(evidence.model_dump(mode="json"), material)
    return response


def resolve_findings(response: ReviewResponse, material: dict[str, Any]) -> list[dict[str, Any]]:
    """Attach original values and IR/pointer locations without trusting model paths."""
    material = checked_review_material(material)
    response = validate_response(response.model_dump(mode="json"), material)
    return [{**finding.model_dump(mode="json"), "targets": resolve_targets(finding.target_ids, material)}
            for finding in response.findings]


def review_annotation(material: dict[str, Any], raw_annotation: dict[str, Any], *, client: CompletionClient) -> ReviewResponse:
    prepared = prepare_review_material(material, raw_annotation)
    return validate_response(client.complete(build_prompt(prepared)), prepared)
