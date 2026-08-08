const { buildNodeProfiles, buildNodeProfilesWithOptions } = require('./node-profiler');
const { getOntologyStats } = require('./label-ontology');
const { analyzeGraphTransfers } = require('./graph-transfer-analyzer');
const { buildObservations } = require('./observation-analyzer');
const { buildProvenanceGraph } = require('./provenance-extractor');
const { findCrossingViolations } = require('../analyzer/node-splitter');
const { isFeedbackEdge } = require('../analyzer/cycle-remover');

// TEMP diagnostic: env-gated phase timer (FCG_PHASE_TIMING=1). Logs to stderr so
// it never contaminates the JSON on stdout. Zero cost when the env var is unset.
const _PHASE_TIMING = process.env.FCG_PHASE_TIMING === '1';
function _phase(label, startMs, extra) {
  if (!_PHASE_TIMING) return;
  const dur = ((Date.now() - startMs) / 1000).toFixed(2);
  process.stderr.write(`[phase] ${label}: ${dur}s${extra ? ' ' + extra : ''}\n`);
}

// Cycle-breaking feedback edges are retained in the public edges array for
// visualization, but security analysis (role inference, label propagation) must
// run on the acyclic active graph exactly as before, or the broken cycle would
// re-enter propagation.
//
// Two edge sets when cycleExpand is on (see cycle-in-transfer-layer plan):
//   - edgesForProfiles: strip ALL feedback edges (= legacy behavior). Role
//     inference must NOT see re-admitted back-edges — a re-entered edge changes a
//     node's in/out edge set and could perturb role inference
//     (fcg-semantic-reason-role-pollution-fix). Profiles stay on the fully
//     stripped set to hold the 3-component / 5.1 invariants.
//   - edgesForTransfer: strip only IMPLAUSIBLE (fake) feedback edges; keep
//     plausible (real) cycles so the transfer layer can expand them one lap.
// When cycleExpand is off, both collapse to the legacy fully-stripped set —
// byte-identical to pre-feature behavior.
function activeEdges(edges = []) {
  return edges.filter(edge => !isFeedbackEdge(edge));
}

function transferEdges(edges = [], cycleExpand = false) {
  if (!cycleExpand) return activeEdges(edges);
  // Keep real cycles (plausible feedback edges); drop only fake ones.
  return edges.filter(edge => !isFeedbackEdge(edge) || edge.feedback_plausibility === 'plausible');
}

function buildTransferSecurityProfile({ nodes = [], edges = [], cycleExpand = false }) {
  const edgesActive = activeEdges(edges);
  const edgesForTransfer = transferEdges(edges, cycleExpand);
  const nodeProfiles = buildNodeProfiles(nodes, edgesActive);
  return buildProfileFromNodeProfiles({ nodes, edges: edgesActive, edgesForTransfer, nodeProfiles, labelAssistStats: defaultLabelAssistStats(false) });
}

async function buildTransferSecurityProfileAsync({ nodes = [], edges = [], options = {} }) {
  const edgesActive = activeEdges(edges);
  const edgesForTransfer = transferEdges(edges, Boolean(options.cycleExpand));
  const _tAssist = Date.now();
  const result = await buildNodeProfilesWithOptions(nodes, edgesActive, options);
  _phase('1_label_assist(node_profiles)', _tAssist, `profiles=${(result.profiles || []).length}`);
  return buildProfileFromNodeProfiles({
    nodes,
    edges: edgesActive,
    edgesForTransfer,
    nodeProfiles: result.profiles,
    labelAssistStats: result.statistics || defaultLabelAssistStats(Boolean(options.labelLlmAssist))
  });
}

