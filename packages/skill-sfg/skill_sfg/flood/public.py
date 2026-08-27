"""v6 public output assembler (path-free port of transfer-analysis.js).

Produces ``security_profile`` with ``version: '6.0'``. The v5.1 output duplicated
node_path / node_names / edge_path / filter_events on every flow — the JSON
analogue of the memory wall. v6 emits only what DOE reads:

  * label_flows — path-free minimal (single parent, current_node, incoming_edge_id,
    origin_node, local_filter_event_ids, flow_state_id, label_ref, flow_mode,
    confidence, termination/cycle flags). node_path / edge_path / route_history /
    full filter_events are DROPPED — DOE rebuilds paths from the parent chain.
  * flow_states — the authoritative decision-unit table, enriched with
    transform_sig / transform_digest / word_set / origin_node / origin_boundary.
  * observations — carry the M3 judgment summary so DOE scores task_need /
    reduction without re-walking flows.
  * provenance_graph.events.filtering — KEPT (load-bearing: DOE resolves
    local_filter_event_ids → transform type via this flat list).

This is intentionally a NEW contract (v6), not byte-compatible with v5.1, since
DOE is being rewritten to consume it.
"""

from .analyzer import analyze_graph_transfers
from .observations import build_observations
from .constants import REAL_TRANSFORM_TYPES


def build_transfer_security_profile_v6(nodes=None, edges=None, node_profiles=None,
                                       edges_for_transfer=None, limits=None,
                                       label_assist_stats=None):
    """Assemble the v6 security_profile from node profiles + the flood result.

    ``edges_for_transfer`` mirrors the JS split (cycle-expanded edges for
    propagation); falls back to ``edges``.
    """
    nodes = nodes or []
    edges = edges or []
    node_profiles = node_profiles or []
    flood_edges = edges_for_transfer if edges_for_transfer is not None else edges

    transfer = analyze_graph_transfers(
        nodes=nodes, edges=flood_edges, node_profiles=node_profiles, limits=limits)

    states_by_flow_id = {f.label_flow_id: f for f in transfer["label_flows"]}
    observation_result = build_observations(
        node_profiles=node_profiles,
        label_flows=transfer["label_flows"],
        observation_events=transfer["observation_events"],
        states_by_flow_id=states_by_flow_id,
    )

    provenance_graph, kept_filter_ids = _build_provenance_graph_v6(transfer)

    label_dictionary = _LabelDictionary()
    public_label_flows = [
        _compact_public_label_flow(flow, label_dictionary, kept_filter_ids)
        for flow in transfer["label_flows"]
    ]
    public_flow_states = [
        _compact_public_flow_state(state, label_dictionary)
        for state in transfer["flow_states"]
    ]

    stats = {
        "node_profile_count": len(node_profiles),
        "label_flow_count": len(transfer["label_flows"]),
        "label_dictionary_count": label_dictionary.size,
        "flow_state_count": len(transfer["flow_states"]),
        "node_flow_set_count": len(transfer["node_flow_sets"]),
        "transition_count": len(transfer["transitions"]),
        "observation_count": len(observation_result["observations"]),
        "observation_event_count": len(transfer["observation_events"]),
        "sink_like_observation_count": len(observation_result["observations"]),
        "truncated": transfer["truncated"],
    }
    stats.update(transfer["statistics"])
    if label_assist_stats:
        stats.update(label_assist_stats)

    # node_flow_sets dropped from the public profile: zero consumers repo-wide.
    # Its count is retained in statistics for parity/observability.
    return {
        "version": "6.0",
        "node_profiles": node_profiles,
        "label_dictionary": label_dictionary.to_object(),
        "label_flows": public_label_flows,
        "flow_states": public_flow_states,
        "provenance_graph": provenance_graph,
        "observations": observation_result["observations"],
        "statistics": stats,
    }


