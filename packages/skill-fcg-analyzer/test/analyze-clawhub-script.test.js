const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const {
  parseArgs,
  parseSkillNameFromUrl,
  sanitizeSkillName,
  buildSkillOutputPaths,
  isHttpUrl
} = require('../scripts/analyze-clawhub');

test('parseArgs parses urls and output directory', () => {
  const options = parseArgs([
    '--url', 'https://clawhub.ai/skills/foo/alpha',
    'https://clawhub.ai/skills/foo/beta',
    '--results', './results-custom',
    '--llm-timeout', '5000'
  ]);

  assert.deepEqual(options.urls, [
    'https://clawhub.ai/skills/foo/alpha',
    'https://clawhub.ai/skills/foo/beta'
  ]);
  assert.equal(options.resultsRoot, path.resolve('./results-custom'));
  assert.equal(options.llmTimeout, 5000);
});

test('parseSkillNameFromUrl handles download suffix', () => {
  const name = parseSkillNameFromUrl('https://clawhub.ai/skills/foo/my-skill/download?x=1');
  assert.equal(name, 'my-skill');
});

test('sanitizeSkillName keeps unicode and removes invalid filename chars', () => {
  const safe = sanitizeSkillName('技能:My/Skill?');
  assert.equal(safe, '技能_My_Skill_');
});

test('buildSkillOutputPaths matches required naming convention', () => {
  const outputs = buildSkillOutputPaths('D:/tmp/results', 'my-skill');
  assert.equal(outputs.skillDir.endsWith(path.join('results', 'my-skill')), true);
  assert.equal(outputs.fullJson.endsWith(path.join('my-skill', 'my-skill_full.json')), true);
  assert.deepEqual(Object.keys(outputs).sort(), ['fullJson', 'skillDir', 'skillMarkdown'].sort());
});

test('isHttpUrl validates http/https only', () => {
  assert.equal(isHttpUrl('https://clawhub.ai/skills/foo/bar'), true);
  assert.equal(isHttpUrl('http://example.com/a.zip'), true);
  assert.equal(isHttpUrl('C:/tmp/a.zip'), false);
});