function buildProfileFromNodeProfiles({ nodes = [], edges = [], edgesForTransfer = null, nodeProfiles = [], labelAssistStats = defaultLabelAssistStats(false) }) {
  // Guardrail for the single-crossing invariant enforced by the node splitter.
  // A violation means a node still crosses >1 boundary after splitting (the
  // splitter is deterministic, so this should be empty); warn with node ids
  // rather than trusting the LLM to have split cleanly.
  const crossingViolations = findCrossingViolations(
    nodeProfiles,
    new Map((nodes || []).map(node => [node.id, node]))
  );
  if (crossingViolations.length > 0) {
    console.warn(
      `Warning: ${crossingViolations.length} node(s) violate the single-crossing invariant: ` +
      crossingViolations.map(v => `${v.node_id}[${v.crossing_ops.join('+')}]`).join(', ')
    );
  }

  // Role inference / crossing checks run on the fully-stripped `edges`. Label
  // propagation runs on `edgesForTransfer`, which additionally keeps real cycles
  // when cycleExpand is on (falls back to `edges` for legacy callers).
  const _tFlood = Date.now();
  const transfer = analyzeGraphTransfers({ nodes, edges: edgesForTransfer || edges, nodeProfiles });
  _phase('2_flood(analyzeGraphTransfers)', _tFlood, `flows=${(transfer.label_flows || []).length}`);
  const nodesById = new Map((nodes || []).map(node => [node.id, node]));
  const _tObs = Date.now();
  const observationResult = buildObservations({
    nodeProfiles,
    labelFlows: transfer.label_flows,
    observationEvents: transfer.observation_events,
    nodesById
  });
  _phase('3_observations', _tObs);
  const _tProv = Date.now();
  const provenanceGraph = buildProvenanceGraph({
    labelFlows: transfer.label_flows,
    transitions: transfer.transitions,
    routeEvents: transfer.route_events,
    filterEvents: transfer.filter_events,
    mergeEvents: transfer.merge_events,
    observationEvents: transfer.observation_events,
    truncationEvents: transfer.truncation_events,
    observations: observationResult.observations,
    nodesById
  });
  _phase('4_provenance', _tProv);

  const _tCompact = Date.now();
  const labelDictionary = createLabelDictionary();
  const publicLabelFlows = compactPublicLabelFlows(transfer.label_flows, labelDictionary);
  const publicFlowStates = (transfer.flow_states || []).map(state => compactPublicFlowState(state, labelDictionary));
  _phase('5_compact_public', _tCompact, `public_flows=${publicLabelFlows.length}`);

  return {
    version: '5.1',
    node_profiles: nodeProfiles,
    label_dictionary: labelDictionary.toObject(),
    label_flows: publicLabelFlows,
    flow_states: publicFlowStates,
    provenance_store: compactPublicProvenanceStore(transfer.provenance_store || {}),
    node_flow_sets: transfer.node_flow_sets,
    provenance_graph: compactPublicProvenanceGraph(provenanceGraph),
    observations: observationResult.observations,
    statistics: {
      ...getOntologyStats(),
      node_profile_count: nodeProfiles.length,
      doc_step_node_count: nodes.filter(node => node.semanticKind === 'doc_step').length,
      doc_operation_node_count: nodes.filter(node => node.semanticKind === 'doc_operation').length,
      label_flow_count: transfer.label_flows.length,
      label_dictionary_count: labelDictionary.size,
      flow_state_count: (transfer.flow_states || []).length,
      path_class_count: transfer.provenance_store?.statistics?.path_class_count || 0,
      representative_path_count: transfer.provenance_store?.statistics?.representative_path_count || 0,
      node_flow_set_count: transfer.node_flow_sets.length,
      transition_count: transfer.transitions.length,
      observation_count: observationResult.observations.length,
      observation_event_count: transfer.observation_events.length,
      provenance_label_flow_count: provenanceGraph.statistics.label_flow_node_count,
      provenance_edge_count: provenanceGraph.statistics.propagation_edge_count,
      sink_like_observation_count: observationResult.observations.length,
      truncated: transfer.truncated,
      ...labelAssistStats,
      ...transfer.statistics
    }
  };
}

function compactPublicLabelFlows(flows = [], labelDictionary = null) {
  const flowById = new Map((flows || []).map(flow => [flow.label_flow_id, flow]));
  return (flows || []).map(flow => compactPublicLabelFlow(flow, flowById, labelDictionary));
}

