const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DEFAULT_API_BASE = 'https://clawhub.ai/api/v1';
const DEFAULT_PAGE_LIMIT = 100;
const DEFAULT_TIMEOUT_MS = 30000;
const DEFAULT_RETRIES = 4;
const DEFAULT_USER_AGENT = 'skillflow-skill-similarity/1.0';

async function fetchTopSkills(options = {}) {
  const limit = normalizeInteger(options.limit, 10000);
  const sort = options.sort || 'downloads';
  const pageLimit = normalizeInteger(options.pageLimit, DEFAULT_PAGE_LIMIT);
  const apiBase = normalizeApiBase(options.apiBase);
  const fetchImpl = options.fetchImpl || globalThis.fetch;
  const items = [];
  let cursor = options.cursor || '';
  let page = 0;

  if (typeof fetchImpl !== 'function') {
    throw new Error('fetch is not available; Node.js >=18 is required');
  }

  while (items.length < limit) {
    page += 1;
    const url = new URL(`${apiBase}/skills`);
    url.searchParams.set('sort', sort);
    url.searchParams.set('limit', String(Math.min(pageLimit, limit - items.length)));
    if (cursor) url.searchParams.set('cursor', cursor);
    if (options.nonSuspiciousOnly) url.searchParams.set('nonSuspiciousOnly', 'true');

    const payload = await fetchJsonWithRetry(url.toString(), {
      fetchImpl,
      timeoutMs: options.timeoutMs,
      retries: options.retries,
      userAgent: options.userAgent
    });

    const pageItems = Array.isArray(payload.items) ? payload.items : [];
    for (const item of pageItems) {
      if (items.length >= limit) break;
      items.push(normalizeSkillListItem(item, items.length + 1));
    }

    if (typeof options.onPage === 'function') {
      options.onPage({ page, fetched: pageItems.length, total: items.length, nextCursor: payload.nextCursor || '' });
    }

    if (!payload.nextCursor || pageItems.length === 0) break;
    cursor = payload.nextCursor;
  }

  return {
    generated_at: new Date().toISOString(),
    api_base: apiBase,
    sort,
    limit,
    non_suspicious_only: Boolean(options.nonSuspiciousOnly),
    total: items.length,
    items
  };
}

async function downloadSkillZip(skill, targetDir, options = {}) {
  const apiBase = normalizeApiBase(options.apiBase);
  const fetchImpl = options.fetchImpl || globalThis.fetch;
  if (typeof fetchImpl !== 'function') {
    throw new Error('fetch is not available; Node.js >=18 is required');
  }

  const slug = skill.slug || skill.skill?.slug;
  if (!slug) throw new Error('Cannot download skill without slug');

  fs.mkdirSync(targetDir, { recursive: true });
  const fileName = buildZipFileName(skill);
  const filePath = path.join(targetDir, fileName);

  if (options.skipExisting !== false && isValidZipFile(filePath)) {
    return {
      slug,
      status: 'skipped',
      reason: 'existing-valid-zip',
      zip_path: filePath,
      size: fs.statSync(filePath).size,
      sha256: sha256File(filePath)
    };
  }

  const url = new URL(`${apiBase}/download`);
  url.searchParams.set('slug', slug);
  const response = await fetchWithRetry(url.toString(), {
    fetchImpl,
    timeoutMs: options.timeoutMs,
    retries: options.retries,
    userAgent: options.userAgent,
    binary: true
  });

  const contentType = (response.headers.get('content-type') || '').toLowerCase();
  if (!contentType.includes('zip') && !contentType.includes('octet-stream')) {
    const text = await response.text();
    throw new Error(`Download did not return a zip payload: ${contentType || 'unknown'} ${text.slice(0, 160)}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  const tempPath = `${filePath}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(tempPath, buffer);

  if (!isValidZipFile(tempPath)) {
    fs.rmSync(tempPath, { force: true });
    throw new Error('Downloaded file is not a valid zip');
  }

  fs.renameSync(tempPath, filePath);
  return {
    slug,
    status: 'ok',
    zip_path: filePath,
    size: buffer.length,
    sha256: sha256Buffer(buffer),
    content_disposition: response.headers.get('content-disposition') || ''
  };
}

async function fetchJsonWithRetry(url, options = {}) {
  const response = await fetchWithRetry(url, options);
  return response.json();
}

async function fetchWithRetry(url, options = {}) {
  const fetchImpl = options.fetchImpl || globalThis.fetch;
  const retries = normalizeInteger(options.retries, DEFAULT_RETRIES);
  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetchWithTimeout(fetchImpl, url, {
        timeoutMs: normalizeInteger(options.timeoutMs, DEFAULT_TIMEOUT_MS),
        userAgent: options.userAgent || DEFAULT_USER_AGENT
      });

      if (response.ok) return response;

      if (![408, 425, 429, 500, 502, 503, 504].includes(response.status) || attempt === retries) {
        const body = options.binary ? '' : `: ${(await response.text()).slice(0, 300)}`;
        throw new Error(`HTTP ${response.status} ${response.statusText}${body}`);
      }

      const retryAfterMs = retryAfterToMs(response.headers.get('retry-after'));
      await delay(retryAfterMs || backoffMs(attempt));
    } catch (error) {
      lastError = error;
      if (attempt === retries) break;
      await delay(backoffMs(attempt));
    }
  }

  throw lastError;
}

