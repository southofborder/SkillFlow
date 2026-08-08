// Parity driver: read {files:[abs...], rootDir, semanticLlm} JSON from argv[2],
// run the REAL JS extractScriptFlow, print {nodes, edges} to stdout. Paired with
// test_parity_script_flow.py. Runs with semanticLlm:false (rule-only) so no LLM.
const fs = require('fs');
const { extractScriptFlow } = require('../../../skill-fcg-analyzer/src/parser/script-flow-extractor');

(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
  const flow = await extractScriptFlow(spec.files || [], {
    rootDir: spec.rootDir || '',
    semanticLlm: spec.semanticLlm === true
  });
  process.stdout.write(JSON.stringify(flow));
})();
