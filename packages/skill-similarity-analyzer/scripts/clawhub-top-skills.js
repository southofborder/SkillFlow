#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const {
  fetchTopSkills,
  downloadSkillZip,
  DEFAULT_API_BASE
} = require('../src/clawhub/client');
const { analyzeSimilarity } = require('../src/grouping');

const DEFAULT_ROOT = path.resolve(__dirname, '..', '..', '..', 'results', 'clawhub-top10000');

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/clawhub-top-skills.js [--semantic-llm] [--phase list|download|list-download|group|all]');
  console.log('');
  console.log('Options:');
  console.log('  --k <n>, -k <n>             Number of top skills to process');
  console.log('  --limit <n>                 Default: 10000');
  console.log(`  --root <dir>                Default: ${DEFAULT_ROOT}`);
  console.log('  --sort downloads|stars|installs  Default: downloads');
  console.log('  --non-suspicious-only       Filter ClawHub suspicious/malicious skills');
  console.log('  --download-concurrency <n>  Default: 8');
  console.log('  --llm-concurrency <n>       Default: 2');
  console.log('  --top-k <n>                 Default: 5');
  console.log('  --threshold <n>             Default: 0.68');
  console.log('  --api-base <url>            Default: https://clawhub.ai/api/v1');
  console.log('  --timeout-ms <n>            Default: 30000');
  console.log('  --retries <n>               Default: 4');
}

function parseArgs(argv) {
  const options = {
    limit: 10000,
    root: DEFAULT_ROOT,
    sort: 'downloads',
    nonSuspiciousOnly: false,
    downloadConcurrency: 8,
    llmConcurrency: 2,
    topK: 5,
    threshold: 0.68,
    phase: 'all',
    semanticLlm: false,
    apiBase: DEFAULT_API_BASE,
    timeoutMs: 30000,
    retries: 4,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if ((arg === '--k' || arg === '-k' || arg === '--limit') && i + 1 < argv.length) {
      options.limit = Number(argv[++i]);
    } else if (arg === '--root' && i + 1 < argv.length) {
      options.root = argv[++i];
    } else if (arg === '--sort' && i + 1 < argv.length) {
      options.sort = argv[++i];
    } else if (arg === '--non-suspicious-only') {
      options.nonSuspiciousOnly = true;
    } else if (arg === '--download-concurrency' && i + 1 < argv.length) {
      options.downloadConcurrency = Number(argv[++i]);
    } else if (arg === '--llm-concurrency' && i + 1 < argv.length) {
      options.llmConcurrency = Number(argv[++i]);
    } else if (arg === '--top-k' && i + 1 < argv.length) {
      options.topK = Number(argv[++i]);
    } else if (arg === '--threshold' && i + 1 < argv.length) {
      options.threshold = Number(argv[++i]);
    } else if (arg === '--phase' && i + 1 < argv.length) {
      options.phase = argv[++i];
    } else if (arg === '--semantic-llm') {
      options.semanticLlm = true;
    } else if (arg === '--api-base' && i + 1 < argv.length) {
      options.apiBase = argv[++i];
    } else if (arg === '--timeout-ms' && i + 1 < argv.length) {
      options.timeoutMs = Number(argv[++i]);
    } else if (arg === '--retries' && i + 1 < argv.length) {
      options.retries = Number(argv[++i]);
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  validateOptions(options);
  options.root = path.resolve(options.root);
  return options;
}

function validateOptions(options) {
  if (!Number.isInteger(options.limit) || options.limit <= 0) throw new Error('--limit must be a positive integer');
  if (!['downloads', 'stars', 'installs'].includes(options.sort)) throw new Error('--sort must be downloads, stars, or installs');
  if (!['list', 'download', 'list-download', 'group', 'all'].includes(options.phase)) throw new Error('--phase must be list, download, list-download, group, or all');
  if (!Number.isInteger(options.downloadConcurrency) || options.downloadConcurrency <= 0) throw new Error('--download-concurrency must be a positive integer');
  if (!Number.isInteger(options.llmConcurrency) || options.llmConcurrency <= 0) throw new Error('--llm-concurrency must be a positive integer');
  if (!Number.isInteger(options.topK) || options.topK <= 0) throw new Error('--top-k must be a positive integer');
  if (!Number.isFinite(options.threshold) || options.threshold < 0 || options.threshold > 1) throw new Error('--threshold must be a number in [0, 1]');
  if (!Number.isInteger(options.timeoutMs) || options.timeoutMs <= 0) throw new Error('--timeout-ms must be a positive integer');
  if (!Number.isInteger(options.retries) || options.retries < 0) throw new Error('--retries must be a non-negative integer');
}

function getPaths(root) {
  return {
    root,
    zipsDir: path.join(root, 'zips'),
    manifestsDir: path.join(root, 'manifests'),
    similarityDir: path.join(root, 'similarity'),
    topSkills: path.join(root, 'manifests', 'top-skills.json'),
    downloadsJsonl: path.join(root, 'manifests', 'downloads.jsonl'),
    downloadSummary: path.join(root, 'manifests', 'download-summary.json'),
    semanticCache: path.join(root, 'similarity', 'semantic-cache.jsonl')
  };
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`Argument error: ${error.message}`);
    printUsage();
    process.exit(1);
  }

  if (options.help) {
    printUsage();
    return;
  }

  const paths = getPaths(options.root);
  fs.mkdirSync(paths.zipsDir, { recursive: true });
  fs.mkdirSync(paths.manifestsDir, { recursive: true });
  fs.mkdirSync(paths.similarityDir, { recursive: true });

  try {
    if (options.phase === 'list' || options.phase === 'list-download' || options.phase === 'all') {
      await runListPhase(options, paths);
    }
    if (options.phase === 'download' || options.phase === 'list-download' || options.phase === 'all') {
      await runDownloadPhase(options, paths);
    }
    if (options.phase === 'group' || options.phase === 'all') {
      await runGroupPhase(options, paths);
    }
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    process.exit(1);
  }
}

