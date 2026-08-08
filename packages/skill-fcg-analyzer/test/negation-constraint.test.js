const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { parseSkill, parseReadme } = require('../src/parser/skill-parser');
const { extractDocumentFlow, resolvePendingConstraints } = require('../src/parser/doc-flow-extractor');

function createTempSkill(markdownBody) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-negation-'));
  fs.writeFileSync(
    path.join(tempDir, 'SKILL.md'),
    `---\nname: negation-test\ndescription: Use when testing.\nversion: 0.1.0\n---\n\n${markdownBody}\n`,
    'utf-8'
  );
  return tempDir;
}

async function withSkill(markdownBody, refiner, fn, resolveOpts = {}) {
  const tempDir = createTempSkill(markdownBody);
  try {
    const skillData = parseSkill(tempDir);
    const readmeData = parseReadme(tempDir);
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      llmApiKey: 'test-key',
      semanticRefiner: refiner
    });
    // Mirror the pipeline: constraint resolution now runs GLOBALLY after all
    // node sources merge. Here the doc nodes are the only source, but this
    // exercises the same code path index.js uses.
    const resolved = await resolvePendingConstraints(result.nodes, resolveOpts);
    result.nodes = resolved.nodes; // already includes synthesized endpoints
    result.edges = result.edges.concat(resolved.edges);
    return await fn(result);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

// Refiner that classifies by matching the node's instruction text.
function negationRefiner(node) {
  const text = String(node.instructionText || node.formal_semantics?.evidence?.text || '').toLowerCase();
  if (text.includes('install') && text.includes('vetting')) {
    return JSON.stringify({
      classification: 'policy_rule', actionability: 'runtime_action', operation_type: 'guard',
      negation_kind: 'constraint',
      constraint_edge: { kind: 'ordering', before_action: 'vet skill', after_action: 'install skill', note: '' },
      confidence: 0.9, reason: 'vetting must precede install'
    });
  }
  if (text.includes('overwrite')) {
    return JSON.stringify({
      classification: 'policy_rule', actionability: 'runtime_action', operation_type: 'guard',
      negation_kind: 'constraint',
      constraint_edge: { kind: 'guard', guarded_action: 'overwrite existing files', note: '' },
      confidence: 0.9, reason: 'overwrite is forbidden'
    });
  }
  if (text.includes('send') && text.includes('external')) {
    return JSON.stringify({
      classification: 'description', actionability: 'context_only',
      negation_kind: 'disclaimer', constraint_edge: null,
      confidence: 0.9, reason: 'capability disclaimer'
    });
  }
  // default: keep as a plain action
  return JSON.stringify({ classification: 'workflow_instruction', actionability: 'runtime_action', operation_type: 'read', confidence: 0.6, reason: 'action' });
}

test('ordering constraint with matchable endpoints produces a doc_flow_constraint edge', async () => {
  await withSkill(
    '## Steps\nVet the skill thoroughly.\nInstall the skill from the registry.\n## Rules\nNever install a skill without vetting it first.',
    negationRefiner,
    (result) => {
      const constraintEdges = result.edges.filter(e => e.validation_method === 'doc_flow_constraint');
      assert.ok(constraintEdges.length >= 1, 'expected at least one constraint edge');
      const e = constraintEdges[0];
      assert.equal(e.type, 'control_flow');
      assert.equal(e.data_flow.from_param, 'state');
      assert.equal(e.data_flow.to_param, 'state');
      assert.match(e.semantic_reason, /must precede/);
    }
  );
});

test('guard-kind constraint marks node conditions and creates NO edge', async () => {
  await withSkill(
    '## Rules\nNever overwrite existing files.',
    negationRefiner,
    (result) => {
      const constraintEdges = result.edges.filter(e => e.validation_method === 'doc_flow_constraint');
      assert.equal(constraintEdges.length, 0, 'guard constraint must not create an edge');
      const node = result.nodes.find(n =>
        String(n.instructionText || '').toLowerCase().includes('overwrite'));
      assert.ok(node, 'overwrite node should be retained as a runtime action');
      const conds = node.formal_semantics?.conditions || [];
      assert.ok(conds.some(c => /constraint:/.test(String(c.text || ''))), 'guarded action should be in conditions');
      assert.equal(node.formal_semantics.operation_type, 'guard');
    }
  );
});

test('capability disclaimer is dropped to context', async () => {
  await withSkill(
    '## Notes\nThe skill does not send any personal data externally.',
    negationRefiner,
    (result) => {
      const node = result.nodes.find(n =>
        String(n.instructionText || n.formal_semantics?.evidence?.text || '').toLowerCase().includes('send'));
      // disclaimer -> context node (doc_definition), excluded from flow
      if (node) {
        assert.ok(
          node.semanticKind === 'doc_definition' || node.excludeFromFlow === true,
          'disclaimer should be context-only'
        );
      }
      const constraintEdges = result.edges.filter(e => e.validation_method === 'doc_flow_constraint');
      assert.equal(constraintEdges.length, 0);
    }
  );
});

test('ordering constraint with unmatchable endpoints synthesizes constraint nodes', async () => {
  // No "vet"/"install" action steps exist elsewhere, so endpoints must be synthesized.
  await withSkill(
    '## Rules\nNever install a skill without vetting it first.',
    negationRefiner,
    (result) => {
      const synth = result.nodes.filter(n => n.synthesized_from === 'negation_constraint');
      assert.ok(synth.length >= 1, 'expected synthesized constraint endpoint(s)');
      const constraintEdges = result.edges.filter(e => e.validation_method === 'doc_flow_constraint');
      assert.ok(constraintEdges.length >= 1, 'expected a constraint edge between synthesized/real nodes');
    }
  );
});

test('LLM endpoint resolver links constraint to word-form / paraphrase nodes instead of synthesizing', async () => {
  // Steps are worded so the rule matcher (stemmed token overlap) cannot place
  // "vet skill" / "install skill": "Review the package" and "Deploy it".
  // The injected resolver maps each endpoint to the real node, so NO synthesis.
  const resolver = async ({ phrases, candidates }) => {
    const findId = (needle) => {
      const i = candidates.findIndex(c => c.text.toLowerCase().includes(needle));
      return i >= 0 ? `n${i + 1}` : null;
    };
    const results = phrases.map((phrase) => {
      if (/vet/.test(phrase)) return { phrase, node_id: findId('review') };
      if (/install/.test(phrase)) return { phrase, node_id: findId('deploy') };
      return { phrase, node_id: null };
    });
    return JSON.stringify({ results });
  };

  await withSkill(
    '## Steps\nReview the package thoroughly.\nDeploy it to the target environment.\n## Rules\nNever install a skill without vetting it first.',
    negationRefiner,
    (result) => {
      const synth = result.nodes.filter(n => n.synthesized_from === 'negation_constraint');
      assert.equal(synth.length, 0, 'LLM resolved both endpoints, so nothing should be synthesized');
      const constraintEdges = result.edges.filter(e => e.validation_method === 'doc_flow_constraint');
      assert.equal(constraintEdges.length, 1, 'expected exactly one constraint edge');
      const e = constraintEdges[0];
      const byName = new Map(result.nodes.map(n => [n.name, n]));
      const src = byName.get(e.source);
      const tgt = byName.get(e.target);
      assert.ok(/review/i.test(String(src?.instructionText || '')), 'before endpoint should link to the review node');
      assert.ok(/deploy/i.test(String(tgt?.instructionText || '')), 'after endpoint should link to the deploy node');
    },
    { llmApiKey: 'test-key', constraintEndpointResolver: resolver }
  );
});
