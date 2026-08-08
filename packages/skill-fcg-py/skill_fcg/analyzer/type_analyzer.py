"""Port of src/parser/type-analyzer.js.

Sparse dependency-candidate analysis over the merged node set: four candidate
generators (scoped sequence / explicit reference / boundary impact / global
route), compatible-param + confidence scoring, and a stable candidate sort. The
returned list carries a non-enumerable `.statistics` in JS; here statistics ride
on a `_statistics` attribute of the returned list subclass so downstream reads
(`candidates.statistics`) work without polluting JSON. Node/edge shapes and all
keys mirror the JS verbatim.
"""

import functools
import re


TypeSystem = {
    "string": {"compatible_with": ["string", "text"]},
    "number": {"compatible_with": ["number", "integer", "float"]},
    "boolean": {"compatible_with": ["boolean"]},
    "array": {"compatible_with": ["array", "list"]},
    "object": {"compatible_with": ["object", "dict", "map"]},
    "app_token": {"compatible_with": ["string", "app_token"]},
    "table_id": {"compatible_with": ["string", "table_id"]},
    "record_id": {"compatible_with": ["string", "record_id"]},
    "user_id": {"compatible_with": ["string", "open_id", "user_id"]},
    "chat_id": {"compatible_with": ["string", "chat_id"]},
    "timestamp": {"compatible_with": ["number", "string", "timestamp"]},
    "date": {"compatible_with": ["string", "number", "date", "timestamp"]},
    "file_content": {"compatible_with": ["string", "file_content", "text"]},
    "message": {"compatible_with": ["string", "message", "text"]},
    "structured_data": {"compatible_with": ["object", "array", "structured_data"]},
}


class _CandidateList(list):
    """List subclass carrying the non-enumerable `.statistics` the JS attaches."""
    statistics = None


# Port of isTypeCompatible (type-analyzer.js:34-55)
def is_type_compatible(return_type, input_type):
    if return_type == input_type:
        return True
    return_type_info = TypeSystem.get(return_type)
    if return_type_info and input_type in return_type_info["compatible_with"]:
        return True
    if str(input_type).startswith("array<"):
        m = re.search(r"<(.+)>", input_type)
        if m and return_type == m.group(1):
            return True
    if return_type == "string" and input_type not in ("boolean", "number"):
        return True
    return False


# Port of analyzeTypeCompatibility (type-analyzer.js:62-100)
def analyze_type_compatibility(tools, options=None):
    options = options or {}
    all_nodes = tools or []
    eligible_nodes = [n for n in all_nodes if is_dependency_candidate_node(n)]
    raw_pair_upper_bound = len(eligible_nodes) * max(0, len(eligible_nodes) - 1)
    max_candidates = normalize_positive_integer(
        options.get("maxCandidates", _env("FCG_DEPENDENCY_MAX_CANDIDATES")), 2000
    )
    scope_window = normalize_positive_integer(
        options.get("scopeWindow", _env("FCG_DEPENDENCY_SCOPE_WINDOW")), 4
    )
    candidate_map = {}

    add_scoped_sequence_candidates(candidate_map, eligible_nodes, scope_window)
    add_explicit_reference_candidates(candidate_map, eligible_nodes)
    add_boundary_impact_candidates(candidate_map, eligible_nodes)
    add_global_route_candidates(candidate_map, eligible_nodes)

    ordered = sorted(candidate_map.values(), key=functools.cmp_to_key(compare_dependency_candidates))[:max_candidates]
    candidates = _CandidateList()
    for index, candidate in enumerate(ordered):
        candidates.append({
            **candidate,
            "candidate_id": candidate.get("candidate_id") or f"dep_{str(index + 1).rjust(4, '0')}",
        })

    candidates.statistics = {
        "dependency_candidate_count": len(candidates),
        "dependency_candidate_pruned_count": max(0, raw_pair_upper_bound - len(candidates)),
        "dependency_candidate_raw_upper_bound": raw_pair_upper_bound,
        "dependency_candidate_max": max_candidates,
    }
    return candidates


