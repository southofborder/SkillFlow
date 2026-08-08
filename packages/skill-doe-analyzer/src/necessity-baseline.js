const {
  buildLabelTerms,
  overlapScore,
  normalizeText
} = require('./necessity-text-utils');
const { createFlowPathContext, resolveLabelFlowPath } = require('./flow-path-utils');
const { round3, clamp, categoryFromLabel } = require('./utils');

const COMPONENT_KEYS = [
  'action_input_need',
  'receiver_semantic_need',
  'task_need'
];

const TASK_STOPWORDS = new Set([
  'a', 'an', 'the', 'to', 'into', 'in', 'on', 'for', 'from', 'of', 'and', 'or', 'then',
  'with', 'by', 'as', 'it', 'this', 'that', 'these', 'those', 'use', 'using', 'skill',
  'tool', 'data', 'content', 'input', 'output', 'result', 'results', 'user', 'query',
  'when', 'if', 'after', 'before', 'only', 'should', 'must', 'can', 'will'
]);

function createNecessityContext(fcg = {}) {
  const nodeById = new Map((fcg.nodes || []).map(node => [node.id, node]));
  // v6 flow_states carry the decision-unit summary (transform_digest / origin_boundary).
  // Indexed by state_id so a label_flow resolves its own summary via flow_state_id
  // — the structural necessity signals (transform participation, origin class) read
  // this instead of walking the parent chain (necessity redesign, milestone N).
  const security = fcg.security_profile || {};
  const flowStateById = new Map((security.flow_states || []).map(s => [s.state_id, s]));
  return {
    fcg,
    nodeById,
    flowStateById,
    taskText: buildTaskContextText(fcg),
    taskTokens: null,
    taskKeywordTokens: null,
    labelTermsByLabel: new Map(),
    keywordTokensBySource: new Map(),
    termTokenCache: new Map(),
    actionTextByNodeId: new Map(),
    nodeTextById: new Map(),
    schemaTextByNodeId: new Map(),
    receiverTextByNodeId: new Map(),
    nodeTaskTextByNodeId: new Map(),
    flowTextByFlowId: new Map(),
    flowPathContext: createFlowPathContext(fcg),
    tokenCache: new Map(),
    overlapCache: new Map(),
    keywordOverlapCache: new Map()
  };
}

function scoreNecessityBaseline({ fcg = {}, observation = {}, labelFlow = {}, nodeProfile = {}, groupSupport = null, context = null }) {
  const necessityContext = context || createNecessityContext(fcg);
  const label = labelFlow.label || {};
  const labelTerms = getCachedLabelTerms(necessityContext, label);
  const taskText = necessityContext.taskText || buildTaskContextText(fcg);
  const actionText = getCachedActionText(necessityContext, { fcg, observation, nodeProfile });
  const receiverText = getCachedReceiverText(necessityContext, { observation, nodeProfile, actionText });
  const flowText = getCachedFlowPathText(necessityContext, { fcg, labelFlow });
  const nodeTaskText = getCachedNodeTaskText(necessityContext, { observation, actionText, receiverText });

  const actionInput = scoreActionInputNeed({ label, labelTerms, actionText, nodeProfile, observation, labelFlow, context: necessityContext });
  const receiverNeed = scoreReceiverSemanticNeed({ label, labelTerms, receiverText, observation, nodeProfile, labelFlow, context: necessityContext });
  const flowTask = scoreFlowPathTaskNeed({ label, labelTerms, taskText, flowText, labelFlow, context: necessityContext });
  const boundaryNode = scoreBoundaryNodeTaskNeed({ labelTerms, taskText, nodeTaskText, observation, nodeProfile, groupSupport, context: necessityContext });

  // Global necessity is a single component: the whole label_flow path AND the
  // boundary node must both belong to the task. Conjunction = min, so this is
  // numerically identical to the old separate flow_path_task_need /
  // boundary_node_task_need pair under componentMin, but it is one question for
  // the LLM (less evidence, smaller schema) and one score downstream.
  const taskNeedScore = Math.min(flowTask.score, boundaryNode.score);

  const componentScores = normalizeComponentScores({
    action_input_need: actionInput.score,
    receiver_semantic_need: receiverNeed.score,
    task_need: taskNeedScore
  });

  const necessityScore = componentMin(componentScores);

  return {
    necessity_score: necessityScore,
    component_scores: componentScores,
    local_necessity: {
      action_input_need: componentScores.action_input_need,
      receiver_semantic_need: componentScores.receiver_semantic_need,
      score: round3(Math.min(componentScores.action_input_need, componentScores.receiver_semantic_need))
    },
    global_necessity: {
      task_need: componentScores.task_need,
      // Sub-signals retained for transparency/debugging; they no longer form
      // separate scored components but explain how task_need was derived.
      flow_path_signal: round3(flowTask.score),
      boundary_node_signal: round3(boundaryNode.score),
      score: componentScores.task_need
    },
    necessity_basis: weakestComponent(componentScores),
    evidence: [
      evidence('necessity.local.action_input_need', actionInput.score, actionInput.reason),
      evidence('necessity.local.receiver_semantic_need', receiverNeed.score, receiverNeed.reason),
      evidence('necessity.global.task_need', taskNeedScore,
        `flow_path_signal=${round3(flowTask.score)} (${flowTask.reason}); boundary_node_signal=${round3(boundaryNode.score)} (${boundaryNode.reason})`)
    ]
  };
}

