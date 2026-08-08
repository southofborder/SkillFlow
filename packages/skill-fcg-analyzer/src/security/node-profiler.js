const { buildDataProfile } = require('./data-labeler');
const { applyLlmLabelAssistToProfiles } = require('./label-llm-assistant');

function buildNodeProfiles(nodes = [], edges = []) {
  const incomingByNode = groupEdges(edges, 'target');
  const outgoingByNode = groupEdges(edges, 'source');

  return (nodes || []).map(node => buildNodeProfile(node, {
    incomingEdges: incomingByNode.get(node.id) || [],
    outgoingEdges: outgoingByNode.get(node.id) || []
  }));
}

async function buildNodeProfilesWithOptions(nodes = [], edges = [], options = {}) {
  const profiles = buildNodeProfiles(nodes, edges);
  const assist = await applyLlmLabelAssistToProfiles(profiles, nodes, edges, {
    enabled: Boolean(options.labelLlmAssist),
    provider: options.llmProvider,
    model: options.llmModel,
    apiKey: options.llmApiKey,
    endpoint: options.llmEndpoint,
    timeout: options.llmTimeout,
    concurrency: options.labelLlmConcurrency,
    cachePath: options.labelLlmCache,
    labelAssistant: options.labelAssistant
  });
  return assist;
}

function buildNodeProfile(node = {}, context = {}) {
  const evidence = [];
  const roles = new Set();
  const securityTags = new Set();
  const operationTags = new Set();
  const displayName = nodeDisplayName(node);
  const text = nodeSecurityText(node, context);
  const lower = text.toLowerCase();
  const actionText = nodeActionText(node);
  const op = String(node.formal_semantics?.operation_type || node.operationType || '').toLowerCase();
  const docActions = new Set(node.docActions || (node.docAction ? [node.docAction] : []));

  if (isUserQuery(node)) {
    roles.add('data_introduction');
    roles.add('control_context');
    securityTags.add('user_input');
    addEvidence(evidence, 'builtin_user_query', 'user.query introduces the task prompt and controls activation', 0.95);
  }

  if (op === 'trigger' || node.semanticKind === 'trigger' || /^rule\.trigger\./i.test(displayName || '')) {
    roles.add('control_context');
    securityTags.add('user_input');
    addEvidence(evidence, 'formal_semantics.trigger', 'trigger/control context', 0.85);
  }

  if (['condition', 'decision', 'guard'].includes(op) || node.semanticKind === 'policy') {
    roles.add('decision');
    if (op === 'guard') operationTags.add('policy_guard');
    if (op === 'decision' || op === 'condition') operationTags.add('routing_decision');
    addEvidence(evidence, 'formal_semantics.decision', `operation_type=${op || node.semanticKind}`, 0.8);
  }

  if (op === 'read' || docActions.has('read') || readPattern(lower)) {
    roles.add('data_introduction');
    securityTags.add('tool_response');
    addEvidence(evidence, 'read_pattern', op || displayName || 'read', 0.75);
  }

  if (op === 'produce_artifact') {
    roles.add('data_introduction');
    securityTags.add('artifact_generated');
    addEvidence(evidence, 'formal_semantics.produce_artifact', 'operation_type=produce_artifact emits generated data', 0.78);
  }

  if (op === 'transform' || transformPattern(lower)) {
    roles.add('transform');
    addEvidence(evidence, 'transform_pattern', op || displayName || 'transform', 0.75);
  }

  if (isLlmConsumingTransform(lower, op)) {
    roles.add('transform');
    roles.add('model_inference');
    securityTags.add('model_context');
    addEvidence(evidence, 'llm_consuming_transform', displayName || text, 0.78);
  }

  if (op === 'invoke_tool') {
    roles.add('tool_invocation');
    addEvidence(evidence, 'formal_semantics.invoke_tool', 'operation_type=invoke_tool', 0.85);
  }

  if (isModelNode(lower)) {
    roles.add('model_inference');
    securityTags.add('model_context');
    addEvidence(evidence, 'model_pattern', displayName || 'model inference', 0.9);
  }

  if (externalEgressPattern(lower)) {
    roles.add('external_egress');
    roles.add('tool_invocation');
    securityTags.add('network_egress');
    addEvidence(evidence, 'external_egress_pattern', displayName || text, 0.85);
  }

  if (localPersistencePattern(lower) || op === 'write' || op === 'produce_artifact' || docActions.has('write')) {
    roles.add('local_persistence');
    addEvidence(evidence, 'persistence_pattern', op || displayName || 'write', 0.75);
  }

  if (commandPattern(lower)) {
    roles.add('command_execution');
    roles.add('tool_invocation');
    securityTags.add('shell_exec');
    addEvidence(evidence, 'command_pattern', displayName || text, 0.9);
  }

  if (destructivePattern(lower)) {
    roles.add('destructive_operation');
    addEvidence(evidence, 'destructive_pattern', displayName || text, 0.85);
  }

  if (node.category === 'Sink' && !hasSinkLikeRole(roles)) {
    roles.add('tool_invocation');
    if (externalEgressPattern(String(displayName || '').toLowerCase()) || /\bapi\b/i.test(String(displayName || ''))) {
      roles.add('external_egress');
      securityTags.add('network_egress');
    }
    addEvidence(evidence, 'legacy_sink_category', 'legacy graph category=Sink', 0.65);
  }

  addSecuritySurfaceTags(securityTags, lower);
  addOperationTags(operationTags, lower, op);

  if (roles.size === 0) {
    roles.add('transform');
    addEvidence(evidence, 'fallback_role', 'default transform/intermediate node', 0.35);
  }

  const boundary = inferBoundary({
    roles,
    securityTags,
    operationTags,
    text: lower,
    node
  });

  const dataProfile = roles.has('data_introduction')
    ? buildDataProfile(node, {
        node_id: node.id,
        node_name: displayName || node.id || '',
        data_type: profileDataType(node),
        reason: evidence.map(item => item.text).join(' ')
      })
    : { primary_category: 'none', sensitivity: 'low', labels: [], alternatives: [], unknown_tail: false };
  const actionPlan = buildActionPlan(node, {
    roles,
    securityTags,
    operationTags,
    text,
    actionText,
    lower,
    op,
    docActions,
    evidence
  });

  return {
    node_id: node.id || '',
    node_name: displayName || node.id || '',
    node_roles: Array.from(roles).sort(),
    security_tags: Array.from(securityTags).sort(),
    operation_tags: Array.from(operationTags).sort(),
    data_surface: boundary.data_surface,
    receiver_scope: boundary.receiver_scope,
    retention_scope: boundary.retention_scope,
    trust_boundary: boundary.trust_boundary,
    data_profile: dataProfile,
    action_steps: actionPlan.action_steps,
    action_order_confidence: actionPlan.action_order_confidence,
    action_order_source: actionPlan.action_order_source,
    has_multi_action: actionPlan.has_multi_action,
    ambiguous_action_order: actionPlan.ambiguous_action_order,
    produced_object_key: String(node.formal_semantics?.evidence?.produced_object_key || ''),
    produced_object_text: String(node.formal_semantics?.evidence?.produced_object_text || ''),
    consumed_object_key: String(node.formal_semantics?.evidence?.consumed_object_key || ''),
    consumed_object_text: String(node.formal_semantics?.evidence?.consumed_object_text || ''),
    // Part 2: surface the extracted guard/trigger conditions so the routing
    // layer can use them as an edge-connection precision signal (prevent
    // over-connecting). Additive field; no existing consumer reads it.
    conditions: normalizeProfileConditions(node.formal_semantics?.conditions),
    confidence: confidenceFromEvidence(evidence),
    evidence: evidence.sort((a, b) => b.confidence - a.confidence)
  };
}

