const test = require('node:test');
const assert = require('node:assert/strict');

const { getHeuristicValidation, validatePairs } = require('../src/analyzer/llm-validator');

test('heuristic validation marks exact param overlap as compatible', () => {
  const sourceTool = {
    name: 'feishu_bitable_app.create',
    output: {
      app_token: { type: 'string' }
    }
  };

  const targetTool = {
    name: 'feishu_bitable_table.list',
    input: {
      app_token: { type: 'string' }
    }
  };

  const result = getHeuristicValidation(sourceTool, targetTool);
  assert.equal(result.is_compatible, true);
  assert.ok(result.confidence >= 0.4);
});

test('heuristic validation can reject unrelated pairs', () => {
  const sourceTool = {
    name: 'tool.create',
    output: {
      success: { type: 'boolean' }
    }
  };

  const targetTool = {
    name: 'analytics.query',
    input: {
      sql: { type: 'string' }
    }
  };

  const result = getHeuristicValidation(sourceTool, targetTool);
  assert.equal(result.is_compatible, false);
});

test('validatePairs batches only high-value dependency candidates and uses rule fallback for the rest', async () => {
  const oldKey = process.env.LLM_API_KEY;
  process.env.LLM_API_KEY = 'test-key';
  try {
    let batchCalls = 0;
    const pairs = Array.from({ length: 3 }, (_, index) => ({
      candidate_id: `dep_${index + 1}`,
      source: {
        id: `source_${index}`,
        name: `source.${index}`,
        output: { payload: { type: 'object' } }
      },
      target: {
        id: `target_${index}`,
        name: `target.${index}`,
        input: { payload: { type: 'object' } }
      },
      compatibleParams: [{ fromParam: 'payload', toParam: 'payload', fromType: 'object', toType: 'object' }],
      confidence: 0.95 - index * 0.01,
      candidate_kind: index === 0 ? 'boundary_impact' : 'scoped_sequence',
      high_value: index === 0,
      high_value_reasons: index === 0 ? ['boundary-impact'] : [],
      llm_priority: index === 0 ? 1 : 50
    }));

    const edges = await validatePairs(pairs, {
      apiKey: 'test-key',
      dependencyLlmPolicy: 'high_value',
      dependencyLlmMaxPairs: 2,
      dependencyLlmCache: false,
      semanticBatchValidator: async ({ candidates }) => {
        batchCalls += 1;
        assert.equal(candidates.length, 1);
        return {
          results: [{
            candidate_id: candidates[0].candidate_id,
            is_compatible: true,
            confidence: 1,
            reason: 'LLM accepted high-value edge',
            data_flow_description: 'payload -> payload'
          }]
        };
      }
    });

    assert.equal(batchCalls, 1);
    assert.equal(edges.length, 3);
    assert.equal(edges.filter(edge => edge.validation_method === 'dependency_llm_high_value').length, 1);
    assert.equal(edges.filter(edge => edge.validation_method === 'dependency_rule').length, 2);
    assert.equal(edges.statistics.dependency_llm_candidate_count, 1);
    assert.equal(edges.statistics.dependency_llm_request_count, 1);
  } finally {
    if (oldKey === undefined) {
      delete process.env.LLM_API_KEY;
    } else {
      process.env.LLM_API_KEY = oldKey;
    }
  }
});

test('validatePairs uses dependency LLM cache before batch calls', async () => {
  const oldKey = process.env.LLM_API_KEY;
  const oldCache = process.env.FCG_DEPENDENCY_LLM_CACHE;
  process.env.LLM_API_KEY = 'test-key';
  const fs = require('fs');
  const os = require('os');
  const path = require('path');
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-dep-cache-'));
  const cachePath = path.join(tempDir, 'cache.jsonl');

  try {
    const pair = {
      candidate_id: 'dep_cached',
      source: { id: 'source_cached', name: 'source.cached', output: { payload: { type: 'object' } } },
      target: { id: 'target_cached', name: 'target.cached', input: { payload: { type: 'object' } } },
      compatibleParams: [{ fromParam: 'payload', toParam: 'payload', fromType: 'object', toType: 'object' }],
      confidence: 0.9,
      candidate_kind: 'boundary_impact',
      high_value: true,
      high_value_reasons: ['boundary-impact'],
      llm_priority: 1
    };

    let calls = 0;
    const first = await validatePairs([pair], {
      apiKey: 'test-key',
      dependencyLlmCache: cachePath,
      semanticBatchValidator: async ({ candidates }) => {
        calls += 1;
        return {
          results: [{
            candidate_id: candidates[0].candidate_id,
            is_compatible: true,
            confidence: 0.9,
            reason: 'cached accept',
            data_flow_description: 'payload -> payload'
          }]
        };
      }
    });
    const second = await validatePairs([pair], {
      apiKey: 'test-key',
      dependencyLlmCache: cachePath,
      semanticBatchValidator: async () => {
        calls += 1;
        throw new Error('should not call batch validator on cache hit');
      }
    });

    assert.equal(calls, 1);
    assert.equal(first.statistics.dependency_llm_cache_hit_count, 0);
    assert.equal(second.statistics.dependency_llm_cache_hit_count, 1);
    assert.equal(second[0].validation_method, 'dependency_llm_high_value');
  } finally {
    if (oldKey === undefined) delete process.env.LLM_API_KEY;
    else process.env.LLM_API_KEY = oldKey;
    if (oldCache === undefined) delete process.env.FCG_DEPENDENCY_LLM_CACHE;
    else process.env.FCG_DEPENDENCY_LLM_CACHE = oldCache;
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