# --- label dictionary (transfer-analysis.js:552-578) ---------------------------
class _LabelDictionary:
    def __init__(self):
        self._by_id = {}

    def register(self, compacted):
        """Return {'label_id': id} when dictionaried, else {'label': compacted}
        (missing id → inline, lossless). Never both."""
        if not compacted:
            return {"label": None}
        id_ = compacted.get("id") or ""
        if not id_:
            return {"label": compacted}
        if id_ not in self._by_id:
            self._by_id[id_] = compacted
        return {"label_id": id_}

    def to_object(self):
        return dict(self._by_id)

    @property
    def size(self):
        return len(self._by_id)


# Port of compactPublicLabel (transfer-analysis.js:517-541)
def _compact_public_label(label=None):
    if not label:
        return None
    return {
        "id": label.get("id") or "",
        "label": label.get("label") or "",
        "category": label.get("category") or "",
        "subtype": label.get("subtype") or "",
        "sensitivity": label.get("sensitivity") or "",
        "field_name": label.get("field_name") or "",
        "field_path": label.get("field_path") or "",
        "origin_node": label.get("origin_node") or "",
        "origin_node_name": label.get("origin_node_name") or "",
        "introduced_at": label.get("introduced_at") or "",
        "mode": label.get("mode") or "",
        "confidence": label.get("confidence"),
        "evidence_level": label.get("evidence_level") or "",
        "evidence_kind": label.get("evidence_kind") or "",
        "evidence_text": label.get("evidence_text") or "",
        "ontology_version": label.get("ontology_version") or "",
        "ontology_label_id": label.get("ontology_label_id") or "",
        "requires_review": bool(label.get("requires_review")),
        "uncertainty": label.get("uncertainty") or "",
        "reason": label.get("reason") or "",
    }


# Port of emitLabelRef (transfer-analysis.js:510-515)
def _emit_label_ref(raw_label, label_dictionary):
    compacted = _compact_public_label(raw_label)
    if not compacted:
        return {"label": None}
    return label_dictionary.register(compacted)


def _unique_values(values):
    out = []
    seen = set()
    for v in (values or []):
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


# v6 path-free label flow. A StateNode → the minimal DOE-read shape.
# local_filter_event_ids is filtered to kept_filter_ids (the real-transform events
# retained in provenance_graph); refs to dropped source_introduction/unknown_may_flow
# events are removed so no id dangles (DOE would `continue` past them anyway).
def _compact_public_label_flow(flow, label_dictionary, kept_filter_ids=None):
    local_ids = list(flow.local_filter_event_ids or [])
    if kept_filter_ids is not None:
        local_ids = [i for i in local_ids if i in kept_filter_ids]
    out = {
        "label_flow_id": flow.label_flow_id or "",
        "parent_label_flow_ids": _unique_values(flow.parent_label_flow_ids or []),
        "current_node": flow.current_node or "",
        "current_node_name": flow.current_node_name or "",
        "incoming_edge_id": flow.incoming_edge_id or "",
        "origin_node": flow.origin_node or "",
        "introduced_at": flow.introduced_at or "",
        "flow_mode": flow.flow_mode or "may_flow",
        "confidence": flow.confidence or 0.3,
        "local_filter_event_ids": local_ids,
        "flow_state_id": flow.flow_state_id or "",
        "storage_key": flow.storage_key or "",
        "merge_group_ids": _unique_values(flow.merge_group_ids or []),
        "terminated": bool(flow.terminated),
        "termination_reason": flow.termination_reason or "",
        "truncated": bool(flow.truncated),
        "cycle_handling": flow.cycle_handling or "",
        "label_fingerprint": flow.label_fingerprint or "",
    }
    out.update(_emit_label_ref(flow.label, label_dictionary))
    return out