// Keep only well-formed {type, text} condition entries for the profile.
function normalizeProfileConditions(conditions) {
  if (!Array.isArray(conditions)) return [];
  return conditions
    .map(item => ({
      type: String(item?.type || 'condition'),
      text: String(item?.text || '').trim()
    }))
    .filter(item => item.text);
}

function buildActionPlan(node = {}, context = {}) {
  const memberSteps = buildMemberActionSteps(node, context);
  if (memberSteps.length > 0) {
    return finalizeActionPlan(memberSteps, 'member_steps', 0.9, false);
  }

  const textSteps = buildTextOrderedActionSteps(node, context);
  if (textSteps.length > 0) {
    const source = textSteps.length === 1 && context.op ? 'formal_semantics' : 'text_order';
    const ambiguousTextOrder = source === 'text_order' && textSteps.length > 1 && stepsContainFilterAndSink(textSteps);
    return finalizeActionPlan(textSteps, source, source === 'formal_semantics' ? 0.85 : (ambiguousTextOrder ? 0.45 : 0.7), ambiguousTextOrder);
  }

  const docActionSteps = buildDocActionSteps(node, context);
  if (docActionSteps.length > 0) {
    return finalizeActionPlan(docActionSteps, 'doc_actions', docActionSteps.length > 1 ? 0.55 : 0.75, docActionSteps.length > 1);
  }

  const heuristicSteps = buildHeuristicActionSteps(node, context);
  return finalizeActionPlan(heuristicSteps, 'heuristic', heuristicSteps.length > 1 ? 0.45 : 0.65, heuristicSteps.length > 1);
}

