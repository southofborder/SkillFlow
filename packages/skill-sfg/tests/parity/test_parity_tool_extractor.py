"""Cross-engine parity: REAL JS extractToolCalls vs the Python port.

Runs both implementations on identical specs and asserts the emitted tool-node
arrays are deeply equal. This is the M1 acceptance shape (nodes-by-id parity)
in miniature — the golden corpus harness (M1 proper) generalizes it. Skipped
automatically when Node or the JS package deps are unavailable.
"""

import json
import os

import pytest

_HERE = os.path.dirname(__file__)
_SPECS = os.path.join(_HERE, "specs.json")
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "tool_extractor.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)

from skill_sfg.parser.tool_extractor import extract_tool_calls


def _run_py(specs: list) -> list:
    out = []
    for spec in specs:
        skill_data = {"content": spec.get("content"), "sections": spec.get("sections") or []}
        readme_data = {"exists": True, "content": spec["readme"]} if spec.get("readme") else None
        options = {"markdownDocs": spec["markdownDocs"]} if spec.get("markdownDocs") else None
        # JSON round-trip so Python tuples/etc. normalize to JSON types like JS.
        out.append(json.loads(json.dumps(extract_tool_calls(skill_data, readme_data, [], options))))
    return out


def test_js_python_tool_node_parity():
    with open(_SPECS, "r", encoding="utf-8") as handle:
        specs = json.load(handle)

    js_out = _GOLDEN
    py_out = _run_py(specs)

    assert len(js_out) == len(py_out)
    for idx, (js_nodes, py_nodes) in enumerate(zip(js_out, py_out)):
        assert py_nodes == js_nodes, f"spec[{idx}] diverged:\nJS ={json.dumps(js_nodes)[:800]}\nPY ={json.dumps(py_nodes)[:800]}"
