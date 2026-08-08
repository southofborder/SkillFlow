const test = require('node:test');
const assert = require('node:assert/strict');

const { analyzeGraphTransfers } = require('../src/security/graph-transfer-analyzer');
const {
  detectAndTagCycles,
  breakOnlyFake,
  removeCycles
} = require('../src/analyzer/cycle-remover');

// --- Graph builders --------------------------------------------------------
// A minimal FunctionCallGraph-shaped object (nodes Map, edges array,
// adjacencyList Map) for the cycle-remover, which reads/mutates adjacencyList.
function makeGraph(nodeIds, edges) {
  const nodes = new Map(nodeIds.map(id => [id, { id }]));
  const adjacencyList = new Map(nodeIds.map(id => [id, []]));
  for (const edge of edges) {
    adjacencyList.get(edge.source).push(edge.target);
  }
  return { nodes, edges, adjacencyList };
}

function adjacencyOf(graph) {
  const out = {};
  for (const [k, v] of graph.adjacencyList.entries()) out[k] = [...v].sort();
  return out;
}

// --- Profiles --------------------------------------------------------------
function sourceProfile(id = 'src', label = {}) {
  return {
    node_id: id,
    node_name: `read.${id}`,
    node_roles: ['data_introduction'],
    security_tags: ['file_read'],
    data_surface: 'local_file',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process',
    data_profile: {
      labels: [{
        label: 'pii.email',
        category: 'pii',
        subtype: 'email',
        sensitivity: 'high',
        origin_node: id,
        introduced_at: id,
        confidence: 0.95,
        ...label
      }]
    }
  };
}

function sinkProfile(id, roles = ['external_egress']) {
  return {
    node_id: id,
    node_name: `sink.${id}`,
    node_roles: roles,
    security_tags: ['webhook_post'],
    data_surface: 'network',
    receiver_scope: 'third_party_service',
    retention_scope: 'external',
    trust_boundary: 'external_network',
    formal_semantics: { operation_type: 'invoke_tool' }
  };
}

function passThroughProfile(id) {
  return {
    node_id: id,
    node_name: `step.${id}`,
    node_roles: ['transform'],
    data_surface: 'local_file',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process'
  };
}

const LIMITS = { maxLabelFlows: 200, maxEvents: 2000, maxDepth: 12, maxBranchesPerNode: 20 };

// =========================================================================
// 1. cycle-remover split: breakOnlyFake removes implausible, keeps plausible;
//    the implausible-only path is byte-identical to legacy removeCycles.
// =========================================================================
test('breakOnlyFake keeps plausible cycles in adjacency, removes implausible', () => {
  // Cycle a -> b -> a; the b->a edge is the weakest (data_dependency, low conf).
  const edges = [
    { source: 'a', target: 'b', type: 'control_flow', confidence: 0.9 },
    { source: 'b', target: 'a', type: 'data_dependency', confidence: 0.3 }
  ];

  // Plausible: real cycle survives in adjacency.
  const gPlausible = makeGraph(['a', 'b'], edges.map(e => ({ ...e })));
  detectAndTagCycles(gPlausible);
  const feedbackEdge = gPlausible.edges.find(e => e.is_feedback_edge);
  assert.ok(feedbackEdge, 'a feedback edge is tagged');
  feedbackEdge.feedback_plausibility = 'plausible';
  breakOnlyFake(gPlausible);
  assert.deepEqual(adjacencyOf(gPlausible), { a: ['b'], b: ['a'] }, 'real cycle retained');

  // Implausible: broken exactly like legacy removeCycles.
  const gImplausible = makeGraph(['a', 'b'], edges.map(e => ({ ...e })));
  detectAndTagCycles(gImplausible);
  gImplausible.edges.find(e => e.is_feedback_edge).feedback_plausibility = 'implausible';
  breakOnlyFake(gImplausible);

  const gLegacy = makeGraph(['a', 'b'], edges.map(e => ({ ...e })));
  removeCycles(gLegacy);

  assert.deepEqual(
    adjacencyOf(gImplausible),
    adjacencyOf(gLegacy),
    'fake-cycle adjacency is byte-identical to legacy removeCycles'
  );
});