function buildMemberActionSteps(node = {}, context = {}) {
  if (!Array.isArray(node.member_steps) || node.member_steps.length === 0) return [];
  return node.member_steps
    .map((step, index) => {
      const stepText = [
        step.instruction,
        step.text,
        step.source_line,
        step.operation_type,
        step.docAction,
        step.action,
        step.formal_semantics?.evidence?.text
      ].filter(Boolean).join(' ');
      const operationType = normalizeOperationType(
        step.formal_semantics?.operation_type ||
        step.operation_type ||
        step.docAction ||
        step.action ||
        detectPrimaryOperationType(stepText) ||
        context.op
      );
      return createActionStep({
        node,
        operationType,
        text: stepText || context.text,
        order: Number(step.line || step.sourceLine || index + 1),
        source: 'member_steps',
        confidence: Math.max(0.65, Number(step.formal_semantics?.confidence || step.confidence || 0.9)),
        targets: step.formal_semantics?.targets || []
      });
    })
    .filter(Boolean)
    .sort((a, b) => a.order - b.order);
}

function buildTextOrderedActionSteps(node = {}, context = {}) {
  // Scan only clean instruction prose (actionText), never the name/JSON blob.
  const scanText = String(context.actionText || '');
  const op = String(context.op || '');
  // B-guard: pure routing/control nodes (condition/decision/guard/trigger) with
  // no member_steps must not spawn data-sink steps from descriptive prose. Their
  // only action is the routing decision itself; sink roles, if genuinely present,
  // are re-added by enrichActionMentions from node roles.
  const routingOnly = ['condition', 'decision', 'guard', 'trigger'].includes(op);
  const rawMentions = routingOnly
    ? filterSinkMentions(detectActionMentions(scanText))
    : detectActionMentions(scanText);
  const mentions = enrichActionMentions(rawMentions, context);
  if (mentions.length === 0 && context.op) {
    return [createActionStep({
      node,
      operationType: normalizeOperationType(context.op),
      text: scanText,
      order: 1,
      source: 'formal_semantics',
      confidence: 0.85,
      targets: node.formal_semantics?.targets || []
    })];
  }
  if (mentions.length === 0) return [];

  const byType = new Map();
  for (const mention of mentions) {
    if (!byType.has(mention.operation_type)) byType.set(mention.operation_type, mention);
  }
  return Array.from(byType.values())
    .sort((a, b) => a.index - b.index)
    .map((mention, index) => createActionStep({
      node,
      operationType: mention.operation_type,
      text: actionEvidenceWindow(scanText, mention),
      order: index + 1,
      source: 'text_order',
      confidence: 0.7,
      targets: node.formal_semantics?.targets || []
    }));
}

// Drop data-sink mentions (egress/model/command/destructive/write) from a set,
// keeping routing/read/transform. Used to stop pure routing nodes from
// fabricating sinks out of descriptive prose.
const SINK_MENTION_TYPES = new Set([
  'external_egress',
  'model_inference',
  'command_execution',
  'destructive_operation',
  'write'
]);
function filterSinkMentions(mentions = []) {
  return mentions.filter(m => !SINK_MENTION_TYPES.has(m.operation_type));
}

function enrichActionMentions(mentions = [], context = {}) {
  const result = [...mentions];
  const hasType = type => result.some(mention => mention.operation_type === type);
  const tags = context.securityTags || new Set();
  const roles = context.roles || new Set();
  const text = String(context.actionText || context.text || '');
  if (!hasType('external_egress') && (
    roles.has('external_egress') ||
    tags.has('webhook_post') ||
    tags.has('email_send') ||
    tags.has('api_call') ||
    tags.has('network_egress') ||
    /send[A-Z_]?.*webhook|webhook|send[A-Z_]?.*email|api\.call/i.test(text)
  )) {
    result.push({ operation_type: 'external_egress', index: Math.max(0, text.search(/send|webhook|external|api/i)), text: 'external_egress' });
  }
  if (!hasType('model_inference') && roles.has('model_inference')) {
    result.push({ operation_type: 'model_inference', index: Math.max(0, text.search(/llm|model|inference/i)), text: 'model_inference' });
  }
  if (!hasType('write') && roles.has('local_persistence')) {
    result.push({ operation_type: 'write', index: Math.max(0, text.search(/write|save|store|persist|report|artifact/i)), text: 'write' });
  }
  return result.sort((a, b) => a.index - b.index);
}

function buildDocActionSteps(node = {}, context = {}) {
  const actions = Array.from(context.docActions || []);
  if (actions.length === 0) return [];
  const stepText = String(context.actionText || context.text || '');
  return actions.map((action, index) => createActionStep({
    node,
    operationType: normalizeOperationType(action),
    text: stepText,
    order: index + 1,
    source: 'doc_actions',
    confidence: actions.length > 1 ? 0.55 : 0.75,
    targets: node.formal_semantics?.targets || []
  }));
}

