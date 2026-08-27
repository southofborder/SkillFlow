"""Cross-engine parity for node splitting + feedback classification + the M1
acceptance oracle findCrossingViolations (M1e-3).

Runs the full analyzer chain (mediation -> candidates -> maps -> buildFCG ->
dedup -> removeCycles -> classifyFeedbackEdges rule-only -> splitGraphNodes ->
findCrossingViolations) in Python and deep-compares node ids, split children,
edges, adjacency, feedback plausibility, and crossing violations against the
REAL JS pipeline. Fixtures include multi-crossing nodes so the splitter actually
fires and the post-split violation set can be asserted empty (the M1 oracle).

Skipped when Node is unavailable.
"""

import json
import os

import pytest

from skill_sfg.analyzer.type_analyzer import analyze_type_compatibility
from skill_sfg.analyzer.fcg_builder import build_fcg, remove_duplicate_edges
from skill_sfg.analyzer.cycle_remover import remove_cycles
from skill_sfg.analyzer.callsite_expander import (
    build_call_site_mediation,
    build_endpoint_maps,
    expand_and_map_edges,
)
from skill_sfg.analyzer.feedback_edge_classifier import classify_feedback_edges
from skill_sfg.analyzer.node_splitter import split_graph_nodes, find_crossing_violations
from skill_sfg.security.node_profiler import build_node_profiles

_HERE = os.path.dirname(__file__)
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "split_feedback.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)


def _tool(name, **kw):
    base = {"name": name, "type": "custom_func", "input": {}, "output": {}}
    base.update(kw)
    return base


_FIXTURES = {
    # Multi-crossing tool nodes that MUST split (each has write+egress prose),
    # plus a cycle to exercise feedback classification, plus a doc-slug node that
    # must NOT split (single read crossing despite JSON).
    "split_and_cycle": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query", "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference", "input": {}, "output": {}},
            _tool("saveThenUpload", type="tool_call", canonical_name="saveThenUpload", action="post",
                  instructionText="save the report to a local file and then upload it to the external api",
                  location={"file": "scripts/a.sh", "line": 3},
                  formal_semantics={"operation_type": "write",
                                    "evidence": {"text": "save the report to a local file and then upload it to the external api"}}),
            _tool("readModelWrite", type="tool_call", canonical_name="readModelWrite", action="run",
                  instructionText="read the records, send them to the model, then write the summary to disk",
                  location={"file": "scripts/a.sh", "line": 5},
                  formal_semantics={"operation_type": "transform",
                                    "evidence": {"text": "read the records, send them to the model, then write the summary to disk"}}),
            _tool("doc.step.skill.l9.s1.read.memory", semanticKind="doc_step", action="read",
                  operationType="read", docActions=["read"], ownerDoc="SKILL.md",
                  instructionText="read the memory file",
                  input={"file_path": {"type": "string"}}, output={"content": {"type": "string"}},
                  location={"file": "SKILL.md", "line": 9},
                  formal_semantics={"operation_type": "read", "evidence": {"text": "read the memory file"},
                                    "targets": [{"type": "file", "value": "memory.md"}]}),
        ],
        "edges": [
            {"source": "saveThenUpload", "target": "readModelWrite", "type": "data_dependency",
             "confidence": 0.3, "validation_method": "dependency_rule",
             "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
             "semantic_reason": "a->b"},
            {"source": "readModelWrite", "target": "saveThenUpload", "type": "data_dependency",
             "confidence": 0.2, "validation_method": "dependency_rule",
             "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
             "semantic_reason": "b->a back-edge"},
        ],
    },
    "callsites_no_split": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query", "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference", "input": {}, "output": {}},
            _tool("gmail.message.get#call_001", type="tool_call", canonical_name="gmail.message.get",
                  callsite_id="call_001", callsite_order=1, action="get",
                  location={"file": "SKILL.md", "line": 5}, output={"data": {"type": "object"}}),
            _tool("webhook.post#call_002", type="tool_call", canonical_name="webhook.post",
                  callsite_id="call_002", callsite_order=2, action="post",
                  location={"file": "SKILL.md", "line": 6}, input={"payload": {"type": "object"}}),
        ],
        "edges": [],
    },
}