function compactPublicLabelFlow(flow = {}, flowById = new Map(), labelDictionary = null) {
  const routeHistory = (flow.route_history || []).map(compactFlowRouteEvent);
  const localFilterEvents = compactLocalFlowFilterEvents(flow, flowById);
  const allFilterEventIds = uniqueValues(
    (flow.filter_events || [])
      .map(event => event.event_id)
      .filter(Boolean)
  );
  const mergeGroupIds = uniqueValues(flow.merge_group_ids || []);
  const relatedLabelFlowIds = uniqueValues(flow.related_label_flow_ids || []);
  const provenanceEventIds = uniqueValues(flow.provenance_event_ids || []);
  const pathClassIds = uniqueValues(flow.path_class_ids || []);
  const representativePathIds = uniqueValues(flow.representative_path_ids || []);

  return {
    label_flow_id: flow.label_flow_id || '',
    parent_label_flow_ids: uniqueValues(flow.parent_label_flow_ids || []),
    current_node: flow.current_node || '',
    current_node_name: flow.current_node_name || '',
    node_path: [...(flow.node_path || [])],
    node_names: [...(flow.node_names || [])],
    edge_path: [...(flow.edge_path || [])],
    incoming_edge_id: lastValue(flow.edge_path || []),
    ...emitLabelRef(flow.label, labelDictionary),
    trigger_context: compactTriggerContext(flow.trigger_context || []),
    route_event_id: lastValue(routeHistory.map(event => event.event_id).filter(Boolean)),
    route_event_ids: [],
    route_event_id_count: routeHistory.length,
    local_filter_event_ids: localFilterEvents.map(event => event.event_id).filter(Boolean),
    filter_events: [],
    filter_event_ids: [],
    filter_event_id_count: allFilterEventIds.length,
    source_intro_applied_nodes: uniqueValues(flow.source_intro_applied_nodes || []),
    flow_mode: flow.flow_mode || 'may_flow',
    confidence: flow.confidence || 0.3,
    terminated: Boolean(flow.terminated),
    termination_reason: flow.termination_reason || '',
    truncated: Boolean(flow.truncated),
    merge_group_ids: [],
    merge_group_id_count: mergeGroupIds.length,
    merge_group_ids_truncated: false,
    related_label_flow_ids: [],
    related_label_flow_id_count: relatedLabelFlowIds.length,
    related_label_flow_ids_truncated: false,
    parent_label_origin: flow.parent_label_origin || '',
    storage_key: flow.storage_key || '',
    cycle_handling: flow.cycle_handling || '',
    origin_node: flow.origin_node || flow.label?.origin_node || '',
    origin_node_name: flow.origin_node_name || flow.label?.origin_node_name || '',
    introduced_at: flow.introduced_at || flow.label?.introduced_at || '',
    label_fingerprint: flow.label_fingerprint || '',
    path_fingerprint: flow.path_fingerprint || '',
    flow_state_id: flow.flow_state_id || '',
    origin_ids: uniqueValues(flow.origin_ids || []),
    provenance_event_ids: [],
    provenance_event_id_count: provenanceEventIds.length,
    path_class_ids: [],
    path_class_id_count: pathClassIds.length,
    representative_path_ids: representativePathIds,
    representative_path_id_count: representativePathIds.length,
    merged_path_count: flow.merged_path_count || 1
  };
}

function compactPublicFlowState(state = {}, labelDictionary = null) {
  const labelFlowIds = uniqueValues(state.label_flow_ids || []);
  const originIds = uniqueValues(state.origin_ids || []);
  const provenanceEventIds = uniqueValues(state.provenance_event_ids || []);
  const pathClassIds = uniqueValues(state.path_class_ids || []);
  const representativePathIds = uniqueValues(state.representative_path_ids || []);
  return {
    state_id: state.state_id || '',
    representative_label_flow_id: state.representative_label_flow_id || '',
    node_id: state.node_id || '',
    node_name: state.node_name || '',
    ...emitLabelRef(state.label, labelDictionary),
    availability: state.availability || '',
    storage_key: state.storage_key || '',
    phase: state.phase || '',
    origin_ids: originIds,
    origin_id_count: originIds.length,
    provenance_event_ids: [],
    provenance_event_id_count: provenanceEventIds.length,
    path_class_ids: [],
    path_class_id_count: pathClassIds.length,
    representative_path_ids: representativePathIds,
    representative_path_id_count: representativePathIds.length,
    label_flow_id_count: state.label_flow_id_count || labelFlowIds.length,
    label_flow_ids_truncated: false,
    merged_path_count: state.merged_path_count || 0,
    confidence_min: state.confidence_min,
    confidence_max: state.confidence_max,
    reached_observation_ids: uniqueValues(state.reached_observation_ids || [])
  };
}

