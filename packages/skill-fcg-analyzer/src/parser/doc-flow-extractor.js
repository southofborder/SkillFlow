const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const {
  normalizeAssistantContent,
  parseLooseJson,
  normalizeScaledNumber,
  postJsonWithTimeout
} = require('../../../../shared/llm-utils.cjs');
const { buildSourceContext } = require('./document-context');
const { classifyShellCommandLine, isShellFenceLang } = require('./shell-command-classifier');

const BACKTICK_FILE_REF_REGEX = /`([^`\n]+?\.md)`/gi;
const PLAIN_FILE_REF_REGEX = /(?:^|[\s(])([~./A-Za-z0-9_-]+(?:\/[~./A-Za-z0-9_-]+)*\.md)\b/gi;
const SEMANTIC_GATE_PROMPT_VERSION = 'fcg-doc-semantic-gate-v4-negation';
const DEFAULT_SEMANTIC_GATE_BATCH_SIZE = 10;
const DEFAULT_SEMANTIC_GATE_BATCH_CONCURRENCY = 4;
const DEFAULT_SEMANTIC_GATE_MAX_BATCH_CHARS = 60000;

// Endpoint-reported token usage for the semantic gate, summed across every
// actual model call. Zero extra API cost: usage ships inside each existing
// response body; we just stop discarding it. cached_tokens quantifies the
// prompt-caching win — the constant system prefix is re-billed at a discount
// (observed ~90% hit). Mirrors DOE's llm_token_usage accounting so a broken
// cache prefix shows up as a hit-ratio drop instead of a silent cost regression.
function newSemanticGateUsage() {
  return { calls: 0, prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, cached_tokens: 0 };
}

function accumulateSemanticGateUsage(acc, usage) {
  if (!acc || !usage || typeof usage !== 'object') return;
  acc.calls += 1;
  acc.prompt_tokens += Number(usage.prompt_tokens || usage.input_tokens || 0);
  acc.completion_tokens += Number(usage.completion_tokens || usage.output_tokens || 0);
  acc.total_tokens += Number(usage.total_tokens || 0);
  acc.cached_tokens += Number(
    usage.prompt_tokens_details?.cached_tokens
    ?? usage.cached_tokens
    ?? usage.prompt_cache_hit_tokens
    ?? 0
  );
}

function summarizeSemanticGateUsage(acc) {
  if (!acc || !acc.calls) return null;
  const cacheHitRatio = acc.prompt_tokens ? Math.round((acc.cached_tokens / acc.prompt_tokens) * 1000) / 1000 : 0;
  return { ...acc, prompt_cache_hit_ratio: cacheHitRatio };
}

const READ_KEYWORDS = [
  'read', 'load', 'search', 'show', 'list', 'query', 'review', 'check', 'inspect', 'open',
  'get', 'fetch', 'retrieve'
];

const WRITE_KEYWORDS = [
  'write', 'save', 'log', 'add', 'append', 'store', 'persist', 'export', 'record',
  'update', 'promote', 'demote', 'archive', 'remove', 'delete'
];

const RUN_KEYWORDS = [
  'run', 'setup', 'install', 'execute', 'init', 'initialize', 'call', 'invoke', 'send', 'post', 'upload'
];

const ACTION_KEYWORDS = [...READ_KEYWORDS, ...WRITE_KEYWORDS, ...RUN_KEYWORDS];

const SEMANTIC_CONNECTOR_REGEX =
  /\b(?:and then|then|after that|before that|finally|next|and|before|after)\b|[,;]|\b(?:,\s*and)\b/gi;

const CONDITION_REGEXES = [
  /\b(?:when|if|after|before|whenever|once|unless)\b[^,.;]*/gi,
  /[^,.;]*(?:fail|failed|error|correct|wrong|reject|periodic|recurring|weekly|daily|monthly|heartbeat)[^,.;]*/gi
];

const OPERATION_TYPE_DEFINITIONS = [
  { type: 'guard', keywords: ['do not', "don't", 'never', 'avoid', 'must not', 'does not', "doesn't", 'cannot', "can't", 'will not', "won't", 'no longer', 'without'] },
  { type: 'decision', keywords: ['decide', 'choose', 'whether', 'determine'] },
  { type: 'verify', keywords: ['verify', 'validate', 'ensure', 'confirm', 'test'] },
  { type: 'review', keywords: ['review', 'reflect', 'heartbeat', 'periodic', 'recurring'] },
  { type: 'transform', keywords: ['summarize', 'summary', 'digest', 'brief', 'extract', 'convert', 'classify', 'parse', 'analyze', 'redact', 'mask', 'sanitize'] },
  { type: 'produce_artifact', keywords: ['produce', 'generate', 'output', 'report', 'create file', 'create', 'build', 'compose', 'draft'] },
  { type: 'invoke_tool', keywords: RUN_KEYWORDS },
  { type: 'write', keywords: WRITE_KEYWORDS },
  { type: 'read', keywords: READ_KEYWORDS },
  { type: 'condition', keywords: ['when', 'if', 'unless', 'only if'] }
];

const OPERATION_EFFECTS = {
  trigger: ['branch'],
  condition: ['branch'],
  decision: ['branch'],
  read: ['read_context'],
  write: ['persist_state'],
  transform: ['summarize'],
  invoke_tool: ['call_tool'],
  model_inference: ['model_context'],
  external_egress: ['network_egress'],
  verify: ['validate'],
  review: ['read_context', 'summarize'],
  produce_artifact: ['persist_state'],
  guard: ['branch']
};

const OPERATION_DOC_ACTION = {
  trigger: 'condition',
  condition: 'condition',
  decision: 'decision',
  read: 'read',
  write: 'write',
  transform: 'transform',
  invoke_tool: 'run',
  model_inference: 'run',
  external_egress: 'run',
  verify: 'verify',
  review: 'review',
  produce_artifact: 'write',
  guard: 'guard'
};

const VALID_OPERATION_TYPES = new Set(Object.keys(OPERATION_EFFECTS));
const VALID_EFFECTS = new Set([
  ...Object.values(OPERATION_EFFECTS).flat(),
  'update_memory'
]);
const VALID_TARGET_TYPES = new Set([
  'file',
  'directory',
  'tool',
  'memory_tier',
  'memory',
  'artifact',
  'document',
  'instruction',
  'semantic_rule',
  'external',
  'url',
  'command',
  'object'
]);

/**
 * Extract document-flow and semantic-rule-flow nodes/edges from markdown instructions.
 * Raw markdown steps are emitted as step-level FCG nodes. Legacy operation merging is
 * kept as an internal helper only; security propagation should prefer doc_step nodes.
 *
 * @param {Object} skillData
 * @param {Object|null} readmeData
 * @param {Object} options
 * @returns {Promise<{nodes: Array<Object>, edges: Array<Object>}>}
 */
async function extractDocumentFlow(skillData, readmeData, options = {}) {
  const docs = Array.isArray(options.extractionDocs)
    ? dedupeDocs(options.extractionDocs)
    : buildDocumentSet(skillData, readmeData);
  const docIndex = buildDocIndex(docs);
  const stepFlow = extractStepFlow(docs, docIndex);
  const routeFlow = extractReviewRouteFlow({
    reviewDocs: options.reviewDocs || [],
    extractionDocs: docs,
    docIndex,
    stepsByDoc: stepFlow.stepsByDoc
  });
  stepFlow.edges.push(...routeFlow.edges);
  const rawNodes = dedupeNodes(stepFlow.nodes);
  const gateLimit = limitNodesBeforeSemanticGate(rawNodes, options.maxDocFlowNodes);
  if (gateLimit.truncated) {
    console.warn(
      `Warning: doc-flow semantic gate candidates capped at ${gateLimit.nodes.length}/${rawNodes.length}; ` +
      `set FCG_MAX_DOC_FLOW_NODES to adjust batch breadth.`
    );
  }
  const semanticGateUsage = newSemanticGateUsage();
  const gatedNodes = await refineDocumentFlowSemantics(gateLimit.nodes, {
    ...options,
    semanticGateUsage
  });

  // Ordering-kind prohibitive constraints are NOT resolved here. Each affected
  // node keeps its node.pending_constraint (stashed by applyNegationConstraint);
  // the pipeline resolves them GLOBALLY via resolvePendingConstraints() once
  // tool-call, script, doc-flow, and mediation nodes are all merged, so a
  // constraint endpoint like "install" can match a tool/script node instead of
  // being redundantly synthesized. Guard-kind constraints are already handled
  // inline (marked on their node) and carry no pending_constraint.
  const flowNodeNames = new Set(['user.query', 'llm.inference']);
  for (const node of gatedNodes || []) {
    if (!isContextOnlyNode(node) && node.name) flowNodeNames.add(node.name);
  }
  const allEdges = dedupeEdges([...stepFlow.edges]).map((edge, index) => ({
    id: `doc_edge_${String(index + 1).padStart(3, '0')}`,
    ...edge
  })).filter(edge => flowNodeNames.has(edge.source) && flowNodeNames.has(edge.target));

  return {
    nodes: gatedNodes,
    edges: allEdges,
    semantic_gate_usage: summarizeSemanticGateUsage(semanticGateUsage)
  };
}

// Resolve ordering-kind prohibitive constraints into explicit control_flow
// edges. Runs once, after all nodes are gated. Returns the (possibly enlarged)
// node list plus the constraint edges. Guard-kind constraints are already
// handled inline (marked on their node), so only ordering pendings appear here.
async function resolvePendingConstraints(nodes, options = {}) {
  const resultNodes = Array.isArray(nodes) ? nodes.slice() : [];
  const addedNodes = []; // synthesized endpoints created in this pass
  const edges = [];
  const pendings = resultNodes.filter(n => n && n.pending_constraint && n.pending_constraint.kind === 'ordering');
  if (pendings.length === 0) {
    for (const n of resultNodes) delete n.pending_constraint;
    return { nodes: resultNodes, addedNodes, edges };
  }

  // Match constraint endpoints against the FULL actionable node set the caller
  // passed in (tool-call + script + doc-flow + mediation once merged), so an
  // endpoint like "install" links to an existing node rather than being
  // synthesized redundantly. Exclude the constraint-declaring nodes themselves
  // (the "never install without vetting" sentence is the prohibition, not the
  // install action) so an endpoint resolves to a real actor node.
  const holderSet = new Set(pendings);
  const actionable = resultNodes.filter(n => n && n.name && !isContextOnlyNode(n) && !holderSet.has(n));
  const synthesized = new Map(); // phrase -> synthesized node (dedupe within this pass)

  // Phase A: rule match (stemmed token overlap) for each endpoint. Anything the
  // rule cannot confidently place is collected for one LLM disambiguation pass
  // (word-form / paraphrase gaps the rule can't measure). Synthesis is the last
  // resort only after both rule AND LLM decline to place the endpoint.
  const endpointMatch = new Map(); // phrase -> node | null (resolved) ; absent = undecided
  const unresolvedPhrases = new Map(); // phrase -> canonical phrase text
  for (const holder of pendings) {
    const pc = holder.pending_constraint;
    for (const phrase of [pc.before_action, pc.after_action]) {
      if (!phrase || endpointMatch.has(phrase)) continue;
      const hit = matchActionNode(phrase, actionable);
      if (hit) endpointMatch.set(phrase, hit);
      else unresolvedPhrases.set(phrase, phrase);
    }
  }

  if (unresolvedPhrases.size > 0) {
    const llmResolved = await llmResolveConstraintEndpoints(
      Array.from(unresolvedPhrases.keys()), actionable, options
    );
    for (const [phrase, node] of llmResolved) {
      if (node) endpointMatch.set(phrase, node);
    }
  }

  const seenEdgeKeys = new Set();
  for (const holder of pendings) {
    const pc = holder.pending_constraint;
    const beforeNode = endpointMatch.get(pc.before_action)
      || getOrCreateConstraintNode(pc.before_action, holder, synthesized, resultNodes, actionable, addedNodes);
    const afterNode = endpointMatch.get(pc.after_action)
      || getOrCreateConstraintNode(pc.after_action, holder, synthesized, resultNodes, actionable, addedNodes);
    delete holder.pending_constraint;
    if (!beforeNode || !afterNode || beforeNode.name === afterNode.name) continue;

    const key = `${beforeNode.name}->${afterNode.name}`;
    if (seenEdgeKeys.has(key)) continue;
    seenEdgeKeys.add(key);
    edges.push({
      source: beforeNode.name,
      target: afterNode.name,
      type: 'control_flow',
      confidence: 0.5,
      validation_method: 'doc_flow_constraint',
      data_flow: { from_param: 'state', to_param: 'state', data_type: 'object' },
      semantic_reason: `Prohibitive ordering: "${pc.before_action}" must precede "${pc.after_action}"${pc.note ? ` (${pc.note})` : ''}`,
      source_context: edgeSourceContextFromNode(holder, 'doc_flow_constraint')
    });
  }

  for (const n of resultNodes) delete n.pending_constraint;
  return { nodes: resultNodes, addedNodes, edges };
}

// Fuzzy-match an action phrase ("vet skill", "install skill") to an existing
// actionable node by comparing normalized content words. Conservative: requires
// a strong token-overlap so we synthesize rather than mis-link.
function matchActionNode(phrase, actionable) {
  const target = actionPhraseTokens(phrase);
  if (target.size === 0) return null;
  let best = null;
  let bestScore = 0;
  for (const node of actionable) {
    const text = String(node.instructionText || node.formal_semantics?.evidence?.text || node.name || '');
    const tokens = actionPhraseTokens(text);
    if (tokens.size === 0) continue;
    let overlap = 0;
    for (const t of target) if (tokens.has(t)) overlap++;
    const score = overlap / target.size;
    if (score > bestScore) { bestScore = score; best = node; }
  }
  // Require the phrase's key verb/noun to be substantially present.
  return bestScore >= 0.6 ? best : null;
}

function actionPhraseTokens(text) {
  const STOP = new Set(['the', 'a', 'an', 'to', 'of', 'it', 'them', 'this', 'that', 'first', 'any', 'all', 'without', 'before', 'after', 'is', 'are', 'be', 'and', 'or']);
  return new Set(
    String(text || '')
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 2 && !STOP.has(w))
      .map(stemActionWord)
  );
}

// Light inflectional stemmer so a constraint phrase ("vet skill", "install
// skill") matches the extracted node's wording ("vetting", "installing",
// "installs"). Not a full stemmer: strips only the common -ing/-ed/-s/-es
// endings that separate a constraint verb from its inflected form in prose.
function stemActionWord(word) {
  let w = word;
  if (w.length > 4 && w.endsWith('ing')) {
    w = w.slice(0, -3);
    // "installing" -> "install"; "vetting" -> "vet" (undouble final consonant)
    if (/([bcdfgklmnprstvz])\1$/.test(w)) w = w.slice(0, -1);
  } else if (w.length > 4 && w.endsWith('ed')) {
    w = w.slice(0, -2);
    if (/([bcdfgklmnprstvz])\1$/.test(w)) w = w.slice(0, -1);
  } else if (w.length > 4 && w.endsWith('es')) {
    w = w.slice(0, -2);
  } else if (w.length > 3 && w.endsWith('s') && !w.endsWith('ss')) {
    w = w.slice(0, -1);
  }
  return w;
}

// LLM fallback for constraint endpoints the rule matcher could not place.
// Word-form and paraphrase gaps ("vet skill" vs a node worded "After vetting,
// produce the report") are hard to score with token overlap, so we hand the
// judgement to the model: given the unresolved phrases and a numbered list of
// candidate action nodes, it returns, per phrase, the matching candidate id or
// null. A null answer (or no LLM available) falls through to synthesis.
// options.constraintEndpointResolver, when supplied, replaces the network call
// (used by tests and to keep this deterministic offline).
async function llmResolveConstraintEndpoints(phrases, actionable, options = {}) {
  const resolved = new Map();
  if (!Array.isArray(phrases) || phrases.length === 0) return resolved;

  // Candidate pool: actionable nodes with a usable action description.
  const candidates = actionable
    .map((n) => ({
      node: n,
      text: String(n.instructionText || n.formal_semantics?.evidence?.text || n.name || '').replace(/\s+/g, ' ').trim().slice(0, 160)
    }))
    .filter((c) => c.text.length > 0);
  if (candidates.length === 0) return resolved;

  const idByNode = new Map();
  candidates.forEach((c, i) => idByNode.set(c.node, `n${i + 1}`));
  const nodeById = new Map();
  candidates.forEach((c, i) => nodeById.set(`n${i + 1}`, c.node));

  let raw;
  try {
    if (typeof options.constraintEndpointResolver === 'function') {
      raw = await options.constraintEndpointResolver({ phrases, candidates });
    } else {
      const apiKey = options.llmApiKey || process.env.LLM_API_KEY || '';
      if (!apiKey || options.disableLlm === true) return resolved; // no LLM -> synthesize
      raw = await callConstraintEndpointModel(phrases, candidates, options);
    }
  } catch (err) {
    console.warn(`Warning: constraint endpoint LLM resolution failed (${err.message}); falling back to synthesis.`);
    return resolved;
  }

  const parsed = parseLooseJson(raw);
  const results = Array.isArray(parsed?.results) ? parsed.results : [];
  for (const r of results) {
    const phrase = typeof r?.phrase === 'string' ? r.phrase : null;
    const id = typeof r?.node_id === 'string' ? r.node_id.trim() : null;
    if (!phrase || !phrases.includes(phrase)) continue;
    const node = id && id.toLowerCase() !== 'null' ? nodeById.get(id) : null;
    if (node) resolved.set(phrase, node);
  }
  return resolved;
}

async function callConstraintEndpointModel(phrases, candidates, options) {
  const endpoint = resolveSemanticLlmEndpoint(options);
  const model = options.llmModel || 'gpt-5.5';
  const timeout = Number(options.llmTimeout || 180000);
  const payload = await postJsonWithTimeout(endpoint, {
    model,
    temperature: 0,
    messages: [
      { role: 'system', content: buildConstraintEndpointSystemPrompt() },
      { role: 'user', content: buildConstraintEndpointPrompt(phrases, candidates) }
    ]
  }, {
    timeoutMs: timeout,
    headers: { Authorization: `Bearer ${options.llmApiKey}` }
  });
  accumulateSemanticGateUsage(options.semanticGateUsage, payload?.usage);
  return normalizeAssistantContent(payload?.choices?.[0]?.message?.content);
}

function buildConstraintEndpointSystemPrompt() {
  return [
    'You match action phrases from a prohibitive-ordering constraint to the action node that already represents that action in a skill flow graph.',
    'Each phrase is a short action (e.g. "vet skill", "install skill").',
    'You are given a numbered list of candidate action nodes with their instruction text.',
    'For each phrase, return the id of the ONE candidate that denotes the SAME runtime action, allowing for word-form differences (vet/vetting), paraphrase, or extra wording.',
    'Only match when the candidate genuinely performs that action; a node that merely mentions the word in a condition, heading, or disclaimer is NOT a match.',
    'If no candidate denotes the action, return null for that phrase — do not force a weak match.',
    'Return strict JSON only: {"results":[{"phrase":"...","node_id":"nK"|null}]}. One entry per phrase.'
  ].join(' ');
}

function buildConstraintEndpointPrompt(phrases, candidates) {
  const lines = [];
  lines.push('Phrases to match:');
  phrases.forEach((p) => lines.push(`- ${p}`));
  lines.push('');
  lines.push('Candidate action nodes:');
  candidates.forEach((c, i) => lines.push(`n${i + 1}: ${c.text}`));
  lines.push('');
  lines.push('Return {"results":[{"phrase","node_id"}]} with node_id = matching id or null.');
  return lines.join('\n');
}

// Create (once per phrase) a synthesized doc node for a constraint endpoint that
// has no matching extracted node. Shaped like a doc_step so downstream dedup /
// split / endpoint-mapping treat it uniformly.
function getOrCreateConstraintNode(phrase, holder, synthesized, resultNodes, actionable, addedNodes) {
  const clean = String(phrase || '').trim();
  if (!clean) return null;
  const key = Array.from(actionPhraseTokens(clean)).sort().join('_');
  if (synthesized.has(key)) return synthesized.get(key);

  const ownerDoc = holder.pending_constraint?.source_doc || holder.ownerDoc || 'SKILL.md';
  const section = holder.pending_constraint?.source_section || holder.location?.section || '';
  const slug = clean.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 40) || 'action';
  const name = `doc.constraint.${fileSlug(ownerDoc)}.${slug}`;
  const node = {
    name,
    action: 'guard',
    type: 'custom_func',
    description: `Constraint endpoint (synthesized) in ${ownerDoc}: ${clean}`,
    input: {},
    output: {},
    location: { file: normalizeDocPath(ownerDoc), line: holder.location?.line || 0, section },
    ownerDoc: normalizeDocPath(ownerDoc),
    docAction: 'guard',
    docActions: ['guard'],
    operationType: 'guard',
    instructionText: clean,
    synthesized_from: 'negation_constraint',
    formal_semantics: {
      operation_type: 'guard',
      actor: 'llm',
      inputs: [],
      outputs: [{ name: 'branch_state', type: 'object' }],
      targets: [],
      conditions: [],
      effects: ['branch'],
      confidence: 0.5,
      evidence: {
        text: clean,
        source_line: clean,
        file: normalizeDocPath(ownerDoc),
        line: holder.location?.line || 0,
        section,
        method: 'negation_constraint_synthesis',
        role: 'constraint_endpoint'
      },
      action: 'guard'
    },
    semantic_gate: {
      classification: 'policy_rule',
      actionability: 'runtime_action',
      grammar: 'synthesized constraint endpoint',
      reason: 'synthesized from prohibitive ordering constraint with no matching extracted node',
      method: 'negation_constraint_synthesis'
    }
  };
  synthesized.set(key, node);
  resultNodes.push(node);
  actionable.push(node);
  if (Array.isArray(addedNodes)) addedNodes.push(node);
  return node;
}

async function refineDocumentFlowSemantics(nodes, options = {}) {
  if (options.semanticLlm === false || options.disableLlm) {
    return nodes.map(applyRuleOnlySemanticGate).filter(Boolean);
  }

  const apiKey = String(options.llmApiKey || process.env.LLM_API_KEY || '').trim();
  if (!apiKey && typeof options.semanticRefiner !== 'function' && typeof options.semanticBatchRefiner !== 'function') {
    throw new Error('LLM_API_KEY is required for FCG Markdown semantic gate');
  }

  const candidates = (nodes || []).filter(shouldGateSemanticNode);
  if (candidates.length === 0) {
    return nodes;
  }

  const config = {
    ...options,
    llmApiKey: apiKey
  };

  const cache = loadSemanticGateCache(config);
  const candidateNames = new Set(candidates.map(node => node.name).filter(Boolean));
  const gatedByName = new Map();
  const missing = [];

  for (const node of candidates) {
    const cacheKey = buildSemanticGateCacheKey(node, config);
    const cached = cache.records.get(cacheKey);
    if (cached) {
      const refinement = {
        ...cached,
        cache_hit: true
      };
      const nextNode = applyCandidateSemanticGate(node, refinement);
      if (nextNode) gatedByName.set(node.name, nextNode);
      continue;
    }
    missing.push({
      node,
      cacheKey
    });
  }

  const resolved = await resolveSemanticGateCandidates(missing, config);
  for (const item of resolved) {
    const nextNode = item.error
      ? createContextNodeFromNode(item.node, 'doc_review_error', {
          reason: item.error.message || 'semantic LLM gate failed',
          requiresReview: true
        })
      : applyCandidateSemanticGate(item.node, item.refinement);
    if (nextNode) gatedByName.set(item.node.name, nextNode);
    if (!item.error && item.refinement) {
      appendSemanticGateCacheRecord(cache, item.cacheKey, item.node, item.refinement, config);
    }
  }

  return (nodes || [])
    .map(node => {
      if (!candidateNames.has(node.name)) return node;
      return gatedByName.get(node.name) || createContextNodeFromNode(node, 'doc_review_error', {
        reason: 'semantic LLM gate did not return a result',
        requiresReview: true
      });
    })
    .filter(Boolean);
}

function shouldGateSemanticNode(node) {
  if (!node || !node.formal_semantics) return false;
  if (!['doc_operation', 'doc_step'].includes(node.semanticKind)) return false;
  const method = String(node.source_context?.action_evidence?.extraction_method || node.formal_semantics?.evidence?.method || '');
  if (method === 'implicit_object_read' || method === 'doc_review_route') return false;
  // Shell commands from code blocks are deterministic, grounded runtime
  // actions; no LLM gating needed.
  if (method === 'doc_code_block_command') return false;
  return true;
}

function limitNodesBeforeSemanticGate(nodes = [], maxNodes) {
  const limit = Number(maxNodes || 0);
  if (!Number.isInteger(limit) || limit <= 0 || nodes.length <= limit) {
    return { nodes, truncated: false };
  }

  const priority = node => {
    if (!node) return 99;
    if (node.semanticKind === 'trigger' || node.semanticKind === 'policy') return 0;
    if (node.semanticKind === 'doc_step') return 1;
    if (node.semanticKind === 'doc_operation') return 2;
    if (String(node.semanticKind || '').startsWith('doc_')) return 3;
    return 4;
  };

  const capped = [...nodes]
    .sort((a, b) => {
      const pa = priority(a);
      const pb = priority(b);
      if (pa !== pb) return pa - pb;
      const af = String(a.location?.file || a.ownerDoc || '');
      const bf = String(b.location?.file || b.ownerDoc || '');
      if (af !== bf) return af.localeCompare(bf);
      return Number(a.location?.line || 0) - Number(b.location?.line || 0);
    })
    .slice(0, limit);
  return { nodes: capped, truncated: true };
}

async function resolveSemanticGateCandidates(items, config) {
  if (!items || items.length === 0) return [];

  if (typeof config.semanticRefiner === 'function' && typeof config.semanticBatchRefiner !== 'function') {
    return runWithConcurrency(items, normalizePositiveInteger(config.semanticGateConcurrency, DEFAULT_SEMANTIC_GATE_BATCH_CONCURRENCY), async item => {
      try {
        const rawRefinement = await invokeSemanticRefiner(item.node, config);
        return normalizeSemanticGateResult(item, rawRefinement);
      } catch (error) {
        return {
          ...item,
          error
        };
      }
    });
  }

  const batchSize = normalizePositiveInteger(
    config.semanticGateBatchSize ?? process.env.FCG_SEMANTIC_GATE_BATCH_SIZE,
    DEFAULT_SEMANTIC_GATE_BATCH_SIZE
  );
  const concurrency = normalizePositiveInteger(
    config.semanticGateConcurrency ?? process.env.FCG_SEMANTIC_GATE_CONCURRENCY,
    DEFAULT_SEMANTIC_GATE_BATCH_CONCURRENCY
  );
  const maxBatchChars = normalizePositiveInteger(
    config.semanticGateMaxBatchChars ?? process.env.FCG_SEMANTIC_GATE_MAX_BATCH_CHARS,
    DEFAULT_SEMANTIC_GATE_MAX_BATCH_CHARS
  );
  const batches = chunkSemanticGateItems(items, { batchSize, maxBatchChars });
  const batchResults = await runWithConcurrency(batches, concurrency, batch => judgeSemanticGateBatchWithRetry(batch, config));

  return batchResults.flat();
}

async function runWithConcurrency(items, concurrency, worker) {
  const input = Array.isArray(items) ? items : [];
  const limit = Math.max(1, Math.min(Number(concurrency) || 1, input.length || 1));
  const results = new Array(input.length);
  let cursor = 0;

  async function runWorker() {
    while (cursor < input.length) {
      const index = cursor;
      cursor += 1;
      results[index] = await worker(input[index], index);
    }
  }

  await Promise.all(Array.from({ length: limit }, runWorker));
  return results;
}

function chunkSemanticGateItems(items, { batchSize, maxBatchChars }) {
  const chunks = [];
  const sorted = [...(items || [])].sort(compareSemanticGateBatchItems);
  let current = [];
  let currentChars = 0;

  for (const item of sorted) {
    const itemChars = estimateSemanticGateItemChars(item);
    const wouldExceedSize = current.length >= batchSize;
    const wouldExceedChars = current.length > 0 && currentChars + itemChars > maxBatchChars;
    if (wouldExceedSize || wouldExceedChars) {
      chunks.push(current);
      current = [];
      currentChars = 0;
    }
    current.push(item);
    currentChars += itemChars;
  }
  if (current.length > 0) {
    chunks.push(current);
  }
  return chunks;
}

function compareSemanticGateBatchItems(a, b) {
  const aNode = a?.node || {};
  const bNode = b?.node || {};
  const aFile = String(aNode.location?.file || aNode.ownerDoc || '');
  const bFile = String(bNode.location?.file || bNode.ownerDoc || '');
  if (aFile !== bFile) return aFile.localeCompare(bFile);
  const aSection = String(aNode.location?.section || '');
  const bSection = String(bNode.location?.section || '');
  if (aSection !== bSection) return aSection.localeCompare(bSection);
  return Number(aNode.location?.line || 0) - Number(bNode.location?.line || 0);
}

function estimateSemanticGateItemChars(item) {
  const node = item?.node || {};
  return JSON.stringify(buildSemanticBatchRecord({ id: 'c0', node })).length + 512;
}

async function judgeSemanticGateBatchWithRetry(batch, config) {
  try {
    const rawBatch = await invokeSemanticBatchRefiner(batch.map(item => item.node), config);
    return normalizeSemanticGateBatchResult(batch, rawBatch);
  } catch (error) {
    if (batch.length <= 1) {
      return batch.map(item => ({
        ...item,
        error
      }));
    }
    const midpoint = Math.ceil(batch.length / 2);
    const left = await judgeSemanticGateBatchWithRetry(batch.slice(0, midpoint), config);
    const right = await judgeSemanticGateBatchWithRetry(batch.slice(midpoint), config);
    return [...left, ...right];
  }
}

function normalizeSemanticGateResult(item, rawRefinement) {
  const refinement = normalizeSemanticRefinement(rawRefinement);
  if (!refinement) {
    return {
      ...item,
      error: new Error('Invalid semantic LLM JSON')
    };
  }
  return {
    ...item,
    refinement
  };
}

async function invokeSemanticRefiner(node, options) {
  if (typeof options.semanticRefiner === 'function') {
    return options.semanticRefiner(node, {
      current: node.formal_semantics,
      provider: options.llmProvider || 'openai',
      model: options.llmModel || 'gpt-5.5'
    });
  }

  return callSemanticRefinementModel(node, options);
}

async function invokeSemanticBatchRefiner(nodes, options) {
  const candidates = (nodes || []).map((node, index) => ({
    id: `c${index + 1}`,
    node,
    current: node.formal_semantics
  }));

  if (typeof options.semanticBatchRefiner === 'function') {
    return options.semanticBatchRefiner(nodes, {
      candidates,
      provider: options.llmProvider || 'openai',
      model: options.llmModel || 'gpt-5.5'
    });
  }

  return callSemanticBatchRefinementModel(candidates, options);
}

async function callSemanticRefinementModel(node, options) {
  const endpoint = resolveSemanticLlmEndpoint(options);
  const model = options.llmModel || 'gpt-5.5';
  const timeout = Number(options.llmTimeout || 180000);
  const payload = await postJsonWithTimeout(endpoint, {
    model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: buildSemanticGateSystemPrompt()
      },
      {
        role: 'user',
        content: buildSemanticRefinementPrompt(node)
      }
    ]
  }, {
    timeoutMs: timeout,
    headers: {
      Authorization: `Bearer ${options.llmApiKey}`
    }
  });

  accumulateSemanticGateUsage(options.semanticGateUsage, payload?.usage);
  return normalizeAssistantContent(payload?.choices?.[0]?.message?.content);
}

async function callSemanticBatchRefinementModel(candidates, options) {
  const endpoint = resolveSemanticLlmEndpoint(options);
  const model = options.llmModel || 'gpt-5.5';
  const timeout = Number(options.llmTimeout || 180000);
  const payload = await postJsonWithTimeout(endpoint, {
    model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: buildSemanticGateSystemPrompt({
          returnShape: 'Return strict JSON only: {"results":[{...}]}. Each result must include the candidate id.'
        })
      },
      {
        role: 'user',
        content: buildSemanticBatchRefinementPrompt(candidates)
      }
    ]
  }, {
    timeoutMs: timeout,
    headers: {
      Authorization: `Bearer ${options.llmApiKey}`
    }
  });

  accumulateSemanticGateUsage(options.semanticGateUsage, payload?.usage);
  return normalizeAssistantContent(payload?.choices?.[0]?.message?.content);
}

function buildSemanticGateSystemPrompt({ returnShape } = {}) {
  return [
    'You gate Markdown soft-instruction candidates before they become FCG action nodes.',
    returnShape || 'Return strict JSON only in English.',
    'First classify each source as one of: workflow_instruction, policy_rule, definition, schema, example, template, description, discard.',
    'Analyze English grammar: fragment, SVC, SVO, passive, imperative, table_row, heading, list_item.',
    'For fragments, reconstruct the missing subject or predicate before deciding actionability.',
    'For passive clauses, identify the patient/theme and only infer a runtime producer or consumer if the sentence commands an agent action.',
    'Table definitions, examples, templates, field schemas, and descriptive prose are not runtime actions unless the text explicitly instructs the agent to do something at runtime.',
    'Allowed operation_type values: trigger, condition, decision, read, write, transform, invoke_tool, verify, review, produce_artifact, guard.',
    'Allowed effects: read_context, persist_state, call_tool, update_memory, summarize, validate, branch.',
    'confidence must be a number from 0 to 1.',
    'Set actionability to runtime_action only when this candidate should become a flow node.',
    'Treat SKILL.md as the highest-priority semantic anchor for declared task, trigger conditions, route rules, policy rules, and workflow steps.',
    'For SKILL.md Situation->Action table rows, judge the whole row: put the situation in conditions and the action receiver/target in targets/effects.',
    'Do not split a Situation->Action row into fake standalone trigger or policy nodes.',
    'Never infer trigger/policy nodes from headings, file names, directory trees, template placeholders, or example error text.',
    'If a title or file description only names a log/template/example, classify it as description/template/example context_only.',
    'NEGATION HANDLING: a negated sentence is NOT automatically a disclaimer. Set negation_kind to disclaimer, constraint, or null.',
    'A genuine DISCLAIMER states a capability the skill does not have ("does not connect to a wallet", "does not send data externally"): negation_kind=disclaimer, classification=description, actionability=context_only.',
    'A PROHIBITIVE CONSTRAINT forbids or orders a runtime action ("never install a skill without vetting it first", "never delete without asking", "never overwrite existing files", "do not log secrets unless the user asks"): negation_kind=constraint, classification=policy_rule, actionability=runtime_action.',
    'For a constraint set constraint_edge to {kind:"ordering"|"guard", before_action, after_action, guarded_action, note}. ordering: before_action must precede after_action (e.g. before="vet skill", after="install skill"). guard: guarded_action is the forbidden/conditional action (e.g. guarded="overwrite existing files"); leave before_action/after_action null.',
    'If the candidate is not a negation, set negation_kind=null and constraint_edge=null.',
    'Do not create graph edges or path relationships.'
  ].join(' ');
}

function resolveSemanticLlmEndpoint(options = {}) {
  if (options.llmEndpoint || process.env.LLM_ENDPOINT) return options.llmEndpoint || process.env.LLM_ENDPOINT;
  const provider = String(options.llmProvider || process.env.LLM_PROVIDER || 'openai').toLowerCase();
  if (provider === 'dashscope') {
    return process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
  }
  return 'https://api.openai.com/v1/chat/completions';
}

function buildSemanticRefinementPrompt(node) {
  return [
    'Decide whether this Markdown candidate is a runtime action flow node or documentation context only.',
    'Return JSON in English with these keys: classification, actionability, grammar, completed_sentence, operation_type, targets, conditions, effects, confidence, reason.',
    'classification must be workflow_instruction, policy_rule, definition, schema, example, template, description, or discard.',
    'actionability must be runtime_action or context_only.',
    'grammar must describe fragment/SVC/SVO/passive/imperative/table_row/list_item and the subject/predicate/object roles.',
    'targets must be objects with type, value, and optional raw.',
    'conditions must be objects with type and text.',
    'confidence must be a number from 0 to 1.',
    '',
    `Node: ${node.name || ''}`,
    `Document: ${node.ownerDoc || node.location?.file || ''}`,
    `Line: ${node.location?.line || 0}`,
    `Instruction: ${node.instructionText || node.formal_semantics?.evidence?.text || ''}`,
    '',
    'Current formal_semantics:',
    JSON.stringify(node.formal_semantics || {}, null, 2)
  ].join('\n');
}

function buildSemanticBatchRefinementPrompt(candidates) {
  const records = (candidates || []).map(buildSemanticBatchRecord);

  return [
    'Gate each Markdown candidate independently.',
    'Return JSON with this shape:',
    '{"results":[{"id":"c1","classification":"workflow_instruction|policy_rule|definition|schema|example|template|description|discard","actionability":"runtime_action|context_only","grammar":"...","completed_sentence":"...","operation_type":"read|write|transform|invoke_tool|verify|review|produce_artifact|guard|condition|decision|trigger","targets":[],"conditions":[],"effects":[],"negation_kind":"disclaimer|constraint|null","constraint_edge":null,"confidence":0.0,"reason":"..."}]}',
    'For a negated candidate that is a prohibitive constraint, set negation_kind="constraint" and constraint_edge={"kind":"ordering|guard","before_action":null,"after_action":null,"guarded_action":null,"note":""}. Otherwise negation_kind=null (or "disclaimer" for a capability disclaimer) and constraint_edge=null.',
    'Use the exact candidate id. Do not omit a candidate. Do not infer graph edges.',
    '',
    'Candidates:',
    JSON.stringify(records, null, 2)
  ].join('\n');
}

function buildSemanticBatchRecord(candidate) {
  const node = candidate.node || {};
  return {
    id: candidate.id,
    node: node.name || '',
    document: node.ownerDoc || node.location?.file || '',
    line: node.location?.line || 0,
    section: node.location?.section || '',
    source_role: node.source_context?.source_role || '',
    instruction: node.instructionText || node.formal_semantics?.evidence?.text || '',
    source_line: node.source_context?.source_line || node.formal_semantics?.evidence?.source_line || '',
    current_formal_semantics: node.formal_semantics || {}
  };
}

function normalizeSemanticGateBatchResult(batch, rawBatch) {
  const parsed = parseLooseJson(rawBatch);
  const byId = normalizeBatchResultMap(parsed);
  return batch.map((item, index) => {
    const candidateId = `c${index + 1}`;
    const raw = byId.get(candidateId) || byId.get(item.node.name) || byId.get(String(index));
    if (!raw) {
      return {
        ...item,
        error: new Error(`Missing semantic LLM result for ${candidateId}`)
      };
    }
    return normalizeSemanticGateResult(item, raw);
  });
}

function normalizeBatchResultMap(parsed) {
  const byId = new Map();
  if (!parsed) return byId;

  const results = Array.isArray(parsed)
    ? parsed
    : (Array.isArray(parsed.results)
        ? parsed.results
        : (Array.isArray(parsed.refinements) ? parsed.refinements : null));

  if (results) {
    results.forEach((item, index) => {
      const id = String(item?.id || item?.candidate_id || item?.node_id || `c${index + 1}`).trim();
      if (id) byId.set(id, item);
    });
    return byId;
  }

  if (typeof parsed === 'object' && !Array.isArray(parsed)) {
    for (const [key, value] of Object.entries(parsed)) {
      if (!value || typeof value !== 'object') continue;
      byId.set(String(key), value);
      const id = String(value.id || value.candidate_id || value.node_id || '').trim();
      if (id) byId.set(id, value);
    }
  }

  return byId;
}

function normalizeSemanticRefinement(raw) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return null;
  }

  const refinement = {};
  const classification = normalizeClassification(parsed.classification || parsed.node_kind || parsed.kind || parsed.semantic_kind);
  if (classification) refinement.classification = classification;

  const actionability = normalizeActionability(parsed.actionability || parsed.actionable || parsed.flow_role);
  if (actionability) refinement.actionability = actionability;

  if (typeof parsed.grammar === 'string' && parsed.grammar.trim()) {
    refinement.grammar = parsed.grammar.trim();
  } else if (parsed.grammar && typeof parsed.grammar === 'object') {
    refinement.grammar = JSON.stringify(parsed.grammar);
  }

  if (typeof parsed.completed_sentence === 'string' && parsed.completed_sentence.trim()) {
    refinement.completed_sentence = parsed.completed_sentence.trim();
  }

  const operationType = String(parsed.operation_type || '').trim();
  if (VALID_OPERATION_TYPES.has(operationType)) {
    refinement.operation_type = operationType;
  }

  if (Array.isArray(parsed.targets)) {
    refinement.targets = parsed.targets
      .map(normalizeRefinementTarget)
      .filter(Boolean);
  }

  if (Array.isArray(parsed.conditions)) {
    refinement.conditions = parsed.conditions
      .map(normalizeRefinementCondition)
      .filter(Boolean);
  }

  if (Array.isArray(parsed.effects)) {
    refinement.effects = Array.from(new Set(
      parsed.effects
        .map(effect => String(effect || '').trim())
        .filter(effect => VALID_EFFECTS.has(effect))
    ));
  }

  refinement.confidence = normalizeScaledNumber(parsed.confidence, { fallback: NaN });
  if (!Number.isFinite(refinement.confidence)) {
    delete refinement.confidence;
  }

  if (typeof parsed.reason === 'string' && parsed.reason.trim()) {
    refinement.reason = parsed.reason.trim();
  }

  const negationKind = normalizeNegationKind(parsed.negation_kind);
  if (negationKind) {
    refinement.negation_kind = negationKind;
    if (negationKind === 'constraint') {
      const constraintEdge = normalizeConstraintEdge(parsed.constraint_edge);
      if (constraintEdge) refinement.constraint_edge = constraintEdge;
    }
  }

  const hasUsefulField = [
    refinement.classification,
    refinement.actionability,
    refinement.grammar,
    refinement.completed_sentence,
    refinement.operation_type,
    refinement.targets && refinement.targets.length > 0,
    refinement.conditions && refinement.conditions.length > 0,
    refinement.effects && refinement.effects.length > 0,
    typeof refinement.confidence === 'number',
    refinement.reason,
    refinement.negation_kind
  ].some(Boolean);

  return hasUsefulField ? refinement : null;
}

function normalizeNegationKind(value) {
  const normalized = normalizeForSearch(value).replace(/\s+/g, '_');
  if (['disclaimer', 'capability_disclaimer'].includes(normalized)) return 'disclaimer';
  if (['constraint', 'prohibitive_constraint', 'ordering_constraint', 'guard'].includes(normalized)) return 'constraint';
  return '';
}

function normalizeConstraintEdge(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const kind = normalizeForSearch(raw.kind).replace(/\s+/g, '_');
  const edgeKind = kind === 'ordering' ? 'ordering' : (kind === 'guard' ? 'guard' : '');
  if (!edgeKind) return null;
  const str = value => {
    const s = String(value == null ? '' : value).trim();
    return s && s.toLowerCase() !== 'null' ? s : '';
  };
  const edge = { kind: edgeKind };
  const before = str(raw.before_action);
  const after = str(raw.after_action);
  const guarded = str(raw.guarded_action);
  const note = str(raw.note);
  if (edgeKind === 'ordering') {
    // ordering needs both endpoints to be meaningful; without them it degrades to a guard.
    if (before) edge.before_action = before;
    if (after) edge.after_action = after;
    if (!before || !after) {
      edge.kind = 'guard';
      edge.guarded_action = guarded || after || before || '';
    }
  } else {
    edge.guarded_action = guarded || '';
  }
  if (note) edge.note = note;
  // Reject an edge that carries no usable action text at all.
  if (edge.kind === 'ordering' && (!edge.before_action || !edge.after_action)) return null;
  if (edge.kind === 'guard' && !edge.guarded_action) return null;
  return edge;
}

function normalizeClassification(value) {
  const normalized = normalizeForSearch(value).replace(/\s+/g, '_');
  if (!normalized) return '';
  if (['workflow_instruction', 'runtime_action', 'instruction', 'action'].includes(normalized)) return 'workflow_instruction';
  if (['policy_rule', 'policy'].includes(normalized)) return 'policy_rule';
  if (['definition', 'term_definition', 'table_definition'].includes(normalized)) return 'definition';
  if (['schema', 'field_schema', 'data_schema', 'fields'].includes(normalized)) return 'schema';
  if (['example', 'sample'].includes(normalized)) return 'example';
  if (['template', 'boilerplate'].includes(normalized)) return 'template';
  if (['description', 'descriptive', 'overview', 'context'].includes(normalized)) return 'description';
  if (['discard', 'irrelevant', 'non_action'].includes(normalized)) return 'discard';
  return '';
}

function normalizeActionability(value) {
  const normalized = normalizeForSearch(value).replace(/\s+/g, '_');
  if (!normalized) return '';
  if (['runtime_action', 'action', 'actionable', 'flow', 'flow_node', 'true', 'yes'].includes(normalized)) return 'runtime_action';
  if (['context_only', 'context', 'non_action', 'false', 'no', 'definition', 'schema', 'example', 'template', 'discard'].includes(normalized)) return 'context_only';
  return '';
}

function normalizeRefinementTarget(target) {
  if (!target || typeof target !== 'object') return null;
  const type = String(target.type || '').trim();
  const value = String(target.value || '').trim();
  if (!type || !value || !VALID_TARGET_TYPES.has(type)) return null;
  const normalized = {
    type,
    value: type === 'file' || type === 'directory' ? normalizeDocPath(value) : value
  };
  if (target.raw !== undefined) {
    normalized.raw = String(target.raw || '').trim();
  }
  return normalized;
}

function normalizeRefinementCondition(condition) {
  if (!condition || typeof condition !== 'object') return null;
  const text = String(condition.text || '').trim();
  if (!text) return null;
  return {
    type: String(condition.type || 'condition').trim() || 'condition',
    text
  };
}

function applySemanticRefinement(node, refinement) {
  const current = node.formal_semantics || {};
  const priorMethod = current.evidence?.method || '';
  const operationType = refinement.operation_type || current.operation_type || 'read';
  const targets = refinement.targets && refinement.targets.length > 0
    ? dedupeTargets(refinement.targets)
    : (current.targets || []);
  const conditions = refinement.conditions
    ? dedupeConditions(refinement.conditions)
    : (current.conditions || []);
  const effects = refinement.effects && refinement.effects.length > 0
    ? refinement.effects
    : (OPERATION_EFFECTS[operationType] || current.effects || []);
  const confidence = typeof refinement.confidence === 'number'
    ? refinement.confidence
    : Number(current.confidence || 0.5);
  const action = OPERATION_DOC_ACTION[operationType] || current.action || node.docAction || 'read';

  node.formal_semantics = {
    ...current,
    operation_type: operationType,
    actor: current.actor || 'llm',
    inputs: buildFormalInputs(operationType, targets, conditions),
    outputs: buildFormalOutputs(operationType, targets),
    targets,
    conditions,
    effects,
    confidence,
    action,
    evidence: {
      ...(current.evidence || {}),
      method: appendEvidenceMethod(priorMethod || 'rule', 'semantic_llm'),
      llm_reason: refinement.reason || ''
    }
  };
  node.source_context = updateSourceContextActionEvidence(node.source_context, {
    action,
    operationType,
    extractionMethod: appendEvidenceMethod(
      node.source_context?.action_evidence?.extraction_method || priorMethod || 'rule',
      'semantic_llm'
    ),
    reason: refinement.reason || '',
    grounded: true
  });
}

function applySemanticGate(node, refinement) {
  const classification = refinement.classification || '';
  const actionability = refinement.actionability || '';

  // Negation dispatch. A deferred negated line is classified here by the LLM:
  //  - disclaimer  -> genuine capability disclaimer, drop to context (as before).
  //  - constraint  -> keep as a runtime action; a guard-kind constraint attaches
  //    the forbidden/conditional action to node conditions (DOE router already
  //    consumes negative-condition guards, no edge needed); an ordering-kind
  //    constraint additionally records a pending (before -> after) edge to be
  //    resolved after all nodes are extracted (resolvePendingConstraints).
  if (refinement.negation_kind === 'disclaimer') {
    return createContextNodeFromNode(node, 'doc_definition', {
      refinement,
      reason: refinement.reason || 'capability disclaimer is context only'
    });
  }
  if (refinement.negation_kind === 'constraint' && refinement.constraint_edge) {
    return applyNegationConstraint(node, refinement);
  }

  const contextKind = contextKindForClassification(classification, actionability);
  if (contextKind) {
    return createContextNodeFromNode(node, contextKind, {
      refinement,
      reason: refinement.reason || `${classification || actionability} is context only`
    });
  }

  applySemanticRefinement(node, refinement);
  if (node.formal_semantics?.evidence) {
    node.formal_semantics.evidence.method = appendEvidenceMethod(node.formal_semantics.evidence.method || 'rule', 'semantic_llm_gate');
  }
  node.semantic_gate = buildSemanticGateRecord(refinement, 'runtime_action');
  node.source_context = updateSourceContextActionEvidence(node.source_context, {
    action: node.formal_semantics?.action || node.docAction || '',
    operationType: node.formal_semantics?.operation_type || node.operationType || '',
    extractionMethod: appendEvidenceMethod(
      node.source_context?.action_evidence?.extraction_method || node.formal_semantics?.evidence?.method || 'rule',
      'semantic_llm_gate'
    ),
    reason: refinement.reason || '',
    grounded: true
  });
  return node;
}

// A prohibitive constraint stays a runtime-action node (it IS a real policy on
// the flow). guard-kind: attach the forbidden/conditional action to the node's
// formal_semantics.conditions so the DOE router's negative-condition gate picks
// it up — no new edge (per design decision, guards mark the node, not an edge).
// ordering-kind: same runtime-action node PLUS a pending (before -> after) edge
// stashed on the node; resolvePendingConstraints() links it to real nodes (or
// synthesizes endpoints) once the full node set exists.
function applyNegationConstraint(node, refinement) {
  applySemanticRefinement(node, refinement);
  const fs_ = node.formal_semantics || (node.formal_semantics = {});
  fs_.operation_type = 'guard';
  if (fs_.evidence) {
    fs_.evidence.method = appendEvidenceMethod(fs_.evidence.method || 'rule', 'semantic_llm_gate');
    fs_.evidence.role = 'prohibitive_constraint';
  }
  const edge = refinement.constraint_edge;
  const guardText = edge.kind === 'guard'
    ? edge.guarded_action
    : `${edge.before_action} must precede ${edge.after_action}`;
  fs_.conditions = Array.isArray(fs_.conditions) ? fs_.conditions : [];
  fs_.conditions.push({ type: 'condition', text: `constraint: ${guardText}` });

  if (edge.kind === 'ordering') {
    node.pending_constraint = {
      kind: 'ordering',
      before_action: edge.before_action,
      after_action: edge.after_action,
      note: edge.note || '',
      source_node: node.name,
      source_doc: node.ownerDoc || node.location?.file || '',
      source_section: node.location?.section || ''
    };
  }

  node.semantic_gate = buildSemanticGateRecord(refinement, 'runtime_action');
  node.source_context = updateSourceContextActionEvidence(node.source_context, {
    action: 'guard',
    operationType: 'guard',
    extractionMethod: appendEvidenceMethod(
      node.source_context?.action_evidence?.extraction_method || fs_.evidence?.method || 'rule',
      'semantic_llm_gate'
    ),
    reason: refinement.reason || 'prohibitive constraint',
    grounded: true
  });
  return node;
}

function applyCandidateSemanticGate(node, refinement) {
  if (!refinement) {
    return createContextNodeFromNode(node, 'doc_review_error', {
      reason: 'Invalid semantic LLM JSON',
      requiresReview: true
    });
  }
  return applySemanticGate(node, refinement);
}

function applyRuleOnlySemanticGate(node) {
  if (!shouldGateSemanticNode(node)) return node;
  const evidenceMethod = String(node.source_context?.action_evidence?.extraction_method || node.formal_semantics?.evidence?.method || '');
  if (evidenceMethod === 'implicit_object_read' || evidenceMethod === 'doc_review_route') {
    node.semantic_gate = {
      classification: 'workflow_instruction',
      actionability: 'runtime_action',
      grammar: 'derived runtime support node',
      completed_sentence: '',
      reason: `${evidenceMethod} remains an internal support flow node`,
      confidence: node.formal_semantics?.confidence,
      method: 'rule_candidate_gate'
    };
    return node;
  }
  const text = String(node.instructionText || node.formal_semantics?.evidence?.source_line || node.formal_semantics?.evidence?.text || '');
  const role = classifyMarkdownLineRole({
    line: text,
    ownerDoc: node.ownerDoc || node.location?.file || '',
    section: node.location?.section || ''
  });
  if (role.contextOnly) {
    return createContextNodeFromNode(node, role.semanticKind || 'doc_definition', {
      reason: role.reason || 'rule-only context gate',
      requiresReview: true,
      role
    });
  }

  const current = node.formal_semantics || {};
  node.formal_semantics = {
    ...current,
    confidence: Math.min(0.68, Number(current.confidence || 0.55)),
    evidence: {
      ...(current.evidence || {}),
      method: appendEvidenceMethod(current.evidence?.method || 'rule', 'rule_candidate_gate'),
      requires_review: true
    }
  };
  node.semantic_gate = {
    classification: 'workflow_instruction',
    actionability: 'runtime_action',
    grammar: role.grammar || '',
    completed_sentence: '',
    reason: role.reason || 'rule-only high precision action candidate',
    confidence: node.formal_semantics.confidence,
    method: 'rule_candidate_gate'
  };
  node.source_context = updateSourceContextActionEvidence(node.source_context, {
    extractionMethod: appendEvidenceMethod(
      node.source_context?.action_evidence?.extraction_method || current.evidence?.method || 'rule',
      'rule_candidate_gate'
    ),
    reason: node.semantic_gate.reason,
    grounded: true
  });
  if (node.source_context?.action_evidence) {
    node.source_context.action_evidence.requires_review = true;
  }
  return node;
}

function contextKindForClassification(classification, actionability) {
  if (actionability === 'runtime_action') return '';
  if (classification === 'definition') return 'doc_definition';
  if (classification === 'schema') return 'doc_schema';
  if (classification === 'example') return 'doc_example';
  if (classification === 'template') return 'doc_template';
  if (classification === 'discard') return 'doc_discard';
  if (classification === 'description' || actionability === 'context_only') return 'doc_definition';
  return '';
}

function createContextNodeFromNode(node, semanticKind, options = {}) {
  const refinement = options.refinement || {};
  const sourceContext = node.source_context || {};
  const semantics = node.formal_semantics || {};
  const gateRecord = buildSemanticGateRecord(refinement, 'context_only', {
    reason: options.reason || refinement.reason || '',
    method: semanticKind === 'doc_review_error' ? 'semantic_llm_gate_error' : 'semantic_llm_gate',
    role: options.role || null
  });
  const text = String(node.instructionText || semantics.evidence?.source_line || semantics.evidence?.text || sourceContext.source_line || '');
  const next = {
    ...node,
    name: String(node.name || '').replace(/^doc\.step\./, 'doc.context.').replace(/^doc\.op\./, 'doc.context.'),
    action: 'context',
    docAction: 'context',
    docActions: ['context'],
    operationType: 'context',
    description: `Documentation context in ${node.ownerDoc || node.location?.file || ''}: ${truncateForNode(text, 120)}`,
    input: {},
    output: {},
    formal_semantics: {
      operation_type: 'context',
      actor: 'documentation',
      inputs: [],
      outputs: [],
      targets: semantics.targets || [],
      conditions: [],
      effects: [],
      confidence: Math.min(0.65, Number(refinement.confidence || semantics.confidence || 0.45)),
      evidence: {
        ...(semantics.evidence || {}),
        text,
        method: gateRecord.method,
        llm_reason: gateRecord.reason,
        grammar: gateRecord.grammar,
        completed_sentence: gateRecord.completed_sentence
      },
      action: 'context'
    },
    source_context: updateSourceContextActionEvidence(sourceContext, {
      action: 'context',
      operationType: 'context',
      extractionMethod: gateRecord.method,
      reason: gateRecord.reason,
      grounded: true
    }),
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    excludeFromFlow: true,
    semanticKind,
    semantic_gate: gateRecord
  };
  if (next.source_context?.action_evidence) {
    next.source_context.action_evidence.requires_review = options.requiresReview ?? true;
  }
  return next;
}

function buildSemanticGateRecord(refinement = {}, actionability = '', extra = {}) {
  return {
    classification: refinement.classification || extra.classification || '',
    actionability: refinement.actionability || actionability || '',
    grammar: refinement.grammar || extra.grammar || '',
    completed_sentence: refinement.completed_sentence || extra.completed_sentence || '',
    reason: refinement.reason || extra.reason || '',
    confidence: typeof refinement.confidence === 'number' ? refinement.confidence : undefined,
    method: extra.method || 'semantic_llm_gate',
    ...(refinement.cache_hit ? { cache_hit: true } : {}),
    ...(refinement.negation_kind ? { negation_kind: refinement.negation_kind } : {}),
    ...(refinement.constraint_edge ? { constraint_edge: refinement.constraint_edge } : {}),
    ...(extra.role ? { role: extra.role } : {})
  };
}

function loadSemanticGateCache(options = {}) {
  const cachePath = resolveSemanticGateCachePath(options);
  const cache = {
    path: cachePath,
    records: new Map(),
    enabled: Boolean(cachePath)
  };
  if (!cache.enabled || !fs.existsSync(cachePath)) return cache;

  try {
    const lines = fs.readFileSync(cachePath, 'utf-8').split(/\r?\n/);
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const record = JSON.parse(line);
        if (!record?.key || !record.refinement) continue;
        const refinement = normalizeSemanticRefinement(record.refinement);
        if (refinement) cache.records.set(record.key, refinement);
      } catch {
        // Ignore a corrupt JSONL row; the next miss can refresh it.
      }
    }
  } catch {
    return {
      path: '',
      records: new Map(),
      enabled: false
    };
  }

  return cache;
}

function resolveSemanticGateCachePath(options = {}) {
  if (options.semanticGateCache === false || process.env.FCG_SEMANTIC_GATE_CACHE === '0') {
    return '';
  }
  if (typeof options.semanticGateCache === 'string' && options.semanticGateCache.trim()) {
    return path.resolve(options.semanticGateCache.trim());
  }
  if (process.env.FCG_SEMANTIC_GATE_CACHE && process.env.FCG_SEMANTIC_GATE_CACHE.trim()) {
    return path.resolve(process.env.FCG_SEMANTIC_GATE_CACHE.trim());
  }
  if (typeof options.semanticRefiner === 'function' || typeof options.semanticBatchRefiner === 'function') {
    return '';
  }
  return path.join(os.tmpdir(), 'skill-fcg-semantic-gate-cache.jsonl');
}

function buildSemanticGateCacheKey(node, options = {}) {
  const sourceText = [
    node.instructionText || '',
    node.source_context?.source_line || '',
    node.source_context?.action_evidence?.snippet || '',
    node.formal_semantics?.evidence?.text || '',
    node.formal_semantics?.evidence?.source_line || ''
  ].filter(Boolean).join('\n');
  const payload = {
    version: SEMANTIC_GATE_PROMPT_VERSION,
    provider: options.llmProvider || 'openai',
    model: options.llmModel || 'gpt-5.5',
    document: node.ownerDoc || node.location?.file || '',
    line: node.location?.line || 0,
    span: node.stepRange || node.source_context?.span || null,
    section: node.location?.section || '',
    semantic_kind: node.semanticKind || '',
    extraction_method: node.source_context?.action_evidence?.extraction_method || '',
    source_hash: crypto.createHash('sha256').update(sourceText).digest('hex')
  };
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(payload))
    .digest('hex');
}

function appendSemanticGateCacheRecord(cache, key, node, refinement, options = {}) {
  if (!cache?.enabled || !cache.path || !key || !refinement) return;
  if (cache.records.has(key)) return;

  const record = {
    key,
    prompt_version: SEMANTIC_GATE_PROMPT_VERSION,
    provider: options.llmProvider || 'openai',
    model: options.llmModel || 'gpt-5.5',
    document: node.ownerDoc || node.location?.file || '',
    line: node.location?.line || 0,
    node: node.name || '',
    refinement: stripRuntimeSemanticGateFields(refinement)
  };

  try {
    fs.mkdirSync(path.dirname(cache.path), { recursive: true });
    fs.appendFileSync(cache.path, `${JSON.stringify(record)}\n`, 'utf-8');
    cache.records.set(key, record.refinement);
  } catch {
    cache.enabled = false;
  }
}

function stripRuntimeSemanticGateFields(refinement = {}) {
  const {
    cache_hit: _cacheHit,
    ...rest
  } = refinement || {};
  return rest;
}

function truncateForNode(value, max) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function updateSourceContextActionEvidence(sourceContext = {}, patch = {}) {
  if (!sourceContext || typeof sourceContext !== 'object') return sourceContext;
  const current = sourceContext.action_evidence || {};
  return {
    ...sourceContext,
    action_evidence: {
      ...current,
      action: patch.action || current.action || '',
      operation_type: patch.operationType || current.operation_type || '',
      extraction_method: patch.extractionMethod || current.extraction_method || '',
      llm_reason: patch.reason || current.llm_reason || '',
      grounded: patch.grounded ?? current.grounded,
      requires_review: current.requires_review || patch.grounded === false
    }
  };
}

function appendEvidenceMethod(current, next) {
  const parts = String(current || '')
    .split('+')
    .map(part => part.trim())
    .filter(Boolean);
  const extra = String(next || '').trim();
  if (extra && !parts.includes(extra)) parts.push(extra);
  return parts.join('+') || extra || '';
}

function extractStepFlow(docs, docIndex) {
  const nodes = [];
  const edges = [];
  const stepsByDoc = new Map();

  for (const doc of docs) {
    const rawSteps = extractStepsFromDoc(doc, docIndex);
    if (rawSteps.length === 0) continue;

    const actionSteps = rawSteps.filter(isActionFlowNode);
    stepsByDoc.set(doc.file, actionSteps);

    for (const step of rawSteps) {
      nodes.push(step);
      addStepPrimaryEdges(edges, step);
    }

    addStepSequenceEdges(edges, doc.file, actionSteps);
    addObjectProducerEdges(edges, doc.file, actionSteps);
  }

  // Build jump edges across markdown files based on references in steps.
  for (const [docFile, steps] of stepsByDoc.entries()) {
    for (const step of steps) {
      if (!Array.isArray(step.stepRefs) || step.stepRefs.length === 0) continue;

      for (const targetDoc of step.stepRefs) {
        const targetSteps = stepsByDoc.get(targetDoc);
        const targetEntry = targetSteps && targetSteps[0];
        if (!targetEntry || targetEntry.name === step.name) continue;

        edges.push({
          source: step.name,
          target: targetEntry.name,
          type: 'control_flow',
          confidence: 0.63,
          validation_method: 'doc_flow',
          data_flow: {
            from_param: 'instruction',
            to_param: 'context',
            data_type: 'string'
          },
          semantic_reason: `Markdown reference jump from ${docFile} to ${targetDoc}`
        });
      }
    }
  }

  return { nodes, edges, stepsByDoc };
}

function extractReviewRouteFlow({ reviewDocs = [], extractionDocs = [], docIndex, stepsByDoc }) {
  const edges = [];
  const extractionFiles = new Set((extractionDocs || []).map(doc => normalizeDocPath(doc.file)));

  for (const doc of reviewDocs || []) {
    const docFile = normalizeDocPath(doc.file);
    if (!docFile || extractionFiles.has(docFile)) continue;
    const lines = String(doc.content || '').split('\n');
    let inCodeBlock = false;

    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      const trimmed = line.trim();
      if (/^```/.test(trimmed)) {
        inCodeBlock = !inCodeBlock;
        continue;
      }
      if (inCodeBlock || !trimmed) continue;

      const refs = extractFileRefsFromLine(trimmed);
      if (!refs.length) continue;
      const section = findSectionForLine(doc.sections || [], index + 1);

      for (const refInfo of refs) {
        const targetDoc = resolveDocReference(refInfo.ref, docFile, docIndex);
        if (!targetDoc) continue;
        const targetSteps = stepsByDoc.get(targetDoc);
        const routeContext = buildDocSourceContext({
          doc,
          line: index + 1,
          section,
          sourceLine: trimmed,
          action: inferActionFromLine(trimmed, refInfo.index),
          operationType: 'route',
          actionSnippet: trimmed,
          extractionMethod: 'doc_review_route',
          trigger: refInfo.ref
        });
        const targetEntry = targetSteps && targetSteps[0];
        if (!targetEntry?.name) continue;
        edges.push({
          source: 'user.query',
          target: targetEntry.name,
          type: 'doc_instruction',
          confidence: 0.46,
          validation_method: 'doc_review_route',
          data_flow: {
            from_param: 'query_text',
            to_param: 'file_path',
            data_type: 'string'
          },
          semantic_reason: `Review context in ${docFile} routes to ${targetDoc}`,
          source_context: routeContext
        });
      }
    }
  }

  return { edges };
}