function buildHeuristicActionSteps(node = {}, context = {}) {
  const candidates = new Set();
  if ((context.roles || new Set()).has('data_introduction')) candidates.add('read');
  if ((context.roles || new Set()).has('control_context')) candidates.add('trigger');
  if ((context.roles || new Set()).has('decision')) candidates.add('decision');
  if ((context.roles || new Set()).has('transform')) candidates.add('transform');
  if ((context.roles || new Set()).has('local_persistence')) candidates.add('write');
  if ((context.roles || new Set()).has('external_egress')) candidates.add('external_egress');
  if ((context.roles || new Set()).has('model_inference')) candidates.add('model_inference');
  if ((context.roles || new Set()).has('command_execution')) candidates.add('command_execution');
  if ((context.roles || new Set()).has('destructive_operation')) candidates.add('destructive_operation');
  if ((context.roles || new Set()).has('tool_invocation') && !candidates.has('external_egress')) candidates.add('invoke_tool');
  if (context.op) candidates.add(normalizeOperationType(context.op));

  const ordered = Array.from(candidates).sort((a, b) => canonicalActionOrder(a) - canonicalActionOrder(b));
  const source = ordered.length ? ordered : ['transform'];
  const stepText = String(context.actionText || context.text || '');
  return source.map((operationType, index) => createActionStep({
    node,
    operationType,
    text: stepText,
    order: index + 1,
    source: 'heuristic',
    confidence: source.length > 1 ? 0.45 : 0.65,
    targets: node.formal_semantics?.targets || []
  }));
}

function createActionStep({ node = {}, operationType = 'transform', text = '', order = 1, source = 'heuristic', confidence = 0.5, targets = [] }) {
  const normalized = normalizeOperationType(operationType);
  const roles = new Set();
  const securityTags = new Set();
  const operationTags = new Set();
  const lower = String(text || '').toLowerCase();

  applyOperationTypeToStep(normalized, roles, securityTags, operationTags);
  applyTextPatternsToStep(lower, roles, securityTags, operationTags, normalized, node, source);
  if (roles.size === 0) roles.add('transform');

  const boundary = inferBoundary({ roles, securityTags, operationTags, text: lower, node });
  const orderNumber = Number.isFinite(Number(order)) ? Number(order) : 1;
  const stepId = `${node.id || 'node'}:step_${String(Math.max(1, Math.round(orderNumber))).padStart(3, '0')}:${normalized}`;
  return {
    step_id: stepId,
    order: orderNumber,
    operation_type: normalized,
    node_roles: Array.from(roles).sort(),
    security_tags: Array.from(securityTags).sort(),
    operation_tags: Array.from(operationTags).sort(),
    boundary,
    targets: Array.isArray(targets) ? targets : [],
    evidence: [{
      kind: `action_step.${source}`,
      text: String(text || normalized).slice(0, 240),
      confidence: roundConfidence(confidence)
    }],
    confidence: roundConfidence(confidence)
  };
}

function applyOperationTypeToStep(operationType, roles, securityTags, operationTags) {
  if (operationType === 'trigger') {
    roles.add('control_context');
    securityTags.add('user_input');
  } else if (['condition', 'decision', 'guard'].includes(operationType)) {
    roles.add('decision');
    operationTags.add(operationType === 'guard' ? 'policy_guard' : 'routing_decision');
  } else if (operationType === 'read' || operationType === 'review' || operationType === 'verify') {
    roles.add('data_introduction');
    securityTags.add('tool_response');
  } else if (operationType === 'produce_artifact') {
    roles.add('data_introduction');
    roles.add('local_persistence');
    securityTags.add('artifact_generated');
    securityTags.add('file_write');
  } else if (operationType === 'write') {
    roles.add('local_persistence');
    securityTags.add('file_write');
  } else if (operationType === 'external_egress') {
    roles.add('external_egress');
    roles.add('tool_invocation');
    securityTags.add('network_egress');
  } else if (operationType === 'model_inference') {
    roles.add('model_inference');
    securityTags.add('model_context');
  } else if (operationType === 'invoke_tool') {
    roles.add('tool_invocation');
  } else if (operationType === 'command_execution') {
    roles.add('command_execution');
    roles.add('tool_invocation');
    securityTags.add('shell_exec');
  } else if (operationType === 'destructive_operation') {
    roles.add('destructive_operation');
  } else {
    roles.add('transform');
  }
}

