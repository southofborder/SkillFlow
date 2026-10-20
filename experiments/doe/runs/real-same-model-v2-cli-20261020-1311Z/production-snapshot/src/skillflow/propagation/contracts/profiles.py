"""Strict joint IR semantics; no parallel profile or effect sequence."""
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from skillflow.propagation.contracts.evidence import Operator, OPERATORS, Effect, EFFECTS, Evidences
from skillflow.propagation.contracts.specs import IRSemantics, RawIRSemantics, LocationSpec
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.task import TaskReference
from skillflow.propagation.contracts.realizations import TaskRealization
from skillflow.propagation.contracts.demand import DemandGoal, RawDemandGoal, DemandSupplement, RawDemandSupplement

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
SCHEMA_VERSION = "security-profile-v15"


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class AnnotationPayload(StrictRecord):
    task_ref: TaskReference
    realizations: list[TaskRealization]
    demands: list[DemandGoal]
    expressions: list[DemandSupplement]
    ir_semantics: dict[Text, IRSemantics]
    locations: dict[Text, LocationSpec]
    sink_boundaries: list[SinkBoundary]


class AnnotationResponse(AnnotationPayload):
    outcome: Literal["completed"]
    location_evidences: dict[Text, Evidences]

    @model_validator(mode="after")
    def complete_location_evidence(self):
        if set(self.location_evidences) != set(self.locations):
            raise ValueError("location evidence coverage must match locations exactly")
        return self


class RawAnnotationResponse(StrictRecord):
    outcome: Literal["completed"]
    task_revision_id: Text
    realizations: list[TaskRealization]
    demands: list[RawDemandGoal]
    expressions: list[RawDemandSupplement]
    ir_semantics: dict[Text, RawIRSemantics]
    locations: dict[Text, LocationSpec]
    location_evidences: dict[Text, Evidences]

    @model_validator(mode="after")
    def complete_location_evidence(self):
        if set(self.location_evidences) != set(self.locations):
            raise ValueError("location evidence coverage must match locations exactly")
        return self


class AnnotationFailure(StrictRecord):
    reason: Text
    instruction_ids: Annotated[list[Text], Field(min_length=1)]
    evidences: Evidences

    @model_validator(mode="after")
    def unique_ir_ids(self):
        if len(self.instruction_ids) != len(set(self.instruction_ids)):
            raise ValueError("failure instruction IDs must be unique")
        return self


class FailureResponse(StrictRecord):
    outcome: Literal["cannot_assess"]
    failure: AnnotationFailure
