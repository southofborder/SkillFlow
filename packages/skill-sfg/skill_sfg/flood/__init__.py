"""Flood engine (judgment-driven rewrite of graph-transfer-analyzer.js).

This package is the M3 core: it replaces the JS flood's per-child O(depth)
spread-copy of five arrays (node_path/node_names/edge_path/route_history/
filter_events) with a state-DAG where each StateNode carries a single parent
pointer plus O(#real-transforms) judgment summary (transform_digest / word_set /
origin), collapsing peak memory from O(depth) to O(small-constant) per flow.
"""

from .analyzer import analyze_graph_transfers
from .public import build_transfer_security_profile_v6
from .observations import build_observations

__all__ = [
    "analyze_graph_transfers",
    "build_transfer_security_profile_v6",
    "build_observations",
]
