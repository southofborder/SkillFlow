"""Read and serialize analysis artifacts without running extraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING
from ..ir.cfg import ControlFlowGraph

if TYPE_CHECKING:
    from ..extraction.pipeline import SkillAnalysisResult


def load_candidate_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("fixed candidate JSON must be an object")
    return value


def serialize_analysis_result(result: SkillAnalysisResult) -> dict[str, Any]:
    payload = result.model_dump(mode="json")
    if result.cfg is not None:
        payload["cfg"] = json.loads(result.cfg.to_json())
    return payload


def load_analysis_cfg(path: str | Path) -> ControlFlowGraph:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("analysis JSON must be an object")
    if payload.get("status") == "degraded":
        raise ValueError("analysis result is degraded and has no accepted CFG")
    cfg_payload = payload.get("cfg")
    if cfg_payload is None:
        raise ValueError("analysis JSON does not contain cfg")
    _check_supported_cfg_format(cfg_payload)
    try:
        cfg = ControlFlowGraph.model_validate(cfg_payload)
        cfg.validate_integrity()
    except ValueError as error:
        raise ValueError(f"analysis CFG validation failed: {error}") from error
    return cfg


def _check_supported_cfg_format(payload: Any) -> None:
    """Reject persisted CFGs written against the shared-context contract.

    An old CFG names data by shared context key and scopes its ``local_dep``
    names per block, so reading it as value references would silently merge two
    unrelated values that happen to share a identifier.  Refusing is the only
    high-precision option: a wrong reading here would quietly redraw the graph.
    """

    if not isinstance(payload, dict) or not isinstance(payload.get("blocks"), dict):
        return  # Leave malformed structures to the canonical model's diagnostics.
    for block_id, block in payload["blocks"].items():
        if not isinstance(block, dict):
            continue
        if "data_source_kind" not in block:
            raise ValueError(
                f"block {block_id!r} does not declare data_source_kind; regenerate this "
                "analysis with the current skill-ir analyzer"
            )
        legacy = {"context_exports", "context_passthrough"} & block.keys()
        if legacy:
            raise ValueError(
                f"block {block_id!r} carries the retired shared-context contract "
                f"({', '.join(sorted(legacy))}); regenerate this analysis with the "
                "current skill-ir analyzer, which references values directly"
            )
