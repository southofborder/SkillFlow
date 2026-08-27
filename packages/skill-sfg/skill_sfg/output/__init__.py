"""FCG output layer: v6 JSON envelope assembler (port of output/json-generator.js
envelope). build_fcg_json wraps a run_pipeline result into the top-level FCG JSON
DOE consumes (meta / nodes / edges / documentation_context / security_profile)."""

from .json_generator import build_fcg_json, build_node_json, build_edge_json
from .flowchart_generator import (
    generate_flowchart_artifacts,
    save_flowchart_artifacts,
    derive_flowchart_paths,
)

__all__ = [
    "build_fcg_json",
    "build_node_json",
    "build_edge_json",
    "generate_flowchart_artifacts",
    "save_flowchart_artifacts",
    "derive_flowchart_paths",
]
