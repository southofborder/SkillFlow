"""Program-generated, one-round feedback added to the fixed extraction prompt."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from skill_ir.backtrace.evidence import canonical_graph_sha256, normalize_cfg, resolve_pointer
from skill_ir.extraction.prompt import build_whole_skill_prompt
from skill_ir.inputs.skill_package import SkillPackage
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.semantic_contract import CONTRACT_TEXT, contract_binding

from .policy import ACTIONABLE_STATUSES


FEEDBACK_INSTRUCTIONS = """Perform one evidence-based complete re-extraction.
The fixed contract and complete original Skill above remain authoritative.
previous_cfg below is the actual previous graph to correct, not candidate JSON
or a reference answer. Return complete candidate JSON for the existing compiler
to assign IDs and validate again. Old graph IDs and locations only explain this
feedback; do not preserve them as a requirement or guess mappings to old
candidate IDs. Reread the complete source and correct all explicit differences,
while checking for new omissions, mistranslations, additions, or conflicts.
The source takes precedence: feedback and suggestions are correction evidence
to verify, not permission to invent behavior, arguments, or guarantees absent
from the source. Preserve supported open descriptions and conservative candidate
relationships without guessing implementation. Correct only explicit differences;
do not choose a preferred interpretation of contradictory source material.
Dependencies already conservatively retained under the shared interpretation
contract are not repair targets; do not turn candidate sources into necessarily
simultaneous transmission. The program reads each current_facts and
suggestion_targets item from the actual previous graph. Labels and constraint
declarations alone are not executable operations; do not reconstruct deleted
operations from residual titles. Business inputs include only the latest graph
and review differences. Return only complete JSON conforming to the existing
candidate contract above, not JSON Patch, old graph fragments, or commentary.
Write explanatory diagnostics in Chinese; keep source quotations and code in
their original language without alteration."""


def _locations(graph: dict[str, Any], pointers: Any) -> list[dict[str, Any]]:
    if not isinstance(pointers, list) or not pointers:
        raise ValueError("feedback requires program-resolved graph locations")
    if len(pointers) != len(set(pointers)):
        raise ValueError("feedback contains duplicate graph locations")
    return [{"graph_pointer": pointer, "value": deepcopy(resolve_pointer(graph, pointer))}
            for pointer in pointers]


def build_feedback_prompt(
    package: SkillPackage, previous_cfg: ControlFlowGraph | dict[str, Any], audit: dict[str, Any],
) -> str:
    """Use the actual previous graph and only already validated finding fields."""
    cfg = previous_cfg if isinstance(previous_cfg, ControlFlowGraph) else ControlFlowGraph.model_validate_json(
        json.dumps(previous_cfg, ensure_ascii=False, allow_nan=False))
    graph = normalize_cfg(cfg)
    if audit.get("graph_sha256") != canonical_graph_sha256(graph):
        raise ValueError("feedback audit does not belong to the actual previous CFG")
    differences = []
    for finding in audit["findings"]:
        if finding["kind"] != "semantic" or finding["status"] == "represented":
            continue
        item = {key: deepcopy(finding[key]) for key in (
            "id", "status", "source_requirement", "actual_representation", "reason",
            "source_refs", "controlled_refs", "basis",
        )}
        item["current_facts"] = (
            _locations(graph, finding["graph_refs"]) if finding["graph_refs"] else []
        )
        item["suggestions"] = [{
            "target_ids": deepcopy(suggestion["target_ids"]),
            "change": suggestion["change"], "reason": suggestion["reason"],
            "suggestion_targets": _locations(graph, suggestion["graph_refs"]),
        } for suggestion in finding["suggestions"]]
        if finding["status"] in ACTIONABLE_STATUSES:
            if not item["suggestions"]:
                raise ValueError("an explicit difference requires a located suggestion")
            differences.append(item)
        else:
            raise ValueError("unsupported semantic finding status")
    if not differences:
        raise ValueError("cannot request a semantic revision without explicit differences")
    payload = {"previous_cfg": graph, "explicit_differences": differences,
               **contract_binding()}
    return build_whole_skill_prompt(package) + "\n\n" + CONTRACT_TEXT + "\n\n" + FEEDBACK_INSTRUCTIONS + "\n\n" + json.dumps(
        payload, ensure_ascii=False, indent=2, allow_nan=False)
