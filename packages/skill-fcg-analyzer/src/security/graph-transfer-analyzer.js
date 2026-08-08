const { shortHash } = require('./data-labeler');
const { classifyRouteState, SINK_LIKE_ROLES } = require('./flow-instance-router');
const {
  applyLabelFlowFilter,
  compactLabels,
  dedupeLabels,
  mergeTriggerContextInto
} = require('./flow-instance-filter');

// Local flooding is a DETERMINISTIC, guaranteed-to-converge computation — it is
// NOT a remote call that can hang. So its size gates are not "safety timeouts";
// they are optional result-size ceilings. By default we let the flood enumerate
// every path instance to its natural fixpoint (no truncation), and keep each gate
// only as an env-overridable escape hatch for the rare operator who wants to cap a
// pathological graph. A gate at MAX_SAFE_INTEGER is effectively "no limit": the
// slice()/counter checks against it never fire on any real graph, so the run ends
// only when the queue drains (true convergence), exactly as with no gate at all.
//
// NOTE the two classes below:
//   * Convergence/size gates (raised to effectively-infinite): maxLabelFlows,
//     maxInstances, maxEvents, maxBranchesPerNode. maxDepth is raised to 1000
//     rather than infinity because it doubles as a pathological-chain backstop —
//     see flow-instance-router; 1000 hops is unreachable on real skills yet still
//     guarantees termination against an unbounded chain.
//   * Output-shape gates (UNCHANGED): maxMergeParents/maxRelatedFlows/
//     maxMergeGroupsPerFlow bound how many ids a single flow RECORD lists. They
//     shape the emitted JSON, not convergence or wall-time, so they stay put.
const NO_LIMIT = Number.MAX_SAFE_INTEGER;

const DEFAULT_LIMITS = {
  maxLabelFlows: NO_LIMIT,
  maxInstances: NO_LIMIT,
  maxEvents: NO_LIMIT,
  maxDepth: 1000,
  maxBranchesPerNode: NO_LIMIT,
  maxMergeParents: 8,
  maxRelatedFlows: 128,
  maxMergeGroupsPerFlow: 64,
  // Cycle-closure convergence backstop. A real cycle is folded into a label
  // FIXPOINT CLOSURE (computeCycleClosure): the cycle body is applied as a
  // transform operator until the label set stops growing. Convergence is
  // guaranteed because every derived label's introduced_at binds to a node id
  // over the fixed cycle node set (finite key space), so this cap is never hit on
  // a real graph. It exists only to bound a pathological operator that mints a
  // fresh label every lap; beyond it the closure is returned as-is and truncation-
  // logged (never silent). Env-overridable via FCG_SECURITY_MAX_CLOSURE_ITERATIONS.
  maxClosureIterations: 16
};

const LIMIT_ENV_KEYS = {
  maxLabelFlows: 'FCG_SECURITY_MAX_LABEL_FLOWS',
  maxInstances: 'FCG_SECURITY_MAX_INSTANCES',
  maxEvents: 'FCG_SECURITY_MAX_EVENTS',
  maxDepth: 'FCG_SECURITY_MAX_DEPTH',
  maxBranchesPerNode: 'FCG_SECURITY_MAX_BRANCHES_PER_NODE',
  maxMergeParents: 'FCG_SECURITY_MAX_MERGE_PARENTS',
  maxRelatedFlows: 'FCG_SECURITY_MAX_RELATED_FLOWS',
  maxMergeGroupsPerFlow: 'FCG_SECURITY_MAX_MERGE_GROUPS_PER_FLOW',
  maxClosureIterations: 'FCG_SECURITY_MAX_CLOSURE_ITERATIONS'
};

function analyzeGraphTransfers({ nodes = [], edges = [], nodeProfiles = [], limits = {} }) {
  const options = normalizeLimits(limits);
  const nodesById = new Map((nodes || []).map(node => [node.id, node]));
  const profilesByNode = new Map((nodeProfiles || []).map(profile => [profile.node_id, profile]));
  const outgoing = groupEdges(edges, 'source');
  const state = createState(options);

  for (const profile of nodeProfiles || []) {
    if (!profile.node_roles?.includes('data_introduction')) continue;
    if (shouldSkipInitialSourceIntroduction(profile, edges)) continue;
    const labels = compactLabels(profile.data_profile?.labels || []);
    for (const label of labels) {
      const initial = createInitialLabelFlow(profile, label, state);
      if (registerLabelFlow(initial, state, { enqueue: true })) {
        recordSinkObservationsForArrivedLabelFlow(initial, profile, state);
      }
    }
  }

  while (true) {
    while (state.queue.length > 0) {
      const labelFlow = state.queue.shift();
      if (state.allEvents.length >= options.maxEvents || (
        options._explicitMaxLabelFlows && state.labelFlows.length >= options.maxLabelFlows
      )) {
        markTruncated(labelFlow, state, state.allEvents.length >= options.maxEvents ? 'max_events' : 'max_label_flows_or_events');
        continue;
      }

      maybeCreateMergeRelationships(labelFlow, state, profilesByNode);
      expandLabelFlow(labelFlow, {
        state,
        options,
        outgoing,
        profilesByNode,
        nodesById
      });
    }

    if (!processPendingStorageReads(state)) break;
  }

  return {
    label_flows: state.labelFlows,
    flow_states: buildFlowStates(state),
    provenance_store: buildProvenanceStore(state),
    node_flow_sets: buildNodeFlowSets(state.labelFlows),
    label_flows_by_node: state.labelFlowsByNode,
    transitions: state.transitions,
    route_events: state.routeEvents,
    filter_events: state.filterEvents,
    merge_events: state.mergeEvents,
    observation_events: state.observationEvents,
    source_introductions: state.sourceIntroductions,
    truncation_events: state.truncationEvents,
    truncated: state.truncated,
    statistics: buildStatistics(state, options)
  };
}

function expandLabelFlow(labelFlow, context) {
  const { state, options, outgoing, profilesByNode, nodesById } = context;
  if (labelFlow.terminated) return;

  const currentProfile = profilesByNode.get(labelFlow.current_node);
  if (!currentProfile) {
    terminateLabelFlow(labelFlow, 'missing_current_profile');
    return;
  }

  applyActionStepsAtNode(labelFlow, currentProfile, state);

  const edgesOut = outgoing.get(labelFlow.current_node) || [];
  if (edgesOut.length === 0) {
    terminateLabelFlow(labelFlow, 'no_outgoing_edges');
    return;
  }

  const prioritizedEdges = prioritizeEdgesForObservationCoverage(edgesOut, profilesByNode);
  const limitedEdges = prioritizedEdges.slice(0, options.maxBranchesPerNode);
  if (edgesOut.length > limitedEdges.length) {
    markTruncated(labelFlow, state, 'max_branches_per_node');
  }

  // A plausible feedback edge out of the current node means the current node sits
  // ON a real cycle. Collect that cycle's node set so children forking from here
  // (down ANY out-edge, incl. the one leaving the cycle) know they passed through
  // the cycle body — this drives collapse tagging for flows that exit to an
  // outside sink. Union with any cycle the flow was already traversing.
  const feedbackCyclePaths = limitedEdges
    .filter(edge => edge.is_feedback_edge && edge.feedback_plausibility === 'plausible' && Array.isArray(edge.feedback_cycle_path))
    .map(edge => edge.feedback_cycle_path);
  const cycleNodesHere = uniqueValues([
    ...(labelFlow._cycle_nodes || []),
    ...feedbackCyclePaths.flat()
  ]);

  // Real cycle at this node. Every node in the cycle body is an INTERMEDIATE node
  // for GENERALIZING transforms (summarize/aggregate/redact/slice): the loop lets the
  // seed circulate through more transform points but mints no label class the acyclic
  // flood wouldn't already produce, so the flow leaving the cycle carries only its
  // seed (zero extra flows). But a SPECIALIZING transform on the cycle (semantic
  // extract / pseudonymize) DOES resolve a concrete new label class out of the seed;
  // if that extract point is reachable ONLY once the feedback edge closes the loop,
  // the forward flood never produced it, so the cycle must carry those extracted
  // classes OUT — reusing the ordinary derive multi-flow semantics (one broad input
  // label → several specific extracted flows). We therefore let the cycle contribute
  // both OBSERVATIONS and, for specializing members only, extra out-of-cycle flows:
  //   - periodic: an in-cycle sink re-emits its data class every loop iteration;
  //   - severity: how the seed is transformed as it circulates (steady / mutating /
  //     amplifying) — needs the fixpoint of the cycle transform on the seed;
  //   - specializing out-flows: closure members the cycle EXTRACTED (concrete new
  //     class) leave via the out-edges as their own flows, deduped against the flood
  //     by buildFlowStateKey.
  // The fixpoint closure grades severity, drives periodic, AND supplies the
  // specializing members. The feedback edge itself is blocked by the router (never
  // traversed).
  //
  // The closure depends ONLY on (this node, the seed label class, the cycle
  // structure) — NOT on which flow arrived. Thousands of flows can reach the same
  // cycle node with the same label class, so we MEMOIZE by (node, seed key): the
  // heavy fixpoint iteration runs once per distinct (node, label class), not once
  // per flow. Without this the run is O(flows × cycle-length × filter) and blows up.
  let specializingMembers = [];
  if (feedbackCyclePaths.length > 0) {
    const cacheKey = `${labelFlow.current_node}|${closureLabelKey(labelFlow.label)}`;
    let cached = state.closureCache.get(cacheKey);
    if (!cached) {
      const closure = computeCycleClosure({
        seedLabel: labelFlow.label,
        feedbackCyclePaths,
        profilesByNode,
        nodesById,
        maxIterations: options.maxClosureIterations
      });
      cached = closure;
      state.closureCache.set(cacheKey, closure);
      state.cycleClosureCount += 1;
    }
    if (cached.truncated) markTruncated(labelFlow, state, 'cycle_closure_not_converged');
    // One periodic observation per (in-cycle sink, seed label class) — NOT per flow.
    // Periodic is a property of the cycle+data, not of each individual flow copy, so
    // deduping by label class (inside recordCyclePeriodicObservations) keeps the
    // observation set bounded even when many flows pass the same cycle sink. The
    // closure labels grade severity only; they never fork the flow.
    recordCyclePeriodicObservations({ labelFlow, feedbackCyclePaths, severityLabels: cached.labels, profilesByNode, state });
    // Specializing members (concrete new classes the cycle EXTRACTED) that must leave
    // the cycle as their own flows. Generalizing members (summary/aggregate) and the
    // seed itself are excluded — the seed's own out-edge filter already carries them.
    specializingMembers = (cached.labels || []).filter(member => isSpecializingClosureMember(member, labelFlow.label));
  }

  let propagated = 0;
  for (const edge of limitedEdges) {
    const targetProfile = profilesByNode.get(edge.target);
    if (!targetProfile) continue;

    const route = classifyRouteState({
      instance: labelFlow,
      currentProfile,
      targetProfile,
      edge,
      maxDepth: options.maxDepth
    });
    const routeEvent = buildRouteEvent({ labelFlow, route, currentProfile, targetProfile, edge, state });
    state.routeEvents.push(routeEvent);
    state.allEvents.push(routeEvent);

    if (route.state === 'blocked') continue;

    // The node transform applied to the flow's OWN seed label — the ordinary,
    // always-present out-flow. For a generalizing cycle (or no cycle) this is the
    // only thing emitted, byte-identical to the acyclic case.
    propagated += emitFlowsForLabelAtEdge({
      sourceFlow: labelFlow,
      currentProfile,
      edge,
      route,
      routeEvent,
      targetProfile,
      cycleNodesHere,
      nodesById,
      state
    });

    // Specializing cycle members (concrete new classes the cycle EXTRACTED): each
    // leaves via this out-edge as its own flow, reusing the ordinary derive multi-flow
    // path. Empty for generalizing / acyclic cases → zero extra flows. Each is a
    // shallow clone of the seed flow with its label swapped, so node_path / parent
    // chain / dedup key are all correct; buildFlowStateKey dedups any member the
    // forward flood already produced at this node (collision → dropped, no double
    // count).
    for (const member of specializingMembers) {
      propagated += emitFlowsForLabelAtEdge({
        sourceFlow: { ...labelFlow, label: member },
        currentProfile,
        edge,
        route,
        routeEvent,
        targetProfile,
        cycleNodesHere,
        nodesById,
        state
      });
    }
  }

  if (propagated === 0 && !labelFlow.terminated && !labelFlow.truncated) {
    terminateLabelFlow(labelFlow, 'no_viable_route');
  }
}

