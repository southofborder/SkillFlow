"""Flood engine main loop (port of graph-transfer-analyzer.js), design B.

The heavy change vs JS is concentrated in create_initial_state / create_child_state
(the wall: five per-child spread-copied arrays are gone) and build_flow_state_key
(JS-8 + origin_class, a bounded 9-tuple — transform_sig is deliberately NOT a key
component, see state.py). Everything else — action steps, edge prioritization, cycle
closure injection, storage read/write, merge relationships, statistics — is ported
faithfully. StateNode replaces the JS labelFlow record; the deduped flowState
bucket stays a dict.

DOE reconstructs node/edge paths from the single parent pointer, so the dropped
arrays are never read downstream. The two O(1) substitutes are:
  * filter_derived_seen — replaces isDerivedLabel's scan of accumulated events.
  * transform_digest / word_set / parent-chain walk / depth_min — replace paths.
"""

import os

from ..security.data_labeler import short_hash
from .constants import DEFAULT_LIMITS, LIMIT_ENV_KEYS
from .filter import (
    apply_label_flow_filter, compact_label, compact_labels,
    merge_trigger_contexts,
)
from .router import classify_route_state, SINK_LIKE_ROLES
from .state import (
    StateNode, ancestor_path, build_flow_state_key, digest_from_hop,
    hop_marks_derived, label_availability, label_fingerprint,
    reduction_applied_of, reduction_profile_of, seed_word_set, transform_sig_of,
)
from .cycle import (
    closure_label_key, compute_cycle_closure, is_specializing_closure_member,
)
from . import observations as obs_mod
from .observations import (
    has_filter_like_step, has_sink_like_step, is_filter_like_step,
    is_sink_like_step, normalized_action_steps, profile_boundary,
    record_cycle_periodic_observations, record_step_observation,
)


class FloodState:
    """Port of createState (graph-transfer-analyzer.js:540-587). Attribute names
    are snake_case; the duck-typed surface used by observations.py is
    observation_signatures / observation_events / all_events / flow_states /
    next_id."""

    def __init__(self, options):
        self.options = options
        self.label_flows = []            # list[StateNode]
        self.flow_by_id = {}             # label_flow_id -> StateNode
        self.flow_state_index = {}       # state_key -> state_id
        self.flow_states = {}            # state_id -> dict (the deduped bucket)
        self.label_flows_by_node = {}
        self.queue = __import__("collections").deque()  # FIFO, popleft == Array.shift
        self.transitions = []
        self.route_events = []
        self.filter_events = []
        self.merge_events = []
        self.observation_events = []
        self.source_introductions = []
        self.truncation_events = []
        self.all_events = []
        self.truncated = False
        self.cycle_closure_count = 0
        self.closure_cache = {}
        self.ids = {
            "labelFlow": 0, "flowState": 0, "origin": 0, "pathClass": 0,
            "representativePath": 0, "transition": 0, "route": 0, "filter": 0,
            "merge": 0, "observation": 0, "truncation": 0,
        }
        self.observation_signatures = set()
        self.merge_signatures = set()
        # profiles_by_node is set by analyze_graph_transfers so _create_flow_state
        # can resolve origin_boundary (trust_boundary/data_surface of the origin
        # node) — the DOE origin_class input.
        self.profiles_by_node = {}
        self.storage_state = {}
        self.storage_read_profiles = {}
        self.storage_read_signatures = set()
        self.storage_merge_signatures = set()
        # O(1) companions that kill the storage-merge O(W^2): a set for dedup of
        # writer ids (was an O(W) `not in list` scan) and a storage_key->event
        # index (was an O(E) linear scan of merge_events on every write).
        self.storage_written_set = {}
        self.storage_merge_event_by_key = {}
        # storage_key -> set of label fingerprints already in event["labels"],
        # so an UPDATE fold can dedup its single new label in O(1) instead of
        # re-running _unique_labels_by_fingerprint over all W members.
        self.storage_merge_label_fp = {}
        # v6 drops path_classes / representative_paths (path-derived). Origins kept.
        self.origins = {}          # origin_id -> dict
        self.origin_index = {}     # key -> origin_id

    # Port of nextId (graph-transfer-analyzer.js:1840-1843)
    def next_id(self, key, prefix):
        self.ids[key] += 1
        return f"{prefix}_{str(self.ids[key]).zfill(6)}"


# --- limit normalization (graph-transfer-analyzer.js:1810-1838) ----------------
def _read_limit_env():
    result = {}
    for key, env_key in LIMIT_ENV_KEYS.items():
        if env_key in os.environ:
            result[key] = os.environ[env_key]
    return result


def _normalize_positive_limit(value, fallback):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return fallback
    if n != n or n in (float("inf"), float("-inf")) or n <= 0:
        return fallback
    return int(n)  # Math.floor for positive n


def normalize_limits(limits=None):
    limits = limits or {}
    env_limits = _read_limit_env()
    merged = {**DEFAULT_LIMITS, **env_limits, **limits}
    if limits.get("maxInstances") and not limits.get("maxLabelFlows"):
        merged["maxLabelFlows"] = limits["maxInstances"]
    normalized = {
        key: _normalize_positive_limit(value, DEFAULT_LIMITS.get(key, 1))
        for key, value in merged.items()
    }
    normalized["_explicitMaxLabelFlows"] = (
        "maxLabelFlows" in limits or "maxInstances" in limits
        or LIMIT_ENV_KEYS["maxLabelFlows"] in os.environ
        or LIMIT_ENV_KEYS["maxInstances"] in os.environ
    )
    return normalized


# --- small id helpers (graph-transfer-analyzer.js:1645-1665) -------------------
def _unique_values(values):
    out = []
    seen = set()
    for v in (values or []):
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _append_ids(existing, additions):
    # Port of appendIds (graph-transfer-analyzer.js): dedupe truthy, then a PLAIN
    # Array.prototype.sort() — lexicographic UTF-16 code-unit order, NOT
    # localeCompare. For the ASCII id strings here (lf_*/obsev_*/fs_*) Python's
    # default str sort is code-point ascending == JS code-unit ascending, so
    # sorted() matches byte-for-byte. (An earlier port wrongly used locale_compare
    # via cmp_to_key here: both semantically wrong AND O(n log n) Python-level
    # comparator calls that hung dense graphs like 00003.)
    #
    # Fast path (this is the flood's #1 hotspot — ~1.1M calls on 00005, dominated
    # by storage-merge re-touching every prior flow): `existing` is ALWAYS the
    # output of a prior _append_ids (sorted+unique) or []. So when no addition is
    # new, the answer IS `existing` unchanged — skip the O(n log n) rebuild. Output
    # is byte-identical to the full sorted(unique(existing+additions)) either way.
    existing = existing or []
    additions = additions or []
    if not additions:
        return list(existing)
    seen = set(existing)
    has_new = any(a and a not in seen for a in additions)
    if not has_new:
        return list(existing)
    return sorted(_unique_values([*existing, *additions]))


def _append_limited_ids(existing, additions, limit=64):
    return _append_ids(existing, additions)[:limit]


def _edge_key(edge=None):
    edge = edge or {}
    return f"{edge.get('source') or ''}->{edge.get('target') or ''}"


def _group_edges(edges, key):
    grouped = {}
    for edge in (edges or []):
        node_id = edge.get(key) if isinstance(edge, dict) else None
        if not node_id:
            continue
        grouped.setdefault(node_id, []).append(edge)
    return grouped


