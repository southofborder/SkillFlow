'use strict';

/**
 * Tiered, conditional evidence-pack sizing for the DOE LLM judge (flow-centric pack).
 *
 * Accuracy contract:
 *   - Tier 0 (default): packs at or below the context ceiling are returned
 *     untouched (deep-equal to the input). The judge sees full evidence, so
 *     verdicts are identical to not having this module at all.
 *   - Tier 2 (last resort): only packs that EXCEED the ceiling are reduced.
 *     We first apply lossless reduction (whitespace cleanup), then window the
 *     interior flow nodes while always retaining the source and sink endpoints,
 *     then clamp long free-text. The unit is flagged so downstream marks it for
 *     review.
 *
 * The flow-centric pack is small by construction (label + sink_boundary + a
 * source-to-sink flow[] of {node_name, role, action, transform?}), so trimming
 * almost never fires. Nothing here changes scoring math, gating, or which units
 * are judged.
 */

const DEFAULT_LIMITS = {
  // High ceiling on purpose: trimming should almost never fire. Packs below
  // this are passed through verbatim.
  maxPackChars: 100000,
  // How many flow nodes at each end to keep verbatim when windowing is required.
  // The sink node (last) and source node (first) are always within the window.
  pathNodeWindow: 4,
  // Cap for long free-text fields (only applied during Tier-2 trimming).
  maxTextChars: 2000
};

// Free-text fields safe to clamp during Tier-2 trimming. Structural fields
// (names, roles, transform types) are never clamped.
const TEXT_FIELDS = new Set([
  'action',
  'instructionText',
  'description',
  'preview',
  'readme_preview',
  'reasoning_summary',
  'reason',
  'text'
]);

function resolveBudgetLimits(options = {}) {
  return {
    maxPackChars: positiveInt(options.evidenceMaxPackChars, DEFAULT_LIMITS.maxPackChars),
    pathNodeWindow: nonNegativeInt(options.evidencePathNodeWindow, DEFAULT_LIMITS.pathNodeWindow),
    maxTextChars: positiveInt(options.evidenceMaxTextChars, DEFAULT_LIMITS.maxTextChars)
  };
}

function estimatePackChars(pack) {
  try {
    return JSON.stringify(pack || {}).length;
  } catch (_) {
    return 0;
  }
}

/**
 * Tier-2 entry point. Returns the pack unchanged when it fits the ceiling;
 * otherwise returns a reduced clone with `_budgeted` metadata.
 */
function budgetPackIfNeeded(pack, options = {}) {
  const limits = resolveBudgetLimits(options);
  if (!pack || typeof pack !== 'object') return pack;
  if (estimatePackChars(pack) <= limits.maxPackChars) return pack; // Tier 0: untouched.

  const notes = [];
  const NOTE_RESERVE = 1200;
  const ceiling = Math.max(1, limits.maxPackChars - NOTE_RESERVE);

  // Step 1: lossless reduction (no information removed, only normalized).
  let working = losslessReduce(pack);
  if (estimatePackChars(working) <= ceiling) {
    notes.push('lossless_reduction');
    return finalizeBudgetedPack(pack, working, notes);
  }

  // Step 2: window interior flow nodes; always keep source + sink endpoints.
  const windowResult = windowFlowPathNodes(working, limits);
  working = windowResult.pack;
  if (windowResult.omittedCount > 0) {
    notes.push(`flow_node_window(kept_head_tail=${limits.pathNodeWindow},omitted=${windowResult.omittedCount})`);
  }
  if (estimatePackChars(working) <= ceiling) {
    return finalizeBudgetedPack(pack, working, notes);
  }

  // Step 3: clamp long free-text (action strings) in retained nodes.
  working = clampTextAndArrays(working, limits);
  notes.push('text_clamp');
  if (estimatePackChars(working) <= ceiling) {
    return finalizeBudgetedPack(pack, working, notes);
  }

  // Step 4: hard ceiling guarantee. Drop interior flow nodes (never the source
  // or sink endpoints) until the pack fits, then rebuild the evidence index.
  const hardDropped = enforceHardCeiling(working, ceiling);
  if (hardDropped > 0) notes.push(`hard_ceiling_drop(nodes=${hardDropped})`);

  return finalizeBudgetedPack(pack, working, notes);
}

function finalizeBudgetedPack(originalPack, reducedPack, notes) {
  const result = reducedPack;
  result._budgeted = true;
  result._budget_notes = notes;
  result._original_chars = estimatePackChars(originalPack);
  result._budgeted_chars = estimatePackChars(reducedPack);
  result.budget_note = {
    budgeted: true,
    reductions: notes,
    original_chars: result._original_chars,
    budgeted_chars: result._budgeted_chars,
    note: 'Evidence was reduced to fit model context. The source and sink nodes are retained; some interior flow nodes may be summarized or omitted. Treat omitted detail as unknown rather than absent.'
  };
  return result;
}

