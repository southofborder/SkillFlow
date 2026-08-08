/**
 * Feedback Edge Classifier
 *
 * After removeCycles tags the weakest cycle edge of each loop as a feedback edge
 * (see cycle-remover.js / method A), this module judges, for each feedback edge,
 * whether it is *plausible as a feedback edge* — i.e. whether the back-edge really
 * encodes a self-optimizing loop (write -> read -> write on the same store,
 * refined output flowing back into an earlier step) rather than being a mere
 * by-product of duplicate/structural edge resolution.
 *
 * Deliberately NOT a "real cycle vs fake cycle" classifier. Per user direction we
 * do not try to prove a loop true/false (e.g. by whether it passes through the
 * global llm.inference). Instead we ask the narrower, better-posed question about
 * the *back-edge itself*, and we bias toward recall:
 *
 *   1. A coarse rule pass (WIDE NET). Anything that looks like real feedback is
 *      marked `plausible` — we would rather keep a borderline edge than drop it.
 *      Only an edge with none of the plausibility signals (a low-confidence, no-
 *      data-flow, non-semantic, non-sink bare dependency back-edge) falls to the
 *      `implausible` candidate set.
 *   2. An optional LLM review pass (PRECISION). Only the rule-`implausible` edges
 *      are sent to the LLM, which may rescue them back to `plausible`. Rule-
 *      `plausible` edges are never sent (the wide net already kept them; cheaper).
 *
 * The classification is advisory metadata on the edge object only. It never
 * changes the adjacencyList, propagation, split, or label-flow behaviour — every
 * downstream consumer still filters feedback edges out via isFeedbackEdge
 * regardless of plausibility. So this pass is zero-regression by construction.
 */

const { isFeedbackEdge, isProtectedCycleEdge } = require('./cycle-remover');
const { buildNodeProfile } = require('../security/node-profiler');
const { postJsonWithTimeout, parseLooseJson } = require('../../../../shared/llm-utils.cjs');

// Confidence at or above which a bare dependency back-edge is considered strong
// enough to be plausible feedback on its own. Deliberately low (wide net): on the
// real corpus feedback-edge confidence clusters at 0.2-0.3, so 0.3 keeps the bulk
// as plausible while demoting only the weakest 0.1-0.2 band (non-sink, non-doc)
// into the LLM-review bucket. A higher cutoff (>=0.4) would flip almost all
// non-sink back-edges to implausible, which is no longer "wide".
const DEFAULT_PLAUSIBLE_MIN_CONF = 0.3;

// Roles that make a node a data sink. A feedback edge touching a sink is far more
// likely to be a genuine "write -> read back" loop, so it is kept as plausible.
// Mirrors SINK_LIKE_ROLES in node-splitter/node-profiler (single source of truth
// is the profiler; we re-derive the set here to avoid a cross-module import that
// those files don't export).
const SINK_LIKE_ROLES = new Set([
  'external_egress',
  'model_inference',
  'local_persistence',
  'command_execution',
  'destructive_operation',
  'tool_invocation'
]);

function isTruthyEnv(value) {
  return /^(1|true|yes|on)$/i.test(String(value || '').trim());
}

function isFalsyEnv(value) {
  return /^(0|false|no|off)$/i.test(String(value || '').trim());
}

/**
 * True if a graph node carries sink semantics — either an explicit Sink category
 * or a profile role in SINK_LIKE_ROLES.
 * @param {Object} node
 * @returns {boolean}
 */
function nodeIsSinkLike(node) {
  if (!node) return false;
  if (node.category === 'Sink') return true;
  try {
    const profile = buildNodeProfile(node, {});
    const roles = Array.isArray(profile.node_roles) ? profile.node_roles : [];
    return roles.some(role => SINK_LIKE_ROLES.has(role));
  } catch (_error) {
    // Profiling is best-effort; a failure here must not break classification.
    return false;
  }
}

/**
 * Coarse, recall-biased rule pass over a single feedback edge.
 * Returns { plausible, reason }. Any single plausibility signal wins.
 *
 * Note on data_flow: nearly every FCG edge carries a default structural data_flow
 * (e.g. response->content), so its presence is NOT a discriminative plausibility
 * signal and is deliberately not used here — it would make every edge plausible
 * and starve the LLM-review bucket. The discriminative signals are semantic/doc
 * edges, sink involvement, and confidence.
 *
 * @param {Object} edge
 * @param {Map<string, Object>} nodesById
 * @param {number} minConfidence
 */
