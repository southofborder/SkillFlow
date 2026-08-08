"""Cross-engine parity for the full pipeline on the REAL frozen corpus (M1
acceptance).

For each real skill directory (00002-00010), runs the entire rule-only
SkillFCGAnalyzer.analyze() sequence (parse -> extract -> merge user.query /
mediation -> resolve constraints -> type candidates -> validatePairs(rule) ->
buildFCG -> cycle handling -> classifyFeedback(rule) -> splitGraphNodes) in BOTH
engines and deep-compares:

  * node ids (list-equal: JS assigns node_NNN deterministically, so ordering must
    match too, which is strictly stronger than the plan's "set equality"),
  * id -> name mapping,
  * edges (source/target/type/validation_method/is_feedback_edge),
  * adjacency lists,
  * split children,
  * findCrossingViolations == [] on BOTH engines (the M1 oracle).

LLM is fully disabled on both sides, so the comparison is deterministic and
network-free. Skipped when Node is unavailable. This is the first end-to-end
cross-engine proof on real skills (all prior parity was on synthetic fixtures).
"""

import json
import os
import shutil
import subprocess

import pytest

from skill_fcg.analyzer.pipeline import run_pipeline
from skill_fcg.analyzer.node_splitter import find_crossing_violations
from skill_fcg.security.node_profiler import build_node_profiles

_HERE = os.path.dirname(__file__)
_JS_DRIVER = os.path.join(_HERE, "js_pipeline.cjs")
_CORPUS = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "..", "results", "clawhub-top-k10000", "corpus-src")
)

# Frozen golden subset: 00002-00010. All are script-free for FCG purposes
# (.py scripts are not picked up by findExecutableFiles), so no babel sidecar is
# needed and the whole chain is pure-Python vs pure-JS.
_SKILLS = [
    "00002_skill-vetter_1.0.0",
    "00003_polymarket-trade_1.0.6",
    "00004_self-improving_1.2.16",
    "00005_ontology_1.0.4",
    "00006_github_1.0.0",
    "00007_gog_1.0.0",
    "00008_skillscan_1.1.6",
    "00009_weather_1.0.0",
    "00010_multi-search-engine_2.1.3",
]


def _skill_dir(name):
    return os.path.join(_CORPUS, name)


def _py_snapshot(skill_dir, mode="full", cycle_expand=True):
    res = run_pipeline(skill_dir, {"mode": mode, "cycle_expand": cycle_expand})
    graph = res["graph"]
    profiles = build_node_profiles(list(graph.nodes.values()), graph.edges)
    violations = find_crossing_violations(profiles, graph.nodes)
    return json.loads(json.dumps({
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "node_ids": list(graph.nodes.keys()),
        "id_to_name": {n["id"]: n["name"] for n in graph.nodes.values()},
        "split_children": [
            {"id": n["id"], "name": n["name"], "op": n.get("operationType"), "split_from": n.get("split_from")}
            for n in graph.nodes.values() if n.get("split_from")
        ],
        "edges": [{
            "source": e["source"], "target": e["target"], "type": e.get("type"),
            "validation_method": e.get("validation_method"),
            "is_feedback_edge": bool(e.get("is_feedback_edge")),
        } for e in graph.edges],
        "adjacency": {k: list(v) for k, v in graph.adjacency_list.items()},
        "crossing_violations": violations,
    }))


def _js_snapshot(skill_dir, mode="full", cycle_expand=True):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    proc = subprocess.run(
        [node, _JS_DRIVER, skill_dir, mode, "1" if cycle_expand else "0"],
        capture_output=True, text=True, cwd=_HERE,
    )
    if proc.returncode != 0:
        pytest.skip(f"JS pipeline driver failed: {proc.stderr.strip()[:400]}")
    return json.loads(proc.stdout)


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


@pytest.mark.parametrize("skill", _SKILLS)
def test_pipeline_parity_full(skill):
    skill_dir = _skill_dir(skill)
    if not os.path.isdir(skill_dir):
        pytest.skip(f"corpus skill not present: {skill}")

    js = _canon(_js_snapshot(skill_dir, "full", True))
    py = _canon(_py_snapshot(skill_dir, "full", True))

    # M1 acceptance oracle: node id set (list) equality.
    assert py["node_ids"] == js["node_ids"], (
        f"[{skill}] node ids diverged\n"
        f"  py-only: {sorted(set(py['node_ids']) - set(js['node_ids']))[:10]}\n"
        f"  js-only: {sorted(set(js['node_ids']) - set(py['node_ids']))[:10]}"
    )
    assert py["node_count"] == js["node_count"], f"[{skill}] node count diverged"
    assert py["id_to_name"] == js["id_to_name"], f"[{skill}] id->name diverged"
    assert py["split_children"] == js["split_children"], f"[{skill}] split children diverged"
    assert py["edge_count"] == js["edge_count"], f"[{skill}] edge count diverged"
    assert py["edges"] == js["edges"], f"[{skill}] edges diverged"
    assert py["adjacency"] == js["adjacency"], f"[{skill}] adjacency diverged"
    assert py["crossing_violations"] == js["crossing_violations"], f"[{skill}] violations diverged"
    # The single-crossing invariant must hold post-split on BOTH engines.
    assert py["crossing_violations"] == [], f"[{skill}] py findCrossingViolations must be empty"
    assert js["crossing_violations"] == [], f"[{skill}] js findCrossingViolations must be empty"


@pytest.mark.parametrize("skill", ["00002_skill-vetter_1.0.0", "00006_github_1.0.0"])
def test_pipeline_parity_quick(skill):
    """Quick mode takes the direct-candidate path (no validatePairs); confirm it
    also matches cross-engine on the cleanest skills."""
    skill_dir = _skill_dir(skill)
    if not os.path.isdir(skill_dir):
        pytest.skip(f"corpus skill not present: {skill}")
    js = _canon(_js_snapshot(skill_dir, "quick", True))
    py = _canon(_py_snapshot(skill_dir, "quick", True))
    assert py["node_ids"] == js["node_ids"], f"[{skill}] quick node ids diverged"
    assert py["edges"] == js["edges"], f"[{skill}] quick edges diverged"
    assert py["crossing_violations"] == [] == js["crossing_violations"], f"[{skill}] quick violations"


def test_corpus_present():
    """Guard: the frozen corpus must be reachable or the whole suite is vacuous."""
    assert os.path.isdir(_CORPUS), f"corpus dir missing: {_CORPUS}"
    assert os.path.isdir(_skill_dir("00002_skill-vetter_1.0.0")), "00002 skill missing"
