"""Port of label-llm-assistant.js — the SECOND LLM feature, distinct from the
Markdown semantic gate. It reviews LOW-CONFIDENCE data labels via the LLM against
a CLOSED ontology, in the OUTPUT layer (via build_node_profiles_with_options →
build_transfer_security_profile). Production default is OFF.

Faithful port of applyLlmLabelAssistToProfiles and its helpers. The JS async
worker-pool is collapsed to a sequential loop: candidate profiles are disjoint
and their cache keys unique, so the final mutated state is order-independent —
identical output, and consistent with the rest of the Python engine's synchronous
LLM calls (doc_flow_extractor, feedback_edge_classifier).
"""
import json
import os
import re

from ..llm.normalizers import parse_loose_json, normalize_scaled_number
from ..llm.transport import post_json_with_timeout
from .data_labeler import create_label, max_sensitivity, short_hash
from .label_ontology import (
    get_allowed_llm_label_map,
    get_ontology_version,
    get_ontology_stats,
    list_allowed_llm_labels,
)

ONTOLOGY_VERSION = get_ontology_version()
ALLOWED_LABELS = get_allowed_llm_label_map()
AMBIGUOUS_FIELD_PATTERN = re.compile(
    r"\b(payload|data|content|result|metadata|value|body|response|output|input|"
    r"object|record|item|info|details)\b",
    re.IGNORECASE,
)


# Port of applyLlmLabelAssistToProfiles (label-llm-assistant.js:24-58)
def apply_llm_label_assist_to_profiles(profiles=None, nodes=None, edges=None, options=None):
    profiles = profiles or []
    nodes = nodes or []
    edges = edges or []
    options = options or {}
    stats = _create_stats(bool(options.get("enabled")))
    if not options.get("enabled"):
        return {"profiles": profiles, "statistics": stats}
    if not str(options.get("apiKey") or "").strip():
        raise ValueError("LLM_API_KEY is required when --label-llm-assist is enabled")

    nodes_by_id = {n.get("id"): n for n in nodes}
    edge_context_by_node = _build_edge_context(edges)
    cache = _load_cache(options.get("cachePath"))

    candidates = []
    for profile in profiles:
        reason = should_assist_profile(profile)
        if reason["shouldAssist"]:
            candidates.append({"profile": profile, "reason": reason})
    stats["label_llm_candidate_count"] = len(candidates)

    # JS runs an async worker-pool of size `concurrency`; Python transport is
    # synchronous and each profile mutation is disjoint (unique cache key), so a
    # sequential pass yields byte-identical output.
    for item in candidates:
        _review_one_profile(item["profile"], item["reason"], {
            "nodes_by_id": nodes_by_id,
            "edge_context_by_node": edge_context_by_node,
            "cache": cache,
            "options": options,
            "stats": stats,
        })

    _save_cache(options.get("cachePath"), cache)
    return {"profiles": profiles, "statistics": stats}


# Port of reviewOneProfile (label-llm-assistant.js:60-134)
def _review_one_profile(profile, reason, context):
    nodes_by_id = context["nodes_by_id"]
    cache = context["cache"]
    options = context["options"]
    stats = context["stats"]
    node = nodes_by_id.get(profile.get("node_id")) or {}
    cache_key = build_cache_key(profile, node, options.get("model"))
    response = cache.get(cache_key)
    cache_hit = bool(response)  # JS: Boolean(response) — falsy cached value re-calls
    if cache_hit:
        stats["label_llm_cache_hit_count"] += 1
    else:
        try:
            prompt = build_prompt(
                profile, node, context["edge_context_by_node"].get(profile.get("node_id")) or [])
            assistant = options.get("labelAssistant")
            if callable(assistant):
                response = assistant({
                    "profile": profile, "node": node, "reason": reason,
                    "prompt": prompt, "options": options,
                })
            else:
                response = _call_label_assistant(prompt, options)
            cache[cache_key] = response
        except Exception as error:  # noqa: BLE001 — mirror JS catch(all)
            stats["label_llm_error_count"] += 1
            _attach_assist_error(profile, str(error))
            return

    normalized = normalize_assistant_labels(
        response, {"profile": profile, "node": node, "reason": reason, "model": options.get("model")})
    stats["label_llm_ignored_count"] += len(normalized["ignored"])
    data_profile = profile.setdefault("data_profile", {"labels": []})
    if normalized["errors"]:
        data_profile["label_llm_assist_errors"] = (
            data_profile.get("label_llm_assist_errors") or []) + normalized["errors"]

    deterministic_labels = data_profile.get("labels") or []
    has_explicit_deterministic = any(not is_fallback_label(l) for l in deterministic_labels)
    existing_keys = {l.get("label") for l in deterministic_labels}
    accepted = []
    review_evidence = []
    for label in normalized["labels"]:
        if label["label"] in existing_keys or (is_fallback_label(label) and has_explicit_deterministic):
            review_evidence.append({
                "label": label["label"],
                "reason": label.get("reason") or (label.get("llm_review") or {}).get("reason")
                or "LLM supported existing deterministic label",
                "model": options.get("model") or "",
                "ontology_version": ONTOLOGY_VERSION,
                "fallback_suppressed": bool(is_fallback_label(label) and has_explicit_deterministic),
            })
            continue
        accepted.append(label)
        existing_keys.add(label["label"])

    if accepted:
        data_profile.setdefault("labels", []).extend(accepted)
        data_profile["primary_category"] = _choose_primary_category(data_profile["labels"])
        data_profile["sensitivity"] = max_sensitivity(data_profile["labels"])
        data_profile["unknown_tail"] = True
        stats["label_llm_accepted_count"] += len(accepted)
    if review_evidence:
        data_profile["review_evidence"] = (
            data_profile.get("review_evidence") or []) + review_evidence
    data_profile["label_llm_assist"] = {
        "enabled": True,
        "triggered": True,
        "trigger_reasons": reason["reasons"],
        "accepted_count": len(accepted),
        "ignored_count": len(normalized["ignored"]),
        "cache_key": cache_key,
        "cache_hit": cache_hit,
        "ontology_version": ONTOLOGY_VERSION,
    }


