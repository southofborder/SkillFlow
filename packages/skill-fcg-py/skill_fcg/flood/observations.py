"""Observation recording + summary aggregation (port of the observation parts of
graph-transfer-analyzer.js + observation-analyzer.js, plus the M3 judgment
summary fields).

The recording functions (record_step_observation / record_cycle_periodic_*) are
ported verbatim: observation events, signatures, and flow_state linkage are
unchanged. The NEW M3 work is in build_observations: each observation groups many
label_flow_ids → many reaching StateNodes, and we aggregate their transform_digest
/ word_set / reduction_applied / origin into the observation so DOE can score
task_need / reduction without re-walking the parent chain.

The shared action-step layer (normalized_action_steps / is_sink_like_step /
profile_boundary / is_filter_like_step) lives here as the first consumer; the
analyzer imports it from this module to keep the dependency DAG acyclic.
"""

from .router import SINK_LIKE_ROLES
from .constants import reduction_antichain
from .state import (
    label_availability, reduction_applied_of, reduction_profile_of,
    summarize_transform, transform_sig_of,
)
from .cycle import closure_label_key

_FILTER_TAGS = frozenset([
    "field_slice", "semantic_extraction", "summarization",
    "aggregation", "redaction", "pseudonymization",
])


# Port of normalizedActionSteps (graph-transfer-analyzer.js:1165-1181)
def normalized_action_steps(profile=None):
    profile = profile or {}
    action_steps = profile.get("action_steps")
    if isinstance(action_steps, list) and action_steps:
        steps = action_steps
    else:
        fs = profile.get("formal_semantics") or {}
        steps = [{
            "step_id": f"{profile.get('node_id') or 'node'}:step_001:node",
            "order": 1,
            "operation_type": fs.get("operation_type") or "node",
            "node_roles": profile.get("node_roles") or [],
            "security_tags": profile.get("security_tags") or [],
            "operation_tags": profile.get("operation_tags") or [],
            "boundary": profile_boundary(profile),
            "targets": [],
            "evidence": profile.get("evidence") or [],
            "confidence": profile.get("confidence") or 0.3,
        }]
    # stable sort by numeric order (Python sort is stable, like JS here)
    return sorted(steps, key=lambda s: _num(s.get("order") or 0))


# Port of isSinkLikeStep (graph-transfer-analyzer.js:1209-1211)
def is_sink_like_step(step=None):
    step = step or {}
    return any(role in SINK_LIKE_ROLES for role in (step.get("node_roles") or []))


# Port of isFilterLikeStep (graph-transfer-analyzer.js:1198-1207)
def is_filter_like_step(step=None):
    step = step or {}
    return any(tag in _FILTER_TAGS for tag in (step.get("operation_tags") or []))


# Port of hasSinkLikeStep / hasFilterLikeStep (graph-transfer-analyzer.js:1183-1196)
def has_sink_like_step(steps=None):
    return any(is_sink_like_step(s) for s in (steps or []))


def has_filter_like_step(steps=None):
    return any(is_filter_like_step(s) for s in (steps or []))


# Port of profileBoundary (graph-transfer-analyzer.js:1213-1220)
def profile_boundary(profile=None):
    profile = profile or {}
    return {
        "data_surface": profile.get("data_surface"),
        "receiver_scope": profile.get("receiver_scope"),
        "retention_scope": profile.get("retention_scope"),
        "trust_boundary": profile.get("trust_boundary"),
    }


# Port of isSinkLikeProfile (observation-analyzer.js:76-78)
def is_sink_like_profile(profile=None):
    profile = profile or {}
    return any(role in SINK_LIKE_ROLES for role in (profile.get("node_roles") or []))


# Port of classifyPeriodicSeverity (graph-transfer-analyzer.js:459-470)
def classify_periodic_severity(label_flow=None):
    label_flow = label_flow or {}
    label = label_flow.get("label") or {}
    sensitivity = str(label.get("sensitivity") or "").lower()
    merge_group_ids = label_flow.get("merge_group_ids")
    accumulates = isinstance(merge_group_ids, list) and len(merge_group_ids) > 0
    if sensitivity in ("high", "critical") or accumulates:
        return "amplifying"
    if label.get("mode") == "derived" or _availability_of(label_flow) == "transformed":
        return "mutating"
    return "steady"