// Run one node transform (applyLabelFlowFilter) for `sourceFlow`'s label across a
// single out-edge and register every resulting branch as a child flow. Returns the
// number of children actually registered (dedup misses don't count). Shared by the
// seed out-flow and each specializing cycle member so both walk the identical
// filter → branch → createChildLabelFlow → registerLabelFlow pipeline.
function emitFlowsForLabelAtEdge({ sourceFlow, currentProfile, edge, route, routeEvent, targetProfile, cycleNodesHere, nodesById, state }) {
  const filter = applyLabelFlowFilter({
    labelFlow: sourceFlow,
    currentProfile: propagationProfile(currentProfile),
    currentNode: nodesById.get(sourceFlow.current_node),
    edge,
    targetProfile
  });
  const filterEvents = materializeFilterEvents(filter.filter_events, state, sourceFlow, edge);
  state.filterEvents.push(...filterEvents);
  state.allEvents.push(...filterEvents);
  state.sourceIntroductions.push(...filterEvents.filter(event => event.type === 'source_introduction'));

  if (!filter.branches.length) return 0;

  let emitted = 0;
  for (const branch of filter.branches) {
    const branchEvents = filterEvents.filter(event => (branch.filter_event_keys || []).includes(event.local_event_key));
    const child = createChildLabelFlow({
      parent: sourceFlow,
      targetProfile,
      edge,
      route,
      routeEvent,
      cycleNodesHere,
      branch,
      filterEvents: branchEvents.length ? branchEvents : filterEvents,
      state
    });
    if (registerLabelFlow(child, state, { enqueue: true })) {
      recordSinkObservationsForArrivedLabelFlow(child, targetProfile, state);
      state.transitions.push(buildTransition(sourceFlow, child, edge, routeEvent, branchEvents.length ? branchEvents : filterEvents));
      emitted += 1;
    }
  }
  return emitted;
}

function shouldSkipInitialSourceIntroduction(profile = {}, edges = []) {
  if (!isProducedArtifactProfile(profile)) return false;
  return hasIncomingObjectContextEdge(profile, edges);
}

function isProducedArtifactProfile(profile = {}) {
  return normalizedActionSteps(profile).some(step => step.operation_type === 'produce_artifact') ||
    (profile.evidence || []).some(item => item.kind === 'formal_semantics.produce_artifact');
}

function hasIncomingObjectContextEdge(profile = {}, edges = []) {
  return (edges || []).some(edge =>
    edge.target === profile.node_id &&
    edge.validation_method === 'doc_flow_object_context'
  );
}

function applyActionStepsAtNode(labelFlow, profile, state) {
  const steps = normalizedActionSteps(profile);
  const ambiguousDualPhase = Boolean(profile.ambiguous_action_order && hasSinkLikeStep(steps) && hasFilterLikeStep(steps));

  if (ambiguousDualPhase) {
    for (const step of steps.filter(isSinkLikeStep)) {
      recordStepObservation(labelFlow, profile, step, state, 'pre_action_observation');
    }
  }

  for (let index = 0; index < steps.length; index += 1) {
    const step = steps[index];
    if (!labelAvailableBeforeStep(labelFlow, profile, steps, index)) continue;
    const storageKey = inferStorageKey(profile, step);
    if (isSinkLikeStep(step) && !ambiguousDualPhase) {
      recordStepObservation(labelFlow, profile, step, state, 'step_observation');
    }
    if (storageKey && isStorageWriteStep(step, profile)) {
      recordStorageWrite(labelFlow, storageKey, state, profile, step);
    }
    if (storageKey && isStorageReadStep(step, profile)) {
      recordStorageReadProfile(storageKey, state, profile, step);
    }
  }
}

function recordSinkObservationsForArrivedLabelFlow(labelFlow, profile, state) {
  const steps = normalizedActionSteps(profile);
  const ambiguousDualPhase = Boolean(profile.ambiguous_action_order && hasSinkLikeStep(steps) && hasFilterLikeStep(steps));

  if (ambiguousDualPhase) {
    for (const step of steps.filter(isSinkLikeStep)) {
      recordStepObservation(labelFlow, profile, step, state, 'pre_action_observation');
    }
    return;
  }

  for (let index = 0; index < steps.length; index += 1) {
    const step = steps[index];
    if (!isSinkLikeStep(step)) continue;
    if (!labelAvailableBeforeStep(labelFlow, profile, steps, index)) continue;
    recordStepObservation(labelFlow, profile, step, state, 'step_observation');
  }
}

function labelAvailableBeforeStep(labelFlow, profile, steps, stepIndex) {
  let simulated = labelFlow;
  for (const step of steps.slice(0, stepIndex)) {
    if (!isFilterLikeStep(step)) continue;
    const result = applyLabelFlowFilter({
      labelFlow: simulated,
      currentProfile: filterProfileFromStep(profile, step),
      edge: {}
    });
    if (!result.branches.length) return false;
    const branch = result.branches[0];
    simulated = {
      ...simulated,
      label: compactLabel(branch.label),
      flow_mode: branch.flow_mode || simulated.flow_mode
    };
  }
  return true;
}

function filterProfileFromStep(profile, step) {
  return {
    ...profile,
    node_roles: step.node_roles || [],
    security_tags: step.security_tags || [],
    operation_tags: step.operation_tags || [],
    evidence: step.evidence || [],
    action_step_id: step.step_id,
    operation_type: step.operation_type
  };
}

function recordStepObservation(labelFlow, profile, step, state, reason) {
  const signature = `${profile.node_id}|${step.step_id}|${labelFlow.label_flow_id}|${reason}`;
  if (state.observationSignatures.has(signature)) return;
  state.observationSignatures.add(signature);

  // Plain step observation. Periodic leaks (an in-cycle sink re-emitting each
  // loop) are NO LONGER discovered here on a second lap — the cycle is folded into
  // a label closure, so periodic observations are emitted explicitly by
  // recordCyclePeriodicObservations. A step observation is therefore always a
  // single (non-periodic) crossing.
  const event = {
    observation_event_id: nextId(state, 'observation', 'obsev'),
    node_id: profile.node_id,
    node_name: profile.node_name,
    label_flow_id: labelFlow.label_flow_id,
    action_step_id: step.step_id,
    operation_type: step.operation_type,
    order: step.order,
    order_confidence: profile.action_order_confidence,
    ambiguous_action_order: Boolean(profile.ambiguous_action_order),
    node_roles: (step.node_roles || []).filter(role => SINK_LIKE_ROLES.has(role)),
    security_tags: step.security_tags || [],
    boundary: step.boundary || profileBoundary(profile),
    flow_state_id: labelFlow.flow_state_id || '',
    observed_state_ids: (labelFlow.flow_state_id ? [labelFlow.flow_state_id] : []),
    leak_type: '',
    leak_severity: '',
    reason
  };
  const flowState = labelFlow.flow_state_id ? state.flowStates.get(labelFlow.flow_state_id) : null;
  if (flowState) {
    flowState.reached_observation_ids = appendIds(
      flowState.reached_observation_ids || [],
      [event.observation_event_id]
    );
  }
  state.observationEvents.push(event);
  state.allEvents.push({ ...event, type: 'observation' });
}

