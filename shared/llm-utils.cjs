'use strict';

const http = require('http');
const https = require('https');
const http2 = require('http2');

function normalizeAssistantContent(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .map(part => {
        if (typeof part === 'string') return part;
        if (part && typeof part.text === 'string') return part.text;
        if (part && typeof part.content === 'string') return part.content;
        return '';
      })
      .join('\n');
  }
  if (content && typeof content === 'object') {
    return JSON.stringify(content);
  }
  return '';
}

function parseLooseJson(raw) {
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) return raw;
  const text = normalizeAssistantContent(raw).trim();
  if (!text) return null;

  const candidates = [text];
  const fenced = text.match(/```json\s*([\s\S]*?)```/i);
  if (fenced) candidates.push(fenced[1].trim());
  const objectLike = text.match(/\{[\s\S]*\}/);
  if (objectLike) candidates.push(objectLike[0]);

  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch {
      // try next
    }
  }
  return null;
}

function normalizeBoolean(value, fallback = false) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') {
    if (value === 1) return true;
    if (value === 0) return false;
  }
  const text = String(value || '').trim().toLowerCase();
  if (['true', 'yes', 'y', '1', 'agree', 'agrees'].includes(text)) return true;
  if (['false', 'no', 'n', '0', 'disagree', 'disagrees'].includes(text)) return false;
  return fallback;
}

function normalizeScaledNumber(value, options = {}) {
  const fallback = options.fallback ?? 0;
  const min = options.min ?? 0;
  const max = options.max ?? 1;
  const map = options.map || {};

  if (typeof value === 'number' && Number.isFinite(value)) {
    return clamp(value, min, max);
  }

  const text = String(value || '').trim().toLowerCase();
  if (!text) return fallback;

  if (Object.prototype.hasOwnProperty.call(map, text)) {
    return clamp(Number(map[text]), min, max);
  }

  const numeric = Number(text);
  if (Number.isFinite(numeric)) {
    return clamp(numeric, min, max);
  }

  return fallback;
}

function normalizeSeverity(value) {
  const text = String(value || '').trim().toLowerCase();
  if (!text) return '';
  if (['critical', 'crit', 'severe'].includes(text)) return 'critical';
  if (['high', 'major'].includes(text)) return 'high';
  if (['medium', 'med', 'moderate'].includes(text)) return 'medium';
  if (['low', 'minor'].includes(text)) return 'low';
  return '';
}

function normalizeSimilarityResult(raw) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null;

  return {
    similarity: round6(normalizeScaledNumber(
      parsed.similarity ?? parsed.score ?? parsed.similarity_score,
      {
        fallback: 0,
        map: {
          identical: 1,
          very_high: 0.9,
          'very high': 0.9,
          high: 0.8,
          medium: 0.5,
          low: 0.2,
          none: 0
        }
      }
    )),
    reason: String(parsed.reason || parsed.explanation || '').trim(),
    has_contradiction: normalizeBoolean(parsed.has_contradiction, false),
    contradiction_reason: String(parsed.contradiction_reason || '').trim()
  };
}

function normalizeValidationResult(raw) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null;

  return {
    is_compatible: normalizeBoolean(parsed.is_compatible, false),
    confidence: normalizeScaledNumber(parsed.confidence, {
      fallback: 0.5,
      map: { high: 0.85, medium: 0.6, low: 0.3 }
    }),
    reason: String(parsed.reason || '').trim() || 'LLM semantic validation',
    data_flow_description: String(parsed.data_flow_description || '').trim() || 'Data flows from source to target'
  };
}

