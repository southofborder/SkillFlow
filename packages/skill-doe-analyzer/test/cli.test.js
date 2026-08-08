const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { main, parseArgs } = require('../src/index');

function withEnv(name, value, fn) {
  const previous = process.env[name];
  if (value === undefined) delete process.env[name];
  else process.env[name] = value;
  return Promise.resolve()
    .then(fn)
    .finally(() => {
      if (previous === undefined) delete process.env[name];
      else process.env[name] = previous;
    });
}

test('parseArgs reads analyze options', () => {
  const args = parseArgs([
    'analyze',
    '--fcg', 'in.json',
    '--out', 'out.json',
    '--group-baseline', 'group.json',
    '--threshold', '0.8',
    '--pretty',
    '--no-llm-judge',
    '--llm-cache', 'cache.jsonl',
    '--llm-batch-size', '5',
    '--llm-votes', '1',
    '--llm-concurrency', '2',
    '--llm-escalation-votes', '3',
    '--llm-escalation-policy', 'risk_or_uncertain',
    '--llm-max-batch-chars', '60000'
  ]);
  assert.equal(args.command, 'analyze');
  assert.equal(args.fcg, 'in.json');
  assert.equal(args.out, 'out.json');
  assert.equal(args.groupBaseline, 'group.json');
  assert.equal(args.threshold, 0.8);
  assert.equal(args.pretty, true);
  assert.equal(args.llmJudge, false);
  assert.equal(args.llmCache, 'cache.jsonl');
  assert.equal(args.llmBatchSize, 5);
  assert.equal(args.llmVotes, 1);
  assert.equal(args.llmConcurrency, 2);
  assert.equal(args.llmEscalationVotes, 3);
  assert.equal(args.llmEscalationPolicy, 'risk_or_uncertain');
  assert.equal(args.llmMaxBatchChars, 60000);
});

test('CLI analyze reads FCG and writes pretty rule-only JSON', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-doe-cli-'));
  try {
    const fcgPath = path.join(dir, 'fcg.json');
    const outPath = path.join(dir, 'doe.json');
    fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg()), 'utf-8');
    await main(['analyze', '--fcg', fcgPath, '--out', outPath, '--pretty', '--no-llm-judge']);
    const result = JSON.parse(fs.readFileSync(outPath, 'utf-8'));
    assert.equal(result.version, '0.3');
    assert.equal(result.assessment_unit, 'observation_label_flow');
    assert.equal(result.assessments.length, 1);
    assert.equal(typeof result.assessments[0].boundary_crossed, 'boolean');
    assert.equal(typeof result.assessments[0].necessity_score, 'number');
    assert.equal(result.statistics.llm_judge_enabled, false);
    assert.ok(fs.readFileSync(outPath, 'utf-8').includes('\n  "version"'));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('CLI default LLM judge requires LLM_API_KEY', async () => {
  await withEnv('LLM_API_KEY', undefined, async () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-doe-cli-key-'));
    try {
      const fcgPath = path.join(dir, 'fcg.json');
      fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg()), 'utf-8');
      await assert.rejects(
        () => main(['analyze', '--fcg', fcgPath]),
        /LLM_API_KEY is required/
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });
});

test('CLI reports missing security profile as clear error', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-doe-cli-error-'));
  try {
    const fcgPath = path.join(dir, 'bad.json');
    fs.writeFileSync(fcgPath, JSON.stringify({}), 'utf-8');
    await assert.rejects(
      () => main(['analyze', '--fcg', fcgPath, '--no-llm-judge']),
      /missing security_profile/
    );
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

function minimalFcg() {
  return {
    meta: { skill_name: 'cli test' },
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
