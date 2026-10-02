"""Deterministic compilation and validation of LLM IR candidates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..ir import BasicBlock, IRInstruction, Operand, OperandType
from .candidate import CandidateBlock, IRAnalysisCandidate
from ..ir.cfg import CFGEdge, ControlFlowGraph
from ..ir.validation import CFGIntegrityError
from ..inputs.skill_package import SkillPackage


class CompileDiagnostic(BaseModel):
    """A deterministic compiler or validation error."""

    model_config = ConfigDict(extra="forbid")

    code: str
    path: str
    message: str


class CompileResult(BaseModel):
    """The result of compiling a candidate into a canonical CFG."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    cfg: ControlFlowGraph | None = None
    diagnostics: list[CompileDiagnostic] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.cfg is not None and not self.diagnostics


def _diagnostic(code: str, path: str, message: str) -> CompileDiagnostic:
    return CompileDiagnostic(code=code, path=path, message=message)


def _error_text(error: ValidationError | ValueError) -> str:
    if isinstance(error, ValidationError):
        return "; ".join(
            f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
            for item in error.errors()
        )
    return str(error)


def _parse_candidate(
    candidate: IRAnalysisCandidate | dict[str, Any]
) -> tuple[IRAnalysisCandidate | None, list[CompileDiagnostic]]:
    if isinstance(candidate, IRAnalysisCandidate):
        return candidate, []
    try:
        return IRAnalysisCandidate.model_validate(candidate), []
    except ValidationError as error:
        diagnostics = [
            _diagnostic(
                "CANDIDATE_SCHEMA_INVALID",
                ".".join(str(part) for part in item["loc"]) or "candidate",
                item["msg"],
            )
            for item in error.errors()
        ]
        return None, diagnostics


def _copy_operand(operand: Operand, *, identifier: str | None = None) -> Operand:
    """Copy an operand, optionally renaming it to its canonical result identifier.

    The extractor's own wording is kept in ``semantic_name`` whenever a rename
    happens: ``result_007`` says nothing on its own, and backtranslation needs
    the original label to turn the reference back into a sentence.
    """

    operand_fields: dict[str, Any] = {"type": operand.type}
    if operand.identifier is not None:
        operand_fields["identifier"] = (
            identifier if identifier is not None else operand.identifier
        )
    if operand.type is OperandType.LITERAL:
        operand_fields["literal_value"] = operand.literal_value
    else:
        semantic_name = operand.semantic_name or operand.identifier
        if semantic_name is not None:
            operand_fields["semantic_name"] = semantic_name
    return Operand(**operand_fields)


@dataclass
class _ResultIdAssignment:
    """Where a candidate result identifier was first produced."""

    result_id: str
    path: str


@dataclass
class _ResultIdRegistry:
    """Map candidate result identifiers to stable, graph-global result IDs."""

    definitions: dict[str, _ResultIdAssignment] = field(default_factory=dict)
    next_result_number: int = 1

    def define(
        self, candidate_identifier: str, path: str
    ) -> tuple[str, _ResultIdAssignment | None]:
        """Reserve a canonical identifier, or report the definition that already owns it."""

        existing = self.definitions.get(candidate_identifier)
        if existing is not None:
            return existing.result_id, existing
        result_id = f"result_{self.next_result_number:03d}"
        self.next_result_number += 1
        self.definitions[candidate_identifier] = _ResultIdAssignment(result_id, path)
        return result_id, None

    def resolve(self, candidate_identifier: str | None) -> str | None:
        if candidate_identifier is None:
            return None
        definition = self.definitions.get(candidate_identifier)
        return definition.result_id if definition is not None else None


