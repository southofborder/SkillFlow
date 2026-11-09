"""Shared forward checks and candidate preservation, never positive demands."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from skillflow.common.source_evidence import Text
from skillflow.propagation.contracts.sensitivity import SensitivityPath
from .demand_results import DemandNode


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class ConstraintCheck(Strict):
    requirement_id: Text
    raw_pointer: Text
    kind: Literal["forbid_information", "only_if", "at_most", "requires_prior", "forbid_after"]
    status: Literal["satisfied", "potential_violation", "not_established"]
    operations: list[Text]
    reasons: list[Text]
    witness: list[Text]
    structural: bool


class ChangeStep(Strict):
    node: DemandNode
    path: SensitivityPath
    rule: Text
    parents: list[Text]


class Preservation(Strict):
    constraint_id: Text
    operation_id: Text
    input_index: int = Field(ge=0)
    data_id: Text
    path: SensitivityPath
    preserved: bool
    rule: Literal["structural", "terminal_subset", "no_influence", "not_established"]
    reason: Text
    influence_refs: list[Text]


class ConstraintSupport(Strict):
    checks: dict[Text, ConstraintCheck]
    preservation: dict[Text, Preservation]
    influence: dict[Text, ChangeStep]
