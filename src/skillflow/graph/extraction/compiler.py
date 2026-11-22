"""Deterministic compilation and validation of LLM IR candidates."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from skillflow.graph.ir import BasicBlock
from skillflow.graph.ir import IRInstruction
from skillflow.graph.ir import Operand
from skillflow.graph.ir import OperandType
from skillflow.graph.extraction.candidate import CandidateBlock
from skillflow.graph.extraction.candidate import IRAnalysisCandidate
from skillflow.graph.ir.cfg import CFGEdge
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.ir.validation import CFGIntegrityError
from skillflow.graph.ir.validation import structure_issues
from skillflow.common.inputs.skill_package import SkillPackage
from skillflow.common.recording import canonical_sha256


class CompileDiagnostic(BaseModel):
    """A deterministic compiler or validation error."""

    model_config = ConfigDict(extra="forbid")

    code: str
    path: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class CompileResult(BaseModel):
    """The result of compiling a candidate into a canonical CFG."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    cfg: ControlFlowGraph | None = None
    diagnostics: list[CompileDiagnostic] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.cfg is not None and not self.diagnostics


def _diagnostic(
    code: str, path: str, message: str, *, context: dict[str, Any] | None = None
) -> CompileDiagnostic:
    return CompileDiagnostic(code=code, path=path, message=message, context=context or {})


def _rejected_endpoint_context(
    parsed: IRAnalysisCandidate,
    graph_fields: dict[str, Any],
    rejected_blocks: dict[str, dict[str, Any]],
    edge_indices: list[int],
    error: ValidationError,
    block_ids: list[str],
) -> dict[str, Any]:
    """Explain a constructor failure without changing or bypassing validation.

    Every constituent issue must have exact typed ownership: a missing endpoint
    whose block was rejected above, or a surviving guarded dispatch with no
    inputs. A real missing reference, absent entry, or any other defect cannot
    acquire this ownership. The
    diagnostic-only object is never returned as a CFG or used for acceptance.
    """
    errors = error.errors()
    if len(errors) != 1 or errors[0]["loc"] != () or errors[0]["type"] != "value_error":
        return {}
    issues = structure_issues(ControlFlowGraph.model_construct(**graph_fields))
    if not issues or any(issue.code not in {"EDGE_ENDPOINT_NOT_FOUND", "DISPATCH_INPUTS_MISSING"}
                         for issue in issues):
        return {}
    expected = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
    if str(errors[0].get("ctx", {}).get("error")) != expected:
        return {}
    endpoints, dispatches = [], []
    owners = {}
    for issue in issues:
        cause = issue.context
        if issue.code == "DISPATCH_INPUTS_MISSING":
            block_id = cause.get("block_id")
            matches = [bi for bi, compiled_id in enumerate(block_ids) if compiled_id == block_id]
            if len(matches) != 1 or block_id not in graph_fields["blocks"]:
                return {}
            bi = matches[0]
            block, compiled = parsed.blocks[bi], graph_fields["blocks"][block_id]
            if (not block.instructions or not compiled.instructions
                    or block.instructions[-1].opcode != "dispatch" or block.instructions[-1].inputs
                    or cause.get("instruction_id") != compiled.instructions[-1].id):
                return {}
            outgoing = [ei for ei, edge in enumerate(parsed.edges) if edge.source_block_ref == block.block_ref]
            # Missing/duplicate authored identities cannot justify local scope.
            # The selector also rejects independent ambiguity diagnostics.
            if (len(outgoing) <= 1 and not any(parsed.edges[ei].condition_text for ei in outgoing)):
                return {}
            dispatches.append({"block_index": bi, "block_ref": block.block_ref,
                "canonical_block_id": block_id, "instruction_index": len(block.instructions) - 1,
                "canonical_instruction_id": compiled.instructions[-1].id,
                "edge_indices": outgoing, "code": issue.code})
            continue
        owner = rejected_blocks.get(cause.get("block_id"))
        edge_index = cause.get("edge_index")
        if owner is None or type(edge_index) is not int or not 0 <= edge_index < len(edge_indices):
            return {}
        endpoints.append({
            "edge_index": edge_indices[edge_index],
            "canonical_edge_index": edge_index,
            "role": cause["role"],
            "block_index": owner["block_index"],
            "block_ref": owner["block_ref"],
            "canonical_block_id": owner["canonical_block_id"],
        })
        owners[owner["block_index"]] = owner
    return {"cfg_rejected_block_cascade": {
        "version": ("skillflow-cfg-rejected-block-cascade-v2" if dispatches
                    else "skillflow-cfg-rejected-block-cascade-v1"),
        "compiled_candidate_sha256": canonical_sha256(parsed.model_dump(mode="json")),
        # Bind the exact rejecting root in document JSON-pointer coordinates;
        # the explanation cannot authorize edits for a detached root message.
        "root_diagnostic_sha256": canonical_sha256({"code": "CFG_STRUCTURE_INVALID",
            "path": "", "message": _error_text(error)}),
        "complete": True,
        "rejected_blocks": [owners[index] for index in sorted(owners)],
        "endpoints": endpoints,
        **({"dispatches": dispatches, "structure_issue_count": len(issues)} if dispatches else {}),
    }}


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
        self, candidate_identifier: str, path: str, assigned: str | None = None
    ) -> tuple[str, _ResultIdAssignment | None]:
        """Reserve a canonical identifier, or report the definition that already owns it."""

        existing = self.definitions.get(candidate_identifier)
        if existing is not None:
            return existing.result_id, existing
        result_id = assigned if assigned is not None else f"result_{self.next_result_number:03d}"
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
    result_ids: dict[str, str] | None = None,
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
                _, existing = table.define(operand.identifier, output_path,
                    result_ids[operand.identifier] if result_ids is not None else None)
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


