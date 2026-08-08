"""Port of src/security/label-ontology.js.

Compiles label-ontology.json (135 labels, 153 regexes, all Python-re-compatible —
verified: no lookbehind / named groups / unicode props / backrefs) into a matcher
with priority/supersedes/sensitivity post-processing. Regexes use re.IGNORECASE
to mirror the JS `new RegExp(pattern, 'i')`. The compiled ontology is a
module-level singleton like the JS `compiledOntology`.
"""

import json
import os
import re

_ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "label-ontology.json")

with open(_ONTOLOGY_PATH, "r", encoding="utf-8") as _handle:
    _RAW_ONTOLOGY = json.load(_handle)

DEFAULT_EVIDENCE_CAPS = {"L4": 0.95, "L3": 0.85, "L2": 0.7, "L1": 0.55, "L0": 0.3}

DEFAULT_CATEGORY_SENSITIVITY = {
    "credentials": "critical",
    "financial": "critical",
    "health": "critical",
    "biometric": "critical",
    "pii": "high",
    "communication": "high",
    "file_content": "high",
    "browser_data": "high",
    "device_data": "high",
    "database_record": "high",
    "location": "high",
    "enterprise": "high",
    "unknown_sensitive": "high",
    "special_category": "critical",
    "personal_record": "high",
    "ai_context": "high",
    "security_data": "high",
    "network_data": "medium",
    "secret_material": "critical",
    "user_prompt": "medium",
    "aggregate_data": "medium",
    "pseudonymous_data": "medium",
    "generic_data": "low",
}

_compiled_ontology = None


# Port of getLabelOntology (label-ontology.js:39-42)
def get_label_ontology():
    global _compiled_ontology
    if _compiled_ontology is None:
        _compiled_ontology = _compile_ontology(_RAW_ONTOLOGY)
    return _compiled_ontology


# Port of compileOntology (label-ontology.js:44-70)
def _compile_ontology(raw):
    if not raw or not isinstance(raw, dict):
        raise ValueError("Invalid label ontology: expected object")
    if not raw.get("version") or not isinstance(raw.get("version"), str):
        raise ValueError("Invalid label ontology: missing version")
    if not isinstance(raw.get("labels"), list):
        raise ValueError("Invalid label ontology: labels must be an array")

    by_label = {}
    labels = [_compile_entry(entry, index) for index, entry in enumerate(raw["labels"])]
    for label in labels:
        if label["label"] in by_label:
            raise ValueError(f"Invalid label ontology: duplicate label {label['label']}")
        by_label[label["label"]] = label

    return {
        "version": raw["version"],
        "labels": labels,
        "byLabel": by_label,
        "llmAllowedLabels": [l for l in labels if l["llm_allowed"]],
    }


# Port of compileEntry (label-ontology.js:72-99)
def _compile_entry(entry, index):
    for field in ("label", "category", "subtype", "sensitivity"):
        if not entry.get(field) or not isinstance(entry.get(field), str):
            raise ValueError(f"Invalid label ontology entry at {index}: missing {field}")
    expected_label = f"{entry['category']}.{entry['subtype']}"
    if entry["label"] != expected_label:
        raise ValueError(f"Invalid label ontology entry {entry['label']}: expected {expected_label}")

    return {
        "label": entry["label"],
        "category": entry["category"],
        "subtype": entry["subtype"],
        "sensitivity": entry["sensitivity"],
        "patterns": _compile_patterns(entry.get("patterns"), entry["label"], "patterns"),
        "negative_patterns": _compile_patterns(entry.get("negative_patterns") or [], entry["label"], "negative_patterns"),
        "aliases": _normalize_string_array(entry.get("aliases")),
        "examples": _normalize_string_array(entry.get("examples")),
        "llm_allowed": bool(entry.get("llm_allowed")),
        "evidence_caps": {**DEFAULT_EVIDENCE_CAPS, **(entry.get("evidence_caps") or {})},
        "fallback": bool(entry.get("fallback")),
        "priority": _normalize_number(entry.get("priority"), 0),
        "supersedes": _normalize_string_array(entry.get("supersedes")),
        "source_refs": _normalize_string_array(entry.get("source_refs")),
    }


# Port of compilePatterns (label-ontology.js:101-112)
def _compile_patterns(patterns, label, field):
    if not isinstance(patterns, list):
        raise ValueError(f"Invalid label ontology entry {label}: {field} must be an array")
    compiled = []
    for index, pattern in enumerate(patterns):
        try:
            compiled.append(re.compile(pattern, re.IGNORECASE))
        except re.error as error:
            raise ValueError(f"Invalid regex for {label}.{field}[{index}]: {error}")
    return compiled


def _normalize_string_array(value):
    if isinstance(value, list):
        return [s for s in (str(item or "") for item in value) if s]
    return []


def _normalize_number(value, fallback):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return fallback
    if n != n or n in (float("inf"), float("-inf")):
        return fallback
    return int(n) if n.is_integer() else n


# Port of getOntologyVersion (label-ontology.js:123-125)
def get_ontology_version():
    return get_label_ontology()["version"]