# Port of addScopedSequenceCandidates (type-analyzer.js:102-123)
def add_scoped_sequence_candidates(candidate_map, nodes, scope_window):
    by_file = group_by([n for n in nodes if (n.get("location") or {}).get("file")],
                       lambda n: normalize_path(n["location"]["file"]))
    for group in by_file.values():
        ordered = sorted(group, key=lambda n: _num((n.get("location") or {}).get("line")))
        for index in range(len(ordered)):
            source = ordered[index]
            seen = 0
            nxt = index + 1
            while nxt < len(ordered) and seen < scope_window:
                target = ordered[nxt]
                seen += 1
                if is_low_value_script_call_pair(source, target):
                    nxt += 1
                    continue
                add_candidate(candidate_map, source, target, {
                    "kind": "scoped_sequence",
                    "reason": "same file local execution/document order",
                    "priority": 20 if is_boundary_like_node(target) else 55,
                })
                nxt += 1


# Port of addExplicitReferenceCandidates (type-analyzer.js:125-148)
def add_explicit_reference_candidates(candidate_map, nodes):
    token_map = {}
    for node in nodes:
        for token in meaningful_reference_tokens(node):
            token_map.setdefault(token, []).append(node)
    for token, bucket in token_map.items():
        if len(bucket) < 2 or len(bucket) > 24:
            continue
        for source in bucket:
            for target in bucket:
                if source is target:
                    continue
                if not is_likely_forward_reference(source, target):
                    continue
                add_candidate(candidate_map, source, target, {
                    "kind": "explicit_reference",
                    "reason": f"shared explicit reference token: {token}",
                    "priority": 15 if is_boundary_like_node(target) else 35,
                })


# Port of addBoundaryImpactCandidates (type-analyzer.js:150-166)
def add_boundary_impact_candidates(candidate_map, nodes):
    by_file = group_by([n for n in nodes if (n.get("location") or {}).get("file")],
                       lambda n: normalize_path(n["location"]["file"]))
    for target in [n for n in nodes if is_boundary_like_node(n)]:
        file_group = by_file.get(normalize_path((target.get("location") or {}).get("file") or "")) or []
        before = [
            s for s in file_group
            if s is not target and _num((s.get("location") or {}).get("line")) <= _num((target.get("location") or {}).get("line"))
        ]
        before = sorted(before, key=lambda a: -_num((a.get("location") or {}).get("line")))[:8]
        for source in before:
            add_candidate(candidate_map, source, target, {
                "kind": "boundary_impact",
                "reason": "nearby source may affect boundary observation",
                "priority": 5,
            })


# Port of addGlobalRouteCandidates (type-analyzer.js:168-183)
def add_global_route_candidates(candidate_map, nodes):
    route_sources = [n for n in nodes if is_route_context_node(n) or is_doc_action_node(n)]
    route_targets = [n for n in nodes if is_executable_or_tool_node(n) or is_boundary_like_node(n)]
    for source in route_sources:
        for target in route_targets:
            if source is target:
                continue
            if not is_cross_stage_pair(source, target):
                continue
            if not has_meaningful_token_overlap(source, target):
                continue
            add_candidate(candidate_map, source, target, {
                "kind": "global_route",
                "reason": "cross-file or cross-stage route candidate",
                "priority": 10 if is_boundary_like_node(target) else 25,
            })


