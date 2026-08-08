const { SINK_LIKE_ROLES } = require('./flow-instance-router');

function buildObservations({ nodeProfiles = [], labelFlows = [], observationEvents = [] }) {
  const profilesByNode = new Map((nodeProfiles || []).map(profile => [profile.node_id, profile]));
  const flows = labelFlows || [];
  const byNode = new Map();

  if ((observationEvents || []).length > 0) {
    for (const event of observationEvents || []) {
      // leak_type is part of the key: a periodic observation on a real-cycle lap
      // must not be merged into the plain observation at the same node/step.
      const key = `${event.node_id}|${event.action_step_id || ''}|${event.operation_type || ''}|${event.order || 0}|${event.reason || ''}|${event.leak_type || ''}|${event.leak_severity || ''}`;
      if (!byNode.has(key)) {
        byNode.set(key, { event, labelFlowIds: [] });
      }
      byNode.get(key).labelFlowIds.push(event.label_flow_id);
    }
    return { observations: buildStepObservations(byNode) };
  }

  for (const labelFlow of flows || []) {
    if (!labelFlow?.label) continue;
    const profile = profilesByNode.get(labelFlow.current_node);
    if (!isSinkLikeProfile(profile)) continue;
    if (!byNode.has(profile.node_id)) {
      byNode.set(profile.node_id, { profile, labelFlowIds: [] });
    }
    byNode.get(profile.node_id).labelFlowIds.push(labelFlow.label_flow_id);
  }

  const observations = [];
  for (const { profile, labelFlowIds } of byNode.values()) {
    observations.push({
      observation_id: `obs_${String(observations.length + 1).padStart(6, '0')}`,
      node_id: profile.node_id,
      node_name: profile.node_name,
      node_roles: (profile.node_roles || []).filter(role => SINK_LIKE_ROLES.has(role)),
      security_tags: profile.security_tags || [],
      boundary: {
        data_surface: profile.data_surface,
        receiver_scope: profile.receiver_scope,
        retention_scope: profile.retention_scope, // 留存多久
        trust_boundary: profile.trust_boundary
      },
      label_flow_ids: uniqueValues(labelFlowIds).sort()
    });
  }

  return { observations };
}

function buildStepObservations(byNode) {
  const observations = [];
  for (const { event, labelFlowIds } of byNode.values()) {
    observations.push({
      observation_id: `obs_${String(observations.length + 1).padStart(6, '0')}`,
      node_id: event.node_id,
      node_name: event.node_name,
      node_roles: event.node_roles || [],
      security_tags: event.security_tags || [],
      boundary: event.boundary || {},
      action_step_id: event.action_step_id || '',
      operation_type: event.operation_type || '',
      order: event.order || 0,
      order_confidence: event.order_confidence || 0,
      ambiguous_action_order: Boolean(event.ambiguous_action_order),
      // Periodic-leak classification (empty unless observed on a real-cycle lap).
      leak_type: event.leak_type || '',
      leak_severity: event.leak_severity || '',
      label_flow_ids: uniqueValues(labelFlowIds).sort()
    });
  }
  return observations;
}

function isSinkLikeProfile(profile = {}) {
  return (profile.node_roles || []).some(role => SINK_LIKE_ROLES.has(role));
}

function uniqueValues(values = []) {
  return Array.from(new Set(values.filter(Boolean)));
}

module.exports = {
  buildObservations,
  isSinkLikeProfile
};

