const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const {
  normalizeAssistantContent,
  normalizeValidationResult,
  postJsonWithTimeout
} = require('../../../../shared/llm-utils.cjs');

/**
 * LLM Validator for semantic verification of tool dependencies.
 * Uses provider APIs when configured and a deterministic heuristic fallback.
 */

/**
 * Load LLM prompt template
 * @returns {string} Prompt template
 */
function loadPromptTemplate() {
  const templatePath = path.join(__dirname, '..', '..', 'templates', 'llm-prompt.md');

  if (fs.existsSync(templatePath)) {
    return fs.readFileSync(templatePath, 'utf-8');
  }

  return getDefaultPromptTemplate();
}

/**
 * Get default prompt template
 * @returns {string} Default prompt template
 */
function getDefaultPromptTemplate() {
  return `# Tool Dependency Validation

## Function A (Upstream)
- **Name**: {{func_a_name}}
- **Description**: {{func_a_description}}
- **Return Type**: {{func_a_output_type}}
- **Return Example**: {{func_a_output_example}}

## Function B (Downstream)
- **Name**: {{func_b_name}}
- **Description**: {{func_b_description}}
- **Input Parameters**: {{func_b_input_params}}
- **Input Type**: {{func_b_input_type}}

## Question
Can the output of Function A be used as input for Function B?

Please consider:
1. Type compatibility
2. Semantic relevance (should A's output logically be passed to B?)
3. Common tool usage patterns

## Response Format
\`\`\`json
{
  "is_compatible": true/false,
  "confidence": 0.0-1.0,
  "reason": "Brief explanation",
  "data_flow_description": "Describe how data flows from A to B"
}
\`\`\``;
}

/**
 * Build validation prompt for a tool pair
 * @param {Object} sourceTool - Source tool
 * @param {Object} targetTool - Target tool
 * @param {string} template - Prompt template
 * @returns {string} Filled prompt
 */
function buildValidationPrompt(sourceTool, targetTool, template) {
  return template
    .replace('{{func_a_name}}', sourceTool.name || 'Unknown')
    .replace('{{func_a_description}}', sourceTool.description || 'No description')
    .replace('{{func_a_output_type}}', JSON.stringify(sourceTool.output || {}))
    .replace('{{func_a_output_example}}', JSON.stringify(sourceTool.example || {}))
    .replace('{{func_b_name}}', targetTool.name || 'Unknown')
    .replace('{{func_b_description}}', targetTool.description || 'No description')
    .replace('{{func_b_input_params}}', JSON.stringify(Object.keys(targetTool.input || {})))
    .replace('{{func_b_input_type}}', JSON.stringify(targetTool.input || {}));
}

/**
 * Call LLM for validation.
 * Falls back to deterministic heuristic if API key is unavailable or call fails.
 *
 * @param {string} prompt - Prompt to send to LLM
 * @param {Object} config - LLM configuration
 * @param {Object} context - Optional context with sourceTool/targetTool
 * @returns {Promise<Object>} Validation response
 */
async function callLLM(prompt, config = {}, context = {}) {
  const {
    provider = 'openai',
    model = 'gpt-5.5',
    apiKey = process.env.LLM_API_KEY,
    timeout = 180000,
    endpoint = '',
    disableLlm = false
  } = config;

  if (disableLlm || !String(apiKey || '').trim()) {
    return getHeuristicValidation(context.sourceTool, context.targetTool, 'Heuristic validation: LLM_API_KEY not set');
  }

  try {
    switch (provider) {
      case 'openai':
        return await callOpenAI(prompt, model, apiKey, timeout, endpoint);
      case 'dashscope':
        return await callDashScope(prompt, model, apiKey, timeout, endpoint);
      default:
        return await callOpenAI(prompt, model, apiKey, timeout, endpoint);
    }
  } catch (error) {
    return getHeuristicValidation(
      context.sourceTool,
      context.targetTool,
      `Heuristic validation: LLM call failed (${error.message})`
    );
  }
}

/**
 * Call DashScope API using its OpenAI-compatible endpoint.
 */
