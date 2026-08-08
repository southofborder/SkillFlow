const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const AdmZip = require('adm-zip');
const {
  normalizeSimilarityResult
} = require('../../../shared/llm-utils.cjs');

const VERSION = '1.0.0';
const DEFAULT_THRESHOLD = 0.68;
const DEFAULT_TOP_K = 20;
const DEFAULT_EXHAUSTIVE_PAIR_LIMIT = 1_000_000;
const DEFAULT_CANDIDATE_BUCKET_LIMIT = 450;
const DEFAULT_OVERSIZED_BUCKET_WINDOW = 8;
const DEFAULT_MAX_CANDIDATE_PAIRS = 1_200_000;

const STOPWORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can', 'for', 'from', 'has',
  'if', 'in', 'into', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this',
  'to', 'use', 'used', 'using', 'when', 'with', 'you', 'your', 'skill',
  'skills', 'agent', 'assistant', 'user', 'users', 'should', 'must', 'will',
  'may', 'help', 'helps', 'based', 'provide', 'provides'
]);

const COMMON_CANDIDATE_TOKENS = new Set([
  'api', 'app', 'apps', 'bot', 'cli', 'codex', 'content', 'custom', 'data',
  'file', 'files', 'helper', 'helpers', 'manager', 'management', 'mcp',
  'project', 'projects', 'prompt', 'prompts', 'service', 'services', 'system',
  'systems', 'task', 'tasks', 'tool', 'tools', 'utility', 'utilities',
  'workflow', 'workflows'
]);

const ACTION_PATTERNS = [
  ['analyze', /\b(analy[sz]e|analysis|inspect|diagnose|evaluate|assess|audit)\b|分析|诊断|评估|审计/g],
  ['generate', /\b(generate|create|produce|build|make|compose)\b|生成|创建|构建|制作/g],
  ['query', /\b(query|search|find|lookup|retrieve|fetch|get|list)\b|查询|搜索|查找|检索|获取|列出/g],
  ['visualize', /\b(visuali[sz]e|chart|plot|graph|dashboard|diagram|render)\b|可视化|图表|绘图|看板/g],
  ['transform', /\b(transform|convert|format|normalize|clean|migrate)\b|转换|格式化|清洗|迁移/g],
  ['summarize', /\b(summari[sz]e|brief|digest|abstract|report)\b|总结|摘要|报告/g],
  ['translate', /\b(translate|locali[sz]e|polish|rewrite)\b|翻译|润色|改写/g],
  ['test', /\b(test|validate|verify|check|lint|qa)\b|测试|验证|校验|检查/g],
  ['monitor', /\b(monitor|track|observe|alert|notify)\b|监控|跟踪|告警|通知/g],
  ['design', /\b(design|architect|model|schema|prototype)\b|设计|建模|原型/g],
  ['extract', /\b(extract|parse|classify|tag|label)\b|提取|解析|分类|标注/g],
  ['compare', /\b(compare|diff|match|similarity|dedupe)\b|比较|对比|相似|去重/g],
  ['execute', /\b(run|execute|invoke|call|deploy|install)\b|运行|执行|调用|部署|安装/g],
  ['write', /\b(write|save|store|append|update|edit|record)\b|写入|保存|存储|更新|编辑|记录/g]
];

const PLATFORM_PATTERNS = [
  ['openai', /\b(openai|chatgpt|gpt)\b/g],
  ['anthropic', /\b(anthropic|claude)\b/g],
  ['dashscope', /\b(dashscope|qwen|aliyun|alibaba)\b|通义|阿里/g],
  ['github', /\b(github|gitlab|git)\b/g],
  ['database', /\b(mysql|postgres|postgresql|sqlite|mongodb|redis|database|sql|db)\b|数据库/g],
  ['spreadsheet', /\b(excel|spreadsheet|sheet|csv|xlsx|google sheets)\b|表格/g],
  ['document', /\b(pdf|docx|markdown|md|document|docs|notion)\b|文档/g],
  ['browser', /\b(browser|playwright|selenium|webpage|html|crawler|scraper)\b|浏览器|网页|爬虫/g],
  ['feishu', /\b(feishu|lark|bitable)\b|飞书|多维表/g],
  ['wechat', /\b(wechat|wecom|wx)\b|微信|企业微信/g],
  ['slack', /\b(slack|discord|telegram)\b/g],
  ['jira', /\b(jira|linear|trello)\b/g],
  ['aws', /\b(aws|s3|lambda|cloudwatch)\b/g],
  ['azure', /\b(azure|microsoft)\b/g],
  ['docker', /\b(docker|kubernetes|k8s|container)\b/g],
  ['frontend', /\b(react|vue|angular|css|tailwind|frontend|ui)\b/g],
  ['python', /\b(python|pandas|numpy|matplotlib)\b/g],
  ['nodejs', /\b(node|nodejs|javascript|typescript|npm)\b/g],
  ['image', /\b(image|photo|picture|png|jpg|jpeg|svg|vision)\b|图片|图像/g],
  ['audio', /\b(audio|speech|voice|tts|stt|music)\b|音频|语音|音乐/g],
  ['finance', /\b(stock|equity|trade|trading|portfolio|finance|financial|quant)\b|股票|金融|量化/g]
];

const IO_PATTERNS = [
  ['data', /\b(data|dataset|records?|items?)\b|数据/g],
  ['file', /\b(files?|path|directory|folder)\b|文件|目录/g],
  ['url', /\b(url|link|uri|endpoint|website)\b|链接|网址/g],
  ['text', /\b(text|content|message|prompt)\b|文本|内容|消息/g],
  ['image', /\b(image|photo|picture|screenshot)\b|图片|截图/g],
  ['audio', /\b(audio|voice|speech|sound)\b|音频|语音/g],
  ['video', /\b(video|movie|clip)\b|视频/g],
  ['table', /\b(table|spreadsheet|csv|xlsx|row|column)\b|表格|行|列/g],
  ['database', /\b(database|schema|sql|query|record)\b|数据库|记录/g],
  ['report', /\b(report|summary|dashboard|chart)\b|报告|摘要|图表/g],
  ['credential', /\b(token|secret|key|credential|password|env)\b|密钥|令牌|凭据|密码/g],
  ['user_info', /\b(user|customer|profile|email|phone|address|pii)\b|用户|客户|邮箱|电话|地址/g],
  ['code', /\b(code|source|function|class|api)\b|代码|函数|接口/g]
];

const POLARITY_PATTERNS = [
  ['deny', /\b(do\s+not|don't|does\s+not|must\s+not|should\s+not|cannot|can't|never|avoid|forbid|forbidden|prohibit|without|not)\b|禁止|不要|避免|不得|不能|不可|不允许|不喜欢/g],
  ['require', /\b(must|required|require|requires|always|need|needs|shall)\b|必须|需要|始终|务必|要求/g],
  ['only', /\b(only|unless|except|exclusive|solely)\b|仅|只|只有|除非|除了/g],
  ['allow', /\b(allow|allows|allowed|can|may|support|supports|enable|like|prefer|use)\b|允许|可以|支持|启用|喜欢|偏好|使用/g]
];

const POLARITY_ACTION_PATTERNS = [
  ['send', /\b(send|upload|post|share|export|transmit|publish)\b|发送|上传|外发|分享|导出|发布/g],
  ['read', /\b(read|access|load|inspect|retrieve|fetch|get|query)\b|读取|访问|加载|查看|获取|查询/g],
  ['write', /\b(write|save|store|append|update|edit|record|persist)\b|写入|保存|存储|更新|编辑|记录/g],
  ['execute', /\b(run|execute|invoke|call|deploy|install)\b|运行|执行|调用|部署|安装/g],
  ['like', /\b(like|prefer|enjoy)\b|喜欢|偏好/g],
  ['watch', /\b(watch|view|see|television|tv)\b|观看|看电视|电视/g],
  ...ACTION_PATTERNS
];

const POLARITY_WORDS = new Set([
  'do', 'not', 'dont', "don't", 'does', 'must', 'should', 'cannot', 'cant', "can't",
  'never', 'avoid', 'forbid', 'forbidden', 'prohibit', 'without', 'only', 'unless',
  'except', 'allow', 'allows', 'allowed', 'can', 'may', 'support', 'supports',
  'enable', 'required', 'require', 'requires', 'always', 'need', 'needs', 'shall',
  'like', 'prefer', 'enjoy'
]);

