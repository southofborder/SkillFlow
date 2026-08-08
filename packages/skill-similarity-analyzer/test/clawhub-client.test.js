const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');

const {
  fetchTopSkills,
  downloadSkillZip,
  buildZipFileName
} = require('../src/clawhub/client');

function makeTempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'clawhub-client-'));
}

function makeFetchStub(handler) {
  const calls = [];
  const fetchImpl = async url => {
    calls.push(String(url));
    return handler(String(url));
  };
  fetchImpl.calls = calls;
  return fetchImpl;
}

function jsonResponse(value, status = 200, headers = {}) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'content-type': 'application/json', ...headers }
  });
}

function startServer(handler) {
  return new Promise(resolve => {
    const server = http.createServer(handler);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({
        server,
        baseUrl: `http://127.0.0.1:${address.port}`
      });
    });
  });
}

test('fetchTopSkills follows cursor pages and truncates to requested limit', async () => {
  const fetchImpl = makeFetchStub(url => {
    const parsed = new URL(url);
    assert.equal(parsed.searchParams.get('sort'), 'downloads');
    assert.equal(parsed.searchParams.has('nonSuspiciousOnly'), false);
    if (!parsed.searchParams.get('cursor')) {
      return jsonResponse({
        items: [
          { slug: 'a', displayName: 'A', stats: { downloads: 10 }, latestVersion: { version: '1.0.0' } },
          { slug: 'b', displayName: 'B', stats: { downloads: 9 }, latestVersion: { version: '1.0.0' } }
        ],
        nextCursor: 'cursor-1'
      });
    }
    return jsonResponse({
      items: [
        { slug: 'c', displayName: 'C', stats: { downloads: 8 }, latestVersion: { version: '1.0.0' } },
        { slug: 'd', displayName: 'D', stats: { downloads: 7 }, latestVersion: { version: '1.0.0' } }
      ],
      nextCursor: 'cursor-2'
    });
  });

  const result = await fetchTopSkills({
    apiBase: 'https://example.test/api/v1',
    limit: 3,
    sort: 'downloads',
    fetchImpl
  });

  assert.equal(result.total, 3);
  assert.deepEqual(result.items.map(item => item.slug), ['a', 'b', 'c']);
  assert.equal(fetchImpl.calls.length, 2);
  assert.match(fetchImpl.calls[1], /cursor=cursor-1/);
});

test('fetchTopSkills can request nonSuspiciousOnly filtering', async () => {
  const fetchImpl = makeFetchStub(url => {
    const parsed = new URL(url);
    assert.equal(parsed.searchParams.get('nonSuspiciousOnly'), 'true');
    return jsonResponse({
      items: [{ slug: 'safe', stats: { downloads: 1 }, latestVersion: { version: '1' } }],
      nextCursor: null
    });
  });

  const result = await fetchTopSkills({
    apiBase: 'https://example.test/api/v1',
    limit: 1,
    nonSuspiciousOnly: true,
    fetchImpl
  });

  assert.equal(result.items[0].slug, 'safe');
});

test('downloadSkillZip retries transient failure and validates zip', async () => {
  const tempDir = makeTempDir();
  const zipPayload = Buffer.from([0x50, 0x4b, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00, ...Buffer.alloc(32)]);
  let calls = 0;
  const { server, baseUrl } = await startServer((req, res) => {
    calls += 1;
    assert.equal(req.url, '/download?slug=demo');
    if (calls === 1) {
      res.writeHead(503, { 'content-type': 'text/plain' });
      res.end('try again');
      return;
    }
    res.writeHead(200, { 'content-type': 'application/zip' });
    res.end(zipPayload);
  });

  try {
    const result = await downloadSkillZip({
      rank: 1,
      slug: 'demo',
      latest_version: '1.0.0'
    }, tempDir, {
      apiBase: baseUrl,
      retries: 1,
      timeoutMs: 5000
    });

    assert.equal(result.status, 'ok');
    assert.equal(calls, 2);
    assert.ok(fs.existsSync(path.join(tempDir, buildZipFileName({ rank: 1, slug: 'demo', latest_version: '1.0.0' }))));
  } finally {
    server.close();
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('downloadSkillZip skips existing valid zip', async () => {
  const tempDir = makeTempDir();
  try {
    const skill = { rank: 1, slug: 'demo', latest_version: '1.0.0' };
    fs.writeFileSync(path.join(tempDir, buildZipFileName(skill)), Buffer.from([0x50, 0x4b, 0x03, 0x04, ...Buffer.alloc(32)]));
    const result = await downloadSkillZip(skill, tempDir, {
      fetchImpl: async () => {
        throw new Error('fetch should not be called');
      }
    });
    assert.equal(result.status, 'skipped');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
