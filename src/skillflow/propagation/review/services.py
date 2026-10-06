"""One injected review call, strict references and real quotations; no repair."""

from __future__ import annotations

from typing import Any, Protocol

from skillflow.propagation.material import check_evidence
from skillflow.common.source_evidence import _exact
from skillflow.common.source_evidence import _json_object
from skillflow.common.semantic_failure import SemanticFailure

from skillflow.propagation.review.material import checked_review_material
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.material import resolve_targets
from skillflow.propagation.review.models import ReviewResponse
from skillflow.propagation.review.models import CannotAssessResponse
from skillflow.propagation.review.models import RESPONSE_ADAPTER
from skillflow.propagation.review.prompts import build_prompt


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
