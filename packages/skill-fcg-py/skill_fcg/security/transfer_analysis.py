"""Security-profile orchestrator (port of transfer-analysis.js:33-148).

Mirrors buildTransferSecurityProfile: split the edge set into the acyclic
`edges_active` (role inference + label propagation must not see re-admitted
feedback edges) vs `edges_for_transfer` (keeps plausible real cycles when
cycle_expand is on), build node profiles on the active set, then hand off to the
v6 flood assembler (flood/public.py).

RULE-ONLY: this targets the deterministic, network-free path (build_node_profiles,
not the label-LLM-assist async variant). That matches the M4 verdict-equivalence
oracle, which runs both engines with LLM disabled.
"""

from ..analyzer.cycle_remover import is_feedback_edge
from ..flood.public import build_transfer_security_profile_v6
from .node_profiler import build_node_profiles


# Port of activeEdges (transfer-analysis.js:33-35): strip ALL feedback edges.
def active_edges(edges=None):
    return [e for e in (edges or []) if not is_feedback_edge(e)]


# Port of transferEdges (transfer-analysis.js:37-41): keep plausible real cycles
# when cycle_expand is on; else identical to active_edges.
def transfer_edges(edges=None, cycle_expand=False):
    edges = edges or []
    if not cycle_expand:
        return active_edges(edges)
    return [
        e for e in edges
        if not is_feedback_edge(e) or e.get("feedback_plausibility") == "plausible"
    ]


# Port of buildTransferSecurityProfile (transfer-analysis.js:43-48) +
# buildProfileFromNodeProfiles (65-148), collapsed for the rule-only path.
def build_transfer_security_profile(nodes=None, edges=None, cycle_expand=False,
                                    limits=None):
    nodes = nodes or []
    edges = edges or []
    edges_active = active_edges(edges)
    edges_for_transfer = transfer_edges(edges, cycle_expand)
    node_profiles = build_node_profiles(nodes, edges_active)
    return build_transfer_security_profile_v6(
        nodes=nodes,
        edges=edges_active,
        node_profiles=node_profiles,
        edges_for_transfer=edges_for_transfer,
        limits=limits,
    )
