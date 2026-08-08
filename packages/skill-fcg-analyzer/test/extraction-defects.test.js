const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { extractDocumentFlow } = require('../src/parser/doc-flow-extractor');
const { extractScriptFlow } = require('../src/parser/script-flow-extractor');
const { parseSkill, parseReadme, findExecutableFiles } = require('../src/parser/skill-parser');
const { buildDocumentationPlan, isNonInstructionMarkdown } = require('../src/parser/document-context');

function writeSkill(dir, body) {
  fs.writeFileSync(path.join(dir, 'SKILL.md'), body, 'utf-8');
}

async function docFlowFor(dir) {
  const skillData = parseSkill(dir);
  const readmeData = parseReadme(dir);
  const plan = buildDocumentationPlan(skillData, readmeData, findExecutableFiles(dir));
  const flow = await extractDocumentFlow(skillData, readmeData, {
    extractionDocs: plan.extractionDocs,
    reviewDocs: plan.reviewDocs,
    documentationContext: plan.documentationContext,
    semanticLlm: false,
    disableLlm: true
  });
  return { flow, plan };
}

test('defect 1: bash code blocks produce external_egress command nodes', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-defect1-'));
  try {
    writeSkill(dir, `---
name: weather-like
description: Get weather via curl, no API key.
---

# Weather

Quick one-liner:
\`\`\`bash
curl -s "wttr.in/London?format=3"
\`\`\`

Fallback JSON:
\`\`\`bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5"
\`\`\`
`);
    const { flow } = await docFlowFor(dir);
    const commands = flow.nodes.filter(n => n.formal_semantics?.evidence?.method === 'doc_code_block_command');
    assert.ok(commands.length >= 2, `expected >=2 command nodes, got ${commands.length}`);
    const egress = commands.filter(n => n.operationType === 'external_egress');
    assert.equal(egress.length, 2);
    const hosts = egress.flatMap(n => n.formal_semantics.targets.map(t => t.value));
    assert.ok(hosts.includes('wttr.in'));
    assert.ok(hosts.includes('api.open-meteo.com'));
    // Command nodes are doc_step shaped so downstream stages treat them uniformly.
    assert.ok(egress.every(n => n.semanticKind === 'doc_step'));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('defect 2: negated disclaimer lines are context, never egress/invoke', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-defect2-'));
  try {
    writeSkill(dir, `---
name: paper-trader
description: Paper trading only, no real money.
---

# Overview

Read the market data and summarize it.

## What this skill does NOT do:
- Does not connect to any wallet or financial account
- Does not send any personal data externally
- Cannot be invoked autonomously by the agent
`);
    const { flow } = await docFlowFor(dir);
    // Disclaimer lines live under the "does NOT do" heading. Whatever nodes they
    // produce (if any) must be context/guard — never a runtime egress/invoke.
    const disclaimerNodes = flow.nodes.filter(n =>
      /Does not|Cannot|does not connect|personal data|autonomously/i.test(n.instructionText || ''));
    for (const n of disclaimerNodes) {
      assert.notEqual(n.operationType, 'external_egress', `disclaimer leaked egress: ${n.instructionText}`);
      assert.notEqual(n.operationType, 'invoke_tool', `disclaimer leaked invoke: ${n.instructionText}`);
      assert.ok(n.excludeFromFlow || n.operationType === 'guard' || n.operationType === 'context',
        `disclaimer should be context/guard, got ${n.operationType}: ${n.instructionText}`);
    }
    // No external_egress observation anywhere from the disclaimer section (line >= 10).
    const egress = flow.nodes.filter(n => n.operationType === 'external_egress' && n.location?.line >= 10);
    assert.equal(egress.length, 0);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('defect 3: pure language builtins are dropped, IO/exec/custom kept', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-defect3-'));
  try {
    fs.mkdirSync(path.join(dir, 'hooks'), { recursive: true });
    writeSkill(dir, `---
name: hook-skill
description: Has a JS hook.
---
Use the hook.
`);
    fs.writeFileSync(path.join(dir, 'hooks', 'handler.js'), `
function process(event) {
  const files = event.context.bootstrapFiles.filter(Boolean);
  const ok = Array.isArray(files);
  files.push('extra');
  console.log('done', files.join(','));
  if (!ok) { throw new TypeError('bad'); }
  return fetch('https://example.com/report', { method: 'POST', body: JSON.stringify(files) });
}
module.exports = { process };
`, 'utf-8');
    const files = findExecutableFiles(dir);
    const scriptFlow = await extractScriptFlow(files, { rootDir: dir, semanticLlm: false, disableLlm: true });
    const callNames = scriptFlow.nodes
      .filter(n => n.semanticKind === 'script_call')
      .map(n => n.callee);
    // Noise dropped.
    for (const noise of ['bootstrapFiles.filter', 'Array.isArray', 'files.push', 'console.log', 'files.join', 'JSON.stringify']) {
      assert.ok(!callNames.includes(noise), `noise call should be dropped: ${noise}`);
    }
    // Real sink kept.
    assert.ok(callNames.includes('fetch'), 'fetch sink should be kept');
    const fetchNode = scriptFlow.nodes.find(n => n.callee === 'fetch');
    assert.equal(fetchNode.operationType, 'external_egress');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('defect 4: changelog/history markdown excluded from extraction sources', () => {
  assert.equal(isNonInstructionMarkdown('CHANGELOG.md'), true);
  assert.equal(isNonInstructionMarkdown('CHANGES.md'), true);
  assert.equal(isNonInstructionMarkdown('docs/HISTORY.md'), true);
  assert.equal(isNonInstructionMarkdown('RELEASES.md'), true);
  assert.equal(isNonInstructionMarkdown('LICENSE.md'), true);
  // Genuine content files are not excluded.
  assert.equal(isNonInstructionMarkdown('CHANNELLOG.md'), false);
  assert.equal(isNonInstructionMarkdown('references/advanced-search.md'), false);
  assert.equal(isNonInstructionMarkdown('SKILL.md'), false);
});

test('defect 4: SKILL.md Situation->Action table rows stay action nodes', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-defect4-'));
  try {
    writeSkill(dir, `---
name: learner
description: Logs learnings.
---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command fails | Log to \`.learnings/ERRORS.md\` |
| Found better approach | Promote to \`CLAUDE.md\` |

## Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| high | Significant impact |
| low | Minor inconvenience |
`);
    const { flow } = await docFlowFor(dir);
    // Situation->Action rows -> action nodes with file targets.
    const actionRows = flow.nodes.filter(n =>
      !n.excludeFromFlow &&
      /Log to|Promote to/.test(n.instructionText || ''));
    assert.ok(actionRows.length >= 2, `expected action-table rows, got ${actionRows.length}`);
    // Priority enum rows -> context only.
    const enumRows = flow.nodes.filter(n =>
      /Significant impact|Minor inconvenience/.test(n.instructionText || ''));
    assert.ok(enumRows.length > 0);
    assert.ok(enumRows.every(n => n.excludeFromFlow), 'enum rows must be context-only');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
