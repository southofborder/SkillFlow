'use strict';
/**
 * Semantic review of FCG outputs: flag "unreasonable / incomplete" nodes and
 * paths after the list-block + conditions + sequence-edge changes.
 *
 * Reads every *-sfg.json under a skills dir and reports, per skill and in
 * aggregate:
 *   - node/edge/observation/label_flow counts
 *   - fragmented bullet nodes (multi-line list items that should have folded)
 *   - disclaimer bullets mis-extracted as active instructions
 *   - dangling nodes (no in/out edge) excluding the implicit user-query source
 *   - empty-action doc nodes (no instructionText / no targets)
 *   - non-instruction doc residue (pure description nodes carrying observations)
 *   - broken paths (edge endpoints missing from node set)
 *
 * Usage: node scripts/review-fcg-semantics.js <skillsDir> [--json <out>]
 */
const fs = require('fs');
const path = require('path');

const skillsDir = process.argv[2];
if (!skillsDir) {
  console.error('usage: node scripts/review-fcg-semantics.js <skillsDir> [--json <out>]');
  process.exit(1);
}
let jsonOut = '';
for (let i = 3; i < process.argv.length; i++) {
  if (process.argv[i] === '--json' && i + 1 < process.argv.length) jsonOut = process.argv[++i];
}

const files = fs.readdirSync(skillsDir)
  .filter(n => /-fcg\.json$/.test(n))
  .sort((a, b) => a.localeCompare(b));

const UNORDERED_MARKER = /^\s*[-*+]\s+/;
const ORDERED_MARKER = /^\s*\d+[.)]\s+/;

function isListLine(s) {
  return UNORDERED_MARKER.test(s) || ORDERED_MARKER.test(s);
}

function nodeText(n) {
  return String(n.instructionText || n.source_context?.source_line || n.description || '');
}

function reviewSkill(fcg, fileName) {
  const nodes = fcg.nodes || [];
  const edges = fcg.edges || [];
  const sp = fcg.security_profile || {};
  const observations = sp.observations || [];
  const nodeIds = new Set(nodes.map(n => n.id));

  // in/out degree keyed by node id (edges reference ids)
  const deg = new Map();
  const bump = (k, dir) => {
    if (!deg.has(k)) deg.set(k, { in: 0, out: 0 });
    deg.get(k)[dir]++;
  };
  let brokenEdges = 0;
  for (const e of edges) {
    const s = e.source, t = e.target;
    if (!nodeIds.has(s) || !nodeIds.has(t)) brokenEdges++;
    bump(s, 'out');
    bump(t, 'in');
  }

  const findings = {
    fragmented_bullets: [],   // node whose text still spans an un-folded multi-line bullet
    disclaimer_as_action: [], // negated/disclaimer text extracted as an active op
    dangling: [],             // no in and no out edge
    empty_action: [],         // active op but no instructionText and no targets
    description_with_obs: []  // pure description/context node that still carries an observation
  };

  const obsNodeIds = new Set(observations.map(o => o.node_id));

  for (const n of nodes) {
    const name = String(n.name || '');
    const kind = String(n.semanticKind || '');
    const op = String(n.operationType || n.formal_semantics?.operation_type || '');
    const text = nodeText(n);
    const isDoc = /^doc\./.test(name) || n.source_context?.source_type === 'markdown';
    const isUserQuery = /user.?query|user_query/i.test(name) || kind === 'user_input';

    // fragmented bullet: text starts with a list marker AND contains an internal
    // newline whose next line is NOT a new marker (i.e. a continuation that should
    // have folded). Also flag if text is a bare marker fragment.
    if (isDoc && /\n/.test(text)) {
      const lines = text.split('\n');
      const firstIsList = isListLine(lines[0]);
      const hasUnfoldedCont = lines.slice(1).some(l => l.trim() && !isListLine(l));
      if (firstIsList && hasUnfoldedCont) {
        findings.fragmented_bullets.push({ id: n.id, name, sample: text.slice(0, 120) });
      }
    }

    // disclaimer extracted as an active op
    const activeOp = op && !['context', 'definition', 'note', ''].includes(op)
      && kind !== 'doc_definition' && kind !== 'policy';
    const looksNegated = /\b(do not|don'?t|does not|doesn'?t|never|must not|cannot|can'?t|no longer|avoid|refrain|should not|shouldn'?t)\b/i.test(text)
      || /does\s+not\s+do/i.test(text);
    if (isDoc && activeOp && looksNegated) {
      findings.disclaimer_as_action.push({ id: n.id, name, op, sample: text.slice(0, 120) });
    }

    // dangling
    const d = deg.get(n.id) || { in: 0, out: 0 };
    if (d.in === 0 && d.out === 0 && !isUserQuery) {
      findings.dangling.push({ id: n.id, name, kind, sample: text.slice(0, 80) });
    }

    // empty action node
    const targets = n.formal_semantics?.targets || [];
    if (isDoc && activeOp && !text.trim() && targets.length === 0) {
      findings.empty_action.push({ id: n.id, name, op });
    }

    // description node carrying an observation (potential non-instruction residue)
    if (isDoc && (kind === 'doc_definition' || op === 'context') && obsNodeIds.has(n.id)) {
      findings.description_with_obs.push({ id: n.id, name, sample: text.slice(0, 80) });
    }
  }

  return {
    file: fileName,
    skill: fcg.meta?.skill_name || fileName,
    counts: {
      nodes: nodes.length,
      edges: edges.length,
      observations: observations.length,
      label_flows: (sp.label_flows || []).length,
      broken_edges: brokenEdges
    },
    findings,
    finding_counts: Object.fromEntries(Object.entries(findings).map(([k, v]) => [k, v.length]))
  };
}

