const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  parseArgs,
  resolvePipelineOptions,
  formatOutputRoot,
  preflight,
  buildCommands,
  runPipeline
} = require('../scripts/skillflow-pipeline');

test('parseArgs requires k through resolved validation and accepts aliases', () => {
  assert.equal(parseArgs(['--k', '100']).k, 100);
  assert.equal(parseArgs(['-k', '50']).k, 50);
  assert.throws(() => resolvePipelineOptions(parseArgs([]), fixtureConfig()), /--k/);
  assert.throws(() => resolvePipelineOptions(parseArgs(['--k', '0']), fixtureConfig()), /--k/);
});

test('default output root appends k suffix', () => {
  assert.equal(formatOutputRoot('D:\\data\\clawhub-top', 123), 'D:\\data\\clawhub-top-k123');
  assert.equal(formatOutputRoot('D:\\data\\clawhub-top-k123', 123), 'D:\\data\\clawhub-top-k123');

  const options = resolvePipelineOptions(parseArgs(['--k', '25']), fixtureConfig({
    paths: { resultsRoot: './results/clawhub-top' }
  }));
  assert.ok(options.paths.root.endsWith(path.join('results', 'clawhub-top-k25')));
});

test('CLI root and semantic flag override config', () => {
  const options = resolvePipelineOptions(parseArgs([
    '--k', '10',
    '--root', 'D:\\override\\run',
    '--phase', 'fcg',
    '--semantic-llm'
  ]), fixtureConfig({
    paths: { resultsRoot: '.\\results\\config-run' }
  }));

  assert.ok(options.paths.root.endsWith('run-k10'));
  assert.equal(options.phase, 'fcg');
  assert.equal(options.similarity.semanticLlm, false);
  assert.equal(Object.prototype.hasOwnProperty.call(options.fcg, 'semanticLlm'), false);
});

test('buildCommands defaults to download, FCG, and DOE without grouping', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7']), fixtureConfig());
  const commands = buildCommands(options);
  assert.equal(commands.length, 3);

  const download = commands[0];
  assert.equal(download.name, 'download');
  assert.equal(options.similarity.enabled, false);
  assert.ok(download.args.includes('--k'));
  assert.ok(download.args.includes('7'));
  assert.ok(download.args.includes('--root'));
  assert.ok(download.args.includes(options.paths.root));
  assert.ok(download.args.includes('--sort'));
  assert.ok(download.args.includes('downloads'));
  assert.equal(argAfter(download.args, '--phase'), 'list-download');

  const fcg = commands[1];
  assert.equal(fcg.name, 'fcg');
  assert.ok(fcg.args.includes('--root'));
  assert.ok(fcg.args.includes(options.paths.root));
  assert.ok(fcg.args.includes('--scope'));
  assert.ok(fcg.args.includes('all'));
  assert.equal(fcg.args.includes('--semantic-llm'), false);
  assert.equal(fcg.args.includes('--doc' + '-flow'), false);

  const doe = commands[2];
  assert.equal(doe.name, 'doe');
  assert.ok(doe.args.includes('--root'));
  assert.ok(doe.args.includes(options.paths.root));
  assert.ok(doe.args.includes('--fcg-root'));
  assert.ok(doe.args.includes(path.join(options.paths.root, 'fcg')));
});

test('with similarity enables grouping during download phase', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7', '--with-similarity']), fixtureConfig());
  const commands = buildCommands(options);
  assert.equal(commands.length, 3);
  assert.equal(options.similarity.enabled, true);
  assert.equal(commands[0].name, 'download-group');
  assert.equal(argAfter(commands[0].args, '--phase'), 'all');
  assert.equal(commands[2].name, 'doe');
});

test('download-group phase remains a compatibility alias for grouped download', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7', '--phase', 'download-group']), fixtureConfig());
  const commands = buildCommands(options);
  assert.equal(options.phase, 'download');
  assert.equal(options.similarity.enabled, true);
  assert.equal(commands.length, 1);
  assert.equal(commands[0].name, 'download-group');
  assert.equal(argAfter(commands[0].args, '--phase'), 'all');
});

test('fcg phase only constructs FCG command', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7', '--phase', 'fcg']), fixtureConfig());
  const commands = buildCommands(options);
  assert.equal(commands.length, 1);
  assert.equal(commands[0].name, 'fcg');
});

test('doe phase only constructs DOE command', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7', '--phase', 'doe']), fixtureConfig());
  const commands = buildCommands(options);
  assert.equal(commands.length, 1);
  assert.equal(commands[0].name, 'doe');
});

test('FCG label LLM assist is configurable and passed to batch command', () => {
  const options = resolvePipelineOptions(parseArgs(['--k', '7', '--phase', 'fcg']), fixtureConfig({
    similarity: { semanticLlm: false },
    fcg: {
      labelLlmAssist: true,
      labelLlmConcurrency: 3,
      labelLlmCache: 'cache.jsonl'
    }
  }));
  const commands = buildCommands(options);
  const fcg = commands[0];

  assert.equal(options.fcg.labelLlmAssist, true);
  assert.ok(fcg.args.includes('--label-llm-assist'));
  assert.ok(fcg.args.includes('--label-llm-concurrency'));
  assert.ok(fcg.args.includes('3'));
  assert.ok(fcg.args.includes('--label-llm-cache'));
  assert.ok(fcg.args.includes('cache.jsonl'));
});

