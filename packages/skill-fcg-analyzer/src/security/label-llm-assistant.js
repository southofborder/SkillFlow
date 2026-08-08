const fs = require('fs');
const path = require('path');
const {
  parseLooseJson,
  postJsonWithTimeout,
  normalizeScaledNumber
} = require('../../../../shared/llm-utils.cjs');
const {
  createLabel,
  maxSensitivity,
  shortHash
} = require('./data-labeler');
const {
  getAllowedLlmLabelMap,
  getOntologyVersion,
  getOntologyStats,
  listAllowedLlmLabels
} = require('./label-ontology');

const ONTOLOGY_VERSION = getOntologyVersion();
const ALLOWED_LABELS = getAllowedLlmLabelMap();
const AMBIGUOUS_FIELD_PATTERN = /\b(payload|data|content|result|metadata|value|body|response|output|input|object|record|item|info|details)\b/i;

async function applyLlmLabelAssistToProfiles(profiles = [], nodes = [], edges = [], options = {}) {
  const stats = createStats(Boolean(options.enabled));
  if (!options.enabled) return { profiles, statistics: stats };
  if (!String(options.apiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required when --label-llm-assist is enabled');
  }

  const nodesById = new Map((nodes || []).map(node => [node.id, node]));
  const edgeContextByNode = buildEdgeContext(edges);
  const cache = loadCache(options.cachePath);
  const candidates = profiles
    .map(profile => ({ profile, reason: shouldAssistProfile(profile) }))
    .filter(item => item.reason.shouldAssist);

  stats.label_llm_candidate_count = candidates.length;
  const concurrency = normalizePositiveInteger(options.concurrency, 2);
  let cursor = 0;

  const workers = Array.from({ length: Math.min(concurrency, candidates.length || 1) }, async () => {
    while (cursor < candidates.length) {
      const current = candidates[cursor++];
      await reviewOneProfile(current.profile, current.reason, {
        nodesById,
        edgeContextByNode,
        cache,
        options,
        stats
      });
    }
  });

  await Promise.all(workers);
  saveCache(options.cachePath, cache);
  return { profiles, statistics: stats };
}

async function reviewOneProfile(profile, reason, context) {
  const { nodesById, edgeContextByNode, cache, options, stats } = context;
  const node = nodesById.get(profile.node_id) || {};
  const cacheKey = buildCacheKey(profile, node, options.model);
  let response = cache.get(cacheKey);
  const cacheHit = Boolean(response);
  if (cacheHit) {
    stats.label_llm_cache_hit_count += 1;
  } else {
    try {
      const prompt = buildPrompt(profile, node, edgeContextByNode.get(profile.node_id) || []);
      response = typeof options.labelAssistant === 'function'
        ? await options.labelAssistant({ profile, node, reason, prompt, options })
        : await callLabelAssistant(prompt, options);
      cache.set(cacheKey, response);
    } catch (error) {
      stats.label_llm_error_count += 1;
      attachAssistError(profile, error.message);
      return;
    }
  }

  const normalized = normalizeAssistantLabels(response, { profile, node, reason, model: options.model });
  stats.label_llm_ignored_count += normalized.ignored.length;
  if (normalized.errors.length > 0) {
    profile.data_profile.label_llm_assist_errors = [
      ...(profile.data_profile.label_llm_assist_errors || []),
      ...normalized.errors
    ];
  }

  const deterministicLabels = profile.data_profile?.labels || [];
  const hasExplicitDeterministic = deterministicLabels.some(label => !isFallbackLabel(label));
  const existingKeys = new Set(deterministicLabels.map(label => label.label));
  const accepted = [];
  const reviewEvidence = [];
  for (const label of normalized.labels) {
    if (existingKeys.has(label.label) || (isFallbackLabel(label) && hasExplicitDeterministic)) {
      reviewEvidence.push({
        label: label.label,
        reason: label.reason || label.llm_review?.reason || 'LLM supported existing deterministic label',
        model: options.model || '',
        ontology_version: ONTOLOGY_VERSION,
        fallback_suppressed: Boolean(isFallbackLabel(label) && hasExplicitDeterministic)
      });
      continue;
    }
    accepted.push(label);
    existingKeys.add(label.label);
  }

  if (accepted.length > 0) {
    profile.data_profile.labels.push(...accepted);
    profile.data_profile.primary_category = choosePrimaryCategory(profile.data_profile.labels);
    profile.data_profile.sensitivity = maxSensitivity(profile.data_profile.labels);
    profile.data_profile.unknown_tail = true;
    stats.label_llm_accepted_count += accepted.length;
  }
  if (reviewEvidence.length > 0) {
    profile.data_profile.review_evidence = [
      ...(profile.data_profile.review_evidence || []),
      ...reviewEvidence
    ];
  }
  profile.data_profile.label_llm_assist = {
    enabled: true,
    triggered: true,
    trigger_reasons: reason.reasons,
    accepted_count: accepted.length,
    ignored_count: normalized.ignored.length,
    cache_key: cacheKey,
    cache_hit: cacheHit,
    ontology_version: ONTOLOGY_VERSION
  };
}

function shouldAssistProfile(profile = {}) {
  const reasons = [];
  const labels = profile.data_profile?.labels || [];
  if (!profile.node_roles?.includes('data_introduction')) return { shouldAssist: false, reasons };
  if (labels.length === 0) reasons.push('no_deterministic_labels');
  if (labels.length === 1 && labels[0].label === 'generic_data.data') reasons.push('generic_only');
  if (profile.data_profile?.unknown_tail) reasons.push('unknown_tail');
  const highestEvidence = Math.max(...labels.map(label => evidenceRank(label.evidence_level)), -1);
  if (highestEvidence >= 0 && highestEvidence < evidenceRank('L2')) reasons.push('low_evidence_level');
  if (hasAmbiguousFields(profile)) reasons.push('ambiguous_field_name');
  return { shouldAssist: reasons.length > 0, reasons };
}

function hasAmbiguousFields(profile = {}) {
  const text = [
    profile.node_name,
    ...(profile.data_profile?.labels || []).flatMap(label => [label.field_name, label.field_path, label.evidence_text]),
    ...(profile.evidence || []).map(item => item.text)
  ].filter(Boolean).join(' ');
  return AMBIGUOUS_FIELD_PATTERN.test(text);
}

async function callLabelAssistant(prompt, options = {}) {
  const endpoint = resolveEndpoint(options);
  const payload = await postJsonWithTimeout(endpoint, {
    model: options.model || 'gpt-5.5',
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: 'You assist low-confidence data label classification. Return strict JSON only. You may only choose labels from the provided closed ontology. If uncertain, return an empty labels array or generic_data.data.'
      },
      { role: 'user', content: prompt }
    ]
  }, {
    timeoutMs: options.timeout || 180000,
    headers: { Authorization: `Bearer ${options.apiKey}` }
  });
  return payload?.choices?.[0]?.message?.content || payload;
}