PERIODIC_SEVERITY_RANK = {"steady": 0, "mutating": 1, "amplifying": 2}


def _availability_of(label_flow):
    """labelAvailability(label, flow) where flow is a dict-like label_flow. The
    state.label_availability reads flow_mode + filter_derived_seen via getattr;
    for a dict label_flow we adapt through a tiny shim."""
    label = label_flow.get("label") or {}

    class _Shim:
        flow_mode = label_flow.get("flow_mode")
        filter_derived_seen = label.get("mode") == "derived"

    return label_availability(label, _Shim)


def _num(value):
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


# --- observation recording (ported verbatim) ----------------------------------
# `state` is the FloodState (analyzer.py); it provides observation_signatures
# (set), observation_events / all_events (lists), flow_states (dict), and
# next_id(kind, prefix). `flow` is a StateNode.

def _append_ids(existing, additions):
    """Port of appendIds — order-preserving dedupe union of truthy ids."""
    out = list(existing or [])
    seen = set(out)
    for item in (additions or []):
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


# Port of recordStepObservation (graph-transfer-analyzer.js:411-449)
def record_step_observation(flow, profile, step, state, reason):
    signature = f"{profile.get('node_id')}|{step.get('step_id')}|{flow.label_flow_id}|{reason}"
    if signature in state.observation_signatures:
        return
    state.observation_signatures.add(signature)

    event = {
        "observation_event_id": state.next_id("observation", "obsev"),
        "node_id": profile.get("node_id"),
        "node_name": profile.get("node_name"),
        "label_flow_id": flow.label_flow_id,
        "action_step_id": step.get("step_id"),
        "operation_type": step.get("operation_type"),
        "order": step.get("order"),
        "order_confidence": profile.get("action_order_confidence"),
        "ambiguous_action_order": bool(profile.get("ambiguous_action_order")),
        "node_roles": [r for r in (step.get("node_roles") or []) if r in SINK_LIKE_ROLES],
        "security_tags": step.get("security_tags") or [],
        "boundary": step.get("boundary") or profile_boundary(profile),
        "flow_state_id": flow.flow_state_id or "",
        "observed_state_ids": [flow.flow_state_id] if flow.flow_state_id else [],
        "leak_type": "",
        "leak_severity": "",
        "reason": reason,
    }
    flow_state = state.flow_states.get(flow.flow_state_id) if flow.flow_state_id else None
    if flow_state:
        flow_state["reached_observation_ids"] = _append_ids(
            flow_state.get("reached_observation_ids") or [], [event["observation_event_id"]])
    state.observation_events.append(event)
    state.all_events.append({**event, "type": "observation"})


# Port of recordCyclePeriodicObservations (graph-transfer-analyzer.js:481-499)
def record_cycle_periodic_observations(flow, feedback_cycle_paths, severity_labels,
                                       profiles_by_node, state):
    members = [m for m in (severity_labels if severity_labels else [flow.label]) if m]
    severity = "steady"
    for member in members:
        tier = classify_periodic_severity({
            "label": member,
            "flow_mode": flow.flow_mode,
            "merge_group_ids": flow.merge_group_ids,
        })
        if PERIODIC_SEVERITY_RANK[tier] > PERIODIC_SEVERITY_RANK[severity]:
            severity = tier

    cycle_node_ids = []
    seen = set()
    for path in (feedback_cycle_paths or []):
        for nid in path:
            if nid and nid not in seen:
                seen.add(nid)
                cycle_node_ids.append(nid)

    for node_id in cycle_node_ids:
        profile = profiles_by_node.get(node_id)
        if not profile:
            continue
        for step in normalized_action_steps(profile):
            if not is_sink_like_step(step):
                continue
            record_periodic_step_observation(flow, profile, step, severity, state)


