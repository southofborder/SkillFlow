"""Cross-engine parity for the 4 clean analyzer modules (M1e-1).

Drives type_analyzer -> callsite mediation -> endpoint maps -> expand ->
build_fcg -> remove_duplicate_edges -> remove_cycles in the exact index.js
order, over synthetic {tools, edges} fixtures, and deep-compares the Python
snapshot against the REAL JS modules. Isolates M1e-1 from the not-yet-ported
pipeline assembly glue by feeding both engines the same tool/edge input.

Skipped when Node is unavailable. The node-splitter + profiler-dependent stages
are covered separately once node_profiler lands (M1e-2/3).
"""

import json
import os
import shutil
import subprocess

import pytest

from skill_fcg.analyzer.type_analyzer import analyze_type_compatibility
from skill_fcg.analyzer.fcg_builder import build_fcg, remove_duplicate_edges
from skill_fcg.analyzer.cycle_remover import remove_cycles
from skill_fcg.analyzer.callsite_expander import (
    build_call_site_mediation,
    build_endpoint_maps,
    expand_and_map_edges,
)

_HERE = os.path.dirname(__file__)
_JS_DRIVER = os.path.join(_HERE, "js_analyzer_core.cjs")


def _tool(name, **kw):
    base = {"name": name, "type": "custom_func", "input": {}, "output": {}}
    base.update(kw)
    return base


# Fixtures exercise: doc steps with same-file ordering (scoped_sequence),
# boundary-like egress/persistence targets (boundary_impact / high_value),
# repeated tool call-sites (mediation nodes + callsite order), cross-stage
# route candidates (user.query / llm / doc / tool stages), and a supplied
# structural edge set that must map name->id and survive dedup/cycle removal.
_FIXTURES = {
    "doc_steps_boundary": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query",
             "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference",
             "input": {}, "output": {}},
            _tool("doc.step.skill.l7.s1.read.memory", semanticKind="doc_step", action="read",
                  operationType="read", ownerDoc="SKILL.md",
                  location={"file": "SKILL.md", "line": 7, "section": "Steps"},
                  formal_semantics={"operation_type": "read", "targets": [{"type": "file", "value": "memory.md"}]}),
            _tool("doc.step.skill.l8.s2.external_egress.api", semanticKind="doc_step", action="run",
                  operationType="external_egress", ownerDoc="SKILL.md",
                  location={"file": "SKILL.md", "line": 8, "section": "Steps"},
                  formal_semantics={"operation_type": "external_egress",
                                    "effects": ["network_egress"],
                                    "targets": [{"type": "url", "value": "https://api.example.com"}]}),
            _tool("doc.step.skill.l9.s3.write.log", semanticKind="doc_step", action="write",
                  operationType="write", ownerDoc="SKILL.md",
                  location={"file": "SKILL.md", "line": 9, "section": "Steps"},
                  formal_semantics={"operation_type": "write", "targets": [{"type": "file", "value": "log.md"}]}),
        ],
        "edges": [],
    },
    "repeated_callsites": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query", "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference", "input": {}, "output": {}},
            _tool("gmail.message.get#call_001", type="tool_call", canonical_name="gmail.message.get",
                  callsite_id="call_001", callsite_order=1, action="get",
                  location={"file": "SKILL.md", "line": 5},
                  output={"data": {"type": "object"}}),
            _tool("webhook.post#call_002", type="tool_call", canonical_name="webhook.post",
                  callsite_id="call_002", callsite_order=2, action="post",
                  location={"file": "SKILL.md", "line": 6},
                  input={"payload": {"type": "object"}}),
            _tool("gmail.message.get#call_003", type="tool_call", canonical_name="gmail.message.get",
                  callsite_id="call_003", callsite_order=3, action="get",
                  location={"file": "SKILL.md", "line": 7},
                  output={"data": {"type": "object"}}),
        ],
        "edges": [
            {"source": "user.query", "target": "llm.inference", "type": "data_dependency",
             "confidence": 1.0, "validation_method": "dependency_structural",
             "data_flow": {"from_param": "query_text", "to_param": "user_query", "data_type": "string"},
             "semantic_reason": "activation"},
        ],
    },
    "cross_stage_route": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query", "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference", "input": {}, "output": {}},
            _tool("doc.step.skill.l5.s1.invoke_tool.weather", semanticKind="doc_step", action="run",
                  operationType="invoke_tool", ownerDoc="SKILL.md", instructionText="call the weather api",
                  location={"file": "SKILL.md", "line": 5},
                  formal_semantics={"operation_type": "invoke_tool",
                                    "targets": [{"type": "tool", "value": "weather.api"}]}),
            _tool("weather.api", type="tool_call", canonical_name="weather.api", action="get",
                  instructionText="weather api endpoint",
                  location={"file": "scripts/run.sh", "line": 3},
                  output={"data": {"type": "object"}}),
        ],
        "edges": [
            {"source": "doc.step.skill.l5.s1.invoke_tool.weather", "target": "weather.api",
             "type": "control_flow", "confidence": 0.6, "validation_method": "doc_flow",
             "data_flow": {"from_param": "instruction", "to_param": "context", "data_type": "string"},
             "semantic_reason": "route"},
        ],
    },
    "cycle_break": {
        "tools": [
            {"name": "user.query", "type": "builtin_call", "canonical_name": "user.query", "input": {}, "output": {}},
            {"name": "llm.inference", "type": "builtin_call", "canonical_name": "llm.inference", "input": {}, "output": {}},
            _tool("a.node", action="write", output={"success": {"type": "boolean"}}),
            _tool("b.node", action="read", output={"data": {"type": "object"}}),
        ],
        "edges": [
            {"source": "a.node", "target": "b.node", "type": "data_dependency", "confidence": 0.3,
             "validation_method": "dependency_rule",
             "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
             "semantic_reason": "a->b"},
            {"source": "b.node", "target": "a.node", "type": "data_dependency", "confidence": 0.2,
             "validation_method": "dependency_rule",
             "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
             "semantic_reason": "b->a back-edge"},
        ],
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
            "source": pair["source"]["name"],
            "target": pair["target"]["name"],
            "type": "data_dependency",
            "confidence": pair["confidence"],
            "validation_method": "dependency_rule",
            "data_flow": {
                "from_param": cp.get("fromParam") or "unknown",
                "to_param": cp.get("toParam") or "unknown",
                "data_type": cp.get("fromType") or "string",
            },
            "semantic_reason": pair.get("candidate_reason") or "Sparse dependency rule",
        })
    mapped_candidate_edges = expand_and_map_edges(candidate_edges, maps)
    mapped_mediation_edges = expand_and_map_edges(mediation["edges"], maps)
    mapped_supplied_edges = expand_and_map_edges(supplied_edges, maps)

    graph = build_fcg(all_tools, [*mapped_candidate_edges, *mapped_mediation_edges, *mapped_supplied_edges])
    graph = remove_duplicate_edges(graph)
    graph = remove_cycles(graph)

    node_ids = list(graph.nodes.keys())
    node_names_by_id = {nid: node["name"] for nid, node in graph.nodes.items()}
    edges = []
    for e in graph.edges:
        edge = {"source": e["source"], "target": e["target"], "type": e.get("type"),
                "confidence": e.get("confidence"), "validation_method": e.get("validation_method"),
                "is_feedback_edge": bool(e.get("is_feedback_edge"))}
        # Mirror JS JSON.stringify: undefined `id` (edges without one) is dropped.
        if e.get("id") is not None:
            edge = {"id": e["id"], **edge}
        edges.append(edge)

    return json.loads(json.dumps({
        "node_ids": node_ids,
        "node_names_by_id": node_names_by_id,
        "mediation_node_names": [n["name"] for n in mediation["nodes"]],
        "candidate_count": len(candidates),
        "candidate_pairs": [f"{c['source']['name']}->{c['target']['name']}:{c['candidate_kind']}" for c in candidates],
        "edges": edges,
        "adjacency": {k: list(v) for k, v in graph.adjacency_list.items()},
    }))