async function runListPhase(options, paths) {
  console.log(`Listing top ${options.limit} ClawHub skills by ${options.sort}`);
  const manifest = await fetchTopSkills({
    limit: options.limit,
    sort: options.sort,
    nonSuspiciousOnly: options.nonSuspiciousOnly,
    apiBase: options.apiBase,
    timeoutMs: options.timeoutMs,
    retries: options.retries,
    onPage: page => {
      console.log(`Listed page ${page.page}: +${page.fetched}, total ${page.total}`);
    }
  });
  fs.writeFileSync(paths.topSkills, JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`Wrote ${manifest.total} skills to ${paths.topSkills}`);
}

async function runDownloadPhase(options, paths) {
  const manifest = loadTopSkills(paths.topSkills);
  console.log(`Downloading ${manifest.items.length} skill zips to ${paths.zipsDir}`);

  const existing = loadDownloadStatus(paths.downloadsJsonl);
  const queue = manifest.items.filter(item => existing.get(item.slug)?.status !== 'ok' && existing.get(item.slug)?.status !== 'skipped');
  console.log(`Pending downloads: ${queue.length}`);

  let completed = 0;
  let failed = 0;
  await runConcurrent(queue, options.downloadConcurrency, async item => {
    try {
      const result = await downloadSkillZip(item, paths.zipsDir, {
        apiBase: options.apiBase,
        timeoutMs: options.timeoutMs,
        retries: options.retries,
        skipExisting: true
      });
      completed += 1;
      appendJsonl(paths.downloadsJsonl, { ...result, rank: item.rank, latest_version: item.latest_version });
      console.log(`[${completed + failed}/${queue.length}] ${result.status.toUpperCase()} ${item.slug}`);
    } catch (error) {
      failed += 1;
      appendJsonl(paths.downloadsJsonl, {
        slug: item.slug,
        rank: item.rank,
        status: 'failed',
        reason: error.message,
        latest_version: item.latest_version,
        at: new Date().toISOString()
      });
      console.warn(`[${completed + failed}/${queue.length}] FAIL ${item.slug}: ${error.message}`);
    }
  });

  writeDownloadSummary(paths, manifest);
}