function getCachedActionText(context = {}, args = {}) {
  const nodeId = args.observation?.node_id || args.nodeProfile?.node_id || '';
  const profileKey = [
    nodeId,
    args.nodeProfile?.node_name || '',
    args.observation?.operation_type || '',
    (args.observation?.security_tags || []).join(','),
    (args.nodeProfile?.security_tags || []).join(',')
  ].join('|');
  if (context.actionTextByNodeId?.has(profileKey)) return context.actionTextByNodeId.get(profileKey);
  const text = buildActionText({ ...args, nodeById: context.nodeById });
  context.actionTextByNodeId?.set(profileKey, text);
  return text;
}

function getCachedLabelTerms(context = {}, label = {}) {
  const key = label.label || [label.category, label.subtype, label.field_name].filter(Boolean).join('.');
  if (context.labelTermsByLabel?.has(key)) return context.labelTermsByLabel.get(key);
  const terms = buildLabelTerms(label);
  context.labelTermsByLabel?.set(key, terms);
  return terms;
}

function getCachedFlowPathText(context = {}, args = {}) {
  const key = args.labelFlow?.label_flow_id || stableFlowKey(args.labelFlow || {});
  if (context.flowTextByFlowId?.has(key)) return context.flowTextByFlowId.get(key);
  const text = buildFlowPathText({
    ...args,
    nodeById: context.nodeById,
    nodeTextById: context.nodeTextById,
    flowPathContext: context.flowPathContext
  });
  context.flowTextByFlowId?.set(key, text);
  return text;
}

function getCachedSchemaText(context = {}, { observation = {}, nodeProfile = {} }) {
  const key = observation.node_id || nodeProfile.node_id || nodeProfile.node_name || '';
  if (context.schemaTextByNodeId?.has(key)) return context.schemaTextByNodeId.get(key);
  const text = normalizeText([
    safeJson(nodeProfile.formal_semantics?.inputs || []),
    safeJson(nodeProfile.formal_semantics?.targets || []),
    safeJson(nodeProfile.formal_semantics?.outputs || []),
    safeJson(nodeProfile.data_profile || {})
  ].join(' '));
  context.schemaTextByNodeId?.set(key, text);
  return text;
}

function getCachedReceiverText(context = {}, { observation = {}, nodeProfile = {}, actionText = '' }) {
  const key = [
    observation.node_id || nodeProfile.node_id || '',
    observation.operation_type || '',
    safeJson(observation.boundary || {}),
    (observation.security_tags || []).join(','),
    (nodeProfile.security_tags || []).join(',')
  ].join('|');
  if (context.receiverTextByNodeId?.has(key)) return context.receiverTextByNodeId.get(key);
  const text = buildReceiverText({ observation, nodeProfile, actionText });
  context.receiverTextByNodeId?.set(key, text);
  return text;
}

function getCachedNodeTaskText(context = {}, { observation = {}, actionText = '', receiverText = '' }) {
  const key = observation.node_id || `${hashString(actionText)}:${hashString(receiverText)}`;
  if (context.nodeTaskTextByNodeId?.has(key)) return context.nodeTaskTextByNodeId.get(key);
  const text = normalizeText([actionText, receiverText].join(' '));
  context.nodeTaskTextByNodeId?.set(key, text);
  return text;
}

// Sink operation_type -> does the sink inherently CONSUME the arriving label as
// action input? (necessity redesign N1, replacing the brittle word-bag). These
// ops all act ON the data that reaches them, so the label is their input payload:
//   model_inference — feeds the label to the model
//   external_egress — sends the label out (it IS the payload)
//   command_execution / invoke_tool — passes the label as an argument
//   write — persists the label (it is the written content)
// `read` PRODUCES data rather than consuming the flowing label, so it does not
// establish input-need for the arriving label. Unknown ops fall to neutral.
const ACTION_INPUT_OP_BASELINE = {
  model_inference: 0.85,
  external_egress: 0.8,
  command_execution: 0.8,
  invoke_tool: 0.8,
  write: 0.7,
  read: 0.15
};

// Did the SINK node itself apply a real transform to THIS label? The flow_state's
// ordered transform_digest ends with the most-recent transform; a non-empty
// transform_sig on a flow reaching a transform/egress sink means the sink consumed
// and reshaped the label (redact/slice/summarize/aggregate/...). That is direct
// structural proof the label is a needed input — the strongest signal, and the one
// the word-bag missed on 522 units (transform happened, yet it scored the 0.05
// floor because the label's NAME did not appear in the action text).
function sinkTransformedLabel({ labelFlow = {}, context = null }) {
  const stateId = labelFlow.flow_state_id || '';
  if (!stateId || !context?.flowStateById) return false;
  const state = context.flowStateById.get(stateId);
  if (!state) return false;
  const sig = String(state.transform_sig || 'none');
  return sig !== 'none' && sig.length > 0;
}

