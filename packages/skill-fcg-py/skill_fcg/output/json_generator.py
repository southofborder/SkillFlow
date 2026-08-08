"""v6 FCG output assembler (port of output/json-generator.js envelope).

build_fcg_json wraps the run_pipeline result into the top-level FCG JSON that DOE
consumes: meta / nodes / edges / documentation_context / security_profile (v6).

DOE reads only meta(.skill_name/.skill_version/.input_source), nodes,
documentation_context, and security_profile for its verdicts (confirmed by
grepping fcg.* reads). The debug `paths` / `risks` / `source_sink` blocks that
json-generator.js also emits feed only debug output — no verdict depends on them
and run_pipeline does not compute them — so they are omitted here. edges are kept
(faithful FCG shape; flood already ran on node-id-resolved edges upstream).
"""

import datetime

from ..security.transfer_analysis import build_transfer_security_profile


# Port of normalizeLocation (json-generator.js:539-545)
def _normalize_location(location=None):
    location = location or {}
    file = location.get("file")
    line = location.get("line")
    section = location.get("section")
    if not isinstance(line, int) or isinstance(line, bool):
        try:
            line = int(line)
        except (TypeError, ValueError):
            line = 0
    return {
        "file": file if isinstance(file, str) else "",
        "line": line,
        "section": section if isinstance(section, str) else "",
    }


_OPTIONAL_NODE_FIELDS = [
    "semanticKind", "action", "operationType", "extraction_method", "ownerDoc",
    "docRef", "docAction", "docActions", "stepIndex", "stepRange", "stepRefs",
    "instructionText", "member_step_count", "member_steps", "formal_semantics",
    "source_context", "semantic_gate", "ownerScript", "functionName", "callee",
    "excludeFromFlow", "excludeFromTypeAnalysis", "canonical_name", "callsite_id",
    "callsite_order", "callsite_role",
]


# Port of buildNodeJson (json-generator.js:547-598)
def build_node_json(node=None):
    node = node or {}
    out = {
        "id": node.get("id"),
        "name": node.get("name"),
        "type": node.get("type") or "tool_call",
        "category": node.get("category") or "Intermediate",
        "is_critical": bool(node.get("isCritical")),
        "description": node.get("description") or "",
        "location": _normalize_location(node.get("location")),
        "signature": {
            "input": node.get("input") or {},
            "output": node.get("output") or {},
        },
    }
    for field in _OPTIONAL_NODE_FIELDS:
        if node.get(field) is not None:
            out[field] = node.get(field)
    return out


# Port of the edges .map in buildBaseFCGJson (json-generator.js:327-348).
def build_edge_json(edge=None, index=0):
    edge = edge or {}
    out = {
        "id": f"edge_{str(index + 1).zfill(3)}",
        "source": edge.get("source"),
        "target": edge.get("target"),
        "type": edge.get("type") or "data_dependency",
        "confidence": edge.get("confidence") or 0.5,
        "validation_method": edge.get("validation_method") or "type_check",
        "data_flow": edge.get("data_flow") or {},
        "semantic_reason": edge.get("semantic_reason") or "",
    }
    if edge.get("source_context") is not None:
        out["source_context"] = edge.get("source_context")
    if edge.get("edge_evidence") is not None:
        out["edge_evidence"] = edge.get("edge_evidence")
    if edge.get("is_feedback_edge"):
        out["is_feedback_edge"] = True
        out["feedback_removed_reason"] = edge.get("feedback_removed_reason") or "cycle_break"
        if isinstance(edge.get("feedback_cycle_path"), list):
            out["feedback_cycle_path"] = edge.get("feedback_cycle_path")
        if edge.get("feedback_plausibility"):
            out["feedback_plausibility"] = edge.get("feedback_plausibility")
            out["feedback_plausibility_source"] = edge.get("feedback_plausibility_source") or "rule"
            if edge.get("feedback_plausibility_reason"):
                out["feedback_plausibility_reason"] = edge.get("feedback_plausibility_reason")
    return out


def build_fcg_json(pipeline_result, input_source="unknown", limits=None):
    """Assemble the full v6 FCG JSON from a run_pipeline() result.

    ``pipeline_result`` is the dict returned by analyzer.pipeline.run_pipeline
    (graph + skill_data + documentation_context + mode). cycle_expand is inferred
    from whether any edge carries a plausible feedback marker being kept — but the
    caller already ran the pipeline with a cycle_expand flag; we re-read it off the
    graph's edges the same way transfer_edges does (feedback edges present ==>
    cycle_expand was on). To stay explicit we accept the flag via the result.
    """
    graph = pipeline_result["graph"]
    skill_data = pipeline_result.get("skill_data") or {}
    documentation_context = pipeline_result.get("documentation_context") or {}
    mode = pipeline_result.get("mode") or "full"
    cycle_expand = bool(pipeline_result.get("cycle_expand", True))

    nodes = [build_node_json(n) for n in graph.nodes.values()]
    edges = [build_edge_json(e, i) for i, e in enumerate(graph.edges)]

    security_profile = build_transfer_security_profile(
        nodes=nodes, edges=edges, cycle_expand=cycle_expand, limits=limits)

    statistics = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "feedback_edge_count": sum(1 for e in edges if e.get("is_feedback_edge")),
    }
    if pipeline_result.get("semantic_gate_usage"):
        statistics["semantic_gate_llm_usage"] = pipeline_result["semantic_gate_usage"]

    return {
        "meta": {
            "skill_name": skill_data.get("name"),
            "skill_version": skill_data.get("version") or "1.0.0",
            "analysis_timestamp": datetime.datetime.now(datetime.timezone.utc)
                .isoformat().replace("+00:00", "Z"),
            "analyzer_version": "6.0.0",
            "input_source": input_source,
            "analysis_mode": mode,
        },
        "nodes": nodes,
        "edges": edges,
        "statistics": statistics,
        "documentation_context": documentation_context or {},
        "security_profile": security_profile,
    }
