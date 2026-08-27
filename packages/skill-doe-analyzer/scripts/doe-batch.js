#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const { analyzeDoeAsync } = require('../src/doe-analyzer');

async function main(argv = process.argv.slice(2)) {
  try {
    const options = resolveOptions(parseArgs(argv));
    const summary = await runDoeBatch(options);
    console.log(`DOE batch completed: ${summary.success_count} succeeded, ${summary.error_count} failed`);
    console.log(`Summary: ${path.join(options.output, 'doe-summary.json')}`);
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    printUsage();
    process.exit(1);
  }
}

function parseArgs(args = []) {
  const options = {};
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') options.help = true;
    else if (arg === '--root' && i + 1 < args.length) options.root = args[++i];
    else if (arg === '--fcg-root' && i + 1 < args.length) options.fcgRoot = args[++i];
    else if (arg === '--output' && i + 1 < args.length) options.output = args[++i];
    else if (arg === '--concurrency' && i + 1 < args.length) options.concurrency = Number(args[++i]);
    else if (arg === '--threshold' && i + 1 < args.length) options.threshold = Number(args[++i]);
    else if (arg === '--llm-cache' && i + 1 < args.length) options.llmCache = args[++i];
    else if (arg === '--llm-batch-size' && i + 1 < args.length) options.llmBatchSize = Number(args[++i]);
    else if (arg === '--llm-votes' && i + 1 < args.length) options.llmVotes = Number(args[++i]);
    else if (arg === '--llm-concurrency' && i + 1 < args.length) options.llmConcurrency = Number(args[++i]);
    else if (arg === '--llm-escalation-votes' && i + 1 < args.length) options.llmEscalationVotes = Number(args[++i]);
    else if (arg === '--llm-escalation-policy' && i + 1 < args.length) options.llmEscalationPolicy = args[++i];
    else if (arg === '--llm-max-batch-chars' && i + 1 < args.length) options.llmMaxBatchChars = Number(args[++i]);
    else if (arg === '--evidence-max-pack-chars' && i + 1 < args.length) options.evidenceMaxPackChars = Number(args[++i]);
    else if (arg === '--evidence-path-node-window' && i + 1 < args.length) options.evidencePathNodeWindow = Number(args[++i]);
    else if (arg === '--evidence-max-text-chars' && i + 1 < args.length) options.evidenceMaxTextChars = Number(args[++i]);
    else if (arg === '--evidence-max-array-items' && i + 1 < args.length) options.evidenceMaxArrayItems = Number(args[++i]);
    else if (arg === '--adaptive-timeout-max-ms' && i + 1 < args.length) options.adaptiveTimeoutMaxMs = Number(args[++i]);
    else if (arg === '--llm-timeout' && i + 1 < args.length) options.llmTimeout = Number(args[++i]);
    else if (arg === '--no-llm-judge') options.llmJudge = false;
    else if (arg === '--refresh') options.refresh = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return options;
}

function resolveOptions(options = {}) {
  if (options.help) return { help: true };
  const projectRoot = path.resolve(__dirname, '..', '..', '..');
  const root = path.resolve(options.root || path.join(projectRoot, 'results', 'clawhub-top10000'));
  const output = path.resolve(options.output || path.join(root, 'doe'));
  const resolved = {
    root,
    fcgRoot: path.resolve(options.fcgRoot || path.join(root, 'fcg')),
    output,
    concurrency: Number(options.concurrency || 2),
    threshold: options.threshold,
    llmJudge: options.llmJudge !== false,
    llmCache: path.resolve(options.llmCache || path.join(output, 'doe-llm-cache.jsonl')),
    llmBatchSize: options.llmBatchSize,
    llmVotes: options.llmVotes,
    llmConcurrency: options.llmConcurrency,
    llmEscalationVotes: options.llmEscalationVotes,
    llmEscalationPolicy: options.llmEscalationPolicy,
    llmMaxBatchChars: options.llmMaxBatchChars,
    evidenceMaxPackChars: options.evidenceMaxPackChars,
    evidencePathNodeWindow: options.evidencePathNodeWindow,
    evidenceMaxTextChars: options.evidenceMaxTextChars,
    evidenceMaxArrayItems: options.evidenceMaxArrayItems,
    adaptiveTimeoutMaxMs: options.adaptiveTimeoutMaxMs,
    llmTimeout: options.llmTimeout,
    refresh: Boolean(options.refresh),
    llmApiKey: Object.prototype.hasOwnProperty.call(options, 'llmApiKey')
      ? options.llmApiKey
      : (process.env.LLM_API_KEY || '')
  };
  validateOptions(resolved);
  return resolved;
}

