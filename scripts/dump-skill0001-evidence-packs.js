// Dump (1) new flow-centric evidence packs and (2) the EXACT payload sent to the
// model, for human review. Pure construction — no API calls.
//
// The model payload is built by llm-judge.js: buildJudgePayload(packs, config),
// which produces { model, temperature, messages:[system,user] }. The user
// message content is a JSON string carrying output_schema, scoring_guidance,
// judgement_flow, shared_context.task_memory (skill-level), and evidence_packs
// (each pack run through compactPackForPrompt + budgetPackIfNeeded).
const fs = require('fs');
const path = require('path');
const { buildEvidencePack, createEvidencePackContext } = require('../packages/skill-doe-analyzer/src/evidence-pack');
const { buildJudgePayload, resolveJudgeOptions } = require('../packages/skill-doe-analyzer/src/llm-judge');
const { buildLabelDictionary, resolveLabel } = require('../packages/skill-doe-analyzer/src/label-resolver');
const { buildNodeProfiles } = require('../packages/skill-fcg-analyzer/src/security/node-profiler');
const { buildObservations } = require('../packages/skill-fcg-analyzer/src/security/observation-analyzer');

const FCG_PATH = path.resolve(__dirname, '../results/sample-skill1/fcg/skills/skill_0001-00001_self-improving-agent_3.0.21-fcg.json');
const PACK_OUT = path.resolve(__dirname, '../results/sample-skill1/skill_0001-evidence-pack-demo.json');
const PAYLOAD_OUT = path.resolve(__dirname, '../results/sample-skill1/skill_0001-model-payload-demo.json');
const SAMPLE_COUNT = Number(process.argv[2] || 3);

const fcg = JSON.parse(fs.readFileSync(FCG_PATH, 'utf8'));
const security = fcg.security_profile || {};
// The saved FCG json was produced by older node-profiler code (semantic_reason
// polluted node roles). Recompute node_profiles + observations locally with the
// current code so this demo faithfully reflects the fixed pipeline — no API call,
// no full FCG rerun. (Recompute is pure: profiles/observations derive from
// nodes/edges/label_flows already in the file.)
security.node_profiles = buildNodeProfiles(fcg.nodes || [], fcg.edges || []);
security.observations = buildObservations({
  nodeProfiles: security.node_profiles,
  labelFlows: security.label_flows || []
}).observations;
const observations = security.observations || [];
const nodeProfiles = security.node_profiles || [];

const labelDictionary = buildLabelDictionary(security);
const labelFlowById = new Map((security.label_flows || []).map(flow => {
  const resolved = resolveLabel(flow, labelDictionary, () => {});
  return [flow.label_flow_id, flow.label === resolved ? flow : { ...flow, label: resolved }];
}));
const profileByNodeId = new Map(nodeProfiles.map(p => [p.node_id, p]));
const context = createEvidencePackContext(fcg);

// Pick SAMPLE_COUNT (observation x label_flow) pairs across DISTINCT boundary
// nodes and DISTINCT label categories so the demo isn't all one node. Prefer
// units whose flow has MULTIPLE nodes (a real source-to-sink path), so the demo
// shows full provenance rather than degenerate single-node introduction points.
const { resolveLabelFlowPath } = require('../packages/skill-doe-analyzer/src/flow-path-utils');

const candidates = [];
for (const observation of observations) {
  const nodeProfile = profileByNodeId.get(observation.node_id) || {};
  for (const labelFlowId of observation.label_flow_ids || []) {
    const labelFlow = labelFlowById.get(labelFlowId);
    if (!labelFlow) continue;
    const resolved = resolveLabelFlowPath(labelFlow, context.flowPathContext);
    candidates.push({
      observation,
      labelFlow,
      nodeProfile,
      cat: (labelFlow.label || {}).category || 'unknown',
      pathLen: (resolved.node_path || []).length,
      hasTransform: (labelFlow.filter_events || []).length > 0
    });
  }
}
// Rank: longer path first, then has-transform, so the sample is representative.
candidates.sort((a, b) =>
  (b.pathLen - a.pathLen) || (Number(b.hasTransform) - Number(a.hasTransform)));

const packs = [];
const seenNodes = new Set();
const seenLabels = new Set();
for (const c of candidates) {
  if (seenNodes.has(c.observation.node_id) || seenLabels.has(c.cat)) continue;
  seenNodes.add(c.observation.node_id);
  seenLabels.add(c.cat);
  packs.push(buildEvidencePack({ fcg, observation: c.observation, labelFlow: c.labelFlow, nodeProfile: c.nodeProfile, context }));
  if (packs.length >= SAMPLE_COUNT) break;
}

// (1) The packs themselves.
const packOut = {
  source_fcg: path.basename(FCG_PATH),
  skill: fcg.meta?.skill_name,
  note: 'Flow-centric evidence packs. Necessity remains 3-component (local: action_input_need + receiver_semantic_need; global: task_need). This file is only the EVIDENCE provided to the judge.',
  sample_count: packs.length,
  evidence_packs: packs
};
fs.writeFileSync(PACK_OUT, JSON.stringify(packOut, null, 2));

// (2) The EXACT payload that goes to the model. buildJudgePayload internally
// assembles shared_context.task_memory (from FCG) and compacts/budgets packs.
const config = resolveJudgeOptions({});
const payload = buildJudgePayload(packs, {
  ...config,
  // task_memory is FCG-driven; judge needs fcg + the shared context.
  skillTaskMemory: require('../packages/skill-doe-analyzer/src/evidence-pack').buildSharedTaskMemory(fcg, context)
});

// The user message content is a JSON string; parse it so the dump is readable.
const userContent = JSON.parse(payload.messages[1].content);
const payloadOut = {
  note: 'EXACT content sent to the model (one batch of the sampled units). messages[0]=system instructions, messages[1].user_content=the structured payload. shared_context.task_memory is skill-level and shared across all units; each unit pack references relevant task nodes via task_memory_evidence_ids.',
  model: payload.model,
  temperature: payload.temperature,
  system_instructions: payload.messages[0].content,
  user_content: userContent
};
fs.writeFileSync(PAYLOAD_OUT, JSON.stringify(payloadOut, null, 2));

console.log('Wrote', packs.length, 'units');
console.log('  evidence packs :', PACK_OUT, `(${fs.statSync(PACK_OUT).size} bytes)`);
console.log('  model payload  :', PAYLOAD_OUT, `(${fs.statSync(PAYLOAD_OUT).size} bytes)`);
console.log('Units:', packs.map(p => `${p.unit_id} (${p.label?.category})`).join('\n       '));
console.log('task_memory nodes in payload:', userContent.shared_context.task_memory.task_context_node_count);
