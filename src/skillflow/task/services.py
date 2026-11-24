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


def validate_task_response(raw, material, *, revision=None, slot_receipt=None):
    material = checked_task_material(material)
    files = task_source_files(material["source"])
    if revision is not None:
        from skillflow.common.revision_slots import read_revision_object
        from skillflow.task.material import validate_revision
        from skillflow.task.revision import assemble_task_revision
        revision = validate_revision(revision, material)
        parsed = read_revision_object(raw)
        if parsed.value.get("outcome") != "cannot_assess":
            if slot_receipt is not None:
                from skillflow.common.recording import canonical_sha256
                slot_receipt.clear()
                slot_receipt.update(scope_sha256=canonical_sha256(revision), raw_sha256=canonical_sha256(raw),
                                    repairs=parsed.repairs, diagnostics=parsed.diagnostics)
            task, receipt = assemble_task_revision(parsed, material, revision)
            if slot_receipt is not None:
                slot_receipt.update(receipt)
            elif receipt["diagnostics"]:
                # The direct service returns only Task. Resolve outstanding
                # diagnostics in its correction loop before it can return one.
                from skillflow.common.validation import StructuralValidationError
                raise StructuralValidationError(receipt["diagnostics"])
            return task
        raw = parsed.value
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
    return validate_task_candidate(raw, source_files=files,
                                   source_sha256=material["source"]["source_sha256"]).model_dump(mode="json")


def extract_task(source, *, client, revision=None, stop_event=None):
    material = prepare_task_material(source)
    prompt = build_task_prompt(material, revision)
    if revision is not None:
        from skillflow.task.revision import TaskRevisionCorrection
        receipt = {}
        return correct_response(prompt, complete=client.complete, stop_event=stop_event,
            max_corrections=1, correction_strategy=TaskRevisionCorrection(),
            validate=lambda raw: validate_task_response(raw, material, revision=revision, slot_receipt=receipt))
    return correct_response(prompt, complete=client.complete,
                            validate=lambda raw: validate_task_response(raw, material), stop_event=stop_event)


def revise_task(source, *, previous_task, objections, client, stop_event=None):
    return extract_task(source, client=client, stop_event=stop_event,
                        revision={"previous_task": previous_task, "objections": objections})
