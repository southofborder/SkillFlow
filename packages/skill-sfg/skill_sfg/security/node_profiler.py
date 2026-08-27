"""Port of src/security/node-profiler.js (sync path).

buildNodeProfile derives a node's roles, security tags, operation tags, boundary,
data_profile (via data_labeler), and the ordered action_steps that the node
splitter and observation layer consume. This is the metadata-pollution-critical
module (see [[node-profiler-metadata-pollution-fix]]): node_security_text vs
node_action_text are deliberately different — the latter excludes the node name
for doc slugs and NEVER includes serialized JSON, so action-step detection can't
fabricate sink children from metadata key words. Every regex mirrors the JS
(case-insensitive), and rounding uses JS Math.round via _js_round.

The async LLM-assist wrapper (buildNodeProfilesWithOptions) is intentionally NOT
ported here — it is off the M1e critical path (splitter/feedback classifier call
the sync buildNodeProfile). It lands with the label-llm-assistant port later.
"""

import functools
import json
import re

from .data_labeler import build_data_profile
from ..llm.normalizers import js_round


# Port of buildNodeProfiles (node-profiler.js:4-12)
def build_node_profiles(nodes=None, edges=None):
    nodes = nodes or []
    edges = edges or []
    incoming_by_node = group_edges(edges, "target")
    outgoing_by_node = group_edges(edges, "source")
    return [
        build_node_profile(node, {
            "incomingEdges": incoming_by_node.get(node.get("id")) or [],
            "outgoingEdges": outgoing_by_node.get(node.get("id")) or [],
        })
        for node in nodes
    ]


# Port of buildNodeProfilesWithOptions (node-profiler.js:14-28). The JS async
# worker-pool is collapsed to a sequential pass inside
# apply_llm_label_assist_to_profiles (see that module's docstring). Returns
# {"profiles", "statistics"}; when labelLlmAssist is falsy the assist step returns
# the profiles unchanged with zeroed stats, so the sync path stays byte-identical.
def build_node_profiles_with_options(nodes=None, edges=None, options=None):
    from .label_llm_assistant import apply_llm_label_assist_to_profiles
    nodes = nodes or []
    edges = edges or []
    options = options or {}
    profiles = build_node_profiles(nodes, edges)
    return apply_llm_label_assist_to_profiles(profiles, nodes, edges, {
        "enabled": bool(options.get("labelLlmAssist")),
        "provider": options.get("llmProvider"),
        "model": options.get("llmModel"),
        "apiKey": options.get("llmApiKey"),
        "endpoint": options.get("llmEndpoint"),
        "timeout": options.get("llmTimeout"),
        "concurrency": options.get("labelLlmConcurrency"),
        "cachePath": options.get("labelLlmCache"),
        "labelAssistant": options.get("labelAssistant"),
    })