function normalizeReviewResult(raw) {
  const parsed = parseLooseJson(raw);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null;

  return {
    agrees: normalizeBoolean(parsed.agrees, false),
    confidence: normalizeScaledNumber(parsed.confidence, {
      fallback: 0,
      map: { high: 0.85, medium: 0.6, low: 0.3 }
    }),
    reason: String(parsed.reason || '').trim(),
    suggested_severity: normalizeSeverity(parsed.suggested_severity)
  };
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round6(value) {
  return Math.round(Number(value || 0) * 1_000_000) / 1_000_000;
}

// Single HTTP attempt. Rejected errors carry .code (LLM_TIMEOUT / network) or
// .statusCode (HTTP status) plus .retryAfterMs when the server sent Retry-After,
// so the retry wrapper can decide what is transient.
function postJsonOnce(url, payload, options = {}) {
  const timeoutMs = normalizeTimeoutMs(options.timeoutMs || options.timeout || 30000);
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  const body = JSON.stringify(payload || {});
  const parsedUrl = new URL(url);
  const client = parsedUrl.protocol === 'http:' ? http : https;
  const resolvedIp = String(options.resolvedIp || process.env.LLM_ENDPOINT_RESOLVED_IP || '').trim();
  const forcedLookup = resolvedIp
    ? (_hostname, lookupOptions, callback) => {
      const family = resolvedIp.includes(':') ? 6 : 4;
      if (lookupOptions?.all) {
        callback(null, [{ address: resolvedIp, family }]);
        return;
      }
      callback(null, resolvedIp, family);
    }
    : undefined;
  const useHttp2 = parsedUrl.protocol === 'https:' &&
    (options.http2 === true || isTruthy(process.env.LLM_HTTP2));

  if (useHttp2) {
    return postJsonHttp2Once(parsedUrl, body, headers, timeoutMs, forcedLookup);
  }

  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      fn(value);
    };
    const timer = setTimeout(() => {
      const error = new Error(`HTTP request timed out after ${timeoutMs}ms`);
      error.code = 'LLM_TIMEOUT';
      request.destroy(error);
      finish(reject, error);
    }, timeoutMs);

    const request = client.request({
      protocol: parsedUrl.protocol,
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || undefined,
      path: `${parsedUrl.pathname}${parsedUrl.search}`,
      method: 'POST',
      lookup: forcedLookup,
      headers: {
        ...headers,
        'Content-Length': Buffer.byteLength(body)
      },
      timeout: timeoutMs
    }, response => {
      const chunks = [];
      response.on('data', chunk => chunks.push(chunk));
      response.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf-8');
        if (response.statusCode < 200 || response.statusCode >= 300) {
          finish(reject, httpStatusError(response.statusCode, text, response.headers));
          return;
        }
        try {
          finish(resolve, JSON.parse(text));
        } catch (error) {
          finish(reject, new Error(`Invalid JSON response: ${error.message}`));
        }
      });
    });

    request.on('timeout', () => {
      const error = new Error(`HTTP request timed out after ${timeoutMs}ms`);
      error.code = 'LLM_TIMEOUT';
      request.destroy(error);
      finish(reject, error);
    });
    request.on('error', error => finish(reject, error));
    request.write(body);
    request.end();
  });
}

function postJsonHttp2Once(parsedUrl, body, headers, timeoutMs, lookup) {
  return new Promise((resolve, reject) => {
    let settled = false;
    let request = null;
    let responseHeadersAll = {};
    const client = http2.connect(`${parsedUrl.protocol}//${parsedUrl.host}`, {
      lookup,
      servername: parsedUrl.hostname
    });
    const timer = setTimeout(() => {
      const error = new Error(`HTTP request timed out after ${timeoutMs}ms`);
      error.code = 'LLM_TIMEOUT';
      if (request) request.close();
      client.close();
      finish(reject, error);
    }, timeoutMs);

    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      try { client.close(); } catch {}
      fn(value);
    };

    client.on('error', error => finish(reject, error));
    request = client.request({
      ':method': 'POST',
      ':path': `${parsedUrl.pathname}${parsedUrl.search}`,
      ...headers,
      'content-length': String(Buffer.byteLength(body))
    });

    const chunks = [];
    let statusCode = 0;
    request.setEncoding('utf8');
    request.setTimeout(timeoutMs, () => {
      const error = new Error(`HTTP request timed out after ${timeoutMs}ms`);
      error.code = 'LLM_TIMEOUT';
      request.close();
      finish(reject, error);
    });
    request.on('response', responseHeaders => {
      statusCode = Number(responseHeaders[':status'] || 0);
      responseHeadersAll = responseHeaders || {};
    });
    request.on('data', chunk => chunks.push(Buffer.from(chunk, 'utf8')));
    request.on('end', () => {
      const text = Buffer.concat(chunks).toString('utf-8');
      if (statusCode < 200 || statusCode >= 300) {
        finish(reject, httpStatusError(statusCode, text, responseHeadersAll));
        return;
      }
      try {
        finish(resolve, JSON.parse(text));
      } catch (error) {
        finish(reject, new Error(`Invalid JSON response: ${error.message}`));
      }
    });
    request.on('error', error => finish(reject, error));
    request.end(body);
  });
}