// Sub-classify a periodic leak by how the circulating data changes each lap.
// Grounded in what the flow's label reliably carries after one iteration:
//   - amplifying: high/critical sensitivity re-exposed every loop, or the flow
//     accumulated additional merged label groups (data grows per pass).
//   - mutating:   the data's identity was transformed on the loop (derived label
//     or transformed availability) — a different class re-emitted each pass.
//   - steady:     the same raw label re-circulates unchanged.
// DOE escalates amplifying/mutating above steady (see evidence-pack leak_type).
function classifyPeriodicSeverity(labelFlow = {}) {
  const label = labelFlow.label || {};
  const sensitivity = String(label.sensitivity || '').toLowerCase();
  const accumulates = Array.isArray(labelFlow.merge_group_ids) && labelFlow.merge_group_ids.length > 0;
  if (sensitivity === 'high' || sensitivity === 'critical' || accumulates) {
    return 'amplifying';
  }
  if (label.mode === 'derived' || labelAvailability(label, labelFlow) === 'transformed') {
    return 'mutating';
  }
  return 'steady';
}

const PERIODIC_SEVERITY_RANK = { steady: 0, mutating: 1, amplifying: 2 };

// Emit ONE periodic observation per sink that lies inside a real cycle (whole-
// cycle, not per closure member). A cycle-internal sink re-emits its data class
// every loop iteration; the closure fold replaced the flow copy, so periodic leaks
// are recorded explicitly here instead of being discovered on a second lap.
// `severityLabels` is the fixpoint closure of the seed under the cycle transform —
// used ONLY to grade severity (the loop is as unsafe as its worst circulating
// label); it never forks the flow. Severity is the HIGHEST tier across the closure.
function recordCyclePeriodicObservations({ labelFlow, feedbackCyclePaths, severityLabels, profilesByNode, state }) {
  const members = (severityLabels && severityLabels.length ? severityLabels : [labelFlow.label]).filter(Boolean);
  let severity = 'steady';
  for (const member of members) {
    const tier = classifyPeriodicSeverity({ ...labelFlow, label: member });
    if (PERIODIC_SEVERITY_RANK[tier] > PERIODIC_SEVERITY_RANK[severity]) severity = tier;
  }

  const cycleNodeIds = uniqueValues(feedbackCyclePaths.flat());
  for (const nodeId of cycleNodeIds) {
    const profile = profilesByNode.get(nodeId);
    if (!profile) continue;
    const steps = normalizedActionSteps(profile);
    for (const step of steps) {
      if (!isSinkLikeStep(step)) continue;
      recordPeriodicStepObservation(labelFlow, profile, step, severity, state);
    }
  }
}

// Record a single periodic observation per (in-cycle sink step, seed label class).
// Deduped on (node, step, seed-label-class) — NOT on label_flow_id — so all the
// flows that carry the same data class through the same cycle sink collapse to ONE
// periodic observation. A representative label_flow_id is attached for linkage.
function recordPeriodicStepObservation(labelFlow, profile, step, severity, state) {
  const signature = `${profile.node_id}|${step.step_id}|${closureLabelKey(labelFlow.label)}|cycle_periodic`;
  if (state.observationSignatures.has(signature)) return;
  state.observationSignatures.add(signature);

  const event = {
    observation_event_id: nextId(state, 'observation', 'obsev'),
    node_id: profile.node_id,
    node_name: profile.node_name,
    label_flow_id: labelFlow.label_flow_id,
    action_step_id: step.step_id,
    operation_type: step.operation_type,
    order: step.order,
    order_confidence: profile.action_order_confidence,
    ambiguous_action_order: Boolean(profile.ambiguous_action_order),
    node_roles: (step.node_roles || []).filter(role => SINK_LIKE_ROLES.has(role)),
    security_tags: step.security_tags || [],
    boundary: step.boundary || profileBoundary(profile),
    flow_state_id: labelFlow.flow_state_id || '',
    observed_state_ids: (labelFlow.flow_state_id ? [labelFlow.flow_state_id] : []),
    leak_type: 'periodic',
    leak_severity: severity,
    reason: 'cycle_periodic'
  };
  const flowState = labelFlow.flow_state_id ? state.flowStates.get(labelFlow.flow_state_id) : null;
  if (flowState) {
    flowState.reached_observation_ids = appendIds(
      flowState.reached_observation_ids || [],
      [event.observation_event_id]
    );
  }
  state.observationEvents.push(event);
  state.allEvents.push({ ...event, type: 'observation' });
}

function createState(options) {
  return {
    options,
    labelFlows: [],
    flowById: new Map(),
    flowStateIndex: new Map(),
    flowStates: new Map(),
    labelFlowsByNode: new Map(),
    queue: [],
    transitions: [],
    routeEvents: [],
    filterEvents: [],
    mergeEvents: [],
    observationEvents: [],
    sourceIntroductions: [],
    truncationEvents: [],
    allEvents: [],
    truncated: false,
    cycleClosureCount: 0,
    closureCache: new Map(),
    ids: {
      labelFlow: 0,
      flowState: 0,
      origin: 0,
      pathClass: 0,
      representativePath: 0,
      transition: 0,
      route: 0,
      filter: 0,
      merge: 0,
      observation: 0,
      truncation: 0
    },
    observationSignatures: new Set(),
    mergeSignatures: new Set(),
    storageState: new Map(),
    storageReadProfiles: new Map(),
    storageReadSignatures: new Set(),
    storageMergeSignatures: new Set(),
    provenanceStore: {
      origins: new Map(),
      originIndex: new Map(),
      pathClasses: new Map(),
      pathClassIndex: new Map(),
      representativePaths: new Map(),
      representativePathIndex: new Map()
    }
  };
}

function createInitialLabelFlow(profile, label, state) {
  const introEvent = {
    event_id: nextId(state, 'filter', 'filter'),
    local_event_key: `initial:${profile.node_id}:${label.label}`,
    type: 'source_introduction',
    node_id: profile.node_id,
    node_name: profile.node_name,
    introduced_label: compactLabel(label),
    introduced_labels: [compactLabel(label)],
    context_label: null,
    evidence: 'initial data_introduction node'
  };
  state.filterEvents.push(introEvent);
  state.sourceIntroductions.push(introEvent);
  state.allEvents.push(introEvent);

  const triggerContext = [];
  if (profile.node_roles?.includes('control_context')) {
    triggerContext.push({
      node_id: profile.node_id,
      node_name: profile.node_name,
      reason: 'source is also control context'
    });
  }

  return normalizeLabelFlow({
    label_flow_id: nextId(state, 'labelFlow', 'lf'),
    parent_label_flow_ids: [],
    current_node: profile.node_id,
    current_node_name: profile.node_name,
    node_path: [profile.node_id],
    node_names: [profile.node_name || profile.node_id],
    edge_path: [],
    label: compactLabel(label),
    trigger_context: triggerContext,
    route_history: [],
    filter_events: [introEvent],
    source_intro_applied_nodes: [profile.node_id],
    flow_mode: 'source_introduction',
    confidence: roundConfidence(label.confidence || 0.3),
    terminated: false,
    termination_reason: '',
    truncated: false,
    merge_group_ids: [],
    related_label_flow_ids: [],
    parent_label_origin: '',
    storage_key: '',
    // Cycle bookkeeping (inert unless a real cycle is passed through):
    //   _cycle_nodes — node ids of every real cycle body this flow has PASSED
    //                  THROUGH. Used only to tag collapse on a flow that exits the
    //                  cycle to an outside sink. A flow no longer circles the loop
    //                  (the cycle is folded into a label closure), so there is no
    //                  revisit counter or in-cycle-lap flag anymore.
    _cycle_nodes: []
  });
}

// 语义型 flow_mode 描述【节点对数据的变换】(在该节点引入/派生/读存储),与边的
// 遍历方式无关,必须保留,不被 route 降级覆盖。
const SEMANTIC_FLOW_MODES = new Set(['source_introduction', 'derived_flow', 'storage_read']);

// 子流 flow_mode 解析:
//  - 若 filter 给出语义型 mode(引入/派生/读存储),尊重之(节点变换语义优先)。
//  - 否则由 route.state 决定遍历确定性:definite_route => definite_flow;其余 => may_flow。
// P2-A 的效果在此落地:纯顺序 control_flow 边 route.state=may_route,使得即便父流是
// definite_flow,跨这条"只表达步骤先后"的边后子流也降为 may_flow —— 数据标签不再沿
// 文档步骤顺序被当作确定数据流无脑扩散。
function resolveChildFlowMode(branch = {}, route = {}) {
  const branchMode = branch.flow_mode || '';
  if (SEMANTIC_FLOW_MODES.has(branchMode)) return branchMode;
  return route.state === 'definite_route' ? 'definite_flow' : 'may_flow';
}

function createChildLabelFlow({ parent, targetProfile, edge, route, routeEvent, branch, filterEvents, cycleNodesHere = [] }) {
  const label = compactLabel(branch.label);
  const triggerContext = mergeTriggerContexts(parent.trigger_context || [], branch.trigger_context || []);
  const confidence = roundConfidence(
    Number(parent.confidence || 0.3) *
    Number(route.confidence || 0.65) *
    Number(branch.confidence_multiplier || 1) *
    Number(label.confidence || parent.label?.confidence || 0.7)
  );

  const cycle = resolveChildCycleState(parent, targetProfile, edge, route, cycleNodesHere);

  return normalizeLabelFlow({
    label_flow_id: branch.label_flow_id || '',
    parent_label_flow_ids: branch.parent_label_flow_ids?.length ? branch.parent_label_flow_ids : [parent.label_flow_id],
    current_node: targetProfile.node_id,
    current_node_name: targetProfile.node_name,
    node_path: [...(parent.node_path || []), targetProfile.node_id],
    node_names: [...(parent.node_names || []), targetProfile.node_name || targetProfile.node_id],
    edge_path: [...(parent.edge_path || []), edge.id || edgeKey(edge)],
    label,
    trigger_context: triggerContext,
    route_history: [...(parent.route_history || []), compactRouteEvent(routeEvent)],
    filter_events: [...(parent.filter_events || []), ...filterEvents],
    source_intro_applied_nodes: branch.source_intro_applied_nodes || parent.source_intro_applied_nodes || [],
    flow_mode: resolveChildFlowMode(branch, route),
    confidence,
    terminated: false,
    termination_reason: '',
    truncated: false,
    merge_group_ids: [...(parent.merge_group_ids || []), ...(branch.merge_group_ids || [])].filter(Boolean),
    related_label_flow_ids: [...(parent.related_label_flow_ids || []), ...(branch.related_label_flow_ids || [])].filter(Boolean),
    parent_label_origin: parent.label_flow_id,
    storage_key: branch.storage_key || parent.storage_key || '',
    _cycle_nodes: cycle.cycle_nodes,
    ...(cycle.cycle_handling ? { cycle_handling: cycle.cycle_handling } : {})
  });
}