async function runGroupPhase(options, paths) {
  if (options.semanticLlm && !String(process.env.LLM_API_KEY || '').trim()) {
    throw new Error('--semantic-llm requires LLM_API_KEY');
  }

  console.log(`Grouping zips from ${paths.zipsDir}`);
  const result = await analyzeSimilarity([paths.zipsDir], {
    output: paths.similarityDir,
    threshold: options.threshold,
    topK: options.topK,
    semanticLlm: options.semanticLlm,
    llmConcurrency: options.llmConcurrency,
    semanticCachePath: paths.semanticCache,
    onPairProgress: progress => {
      const elapsedSeconds = Math.round(progress.elapsedMs / 1000);
      const theoretical = progress.theoreticalPairCount
        ? `, theoretical ${progress.theoreticalPairCount}`
        : '';
      const strategy = progress.strategy ? `${progress.strategy} ` : '';
      console.log(`Scored ${strategy}${progress.pairCount}/${progress.totalPairs} pairs${theoretical} (${progress.percent}%) after ${elapsedSeconds}s`);
    }
  });
  console.log(`Pair strategy: ${result.statistics.pair_index_strategy}`);
  console.log(`Scored pairs: ${result.statistics.scored_pair_count}/${result.statistics.theoretical_pair_count}`);
  console.log(`Grouped ${result.statistics.grouped_skill_count} skills into ${result.statistics.group_count} groups`);
  console.log(`Ungrouped skills: ${result.statistics.ungrouped_skill_count}`);
  console.log(`Output: ${paths.similarityDir}`);
}

function loadTopSkills(topSkillsPath) {
  if (!fs.existsSync(topSkillsPath)) {
    throw new Error(`Missing top skills manifest: ${topSkillsPath}. Run --phase list first.`);
  }
  const manifest = JSON.parse(fs.readFileSync(topSkillsPath, 'utf-8'));
  if (!Array.isArray(manifest.items)) {
    throw new Error(`Invalid top skills manifest: ${topSkillsPath}`);
  }
  return manifest;
}

function loadDownloadStatus(jsonlPath) {
  const status = new Map();
  if (!fs.existsSync(jsonlPath)) return status;
  const lines = fs.readFileSync(jsonlPath, 'utf-8').split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const item = JSON.parse(line);
      if (item.slug) status.set(item.slug, item);
    } catch {
      // Ignore partial JSONL lines from interrupted runs.
    }
  }
  return status;
}

function writeDownloadSummary(paths, manifest) {
  const status = Array.from(loadDownloadStatus(paths.downloadsJsonl).values());
  const summary = {
    generated_at: new Date().toISOString(),
    requested: manifest.items.length,
    ok: status.filter(item => item.status === 'ok').length,
    skipped: status.filter(item => item.status === 'skipped').length,
    failed: status.filter(item => item.status === 'failed').length,
    zips_dir: paths.zipsDir,
    downloads_jsonl: paths.downloadsJsonl
  };
  fs.writeFileSync(paths.downloadSummary, JSON.stringify(summary, null, 2), 'utf-8');
  console.log(`Download summary: ${paths.downloadSummary}`);
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

function appendJsonl(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.appendFileSync(filePath, `${JSON.stringify(value)}\n`, 'utf-8');
}

if (require.main === module) {
  main();
}

module.exports = {
  DEFAULT_ROOT,
  parseArgs,
  getPaths,
  runListPhase,
  runDownloadPhase,
  runGroupPhase
};
