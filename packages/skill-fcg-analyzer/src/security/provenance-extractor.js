const { shortHash } = require('./data-labeler');

function buildProvenanceGraph({
  labelFlows = [],
  transitions = [],
  routeEvents = [],
  filterEvents = [],
  mergeEvents = [],
  observationEvents = [],
  truncationEvents = [],
  observations = [],
  nodesById = new Map()
}) {
  const flows = labelFlows || [];
  return {
    graph_id: `prov_graph_${shortHash([
      flows.length,
      transitions.length,
      observations.length
    ].join('|'))}`,
    label_flow_nodes: flows.map(flow => compactLabelFlow(flow, nodesById)),
    propagation_edges: transitions.map(compactTransition),
    observation_links: observations.flatMap(observation => (observation.label_flow_ids || []).map(labelFlowId => ({
      observation_id: observation.observation_id,
      label_flow_id: labelFlowId,
      node_id: observation.node_id
    }))),
    events: {
      routing: routeEvents.map(compactRouteEvent),
      filtering: filterEvents.map(compactFilterEvent),
      merge: mergeEvents.map(compactMergeEvent),
      observation: observationEvents.map(compactObservationEvent),
      truncation: truncationEvents.map(event => ({ ...event }))
    },
    statistics: {
      label_flow_node_count: flows.length,
      propagation_edge_count: transitions.length,
      observation_link_count: observations.reduce((sum, observation) => sum + (observation.label_flow_ids || []).length, 0),
      routing_event_count: routeEvents.length,
      filtering_event_count: filterEvents.length,
      merge_event_count: mergeEvents.length,
      observation_event_count: observationEvents.length,
      truncation_event_count: truncationEvents.length
    }
  };
}

function compactLabelFlow(flow = {}, nodesById) {
  return {
    label_flow_id: flow.label_flow_id,
    flow_state_id: flow.flow_state_id || '',
    parent_label_flow_ids: flow.parent_label_flow_ids || [],
    current_node: flow.current_node,
    current_node_name: flow.current_node_name || nodesById.get(flow.current_node)?.name || flow.current_node,
    origin_node: flow.origin_node || flow.label?.origin_node || '',
    origin_node_name: flow.origin_node_name || flow.label?.origin_node_name || '',
    introduced_at: flow.introduced_at || flow.label?.introduced_at || '',
    label: flow.label ? {
      label: flow.label.label,
      category: flow.label.category,
      subtype: flow.label.subtype,
      sensitivity: flow.label.sensitivity,
      origin_node: flow.label.origin_node,
      introduced_at: flow.label.introduced_at,
      confidence: flow.label.confidence,
      ontology_version: flow.label.ontology_version,
      ontology_label_id: flow.label.ontology_label_id
    } : null,
    node_path: flow.node_path || [],
    node_names: flow.node_names || [],
    edge_path: flow.edge_path || [],
    trigger_context: flow.trigger_context || [],
    route_event_ids: (flow.route_history || []).map(event => event.event_id),
    filter_event_ids: (flow.filter_events || []).map(event => event.event_id),
    flow_mode: flow.flow_mode || 'may_flow',
    confidence: flow.confidence || 0.3,
    terminated: Boolean(flow.terminated),
    termination_reason: flow.termination_reason || '',
    truncated: Boolean(flow.truncated),
    path_fingerprint: flow.path_fingerprint,
    label_fingerprint: flow.label_fingerprint,
    origin_ids: flow.origin_ids || [],
    provenance_event_ids: flow.provenance_event_ids || [],
    path_class_ids: flow.path_class_ids || [],
    representative_path_ids: flow.representative_path_ids || [],
    merged_path_count: flow.merged_path_count || 1,
    merge_group_ids: flow.merge_group_ids || [],
    related_label_flow_ids: flow.related_label_flow_ids || [],
    storage_key: flow.storage_key || ''
  };
}

function compactTransition(transition = {}) {
  return {
    transition_id: transition.transition_id,
    type: transition.type || 'edge_propagation',
    from_label_flow_id: transition.from_label_flow_id,
    to_label_flow_id: transition.to_label_flow_id,
    fcg_edge_id: transition.fcg_edge_id || '',
    source: transition.source || '',
    target: transition.target || '',
    route_event_id: transition.route_event_id || '',
    filter_event_ids: transition.filter_event_ids || [],
    route_state: transition.route_state || '',
    route_confidence: transition.route_confidence
  };
}

function compactRouteEvent(event = {}) {
  return {
    event_id: event.event_id,
    label_flow_id: event.label_flow_id,
    edge_id: event.edge_id,
    source: event.source,
    target: event.target,
    state: event.state,
    reason: event.reason,
    confidence: event.confidence
  };
}

function compactFilterEvent(event = {}) {
  return {
    event_id: event.event_id,
    label_flow_id: event.label_flow_id,
    parent_label_flow_ids: event.parent_label_flow_ids || [],
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    edge_id: event.edge_id,
    source: event.source,
    target: event.target,
    type: event.type,
    node_id: event.node_id,
    node_name: event.node_name,
    propagated_label: event.propagated_label || null,
    propagated_labels: event.propagated_labels || [],
    introduced_label: event.introduced_label || null,
    introduced_labels: event.introduced_labels || [],
    dropped_label: event.dropped_label || null,
    dropped_labels: event.dropped_labels || [],
    kept_label: event.kept_label || null,
    kept_labels: event.kept_labels || [],
    context_label: event.context_label || null,
    from_label: event.from_label || null,
    produced_object_key: event.produced_object_key || '',
    produced_object_text: event.produced_object_text || '',
    storage_key: event.storage_key || '',
    evidence: event.evidence || ''
  };
}

function compactMergeEvent(event = {}) {
  return {
    event_id: event.event_id,
    type: event.type,
    node_id: event.node_id,
    node_name: event.node_name,
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    label_flow_ids: event.label_flow_ids || [],
    labels: event.labels || [],
    introduced_label: event.introduced_label || null,
    introduced_labels: event.introduced_labels || [],
    evidence: event.evidence || '',
    storage_key: event.storage_key || ''
  };
}

function compactObservationEvent(event = {}) {
  return {
    observation_event_id: event.observation_event_id,
    node_id: event.node_id,
    node_name: event.node_name,
    label_flow_id: event.label_flow_id,
    flow_state_id: event.flow_state_id || '',
    observed_state_ids: event.observed_state_ids || [],
    action_step_id: event.action_step_id || '',
    operation_type: event.operation_type || '',
    order: event.order || 0,
    order_confidence: event.order_confidence || 0,
    ambiguous_action_order: Boolean(event.ambiguous_action_order),
    node_roles: event.node_roles || [],
    security_tags: event.security_tags || [],
    boundary: event.boundary || {},
    reason: event.reason || ''
  };
}

module.exports = {
  buildProvenanceGraph
};