// =========================================================================
// 2. Real-cycle periodic leak: an in-cycle sink observed on the expanded lap
//    carries leak_type='periodic'.
// =========================================================================
test('in-cycle sink observed on the real-cycle lap is marked periodic', () => {
  // src -> A(sink, in cycle) -> B -> A  (B->A is the plausible feedback edge)
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible',
        feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  const periodic = transfer.observation_events.filter(e => e.leak_type === 'periodic');
  assert.ok(periodic.length >= 1, 'at least one periodic observation on in-cycle sink A');
  assert.ok(periodic.every(e => e.node_id === 'A'), 'periodic observations are on the in-cycle sink');
  assert.equal(transfer.statistics.periodic_leak_count, periodic.length);
});

// =========================================================================
// 3. Closure absorption: the feedback edge is NOT traversed (no flow copies
//    circle the loop). Its route is blocked as cycle_absorbed_into_closure, the
//    cycle is folded into the label closure, and the flow set stays bounded.
// =========================================================================
test('real cycle is absorbed into the closure, feedback edge never traversed', () => {
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible',
        feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  // Converged on its own (no cap).
  assert.equal(transfer.truncated, false, 'converged without hitting any limit');
  // The feedback edge is blocked into the closure — never admitted as a lap.
  const absorbed = transfer.route_events.filter(e => e.reason === 'cycle_absorbed_into_closure');
  assert.ok(absorbed.length >= 1, 'feedback edge blocked as cycle_absorbed_into_closure');
  assert.equal(
    transfer.route_events.filter(e => e.state !== 'blocked' && e.edge_id === 'e_B_A').length,
    0,
    'the feedback edge is never traversed (no circling copy)'
  );
  // No flow circled the loop: no flow's node_path contains A twice.
  const circled = transfer.label_flows.filter(f => (f.node_path || []).filter(n => n === 'A').length > 1);
  assert.equal(circled.length, 0, 'no flow copy circled back through the cycle');
  // The closure was computed for this cycle.
  assert.ok(transfer.statistics.cycle_closure_count >= 1, 'a cycle closure was computed');
});

// =========================================================================
// 3b. A summarize (pass-through) cycle contributes ZERO extra flows: the closure
//     is a single member (T(L)≡L), so the flow set is byte-identical in COUNT to
//     the same graph with the feedback edge removed entirely.
// =========================================================================
test('pass-through cycle closure adds zero extra flows vs the acyclic graph', () => {
  const build = (withFeedback) => analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      ...(withFeedback ? [{
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }] : [])
    ],
    // All pass-through (no derive/summarize label change) => T(L) === L.
    nodeProfiles: [sourceProfile('src'), passThroughProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  const withCycle = build(true);
  const acyclic = build(false);
  assert.equal(
    withCycle.statistics.label_flow_count,
    acyclic.statistics.label_flow_count,
    'pass-through cycle adds no extra label flows (closure is a single member)'
  );
});

// =========================================================================
// 7. Closure convergence backstop: maxClosureIterations bounds a pathological
//    operator that never reaches a fixpoint, truncation-logging the cap instead
//    of looping forever. A normal cycle converges far under the cap.
// =========================================================================
test('maxClosureIterations bounds a non-converging closure and truncation-logs it', () => {
  // A tiny cycle whose closure converges immediately; a very low cap of 1 still
  // lets it finish (it converges in <=1 lap). We assert it never runs away and the
  // cap is available as an env-overridable ceiling.
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B')],
    limits: { ...LIMITS, maxClosureIterations: 1 }
  });

  // A pass-through/summarize closure converges within one lap, so even a cap of 1
  // does not truncate.
  assert.equal(
    transfer.truncation_events.filter(e => e.reason === 'cycle_closure_not_converged').length,
    0,
    'a converging closure is not truncated even at a low cap'
  );
  assert.ok(transfer.statistics.cycle_closure_count >= 1);
});

