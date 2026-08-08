"""Port of src/security/data-labeler.js — buildDataProfile.

Assigns ontology-driven sensitivity labels to a node from its schema fields,
formal targets, instruction text, produced-artifact evidence, and name/data-type,
then dedupes + ranks them. Label ids are `label_<sha1[:12]>` over a fixed field
join — byte-identical to JS. roundConfidence uses JS Math.round (round half toward
+Inf via _js_round). Only buildDataProfile is on the M1e critical path (the
profiler calls it when a node has the data_introduction role); the derived/
synthetic-label helpers are ported for completeness and the flood layer (M3).
"""

import functools
import hashlib

from .label_ontology import (
    DEFAULT_EVIDENCE_CAPS,
    classify_ontology_text,
    get_evidence_cap,
    get_label_sensitivity,
    get_ontology_version,
    get_ontology_stats,
    get_label_definition,
    normalize_security_text,
)
from ..llm.normalizers import js_round

EVIDENCE_CONFIDENCE = DEFAULT_EVIDENCE_CAPS


# Port of buildDataProfile (data-labeler.js:15-78)
def build_data_profile(node=None, source_info=None):
    node = node or {}
    source_info = source_info or {}
    labels = []
    origin_node = source_info.get("node_id") or node.get("id") or ""
    origin_node_name = node.get("canonical_name") or node.get("name") or source_info.get("node_name") or origin_node

    if is_user_query_node(node):
        labels.append(create_label({
            "category": "user_prompt",
            "subtype": "query",
            "fieldName": "query_text",
            "fieldPath": "signature.output.query_text",
            "originNode": origin_node,
            "originNodeName": origin_node_name,
            "evidenceLevel": "L4",
            "evidenceKind": "builtin_user_query",
            "evidenceText": node.get("canonical_name") or node.get("name") or "user.query",
        }))

    if is_produced_artifact_node(node):
        add_labels_from_produced_artifact(labels, node, origin_node, origin_node_name)

    add_labels_from_fields(labels, collect_schema_fields(get_signature_output(node), "signature.output"), origin_node, origin_node_name, "output_field", "L4")
    if not is_produced_artifact_node(node):
        add_labels_from_fields(labels, collect_schema_fields(get_signature_input(node), "signature.input"), origin_node, origin_node_name, "input_field", "L4")
    add_labels_from_targets(labels, (node.get("formal_semantics") or {}).get("targets"), origin_node, origin_node_name)
    if not is_produced_artifact_node(node):
        add_labels_from_instruction(labels, collect_instruction_text(node), origin_node, origin_node_name)
    add_labels_from_text(labels, " ".join(
        str(p) for p in [source_info.get("data_type"), source_info.get("reason"), node.get("canonical_name"), node.get("name"), node.get("description")] if p
    ), {
        "originNode": origin_node,
        "originNodeName": origin_node_name,
        "fieldName": "",
        "fieldPath": "",
        "evidenceLevel": "L1",
        "evidenceKind": "name_or_data_type",
    })

    deduped = dedupe_labels(labels)
    if len(deduped) > 0:
        final_labels = deduped
    else:
        final_labels = [create_label({
            "category": "generic_data",
            "subtype": "data",
            "fieldName": "data",
            "fieldPath": "",
            "originNode": origin_node,
            "originNodeName": origin_node_name,
            "evidenceLevel": "L0",
            "evidenceKind": "fallback",
            "evidenceText": source_info.get("data_type") or node.get("canonical_name") or node.get("name") or "data",
        })]

    primary_category = choose_primary_category(final_labels)
    return {
        "primary_category": primary_category,
        "sensitivity": max_sensitivity(final_labels),
        "labels": final_labels,
        "alternatives": [],
        "unknown_tail": any(l["evidence_level"] == "L0" or l["label"] == "generic_data.data" for l in final_labels),
    }


# Port of isProducedArtifactNode (data-labeler.js:80-82)
def is_produced_artifact_node(node=None):
    node = node or {}
    return str((node.get("formal_semantics") or {}).get("operation_type") or node.get("operationType") or "").lower() == "produce_artifact"


