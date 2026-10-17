"""Source-only task baseline, physical source accounting, and sealed identity.

Checks establish representation and provenance, never completeness, semantic
support, minimality, or compliance with a natural-language obligation.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from skillflow.common.inputs.snapshot import _member_path
from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import (
    Digest, Text, _json_object, _require_json, extract_source_lines, nonempty_source_lines,
)
from skillflow.common.validation import structural_error, schema_error
from skillflow.propagation.contracts.references import CFGTarget

TASK_SCHEMA_VERSION = "skillflow-task-v3"
TaskBasis = Literal["user_request", "declared_skill"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, revalidate_instances="always")


class TaskSourceSpan(_Strict):
    file: Text
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def ordered_lines(self):
        if self.end_line < self.start_line:
            raise ValueError("source end_line precedes start_line")
        return self


class TaskEvidence(TaskSourceSpan):
    """An exact physical span with an unverified relevance explanation."""
    reason: Text


def _unique_evidences(evidences):
    spans = [(x.file, x.start_line, x.end_line) for x in evidences]
    if len(set(spans)) != len(spans):
        raise ValueError("duplicate evidence spans within one claim")


class TaskPurpose(_Strict):
    text: Text
    evidences: list[TaskEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def distinct_evidence(self):
        _unique_evidences(self.evidences)
        return self


class TaskBinding(_Strict):
    """A later realization correspondence; deliberately absent from Task."""
    target: CFGTarget
    reason: Text


class TaskRequirement(_Strict):
    id: Text
    text: Text
    evidences: list[TaskEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def distinct_references(self):
        _unique_evidences(self.evidences)
        return self


class SourceAccounting(TaskSourceSpan):
    disposition: Literal["requirement", "supporting_context", "implementation_fact",
                         "capability", "example", "not_applicable", "unresolved"]
    requirement_ids: list[Text]
    issue_ids: list[Text]
    reason: Text

    @model_validator(mode="after")
    def references_and_disposition(self):
        for values in (self.requirement_ids, self.issue_ids):
            if len(values) != len(set(values)):
                raise ValueError("duplicate source-accounting references")
        if self.disposition == "requirement" and not self.requirement_ids:
            raise ValueError("requirement disposition requires requirement_ids")
        if self.disposition == "unresolved" and not self.issue_ids:
            raise ValueError("unresolved disposition requires issue_ids")
        return self


class TaskIssue(_Strict):
    id: Text
    kind: Literal["conflict", "ambiguity"]
    evidences: list[TaskEvidence] = Field(min_length=1)
    requirement_ids: list[Text]
    resolution: Literal["resolved", "unresolved"]
    reason: Text

    @model_validator(mode="after")
    def distinct_references(self):
        _unique_evidences(self.evidences)
        if len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("duplicate issue requirement references")
        return self


class CandidateTask(_Strict):
    purpose: TaskPurpose
    requirements: list[TaskRequirement] = Field(min_length=1)
    source_accounting: list[SourceAccounting] = Field(min_length=1)
    issues: list[TaskIssue]

    @model_validator(mode="after")
    def unique_identifiers(self):
        for rows, label in ((self.requirements, "requirement"), (self.issues, "issue")):
            identities = [entry.id for entry in rows]
            if len(set(identities)) != len(identities):
                raise ValueError("duplicate " + label + " identifiers")
        return self


class Task(CandidateTask):
    schema_version: Literal["skillflow-task-v3"] = TASK_SCHEMA_VERSION
    basis: TaskBasis
    source_sha256: Digest
    user_request_sha256: Digest | None
    task_sha256: Digest

    @model_validator(mode="after")
    def sealed_identity(self):
        if (self.basis == "user_request") != (self.user_request_sha256 is not None):
            raise ValueError("Task basis and user-request identity differ")
        if canonical_sha256(self.model_dump(mode="json", exclude={"task_sha256"})) != self.task_sha256:
            raise ValueError("Task sealed identity differs")
        return self


class TaskReference(_Strict):
    schema_version: Literal["skillflow-task-reference-v1"] = "skillflow-task-reference-v1"
    task_schema_version: Literal["skillflow-task-v3"] = TASK_SCHEMA_VERSION
    task_sha256: Digest
    source_sha256: Digest
    user_request_sha256: Digest | None
    basis: TaskBasis


TaskRepairCode = Literal[
    "missing_requirement", "unsupported_requirement", "broadened_requirement",
    "condition_scope", "atomicity", "conflict_resolution", "source_disposition",
]


class TaskRepairObjection(_Strict):
    """No explanations, graph targets, demands, or arbitrary feedback context."""
    code: TaskRepairCode
    source_spans: list[TaskSourceSpan] = Field(min_length=1)
    requirement_ids: list[Text]

    @model_validator(mode="after")
    def unique_references(self):
        spans = [(x.file, x.start_line, x.end_line) for x in self.source_spans]
        if len(spans) != len(set(spans)) or len(self.requirement_ids) != len(set(self.requirement_ids)):
            raise ValueError("duplicate Task repair references")
        return self


def task_source_files(source: dict[str, Any], *, user_request: str | None = None) -> dict[str, str]:
    """Namespace readable frozen members without changing paths or contents."""
    if not isinstance(source, dict) or not isinstance(source.get("files"), list):
        raise ValueError("source must contain its readable file list")
    result: dict[str, str] = {}
    for entry in source["files"]:
        if not isinstance(entry, dict) or type(entry.get("path")) is not str or type(entry.get("content")) is not str:
            raise ValueError("source file must have a string path and content")
        path = entry["path"]
        if _member_path(path) != path:
            raise ValueError("source paths must retain their canonical relative spelling")
        name = f"skill/{path}"
        if name in result:
            raise ValueError("duplicate source file path")
        result[name] = entry["content"]
    if not result:
        raise ValueError("source must contain at least one readable file")
    if user_request is not None:
        if type(user_request) is not str or not user_request.strip():
            raise ValueError("user task must be nonempty text when provided")
        result["task/user-request.txt"] = user_request
    return result


def user_request_digest(text):
    return None if text is None else hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_task_target_index(cfg):
    """Transient graph lookup for realizations, never Task extraction input."""
    from skillflow.graph.validation import checked_cfg
    from skillflow.propagation.contracts.references import cfg_target_index
    return cfg_target_index(checked_cfg(cfg))


def _check_span(span, source_files, pointer):
    if span.file not in source_files:
        raise structural_error("evidence_file", pointer, "source file is not in the frozen source table: " + span.file)
    try:
        extract_source_lines(source_files[span.file], span.start_line, span.end_line)
    except ValueError as error:
        raise structural_error("evidence_span", pointer, str(error)) from error


def _candidate(value):
    if isinstance(value, CandidateTask):
        value = value.model_dump(mode="json")
    try:
        if isinstance(value, dict):
            _require_json(value, "")
        value = _json_object(value)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    try:
        return CandidateTask.model_validate(value)
    except ValidationError as error:
        raise schema_error(error, candidate=value, schema=CandidateTask.model_json_schema()) from error


def validate_task_candidate(candidate, *, source_files, basis, source_sha256=None) -> Task:
    """Validate physical accounting and seal, without interpreting requirements."""
    parsed = _candidate(candidate)
    has_request = "task/user-request.txt" in source_files
    if basis not in ("user_request", "declared_skill") or has_request != (basis == "user_request"):
        raise ValueError("task basis differs from the supplied source identity")
    if has_request and not any(x.file == "task/user-request.txt" for x in parsed.purpose.evidences):
        raise structural_error("task_purpose_evidence", "/purpose/evidences", "user-task purpose must cite the supplied user task")
    requirement_ids, issue_ids = {x.id for x in parsed.requirements}, {x.id for x in parsed.issues}
    for index, claim in enumerate([parsed.purpose, *parsed.requirements]):
        prefix = "/purpose" if index == 0 else f"/requirements/{index - 1}"
        for number, evidence in enumerate(claim.evidences):
            _check_span(evidence, source_files, f"{prefix}/evidences/{number}")
    for index, issue in enumerate(parsed.issues):
        if not set(issue.requirement_ids) <= requirement_ids:
            raise structural_error("requirement_reference", f"/issues/{index}/requirement_ids", "unknown Task requirement")
        for number, evidence in enumerate(issue.evidences):
            _check_span(evidence, source_files, f"/issues/{index}/evidences/{number}")
    expected, coverage = nonempty_source_lines(source_files), Counter()
    accounted_requirements, accounted_issues = set(), set()
    for index, entry in enumerate(parsed.source_accounting):
        pointer = f"/source_accounting/{index}"
        _check_span(entry, source_files, pointer)
        if not set(entry.requirement_ids) <= requirement_ids or not set(entry.issue_ids) <= issue_ids:
            raise structural_error("source_accounting_reference", pointer, "unknown requirement or issue")
        accounted_requirements.update(entry.requirement_ids)
        accounted_issues.update(entry.issue_ids)
        for number in range(entry.start_line, entry.end_line + 1):
            if (entry.file, number) in expected:
                coverage[(entry.file, number)] += 1
    missing = sorted(expected - set(coverage))
    repeated = sorted(key for key, count in coverage.items() if count != 1)
    if missing or repeated:
        raise structural_error("source_accounting_coverage", "/source_accounting",
                               f"nonempty physical line coverage differs: missing={missing}, repeated={repeated}")
    if accounted_requirements != requirement_ids or accounted_issues != issue_ids:
        raise structural_error("source_accounting_claim_coverage", "/source_accounting",
                               "every requirement and issue must occur in source accounting")
    for index, requirement in enumerate(parsed.requirements):
        for evidence in requirement.evidences:
            if not any(requirement.id in row.requirement_ids and row.file == evidence.file
                       and row.start_line <= evidence.end_line and evidence.start_line <= row.end_line
                       for row in parsed.source_accounting):
                raise structural_error("source_accounting_evidence", f"/requirements/{index}/evidences",
                                       "requirement evidence has no corresponding accounting entry")
    payload = {"schema_version": TASK_SCHEMA_VERSION, "basis": basis,
               "source_sha256": source_sha256 or canonical_sha256({k: v for k, v in source_files.items()
                                                                   if k != "task/user-request.txt"}),
               "user_request_sha256": user_request_digest(source_files.get("task/user-request.txt")),
               **deepcopy(parsed.model_dump(mode="json"))}
    return Task.model_validate({**payload, "task_sha256": canonical_sha256(payload)})


def checked_task(task, *, source_files=None, source_sha256=None) -> Task:
    value = task.model_dump(mode="json") if isinstance(task, Task) else task
    parsed = Task.model_validate(value)
    if source_sha256 is not None and parsed.source_sha256 != source_sha256:
        raise ValueError("Task source identity differs")
    if source_files is not None:
        candidate = {name: value[name] for name in CandidateTask.model_fields}
        verified = validate_task_candidate(candidate, source_files=source_files, basis=parsed.basis,
                                           source_sha256=source_sha256 or parsed.source_sha256)
        if verified != parsed:
            raise ValueError("Task evidence or request identity differs")
    return parsed


def task_reference(task):
    task = checked_task(task)
    return TaskReference(task_sha256=task.task_sha256, source_sha256=task.source_sha256,
                         user_request_sha256=task.user_request_sha256, basis=task.basis).model_dump(mode="json")