# v6 enriched flow state (the decision-unit table). transfer["flow_states"] is
# already a list of dicts (from analyzer._build_flow_states); we just swap the
# inline label for a dictionary ref and keep the design-B fields.
def _compact_public_flow_state(state, label_dictionary):
    # DOE reads only 4 fields from a flow_state (necessity-baseline.js): state_id
    # (index key), transform_sig, reduction_applied, origin_boundary.trust_boundary.
    # Everything v6 used to emit besides those — provenance_event_ids / word_set /
    # label_flow_ids / origin_ids / reached_observation_ids / confidence_min/max /
    # label_flow_id_count / merged_path_count / availability / storage_key / phase —
    # had ZERO consumers repo-wide (~41% of flow_states bytes on polymarket) and is
    # dropped. node_id / node_name / representative_label_flow_id / transform_digest /
    # origin_node / label ref are kept as lightweight traceability (transform_digest
    # is the pre-image reduction_applied derives from, so a reader can audit it).
    out = {
        "state_id": state.get("state_id") or "",
        "representative_label_flow_id": state.get("representative_label_flow_id") or "",
        "node_id": state.get("node_id") or "",
        "node_name": state.get("node_name") or "",
        # design-B decision-unit fields
        "transform_sig": state.get("transform_sig") or "none",
        "transform_digest": state.get("transform_digest") or [],
        # reduction_applied: read the CONSERVATIVE-AND value the analyzer maintains
        # across every path merged into this state (seeded in _create_flow_state,
        # ANDed in _merge_flow_into_representative). It is NOT re-derived from the
        # single representative transform_digest here: after transform_sig left the
        # dedup key, a reducing and a non-reducing path can share a state, and the
        # representative keeps only one digest — deriving from it would be
        # first-arrival-dependent and could credit a reduction some merged path
        # never applied (missed exposure). DOE reads flow_state.reduction_applied
        # (necessity-baseline.js:345) for the receiver_semantic_need +0.2 bonus.
        "reduction_applied": bool(state.get("reduction_applied")),
        # reduction antichain — the maximal, mutually-incomparable reductions this
        # bucket applied before egress (reduction_applied == bool(this)). Now a
        # dedup-key component (state.build_flow_state_key), so it is homogeneous
        # across every path in the bucket — no conservative-AND blur. This is the
        # per-unit protection fact the DOE/LLM judge reads to decide WHICH kind of
        # reduction ran (not just whether any did) when assessing whether the
        # protection is sufficient to clear an egress.
        "reduction_profile": state.get("reduction_profile") or [],
        "origin_node": state.get("origin_node") or "",
        "origin_boundary": state.get("origin_boundary"),
    }
    out.update(_emit_label_ref(state.get("label"), label_dictionary))
    return out


# v6 provenance graph — keeps ONLY events.filtering (load-bearing for DOE's
# local_filter_event_ids → transform type resolution). routing/merge/observation
# event lists are available in the flood result if a future DOE reader needs
# them, but the critical join is filtering.
#
# DOE (evidence-pack.js transformsByNode) processes ONLY REAL_TRANSFORM_TYPES
# events and `continue`s past every other type. source_introduction /
# unknown_may_flow events (measured 97–100% of the list; the whole
# provenance_graph was 27–82% of the FCG file) are therefore pure ballast — each
# also embeds a full ~700B label object DOE never reads. We keep only the real-
# transform events and return their id set so label_flows can drop dangling
# local_filter_event_ids refs to the removed events.
def _build_provenance_graph_v6(transfer):
    all_events = transfer["filter_events"] or []
    real_events = [ev for ev in all_events if ev.get("type") in REAL_TRANSFORM_TYPES]
    kept = [_compact_public_filter_event(ev) for ev in real_events]
    kept_ids = {e["event_id"] for e in kept if e.get("event_id")}
    graph = {
        "events": {"filtering": kept},
        "statistics": {
            "filter_event_count": len(kept),
            "filter_event_total": len(all_events),
            "filter_event_dropped_nonreal": len(all_events) - len(kept),
        },
    }
    return graph, kept_ids


# The filter event fields DOE reads to resolve a transform (evidence-pack.js
# summarizeTransform reads type / from_label / dropped_label / context_label /
# kept_label / introduced_label). We keep those + id/node.
def _compact_public_filter_event(event=None):
    event = event or {}
    out = {
        "event_id": event.get("event_id") or "",
        "type": event.get("type") or "",
        "node_id": event.get("node_id") or "",
        "node_name": event.get("node_name") or "",
    }
    for key in ("from_label", "dropped_label", "context_label", "kept_label",
                "introduced_label", "propagated_label", "storage_key"):
        if event.get(key) is not None:
            out[key] = event.get(key)
    return out
