"""Port of src/parser/doc-flow-extractor.js (3841 lines) — the largest FCG file.

Extracts document-flow and semantic-rule-flow nodes/edges from markdown
instructions. This is the rule-only + LLM semantic-gate core, carrying:
  - multi-line bullet folding + list-block disclaimer scope (segment_markdown_blocks)
  - negation -> disclaimer/constraint dispatch (apply_semantic_gate / apply_negation_constraint)
  - global two-phase ordering-constraint resolution (resolve_pending_constraints)
  - implicit object reads + object-producer edges
  - SKILL.md situation->action route rows

Data-boundary convention (matches the rest of the M1 port): node/edge objects
mirror the JS object shapes VERBATIM, including camelCase keys (instructionText,
stepIndex, docActions, excludeFromFlow, semanticKind, ...). Every function is
annotated `# Port of xxx.js:line`. The semantic gate calls into ..llm.transport
for the live HTTP path but supports injected refiners (used by tests) exactly
like the JS version's semanticRefiner / semanticBatchRefiner / constraintEndpointResolver.
"""

import hashlib
import json
import math
import os
import posixpath
import re
import sys
import tempfile

from .document_context import build_source_context, normalize_doc_path
from .shell_command_classifier import classify_shell_command_line, is_shell_fence_lang
from ..llm.normalizers import (
    normalize_assistant_content,
    parse_loose_json,
    normalize_scaled_number,
)
from ..llm.transport import post_json_with_timeout

# ---------------------------------------------------------------------------
# Module constants (doc-flow-extractor.js:14-139)
# ---------------------------------------------------------------------------

_BACKTICK_FILE_REF_RE = re.compile(r"`([^`\n]+?\.md)`", re.IGNORECASE)
_PLAIN_FILE_REF_RE = re.compile(
    r"(?:^|[\s(])([~./A-Za-z0-9_-]+(?:/[~./A-Za-z0-9_-]+)*\.md)\b", re.IGNORECASE
)
SEMANTIC_GATE_PROMPT_VERSION = "fcg-doc-semantic-gate-v4-negation"
DEFAULT_SEMANTIC_GATE_BATCH_SIZE = 10
DEFAULT_SEMANTIC_GATE_BATCH_CONCURRENCY = 4
DEFAULT_SEMANTIC_GATE_MAX_BATCH_CHARS = 60000


# Port of newSemanticGateUsage (doc-flow-extractor.js:27-29)
def new_semantic_gate_usage() -> dict:
    return {
        "calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cached_tokens": 0,
    }


# Port of accumulateSemanticGateUsage (doc-flow-extractor.js:31-43)
def accumulate_semantic_gate_usage(acc, usage) -> None:
    if not acc or not usage or not isinstance(usage, dict):
        return
    acc["calls"] += 1
    acc["prompt_tokens"] += _js_number(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    acc["completion_tokens"] += _js_number(
        usage.get("completion_tokens") or usage.get("output_tokens") or 0
    )
    acc["total_tokens"] += _js_number(usage.get("total_tokens") or 0)
    details = usage.get("prompt_tokens_details")
    cached = None
    if isinstance(details, dict):
        cached = details.get("cached_tokens")
    if cached is None:
        cached = usage.get("cached_tokens")
    if cached is None:
        cached = usage.get("prompt_cache_hit_tokens")
    if cached is None:
        cached = 0
    acc["cached_tokens"] += _js_number(cached)


# Port of summarizeSemanticGateUsage (doc-flow-extractor.js:45-49)
def summarize_semantic_gate_usage(acc):
    if not acc or not acc.get("calls"):
        return None
    prompt_tokens = acc.get("prompt_tokens") or 0
    cache_hit_ratio = (
        _js_round((acc.get("cached_tokens", 0) / prompt_tokens) * 1000) / 1000
        if prompt_tokens
        else 0
    )
    return {**acc, "prompt_cache_hit_ratio": cache_hit_ratio}


READ_KEYWORDS = [
    "read", "load", "search", "show", "list", "query", "review", "check", "inspect", "open",
    "get", "fetch", "retrieve",
]
WRITE_KEYWORDS = [
    "write", "save", "log", "add", "append", "store", "persist", "export", "record",
    "update", "promote", "demote", "archive", "remove", "delete",
]
RUN_KEYWORDS = [
    "run", "setup", "install", "execute", "init", "initialize", "call", "invoke", "send", "post", "upload",
]
ACTION_KEYWORDS = [*READ_KEYWORDS, *WRITE_KEYWORDS, *RUN_KEYWORDS]

_SEMANTIC_CONNECTOR_RE = re.compile(
    r"\b(?:and then|then|after that|before that|finally|next|and|before|after)\b|[,;]|\b(?:,\s*and)\b",
    re.IGNORECASE,
)

_CONDITION_REGEXES = [
    re.compile(r"\b(?:when|if|after|before|whenever|once|unless)\b[^,.;]*", re.IGNORECASE),
    re.compile(
        r"[^,.;]*(?:fail|failed|error|correct|wrong|reject|periodic|recurring|weekly|daily|monthly|heartbeat)[^,.;]*",
        re.IGNORECASE,
    ),
]

OPERATION_TYPE_DEFINITIONS = [
    {"type": "guard", "keywords": ["do not", "don't", "never", "avoid", "must not", "does not", "doesn't", "cannot", "can't", "will not", "won't", "no longer", "without"]},
    {"type": "decision", "keywords": ["decide", "choose", "whether", "determine"]},
    {"type": "verify", "keywords": ["verify", "validate", "ensure", "confirm", "test"]},
    {"type": "review", "keywords": ["review", "reflect", "heartbeat", "periodic", "recurring"]},
    {"type": "transform", "keywords": ["summarize", "summary", "digest", "brief", "extract", "convert", "classify", "parse", "analyze", "redact", "mask", "sanitize"]},
    {"type": "produce_artifact", "keywords": ["produce", "generate", "output", "report", "create file", "create", "build", "compose", "draft"]},
    {"type": "invoke_tool", "keywords": RUN_KEYWORDS},
    {"type": "write", "keywords": WRITE_KEYWORDS},
    {"type": "read", "keywords": READ_KEYWORDS},
    {"type": "condition", "keywords": ["when", "if", "unless", "only if"]},
]

OPERATION_EFFECTS = {
    "trigger": ["branch"],
    "condition": ["branch"],
    "decision": ["branch"],
    "read": ["read_context"],
    "write": ["persist_state"],
    "transform": ["summarize"],
    "invoke_tool": ["call_tool"],
    "model_inference": ["model_context"],
    "external_egress": ["network_egress"],
    "verify": ["validate"],
    "review": ["read_context", "summarize"],
    "produce_artifact": ["persist_state"],
    "guard": ["branch"],
}

OPERATION_DOC_ACTION = {
    "trigger": "condition",
    "condition": "condition",
    "decision": "decision",
    "read": "read",
    "write": "write",
    "transform": "transform",
    "invoke_tool": "run",
    "model_inference": "run",
    "external_egress": "run",
    "verify": "verify",
    "review": "review",
    "produce_artifact": "write",
    "guard": "guard",
}

VALID_OPERATION_TYPES = set(OPERATION_EFFECTS.keys())
VALID_EFFECTS = set()
for _effs in OPERATION_EFFECTS.values():
    VALID_EFFECTS.update(_effs)
VALID_EFFECTS.add("update_memory")
VALID_TARGET_TYPES = {
    "file", "directory", "tool", "memory_tier", "memory", "artifact", "document",
    "instruction", "semantic_rule", "external", "url", "command", "object",
}


# ---------------------------------------------------------------------------
# Small JS-parity numeric helpers
# ---------------------------------------------------------------------------

def _js_number(value):
    """JS Number(x) for numeric-usage fields. Returns int when integral (so the
    usage counters stay integers like JS, e.g. 2546 not 2546.0), else float; 0
    for the unparseable/empty cases JS would coerce to 0 (via `|| 0`)."""
    try:
        if value is None or value == "":
            return 0
        num = float(value)
    except (TypeError, ValueError):
        return 0
    return int(num) if num.is_integer() else num


def _js_round(x: float) -> int:
    """JS Math.round: round half toward +Infinity (not banker's rounding)."""
    return math.floor(x + 0.5)


def _lower(value) -> str:
    return str(value if value is not None else "").lower()


class _LocaleStr(str):
    """Sort-key wrapper reproducing JS ``String.localeCompare`` (ICU-root ASCII,
    NOT code-point) so tuple sort keys built from file/section strings order
    exactly as V8 does. Punctuation like ``_`` vs ``.`` differs between locale and
    code-point order, and these keys (doc slugs such as
    ``doc.step.memory_template...``) hit that difference. Subclassing str keeps
    the keys hashable; only comparison is overridden. See util/locale.py.
    """
    __slots__ = ()

    def __lt__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) < 0

    def __gt__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) > 0

    def __le__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) <= 0

    def __ge__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) >= 0

    def __eq__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) == 0

    def __ne__(self, other):
        from ..util.locale import locale_compare
        return locale_compare(str(self), str(other)) != 0

    def __hash__(self):
        return str.__hash__(self)