# Port of buildNodeProfile (node-profiler.js:30-193)
def build_node_profile(node=None, context=None):
    node = node or {}
    context = context or {}
    evidence = []
    roles = set()
    security_tags = set()
    operation_tags = set()
    display_name = node_display_name(node)
    text = node_security_text(node, context)
    lower = text.lower()
    action_text = node_action_text(node)
    fs = node.get("formal_semantics") or {}
    op = str(fs.get("operation_type") or node.get("operationType") or "").lower()
    doc_actions = set(node.get("docActions") or ([node["docAction"]] if node.get("docAction") else []))

    if is_user_query(node):
        roles.add("data_introduction")
        roles.add("control_context")
        security_tags.add("user_input")
        add_evidence(evidence, "builtin_user_query", "user.query introduces the task prompt and controls activation", 0.95)

    if op == "trigger" or node.get("semanticKind") == "trigger" or re.match(r"^rule\.trigger\.", display_name or "", re.IGNORECASE):
        roles.add("control_context")
        security_tags.add("user_input")
        add_evidence(evidence, "formal_semantics.trigger", "trigger/control context", 0.85)

    if op in ("condition", "decision", "guard") or node.get("semanticKind") == "policy":
        roles.add("decision")
        if op == "guard":
            operation_tags.add("policy_guard")
        if op in ("decision", "condition"):
            operation_tags.add("routing_decision")
        add_evidence(evidence, "formal_semantics.decision", f"operation_type={op or node.get('semanticKind')}", 0.8)

    if op == "read" or "read" in doc_actions or read_pattern(lower):
        roles.add("data_introduction")
        security_tags.add("tool_response")
        add_evidence(evidence, "read_pattern", op or display_name or "read", 0.75)

    if op == "produce_artifact":
        roles.add("data_introduction")
        security_tags.add("artifact_generated")
        add_evidence(evidence, "formal_semantics.produce_artifact", "operation_type=produce_artifact emits generated data", 0.78)

    if op == "transform" or transform_pattern(lower):
        roles.add("transform")
        add_evidence(evidence, "transform_pattern", op or display_name or "transform", 0.75)

    if is_llm_consuming_transform(lower, op):
        roles.add("transform")
        roles.add("model_inference")
        security_tags.add("model_context")
        add_evidence(evidence, "llm_consuming_transform", display_name or text, 0.78)

    if op == "invoke_tool":
        roles.add("tool_invocation")
        add_evidence(evidence, "formal_semantics.invoke_tool", "operation_type=invoke_tool", 0.85)

    if is_model_node(lower):
        roles.add("model_inference")
        security_tags.add("model_context")
        add_evidence(evidence, "model_pattern", display_name or "model inference", 0.9)

    if external_egress_pattern(lower):
        roles.add("external_egress")
        roles.add("tool_invocation")
        security_tags.add("network_egress")
        add_evidence(evidence, "external_egress_pattern", display_name or text, 0.85)

    if local_persistence_pattern(lower) or op == "write" or op == "produce_artifact" or "write" in doc_actions:
        roles.add("local_persistence")
        add_evidence(evidence, "persistence_pattern", op or display_name or "write", 0.75)

    if command_pattern(lower):
        roles.add("command_execution")
        roles.add("tool_invocation")
        security_tags.add("shell_exec")
        add_evidence(evidence, "command_pattern", display_name or text, 0.9)

    if destructive_pattern(lower):
        roles.add("destructive_operation")
        add_evidence(evidence, "destructive_pattern", display_name or text, 0.85)

    if node.get("category") == "Sink" and not has_sink_like_role(roles):
        roles.add("tool_invocation")
        if external_egress_pattern(str(display_name or "").lower()) or re.search(r"\bapi\b", str(display_name or ""), re.IGNORECASE):
            roles.add("external_egress")
            security_tags.add("network_egress")
        add_evidence(evidence, "legacy_sink_category", "legacy graph category=Sink", 0.65)

    add_security_surface_tags(security_tags, lower)
    add_operation_tags(operation_tags, lower, op)

    if len(roles) == 0:
        roles.add("transform")
        add_evidence(evidence, "fallback_role", "default transform/intermediate node", 0.35)

    boundary = infer_boundary({
        "roles": roles,
        "securityTags": security_tags,
        "operationTags": operation_tags,
        "text": lower,
        "node": node,
    })

    if "data_introduction" in roles:
        data_profile = build_data_profile(node, {
            "node_id": node.get("id"),
            "node_name": display_name or node.get("id") or "",
            "data_type": profile_data_type(node),
            "reason": " ".join(item["text"] for item in evidence),
        })
    else:
        data_profile = {"primary_category": "none", "sensitivity": "low", "labels": [], "alternatives": [], "unknown_tail": False}

    action_plan = build_action_plan(node, {
        "roles": roles,
        "securityTags": security_tags,
        "operationTags": operation_tags,
        "text": text,
        "actionText": action_text,
        "lower": lower,
        "op": op,
        "docActions": doc_actions,
        "evidence": evidence,
    })

    ev = fs.get("evidence") or {}
    return {
        "node_id": node.get("id") or "",
        "node_name": display_name or node.get("id") or "",
        "node_roles": sorted(roles),
        "security_tags": sorted(security_tags),
        "operation_tags": sorted(operation_tags),
        "data_surface": boundary["data_surface"],
        "receiver_scope": boundary["receiver_scope"],
        "retention_scope": boundary["retention_scope"],
        "trust_boundary": boundary["trust_boundary"],
        "data_profile": data_profile,
        "action_steps": action_plan["action_steps"],
        "action_order_confidence": action_plan["action_order_confidence"],
        "action_order_source": action_plan["action_order_source"],
        "has_multi_action": action_plan["has_multi_action"],
        "ambiguous_action_order": action_plan["ambiguous_action_order"],
        "produced_object_key": str(ev.get("produced_object_key") or ""),
        "produced_object_text": str(ev.get("produced_object_text") or ""),
        "consumed_object_key": str(ev.get("consumed_object_key") or ""),
        "consumed_object_text": str(ev.get("consumed_object_text") or ""),
        "conditions": normalize_profile_conditions(fs.get("conditions")),
        "confidence": confidence_from_evidence(evidence),
        "evidence": sorted(evidence, key=functools.cmp_to_key(lambda a, b: _cmp_conf(b, a))),
    }


def _cmp_conf(a, b):
    # JS sort((a,b)=>b.confidence-a.confidence): descending by confidence.
    da = _num(a.get("confidence"))
    db = _num(b.get("confidence"))
    if da == db:
        return 0
    return -1 if da < db else 1


# Port of normalizeProfileConditions (node-profiler.js:196-204)
def normalize_profile_conditions(conditions):
    if not isinstance(conditions, list):
        return []
    out = []
    for item in conditions:
        item = item or {}
        entry = {"type": str(item.get("type") or "condition"), "text": str(item.get("text") or "").strip()}
        if entry["text"]:
            out.append(entry)
    return out


# Port of buildActionPlan (node-profiler.js:206-226)
def build_action_plan(node=None, context=None):
    node = node or {}
    context = context or {}
    member_steps = build_member_action_steps(node, context)
    if len(member_steps) > 0:
        return finalize_action_plan(member_steps, "member_steps", 0.9, False)

    text_steps = build_text_ordered_action_steps(node, context)
    if len(text_steps) > 0:
        source = "formal_semantics" if (len(text_steps) == 1 and context.get("op")) else "text_order"
        ambiguous_text_order = source == "text_order" and len(text_steps) > 1 and steps_contain_filter_and_sink(text_steps)
        return finalize_action_plan(text_steps, source, 0.85 if source == "formal_semantics" else (0.45 if ambiguous_text_order else 0.7), ambiguous_text_order)

    doc_action_steps = build_doc_action_steps(node, context)
    if len(doc_action_steps) > 0:
        return finalize_action_plan(doc_action_steps, "doc_actions", 0.55 if len(doc_action_steps) > 1 else 0.75, len(doc_action_steps) > 1)

    heuristic_steps = build_heuristic_action_steps(node, context)
    return finalize_action_plan(heuristic_steps, "heuristic", 0.45 if len(heuristic_steps) > 1 else 0.65, len(heuristic_steps) > 1)


