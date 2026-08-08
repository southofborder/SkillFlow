#!/usr/bin/env node
/**
 * review-digest.js — build a compact, token-cheap semantic digest of an FCG JSON
 * so a reviewer (human or LLM) can judge node extraction + flow paths WITHOUT
 * loading the raw multi-hundred-MB FCG file.
 *
 * For each skill it emits:
 *   - node table: id | name | type | critical | one-line description
 *   - cross-boundary observations (the effective "sinks"): node | op | boundary
 *   - multi-node label flows: readable node_name paths (deduped)
 * Usage: node scripts/review-digest.js <fcg.json> [--json]
 */
const fs = require('fs');

function loadFcg(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function shortBoundary(b = {}) {
  return `${b.trust_boundary || '?'}/${b.receiver_scope || '?'}/${b.data_surface || '?'}`;
}

function buildDigest(j) {
  const meta = j.meta || {};
  const nodes = j.nodes || [];
  const sp = j.security_profile || {};
  const obs = sp.observations || [];
  const flows = sp.label_flows || [];

  const nodeSummary = nodes.map(n => ({
    id: n.id,
    name: n.name,
    type: n.type,
    critical: !!n.is_critical,
    action: n.action || '',
    line: n.location?.line ?? '',
    desc: (n.description || '').replace(/\s+/g, ' ').slice(0, 90)
  }));

  // cross-boundary observations = effective sinks. Skip pure model_inference
  // (every node has one) unless it is the only observation for that node.
  const crossing = obs
    .filter(o => o.operation_type !== 'model_inference')
    .map(o => ({
      obs: o.observation_id,
      node: o.node_name,
      op: o.operation_type,
      boundary: shortBoundary(o.boundary)
    }));

  // dedupe multi-node flows by their node_name path
  const seen = new Set();
  const flowPaths = [];
  for (const f of flows) {
    const p = f.node_names || [];
    if (p.length < 2) continue;
    const key = p.join(' -> ');
    if (seen.has(key)) continue;
    seen.add(key);
    flowPaths.push(key);
  }

  return {
    skill: meta.skill_name,
    version: meta.skill_version,
    counts: {
      nodes: nodes.length,
      edges: (j.edges || []).length,
      observations: obs.length,
      crossing_observations: crossing.length,
      label_flows: flows.length,
      unique_multi_node_flows: flowPaths.length
    },
    nodes: nodeSummary,
    crossing_observations: crossing,
    flow_paths: flowPaths
  };
}

function renderText(d) {
  const L = [];
  L.push(`# ${d.skill} v${d.version}`);
  L.push(`counts: ${JSON.stringify(d.counts)}`);
  L.push(`\n## NODES (${d.nodes.length})`);
  for (const n of d.nodes) {
    L.push(`${n.id} | ${n.name} | ${n.type}${n.critical ? ' CRIT' : ''} | L${n.line} | ${n.desc}`);
  }
  L.push(`\n## CROSSING OBSERVATIONS (${d.crossing_observations.length})`);
  for (const o of d.crossing_observations) {
    L.push(`${o.obs} | ${o.node} | ${o.op} | ${o.boundary}`);
  }
  L.push(`\n## FLOW PATHS (${d.flow_paths.length} unique multi-node)`);
  for (const p of d.flow_paths) L.push(`- ${p}`);
  return L.join('\n');
}

function main() {
  const args = process.argv.slice(2);
  const file = args.find(a => !a.startsWith('--'));
  const asJson = args.includes('--json');
  if (!file) {
    console.error('usage: node scripts/review-digest.js <fcg.json> [--json]');
    process.exit(1);
  }
  const d = buildDigest(loadFcg(file));
  process.stdout.write(asJson ? JSON.stringify(d, null, 2) : renderText(d));
}

if (require.main === module) main();
module.exports = { buildDigest, renderText };
