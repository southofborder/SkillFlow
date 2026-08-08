// N4 acceptance harness.
//
// The 517 cleared_DOE flips are only DANGEROUS when the recall-first LLM gate
// ALSO skips them — those are rule-final silent clears with no LLM backstop.
// Flips the gate still sends to the LLM are safe (LLM re-judges), so they need
// no human ground truth.
//
// This harness re-runs the current rule-only DOE, attaches each flip's gate
// decision + receiver + trust boundary, and partitions the 517 into:
//   (A) rule-final (gate skip)  -> REQUIRES human label (precision risk)
//   (B) still sent to LLM       -> safe, LLM backstops
// It writes a compact, human-labelable worklist for bucket A to
// .necessity-probe/n4-worklist.json and prints the partition summary.
//
// Usage: node .necessity-probe/n4-accept.js
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const BASE_DIR = path.resolve(__dirname, '..', '.m4gate');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];

function run() {
  const worklist = [];
  let clearedTotal = 0, ruleFinal = 0, sentToLlm = 0;
  const finalByCat = {}, sentByCat = {};
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    const basePath = path.join(BASE_DIR, `baseline_${skill}.json`);
    if (!fs.existsSync(fcgPath) || !fs.existsSync(basePath)) { console.error('skip', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const base = new Map(JSON.parse(fs.readFileSync(basePath, 'utf-8')).map(a => [a.k, a]));
    const r = analyzeDoe(fcg, { llmJudge: false, keepInternal: true });
    for (const a of r.assessments) {
      const k = `${a.observation_id}::${a.label_flow_id}`;
      const b = base.get(k);
      if (!b) continue;
      const clearedNow = b.pd && !a.potential_doe;
      if (!clearedNow) continue;
      clearedTotal += 1;
      const gate = a._llm_gate || {};
      const cat = a.label_category || '(none)';
      if (gate.eligible) {
        sentToLlm += 1;
        sentByCat[cat] = (sentByCat[cat] || 0) + 1;
      } else {
        ruleFinal += 1;
        finalByCat[cat] = (finalByCat[cat] || 0) + 1;
        worklist.push({
          skill, k,
          cat,
          sensitivity: gate.label_sensitivity || '',
          gate_reason: gate.reason || '',
          trust_boundary: gate.trust_boundary || '',
          receiver_scope: gate.receiver_scope || '',
          nec_before: b.nec, nec_after: a.necessity_score,
          doe_before: b.doe, doe_after: a.doe_score,
          comp_after: a.component_scores,
          label: a.label_name || '',
          observation: a.observation_summary || a.observation_id,
          truth: null, // human fills: "necessary" | "doe" | "unsure"
        });
      }
    }
  }
  worklist.sort((x, y) => (y.doe_after - x.doe_after) || x.cat.localeCompare(y.cat));
  fs.writeFileSync(path.join(__dirname, 'n4-worklist.json'), JSON.stringify(worklist, null, 1));
  console.log(`cleared_DOE flips: ${clearedTotal}`);
  console.log(`  (A) RULE-FINAL (gate skip, no LLM backstop): ${ruleFinal}  -> needs ground truth`);
  console.log(`      by category:`, finalByCat);
  console.log(`  (B) still SENT to LLM (safe, backstopped):   ${sentToLlm}`);
  console.log(`      by category:`, sentByCat);
  console.log(`worklist (bucket A) written to .necessity-probe/n4-worklist.json`);
}

run();