# Port of addCandidate (type-analyzer.js:185-216)
def add_candidate(candidate_map, source_tool, target_tool, meta=None):
    meta = meta or {}
    if not source_tool.get("name") or not target_tool.get("name"):
        return
    if source_tool["name"] == target_tool["name"]:
        return
    if not is_reasonable_direction(source_tool, target_tool):
        return
    if not is_call_site_order_compatible(source_tool, target_tool):
        return
    if is_global_llm_call_site_pair(source_tool, target_tool):
        return
    if is_context_only_node(source_tool) or is_context_only_node(target_tool):
        return
    if is_low_value_script_call_pair(source_tool, target_tool) and meta.get("kind") != "boundary_impact":
        return

    compatible_params = find_compatible_params(source_tool, target_tool)
    if not compatible_params:
        return

    key = f"{source_tool['name']}->{target_tool['name']}"
    confidence = calculate_type_confidence(compatible_params)
    high_value_reasons = high_value_reasons_for_pair(source_tool, target_tool, meta)
    candidate = {
        "source": source_tool,
        "target": target_tool,
        "compatibleParams": compatible_params,
        "confidence": confidence,
        "candidate_kind": meta.get("kind") or "dependency_rule",
        "candidate_reason": meta.get("reason") or "sparse dependency candidate",
        "high_value": len(high_value_reasons) > 0,
        "high_value_reasons": high_value_reasons,
        "llm_priority": _num(meta.get("priority") if meta.get("priority") is not None else 50) - len(high_value_reasons) * 10,
    }

    existing = candidate_map.get(key)
    if not existing or compare_dependency_candidates(candidate, existing) < 0:
        candidate_map[key] = candidate


# Port of findCompatibleParams (type-analyzer.js:224-248)
def find_compatible_params(source_tool, target_tool):
    compatible = []
    source_outputs = with_fallback_outputs(source_tool)
    target_inputs = with_fallback_inputs(target_tool)
    for output_param, output_info in source_outputs.items():
        for input_param, input_info in target_inputs.items():
            output_type = output_info.get("type") or "string"
            input_type = input_info.get("type") or "string"
            name_compatibility = is_param_name_compatible(output_param, input_param)
            if is_type_compatible(output_type, input_type) and name_compatibility:
                compatible.append({
                    "fromParam": output_param,
                    "toParam": input_param,
                    "fromType": output_type,
                    "toType": input_type,
                })
    return compatible


# Port of calculateTypeConfidence (type-analyzer.js:255-270)
def calculate_type_confidence(compatible_params):
    if len(compatible_params) == 0:
        return 0
    confidence = min(0.5 + len(compatible_params) * 0.1, 0.9)
    exact_matches = len([p for p in compatible_params if p["fromType"] == p["toType"]])
    confidence += exact_matches * 0.05
    name_matches = len([p for p in compatible_params if p["fromParam"] == p["toParam"]])
    confidence += name_matches * 0.05
    return min(confidence, 1.0)


# Port of withFallbackOutputs (type-analyzer.js:272-293)
def with_fallback_outputs(tool):
    output = {**(tool.get("output") or {})}
    if len(output) > 0:
        return output
    action = get_action(tool)
    if re.search(r"get|read|fetch|query|find|retrieve", action):
        output["data"] = {"type": "object"}
    elif re.search(r"list|search", action):
        output["items"] = {"type": "array"}
    elif re.search(r"create|add|insert", action):
        output["success"] = {"type": "boolean"}
        output["id"] = {"type": "string"}
    elif re.search(r"update|write|delete|remove|send|post|publish", action):
        output["success"] = {"type": "boolean"}
    if len(output) == 0:
        output["result"] = {"type": "object"}
    return output


# Port of withFallbackInputs (type-analyzer.js:295-308)
def with_fallback_inputs(tool):
    input_ = {**(tool.get("input") or {})}
    if len(input_) > 0:
        return input_
    action = get_action(tool)
    if re.search(r"create|add|insert|update|write|send|post|publish", action):
        input_["payload"] = {"type": "object"}
    elif re.search(r"get|list|search|query|fetch|read", action):
        input_["filter"] = {"type": "object", "required": False}
    else:
        input_["context"] = {"type": "object", "required": False}
    return input_