const reports = [];
for (const f of files) {
  let fcg;
  try {
    fcg = JSON.parse(fs.readFileSync(path.join(skillsDir, f), 'utf-8'));
  } catch (e) {
    reports.push({ file: f, error: String(e.message) });
    continue;
  }
  reports.push(reviewSkill(fcg, f));
}

// aggregate
const agg = { skills: reports.length, nodes: 0, edges: 0, observations: 0, label_flows: 0, broken_edges: 0,
  fragmented_bullets: 0, disclaimer_as_action: 0, dangling: 0, empty_action: 0, description_with_obs: 0 };
for (const r of reports) {
  if (r.error) continue;
  agg.nodes += r.counts.nodes; agg.edges += r.counts.edges;
  agg.observations += r.counts.observations; agg.label_flows += r.counts.label_flows;
  agg.broken_edges += r.counts.broken_edges;
  for (const k of ['fragmented_bullets','disclaimer_as_action','dangling','empty_action','description_with_obs']) {
    agg[k] += r.finding_counts[k];
  }
}

console.log('=== FCG SEMANTIC REVIEW ===');
console.log(`skills: ${agg.skills}`);
console.log(`totals: nodes=${agg.nodes} edges=${agg.edges} observations=${agg.observations} label_flows=${agg.label_flows} broken_edges=${agg.broken_edges}`);
console.log(`flags: fragmented_bullets=${agg.fragmented_bullets} disclaimer_as_action=${agg.disclaimer_as_action} dangling=${agg.dangling} empty_action=${agg.empty_action} description_with_obs=${agg.description_with_obs}`);
console.log('');
console.log('per-skill:');
for (const r of reports) {
  if (r.error) { console.log(`  ${r.file}  ERROR ${r.error}`); continue; }
  const c = r.counts, fc = r.finding_counts;
  const flags = ['fragmented_bullets','disclaimer_as_action','dangling','empty_action','description_with_obs']
    .filter(k => fc[k] > 0).map(k => `${k}=${fc[k]}`).join(' ');
  console.log(`  ${r.file.replace('-sfg.json','')}  N=${c.nodes} E=${c.edges} O=${c.observations} LF=${c.label_flows} brk=${c.broken_edges}  ${flags || 'clean'}`);
}

if (jsonOut) {
  fs.writeFileSync(jsonOut, JSON.stringify({ aggregate: agg, reports }, null, 2), 'utf-8');
  console.log(`\nfull report: ${jsonOut}`);
}
