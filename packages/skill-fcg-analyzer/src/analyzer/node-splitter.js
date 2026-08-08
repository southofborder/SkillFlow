/**
 * Node splitter — enforces the single-crossing invariant deterministically.
 *
 * Invariant: a graph node crosses at most ONE data boundary. A "crossing" is an
 * ordered action step whose node_roles intersect SINK_LIKE_ROLES (egress /
 * model_inference / persistence / command / destructive / tool_invocation).
 * read/transform steps are not crossings and may accompany the one crossing.
 *
 * WHY split here (post-edge): the expensive O(n^2) dependency pairing
 * (analyzeTypeCompatibility) runs on `tools` BEFORE the graph exists. By the
 * time this pass runs (after buildFCG/removeCycles), edges are already resolved
 * to node ids. Splitting a node into a chain of children lets the children
 * INHERIT the parent's edges (incoming->first, outgoing->last, chained between)
 * instead of re-running any pairing. Node internals were already established by
 * the LLM to not cross with other nodes' internals, so no re-pairing is needed.
 *
 * WHY the profiler reproduces the split: node-level roles derive from whole-node
 * text (nodeSecurityText), but action_steps are the authoritative per-crossing
 * decomposition and observations fire per step. Each child carries ONLY its
 * segment's steps as member_steps, so buildActionPlan's member_steps path yields
 * exactly that segment -> the child re-profiles to a single crossing.
 */

const { buildNodeProfile } = require('../security/node-profiler');
const { isFeedbackEdge } = require('./cycle-remover');

const SINK_LIKE_ROLES = new Set([
  'external_egress',
  'model_inference',
  'local_persistence',
  'command_execution',
  'destructive_operation',
  'tool_invocation'
]);

function stepIsCrossing(step = {}) {
  return (step.node_roles || []).some(role => SINK_LIKE_ROLES.has(role));
}

// Synthetic builtin nodes (user.query, the global llm.inference, and per-call-site
// llm mediation wrappers) are atomic by construction — one operation each. They
// must NOT be split: their `description`/`name` deliberately reference the tool
// they wrap ("Post-tool LLM mediation for webhook.post"), which would otherwise
// pollute the profile with a spurious second crossing (external_egress from the
// word "webhook"/"post"). This mirrors the semantic_reason role-pollution guard:
// a node's role must come from what it does, not from text describing neighbours.
function isAtomicBuiltin(node = {}) {
  return node.type === 'builtin_call';
}

// Ordered action steps for a node, using the profiler as the single source of
// truth (no duplicated heuristics). Steps are already sorted by `order`.
function orderedActionSteps(node = {}) {
  const profile = buildNodeProfile(node, {});
  return Array.isArray(profile.action_steps) ? profile.action_steps : [];
}

// Partition ordered steps into segments, each ending at a crossing step.
// A trailing run of non-crossing steps (no crossing after it) attaches to the
// last segment rather than forming a bare crossing-less node.
function segmentSteps(steps = []) {
  const segments = [];
  let current = [];
  for (const step of steps) {
    current.push(step);
    if (stepIsCrossing(step)) {
      segments.push(current);
      current = [];
    }
  }
  if (current.length) {
    if (segments.length) segments[segments.length - 1].push(...current);
    else segments.push(current);
  }
  return segments;
}

// Convert an action step back into a member_step shape that buildMemberActionSteps
// consumes, so the child re-profiles to this exact step.
function stepToMemberStep(step = {}, index = 0) {
  const evidenceText = (step.evidence && step.evidence[0] && step.evidence[0].text) || step.operation_type || '';
  return {
    instruction: evidenceText,
    text: evidenceText,
    operation_type: step.operation_type || 'transform',
    docAction: step.operation_type || '',
    line: Number.isFinite(Number(step.order)) ? Number(step.order) : index + 1,
    formal_semantics: {
      operation_type: step.operation_type || 'transform',
      targets: Array.isArray(step.targets) ? step.targets : [],
      confidence: step.confidence
    }
  };
}

// Build a child node for one segment. Carries only this segment's steps as
// member_steps and narrows instructionText to the segment evidence, so both the
// member_steps profiling path and nodeSecurityText are scoped to this crossing.
function buildChildNode(parent = {}, segment = [], segmentIndex = 0) {
  const crossing = segment.find(stepIsCrossing) || segment[segment.length - 1] || {};
  const order = Number.isFinite(Number(crossing.order)) ? Number(crossing.order) : segmentIndex + 1;
  const op = crossing.operation_type || 'transform';
  const childId = `${parent.id}::s${String(order).padStart(3, '0')}::${op}`;
  const memberSteps = segment.map((step, i) => stepToMemberStep(step, i));
  const instructionText = segment
    .map(step => (step.evidence && step.evidence[0] && step.evidence[0].text) || step.operation_type || '')
    .filter(Boolean)
    .join(' ');

  return {
    ...parent,
    id: childId,
    name: `${parent.name || parent.id}#s${order}`,
    canonical_name: parent.canonical_name || parent.name || parent.id,
    // Scope profiling inputs to this segment only.
    member_steps: memberSteps,
    member_step_count: memberSteps.length,
    instructionText: instructionText || parent.instructionText || '',
    docActions: [op],
    docAction: op,
    operationType: op,
    formal_semantics: {
      ...(parent.formal_semantics || {}),
      operation_type: op
    },
    // Provenance back to the parent for tracing/debugging.
    split_from: parent.id,
    split_segment_index: segmentIndex
  };
}

