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

from skill_sfg.flood.filter import apply_label_flow_filter
from skill_sfg.flood.state import label_fingerprint

_HERE = os.path.dirname(__file__)
# Frozen JS oracle (see golden/README.md). These 3 hashes are the PERMANENT
# reference for the FCG↔DOE join key: data-labeler.js dies with the analyzer,
# so this golden is the only surviving witness that Python's JSON/hash matches
# Node's byte-for-byte, including non-ASCII (café / 中文).
with open(os.path.join(_HERE, "golden", "flood_filter.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)


def test_filter_event_id_matches_node_ascii():
    res = apply_label_flow_filter(
        label_flow={"label": {"id": "L1", "label": "pii.email", "category": "pii",
                              "subtype": "email", "confidence": 0.9, "origin_node": "n0"},
                    "label_flow_id": "lf_1", "flow_mode": "may_flow"},
        current_profile={"node_id": "n1", "node_name": "Node One", "operation_tags": []},
        edge={"type": "data_flow"})
    ev = res["filter_events"][0]
    assert ev["event_id"] == _GOLDEN["event_id_ascii"]


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
    assert ev["event_id"] == _GOLDEN["event_id_non_ascii"]


def test_label_fingerprint_matches_node():
    py_fp = label_fingerprint(
        {"label": "pii.email", "origin_node": "n0", "introduced_at": "n0", "evidence_kind": "field"})
    assert py_fp == _GOLDEN["label_fingerprint"]