def _assign_result_ids(
    blocks: list[CandidateBlock],
    diagnostics: list[CompileDiagnostic],
) -> _ResultIdRegistry:
    """Number every produced result before any instruction is compiled.

    Definitions are collected in a pass of their own because a read may precede
    its definition in candidate order: a loop body can legitimately consume a
    result that a later block produces. Whether such a read is actually
    satisfiable is a path question, which CFG reference validation answers; here we
    only need every identifier to exist.
    """

    table = _ResultIdRegistry()
    for block_index, block in enumerate(blocks):
        for instruction_index, instruction in enumerate(block.instructions):
            instruction_path = (
                f"blocks[{block_index}].instructions[{instruction_index}]"
            )
            for output_index, operand in enumerate(instruction.outputs):
                if operand.type is not OperandType.RESULT or operand.identifier is None:
                    continue
                output_path = f"{instruction_path}.outputs[{output_index}]"
                _, existing = table.define(operand.identifier, output_path)
                if existing is not None:
                    diagnostics.append(
                        _diagnostic(
                            "DUPLICATE_RESULT_IDENTIFIER",
                            output_path,
                            f"result identifier {operand.identifier!r} is already defined at "
                            f"{existing.path}; result identifiers must be unique across the "
                            "whole graph",
                        )
                    )
    return table


