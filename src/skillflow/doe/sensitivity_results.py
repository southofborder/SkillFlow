"""Strict, stage-local sensitivity and sink comparisons.

The conclusion concerns supported preservation rules and declared sensitivity;
it is neither an execution observation nor an irreplacability proof.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

from skillflow.common.source_evidence import Text
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.data.models import PathStep
from .demand_results import ActualPayload, Derivation
from .constraint_results import ConstraintSupport


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Each(Strict):
    kind: Literal["each"]


RangePath = list[PathStep | Each]
Property = Literal["value", "presence", "cardinality", "shape", "truth"]
Relation = Literal["direct", "derived", "possible"]
Index = Annotated[int, Field(strict=True, ge=0)]


class SensitivityDerivation(Strict):
    declaration_id: Text
    data_id: Text
    label: Text
    property: Property
    path: RangePath
    excluded_paths: list[RangePath]
    relation: Relation
    rules: list[Text]
    parents: list[Text]


class FieldReduction(Strict):
    kind: Literal["exclude_field"]
    path: Annotated[RangePath, Field(min_length=1)]


class InputReduction(Strict):
    """Remove this supplied input, without representing it as an empty field."""
    kind: Literal["remove_input"]


class DataReview(Strict):
    id: Text
    operation_id: Text
    input_index: Index
    derivation_id: Text
    conclusion: Literal["excess_supported", "possible_excess", "no_excess_established"]
    reason: Text
    demand_refs: list[Text]
    constraint_refs: list[Text]
    assessment_refs: list[Text] = Field(default_factory=list)
    limitation_refs: list[Text] | None = None
    reduction: Annotated[FieldReduction | InputReduction, Field(discriminator="kind")] | None

    @model_serializer(mode="wrap")
    def omit_empty_assessment_refs(self, handler):
        value = handler(self)
        if not self.assessment_refs:
            value.pop("assessment_refs", None)
        if self.limitation_refs is None:
            value.pop("limitation_refs", None)
        return value


class SinkReview(Strict):
    id: Text
    boundary: SinkBoundary
    actual_payload: list[ActualPayload]
    related_requirements: list[Text]
    data_reviews: list[DataReview]
    limitations: list[Text]


class Diagnostic(Strict):
    id: Text
    code: Text
    reason: Text
    instruction_id: Text | None
    operation_id: Text | None
    blocking: bool
    affected_instruction_ids: list[Text] | None = None

    @model_serializer(mode="wrap")
    def omit_legacy_scope(self, handler):
        result = handler(self)
        if self.affected_instruction_ids is None:
            result.pop("affected_instruction_ids", None)
        return result


class SharedDerivations(Strict):
    sensitivity: dict[Text, SensitivityDerivation]
    demand: dict[Text, Derivation]


class Coverage(Strict):
    declared_scopes: Index
    declarations: Index
    resolved_declarations: Index
    sinks: Index
    expected_sinks: Index
    sensitivity_basis: Literal["declared_ranges_only"]
    demand_status: Literal["complete", "partial"]
    unresolved_boundaries: list[SinkBoundary] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def omit_empty_boundary_gaps(self, handler):
        result = handler(self)
        if not self.unresolved_boundaries:
            result.pop("unresolved_boundaries", None)
        return result


class SensitivityResult(Strict):
    schema_version: Literal["skillflow-sensitivity-review-v10", "skillflow-sensitivity-review-v11"]
    declaration_aliases: dict[Text, list[Text]] = Field(default_factory=dict)
    status: Literal["complete", "partial"]
    sinks: list[SinkReview]
    derivations: SharedDerivations
    constraints: ConstraintSupport
    diagnostics: list[Diagnostic]
    coverage: Coverage

    @model_validator(mode="before")
    @classmethod
    def versioned_alias_table(cls, value):
        if isinstance(value, dict):
            if (value.get("schema_version") == "skillflow-sensitivity-review-v11") != ("declaration_aliases" in value):
                raise ValueError("Only sensitivity review v11 carries the required declaration_aliases table")
            if value.get("schema_version") == "skillflow-sensitivity-review-v10" and isinstance(value.get("derivations"), dict):
                from .demand_results import reject_archived_selectors
                reject_archived_selectors(value["derivations"].get("demand"))
        return value

    @model_serializer(mode="wrap")
    def retain_historical_shape(self, handler):
        row = handler(self)
        if self.schema_version == "skillflow-sensitivity-review-v10":
            row.pop("declaration_aliases", None)
        return row


def resolve_data_review(review: dict, sink: dict, derivations: dict) -> dict:
    """Resolve a compact row for checks and display without mutating wire data.

    The original input_index is an operation slot, not an index in the filtered
    payload list. Range truth belongs to the referenced derivation. Current
    comparisons retain their recomputed local limitation references; legacy
    display-only rows without this field retain the boundary's complete list.
    """
    checked = DataReview.model_validate(review).model_dump(mode="json")
    identity = checked["derivation_id"]
    if identity not in derivations:
        raise ValueError("Dangling sensitivity review derivation")
    signal = SensitivityDerivation.model_validate(derivations[identity]).model_dump(mode="json")
    limitations = checked.get("limitation_refs", sink["limitations"])
    if len(limitations) != len(set(limitations)) or not set(limitations) <= set(sink["limitations"]):
        raise ValueError("Comparison limitations must reference distinct existing boundary limitations")
    return {**deepcopy(checked), **{key: deepcopy(signal[key]) for key in (
        "data_id", "label", "property", "path", "excluded_paths", "relation", "declaration_id")},
        "limitations": deepcopy(limitations)}
