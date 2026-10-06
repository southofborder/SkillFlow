"""First-stage CFG checks: structure and references, without data propagation.

Reachability only establishes that the recorded producer can reach a reader.
It does not evaluate conditions, guarantee first-iteration availability, or
establish whether the graph covers every behavior in the original Skill.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ValidationError
from pydantic_core import SchemaValidator

from .operand import OperandType

if TYPE_CHECKING:
    from .cfg import ControlFlowGraph


@dataclass(frozen=True)
class CFGIssue:
    code: str
    message: str


class CFGIntegrityError(ValueError):
    """All integrity findings, also available separately to the compiler."""

    def __init__(self, issues: list[CFGIssue]):
        self.issues = issues
        super().__init__(
            "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        )


def _schema_without_structure(schema: dict[str, Any]) -> dict[str, Any]:
    """Copy the real field schema, deferring only the existing graph rules.

    These three after-validators implement rules already checked by
    ``structure_issues``. Deferring them preserves its individual issue codes
    and lets callers examine schema-valid but structurally invalid graphs.
    All field validators, Operand source constraints, and any other validators
    stay in place. The original Pydantic schema and constructor are untouched.
    """
    from .basic_block import BasicBlock
    from .cfg import ControlFlowGraph
    from .instruction import IRInstruction

    deferred = {
        IRInstruction.validate_outputs,
        BasicBlock.validate_block,
        ControlFlowGraph.validate_structure,
    }

    def visit(value: Any) -> Any:
        if isinstance(value, list):
            return [visit(item) for item in value]
        if not isinstance(value, dict):
            return value
        copied = {key: visit(item) for key, item in value.items()}
        if (
            copied.get("type") == "function-after"
            and copied.get("function", {}).get("function") in deferred
        ):
            inner = copied["schema"]
            # References can point at the after-wrapper rather than its model.
            if "ref" in copied:
                inner["ref"] = copied["ref"]
            return inner
        return copied

    return visit(deepcopy(schema))


@lru_cache(maxsize=1)
def _cfg_field_schema_validator() -> SchemaValidator:
    """Validate the original CFG field schema independently of graph rules."""
    from .cfg import ControlFlowGraph

    return SchemaValidator(
        _schema_without_structure(ControlFlowGraph.__pydantic_core_schema__)
    )


class _SnapshotError(ValueError):
    pass


def _model_snapshot(value: Any, location: str = "cfg") -> Any:
    """Read actual fields, including extras and changes absent from fields_set.

    ``model_dump`` can omit undeclared fields; JSON export also removes illegal
    non-literal payloads. Neither is a suitable validation input. Only an
    *unset, unchanged default* may be omitted here, so an ordinary result's
    default literal_value=None stays distinct from explicitly supplying it.
    Opaque Any payloads are passed through: no validator changes their contents.
    """
    from .instruction import IRInstruction
    from .operand import Operand

    active: set[int] = set()

    def visit(item: Any, path: str) -> Any:
        if not isinstance(item, (BaseModel, dict, list, tuple)):
            return item
        if id(item) in active:
            raise _SnapshotError(f"{path}: cyclic model/container reference")
        active.add(id(item))
        try:
            if isinstance(item, BaseModel):
                fields = type(item).model_fields
                actual = dict(item.__dict__)
                actual.update(item.__pydantic_extra__ or {})
                result = {}
                for name, content in actual.items():
                    field = fields.get(name)
                    if (
                        field is not None
                        and name not in item.model_fields_set
                        and not field.is_required()
                    ):
                        default = field.get_default(call_default_factory=True)
                        if type(content) is type(default) and content == default:
                            continue
                    if (isinstance(item, Operand) and name == "literal_value") or (
                        isinstance(item, IRInstruction) and name == "metadata"
                    ):
                        result[name] = content
                    else:
                        result[name] = visit(content, f"{path}.{name}")
                return result
            if isinstance(item, dict):
                return {
                    key: visit(content, f"{path}[{key!r}]")
                    for key, content in item.items()
                }
            values = [visit(content, f"{path}[{i}]") for i, content in enumerate(item)]
            return tuple(values) if isinstance(item, tuple) else values
        finally:
            active.remove(id(item))

    return visit(value, location)


def _changed_fields(before: Any, after: Any, path: str = "cfg") -> list[str]:
    """Locate coercion, normalization, or missing in-memory default fields."""
    if before is after:
        return []
    if isinstance(before, BaseModel) and isinstance(after, BaseModel):
        if not isinstance(before, type(after)):
            return [path]
        return _changed_fields(before.__dict__, after.__dict__, path)
    if type(before) is not type(after):
        return [path]
    if isinstance(before, dict):
        changed = [f"{path}[{key!r}]" for key in before if key not in after]
        changed.extend(f"{path}[{key!r}]" for key in after if key not in before)
        for key in before:
            if key in after:
                changed.extend(
                    _changed_fields(before[key], after[key], f"{path}[{key!r}]")
                )
        return changed
    if isinstance(before, (list, tuple)):
        if len(before) != len(after):
            return [path]
        return [
            changed
            for i, (left, right) in enumerate(zip(before, after))
            for changed in _changed_fields(left, right, f"{path}[{i}]")
        ]
    return [] if before == after else [path]


def _schema_issues(graph: ControlFlowGraph) -> list[CFGIssue]:
    """Revalidate a fresh snapshot without accepting normalization as a repair."""
    try:
        snapshot = _model_snapshot(graph)
        validated = _cfg_field_schema_validator().validate_python(snapshot, strict=True)
    except ValidationError as error:
        return [
            CFGIssue(
                "CFG_SCHEMA_INVALID",
                "cfg"
                + "".join(f"[{part!r}]" for part in finding["loc"])
                + f": {finding['msg']} ({finding['type']})",
            )
            for finding in error.errors(include_url=False)
        ]
    except _SnapshotError as error:
        return [CFGIssue("CFG_SCHEMA_INVALID", str(error))]
    except RecursionError:
        return [CFGIssue("CFG_SCHEMA_INVALID", "cfg: model/container nesting is too deep")]
    return [
        CFGIssue(
            "CFG_SCHEMA_INVALID",
            f"{path}: stored value requires normalization or reconstruction",
        )
        for path in _changed_fields(graph, validated)
    ]


def block_label(graph: ControlFlowGraph, block_id: str) -> str:
    block = graph.blocks.get(block_id)
    return (
        f"block {block_id!r} ({block.block_name})" if block else f"block {block_id!r}"
    )


def result_label(result_id: str, semantic_name: str | None) -> str:
    suffix = (
        f" ({semantic_name!r})" if semantic_name and semantic_name != result_id else ""
    )
    return f"result {result_id!r}{suffix}"


def graph_adjacency(
    graph: ControlFlowGraph,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build adjacency, ignoring dangling endpoints and parallel guarded edges."""
    predecessors: dict[str, list[str]] = {block_id: [] for block_id in graph.blocks}
    successors: dict[str, list[str]] = {block_id: [] for block_id in graph.blocks}
    for edge in graph.edges:
        source, target = edge.source_block_id, edge.target_block_id
        if source not in graph.blocks or target not in graph.blocks:
            continue
        if target not in successors[source]:
            successors[source].append(target)
            predecessors[target].append(source)
    return predecessors, successors