function buildPrompt(profile, node, edgeContext) {
  return JSON.stringify({
    task: 'Suggest candidate data labels only for low-confidence deterministic labeling. Do not invent labels outside ontology.',
    ontology_version: ONTOLOGY_VERSION,
    ontology: listAllowedLlmLabels(),
    response_schema: {
      labels: [{
        label: 'one ontology label',
        category: 'category from ontology',
        subtype: 'subtype from ontology',
        field_name: 'field or empty',
        evidence_text: 'short direct evidence from input',
        reason: 'why this label may apply',
        confidence: '0..1',
        uncertainty: 'what is uncertain'
      }]
    },
    node: {
      id: node.id || profile.node_id,
      name: node.name || profile.node_name,
      description: node.description || '',
      input: node.signature?.input || node.input || {},
      output: node.signature?.output || node.output || {},
      formal_semantics: node.formal_semantics || {},
      instructionText: node.instructionText || '',
      docAction: node.docAction || '',
      docActions: node.docActions || []
    },
    deterministic_profile: {
      node_roles: profile.node_roles || [],
      security_tags: profile.security_tags || [],
      operation_tags: profile.operation_tags || [],
      data_profile: profile.data_profile || {},
      evidence: profile.evidence || []
    },
    adjacent_edges: edgeContext
  }, null, 2);
}

function normalizeAssistantLabels(raw, context) {
  const parsed = parseLooseJson(raw);
  const source = parsed && Array.isArray(parsed.labels) ? parsed.labels : [];
  const labels = [];
  const ignored = [];
  const errors = [];

  if (!parsed) {
    errors.push({ type: 'parse_failed', message: 'Unable to parse LLM label JSON' });
    return { labels, ignored, errors };
  }

  for (const candidate of source) {
    const normalized = normalizeCandidate(candidate, context);
    if (normalized.ignored) {
      ignored.push(normalized.ignored);
      continue;
    }
    labels.push(normalized.label);
  }
  return { labels, ignored, errors };
}

function normalizeCandidate(candidate = {}, context) {
  const rawLabel = String(candidate.label || `${candidate.category || ''}.${candidate.subtype || ''}`).trim();
  const ontology = ALLOWED_LABELS.get(rawLabel);
  if (!ontology) {
    return { ignored: { reason: 'unknown_or_disallowed_ontology_label', label: rawLabel } };
  }
  const cap = confidenceCap(context.node, candidate);
  const confidence = Math.min(cap, normalizeScaledNumber(candidate.confidence, { fallback: 0.45 }));
  const evidenceLevel = cap >= 0.75 ? 'L2' : 'L1';
  const originNode = context.profile.node_id;
  const originNodeName = context.profile.node_name || originNode;
  const reason = String(candidate.reason || '').trim();
  const uncertainty = String(candidate.uncertainty || '').trim();
  const evidenceText = String(candidate.evidence_text || candidate.evidence || reason || context.profile.node_name || '').slice(0, 300);

  return {
    label: createLabel({
      category: ontology.category,
      subtype: ontology.subtype,
      fieldName: candidate.field_name || ontology.subtype,
      fieldPath: candidate.field_path || '',
      originNode,
      originNodeName,
      introducedAt: originNode,
      mode: 'llm_assisted',
      confidence,
      evidenceLevel,
      evidenceKind: 'llm_low_confidence_assist',
      evidenceText,
      requiresReview: true,
      uncertainty,
      reason,
      ontologyVersion: ONTOLOGY_VERSION,
      ontologyLabelId: ontology.label,
      llmReview: {
        model: context.model || '',
        reason,
        uncertainty,
        ontology_version: ONTOLOGY_VERSION
      }
    })
  };
}