// Derive the child flow's cycle bookkeeping. Only ONE fact is tracked now (the
// flow no longer circles the loop — the cycle is folded into a label closure):
//   _cycle_nodes — union of every real cycle body the flow has PASSED THROUGH
//                  (touched any cycle-body node). A copy that leaves via a
//                  non-feedback edge to a node OUTSIDE the cycle "passed through
//                  the cycle" and collapses.
// cycle_handling='collapse' is set on exactly those exiting copies.
function resolveChildCycleState(parent, targetProfile, edge, route, cycleNodesHere = []) {
  const targetId = targetProfile.node_id;

  // The flow's known cycle-body node set after stepping from the current node:
  // parent's accumulated set ∪ the cycle(s) rooted at the node just left.
  const cycleNodes = uniqueValues([...(parent._cycle_nodes || []), ...cycleNodesHere]);

  // Collapse: the flow passed through a cycle body (cycleNodes non-empty) and this
  // non-feedback edge lands on a node OUTSIDE that cycle — it exits to the wider
  // graph. Not the feedback edge itself (that's absorbed into the closure).
  const exitsCycle = cycleNodes.length > 0 &&
    !edge.is_feedback_edge &&
    !cycleNodes.includes(targetId);

  return {
    cycle_nodes: cycleNodes,
    cycle_handling: exitsCycle ? 'collapse' : ''
  };
}

// dedupeLabels' uniqueness key: [label, origin_node, introduced_at]. Two labels
// with the same key are the same data item and must NOT both enter the closure.
function closureLabelKey(label = {}) {
  return [
    label.label || '',
    label.origin_node || '',
    label.introduced_at || label.origin_node || ''
  ].join('|');
}

// Direction of a cycle transform, hard-coded by product type (not by comparing
// label contents). A closure member is SPECIALIZING relative to the seed when the
// cycle EXTRACTED a concrete new label class out of it — semantic_extraction reads
// a vague/broad label and pulls out a specific, nameable class (pii / location /
// credentials / file_content …); pseudonymization mints a 'pseudonymous_data' class.
// The reason each of these forks its own flow is NOT that it "grows" the flow set —
// it is that the transform made the data MORE SPECIFIC: it resolved one broad label
// into several distinct classes that can now be tracked and graded individually.
// Each concrete class is a different downstream risk, so each must travel as its own
// flow (exactly like an ordinary derive point in the forward flood fans a user_prompt
// into multiple derived classes, each its own flow — we reuse that multi-flow
// semantics here). More flows is the CONSEQUENCE of specialization, not its criterion.
//
// A member is NOT specializing (the seed already covers it) when it IS the seed, or
// when it is a GENERALIZING product — a transform that made the data BROADER / a
// subset of its input (summarize/aggregate → an abstracted 'aggregate_data' class).
// A generalization carries strictly ≤ the information of the seed, so the seed's own
// out-flow already covers it: nothing new to name, nothing new to fork.
//
// Both specializing and generalizing products carry mode==='derived'
// (createSyntheticLabel stamps it for BOTH the semantic-extraction extract AND the
// summarize/aggregate summary), so mode alone CANNOT tell them apart. Direction is
// carried by CATEGORY:
//   * summarization / aggregation -> category 'aggregate_data' (broader abstraction,
//     subset of the input -> GENERALIZING, the seed's own out-flow already carries
//     it, never inject);
//   * redact / slice -> label dropped (empty branch, never enters the closure);
//   * semantic_extraction -> a concrete new class (pii / location / file_content …,
//     NOT aggregate_data) the loop EXTRACTED -> SPECIALIZING;
//   * pseudonymization -> category 'pseudonymous_data' -> SPECIALIZING.
// So a member is specializing iff mode==='derived' AND its category is not a known
// generalizing product. Unknown/non-derived products default to non-specializing: we
// would rather degrade to zero inflation and let the forward flood carry recall than
// fork a flow we cannot classify.
const GENERALIZING_DERIVED_CATEGORIES = new Set(['aggregate_data']);
function isSpecializingClosureMember(member = {}, seedLabel = {}) {
  if (!member) return false;
  if (closureLabelKey(member) === closureLabelKey(seedLabel)) return false;
  if (member.category === 'pseudonymous_data') return true;
  if (member.mode === 'derived' && !GENERALIZING_DERIVED_CATEGORIES.has(member.category)) return true;
  return false;
}

// Fold a real cycle into the FIXPOINT CLOSURE of its label transform.
//
// A cycle body is a transform operator T (its nodes summarize / derive / slice /
// aggregate the circulating label). We compute the set of labels the seed would
// become after passing the cycle 0, 1, 2, … times — L ∪ T(L) ∪ T²(L) ∪ … — the
// fixpoint of T on the seed.
//
// The closure serves two consumers:
//   1. GRADE SEVERITY of the cycle's periodic leak (does the loop leave the data
//      unchanged=steady, transform its class=mutating, or re-expose/accumulate
//      sensitivity=amplifying). For a pass-through cycle (T(L)≡L) the closure is
//      {L} → severity steady.
//   2. Supply the SPECIALIZING members that must leave the cycle as their own flows —
//      concrete new classes the loop EXTRACTED (mode==='derived') or pseudonymized
//      (category==='pseudonymous_data') that are NOT a subset of the seed (see
//      isSpecializingClosureMember). GENERALIZING members (summary/aggregate, a subset
//      of the input) and the seed itself are not injected: the seed's own out-edge
//      filter already carries them, so a pass-through / generalizing cycle emits zero
//      extra flows, byte-identical to the acyclic case. Any specializing member the
//      forward flood already produces at the exit node collapses on buildFlowStateKey
//      (no double count).
//
// Convergence: every transform primitive binds a derived label's introduced_at to
// a node id over the fixed cycle node set, so closureLabelKey space is finite and
// the union stops growing. maxIterations is a backstop against a pathological
// operator that mints a fresh key each lap (returns truncated:true, never silent).
//
// Returns { labels: [seed + transformed forms, deduped], truncated }.
function computeCycleClosure({ seedLabel, feedbackCyclePaths, profilesByNode, nodesById, maxIterations }) {
  const byKey = new Map();
  byKey.set(closureLabelKey(seedLabel), compactLabel(seedLabel));

  // One "lap" applies the transform of every node on every cycle path to every
  // label currently in the closure, unioning the results. Repeat until a lap adds
  // nothing (fixpoint) or the backstop trips.
  let truncated = false;
  let iterations = 0;
  while (true) {
    if (iterations >= maxIterations) {
      truncated = true;
      break;
    }
    iterations += 1;
    let grew = false;
    const current = Array.from(byKey.values());
    for (const cyclePath of feedbackCyclePaths) {
      for (const nodeId of cyclePath) {
        const profile = profilesByNode.get(nodeId);
        if (!profile) continue;
        for (const label of current) {
          const result = applyLabelFlowFilter({
            labelFlow: {
              label,
              trigger_context: [],
              // Mark this node as already-source-introduced so the filter does NOT
              // re-introduce the node's OWN independent labels into the closure.
              // The closure is the set of labels the SEED TRANSFORMS INTO
              // (summarize / derive / slice of the input) — NOT every source label
              // the cycle nodes happen to introduce. Those independent sources are
              // already seeded by the normal flood as their own initial flows;
              // pulling them in here caused the closure to balloon to hundreds of
              // members and duplicate flows the flood already produces.
              source_intro_applied_nodes: [nodeId],
              flow_mode: 'may_flow'
            },
            currentProfile: propagationProfile(profile),
            currentNode: nodesById.get(nodeId),
            edge: {}
          });
          for (const branch of result.branches || []) {
            // A source_introduction branch is the node introducing its own label,
            // not a transform of the seed — skip it (defensive; the flag above
            // already suppresses shouldIntroduceSource for this node).
            if (branch.flow_mode === 'source_introduction') continue;
            const produced = compactLabel(branch.label);
            if (!produced) continue;
            const key = closureLabelKey(produced);
            if (!byKey.has(key)) {
              byKey.set(key, produced);
              grew = true;
            }
          }
        }
      }
    }
    if (!grew) break;
  }

  return { labels: dedupeLabels(Array.from(byKey.values())), truncated };
}

function maybeCreateMergeRelationships(labelFlow, state, profilesByNode) {
  const profile = profilesByNode.get(labelFlow.current_node);
  if (!profile || !profile.operation_tags?.includes('merge_join')) return;

  const peers = (state.labelFlowsByNode.get(labelFlow.current_node) || [])
    .filter(peer => !peer.terminated)
    .slice(0, state.options.maxMergeParents);
  if (peers.length < 2) return;

  const ids = peers.map(peer => peer.label_flow_id).sort();
  const signature = `${profile.node_id}|merge_join`;
  let event = state.mergeEvents.find(item => item.type === 'merge_join' && item.node_id === profile.node_id);
  if (!event) {
    if (state.mergeSignatures.has(signature)) return;
    state.mergeSignatures.add(signature);
    event = {
      event_id: nextId(state, 'merge', 'merge'),
      type: 'merge_join',
      node_id: profile.node_id,
      node_name: profile.node_name,
      label_flow_ids: [],
      label_flow_id_count: 0,
      labels: [],
      evidence: 'explicit merge_join operation relates co-located label flows without merging labels'
    };
    state.mergeEvents.push(event);
    state.allEvents.push(event);
  }
  updateMergeEventMembers(event, peers, state.options);

  for (const peer of peers) {
    peer.merge_group_ids = appendIds(peer.merge_group_ids || [], [event.event_id]);
    const related = ids.filter(id => id !== peer.label_flow_id);
    peer.related_label_flow_ids = appendIds(peer.related_label_flow_ids || [], related);
  }
}

