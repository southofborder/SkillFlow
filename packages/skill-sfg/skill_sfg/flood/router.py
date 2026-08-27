"""Port of src/security/flow-instance-router.js — de-path-ized for the flood
state-DAG.

The ONLY behavioral change from the JS is how the two path reads are satisfied:

  * flow-instance-router.js:50  ``path.includes(targetNodeId)``  (acyclic guard)
    → ``target_node_id in ancestor_nodes`` — the caller passes the StateNode's
      monotone ancestor set (which INCLUDES the current node, so an A→…→A
      revisit is caught exactly as ``path.includes`` caught it).
  * flow-instance-router.js:57  ``path.length >= maxDepth``  (depth backstop)
    → ``depth_min >= maxDepth`` — the StateNode's hop depth (root=1, child=
      parent+1), replacing ``node_path.length``.

Everything else (feedback absorb, deny/allow regexes, control_flow data vs
order-only, sink-like target, decision-like, control→source) is ported verbatim.
The classification result dict is byte-identical to JS ``decision(...)``.
"""

from .constants import CONTROL_FLOW_PLACEHOLDER_PARAMS, NEGATIVE_CONDITION_REGEX

import re

# Port of SINK_LIKE_ROLES (flow-instance-router.js:1-8)
SINK_LIKE_ROLES = frozenset([
    "external_egress",
    "model_inference",
    "local_persistence",
    "command_execution",
    "destructive_operation",
    "tool_invocation",
])

_DENY_RE = re.compile(r"deny|forbid|block|reject|stop", re.IGNORECASE)
_ALLOW_RE = re.compile(r"allow|permit|pass|route|branch|when|if\b", re.IGNORECASE)


# Port of classifyRouteState (flow-instance-router.js:10-101).
# De-path-ized: takes ancestor_nodes (set) + depth_min instead of instance.
def classify_route_state(
    ancestor_nodes=None,
    depth_min=0,
    current_profile=None,
    target_profile=None,
    edge=None,
    max_depth=1000,
):
    ancestor_nodes = ancestor_nodes if ancestor_nodes is not None else frozenset()
    current_profile = current_profile or {}
    target_profile = target_profile or {}
    edge = edge or {}

    target_node_id = target_profile.get("node_id") or edge.get("target") or ""
    route_text = build_route_text(current_profile, target_profile, edge)
    # Part 2: an explicit negative/conditional guard on the target downgrades an
    # otherwise-definite route to may_route (never hard-block, never on absence).
    conditional_guard = has_negative_condition_gate(target_profile)

    if not target_node_id:
        return _decision("blocked", "missing_target", 0.05)

    # Plausible feedback edge — unconditionally absorbed into the cycle's label
    # closure, never traversed (flow-instance-router.js:46-48).
    if edge.get("is_feedback_edge") and edge.get("feedback_plausibility") == "plausible":
        return _decision("blocked", "cycle_absorbed_into_closure", 0.1)

    # flow-instance-router.js:50 — was path.includes(targetNodeId).
    if target_node_id in ancestor_nodes:
        return _decision("blocked", "cycle_blocked", 0.1)

    # flow-instance-router.js:57 — was path.length >= maxDepth.
    if depth_min >= max_depth:
        return _decision("blocked", "max_depth", 0.1)

    if _DENY_RE.search(route_text):
        return _decision("blocked", "explicit_block", 0.2)

    if edge.get("type") == "control_flow":
        # Data-carrying control_flow => definite_route; pure-ordering => may_route.
        if control_flow_carries_data(edge):
            if conditional_guard:
                return _decision("may_route", "control_flow_data_conditional", 0.6)
            return _decision("definite_route", "control_flow_data_edge", 0.9)
        return _decision("may_route", "control_flow_order_only", 0.5)

    target_roles = target_profile.get("node_roles") or []
    if any(role in SINK_LIKE_ROLES for role in target_roles):
        if conditional_guard:
            return _decision("may_route", "sink_like_target_conditional", 0.6)
        return _decision("definite_route", "sink_like_target", 0.85)

    if is_decision_like_profile(target_profile):
        if _ALLOW_RE.search(route_text):
            return _decision("definite_route", "decision_allowed", 0.75)
        return _decision("may_route", "decision_unknown", 0.55)

    current_roles = current_profile.get("node_roles") or []
    if "control_context" in current_roles and "data_introduction" in target_roles:
        return _decision("may_route", "control_triggers_source", 0.7)

    return _decision("may_route", "default_flooding", 0.65)


# Port of controlFlowCarriesData (flow-instance-router.js:110-115)
def control_flow_carries_data(edge=None):
    edge = edge or {}
    df = edge.get("data_flow") or {}
    from_param = df.get("from_param") or ""
    to_param = df.get("to_param") or ""
    return not (
        from_param in CONTROL_FLOW_PLACEHOLDER_PARAMS
        and to_param in CONTROL_FLOW_PLACEHOLDER_PARAMS
    )


# Port of isDecisionLikeProfile (flow-instance-router.js:117-123)
def is_decision_like_profile(profile=None):
    profile = profile or {}
    node_roles = profile.get("node_roles") or []
    operation_tags = profile.get("operation_tags") or []
    return bool(
        "decision" in node_roles
        or "routing_decision" in operation_tags
        or "policy_guard" in operation_tags
    )


# Port of hasNegativeConditionGate (flow-instance-router.js:135-142)
def has_negative_condition_gate(profile=None):
    profile = profile or {}
    conditions = profile.get("conditions")
    if not isinstance(conditions, list):
        return False
    for cond in conditions:
        if not cond or str(cond.get("type") or "") != "condition":
            continue
        if NEGATIVE_CONDITION_REGEX.search(str(cond.get("text") or "")):
            return True
    return False


# Port of buildRouteText (flow-instance-router.js:144-159)
def build_route_text(current_profile=None, target_profile=None, edge=None):
    current_profile = current_profile or {}
    target_profile = target_profile or {}
    edge = edge or {}
    evidence = target_profile.get("evidence") or []
    conditions = target_profile.get("conditions") or []
    df = edge.get("data_flow") or {}
    parts = [
        current_profile.get("node_name"),
        target_profile.get("node_name"),
        target_profile.get("description"),
        target_profile.get("instructionText"),
        " ".join(item.get("text") or "" for item in evidence),
        " ".join(item.get("text") or "" for item in conditions),
        edge.get("semantic_reason"),
        df.get("from_param"),
        df.get("to_param"),
        df.get("data_type"),
    ]
    return " ".join(str(p) for p in parts if p)


# Port of decision (flow-instance-router.js:161-167)
def _decision(state, reason, confidence):
    return {"state": state, "reason": reason, "confidence": confidence}
