#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const path = require('path');
const {
  createDoePathReport,
  writeDoePathReport,
  normalizeScope,
  normalizeFormat
} = require('../src/path-report');

function main(argv = process.argv.slice(2)) {
  try {
    const options = resolveOptions(parseArgs(argv));
    if (options.help) {
      printUsage();
      return;
    }
    const report = createDoePathReport(options);
    const written = writeDoePathReport(report, options);
    console.log(`DOE path report completed: ${report.summary.path_count} paths across ${report.summary.skill_count} skills`);
    if (written.markdown) console.log(`Markdown: ${written.markdown}`);
    if (written.json) console.log(`JSON: ${written.json}`);
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
    else if (arg === '--doe-root' && i + 1 < args.length) options.doeRoot = args[++i];
    else if (arg === '--zips-root' && i + 1 < args.length) options.zipsRoot = args[++i];
    else if (arg === '--output' && i + 1 < args.length) options.output = args[++i];
    else if (arg === '--skill' && i + 1 < args.length) options.skill = args[++i];
    else if (arg === '--scope' && i + 1 < args.length) options.scope = args[++i];
    else if (arg === '--format' && i + 1 < args.length) options.format = args[++i];
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return options;
}

function resolveOptions(options = {}) {
  if (options.help) return { help: true };
  const projectRoot = path.resolve(__dirname, '..', '..', '..');
  const root = path.resolve(options.root || path.join(projectRoot, 'results', 'clawhub-top10000'));
  return {
    root,
    fcgRoot: path.resolve(options.fcgRoot || path.join(root, 'fcg')),
    doeRoot: path.resolve(options.doeRoot || path.join(root, 'doe')),
    zipsRoot: path.resolve(options.zipsRoot || path.join(root, 'zips')),
    output: path.resolve(options.output || path.join(root, 'doe', 'reports')),
    skill: options.skill || '',
    scope: normalizeScope(options.scope || 'potential'),
    format: normalizeFormat(options.format || 'both')
  };
}

function printUsage() {
  console.log('Usage:');
  console.log('  node scripts/doe-path-report.js --root <clawhub-run-root> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --root <dir>           Run root containing fcg/, doe/, and zips/');
  console.log('  --fcg-root <dir>       Default <root>/fcg');
  console.log('  --doe-root <dir>       Default <root>/doe');
  console.log('  --zips-root <dir>      Default <root>/zips');
  console.log('  --output <path>        Directory or .md/.json file path, default <root>/doe/reports');
  console.log('  --skill <text>         Filter by skill id, skill name, or output filename fragment');
  console.log('  --scope <scope>        potential|boundary|all, default potential');
  console.log('  --format <format>      md|json|both, default both');
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  resolveOptions,
  main
};
