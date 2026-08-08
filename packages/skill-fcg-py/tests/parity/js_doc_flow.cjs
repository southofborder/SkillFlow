// Parity driver: read {skillDir, semanticLlm} JSON from argv[2], parse the skill
// with the REAL JS parser, run the REAL JS extractDocumentFlow (rule-only:
// semanticLlm=false, disableLlm=true) and print {nodes, edges} to stdout. Paired
// with test_parity_doc_flow.py. No LLM is exercised.
const fs = require('fs');
const { parseSkill, parseReadme, findExecutableFiles } = require('../../../skill-fcg-analyzer/src/parser/skill-parser');
const { buildDocumentationPlan } = require('../../../skill-fcg-analyzer/src/parser/document-context');
const { extractDocumentFlow } = require('../../../skill-fcg-analyzer/src/parser/doc-flow-extractor');

(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
  const skillData = parseSkill(spec.skillDir);
  const readmeData = parseReadme(spec.skillDir);
  const plan = buildDocumentationPlan(skillData, readmeData, findExecutableFiles(spec.skillDir));
  const flow = await extractDocumentFlow(skillData, readmeData, {
    extractionDocs: plan.extractionDocs,
    reviewDocs: plan.reviewDocs,
    documentationContext: plan.documentationContext,
    semanticLlm: false,
    disableLlm: true
  });
  process.stdout.write(JSON.stringify({ nodes: flow.nodes, edges: flow.edges }));
})();