function recordStorageWrite(labelFlow, storageKey, state, profile, step = null) {
  labelFlow.storage_key = storageKey;
  if (!state.storageState.has(storageKey)) {
    state.storageState.set(storageKey, []);
  }
  const written = state.storageState.get(storageKey);
  if (!written.includes(labelFlow.label_flow_id)) written.push(labelFlow.label_flow_id);
  maybeCreateStorageMergeEvent(storageKey, state, profile, step);
}

function recordStorageReadProfile(storageKey, state, profile, step = null) {
  if (!state.storageReadProfiles.has(storageKey)) {
    state.storageReadProfiles.set(storageKey, new Map());
  }
  state.storageReadProfiles.get(storageKey).set(`${profile.node_id}:${step?.step_id || 'node'}`, { profile, step });
}

function processPendingStorageReads(state) {
  let created = 0;
  for (const [storageKey, profiles] of state.storageReadProfiles.entries()) {
    if (!state.storageState.has(storageKey)) continue;
    for (const item of profiles.values()) {
      created += maybeCreateStorageReadFlows(storageKey, state, item.profile, item.step);
    }
  }
  return created > 0;
}

function maybeCreateStorageReadFlows(storageKey, state, profile, step = null) {
  const writtenIds = state.storageState.get(storageKey) || [];
  if (!writtenIds.length) return 0;

  const writtenFlows = writtenIds
    .map(id => state.flowById.get(id))
    .filter(Boolean)
    .slice(0, state.options.maxMergeParents);
  if (!writtenFlows.length) return 0;

  const mergeEvent = maybeCreateStorageMergeEvent(storageKey, state, profile, step);
  let created = 0;
  for (const writtenFlow of writtenFlows) {
    const signature = `${profile.node_id}|${step?.step_id || 'node'}|storage_read|${storageKey}|${writtenFlow.label_flow_id}`;
    if (state.storageReadSignatures.has(signature)) continue;
    state.storageReadSignatures.add(signature);

    if (state.labelFlows.length >= state.options.maxLabelFlows) {
      markTruncated(writtenFlow, state, 'max_label_flows_before_storage_read');
      return created;
    }
    const storageLabel = {
      ...writtenFlow.label,
      introduced_at: profile.node_id
    };
    const event = {
      event_id: nextId(state, 'filter', 'filter'),
      type: 'storage_read',
      node_id: profile.node_id,
      node_name: profile.node_name,
      label_flow_id: writtenFlow.label_flow_id,
      action_step_id: step?.step_id || '',
      operation_type: step?.operation_type || '',
      storage_key: storageKey,
      introduced_label: compactLabel(storageLabel),
      introduced_labels: [compactLabel(storageLabel)],
      parent_label_flow_ids: [writtenFlow.label_flow_id],
      evidence: `read label flow from persisted storage ${storageKey}`
    };
    state.filterEvents.push(event);
    state.sourceIntroductions.push(event);
    state.allEvents.push(event);

    const child = normalizeLabelFlow({
      label_flow_id: nextId(state, 'labelFlow', 'lf'),
      parent_label_flow_ids: [writtenFlow.label_flow_id],
      current_node: profile.node_id,
      current_node_name: profile.node_name,
      node_path: [...(writtenFlow.node_path || []), profile.node_id],
      node_names: [...(writtenFlow.node_names || []), profile.node_name || profile.node_id],
      // 存储读跳(写入节点 -> 读取节点)不经图边,而是经持久化存储传递。为维持
      // edge_path 的位置契约 len(edge)==len(node)-1(edge[i] 连 node[i]->node[i+1]),
      // 补一条可识别的合成哨兵边,而非留空。哨兵不命中任何真实图边 id,消费方
      // (evidence-pack link 标注)查不到即正确地不产 data_flow link——存储读本非图边传递。
      edge_path: [...(writtenFlow.edge_path || []), storageReadEdgeId(writtenFlow.current_node, profile.node_id)],
      label: compactLabel(storageLabel),
      trigger_context: writtenFlow.trigger_context || [],
      route_history: [...(writtenFlow.route_history || [])],
      filter_events: [...(writtenFlow.filter_events || []), event],
      source_intro_applied_nodes: uniqueValues([...(writtenFlow.source_intro_applied_nodes || []), profile.node_id]),
      flow_mode: 'storage_read',
      confidence: roundConfidence(Number(writtenFlow.confidence || 0.3) * 0.9),
      terminated: false,
      termination_reason: '',
      truncated: false,
      merge_group_ids: appendIds(writtenFlow.merge_group_ids || [], [mergeEvent?.event_id || '']),
      related_label_flow_ids: appendIds(writtenFlow.related_label_flow_ids || [], writtenIds.filter(id => id !== writtenFlow.label_flow_id)),
      parent_label_origin: writtenFlow.label_flow_id,
      storage_key: storageKey
    });

    if (registerLabelFlow(child, state, { enqueue: true })) {
      created += 1;
      state.transitions.push({
        transition_id: nextId(state, 'transition', 'tr'),
        type: 'storage_read',
        from_label_flow_id: writtenFlow.label_flow_id,
        to_label_flow_id: child.label_flow_id,
        fcg_edge_id: '',
        source: writtenFlow.current_node,
        target: profile.node_id,
        route_event_id: '',
        filter_event_ids: [event.event_id],
        route_state: 'definite_route'
      });
    }
  }
  return created;
}

function maybeCreateStorageMergeEvent(storageKey, state, profile, step = null) {
  const writtenIds = uniqueValues(state.storageState.get(storageKey) || []).sort();
  if (writtenIds.length < 2) return null;
  const signature = `${storageKey}|storage_merge`;
  let existing = state.mergeEvents.find(event => event.type === 'storage_merge' && event.storage_key === storageKey);
  const writtenFlows = writtenIds.map(id => state.flowById.get(id)).filter(Boolean);
  if (existing) {
    updateMergeEventMembers(existing, writtenFlows, state.options);
    applyMergeEventToFlows(existing, writtenFlows, state.options);
    return existing;
  }
  if (state.storageMergeSignatures.has(signature)) return null;
  state.storageMergeSignatures.add(signature);

  const event = {
    event_id: nextId(state, 'merge', 'merge'),
    type: 'storage_merge',
    node_id: profile.node_id,
    node_name: profile.node_name,
    action_step_id: step?.step_id || '',
    operation_type: step?.operation_type || '',
    storage_key: storageKey,
    label_flow_ids: [],
    label_flow_id_count: 0,
    labels: [],
    evidence: `multiple label flows persisted into ${storageKey}`
  };
  updateMergeEventMembers(event, writtenFlows, state.options);
  state.mergeEvents.push(event);
  state.allEvents.push(event);

  applyMergeEventToFlows(event, writtenFlows, state.options);
  return event;
}

function updateMergeEventMembers(event, flows = [], options = {}) {
  const existingIds = event._all_label_flow_ids || event.label_flow_ids || [];
  const ids = uniqueValues([...existingIds, ...flows.map(flow => flow.label_flow_id).filter(Boolean)]).sort();
  event._all_label_flow_ids = ids;
  event.label_flow_ids = ids;
  event.label_flow_id_count = ids.length;
  event.label_flow_ids_truncated = false;

  const labels = uniqueLabelsByFingerprint([...(event.labels || []), ...flows.map(flow => compactLabel(flow.label)).filter(Boolean)]);
  event.labels = labels;
  event.label_count = labels.length;
  event.labels_truncated = false;
}

function applyMergeEventToFlows(event, flows = [], options = {}) {
  const ids = event._all_label_flow_ids || event.label_flow_ids || [];
  for (const flow of flows) {
    flow.storage_key = event.storage_key || flow.storage_key || '';
    flow.merge_group_ids = appendIds(flow.merge_group_ids || [], [event.event_id]);
    flow.related_label_flow_ids = appendIds(
      flow.related_label_flow_ids || [],
      ids.filter(id => id !== flow.label_flow_id)
    );
  }
}

function isStorageWriteStep(step = {}, profile = {}) {
  const tags = new Set(step.security_tags || []);
  return (step.node_roles || []).includes('local_persistence') && isWriteLikeStep(step, profile) && (
    tags.has('file_write') || tags.has('memory_write') || tags.has('database_write') || tags.has('log_write') || tags.has('artifact_write')
  );
}

function isStorageReadStep(step = {}, profile = {}) {
  const tags = new Set(step.security_tags || []);
  if (!(step.node_roles || []).includes('data_introduction') || !isReadLikeStep(step, profile) || isWriteLikeStep(step, profile)) return false;
  if (tags.has('file_read') || tags.has('memory_read') || tags.has('database_read')) return true;
  const key = inferStorageKey(profile, step);
  return Boolean(key && !key.endsWith(':unknown'));
}

function inferStorageKey(profile = {}, step = null) {
  const tags = new Set([...(profile.security_tags || []), ...(step?.security_tags || [])]);
  const text = [
    profile.node_name,
    step?.operation_type,
    ...(step?.targets || []).map(target => `${target.type || ''}:${target.value || ''}:${target.raw || ''}`),
    ...(step?.evidence || []).map(item => item.text || ''),
    ...(profile.evidence || []).map(item => item.text || ''),
    ...(profile.data_profile?.labels || []).map(label => [label.field_name, label.field_path, label.evidence_text].filter(Boolean).join(' '))
  ].filter(Boolean).join(' ');
  const lower = text.toLowerCase();
  const surface = tags.has('memory_write') || tags.has('memory_read') || /\b(memory|session|state)\b/i.test(lower) ? 'memory_store'
    : tags.has('database_write') || tags.has('database_read') || /\b(database|db|sql|table|collection)\b/i.test(lower) ? 'database'
      : 'local_file';
  const key = extractStorageObjectName(text, surface) || 'unknown';
  return `${surface}:${key}`;
}