// =========================================================================
// 8. Default limits: a single small cycle computes its closure once and produces a
//    periodic observation for its in-cycle sink, without truncation.
// =========================================================================
test('default limits compute one closure and a periodic leak for a small cycle', () => {
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  assert.ok(transfer.statistics.cycle_closure_count >= 1, 'closure computed');
  assert.ok(transfer.observation_events.some(e => e.leak_type === 'periodic'), 'in-cycle sink is periodic');
  assert.equal(transfer.truncation_events.filter(e => e.reason === 'cycle_closure_not_converged').length, 0);
});

// =========================================================================
// 4. Collapse: a flow that passes through the cycle body then exits to an
//    external sink OUTSIDE the cycle is tagged cycle_handling='collapse'
//    (and that outside sink is NOT periodic).
// =========================================================================
test('flow exiting the cycle to an outside sink is tagged collapse, not periodic', () => {
  // src -> A -> B -> A (feedback)  and  B -> C(sink outside cycle)
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }, { id: 'C' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible',
        feedback_cycle_path: ['A', 'B']
      },
      { id: 'e_B_C', source: 'B', target: 'C', type: 'data_dependency', confidence: 1 }
    ],
    nodeProfiles: [
      sourceProfile('src'),
      passThroughProfile('A'),
      passThroughProfile('B'),
      sinkProfile('C')
    ],
    limits: LIMITS
  });

  const collapsed = transfer.label_flows.filter(f => f.cycle_handling === 'collapse');
  assert.ok(collapsed.length >= 1, 'at least one collapsed through-flow reaching C');
  assert.ok(collapsed.every(f => f.current_node === 'C'), 'collapse flows land on the outside sink');
  assert.equal(transfer.statistics.collapsed_flow_count, collapsed.length);

  // C is outside the cycle, so its observation must NOT be periodic.
  const cObs = transfer.observation_events.filter(e => e.node_id === 'C');
  assert.ok(cObs.length >= 1, 'C is observed');
  assert.ok(cObs.every(e => e.leak_type !== 'periodic'), 'outside sink is not periodic');
});

// =========================================================================
// 5. Severity sub-classification: a high-sensitivity in-cycle leak is
//    amplifying (decision 4 — severity escalation).
// =========================================================================
test('periodic severity classifies high-sensitivity in-cycle leak as amplifying', () => {
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible',
        feedback_cycle_path: ['A', 'B']
      }
    ],
    // sensitivity: 'high' on the label -> amplifying.
    nodeProfiles: [sourceProfile('src', { sensitivity: 'high' }), sinkProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  const periodic = transfer.observation_events.filter(e => e.leak_type === 'periodic');
  assert.ok(periodic.length >= 1);
  assert.ok(periodic.some(e => e.leak_severity === 'amplifying'), 'high-sensitivity leak is amplifying');
  assert.equal(transfer.statistics.periodic_leak_severity.amplifying >= 1, true);
});

// =========================================================================
// 9. Fake cycle is inert in the transfer layer: an implausible feedback edge is
//    stripped by the caller, so no periodic/collapse arises and the observation
//    set matches an ordinary acyclic run.
// =========================================================================
test('implausible feedback edge is not re-entered (no periodic when fake cycle stripped)', () => {
  // The caller (transfer-analysis.transferEdges) strips an implausible feedback
  // edge before this point; simulate that by NOT passing it.
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 }
      // B->A implausible feedback edge stripped by the caller.
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });

  assert.equal(transfer.statistics.periodic_leak_count, 0, 'no periodic leaks without a real cycle');
  assert.equal(transfer.statistics.collapsed_flow_count, 0, 'no collapse without a real cycle');
  assert.equal(transfer.statistics.cycle_closure_count, 0, 'no closure computed on the acyclic graph');
  assert.ok(
    transfer.observation_events.every(e => !e.leak_type),
    'all observations are plain (no leak_type) on the acyclic graph'
  );
});