# Port of shouldAssistProfile (label-llm-assistant.js:136-147)
def should_assist_profile(profile=None):
    profile = profile or {}
    reasons = []
    data_profile = profile.get("data_profile") or {}
    labels = data_profile.get("labels") or []
    if "data_introduction" not in (profile.get("node_roles") or []):
        return {"shouldAssist": False, "reasons": reasons}
    if len(labels) == 0:
        reasons.append("no_deterministic_labels")
    if len(labels) == 1 and labels[0].get("label") == "generic_data.data":
        reasons.append("generic_only")
    if data_profile.get("unknown_tail"):
        reasons.append("unknown_tail")
    highest_evidence = max([_evidence_rank(l.get("evidence_level")) for l in labels], default=-1)
    if 0 <= highest_evidence < _evidence_rank("L2"):
        reasons.append("low_evidence_level")
    if _has_ambiguous_fields(profile):
        reasons.append("ambiguous_field_name")
    return {"shouldAssist": len(reasons) > 0, "reasons": reasons}


# Port of hasAmbiguousFields (label-llm-assistant.js:149-156)
def _has_ambiguous_fields(profile=None):
    profile = profile or {}
    parts = [profile.get("node_name")]
    for label in (profile.get("data_profile") or {}).get("labels") or []:
        parts.extend([label.get("field_name"), label.get("field_path"), label.get("evidence_text")])
    for item in profile.get("evidence") or []:
        parts.append(item.get("text"))
    text = " ".join(p for p in parts if p)
    return bool(AMBIGUOUS_FIELD_PATTERN.search(text))


# Port of callLabelAssistant (label-llm-assistant.js:158-175)
def _call_label_assistant(prompt, options=None):
    options = options or {}
    endpoint = _resolve_endpoint(options)
    payload = post_json_with_timeout(endpoint, {
        "model": options.get("model") or "gpt-5.5",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You assist low-confidence data label classification. Return "
                    "strict JSON only. You may only choose labels from the provided "
                    "closed ontology. If uncertain, return an empty labels array or "
                    "generic_data.data."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }, {
        "timeoutMs": options.get("timeout") or 180000,
        "headers": {"Authorization": f"Bearer {options.get('apiKey')}"},
    })
    choices = (payload or {}).get("choices") or [{}]
    return (choices[0] or {}).get("message", {}).get("content") or payload