# Port of addLabelsFromProducedArtifact (data-labeler.js:84-101)
def add_labels_from_produced_artifact(labels, node, origin_node, origin_node_name):
    fs = node.get("formal_semantics") or {}
    evidence = fs.get("evidence") or {}
    parts = [evidence.get("produced_object_text"), evidence.get("produced_object_key")]
    parts += [" ".join(x for x in (o.get("name"), o.get("type")) if x) for o in (fs.get("outputs") or [])]
    parts += [" ".join(x for x in (t.get("type"), t.get("value"), t.get("raw")) if x) for t in (fs.get("targets") or [])]
    produced_text = " ".join(p for p in parts if p)

    add_labels_from_text(labels, produced_text, {
        "originNode": origin_node,
        "originNodeName": origin_node_name,
        "fieldName": str(evidence.get("produced_object_text") or evidence.get("produced_object_key") or "artifact"),
        "fieldPath": "formal_semantics.produced_object",
        "evidenceLevel": "L3",
        "evidenceKind": "produced_artifact",
    })


# Port of classifyTextLabels (data-labeler.js:103-105)
def classify_text_labels(text, options=None):
    return classify_ontology_text(text, options or {})


# Port of createDerivedLabel (data-labeler.js:107-124)
def create_derived_label(config):
    from_label = config.get("fromLabel") or {}
    origin_node = from_label.get("origin_node") or ""
    origin_node_name = from_label.get("origin_node_name") or origin_node
    return create_label({
        "category": config.get("category"),
        "subtype": config.get("subtype"),
        "fieldName": config.get("fieldName") or config.get("subtype"),
        "fieldPath": config.get("fieldPath") or "",
        "originNode": origin_node,
        "originNodeName": origin_node_name,
        "introducedAt": config.get("introducedAt"),
        "mode": "derived",
        "confidence": config.get("confidence") or min(0.8, _num(from_label.get("confidence") or 0.7)),
        "evidenceLevel": "L2",
        "evidenceKind": "semantic_derivation",
        "evidenceText": config.get("evidenceText"),
    })


# Port of createSyntheticLabel (data-labeler.js:126-141)
def create_synthetic_label(config):
    return create_label({
        "category": config.get("category"),
        "subtype": config.get("subtype"),
        "fieldName": config.get("subtype") or config.get("category"),
        "fieldPath": "",
        "originNode": config.get("originNode"),
        "originNodeName": config.get("originNodeName"),
        "introducedAt": config.get("introducedAt"),
        "mode": "derived",
        "confidence": config.get("confidence") or EVIDENCE_CONFIDENCE["L2"],
        "evidenceLevel": "L2",
        "evidenceKind": config.get("evidenceKind") or "synthetic_transfer",
        "evidenceText": config.get("evidenceText") or "",
    })


# Port of maxSensitivity (data-labeler.js:143-153)
def max_sensitivity(labels_or_categories):
    rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    selected = "low"
    for item in labels_or_categories or []:
        if isinstance(item, str):
            sensitivity = get_label_sensitivity(item)
        else:
            sensitivity = get_label_sensitivity((item or {}).get("label") or (item or {}).get("category") or "")
        if rank.get(sensitivity, 0) > rank[selected]:
            selected = sensitivity
    return selected


# Port of addLabelsFromFields (data-labeler.js:155-167)
def add_labels_from_fields(labels, fields, origin_node, origin_node_name, evidence_kind, evidence_level):
    for field in fields:
        text = " ".join(x for x in (field.get("name"), field.get("path"), field.get("type"), field.get("description")) if x)
        add_labels_from_text(labels, text, {
            "originNode": origin_node,
            "originNodeName": origin_node_name,
            "fieldName": field.get("name"),
            "fieldPath": field.get("path"),
            "evidenceLevel": evidence_level,
            "evidenceKind": evidence_kind,
        })