test('dry-run does not execute child commands', async () => {
  const tmp = makeModuleTree();
  const options = resolvePipelineOptions(parseArgs(['--k', '3', '--dry-run']), fixtureConfig({
    paths: tmp.paths,
    similarity: { semanticLlm: false }
  }));

  let called = false;
  const result = await runPipeline(options, async () => {
    called = true;
  });

  assert.equal(result.dryRun, true);
  assert.equal(called, false);
  assert.equal(result.commands.length, 3);
});

test('relative config paths resolve from projectRoot instead of current cwd', () => {
  const tmp = makeModuleTree();
  const originalCwd = process.cwd();
  const other = fs.mkdtempSync(path.join(os.tmpdir(), 'skillflow-cwd-'));
  try {
    process.chdir(other);
    const options = resolvePipelineOptions(parseArgs(['--k', '9']), fixtureConfig({
      paths: {
        projectRoot: tmp.tmp,
        resultsRoot: './results/clawhub-top',
        similarityAnalyzer: './packages/skill-similarity-analyzer',
        fcgAnalyzer: './packages/skill-fcg-analyzer'
      }
    }));

    assert.equal(options.paths.projectRoot, tmp.tmp);
    assert.equal(options.paths.clawhubDownloader, path.join(tmp.tmp, 'packages', 'skill-similarity-analyzer'));
    assert.equal(options.paths.similarityAnalyzer, options.paths.clawhubDownloader);
    assert.equal(options.paths.fcgAnalyzer, path.join(tmp.tmp, 'packages', 'skill-fcg-analyzer'));
    assert.equal(options.paths.doeAnalyzer, path.join(tmp.tmp, 'packages', 'skill-doe-analyzer'));
    assert.equal(options.paths.root, path.join(tmp.tmp, 'results', 'clawhub-top-k9'));
  } finally {
    process.chdir(originalCwd);
  }
});

test('clawhubDownloader path takes priority over legacy similarityAnalyzer', () => {
  const tmp = makeModuleTree({ includeSimilarity: false, includeDownloader: true });
  const options = resolvePipelineOptions(parseArgs(['--k', '5']), fixtureConfig({
    paths: {
      projectRoot: tmp.tmp,
      clawhubDownloader: './packages/clawhub-downloader',
      similarityAnalyzer: './packages/missing-similarity',
      fcgAnalyzer: './packages/skill-fcg-analyzer'
    },
    doe: { llmJudge: false }
  }));
  const commands = buildCommands(options);

  assert.equal(options.paths.clawhubDownloader, path.join(tmp.tmp, 'packages', 'clawhub-downloader'));
  assert.equal(options.paths.similarityAnalyzer, options.paths.clawhubDownloader);
  assert.equal(commands[0].cwd, options.paths.clawhubDownloader);
  assert.doesNotThrow(() => preflight(options));
});

test('legacy similarityAnalyzer path remains a fallback for download entry', () => {
  const tmp = makeModuleTree();
  const options = resolvePipelineOptions(parseArgs(['--k', '5']), fixtureConfig({
    paths: {
      projectRoot: tmp.tmp,
      clawhubDownloader: '',
      similarityAnalyzer: './packages/skill-similarity-analyzer',
      fcgAnalyzer: './packages/skill-fcg-analyzer'
    },
    doe: { llmJudge: false }
  }));
  const commands = buildCommands(options);

  assert.equal(options.paths.clawhubDownloader, path.join(tmp.tmp, 'packages', 'skill-similarity-analyzer'));
  assert.equal(commands[0].cwd, options.paths.clawhubDownloader);
  assert.doesNotThrow(() => preflight(options));
});

