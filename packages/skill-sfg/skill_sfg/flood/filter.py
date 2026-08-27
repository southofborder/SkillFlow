"""Port of src/security/flow-instance-filter.js.

ZERO structural change from the JS. The event ``type`` strings are load-bearing:
they feed transform_digest / transform_sig on the flood side and DOE's
transform_seq on the consumer side, so they are byte-identical to the JS.

The single sharp edge is buildResult's ``event_id`` (flow-instance-filter.js:412):

    filter_${shortHash([event.type, event.node_id, JSON.stringify(event)].join('|'))}

which folds a full ``JSON.stringify`` of the event into a sha1 hash. That JSON MUST
be byte-identical to Node or the id changes and the FCG↔DOE join keyed on
``local_filter_event_ids`` silently breaks — see util/js_json.py, verified
byte-identical to Node.

The event objects here are built with keys in the SAME insertion order as the JS
object literals so JSON.stringify emits identical bytes. Any JS field that would be
``undefined`` (never happens in these literals) is simply not inserted.
"""

from ..security.data_labeler import (
    classify_text_labels,
    create_derived_label,
    create_synthetic_label,
    round_confidence,
    short_hash,
)
from ..util.js_json import js_json_stringify

import re


def apply_label_flow_filter(label_flow=None, current_profile=None, edge=None):
    """Port of applyLabelFlowFilter (flow-instance-filter.js:8-278)."""
    label_flow = label_flow or {}
    current_profile = current_profile or {}
    edge = edge or {}

    profile_tags = set(current_profile.get("operation_tags") or [])
    input_label = clone_label(label_flow.get("label"))
    events = []
    next_trigger_context = list(label_flow.get("trigger_context") or [])
    source_intro_applied_nodes = list(label_flow.get("source_intro_applied_nodes") or [])
    flow_mode = label_flow.get("flow_mode") or "may_flow"
    confidence_multiplier = 1

    if not input_label:
        return build_result(
            branches=[], events=events,
            source_intro_applied_nodes=source_intro_applied_nodes,
            terminated=True, termination_reason="filtered_out",
        )

    node_id = current_profile.get("node_id")
    node_name = current_profile.get("node_name")

    if is_produced_artifact_profile(current_profile):
        key = f"artifact:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "artifact_production",
            "node_id": node_id,
            "node_name": node_name,
            "from_label": compact_label(input_label),
            "produced_object_key": current_profile.get("produced_object_key") or "",
            "produced_object_text": current_profile.get("produced_object_text") or "",
            "evidence": filter_evidence(current_profile, edge),
        })
        return build_result(
            branches=[{
                "label": input_label,
                "flow_mode": "may_flow" if flow_mode == "source_introduction" else flow_mode,
                "confidence_multiplier": 0.95,
                "trigger_context": next_trigger_context,
                "source_intro_applied_nodes": source_intro_applied_nodes,
                "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                "filter_event_keys": [key],
            }],
            events=events,
            source_intro_applied_nodes=source_intro_applied_nodes,
        )

    if should_introduce_source(current_profile, label_flow):
        introduced = compact_labels((current_profile.get("data_profile") or {}).get("labels") or [])
        merge_trigger_context_into(
            next_trigger_context,
            label_to_trigger_context(input_label, "upstream_context_triggers_source_introduction"),
        )
        if node_id not in source_intro_applied_nodes:
            source_intro_applied_nodes.append(node_id)
        branches = []
        for label in introduced:
            key = f"source:{node_id}:{label.get('label')}:{label.get('origin_node')}:{label.get('introduced_at')}"
            events.append({
                "local_event_key": key,
                "type": "source_introduction",
                "node_id": node_id,
                "node_name": node_name,
                "introduced_label": compact_label(label),
                "introduced_labels": [compact_label(label)],
                "context_label": compact_label(input_label),
                "evidence": "data_introduction node emits its own data label",
            })
            branches.append({
                "label": label,
                "flow_mode": "source_introduction",
                "confidence_multiplier": 1,
                "trigger_context": next_trigger_context,
                "source_intro_applied_nodes": source_intro_applied_nodes,
                "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                "filter_event_keys": [key],
            })
        return build_result(branches=branches, events=events,
                            source_intro_applied_nodes=source_intro_applied_nodes)

    if "redaction" in profile_tags and should_redact_label(input_label, current_profile):
        key = f"redact:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "redact_drop",
            "node_id": node_id,
            "node_name": node_name,
            "dropped_label": compact_label(input_label),
            "dropped_labels": [compact_label(input_label)],
            "evidence": filter_evidence(current_profile, edge),
        })
        return build_result(branches=[], events=events,
                            source_intro_applied_nodes=source_intro_applied_nodes,
                            terminated=True, termination_reason="filtered_out")

    if "aggregation" in profile_tags:
        aggregate = create_summary_label(input_label, current_profile, edge, "aggregate")
        key = f"aggregate:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "aggregate",
            "node_id": node_id,
            "node_name": node_name,
            "from_label": compact_label(input_label),
            "introduced_label": compact_label(aggregate),
            "introduced_labels": [compact_label(aggregate)],
            "dropped_label": compact_label(input_label),
            "dropped_labels": [compact_label(input_label)],
            "evidence": filter_evidence(current_profile, edge),
        })
        return build_result(
            branches=[{
                "label": aggregate,
                "flow_mode": "derived_flow",
                "confidence_multiplier": 1,
                "trigger_context": next_trigger_context,
                "source_intro_applied_nodes": source_intro_applied_nodes,
                "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                "filter_event_keys": [key],
            }],
            events=events, source_intro_applied_nodes=source_intro_applied_nodes,
        )

    if "summarization" in profile_tags and not should_preserve_raw_after_summary(current_profile, edge):
        summary = create_summary_label(input_label, current_profile, edge, "summarization")
        key = f"summary:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "summarization",
            "node_id": node_id,
            "node_name": node_name,
            "from_label": compact_label(input_label),
            "introduced_label": compact_label(summary),
            "introduced_labels": [compact_label(summary)],
            "dropped_label": compact_label(input_label),
            "dropped_labels": [compact_label(input_label)],
            "evidence": filter_evidence(current_profile, edge),
        })
        return build_result(
            branches=[{
                "label": summary,
                "flow_mode": "derived_flow",
                "confidence_multiplier": 1,
                "trigger_context": next_trigger_context,
                "source_intro_applied_nodes": source_intro_applied_nodes,
                "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                "filter_event_keys": [key],
            }],
            events=events, source_intro_applied_nodes=source_intro_applied_nodes,
        )

    if "pseudonymization" in profile_tags:
        pseudo = create_synthetic_label({
            "category": "pseudonymous_data",
            "subtype": "protected",
            "originNode": input_label.get("origin_node") or node_id,
            "originNodeName": input_label.get("origin_node_name") or node_name or node_id,
            "introducedAt": node_id,
            "evidenceKind": "pseudonymize",
            "evidenceText": filter_evidence(current_profile, edge),
            "confidence": min(0.8, _num(input_label.get("confidence") or 0.7)),
        })
        key = f"pseudonymize:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "pseudonymize",
            "node_id": node_id,
            "node_name": node_name,
            "from_label": compact_label(input_label),
            "introduced_label": compact_label(pseudo),
            "introduced_labels": [compact_label(pseudo)],
            "evidence": filter_evidence(current_profile, edge),
        })
        return build_result(
            branches=[{
                "label": pseudo,
                "flow_mode": "derived_flow",
                "confidence_multiplier": 1,
                "trigger_context": next_trigger_context,
                "source_intro_applied_nodes": source_intro_applied_nodes,
                "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                "filter_event_keys": [key],
            }],
            events=events, source_intro_applied_nodes=source_intro_applied_nodes,
        )

    if "semantic_extraction" in profile_tags:
        derived = derive_semantic_labels(input_label, current_profile, edge)
        if len(derived) > 0:
            branches = []
            for label in derived:
                key = f"derive:{node_id}:{input_label.get('label')}:{label.get('label')}"
                events.append({
                    "local_event_key": key,
                    "type": "semantic_derivation",
                    "node_id": node_id,
                    "node_name": node_name,
                    "from_label": compact_label(input_label),
                    "introduced_label": compact_label(label),
                    "introduced_labels": [compact_label(label)],
                    "evidence": filter_evidence(current_profile, edge),
                })
                branches.append({
                    "label": label,
                    "flow_mode": "derived_flow",
                    "confidence_multiplier": 1,
                    "trigger_context": merge_trigger_contexts(
                        next_trigger_context,
                        label_to_trigger_context(input_label, "semantic_extraction_source_context"),
                    ),
                    "source_intro_applied_nodes": source_intro_applied_nodes,
                    "parent_label_flow_ids": [label_flow.get("label_flow_id")],
                    "filter_event_keys": [key],
                })
            return build_result(branches=branches, events=events,
                                source_intro_applied_nodes=source_intro_applied_nodes)

    if "field_slice" in profile_tags:
        result = slice_label(input_label, current_profile, edge)
        if result["applied"] and not result["keep"]:
            key = f"slice_drop:{node_id}:{input_label.get('label')}"
            events.append({
                "local_event_key": key,
                "type": "field_slice_drop",
                "node_id": node_id,
                "node_name": node_name,
                "dropped_label": compact_label(input_label),
                "dropped_labels": [compact_label(input_label)],
                "evidence": result["evidence"],
            })
            return build_result(branches=[], events=events,
                                source_intro_applied_nodes=source_intro_applied_nodes)
        if result["applied"] and result["keep"]:
            key = f"slice_keep:{node_id}:{input_label.get('label')}"
            events.append({
                "local_event_key": key,
                "type": "field_slice_keep",
                "node_id": node_id,
                "node_name": node_name,
                "kept_label": compact_label(input_label),
                "kept_labels": [compact_label(input_label)],
                "evidence": result["evidence"],
            })
            flow_mode = "definite_flow"

    if len(events) == 0:
        confidence_multiplier = 0.95
        key = f"unknown:{node_id}:{input_label.get('label')}"
        events.append({
            "local_event_key": key,
            "type": "unknown_may_flow",
            "node_id": node_id,
            "node_name": node_name,
            "propagated_label": compact_label(input_label),
            "propagated_labels": [compact_label(input_label)],
            "evidence": filter_evidence(current_profile, edge),
        })
        if flow_mode != "derived_flow":
            flow_mode = "may_flow"

    return build_result(
        branches=[{
            "label": input_label,
            "flow_mode": flow_mode,
            "confidence_multiplier": confidence_multiplier,
            "trigger_context": next_trigger_context,
            "source_intro_applied_nodes": source_intro_applied_nodes,
            "parent_label_flow_ids": [label_flow.get("label_flow_id")],
            "filter_event_keys": [event["local_event_key"] for event in events],
        }],
        events=events, source_intro_applied_nodes=source_intro_applied_nodes,
    )