# Port of buildMemberActionSteps (node-profiler.js:228-261)
def build_member_action_steps(node=None, context=None):
    node = node or {}
    context = context or {}
    if not isinstance(node.get("member_steps"), list) or len(node["member_steps"]) == 0:
        return []
    steps = []
    for index, step in enumerate(node["member_steps"]):
        sfs = step.get("formal_semantics") or {}
        sev = sfs.get("evidence") or {}
        step_text = " ".join(str(p) for p in [
            step.get("instruction"), step.get("text"), step.get("source_line"),
            step.get("operation_type"), step.get("docAction"), step.get("action"),
            sev.get("text"),
        ] if p)
        operation_type = normalize_operation_type(
            sfs.get("operation_type")
            or step.get("operation_type")
            or step.get("docAction")
            or step.get("action")
            or detect_primary_operation_type(step_text)
            or context.get("op")
        )
        steps.append(create_action_step({
            "node": node,
            "operationType": operation_type,
            "text": step_text or context.get("text"),
            "order": _num(step.get("line") or step.get("sourceLine") or (index + 1)),
            "source": "member_steps",
            "confidence": max(0.65, _num(sfs.get("confidence") or step.get("confidence") or 0.9)),
            "targets": sfs.get("targets") or [],
        }))
    return sorted(steps, key=lambda s: s["order"])


# Port of buildTextOrderedActionSteps (node-profiler.js:263-304)
def build_text_ordered_action_steps(node=None, context=None):
    node = node or {}
    context = context or {}
    scan_text = str(context.get("actionText") or "")
    op = str(context.get("op") or "")
    routing_only = op in ("condition", "decision", "guard", "trigger")
    raw_mentions = filter_sink_mentions(detect_action_mentions(scan_text)) if routing_only else detect_action_mentions(scan_text)
    mentions = enrich_action_mentions(raw_mentions, context)
    if len(mentions) == 0 and context.get("op"):
        return [create_action_step({
            "node": node,
            "operationType": normalize_operation_type(context.get("op")),
            "text": scan_text,
            "order": 1,
            "source": "formal_semantics",
            "confidence": 0.85,
            "targets": (node.get("formal_semantics") or {}).get("targets") or [],
        })]
    if len(mentions) == 0:
        return []

    by_type = {}
    for mention in mentions:
        if mention["operation_type"] not in by_type:
            by_type[mention["operation_type"]] = mention
    ordered = sorted(by_type.values(), key=lambda m: m["index"])
    return [create_action_step({
        "node": node,
        "operationType": mention["operation_type"],
        "text": action_evidence_window(scan_text, mention),
        "order": index + 1,
        "source": "text_order",
        "confidence": 0.7,
        "targets": (node.get("formal_semantics") or {}).get("targets") or [],
    }) for index, mention in enumerate(ordered)]


SINK_MENTION_TYPES = {"external_egress", "model_inference", "command_execution", "destructive_operation", "write"}


# Port of filterSinkMentions (node-profiler.js:316-318)
def filter_sink_mentions(mentions=None):
    return [m for m in (mentions or []) if m["operation_type"] not in SINK_MENTION_TYPES]


# Port of enrichActionMentions (node-profiler.js:320-343)
def enrich_action_mentions(mentions=None, context=None):
    context = context or {}
    result = list(mentions or [])
    def has_type(t):
        return any(m["operation_type"] == t for m in result)
    tags = context.get("securityTags") or set()
    roles = context.get("roles") or set()
    text = str(context.get("actionText") or context.get("text") or "")
    if not has_type("external_egress") and (
        "external_egress" in roles or "webhook_post" in tags or "email_send" in tags
        or "api_call" in tags or "network_egress" in tags
        or re.search(r"send[A-Z_]?.*webhook|webhook|send[A-Z_]?.*email|api\.call", text, re.IGNORECASE)
    ):
        result.append({"operation_type": "external_egress", "index": max(0, _search(text, r"send|webhook|external|api")), "text": "external_egress"})
    if not has_type("model_inference") and "model_inference" in roles:
        result.append({"operation_type": "model_inference", "index": max(0, _search(text, r"llm|model|inference")), "text": "model_inference"})
    if not has_type("write") and "local_persistence" in roles:
        result.append({"operation_type": "write", "index": max(0, _search(text, r"write|save|store|persist|report|artifact")), "text": "write"})
    return sorted(result, key=lambda m: m["index"])