# Port of analyzeGraphTransfers (graph-transfer-analyzer.js:62-120)
def analyze_graph_transfers(nodes=None, edges=None, node_profiles=None, limits=None):
    nodes = nodes or []
    edges = edges or []
    node_profiles = node_profiles or []
    options = normalize_limits(limits or {})
    profiles_by_node = {p.get("node_id"): p for p in node_profiles}
    nodes_by_id = {n.get("id"): n for n in nodes}
    outgoing = _group_edges(edges, "source")
    state = FloodState(options)
    state.profiles_by_node = profiles_by_node
    ctx = {
        "state": state, "options": options, "outgoing": outgoing,
        "profiles_by_node": profiles_by_node, "nodes_by_id": nodes_by_id,
    }

    for profile in node_profiles:
        if "data_introduction" not in (profile.get("node_roles") or []):
            continue
        if _should_skip_initial_source_introduction(profile, edges):
            continue
        labels = compact_labels((profile.get("data_profile") or {}).get("labels") or [])
        for label in labels:
            initial = create_initial_label_flow(profile, label, state)
            if register_label_flow(initial, state, enqueue=True):
                _record_sink_observations_for_arrived(initial, profile, state)

    while True:
        while len(state.queue) > 0:
            flow = state.queue.popleft()
            if (len(state.all_events) >= options["maxEvents"]
                    or (options["_explicitMaxLabelFlows"]
                        and len(state.label_flows) >= options["maxLabelFlows"])):
                reason = ("max_events" if len(state.all_events) >= options["maxEvents"]
                          else "max_label_flows_or_events")
                _mark_truncated(flow, state, reason)
                continue
            _maybe_create_merge_relationships(flow, state, profiles_by_node)
            expand_label_flow(flow, ctx)
        if not _process_pending_storage_reads(state):
            break

    return {
        "label_flows": state.label_flows,
        "flow_states": _build_flow_states(state),
        "provenance_store": _build_provenance_store(state),
        "node_flow_sets": _build_node_flow_sets(state.label_flows),
        "label_flows_by_node": state.label_flows_by_node,
        "transitions": state.transitions,
        "route_events": state.route_events,
        "filter_events": state.filter_events,
        "merge_events": state.merge_events,
        "observation_events": state.observation_events,
        "source_introductions": state.source_introductions,
        "truncation_events": state.truncation_events,
        "truncated": state.truncated,
        "statistics": _build_statistics(state, options),
    }


# Port of expandLabelFlow (graph-transfer-analyzer.js:122-272)
def expand_label_flow(flow, ctx):
    state = ctx["state"]
    options = ctx["options"]
    outgoing = ctx["outgoing"]
    profiles_by_node = ctx["profiles_by_node"]
    nodes_by_id = ctx["nodes_by_id"]
    if flow.terminated:
        return

    current_profile = profiles_by_node.get(flow.current_node)
    if not current_profile:
        _terminate_label_flow(flow, "missing_current_profile")
        return

    _apply_action_steps_at_node(flow, current_profile, state)

    edges_out = outgoing.get(flow.current_node) or []
    if len(edges_out) == 0:
        _terminate_label_flow(flow, "no_outgoing_edges")
        return

    prioritized = _prioritize_edges(edges_out, profiles_by_node)
    limited_edges = prioritized[:options["maxBranchesPerNode"]]
    if len(edges_out) > len(limited_edges):
        _mark_truncated(flow, state, "max_branches_per_node")

    feedback_cycle_paths = [
        edge.get("feedback_cycle_path") for edge in limited_edges
        if edge.get("is_feedback_edge") and edge.get("feedback_plausibility") == "plausible"
        and isinstance(edge.get("feedback_cycle_path"), list)
    ]
    cycle_nodes_here = _unique_values([
        *(flow._cycle_nodes or []),
        *[nid for path in feedback_cycle_paths for nid in path],
    ])

    specializing_members = []
    if len(feedback_cycle_paths) > 0:
        cache_key = f"{flow.current_node}|{closure_label_key(flow.label)}"
        cached = state.closure_cache.get(cache_key)
        if not cached:
            cached = compute_cycle_closure(
                seed_label=flow.label,
                feedback_cycle_paths=feedback_cycle_paths,
                profiles_by_node=profiles_by_node,
                nodes_by_id=nodes_by_id,
                max_iterations=options["maxClosureIterations"],
                apply_filter=apply_label_flow_filter,
                propagation_profile=_propagation_profile,
            )
            state.closure_cache[cache_key] = cached
            state.cycle_closure_count += 1
        if cached["truncated"]:
            _mark_truncated(flow, state, "cycle_closure_not_converged")
        record_cycle_periodic_observations(
            flow, feedback_cycle_paths, cached["labels"], profiles_by_node, state)
        specializing_members = [
            m for m in (cached["labels"] or [])
            if is_specializing_closure_member(m, flow.label)
        ]

    propagated = 0
    for edge in limited_edges:
        target_profile = profiles_by_node.get(edge.get("target"))
        if not target_profile:
            continue
        route = classify_route_state(
            ancestor_nodes=ancestor_path(flow), depth_min=flow.depth_min,
            current_profile=current_profile, target_profile=target_profile,
            edge=edge, max_depth=options["maxDepth"])
        route_event = _build_route_event(flow, route, current_profile, target_profile, edge, state)
        state.route_events.append(route_event)
        state.all_events.append(route_event)
        if route["state"] == "blocked":
            continue
        propagated += emit_flows_for_label_at_edge(
            flow, current_profile, edge, route, route_event,
            target_profile, cycle_nodes_here, nodes_by_id, state)
        for member in specializing_members:
            member_flow = _shallow_relabel(flow, member)
            propagated += emit_flows_for_label_at_edge(
                member_flow, current_profile, edge, route, route_event,
                target_profile, cycle_nodes_here, nodes_by_id, state)

    if propagated == 0 and not flow.terminated and not flow.truncated:
        _terminate_label_flow(flow, "no_viable_route")


# Port of emitFlowsForLabelAtEdge (graph-transfer-analyzer.js:279-315)
def emit_flows_for_label_at_edge(source_flow, current_profile, edge, route,
                                 route_event, target_profile, cycle_nodes_here,
                                 nodes_by_id, state):
    filter_result = apply_label_flow_filter(
        label_flow=_flow_as_filter_input(source_flow),
        current_profile=_propagation_profile(current_profile),
        edge=edge)
    filter_events = _materialize_filter_events(
        filter_result["filter_events"], state, source_flow, edge)
    state.filter_events.extend(filter_events)
    state.all_events.extend(filter_events)
    state.source_introductions.extend(
        ev for ev in filter_events if ev.get("type") == "source_introduction")

    if not filter_result["branches"]:
        return 0

    emitted = 0
    for branch in filter_result["branches"]:
        keys = set(branch.get("filter_event_keys") or [])
        branch_events = [ev for ev in filter_events if ev.get("local_event_key") in keys]
        hop_events = branch_events if branch_events else filter_events
        child = create_child_label_flow(
            source_flow, target_profile, edge, route, route_event,
            branch, hop_events, cycle_nodes_here, state)
        if register_label_flow(child, state, enqueue=True):
            _record_sink_observations_for_arrived(child, target_profile, state)
            state.transitions.append(
                _build_transition(source_flow, child, edge, route_event, hop_events))
            emitted += 1
    return emitted


# StateNode → the dict shape applyLabelFlowFilter/observations expect for a
# traveling flow. The filter reads only label / flow_mode / trigger_context /
# source_intro_applied_nodes / label_flow_id.
def _flow_as_filter_input(flow):
    return {
        "label": flow.label,
        "label_flow_id": flow.label_flow_id,
        "flow_mode": flow.flow_mode,
        "trigger_context": flow.trigger_context,
        "source_intro_applied_nodes": flow.source_intro_applied_nodes,
    }


# Port of the specializing-member ``{...labelFlow, label: member}`` shallow clone
# (graph-transfer-analyzer.js:256). A StateNode with the seed's carried fields and
# the label swapped; the child recomputes its own digest/key, so a different label
# naturally lands in a different state.
def _shallow_relabel(flow, member):
    clone = StateNode(
        label_flow_id=flow.label_flow_id, flow_state_id=flow.flow_state_id,
        current_node=flow.current_node, current_node_name=flow.current_node_name,
        label=member, flow_mode=flow.flow_mode, phase=flow.phase,
        storage_key=flow.storage_key, confidence=flow.confidence,
        parent_state=flow.parent_state, parent_label_flow_ids=flow.parent_label_flow_ids,
        incoming_edge_id=flow.incoming_edge_id, depth_min=flow.depth_min,
        filter_derived_seen=flow.filter_derived_seen,
        transform_digest=list(flow.transform_digest), transform_sig=flow.transform_sig,
        word_set=set(flow.word_set), local_filter_event_ids=list(flow.local_filter_event_ids),
        origin_node=flow.origin_node, origin_boundary=flow.origin_boundary,
        trigger_context=flow.trigger_context,
        source_intro_applied_nodes=flow.source_intro_applied_nodes,
        _cycle_nodes=flow._cycle_nodes, cycle_handling=flow.cycle_handling,
        merge_group_ids=flow.merge_group_ids,
    )
    return clone


