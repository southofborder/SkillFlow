const test = require('node:test');
const assert = require('node:assert/strict');

const { normalizeValidationResult } = require('../../../shared/llm-utils.cjs');

test('normalizeValidationResult accepts textual confidence and boolean strings', () => {
  const result = normalizeValidationResult('{"is_compatible":"yes","confidence":"medium","reason":"Compatible","data_flow_description":"token -> input"}');
  assert.equal(result.is_compatible, true);
  assert.equal(result.confidence, 0.6);
  assert.equal(result.data_flow_description, 'token -> input');
});
