const test = require('node:test');
const assert = require('node:assert/strict');

const { FunctionCallGraph } = require('../src/analyzer/fcg-builder');
const { removeCycles, isFeedbackEdge } = require('../src/analyzer/cycle-remover');
const { splitGraphNodes } = require('../src/analyzer/node-splitter');
const { extractAllPaths } = require('../src/analyzer/path-extractor');

// Minimal self-optimizing feedback loop: a skill that writes learnings to a file
// and later reads them back to refine itself (write -> read -> write on the same
// store). This is the core semantics method A must preserve instead of silently
// deleting, as documented in
// .claude/plans/self-loop-cycle-representation-plan.md (section 2.6).
function feedbackLoopGraph() {
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'node_w', name: 'doc.write.learnings' });
  graph.addNode({ id: 'node_r', name: 'doc.read.learnings' });

  // write -> read (control flow: later periodic review reads what was written)
  graph.addEdge({
    source: 'node_w',
    target: 'node_r',
    type: 'control_flow',
    confidence: 0.7,
    validation_method: 'doc_flow'
  });
  // read -> write (data dependency: refined learnings flow back into the file)
  graph.addEdge({
    source: 'node_r',
    target: 'node_w',
    type: 'data_dependency',
    confidence: 0.6,
    validation_method: 'dependency_rule'
  });
  return graph;
}

test('removeCycles tags the weakest cycle edge as feedback instead of deleting it', () => {
  const graph = removeCycles(feedbackLoopGraph());

  // Both edges are retained in graph.edges (nothing deleted).
  assert.equal(graph.edges.length, 2);

  const feedback = graph.edges.filter(isFeedbackEdge);
  assert.equal(feedback.length, 1, 'exactly one edge broken to acyclicate the loop');

  const fb = feedback[0];
  // The data_dependency edge (conf 0.6) is weaker than the protected doc_flow
  // control edge, so it is the one demoted.
  assert.equal(fb.source, 'node_r');
  assert.equal(fb.target, 'node_w');
  assert.equal(fb.is_feedback_edge, true);
  assert.equal(fb.feedback_removed_reason, 'cycle_break');
  assert.ok(Array.isArray(fb.feedback_cycle_path) && fb.feedback_cycle_path.length > 0);
});

test('removeCycles drops the feedback edge from adjacencyList so traversal is a DAG', () => {
  const graph = removeCycles(feedbackLoopGraph());

  // node_r no longer points back to node_w in the traversal view.
  assert.deepEqual(graph.adjacencyList.get('node_r'), []);
  // The forward edge survives in adjacency.
  assert.deepEqual(graph.adjacencyList.get('node_w'), ['node_r']);
});

test('splitGraphNodes does not resurrect the broken cycle when rebuilding adjacency', () => {
  const graph = splitGraphNodes(removeCycles(feedbackLoopGraph()));

  // The feedback edge is still present in edges (retained for output)...
  assert.equal(graph.edges.filter(isFeedbackEdge).length, 1);
  // ...but must NOT be back in adjacencyList (that is how the cycle would return).
  for (const [source, targets] of graph.adjacencyList.entries()) {
    for (const target of targets) {
      const revives = graph.edges.some(e =>
        isFeedbackEdge(e) && e.source === source && e.target === target
      );
      assert.ok(!revives, `feedback edge ${source}->${target} leaked into adjacencyList`);
    }
  }
});

test('path extraction terminates and enumerates only acyclic paths after feedback tagging', () => {
  const graph = splitGraphNodes(removeCycles(feedbackLoopGraph()));
  const paths = extractAllPaths(graph, {
    maxAllPathsTotal: 100,
    maxNeighborPaths: 5,
    maxPathLength: 12,
    maxStateExpansionsPerSearch: 500
  });

  // Only the forward write->read path remains; no path revisits a node.
  for (const p of paths) {
    assert.equal(new Set(p.nodes).size, p.nodes.length, `path ${p.path_id} revisits a node`);
  }
  assert.ok(paths.some(p => p.nodes.join('->') === 'node_w->node_r'));
});

test('feedback tagging is idempotent when an edge is selected across multiple cycles', () => {
  // Two overlapping cycles sharing the same weakest edge must tag it once and not
  // corrupt the deterministic selection.
  const graph = new FunctionCallGraph();
  graph.addNode({ id: 'a', name: 'a' });
  graph.addNode({ id: 'b', name: 'b' });
  graph.addNode({ id: 'c', name: 'c' });
  // a->b->a and a->b->c->a share edge b->? ; keep it simple: a<->b plus b->c->a.
  graph.addEdge({ source: 'a', target: 'b', type: 'control_flow', confidence: 0.9, validation_method: 'doc_flow' });
  graph.addEdge({ source: 'b', target: 'a', type: 'data_dependency', confidence: 0.3, validation_method: 'dependency_rule' });
  graph.addEdge({ source: 'b', target: 'c', type: 'control_flow', confidence: 0.9, validation_method: 'doc_flow' });
  graph.addEdge({ source: 'c', target: 'a', type: 'data_dependency', confidence: 0.4, validation_method: 'dependency_rule' });

  const result = removeCycles(graph);
  // Nothing deleted.
  assert.equal(result.edges.length, 4);
  // adjacencyList must be acyclic: no node reaches itself.
  for (const start of result.nodes.keys()) {
    const seen = new Set();
    const stack = [start];
    let revisitedStart = false;
    while (stack.length) {
      const cur = stack.pop();
      for (const nb of result.adjacencyList.get(cur) || []) {
        if (nb === start) { revisitedStart = true; break; }
        if (!seen.has(nb)) { seen.add(nb); stack.push(nb); }
      }
      if (revisitedStart) break;
    }
    assert.ok(!revisitedStart, `node ${start} still reaches itself (cycle remains)`);
  }
});
