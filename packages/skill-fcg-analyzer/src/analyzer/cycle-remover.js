/**
 * Cycle Remover
 * Detects cycles in the FCG and selects a weakest breaking edge per cycle.
 *
 * Two-stage design (so plausibility can decide WHICH cycles physically break):
 *   1. detectAndTagCycles(graph) — DFS-detect cycles, select the weakest edge of
 *      each, and TAG it (is_feedback_edge / feedback_cycle_path). Does NOT touch
 *      adjacencyList. Runs BEFORE feedback-edge plausibility classification.
 *   2. breakOnlyFake(graph) — remove from adjacencyList only the feedback edges
 *      classified implausible (fake cycles). Real cycles (plausible) stay in
 *      adjacencyList so the transfer layer can expand them one lap. Runs AFTER
 *      classification.
 *
 * The breaking edge is NEVER deleted from graph.edges (method A in
 * .claude/plans/self-loop-cycle-representation-plan.md); only its adjacencyList
 * entry is removed, and only for fake cycles.
 *
 * Consumers that rebuild adjacency from `graph.edges` (node-splitter) or derive
 * propagation/role structure from edges (transfer-analysis) filter feedback edges
 * via `isFeedbackEdge` — narrowed to implausible-only where real cycles must
 * survive (see transfer-analysis activeEdges / node-splitter).
 */

/**
 * Stage 1: detect cycles and TAG the weakest breakable edge of each. Does not
 * mutate adjacencyList — physical breaking is deferred to breakOnlyFake so the
 * plausibility classifier (which runs between the two) can decide which cycles
 * actually break.
 * @param {Object} graph - FunctionCallGraph instance
 * @returns {Object} Same graph; weakest cycle edges tagged is_feedback_edge=true.
 */
function detectAndTagCycles(graph) {
  const visited = new Set();
  const recStack = new Set();
  const cycles = [];

  /**
   * DFS to detect cycles
   * @param {string} nodeId - Current node ID
   * @param {Array} path - Current path
   */
  function dfs(nodeId, path) {
    visited.add(nodeId);
    recStack.add(nodeId);

    const neighbors = graph.adjacencyList.get(nodeId) || [];
    for (const neighborId of neighbors) {
      if (!visited.has(neighborId)) {
        dfs(neighborId, [...path, neighborId]);
      } else if (recStack.has(neighborId)) {
        // Cycle detected
        const cycleStart = path.indexOf(neighborId);
        cycles.push({
          start: neighborId,
          path: path.slice(cycleStart)
        });
      }
    }

    recStack.delete(nodeId);
  }

  // Traverse all nodes
  for (const nodeId of graph.nodes.keys()) {
    if (!visited.has(nodeId)) {
      dfs(nodeId, [nodeId]);
    }
  }

  // Select the weakest edge of each cycle and TAG it (do not break adjacency).
  // `cut` tracks already-selected edges so a later cycle re-selecting them
  // behaves exactly as the old delete-based pass: once selected an edge is
  // invisible to subsequent cycle resolution, yet stays in graph.edges. The
  // selection order and result are byte-identical to the former removeCycles;
  // only the adjacencyList mutation is deferred to breakOnlyFake.
  const cut = new Set();
  for (const cycle of cycles) {
    const cycleEdges = graph.edges.filter(e =>
      !cut.has(e) &&
      cycle.path.includes(e.source) &&
      cycle.path.includes(e.target)
    );

    if (cycleEdges.length === 0) continue;

    // Keep semantic/document feedback loops when no safe edge can be removed.
    // This preserves doc-flow directionality (e.g. llm -> doc.write/run).
    const removableEdges = cycleEdges.filter(edge => !isProtectedCycleEdge(edge));
    if (removableEdges.length === 0) {
      continue;
    }

    const weakestEdge = removableEdges.reduce((min, edge) =>
      compareEdgeRemovalPriority(edge, min) < 0 ? edge : min
    );

    cut.add(weakestEdge);
    weakestEdge.is_feedback_edge = true;
    weakestEdge.feedback_removed_reason = 'cycle_break';
    weakestEdge.feedback_cycle_path = cycle.path.slice();
  }

  return graph;
}

