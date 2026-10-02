'use strict';

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

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round6(value) {
  return Math.round(Number(value || 0) * 1_000_000) / 1_000_000;
}

module.exports = { normalizeSimilarityResult };