function validateOptions(options) {
  if (!Number.isInteger(options.concurrency) || options.concurrency <= 0) {
    throw new Error('--concurrency must be a positive integer');
  }
  if (options.threshold !== undefined && (!Number.isFinite(options.threshold) || options.threshold < 0 || options.threshold > 1)) {
    throw new Error('--threshold must be a number in [0, 1]');
  }
  if (options.llmBatchSize !== undefined && (!Number.isInteger(options.llmBatchSize) || options.llmBatchSize <= 0)) {
    throw new Error('--llm-batch-size must be a positive integer');
  }
  if (options.llmVotes !== undefined && (!Number.isInteger(options.llmVotes) || options.llmVotes <= 0)) {
    throw new Error('--llm-votes must be a positive integer');
  }
  if (options.llmConcurrency !== undefined && (!Number.isInteger(options.llmConcurrency) || options.llmConcurrency <= 0)) {
    throw new Error('--llm-concurrency must be a positive integer');
  }
  if (options.llmEscalationVotes !== undefined && (!Number.isInteger(options.llmEscalationVotes) || options.llmEscalationVotes <= 0)) {
    throw new Error('--llm-escalation-votes must be a positive integer');
  }
  if (options.llmEscalationPolicy !== undefined && !['risk_or_uncertain', 'none', 'all'].includes(String(options.llmEscalationPolicy))) {
    throw new Error('--llm-escalation-policy must be risk_or_uncertain, none, or all');
  }
  if (options.llmMaxBatchChars !== undefined && (!Number.isInteger(options.llmMaxBatchChars) || options.llmMaxBatchChars <= 0)) {
    throw new Error('--llm-max-batch-chars must be a positive integer');
  }
  if (options.evidenceMaxPackChars !== undefined && (!Number.isInteger(options.evidenceMaxPackChars) || options.evidenceMaxPackChars <= 0)) {
    throw new Error('--evidence-max-pack-chars must be a positive integer');
  }
  if (options.evidencePathNodeWindow !== undefined && (!Number.isInteger(options.evidencePathNodeWindow) || options.evidencePathNodeWindow < 0)) {
    throw new Error('--evidence-path-node-window must be a non-negative integer');
  }
  if (options.evidenceMaxTextChars !== undefined && (!Number.isInteger(options.evidenceMaxTextChars) || options.evidenceMaxTextChars <= 0)) {
    throw new Error('--evidence-max-text-chars must be a positive integer');
  }
  if (options.evidenceMaxArrayItems !== undefined && (!Number.isInteger(options.evidenceMaxArrayItems) || options.evidenceMaxArrayItems <= 0)) {
    throw new Error('--evidence-max-array-items must be a positive integer');
  }
  if (options.adaptiveTimeoutMaxMs !== undefined && (!Number.isInteger(options.adaptiveTimeoutMaxMs) || options.adaptiveTimeoutMaxMs <= 0)) {
    throw new Error('--adaptive-timeout-max-ms must be a positive integer');
  }
  if (options.llmTimeout !== undefined && (!Number.isInteger(options.llmTimeout) || options.llmTimeout <= 0)) {
    throw new Error('--llm-timeout must be a positive integer');
  }
  if (options.llmJudge && !String(options.llmApiKey || '').trim()) {
    throw new Error('LLM_API_KEY is required for DOE LLM judge; pass --no-llm-judge for rule-only analysis');
  }
}

async function runDoeBatch(options, deps = {}) {
  if (options.help) {
    printUsage();
    return null;
  }
  const fcgFiles = discoverFcgFiles(options.fcgRoot);
  const outputDir = path.join(options.output, 'skills');
  fs.mkdirSync(outputDir, { recursive: true });

  const queue = [...fcgFiles];
  const results = [];
  const errors = [];
  const workerCount = Math.min(Math.max(1, options.concurrency), queue.length || 1);
  const analyze = deps.analyze || analyzeFcgFile;

  const workers = Array.from({ length: workerCount }, async () => {
    while (queue.length > 0) {
      const fcgPath = queue.shift();
      if (!fcgPath) break;
      const result = await analyze(fcgPath, options);
      if (result.error) errors.push(result.error);
      else results.push(result);
    }
  });
  await Promise.all(workers);

  const summary = buildSummary({ options, fcgFiles, results, errors });
  saveJson(path.join(options.output, 'doe-summary.json'), summary);
  fs.writeFileSync(path.join(options.output, 'doe-summary.md'), renderSummaryMarkdown(summary), 'utf-8');
  return summary;
}