// =========================================================================
// 10. Defaults: local flooding no longer imposes wall-clock/size ceilings.
//     A long acyclic chain far past the former maxDepth (12) must still reach
//     its sink under DEFAULT limits — proving the size gate was lifted, not just
//     raised for one test. Guarantees "correct but slow" analysis finishes.
// =========================================================================
test('default limits do not truncate a long acyclic chain past the old maxDepth', () => {
  // Chain src -> n1 -> ... -> n30 -> sink: 31 hops, well past the former 12.
  const CHAIN = 30;
  const nodes = [{ id: 'src' }];
  const edges = [];
  const profiles = [sourceProfile('src')];
  let prev = 'src';
  for (let i = 1; i <= CHAIN; i++) {
    const id = `n${i}`;
    nodes.push({ id });
    profiles.push(passThroughProfile(id));
    edges.push({ id: `e_${prev}_${id}`, source: prev, target: id, type: 'data_dependency', confidence: 1 });
    prev = id;
  }
  nodes.push({ id: 'sink' });
  profiles.push(sinkProfile('sink'));
  edges.push({ id: `e_${prev}_sink`, source: prev, target: 'sink', type: 'data_dependency', confidence: 1 });

  // NO limits passed at all -> DEFAULT_LIMITS (maxDepth 1000, others no-limit).
  const transfer = analyzeGraphTransfers({ nodes, edges, nodeProfiles: profiles });

  assert.equal(transfer.truncated, false, 'the long chain converged without truncation');
  assert.equal(
    transfer.truncation_events.filter(e => e.reason === 'max_depth').length,
    0,
    'no max_depth truncation on a 31-hop chain (old default 12 would have blocked it)'
  );
  assert.ok(
    transfer.observation_events.some(e => e.node_id === 'sink'),
    'the label reached the far sink past the old depth ceiling'
  );
});

// =========================================================================
// 11. cycleExpand default flipped ON. The top-level analyzer must default to
//     the cycle-expansion pipeline; FCG_CYCLE_EXPAND=0 (or option false) opts
//     out. This is the anchor that guards the default from silent regression.
// =========================================================================
test('SkillFCGAnalyzer defaults cycleExpand ON and honors explicit opt-out', () => {
  const { SkillFCGAnalyzer } = require('../src/index');
  const prev = process.env.FCG_CYCLE_EXPAND;
  try {
    delete process.env.FCG_CYCLE_EXPAND;
    assert.equal(new SkillFCGAnalyzer({}).cycleExpand, true, 'default (env unset) is ON');

    process.env.FCG_CYCLE_EXPAND = '0';
    assert.equal(new SkillFCGAnalyzer({}).cycleExpand, false, 'FCG_CYCLE_EXPAND=0 opts out');
    process.env.FCG_CYCLE_EXPAND = 'off';
    assert.equal(new SkillFCGAnalyzer({}).cycleExpand, false, 'FCG_CYCLE_EXPAND=off opts out');

    delete process.env.FCG_CYCLE_EXPAND;
    assert.equal(new SkillFCGAnalyzer({ cycleExpand: false }).cycleExpand, false, 'option false overrides default');
    assert.equal(new SkillFCGAnalyzer({ cycleExpand: true }).cycleExpand, true, 'option true is honored');
  } finally {
    if (prev === undefined) delete process.env.FCG_CYCLE_EXPAND;
    else process.env.FCG_CYCLE_EXPAND = prev;
  }
});

// --- Builders for closure (deriving) cycles --------------------------------
// A user_prompt source (the only category deriveSemanticLabels will derive from).
function userPromptSource(id = 'src') {
  return {
    node_id: id,
    node_name: `read.${id}`,
    node_roles: ['data_introduction'],
    security_tags: ['user_input'],
    data_surface: 'user',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process',
    data_profile: {
      labels: [{
        label: 'user_prompt.text',
        category: 'user_prompt',
        subtype: 'text',
        sensitivity: 'low',
        origin_node: id,
        introduced_at: id,
        confidence: 0.95
      }]
    }
  };
}

// A cycle node that DERIVES a new label from a user_prompt input (semantic
// extraction). Evidence text drives classifyTextLabels to the given category.
function deriveProfile(id, evidenceText = 'extract the email address') {
  return {
    node_id: id,
    node_name: `derive.${id}`,
    node_roles: ['transform'],
    operation_tags: ['semantic_extraction'],
    data_surface: 'local_file',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process',
    evidence: [{ kind: 'doc', text: evidenceText }]
  };
}

