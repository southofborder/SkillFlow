"""Read-only DOE preparation types; no sensitivity or necessity verdicts."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_serializer, model_validator

from skillflow.common.source_evidence import Text
from skillflow.graph.ir.cfg import CFGEdge
from skillflow.graph.ir.instruction import IRInstruction
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.profiles import Operator, Effect
from skillflow.propagation.contracts.specs import CaseLabel, LocationSpec, Precedence
from skillflow.propagation.data import Data
from skillflow.propagation.models import AtomicOpRecord


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Position(Strict):
    instruction_id: Text
    event_index: int = Field(ge=0)
    op_index: int = Field(ge=0)
    body_event_index: int | None = Field(default=None, ge=0)
    instance_index: int | None = Field(default=None, ge=0)


class Operation(Strict):
    position: Position
    effect: Effect | None
    record: AtomicOpRecord
    case: CaseLabel | None = None
    requires_completion: list[Text] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def optional_case(self, handler):
        value = handler(self)
        if self.case is None:
            value.pop("case", None)
        if not self.requires_completion:
            value.pop("requires_completion", None)
        return value


class Block(Strict):
    block_id: Text
    block_name: str
    instruction_ids: list[Text]
    constraints: list[str]
    data_source_kind: str | None


class Action(Strict):
    operator: list[Operator] | None

    @model_validator(mode="after")
    def unique(self):
        if self.operator is not None and len(set(self.operator)) != len(self.operator):
            raise ValueError("action labels must not repeat")
        return self


class Order(Strict):
    order: Literal["fixed", "partial"]
    precedence: list[Precedence]


class Scope(Strict):
    instruction_id: Text
    event_index: int = Field(ge=0)
    instance_index: int = Field(ge=0)
    collection: Text
    element: Text


class Link(Strict):
    kind: Literal["produces_consumes", "result_use", "saved_read", "observed_use", "result_binding", "request_response"]
    source: Text
    target: Text
    data_ids: list[Text]
    result: Text | None = None


class SharedInfo(Strict):
    entry_block_id: Text
    instructions: dict[str, IRInstruction]
    blocks: dict[str, Block]
    edges: list[CFGEdge]
    constraints: list[str]
    declared_context_keys: list[str]
    data: dict[str, Data]
    operations: dict[str, Operation]
    locations: dict[str, LocationSpec]
    actions: dict[str, Action]
    orders: dict[str, Order]
    scopes: dict[str, Scope]
    links: dict[str, Link]


class Sink(Strict):
    id: Text
    boundary: SinkBoundary
    operations: list[Text] = Field(min_length=1)


class BackwardSlice(Strict):
    data: list[Text]
    operations: list[Text]


class UsageContext(Strict):
    instructions: list[Text]
    operations: list[Text]
    links: list[Text]


class Context(Strict):
    blocks: list[Text]
    edge_indices: list[int]
    scope_ids: list[Text]
    diagnostics: list[dict[str, JsonValue]]
    partial_ir_ids: list[Text]


class SinkSlice(Strict):
    sink: Sink
    backward_slice: BackwardSlice
    usage_context: UsageContext
    context: Context


class DoeMaterial(Strict):
    schema_version: Literal["skillflow-doe-material-v3"] = "skillflow-doe-material-v3"
    source: dict[str, JsonValue]
    runtime_contract: dict[str, JsonValue]
    shared_info: SharedInfo
    sinks: list[SinkSlice]

    @model_serializer(mode="wrap")
    def graph_wire_operands(self, handler):
        value = handler(self)
        # Match ControlFlowGraph.to_json: nonliteral operands must not carry
        # literal_value, even null. Literal null remains an explicit value.
        for ir in value["shared_info"]["instructions"].values():
            for operand in [*ir["inputs"], *ir["outputs"]]:
                if operand["type"] != "literal":
                    operand.pop("literal_value", None)
                if operand.get("semantic_name") is None:
                    operand.pop("semantic_name", None)
        return value