# Port of createInitialLabelFlow (graph-transfer-analyzer.js:590-645).
# The five spread-copy arrays are gone; depth_min=1, acyclic guard walks the
# parent chain, transform_digest=[], word_set seeded from label, parent_state=None.
def create_initial_label_flow(profile, label, state):
    node_id = profile.get("node_id")
    node_name = profile.get("node_name")
    intro_event = {
        "event_id": state.next_id("filter", "filter"),
        "local_event_key": f"initial:{node_id}:{label.get('label')}",
        "type": "source_introduction",
        "node_id": node_id,
        "node_name": node_name,
        "introduced_label": compact_label(label),
        "introduced_labels": [compact_label(label)],
        "context_label": None,
        "evidence": "initial data_introduction node",
    }
    state.filter_events.append(intro_event)
    state.source_introductions.append(intro_event)
    state.all_events.append(intro_event)

    trigger_context = []
    if "control_context" in (profile.get("node_roles") or []):
        trigger_context.append({
            "node_id": node_id, "node_name": node_name,
            "reason": "source is also control context",
        })

    clabel = compact_label(label)
    flow = StateNode(
        label_flow_id=state.next_id("labelFlow", "lf"),
        parent_label_flow_ids=[],
        parent_state=None,
        current_node=node_id,
        current_node_name=node_name,
        label=clabel,
        depth_min=1,
        incoming_edge_id="",
        local_filter_event_ids=[intro_event["event_id"]],
        transform_digest=[],
        transform_sig="",
        word_set=seed_word_set(clabel),
        filter_derived_seen=False,
        trigger_context=trigger_context,
        route_event_id="",
        source_intro_applied_nodes=[node_id],
        flow_mode="source_introduction",
        confidence=_round_confidence(clabel.get("confidence") or 0.3),
        terminated=False, termination_reason="", truncated=False,
        merge_group_ids=[], parent_label_origin="",
        storage_key="",
        _cycle_nodes=frozenset(),
    )
    _normalize_state(flow)
    return flow


# Port of resolveChildFlowMode (graph-transfer-analyzer.js:657-661)
def _resolve_child_flow_mode(branch, route):
    from .constants import SEMANTIC_FLOW_MODES
    branch_mode = branch.get("flow_mode") or ""
    if branch_mode in SEMANTIC_FLOW_MODES:
        return branch_mode
    return "definite_flow" if route.get("state") == "definite_route" else "may_flow"


# Port of createChildLabelFlow (graph-transfer-analyzer.js:663-700) — MOST CHANGED.
# The five spread-copies are replaced by: single parent_state, depth_min+1,
# parent-chain acyclic guard, incoming_edge_id, local_filter_event_ids (this hop),
# transform_digest append + transform_sig, word_set union, filter_derived_seen |=.
def create_child_label_flow(parent, target_profile, edge, route, route_event,
                            branch, filter_events, cycle_nodes_here, state):
    label = compact_label(branch.get("label"))
    trigger_context = merge_trigger_contexts(
        parent.trigger_context or [], branch.get("trigger_context") or [])
    confidence = _round_confidence(
        float(parent.confidence or 0.3)
        * float(route.get("confidence") or 0.65)
        * float(branch.get("confidence_multiplier") or 1)
        * float(label.get("confidence") or (parent.label or {}).get("confidence") or 0.7))

    cycle = _resolve_child_cycle_state(parent, target_profile, edge, route, cycle_nodes_here)

    target_id = target_profile.get("node_id")
    # this hop's real transforms, appended in execution order (T1-safety)
    hop_digest = digest_from_hop(filter_events)
    # Digest must only carry transforms from origin_node onward — DOE's
    # transformSequence trims the chain to the label's origin (trimChainToOrigin)
    # and counts only post-origin-path nodes (plan line 112). When a
    # source_introduction re-introduces the label at a NEW origin_node, the parent's
    # accumulated digest belonged to the PREVIOUS label identity and must be
    # dropped, else transform_sig over-counts (e.g. a pre-origin `summarization`
    # leaking into a freshly-introduced label's sig — 253/835 units on 00002).
    # Criterion: child label origin differs from parent label origin => reset.
    parent_origin = (parent.label or {}).get("origin_node") or parent.origin_node or ""
    child_origin = label.get("origin_node") or ""
    if child_origin and parent_origin and child_origin != parent_origin:
        child_digest = list(hop_digest)
    else:
        child_digest = list(parent.transform_digest) + hop_digest
    hop_event_ids = [ev.get("event_id") for ev in (filter_events or []) if ev.get("event_id")]
    # word_set union: parent tokens + this label's surface tokens
    child_words = set(parent.word_set) | seed_word_set(label)

    parent_ids = (branch.get("parent_label_flow_ids")
                  if branch.get("parent_label_flow_ids") else [parent.label_flow_id])

    child = StateNode(
        label_flow_id=branch.get("label_flow_id") or "",
        parent_label_flow_ids=parent_ids,
        parent_state=parent,
        current_node=target_id,
        current_node_name=target_profile.get("node_name"),
        label=label,
        depth_min=parent.depth_min + 1,
        incoming_edge_id=(edge.get("id") or _edge_key(edge)),
        local_filter_event_ids=hop_event_ids,
        transform_digest=child_digest,
        transform_sig=transform_sig_of(child_digest),
        word_set=child_words,
        filter_derived_seen=parent.filter_derived_seen or hop_marks_derived(filter_events),
        trigger_context=trigger_context,
        source_intro_applied_nodes=(branch.get("source_intro_applied_nodes")
                                    or parent.source_intro_applied_nodes or []),
        flow_mode=_resolve_child_flow_mode(branch, route),
        confidence=confidence,
        route_event_id=route_event.get("event_id", ""),
        terminated=False, termination_reason="", truncated=False,
        merge_group_ids=[x for x in [*(parent.merge_group_ids or []),
                                     *(branch.get("merge_group_ids") or [])] if x],
        parent_label_origin=parent.label_flow_id,
        storage_key=branch.get("storage_key") or parent.storage_key or "",
        _cycle_nodes=frozenset(cycle["cycle_nodes"]),
        cycle_handling=cycle["cycle_handling"],
    )
    _normalize_state(child)
    return child


# Port of resolveChildCycleState (graph-transfer-analyzer.js:709-727)
def _resolve_child_cycle_state(parent, target_profile, edge, route, cycle_nodes_here):
    target_id = target_profile.get("node_id")
    cycle_nodes = _unique_values([*(parent._cycle_nodes or []), *cycle_nodes_here])
    exits_cycle = (len(cycle_nodes) > 0
                   and not edge.get("is_feedback_edge")
                   and target_id not in cycle_nodes)
    return {"cycle_nodes": cycle_nodes, "cycle_handling": "collapse" if exits_cycle else ""}


# Port of normalizeLabelFlow (graph-transfer-analyzer.js:1563-1583), path-free.
# Enforces single parent (slice(0,1)), recomputes label + origin fields +
# label_fingerprint. path_fingerprint is DROPPED (path-derived; v6 omits it).
# Mutates the StateNode in place (JS returned a new object; we keep identity).
def _normalize_state(flow):
    label = compact_label(flow.label)
    parent_ids = _unique_values(flow.parent_label_flow_ids or [])[:1]
    flow.label = label
    flow.parent_label_flow_ids = parent_ids
    flow.origin_node = label.get("origin_node") or ""
    flow.origin_node_name = label.get("origin_node_name") or label.get("origin_node") or ""
    flow.introduced_at = label.get("introduced_at") or ""
    flow.merge_group_ids = _append_ids([], flow.merge_group_ids or [])
    flow.storage_key = flow.storage_key or ""
    flow.label_fingerprint = label_fingerprint(label)


