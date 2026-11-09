"""Claim evidence points into frozen source or a typed reference registry.

The program extracts the cited content. A valid location does not establish
that the content supports the accompanying semantic interpretation.
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import StrictSpec, Text
from skillflow.propagation.contracts.references import CFGTarget

SourceEvidence = TaskEvidence


class RuleEvidence(StrictSpec):
    rule_id: Text
    reason: Text


class CFGEvidence(StrictSpec):
    target: CFGTarget
    reason: Text


SpecEvidence = SourceEvidence | CFGEvidence | RuleEvidence
Evidences = Annotated[list[SpecEvidence], Field(min_length=1)]
Operator = Literal["llm", "agent_runtime", "tool", "human"]
OPERATORS = ("llm", "agent_runtime", "tool", "human")


class OperatorSourceEvidence(SourceEvidence):
    value: Operator | None


class OperatorRuleEvidence(RuleEvidence):
    value: Operator | None


class OperatorCFGEvidence(CFGEvidence):
    value: Operator | None


OperatorEvidence = OperatorSourceEvidence | OperatorCFGEvidence | OperatorRuleEvidence

Effect = Literal[
    "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
    "model_observe", "user_output", "transform",
]
RawEffect = Literal[
    "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
    "user_output", "transform",
]
EFFECTS = (
    "context_read", "context_write", "fs_read", "fs_write", "net_send", "net_receive",
    "model_observe", "user_output", "transform",
)