async function callDashScope(prompt, model, apiKey, timeout, endpoint) {
  const effectiveEndpoint =
    endpoint ||
    process.env.DASHSCOPE_ENDPOINT ||
    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';

  return callOpenAICompatible(prompt, {
    endpoint: effectiveEndpoint,
    model,
    apiKey,
    timeout
  });
}

/**
 * Call OpenAI Chat Completions API.
 */
async function callOpenAI(prompt, model, apiKey, timeout, endpoint) {
  const effectiveEndpoint = endpoint || 'https://api.openai.com/v1/chat/completions';

  return callOpenAICompatible(prompt, {
    endpoint: effectiveEndpoint,
    model,
    apiKey,
    timeout
  });
}

/**
 * Call an OpenAI-compatible chat completions endpoint and parse JSON response.
 *
 * @param {string} prompt
 * @param {Object} config
 * @returns {Promise<Object>}
 */
async function callOpenAICompatible(prompt, config) {
  const { endpoint, model, apiKey, timeout } = config;

  const payload = await postJsonWithTimeout(endpoint, {
    model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content:
          'You validate tool dependency semantics. Return strict JSON only in English with keys: is_compatible, confidence, reason, data_flow_description. is_compatible must be true or false. confidence must be a number from 0 to 1.'
      },
      {
        role: 'user',
        content: prompt
      }
    ]
  }, {
    timeoutMs: timeout,
    headers: {
      Authorization: `Bearer ${apiKey}`
    }
  });

  const parsed = normalizeValidationResult(payload?.choices?.[0]?.message?.content);
  if (!parsed) {
    throw new Error('Unable to parse LLM JSON response');
  }

  return parsed;
}

/**
 * Deterministic semantic fallback when LLM is unavailable.
 *
 * @param {Object} sourceTool
 * @param {Object} targetTool
 * @param {string} reasonPrefix
 * @returns {Object}
 */
function getHeuristicValidation(sourceTool = {}, targetTool = {}, reasonPrefix = 'Heuristic validation') {
  const outputKeys = Object.keys(sourceTool.output || {});
  const inputKeys = Object.keys(targetTool.input || {});

  const outputSet = new Set(outputKeys.map(k => k.toLowerCase()));
  const inputSet = new Set(inputKeys.map(k => k.toLowerCase()));
  const exactOverlap = outputKeys.filter(k => inputSet.has(k.toLowerCase())).length;

  const sourceTokens = tokenize(sourceTool.name, sourceTool.description, ...outputKeys);
  const targetTokens = tokenize(targetTool.name, targetTool.description, ...inputKeys);
  const sharedSemanticTokens = intersectSize(sourceTokens, targetTokens);

  let score = 0.2;
  score += Math.min(0.5, exactOverlap * 0.25);
  score += Math.min(0.25, sharedSemanticTokens * 0.05);

  const sourceName = String(sourceTool.name || '').toLowerCase();
  const targetName = String(targetTool.name || '').toLowerCase();
  if (/(get|list|read|fetch|query|search)/.test(sourceName) && /(create|update|write|send|post|insert)/.test(targetName)) {
    score += 0.15;
  }

  const confidence = clamp(score, 0.05, 0.95);
  const isCompatible = exactOverlap > 0 || sharedSemanticTokens >= 2 || confidence >= 0.65;

  return {
    is_compatible: isCompatible,
    confidence,
    reason: `${reasonPrefix}. exact_overlap=${exactOverlap}, semantic_overlap=${sharedSemanticTokens}`,
    data_flow_description: describeHeuristicFlow(outputKeys, inputKeys)
  };
}

function describeHeuristicFlow(outputKeys, inputKeys) {
  const src = outputKeys.length ? outputKeys.join(', ') : 'source_output';
  const tgt = inputKeys.length ? inputKeys.join(', ') : 'target_input';
  return `${src} -> ${tgt}`;
}

function tokenize(...parts) {
  return new Set(
    parts
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .split(/[^a-z0-9_]+/)
      .filter(token => token.length >= 3)
  );
}