# Port of registerLabelFlow (graph-transfer-analyzer.js:1255-1292).
def register_label_flow(flow, state, enqueue=False):
    if not flow.label_flow_id:
        flow.label_flow_id = state.next_id("labelFlow", "lf")
    _normalize_state(flow)
    # origin_node is set by _normalize_state from the label; resolve its boundary
    # equivalence class now so the StateNode carries it for observation summaries.
    flow.origin_boundary = _resolve_origin_boundary(flow.origin_node, state)
    _attach_flow_state_metadata(flow, state)
    state_key = build_flow_state_key(flow)
    existing_id = state.flow_state_index.get(state_key)
    if existing_id:
        existing_state = state.flow_states.get(existing_id)
        existing_flow = state.flow_by_id.get(existing_state["representative_label_flow_id"])
        _merge_flow_into_representative(existing_flow, flow, existing_state, state)
        return False

    if len(state.label_flows) >= state.options["maxLabelFlows"]:
        _mark_truncated(flow, state, "max_label_flows")
        return False

    flow_state = _create_flow_state(flow, state_key, state)
    flow.flow_state_id = flow_state["state_id"]

    state.flow_state_index[state_key] = flow_state["state_id"]
    state.flow_states[flow_state["state_id"]] = flow_state
    state.flow_by_id[flow.label_flow_id] = flow
    state.label_flows.append(flow)
    state.label_flows_by_node.setdefault(flow.current_node, []).append(flow)
    if enqueue:
        state.queue.append(flow)
    return True


# Port of createFlowState (graph-transfer-analyzer.js:1349-1371). The deduped
# bucket; enriched with the design-B judgment-unit fields.
def _create_flow_state(flow, state_key, state):
    return {
        "state_id": state.next_id("flowState", "fs"),
        "state_key": state_key,
        "representative_label_flow_id": flow.label_flow_id,
        "node_id": flow.current_node or "",
        "node_name": flow.current_node_name or "",
        "label": compact_label(flow.label),
        "availability": label_availability(flow.label or {}, flow),
        "storage_key": flow.storage_key or "",
        "phase": flow.phase or "after_action",
        "origin_ids": flow.origin_ids or [],
        "provenance_event_ids": flow.provenance_event_ids or [],
        "label_flow_ids": [flow.label_flow_id],
        "label_flow_id_count": 1,
        "merged_path_count": 1,
        "confidence_min": flow.confidence or 0.3,
        "confidence_max": flow.confidence or 0.3,
        "reached_observation_ids": [],
        # design-B decision-unit fields
        "transform_sig": flow.transform_sig or "none",
        "transform_digest": flow.transform_digest,
        "word_set": sorted(flow.word_set),
        "origin_node": flow.origin_node,
        "origin_boundary": _resolve_origin_boundary(flow.origin_node, state),
        "depth_min": flow.depth_min,
        # reduction_applied is a CONSERVATIVE AND across every path merged into
        # this state (see _merge_flow_into_representative). Seeded from the first
        # (representative) path's digest. Once transform_sig left the key, a
        # reducing path and a non-reducing path can share a key and merge; the
        # representative keeps only ONE digest, so deriving reduction_applied from
        # that single digest would be first-arrival-dependent and could report a
        # reduction that some merged path never applied (false-negative / missed
        # exposure). ANDing keeps it true only when ALL merged paths reduced.
        #
        # NOTE (reduction-antichain era): reduction_profile_sig is now a KEY
        # component (state.build_flow_state_key), so every path merged into this
        # bucket has the IDENTICAL reduction antichain — reduction_applied is
        # homogeneous and the AND below is a proven no-op (true∧true / false∧false).
        # It is kept as a defensive invariant. The profile is the exact per-bucket
        # protection fact DOE/LLM read to judge WHICH kind of reduction ran.
        "reduction_applied": reduction_applied_of(flow.transform_digest),
        "reduction_profile": list(reduction_profile_of(flow.transform_digest)),
    }


# Resolve the origin node's boundary equivalence class — the input DOE originClass
# reads (doe-analyzer.js:491-498): {trust_boundary, data_surface} of the origin
# node's profile, 'unknown' when the profile is missing. Stored on the state (and
# mirrored onto the StateNode) so the observation summary and the granularity
# parity test can synthesize origin_class without a second profile join.
def _resolve_origin_boundary(origin_node, state):
    profile = state.profiles_by_node.get(origin_node)
    if not profile:
        return {"trust_boundary": "unknown", "data_surface": "unknown"}
    return {
        "trust_boundary": profile.get("trust_boundary") or "unknown",
        "data_surface": profile.get("data_surface") or "unknown",
    }


# Port of mergeFlowIntoRepresentative (graph-transfer-analyzer.js:1373-1404).
# The key is JS-8 + origin_class (transform_sig is NOT a key component), so the
# fan-in is JS-like plus an origin_class split: flows that differ only in path
# order (or in any un-keyed transform_digest) now merge here. That is exactly why
# reduction_applied must be a conservative AND below — a reducing and a
# non-reducing path can share this bucket, and the representative keeps only one
# transform_digest. confidence_min/max formula unchanged.
def _merge_flow_into_representative(existing_flow, incoming_flow, flow_state, state):
    if not existing_flow or not flow_state:
        return
    flow_state["label_flow_ids"] = _append_ids(
        flow_state.get("label_flow_ids") or [], [incoming_flow.label_flow_id])
    flow_state["label_flow_id_count"] = max(
        flow_state.get("label_flow_id_count") or 1, len(flow_state.get("label_flow_ids") or []))
    flow_state["merged_path_count"] = int(flow_state.get("merged_path_count") or 1) + 1
    flow_state["origin_ids"] = _append_ids(
        flow_state.get("origin_ids") or [], incoming_flow.origin_ids or [])
    flow_state["provenance_event_ids"] = _append_ids(
        flow_state.get("provenance_event_ids") or [], incoming_flow.provenance_event_ids or [])
    flow_state["confidence_min"] = min(
        float(flow_state.get("confidence_min") or 1), float(incoming_flow.confidence or 0.3))
    flow_state["confidence_max"] = max(
        float(flow_state.get("confidence_max") or 0), float(incoming_flow.confidence or 0.3))
    # Conservative AND: the state's reduction_applied stays true only if EVERY
    # merged path reduced before egress. transform_sig no longer separates a
    # reducing path from a non-reducing one, so a path that applied no reduction
    # can merge here and must pull the flag to false (safe direction — treat the
    # sink as unprotected rather than credit a reduction some path skipped).
    flow_state["reduction_applied"] = bool(
        flow_state.get("reduction_applied")) and reduction_applied_of(
        incoming_flow.transform_digest)

    existing_flow.parent_label_flow_ids = _append_limited_ids(
        existing_flow.parent_label_flow_ids or [],
        incoming_flow.parent_label_flow_ids or [], 1)
    existing_flow.merge_group_ids = _append_ids(
        existing_flow.merge_group_ids or [], incoming_flow.merge_group_ids or [])
    existing_flow.origin_ids = flow_state["origin_ids"]
    existing_flow.provenance_event_ids = flow_state["provenance_event_ids"]
    existing_flow.confidence = _round_confidence(
        max(float(existing_flow.confidence or 0.3), float(incoming_flow.confidence or 0.3)))


# Port of attachFlowStateMetadata (graph-transfer-analyzer.js:1332-1347), minus
# the path_class / representative_path interners (v6 drops both). Only origin
# interning (label-derived) + provenance_event_ids accumulation remain.
def _attach_flow_state_metadata(flow, state):
    origin_id = _intern_origin(flow, state)
    flow.origin_ids = _append_ids(flow.origin_ids or [], [origin_id])
    flow.provenance_event_ids = _append_ids(
        flow.provenance_event_ids or [],
        [*(flow.local_filter_event_ids or []),
         *([flow.route_event_id] if flow.route_event_id else []),
         *(flow.merge_group_ids or [])])