# Port of shouldIntroduceSource (flow-instance-filter.js:280-286)
def should_introduce_source(profile=None, label_flow=None):
    profile = profile or {}
    label_flow = label_flow or {}
    if "data_introduction" not in (profile.get("node_roles") or []):
        return False
    if is_produced_artifact_profile(profile):
        return False
    if is_pure_control_source(profile):
        return False
    if profile.get("node_id") in (label_flow.get("source_intro_applied_nodes") or []):
        return False
    return len((profile.get("data_profile") or {}).get("labels") or []) > 0


# Port of isProducedArtifactProfile (flow-instance-filter.js:288-292)
def is_produced_artifact_profile(profile=None):
    profile = profile or {}
    if profile.get("operation_type") == "produce_artifact":
        return True
    if any(item.get("kind") == "formal_semantics.produce_artifact"
           for item in (profile.get("evidence") or [])):
        return True
    if any(step.get("operation_type") == "produce_artifact"
           for step in (profile.get("action_steps") or [])):
        return True
    return False


# Port of isPureControlSource (flow-instance-filter.js:294-298)
def is_pure_control_source(profile=None):
    profile = profile or {}
    labels = (profile.get("data_profile") or {}).get("labels") or []
    only_prompt = len(labels) > 0 and all(label.get("category") == "user_prompt" for label in labels)
    return "control_context" in (profile.get("node_roles") or []) and only_prompt


