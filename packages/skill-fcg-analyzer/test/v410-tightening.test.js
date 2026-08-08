const test = require('node:test');
const assert = require('node:assert/strict');

const { buildCallSiteMediation, buildEndpointMaps, expandAndMapEdges } = require('../src/analyzer/callsite-expander');
const { removeCycles } = require('../src/analyzer/cycle-remover');
const { FunctionCallGraph } = require('../src/analyzer/fcg-builder');
const { deduplicateCallSites, deduplicateTools } = require('../src/parser/tool-extractor');
const { buildObservations } = require('../src/security/observation-analyzer');
const { buildProvenanceGraph } = require('../src/security/provenance-extractor');

test('deduplicateTools remains a compatibility alias for exact call-site dedupe', () => {
  const tools = [
    toolAt('gmail.message.get', 'SKILL.md', 10, 3, 'markdown'),
    toolAt('gmail.message.get', 'SKILL.md', 10, 3, 'markdown'),
    toolAt('gmail.message.get', 'SKILL.md', 11, 3, 'markdown')
  ];

  const direct = deduplicateCallSites(tools);
  const alias = deduplicateTools(tools);

  assert.equal(direct.length, 2);
  assert.deepEqual(alias, direct);
});

test('callsite expander creates ordered before/after LLM mediation nodes and edges', () => {
  const tools = [
    callSite('gmail.message.get#call_001', 'gmail.message.get', 'call_001', 1),
    callSite('webhook.post#call_002', 'webhook.post', 'call_002', 2)
  ];

  const mediation = buildCallSiteMediation(tools);
  const nodeNames = mediation.nodes.map(node => node.name);
  const edgeNames = mediation.edges.map(edge => `${edge.source}->${edge.target}`);

  assert.deepEqual(nodeNames, [
    'llm.inference#before_call_001',
    'llm.inference#after_call_001',
    'llm.inference#before_call_002',
    'llm.inference#after_call_002'
  ]);
  assert.ok(edgeNames.includes('llm.inference#before_call_001->gmail.message.get#call_001'));
  assert.ok(edgeNames.includes('gmail.message.get#call_001->llm.inference#after_call_001'));
  assert.ok(edgeNames.includes('llm.inference#after_call_001->llm.inference#before_call_002'));
  assert.ok(mediation.edges.every(edge => edge.validation_method === 'callsite_mediation'));
});

test('callsite endpoint mapping prefers unique names and fans out canonical fallback', () => {
  const tools = [
    { name: 'gmail.message.get#call_001', canonical_name: 'gmail.message.get' },
    { name: 'gmail.message.get#call_002', canonical_name: 'gmail.message.get' },
    { name: 'webhook.post#call_003', canonical_name: 'webhook.post' }
  ];
  const maps = buildEndpointMaps(tools);

  const uniqueMapped = expandAndMapEdges([
    edge('gmail.message.get#call_001', 'webhook.post#call_003')
  ], maps);
  const fallbackMapped = expandAndMapEdges([
    edge('gmail.message.get', 'webhook.post#call_003')
  ], maps);

  assert.deepEqual(uniqueMapped.map(item => item.source), ['node_001']);
  assert.deepEqual(uniqueMapped.map(item => item.target), ['node_003']);
  assert.deepEqual(fallbackMapped.map(item => item.source).sort(), ['node_001', 'node_002']);
  assert.ok(fallbackMapped.every(item => item.target === 'node_003'));
});

test('cycle remover protects call-site mediation edges and removes weaker data edge', () => {
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'node_a', name: 'llm.inference#before_call_001' });
  graph.addNode({ id: 'node_b', name: 'tool.read#call_001' });
  graph.addNode({ id: 'node_c', name: 'llm.inference#after_call_001' });

  graph.addEdge({
    source: 'node_a',
    target: 'node_b',
    type: 'control_flow',
    confidence: 0.92,
    validation_method: 'callsite_mediation'
  });
  graph.addEdge({
    source: 'node_b',
    target: 'node_c',
    type: 'control_flow',
    confidence: 0.92,
    validation_method: 'callsite_mediation'
  });
  graph.addEdge({
    source: 'node_c',
    target: 'node_a',
    type: 'data_dependency',
    confidence: 0.99,
    validation_method: 'type_check'
  });

  const result = removeCycles(graph);

  // The weaker data edge is no longer deleted; it is retained as a feedback edge
  // (method A) but dropped from the adjacencyList so the traversal view is a DAG.
  assert.equal(result.edges.length, 3);
  const feedback = result.edges.filter(edge => edge.is_feedback_edge);
  assert.equal(feedback.length, 1);
  assert.equal(feedback[0].validation_method, 'type_check');
  assert.equal(feedback[0].source, 'node_c');
  assert.equal(feedback[0].target, 'node_a');
  assert.equal(feedback[0].feedback_removed_reason, 'cycle_break');
  assert.ok(Array.isArray(feedback[0].feedback_cycle_path) && feedback[0].feedback_cycle_path.length > 0);
  // Protected callsite_mediation edges keep their adjacency; the data edge does not.
  assert.deepEqual(result.adjacencyList.get('node_c'), []);
  assert.ok(result.edges
    .filter(edge => !edge.is_feedback_edge)
    .every(edge => edge.validation_method === 'callsite_mediation'));
});

test('observations ignore obsolete flowInstances fallback and use labelFlows only', () => {
  const result = buildObservations({
    nodeProfiles: [{
      node_id: 'node_sink',
      node_name: 'send.webhook',
      node_roles: ['external_egress'],
      security_tags: ['webhook_post'],
      data_surface: 'network',
      receiver_scope: 'third_party_service',
      retention_scope: 'external',
      trust_boundary: 'external_network'
    }],
    labelFlows: [],
    flowInstances: [labelFlow('legacy_lf', 'node_sink')]
  });

  assert.deepEqual(result.observations, []);
});

test('provenance graph ignores obsolete flowInstances fallback and uses labelFlows only', () => {
  const result = buildProvenanceGraph({
    labelFlows: [],
    flowInstances: [labelFlow('legacy_lf', 'node_sink')],
    observations: []
  });

  assert.equal(result.statistics.label_flow_node_count, 0);
  assert.deepEqual(result.label_flow_nodes, []);
});

function toolAt(name, file, line, column, extractionMethod) {
  return {
    name,
    canonical_name: name,
    type: 'tool_call',
    location: { file, line, column },
    extraction_method: extractionMethod,
    input: {},
    output: {}
  };
}

function callSite(name, canonicalName, callsiteId, callsiteOrder) {
  return {
    name,
    canonical_name: canonicalName,
    callsite_id: callsiteId,
    callsite_order: callsiteOrder,
    type: 'tool_call',
    input: {},
    output: {}
  };
}

function edge(source, target) {
  return {
    source,
    target,
    type: 'data_dependency',
    confidence: 0.8,
    validation_method: 'fixture',
    data_flow: { from_param: 'out', to_param: 'in', data_type: 'object' }
  };
}

function labelFlow(labelFlowId, currentNode) {
  return {
    label_flow_id: labelFlowId,
    current_node: currentNode,
    label: {
      label: 'pii.email',
      category: 'pii',
      subtype: 'email'
    }
  };
}