# Port of recordPeriodicStepObservation (graph-transfer-analyzer.js:505-538)
def record_periodic_step_observation(flow, profile, step, severity, state):
    signature = f"{profile.get('node_id')}|{step.get('step_id')}|{closure_label_key(flow.label)}|cycle_periodic"
    if signature in state.observation_signatures:
        return
    state.observation_signatures.add(signature)

    event = {
        "observation_event_id": state.next_id("observation", "obsev"),
        "node_id": profile.get("node_id"),
        "node_name": profile.get("node_name"),
        "label_flow_id": flow.label_flow_id,
        "action_step_id": step.get("step_id"),
        "operation_type": step.get("operation_type"),
        "order": step.get("order"),
        "order_confidence": profile.get("action_order_confidence"),
        "ambiguous_action_order": bool(profile.get("ambiguous_action_order")),
        "node_roles": [r for r in (step.get("node_roles") or []) if r in SINK_LIKE_ROLES],
        "security_tags": step.get("security_tags") or [],
        "boundary": step.get("boundary") or profile_boundary(profile),
        "flow_state_id": flow.flow_state_id or "",
        "observed_state_ids": [flow.flow_state_id] if flow.flow_state_id else [],
        "leak_type": "periodic",
        "leak_severity": severity,
        "reason": "cycle_periodic",
    }
    flow_state = state.flow_states.get(flow.flow_state_id) if flow.flow_state_id else None
    if flow_state:
        flow_state["reached_observation_ids"] = _append_ids(
            flow_state.get("reached_observation_ids") or [], [event["observation_event_id"]])
    state.observation_events.append(event)
    state.all_events.append({**event, "type": "observation"})


def _unique_values(values):
    """Port of uniqueValues (observation-analyzer.js:80-82) — dedupe truthy,
    preserving first-seen order."""
    out = []
    seen = set()
    for v in (values or []):
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


# Port of buildObservations (observation-analyzer.js:3-50) + M3 summary
# aggregation. `states_by_flow_id` maps label_flow_id -> StateNode so we can pull
# the judgment summary (transform_digest / word_set / reduction / origin) onto
# each observation. NEW argument (JS had only label_flow_ids); when None,
# summaries are omitted (byte-compatible with JS shape for parity tests).
def build_observations(node_profiles=None, label_flows=None, observation_events=None,
                       states_by_flow_id=None):
    profiles_by_node = {p.get("node_id"): p for p in (node_profiles or [])}
    flows = label_flows or []
    by_node = {}

    if observation_events:
        for event in observation_events:
            key = "|".join([
                str(event.get("node_id")),
                str(event.get("action_step_id") or ""),
                str(event.get("operation_type") or ""),
                str(event.get("order") or 0),
                str(event.get("reason") or ""),
                str(event.get("leak_type") or ""),
                str(event.get("leak_severity") or ""),
            ])
            if key not in by_node:
                by_node[key] = {"event": event, "labelFlowIds": []}
            by_node[key]["labelFlowIds"].append(event.get("label_flow_id"))
        return {"observations": _build_step_observations(by_node, states_by_flow_id)}

    for flow in flows:
        lf_id = flow.get("label_flow_id") if isinstance(flow, dict) else flow.label_flow_id
        label = flow.get("label") if isinstance(flow, dict) else flow.label
        current_node = flow.get("current_node") if isinstance(flow, dict) else flow.current_node
        if not label:
            continue
        profile = profiles_by_node.get(current_node)
        if not is_sink_like_profile(profile):
            continue
        node_id = profile.get("node_id")
        if node_id not in by_node:
            by_node[node_id] = {"profile": profile, "labelFlowIds": []}
        by_node[node_id]["labelFlowIds"].append(lf_id)

    observations = []
    for bucket in by_node.values():
        profile = bucket["profile"]
        label_flow_ids = sorted(_unique_values(bucket["labelFlowIds"]))
        obs = {
            "observation_id": f"obs_{str(len(observations) + 1).zfill(6)}",
            "node_id": profile.get("node_id"),
            "node_name": profile.get("node_name"),
            "node_roles": [r for r in (profile.get("node_roles") or []) if r in SINK_LIKE_ROLES],
            "security_tags": profile.get("security_tags") or [],
            "boundary": {
                "data_surface": profile.get("data_surface"),
                "receiver_scope": profile.get("receiver_scope"),
                "retention_scope": profile.get("retention_scope"),
                "trust_boundary": profile.get("trust_boundary"),
            },
            "label_flow_ids": label_flow_ids,
        }
        _attach_summary(obs, label_flow_ids, states_by_flow_id)
        observations.append(obs)

    return {"observations": observations}