function applyTextPatternsToStep(text, roles, securityTags, operationTags, operationType, node = {}, source = '') {
  const scoped = ['member_steps', 'text_order', 'doc_actions', 'formal_semantics'].includes(source);
  if (!scoped && operationType !== 'write' && operationType !== 'produce_artifact' && readPattern(text)) {
    roles.add('data_introduction');
    securityTags.add('tool_response');
  }
  if (!scoped && operationType !== 'read' && transformPattern(text)) roles.add('transform');
  if ((operationType === 'model_inference' || !scoped) && isModelNode(text)) {
    roles.add('model_inference');
    securityTags.add('model_context');
  }
  if (isLlmConsumingTransform(text, operationType)) {
    roles.add('transform');
    roles.add('model_inference');
    securityTags.add('model_context');
  }
  if (operationType === 'external_egress' || (!scoped && externalEgressPattern(text)) || (operationType === 'invoke_tool' && node.category === 'Sink' && /\bapi\b/i.test(String(nodeDisplayName(node) || '')))) {
    roles.add('external_egress');
    roles.add('tool_invocation');
    securityTags.add('network_egress');
  }
  if (operationType === 'write' || operationType === 'produce_artifact' || (!scoped && localPersistencePattern(text))) {
    roles.add('local_persistence');
  }
  if (operationType === 'command_execution' || (!scoped && commandPattern(text))) {
    roles.add('command_execution');
    roles.add('tool_invocation');
    securityTags.add('shell_exec');
  }
  if (operationType === 'destructive_operation' || (!scoped && destructivePattern(text))) roles.add('destructive_operation');
  addSecuritySurfaceTags(securityTags, text);
  addOperationTags(operationTags, text, operationType);
}

function finalizeActionPlan(steps, source, confidence, ambiguous) {
  const normalized = dedupeActionSteps(steps)
    .sort((a, b) => a.order - b.order)
    .map((step, index) => ({ ...step, order: index + 1 }));
  return {
    action_steps: normalized,
    action_order_confidence: roundConfidence(confidence),
    action_order_source: source,
    has_multi_action: normalized.length > 1,
    ambiguous_action_order: Boolean(ambiguous && normalized.length > 1)
  };
}

function stepsContainFilterAndSink(steps = []) {
  const hasFilter = steps.some(step => (step.operation_tags || []).some(tag => (
    tag === 'field_slice' ||
    tag === 'semantic_extraction' ||
    tag === 'aggregation' ||
    tag === 'redaction' ||
    tag === 'pseudonymization'
  )));
  const hasSink = steps.some(step => (step.node_roles || []).some(role => hasSinkLikeRole(new Set([role]))));
  return hasFilter && hasSink;
}

function dedupeActionSteps(steps = []) {
  const result = [];
  const seen = new Set();
  for (const step of steps || []) {
    if (!step) continue;
    const key = [
      step.operation_type,
      (step.node_roles || []).join(','),
      (step.operation_tags || []).join(','),
      (step.security_tags || []).join(',')
    ].join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(step);
  }
  return result.length ? result : [createActionStep({ operationType: 'transform' })];
}

function detectActionMentions(text = '') {
  const patterns = [
    ['read', /\b(read|get|fetch|retrieve|search|list|find|select|query|load|scrape|open)[A-Za-z0-9_]*/ig],
    ['transform', /\b(transform|extract|parse|summari[sz]e|filter|format|convert|redact|mask|sanitize|aggregate|count|hash|merge|join)[A-Za-z0-9_]*/ig],
    ['write', /\b(write|save|persist|store|append|produce|create|generate|export)[A-Za-z0-9_]*/ig],
    // Egress: unambiguous transport tokens (webhook/http/upload/api.call) match
    // bare; ambiguous verbs (send/post/publish/share) require an egress object so
    // descriptive prose like "skills shared by agents" or "post-processing" does
    // not fabricate a sink. Bare "external" removed (over-matched "external tool").
    ['external_egress', /\b(webhooks?|https?|upload|email\.send|api\.call|external\.api|third[_\-\s]?party)[A-Za-z0-9_.]*|\b(?:send|posts?|publish|shares?|push)(?:ed|ing|s)?\s+(?:to|the|a|an|it|them|data|payload|request|message|report|results?|file|email|webhook|via)\b/ig],
    ['model_inference', /\b(llm|model|chat|completion|openai|anthropic|qwen|gpt|claude|gemini|inference)[A-Za-z0-9_]*/ig],
    ['command_execution', /\b(exec|execute|shell|command|process|spawn|run_script|subprocess)[A-Za-z0-9_]*/ig],
    ['destructive_operation', /\b(delete|remove|destroy|drop|truncate|wipe)[A-Za-z0-9_]*/ig],
    ['decision', /\b(condition|decision|route|decide|choose|branch|if|when|guard|policy|allow|deny)[A-Za-z0-9_]*/ig]
  ];
  const mentions = [];
  for (const [operationType, pattern] of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      mentions.push({ operation_type: operationType, index: match.index, text: match[0] });
    }
  }
  return mentions.sort((a, b) => a.index - b.index);
}

function actionEvidenceWindow(text = '', mention = {}) {
  const raw = String(text || '');
  if (!raw) return mention.text || '';
  const start = Math.max(0, Number(mention.index || 0) - 80);
  const end = Math.min(raw.length, Number(mention.index || 0) + String(mention.text || '').length + 160);
  return raw.slice(start, end);
}

function detectPrimaryOperationType(text = '') {
  const mentions = detectActionMentions(text);
  return mentions[0]?.operation_type || '';
}