const POLARITY_HIGH_RISK_TERMS = new Set([
  'credential', 'credentials', 'secret', 'secrets', 'token', 'tokens', 'key', 'keys',
  'password', 'passwords', 'env', 'external', 'externally', 'api', 'user', 'users',
  'customer', 'customers', 'profile', 'email', 'phone', 'address', 'pii',
  '凭据', '密钥', '令牌', '密码', '用户', '客户', '邮箱', '电话', '地址', '外部', '外发'
]);

function printUsage() {
  console.log('Usage:');
  console.log('  node src/index.js group <zip-or-dir...> --output <dir> [--semantic-llm] [--threshold <n>] [--top-k <n>] [--llm-concurrency <n>] [--semantic-cache <file>]');
  console.log('');
  console.log('Output:');
  console.log('  <output>/grouping.json');
  console.log('  <output>/grouping.md');
  console.log('  <output>/groups/group_001/*.zip');
  console.log('  <output>/ungrouped/*.zip');
}

function parseArgs(argv) {
  const parsed = {
    command: argv[0],
    inputs: [],
    help: false,
    options: {
      output: '',
      threshold: DEFAULT_THRESHOLD,
      topK: DEFAULT_TOP_K,
      semanticLlm: false,
      llmConcurrency: 1,
      semanticCachePath: ''
    }
  };

  if (!argv.length || argv.includes('--help') || argv.includes('-h')) {
    parsed.help = true;
    return parsed;
  }

  for (let i = 1; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--output' && i + 1 < argv.length) {
      parsed.options.output = argv[++i];
    } else if (arg === '--threshold' && i + 1 < argv.length) {
      parsed.options.threshold = Number(argv[++i]);
    } else if (arg === '--top-k' && i + 1 < argv.length) {
      parsed.options.topK = Number(argv[++i]);
    } else if (arg === '--llm-concurrency' && i + 1 < argv.length) {
      parsed.options.llmConcurrency = Number(argv[++i]);
    } else if (arg === '--semantic-cache' && i + 1 < argv.length) {
      parsed.options.semanticCachePath = argv[++i];
    } else if (arg === '--semantic-llm') {
      parsed.options.semanticLlm = true;
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      parsed.inputs.push(arg);
    }
  }

  if (!parsed.help && parsed.command === 'group') {
    if (parsed.inputs.length === 0) {
      throw new Error('At least one zip file or directory is required');
    }
    if (!parsed.options.output) {
      throw new Error('--output <dir> is required');
    }
    if (!Number.isFinite(parsed.options.threshold) || parsed.options.threshold < 0 || parsed.options.threshold > 1) {
      throw new Error('--threshold must be a number between 0 and 1');
    }
    if (!Number.isInteger(parsed.options.topK) || parsed.options.topK <= 0) {
      throw new Error('--top-k must be a positive integer');
    }
    if (!Number.isInteger(parsed.options.llmConcurrency) || parsed.options.llmConcurrency <= 0) {
      throw new Error('--llm-concurrency must be a positive integer');
    }
  }

  return parsed;
}

async function analyzeSimilarity(inputs, options = {}) {
  const threshold = normalizeNumber(options.threshold, DEFAULT_THRESHOLD);
  const topK = normalizeInteger(options.topK, DEFAULT_TOP_K);
  const outputDir = options.output ? path.resolve(options.output) : '';
  const semanticCachePath = options.semanticCachePath
    ? path.resolve(options.semanticCachePath)
    : (outputDir ? path.join(outputDir, 'semantic-cache.jsonl') : '');
  const errors = [];
  const zipPaths = collectZipInputs(inputs, errors);
  const skills = [];

  for (const zipPath of zipPaths) {
    const parsed = parseSkillZip(zipPath);
    if (parsed.error) {
      errors.push(parsed.error);
    } else {
      parsed.skill.id = `skill_${String(skills.length + 1).padStart(4, '0')}`;
      skills.push(parsed.skill);
    }
  }

  const vectors = buildTfidfVectors(skills.map(skill => skill.profile.textTokens));
  for (let i = 0; i < skills.length; i++) {
    skills[i].profile.tfidfVector = vectors[i];
  }

  const pairIndex = buildStreamingPairIndex(skills, {
    threshold,
    topK,
    keepAllPairs: Boolean(options.keepAllPairs),
    onProgress: options.onPairProgress,
    progressIntervalPairs: options.progressIntervalPairs,
    exhaustivePairLimit: options.exhaustivePairLimit,
    maxCandidateBucketSize: options.maxCandidateBucketSize,
    oversizedBucketWindow: options.oversizedBucketWindow,
    maxCandidatePairs: options.maxCandidatePairs,
    pairStrategy: options.pairStrategy
  });
  const llmCandidateKeys = new Set(pairIndex.candidatePairs.map(pairKey));
  if (options.semanticLlm) {
    const apiKey = String(options.llmApiKey || process.env.LLM_API_KEY || '').trim();
    if (!apiKey && typeof options.semanticScorer !== 'function') {
      throw new Error('--semantic-llm requires LLM_API_KEY unless a semanticScorer is provided');
    }
    await refinePairsWithSemanticLlm(pairIndex.candidatePairs, skills, llmCandidateKeys, {
      ...options,
      semanticCachePath
    }, errors);
  }

  for (const pair of pairIndex.candidatePairs) {
    const fusedScore = pair.llm_score === null
      ? pair.rule_score
      : clamp(0.75 * pair.rule_score + 0.25 * pair.llm_score, 0, 1);
    const llmContradictionPenalty = pair.llm_has_contradiction ? 0.35 : 0;
    pair.components.llm_contradiction_penalty = llmContradictionPenalty;
    pair.similarity_score = round6(Math.max(0, fusedScore - llmContradictionPenalty));
    pair.semantic_distance = round6(1 - pair.similarity_score);
  }

  const scoredPairMap = buildScoredPairMap(pairIndex, threshold);
  const grouping = buildGroupsFromPairMap(skills, scoredPairMap, threshold);
  const similarityPairs = Array.from(scoredPairMap.values())
    .sort((a, b) => b.similarity_score - a.similarity_score)
    .map(pair => serializePair(pair, skills));

  const result = {
    meta: {
      analyzer: 'skill-similarity-analyzer',
      analyzer_version: VERSION,
      generated_at: new Date().toISOString(),
      threshold,
      top_k: topK,
      semantic_llm: Boolean(options.semanticLlm),
      llm_concurrency: normalizeInteger(options.llmConcurrency, 1),
      semantic_cache: semanticCachePath,
      output_dir: outputDir
    },
    skills: skills.map(serializeSkill),
    similarity_pairs: similarityPairs,
    groups: grouping.groups,
    ungrouped: grouping.ungrouped,
    statistics: {
      total_zips: zipPaths.length,
      valid_skills: skills.length,
      invalid_skills: errors.length,
      pair_index_strategy: pairIndex.strategy,
      pair_count: pairIndex.totalPairCount,
      theoretical_pair_count: pairIndex.totalPairCount,
      scored_pair_count: pairIndex.scoredPairCount,
      candidate_source_pair_count: pairIndex.candidateSourcePairCount,
      reported_pair_count: similarityPairs.length,
      threshold_pair_count: pairIndex.thresholdPairKeys.size,
      top_k_candidate_pair_count: llmCandidateKeys.size,
      candidate_feature_count: pairIndex.candidateStats.featureCount,
      candidate_bucket_count: pairIndex.candidateStats.bucketCount,
      oversized_candidate_bucket_count: pairIndex.candidateStats.oversizedBucketCount,
      skipped_candidate_bucket_count: pairIndex.candidateStats.skippedBucketCount,
      group_count: grouping.groups.length,
      grouped_skill_count: grouping.groups.reduce((sum, group) => sum + group.members.length, 0),
      ungrouped_skill_count: grouping.ungrouped.length
    },
    errors
  };

  if (outputDir) {
    saveOutputs(result, skills, scoredPairMap, outputDir);
  }

  return result;
}

