"""Single injected model call and strict evidence/coverage validation."""

from __future__ import annotations
from skillflow.propagation.contracts.references import cfg_instructions

from typing import Any, Protocol

from pydantic import ValidationError

from skillflow.common.source_evidence import _json_object
from skillflow.propagation.contracts.specs import iter_located_spec_evidence
from skillflow.common.source_evidence import json_pointer
from skillflow.propagation.contracts.specs import validate_specs

from skillflow.propagation.material import check_evidence
from skillflow.propagation.material import checked_material
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.profiles import AnnotationResponse
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.contracts.profiles import FailureResponse
from skillflow.propagation.contracts.specs import ProcessingSpec, RawForEachSpec
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.common.validation import StructuralValidationError, structural_error, validation_at, schema_error
from skillflow.common.structural_correction import correct_response


def parse_candidate_json(raw):
    """Only this candidate parsing boundary classifies JSON representation errors."""
    try:
        return _json_object(raw)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error


def _candidate_model(model, value):
    try:
        return model.model_validate(value)
    except ValidationError as error:
        diagnostic = schema_error(error, candidate=value, schema=model.model_json_schema())
        # The stage owns its expression grammar. Common correction only
        # displays this deterministic, error-selected syntax fragment.
        for row in diagnostic.diagnostics:
            parts = row["path"].split("/")
            if "atomic_ops" not in parts or "expression" not in parts:
                continue
            operation_end = parts.index("atomic_ops") + 2
            if operation_end >= len(parts) or parts[operation_end] != "expression":
                continue
            current = value
            try:
                for token in parts[1:operation_end]:
                    token = token.replace("~1", "/").replace("~0", "~")
                    current = current[int(token)] if isinstance(current, list) else current[token]
            except (KeyError, IndexError, ValueError, TypeError):
                continue
            if isinstance(current, dict) and current.get("op") in {"compute", "filter_items"}:
                row["context"]["format_example"] = (
                    'Wrapper syntax: operation.expression = {"expression": <DemandExpression>, '
                    '"evidences": [<TaskEvidence>, ...]}. Angle-bracket names denote existing schema types, '
                    'not literal response values. Keep the supported expression; add real source spans '
                    'under evidences. Do not attach the bare {"op":...} expression directly to operation.expression.')
                break
        raise diagnostic from error


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
        ("ir_semantics", "locations", "sink_boundaries", "task_ref", "realizations", "demands", "expressions")}).model_dump(mode="json")


def _validate_response(raw: Any, material: dict[str, Any], response_type) -> dict[str, Any]:
    material = checked_material(material)
    raw = parse_candidate_json(raw)
    if raw.get("outcome") == "cannot_assess":
        failure = _candidate_model(FailureResponse, raw).failure
        failure_errors = []
        if not set(failure.instruction_ids) <= set(cfg_instructions(material["cfg"])):
            failure_errors.extend(structural_error("instruction_reference", "/failure/instruction_ids",
                "semantic failure references an unknown IR",
                allowed=sorted(cfg_instructions(material["cfg"]))).diagnostics)
        for index, evidence in enumerate(failure.evidences):
            try:
                with validation_at(f"/failure/evidences/{index}"):
                    check_evidence(evidence.model_dump(mode="json"), material)
            except StructuralValidationError as error:
                failure_errors.extend(error.diagnostics)
        if failure_errors:
            raise StructuralValidationError(failure_errors)
        from skillflow.common.semantic_failure import SemanticFailure
        raise SemanticFailure(failure.model_dump(mode="json"))
    annotation = (_candidate_model(response_type, raw) if response_type is RawAnnotationResponse
                  else response_type.model_validate(raw))
    parsed = annotation.model_dump(mode="json")
    expected = set(cfg_instructions(material["cfg"]))
    actual = set(parsed["ir_semantics"])
    if actual != expected:
        raise structural_error("instruction_coverage", "/ir_semantics",
                               f"IR semantics coverage mismatch: missing={sorted(expected-actual)}, unexpected={sorted(actual-expected)}")
    diagnostics = []
    def check_modes(events, path):
        for index, event in enumerate(events):
            position = path + f"/{index}"
            if isinstance(event, RawForEachSpec):
                check_modes(event.body, position + "/body")
            elif isinstance(event, ProcessingSpec) and event.mode == "local":
                # Typed evidence category is independent of citation validity;
                # each citation is checked below at its actual candidate path.
                if not any(hasattr(item, "file") or hasattr(item, "target") for item in event.evidences):
                    diagnostics.extend(structural_error("mechanism_evidence_reference", position + "/evidences",
                                           "local processing requires source or CFG mechanism evidence").diagnostics)
    if response_type is RawAnnotationResponse:
        for ir_id, spec in annotation.ir_semantics.items():
            check_modes(spec.events, json_pointer("ir_semantics", ir_id, "events"))
    specs_valid = True
    try:
        validate_specs(material["cfg"], annotation)
    except StructuralValidationError as error:
        specs_valid = False
        diagnostics.extend(error.diagnostics)
    evidence_items = [(json_pointer("location_evidences", location_id, index), evidence)
                      for location_id, evidences in annotation.location_evidences.items()
                      for index, evidence in enumerate(evidences)]
    for path, evidence in [*evidence_items, *iter_located_spec_evidence(annotation)]:
        try:
            with validation_at(path):
                check_evidence(evidence.model_dump(mode="json"), material)
        except StructuralValidationError as error:
            diagnostics.extend(error.diagnostics)
    from skillflow.propagation.contracts.joint import normalize_joint_semantics, validate_compiled_joint_semantics
    if response_type is RawAnnotationResponse and specs_valid:
        # Citation validity does not affect goal coordinates or realization
        # status. Collect those independent errors in the same correction.
        # Invalid transfer references suppress dependent joint checks.
        try:
            normalize_joint_semantics(parsed, material)
        except StructuralValidationError as error:
            diagnostics.extend(error.diagnostics)
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    if response_type is not RawAnnotationResponse:
        validate_compiled_joint_semantics(parsed, material)
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
    from skillflow.propagation.annotation.compiler import compile_response as compile_processing
    return compile_processing(raw, material)


def annotate_skill(source: dict[str, Any], cfg: dict[str, Any], *, task_baseline, client: CompletionClient,
                   user_request=None, stop_event=None) -> dict[str, Any]:
    """Obtain a structurally valid whole-graph candidate; semantic review is separate."""
    material = prepare_material(source, cfg, task_baseline=task_baseline, user_request=user_request)
    return correct_response(build_prompt(material), complete=client.complete,
                            validate=lambda response: validate_response(response, material),
                            stop_event=stop_event)