# Port of deriveSemanticLabels (flow-instance-filter.js:300-316)
def derive_semantic_labels(label, profile, edge):
    text = filter_evidence(profile, edge)
    matches = [m for m in classify_text_labels(text)
               if m.get("category") not in ("user_prompt", "generic_data")]
    if len(matches) == 0 or label.get("category") != "user_prompt":
        return []
    derived = [create_derived_label({
        "fromLabel": label,
        "category": m.get("category"),
        "subtype": m.get("subtype"),
        "fieldName": m.get("subtype"),
        "fieldPath": "",
        "introducedAt": profile.get("node_id"),
        "evidenceText": text,
        "confidence": min(0.8, _num(label.get("confidence") or 0.7)),
    }) for m in matches]
    return dedupe_labels(derived)


# Port of sliceLabel (flow-instance-filter.js:318-327)
def slice_label(label, profile, edge):
    text = slice_intent_text(profile, edge)
    matches = [m for m in classify_text_labels(text)
               if m.get("category") not in ("user_prompt", "generic_data")]
    if len(matches) == 0:
        return {"applied": False, "keep": True, "evidence": text}
    return {
        "applied": True,
        "keep": any(labels_match(label, m) for m in matches),
        "evidence": text,
    }


# Port of shouldRedactLabel (flow-instance-filter.js:329-347)
def should_redact_label(label, profile):
    text = filter_evidence(profile, None)
    matches = [m for m in classify_text_labels(text) if m.get("category") != "user_prompt"]
    redacts_specific_pii = bool(re.search(r"(email|phone|address|profile|pii|personal)", text, re.IGNORECASE))
    specific_pii_subtype = specific_pii_redaction_subtype(text)
    credential_redaction = bool(re.search(
        r"secret|credential|api[_\-\s]?key|token|password|private[_\-\s]?key", text, re.IGNORECASE))
    pii_redaction = redacts_specific_pii
    if credential_redaction and label.get("category") == "credentials":
        return True
    if specific_pii_subtype:
        return label.get("category") == "pii" and label.get("subtype") == specific_pii_subtype
    if pii_redaction and label.get("category") == "pii":
        return True
    if len(matches) == 0:
        return label.get("category") == "credentials"
    if re.search(r"redact|mask|sanitize|scrub|strip|remove", text, re.IGNORECASE) and all(
            m.get("category") in ("file_content", "generic_data") for m in matches):
        return label.get("category") == "credentials"
    if re.search(r"redact|mask|sanitize|scrub|strip|remove", text, re.IGNORECASE) \
            and not redacts_specific_pii and label.get("category") != "credentials":
        return False
    return any(label.get("category") == m.get("category") or labels_match(label, m) for m in matches)


