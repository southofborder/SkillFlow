const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { extractDocumentFlow } = require('../src/parser/doc-flow-extractor');
const { parseSkill, parseReadme, findExecutableFiles } = require('../src/parser/skill-parser');
const { buildDocumentationPlan } = require('../src/parser/document-context');

// A skill whose action steps span TWO sections. Under same-section scope, the
// last step of section A must NOT be sequence-linked to the first step of
// section B; under global scope, it is.
const BODY = `---
name: seqscope
description: two-section procedure.
---

## Fetch

Read the config file from disk.
Send the config to the remote API at config.example.com.

## Report

Write the response to the local log.
Summarize the outcome for the user.
`;

async function sequenceEdgesFor(scope) {
  const prev = process.env.FCG_SEQUENCE_EDGE_SCOPE;
  if (scope === undefined) delete process.env.FCG_SEQUENCE_EDGE_SCOPE;
  else process.env.FCG_SEQUENCE_EDGE_SCOPE = scope;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-seqscope-'));
  try {
    fs.writeFileSync(path.join(dir, 'SKILL.md'), BODY, 'utf-8');
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
    const seqEdges = (flow.edges || []).filter(e =>
      e.type === 'control_flow' && /Sequential markdown steps/.test(e.semantic_reason || ''));
    // Map node name -> section for cross-section detection.
    const sectionByName = new Map(flow.nodes.map(n => [n.name, String(n.location?.section || '')]));
    const crossSection = seqEdges.filter(e =>
      sectionByName.get(e.source) !== undefined &&
      sectionByName.get(e.target) !== undefined &&
      sectionByName.get(e.source) !== sectionByName.get(e.target));
    return { seqEdges, crossSection };
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
    if (prev === undefined) delete process.env.FCG_SEQUENCE_EDGE_SCOPE;
    else process.env.FCG_SEQUENCE_EDGE_SCOPE = prev;
  }
}

test('Part 3: default (same-section) scope emits no cross-section sequence edge', async () => {
  const { seqEdges, crossSection } = await sequenceEdgesFor(undefined);
  assert.ok(seqEdges.length >= 1, 'intra-section sequence edges should still exist');
  assert.equal(crossSection.length, 0, 'no sequence edge may cross a section boundary by default');
});

test('Part 3: explicit section scope behaves the same as default', async () => {
  const { crossSection } = await sequenceEdgesFor('section');
  assert.equal(crossSection.length, 0);
});

test('Part 3: global scope restores cross-section sequence linking (A/B switch)', async () => {
  const { seqEdges, crossSection } = await sequenceEdgesFor('global');
  assert.ok(seqEdges.length >= 1, 'global scope still emits sequence edges');
  assert.ok(crossSection.length >= 1, 'global scope links across section boundaries');
});