// Schema membership: when the sink declares formal inputs, does THIS label's
// field/subtype/category actually appear among them? Sparse in practice (only ~3%
// of checkable units hit), so it is used as a strong POSITIVE signal (member => the
// sink explicitly takes it) and a mild negative (declared inputs but absent => the
// label is structurally not among the declared inputs). Returns 1 / 0.2 / null.
function schemaInputMembership({ label = {}, observation = {}, context = null }) {
  const node = context?.nodeById?.get?.(observation.node_id) || {};
  const fs2 = node.formal_semantics || {};
  const inputs = fs2.inputs || [];
  if (!inputs.length) return null;
  const needles = [label.field_name, label.field_path, label.subtype, label.category, label.label]
    .filter(Boolean).map(s => normalizeText(String(s)));
  const hay = normalizeText(inputs.map(i => `${i.name || ''} ${i.type || ''}`).join(' '));
  const hit = needles.some(n => n && (hay.includes(n) || n.split(/\s+/).some(t => t && hay.includes(t))));
  return hit ? 1 : 0.2;
}

function scoreActionInputNeed({ label = {}, labelTerms = [], actionText = '', nodeProfile = {}, observation = {}, labelFlow = {}, context = null }) {
  const op = String(observation.operation_type || '').toLowerCase();
  const opBaseline = ACTION_INPUT_OP_BASELINE[op];

  // (1) Transform participation — strongest, direct proof the sink consumed it.
  const transformed = sinkTransformedLabel({ labelFlow, context });

  // (2) Schema membership — strong positive when the sink declares inputs.
  const schemaMember = schemaInputMembership({ label, observation, context });

  // (3) Word-bag matches retained as floor-raising signals (never the sole driver).
  const schemaText = getCachedSchemaText(context || {}, { observation, nodeProfile });
  const schemaMatch = cachedOverlapScore(context, labelTerms, schemaText);
  const actionMatch = cachedOverlapScore(context, labelTerms, actionText);

  const candidates = [
    0.05, // hard floor unchanged
    transformed ? 0.9 : 0,
    opBaseline || 0,
    schemaMember === 1 ? 0.95 : 0,
    0.95 * schemaMatch,
    0.85 * actionMatch
  ];
  let score = Math.max(...candidates);
  // Structural negative DOMINATES the op-baseline: when the sink DECLARES its
  // formal inputs and this label is NOT among them, the sink structurally does not
  // take this label as input — even for an egress/exec op whose generic baseline is
  // high. Only a direct transform of THIS label (the sink demonstrably reshaped it)
  // or an explicit lexical hit overrides. This is the "weather API declares {city},
  // so a pii.email arriving here is not a needed input" case. The op-baseline only
  // carries weight when the sink does NOT declare inputs (schemaMember === null).
  if (schemaMember === 0.2 && !transformed) {
    const lexicalHit = Math.max(0.95 * schemaMatch, 0.85 * actionMatch);
    score = Math.max(0.05, Math.min(score, 0.25), lexicalHit >= 0.7 ? lexicalHit : 0);
  }

  return {
    score: clamp(round3(score)),
    reason: `op=${op || 'unknown'}(base=${round3(opBaseline || 0)}); transformed=${transformed}; schema_member=${schemaMember}; schema_match=${round3(schemaMatch)}; action_match=${round3(actionMatch)}`
  };
}

// (receiver_scope × label.category) semantic compatibility (necessity redesign N2,
// replacing the word-bag + hardcoded-trust heuristics). The question: does THIS
// receiver type legitimately need THIS category of data? High = the receiver
// expects/consumes it; low = the receiver has no semantic business with it (a DOE
// signal). Grounded in the real corpus receiver/category distribution.
//   model_provider (LLM)     — consumes context/prompts/documents/summaries to
//                              reason; credentials/pii/financial have no place in a
//                              prompt.
//   third_party_service      — narrowest trust: only the specific payload the
//                              service needs; secrets/pii/browser_data leaking here
//                              is the classic over-exposure.
//   first_party_service      — own backend, broader than third-party but still
//                              scoped.
//   local_runtime            — stays on the local process; most categories are fine
//                              (not really an external receiver — exposure already
//                              gated boundary_crossed upstream).
const RECEIVER_CATEGORY_COMPAT = {
  model_provider: {
    ai_context: 0.85, user_prompt: 0.85, file_content: 0.7, aggregate_data: 0.75,
    database_record: 0.55, communication: 0.5, location: 0.5,
    credentials: 0.05, secret_material: 0.05, pii: 0.2, financial: 0.1,
    health: 0.15, browser_data: 0.15, biometric: 0.1
  },
  third_party_service: {
    file_content: 0.45, aggregate_data: 0.5, location: 0.55, ai_context: 0.3,
    user_prompt: 0.35, database_record: 0.4, communication: 0.4,
    credentials: 0.08, secret_material: 0.05, pii: 0.15, financial: 0.15,
    health: 0.1, browser_data: 0.1, biometric: 0.08
  },
  first_party_service: {
    file_content: 0.6, aggregate_data: 0.6, location: 0.6, ai_context: 0.5,
    user_prompt: 0.55, database_record: 0.65, communication: 0.55,
    credentials: 0.35, secret_material: 0.2, pii: 0.45, financial: 0.5,
    health: 0.3, browser_data: 0.3, biometric: 0.25
  },
  local_runtime: {
    // local stays local; generically higher (need-satisfied), even for secrets a
    // local process legitimately uses them. Category floor 0.55 via fallback.
  }
};
const RECEIVER_DEFAULT_COMPAT = {
  model_provider: 0.4, third_party_service: 0.3,
  first_party_service: 0.5, local_runtime: 0.6
};
// Trust boundary → receiver_scope backfill when receiver_scope is unset/unknown.
const TRUST_TO_RECEIVER = {
  model_provider: 'model_provider', external_network: 'third_party_service',
  persistent_storage: 'first_party_service', local_process: 'local_runtime'
};