// A cycle node that SUMMARIZES its input. createSummaryLabel mints an
// 'aggregate_data' summary that — like every synthetic label — carries
// mode==='derived'. It is a GENERALIZING product (a broader abstraction, a subset of
// the input), so it must NOT be injected as a specializing out-of-cycle flow. This is
// the exact shape that a naive `mode==='derived'` check misclassifies; N7 guards it.
function summarizeProfile(id, evidenceText = 'summarize the results into a digest') {
  return {
    node_id: id,
    node_name: `summarize.${id}`,
    node_roles: ['transform'],
    operation_tags: ['summarization'],
    data_surface: 'local_file',
    receiver_scope: 'local_runtime',
    retention_scope: 'transient',
    trust_boundary: 'local_process',
    evidence: [{ kind: 'doc', text: evidenceText }]
  };
}

// =========================================================================
// N1. A summarize/pass-through cycle contributes NO derived closure member:
//     the closure is a single seed member, so the observation set (minus the
//     periodic marker) equals the acyclic run.
// =========================================================================
test('N1: pass-through (summarize) cycle closure is a single member', () => {
  const withCycle = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), passThroughProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });
  const acyclic = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 }
    ],
    nodeProfiles: [sourceProfile('src'), passThroughProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });
  // Same flow count: the closure added no member.
  assert.equal(withCycle.statistics.label_flow_count, acyclic.statistics.label_flow_count);
  // The only label carried is the seed's — no derived member appeared.
  const labels = new Set(withCycle.label_flows.map(f => f.label?.label));
  assert.deepEqual([...labels].sort(), [...new Set(acyclic.label_flows.map(f => f.label?.label))].sort());
});

// =========================================================================
// N2. A DERIVING cycle whose derive point is reachable ONLY once the feedback
//     edge closes the loop: the forward flood never produces the derived class,
//     so the cycle MUST carry it OUT as a specializing closure member. Flow count
//     and the labels reaching OUT are therefore STRICTLY GREATER with the cycle.
//
//     Graph: src(user_prompt) -> A(pass) -> OUT, plus a cycle A <-> B where the
//     A->B edge IS the feedback edge (blocked, never traversed forward) and B
//     DERIVES pii.email. Forward flood: src->A->OUT only — B is never visited, so
//     acyclic OUT sees only user_prompt. With the cycle, the closure at A includes
//     B's derived pii.email, which leaves via A->OUT as its own flow.
// =========================================================================
test('N2: deriving cycle reachable only via feedback carries the derived class OUT (specializing member)', () => {
  const build = (withFeedback) => analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }, { id: 'OUT' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_OUT', source: 'A', target: 'OUT', type: 'data_dependency', confidence: 1 },
      { id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 1 },
      // A -> B is the feedback edge: blocked by the router, so B is NEVER reached by
      // the forward flood. B only enters the picture through the closure computation.
      ...(withFeedback ? [{
        id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }] : [])
    ],
    nodeProfiles: [
      userPromptSource('src'),
      passThroughProfile('A'),
      deriveProfile('B', 'extract the email address'),
      passThroughProfile('OUT')
    ],
    limits: LIMITS
  });

  const withCycle = build(true);
  const acyclic = build(false);

  // A closure was computed for the cycle.
  assert.ok(withCycle.statistics.cycle_closure_count >= 1);
  // The specializing member (B's extracted pii.email) adds flow(s) the flood never made.
  assert.ok(
    withCycle.statistics.label_flow_count > acyclic.statistics.label_flow_count,
    'the deriving cycle carries the feedback-only derived class OUT as an extra flow'
  );
  const outLabels = (t) => new Set(
    t.label_flows.filter(f => f.current_node === 'OUT').map(f => f.label?.label)
  );
  const withOut = outLabels(withCycle);
  const acyclicOut = outLabels(acyclic);
  // acyclic OUT never sees the derived class; the cycle introduces it.
  assert.ok(![...acyclicOut].some(l => /email/i.test(l || '')), 'acyclic OUT has no derived pii.email');
  assert.ok([...withOut].some(l => /email/i.test(l || '')), 'the cycle carries derived pii.email to OUT');
});

