"""Port of src/analyzer/feedback-edge-classifier.js.

Judges each cycle-broken feedback edge for *plausibility as a feedback edge*
(genuine self-optimizing loop vs dedup/structural artifact). A coarse recall-
biased rule pass (protected edge / touches-a-sink / confidence>=min) marks
plausible; only rule-implausible edges go to an optional LLM review that may
rescue them. Classification is advisory metadata on the edge only. nodeIsSinkLike
calls buildNodeProfile (now available). The LLM review is synchronous in the
Python port (injected reviewer + live transport are both sync); result ordering
is unchanged.
"""

import os
import re

from .cycle_remover import is_feedback_edge, is_protected_cycle_edge
from ..security.node_profiler import build_node_profile
from ..llm.transport import post_json_with_timeout
from ..llm.normalizers import parse_loose_json


DEFAULT_PLAUSIBLE_MIN_CONF = 0.3

SINK_LIKE_ROLES = {
    "external_egress",
    "model_inference",
    "local_persistence",
    "command_execution",
    "destructive_operation",
    "tool_invocation",
}


# Port of isTruthyEnv (feedback-edge-classifier.js:57-59)
def _is_truthy_env(value):
    return bool(re.match(r"^(1|true|yes|on)$", str(value or "").strip(), re.IGNORECASE))


# Port of isFalsyEnv (feedback-edge-classifier.js:61-63)
def _is_falsy_env(value):
    return bool(re.match(r"^(0|false|no|off)$", str(value or "").strip(), re.IGNORECASE))


# Port of nodeIsSinkLike (feedback-edge-classifier.js:71-82)
def node_is_sink_like(node):
    if not node:
        return False
    if node.get("category") == "Sink":
        return True
    try:
        profile = build_node_profile(node, {})
        roles = profile.get("node_roles") if isinstance(profile.get("node_roles"), list) else []
        return any(role in SINK_LIKE_ROLES for role in roles)
    except Exception:  # noqa: BLE001 — profiling is best-effort
        return False


# Port of classifyFeedbackEdgeByRule (feedback-edge-classifier.js:98-123)
def classify_feedback_edge_by_rule(edge, nodes_by_id, min_confidence):
    if is_protected_cycle_edge(edge):
        return {"plausible": True, "reason": "semantic/doc/constraint edge"}

    source_node = nodes_by_id.get(edge["source"])
    target_node = nodes_by_id.get(edge["target"])
    if node_is_sink_like(source_node) or node_is_sink_like(target_node):
        return {"plausible": True, "reason": "touches a sink node"}

    confidence = edge.get("confidence") if _is_finite(edge.get("confidence")) else 0.5
    if confidence >= min_confidence:
        return {"plausible": True, "reason": f"confidence {_to_fixed(confidence, 2)} >= {min_confidence}"}

    return {"plausible": False, "reason": "low-confidence non-sink dependency back-edge"}


# Port of buildFeedbackReviewPrompt (feedback-edge-classifier.js:129-144)
def build_feedback_review_prompt(items):
    lines = []
    for i, it in enumerate(items):
        edge = it["edge"]
        path = " -> ".join(edge["feedback_cycle_path"]) if isinstance(edge.get("feedback_cycle_path"), list) else ""
        conf = edge.get("confidence") if _is_finite(edge.get("confidence")) else "n/a"
        parts = [
            f"#{i} id={it['id']}",
            f"  edge: {it['sourceName']} -> {it['targetName']}",
            f"  type: {edge.get('type') or 'data_dependency'}, confidence: {conf}",
            f"  validation_method: {edge.get('validation_method') or 'n/a'}",
            f"  touches_sink: {_js_bool(it['touchesSink'])}",
            f"  cycle_path: {path or 'n/a'}",
        ]
        if edge.get("semantic_reason"):
            parts.append(f"  note: {str(edge['semantic_reason'])[:160]}")
        lines.append("\n".join(parts))
    body = "\n\n".join(lines)
    return f"Judge plausibility of each removed back-edge below.\n\n{body}"


# Port of parseFeedbackReviewResponse (feedback-edge-classifier.js:146-158)
def parse_feedback_review_response(raw):
    results = {}
    if not raw or not isinstance(raw, dict):
        return results
    arr = raw.get("results") if isinstance(raw.get("results"), list) else []
    for r in arr:
        if not r or r.get("id") is None:
            continue
        ip = r.get("is_plausible")
        is_plausible = ip is True or bool(re.match(r"^(true|yes|plausible)$", str(ip or ""), re.IGNORECASE))
        results[str(r["id"])] = {"is_plausible": is_plausible, "reason": r.get("reason") if isinstance(r.get("reason"), str) else ""}
    return results