# Port of addLabelsFromTargets (data-labeler.js:169-181)
def add_labels_from_targets(labels, targets, origin_node, origin_node_name):
    for target in (targets if isinstance(targets, list) else []):
        text = ":".join(x for x in (target.get("type"), target.get("value"), target.get("raw")) if x)
        add_labels_from_text(labels, text, {
            "originNode": origin_node,
            "originNodeName": origin_node_name,
            "fieldName": str(target.get("value") or target.get("raw") or target.get("type") or ""),
            "fieldPath": f"formal_semantics.targets.{str(target.get('type') or 'target')}",
            "evidenceLevel": "L3",
            "evidenceKind": "formal_target",
        })


# Port of addLabelsFromInstruction (data-labeler.js:183-192)
def add_labels_from_instruction(labels, instruction, origin_node, origin_node_name):
    add_labels_from_text(labels, instruction, {
        "originNode": origin_node,
        "originNodeName": origin_node_name,
        "fieldName": "",
        "fieldPath": "instruction",
        "evidenceLevel": "L2",
        "evidenceKind": "instruction_text",
    })


# Port of addLabelsFromText (data-labeler.js:194-208)
def add_labels_from_text(labels, text, context):
    for match in classify_text_labels(text):
        labels.append(create_label({
            **match,
            "fieldName": context.get("fieldName"),
            "fieldPath": context.get("fieldPath"),
            "originNode": context.get("originNode"),
            "originNodeName": context.get("originNodeName"),
            "evidenceLevel": context.get("evidenceLevel"),
            "evidenceKind": context.get("evidenceKind"),
            "evidenceText": text,
        }))


# Port of createLabel (data-labeler.js:210-265)
def create_label(config):
    category = config.get("category")
    subtype = config.get("subtype")
    field_name = config.get("fieldName", "")
    field_path = config.get("fieldPath", "")
    origin_node = config.get("originNode", "")
    origin_node_name = config.get("originNodeName", "")
    introduced_at = config.get("introducedAt", origin_node)
    mode = config.get("mode", "definite")
    confidence = config.get("confidence")
    evidence_level = config.get("evidenceLevel", "L0")
    evidence_kind = config.get("evidenceKind", "fallback")
    evidence_text = config.get("evidenceText", "")
    requires_review = config.get("requiresReview", False)
    llm_review = config.get("llmReview")
    uncertainty = config.get("uncertainty", "")
    reason = config.get("reason", "")
    ontology_version = config.get("ontologyVersion", get_ontology_version())
    ontology_label_id = config.get("ontologyLabelId", "")

    label = f"{category}.{subtype or 'data'}"
    definition = get_label_definition(label)
    value = {
        "id": "",
        "label": label,
        "category": category,
        "subtype": subtype or "data",
        "sensitivity": (definition.get("sensitivity") if definition else None) or get_label_sensitivity(label),
        "field_name": str(field_name or subtype or category or ""),
        "field_path": str(field_path or ""),
        "origin_node": origin_node,
        "origin_node_name": origin_node_name or origin_node,
        "introduced_at": introduced_at or origin_node,
        "mode": mode,
        "confidence": round_confidence(confidence if confidence is not None else get_evidence_cap(label, evidence_level)),
        "evidence_level": evidence_level,
        "evidence_kind": evidence_kind,
        "evidence_text": str(evidence_text or "")[:300],
        "ontology_version": ontology_version,
        "ontology_label_id": ontology_label_id or (definition.get("label") if definition else None) or label,
    }
    if requires_review:
        value["requires_review"] = True
    if llm_review and isinstance(llm_review, dict):
        value["llm_review"] = llm_review
    if uncertainty:
        value["uncertainty"] = str(uncertainty or "")[:200]
    if reason:
        value["reason"] = str(reason or "")[:240]
    value["id"] = "label_" + short_hash("|".join([
        value["ontology_version"],
        value["label"],
        value["field_name"],
        value["field_path"],
        value["origin_node"],
        value["introduced_at"],
        value["evidence_kind"],
    ]))
    return value