function classifyFeedbackEdgeByRule(edge, nodesById, minConfidence) {
  // 1. Semantic / document / constraint back-edges carry directional feedback
  //    meaning by construction (a doc says "review then promote", an ordering
  //    constraint, an LLM-mediated hop). Reuse the protected-edge predicate.
  if (isProtectedCycleEdge(edge)) {
    return { plausible: true, reason: 'semantic/doc/constraint edge' };
  }

  // 2. Either endpoint is a sink -> likely a write->read-back feedback loop.
  const sourceNode = nodesById.get(edge.source);
  const targetNode = nodesById.get(edge.target);
  if (nodeIsSinkLike(sourceNode) || nodeIsSinkLike(targetNode)) {
    return { plausible: true, reason: 'touches a sink node' };
  }

  // 3. Confidence not low -> strong enough dependency to be real feedback.
  const confidence = Number.isFinite(edge.confidence) ? edge.confidence : 0.5;
  if (confidence >= minConfidence) {
    return { plausible: true, reason: `confidence ${confidence.toFixed(2)} >= ${minConfidence}` };
  }

  // No plausibility signal: low-confidence, non-semantic, non-sink bare
  // dependency back-edge. Most likely a dedup/structural by-product -> implausible
  // (this is the set handed to LLM review to be rescued or confirmed).
  return { plausible: false, reason: 'low-confidence non-sink dependency back-edge' };
}

/**
 * Build the user-message body listing each implausible back-edge for review.
 * The task instructions live in the system prompt (see reviewImplausibleWithLLM).
 */
function buildFeedbackReviewPrompt(items) {
  const lines = items.map((it, i) => {
    const path = Array.isArray(it.edge.feedback_cycle_path) ? it.edge.feedback_cycle_path.join(' -> ') : '';
    return [
      `#${i} id=${it.id}`,
      `  edge: ${it.sourceName} -> ${it.targetName}`,
      `  type: ${it.edge.type || 'data_dependency'}, confidence: ${Number.isFinite(it.edge.confidence) ? it.edge.confidence : 'n/a'}`,
      `  validation_method: ${it.edge.validation_method || 'n/a'}`,
      `  touches_sink: ${it.touchesSink}`,
      `  cycle_path: ${path || 'n/a'}`,
      it.edge.semantic_reason ? `  note: ${String(it.edge.semantic_reason).slice(0, 160)}` : null
    ].filter(Boolean).join('\n');
  });

  return `Judge plausibility of each removed back-edge below.\n\n${lines.join('\n\n')}`;
}

function parseFeedbackReviewResponse(raw) {
  const results = new Map();
  if (!raw || typeof raw !== 'object') return results;
  const arr = Array.isArray(raw.results) ? raw.results : [];
  for (const r of arr) {
    if (!r || r.id == null) continue;
    results.set(String(r.id), {
      is_plausible: r.is_plausible === true || /^(true|yes|plausible)$/i.test(String(r.is_plausible || '')),
      reason: typeof r.reason === 'string' ? r.reason : ''
    });
  }
  return results;
}

/**
 * Send the implausible feedback edges to the LLM in one batch to rescue any that
 * are actually genuine feedback. Returns a Map id -> { is_plausible, reason }.
 * Any failure/timeout/disabled state yields an empty Map (caller keeps the rule
 * verdict and marks the source as a fallback).
 *
 * Transport mirrors callDependencyBatchLLM in llm-validator.js: a single
 * OpenAI-compatible request via postJsonWithTimeout (timeout + retry handled
 * there), returning our own {results:[...]} schema parsed with parseLooseJson.
 */
