const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { generateFCGJsonAsync } = require('../src/output/json-generator');
const { shouldAssistProfile, normalizeAssistantLabels, buildCacheKey, ONTOLOGY_VERSION, ALLOWED_LABELS } = require('../src/security/label-llm-assistant');
const { SkillFCGAnalyzer, parseArgs } = require('../src/index');
const { resolveOptions } = require('../scripts/fcg-batch');

test('low-confidence generic data profile triggers LLM label assist', () => {
  const result = shouldAssistProfile({
    node_roles: ['data_introduction'],
    node_name: 'read.payload',
    data_profile: {
      labels: [{ label: 'generic_data.data', evidence_level: 'L0', field_name: 'payload' }],
      unknown_tail: true
    },
    evidence: [{ text: 'payload content' }]
  });

  assert.equal(result.shouldAssist, true);
  assert.ok(result.reasons.includes('generic_only'));
});

test('high-confidence explicit deterministic labels do not trigger LLM assist', () => {
  const result = shouldAssistProfile({
    node_roles: ['data_introduction'],
    node_name: 'read.api_key',
    data_profile: {
      labels: [{ label: 'credentials.api_key', evidence_level: 'L4', field_name: 'api_key' }],
      unknown_tail: false
    },
    evidence: [{ text: 'api_key' }]
  });

  assert.equal(result.shouldAssist, false);
});

test('LLM label normalization enforces closed ontology and confidence cap', () => {
  const normalized = normalizeAssistantLabels({
    labels: [
      {
        label: 'pii.email',
        category: 'pii',
        subtype: 'email',
        field_name: 'payload',
        evidence_text: 'payload may include user email',
        reason: 'email evidence in description',
        confidence: 0.99,
        uncertainty: 'field is ambiguous'
      },
      {
        label: 'invented.secret_thing',
        category: 'invented',
        subtype: 'secret_thing',
        confidence: 0.9
      }
    ]
  }, {
    profile: { node_id: 'node_001', node_name: 'read.payload' },
    node: { id: 'node_001', name: 'read.payload', output: { payload: { type: 'string' } } },
    reason: { reasons: ['generic_only'] },
    model: 'mock-model'
  });

  assert.equal(normalized.labels.length, 1);
  assert.equal(normalized.ignored.length, 1);
  assert.equal(normalized.labels[0].label, 'pii.email');
  assert.equal(normalized.labels[0].mode, 'llm_assisted');
  assert.equal(normalized.labels[0].requires_review, true);
  assert.equal(normalized.labels[0].confidence, 0.65);
  assert.equal(normalized.labels[0].ontology_version, ONTOLOGY_VERSION);
  assert.equal(normalized.labels[0].ontology_label_id, 'pii.email');
});

test('LLM-assisted labels enter label flows and observations', async () => {
  let calls = 0;
  const result = await generateFixtureAsync({
    nodes: [
      sourceNode('node_001', 'read.payload', { payload: { type: 'string' } }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'payload', 'payload')]
  }, {
    labelLlmAssist: true,
    llmApiKey: 'test-key',
    llmModel: 'mock-model',
    labelAssistant: async () => {
      calls += 1;
      return {
        labels: [{
          label: 'pii.email',
          category: 'pii',
          subtype: 'email',
          field_name: 'payload',
          evidence_text: 'payload may contain email',
          reason: 'ambiguous payload is described as user content',
          confidence: 0.8,
          uncertainty: 'ambiguous payload'
        }]
      };
    }
  });

  const sourceProfile = result.security_profile.node_profiles.find(profile => profile.node_id === 'node_001');
  const webhookObservation = result.security_profile.observations.find(obs => obs.node_id === 'node_002');
  const labelFlowById = new Map(result.security_profile.label_flows.map(flow => [flow.label_flow_id, flow]));
  const dict = result.security_profile.label_dictionary || {};
  const labelOf = (flow) => flow.label || dict[flow.label_id] || {};
  const assistedFlow = webhookObservation.label_flow_ids.map(id => labelFlowById.get(id)).find(flow => labelOf(flow).label === 'pii.email');
  const assistedLabel = assistedFlow ? labelOf(assistedFlow) : undefined;

  assert.equal(calls, 1);
  assert.ok(sourceProfile.data_profile.labels.some(label => label.mode === 'llm_assisted'));
  assert.ok(assistedLabel);
  assert.equal(assistedLabel.mode, 'llm_assisted');
  assert.equal(assistedLabel.requires_review, true);
  assert.equal(assistedLabel.ontology_version, ONTOLOGY_VERSION);
  assert.equal(result.security_profile.statistics.label_llm_accepted_count, 1);
  assert.equal(result.security_profile.statistics.label_ontology_version, ONTOLOGY_VERSION);
});