# Port of buildDocActionSteps (node-profiler.js:345-358)
def build_doc_action_steps(node=None, context=None):
    node = node or {}
    context = context or {}
    actions = list(context.get("docActions") or [])
    if len(actions) == 0:
        return []
    step_text = str(context.get("actionText") or context.get("text") or "")
    return [create_action_step({
        "node": node,
        "operationType": normalize_operation_type(action),
        "text": step_text,
        "order": index + 1,
        "source": "doc_actions",
        "confidence": 0.55 if len(actions) > 1 else 0.75,
        "targets": (node.get("formal_semantics") or {}).get("targets") or [],
    }) for index, action in enumerate(actions)]


# Port of buildHeuristicActionSteps (node-profiler.js:360-386)
def build_heuristic_action_steps(node=None, context=None):
    node = node or {}
    context = context or {}
    roles = context.get("roles") or set()
    candidates = set()
    if "data_introduction" in roles:
        candidates.add("read")
    if "control_context" in roles:
        candidates.add("trigger")
    if "decision" in roles:
        candidates.add("decision")
    if "transform" in roles:
        candidates.add("transform")
    if "local_persistence" in roles:
        candidates.add("write")
    if "external_egress" in roles:
        candidates.add("external_egress")
    if "model_inference" in roles:
        candidates.add("model_inference")
    if "command_execution" in roles:
        candidates.add("command_execution")
    if "destructive_operation" in roles:
        candidates.add("destructive_operation")
    if "tool_invocation" in roles and "external_egress" not in candidates:
        candidates.add("invoke_tool")
    if context.get("op"):
        candidates.add(normalize_operation_type(context.get("op")))

    ordered = sorted(candidates, key=functools.cmp_to_key(lambda a, b: canonical_action_order(a) - canonical_action_order(b)))
    source = ordered if len(ordered) else ["transform"]
    step_text = str(context.get("actionText") or context.get("text") or "")
    return [create_action_step({
        "node": node,
        "operationType": operation_type,
        "text": step_text,
        "order": index + 1,
        "source": "heuristic",
        "confidence": 0.45 if len(source) > 1 else 0.65,
        "targets": (node.get("formal_semantics") or {}).get("targets") or [],
    }) for index, operation_type in enumerate(source)]


# Port of createActionStep (node-profiler.js:388-418)
def create_action_step(config):
    node = config.get("node") or {}
    operation_type = config.get("operationType", "transform")
    text = config.get("text", "")
    order = config.get("order", 1)
    source = config.get("source", "heuristic")
    confidence = config.get("confidence", 0.5)
    targets = config.get("targets", [])

    normalized = normalize_operation_type(operation_type)
    roles = set()
    security_tags = set()
    operation_tags = set()
    lower = str(text or "").lower()

    apply_operation_type_to_step(normalized, roles, security_tags, operation_tags)
    apply_text_patterns_to_step(lower, roles, security_tags, operation_tags, normalized, node, source)
    if len(roles) == 0:
        roles.add("transform")

    boundary = infer_boundary({"roles": roles, "securityTags": security_tags, "operationTags": operation_tags, "text": lower, "node": node})
    order_number = _num(order) if _is_finite_num(order) else 1
    step_id = f"{node.get('id') or 'node'}:step_{str(max(1, js_round(order_number))).rjust(3, '0')}:{normalized}"
    return {
        "step_id": step_id,
        "order": order_number,
        "operation_type": normalized,
        "node_roles": sorted(roles),
        "security_tags": sorted(security_tags),
        "operation_tags": sorted(operation_tags),
        "boundary": boundary,
        "targets": targets if isinstance(targets, list) else [],
        "evidence": [{
            "kind": f"action_step.{source}",
            "text": str(text or normalized)[:240],
            "confidence": round_confidence(confidence),
        }],
        "confidence": round_confidence(confidence),
    }


# Port of applyOperationTypeToStep (node-profiler.js:420-456)
def apply_operation_type_to_step(operation_type, roles, security_tags, operation_tags):
    if operation_type == "trigger":
        roles.add("control_context")
        security_tags.add("user_input")
    elif operation_type in ("condition", "decision", "guard"):
        roles.add("decision")
        operation_tags.add("policy_guard" if operation_type == "guard" else "routing_decision")
    elif operation_type in ("read", "review", "verify"):
        roles.add("data_introduction")
        security_tags.add("tool_response")
    elif operation_type == "produce_artifact":
        roles.add("data_introduction")
        roles.add("local_persistence")
        security_tags.add("artifact_generated")
        security_tags.add("file_write")
    elif operation_type == "write":
        roles.add("local_persistence")
        security_tags.add("file_write")
    elif operation_type == "external_egress":
        roles.add("external_egress")
        roles.add("tool_invocation")
        security_tags.add("network_egress")
    elif operation_type == "model_inference":
        roles.add("model_inference")
        security_tags.add("model_context")
    elif operation_type == "invoke_tool":
        roles.add("tool_invocation")
    elif operation_type == "command_execution":
        roles.add("command_execution")
        roles.add("tool_invocation")
        security_tags.add("shell_exec")
    elif operation_type == "destructive_operation":
        roles.add("destructive_operation")
    else:
        roles.add("transform")