# Port of createSummaryLabel (flow-instance-filter.js:349-360)
def create_summary_label(input_label, current_profile, edge, evidence_kind):
    return create_synthetic_label({
        "category": "aggregate_data",
        "subtype": "summary",
        "originNode": input_label.get("origin_node") or current_profile.get("node_id"),
        "originNodeName": input_label.get("origin_node_name")
        or current_profile.get("node_name") or current_profile.get("node_id"),
        "introducedAt": current_profile.get("node_id"),
        "evidenceKind": evidence_kind,
        "evidenceText": filter_evidence(current_profile, edge),
        "confidence": min(0.75, _num(input_label.get("confidence") or 0.7)),
    })


# Port of shouldPreserveRawAfterSummary (flow-instance-filter.js:362-365)
def should_preserve_raw_after_summary(profile=None, edge=None):
    text = filter_evidence(profile or {}, edge or {})
    return bool(re.search(r"\b(raw|original|full|verbatim|complete|unmodified)\b", text, re.IGNORECASE))


# Port of specificPiiRedactionSubtype (flow-instance-filter.js:367-374)
def specific_pii_redaction_subtype(text=""):
    value = str(text or "")
    if re.search(r"(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(email|mail)|redactEmail|maskEmail|removeEmail", value, re.IGNORECASE):
        return "email"
    if re.search(r"(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(phone|mobile)|redactPhone|maskPhone|removePhone", value, re.IGNORECASE):
        return "phone"
    if re.search(r"(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(address)|redactAddress|maskAddress|removeAddress", value, re.IGNORECASE):
        return "address"
    if re.search(r"(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(profile)|redactProfile|maskProfile|removeProfile", value, re.IGNORECASE):
        return "profile"
    return ""


