const assert = require('node:assert/strict');
const { test } = require('node:test');

const {
  budgetPackIfNeeded,
  estimatePackChars,
  losslessReduce
} = require('../src/evidence-budget');

// Build a flow-centric pack with `nodeCount` flow nodes (index 0 = source, last
// = sink). Interior node action text is `nodeTextChars` long to drive size.
function buildPack({ unitId = 'u1', nodeCount = 3, nodeTextChars = 0 } = {}) {
  const flow = [];
  for (let i = 0; i < nodeCount; i += 1) {
    const role = i === 0 ? 'source' : (i === nodeCount - 1 ? 'sink' : 'transform');
    flow.push({
      node_name: `node${i}`,
      role,
      action: nodeTextChars ? `read: ${'X'.repeat(nodeTextChars)}` : `read: step ${i}`
    });
  }
  const pack = {
    unit_id: unitId,
    observation_id: 'obs1',
    label_flow_id: 'lf1',
    question: 'judge necessity',
    label: { category: 'pii', subtype: 'email', sensitivity: 'high' },
    sink_boundary: { node_name: `node${nodeCount - 1}`, trust_boundary: 'external_network' },
    flow,
    task_memory_evidence_ids: ['task.memory.identity']
  };
  return pack;
}

test('Tier-0: a pack within the ceiling is returned byte-identical', () => {
  const pack = buildPack({ nodeCount: 5, nodeTextChars: 50 });
  const before = JSON.stringify(pack);
  const out = budgetPackIfNeeded(pack, {}); // default 100k ceiling
  assert.equal(JSON.stringify(out), before, 'small pack must be untouched');
  assert.equal(out._budgeted, undefined, 'no budgeting metadata on a Tier-0 pack');
});

test('Tier-2: an oversized pack is reduced under the ceiling', () => {
  const pack = buildPack({ nodeCount: 30, nodeTextChars: 5000 });
  const before = estimatePackChars(pack);
  const out = budgetPackIfNeeded(pack, { evidenceMaxPackChars: 40000, evidencePathNodeWindow: 3 });
  const after = estimatePackChars(out);
  assert.ok(before > 40000, 'precondition: pack starts oversized');
  assert.ok(after < before, 'pack must shrink');
  assert.equal(out._budgeted, true, 'budgeted flag set');
  assert.ok(Array.isArray(out._budget_notes) && out._budget_notes.length > 0, 'budget notes recorded');
});

test('Tier-2: source and sink endpoints are always retained verbatim', () => {
  const pack = buildPack({ nodeCount: 30, nodeTextChars: 5000 });
  const out = budgetPackIfNeeded(pack, { evidenceMaxPackChars: 40000, evidencePathNodeWindow: 3 });
  const source = out.flow[0];
  const sink = out.flow[out.flow.length - 1];
  assert.equal(source.role, 'source');
  assert.equal(sink.role, 'sink');
  assert.ok(!source.summarized, 'source node not summarized');
  assert.ok(!sink.summarized, 'sink node not summarized');
});

test('Tier-2: a budget note describes the reduction', () => {
  const pack = buildPack({ nodeCount: 30, nodeTextChars: 5000 });
  const out = budgetPackIfNeeded(pack, { evidenceMaxPackChars: 40000, evidencePathNodeWindow: 3 });
  assert.ok(out.budget_note, 'budget_note present');
  assert.equal(out.budget_note.budgeted, true);
  assert.ok(out.budget_note.original_chars > out.budget_note.budgeted_chars, 'note records the size reduction');
});

test('losslessReduce collapses whitespace without dropping content', () => {
  const pack = buildPack({ nodeCount: 1 });
  pack.flow[0].action = 'send    the\n\n\n\nemail   now';
  const out = losslessReduce(pack);
  const text = out.flow[0].action;
  assert.ok(!/\n{3,}/.test(text), 'no 3+ newline runs');
  assert.ok(!/ {2,}/.test(text), 'no 2+ space runs');
  assert.ok(/send/.test(text) && /email/.test(text) && /now/.test(text), 'words preserved');
});

test('default ceiling (100k) leaves a moderately large pack mostly intact', () => {
  const pack = buildPack({ nodeCount: 30, nodeTextChars: 1000 }); // ~31k
  const before = JSON.stringify(pack);
  const out = budgetPackIfNeeded(pack, {});
  assert.equal(JSON.stringify(out), before, 'a ~31k pack stays untouched at the 100k default');
});

test('hard ceiling guarantee: a huge pack ends up under the ceiling, endpoints kept', () => {
  // 400 nodes x 4000 chars — far over the ceiling.
  const pack = buildPack({ nodeCount: 400, nodeTextChars: 4000 });
  const ceiling = 100000;
  const out = budgetPackIfNeeded(pack, { evidenceMaxPackChars: ceiling });
  assert.equal(out._budgeted, true);
  assert.ok(estimatePackChars(out) <= ceiling, `final pack ${estimatePackChars(out)} must be <= ${ceiling}`);
  // Endpoints survive.
  assert.equal(out.flow[0].role, 'source');
  assert.equal(out.flow[out.flow.length - 1].role, 'sink');
  // label + sink_boundary are never dropped.
  assert.ok(out.label && out.label.category === 'pii');
  assert.ok(out.sink_boundary && out.sink_boundary.trust_boundary === 'external_network');
});

test('hard ceiling keeps surviving flow nodes citable by node_name (no separate index)', () => {
  const pack = buildPack({ nodeCount: 400, nodeTextChars: 4000 });
  const out = budgetPackIfNeeded(pack, { evidenceMaxPackChars: 60000 });
  // No redundant evidence[] index is (re)built — the surviving flow nodes are the
  // citable handles. Every retained node still carries a node_name to cite.
  assert.equal(out.evidence, undefined);
  assert.ok(out.flow.length > 0);
  assert.ok(out.flow.every(n => typeof n.node_name === 'string' && n.node_name.length > 0));
});
