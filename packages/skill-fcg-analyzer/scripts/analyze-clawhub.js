#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');
const { SkillFCGAnalyzer } = require('../src/index');
const { saveToJson } = require('../src/output/json-generator');
const { saveFlowchartArtifacts, deriveFlowchartPaths } = require('../src/output/flowchart-generator');

const WINDOW_INVALID_CHARS = /[<>:"/\\|?*\u0000-\u001F]/g;
const WINDOW_RESERVED_NAMES = new Set([
  'CON', 'PRN', 'AUX', 'NUL',
  'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
  'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
]);

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/analyze-clawhub.js --url <skill_url> [--url <skill_url> ...] [--results <dir>] [--llm-timeout <ms>] [--skip-existing]');
  console.log('  node scripts/analyze-clawhub.js <skill_url_1> <skill_url_2> ... [--results <dir>] [--llm-timeout <ms>] [--skip-existing]');
  console.log('  node scripts/analyze-clawhub.js --list <urls.txt> [--results <dir>] [--llm-timeout <ms>] [--skip-existing]');
  console.log('');
  console.log('Output layout:');
  console.log('  results/<skill_name>/SKILL.md');
  console.log('  results/<skill_name>/<skill_name>_full.json');
  console.log('  results/<skill_name>/<skill_name>_full.flow.md');
  console.log('  results/<skill_name>/<skill_name>_full.flow.mmd');
}

function parseArgs(argv) {
  const options = {
    urls: [],
    listFile: '',
    help: false,
    resultsRoot: path.resolve(__dirname, '..', 'results'),
    llmTimeout: Number(process.env.LLM_TIMEOUT || 180000),
    skipExisting: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--url' && i + 1 < argv.length) {
      options.urls.push(argv[i + 1]);
      i++;
    } else if (arg === '--list' && i + 1 < argv.length) {
      options.listFile = argv[i + 1];
      i++;
    } else if (arg === '--results' && i + 1 < argv.length) {
      options.resultsRoot = path.resolve(argv[i + 1]);
      i++;
    } else if (arg === '--llm-timeout' && i + 1 < argv.length) {
      options.llmTimeout = Number(argv[i + 1]);
      i++;
    } else if (arg === '--skip-existing') {
      options.skipExisting = true;
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      options.urls.push(arg);
    }
  }

  if (!Number.isFinite(options.llmTimeout) || options.llmTimeout <= 0) {
    throw new Error('Invalid --llm-timeout value');
  }

  return options;
}