// =========================================================================
// N2b. Dedup backstop: when the derive point is ALSO reachable by the forward
//     flood, the specializing closure member collides on buildFlowStateKey with the
//     flood-produced flow and is dropped — zero double count. Flow count is
//     identical with and without the feedback edge.
//
//     Graph: src -> A(derive pii.email) -> B -> A(feedback), and A -> OUT. A is on
//     the forward path (src->A), so pii.email reaches OUT via the flood already;
//     the cycle's specializing member for the same class at A collides and is absorbed.
// =========================================================================
test('N2b: specializing member colliding with the forward flood is deduped — zero extra flow', () => {
  const build = (withFeedback) => analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }, { id: 'OUT' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      ...(withFeedback ? [{
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }] : []),
      { id: 'e_A_OUT', source: 'A', target: 'OUT', type: 'data_dependency', confidence: 1 }
    ],
    nodeProfiles: [
      userPromptSource('src'),
      deriveProfile('A', 'extract the email address'),
      passThroughProfile('B'),
      passThroughProfile('OUT')
    ],
    limits: LIMITS
  });

  const withCycle = build(true);
  const acyclic = build(false);

  assert.ok(withCycle.statistics.cycle_closure_count >= 1);
  // Same flow count: the specializing member collides with the flood-produced flow.
  assert.equal(
    withCycle.statistics.label_flow_count,
    acyclic.statistics.label_flow_count,
    'the specializing member is deduped against the forward flood (no double count)'
  );
  const outLabels = (t) => new Set(
    t.label_flows.filter(f => f.current_node === 'OUT').map(f => f.label?.label)
  );
  assert.deepEqual(
    [...outLabels(withCycle)].sort(),
    [...outLabels(acyclic)].sort(),
    'the labels reaching OUT are identical — the flood already carried the derived class'
  );
});

// =========================================================================
// N3. Double pass-through cycle converges without duplicating the seed member.
// =========================================================================
test('N3: two-node pass-through cycle converges to a single member', () => {
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [sourceProfile('src'), passThroughProfile('A'), passThroughProfile('B')],
    limits: LIMITS
  });
  assert.equal(transfer.truncated, false, 'converges');
  // No flow carries a duplicated node in its path (no circling).
  assert.ok(transfer.label_flows.every(f => new Set(f.node_path).size === (f.node_path || []).length));
});

// =========================================================================
// N4. A deriving cycle whose in-cycle node is ALSO a sink: exactly one periodic
//     observation on that sink, severity reflecting the highest closure member.
// =========================================================================
test('N4: in-cycle sink on a deriving cycle emits one periodic with escalated severity', () => {
  // src(user_prompt) -> A(derive pii.email, sink) -> B -> A (feedback)
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [
      userPromptSource('src'),
      // A both derives (semantic_extraction) and is an egress sink.
      {
        ...deriveProfile('A', 'extract the email address'),
        node_roles: ['transform', 'external_egress'],
        security_tags: ['webhook_post'],
        data_surface: 'network',
        receiver_scope: 'third_party_service',
        retention_scope: 'external',
        trust_boundary: 'external_network',
        formal_semantics: { operation_type: 'invoke_tool' }
      },
      passThroughProfile('B')
    ],
    limits: LIMITS
  });

  const periodic = transfer.observation_events.filter(e => e.leak_type === 'periodic');
  assert.ok(periodic.length >= 1, 'the in-cycle sink is periodic');
  assert.ok(periodic.every(e => e.node_id === 'A'), 'periodic is on the in-cycle sink A');
  // One periodic per (cycle, sink, seed) — not one per closure member.
  assert.equal(periodic.length, 1, 'exactly one periodic observation for the whole cycle sink');
});

// =========================================================================
// N5. Convergence backstop: a very low maxClosureIterations still terminates and
//     never runs away, even on a deriving cycle.
// =========================================================================
test('N5: maxClosureIterations bounds the closure computation (bounded termination)', () => {
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }
    ],
    nodeProfiles: [userPromptSource('src'), deriveProfile('A'), passThroughProfile('B')],
    limits: { ...LIMITS, maxClosureIterations: 1 }
  });
  // It terminates (no runaway) regardless of the cap value.
  assert.ok(transfer.statistics.label_flow_count > 0, 'analysis terminated with a bounded flow set');
  assert.ok(transfer.statistics.cycle_closure_count >= 1);
});

