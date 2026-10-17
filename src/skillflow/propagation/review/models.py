"""Four-axis semantic review: coverage is recorded, never semantic proof."""
from __future__ import annotations

import json
from typing import Annotated, Literal

from pydantic import Field, model_validator, TypeAdapter

from skillflow.common.source_evidence import StrictRecord, Text, SourceRef
from skillflow.propagation.contracts.evidence import SpecEvidence
from skillflow.propagation.contracts.task import TaskRepairObjection

SCHEMA_VERSION = "annotation-review-v6"
Evidence = SpecEvidence


class RawFinding(StrictRecord):
    domain: Literal["task", "annotation"]
    target_ids: list[Text] = Field(min_length=1)
    explanation: Text
    evidences: list[Evidence] = Field(min_length=1)
    suggestion: Text
    task_objection: TaskRepairObjection | None = None

    @model_validator(mode="after")
    def valid_finding(self):
        if len(set(self.target_ids)) != len(self.target_ids):
            raise ValueError("finding target IDs must be unique")
        if self.domain == "task":
            if self.task_objection is None:
                raise ValueError("task findings require a source-only task objection")
            if any(not hasattr(item, "file") for item in self.evidences):
                raise ValueError("task findings may cite only original source evidence")
        elif self.task_objection is not None:
            raise ValueError("annotation findings cannot carry task objections")
        return self


class Finding(RawFinding):
    id: Text


class RawCheck(StrictRecord):
    status: Literal["accepted", "issue"]
    reason: Text
    finding_indexes: list[Annotated[int, Field(ge=0)]]

    @model_validator(mode="after")
    def conclusion_links(self):
        if len(self.finding_indexes) != len(set(self.finding_indexes)):
            raise ValueError("check finding indexes must be unique")
        if (self.status == "issue") != bool(self.finding_indexes):
            raise ValueError("issue checks require findings; accepted checks cannot reference findings")
        return self


class CheckedConclusion(StrictRecord):
    status: Literal["accepted", "issue"]
    reason: Text
    finding_ids: list[Text]

    @model_validator(mode="after")
    def conclusion_links(self):
        if len(self.finding_ids) != len(set(self.finding_ids)):
            raise ValueError("check finding IDs must be unique")
        if (self.status == "issue") != bool(self.finding_ids):
            raise ValueError("issue checks require findings; accepted checks cannot reference findings")
        return self


class RawSourceCheck(RawCheck, SourceRef):
    pass


class SourceCheck(CheckedConclusion, SourceRef):
    pass


class RawRequirementCheck(RawCheck):
    requirement_id: Text


class RequirementCheck(CheckedConclusion):
    requirement_id: Text


class RawGoalCheck(RawCheck):
    raw_pointer: Text


class GoalCheck(CheckedConclusion):
    raw_pointer: Text


class RawReviewResponse(StrictRecord):
    outcome: Literal["completed"]
    source_checks: list[RawSourceCheck] = Field(min_length=1)
    requirement_checks: list[RawRequirementCheck] = Field(min_length=1)
    goal_checks: list[RawGoalCheck]
    reviewed_ir_ids: list[Text] = Field(min_length=1)
    findings: list[RawFinding]

    @model_validator(mode="after")
    def unique_ids(self):
        if len(set(self.reviewed_ir_ids)) != len(self.reviewed_ir_ids):
            raise ValueError("reviewed IR IDs must be unique")
        rows = [json.dumps(f.model_dump(mode="json", exclude={"id"}), ensure_ascii=False, sort_keys=True)
                for f in self.findings]
        if len(rows) != len(set(rows)):
            raise ValueError("duplicate finding records")
        return self


class ReviewResponse(RawReviewResponse):
    source_checks: list[SourceCheck] = Field(min_length=1)
    requirement_checks: list[RequirementCheck] = Field(min_length=1)
    goal_checks: list[GoalCheck]
    findings: list[Finding]

    @model_validator(mode="after")
    def generated_ids(self):
        if [f.id for f in self.findings] != [f"F{i + 1:03d}" for i in range(len(self.findings))]:
            raise ValueError("finding IDs differ from their response positions")
        return self


class ReviewFailure(StrictRecord):
    reason: Text
    target_ids: list[Text] = Field(min_length=1)
    evidences: list[Evidence] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_targets(self):
        if len(self.target_ids) != len(set(self.target_ids)):
            raise ValueError("failure target IDs must be unique")
        return self


class CannotAssessResponse(StrictRecord):
    outcome: Literal["cannot_assess"]
    failure: ReviewFailure


RESPONSE_ADAPTER = TypeAdapter(Annotated[RawReviewResponse | CannotAssessResponse, Field(discriminator="outcome")])
NORMALIZED_ADAPTER = TypeAdapter(Annotated[ReviewResponse | CannotAssessResponse, Field(discriminator="outcome")])


def review_summary(response: ReviewResponse) -> str:
    return "issues_found" if response.findings else "no_material_issue"


def task_objections(response: ReviewResponse) -> list[dict]:
    """Strict source-only projection; never forward finding prose to extraction."""
    return [finding.task_objection.model_dump(mode="json") for finding in response.findings
            if finding.domain == "task"]