// Internal edge chaining consecutive children of one split node. Tagged so the
// evidence-pack link logic (edgeCarriesData) treats it as a real intra-node data
// dependency (data_flow), not an order_only hop.
function internalChainEdge(sourceId, targetId, seq) {
  return {
    id: `split_edge_${sourceId}__${targetId}`,
    source: sourceId,
    target: targetId,
    type: 'data_dependency',
    confidence: 1.0,
    validation_method: 'node_split_sequential',
    data_flow: {
      from_param: 'segment_output',
      to_param: 'segment_input',
      data_type: 'object'
    },
    semantic_reason: `Intra-node data flow between split segments ${seq} of ${sourceId.split('::')[0]}`
  };
}

/**
 * Split every graph node that crosses >1 boundary into a chain of single-crossing
 * children. Returns a NEW graph-like object { nodes: Map, edges: [], adjacencyList }.
 *
 * Edge rewiring per split parent P -> children C0..Cn:
 *   - edges into P    -> retargeted to C0 (first child)
 *   - edges out of P  -> resourced from Cn (last child)
 *   - Ci -> Ci+1      -> internal node_split_sequential data_dependency edges
 * Self-loops on P (rare) map to Cn -> C0.
 */
function splitGraphNodes(graph) {
  const originalNodes = Array.from(graph.nodes.values());
  const childrenByParent = new Map(); // parentId -> [childId...]
  const newNodes = new Map();
  const internalEdges = [];

  for (const node of originalNodes) {
    if (isAtomicBuiltin(node)) {
      newNodes.set(node.id, node);
      continue;
    }

    const steps = orderedActionSteps(node);
    const crossingCount = steps.filter(stepIsCrossing).length;

    if (crossingCount <= 1) {
      newNodes.set(node.id, node);
      continue;
    }

    const segments = segmentSteps(steps);
    if (segments.length <= 1) {
      // Defensive: crossings collapsed into one segment; keep node intact.
      newNodes.set(node.id, node);
      continue;
    }

    const childIds = [];
    let prevChildId = null;
    segments.forEach((segment, segmentIndex) => {
      const child = buildChildNode(node, segment, segmentIndex);
      newNodes.set(child.id, child);
      childIds.push(child.id);
      if (prevChildId) internalEdges.push(internalChainEdge(prevChildId, child.id, segmentIndex));
      prevChildId = child.id;
    });
    childrenByParent.set(node.id, childIds);
  }

  const firstChild = id => (childrenByParent.get(id) || [id])[0];
  const lastChild = id => {
    const kids = childrenByParent.get(id);
    return kids ? kids[kids.length - 1] : id;
  };

  const rewiredEdges = [];
  for (const edge of graph.edges) {
    const srcSplit = childrenByParent.has(edge.source);
    const dstSplit = childrenByParent.has(edge.target);
    if (edge.source === edge.target && srcSplit) {
      // Self-loop on a split node: connect tail back to head.
      rewiredEdges.push({ ...edge, source: lastChild(edge.source), target: firstChild(edge.target) });
      continue;
    }
    rewiredEdges.push({
      ...edge,
      source: srcSplit ? lastChild(edge.source) : edge.source,
      target: dstSplit ? firstChild(edge.target) : edge.target
    });
  }

  const allEdges = [...rewiredEdges, ...internalEdges];

  // Feedback edges (cycle-breakers tagged by removeCycles) stay in graph.edges
  // but must NOT re-enter adjacencyList, or the cycle they broke returns here
  // when this pass rebuilds adjacency from scratch.
  const adjacencyList = new Map();
  for (const nodeId of newNodes.keys()) adjacencyList.set(nodeId, []);
  for (const edge of allEdges) {
    if (isFeedbackEdge(edge)) continue;
    if (!adjacencyList.has(edge.source)) adjacencyList.set(edge.source, []);
    adjacencyList.get(edge.source).push(edge.target);
  }

  graph.nodes = newNodes;
  graph.edges = allEdges;
  graph.adjacencyList = adjacencyList;
  return graph;
}

/**
 * Assert the single-crossing invariant on node profiles. Returns array of
 * violation descriptors (empty when clean) rather than throwing, so the caller
 * can warn consistently with existing validation warnings.
 */
function findCrossingViolations(nodeProfiles = [], nodesById = new Map()) {
  const violations = [];
  for (const profile of nodeProfiles || []) {
    // Atomic builtins (user.query / llm.inference / mediation) are exempt: they
    // are single-operation by construction and their text intentionally names
    // wrapped tools, so a >1 crossing here is pollution, not a real violation.
    const node = nodesById.get(profile.node_id);
    if (node && isAtomicBuiltin(node)) continue;
    const steps = Array.isArray(profile.action_steps) ? profile.action_steps : [];
    const crossings = steps.filter(stepIsCrossing);
    if (crossings.length > 1) {
      violations.push({
        node_id: profile.node_id,
        node_name: profile.node_name,
        crossing_count: crossings.length,
        crossing_ops: crossings.map(step => step.operation_type)
      });
    }
  }
  return violations;
}

module.exports = {
  splitGraphNodes,
  findCrossingViolations,
  segmentSteps,
  stepIsCrossing,
  orderedActionSteps,
  SINK_LIKE_ROLES
};
