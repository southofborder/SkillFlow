const { scoreExposure, resolveLabelSensitivity } = require('./exposure-scorer');
const {
  COMPONENT_KEYS,
  createNecessityContext,
  scoreNecessityBaseline,
  normalizeComponentScores,
  componentMin,
  weakestComponent
} = require('./necessity-baseline');
const { scoreGroupBaseline } = require('./group-baseline');
const { buildEvidencePack, createEvidencePackContext, transformsByNode } = require('./evidence-pack');
const { resolveLabelFlowPath } = require('./flow-path-utils');
const { judgeEvidencePacks, resolveJudgeOptions, summarizeUsage } = require('./llm-judge');
const { round3, clamp, categoryFromLabel, subtypeFromLabel } = require('./utils');
const { buildLabelDictionary, resolveLabel } = require('./label-resolver');

const DEFAULT_THRESHOLD = 0.7;
const DEFAULT_NECESSITY_THRESHOLD = 0.7;

function analyzeDoe(fcgJson, options = {}) {
  if (options.llmJudge) {
    throw new Error('analyzeDoe is rule-only and synchronous; use analyzeDoeAsync for LLM judge analysis');
  }
  return analyzeDoeRuleOnly(fcgJson, options);
}

async function analyzeDoeAsync(fcgJson, options = {}) {
  const llmJudge = options.llmJudge !== false;
  if (!llmJudge) return analyzeDoeRuleOnly(fcgJson, options);

  const result = analyzeDoeRuleOnly(fcgJson, { ...options, keepInternal: true });
  const judgeConfig = resolveJudgeOptions(options);
  if (!judgeConfig.llmClient && !String(judgeConfig.apiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required for DOE LLM judge; use --no-llm-judge for rule-only analysis');
  }
  const packs = selectRepresentativePacks(result.assessments);
  const assessmentByUnit = new Map(result.assessments
    .filter(assessment => assessment._evidence_pack?.unit_id)
    .map(assessment => [assessment._evidence_pack.unit_id, assessment]));
  const judgeResults = await judgeEvidencePacks(packs, {
    ...options,
    ...judgeConfig,
    assessmentByUnit,
    // task_memory 现在由 FCG 在 skill 级聚合,judge 需要 fcg 与共享 context。
    fcg: fcgJson,
    evidencePackContext: result._evidencePackContext || null
  });
  applyLlmJudgements(result, judgeResults, judgeConfig);
  stripInternalFields(result);
  return result;
}

// 送审去重:按 _dedup_key 分组,每组选 assessment_confidence 最高者为代表,只送代表的
// pack 给 LLM。其余成员记下代表 unit_id,回填时复用代表判定 —— 同 (observation, label,
// transform 签名) 的 necessity 判断等价,送一条即可,省约 70% 的 LLM 调用。
function selectRepresentativePacks(assessments = []) {
  const groups = new Map(); // dedup_key -> assessment[]
  for (const a of assessments) {
    if (!a._evidence_pack?.unit_id) continue;
    const key = a._dedup_key || a._evidence_pack.unit_id;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(a);
  }
  const repPacks = [];
  for (const members of groups.values()) {
    members.sort((x, y) =>
      (Number(y.assessment_confidence || 0) - Number(x.assessment_confidence || 0)) ||
      (Number(y.doe_score || 0) - Number(x.doe_score || 0)) || // tie-break: 风险高者优先
      String(x._evidence_pack.unit_id).localeCompare(String(y._evidence_pack.unit_id))); // 稳定
    const rep = members[0];
    repPacks.push(rep._evidence_pack);
    rep._dedup_role = 'representative';
    for (const m of members) {
      m._dedup_representative_unit_id = rep._evidence_pack.unit_id;
      m._dedup_group_size = members.length;
    }
  }
  return repPacks;
}

function analyzeDoeRuleOnly(fcgJson, options = {}) {
  validateFcg(fcgJson);
  const security = fcgJson.security_profile || {};
  const labelFlows = security.label_flows || [];
  const observations = security.observations || [];
  const nodeProfiles = security.node_profiles || [];
  // Normalize each label_flow's label ONCE at this single boundary: resolve the
  // FCG label_dictionary reference (>= v5.0) into an inline label, or keep the
  // inline label (<= v4.9). Every downstream consumer (exposure/necessity/group
  // /evidence-pack/confidence) reads labelFlow.label unchanged — the data flow
  // is identical to before, only the source of the label is now dual-mode.
  // Misses (a label_id with no dictionary entry) are surfaced as warnings, never
  // silently dropped.
  const labelDictionary = buildLabelDictionary(security);
  const labelMisses = [];
  const labelFlowById = new Map(labelFlows.map(flow => {
    const resolved = resolveLabel(flow, labelDictionary, (m) => labelMisses.push(m));
    // Only attach when we actually resolved something via the dictionary; if the
    // flow already had an inline label this returns the same object (no-op).
    const normalized = flow.label === resolved ? flow : { ...flow, label: resolved };
    return [flow.label_flow_id, normalized];
  }));
  const profileByNodeId = new Map(nodeProfiles.map(profile => [profile.node_id, profile]));
  const threshold = normalizeThreshold(options.threshold);
  const necessityThreshold = normalizeThreshold(options.necessityThreshold ?? DEFAULT_NECESSITY_THRESHOLD);
  const groupBaseline = options.groupBaseline || null;
  const evidencePackContext = createEvidencePackContext(fcgJson);
  const necessityContext = createNecessityContext(fcgJson);
  const warnings = [];
  for (const miss of labelMisses) {
    warnings.push({
      kind: 'label_dictionary.miss',
      label_flow_id: miss.label_flow_id,
      label_id: miss.label_id
    });
  }
  const assessments = [];

  for (const observation of observations) {
    for (const labelFlowId of observation.label_flow_ids || []) {
      const labelFlow = labelFlowById.get(labelFlowId);
      if (!labelFlow) {
        warnings.push({
          kind: 'missing_label_flow',
          observation_id: observation.observation_id || '',
          label_flow_id: labelFlowId
        });
        continue;
      }
      const nodeProfile = profileByNodeId.get(observation.node_id) || {};
      const group = scoreGroupBaseline({ observation, labelFlow, groupBaseline });
      const exposure = scoreExposure({ labelFlow, observation });
      const necessity = scoreNecessityBaseline({
        fcg: fcgJson,
        observation,
        labelFlow,
        nodeProfile,
        groupSupport: group,
        context: necessityContext
      });
      const doeScore = exposure.boundary_crossed
        ? calculateDoeScore(exposure.exposure_score, necessity.necessity_score, group.baseline_adjustment)
        : 0;
      const potentialDoe = Boolean(exposure.boundary_crossed && necessity.necessity_score < necessityThreshold);
      const label = labelFlow.label || {};
      const evidence = [
        ...prefixEvidence(exposure.evidence, 'exposure'),
        ...prefixEvidence(necessity.evidence, 'necessity'),
        ...prefixEvidence(group.evidence, 'baseline')
      ];
      const labelRequiresReview = Boolean(label.requires_review || label.mode === 'llm_assisted');
      const flowRequiresReview = Boolean(labelFlow.truncated);
      if (labelRequiresReview) {
        evidence.push({
          kind: 'label.requires_review',
          reason: `label mode=${label.mode || ''}; evidence_kind=${label.evidence_kind || ''}`
        });
      }
      if (flowRequiresReview) {
        evidence.push({
          kind: 'label_flow.requires_review',
          reason: 'label flow was explicitly truncated by FCG transfer limits'
        });
      }

      const llmGate = shouldJudgeAssessmentWithLlm({ label, observation, exposure, potentialDoe });
      const assessment = {
        assessment_id: `doe_${String(assessments.length + 1).padStart(6, '0')}`,
        observation_id: observation.observation_id || '',
        label_flow_id: labelFlow.label_flow_id || labelFlowId,
        label: label.label || [label.category, label.subtype].filter(Boolean).join('.') || 'unknown',
        label_category: label.category || categoryFromLabel(label.label),
        label_subtype: label.subtype || subtypeFromLabel(label.label),
        observation_node_id: observation.node_id || '',
        observation_node_name: observation.node_name || '',
        doe_score: doeScore,
        exposure_score: exposure.exposure_score,
        boundary_crossed: Boolean(exposure.boundary_crossed),
        boundary_basis: exposure.boundary_basis || [],
        exposure_tier: exposure.exposure_tier || '',
        necessity_score: necessity.necessity_score,
        rule_necessity_score: necessity.necessity_score,
        llm_necessity_score: null,
        component_scores: necessity.component_scores,
        rule_component_scores: necessity.component_scores,
        local_necessity: necessity.local_necessity,
        global_necessity: necessity.global_necessity,
        baseline_adjustment: group.baseline_adjustment,
        assessment_confidence: assessmentConfidence({ labelFlow, observation, exposure, necessity }),
        necessity_basis: necessity.necessity_basis,
        high_score: doeScore >= threshold,
        potential_doe: potentialDoe,
        requires_review: potentialDoe || doeScore >= threshold || labelRequiresReview || flowRequiresReview,
        evidence,
        _llm_context: { labelFlow, observation, exposure, ruleNecessity: necessity },
        _llm_gate: llmGate,
        // 送审去重键:同一 observation(已绑定具体 sink 边界)下,necessity 判定等价的多条
        // 上游路径归为一组,只送一条代表给 LLM。键必须是 necessity 判定的充分统计量——凡
        // necessity 可能依赖的维度都进键,否则会把判定其实不同的流错误合并、只送一条代表,
        // 产生安全误判。四段维度:
        //   observation_id —— 绑定具体 sink 边界(receiver/retention/trust)。
        //   label —— 数据的敏感类目。
        //   transform_seq —— 有序 + 计次的 transform 序列(见 transformSequence),区分
        //     「脱敏在外发前/后」「脱敏一/多次」。
        //   origin_class —— 数据来源的信任语义等价类(见 originClass),区分「用户自己输入
        //     回给用户」vs「第三方抓取的数据发同一汇点」——两者 necessity 不同。
        _dedup_key: `${observation.observation_id || ''}|${label.label || [label.category, label.subtype].filter(Boolean).join('.')}|${transformSequence(labelFlow, evidencePackContext)}|${originClass(labelFlow, evidencePackContext)}`
      };
      if (options.keepInternal && llmGate.eligible) {
        assessment._evidence_pack = buildEvidencePack({ fcg: fcgJson, observation, labelFlow, nodeProfile, exposure, context: evidencePackContext });
      }
      assessments.push(assessment);
    }
  }

  const result = {
    version: '0.3',
    input_fcg: options.inputFcg || '',
    assessment_unit: 'observation_label_flow',
    assessments,
    warnings,
    statistics: {
      assessment_count: assessments.length,
      high_score_count: assessments.filter(item => item.doe_score >= threshold).length,
      requires_review_count: assessments.filter(item => item.requires_review).length,
      warning_count: warnings.length,
      threshold,
      necessity_threshold: necessityThreshold,
      boundary_crossing_count: assessments.filter(item => item.boundary_crossed).length,
      potential_doe_count: assessments.filter(item => item.potential_doe).length,
      llm_eligible_count: assessments.filter(item => item._llm_gate?.eligible).length,
      llm_skipped_count: assessments.filter(item => item._llm_gate && !item._llm_gate.eligible).length,
      llm_judge_enabled: false
    }
  };
  if (!options.keepInternal) stripInternalFields(result);
  else result._evidencePackContext = evidencePackContext;
  return result;
}

function applyLlmJudgements(result, judgeResults, judgeConfig) {
  const threshold = result.statistics.threshold;
  const necessityThreshold = result.statistics.necessity_threshold ?? DEFAULT_NECESSITY_THRESHOLD;
  const llmWeight = judgeConfig.llmWeight;
  const ruleWeight = 1 - llmWeight;
  let llmJudgedCount = 0;
  let llmReviewCount = 0;
  let cacheHitCount = 0;
  let escalatedCount = 0;
  let llmSkippedCount = 0;

  for (const assessment of result.assessments) {
    const context = assessment._llm_context || {};
    const pack = assessment._evidence_pack;
    if (!pack && assessment._llm_gate && !assessment._llm_gate.eligible) {
      llmSkippedCount += 1;
      assessment.llm_judge = {
        skipped: true,
        skip_reason: assessment._llm_gate.reason,
        gate: {
          label_sensitivity: assessment._llm_gate.label_sensitivity,
          boundary_risk: assessment._llm_gate.boundary_risk,
          boundary_crossed: assessment._llm_gate.boundary_crossed
        }
      };
      continue;
    }
    // 送审去重回填:代表自身用本 unit 判定;非代表(未送审)复用同组代表的判定
    // —— 同 (observation, label, transform 签名) necessity 等价。规则分仍是本单元自己的,
    // 仅 LLM 分共享代表结果。代表判定也缺失(如代表送审失败)才落 requires_review。
    const repUnitId = assessment._dedup_representative_unit_id;
    const judgement = (pack && judgeResults.get(pack.unit_id))
      || (repUnitId && judgeResults.get(repUnitId))
      || null;
    if (!judgement) {
      result.warnings.push({
        kind: 'llm_judge.missing_result',
        assessment_id: assessment.assessment_id,
        observation_id: assessment.observation_id,
        label_flow_id: assessment.label_flow_id
      });
      assessment.requires_review = true;
      continue;
    }
    const isDedupMember = !(pack && judgeResults.get(pack.unit_id)) && Boolean(repUnitId);

    llmJudgedCount += 1;
    if (judgement.cache_hit) cacheHitCount += 1;
    if (judgement.escalated || judgement.stage === 'escalation') escalatedCount += 1;
    if (judgement.requires_review) llmReviewCount += 1;

    const ruleComponents = assessment.rule_component_scores || {};
    const llmComponents = judgement.component_scores || {};
    const componentScores = combineComponentScores({ ruleComponents, llmComponents, llmWeight });
    const necessityScore = componentMin(componentScores);
    assessment.llm_necessity_score = round3(judgement.llm_necessity_score ?? componentMin(llmComponents));
    assessment.component_scores = componentScores;
    assessment.necessity_score = necessityScore;
    assessment.necessity_basis = weakestComponent(componentScores);
    assessment.local_necessity = {
      action_input_need: componentScores.action_input_need,
      receiver_semantic_need: componentScores.receiver_semantic_need,
      score: round3(Math.min(componentScores.action_input_need, componentScores.receiver_semantic_need))
    };
    assessment.global_necessity = {
      task_need: componentScores.task_need,
      score: componentScores.task_need
    };
    assessment.doe_score = assessment.boundary_crossed
      ? calculateDoeScore(
        assessment.exposure_score,
        assessment.necessity_score,
        assessment.baseline_adjustment
      )
      : 0;
    assessment.high_score = assessment.doe_score >= threshold;
    assessment.potential_doe = Boolean(assessment.boundary_crossed && assessment.necessity_score < necessityThreshold);
    assessment.llm_judge = {
      model: judgement.model,
      provider: judgement.provider,
      prompt_version: judgement.prompt_version,
      vote_count: judgement.vote_count,
      stage: judgement.stage || 'first_pass',
      escalated: Boolean(judgement.escalated || judgement.stage === 'escalation'),
      cache_hit: Boolean(judgement.cache_hit),
      cache_stage: judgement.cache_stage || '',
      llm_weight: llmWeight,
      rule_weight: ruleWeight,
      // 送审去重溯源:representative=本组送审的代表,member=复用了代表判定(未单独送审)。
      // key 暴露分组维度(transform_seq / origin_class),供审计「为何这几条被合并」。
      dedup: {
        role: isDedupMember ? 'member' : 'representative',
        representative_unit_id: repUnitId || (pack ? pack.unit_id : ''),
        group_size: assessment._dedup_group_size || 1,
        key: dedupKeyBreakdown(assessment._dedup_key)
      },
      required_for_task: judgement.required_for_task,
      necessity_level: judgement.necessity_level,
      component_scores: judgement.component_scores || {},
      component_judgements: judgement.component_judgements || {},
      evidence_refs: {
        supporting: judgement.supporting_evidence_ids || [],
        contradicting: judgement.contradicting_evidence_ids || [],
        invalid: judgement.invalid_evidence_ids || []
      },
      reasoning_summary: judgement.reasoning_summary || '',
      disagreement: judgement.disagreement,
      votes: (judgement.votes || []).map(vote => ({
        component_scores: vote.component_scores || {},
        llm_necessity_score: vote.llm_necessity_score,
        necessity_level: vote.necessity_level,
        required_for_task: vote.required_for_task,
        supporting_evidence_ids: vote.supporting_evidence_ids || [],
        contradicting_evidence_ids: vote.contradicting_evidence_ids || []
      }))
    };
    assessment.evidence.push({
      kind: 'necessity.llm_judge',
      score: assessment.llm_necessity_score,
      reason: judgement.reasoning_summary || '',
      component_scores: judgement.component_scores || {},
      supporting_evidence_ids: judgement.supporting_evidence_ids || [],
      contradicting_evidence_ids: judgement.contradicting_evidence_ids || []
    });
    if ((judgement.invalid_evidence_ids || []).length) {
      result.warnings.push({
        kind: 'llm_judge.invalid_evidence_refs',
        assessment_id: assessment.assessment_id,
        invalid_evidence_ids: judgement.invalid_evidence_ids
      });
    }
    if (judgement.disagreement > 0.35) {
      result.warnings.push({
        kind: 'llm_judge.vote_disagreement',
        assessment_id: assessment.assessment_id,
        disagreement: judgement.disagreement
      });
    }
    const evidenceRequiresReview = assessment.evidence.some(item => (
      item.kind === 'label.requires_review' ||
      item.kind === 'label_flow.requires_review'
    ));
    assessment.requires_review = assessment.potential_doe || assessment.high_score || evidenceRequiresReview || Boolean(judgement.requires_review);
    assessment.assessment_confidence = assessmentConfidence({
      labelFlow: context.labelFlow,
      observation: context.observation,
      exposure: context.exposure,
      necessity: { necessity_basis: assessment.necessity_basis },
      llmJudge: judgement
    });
  }

  result.statistics.high_score_count = result.assessments.filter(item => item.doe_score >= threshold).length;
  result.statistics.requires_review_count = result.assessments.filter(item => item.requires_review).length;
  result.statistics.boundary_crossing_count = result.assessments.filter(item => item.boundary_crossed).length;
  result.statistics.potential_doe_count = result.assessments.filter(item => item.potential_doe).length;
  result.statistics.warning_count = result.warnings.length;
  result.statistics.llm_judge_enabled = true;
  result.statistics.llm_judged_count = llmJudgedCount;
  result.statistics.llm_eligible_count = result.assessments.filter(item => item._llm_gate?.eligible).length;
  // 送审去重统计:eligible 单元总数 vs 实际送 LLM 的代表数。
  const dedupTotal = result.assessments.filter(item => item._evidence_pack?.unit_id).length;
  const dedupSent = new Set(result.assessments
    .filter(item => item._dedup_role === 'representative')
    .map(item => item._evidence_pack.unit_id)).size;
  result.statistics.llm_dedup_units_total = dedupTotal;
  result.statistics.llm_dedup_units_sent = dedupSent;
  result.statistics.llm_dedup_saved = dedupTotal - dedupSent;
  result.statistics.llm_dedup_ratio = dedupTotal ? round3((dedupTotal - dedupSent) / dedupTotal) : 0;
  result.statistics.llm_skipped_count = llmSkippedCount;
  result.statistics.llm_review_count = llmReviewCount;
  result.statistics.llm_cache_hit_count = cacheHitCount;
  result.statistics.llm_first_pass_count = judgeResults.judge_stats?.first_pass_count ?? llmJudgedCount;
  result.statistics.llm_escalated_count = judgeResults.judge_stats?.escalated_count ?? escalatedCount;
  result.statistics.llm_timeout_split_count = judgeResults.judge_stats?.timeout_split_count ?? 0;
  result.statistics.llm_fallback_count = judgeResults.judge_stats?.fallback_count ?? 0;
  if (judgeResults.judge_stats?.fallback_units?.length) {
    result.statistics.llm_fallback_units = judgeResults.judge_stats.fallback_units;
  }
  result.statistics.llm_task_memory_node_count = judgeResults.judge_stats?.task_memory_node_count ?? 0;
  result.statistics.llm_task_memory_doc_source_count = judgeResults.judge_stats?.task_memory_doc_source_count ?? 0;
  // Endpoint-reported token usage (no extra API cost — read from response bodies
  // we already receive). prompt_cache_hit_ratio quantifies the stable-prefix
  // caching win; a drop signals a broken cache prefix. Absent for --no-llm-judge
  // or when a custom llmClient returns no usage envelope.
  const usageSummary = summarizeUsage(judgeResults.judge_stats?.usage);
  if (usageSummary) result.statistics.llm_token_usage = usageSummary;
  result.statistics.llm_model = judgeConfig.model;
  result.statistics.llm_votes = judgeConfig.votes;
  result.statistics.llm_escalation_votes = judgeConfig.escalationVotes;
  result.statistics.llm_escalation_policy = judgeConfig.escalationPolicy;
  result.statistics.llm_concurrency = judgeConfig.concurrency;
  result.statistics.llm_batch_size = judgeConfig.batchSize;
  result.statistics.llm_weight = judgeConfig.llmWeight;
}

function validateFcg(fcgJson) {
  if (!fcgJson || typeof fcgJson !== 'object') throw new Error('Invalid FCG JSON: expected object');
  const security = fcgJson.security_profile;
  if (!security || typeof security !== 'object') throw new Error('Invalid FCG JSON: missing security_profile');
  if (!Array.isArray(security.label_flows)) throw new Error('Invalid FCG JSON: security_profile.label_flows must be an array');
  if (!Array.isArray(security.observations)) throw new Error('Invalid FCG JSON: security_profile.observations must be an array');
  if (!Array.isArray(security.node_profiles)) throw new Error('Invalid FCG JSON: security_profile.node_profiles must be an array');
}

function assessmentConfidence({ labelFlow = {}, observation = {}, exposure = {}, necessity = {}, llmJudge = null }) {
  const label = labelFlow.label || {};
  let confidence = 0.75;
  confidence *= Number(labelFlow.confidence || 0.7);
  confidence *= Number(label.confidence || 0.8);
  if (label.requires_review || label.mode === 'llm_assisted') confidence *= 0.65;
  if (labelFlow.truncated) confidence *= 0.5;
  if (observation.ambiguous_action_order) confidence *= 0.85;
  if (necessity.necessity_basis === 'task_need') confidence *= 0.9;
  if (llmJudge?.disagreement > 0.35) confidence *= 0.7;
  if ((llmJudge?.invalid_evidence_ids || []).length) confidence *= 0.75;
  if (exposure.exposure_score <= 0.35) confidence *= 0.9;
  return clamp(round3(confidence));
}

// 送审去重的 transform 维度签名:沿 resolved node_path 顺序、逐节点展开该节点上发生的
// real transform 类型(不去重、不排序),join('>')。空 = 'none'。
//   - 有序:天然区分「脱敏在外发前 vs 后」(redact>send vs send>redact 键不同)。
//   - 计次:天然区分「脱敏一次 vs 多次」(redact vs redact>redact)。
// 顺 parent 链取回 transform 事件:序列化后 labelFlow.filter_events 恒为 [],真身集中在
// provenance_graph.events.filtering,transformsByNode 顺 parent 链经 filterEventById 累积
// (与 evidence-pack 同源);再用 resolveLabelFlowPath 的 node_path 定序展开。node_path 已按
// P1 裁到 origin_node,故裁掉的前缀节点不在路径内,其 transform 也不会被展开进签名。
// 若签名恒为 'none' 会把「已脱敏后外发」与「未脱敏外发」错误合并成一组,产生安全误判。
function transformSequence(labelFlow = {}, context = null) {
  const flowById = context?.flowPathContext?.flowById || new Map();
  const filterEventById = context?.filterEventById || new Map();
  const byNode = transformsByNode(labelFlow, flowById, filterEventById);
  if (!byNode.size) return 'none';
  const resolved = resolveLabelFlowPath(labelFlow, context?.flowPathContext || {});
  const seq = [];
  for (const nodeId of resolved.node_path || []) {
    for (const t of byNode.get(nodeId) || []) {
      if (t && t.type) seq.push(t.type);
    }
  }
  return seq.length ? seq.join('>') : 'none';
}

// 送审去重的 origin(数据来源)维度签名:origin 节点的「安全语义等价类」,而非其 node_id。
// 两个来源节点若 trust_boundary + data_surface 相同,它们引入的数据对 necessity 可互换,
// 应留在同一 dedup 组;直接用 node_id 会令每个来源自成一组、dedup 退化到近乎无去重。
//   origin_class = `${trust_boundary}/${data_surface}`
// 不纳入 node_roles:role 是「节点能做什么」的全局能力,非「本 label 从此处进入」的来源
// 语义,纳入会因角色排列过度切分。origin_node 实测 100% 填充且必有 profile,故 'unknown'
// 回退纯为防御(缺 profile 时不退化成 node_id,避免过度切分)。
function originClass(labelFlow = {}, context = null) {
  const originNodeId = labelFlow.origin_node || labelFlow.label?.origin_node || '';
  const profile = context?.profileByNodeId?.get(originNodeId);
  if (!profile) return 'unknown';
  const trustBoundary = profile.trust_boundary || 'unknown';
  const dataSurface = profile.data_surface || 'unknown';
  return `${trustBoundary}/${dataSurface}`;
}

// 拆解 _dedup_key(`obs|label|transform_seq|origin_class`)为可审计字段。仅取 dedup 独有的
// transform_seq / origin_class(obs/label 已是 assessment 顶层字段,不重复)。
function dedupKeyBreakdown(dedupKey = '') {
  const parts = String(dedupKey || '').split('|');
  return {
    transform_seq: parts[2] ?? 'none',
    origin_class: parts[3] ?? 'unknown'
  };
}

function prefixEvidence(items = [], prefix = '') {
  return (items || []).map(item => {
    const kind = item.kind || prefix;
    return {
      ...item,
      kind: kind.startsWith(`${prefix}.`) ? kind : `${prefix}.${kind}`
    };
  });
}

function normalizeThreshold(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return DEFAULT_THRESHOLD;
  return clamp(n);
}

function calculateDoeScore(exposureScore, necessityScore, baselineAdjustment) {
  return clamp(round3((Number(exposureScore || 0) * (1 - Number(necessityScore || 0))) + Number(baselineAdjustment || 0)));
}

function combineComponentScores({ ruleComponents = {}, llmComponents = {}, llmWeight = 0.7 }) {
  const ruleWeight = 1 - llmWeight;
  return normalizeComponentScores(COMPONENT_KEYS.reduce((acc, key) => {
    const ruleScore = Number(ruleComponents[key] ?? 0);
    const llmScore = Number(llmComponents[key] ?? ruleScore);
    acc[key] = clamp(round3((llmWeight * llmScore) + (ruleWeight * ruleScore)));
    return acc;
  }, {}));
}

function stripInternalFields(result) {
  delete result._evidencePackContext;
  for (const assessment of result.assessments || []) {
    delete assessment._llm_context;
    delete assessment._evidence_pack;
    delete assessment._llm_gate;
    delete assessment._dedup_key;
    delete assessment._dedup_role;
    delete assessment._dedup_group_size;
    delete assessment._dedup_representative_unit_id;
  }
}

// LLM send gate — RECALL-FIRST (necessity redesign N: rules should not make the
// final call on anything suspicious; hand it to the LLM). A boundary-crossing unit
// is sent when EITHER:
//   (a) the label is HIGH/critical sensitivity — sent UNCONDITIONALLY, even if the
//       rules judged it necessary. High-stakes categories (credentials, secrets,
//       financial, health, pii, ...) get LLM backstop review so a rule misjudgment
//       cannot silently clear a real leak; OR
//   (b) the label is MEDIUM sensitivity AND the recall-first rules flagged it
//       potential_doe (suspicious). Medium stakes only escalate when suspicious.
// low sensitivity (generic_data) is never sent — negligible data-minimization stakes.
//
// The rules are recall-first: the structural signals (transform participation /
// schema membership / declaration coverage / receiver×category) sharpen WHICH units
// look suspicious, but the LLM makes the real call on everything sensitive. Dedup
// (obs|label|transform_seq|origin_class) collapses the corpus 4431 boundary-crossing
// units to ~832 unique decision units, keeping volume controlled.
// boundary_risk is retained in the return for transparency but no longer gates.
function shouldJudgeAssessmentWithLlm({ label = {}, observation = {}, exposure = {}, potentialDoe = false }) {
  const sensitivity = resolveLabelSensitivity(label);
  const sensitivityRank = SENSITIVITY_RANK[sensitivity] || 0;
  const boundaryRisk = Number(exposure.boundary_risk || 0);
  const boundaryCrossed = Boolean(exposure.boundary_crossed);
  const highSensitive = sensitivityRank >= SENSITIVITY_RANK.high;
  const mediumSensitive = sensitivityRank >= SENSITIVITY_RANK.medium;
  const eligible = Boolean(boundaryCrossed && (highSensitive || (mediumSensitive && potentialDoe)));
  let reason;
  if (eligible) {
    reason = highSensitive ? 'high_sensitivity_backstop' : 'medium_sensitivity_potential_doe';
  } else if (!boundaryCrossed) {
    reason = 'no_boundary_crossed';
  } else if (!mediumSensitive) {
    reason = `label_sensitivity_${sensitivity}`;
  } else {
    reason = 'medium_sensitivity_not_potential_doe';
  }
  return {
    eligible,
    reason,
    label_sensitivity: sensitivity,
    boundary_risk: round3(boundaryRisk),
    boundary_crossed: boundaryCrossed,
    trust_boundary: observation.boundary?.trust_boundary || '',
    receiver_scope: observation.boundary?.receiver_scope || ''
  };
}

const SENSITIVITY_RANK = {
  low: 1,
  medium: 2,
  high: 3,
  critical: 4
};

module.exports = {
  analyzeDoe,
  analyzeDoeAsync,
  shouldJudgeAssessmentWithLlm,
  DEFAULT_THRESHOLD
};