function extractStepsFromDoc(doc, docIndex) {
  const steps = [];
  const lines = String(doc.content || '').split('\n');
  // Part 1: precompute block structure (multi-line bullet folding + list-block
  // disclaimer scope). Prose lines get no directive and are processed as before.
  const blockDirectives = segmentMarkdownBlocks(lines, doc.sections);
  let inCodeBlock = false;
  let codeBlockLang = '';
  let stepIndex = 0;
  const objectProducers = new Map();
  let lastObjectKey = '';
  let lastObjectText = '';

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    const trimmed = line.trim();

    const fenceMatch = trimmed.match(/^```+\s*([A-Za-z0-9_-]*)/);
    if (fenceMatch) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeBlockLang = fenceMatch[1] || '';
      } else {
        inCodeBlock = false;
        codeBlockLang = '';
      }
      continue;
    }
    if (inCodeBlock) {
      // Defect (1) fix: shell/command code blocks carry the strongest sink
      // evidence (curl/wget URLs, file writes). Extract each command line
      // instead of dropping the whole block.
      if (isShellFenceLang(codeBlockLang)) {
        const section = findSectionForLine(doc.sections, idx + 1);
        for (const command of classifyShellCommandLine(line)) {
          stepIndex += 1;
          steps.push(createCommandStepNode({
            doc,
            line: idx + 1,
            stepIndex,
            section,
            command
          }));
        }
      }
      continue;
    }
    if (!trimmed) continue;
    if (/^#{1,6}\s+/.test(trimmed)) continue;
    if (/^\|?\s*[-:| ]+\|?\s*$/.test(trimmed)) continue;

    // Part 1: a folded continuation line of a multi-line bullet was already
    // merged into its item's first line — skip it here.
    const directive = blockDirectives.get(idx);
    if (directive?.role === 'continuation') continue;

    // For a list item, classify/extract on the merged (multi-line) text and
    // carry the block's disclaimer scope. Prose lines keep the raw single line.
    const isListItem = directive?.role === 'item_start';
    const effectiveLine = isListItem ? directive.mergedText : line;
    const blockScope = isListItem ? directive.blockScope : null;

    const section = findSectionForLine(doc.sections, idx + 1);
    const lineRole = classifyMarkdownLineRole({
      line: effectiveLine,
      ownerDoc: doc.file,
      section,
      previousLine: lines[idx - 1] || '',
      nextLine: lines[idx + 1] || '',
      blockScope
    });
    if (lineRole.contextOnly) {
      stepIndex += 1;
      steps.push(createDocContextNode({
        doc,
        line: idx + 1,
        stepIndex,
        section,
        sourceLine: isListItem ? effectiveLine : trimmed,
        role: lineRole
      }));
      continue;
    }

    const semanticOps = extractSemanticOperationsFromLine({
      line: effectiveLine,
      ownerDoc: doc.file,
      lineNumber: idx + 1,
      section,
      docIndex
    });

    if (semanticOps.length === 0) continue;

    for (const operation of semanticOps) {
      const consumedObject = normalizeObjectInfo(operation.consumedObject) || (
        operation.operationType !== 'read' && referencesPriorObject(operation.sourceLine)
          ? { key: lastObjectKey, text: lastObjectText || lastObjectKey }
          : null
      );
      const producedObject = normalizeObjectInfo(operation.producedObject) || (
        operation.operationType === 'read' ? normalizeObjectInfo({ key: operation.objectKey, text: operation.objectText }) : null
      );

      let consumedProducer = null;
      if (consumedObject?.key) {
        if (!objectProducers.has(consumedObject.key) && isReadableDataObject(consumedObject.text || consumedObject.key)) {
          stepIndex += 1;
          const implicitStep = createDocStepNode({
            ownerDoc: doc.file,
            line: idx + 1,
            stepIndex,
            section,
            action: 'read',
            operationType: 'read',
            targetDoc: semanticTargetRef(doc.file, consumedObject.key),
            stepRefs: [],
            sourceLine: `Implicitly read ${consumedObject.text || consumedObject.key}`,
            formalSemantics: buildImplicitObjectReadSemantics({
              ownerDoc: doc.file,
              line: idx + 1,
              section,
              instructionText: operation.sourceLine || line,
              objectText: consumedObject.text || consumedObject.key,
              objectKey: consumedObject.key
            }),
            sourceContext: buildDocSourceContext({
              doc,
              line: idx + 1,
              section,
              sourceLine: operation.sourceLine || line,
              action: 'read',
              operationType: 'read',
              actionSnippet: `Implicitly read ${consumedObject.text || consumedObject.key}`,
              extractionMethod: 'implicit_object_read',
              trigger: consumedObject.text || consumedObject.key,
              grounded: false,
              derived: true,
              requiresReview: true
            })
          });
          steps.push(implicitStep);
          objectProducers.set(consumedObject.key, implicitStep);
        }
        consumedProducer = objectProducers.get(consumedObject.key);
      }

      stepIndex += 1;
      const step = createDocStepNode({
        ownerDoc: doc.file,
        line: idx + 1,
        stepIndex,
        section,
        action: operation.action,
        operationType: operation.operationType,
        targetDoc: operation.targetDoc,
        stepRefs: operation.stepRefs,
        sourceLine: operation.sourceLine,
        formalSemantics: operation.formalSemantics,
        sourceContext: buildDocSourceContext({
          doc,
          line: idx + 1,
          section,
          sourceLine: operation.sourceLine || line,
          action: operation.action,
          operationType: operation.operationType,
          actionSnippet: operation.sourceLine || line,
          extractionMethod: operation.formalSemantics?.evidence?.method || 'doc_flow',
          trigger: operation.operationType
        })
      });
      if (consumedProducer && consumedProducer.name !== step.name) {
        step.objectProducer = consumedProducer.name;
        step.objectKey = consumedObject.key;
      }
      if (consumedObject?.key) {
        step.formal_semantics.evidence.consumed_object_key = consumedObject.key;
        step.formal_semantics.evidence.consumed_object_text = consumedObject.text || consumedObject.key;
      }
      if (producedObject?.key) {
        step.formal_semantics.evidence.produced_object_key = producedObject.key;
        step.formal_semantics.evidence.produced_object_text = producedObject.text || producedObject.key;
      }
      steps.push(step);

      if (producedObject?.key && producesObject(operation.operationType)) {
        objectProducers.set(producedObject.key, step);
        lastObjectKey = producedObject.key;
        lastObjectText = producedObject.text || producedObject.key;
      } else if (consumedObject?.key) {
        lastObjectKey = consumedObject.key;
        lastObjectText = consumedObject.text || consumedObject.key;
      }
    }
  }

  return steps;
}

function buildStepMember(step) {
  return {
    raw_name: String(step.name || ''),
    line: Number(step.location?.line || 0),
    section: String(step.location?.section || ''),
    step_index: Number(step.stepIndex || 0),
    action: String(step.docAction || step.action || 'read'),
    operation_type: String(step.formal_semantics?.operation_type || step.operationType || step.docAction || step.action || 'read'),
    doc_ref: String(step.docRef || ''),
    instruction: String(step.instructionText || ''),
    formal_semantics: step.formal_semantics || null
  };
}

function createDocOperationNode(group, opIndex) {
  const ownerDoc = normalizeDocPath(group.ownerDoc);
  const targetDoc = normalizeDocPath(group.docRef || ownerDoc);
  const ownerSlug = fileSlug(ownerDoc);
  const targetSlug = fileSlug(targetDoc);
  const action = group.action || 'read';
  const operationType = group.operationType || action;
  const linePart = group.startLine === group.endLine
    ? `l${group.startLine}`
    : `l${group.startLine}_${group.endLine}`;
  const nodeName = `doc.op.${ownerSlug}.${linePart}.o${opIndex}.${operationType}.${targetSlug}`;
  const memberCount = group.members.length;
  const section = group.section || '';
  const instructionPreview = buildInstructionPreview(group.members);

  const description = memberCount === 1
    ? `Operation in ${ownerDoc}: ${instructionPreview || `${action} ${targetDoc}`}`
    : `Merged ${memberCount} continuous ${action} operations in ${ownerDoc} (lines ${group.startLine}-${group.endLine}) targeting ${targetDoc}`;

  return {
    name: nodeName,
    action,
    type: 'custom_func',
    description,
    input: buildStepInput(action, targetDoc),
    output: buildStepOutput(action),
    location: {
      file: ownerDoc,
      line: group.startLine || 0,
      section
    },
    ownerDoc,
    docRef: targetDoc,
    docAction: action,
    docActions: [action],
    operationType,
    stepIndex: group.startStepIndex || opIndex,
    stepRange: {
      start: group.startStepIndex || opIndex,
      end: group.endStepIndex || opIndex
    },
    stepRefs: Array.from(group.stepRefs || []).map(normalizeDocPath).filter(Boolean).sort(),
    instructionText: instructionPreview,
    member_step_count: memberCount,
    member_steps: group.members,
    formal_semantics: mergeFormalSemantics(group, operationType, action, targetDoc, instructionPreview),
    source_context: config.sourceContext || buildDocSourceContext({
      doc: { file: ownerDoc, content: '', sections: [] },
      line: group.startLine || 0,
      section,
      sourceLine: instructionPreview,
      action,
      operationType,
      actionSnippet: instructionPreview,
      extractionMethod: 'doc_operation'
    }),
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    semanticKind: 'doc_operation'
  };
}

function buildInstructionPreview(members) {
  const lines = [];
  for (const member of members || []) {
    const text = String(member.instruction || '').trim();
    if (!text) continue;
    if (lines.includes(text)) continue;
    lines.push(text);
    if (lines.length >= 2) break;
  }
  const preview = lines.join(' | ');
  return preview.length > 160 ? `${preview.slice(0, 157)}...` : preview;
}

function createDocStepNode(config) {
  const ownerDoc = normalizeDocPath(config.ownerDoc);
  const targetDoc = normalizeDocPath(config.targetDoc || config.ownerDoc);
  const ownerSlug = fileSlug(ownerDoc);
  const targetSlug = fileSlug(targetDoc);
  const action = config.action || 'read';
  const operationType = config.operationType || config.formalSemantics?.operation_type || action;

  const nodeName = `doc.step.${ownerSlug}.l${config.line}.s${config.stepIndex}.${operationType}.${targetSlug}`;
  const section = config.section || '';
  const lineText = String(config.sourceLine || '').trim();
  const shortLine = lineText.length > 120 ? `${lineText.slice(0, 117)}...` : lineText;

  return {
    name: nodeName,
    action,
    type: 'custom_func',
    description: `Step ${config.stepIndex} in ${ownerDoc}: ${shortLine || 'instruction step'}`,
    input: buildStepInput(action, targetDoc),
    output: buildStepOutput(action),
    location: {
      file: ownerDoc,
      line: config.line || 0,
      section
    },
    ownerDoc,
    docRef: targetDoc,
    docAction: action,
    docActions: [action],
    operationType,
    stepIndex: config.stepIndex,
    stepRefs: Array.isArray(config.stepRefs) ? config.stepRefs.map(normalizeDocPath).filter(Boolean) : [],
    instructionText: lineText,
    formal_semantics: config.formalSemantics || createFallbackFormalSemantics({
      operationType,
      action,
      ownerDoc,
      line: config.line,
      section,
      instructionText: lineText,
      targetDoc
    }),
    source_context: config.sourceContext || buildDocSourceContext({
      doc: { file: ownerDoc, content: '', sections: [] },
      line: config.line || 0,
      section,
      sourceLine: lineText,
      action,
      operationType,
      actionSnippet: lineText,
      extractionMethod: 'doc_step'
    }),
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    semanticKind: 'doc_step'
  };
}

/**
 * Build a doc_step node from a classified shell command found in a fenced
 * code block. Shaped identically to createDocStepNode so downstream stages
 * (node-splitter, observation-analyzer, edge building) treat it as any other
 * grounded runtime action. This is the node-producing half of the defect (1)
 * fix.
 * @param {Object} config
 * @returns {Object}
 */
function createCommandStepNode(config) {
  const doc = config.doc || {};
  const ownerDoc = normalizeDocPath(doc.file || '');
  const ownerSlug = fileSlug(ownerDoc);
  const command = config.command || {};
  const operationType = command.operationType || 'invoke_tool';
  const action = OPERATION_DOC_ACTION[operationType] || 'run';
  const section = config.section || '';
  const snippet = String(command.segment || '').trim();
  const shortSnippet = snippet.length > 120 ? `${snippet.slice(0, 117)}...` : snippet;

  const targets = (command.targets || []).map(target => ({
    type: target.type,
    value: target.value,
    raw: target.raw || target.value
  }));
  const primaryTarget = targets[0]
    ? targets[0].value
    : semanticTargetRef(ownerDoc, command.command || operationType);
  const targetSlug = fileSlug(primaryTarget);

  const nodeName = `doc.step.${ownerSlug}.l${config.line}.s${config.stepIndex}.${operationType}.${targetSlug}`;

  const formalSemantics = buildFormalSemantics({
    operationType,
    action,
    ownerDoc,
    line: config.line,
    section,
    instructionText: snippet,
    clauseText: snippet,
    targets: targets.length ? targets : [{ type: 'command', value: command.command || snippet, raw: snippet }],
    conditions: []
  });
  formalSemantics.actor = 'shell';
  formalSemantics.evidence.method = 'doc_code_block_command';

  return {
    name: nodeName,
    action,
    type: 'custom_func',
    description: `Command in ${ownerDoc}: ${shortSnippet || command.command}`,
    input: buildStepInput(action, primaryTarget),
    output: buildStepOutput(action),
    location: {
      file: ownerDoc,
      line: config.line || 0,
      section
    },
    ownerDoc,
    docRef: ownerDoc,
    docAction: action,
    docActions: [action],
    operationType,
    stepIndex: config.stepIndex,
    stepRefs: [],
    instructionText: snippet,
    formal_semantics: formalSemantics,
    source_context: buildDocSourceContext({
      doc,
      line: config.line || 0,
      section,
      sourceLine: snippet,
      action,
      operationType,
      actionSnippet: snippet,
      extractionMethod: 'doc_code_block_command',
      trigger: command.command || operationType,
      grounded: true
    }),
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    semanticKind: 'doc_step'
  };
}

function createDocContextNode(config) {
  const ownerDoc = normalizeDocPath(config.doc?.file || '');
  const ownerSlug = fileSlug(ownerDoc);
  const role = config.role || {};
  const semanticKind = role.semanticKind || 'doc_definition';
  const kindSlug = stableSlug(semanticKind.replace(/^doc_/, ''));
  const lineText = String(config.sourceLine || '').trim();
  const shortLine = lineText.length > 120 ? `${lineText.slice(0, 117)}...` : lineText;
  const nodeName = `doc.context.${ownerSlug}.l${config.line}.s${config.stepIndex}.${kindSlug}`;

  const sourceContext = buildDocSourceContext({
    doc: config.doc,
    line: config.line || 0,
    section: config.section || '',
    sourceLine: lineText,
    action: 'context',
    operationType: 'context',
    actionSnippet: lineText,
    extractionMethod: role.method || 'doc_context_gate',
    trigger: role.reason || semanticKind,
    grounded: true,
    requiresReview: true
  });

  return {
    name: nodeName,
    action: 'context',
    type: 'custom_func',
    description: `Documentation context in ${ownerDoc}: ${shortLine || semanticKind}`,
    input: {},
    output: {},
    location: {
      file: ownerDoc,
      line: config.line || 0,
      section: config.section || ''
    },
    ownerDoc,
    docRef: ownerDoc,
    docAction: 'context',
    docActions: ['context'],
    operationType: 'context',
    stepIndex: config.stepIndex,
    stepRefs: [],
    instructionText: lineText,
    formal_semantics: {
      operation_type: 'context',
      actor: 'documentation',
      inputs: [],
      outputs: [],
      targets: [{ type: 'document', value: ownerDoc, raw: ownerDoc }],
      conditions: [],
      effects: [],
      confidence: 0.55,
      evidence: {
        text: lineText,
        source_line: lineText,
        file: ownerDoc,
        line: config.line || 0,
        section: config.section || '',
        method: role.method || 'doc_context_gate',
        role: role.role || '',
        grammar: role.grammar || '',
        reason: role.reason || ''
      },
      action: 'context'
    },
    source_context: sourceContext,
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    excludeFromFlow: true,
    semanticKind,
    semantic_gate: {
      classification: role.classification || semanticKind.replace(/^doc_/, ''),
      actionability: 'context_only',
      grammar: role.grammar || '',
      completed_sentence: role.completed_sentence || '',
      reason: role.reason || '',
      method: role.method || 'doc_context_gate'
    }
  };
}

function classifyMarkdownLineRole(config = {}) {
  const ownerDoc = normalizeDocPath(config.ownerDoc || '');
  const section = String(config.section || '');
  const raw = String(config.line || '').trim();
  const clean = stripMarkdownListMarker(raw);
  const lower = clean.toLowerCase();
  const fileLower = ownerDoc.toLowerCase();
  const previous = String(config.previousLine || '').trim().toLowerCase();
  const blockScope = config.blockScope || null;

  if (!clean) return { contextOnly: false };

  // Defect (2) fix + Part 1: negated statements, disclaimer sections, and list
  // items under a disclaimer lead-in ("What this skill does NOT do:") describe
  // what the skill does NOT do. Treat as context, never as runtime actions.
  //
  // Two scope strengths:
  //  - STRONG ('disclaimer'): the list's lead-in explicitly negates the whole
  //    list ("What this skill does NOT do:"). Its items ARE the negated actions
  //    ("does not [connect], [send], [execute]"), so even imperative-looking
  //    bullets are suppressed. Real egress, if any, is caught by script/code-
  //    block extraction, which is never subject to prose disclaimer scope.
  //  - SOFT (section heading like "Limitations"): keep reverse protection — an
  //    explicit imperative runtime instruction in such a section may be a real
  //    sink (e.g. weather's `- PNG: curl ... -o file`), so it is NOT suppressed.
  const strongDisclaimerScope = blockScope === 'disclaimer';
  const softNegationScope = isNegationScopeHeading(section) && !looksImperativeRuntimeInstruction(clean);
  // STRONG disclaimer scope ("What this skill does NOT do:" lead-in) and a soft
  // negation SECTION heading remain high-confidence disclaimers -> context, as
  // before. But a bare negated action line ("Never install without vetting",
  // "Never overwrite existing files") is NOT necessarily a disclaimer: it is
  // often a PROHIBITIVE CONSTRAINT that implies an ordering/guard on a real
  // action. The rule cannot reliably tell these apart (verb enumeration misses
  // infer/lose/... — see quantify-negation-misclass: 66% land in "other"), so
  // instead of dropping it we DEFER to the LLM semantic gate, which classifies
  // negation_kind (disclaimer|constraint) and extracts the constraint edge.
  if (strongDisclaimerScope || softNegationScope) {
    return {
      contextOnly: true,
      semanticKind: 'doc_definition',
      classification: 'disclaimer',
      role: 'negated_disclaimer',
      grammar: 'negated clause; states an action the skill does not perform',
      reason: strongDisclaimerScope
        ? 'list item under an explicit disclaimer lead-in ("does NOT do")'
        : 'negated/disclaimer statement is not a runtime action',
      method: 'rule_context_gate'
    };
  }
  if (isNegatedActionText(clean)) {
    // Defer: keep it as a runtime-action candidate so it is extracted as a
    // doc_step and sent through the semantic gate. The LLM decides disclaimer
    // vs constraint downstream (applySemanticGate).
    return {
      contextOnly: false,
      deferNegation: true,
      role: 'negation_pending',
      grammar: 'negated clause; disclaimer-vs-constraint deferred to semantic gate',
      reason: 'negated action deferred to LLM semantic gate for disclaimer/constraint classification'
    };
  }

    if (isMarkdownTableDefinitionRow(clean, previous) && !isSkillAnchorRouteTableRow(clean, ownerDoc, section, previous)) {
    return {
      contextOnly: true,
      semanticKind: 'doc_definition',
      classification: 'definition',
      role: 'definition_table_row',
      grammar: 'table_row definition; subject is the row key, predicate describes its meaning',
      reason: 'table row defines terminology or status meaning, not a runtime action',
      method: 'rule_context_gate'
    };
  }

  if (/^\*\*[A-Za-z][^*]{0,40}\*\*:\s*[^.]+(?:\s*\|\s*[^.]+)+$/.test(clean)) {
    return {
      contextOnly: true,
      semanticKind: 'doc_schema',
      classification: 'schema',
      role: 'metadata_enum',
      grammar: 'field schema or enum declaration',
      reason: 'metadata enum describes allowed values',
      method: 'rule_context_gate'
    };
  }

  if (/\b(template|example|sample)\b/i.test(fileLower) && !looksImperativeRuntimeInstruction(clean)) {
    return {
      contextOnly: true,
      semanticKind: fileLower.includes('template') ? 'doc_template' : 'doc_example',
      classification: fileLower.includes('template') ? 'template' : 'example',
      role: 'template_or_example_source',
      grammar: 'descriptive/template context',
      reason: 'template or example file text is not a runtime instruction without imperative action',
      method: 'rule_context_gate'
    };
  }

  if (isPassiveDefinitionFragment(clean)) {
    return {
      contextOnly: true,
      semanticKind: 'doc_definition',
      classification: 'definition',
      role: 'passive_definition_fragment',
      grammar: 'passive fragment; missing subject is a documented term or prior noun phrase',
      completed_sentence: completePassiveFragment(clean, section),
      reason: 'passive descriptive fragment is not an instruction to read or write the referenced target',
      method: 'rule_context_gate'
    };
  }

  if (isPureDescription(clean)) {
    return {
      contextOnly: true,
      semanticKind: 'doc_definition',
      classification: 'description',
      role: 'description',
      grammar: 'descriptive clause',
      reason: 'line describes document purpose or concepts',
      method: 'rule_context_gate'
    };
  }

  return {
    contextOnly: false,
    grammar: looksImperativeRuntimeInstruction(clean) ? 'imperative or explicit runtime instruction' : ''
  };
}

function isMarkdownTableDefinitionRow(clean, previous) {
  if (!clean.includes('|')) return false;
  if (/^\|?\s*[-:| ]+\|?\s*$/.test(clean)) return false;
  const cells = parseMarkdownTableCells(clean);
  if (cells.length < 2) return false;
  const headerish = previous.includes('|') && /\b(status|meaning|field|description|category|area|type|value|name|purpose)\b/i.test(previous);
  const firstCellLooksTerm = /^`?[\w.-]+`?$/.test(cells[0]) || cells[0].length <= 32;
  const second = cells.slice(1).join(' ');
  const explicitInstruction = looksImperativeRuntimeInstruction(second) && /\b(you|agent|assistant|must|should|run|execute|call|read|write|save|send|upload)\b/i.test(second);
  return (headerish || (cells.length === 2 && firstCellLooksTerm)) && !explicitInstruction;
}

function isSkillAnchorRouteTableRow(clean, ownerDoc, section, previous) {
  if (normalizeDocPath(ownerDoc) !== 'SKILL.md') return false;
  if (!clean.includes('|')) return false;
  const headerText = `${previous || ''} ${section || ''}`.toLowerCase();
  if (!/\b(quick reference|situation|action|trigger|when|condition|route|routing|workflow|policy)\b/.test(headerText)) return false;
  const cells = parseMarkdownTableCells(clean);
  if (cells.length < 2) return false;
  const action = cells.slice(1).join(' ');
  return looksImperativeRuntimeInstruction(action) ||
    /\b(log|append|write|promote|review|send|create|update|consider)\b/i.test(action);
}

function parseMarkdownTableCells(line) {
  return String(line || '')
    .replace(/^\|\s*|\s*\|$/g, '')
    .split('|')
    .map(cell => cell.trim())
    .filter(Boolean);
}

function looksImperativeRuntimeInstruction(text) {
  const value = String(text || '').trim().toLowerCase();
  if (!value) return false;
  if (/^(?:must|should|always|never|do not|don't|use|read|write|save|store|append|run|execute|call|invoke|send|post|upload|generate|create|summarize|extract|validate|verify|check|ensure|open|load|fetch|retrieve|review)\b/.test(value)) {
    return true;
  }
  if (/^(?:when|if|after|before|once|unless)\b[\s\S]{0,120}\b(?:read|write|save|run|execute|call|invoke|send|post|upload|generate|create|add|update|append)\b/.test(value)) {
    return true;
  }
  return false;
}

function isPassiveDefinitionFragment(text) {
  const value = String(text || '').trim();
  return /^(?:elevated|extracted|captured|recorded|stored|saved|written|generated|created|used|intended|designed|defined|listed)\b/i.test(value) &&
    !looksImperativeRuntimeInstruction(value);
}

function completePassiveFragment(text, section) {
  const subject = section ? `The item in ${section}` : 'The documented item';
  return `${subject} is ${String(text || '').trim()}`;
}

function isPureDescription(text) {
  const value = String(text || '').trim();
  if (looksImperativeRuntimeInstruction(value)) return false;
  if (/^[A-Z][^.?!]{10,}\.$/.test(value) && !ACTION_KEYWORDS.some(keyword => value.toLowerCase().includes(keyword))) return true;
  if (/^(?:this|these|the file|the document|corrections|insights|knowledge gaps)\b/i.test(value) &&
      /\b(?:is|are|contains|captures|describes|lists|defines)\b/i.test(value)) {
    return true;
  }
  return false;
}

function extractSemanticOperationsFromLine(config) {
  const {
    line,
    ownerDoc,
    lineNumber,
    section,
    docIndex
  } = config;
  const sourceLine = String(line || '').trim();
  const cleanLine = stripMarkdownListMarker(sourceLine);
  const conditions = extractLineConditions(cleanLine);
  const operations = [];
  const anchorRoute = extractSkillAnchorRouteOperation({
    sourceLine,
    cleanLine,
    ownerDoc,
    lineNumber,
    section,
    docIndex
  });
  if (anchorRoute) return [anchorRoute];

  if (!isActionableInstructionLine(cleanLine) &&
      !isSemanticInstructionLine(cleanLine) &&
      extractFileRefsFromLine(cleanLine).length === 0 &&
      conditions.length === 0) {
    return operations;
  }

  if (conditions.length > 0) {
    const operationType = inferConditionOperationType(conditions);
    const action = OPERATION_DOC_ACTION[operationType] || 'condition';
    const targetDoc = semanticTargetRef(ownerDoc, operationType);
    operations.push({
      action,
      operationType,
      targetDoc,
      stepRefs: [],
      sourceLine,
      formalSemantics: buildFormalSemantics({
        operationType,
        action,
        ownerDoc,
        line: lineNumber,
        section,
        instructionText: sourceLine,
        clauseText: conditions.join('; '),
        targets: [{ type: 'instruction', value: targetDoc, raw: cleanLine }],
        conditions
      })
    });
  }

  for (const clause of splitInstructionClauses(cleanLine)) {
    const clauseText = clause.trim();
    if (!clauseText || !isActionableClause(clauseText)) continue;

    const operationType = inferOperationType(clauseText);
    if (operationType === 'condition' && operations.length > 0) continue;

    const action = OPERATION_DOC_ACTION[operationType] || inferActionFromLine(clauseText, -1);
    const targetInfo = extractOperationTargets(clauseText, ownerDoc, docIndex);
    const objectInfo = inferDataObjectFromClause(clauseText, operationType);
    const targetDoc = targetInfo.primaryTarget || semanticTargetRef(ownerDoc, operationType);
    const stepRefs = targetInfo.fileRefs;
    const fallbackObject = objectInfo.consumed || objectInfo.produced || {};

    operations.push({
      action,
      operationType,
      targetDoc,
      stepRefs,
      sourceLine: clauseText,
      objectKey: fallbackObject.key || '',
      objectText: fallbackObject.text || '',
      consumedObject: objectInfo.consumed || null,
      producedObject: objectInfo.produced || null,
      formalSemantics: buildFormalSemantics({
        operationType,
        action,
        ownerDoc,
        line: lineNumber,
        section,
        instructionText: sourceLine,
        clauseText,
        targets: targetInfo.targets,
        conditions
      })
    });
  }

  return dedupeSemanticOperations(operations);
}

function extractSkillAnchorRouteOperation(config = {}) {
  const ownerDoc = normalizeDocPath(config.ownerDoc || '');
  if (ownerDoc !== 'SKILL.md') return null;

  const cleanLine = String(config.cleanLine || '').trim();
  if (!cleanLine.includes('|')) return null;

  const cells = parseMarkdownTableCells(cleanLine);
  if (cells.length < 2) return null;

  const headerText = String(config.section || '').toLowerCase();
  const actionText = cells.slice(1).join(' | ');
  const routeSection = /\b(quick reference|situation|action|trigger|route|routing|workflow|policy|when)\b/.test(headerText);
  const routeAction = looksImperativeRuntimeInstruction(actionText) ||
    /\b(log|append|write|promote|review|send|create|update|consider|link)\b/i.test(actionText);
  if (!routeSection || !routeAction) return null;

  const situation = cells[0];
  const routeConditions = [{
    type: inferConditionKind(situation),
    text: situation
  }];
  const operationType = inferOperationType(actionText);
  const action = OPERATION_DOC_ACTION[operationType] || inferActionFromLine(actionText, -1);
  const targetInfo = extractOperationTargets(actionText, ownerDoc, config.docIndex);
  const objectInfo = inferDataObjectFromClause(actionText, operationType);
  const targetDoc = targetInfo.primaryTarget || semanticTargetRef(ownerDoc, actionText);
  const fallbackObject = objectInfo.consumed || objectInfo.produced || {};
  const formalSemantics = buildFormalSemantics({
    operationType,
    action,
    ownerDoc,
    line: config.lineNumber,
    section: config.section,
    instructionText: config.sourceLine,
    clauseText: actionText,
    targets: targetInfo.targets,
    conditions: routeConditions
  });
  formalSemantics.evidence = {
    ...(formalSemantics.evidence || {}),
    method: 'skill_anchor_route',
    source_line: config.sourceLine || cleanLine,
    situation,
    action_text: actionText
  };

  return {
    action,
    operationType,
    targetDoc,
    stepRefs: targetInfo.fileRefs,
    sourceLine: config.sourceLine || cleanLine,
    objectKey: fallbackObject.key || '',
    objectText: fallbackObject.text || '',
    consumedObject: objectInfo.consumed || null,
    producedObject: objectInfo.produced || null,
    formalSemantics
  };
}

function producesObject(operationType) {
  return ['read', 'transform', 'model_inference', 'external_egress', 'write', 'produce_artifact'].includes(operationType);
}

function inferDataObjectFromClause(clauseText, operationType) {
  const text = String(clauseText || '').trim();
  if (!text || !isEnglishText(text)) return emptyObjectUsage();

  const lower = text.toLowerCase();
  const consumed = inferConsumedObject(lower, operationType);
  const produced = inferProducedObject(lower, operationType, consumed);

  return {
    consumed: normalizeObjectInfo(consumed),
    produced: normalizeObjectInfo(produced),
    key: normalizeObjectInfo(consumed)?.key || normalizeObjectInfo(produced)?.key || '',
    text: normalizeObjectInfo(consumed)?.text || normalizeObjectInfo(produced)?.text || ''
  };
}

function inferConsumedObject(lower, operationType) {
  if (operationType === 'read') return null;

  if (operationType === 'write') {
    const match = lower.match(/\b(?:write|save|store|persist|export)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+(?:to|into|in|locally|as)\b/i);
    return objectInfoFromText(match?.[1] || findKnownObjectPhrase(lower));
  }

  if (operationType === 'produce_artifact') {
    const consumedText = inferProducedArtifactConsumedText(lower);
    if (!consumedText || !isReadableDataObject(consumedText)) return null;
    return objectInfoFromText(consumedText);
  }

  if (operationType === 'transform') {
    const match = lower.match(/\b(?:summarize|digest|brief|extract|classify|parse|analyze|redact|mask|sanitize)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+(?:into|as|to)\b|\s+and\b|$)/i);
    return objectInfoFromText(match?.[1] || findKnownObjectPhrase(lower));
  }

  if (operationType === 'external_egress' || operationType === 'model_inference' || operationType === 'invoke_tool') {
    const match = lower.match(/\b(?:send|upload|post|call|invoke|provide|pass|forward)\s+(?:the\s+|a\s+|an\s+)?(.+?)\s+(?:to|into|in|via|through)\b/i);
    return objectInfoFromText(match?.[1] || findKnownObjectPhrase(lower));
  }

  return objectInfoFromText(findKnownObjectPhrase(lower));
}

function inferProducedObject(lower, operationType, consumed) {
  if (operationType === 'read') {
    const match = lower.match(/\b(?:read|get|fetch|retrieve|load|search|query|open|inspect)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+and\b|\s+to\b|$)/i);
    return objectInfoFromText(match?.[1] || findKnownObjectPhrase(lower));
  }

  if (operationType === 'produce_artifact') {
    const match = lower.match(/\b(?:generate|create|produce|output|build|compose|draft)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+(?:about|from|using|based\s+on|with)\b|\s+and\b|\s+then\b|$)/i);
    return objectInfoFromText(match?.[1] || findKnownObjectPhrase(lower));
  }

  if (operationType === 'transform') {
    const explicit = lower.match(/\b(?:into|as|to)\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,3})(?:\s+and\b|$)/i);
    if (explicit) return objectInfoFromText(explicit[1]);
    if (/\b(summarize|summary|digest|brief)\b/i.test(lower)) return objectInfoFromText('summary');
    if (/\b(redact|mask|sanitize|scrub)\b/i.test(lower)) return objectInfoFromText('safe content');
    if (/\bextract\b/i.test(lower)) return objectInfoFromText(inferExtractedObject(lower) || 'extracted field');
  }

  if (operationType === 'write') {
    return consumed;
  }

  return null;
}

function findKnownObjectPhrase(text) {
  const patterns = [
    /\b(email content|mail content|customer records|chat history|conversation history|invoice pdf|invoice document|file content|report content|analysis result|user profile|customer profile|message content|raw report)\b/i,
    /\b(?:the|a|an)\s+(summary|report|profile|message|file|document|invoice|attachment|email|record|records|result)\b/i,
    /\b(?:the|a|an)?\s*([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,2})\s+(?:content|records|history|profile|message)\b/i
  ];
  for (const pattern of patterns) {
    const match = String(text || '').match(pattern);
    if (match) return (match[1] || match[0] || '').trim();
  }
  return '';
}

function inferProducedArtifactConsumedText(text) {
  const value = String(text || '').trim();
  const match = value.match(/\b(?:about|from|using|based\s+on|with)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+and\b|\s+then\b|$)/i);
  if (!match) return '';
  return match[1].trim();
}

function normalizeObjectClassText(text) {
  return cleanObjectText(text).replace(/[_.-]+/g, ' ').trim();
}

function isAbstractContextObject(text) {
  const normalized = normalizeObjectClassText(text);
  if (!normalized) return false;

  return [
    /^(?:current|this|that)\s+(?:ai|agent|assistant|task|context|state|request|instruction|workflow|skill|answer|response|conversation|session|environment)$/i,
    /^(?:current\s+)?(?:ai|agent|assistant|task|context|state|request|instruction|workflow|skill|answer|response|work)$/i,
    /^(?:assistant|agent|model|ai)\s+(?:behavior|behaviour|state|policy|capability|response|answer)$/i,
    /^(?:this\s+)?(?:skill|workflow)$/i
  ].some(pattern => pattern.test(normalized));
}

function isArtifactLikeObject(text) {
  const normalized = normalizeObjectClassText(text);
  if (!normalized || isAbstractContextObject(normalized)) return false;

  return [
    /^(?:report|summary|result|document|file)$/i,
    /^(?:analysis|final|draft|generated|output)\s+(?:report|summary|result|document|file)$/i
  ].some(pattern => pattern.test(normalized));
}

function isReadableDataObject(text) {
  const normalized = normalizeObjectClassText(text);
  if (!normalized || isAbstractContextObject(normalized)) return false;
  if (isArtifactLikeObject(normalized)) return true;

  return [
    /\b(?:email|mail)(?:\s+(?:content|message|body|thread|attachment))?\b/i,
    /\b(?:customer|user|client|patient|employee|account)?\s*records?\b/i,
    /\b(?:chat|conversation|message)\s+history\b/i,
    /\b(?:user|customer|account)?\s*profile\b/i,
    /\b(?:file|document|report|message|email|mail|invoice|pdf|attachment)\s+content\b/i,
    /\binvoice\s+(?:pdf|document|file)?\b/i,
    /\b(?:database|table|row|rows|column|columns|query result|dataset|spreadsheet)\b/i,
    /\bbrowser\s+(?:cookie|cookies|history|data)\b|\bcookies?\b/i,
    /\bcalendar(?:\s+(?:event|events|entry|entries))?\b/i,
    /\bcontacts?\b/i,
    /\blogs?\b/i,
    /\b(?:message|attachment|note|notes)\b/i
  ].some(pattern => pattern.test(normalized));
}

function inferExtractedObject(text) {
  const match = String(text || '').match(/\bextract\s+(?:the\s+|a\s+|an\s+)?([a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,2})\s+from\b/i);
  return match ? match[1] : '';
}

function objectInfoFromText(value) {
  const text = cleanObjectText(value);
  const key = objectKeyFromText(text);
  return key ? { key, text } : null;
}

function normalizeObjectInfo(value) {
  if (!value || typeof value !== 'object') return null;
  return objectInfoFromText(value.text || value.key || '');
}

function emptyObjectUsage() {
  return { consumed: null, produced: null, key: '', text: '' };
}

function isEnglishText(text) {
  return /^[\x00-\x7F]+$/.test(String(text || ''));
}

function cleanObjectText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\b(the|a|an|it|locally|local|raw|full|original)\b/g, ' ')
    .replace(/\b(to|into|in|as|via|through|with|from|for|on|at)\b.*$/g, ' ')
    .replace(/[^\w\s.-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function objectKeyFromText(value) {
  const cleaned = cleanObjectText(value);
  if (!cleaned || cleaned.length < 3) return '';
  return stableSlug(cleaned);
}

function referencesPriorObject(text = '') {
  return /\b(it|this|that|them|the same|same data|same content|summary)\b/i.test(String(text || ''));
}

function buildImplicitObjectReadSemantics(config) {
  const objectText = config.objectText || config.objectKey || 'data';
  const target = { type: inferObjectTargetType(objectText), value: objectText, raw: objectText };
  const semantics = buildFormalSemantics({
    operationType: 'read',
    action: 'read',
    ownerDoc: config.ownerDoc,
    line: config.line,
    section: config.section,
    instructionText: config.instructionText,
    clauseText: `Implicitly read ${objectText}`,
    targets: [target],
    conditions: []
  });
  return {
    ...semantics,
    confidence: Math.min(0.72, Number(semantics.confidence || 0.6)),
    evidence: {
      ...semantics.evidence,
      method: 'implicit_object_read',
      object_key: config.objectKey || objectKeyFromText(objectText),
      source_line: config.instructionText || semantics.evidence.source_line || ''
    }
  };
}

function buildDocSourceContext({
  doc = {},
  line = 0,
  section = '',
  sourceLine = '',
  action = '',
  operationType = '',
  actionSnippet = '',
  extractionMethod = 'doc_flow',
  trigger = '',
  grounded = true,
  derived = false,
  requiresReview = false
}) {
  return buildSourceContext({
    content: doc.content || '',
    file: doc.file || '',
    line,
    section,
    sourceText: sourceLine,
    action,
    operationType,
    actionSnippet,
    extractionMethod,
    trigger,
    sourceRole: doc.source_role || (normalizeDocPath(doc.file || '') === 'SKILL.md' ? 'semantic_anchor' : 'extraction_source'),
    sourceType: 'markdown',
    grounded,
    derived,
    requiresReview
  });
}

function inferObjectTargetType(objectText) {
  const text = String(objectText || '').toLowerCase();
  if (/\b(email|mail|message|chat|conversation)\b/.test(text)) return 'object';
  if (/\b(file|pdf|document|report|attachment)\b/.test(text)) return 'file';
  if (/\b(record|records|database|table|row)\b/.test(text)) return 'object';
  return 'object';
}

function stripMarkdownListMarker(line) {
  return String(line || '')
    .trim()
    .replace(/^[-*+]\s+/, '')
    .replace(/^\d+[.)]\s+/, '')
    .replace(/^\|\s*|\s*\|$/g, '')
    .trim();
}

// Recognizes the exact same list markers stripMarkdownListMarker handles, but
// reports the marker kind + leading indentation so the block segmenter can
// group items and their wrapped continuation lines.
const UNORDERED_MARKER_REGEX = /^(\s*)[-*+]\s+/;
const ORDERED_MARKER_REGEX = /^(\s*)\d+[.)]\s+/;

function detectListMarker(rawLine) {
  const line = String(rawLine || '');
  const ordered = line.match(ORDERED_MARKER_REGEX);
  if (ordered) return { listType: 'ordered', indent: ordered[1].length, markerLen: ordered[0].length };
  const unordered = line.match(UNORDERED_MARKER_REGEX);
  if (unordered) return { listType: 'unordered', indent: unordered[1].length, markerLen: unordered[0].length };
  return null;
}

// Part 1: block-level structure for prose/list. Pure, side-effect-free.
// Returns a per-line directive map keyed by 0-based line index. The main loop
// consults it so that:
//   - continuation lines of a multi-line bullet are folded into the bullet's
//     first line (mergedText), and the continuation lines themselves are skipped
//   - a list item inherits a disclaimer scope when its lead-in ("What this
//     skill does NOT do:") or enclosing section is a negation scope
// Physical lines that are not list items get no directive (undefined) and the
// main loop processes them exactly as before (byte-for-byte prose parity).
function segmentMarkdownBlocks(lines, sections) {
  const directives = new Map();
  const rows = Array.isArray(lines) ? lines : [];

  // Fence state so we never treat code-block interiors as prose/list.
  let inCode = false;
  // The most recent non-empty, non-list line — candidate list lead-in.
  let lastNonListText = '';
  let lastNonListLine = -1;
  // Disclaimer scope of the CURRENT contiguous list block. Set from the lead-in
  // when the first item is seen; carried to every item until the list ends
  // (blank line / heading / fence / table separator / prose line).
  let currentListScope = null;
  let inList = false;

  for (let idx = 0; idx < rows.length; idx++) {
    const raw = rows[idx];
    const trimmed = String(raw || '').trim();

    const fence = trimmed.match(/^```+/);
    if (fence) { inCode = !inCode; lastNonListText = ''; currentListScope = null; inList = false; continue; }
    if (inCode) continue;
    if (!trimmed) { lastNonListText = ''; currentListScope = null; inList = false; continue; } // blank ends list
    if (/^#{1,6}\s+/.test(trimmed)) { lastNonListText = ''; currentListScope = null; inList = false; continue; }
    if (/^\|?\s*[-:| ]+\|?\s*$/.test(trimmed)) { lastNonListText = ''; currentListScope = null; inList = false; continue; }

    const marker = detectListMarker(raw);
    if (!marker) {
      lastNonListText = trimmed;
      lastNonListLine = idx;
      currentListScope = null;
      inList = false;
      continue;
    }

    // First item of a new list block: compute the block's disclaimer scope from
    // the immediate lead-in line. STRONG disclaimer scope only when the lead-in
    // explicitly negates the whole list ("What this skill does NOT do:"). A
    // negation SECTION heading (e.g. "## Limitations") is handled separately and
    // softly inside classifyMarkdownLineRole (which keeps reverse protection for
    // imperative sinks), so it is deliberately NOT promoted to strong scope here.
    if (!inList) {
      // Strip markdown emphasis so a bold "**...NOT do:**" still reads as a lead-in.
      const leadClean = lastNonListText.replace(/[*_`]+/g, '').trim();
      const leadEndsColon = /[:：]\s*$/.test(leadClean);
      const leadInIsDisclaimer =
        lastNonListLine === idx - 1 &&
        (isNegatedActionText(leadClean) ||
          (leadEndsColon && NEGATION_HEADING_REGEX.test(leadClean)));
      currentListScope = leadInIsDisclaimer ? 'disclaimer' : null;
      inList = true;
    }
    const blockScope = currentListScope;

    // Fold continuation lines: subsequent non-empty lines that are NOT a new
    // list marker, heading, fence, table separator, and are indented deeper
    // than this marker's content column. Conservative: stop on anything
    // structural or a blank line.
    const parts = [String(raw)];
    let last = idx;
    for (let j = idx + 1; j < rows.length; j++) {
      const contRaw = rows[j];
      const contTrim = String(contRaw || '').trim();
      if (!contTrim) break;
      if (/^```+/.test(contTrim)) break;
      if (/^#{1,6}\s+/.test(contTrim)) break;
      if (/^\|?\s*[-:| ]+\|?\s*$/.test(contTrim)) break;
      if (detectListMarker(contRaw)) break;
      const contIndent = contRaw.match(/^(\s*)/)[1].length;
      if (contIndent < marker.indent + marker.markerLen) break; // not a wrapped continuation
      parts.push(contTrim);
      last = j;
    }

    const mergedText = parts
      .map((part, i) => (i === 0 ? String(part) : part))
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();

    directives.set(idx, { role: 'item_start', blockScope, listType: marker.listType, mergedText });
    for (let j = idx + 1; j <= last; j++) {
      directives.set(j, { role: 'continuation' });
    }
    idx = last; // advance past folded continuation lines

    // The list item itself is not a lead-in for a following list. Keep inList /
    // currentListScope so the rest of this contiguous list inherits the scope.
    lastNonListText = '';
    lastNonListLine = -1;
  }

  return directives;
}

function splitInstructionClauses(line) {
  const normalized = String(line || '')
    .replace(/\r/g, '')
    .trim();
  return normalized
    .split(SEMANTIC_CONNECTOR_REGEX)
    .map(part => part.trim().replace(/^,+|,+$/g, '').trim())
    .filter(Boolean);
}

function extractLineConditions(line) {
  const conditions = [];
  const seen = new Set();

  for (const regex of CONDITION_REGEXES) {
    regex.lastIndex = 0;
    let match;
    while ((match = regex.exec(line)) !== null) {
      const raw = String(match[0] || '').trim().replace(/[,:]+$/g, '');
      if (!raw || seen.has(raw.toLowerCase())) continue;
      seen.add(raw.toLowerCase());
      conditions.push({
        type: inferConditionKind(raw),
        text: raw
      });
    }
  }

  return conditions;
}

function inferConditionKind(conditionText) {
  const text = normalizeForSearch(conditionText);
  if (/fail|failed|error/.test(text)) return 'failure';
  if (/correct|wrong|reject|mistake/.test(text)) return 'user_correction';
  if (/periodic|recurring|weekly|daily|monthly|heartbeat/.test(text)) return 'periodic';
  if (/3x|3\+|repeated/.test(text)) return 'repetition';
  return 'condition';
}

function inferConditionOperationType(conditions) {
  const kinds = new Set((conditions || []).map(item => item.type));
  if (kinds.has('failure') || kinds.has('user_correction') || kinds.has('periodic')) {
    return 'trigger';
  }
  return 'condition';
}

function isActionableClause(clauseText) {
  const text = String(clauseText || '').trim().toLowerCase();
  if (!text) return false;
  if (extractFileRefsFromLine(text).length > 0) return true;
  if (ACTION_KEYWORDS.some(keyword => text.includes(String(keyword).toLowerCase()))) return true;
  return OPERATION_TYPE_DEFINITIONS.some(def =>
    def.keywords.some(keyword => text.includes(String(keyword).toLowerCase()))
  );
}

function isSemanticInstructionLine(line) {
  const text = normalizeForSearch(line);
  return OPERATION_TYPE_DEFINITIONS.some(def =>
    def.keywords.some(keyword => text.includes(normalizeForSearch(keyword)))
  );
}

// Defect (2) fix: negation detection. A clause under negation ("does not send",
// "cannot invoke", "never uploads") is a safety disclaimer, not a runtime
// action. Return guard so it does not become a false egress/invoke sink.
const NEGATION_LEAD_REGEX = /^(?:it\s+|this\s+skill\s+|the\s+skill\s+|we\s+|agent\s+)?(?:does not|doesn't|do not|don't|will not|won't|cannot|can't|never|no longer|must not|should not|shouldn't)\b/;
const NEGATION_HEADING_REGEX = /\b(?:does not do|not do|never|limitations?|out of scope|disclaimer|non-goals?|what (?:it|this|the skill) (?:does not|doesn't|will not|won't|cannot|can't))\b/i;

function isNegatedActionText(text) {
  const value = String(text || '').trim().toLowerCase();
  if (!value) return false;
  if (NEGATION_LEAD_REGEX.test(value)) return true;
  // "without sending / with no upload" style negation of an action.
  if (/\bwithout\s+(?:\w+ing|any|real|sending|uploading|storing|writing)\b/.test(value)) return true;
  return false;
}

function isNegationScopeHeading(section) {
  return NEGATION_HEADING_REGEX.test(String(section || ''));
}

function inferOperationType(text) {
  const normalized = normalizeForSearch(text);
  // Negation guard: check before positive keyword matching so disclaimers like
  // "Does not send any personal data externally" never resolve to egress.
  if (isNegatedActionText(text)) {
    return 'guard';
  }
  const startsWithWriteVerb = /^(?:write|save|store|persist|export)\b/.test(normalized);
  const startsWithProduceVerb = /^(?:generate|create|produce|output|build|compose|draft)\b/.test(normalized);

  if (/\b(review|reflect|heartbeat|periodic|recurring)\b/.test(normalized)) {
    return 'review';
  }
  if (/\b(read|get|fetch|retrieve|load|search|query|open|inspect)\b/.test(normalized)) {
    return 'read';
  }
  if (/\b(send|provide|pass|route|forward)\b[\s\S]{0,80}\b(model|llm|chat|completion|gpt|claude|gemini|openai|anthropic)\b/.test(normalized)) {
    return 'model_inference';
  }
  if (/\b(webhook|http|https|external|third party|third-party|post|upload|publish|share)\b/.test(normalized) ||
      /\b(call|invoke|send)\b[\s\S]{0,80}\b(api|endpoint|service|weather api)\b/.test(normalized)) {
    return 'external_egress';
  }
  if (startsWithWriteVerb) {
    return 'write';
  }
  if (startsWithProduceVerb) {
    return 'produce_artifact';
  }
  if (/\b(redact|mask|sanitize|scrub|strip|remove)\b[\s\S]{0,80}\b(secret|secrets|credential|credentials|api key|token|password|pii|email|phone|address)\b/.test(normalized)) {
    return 'transform';
  }
  if (/\b(summarize|summary|digest|brief|classify|extract|parse|analyze)\b/.test(normalized)) {
    return 'transform';
  }
  if (/\b(save|store|write|persist|export)\b/.test(normalized)) {
    return 'write';
  }
  for (const definition of OPERATION_TYPE_DEFINITIONS) {
    if (definition.keywords.some(keyword => normalized.includes(normalizeForSearch(keyword)))) {
      return definition.type;
    }
  }
  return 'read';
}

function extractOperationTargets(clauseText, ownerDoc, docIndex) {
  const targets = [];
  const fileRefs = [];

  for (const refInfo of extractFileRefsFromLine(clauseText)) {
    const resolved = resolveDocReference(refInfo.ref, ownerDoc, docIndex);
    fileRefs.push(resolved);
    targets.push({
      type: 'file',
      value: resolved,
      raw: refInfo.ref
    });
  }

  for (const toolName of extractToolRefsFromLine(clauseText)) {
    targets.push({
      type: 'tool',
      value: toolName,
      raw: toolName
    });
  }

  for (const tier of extractMemoryTiers(clauseText)) {
    targets.push({
      type: 'memory_tier',
      value: tier,
      raw: tier
    });
  }

  for (const semanticTarget of extractSemanticTargets(clauseText)) {
    targets.push(semanticTarget);
  }

  const primary = targets.find(target => target.type === 'file') || targets[0];
  return {
    targets: dedupeTargets(targets.length > 0 ? targets : [{ type: 'document', value: ownerDoc, raw: ownerDoc }]),
    fileRefs: Array.from(new Set(fileRefs.map(normalizeDocPath))),
    primaryTarget: primary ? semanticTargetRef(ownerDoc, primary.value) : ownerDoc
  };
}

function extractToolRefsFromLine(line) {
  const refs = [];
  const regex = /`?([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)`?/g;
  let match;
  while ((match = regex.exec(line)) !== null) {
    const value = match[1];
    if (/\.md$/i.test(value)) continue;
    refs.push(value);
  }
  return Array.from(new Set(refs));
}

function extractMemoryTiers(line) {
  const tiers = [];
  const lower = String(line || '').toLowerCase();
  if (/\bhot\b/.test(lower)) tiers.push('HOT');
  if (/\bwarm\b/.test(lower)) tiers.push('WARM');
  if (/\bcold\b/.test(lower)) tiers.push('COLD');
  return tiers;
}

function extractSemanticTargets(line) {
  const text = String(line || '');
  const lower = text.toLowerCase();
  const targets = [];

  if (/memory/.test(lower)) targets.push({ type: 'memory', value: 'memory', raw: 'memory' });
  if (/log/.test(lower)) targets.push({ type: 'artifact', value: 'logs', raw: 'logs' });
  if (/correction/.test(lower)) targets.push({ type: 'artifact', value: 'corrections', raw: 'corrections' });
  if (/report/.test(lower)) targets.push({ type: 'artifact', value: 'report', raw: 'report' });
  if (/note|notes/.test(lower)) targets.push({ type: 'artifact', value: 'notes', raw: 'notes' });

  return targets;
}

function dedupeTargets(targets) {
  const seen = new Set();
  const result = [];
  for (const target of targets || []) {
    const key = `${target.type}:${target.value}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(target);
  }
  return result;
}

function semanticTargetRef(ownerDoc, value) {
  const normalized = normalizeDocPath(value || '');
  if (!normalized) return ownerDoc;
  if (/\.md$/i.test(normalized) || normalized.includes('/')) return normalized;
  const slug = fileSlug(normalized);
  return `semantic/${slug && slug !== 'doc' ? slug : stableSlug(normalized)}`;
}

function stableSlug(value) {
  const text = String(value || '');
  const ascii = text
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
  if (ascii) return ascii;

  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
  }
  return `target_${Math.abs(hash).toString(36)}`;
}

function buildFormalSemantics(config) {
  const operationType = config.operationType || 'read';
  const action = config.action || OPERATION_DOC_ACTION[operationType] || 'read';
  const targets = dedupeTargets(config.targets || []);
  const effects = OPERATION_EFFECTS[operationType] || [];

  return {
    operation_type: operationType,
    actor: 'llm',
    inputs: buildFormalInputs(operationType, targets, config.conditions),
    outputs: buildFormalOutputs(operationType, targets),
    targets,
    conditions: config.conditions || [],
    effects,
    confidence: calculateSemanticConfidence(operationType, targets, config.conditions),
    evidence: {
      text: config.clauseText || config.instructionText || '',
      source_line: config.instructionText || '',
      file: normalizeDocPath(config.ownerDoc),
      line: Number(config.line || 0),
      section: config.section || '',
      method: 'rule'
    },
    action
  };
}

function buildFormalInputs(operationType, targets, conditions) {
  const inputs = [];
  if ((conditions || []).length > 0) {
    inputs.push({ name: 'condition_signal', type: 'condition' });
  }
  if (['write', 'transform', 'produce_artifact', 'verify', 'decision', 'guard'].includes(operationType)) {
    inputs.push({ name: 'llm_context', type: 'context' });
  }
  for (const target of targets || []) {
    if (['read', 'review', 'verify'].includes(operationType)) {
      inputs.push({ name: target.value, type: target.type });
    }
  }
  return inputs;
}

function buildFormalOutputs(operationType, targets) {
  if (operationType === 'read' || operationType === 'review' || operationType === 'verify') {
    return [{ name: 'context', type: 'string' }];
  }
  if (operationType === 'decision' || operationType === 'condition' || operationType === 'trigger' || operationType === 'guard') {
    return [{ name: 'branch_state', type: 'object' }];
  }
  if (operationType === 'invoke_tool') {
    return [{ name: 'tool_result', type: 'object' }];
  }
  return (targets || []).map(target => ({ name: target.value, type: target.type || 'artifact' }));
}

function calculateSemanticConfidence(operationType, targets, conditions) {
  let confidence = 0.55;
  if (operationType && operationType !== 'read') confidence += 0.1;
  if ((targets || []).length > 0) confidence += 0.15;
  if ((conditions || []).length > 0) confidence += 0.1;
  return Math.min(0.95, confidence);
}

function dedupeSemanticOperations(operations) {
  const seen = new Set();
  const result = [];
  for (const operation of operations || []) {
    const targetKey = operation.formalSemantics?.targets
      ?.map(target => `${target.type}:${target.value}`)
      .join('|') || operation.targetDoc;
    const key = `${operation.operationType}:${operation.action}:${operation.targetDoc}:${targetKey}:${operation.sourceLine}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(operation);
  }
  return result;
}

function mergeFormalSemantics(group, operationType, action, targetDoc, instructionPreview) {
  const semantics = (group.members || [])
    .map(member => member.formal_semantics)
    .filter(Boolean);

  if (semantics.length === 0) {
    return createFallbackFormalSemantics({
      operationType,
      action,
      ownerDoc: group.ownerDoc,
      line: group.startLine,
      section: group.section,
      instructionText: instructionPreview,
      targetDoc
    });
  }

  const first = semantics[0];
  return {
    ...first,
    operation_type: operationType,
    action,
    targets: dedupeTargets(semantics.flatMap(item => item.targets || [])),
    conditions: dedupeConditions(semantics.flatMap(item => item.conditions || [])),
    effects: Array.from(new Set(semantics.flatMap(item => item.effects || []))),
    inputs: dedupeNamedItems(semantics.flatMap(item => item.inputs || [])),
    outputs: dedupeNamedItems(semantics.flatMap(item => item.outputs || [])),
    confidence: Math.max(...semantics.map(item => Number(item.confidence || 0.5))),
    evidence: {
      ...first.evidence,
      text: instructionPreview || first.evidence?.text || '',
      source_line: instructionPreview || first.evidence?.source_line || '',
      line: Number(group.startLine || first.evidence?.line || 0),
      method: 'rule_merge',
      member_count: group.members.length
    }
  };
}

function createFallbackFormalSemantics(config) {
  return buildFormalSemantics({
    operationType: config.operationType || 'read',
    action: config.action || 'read',
    ownerDoc: config.ownerDoc,
    line: config.line,
    section: config.section,
    instructionText: config.instructionText,
    clauseText: config.instructionText,
    targets: [{ type: 'document', value: config.targetDoc || config.ownerDoc, raw: config.targetDoc || config.ownerDoc }],
    conditions: []
  });
}

function dedupeConditions(conditions) {
  const seen = new Set();
  const result = [];
  for (const condition of conditions || []) {
    const key = `${condition.type}:${condition.text}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(condition);
  }
  return result;
}

function dedupeNamedItems(items) {
  const seen = new Set();
  const result = [];
  for (const item of items || []) {
    const key = `${item.name}:${item.type}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(item);
  }
  return result;
}

function buildStepInput(action, targetDoc) {
  const base = {
    file_path: { type: 'string', required: false, example: targetDoc }
  };
  if (action === 'write') {
    base.content = { type: 'string', required: true };
    return base;
  }
  if (action === 'run') {
    base.instruction = { type: 'string', required: true };
    return base;
  }
  if (['condition', 'decision', 'guard', 'transform', 'verify', 'review'].includes(action)) {
    base.context = { type: 'string', required: false };
    return base;
  }
  base.context = { type: 'string', required: false };
  return base;
}

function buildStepOutput(action) {
  if (action === 'write') {
    return { success: { type: 'boolean' } };
  }
  if (action === 'run') {
    return {
      success: { type: 'boolean' },
      result: { type: 'string' }
    };
  }
  if (action === 'condition' || action === 'decision' || action === 'guard') {
    return {
      branch_state: { type: 'object' },
      success: { type: 'boolean' }
    };
  }
  if (action === 'transform') {
    return {
      result: { type: 'string' },
      success: { type: 'boolean' }
    };
  }
  return {
    content: { type: 'string' },
    success: { type: 'boolean' }
  };
}

function edgeSourceContextFromNode(node = {}, method = '') {
  if (!node.source_context) return undefined;
  return {
    ...node.source_context,
    edge_evidence_method: method
  };
}

function addStepPrimaryEdges(edges, stepNode) {
  if (!isActionFlowNode(stepNode)) return;
  const action = stepNode.docAction || stepNode.action || 'read';

  if (action === 'write') {
    edges.push({
      source: 'llm.inference',
      target: stepNode.name,
      type: 'doc_instruction',
      confidence: 0.74,
      validation_method: 'doc_flow',
      data_flow: {
        from_param: 'response',
        to_param: 'content',
        data_type: 'string'
      },
      semantic_reason: `LLM persists knowledge update via step in ${stepNode.ownerDoc}`,
      source_context: edgeSourceContextFromNode(stepNode, 'doc_flow')
    });
    return;
  }

  if (action === 'run') {
    edges.push({
      source: 'llm.inference',
      target: stepNode.name,
      type: 'doc_instruction',
      confidence: 0.69,
      validation_method: 'doc_flow',
      data_flow: {
        from_param: 'response',
        to_param: 'instruction',
        data_type: 'string'
      },
      semantic_reason: `LLM executes procedural markdown step in ${stepNode.ownerDoc}`,
      source_context: edgeSourceContextFromNode(stepNode, 'doc_flow')
    });
    edges.push({
      source: stepNode.name,
      target: 'llm.inference',
      type: 'doc_instruction',
      confidence: 0.52,
      validation_method: 'doc_flow',
      data_flow: {
        from_param: 'result',
        to_param: 'context',
        data_type: 'string'
      },
      semantic_reason: `Execution result from markdown step feeds back to LLM`,
      source_context: edgeSourceContextFromNode(stepNode, 'doc_flow')
    });
    return;
  }

  edges.push({
    source: 'user.query',
    target: stepNode.name,
    type: 'doc_instruction',
    confidence: 0.44,
    validation_method: 'doc_flow',
    data_flow: {
      from_param: 'query_text',
      to_param: 'file_path',
      data_type: 'string'
    },
    semantic_reason: `User request activates markdown step in ${stepNode.ownerDoc}`,
    source_context: edgeSourceContextFromNode(stepNode, 'doc_flow')
  });
  edges.push({
    source: stepNode.name,
    target: 'llm.inference',
    type: 'doc_instruction',
    confidence: 0.66,
    validation_method: 'doc_flow',
    data_flow: {
      from_param: 'content',
      to_param: 'skill_content',
      data_type: 'string'
    },
    semantic_reason: `Step output from ${stepNode.ownerDoc} becomes LLM context`,
    source_context: edgeSourceContextFromNode(stepNode, 'doc_flow')
  });
}

function isActionFlowNode(node = {}) {
  return Boolean(node && ['doc_step', 'doc_operation'].includes(node.semanticKind) && !node.excludeFromFlow);
}

function isContextOnlyNode(node = {}) {
  return Boolean(
    node &&
    (node.excludeFromFlow ||
      ['doc_definition', 'doc_schema', 'doc_example', 'doc_template', 'doc_discard', 'doc_review_error'].includes(node.semanticKind))
  );
}

// Part 3: sequence-edge scope. These control_flow edges are pure-order (state>
// state placeholder) — the router already routes them as `may_route`/order_only
// and they account for the bulk of "flooding along document order". Default is
// SAME-SECTION linking: only consecutive steps under the same markdown section
// heading are chained, which removes cross-section flooding while keeping the
// intra-section step order that real procedures rely on. Genuine cross-section
// data carriage is unaffected — it rides addObjectProducerEdges (data_dependency)
// and type-analyzer candidates, both independent of these order edges.
// Set FCG_SEQUENCE_EDGE_SCOPE=global to restore the legacy global linking (used
// for A/B comparison and as a trivial revert switch).
function sequenceEdgeScope() {
  const raw = String(process.env.FCG_SEQUENCE_EDGE_SCOPE || '').trim().toLowerCase();
  return raw === 'global' ? 'global' : 'section';
}

function addStepSequenceEdges(edges, docFile, steps) {
  const scope = sequenceEdgeScope();
  for (let i = 0; i < steps.length - 1; i++) {
    const current = steps[i];
    const next = steps[i + 1];
    if (!current?.name || !next?.name) continue;

    // Same-section gate (default). Steps are already in document order within a
    // doc, so comparing the enclosing section of adjacent steps is sufficient to
    // keep intra-section chains and drop cross-section flooding edges.
    if (scope === 'section') {
      const curSection = String(current.location?.section || '');
      const nextSection = String(next.location?.section || '');
      if (curSection !== nextSection) continue;
    }

    edges.push({
      source: current.name,
      target: next.name,
      type: 'control_flow',
      confidence: 0.51,
      validation_method: 'doc_flow',
      data_flow: {
        from_param: 'state',
        to_param: 'state',
        data_type: 'object'
      },
      semantic_reason: `Sequential markdown steps in ${docFile}`,
      source_context: edgeSourceContextFromNode(current, 'doc_flow_sequence')
    });
  }
}

function addObjectProducerEdges(edges, docFile, steps) {
  for (const step of steps || []) {
    if (!step?.objectProducer || !step?.name || step.objectProducer === step.name) continue;
    edges.push({
      source: step.objectProducer,
      target: step.name,
      type: 'data_dependency',
      confidence: 0.68,
      validation_method: 'doc_flow_object_context',
      data_flow: {
        from_param: 'content',
        to_param: 'context',
        data_type: 'string'
      },
      semantic_reason: `Object context reuse for ${step.objectKey || 'data object'} in ${docFile}`,
      source_context: edgeSourceContextFromNode(step, 'doc_flow_object_context')
    });
  }
}

function buildDocumentSet(skillData, readmeData) {
  const mdFiles = findMarkdownFiles(skillData.skillRootDir);
  const docs = [];
  for (const mdFile of mdFiles) {
    const relPath = normalizeDocPath(path.relative(skillData.skillRootDir, mdFile));
    const base = path.basename(relPath).toLowerCase();
    if (base === 'skill.md' || base === 'readme.md') continue;
    const content = fs.readFileSync(mdFile, 'utf-8');
    docs.push({
      file: relPath,
      content,
      sections: extractSections(content)
    });
  }

  if (docs.length === 0) {
    docs.push({
      file: 'SKILL.md',
      content: skillData.content,
      sections: skillData.sections || []
    });
  }

  return dedupeDocs(docs);
}

function dedupeDocs(docs) {
  const byFile = new Map();
  for (const doc of docs) {
    const file = normalizeDocPath(doc.file);
    if (!byFile.has(file)) {
      byFile.set(file, { ...doc, file });
      continue;
    }

    // Prefer parsed SKILL/README over recursively discovered copies.
    const existing = byFile.get(file);
    if ((existing.content || '').length >= (doc.content || '').length) continue;
    byFile.set(file, { ...doc, file });
  }
  return Array.from(byFile.values());
}

function buildDocIndex(docs) {
  const byCanonical = new Map();
  const byBasename = new Map();

  for (const doc of docs) {
    const canonical = normalizeDocPath(doc.file);
    byCanonical.set(canonical.toLowerCase(), canonical);

    const base = path.posix.basename(canonical).toLowerCase();
    if (!byBasename.has(base)) byBasename.set(base, []);
    byBasename.get(base).push(canonical);
  }

  return { byCanonical, byBasename };
}

function resolveDocReference(rawRef, ownerDoc, docIndex) {
  const direct = normalizeDocPath(rawRef);
  const directKey = direct.toLowerCase();
  if (docIndex.byCanonical.has(directKey)) {
    return docIndex.byCanonical.get(directKey);
  }

  const ownerDir = normalizeDocPath(path.posix.dirname(normalizeDocPath(ownerDoc)));
  const relative = normalizeDocPath(path.posix.normalize(path.posix.join(ownerDir, direct)));
  const relativeKey = relative.toLowerCase();
  if (docIndex.byCanonical.has(relativeKey)) {
    return docIndex.byCanonical.get(relativeKey);
  }

  const base = path.posix.basename(direct).toLowerCase();
  const byName = docIndex.byBasename.get(base) || [];
  if (byName.length > 0) {
    return byName[0];
  }

  return direct || rawRef;
}

function findMarkdownFiles(rootDir) {
  const result = [];
  const ignoredDirs = new Set(['node_modules', '.git', '.svn', '.hg', 'dist', 'build', 'coverage']);

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (ignoredDirs.has(entry.name)) continue;
        walk(fullPath);
      } else if (entry.name.toLowerCase().endsWith('.md')) {
        result.push(fullPath);
      }
    }
  }

  walk(rootDir);
  return result;
}

function extractFileRefsFromLine(line) {
  const refs = [];
  const seen = new Set();

  BACKTICK_FILE_REF_REGEX.lastIndex = 0;
  let match;
  while ((match = BACKTICK_FILE_REF_REGEX.exec(line)) !== null) {
    const ref = normalizeDocPath(match[1]);
    if (!ref || seen.has(ref)) continue;
    seen.add(ref);
    refs.push({
      ref,
      index: match.index
    });
  }

  PLAIN_FILE_REF_REGEX.lastIndex = 0;
  while ((match = PLAIN_FILE_REF_REGEX.exec(line)) !== null) {
    const ref = normalizeDocPath(match[1]);
    if (!ref || seen.has(ref)) continue;
    seen.add(ref);
    refs.push({
      ref,
      index: match.index
    });
  }

  return refs;
}

function inferActionFromLine(line, refIndex = -1) {
  const lower = String(line || '').toLowerCase();
  if (/\b(read|get|fetch|retrieve|load|search|query|open|inspect)\b/.test(lower)) return 'read';
  if (/\b(save|store|write|persist|export|record)\b/.test(lower)) return 'write';
  if (/\b(send|post|upload|call|invoke)\b/.test(lower)) return 'run';
  if (refIndex >= 0) {
    const before = lower.slice(Math.max(0, refIndex - 100), refIndex);
    if (WRITE_KEYWORDS.some(keyword => before.includes(keyword))) return 'write';
    if (RUN_KEYWORDS.some(keyword => before.includes(keyword))) return 'run';
    if (READ_KEYWORDS.some(keyword => before.includes(keyword))) return 'read';
  }

  if (WRITE_KEYWORDS.some(keyword => lower.includes(keyword))) return 'write';
  if (RUN_KEYWORDS.some(keyword => lower.includes(keyword))) return 'run';
  if (READ_KEYWORDS.some(keyword => lower.includes(keyword))) return 'read';
  return 'read';
}

function isActionableInstructionLine(trimmedLine) {
  const text = String(trimmedLine || '').trim().toLowerCase();
  if (!text) return false;
  if (text.length < 3) return false;
  if (/^>\s*/.test(text)) return false;

  if (/^([-*+]|\d+[.)])\s+/.test(text)) return true;
  if (ACTION_KEYWORDS.some(keyword => text.includes(keyword))) return true;
  if (/^(then|after|before|finally|next)\b/.test(text)) return true;
  return false;
}

function normalizeDocPath(fileRef) {
  return String(fileRef || '')
    .trim()
    .replace(/^['"`\s]+|['"`\s]+$/g, '')
    .replace(/[),.;:!?]+$/g, '')
    .replace(/\\/g, '/')
    .replace(/^\.\/+/, '')
    .replace(/\/+/g, '/');
}

function fileSlug(docPath) {
  return normalizeDocPath(docPath)
    .replace(/\.[^.]+$/, '')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase() || 'doc';
}

function dedupeNodes(nodes) {
  const byName = new Map();
  for (const node of nodes) {
    if (!node?.name) continue;
    if (!byName.has(node.name)) {
      byName.set(node.name, node);
      continue;
    }

    const existing = byName.get(node.name);
    byName.set(node.name, mergeNodes(existing, node));
  }
  return Array.from(byName.values());
}

function mergeNodes(a, b) {
  const mergedActions = new Set([...(a.docActions || []), ...(b.docActions || [])]);
  const mergedRefs = new Set([...(a.stepRefs || []), ...(b.stepRefs || [])]);
  return {
    ...a,
    ...b,
    description: (b.description && b.description.length > (a.description || '').length) ? b.description : a.description,
    input: { ...(a.input || {}), ...(b.input || {}) },
    output: { ...(a.output || {}), ...(b.output || {}) },
    docActions: mergedActions.size ? Array.from(mergedActions).sort() : undefined,
    stepRefs: mergedRefs.size ? Array.from(mergedRefs).sort() : [],
    location: preferLocation(a.location, b.location),
    excludeFromTypeAnalysis: Boolean(a.excludeFromTypeAnalysis || b.excludeFromTypeAnalysis),
    excludeFromImplicitLlmEdge: Boolean(a.excludeFromImplicitLlmEdge || b.excludeFromImplicitLlmEdge)
  };
}

function preferLocation(a = {}, b = {}) {
  if (!a.file) return b;
  if (!b.file) return a;
  if (a.file === 'SKILL.md' && b.file !== 'SKILL.md') return a;
  if (b.file === 'SKILL.md' && a.file !== 'SKILL.md') return b;
  return (a.line || Number.MAX_SAFE_INTEGER) <= (b.line || Number.MAX_SAFE_INTEGER) ? a : b;
}

function dedupeEdges(edges) {
  const map = new Map();
  for (const edge of edges) {
    const fromParam = String(edge?.data_flow?.from_param || '');
    const toParam = String(edge?.data_flow?.to_param || '');
    const key = `${edge.source}->${edge.target}:${edge.type}:${edge.validation_method || ''}:${fromParam}->${toParam}`;
    if (!map.has(key)) {
      map.set(key, edge);
      continue;
    }

    const existing = map.get(key);
    if ((edge.confidence || 0) > (existing.confidence || 0)) {
      map.set(key, edge);
    }
  }
  return Array.from(map.values());
}

function extractSections(content) {
  const lines = content.split('\n');
  const sections = [];
  let currentSection = null;
  let currentContent = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      if (currentSection) {
        sections.push({
          ...currentSection,
          content: currentContent.join('\n'),
          endLine: i
        });
      }
      currentSection = {
        title: headingMatch[2].trim(),
        level: headingMatch[1].length,
        startLine: i + 1
      };
      currentContent = [];
    } else if (currentSection) {
      currentContent.push(line);
    }
  }

  if (currentSection) {
    sections.push({
      ...currentSection,
      content: currentContent.join('\n'),
      endLine: lines.length
    });
  }

  return sections;
}

function findSectionForLine(sections, line) {
  for (const section of sections || []) {
    if (line >= section.startLine && line <= section.endLine) {
      return section.title;
    }
  }
  return '';
}

function normalizeForSearch(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizePositiveInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

module.exports = {
  extractDocumentFlow,
  // Global two-phase constraint resolution. Called by the pipeline (index.js)
  // AFTER all node sources (tool-call, script, doc-flow, mediation) are merged,
  // so ordering-constraint endpoints match the full node set before synthesis.
  resolvePendingConstraints,
  // Exported for unit testing the token-usage accounting; not part of the
  // public extraction API.
  newSemanticGateUsage,
  accumulateSemanticGateUsage,
  summarizeSemanticGateUsage
};