function isFallbackLabel(label = {}) {
  return label.label === 'generic_data.data' || label.label === 'unknown_sensitive.data' || Boolean(label.fallback);
}

function confidenceCap(node = {}, candidate = {}) {
  const evidenceText = [candidate.field_name, candidate.evidence_text, candidate.reason].filter(Boolean).join(' ');
  const hasFormal = Array.isArray(node.formal_semantics?.targets) && node.formal_semantics.targets.length > 0;
  const hasInstruction = Boolean(node.instructionText || node.formal_semantics?.evidence?.text);
  if (hasFormal || hasInstruction) return 0.75;
  if (candidate.field_name || /signature\.|input|output|field|schema/i.test(evidenceText)) return 0.65;
  return 0.55;
}

function attachAssistError(profile, message) {
  if (!profile.data_profile) profile.data_profile = { labels: [] };
  profile.data_profile.label_llm_assist_errors = [
    ...(profile.data_profile.label_llm_assist_errors || []),
    { type: 'call_failed', message: String(message || '') }
  ];
}

function buildCacheKey(profile, node, model) {
  return `label_assist_${shortHash(JSON.stringify({
    ontology: ONTOLOGY_VERSION,
    model: model || '',
    node: {
      id: node.id || profile.node_id,
      name: node.name || profile.node_name,
      description: node.description || '',
      input: node.signature?.input || node.input || {},
      output: node.signature?.output || node.output || {},
      formal_semantics: node.formal_semantics || {},
      instructionText: node.instructionText || ''
    },
    profile: {
      roles: profile.node_roles || [],
      security_tags: profile.security_tags || [],
      operation_tags: profile.operation_tags || [],
      labels: profile.data_profile?.labels || []
    }
  }))}`;
}

function buildEdgeContext(edges = []) {
  const grouped = new Map();
  for (const edge of edges || []) {
    for (const nodeId of [edge.source, edge.target]) {
      if (!nodeId) continue;
      if (!grouped.has(nodeId)) grouped.set(nodeId, []);
      grouped.get(nodeId).push({
        direction: edge.source === nodeId ? 'outgoing' : 'incoming',
        source: edge.source,
        target: edge.target,
        type: edge.type || '',
        data_flow: edge.data_flow || {},
        semantic_reason: edge.semantic_reason || ''
      });
    }
  }
  return grouped;
}

function loadCache(cachePath) {
  const map = new Map();
  if (!cachePath || !fs.existsSync(cachePath)) return map;
  const lines = fs.readFileSync(cachePath, 'utf-8').split(/\r?\n/).filter(Boolean);
  for (const line of lines) {
    try {
      const item = JSON.parse(line);
      if (item.key) map.set(item.key, item.response);
    } catch {
      // Ignore corrupt cache lines.
    }
  }
  return map;
}

function saveCache(cachePath, cache) {
  if (!cachePath) return;
  fs.mkdirSync(path.dirname(path.resolve(cachePath)), { recursive: true });
  const lines = [];
  for (const [key, response] of cache.entries()) {
    lines.push(JSON.stringify({ key, response }));
  }
  fs.writeFileSync(cachePath, lines.join('\n') + (lines.length ? '\n' : ''), 'utf-8');
}

function resolveEndpoint(options = {}) {
  if (options.endpoint) return options.endpoint;
  if (options.provider === 'dashscope') {
    return process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
  }
  return 'https://api.openai.com/v1/chat/completions';
}

function createStats(enabled) {
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

function choosePrimaryCategory(labels = []) {
  if (!labels.length) return 'generic_data';
  return [...labels].sort((a, b) => Number(b.confidence || 0) - Number(a.confidence || 0))[0].category || 'generic_data';
}

function evidenceRank(level) {
  const ranks = { L0: 0, L1: 1, L2: 2, L3: 3, L4: 4 };
  return ranks[level] || 0;
}

function normalizePositiveInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

module.exports = {
  applyLlmLabelAssistToProfiles,
  shouldAssistProfile,
  normalizeAssistantLabels,
  buildPrompt,
  buildCacheKey,
  ONTOLOGY_VERSION,
  ALLOWED_LABELS
};

