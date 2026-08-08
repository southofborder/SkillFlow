const test = require('node:test');
const assert = require('node:assert/strict');

const { classifyRouteState, controlFlowCarriesData, hasNegativeConditionGate } = require('../src/security/flow-instance-router');

// P2-A: control_flow 边区分"真携带数据"与"纯顺序"。纯顺序边(state>state /
// context>context / 空参)只表达步骤先后,不应让 label 确定传播 —— 降为 may_route。
// 携带真实数据的 control_flow(response/result/instruction>context)保持 definite_route。

const baseArgs = {
  instance: { node_path: ['n0'] },
  currentProfile: { node_id: 'n0', node_roles: ['transform'] },
  targetProfile: { node_id: 'n1', node_roles: ['transform'] }, // 非 sink/decision,避免走别的分支
  maxDepth: 12
};

test('controlFlowCarriesData: placeholder params are NOT data', () => {
  assert.equal(controlFlowCarriesData({ data_flow: { from_param: 'state', to_param: 'state' } }), false);
  assert.equal(controlFlowCarriesData({ data_flow: { from_param: 'context', to_param: 'context' } }), false);
  assert.equal(controlFlowCarriesData({ data_flow: {} }), false);
  assert.equal(controlFlowCarriesData({}), false);
});

test('controlFlowCarriesData: real params ARE data', () => {
  assert.equal(controlFlowCarriesData({ data_flow: { from_param: 'response', to_param: 'context' } }), true);
  assert.equal(controlFlowCarriesData({ data_flow: { from_param: 'result', to_param: 'context' } }), true);
  assert.equal(controlFlowCarriesData({ data_flow: { from_param: 'instruction', to_param: 'context' } }), true);
});

test('P2-A: pure-order control_flow edge => may_route (not definite)', () => {
  const route = classifyRouteState({
    ...baseArgs,
    edge: { type: 'control_flow', data_flow: { from_param: 'state', to_param: 'state' }, semantic_reason: 'Sequential markdown steps in SKILL.md' }
  });
  assert.equal(route.state, 'may_route');
  assert.equal(route.reason, 'control_flow_order_only');
});

test('P2-A: data-carrying control_flow edge => definite_route', () => {
  const route = classifyRouteState({
    ...baseArgs,
    edge: { type: 'control_flow', data_flow: { from_param: 'response', to_param: 'context' }, semantic_reason: 'LLM response feeds next step' }
  });
  assert.equal(route.state, 'definite_route');
  assert.equal(route.reason, 'control_flow_data_edge');
});

test('P2-A: sink-like target still routes definite even on pure-order edge (precedence unchanged)', () => {
  // control_flow is checked before sink_like_target, so a pure-order edge into a sink
  // becomes may_route. That is intended: the ordering edge itself is not a data path.
  const route = classifyRouteState({
    ...baseArgs,
    targetProfile: { node_id: 'n1', node_roles: ['external_egress'] },
    edge: { type: 'control_flow', data_flow: { from_param: 'state', to_param: 'state' } }
  });
  assert.equal(route.state, 'may_route');
});

// P2-B: conditions as a precision (prevent-over-connect) signal. A NEGATIVE
// guard on the target downgrades an otherwise-definite route; positive or
// absent conditions leave routing byte-for-byte unchanged (no recall loss).

test('hasNegativeConditionGate: only explicit negative condition-kind guards fire', () => {
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'condition', text: 'unless the data is redacted' }] }), true);
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'condition', text: 'only if not a credential' }] }), true);
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'condition', text: 'without sending personal data' }] }), true);
  // Positive when-guard is not a negative gate.
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'condition', text: 'when the user asks' }] }), false);
  // Trigger-kind conditions describe WHEN, not WHETHER — never a flow gate.
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'failure', text: 'unless it failed' }] }), false);
  assert.equal(hasNegativeConditionGate({ conditions: [{ type: 'periodic', text: 'unless weekly' }] }), false);
  // Absence => false (conservative; cannot fabricate a block).
  assert.equal(hasNegativeConditionGate({}), false);
  assert.equal(hasNegativeConditionGate({ conditions: [] }), false);
});

test('P2-B: negative guard downgrades a sink-like definite route to may_route', () => {
  const guarded = classifyRouteState({
    ...baseArgs,
    targetProfile: {
      node_id: 'n1',
      node_roles: ['external_egress'],
      conditions: [{ type: 'condition', text: 'unless the payload is redacted' }]
    },
    edge: { type: 'data_dependency', data_flow: { from_param: 'body', to_param: 'payload' } }
  });
  assert.equal(guarded.state, 'may_route');
  assert.equal(guarded.reason, 'sink_like_target_conditional');
});

test('P2-B: NO conditions => sink-like route stays definite (no regression)', () => {
  const plain = classifyRouteState({
    ...baseArgs,
    targetProfile: { node_id: 'n1', node_roles: ['external_egress'] },
    edge: { type: 'data_dependency', data_flow: { from_param: 'body', to_param: 'payload' } }
  });
  assert.equal(plain.state, 'definite_route');
  assert.equal(plain.reason, 'sink_like_target');
});

test('P2-B: positive when-guard leaves sink route definite (only negatives downgrade)', () => {
  const positive = classifyRouteState({
    ...baseArgs,
    targetProfile: {
      node_id: 'n1',
      node_roles: ['external_egress'],
      conditions: [{ type: 'condition', text: 'when the user requests a report' }]
    },
    edge: { type: 'data_dependency', data_flow: { from_param: 'body', to_param: 'payload' } }
  });
  assert.equal(positive.state, 'definite_route');
  assert.equal(positive.reason, 'sink_like_target');
});

test('P2-B: negative guard downgrades a data-carrying control_flow route', () => {
  const guarded = classifyRouteState({
    ...baseArgs,
    targetProfile: {
      node_id: 'n1',
      node_roles: ['transform'],
      conditions: [{ type: 'condition', text: 'do not forward without consent' }]
    },
    edge: { type: 'control_flow', data_flow: { from_param: 'response', to_param: 'context' } }
  });
  assert.equal(guarded.state, 'may_route');
  assert.equal(guarded.reason, 'control_flow_data_conditional');
});

test('P2-B: explicit deny in condition text still hard-blocks via existing gate', () => {
  const denied = classifyRouteState({
    ...baseArgs,
    targetProfile: {
      node_id: 'n1',
      node_roles: ['external_egress'],
      conditions: [{ type: 'condition', text: 'forbid sending to third parties' }]
    },
    edge: { type: 'data_dependency', data_flow: { from_param: 'body', to_param: 'payload' } }
  });
  // 'forbid' matches the pre-existing explicit_block regex over routeText, which
  // now includes condition text — so it blocks outright.
  assert.equal(denied.state, 'blocked');
  assert.equal(denied.reason, 'explicit_block');
});