# Port of applyTextPatternsToStep (node-profiler.js:458-490)
def apply_text_patterns_to_step(text, roles, security_tags, operation_tags, operation_type, node=None, source=""):
    node = node or {}
    scoped = source in ("member_steps", "text_order", "doc_actions", "formal_semantics")
    if not scoped and operation_type != "write" and operation_type != "produce_artifact" and read_pattern(text):
        roles.add("data_introduction")
        security_tags.add("tool_response")
    if not scoped and operation_type != "read" and transform_pattern(text):
        roles.add("transform")
    if (operation_type == "model_inference" or not scoped) and is_model_node(text):
        roles.add("model_inference")
        security_tags.add("model_context")
    if is_llm_consuming_transform(text, operation_type):
        roles.add("transform")
        roles.add("model_inference")
        security_tags.add("model_context")
    if (operation_type == "external_egress"
            or (not scoped and external_egress_pattern(text))
            or (operation_type == "invoke_tool" and node.get("category") == "Sink" and re.search(r"\bapi\b", str(node_display_name(node) or ""), re.IGNORECASE))):
        roles.add("external_egress")
        roles.add("tool_invocation")
        security_tags.add("network_egress")
    if operation_type == "write" or operation_type == "produce_artifact" or (not scoped and local_persistence_pattern(text)):
        roles.add("local_persistence")
    if operation_type == "command_execution" or (not scoped and command_pattern(text)):
        roles.add("command_execution")
        roles.add("tool_invocation")
        security_tags.add("shell_exec")
    if operation_type == "destructive_operation" or (not scoped and destructive_pattern(text)):
        roles.add("destructive_operation")
    add_security_surface_tags(security_tags, text)
    add_operation_tags(operation_tags, text, operation_type)


# Port of finalizeActionPlan (node-profiler.js:492-503)
def finalize_action_plan(steps, source, confidence, ambiguous):
    deduped = sorted(dedupe_action_steps(steps), key=lambda s: s["order"])
    normalized = [{**step, "order": index + 1} for index, step in enumerate(deduped)]
    return {
        "action_steps": normalized,
        "action_order_confidence": round_confidence(confidence),
        "action_order_source": source,
        "has_multi_action": len(normalized) > 1,
        "ambiguous_action_order": bool(ambiguous and len(normalized) > 1),
    }


# Port of stepsContainFilterAndSink (node-profiler.js:505-515)
def steps_contain_filter_and_sink(steps=None):
    steps = steps or []
    has_filter = any(
        any(tag in ("field_slice", "semantic_extraction", "aggregation", "redaction", "pseudonymization") for tag in (step.get("operation_tags") or []))
        for step in steps
    )
    has_sink = any(any(has_sink_like_role({role}) for role in (step.get("node_roles") or [])) for step in steps)
    return has_filter and has_sink


# Port of dedupeActionSteps (node-profiler.js:517-533)
def dedupe_action_steps(steps=None):
    result = []
    seen = set()
    for step in steps or []:
        if not step:
            continue
        key = "|".join([
            step["operation_type"],
            ",".join(step.get("node_roles") or []),
            ",".join(step.get("operation_tags") or []),
            ",".join(step.get("security_tags") or []),
        ])
        if key in seen:
            continue
        seen.add(key)
        result.append(step)
    return result if result else [create_action_step({"operationType": "transform"})]