function compactPublicProvenanceStore(store = {}) {
  return {
    origins: (store.origins || []).map(origin => ({
      origin_id: origin.origin_id || '',
      origin_node: origin.origin_node || '',
      origin_node_name: origin.origin_node_name || '',
      introduced_at: origin.introduced_at || '',
      label: compactLabelRef(origin.label),
      evidence_kind: origin.evidence_kind || '',
      evidence_text: origin.evidence_text || ''
    })),
    path_classes: (store.path_classes || []).map(pathClass => ({
      path_class_id: pathClass.path_class_id || '',
      start_node: pathClass.start_node || '',
      end_node: pathClass.end_node || '',
      label: pathClass.label || '',
      flow_mode: pathClass.flow_mode || '',
      storage_key: pathClass.storage_key || '',
      edge_kind_count: (pathClass.edge_kinds || []).length,
      critical_node_count: uniqueValues(pathClass.critical_nodes || []).length,
      critical_event_count: uniqueValues(pathClass.critical_events || []).length
    })),
    representative_paths: (store.representative_paths || []).map(path => ({
      representative_path_id: path.representative_path_id || '',
      label_flow_id: path.label_flow_id || '',
      parent_label_flow_ids: uniqueValues(path.parent_label_flow_ids || []),
      current_node: path.current_node || '',
      current_node_name: path.current_node_name || '',
      incoming_edge_id: path.incoming_edge_id || '',
      label: compactLabelRef(path.label),
      route_event_ids: [],
      route_event_id_count: uniqueValues(path.route_event_ids || []).length,
      filter_event_ids: [],
      filter_event_id_count: uniqueValues(path.filter_event_ids || []).length,
      merge_group_ids: uniqueValues(path.merge_group_ids || []),
      storage_key: path.storage_key || ''
    })),
    statistics: store.statistics || {}
  };
}

function compactPublicProvenanceGraph(graph = {}) {
  const events = graph.events || {};
  return {
    graph_id: graph.graph_id || '',
    label_flow_nodes: (graph.label_flow_nodes || []).map(compactPublicProvenanceFlow),
    propagation_edges: (graph.propagation_edges || []).map(compactPublicTransition),
    observation_links: graph.observation_links || [],
    events: {
      routing: (events.routing || []).map(compactPublicRouteEvent),
      filtering: (events.filtering || []).map(compactPublicFilterEvent),
      merge: (events.merge || []).map(compactPublicMergeEvent),
      observation: (events.observation || []).map(compactPublicObservationEvent),
      truncation: events.truncation || []
    },
    statistics: graph.statistics || {}
  };
}

function compactPublicProvenanceFlow(flow = {}) {
  return {
    label_flow_id: flow.label_flow_id || '',
    parent_label_flow_ids: uniqueValues(flow.parent_label_flow_ids || []),
    current_node: flow.current_node || '',
    current_node_name: flow.current_node_name || '',
    incoming_edge_id: lastValue(flow.edge_path || []),
    origin_node: flow.origin_node || '',
    introduced_at: flow.introduced_at || '',
    label: compactLabelRef(flow.label),
    flow_mode: flow.flow_mode || 'may_flow',
    confidence: flow.confidence || 0.3,
    terminated: Boolean(flow.terminated),
    termination_reason: flow.termination_reason || '',
    truncated: Boolean(flow.truncated),
    path_fingerprint: flow.path_fingerprint || '',
    label_fingerprint: flow.label_fingerprint || ''
  };
}

function compactPublicTransition(transition = {}) {
  return {
    transition_id: transition.transition_id || '',
    type: transition.type || '',
    from_label_flow_id: transition.from_label_flow_id || '',
    to_label_flow_id: transition.to_label_flow_id || '',
    fcg_edge_id: transition.fcg_edge_id || '',
    source: transition.source || '',
    target: transition.target || '',
    route_event_id: transition.route_event_id || '',
    route_state: transition.route_state || '',
    route_confidence: transition.route_confidence,
    filter_event_ids: uniqueValues(transition.filter_event_ids || [])
  };
}

function compactFlowRouteEvent(event = {}) {
  return {
    event_id: event.event_id || '',
    edge_id: event.edge_id || '',
    state: event.state || ''
  };
}

