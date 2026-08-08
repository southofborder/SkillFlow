'use strict';
// One-off probe: does the configured LLM endpoint honor prompt caching?
// Sends two requests sharing a large (>1024 token) stable prefix and reports
// usage.prompt_tokens_details.cached_tokens. Uses the real endpoint + key.
const fs = require('fs');
const path = require('path');

// load .env manually (no dotenv dependency assumed)
try {
  const env = fs.readFileSync(path.join(__dirname, '..', '.env'), 'utf8');
  for (const line of env.split(/\r?\n/)) {
    const m = line.match(/^([A-Z_]+)=(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
} catch (_) {}

const ENDPOINT = process.env.LLM_ENDPOINT || 'https://api.openai.com/v1/chat/completions';
const MODEL = process.env.LLM_MODEL || 'gpt-5.5';
const KEY = process.env.LLM_API_KEY;

// Build a large stable prefix (~2k+ tokens) as the system message, mimicking how
// shared_context/task_memory would sit as a cacheable prefix.
const bigPrefix = Array.from({ length: 400 }, (_, i) =>
  `Task memory node ${i}: this is a stable skill-level task declaration entry used as a shared grounding context; it does not change across batches within a skill.`
).join('\n');

async function call(userSuffix) {
  const body = {
    model: MODEL,
    temperature: 0,
    messages: [
      { role: 'system', content: bigPrefix },
      { role: 'user', content: userSuffix }
    ]
  };
  const t0 = Date.now();
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${KEY}` },
    body: JSON.stringify(body)
  });
  const json = await res.json();
  const ms = Date.now() - t0;
  return { json, ms, status: res.status };
}

(async () => {
  console.log('endpoint:', ENDPOINT);
  console.log('model:', MODEL);
  console.log('prefix chars:', bigPrefix.length, '\n');

  const r1 = await call('First request. Reply with the single word OK.');
  console.log('--- request 1 ---', 'status', r1.status, r1.ms + 'ms');
  console.log('usage:', JSON.stringify(r1.json.usage || r1.json.error || r1.json, null, 1));

  // brief pause so the cache can register
  await new Promise(r => setTimeout(r, 1500));

  const r2 = await call('Second request. Reply with the single word OK.');
  console.log('\n--- request 2 (same prefix) ---', 'status', r2.status, r2.ms + 'ms');
  console.log('usage:', JSON.stringify(r2.json.usage || r2.json.error || r2.json, null, 1));

  const cached = r2.json?.usage?.prompt_tokens_details?.cached_tokens
    ?? r2.json?.usage?.cached_tokens
    ?? r2.json?.usage?.prompt_cache_hit_tokens;
  console.log('\n=== cached_tokens on request 2:', cached, '===');
})().catch(e => { console.error('probe failed:', e.message); process.exit(1); });