function receiverCompatBase(receiver, category) {
  const table = RECEIVER_CATEGORY_COMPAT[receiver];
  if (table && Object.hasOwn(table, category)) return table[category];
  return RECEIVER_DEFAULT_COMPAT[receiver] ?? 0.35;
}

function scoreReceiverSemanticNeed({ label = {}, labelTerms = [], receiverText = '', observation = {}, nodeProfile = {}, labelFlow = {}, context = null }) {
  const boundary = observation.boundary || {};
  const trust = String(boundary.trust_boundary || '').toLowerCase();
  let receiver = String(boundary.receiver_scope || '').toLowerCase();
  if (!RECEIVER_CATEGORY_COMPAT[receiver]) receiver = TRUST_TO_RECEIVER[trust] || receiver;
  const category = label.category || categoryFromLabel(label.label);

  // (1) Structural base: does this receiver type semantically need this category?
  let score = receiverCompatBase(receiver, category);

  // (2) Reduction-before-egress (read flow_state): if the data was redacted/
  // aggregated/pseudonymized/sliced BEFORE reaching this receiver, the receiver
  // gets a PROTECTED form. This is a MILD prior only — whether the SPECIFIC
  // reductions applied (state.reduction_profile) are sufficient to defend sending
  // THIS label to THIS receiver is a semantic judgement, delegated to the LLM judge
  // (which reads sink_boundary.reduction_before_egress = the same antichain). The
  // rule layer must not clear a flag on reduction alone, so the raise is small and
  // capped at 0.6 — strictly below the 0.70 necessity flag threshold. A reduction
  // can nudge a borderline case up, never mechanically exempt a real exposure; the
  // LLM does the sufficiency call. reduction_applied == bool(reduction_profile).
  const state = labelFlow.flow_state_id && context?.flowStateById
    ? context.flowStateById.get(labelFlow.flow_state_id) : null;
  const reductionProfile = (state && state.reduction_profile) || [];
  const reduced = reductionProfile.length > 0;
  if (reduced) score = Math.max(score, Math.min(0.6, score + 0.1));

  // (3) origin_class combination (read flow_state.origin_boundary): user's own
  // input flowing back to a user-visible/first-party receiver is expected (raise);
  // third-party-sourced data going to a different third party is less defensible.
  // origin trust values (observed): user_visible / local_process / external_network
  // / persistent_storage. User-originated data (user_visible) returning to a first-
  // party backend or user-visible surface is expected; raise its defensibility.
  const originTrust = state?.origin_boundary?.trust_boundary || '';
  if (originTrust === 'user_visible' && (receiver === 'first_party_service' || trust === 'local_process')) {
    score = Math.max(score, 0.6);
  }

  // (4) Lexical corroboration retained as a mild raise only (never the sole driver):
  // if the label terms actually appear in the receiver text, that supports need.
  const receiverMatch = cachedOverlapScore(context, labelTerms, receiverText);
  if (receiverMatch > 0.5) score = Math.max(score, 0.5 * receiverMatch + 0.3);

  return {
    score: clamp(round3(Math.max(0.03, score))),
    reason: `receiver=${receiver}; category=${category}; compat_base=${round3(receiverCompatBase(receiver, category))}; reduced=${reduced}${reduced ? `(${reductionProfile.join('+')})` : ''}; receiver_match=${round3(receiverMatch)}`
  };
}

// Synthesized builtin nodes (llm.inference, user.query) are undeclared by
// construction — the analyzer creates them, they are not doc steps. On a flow path
// they are structural, not "unaccounted-for routing", so declaration-coverage must
// treat them as legitimate (necessity redesign N3, N0 found EVERY non-declared path
// node was one of these two — no genuine off-task node existed in the corpus).
const SYNTHESIZED_NODE_NAMES = new Set(['llm.inference', 'user.query']);

function isTaskLegitimateNode(node = {}) {
  if (!node) return false;
  if (isTaskContextNode(node)) return true;
  if (node.type === 'builtin_call' && SYNTHESIZED_NODE_NAMES.has(node.name)) return true;
  return false;
}

