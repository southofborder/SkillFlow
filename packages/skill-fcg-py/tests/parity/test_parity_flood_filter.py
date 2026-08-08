"""Cross-engine parity for the flood filter's load-bearing hashes (T-new-1, T4).

The filter's ``event_id`` (flow-instance-filter.js:412) folds a full
``JSON.stringify(event)`` into a sha1 hash. If Python's JSON serialization
diverges from Node by one byte, the id changes and the FCG↔DOE join keyed on
``local_filter_event_ids`` silently breaks. These tests run the REAL JS
data-labeler shortHash against the Python-built event and assert identical ids,
including non-ASCII payloads (café / 中文) where Node's raw-Unicode output and
Python's ``ensure_ascii=False`` must agree.
"""

import json
import os
import subprocess
import tempfile

import pytest

from skill_fcg.flood.filter import apply_label_flow_filter
from skill_fcg.flood.state import label_fingerprint

_DATA_LABELER = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "skill-fcg-analyzer", "src", "security", "data-labeler.js"))


def _node_available():
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        return os.path.exists(_DATA_LABELER)
    except Exception:
        return False


requires_node = pytest.mark.skipif(
    not _node_available(), reason="node or JS data-labeler.js unavailable")


def _js_event_id(event_without_id):
    """Compute filter_${shortHash([type,node_id,JSON.stringify(event)].join('|'))}
    using the REAL JS shortHash."""
    d = tempfile.mkdtemp(prefix="flood_parity_")
    evj = os.path.join(d, "ev.json")
    with open(evj, "w", encoding="utf-8") as fh:
        json.dump(event_without_id, fh)
    cjs = os.path.join(d, "h.cjs")
    with open(cjs, "w", encoding="utf-8") as fh:
        fh.write(
            "const fs=require('fs');const {shortHash}=require(process.argv[2]);"
            "const ev=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));"
            "const id='filter_'+shortHash([ev.type,ev.node_id,JSON.stringify(ev)].join('|'));"
            "fs.writeFileSync(process.argv[4],id,'utf8');")
    out = os.path.join(d, "id.txt")
    subprocess.run(["node", cjs, _DATA_LABELER, evj, out], check=True)
    with open(out, encoding="utf-8") as fh:
        return fh.read().strip()


@requires_node
def test_filter_event_id_matches_node_ascii():
    res = apply_label_flow_filter(
        label_flow={"label": {"id": "L1", "label": "pii.email", "category": "pii",
                              "subtype": "email", "confidence": 0.9, "origin_node": "n0"},
                    "label_flow_id": "lf_1", "flow_mode": "may_flow"},
        current_profile={"node_id": "n1", "node_name": "Node One", "operation_tags": []},
        edge={"type": "data_flow"})
    ev = res["filter_events"][0]
    event_wo = {k: v for k, v in ev.items() if k != "event_id"}
    assert ev["event_id"] == _js_event_id(event_wo)


@requires_node
def test_filter_event_id_matches_node_non_ascii():
    res = apply_label_flow_filter(
        label_flow={"label": {"id": "L1", "label": "pii.email", "category": "pii",
                              "subtype": "email", "confidence": 0.9, "origin_node": "n0",
                              "evidence_text": "用户邮箱 café"},
                    "label_flow_id": "lf_1", "flow_mode": "may_flow"},
        current_profile={"node_id": "n1", "node_name": "Node 中文", "operation_tags": [],
                         "security_tags": ["pii"], "evidence": [{"text": "handles email 中文"}]},
        edge={"type": "data_flow", "semantic_reason": "pass data",
              "data_flow": {"from_param": "x", "to_param": "y"}})
    ev = res["filter_events"][0]
    event_wo = {k: v for k, v in ev.items() if k != "event_id"}
    assert ev["event_id"] == _js_event_id(event_wo)


@requires_node
def test_label_fingerprint_matches_node():
    d = tempfile.mkdtemp(prefix="flood_fp_")
    cjs = os.path.join(d, "fp.cjs")
    with open(cjs, "w", encoding="utf-8") as fh:
        fh.write(
            "const {shortHash}=require(process.argv[2]);"
            "const l={label:'pii.email',origin_node:'n0',introduced_at:'n0',evidence_kind:'field'};"
            "const fp=`label_${shortHash(`${l.label}:${l.origin_node}:${l.introduced_at}:${l.evidence_kind || ''}`)}`;"
            "require('fs').writeFileSync(process.argv[3],fp,'utf8');")
    out = os.path.join(d, "o.txt")
    subprocess.run(["node", cjs, _DATA_LABELER, out], check=True)
    with open(out, encoding="utf-8") as fh:
        js_fp = fh.read().strip()
    py_fp = label_fingerprint(
        {"label": "pii.email", "origin_node": "n0", "introduced_at": "n0", "evidence_kind": "field"})
    assert py_fp == js_fp
