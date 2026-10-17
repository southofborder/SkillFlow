"""Strict, stage-local sensitivity and sink comparisons.

The conclusion concerns supported preservation rules and declared sensitivity;
it is neither an execution observation nor an irreplacability proof.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

from skillflow.common.source_evidence import Text
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.data.models import PathStep
from .demand_results import ActualPayload, Derivation


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
    path: RangePath


class DataReview(Strict):
    id: Text
    operation_id: Text
    input_index: Index
    derivation_id: Text
    conclusion: Literal["excess_supported", "possible_excess", "no_excess_established"]
    reason: Text
    demand_refs: list[Text]
    reduction: FieldReduction | None


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


class SensitivityResult(Strict):
    schema_version: Literal["skillflow-sensitivity-review-v3"]
    status: Literal["complete", "partial"]
    sinks: list[SinkReview]
    derivations: SharedDerivations
    diagnostics: list[Diagnostic]
    coverage: Coverage


def resolve_data_review(review: dict, sink: dict, derivations: dict) -> dict:
    """Resolve a compact row for checks and display without mutating wire data.

    The original input_index is an operation slot, not an index in the filtered
    payload list. Range truth belongs to the referenced derivation; applicable
    limitations belong to the sink. Neither can be overridden on a review.
    """
    checked = DataReview.model_validate(review).model_dump(mode="json")
    identity = checked["derivation_id"]
    if identity not in derivations:
        raise ValueError("Dangling sensitivity review derivation")
    signal = SensitivityDerivation.model_validate(derivations[identity]).model_dump(mode="json")
    return {**deepcopy(checked), **{key: deepcopy(signal[key]) for key in (
        "data_id", "label", "property", "path", "excluded_paths", "relation", "declaration_id")},
        "limitations": deepcopy(sink["limitations"])}