// Declaration coverage: of the path's nodes that carry a semanticKind (i.e. came
// from real FCG extraction, not a bare test fixture), how many are task-legitimate
// (declared doc step OR synthesized builtin)? Returns { cov, graded } where graded
// is false when NO path node carries semanticKind (so the caller falls back to the
// lexical signal — hand-built fixtures, older FCG versions).
function pathDeclarationCoverage(labelFlow, context) {
  const nodeById = context?.nodeById;
  if (!nodeById) return { cov: 0, graded: false };
  const fpc = context.flowPathContext || createFlowPathContext(context.fcg || {});
  const resolved = resolveLabelFlowPath(labelFlow, fpc);
  const nodePath = resolved.node_path || [];
  let kinded = 0;
  let legit = 0;
  for (const id of nodePath) {
    const node = nodeById.get(id) || {};
    if (!node.semanticKind && node.type !== 'builtin_call') continue; // no structural signal on this node
    kinded += 1;
    if (isTaskLegitimateNode(node)) legit += 1;
  }
  if (!kinded) return { cov: 0, graded: false };
  return { cov: legit / kinded, graded: true, kinded, legit };
}

function scoreFlowPathTaskNeed({ label = {}, labelTerms = [], taskText = '', flowText = '', labelFlow = {}, context = null }) {
  const taskLabelMatch = cachedOverlapScore(context, labelTerms, taskText);
  const taskPathMatch = cachedKeywordOverlap(context, taskText, flowText);
  const flowMode = String(labelFlow.flow_mode || '');
  const storageBridgeSupport = flowMode === 'storage_read' || Boolean(labelFlow.storage_key);

  // Structural signal (N3): when path nodes carry semanticKind, a fully task-
  // legitimate path (all declared steps and/or synthesized builtins) IS on the
  // declared task flow — high task_need floor. A path diluted by nodes that are
  // neither declared nor synthesized lowers it proportionally.
  const dc = pathDeclarationCoverage(labelFlow, context);
  const structural = dc.graded ? dc.cov : 0;

  // Lexical signal retained for fixtures/older FCG lacking semanticKind, and as a
  // corroborating floor.
  let lexical = Math.max(taskLabelMatch, taskPathMatch);
  if (storageBridgeSupport && /save|store|persist|memory|database|file|report|summary/i.test(taskText)) {
    lexical = Math.max(lexical, 0.65);
  }
  if (isDerivedSummaryLabel(label) && /summary|summariz|digest|report|brief/i.test(taskText)) {
    lexical = Math.max(lexical, 0.8);
  }

  // Structural coverage, when available, is the stronger evidence the path belongs
  // to the task; take the max so a declared path is not penalized by lexical misses
  // (the 522-false-floor lesson applied to task_need). Lexical still lifts fixtures.
  const score = dc.graded ? Math.max(structural, lexical) : lexical;
  return {
    score: clamp(round3(score || 0.05)),
    reason: `structural_cov=${round3(structural)}(graded=${dc.graded}); task_label_match=${round3(taskLabelMatch)}; task_path_match=${round3(taskPathMatch)}; flow_mode=${flowMode || 'unknown'}`
  };
}

function scoreBoundaryNodeTaskNeed({ labelTerms = [], taskText = '', nodeTaskText = '', observation = {}, nodeProfile = {}, groupSupport = null, context = null }) {
  const taskNodeMatch = cachedKeywordOverlap(context, taskText, nodeTaskText);
  const labelNodeMatch = cachedOverlapScore(context, labelTerms, nodeTaskText);
  const groupSupportScore = Number(groupSupport?.justification_support || 0);
  let score = Math.max(taskNodeMatch, groupSupportScore);

  // Structural signal (N3): is the boundary (sink) node itself a declared task
  // step, or a synthesized builtin (llm.inference/user.query)? A declared sink IS
  // part of the task by construction — high floor. This is the "boundary node
  // belongs to the task" half of task_need, replacing pure lexical matching.
  const sinkNode = context?.nodeById?.get?.(observation.node_id) || {};
  const sinkLegit = isTaskLegitimateNode(sinkNode);
  if (sinkLegit) score = Math.max(score, 0.7);

  const boundary = observation.boundary || {};
  const trust = String(boundary.trust_boundary || '').toLowerCase();
  const text = normalizeText(nodeTaskText);
  const task = normalizeText(taskText);
  if (taskNodeMatch > 0.15 && labelNodeMatch > 0) {
    score = Math.max(score, Math.min(0.45, 0.2 + (0.25 * labelNodeMatch)));
  }
  const explicitTaskSink = /email|mail|weather|calendar|payment|search|api|summary|summariz|save|store|report|document|artifact|model|llm/i.test(text) &&
    cachedKeywordOverlap(context, taskText, text) > 0;
  if (explicitTaskSink) score = Math.max(score, 0.75);
  if (trust === 'model_provider' && isTransformLike(nodeProfile, observation) && cachedKeywordOverlap(context, taskText, text) > 0) {
    score = Math.max(score, 0.75);
  }
  // Generic-sink penalty is applied LAST and caps regardless of the structural
  // floor: a webhook/analytics/telemetry/log sink NOT named in the task is off-task
  // even if it is a declared step — this is the classic "declared but exfiltrating
  // to analytics" case. Preserved from the word-bag design (tests assert <=0.12).
  const genericBoundarySink = /webhook|analytics|telemetry|callback|log/i.test(text);
  const taskDeclaresGenericSink = /webhook|analytics|telemetry|callback|log/i.test(task);
  if (genericBoundarySink && !taskDeclaresGenericSink) {
    score = Math.min(score, 0.12);
  }

  return {
    score: clamp(round3(score || 0.05)),
    reason: `sink_legit=${sinkLegit}; task_node_match=${round3(taskNodeMatch)}; label_node_match=${round3(labelNodeMatch)}; group_support=${round3(groupSupportScore)}`
  };
}

