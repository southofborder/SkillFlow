const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { loadProjectEnv, findNearestEnv, parseEnvFile } = require('../shared/load-env.cjs');

test('parseEnvFile supports quoted values and comments', () => {
  const parsed = parseEnvFile([
    '# comment',
    'LLM_PROVIDER=openai',
    'LLM_MODEL="gpt-5.5"',
    "LLM_ENDPOINT='https://xiaomuai.cn/v1/chat/completions'",
    'LLM_TIMEOUT=30000 # inline comment'
  ].join('\n'));

  assert.equal(parsed.LLM_PROVIDER, 'openai');
  assert.equal(parsed.LLM_MODEL, 'gpt-5.5');
  assert.equal(parsed.LLM_ENDPOINT, 'https://xiaomuai.cn/v1/chat/completions');
  assert.equal(parsed.LLM_TIMEOUT, '30000');
});

test('parseEnvFile rejects malformed lines', () => {
  assert.throws(() => parseEnvFile('NOT A VALID LINE'), /Malformed \.env line/);
});

test('findNearestEnv finds root env from nested directory', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'skillflow-env-'));
  const nested = path.join(root, 'packages', 'skill-similarity-analyzer', 'src');
  fs.mkdirSync(nested, { recursive: true });
  fs.writeFileSync(path.join(root, '.env'), 'LLM_MODEL=gpt-5.5\n', 'utf-8');
  try {
    assert.equal(findNearestEnv([nested]), path.join(root, '.env'));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('loadProjectEnv preserves existing shell env values', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'skillflow-env-'));
  const nested = path.join(root, 'packages', 'skill-sfg', 'src');
  fs.mkdirSync(nested, { recursive: true });
  fs.writeFileSync(path.join(root, '.env'), 'LLM_MODEL=gpt-5.5\nLLM_PROVIDER=openai\n', 'utf-8');
  const previous = process.env.LLM_MODEL;
  const previousProvider = process.env.LLM_PROVIDER;
  process.env.LLM_MODEL = 'deepseek-v4-pro';
  delete process.env.LLM_PROVIDER;

  try {
    const result = loadProjectEnv({ startDir: nested, forceReload: true });
    assert.equal(result.loaded, true);
    assert.equal(process.env.LLM_MODEL, 'deepseek-v4-pro');
    assert.equal(process.env.LLM_PROVIDER, 'openai');
  } finally {
    if (previous === undefined) delete process.env.LLM_MODEL;
    else process.env.LLM_MODEL = previous;
    if (previousProvider === undefined) delete process.env.LLM_PROVIDER;
    else process.env.LLM_PROVIDER = previousProvider;
    fs.rmSync(root, { recursive: true, force: true });
  }
});

