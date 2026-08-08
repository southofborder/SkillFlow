const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { extractDocumentFlow } = require('../src/parser/doc-flow-extractor');
const { parseSkill, parseReadme, findExecutableFiles } = require('../src/parser/skill-parser');
const { buildDocumentationPlan } = require('../src/parser/document-context');

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

function withSkill(prefix, body, fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  try {
    writeSkill(dir, body);
    return fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

// 1. A bullet wrapped across physical lines collapses into ONE node whose text
//    spans the whole item, instead of the continuation becoming stray nodes.
test('multi-line bullet folds into one node with full merged text', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-fold-'));
  try {
    writeSkill(dir, `---
name: folder
description: Fetches and forwards.
---

# Steps

- Fetch the remote report from the archive service
  and send it to the analytics endpoint at metrics.example.com
- Read the local cache file
`);
    const { flow } = await docFlowFor(dir);
    // The wrapped continuation ("and send it to ... metrics.example.com") must
    // be merged into the first bullet's node, not become a separate fragment.
    const merged = flow.nodes.find(n => /send it to|metrics\.example\.com/i.test(n.instructionText || ''));
    assert.ok(merged, 'continuation text must be merged into the bullet node');
    const fetchNode = flow.nodes.find(n => /Fetch the remote report/i.test(n.instructionText || ''));
    assert.ok(fetchNode, 'first bullet node should exist');
    // The merged node and the fetch node should be the SAME node (one item),
    // i.e. the continuation did not spawn its own separate node on another line.
    assert.equal(merged.location.line, fetchNode.location.line,
      'continuation must fold into the bullet start line, not a separate node');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 2. A list under a disclaimer lead-in inherits the disclaimer scope, so bullets
//    that do NOT repeat a negation word are still treated as context.
test('list items inherit disclaimer scope from lead-in', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-scope-'));
  try {
    writeSkill(dir, `---
name: scoped
description: Local only.
---

# Overview

**What this skill does NOT do:**
- Connect to any wallet or financial account
- Send personal data to external services
- Execute real trades on the network
`);
    const { flow } = await docFlowFor(dir);
    // None of these bullets repeats "does not"; without block scope, "Send
    // personal data to external services" would classify as egress.
    const scoped = flow.nodes.filter(n =>
      /wallet|personal data|real trades/i.test(n.instructionText || ''));
    assert.ok(scoped.length > 0, 'expected scoped bullet nodes to exist');
    assert.ok(scoped.every(n => n.excludeFromFlow || n.operationType === 'context' || n.operationType === 'guard'),
      'all disclaimer-scoped bullets must be context/guard');
    const leak = scoped.filter(n => n.operationType === 'external_egress' || n.operationType === 'invoke_tool');
    assert.equal(leak.length, 0, 'disclaimer-scoped bullets must not produce egress/invoke');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 3a. STRONG scope: an explicit "What this skill does NOT do:" lead-in governs
//     the whole list. Even imperative-looking bullets ("Send ...", "Execute
//     ...") are the negated actions and must be suppressed to context.
test('explicit "does NOT do" lead-in suppresses even imperative-looking bullets', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-strong-'));
  try {
    writeSkill(dir, `---
name: strong
description: local only.
---

# Boundaries

**What this skill does NOT do:**
- Connect to any wallet or financial account
- Send personal data to external services
- Execute real trades on the network
`);
    const { flow } = await docFlowFor(dir);
    const bullets = flow.nodes.filter(n => /wallet|personal data|real trades/i.test(n.instructionText || ''));
    assert.equal(bullets.length, 3, 'all three disclaimer bullets should produce nodes');
    assert.ok(bullets.every(n => n.excludeFromFlow || n.operationType === 'context' || n.operationType === 'guard'),
      'every bullet under an explicit "does NOT do" lead-in must be context/guard');
    const leak = bullets.filter(n => n.operationType === 'external_egress' || n.operationType === 'invoke_tool');
    assert.equal(leak.length, 0, 'no bullet under a negation lead-in may become egress/invoke');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 3b. SOFT scope reverse protection: in a negation SECTION (e.g. "Limitations"),
//     a non-imperative descriptive bullet is context, but an explicit imperative
//     runtime instruction is NOT suppressed — it may be a real sink. This is the
//     guard that keeps weather's `- PNG: curl ...` alive in a tips-like section.
test('imperative bullet in a soft negation section keeps reverse protection', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-soft-'));
  try {
    writeSkill(dir, `---
name: soft
description: has limitations section.
---

## Limitations

- The cache is best-effort and may be stale
- Send the diagnostic bundle to logs.example.com when debugging
`);
    const { flow } = await docFlowFor(dir);
    // Descriptive bullet -> context.
    const cacheNode = flow.nodes.find(n => /cache is best-effort|stale/i.test(n.instructionText || ''));
    assert.ok(cacheNode, 'descriptive bullet node should exist');
    assert.ok(cacheNode.excludeFromFlow || cacheNode.operationType === 'context' || cacheNode.operationType === 'guard',
      'descriptive bullet in a limitations section stays context');
    // Imperative "Send ... to <host>" bullet -> survives as a runtime action.
    const sendNode = flow.nodes.find(n => /logs\.example\.com|diagnostic bundle/i.test(n.instructionText || ''));
    assert.ok(sendNode, 'imperative send bullet node should exist');
    assert.ok(!sendNode.excludeFromFlow && sendNode.role !== 'negated_disclaimer' &&
      sendNode.operationType !== 'context' && sendNode.operationType !== 'guard',
      `imperative bullet must survive soft section scope, got ${sendNode.operationType}`);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 4. Pure prose (no lists) is unchanged: single-line sentences parse exactly as
//    before. We assert prose still yields the same action it always did.
test('plain prose lines are unaffected by block segmentation', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-prose-'));
  try {
    writeSkill(dir, `---
name: prose
description: prose only.
---

# Flow

Read the market data and send it to the analytics API at metrics.example.com.

Summarize the findings for the user.
`);
    const { flow } = await docFlowFor(dir);
    // Prose egress sentence still produces an egress action node.
    const egress = flow.nodes.filter(n =>
      n.operationType === 'external_egress' && /metrics\.example\.com|analytics/i.test(n.instructionText || ''));
    assert.ok(egress.length >= 1, 'prose egress sentence must still be extracted');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 5. An enumeration list (bold label : piped values) stays context, not action.
test('enum-style bullets remain context, not actions', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-enum-'));
  try {
    writeSkill(dir, `---
name: enum
description: options.
---

# Options

- **mode**: fast | slow | off
- **retries**: 0 | 1 | 3
`);
    const { flow } = await docFlowFor(dir);
    const enumNodes = flow.nodes.filter(n => /mode|retries/i.test(n.instructionText || ''));
    assert.ok(enumNodes.length > 0, 'enum bullets should produce nodes');
    assert.ok(enumNodes.every(n => n.excludeFromFlow), 'enum bullets must be context-only');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

// 6. An ordered list of actions yields one action node per step (not merged,
//    not lost).
test('ordered action steps each become their own action node', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-ordered-'));
  try {
    writeSkill(dir, `---
name: ordered
description: steps.
---

# Procedure

1. Read the configuration file from disk
2. Send the configuration to the remote API at config.example.com
3. Write the response to the local log
`);
    const { flow } = await docFlowFor(dir);
    // Three distinct steps on three lines -> at least three action-bearing nodes,
    // each on its own line (not merged into one).
    const actionLines = new Set(flow.nodes
      .filter(n => !n.excludeFromFlow)
      .map(n => n.location?.line));
    assert.ok(actionLines.size >= 3, `expected >=3 distinct action lines, got ${actionLines.size}`);
    const egress = flow.nodes.filter(n =>
      n.operationType === 'external_egress' && /config\.example\.com/i.test(n.instructionText || ''));
    assert.ok(egress.length >= 1, 'the send step must be an egress action');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
