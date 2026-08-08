// Parity driver: REAL JS buildNodeProfile over a list of nodes (+ optional edges
// grouped by target/source into context). Prints [profile...]. Paired with
// test_parity_node_profiler.py. Exercises the metadata-pollution guards.
const path = require('path');
const ANALYZER = path.resolve(__dirname, '../../../skill-fcg-analyzer/src');
const { buildNodeProfiles } = require(path.join(ANALYZER, 'security/node-profiler'));

(() => {
  const spec = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf-8'));
  const profiles = buildNodeProfiles(spec.nodes || [], spec.edges || []);
  process.stdout.write(JSON.stringify(profiles));
})();