# Port of internOrigin (graph-transfer-analyzer.js:1406-1429)
def _intern_origin(flow, state):
    label = flow.label or {}
    key = "|".join([
        label.get("origin_node") or flow.origin_node or "",
        label.get("introduced_at") or flow.introduced_at or "",
        label.get("label") or "",
        label.get("evidence_kind") or "",
        label.get("evidence_text") or "",
    ])
    existing = state.origin_index.get(key)
    if existing:
        return existing
    origin_id = state.next_id("origin", "origin")
    state.origin_index[key] = origin_id
    state.origins[origin_id] = {
        "origin_id": origin_id,
        "origin_node": label.get("origin_node") or flow.origin_node or "",
        "origin_node_name": (label.get("origin_node_name") or flow.origin_node_name
                             or label.get("origin_node") or ""),
        "introduced_at": label.get("introduced_at") or flow.introduced_at or "",
        "label": compact_label(label),
        "evidence_kind": label.get("evidence_kind") or "",
        "evidence_text": label.get("evidence_text") or "",
    }
    return origin_id


# Port of materializeFilterEvents (graph-transfer-analyzer.js:1522-1533).
# NOTE: this re-stamps a fresh global event_id (filter_NNNNNN) distinct from the
# filter's content-hash local event_id. local_filter_event_ids on the child use
# these global ids; DOE resolves them via provenance_graph.events.filtering.
def _materialize_filter_events(events, state, flow, edge):
    out = []
    for event in (events or []):
        out.append({
            **event,
            "event_id": state.next_id("filter", "filter"),
            "label_flow_id": flow.label_flow_id,
            "action_step_id": event.get("action_step_id") or "",
            "operation_type": event.get("operation_type") or "",
            "edge_id": edge.get("id") or _edge_key(edge),
            "source": edge.get("source"),
            "target": edge.get("target"),
        })
    return out


# Port of buildTransition (graph-transfer-analyzer.js:1535-1549)
def _build_transition(parent, child, edge, route_event, filter_events):
    return {
        "transition_id": "tr_" + short_hash("|".join([
            parent.label_flow_id, child.label_flow_id, edge.get("id") or _edge_key(edge)])),
        "type": "edge_propagation",
        "from_label_flow_id": parent.label_flow_id,
        "to_label_flow_id": child.label_flow_id,
        "fcg_edge_id": edge.get("id") or _edge_key(edge),
        "source": edge.get("source"),
        "target": edge.get("target"),
        "route_event_id": route_event.get("event_id"),
        "filter_event_ids": [ev.get("event_id") for ev in (filter_events or [])],
        "route_state": route_event.get("state"),
        "route_confidence": route_event.get("confidence"),
    }


# Port of buildRouteEvent (graph-transfer-analyzer.js:1506-1520)
def _build_route_event(flow, route, current_profile, target_profile, edge, state):
    return {
        "event_id": state.next_id("route", "route"),
        "type": "routing",
        "label_flow_id": flow.label_flow_id,
        "edge_id": edge.get("id") or _edge_key(edge),
        "source": edge.get("source"),
        "target": edge.get("target"),
        "state": route["state"],
        "reason": route["reason"],
        "confidence": route["confidence"],
    }


# Port of propagationProfile (graph-transfer-analyzer.js:1245-1253)
def _propagation_profile(profile):
    profile = profile or {}
    if _is_produced_artifact_profile_steps(profile):
        return {**profile, "operation_type": "produce_artifact"}
    return _filter_profile_for_propagation(profile)


# Port of filterProfileForPropagation (graph-transfer-analyzer.js:1222-1243)
def _filter_profile_for_propagation(profile):
    steps = normalized_action_steps(profile)
    filter_steps = [s for s in steps if is_filter_like_step(s)]
    if not filter_steps:
        return profile

    def _sorted_tags(values):
        # JS uses a plain Array.prototype.sort() here (graph-transfer-analyzer.js
        # :1236-1238) — code-unit order, NOT localeCompare. sorted() matches for
        # these ASCII tag strings.
        return sorted(_unique_values(values))

    return {
        **profile,
        "operation_tags": _sorted_tags(
            [t for s in filter_steps for t in (s.get("operation_tags") or [])]),
        "security_tags": _sorted_tags(
            [t for s in filter_steps for t in (s.get("security_tags") or [])]),
        "node_roles": _sorted_tags(
            [t for s in filter_steps for t in (s.get("node_roles") or [])]),
        "evidence": [e for s in filter_steps for e in (s.get("evidence") or [])],
        "action_step_id": filter_steps[0].get("step_id"),
        "operation_type": filter_steps[0].get("operation_type"),
    }


# Port of isProducedArtifactProfile (graph-transfer-analyzer.js:322-325) — the
# STEPS variant (distinct from the filter's evidence variant).
def _is_produced_artifact_profile_steps(profile):
    profile = profile or {}
    if any(s.get("operation_type") == "produce_artifact"
           for s in normalized_action_steps(profile)):
        return True
    return any(item.get("kind") == "formal_semantics.produce_artifact"
               for item in (profile.get("evidence") or []))


# Port of shouldSkipInitialSourceIntroduction (graph-transfer-analyzer.js:317-332)
def _should_skip_initial_source_introduction(profile, edges):
    if not _is_produced_artifact_profile_steps(profile):
        return False
    return any(edge.get("target") == profile.get("node_id")
               and edge.get("validation_method") == "doc_flow_object_context"
               for edge in (edges or []))


# Port of applyActionStepsAtNode (graph-transfer-analyzer.js:334-358)
def _apply_action_steps_at_node(flow, profile, state):
    steps = normalized_action_steps(profile)
    ambiguous_dual_phase = bool(
        profile.get("ambiguous_action_order")
        and has_sink_like_step(steps) and has_filter_like_step(steps))

    if ambiguous_dual_phase:
        for step in [s for s in steps if is_sink_like_step(s)]:
            record_step_observation(flow, profile, step, state, "pre_action_observation")

    for index, step in enumerate(steps):
        if not _label_available_before_step(flow, profile, steps, index):
            continue
        storage_key = _infer_storage_key(profile, step)
        if is_sink_like_step(step) and not ambiguous_dual_phase:
            record_step_observation(flow, profile, step, state, "step_observation")
        if storage_key and _is_storage_write_step(step, profile):
            _record_storage_write(flow, storage_key, state, profile, step)
        if storage_key and _is_storage_read_step(step, profile):
            _record_storage_read_profile(storage_key, state, profile, step)


# Port of recordSinkObservationsForArrivedLabelFlow (graph-transfer-analyzer.js:360-377)
def _record_sink_observations_for_arrived(flow, profile, state):
    steps = normalized_action_steps(profile)
    ambiguous_dual_phase = bool(
        profile.get("ambiguous_action_order")
        and has_sink_like_step(steps) and has_filter_like_step(steps))
    if ambiguous_dual_phase:
        for step in [s for s in steps if is_sink_like_step(s)]:
            record_step_observation(flow, profile, step, state, "pre_action_observation")
        return
    for index, step in enumerate(steps):
        if not is_sink_like_step(step):
            continue
        if not _label_available_before_step(flow, profile, steps, index):
            continue
        record_step_observation(flow, profile, step, state, "step_observation")


# Port of labelAvailableBeforeStep (graph-transfer-analyzer.js:379-397)
def _label_available_before_step(flow, profile, steps, step_index):
    simulated = _flow_as_filter_input(flow)
    for step in steps[:step_index]:
        if not is_filter_like_step(step):
            continue
        result = apply_label_flow_filter(
            label_flow=simulated,
            current_profile=_filter_profile_from_step(profile, step),
            edge={})
        if not result["branches"]:
            return False
        branch = result["branches"][0]
        simulated = {
            **simulated,
            "label": compact_label(branch.get("label")),
            "flow_mode": branch.get("flow_mode") or simulated.get("flow_mode"),
        }
    return True


# Port of filterProfileFromStep (graph-transfer-analyzer.js:399-409)
def _filter_profile_from_step(profile, step):
    return {
        **profile,
        "node_roles": step.get("node_roles") or [],
        "security_tags": step.get("security_tags") or [],
        "operation_tags": step.get("operation_tags") or [],
        "evidence": step.get("evidence") or [],
        "action_step_id": step.get("step_id"),
        "operation_type": step.get("operation_type"),
    }