function normalizeOperationType(operationType = '') {
  const op = String(operationType || '').toLowerCase();
  if (op === 'run') return 'command_execution';
  if (op === 'send' || op === 'post' || op === 'api_call') return 'external_egress';
  if (op === 'llm' || op === 'model') return 'model_inference';
  if (op === 'artifact') return 'produce_artifact';
  if (['trigger', 'condition', 'decision', 'read', 'write', 'transform', 'invoke_tool', 'verify', 'review', 'produce_artifact', 'guard', 'external_egress', 'model_inference', 'command_execution', 'destructive_operation'].includes(op)) return op;
  return op || 'transform';
}

function canonicalActionOrder(operationType = '') {
  const order = {
    trigger: 5,
    condition: 10,
    decision: 10,
    guard: 10,
    read: 20,
    review: 20,
    verify: 20,
    transform: 40,
    produce_artifact: 70,
    write: 70,
    model_inference: 80,
    external_egress: 90,
    invoke_tool: 95,
    command_execution: 100,
    destructive_operation: 110
  };
  return order[operationType] || 50;
}

function addSecuritySurfaceTags(tags, text) {
  if (/(api[_\-\s]?key|secret|token|credential|password|private[_\-\s]?key)/i.test(text)) {
    tags.add('credential_read');
  }
  if (/\b(env|environment|process\.env)\b/i.test(text)) tags.add('env_read');
  if (/(file|document|attachment|readme|skill\.md|path|folder|directory)/i.test(text)) tags.add('file_read');
  if (/(memory|mem0|vector|embedding|session|remember|recall)/i.test(text)) tags.add('memory_read');
  if (/(database|db|sql|record|table|collection|row)/i.test(text)) tags.add('database_read');
  if (/(browser|cookie|history|localstorage|webpage|tab)/i.test(text)) tags.add('browser_read');
  if (/(http|https|url|web|network|request|fetch|scrape)/i.test(text)) tags.add('network_read');
  if (/(email|mail|inbox|message)/i.test(text)) tags.add('email_read');
  if (/(calendar|event|meeting|schedule)/i.test(text)) tags.add('calendar_read');
  if (/(contact|address[_\-\s]?book|phone)/i.test(text)) tags.add('contact_read');

  if (/(send[_\-.]?mail|send.*email|email\.send|mail\.send|smtp)/i.test(text)) tags.add('email_send');
  if (/(webhook|callback)/i.test(text)) tags.add('webhook_post');
  if (/(api\.call|external\.api|http[_\-.]?post|\bpost\b|\bput\b|\bupload\b|\bpublish\b|\bshare\b|\bapi\b)/i.test(text)) tags.add('api_call');
  if (/(third[_\-\s]?party|external|public)/i.test(text)) tags.add('third_party_service');
  if (/(write.*file|save.*file|file_write|append|(?:write|save|store|persist|create|generate|export|produce)[\s._-]*(?:artifact|report|markdown|document|file))/i.test(text)) tags.add('file_write');
  if (/(write.*memory|store.*memory|save_state|remember|persist.*memory)/i.test(text)) tags.add('memory_write');
  if (/(insert|update|database_write|db_write|sql.*write)/i.test(text)) tags.add('database_write');
  if (/(write.*log|log_write|append.*log|audit.*write|telemetry.*write)/i.test(text)) tags.add('log_write');
  if (/(produce_artifact|artifact_write|(?:write|save|store|persist|create|generate|export|produce)[\s._-]*(?:artifact|report|markdown))/i.test(text)) tags.add('artifact_write');
}

function addOperationTags(tags, text, op) {
  if (/(extract|select|pick|only|filter|field|slice|project)/i.test(text)) tags.add('field_slice');
  if (/(extract|parse|derive|detect|identify).*(api[_\-\s]?key|secret|token|credential|email|phone|address|pii)|from[_\-\s]?prompt/i.test(text)) {
    tags.add('semantic_extraction');
  }
  if (/(summari[sz]e|summary|digest|brief)/i.test(text)) tags.add('summarization');
  if (/(aggregate|count|average|total|histogram)\b|statistics\b/i.test(text)) tags.add('aggregation');
  if (/(redact|mask|sanitize|scrub|strip|remove.*secret|remove.*pii)/i.test(text)) tags.add('redaction');
  if (/(pseudonym|anonym|hash|deidentify|de-identify)/i.test(text)) tags.add('pseudonymization');
  if (/(format|convert|serialize|deserialize|parse|render)/i.test(text)) tags.add('format_conversion');
  if (/(merge|join|combine|concat|append)/i.test(text)) tags.add('merge_join');
  if (op === 'decision' || op === 'condition' || /(route|decide|choose|branch|if\b|when\b)/i.test(text)) tags.add('routing_decision');
  if (op === 'guard' || /(policy|guard|allow|deny|must|should not|forbid)/i.test(text)) tags.add('policy_guard');
}

