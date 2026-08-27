const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');

const {
  resolveOptions,
  discoverFcgFiles,
  buildDoeOutputPath,
  runDoeBatch
} = require('../scripts/doe-batch');

test('DOE batch resolve requires API key for default LLM judge', () => {
  const root = makeRunRoot();
  assert.throws(() => resolveOptions({
    root,
    llmApiKey: ''
  }), /LLM_API_KEY/);
});

test('DOE batch resolve accepts LLM acceleration options', () => {
  const root = makeRunRoot();
  const options = resolveOptions({
    root,
    llmApiKey: 'test-key',
    llmConcurrency: 3,
    llmEscalationVotes: 5,
    llmEscalationPolicy: 'all',
    llmMaxBatchChars: 50000
  });

  assert.equal(options.llmConcurrency, 3);
  assert.equal(options.llmEscalationVotes, 5);
  assert.equal(options.llmEscalationPolicy, 'all');
  assert.equal(options.llmMaxBatchChars, 50000);
});

test('DOE batch writes per-skill outputs and summary in rule-only mode', async () => {
  const root = makeRunRoot();
  const fcgPath = path.join(root, 'fcg', 'skills', 'skill-a-sfg.json');
  fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg()), 'utf-8');

  const options = resolveOptions({
    root,
    llmJudge: false,
    concurrency: 1
  });
  const summary = await runDoeBatch(options);
  const doePath = buildDoeOutputPath(fcgPath, options.output);

  assert.equal(discoverFcgFiles(options.fcgRoot).length, 1);
  assert.equal(path.basename(doePath), 'skill-a-doe.json');
  assert.equal(summary.success_count, 1);
  assert.equal(summary.assessment_count, 1);
  assert.equal(summary.llm_first_pass_count, 0);
  assert.equal(summary.llm_escalated_count, 0);
  assert.equal(summary.llm_timeout_split_count, 0);
  assert.ok(fs.existsSync(doePath));
  assert.ok(fs.existsSync(path.join(options.output, 'doe-summary.json')));
  assert.ok(fs.existsSync(path.join(options.output, 'doe-summary.md')));
});

test('DOE batch reuses existing JSON when refresh is false', async () => {
  const root = makeRunRoot();
  const fcgPath = path.join(root, 'fcg', 'skills', 'skill-a-sfg.json');
  const outputRoot = path.join(root, 'doe');
  fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg()), 'utf-8');
  const doePath = buildDoeOutputPath(fcgPath, outputRoot);
  fs.mkdirSync(path.dirname(doePath), { recursive: true });
  fs.writeFileSync(doePath, JSON.stringify({
    statistics: {
      assessment_count: 2,
      potential_doe_count: 1,
      requires_review_count: 1
    }
  }), 'utf-8');

  const summary = await runDoeBatch(resolveOptions({
    root,
    llmJudge: false,
    output: outputRoot,
    concurrency: 1
  }));

  assert.equal(summary.success_count, 1);
  assert.equal(summary.reused_count, 1);
  assert.equal(summary.assessment_count, 2);
  assert.equal(summary.potential_doe_count, 1);
});

function makeRunRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'doe-batch-'));
  fs.mkdirSync(path.join(root, 'fcg', 'skills'), { recursive: true });
  return root;
}

function minimalFcg() {
  return {
    meta: { skill_name: 'batch fixture' },
    nodes: [],
    edges: [],
    security_profile: {
      version: '4.9',
      node_profiles: [{
        node_id: 'node_1',
        node_name: 'send.webhook',
        node_roles: ['external_egress'],
        security_tags: ['network_egress'],
        operation_tags: [],
        formal_semantics: {
          operation_type: 'external_egress',
          inputs: [],
          outputs: [],
          targets: [],
          evidence: { text: 'Post payload to webhook' }
        }
      }],
      label_flows: [{
        label_flow_id: 'lf_1',
        current_node: 'node_1',
        node_path: ['node_0', 'node_1'],
        node_names: ['read.api_key', 'send.webhook'],
        label: {
          label: 'credentials.api_key',
          category: 'credentials',
          subtype: 'api_key',
          confidence: 0.9
        },
        confidence: 0.9,
        filter_events: []
      }],
      observations: [{
        observation_id: 'obs_1',
        node_id: 'node_1',
        node_name: 'send.webhook',
        node_roles: ['external_egress'],
        security_tags: ['network_egress'],
        boundary: {
          data_surface: 'network',
          receiver_scope: 'third_party_service',
          retention_scope: 'external',
          trust_boundary: 'external_network'
        },
        operation_type: 'external_egress',
        label_flow_ids: ['lf_1']
      }]
    }
  };
}
