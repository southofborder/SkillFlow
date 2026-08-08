#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const {
  SkillFCGAnalyzer,
  saveToJson,
  saveFlowchartArtifacts,
  deriveFlowchartPaths
} = require('../src/index');

async function main(argv = process.argv.slice(2)) {
  try {
    const options = resolveOptions(parseArgs(argv));
    const summary = await runFcgBatch(options);
    console.log(`FCG batch completed: ${summary.success_count} succeeded, ${summary.error_count} failed`);
    console.log(`Summary: ${path.join(options.output, 'fcg-summary.json')}`);
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    printUsage();
    process.exit(1);
  }
}

function parseArgs(args) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--root' && i + 1 < args.length) {
      options.root = args[++i];
    } else if (arg === '--similarity-root' && i + 1 < args.length) {
      options.similarityRoot = args[++i];
    } else if (arg === '--output' && i + 1 < args.length) {
      options.output = args[++i];
    } else if (arg === '--scope' && i + 1 < args.length) {
      options.scope = args[++i];
    } else if (arg === '--concurrency' && i + 1 < args.length) {
      options.concurrency = Number(args[++i]);
    } else if (arg === '--mode' && i + 1 < args.length) {
      options.mode = args[++i];
    } else if (arg === '--llm-timeout' && i + 1 < args.length) {
      options.llmTimeout = Number(args[++i]);
    } else if (arg === '--label-llm-assist') {
      options.labelLlmAssist = true;
    } else if (arg === '--label-llm-concurrency' && i + 1 < args.length) {
      options.labelLlmConcurrency = Number(args[++i]);
    } else if (arg === '--label-llm-cache' && i + 1 < args.length) {
      options.labelLlmCache = args[++i];
    } else if (arg === '--semantic-gate-cache' && i + 1 < args.length) {
      options.semanticGateCache = args[++i];
    } else if (arg === '--refresh') {
      options.refresh = true;
    } else if (arg === '--only' && i + 1 < args.length) {
      // Comma-separated selector applied AFTER skill_id assignment, so it never
      // shifts positional skill_id numbering (which would orphan existing outputs
      // and force needless LLM re-spend). Each token substring-matches skill_id,
      // skill_name, or zip_name. Used to run beast-suspect skills in isolation.
      options.only = args[++i];
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return options;
}

function resolveOptions(options = {}) {
  if (options.help) return { help: true };
  const projectRoot = path.resolve(__dirname, '..', '..', '..');
  const root = path.resolve(options.root || path.join(projectRoot, 'results', 'clawhub-top10000'));
  const resolved = {
    root,
    similarityRoot: path.resolve(options.similarityRoot || path.join(root, 'similarity')),
    output: path.resolve(options.output || path.join(root, 'fcg')),
    scope: options.scope || 'all',
    concurrency: Number(options.concurrency || 4),
    mode: options.mode || 'full',
    labelLlmAssist: Boolean(options.labelLlmAssist),
    labelLlmConcurrency: Number(options.labelLlmConcurrency || 2),
    labelLlmCache: path.resolve(options.labelLlmCache || path.join(root, 'fcg', 'label-llm-cache.jsonl')),
    dependencyLlmCache: path.resolve(options.dependencyLlmCache || path.join(root, 'fcg', 'dependency-llm-cache.jsonl')),
    semanticGateCache: resolveSemanticGateCacheOption(options.semanticGateCache, root),
    refresh: Boolean(options.refresh),
    only: typeof options.only === 'string' ? options.only.trim() : '',
    llmProvider: options.llmProvider || process.env.LLM_PROVIDER || 'openai',
    llmModel: options.llmModel || process.env.LLM_MODEL || 'gpt-5.5',
    llmApiKey: Object.prototype.hasOwnProperty.call(options, 'llmApiKey')
      ? options.llmApiKey
      : (process.env.LLM_API_KEY || ''),
    llmEndpoint: options.llmEndpoint || process.env.LLM_ENDPOINT || '',
    llmTimeout: Number(options.llmTimeout || process.env.LLM_TIMEOUT || 180000)
  };

  validateOptions(resolved);
  return resolved;
}

