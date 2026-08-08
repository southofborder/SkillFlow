const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const {
  parseLooseJson,
  normalizeBoolean,
  normalizeScaledNumber,
  postJsonWithTimeout
} = require('../../../shared/llm-utils.cjs');
const { stableStringify, round3, uniqueValues } = require('./utils');
const { budgetPackIfNeeded } = require('./evidence-budget');
const { buildSharedTaskMemory } = require('./evidence-pack');
const {
  COMPONENT_KEYS,
  normalizeComponentScores,
  componentMin
} = require('./necessity-baseline');

const PROMPT_VERSION = 'doe-llm-judge-v6-reduction-antichain';
const DEFAULT_LLM_MODEL = 'gpt-5.5';
const DEFAULT_BATCH_SIZE = 4;
const DEFAULT_VOTES = 1;
const DEFAULT_ESCALATION_VOTES = 3;
const DEFAULT_ESCALATION_POLICY = 'risk_or_uncertain';
const DEFAULT_LLM_CONCURRENCY = 2;
const DEFAULT_MAX_BATCH_CHARS = 60000;
const DEFAULT_TIMEOUT_MS = 30000;
const DEFAULT_LLM_WEIGHT = 0.7;
const DEFAULT_THRESHOLD = 0.7;
const DEFAULT_NECESSITY_THRESHOLD = 0.7;