async function fetchWithTimeout(fetchImpl, url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs || DEFAULT_TIMEOUT_MS);
  try {
    return await fetchImpl(url, {
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        'User-Agent': options.userAgent || DEFAULT_USER_AGENT
      }
    });
  } finally {
    clearTimeout(timer);
  }
}

function normalizeSkillListItem(item, rank) {
  const latest = item.latestVersion || item.latest_version || {};
  const stats = item.stats || {};
  return {
    rank,
    slug: item.slug,
    display_name: item.displayName || item.display_name || item.slug,
    summary: item.summary || '',
    stats,
    downloads: Number(stats.downloads || item.downloads || 0),
    stars: Number(stats.stars || item.stars || 0),
    installs_all_time: Number(stats.installsAllTime || item.installsAllTime || 0),
    installs_current: Number(stats.installsCurrent || item.installsCurrent || 0),
    created_at: item.createdAt || item.created_at || null,
    updated_at: item.updatedAt || item.updated_at || null,
    latest_version: latest.version || item.version || '',
    latest_version_created_at: latest.createdAt || null,
    clawhub_url: `https://clawhub.ai/skills/${item.slug}`
  };
}

function buildZipFileName(skill) {
  const rank = String(skill.rank || 0).padStart(5, '0');
  const slug = sanitizeFileName(skill.slug || 'skill');
  const version = sanitizeFileName(skill.latest_version || 'latest');
  return `${rank}_${slug}_${version}.zip`;
}

function isValidZipFile(filePath) {
  if (!fs.existsSync(filePath)) return false;
  const stat = fs.statSync(filePath);
  if (!stat.isFile() || stat.size < 22) return false;
  const fd = fs.openSync(filePath, 'r');
  try {
    const header = Buffer.alloc(4);
    fs.readSync(fd, header, 0, 4, 0);
    return header.equals(Buffer.from([0x50, 0x4b, 0x03, 0x04])) ||
      header.equals(Buffer.from([0x50, 0x4b, 0x05, 0x06])) ||
      header.equals(Buffer.from([0x50, 0x4b, 0x07, 0x08]));
  } finally {
    fs.closeSync(fd);
  }
}

function sha256File(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function sha256Buffer(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function retryAfterToMs(value) {
  if (!value) return 0;
  const seconds = Number(value);
  if (Number.isFinite(seconds)) return Math.max(0, seconds * 1000);
  const date = Date.parse(value);
  return Number.isFinite(date) ? Math.max(0, date - Date.now()) : 0;
}

function backoffMs(attempt) {
  return Math.min(30000, 1000 * (2 ** attempt));
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function normalizeApiBase(value) {
  return String(value || DEFAULT_API_BASE).replace(/\/+$/, '');
}

function normalizeInteger(value, fallback) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : fallback;
}

function sanitizeFileName(value) {
  const safe = String(value || '')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/[. ]+$/g, '')
    .slice(0, 140);
  return safe || 'skill';
}

module.exports = {
  DEFAULT_API_BASE,
  DEFAULT_PAGE_LIMIT,
  fetchTopSkills,
  downloadSkillZip,
  fetchWithRetry,
  buildZipFileName,
  isValidZipFile,
  normalizeSkillListItem
};

