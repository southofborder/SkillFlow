"""Port of src/analyzer/callsite-expander.js.

Builds per-call-site LLM mediation nodes (llm.inference#before/after_<id>),
the name->id / canonical->ids endpoint maps used to resolve edges to node ids,
and expand_and_map_edges which fans an edge over all canonical matches. Node/edge
shapes mirror the JS objects verbatim.
"""

import functools


# Port of buildCallSiteMediation (callsite-expander.js:1-45)
def build_call_site_mediation(tools):
    call_sites = sorted(
        [t for t in (tools or []) if is_runtime_tool_call_site(t)],
        key=functools.cmp_to_key(compare_call_site_order),
    )
    nodes = []
    edges = []

    for i, callsite in enumerate(call_sites):
        before = create_mediation_node(callsite, "before")
        after = create_mediation_node(callsite, "after")
        nodes.append(before)
        nodes.append(after)

        edges.append(create_mediation_edge(
            source=before["name"], target=callsite["name"], index=len(edges),
            from_param="response", to_param="context",
            reason=f"LLM prepares tool call {callsite.get('canonical_name') or callsite['name']}",
        ))
        edges.append(create_mediation_edge(
            source=callsite["name"], target=after["name"], index=len(edges),
            from_param="result", to_param="context",
            reason=f"Tool result returns to LLM after {callsite.get('canonical_name') or callsite['name']}",
        ))

        nxt = call_sites[i + 1] if i + 1 < len(call_sites) else None
        if nxt:
            edges.append(create_mediation_edge(
                source=after["name"],
                target=f"llm.inference#before_{nxt['callsite_id']}",
                index=len(edges), from_param="context", to_param="context",
                reason="LLM carries context between ordered tool call-sites",
            ))

    return {"nodes": nodes, "edges": edges}


# Port of createMediationNode (callsite-expander.js:47-72)
def create_mediation_node(callsite, phase):
    callsite_id = callsite.get("callsite_id") or "call_unknown"
    return {
        "name": f"llm.inference#{phase}_{callsite_id}",
        "canonical_name": "llm.inference",
        "callsite_id": callsite_id,
        "callsite_order": callsite.get("callsite_order"),
        "callsite_role": f"llm_{phase}",
        "action": "inference",
        "type": "builtin_call",
        "category": "Sink",
        "isCritical": True,
        "description": f"{'Pre' if phase == 'before' else 'Post'}-tool LLM mediation for {callsite.get('canonical_name') or callsite['name']}",
        "input": {
            "context": {"type": "object", "required": False},
            "user_query": {"type": "string", "required": False},
        },
        "output": {
            "context": {"type": "object"},
            "response": {"type": "string"},
        },
        "location": callsite.get("location") or {},
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
    }


# Port of createMediationEdge (callsite-expander.js:74-89)
def create_mediation_edge(source, target, index, from_param, to_param, reason):
    return {
        "id": f"callsite_mediation_{index + 1}",
        "source": source,
        "target": target,
        "type": "control_flow",
        "confidence": 0.92,
        "validation_method": "callsite_mediation",
        "data_flow": {"from_param": from_param, "to_param": to_param, "data_type": "object"},
        "semantic_reason": reason,
    }


# Port of isRuntimeToolCallSite (callsite-expander.js:91-99)
def is_runtime_tool_call_site(tool):
    return bool(
        tool
        and tool.get("type") == "tool_call"
        and tool.get("callsite_id")
        and tool.get("canonical_name")
        and not tool.get("excludeFromTypeAnalysis")
    )


# Port of compareCallSiteOrder (callsite-expander.js:101-105)
def compare_call_site_order(a, b):
    order_delta = _num(a.get("callsite_order")) - _num(b.get("callsite_order"))
    if order_delta != 0:
        return -1 if order_delta < 0 else 1
    return _locale_compare(str(a.get("name") or ""), str(b.get("name") or ""))


# Port of buildEndpointMaps (callsite-expander.js:107-123)
def build_endpoint_maps(tools=None):
    tools = tools or []
    name_to_id = {}
    canonical_name_to_ids = {}
    for i, tool in enumerate(tools):
        node_id = f"node_{str(i + 1).rjust(3, '0')}"
        name_to_id[tool["name"]] = node_id
        cn = tool.get("canonical_name")
        if cn and cn != tool["name"]:
            canonical_name_to_ids.setdefault(cn, []).append({"id": node_id, "tool": tool})
    return {"nameToId": name_to_id, "canonicalNameToIds": canonical_name_to_ids}


# Port of expandAndMapEdges (callsite-expander.js:125-138)
def expand_and_map_edges(edges, maps):
    mapped = []
    for edge in edges or []:
        sources = resolve_endpoint_ids(edge["source"], maps)
        targets = resolve_endpoint_ids(edge["target"], maps)
        for source in sources:
            for target in targets:
                if not source or not target:
                    continue
                mapped.append({**edge, "source": source, "target": target})
    return mapped


# Port of resolveEndpointIds (callsite-expander.js:140-147)
def resolve_endpoint_ids(endpoint, maps):
    if endpoint in maps["nameToId"]:
        return [maps["nameToId"][endpoint]]
    canonical_matches = maps["canonicalNameToIds"].get(endpoint)
    if canonical_matches and len(canonical_matches) > 0:
        return [item["id"] for item in canonical_matches]
    return [endpoint]


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _locale_compare(a, b):
    """Faithful JS String.localeCompare (ICU-root ASCII). See util/locale.py."""
    from ..util.locale import locale_compare
    return locale_compare(a, b)