// Pin the semantic-gate cache to <root>/fcg so it persists with the run and is
// reused across machines/CI, instead of the analyzer default of os.tmpdir().
// '0'/'false' disables caching; an explicit path is honored as-is.
function resolveSemanticGateCacheOption(value, root) {
  if (value === false) return false;
  const text = typeof value === 'string' ? value.trim() : '';
  if (text === '0' || text.toLowerCase() === 'false') return false;
  if (text) return path.resolve(text);
  return path.join(root, 'fcg', 'semantic-gate-cache.jsonl');
}

function validateOptions(options) {
  if (!['all', 'grouped', 'ungrouped'].includes(options.scope)) {
    throw new Error('--scope must be all, grouped, or ungrouped');
  }
  if (!['quick', 'full', 'deep'].includes(options.mode)) {
    throw new Error('--mode must be quick, full, or deep');
  }
  if (!Number.isInteger(options.concurrency) || options.concurrency <= 0) {
    throw new Error('--concurrency must be a positive integer');
  }
  if (options.labelLlmAssist && !String(options.llmApiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required when --label-llm-assist is enabled');
  }
  if (!String(options.llmApiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required for FCG Markdown semantic gate');
  }
}

async function runFcgBatch(options, deps = {}) {
  if (options.help) {
    printUsage();
    return null;
  }

  const skills = applyOnlyFilter(discoverSkills(options.root, options.similarityRoot, options.scope), options.only);
  const skillsDir = path.join(options.output, 'skills');
  fs.mkdirSync(skillsDir, { recursive: true });

  const queue = [...skills];
  const results = [];
  const errors = [];
  const workerCount = Math.min(Math.max(1, options.concurrency), queue.length || 1);
  const createAnalyzer = deps.createAnalyzer || (() => new SkillFCGAnalyzer({
    llmProvider: options.llmProvider,
    llmModel: options.llmModel,
    llmApiKey: options.llmApiKey,
    llmEndpoint: options.llmEndpoint,
    llmTimeout: options.llmTimeout,
    mode: options.mode,
    labelLlmAssist: options.labelLlmAssist,
    labelLlmConcurrency: options.labelLlmConcurrency,
    labelLlmCache: options.labelLlmCache,
    dependencyLlmCache: options.dependencyLlmCache,
    semanticGateCache: options.semanticGateCache
  }));

  const analyzeSkill = deps.analyzeSkill || analyzeOrReuseSkill;

  const workers = Array.from({ length: workerCount }, async () => {
    const analyzer = createAnalyzer();
    while (queue.length > 0) {
      const skill = queue.shift();
      if (!skill) break;
      const result = await analyzeSkill(skill, options, analyzer);
      if (result.error) errors.push(result.error);
      else results.push(result);
    }
    if (analyzer && typeof analyzer.cleanup === 'function') {
      analyzer.cleanup();
    }
  });

  await Promise.all(workers);

  const summary = buildSummary(options, skills, results, errors);
  saveJson(path.join(options.output, 'fcg-summary.json'), summary);
  fs.writeFileSync(path.join(options.output, 'fcg-summary.md'), renderSummaryMarkdown(summary), 'utf-8');
  return summary;
}

function discoverSkills(root, similarityRoot, scope = 'all') {
  const groupingPath = path.join(similarityRoot, 'grouping.json');
  if (fs.existsSync(groupingPath)) {
    return discoverSkillsFromGrouping(groupingPath, scope);
  }
  return discoverSkillsFromZips(path.join(root, 'zips'), scope);
}

function discoverSkillsFromGrouping(groupingPath, scope = 'all') {
  const grouping = JSON.parse(fs.readFileSync(groupingPath, 'utf-8'));
  const groupBySkillId = new Map();

  for (const group of grouping.groups || []) {
    for (const member of group.members || []) {
      if (member.skill_id) groupBySkillId.set(member.skill_id, group.group_id || '');
    }
  }

  const ungroupedIds = new Set((grouping.ungrouped || []).map(item => item.skill_id).filter(Boolean));
  const skills = (grouping.skills || []).map((skill, index) => {
    const groupId = groupBySkillId.get(skill.id) || '';
    const isUngrouped = ungroupedIds.has(skill.id) || !groupId;
    return {
      skill_id: skill.id || `skill_${index + 1}`,
      skill_name: skill.skill_name || skill.name || skill.id || `skill_${index + 1}`,
      zip_path: resolveZipPath(skill.zip_path, path.dirname(groupingPath)),
      zip_name: skill.zip_name || path.basename(skill.zip_path || ''),
      group_id: groupId,
      is_ungrouped: isUngrouped,
      readme_missing: Boolean(skill.readme_missing)
    };
  });

  return filterByScope(skills, scope);
}

function discoverSkillsFromZips(zipsDir, scope = 'all') {
  if (scope === 'grouped') return [];
  if (!fs.existsSync(zipsDir)) {
    throw new Error(`Neither grouping.json nor zips directory found: ${zipsDir}`);
  }
  return fs.readdirSync(zipsDir)
    .filter(name => /\.zip$/i.test(name))
    .sort((a, b) => a.localeCompare(b))
    .map((name, index) => ({
      skill_id: `skill_${String(index + 1).padStart(4, '0')}`,
      skill_name: path.basename(name, '.zip'),
      zip_path: path.join(zipsDir, name),
      zip_name: name,
      group_id: '',
      is_ungrouped: true,
      readme_missing: false
    }));
}

function filterByScope(skills, scope) {
  if (scope === 'grouped') return skills.filter(skill => !skill.is_ungrouped);
  if (scope === 'ungrouped') return skills.filter(skill => skill.is_ungrouped);
  return skills;
}

// Post-assignment selector: keep only skills whose skill_id / skill_name / zip_name
// contains any of the comma-separated tokens. Runs AFTER skill_id numbering so it
// never renumbers the corpus (which would orphan existing outputs). Empty = no-op.
function applyOnlyFilter(skills, only) {
  const tokens = String(only || '')
    .split(',')
    .map(t => t.trim().toLowerCase())
    .filter(Boolean);
  if (tokens.length === 0) return skills;
  return skills.filter(skill => {
    const hay = `${skill.skill_id || ''} ${skill.skill_name || ''} ${skill.zip_name || ''}`.toLowerCase();
    return tokens.some(t => hay.includes(t));
  });
}

function resolveZipPath(zipPath, baseDir) {
  if (!zipPath) return '';
  return path.isAbsolute(zipPath) ? path.resolve(zipPath) : path.resolve(baseDir, zipPath);
}

async function analyzeOrReuseSkill(skill, options, analyzer) {
  const outputPath = buildFcgOutputPath(skill, options.output);
  try {
    if (!skill.zip_path || !fs.existsSync(skill.zip_path)) {
      throw new Error(`Skill zip not found: ${skill.zip_path || '<empty>'}`);
    }

    if (!options.refresh && fs.existsSync(outputPath)) {
      const fcgJson = readJson(outputPath);
      ensureFlowchartArtifacts(fcgJson, outputPath);
      return buildResult(skill, outputPath, true, fcgJson);
    }

    const fcgJson = await analyzer.analyze(skill.zip_path);
    saveToJson(fcgJson, outputPath);
    ensureFlowchartArtifacts(fcgJson, outputPath);
    return buildResult(skill, outputPath, false, fcgJson);
  } catch (error) {
    return {
      error: {
        skill_id: skill.skill_id,
        skill_name: skill.skill_name,
        zip_path: skill.zip_path,
        fcg_path: outputPath,
        message: error.message
      }
    };
  }
}

function ensureFlowchartArtifacts(fcgJson, outputPath) {
  const flowPaths = deriveFlowchartPaths(outputPath);
  saveFlowchartArtifacts(fcgJson, flowPaths.markdownPath, flowPaths.mermaidPath);
}

function buildResult(skill, outputPath, reused, fcgJson) {
  return {
    skill_id: skill.skill_id,
    skill_name: skill.skill_name,
    group_id: skill.group_id,
    is_ungrouped: skill.is_ungrouped,
    zip_path: skill.zip_path,
    fcg_path: outputPath,
    reused,
    source_count: Number(fcgJson.security_profile?.sources?.length || fcgJson.source_sink?.sources?.length || 0),
    sink_count: Number(fcgJson.security_profile?.sinks?.length || fcgJson.source_sink?.sinks?.length || 0),
    flow_count: Number(
      fcgJson.security_profile?.observations?.length ||
      fcgJson.security_profile?.flows?.length ||
      fcgJson.paths?.source_to_sink_paths?.length ||
      0
    )
  };
}

function buildFcgOutputPath(skill, outputDir) {
  const skillsDir = path.join(outputDir, 'skills');
  const base = `${safeBaseName(skill.skill_id)}-${safeBaseName(skill.skill_name || skill.zip_name || 'skill')}`.slice(0, 180);
  return path.join(skillsDir, `${base}-fcg.json`);
}

function safeBaseName(value) {
  return String(value || 'skill')
    .replace(/\.zip$/i, '')
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')
    .replace(/\s+/g, '_')
    .slice(0, 160) || 'skill';
}

function buildSummary(options, skills, results, errors) {
  const sortedResults = results.slice().sort((a, b) => a.skill_id.localeCompare(b.skill_id));
  const sortedErrors = errors.slice().sort((a, b) => String(a.skill_id).localeCompare(String(b.skill_id)));
  return {
    generated_at: new Date().toISOString(),
    root: options.root,
    similarity_root: options.similarityRoot,
    output: options.output,
    scope: options.scope,
    mode: options.mode,
    total_skills: skills.length,
    success_count: sortedResults.length,
    reused_count: sortedResults.filter(result => result.reused).length,
    analyzed_count: sortedResults.filter(result => !result.reused).length,
    error_count: sortedErrors.length,
    results: sortedResults,
    errors: sortedErrors
  };
}

function renderSummaryMarkdown(summary) {
  const lines = [];
  lines.push('# FCG Batch Summary');
  lines.push('');
  lines.push(`- Generated: ${summary.generated_at}`);
  lines.push(`- Root: ${summary.root}`);
  lines.push(`- Scope: ${summary.scope}`);
  lines.push(`- Total skills: ${summary.total_skills}`);
  lines.push(`- Success: ${summary.success_count}`);
  lines.push(`- Reused: ${summary.reused_count}`);
  lines.push(`- Analyzed: ${summary.analyzed_count}`);
  lines.push(`- Errors: ${summary.error_count}`);
  lines.push('');

  if (summary.errors.length > 0) {
    lines.push('## Errors');
    lines.push('');
    lines.push('| Skill | Message |');
    lines.push('| --- | --- |');
    for (const error of summary.errors.slice(0, 100)) {
      lines.push(`| ${escapePipe(error.skill_name || error.skill_id)} | ${escapePipe(error.message)} |`);
    }
    lines.push('');
  }

  lines.push('## Outputs');
  lines.push('');
  lines.push('| Skill | Sources | Sinks | Flows | Reused | FCG JSON |');
  lines.push('| --- | ---: | ---: | ---: | --- | --- |');
  for (const result of summary.results.slice(0, 100)) {
    lines.push(`| ${escapePipe(result.skill_name)} | ${result.source_count} | ${result.sink_count} | ${result.flow_count} | ${result.reused ? 'yes' : 'no'} | ${escapePipe(result.fcg_path)} |`);
  }

  return lines.join('\n');
}

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/fcg-batch.js --root <clawhub-run-root> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --root <dir>                 Run root containing zips/ or similarity/grouping.json');
  console.log('  --similarity-root <dir>      Default <root>/similarity');
  console.log('  --output <dir>               Default <root>/fcg');
  console.log('  --scope all|grouped|ungrouped  Default all');
  console.log('  --concurrency <n>            Default 4');
  console.log('  --mode quick|full|deep       Default full');
  console.log('  --label-llm-assist          Enable low-confidence label LLM assist');
  console.log('  --label-llm-concurrency <n> Default 2');
  console.log('  --label-llm-cache <file>    Default <root>/fcg/label-llm-cache.jsonl');
  console.log('  --semantic-gate-cache <file> Default <root>/fcg/semantic-gate-cache.jsonl (0/false to disable)');
  console.log('  --refresh                    Re-run FCG when JSON exists');
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function saveJson(filePath, value) {
  fs.mkdirSync(path.dirname(path.resolve(filePath)), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2), 'utf-8');
}

function escapePipe(value) {
  return String(value ?? '').replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  resolveOptions,
  validateOptions,
  runFcgBatch,
  discoverSkills,
  discoverSkillsFromGrouping,
  discoverSkillsFromZips,
  filterByScope,
  buildFcgOutputPath,
  safeBaseName,
  buildSummary,
  renderSummaryMarkdown
};
