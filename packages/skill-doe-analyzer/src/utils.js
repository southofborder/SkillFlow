'use strict';

/**
 * Shared numeric/label/serialization helpers for the DOE analyzer.
 *
 * These were previously copy-pasted across exposure-scorer, doe-analyzer,
 * necessity-baseline, necessity-text-utils, group-baseline, llm-judge,
 * evidence-pack, and path-report. Consolidated here so scoring math stays
 * consistent in one place.
 *
 * Note: exposure-scorer keeps its own categoryFromLabel because it falls back
 * to 'generic_data' rather than '' for sensitivity lookups.
 */

/** Round to 3 decimals; non-finite input collapses to 0. */
function round3(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.round(n * 1000) / 1000;
}

/** Clamp to [0, 1]; non-finite input collapses to 0. */
function clamp(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

/** First dot-segment of a label, e.g. "pii.email" -> "pii". */
function categoryFromLabel(label = '') {
  return String(label || '').split('.')[0] || '';
}

/** Second dot-segment of a label, e.g. "pii.email" -> "email". */
function subtypeFromLabel(label = '') {
  return String(label || '').split('.')[1] || '';
}

/** Deduplicate an array, dropping falsy values, preserving first-seen order. */
function uniqueValues(values = []) {
  return Array.from(new Set((values || []).filter(Boolean)));
}

/** Recursively sort object keys so equivalent objects serialize identically. */
function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (!value || typeof value !== 'object') return value;
  return Object.keys(value).sort().reduce((acc, key) => {
    acc[key] = sortKeys(value[key]);
    return acc;
  }, {});
}

/** Deterministic JSON string (stable key order) for hashing/caching. */
function stableStringify(value) {
  return JSON.stringify(sortKeys(value));
}

module.exports = {
  round3,
  clamp,
  categoryFromLabel,
  subtypeFromLabel,
  uniqueValues,
  sortKeys,
  stableStringify
};