# Port of labelsMatch (flow-instance-filter.js:376-380)
def labels_match(label, match):
    if not label or not match:
        return False
    if label.get("label") == match.get("label"):
        return True
    return label.get("category") == match.get("category") and (
        not match.get("subtype") or label.get("subtype") == match.get("subtype"))


# Port of filterEvidence (flow-instance-filter.js:382-393)
def filter_evidence(profile=None, edge=None):
    profile = profile or {}
    edge = edge or {}
    df = edge.get("data_flow") or {}
    security_tags = profile.get("security_tags")
    operation_tags = profile.get("operation_tags")
    evidence = profile.get("evidence")
    parts = [
        profile.get("node_name"),
        " ".join(security_tags) if security_tags else None,
        " ".join(operation_tags) if operation_tags else None,
        " ".join(item.get("text") or "" for item in evidence) if evidence else None,
        df.get("from_param"),
        df.get("to_param"),
        df.get("data_type"),
        edge.get("semantic_reason"),
    ]
    return " ".join(str(p) for p in parts if p)


# Port of sliceIntentText (flow-instance-filter.js:395-404)
def slice_intent_text(profile=None, edge=None):
    profile = profile or {}
    edge = edge or {}
    df = edge.get("data_flow") or {}
    evidence = profile.get("evidence")
    parts = [
        profile.get("node_name"),
        " ".join(item.get("text") or "" for item in evidence) if evidence else None,
        df.get("from_param"),
        df.get("to_param"),
        df.get("data_type"),
        edge.get("semantic_reason"),
    ]
    return " ".join(str(p) for p in parts if p)


# Port of buildResult (flow-instance-filter.js:406-417).
# event_id folds a full JSON.stringify of the event into a sha1 — MUST be
# byte-identical to Node (see util/js_json.py). The ``...event`` spread means the
# event's own keys follow event_id in the emitted object; we preserve that order.
def build_result(branches=None, events=None, source_intro_applied_nodes=None,
                 terminated=False, termination_reason=""):
    filter_events = []
    for event in (events or []):
        event_id = "filter_" + short_hash(
            "|".join([event["type"], str(event["node_id"]), js_json_stringify(event)]))
        # {event_id, ...event} — event_id first, then the event's own keys in order.
        merged = {"event_id": event_id}
        merged.update(event)
        filter_events.append(merged)
    return {
        "branches": branches or [],
        "terminated": terminated,
        "termination_reason": termination_reason,
        "filter_events": filter_events,
        "source_intro_applied_nodes": source_intro_applied_nodes or [],
    }