function scoreTransformNeed({ label = {}, labelTerms = [], actionText = '', nodeProfile = {}, observation = {}, context = null }) {
  const text = String(actionText || '');
  const transformIntent = isTransformLike(nodeProfile, observation) ||
    /\b(summariz|summary|digest|brief|classif|extract|parse|analyz|reason|review)\b/i.test(text);
  if (!transformIntent) return 0;
  const match = cachedOverlapScore(context, labelTerms, text);
  if (match > 0) return Math.max(0.65, match);
  if (/\b(summary|summariz|digest|brief)\b/i.test(text) && ['communication', 'file_content', 'database_record', 'aggregate_data'].includes(label.category)) {
    return 0.8;
  }
  return 0.35;
}

function buildTaskContextText(fcg = {}) {
  const taskNodes = (fcg.nodes || [])
    .filter(isTaskContextNode)
    .slice(0, 80);
  return normalizeText([
    fcg.meta?.skill_name,
    fcg.meta?.skill_version,
    fcg.skill?.name,
    fcg.skill?.description,
    fcg.description,
    fcg.readme,
    fcg.readmeText,
    JSON.stringify(fcg.documentation_context || {}),
    ...taskNodes.map(node => [
      node.name,
      node.description,
      node.instructionText,
      node.ownerScript,
      node.functionName,
      node.callee,
      JSON.stringify(node.semantic_gate || {}),
      JSON.stringify(node.source_context || {}),
      node.formal_semantics?.operation_type,
      JSON.stringify(node.formal_semantics?.targets || []),
      JSON.stringify(node.formal_semantics?.inputs || []),
      JSON.stringify(node.formal_semantics?.outputs || [])
    ].filter(Boolean).join(' '))
  ].filter(Boolean).join(' '));
}

function isTaskContextNode(node = {}) {
  const semanticKind = String(node.semanticKind || '').toLowerCase();
  if ([
    'doc_step',
    'doc_operation',
    'doc_definition',
    'doc_schema',
    'doc_example',
    'doc_template',
    'trigger',
    'policy',
    'script_entry',
    'script_function'
  ].includes(semanticKind)) return true;
  const file = String(node.location?.file || node.ownerDoc || '').toLowerCase();
  const hasDocAction = Boolean(node.docAction || (Array.isArray(node.docActions) && node.docActions.length));
  return hasDocAction && (file.includes('skill.md') || file.includes('readme.md'));
}

function buildActionText({ fcg = {}, observation = {}, nodeProfile = {}, nodeById = null }) {
  const node = nodeById?.get?.(observation.node_id) || (fcg.nodes || []).find(item => item.id === observation.node_id) || {};
  const semantics = nodeProfile.formal_semantics || node.formal_semantics || {};
  return normalizeText([
    observation.node_name,
    nodeProfile.node_name,
    node.name,
    node.description,
    node.instructionText,
    node.ownerScript,
    node.functionName,
    node.callee,
    node.semantic_gate?.classification,
    node.semantic_gate?.actionability,
    node.semantic_gate?.completed_sentence,
    node.semantic_gate?.reason,
    node.source_context?.source_line,
    node.source_context?.section,
    node.source_context?.action_evidence?.snippet,
    node.source_context?.action_evidence?.trigger,
    nodeProfile.instructionText,
    semantics.operation_type,
    observation.operation_type,
    ...(observation.security_tags || []),
    ...(nodeProfile.security_tags || []),
    ...(nodeProfile.operation_tags || []),
    ...(nodeProfile.node_roles || []),
    JSON.stringify(semantics.targets || []),
    JSON.stringify(semantics.inputs || []),
    JSON.stringify(semantics.outputs || []),
    semantics.evidence?.text,
    semantics.evidence?.source_line
  ].filter(Boolean).join(' '));
}

function buildReceiverText({ observation = {}, nodeProfile = {}, actionText = '' }) {
  const boundary = observation.boundary || {};
  return normalizeText([
    actionText,
    boundary.data_surface,
    boundary.receiver_scope,
    boundary.retention_scope,
    boundary.trust_boundary,
    ...(observation.security_tags || []),
    ...(nodeProfile.security_tags || [])
  ].filter(Boolean).join(' '));
}