async function judgeEvidencePacks(evidencePacks = [], options = {}) {
  if (!evidencePacks.length) return new Map();
  const config = {
    ...resolveJudgeOptions(options),
    // task_memory 现在由 FCG 直接聚合(skill 级,batch 内共享),不再从 packs 扫 section。
    skillTaskMemory: buildSharedTaskMemory(options.fcg || {}, options.evidencePackContext || null)
  };
  if (!config.llmClient && !String(config.apiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required for DOE LLM judge; use --no-llm-judge for rule-only analysis');
  }

  const cache = loadJudgeCache(config.cachePath);
  const stats = {
    first_pass_count: evidencePacks.length,
    escalated_count: 0,
    timeout_split_count: 0,
    cache_hit_count: 0,
    fallback_count: 0,
    fallback_units: [],
    task_memory_node_count: config.skillTaskMemory.task_context_node_count || 0,
    task_memory_doc_source_count: config.skillTaskMemory.documentation_source_count || 0,
    // Endpoint-reported token usage, summed across every actual model call.
    // Zero extra API cost: usage ships inside each existing response body; we
    // just stop discarding it. cached_tokens quantifies prompt-caching wins
    // (the stable task_memory/instructions prefix is re-billed at a discount).
    usage: newUsageAccumulator()
  };

  const firstPass = await judgePackStage(evidencePacks, {
    ...config,
    activeVotes: config.votes,
    stage: 'first_pass',
    cache,
    stats
  });
  const results = new Map(firstPass);

  const escalationPacks = selectEscalationPacks(evidencePacks, firstPass, config);
  stats.escalated_count = escalationPacks.length;
  if (escalationPacks.length > 0) {
    const escalated = await judgePackStage(escalationPacks, {
      ...config,
      activeVotes: config.escalationVotes,
      stage: 'escalation',
      cache,
      stats
    });
    for (const [unitId, result] of escalated.entries()) {
      results.set(unitId, {
        ...result,
        escalated: true
      });
    }
  }

  results.judge_stats = stats;
  return results;
}

async function judgePackStage(evidencePacks, config) {
  const results = new Map();
  const uncached = [];

  for (const pack of evidencePacks) {
    const cacheKey = buildJudgeCacheKey(pack, config, {
      stage: config.stage,
      votes: config.activeVotes
    });
    const cached = config.cache.entries.get(cacheKey);
    if (cached?.result) {
      config.stats.cache_hit_count += 1;
      results.set(pack.unit_id, {
        ...cached.result,
        cache_hit: true,
        cache_stage: config.stage
      });
    } else {
      uncached.push({ pack, cacheKey });
    }
  }

  const batches = chunkJudgePacks(uncached, config);
  const batchResults = await runWithConcurrency(batches, config.concurrency, batch => judgePackBatchWithRetry(batch, config));
  for (const item of batchResults.flat()) {
    const result = item.result;
    if (!result) {
      // Graceful fallback: a single pack that still failed (e.g. a timeout that
      // survived budgeting + adaptive timeout). Rather than throw and drop the
      // whole skill, leave this unit absent from results. applyLlmJudgements
      // then degrades it to rule-only scoring with requires_review=true.
      config.stats.fallback_count += 1;
      config.stats.fallback_units.push({
        unit_id: item.pack.unit_id,
        reason: item.fallback_reason || 'llm_judge_failed'
      });
      continue;
    }
    results.set(item.pack.unit_id, result);
    appendJudgeCacheEntry(config.cachePath, item.cacheKey, result, item.pack, config);
  }

  return results;
}

async function judgePackBatchWithRetry(batch, config) {
  try {
    const batchResults = await judgePackBatch(batch.map(item => item.pack), config);
    return batch.map(item => ({
      ...item,
      result: batchResults.get(item.pack.unit_id)
    }));
  } catch (error) {
    // Only transient transport failures (timeout/network/429/5xx) are eligible
    // for split + per-unit fallback. Everything else — schema/validation/parse
    // errors, auth/config errors — is terminal and must fail fast, since it
    // would fail identically on retry and signals a real defect.
    if (!isTransientLlmError(error)) throw error;
    if (batch.length <= 1) {
      // Transient failure on a single pack: surface a null result so the unit
      // falls back to rule-only scoring instead of crashing the skill.
      return batch.map(item => ({
        ...item,
        result: null,
        fallback_reason: error.code === 'LLM_TIMEOUT' ? 'llm_timeout' : `llm_error:${truncate(String(error.message || ''), 160)}`
      }));
    }
    config.stats.timeout_split_count += 1;
    const midpoint = Math.ceil(batch.length / 2);
    const left = await judgePackBatchWithRetry(batch.slice(0, midpoint), config);
    const right = await judgePackBatchWithRetry(batch.slice(midpoint), config);
    return [...left, ...right];
  }
}

// Transient = recoverable-in-principle transport failures: request timeout,
// network reset/refusal/DNS, HTTP 429 (rate limit), or HTTP 5xx (server). These
// are the only errors that justify batch-splitting or per-unit fallback.
function isTransientLlmError(error) {
  if (!error) return false;
  if (error.code === 'LLM_TIMEOUT') return true;
  const code = String(error.code || '');
  if (['ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED', 'EAI_AGAIN', 'EPIPE', 'ENOTFOUND'].includes(code)) return true;
  const message = String(error.message || '');
  if (/^HTTP\s+429\b/.test(message)) return true;
  if (/^HTTP\s+5\d\d\b/.test(message)) return true;
  if (/timed out/i.test(message)) return true;
  // Response-level malformation is transient: a truncated body, a gateway error
  // page, or the model failing to emit the envelope. Splitting the batch shrinks
  // the prompt and usually recovers; at size 1 the unit falls back to rule-only
  // rather than losing the whole skill. NOT transient: per-unit schema defects
  // (`component scores are required`, `no valid evidence_id references`) which
  // are deterministic and would fail identically on retry.
  if (/Invalid JSON response/i.test(message)) return true;
  if (/expected JSON object/i.test(message)) return true;
  if (/missing assessments/i.test(message)) return true;
  if (/missing unit_id/i.test(message)) return true;
  return false;
}

async function judgePackBatch(evidencePacks, config) {
  const votesByUnit = new Map(evidencePacks.map(pack => [pack.unit_id, []]));
  for (let voteIndex = 0; voteIndex < config.activeVotes; voteIndex += 1) {
    const raw = await callJudgeBatchModel(evidencePacks, config);
    const normalized = normalizeJudgeBatchResult(raw, evidencePacks);
    for (const pack of evidencePacks) {
      votesByUnit.get(pack.unit_id).push(normalized.get(pack.unit_id));
    }
  }

  const results = new Map();
  for (const pack of evidencePacks) {
    results.set(pack.unit_id, aggregateVotes(votesByUnit.get(pack.unit_id), pack, config));
  }
  return results;
}

function selectEscalationPacks(evidencePacks, firstPassResults, config) {
  if (config.escalationPolicy === 'none' || config.escalationVotes <= config.votes) return [];
  // Never escalate a unit that produced no first-pass result: it fell back
  // (transient failure) and is already degrading to rule-only scoring. Re-judging
  // it would just time out again and double-count the fallback.
  const judged = evidencePacks.filter(pack => firstPassResults.has(pack.unit_id));
  if (config.escalationPolicy === 'all') return judged;
  return judged.filter(pack => shouldEscalatePack(pack, firstPassResults.get(pack.unit_id), config));
}

function shouldEscalatePack(pack, result, config) {
  if (!result) return true;
  const assessment = config.assessmentByUnit?.get?.(pack.unit_id) || {};
  if (result.requires_review || (result.invalid_evidence_ids || []).length > 0) return true;
  if (result.disagreement >= 0.35) return true;
  if (Object.values(result.component_scores || {}).some(score => Number(score) < 0.45)) return true;

  const ruleScores = assessment.rule_component_scores || assessment.component_scores || {};
  const blendedScores = {};
  for (const key of COMPONENT_KEYS) {
    const llmScore = Number(result.component_scores?.[key] ?? result.llm_necessity_score ?? 0.1);
    const ruleScore = Number(ruleScores[key] ?? assessment.necessity_score ?? 0.1);
    blendedScores[key] = round3(config.llmWeight * llmScore + (1 - config.llmWeight) * ruleScore);
  }
  const blendedNecessity = componentMin(blendedScores);
  const doeScore = Number(assessment.exposure_score || 0) * (1 - blendedNecessity) + Number(assessment.baseline_adjustment || 0);
  const potentialDoe = Boolean(assessment.boundary_crossed && blendedNecessity < config.necessityThreshold);
  const ruleLlmGap = Math.abs(Number(assessment.necessity_score || 0) - Number(result.llm_necessity_score || 0));
  return (
    potentialDoe ||
    doeScore >= config.threshold ||
    Boolean(assessment.requires_review) ||
    ruleLlmGap >= 0.35
  );
}

function chunkJudgePacks(items, config) {
  const chunks = [];
  let current = [];
  let currentChars = 0;

  for (const item of items || []) {
    const itemChars = estimateJudgePackChars(item.pack);
    const wouldExceedSize = current.length >= config.batchSize;
    const wouldExceedChars = current.length > 0 && currentChars + itemChars > config.maxBatchChars;
    if (wouldExceedSize || wouldExceedChars) {
      chunks.push(current);
      current = [];
      currentChars = 0;
    }
    current.push(item);
    currentChars += itemChars;
  }
  if (current.length > 0) chunks.push(current);
  return chunks;
}

function estimateJudgePackChars(pack) {
  return stableStringify(compactPackForCache(pack || {})).length + 1024;
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

async function callJudgeBatchModel(evidencePacks, config) {
  const payload = buildJudgePayload(evidencePacks, config);
  if (config.llmClient) {
    const clientResult = await config.llmClient({ evidencePacks, payload, config });
    // A custom client may return either raw content (tests) or a response-shaped
    // object carrying usage; accumulate when present (no-op otherwise).
    accumulateUsage(config.stats, clientResult?.usage);
    return clientResult;
  }
  const response = await postJsonWithTimeout(config.endpoint, payload, {
    timeoutMs: adaptiveTimeoutMs(payload, config),
    headers: {
      Authorization: `Bearer ${config.apiKey}`
    }
  });
  // Fold this call's token usage into the run accumulator before we discard the
  // envelope. No extra request/tokens — usage is already in this response body.
  accumulateUsage(config.stats, response?.usage);
  return response?.choices?.[0]?.message?.content ?? response;
}

// OpenAI-compatible usage accounting. cached_tokens (prompt_tokens_details) is
// the prompt-caching hit count; different providers expose the same figure under
// a couple of legacy keys, so we probe all of them.
function newUsageAccumulator() {
  return { calls: 0, prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, cached_tokens: 0 };
}

function accumulateUsage(stats, usage) {
  if (!stats || !stats.usage || !usage || typeof usage !== 'object') return;
  const acc = stats.usage;
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

// Fraction of prompt tokens served from cache across the run. This is the direct
// signal that the stable-prefix design is working; a drop flags a prefix break.
function summarizeUsage(usage) {
  if (!usage || !usage.calls) return null;
  const cacheHitRatio = usage.prompt_tokens ? round3(usage.cached_tokens / usage.prompt_tokens) : 0;
  return { ...usage, prompt_cache_hit_ratio: cacheHitRatio };
}

// Large payloads legitimately take longer to generate. Rather than cut content
// (which would cost accuracy), give bigger requests proportionally more time so
// they complete with full fidelity. Scales from config.timeoutMs up to a cap.
function adaptiveTimeoutMs(payload, config) {
  const base = Number(config.timeoutMs) || DEFAULT_TIMEOUT_MS;
  const cap = Number(config.adaptiveTimeoutMaxMs) || Math.max(base, base * 4);
  let chars = 0;
  try {
    chars = JSON.stringify(payload || {}).length;
  } catch (_) {
    chars = 0;
  }
  // +1ms per 40 chars beyond a 20k baseline (~+25s per 1M chars), capped.
  const extra = Math.max(0, chars - 20000) / 40;
  return Math.min(cap, Math.round(base + extra));
}

function buildJudgePayload(evidencePacks, config) {
  const promptBody = buildJudgePromptBody(evidencePacks, config);
  return {
    model: config.model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: [
          'You are a security evidence judge for potential data over-exposure analysis.',
          'Judge layered necessity for each boundary observation and label_flow.',
          'Local necessity has two components: action_input_need and receiver_semantic_need.',
          'Global necessity is a single component, task_need: whether the full label_flow path belongs to the data/control flow needed for the declared skill task AND the boundary node is necessary in that path. Both must hold for task_need to be high.',
          'Do not decide exposure or final risk. Do not lower necessity merely because a label is sensitive.',
          "A flow reaches you ONLY because it crosses a real exposure boundary. sink_boundary.exposure_tier=='high_sensitivity_egress' means the data genuinely leaves the local process or is retained — this covers model providers, external networks, third-party AND first-party services, webhooks, and persistent storage ALIKE. Treat EVERY high_sensitivity_egress as a real, severe leak; none of them is a trusted-internal sink. In particular a model provider (the LLM itself) is a real egress, not an insider — do NOT raise receiver_semantic_need merely because the model needs the data to reason. For every such receiver, judge whether it semantically needs THIS specific label by the same standard you would apply to any external receiver.",
          'First read shared_context.task_memory as the global task memory, then judge each unit with its unit-local evidence.',
          'Use task_memory evidence only when the unit lists that id in task_memory_evidence_ids.',
          'Every conclusion must cite evidence handles that exist in the pack: the literal strings "label" or "sink_boundary", a flow[] node\'s node_name, or a task_memory id listed in task_memory_evidence_ids.',
          'Return strict JSON only.'
        ].join(' ')
      },
      {
        role: 'user',
        content: JSON.stringify({
          prompt_version: PROMPT_VERSION,
          output_schema: 'Return {"assessments":[...]} only. Each item: unit_id; components for action_input_need, receiver_semantic_need, task_need. Each component has score [0,1], status supporting|contradicting|insufficient, supporting_evidence_ids, contradicting_evidence_ids, reasoning_summary. Also include required_for_task, necessity_level none|low|medium|high|critical, reasoning_summary, supporting_evidence_ids, contradicting_evidence_ids.',
          scoring_guidance: [
            'Score action input need, receiver semantic need, and overall task need (full flow-path plus boundary-node necessity, conjunction).',
            '0.95 explicit proof; 0.75 strong support; 0.45 weak/broad support; 0.10 insufficient; 0 unrelated or contradicted.',
            'Cite evidence handles only: "label", "sink_boundary", a flow[] node_name, or a task_memory id.'
          ],
          judgement_flow: [
            'Use shared_context.task_memory for the stable skill-level task and route context.',
            'Use the pack label and sink_boundary for local necessity (action_input_need, receiver_semantic_need).',
            'The flow[] sink node (role="sink" or "source_sink") may carry a sink_surface[] field listing the concrete output channel/medium (e.g. webhook_post, api_call, file_write, database_write, shell_exec) — finer than sink_boundary\'s operation_type/data_surface. Every sink_boundary.exposure_tier=="high_sensitivity_egress" is a real egress regardless of channel; do not treat any of them as a trusted-internal sink.',
            'The flow[] sink node may carry schema_declares_input (true/false): whether the sink\'s declared input schema includes THIS specific label — a strong, direct action_input_need signal (true=the sink explicitly consumes it; false=the sink declares inputs but not this label). The source node may carry origin_trust (where the data was introduced): a user_visible origin returning to the user differs from external_network data flowing onward. Use these structural facts as hard evidence, not the narrative text alone.',
            'sink_boundary describes the single boundary the sink node crosses (each node crosses at most one boundary by construction); the sink node\'s role/capabilities live on the flow[] node with role="sink".',
            'Use the pack flow[] (source-to-sink path with per-node transforms) plus task_memory for task_need (full-path AND boundary/sink-node necessity together).',
            'In flow[], each node role is positional (source=introduction point, sink=the single boundary node, transform=intermediate); a node\'s capabilities[] list what it CAN do, not what it does to this label here.',
            'A node either has action (single operation, a summary string) or operations[] (ordered multi-step sequence). In operations[], the order IS the execution order, and a step tags[] may mark data-shaping steps (field_slice, redaction, semantic_extraction, aggregation, pseudonymization). Judge exposure by that order: a slice/redaction BEFORE an egress/write step mitigates it; the same shaping AFTER egress does not.',
            'A node transform/transforms field reports label changes actually observed during propagation (e.g. field sliced, summarized); treat these as realized mitigations, and check they align with the operations[] the node declares.',
            'sink_boundary.reduction_before_egress (when present) lists the SPECIFIC data reductions this flow actually applied before crossing the boundary — the maximal, mutually-incomparable set drawn from {redact_drop (fields dropped by redaction), field_slice_drop / field_slice_keep (a subset of fields selected), summarization (free-text condensed, identifiers not guaranteed removed), aggregate (many records combined into statistics)}. It raises receiver_semantic_need ONLY to the extent the applied kinds actually neutralize THIS label for THIS receiver: judge sufficiency, do not clear exposure on mere presence. redact_drop/aggregate of the sensitive field are strong protection; summarization or a field_slice that KEEPS the sensitive field is weak or none. An absent/empty field means raw data crossed the boundary. Cross-check against the sink node operations[] order (a reduction listed here must precede the egress step to count).',
            'Score every assessment independently, but apply the same task memory consistently across the batch.'
          ],
          shared_context: promptBody.shared_context,
          evidence_packs: promptBody.evidence_packs
        })
      }
    ]
  };
}

// task_memory 进 prompt 前剔除纯观测字段:count 类计数对 LLM 判定无信息量,
// 仅供 stats(见 judgeEvidencePacks)。stats 读的是 config.skillTaskMemory 原对象,
// 不受此裁剪影响。evidence[] 里的 evidence_id 是 grounding 锚点,保留。
function trimTaskMemoryForPrompt(taskMemory = {}) {
  const { task_context_node_count, documentation_source_count, ...rest } = taskMemory;
  return rest;
}

function buildJudgePromptBody(evidencePacks = [], config = {}) {
  return {
    shared_context: {
      // task_memory 由 FCG 在 skill 级聚合一次(config.skillTaskMemory),batch 内共享。
      task_memory: trimTaskMemoryForPrompt(config.skillTaskMemory || { evidence: [] })
    },
    // Tier 0: packs within the ceiling are passed through unmodified, so the
    // judge sees full evidence (verdict identical to no budgeting). Tier 2:
    // only oversized packs — which would otherwise overflow context and be
    // dropped — are reduced, with the boundary node and path endpoints kept.
    evidence_packs: evidencePacks.map(pack => budgetPackIfNeeded(compactPackForPrompt(pack), config.budgetLimits || {}))
  };
}



// 新 pack 已是扁平 flow-centric 结构,自带 task_memory_evidence_ids,
// prompt 形态几乎等同于 pack 本身——只透传判断所需字段。
function compactPackForPrompt(pack = {}) {
  return {
    unit_id: pack.unit_id || '',
    question: pack.question || '',
    observation_id: pack.observation_id || '',
    label_flow_id: pack.label_flow_id || '',
    label: pack.label || {},
    sink_boundary: pack.sink_boundary || {},
    flow: pack.flow || [],
    task_memory_evidence_ids: pack.task_memory_evidence_ids || []
  };
}

// 缓存键用的稳定投影:任务记忆在 skill 内恒定,不进单 pack 哈希。
function compactPackForCache(pack = {}) {
  return {
    unit_id: pack.unit_id || '',
    observation_id: pack.observation_id || '',
    label_flow_id: pack.label_flow_id || '',
    label: pack.label || {},
    sink_boundary: pack.sink_boundary || {},
    flow: pack.flow || [],
    task_memory_evidence_ids: pack.task_memory_evidence_ids || []
  };
}

// 合法引用句柄 = pack 结构里真实存在的东西,不再是单列的 evidence_id 索引:
//   - 字面量 'label' / 'sink_boundary' 两块
//   - flow[] 每个节点的 node_name(判据即节点本身)
//   - task_memory_evidence_ids(指向 batch 共享的 task_memory 条目)
// 校验只看引用是否落在这个集合内,落空的进 invalid_evidence_ids。
function validEvidenceIdsForPack(pack = {}) {
  return new Set([
    'label',
    'sink_boundary',
    ...(pack.flow || []).map(node => node && node.node_name).filter(Boolean),
    ...(pack.task_memory_evidence_ids || [])
  ]);
}

function normalizeJudgeBatchResult(raw, evidencePacks) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('Invalid DOE LLM judge response: expected JSON object');
  }
  const items = Array.isArray(parsed.assessments)
    ? parsed.assessments
    : (evidencePacks.length === 1 ? [{ unit_id: evidencePacks[0].unit_id, ...parsed }] : []);
  if (!items.length) throw new Error('Invalid DOE LLM judge response: missing assessments[]');

  const packByUnit = new Map(evidencePacks.map(pack => [pack.unit_id, pack]));
  const results = new Map();
  for (const item of items) {
    const unitId = String(item.unit_id || '').trim();
    const pack = packByUnit.get(unitId);
    if (!pack) continue;
    results.set(unitId, normalizeJudgeResult(item, pack));
  }
  for (const pack of evidencePacks) {
    if (!results.has(pack.unit_id)) throw new Error(`Invalid DOE LLM judge response: missing unit_id ${pack.unit_id}`);
  }
  return results;
}