# Port of labelToTriggerContext (flow-instance-filter.js:419-427)
def label_to_trigger_context(label, reason):
    node_id = (label or {}).get("origin_node") or ""
    if not node_id:
        return []
    return [{
        "node_id": node_id,
        "node_name": label.get("origin_node_name") or node_id,
        "reason": reason,
    }]


# Port of mergeTriggerContextInto (flow-instance-filter.js:429-437)
def merge_trigger_context_into(target, additions):
    seen = {item.get("node_id") or item.get("node_name")
            for item in target if (item.get("node_id") or item.get("node_name"))}
    for item in (additions or []):
        key = item.get("node_id") or item.get("node_name")
        if not key or key in seen:
            continue
        seen.add(key)
        target.append(item)


# Port of mergeTriggerContexts (flow-instance-filter.js:439-443)
def merge_trigger_contexts(a=None, b=None):
    result = list(a or [])
    merge_trigger_context_into(result, b or [])
    return result


# Port of compactLabels (flow-instance-filter.js:445-447)
def compact_labels(labels):
    return [compact_label(label) for label in dedupe_labels(labels)]


# Port of compactLabel (flow-instance-filter.js:449-474).
# Key insertion order mirrors the JS object literal exactly (matters because
# compact_label output feeds JSON.stringify in build_result's event hash). JS
# ``llm_review || undefined`` drops the key when falsy → omit it in Python.
def compact_label(label=None):
    if not label:
        return None
    out = {
        "id": label.get("id"),
        "label": label.get("label"),
        "category": label.get("category"),
        "subtype": label.get("subtype"),
        "sensitivity": label.get("sensitivity"),
        "field_name": label.get("field_name"),
        "field_path": label.get("field_path"),
        "origin_node": label.get("origin_node"),
        "origin_node_name": label.get("origin_node_name"),
        "introduced_at": label.get("introduced_at"),
        "mode": label.get("mode"),
        "confidence": round_confidence(label.get("confidence")),
        "evidence_level": label.get("evidence_level"),
        "evidence_kind": label.get("evidence_kind"),
        "evidence_text": label.get("evidence_text"),
        "ontology_version": label.get("ontology_version"),
        "ontology_label_id": label.get("ontology_label_id"),
        "requires_review": bool(label.get("requires_review")),
    }
    # JS: llm_review: label.llm_review || undefined — key present only when truthy.
    if label.get("llm_review"):
        out["llm_review"] = label.get("llm_review")
    out["uncertainty"] = label.get("uncertainty") or ""
    out["reason"] = label.get("reason") or ""
    return out


# Port of dedupeLabels (flow-instance-filter.js:476-491).
# NOTE: this is the filter's OWN dedupeLabels (distinct from data_labeler's) —
# same key but sorts by label.localeCompare at the end.
def dedupe_labels(labels):
    by_key = {}
    for label in (labels or []):
        if not label:
            continue
        key = "|".join([
            str(label.get("label")),
            str(label.get("origin_node")),
            str(label.get("introduced_at") or label.get("origin_node")),
        ])
        existing = by_key.get(key)
        if not existing or label_rank(label) > label_rank(existing):
            by_key[key] = dict(label)
    import functools
    from ..util.locale import locale_compare
    values = list(by_key.values())
    values.sort(key=functools.cmp_to_key(
        lambda a, b: locale_compare(str(a.get("label")), str(b.get("label")))))
    return values


# Port of labelRank (flow-instance-filter.js:493-496)
def label_rank(label=None):
    label = label or {}
    level = {"L4": 4, "L3": 3, "L2": 2, "L1": 1, "L0": 0}.get(label.get("evidence_level"), 0)
    return level * 10 + _num(label.get("confidence") or 0)


# Port of cloneLabel (flow-instance-filter.js:498-500)
def clone_label(label):
    return dict(label) if label else None


def _num(value):
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0