# Port of isReasonableDirection (type-analyzer.js:310-321)
def is_reasonable_direction(source_tool, target_tool):
    src_action = get_action(source_tool)
    tgt_action = get_action(target_tool)
    if (re.search(r"(create|add|insert|update|write|send|post|publish|delete|remove)", src_action)
            and re.search(r"(get|list|search|query|fetch|read|retrieve|find|select)", tgt_action)):
        return False
    return True


# Port of isCallSiteOrderCompatible (type-analyzer.js:323-328)
def is_call_site_order_compatible(source_tool, target_tool):
    source_order = _num(source_tool.get("callsite_order"))
    target_order = _num(target_tool.get("callsite_order"))
    if not source_order or not target_order:
        return True
    return source_order < target_order


# Port of isGlobalLlmCallSitePair (type-analyzer.js:330-333)
def is_global_llm_call_site_pair(source_tool, target_tool):
    if not source_tool.get("callsite_id") and not target_tool.get("callsite_id"):
        return False
    return source_tool.get("name") == "llm.inference" or target_tool.get("name") == "llm.inference"


# Port of getAction (type-analyzer.js:335-341)
def get_action(tool):
    if tool and isinstance(tool.get("action"), str) and tool.get("action"):
        return tool["action"].lower()
    name = str((tool or {}).get("name") or "").lower()
    parts = name.split(".")
    return parts[-1] if parts else ""


# Port of isParamNameCompatible (type-analyzer.js:343-361)
def is_param_name_compatible(from_param, to_param):
    src = str(from_param or "").lower()
    tgt = str(to_param or "").lower()
    if not src or not tgt:
        return True
    if src == tgt:
        return True
    src_tokens = set(t for t in re.split(r"[^a-z0-9]+", src) if len(t) >= 3)
    tgt_tokens = set(t for t in re.split(r"[^a-z0-9]+", tgt) if len(t) >= 3)
    if len(src_tokens) == 0 or len(tgt_tokens) == 0:
        return True
    for token in src_tokens:
        if token in tgt_tokens:
            return True
    generic = {"data", "payload", "result", "items", "content", "body"}
    return src in generic or tgt in generic


CONTEXT_ONLY_KINDS = {"doc_definition", "doc_schema", "doc_template", "doc_example", "doc_discard", "doc_review_error"}
ROUTE_CONTEXT_KINDS = {"doc_step", "doc_operation", "trigger", "policy"}
GENERIC_REFERENCE_TOKENS = {
    "data", "payload", "result", "context", "content", "object", "string", "boolean",
    "number", "array", "items", "script", "function", "call", "node", "step", "read",
    "write", "invoke", "tool", "model", "local", "runtime",
}


# Port of isDependencyCandidateNode (type-analyzer.js:405-411)
def is_dependency_candidate_node(node=None):
    node = node or {}
    if not node.get("name"):
        return False
    if node.get("callsite_id") or re.match(r"^llm\.inference#", str(node.get("name") or ""), re.IGNORECASE):
        return False
    if is_context_only_node(node):
        return False
    if node.get("excludeFromTypeAnalysis") and node.get("semanticKind") not in ROUTE_CONTEXT_KINDS:
        return False
    return True


# Port of isContextOnlyNode (type-analyzer.js:413-416)
def is_context_only_node(node=None):
    node = node or {}
    return (node.get("semanticKind") in CONTEXT_ONLY_KINDS
            or (node.get("excludeFromFlow") is True
                and str(node.get("operationType") or (node.get("formal_semantics") or {}).get("operation_type") or "") == "context"))


# Port of isDocActionNode (type-analyzer.js:418-420)
def is_doc_action_node(node=None):
    node = node or {}
    return node.get("semanticKind") in ("doc_step", "doc_operation") and not is_context_only_node(node)


