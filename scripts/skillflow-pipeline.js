#!/usr/bin/env node

require('../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const DEFAULT_CONFIG = path.resolve(__dirname, '..', 'skillflow-pipeline.config.cjs');

function parseArgs(argv) {
  const cli = {
    help: false,
    dryRun: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      cli.help = true;
    } else if ((arg === '--k' || arg === '-k') && i + 1 < argv.length) {
      cli.k = Number(argv[++i]);
    } else if (arg === '--config' && i + 1 < argv.length) {
      cli.config = argv[++i];
    } else if (arg === '--root' && i + 1 < argv.length) {
      cli.root = argv[++i];
    } else if (arg === '--phase' && i + 1 < argv.length) {
      cli.phase = argv[++i];
    } else if (arg === '--semantic-llm') {
      cli.semanticLlm = true;
    } else if (arg === '--with-similarity') {
      cli.withSimilarity = true;
    } else if (arg === '--dry-run') {
      cli.dryRun = true;
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  return cli;
}

function loadConfig(configPath = DEFAULT_CONFIG) {
  const resolved = path.resolve(configPath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`Config file not found: ${resolved}`);
  }

  delete require.cache[require.resolve(resolved)];
  const loaded = require(resolved);
  if (!loaded || typeof loaded !== 'object') {
    throw new Error(`Config file must export an object: ${resolved}`);
  }
  return { config: loaded, configPath: resolved };
}

function resolvePipelineOptions(cli, loadedConfig) {
  const config = mergeDefaults(loadedConfig || {});
  const k = cli.k !== undefined ? cli.k : config.k;
  const phaseInput = cli.phase || config.phase || 'all';
  const similarityEnabled = Boolean(cli.withSimilarity || config.similarity.enabled || phaseInput === 'download-group');
  const phase = normalizePhase(phaseInput);
  const cliSemanticLlm = Boolean(cli.semanticLlm);
  const projectRoot = resolveFrom(process.cwd(), config.paths.projectRoot);
  const baseRoot = cli.root || config.paths.resultsRoot;
  const root = resolveFrom(projectRoot, formatOutputRoot(baseRoot, k));
  const clawhubDownloader = resolveFrom(
    projectRoot,
    config.paths.clawhubDownloader || config.paths.similarityAnalyzer
  );

  const resolved = {
    k,
    phase,
    dryRun: Boolean(cli.dryRun),
    configPath: cli.config ? path.resolve(cli.config) : DEFAULT_CONFIG,
    paths: {
      projectRoot,
      root,
      resultsRoot: resolveFrom(projectRoot, config.paths.resultsRoot),
      clawhubDownloader,
      similarityAnalyzer: clawhubDownloader,
      fcgAnalyzer: resolveFrom(projectRoot, config.paths.fcgAnalyzer),
      doeAnalyzer: resolveFrom(projectRoot, config.paths.doeAnalyzer)
    },
    clawhub: {
      sort: config.clawhub.sort,
      apiBase: config.clawhub.apiBase,
      timeoutMs: Number(config.clawhub.timeoutMs),
      retries: Number(config.clawhub.retries),
      downloadConcurrency: Number(config.clawhub.downloadConcurrency),
      nonSuspiciousOnly: Boolean(config.clawhub.nonSuspiciousOnly)
    },
    similarity: {
      enabled: similarityEnabled,
      threshold: Number(config.similarity.threshold),
      topK: Number(config.similarity.topK),
      llmConcurrency: Number(config.similarity.llmConcurrency),
      semanticLlm: similarityEnabled && Boolean(cliSemanticLlm || config.similarity.semanticLlm)
    },
    fcg: {
      mode: config.fcg.mode,
      concurrency: Number(config.fcg.concurrency),
      refresh: Boolean(config.fcg.refresh),
      scope: config.fcg.scope || 'all',
      // FCG Markdown semantic gate uses the real chat model (gpt-5.5), whose judge
      // latency is 50-100s. This MUST NOT reuse clawhub.timeoutMs (download timeout).
      // Fall back to env LLM_TIMEOUT, then a safe 180000ms default.
      llmTimeout: Number(config.fcg.llmTimeout || process.env.LLM_TIMEOUT || 180000),
      labelLlmAssist: Boolean(config.fcg.labelLlmAssist),
      labelLlmConcurrency: Number(config.fcg.labelLlmConcurrency || 2),
      labelLlmCache: config.fcg.labelLlmCache || '',
      semanticGateCache: config.fcg.semanticGateCache || '',
      pythonExecutable: config.fcg.pythonExecutable || process.env.PYTHON || 'python'
    },
    doe: {
      enabled: config.doe.enabled !== false,
      concurrency: Number(config.doe.concurrency || 2),
      threshold: config.doe.threshold,
      llmJudge: config.doe.llmJudge !== false,
      llmBatchSize: config.doe.llmBatchSize,
      llmVotes: config.doe.llmVotes,
      llmConcurrency: config.doe.llmConcurrency,
      llmEscalationVotes: config.doe.llmEscalationVotes,
      llmEscalationPolicy: config.doe.llmEscalationPolicy,
      llmMaxBatchChars: config.doe.llmMaxBatchChars,
      evidenceMaxPackChars: config.doe.evidenceMaxPackChars,
      evidencePathNodeWindow: config.doe.evidencePathNodeWindow,
      evidenceMaxTextChars: config.doe.evidenceMaxTextChars,
      evidenceMaxArrayItems: config.doe.evidenceMaxArrayItems,
      adaptiveTimeoutMaxMs: config.doe.adaptiveTimeoutMaxMs,
      llmCache: config.doe.llmCache || '',
      refresh: Boolean(config.doe.refresh)
    }
  };

  validateOptions(resolved);
  return resolved;
}

function mergeDefaults(config) {
  const projectRoot = path.resolve(__dirname, '..');
  return {
    k: config.k,
    phase: config.phase,
    paths: {
      projectRoot,
      resultsRoot: './results/clawhub-top',
      clawhubDownloader: './packages/skill-similarity-analyzer',
      similarityAnalyzer: './packages/skill-similarity-analyzer',
      doeAnalyzer: './packages/skill-doe-analyzer',
      fcgAnalyzer: './packages/skill-sfg',
      ...(config.paths || {})
    },
    clawhub: {
      sort: 'downloads',
      apiBase: 'https://clawhub.ai/api/v1',
      timeoutMs: 30000,
      retries: 4,
      downloadConcurrency: 8,
      nonSuspiciousOnly: false,
      ...(config.clawhub || {})
    },
    similarity: {
      enabled: false,
      threshold: 0.68,
      topK: 5,
      llmConcurrency: 2,
      semanticLlm: false,
      ...(config.similarity || {})
    },
    fcg: {
      mode: 'full',
      concurrency: 4,
      refresh: false,
      scope: 'all',
      llmTimeout: '',
      labelLlmAssist: false,
      labelLlmConcurrency: 2,
      labelLlmCache: '',
      semanticGateCache: '',
      ...(config.fcg || {})
    },
    doe: {
      enabled: true,
      concurrency: 2,
      threshold: 0.7,
      llmJudge: true,
      llmBatchSize: 4,
      llmVotes: 1,
      llmConcurrency: 2,
      llmEscalationVotes: 3,
      llmEscalationPolicy: 'risk_or_uncertain',
      llmMaxBatchChars: 60000,
      evidenceMaxPackChars: 100000,
      evidencePathNodeWindow: 4,
      evidenceMaxTextChars: 2000,
      evidenceMaxArrayItems: 40,
      adaptiveTimeoutMaxMs: 0,
      llmCache: '',
      refresh: false,
      ...(config.doe || {})
    }
  };
}

function normalizePhase(phase) {
  return phase === 'download-group' ? 'download' : phase;
}

function resolveFrom(baseDir, value) {
  if (!value) return path.resolve(baseDir);
  return path.isAbsolute(value) ? path.resolve(value) : path.resolve(baseDir, value);
}

function formatOutputRoot(baseRoot, k) {
  const text = String(baseRoot || '').trim();
  if (!text) return text;
  if (/-k\d+$/i.test(text)) return text;
  return `${text}-k${k}`;
}

function validateOptions(options) {
  if (!Number.isInteger(options.k) || options.k <= 0) {
    throw new Error('--k must be a positive integer');
  }
  if (!['download', 'fcg', 'doe', 'all'].includes(options.phase)) {
    throw new Error('--phase must be download, fcg, doe, all, or download-group');
  }
  if (!['downloads', 'stars', 'installs'].includes(options.clawhub.sort)) {
    throw new Error('clawhub.sort must be downloads, stars, or installs');
  }
  if (!Number.isInteger(options.clawhub.downloadConcurrency) || options.clawhub.downloadConcurrency <= 0) {
    throw new Error('clawhub.downloadConcurrency must be a positive integer');
  }
  if (!Number.isInteger(options.similarity.topK) || options.similarity.topK <= 0) {
    throw new Error('similarity.topK must be a positive integer');
  }
  if (!Number.isFinite(options.similarity.threshold) || options.similarity.threshold < 0 || options.similarity.threshold > 1) {
    throw new Error('similarity.threshold must be a number in [0, 1]');
  }
  if (!['quick', 'full', 'deep'].includes(options.fcg.mode)) {
    throw new Error('fcg.mode must be quick, full, or deep');
  }
  if (!['all', 'grouped', 'ungrouped'].includes(options.fcg.scope)) {
    throw new Error('fcg.scope must be all, grouped, or ungrouped');
  }
  if (!Number.isInteger(options.doe.concurrency) || options.doe.concurrency <= 0) {
    throw new Error('doe.concurrency must be a positive integer');
  }
  if (options.doe.threshold !== undefined && (!Number.isFinite(Number(options.doe.threshold)) || Number(options.doe.threshold) < 0 || Number(options.doe.threshold) > 1)) {
    throw new Error('doe.threshold must be a number in [0, 1]');
  }
  if (options.doe.llmConcurrency !== undefined && (!Number.isInteger(Number(options.doe.llmConcurrency)) || Number(options.doe.llmConcurrency) <= 0)) {
    throw new Error('doe.llmConcurrency must be a positive integer');
  }
  if (options.doe.llmEscalationVotes !== undefined && (!Number.isInteger(Number(options.doe.llmEscalationVotes)) || Number(options.doe.llmEscalationVotes) <= 0)) {
    throw new Error('doe.llmEscalationVotes must be a positive integer');
  }
  if (options.doe.llmEscalationPolicy !== undefined && !['risk_or_uncertain', 'none', 'all'].includes(String(options.doe.llmEscalationPolicy))) {
    throw new Error('doe.llmEscalationPolicy must be risk_or_uncertain, none, or all');
  }
  if (options.doe.llmMaxBatchChars !== undefined && (!Number.isInteger(Number(options.doe.llmMaxBatchChars)) || Number(options.doe.llmMaxBatchChars) <= 0)) {
    throw new Error('doe.llmMaxBatchChars must be a positive integer');
  }
}

function preflight(options) {
  const major = Number(process.versions.node.split('.')[0]);
  if (!Number.isInteger(major) || major < 18) {
    throw new Error(`Node.js >=18 is required. Current: ${process.version}`);
  }

  const requiredDirs = [];
  if (options.phase === 'download' || options.phase === 'all') {
    requiredDirs.push(options.paths.clawhubDownloader);
  }
  if (options.phase === 'fcg' || options.phase === 'all') {
    requiredDirs.push(options.paths.fcgAnalyzer);
  }
  if (options.phase === 'doe' || (options.phase === 'all' && options.doe.enabled)) {
    requiredDirs.push(options.paths.doeAnalyzer);
  }
  for (const dir of requiredDirs) {
    if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
      throw new Error(`Required module directory not found: ${dir}`);
    }
  }

  const requiredFiles = [];
  if (options.phase === 'download' || options.phase === 'all') {
    requiredFiles.push(path.join(options.paths.clawhubDownloader, 'scripts', 'clawhub-top-skills.js'));
  }
  if (options.phase === 'fcg' || options.phase === 'all') {
    requiredFiles.push(path.join(options.paths.fcgAnalyzer, 'skill_sfg', 'batch.py'));
  }
  if (options.phase === 'doe' || (options.phase === 'all' && options.doe.enabled)) {
    requiredFiles.push(path.join(options.paths.doeAnalyzer, 'scripts', 'doe-batch.js'));
  }
  for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
      throw new Error(`Required entry not found: ${file}`);
    }
  }

  if (!options.dryRun) {
    if (options.similarity.semanticLlm && !String(process.env.LLM_API_KEY || '').trim()) {
      throw new Error('LLM_API_KEY is required when semantic LLM is enabled');
    }
    if (options.fcg.labelLlmAssist && !String(process.env.LLM_API_KEY || '').trim()) {
      throw new Error('LLM_API_KEY is required when FCG label LLM assist is enabled');
    }
    if ((options.phase === 'fcg' || options.phase === 'all') && !String(process.env.LLM_API_KEY || '').trim()) {
      throw new Error('LLM_API_KEY is required for FCG Markdown semantic gate');
    }
    if ((options.phase === 'doe' || (options.phase === 'all' && options.doe.enabled)) &&
        options.doe.llmJudge &&
        !String(process.env.LLM_API_KEY || '').trim()) {
      throw new Error('LLM_API_KEY is required when DOE LLM judge is enabled');
    }
  }
}