function collectZipInputs(inputs, errors = []) {
  const seen = new Set();
  const zips = [];

  for (const input of inputs || []) {
    const resolved = path.resolve(input);
    if (!fs.existsSync(resolved)) {
      errors.push({ input: resolved, reason: 'Input path does not exist' });
      continue;
    }

    const stat = fs.statSync(resolved);
    if (stat.isFile()) {
      if (/\.zip$/i.test(resolved)) addZip(resolved, seen, zips);
      else errors.push({ input: resolved, reason: 'Input file is not a .zip package' });
      continue;
    }

    if (stat.isDirectory()) {
      for (const zipPath of findZipFiles(resolved)) {
        addZip(zipPath, seen, zips);
      }
    }
  }

  return zips.sort((a, b) => a.localeCompare(b));
}

function findZipFiles(rootDir) {
  const results = [];
  const ignoredDirs = new Set(['node_modules', '.git', 'groups', 'ungrouped']);

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!ignoredDirs.has(entry.name)) walk(fullPath);
      } else if (entry.isFile() && /\.zip$/i.test(entry.name)) {
        results.push(fullPath);
      }
    }
  }

  walk(rootDir);
  return results;
}

function addZip(zipPath, seen, zips) {
  const real = path.resolve(zipPath);
  const key = real.toLowerCase();
  if (!seen.has(key)) {
    seen.add(key);
    zips.push(real);
  }
}

function parseSkillZip(zipPath) {
  try {
    const zip = new AdmZip(zipPath);
    const entries = zip.getEntries().filter(entry => !entry.isDirectory);
    const skillEntry = findBestMarkdownEntry(entries, 'skill.md');
    if (!skillEntry) {
      return {
        error: {
          input: zipPath,
          reason: 'SKILL.md not found in zip package'
        }
      };
    }

    const readmeEntry = findBestMarkdownEntry(entries, 'readme.md');
    const skillContent = skillEntry.getData().toString('utf-8');
    const readmeContent = readmeEntry ? readmeEntry.getData().toString('utf-8') : '';
    const frontMatter = parseFrontMatter(skillContent);
    const skillName = String(frontMatter.data.name || path.basename(zipPath, path.extname(zipPath))).trim();
    const description = String(frontMatter.data.description || '').trim();
    const profile = buildDocumentProfile({
      skillName,
      description,
      skillContent: frontMatter.content,
      readmeContent
    });

    return {
      skill: {
        id: '',
        skill_name: skillName || path.basename(zipPath, path.extname(zipPath)),
        description,
        zip_path: path.resolve(zipPath),
        zip_name: path.basename(zipPath),
        skill_entry: skillEntry.entryName,
        readme_entry: readmeEntry ? readmeEntry.entryName : '',
        readme_missing: !readmeEntry,
        profile
      }
    };
  } catch (error) {
    return {
      error: {
        input: zipPath,
        reason: `Failed to read zip package: ${error.message}`
      }
    };
  }
}

function findBestMarkdownEntry(entries, basename) {
  const lowerBase = basename.toLowerCase();
  const candidates = entries
    .filter(entry => path.posix.basename(entry.entryName).toLowerCase() === lowerBase)
    .sort((a, b) => {
      const depthA = a.entryName.split('/').length;
      const depthB = b.entryName.split('/').length;
      if (depthA !== depthB) return depthA - depthB;
      return a.entryName.length - b.entryName.length;
    });
  return candidates[0] || null;
}

function parseFrontMatter(markdown) {
  const text = String(markdown || '').replace(/^\uFEFF/, '');
  if (!text.startsWith('---')) {
    return { data: {}, content: text };
  }

  const end = text.indexOf('\n---', 3);
  if (end === -1) {
    return { data: {}, content: text };
  }

  const raw = text.slice(3, end).trim();
  const contentStart = text.indexOf('\n', end + 4);
  const content = contentStart === -1 ? '' : text.slice(contentStart + 1);
  const data = {};

  for (const line of raw.split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$/);
    if (!match) continue;
    let value = match[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    data[match[1]] = value;
  }

  return { data, content };
}

function buildDocumentProfile({ skillName, description, skillContent, readmeContent }) {
  const combined = [skillName, description, skillContent, readmeContent].filter(Boolean).join('\n\n');
  const headings = extractHeadings(combined);
  const headingText = headings.join(' ');
  const textTokens = [
    ...tokenize(`${skillName} ${description} ${headingText}`),
    ...tokenize(`${skillName} ${description} ${headingText}`),
    ...tokenize(combined)
  ];
  const titleDescriptionTokens = uniqueTokens(tokenize(`${skillName} ${description} ${headingText}`));
  const actionTags = extractPatternTags(combined, ACTION_PATTERNS);
  const platformTags = new Set([
    ...extractPatternTags(combined, PLATFORM_PATTERNS),
    ...extractDottedToolTags(combined)
  ]);
  const ioTags = extractPatternTags(combined, IO_PATTERNS);
  const domainTerms = extractDomainTerms(textTokens, actionTags, platformTags, ioTags);
  const polarityProfile = buildPolarityProfile(combined, {
    actionTags,
    platformTags,
    ioTags
  });

  return {
    headings,
    titleDescriptionTokens: Array.from(titleDescriptionTokens).sort(),
    actionTags: Array.from(actionTags).sort(),
    platformTags: Array.from(platformTags).sort(),
    ioTags: Array.from(ioTags).sort(),
    domainTerms,
    polarityProfile,
    textTokens,
    summary: buildProfileSummary(skillName, description, headings, actionTags, platformTags, ioTags, domainTerms, polarityProfile)
  };
}

function extractHeadings(text) {
  const headings = [];
  for (const line of String(text || '').split(/\r?\n/)) {
    const match = line.match(/^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$/);
    if (match) headings.push(match[1].trim());
  }
  return headings.slice(0, 40);
}

function tokenize(text) {
  const normalized = String(text || '')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .toLowerCase();
  const tokens = [];
  const asciiParts = normalized.match(/[a-z0-9_][a-z0-9_.-]*/g) || [];
  for (const part of asciiParts) {
    for (const token of part.split(/[^a-z0-9_]+/)) {
      if (token.length >= 2 && !STOPWORDS.has(token)) tokens.push(token);
    }
  }

  const cjkParts = normalized.match(/[\u3400-\u9FFF]{2,}/g) || [];
  for (const part of cjkParts) {
    for (let i = 0; i < part.length - 1; i++) {
      tokens.push(part.slice(i, i + 2));
    }
    for (let i = 0; i < part.length - 2; i++) {
      tokens.push(part.slice(i, i + 3));
    }
  }

  return tokens;
}

function uniqueTokens(tokens) {
  return new Set((tokens || []).filter(Boolean));
}

function extractPatternTags(text, definitions) {
  const tags = new Set();
  const source = String(text || '').toLowerCase();
  for (const [tag, regex] of definitions) {
    regex.lastIndex = 0;
    if (regex.test(source)) tags.add(tag);
  }
  return tags;
}

function extractDottedToolTags(text) {
  const tags = new Set();
  const regex = /\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\b/g;
  let match;
  while ((match = regex.exec(String(text || ''))) !== null) {
    tags.add(match[1].toLowerCase().split('.')[0]);
  }
  return tags;
}

function buildPolarityProfile(text, context = {}) {
  const claims = [];
  const sentences = splitIntoSentences(text);

  for (const sentence of sentences) {
    const polarity = detectSentencePolarity(sentence);
    const actions = extractPolarityActions(sentence);
    const platformTags = extractPatternTags(sentence, PLATFORM_PATTERNS);
    const ioTags = extractPatternTags(sentence, IO_PATTERNS);
    const objectTokens = extractPolarityObjectTokens(sentence, actions, platformTags, ioTags);

    const hasContextualSignal =
      actions.size > 0 ||
      platformTags.size > 0 ||
      ioTags.size > 0 ||
      polarity !== 'allow';
    if (!hasContextualSignal || objectTokens.size === 0) continue;

    claims.push({
      polarity,
      actions: Array.from(actions).sort(),
      objects: Array.from(objectTokens).sort(),
      platform_tags: Array.from(platformTags).sort(),
      io_tags: Array.from(ioTags).sort(),
      text: sentence.slice(0, 240)
    });
  }

  return {
    claims: dedupePolarityClaims(claims),
    action_tags: Array.from(context.actionTags || []).sort(),
    platform_tags: Array.from(context.platformTags || []).sort(),
    io_tags: Array.from(context.ioTags || []).sort()
  };
}

function splitIntoSentences(text) {
  return String(text || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .split(/[\r\n]+|(?<=[.!?;。！？；])\s+/)
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 0)
    .slice(0, 300);
}