function loadUrls(options) {
  const collected = [];

  if (options.listFile) {
    const filePath = path.resolve(options.listFile);
    if (!fs.existsSync(filePath)) {
      throw new Error(`URL list file not found: ${filePath}`);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const listUrls = content
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'));

    collected.push(...listUrls);
  }

  collected.push(...options.urls);

  const dedup = [];
  const seen = new Set();
  for (const url of collected) {
    if (seen.has(url)) {
      continue;
    }
    seen.add(url);
    dedup.push(url);
  }

  return dedup;
}

function parseSkillNameFromUrl(url) {
  try {
    const parsed = new URL(url);
    const parts = parsed.pathname
      .split('/')
      .filter(Boolean)
      .map(segment => decodeURIComponent(segment));

    if (parts.length === 0) {
      return '';
    }

    const last = parts[parts.length - 1];
    if (last.toLowerCase() === 'download' && parts.length > 1) {
      return parts[parts.length - 2];
    }

    return last;
  } catch {
    return '';
  }
}

function sanitizeSkillName(name) {
  const raw = String(name || '').trim();
  let safeName = raw
    .replace(WINDOW_INVALID_CHARS, '_')
    .replace(/\s+/g, '_')
    .replace(/[. ]+$/g, '')
    .slice(0, 120);

  if (!safeName) {
    safeName = `skill_${Date.now()}`;
  }

  if (WINDOW_RESERVED_NAMES.has(safeName.toUpperCase())) {
    safeName = `${safeName}_skill`;
  }

  return safeName;
}

function buildSkillOutputPaths(resultsRoot, skillName) {
  const skillDir = path.join(resultsRoot, skillName);
  const prefix = path.join(skillDir, skillName);

  return {
    skillDir,
    skillMarkdown: path.join(skillDir, 'SKILL.md'),
    fullJson: `${prefix}_full.json`
  };
}

function createAnalyzer(options) {
  return new SkillFCGAnalyzer({
    llmProvider: process.env.LLM_PROVIDER || 'openai',
    llmModel: process.env.LLM_MODEL || 'gpt-5.5',
    llmApiKey: process.env.LLM_API_KEY || '',
    llmEndpoint: process.env.LLM_ENDPOINT || '',
    llmTimeout: options.llmTimeout,
    mode: 'full'
  });
}

async function runSingleAnalysis(zipPath, outputJsonPath, options) {
  const analyzer = createAnalyzer(options);
  const result = await analyzer.analyze(zipPath);

  saveToJson(result, outputJsonPath);
  const flowPaths = deriveFlowchartPaths(outputJsonPath);
  saveFlowchartArtifacts(result, flowPaths.markdownPath, flowPaths.mermaidPath);
}

function extractSkillMarkdownFromZip(zipPath, targetPath) {
  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries().filter(entry => !entry.isDirectory);
  const skillCandidates = entries
    .filter(entry => path.posix.basename(entry.entryName).toLowerCase() === 'skill.md')
    .sort((a, b) => {
      const depthA = a.entryName.split('/').length;
      const depthB = b.entryName.split('/').length;
      if (depthA !== depthB) return depthA - depthB;
      return a.entryName.length - b.entryName.length;
    });

  if (skillCandidates.length === 0) {
    return false;
  }

  const bestEntry = skillCandidates[0];
  const content = bestEntry.getData().toString('utf-8');
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  fs.writeFileSync(targetPath, content, 'utf-8');
  return true;
}

async function analyzeSkillUrl(url, options) {
  const rawSkillName = parseSkillNameFromUrl(url);
  const skillName = sanitizeSkillName(rawSkillName);
  const outputPaths = buildSkillOutputPaths(options.resultsRoot, skillName);

  fs.mkdirSync(outputPaths.skillDir, { recursive: true });
  console.log(`\n=== ${skillName} ===`);
  console.log(`URL: ${url}`);
  console.log(`Result folder prepared: ${outputPaths.skillDir}`);

  const downloader = createAnalyzer(options);
  try {
    const zipPath = await downloader.downloadZip(url, skillName);
    console.log(`Downloaded zip: ${zipPath}`);
    const hasSkillMarkdown = extractSkillMarkdownFromZip(zipPath, outputPaths.skillMarkdown);
    if (hasSkillMarkdown) {
      console.log(`Saved SKILL.md to: ${outputPaths.skillMarkdown}`);
    } else {
      console.warn(`SKILL.md not found in zip: ${url}`);
    }

    console.log('Running full analysis...');
    await runSingleAnalysis(zipPath, outputPaths.fullJson, options);
  } finally {
    downloader.cleanup();
  }

  return {
    skillName,
    outputPaths
  };
}

function isHttpUrl(value) {
  return /^https?:\/\//i.test(String(value || ''));
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

  let urls;
  try {
    urls = loadUrls(options);
  } catch (error) {
    console.error(`Input error: ${error.message}`);
    process.exit(1);
  }

  if (urls.length === 0) {
    console.error('No skill URL provided.');
    printUsage();
    process.exit(1);
  }

  fs.mkdirSync(options.resultsRoot, { recursive: true });
  console.log(`Results root: ${options.resultsRoot}`);
  console.log(`Total skills: ${urls.length}`);

  const summary = [];
  const seenSkillNames = new Set();
  for (const url of urls) {
    if (!isHttpUrl(url)) {
      const message = `Skipped non-URL input: ${url}`;
      console.warn(message);
      summary.push({ url, status: 'skipped', reason: 'non-url' });
      continue;
    }

    const rawSkillName = parseSkillNameFromUrl(url);
    const skillName = sanitizeSkillName(rawSkillName);
    if (seenSkillNames.has(skillName)) {
      const message = `Skipped duplicate skill name: ${skillName} (${url})`;
      console.warn(message);
      summary.push({ url, status: 'skipped', reason: `duplicate-skill-name:${skillName}` });
      continue;
    }
    seenSkillNames.add(skillName);

    if (options.skipExisting) {
      const existingPaths = buildSkillOutputPaths(options.resultsRoot, skillName);
      const isCompleted = (
        fs.existsSync(existingPaths.fullJson) &&
        fs.existsSync(existingPaths.fullDocFlowJson) &&
        fs.existsSync(existingPaths.skillMarkdown)
      );
      if (isCompleted) {
        const message = `Skipped existing completed skill: ${skillName} (${url})`;
        console.warn(message);
        summary.push({ url, status: 'skipped', reason: `existing:${skillName}` });
        continue;
      }
    }

    try {
      const output = await analyzeSkillUrl(url, options);
      summary.push({ url, status: 'ok', skillName: output.skillName });
    } catch (error) {
      console.error(`Failed to analyze ${url}: ${error.message}`);
      summary.push({ url, status: 'failed', reason: error.message });
    }
  }

  console.log('\n=== Summary ===');
  for (const item of summary) {
    if (item.status === 'ok') {
      console.log(`[OK] ${item.skillName} <- ${item.url}`);
    } else if (item.status === 'skipped') {
      console.log(`[SKIP] ${item.url} (${item.reason})`);
    } else {
      console.log(`[FAIL] ${item.url} (${item.reason})`);
    }
  }

  const hasFailures = summary.some(item => item.status === 'failed');
  if (hasFailures) {
    process.exitCode = 1;
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  loadUrls,
  parseSkillNameFromUrl,
  sanitizeSkillName,
  buildSkillOutputPaths,
  isHttpUrl
};