function normalizeJudgeResult(raw, evidencePack) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`Invalid DOE LLM judge response for ${evidencePack.unit_id}: expected JSON object`);
  }
  const evidenceIds = validEvidenceIdsForPack(evidencePack);
  if (!hasComponentScoreEvidence(parsed)) {
    throw new Error(`Invalid DOE LLM judge response for ${evidencePack.unit_id}: component scores are required`);
  }
  const components = normalizeComponentResults(parsed, evidenceIds);
  const supporting = normalizeEvidenceRefs([
    ...evidenceRefValues(parsed.supporting_evidence_ids),
    ...COMPONENT_KEYS.flatMap(key => components[key].supporting_evidence_ids || [])
  ], evidenceIds);
  const contradicting = normalizeEvidenceRefs([
    ...evidenceRefValues(parsed.contradicting_evidence_ids),
    ...COMPONENT_KEYS.flatMap(key => components[key].contradicting_evidence_ids || [])
  ], evidenceIds);
  if (!supporting.valid && !contradicting.valid) {
    throw new Error(`Invalid DOE LLM judge response for ${evidencePack.unit_id}: no valid evidence_id references`);
  }

  const componentScores = normalizeComponentScores(COMPONENT_KEYS.reduce((acc, key) => {
    acc[key] = components[key].score;
    return acc;
  }, {}));
  const necessityScore = componentMin(componentScores);
  return {
    component_scores: componentScores,
    component_judgements: components,
    llm_necessity_score: necessityScore,
    necessity_level: normalizeNecessityLevel(parsed.necessity_level),
    required_for_task: normalizeBoolean(parsed.required_for_task, necessityScore >= 0.7),
    reasoning_summary: truncate(String(parsed.reasoning_summary || parsed.reason || '').trim(), 600),
    supporting_evidence_ids: supporting.refs,
    contradicting_evidence_ids: contradicting.refs,
    invalid_evidence_ids: uniqueValues([
      ...supporting.invalidRefs,
      ...contradicting.invalidRefs,
      ...COMPONENT_KEYS.flatMap(key => components[key].invalid_evidence_ids || [])
    ])
  };
}