function inferBoundary({ roles, securityTags, text }) {
  let data_surface = 'tool_io';
  let receiver_scope = 'local_runtime';
  let retention_scope = 'transient';
  let trust_boundary = 'local_process';

  const isExternal = roles.has('external_egress') || securityTags.has('network_egress') || securityTags.has('webhook_post') || securityTags.has('api_call');
  const isModel = roles.has('model_inference');
  const isPersistent = roles.has('local_persistence');

  if (roles.has('control_context') && securityTags.has('user_input') && !isExternal && !isModel && !isPersistent) {
    data_surface = 'user_prompt';
    receiver_scope = 'same_skill';
    trust_boundary = 'user_visible';
  }
  if (isModel) {
    data_surface = 'llm_context';
    receiver_scope = 'model_provider';
    trust_boundary = 'model_provider';
  }
  if (isExternal) {
    data_surface = 'network';
    receiver_scope = securityTags.has('third_party_service') || /webhook|external|public|third/i.test(text)
      ? 'third_party_service'
      : 'first_party_service';
    retention_scope = 'external';
    trust_boundary = 'external_network';
  }
  if (isPersistent && !isExternal && !isModel) {
    retention_scope = 'persistent';
    trust_boundary = 'persistent_storage';
    if (securityTags.has('memory_write') || securityTags.has('memory_read')) data_surface = 'memory_store';
    else if (securityTags.has('database_write') || securityTags.has('database_read')) data_surface = 'database';
    else data_surface = 'local_file';
  }
  if (roles.has('command_execution')) {
    data_surface = 'runtime_env';
    receiver_scope = 'local_runtime';
    trust_boundary = 'local_process';
  }
  if (!isExternal && !isModel && !isPersistent) {
    if (securityTags.has('browser_read')) data_surface = 'browser';
    if (securityTags.has('env_read') || securityTags.has('credential_read')) data_surface = 'runtime_env';
    if (securityTags.has('file_read')) data_surface = 'local_file';
    if (securityTags.has('database_read')) data_surface = 'database';
    if (securityTags.has('memory_read')) data_surface = 'memory_store';
  }

  return { data_surface, receiver_scope, retention_scope, trust_boundary };
}

function nodeDisplayName(node = {}) {
  return node.canonical_name || node.name || node.id || '';
}

function nodeSecurityText(node = {}, context = {}) {
  const semantics = node.formal_semantics || {};
  const targets = Array.isArray(semantics.targets)
    ? semantics.targets.map(target => `${target.type || ''}:${target.value || ''}:${target.raw || ''}`).join(' ')
    : '';
  const effects = Array.isArray(semantics.effects) ? semantics.effects.join(' ') : '';
  // Edges contribute only their DATA (data_flow params/type) to a node's role
  // inference — never `semantic_reason`. semantic_reason is prose that explains
  // why an edge exists (e.g. "...flows to LLM inference") or an FCG routing log
  // ("not selected for high-value LLM budget"); it describes the EDGE/downstream,
  // not this node's own action. Feeding it here let words like "LLM"/"send" in a
  // neighbour's reason falsely stamp this node with model_inference/external_egress
  // (e.g. user.query and pure JS calls like Array.isArray). A node's role must come
  // from what the node itself does plus the data flowing through it — not from edge
  // explanations. (semantic_reason stays on the edge; it is just not read here.)
  const edgeText = [...(context.incomingEdges || []), ...(context.outgoingEdges || [])]
    .map(edge => [edge.data_flow?.from_param, edge.data_flow?.to_param, edge.data_flow?.data_type].filter(Boolean).join(' '))
    .join(' ');

  // Role/keyword detection text. Deliberately EXCLUDES serialized semantic_gate
  // and source_context.action_evidence JSON: those carry gate REASON prose and
  // metadata keys (e.g. "reason":"...flows to the model...", "extraction_method")
  // whose words falsely stamp sink roles onto pure routing/read nodes. This is
  // the same guard already applied to edge semantic_reason (see
  // fcg-semantic-reason-role-pollution-fix): a node's role must come from what it
  // does and the data flowing through it, not from prose explaining it.
  return [
    node.canonical_name,
    node.name,
    node.description,
    node.action,
    node.instructionText,
    node.docAction,
    Array.isArray(node.docActions) ? node.docActions.join(' ') : '',
    semantics.operation_type,
    semantics.evidence?.text,
    targets,
    effects,
    JSON.stringify(node.signature || {}),
    JSON.stringify(node.input || {}),
    JSON.stringify(node.output || {}),
    edgeText
  ].filter(Boolean).join(' ');
}