# Port of isRouteContextNode (type-analyzer.js:422-424)
def is_route_context_node(node=None):
    node = node or {}
    return node.get("semanticKind") in ROUTE_CONTEXT_KINDS


# Port of isExecutableOrToolNode (type-analyzer.js:426-430)
def is_executable_or_tool_node(node=None):
    node = node or {}
    return (node.get("semanticKind") in ("script_entry", "script_function", "script_call")
            or node.get("type") == "tool_call"
            or bool(node.get("canonical_name") and not str(node.get("name") or "").startswith("llm.inference")))


# Port of isBoundaryLikeNode (type-analyzer.js:432-447)
def is_boundary_like_node(node=None):
    node = node or {}
    fs = node.get("formal_semantics") or {}
    parts = [
        node.get("name"),
        node.get("canonical_name"),
        node.get("action"),
        node.get("operationType"),
        fs.get("operation_type"),
        *(fs.get("effects") or []),
        *[f"{(t.get('type') or '')}:{(t.get('value') or '')}:{(t.get('raw') or '')}" for t in (fs.get("targets") or [])],
    ]
    text = " ".join(str(p) for p in parts if p).lower()
    return (has_boundary_term(text, ["external_egress", "webhook", "http", "https", "curl", "fetch", "post", "send", "upload", "publish", "api"])
            or has_boundary_term(text, ["model_inference", "llm", "openai", "anthropic", "dashscope", "gpt", "claude", "gemini", "model_context"])
            or has_boundary_term(text, ["persist", "save", "write", "append", "database", "db", "file_write", "local_file", "storage", "artifact"])
            or has_boundary_term(text, ["user_visible", "display", "show", "render", "print", "stdout"]))


# Port of hasBoundaryTerm (type-analyzer.js:449-456)
def has_boundary_term(text, terms=None):
    terms = terms or []
    normalized = re.sub(r"[^a-z0-9_:/.-]+", " ", str(text or ""))
    for term in terms:
        if term in ("http", "https"):
            if f"{term}:" in normalized:
                return True
            continue
        escaped = re.escape(term)
        if re.search(rf"(^|[^a-z0-9_]){escaped}([^a-z0-9_]|$)", normalized, re.IGNORECASE):
            return True
    return False


# Port of highValueReasonsForPair (type-analyzer.js:458-463)
def high_value_reasons_for_pair(source, target, meta=None):
    meta = meta or {}
    reasons = []
    if meta.get("kind") == "boundary_impact" or is_boundary_like_node(target):
        reasons.append("boundary-impact")
    if meta.get("kind") == "global_route" or is_cross_stage_pair(source, target):
        reasons.append("global-route")
    return list(dict.fromkeys(reasons))


# Port of isLowValueScriptCallPair (type-analyzer.js:465-469)
def is_low_value_script_call_pair(source=None, target=None):
    source = source or {}
    target = target or {}
    return (source.get("semanticKind") == "script_call"
            and target.get("semanticKind") == "script_call"
            and not is_boundary_like_node(target))


# Port of isLikelyForwardReference (type-analyzer.js:471-476)
def is_likely_forward_reference(source=None, target=None):
    source = source or {}
    target = target or {}
    sf = (source.get("location") or {}).get("file")
    tf = (target.get("location") or {}).get("file")
    if sf and tf and normalize_path(sf) == normalize_path(tf):
        return _num((source.get("location") or {}).get("line")) <= _num((target.get("location") or {}).get("line"))
    return is_cross_stage_pair(source, target) or is_boundary_like_node(target)


# Port of isCrossStagePair (type-analyzer.js:478-482)
def is_cross_stage_pair(source=None, target=None):
    source_stage = node_stage(source or {})
    target_stage = node_stage(target or {})
    return bool(source_stage and target_stage and source_stage != target_stage)


