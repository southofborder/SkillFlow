/**
 * Type system for compatibility checking
 * Defines which types are compatible with each other
 */
const TypeSystem = {
  // Base types
  'string': { compatible_with: ['string', 'text'] },
  'number': { compatible_with: ['number', 'integer', 'float'] },
  'boolean': { compatible_with: ['boolean'] },
  'array': { compatible_with: ['array', 'list'] },
  'object': { compatible_with: ['object', 'dict', 'map'] },
  
  // Business types
  'app_token': { compatible_with: ['string', 'app_token'] },
  'table_id': { compatible_with: ['string', 'table_id'] },
  'record_id': { compatible_with: ['string', 'record_id'] },
  'user_id': { compatible_with: ['string', 'open_id', 'user_id'] },
  'chat_id': { compatible_with: ['string', 'chat_id'] },
  'timestamp': { compatible_with: ['number', 'string', 'timestamp'] },
  'date': { compatible_with: ['string', 'number', 'date', 'timestamp'] },
  
  // Composite types
  'file_content': { compatible_with: ['string', 'file_content', 'text'] },
  'message': { compatible_with: ['string', 'message', 'text'] },
  'structured_data': { compatible_with: ['object', 'array', 'structured_data'] }
};

/**
 * Check if two types are compatible
 * @param {string} returnType - The return type of the source function
 * @param {string} inputType - The input type of the target function
 * @returns {boolean} Whether the types are compatible
 */
function isTypeCompatible(returnType, inputType) {
  // Rule 1: Type equivalence
  if (returnType === inputType) return true;
  
  // Rule 2: Type in compatibility list
  const returnTypeInfo = TypeSystem[returnType];
  if (returnTypeInfo && returnTypeInfo.compatible_with.includes(inputType)) {
    return true;
  }
  
  // Rule 3: Array element type matching
  if (inputType.startsWith('array<') && returnType === inputType.match(/<(.+)>/)?.[1]) {
    return true;
  }
  
  // Rule 4: string can match most business types
  if (returnType === 'string' && !['boolean', 'number'].includes(inputType)) {
    return true;
  }
  
  return false;
}

/**
 * Analyze sparse dependency candidates between extracted nodes.
 * @param {Array} tools - Array of extracted tools
 * @returns {Array} Array of compatible tool pairs
 */
function analyzeTypeCompatibility(tools, options = {}) {
  const allNodes = tools || [];
  const eligibleNodes = allNodes.filter(isDependencyCandidateNode);
  const rawPairUpperBound = eligibleNodes.length * Math.max(0, eligibleNodes.length - 1);
  const maxCandidates = normalizePositiveInteger(
    options.maxCandidates ?? process.env.FCG_DEPENDENCY_MAX_CANDIDATES,
    2000
  );
  const scopeWindow = normalizePositiveInteger(
    options.scopeWindow ?? process.env.FCG_DEPENDENCY_SCOPE_WINDOW,
    4
  );
  const candidateMap = new Map();

  addScopedSequenceCandidates(candidateMap, eligibleNodes, scopeWindow);
  addExplicitReferenceCandidates(candidateMap, eligibleNodes);
  addBoundaryImpactCandidates(candidateMap, eligibleNodes);
  addGlobalRouteCandidates(candidateMap, eligibleNodes);

  const candidates = Array.from(candidateMap.values())
    .sort(compareDependencyCandidates)
    .slice(0, maxCandidates)
    .map((candidate, index) => ({
      ...candidate,
      candidate_id: candidate.candidate_id || `dep_${String(index + 1).padStart(4, '0')}`
    }));

  Object.defineProperty(candidates, 'statistics', {
    enumerable: false,
    value: {
      dependency_candidate_count: candidates.length,
      dependency_candidate_pruned_count: Math.max(0, rawPairUpperBound - candidates.length),
      dependency_candidate_raw_upper_bound: rawPairUpperBound,
      dependency_candidate_max: maxCandidates
    }
  });

  return candidates;
}