function intersectSize(setA, setB) {
  let size = 0;
  for (const token of setA) {
    if (setB.has(token)) size++;
  }
  return size;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

/**
 * Validate multiple tool pairs using LLM.
 * @param {Array} compatiblePairs - Array of type-compatible pairs
 * @param {Object} config - LLM configuration
 * @returns {Promise<Array>} Array of validated edges
 */
async function validatePairs(compatiblePairs, config = {}) {
  const validatedEdges = [];
  const hasApiKey = !config.disableLlm && Boolean(String(config.apiKey || process.env.LLM_API_KEY || '').trim());
  const policy = normalizeDependencyLlmPolicy(config.dependencyLlmPolicy || process.env.FCG_DEPENDENCY_LLM_POLICY || 'high_value');
  const llmMaxPairs = hasApiKey && policy !== 'off'
    ? normalizePositiveInteger(config.dependencyLlmMaxPairs || config.llmMaxPairs || process.env.FCG_DEPENDENCY_LLM_MAX_PAIRS, 32)
    : 0;
  const batchSize = normalizePositiveInteger(
    config.dependencyLlmBatchSize || process.env.FCG_DEPENDENCY_LLM_BATCH_SIZE,
    16
  );
  const pairs = [...compatiblePairs].sort(compareValidationPairs);
  const cache = loadDependencyLlmCache(config);
  const llmSelection = selectDependencyLlmPairs(pairs, { hasApiKey, policy, llmMaxPairs });
  const llmPairKeys = new Set(llmSelection.map(pair => pairKey(pair)));
  const llmResults = new Map();
  const statistics = {
    dependency_llm_policy: policy,
    dependency_llm_candidate_count: llmSelection.length,
    dependency_llm_validated_count: 0,
    dependency_llm_cache_hit_count: 0,
    dependency_llm_request_count: 0,
    dependency_llm_error_count: 0
  };

  const uncached = [];
  for (const pair of llmSelection) {
    const key = buildDependencyCacheKey(pair, config);
    pair._dependency_cache_key = key;
    const cached = cache.records.get(key);
    if (cached) {
      llmResults.set(pairKey(pair), { ...cached, cache_hit: true });
      statistics.dependency_llm_cache_hit_count += 1;
    } else {
      uncached.push(pair);
    }
  }

  for (const batch of chunk(uncached, batchSize)) {
    try {
      const batchResults = await validateDependencyPairBatch(batch, config);
      statistics.dependency_llm_request_count += 1;
      for (const pair of batch) {
        const result = batchResults.get(pair.candidate_id) || batchResults.get(pairKey(pair));
        if (!result) continue;
        const normalized = normalizeDependencyBatchResult(result);
        if (!normalized) continue;
        llmResults.set(pairKey(pair), normalized);
        appendDependencyCacheRecord(cache, pair._dependency_cache_key, normalized, config);
      }
    } catch (error) {
      statistics.dependency_llm_error_count += batch.length;
    }
  }

  for (const pair of pairs) {
    const selectedForLlm = llmPairKeys.has(pairKey(pair));
    const llmResult = llmResults.get(pairKey(pair));
    const useLlm = Boolean(llmResult);
    const result = useLlm
      ? llmResult
      : getHeuristicValidation(
          pair.source,
          pair.target,
          ruleReasonPrefix({ hasApiKey, policy, selectedForLlm, llmMaxPairs, totalPairs: pairs.length })
        );
    const heuristicPass = !useLlm && pair.confidence >= 0.8;

    if (result.is_compatible || heuristicPass) {
      const combinedConfidence = result.is_compatible
        ? clamp(result.confidence * pair.confidence, 0, 1)
        : clamp(pair.confidence * 0.7, 0, 1);

      validatedEdges.push({
        id: `edge_${validatedEdges.length + 1}`,
        source: pair.source.id || pair.source.name,
        target: pair.target.id || pair.target.name,
        type: 'data_dependency',
        confidence: combinedConfidence,
        validation_method: useLlm
          ? 'dependency_llm_high_value'
          : 'dependency_rule',
        data_flow: {
          from_param: pair.compatibleParams[0]?.fromParam || 'unknown',
          to_param: pair.compatibleParams[0]?.toParam || 'unknown',
          data_type: pair.compatibleParams[0]?.fromType || 'string'
        },
        semantic_reason: result.is_compatible
          ? result.reason
          : 'Rule fallback accepted high-confidence sparse dependency edge',
        candidate_id: pair.candidate_id || '',
        candidate_kind: pair.candidate_kind || '',
        candidate_reason: pair.candidate_reason || '',
        high_value_reasons: pair.high_value_reasons || [],
        ...(useLlm ? { llm_review: { cache_hit: Boolean(llmResult.cache_hit) } } : {})
      });
      if (useLlm) statistics.dependency_llm_validated_count += 1;
    }
  }

  Object.defineProperty(validatedEdges, 'statistics', {
    enumerable: false,
    value: statistics
  });

  return validatedEdges;
}

function selectDependencyLlmPairs(pairs = [], { hasApiKey, policy, llmMaxPairs }) {
  if (!hasApiKey || policy === 'off' || llmMaxPairs <= 0) return [];
  const eligible = policy === 'all'
    ? pairs
    : pairs.filter(pair => pair.high_value || (pair.high_value_reasons || []).length > 0);
  return eligible
    .slice()
    .sort(compareDependencyLlmPriority)
    .slice(0, llmMaxPairs);
}

function compareDependencyLlmPriority(a, b) {
  const priorityDelta = Number(a.llm_priority || 50) - Number(b.llm_priority || 50);
  if (priorityDelta !== 0) return priorityDelta;
  const reasonDelta = Number((b.high_value_reasons || []).length) - Number((a.high_value_reasons || []).length);
  if (reasonDelta !== 0) return reasonDelta;
  const uncertaintyA = Math.abs(Number(a.confidence || 0.5) - 0.65);
  const uncertaintyB = Math.abs(Number(b.confidence || 0.5) - 0.65);
  if (uncertaintyA !== uncertaintyB) return uncertaintyA - uncertaintyB;
  return validationPairKey(a).localeCompare(validationPairKey(b));
}

async function validateDependencyPairBatch(pairs, config = {}) {
  if (!pairs.length) return new Map();

  if (typeof config.semanticBatchValidator === 'function') {
    return normalizeDependencyBatchMap(await config.semanticBatchValidator({
      candidates: pairs.map(serializeDependencyCandidate),
      config
    }));
  }

  if (typeof config.semanticValidator === 'function') {
    const results = new Map();
    for (const pair of pairs) {
      const prompt = buildValidationPrompt(pair.source, pair.target, loadPromptTemplate());
      const result = await config.semanticValidator({ sourceTool: pair.source, targetTool: pair.target, prompt, config, pair });
      results.set(pair.candidate_id || pairKey(pair), result);
    }
    return results;
  }

  const response = await callDependencyBatchLLM(pairs, config);
  return normalizeDependencyBatchMap(response);
}

async function callDependencyBatchLLM(pairs, config = {}) {
  const {
    provider = 'openai',
    model = 'gpt-5.5',
    apiKey = process.env.LLM_API_KEY,
    timeout = 180000,
    endpoint = ''
  } = config;

  const effectiveEndpoint = provider === 'dashscope'
    ? (endpoint || process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
    : (endpoint || 'https://api.openai.com/v1/chat/completions');

  const payload = await postJsonWithTimeout(effectiveEndpoint, {
    model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: 'You validate high-value FCG dependency candidates. Return strict JSON only: {"results":[{"candidate_id":"...","is_compatible":true|false,"confidence":0..1,"reason":"...","data_flow_description":"..."}]}.'
      },
      {
        role: 'user',
        content: JSON.stringify({
          task: 'Accept only candidates where source output or context should flow to target input in the skill runtime/control flow.',
          candidates: pairs.map(serializeDependencyCandidate)
        })
      }
    ]
  }, {
    timeoutMs: timeout,
    headers: {
      Authorization: `Bearer ${apiKey}`
    }
  });

  return payload?.choices?.[0]?.message?.content;
}