test('preflight ignores similarity semantic LLM when similarity is disabled', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  delete process.env.LLM_API_KEY;
  try {
    const options = resolvePipelineOptions(parseArgs(['--k', '3', '--phase', 'download']), fixtureConfig({
      paths: tmp.paths,
      similarity: { semanticLlm: true, enabled: false },
      fcg: {}
    }));
    assert.equal(options.similarity.semanticLlm, false);
    assert.doesNotThrow(() => preflight(options));
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight requires LLM_API_KEY when active similarity semantic LLM is enabled', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  delete process.env.LLM_API_KEY;
  try {
    const options = resolvePipelineOptions(parseArgs(['--k', '3', '--with-similarity', '--semantic-llm']), fixtureConfig({
      paths: tmp.paths,
      similarity: { enabled: false },
      doe: { llmJudge: false }
    }));
    assert.throws(() => preflight(options), /LLM_API_KEY/);
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight requires LLM_API_KEY when DOE LLM judge is enabled', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  delete process.env.LLM_API_KEY;
  try {
    const options = resolvePipelineOptions(parseArgs(['--k', '3', '--phase', 'doe']), fixtureConfig({
      paths: tmp.paths
    }));
    assert.throws(() => preflight(options), /DOE LLM judge/);
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight requires LLM_API_KEY when label LLM assist is enabled', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  delete process.env.LLM_API_KEY;
  try {
    const options = resolvePipelineOptions(parseArgs(['--k', '3']), fixtureConfig({
      paths: tmp.paths,
      similarity: { semanticLlm: false },
      fcg: { labelLlmAssist: true },
      doe: { llmJudge: false }
    }));
    assert.throws(() => preflight(options), /LLM_API_KEY/);
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight requires LLM_API_KEY for FCG Markdown semantic gate', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  delete process.env.LLM_API_KEY;
  try {
    const options = resolvePipelineOptions(parseArgs(['--k', '3', '--phase', 'fcg']), fixtureConfig({
      paths: tmp.paths,
      similarity: { semanticLlm: false },
      doe: { llmJudge: false }
    }));
    assert.throws(() => preflight(options), /FCG Markdown semantic gate/);
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight for fcg phase does not require similarity analyzer entry', () => {
  const tmp = makeModuleTree({ includeSimilarity: false });
  const previous = process.env.LLM_API_KEY;
  process.env.LLM_API_KEY = 'test-key';
  const options = resolvePipelineOptions(parseArgs(['--k', '3', '--phase', 'fcg']), fixtureConfig({
    paths: tmp.paths,
    similarity: { semanticLlm: false }
  }));

  try {
    assert.doesNotThrow(() => preflight(options));
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

test('preflight for default pipeline requires download, FCG, and DOE entries', () => {
  const tmp = makeModuleTree();
  const previous = process.env.LLM_API_KEY;
  process.env.LLM_API_KEY = 'test-key';
  const options = resolvePipelineOptions(parseArgs(['--k', '3']), fixtureConfig({
    paths: tmp.paths,
    similarity: { semanticLlm: false },
    doe: { llmJudge: false }
  }));

  try {
    assert.doesNotThrow(() => preflight(options));
  } finally {
    if (previous === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = previous;
  }
});

function fixtureConfig(overrides = {}) {
  const root = 'D:\\projects\\SkillFlow';
  return {
    paths: {
      projectRoot: root,
      resultsRoot: './results/clawhub-top',
      clawhubDownloader: './packages/skill-similarity-analyzer',
      similarityAnalyzer: './packages/skill-similarity-analyzer',
      fcgAnalyzer: './packages/skill-fcg-analyzer',
      doeAnalyzer: './packages/skill-doe-analyzer',
      ...(overrides.paths || {})
    },
    clawhub: {
      sort: 'downloads',
      apiBase: 'https://clawhub.ai/api/v1',
      timeoutMs: 30000,
      retries: 4,
      downloadConcurrency: 8,
      nonSuspiciousOnly: false,
      ...(overrides.clawhub || {})
    },
    similarity: {
      enabled: false,
      threshold: 0.68,
      topK: 5,
      llmConcurrency: 2,
      semanticLlm: false,
      ...(overrides.similarity || {})
    },
    fcg: {
      mode: 'full',
      concurrency: 4,
      refresh: false,
      scope: 'all',
      labelLlmAssist: false,
      labelLlmConcurrency: 2,
      labelLlmCache: '',
      ...(overrides.fcg || {})
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
      llmCache: '',
      refresh: false,
      ...(overrides.doe || {})
    }
  };
}

function argAfter(args, name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
}

function makeModuleTree({ includeSimilarity = true, includeDownloader = false } = {}) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'skillflow-pipeline-'));
  const packages = path.join(tmp, 'packages');
  const similarityAnalyzer = path.join(packages, 'skill-similarity-analyzer');
  const clawhubDownloader = path.join(packages, 'clawhub-downloader');
  const fcgAnalyzer = path.join(packages, 'skill-fcg-analyzer');
  const doeAnalyzer = path.join(packages, 'skill-doe-analyzer');
  if (includeSimilarity) {
    fs.mkdirSync(path.join(similarityAnalyzer, 'scripts'), { recursive: true });
    fs.writeFileSync(path.join(similarityAnalyzer, 'scripts', 'clawhub-top-skills.js'), '');
  }
  if (includeDownloader) {
    fs.mkdirSync(path.join(clawhubDownloader, 'scripts'), { recursive: true });
    fs.writeFileSync(path.join(clawhubDownloader, 'scripts', 'clawhub-top-skills.js'), '');
  }
  fs.mkdirSync(path.join(fcgAnalyzer, 'scripts'), { recursive: true });
  fs.writeFileSync(path.join(fcgAnalyzer, 'scripts', 'fcg-batch.js'), '');
  fs.mkdirSync(path.join(doeAnalyzer, 'scripts'), { recursive: true });
  fs.writeFileSync(path.join(doeAnalyzer, 'scripts', 'doe-batch.js'), '');

  return {
    tmp,
    paths: {
      projectRoot: tmp,
      resultsRoot: './results/clawhub-top',
      clawhubDownloader: similarityAnalyzer,
      similarityAnalyzer,
      fcgAnalyzer,
      doeAnalyzer
    }
  };
}