# Port of buildPrompt (label-llm-assistant.js:177-214)
def build_prompt(profile, node, edge_context):
    node = node or {}
    profile = profile or {}
    signature = node.get("signature") or {}
    return json.dumps({
        "task": ("Suggest candidate data labels only for low-confidence deterministic "
                 "labeling. Do not invent labels outside ontology."),
        "ontology_version": ONTOLOGY_VERSION,
        "ontology": list_allowed_llm_labels(),
        "response_schema": {
            "labels": [{
                "label": "one ontology label",
                "category": "category from ontology",
                "subtype": "subtype from ontology",
                "field_name": "field or empty",
                "evidence_text": "short direct evidence from input",
                "reason": "why this label may apply",
                "confidence": "0..1",
                "uncertainty": "what is uncertain",
            }],
        },
        "node": {
            "id": node.get("id") or profile.get("node_id"),
            "name": node.get("name") or profile.get("node_name"),
            "description": node.get("description") or "",
            "input": signature.get("input") if signature.get("input") is not None else (node.get("input") or {}),
            "output": signature.get("output") if signature.get("output") is not None else (node.get("output") or {}),
            "formal_semantics": node.get("formal_semantics") or {},
            "instructionText": node.get("instructionText") or "",
            "docAction": node.get("docAction") or "",
            "docActions": node.get("docActions") or [],
        },
        "deterministic_profile": {
            "node_roles": profile.get("node_roles") or [],
            "security_tags": profile.get("security_tags") or [],
            "operation_tags": profile.get("operation_tags") or [],
            "data_profile": profile.get("data_profile") or {},
            "evidence": profile.get("evidence") or [],
        },
        "adjacent_edges": edge_context,
    }, indent=2, ensure_ascii=False)


# Port of normalizeAssistantLabels (label-llm-assistant.js:216-237)
def normalize_assistant_labels(raw, context):
    parsed = parse_loose_json(raw)
    source = parsed["labels"] if (isinstance(parsed, dict) and isinstance(parsed.get("labels"), list)) else []
    labels = []
    ignored = []
    errors = []
    if not parsed:
        errors.append({"type": "parse_failed", "message": "Unable to parse LLM label JSON"})
        return {"labels": labels, "ignored": ignored, "errors": errors}
    for candidate in source:
        normalized = _normalize_candidate(candidate, context)
        if normalized.get("ignored"):
            ignored.append(normalized["ignored"])
            continue
        labels.append(normalized["label"])
    return {"labels": labels, "ignored": ignored, "errors": errors}


# Port of normalizeCandidate (label-llm-assistant.js:239-281)
def _normalize_candidate(candidate=None, context=None):
    candidate = candidate or {}
    context = context or {}
    raw_label = str(candidate.get("label")
                    or f"{candidate.get('category') or ''}.{candidate.get('subtype') or ''}").strip()
    ontology = ALLOWED_LABELS.get(raw_label)
    if not ontology:
        return {"ignored": {"reason": "unknown_or_disallowed_ontology_label", "label": raw_label}}
    cap = _confidence_cap(context.get("node"), candidate)
    confidence = min(cap, normalize_scaled_number(candidate.get("confidence"), fallback=0.45))
    evidence_level = "L2" if cap >= 0.75 else "L1"
    profile = context.get("profile") or {}
    origin_node = profile.get("node_id")
    origin_node_name = profile.get("node_name") or origin_node
    reason = str(candidate.get("reason") or "").strip()
    uncertainty = str(candidate.get("uncertainty") or "").strip()
    evidence_text = str(candidate.get("evidence_text") or candidate.get("evidence")
                        or reason or profile.get("node_name") or "")[:300]
    return {
        "label": create_label({
            "category": ontology["category"],
            "subtype": ontology["subtype"],
            "fieldName": candidate.get("field_name") or ontology["subtype"],
            "fieldPath": candidate.get("field_path") or "",
            "originNode": origin_node,
            "originNodeName": origin_node_name,
            "introducedAt": origin_node,
            "mode": "llm_assisted",
            "confidence": confidence,
            "evidenceLevel": evidence_level,
            "evidenceKind": "llm_low_confidence_assist",
            "evidenceText": evidence_text,
            "requiresReview": True,
            "uncertainty": uncertainty,
            "reason": reason,
            "ontologyVersion": ONTOLOGY_VERSION,
            "ontologyLabelId": ontology["label"],
            "llmReview": {
                "model": context.get("model") or "",
                "reason": reason,
                "uncertainty": uncertainty,
                "ontology_version": ONTOLOGY_VERSION,
            },
        }),
    }


# Port of isFallbackLabel (label-llm-assistant.js:283-285)
def is_fallback_label(label=None):
    label = label or {}
    return (label.get("label") == "generic_data.data"
            or label.get("label") == "unknown_sensitive.data"
            or bool(label.get("fallback")))


# Port of confidenceCap (label-llm-assistant.js:287-294)
def _confidence_cap(node=None, candidate=None):
    node = node or {}
    candidate = candidate or {}
    evidence_text = " ".join(
        p for p in [candidate.get("field_name"), candidate.get("evidence_text"), candidate.get("reason")] if p)
    formal = node.get("formal_semantics") or {}
    targets = formal.get("targets")
    has_formal = isinstance(targets, list) and len(targets) > 0
    has_instruction = bool(node.get("instructionText") or (formal.get("evidence") or {}).get("text"))
    if has_formal or has_instruction:
        return 0.75
    if candidate.get("field_name") or re.search(r"signature\.|input|output|field|schema", evidence_text, re.IGNORECASE):
        return 0.65
    return 0.55