/**
 * Stage 2: physically break ONLY fake cycles. Removes from adjacencyList the
 * feedback edges whose plausibility classification is NOT 'plausible'
 * (implausible = fake cycle, or unclassified as a defensive fallback). Real
 * (plausible) cycles are left in adjacencyList so the transfer layer expands
 * them one lap.
 *
 * For the implausible set this is byte-identical to the former removeCycles
 * adjacency mutation: same edges, same per-source filter.
 * @param {Object} graph - FunctionCallGraph instance (post-classification)
 * @returns {Object} Graph whose adjacencyList has fake cycles removed; real
 *   cycles retained.
 */
function breakOnlyFake(graph) {
  for (const edge of graph.edges) {
    if (!isFeedbackEdge(edge)) continue;
    // Real cycle: keep it in adjacencyList so the transfer layer can traverse
    // it (guarded to exactly one re-entry by flow-instance-router).
    if (edge.feedback_plausibility === 'plausible') continue;

    const neighbors = graph.adjacencyList.get(edge.source) || [];
    graph.adjacencyList.set(
      edge.source,
      neighbors.filter(t => t !== edge.target)
    );
  }
  return graph;
}

/**
 * Back-compat wrapper: detect + tag + break everything (the pre-split legacy
 * behavior, breaking all cycles regardless of plausibility). Retained so callers
 * that break cycles WITHOUT a plausibility pass still get an acyclic graph.
 * @param {Object} graph - FunctionCallGraph instance
 * @returns {Object} Graph whose adjacencyList is acyclic; feedback edges retained.
 */
function removeCycles(graph) {
  detectAndTagCycles(graph);
  for (const edge of graph.edges) {
    if (!isFeedbackEdge(edge)) continue;
    const neighbors = graph.adjacencyList.get(edge.source) || [];
    graph.adjacencyList.set(
      edge.source,
      neighbors.filter(t => t !== edge.target)
    );
  }
  return graph;
}

/**
 * True if an edge was tagged as a cycle-breaking feedback edge. Consumers that
 * rebuild adjacency or propagation structure from edges must exclude these.
 * @param {Object} edge
 * @returns {boolean}
 */
function isFeedbackEdge(edge) {
  return Boolean(edge && edge.is_feedback_edge);
}

function isProtectedCycleEdge(edge) {
  if (!edge) return false;
  if (edge.type === 'doc_instruction') return true;
  if (edge.validation_method === 'doc_flow') return true;
  if (edge.validation_method === 'semantic_rule') return true;
  if (edge.validation_method === 'callsite_mediation') return true;
  // Prohibitive-ordering constraint edges encode a required security invariant
  // (e.g. "vet before install"); never drop one to break a cycle.
  if (edge.validation_method === 'doc_flow_constraint') return true;
  return false;
}

function compareEdgeRemovalPriority(a, b) {
  const confidenceA = Number.isFinite(a?.confidence) ? a.confidence : 0.5;
  const confidenceB = Number.isFinite(b?.confidence) ? b.confidence : 0.5;
  if (confidenceA !== confidenceB) return confidenceA - confidenceB;

  const typeScoreA = edgeTypeRemovalScore(a?.type);
  const typeScoreB = edgeTypeRemovalScore(b?.type);
  if (typeScoreA !== typeScoreB) return typeScoreA - typeScoreB;

  const sourceA = String(a?.source || '');
  const sourceB = String(b?.source || '');
  if (sourceA !== sourceB) return sourceA.localeCompare(sourceB);

  return String(a?.target || '').localeCompare(String(b?.target || ''));
}

function edgeTypeRemovalScore(type) {
  switch (type) {
    case 'data_dependency':
      return 1;
    case 'control_flow':
      return 2;
    case 'semantic':
      return 3;
    case 'doc_instruction':
      return 4;
    default:
      return 5;
  }
}

module.exports = {
  detectAndTagCycles,
  breakOnlyFake,
  removeCycles,
  isFeedbackEdge,
  isProtectedCycleEdge
};