test('LLM label assist cache avoids repeated model calls', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'label-llm-cache-'));
  const cachePath = path.join(tempDir, 'cache.jsonl');
  let calls = 0;
  const options = {
    labelLlmAssist: true,
    labelLlmCache: cachePath,
    llmApiKey: 'test-key',
    llmModel: 'mock-model',
    labelAssistant: async () => {
      calls += 1;
      return { labels: [{ label: 'pii.email', field_name: 'payload', evidence_text: 'payload', reason: 'mock', confidence: 0.7, uncertainty: 'mock' }] };
    }
  };

  await generateFixtureAsync({
    nodes: [sourceNode('node_001', 'read.payload', { payload: { type: 'string' } })],
    edges: []
  }, options);
  const second = await generateFixtureAsync({
    nodes: [sourceNode('node_001', 'read.payload', { payload: { type: 'string' } })],
    edges: []
  }, options);

  assert.equal(calls, 1);
  assert.equal(second.security_profile.statistics.label_llm_cache_hit_count, 1);
});

test('LLM label normalization rejects labels outside the configured ontology', () => {
  const normalized = normalizeAssistantLabels({
    labels: [
      { label: 'credentials.private_key', field_name: 'payload', evidence_text: 'private key', reason: 'mock', confidence: 0.8 },
      { label: 'not_allowed.secret', field_name: 'payload', evidence_text: 'secret', reason: 'mock', confidence: 0.8 }
    ]
  }, {
    profile: { node_id: 'node_001', node_name: 'read.payload' },
    node: { id: 'node_001', name: 'read.payload', output: { payload: { type: 'string' } } },
    reason: { reasons: ['generic_only'] },
    model: 'mock-model'
  });

  assert.equal(normalized.labels.length, 1);
  assert.equal(normalized.labels[0].label, 'credentials.private_key');
  assert.equal(normalized.ignored.length, 1);
  assert.ok(ALLOWED_LABELS.has('credentials.private_key'));
});

test('LLM label assist cache key includes ontology version', () => {
  const key = buildCacheKey({
    node_id: 'node_001',
    node_name: 'read.payload',
    node_roles: ['data_introduction'],
    security_tags: [],
    operation_tags: [],
    data_profile: { labels: [{ label: 'generic_data.data', evidence_level: 'L0' }] }
  }, {
    id: 'node_001',
    name: 'read.payload',
    output: { payload: { type: 'string' } }
  }, 'mock-model');

  assert.match(key, /^label_assist_/);
  assert.equal(typeof ONTOLOGY_VERSION, 'string');
});

test('LLM fallback label becomes review evidence when deterministic labels are explicit', async () => {
  const result = await generateFixtureAsync({
    nodes: [sourceNode('node_001', 'read.email', { email: { type: 'string' } })],
    edges: []
  }, {
    labelLlmAssist: true,
    llmApiKey: 'test-key',
    llmModel: 'mock-model',
    labelAssistant: async () => ({
      labels: [{
        label: 'generic_data.data',
        field_name: 'payload',
        evidence_text: 'generic payload',
        reason: 'fallback only',
        confidence: 0.6,
        uncertainty: 'fallback'
      }]
    })
  });

  const sourceProfile = result.security_profile.node_profiles.find(profile => profile.node_id === 'node_001');
  const labels = sourceProfile.data_profile.labels.map(label => label.label);

  assert.ok(labels.includes('pii.email'));
  assert.ok(!labels.includes('generic_data.data'));
  assert.equal(result.security_profile.statistics.label_llm_accepted_count, 0);
  assert.ok(sourceProfile.data_profile.review_evidence.some(item => item.fallback_suppressed === true));
});

test('analyzer rejects label LLM assist without API key', async () => {
  const analyzer = new SkillFCGAnalyzer({ labelLlmAssist: true, llmApiKey: '' });
  await assert.rejects(() => analyzer.analyze('missing.zip'), /LLM_API_KEY is required/);
});

test('CLI parses label LLM assist switches and batch resolve validates key', () => {
  const parsed = parseArgs(['analyze', 'x.zip', '--label-llm-assist', '--label-llm-concurrency', '3', '--label-llm-cache', 'cache.jsonl']);
  assert.equal(parsed.labelLlmAssist, true);
  assert.equal(parsed.labelLlmConcurrency, 3);
  assert.equal(parsed.labelLlmCache, 'cache.jsonl');

  assert.throws(() => resolveOptions({
    root: process.cwd(),
    labelLlmAssist: true,
    llmApiKey: ''
  }), /LLM_API_KEY is required/);
});

async function generateFixtureAsync({ nodes, edges }, options) {
  return generateFCGJsonAsync({
    skillData: { name: 'fixture-skill', version: '1.0.0' },
    graph: {
      getAllNodes() { return nodes; },
      getAllEdges() { return edges; }
    },
    sourceSink: { sources: [], sinks: [] },
    paths: [],
    allPaths: [],
    pathClusters: [],
    mode: 'full',
    inputSource: 'fixture.zip'
  }, options);
}

function sourceNode(id, name, output) {
  return { id, name, type: 'tool_call', category: 'Source', input: {}, output };
}

function sinkNode(id, name, input) {
  return { id, name, type: 'tool_call', category: 'Sink', isCritical: true, input, output: {} };
}

function edge(source, target, fromParam, toParam) {
  return {
    source,
    target,
    type: 'data_dependency',
    confidence: 0.9,
    validation_method: 'fixture',
    data_flow: { from_param: fromParam, to_param: toParam, data_type: 'string' }
  };
}