function addScopedSequenceCandidates(candidateMap, nodes, scopeWindow) {
  const byFile = groupBy(nodes.filter(node => node.location?.file), node => normalizePath(node.location.file));
  for (const group of byFile.values()) {
    const sorted = group
      .slice()
      .sort((a, b) => Number(a.location?.line || 0) - Number(b.location?.line || 0));
    for (let index = 0; index < sorted.length; index += 1) {
      const source = sorted[index];
      let seen = 0;
      for (let next = index + 1; next < sorted.length && seen < scopeWindow; next += 1) {
        const target = sorted[next];
        seen += 1;
        if (isLowValueScriptCallPair(source, target)) continue;
        addCandidate(candidateMap, source, target, {
          kind: 'scoped_sequence',
          reason: 'same file local execution/document order',
          priority: isBoundaryLikeNode(target) ? 20 : 55
        });
      }
    }
  }
}

function addExplicitReferenceCandidates(candidateMap, nodes) {
  const tokenMap = new Map();
  for (const node of nodes) {
    for (const token of meaningfulReferenceTokens(node)) {
      if (!tokenMap.has(token)) tokenMap.set(token, []);
      tokenMap.get(token).push(node);
    }
  }

  for (const [token, bucket] of tokenMap.entries()) {
    if (bucket.length < 2 || bucket.length > 24) continue;
    for (const source of bucket) {
      for (const target of bucket) {
        if (source === target) continue;
        if (!isLikelyForwardReference(source, target)) continue;
        addCandidate(candidateMap, source, target, {
          kind: 'explicit_reference',
          reason: `shared explicit reference token: ${token}`,
          priority: isBoundaryLikeNode(target) ? 15 : 35
        });
      }
    }
  }
}

function addBoundaryImpactCandidates(candidateMap, nodes) {
  const byFile = groupBy(nodes.filter(node => node.location?.file), node => normalizePath(node.location.file));
  for (const target of nodes.filter(isBoundaryLikeNode)) {
    const fileGroup = byFile.get(normalizePath(target.location?.file || '')) || [];
    const before = fileGroup
      .filter(source => source !== target && Number(source.location?.line || 0) <= Number(target.location?.line || 0))
      .sort((a, b) => Number(b.location?.line || 0) - Number(a.location?.line || 0))
      .slice(0, 8);
    for (const source of before) {
      addCandidate(candidateMap, source, target, {
        kind: 'boundary_impact',
        reason: 'nearby source may affect boundary observation',
        priority: 5
      });
    }
  }
}

function addGlobalRouteCandidates(candidateMap, nodes) {
  const routeSources = nodes.filter(node => isRouteContextNode(node) || isDocActionNode(node));
  const routeTargets = nodes.filter(node => isExecutableOrToolNode(node) || isBoundaryLikeNode(node));
  for (const source of routeSources) {
    for (const target of routeTargets) {
      if (source === target) continue;
      if (!isCrossStagePair(source, target)) continue;
      if (!hasMeaningfulTokenOverlap(source, target)) continue;
      addCandidate(candidateMap, source, target, {
        kind: 'global_route',
        reason: 'cross-file or cross-stage route candidate',
        priority: isBoundaryLikeNode(target) ? 10 : 25
      });
    }
  }
}

function addCandidate(candidateMap, sourceTool, targetTool, meta = {}) {
  if (!sourceTool?.name || !targetTool?.name) return;
  if (sourceTool.name === targetTool.name) return;
  if (!isReasonableDirection(sourceTool, targetTool)) return;
  if (!isCallSiteOrderCompatible(sourceTool, targetTool)) return;
  if (isGlobalLlmCallSitePair(sourceTool, targetTool)) return;
  if (isContextOnlyNode(sourceTool) || isContextOnlyNode(targetTool)) return;
  if (isLowValueScriptCallPair(sourceTool, targetTool) && meta.kind !== 'boundary_impact') return;

  const compatibleParams = findCompatibleParams(sourceTool, targetTool);
  if (!compatibleParams.length) return;

  const key = `${sourceTool.name}->${targetTool.name}`;
  const confidence = calculateTypeConfidence(compatibleParams);
  const highValueReasons = highValueReasonsForPair(sourceTool, targetTool, meta);
  const candidate = {
    source: sourceTool,
    target: targetTool,
    compatibleParams,
    confidence,
    candidate_kind: meta.kind || 'dependency_rule',
    candidate_reason: meta.reason || 'sparse dependency candidate',
    high_value: highValueReasons.length > 0,
    high_value_reasons: highValueReasons,
    llm_priority: Number(meta.priority || 50) - highValueReasons.length * 10
  };

  const existing = candidateMap.get(key);
  if (!existing || compareDependencyCandidates(candidate, existing) < 0) {
    candidateMap.set(key, candidate);
  }
}

