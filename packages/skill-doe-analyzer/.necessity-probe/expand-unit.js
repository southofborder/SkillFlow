// Expand a single (skill, obs::lf) decision unit into full human-readable context:
// origin node, sink node, label flow, flow_state (transform/origin), and the DOE
// assessment's exposure + necessity components.
// Usage: node .necessity-probe/expand-unit.js <skill> <obsId> <lfId>
const fs = require('fs');
const path = require('path');
const { analyzeDoe } = require('../src/doe-analyzer');

const [skill, obsId, lfId] = process.argv.slice(2);
const fcg = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', '..', 'skill-fcg-py', '.m4tmp', `v6_${skill}.json`)));
const sp = fcg.security_profile || {};
const nodeById = new Map((fcg.nodes || []).map(n => [n.id || n.node_id, n]));

const lf = (sp.label_flows || []).find(l => l.label_flow_id === lfId);
const fst = (sp.flow_states || []).find(s => s.state_id === (lf && lf.flow_state_id));
const obs = (sp.observations || []).find(o => o.observation_id === obsId);
const originNode = nodeById.get(lf && lf.origin_node);
const sinkNode = nodeById.get(obs && obs.node_id);

const r = analyzeDoe(fcg, { llmJudge: false, keepInternal: true });
const a = r.assessments.find(x => x.observation_id === obsId && x.label_flow_id === lfId);

function nodeBrief(n) {
  if (!n) return null;
  return {
    id: n.id || n.node_id, name: n.name || n.node_name, type: n.type,
    semanticKind: n.semanticKind, operationType: n.operationType || n.operation_type,
    description: n.description, instructionText: n.instructionText,
    signature: n.signature, location: n.location,
  };
}
console.log('#### SKILL:', skill, '| unit:', `${obsId}::${lfId}`);
console.log('\n=== ORIGIN NODE ===\n', JSON.stringify(nodeBrief(originNode), null, 1));
console.log('\n=== SINK NODE (observation) ===\n', JSON.stringify(nodeBrief(sinkNode), null, 1));
console.log('\n=== OBSERVATION BOUNDARY ===\n', JSON.stringify(obs && obs.boundary, null, 1),
  '\n  operation_type:', obs && obs.operation_type, '| security_tags:', JSON.stringify(obs && obs.security_tags));
console.log('\n=== FLOW STATE ===\n', JSON.stringify({
  transform_sig: fst && fst.transform_sig, word_set: fst && fst.word_set,
  origin_node: fst && fst.origin_node, origin_boundary: fst && fst.origin_boundary,
  availability: fst && fst.availability, merged_path_count: fst && fst.merged_path_count,
}, null, 1));
console.log('\n=== DOE ASSESSMENT ===\n', JSON.stringify({
  label_category: a && a.label_category, label_name: a && a.label_name,
  exposure_score: a && a.exposure_score, doe_score: a && a.doe_score,
  necessity_score: a && a.necessity_score, potential_doe: a && a.potential_doe,
  components: a && a.component_scores, gate: a && a._llm_gate,
}, null, 1));
