const test = require('node:test');
const assert = require('node:assert/strict');

const {
  newSemanticGateUsage,
  accumulateSemanticGateUsage,
  summarizeSemanticGateUsage
} = require('../src/parser/doc-flow-extractor');

test('accumulates OpenAI-style usage with prompt_tokens_details.cached_tokens', () => {
  const acc = newSemanticGateUsage();
  accumulateSemanticGateUsage(acc, {
    prompt_tokens: 2546,
    completion_tokens: 1697,
    total_tokens: 4243,
    prompt_tokens_details: { cached_tokens: 2304 }
  });
  assert.equal(acc.calls, 1);
  assert.equal(acc.prompt_tokens, 2546);
  assert.equal(acc.completion_tokens, 1697);
  assert.equal(acc.total_tokens, 4243);
  assert.equal(acc.cached_tokens, 2304);
});

test('accepts alternate cached-token field names across endpoints', () => {
  const a = newSemanticGateUsage();
  accumulateSemanticGateUsage(a, { prompt_tokens: 100, cached_tokens: 40 });
  assert.equal(a.cached_tokens, 40);

  const b = newSemanticGateUsage();
  accumulateSemanticGateUsage(b, { prompt_tokens: 100, prompt_cache_hit_tokens: 55 });
  assert.equal(b.cached_tokens, 55);

  const c = newSemanticGateUsage();
  accumulateSemanticGateUsage(c, { input_tokens: 80, output_tokens: 20 });
  assert.equal(c.prompt_tokens, 80);
  assert.equal(c.completion_tokens, 20);
});

test('sums usage across multiple calls', () => {
  const acc = newSemanticGateUsage();
  accumulateSemanticGateUsage(acc, { prompt_tokens: 1000, prompt_tokens_details: { cached_tokens: 900 } });
  accumulateSemanticGateUsage(acc, { prompt_tokens: 1000, prompt_tokens_details: { cached_tokens: 0 } });
  assert.equal(acc.calls, 2);
  assert.equal(acc.prompt_tokens, 2000);
  assert.equal(acc.cached_tokens, 900);
});

test('ignores missing/invalid usage payloads without throwing', () => {
  const acc = newSemanticGateUsage();
  accumulateSemanticGateUsage(acc, undefined);
  accumulateSemanticGateUsage(acc, null);
  accumulateSemanticGateUsage(acc, 'not-an-object');
  assert.equal(acc.calls, 0);
});

test('summarize computes prompt_cache_hit_ratio and returns null for no calls', () => {
  assert.equal(summarizeSemanticGateUsage(newSemanticGateUsage()), null);

  const acc = newSemanticGateUsage();
  accumulateSemanticGateUsage(acc, { prompt_tokens: 2000, prompt_tokens_details: { cached_tokens: 900 } });
  const summary = summarizeSemanticGateUsage(acc);
  assert.equal(summary.prompt_cache_hit_ratio, 0.45);
  assert.equal(summary.calls, 1);
});
