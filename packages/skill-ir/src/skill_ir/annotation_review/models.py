"""Small, independent response contract for one read-only annotation review."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, TypeAdapter, model_validator

from skill_ir.source_evidence import StrictRecord, Text

SCHEMA_VERSION = "annotation-review-v2"


class ReviewEvidence(StrictRecord):
    basis: Literal["source", "cfg", "execution_model"]
    ref_id: Text
    quote: Text


class Finding(StrictRecord):
    id: Text
    target_ids: list[Text] = Field(min_length=1)
    status: Literal["issue"]
    explanation: Text
    evidences: list[ReviewEvidence] = Field(min_length=1)
    suggestion: Text

    @model_validator(mode="after")
    def valid_finding(self) -> "Finding":
        if len(set(self.target_ids)) != len(self.target_ids):
            raise ValueError("finding target IDs must be unique")
        return self


class ReviewResponse(StrictRecord):
    outcome: Literal["completed"]
    reviewed_ir_ids: list[Text] = Field(min_length=1)
    findings: list[Finding]

    @model_validator(mode="after")
    def unique_ids(self) -> "ReviewResponse":
        if len(set(self.reviewed_ir_ids)) != len(self.reviewed_ir_ids):
            raise ValueError("reviewed IR IDs must be unique")
        ids = [item.id for item in self.findings]
        if len(set(ids)) != len(ids):
            raise ValueError("finding IDs must be unique")
        return self


class ReviewFailure(StrictRecord):
    reason: Text
    target_ids: list[Text] = Field(min_length=1)
    evidences: list[ReviewEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_targets(self):
        if len(self.target_ids) != len(set(self.target_ids)):
            raise ValueError("failure target IDs must be unique")
        return self


class CannotAssessResponse(StrictRecord):
    outcome: Literal["cannot_assess"]
    failure: ReviewFailure


RESPONSE_ADAPTER = TypeAdapter(Annotated[ReviewResponse | CannotAssessResponse,
                                       Field(discriminator="outcome")])


def review_summary(response: ReviewResponse) -> str:
    """A review outcome is separate from execution or original annotation status."""
    if response.findings:
        return "issues_found"
    return "no_material_issue"
