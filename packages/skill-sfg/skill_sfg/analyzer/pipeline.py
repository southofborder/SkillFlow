"""Port of src/index.js SkillFCGAnalyzer.analyze() — the orchestration glue.

Runs the full FCG build pipeline up to (and including) node splitting, which is
where M1 acceptance is measured. RULE-ONLY: this port targets the deterministic,
network-free path (disableLlm=True, semanticLlm=False), which is exactly what the
M1 cross-engine oracle needs — no LLM calls, so JS and Python are bit-for-bit
comparable on node ids / edges / crossing violations.

Ordering is 1:1 with index.js:156-452. The console.log lines are dropped (no side
effects). Output generation (v6 JSON) is NOT here — that is M3/M4. run_pipeline
returns the built FunctionCallGraph plus the merged tool list, which is all the
acceptance harness inspects.

Deferred vs JS: LLM-assisted doc-flow / mediation / constraint resolution / label
assist all no-op under disableLlm; deep-mode edges only fire for mode=='deep'.
"""

import os

from ..parser.skill_parser import parse_skill, parse_readme, find_executable_files
from ..parser.document_context import build_documentation_plan
from ..parser.tool_extractor import extract_tool_calls
from ..parser.script_flow_extractor import extract_script_flow
from ..parser.doc_flow_extractor import (
    extract_document_flow,
    resolve_pending_constraints,
    new_semantic_gate_usage,
    summarize_semantic_gate_usage,
)
from ..classifier.source_sink import create_user_query_source
from .type_analyzer import analyze_type_compatibility
from .llm_validator import validate_pairs
from .fcg_builder import build_fcg, remove_duplicate_edges
from .cycle_remover import remove_cycles, detect_and_tag_cycles, break_only_fake
from .feedback_edge_classifier import classify_feedback_edges, resolve_feedback_llm_review
from .node_splitter import split_graph_nodes
from .callsite_expander import (
    build_call_site_mediation,
    build_endpoint_maps,
    expand_and_map_edges,
)


# Port of shouldAddImplicitToolToLlmEdge (index.js:978-986)
def should_add_implicit_tool_to_llm_edge(tool):
    if not tool or not tool.get("name"):
        return False
    if tool.get("callsite_id"):
        return False
    if tool.get("excludeFromImplicitLlmEdge"):
        return False
    if tool.get("excludeFromTypeAnalysis"):
        return False
    if str(tool["name"]).startswith("doc."):
        return False
    if str(tool["name"]).startswith("rule."):
        return False
    return True


# Port of limitDocumentFlow (index.js:988-1009). max=0 -> no truncation.
def limit_document_flow(document_flow=None, max_nodes=80):
    document_flow = document_flow or {}
    nodes = document_flow.get("nodes") or []
    edges = document_flow.get("edges") or []
    if not isinstance(max_nodes, int) or max_nodes <= 0 or len(nodes) <= max_nodes:
        return {"nodes": nodes, "edges": edges, "truncated": False}

    kept_nodes = nodes[:max_nodes]
    allowed = set()
    for node in kept_nodes:
        if node.get("id"):
            allowed.add(node["id"])
        if node.get("name"):
            allowed.add(node["name"])
    allowed.add("user.query")
    allowed.add("llm.inference")

    return {
        "nodes": kept_nodes,
        "edges": [e for e in edges if e.get("source") in allowed and e.get("target") in allowed],
        "truncated": True,
    }


# Port of limitMediation (index.js:1011-1029). max=0 -> no truncation.
def limit_mediation(mediation=None, existing_tools=None, max_nodes=0):
    mediation = mediation or {}
    existing_tools = existing_tools or []
    nodes = mediation.get("nodes") or []
    edges = mediation.get("edges") or []
    if not isinstance(max_nodes, int) or max_nodes <= 0 or len(nodes) <= max_nodes:
        return {"nodes": nodes, "edges": edges, "truncated": False}

    kept_nodes = nodes[:max_nodes]
    allowed = {t.get("name") for t in existing_tools if t.get("name")}
    for node in kept_nodes:
        if node.get("name"):
            allowed.add(node["name"])

    return {
        "nodes": kept_nodes,
        "edges": [e for e in edges if e.get("source") in allowed and e.get("target") in allowed],
        "truncated": True,
    }