# Port of nodeStage (type-analyzer.js:484-491)
def node_stage(node=None):
    node = node or {}
    name = str(node.get("name") or "")
    if name == "user.query":
        return "user"
    if name.startswith("llm.inference"):
        return "llm"
    sk = str(node.get("semanticKind") or "")
    if sk.startswith("doc_") or node.get("semanticKind") in ("trigger", "policy"):
        return "doc"
    if sk.startswith("script_"):
        return "script"
    if node.get("type") == "tool_call" or node.get("canonical_name"):
        return "tool"
    return ""


# Port of meaningfulReferenceTokens (type-analyzer.js:493-513)
def meaningful_reference_tokens(node=None):
    node = node or {}
    semantics = node.get("formal_semantics") or {}
    ev = semantics.get("evidence") or {}
    values = [
        node.get("name"),
        node.get("canonical_name"),
        node.get("docRef"),
        node.get("ownerDoc"),
        node.get("ownerScript"),
        node.get("functionName"),
        node.get("callee"),
        node.get("instructionText"),
        ev.get("produced_object_key"),
        ev.get("consumed_object_key"),
        *[v for t in (semantics.get("targets") or []) for v in (t.get("type"), t.get("value"), t.get("raw"))],
        *[v for i in (semantics.get("inputs") or []) for v in (i.get("name"), i.get("type"))],
        *[v for o in (semantics.get("outputs") or []) for v in (o.get("name"), o.get("type"))],
    ]
    return set(
        t for t in tokenize_text(" ".join(str(v) for v in values if v))
        if len(t) >= 4 and t not in GENERIC_REFERENCE_TOKENS
    )


# Port of hasMeaningfulTokenOverlap (type-analyzer.js:515-522)
def has_meaningful_token_overlap(source, target):
    source_tokens = meaningful_reference_tokens(source)
    if not source_tokens:
        return False
    for token in meaningful_reference_tokens(target):
        if token in source_tokens:
            return True
    return False


# Port of tokenizeText (type-analyzer.js:524-530)
def tokenize_text(text):
    s = str(text or "").lower()
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    return [t for t in re.split(r"[^a-z0-9]+", s) if t]


# Port of groupBy (type-analyzer.js:532-541)
def group_by(items, key_fn):
    grouped = {}
    for item in items or []:
        key = key_fn(item)
        if not key:
            continue
        grouped.setdefault(key, []).append(item)
    return grouped


# Port of normalizePath (type-analyzer.js:543-545)
def normalize_path(value=""):
    return str(value or "").replace("\\", "/").lower()


# Port of compareDependencyCandidates (type-analyzer.js:547-555)
def compare_dependency_candidates(a, b):
    priority_delta = _num(a.get("llm_priority") if a.get("llm_priority") is not None else 50) - _num(b.get("llm_priority") if b.get("llm_priority") is not None else 50)
    if priority_delta != 0:
        return -1 if priority_delta < 0 else 1
    high_value_delta = int(bool(b.get("high_value"))) - int(bool(a.get("high_value")))
    if high_value_delta != 0:
        return high_value_delta
    confidence_delta = _num(b.get("confidence")) - _num(a.get("confidence"))
    if confidence_delta != 0:
        return -1 if confidence_delta < 0 else 1
    return _locale_compare(dependency_candidate_key(a), dependency_candidate_key(b))


# Port of dependencyCandidateKey (type-analyzer.js:557-563)
def dependency_candidate_key(candidate=None):
    candidate = candidate or {}
    return "::".join([
        (candidate.get("source") or {}).get("name") or "",
        (candidate.get("target") or {}).get("name") or "",
        candidate.get("candidate_kind") or "",
    ])


# Port of normalizePositiveInteger (type-analyzer.js:565-568)
def normalize_positive_integer(value, fallback):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number == int(number) and number > 0:
        return int(number)
    return fallback


# Port of inferType (type-analyzer.js:575-582)
def infer_type(value):
    if isinstance(value, str):
        return "string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)


def _env(name):
    import os
    return os.environ.get(name)
