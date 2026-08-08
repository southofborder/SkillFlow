const test = require('node:test');
const assert = require('node:assert/strict');

const { FunctionCallGraph } = require('../src/analyzer/fcg-builder');
const {
  splitGraphNodes,
  findCrossingViolations,
  segmentSteps,
  stepIsCrossing
} = require('../src/analyzer/node-splitter');
const { buildNodeProfile } = require('../src/security/node-profiler');

// A node whose text implies two boundary crossings: post to an external webhook
// AND write the result to a local file. The profiler should yield >=2 crossing
// action steps, so the splitter must break it into a chain of single-crossing
// children.
function twoSinkNode() {
  return {
    id: 'node_002',
    name: 'doc.step.export',
    instructionText: 'Read the report, then send it to the external webhook API, and finally write the report to a local file.',
    docActions: ['read', 'external_egress', 'write'],
    formal_semantics: { operation_type: 'read' }
  };
}

test('twoSinkNode profiles to more than one crossing step (precondition)', () => {
  const profile = buildNodeProfile(twoSinkNode(), {});
  const crossings = (profile.action_steps || []).filter(stepIsCrossing);
  assert.ok(crossings.length >= 2, `expected >=2 crossings, got ${crossings.length}`);
});

test('segmentSteps: each segment ends at a crossing; trailing tail attaches', () => {
  const steps = [
    { order: 1, operation_type: 'read', node_roles: ['data_introduction'] },
    { order: 2, operation_type: 'external_egress', node_roles: ['external_egress', 'tool_invocation'] },
    { order: 3, operation_type: 'transform', node_roles: ['transform'] },
    { order: 4, operation_type: 'write', node_roles: ['local_persistence'] },
    { order: 5, operation_type: 'transform', node_roles: ['transform'] }
  ];
  const segments = segmentSteps(steps);
  assert.equal(segments.length, 2);
  // seg0: read + egress (ends at crossing)
  assert.deepEqual(segments[0].map(s => s.operation_type), ['read', 'external_egress']);
  // seg1: transform + write + trailing transform (tail attaches to last segment)
  assert.deepEqual(segments[1].map(s => s.operation_type), ['transform', 'write', 'transform']);
});

test('segmentSteps: no crossing => single segment', () => {
  const segments = segmentSteps([
    { order: 1, operation_type: 'read', node_roles: ['data_introduction'] },
    { order: 2, operation_type: 'transform', node_roles: ['transform'] }
  ]);
  assert.equal(segments.length, 1);
});

test('splitGraphNodes: two-sink node becomes chained single-crossing children', () => {
  const graph = new FunctionCallGraph();
  const src = { id: 'node_001', name: 'source' };
  const mid = twoSinkNode();
  const dst = { id: 'node_003', name: 'downstream' };
  graph.addNode(src);
  graph.addNode(mid);
  graph.addNode(dst);
  graph.addEdge({ id: 'e1', source: 'node_001', target: 'node_002', type: 'data_dependency' });
  graph.addEdge({ id: 'e2', source: 'node_002', target: 'node_003', type: 'data_dependency' });

  splitGraphNodes(graph);

  // Original composite node is gone; replaced by >=2 children.
  assert.equal(graph.nodes.has('node_002'), false);
  const children = Array.from(graph.nodes.keys()).filter(id => id.startsWith('node_002::'));
  assert.ok(children.length >= 2, `expected >=2 children, got ${children.length}`);

  // Each child re-profiles to <=1 crossing.
  for (const childId of children) {
    const profile = buildNodeProfile(graph.nodes.get(childId), {});
    const crossings = (profile.action_steps || []).filter(stepIsCrossing);
    assert.ok(crossings.length <= 1, `child ${childId} has ${crossings.length} crossings`);
  }

  // Incoming edge retargeted to first child; outgoing resourced from last child.
  const incoming = graph.edges.find(e => e.id === 'e1');
  const outgoing = graph.edges.find(e => e.id === 'e2');
  assert.equal(incoming.target, children[0]);
  assert.equal(outgoing.source, children[children.length - 1]);

  // Internal chain edges exist and are tagged node_split_sequential.
  const chain = graph.edges.filter(e => e.validation_method === 'node_split_sequential');
  assert.equal(chain.length, children.length - 1);
  assert.equal(chain[0].source, children[0]);
  assert.equal(chain[0].target, children[1]);
});

test('splitGraphNodes: single-crossing node is left untouched', () => {
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'node_001', name: 'source' });
  graph.addNode({
    id: 'node_002',
    name: 'just.egress',
    instructionText: 'Send the payload to the external webhook API.',
    docActions: ['external_egress'],
    formal_semantics: { operation_type: 'external_egress' }
  });
  graph.addEdge({ id: 'e1', source: 'node_001', target: 'node_002', type: 'data_dependency' });

  splitGraphNodes(graph);
  assert.ok(graph.nodes.has('node_002'), 'single-crossing node must not be split');
  assert.equal(graph.edges.find(e => e.id === 'e1').target, 'node_002');
});

test('findCrossingViolations: flags profiles with >1 crossing, clean otherwise', () => {
  const dirty = buildNodeProfile(twoSinkNode(), {});
  assert.ok(findCrossingViolations([dirty]).length >= 1);

  const clean = buildNodeProfile({
    id: 'n', name: 'x', instructionText: 'Read a file.', docActions: ['read'],
    formal_semantics: { operation_type: 'read' }
  }, {});
  assert.equal(findCrossingViolations([clean]).length, 0);
});