# Port of dedupeLabels (data-labeler.js:267-291)
def dedupe_labels(labels):
    by_key = {}
    for label in labels:
        key = "|".join([
            label["label"],
            normalize_field_name(label["field_name"]),
            label["field_path"],
            label["origin_node"],
            label["introduced_at"],
        ])
        existing = by_key.get(key)
        if not existing or evidence_rank(label["evidence_level"]) > evidence_rank(existing["evidence_level"]):
            by_key[key] = label

    def cmp(a, b):
        sensitivity_delta = _sensitivity_rank(b.get("label") or b.get("category")) - _sensitivity_rank(a.get("label") or a.get("category"))
        if sensitivity_delta != 0:
            return sensitivity_delta
        evidence_delta = evidence_rank(b["evidence_level"]) - evidence_rank(a["evidence_level"])
        if evidence_delta != 0:
            return evidence_delta
        return _locale_compare(a["label"], b["label"])

    return sorted(by_key.values(), key=functools.cmp_to_key(cmp))[:24]


# Port of choosePrimaryCategory (data-labeler.js:293-302)
def choose_primary_category(labels):
    if not isinstance(labels, list) or len(labels) == 0:
        return "generic_data"

    def cmp(a, b):
        sensitivity_delta = _sensitivity_rank(b.get("label") or b.get("category")) - _sensitivity_rank(a.get("label") or a.get("category"))
        if sensitivity_delta != 0:
            return sensitivity_delta
        confidence_delta = _num(b.get("confidence")) - _num(a.get("confidence"))
        if confidence_delta != 0:
            return -1 if confidence_delta < 0 else 1
        return _locale_compare(a["label"], b["label"])

    return sorted(labels, key=functools.cmp_to_key(cmp))[0]["category"]


# Port of collectSchemaFields (data-labeler.js:304-322)
def collect_schema_fields(schema=None, prefix=""):
    schema = schema or {}
    fields = []
    for name, spec in schema.items():
        path = f"{prefix}.{name}" if prefix else name
        is_obj = isinstance(spec, dict) and spec
        field = {
            "name": name,
            "path": path,
            "type": (spec.get("type") or "") if is_obj else str(spec or ""),
            "description": (spec.get("description") or "") if is_obj else "",
        }
        fields.append(field)
        properties = spec.get("properties") if is_obj else None
        if properties and isinstance(properties, dict):
            fields.extend(collect_schema_fields(properties, path))
    return fields


# Port of collectInstructionText (data-labeler.js:324-335)
def collect_instruction_text(node=None):
    node = node or {}
    semantics = node.get("formal_semantics") or {}
    if isinstance(node.get("member_steps"), list):
        member_steps = " ".join(str(s.get("instruction") or s.get("text") or "") for s in node["member_steps"])
    else:
        member_steps = ""
    effects = semantics.get("effects")
    parts = [
        node.get("instructionText"),
        (semantics.get("evidence") or {}).get("text"),
        " ".join(effects) if isinstance(effects, list) else "",
        member_steps,
    ]
    return " ".join(p for p in parts if p)


# Port of getSignatureInput (data-labeler.js:337-339)
def get_signature_input(node=None):
    node = node or {}
    return (node.get("signature") or {}).get("input") or node.get("input") or {}


# Port of getSignatureOutput (data-labeler.js:341-343)
def get_signature_output(node=None):
    node = node or {}
    return (node.get("signature") or {}).get("output") or node.get("output") or {}


# Port of isUserQueryNode (data-labeler.js:345-347)
def is_user_query_node(node=None):
    node = node or {}
    return str(node.get("name") or "").lower() == "user.query"


# Port of normalizeFieldName (data-labeler.js:349-351)
def normalize_field_name(value):
    import re
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower())


# Port of evidenceRank (data-labeler.js:353-356)
def evidence_rank(level):
    return {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}.get(level, 0)


# Port of sensitivityRank (data-labeler.js:358-361)
def _sensitivity_rank(label_or_category):
    return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(get_label_sensitivity(label_or_category), 1)


# Port of roundConfidence (data-labeler.js:363-367)
def round_confidence(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return EVIDENCE_CONFIDENCE["L0"]
    if n != n or n in (float("inf"), float("-inf")):
        return EVIDENCE_CONFIDENCE["L0"]
    return max(0, min(1, js_round(n * 1000) / 1000))


# Port of shortHash (data-labeler.js:369-371)
def short_hash(value):
    return hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:12]


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)