def _js_snapshot(spec):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    spec_path = os.path.join(_HERE, "_analyzer_core_spec.json")
    with open(spec_path, "w", encoding="utf-8") as handle:
        json.dump(spec, handle)
    proc = subprocess.run([node, _JS_DRIVER, spec_path], capture_output=True, text=True, cwd=_HERE)
    if proc.returncode != 0:
        pytest.skip(f"JS analyzer-core driver failed: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


@pytest.mark.parametrize("name", sorted(_FIXTURES.keys()))
def test_analyzer_core_parity(name):
    spec = _FIXTURES[name]
    js = _canon(_js_snapshot(spec))
    py = _canon(_py_snapshot(spec["tools"], spec["edges"]))

    assert py["node_ids"] == js["node_ids"], f"[{name}] node ids diverged"
    assert py["node_names_by_id"] == js["node_names_by_id"], f"[{name}] id->name diverged"
    assert py["mediation_node_names"] == js["mediation_node_names"], f"[{name}] mediation nodes diverged"
    assert py["candidate_count"] == js["candidate_count"], f"[{name}] candidate count diverged"
    assert py["candidate_pairs"] == js["candidate_pairs"], f"[{name}] candidate pairs diverged"
    assert py["edges"] == js["edges"], f"[{name}] edges diverged"
    assert py["adjacency"] == js["adjacency"], f"[{name}] adjacency diverged"


def _canon(value):
    """Normalize JS-number formatting: integral floats (1.0) collapse to int (1),
    matching how V8/JSON.stringify renders whole numbers, so 1.0 == 1 in compare."""
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [_canon(v) for v in value]
    if isinstance(value, dict):
        return {k: _canon(v) for k, v in value.items()}
    return value