function aggregateVotes(votes = [], evidencePack = {}, config = {}) {
  if (!votes.length) throw new Error(`No DOE LLM judge votes for ${evidencePack.unit_id}`);
  const componentScores = {};
  const componentJudgements = {};
  for (const key of COMPONENT_KEYS) {
    const scores = votes.map(vote => vote.component_scores?.[key] ?? vote.llm_necessity_score ?? 0.1).sort((a, b) => a - b);
    componentScores[key] = round3(scores[Math.floor(scores.length / 2)]);
    componentJudgements[key] = aggregateComponentEvidence(votes, key);
  }
  const median = componentMin(componentScores);
  const requiredTrue = votes.filter(vote => vote.required_for_task).length;
  const requiredForTask = requiredTrue > votes.length / 2;
  const allScores = COMPONENT_KEYS.flatMap(key => votes.map(vote => vote.component_scores?.[key] ?? 0.1));
  const disagreement = round3(Math.max(...allScores) - Math.min(...allScores));
  const chosen = votes.reduce((best, vote) => (
    Math.abs(vote.llm_necessity_score - median) < Math.abs(best.llm_necessity_score - median) ? vote : best
  ), votes[0]);
  const supporting = uniqueValues(votes.flatMap(vote => vote.supporting_evidence_ids || []));
  const contradicting = uniqueValues(votes.flatMap(vote => vote.contradicting_evidence_ids || []));
  const invalidRefs = uniqueValues(votes.flatMap(vote => vote.invalid_evidence_ids || []));
  return {
    component_scores: normalizeComponentScores(componentScores),
    component_judgements: componentJudgements,
    llm_necessity_score: round3(median),
    necessity_level: chosen.necessity_level,
    required_for_task: requiredForTask,
    reasoning_summary: chosen.reasoning_summary,
    supporting_evidence_ids: supporting,
    contradicting_evidence_ids: contradicting,
    invalid_evidence_ids: invalidRefs,
    vote_count: votes.length,
    votes,
    disagreement,
    requires_review: disagreement > 0.35 || invalidRefs.length > 0,
    model: config.model,
    provider: config.provider,
    stage: config.stage || 'first_pass',
    prompt_version: PROMPT_VERSION
  };
}