def _json_compact(value) -> str:
    """JSON.stringify(value) with no spaces (JS default separators)."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Public entry (doc-flow-extractor.js:151-199)
# ---------------------------------------------------------------------------

def extract_document_flow(skill_data, readme_data, options=None):
    """Port of extractDocumentFlow. Synchronous (injected refiners + live HTTP
    transport are all synchronous in the Python port)."""
    options = options or {}
    extraction_docs = options.get("extractionDocs")
    if isinstance(extraction_docs, list):
        docs = _dedupe_docs(extraction_docs)
    else:
        docs = build_document_set(skill_data, readme_data)
    doc_index = build_doc_index(docs)
    step_flow = extract_step_flow(docs, doc_index)
    route_flow = extract_review_route_flow({
        "reviewDocs": options.get("reviewDocs") or [],
        "extractionDocs": docs,
        "docIndex": doc_index,
        "stepsByDoc": step_flow["stepsByDoc"],
    })
    step_flow["edges"].extend(route_flow["edges"])
    raw_nodes = dedupe_nodes(step_flow["nodes"])
    gate_limit = limit_nodes_before_semantic_gate(raw_nodes, options.get("maxDocFlowNodes"))
    if gate_limit["truncated"]:
        print(
            f"Warning: doc-flow semantic gate candidates capped at "
            f"{len(gate_limit['nodes'])}/{len(raw_nodes)}; "
            f"set SFG_MAX_DOC_FLOW_NODES to adjust batch breadth.",
            file=sys.stderr,
        )
    semantic_gate_usage = new_semantic_gate_usage()
    gated_nodes = refine_document_flow_semantics(
        gate_limit["nodes"], {**options, "semanticGateUsage": semantic_gate_usage}
    )

    # Ordering constraints stay pending on their nodes; resolved GLOBALLY later
    # by resolve_pending_constraints once all node sources merge (see JS 178-184).
    flow_node_names = {"user.query", "llm.inference"}
    for node in gated_nodes or []:
        if not is_context_only_node(node) and node.get("name"):
            flow_node_names.add(node["name"])
    deduped = dedupe_edges(list(step_flow["edges"]))
    all_edges = []
    for index, edge in enumerate(deduped):
        e = {"id": f"doc_edge_{str(index + 1).rjust(3, '0')}", **edge}
        if e["source"] in flow_node_names and e["target"] in flow_node_names:
            all_edges.append(e)

    return {
        "nodes": gated_nodes,
        "edges": all_edges,
        "semantic_gate_usage": summarize_semantic_gate_usage(semantic_gate_usage),
    }


# Port of resolvePendingConstraints (doc-flow-extractor.js:205-277)
def resolve_pending_constraints(nodes, options=None):
    options = options or {}
    result_nodes = list(nodes) if isinstance(nodes, list) else []
    added_nodes = []
    edges = []
    pendings = [
        n for n in result_nodes
        if n and n.get("pending_constraint") and n["pending_constraint"].get("kind") == "ordering"
    ]
    if len(pendings) == 0:
        for n in result_nodes:
            n.pop("pending_constraint", None)
        return {"nodes": result_nodes, "addedNodes": added_nodes, "edges": edges}

    holder_set = set(id(h) for h in pendings)
    actionable = [
        n for n in result_nodes
        if n and n.get("name") and not is_context_only_node(n) and id(n) not in holder_set
    ]
    synthesized = {}  # key -> synthesized node

    endpoint_match = {}  # phrase -> node (resolved)
    unresolved_phrases = {}  # phrase -> phrase
    for holder in pendings:
        pc = holder["pending_constraint"]
        for phrase in (pc.get("before_action"), pc.get("after_action")):
            if not phrase or phrase in endpoint_match:
                continue
            hit = match_action_node(phrase, actionable)
            if hit is not None:
                endpoint_match[phrase] = hit
            else:
                unresolved_phrases[phrase] = phrase

    if len(unresolved_phrases) > 0:
        llm_resolved = llm_resolve_constraint_endpoints(
            list(unresolved_phrases.keys()), actionable, options
        )
        for phrase, node in llm_resolved.items():
            if node is not None:
                endpoint_match[phrase] = node

    seen_edge_keys = set()
    for holder in pendings:
        pc = holder["pending_constraint"]
        before_node = endpoint_match.get(pc.get("before_action")) or get_or_create_constraint_node(
            pc.get("before_action"), holder, synthesized, result_nodes, actionable, added_nodes
        )
        after_node = endpoint_match.get(pc.get("after_action")) or get_or_create_constraint_node(
            pc.get("after_action"), holder, synthesized, result_nodes, actionable, added_nodes
        )
        holder.pop("pending_constraint", None)
        if not before_node or not after_node or before_node["name"] == after_node["name"]:
            continue
        key = f"{before_node['name']}->{after_node['name']}"
        if key in seen_edge_keys:
            continue
        seen_edge_keys.add(key)
        note = pc.get("note")
        edges.append({
            "source": before_node["name"],
            "target": after_node["name"],
            "type": "control_flow",
            "confidence": 0.5,
            "validation_method": "doc_flow_constraint",
            "data_flow": {"from_param": "state", "to_param": "state", "data_type": "object"},
            "semantic_reason": (
                f'Prohibitive ordering: "{pc.get("before_action")}" must precede '
                f'"{pc.get("after_action")}"' + (f" ({note})" if note else "")
            ),
            "source_context": edge_source_context_from_node(holder, "doc_flow_constraint"),
        })

    for n in result_nodes:
        n.pop("pending_constraint", None)
    return {"nodes": result_nodes, "addedNodes": added_nodes, "edges": edges}


# Port of matchActionNode (doc-flow-extractor.js:282-298)
def match_action_node(phrase, actionable):
    target = action_phrase_tokens(phrase)
    if len(target) == 0:
        return None
    best = None
    best_score = 0
    for node in actionable:
        text = str(
            node.get("instructionText")
            or (node.get("formal_semantics") or {}).get("evidence", {}).get("text")
            or node.get("name")
            or ""
        )
        tokens = action_phrase_tokens(text)
        if len(tokens) == 0:
            continue
        overlap = sum(1 for t in target if t in tokens)
        score = overlap / len(target)
        if score > best_score:
            best_score = score
            best = node
    return best if best_score >= 0.6 else None


_ACTION_STOP = {
    "the", "a", "an", "to", "of", "it", "them", "this", "that", "first", "any", "all",
    "without", "before", "after", "is", "are", "be", "and", "or",
}


# Port of actionPhraseTokens (doc-flow-extractor.js:300-310)
def action_phrase_tokens(text):
    lowered = re.sub(r"[^a-z0-9\s]", " ", str(text or "").lower())
    result = set()
    for w in re.split(r"\s+", lowered):
        if len(w) > 2 and w not in _ACTION_STOP:
            result.add(stem_action_word(w))
    return result


# Port of stemActionWord (doc-flow-extractor.js:316-331)
def stem_action_word(word):
    w = word
    if len(w) > 4 and w.endswith("ing"):
        w = w[:-3]
        if re.search(r"([bcdfgklmnprstvz])\1$", w):
            w = w[:-1]
    elif len(w) > 4 and w.endswith("ed"):
        w = w[:-2]
        if re.search(r"([bcdfgklmnprstvz])\1$", w):
            w = w[:-1]
    elif len(w) > 4 and w.endswith("es"):
        w = w[:-2]
    elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


# ---------------------------------------------------------------------------
# Constraint-endpoint LLM resolution (doc-flow-extractor.js:341-488)
# ---------------------------------------------------------------------------

# Port of llmResolveConstraintEndpoints (doc-flow-extractor.js:341-383)
def llm_resolve_constraint_endpoints(phrases, actionable, options=None):
    options = options or {}
    resolved = {}
    if not isinstance(phrases, list) or len(phrases) == 0:
        return resolved

    candidates = []
    for n in actionable:
        text = re.sub(
            r"\s+", " ",
            str(
                n.get("instructionText")
                or (n.get("formal_semantics") or {}).get("evidence", {}).get("text")
                or n.get("name")
                or ""
            ),
        ).strip()[:160]
        candidates.append({"node": n, "text": text})
    candidates = [c for c in candidates if len(c["text"]) > 0]
    if len(candidates) == 0:
        return resolved

    node_by_id = {}
    for i, c in enumerate(candidates):
        node_by_id[f"n{i + 1}"] = c["node"]

    try:
        resolver = options.get("constraintEndpointResolver")
        if callable(resolver):
            raw = resolver({"phrases": phrases, "candidates": candidates})
        else:
            api_key = options.get("llmApiKey") or os.environ.get("LLM_API_KEY") or ""
            if not api_key or options.get("disableLlm") is True:
                return resolved
            raw = call_constraint_endpoint_model(phrases, candidates, options)
    except Exception as err:  # noqa: BLE001 — mirror JS catch-all fallback
        print(
            f"Warning: constraint endpoint LLM resolution failed ({err}); "
            f"falling back to synthesis.",
            file=sys.stderr,
        )
        return resolved

    parsed = parse_loose_json(raw)
    results = parsed.get("results") if isinstance(parsed, dict) else None
    if not isinstance(results, list):
        results = []
    for r in results:
        if not isinstance(r, dict):
            continue
        phrase = r.get("phrase") if isinstance(r.get("phrase"), str) else None
        rid = r.get("node_id")
        rid = rid.strip() if isinstance(rid, str) else None
        if not phrase or phrase not in phrases:
            continue
        node = node_by_id.get(rid) if (rid and rid.lower() != "null") else None
        if node is not None:
            resolved[phrase] = node
    return resolved


# Port of callConstraintEndpointModel (doc-flow-extractor.js:385-402)
def call_constraint_endpoint_model(phrases, candidates, options):
    endpoint = resolve_semantic_llm_endpoint(options)
    model = options.get("llmModel") or "gpt-5.5"
    timeout = int(options.get("llmTimeout") or 180000)
    payload = post_json_with_timeout(endpoint, {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": build_constraint_endpoint_system_prompt()},
            {"role": "user", "content": build_constraint_endpoint_prompt(phrases, candidates)},
        ],
    }, {
        "timeoutMs": timeout,
        "headers": {"Authorization": f"Bearer {options.get('llmApiKey')}"},
    })
    accumulate_semantic_gate_usage(options.get("semanticGateUsage"), (payload or {}).get("usage"))
    choices = (payload or {}).get("choices") or [{}]
    return normalize_assistant_content((choices[0] or {}).get("message", {}).get("content"))


# Port of buildConstraintEndpointSystemPrompt (doc-flow-extractor.js:404-414)
def build_constraint_endpoint_system_prompt():
    return " ".join([
        "You match action phrases from a prohibitive-ordering constraint to the action node that already represents that action in a skill flow graph.",
        'Each phrase is a short action (e.g. "vet skill", "install skill").',
        "You are given a numbered list of candidate action nodes with their instruction text.",
        "For each phrase, return the id of the ONE candidate that denotes the SAME runtime action, allowing for word-form differences (vet/vetting), paraphrase, or extra wording.",
        "Only match when the candidate genuinely performs that action; a node that merely mentions the word in a condition, heading, or disclaimer is NOT a match.",
        "If no candidate denotes the action, return null for that phrase — do not force a weak match.",
        'Return strict JSON only: {"results":[{"phrase":"...","node_id":"nK"|null}]}. One entry per phrase.',
    ])


# Port of buildConstraintEndpointPrompt (doc-flow-extractor.js:416-426)
def build_constraint_endpoint_prompt(phrases, candidates):
    lines = ["Phrases to match:"]
    for p in phrases:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("Candidate action nodes:")
    for i, c in enumerate(candidates):
        lines.append(f"n{i + 1}: {c['text']}")
    lines.append("")
    lines.append('Return {"results":[{"phrase","node_id"}]} with node_id = matching id or null.')
    return "\n".join(lines)


# Port of getOrCreateConstraintNode (doc-flow-extractor.js:431-488)
def get_or_create_constraint_node(phrase, holder, synthesized, result_nodes, actionable, added_nodes):
    clean = str(phrase or "").strip()
    if not clean:
        return None
    key = "_".join(sorted(action_phrase_tokens(clean)))
    if key in synthesized:
        return synthesized[key]

    pc = holder.get("pending_constraint") or {}
    owner_doc = pc.get("source_doc") or holder.get("ownerDoc") or "SKILL.md"
    section = pc.get("source_section") or (holder.get("location") or {}).get("section") or ""
    slug = re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", clean.lower()))[:40] or "action"
    name = f"doc.constraint.{file_slug(owner_doc)}.{slug}"
    norm_owner = normalize_doc_path(owner_doc)
    line = (holder.get("location") or {}).get("line") or 0
    node = {
        "name": name,
        "action": "guard",
        "type": "custom_func",
        "description": f"Constraint endpoint (synthesized) in {owner_doc}: {clean}",
        "input": {},
        "output": {},
        "location": {"file": norm_owner, "line": line, "section": section},
        "ownerDoc": norm_owner,
        "docAction": "guard",
        "docActions": ["guard"],
        "operationType": "guard",
        "instructionText": clean,
        "synthesized_from": "negation_constraint",
        "formal_semantics": {
            "operation_type": "guard",
            "actor": "llm",
            "inputs": [],
            "outputs": [{"name": "branch_state", "type": "object"}],
            "targets": [],
            "conditions": [],
            "effects": ["branch"],
            "confidence": 0.5,
            "evidence": {
                "text": clean,
                "source_line": clean,
                "file": norm_owner,
                "line": line,
                "section": section,
                "method": "negation_constraint_synthesis",
                "role": "constraint_endpoint",
            },
            "action": "guard",
        },
        "semantic_gate": {
            "classification": "policy_rule",
            "actionability": "runtime_action",
            "grammar": "synthesized constraint endpoint",
            "reason": "synthesized from prohibitive ordering constraint with no matching extracted node",
            "method": "negation_constraint_synthesis",
        },
    }
    synthesized[key] = node
    result_nodes.append(node)
    actionable.append(node)
    if isinstance(added_nodes, list):
        added_nodes.append(node)
    return node


# ---------------------------------------------------------------------------
# Semantic gate: refine core + batching (doc-flow-extractor.js:490-943)
# The JS runs candidates through bounded async concurrency; the Python injected
# refiners and the live transport are all synchronous, so we run them
# sequentially. Result ordering is identical (JS fills a results[] by index).
# ---------------------------------------------------------------------------

# Port of refineDocumentFlowSemantics (doc-flow-extractor.js:490-556)
def refine_document_flow_semantics(nodes, options=None):
    options = options or {}
    if options.get("semanticLlm") is False or options.get("disableLlm"):
        return [n for n in (apply_rule_only_semantic_gate(node) for node in nodes) if n]

    api_key = str(options.get("llmApiKey") or os.environ.get("LLM_API_KEY") or "").strip()
    if (not api_key
            and not callable(options.get("semanticRefiner"))
            and not callable(options.get("semanticBatchRefiner"))):
        raise ValueError("LLM_API_KEY is required for FCG Markdown semantic gate")

    candidates = [n for n in (nodes or []) if should_gate_semantic_node(n)]
    if len(candidates) == 0:
        return nodes

    config = {**options, "llmApiKey": api_key}

    cache = load_semantic_gate_cache(config)
    candidate_names = set(n["name"] for n in candidates if n.get("name"))
    gated_by_name = {}
    missing = []

    for node in candidates:
        cache_key = build_semantic_gate_cache_key(node, config)
        cached = cache["records"].get(cache_key)
        if cached:
            refinement = {**cached, "cache_hit": True}
            next_node = apply_candidate_semantic_gate(node, refinement)
            if next_node:
                gated_by_name[node["name"]] = next_node
            continue
        missing.append({"node": node, "cacheKey": cache_key})

    resolved = resolve_semantic_gate_candidates(missing, config)
    for item in resolved:
        if item.get("error") is not None:
            next_node = create_context_node_from_node(item["node"], "doc_review_error", {
                "reason": str(item["error"]) or "semantic LLM gate failed",
                "requiresReview": True,
            })
        else:
            next_node = apply_candidate_semantic_gate(item["node"], item.get("refinement"))
        if next_node:
            gated_by_name[item["node"]["name"]] = next_node
        if item.get("error") is None and item.get("refinement"):
            append_semantic_gate_cache_record(cache, item["cacheKey"], item["node"], item["refinement"], config)

    out = []
    for node in (nodes or []):
        if node["name"] not in candidate_names:
            out.append(node)
            continue
        nn = gated_by_name.get(node["name"]) or create_context_node_from_node(
            node, "doc_review_error",
            {"reason": "semantic LLM gate did not return a result", "requiresReview": True},
        )
        if nn:
            out.append(nn)
    return out


# Port of shouldGateSemanticNode (doc-flow-extractor.js:558-567)
def should_gate_semantic_node(node):
    if not node or not node.get("formal_semantics"):
        return False
    if node.get("semanticKind") not in ("doc_operation", "doc_step"):
        return False
    method = str(
        (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method")
        or (node.get("formal_semantics") or {}).get("evidence", {}).get("method")
        or ""
    )
    if method in ("implicit_object_read", "doc_review_route"):
        return False
    if method == "doc_code_block_command":
        return False
    return True


# Port of limitNodesBeforeSemanticGate (doc-flow-extractor.js:569-596)
def limit_nodes_before_semantic_gate(nodes=None, max_nodes=None):
    nodes = nodes or []
    try:
        limit = int(max_nodes or 0)
    except (TypeError, ValueError):
        limit = 0
    if limit <= 0 or len(nodes) <= limit:
        return {"nodes": nodes, "truncated": False}

    def priority(node):
        if not node:
            return 99
        k = node.get("semanticKind")
        if k in ("trigger", "policy"):
            return 0
        if k == "doc_step":
            return 1
        if k == "doc_operation":
            return 2
        if str(k or "").startswith("doc_"):
            return 3
        return 4

    def sort_key(node):
        loc = node.get("location") or {}
        f = str(loc.get("file") or node.get("ownerDoc") or "")
        line = _js_number(loc.get("line") or 0)
        return (priority(node), _LocaleStr(f), line)

    capped = sorted(nodes, key=sort_key)[:limit]
    return {"nodes": capped, "truncated": True}


# Port of resolveSemanticGateCandidates (doc-flow-extractor.js:598-631)
def resolve_semantic_gate_candidates(items, config):
    if not items or len(items) == 0:
        return []

    if callable(config.get("semanticRefiner")) and not callable(config.get("semanticBatchRefiner")):
        out = []
        for item in items:
            try:
                raw_refinement = invoke_semantic_refiner(item["node"], config)
                out.append(normalize_semantic_gate_result(item, raw_refinement))
            except Exception as error:  # noqa: BLE001
                out.append({**item, "error": error})
        return out

    batch_size = normalize_positive_integer(
        config.get("semanticGateBatchSize", os.environ.get("SFG_SEMANTIC_GATE_BATCH_SIZE")),
        DEFAULT_SEMANTIC_GATE_BATCH_SIZE,
    )
    max_batch_chars = normalize_positive_integer(
        config.get("semanticGateMaxBatchChars", os.environ.get("SFG_SEMANTIC_GATE_MAX_BATCH_CHARS")),
        DEFAULT_SEMANTIC_GATE_MAX_BATCH_CHARS,
    )
    batches = chunk_semantic_gate_items(items, {"batchSize": batch_size, "maxBatchChars": max_batch_chars})
    batch_results = [judge_semantic_gate_batch_with_retry(batch, config) for batch in batches]
    flat = []
    for br in batch_results:
        flat.extend(br)
    return flat


# Port of chunkSemanticGateItems (doc-flow-extractor.js:651-673)
def chunk_semantic_gate_items(items, opts):
    batch_size = opts["batchSize"]
    max_batch_chars = opts["maxBatchChars"]
    chunks = []
    sorted_items = sorted(items or [], key=_semantic_gate_batch_sort_key)
    current = []
    current_chars = 0
    for item in sorted_items:
        item_chars = estimate_semantic_gate_item_chars(item)
        would_exceed_size = len(current) >= batch_size
        would_exceed_chars = len(current) > 0 and current_chars + item_chars > max_batch_chars
        if would_exceed_size or would_exceed_chars:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(item)
        current_chars += item_chars
    if len(current) > 0:
        chunks.append(current)
    return chunks


# Port of compareSemanticGateBatchItems (doc-flow-extractor.js:675-685) as a sort key.
def _semantic_gate_batch_sort_key(item):
    node = (item or {}).get("node") or {}
    loc = node.get("location") or {}
    f = str(loc.get("file") or node.get("ownerDoc") or "")
    section = str(loc.get("section") or "")
    line = _js_number(loc.get("line") or 0)
    return (_LocaleStr(f), _LocaleStr(section), line)


# Port of estimateSemanticGateItemChars (doc-flow-extractor.js:687-690)
def estimate_semantic_gate_item_chars(item):
    node = (item or {}).get("node") or {}
    return len(_json_compact(build_semantic_batch_record({"id": "c0", "node": node}))) + 512


# Port of judgeSemanticGateBatchWithRetry (doc-flow-extractor.js:692-708)
def judge_semantic_gate_batch_with_retry(batch, config):
    try:
        raw_batch = invoke_semantic_batch_refiner([item["node"] for item in batch], config)
        return normalize_semantic_gate_batch_result(batch, raw_batch)
    except Exception as error:  # noqa: BLE001
        if len(batch) <= 1:
            return [{**item, "error": error} for item in batch]
        midpoint = math.ceil(len(batch) / 2)
        left = judge_semantic_gate_batch_with_retry(batch[:midpoint], config)
        right = judge_semantic_gate_batch_with_retry(batch[midpoint:], config)
        return [*left, *right]


# Port of normalizeSemanticGateResult (doc-flow-extractor.js:710-722)
def normalize_semantic_gate_result(item, raw_refinement):
    refinement = normalize_semantic_refinement(raw_refinement)
    if not refinement:
        return {**item, "error": ValueError("Invalid semantic LLM JSON")}
    return {**item, "refinement": refinement}


# Port of invokeSemanticRefiner (doc-flow-extractor.js:724-734)
def invoke_semantic_refiner(node, options):
    refiner = options.get("semanticRefiner")
    if callable(refiner):
        return refiner(node, {
            "current": node.get("formal_semantics"),
            "provider": options.get("llmProvider") or "openai",
            "model": options.get("llmModel") or "gpt-5.5",
        })
    return call_semantic_refinement_model(node, options)


# Port of invokeSemanticBatchRefiner (doc-flow-extractor.js:736-752)
def invoke_semantic_batch_refiner(nodes, options):
    candidates = [
        {"id": f"c{index + 1}", "node": node, "current": node.get("formal_semantics")}
        for index, node in enumerate(nodes or [])
    ]
    refiner = options.get("semanticBatchRefiner")
    if callable(refiner):
        return refiner(nodes, {
            "candidates": candidates,
            "provider": options.get("llmProvider") or "openai",
            "model": options.get("llmModel") or "gpt-5.5",
        })
    return call_semantic_batch_refinement_model(candidates, options)


# Port of callSemanticRefinementModel (doc-flow-extractor.js:754-780)
def call_semantic_refinement_model(node, options):
    endpoint = resolve_semantic_llm_endpoint(options)
    model = options.get("llmModel") or "gpt-5.5"
    timeout = int(options.get("llmTimeout") or 180000)
    payload = post_json_with_timeout(endpoint, {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": build_semantic_gate_system_prompt()},
            {"role": "user", "content": build_semantic_refinement_prompt(node)},
        ],
    }, {
        "timeoutMs": timeout,
        "headers": {"Authorization": f"Bearer {options.get('llmApiKey')}"},
    })
    accumulate_semantic_gate_usage(options.get("semanticGateUsage"), (payload or {}).get("usage"))
    choices = (payload or {}).get("choices") or [{}]
    return normalize_assistant_content((choices[0] or {}).get("message", {}).get("content"))


# Port of callSemanticBatchRefinementModel (doc-flow-extractor.js:782-810)
def call_semantic_batch_refinement_model(candidates, options):
    endpoint = resolve_semantic_llm_endpoint(options)
    model = options.get("llmModel") or "gpt-5.5"
    timeout = int(options.get("llmTimeout") or 180000)
    payload = post_json_with_timeout(endpoint, {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": build_semantic_gate_system_prompt({
                "returnShape": 'Return strict JSON only: {"results":[{...}]}. Each result must include the candidate id.'
            })},
            {"role": "user", "content": build_semantic_batch_refinement_prompt(candidates)},
        ],
    }, {
        "timeoutMs": timeout,
        "headers": {"Authorization": f"Bearer {options.get('llmApiKey')}"},
    })
    accumulate_semantic_gate_usage(options.get("semanticGateUsage"), (payload or {}).get("usage"))
    choices = (payload or {}).get("choices") or [{}]
    return normalize_assistant_content((choices[0] or {}).get("message", {}).get("content"))


# Port of buildSemanticGateSystemPrompt (doc-flow-extractor.js:812-837)
def build_semantic_gate_system_prompt(opts=None):
    return_shape = (opts or {}).get("returnShape")
    return " ".join([
        "You gate Markdown soft-instruction candidates before they become FCG action nodes.",
        return_shape or "Return strict JSON only in English.",
        "First classify each source as one of: workflow_instruction, policy_rule, definition, schema, example, template, description, discard.",
        "Analyze English grammar: fragment, SVC, SVO, passive, imperative, table_row, heading, list_item.",
        "For fragments, reconstruct the missing subject or predicate before deciding actionability.",
        "For passive clauses, identify the patient/theme and only infer a runtime producer or consumer if the sentence commands an agent action.",
        "Table definitions, examples, templates, field schemas, and descriptive prose are not runtime actions unless the text explicitly instructs the agent to do something at runtime.",
        "Allowed operation_type values: trigger, condition, decision, read, write, transform, invoke_tool, verify, review, produce_artifact, guard.",
        "Allowed effects: read_context, persist_state, call_tool, update_memory, summarize, validate, branch.",
        "confidence must be a number from 0 to 1.",
        "Set actionability to runtime_action only when this candidate should become a flow node.",
        "Treat SKILL.md as the highest-priority semantic anchor for declared task, trigger conditions, route rules, policy rules, and workflow steps.",
        "For SKILL.md Situation->Action table rows, judge the whole row: put the situation in conditions and the action receiver/target in targets/effects.",
        "Do not split a Situation->Action row into fake standalone trigger or policy nodes.",
        "Never infer trigger/policy nodes from headings, file names, directory trees, template placeholders, or example error text.",
        "If a title or file description only names a log/template/example, classify it as description/template/example context_only.",
        "NEGATION HANDLING: a negated sentence is NOT automatically a disclaimer. Set negation_kind to disclaimer, constraint, or null.",
        'A genuine DISCLAIMER states a capability the skill does not have ("does not connect to a wallet", "does not send data externally"): negation_kind=disclaimer, classification=description, actionability=context_only.',
        'A PROHIBITIVE CONSTRAINT forbids or orders a runtime action ("never install a skill without vetting it first", "never delete without asking", "never overwrite existing files", "do not log secrets unless the user asks"): negation_kind=constraint, classification=policy_rule, actionability=runtime_action.',
        'For a constraint set constraint_edge to {kind:"ordering"|"guard", before_action, after_action, guarded_action, note}. ordering: before_action must precede after_action (e.g. before="vet skill", after="install skill"). guard: guarded_action is the forbidden/conditional action (e.g. guarded="overwrite existing files"); leave before_action/after_action null.',
        "If the candidate is not a negation, set negation_kind=null and constraint_edge=null.",
        "Do not create graph edges or path relationships.",
    ])


# Port of resolveSemanticLlmEndpoint (doc-flow-extractor.js:839-846)
def resolve_semantic_llm_endpoint(options=None):
    options = options or {}
    if options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT"):
        return options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT")
    provider = str(options.get("llmProvider") or os.environ.get("LLM_PROVIDER") or "openai").lower()
    if provider == "dashscope":
        return os.environ.get("DASHSCOPE_ENDPOINT") or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    return "https://api.openai.com/v1/chat/completions"


# Port of buildSemanticRefinementPrompt (doc-flow-extractor.js:848-867)
def build_semantic_refinement_prompt(node):
    loc = node.get("location") or {}
    fs = node.get("formal_semantics") or {}
    return "\n".join([
        "Decide whether this Markdown candidate is a runtime action flow node or documentation context only.",
        "Return JSON in English with these keys: classification, actionability, grammar, completed_sentence, operation_type, targets, conditions, effects, confidence, reason.",
        "classification must be workflow_instruction, policy_rule, definition, schema, example, template, description, or discard.",
        "actionability must be runtime_action or context_only.",
        "grammar must describe fragment/SVC/SVO/passive/imperative/table_row/list_item and the subject/predicate/object roles.",
        "targets must be objects with type, value, and optional raw.",
        "conditions must be objects with type and text.",
        "confidence must be a number from 0 to 1.",
        "",
        f"Node: {node.get('name') or ''}",
        f"Document: {node.get('ownerDoc') or loc.get('file') or ''}",
        f"Line: {loc.get('line') or 0}",
        f"Instruction: {node.get('instructionText') or fs.get('evidence', {}).get('text') or ''}",
        "",
        "Current formal_semantics:",
        _json_pretty(node.get("formal_semantics") or {}),
    ])


# Port of buildSemanticBatchRefinementPrompt (doc-flow-extractor.js:869-882)
def build_semantic_batch_refinement_prompt(candidates):
    records = [build_semantic_batch_record(c) for c in (candidates or [])]
    return "\n".join([
        "Gate each Markdown candidate independently.",
        "Return JSON with this shape:",
        '{"results":[{"id":"c1","classification":"workflow_instruction|policy_rule|definition|schema|example|template|description|discard","actionability":"runtime_action|context_only","grammar":"...","completed_sentence":"...","operation_type":"read|write|transform|invoke_tool|verify|review|produce_artifact|guard|condition|decision|trigger","targets":[],"conditions":[],"effects":[],"negation_kind":"disclaimer|constraint|null","constraint_edge":null,"confidence":0.0,"reason":"..."}]}',
        'For a negated candidate that is a prohibitive constraint, set negation_kind="constraint" and constraint_edge={"kind":"ordering|guard","before_action":null,"after_action":null,"guarded_action":null,"note":""}. Otherwise negation_kind=null (or "disclaimer" for a capability disclaimer) and constraint_edge=null.',
        "Use the exact candidate id. Do not omit a candidate. Do not infer graph edges.",
        "",
        "Candidates:",
        _json_pretty(records),
    ])


# Port of buildSemanticBatchRecord (doc-flow-extractor.js:884-897)
def build_semantic_batch_record(candidate):
    node = candidate.get("node") or {}
    loc = node.get("location") or {}
    sc = node.get("source_context") or {}
    fs = node.get("formal_semantics") or {}
    ev = fs.get("evidence", {}) if isinstance(fs, dict) else {}
    return {
        "id": candidate.get("id"),
        "node": node.get("name") or "",
        "document": node.get("ownerDoc") or loc.get("file") or "",
        "line": loc.get("line") or 0,
        "section": loc.get("section") or "",
        "source_role": sc.get("source_role") or "",
        "instruction": node.get("instructionText") or ev.get("text") or "",
        "source_line": sc.get("source_line") or ev.get("source_line") or "",
        "current_formal_semantics": node.get("formal_semantics") or {},
    }


# Port of normalizeSemanticGateBatchResult (doc-flow-extractor.js:899-913)
def normalize_semantic_gate_batch_result(batch, raw_batch):
    parsed = parse_loose_json(raw_batch)
    by_id = normalize_batch_result_map(parsed)
    out = []
    for index, item in enumerate(batch):
        candidate_id = f"c{index + 1}"
        raw = by_id.get(candidate_id) or by_id.get(item["node"].get("name")) or by_id.get(str(index))
        if not raw:
            out.append({**item, "error": ValueError(f"Missing semantic LLM result for {candidate_id}")})
            continue
        out.append(normalize_semantic_gate_result(item, raw))
    return out


# Port of normalizeBatchResultMap (doc-flow-extractor.js:915-943)
def normalize_batch_result_map(parsed):
    by_id = {}
    if not parsed:
        return by_id

    if isinstance(parsed, list):
        results = parsed
    elif isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
        results = parsed["results"]
    elif isinstance(parsed, dict) and isinstance(parsed.get("refinements"), list):
        results = parsed["refinements"]
    else:
        results = None

    if results is not None:
        for index, item in enumerate(results):
            item = item if isinstance(item, dict) else {}
            rid = str(item.get("id") or item.get("candidate_id") or item.get("node_id") or f"c{index + 1}").strip()
            if rid:
                by_id[rid] = results[index]
        return by_id

    if isinstance(parsed, dict):
        for key, value in parsed.items():
            if not value or not isinstance(value, dict):
                continue
            by_id[str(key)] = value
            rid = str(value.get("id") or value.get("candidate_id") or value.get("node_id") or "").strip()
            if rid:
                by_id[rid] = value

    return by_id


def _json_pretty(value) -> str:
    """JSON.stringify(value, null, 2)."""
    return json.dumps(value, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Refinement normalization + apply (doc-flow-extractor.js:945-1550)
# ---------------------------------------------------------------------------

# Port of normalizeSemanticRefinement (doc-flow-extractor.js:945-1026)
def normalize_semantic_refinement(raw):
    parsed = parse_loose_json(raw)
    if not parsed or not isinstance(parsed, dict):
        return None

    refinement = {}
    classification = normalize_classification(
        parsed.get("classification") or parsed.get("node_kind") or parsed.get("kind") or parsed.get("semantic_kind")
    )
    if classification:
        refinement["classification"] = classification

    actionability = normalize_actionability(
        parsed.get("actionability") or parsed.get("actionable") or parsed.get("flow_role")
    )
    if actionability:
        refinement["actionability"] = actionability

    grammar = parsed.get("grammar")
    if isinstance(grammar, str) and grammar.strip():
        refinement["grammar"] = grammar.strip()
    elif grammar and isinstance(grammar, dict):
        refinement["grammar"] = _json_compact(grammar)

    completed = parsed.get("completed_sentence")
    if isinstance(completed, str) and completed.strip():
        refinement["completed_sentence"] = completed.strip()

    operation_type = str(parsed.get("operation_type") or "").strip()
    if operation_type in VALID_OPERATION_TYPES:
        refinement["operation_type"] = operation_type

    if isinstance(parsed.get("targets"), list):
        refinement["targets"] = [t for t in (normalize_refinement_target(x) for x in parsed["targets"]) if t]

    if isinstance(parsed.get("conditions"), list):
        refinement["conditions"] = [c for c in (normalize_refinement_condition(x) for x in parsed["conditions"]) if c]

    if isinstance(parsed.get("effects"), list):
        seen_eff = []
        for effect in parsed["effects"]:
            e = str(effect if effect is not None else "").strip()
            if e in VALID_EFFECTS and e not in seen_eff:
                seen_eff.append(e)
        refinement["effects"] = seen_eff

    confidence = normalize_scaled_number(parsed.get("confidence"), fallback=float("nan"))
    if _is_finite(confidence):
        refinement["confidence"] = confidence

    reason = parsed.get("reason")
    if isinstance(reason, str) and reason.strip():
        refinement["reason"] = reason.strip()

    negation_kind = normalize_negation_kind(parsed.get("negation_kind"))
    if negation_kind:
        refinement["negation_kind"] = negation_kind
        if negation_kind == "constraint":
            constraint_edge = normalize_constraint_edge(parsed.get("constraint_edge"))
            if constraint_edge:
                refinement["constraint_edge"] = constraint_edge

    has_useful_field = any([
        bool(refinement.get("classification")),
        bool(refinement.get("actionability")),
        bool(refinement.get("grammar")),
        bool(refinement.get("completed_sentence")),
        bool(refinement.get("operation_type")),
        bool(refinement.get("targets")),
        bool(refinement.get("conditions")),
        bool(refinement.get("effects")),
        isinstance(refinement.get("confidence"), (int, float)),
        bool(refinement.get("reason")),
        bool(refinement.get("negation_kind")),
    ])
    return refinement if has_useful_field else None


# Port of normalizeNegationKind (doc-flow-extractor.js:1028-1033)
def normalize_negation_kind(value):
    normalized = re.sub(r"\s+", "_", normalize_for_search(value))
    if normalized in ("disclaimer", "capability_disclaimer"):
        return "disclaimer"
    if normalized in ("constraint", "prohibitive_constraint", "ordering_constraint", "guard"):
        return "constraint"
    return ""


# Port of normalizeConstraintEdge (doc-flow-extractor.js:1035-1065)
def normalize_constraint_edge(raw):
    if not raw or not isinstance(raw, dict):
        return None
    kind = re.sub(r"\s+", "_", normalize_for_search(raw.get("kind")))
    edge_kind = "ordering" if kind == "ordering" else ("guard" if kind == "guard" else "")
    if not edge_kind:
        return None

    def _str(value):
        s = str("" if value is None else value).strip()
        return s if s and s.lower() != "null" else ""

    edge = {"kind": edge_kind}
    before = _str(raw.get("before_action"))
    after = _str(raw.get("after_action"))
    guarded = _str(raw.get("guarded_action"))
    note = _str(raw.get("note"))
    if edge_kind == "ordering":
        if before:
            edge["before_action"] = before
        if after:
            edge["after_action"] = after
        if not before or not after:
            edge["kind"] = "guard"
            edge["guarded_action"] = guarded or after or before or ""
    else:
        edge["guarded_action"] = guarded or ""
    if note:
        edge["note"] = note
    if edge["kind"] == "ordering" and (not edge.get("before_action") or not edge.get("after_action")):
        return None
    if edge["kind"] == "guard" and not edge.get("guarded_action"):
        return None
    return edge


# Port of normalizeClassification (doc-flow-extractor.js:1067-1079)
def normalize_classification(value):
    normalized = re.sub(r"\s+", "_", normalize_for_search(value))
    if not normalized:
        return ""
    if normalized in ("workflow_instruction", "runtime_action", "instruction", "action"):
        return "workflow_instruction"
    if normalized in ("policy_rule", "policy"):
        return "policy_rule"
    if normalized in ("definition", "term_definition", "table_definition"):
        return "definition"
    if normalized in ("schema", "field_schema", "data_schema", "fields"):
        return "schema"
    if normalized in ("example", "sample"):
        return "example"
    if normalized in ("template", "boilerplate"):
        return "template"
    if normalized in ("description", "descriptive", "overview", "context"):
        return "description"
    if normalized in ("discard", "irrelevant", "non_action"):
        return "discard"
    return ""


# Port of normalizeActionability (doc-flow-extractor.js:1081-1087)
def normalize_actionability(value):
    normalized = re.sub(r"\s+", "_", normalize_for_search(value))
    if not normalized:
        return ""
    if normalized in ("runtime_action", "action", "actionable", "flow", "flow_node", "true", "yes"):
        return "runtime_action"
    if normalized in ("context_only", "context", "non_action", "false", "no", "definition", "schema", "example", "template", "discard"):
        return "context_only"
    return ""


# Port of normalizeRefinementTarget (doc-flow-extractor.js:1089-1102)
def normalize_refinement_target(target):
    if not target or not isinstance(target, dict):
        return None
    type_ = str(target.get("type") or "").strip()
    value = str(target.get("value") or "").strip()
    if not type_ or not value or type_ not in VALID_TARGET_TYPES:
        return None
    normalized = {
        "type": type_,
        "value": normalize_doc_path(value) if type_ in ("file", "directory") else value,
    }
    if target.get("raw") is not None:
        normalized["raw"] = str(target.get("raw") or "").strip()
    return normalized


# Port of normalizeRefinementCondition (doc-flow-extractor.js:1104-1112)
def normalize_refinement_condition(condition):
    if not condition or not isinstance(condition, dict):
        return None
    text = str(condition.get("text") or "").strip()
    if not text:
        return None
    return {
        "type": str(condition.get("type") or "condition").strip() or "condition",
        "text": text,
    }


# Port of applySemanticRefinement (doc-flow-extractor.js:1114-1159)
def apply_semantic_refinement(node, refinement):
    current = node.get("formal_semantics") or {}
    prior_method = (current.get("evidence") or {}).get("method") or ""
    operation_type = refinement.get("operation_type") or current.get("operation_type") or "read"
    if refinement.get("targets") and len(refinement["targets"]) > 0:
        targets = dedupe_targets(refinement["targets"])
    else:
        targets = current.get("targets") or []
    if refinement.get("conditions") is not None:
        conditions = dedupe_conditions(refinement["conditions"])
    else:
        conditions = current.get("conditions") or []
    if refinement.get("effects") and len(refinement["effects"]) > 0:
        effects = refinement["effects"]
    else:
        effects = OPERATION_EFFECTS.get(operation_type) or current.get("effects") or []
    if isinstance(refinement.get("confidence"), (int, float)):
        confidence = refinement["confidence"]
    else:
        confidence = _js_number(current.get("confidence") or 0.5)
    action = OPERATION_DOC_ACTION.get(operation_type) or current.get("action") or node.get("docAction") or "read"

    node["formal_semantics"] = {
        **current,
        "operation_type": operation_type,
        "actor": current.get("actor") or "llm",
        "inputs": build_formal_inputs(operation_type, targets, conditions),
        "outputs": build_formal_outputs(operation_type, targets),
        "targets": targets,
        "conditions": conditions,
        "effects": effects,
        "confidence": confidence,
        "action": action,
        "evidence": {
            **(current.get("evidence") or {}),
            "method": append_evidence_method(prior_method or "rule", "semantic_llm"),
            "llm_reason": refinement.get("reason") or "",
        },
    }
    node["source_context"] = update_source_context_action_evidence(node.get("source_context"), {
        "action": action,
        "operationType": operation_type,
        "extractionMethod": append_evidence_method(
            (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method") or prior_method or "rule",
            "semantic_llm",
        ),
        "reason": refinement.get("reason") or "",
        "grounded": True,
    })


# Port of applySemanticGate (doc-flow-extractor.js:1161-1206)
def apply_semantic_gate(node, refinement):
    classification = refinement.get("classification") or ""
    actionability = refinement.get("actionability") or ""

    if refinement.get("negation_kind") == "disclaimer":
        return create_context_node_from_node(node, "doc_definition", {
            "refinement": refinement,
            "reason": refinement.get("reason") or "capability disclaimer is context only",
        })
    if refinement.get("negation_kind") == "constraint" and refinement.get("constraint_edge"):
        return apply_negation_constraint(node, refinement)

    context_kind = context_kind_for_classification(classification, actionability)
    if context_kind:
        return create_context_node_from_node(node, context_kind, {
            "refinement": refinement,
            "reason": refinement.get("reason") or f"{classification or actionability} is context only",
        })

    apply_semantic_refinement(node, refinement)
    fs = node.get("formal_semantics") or {}
    if fs.get("evidence"):
        fs["evidence"]["method"] = append_evidence_method(fs["evidence"].get("method") or "rule", "semantic_llm_gate")
    node["semantic_gate"] = build_semantic_gate_record(refinement, "runtime_action")
    node["source_context"] = update_source_context_action_evidence(node.get("source_context"), {
        "action": fs.get("action") or node.get("docAction") or "",
        "operationType": fs.get("operation_type") or node.get("operationType") or "",
        "extractionMethod": append_evidence_method(
            (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method")
            or fs.get("evidence", {}).get("method") or "rule",
            "semantic_llm_gate",
        ),
        "reason": refinement.get("reason") or "",
        "grounded": True,
    })
    return node


# Port of applyNegationConstraint (doc-flow-extractor.js:1215-1254)
def apply_negation_constraint(node, refinement):
    apply_semantic_refinement(node, refinement)
    fs = node.get("formal_semantics")
    if fs is None:
        fs = {}
        node["formal_semantics"] = fs
    fs["operation_type"] = "guard"
    if fs.get("evidence"):
        fs["evidence"]["method"] = append_evidence_method(fs["evidence"].get("method") or "rule", "semantic_llm_gate")
        fs["evidence"]["role"] = "prohibitive_constraint"
    edge = refinement["constraint_edge"]
    if edge["kind"] == "guard":
        guard_text = edge["guarded_action"]
    else:
        guard_text = f"{edge['before_action']} must precede {edge['after_action']}"
    fs["conditions"] = fs.get("conditions") if isinstance(fs.get("conditions"), list) else []
    fs["conditions"].append({"type": "condition", "text": f"constraint: {guard_text}"})

    if edge["kind"] == "ordering":
        loc = node.get("location") or {}
        node["pending_constraint"] = {
            "kind": "ordering",
            "before_action": edge["before_action"],
            "after_action": edge["after_action"],
            "note": edge.get("note") or "",
            "source_node": node.get("name"),
            "source_doc": node.get("ownerDoc") or loc.get("file") or "",
            "source_section": loc.get("section") or "",
        }

    node["semantic_gate"] = build_semantic_gate_record(refinement, "runtime_action")
    node["source_context"] = update_source_context_action_evidence(node.get("source_context"), {
        "action": "guard",
        "operationType": "guard",
        "extractionMethod": append_evidence_method(
            (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method")
            or fs.get("evidence", {}).get("method") or "rule",
            "semantic_llm_gate",
        ),
        "reason": refinement.get("reason") or "prohibitive constraint",
        "grounded": True,
    })
    return node


# Port of applyCandidateSemanticGate (doc-flow-extractor.js:1256-1264)
def apply_candidate_semantic_gate(node, refinement):
    if not refinement:
        return create_context_node_from_node(node, "doc_review_error", {
            "reason": "Invalid semantic LLM JSON",
            "requiresReview": True,
        })
    return apply_semantic_gate(node, refinement)


# Port of applyRuleOnlySemanticGate (doc-flow-extractor.js:1266-1326)
def apply_rule_only_semantic_gate(node):
    if not should_gate_semantic_node(node):
        return node
    evidence_method = str(
        (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method")
        or (node.get("formal_semantics") or {}).get("evidence", {}).get("method")
        or ""
    )
    if evidence_method in ("implicit_object_read", "doc_review_route"):
        gate = {
            "classification": "workflow_instruction",
            "actionability": "runtime_action",
            "grammar": "derived runtime support node",
            "completed_sentence": "",
            "reason": f"{evidence_method} remains an internal support flow node",
        }
        # JS: `confidence: node.formal_semantics?.confidence` (undefined -> dropped).
        conf = (node.get("formal_semantics") or {}).get("confidence")
        if conf is not None:
            gate["confidence"] = conf
        gate["method"] = "rule_candidate_gate"
        node["semantic_gate"] = gate
        return node
    fs0 = node.get("formal_semantics") or {}
    ev0 = fs0.get("evidence", {}) if isinstance(fs0, dict) else {}
    text = str(node.get("instructionText") or ev0.get("source_line") or ev0.get("text") or "")
    role = classify_markdown_line_role({
        "line": text,
        "ownerDoc": node.get("ownerDoc") or (node.get("location") or {}).get("file") or "",
        "section": (node.get("location") or {}).get("section") or "",
    })
    if role.get("contextOnly"):
        return create_context_node_from_node(node, role.get("semanticKind") or "doc_definition", {
            "reason": role.get("reason") or "rule-only context gate",
            "requiresReview": True,
            "role": role,
        })

    current = node.get("formal_semantics") or {}
    node["formal_semantics"] = {
        **current,
        "confidence": min(0.68, _js_number(current.get("confidence") or 0.55)),
        "evidence": {
            **(current.get("evidence") or {}),
            "method": append_evidence_method((current.get("evidence") or {}).get("method") or "rule", "rule_candidate_gate"),
            "requires_review": True,
        },
    }
    node["semantic_gate"] = {
        "classification": "workflow_instruction",
        "actionability": "runtime_action",
        "grammar": role.get("grammar") or "",
        "completed_sentence": "",
        "reason": role.get("reason") or "rule-only high precision action candidate",
        "confidence": node["formal_semantics"]["confidence"],
        "method": "rule_candidate_gate",
    }
    node["source_context"] = update_source_context_action_evidence(node.get("source_context"), {
        "extractionMethod": append_evidence_method(
            (node.get("source_context") or {}).get("action_evidence", {}).get("extraction_method")
            or (current.get("evidence") or {}).get("method") or "rule",
            "rule_candidate_gate",
        ),
        "reason": node["semantic_gate"]["reason"],
        "grounded": True,
    })
    if (node.get("source_context") or {}).get("action_evidence"):
        node["source_context"]["action_evidence"]["requires_review"] = True
    return node


# Port of contextKindForClassification (doc-flow-extractor.js:1328-1337)
def context_kind_for_classification(classification, actionability):
    if actionability == "runtime_action":
        return ""
    if classification == "definition":
        return "doc_definition"
    if classification == "schema":
        return "doc_schema"
    if classification == "example":
        return "doc_example"
    if classification == "template":
        return "doc_template"
    if classification == "discard":
        return "doc_discard"
    if classification == "description" or actionability == "context_only":
        return "doc_definition"
    return ""


# Port of createContextNodeFromNode (doc-flow-extractor.js:1339-1395)
def create_context_node_from_node(node, semantic_kind, options=None):
    options = options or {}
    refinement = options.get("refinement") or {}
    source_context = node.get("source_context") or {}
    semantics = node.get("formal_semantics") or {}
    ev = semantics.get("evidence", {}) if isinstance(semantics, dict) else {}
    gate_record = build_semantic_gate_record(refinement, "context_only", {
        "reason": options.get("reason") or refinement.get("reason") or "",
        "method": "semantic_llm_gate_error" if semantic_kind == "doc_review_error" else "semantic_llm_gate",
        "role": options.get("role") or None,
    })
    text = str(
        node.get("instructionText") or ev.get("source_line") or ev.get("text") or source_context.get("source_line") or ""
    )
    new_name = re.sub(r"^doc\.op\.", "doc.context.",
                      re.sub(r"^doc\.step\.", "doc.context.", str(node.get("name") or "")))
    next_node = {
        **node,
        "name": new_name,
        "action": "context",
        "docAction": "context",
        "docActions": ["context"],
        "operationType": "context",
        "description": f"Documentation context in {node.get('ownerDoc') or (node.get('location') or {}).get('file') or ''}: {truncate_for_node(text, 120)}",
        "input": {},
        "output": {},
        "formal_semantics": {
            "operation_type": "context",
            "actor": "documentation",
            "inputs": [],
            "outputs": [],
            "targets": semantics.get("targets") or [],
            "conditions": [],
            "effects": [],
            "confidence": min(0.65, _js_number(refinement.get("confidence") or semantics.get("confidence") or 0.45)),
            "evidence": {
                **ev,
                "text": text,
                "method": gate_record["method"],
                "llm_reason": gate_record["reason"],
                "grammar": gate_record["grammar"],
                "completed_sentence": gate_record["completed_sentence"],
            },
            "action": "context",
        },
        "source_context": update_source_context_action_evidence(source_context, {
            "action": "context",
            "operationType": "context",
            "extractionMethod": gate_record["method"],
            "reason": gate_record["reason"],
            "grounded": True,
        }),
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
        "excludeFromFlow": True,
        "semanticKind": semantic_kind,
        "semantic_gate": gate_record,
    }
    if (next_node.get("source_context") or {}).get("action_evidence"):
        rr = options.get("requiresReview")
        next_node["source_context"]["action_evidence"]["requires_review"] = rr if rr is not None else True
    return next_node


# Port of buildSemanticGateRecord (doc-flow-extractor.js:1397-1411)
def build_semantic_gate_record(refinement=None, actionability="", extra=None):
    refinement = refinement or {}
    extra = extra or {}
    record = {
        "classification": refinement.get("classification") or extra.get("classification") or "",
        "actionability": refinement.get("actionability") or actionability or "",
        "grammar": refinement.get("grammar") or extra.get("grammar") or "",
        "completed_sentence": refinement.get("completed_sentence") or extra.get("completed_sentence") or "",
        "reason": refinement.get("reason") or extra.get("reason") or "",
    }
    # JS sets `confidence: <num> | undefined`; JSON.stringify drops the key when
    # undefined. Insert it here (before `method`) only when it is a real number.
    if isinstance(refinement.get("confidence"), (int, float)):
        record["confidence"] = refinement["confidence"]
    record["method"] = extra.get("method") or "semantic_llm_gate"
    if refinement.get("cache_hit"):
        record["cache_hit"] = True
    if refinement.get("negation_kind"):
        record["negation_kind"] = refinement["negation_kind"]
    if refinement.get("constraint_edge"):
        record["constraint_edge"] = refinement["constraint_edge"]
    if extra.get("role"):
        record["role"] = extra["role"]
    return record


# ---------------------------------------------------------------------------
# Semantic-gate cache + evidence helpers (doc-flow-extractor.js:1413-1550)
# ---------------------------------------------------------------------------

# Port of loadSemanticGateCache (doc-flow-extractor.js:1413-1444)
def load_semantic_gate_cache(options=None):
    options = options or {}
    cache_path = resolve_semantic_gate_cache_path(options)
    cache = {"path": cache_path, "records": {}, "enabled": bool(cache_path)}
    if not cache["enabled"] or not os.path.exists(cache_path):
        return cache
    try:
        with open(cache_path, "r", encoding="utf-8") as handle:
            lines = re.split(r"\r?\n", handle.read())
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except (ValueError, TypeError):
                continue
            if not record or not record.get("key") or not record.get("refinement"):
                continue
            refinement = normalize_semantic_refinement(record["refinement"])
            if refinement:
                cache["records"][record["key"]] = refinement
    except OSError:
        return {"path": "", "records": {}, "enabled": False}
    return cache


# Port of resolveSemanticGateCachePath (doc-flow-extractor.js:1446-1460)
def resolve_semantic_gate_cache_path(options=None):
    options = options or {}
    if options.get("semanticGateCache") is False or os.environ.get("SFG_SEMANTIC_GATE_CACHE") == "0":
        return ""
    sgc = options.get("semanticGateCache")
    if isinstance(sgc, str) and sgc.strip():
        return os.path.abspath(sgc.strip())
    env = os.environ.get("SFG_SEMANTIC_GATE_CACHE")
    if env and env.strip():
        return os.path.abspath(env.strip())
    if callable(options.get("semanticRefiner")) or callable(options.get("semanticBatchRefiner")):
        return ""
    return os.path.join(tempfile.gettempdir(), "skill-sfg-semantic-gate-cache.jsonl")


# Port of buildSemanticGateCacheKey (doc-flow-extractor.js:1462-1486)
def build_semantic_gate_cache_key(node, options=None):
    options = options or {}
    loc = node.get("location") or {}
    sc = node.get("source_context") or {}
    fs = node.get("formal_semantics") or {}
    ev = fs.get("evidence", {}) if isinstance(fs, dict) else {}
    source_text = "\n".join([
        p for p in [
            node.get("instructionText") or "",
            sc.get("source_line") or "",
            sc.get("action_evidence", {}).get("snippet") or "",
            ev.get("text") or "",
            ev.get("source_line") or "",
        ] if p
    ])
    payload = {
        "version": SEMANTIC_GATE_PROMPT_VERSION,
        "provider": options.get("llmProvider") or "openai",
        "model": options.get("llmModel") or "gpt-5.5",
        "document": node.get("ownerDoc") or loc.get("file") or "",
        "line": loc.get("line") or 0,
        "span": node.get("stepRange") or sc.get("span") or None,
        "section": loc.get("section") or "",
        "semantic_kind": node.get("semanticKind") or "",
        "extraction_method": sc.get("action_evidence", {}).get("extraction_method") or "",
        "source_hash": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    }
    return hashlib.sha256(_json_compact(payload).encode("utf-8")).hexdigest()


# Port of appendSemanticGateCacheRecord (doc-flow-extractor.js:1488-1510)
def append_semantic_gate_cache_record(cache, key, node, refinement, options=None):
    options = options or {}
    if not cache or not cache.get("enabled") or not cache.get("path") or not key or not refinement:
        return
    if key in cache["records"]:
        return
    loc = node.get("location") or {}
    record = {
        "key": key,
        "prompt_version": SEMANTIC_GATE_PROMPT_VERSION,
        "provider": options.get("llmProvider") or "openai",
        "model": options.get("llmModel") or "gpt-5.5",
        "document": node.get("ownerDoc") or loc.get("file") or "",
        "line": loc.get("line") or 0,
        "node": node.get("name") or "",
        "refinement": strip_runtime_semantic_gate_fields(refinement),
    }
    try:
        os.makedirs(os.path.dirname(cache["path"]), exist_ok=True)
        with open(cache["path"], "a", encoding="utf-8") as handle:
            handle.write(f"{_json_compact(record)}\n")
        cache["records"][key] = record["refinement"]
    except OSError:
        cache["enabled"] = False


# Port of stripRuntimeSemanticGateFields (doc-flow-extractor.js:1512-1518)
def strip_runtime_semantic_gate_fields(refinement=None):
    refinement = refinement or {}
    return {k: v for k, v in refinement.items() if k != "cache_hit"}


# Port of truncateForNode (doc-flow-extractor.js:1520-1523)
def truncate_for_node(value, maximum):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return f"{text[:maximum - 3]}..." if len(text) > maximum else text


# Port of updateSourceContextActionEvidence (doc-flow-extractor.js:1525-1540)
def update_source_context_action_evidence(source_context=None, patch=None):
    if not source_context or not isinstance(source_context, dict):
        return source_context
    patch = patch or {}
    current = source_context.get("action_evidence") or {}
    grounded = patch.get("grounded") if patch.get("grounded") is not None else current.get("grounded")
    return {
        **source_context,
        "action_evidence": {
            **current,
            "action": patch.get("action") or current.get("action") or "",
            "operation_type": patch.get("operationType") or current.get("operation_type") or "",
            "extraction_method": patch.get("extractionMethod") or current.get("extraction_method") or "",
            "llm_reason": patch.get("reason") or current.get("llm_reason") or "",
            "grounded": grounded,
            "requires_review": current.get("requires_review") or (patch.get("grounded") is False),
        },
    }


# Port of appendEvidenceMethod (doc-flow-extractor.js:1542-1550)
def append_evidence_method(current, nxt):
    parts = [p.strip() for p in str(current or "").split("+") if p.strip()]
    extra = str(nxt or "").strip()
    if extra and extra not in parts:
        parts.append(extra)
    return "+".join(parts) or extra or ""


# ---------------------------------------------------------------------------
# Step-flow extraction + node builders (doc-flow-extractor.js:1552-2175)
# ---------------------------------------------------------------------------

# Port of extractStepFlow (doc-flow-extractor.js:1552-1601)
def extract_step_flow(docs, doc_index):
    nodes = []
    edges = []
    steps_by_doc = {}

    for doc in docs:
        raw_steps = extract_steps_from_doc(doc, doc_index)
        if len(raw_steps) == 0:
            continue
        action_steps = [s for s in raw_steps if is_action_flow_node(s)]
        steps_by_doc[doc["file"]] = action_steps
        for step in raw_steps:
            nodes.append(step)
            add_step_primary_edges(edges, step)
        add_step_sequence_edges(edges, doc["file"], action_steps)
        add_object_producer_edges(edges, doc["file"], action_steps)

    for doc_file, steps in steps_by_doc.items():
        for step in steps:
            refs = step.get("stepRefs")
            if not isinstance(refs, list) or len(refs) == 0:
                continue
            for target_doc in refs:
                target_steps = steps_by_doc.get(target_doc)
                target_entry = target_steps[0] if target_steps else None
                if not target_entry or target_entry["name"] == step["name"]:
                    continue
                edges.append({
                    "source": step["name"],
                    "target": target_entry["name"],
                    "type": "control_flow",
                    "confidence": 0.63,
                    "validation_method": "doc_flow",
                    "data_flow": {"from_param": "instruction", "to_param": "context", "data_type": "string"},
                    "semantic_reason": f"Markdown reference jump from {doc_file} to {target_doc}",
                })

    return {"nodes": nodes, "edges": edges, "stepsByDoc": steps_by_doc}


# Port of extractReviewRouteFlow (doc-flow-extractor.js:1603-1662)
def extract_review_route_flow(config):
    review_docs = config.get("reviewDocs") or []
    extraction_docs = config.get("extractionDocs") or []
    doc_index = config.get("docIndex")
    steps_by_doc = config.get("stepsByDoc")
    edges = []
    extraction_files = set(normalize_doc_path(doc["file"]) for doc in extraction_docs)

    for doc in review_docs:
        doc_file = normalize_doc_path(doc.get("file"))
        if not doc_file or doc_file in extraction_files:
            continue
        lines = str(doc.get("content") or "").split("\n")
        in_code_block = False
        for index in range(len(lines)):
            line = lines[index]
            trimmed = line.strip()
            if re.match(r"^```", trimmed):
                in_code_block = not in_code_block
                continue
            if in_code_block or not trimmed:
                continue
            refs = extract_file_refs_from_line(trimmed)
            if not refs:
                continue
            section = find_section_for_line(doc.get("sections") or [], index + 1)
            for ref_info in refs:
                target_doc = resolve_doc_reference(ref_info["ref"], doc_file, doc_index)
                if not target_doc:
                    continue
                target_steps = steps_by_doc.get(target_doc)
                route_context = build_doc_source_context({
                    "doc": doc,
                    "line": index + 1,
                    "section": section,
                    "sourceLine": trimmed,
                    "action": infer_action_from_line(trimmed, ref_info["index"]),
                    "operationType": "route",
                    "actionSnippet": trimmed,
                    "extractionMethod": "doc_review_route",
                    "trigger": ref_info["ref"],
                })
                target_entry = target_steps[0] if target_steps else None
                if not target_entry or not target_entry.get("name"):
                    continue
                edges.append({
                    "source": "user.query",
                    "target": target_entry["name"],
                    "type": "doc_instruction",
                    "confidence": 0.46,
                    "validation_method": "doc_review_route",
                    "data_flow": {"from_param": "query_text", "to_param": "file_path", "data_type": "string"},
                    "semantic_reason": f"Review context in {doc_file} routes to {target_doc}",
                    "source_context": route_context,
                })

    return {"edges": edges}


# Port of extractStepsFromDoc (doc-flow-extractor.js:1664-1861)
def extract_steps_from_doc(doc, doc_index):
    steps = []
    lines = str(doc.get("content") or "").split("\n")
    block_directives = segment_markdown_blocks(lines, doc.get("sections"))
    in_code_block = False
    code_block_lang = ""
    step_index = 0
    object_producers = {}
    last_object_key = ""
    last_object_text = ""

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        trimmed = line.strip()

        fence_match = re.match(r"^```+\s*([A-Za-z0-9_-]*)", trimmed)
        if fence_match:
            if not in_code_block:
                in_code_block = True
                code_block_lang = fence_match.group(1) or ""
            else:
                in_code_block = False
                code_block_lang = ""
            idx += 1
            continue
        if in_code_block:
            if is_shell_fence_lang(code_block_lang):
                section = find_section_for_line(doc.get("sections"), idx + 1)
                for command in classify_shell_command_line(line):
                    step_index += 1
                    steps.append(create_command_step_node({
                        "doc": doc,
                        "line": idx + 1,
                        "stepIndex": step_index,
                        "section": section,
                        "command": command,
                    }))
            idx += 1
            continue
        if not trimmed:
            idx += 1
            continue
        if re.match(r"^#{1,6}\s+", trimmed):
            idx += 1
            continue
        if re.match(r"^\|?\s*[-:| ]+\|?\s*$", trimmed):
            idx += 1
            continue

        directive = block_directives.get(idx)
        if directive and directive.get("role") == "continuation":
            idx += 1
            continue

        is_list_item = bool(directive and directive.get("role") == "item_start")
        effective_line = directive["mergedText"] if is_list_item else line
        block_scope = directive.get("blockScope") if is_list_item else None

        section = find_section_for_line(doc.get("sections"), idx + 1)
        line_role = classify_markdown_line_role({
            "line": effective_line,
            "ownerDoc": doc.get("file"),
            "section": section,
            "previousLine": _at_list(lines, idx - 1),
            "nextLine": _at_list(lines, idx + 1),
            "blockScope": block_scope,
        })
        if line_role.get("contextOnly"):
            step_index += 1
            steps.append(create_doc_context_node({
                "doc": doc,
                "line": idx + 1,
                "stepIndex": step_index,
                "section": section,
                "sourceLine": effective_line if is_list_item else trimmed,
                "role": line_role,
            }))
            idx += 1
            continue

        semantic_ops = extract_semantic_operations_from_line({
            "line": effective_line,
            "ownerDoc": doc.get("file"),
            "lineNumber": idx + 1,
            "section": section,
            "docIndex": doc_index,
        })

        if len(semantic_ops) == 0:
            idx += 1
            continue

        for operation in semantic_ops:
            consumed_object = normalize_object_info(operation.get("consumedObject"))
            if (consumed_object is None
                    and operation.get("operationType") != "read"
                    and references_prior_object(operation.get("sourceLine"))):
                consumed_object = {"key": last_object_key, "text": last_object_text or last_object_key}

            produced_object = normalize_object_info(operation.get("producedObject"))
            if produced_object is None and operation.get("operationType") == "read":
                produced_object = normalize_object_info(
                    {"key": operation.get("objectKey"), "text": operation.get("objectText")}
                )

            consumed_producer = None
            if consumed_object and consumed_object.get("key"):
                ck = consumed_object["key"]
                if ck not in object_producers and is_readable_data_object(consumed_object.get("text") or ck):
                    step_index += 1
                    implicit_step = create_doc_step_node({
                        "ownerDoc": doc.get("file"),
                        "line": idx + 1,
                        "stepIndex": step_index,
                        "section": section,
                        "action": "read",
                        "operationType": "read",
                        "targetDoc": semantic_target_ref(doc.get("file"), ck),
                        "stepRefs": [],
                        "sourceLine": f"Implicitly read {consumed_object.get('text') or ck}",
                        "formalSemantics": build_implicit_object_read_semantics({
                            "ownerDoc": doc.get("file"),
                            "line": idx + 1,
                            "section": section,
                            "instructionText": operation.get("sourceLine") or line,
                            "objectText": consumed_object.get("text") or ck,
                            "objectKey": ck,
                        }),
                        "sourceContext": build_doc_source_context({
                            "doc": doc,
                            "line": idx + 1,
                            "section": section,
                            "sourceLine": operation.get("sourceLine") or line,
                            "action": "read",
                            "operationType": "read",
                            "actionSnippet": f"Implicitly read {consumed_object.get('text') or ck}",
                            "extractionMethod": "implicit_object_read",
                            "trigger": consumed_object.get("text") or ck,
                            "grounded": False,
                            "derived": True,
                            "requiresReview": True,
                        }),
                    })
                    steps.append(implicit_step)
                    object_producers[ck] = implicit_step
                consumed_producer = object_producers.get(ck)

            step_index += 1
            step = create_doc_step_node({
                "ownerDoc": doc.get("file"),
                "line": idx + 1,
                "stepIndex": step_index,
                "section": section,
                "action": operation.get("action"),
                "operationType": operation.get("operationType"),
                "targetDoc": operation.get("targetDoc"),
                "stepRefs": operation.get("stepRefs"),
                "sourceLine": operation.get("sourceLine"),
                "formalSemantics": operation.get("formalSemantics"),
                "sourceContext": build_doc_source_context({
                    "doc": doc,
                    "line": idx + 1,
                    "section": section,
                    "sourceLine": operation.get("sourceLine") or line,
                    "action": operation.get("action"),
                    "operationType": operation.get("operationType"),
                    "actionSnippet": operation.get("sourceLine") or line,
                    "extractionMethod": (operation.get("formalSemantics") or {}).get("evidence", {}).get("method") or "doc_flow",
                    "trigger": operation.get("operationType"),
                }),
            })
            if consumed_producer and consumed_producer["name"] != step["name"]:
                step["objectProducer"] = consumed_producer["name"]
                step["objectKey"] = consumed_object["key"]
            if consumed_object and consumed_object.get("key"):
                step["formal_semantics"]["evidence"]["consumed_object_key"] = consumed_object["key"]
                step["formal_semantics"]["evidence"]["consumed_object_text"] = consumed_object.get("text") or consumed_object["key"]
            if produced_object and produced_object.get("key"):
                step["formal_semantics"]["evidence"]["produced_object_key"] = produced_object["key"]
                step["formal_semantics"]["evidence"]["produced_object_text"] = produced_object.get("text") or produced_object["key"]
            steps.append(step)

            if produced_object and produced_object.get("key") and produces_object(operation.get("operationType")):
                object_producers[produced_object["key"]] = step
                last_object_key = produced_object["key"]
                last_object_text = produced_object.get("text") or produced_object["key"]
            elif consumed_object and consumed_object.get("key"):
                last_object_key = consumed_object["key"]
                last_object_text = consumed_object.get("text") or consumed_object["key"]

        idx += 1

    return steps


def _at_list(lines, index):
    if 0 <= index < len(lines):
        return lines[index] or ""
    return ""


# Port of buildStepMember (doc-flow-extractor.js:1863-1875) — retained for parity;
# createDocOperationNode is dead in the current JS pipeline (references an
# undefined `config`), so it is intentionally NOT ported.
def build_step_member(step):
    loc = step.get("location") or {}
    fs = step.get("formal_semantics") or {}
    return {
        "raw_name": str(step.get("name") or ""),
        "line": _int(loc.get("line") or 0),
        "section": str(loc.get("section") or ""),
        "step_index": _int(step.get("stepIndex") or 0),
        "action": str(step.get("docAction") or step.get("action") or "read"),
        "operation_type": str(fs.get("operation_type") or step.get("operationType") or step.get("docAction") or step.get("action") or "read"),
        "doc_ref": str(step.get("docRef") or ""),
        "instruction": str(step.get("instructionText") or ""),
        "formal_semantics": step.get("formal_semantics") or None,
    }


# Port of buildInstructionPreview (doc-flow-extractor.js:1939-1950)
def build_instruction_preview(members):
    lines = []
    for member in members or []:
        text = str(member.get("instruction") or "").strip()
        if not text:
            continue
        if text in lines:
            continue
        lines.append(text)
        if len(lines) >= 2:
            break
    preview = " | ".join(lines)
    return f"{preview[:157]}..." if len(preview) > 160 else preview


# Port of createDocStepNode (doc-flow-extractor.js:1952-2008)
def create_doc_step_node(config):
    owner_doc = normalize_doc_path(config.get("ownerDoc"))
    target_doc = normalize_doc_path(config.get("targetDoc") or config.get("ownerDoc"))
    owner_slug = file_slug(owner_doc)
    target_slug = file_slug(target_doc)
    action = config.get("action") or "read"
    operation_type = config.get("operationType") or (config.get("formalSemantics") or {}).get("operation_type") or action

    node_name = f"doc.step.{owner_slug}.l{config.get('line')}.s{config.get('stepIndex')}.{operation_type}.{target_slug}"
    section = config.get("section") or ""
    line_text = str(config.get("sourceLine") or "").strip()
    short_line = f"{line_text[:117]}..." if len(line_text) > 120 else line_text

    return {
        "name": node_name,
        "action": action,
        "type": "custom_func",
        "description": f"Step {config.get('stepIndex')} in {owner_doc}: {short_line or 'instruction step'}",
        "input": build_step_input(action, target_doc),
        "output": build_step_output(action),
        "location": {"file": owner_doc, "line": config.get("line") or 0, "section": section},
        "ownerDoc": owner_doc,
        "docRef": target_doc,
        "docAction": action,
        "docActions": [action],
        "operationType": operation_type,
        "stepIndex": config.get("stepIndex"),
        "stepRefs": [normalize_doc_path(r) for r in config.get("stepRefs") if normalize_doc_path(r)] if isinstance(config.get("stepRefs"), list) else [],
        "instructionText": line_text,
        "formal_semantics": config.get("formalSemantics") or create_fallback_formal_semantics({
            "operationType": operation_type,
            "action": action,
            "ownerDoc": owner_doc,
            "line": config.get("line"),
            "section": section,
            "instructionText": line_text,
            "targetDoc": target_doc,
        }),
        "source_context": config.get("sourceContext") or build_doc_source_context({
            "doc": {"file": owner_doc, "content": "", "sections": []},
            "line": config.get("line") or 0,
            "section": section,
            "sourceLine": line_text,
            "action": action,
            "operationType": operation_type,
            "actionSnippet": line_text,
            "extractionMethod": "doc_step",
        }),
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
        "semanticKind": "doc_step",
    }


# Port of createCommandStepNode (doc-flow-extractor.js:2019-2093)
def create_command_step_node(config):
    doc = config.get("doc") or {}
    owner_doc = normalize_doc_path(doc.get("file") or "")
    owner_slug = file_slug(owner_doc)
    command = config.get("command") or {}
    operation_type = command.get("operationType") or "invoke_tool"
    action = OPERATION_DOC_ACTION.get(operation_type) or "run"
    section = config.get("section") or ""
    snippet = str(command.get("segment") or "").strip()
    short_snippet = f"{snippet[:117]}..." if len(snippet) > 120 else snippet

    targets = [
        {"type": t.get("type"), "value": t.get("value"), "raw": t.get("raw") or t.get("value")}
        for t in (command.get("targets") or [])
    ]
    primary_target = (
        targets[0]["value"] if targets
        else semantic_target_ref(owner_doc, command.get("command") or operation_type)
    )
    target_slug = file_slug(primary_target)

    node_name = f"doc.step.{owner_slug}.l{config.get('line')}.s{config.get('stepIndex')}.{operation_type}.{target_slug}"

    formal_semantics = build_formal_semantics({
        "operationType": operation_type,
        "action": action,
        "ownerDoc": owner_doc,
        "line": config.get("line"),
        "section": section,
        "instructionText": snippet,
        "clauseText": snippet,
        "targets": targets if targets else [{"type": "command", "value": command.get("command") or snippet, "raw": snippet}],
        "conditions": [],
    })
    formal_semantics["actor"] = "shell"
    formal_semantics["evidence"]["method"] = "doc_code_block_command"

    return {
        "name": node_name,
        "action": action,
        "type": "custom_func",
        "description": f"Command in {owner_doc}: {short_snippet or command.get('command')}",
        "input": build_step_input(action, primary_target),
        "output": build_step_output(action),
        "location": {"file": owner_doc, "line": config.get("line") or 0, "section": section},
        "ownerDoc": owner_doc,
        "docRef": owner_doc,
        "docAction": action,
        "docActions": [action],
        "operationType": operation_type,
        "stepIndex": config.get("stepIndex"),
        "stepRefs": [],
        "instructionText": snippet,
        "formal_semantics": formal_semantics,
        "source_context": build_doc_source_context({
            "doc": doc,
            "line": config.get("line") or 0,
            "section": section,
            "sourceLine": snippet,
            "action": action,
            "operationType": operation_type,
            "actionSnippet": snippet,
            "extractionMethod": "doc_code_block_command",
            "trigger": command.get("command") or operation_type,
            "grounded": True,
        }),
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
        "semanticKind": "doc_step",
    }


# Port of createDocContextNode (doc-flow-extractor.js:2095-2175)
def create_doc_context_node(config):
    owner_doc = normalize_doc_path((config.get("doc") or {}).get("file") or "")
    owner_slug = file_slug(owner_doc)
    role = config.get("role") or {}
    semantic_kind = role.get("semanticKind") or "doc_definition"
    kind_slug = stable_slug(re.sub(r"^doc_", "", semantic_kind))
    line_text = str(config.get("sourceLine") or "").strip()
    short_line = f"{line_text[:117]}..." if len(line_text) > 120 else line_text
    node_name = f"doc.context.{owner_slug}.l{config.get('line')}.s{config.get('stepIndex')}.{kind_slug}"

    source_context = build_doc_source_context({
        "doc": config.get("doc"),
        "line": config.get("line") or 0,
        "section": config.get("section") or "",
        "sourceLine": line_text,
        "action": "context",
        "operationType": "context",
        "actionSnippet": line_text,
        "extractionMethod": role.get("method") or "doc_context_gate",
        "trigger": role.get("reason") or semantic_kind,
        "grounded": True,
        "requiresReview": True,
    })

    return {
        "name": node_name,
        "action": "context",
        "type": "custom_func",
        "description": f"Documentation context in {owner_doc}: {short_line or semantic_kind}",
        "input": {},
        "output": {},
        "location": {"file": owner_doc, "line": config.get("line") or 0, "section": config.get("section") or ""},
        "ownerDoc": owner_doc,
        "docRef": owner_doc,
        "docAction": "context",
        "docActions": ["context"],
        "operationType": "context",
        "stepIndex": config.get("stepIndex"),
        "stepRefs": [],
        "instructionText": line_text,
        "formal_semantics": {
            "operation_type": "context",
            "actor": "documentation",
            "inputs": [],
            "outputs": [],
            "targets": [{"type": "document", "value": owner_doc, "raw": owner_doc}],
            "conditions": [],
            "effects": [],
            "confidence": 0.55,
            "evidence": {
                "text": line_text,
                "source_line": line_text,
                "file": owner_doc,
                "line": config.get("line") or 0,
                "section": config.get("section") or "",
                "method": role.get("method") or "doc_context_gate",
                "role": role.get("role") or "",
                "grammar": role.get("grammar") or "",
                "reason": role.get("reason") or "",
            },
            "action": "context",
        },
        "source_context": source_context,
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
        "excludeFromFlow": True,
        "semanticKind": semantic_kind,
        "semantic_gate": {
            "classification": role.get("classification") or re.sub(r"^doc_", "", semantic_kind),
            "actionability": "context_only",
            "grammar": role.get("grammar") or "",
            "completed_sentence": role.get("completed_sentence") or "",
            "reason": role.get("reason") or "",
            "method": role.get("method") or "doc_context_gate",
        },
    }


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0



# Port of classifyMarkdownLineRole (doc-flow-extractor.js:2177-2304)
def classify_markdown_line_role(config=None):
    config = config or {}
    owner_doc = normalize_doc_path(config.get("ownerDoc") or "")
    section = str(config.get("section") or "")
    raw = str(config.get("line") or "").strip()
    clean = strip_markdown_list_marker(raw)
    lower = clean.lower()
    file_lower = owner_doc.lower()
    previous = str(config.get("previousLine") or "").strip().lower()
    block_scope = config.get("blockScope")

    if not clean:
        return {"contextOnly": False}

    strong_disclaimer_scope = block_scope == "disclaimer"
    soft_negation_scope = is_negation_scope_heading(section) and not looks_imperative_runtime_instruction(clean)
    if strong_disclaimer_scope or soft_negation_scope:
        return {
            "contextOnly": True,
            "semanticKind": "doc_definition",
            "classification": "disclaimer",
            "role": "negated_disclaimer",
            "grammar": "negated clause; states an action the skill does not perform",
            "reason": (
                'list item under an explicit disclaimer lead-in ("does NOT do")'
                if strong_disclaimer_scope
                else "negated/disclaimer statement is not a runtime action"
            ),
            "method": "rule_context_gate",
        }
    if is_negated_action_text(clean):
        return {
            "contextOnly": False,
            "deferNegation": True,
            "role": "negation_pending",
            "grammar": "negated clause; disclaimer-vs-constraint deferred to semantic gate",
            "reason": "negated action deferred to LLM semantic gate for disclaimer/constraint classification",
        }

    if is_markdown_table_definition_row(clean, previous) and not is_skill_anchor_route_table_row(clean, owner_doc, section, previous):
        # A definition-shaped row whose action cells still carry a runtime signal is
        # a likely false-drop (the `explicit_instruction` escape valve is a
        # sentence-initial keyword regex and misses passive/non-initial/synonym
        # verbs). Under SFG_TABLE_DEFER_LLM, hand it to the semantic gate instead of
        # short-circuiting to context-only — same deferral template as negation.
        if table_defer_enabled() and table_row_has_soft_action_signal(clean):
            return {
                "contextOnly": False,
                "deferTable": True,
                "role": "table_action_pending",
                "grammar": "table_row with action-bearing cells; definition-vs-action deferred to semantic gate",
                "reason": "table row with a soft action signal deferred to LLM semantic gate for definition/action classification",
            }
        return {
            "contextOnly": True,
            "semanticKind": "doc_definition",
            "classification": "definition",
            "role": "definition_table_row",
            "grammar": "table_row definition; subject is the row key, predicate describes its meaning",
            "reason": "table row defines terminology or status meaning, not a runtime action",
            "method": "rule_context_gate",
        }

    if re.search(r"^\*\*[A-Za-z][^*]{0,40}\*\*:\s*[^.]+(?:\s*\|\s*[^.]+)+$", clean):
        return {
            "contextOnly": True,
            "semanticKind": "doc_schema",
            "classification": "schema",
            "role": "metadata_enum",
            "grammar": "field schema or enum declaration",
            "reason": "metadata enum describes allowed values",
            "method": "rule_context_gate",
        }

    if re.search(r"\b(template|example|sample)\b", file_lower, re.IGNORECASE) and not looks_imperative_runtime_instruction(clean):
        return {
            "contextOnly": True,
            "semanticKind": "doc_template" if "template" in file_lower else "doc_example",
            "classification": "template" if "template" in file_lower else "example",
            "role": "template_or_example_source",
            "grammar": "descriptive/template context",
            "reason": "template or example file text is not a runtime instruction without imperative action",
            "method": "rule_context_gate",
        }

    if is_passive_definition_fragment(clean):
        return {
            "contextOnly": True,
            "semanticKind": "doc_definition",
            "classification": "definition",
            "role": "passive_definition_fragment",
            "grammar": "passive fragment; missing subject is a documented term or prior noun phrase",
            "completed_sentence": complete_passive_fragment(clean, section),
            "reason": "passive descriptive fragment is not an instruction to read or write the referenced target",
            "method": "rule_context_gate",
        }

    if is_pure_description(clean):
        return {
            "contextOnly": True,
            "semanticKind": "doc_definition",
            "classification": "description",
            "role": "description",
            "grammar": "descriptive clause",
            "reason": "line describes document purpose or concepts",
            "method": "rule_context_gate",
        }

    return {
        "contextOnly": False,
        "grammar": "imperative or explicit runtime instruction" if looks_imperative_runtime_instruction(clean) else "",
    }


# Port of isMarkdownTableDefinitionRow (doc-flow-extractor.js:2306-2316)
def is_markdown_table_definition_row(clean, previous):
    if "|" not in clean:
        return False
    if re.match(r"^\|?\s*[-:| ]+\|?\s*$", clean):
        return False
    cells = parse_markdown_table_cells(clean)
    if len(cells) < 2:
        return False
    headerish = "|" in previous and re.search(
        r"\b(status|meaning|field|description|category|area|type|value|name|purpose)\b", previous, re.IGNORECASE
    )
    first_cell_looks_term = bool(re.match(r"^`?[\w.-]+`?$", cells[0])) or len(cells[0]) <= 32
    second = " ".join(cells[1:])
    explicit_instruction = looks_imperative_runtime_instruction(second) and re.search(
        r"\b(you|agent|assistant|must|should|run|execute|call|read|write|save|send|upload)\b", second, re.IGNORECASE
    )
    return bool((headerish or (len(cells) == 2 and first_cell_looks_term)) and not explicit_instruction)


# Port of isSkillAnchorRouteTableRow (doc-flow-extractor.js:2318-2328)
def is_skill_anchor_route_table_row(clean, owner_doc, section, previous):
    if normalize_doc_path(owner_doc) != "SKILL.md":
        return False
    if "|" not in clean:
        return False
    header_text = f"{previous or ''} {section or ''}".lower()
    if not re.search(r"\b(quick reference|situation|action|trigger|when|condition|route|routing|workflow|policy)\b", header_text):
        return False
    cells = parse_markdown_table_cells(clean)
    if len(cells) < 2:
        return False
    action = " ".join(cells[1:])
    return bool(
        looks_imperative_runtime_instruction(action)
        or re.search(r"\b(log|append|write|promote|review|send|create|update|consider)\b", action, re.IGNORECASE)
    )


def table_defer_enabled():
    # SkillFlow-only extension (no JS counterpart). Default OFF so the frozen
    # doc_flow.json parity golden stays byte-identical; mirrors the env-flag
    # convention used by SFG_SEQUENCE_EDGE_SCOPE / FCG_CYCLE_EXPAND.
    return str(os.environ.get("SFG_TABLE_DEFER_LLM") or "").strip().lower() in ("1", "true", "on", "yes")


def table_row_has_soft_action_signal(clean):
    # True when a table row that is_markdown_table_definition_row would DROP still
    # carries an action signal in its non-key cells — i.e. the row slipped past the
    # narrow `explicit_instruction` escape valve (verb not sentence-initial, passive
    # with an object, or a synonym verb). These are the silent false-drops. Passive
    # definition fragments ("Elevated to ...") and pure descriptions are NOT soft
    # signals, so genuine definition rows are never deferred.
    cells = parse_markdown_table_cells(clean)
    if len(cells) < 2:
        return False
    action_text = " ".join(cells[1:]).strip()
    if not action_text:
        return False
    if is_passive_definition_fragment(action_text) or is_pure_description(action_text):
        return False
    return is_actionable_clause(action_text) or is_semantic_instruction_line(action_text)


# Port of parseMarkdownTableCells (doc-flow-extractor.js:2330-2336)
def parse_markdown_table_cells(line):
    stripped = re.sub(r"^\|\s*|\s*\|$", "", str(line or ""))
    return [c for c in (cell.strip() for cell in stripped.split("|")) if c]


# Port of looksImperativeRuntimeInstruction (doc-flow-extractor.js:2338-2348)
def looks_imperative_runtime_instruction(text):
    value = str(text or "").strip().lower()
    if not value:
        return False
    if re.match(
        r"^(?:must|should|always|never|do not|don't|use|read|write|save|store|append|run|execute|call|invoke|send|post|upload|generate|create|summarize|extract|validate|verify|check|ensure|open|load|fetch|retrieve|review)\b",
        value,
    ):
        return True
    if re.match(
        r"^(?:when|if|after|before|once|unless)\b[\s\S]{0,120}\b(?:read|write|save|run|execute|call|invoke|send|post|upload|generate|create|add|update|append)\b",
        value,
    ):
        return True
    return False


# Port of isPassiveDefinitionFragment (doc-flow-extractor.js:2350-2354)
def is_passive_definition_fragment(text):
    value = str(text or "").strip()
    return bool(
        re.match(
            r"^(?:elevated|extracted|captured|recorded|stored|saved|written|generated|created|used|intended|designed|defined|listed)\b",
            value,
            re.IGNORECASE,
        )
        and not looks_imperative_runtime_instruction(value)
    )


# Port of completePassiveFragment (doc-flow-extractor.js:2356-2359)
def complete_passive_fragment(text, section):
    subject = f"The item in {section}" if section else "The documented item"
    return f"{subject} is {str(text or '').strip()}"


# Port of isPureDescription (doc-flow-extractor.js:2361-2370)
def is_pure_description(text):
    value = str(text or "").strip()
    if looks_imperative_runtime_instruction(value):
        return False
    if re.match(r"^[A-Z][^.?!]{10,}\.$", value) and not any(k in value.lower() for k in ACTION_KEYWORDS):
        return True
    if (re.match(r"^(?:this|these|the file|the document|corrections|insights|knowledge gaps)\b", value, re.IGNORECASE)
            and re.search(r"\b(?:is|are|contains|captures|describes|lists|defines)\b", value, re.IGNORECASE)):
        return True
    return False



# Port of extractSemanticOperationsFromLine (doc-flow-extractor.js:2372-2464)
def extract_semantic_operations_from_line(config):
    line = config.get("line")
    owner_doc = config.get("ownerDoc")
    line_number = config.get("lineNumber")
    section = config.get("section")
    doc_index = config.get("docIndex")
    source_line = str(line or "").strip()
    clean_line = strip_markdown_list_marker(source_line)
    conditions = extract_line_conditions(clean_line)
    operations = []
    anchor_route = extract_skill_anchor_route_operation({
        "sourceLine": source_line,
        "cleanLine": clean_line,
        "ownerDoc": owner_doc,
        "lineNumber": line_number,
        "section": section,
        "docIndex": doc_index,
    })
    if anchor_route:
        return [anchor_route]

    if (not is_actionable_instruction_line(clean_line)
            and not is_semantic_instruction_line(clean_line)
            and len(extract_file_refs_from_line(clean_line)) == 0
            and len(conditions) == 0):
        return operations

    if len(conditions) > 0:
        operation_type = infer_condition_operation_type(conditions)
        action = OPERATION_DOC_ACTION.get(operation_type) or "condition"
        target_doc = semantic_target_ref(owner_doc, operation_type)
        operations.append({
            "action": action,
            "operationType": operation_type,
            "targetDoc": target_doc,
            "stepRefs": [],
            "sourceLine": source_line,
            "formalSemantics": build_formal_semantics({
                "operationType": operation_type,
                "action": action,
                "ownerDoc": owner_doc,
                "line": line_number,
                "section": section,
                "instructionText": source_line,
                "clauseText": "; ".join(_cond_texts(conditions)),
                "targets": [{"type": "instruction", "value": target_doc, "raw": clean_line}],
                "conditions": conditions,
            }),
        })

    for clause in split_instruction_clauses(clean_line):
        clause_text = clause.strip()
        if not clause_text or not is_actionable_clause(clause_text):
            continue
        operation_type = infer_operation_type(clause_text)
        if operation_type == "condition" and len(operations) > 0:
            continue
        action = OPERATION_DOC_ACTION.get(operation_type) or infer_action_from_line(clause_text, -1)
        target_info = extract_operation_targets(clause_text, owner_doc, doc_index)
        object_info = infer_data_object_from_clause(clause_text, operation_type)
        target_doc = target_info["primaryTarget"] or semantic_target_ref(owner_doc, operation_type)
        step_refs = target_info["fileRefs"]
        fallback_object = object_info.get("consumed") or object_info.get("produced") or {}

        operations.append({
            "action": action,
            "operationType": operation_type,
            "targetDoc": target_doc,
            "stepRefs": step_refs,
            "sourceLine": clause_text,
            "objectKey": fallback_object.get("key") or "",
            "objectText": fallback_object.get("text") or "",
            "consumedObject": object_info.get("consumed"),
            "producedObject": object_info.get("produced"),
            "formalSemantics": build_formal_semantics({
                "operationType": operation_type,
                "action": action,
                "ownerDoc": owner_doc,
                "line": line_number,
                "section": section,
                "instructionText": source_line,
                "clauseText": clause_text,
                "targets": target_info["targets"],
                "conditions": conditions,
            }),
        })

    return dedupe_semantic_operations(operations)


def _cond_texts(conditions):
    # JS `conditions.join('; ')` on an array of {type,text} coerces each object to
    # "[object Object]". The clauseText only feeds evidence.text; the JS behavior
    # here is actually the object list joined — but conditions passed to this call
    # site is the SAME array of objects, and JS join stringifies each to
    # "[object Object]". Reproduce that exactly.
    return ["[object Object]" for _ in (conditions or [])]


# Port of extractSkillAnchorRouteOperation (doc-flow-extractor.js:2466-2525)
def extract_skill_anchor_route_operation(config=None):
    config = config or {}
    owner_doc = normalize_doc_path(config.get("ownerDoc") or "")
    if owner_doc != "SKILL.md":
        return None

    clean_line = str(config.get("cleanLine") or "").strip()
    if "|" not in clean_line:
        return None

    cells = parse_markdown_table_cells(clean_line)
    if len(cells) < 2:
        return None

    header_text = str(config.get("section") or "").lower()
    action_text = " | ".join(cells[1:])
    route_section = bool(re.search(
        r"\b(quick reference|situation|action|trigger|route|routing|workflow|policy|when)\b", header_text
    ))
    route_action = looks_imperative_runtime_instruction(action_text) or bool(re.search(
        r"\b(log|append|write|promote|review|send|create|update|consider|link)\b", action_text, re.IGNORECASE
    ))
    if not route_section or not route_action:
        return None

    situation = cells[0]
    route_conditions = [{"type": infer_condition_kind(situation), "text": situation}]
    operation_type = infer_operation_type(action_text)
    action = OPERATION_DOC_ACTION.get(operation_type) or infer_action_from_line(action_text, -1)
    target_info = extract_operation_targets(action_text, owner_doc, config.get("docIndex"))
    object_info = infer_data_object_from_clause(action_text, operation_type)
    target_doc = target_info["primaryTarget"] or semantic_target_ref(owner_doc, action_text)
    fallback_object = object_info.get("consumed") or object_info.get("produced") or {}
    formal_semantics = build_formal_semantics({
        "operationType": operation_type,
        "action": action,
        "ownerDoc": owner_doc,
        "line": config.get("lineNumber"),
        "section": config.get("section"),
        "instructionText": config.get("sourceLine"),
        "clauseText": action_text,
        "targets": target_info["targets"],
        "conditions": route_conditions,
    })
    formal_semantics["evidence"] = {
        **(formal_semantics.get("evidence") or {}),
        "method": "skill_anchor_route",
        "source_line": config.get("sourceLine") or clean_line,
        "situation": situation,
        "action_text": action_text,
    }

    return {
        "action": action,
        "operationType": operation_type,
        "targetDoc": target_doc,
        "stepRefs": target_info["fileRefs"],
        "sourceLine": config.get("sourceLine") or clean_line,
        "objectKey": fallback_object.get("key") or "",
        "objectText": fallback_object.get("text") or "",
        "consumedObject": object_info.get("consumed"),
        "producedObject": object_info.get("produced"),
        "formalSemantics": formal_semantics,
    }


# Port of producesObject (doc-flow-extractor.js:2527-2529)
def produces_object(operation_type):
    return operation_type in ("read", "transform", "model_inference", "external_egress", "write", "produce_artifact")


# Port of inferDataObjectFromClause (doc-flow-extractor.js:2531-2545)
def infer_data_object_from_clause(clause_text, operation_type):
    text = str(clause_text or "").strip()
    if not text or not is_english_text(text):
        return empty_object_usage()
    lower = text.lower()
    consumed = infer_consumed_object(lower, operation_type)
    produced = infer_produced_object(lower, operation_type, consumed)
    nc = normalize_object_info(consumed)
    np = normalize_object_info(produced)
    return {
        "consumed": nc,
        "produced": np,
        "key": (nc or {}).get("key") or (np or {}).get("key") or "",
        "text": (nc or {}).get("text") or (np or {}).get("text") or "",
    }


# Port of inferConsumedObject (doc-flow-extractor.js:2547-2572)
def infer_consumed_object(lower, operation_type):
    if operation_type == "read":
        return None
    if operation_type == "write":
        match = re.search(r"\b(?:write|save|store|persist|export)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+(?:to|into|in|locally|as)\b", lower, re.IGNORECASE)
        return object_info_from_text((match.group(1) if match else None) or find_known_object_phrase(lower))
    if operation_type == "produce_artifact":
        consumed_text = infer_produced_artifact_consumed_text(lower)
        if not consumed_text or not is_readable_data_object(consumed_text):
            return None
        return object_info_from_text(consumed_text)
    if operation_type == "transform":
        match = re.search(r"\b(?:summarize|digest|brief|extract|classify|parse|analyze|redact|mask|sanitize)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+(?:into|as|to)\b|\s+and\b|$)", lower, re.IGNORECASE)
        return object_info_from_text((match.group(1) if match else None) or find_known_object_phrase(lower))
    if operation_type in ("external_egress", "model_inference", "invoke_tool"):
        match = re.search(r"\b(?:send|upload|post|call|invoke|provide|pass|forward)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+(?:to|into|in|via|through)\b", lower, re.IGNORECASE)
        return object_info_from_text((match.group(1) if match else None) or find_known_object_phrase(lower))
    return object_info_from_text(find_known_object_phrase(lower))


# Port of inferProducedObject (doc-flow-extractor.js:2574-2598)
def infer_produced_object(lower, operation_type, consumed):
    if operation_type == "read":
        match = re.search(r"\b(?:read|get|fetch|retrieve|load|search|query|open|inspect)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+and\b|\s+to\b|$)", lower, re.IGNORECASE)
        return object_info_from_text((match.group(1) if match else None) or find_known_object_phrase(lower))
    if operation_type == "produce_artifact":
        match = re.search(r"\b(?:generate|create|produce|output|build|compose|draft)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+(?:about|from|using|based\s+on|with)\b|\s+and\b|\s+then\b|$)", lower, re.IGNORECASE)
        return object_info_from_text((match.group(1) if match else None) or find_known_object_phrase(lower))
    if operation_type == "transform":
        explicit = re.search(r"\b(?:into|as|to)\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,3})(?:\s+and\b|$)", lower, re.IGNORECASE)
        if explicit:
            return object_info_from_text(explicit.group(1))
        if re.search(r"\b(summarize|summary|digest|brief)\b", lower, re.IGNORECASE):
            return object_info_from_text("summary")
        if re.search(r"\b(redact|mask|sanitize|scrub)\b", lower, re.IGNORECASE):
            return object_info_from_text("safe content")
        if re.search(r"\bextract\b", lower, re.IGNORECASE):
            return object_info_from_text(infer_extracted_object(lower) or "extracted field")
    if operation_type == "write":
        return consumed
    return None


# Port of findKnownObjectPhrase (doc-flow-extractor.js:2600-2611)
def find_known_object_phrase(text):
    patterns = [
        r"\b(email content|mail content|customer records|chat history|conversation history|invoice pdf|invoice document|file content|report content|analysis result|user profile|customer profile|message content|raw report)\b",
        r"\b(?:the|a|an)\s+(summary|report|profile|message|file|document|invoice|attachment|email|record|records|result)\b",
        r"\b(?:the|a|an)?\s*([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,2})\s+(?:content|records|history|profile|message)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, str(text or ""), re.IGNORECASE)
        if match:
            return (match.group(1) if match.lastindex else match.group(0) or "").strip()
    return ""


# Port of inferProducedArtifactConsumedText (doc-flow-extractor.js:2613-2618)
def infer_produced_artifact_consumed_text(text):
    value = str(text or "").strip()
    match = re.search(r"\b(?:about|from|using|based\s+on|with)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+and\b|\s+then\b|$)", value, re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()


# Port of normalizeObjectClassText (doc-flow-extractor.js:2620-2622)
def normalize_object_class_text(text):
    return re.sub(r"[_.-]+", " ", clean_object_text(text)).strip()


# Port of isAbstractContextObject (doc-flow-extractor.js:2624-2634)
def is_abstract_context_object(text):
    normalized = normalize_object_class_text(text)
    if not normalized:
        return False
    patterns = [
        r"^(?:current|this|that)\s+(?:ai|agent|assistant|task|context|state|request|instruction|workflow|skill|answer|response|conversation|session|environment)$",
        r"^(?:current\s+)?(?:ai|agent|assistant|task|context|state|request|instruction|workflow|skill|answer|response|work)$",
        r"^(?:assistant|agent|model|ai)\s+(?:behavior|behaviour|state|policy|capability|response|answer)$",
        r"^(?:this\s+)?(?:skill|workflow)$",
    ]
    return any(re.search(p, normalized, re.IGNORECASE) for p in patterns)


# Port of isArtifactLikeObject (doc-flow-extractor.js:2636-2644)
def is_artifact_like_object(text):
    normalized = normalize_object_class_text(text)
    if not normalized or is_abstract_context_object(normalized):
        return False
    patterns = [
        r"^(?:report|summary|result|document|file)$",
        r"^(?:analysis|final|draft|generated|output)\s+(?:report|summary|result|document|file)$",
    ]
    return any(re.search(p, normalized, re.IGNORECASE) for p in patterns)


# Port of isReadableDataObject (doc-flow-extractor.js:2646-2665)
def is_readable_data_object(text):
    normalized = normalize_object_class_text(text)
    if not normalized or is_abstract_context_object(normalized):
        return False
    if is_artifact_like_object(normalized):
        return True
    patterns = [
        r"\b(?:email|mail)(?:\s+(?:content|message|body|thread|attachment))?\b",
        r"\b(?:customer|user|client|patient|employee|account)?\s*records?\b",
        r"\b(?:chat|conversation|message)\s+history\b",
        r"\b(?:user|customer|account)?\s*profile\b",
        r"\b(?:file|document|report|message|email|mail|invoice|pdf|attachment)\s+content\b",
        r"\binvoice\s+(?:pdf|document|file)?\b",
        r"\b(?:database|table|row|rows|column|columns|query result|dataset|spreadsheet)\b",
        r"\bbrowser\s+(?:cookie|cookies|history|data)\b|\bcookies?\b",
        r"\bcalendar(?:\s+(?:event|events|entry|entries))?\b",
        r"\bcontacts?\b",
        r"\blogs?\b",
        r"\b(?:message|attachment|note|notes)\b",
    ]
    return any(re.search(p, normalized, re.IGNORECASE) for p in patterns)


# Port of inferExtractedObject (doc-flow-extractor.js:2667-2670)
def infer_extracted_object(text):
    match = re.search(r"\bextract\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,2})\s+from\b", str(text or ""), re.IGNORECASE)
    return match.group(1) if match else ""


# Port of objectInfoFromText (doc-flow-extractor.js:2672-2676)
def object_info_from_text(value):
    text = clean_object_text(value)
    key = object_key_from_text(text)
    return {"key": key, "text": text} if key else None


# Port of normalizeObjectInfo (doc-flow-extractor.js:2678-2681)
def normalize_object_info(value):
    if not value or not isinstance(value, dict):
        return None
    return object_info_from_text(value.get("text") or value.get("key") or "")


# Port of emptyObjectUsage (doc-flow-extractor.js:2683-2685)
def empty_object_usage():
    return {"consumed": None, "produced": None, "key": "", "text": ""}


# Port of isEnglishText (doc-flow-extractor.js:2687-2689)
def is_english_text(text):
    return bool(re.match(r"^[\x00-\x7F]+$", str(text or "")))


# Port of cleanObjectText (doc-flow-extractor.js:2691-2699)
def clean_object_text(value):
    text = str(value or "").lower()
    text = re.sub(r"\b(the|a|an|it|locally|local|raw|full|original)\b", " ", text)
    text = re.sub(r"\b(to|into|in|as|via|through|with|from|for|on|at)\b.*$", " ", text)
    text = re.sub(r"[^\w\s.-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Port of objectKeyFromText (doc-flow-extractor.js:2701-2705)
def object_key_from_text(value):
    cleaned = clean_object_text(value)
    if not cleaned or len(cleaned) < 3:
        return ""
    return stable_slug(cleaned)


# Port of referencesPriorObject (doc-flow-extractor.js:2707-2709)
def references_prior_object(text=""):
    return bool(re.search(r"\b(it|this|that|them|the same|same data|same content|summary)\b", str(text or ""), re.IGNORECASE))


# Port of buildImplicitObjectReadSemantics (doc-flow-extractor.js:2711-2735)
def build_implicit_object_read_semantics(config):
    object_text = config.get("objectText") or config.get("objectKey") or "data"
    target = {"type": infer_object_target_type(object_text), "value": object_text, "raw": object_text}
    semantics = build_formal_semantics({
        "operationType": "read",
        "action": "read",
        "ownerDoc": config.get("ownerDoc"),
        "line": config.get("line"),
        "section": config.get("section"),
        "instructionText": config.get("instructionText"),
        "clauseText": f"Implicitly read {object_text}",
        "targets": [target],
        "conditions": [],
    })
    return {
        **semantics,
        "confidence": min(0.72, _js_number(semantics.get("confidence") or 0.6)),
        "evidence": {
            **semantics["evidence"],
            "method": "implicit_object_read",
            "object_key": config.get("objectKey") or object_key_from_text(object_text),
            "source_line": config.get("instructionText") or semantics["evidence"].get("source_line") or "",
        },
    }


# Port of buildDocSourceContext (doc-flow-extractor.js:2737-2768)
def build_doc_source_context(config):
    doc = config.get("doc") or {}
    return build_source_context({
        "content": doc.get("content") or "",
        "file": doc.get("file") or "",
        "line": config.get("line") or 0,
        "section": config.get("section") or "",
        "sourceText": config.get("sourceLine") or "",
        "action": config.get("action") or "",
        "operationType": config.get("operationType") or "",
        "actionSnippet": config.get("actionSnippet") or "",
        "extractionMethod": config.get("extractionMethod") or "doc_flow",
        "trigger": config.get("trigger") or "",
        "sourceRole": doc.get("source_role") or ("semantic_anchor" if normalize_doc_path(doc.get("file") or "") == "SKILL.md" else "extraction_source"),
        "sourceType": "markdown",
        "grounded": config.get("grounded", True),
        "derived": config.get("derived", False),
        "requiresReview": config.get("requiresReview", False),
    })


# Port of inferObjectTargetType (doc-flow-extractor.js:2770-2776)
def infer_object_target_type(object_text):
    text = str(object_text or "").lower()
    if re.search(r"\b(email|mail|message|chat|conversation)\b", text):
        return "object"
    if re.search(r"\b(file|pdf|document|report|attachment)\b", text):
        return "file"
    if re.search(r"\b(record|records|database|table|row)\b", text):
        return "object"
    return "object"



# Port of stripMarkdownListMarker (doc-flow-extractor.js:2778-2785)
def strip_markdown_list_marker(line):
    text = str(line or "").strip()
    text = re.sub(r"^[-*+]\s+", "", text)
    text = re.sub(r"^\d+[.)]\s+", "", text)
    text = re.sub(r"^\|\s*|\s*\|$", "", text)
    return text.strip()


_UNORDERED_MARKER_RE = re.compile(r"^(\s*)[-*+]\s+")
_ORDERED_MARKER_RE = re.compile(r"^(\s*)\d+[.)]\s+")


# Port of detectListMarker (doc-flow-extractor.js:2793-2800)
def detect_list_marker(raw_line):
    line = str(raw_line or "")
    ordered = _ORDERED_MARKER_RE.match(line)
    if ordered:
        return {"listType": "ordered", "indent": len(ordered.group(1)), "markerLen": len(ordered.group(0))}
    unordered = _UNORDERED_MARKER_RE.match(line)
    if unordered:
        return {"listType": "unordered", "indent": len(unordered.group(1)), "markerLen": len(unordered.group(0))}
    return None


# Port of segmentMarkdownBlocks (doc-flow-extractor.js:2811-2904)
def segment_markdown_blocks(lines, sections):
    directives = {}
    rows = lines if isinstance(lines, list) else []

    in_code = False
    last_non_list_text = ""
    last_non_list_line = -1
    current_list_scope = None
    in_list = False

    idx = 0
    while idx < len(rows):
        raw = rows[idx]
        trimmed = str(raw or "").strip()

        if re.match(r"^```+", trimmed):
            in_code = not in_code
            last_non_list_text = ""
            current_list_scope = None
            in_list = False
            idx += 1
            continue
        if in_code:
            idx += 1
            continue
        if not trimmed:
            last_non_list_text = ""
            current_list_scope = None
            in_list = False
            idx += 1
            continue
        if re.match(r"^#{1,6}\s+", trimmed):
            last_non_list_text = ""
            current_list_scope = None
            in_list = False
            idx += 1
            continue
        if re.match(r"^\|?\s*[-:| ]+\|?\s*$", trimmed):
            last_non_list_text = ""
            current_list_scope = None
            in_list = False
            idx += 1
            continue

        marker = detect_list_marker(raw)
        if not marker:
            last_non_list_text = trimmed
            last_non_list_line = idx
            current_list_scope = None
            in_list = False
            idx += 1
            continue

        if not in_list:
            lead_clean = re.sub(r"[*_`]+", "", last_non_list_text).strip()
            lead_ends_colon = bool(re.search(r"[:：]\s*$", lead_clean))
            lead_in_is_disclaimer = (
                last_non_list_line == idx - 1
                and (is_negated_action_text(lead_clean)
                     or (lead_ends_colon and _NEGATION_HEADING_RE.search(lead_clean)))
            )
            current_list_scope = "disclaimer" if lead_in_is_disclaimer else None
            in_list = True
        block_scope = current_list_scope

        parts = [str(raw)]
        last = idx
        j = idx + 1
        while j < len(rows):
            cont_raw = rows[j]
            cont_trim = str(cont_raw or "").strip()
            if not cont_trim:
                break
            if re.match(r"^```+", cont_trim):
                break
            if re.match(r"^#{1,6}\s+", cont_trim):
                break
            if re.match(r"^\|?\s*[-:| ]+\|?\s*$", cont_trim):
                break
            if detect_list_marker(cont_raw):
                break
            cont_indent = len(re.match(r"^(\s*)", cont_raw).group(1))
            if cont_indent < marker["indent"] + marker["markerLen"]:
                break
            parts.append(cont_trim)
            last = j
            j += 1

        merged_parts = [str(part) if i == 0 else part for i, part in enumerate(parts)]
        merged_text = re.sub(r"\s+", " ", " ".join(merged_parts)).strip()

        directives[idx] = {"role": "item_start", "blockScope": block_scope, "listType": marker["listType"], "mergedText": merged_text}
        for k in range(idx + 1, last + 1):
            directives[k] = {"role": "continuation"}
        idx = last  # advance past folded continuation lines

        last_non_list_text = ""
        last_non_list_line = -1
        idx += 1

    return directives


# Port of splitInstructionClauses (doc-flow-extractor.js:2906-2914)
def split_instruction_clauses(line):
    normalized = str(line or "").replace("\r", "").strip()
    parts = _SEMANTIC_CONNECTOR_RE.split(normalized)
    result = []
    for part in parts:
        if part is None:
            continue
        p = re.sub(r"^,+|,+$", "", part.strip()).strip()
        if p:
            result.append(p)
    return result


# Port of extractLineConditions (doc-flow-extractor.js:2916-2935)
def extract_line_conditions(line):
    conditions = []
    seen = set()
    for regex in _CONDITION_REGEXES:
        for match in regex.finditer(line):
            raw = re.sub(r"[,:]+$", "", str(match.group(0) or "").strip())
            if not raw or raw.lower() in seen:
                continue
            seen.add(raw.lower())
            conditions.append({"type": infer_condition_kind(raw), "text": raw})
    return conditions


# Port of inferConditionKind (doc-flow-extractor.js:2937-2944)
def infer_condition_kind(condition_text):
    text = normalize_for_search(condition_text)
    if re.search(r"fail|failed|error", text):
        return "failure"
    if re.search(r"correct|wrong|reject|mistake", text):
        return "user_correction"
    if re.search(r"periodic|recurring|weekly|daily|monthly|heartbeat", text):
        return "periodic"
    if re.search(r"3x|3\+|repeated", text):
        return "repetition"
    return "condition"


# Port of inferConditionOperationType (doc-flow-extractor.js:2946-2952)
def infer_condition_operation_type(conditions):
    kinds = set(item.get("type") for item in (conditions or []))
    if "failure" in kinds or "user_correction" in kinds or "periodic" in kinds:
        return "trigger"
    return "condition"


# Port of isActionableClause (doc-flow-extractor.js:2954-2962)
def is_actionable_clause(clause_text):
    text = str(clause_text or "").strip().lower()
    if not text:
        return False
    if len(extract_file_refs_from_line(text)) > 0:
        return True
    if any(str(keyword).lower() in text for keyword in ACTION_KEYWORDS):
        return True
    return any(
        any(str(keyword).lower() in text for keyword in d["keywords"])
        for d in OPERATION_TYPE_DEFINITIONS
    )


# Port of isSemanticInstructionLine (doc-flow-extractor.js:2964-2969)
def is_semantic_instruction_line(line):
    text = normalize_for_search(line)
    return any(
        any(normalize_for_search(keyword) in text for keyword in d["keywords"])
        for d in OPERATION_TYPE_DEFINITIONS
    )


_NEGATION_LEAD_RE = re.compile(
    r"^(?:it\s+|this\s+skill\s+|the\s+skill\s+|we\s+|agent\s+)?(?:does not|doesn't|do not|don't|will not|won't|cannot|can't|never|no longer|must not|should not|shouldn't)\b"
)
_NEGATION_HEADING_RE = re.compile(
    r"\b(?:does not do|not do|never|limitations?|out of scope|disclaimer|non-goals?|what (?:it|this|the skill) (?:does not|doesn't|will not|won't|cannot|can't))\b",
    re.IGNORECASE,
)


# Port of isNegatedActionText (doc-flow-extractor.js:2977-2984)
def is_negated_action_text(text):
    value = str(text or "").strip().lower()
    if not value:
        return False
    if _NEGATION_LEAD_RE.search(value):
        return True
    if re.search(r"\bwithout\s+(?:\w+ing|any|real|sending|uploading|storing|writing)\b", value):
        return True
    return False


# Port of isNegationScopeHeading (doc-flow-extractor.js:2986-2988)
def is_negation_scope_heading(section):
    return bool(_NEGATION_HEADING_RE.search(str(section or "")))


# Port of inferOperationType (doc-flow-extractor.js:2990-3034)
def infer_operation_type(text):
    normalized = normalize_for_search(text)
    if is_negated_action_text(text):
        return "guard"
    starts_with_write_verb = bool(re.match(r"^(?:write|save|store|persist|export)\b", normalized))
    starts_with_produce_verb = bool(re.match(r"^(?:generate|create|produce|output|build|compose|draft)\b", normalized))

    if re.search(r"\b(review|reflect|heartbeat|periodic|recurring)\b", normalized):
        return "review"
    if re.search(r"\b(read|get|fetch|retrieve|load|search|query|open|inspect)\b", normalized):
        return "read"
    if re.search(r"\b(send|provide|pass|route|forward)\b[\s\S]{0,80}\b(model|llm|chat|completion|gpt|claude|gemini|openai|anthropic)\b", normalized):
        return "model_inference"
    if (re.search(r"\b(webhook|http|https|external|third party|third-party|post|upload|publish|share)\b", normalized)
            or re.search(r"\b(call|invoke|send)\b[\s\S]{0,80}\b(api|endpoint|service|weather api)\b", normalized)):
        return "external_egress"
    if starts_with_write_verb:
        return "write"
    if starts_with_produce_verb:
        return "produce_artifact"
    if re.search(r"\b(redact|mask|sanitize|scrub|strip|remove)\b[\s\S]{0,80}\b(secret|secrets|credential|credentials|api key|token|password|pii|email|phone|address)\b", normalized):
        return "transform"
    if re.search(r"\b(summarize|summary|digest|brief|classify|extract|parse|analyze)\b", normalized):
        return "transform"
    if re.search(r"\b(save|store|write|persist|export)\b", normalized):
        return "write"
    for definition in OPERATION_TYPE_DEFINITIONS:
        if any(normalize_for_search(keyword) in normalized for keyword in definition["keywords"]):
            return definition["type"]
    return "read"


# Port of extractOperationTargets (doc-flow-extractor.js:3036-3076)
def extract_operation_targets(clause_text, owner_doc, doc_index):
    targets = []
    file_refs = []

    for ref_info in extract_file_refs_from_line(clause_text):
        resolved = resolve_doc_reference(ref_info["ref"], owner_doc, doc_index)
        file_refs.append(resolved)
        targets.append({"type": "file", "value": resolved, "raw": ref_info["ref"]})

    for tool_name in extract_tool_refs_from_line(clause_text):
        targets.append({"type": "tool", "value": tool_name, "raw": tool_name})

    for tier in extract_memory_tiers(clause_text):
        targets.append({"type": "memory_tier", "value": tier, "raw": tier})

    for semantic_target in extract_semantic_targets(clause_text):
        targets.append(semantic_target)

    primary = next((t for t in targets if t["type"] == "file"), None) or (targets[0] if targets else None)
    deduped = dedupe_targets(targets if len(targets) > 0 else [{"type": "document", "value": owner_doc, "raw": owner_doc}])
    return {
        "targets": deduped,
        "fileRefs": list(dict.fromkeys(normalize_doc_path(f) for f in file_refs)),
        "primaryTarget": semantic_target_ref(owner_doc, primary["value"]) if primary else owner_doc,
    }


# Port of extractToolRefsFromLine (doc-flow-extractor.js:3078-3088)
def extract_tool_refs_from_line(line):
    refs = []
    for match in re.finditer(r"`?([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)`?", line):
        value = match.group(1)
        if re.search(r"\.md$", value, re.IGNORECASE):
            continue
        refs.append(value)
    return list(dict.fromkeys(refs))


# Port of extractMemoryTiers (doc-flow-extractor.js:3090-3097)
def extract_memory_tiers(line):
    tiers = []
    lower = str(line or "").lower()
    if re.search(r"\bhot\b", lower):
        tiers.append("HOT")
    if re.search(r"\bwarm\b", lower):
        tiers.append("WARM")
    if re.search(r"\bcold\b", lower):
        tiers.append("COLD")
    return tiers


# Port of extractSemanticTargets (doc-flow-extractor.js:3099-3111)
def extract_semantic_targets(line):
    lower = str(line or "").lower()
    targets = []
    if re.search(r"memory", lower):
        targets.append({"type": "memory", "value": "memory", "raw": "memory"})
    if re.search(r"log", lower):
        targets.append({"type": "artifact", "value": "logs", "raw": "logs"})
    if re.search(r"correction", lower):
        targets.append({"type": "artifact", "value": "corrections", "raw": "corrections"})
    if re.search(r"report", lower):
        targets.append({"type": "artifact", "value": "report", "raw": "report"})
    if re.search(r"note|notes", lower):
        targets.append({"type": "artifact", "value": "notes", "raw": "notes"})
    return targets


# Port of dedupeTargets (doc-flow-extractor.js:3113-3123)
def dedupe_targets(targets):
    seen = set()
    result = []
    for target in targets or []:
        key = f"{target.get('type')}:{target.get('value')}"
        if key in seen:
            continue
        seen.add(key)
        result.append(target)
    return result


# Port of semanticTargetRef (doc-flow-extractor.js:3125-3131)
def semantic_target_ref(owner_doc, value):
    normalized = normalize_doc_path(value or "")
    if not normalized:
        return owner_doc
    if re.search(r"\.md$", normalized, re.IGNORECASE) or "/" in normalized:
        return normalized
    slug = file_slug(normalized)
    return f"semantic/{slug if slug and slug != 'doc' else stable_slug(normalized)}"


# Port of stableSlug (doc-flow-extractor.js:3133-3146)
def stable_slug(value):
    text = str(value or "")
    ascii_ = re.sub(r"^_+|_+$", "", re.sub(r"[^a-zA-Z0-9]+", "_", text)).lower()
    if ascii_:
        return ascii_
    hash_ = 0
    for ch in text:
        hash_ = _to_int32((hash_ << 5) - hash_ + ord(ch))
    return f"target_{_base36(abs(hash_))}"


def _to_int32(n):
    n &= 0xFFFFFFFF
    if n >= 0x80000000:
        n -= 0x100000000
    return n


def _base36(n):
    if n == 0:
        return "0"
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while n:
        out = digits[n % 36] + out
        n //= 36
    return out


# Port of buildFormalSemantics (doc-flow-extractor.js:3148-3173)
def build_formal_semantics(config):
    operation_type = config.get("operationType") or "read"
    action = config.get("action") or OPERATION_DOC_ACTION.get(operation_type) or "read"
    targets = dedupe_targets(config.get("targets") or [])
    effects = OPERATION_EFFECTS.get(operation_type) or []
    return {
        "operation_type": operation_type,
        "actor": "llm",
        "inputs": build_formal_inputs(operation_type, targets, config.get("conditions")),
        "outputs": build_formal_outputs(operation_type, targets),
        "targets": targets,
        "conditions": config.get("conditions") or [],
        "effects": effects,
        "confidence": calculate_semantic_confidence(operation_type, targets, config.get("conditions")),
        "evidence": {
            "text": config.get("clauseText") or config.get("instructionText") or "",
            "source_line": config.get("instructionText") or "",
            "file": normalize_doc_path(config.get("ownerDoc")),
            "line": _int(config.get("line") or 0),
            "section": config.get("section") or "",
            "method": "rule",
        },
        "action": action,
    }


# Port of buildFormalInputs (doc-flow-extractor.js:3175-3189)
def build_formal_inputs(operation_type, targets, conditions):
    inputs = []
    if len(conditions or []) > 0:
        inputs.append({"name": "condition_signal", "type": "condition"})
    if operation_type in ("write", "transform", "produce_artifact", "verify", "decision", "guard"):
        inputs.append({"name": "llm_context", "type": "context"})
    for target in targets or []:
        if operation_type in ("read", "review", "verify"):
            inputs.append({"name": target["value"], "type": target["type"]})
    return inputs


# Port of buildFormalOutputs (doc-flow-extractor.js:3191-3202)
def build_formal_outputs(operation_type, targets):
    if operation_type in ("read", "review", "verify"):
        return [{"name": "context", "type": "string"}]
    if operation_type in ("decision", "condition", "trigger", "guard"):
        return [{"name": "branch_state", "type": "object"}]
    if operation_type == "invoke_tool":
        return [{"name": "tool_result", "type": "object"}]
    return [{"name": t["value"], "type": t.get("type") or "artifact"} for t in (targets or [])]


# Port of calculateSemanticConfidence (doc-flow-extractor.js:3204-3210)
def calculate_semantic_confidence(operation_type, targets, conditions):
    confidence = 0.55
    if operation_type and operation_type != "read":
        confidence += 0.1
    if len(targets or []) > 0:
        confidence += 0.15
    if len(conditions or []) > 0:
        confidence += 0.1
    return min(0.95, confidence)


# Port of dedupeSemanticOperations (doc-flow-extractor.js:3212-3225)
def dedupe_semantic_operations(operations):
    seen = set()
    result = []
    for operation in operations or []:
        fs_targets = (operation.get("formalSemantics") or {}).get("targets")
        if fs_targets:
            target_key = "|".join(f"{t.get('type')}:{t.get('value')}" for t in fs_targets)
        else:
            target_key = operation.get("targetDoc")
        key = f"{operation.get('operationType')}:{operation.get('action')}:{operation.get('targetDoc')}:{target_key}:{operation.get('sourceLine')}"
        if key in seen:
            continue
        seen.add(key)
        result.append(operation)
    return result


# Port of createFallbackFormalSemantics (doc-flow-extractor.js:3266-3278)
def create_fallback_formal_semantics(config):
    return build_formal_semantics({
        "operationType": config.get("operationType") or "read",
        "action": config.get("action") or "read",
        "ownerDoc": config.get("ownerDoc"),
        "line": config.get("line"),
        "section": config.get("section"),
        "instructionText": config.get("instructionText"),
        "clauseText": config.get("instructionText"),
        "targets": [{"type": "document", "value": config.get("targetDoc") or config.get("ownerDoc"), "raw": config.get("targetDoc") or config.get("ownerDoc")}],
        "conditions": [],
    })


# Port of dedupeConditions (doc-flow-extractor.js:3280-3290)
def dedupe_conditions(conditions):
    seen = set()
    result = []
    for condition in conditions or []:
        key = f"{condition.get('type')}:{condition.get('text')}"
        if key in seen:
            continue
        seen.add(key)
        result.append(condition)
    return result


# Port of buildStepInput (doc-flow-extractor.js:3304-3322)
def build_step_input(action, target_doc):
    base = {"file_path": {"type": "string", "required": False, "example": target_doc}}
    if action == "write":
        base["content"] = {"type": "string", "required": True}
        return base
    if action == "run":
        base["instruction"] = {"type": "string", "required": True}
        return base
    if action in ("condition", "decision", "guard", "transform", "verify", "review"):
        base["context"] = {"type": "string", "required": False}
        return base
    base["context"] = {"type": "string", "required": False}
    return base


# Port of buildStepOutput (doc-flow-extractor.js:3324-3350)
def build_step_output(action):
    if action == "write":
        return {"success": {"type": "boolean"}}
    if action == "run":
        return {"success": {"type": "boolean"}, "result": {"type": "string"}}
    if action in ("condition", "decision", "guard"):
        return {"branch_state": {"type": "object"}, "success": {"type": "boolean"}}
    if action == "transform":
        return {"result": {"type": "string"}, "success": {"type": "boolean"}}
    return {"content": {"type": "string"}, "success": {"type": "boolean"}}


# Port of edgeSourceContextFromNode (doc-flow-extractor.js:3352-3358)
def edge_source_context_from_node(node=None, method=""):
    node = node or {}
    if not node.get("source_context"):
        return None
    return {**node["source_context"], "edge_evidence_method": method}



# Port of addStepPrimaryEdges (doc-flow-extractor.js:3360-3442)
def add_step_primary_edges(edges, step_node):
    if not is_action_flow_node(step_node):
        return
    action = step_node.get("docAction") or step_node.get("action") or "read"

    if action == "write":
        edges.append({
            "source": "llm.inference",
            "target": step_node["name"],
            "type": "doc_instruction",
            "confidence": 0.74,
            "validation_method": "doc_flow",
            "data_flow": {"from_param": "response", "to_param": "content", "data_type": "string"},
            "semantic_reason": f"LLM persists knowledge update via step in {step_node.get('ownerDoc')}",
            "source_context": edge_source_context_from_node(step_node, "doc_flow"),
        })
        return

    if action == "run":
        edges.append({
            "source": "llm.inference",
            "target": step_node["name"],
            "type": "doc_instruction",
            "confidence": 0.69,
            "validation_method": "doc_flow",
            "data_flow": {"from_param": "response", "to_param": "instruction", "data_type": "string"},
            "semantic_reason": f"LLM executes procedural markdown step in {step_node.get('ownerDoc')}",
            "source_context": edge_source_context_from_node(step_node, "doc_flow"),
        })
        edges.append({
            "source": step_node["name"],
            "target": "llm.inference",
            "type": "doc_instruction",
            "confidence": 0.52,
            "validation_method": "doc_flow",
            "data_flow": {"from_param": "result", "to_param": "context", "data_type": "string"},
            "semantic_reason": "Execution result from markdown step feeds back to LLM",
            "source_context": edge_source_context_from_node(step_node, "doc_flow"),
        })
        return

    edges.append({
        "source": "user.query",
        "target": step_node["name"],
        "type": "doc_instruction",
        "confidence": 0.44,
        "validation_method": "doc_flow",
        "data_flow": {"from_param": "query_text", "to_param": "file_path", "data_type": "string"},
        "semantic_reason": f"User request activates markdown step in {step_node.get('ownerDoc')}",
        "source_context": edge_source_context_from_node(step_node, "doc_flow"),
    })
    edges.append({
        "source": step_node["name"],
        "target": "llm.inference",
        "type": "doc_instruction",
        "confidence": 0.66,
        "validation_method": "doc_flow",
        "data_flow": {"from_param": "content", "to_param": "skill_content", "data_type": "string"},
        "semantic_reason": f"Step output from {step_node.get('ownerDoc')} becomes LLM context",
        "source_context": edge_source_context_from_node(step_node, "doc_flow"),
    })


# Port of isActionFlowNode (doc-flow-extractor.js:3444-3446)
def is_action_flow_node(node=None):
    node = node or {}
    return bool(node and node.get("semanticKind") in ("doc_step", "doc_operation") and not node.get("excludeFromFlow"))


# Port of isContextOnlyNode (doc-flow-extractor.js:3448-3454)
def is_context_only_node(node=None):
    node = node or {}
    return bool(
        node and (
            node.get("excludeFromFlow")
            or node.get("semanticKind") in ("doc_definition", "doc_schema", "doc_example", "doc_template", "doc_discard", "doc_review_error")
        )
    )


# Port of sequenceEdgeScope (doc-flow-extractor.js:3466-3469)
def sequence_edge_scope():
    raw = str(os.environ.get("SFG_SEQUENCE_EDGE_SCOPE") or "").strip().lower()
    return "global" if raw == "global" else "section"


# Port of addStepSequenceEdges (doc-flow-extractor.js:3471-3502)
def add_step_sequence_edges(edges, doc_file, steps):
    scope = sequence_edge_scope()
    for i in range(len(steps) - 1):
        current = steps[i]
        nxt = steps[i + 1]
        if not current or not current.get("name") or not nxt or not nxt.get("name"):
            continue
        if scope == "section":
            cur_section = str((current.get("location") or {}).get("section") or "")
            next_section = str((nxt.get("location") or {}).get("section") or "")
            if cur_section != next_section:
                continue
        edges.append({
            "source": current["name"],
            "target": nxt["name"],
            "type": "control_flow",
            "confidence": 0.51,
            "validation_method": "doc_flow",
            "data_flow": {"from_param": "state", "to_param": "state", "data_type": "object"},
            "semantic_reason": f"Sequential markdown steps in {doc_file}",
            "source_context": edge_source_context_from_node(current, "doc_flow_sequence"),
        })


# Port of addObjectProducerEdges (doc-flow-extractor.js:3504-3522)
def add_object_producer_edges(edges, doc_file, steps):
    for step in steps or []:
        if not step or not step.get("objectProducer") or not step.get("name") or step.get("objectProducer") == step.get("name"):
            continue
        edges.append({
            "source": step["objectProducer"],
            "target": step["name"],
            "type": "data_dependency",
            "confidence": 0.68,
            "validation_method": "doc_flow_object_context",
            "data_flow": {"from_param": "content", "to_param": "context", "data_type": "string"},
            "semantic_reason": f"Object context reuse for {step.get('objectKey') or 'data object'} in {doc_file}",
            "source_context": edge_source_context_from_node(step, "doc_flow_object_context"),
        })


# Port of buildDocumentSet (doc-flow-extractor.js:3524-3548)
def build_document_set(skill_data, readme_data):
    md_files = _find_markdown_files_fs((skill_data or {}).get("skillRootDir"))
    docs = []
    for md_file in md_files:
        rel_path = normalize_doc_path(os.path.relpath(md_file, (skill_data or {}).get("skillRootDir")))
        base = os.path.basename(rel_path).lower()
        if base in ("skill.md", "readme.md"):
            continue
        with open(md_file, "r", encoding="utf-8") as handle:
            content = handle.read()
        docs.append({"file": rel_path, "content": content, "sections": extract_sections(content)})

    if len(docs) == 0:
        docs.append({
            "file": "SKILL.md",
            "content": (skill_data or {}).get("content"),
            "sections": (skill_data or {}).get("sections") or [],
        })

    return _dedupe_docs(docs)


# Port of dedupeDocs (doc-flow-extractor.js:3550-3565)
def _dedupe_docs(docs):
    by_file = {}
    for doc in docs:
        file = normalize_doc_path(doc.get("file"))
        if file not in by_file:
            by_file[file] = {**doc, "file": file}
            continue
        existing = by_file[file]
        if len(existing.get("content") or "") >= len(doc.get("content") or ""):
            continue
        by_file[file] = {**doc, "file": file}
    return list(by_file.values())


# Port of buildDocIndex (doc-flow-extractor.js:3567-3581)
def build_doc_index(docs):
    by_canonical = {}
    by_basename = {}
    for doc in docs:
        canonical = normalize_doc_path(doc.get("file"))
        by_canonical[canonical.lower()] = canonical
        base = posixpath.basename(canonical).lower()
        by_basename.setdefault(base, []).append(canonical)
    return {"byCanonical": by_canonical, "byBasename": by_basename}


# Port of resolveDocReference (doc-flow-extractor.js:3583-3604)
def resolve_doc_reference(raw_ref, owner_doc, doc_index):
    direct = normalize_doc_path(raw_ref)
    direct_key = direct.lower()
    if direct_key in doc_index["byCanonical"]:
        return doc_index["byCanonical"][direct_key]

    owner_dir = normalize_doc_path(posixpath.dirname(normalize_doc_path(owner_doc)))
    relative = normalize_doc_path(posixpath.normpath(posixpath.join(owner_dir, direct)))
    relative_key = relative.lower()
    if relative_key in doc_index["byCanonical"]:
        return doc_index["byCanonical"][relative_key]

    base = posixpath.basename(direct).lower()
    by_name = doc_index["byBasename"].get(base) or []
    if len(by_name) > 0:
        return by_name[0]

    return direct or raw_ref


# Port of findMarkdownFiles (doc-flow-extractor.js:3606-3625)
def _find_markdown_files_fs(root_dir):
    result = []
    ignored_dirs = {"node_modules", ".git", ".svn", ".hg", "dist", "build", "coverage"}
    if not root_dir:
        return result

    def walk(directory):
        try:
            entries = list(os.scandir(directory))
        except OSError:
            return
        for entry in entries:
            full_path = os.path.join(directory, entry.name)
            if entry.is_dir():
                if entry.name in ignored_dirs:
                    continue
                walk(full_path)
            elif entry.name.lower().endswith(".md"):
                result.append(full_path)

    walk(root_dir)
    return result


# Port of extractFileRefsFromLine (doc-flow-extractor.js:3627-3655)
def extract_file_refs_from_line(line):
    refs = []
    seen = set()

    for match in _BACKTICK_FILE_REF_RE.finditer(line):
        ref = normalize_doc_path(match.group(1))
        if not ref or ref in seen:
            continue
        seen.add(ref)
        refs.append({"ref": ref, "index": match.start()})

    for match in _PLAIN_FILE_REF_RE.finditer(line):
        ref = normalize_doc_path(match.group(1))
        if not ref or ref in seen:
            continue
        seen.add(ref)
        refs.append({"ref": ref, "index": match.start()})

    return refs


# Port of inferActionFromLine (doc-flow-extractor.js:3657-3673)
def infer_action_from_line(line, ref_index=-1):
    lower = str(line or "").lower()
    if re.search(r"\b(read|get|fetch|retrieve|load|search|query|open|inspect)\b", lower):
        return "read"
    if re.search(r"\b(save|store|write|persist|export|record)\b", lower):
        return "write"
    if re.search(r"\b(send|post|upload|call|invoke)\b", lower):
        return "run"
    if ref_index >= 0:
        before = lower[max(0, ref_index - 100):ref_index]
        if any(k in before for k in WRITE_KEYWORDS):
            return "write"
        if any(k in before for k in RUN_KEYWORDS):
            return "run"
        if any(k in before for k in READ_KEYWORDS):
            return "read"
    if any(k in lower for k in WRITE_KEYWORDS):
        return "write"
    if any(k in lower for k in RUN_KEYWORDS):
        return "run"
    if any(k in lower for k in READ_KEYWORDS):
        return "read"
    return "read"


# Port of isActionableInstructionLine (doc-flow-extractor.js:3675-3685)
def is_actionable_instruction_line(trimmed_line):
    text = str(trimmed_line or "").strip().lower()
    if not text:
        return False
    if len(text) < 3:
        return False
    if re.match(r"^>\s*", text):
        return False
    if re.match(r"^([-*+]|\d+[.)])\s+", text):
        return True
    if any(k in text for k in ACTION_KEYWORDS):
        return True
    if re.match(r"^(then|after|before|finally|next)\b", text):
        return True
    return False


# Port of fileSlug (doc-flow-extractor.js:3697-3703)
def file_slug(doc_path):
    slug = normalize_doc_path(doc_path)
    slug = re.sub(r"\.[^.]+$", "", slug)
    slug = re.sub(r"^_+|_+$", "", re.sub(r"[^a-zA-Z0-9]+", "_", slug)).lower()
    return slug or "doc"


# Port of dedupeNodes (doc-flow-extractor.js:3705-3718)
def dedupe_nodes(nodes):
    by_name = {}
    for node in nodes:
        if not node or not node.get("name"):
            continue
        if node["name"] not in by_name:
            by_name[node["name"]] = node
            continue
        existing = by_name[node["name"]]
        by_name[node["name"]] = merge_nodes(existing, node)
    return list(by_name.values())


# Port of mergeNodes (doc-flow-extractor.js:3720-3735)
def merge_nodes(a, b):
    merged_actions = set([*(a.get("docActions") or []), *(b.get("docActions") or [])])
    merged_refs = set([*(a.get("stepRefs") or []), *(b.get("stepRefs") or [])])
    merged = {
        **a,
        **b,
        "description": b.get("description") if (b.get("description") and len(b["description"]) > len(a.get("description") or "")) else a.get("description"),
        "input": {**(a.get("input") or {}), **(b.get("input") or {})},
        "output": {**(a.get("output") or {}), **(b.get("output") or {})},
        "docActions": sorted(merged_actions) if merged_actions else None,
        "stepRefs": sorted(merged_refs) if merged_refs else [],
        "location": prefer_location(a.get("location"), b.get("location")),
        "excludeFromTypeAnalysis": bool(a.get("excludeFromTypeAnalysis") or b.get("excludeFromTypeAnalysis")),
        "excludeFromImplicitLlmEdge": bool(a.get("excludeFromImplicitLlmEdge") or b.get("excludeFromImplicitLlmEdge")),
    }
    # JS assigns docActions = undefined when empty; JSON.stringify drops the key.
    if merged["docActions"] is None:
        del merged["docActions"]
    return merged


# Port of preferLocation (doc-flow-extractor.js:3737-3743)
def prefer_location(a=None, b=None):
    a = a or {}
    b = b or {}
    if not a.get("file"):
        return b
    if not b.get("file"):
        return a
    if a.get("file") == "SKILL.md" and b.get("file") != "SKILL.md":
        return a
    if b.get("file") == "SKILL.md" and a.get("file") != "SKILL.md":
        return b
    a_line = a.get("line") if a.get("line") else 2**53 - 1
    b_line = b.get("line") if b.get("line") else 2**53 - 1
    return a if a_line <= b_line else b


# Port of dedupeEdges (doc-flow-extractor.js:3745-3762)
def dedupe_edges(edges):
    edge_map = {}
    for edge in edges:
        from_param = str((edge.get("data_flow") or {}).get("from_param") or "")
        to_param = str((edge.get("data_flow") or {}).get("to_param") or "")
        key = f"{edge.get('source')}->{edge.get('target')}:{edge.get('type')}:{edge.get('validation_method') or ''}:{from_param}->{to_param}"
        if key not in edge_map:
            edge_map[key] = edge
            continue
        existing = edge_map[key]
        if (edge.get("confidence") or 0) > (existing.get("confidence") or 0):
            edge_map[key] = edge
    return list(edge_map.values())


# Port of extractSections (doc-flow-extractor.js:3764-3801)
def extract_sections(content):
    lines = content.split("\n")
    sections = []
    current_section = None
    current_content = []

    for i in range(len(lines)):
        line = lines[i]
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            if current_section:
                sections.append({**current_section, "content": "\n".join(current_content), "endLine": i})
            current_section = {
                "title": heading_match.group(2).strip(),
                "level": len(heading_match.group(1)),
                "startLine": i + 1,
            }
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections.append({**current_section, "content": "\n".join(current_content), "endLine": len(lines)})

    return sections


# Port of findSectionForLine (doc-flow-extractor.js:3803-3810)
def find_section_for_line(sections, line):
    for section in sections or []:
        if line >= section.get("startLine") and line <= section.get("endLine"):
            return section.get("title")
    return ""


# Port of normalizeForSearch (doc-flow-extractor.js:3812-3818)
def normalize_for_search(value):
    text = str(value if value is not None else "").lower()
    text = re.sub(r"[_-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Port of normalizePositiveInteger (doc-flow-extractor.js:3820-3823)
def normalize_positive_integer(value, fallback):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number == int(number) and number > 0:
        return int(number)
    return fallback


def _is_finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)