function detectSentencePolarity(sentence) {
  const source = String(sentence || '').toLowerCase();
  for (const polarity of ['deny', 'require', 'only', 'allow']) {
    const definition = POLARITY_PATTERNS.find(([name]) => name === polarity);
    const regex = definition?.[1];
    if (!regex) continue;
    regex.lastIndex = 0;
    if (regex.test(source)) return polarity;
  }
  return 'allow';
}

function extractPolarityActions(sentence) {
  const actions = new Set();
  const source = String(sentence || '').toLowerCase();
  for (const [tag, regex] of POLARITY_ACTION_PATTERNS) {
    regex.lastIndex = 0;
    if (regex.test(source)) actions.add(tag);
  }
  return actions;
}

function extractPolarityObjectTokens(sentence, actions, platformTags, ioTags) {
  const actionWords = new Set([...Array.from(actions || []), ...POLARITY_WORDS]);
  const objectTokens = new Set();

  for (const tag of platformTags || []) objectTokens.add(tag);
  for (const tag of ioTags || []) objectTokens.add(tag);

  for (const token of tokenize(sentence)) {
    if (STOPWORDS.has(token)) continue;
    if (actionWords.has(token)) continue;
    if (token.length < 2) continue;
    objectTokens.add(token);
  }

  return objectTokens;
}

function dedupePolarityClaims(claims) {
  const seen = new Set();
  const output = [];
  for (const claim of claims) {
    const key = [
      claim.polarity,
      claim.actions.join(','),
      claim.objects.slice(0, 12).join(',')
    ].join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(claim);
  }
  return output.slice(0, 80);
}

function extractDomainTerms(tokens, actionTags, platformTags, ioTags) {
  const blocked = new Set([
    ...Array.from(actionTags),
    ...Array.from(platformTags),
    ...Array.from(ioTags),
    ...STOPWORDS
  ]);
  const counts = new Map();
  for (const token of tokens || []) {
    if (blocked.has(token) || token.length < 3) continue;
    counts.set(token, (counts.get(token) || 0) + 1);
  }
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 30)
    .map(([token]) => token);
}

function buildProfileSummary(skillName, description, headings, actionTags, platformTags, ioTags, domainTerms, polarityProfile) {
  return {
    name: skillName,
    description,
    headings: headings.slice(0, 12),
    actions: Array.from(actionTags).sort(),
    platforms: Array.from(platformTags).sort(),
    io_objects: Array.from(ioTags).sort(),
    domain_terms: domainTerms.slice(0, 15),
    polarity_claims: (polarityProfile?.claims || []).slice(0, 12)
  };
}

function buildTfidfVectors(tokenLists) {
  const docCount = tokenLists.length || 1;
  const dfs = new Map();
  const tfs = tokenLists.map(tokens => {
    const counts = new Map();
    for (const token of tokens || []) {
      counts.set(token, (counts.get(token) || 0) + 1);
    }
    for (const token of counts.keys()) {
      dfs.set(token, (dfs.get(token) || 0) + 1);
    }
    return counts;
  });

  return tfs.map(counts => {
    const vector = new Map();
    for (const [token, count] of counts.entries()) {
      const idf = Math.log((docCount + 1) / ((dfs.get(token) || 0) + 1)) + 1;
      vector.set(token, (1 + Math.log(count)) * idf);
    }
    return vector;
  });
}

function buildPairScores(skills) {
  const pairs = [];
  for (let i = 0; i < skills.length; i++) {
    for (let j = i + 1; j < skills.length; j++) {
      const a = skills[i];
      const b = skills[j];
      pairs.push(scoreSkillPair(a, b));
    }
  }
  return pairs;
}

function buildStreamingPairIndex(skills, options = {}) {
  const totalPairs = skills.length * (skills.length - 1) / 2;
  const exhaustivePairLimit = normalizeInteger(options.exhaustivePairLimit, DEFAULT_EXHAUSTIVE_PAIR_LIMIT);
  const requestedStrategy = String(options.pairStrategy || '').trim().toLowerCase();
  const useExhaustive =
    requestedStrategy === 'exhaustive' ||
    Boolean(options.keepAllPairs) ||
    requestedStrategy !== 'candidate' && (totalPairs <= exhaustivePairLimit || skills.length <= 2);

  if (useExhaustive) {
    return buildExhaustivePairIndex(skills, options, totalPairs);
  }

  return buildCandidatePairIndex(skills, options, totalPairs);
}

function buildExhaustivePairIndex(skills, options, totalPairs) {
  const threshold = normalizeNumber(options.threshold, DEFAULT_THRESHOLD);
  const topK = normalizeInteger(options.topK, DEFAULT_TOP_K);
  const thresholdPairs = new Map();
  const topKBySkill = new Map(skills.map(skill => [skill.id, []]));
  const allPairs = options.keepAllPairs ? [] : null;
  const progressIntervalPairs = normalizeInteger(options.progressIntervalPairs, 1_000_000);
  const onProgress = typeof options.onProgress === 'function' ? options.onProgress : null;
  let nextProgressAt = progressIntervalPairs;
  const startedAt = Date.now();
  let pairCount = 0;

  for (let i = 0; i < skills.length; i++) {
    for (let j = i + 1; j < skills.length; j++) {
      const pair = scoreSkillPair(skills[i], skills[j]);
      pairCount += 1;
      if (allPairs) allPairs.push(pair);
      if (pair.similarity_score >= threshold) {
        thresholdPairs.set(pairKey(pair), pair);
      }
      addTopKPair(topKBySkill.get(pair.source), pair, topK);
      addTopKPair(topKBySkill.get(pair.target), pair, topK);
      if (onProgress && pairCount >= nextProgressAt) {
        onProgress({
          pairCount,
          totalPairs,
          percent: totalPairs ? round6(pairCount / totalPairs * 100) : 100,
          elapsedMs: Date.now() - startedAt
        });
        nextProgressAt += progressIntervalPairs;
      }
    }
  }

  if (onProgress) {
    onProgress({
      pairCount,
      totalPairs,
      percent: 100,
      elapsedMs: Date.now() - startedAt
    });
  }

  const candidatePairsByKey = new Map(thresholdPairs);
  for (const pairs of topKBySkill.values()) {
    for (const pair of pairs) {
      candidatePairsByKey.set(pairKey(pair), pair);
    }
  }

  return {
    strategy: 'exhaustive',
    pairCount,
    totalPairCount: totalPairs,
    scoredPairCount: pairCount,
    candidateSourcePairCount: pairCount,
    candidateStats: emptyCandidateStats(),
    thresholdPairKeys: new Set(thresholdPairs.keys()),
    thresholdPairs,
    topKBySkill,
    candidatePairs: Array.from(candidatePairsByKey.values()),
    allPairs
  };
}

function buildCandidatePairIndex(skills, options, totalPairs) {
  const threshold = normalizeNumber(options.threshold, DEFAULT_THRESHOLD);
  const topK = normalizeInteger(options.topK, DEFAULT_TOP_K);
  const thresholdPairs = new Map();
  const topKBySkill = new Map(skills.map(skill => [skill.id, []]));
  const candidateIndex = buildCandidatePairKeys(skills, options);
  const candidatePairs = candidateIndex.pairs;
  const progressIntervalPairs = normalizeInteger(options.progressIntervalPairs, 100_000);
  const onProgress = typeof options.onProgress === 'function' ? options.onProgress : null;
  let nextProgressAt = progressIntervalPairs;
  const startedAt = Date.now();
  let pairCount = 0;

  for (const [sourceIndex, targetIndex] of candidatePairs) {
    const pair = scoreSkillPair(skills[sourceIndex], skills[targetIndex]);
    pairCount += 1;
    if (pair.similarity_score >= threshold) {
      thresholdPairs.set(pairKey(pair), pair);
    }
    addTopKPair(topKBySkill.get(pair.source), pair, topK);
    addTopKPair(topKBySkill.get(pair.target), pair, topK);
    if (onProgress && pairCount >= nextProgressAt) {
      onProgress({
        pairCount,
        totalPairs: candidatePairs.length,
        theoreticalPairCount: totalPairs,
        strategy: 'candidate',
        percent: candidatePairs.length ? round6(pairCount / candidatePairs.length * 100) : 100,
        elapsedMs: Date.now() - startedAt
      });
      nextProgressAt += progressIntervalPairs;
    }
  }

  if (onProgress) {
    onProgress({
      pairCount,
      totalPairs: candidatePairs.length,
      theoreticalPairCount: totalPairs,
      strategy: 'candidate',
      percent: 100,
      elapsedMs: Date.now() - startedAt
    });
  }

  const candidatePairsByKey = new Map(thresholdPairs);
  for (const pairs of topKBySkill.values()) {
    for (const pair of pairs) {
      candidatePairsByKey.set(pairKey(pair), pair);
    }
  }

  return {
    strategy: 'candidate',
    pairCount,
    totalPairCount: totalPairs,
    scoredPairCount: pairCount,
    candidateSourcePairCount: candidatePairs.length,
    candidateStats: candidateIndex.stats,
    thresholdPairKeys: new Set(thresholdPairs.keys()),
    thresholdPairs,
    topKBySkill,
    candidatePairs: Array.from(candidatePairsByKey.values()),
    allPairs: null
  };
}

