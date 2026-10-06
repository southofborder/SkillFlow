"""Strict local action annotations; no propagated data or risk conclusions."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from skillflow.propagation.contracts.specs import Evidences
from skillflow.propagation.contracts.specs import IRTransferSpec
from skillflow.propagation.contracts.specs import RawIRTransferSpec
from skillflow.propagation.contracts.specs import LocationSpec
from skillflow.propagation.contracts.boundaries import SinkBoundary

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Operator = Literal["llm", "agent_runtime", "tool", "human"]
Role = Literal["source", "sink", "transformer"]
Effect = Literal[
    "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
    "model_observe", "user_output", "transform",
]
ProfileField = Literal["operator", "roles", "effects"]
OPERATORS = ("llm", "agent_runtime", "tool", "human")
ROLES = ("source", "sink", "transformer")
EFFECTS = (
    "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
    "model_observe", "user_output", "transform",
)
PROFILE_FIELDS = ("operator", "roles", "effects")
SCHEMA_VERSION = "security-profile-v10"


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Evidence(StrictRecord):
    field: ProfileField
    value: Text | None
    basis: Literal["source", "cfg", "execution_model"]
    ref_id: Text
    quote: Text
    reason: Text
    effect_index: Annotated[int, Field(strict=True, ge=0)] | None = None

    @model_validator(mode="after")
    def effect_occurrence(self) -> "Evidence":
        if self.field == "effects" and self.value is not None:
            if self.effect_index is None:
                raise ValueError("nonempty effect evidence requires effect_index")
        elif self.effect_index is not None:
            raise ValueError("effect_index is only valid for a nonempty effect evidence")
        return self


class SecurityProfile(StrictRecord):
    operator: list[Operator]
    roles: list[Role]
    effects: list[Effect]
    evidences: list[Evidence]

    @model_validator(mode="after")
    def unique_labels(self) -> "SecurityProfile":
        for field in ("operator", "roles"):
            values = getattr(self, field)
            if len(set(values)) != len(values):
                raise ValueError(f"{field}: duplicate labels")
        for evidence in self.evidences:
            if evidence.effect_index is None:
                continue
            if evidence.effect_index >= len(self.effects):
                raise ValueError("effect_index is outside the effects sequence")
            if self.effects[evidence.effect_index] != evidence.value:
                raise ValueError("effect_index label does not match the effects sequence")
        return self


class AnnotationPayload(StrictRecord):
    profiles: dict[str, SecurityProfile]
    locations: dict[Text, LocationSpec]
    transfer_specs: dict[Text, IRTransferSpec]
    sink_boundaries: list[SinkBoundary]


class AnnotationResponse(AnnotationPayload):
    outcome: Literal["completed"]
    location_evidences: dict[Text, Evidences]

    @model_validator(mode="after")
    def complete_location_evidence(self) -> "AnnotationResponse":
        if set(self.location_evidences) != set(self.locations):
            raise ValueError("location evidence coverage must match locations exactly")
        return self


class RawSecurityProfile(SecurityProfile):
    effects: list[Literal[
        "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
        "user_output", "transform",
    ]]


class RawAnnotationResponse(StrictRecord):
    outcome: Literal["completed"]
    profiles: dict[str, RawSecurityProfile]
    locations: dict[Text, LocationSpec]
    transfer_specs: dict[Text, RawIRTransferSpec]
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