# Port of buildDeepModeEdges (index.js:912-955) — only used when mode=='deep'.
def build_deep_mode_edges(tools):
    import functools

    sortable = [
        {
            "tool": tool,
            "file": str((tool.get("location") or {}).get("file") or ""),
            "line": _num((tool.get("location") or {}).get("line"), 0),
        }
        for tool in tools
    ]

    def cmp(a, b):
        if a["file"] != b["file"]:
            if a["file"] == "SKILL.md":
                return -1
            if b["file"] == "SKILL.md":
                return 1
            if a["file"] == "README.md":
                return -1
            if b["file"] == "README.md":
                return 1
            return _locale_compare(a["file"], b["file"])
        d = a["line"] - b["line"]
        return -1 if d < 0 else (1 if d > 0 else 0)

    sortable.sort(key=functools.cmp_to_key(cmp))

    edges = []
    for i in range(len(sortable) - 1):
        current = sortable[i]["tool"]
        nxt = sortable[i + 1]["tool"]
        if not current.get("name") or not nxt.get("name") or current["name"] == nxt["name"]:
            continue
        edges.append({
            "id": f"deep_edge_{len(edges) + 1}",
            "source": current["name"],
            "target": nxt["name"],
            "type": "control_flow",
            "confidence": 0.35,
            "validation_method": "structural",
            "data_flow": {"from_param": "context", "to_param": "context", "data_type": "object"},
            "semantic_reason": "Deep mode structural sequence edge",
        })
    return edges


# Port of mergeSemanticGateUsage (index.js:960-976)
def merge_semantic_gate_usage(a, b):
    if not a:
        return b or None
    if not b:
        return a
    calls = (a.get("calls") or 0) + (b.get("calls") or 0)
    prompt_tokens = (a.get("prompt_tokens") or 0) + (b.get("prompt_tokens") or 0)
    completion_tokens = (a.get("completion_tokens") or 0) + (b.get("completion_tokens") or 0)
    total_tokens = (a.get("total_tokens") or 0) + (b.get("total_tokens") or 0)
    cached_tokens = (a.get("cached_tokens") or 0) + (b.get("cached_tokens") or 0)
    from ..llm.normalizers import js_round
    ratio = js_round((cached_tokens / prompt_tokens) * 1000) / 1000 if prompt_tokens else 0
    return {
        "calls": calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "prompt_cache_hit_ratio": ratio,
    }