function buildCandidatePairKeys(skills, options = {}) {
  const maxBucketSize = normalizeInteger(options.maxCandidateBucketSize, DEFAULT_CANDIDATE_BUCKET_LIMIT);
  const oversizedBucketWindow = normalizeNonNegativeInteger(options.oversizedBucketWindow, DEFAULT_OVERSIZED_BUCKET_WINDOW);
  const fallbackNeighborWindow = normalizeNonNegativeInteger(options.fallbackNeighborWindow, 2);
  const maxCandidatePairs = normalizeInteger(options.maxCandidatePairs, DEFAULT_MAX_CANDIDATE_PAIRS);
  const buckets = new Map();
  let featureAssignmentCount = 0;

  for (let index = 0; index < skills.length; index++) {
    const features = collectCandidateFeatures(skills[index]);
    featureAssignmentCount += features.size;
    for (const feature of features) {
      if (!buckets.has(feature)) buckets.set(feature, []);
      buckets.get(feature).push(index);
    }
  }

  const candidateKeys = new Set();
  const stats = {
    ...emptyCandidateStats(),
    featureCount: buckets.size,
    featureAssignmentCount
  };
  const entries = Array.from(buckets.entries())
    .map(([feature, indexes]) => ({
      feature,
      indexes: Array.from(new Set(indexes)).sort((a, b) => compareCandidateSkillOrder(skills[a], skills[b])),
      priority: candidateFeaturePriority(feature)
    }))
    .filter(entry => entry.indexes.length >= 2)
    .sort((a, b) => {
      const pairDelta = candidateBucketPairCount(a.indexes.length) - candidateBucketPairCount(b.indexes.length);
      if (pairDelta !== 0) return pairDelta;
      if (a.priority !== b.priority) return b.priority - a.priority;
      return a.feature.localeCompare(b.feature);
    });

  stats.bucketCount = entries.length;

  let limitReached = false;
  for (let entryIndex = 0; entryIndex < entries.length; entryIndex++) {
    if (candidateKeys.size >= maxCandidatePairs) {
      stats.skippedBucketCount += entries.length - entryIndex;
      limitReached = true;
      break;
    }

    const entry = entries[entryIndex];
    if (entry.indexes.length > maxBucketSize) {
      stats.oversizedBucketCount += 1;
      if (isLowSignalCandidateFeature(entry.feature)) {
        stats.skippedBucketCount += 1;
        continue;
      }
      addWindowedBucketPairs(entry.indexes, skills.length, oversizedBucketWindow, candidateKeys, maxCandidatePairs);
      continue;
    }

    addAllBucketPairs(entry.indexes, skills.length, candidateKeys, maxCandidatePairs);
  }

  if (!limitReached && fallbackNeighborWindow > 0 && candidateKeys.size < maxCandidatePairs) {
    const orderedIndexes = skills
      .map((skill, index) => ({ skill, index }))
      .sort((a, b) => compareCandidateSkillOrder(a.skill, b.skill))
      .map(item => item.index);
    addWindowedBucketPairs(orderedIndexes, skills.length, fallbackNeighborWindow, candidateKeys, maxCandidatePairs);
  }

  const pairs = Array.from(candidateKeys)
    .map(key => decodeCandidatePairKey(key, skills.length))
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  stats.candidatePairCount = pairs.length;
  return { pairs, stats };
}

function collectCandidateFeatures(skill) {
  const profile = skill.profile || {};
  const features = new Set();
  const actionTags = (profile.actionTags || []).slice(0, 8);
  const platformTags = (profile.platformTags || []).slice(0, 8);
  const ioTags = (profile.ioTags || []).slice(0, 8);
  const domainTerms = (profile.domainTerms || []).filter(isUsefulCandidateToken).slice(0, 12);
  const titleTokens = (profile.titleDescriptionTokens || []).filter(isUsefulCandidateToken).slice(0, 30);
  const nameTokens = tokenize(skill.skill_name || '').filter(isUsefulCandidateToken).slice(0, 12);

  for (const tag of actionTags) features.add(`a:${tag}`);
  for (const tag of platformTags) features.add(`p:${tag}`);
  for (const tag of ioTags) features.add(`io:${tag}`);
  for (const term of domainTerms) features.add(`d:${term}`);
  for (const token of titleTokens) features.add(`t:${token}`);
  for (const token of nameTokens) features.add(`n:${token}`);

  for (const action of actionTags.slice(0, 5)) {
    for (const platform of platformTags.slice(0, 5)) features.add(`ap:${action}:${platform}`);
    for (const io of ioTags.slice(0, 5)) features.add(`ai:${action}:${io}`);
  }
  for (const platform of platformTags.slice(0, 5)) {
    for (const io of ioTags.slice(0, 5)) features.add(`pi:${platform}:${io}`);
  }
  for (const term of domainTerms.slice(0, 5)) {
    for (const platform of platformTags.slice(0, 3)) features.add(`dp:${term}:${platform}`);
    for (const action of actionTags.slice(0, 3)) features.add(`da:${term}:${action}`);
  }

  addAdjacentTokenFeatures(features, 'nt', nameTokens);
  addAdjacentTokenFeatures(features, 'tt', titleTokens);
  return features;
}

function addAdjacentTokenFeatures(features, prefix, tokens) {
  const unique = Array.from(new Set(tokens || []));
  for (let index = 0; index < unique.length - 1; index++) {
    features.add(`${prefix}:${unique[index]}:${unique[index + 1]}`);
  }
}

function isUsefulCandidateToken(token) {
  const value = String(token || '').toLowerCase().trim();
  if (value.length < 3) return false;
  if (/^\d+$/.test(value)) return false;
  if (STOPWORDS.has(value)) return false;
  return !COMMON_CANDIDATE_TOKENS.has(value);
}

function candidateFeaturePriority(feature) {
  if (/^(ap|ai|pi|dp|da|nt|tt):/.test(feature)) return 5;
  if (/^(d|n):/.test(feature)) return 4;
  if (/^t:/.test(feature)) return 3;
  if (/^p:/.test(feature)) return 2;
  if (/^(a|io):/.test(feature)) return 1;
  return 0;
}

function isLowSignalCandidateFeature(feature) {
  return /^(a|io|t):/.test(feature);
}

function addAllBucketPairs(indexes, skillCount, candidateKeys, maxCandidatePairs) {
  for (let i = 0; i < indexes.length; i++) {
    for (let j = i + 1; j < indexes.length; j++) {
      if (!addCandidatePairKey(indexes[i], indexes[j], skillCount, candidateKeys, maxCandidatePairs)) return;
    }
  }
}

function addWindowedBucketPairs(indexes, skillCount, windowSize, candidateKeys, maxCandidatePairs) {
  if (windowSize <= 0) return;
  for (let i = 0; i < indexes.length; i++) {
    const upper = Math.min(indexes.length, i + windowSize + 1);
    for (let j = i + 1; j < upper; j++) {
      if (!addCandidatePairKey(indexes[i], indexes[j], skillCount, candidateKeys, maxCandidatePairs)) return;
    }
  }
}

function addCandidatePairKey(a, b, skillCount, candidateKeys, maxCandidatePairs) {
  if (a === b || candidateKeys.size >= maxCandidatePairs) return false;
  const source = Math.min(a, b);
  const target = Math.max(a, b);
  candidateKeys.add(source * skillCount + target);
  return candidateKeys.size < maxCandidatePairs;
}

function decodeCandidatePairKey(key, skillCount) {
  const source = Math.floor(key / skillCount);
  return [source, key % skillCount];
}

