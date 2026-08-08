// Parity driver for the 4 clean analyzer modules (M1e-1). Reads
// {tools, edges} JSON from argv[2], runs the REAL JS modules in the index.js
// order (type candidates -> endpoint maps -> expand -> buildFCG ->
// removeDuplicateEdges -> removeCycles), and prints a normalized snapshot to
// stdout. Paired with test_parity_analyzer_core.py. No LLM, no profiler.
const fs = require('fs');
const { analyzeTypeCompatibility } = require('../../../skill-fcg-analyzer/src/parser/type-analyzer');
const { buildFCG, removeDuplicateEdges } = require('../../../skill-fcg-analyzer/src/analyzer/fcg-builder');
const { removeCycles } = require('../../../skill-fcg-analyzer/src/analyzer/cycle-remover');
const { buildCallSiteMediation, buildEndpointMaps, expandAndMapEdges } = require('../../../skill-fcg-analyzer/src/analyzer/callsite-expander');

function adjacencySnapshot(graph) {
  const out = {};
  for (const [k, v] of graph.adjacencyList.entries()) out[k] = v.slice();
  return out;
}

(() => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
  const tools = spec.tools || [];
  const suppliedEdges = spec.edges || [];

  // 1. mediation nodes (appended to tools, as index.js does before buildFCG)
  const mediation = buildCallSiteMediation(tools);
  const allTools = tools.concat(mediation.nodes);

  // 2. dependency candidates over the FULL node set
  const candidates = analyzeTypeCompatibility(allTools, {});

  // 3. endpoint maps + edge expansion/mapping to node ids
  const maps = buildEndpointMaps(allTools);
  const candidateEdges = candidates.map((pair, index) => ({
    id: `edge_${String(index + 1).padStart(3, '0')}`,
    source: pair.source.name,
    target: pair.target.name,
    type: 'data_dependency',
    confidence: pair.confidence,
    validation_method: 'dependency_rule',
    data_flow: {
      from_param: (pair.compatibleParams[0] || {}).fromParam || 'unknown',
      to_param: (pair.compatibleParams[0] || {}).toParam || 'unknown',
      data_type: (pair.compatibleParams[0] || {}).fromType || 'string'
    },
    semantic_reason: pair.candidate_reason || 'Sparse dependency rule'
  }));
  const mappedCandidateEdges = expandAndMapEdges(candidateEdges, maps);
  const mappedMediationEdges = expandAndMapEdges(mediation.edges, maps);
  const mappedSuppliedEdges = expandAndMapEdges(suppliedEdges, maps);

  // 4. build FCG (assigns node_NNN ids) + dedup + cycle removal
  let graph = buildFCG(allTools, [...mappedCandidateEdges, ...mappedMediationEdges, ...mappedSuppliedEdges]);
  graph = removeDuplicateEdges(graph);
  graph = removeCycles(graph);

  const nodeIds = Array.from(graph.nodes.keys());
  const nodeNamesById = {};
  for (const [id, node] of graph.nodes.entries()) nodeNamesById[id] = node.name;
  const edges = graph.edges.map(e => ({
    id: e.id, source: e.source, target: e.target, type: e.type,
    confidence: e.confidence, validation_method: e.validation_method,
    is_feedback_edge: Boolean(e.is_feedback_edge)
  }));

  process.stdout.write(JSON.stringify({
    node_ids: nodeIds,
    node_names_by_id: nodeNamesById,
    mediation_node_names: mediation.nodes.map(n => n.name),
    candidate_count: candidates.length,
    candidate_pairs: candidates.map(c => `${c.source.name}->${c.target.name}:${c.candidate_kind}`),
    edges,
    adjacency: adjacencySnapshot(graph)
  }));
})();
