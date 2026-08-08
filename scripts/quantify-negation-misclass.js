#!/usr/bin/env node
// Quantify how many `negated_disclaimer` nodes across the first-30 corpus are
// actually PROHIBITIVE CONSTRAINTS (a guard on a real action / an ordering
// dependency) that were wrongly dropped to context, vs genuine disclaimers
// ("skill does NOT do X") that are correctly context.
//
// Heuristic buckets (for triage only — the real decision goes to the LLM gate):
//   ordering_constraint : negation + temporal connective (before/until/after/without X-ing)
//                         referencing a concrete action  => implies an ordering edge
//   prohibitive_guard   : "never/do not <action>" on a runtime action (overwrite, log,
//                         delete, send, commit...) => guard on that action
//   conditional_policy  : negation + unless/only if/except => conditional data/act policy
//   pure_disclaimer     : "does not <capability>" describing what the skill can't/won't do
//   other               : uncategorized

const fs = require('fs');
const path = require('path');

const dir = process.argv[2] || 'results/review-30/fcg/skills';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));

const TEMPORAL = /\b(before|after|until|first|then|prior to|once)\b/i;
const WITHOUT_ING = /\bwithout\s+(?:\w+ing|a |an |the |any )/i;
const UNLESS = /\b(unless|only if|except|provided that|as long as)\b/i;
const ACTION_VERB = /\b(overwrite|delete|remove|log|send|post|upload|commit|push|install|run|execute|write|store|persist|share|expose|modify|edit|add|create|publish|transmit|export)\b/i;
const CAPABILITY_NEG = /\b(does not|doesn't|do not|don't|will not|won't|cannot|can't)\b/i;

function bucket(text) {
  const t = String(text || '').trim();
  if (!t) return 'other';
  const hasAction = ACTION_VERB.test(t);
  // ordering: temporal connective OR "without <do>ing" tying two actions
  if ((TEMPORAL.test(t) || WITHOUT_ING.test(t)) && hasAction) return 'ordering_constraint';
  if (UNLESS.test(t) && hasAction) return 'conditional_policy';
  // prohibitive guard: never/don't + concrete runtime action
  if (/\b(never|do not|don't|must not|should not|shouldn't|no longer)\b/i.test(t) && hasAction) return 'prohibitive_guard';
  // pure disclaimer: "does not <verb>" describing capability, no ordering/condition
  if (CAPABILITY_NEG.test(t)) return 'pure_disclaimer';
  return 'other';
}

const counts = {};
const examples = {};
let total = 0;

for (const f of files) {
  let d;
  try { d = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); } catch { continue; }
  for (const n of (d.nodes || [])) {
    const ev = n.formal_semantics?.evidence || {};
    if (ev.role !== 'negated_disclaimer') continue;
    total++;
    const text = n.instructionText || ev.text || '';
    const b = bucket(text);
    counts[b] = (counts[b] || 0) + 1;
    if (!examples[b]) examples[b] = [];
    if (examples[b].length < 4) examples[b].push(text.slice(0, 100));
  }
}

console.log(`=== negated_disclaimer nodes across ${files.length} skills: ${total} total ===\n`);
const order = ['ordering_constraint', 'prohibitive_guard', 'conditional_policy', 'pure_disclaimer', 'other'];
for (const b of order) {
  const c = counts[b] || 0;
  const pct = total ? Math.round(100 * c / total) : 0;
  console.log(`${b.padEnd(22)} ${String(c).padStart(4)}  (${pct}%)`);
  for (const ex of (examples[b] || [])) console.log(`      • ${JSON.stringify(ex)}`);
  console.log('');
}
const misclassified = (counts.ordering_constraint || 0) + (counts.prohibitive_guard || 0) + (counts.conditional_policy || 0);
console.log(`=== 疑似被误丢的约束(非纯免责): ${misclassified}/${total} (${total ? Math.round(100 * misclassified / total) : 0}%) ===`);
