"""Port of src/analyzer/llm-validator.js — RULE-ONLY subset.

Only the deterministic (LLM-disabled) path is ported: this is all M1 acceptance
needs. When disableLlm is true (or no api key), validatePairs never selects any
pair for the LLM, the batch loop is a no-op, and every candidate is judged by
getHeuristicValidation (key overlap + shared-token scoring). The full async LLM
batch/cache path (validateDependencyPairBatch, callDependencyBatchLLM, cache
files) is intentionally NOT ported — it never fires in rule-only mode.

The returned list carries a non-enumerable `.statistics` in JS; here it rides on
a `_CandidateList` subclass attribute, same convention as type_analyzer.

Node/edge shapes and all keys mirror the JS verbatim.
"""

import functools
import re


class _CandidateList(list):
    """List subclass carrying the non-enumerable `.statistics` the JS attaches."""
    statistics = None


# Port of tokenize (llm-validator.js:245-254)
def tokenize(*parts):
    joined = " ".join(str(p) for p in parts if p)
    tokens = re.split(r"[^a-z0-9_]+", joined.lower())
    return {t for t in tokens if len(t) >= 3}


# Port of intersectSize (llm-validator.js:256-262)
def intersect_size(set_a, set_b):
    size = 0
    for token in set_a:
        if token in set_b:
            size += 1
    return size


# Port of clamp (llm-validator.js:264-266)
def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


# Port of describeHeuristicFlow (llm-validator.js:239-243)
def describe_heuristic_flow(output_keys, input_keys):
    src = ", ".join(output_keys) if output_keys else "source_output"
    tgt = ", ".join(input_keys) if input_keys else "target_input"
    return f"{src} -> {tgt}"


# Port of getHeuristicValidation (llm-validator.js:206-237)
def get_heuristic_validation(source_tool=None, target_tool=None, reason_prefix="Heuristic validation"):
    source_tool = source_tool or {}
    target_tool = target_tool or {}
    output_keys = list((source_tool.get("output") or {}).keys())
    input_keys = list((target_tool.get("input") or {}).keys())

    input_set = {k.lower() for k in input_keys}
    exact_overlap = len([k for k in output_keys if k.lower() in input_set])

    source_tokens = tokenize(source_tool.get("name"), source_tool.get("description"), *output_keys)
    target_tokens = tokenize(target_tool.get("name"), target_tool.get("description"), *input_keys)
    shared_semantic_tokens = intersect_size(source_tokens, target_tokens)

    score = 0.2
    score += min(0.5, exact_overlap * 0.25)
    score += min(0.25, shared_semantic_tokens * 0.05)

    source_name = str(source_tool.get("name") or "").lower()
    target_name = str(target_tool.get("name") or "").lower()
    if re.search(r"(get|list|read|fetch|query|search)", source_name) and re.search(r"(create|update|write|send|post|insert)", target_name):
        score += 0.15

    confidence = clamp(score, 0.05, 0.95)
    is_compatible = exact_overlap > 0 or shared_semantic_tokens >= 2 or confidence >= 0.65

    return {
        "is_compatible": is_compatible,
        "confidence": confidence,
        "reason": f"{reason_prefix}. exact_overlap={exact_overlap}, semantic_overlap={shared_semantic_tokens}",
        "data_flow_description": describe_heuristic_flow(output_keys, input_keys),
    }


# Port of normalizeDependencyLlmPolicy (llm-validator.js:523-528)
def normalize_dependency_llm_policy(value):
    policy = str(value or "").strip().lower()
    if policy in ("off", "none", "false", "0"):
        return "off"
    if policy == "all":
        return "all"
    return "high_value"


# Port of ruleReasonPrefix (llm-validator.js:530-535)
def rule_reason_prefix(has_api_key, policy, selected_for_llm, llm_max_pairs, total_pairs):
    if not has_api_key:
        return "Rule dependency validation: LLM_API_KEY not set"
    if policy == "off":
        return "Rule dependency validation: dependency LLM policy is off"
    if selected_for_llm:
        return "Rule dependency validation: selected high-value LLM candidate had no valid LLM result"
    return f"Rule dependency validation: not selected for high-value LLM budget ({llm_max_pairs}/{total_pairs})"


# Port of pairKey (llm-validator.js:643-645)
def pair_key(pair=None):
    pair = pair or {}
    src = (pair.get("source") or {}).get("name") or ""
    tgt = (pair.get("target") or {}).get("name") or ""
    return f"{src}->{tgt}"


# Port of validationPairKey (llm-validator.js:659-666)
def validation_pair_key(pair):
    pair = pair or {}
    cp = pair.get("compatibleParams") or []
    first = cp[0] if cp else {}
    return "::".join([
        (pair.get("source") or {}).get("name") or "",
        (pair.get("target") or {}).get("name") or "",
        first.get("fromParam") or "",
        first.get("toParam") or "",
    ])


# Port of normalizePositiveInteger (llm-validator.js:668-671)
def normalize_positive_integer(value, fallback):
    number = _js_number(value)
    if isinstance(number, int) and number > 0:
        return number
    if isinstance(number, float) and number.is_integer() and number > 0:
        return int(number)
    return fallback


# Port of compareValidationPairs (llm-validator.js:651-657) — via cmp_to_key
def _compare_validation_pairs(a, b):
    priority_delta = _num(a.get("llm_priority"), 50) - _num(b.get("llm_priority"), 50)
    if priority_delta != 0:
        return -1 if priority_delta < 0 else 1
    confidence_delta = _num(b.get("confidence"), 0) - _num(a.get("confidence"), 0)
    if confidence_delta != 0:
        return -1 if confidence_delta < 0 else 1
    return _locale_compare(validation_pair_key(a), validation_pair_key(b))