async function reviewImplausibleWithLLM(items, config) {
  // Test/offline injection hook: bypass the network entirely.
  if (typeof config.feedbackReviewer === 'function') {
    try {
      const injected = await config.feedbackReviewer(items, config);
      return parseFeedbackReviewResponse({ results: injected });
    } catch (_error) {
      return new Map();
    }
  }

  const provider = config.provider || 'openai';
  const model = config.model || 'gpt-5.5';
  const apiKey = config.apiKey != null ? config.apiKey : process.env.LLM_API_KEY;
  const timeout = Number.isFinite(config.timeout) ? config.timeout : 180000;
  const endpoint = config.endpoint || '';

  if (config.disableLlm || !String(apiKey || '').trim() || items.length === 0) {
    return new Map();
  }

  const effectiveEndpoint = provider === 'dashscope'
    ? (endpoint || process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
    : (endpoint || 'https://api.openai.com/v1/chat/completions');

  try {
    const payload = await postJsonWithTimeout(effectiveEndpoint, {
      model,
      temperature: 0,
      messages: [
        {
          role: 'system',
          content: 'You audit removed back-edges (feedback edges) of a call graph. A feedback edge is PLAUSIBLE if it encodes a genuine self-optimizing loop (data/control flowing back into an earlier step, e.g. write then later read-back to refine, or a repeated review/promote cycle); IMPLAUSIBLE if it is only an artifact of duplicate/structural edge resolution with no real feedback meaning. Be lenient: when unsure, prefer plausible. Return strict JSON only: {"results":[{"id":"...","is_plausible":true|false,"reason":"..."}]}.'
        },
        {
          role: 'user',
          content: buildFeedbackReviewPrompt(items)
        }
      ]
    }, {
      timeoutMs: timeout,
      headers: { Authorization: `Bearer ${apiKey}` }
    });

    const content = payload?.choices?.[0]?.message?.content;
    return parseFeedbackReviewResponse(parseLooseJson(content));
  } catch (_error) {
    return new Map();
  }
}

/**
 * Classify every feedback edge in the graph, attaching plausibility metadata.
 * Mutates edge objects in place and returns a statistics object.
 *
 * @param {Object} graph - FCG with feedback edges already tagged by removeCycles.
 * @param {Object} config - LLM config (provider/model/apiKey/timeout/endpoint/
 *   disableLlm) plus optional feedbackLlmReview (bool), feedbackPlausibleMinConf
 *   (number) and feedbackReviewer (test hook).
 * @returns {Promise<Object>} statistics
 */
async function classifyFeedbackEdges(graph, config = {}) {
  const stats = {
    feedback_edge_count: 0,
    rule_plausible_count: 0,
    rule_implausible_count: 0,
    llm_reviewed_count: 0,
    llm_rescued_count: 0,
    llm_fallback_count: 0
  };
  if (!graph || !Array.isArray(graph.edges)) return stats;

  const feedbackEdges = graph.edges.filter(isFeedbackEdge);
  stats.feedback_edge_count = feedbackEdges.length;
  if (feedbackEdges.length === 0) return stats;

  const nodesById = graph.nodes instanceof Map ? graph.nodes : new Map();
  const minConfidence = Number.isFinite(config.feedbackPlausibleMinConf)
    ? config.feedbackPlausibleMinConf
    : DEFAULT_PLAUSIBLE_MIN_CONF;

  // Pass 1: coarse rule (wide net).
  const implausible = [];
  for (const edge of feedbackEdges) {
    const verdict = classifyFeedbackEdgeByRule(edge, nodesById, minConfidence);
    edge.feedback_plausibility = verdict.plausible ? 'plausible' : 'implausible';
    edge.feedback_plausibility_source = 'rule';
    edge.feedback_plausibility_reason = verdict.reason;
    if (verdict.plausible) {
      stats.rule_plausible_count += 1;
    } else {
      stats.rule_implausible_count += 1;
      const sourceNode = nodesById.get(edge.source);
      const targetNode = nodesById.get(edge.target);
      implausible.push({
        id: edge.id || `${edge.source}->${edge.target}`,
        edge,
        sourceName: (sourceNode && sourceNode.name) || edge.source,
        targetName: (targetNode && targetNode.name) || edge.target,
        touchesSink: nodeIsSinkLike(sourceNode) || nodeIsSinkLike(targetNode)
      });
    }
  }

  // Pass 2: LLM review of the implausible set only (precision, may rescue).
  const reviewEnabled = config.feedbackLlmReview !== false;
  if (!reviewEnabled || implausible.length === 0) {
    return stats;
  }

  const verdicts = await reviewImplausibleWithLLM(implausible, config);
  if (verdicts.size === 0) {
    // LLM unavailable/failed/timed out: keep rule verdict, mark as fallback.
    for (const it of implausible) {
      it.edge.feedback_plausibility_source = 'llm_fallback';
      stats.llm_fallback_count += 1;
    }
    return stats;
  }

  for (const it of implausible) {
    const verdict = verdicts.get(it.id);
    if (!verdict) {
      // No verdict returned for this id: fall back to the rule result.
      it.edge.feedback_plausibility_source = 'llm_fallback';
      stats.llm_fallback_count += 1;
      continue;
    }
    stats.llm_reviewed_count += 1;
    it.edge.feedback_plausibility_source = 'llm';
    it.edge.feedback_plausibility_reason = verdict.reason || it.edge.feedback_plausibility_reason;
    if (verdict.is_plausible) {
      it.edge.feedback_plausibility = 'plausible';
      stats.rule_implausible_count -= 1;
      stats.rule_plausible_count += 1;
      stats.llm_rescued_count += 1;
    }
  }

  return stats;
}

/**
 * Resolve the LLM-review toggle from an explicit option or the
 * FCG_FEEDBACK_LLM_REVIEW env var (default ON).
 * @param {boolean|undefined} explicit
 * @returns {boolean}
 */
function resolveFeedbackLlmReview(explicit) {
  if (explicit === true || explicit === false) return explicit;
  const env = process.env.FCG_FEEDBACK_LLM_REVIEW;
  if (env === undefined || env === '') return true;
  if (isFalsyEnv(env)) return false;
  if (isTruthyEnv(env)) return true;
  return true;
}

module.exports = {
  classifyFeedbackEdges,
  classifyFeedbackEdgeByRule,
  nodeIsSinkLike,
  resolveFeedbackLlmReview,
  DEFAULT_PLAUSIBLE_MIN_CONF
};