function compactFlowFilterEvent(event = {}) {
  return {
    event_id: event.event_id || '',
    type: event.type || '',
    operation_type: event.operation_type || '',
    action_step_id: event.action_step_id || '',
    edge_id: event.edge_id || '',
    source: event.source || '',
    target: event.target || '',
    node_id: event.node_id || '',
    node_name: event.node_name || '',
    parent_label_flow_ids: uniqueValues(event.parent_label_flow_ids || []),
    labels: compactEventLabelRefs(event),
    produced_object_text: event.produced_object_text || '',
    produced_object_key: event.produced_object_key || '',
    storage_key: event.storage_key || ''
  };
}

function compactLocalFlowFilterEvents(flow = {}, flowById = new Map()) {
  const currentNode = flow.current_node || '';
  const incomingEdge = lastValue(flow.edge_path || []);
  const parent = flowById.get((flow.parent_label_flow_ids || [])[0] || '');
  const parentEventIds = new Set((parent?.filter_events || []).map(event => event.event_id).filter(Boolean));
  const seen = new Set();
  const localEvents = [];
  for (const event of flow.filter_events || []) {
    if (event.event_id && parentEventIds.has(event.event_id)) continue;
    const isCurrentNode = event.node_id && event.node_id === currentNode;
    const isIncomingEdge = incomingEdge && event.edge_id && event.edge_id === incomingEdge;
    if (!isCurrentNode && !isIncomingEdge) continue;
    const key = event.event_id || event.local_event_key || `${event.type || ''}:${event.node_id || ''}:${event.edge_id || ''}`;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    localEvents.push(compactFlowFilterEvent(event));
  }
  return localEvents;
}

function compactPublicRouteEvent(event = {}) {
  return {
    event_id: event.event_id || '',
    label_flow_id: event.label_flow_id || '',
    edge_id: event.edge_id || '',
    source: event.source || '',
    target: event.target || '',
    state: event.state || '',
    reason: event.reason || '',
    confidence: event.confidence
  };
}

function compactPublicFilterEvent(event = {}) {
  return {
    event_id: event.event_id || '',
    label_flow_id: event.label_flow_id || '',
    parent_label_flow_ids: uniqueValues(event.parent_label_flow_ids || []),
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    edge_id: event.edge_id || '',
    source: event.source || '',
    target: event.target || '',
    type: event.type || '',
    node_id: event.node_id || '',
    node_name: event.node_name || '',
    labels: compactEventLabelRefs(event),
    produced_object_key: event.produced_object_key || '',
    produced_object_text: event.produced_object_text || '',
    storage_key: event.storage_key || '',
    evidence: event.evidence || ''
  };
}

function compactPublicMergeEvent(event = {}) {
  const labelFlowIds = uniqueValues(event.label_flow_ids || []);
  return {
    event_id: event.event_id || '',
    type: event.type || '',
    node_id: event.node_id || '',
    node_name: event.node_name || '',
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    label_flow_ids: labelFlowIds,
    label_flow_id_count: labelFlowIds.length,
    label_flow_ids_truncated: false,
    labels: (event.labels || []).map(compactLabelRef),
    introduced_label: compactLabelRef(event.introduced_label),
    introduced_labels: (event.introduced_labels || []).map(compactLabelRef),
    evidence: event.evidence || '',
    storage_key: event.storage_key || ''
  };
}

function compactPublicObservationEvent(event = {}) {
  return {
    observation_event_id: event.observation_event_id || '',
    observation_id: event.observation_id || '',
    node_id: event.node_id || '',
    node_name: event.node_name || '',
    label_flow_id: event.label_flow_id || '',
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    order: event.order || 0,
    order_confidence: event.order_confidence || 0,
    ambiguous_action_order: Boolean(event.ambiguous_action_order),
    node_roles: event.node_roles || [],
    security_tags: event.security_tags || [],
    boundary: event.boundary || {},
    flow_state_id: event.flow_state_id || '',
    observed_state_ids: uniqueValues(event.observed_state_ids || []),
    leak_type: event.leak_type || '',
    leak_severity: event.leak_severity || '',
    reason: event.reason || ''
  };
}