async function analyzeFcgFile(fcgPath, options) {
  const outputPath = buildDoeOutputPath(fcgPath, options.output);
  if (!options.refresh && fs.existsSync(outputPath)) {
    const cached = readJson(outputPath);
    return summarizeDoeResult({ fcgPath, outputPath, result: cached, reused: true });
  }

  try {
    const fcg = readJson(fcgPath);
    const result = await analyzeDoeAsync(fcg, {
      inputFcg: fcgPath,
      threshold: options.threshold,
      llmJudge: options.llmJudge,
      llmCache: options.llmCache,
      llmBatchSize: options.llmBatchSize,
      llmVotes: options.llmVotes,
      llmConcurrency: options.llmConcurrency,
      llmEscalationVotes: options.llmEscalationVotes,
      llmEscalationPolicy: options.llmEscalationPolicy,
      llmMaxBatchChars: options.llmMaxBatchChars,
      evidenceMaxPackChars: options.evidenceMaxPackChars,
      evidencePathNodeWindow: options.evidencePathNodeWindow,
      evidenceMaxTextChars: options.evidenceMaxTextChars,
      evidenceMaxArrayItems: options.evidenceMaxArrayItems,
      adaptiveTimeoutMaxMs: options.adaptiveTimeoutMaxMs,
      llmTimeout: options.llmTimeout
    });
    saveJson(outputPath, result);
    return summarizeDoeResult({ fcgPath, outputPath, result, reused: false });
  } catch (error) {
    return {
      error: {
        fcg_path: fcgPath,
        doe_path: outputPath,
        message: error.message
      }
    };
  }
}

function discoverFcgFiles(fcgRoot) {
  const root = path.resolve(fcgRoot);
  const skillsDir = path.join(root, 'skills');
  const searchDir = fs.existsSync(skillsDir) && fs.statSync(skillsDir).isDirectory() ? skillsDir : root;
  if (!fs.existsSync(searchDir)) return [];
  return fs.readdirSync(searchDir)
    .filter(name => name.endsWith('-sfg.json'))
    .map(name => path.join(searchDir, name))
    .sort((a, b) => a.localeCompare(b));
}

function buildDoeOutputPath(fcgPath, outputRoot) {
  const fileName = path.basename(fcgPath);
  const base = /-sfg\.json$/i.test(fileName)
    ? fileName.replace(/-sfg\.json$/i, '-doe.json')
    : fileName.replace(/\.json$/i, '-doe.json');
  return path.join(outputRoot, 'skills', base);
}

function summarizeDoeResult({ fcgPath, outputPath, result, reused }) {
  const stats = result.statistics || {};
  return {
    skill_name: result.meta?.skill_name || result.skill_name || path.basename(fcgPath, '.json'),
    fcg_path: fcgPath,
    doe_path: outputPath,
    reused: Boolean(reused),
    assessment_count: Number(stats.assessment_count || 0),
    boundary_crossing_count: Number(stats.boundary_crossing_count || 0),
    potential_doe_count: Number(stats.potential_doe_count || 0),
    high_score_count: Number(stats.high_score_count || 0),
    requires_review_count: Number(stats.requires_review_count || 0),
    llm_cache_hit_count: Number(stats.llm_cache_hit_count || 0),
    llm_first_pass_count: Number(stats.llm_first_pass_count || 0),
    llm_escalated_count: Number(stats.llm_escalated_count || 0),
    llm_timeout_split_count: Number(stats.llm_timeout_split_count || 0),
    llm_task_memory_node_count: Number(stats.llm_task_memory_node_count || 0),
    llm_task_memory_doc_source_count: Number(stats.llm_task_memory_doc_source_count || 0),
    warning_count: Number(stats.warning_count || 0)
  };
}

function buildSummary({ options, fcgFiles, results, errors }) {
  const sortedResults = results.slice().sort((a, b) => a.fcg_path.localeCompare(b.fcg_path));
  const sortedErrors = errors.slice().sort((a, b) => a.fcg_path.localeCompare(b.fcg_path));
  return {
    generated_at: new Date().toISOString(),
    root: options.root,
    fcg_root: options.fcgRoot,
    output: options.output,
    llm_judge: options.llmJudge,
    total_fcg_files: fcgFiles.length,
    success_count: sortedResults.length,
    reused_count: sortedResults.filter(result => result.reused).length,
    analyzed_count: sortedResults.filter(result => !result.reused).length,
    error_count: sortedErrors.length,
    assessment_count: sum(sortedResults, 'assessment_count'),
    boundary_crossing_count: sum(sortedResults, 'boundary_crossing_count'),
    potential_doe_count: sum(sortedResults, 'potential_doe_count'),
    high_score_count: sum(sortedResults, 'high_score_count'),
    requires_review_count: sum(sortedResults, 'requires_review_count'),
    llm_cache_hit_count: sum(sortedResults, 'llm_cache_hit_count'),
    llm_first_pass_count: sum(sortedResults, 'llm_first_pass_count'),
    llm_escalated_count: sum(sortedResults, 'llm_escalated_count'),
    llm_timeout_split_count: sum(sortedResults, 'llm_timeout_split_count'),
    llm_task_memory_node_count: sum(sortedResults, 'llm_task_memory_node_count'),
    llm_task_memory_doc_source_count: sum(sortedResults, 'llm_task_memory_doc_source_count'),
    warning_count: sum(sortedResults, 'warning_count'),
    results: sortedResults,
    errors: sortedErrors
  };
}