def compile_candidate(
    candidate: IRAnalysisCandidate | dict[str, Any],
    package: SkillPackage | None = None,
) -> CompileResult:
    """Compile a candidate into a stable, validated CFG."""

    del package
    parsed, diagnostics = _parse_candidate(candidate)
    if parsed is None:
        return CompileResult(diagnostics=diagnostics)

    warnings = list(parsed.diagnostics)
    block_refs: dict[str, int] = {}
    for index, block in enumerate(parsed.blocks):
        if block.block_ref in block_refs:
            diagnostics.append(
                _diagnostic(
                    "DUPLICATE_BLOCK_REF",
                    f"blocks[{index}].block_ref",
                    f"block_ref {block.block_ref!r} is already defined at blocks[{block_refs[block.block_ref]}]",
                )
            )
        else:
            block_refs[block.block_ref] = index

    if parsed.entry_block_ref not in block_refs:
        diagnostics.append(
            _diagnostic(
                "ENTRY_BLOCK_NOT_FOUND",
                "entry_block_ref",
                f"entry block reference {parsed.entry_block_ref!r} does not exist",
            )
        )

    instruction_refs: dict[str, str] = {}
    canonical_blocks: dict[str, BasicBlock] = {}
    block_id_by_ref: dict[str, str] = {}
    next_instruction_number = 1
    result_registry = _assign_result_ids(parsed.blocks, diagnostics)

    for block_index, block in enumerate(parsed.blocks):
        block_id = f"block_{block_index + 1:03d}"
        block_id_by_ref.setdefault(block.block_ref, block_id)
        canonical_instructions: list[IRInstruction] = []

        for instruction_index, instruction in enumerate(block.instructions):
            instruction_path = (
                f"blocks[{block_index}].instructions[{instruction_index}]"
            )
            if instruction.instruction_ref in instruction_refs:
                diagnostics.append(
                    _diagnostic(
                        "DUPLICATE_INSTRUCTION_REF",
                        f"{instruction_path}.instruction_ref",
                        f"instruction_ref {instruction.instruction_ref!r} is already defined at {instruction_refs[instruction.instruction_ref]}",
                    )
                )
            else:
                instruction_refs[instruction.instruction_ref] = instruction_path

            canonical_id = f"ir_{next_instruction_number:03d}"
            next_instruction_number += 1
            canonical_inputs: list[Operand] = []
            canonical_outputs: list[Operand] = []

            for input_index, operand in enumerate(instruction.inputs):
                input_path = f"{instruction_path}.inputs[{input_index}]"
                if operand.type is OperandType.RESULT:
                    result_id = result_registry.resolve(operand.identifier)
                    if result_id is None:
                        # No instruction anywhere produces this identifier, so no path
                        # can ever satisfy the read. Whether an identifier that *does*
                        # exist actually reaches here is a path question, left to
                        # CFG reference validation.
                        diagnostics.append(
                            _diagnostic(
                                "RESULT_NOT_DEFINED",
                                input_path,
                                f"result {operand.identifier!r} is not produced by any "
                                "instruction in this candidate",
                            )
                        )
                        canonical_inputs.append(_copy_operand(operand))
                    else:
                        canonical_inputs.append(
                            _copy_operand(operand, identifier=result_id)
                        )
                else:
                    canonical_inputs.append(_copy_operand(operand))

            for output_index, operand in enumerate(instruction.outputs):
                output_path = f"{instruction_path}.outputs[{output_index}]"
                if operand.type is not OperandType.RESULT:
                    diagnostics.append(
                        _diagnostic(
                            "OUTPUT_NOT_RESULT",
                            output_path,
                            "instruction outputs must have type result",
                        )
                    )
                    canonical_outputs.append(_copy_operand(operand))
                    continue
                # ``_assign_result_ids`` already numbered every output and
                # reported duplicates, so the lookup cannot miss here.
                canonical_outputs.append(
                    _copy_operand(
                        operand, identifier=result_registry.resolve(operand.identifier)
                    )
                )

            try:
                canonical_instructions.append(
                    IRInstruction(
                        id=canonical_id,
                        opcode=instruction.opcode,
                        inputs=canonical_inputs,
                        outputs=canonical_outputs,
                        metadata=instruction.metadata,
                        draft_instruction_id=instruction.instruction_ref,
                    )
                )
            except ValidationError as error:
                diagnostics.append(
                    _diagnostic(
                        "IR_INSTRUCTION_INVALID",
                        instruction_path,
                        _error_text(error),
                    )
                )

        try:
            canonical_blocks[block_id] = BasicBlock(
                block_id=block_id,
                block_name=block.block_name,
                instructions=canonical_instructions,
                data_source_kind=block.data_source_kind,
            )
        except ValidationError as error:
            diagnostics.append(
                _diagnostic(
                    (
                        "RESULT_READ_BEFORE_DEFINITION"
                        if "is read before instruction" in str(error)
                        else "BASIC_BLOCK_INVALID"
                    ),
                    f"blocks[{block_index}]",
                    _error_text(error),
                )
            )

    canonical_edges: list[CFGEdge] = []
    seen_edges: set[tuple[str, str, str | None]] = set()
    for edge_index, edge in enumerate(parsed.edges):
        edge_path = f"edges[{edge_index}]"
        source_id = block_id_by_ref.get(edge.source_block_ref)
        target_id = block_id_by_ref.get(edge.target_block_ref)
        if source_id is None:
            diagnostics.append(
                _diagnostic(
                    "EDGE_SOURCE_NOT_FOUND",
                    f"{edge_path}.source_block_ref",
                    f"block reference {edge.source_block_ref!r} does not exist",
                )
            )
        if target_id is None:
            diagnostics.append(
                _diagnostic(
                    "EDGE_TARGET_NOT_FOUND",
                    f"{edge_path}.target_block_ref",
                    f"block reference {edge.target_block_ref!r} does not exist",
                )
            )
        if source_id is None or target_id is None:
            continue
        edge_key = (source_id, target_id, edge.condition_text)
        if edge_key in seen_edges:
            diagnostics.append(
                _diagnostic(
                    "DUPLICATE_EDGE",
                    edge_path,
                    f"edge {edge_key!r} is duplicated",
                )
            )
        seen_edges.add(edge_key)
        canonical_edges.append(
            CFGEdge(
                source_block_id=source_id,
                target_block_id=target_id,
                condition_text=edge.condition_text,
            )
        )

    entry_block_id = block_id_by_ref.get(parsed.entry_block_ref, "")
    if not canonical_blocks or not entry_block_id:
        if not canonical_blocks:
            diagnostics.append(
                _diagnostic(
                    "NO_VALID_BLOCKS",
                    "blocks",
                    "candidate produced no valid basic blocks",
                )
            )
        return CompileResult(diagnostics=diagnostics, warnings=warnings)

    try:
        cfg = ControlFlowGraph(
            entry_block_id=entry_block_id,
            blocks=canonical_blocks,
            edges=canonical_edges,
            declared_context_keys=parsed.declared_context_keys,
        )
    except ValidationError as error:
        diagnostics.append(
            _diagnostic("CFG_STRUCTURE_INVALID", "cfg", _error_text(error))
        )
        return CompileResult(diagnostics=diagnostics, warnings=warnings)

    try:
        cfg.validate_integrity()
    except CFGIntegrityError as error:
        diagnostics.extend(
            _diagnostic(issue.code, "cfg", issue.message) for issue in error.issues
        )
        return CompileResult(diagnostics=diagnostics, warnings=warnings)

    if diagnostics:
        return CompileResult(diagnostics=diagnostics, warnings=warnings)
    return CompileResult(cfg=cfg, warnings=warnings)