function serializeDependencyCandidate(pair = {}) {
  return {
    candidate_id: pair.candidate_id || pairKey(pair),
    source: compactNodeForDependency(pair.source),
    target: compactNodeForDependency(pair.target),
    compatible_params: pair.compatibleParams || [],
    rule_confidence: pair.confidence,
    candidate_kind: pair.candidate_kind || '',
    candidate_reason: pair.candidate_reason || '',
    high_value_reasons: pair.high_value_reasons || []
  };
}

function compactNodeForDependency(node = {}) {
  const semantics = node.formal_semantics || {};
  const sourceContext = node.source_context || {};
  return {
    id: node.id || '',
    name: node.name || '',
    canonical_name: node.canonical_name || '',
    semantic_kind: node.semanticKind || '',
    operation_type: semantics.operation_type || node.operationType || '',
    file: node.location?.file || '',
    line: node.location?.line || 0,
    instruction: node.instructionText || semantics.evidence?.text || sourceContext.source_line || '',
    action_evidence: sourceContext.action_evidence || undefined,
    targets: semantics.targets || [],
    effects: semantics.effects || []
  };
}

function normalizeDependencyBatchMap(raw) {
  if (raw instanceof Map) return raw;
  const parsed = parseLooseJson(raw);
  const values = Array.isArray(parsed) ? parsed : (Array.isArray(parsed?.results) ? parsed.results : []);
  const results = new Map();
  for (const item of values) {
    const normalized = normalizeDependencyBatchResult(item);
    if (!normalized) continue;
    const id = String(item.candidate_id || item.id || item.candidate || '').trim();
    if (id) results.set(id, normalized);
  }
  return results;
}