/**
 * Find compatible parameters between source and target tools
 * @param {Object} sourceTool - Source tool
 * @param {Object} targetTool - Target tool
 * @returns {Array} Array of compatible parameter pairs
 */
function findCompatibleParams(sourceTool, targetTool) {
  const compatible = [];
  
  const sourceOutputs = withFallbackOutputs(sourceTool);
  const targetInputs = withFallbackInputs(targetTool);
  
  for (const [outputParam, outputInfo] of Object.entries(sourceOutputs)) {
    for (const [inputParam, inputInfo] of Object.entries(targetInputs)) {
      const outputType = outputInfo.type || 'string';
      const inputType = inputInfo.type || 'string';
      
      const nameCompatibility = isParamNameCompatible(outputParam, inputParam);
      if (isTypeCompatible(outputType, inputType) && nameCompatibility) {
        compatible.push({
          fromParam: outputParam,
          toParam: inputParam,
          fromType: outputType,
          toType: inputType
        });
      }
    }
  }
  
  return compatible;
}

/**
 * Calculate confidence score based on type compatibility
 * @param {Array} compatibleParams - Array of compatible parameter pairs
 * @returns {number} Confidence score (0.0-1.0)
 */
function calculateTypeConfidence(compatibleParams) {
  if (compatibleParams.length === 0) return 0;
  
  // Base confidence from number of compatible params
  let confidence = Math.min(0.5 + compatibleParams.length * 0.1, 0.9);
  
  // Boost confidence for exact type matches
  const exactMatches = compatibleParams.filter(p => p.fromType === p.toType).length;
  confidence += exactMatches * 0.05;
  
  // Boost confidence for parameter name matches
  const nameMatches = compatibleParams.filter(p => p.fromParam === p.toParam).length;
  confidence += nameMatches * 0.05;
  
  return Math.min(confidence, 1.0);
}

function withFallbackOutputs(tool) {
  const output = { ...(tool.output || {}) };
  if (Object.keys(output).length > 0) return output;

  const action = getAction(tool);
  if (/get|read|fetch|query|find|retrieve/.test(action)) {
    output.data = { type: 'object' };
  } else if (/list|search/.test(action)) {
    output.items = { type: 'array' };
  } else if (/create|add|insert/.test(action)) {
    output.success = { type: 'boolean' };
    output.id = { type: 'string' };
  } else if (/update|write|delete|remove|send|post|publish/.test(action)) {
    output.success = { type: 'boolean' };
  }

  if (Object.keys(output).length === 0) {
    output.result = { type: 'object' };
  }

  return output;
}

function withFallbackInputs(tool) {
  const input = { ...(tool.input || {}) };
  if (Object.keys(input).length > 0) return input;

  const action = getAction(tool);
  if (/create|add|insert|update|write|send|post|publish/.test(action)) {
    input.payload = { type: 'object' };
  } else if (/get|list|search|query|fetch|read/.test(action)) {
    input.filter = { type: 'object', required: false };
  } else {
    input.context = { type: 'object', required: false };
  }
  return input;
}

function isReasonableDirection(sourceTool, targetTool) {
  const srcAction = getAction(sourceTool);
  const tgtAction = getAction(targetTool);

  // Avoid obvious reverse edges from pure sinks to pure sources.
  if (/(create|add|insert|update|write|send|post|publish|delete|remove)/.test(srcAction) &&
      /(get|list|search|query|fetch|read|retrieve|find|select)/.test(tgtAction)) {
    return false;
  }

  return true;
}

function isCallSiteOrderCompatible(sourceTool, targetTool) {
  const sourceOrder = Number(sourceTool.callsite_order || 0);
  const targetOrder = Number(targetTool.callsite_order || 0);
  if (!sourceOrder || !targetOrder) return true;
  return sourceOrder < targetOrder;
}

function isGlobalLlmCallSitePair(sourceTool, targetTool) {
  if (!sourceTool?.callsite_id && !targetTool?.callsite_id) return false;
  return sourceTool?.name === 'llm.inference' || targetTool?.name === 'llm.inference';
}

function getAction(tool) {
  if (tool && typeof tool.action === 'string' && tool.action) {
    return tool.action.toLowerCase();
  }
  const name = String(tool?.name || '').toLowerCase();
  return name.split('.').pop() || '';
}