# Port of prioritizeEdgesForObservationCoverage (graph-transfer-analyzer.js:1773-1795)
def _prioritize_edges(edges, profiles_by_node):
    indexed = [
        {"edge": edge, "index": i, "priority": _observation_coverage_priority(edge, profiles_by_node)}
        for i, edge in enumerate(edges or [])
    ]
    indexed.sort(key=lambda item: (item["priority"], item["index"]))
    return [item["edge"] for item in indexed]


def _observation_coverage_priority(edge, profiles_by_node):
    edge = edge or {}
    target_profile = profiles_by_node.get(edge.get("target"))
    if not target_profile:
        return 100
    roles = set(target_profile.get("node_roles") or [])
    tags = set(target_profile.get("security_tags") or [])
    boundary = (target_profile.get("trust_boundary") or target_profile.get("receiver_scope")
                or target_profile.get("data_surface") or "")
    if "external_egress" in roles:
        return 0
    if boundary == "external_network" or "network_egress" in tags or "webhook_post" in tags:
        return 1
    if "model_inference" in roles or boundary == "model_provider":
        return 2
    if ("local_persistence" in roles or target_profile.get("retention_scope") == "persistent"
            or target_profile.get("retention_scope") == "external"):
        return 3
    if "tool_invocation" in roles:
        return 4
    if "command_execution" in roles or "destructive_operation" in roles:
        return 5
    if any(r in SINK_LIKE_ROLES for r in (target_profile.get("node_roles") or [])):
        return 6
    return 20


# Port of terminateLabelFlow (graph-transfer-analyzer.js:1703-1706)
def _terminate_label_flow(flow, reason):
    flow.terminated = True
    flow.termination_reason = reason


# Port of markTruncated (graph-transfer-analyzer.js:1686-1701)
def _mark_truncated(flow, state, reason):
    state.truncated = True
    if flow:
        flow.truncated = True
        flow.termination_reason = flow.termination_reason or reason
    event = {
        "event_id": state.next_id("truncation", "trunc"),
        "type": "truncation",
        "label_flow_id": flow.label_flow_id if flow else "",
        "node_id": flow.current_node if flow else "",
        "reason": reason,
    }
    state.truncation_events.append(event)
    state.all_events.append(event)


