// Micro-N4 on the rule-cleared, no-LLM-backstop, external_network flows — the
// subset where the rule silently clears a REAL network egress. Dedups them into
// distinct decision patterns (skill + sink operation + category + receiver +
// necessity + limiting component) and dumps a labelable worklist so each pattern
// can be given ground truth. If every pattern is genuinely necessary, the rule
// is trustworthy at this exposure tier and the gate rightly saves LLM spend; if
// any is wrong, this tier must be added to the unconditional-send gate.
//
// Usage: node .necessity-probe/external-egress-audit.js
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];

function domComp(c) {
  const e = Object.entries(c || {});
  e.sort((a, b) => a[1] - b[1]);
  return e.length ? e[0][0] : '';
}

function run() {
  const rows = [];
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    if (!fs.existsSync(fcgPath)) { console.error('skip', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const sp = fcg.security_profile || {};
    const nodeById = new Map((fcg.nodes || []).map(n => [n.id || n.node_id, n]));
    const obsById = new Map((sp.observations || []).map(o => [o.observation_id, o]));
    const r = analyzeDoe(fcg, { llmJudge: false, keepInternal: true });
    for (const a of r.assessments) {
      if (a.potential_doe) continue;
      const g = a._llm_gate || {};
      if (g.eligible) continue;                          // has LLM backstop -> not silent
      if (g.trust_boundary !== 'external_network') continue;  // real network egress only
      const obs = obsById.get(a.observation_id) || {};
      const sinkNode = nodeById.get(obs.node_id) || {};
      rows.push({
        skill, k: `${a.observation_id}::${a.label_flow_id}`,
        cat: a.label_category || '', receiver: g.receiver_scope || '',
        retention: (obs.boundary || {}).retention_scope || '',
        op: obs.operation_type || sinkNode.operationType || '',
        sink_name: sinkNode.name || obs.node_name || '',
        sink_desc: (sinkNode.description || '').slice(0, 90),
        nec: a.necessity_score, risk: g.boundary_risk,
        comp: a.component_scores, lim: domComp(a.component_scores),
      });
    }
  }
  // dedup into patterns
  const groups = {};
  for (const row of rows) {
    const key = [row.skill, row.op, row.cat, row.receiver, row.retention, row.lim, row.nec].join('|');
    (groups[key] = groups[key] || []).push(row);
  }
  const patterns = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length).map((k, i) => {
    const m = groups[k];
    const [skill, op, cat, receiver, retention, lim, nec] = k.split('|');
    return {
      pattern_id: i + 1, count: m.length, skill, op, cat, receiver, retention,
      limiting_component: lim, necessity: Number(nec), boundary_risk: m[0].risk,
      sink_name: m[0].sink_name, sink_desc: m[0].sink_desc,
      comp: m[0].comp, example_key: m[0].k, truth: null, rationale: '',
    };
  });
  fs.writeFileSync(path.join(__dirname, 'external-egress-patterns.json'), JSON.stringify(patterns, null, 1));
  console.log(`external_network no-backstop rule-cleared flows: ${rows.length}`);
  console.log(`collapse to ${patterns.length} distinct patterns:`);
  for (const p of patterns) {
    console.log(`  x${String(p.count).padStart(3)} [${p.skill.slice(0, 14)}] ${p.op} ${p.cat}->${p.receiver}/${p.retention} nec=${p.necessity} lim=${p.limiting_component}`);
    console.log(`         sink: ${p.sink_name}`);
    console.log(`         desc: ${p.sink_desc}`);
  }
}

run();
