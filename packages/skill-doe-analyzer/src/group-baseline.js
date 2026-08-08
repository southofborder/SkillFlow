const { round3, categoryFromLabel, subtypeFromLabel } = require('./utils');

function scoreGroupBaseline({ observation = {}, labelFlow = {}, groupBaseline = null }) {
  if (!groupBaseline) {
    return { baseline_adjustment: 0, justification_support: 0, evidence: [] };
  }

  const behaviorKey = buildBehaviorKey({ observation, labelFlow });
  const behavior = lookupBehavior(groupBaseline, behaviorKey);
  if (!behavior) {
    return { baseline_adjustment: 0, justification_support: 0, evidence: [{ kind: 'baseline.no_match', behavior_key: behaviorKey, reason: 'no group baseline behavior matched' }] };
  }

  const supportRatio = normalizeRatio(behavior.support_ratio ?? behavior.supportRatio ?? behavior.ratio);
  const count = Number(behavior.count ?? behavior.support_count ?? behavior.supportCount ?? 0);
  const groupSize = Number(behavior.group_size ?? behavior.groupSize ?? groupBaseline.group_size ?? groupBaseline.groupSize ?? 0);
  let adjustment = 0;
  let justificationSupport = 0;
  let kind = 'baseline.neutral';

  if (supportRatio >= 0.6 || (groupSize > 0 && count / groupSize >= 0.6)) {
    adjustment = -0.08;
    justificationSupport = 0.6;
    kind = 'baseline.majority_support';
  } else if (count === 1 || (supportRatio > 0 && supportRatio <= 0.2)) {
    adjustment = 0.08;
    kind = 'baseline.rare_behavior';
    if (isSensitive(labelFlow.label)) {
      adjustment = 0.12;
      kind = 'baseline.singleton_sensitive_behavior';
    }
  }

  return {
    baseline_adjustment: round3(adjustment),
    justification_support: justificationSupport,
    evidence: [{
      kind,
      behavior_key: behaviorKey,
      support_ratio: round3(supportRatio || (groupSize ? count / groupSize : 0)),
      count,
      group_size: groupSize,
      adjustment: round3(adjustment),
      reason: behavior.reason || ''
    }]
  };
}

function buildBehaviorKey({ observation = {}, labelFlow = {} }) {
  const label = labelFlow.label || {};
  const category = label.category || categoryFromLabel(label.label);
  const subtype = label.subtype || subtypeFromLabel(label.label);
  const boundary = observation.boundary || {};
  return [
    category || 'unknown',
    subtype || 'unknown',
    observation.operation_type || 'unknown_operation',
    boundary.trust_boundary || 'unknown_trust',
    boundary.receiver_scope || 'unknown_receiver'
  ].join('|');
}

function lookupBehavior(groupBaseline, key) {
  if (!groupBaseline) return null;
  if (groupBaseline.behaviors && Object.hasOwn(groupBaseline.behaviors, key)) return groupBaseline.behaviors[key];
  if (Array.isArray(groupBaseline.behaviors)) {
    return groupBaseline.behaviors.find(item => item.behavior_key === key || item.key === key) || null;
  }
  if (groupBaseline.behavior_counts && Object.hasOwn(groupBaseline.behavior_counts, key)) {
    const count = groupBaseline.behavior_counts[key];
    return { count, group_size: groupBaseline.group_size };
  }
  return null;
}

function normalizeRatio(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

function isSensitive(label = {}) {
  const category = label.category || categoryFromLabel(label.label);
  return ['credentials', 'secret_material', 'health', 'biometric', 'special_category', 'financial', 'security_data', 'pii', 'browser_data', 'enterprise', 'unknown_sensitive'].includes(category);
}

module.exports = {
  scoreGroupBaseline,
  buildBehaviorKey
};
