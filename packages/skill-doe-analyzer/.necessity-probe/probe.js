// N0 read-only probe: for every (observation, label_flow) unit in the completable
// v6 corpus, compute BOTH the current word-bag task_need AND candidate structural
// signals (declaration coverage, sink declared, schema-input membership,
// receiver×category compatibility). NO DOE change — pure observation to calibrate
// the necessity redesign before touching scoring.
//
// Usage: node .necessity-probe/probe.js
const fs = require('fs');
const path = require('path');
const {
  createNecessityContext, scoreNecessityBaseline, isTaskContextNode
} = require('../src/necessity-baseline');
const { scoreExposure } = require('../src/exposure-scorer');
const { resolveLabelFlowPath, createFlowPathContext } = require('../src/flow-path-utils');
const { buildLabelDictionary, resolveLabel } = require('../src/label-resolver');

const V6_DIR = path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp');
const SKILLS = [
  '00002_skill-vetter_1.0.0', '00003_polymarket-trade_1.0.6', '00006_github_1.0.0',
  '00007_gog_1.0.0', '00008_skillscan_1.1.6', '00009_weather_1.0.0',
];
const TASK_KINDS = new Set([
  'doc_step', 'doc_operation', 'doc_definition', 'trigger', 'policy',
  'script_entry', 'script_function',
]);

function declarationCoverage(nodePath, nodeById) {
  if (!nodePath.length) return { cov: 0, declared: 0, total: 0 };
  let declared = 0;
  for (const id of nodePath) {
    const n = nodeById.get(id) || {};
    if (TASK_KINDS.has(n.semanticKind) || isTaskContextNode(n)) declared += 1;
  }
  return { cov: declared / nodePath.length, declared, total: nodePath.length };
}

function schemaInputMembership(label, sinkNode) {
  const fs2 = (sinkNode && sinkNode.formal_semantics) || {};
  const inputs = fs2.inputs || [];
  if (!inputs.length) return null; // sparse: no schema to check
  const needles = [label.field_name, label.subtype, label.category, label.label]
    .filter(Boolean).map(s => String(s).toLowerCase());
  const hay = inputs.map(i => `${i.name || ''} ${i.type || ''}`.toLowerCase()).join(' ');
  return needles.some(n => hay.includes(n));
}

function run() {
  const rows = [];
  for (const skill of SKILLS) {
    const fcgPath = path.join(V6_DIR, `v6_${skill}.json`);
    if (!fs.existsSync(fcgPath)) { console.error('skip missing', skill); continue; }
    const fcg = JSON.parse(fs.readFileSync(fcgPath, 'utf-8'));
    const sp = fcg.security_profile || {};
    const nodeById = new Map((fcg.nodes || []).map(n => [n.id, n]));
    const fsById = new Map((sp.flow_states || []).map(f => [f.state_id, f]));
    const dict = buildLabelDictionary(sp);
    const flowById = new Map((sp.label_flows || []).map(f => {
      const resolved = resolveLabel(f, dict, () => {});
      return [f.label_flow_id, f.label === resolved ? f : { ...f, label: resolved }];
    }));
    const profById = new Map((sp.node_profiles || []).map(p => [p.node_id, p]));
    const nctx = createNecessityContext(fcg);
    const fpc = createFlowPathContext(fcg);

    for (const obs of sp.observations || []) {
      const sinkNode = nodeById.get(obs.node_id) || {};
      const sinkDeclared = TASK_KINDS.has(sinkNode.semanticKind) || isTaskContextNode(sinkNode);
      for (const lfid of obs.label_flow_ids || []) {
        const lf = flowById.get(lfid);
        if (!lf) continue;
        const label = lf.label || {};
        const nodeProfile = profById.get(obs.node_id) || {};
        const exposure = scoreExposure({ labelFlow: lf, observation: obs });
        const nec = scoreNecessityBaseline({ fcg, observation: obs, labelFlow: lf, nodeProfile, context: nctx });
        const rp = resolveLabelFlowPath(lf, fpc);
        const dc = declarationCoverage(rp.node_path || [], nodeById);
        const fstate = fsById.get(lf.flow_state_id) || {};
        rows.push({
          skill,
          k: `${obs.observation_id}::${lfid}`,
          category: label.category || '',
          trust: (obs.boundary || {}).trust_boundary || '',
          receiver: (obs.boundary || {}).receiver_scope || '',
          boundary_crossed: exposure.boundary_crossed,
          // current word-bag components
          wb_task: nec.component_scores.task_need,
          wb_action: nec.component_scores.action_input_need,
          wb_receiver: nec.component_scores.receiver_semantic_need,
          wb_nec: nec.necessity_score,
          // candidate structural signals
          decl_cov: Number(dc.cov.toFixed(3)),
          path_len: dc.total,
          sink_declared: sinkDeclared,
          schema_member: schemaInputMembership(label, sinkNode), // true/false/null
          transform_sig: fstate.transform_sig || 'none',
          reduction_applied: Boolean(fstate.reduction_applied),
        });
      }
    }
  }
  fs.writeFileSync(path.join(__dirname, 'probe-rows.json'), JSON.stringify(rows));
  summarize(rows);
}

function summarize(rows) {
  const n = rows.length;
  const bc = rows.filter(r => r.boundary_crossed);
  console.log(`total units=${n}, boundary_crossed=${bc.length}`);
  // task_need: word-bag vs declaration coverage
  const fullyDeclared = rows.filter(r => r.decl_cov === 1);
  const zeroDeclared = rows.filter(r => r.decl_cov === 0);
  const mixed = rows.filter(r => r.decl_cov > 0 && r.decl_cov < 1);
  console.log(`decl_cov: full=${fullyDeclared.length} zero=${zeroDeclared.length} mixed=${mixed.length}`);
  const avg = (a, f) => a.length ? (a.reduce((s, r) => s + f(r), 0) / a.length).toFixed(3) : 'n/a';
  console.log(`  wb_task avg | fullyDeclared=${avg(fullyDeclared, r => r.wb_task)} zeroDeclared=${avg(zeroDeclared, r => r.wb_task)} mixed=${avg(mixed, r => r.wb_task)}`);
  console.log(`  sink_declared=true: ${rows.filter(r => r.sink_declared).length}, false: ${rows.filter(r => !r.sink_declared).length}`);
  // schema membership availability
  const sm = rows.filter(r => r.schema_member !== null);
  console.log(`schema checkable=${sm.length} (member=true ${sm.filter(r => r.schema_member).length}), sparse(null)=${rows.filter(r => r.schema_member === null).length}`);
  console.log(`  wb_action avg | schemaMember=${avg(sm.filter(r => r.schema_member), r => r.wb_action)} schemaMiss=${avg(sm.filter(r => !r.schema_member), r => r.wb_action)} sparse=${avg(rows.filter(r => r.schema_member === null), r => r.wb_action)}`);
  // divergence: word-bag says task-necessary (high) but zero declaration coverage (structural says suspicious)
  const conflict = bc.filter(r => r.wb_task >= 0.7 && r.decl_cov === 0);
  const conflict2 = bc.filter(r => r.wb_task < 0.3 && r.decl_cov === 1 && r.sink_declared);
  console.log(`CONFLICTS (boundary-crossed): wb_task>=0.7 but decl_cov=0 => ${conflict.length}`);
  console.log(`CONFLICTS: wb_task<0.3 but fully-declared+sink-declared => ${conflict2.length}`);
}

run();
