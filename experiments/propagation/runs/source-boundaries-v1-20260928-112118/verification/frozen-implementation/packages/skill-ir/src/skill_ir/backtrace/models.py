"""Contracts for the single source-to-controlled-text semantic review.

These records constrain evidence and coverage, not the truth of model judgments.
Graph locations are absent from model output and derived by the local service.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from skill_ir.semantic_contract import CONTRACT_VERSION, ConservativeRuleId
from skill_ir.source_evidence import (
    Digest, SourceBundle, SourceFile, SourceRef, StrictRecord, Text,
)


Basis = Literal["explicit_graph", "declared_constraint", "embedded_content", "mixed"]
FindingBasis = Literal[
    "explicit_graph", "declared_constraint", "embedded_content", "interpretation", "insufficient"
]
Status = Literal[
    "represented", "omitted", "mistranslated", "unsupported_addition", "internal_conflict", "unknown"
]


class ControlledRef(StrictRecord):
    unit_id: Text
    quote: Text | None = None


class Suggestion(StrictRecord):
    target_ids: list[Text] = Field(min_length=1)
    change: Text
    reason: Text


class ConservativeRepresentation(StrictRecord):
    rule_id: ConservativeRuleId
    candidate_fact_ids: list[Text] = Field(min_length=2)
    lost_distinctions: list[Text] = Field(min_length=1)
    reason: Text

    @model_validator(mode="after")
    def unique_candidates(self) -> "ConservativeRepresentation":
        if len(set(self.candidate_fact_ids)) != len(self.candidate_fact_ids):
            raise ValueError("candidate_fact_ids must not repeat")
        return self


class Finding(StrictRecord):
    id: Text
    kind: Literal["semantic", "context"]
    status: Status
    conservative: ConservativeRepresentation | None = None
    source_requirement: Text
    actual_representation: Text
    reason: Text
    source_refs: list[SourceRef]
    controlled_refs: list[ControlledRef]
    basis: list[FindingBasis] = Field(min_length=1)
    suggestions: list[Suggestion]
    unknown_reason: Text | None = None

    @model_validator(mode="after")
    def judgment_contract(self) -> "Finding":
        if self.status == "unknown" and not self.unknown_reason:
            raise ValueError("unknown requires an explicit unknown_reason")
        if self.status != "unknown" and self.unknown_reason is not None:
            raise ValueError("unknown_reason is reserved for unknown findings")
        if not self.source_refs and not self.controlled_refs:
            raise ValueError("finding requires source or controlled evidence")
        if self.kind == "context":
            if self.status != "represented" or self.suggestions:
                raise ValueError("context items record non-business context, without change suggestions")
            if self.conservative is not None:
                raise ValueError("conservative evidence is reserved for represented semantic findings")
            return self
        if self.conservative is not None and self.status != "represented":
            raise ValueError("conservative evidence is reserved for represented semantic findings")
        if self.status in {"represented", "mistranslated", "omitted"}:
            if not self.source_refs or not self.controlled_refs:
                raise ValueError(f"{self.status} requires source and controlled evidence")
        if self.status == "unsupported_addition" and not self.controlled_refs:
            raise ValueError("unsupported_addition requires controlled evidence")
        if self.status == "internal_conflict":
            if len({ref.unit_id for ref in self.controlled_refs}) < 2:
                raise ValueError("internal_conflict requires two distinct controlled evidence units")
        if self.status in {"omitted", "mistranslated", "unsupported_addition", "internal_conflict"}:
            if not self.suggestions:
                raise ValueError(f"{self.status} requires a located change suggestion")
        return self


class AuditResult(StrictRecord):
    schema_version: Literal[4]
    contract_version: Literal["skill-ir-semantic-contract-v3"]
    findings: list[Finding] = Field(min_length=1)
    reviewed_source_unit_ids: list[Text]
    reviewed_controlled_unit_ids: list[Text]
    notes: list[Text]

    @model_validator(mode="after")
    def record_identity(self) -> "AuditResult":
        if self.contract_version != CONTRACT_VERSION:
            raise ValueError("unsupported semantic contract version")
        findings = {finding.id: finding for finding in self.findings}
        if len(findings) != len(self.findings):
            raise ValueError("finding ids must not repeat")
        return self
