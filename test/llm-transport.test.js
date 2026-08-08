const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('http');

const {
  postJsonWithTimeout,
  parseRetryAfterMs,
  isTransientTransportError
} = require('../shared/llm-utils.cjs');

function listen(server) {
  return new Promise(resolve => server.listen(0, () => resolve(server.address().port)));
}

test('parseRetryAfterMs parses delta-seconds and ignores garbage', () => {
  assert.equal(parseRetryAfterMs('2'), 2000);
  assert.equal(parseRetryAfterMs('0'), 0);
  assert.equal(parseRetryAfterMs(''), null);
  assert.equal(parseRetryAfterMs(undefined), null);
  assert.equal(parseRetryAfterMs('not-a-date'), null);
});

test('isTransientTransportError classifies transient vs terminal', () => {
  assert.equal(isTransientTransportError({ code: 'LLM_TIMEOUT' }), true);
  assert.equal(isTransientTransportError({ code: 'ECONNRESET' }), true);
  assert.equal(isTransientTransportError({ statusCode: 429 }), true);
  assert.equal(isTransientTransportError({ statusCode: 503 }), true);
  assert.equal(isTransientTransportError({ statusCode: 401 }), false);
  assert.equal(isTransientTransportError({ statusCode: 400 }), false);
  assert.equal(isTransientTransportError(new Error('component scores are required')), false);
});

test('postJsonWithTimeout retries on 503 then succeeds', async () => {
  let hits = 0;
  const server = http.createServer((req, res) => {
    hits += 1;
    let body = '';
    req.on('data', c => { body += c; });
    req.on('end', () => {
      if (hits < 3) {
        res.writeHead(503);
        res.end('busy');
      } else {
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ ok: true, hits }));
      }
    });
  });
  const port = await listen(server);
  try {
    const result = await postJsonWithTimeout(`http://127.0.0.1:${port}/`, { x: 1 }, {
      timeoutMs: 2000,
      retryBaseMs: 20
    });
    assert.equal(result.ok, true);
    assert.equal(result.hits, 3);
  } finally {
    server.close();
  }
});

test('postJsonWithTimeout fails fast on 401 (no retry)', async () => {
  let hits = 0;
  const server = http.createServer((req, res) => {
    hits += 1;
    let body = '';
    req.on('data', c => { body += c; });
    req.on('end', () => {
      res.writeHead(401);
      res.end('unauthorized');
    });
  });
  const port = await listen(server);
  try {
    await assert.rejects(
      () => postJsonWithTimeout(`http://127.0.0.1:${port}/`, { x: 1 }, { timeoutMs: 2000, retryBaseMs: 20 }),
      /HTTP 401/
    );
    assert.equal(hits, 1, '401 must not be retried');
  } finally {
    server.close();
  }
});

test('postJsonWithTimeout stops after maxRetries and rejects', async () => {
  let hits = 0;
  const server = http.createServer((req, res) => {
    hits += 1;
    let body = '';
    req.on('data', c => { body += c; });
    req.on('end', () => {
      res.writeHead(500);
      res.end('boom');
    });
  });
  const port = await listen(server);
  try {
    await assert.rejects(
      () => postJsonWithTimeout(`http://127.0.0.1:${port}/`, { x: 1 }, { timeoutMs: 2000, retryBaseMs: 10, maxRetries: 2 }),
      /HTTP 500/
    );
    assert.equal(hits, 3, '1 initial attempt + 2 retries');
  } finally {
    server.close();
  }
});
