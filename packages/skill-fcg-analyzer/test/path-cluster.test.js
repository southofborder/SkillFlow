const test = require('node:test');
const assert = require('node:assert/strict');

const { clusterSourceToSinkPaths } = require('../src/analyzer/path-extractor');

test('clusterSourceToSinkPaths groups by semantic template and keeps full path ids', () => {
  const graph = {
    getNode(nodeId) {
      const map = {
        node_001: { name: 'user.query' },
        node_002: { name: 'rule.trigger.user_correction' },
        node_003: { name: 'llm.inference' },
        node_004: { name: 'rule.policy.log_corrections' },
        node_005: { name: 'doc.file.corrections' },
        node_006: { name: 'rule.trigger.execution_failure' },
        node_007: { name: 'doc.file.memory' }
      };
      return map[nodeId] || null;
    }
  };

  const paths = [
    {
      path_id: 'path_001',
      nodes: ['node_001', 'node_002', 'node_003', 'node_004', 'node_005'],
      source_node: 'node_001',
      sink_node: 'node_005',
      risk_level: 'high'
    },
    {
      path_id: 'path_002',
      nodes: ['node_001', 'node_006', 'node_003', 'node_004', 'node_007'],
      source_node: 'node_001',
      sink_node: 'node_007',
      risk_level: 'critical'
    },
    {
      path_id: 'path_003',
      nodes: ['node_001', 'node_003', 'node_007'],
      source_node: 'node_001',
      sink_node: 'node_007',
      risk_level: 'critical'
    }
  ];

  const clusters = clusterSourceToSinkPaths(paths, graph);
  assert.equal(clusters.length, 2);

  const mainCluster = clusters.find(item => item.semantic_template.includes('rule.trigger'));
  assert.ok(mainCluster);
  assert.equal(mainCluster.path_count, 2);
  assert.deepEqual(mainCluster.path_ids.sort(), ['path_001', 'path_002']);
  assert.equal(mainCluster.involved_policies.includes('rule.policy.log_corrections'), true);
  assert.equal(mainCluster.involved_documents.includes('doc.file.corrections'), true);
  assert.equal(mainCluster.involved_documents.includes('doc.file.memory'), true);

  const shortCluster = clusters.find(item => item.path_ids.includes('path_003'));
  assert.ok(shortCluster);
  assert.equal(shortCluster.path_count, 1);
  assert.equal(shortCluster.representative_path_id, 'path_003');
});
