"""Single injected model call and strict evidence/coverage validation."""

from __future__ import annotations

from typing import Any, Protocol

from skill_ir.source_evidence import _json_object
from skill_ir.propagation.specs import iter_spec_evidence, validate_specs

from .evidence import check_evidence, checked_material, prepare_material
from .models import AnnotationPayload, AnnotationResponse, RawAnnotationResponse, FailureResponse, PROFILE_FIELDS
from .prompts import build_prompt


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> Any: ...


def to_payload(response: AnnotationResponse | dict) -> dict[str, Any]:
    """Explicitly project a complete response onto the propagation fields.

    This checks the response schema, including the audit table coverage. Source
    quotations require validate_response with the prepared original material.
    """
    raw = response.model_dump(mode="python") if isinstance(response, AnnotationResponse) else response
    parsed = AnnotationResponse.model_validate(raw).model_dump(mode="json")
    return AnnotationPayload.model_validate({name: parsed[name] for name in
        ("profiles", "locations", "transfer_specs", "sink_boundaries")}).model_dump(mode="json")


def _validate_response(raw: Any, material: dict[str, Any], response_type) -> dict[str, Any]:
    material = checked_material(material)
    raw = _json_object(raw)
    if raw.get("outcome") == "cannot_assess":
        failure = FailureResponse.model_validate(raw).failure
        if not set(failure.instruction_ids) <= set(material["instruction_index"]):
            raise ValueError("semantic failure references an unknown IR")
        for evidence in failure.evidences:
            check_evidence(evidence.model_dump(mode="json"), material)
        from skill_ir.semantic_failure import SemanticFailure
        raise SemanticFailure(failure.model_dump(mode="json"))
    annotation = response_type.model_validate(raw)
    parsed = annotation.model_dump(mode="json")
    expected = set(material["instruction_index"])
    actual = set(parsed["profiles"])
    if actual != expected:
        raise ValueError(f"profile coverage mismatch: missing={sorted(expected-actual)}, unexpected={sorted(actual-expected)}")
    for instruction_id, profile in parsed["profiles"].items():
        supported: set[tuple[str, str | None, int | None]] = set()
        for evidence in profile["evidences"]:
            field, value = evidence["field"], evidence["value"]
            if value is None:
                if profile[field]:
                    raise ValueError(f"null evidence is reserved for an empty field: {instruction_id}/{field}")
            elif value not in profile[field]:
                raise ValueError(f"evidence label is absent from the profile: {instruction_id}/{field}/{value}")
            check_evidence(evidence, material)
            supported.add((field, value, evidence["effect_index"]))
        for field in PROFILE_FIELDS:
            for position, value in enumerate(profile[field]):
                index = position if field == "effects" else None
                if (field, value, index) not in supported:
                    raise ValueError(f"profile label lacks evidence: {instruction_id}/{field}/{value}/{index}")
            if not profile[field] and (field, None, None) not in supported:
                raise ValueError(f"empty profile field lacks evidence: {instruction_id}/{field}")
    validate_specs(material["cfg"], annotation)
    for evidences in annotation.location_evidences.values():
        for evidence in evidences:
            check_evidence(evidence.model_dump(mode="json"), material)
    for evidence in iter_spec_evidence(annotation):
        check_evidence(evidence.model_dump(mode="json"), material)
    return parsed


def validate_raw_response(raw: Any, material: dict[str, Any]) -> dict[str, Any]:
    """Check the model-only processing protocol, not a compiled payload."""
    return _validate_response(raw, material, RawAnnotationResponse)


def validate_compiled_response(raw: Any, material: dict[str, Any]) -> dict[str, Any]:
    """Check compiled structure/evidence; provenance requires re-compilation."""
    return _validate_response(raw, material, AnnotationResponse)


def validate_response(raw: Any, material: dict[str, Any]) -> dict[str, Any]:
    """Validate and deterministically compile one raw model response."""
    return compile_response(raw, material)[1]


def compile_response(raw: Any, material: dict[str, Any]):
    """Public compilation service retaining raw, compiled and mapping artifacts."""
    from .compiler import compile_response as compile_processing
    return compile_processing(raw, material)


def annotate_skill(source: dict[str, Any], cfg: dict[str, Any], *, client: CompletionClient) -> dict[str, Any]:
    """Label one complete graph exactly once; do not repair model responses."""
    material = prepare_material(source, cfg)
    response = client.complete(build_prompt(material))
    return validate_response(response, material)