function extractStorageObjectName(text, surface) {
  const normalized = String(text || '').replace(/\\/g, '/');
  const prefixedFile = normalized.match(/(?:^|[\s/_.-])(?:read|write|save|append|store|persist|load|open)[_.-]([A-Za-z0-9_.-]+\.(?:md|txt|json|yaml|yml|csv|log|html|xml|pdf|docx?|xlsx?|py|js|ts|zip))/i);
  if (prefixedFile) return prefixedFile[1].toLowerCase();
  const fileMatch = normalized.match(/([A-Za-z0-9_.-]+\.(?:md|txt|json|yaml|yml|csv|log|html|xml|pdf|docx?|xlsx?|py|js|ts|zip))/i);
  if (fileMatch) return fileMatch[1].toLowerCase();
  const dotted = normalized.match(/(?:read|write|save|append|store|persist|load|open|insert|query|update)[_.-]([A-Za-z0-9_.-]+)/i);
  if (dotted) return dotted[1].toLowerCase();
  if (surface === 'database') {
    const table = normalized.match(/(?:table|collection|database|db|sql)[\s:._-]+([A-Za-z0-9_-]+)/i);
    if (table) return table[1].toLowerCase();
  }
  if (surface === 'memory_store') {
    const mem = normalized.match(/(?:memory|session|state)[\s:._-]+([A-Za-z0-9_-]+)/i);
    if (mem) return mem[1].toLowerCase();
  }
  return '';
}

function isReadLikeProfile(profile = {}) {
  const text = [profile.node_name, ...(profile.evidence || []).map(item => item.kind || item.text || '')].join(' ');
  return /(?:^|[\s._-])(read|get|fetch|retrieve|load|open|query|select)(?:$|[\s._-])/i.test(text) ||
    (profile.evidence || []).some(item => item.kind === 'read_pattern');
}

function isWriteLikeProfile(profile = {}) {
  const text = [profile.node_name, ...(profile.evidence || []).map(item => item.kind || item.text || '')].join(' ');
  return /(?:^|[\s._-])(write|save|store|persist|append|insert|update)(?:$|[\s._-])/i.test(text) ||
    (profile.evidence || []).some(item => item.kind === 'persistence_pattern' && /\b(write|save|store|persist|append|insert|update)\b/i.test(item.text || ''));
}

function isReadLikeStep(step = {}, profile = {}) {
  if (['read', 'review', 'verify'].includes(step.operation_type)) return true;
  const text = [profile.node_name, step.operation_type, ...(step.evidence || []).map(item => item.kind || item.text || '')].join(' ');
  return /(?:^|[\s._-])(read|get|fetch|retrieve|load|open|query|select)(?:$|[\s._-])/i.test(text);
}

function isWriteLikeStep(step = {}, profile = {}) {
  if (['write', 'produce_artifact'].includes(step.operation_type)) return true;
  const text = [profile.node_name, step.operation_type, ...(step.evidence || []).map(item => item.kind || item.text || '')].join(' ');
  return /(?:^|[\s._-])(write|save|store|persist|append|insert|update)(?:$|[\s._-])/i.test(text);
}

function normalizedActionSteps(profile = {}) {
  const steps = Array.isArray(profile.action_steps) && profile.action_steps.length
    ? profile.action_steps
    : [{
        step_id: `${profile.node_id || 'node'}:step_001:node`,
        order: 1,
        operation_type: profile.formal_semantics?.operation_type || 'node',
        node_roles: profile.node_roles || [],
        security_tags: profile.security_tags || [],
        operation_tags: profile.operation_tags || [],
        boundary: profileBoundary(profile),
        targets: [],
        evidence: profile.evidence || [],
        confidence: profile.confidence || 0.3
      }];
  return steps.slice().sort((a, b) => Number(a.order || 0) - Number(b.order || 0));
}

function hasSinkLikeStep(steps = []) {
  return steps.some(isSinkLikeStep);
}

function hasFilterLikeStep(steps = []) {
  return steps.some(step => (step.operation_tags || []).some(tag => (
    tag === 'field_slice' ||
    tag === 'semantic_extraction' ||
    tag === 'summarization' ||
    tag === 'aggregation' ||
    tag === 'redaction' ||
    tag === 'pseudonymization'
  )));
}

function isFilterLikeStep(step = {}) {
  return (step.operation_tags || []).some(tag => (
    tag === 'field_slice' ||
    tag === 'semantic_extraction' ||
    tag === 'summarization' ||
    tag === 'aggregation' ||
    tag === 'redaction' ||
    tag === 'pseudonymization'
  ));
}

function isSinkLikeStep(step = {}) {
  return (step.node_roles || []).some(role => SINK_LIKE_ROLES.has(role));
}

function profileBoundary(profile = {}) {
  return {
    data_surface: profile.data_surface,
    receiver_scope: profile.receiver_scope,
    retention_scope: profile.retention_scope,
    trust_boundary: profile.trust_boundary
  };
}

function filterProfileForPropagation(profile = {}) {
  const steps = normalizedActionSteps(profile);
  const filterSteps = steps.filter(step => (step.operation_tags || []).some(tag => (
    tag === 'field_slice' ||
    tag === 'semantic_extraction' ||
    tag === 'summarization' ||
    tag === 'aggregation' ||
    tag === 'redaction' ||
    tag === 'pseudonymization'
  )));
  if (!filterSteps.length) return profile;

  return {
    ...profile,
    operation_tags: uniqueValues(filterSteps.flatMap(step => step.operation_tags || [])).sort(),
    security_tags: uniqueValues(filterSteps.flatMap(step => step.security_tags || [])).sort(),
    node_roles: uniqueValues(filterSteps.flatMap(step => step.node_roles || [])).sort(),
    evidence: filterSteps.flatMap(step => step.evidence || []),
    action_step_id: filterSteps[0].step_id,
    operation_type: filterSteps[0].operation_type
  };
}

function propagationProfile(profile = {}) {
  if (isProducedArtifactProfile(profile)) {
    return {
      ...profile,
      operation_type: 'produce_artifact'
    };
  }
  return filterProfileForPropagation(profile);
}

function registerLabelFlow(labelFlow, state, { enqueue }) {
  if (!labelFlow.label_flow_id) {
    labelFlow.label_flow_id = nextId(state, 'labelFlow', 'lf');
  }
  const normalized = normalizeLabelFlow(labelFlow);
  attachFlowStateMetadata(normalized, state);
  const stateKey = buildFlowStateKey(normalized);
  const existingId = state.flowStateIndex.get(stateKey);
  if (existingId) {
    const existingState = state.flowStates.get(existingId);
    const existingFlow = state.flowById.get(existingState.representative_label_flow_id);
    mergeFlowIntoRepresentative(existingFlow, normalized, existingState, state);
    return false;
  }

  if (state.labelFlows.length >= state.options.maxLabelFlows) {
    markTruncated(normalized, state, 'max_label_flows');
    return false;
  }

  const flowState = createFlowState(normalized, stateKey, state);
  normalized.flow_state_id = flowState.state_id;
  normalized.path_class_ids = flowState.path_class_ids;
  normalized.representative_path_ids = flowState.representative_path_ids;
  normalized.origin_ids = flowState.origin_ids;
  normalized.provenance_event_ids = flowState.provenance_event_ids;

  state.flowStateIndex.set(stateKey, flowState.state_id);
  state.flowStates.set(flowState.state_id, flowState);
  state.flowById.set(normalized.label_flow_id, normalized);
  state.labelFlows.push(normalized);
  if (!state.labelFlowsByNode.has(labelFlow.current_node)) {
    state.labelFlowsByNode.set(normalized.current_node, []);
  }
  state.labelFlowsByNode.get(normalized.current_node).push(normalized);
  if (enqueue) state.queue.push(normalized);
  return true;
}

function buildFlowStateKey(flow = {}) {
  const label = flow.label || {};
  return [
    flow.current_node || '',
    label.label || '',
    label.category || '',
    label.subtype || '',
    labelAvailability(label, flow),
    flow.storage_key || '',
    flow.flow_mode || '',
    flow.phase || 'after_action'
    // No cycle bit: a flow no longer circles the loop, so there is no "on-lap vs
    // pre-lap" state to distinguish. Periodic observations are recorded explicitly
    // (recordCyclePeriodicObservations), not discovered via a dedup-preserving
    // second visit. The closure-derived labels (if any) already differ by their
    // label key above, so distinct closure members occupy distinct states naturally.
  ].join('|');
}

function labelAvailability(label = {}, flow = {}) {
  if (flow.flow_mode === 'storage_read') return 'stored';
  if (flow.flow_mode === 'source_introduction') return label.mode === 'derived' ? 'generated' : 'raw';
  if (isDerivedLabel(label, flow)) return 'transformed';
  return label.mode || 'raw';
}

function isDerivedLabel(label = {}, flow = {}) {
  if (label.mode === 'derived') return true;
  return (flow.filter_events || []).some(event => [
    'field_slice_keep',
    'semantic_derivation',
    'semantic_extraction',
    'aggregate',
    'summarization',
    'artifact_production'
  ].includes(event.type));
}

function attachFlowStateMetadata(flow, state) {
  const originId = internOrigin(flow, state);
  const pathClassId = internPathClass(flow, state);
  const representativePathId = internRepresentativePath(flow, state);
  flow.origin_ids = appendIds(flow.origin_ids || [], [originId]);
  flow.path_class_ids = appendIds(flow.path_class_ids || [], [pathClassId]);
  flow.representative_path_ids = appendIds(flow.representative_path_ids || [], [representativePathId]);
  flow.provenance_event_ids = appendIds(
    flow.provenance_event_ids || [],
    [
      ...(flow.route_history || []).map(event => event.event_id),
      ...(flow.filter_events || []).map(event => event.event_id),
      ...(flow.merge_group_ids || [])
    ]
  );
}

function createFlowState(flow, stateKey, state) {
  return {
    state_id: nextId(state, 'flowState', 'fs'),
    state_key: stateKey,
    representative_label_flow_id: flow.label_flow_id,
    node_id: flow.current_node || '',
    node_name: flow.current_node_name || '',
    label: compactLabel(flow.label),
    availability: labelAvailability(flow.label || {}, flow),
    storage_key: flow.storage_key || '',
    phase: flow.phase || 'after_action',
    origin_ids: flow.origin_ids || [],
    provenance_event_ids: flow.provenance_event_ids || [],
    path_class_ids: flow.path_class_ids || [],
    representative_path_ids: flow.representative_path_ids || [],
    label_flow_ids: [flow.label_flow_id],
    label_flow_id_count: 1,
    merged_path_count: 1,
    confidence_min: flow.confidence || 0.3,
    confidence_max: flow.confidence || 0.3,
    reached_observation_ids: []
  };
}