function resolveJudgeOptions(options = {}) {
  const escalationPolicy = normalizeEscalationPolicy(options.llmEscalationPolicy || process.env.DOE_LLM_ESCALATION_POLICY);
  return {
    provider: options.llmProvider || process.env.LLM_PROVIDER || 'openai',
    model: options.llmModel || process.env.LLM_MODEL || DEFAULT_LLM_MODEL,
    endpoint: resolveLlmEndpoint(options),
    apiKey: Object.prototype.hasOwnProperty.call(options, 'llmApiKey') ? options.llmApiKey : process.env.LLM_API_KEY,
    timeoutMs: normalizePositiveInteger(options.llmTimeout || process.env.LLM_TIMEOUT, DEFAULT_TIMEOUT_MS),
    cachePath: options.llmCache || '',
    batchSize: normalizePositiveInteger(options.llmBatchSize, DEFAULT_BATCH_SIZE),
    votes: normalizePositiveInteger(options.llmVotes, DEFAULT_VOTES),
    escalationVotes: normalizePositiveInteger(options.llmEscalationVotes ?? process.env.DOE_LLM_ESCALATION_VOTES, DEFAULT_ESCALATION_VOTES),
    escalationPolicy,
    concurrency: normalizePositiveInteger(options.llmConcurrency ?? process.env.DOE_LLM_CONCURRENCY, DEFAULT_LLM_CONCURRENCY),
    maxBatchChars: normalizePositiveInteger(options.llmMaxBatchChars ?? process.env.DOE_LLM_MAX_BATCH_CHARS, DEFAULT_MAX_BATCH_CHARS),
    adaptiveTimeoutMaxMs: normalizePositiveInteger(options.adaptiveTimeoutMaxMs ?? process.env.DOE_ADAPTIVE_TIMEOUT_MAX_MS, 0) || undefined,
    budgetLimits: {
      evidenceMaxPackChars: options.evidenceMaxPackChars ?? process.env.DOE_EVIDENCE_MAX_PACK_CHARS,
      evidencePathNodeWindow: options.evidencePathNodeWindow ?? process.env.DOE_EVIDENCE_PATH_NODE_WINDOW,
      evidenceMaxTextChars: options.evidenceMaxTextChars ?? process.env.DOE_EVIDENCE_MAX_TEXT_CHARS,
      evidenceMaxArrayItems: options.evidenceMaxArrayItems ?? process.env.DOE_EVIDENCE_MAX_ARRAY_ITEMS
    },
    threshold: normalizeScaledThreshold(options.threshold, DEFAULT_THRESHOLD),
    necessityThreshold: normalizeScaledThreshold(options.necessityThreshold, DEFAULT_NECESSITY_THRESHOLD),
    assessmentByUnit: options.assessmentByUnit || new Map(),
    llmWeight: normalizeWeight(options.llmWeight),
    llmClient: options.llmClient || null
  };
}

