const test = require('node:test');
const assert = require('node:assert/strict');

const { analyzeGraphTransfers } = require('../src/security/graph-transfer-analyzer');

test('sink observation is recorded when a label reaches sink before transfer cap stops expansion', () => {
  const sourceProfile = {
    node_id: 'node_source',
    node_name: 'read.customer.email',
    node_roles: ['data_introduction'],
    security_tags: ['file_read'],
    data_surface: 'local_file',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process',
    data_profile: {
      labels: [{
        label: 'pii.email',
        category: 'pii',
        subtype: 'email',
        sensitivity: 'high',
        origin_node: 'node_source',
        introduced_at: 'node_source',
        confidence: 0.95
      }]
    }
  };
  const sinkProfile = {
    node_id: 'node_sink',
    node_name: 'send.webhook',
    node_roles: ['external_egress'],
    security_tags: ['webhook_post'],
    data_surface: 'network',
    receiver_scope: 'third_party_service',
    retention_scope: 'external',
    trust_boundary: 'external_network',
    formal_semantics: {
      operation_type: 'invoke_tool'
    }
  };

  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'node_source' }, { id: 'node_sink' }],
    edges: [{
      id: 'edge_001',
      source: 'node_source',
      target: 'node_sink',
      type: 'data_dependency',
      confidence: 1
    }],
    nodeProfiles: [sourceProfile, sinkProfile],
    limits: {
      maxLabelFlows: 2,
      maxEvents: 20,
      maxDepth: 4,
      maxBranchesPerNode: 4
    }
  });

  assert.equal(transfer.truncated, true);
  assert.equal(transfer.label_flows.length, 2);
  assert.equal(transfer.observation_events.length, 1);
  assert.equal(transfer.observation_events[0].node_id, 'node_sink');
  assert.equal(transfer.observation_events[0].operation_type, 'invoke_tool');
});

test('P2-A: label crossing a pure-order control_flow edge becomes may_flow (not definite)', () => {
  const sourceProfile = {
    node_id: 'node_source', node_name: 'read.doc',
    node_roles: ['data_introduction'], security_tags: ['file_read'],
    data_surface: 'local_file', receiver_scope: 'local_runtime',
    retention_scope: 'transient', trust_boundary: 'local_process',
    data_profile: { labels: [{ label: 'file_content.document', category: 'file_content', subtype: 'document', sensitivity: 'high', origin_node: 'node_source', introduced_at: 'node_source', confidence: 0.95 }] }
  };
  const nextProfile = {
    node_id: 'node_next', node_name: 'doc.step.next',
    node_roles: ['transform'], data_surface: 'local_file',
    receiver_scope: 'local_runtime', retention_scope: 'transient', trust_boundary: 'local_process'
  };

  function run(edgeDataFlow) {
    return analyzeGraphTransfers({
      nodes: [{ id: 'node_source' }, { id: 'node_next' }],
      edges: [{ id: 'e1', source: 'node_source', target: 'node_next', type: 'control_flow', data_flow: edgeDataFlow, confidence: 1 }],
      nodeProfiles: [sourceProfile, nextProfile],
      limits: { maxLabelFlows: 50, maxEvents: 200, maxDepth: 6, maxBranchesPerNode: 6 }
    });
  }

  // pure-order edge (state>state): child flow at node_next must be may_flow.
  const ordered = run({ from_param: 'state', to_param: 'state', data_type: 'object' });
  const orderedChild = ordered.label_flows.find(f => f.current_node === 'node_next');
  assert.ok(orderedChild, 'expected a flow reaching node_next');
  assert.equal(orderedChild.flow_mode, 'may_flow');

  // data-carrying control_flow edge (response>context): child flow stays definite_flow.
  const carried = run({ from_param: 'response', to_param: 'context', data_type: 'string' });
  const carriedChild = carried.label_flows.find(f => f.current_node === 'node_next');
  assert.ok(carriedChild, 'expected a flow reaching node_next');
  assert.equal(carriedChild.flow_mode, 'definite_flow');
});

test('P2-A: semantic flow_mode (source_introduction) is preserved across a pure-order edge', () => {
  // node_next introduces a NEW label (data_introduction). Even reached via a pure-order
  // edge, its source_introduction mode must NOT be downgraded to may_flow.
  const sourceProfile = {
    node_id: 'node_source', node_name: 'read.doc',
    node_roles: ['data_introduction'], data_surface: 'local_file',
    receiver_scope: 'local_runtime', retention_scope: 'transient', trust_boundary: 'local_process',
    data_profile: { labels: [{ label: 'file_content.document', category: 'file_content', subtype: 'document', origin_node: 'node_source', introduced_at: 'node_source', confidence: 0.95 }] }
  };
  const introProfile = {
    node_id: 'node_next', node_name: 'llm.inference',
    node_roles: ['data_introduction', 'model_inference'],
    data_surface: 'model_context', receiver_scope: 'local_runtime',
    retention_scope: 'transient', trust_boundary: 'model_context',
    data_profile: { labels: [{ label: 'ai_context.generated', category: 'ai_context', subtype: 'generated', origin_node: 'node_next', introduced_at: 'node_next', confidence: 0.9 }] }
  };
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'node_source' }, { id: 'node_next' }],
    edges: [{ id: 'e1', source: 'node_source', target: 'node_next', type: 'control_flow', data_flow: { from_param: 'state', to_param: 'state' }, confidence: 1 }],
    nodeProfiles: [sourceProfile, introProfile],
    limits: { maxLabelFlows: 50, maxEvents: 200, maxDepth: 6, maxBranchesPerNode: 6 }
  });
  const introFlow = transfer.label_flows.find(f => f.current_node === 'node_next' && f.flow_mode === 'source_introduction');
  assert.ok(introFlow, 'source_introduction at node_next must be preserved, not downgraded to may_flow');
});

