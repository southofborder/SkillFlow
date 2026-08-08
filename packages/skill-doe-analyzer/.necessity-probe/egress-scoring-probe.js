// Does the SCORE already separate necessary from suspicious external egress —
// making a gate guard redundant? For every external_network egress flow in the
// corpus, tabulate origin trust_boundary, the three components, necessity, and
// potential_doe. The claim to test (user's): a flow that LACKS the "safe"
// structure (user_visible origin / declared task / egress-content = the query)
// should ALREADY score < 0.7 and be flagged — so the fix, if any, belongs in
// scoring/threshold, not a special-case gate.
//
// Prints, per (origin_trust x potential_doe), the necessity distribution, and
// flags any UNFLAGGED (necessity>=0.7, medium sensitivity, no LLM backstop)
// external egress whose origin is NOT user_visible — the exact escape a broken
// score would allow.
//
// Usage: node .necessity-probe/egress-scoring-probe.js
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];

function run() {
  const byOriginPd = {};       // originTrust::pd -> {n, necSum, necMin, necMax}
  const escapes = [];          // necessary+medium+no-backstop+non-user origin egress
  let egressTotal = 0;
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    if (!fs.existsSync(fcgPath)) { console.error('skip', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const sp = fcg.security_profile || {};
    const lfById = new Map((sp.label_flows || []).map(l => [l.label_flow_id, l]));
    const fsById = new Map((sp.flow_states || []).map(s => [s.state_id, s]));
    const r = analyzeDoe(fcg, { llmJudge: false, keepInternal: true });
    for (const a of r.assessments) {
      const g = a._llm_gate || {};
      if (g.trust_boundary !== 'external_network') continue;   // egress only
      egressTotal += 1;
      const lf = lfById.get(a.label_flow_id) || {};
      const fst = fsById.get(lf.flow_state_id) || {};
      const originTrust = (fst.origin_boundary || {}).trust_boundary || '(unknown)';
      const pd = a.potential_doe ? 'pd' : 'clr';
      const key = `${originTrust}::${pd}`;
      const b = byOriginPd[key] || { n: 0, necSum: 0, necMin: 9, necMax: -9 };
      b.n += 1; b.necSum += Number(a.necessity_score);
      b.necMin = Math.min(b.necMin, a.necessity_score);
      b.necMax = Math.max(b.necMax, a.necessity_score);
      byOriginPd[key] = b;
      // the escape: rule-cleared, medium, no LLM backstop, origin NOT user_visible
      const medium = (g.label_sensitivity === 'medium');
      if (!a.potential_doe && !g.eligible && medium && originTrust !== 'user_visible') {
        escapes.push({ skill, k: `${a.observation_id}::${a.label_flow_id}`,
          cat: a.label_category, originTrust, receiver: g.receiver_scope,
          nec: a.necessity_score, comp: a.component_scores });
      }
    }
  }
  console.log(`external_network egress flows: ${egressTotal}\n`);
  console.log('necessity by (origin_trust :: potential_doe):');
  for (const k of Object.keys(byOriginPd).sort()) {
    const b = byOriginPd[k];
    console.log(`  ${k.padEnd(28)} n=${String(b.n).padStart(4)}  nec avg=${(b.necSum / b.n).toFixed(3)} min=${b.necMin.toFixed(2)} max=${b.necMax.toFixed(2)}`);
  }
  console.log(`\nESCAPES (cleared + medium + no-backstop + origin!=user_visible): ${escapes.length}`);
  for (const e of escapes.slice(0, 30)) {
    console.log(`  ${e.skill} ${e.k} cat=${e.cat} origin=${e.originTrust} recv=${e.receiver} nec=${e.nec} comp=${JSON.stringify(e.comp)}`);
  }
}

run();