function httpStatusError(statusCode, text, headers = {}) {
  const error = new Error(`HTTP ${statusCode}: ${text}`);
  error.statusCode = statusCode;
  const retryAfter = headers && (headers['retry-after'] || headers['Retry-After']);
  const retryAfterMs = parseRetryAfterMs(retryAfter);
  if (retryAfterMs !== null) error.retryAfterMs = retryAfterMs;
  return error;
}

// Retry-After is either delta-seconds or an HTTP date. Returns ms or null.
function parseRetryAfterMs(value) {
  if (value === undefined || value === null || value === '') return null;
  const seconds = Number(value);
  if (Number.isFinite(seconds) && seconds >= 0) return Math.round(seconds * 1000);
  const dateMs = Date.parse(String(value));
  if (Number.isFinite(dateMs)) {
    const delta = dateMs - Date.now();
    return delta > 0 ? delta : 0;
  }
  return null;
}

function isTransientTransportError(error) {
  if (!error) return false;
  if (error.code === 'LLM_TIMEOUT') return true;
  const code = String(error.code || '');
  if (['ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED', 'EAI_AGAIN', 'EPIPE', 'ENOTFOUND', 'ERR_HTTP2_STREAM_ERROR'].includes(code)) {
    return true;
  }
  const status = Number(error.statusCode || 0);
  if (status === 429) return true;
  if (status >= 500 && status <= 599) return true;
  return false;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function resolveRetryConfig(options = {}) {
  const maxRetries = normalizeNonNegativeInt(
    options.maxRetries ?? process.env.LLM_MAX_RETRIES,
    2
  );
  const baseMs = normalizePositiveIntOr(
    options.retryBaseMs ?? process.env.LLM_RETRY_BASE_MS,
    500
  );
  const maxBackoffMs = normalizePositiveIntOr(
    options.retryMaxBackoffMs ?? process.env.LLM_RETRY_MAX_BACKOFF_MS,
    8000
  );
  return { maxRetries, baseMs, maxBackoffMs };
}

// Bounded retry with exponential backoff + jitter for transient transport
// failures (timeout, network reset/DNS, HTTP 429, HTTP 5xx). Honors Retry-After
// when present. Auth/4xx (except 429) and schema errors are not retried — they
// reject immediately so callers fail fast on real defects.
async function postJsonWithTimeout(url, payload, options = {}) {
  const { maxRetries, baseMs, maxBackoffMs } = resolveRetryConfig(options);
  let attempt = 0;
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      return await postJsonOnce(url, payload, options);
    } catch (error) {
      if (attempt >= maxRetries || !isTransientTransportError(error)) throw error;
      const backoff = Math.min(maxBackoffMs, baseMs * Math.pow(2, attempt));
      const jitter = Math.round(backoff * 0.25 * Math.random());
      const waitMs = error.retryAfterMs !== undefined
        ? Math.min(maxBackoffMs, error.retryAfterMs) + jitter
        : backoff + jitter;
      attempt += 1;
      await sleep(waitMs);
    }
  }
}

function normalizeNonNegativeInt(value, fallback) {
  const n = Number(value);
  return Number.isInteger(n) && n >= 0 ? n : fallback;
}

function normalizePositiveIntOr(value, fallback) {
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? n : fallback;
}

function normalizeTimeoutMs(value) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : 30000;
}

function isTruthy(value) {
  return ['1', 'true', 'yes', 'on'].includes(String(value || '').trim().toLowerCase());
}

module.exports = {
  normalizeAssistantContent,
  parseLooseJson,
  normalizeBoolean,
  normalizeScaledNumber,
  normalizeSeverity,
  normalizeSimilarityResult,
  normalizeValidationResult,
  normalizeReviewResult,
  postJsonWithTimeout,
  parseRetryAfterMs,
  isTransientTransportError
};