function isParamNameCompatible(fromParam, toParam) {
  const src = String(fromParam || '').toLowerCase();
  const tgt = String(toParam || '').toLowerCase();
  if (!src || !tgt) return true;
  if (src === tgt) return true;

  // Keep only informative tokens and compare overlap.
  const srcTokens = new Set(src.split(/[^a-z0-9]+/).filter(token => token.length >= 3));
  const tgtTokens = new Set(tgt.split(/[^a-z0-9]+/).filter(token => token.length >= 3));
  if (srcTokens.size === 0 || tgtTokens.size === 0) return true;

  for (const token of srcTokens) {
    if (tgtTokens.has(token)) return true;
  }

  // Allow generic payload/data/result parameters.
  const generic = new Set(['data', 'payload', 'result', 'items', 'content', 'body']);
  return generic.has(src) || generic.has(tgt);
}

const CONTEXT_ONLY_KINDS = new Set([
  'doc_definition',
  'doc_schema',
  'doc_template',
  'doc_example',
  'doc_discard',
  'doc_review_error'
]);

const ROUTE_CONTEXT_KINDS = new Set([
  'doc_step',
  'doc_operation',
  'trigger',
  'policy'
]);

const GENERIC_REFERENCE_TOKENS = new Set([
  'data',
  'payload',
  'result',
  'context',
  'content',
  'object',
  'string',
  'boolean',
  'number',
  'array',
  'items',
  'script',
  'function',
  'call',
  'node',
  'step',
  'read',
  'write',
  'invoke',
  'tool',
  'model',
  'local',
  'runtime'
]);