function renderSummaryMarkdown(summary) {
  const lines = [];
  lines.push('# DOE Batch Summary');
  lines.push('');
  lines.push(`- Generated: ${summary.generated_at}`);
  lines.push(`- FCG root: ${summary.fcg_root}`);
  lines.push(`- Total FCG files: ${summary.total_fcg_files}`);
  lines.push(`- Success: ${summary.success_count}`);
  lines.push(`- Reused: ${summary.reused_count}`);
  lines.push(`- Analyzed: ${summary.analyzed_count}`);
  lines.push(`- Errors: ${summary.error_count}`);
  lines.push(`- Assessments: ${summary.assessment_count}`);
  lines.push(`- Boundary crossings: ${summary.boundary_crossing_count}`);
  lines.push(`- Potential DOE: ${summary.potential_doe_count}`);
  lines.push(`- High score: ${summary.high_score_count}`);
  lines.push(`- Requires review: ${summary.requires_review_count}`);
  lines.push(`- LLM first-pass judgements: ${summary.llm_first_pass_count}`);
  lines.push(`- LLM escalated judgements: ${summary.llm_escalated_count}`);
  lines.push(`- LLM timeout batch splits: ${summary.llm_timeout_split_count}`);
  lines.push(`- LLM task memory nodes: ${summary.llm_task_memory_node_count}`);
  lines.push(`- LLM task memory doc sources: ${summary.llm_task_memory_doc_source_count}`);
  lines.push('');

  if (summary.errors.length > 0) {
    lines.push('## Errors');
    lines.push('');
    lines.push('| FCG | Message |');
    lines.push('| --- | --- |');
    for (const error of summary.errors.slice(0, 100)) {
      lines.push(`| ${escapePipe(error.fcg_path)} | ${escapePipe(error.message)} |`);
    }
    lines.push('');
  }

  lines.push('## Outputs');
  lines.push('');
  lines.push('| FCG | Assessments | Potential DOE | Review | Reused | DOE JSON |');
  lines.push('| --- | ---: | ---: | ---: | --- | --- |');
  for (const result of summary.results.slice(0, 100)) {
    lines.push(`| ${escapePipe(result.fcg_path)} | ${result.assessment_count} | ${result.potential_doe_count} | ${result.requires_review_count} | ${result.reused ? 'yes' : 'no'} | ${escapePipe(result.doe_path)} |`);
  }

  return lines.join('\n');
}

function sum(items, key) {
  return items.reduce((total, item) => total + Number(item[key] || 0), 0);
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

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/doe-batch.js --root <clawhub-run-root> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --root <dir>                Run root containing fcg/skills');
  console.log('  --fcg-root <dir>            Default <root>/fcg');
  console.log('  --output <dir>              Default <root>/doe');
  console.log('  --concurrency <n>           Default 2');
  console.log('  --threshold <n>             High-score threshold');
  console.log('  --llm-cache <file>          Default <root>/doe/doe-llm-cache.jsonl');
  console.log('  --llm-batch-size <n>        DOE LLM judge batch size');
  console.log('  --llm-votes <n>             First-pass DOE LLM judge votes per unit, default 1');
  console.log('  --llm-concurrency <n>       Concurrent DOE LLM judge requests, default 2');
  console.log('  --llm-escalation-votes <n>  Votes for escalated units, default 3');
  console.log('  --llm-escalation-policy <m> risk_or_uncertain|none|all');
  console.log('  --llm-max-batch-chars <n>   Approximate max chars per LLM batch');
  console.log('  --evidence-max-pack-chars <n>   Per-pack context ceiling; only oversized packs are reduced (default 100000)');
  console.log('  --evidence-path-node-window <n> Head/tail full path nodes kept when trimming (default 4)');
  console.log('  --evidence-max-text-chars <n>   Free-text cap applied only during trimming (default 2000)');
  console.log('  --evidence-max-array-items <n>  Verbose-array cap applied only during trimming (default 40)');
  console.log('  --adaptive-timeout-max-ms <ms>  Upper bound for size-scaled request timeout');
  console.log('  --llm-timeout <ms>          LLM timeout (base; scales up with payload size)');
  console.log('  --no-llm-judge              Rule-only DOE analysis');
  console.log('  --refresh                   Re-run DOE when JSON exists');
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  resolveOptions,
  validateOptions,
  discoverFcgFiles,
  buildDoeOutputPath,
  runDoeBatch,
  analyzeFcgFile,
  summarizeDoeResult
};
