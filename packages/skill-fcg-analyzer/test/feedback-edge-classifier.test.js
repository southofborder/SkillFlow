const test = require('node:test');
const assert = require('node:assert/strict');

const { FunctionCallGraph } = require('../src/analyzer/fcg-builder');
const { removeCycles, isFeedbackEdge } = require('../src/analyzer/cycle-remover');
const {
  classifyFeedbackEdges,
  classifyFeedbackEdgeByRule,
  nodeIsSinkLike,
  resolveFeedbackLlmReview,
  DEFAULT_PLAUSIBLE_MIN_CONF
} = require('../src/analyzer/feedback-edge-classifier');

// The classifier judges whether a cycle-broken back-edge is PLAUSIBLE as a real
// feedback edge (wide-net rules, then optional LLM rescue). It never touches the
// real vs fake cycle question and never changes the graph's traversal structure.

function nodesMap(entries) {
  const m = new Map();
  for (const [id, node] of entries) m.set(id, { id, ...node });
  return m;
}

// --- Rule pass (wide net) ------------------------------------------------------

test('rule marks a doc/semantic/constraint back-edge as plausible', () => {
  const nodes = nodesMap([['a', { name: 'a' }], ['b', { name: 'b' }]]);
  const edge = { source: 'b', target: 'a', type: 'control_flow', confidence: 0.1, validation_method: 'doc_flow' };
  const v = classifyFeedbackEdgeByRule(edge, nodes, DEFAULT_PLAUSIBLE_MIN_CONF);
  assert.equal(v.plausible, true);
});