function mergeFlowIntoRepresentative(existingFlow, incomingFlow, flowState, state) {
  if (!existingFlow || !flowState) return;
  const incomingIds = appendIds([], [incomingFlow.label_flow_id]);
  flowState.label_flow_ids = appendIds(flowState.label_flow_ids || [], incomingIds);
  flowState.label_flow_id_count = Math.max(flowState.label_flow_id_count || 1, (flowState.label_flow_ids || []).length);
  flowState.merged_path_count = Number(flowState.merged_path_count || 1) + 1;
  flowState.origin_ids = appendIds(flowState.origin_ids || [], incomingFlow.origin_ids || []);
  flowState.provenance_event_ids = appendIds(flowState.provenance_event_ids || [], incomingFlow.provenance_event_ids || []);
  flowState.path_class_ids = appendIds(flowState.path_class_ids || [], incomingFlow.path_class_ids || []);
  flowState.representative_path_ids = appendIds(flowState.representative_path_ids || [], incomingFlow.representative_path_ids || []);
  flowState.confidence_min = Math.min(Number(flowState.confidence_min || 1), Number(incomingFlow.confidence || 0.3));
  flowState.confidence_max = Math.max(Number(flowState.confidence_max || 0), Number(incomingFlow.confidence || 0.3));

  existingFlow.related_label_flow_ids = appendIds(
    existingFlow.related_label_flow_ids || [],
    [...(incomingFlow.parent_label_flow_ids || []), incomingFlow.label_flow_id].filter(Boolean)
  );
  existingFlow.parent_label_flow_ids = appendLimitedIds(
    existingFlow.parent_label_flow_ids || [],
    incomingFlow.parent_label_flow_ids || [],
    1
  );
  existingFlow.filter_events = appendEventsById(existingFlow.filter_events || [], incomingFlow.filter_events || []);
  existingFlow.route_history = appendEventsById(existingFlow.route_history || [], incomingFlow.route_history || []);
  existingFlow.merge_group_ids = appendIds(existingFlow.merge_group_ids || [], incomingFlow.merge_group_ids || []);
  existingFlow.origin_ids = flowState.origin_ids;
  existingFlow.provenance_event_ids = flowState.provenance_event_ids;
  existingFlow.path_class_ids = flowState.path_class_ids;
  existingFlow.representative_path_ids = flowState.representative_path_ids;
  existingFlow.merged_path_count = flowState.merged_path_count;
  existingFlow.confidence = roundConfidence(Math.max(Number(existingFlow.confidence || 0.3), Number(incomingFlow.confidence || 0.3)));
}

function internOrigin(flow = {}, state) {
  const label = flow.label || {};
  const key = [
    label.origin_node || flow.origin_node || '',
    label.introduced_at || flow.introduced_at || '',
    label.label || '',
    label.evidence_kind || '',
    label.evidence_text || ''
  ].join('|');
  const existing = state.provenanceStore.originIndex.get(key);
  if (existing) return existing;
  const originId = nextId(state, 'origin', 'origin');
  state.provenanceStore.originIndex.set(key, originId);
  state.provenanceStore.origins.set(originId, {
    origin_id: originId,
    origin_node: label.origin_node || flow.origin_node || '',
    origin_node_name: label.origin_node_name || flow.origin_node_name || label.origin_node || '',
    introduced_at: label.introduced_at || flow.introduced_at || '',
    label: compactLabel(label),
    evidence_kind: label.evidence_kind || '',
    evidence_text: label.evidence_text || ''
  });
  return originId;
}

function internPathClass(flow = {}, state) {
  const key = [
    flow.current_node || '',
    flow.label?.label || '',
    flow.flow_mode || '',
    flow.storage_key || '',
    compactPathKinds(flow).join('>'),
    compactCriticalNodes(flow).join('>')
  ].join('|');
  const existing = state.provenanceStore.pathClassIndex.get(key);
  if (existing) return existing;
  const pathClassId = nextId(state, 'pathClass', 'pc');
  state.provenanceStore.pathClassIndex.set(key, pathClassId);
  state.provenanceStore.pathClasses.set(pathClassId, {
    path_class_id: pathClassId,
    start_node: (flow.node_path || [])[0] || '',
    end_node: flow.current_node || '',
    label: flow.label?.label || '',
    flow_mode: flow.flow_mode || '',
    storage_key: flow.storage_key || '',
    edge_kinds: compactPathKinds(flow),
    critical_nodes: compactCriticalNodes(flow),
    critical_events: compactCriticalEvents(flow)
  });
  return pathClassId;
}

function internRepresentativePath(flow = {}, state) {
  const key = [
    flow.label?.label || '',
    (flow.node_path || []).join('>'),
    (flow.edge_path || []).join('>'),
    (flow.filter_events || []).map(event => event.event_id || event.type || '').join('>')
  ].join('|');
  const existing = state.provenanceStore.representativePathIndex.get(key);
  if (existing) return existing;
  const pathId = nextId(state, 'representativePath', 'rp');
  state.provenanceStore.representativePathIndex.set(key, pathId);
  state.provenanceStore.representativePaths.set(pathId, {
    representative_path_id: pathId,
    label_flow_id: flow.label_flow_id || '',
    parent_label_flow_ids: flow.parent_label_flow_ids || [],
    current_node: flow.current_node || '',
    current_node_name: flow.current_node_name || '',
    incoming_edge_id: (flow.edge_path || [])[Math.max(0, (flow.edge_path || []).length - 1)] || '',
    label: compactLabel(flow.label),
    node_path: flow.node_path || [],
    node_names: flow.node_names || [],
    edge_path: flow.edge_path || [],
    route_event_ids: (flow.route_history || []).map(event => event.event_id).filter(Boolean),
    filter_event_ids: (flow.filter_events || []).map(event => event.event_id).filter(Boolean),
    merge_group_ids: flow.merge_group_ids || [],
    storage_key: flow.storage_key || ''
  });
  return pathId;
}

function compactPathKinds(flow = {}) {
  return (flow.route_history || [])
    .map(event => event.state || event.edge_id || '')
    .filter(Boolean);
}

function compactCriticalNodes(flow = {}) {
  return uniqueValues(flow.node_path || []);
}

function compactCriticalEvents(flow = {}) {
  return uniqueValues([
    ...(flow.route_history || []).map(event => event.event_id),
    ...(flow.filter_events || []).map(event => event.event_id),
    ...(flow.merge_group_ids || [])
  ].filter(Boolean));
}

function buildRouteEvent({ labelFlow, route, currentProfile, targetProfile, edge, state }) {
  return {
    event_id: nextId(state, 'route', 'route'),
    type: 'routing',
    label_flow_id: labelFlow.label_flow_id,
    edge_id: edge.id || edgeKey(edge),
    source: edge.source,
    source_name: currentProfile.node_name || edge.source,
    target: edge.target,
    target_name: targetProfile.node_name || edge.target,
    state: route.state,
    reason: route.reason,
    confidence: route.confidence
  };
}

function materializeFilterEvents(events, state, labelFlow, edge) {
  return (events || []).map(event => ({
    ...event,
    event_id: nextId(state, 'filter', 'filter'),
    label_flow_id: labelFlow.label_flow_id,
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    edge_id: edge.id || edgeKey(edge),
    source: edge.source,
    target: edge.target
  }));
}

function buildTransition(parent, child, edge, routeEvent, filterEvents) {
  return {
    transition_id: `tr_${shortHash([parent.label_flow_id, child.label_flow_id, edge.id || edgeKey(edge)].join('|'))}`,
    type: 'edge_propagation',
    from_label_flow_id: parent.label_flow_id,
    to_label_flow_id: child.label_flow_id,
    fcg_edge_id: edge.id || edgeKey(edge),
    source: edge.source,
    target: edge.target,
    route_event_id: routeEvent.event_id,
    filter_event_ids: (filterEvents || []).map(event => event.event_id),
    route_state: routeEvent.state,
    route_confidence: routeEvent.confidence
  };
}

function compactRouteEvent(event) {
  return {
    event_id: event.event_id,
    edge_id: event.edge_id,
    source: event.source,
    target: event.target,
    state: event.state,
    reason: event.reason,
    confidence: event.confidence
  };
}

function normalizeLabelFlow(labelFlow) {
  const label = compactLabel(labelFlow.label);
  // 单流设计:每条 label_flow 最多一个父。复数 parent_label_flow_ids 是唯一真值,
  // slice(0,1) 是有意为之(强制单父),不是 bug。parent 仅用于溯源——
  // 当提取/概括等步骤 source_introduction 一个新 label 时,parent 指回上游真源,
  // 使提取/概括步不被误判为源点。
  const parentIds = uniqueValues(labelFlow.parent_label_flow_ids || []).slice(0, 1);
  return {
    ...labelFlow,
    parent_label_flow_ids: parentIds,
    label,
    origin_node: label.origin_node || '',
    origin_node_name: label.origin_node_name || label.origin_node || '',
    introduced_at: label.introduced_at || '',
    merge_group_ids: appendIds([], labelFlow.merge_group_ids || []),
    related_label_flow_ids: appendIds([], labelFlow.related_label_flow_ids || []),
    storage_key: labelFlow.storage_key || '',
    label_fingerprint: `label_${shortHash(`${label.label}:${label.origin_node}:${label.introduced_at}:${label.evidence_kind || ''}`)}`,
    path_fingerprint: `path_${shortHash((labelFlow.node_path || []).join('->') + '|' + (labelFlow.edge_path || []).join('->'))}`
  };
}