function normalizeDependencyBatchResult(raw) {
  if (!raw || typeof raw !== 'object') return normalizeValidationResult(raw);
  const confidence = Number(raw.confidence ?? raw.score ?? 0.5);
  return {
    is_compatible: normalizeBooleanLike(raw.is_compatible ?? raw.accepted ?? raw.compatible, false),
    confidence: clamp(Number.isFinite(confidence) ? confidence : 0.5, 0, 1),
    reason: String(raw.reason || raw.explanation || '').trim() || 'LLM high-value dependency review',
    data_flow_description: String(raw.data_flow_description || raw.flow || '').trim() || 'Data flows from source to target'
  };
}

function normalizeDependencyLlmPolicy(value) {
  const policy = String(value || '').trim().toLowerCase();
  if (['off', 'none', 'false', '0'].includes(policy)) return 'off';
  if (policy === 'all') return 'all';
  return 'high_value';
}

function ruleReasonPrefix({ hasApiKey, policy, selectedForLlm, llmMaxPairs, totalPairs }) {
  if (!hasApiKey) return 'Rule dependency validation: LLM_API_KEY not set';
  if (policy === 'off') return 'Rule dependency validation: dependency LLM policy is off';
  if (selectedForLlm) return 'Rule dependency validation: selected high-value LLM candidate had no valid LLM result';
  return `Rule dependency validation: not selected for high-value LLM budget (${llmMaxPairs}/${totalPairs})`;
}

function loadDependencyLlmCache(config = {}) {
  const cachePath = resolveDependencyLlmCachePath(config);
  const cache = {
    path: cachePath,
    records: new Map(),
    enabled: Boolean(cachePath)
  };
  if (!cache.enabled || !fs.existsSync(cachePath)) return cache;

  try {
    for (const line of fs.readFileSync(cachePath, 'utf-8').split(/\r?\n/)) {
      if (!line.trim()) continue;
      const record = JSON.parse(line);
      if (record?.key && record?.result) cache.records.set(record.key, record.result);
    }
  } catch {
    cache.enabled = false;
  }
  return cache;
}