function isDependencyCandidateNode(node = {}) {
  if (!node?.name) return false;
  if (node.callsite_id || /^llm\.inference#/i.test(String(node.name || ''))) return false;
  if (isContextOnlyNode(node)) return false;
  if (node.excludeFromTypeAnalysis && !ROUTE_CONTEXT_KINDS.has(node.semanticKind)) return false;
  return true;
}

function isContextOnlyNode(node = {}) {
  return CONTEXT_ONLY_KINDS.has(node.semanticKind) ||
    (node.excludeFromFlow === true && String(node.operationType || node.formal_semantics?.operation_type || '') === 'context');
}

function isDocActionNode(node = {}) {
  return ['doc_step', 'doc_operation'].includes(node.semanticKind) && !isContextOnlyNode(node);
}

function isRouteContextNode(node = {}) {
  return ROUTE_CONTEXT_KINDS.has(node.semanticKind);
}

function isExecutableOrToolNode(node = {}) {
  return ['script_entry', 'script_function', 'script_call'].includes(node.semanticKind) ||
    node.type === 'tool_call' ||
    Boolean(node.canonical_name && !String(node.name || '').startsWith('llm.inference'));
}

function isBoundaryLikeNode(node = {}) {
  const text = [
    node.name,
    node.canonical_name,
    node.action,
    node.operationType,
    node.formal_semantics?.operation_type,
    ...(node.formal_semantics?.effects || []),
    ...(node.formal_semantics?.targets || []).map(target => `${target.type || ''}:${target.value || ''}:${target.raw || ''}`)
  ].filter(Boolean).join(' ').toLowerCase();

  return hasBoundaryTerm(text, ['external_egress', 'webhook', 'http', 'https', 'curl', 'fetch', 'post', 'send', 'upload', 'publish', 'api']) ||
    hasBoundaryTerm(text, ['model_inference', 'llm', 'openai', 'anthropic', 'dashscope', 'gpt', 'claude', 'gemini', 'model_context']) ||
    hasBoundaryTerm(text, ['persist', 'save', 'write', 'append', 'database', 'db', 'file_write', 'local_file', 'storage', 'artifact']) ||
    hasBoundaryTerm(text, ['user_visible', 'display', 'show', 'render', 'print', 'stdout']);
}

function hasBoundaryTerm(text, terms = []) {
  const normalized = String(text || '').replace(/[^a-z0-9_:/.-]+/g, ' ');
  return terms.some(term => {
    if (term === 'http' || term === 'https') return normalized.includes(`${term}:`);
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp(`(^|[^a-z0-9_])${escaped}([^a-z0-9_]|$)`, 'i').test(normalized);
  });
}

function highValueReasonsForPair(source, target, meta = {}) {
  const reasons = [];
  if (meta.kind === 'boundary_impact' || isBoundaryLikeNode(target)) reasons.push('boundary-impact');
  if (meta.kind === 'global_route' || isCrossStagePair(source, target)) reasons.push('global-route');
  return Array.from(new Set(reasons));
}

function isLowValueScriptCallPair(source = {}, target = {}) {
  return source.semanticKind === 'script_call' &&
    target.semanticKind === 'script_call' &&
    !isBoundaryLikeNode(target);
}

function isLikelyForwardReference(source = {}, target = {}) {
  if (source.location?.file && target.location?.file && normalizePath(source.location.file) === normalizePath(target.location.file)) {
    return Number(source.location?.line || 0) <= Number(target.location?.line || 0);
  }
  return isCrossStagePair(source, target) || isBoundaryLikeNode(target);
}

function isCrossStagePair(source = {}, target = {}) {
  const sourceStage = nodeStage(source);
  const targetStage = nodeStage(target);
  return Boolean(sourceStage && targetStage && sourceStage !== targetStage);
}

function nodeStage(node = {}) {
  if (String(node.name || '') === 'user.query') return 'user';
  if (String(node.name || '').startsWith('llm.inference')) return 'llm';
  if (String(node.semanticKind || '').startsWith('doc_') || ['trigger', 'policy'].includes(node.semanticKind)) return 'doc';
  if (String(node.semanticKind || '').startsWith('script_')) return 'script';
  if (node.type === 'tool_call' || node.canonical_name) return 'tool';
  return '';
}

function meaningfulReferenceTokens(node = {}) {
  const semantics = node.formal_semantics || {};
  const values = [
    node.name,
    node.canonical_name,
    node.docRef,
    node.ownerDoc,
    node.ownerScript,
    node.functionName,
    node.callee,
    node.instructionText,
    semantics.evidence?.produced_object_key,
    semantics.evidence?.consumed_object_key,
    ...(semantics.targets || []).flatMap(target => [target.type, target.value, target.raw]),
    ...(semantics.inputs || []).flatMap(input => [input.name, input.type]),
    ...(semantics.outputs || []).flatMap(output => [output.name, output.type])
  ];

  return new Set(tokenizeText(values.join(' '))
    .filter(token => token.length >= 4 && !GENERIC_REFERENCE_TOKENS.has(token)));
}

function hasMeaningfulTokenOverlap(source, target) {
  const sourceTokens = meaningfulReferenceTokens(source);
  if (!sourceTokens.size) return false;
  for (const token of meaningfulReferenceTokens(target)) {
    if (sourceTokens.has(token)) return true;
  }
  return false;
}

function tokenizeText(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .split(/[^a-z0-9]+/)
    .filter(Boolean);
}

function groupBy(items, keyFn) {
  const grouped = new Map();
  for (const item of items || []) {
    const key = keyFn(item);
    if (!key) continue;
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(item);
  }
  return grouped;
}

function normalizePath(value = '') {
  return String(value || '').replace(/\\/g, '/').toLowerCase();
}

function compareDependencyCandidates(a, b) {
  const priorityDelta = Number(a.llm_priority || 50) - Number(b.llm_priority || 50);
  if (priorityDelta !== 0) return priorityDelta;
  const highValueDelta = Number(Boolean(b.high_value)) - Number(Boolean(a.high_value));
  if (highValueDelta !== 0) return highValueDelta;
  const confidenceDelta = Number(b.confidence || 0) - Number(a.confidence || 0);
  if (confidenceDelta !== 0) return confidenceDelta;
  return dependencyCandidateKey(a).localeCompare(dependencyCandidateKey(b));
}

function dependencyCandidateKey(candidate = {}) {
  return [
    candidate.source?.name || '',
    candidate.target?.name || '',
    candidate.candidate_kind || ''
  ].join('::');
}

function normalizePositiveInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

/**
 * Infer type from value or description
 * @param {*} value - Value to infer type from
 * @returns {string} Inferred type
 */
function inferType(value) {
  if (typeof value === 'string') return 'string';
  if (typeof value === 'number') return 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (Array.isArray(value)) return 'array';
  if (typeof value === 'object') return 'object';
  return 'string';
}

module.exports = {
  TypeSystem,
  isTypeCompatible,
  analyzeTypeCompatibility,
  findCompatibleParams,
  calculateTypeConfidence,
  inferType,
  isDependencyCandidateNode,
  isContextOnlyNode,
  isBoundaryLikeNode
};