_DETECT_PATTERNS = [
    ("read", re.compile(r"\b(read|get|fetch|retrieve|search|list|find|select|query|load|scrape|open)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("transform", re.compile(r"\b(transform|extract|parse|summari[sz]e|filter|format|convert|redact|mask|sanitize|aggregate|count|hash|merge|join)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("write", re.compile(r"\b(write|save|persist|store|append|produce|create|generate|export)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("external_egress", re.compile(r"\b(webhooks?|https?|upload|email\.send|api\.call|external\.api|third[_\-\s]?party)[A-Za-z0-9_.]*|\b(?:send|posts?|publish|shares?|push)(?:ed|ing|s)?\s+(?:to|the|a|an|it|them|data|payload|request|message|report|results?|file|email|webhook|via)\b", re.IGNORECASE)),
    ("model_inference", re.compile(r"\b(llm|model|chat|completion|openai|anthropic|qwen|gpt|claude|gemini|inference)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("command_execution", re.compile(r"\b(exec|execute|shell|command|process|spawn|run_script|subprocess)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("destructive_operation", re.compile(r"\b(delete|remove|destroy|drop|truncate|wipe)[A-Za-z0-9_]*", re.IGNORECASE)),
    ("decision", re.compile(r"\b(condition|decision|route|decide|choose|branch|if|when|guard|policy|allow|deny)[A-Za-z0-9_]*", re.IGNORECASE)),
]


# Port of detectActionMentions (node-profiler.js:535-558)
def detect_action_mentions(text=""):
    mentions = []
    for operation_type, pattern in _DETECT_PATTERNS:
        for match in pattern.finditer(text):
            mentions.append({"operation_type": operation_type, "index": match.start(), "text": match.group(0)})
    return sorted(mentions, key=lambda m: m["index"])


# Port of actionEvidenceWindow (node-profiler.js:560-566)
def action_evidence_window(text="", mention=None):
    mention = mention or {}
    raw = str(text or "")
    if not raw:
        return mention.get("text") or ""
    start = max(0, _num(mention.get("index") or 0) - 80)
    end = min(len(raw), _num(mention.get("index") or 0) + len(str(mention.get("text") or "")) + 160)
    return raw[int(start):int(end)]


# Port of detectPrimaryOperationType (node-profiler.js:568-571)
def detect_primary_operation_type(text=""):
    mentions = detect_action_mentions(text)
    return mentions[0]["operation_type"] if mentions else ""


# Port of normalizeOperationType (node-profiler.js:573-581)
def normalize_operation_type(operation_type=""):
    op = str(operation_type or "").lower()
    if op == "run":
        return "command_execution"
    if op in ("send", "post", "api_call"):
        return "external_egress"
    if op in ("llm", "model"):
        return "model_inference"
    if op == "artifact":
        return "produce_artifact"
    if op in ("trigger", "condition", "decision", "read", "write", "transform", "invoke_tool", "verify", "review", "produce_artifact", "guard", "external_egress", "model_inference", "command_execution", "destructive_operation"):
        return op
    return op or "transform"


# Port of canonicalActionOrder (node-profiler.js:583-602)
def canonical_action_order(operation_type=""):
    order = {
        "trigger": 5, "condition": 10, "decision": 10, "guard": 10,
        "read": 20, "review": 20, "verify": 20, "transform": 40,
        "produce_artifact": 70, "write": 70, "model_inference": 80,
        "external_egress": 90, "invoke_tool": 95, "command_execution": 100,
        "destructive_operation": 110,
    }
    return order.get(operation_type, 50)


# Port of addSecuritySurfaceTags (node-profiler.js:604-627)
def add_security_surface_tags(tags, text):
    if re.search(r"(api[_\-\s]?key|secret|token|credential|password|private[_\-\s]?key)", text, re.IGNORECASE):
        tags.add("credential_read")
    if re.search(r"\b(env|environment|process\.env)\b", text, re.IGNORECASE):
        tags.add("env_read")
    if re.search(r"(file|document|attachment|readme|skill\.md|path|folder|directory)", text, re.IGNORECASE):
        tags.add("file_read")
    if re.search(r"(memory|mem0|vector|embedding|session|remember|recall)", text, re.IGNORECASE):
        tags.add("memory_read")
    if re.search(r"(database|db|sql|record|table|collection|row)", text, re.IGNORECASE):
        tags.add("database_read")
    if re.search(r"(browser|cookie|history|localstorage|webpage|tab)", text, re.IGNORECASE):
        tags.add("browser_read")
    if re.search(r"(http|https|url|web|network|request|fetch|scrape)", text, re.IGNORECASE):
        tags.add("network_read")
    if re.search(r"(email|mail|inbox|message)", text, re.IGNORECASE):
        tags.add("email_read")
    if re.search(r"(calendar|event|meeting|schedule)", text, re.IGNORECASE):
        tags.add("calendar_read")
    if re.search(r"(contact|address[_\-\s]?book|phone)", text, re.IGNORECASE):
        tags.add("contact_read")

    if re.search(r"(send[_\-.]?mail|send.*email|email\.send|mail\.send|smtp)", text, re.IGNORECASE):
        tags.add("email_send")
    if re.search(r"(webhook|callback)", text, re.IGNORECASE):
        tags.add("webhook_post")
    if re.search(r"(api\.call|external\.api|http[_\-.]?post|\bpost\b|\bput\b|\bupload\b|\bpublish\b|\bshare\b|\bapi\b)", text, re.IGNORECASE):
        tags.add("api_call")
    if re.search(r"(third[_\-\s]?party|external|public)", text, re.IGNORECASE):
        tags.add("third_party_service")
    if re.search(r"(write.*file|save.*file|file_write|append|(?:write|save|store|persist|create|generate|export|produce)[\s._-]*(?:artifact|report|markdown|document|file))", text, re.IGNORECASE):
        tags.add("file_write")
    if re.search(r"(write.*memory|store.*memory|save_state|remember|persist.*memory)", text, re.IGNORECASE):
        tags.add("memory_write")
    if re.search(r"(insert|update|database_write|db_write|sql.*write)", text, re.IGNORECASE):
        tags.add("database_write")
    if re.search(r"(write.*log|log_write|append.*log|audit.*write|telemetry.*write)", text, re.IGNORECASE):
        tags.add("log_write")
    if re.search(r"(produce_artifact|artifact_write|(?:write|save|store|persist|create|generate|export|produce)[\s._-]*(?:artifact|report|markdown))", text, re.IGNORECASE):
        tags.add("artifact_write")


# Port of addOperationTags (node-profiler.js:629-642)
def add_operation_tags(tags, text, op):
    if re.search(r"(extract|select|pick|only|filter|field|slice|project)", text, re.IGNORECASE):
        tags.add("field_slice")
    if re.search(r"(extract|parse|derive|detect|identify).*(api[_\-\s]?key|secret|token|credential|email|phone|address|pii)|from[_\-\s]?prompt", text, re.IGNORECASE):
        tags.add("semantic_extraction")
    if re.search(r"(summari[sz]e|summary|digest|brief)", text, re.IGNORECASE):
        tags.add("summarization")
    if re.search(r"(aggregate|count|average|total|histogram)\b|statistics\b", text, re.IGNORECASE):
        tags.add("aggregation")
    if re.search(r"(redact|mask|sanitize|scrub|strip|remove.*secret|remove.*pii)", text, re.IGNORECASE):
        tags.add("redaction")
    if re.search(r"(pseudonym|anonym|hash|deidentify|de-identify)", text, re.IGNORECASE):
        tags.add("pseudonymization")
    if re.search(r"(format|convert|serialize|deserialize|parse|render)", text, re.IGNORECASE):
        tags.add("format_conversion")
    if re.search(r"(merge|join|combine|concat|append)", text, re.IGNORECASE):
        tags.add("merge_join")
    if op == "decision" or op == "condition" or re.search(r"(route|decide|choose|branch|if\b|when\b)", text, re.IGNORECASE):
        tags.add("routing_decision")
    if op == "guard" or re.search(r"(policy|guard|allow|deny|must|should not|forbid)", text, re.IGNORECASE):
        tags.add("policy_guard")


# Port of inferBoundary (node-profiler.js:644-693)
def infer_boundary(config):
    roles = config.get("roles") or set()
    security_tags = config.get("securityTags") or set()
    text = config.get("text") or ""
    data_surface = "tool_io"
    receiver_scope = "local_runtime"
    retention_scope = "transient"
    trust_boundary = "local_process"

    is_external = "external_egress" in roles or "network_egress" in security_tags or "webhook_post" in security_tags or "api_call" in security_tags
    is_model = "model_inference" in roles
    is_persistent = "local_persistence" in roles

    if "control_context" in roles and "user_input" in security_tags and not is_external and not is_model and not is_persistent:
        data_surface = "user_prompt"
        receiver_scope = "same_skill"
        trust_boundary = "user_visible"
    if is_model:
        data_surface = "llm_context"
        receiver_scope = "model_provider"
        trust_boundary = "model_provider"
    if is_external:
        data_surface = "network"
        receiver_scope = "third_party_service" if ("third_party_service" in security_tags or re.search(r"webhook|external|public|third", text, re.IGNORECASE)) else "first_party_service"
        retention_scope = "external"
        trust_boundary = "external_network"
    if is_persistent and not is_external and not is_model:
        retention_scope = "persistent"
        trust_boundary = "persistent_storage"
        if "memory_write" in security_tags or "memory_read" in security_tags:
            data_surface = "memory_store"
        elif "database_write" in security_tags or "database_read" in security_tags:
            data_surface = "database"
        else:
            data_surface = "local_file"
    if "command_execution" in roles:
        data_surface = "runtime_env"
        receiver_scope = "local_runtime"
        trust_boundary = "local_process"
    if not is_external and not is_model and not is_persistent:
        if "browser_read" in security_tags:
            data_surface = "browser"
        if "env_read" in security_tags or "credential_read" in security_tags:
            data_surface = "runtime_env"
        if "file_read" in security_tags:
            data_surface = "local_file"
        if "database_read" in security_tags:
            data_surface = "database"
        if "memory_read" in security_tags:
            data_surface = "memory_store"

    return {"data_surface": data_surface, "receiver_scope": receiver_scope, "retention_scope": retention_scope, "trust_boundary": trust_boundary}


# Port of nodeDisplayName (node-profiler.js:695-697)
def node_display_name(node=None):
    node = node or {}
    return node.get("canonical_name") or node.get("name") or node.get("id") or ""


# Port of nodeSecurityText (node-profiler.js:699-742)
def node_security_text(node=None, context=None):
    node = node or {}
    context = context or {}
    semantics = node.get("formal_semantics") or {}
    if isinstance(semantics.get("targets"), list):
        targets = " ".join(f"{t.get('type') or ''}:{t.get('value') or ''}:{t.get('raw') or ''}" for t in semantics["targets"])
    else:
        targets = ""
    effects = " ".join(semantics["effects"]) if isinstance(semantics.get("effects"), list) else ""
    edge_text = " ".join(
        " ".join(x for x in [(e.get("data_flow") or {}).get("from_param"), (e.get("data_flow") or {}).get("to_param"), (e.get("data_flow") or {}).get("data_type")] if x)
        for e in [*(context.get("incomingEdges") or []), *(context.get("outgoingEdges") or [])]
    )
    ev = semantics.get("evidence") or {}
    parts = [
        node.get("canonical_name"),
        node.get("name"),
        node.get("description"),
        node.get("action"),
        node.get("instructionText"),
        node.get("docAction"),
        " ".join(node["docActions"]) if isinstance(node.get("docActions"), list) else "",
        semantics.get("operation_type"),
        ev.get("text"),
        targets,
        effects,
        _json_stringify(node.get("signature") or {}),
        _json_stringify(node.get("input") or {}),
        _json_stringify(node.get("output") or {}),
        edge_text,
    ]
    return " ".join(str(p) for p in parts if p)


# Port of nodeActionText (node-profiler.js:751-768)
def node_action_text(node=None):
    node = node or {}
    semantics = node.get("formal_semantics") or {}
    ev = semantics.get("evidence") or {}
    parts = [
        node.get("instructionText"),
        ev.get("text"),
        ev.get("source_line"),
        node.get("description"),
    ]
    name = str(node.get("canonical_name") or node.get("name") or "")
    is_doc_slug = bool(re.match(r"^doc\.(step|op|context)\.", name))
    if not is_doc_slug and name:
        parts.insert(0, name)
    return " ".join(str(p) for p in parts if p)


# Port of profileDataType (node-profiler.js:770-777)
def profile_data_type(node=None):
    node = node or {}
    output_keys = list(((node.get("signature") or {}).get("output") or node.get("output") or {}).keys())
    input_keys = list(((node.get("signature") or {}).get("input") or node.get("input") or {}).keys())
    fs = node.get("formal_semantics") or {}
    if isinstance(fs.get("targets"), list):
        targets = ", ".join(f"{t.get('type')}:{t.get('value')}" for t in fs["targets"])
    else:
        targets = ""
    return ", ".join(p for p in [targets, ", ".join(output_keys), ", ".join(input_keys)] if p)


# Port of groupEdges (node-profiler.js:779-788)
def group_edges(edges, key):
    grouped = {}
    for edge in edges or []:
        node_id = (edge or {}).get(key)
        if not node_id:
            continue
        grouped.setdefault(node_id, []).append(edge)
    return grouped


# Port of addEvidence (node-profiler.js:790-792)
def add_evidence(evidence, kind, text, confidence):
    evidence.append({"kind": kind, "text": str(text or "")[:240], "confidence": confidence})


# Port of confidenceFromEvidence (node-profiler.js:794-798)
def confidence_from_evidence(evidence):
    if not len(evidence):
        return 0.3
    mx = max(_num(item.get("confidence") or 0.3) for item in evidence)
    return js_round(mx * 1000) / 1000


# Port of roundConfidence (node-profiler.js:800-804)
def round_confidence(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.3
    if n != n or n in (float("inf"), float("-inf")):
        return 0.3
    return max(0, min(1, js_round(n * 1000) / 1000))


# Port of isUserQuery (node-profiler.js:806-808)
def is_user_query(node=None):
    node = node or {}
    return str(node.get("name") or "").lower() == "user.query"


# Port of readPattern (node-profiler.js:810-812)
def read_pattern(text):
    return bool(re.search(r"\b(read|get|fetch|retrieve|search|list|find|select|query|load|scrape)\b", text, re.IGNORECASE))


# Port of transformPattern (node-profiler.js:814-816)
def transform_pattern(text):
    return bool(re.search(r"\b(transform|extract|parse|summari[sz]e|summary|digest|brief|classify|analyze|filter|format|convert|redact|mask|sanitize|aggregate|count|hash|merge|join)\b", text, re.IGNORECASE))


# Port of isModelNode (node-profiler.js:818-820)
def is_model_node(text):
    return bool(re.search(r"\b(llm|model|chat|completion|openai|anthropic|dashscope|qwen|gpt|claude|gemini|inference)\b", text, re.IGNORECASE))


# Port of isLlmConsumingTransform (node-profiler.js:822-825)
def is_llm_consuming_transform(text, op=""):
    if op != "transform" and not transform_pattern(text):
        return False
    return bool(re.search(r"\b(summari[sz]e|summary|digest|brief|classify|extract|parse|analyze)\b", text, re.IGNORECASE))


# Port of externalEgressPattern (node-profiler.js:827-836)
def external_egress_pattern(text):
    return bool(
        re.search(r"\b(webhooks?|https?|upload|email[._-]?send|send[._-]?mail|api[._-]call|external[._-]api|third[_\-\s]?party)\b", text, re.IGNORECASE)
        or re.search(r"\b(?:send|posts?|publish|shares?|push)(?:ed|ing|s)?\s+(?:to|the|a|an|it|them|data|payload|request|message|report|results?|file|email|webhook|via|externally)\b", text, re.IGNORECASE)
        or re.search(r"\b(?:post|send|publish)\s+request\b|\bhttp[s]?\s+(?:request|call|post|get)\b|\bapi\s+(?:call|request|endpoint)\b", text, re.IGNORECASE)
    )


# Port of localPersistencePattern (node-profiler.js:838-840)
def local_persistence_pattern(text):
    return bool(re.search(r"\b(write|save|persist|store|append|file_write|memory_write|database_write|db_write|produce_artifact)\b|(?:create|generate|export|produce)[\s._-]*(?:artifact|report|log|file|document)", text, re.IGNORECASE))


# Port of commandPattern (node-profiler.js:842-844)
def command_pattern(text):
    return bool(re.search(r"\b(exec|execute|shell|command|process|spawn|run_script|subprocess)\b", text, re.IGNORECASE))


# Port of destructivePattern (node-profiler.js:846-848)
def destructive_pattern(text):
    return bool(re.search(r"\b(delete|remove|destroy|drop|truncate|wipe)\b", text, re.IGNORECASE))


# Port of hasSinkLikeRole (node-profiler.js:850-853)
def has_sink_like_role(roles):
    return any(role in roles for role in ["external_egress", "model_inference", "local_persistence", "command_execution", "destructive_operation", "tool_invocation"])


# ---------------------------------------------------------------------------
# JS-parity helpers
# ---------------------------------------------------------------------------

def _json_stringify(value):
    """JSON.stringify(value) with JS default separators (no spaces)."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _search(text, pattern):
    """String.prototype.search: index of first regex match, or -1."""
    m = re.search(pattern, text, re.IGNORECASE)
    return m.start() if m else -1


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _is_finite_num(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return False
    return n == n and n not in (float("inf"), float("-inf"))