def entry_blocks(
    graph: ControlFlowGraph, predecessors: dict[str, list[str]]
) -> list[str]:
    roots = {block_id for block_id, incoming in predecessors.items() if not incoming}
    if graph.entry_block_id in graph.blocks:
        roots.add(graph.entry_block_id)
    return sorted(roots)


def reachable_blocks(starts: list[str], successors: dict[str, list[str]]) -> set[str]:
    reached: set[str] = set()
    pending = list(starts)
    while pending:
        block_id = pending.pop()
        if block_id in reached:
            continue
        reached.add(block_id)
        pending.extend(
            target for target in successors.get(block_id, ()) if target not in reached
        )
    return reached


def structure_issues(graph: ControlFlowGraph) -> list[CFGIssue]:
    issues: list[CFGIssue] = []
    if graph.entry_block_id not in graph.blocks:
        issues.append(
            CFGIssue(
                "ENTRY_BLOCK_NOT_FOUND",
                f"entry block {graph.entry_block_id!r} does not exist in blocks",
            )
        )

    instruction_owners: dict[str, str] = {}
    for block_id, block in graph.blocks.items():
        if block_id != block.block_id:
            issues.append(
                CFGIssue(
                    "BLOCK_ID_MISMATCH",
                    f"blocks key {block_id!r} does not match BasicBlock.block_id {block.block_id!r}",
                )
            )
        for error in block._dataflow_errors():
            code = (
                "RESULT_READ_BEFORE_DEFINITION"
                if "is read before instruction" in error
                else "BASIC_BLOCK_INVALID"
            )
            issues.append(CFGIssue(code, error))
        for instruction in block.instructions:
            owner = instruction_owners.setdefault(instruction.id, block_id)
            if owner != block_id:
                issues.append(
                    CFGIssue(
                        "DUPLICATE_INSTRUCTION_ID",
                        f"{block_label(graph, block_id)}, instruction {instruction.id!r}: already defined in {block_label(graph, owner)}",
                    )
                )

    seen_edges: set[tuple[str, str, str | None]] = set()
    outgoing: dict[str, list] = {block_id: [] for block_id in graph.blocks}
    for index, edge in enumerate(graph.edges):
        edge_key = (edge.source_block_id, edge.target_block_id, edge.condition_text)
        if edge_key in seen_edges:
            issues.append(
                CFGIssue(
                    "DUPLICATE_EDGE", f"edge[{index}] is a duplicate edge: {edge_key!r}"
                )
            )
        seen_edges.add(edge_key)
        for role, block_id in (
            ("source", edge.source_block_id),
            ("target", edge.target_block_id),
        ):
            if block_id not in graph.blocks:
                issues.append(
                    CFGIssue(
                        "EDGE_ENDPOINT_NOT_FOUND",
                        f"edge[{index}] {role} block {block_id!r} does not exist",
                    )
                )
        if edge.source_block_id in outgoing:
            outgoing[edge.source_block_id].append(edge)

    for block_id, block in graph.blocks.items():
        if not block.instructions:
            continue
        terminator = block.instructions[-1]
        edges = outgoing[block_id]
        if terminator.opcode == "return" and edges:
            issues.append(
                CFGIssue(
                    "RETURN_HAS_OUTGOING_EDGES",
                    f"block {block_id!r} ends with RETURN but has outgoing edges",
                )
            )
        if terminator.opcode == "dispatch" and not edges:
            issues.append(
                CFGIssue(
                    "DISPATCH_HAS_NO_TARGET",
                    f"block {block_id!r} ends with DISPATCH but has no outgoing edges",
                )
            )
        if (
            terminator.opcode == "dispatch"
            and (len(edges) > 1 or any(edge.condition_text for edge in edges))
            and not terminator.inputs
        ):
            issues.append(
                CFGIssue(
                    "DISPATCH_INPUTS_MISSING",
                    f"block {block_id!r}: guarded or branching DISPATCH must declare condition dependencies in inputs",
                )
            )
    return issues


