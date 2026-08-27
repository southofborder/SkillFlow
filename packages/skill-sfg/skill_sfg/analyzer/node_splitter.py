"""Port of src/analyzer/node-splitter.js.

Enforces the single-crossing invariant deterministically AFTER edges resolve to
node ids: a node crossing >1 data boundary is split into a chain of single-
crossing children that INHERIT the parent's edges (incoming->first, outgoing->
last, chained between), so no dependency re-pairing is needed. Children carry
only their segment's steps as member_steps + narrowed instructionText, so each
re-profiles to a single crossing. findCrossingViolations is the M1 acceptance
oracle (must be empty after split). Uses buildNodeProfile from node_profiler as
the single source of truth for ordered action steps.
"""

from ..security.node_profiler import build_node_profile
from .cycle_remover import is_feedback_edge


SINK_LIKE_ROLES = {
    "external_egress",
    "model_inference",
    "local_persistence",
    "command_execution",
    "destructive_operation",
    "tool_invocation",
}


# Port of stepIsCrossing (node-splitter.js:36-38)
def step_is_crossing(step=None):
    step = step or {}
    return any(role in SINK_LIKE_ROLES for role in (step.get("node_roles") or []))


# Port of isAtomicBuiltin (node-splitter.js:47-49)
def is_atomic_builtin(node=None):
    node = node or {}
    return node.get("type") == "builtin_call"


# Port of orderedActionSteps (node-splitter.js:53-56)
def ordered_action_steps(node=None):
    node = node or {}
    profile = build_node_profile(node, {})
    steps = profile.get("action_steps")
    return steps if isinstance(steps, list) else []


# Port of segmentSteps (node-splitter.js:61-76)
def segment_steps(steps=None):
    steps = steps or []
    segments = []
    current = []
    for step in steps:
        current.append(step)
        if step_is_crossing(step):
            segments.append(current)
            current = []
    if len(current):
        if len(segments):
            segments[-1].extend(current)
        else:
            segments.append(current)
    return segments


# Port of stepToMemberStep (node-splitter.js:80-94)
def step_to_member_step(step=None, index=0):
    step = step or {}
    ev = step.get("evidence")
    evidence_text = (ev[0].get("text") if isinstance(ev, list) and ev and isinstance(ev[0], dict) else None) or step.get("operation_type") or ""
    order = step.get("order")
    line = int(order) if _is_finite_num(order) else index + 1
    return {
        "instruction": evidence_text,
        "text": evidence_text,
        "operation_type": step.get("operation_type") or "transform",
        "docAction": step.get("operation_type") or "",
        "line": line,
        "formal_semantics": {
            "operation_type": step.get("operation_type") or "transform",
            "targets": step.get("targets") if isinstance(step.get("targets"), list) else [],
            "confidence": step.get("confidence"),
        },
    }


# Port of buildChildNode (node-splitter.js:99-130)
def build_child_node(parent=None, segment=None, segment_index=0):
    parent = parent or {}
    segment = segment or []
    crossing = next((s for s in segment if step_is_crossing(s)), None) or (segment[-1] if segment else {})
    order = int(crossing.get("order")) if _is_finite_num(crossing.get("order")) else segment_index + 1
    op = crossing.get("operation_type") or "transform"
    child_id = f"{parent.get('id')}::s{str(order).rjust(3, '0')}::{op}"
    member_steps = [step_to_member_step(step, i) for i, step in enumerate(segment)]
    instruction_text = " ".join(
        s for s in (
            (step.get("evidence")[0].get("text") if isinstance(step.get("evidence"), list) and step.get("evidence") and isinstance(step["evidence"][0], dict) else None)
            or step.get("operation_type") or ""
            for step in segment
        ) if s
    )

    return {
        **parent,
        "id": child_id,
        "name": f"{parent.get('name') or parent.get('id')}#s{order}",
        "canonical_name": parent.get("canonical_name") or parent.get("name") or parent.get("id"),
        "member_steps": member_steps,
        "member_step_count": len(member_steps),
        "instructionText": instruction_text or parent.get("instructionText") or "",
        "docActions": [op],
        "docAction": op,
        "operationType": op,
        "formal_semantics": {
            **(parent.get("formal_semantics") or {}),
            "operation_type": op,
        },
        "split_from": parent.get("id"),
        "split_segment_index": segment_index,
    }