# Port of buildStepObservations (observation-analyzer.js:52-74) + M3 summary.
def _build_step_observations(by_node, states_by_flow_id=None):
    observations = []
    for bucket in by_node.values():
        event = bucket["event"]
        label_flow_ids = sorted(_unique_values(bucket["labelFlowIds"]))
        obs = {
            "observation_id": f"obs_{str(len(observations) + 1).zfill(6)}",
            "node_id": event.get("node_id"),
            "node_name": event.get("node_name"),
            "node_roles": event.get("node_roles") or [],
            "security_tags": event.get("security_tags") or [],
            "boundary": event.get("boundary") or {},
            "action_step_id": event.get("action_step_id") or "",
            "operation_type": event.get("operation_type") or "",
            "order": event.get("order") or 0,
            "order_confidence": event.get("order_confidence") or 0,
            "ambiguous_action_order": bool(event.get("ambiguous_action_order")),
            "leak_type": event.get("leak_type") or "",
            "leak_severity": event.get("leak_severity") or "",
            "label_flow_ids": label_flow_ids,
        }
        _attach_summary(obs, label_flow_ids, states_by_flow_id)
        observations.append(obs)
    return observations


# --- M3 judgment-summary aggregation -------------------------------------------
# Distinct ordered digests are kept (deduped by sig) — NEVER concatenated across
# states, which would invent an execution order that never happened (safety,
# mirrors the transform_seq ordering rule).
def _attach_summary(obs, label_flow_ids, states_by_flow_id):
    if states_by_flow_id is None:
        return
    states = [states_by_flow_id.get(lf) for lf in label_flow_ids]
    states = [s for s in states if s is not None]
    if not states:
        obs.update({
            "transform_digest": [], "transform_sig": [], "word_set": [],
            "origin_node": [], "origin_boundary": [], "meaningful_steps": 0,
            "reduction_applied": False, "reduction_applied_all": False,
            "reduction_profile": [], "reduction_profile_all": [],
        })
        return

    digests_by_sig = {}
    sigs = set()
    words = set()
    origins = []
    origin_boundaries = []
    max_steps = 0
    any_reduction = False
    all_reduction = True
    # reduction antichains across the member states. union = every reduction seen
    # on ANY path (informational, pairs with reduction_applied). intersection =
    # reductions guaranteed on EVERY path (the safety-bearing set, pairs with
    # reduction_applied_all — only these can back an exemption).
    profile_union = set()
    profile_intersection = None

    for s in states:
        sig = transform_sig_of(s.transform_digest) or "none"
        sigs.add(sig)
        if sig not in digests_by_sig:
            digests_by_sig[sig] = list(s.transform_digest)
        words |= (s.word_set or set())
        if s.origin_node and s.origin_node not in origins:
            origins.append(s.origin_node)
        if s.origin_boundary and s.origin_boundary not in origin_boundaries:
            origin_boundaries.append(s.origin_boundary)
        max_steps = max(max_steps, len(s.transform_digest))
        red = reduction_applied_of(s.transform_digest)
        any_reduction = any_reduction or red
        all_reduction = all_reduction and red
        prof = set(reduction_profile_of(s.transform_digest))
        profile_union |= prof
        profile_intersection = prof if profile_intersection is None else (profile_intersection & prof)

    obs["transform_digest"] = [digests_by_sig[k] for k in sorted(digests_by_sig)]
    obs["transform_sig"] = sorted(sigs)
    obs["word_set"] = sorted(words)
    obs["origin_node"] = origins
    obs["origin_boundary"] = origin_boundaries
    obs["meaningful_steps"] = max_steps
    obs["reduction_applied"] = any_reduction
    obs["reduction_applied_all"] = all_reduction
    # Re-antichain the union so a future non-flat poset can't leak a dominated
    # element that was maximal on one path but not another. The intersection of
    # antichains is already an antichain; pass it through for the same reason.
    obs["reduction_profile"] = list(reduction_antichain(profile_union))
    obs["reduction_profile_all"] = list(
        reduction_antichain(profile_intersection or set()))