def _py_snapshot(tools, supplied_edges):
    mediation = build_call_site_mediation(tools)
    all_tools = tools + mediation["nodes"]
    candidates = analyze_type_compatibility(all_tools, {})
    maps = build_endpoint_maps(all_tools)
    candidate_edges = []
    for index, pair in enumerate(candidates):
        cp = (pair["compatibleParams"][0] if pair["compatibleParams"] else {})
        candidate_edges.append({
            "id": f"edge_{str(index + 1).rjust(3, '0')}",
            "source": pair["source"]["name"], "target": pair["target"]["name"], "type": "data_dependency",
            "confidence": pair["confidence"], "validation_method": "dependency_rule",
            "data_flow": {"from_param": cp.get("fromParam") or "unknown", "to_param": cp.get("toParam") or "unknown", "data_type": cp.get("fromType") or "string"},
            "semantic_reason": pair.get("candidate_reason") or "Sparse dependency rule",
        })
    mapped = [
        *expand_and_map_edges(candidate_edges, maps),
        *expand_and_map_edges(mediation["edges"], maps),
        *expand_and_map_edges(supplied_edges, maps),
    ]

    graph = build_fcg(all_tools, mapped)
    graph = remove_duplicate_edges(graph)
    graph = remove_cycles(graph)
    classify_feedback_edges(graph, {"feedbackLlmReview": False, "disableLlm": True})

    pre_split_count = len(graph.nodes)
    graph = split_graph_nodes(graph)

    profiles = build_node_profiles(list(graph.nodes.values()), graph.edges)
    violations = find_crossing_violations(profiles, graph.nodes)

    return json.loads(json.dumps({
        "pre_split_count": pre_split_count,
        "post_split_count": len(graph.nodes),
        "node_ids": list(graph.nodes.keys()),
        "split_children": [
            {"id": n["id"], "name": n["name"], "op": n.get("operationType"), "split_from": n.get("split_from")}
            for n in graph.nodes.values() if n.get("split_from")
        ],
        "edges": [{
            "source": e["source"], "target": e["target"], "type": e.get("type"),
            "validation_method": e.get("validation_method"),
            "is_feedback_edge": bool(e.get("is_feedback_edge")),
            "feedback_plausibility": e.get("feedback_plausibility"),
        } for e in graph.edges],
        "adjacency": {k: list(v) for k, v in graph.adjacency_list.items()},
        "crossing_violations": violations,
    }))


def _canon(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [_canon(v) for v in value]
    if isinstance(value, dict):
        return {k: _canon(v) for k, v in value.items()}
    return value


@pytest.mark.parametrize("name", sorted(_FIXTURES.keys()))
def test_split_and_feedback_parity(name):
    spec = _FIXTURES[name]
    js = _canon(_GOLDEN[name])
    py = _canon(_py_snapshot(spec["tools"], spec["edges"]))

    assert py["pre_split_count"] == js["pre_split_count"], f"[{name}] pre-split count diverged"
    assert py["post_split_count"] == js["post_split_count"], f"[{name}] post-split count diverged"
    assert py["node_ids"] == js["node_ids"], f"[{name}] node ids diverged"
    assert py["split_children"] == js["split_children"], f"[{name}] split children diverged"
    assert py["edges"] == js["edges"], f"[{name}] edges diverged"
    assert py["adjacency"] == js["adjacency"], f"[{name}] adjacency diverged"
    assert py["crossing_violations"] == js["crossing_violations"], f"[{name}] violations diverged"
    # M1 acceptance oracle: after splitting, no node crosses >1 boundary.
    assert py["crossing_violations"] == [], f"[{name}] findCrossingViolations must be empty after split"


def test_multi_crossing_nodes_actually_split():
    """Guard against a vacuous green: the split_and_cycle fixture MUST produce
    split children (the multi-crossing nodes get broken)."""
    py = _py_snapshot(_FIXTURES["split_and_cycle"]["tools"], _FIXTURES["split_and_cycle"]["edges"])
    assert py["post_split_count"] > py["pre_split_count"], "expected splitting to add nodes"
    assert len(py["split_children"]) >= 2, f"expected split children, got {py['split_children']}"
