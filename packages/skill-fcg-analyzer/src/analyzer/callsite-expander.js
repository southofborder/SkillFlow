function buildCallSiteMediation(tools) {
  const callSites = (tools || [])
    .filter(isRuntimeToolCallSite)
    .sort(compareCallSiteOrder);
  const nodes = [];
  const edges = [];

  for (let i = 0; i < callSites.length; i++) {
    const callsite = callSites[i];
    const before = createMediationNode(callsite, 'before');
    const after = createMediationNode(callsite, 'after');
    nodes.push(before, after);

    edges.push(createMediationEdge({
      source: before.name,
      target: callsite.name,
      index: edges.length,
      fromParam: 'response',
      toParam: 'context',
      reason: `LLM prepares tool call ${callsite.canonical_name || callsite.name}`
    }));
    edges.push(createMediationEdge({
      source: callsite.name,
      target: after.name,
      index: edges.length,
      fromParam: 'result',
      toParam: 'context',
      reason: `Tool result returns to LLM after ${callsite.canonical_name || callsite.name}`
    }));

    const next = callSites[i + 1];
    if (next) {
      edges.push(createMediationEdge({
        source: after.name,
        target: `llm.inference#before_${next.callsite_id}`,
        index: edges.length,
        fromParam: 'context',
        toParam: 'context',
        reason: 'LLM carries context between ordered tool call-sites'
      }));
    }
  }

  return { nodes, edges };
}

function createMediationNode(callsite, phase) {
  const callsiteId = callsite.callsite_id || 'call_unknown';
  return {
    name: `llm.inference#${phase}_${callsiteId}`,
    canonical_name: 'llm.inference',
    callsite_id: callsiteId,
    callsite_order: callsite.callsite_order,
    callsite_role: `llm_${phase}`,
    action: 'inference',
    type: 'builtin_call',
    category: 'Sink',
    isCritical: true,
    description: `${phase === 'before' ? 'Pre' : 'Post'}-tool LLM mediation for ${callsite.canonical_name || callsite.name}`,
    input: {
      context: { type: 'object', required: false },
      user_query: { type: 'string', required: false }
    },
    output: {
      context: { type: 'object' },
      response: { type: 'string' }
    },
    location: callsite.location || {},
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true
  };
}

function createMediationEdge({ source, target, index, fromParam, toParam, reason }) {
  return {
    id: `callsite_mediation_${index + 1}`,
    source,
    target,
    type: 'control_flow',
    confidence: 0.92,
    validation_method: 'callsite_mediation',
    data_flow: {
      from_param: fromParam,
      to_param: toParam,
      data_type: 'object'
    },
    semantic_reason: reason
  };
}

function isRuntimeToolCallSite(tool) {
  return Boolean(
    tool &&
    tool.type === 'tool_call' &&
    tool.callsite_id &&
    tool.canonical_name &&
    !tool.excludeFromTypeAnalysis
  );
}

function compareCallSiteOrder(a, b) {
  const orderDelta = Number(a.callsite_order || 0) - Number(b.callsite_order || 0);
  if (orderDelta !== 0) return orderDelta;
  return String(a.name || '').localeCompare(String(b.name || ''));
}

function buildEndpointMaps(tools = []) {
  const nameToId = new Map();
  const canonicalNameToIds = new Map();

  for (let i = 0; i < tools.length; i++) {
    const nodeId = `node_${String(i + 1).padStart(3, '0')}`;
    nameToId.set(tools[i].name, nodeId);
    if (tools[i].canonical_name && tools[i].canonical_name !== tools[i].name) {
      if (!canonicalNameToIds.has(tools[i].canonical_name)) {
        canonicalNameToIds.set(tools[i].canonical_name, []);
      }
      canonicalNameToIds.get(tools[i].canonical_name).push({ id: nodeId, tool: tools[i] });
    }
  }

  return { nameToId, canonicalNameToIds };
}

function expandAndMapEdges(edges, maps) {
  const mapped = [];
  for (const edge of edges || []) {
    const sources = resolveEndpointIds(edge.source, maps);
    const targets = resolveEndpointIds(edge.target, maps);
    for (const source of sources) {
      for (const target of targets) {
        if (!source || !target) continue;
        mapped.push({ ...edge, source, target });
      }
    }
  }
  return mapped;
}

function resolveEndpointIds(endpoint, maps) {
  if (maps.nameToId.has(endpoint)) return [maps.nameToId.get(endpoint)];
  const canonicalMatches = maps.canonicalNameToIds.get(endpoint);
  if (canonicalMatches && canonicalMatches.length > 0) {
    return canonicalMatches.map(item => item.id);
  }
  return [endpoint];
}

module.exports = {
  buildCallSiteMediation,
  buildEndpointMaps,
  expandAndMapEdges
};