# Port of validatePairs (llm-validator.js:274-380) — RULE-ONLY.
# In rule-only mode hasApiKey is false, so llmMaxPairs=0, llmSelection is empty,
# the batch loop never runs, and every pair falls to getHeuristicValidation.
def validate_pairs(compatible_pairs, config=None):
    config = config or {}
    validated_edges = _CandidateList()

    api_key = config.get("apiKey")
    if api_key is None:
        api_key = ""
    has_api_key = (not config.get("disableLlm")) and bool(str(api_key).strip())
    policy = normalize_dependency_llm_policy(config.get("dependencyLlmPolicy") or "high_value")
    llm_max_pairs = normalize_positive_integer(
        config.get("dependencyLlmMaxPairs") or config.get("llmMaxPairs"), 32
    ) if (has_api_key and policy != "off") else 0

    pairs = sorted(list(compatible_pairs), key=functools.cmp_to_key(_compare_validation_pairs))

    # LLM selection is empty in rule-only mode; keep the structure for fidelity.
    llm_selection = _select_dependency_llm_pairs(pairs, has_api_key, policy, llm_max_pairs)
    llm_pair_keys = {pair_key(p) for p in llm_selection}
    llm_results = {}
    statistics = {
        "dependency_llm_policy": policy,
        "dependency_llm_candidate_count": len(llm_selection),
        "dependency_llm_validated_count": 0,
        "dependency_llm_cache_hit_count": 0,
        "dependency_llm_request_count": 0,
        "dependency_llm_error_count": 0,
    }

    for pair in pairs:
        selected_for_llm = pair_key(pair) in llm_pair_keys
        llm_result = llm_results.get(pair_key(pair))
        use_llm = bool(llm_result)
        if use_llm:
            result = llm_result
        else:
            result = get_heuristic_validation(
                pair.get("source"),
                pair.get("target"),
                rule_reason_prefix(has_api_key, policy, selected_for_llm, llm_max_pairs, len(pairs)),
            )
        heuristic_pass = (not use_llm) and _num(pair.get("confidence"), 0) >= 0.8

        if result["is_compatible"] or heuristic_pass:
            combined_confidence = (
                clamp(result["confidence"] * _num(pair.get("confidence"), 0), 0, 1)
                if result["is_compatible"]
                else clamp(_num(pair.get("confidence"), 0) * 0.7, 0, 1)
            )
            source = pair.get("source") or {}
            target = pair.get("target") or {}
            cp = pair.get("compatibleParams") or []
            first = cp[0] if cp else {}
            edge = {
                "id": f"edge_{len(validated_edges) + 1}",
                "source": source.get("id") or source.get("name"),
                "target": target.get("id") or target.get("name"),
                "type": "data_dependency",
                "confidence": combined_confidence,
                "validation_method": "dependency_llm_high_value" if use_llm else "dependency_rule",
                "data_flow": {
                    "from_param": first.get("fromParam") or "unknown",
                    "to_param": first.get("toParam") or "unknown",
                    "data_type": first.get("fromType") or "string",
                },
                "semantic_reason": result["reason"] if result["is_compatible"]
                else "Rule fallback accepted high-confidence sparse dependency edge",
                "candidate_id": pair.get("candidate_id") or "",
                "candidate_kind": pair.get("candidate_kind") or "",
                "candidate_reason": pair.get("candidate_reason") or "",
                "high_value_reasons": pair.get("high_value_reasons") or [],
            }
            if use_llm:
                edge["llm_review"] = {"cache_hit": bool(llm_result.get("cache_hit"))}
            validated_edges.append(edge)
            if use_llm:
                statistics["dependency_llm_validated_count"] += 1

    validated_edges.statistics = statistics
    return validated_edges


# Port of selectDependencyLlmPairs (llm-validator.js:382-391)
def _select_dependency_llm_pairs(pairs, has_api_key, policy, llm_max_pairs):
    if not has_api_key or policy == "off" or llm_max_pairs <= 0:
        return []
    eligible = pairs if policy == "all" else [
        p for p in pairs if p.get("high_value") or len(p.get("high_value_reasons") or []) > 0
    ]
    ordered = sorted(list(eligible), key=functools.cmp_to_key(_compare_dependency_llm_priority))
    return ordered[:llm_max_pairs]


# Port of compareDependencyLlmPriority (llm-validator.js:393-402)
def _compare_dependency_llm_priority(a, b):
    priority_delta = _num(a.get("llm_priority"), 50) - _num(b.get("llm_priority"), 50)
    if priority_delta != 0:
        return -1 if priority_delta < 0 else 1
    reason_delta = len(b.get("high_value_reasons") or []) - len(a.get("high_value_reasons") or [])
    if reason_delta != 0:
        return -1 if reason_delta < 0 else 1
    uncertainty_a = abs(_num(a.get("confidence"), 0.5) - 0.65)
    uncertainty_b = abs(_num(b.get("confidence"), 0.5) - 0.65)
    if uncertainty_a != uncertainty_b:
        return -1 if uncertainty_a < uncertainty_b else 1
    return _locale_compare(validation_pair_key(a), validation_pair_key(b))


def _num(value, fallback):
    """JS Number(x) || fallback-ish, but Number() of undefined is NaN -> use as-is
    in arithmetic. Here we coerce to a real number, falling back when non-numeric."""
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return value
    try:
        n = float(value)
    except (TypeError, ValueError):
        return fallback
    return n


def _js_number(value):
    """JS Number(value): integral floats stay int-comparable via is_integer."""
    if isinstance(value, bool):
        return float("nan")
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


# localeCompare — faithful ICU-root ASCII ordering (see util/locale.py).
def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)
