#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const {
  analyzeSimilarity,
  parseArgs,
  printUsage
} = require('./grouping');

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`Argument error: ${error.message}`);
    printUsage();
    process.exit(1);
  }

  if (parsed.help) {
    printUsage();
    return;
  }

  if (parsed.command !== 'group') {
    console.error(`Unknown command: ${parsed.command || ''}`);
    printUsage();
    process.exit(1);
  }

  try {
    const result = await analyzeSimilarity(parsed.inputs, parsed.options);
    console.log(`Pair strategy: ${result.statistics.pair_index_strategy}`);
    console.log(`Scored pairs: ${result.statistics.scored_pair_count}/${result.statistics.theoretical_pair_count}`);
    console.log(`Grouped ${result.statistics.grouped_skill_count} skills into ${result.statistics.group_count} groups`);
    console.log(`Ungrouped skills: ${result.statistics.ungrouped_skill_count}`);
    console.log(`Output: ${result.meta.output_dir}`);
  } catch (error) {
    console.error(`Fatal error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = require('./grouping');
