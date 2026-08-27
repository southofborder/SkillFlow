"""Port of src/analyzer/cycle-remover.js.

Two-stage cycle handling (method A: never delete the breaking edge from
graph.edges, only tag it and, for fake cycles, drop its adjacency entry):
  - detect_and_tag_cycles: DFS-detect cycles, select+tag the weakest breakable
    edge of each (is_feedback_edge / feedback_cycle_path). No adjacency mutation.
  - break_only_fake: remove from adjacency only the implausible feedback edges.
  - remove_cycles: back-compat wrapper (tag + break everything).

DFS uses an explicit path list mirroring the JS recursion. Edge selection
(weakest by confidence -> type score -> source -> target) is byte-identical to
the JS reduce; ties broken by localeCompare (code-point here).
"""

import sys as _sys

_sys.setrecursionlimit(1000000)


# Port of detectAndTagCycles (cycle-remover.js:32-104)
def detect_and_tag_cycles(graph):
    visited = set()
    rec_stack = set()
    cycles = []

    def dfs(node_id, path):
        visited.add(node_id)
        rec_stack.add(node_id)
        neighbors = graph.adjacency_list.get(node_id) or []
        for neighbor_id in neighbors:
            if neighbor_id not in visited:
                dfs(neighbor_id, [*path, neighbor_id])
            elif neighbor_id in rec_stack:
                cycle_start = path.index(neighbor_id) if neighbor_id in path else -1
                cycles.append({"start": neighbor_id, "path": path[cycle_start:]})
        rec_stack.discard(node_id)

    for node_id in list(graph.nodes.keys()):
        if node_id not in visited:
            dfs(node_id, [node_id])

    # Select the weakest edge of each cycle and TAG it (byte-identical selection
    # order to the former removeCycles; `cut` makes a selected edge invisible to
    # later cycles yet keeps it in graph.edges). Uses id()-based membership so an
    # edge dict re-selected across cycles matches the JS `!cut.has(e)` reference
    # check.
    cut = set()
    for cycle in cycles:
        cpath = cycle["path"]
        cycle_edges = [
            e for e in graph.edges
            if id(e) not in cut and e["source"] in cpath and e["target"] in cpath
        ]
        if len(cycle_edges) == 0:
            continue
        removable_edges = [e for e in cycle_edges if not is_protected_cycle_edge(e)]
        if len(removable_edges) == 0:
            continue
        weakest_edge = removable_edges[0]
        for edge in removable_edges[1:]:
            if compare_edge_removal_priority(edge, weakest_edge) < 0:
                weakest_edge = edge
        cut.add(id(weakest_edge))
        weakest_edge["is_feedback_edge"] = True
        weakest_edge["feedback_removed_reason"] = "cycle_break"
        weakest_edge["feedback_cycle_path"] = list(cpath)

    return graph


# Port of breakOnlyFake (cycle-remover.js:119-133)
def break_only_fake(graph):
    for edge in graph.edges:
        if not is_feedback_edge(edge):
            continue
        if edge.get("feedback_plausibility") == "plausible":
            continue
        neighbors = graph.adjacency_list.get(edge["source"]) or []
        graph.adjacency_list[edge["source"]] = [t for t in neighbors if t != edge["target"]]
    return graph


# Port of removeCycles (cycle-remover.js:142-153)
def remove_cycles(graph):
    detect_and_tag_cycles(graph)
    for edge in graph.edges:
        if not is_feedback_edge(edge):
            continue
        neighbors = graph.adjacency_list.get(edge["source"]) or []
        graph.adjacency_list[edge["source"]] = [t for t in neighbors if t != edge["target"]]
    return graph


# Port of isFeedbackEdge (cycle-remover.js:161-163)
def is_feedback_edge(edge):
    return bool(edge and edge.get("is_feedback_edge"))


# Port of isProtectedCycleEdge (cycle-remover.js:165-175)
def is_protected_cycle_edge(edge):
    if not edge:
        return False
    if edge.get("type") == "doc_instruction":
        return True
    if edge.get("validation_method") == "doc_flow":
        return True
    if edge.get("validation_method") == "semantic_rule":
        return True
    if edge.get("validation_method") == "callsite_mediation":
        return True
    if edge.get("validation_method") == "doc_flow_constraint":
        return True
    return False


# Port of compareEdgeRemovalPriority (cycle-remover.js:177-191)
def compare_edge_removal_priority(a, b):
    confidence_a = a.get("confidence") if _is_finite(a and a.get("confidence")) else 0.5
    confidence_b = b.get("confidence") if _is_finite(b and b.get("confidence")) else 0.5
    if confidence_a != confidence_b:
        return -1 if confidence_a < confidence_b else 1
    type_score_a = edge_type_removal_score(a.get("type") if a else None)
    type_score_b = edge_type_removal_score(b.get("type") if b else None)
    if type_score_a != type_score_b:
        return type_score_a - type_score_b
    source_a = str((a.get("source") if a else None) or "")
    source_b = str((b.get("source") if b else None) or "")
    if source_a != source_b:
        return _locale_compare(source_a, source_b)
    return _locale_compare(str((a.get("target") if a else None) or ""), str((b.get("target") if b else None) or ""))


# Port of edgeTypeRemovalScore (cycle-remover.js:193-206)
def edge_type_removal_score(type_):
    return {
        "data_dependency": 1,
        "control_flow": 2,
        "semantic": 3,
        "doc_instruction": 4,
    }.get(type_, 5)


def _is_finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value and value not in (float("inf"), float("-inf"))


def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)