// =========================================================================
// N6. Shared node with TWO plausible feedback edges: both cycles' closures union
//     into the seed set (the node sits on two cycles).
// =========================================================================
test('N6: a node on two feedback cycles unions both closures', () => {
  // src -> A ; A on two self-cycles via B and C:
  //   A -> B -> A (feedback e_B_A)  and  A -> C -> A (feedback e_C_A)
  const transfer = analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }, { id: 'C' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_C', source: 'A', target: 'C', type: 'data_dependency', confidence: 1 },
      {
        id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      },
      {
        id: 'e_C_A', source: 'C', target: 'A', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'C']
      }
    ],
    nodeProfiles: [sourceProfile('src'), sinkProfile('A'), passThroughProfile('B'), passThroughProfile('C')],
    limits: LIMITS
  });

  // Both feedback edges are absorbed into the closure (neither traversed).
  assert.equal(
    transfer.route_events.filter(e => e.state !== 'blocked' && (e.edge_id === 'e_B_A' || e.edge_id === 'e_C_A')).length,
    0,
    'neither feedback edge is traversed'
  );
  assert.ok(transfer.truncated === false, 'converges with two overlapping cycles');
  // A is on both cycles -> periodic observed on A.
  assert.ok(
    transfer.observation_events.some(e => e.node_id === 'A' && e.leak_type === 'periodic'),
    'the shared in-cycle sink is periodic'
  );
});

// =========================================================================
// N7. A GENERALIZING closure member (summarize -> 'aggregate_data', which — like
//     every synthetic label — carries mode==='derived') must NOT be injected as an
//     out-of-cycle flow. It is a subset of the seed; the seed's own out-flow already
//     covers it. Mirror of N2, but the feedback-only cycle node SUMMARIZES instead
//     of DERIVES, so the flow count with the feedback edge equals the acyclic run
//     (zero inflation). Regression guard: a naive `mode==='derived'` specializing check
//     misclassifies 'aggregate_data' and inflates the count here.
// =========================================================================
test('N7: generalizing (summarize -> aggregate_data, mode=derived) closure member is NOT injected out of cycle', () => {
  const build = (withFeedback) => analyzeGraphTransfers({
    nodes: [{ id: 'src' }, { id: 'A' }, { id: 'B' }, { id: 'OUT' }],
    edges: [
      { id: 'e_src_A', source: 'src', target: 'A', type: 'data_dependency', confidence: 1 },
      { id: 'e_A_OUT', source: 'A', target: 'OUT', type: 'data_dependency', confidence: 1 },
      { id: 'e_B_A', source: 'B', target: 'A', type: 'data_dependency', confidence: 1 },
      // A -> B feedback edge: blocked by the router, B only enters via the closure.
      ...(withFeedback ? [{
        id: 'e_A_B', source: 'A', target: 'B', type: 'data_dependency', confidence: 0.3,
        is_feedback_edge: true, feedback_plausibility: 'plausible', feedback_cycle_path: ['A', 'B']
      }] : [])
    ],
    nodeProfiles: [
      userPromptSource('src'),
      passThroughProfile('A'),
      summarizeProfile('B'),
      passThroughProfile('OUT')
    ],
    limits: LIMITS
  });

  const withCycle = build(true);
  const acyclic = build(false);

  // The closure IS computed (B summarizes on the feedback-only lap) ...
  assert.ok(withCycle.statistics.cycle_closure_count >= 1, 'a closure is computed for the summarize cycle');
  // ... but the generalizing 'aggregate_data' member is NOT forked out: zero inflation.
  assert.equal(
    withCycle.statistics.label_flow_count,
    acyclic.statistics.label_flow_count,
    'the summarize (aggregate_data) member is a subset of the seed and is not injected as an extra flow'
  );
  // OUT never gains an aggregate_data label from the cycle.
  const outCats = (t) => new Set(
    t.label_flows.filter(f => f.current_node === 'OUT').map(f => f.label?.category)
  );
  assert.ok(![...outCats(withCycle)].includes('aggregate_data'), 'no aggregate_data leaks OUT via the cycle');
});