function buildCommands(options) {
  const commands = [];
  if (options.phase === 'download' || options.phase === 'all') {
    commands.push(buildClawhubPrepareCommand(options));
  }
  if (options.phase === 'fcg' || options.phase === 'all') {
    commands.push(buildFcgCommand(options));
  }
  if (options.phase === 'doe' || (options.phase === 'all' && options.doe.enabled)) {
    commands.push(buildDoeCommand(options));
  }
  return commands;
}

function buildClawhubPrepareCommand(options) {
  const args = [
    path.join(options.paths.clawhubDownloader, 'scripts', 'clawhub-top-skills.js'),
    '--k', String(options.k),
    '--root', options.paths.root,
    '--sort', options.clawhub.sort,
    '--download-concurrency', String(options.clawhub.downloadConcurrency),
    '--llm-concurrency', String(options.similarity.llmConcurrency),
    '--top-k', String(options.similarity.topK),
    '--threshold', String(options.similarity.threshold),
    '--api-base', options.clawhub.apiBase,
    '--timeout-ms', String(options.clawhub.timeoutMs),
    '--retries', String(options.clawhub.retries),
    '--phase', options.similarity.enabled ? 'all' : 'list-download'
  ];
  if (options.clawhub.nonSuspiciousOnly) args.push('--non-suspicious-only');
  if (options.similarity.enabled && options.similarity.semanticLlm) args.push('--semantic-llm');
  return {
    name: options.similarity.enabled ? 'download-group' : 'download',
    command: process.execPath,
    args,
    cwd: options.paths.clawhubDownloader
  };
}