test('rule does NOT treat a bare structural data_flow as plausible (not discriminative)', () => {
  // Nearly every FCG edge carries a default data_flow (e.g. response->content),
  // so its presence must not by itself mark a low-confidence non-sink back-edge
  // plausible — otherwise the implausible/LLM-review bucket never populates.
  const nodes = nodesMap([['a', { name: 'a' }], ['b', { name: 'b' }]]);
  const edge = {
    source: 'b', target: 'a', type: 'data_dependency', confidence: 0.1,
    validation_method: 'dependency_rule',
    data_flow: { from_param: 'response', to_param: 'content' }
  };
  assert.equal(classifyFeedbackEdgeByRule(edge, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, false);
});

test('rule marks a back-edge touching a Sink node as plausible', () => {
  const nodes = nodesMap([
    ['a', { name: 'doc.write', category: 'Sink' }],
    ['b', { name: 'b' }]
  ]);
  const edge = { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.1, validation_method: 'dependency_rule' };
  assert.equal(classifyFeedbackEdgeByRule(edge, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, true);
});

test('rule marks a confident bare dependency back-edge as plausible', () => {
  const nodes = nodesMap([['a', { name: 'a' }], ['b', { name: 'b' }]]);
  const edge = { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.8, validation_method: 'dependency_rule' };
  assert.equal(classifyFeedbackEdgeByRule(edge, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, true);
});

test('rule marks a low-confidence bare dependency back-edge as implausible', () => {
  const nodes = nodesMap([['a', { name: 'a' }], ['b', { name: 'b' }]]);
  const edge = { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.2, validation_method: 'dependency_rule' };
  assert.equal(classifyFeedbackEdgeByRule(edge, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, false);
});

test('confidence threshold is inclusive at the wide-net default (0.3)', () => {
  const nodes = nodesMap([['a', { name: 'a' }], ['b', { name: 'b' }]]);
  assert.equal(DEFAULT_PLAUSIBLE_MIN_CONF, 0.3);
  const atThreshold = { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.3, validation_method: 'dependency_rule' };
  const belowThreshold = { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.29, validation_method: 'dependency_rule' };
  assert.equal(classifyFeedbackEdgeByRule(atThreshold, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, true);
  assert.equal(classifyFeedbackEdgeByRule(belowThreshold, nodes, DEFAULT_PLAUSIBLE_MIN_CONF).plausible, false);
});

// --- classifyFeedbackEdges over a real broken cycle ---------------------------

// Minimal loop whose broken back-edge is a low-confidence bare dependency (falls
// to implausible under the rule): lets us exercise the LLM-review path.
function bareDependencyLoop() {
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'node_w', name: 'compute.a' });
  graph.addNode({ id: 'node_r', name: 'compute.b' });
  // forward control edge (protected doc_flow) stays in adjacency
  graph.addEdge({ source: 'node_w', target: 'node_r', type: 'control_flow', confidence: 0.7, validation_method: 'doc_flow' });
  // back-edge: low-confidence bare dependency -> chosen as the feedback edge and
  // rule-implausible
  graph.addEdge({ source: 'node_r', target: 'node_w', type: 'data_dependency', confidence: 0.2, validation_method: 'dependency_rule' });
  return graph;
}

test('classifyFeedbackEdges tags plausibility on the broken back-edge (rule, review off)', async () => {
  const graph = removeCycles(bareDependencyLoop());
  const stats = await classifyFeedbackEdges(graph, { feedbackLlmReview: false });

  const fb = graph.edges.filter(isFeedbackEdge);
  assert.equal(fb.length, 1);
  assert.equal(fb[0].feedback_plausibility, 'implausible');
  assert.equal(fb[0].feedback_plausibility_source, 'rule');
  assert.equal(stats.feedback_edge_count, 1);
  assert.equal(stats.rule_implausible_count, 1);
  assert.equal(stats.llm_reviewed_count, 0);
});

test('LLM review rescues an implausible back-edge to plausible', async () => {
  const graph = removeCycles(bareDependencyLoop());
  // Injected reviewer: agree that the (only) implausible edge is real feedback.
  const stats = await classifyFeedbackEdges(graph, {
    apiKey: 'x',
    feedbackLlmReview: true,
    feedbackReviewer: (items) => items.map(it => ({ id: it.id, is_plausible: true, reason: 'genuine loop' }))
  });

  const fb = graph.edges.filter(isFeedbackEdge)[0];
  assert.equal(fb.feedback_plausibility, 'plausible');
  assert.equal(fb.feedback_plausibility_source, 'llm');
  assert.equal(fb.feedback_plausibility_reason, 'genuine loop');
  assert.equal(stats.llm_rescued_count, 1);
  assert.equal(stats.rule_plausible_count, 1);
  assert.equal(stats.rule_implausible_count, 0);
});

test('LLM review can confirm an edge stays implausible', async () => {
  const graph = removeCycles(bareDependencyLoop());
  const stats = await classifyFeedbackEdges(graph, {
    apiKey: 'x',
    feedbackLlmReview: true,
    feedbackReviewer: (items) => items.map(it => ({ id: it.id, is_plausible: false, reason: 'dedup artifact' }))
  });

  const fb = graph.edges.filter(isFeedbackEdge)[0];
  assert.equal(fb.feedback_plausibility, 'implausible');
  assert.equal(fb.feedback_plausibility_source, 'llm');
  assert.equal(stats.llm_reviewed_count, 1);
  assert.equal(stats.llm_rescued_count, 0);
});

test('review falls back to rule verdict when reviewer throws (no rescue, no crash)', async () => {
  const graph = removeCycles(bareDependencyLoop());
  const stats = await classifyFeedbackEdges(graph, {
    apiKey: 'x',
    feedbackLlmReview: true,
    feedbackReviewer: () => { throw new Error('boom'); }
  });

  const fb = graph.edges.filter(isFeedbackEdge)[0];
  assert.equal(fb.feedback_plausibility, 'implausible');
  assert.equal(fb.feedback_plausibility_source, 'llm_fallback');
  assert.equal(stats.llm_fallback_count, 1);
});

test('review is skipped and marked fallback-free when disabled by disableLlm', async () => {
  const graph = removeCycles(bareDependencyLoop());
  // disableLlm short-circuits the network reviewer to an empty verdict map, so
  // implausible edges keep the rule verdict and are marked as a fallback.
  const stats = await classifyFeedbackEdges(graph, { disableLlm: true, feedbackLlmReview: true });
  const fb = graph.edges.filter(isFeedbackEdge)[0];
  assert.equal(fb.feedback_plausibility, 'implausible');
  assert.equal(fb.feedback_plausibility_source, 'llm_fallback');
  assert.equal(stats.llm_fallback_count, 1);
});

// --- Zero regression -----------------------------------------------------------

test('classification does not change edges, adjacency, or feedback tagging', async () => {
  const graph = removeCycles(bareDependencyLoop());
  const edgesBefore = graph.edges.length;
  const adjBefore = JSON.stringify([...graph.adjacencyList.entries()]);
  const feedbackBefore = graph.edges.filter(isFeedbackEdge).length;

  await classifyFeedbackEdges(graph, { feedbackLlmReview: false });

  assert.equal(graph.edges.length, edgesBefore);
  assert.equal(JSON.stringify([...graph.adjacencyList.entries()]), adjBefore);
  assert.equal(graph.edges.filter(isFeedbackEdge).length, feedbackBefore);
});

test('classifyFeedbackEdges on a graph with no feedback edges is a no-op', async () => {
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'a', name: 'a' });
  graph.addNode({ id: 'b', name: 'b' });
  graph.addEdge({ source: 'a', target: 'b', type: 'control_flow', confidence: 0.7 });
  const stats = await classifyFeedbackEdges(graph, { feedbackLlmReview: false });
  assert.equal(stats.feedback_edge_count, 0);
  assert.equal(stats.rule_plausible_count, 0);
});

// --- Helpers -------------------------------------------------------------------

test('nodeIsSinkLike detects Sink category', () => {
  assert.equal(nodeIsSinkLike({ name: 'x', category: 'Sink' }), true);
  assert.equal(nodeIsSinkLike({ name: 'x', category: 'Intermediate' }), false);
  assert.equal(nodeIsSinkLike(undefined), false);
});

test('resolveFeedbackLlmReview: explicit option wins, env parsed, default on', () => {
  assert.equal(resolveFeedbackLlmReview(true), true);
  assert.equal(resolveFeedbackLlmReview(false), false);

  const prev = process.env.FCG_FEEDBACK_LLM_REVIEW;
  try {
    process.env.FCG_FEEDBACK_LLM_REVIEW = '0';
    assert.equal(resolveFeedbackLlmReview(undefined), false);
    process.env.FCG_FEEDBACK_LLM_REVIEW = 'on';
    assert.equal(resolveFeedbackLlmReview(undefined), true);
    delete process.env.FCG_FEEDBACK_LLM_REVIEW;
    assert.equal(resolveFeedbackLlmReview(undefined), true);
  } finally {
    if (prev === undefined) delete process.env.FCG_FEEDBACK_LLM_REVIEW;
    else process.env.FCG_FEEDBACK_LLM_REVIEW = prev;
  }
});
