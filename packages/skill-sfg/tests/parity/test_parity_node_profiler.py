"""Cross-engine parity for node_profiler.build_node_profiles (M1e-2).

Deep-compares full node profiles (roles / security_tags / operation_tags /
boundary / data_profile / action_steps / evidence) against the REAL JS
buildNodeProfiles over hand-built node fixtures that specifically exercise the
metadata-pollution guards ([[node-profiler-metadata-pollution-fix]]):

  - a doc-slug node whose structural name + serialized JSON must NOT fabricate a
    second sink action-step (node_action_text excludes the doc slug + JSON);
  - a tool node whose CODE-derived name (redactEmailAndSendWebhook) SHOULD drive
    action-step detection (node_action_text includes non-doc names);
  - a member_steps node (scoped extraction: text patterns don't re-fire);
  - egress / model / persistence / command boundary variety;
  - a multi-crossing node (two sinks) that the splitter will later break.

Skipped when Node is unavailable.
"""

import json
import os

import pytest

from skill_sfg.security.node_profiler import build_node_profiles

_HERE = os.path.dirname(__file__)
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "node_profiler.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)


_NODES = [
    # 1. user.query builtin
    {"id": "node_001", "name": "user.query", "canonical_name": "user.query", "type": "builtin_call"},
    # 2. doc slug node: name is a structural slug that must NOT be scanned for
    #    action keywords; prose says "read the email" (one read crossing). The
    #    serialized input/output JSON also must not add sink steps.
    {"id": "node_002", "name": "doc.step.skill.l5.s1.read.email",
     "canonical_name": "doc.step.skill.l5.s1.read.email", "semanticKind": "doc_step",
     "operationType": "read", "docActions": ["read"], "instructionText": "read the customer email",
     "input": {"file_path": {"type": "string"}}, "output": {"content": {"type": "string"}},
     "formal_semantics": {"operation_type": "read",
                          "evidence": {"text": "read the customer email"},
                          "targets": [{"type": "file", "value": "email"}]}},
    # 3. code-derived tool name drives detection: name mentions redact+send+webhook.
    {"id": "node_003", "name": "redactEmailAndSendWebhook", "canonical_name": "redactEmailAndSendWebhook",
     "type": "tool_call", "action": "post", "category": "Sink",
     "instructionText": "redact the email then send it to the webhook",
     "formal_semantics": {"operation_type": "external_egress",
                          "targets": [{"type": "url", "value": "https://hooks.example.com"}]}},
    # 4. member_steps node: scoped extraction — text patterns must not re-fire.
    {"id": "node_004", "name": "doc.op.skill.l10.o1.write.log",
     "canonical_name": "doc.op.skill.l10.o1.write.log", "semanticKind": "doc_operation",
     "operationType": "write", "docActions": ["write"],
     "member_steps": [
         {"instruction": "read the analysis result", "operation_type": "read", "line": 10},
         {"instruction": "write the report to the log file", "operation_type": "write", "line": 11},
     ],
     "formal_semantics": {"operation_type": "write", "targets": [{"type": "file", "value": "log.md"}]}},
    # 5. model inference node
    {"id": "node_005", "name": "llm.summarize", "canonical_name": "llm.summarize",
     "operationType": "transform", "instructionText": "summarize the conversation and send to the model",
     "formal_semantics": {"operation_type": "transform", "evidence": {"text": "summarize the conversation and send to the model"}}},
    # 6. command execution node
    {"id": "node_006", "name": "scripts.run", "canonical_name": "scripts.run",
     "semanticKind": "script_call", "operationType": "invoke_tool",
     "instructionText": "execute the shell script via subprocess",
     "formal_semantics": {"operation_type": "invoke_tool", "evidence": {"text": "execute the shell script via subprocess"}}},
    # 7. multi-crossing node: prose has BOTH a persistence write AND an egress send
    #    -> two sink steps (the splitter target). No member_steps so text_order fires.
    {"id": "node_007", "name": "multiCross", "canonical_name": "multiCross", "type": "tool_call",
     "instructionText": "save the report to a local file and then upload it to the external api",
     "formal_semantics": {"operation_type": "write",
                          "evidence": {"text": "save the report to a local file and then upload it to the external api"}}},
    # 8. destructive op
    {"id": "node_008", "name": "cleanup", "canonical_name": "cleanup", "type": "tool_call",
     "instructionText": "delete the temporary records and drop the table",
     "formal_semantics": {"operation_type": "invoke_tool", "evidence": {"text": "delete the temporary records and drop the table"}}},
]

_EDGES = [
    # Edge semantic_reason must NOT pollute node roles; only data_flow params do.
    {"source": "node_002", "target": "node_005", "type": "data_dependency",
     "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
     "semantic_reason": "email content flows to the LLM model for external upload"},
    {"source": "node_005", "target": "node_003", "type": "control_flow",
     "data_flow": {"from_param": "response", "to_param": "context", "data_type": "object"},
     "semantic_reason": "send to webhook after model"},
]


def _canon(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [_canon(v) for v in value]
    if isinstance(value, dict):
        return {k: _canon(v) for k, v in value.items()}
    return value


def test_node_profiler_parity_full():
    js = _canon(_GOLDEN)
    py = _canon(json.loads(json.dumps(build_node_profiles(_NODES, _EDGES))))
    assert len(py) == len(js)
    for i, (p, j) in enumerate(zip(py, js)):
        assert p == j, f"profile[{i}] ({_NODES[i]['name']}) diverged"


def test_metadata_pollution_guards():
    """The doc-slug node (node_002) must have exactly one read crossing and no
    fabricated egress/model step from its name or serialized JSON; the code-name
    node (node_003) must carry the egress crossing. This locks the guard even if
    the JS baseline changes."""
    profiles = {p["node_id"]: p for p in build_node_profiles(_NODES, _EDGES)}
    doc_slug = profiles["node_002"]
    sink_roles = {"external_egress", "model_inference", "local_persistence", "command_execution", "destructive_operation"}
    doc_sink_steps = [s for s in doc_slug["action_steps"] if any(r in sink_roles for r in s["node_roles"])]
    assert len(doc_sink_steps) == 0, f"doc-slug node fabricated sink steps: {doc_sink_steps}"

    code_node = profiles["node_003"]
    assert "external_egress" in code_node["node_roles"]


def test_multi_crossing_node_has_two_sinks():
    """node_007 prose has a persistence write and an egress upload -> the profiler
    should surface >1 sink crossing, which the node splitter (M1e-3) then breaks."""
    profiles = {p["node_id"]: p for p in build_node_profiles(_NODES, _EDGES)}
    multi = profiles["node_007"]
    sink_like = {"external_egress", "model_inference", "local_persistence", "command_execution", "destructive_operation", "tool_invocation"}
    crossings = [s for s in multi["action_steps"] if any(r in sink_like for r in s["node_roles"])]
    assert len(crossings) >= 2, f"expected >=2 sink crossings, got {[s['operation_type'] for s in multi['action_steps']]}"