def run_pipeline(skill_root_dir, options=None):
    """Port of SkillFCGAnalyzer.analyze() up to node splitting (rule-only).

    options: mode ('quick'|'full'|'deep'), cycle_expand (bool), plus rule-only
    knobs. disableLlm/semanticLlm are forced to the network-free path.
    """
    options = options or {}
    mode = options.get("mode", "full")
    # rule-only: LLM fully disabled; cycle_expand default ON (matches JS default).
    cycle_expand = options.get("cycle_expand", True)
    max_doc_flow_nodes = options.get("max_doc_flow_nodes", 0)
    max_callsite_mediation_nodes = options.get("max_callsite_mediation_nodes", 0)
    max_dependency_candidates = options.get("max_dependency_candidates", 2000)

    # LLM enablement. DEFAULT is the network-free rule-only path (disableLlm=True):
    # every existing caller (M1 acceptance harness, parity suite) passes only
    # mode/cycle_expand, so they stay bit-for-bit deterministic. The batch CLI
    # opts in by passing disableLlm=False + credentials. Mirrors index.js
    # constructor semantics: semanticLlm defaults ON unless disabled or the
    # caller explicitly sets semanticLlm=False.
    disable_llm = options.get("disableLlm", True)
    if disable_llm:
        semantic_llm = False
        api_key = ""
    else:
        semantic_llm = options.get("semanticLlm", True) is not False
        api_key = str(options.get("llmApiKey") or os.environ.get("LLM_API_KEY") or "").strip()
        if semantic_llm and not api_key:
            raise ValueError("LLM_API_KEY is required for FCG Markdown semantic gate")

    llm_provider = options.get("llmProvider") or os.environ.get("LLM_PROVIDER") or "openai"
    llm_model = options.get("llmModel") or os.environ.get("LLM_MODEL") or "gpt-5.5"
    llm_endpoint = options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT") or ""
    llm_timeout = options.get("llmTimeout") or 180000
    semantic_gate_cache = options.get("semanticGateCache")

    # index.js splits the LLM option contract across two naming conventions:
    # script/doc/constraint extractors read llmModel/llmApiKey/llmEndpoint/
    # llmTimeout/llmProvider; validatePairs/classifyFeedbackEdges read the short
    # model/apiKey/endpoint/timeout/provider. Build both once.
    script_doc_llm = {
        "semanticLlm": semantic_llm,
        "disableLlm": disable_llm,
        "llmProvider": llm_provider,
        "llmModel": llm_model,
        "llmApiKey": api_key,
        "llmEndpoint": llm_endpoint,
        "llmTimeout": llm_timeout,
    }
    validate_feedback_llm = {
        "disableLlm": disable_llm,
        "provider": llm_provider,
        "model": llm_model,
        "apiKey": api_key,
        "endpoint": llm_endpoint,
        "timeout": llm_timeout,
    }

    # Phase 2: Parse skill files
    skill_data = parse_skill(skill_root_dir)
    readme_data = parse_readme(skill_root_dir)
    executable_files = find_executable_files(skill_root_dir)
    documentation_plan = build_documentation_plan(skill_data, readme_data, executable_files)

    # Phase 3: Extract tool calls
    tools = extract_tool_calls(skill_data, readme_data, executable_files, {
        "markdownDocs": documentation_plan["extractionDocs"],
        "rootDir": skill_root_dir,
    })

    script_flow = extract_script_flow(executable_files, {
        "rootDir": skill_root_dir,
        **script_doc_llm,
    })
    if len(script_flow["nodes"]) > 0:
        tools.extend(script_flow["nodes"])

    document_flow_edges = list(script_flow["edges"])
    semantic_gate_usage = None

    document_flow = extract_document_flow(skill_data, readme_data, {
        "extractionDocs": documentation_plan["extractionDocs"],
        "reviewDocs": documentation_plan["reviewDocs"],
        "documentationContext": documentation_plan["documentationContext"],
        "maxDocFlowNodes": max_doc_flow_nodes,
        "semanticGateCache": semantic_gate_cache,
        **script_doc_llm,
    })
    limited_document_flow = limit_document_flow(document_flow, max_doc_flow_nodes)
    if len(limited_document_flow["nodes"]) > 0:
        tools.extend(limited_document_flow["nodes"])
    document_flow_edges.extend(limited_document_flow["edges"])
    semantic_gate_usage = document_flow.get("semantic_gate_usage") or None

    # Add implicit user query source (OpenClaw activation flow) as first node.
    user_query_node = create_user_query_source()
    tools.insert(0, user_query_node)

    mediation = build_call_site_mediation(tools)
    limited_mediation = limit_mediation(mediation, tools, max_callsite_mediation_nodes)
    if len(limited_mediation["nodes"]) > 0:
        tools.extend(limited_mediation["nodes"])
        document_flow_edges.extend(limited_mediation["edges"])

    # Global two-phase constraint resolution (rule-only).
    constraint_gate_usage = new_semantic_gate_usage()
    resolved = resolve_pending_constraints(tools, {
        "semanticGateUsage": constraint_gate_usage,
        # constraint resolution uses the script/doc LLM naming convention
        # (llmModel/llmApiKey/...); it does not read semanticLlm.
        "disableLlm": disable_llm,
        "llmProvider": llm_provider,
        "llmModel": llm_model,
        "llmApiKey": api_key,
        "llmEndpoint": llm_endpoint,
        "llmTimeout": llm_timeout,
    })
    constraint_usage_summary = summarize_semantic_gate_usage(constraint_gate_usage)
    if constraint_usage_summary:
        semantic_gate_usage = merge_semantic_gate_usage(semantic_gate_usage, constraint_usage_summary)
    if len(resolved["addedNodes"]) > 0:
        tools.extend(resolved["addedNodes"])
    if len(resolved["edges"]) > 0:
        document_flow_edges.extend(resolved["edges"])

    # Phase 4: Sparse dependency candidate analysis
    dependency_candidates = analyze_type_compatibility(tools, {
        "maxCandidates": max_dependency_candidates,
    })

    # Add edges from user query to LLM inference (implicit data flow).
    structural_dependency_edges = []
    llm_node_index = next((i for i, t in enumerate(tools) if t.get("name") == "llm.inference"), -1)
    if llm_node_index != -1:
        structural_dependency_edges.append({
            "source": user_query_node["name"],
            "target": tools[llm_node_index]["name"],
            "type": "data_dependency",
            "confidence": 1.0,
            "validation_method": "dependency_structural",
            "data_flow": {"from_param": "query_text", "to_param": "user_query", "data_type": "string"},
            "semantic_reason": "Implicit OpenClaw activation query flows to LLM inference",
        })

    # Add edges from non-callsite nodes to global LLM inference.
    if llm_node_index != -1:
        llm_node = tools[llm_node_index]
        for i in range(1, len(tools)):  # Skip user query (index 0)
            if i == llm_node_index:
                continue
            tool = tools[i]
            if tool.get("name") == "llm.inference":
                continue
            if not should_add_implicit_tool_to_llm_edge(tool):
                continue
            exists = any(
                e["source"] == tool["name"] and e["target"] == llm_node["name"]
                for e in structural_dependency_edges
            )
            if not exists:
                structural_dependency_edges.append({
                    "source": tool["name"],
                    "target": llm_node["name"],
                    "type": "data_dependency",
                    "confidence": 0.9,
                    "validation_method": "dependency_structural",
                    "data_flow": {"from_param": "skill_content", "to_param": "skill_content", "data_type": "string"},
                    "semantic_reason": "Skill content is available to the global LLM context",
                })

    # Phase 5: dependency validation. mode!='quick' -> validatePairs (rule-only);
    # mode=='quick' -> direct candidate mapping.
    if mode != "quick":
        validated_edges = validate_pairs(dependency_candidates, dict(validate_feedback_llm))
    else:
        validated_edges = []
        for index, pair in enumerate(dependency_candidates):
            cp = pair.get("compatibleParams") or []
            first = cp[0] if cp else {}
            validated_edges.append({
                "id": f"edge_{str(index + 1).rjust(3, '0')}",
                "source": pair["source"]["name"],
                "target": pair["target"]["name"],
                "type": "data_dependency",
                "confidence": pair["confidence"],
                "validation_method": "dependency_rule",
                "data_flow": {
                    "from_param": first.get("fromParam") or "unknown",
                    "to_param": first.get("toParam") or "unknown",
                    "data_type": first.get("fromType") or "string",
                },
                "semantic_reason": pair.get("candidate_reason") or "Sparse dependency rule",
            })
    validated_edges = list(validated_edges) + structural_dependency_edges

    # Deep mode: additional structural control-flow edges.
    deep_mode_edges = []
    if mode == "deep":
        deep_mode_edges = build_deep_mode_edges(tools)

    # Map edge source/target from names/canonical to node IDs.
    endpoint_maps = build_endpoint_maps(tools)
    validated_edges = expand_and_map_edges(validated_edges, endpoint_maps)
    deep_mode_edges = expand_and_map_edges(deep_mode_edges, endpoint_maps)
    document_flow_edges = expand_and_map_edges(document_flow_edges, endpoint_maps)

    # Phase 6: Build FCG
    graph = build_fcg(tools, [*validated_edges, *deep_mode_edges, *document_flow_edges])
    graph = remove_duplicate_edges(graph)
    if cycle_expand:
        graph = detect_and_tag_cycles(graph)
    else:
        graph = remove_cycles(graph)

    # Match analyze(): resolveFeedbackLlmReview(undefined) defaults ON, but the
    # disableLlm guard inside reviewImplausibleWithLLM makes it a no-op (empty
    # verdicts -> llm_fallback source). Rule verdicts (plausible/implausible) are
    # unchanged, so the M1 snapshot is deterministic either way.
    classify_feedback_edges(graph, {
        **validate_feedback_llm,
        "feedbackLlmReview": resolve_feedback_llm_review(options.get("feedbackLlmReview")),
    })

    if cycle_expand:
        graph = break_only_fake(graph)

    # Enforce single-crossing invariant (the M1 acceptance oracle target).
    graph = split_graph_nodes(graph)

    return {
        "graph": graph,
        "tools": tools,
        "semantic_gate_usage": semantic_gate_usage,
        "mode": mode,
        "cycle_expand": bool(cycle_expand),
        # Envelope inputs (meta/skill/documentation_context). The M1 acceptance
        # harness ignores these; the v6 output builder (build_fcg_json) reads them.
        "skill_data": skill_data,
        "readme_data": readme_data,
        "documentation_context": documentation_plan["documentationContext"],
    }


def _num(value, fallback):
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _locale_compare(a, b):
    from ..util.locale import locale_compare
    return locale_compare(a, b)