function normalizeComponentResults(parsed = {}, evidenceIds) {
  const components = parsed.components && typeof parsed.components === 'object' ? parsed.components : {};
  const result = {};
  for (const key of COMPONENT_KEYS) {
    const raw = components[key] && typeof components[key] === 'object'
      ? components[key]
      : (parsed[key] && typeof parsed[key] === 'object' ? parsed[key] : {});
    const score = normalizeScaledNumber(
      raw.score ?? raw.llm_score ?? raw.necessity_score ?? parsed[key],
      { fallback: 0.1 }
    );
    const supporting = normalizeEvidenceRefs(raw.supporting_evidence_ids ?? parsed.supporting_evidence_ids, evidenceIds);
    const contradicting = normalizeEvidenceRefs(raw.contradicting_evidence_ids ?? parsed.contradicting_evidence_ids, evidenceIds);
    result[key] = {
      score: round3(score),
      status: normalizeComponentStatus(raw.status),
      reasoning_summary: truncate(String(raw.reasoning_summary || raw.reason || '').trim(), 400),
      supporting_evidence_ids: supporting.refs,
      contradicting_evidence_ids: contradicting.refs,
      invalid_evidence_ids: uniqueValues([...supporting.invalidRefs, ...contradicting.invalidRefs])
    };
  }
  return result;
}