# Port of getOntologyStats (label-ontology.js:127-134)
def get_ontology_stats():
    current = get_label_ontology()
    return {
        "label_ontology_version": current["version"],
        "label_ontology_label_count": len(current["labels"]),
        "label_ontology_llm_allowed_count": len(current["llmAllowedLabels"]),
    }


# Port of getLabelDefinition (label-ontology.js:136-138)
def get_label_definition(label):
    return get_label_ontology()["byLabel"].get(label)


# Port of getLabelSensitivity (label-ontology.js:140-144)
def get_label_sensitivity(label_or_category):
    definition = get_label_definition(label_or_category)
    if definition:
        return definition["sensitivity"]
    return DEFAULT_CATEGORY_SENSITIVITY.get(label_or_category, "low")


# Port of getEvidenceCap (label-ontology.js:146-150)
def get_evidence_cap(label_or_category, evidence_level):
    definition = get_label_definition(label_or_category)
    caps = (definition.get("evidence_caps") if definition else None) or DEFAULT_EVIDENCE_CAPS
    val = caps.get(evidence_level)
    if val is None:
        val = DEFAULT_EVIDENCE_CAPS.get(evidence_level)
    if val is None:
        val = DEFAULT_EVIDENCE_CAPS["L0"]
    return float(val)


# Port of getAllowedLlmLabelMap (label-ontology.js:152-158)
def get_allowed_llm_label_map():
    return {entry["label"]: entry for entry in get_label_ontology()["llmAllowedLabels"]}


# Port of listAllowedLlmLabels (label-ontology.js:160-170)
def list_allowed_llm_labels():
    return [{
        "label": entry["label"],
        "category": entry["category"],
        "subtype": entry["subtype"],
        "sensitivity": entry["sensitivity"],
        "aliases": entry["aliases"],
        "examples": entry["examples"],
        "fallback": entry["fallback"],
    } for entry in get_label_ontology()["llmAllowedLabels"]]


# Regex-match memoization. classify_ontology_text is pure in
# (normalized_text, include_fallback), and the 153-regex scan dominates cost on
# large graphs (00004: 400 nodes/1742 edges re-ran it per cycle-closure label
# slice → minutes). We cache ONLY the matched ontology entries (the expensive
# part); the output dicts are rebuilt fresh every call so the caller-mutation
# contract is unchanged. Entries themselves come from the immutable ontology.
_ONTOLOGY_MATCH_CACHE = {}


# Port of classifyOntologyText (label-ontology.js:172-196)
def classify_ontology_text(text, options=None):
    options = options or {}
    normalized = normalize_security_text(text)
    if not normalized:
        return []
    include_fallback = options.get("includeFallback") is True or options.get("includeGeneric") is True
    include_suppressed = bool(options.get("includeSuppressedFallbacks"))

    cache_key = (normalized, include_fallback, include_suppressed)
    matches = _ONTOLOGY_MATCH_CACHE.get(cache_key)
    if matches is None:
        raw = []
        for entry in get_label_ontology()["labels"]:
            if not include_fallback and entry["fallback"]:
                continue
            if not any(pattern.search(normalized) for pattern in entry["patterns"]):
                continue
            if any(pattern.search(normalized) for pattern in entry["negative_patterns"]):
                continue
            raw.append(entry)
        matches = _apply_match_post_processing(raw, include_fallback, include_suppressed)
        _ONTOLOGY_MATCH_CACHE[cache_key] = matches
    return [{
        "label": entry["label"],
        "category": entry["category"],
        "subtype": entry["subtype"],
        "sensitivity": entry["sensitivity"],
        "ontology_version": get_ontology_version(),
        "ontology_label_id": entry["label"],
        "fallback": entry["fallback"],
        "priority": entry["priority"],
    } for entry in matches]


# Port of applyMatchPostProcessing (label-ontology.js:198-220)
def _apply_match_post_processing(matches, include_fallback, include_suppressed_fallbacks):
    import functools
    output = list(matches)
    if (not include_fallback or not include_suppressed_fallbacks) and any(not e["fallback"] for e in output):
        output = [e for e in output if not e["fallback"]]

    superseded = set()
    for entry in output:
        for label in entry.get("supersedes") or []:
            superseded.add(label)
    output = [e for e in output if e["label"] not in superseded]

    def cmp(a, b):
        priority_delta = _num(b.get("priority")) - _num(a.get("priority"))
        if priority_delta != 0:
            return -1 if priority_delta < 0 else 1
        sensitivity_delta = _sensitivity_rank(b["sensitivity"]) - _sensitivity_rank(a["sensitivity"])
        if sensitivity_delta != 0:
            return sensitivity_delta
        return _locale_compare(a["label"], b["label"])

    output.sort(key=functools.cmp_to_key(cmp))
    return output


# Port of sensitivityRank (label-ontology.js:222-225)
def _sensitivity_rank(sensitivity):
    return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(sensitivity, 1)


# Port of normalizeSecurityText (label-ontology.js:227-231)
def normalize_security_text(text):
    s = str(text or "")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"[._/-]+", " ", s)
    return s


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)