function buildSimilarityCommand(options) {
  return buildClawhubPrepareCommand({
    ...options,
    similarity: {
      ...options.similarity,
      enabled: true
    }
  });
}

function buildFcgCommand(options) {
  // FCG now runs on the Python engine (packages/skill-sfg). The package is not
  // pip-installed, so `python -m skill_sfg.batch` only resolves when cwd is the
  // package directory (cwd enters sys.path). Flags mirror the retired fcg-batch.js.
  const args = [
    '-m', 'skill_sfg.batch',
    '--root', options.paths.root,
    '--scope', options.fcg.scope,
    '--concurrency', String(options.fcg.concurrency),
    '--mode', options.fcg.mode,
    '--llm-timeout', String(options.fcg.llmTimeout)
  ];
  if (options.fcg.labelLlmAssist) {
    args.push('--label-llm-assist');
    args.push('--label-llm-concurrency', String(options.fcg.labelLlmConcurrency));
    if (options.fcg.labelLlmCache) args.push('--label-llm-cache', options.fcg.labelLlmCache);
  }
  if (options.fcg.semanticGateCache) args.push('--semantic-gate-cache', options.fcg.semanticGateCache);
  if (options.fcg.refresh) args.push('--refresh');
  return {
    name: 'fcg',
    command: options.fcg.pythonExecutable,
    args,
    cwd: options.paths.fcgAnalyzer
  };
}

