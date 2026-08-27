"""M3-i memory probe — the core 'eradication' proof.

The JS memory wall was createChildLabelFlow spread-copying five O(depth) arrays
per child, so peak heap grew with path depth. The design-B StateNode keeps a
single parent pointer + O(#real-transforms) summary, so peak heap must stay ~flat
as depth grows.

We flood a linear chain of N pass-through nodes (one source, N-2 relays, one
egress sink) at increasing lengths and measure tracemalloc peak. If the wall were
still present, peak would scale ~linearly with N (each of the N flows holds arrays
of length up to N → O(N^2) total). With the fix it is ~O(N) (N flows, each O(1) in
path length), and crucially the PER-FLOW footprint is depth-independent.

tracemalloc.peak is the metric (deterministic, cross-platform; win32 has no
ru_maxrss). We assert per-flow peak does not grow with chain length.
"""

import tracemalloc

from skill_sfg.flood.analyzer import analyze_graph_transfers


def _linear_chain(n):
    """A source → (n-2 relays) → egress sink chain. Every relay is a plain
    pass-through (no transform, no sink role) so the single seed flow walks the
    full length, maximizing path depth."""
    node_profiles = []
    nodes = []
    edges = []
    for i in range(n):
        nid = f"n{i:04d}"
        nodes.append({"id": nid})
        if i == 0:
            node_profiles.append({
                "node_id": nid, "node_name": f"Source {i}",
                "node_roles": ["data_introduction"], "operation_tags": [], "security_tags": [],
                "data_profile": {"labels": [{
                    "label": "pii.email", "category": "pii", "subtype": "email",
                    "origin_node": nid, "introduced_at": nid, "confidence": 0.9,
                    "mode": "raw", "evidence_level": "L3"}]},
                "data_surface": "user", "receiver_scope": "self",
                "retention_scope": "transient", "trust_boundary": "internal",
            })
        elif i == n - 1:
            node_profiles.append({
                "node_id": nid, "node_name": f"Egress {i}",
                "node_roles": ["external_egress"], "operation_tags": [], "security_tags": ["network"],
                "data_surface": "network", "receiver_scope": "third_party",
                "retention_scope": "external", "trust_boundary": "external",
            })
        else:
            node_profiles.append({
                "node_id": nid, "node_name": f"Relay {i}",
                "node_roles": [], "operation_tags": [], "security_tags": [],
                "data_surface": "memory", "receiver_scope": "self",
                "retention_scope": "transient", "trust_boundary": "internal",
            })
        if i > 0:
            edges.append({"id": f"e{i}", "source": f"n{i-1:04d}", "target": nid, "type": "data_flow"})
    return nodes, edges, node_profiles


def _peak_for_chain(n):
    nodes, edges, node_profiles = _linear_chain(n)
    tracemalloc.start()
    tracemalloc.clear_traces()
    result = analyze_graph_transfers(nodes=nodes, edges=edges, node_profiles=node_profiles)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    flows = len(result["label_flows"])
    return peak, flows


def test_per_flow_peak_is_depth_independent():
    """Per-flow peak heap must NOT grow with chain depth. The wall would make each
    flow hold arrays of length O(depth); the fix makes each flow O(1) in depth."""
    peak_short, flows_short = _peak_for_chain(50)
    peak_long, flows_long = _peak_for_chain(500)

    per_flow_short = peak_short / max(flows_short, 1)
    per_flow_long = peak_long / max(flows_long, 1)

    # A linear chain produces ~one flow per node, so flows scale with n. The
    # per-flow footprint is the wall-sensitive quantity: with the five arrays it
    # grows ~linearly with depth (10x here); with the fix it is ~flat.
    ratio = per_flow_long / max(per_flow_short, 1)
    # With the parent-chain acyclic guard (no per-flow ancestor set) the per-flow
    # footprint is genuinely flat — measured ~0.94x across 50→1000. A 1.25x ceiling
    # leaves headroom for allocator noise while still catching any O(depth)
    # structure creeping back in.
    assert ratio < 1.25, (
        f"per-flow peak grew {ratio:.2f}x from depth 50 to 500 "
        f"(short={per_flow_short:.0f}B/flow, long={per_flow_long:.0f}B/flow) — "
        f"an O(depth) structure appears to have crept back in")


def test_no_state_holds_depth_scaling_list():
    """Structural assertion: no StateNode carries a container whose size scales
    with hop depth. transform_digest scales with #real-transforms (0 on a
    pass-through chain); the acyclic guard walks the parent pointer, so there is
    no per-flow ancestor set at all."""
    nodes, edges, node_profiles = _linear_chain(300)
    result = analyze_graph_transfers(nodes=nodes, edges=edges, node_profiles=node_profiles)
    for flow in result["label_flows"]:
        # digest is empty on a pure pass-through chain regardless of depth
        assert len(flow.transform_digest) == 0
        # single parent pointer, never an accumulated chain array
        assert len(flow.parent_label_flow_ids) <= 1
        # local filter ids are per-hop only (1 intro or 1 unknown_may_flow)
        assert len(flow.local_filter_event_ids) <= 1