function candidateBucketPairCount(size) {
  return size * (size - 1) / 2;
}

function compareCandidateSkillOrder(a, b) {
  const aText = candidateSkillSortText(a);
  const bText = candidateSkillSortText(b);
  return aText.localeCompare(bText);
}

function candidateSkillSortText(skill) {
  return [
    skill.skill_name || '',
    skill.zip_name || '',
    skill.id || ''
  ].join('\n').toLowerCase();
}

function emptyCandidateStats() {
  return {
    featureCount: 0,
    featureAssignmentCount: 0,
    bucketCount: 0,
    oversizedBucketCount: 0,
    skippedBucketCount: 0,
    candidatePairCount: 0
  };
}

function scoreSkillPair(a, b) {
  const components = scoreComponents(a.profile, b.profile);
  const baseRuleScore = round6(
    components.tfidf_cosine * 0.50 +
    components.title_description * 0.20 +
    components.action_tags * 0.15 +
    components.platform_tags * 0.10 +
    components.io_objects * 0.05
  );
  const contradiction = detectPolarityContradictions(a.profile, b.profile);
  components.base_rule_score = baseRuleScore;
  components.contradiction_penalty = contradiction.penalty;
  components.polarity_conflicts = contradiction.conflicts;
  const ruleScore = round6(Math.max(0, baseRuleScore - contradiction.penalty));
  return {
    source: a.id,
    target: b.id,
    base_rule_score: baseRuleScore,
    rule_score: ruleScore,
    llm_score: null,
    llm_reason: '',
    llm_error: '',
    llm_has_contradiction: false,
    llm_contradiction_reason: '',
    similarity_score: ruleScore,
    semantic_distance: round6(1 - ruleScore),
    components
  };
}

function addTopKPair(list, pair, topK) {
  if (!list) return;
  list.push(pair);
  list.sort((a, b) => b.rule_score - a.rule_score || pairKey(a).localeCompare(pairKey(b)));
  if (list.length > topK) {
    list.length = topK;
  }
}

function buildScoredPairMap(pairIndex, threshold) {
  const scored = new Map();
  for (const pair of pairIndex.candidatePairs) {
    scored.set(pairKey(pair), pair);
  }
  for (const key of pairIndex.thresholdPairKeys) {
    const pair = pairIndex.thresholdPairs.get(key);
    if (pair) scored.set(key, pair);
  }
  return scored;
}

function scoreComponents(a, b) {
  return {
    tfidf_cosine: round6(cosineSimilarity(a.tfidfVector, b.tfidfVector)),
    title_description: round6(jaccard(a.titleDescriptionTokens, b.titleDescriptionTokens)),
    action_tags: round6(jaccard(a.actionTags, b.actionTags)),
    platform_tags: round6(jaccard(a.platformTags, b.platformTags)),
    io_objects: round6(jaccard(a.ioTags, b.ioTags))
  };
}

function detectPolarityContradictions(profileA, profileB) {
  const conflicts = [];
  const claimsA = profileA?.polarityProfile?.claims || [];
  const claimsB = profileB?.polarityProfile?.claims || [];

  for (const claimA of claimsA) {
    for (const claimB of claimsB) {
      if (!hasContrastingPolarity(claimA.polarity, claimB.polarity)) continue;
      const actionOverlap = intersectArray(claimA.actions, claimB.actions);
      const objectOverlap = intersectArray(claimA.objects, claimB.objects);
      if (actionOverlap.length === 0 && objectOverlap.length < 2) continue;
      if (objectOverlap.length === 0) continue;

      const conflict = {
        polarity_a: claimA.polarity,
        polarity_b: claimB.polarity,
        shared_actions: actionOverlap,
        shared_objects: objectOverlap.slice(0, 12),
        penalty: calculatePolarityPenalty(claimA, claimB, actionOverlap, objectOverlap),
        evidence_a: claimA.text,
        evidence_b: claimB.text
      };
      conflicts.push(conflict);
    }
  }

  const penalty = conflicts.length
    ? Math.max(...conflicts.map(conflict => conflict.penalty))
    : 0;

  return {
    penalty: round6(penalty),
    conflicts: conflicts
      .sort((a, b) => b.penalty - a.penalty)
      .slice(0, 8)
      .map(conflict => ({
        ...conflict,
        penalty: round6(conflict.penalty)
      }))
  };
}

function hasContrastingPolarity(a, b) {
  if (a === b) return false;
  const denySet = new Set(['deny']);
  const positiveSet = new Set(['allow', 'require']);
  if (denySet.has(a) && positiveSet.has(b)) return true;
  if (denySet.has(b) && positiveSet.has(a)) return true;
  if ((a === 'only' && b === 'allow') || (b === 'only' && a === 'allow')) return true;
  return false;
}

function calculatePolarityPenalty(claimA, claimB, actionOverlap, objectOverlap) {
  if (isHighRiskPolarityConflict(claimA, claimB, actionOverlap, objectOverlap)) {
    return 0.50;
  }
  if (claimA.polarity === 'deny' || claimB.polarity === 'deny') {
    return 0.35;
  }
  return 0.15;
}

function isHighRiskPolarityConflict(claimA, claimB, actionOverlap, objectOverlap) {
  const combined = new Set([
    ...actionOverlap,
    ...objectOverlap,
    ...(claimA.io_tags || []),
    ...(claimB.io_tags || []),
    ...(claimA.platform_tags || []),
    ...(claimB.platform_tags || [])
  ]);

  if (['send', 'execute'].some(action => combined.has(action))) return true;
  for (const value of combined) {
    if (POLARITY_HIGH_RISK_TERMS.has(value)) return true;
  }
  return false;
}

function intersectArray(aValues, bValues) {
  const b = new Set(bValues || []);
  return Array.from(new Set(aValues || [])).filter(value => b.has(value));
}

function cosineSimilarity(vecA, vecB) {
  if (!vecA || !vecB || vecA.size === 0 || vecB.size === 0) return 0;
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (const value of vecA.values()) normA += value * value;
  for (const value of vecB.values()) normB += value * value;
  const smaller = vecA.size <= vecB.size ? vecA : vecB;
  const larger = vecA.size <= vecB.size ? vecB : vecA;
  for (const [token, value] of smaller.entries()) {
    dot += value * (larger.get(token) || 0);
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function jaccard(aValues, bValues) {
  const a = new Set(aValues || []);
  const b = new Set(bValues || []);
  if (a.size === 0 && b.size === 0) return 0;
  let intersection = 0;
  for (const value of a) {
    if (b.has(value)) intersection += 1;
  }
  const union = new Set([...a, ...b]).size;
  return union === 0 ? 0 : intersection / union;
}

async function refinePairsWithSemanticLlm(pairs, skills, candidateKeys, options, errors) {
  const apiKey = String(options.llmApiKey || process.env.LLM_API_KEY || '').trim();
  if (!apiKey && typeof options.semanticScorer !== 'function') {
    errors.push({ reason: '--semantic-llm enabled but LLM_API_KEY is not set; rule scores were used' });
    return;
  }

  const skillById = new Map(skills.map(skill => [skill.id, skill]));
  const cache = loadSemanticCache(options.semanticCachePath);
  const candidates = pairs
    .filter(pair => candidateKeys.has(pairKey(pair)))
    .sort((a, b) => b.rule_score - a.rule_score);
  const concurrency = normalizeInteger(options.llmConcurrency, 1);

  await runConcurrent(candidates, concurrency, async pair => {
    const a = skillById.get(pair.source);
    const b = skillById.get(pair.target);
    const cacheKey = buildSemanticCacheKey(a, b, pair, options);
    const cached = cache.entries.get(cacheKey);
    if (cached) {
      applySemanticResultToPair(pair, cached.result);
      pair.llm_reason = cached.result.reason ? `${cached.result.reason} [cache]` : '[cache]';
      return;
    }

    try {
      const result = typeof options.semanticScorer === 'function'
        ? await options.semanticScorer(a.profile.summary, b.profile.summary, pair)
        : await callSemanticSimilarityModel(a.profile.summary, b.profile.summary, pair, { ...options, apiKey });
      const normalized = normalizeLlmSimilarityResult(result);
      applySemanticResultToPair(pair, normalized);
      appendSemanticCacheEntry(options.semanticCachePath, cacheKey, normalized, a, b, pair);
      cache.entries.set(cacheKey, { result: normalized });
    } catch (error) {
      pair.llm_error = error.message;
      errors.push({
        pair: `${pair.source}->${pair.target}`,
        reason: `Semantic LLM fallback to rule score: ${error.message}`
      });
    }
  });
}

function applySemanticResultToPair(pair, normalized) {
  pair.llm_score = normalized.similarity;
  pair.llm_reason = normalized.reason;
  pair.llm_has_contradiction = normalized.has_contradiction;
  pair.llm_contradiction_reason = normalized.contradiction_reason;
}

async function runConcurrent(items, concurrency, worker) {
  let index = 0;
  const workers = Array.from({ length: Math.max(1, Math.min(concurrency, items.length || 1)) }, async () => {
    while (index < items.length) {
      const item = items[index++];
      await worker(item);
    }
  });
  await Promise.all(workers);
}

function loadSemanticCache(cachePath) {
  const entries = new Map();
  if (!cachePath || !fs.existsSync(cachePath)) {
    return { entries };
  }

  const lines = fs.readFileSync(cachePath, 'utf-8').split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const item = JSON.parse(line);
      if (item.cache_key && item.result) {
        entries.set(item.cache_key, item);
      }
    } catch {
      // Ignore malformed cache lines so one partial write does not block a run.
    }
  }
  return { entries };
}

