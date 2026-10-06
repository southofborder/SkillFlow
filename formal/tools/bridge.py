"""Field-schema boundary and lossless rule-relevant projection to the Lean core.

The bridge supplies facts, never rule outcomes or a precomputed adjacency matrix.
Field parsing uses the same production schema as full Python validation; the
three graph-rule validators are deferred to each independent implementation.
No Skill instructions, metadata, resources, scripts, or condition text execute.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from skillflow.common.paths import project_root, resolve_material_path
PACKAGE = project_root()


from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.ir.validation import _cfg_field_schema_validator

PROTOCOL_VERSION = "skill-ir-core-v1"


def json_bytes(value: Any) -> bytes:
    """Hash the supplied JSON while retaining object storage order and lists."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def json_hash(value: Any) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def parse_fields(raw: Any) -> ControlFlowGraph:
    """Normalize fields exactly as production does, without deciding graph rules."""
    return _cfg_field_schema_validator().validate_python(raw)


def python_accept(raw: Any) -> tuple[bool, str | None]:
    """Run the actual public constructor AND complete public integrity checker."""
    try:
        ControlFlowGraph.model_validate(raw).validate_integrity()
    except (ValueError, TypeError) as exc:
        return False, str(exc)
    return True, None


class _Names:
    """Injective namespace: references also allocate IDs, including dangling ones."""

    def __init__(self) -> None:
        self.ids: dict[str, int] = {}

    def __call__(self, value: str) -> int:
        if value not in self.ids:
            self.ids[value] = len(self.ids)
        return self.ids[value]


def project(graph: ControlFlowGraph) -> dict[str, Any]:
    """Keep all rule-relevant occurrences, ordering, endpoints, and conditions.

    Business opcode strings collapse because current rules distinguish only
    dispatch/return. Literal payloads, labels, metadata, constraints and draft
    IDs do not participate in any integrity rule, after schema validation.
    Result, block and instruction names use separate injective namespaces.
    Context/resource strings retain their exact normalized identity.
    """
    block_names, instruction_names, result_names = _Names(), _Names(), _Names()

    def operand(value: Any) -> dict[str, Any]:
        kind = value.type.value
        if kind == "literal":
            return {"kind": "literal"}
        if kind == "result":
            return {"kind": "result", "id": result_names(value.identifier)}
        return {"kind": {"context_key": "context", "external_resource": "external"}[kind], "id": value.identifier}

    def instruction(value: Any) -> dict[str, Any]:
        return {
            "id": instruction_names(value.id),
            "opcode": value.opcode if value.opcode in {"return", "dispatch"} else "business",
            "inputs": [operand(item) for item in value.inputs],
            "outputs": [operand(item) for item in value.outputs],
        }

    # No sets or maps replace these lists: duplicate outputs/instructions/edges
    # remain visible to Lean, even when Python would reject them immediately.
    return {
        "entry": block_names(graph.entry_block_id),
        "blocks": [
            {"key": block_names(key), "id": block_names(block.block_id),
             "source": block.data_source_kind or "none",
             "instructions": [instruction(item) for item in block.instructions]}
            for key, block in graph.blocks.items()
        ],
        "edges": [
            {"source": block_names(edge.source_block_id),
             "target": block_names(edge.target_block_id), "condition": edge.condition_text}
            for edge in graph.edges
        ],
        "contexts": list(graph.declared_context_keys),
    }


def project_raw(raw: Any) -> dict[str, Any]:
    return project(parse_fields(raw))
