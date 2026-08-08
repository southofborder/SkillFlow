/**
 * SkillFlow 一键全流程配置文件
 *
 * 新手只需要运行：
 *   node scripts/skillflow-pipeline.js --k 100
 *
 * 如果需要调整高级参数，改这里即可。命令行参数优先级高于本文件。
 */
module.exports = {
  paths: {
    // Project root. Usually no need to change.
    projectRoot: __dirname,

    // Output root prefix. The pipeline appends -k<n> automatically.
    resultsRoot: './results/clawhub-top',

    // ClawHub download entry. Currently reuses the skill-similarity-analyzer package.
    clawhubDownloader: './packages/skill-similarity-analyzer',

    // Compatibility alias for older configs; prefer clawhubDownloader for new configs.
    similarityAnalyzer: './packages/skill-similarity-analyzer',

    // FCG analyzer package.
    fcgAnalyzer: './packages/skill-fcg-analyzer',

    // DOE analyzer package.
    doeAnalyzer: './packages/skill-doe-analyzer'
  },

  clawhub: {
    // 下载热度排序。可选：downloads、stars、installs。
    sort: 'downloads',

    // ClawHub API 根地址。API 变更或代理时才需要改。
    apiBase: 'https://clawhub.ai/api/v1',

    // 网络请求超时，单位毫秒。
    timeoutMs: 30000,

    // 网络失败、429、5xx 时的重试次数。
    retries: 4,

    // 下载并发数。网络或磁盘压力大时可以调低。
    downloadConcurrency: 8,

    // 默认抓取所有公开 skill。改为 true 时只抓非 suspicious skills。
    nonSuspiciousOnly: true
  },

  similarity: {
    // Enable similarity grouping. Default false: FCG processes zips directly.
    enabled: false,

    // Similarity threshold. Higher values create stricter groups.
    threshold: 0.68,

    // Candidate count kept for optional LLM review per skill.
    topK: 5,

    // Similarity-stage LLM concurrency.
    llmConcurrency: 2,

    // Only applies when enabled=true.
    semanticLlm: false
  },

  fcg: {
    // FCG 分析模式。可选：quick、full、deep。
    mode: 'full',

    // FCG 分析并发数。
    concurrency: 4,

    // 是否忽略已有 FCG JSON 重新分析。
    refresh: false,

    // FCG scope. Without grouping, all processes zips directly; with grouping, grouped/ungrouped filters apply.
    scope: 'all',

    // 低置信度标签 LLM 辅助。默认关闭；开启后只在 generic/模糊字段/低证据标签时调用 LLM 生成弱证据候选标签。
    // 需要 LLM_API_KEY。生成的标签会标记 mode=llm_assisted、requires_review=true，供后续 DOE 区分强弱证据。
    labelLlmAssist: false,

    // 标签 LLM 辅助并发数。大批量运行时建议保持较低，避免 API 限流和成本失控。
    labelLlmConcurrency: 2,

    // 标签 LLM 辅助缓存文件。留空时由 FCG batch 使用 <root>/fcg/label-llm-cache.jsonl。
    labelLlmCache: '',

    // Markdown 语义门控（semantic gate）缓存文件。留空时固定到 <root>/fcg/semantic-gate-cache.jsonl，
    // 使其随结果目录持久化、可跨机器/CI 复用，避免每次重跑都对未变文档重新调用远程模型。
    // 设为 '0' 或 'false' 可禁用缓存。
    semanticGateCache: ''
  },

  doe: {
    // 默认在 FCG 后运行 DOE。DOE 默认使用 LLM judge，需要 LLM_API_KEY。
    enabled: true,

    // DOE 并发数。LLM judge 会放大请求量，默认保持较低。
    concurrency: 2,

    // 高分统计阈值。
    threshold: 0.7,

    // 默认使用 LLM judge；如需离线规则模式可改为 false。
    llmJudge: true,

    // 每次 LLM 请求包含的 assessment unit 数量。
    llmBatchSize: 4,

    // 首轮每个 assessment unit 的 LLM 投票数。默认 1，保证每个跨边界 unit 至少被 LLM 看一次。
    llmVotes: 1,

    // DOE LLM judge 请求并发数。
    llmConcurrency: 2,

    // 触发风险或不确定复判时使用的票数。
    llmEscalationVotes: 3,

    // 复判策略：risk_or_uncertain、none、all。
    llmEscalationPolicy: 'risk_or_uncertain',

    // 单个 LLM batch 的近似字符预算，超出后自动拆分。
    llmMaxBatchChars: 60000,

    // 单个 evidence pack 的上下文字符上限。仅当某个 pack 超过此值（否则会超长/超时、
    // 导致整个 skill 的 DOE 结果丢失）时才会触发裁剪；未超过的 pack 原样发送，判定不受影响。
    // 默认设得较高，使裁剪几乎不发生；裁剪时优先保留边界节点与路径首尾节点，并标记 requires_review。
    evidenceMaxPackChars: 100000,

    // 触发裁剪时，flow 路径首尾各保留多少个完整节点（边界节点始终保留）。
    evidencePathNodeWindow: 4,

    // 触发裁剪时，长自由文本字段的字符上限（仅裁剪路径生效）。
    evidenceMaxTextChars: 2000,

    // 触发裁剪时，冗长数组的元素上限（仅裁剪路径生效）。
    evidenceMaxArrayItems: 40,

    // 大 payload 自适应超时的上限（毫秒）。大请求按体积放大超时，避免误判超时而非裁剪内容。
    // 留空时默认取 4 倍基础超时。
    adaptiveTimeoutMaxMs: 0,

    // DOE LLM judge 缓存文件。留空时使用 <root>/doe/doe-llm-cache.jsonl。
    llmCache: '',

    // 是否忽略已有 DOE JSON 重新分析。
    refresh: false
  }
};