# Port of attachAssistError (label-llm-assistant.js:296-302)
def _attach_assist_error(profile, message):
    if not profile.get("data_profile"):
        profile["data_profile"] = {"labels": []}
    profile["data_profile"]["label_llm_assist_errors"] = (
        profile["data_profile"].get("label_llm_assist_errors") or []) + [
        {"type": "call_failed", "message": str(message or "")}]


# Port of buildCacheKey (label-llm-assistant.js:304-324)
def build_cache_key(profile, node, model):
    node = node or {}
    profile = profile or {}
    signature = node.get("signature") or {}
    data_profile = profile.get("data_profile") or {}
    return "label_assist_" + short_hash(json.dumps({
        "ontology": ONTOLOGY_VERSION,
        "model": model or "",
        "node": {
            "id": node.get("id") or profile.get("node_id"),
            "name": node.get("name") or profile.get("node_name"),
            "description": node.get("description") or "",
            "input": signature.get("input") if signature.get("input") is not None else (node.get("input") or {}),
            "output": signature.get("output") if signature.get("output") is not None else (node.get("output") or {}),
            "formal_semantics": node.get("formal_semantics") or {},
            "instructionText": node.get("instructionText") or "",
        },
        "profile": {
            "roles": profile.get("node_roles") or [],
            "security_tags": profile.get("security_tags") or [],
            "operation_tags": profile.get("operation_tags") or [],
            "labels": data_profile.get("labels") or [],
        },
    }, ensure_ascii=False, separators=(",", ":")))


# Port of buildEdgeContext (label-llm-assistant.js:326-343)
def _build_edge_context(edges=None):
    grouped = {}
    for edge in edges or []:
        for node_id in [edge.get("source"), edge.get("target")]:
            if not node_id:
                continue
            grouped.setdefault(node_id, []).append({
                "direction": "outgoing" if edge.get("source") == node_id else "incoming",
                "source": edge.get("source"),
                "target": edge.get("target"),
                "type": edge.get("type") or "",
                "data_flow": edge.get("data_flow") or {},
                "semantic_reason": edge.get("semantic_reason") or "",
            })
    return grouped


# Port of loadCache (label-llm-assistant.js:345-358)
def _load_cache(cache_path):
    cache = {}
    if not cache_path or not os.path.exists(cache_path):
        return cache
    with open(cache_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except (ValueError, TypeError):
                continue  # Ignore corrupt cache lines.
            if item.get("key"):
                cache[item["key"]] = item.get("response")
    return cache


# Port of saveCache (label-llm-assistant.js:360-368)
def _save_cache(cache_path, cache):
    if not cache_path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    lines = [json.dumps({"key": key, "response": response}, ensure_ascii=False)
             for key, response in cache.items()]
    with open(cache_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + ("\n" if lines else ""))


# Port of resolveEndpoint (label-llm-assistant.js:370-376)
def _resolve_endpoint(options=None):
    options = options or {}
    if options.get("endpoint"):
        return options["endpoint"]
    if options.get("provider") == "dashscope":
        return (os.environ.get("DASHSCOPE_ENDPOINT")
                or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    return "https://api.openai.com/v1/chat/completions"


# Port of createStats (label-llm-assistant.js:378-388)
def _create_stats(enabled):
    return {
        **get_ontology_stats(),
        "label_llm_assist_enabled": bool(enabled),
        "label_llm_candidate_count": 0,
        "label_llm_accepted_count": 0,
        "label_llm_cache_hit_count": 0,
        "label_llm_error_count": 0,
        "label_llm_ignored_count": 0,
    }


# Port of choosePrimaryCategory (label-llm-assistant.js:390-393)
def _choose_primary_category(labels=None):
    labels = labels or []
    if not labels:
        return "generic_data"
    ordered = sorted(labels, key=lambda l: float(l.get("confidence") or 0), reverse=True)
    return ordered[0].get("category") or "generic_data"


# Port of evidenceRank (label-llm-assistant.js:395-398)
def _evidence_rank(level):
    return {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}.get(level, 0)


# Port of defaultLabelAssistStats (transfer-analysis.js:609-619) — used when the
# feature is off so the statistics block keeps the same keys as the JS engine.
def default_label_assist_stats(enabled):
    return {
        **get_ontology_stats(),
        "label_llm_assist_enabled": bool(enabled),
        "label_llm_candidate_count": 0,
        "label_llm_accepted_count": 0,
        "label_llm_cache_hit_count": 0,
        "label_llm_error_count": 0,
        "label_llm_ignored_count": 0,
    }
