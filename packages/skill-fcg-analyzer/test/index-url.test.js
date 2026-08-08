const test = require('node:test');
const assert = require('node:assert/strict');

const { SkillFCGAnalyzer } = require('../src/index');

test('analyze delegates URL input to analyzeFromUrl', async () => {
  const analyzer = new SkillFCGAnalyzer({ mode: 'quick' });
  let delegatedUrl = '';

  analyzer.analyzeFromUrl = async url => {
    delegatedUrl = url;
    return { ok: true, url };
  };

  const result = await analyzer.analyze('https://example.com/skills/foo/bar');
  assert.equal(delegatedUrl, 'https://example.com/skills/foo/bar');
  assert.equal(result.ok, true);
});