function resolveDependencyLlmCachePath(config = {}) {
  if (config.dependencyLlmCache === false || process.env.FCG_DEPENDENCY_LLM_CACHE === '0') return '';
  if (typeof config.dependencyLlmCache === 'string' && config.dependencyLlmCache.trim()) {
    return path.resolve(config.dependencyLlmCache.trim());
  }
  if (process.env.FCG_DEPENDENCY_LLM_CACHE && process.env.FCG_DEPENDENCY_LLM_CACHE.trim()) {
    return path.resolve(process.env.FCG_DEPENDENCY_LLM_CACHE.trim());
  }
  return path.join(os.tmpdir(), 'skill-fcg-dependency-llm-cache.jsonl');
}

function buildDependencyCacheKey(pair = {}, config = {}) {
  const hashInput = {
    prompt_version: 'fcg-dependency-llm-v1',
    model: config.model || process.env.LLM_MODEL || 'gpt-5.5',
    source: cacheNodeFingerprint(pair.source),
    target: cacheNodeFingerprint(pair.target),
    candidate_kind: pair.candidate_kind || '',
    candidate_reason: pair.candidate_reason || '',
    compatibleParams: pair.compatibleParams || []
  };
  return `dep_llm_${shortHash(JSON.stringify(hashInput))}`;
}

function cacheNodeFingerprint(node = {}) {
  return {
    id: node.id || '',
    name: node.name || '',
    semanticKind: node.semanticKind || '',
    file: node.location?.file || '',
    line: node.location?.line || 0,
    action_evidence: node.source_context?.action_evidence || '',
    source_line: node.source_context?.source_line || '',
    instructionText: node.instructionText || '',
    formal_text: node.formal_semantics?.evidence?.text || ''
  };
}

function appendDependencyCacheRecord(cache, key, result) {
  if (!cache?.enabled || !cache.path || !key || !result || cache.records.has(key)) return;
  try {
    fs.mkdirSync(path.dirname(cache.path), { recursive: true });
    fs.appendFileSync(cache.path, `${JSON.stringify({ key, result, cached_at: new Date().toISOString() })}\n`, 'utf-8');
    cache.records.set(key, result);
  } catch {
    cache.enabled = false;
  }
}

function parseLooseJson(raw) {
  if (raw && typeof raw === 'object') return raw;
  const text = normalizeAssistantContent(raw).trim();
  if (!text) return null;
  const candidates = [text];
  const fenced = text.match(/```json\s*([\s\S]*?)```/i);
  if (fenced) candidates.push(fenced[1].trim());
  const objectLike = text.match(/\{[\s\S]*\}/);
  if (objectLike) candidates.push(objectLike[0]);
  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch {
      // try next
    }
  }
  return null;
}

function normalizeBooleanLike(value, fallback = false) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  const text = String(value || '').trim().toLowerCase();
  if (['true', 'yes', 'y', '1', 'accept', 'accepted', 'compatible'].includes(text)) return true;
  if (['false', 'no', 'n', '0', 'reject', 'rejected', 'incompatible'].includes(text)) return false;
  return fallback;
}

function chunk(items = [], size = 16) {
  const chunks = [];
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size));
  }
  return chunks;
}

function pairKey(pair = {}) {
  return `${pair.source?.name || ''}->${pair.target?.name || ''}`;
}

function shortHash(value) {
  return crypto.createHash('sha1').update(String(value || '')).digest('hex').slice(0, 16);
}

function compareValidationPairs(a, b) {
  const priorityDelta = Number(a.llm_priority || 50) - Number(b.llm_priority || 50);
  if (priorityDelta !== 0) return priorityDelta;
  const confidenceDelta = Number(b.confidence || 0) - Number(a.confidence || 0);
  if (confidenceDelta !== 0) return confidenceDelta;
  return validationPairKey(a).localeCompare(validationPairKey(b));
}

function validationPairKey(pair) {
  return [
    pair?.source?.name || '',
    pair?.target?.name || '',
    pair?.compatibleParams?.[0]?.fromParam || '',
    pair?.compatibleParams?.[0]?.toParam || ''
  ].join('::');
}

function normalizePositiveInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

module.exports = {
  loadPromptTemplate,
  buildValidationPrompt,
  callLLM,
  validatePairs,
  getHeuristicValidation,
  normalizeAssistantContent,
  normalizeValidationResult
};