function buildNodeFlowSets(labelFlows = []) {
  const byNode = new Map();
  for (const flow of labelFlows || []) {
    if (!flow.current_node) continue;
    if (!byNode.has(flow.current_node)) {
      byNode.set(flow.current_node, {
        node_id: flow.current_node,
        node_name: flow.current_node_name || flow.current_node,
        label_flow_ids: [],
        labels: []
      });
    }
    const item = byNode.get(flow.current_node);
    item.label_flow_ids.push(flow.label_flow_id);
    item.labels.push(flow.label?.label || '');
  }
  return Array.from(byNode.values()).map(item => ({
    node_id: item.node_id,
    node_name: item.node_name,
    label_flow_ids: uniqueValues(item.label_flow_ids).sort(),
    labels: uniqueValues(item.labels).sort()
  })).sort((a, b) => a.node_id.localeCompare(b.node_id));
}

function buildFlowStates(state) {
  return Array.from(state.flowStates.values()).map(item => ({
    state_id: item.state_id,
    representative_label_flow_id: item.representative_label_flow_id,
    node_id: item.node_id,
    node_name: item.node_name,
    label: compactLabel(item.label),
    availability: item.availability,
    storage_key: item.storage_key,
    phase: item.phase,
    origin_ids: item.origin_ids || [],
    provenance_event_ids: item.provenance_event_ids || [],
    path_class_ids: item.path_class_ids || [],
    representative_path_ids: item.representative_path_ids || [],
    label_flow_ids: item.label_flow_ids || [],
    label_flow_id_count: item.label_flow_id_count || 0,
    merged_path_count: item.merged_path_count || 0,
    confidence_min: item.confidence_min,
    confidence_max: item.confidence_max,
    reached_observation_ids: item.reached_observation_ids || []
  })).sort((a, b) => a.state_id.localeCompare(b.state_id));
}

function buildProvenanceStore(state) {
  return {
    origins: Array.from(state.provenanceStore.origins.values()).sort((a, b) => a.origin_id.localeCompare(b.origin_id)),
    path_classes: Array.from(state.provenanceStore.pathClasses.values()).sort((a, b) => a.path_class_id.localeCompare(b.path_class_id)),
    representative_paths: Array.from(state.provenanceStore.representativePaths.values()).sort((a, b) => a.representative_path_id.localeCompare(b.representative_path_id)),
    statistics: {
      origin_count: state.provenanceStore.origins.size,
      path_class_count: state.provenanceStore.pathClasses.size,
      representative_path_count: state.provenanceStore.representativePaths.size
    }
  };
}

function appendLimitedIds(existing = [], additions = [], limit = 64) {
  return uniqueValues([...(existing || []), ...(additions || [])].filter(Boolean)).sort().slice(0, limit);
}

function appendIds(existing = [], additions = []) {
  return uniqueValues([...(existing || []), ...(additions || [])].filter(Boolean)).sort();
}

function appendEventsById(existing = [], additions = [], limit = Infinity) {
  const seen = new Set();
  const result = [];
  for (const event of [...(existing || []), ...(additions || [])]) {
    if (!event) continue;
    const key = event.event_id || event.local_event_key || JSON.stringify(event);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(event);
    if (Number.isFinite(limit) && result.length >= limit) break;
  }
  return result;
}

function uniqueLabelsByFingerprint(labels = []) {
  const seen = new Set();
  const result = [];
  for (const label of labels || []) {
    if (!label) continue;
    const key = [
      label.label || '',
      label.category || '',
      label.subtype || '',
      label.origin_node || '',
      label.introduced_at || ''
    ].join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(label);
  }
  return result;
}

function markTruncated(labelFlow, state, reason) {
  state.truncated = true;
  if (labelFlow) {
    labelFlow.truncated = true;
    labelFlow.termination_reason = labelFlow.termination_reason || reason;
  }
  const event = {
    event_id: nextId(state, 'truncation', 'trunc'),
    type: 'truncation',
    label_flow_id: labelFlow?.label_flow_id || '',
    node_id: labelFlow?.current_node || '',
    reason
  };
  state.truncationEvents.push(event);
  state.allEvents.push(event);
}

function terminateLabelFlow(labelFlow, reason) {
  labelFlow.terminated = true;
  labelFlow.termination_reason = reason;
}

function buildStatistics(state, options) {
  const terminated = state.labelFlows.filter(flow => flow.terminated).length;
  const periodicEvents = state.observationEvents.filter(event => event.leak_type === 'periodic');
  const collapsedFlows = state.labelFlows.filter(flow => flow.cycle_handling === 'collapse').length;
  return {
    label_flow_count: state.labelFlows.length,
    transition_count: state.transitions.length,
    route_event_count: state.routeEvents.length,
    filter_event_count: state.filterEvents.length,
    merge_event_count: state.mergeEvents.length,
    source_introduction_count: state.sourceIntroductions.length,
    truncation_event_count: state.truncationEvents.length,
    terminated_label_flow_count: terminated,
    active_label_flow_count: state.labelFlows.length - terminated,
    periodic_leak_count: periodicEvents.length,
    periodic_leak_severity: {
      steady: periodicEvents.filter(event => event.leak_severity === 'steady').length,
      amplifying: periodicEvents.filter(event => event.leak_severity === 'amplifying').length,
      mutating: periodicEvents.filter(event => event.leak_severity === 'mutating').length
    },
    collapsed_flow_count: collapsedFlows,
    cycle_closure_count: state.cycleClosureCount,
    truncated: state.truncated,
    limits: options
  };
}

function compactLabel(label = {}) {
  if (!label) return null;
  return {
    id: label.id,
    label: label.label,
    category: label.category,
    subtype: label.subtype,
    sensitivity: label.sensitivity,
    field_name: label.field_name,
    field_path: label.field_path,
    origin_node: label.origin_node,
    origin_node_name: label.origin_node_name,
    introduced_at: label.introduced_at,
    mode: label.mode,
    confidence: roundConfidence(label.confidence),
    evidence_level: label.evidence_level,
    evidence_kind: label.evidence_kind,
    evidence_text: label.evidence_text,
    ontology_version: label.ontology_version,
    ontology_label_id: label.ontology_label_id,
    requires_review: Boolean(label.requires_review),
    llm_review: label.llm_review || undefined,
    uncertainty: label.uncertainty || '',
    reason: label.reason || ''
  };
}

function groupEdges(edges, key) {
  const grouped = new Map();
  for (const edge of edges || []) {
    const nodeId = edge?.[key];
    if (!nodeId) continue;
    if (!grouped.has(nodeId)) grouped.set(nodeId, []);
    grouped.get(nodeId).push(edge);
  }
  return grouped;
}

function prioritizeEdgesForObservationCoverage(edges = [], profilesByNode = new Map()) {
  return (edges || [])
    .map((edge, index) => ({ edge, index, priority: observationCoveragePriority(edge, profilesByNode) }))
    .sort((a, b) => a.priority - b.priority || a.index - b.index)
    .map(item => item.edge);
}

function observationCoveragePriority(edge = {}, profilesByNode = new Map()) {
  const targetProfile = profilesByNode.get(edge.target);
  if (!targetProfile) return 100;
  const roles = new Set(targetProfile.node_roles || []);
  const tags = new Set(targetProfile.security_tags || []);
  const boundary = targetProfile.trust_boundary || targetProfile.receiver_scope || targetProfile.data_surface || '';

  if (roles.has('external_egress')) return 0;
  if (boundary === 'external_network' || tags.has('network_egress') || tags.has('webhook_post')) return 1;
  if (roles.has('model_inference') || boundary === 'model_provider') return 2;
  if (roles.has('local_persistence') || targetProfile.retention_scope === 'persistent' || targetProfile.retention_scope === 'external') return 3;
  if (roles.has('tool_invocation')) return 4;
  if (roles.has('command_execution') || roles.has('destructive_operation')) return 5;
  if ((targetProfile.node_roles || []).some(role => SINK_LIKE_ROLES.has(role))) return 6;
  return 20;
}

function mergeTriggerContexts(a = [], b = []) {
  const result = [...a];
  mergeTriggerContextInto(result, b);
  return result;
}


function roundConfidence(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0.3;
  return Math.max(0, Math.min(1, Math.round(n * 1000) / 1000));
}

function normalizeLimits(limits = {}) {
  const envLimits = readLimitEnv();
  const merged = { ...DEFAULT_LIMITS, ...envLimits, ...(limits || {}) };
  if (limits.maxInstances && !limits.maxLabelFlows) merged.maxLabelFlows = limits.maxInstances;
  const normalized = Object.fromEntries(Object.entries(merged).map(([key, value]) => [
    key,
    normalizePositiveLimit(value, DEFAULT_LIMITS[key] || 1)
  ]));
  normalized._explicitMaxLabelFlows = Object.prototype.hasOwnProperty.call(limits || {}, 'maxLabelFlows') ||
    Object.prototype.hasOwnProperty.call(limits || {}, 'maxInstances') ||
    Object.prototype.hasOwnProperty.call(process.env, LIMIT_ENV_KEYS.maxLabelFlows) ||
    Object.prototype.hasOwnProperty.call(process.env, LIMIT_ENV_KEYS.maxInstances);
  return normalized;
}

function readLimitEnv() {
  const result = {};
  for (const [key, envKey] of Object.entries(LIMIT_ENV_KEYS)) {
    if (!Object.prototype.hasOwnProperty.call(process.env, envKey)) continue;
    result[key] = process.env[envKey];
  }
  return result;
}

function normalizePositiveLimit(value, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0) return fallback;
  return Math.floor(n);
}

function nextId(state, key, prefix) {
  state.ids[key] += 1;
  return `${prefix}_${String(state.ids[key]).padStart(6, '0')}`;
}

function edgeKey(edge = {}) {
  return `${edge.source || ''}->${edge.target || ''}`;
}

// 存储读跳的合成边 id。存储读经持久化存储传递、无对应图边,此哨兵仅用于占位以维持
// edge_path 的位置契约。`storage_read:` 前缀确保不与真实图边 id 冲突,消费方按"查不到边"处理。
function storageReadEdgeId(writtenNode = '', readerNode = '') {
  return `storage_read:${writtenNode || ''}->${readerNode || ''}`;
}

function uniqueValues(values = []) {
  return Array.from(new Set(values.filter(Boolean)));
}

module.exports = {
  analyzeGraphTransfers,
  compactLabels,
  dedupeLabels,
  compactLabel
};



