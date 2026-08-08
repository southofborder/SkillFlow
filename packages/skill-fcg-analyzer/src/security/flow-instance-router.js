const SINK_LIKE_ROLES = new Set([
  'external_egress',
  'model_inference',
  'local_persistence',
  'command_execution',
  'destructive_operation',
  'tool_invocation'
]);

function classifyRouteState({
  instance = {},
  currentProfile = {},
  targetProfile = {},
  edge = {},
  // Convergence backstop, not a wall-clock/size cap. The real termination
  // guarantees are !path.includes (acyclic) and revisits < 1 (one-lap cycles);
  // maxDepth only exists to bound a pathological unbounded chain. Kept high (1000
  // hops, unreachable on real skills) so it never truncates a genuine long path.
  // Callers pass options.maxDepth (DEFAULT_LIMITS.maxDepth) which is also 1000.
  maxDepth = 1000
}) {
  const path = Array.isArray(instance.node_path) ? instance.node_path : [];
  const targetNodeId = targetProfile.node_id || edge.target || '';
  const routeText = buildRouteText({ currentProfile, targetProfile, edge });
  // Part 2: precision signal. An explicit negative/conditional guard on the
  // target ("unless redacted", "only if not credential", "without sending")
  // makes an otherwise-definite route conditional. Used to DOWNGRADE definite
  // routes to may_route — never to hard-block, and never fired on absence, so
  // recall is unaffected (we only reduce over-confident definite flows).
  const conditionalGuard = hasNegativeConditionGate(targetProfile);

  if (!targetNodeId) {
    return decision('blocked', 'missing_target', 0.05);
  }

  // Plausible feedback edge — UNCONDITIONALLY absorbed into the cycle's label
  // closure, never traversed, regardless of the arriving flow's path. A feedback
  // edge B->A means "the cycle body loops back to the cycle head"; it must not add
  // a forward reachability B->A, because A is already upstream of B and that
  // reachability is expressed by the forward edges. Blocking it only when
  // path.includes(A) (the old cycle-reentry rule) left it TRAVERSABLE for any flow
  // that reached B without having passed A (e.g. src->X->B), minting paths that do
  // not exist once the cycle is removed — the source of ON's extra flows. The cycle
  // body is handled as a transform operator whose label FIXPOINT CLOSURE is applied
  // for severity/periodic (see graph-transfer-analyzer computeCycleClosure).
  if (edge.is_feedback_edge && edge.feedback_plausibility === 'plausible') {
    return decision('blocked', 'cycle_absorbed_into_closure', 0.1);
  }

  if (path.includes(targetNodeId)) {
    // Ordinary back-edge cycle guard — a non-feedback edge whose target is already
    // on this flow's path would circle the loop. Hard block (acyclic-DAG behavior),
    // byte-identical to the former single-line block for the non-feedback case.
    return decision('blocked', 'cycle_blocked', 0.1);
  }

  if (path.length >= maxDepth) {
    return decision('blocked', 'max_depth', 0.1);
  }

  if (/deny|forbid|block|reject|stop/i.test(routeText)) {
    return decision('blocked', 'explicit_block', 0.2);
  }

  if (edge.type === 'control_flow') {
    // control_flow 边有两类:真携带数据(命令/步骤间传值)与纯顺序(只表达步骤先后,
    // data_flow 是 state>state / context>context / 空占位)。纯顺序边不代表 label 真的
    // 流过去,无差别 definite_route 会让数据标签沿"文档步骤顺序"无脑扩散(实测占
    // control_flow 边的 85%)。故:携带数据 => definite_route;纯顺序 => may_route
    // (保留可达性但标记不确定,不直接 block 以免漏报隐式数据可达)。
    if (controlFlowCarriesData(edge)) {
      if (conditionalGuard) {
        return decision('may_route', 'control_flow_data_conditional', 0.6);
      }
      return decision('definite_route', 'control_flow_data_edge', 0.9);
    }
    return decision('may_route', 'control_flow_order_only', 0.5);
  }

  if (targetProfile.node_roles?.some(role => SINK_LIKE_ROLES.has(role))) {
    if (conditionalGuard) {
      // A guarded sink ("send X unless redacted") is a conditional flow, not a
      // definite one — downgrade so DOE weighs it as uncertain, not certain.
      return decision('may_route', 'sink_like_target_conditional', 0.6);
    }
    return decision('definite_route', 'sink_like_target', 0.85);
  }

  if (isDecisionLikeProfile(targetProfile)) {
    if (/allow|permit|pass|route|branch|when|if\b/i.test(routeText)) {
      return decision('definite_route', 'decision_allowed', 0.75);
    }
    return decision('may_route', 'decision_unknown', 0.55);
  }

  if (currentProfile.node_roles?.includes('control_context') && targetProfile.node_roles?.includes('data_introduction')) {
    return decision('may_route', 'control_triggers_source', 0.7);
  }

  return decision('may_route', 'default_flooding', 0.65);
}