// Clean prose used for per-step action mention detection and evidence windows.
// Unlike nodeSecurityText this NEVER includes the node name or any serialized
// JSON — only human-authored instruction/description text. Feeding the name or
// JSON here let actionEvidenceWindow slice 160-char windows INTO serialized
// metadata, polluting child instructionText with JSON fragments and fabricating
// sink action-steps from metadata key words. Role-driven sink steps are still
// re-added downstream by enrichActionMentions, so recall is unaffected.
function nodeActionText(node = {}) {
  const semantics = node.formal_semantics || {};
  const parts = [
    node.instructionText,
    semantics.evidence?.text,
    semantics.evidence?.source_line,
    node.description
  ];
  // Doc nodes carry their meaning in prose; their name is a structural slug
  // (doc.step.skill.l10.s6.condition.semantic_condition) that must NOT be scanned
  // for action keywords. Tool/script/function nodes instead encode meaning in the
  // name itself (redactEmailAndSendWebhook, webhook.post), so include the name for
  // those. This keeps recall on code-derived sinks while excluding doc slugs.
  const name = String(node.canonical_name || node.name || '');
  const isDocSlug = /^doc\.(step|op|context)\./.test(name);
  if (!isDocSlug && name) parts.unshift(name);
  return parts.filter(Boolean).join(' ');
}

function profileDataType(node = {}) {
  const outputKeys = Object.keys(node.signature?.output || node.output || {});
  const inputKeys = Object.keys(node.signature?.input || node.input || {});
  const targets = Array.isArray(node.formal_semantics?.targets)
    ? node.formal_semantics.targets.map(target => `${target.type}:${target.value}`).join(', ')
    : '';
  return [targets, outputKeys.join(', '), inputKeys.join(', ')].filter(Boolean).join(', ');
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

function addEvidence(evidence, kind, text, confidence) {
  evidence.push({ kind, text: String(text || '').slice(0, 240), confidence });
}

function confidenceFromEvidence(evidence) {
  if (!evidence.length) return 0.3;
  const max = Math.max(...evidence.map(item => Number(item.confidence || 0.3)));
  return Math.round(max * 1000) / 1000;
}

function roundConfidence(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0.3;
  return Math.max(0, Math.min(1, Math.round(n * 1000) / 1000));
}

function isUserQuery(node = {}) {
  return String(node.name || '').toLowerCase() === 'user.query';
}

function readPattern(text) {
  return /\b(read|get|fetch|retrieve|search|list|find|select|query|load|scrape)\b/i.test(text);
}

function transformPattern(text) {
  return /\b(transform|extract|parse|summari[sz]e|summary|digest|brief|classify|analyze|filter|format|convert|redact|mask|sanitize|aggregate|count|hash|merge|join)\b/i.test(text);
}

function isModelNode(text) {
  return /\b(llm|model|chat|completion|openai|anthropic|dashscope|qwen|gpt|claude|gemini|inference)\b/i.test(text);
}

function isLlmConsumingTransform(text, op = '') {
  if (op !== 'transform' && !transformPattern(text)) return false;
  return /\b(summari[sz]e|summary|digest|brief|classify|extract|parse|analyze)\b/i.test(text);
}

function externalEgressPattern(text) {
  // Unambiguous transport tokens match bare. Ambiguous verbs (send/post/publish/
  // share/push) require an egress object, and dotted/underscored forms
  // (send_mail, api.call, api_request) still match, so real tool node names like
  // "webhook.post" / "api.call" / "external.api" are covered. Bare "external" and
  // bare "api" removed: they over-matched "external tool" / "API docs" prose.
  return /\b(webhooks?|https?|upload|email[._-]?send|send[._-]?mail|api[._-]call|external[._-]api|third[_\-\s]?party)\b/i.test(text)
    || /\b(?:send|posts?|publish|shares?|push)(?:ed|ing|s)?\s+(?:to|the|a|an|it|them|data|payload|request|message|report|results?|file|email|webhook|via|externally)\b/i.test(text)
    || /\b(?:post|send|publish)\s+request\b|\bhttp[s]?\s+(?:request|call|post|get)\b|\bapi\s+(?:call|request|endpoint)\b/i.test(text);
}

function localPersistencePattern(text) {
  return /\b(write|save|persist|store|append|file_write|memory_write|database_write|db_write|produce_artifact)\b|(?:create|generate|export|produce)[\s._-]*(?:artifact|report|log|file|document)/i.test(text);
}

function commandPattern(text) {
  return /\b(exec|execute|shell|command|process|spawn|run_script|subprocess)\b/i.test(text);
}

function destructivePattern(text) {
  return /\b(delete|remove|destroy|drop|truncate|wipe)\b/i.test(text);
}

function hasSinkLikeRole(roles) {
  return ['external_egress', 'model_inference', 'local_persistence', 'command_execution', 'destructive_operation', 'tool_invocation']
    .some(role => roles.has(role));
}

module.exports = {
  buildNodeProfiles,
  buildNodeProfilesWithOptions,
  buildNodeProfile,
  nodeSecurityText,
  nodeActionText,
  externalEgressPattern,
  detectActionMentions
};
