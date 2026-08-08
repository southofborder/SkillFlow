const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { SkillFCGAnalyzer, parseArgs } = require('../src/index');
const { parseSkill, parseReadme } = require('../src/parser/skill-parser');
const { extractDocumentFlow } = require('../src/parser/doc-flow-extractor');

function createTempSkill(markdownBody) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-semantic-llm-'));
  fs.writeFileSync(
    path.join(tempDir, 'SKILL.md'),
    `---
name: semantic-llm-test
description: Use when command fails.
version: 0.1.0
---

${markdownBody}
`,
    'utf-8'
  );
  return tempDir;
}

function edgeSignatures(edges) {
  return edges
    .map(edge => `${edge.source}->${edge.target}:${edge.type}:${edge.validation_method}`)
    .sort();
}

async function withParsedSkill(markdownBody, fn) {
  const tempDir = createTempSkill(markdownBody);
  try {
    const skillData = parseSkill(tempDir);
    const readmeData = parseReadme(tempDir);
    return await fn(skillData, readmeData);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

test('parseArgs rejects removed FCG compatibility switches while semantic review stays default', () => {
  const defaults = parseArgs(['analyze', 'skill.zip']);
  assert.equal(defaults.semanticLlm, true);

  assert.throws(() => parseArgs(['analyze', 'skill.zip', '--doc' + '-flow']), /Unknown option/);
  assert.throws(() => parseArgs(['analyze', 'skill.zip', '--semantic' + '-llm']), /Unknown option/);

  // Pin disableLlm off so this assertion tests only the semanticLlm option
  // itself, independent of a FCG_DISABLE_LLM=1 in the ambient environment
  // (which would otherwise force this.semanticLlm to false via index.js:61).
  const analyzer = new SkillFCGAnalyzer({ semanticLlm: true, disableLlm: false });
  assert.equal(analyzer.semanticLlm, true);
});

test('doc-flow can still disable semantic refiner explicitly for unit tests', async () => {
  await withParsedSkill('When command fails, read `memory.md` and update `memory.md`.', async (skillData, readmeData) => {
    let calls = 0;
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: false,
      semanticRefiner: async () => {
        calls += 1;
        return { operation_type: 'review' };
      }
    });

    assert.equal(calls, 0);
    assert.ok(result.nodes.some(node => node.formal_semantics));
  });
});

test('semanticLlm true without API key fails when no test refiner is supplied', async () => {
  await withParsedSkill('When command fails, read `memory.md` and update `memory.md`.', async (skillData, readmeData) => {
    const oldKey = process.env.LLM_API_KEY;
    try {
      delete process.env.LLM_API_KEY;
      await assert.rejects(
        () => extractDocumentFlow(skillData, readmeData, { semanticLlm: true }),
        /LLM_API_KEY is required for FCG Markdown semantic gate/
      );
    } finally {
      if (oldKey === undefined) {
        delete process.env.LLM_API_KEY;
      } else {
        process.env.LLM_API_KEY = oldKey;
      }
    }
  });
});

test('semantic refiner supplements low-confidence formal_semantics without changing edges', async () => {
  await withParsedSkill('When command fails, read `memory.md` and update `memory.md`.', async (skillData, readmeData) => {
    const baseline = await extractDocumentFlow(skillData, readmeData, { semanticLlm: false });
    let calls = 0;
    const refined = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      llmApiKey: 'test-key',
      semanticRefiner: async () => {
        calls += 1;
        return JSON.stringify({
          operation_type: 'review',
          targets: [{ type: 'file', value: 'memory.md', raw: 'memory.md' }],
          conditions: [{ type: 'failure', text: 'When command fails' }],
          effects: ['read_context', 'summarize', 'illegal_effect'],
          confidence: 0.91,
          reason: 'The instruction reviews memory after a failure.'
        });
      }
    });

    assert.ok(calls > 0);
    assert.deepEqual(edgeSignatures(refined.edges), edgeSignatures(baseline.edges));

    const refinedNode = refined.nodes.find(node =>
      String(node.formal_semantics?.evidence?.method || '').includes('semantic_llm_gate')
    );
    assert.ok(refinedNode);
    assert.equal(refinedNode.formal_semantics.operation_type, 'review');
    assert.equal(refinedNode.formal_semantics.confidence, 0.91);
    assert.deepEqual(refinedNode.formal_semantics.effects, ['read_context', 'summarize']);
    assert.ok(refinedNode.formal_semantics.targets.some(target => target.type === 'file' && target.value === 'memory.md'));
    assert.equal(refinedNode.formal_semantics.evidence.llm_reason, 'The instruction reviews memory after a failure.');
  });
});

test('semantic refiner invalid response becomes context-only review error', async () => {
  await withParsedSkill('When command fails, read `memory.md` and update `memory.md`.', async (skillData, readmeData) => {
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      llmApiKey: 'test-key',
      semanticRefiner: async () => 'not json'
    });

    const fallbackNode = result.nodes.find(node =>
      node.semanticKind === 'doc_review_error' &&
      node.formal_semantics?.evidence?.method === 'semantic_llm_gate_error'
    );
    assert.ok(fallbackNode);
    assert.equal(fallbackNode.excludeFromFlow, true);
    assert.ok(fallbackNode.formal_semantics.evidence.llm_reason.includes('Invalid semantic LLM JSON'));
  });
});