// control_flow 边是否真携带数据。纯顺序边的 data_flow 是占位:state>state、
// context>context、或空参——只表达步骤/命令先后,不传递具体数据。携带真实数据的
// control_flow(如 response/result/instruction > context)才让 label 确定流过去。
// 判据已实测:占位组合覆盖 control_flow 边的 85%,且 100% semantic_reason 含
// sequence/step/order,精度可靠。
const CONTROL_FLOW_PLACEHOLDER_PARAMS = new Set(['', 'state', 'context']);

function controlFlowCarriesData(edge = {}) {
  const df = edge.data_flow || {};
  const from = df.from_param || '';
  const to = df.to_param || '';
  return !(CONTROL_FLOW_PLACEHOLDER_PARAMS.has(from) && CONTROL_FLOW_PLACEHOLDER_PARAMS.has(to));
}

function isDecisionLikeProfile(profile = {}) {
  return Boolean(
    profile.node_roles?.includes('decision') ||
    profile.operation_tags?.includes('routing_decision') ||
    profile.operation_tags?.includes('policy_guard')
  );
}

// Part 2: negative-condition precision gate. Returns true only when the target
// carries an EXPLICIT conditional/negative guard on the flow — a `condition`-
// kind guard ("unless ...", "only if ...", "when ...") or negation ("does not",
// "without sending", "no ... "). Deliberately conservative: absence of
// conditions returns false, so this can only downgrade over-confident definite
// routes, never fabricate a block. Trigger-kind conditions (failure/periodic/
// user_correction/repetition) are NOT treated as flow guards — they describe
// WHEN the action runs, not WHETHER data may flow.
const NEGATIVE_CONDITION_REGEX = /\b(?:unless|only if|except|without|do(?:es)? not|don't|doesn't|never|no longer|must not|cannot|can't|if not|provided that|as long as)\b/i;

function hasNegativeConditionGate(profile = {}) {
  const conditions = Array.isArray(profile.conditions) ? profile.conditions : [];
  for (const cond of conditions) {
    if (!cond || String(cond.type || '') !== 'condition') continue;
    if (NEGATIVE_CONDITION_REGEX.test(String(cond.text || ''))) return true;
  }
  return false;
}

function buildRouteText({ currentProfile = {}, targetProfile = {}, edge = {} }) {
  return [
    currentProfile.node_name,
    targetProfile.node_name,
    targetProfile.description,
    targetProfile.instructionText,
    targetProfile.evidence?.map(item => item.text).join(' '),
    // Part 2: include extracted guard/condition text so the existing deny/allow
    // regexes can also see conditions surfaced from formal_semantics.conditions.
    (targetProfile.conditions || []).map(item => item.text).join(' '),
    edge.semantic_reason,
    edge.data_flow?.from_param,
    edge.data_flow?.to_param,
    edge.data_flow?.data_type
  ].filter(Boolean).join(' ');
}

function decision(state, reason, confidence) {
  return {
    state,
    reason,
    confidence
  };
}

module.exports = {
  classifyRouteState,
  isDecisionLikeProfile,
  controlFlowCarriesData,
  hasNegativeConditionGate,
  SINK_LIKE_ROLES
};
