// Flip-audit harness for the necessity redesign. Runs the CURRENT working-tree
// DOE (rule-only) on the completable v6 corpus and diffs potential_doe / doe_score
// against the frozen word-bag baseline snapshots in .m4gate/baseline_*.json.
//
// Classifies every flip and buckets by category/receiver so each N-step change can
// be audited: is a flip a correction (word-bag was wrong) or noise (structural
// over-reach)? Prints a summary; writes full flip list to .necessity-probe/flips.json.
//
// Usage: node .necessity-probe/flip-audit.js
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const BASE_DIR = path.resolve(__dirname, '..', '.m4gate');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];
const EPS = 0.05;

function run() {
  const flips = [];
  let total = 0, pdBefore = 0, pdAfter = 0, scoreDrift = 0, maxDrift = 0;
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    const basePath = path.join(BASE_DIR, `baseline_${skill}.json`);
    if (!fs.existsSync(fcgPath) || !fs.existsSync(basePath)) { console.error('skip', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const base = new Map(JSON.parse(fs.readFileSync(basePath, 'utf-8')).map(a => [a.k, a]));
    const r = analyzeDoe(fcg, { llmJudge: false });
    // rebuild category/receiver lookup from fcg for attribution
    const sp = fcg.security_profile || {};
    for (const a of r.assessments) {
      const k = `${a.observation_id}::${a.label_flow_id}`;
      const b = base.get(k);
      total += 1;
      if (b) {
        if (b.pd) pdBefore += 1;
        if (a.potential_doe) pdAfter += 1;
        const d = Math.abs(Number(a.doe_score) - Number(b.doe));
        scoreDrift += d; maxDrift = Math.max(maxDrift, d);
        if (Boolean(a.potential_doe) !== Boolean(b.pd)) {
          flips.push({
            skill, k,
            dir: a.potential_doe ? 'became_DOE' : 'cleared_DOE',
            cat: a.label_category || '',
            trust: a.boundary_basis ? '' : '',
            recv: (a._recv || ''),
            nec_before: b.nec, nec_after: a.necessity_score,
            doe_before: b.doe, doe_after: a.doe_score,
            comp_before: b.comp, comp_after: a.component_scores,
          });
        }
      }
    }
  }
  fs.writeFileSync(path.join(__dirname, 'flips.json'), JSON.stringify(flips, null, 1));
  console.log(`units=${total} pd_before=${pdBefore} pd_after=${pdAfter} (delta=${pdAfter - pdBefore})`);
  console.log(`flips=${flips.length}  avg_doe_drift=${(scoreDrift / total).toFixed(4)} max_drift=${maxDrift.toFixed(3)}`);
  const dir = {}, cat = {};
  for (const f of flips) {
    dir[f.dir] = (dir[f.dir] || 0) + 1;
    const key = `${f.dir}/${f.cat}`;
    cat[key] = (cat[key] || 0) + 1;
  }
  console.log('flip directions:', dir);
  console.log('flip by direction/category:', cat);
}

run();
