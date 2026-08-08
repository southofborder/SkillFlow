const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  generateFlowchartArtifacts,
  deriveFlowchartPaths,
  saveFlowchartArtifacts
} = require('../src/output/flowchart-generator');

test('generateFlowchartArtifacts includes mermaid and bounded detail preview sections', () => {
  const sample = {
    meta: {
      skill_name: 'sample',
      skill_version: '1.0.0',
      analysis_mode: 'full',
      analysis_timestamp: '2026-04-23T00:00:00.000Z'
    },
    statistics: {
      total_nodes: 2,
      total_edges: 1,
      source_count: 1,
      sink_count: 1,
      total_paths: 1,
      source_to_sink_paths: 1,
      high_risk_paths: 1
    },
    nodes: [
      {
        id: 'node_001',
        name: 'user.query',
        type: 'builtin_call',
        category: 'Source',
        is_critical: false
      },
      {
        id: 'node_002',
        name: 'llm.inference',
        type: 'builtin_call',
        category: 'Sink',
        is_critical: true
      },
      {
        id: 'node_003',
        name: 'doc.step.skill.l7.s1.read.memory',
        type: 'custom_func',
        category: 'Source',
        is_critical: false,
        location: { file: 'SKILL.md', line: 7, section: '' },
        formal_semantics: {
          operation_type: 'read',
          targets: [{ type: 'file', value: 'memory.md' }],
          conditions: [],
          effects: ['read_context'],
          evidence: { text: 'Read memory.md' }
        }
      }
    ],
    edges: [
      {
        id: 'edge_001',
        source: 'node_001',
        target: 'node_002',
        type: 'data_dependency',
        confidence: 0.9,
        data_flow: {
          from_param: 'query_text',
          to_param: 'user_query',
          data_type: 'string'
        }
      }
    ],
    source_sink: { sources: [], sinks: [] },
    paths: {
      all_paths: [],
      source_to_sink_paths: [
        {
          path_id: 'path_001',
          source_node: 'node_001',
          sink_node: 'node_002',
          length: 2,
          risk_level: 'critical',
          data_transferred: 'query_text -> user_query'
        }
      ],
      path_clusters: [
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
      ]
    },
    risks: [],
    security_profile: {
      version: '4.9',
      label_flows: [],
      provenance_graph: { propagation_edges: [] },
      observations: [],
      statistics: { truncated: false }
    }
  };

  const artifacts = generateFlowchartArtifacts(sample);
  assert.ok(artifacts.mermaid.includes('flowchart TD'));
  assert.ok(artifacts.mermaid.includes('node_001'));
  assert.ok(artifacts.markdown.includes('## Diagram (Mermaid)'));
  assert.ok(artifacts.markdown.includes('## Path Clusters (Semantic Groups)'));
  assert.ok(artifacts.markdown.includes('## Formal Markdown Semantics'));
  assert.ok(artifacts.markdown.includes('memory.md'));
  assert.ok(artifacts.markdown.includes('cluster_001'));
  assert.ok(artifacts.markdown.includes('## Detail Preview'));
  assert.ok(artifacts.markdown.includes('### Security Profile'));
  assert.ok(artifacts.markdown.includes('Label Flows'));
});

test('saveFlowchartArtifacts writes markdown and mermaid files', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-flowchart-'));
  try {
    const markdownPath = path.join(tempDir, 'out.flow.md');
    const mermaidPath = path.join(tempDir, 'out.flow.mmd');
    saveFlowchartArtifacts(
      {
        meta: { skill_name: 'x', skill_version: '1', analysis_mode: 'quick', analysis_timestamp: new Date().toISOString() },
        statistics: {},
        nodes: [],
        edges: [],
        source_sink: {},
        paths: { all_paths: [], source_to_sink_paths: [] },
        risks: []
      },
      markdownPath,
      mermaidPath
    );
    assert.equal(fs.existsSync(markdownPath), true);
    assert.equal(fs.existsSync(mermaidPath), true);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('deriveFlowchartPaths derives sidecar names from json output', () => {
  const paths = deriveFlowchartPaths('C:/tmp/result.json');
  assert.equal(paths.markdownPath.endsWith('result.flow.md'), true);
  assert.equal(paths.mermaidPath.endsWith('result.flow.mmd'), true);
});


