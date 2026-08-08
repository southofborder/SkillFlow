#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const { analyzeDoeAsync } = require('./doe-analyzer');

async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.help || !args.command) {
    printHelp();
    return 0;
  }
  if (args.command !== 'analyze') {
    throw new Error(`Unknown command: ${args.command}`);
  }
  if (!args.fcg) {
    throw new Error('Missing required --fcg <file>');
  }

  const fcgPath = path.resolve(args.fcg);
  const fcgJson = readJson(fcgPath);
  const groupBaseline = args.groupBaseline ? readJson(path.resolve(args.groupBaseline)) : null;
  const result = await analyzeDoeAsync(fcgJson, {
    inputFcg: fcgPath,
    threshold: args.threshold,
    groupBaseline,
    llmJudge: args.llmJudge,
    llmCache: args.llmCache ? path.resolve(args.llmCache) : '',
    llmBatchSize: args.llmBatchSize,
    llmVotes: args.llmVotes,
    llmConcurrency: args.llmConcurrency,
    llmEscalationVotes: args.llmEscalationVotes,
    llmEscalationPolicy: args.llmEscalationPolicy,
    llmMaxBatchChars: args.llmMaxBatchChars,
    llmModel: args.llmModel,
    llmEndpoint: args.llmEndpoint,
    llmTimeout: args.llmTimeout
  });
  const output = JSON.stringify(result, null, args.pretty ? 2 : 0) + '\n';
  if (args.out) {
    const outPath = path.resolve(args.out);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, output, 'utf-8');
  } else {
    process.stdout.write(output);
  }
  return 0;
}

function parseArgs(argv = []) {
  const result = {
    command: '',
    fcg: '',
    out: '',
    groupBaseline: '',
    threshold: undefined,
    pretty: false,
    llmJudge: true,
    llmCache: '',
    llmBatchSize: undefined,
    llmVotes: undefined,
    llmConcurrency: undefined,
    llmEscalationVotes: undefined,
    llmEscalationPolicy: '',
    llmMaxBatchChars: undefined,
    llmModel: '',
    llmEndpoint: '',
    llmTimeout: undefined,
    help: false
  };
  const args = [...argv];
  result.command = args.shift() || '';
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') result.help = true;
    else if (arg === '--fcg') result.fcg = requireValue(args, ++i, '--fcg');
    else if (arg === '--out') result.out = requireValue(args, ++i, '--out');
    else if (arg === '--group-baseline') result.groupBaseline = requireValue(args, ++i, '--group-baseline');
    else if (arg === '--threshold') result.threshold = Number(requireValue(args, ++i, '--threshold'));
    else if (arg === '--pretty') result.pretty = true;
    else if (arg === '--no-llm-judge') result.llmJudge = false;
    else if (arg === '--llm-cache') result.llmCache = requireValue(args, ++i, '--llm-cache');
    else if (arg === '--llm-batch-size') result.llmBatchSize = Number(requireValue(args, ++i, '--llm-batch-size'));
    else if (arg === '--llm-votes') result.llmVotes = Number(requireValue(args, ++i, '--llm-votes'));
    else if (arg === '--llm-concurrency') result.llmConcurrency = Number(requireValue(args, ++i, '--llm-concurrency'));
    else if (arg === '--llm-escalation-votes') result.llmEscalationVotes = Number(requireValue(args, ++i, '--llm-escalation-votes'));
    else if (arg === '--llm-escalation-policy') result.llmEscalationPolicy = requireValue(args, ++i, '--llm-escalation-policy');
    else if (arg === '--llm-max-batch-chars') result.llmMaxBatchChars = Number(requireValue(args, ++i, '--llm-max-batch-chars'));
    else if (arg === '--llm-model') result.llmModel = requireValue(args, ++i, '--llm-model');
    else if (arg === '--llm-endpoint') result.llmEndpoint = requireValue(args, ++i, '--llm-endpoint');
    else if (arg === '--llm-timeout') result.llmTimeout = Number(requireValue(args, ++i, '--llm-timeout'));
    else throw new Error(`Unknown option: ${arg}`);
  }
  return result;
}

function requireValue(args, index, name) {
  const value = args[index];
  if (!value || value.startsWith('--')) throw new Error(`Missing value for ${name}`);
  return value;
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf-8'));
  } catch (error) {
    throw new Error(`Failed to read JSON ${file}: ${error.message}`);
  }
}

function printHelp() {
  console.log(`SkillFlow DOE Analyzer\n\nUsage:\n  node src/index.js analyze --fcg <file> [--out <file>] [--group-baseline <file>] [--threshold <n>] [--pretty] [--no-llm-judge] [--llm-cache <file>] [--llm-batch-size <n>] [--llm-votes <n>] [--llm-concurrency <n>] [--llm-escalation-votes <n>] [--llm-escalation-policy <mode>] [--llm-max-batch-chars <n>]\n\nOptions:\n  --fcg <file>                    Required SkillFlow FCG JSON input\n  --out <file>                    Write DOE JSON to file; defaults to stdout\n  --group-baseline <file>         Optional group behavior baseline JSON\n  --threshold <n>                 High-score threshold, default 0.70\n  --pretty                        Pretty-print JSON\n  --no-llm-judge                  Disable default LLM necessity judge and use rule-only scoring\n  --llm-cache <file>              JSONL cache for LLM judge results\n  --llm-batch-size <n>            LLM judge batch size, default 4\n  --llm-votes <n>                 First-pass votes per unit, default 1\n  --llm-concurrency <n>           Concurrent LLM judge requests, default 2\n  --llm-escalation-votes <n>      Votes for escalated units, default 3\n  --llm-escalation-policy <mode>  risk_or_uncertain|none|all, default risk_or_uncertain\n  --llm-max-batch-chars <n>       Approximate max chars per LLM batch, default 60000\n  --llm-model <name>              Override LLM_MODEL\n  --llm-endpoint <url>            Override LLM_ENDPOINT\n  --llm-timeout <ms>              Override LLM_TIMEOUT\n`);
}

if (require.main === module) {
  main().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

module.exports = {
  main,
  parseArgs
};
