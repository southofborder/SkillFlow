// Rule-strength audit.
//
// Question: is the rule layer TOO STRONG — does it clear (judge necessary,
// non-pd) any flow that is actually a DOE (false negative)? Sending to the LLM
// is only worth it where the rule's "necessary" verdict is UNTRUSTWORTHY. So we
// stratify all rule-cleared flows by exposure and surface the fragile ones:
//   - high exposure (external_network / persistent_storage / external retention)
//   - necessity BORDERLINE (>=0.7 but <=0.82) — barely cleared the 0.7 bar
//   - receiver x category SEMANTICALLY WEAK (compat base low for the pair)
// A cleared flow that is high-exposure + borderline + semantically weak is the
// empirical fingerprint of an over-strong rule. If none exist, the rule's
// necessary verdicts are trustworthy and the gate rightly saves LLM spend.
//
// Usage: node .necessity-probe/rule-strength-audit.js
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];
const HIGH_EXPOSURE_TRUST = new Set(['external_network', 'persistent_storage']);
const SENSITIVE_CATS = new Set(['credentials', 'secret_material', 'pii', 'financial',
  'health', 'biometric', 'browser_data', 'security_data']);

function run() {
  let cleared = 0, highExp = 0, borderline = 0, fragile = 0;
  const fragileRows = [], sensitiveHighExp = [];
  const byTrust = {};
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    if (!fs.existsSync(fcgPath)) { console.error('skip', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const r = analyzeDoe(fcg, { llmJudge: false, keepInternal: true });
    for (const a of r.assessments) {
      if (a.potential_doe) continue;              // only rule-CLEARED flows
      const g = a._llm_gate || {};
      if (!g.boundary_crossed) continue;          // must be an exposure at all
      cleared += 1;
      const trust = g.trust_boundary || '';
      const risk = Number(g.boundary_risk || 0);
      const nec = Number(a.necessity_score || 0);
      const cat = a.label_category || '';
      const isHighExp = HIGH_EXPOSURE_TRUST.has(trust) || risk >= 0.85;
      const isBorderline = nec >= 0.7 && nec <= 0.82;
      const isSensitive = SENSITIVE_CATS.has(cat);
      byTrust[trust] = (byTrust[trust] || 0) + 1;
      if (isHighExp) highExp += 1;
      if (isBorderline) borderline += 1;
      // sensitive category leaving on a high-exposure boundary, rule-cleared
      // AND NOT sent to the LLM: the classic over-exposure with no backstop.
      // (eligible=true means the gate already sends it — not a silent clear.)
      if (isHighExp && isSensitive && !g.eligible) {
        sensitiveHighExp.push({ skill, k: `${a.observation_id}::${a.label_flow_id}`,
          cat, trust, risk, nec, comp: a.component_scores, sens: g.label_sensitivity });
      }
      // fragile = high exposure AND borderline necessity AND NOT sent to LLM:
      // the rule barely cleared a heavy flow with no LLM backstop — the exact
      // place an over-strong rule would hide a false negative unchecked.
      if (isHighExp && isBorderline && !g.eligible) {
        fragile += 1;
        fragileRows.push({ skill, k: `${a.observation_id}::${a.label_flow_id}`,
          cat, trust, risk, nec, comp: a.component_scores, sens: g.label_sensitivity,
          eligible: g.eligible, reason: g.reason });
      }
    }
  }
  fragileRows.sort((x, y) => x.nec - y.nec);
  fs.writeFileSync(path.join(__dirname, 'rule-strength-fragile.json'),
    JSON.stringify({ fragileRows, sensitiveHighExp }, null, 1));
  console.log(`rule-cleared boundary-crossing flows: ${cleared}`);
  console.log(`  high-exposure (external/persistent or risk>=0.85): ${highExp}`);
  console.log(`  borderline necessity (0.70-0.82):                  ${borderline}`);
  console.log(`  FRAGILE (high-exposure AND borderline):            ${fragile}  <- rule over-strong risk`);
  console.log(`  SENSITIVE-CAT on high-exposure boundary (leak!):   ${sensitiveHighExp.length}  <- must be 0`);
  console.log('cleared by trust_boundary:', byTrust);
  if (fragile) {
    console.log('\n-- fragile flows (sorted by necessity, lowest first) --');
    for (const f of fragileRows.slice(0, 25)) {
      console.log(`  ${f.skill} ${f.k} cat=${f.cat} trust=${f.trust} risk=${f.risk} nec=${f.nec} sent_llm=${f.eligible} comp=${JSON.stringify(f.comp)}`);
    }
  }
}

run();
