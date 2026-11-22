"""Strict joint IR semantics; no parallel profile or effect sequence."""
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator, model_serializer

from skillflow.propagation.contracts.evidence import Operator, OPERATORS, Effect, EFFECTS, Evidences
from skillflow.propagation.contracts.specs import IRSemantics, RawIRSemantics, LocationSpec
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.task import TaskReference
from skillflow.propagation.contracts.realizations import TaskRealization
from skillflow.propagation.contracts.demand import DemandGoal, RawDemandGoal, DemandSupplement, RawDemandSupplement
from skillflow.propagation.contracts.limitations import ProcessingGap
from skillflow.propagation.contracts.input_requirements import CompiledInputContract
from skillflow.propagation.contracts.locations import require_address_source_evidence

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
SCHEMA_VERSION = "security-profile-v24"


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @model_serializer(mode="wrap")
    def omit_empty_processing_gaps(self, handler):
        result = handler(self)
        if not result.get("processing_gaps"):
            result.pop("processing_gaps", None)
        if not result.get("input_contracts"):
            result.pop("input_contracts", None)
        return result


class AnnotationPayload(StrictRecord):
    task_ref: TaskReference
    realizations: list[TaskRealization]
    demands: list[DemandGoal]
    expressions: list[DemandSupplement]
    ir_semantics: dict[Text, IRSemantics]
    locations: dict[Text, LocationSpec]
    sink_boundaries: list[SinkBoundary]
    processing_gaps: list[ProcessingGap] = Field(default_factory=list)
    input_contracts: list[CompiledInputContract] = Field(default_factory=list)


class AnnotationResponse(AnnotationPayload):
    outcome: Literal["completed"]
    location_evidences: dict[Text, Evidences]

    @model_validator(mode="after")
    def complete_location_evidence(self):
        if set(self.location_evidences) != set(self.locations):
            raise ValueError("location evidence coverage must match locations exactly")
        for name, location in self.locations.items():
            require_address_source_evidence(location, self.location_evidences[name])
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
    processing_gaps: list[ProcessingGap] = Field(default_factory=list)

    @model_validator(mode="after")
    def complete_location_evidence(self):
        if set(self.location_evidences) != set(self.locations):
            raise ValueError("location evidence coverage must match locations exactly")
        for name, location in self.locations.items():
            require_address_source_evidence(location, self.location_evidences[name])
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
