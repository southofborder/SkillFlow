"""Independent records and separate logical-call budgets for feedback runs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


StopStatus = Literal[
    "audit_passed", "semantic_failure", "revision_limit", "extraction_error",
    "fidelity_error", "audit_error", "interrupted",
]


class FeedbackLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    max_semantic_revisions: int = Field(default=3, ge=0, le=3)
    max_structural_repairs: int = Field(default=3, ge=0)
    max_audit_execution_retries: int = Field(default=2, ge=0, le=5)

    def logical_call_bounds(self, *, initial_graph: bool) -> dict[str, int]:
        generations = self.max_semantic_revisions + (0 if initial_graph else 1)
        extraction = generations * (self.max_structural_repairs + 1)
        audit = self.max_semantic_revisions + 1
        return {"extraction": extraction, "audit": audit, "total": extraction + audit}

    def execution_call_bounds(self, *, initial_graph: bool) -> dict[str, int]:
        logical = self.logical_call_bounds(initial_graph=initial_graph)
        audit = logical["audit"] * (1 + self.max_audit_execution_retries)
        return {"extraction": logical["extraction"], "audit": audit,
                "total": logical["extraction"] + audit}


class RoundResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: int = Field(ge=0)
    status: str
    graph_sha256: str | None = None
    decision: dict[str, Any] | None = None
    extraction: dict[str, Any] | None = None
    structural: dict[str, Any] | None = None
    fidelity: dict[str, Any] | None = None
    audit: dict[str, Any] | None = None
    audit_execution: list[dict[str, Any]] = Field(default_factory=list)
    feedback_prompt: str | None = None
    error: dict[str, Any] | None = None


class FeedbackResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[5] = 5
    identity: Literal["skill-ir-semantic-feedback-v5"] = "skill-ir-semantic-feedback-v5"
    contract_version: str
    contract_sha256: str
    representation_summary: dict[str, list[str]]
    status: StopStatus
    reason: str
    last_valid_cfg: dict[str, Any] | None = None
    passed_cfg: dict[str, Any] | None = None
    rounds: list[RoundResult]
    counts: dict[str, Any]
    limits: dict[str, Any]
    source_sha256: str
    run_id: str
    boundaries: list[str]