function compactEventLabelRefs(event = {}) {
  return uniqueByLabel([
    event.propagated_label,
    ...(event.propagated_labels || []),
    event.introduced_label,
    ...(event.introduced_labels || []),
    event.dropped_label,
    ...(event.dropped_labels || []),
    event.kept_label,
    ...(event.kept_labels || []),
    event.context_label,
    event.from_label
  ].filter(Boolean)).map(compactLabelRef);
}

function uniqueByLabel(labels = []) {
  const seen = new Set();
  const result = [];
  for (const label of labels) {
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

/**
 * Produce the label field(s) for a flow/state. With a dictionary, emits a
 * `{ label_id }` reference (and registers the full label once); without one, or
 * when the label has no usable id, falls back to inline `{ label }`. Returning a
 * spread keeps exactly one of label/label_id present, mirroring the DOE reader's
 * "inline wins, else dictionary" precedence.
 */
function emitLabelRef(rawLabel, labelDictionary) {
  const compacted = compactPublicLabel(rawLabel);
  if (!compacted) return { label: null };
  if (!labelDictionary) return { label: compacted }; // legacy direct callers.
  return labelDictionary.register(compacted);
}

function compactPublicLabel(label = null) {
  if (!label) return null;
  return {
    id: label.id || '',
    label: label.label || '',
    category: label.category || '',
    subtype: label.subtype || '',
    sensitivity: label.sensitivity || '',
    field_name: label.field_name || '',
    field_path: label.field_path || '',
    origin_node: label.origin_node || '',
    origin_node_name: label.origin_node_name || '',
    introduced_at: label.introduced_at || '',
    mode: label.mode || '',
    confidence: label.confidence,
    evidence_level: label.evidence_level || '',
    evidence_kind: label.evidence_kind || '',
    evidence_text: label.evidence_text || '',
    ontology_version: label.ontology_version || '',
    ontology_label_id: label.ontology_label_id || '',
    requires_review: Boolean(label.requires_review),
    uncertainty: label.uncertainty || '',
    reason: label.reason || ''
  };
}

/**
 * Label dictionary collector (security_profile >= 5.0). The full label object is
 * stored once per distinct label.id; flows/states emit `label_id` references.
 *
 * Lossless by construction: a label with no usable `id` cannot be a dictionary
 * key, so it is kept INLINE on the flow (and `register` returns null label_id).
 * The DOE reader (label-resolver.js) treats inline as authoritative, so both
 * dictionaried and inline labels round-trip identically.
 */
function createLabelDictionary() {
  const byId = new Map();
  return {
    /**
     * Register a compacted label. Returns { label_id } when it was dictionaried,
     * or { label } when it must stay inline (missing id). Never both.
     */
    register(compacted) {
      if (!compacted) return { label: null };
      const id = compacted.id || '';
      if (!id) return { label: compacted }; // no key -> keep inline, lossless.
      if (!byId.has(id)) {
        byId.set(id, compacted);
      }
      // Defensive: if the same id ever carried different content we would lose
      // the variant. Verified 1:1 on real data, but assert it so a future
      // regression surfaces loudly instead of silently dropping a label.
      return { label_id: id };
    },
    toObject() {
      return Object.fromEntries(byId);
    },
    get size() {
      return byId.size;
    }
  };
}

function compactLabelRef(label = null) {
  if (!label) return null;
  return {
    label: label.label || '',
    category: label.category || '',
    subtype: label.subtype || '',
    sensitivity: label.sensitivity || '',
    origin_node: label.origin_node || '',
    introduced_at: label.introduced_at || '',
    confidence: label.confidence
  };
}

function compactTriggerContext(items = []) {
  return (items || []).map(item => ({
    node_id: item.node_id || '',
    node_name: item.node_name || '',
    reason: item.reason || ''
  }));
}

function uniqueValues(values = []) {
  return Array.from(new Set((values || []).filter(Boolean)));
}

function lastValue(values = []) {
  return Array.isArray(values) && values.length ? values[values.length - 1] : '';
}

function defaultLabelAssistStats(enabled) {
  return {
    ...getOntologyStats(),
    label_llm_assist_enabled: Boolean(enabled),
    label_llm_candidate_count: 0,
    label_llm_accepted_count: 0,
    label_llm_cache_hit_count: 0,
    label_llm_error_count: 0,
    label_llm_ignored_count: 0
  };
}

module.exports = {
  buildTransferSecurityProfile,
  buildTransferSecurityProfileAsync
};
