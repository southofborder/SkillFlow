'use strict';

const fs = require('fs');
const path = require('path');

let cachedResult = null;

function loadProjectEnv(options = {}) {
  if (cachedResult && !options.forceReload) {
    return cachedResult;
  }

  const startDirs = uniqueDirs([
    options.startDir,
    process.cwd(),
    options.entryFile ? path.dirname(path.resolve(options.entryFile)) : '',
    __dirname
  ]);

  const envPath = findNearestEnv(startDirs);
  const result = {
    loaded: false,
    envPath: envPath || '',
    values: {}
  };

  if (!envPath) {
    cachedResult = result;
    return result;
  }

  const parsed = parseEnvFile(fs.readFileSync(envPath, 'utf-8'));
  for (const [key, value] of Object.entries(parsed)) {
    if (process.env[key] === undefined) {
      process.env[key] = value;
      result.values[key] = value;
    }
  }

  result.loaded = true;
  cachedResult = result;
  return result;
}

function findNearestEnv(startDirs) {
  const visited = new Set();
  for (const dir of startDirs) {
    let current = path.resolve(dir);
    while (!visited.has(current)) {
      visited.add(current);
      const candidate = path.join(current, '.env');
      if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
        return candidate;
      }
      const parent = path.dirname(current);
      if (parent === current) break;
      current = parent;
    }
  }
  return '';
}

function parseEnvFile(content) {
  const values = {};
  const lines = String(content || '').split(/\r?\n/);
  for (let index = 0; index < lines.length; index++) {
    const lineNo = index + 1;
    const rawLine = lines[index];
    const trimmed = rawLine.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    const match = rawLine.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!match) {
      throw new Error(`Malformed .env line ${lineNo}: ${rawLine}`);
    }

    const key = match[1];
    let value = match[2];
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    } else {
      const commentIndex = value.indexOf(' #');
      if (commentIndex >= 0) value = value.slice(0, commentIndex).trimEnd();
    }

    value = value
      .replace(/\\n/g, '\n')
      .replace(/\\r/g, '\r')
      .replace(/\\t/g, '\t')
      .replace(/\\"/g, '"')
      .replace(/\\'/g, "'");

    values[key] = value;
  }
  return values;
}

function uniqueDirs(values) {
  const seen = new Set();
  const dirs = [];
  for (const value of values) {
    if (!value) continue;
    const resolved = path.resolve(value);
    if (seen.has(resolved)) continue;
    seen.add(resolved);
    dirs.push(resolved);
  }
  return dirs;
}

module.exports = {
  loadProjectEnv,
  findNearestEnv,
  parseEnvFile
};