function appendSemanticCacheEntry(cachePath, cacheKey, result, skillA, skillB, pair) {
  if (!cachePath) return;
  fs.mkdirSync(path.dirname(cachePath), { recursive: true });
  const entry = {
    cache_key: cacheKey,
    generated_at: new Date().toISOString(),
    model: process.env.LLM_MODEL || 'gpt-5.5',
    provider: process.env.LLM_PROVIDER || 'openai',
    pair: pairKey(pair),
    source: skillA.id,
    source_name: skillA.skill_name,
    target: skillB.id,
    target_name: skillB.skill_name,
    result
  };
  fs.appendFileSync(cachePath, `${JSON.stringify(entry)}\n`, 'utf-8');
}

function buildSemanticCacheKey(skillA, skillB, pair, options = {}) {
  const model = String(options.llmModel || process.env.LLM_MODEL || 'gpt-5.5');
  const provider = String(options.llmProvider || process.env.LLM_PROVIDER || 'openai');
  const payload = {
    analyzer_version: VERSION,
    provider,
    model,
    source: skillA.skill_name,
    target: skillB.skill_name,
    rule_score: pair.rule_score,
    summary_hashes: [
      hashObject(skillA.profile.summary),
      hashObject(skillB.profile.summary)
    ].sort()
  };
  return crypto.createHash('sha256').update(JSON.stringify(payload)).digest('hex');
}

function hashObject(value) {
  return crypto.createHash('sha256').update(JSON.stringify(value || null)).digest('hex');
}