function buildFlowPathText({ fcg = {}, labelFlow = {}, nodeById = null, nodeTextById = null, flowPathContext = null }) {
  const byId = nodeById || new Map((fcg.nodes || []).map(node => [node.id, node]));
  const resolvedPath = resolveLabelFlowPath(labelFlow, flowPathContext || createFlowPathContext(fcg));
  return normalizeText([
    ...(resolvedPath.node_names || []),
    ...(resolvedPath.node_path || []).map(id => {
      const node = byId.get(id) || {};
      return getNodeTextForFlow(nodeTextById, id, node);
    }),
    labelFlow.route_event_id,
    ...(labelFlow.route_event_ids || []),
    ...(labelFlow.filter_event_ids || []),
    ...(labelFlow.local_filter_event_ids || []),
    labelFlow.storage_key,
    labelFlow.flow_mode
  ].filter(Boolean).join(' '));
}

function getNodeTextForFlow(cache, id, node = {}) {
  if (cache?.has?.(id)) return cache.get(id);
  const text = nodeTextForFlow(node);
  cache?.set?.(id, text);
  return text;
}

function nodeTextForFlow(node = {}) {
  return [
    node.name,
    node.description,
    node.instructionText,
    node.ownerScript,
    node.functionName,
    node.callee,
    node.semantic_gate?.classification,
    node.semantic_gate?.actionability,
    node.semantic_gate?.completed_sentence,
    node.semantic_gate?.reason,
    node.source_context?.source_line,
    node.source_context?.section,
    node.source_context?.action_evidence?.snippet,
    node.source_context?.action_evidence?.trigger,
    node.formal_semantics?.operation_type,
    safeJson(node.formal_semantics?.targets || []),
    safeJson(node.formal_semantics?.inputs || []),
    safeJson(node.formal_semantics?.outputs || [])
  ].filter(Boolean).join(' ');
}

function cachedOverlapScore(context = null, labelTerms = [], text = '') {
  if (!context?.overlapCache) return overlapScore(labelTerms, text);
  const normalized = cachedNormalizeText(context, text);
  if (!normalized || !labelTerms.length) return 0;
  const key = `${labelTerms.join('\u0001')}::${normalizedTextKey(context, normalized)}`;
  if (context.overlapCache.has(key)) return context.overlapCache.get(key);
  const score = overlapScoreAgainstNormalized(labelTerms, normalized, cachedTokens(context, normalized), context);
  context.overlapCache.set(key, score);
  return score;
}

function cachedKeywordOverlap(context = null, sourceText = '', candidateText = '') {
  if (!context?.keywordOverlapCache) return keywordOverlap(sourceText, candidateText);
  const source = cachedNormalizeText(context, sourceText);
  const candidate = cachedNormalizeText(context, candidateText);
  if (!source || !candidate) return 0;
  const key = `${normalizedTextKey(context, source)}::${normalizedTextKey(context, candidate)}`;
  if (context.keywordOverlapCache.has(key)) return context.keywordOverlapCache.get(key);
  const score = keywordOverlapNormalized(context, source, candidate);
  context.keywordOverlapCache.set(key, score);
  return score;
}

function cachedNormalizeText(context = null, value = '') {
  const raw = String(value || '');
  if (!context?.tokenCache) return normalizeText(raw);
  if (raw === context.taskText) return context.taskText;
  const key = raw.length > 200 ? hashString(raw) : raw;
  const cached = context.tokenCache.get(key);
  if (cached) return cached.normalized;
  const normalized = normalizeText(raw);
  context.tokenCache.set(key, { normalized, tokens: null });
  return normalized;
}

function cachedTokens(context = null, normalized = '') {
  if (!context?.tokenCache) return new Set(normalized.split(/\s+/).filter(Boolean));
  if (normalized === context.taskText) {
    if (!context.taskTokens) context.taskTokens = new Set(normalized.split(/\s+/).filter(Boolean));
    return context.taskTokens;
  }
  const key = normalized.length > 200 ? `norm:${hashString(normalized)}` : `norm:${normalized}`;
  const cached = context.tokenCache.get(key);
  if (cached?.tokens) return cached.tokens;
  const tokens = new Set(normalized.split(/\s+/).filter(Boolean));
  context.tokenCache.set(key, { normalized, tokens });
  return tokens;
}

function overlapScoreAgainstNormalized(labelTerms = [], normalized = '', tokens = new Set(), context = null) {
  if (!normalized || !labelTerms.length) return 0;
  let best = 0;
  const allowSubstring = normalized.length < 5000;
  for (const term of labelTerms) {
    const { phrase, termTokens } = cachedTermTokens(context, term);
    if (!phrase) continue;
    if (phrase.includes(' ') && allowSubstring && normalized.includes(phrase)) best = Math.max(best, 1);
    if (!termTokens.length) continue;
    const hits = termTokens.filter(token => tokens.has(token) || (allowSubstring && normalized.includes(token))).length;
    best = Math.max(best, hits / termTokens.length);
  }
  return round3(Math.min(1, best));
}

function cachedTermTokens(context = null, term = '') {
  const key = String(term || '');
  if (context?.termTokenCache?.has(key)) return context.termTokenCache.get(key);
  const phrase = normalizeText(term);
  const termTokens = phrase.split(/\s+/).filter(token => token && !LOCAL_STOPWORDS.has(token));
  const result = { phrase, termTokens };
  context?.termTokenCache?.set(key, result);
  return result;
}

