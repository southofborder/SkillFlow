const test = require('node:test');
const assert = require('node:assert/strict');

const { parseArgs } = require('../scripts/clawhub-top-skills');

test('clawhub top script accepts --k and -k as aliases for limit', () => {
  assert.equal(parseArgs(['--k', '123']).limit, 123);
  assert.equal(parseArgs(['-k', '45']).limit, 45);
  assert.equal(parseArgs(['--limit', '67']).limit, 67);
});


test('clawhub top script accepts list-download phase for direct FCG preparation', () => {
  assert.equal(parseArgs(['--k', '10', '--phase', 'list-download']).phase, 'list-download');
});
