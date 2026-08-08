const test = require('node:test');
const assert = require('node:assert/strict');

const { generateFCGJson } = require('../src/output/json-generator');

test('generateFCGJson uses graph node categories and critical flag', () => {
  const graph = {
    getAllNodes() {
      return [
        {
          id: 'node_001',
          name: 'user.query',
          type: 'builtin_call',
          category: 'Source',
          isCritical: false,
          input: {},
          output: { query_text: { type: 'string' } }
        },
        {
          id: 'node_002',
          name: 'llm.inference',
          type: 'builtin_call',
          category: 'Sink',
          isCritical: true,
          input: { skill_content: { type: 'string' } },
          output: { response: { type: 'string' } }
        },
        {
          id: 'node_003',
          name: 'doc.step.skill.l7.s1.read.memory',
          type: 'custom_func',
          category: 'Source',
          isCritical: false,
          input: { file_path: { type: 'string' } },
          output: { content: { type: 'string' } },
          semanticKind: 'doc_step',
          ownerDoc: 'SKILL.md',
          docRef: 'memory.md',
          docAction: 'read',
          docActions: ['read'],
          formal_semantics: {
            operation_type: 'read',
            actor: 'llm',
            inputs: [{ name: 'memory.md', type: 'file' }],
            outputs: [{ name: 'context', type: 'string' }],
            targets: [{ type: 'file', value: 'memory.md', raw: 'memory.md' }],
            conditions: [],
            effects: ['read_context'],
            confidence: 0.8,
            evidence: {
              text: 'Read memory.md',
              file: 'SKILL.md',
              line: 7,
              section: '',
              method: 'rule'
            }
          },
          member_steps: [
            {
              line: 7,
              operation_type: 'read',
              instruction: 'Read memory.md'
            }
          ]
        }
      ];
    },
    getAllEdges() {
      return [
        {
          source: 'node_001',
          target: 'node_002',
          type: 'data_dependency',
          confidence: 0.9,
          validation_method: 'dependency_llm_high_value',
          data_flow: {
            from_param: 'query_text',
            to_param: 'user_query',
            data_type: 'string'
          }
        }
      ];
    }
  };

  const result = generateFCGJson({
    skillData: { name: 'demo-skill', version: '1.0.0' },
    graph,
    sourceSink: {
      sources: [{ node_id: 'node_001', reason: 'User input', data_type: 'query_text' }],
      sinks: [{ node_id: 'node_002', reason: 'LLM call', data_type: 'skill_content', is_critical: true }]
    },
    paths: [
      {
        path_id: 'path_001',
        nodes: ['node_001', 'node_002'],
        length: 2,
        source_node: 'node_001',
        sink_node: 'node_002',
        risk_level: 'critical',
        data_transferred: 'query_text -> skill_content'
      }
    ],
    allPaths: [
      {
        path_id: 'all_path_001',
        nodes: ['node_001', 'node_002'],
        length: 2,
        has_source: true,
        has_sink: true,
        is_complete: true
      }
    ],
    pathClusters: [
      {
        cluster_id: 'cluster_001',
        semantic_template: 'user.query -> llm.inference',
        path_count: 1,
        risk_distribution: { critical: 1, high: 0, medium: 0, low: 0 },
        representative_path_id: 'path_001',
        representative_path_nodes: ['node_001', 'node_002'],
        representative_path_names: ['user.query', 'llm.inference'],
        source_nodes: ['node_001'],
        sink_nodes: ['node_002'],
        source_names: ['user.query'],
        sink_names: ['llm.inference'],
        involved_modules: ['llm', 'user'],
        involved_triggers: [],
        involved_policies: [],
        involved_documents: [],
        path_ids: ['path_001']
      }
    ],
    mode: 'full',
    inputSource: '/tmp/demo.zip'
  });

  const userNode = result.nodes.find(n => n.id === 'node_001');
  const llmNode = result.nodes.find(n => n.id === 'node_002');

  assert.equal(userNode.category, 'Source');
  assert.equal(llmNode.category, 'Sink');
  assert.equal(llmNode.is_critical, true);
  const docNode = result.nodes.find(n => n.id === 'node_003');
  assert.equal(docNode.formal_semantics.operation_type, 'read');
  assert.equal(docNode.semanticKind, 'doc_step');
  assert.equal(docNode.member_steps.length, 1);
  assert.equal(result.risks[0].type, 'critical_data_leakage');
  assert.equal(result.paths.path_clusters.length, 1);
  assert.equal(result.paths.path_clusters[0].cluster_id, 'cluster_001');
  assert.equal(result.security_profile.version, '5.1');
  assert.ok(Array.isArray(result.security_profile.node_profiles));
  assert.ok(Array.isArray(result.security_profile.label_flows));
  assert.equal(typeof result.security_profile.provenance_graph, 'object');
  assert.ok(Array.isArray(result.security_profile.observations));

  const userProfile = result.security_profile.node_profiles.find(profile => profile.node_id === 'node_001');
  const llmProfile = result.security_profile.node_profiles.find(profile => profile.node_id === 'node_002');
  const docProfile = result.security_profile.node_profiles.find(profile => profile.node_id === 'node_003');

  assert.ok(userProfile.node_roles.includes('data_introduction'));
  assert.ok(userProfile.node_roles.includes('control_context'));
  assert.ok(userProfile.security_tags.includes('user_input'));
  assert.ok(userProfile.data_profile.labels.some(label => label.category === 'user_prompt'));

  assert.ok(llmProfile.node_roles.includes('model_inference'));
  assert.ok(llmProfile.security_tags.includes('model_context'));
  assert.equal(llmProfile.receiver_scope, 'model_provider');

  assert.ok(docProfile.node_roles.includes('data_introduction'));
  assert.ok(docProfile.data_profile.labels.some(label => label.category === 'file_content'));

  const llmObservation = result.security_profile.observations.find(obs => obs.node_id === 'node_002');
  const labelFlowById = new Map(result.security_profile.label_flows.map(flow => [flow.label_flow_id, flow]));
  const observedFlows = llmObservation.label_flow_ids.map(id => labelFlowById.get(id));
  const dict = result.security_profile.label_dictionary || {};
  const labelOf = (flow) => flow.label || dict[flow.label_id] || {};
  assert.ok(llmObservation);
  assert.ok(llmObservation.label_flow_ids.length > 0);
  assert.ok(observedFlows.some(flow => labelOf(flow).category === 'user_prompt'));
  assert.ok(result.security_profile.provenance_graph.observation_links.some(link => link.observation_id === llmObservation.observation_id));
});


