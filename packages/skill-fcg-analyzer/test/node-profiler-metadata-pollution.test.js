const test = require('node:test');
const assert = require('node:assert/strict');

const {
  buildNodeProfile,
  nodeSecurityText,
  nodeActionText,
  externalEgressPattern,
  detectActionMentions
} = require('../src/security/node-profiler');

const SINK_OPS = new Set(['external_egress', 'model_inference', 'command_execution', 'destructive_operation']);
function stepOps(profile) {
  return (profile.action_steps || []).map(s => s.operation_type);
}
function stepEvidenceTexts(profile) {
  return (profile.action_steps || []).map(s => (s.evidence && s.evidence[0] && s.evidence[0].text) || '');
}
// Markers that only appear when serialized semantic_gate / action_evidence JSON
// leaks into the text that gets sliced into action steps.
const JSON_LEAK = /extraction_method|semantic_llm_gate|completed_sentence|actionability|"snippet"|"reason":"As a/;

// A pure routing node (op=condition) that also carries a semantic_gate whose
// reason prose mentions "model"/"send" and an action_evidence blob. Before the
// fix this fabricated external_egress/model_inference action steps and polluted
// child instructionText with JSON fragments.
function routingNodeWithMetadata() {
  return {
    id: 'node_c',
    name: 'doc.step.skill.l10.s6.condition.semantic_condition',
    operationType: 'condition',
    instructionText: 'When evaluating skills shared by other agents',
    formal_semantics: {
      operation_type: 'condition',
      evidence: { text: 'When evaluating skills shared by other agents' },
      targets: []
    },
    semantic_gate: {
      classification: 'workflow_instruction',
      actionability: 'runtime_action',
      completed_sentence: 'Use this skill when evaluating skills shared by other agents.',
      reason: 'As a When to Use list item it flows to the model and may send a request'
    },
    source_context: {
      action_evidence: {
        snippet: 'When evaluating skills shared by other agents',
        extraction_method: 'rule+semantic_llm+semantic_llm_gate',
        grounded: true
      }
    }
  };
}

test('nodeActionText excludes node name and all serialized JSON metadata', () => {
  const node = routingNodeWithMetadata();
  const text = nodeActionText(node);
  assert.ok(!/semantic_condition/.test(text), 'must not contain node name');
  assert.ok(!JSON_LEAK.test(text), 'must not contain gate/action_evidence JSON keys');
  assert.ok(/evaluating skills shared/.test(text), 'must keep the real instruction prose');
});

test('nodeSecurityText no longer serializes semantic_gate / action_evidence', () => {
  const text = nodeSecurityText(routingNodeWithMetadata(), {});
  assert.ok(!/extraction_method/.test(text), 'action_evidence JSON should be excluded');
  assert.ok(!/completed_sentence/.test(text), 'semantic_gate JSON should be excluded');
});

test('routing node does not fabricate sink action steps from metadata', () => {
  const profile = buildNodeProfile(routingNodeWithMetadata(), {});
  const ops = stepOps(profile);
  for (const op of ops) {
    assert.ok(!SINK_OPS.has(op), `routing node should not have sink step "${op}" (got ${ops.join(',')})`);
  }
  assert.ok(!profile.node_roles.some(r => SINK_OPS.has(r)),
    `routing node roles should not include a sink role (got ${profile.node_roles.join(',')})`);
});

test('routing node action steps carry no serialized-JSON evidence fragments', () => {
  const profile = buildNodeProfile(routingNodeWithMetadata(), {});
  for (const text of stepEvidenceTexts(profile)) {
    assert.ok(!JSON_LEAK.test(text), `step evidence must be clean prose, got: ${text.slice(0, 80)}`);
  }
});

// ---- Recall regressions: real sinks must still be detected ----

test('real webhook egress still detected (recall)', () => {
  const profile = buildNodeProfile({
    id: 'e', name: 'webhook.post', operationType: 'invoke_tool',
    instructionText: 'POST payload to https://api.example.com/webhook',
    formal_semantics: { operation_type: 'invoke_tool', evidence: { text: 'send payload to the webhook endpoint' }, targets: [{ type: 'url', value: 'https://x' }] }
  }, {});
  assert.ok(profile.node_roles.includes('external_egress'), `expected external_egress, got ${profile.node_roles.join(',')}`);
});

test('real shell command still detected (recall)', () => {
  const profile = buildNodeProfile({
    id: 'c', name: 'script.run', operationType: 'command_execution',
    instructionText: 'execute shell command via subprocess',
    formal_semantics: { operation_type: 'command_execution', evidence: { text: 'run shell command' }, targets: [] }
  }, {});
  assert.ok(profile.node_roles.includes('command_execution'), `expected command_execution, got ${profile.node_roles.join(',')}`);
});

test('real model inference still detected (recall)', () => {
  const profile = buildNodeProfile({
    id: 'm', name: 'llm.inference', operationType: 'model_inference',
    instructionText: 'call the gpt model for a completion',
    formal_semantics: { operation_type: 'model_inference', evidence: { text: 'llm inference' }, targets: [] }
  }, {});
  assert.ok(profile.node_roles.includes('model_inference'), `expected model_inference, got ${profile.node_roles.join(',')}`);
});

// ---- Prose over-match precision (fix B regex tightening) ----

test('externalEgressPattern rejects descriptive prose, accepts real egress', () => {
  // false-positive prose that previously matched bare share/post/api/external
  assert.equal(externalEgressPattern('skills shared by other agents'), false);
  assert.equal(externalEgressPattern('post-processing the results'), false);
  assert.equal(externalEgressPattern('see the API documentation'), false);
  assert.equal(externalEgressPattern('call the external tool'), false);
  // real egress signals
  assert.equal(externalEgressPattern('webhook.post'), true);
  assert.equal(externalEgressPattern('api.call to service'), true);
  assert.equal(externalEgressPattern('send the payload to the webhook'), true);
  assert.equal(externalEgressPattern('upload file to server'), true);
});

test('detectActionMentions does not tag "shared"/"post-processing" as egress', () => {
  const egressOf = t => detectActionMentions(t).filter(m => m.operation_type === 'external_egress');
  assert.equal(egressOf('evaluate skills shared by other agents').length, 0);
  assert.equal(egressOf('post-processing step for the report').length, 0);
  // real egress verb+object still tagged
  assert.ok(egressOf('send the data to the external webhook').length >= 1);
});