# Port of internalChainEdge (node-splitter.js:135-150)
def internal_chain_edge(source_id, target_id, seq):
    return {
        "id": f"split_edge_{source_id}__{target_id}",
        "source": source_id,
        "target": target_id,
        "type": "data_dependency",
        "confidence": 1.0,
        "validation_method": "node_split_sequential",
        "data_flow": {"from_param": "segment_output", "to_param": "segment_input", "data_type": "object"},
        "semantic_reason": f"Intra-node data flow between split segments {seq} of {source_id.split('::')[0]}",
    }


# Port of splitGraphNodes (node-splitter.js:162-240)
def split_graph_nodes(graph):
    original_nodes = list(graph.nodes.values())
    children_by_parent = {}
    new_nodes = {}
    internal_edges = []

    for node in original_nodes:
        if is_atomic_builtin(node):
            new_nodes[node["id"]] = node
            continue

        steps = ordered_action_steps(node)
        crossing_count = len([s for s in steps if step_is_crossing(s)])

        if crossing_count <= 1:
            new_nodes[node["id"]] = node
            continue

        segments = segment_steps(steps)
        if len(segments) <= 1:
            new_nodes[node["id"]] = node
            continue

        child_ids = []
        prev_child_id = None
        for segment_index, segment in enumerate(segments):
            child = build_child_node(node, segment, segment_index)
            new_nodes[child["id"]] = child
            child_ids.append(child["id"])
            if prev_child_id:
                internal_edges.append(internal_chain_edge(prev_child_id, child["id"], segment_index))
            prev_child_id = child["id"]
        children_by_parent[node["id"]] = child_ids

    def first_child(node_id):
        return (children_by_parent.get(node_id) or [node_id])[0]

    def last_child(node_id):
        kids = children_by_parent.get(node_id)
        return kids[-1] if kids else node_id

    rewired_edges = []
    for edge in graph.edges:
        src_split = edge["source"] in children_by_parent
        dst_split = edge["target"] in children_by_parent
        if edge["source"] == edge["target"] and src_split:
            rewired_edges.append({**edge, "source": last_child(edge["source"]), "target": first_child(edge["target"])})
            continue
        rewired_edges.append({
            **edge,
            "source": last_child(edge["source"]) if src_split else edge["source"],
            "target": first_child(edge["target"]) if dst_split else edge["target"],
        })

    all_edges = [*rewired_edges, *internal_edges]

    adjacency_list = {}
    for node_id in new_nodes.keys():
        adjacency_list[node_id] = []
    for edge in all_edges:
        if is_feedback_edge(edge):
            continue
        if edge["source"] not in adjacency_list:
            adjacency_list[edge["source"]] = []
        adjacency_list[edge["source"]].append(edge["target"])

    graph.nodes = new_nodes
    graph.edges = all_edges
    graph.adjacency_list = adjacency_list
    return graph


# Port of findCrossingViolations (node-splitter.js:247-267)
def find_crossing_violations(node_profiles=None, nodes_by_id=None):
    node_profiles = node_profiles or []
    nodes_by_id = nodes_by_id or {}
    violations = []
    for profile in node_profiles:
        node = nodes_by_id.get(profile.get("node_id"))
        if node and is_atomic_builtin(node):
            continue
        steps = profile.get("action_steps") if isinstance(profile.get("action_steps"), list) else []
        crossings = [s for s in steps if step_is_crossing(s)]
        if len(crossings) > 1:
            violations.append({
                "node_id": profile.get("node_id"),
                "node_name": profile.get("node_name"),
                "crossing_count": len(crossings),
                "crossing_ops": [step.get("operation_type") for step in crossings],
            })
    return violations


def _is_finite_num(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return False
    return n == n and n not in (float("inf"), float("-inf"))