/** Deep clone via structured JSON (packs are plain JSON-serializable data). */
function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

/**
 * Lossless reduction: collapse runs of whitespace in strings. No semantic
 * content is removed.
 */
function losslessReduce(pack) {
  const clone = cloneJson(pack);
  normalizeWhitespaceDeep(clone);
  return clone;
}

function normalizeWhitespaceDeep(value) {
  if (Array.isArray(value)) {
    for (const item of value) normalizeWhitespaceDeep(item);
    return;
  }
  if (value && typeof value === 'object') {
    for (const key of Object.keys(value)) {
      const v = value[key];
      if (typeof v === 'string') {
        value[key] = v.replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/[ \t]{2,}/g, ' ');
      } else {
        normalizeWhitespaceDeep(v);
      }
    }
  }
}

/**
 * Keep the first/last `window` flow nodes verbatim; replace interior nodes with
 * compact stubs that retain node_name and role (so the path shape and citations
 * stay valid). The source (index 0) and sink (last) are always within the window.
 */
function windowFlowPathNodes(pack, limits) {
  const flow = pack.flow || [];
  if (flow.length <= limits.pathNodeWindow * 2 + 1) {
    return { pack, omittedCount: 0 };
  }
  const keep = new Set();
  for (let i = 0; i < limits.pathNodeWindow; i += 1) keep.add(i);
  for (let i = flow.length - limits.pathNodeWindow; i < flow.length; i += 1) keep.add(i);
  // Always keep endpoints: source / sink / source_sink (the latter is both).
  flow.forEach((node, i) => { if (isEndpointRole(node.role)) keep.add(i); });

  let omittedCount = 0;
  pack.flow = flow.map((node, i) => {
    if (keep.has(i)) return node;
    omittedCount += 1;
    return { node_name: node.node_name || '', role: node.role || 'transform', summarized: true };
  });
  return { pack, omittedCount };
}

function clampTextAndArrays(pack, limits) {
  clampDeep(pack, limits);
  return pack;
}

function clampDeep(value, limits) {
  if (Array.isArray(value)) {
    for (const item of value) clampDeep(item, limits);
    return;
  }
  if (value && typeof value === 'object') {
    for (const key of Object.keys(value)) {
      const v = value[key];
      if (typeof v === 'string' && TEXT_FIELDS.has(key) && v.length > limits.maxTextChars) {
        value[key] = headTailWindow(v, limits.maxTextChars);
      } else {
        clampDeep(v, limits);
      }
    }
  }
}

/** Keep head and tail of a long string with an explicit elision marker. */
function headTailWindow(text, max) {
  if (text.length <= max) return text;
  const half = Math.floor((max - 24) / 2);
  if (half <= 0) return `${text.slice(0, max)}…`;
  return `${text.slice(0, half)} …[trimmed ${text.length - half * 2} chars]… ${text.slice(text.length - half)}`;
}

/**
 * Hard ceiling guarantee: drop interior flow nodes (never source/sink) until the
 * pack fits. Returns nodes dropped.
 */
function enforceHardCeiling(pack, maxChars) {
  if (estimatePackChars(pack) <= maxChars) return 0;
  const flow = pack.flow || [];
  // Indices eligible to drop: everything that is not source/sink endpoint.
  const droppable = [];
  flow.forEach((node, i) => {
    const isEndpoint = isEndpointRole(node.role) || i === 0 || i === flow.length - 1;
    if (!isEndpoint) droppable.push(i);
  });
  let dropped = 0;
  // Drop from the middle outward (interior detail is lowest value).
  droppable.sort((a, b) => Math.abs(b - flow.length / 2) - Math.abs(a - flow.length / 2));
  const toDrop = new Set();
  for (const idx of droppable) {
    if (estimatePackChars({ ...pack, flow: flow.filter((_, i) => !toDrop.has(i)) }) <= maxChars) break;
    toDrop.add(idx);
    dropped += 1;
  }
  if (dropped > 0) {
    pack.flow = flow.filter((_, i) => !toDrop.has(i));
    pack._flow_nodes_dropped = dropped;
  }
  return dropped;
}

// source / sink / source_sink are flow endpoints — never windowed or dropped.
function isEndpointRole(role) {
  return role === 'source' || role === 'sink' || role === 'source_sink';
}

function positiveInt(value, fallback) {
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? n : fallback;
}

function nonNegativeInt(value, fallback) {
  const n = Number(value);
  return Number.isInteger(n) && n >= 0 ? n : fallback;
}

module.exports = {
  budgetPackIfNeeded,
  losslessReduce,
  estimatePackChars
};
