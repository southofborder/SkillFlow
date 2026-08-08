// Full-chain parity driver (M1e-3). Runs the REAL JS pipeline through node
// splitting + feedback classification + findCrossingViolations, then prints a
// normalized snapshot. Feedback LLM review is disabled (rule-only) for
// determinism. Paired with test_parity_split_and_feedback.py.
const path = require('path');
const ANALYZER = path.resolve(__dirname, '../../../skill-fcg-analyzer/src');
const { analyzeTypeCompatibility } = require(path.join(ANALYZER, 'parser/type-analyzer'));
const { buildFCG, removeDuplicateEdges } = require(path.join(ANALYZER, 'analyzer/fcg-builder'));
const { removeCycles } = require(path.join(ANALYZER, 'analyzer/cycle-remover'));
const { buildCallSiteMediation, buildEndpointMaps, expandAndMapEdges } = require(path.join(ANALYZER, 'analyzer/callsite-expander'));
const { classifyFeedbackEdges } = require(path.join(ANALYZER, 'analyzer/feedback-edge-classifier'));
const { splitGraphNodes, findCrossingViolations } = require(path.join(ANALYZER, 'analyzer/node-splitter'));
const { buildNodeProfiles } = require(path.join(ANALYZER, 'security/node-profiler'));

function adjacencySnapshot(graph) {
  const out = {};
  for (const [k, v] of graph.adjacencyList.entries()) out[k] = v.slice();
  return out;
}

(async () => {
  const spec = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf-8'));
  const tools = spec.tools || [];
  const suppliedEdges = spec.edges || [];

  const mediation = buildCallSiteMediation(tools);
  const allTools = tools.concat(mediation.nodes);
  const candidates = analyzeTypeCompatibility(allTools, {});
  const maps = buildEndpointMaps(allTools);
  const candidateEdges = candidates.map((pair, index) => ({
    id: `edge_${String(index + 1).padStart(3, '0')}`,
    source: pair.source.name, target: pair.target.name, type: 'data_dependency',
    confidence: pair.confidence, validation_method: 'dependency_rule',
    data_flow: {
      from_param: (pair.compatibleParams[0] || {}).fromParam || 'unknown',
      to_param: (pair.compatibleParams[0] || {}).toParam || 'unknown',
      data_type: (pair.compatibleParams[0] || {}).fromType || 'string'
    },
    semantic_reason: pair.candidate_reason || 'Sparse dependency rule'
  }));
  const mapped = [
    ...expandAndMapEdges(candidateEdges, maps),
    ...expandAndMapEdges(mediation.edges, maps),
    ...expandAndMapEdges(suppliedEdges, maps)
  ];

  let graph = buildFCG(allTools, mapped);
  graph = removeDuplicateEdges(graph);
  graph = removeCycles(graph);
  await classifyFeedbackEdges(graph, { feedbackLlmReview: false, disableLlm: true });

  const preSplitCount = graph.nodes.size;
  graph = splitGraphNodes(graph);

  const nodesById = graph.nodes;
  const profiles = buildNodeProfiles(Array.from(graph.nodes.values()), graph.edges);
  const violations = findCrossingViolations(profiles, nodesById);

  process.stdout.write(JSON.stringify({
    pre_split_count: preSplitCount,
    post_split_count: graph.nodes.size,
    node_ids: Array.from(graph.nodes.keys()),
    split_children: Array.from(graph.nodes.values())
      .filter(n => n.split_from)
      .map(n => ({ id: n.id, name: n.name, op: n.operationType, split_from: n.split_from })),
    edges: graph.edges.map(e => ({
      source: e.source, target: e.target, type: e.type,
      validation_method: e.validation_method,
      is_feedback_edge: Boolean(e.is_feedback_edge),
      feedback_plausibility: e.feedback_plausibility || null
    })),
    adjacency: adjacencySnapshot(graph),
    crossing_violations: violations
  }));
})();