function buildDoeCommand(options) {
  const args = [
    path.join(options.paths.doeAnalyzer, 'scripts', 'doe-batch.js'),
    '--root', options.paths.root,
    '--fcg-root', path.join(options.paths.root, 'fcg'),
    '--output', path.join(options.paths.root, 'doe'),
    '--concurrency', String(options.doe.concurrency)
  ];
  if (options.doe.threshold !== undefined) args.push('--threshold', String(options.doe.threshold));
  if (options.doe.llmCache) args.push('--llm-cache', options.doe.llmCache);
  if (options.doe.llmBatchSize !== undefined) args.push('--llm-batch-size', String(options.doe.llmBatchSize));
  if (options.doe.llmVotes !== undefined) args.push('--llm-votes', String(options.doe.llmVotes));
  if (options.doe.llmConcurrency !== undefined) args.push('--llm-concurrency', String(options.doe.llmConcurrency));
  if (options.doe.llmEscalationVotes !== undefined) args.push('--llm-escalation-votes', String(options.doe.llmEscalationVotes));
  if (options.doe.llmEscalationPolicy !== undefined) args.push('--llm-escalation-policy', String(options.doe.llmEscalationPolicy));
  if (options.doe.llmMaxBatchChars !== undefined) args.push('--llm-max-batch-chars', String(options.doe.llmMaxBatchChars));
  if (options.doe.evidenceMaxPackChars) args.push('--evidence-max-pack-chars', String(options.doe.evidenceMaxPackChars));
  if (options.doe.evidencePathNodeWindow !== undefined && options.doe.evidencePathNodeWindow !== '') {
    args.push('--evidence-path-node-window', String(options.doe.evidencePathNodeWindow));
  }
  if (options.doe.evidenceMaxTextChars) args.push('--evidence-max-text-chars', String(options.doe.evidenceMaxTextChars));
  if (options.doe.evidenceMaxArrayItems) args.push('--evidence-max-array-items', String(options.doe.evidenceMaxArrayItems));
  if (options.doe.adaptiveTimeoutMaxMs) args.push('--adaptive-timeout-max-ms', String(options.doe.adaptiveTimeoutMaxMs));
  if (!options.doe.llmJudge) args.push('--no-llm-judge');
  if (options.doe.refresh) args.push('--refresh');
  return {
    name: 'doe',
    command: process.execPath,
    args,
    cwd: options.paths.doeAnalyzer
  };
}