function hasComponentScoreEvidence(parsed = {}) {
  const components = parsed.components && typeof parsed.components === 'object' ? parsed.components : {};
  return COMPONENT_KEYS.some(key => {
    const nested = components[key];
    if (nested && typeof nested === 'object' && (
      nested.score !== undefined ||
      nested.llm_score !== undefined ||
      nested.necessity_score !== undefined
    )) {
      return true;
    }
    const topLevel = parsed[key];
    return topLevel !== undefined && (
      typeof topLevel === 'number' ||
      typeof topLevel === 'string' ||
      (typeof topLevel === 'object' && topLevel !== null && (
        topLevel.score !== undefined ||
        topLevel.llm_score !== undefined ||
        topLevel.necessity_score !== undefined
      ))
    );
  });
}

function aggregateComponentEvidence(votes = [], key) {
  const supporting = uniqueValues(votes.flatMap(vote => vote.component_judgements?.[key]?.supporting_evidence_ids || []));
  const contradicting = uniqueValues(votes.flatMap(vote => vote.component_judgements?.[key]?.contradicting_evidence_ids || []));
  const invalid = uniqueValues(votes.flatMap(vote => vote.component_judgements?.[key]?.invalid_evidence_ids || []));
  const statuses = votes.map(vote => vote.component_judgements?.[key]?.status).filter(Boolean);
  return {
    status: majorityValue(statuses) || '',
    supporting_evidence_ids: supporting,
    contradicting_evidence_ids: contradicting,
    invalid_evidence_ids: invalid,
    reasoning_summary: votes.find(vote => vote.component_judgements?.[key]?.reasoning_summary)?.component_judgements?.[key]?.reasoning_summary || ''
  };
}

