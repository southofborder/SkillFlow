"""Sequential basic blocks and source structure."""

from __future__ import annotations

import json
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from skillflow.graph.ir.operand import Operand
from skillflow.graph.ir.operand import OperandType
from skillflow.graph.ir.instruction import IRInstruction


DataSourceKind = Literal["context", "external"] | None


def normalize_context_keys(values: list[str]) -> list[str]:
    """Normalize raw runtime context keys without merging distinct entries."""

    normalized: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise ValueError(f"context key at index {index} must be a string")
        key = value.strip()
        if not key:
            raise ValueError(f"context key at index {index} must not be empty")
        if key in seen:
            raise ValueError(f"duplicate context key {key!r}")
        seen.add(key)
        normalized.append(key)
    return normalized


class BasicBlock(BaseModel):
    """An ordered, branch-free sequence of IR instructions."""

    model_config = ConfigDict(extra="forbid")

    block_id: str
    block_name: str
    instructions: list[IRInstruction] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    data_source_kind: DataSourceKind = None

    @field_validator("block_id", "block_name")
    @classmethod
    def normalize_block_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("block ID and block identifier must not be empty")
        return value

    @model_validator(mode="after")
    def validate_block(self) -> "BasicBlock":
        errors = self._dataflow_errors()
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def read_context_keys(self) -> list[str]:
        """Return context keys acquired here, based on source structure.

        The operation name is descriptive and does not determine this category.
        """

        if self.data_source_kind != "context" or not self.instructions:
            return []
        acquisition = self.instructions[0]
        keys = [
            operand.identifier
            for operand in acquisition.inputs
            if operand.type is OperandType.CONTEXT_KEY
            and operand.identifier is not None
        ]
        return list(dict.fromkeys(keys))

    def produced_result_ids(self) -> list[str]:
        """Return the instruction result names this block defines, in definition order."""

        names: list[str] = []
        for instruction in self.instructions:
            for operand in instruction.outputs:
                if (
                    operand.type is OperandType.RESULT
                    and operand.identifier is not None
                ):
                    names.append(operand.identifier)
        return list(dict.fromkeys(names))

    def cross_block_result_ids(self) -> list[str]:
        """Return the result identifiers this block reads but does not define itself.

        Whether each of them is actually available here is a reachability
        question about the whole graph, so it is answered by the CFG layer and
        deliberately not guessed at block scope.
        """

        local = set(self.produced_result_ids())
        uses: list[str] = []
        for instruction in self.instructions:
            for operand in instruction.inputs:
                if operand.type is not OperandType.RESULT:
                    continue
                if operand.identifier is not None and operand.identifier not in local:
                    uses.append(operand.identifier)
        return list(dict.fromkeys(uses))

    def _dataflow_errors(self) -> list[str]:
        errors: list[str] = []
        instruction_ids: set[str] = set()
        produced_result_ids: set[str] = set()
        output_definitions: dict[str, str] = {}

        # A result read here may be defined by an upstream block, so an unknown
        # identifier is not a block-scope error.  Knowing which names this block
        # itself defines is still enough to catch a read placed before its own
        # definition, which no upstream block can excuse.
        block_definitions: dict[str, str] = {}
        for instruction in self.instructions:
            for operand in instruction.outputs:
                if (
                    operand.type is OperandType.RESULT
                    and operand.identifier is not None
                ):
                    block_definitions.setdefault(operand.identifier, instruction.id)

        if self.data_source_kind not in {None, "context", "external"}:
            errors.append(
                f"block {self.block_id!r}: invalid data_source_kind {self.data_source_kind!r}"
            )
        if self.data_source_kind is not None:
            if len(self.instructions) != 2:
                errors.append(
                    f"block {self.block_id!r}: source block must contain exactly "
                    "one acquisition instruction followed by a terminator"
                )
            if self.instructions:
                acquisition = self.instructions[0]
                if not acquisition.outputs:
                    errors.append(
                        f"block {self.block_id!r}, acquisition {acquisition.id!r}: "
                        "source acquisition must produce at least one result output"
                    )
                if self.data_source_kind == "context":
                    if not acquisition.inputs or any(
                        operand.type is not OperandType.CONTEXT_KEY
                        for operand in acquisition.inputs
                    ):
                        errors.append(
                            f"block {self.block_id!r}: context acquisition requires "
                            "non-empty context_key-only raw inputs"
                        )
                else:
                    if acquisition.opcode in {
                        "dispatch",
                        "return",
                    }:
                        errors.append(
                            f"block {self.block_id!r}: external source acquisition "
                            f"cannot use reserved opcode {acquisition.opcode!r}"
                        )
                    if not any(
                        operand.type
                        in {OperandType.EXTERNAL_RESOURCE, OperandType.RESULT}
                        for operand in acquisition.inputs
                    ):
                        errors.append(
                            f"block {self.block_id!r}: external source acquisition requires "
                            "an external_resource or previously produced result input"
                        )

        if not self.instructions:
            errors.append(
                f"block {self.block_id!r}: instructions must contain at least one instruction"
            )

        for position, instruction in enumerate(self.instructions):
            # A raw context key names an entry in the caller's namespace, which
            # only the acquisition can reach.  Anywhere else, data already has a
            # definition point, so referring to it by key would reintroduce the
            # shared mutable slot that result operands replace.
            if not (self.data_source_kind == "context" and position == 0):
                for input_index, operand in enumerate(instruction.inputs):
                    if operand.type is OperandType.CONTEXT_KEY:
                        errors.append(
                            f"block {self.block_id!r}, instruction {instruction.id!r}, "
                            f"input[{input_index}]: context_key {operand.identifier!r} is only "
                            "allowed in a context source acquisition; refer to the result "
                            "produced by the defining instruction instead"
                        )
            if instruction.opcode in {"dispatch", "return"} and instruction.outputs:
                errors.append(
                    f"block {self.block_id!r}, instruction {instruction.id!r}: "
                    f"{instruction.opcode} must not produce outputs"
                )
            if instruction.id in instruction_ids:
                errors.append(
                    f"block {self.block_id!r}, instruction[{position}] {instruction.id!r}: "
                    "duplicate instruction id"
                )
            instruction_ids.add(instruction.id)

            for input_index, operand in enumerate(instruction.inputs):
                if operand.type is not OperandType.RESULT:
                    continue
                # Operand validation normally guarantees an identifier; this check
                # keeps the method safe for objects built with model_construct.
                if operand.identifier is None or not operand.identifier.strip():
                    errors.append(
                        f"block {self.block_id!r}, instruction {instruction.id!r}, "
                        f"input[{input_index}]: RESULT requires a non-empty result identifier"
                    )
                elif (
                    operand.identifier not in produced_result_ids
                    and operand.identifier in block_definitions
                ):
                    # Defined in this block, but only later.  No upstream block
                    # can supply it, so the ordering is wrong regardless of the
                    # rest of the graph.  Names absent from this block entirely
                    # are resolved by the CFG-level reachability pass.
                    semantic_label = (
                        f" ({operand.semantic_name!r})"
                        if operand.semantic_name
                        and operand.semantic_name != operand.identifier
                        else ""
                    )
                    errors.append(
                        f"block {self.block_id!r} ({self.block_name}), instruction {instruction.id!r}, "
                        f"input[{input_index}]: RESULT {operand.identifier!r}{semantic_label} is read before "
                        f"instruction {block_definitions[operand.identifier]!r} defines it"
                    )

            for output_index, operand in enumerate(instruction.outputs):
                if operand.type is not OperandType.RESULT:
                    errors.append(
                        f"block {self.block_id!r}, instruction {instruction.id!r}, "
                        f"output[{output_index}]: outputs must have type RESULT"
                    )
                    continue
                if operand.identifier is None or not operand.identifier.strip():
                    errors.append(
                        f"block {self.block_id!r}, instruction {instruction.id!r}, "
                        f"output[{output_index}]: output requires a non-empty result identifier"
                    )
                    continue
                if operand.identifier in output_definitions:
                    first_instruction = output_definitions[operand.identifier]
                    errors.append(
                        f"block {self.block_id!r}, instruction {instruction.id!r}, "
                        f"output[{output_index}]: result identifier {operand.identifier!r} is already "
                        f"defined by instruction {first_instruction!r}"
                    )
                else:
                    output_definitions[operand.identifier] = instruction.id
                    produced_result_ids.add(operand.identifier)

            if position < len(self.instructions) - 1 and instruction.opcode in {
                "dispatch",
                "return",
            }:
                errors.append(
                    f"block {self.block_id!r}: terminator {instruction.id!r} "
                    "must be the final instruction"
                )

        if self.instructions:
            terminator = self.instructions[-1]
            if terminator.opcode not in {"dispatch", "return"}:
                errors.append(
                    f"block {self.block_id!r}: last instruction {terminator.id!r} "
                    f"must have opcode DISPATCH or RETURN, got {terminator.opcode}"
                )

        return errors

    def validate_dataflow(self) -> bool:
        """Validate result definitions, source shape, and terminator placement.

        Whether a result has a producer that can reach this block is checked
        separately by the CFG integrity validator.

        Returns ``True`` for a valid block and raises ``ValueError`` containing
        all discovered violations otherwise.
        """

        errors = self._dataflow_errors()
        if errors:
            raise ValueError("; ".join(errors))
        return True

    def to_json(self) -> str:
        """Return a readable JSON representation of this basic block."""

        # Pydantic 2.5 does not yet expose ``ensure_ascii`` on
        # ``model_dump_json``.  Dump through Pydantic first (so enums and other
        # model values are normalized), remove null placeholder values from
        # non-literal operands, then format with stdlib JSON to keep non-ASCII
        # prompts readable.  A literal ``None`` remains representable as JSON
        # ``null``.
        payload = self.model_dump(mode="json")
        for instruction in payload["instructions"]:
            for operand in [*instruction["inputs"], *instruction["outputs"]]:
                if operand["type"] != OperandType.LITERAL.value:
                    operand.pop("literal_value", None)
        return json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
