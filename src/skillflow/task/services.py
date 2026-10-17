"""Injected source-only Task calls with shared mechanical correction semantics."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import Text, _json_object, extract_source_lines
from skillflow.common.structural_correction import correct_response
from skillflow.common.validation import structural_error, schema_error
from skillflow.propagation.contracts.task import TaskEvidence, task_source_files, validate_task_candidate
from skillflow.task.material import checked_task_material, prepare_task_material
from skillflow.task.prompts import build_task_prompt


class _TaskFailure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)


class _FailureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    outcome: Literal["cannot_assess"]
    failure: _TaskFailure


def validate_task_response(raw, material):
    material = checked_task_material(material)
    files = task_source_files(material["source"], user_request=material["user_request"])
    try:
        raw = _json_object(raw)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    if raw.get("outcome") == "cannot_assess":
        try:
            parsed = _FailureResponse.model_validate(raw)
        except ValidationError as error:
            raise schema_error(error, candidate=raw, schema=_FailureResponse.model_json_schema()) from error
        for index, evidence in enumerate(parsed.failure.evidences):
            if evidence.file not in files:
                raise structural_error("evidence_file", f"/failure/evidences/{index}", "unknown original source file")
            try:
                extract_source_lines(files[evidence.file], evidence.start_line, evidence.end_line)
            except ValueError as error:
                raise structural_error("evidence_span", f"/failure/evidences/{index}", str(error)) from error
        raise SemanticFailure(parsed.failure.model_dump(mode="json"))
    return validate_task_candidate(raw, source_files=files, basis=material["basis"],
                                   source_sha256=material["source"]["source_sha256"]).model_dump(mode="json")


def extract_task(source, *, client, user_request=None, revision=None, stop_event=None):
    material = prepare_task_material(source, user_request=user_request)
    return correct_response(build_task_prompt(material, revision), complete=client.complete,
                            validate=lambda raw: validate_task_response(raw, material), stop_event=stop_event)


def revise_task(source, *, previous_task, objections, client, user_request=None, stop_event=None):
    return extract_task(source, client=client, user_request=user_request, stop_event=stop_event,
                        revision={"previous_task": previous_task, "objections": objections})