function normalizeComponentStatus(value) {
  const text = String(value || '').trim().toLowerCase();
  if (['supporting', 'contradicting', 'insufficient'].includes(text)) return text;
  return '';
}

function resolveLlmEndpoint(options = {}) {
  if (options.llmEndpoint || process.env.LLM_ENDPOINT) return options.llmEndpoint || process.env.LLM_ENDPOINT;
  const provider = String(options.llmProvider || process.env.LLM_PROVIDER || 'openai').toLowerCase();
  if (provider === 'dashscope') {
    return process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
  }
  return 'https://api.openai.com/v1/chat/completions';
}

function buildJudgeCacheKey(evidencePack, config = {}, stageOptions = {}) {
  const payload = {
    prompt_version: PROMPT_VERSION,
    model: config.model,
    provider: config.provider,
    stage: stageOptions.stage || config.stage || 'first_pass',
    votes: stageOptions.votes || config.activeVotes || config.votes || DEFAULT_VOTES,
    evidence_pack: compactPackForCache(evidencePack)
  };
  return crypto.createHash('sha256').update(stableStringify(payload)).digest('hex');
}

function loadJudgeCache(cachePath) {
  const entries = new Map();
  if (!cachePath || !fs.existsSync(cachePath)) return { entries };
  const lines = fs.readFileSync(cachePath, 'utf-8').split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const item = JSON.parse(line);
      if (item.cache_key && item.result) entries.set(item.cache_key, item);
    } catch {
      // Ignore malformed cache lines.
    }
  }
  return { entries };
}

function appendJudgeCacheEntry(cachePath, cacheKey, result, evidencePack, config) {
  if (!cachePath) return;
  fs.mkdirSync(path.dirname(cachePath), { recursive: true });
  fs.appendFileSync(cachePath, `${JSON.stringify({
    cache_key: cacheKey,
    generated_at: new Date().toISOString(),
    prompt_version: PROMPT_VERSION,
    model: config.model,
    provider: config.provider,
    stage: config.stage || 'first_pass',
    votes: config.activeVotes || config.votes,
    unit_id: evidencePack.unit_id,
    observation_id: evidencePack.observation_id,
    label_flow_id: evidencePack.label_flow_id,
    result
  })}\n`, 'utf-8');
}

function normalizeEvidenceRefs(value, validIds) {
  const raw = evidenceRefValues(value);
  const refs = [];
  const invalidRefs = [];
  for (const item of raw) {
    const ref = String(item || '').trim();
    if (!ref) continue;
    if (validIds.has(ref)) refs.push(ref);
    else invalidRefs.push(ref);
  }
  return {
    valid: refs.length > 0,
    refs: uniqueValues(refs),
    invalidRefs: uniqueValues(invalidRefs)
  };
}

function evidenceRefValues(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') return [value];
  return [];
}

function normalizeNecessityLevel(value) {
  const text = String(value || '').trim().toLowerCase();
  if (['none', 'low', 'medium', 'high', 'critical'].includes(text)) return text;
  return '';
}

function normalizePositiveInteger(value, fallback) {
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? n : fallback;
}

function normalizeScaledThreshold(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 && n <= 1 ? n : fallback;
}

function normalizeEscalationPolicy(value) {
  const text = String(value || '').trim().toLowerCase();
  if (['risk_or_uncertain', 'none', 'all'].includes(text)) return text;
  return DEFAULT_ESCALATION_POLICY;
}

function normalizeWeight(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return DEFAULT_LLM_WEIGHT;
  return Math.max(0, Math.min(1, n));
}

function majorityValue(values = []) {
  if (!values.length) return '';
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.entries()).sort((a, b) => b[1] - a[1])[0]?.[0] || '';
}

function truncate(value, max) {
  return value.length > max ? `${value.slice(0, max)}...` : value;
}

module.exports = {
  judgeEvidencePacks,
  normalizeJudgeResult,
  normalizeJudgeBatchResult,
  aggregateVotes,
  resolveJudgeOptions,
  buildJudgeCacheKey,
  buildJudgePayload,
  buildJudgePromptBody,
  buildSharedTaskMemory,
  summarizeUsage,
  PROMPT_VERSION,
  DEFAULT_BATCH_SIZE,
  DEFAULT_VOTES,
  DEFAULT_LLM_WEIGHT
};