def integrity_issues(graph: ControlFlowGraph) -> list[CFGIssue]:
    issues = structure_issues(graph)
    predecessors, successors = graph_adjacency(graph)
    reachable = reachable_blocks(entry_blocks(graph, predecessors), successors)
    for block_id in sorted(set(graph.blocks) - reachable):
        issues.append(
            CFGIssue(
                "BLOCK_UNREACHABLE",
                f"{block_label(graph, block_id)} is unreachable from any entry root",
            )
        )

    # Record definitions before inspecting inputs: candidate order is not execution order.
    definitions: dict[str, tuple[str, str, str | None]] = {}
    declared_keys = set(graph.declared_context_keys)
    for block_id, block in graph.blocks.items():
        for key in block.read_context_keys():
            if key not in declared_keys:
                issues.append(
                    CFGIssue(
                        "CONTEXT_KEY_NOT_DECLARED",
                        f"{block_label(graph, block_id)}, instruction {block.instructions[0].id!r}: raw context key {key!r} is not declared in declared_context_keys",
                    )
                )
        for instruction in block.instructions:
            for output_index, operand in enumerate(instruction.outputs):
                if operand.type is not OperandType.RESULT or operand.identifier is None:
                    continue
                previous = definitions.get(operand.identifier)
                if previous:
                    issues.append(
                        CFGIssue(
                            "DUPLICATE_RESULT_IDENTIFIER",
                            f"{block_label(graph, block_id)}, instruction {instruction.id!r}, output[{output_index}]: {result_label(operand.identifier, operand.semantic_name)} is already defined by instruction {previous[1]!r} in {block_label(graph, previous[0])}",
                        )
                    )
                else:
                    definitions[operand.identifier] = (
                        block_id,
                        instruction.id,
                        operand.semantic_name,
                    )

    # Cache block reachability by producer, never result availability per block.
    reachable_by_producer: dict[str, set[str]] = {}
    for block_id, block in graph.blocks.items():
        for instruction in block.instructions:
            for input_index, operand in enumerate(instruction.inputs):
                if operand.type is not OperandType.RESULT or operand.identifier is None:
                    continue
                definition = definitions.get(operand.identifier)
                semantic_name = operand.semantic_name or (
                    definition[2] if definition else None
                )
                location = f"{block_label(graph, block_id)}, instruction {instruction.id!r}, input[{input_index}]: {result_label(operand.identifier, semantic_name)}"
                if definition is None:
                    issues.append(
                        CFGIssue(
                            "RESULT_NOT_DEFINED",
                            f"{location} is not available; no instruction in the graph defines it",
                        )
                    )
                    continue
                producer, instruction_id, _ = definition
                if producer == block_id:
                    # The block validator reports reads before local production, even in a loop.
                    continue
                if block_id not in reachable or producer not in reachable:
                    continue  # The unreachable component already has its own finding.
                if producer not in reachable_by_producer:
                    reachable_by_producer[producer] = reachable_blocks(
                        [producer], successors
                    )
                if block_id not in reachable_by_producer[producer]:
                    issues.append(
                        CFGIssue(
                            "RESULT_PATH_NOT_FOUND",
                            f"{location} is not available; its definition in {block_label(graph, producer)} (instruction {instruction_id!r}) does not reach here along any path",
                        )
                    )
    return issues


def validate_cfg_integrity(graph: ControlFlowGraph) -> bool:
    schema_issues = _schema_issues(graph)
    if schema_issues:
        raise CFGIntegrityError(schema_issues)
    issues = integrity_issues(graph)
    if issues:
        raise CFGIntegrityError(issues)
    return True