def _round_confidence(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.3
    if n != n or n in (float("inf"), float("-inf")):
        return 0.3
    from ..llm.normalizers import js_round
    return max(0, min(1, js_round(n * 1000) / 1000))


# --- storage read/write (graph-transfer-analyzer.js:910-1026) ------------------
def _record_storage_write(flow, storage_key, state, profile, step=None):
    flow.storage_key = storage_key
    written = state.storage_state.setdefault(storage_key, [])
    seen = state.storage_written_set.setdefault(storage_key, set())
    lf_id = flow.label_flow_id
    is_new = lf_id not in seen  # O(1) set membership (was O(W) list scan)
    if is_new:
        seen.add(lf_id)
        written.append(lf_id)
    # Fold ONLY the just-written flow into the merge event (was: rebuild all W
    # members on every write -> O(W^2)). A duplicate write folds nothing.
    _maybe_create_storage_merge_event(
        storage_key, state, profile, step,
        new_writer_id=lf_id if is_new else None)


def _record_storage_read_profile(storage_key, state, profile, step=None):
    key = f"{profile.get('node_id')}:{step.get('step_id') if step else 'node'}"
    state.storage_read_profiles.setdefault(storage_key, {})[key] = {"profile": profile, "step": step}


def _process_pending_storage_reads(state):
    created = 0
    for storage_key, profiles in state.storage_read_profiles.items():
        if storage_key not in state.storage_state:
            continue
        for item in list(profiles.values()):
            created += _maybe_create_storage_read_flows(storage_key, state, item["profile"], item["step"])
    return created > 0


def _maybe_create_storage_read_flows(storage_key, state, profile, step=None):
    written_ids = state.storage_state.get(storage_key) or []
    if not written_ids:
        return 0
    written_flows = [state.flow_by_id.get(i) for i in written_ids]
    written_flows = [f for f in written_flows if f][:state.options["maxMergeParents"]]
    if not written_flows:
        return 0

    merge_event = _maybe_create_storage_merge_event(storage_key, state, profile, step)
    created = 0
    for written_flow in written_flows:
        signature = f"{profile.get('node_id')}|{step.get('step_id') if step else 'node'}|storage_read|{storage_key}|{written_flow.label_flow_id}"
        if signature in state.storage_read_signatures:
            continue
        state.storage_read_signatures.add(signature)

        if len(state.label_flows) >= state.options["maxLabelFlows"]:
            _mark_truncated(written_flow, state, "max_label_flows_before_storage_read")
            return created
        storage_label = {**written_flow.label, "introduced_at": profile.get("node_id")}
        event = {
            "event_id": state.next_id("filter", "filter"),
            "type": "storage_read",
            "node_id": profile.get("node_id"),
            "node_name": profile.get("node_name"),
            "label_flow_id": written_flow.label_flow_id,
            "action_step_id": step.get("step_id") if step else "",
            "operation_type": step.get("operation_type") if step else "",
            "storage_key": storage_key,
            "introduced_label": compact_label(storage_label),
            "introduced_labels": [compact_label(storage_label)],
            "parent_label_flow_ids": [written_flow.label_flow_id],
            "evidence": f"read label flow from persisted storage {storage_key}",
        }
        state.filter_events.append(event)
        state.source_introductions.append(event)
        state.all_events.append(event)

        clabel = compact_label(storage_label)
        # storage-read child: single parent pointer + this-hop event; no path arrays.
        child = StateNode(
            label_flow_id=state.next_id("labelFlow", "lf"),
            parent_label_flow_ids=[written_flow.label_flow_id],
            parent_state=written_flow,
            current_node=profile.get("node_id"),
            current_node_name=profile.get("node_name"),
            label=clabel,
            depth_min=written_flow.depth_min + 1,
            incoming_edge_id=_storage_read_edge_id(written_flow.current_node, profile.get("node_id")),
            local_filter_event_ids=[event["event_id"]],
            # storage_read is not a REAL_TRANSFORM_TYPE → digest unchanged from parent
            transform_digest=list(written_flow.transform_digest),
            transform_sig=written_flow.transform_sig,
            word_set=set(written_flow.word_set) | seed_word_set(clabel),
            filter_derived_seen=written_flow.filter_derived_seen,
            trigger_context=written_flow.trigger_context or [],
            route_event_id="",
            source_intro_applied_nodes=_unique_values(
                [*(written_flow.source_intro_applied_nodes or []), profile.get("node_id")]),
            flow_mode="storage_read",
            confidence=_round_confidence(float(written_flow.confidence or 0.3) * 0.9),
            terminated=False, termination_reason="", truncated=False,
            merge_group_ids=_append_ids(written_flow.merge_group_ids or [],
                                        [merge_event["event_id"] if merge_event else ""]),
            parent_label_origin=written_flow.label_flow_id,
            storage_key=storage_key,
            _cycle_nodes=frozenset(written_flow._cycle_nodes),
        )
        _normalize_state(child)

        if register_label_flow(child, state, enqueue=True):
            created += 1
            state.transitions.append({
                "transition_id": state.next_id("transition", "tr"),
                "type": "storage_read",
                "from_label_flow_id": written_flow.label_flow_id,
                "to_label_flow_id": child.label_flow_id,
                "fcg_edge_id": "",
                "source": written_flow.current_node,
                "target": profile.get("node_id"),
                "route_event_id": "",
                "filter_event_ids": [event["event_id"]],
                "route_state": "definite_route",
            })
    return created


def _maybe_create_storage_merge_event(storage_key, state, profile, step=None,
                                      new_writer_id=None):
    written = state.storage_state.get(storage_key) or []
    if len(written) < 2:
        return None
    existing = state.storage_merge_event_by_key.get(storage_key)
    if existing is not None:
        # UPDATE: fold ONLY the single just-written flow (O(1)). The old code
        # rebuilt all W members on every write here -> O(W^2). A read-path call
        # (new_writer_id=None) adds no member, just returns the event ref.
        if new_writer_id is not None:
            flow = state.flow_by_id.get(new_writer_id)
            if flow:
                _fold_writer_into_merge_event(existing, flow, state, storage_key)
        return existing
    # CREATE: first time this key reaches 2 writers. Fold the full current batch
    # once (sorted) to reproduce the old full-rebuild's label_flow_ids ordering.
    # new_writer_id is irrelevant on CREATE.
    signature = f"{storage_key}|storage_merge"
    if signature in state.storage_merge_signatures:
        return None
    state.storage_merge_signatures.add(signature)
    event = {
        "event_id": state.next_id("merge", "merge"),
        "type": "storage_merge",
        "node_id": profile.get("node_id"),
        "node_name": profile.get("node_name"),
        "action_step_id": step.get("step_id") if step else "",
        "operation_type": step.get("operation_type") if step else "",
        "storage_key": storage_key,
        "label_flow_ids": [],
        "label_flow_id_count": 0,
        "labels": [],
        "evidence": f"multiple label flows persisted into {storage_key}",
    }
    state.merge_events.append(event)
    state.all_events.append(event)
    state.storage_merge_event_by_key[storage_key] = event
    written_ids = sorted(_unique_values(written))
    written_flows = [f for f in (state.flow_by_id.get(i) for i in written_ids) if f]
    _update_merge_event_members(event, written_flows)
    # seed the O(1) fingerprint dedup set from the labels just installed
    state.storage_merge_label_fp[storage_key] = {
        _merge_label_fp(lbl) for lbl in event["labels"]}
    _apply_merge_event_to_flows(event, written_flows)
    return event


def _fold_writer_into_merge_event(event, flow, state, storage_key):
    # O(1) incremental fold of one new writer into an existing storage_merge event.
    # event["label_flow_ids"] / ["labels"] are internal-only (never emitted, never
    # tested -- public output takes only flow.merge_group_ids + the scalar event
    # count), so we append in arrival order instead of re-sorting / re-fingerprinting
    # all W members. Ids need no dedup: the caller only folds a writer once (on is_new).
    lf_id = flow.label_flow_id
    if lf_id:
        ids = event["label_flow_ids"]
        ids.append(lf_id)
        event["_all_label_flow_ids"] = ids
        event["label_flow_id_count"] = len(ids)
    if flow.label:
        fps = state.storage_merge_label_fp.setdefault(storage_key, set())
        lbl = compact_label(flow.label)
        key = _merge_label_fp(lbl)
        if key not in fps:
            fps.add(key)
            event["labels"].append(lbl)
            event["label_count"] = len(event["labels"])
    _apply_merge_event_to_flows(event, [flow])


def _update_merge_event_members(event, flows):
    existing_ids = event.get("_all_label_flow_ids") or event.get("label_flow_ids") or []
    ids = sorted(_unique_values([*existing_ids, *[f.label_flow_id for f in flows if f.label_flow_id]]))
    event["_all_label_flow_ids"] = ids
    event["label_flow_ids"] = ids
    event["label_flow_id_count"] = len(ids)
    event["label_flow_ids_truncated"] = False
    labels = _unique_labels_by_fingerprint(
        [*(event.get("labels") or []), *[compact_label(f.label) for f in flows if f.label]])
    event["labels"] = labels
    event["label_count"] = len(labels)
    event["labels_truncated"] = False


def _apply_merge_event_to_flows(event, flows):
    for flow in flows:
        flow.storage_key = event.get("storage_key") or flow.storage_key or ""
        flow.merge_group_ids = _append_ids(flow.merge_group_ids or [], [event["event_id"]])


def _merge_label_fp(label):
    # Single source of truth for a merge label's dedup fingerprint (shared by
    # _unique_labels_by_fingerprint's batch dedup and the O(1) incremental fold).
    return "|".join([
        label.get("label") or "", label.get("category") or "",
        label.get("subtype") or "", label.get("origin_node") or "",
        label.get("introduced_at") or "",
    ])


def _unique_labels_by_fingerprint(labels):
    seen = set()
    result = []
    for label in (labels or []):
        if not label:
            continue
        key = _merge_label_fp(label)
        if key in seen:
            continue
        seen.add(key)
        result.append(label)
    return result


def _storage_read_edge_id(written_node="", reader_node=""):
    return f"storage_read:{written_node or ''}->{reader_node or ''}"


# --- storage step predicates (graph-transfer-analyzer.js:1089-1163) ------------
_STORAGE_WRITE_TAGS = frozenset(
    ["file_write", "memory_write", "database_write", "log_write", "artifact_write"])
_STORAGE_READ_TAGS = frozenset(["file_read", "memory_read", "database_read"])


def _is_storage_write_step(step=None, profile=None):
    step = step or {}
    tags = set(step.get("security_tags") or [])
    return ("local_persistence" in (step.get("node_roles") or [])
            and _is_write_like_step(step, profile)
            and bool(tags & _STORAGE_WRITE_TAGS))


def _is_storage_read_step(step=None, profile=None):
    step = step or {}
    tags = set(step.get("security_tags") or [])
    if ("data_introduction" not in (step.get("node_roles") or [])
            or not _is_read_like_step(step, profile)
            or _is_write_like_step(step, profile)):
        return False
    if tags & _STORAGE_READ_TAGS:
        return True
    key = _infer_storage_key(profile, step)
    return bool(key and not key.endswith(":unknown"))


import re as _re


def _is_read_like_step(step=None, profile=None):
    step = step or {}
    profile = profile or {}
    if step.get("operation_type") in ("read", "review", "verify"):
        return True
    text = " ".join(str(x) for x in [
        profile.get("node_name"), step.get("operation_type"),
        *[item.get("kind") or item.get("text") or "" for item in (step.get("evidence") or [])],
    ] if x)
    return bool(_re.search(r"(?:^|[\s._-])(read|get|fetch|retrieve|load|open|query|select)(?:$|[\s._-])", text, _re.IGNORECASE))


def _is_write_like_step(step=None, profile=None):
    step = step or {}
    profile = profile or {}
    if step.get("operation_type") in ("write", "produce_artifact"):
        return True
    text = " ".join(str(x) for x in [
        profile.get("node_name"), step.get("operation_type"),
        *[item.get("kind") or item.get("text") or "" for item in (step.get("evidence") or [])],
    ] if x)
    return bool(_re.search(r"(?:^|[\s._-])(write|save|store|persist|append|insert|update)(?:$|[\s._-])", text, _re.IGNORECASE))


# Port of inferStorageKey (graph-transfer-analyzer.js:1104-1120)
def _infer_storage_key(profile=None, step=None):
    profile = profile or {}
    tags = set([*(profile.get("security_tags") or []), *((step or {}).get("security_tags") or [])])
    labels = (profile.get("data_profile") or {}).get("labels") or []
    text = " ".join(str(x) for x in [
        profile.get("node_name"),
        (step or {}).get("operation_type"),
        *[f"{t.get('type') or ''}:{t.get('value') or ''}:{t.get('raw') or ''}"
          for t in ((step or {}).get("targets") or [])],
        *[item.get("text") or "" for item in ((step or {}).get("evidence") or [])],
        *[item.get("text") or "" for item in (profile.get("evidence") or [])],
        *[" ".join(p for p in [lb.get("field_name"), lb.get("field_path"), lb.get("evidence_text")] if p)
          for lb in labels],
    ] if x)
    lower = text.lower()
    if "memory_write" in tags or "memory_read" in tags or _re.search(r"\b(memory|session|state)\b", lower, _re.IGNORECASE):
        surface = "memory_store"
    elif "database_write" in tags or "database_read" in tags or _re.search(r"\b(database|db|sql|table|collection)\b", lower, _re.IGNORECASE):
        surface = "database"
    else:
        surface = "local_file"
    key = _extract_storage_object_name(text, surface) or "unknown"
    return f"{surface}:{key}"


def _extract_storage_object_name(text, surface):
    normalized = str(text or "").replace("\\", "/")
    ext = r"(?:md|txt|json|yaml|yml|csv|log|html|xml|pdf|docx?|xlsx?|py|js|ts|zip)"
    m = _re.search(r"(?:^|[\s/_.-])(?:read|write|save|append|store|persist|load|open)[_.-]([A-Za-z0-9_.-]+\." + ext + r")", normalized, _re.IGNORECASE)
    if m:
        return m.group(1).lower()
    m = _re.search(r"([A-Za-z0-9_.-]+\." + ext + r")", normalized, _re.IGNORECASE)
    if m:
        return m.group(1).lower()
    m = _re.search(r"(?:read|write|save|append|store|persist|load|open|insert|query|update)[_.-]([A-Za-z0-9_.-]+)", normalized, _re.IGNORECASE)
    if m:
        return m.group(1).lower()
    if surface == "database":
        m = _re.search(r"(?:table|collection|database|db|sql)[\s:._-]+([A-Za-z0-9_-]+)", normalized, _re.IGNORECASE)
        if m:
            return m.group(1).lower()
    if surface == "memory_store":
        m = _re.search(r"(?:memory|session|state)[\s:._-]+([A-Za-z0-9_-]+)", normalized, _re.IGNORECASE)
        if m:
            return m.group(1).lower()
    return ""


# --- merge relationships (graph-transfer-analyzer.js:873-908) ------------------
# Port of maybeCreateMergeRelationships (graph-transfer-analyzer.js:873-908).
# Relates co-located non-terminated flows at an explicit merge_join node WITHOUT
# merging their labels (they stay distinct flows; only merge_group / related ids
# link them).
def _maybe_create_merge_relationships(flow, state, profiles_by_node):
    profile = profiles_by_node.get(flow.current_node)
    if not profile or "merge_join" not in (profile.get("operation_tags") or []):
        return
    peers = [p for p in (state.label_flows_by_node.get(flow.current_node) or [])
             if not p.terminated][:state.options["maxMergeParents"]]
    if len(peers) < 2:
        return
    signature = f"{profile.get('node_id')}|merge_join"
    event = next((e for e in state.merge_events
                  if e.get("type") == "merge_join" and e.get("node_id") == profile.get("node_id")), None)
    if not event:
        if signature in state.merge_signatures:
            return
        state.merge_signatures.add(signature)
        event = {
            "event_id": state.next_id("merge", "merge"),
            "type": "merge_join",
            "node_id": profile.get("node_id"),
            "node_name": profile.get("node_name"),
            "label_flow_ids": [],
            "label_flow_id_count": 0,
            "labels": [],
            "evidence": "explicit merge_join operation relates co-located label flows without merging labels",
        }
        state.merge_events.append(event)
        state.all_events.append(event)
    _update_merge_event_members(event, peers)
    for peer in peers:
        peer.merge_group_ids = _append_ids(peer.merge_group_ids or [], [event["event_id"]])


# --- output builders (graph-transfer-analyzer.js:1585-1643) --------------------
def _build_node_flow_sets(label_flows):
    import functools
    from ..util.locale import locale_compare
    by_node = {}
    for flow in (label_flows or []):
        if not flow.current_node:
            continue
        item = by_node.setdefault(flow.current_node, {
            "node_id": flow.current_node,
            "node_name": flow.current_node_name or flow.current_node,
            "label_flow_ids": [], "labels": [],
        })
        item["label_flow_ids"].append(flow.label_flow_id)
        item["labels"].append((flow.label or {}).get("label") or "")

    def _lc_sort(vals):
        # JS buildNodeFlowSets sorts label_flow_ids / labels with a PLAIN .sort()
        # (graph-transfer-analyzer.js:1604-1605) — code-unit order, not
        # localeCompare (only the outer node_id sort uses localeCompare, :1606).
        return sorted(_unique_values(vals))

    result = [{
        "node_id": item["node_id"],
        "node_name": item["node_name"],
        "label_flow_ids": _lc_sort(item["label_flow_ids"]),
        "labels": _lc_sort(item["labels"]),
    } for item in by_node.values()]
    result.sort(key=functools.cmp_to_key(lambda a, b: locale_compare(a["node_id"], b["node_id"])))
    return result


def _build_flow_states(state):
    import functools
    from ..util.locale import locale_compare
    result = [{
        "state_id": item["state_id"],
        "representative_label_flow_id": item["representative_label_flow_id"],
        "node_id": item["node_id"],
        "node_name": item["node_name"],
        "label": compact_label(item["label"]),
        "availability": item["availability"],
        "storage_key": item["storage_key"],
        "phase": item["phase"],
        "origin_ids": item.get("origin_ids") or [],
        "provenance_event_ids": item.get("provenance_event_ids") or [],
        "label_flow_ids": item.get("label_flow_ids") or [],
        "label_flow_id_count": item.get("label_flow_id_count") or 0,
        "merged_path_count": item.get("merged_path_count") or 0,
        "confidence_min": item["confidence_min"],
        "confidence_max": item["confidence_max"],
        "reached_observation_ids": item.get("reached_observation_ids") or [],
        # design-B decision-unit fields
        "transform_sig": item.get("transform_sig") or "none",
        "transform_digest": item.get("transform_digest") or [],
        # Carry the CONSERVATIVE-AND reduction flag the analyzer maintains
        # (_create_flow_state seed + _merge_flow_into_representative AND). This
        # projection MUST forward it: public._compact_public_flow_state reads it
        # verbatim (it deliberately does NOT re-derive from the single
        # representative transform_digest), and DOE reads flow_state.reduction_applied
        # for the receiver_semantic_need +0.2 bonus. Dropping it here forced every
        # state to False downstream (re-introducing the word-bag false floor).
        "reduction_applied": bool(item.get("reduction_applied")),
        # reduction antichain (the maximal reductions this bucket applied). Now a
        # dedup-key component, so homogeneous per bucket; forwarded verbatim.
        "reduction_profile": item.get("reduction_profile") or [],
        "word_set": item.get("word_set") or [],
        "origin_node": item.get("origin_node") or "",
        "origin_boundary": item.get("origin_boundary"),
    } for item in state.flow_states.values()]
    result.sort(key=functools.cmp_to_key(lambda a, b: locale_compare(a["state_id"], b["state_id"])))
    return result


def _build_provenance_store(state):
    import functools
    from ..util.locale import locale_compare
    origins = list(state.origins.values())
    origins.sort(key=functools.cmp_to_key(lambda a, b: locale_compare(a["origin_id"], b["origin_id"])))
    # v6: path_classes / representative_paths dropped (path-derived).
    return {
        "origins": origins,
        "path_classes": [],
        "representative_paths": [],
        "statistics": {
            "origin_count": len(state.origins),
            "path_class_count": 0,
            "representative_path_count": 0,
        },
    }


def _build_statistics(state, options):
    terminated = sum(1 for f in state.label_flows if f.terminated)
    periodic_events = [e for e in state.observation_events if e.get("leak_type") == "periodic"]
    collapsed = sum(1 for f in state.label_flows if f.cycle_handling == "collapse")
    return {
        "label_flow_count": len(state.label_flows),
        "transition_count": len(state.transitions),
        "route_event_count": len(state.route_events),
        "filter_event_count": len(state.filter_events),
        "merge_event_count": len(state.merge_events),
        "source_introduction_count": len(state.source_introductions),
        "truncation_event_count": len(state.truncation_events),
        "terminated_label_flow_count": terminated,
        "active_label_flow_count": len(state.label_flows) - terminated,
        "periodic_leak_count": len(periodic_events),
        "periodic_leak_severity": {
            "steady": sum(1 for e in periodic_events if e.get("leak_severity") == "steady"),
            "amplifying": sum(1 for e in periodic_events if e.get("leak_severity") == "amplifying"),
            "mutating": sum(1 for e in periodic_events if e.get("leak_severity") == "mutating"),
        },
        "collapsed_flow_count": collapsed,
        "cycle_closure_count": state.cycle_closure_count,
        "flow_state_count": len(state.flow_states),
        "truncated": state.truncated,
        "limits": options,
    }