async function callSemanticSimilarityModel(summaryA, summaryB, pair, options) {
  const endpoint = resolveLlmEndpoint(options);
  const model = options.llmModel || process.env.LLM_MODEL || 'gpt-5.5';
  const timeout = normalizeInteger(options.llmTimeout || process.env.LLM_TIMEOUT, 30000);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${options.apiKey}`
      },
      body: JSON.stringify({
        model,
        temperature: 0,
        messages: [
          {
            role: 'system',
            content: 'You judge whether two OpenClaw Skills provide similar user-facing capabilities and whether their goals or constraints contradict. Return strict JSON only in English with keys: similarity, reason, has_contradiction, contradiction_reason. similarity must be a number from 0 to 1. has_contradiction must be true or false.'
          },
          {
            role: 'user',
            content: JSON.stringify({
              instruction: 'Score functional similarity from 0 to 1. Use only these summaries; do not infer hidden implementation. Write every string value in English. If they are textually similar but one allows or requires an action while the other forbids or avoids the same action or object, set has_contradiction to true.',
              rule_score: pair.rule_score,
              polarity_conflicts: pair.components?.polarity_conflicts || [],
              skill_a: summaryA,
              skill_b: summaryB
            }, null, 2)
          }
        ]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    const payload = await response.json();
    return payload?.choices?.[0]?.message?.content;
  } finally {
    clearTimeout(timer);
  }
}

function resolveLlmEndpoint(options = {}) {
  if (options.llmEndpoint || process.env.LLM_ENDPOINT) {
    return options.llmEndpoint || process.env.LLM_ENDPOINT;
  }
  const provider = String(options.llmProvider || process.env.LLM_PROVIDER || 'openai').toLowerCase();
  if (provider === 'dashscope') {
    return process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
  }
  return 'https://api.openai.com/v1/chat/completions';
}

function normalizeLlmSimilarityResult(result) {
  const normalized = normalizeSimilarityResult(result);
  if (!normalized) {
    throw new Error('Unable to parse semantic LLM JSON');
  }
  return normalized;
}

function buildGroups(skills, pairs, threshold) {
  const pairMap = Array.isArray(pairs)
    ? new Map(pairs.map(pair => [pairKey(pair), pair]))
    : pairs;
  return buildGroupsFromPairMap(skills, pairMap, threshold);
}

function buildGroupsFromPairMap(skills, pairMap, threshold) {
  const adjacency = new Map(skills.map(skill => [skill.id, new Set()]));
  for (const pair of pairMap.values()) {
    if (pair.similarity_score >= threshold) {
      adjacency.get(pair.source)?.add(pair.target);
      adjacency.get(pair.target)?.add(pair.source);
    }
  }

  const visited = new Set();
  const components = [];
  for (const skill of skills) {
    if (visited.has(skill.id)) continue;
    const stack = [skill.id];
    const members = [];
    visited.add(skill.id);
    while (stack.length) {
      const id = stack.pop();
      members.push(id);
      for (const next of adjacency.get(id) || []) {
        if (!visited.has(next)) {
          visited.add(next);
          stack.push(next);
        }
      }
    }
    components.push(members.sort());
  }

  const groups = [];
  const ungrouped = [];
  for (const component of components) {
    if (component.length < 2) {
      ungrouped.push(component[0]);
      continue;
    }
    groups.push(buildGroupSummary(component, groups.length + 1, skills, pairMap));
  }

  groups.sort((a, b) => b.members.length - a.members.length || b.average_similarity - a.average_similarity);
  groups.forEach((group, index) => {
    group.group_id = `group_${String(index + 1).padStart(3, '0')}`;
    group.directory = path.join('groups', group.group_id);
  });

  return {
    groups,
    ungrouped: ungrouped.sort().map(id => {
      const skill = skills.find(item => item.id === id);
      return {
        skill_id: id,
        skill_name: skill?.skill_name || id,
        zip_name: skill?.zip_name || ''
      };
    })
  };
}

function buildGroupSummary(memberIds, index, skills, pairMap) {
  const skillById = new Map(skills.map(skill => [skill.id, skill]));
  const internalPairs = [];
  for (let i = 0; i < memberIds.length; i++) {
    for (let j = i + 1; j < memberIds.length; j++) {
      const pair = pairMap.get(normalizedPairKey(memberIds[i], memberIds[j]));
      if (pair) internalPairs.push(pair);
    }
  }

  const averageSimilarity = internalPairs.length
    ? internalPairs.reduce((sum, pair) => sum + pair.similarity_score, 0) / internalPairs.length
    : 0;
  const representative = chooseRepresentative(memberIds, internalPairs, skillById);

  return {
    group_id: `group_${String(index).padStart(3, '0')}`,
    directory: '',
    representative_skill: representative,
    average_similarity: round6(averageSimilarity),
    members: memberIds.map(id => ({
      skill_id: id,
      skill_name: skillById.get(id)?.skill_name || id,
      zip_name: skillById.get(id)?.zip_name || '',
      readme_missing: Boolean(skillById.get(id)?.readme_missing)
    })),
    pair_count: internalPairs.length
  };
}

function chooseRepresentative(memberIds, internalPairs, skillById) {
  const scores = new Map(memberIds.map(id => [id, { sum: 0, count: 0 }]));
  for (const pair of internalPairs) {
    scores.get(pair.source).sum += pair.similarity_score;
    scores.get(pair.source).count += 1;
    scores.get(pair.target).sum += pair.similarity_score;
    scores.get(pair.target).count += 1;
  }

  const bestId = memberIds
    .slice()
    .sort((a, b) => {
      const avgA = scores.get(a).count ? scores.get(a).sum / scores.get(a).count : 0;
      const avgB = scores.get(b).count ? scores.get(b).sum / scores.get(b).count : 0;
      if (avgA !== avgB) return avgB - avgA;
      return (skillById.get(a)?.skill_name || a).localeCompare(skillById.get(b)?.skill_name || b);
    })[0];

  return {
    skill_id: bestId,
    skill_name: skillById.get(bestId)?.skill_name || bestId
  };
}

function saveOutputs(result, skills, pairMap, outputDir) {
  fs.mkdirSync(outputDir, { recursive: true });
  const groupsDir = path.join(outputDir, 'groups');
  const ungroupedDir = path.join(outputDir, 'ungrouped');

  fs.rmSync(groupsDir, { recursive: true, force: true });
  fs.rmSync(ungroupedDir, { recursive: true, force: true });
  fs.mkdirSync(groupsDir, { recursive: true });
  fs.mkdirSync(ungroupedDir, { recursive: true });

  const skillById = new Map(skills.map(skill => [skill.id, skill]));
  const copiedBySkillId = new Map();

  for (const group of result.groups) {
    const groupDir = path.join(outputDir, group.directory);
    fs.mkdirSync(groupDir, { recursive: true });
    const manifest = buildGroupManifest(group, skillById, pairMap, groupDir, copiedBySkillId);
    fs.writeFileSync(path.join(groupDir, 'group_manifest.json'), JSON.stringify(manifest, null, 2), 'utf-8');
  }

  for (const item of result.ungrouped) {
    const skill = skillById.get(item.skill_id);
    if (!skill) continue;
    const copied = copyZipToDirectory(skill, ungroupedDir, copiedBySkillId);
    item.copied_zip = path.relative(outputDir, copied).replace(/\\/g, '/');
  }

  fs.writeFileSync(path.join(outputDir, 'grouping.json'), JSON.stringify(result, null, 2), 'utf-8');
  fs.writeFileSync(path.join(outputDir, 'grouping.md'), generateMarkdownReport(result), 'utf-8');
}

function buildGroupManifest(group, skillById, pairMap, groupDir, copiedBySkillId) {
  const memberIds = group.members.map(member => member.skill_id);
  const members = memberIds.map(id => {
    const skill = skillById.get(id);
    const copied = copyZipToDirectory(skill, groupDir, copiedBySkillId);
    return {
      skill_id: id,
      skill_name: skill.skill_name,
      zip_original_path: skill.zip_path,
      copied_zip: path.basename(copied),
      readme_missing: skill.readme_missing,
      skill_entry: skill.skill_entry,
      readme_entry: skill.readme_entry
    };
  });

  const pairSimilarities = [];
  for (let i = 0; i < memberIds.length; i++) {
    for (let j = i + 1; j < memberIds.length; j++) {
      const pair = pairMap.get(normalizedPairKey(memberIds[i], memberIds[j]));
      if (pair) pairSimilarities.push(serializePair(pair, Array.from(skillById.values())));
    }
  }

  return {
    group_id: group.group_id,
    representative_skill: group.representative_skill,
    average_similarity: group.average_similarity,
    members,
    pair_similarities: pairSimilarities.sort((a, b) => b.similarity_score - a.similarity_score)
  };
}

function copyZipToDirectory(skill, targetDir, copiedBySkillId) {
  if (!skill) throw new Error('Cannot copy missing skill');
  const existing = copiedBySkillId.get(`${skill.id}:${targetDir}`);
  if (existing) return existing;

  fs.mkdirSync(targetDir, { recursive: true });
  const safeName = uniqueZipName(skill, targetDir);
  const targetPath = path.join(targetDir, safeName);
  try {
    fs.linkSync(skill.zip_path, targetPath);
  } catch {
    fs.copyFileSync(skill.zip_path, targetPath);
  }
  copiedBySkillId.set(`${skill.id}:${targetDir}`, targetPath);
  return targetPath;
}

function uniqueZipName(skill, targetDir) {
  const preferred = sanitizeFileName(skill.zip_name || `${skill.skill_name}.zip`);
  let candidate = preferred.toLowerCase().endsWith('.zip') ? preferred : `${preferred}.zip`;
  if (!fs.existsSync(path.join(targetDir, candidate))) return candidate;

  const hash = crypto.createHash('sha1').update(skill.zip_path).digest('hex').slice(0, 8);
  const base = path.basename(candidate, path.extname(candidate));
  candidate = `${base}-${hash}.zip`;
  return candidate;
}

function generateMarkdownReport(result) {
  const lines = [];
  lines.push('# Skill Similarity Grouping');
  lines.push('');
  lines.push(`- Generated at: ${result.meta.generated_at}`);
  lines.push(`- Threshold: ${result.meta.threshold}`);
  lines.push(`- Valid skills: ${result.statistics.valid_skills}`);
  lines.push(`- Groups: ${result.statistics.group_count}`);
  lines.push(`- Ungrouped: ${result.statistics.ungrouped_skill_count}`);
  lines.push('');

  for (const group of result.groups) {
    lines.push(`## ${group.group_id}`);
    lines.push('');
    lines.push(`- Directory: \`${group.directory}\``);
    lines.push(`- Representative: ${group.representative_skill.skill_name}`);
    lines.push(`- Average similarity: ${group.average_similarity}`);
    lines.push('- Members:');
    for (const member of group.members) {
      lines.push(`  - ${member.skill_name} (${member.zip_name})${member.readme_missing ? ' [README missing]' : ''}`);
    }
    lines.push('');
  }

  if (result.ungrouped.length > 0) {
    lines.push('## Ungrouped');
    lines.push('');
    for (const item of result.ungrouped) {
      lines.push(`- ${item.skill_name} (${item.zip_name})`);
    }
    lines.push('');
  }

  if (result.errors.length > 0) {
    lines.push('## Errors');
    lines.push('');
    for (const error of result.errors) {
      lines.push(`- ${error.input || error.pair || 'general'}: ${error.reason}`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

function serializeSkill(skill) {
  return {
    id: skill.id,
    skill_name: skill.skill_name,
    description: skill.description,
    zip_path: skill.zip_path,
    zip_name: skill.zip_name,
    skill_entry: skill.skill_entry,
    readme_entry: skill.readme_entry,
    readme_missing: skill.readme_missing,
    profile: {
      headings: skill.profile.headings,
      action_tags: skill.profile.actionTags,
      platform_tags: skill.profile.platformTags,
      io_tags: skill.profile.ioTags,
      domain_terms: skill.profile.domainTerms,
      polarity_profile: skill.profile.polarityProfile
    }
  };
}

function serializePair(pair, skills) {
  const skillById = new Map(skills.map(skill => [skill.id, skill]));
  return {
    source: pair.source,
    source_name: skillById.get(pair.source)?.skill_name || pair.source,
    target: pair.target,
    target_name: skillById.get(pair.target)?.skill_name || pair.target,
    base_rule_score: pair.base_rule_score,
    rule_score: pair.rule_score,
    llm_score: pair.llm_score,
    similarity_score: round6(pair.similarity_score),
    semantic_distance: round6(pair.semantic_distance),
    components: pair.components,
    llm_reason: pair.llm_reason,
    llm_has_contradiction: pair.llm_has_contradiction,
    llm_contradiction_reason: pair.llm_contradiction_reason,
    llm_error: pair.llm_error
  };
}

function pairKey(pair) {
  return normalizedPairKey(pair.source, pair.target);
}

function normalizedPairKey(a, b) {
  return [a, b].sort().join('::');
}

function sanitizeFileName(value) {
  const safe = String(value || 'skill.zip')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/[. ]+$/g, '')
    .slice(0, 160);
  return safe || 'skill.zip';
}

function normalizeNumber(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function normalizeInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

function normalizeNonNegativeInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number >= 0 ? number : fallback;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round6(value) {
  return Math.round(Number(value || 0) * 1_000_000) / 1_000_000;
}

module.exports = {
  VERSION,
  DEFAULT_THRESHOLD,
  DEFAULT_TOP_K,
  analyzeSimilarity,
  parseArgs,
  printUsage,
  collectZipInputs,
  parseSkillZip,
  buildDocumentProfile,
  buildTfidfVectors,
  buildStreamingPairIndex,
  buildPairScores,
  buildGroups,
  buildGroupsFromPairMap,
  buildSemanticCacheKey,
  normalizeLlmSimilarityResult,
  pairKey,
  tokenize
};