function keywordOverlapNormalized(context = null, source = '', candidate = '') {
  if (!source || !candidate) return 0;
  const sourceKey = normalizedTextKey(context, source);
  let uniqueTokens = source === context?.taskText
    ? context.taskKeywordTokens
    : context?.keywordTokensBySource?.get(sourceKey);
  if (!uniqueTokens) {
    const sourceTokens = source.split(/\s+/).filter(token => token.length > 2 && !TASK_STOPWORDS.has(token));
    if (!sourceTokens.length) return 0;
    uniqueTokens = Array.from(new Set(sourceTokens)).slice(0, 80);
    if (source === context?.taskText) context.taskKeywordTokens = uniqueTokens;
    else context?.keywordTokensBySource?.set(sourceKey, uniqueTokens);
  }
  const candidateTokens = cachedTokens(context, candidate);
  const allowSubstring = candidate.length < 5000;
  const hits = uniqueTokens.filter(token => candidateTokens.has(token) || (allowSubstring && candidate.includes(token))).length;
  return round3(Math.min(1, hits / Math.min(uniqueTokens.length, 10)));
}

const LOCAL_STOPWORDS = new Set([
  'a', 'an', 'the', 'to', 'into', 'in', 'on', 'for', 'from', 'of', 'and', 'or', 'then', 'with',
  'by', 'as', 'it', 'this', 'that', 'these', 'those', 'locally', 'local', 'file', 'data', 'value',
  'content', 'context', 'input', 'output', 'result', 'results', 'use', 'using', 'send', 'write', 'read'
]);

function hashString(value = '') {
  let hash = 5381;
  const text = String(value || '');
  for (let i = 0; i < text.length; i += 1) {
    hash = ((hash << 5) + hash) ^ text.charCodeAt(i);
  }
  return (hash >>> 0).toString(36);
}

function normalizedTextKey(context = null, normalized = '') {
  if (context?.taskText && normalized === context.taskText) return '__task_text__';
  return normalized.length > 200 ? hashString(normalized) : normalized;
}

function safeJson(value) {
  try {
    return JSON.stringify(value || []);
  } catch {
    return '';
  }
}

function stableFlowKey(labelFlow = {}) {
  return [
    labelFlow.label_flow_id || '',
    (labelFlow.parent_label_flow_ids || []).join('>'),
    labelFlow.current_node || '',
    labelFlow.incoming_edge_id || '',
    labelFlow.flow_mode || '',
    labelFlow.storage_key || ''
  ].join('|');
}

function keywordOverlap(sourceText = '', candidateText = '') {
  const source = normalizeText(sourceText);
  const candidate = normalizeText(candidateText);
  if (!source || !candidate) return 0;
  const sourceTokens = source.split(/\s+/).filter(token => token.length > 2 && !TASK_STOPWORDS.has(token));
  if (!sourceTokens.length) return 0;
  const uniqueTokens = Array.from(new Set(sourceTokens)).slice(0, 80);
  const candidateTokens = new Set(candidate.split(/\s+/).filter(Boolean));
  const hits = uniqueTokens.filter(token => candidateTokens.has(token) || candidate.includes(token)).length;
  return round3(Math.min(1, hits / Math.min(uniqueTokens.length, 10)));
}

function isTransformLike(nodeProfile = {}, observation = {}) {
  const roles = new Set([...(nodeProfile.node_roles || []), ...(observation.node_roles || [])]);
  // 这三个 transform tag 只存在于 nodeProfile.operation_tags;observation 上无 operation_tags,
  // 其 security_tags 也从不含这些值(旧代码曾读 observation.security_tags,为恒不命中的死引用,已删)。
  const tags = new Set(nodeProfile.operation_tags || []);
  return roles.has('transform') || roles.has('model_inference') || tags.has('summarization') || tags.has('semantic_extraction') || tags.has('aggregation');
}

function isDerivedSummaryLabel(label = {}) {
  return label.label === 'aggregate_data.summary' || label.category === 'aggregate_data';
}

function normalizeComponentScores(scores = {}) {
  return COMPONENT_KEYS.reduce((acc, key) => {
    acc[key] = clamp(round3(scores[key]));
    return acc;
  }, {});
}

function componentMin(scores = {}) {
  return round3(Math.min(...COMPONENT_KEYS.map(key => Number(scores[key] || 0))));
}

function weakestComponent(scores = {}) {
  return COMPONENT_KEYS.reduce((weakest, key) => (
    Number(scores[key] || 0) < Number(scores[weakest] || 0) ? key : weakest
  ), COMPONENT_KEYS[0]);
}

function evidence(kind, score, reason) {
  return { kind, score: clamp(round3(score)), reason };
}

module.exports = {
  COMPONENT_KEYS,
  createNecessityContext,
  scoreNecessityBaseline,
  normalizeComponentScores,
  componentMin,
  weakestComponent,
  buildTaskContextText,
  buildActionText,
  buildFlowPathText,
  isTaskContextNode
};
