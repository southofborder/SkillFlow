"""Single injected model call and strict evidence/coverage validation."""

from __future__ import annotations

from typing import Any, Protocol

from skill_ir.source_evidence import _json_object
from skill_ir.propagation.specs import iter_spec_evidence, validate_specs

from .evidence import check_evidence, checked_material, prepare_material
from .models import AnnotationPayload, AnnotationResponse, PROFILE_FIELDS
from .prompts import build_prompt


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> Any: ...


def to_payload(response: AnnotationResponse | dict) -> dict[str, Any]:
    """Explicitly project a complete response onto the four propagation fields.

    This checks the response schema, including the audit table coverage. Source
    quotations require validate_response with the prepared original material.
    """
    raw = response.model_dump(mode="python") if isinstance(response, AnnotationResponse) else response
    parsed = AnnotationResponse.model_validate(raw).model_dump(mode="json")
    return AnnotationPayload.model_validate({name: parsed[name] for name in
        ("profiles", "locations", "transfer_specs", "unresolved")}).model_dump(mode="json")


def validate_response(raw: Any, material: dict[str, Any]) -> dict[str, Any]:
    material = checked_material(material)
    annotation = AnnotationResponse.model_validate(_json_object(raw))
    parsed = annotation.model_dump(mode="json")
    expected = set(material["instruction_index"])
    actual = set(parsed["profiles"])
    if actual != expected:
        raise ValueError(f"profile coverage mismatch: missing={sorted(expected-actual)}, unexpected={sorted(actual-expected)}")
    unresolved: set[tuple[str, str]] = set()
    for item in parsed["unresolved"]:
        if item["instruction_id"] not in expected:
            raise ValueError(f"unresolved instruction does not exist: {item['instruction_id']}")
        key = item["instruction_id"], item["field"]
        if key in unresolved:
            raise ValueError(f"duplicate unresolved field: {key}")
        unresolved.add(key)
    for instruction_id, profile in parsed["profiles"].items():
        supported: set[tuple[str, str | None, int | None]] = set()
        for evidence in profile["evidences"]:
            field, value = evidence["field"], evidence["value"]
            if value is None:
                if profile[field]:
                    raise ValueError(f"null evidence is reserved for an empty field: {instruction_id}/{field}")
                if (instruction_id, field) in unresolved:
                    raise ValueError(f"empty field cannot be both inapplicable and unresolved: {instruction_id}/{field}")
            elif value not in profile[field]:
                raise ValueError(f"evidence label is absent from the profile: {instruction_id}/{field}/{value}")
            check_evidence(evidence, material)
            supported.add((field, value, evidence["effect_index"]))
        for field in PROFILE_FIELDS:
            for position, value in enumerate(profile[field]):
                index = position if field == "effects" else None
                if (field, value, index) not in supported:
                    raise ValueError(f"profile label lacks evidence: {instruction_id}/{field}/{value}/{index}")
            if not profile[field] and (field, None, None) not in supported and (instruction_id, field) not in unresolved:
                raise ValueError(f"empty profile field lacks evidence or unresolved: {instruction_id}/{field}")
    validate_specs(material["cfg"], annotation)
    for evidences in annotation.location_evidences.values():
        for evidence in evidences:
            check_evidence(evidence.model_dump(mode="json"), material)
    for evidence in iter_spec_evidence(annotation):
        check_evidence(evidence.model_dump(mode="json"), material)
    return parsed


def annotate_skill(source: dict[str, Any], cfg: dict[str, Any], *, client: CompletionClient) -> dict[str, Any]:
    """Label one complete graph exactly once; do not repair model responses."""
    material = prepare_material(source, cfg)
    response = client.complete(build_prompt(material))
    return validate_response(response, material)