# Port of reviewImplausibleWithLLM (feedback-edge-classifier.js:170-219)
def review_implausible_with_llm(items, config):
    reviewer = config.get("feedbackReviewer")
    if callable(reviewer):
        try:
            injected = reviewer(items, config)
            return parse_feedback_review_response({"results": injected})
        except Exception:  # noqa: BLE001
            return {}

    provider = config.get("provider") or "openai"
    model = config.get("model") or "gpt-5.5"
    api_key = config.get("apiKey") if config.get("apiKey") is not None else os.environ.get("LLM_API_KEY")
    timeout = config.get("timeout") if _is_finite(config.get("timeout")) else 180000
    endpoint = config.get("endpoint") or ""

    if config.get("disableLlm") or not str(api_key or "").strip() or len(items) == 0:
        return {}

    if provider == "dashscope":
        effective_endpoint = endpoint or os.environ.get("DASHSCOPE_ENDPOINT") or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    else:
        effective_endpoint = endpoint or "https://api.openai.com/v1/chat/completions"

    try:
        payload = post_json_with_timeout(effective_endpoint, {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": 'You audit removed back-edges (feedback edges) of a call graph. A feedback edge is PLAUSIBLE if it encodes a genuine self-optimizing loop (data/control flowing back into an earlier step, e.g. write then later read-back to refine, or a repeated review/promote cycle); IMPLAUSIBLE if it is only an artifact of duplicate/structural edge resolution with no real feedback meaning. Be lenient: when unsure, prefer plausible. Return strict JSON only: {"results":[{"id":"...","is_plausible":true|false,"reason":"..."}]}.'},
                {"role": "user", "content": build_feedback_review_prompt(items)},
            ],
        }, {
            "timeoutMs": timeout,
            "headers": {"Authorization": f"Bearer {api_key}"},
        })
        content = ((payload or {}).get("choices") or [{}])[0].get("message", {}).get("content")
        return parse_feedback_review_response(parse_loose_json(content))
    except Exception:  # noqa: BLE001
        return {}


# Port of classifyFeedbackEdges (feedback-edge-classifier.js:231-310)
def classify_feedback_edges(graph, config=None):
    config = config or {}
    stats = {
        "feedback_edge_count": 0,
        "rule_plausible_count": 0,
        "rule_implausible_count": 0,
        "llm_reviewed_count": 0,
        "llm_rescued_count": 0,
        "llm_fallback_count": 0,
    }
    if not graph or not isinstance(graph.edges, list):
        return stats

    feedback_edges = [e for e in graph.edges if is_feedback_edge(e)]
    stats["feedback_edge_count"] = len(feedback_edges)
    if len(feedback_edges) == 0:
        return stats

    nodes_by_id = graph.nodes if isinstance(graph.nodes, dict) else {}
    min_confidence = config.get("feedbackPlausibleMinConf") if _is_finite(config.get("feedbackPlausibleMinConf")) else DEFAULT_PLAUSIBLE_MIN_CONF

    implausible = []
    for edge in feedback_edges:
        verdict = classify_feedback_edge_by_rule(edge, nodes_by_id, min_confidence)
        edge["feedback_plausibility"] = "plausible" if verdict["plausible"] else "implausible"
        edge["feedback_plausibility_source"] = "rule"
        edge["feedback_plausibility_reason"] = verdict["reason"]
        if verdict["plausible"]:
            stats["rule_plausible_count"] += 1
        else:
            stats["rule_implausible_count"] += 1
            source_node = nodes_by_id.get(edge["source"])
            target_node = nodes_by_id.get(edge["target"])
            implausible.append({
                "id": edge.get("id") or f"{edge['source']}->{edge['target']}",
                "edge": edge,
                "sourceName": (source_node and source_node.get("name")) or edge["source"],
                "targetName": (target_node and target_node.get("name")) or edge["target"],
                "touchesSink": node_is_sink_like(source_node) or node_is_sink_like(target_node),
            })

    review_enabled = config.get("feedbackLlmReview") is not False
    if not review_enabled or len(implausible) == 0:
        return stats

    verdicts = review_implausible_with_llm(implausible, config)
    if len(verdicts) == 0:
        for it in implausible:
            it["edge"]["feedback_plausibility_source"] = "llm_fallback"
            stats["llm_fallback_count"] += 1
        return stats

    for it in implausible:
        verdict = verdicts.get(it["id"])
        if not verdict:
            it["edge"]["feedback_plausibility_source"] = "llm_fallback"
            stats["llm_fallback_count"] += 1
            continue
        stats["llm_reviewed_count"] += 1
        it["edge"]["feedback_plausibility_source"] = "llm"
        it["edge"]["feedback_plausibility_reason"] = verdict.get("reason") or it["edge"]["feedback_plausibility_reason"]
        if verdict["is_plausible"]:
            it["edge"]["feedback_plausibility"] = "plausible"
            stats["rule_implausible_count"] -= 1
            stats["rule_plausible_count"] += 1
            stats["llm_rescued_count"] += 1

    return stats


# Port of resolveFeedbackLlmReview (feedback-edge-classifier.js:318-325)
def resolve_feedback_llm_review(explicit):
    if explicit is True or explicit is False:
        return explicit
    env = os.environ.get("FCG_FEEDBACK_LLM_REVIEW")
    if env is None or env == "":
        return True
    if _is_falsy_env(env):
        return False
    if _is_truthy_env(env):
        return True
    return True


def _is_finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value and value not in (float("inf"), float("-inf"))


def _to_fixed(value, digits):
    """JS Number.toFixed(digits)."""
    return f"{float(value):.{digits}f}"


def _js_bool(value):
    return "true" if value else "false"
