// Parity driver: read {content, sections?, markdownDocs?, readme?} specs (JSON
// array) from argv[2] file, run the REAL JS extractToolCalls on each, print the
// resulting tool-node arrays as JSON to stdout. Paired with the Python port in
// test_parity_tool_extractor.py to prove cross-engine node parity.
const fs = require('fs');
const { extractToolCalls } = require('../../../skill-fcg-analyzer/src/parser/tool-extractor');

const specs = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
const out = specs.map(spec => {
  const skillData = { content: spec.content, sections: spec.sections || [] };
  const readmeData = spec.readme ? { exists: true, content: spec.readme } : null;
  const options = spec.markdownDocs ? { markdownDocs: spec.markdownDocs } : {};
  return extractToolCalls(skillData, readmeData, [], options);
});
process.stdout.write(JSON.stringify(out));