def allocate_candidate_ids(candidate: IRAnalysisCandidate, prior=None):
    """Reuse logical identities and reserve all IDs published by earlier versions."""
    tables = {"blocks": [block.block_ref for block in candidate.blocks],
        "instructions": [op.instruction_ref for block in candidate.blocks for op in block.instructions],
        "results": [operand.identifier for block in candidate.blocks for op in block.instructions
                    for operand in op.outputs if operand.type is OperandType.RESULT and operand.identifier is not None]}
    prefixes = {"blocks": "block", "instructions": "ir", "results": "result"}
    if prior is not None and (not isinstance(prior, dict) or set(prior) != set(tables)):
        raise ValueError("A prior canonical ID map must include blocks, instructions and results")
    result = {}
    for table, keys in tables.items():
        prefix = prefixes[table]
        previous = (prior or {}).get(table, {})
        if (not isinstance(previous, dict)
                or any(not isinstance(key, str) or not isinstance(value, str) or not value.strip()
                       for key, value in previous.items())
                or len(set(previous.values())) != len(previous)):
            raise ValueError("A prior canonical ID map must be one-to-one")
        assigned = dict(previous)
        used = set(assigned.values())
        occupied = [int(value[len(prefix) + 1:]) for value in used
                    if re.fullmatch(rf"{prefix}_[0-9]+", value)]
        number = max(occupied, default=0) + 1
        for key in keys:
            if key not in assigned:
                while f"{prefix}_{number:03d}" in used:
                    number += 1
                assigned[key] = f"{prefix}_{number:03d}"
                used.add(assigned[key])
                number += 1
        result[table] = assigned
    return result


def compile_candidate(
    candidate: IRAnalysisCandidate | dict[str, Any],
    package: SkillPackage | None = None,
    *, canonical_ids: dict[str, dict[str, str]] | None = None,
) -> CompileResult:
    """Compile a candidate into a stable, validated CFG."""

    del package
    parsed, diagnostics = _parse_candidate(candidate)
    if parsed is None:
        return CompileResult(diagnostics=diagnostics)
    if canonical_ids is not None:
        canonical_ids = allocate_candidate_ids(parsed, canonical_ids)

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
    block_ids = []
    next_instruction_number = 1
    result_registry = _assign_result_ids(parsed.blocks, diagnostics,
        canonical_ids["results"] if canonical_ids is not None else None)
    rejected_blocks: dict[str, dict[str, Any]] = {}

    for block_index, block in enumerate(parsed.blocks):
        block_id = (f"block_{block_index + 1:03d}" if canonical_ids is None
                    else canonical_ids["blocks"][block.block_ref])
        block_ids.append(block_id)
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

            canonical_id = (f"ir_{next_instruction_number:03d}" if canonical_ids is None
                            else canonical_ids["instructions"][instruction.instruction_ref])
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
                        constraints=instruction.constraints,
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
                constraints=block.constraints,
                data_source_kind=block.data_source_kind,
            )
        except ValidationError as error:
            diagnostic_index = len(diagnostics)
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
            rejected_blocks[block_id] = {
                "block_index": block_index,
                "block_ref": block.block_ref,
                "canonical_block_id": block_id,
                "diagnostic_index": diagnostic_index,
                "original_diagnostic": diagnostics[-1].model_dump(exclude={"context"}),
            }

    canonical_edges: list[CFGEdge] = []
    canonical_edge_indices: list[int] = []
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
        canonical_edge_indices.append(edge_index)

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

    graph_fields = dict(entry_block_id=entry_block_id, constraints=parsed.constraints,
        blocks=canonical_blocks, edges=canonical_edges,
        declared_context_keys=parsed.declared_context_keys)
    try:
        cfg = ControlFlowGraph(**graph_fields)
    except ValidationError as error:
        diagnostics.append(
            _diagnostic("CFG_STRUCTURE_INVALID", "cfg", _error_text(error), context=
                _rejected_endpoint_context(parsed, graph_fields, rejected_blocks, canonical_edge_indices, error,
                                           block_ids))
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