test('semantic gate batches candidates and localizes missing candidate failures', async () => {
  await withParsedSkill([
    'Read `memory.md` before answering.',
    'Update `memory.md` after confirmed corrections.'
  ].join('\n'), async (skillData, readmeData) => {
    let batchCalls = 0;
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      semanticGateBatchSize: 50,
      semanticBatchRefiner: async (_nodes, context) => {
        batchCalls += 1;
        return {
          results: context.candidates.slice(0, -1).map(candidate => ({
            id: candidate.id,
            classification: 'workflow_instruction',
            actionability: 'runtime_action',
            grammar: 'imperative SVO instruction',
            completed_sentence: 'The agent reads or updates memory.md.',
            operation_type: 'review',
            targets: [{ type: 'file', value: 'memory.md', raw: 'memory.md' }],
            conditions: [],
            effects: ['read_context'],
            confidence: 0.9,
            reason: 'Batched runtime instruction.'
          }))
        };
      }
    });

    assert.equal(batchCalls, 1);
    assert.ok(result.nodes.some(node => node.semantic_gate?.method === 'semantic_llm_gate'));
    assert.ok(result.nodes.some(node => node.semanticKind === 'doc_review_error'));
  });
});

test('semantic gate cache avoids repeated batch refiner calls', async () => {
  const cacheDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-semantic-cache-'));
  const cachePath = path.join(cacheDir, 'semantic-gate.jsonl');

  try {
    await withParsedSkill('Read `memory.md` before answering.', async (skillData, readmeData) => {
      let batchCalls = 0;
      const first = await extractDocumentFlow(skillData, readmeData, {
        semanticLlm: true,
        semanticGateCache: cachePath,
        semanticBatchRefiner: async (_nodes, context) => {
          batchCalls += 1;
          return {
            results: context.candidates.map(candidate => ({
              id: candidate.id,
              classification: 'workflow_instruction',
              actionability: 'runtime_action',
              grammar: 'imperative SVO instruction',
              completed_sentence: 'The agent reads memory.md before answering.',
              operation_type: 'read',
              targets: [{ type: 'file', value: 'memory.md', raw: 'memory.md' }],
              conditions: [],
              effects: ['read_context'],
              confidence: 0.92,
              reason: 'Cached runtime instruction.'
            }))
          };
        }
      });

      assert.equal(batchCalls, 1);
      assert.ok(first.nodes.some(node => node.semantic_gate?.method === 'semantic_llm_gate'));

      const second = await extractDocumentFlow(skillData, readmeData, {
        semanticLlm: true,
        semanticGateCache: cachePath,
        semanticBatchRefiner: async () => {
          throw new Error('cache miss');
        }
      });

      assert.equal(batchCalls, 1);
      assert.ok(second.nodes.some(node => node.semantic_gate?.cache_hit === true));
    });
  } finally {
    fs.rmSync(cacheDir, { recursive: true, force: true });
  }
});

test('semantic gate does not cap more than 200 candidates by default and splits by char budget', async () => {
  const lines = Array.from({ length: 220 }, (_, index) => `Read \`file-${index + 1}.md\` before answering.`);
  await withParsedSkill(lines.join('\n'), async (skillData, readmeData) => {
    let batchCalls = 0;
    let candidateCount = 0;
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      semanticGateBatchSize: 500,
      semanticGateMaxBatchChars: 4000,
      semanticBatchRefiner: async (_nodes, context) => {
        batchCalls += 1;
        candidateCount += context.candidates.length;
        return {
          results: context.candidates.map(candidate => ({
            id: candidate.id,
            classification: 'workflow_instruction',
            actionability: 'runtime_action',
            grammar: 'imperative SVO instruction',
            completed_sentence: 'The agent reads a markdown file before answering.',
            operation_type: 'read',
            targets: [{ type: 'file', value: 'file.md', raw: 'file.md' }],
            conditions: [],
            effects: ['read_context'],
            confidence: 0.9,
            reason: 'Batched runtime instruction.'
          }))
        };
      }
    });

    assert.ok(candidateCount >= 220);
    assert.ok(batchCalls > 1);
    assert.ok(result.nodes.filter(node => node.semantic_gate?.method === 'semantic_llm_gate').length >= 220);
  });
});

test('semantic gate retries failed batches by splitting to single candidates', async () => {
  await withParsedSkill([
    'Read `alpha.md` before answering.',
    'Read `beta.md` before answering.'
  ].join('\n'), async (skillData, readmeData) => {
    let multiCandidateAttempts = 0;
    let singleCandidateAttempts = 0;
    const result = await extractDocumentFlow(skillData, readmeData, {
      semanticLlm: true,
      semanticGateBatchSize: 10,
      semanticGateMaxBatchChars: 60000,
      semanticBatchRefiner: async (nodes, context) => {
        if (nodes.length > 1) {
          multiCandidateAttempts += 1;
          throw new Error('batch too large');
        }
        singleCandidateAttempts += 1;
        return {
          results: context.candidates.map(candidate => ({
            id: candidate.id,
            classification: 'workflow_instruction',
            actionability: 'runtime_action',
            grammar: 'imperative SVO instruction',
            completed_sentence: 'The agent reads a markdown file before answering.',
            operation_type: 'read',
            targets: [{ type: 'file', value: 'alpha.md', raw: 'alpha.md' }],
            conditions: [],
            effects: ['read_context'],
            confidence: 0.9,
            reason: 'Single candidate retry succeeded.'
          }))
        };
      }
    });

    assert.ok(multiCandidateAttempts >= 1);
    assert.ok(singleCandidateAttempts >= 2);
    assert.equal(result.nodes.some(node => node.semanticKind === 'doc_review_error'), false);
  });
});