async function runPipeline(options, runner = runCommand) {
  preflight(options);
  const commands = buildCommands(options);
  printPlan(options, commands);
  if (options.dryRun) return { options, commands, dryRun: true };

  for (const command of commands) {
    console.log(`\n=== Running ${command.name} ===`);
    await runner(command);
  }

  console.log('\nPipeline completed.');
  console.log(`Output root: ${options.paths.root}`);
  return { options, commands, dryRun: false };
}

function runCommand(command) {
  return new Promise((resolve, reject) => {
    const child = spawn(command.command, command.args, {
      cwd: command.cwd,
      stdio: 'inherit',
      shell: false
    });
    child.on('error', reject);
    child.on('exit', code => {
      if (code === 0) resolve();
      else reject(new Error(`${command.name} failed with exit code ${code}`));
    });
  });
}

function printPlan(options, commands) {
  console.log('SkillFlow pipeline plan:');
  console.log(JSON.stringify({
    k: options.k,
    phase: options.phase,
    root: options.paths.root,
    similarityEnabled: options.similarity.enabled,
    similaritySemanticLlm: options.similarity.semanticLlm,
    fcgScope: options.fcg.scope,
    doeEnabled: options.doe.enabled,
    doeLlmJudge: options.doe.llmJudge,
    dryRun: options.dryRun
  }, null, 2));
  console.log('');
  console.log('Commands:');
  for (const command of commands) {
    console.log(`- (${command.cwd}) ${quoteCommand(command.command, command.args)}`);
  }
}

function quoteCommand(command, args) {
  return [command, ...args].map(quoteArg).join(' ');
}

function quoteArg(value) {
  const text = String(value);
  if (/^[A-Za-z0-9_./:=@-]+$/.test(text)) return text;
  return `"${text.replace(/"/g, '\\"')}"`;
}

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/skillflow-pipeline.js --k <n> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --k, -k <n>                 Number of top ClawHub skills to process');
  console.log('  --config <file>             Default skillflow-pipeline.config.cjs');
  console.log('  --root <dir>                Output root prefix or explicit -k root');
  console.log('  --phase download|fcg|doe|all|download-group  Default all');
  console.log('  --with-similarity           Also run similarity grouping during download phase');
  console.log('  --semantic-llm              Enable semantic LLM for similarity grouping only');
  console.log('  --dry-run                   Print resolved config and commands only');
}

async function main(argv = process.argv.slice(2)) {
  try {
    const cli = parseArgs(argv);
    if (cli.help) {
      printUsage();
      return;
    }
    const { config } = loadConfig(cli.config || DEFAULT_CONFIG);
    const options = resolvePipelineOptions(cli, config);
    await runPipeline(options);
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    printUsage();
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  DEFAULT_CONFIG,
  parseArgs,
  loadConfig,
  resolvePipelineOptions,
  mergeDefaults,
  formatOutputRoot,
  validateOptions,
  preflight,
  normalizePhase,
  buildCommands,
  buildClawhubPrepareCommand,
  buildSimilarityCommand,
  buildFcgCommand,
  buildDoeCommand,
  runPipeline,
  quoteCommand
};
