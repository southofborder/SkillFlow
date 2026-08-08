#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function createFcgNodeObservationReport({ fcgPath, outputDir }) {
  const fcg = readJson(fcgPath);
  const outDir = path.resolve(outputDir || path.join(path.dirname(fcgPath), '..', 'reports', skillSlug(fcgPath)));
  const nodeById = new Map((fcg.nodes || []).map(node => [node.id, node]));
  const flowById = new Map((fcg.security_profile?.label_flows || []).map(flow => [flow.label_flow_id, flow]));
  const nodes = (fcg.nodes || []).map(node => naturalizeNode(node));
  const observations = (fcg.security_profile?.observations || []).map(observation => {
    const boundaryNode = nodeById.get(observation.node_id) || {};
    const flows = (observation.label_flow_ids || []).map(id => flowById.get(id)).filter(Boolean);
    return naturalizeObservation({ observation, node: boundaryNode, flows });
  });
  const audit = buildAudit(fcg, nodes, observations);
  const report = {
    generated_at: new Date().toISOString(),
    fcg_path: path.resolve(fcgPath),
    skill_name: fcg.meta?.skill_name || '',
    summary: {
      node_count: nodes.length,
      edge_count: (fcg.edges || []).length,
      observation_count: observations.length,
      label_flow_count: Number(fcg.security_profile?.statistics?.label_flow_count || 0),
      truncated: Boolean(fcg.security_profile?.statistics?.truncated),
      rule_trigger_policy_count: audit.rule_trigger_policy_count,
      skill_anchor_route_count: audit.skill_anchor_route_count,
      script_runtime_block_count: audit.script_runtime_block_count,
      template_placeholder_count: audit.template_placeholder_count
    },
    audit,
    nodes,
    observations
  };

  fs.mkdirSync(outDir, { recursive: true });
  const jsonPath = path.join(outDir, 'fcg-node-observation-report.json');
  const mdPath = path.join(outDir, 'fcg-node-observation-report.md');
  fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf-8');
  fs.writeFileSync(mdPath, renderMarkdown(report), 'utf-8');
  return { report, jsonPath, mdPath };
}

function naturalizeNode(node = {}) {
  const source = node.source_context || {};
  const actionEvidence = node.action_evidence || node.formal_semantics?.action_evidence || source.action_evidence || {};
  const semantics = node.formal_semantics || {};
  return {
    node_id: node.id || '',
    name: node.name || '',
    type: node.type || '',
    category: node.category || '',
    semantic_kind: node.semanticKind || '',
    source_role: source.source_role || '',
    file: node.location?.file || source.file || semantics.evidence?.file || '',
    line: node.location?.line || source.line || semantics.evidence?.line || null,
    section: node.location?.section || source.section || semantics.evidence?.section || '',
    source_text: source.source_line || node.instructionText || semantics.evidence?.source_line || semantics.evidence?.text || '',
    action_text: actionEvidence.snippet || actionEvidence.action || node.docAction || semantics.operation_type || '',
    inputs: semantics.inputs || node.signature?.input || node.input || [],
    outputs: semantics.outputs || node.signature?.output || node.output || [],
    targets: semantics.targets || [],
    effects: semantics.effects || [],
    semantic_gate: node.semantic_gate || null,
    evidence_method: semantics.evidence?.method || '',
    natural_language: buildNodeSentence(node, source, actionEvidence, semantics)
  };
}

function naturalizeObservation({ observation = {}, node = {}, flows = [] }) {
  const boundary = observation.boundary || {};
  const labels = Array.from(new Set(flows.map(flow => flow.label?.label).filter(Boolean))).sort();
  const source = node.source_context || {};
  return {
    observation_id: observation.observation_id || '',
    node_id: observation.node_id || '',
    node_name: observation.node_name || '',
    operation_type: observation.operation_type || '',
    action_step_id: observation.action_step_id || '',
    boundary,
    boundary_text: boundaryText(boundary),
    source_file: node.location?.file || source.file || '',
    source_line: node.location?.line || source.line || null,
    source_text: source.source_line || node.instructionText || node.formal_semantics?.evidence?.text || '',
    labels,
    label_flow_ids: observation.label_flow_ids || [],
    boundary_crossed_like: isBoundaryLike(boundary),
    natural_language: [
      `Observation ${observation.observation_id || ''} occurs at ${observation.node_name || observation.node_id || 'unknown node'}.`,
      `It exposes ${labels.length ? labels.join(', ') : 'no resolved labels'} through ${boundaryText(boundary)}.`
    ].join(' ')
  };
}

function buildNodeSentence(node, source, actionEvidence, semantics) {
  const file = node.location?.file || source.file || semantics.evidence?.file || 'unknown file';
  const line = node.location?.line || source.line || semantics.evidence?.line || '?';
  const action = actionEvidence.snippet || actionEvidence.action || node.docAction || semantics.operation_type || '';
  const sourceText = source.source_line || node.instructionText || semantics.evidence?.text || '';
  return `${node.id || ''} ${node.name || ''} comes from ${file}:${line}; action="${action}"; source="${sourceText}".`;
}

function buildAudit(fcg, nodes, observations) {
  const ruleTriggerPolicy = nodes.filter(node => /^rule\.(trigger|policy)\./.test(node.name));
  const skillAnchorRoutes = nodes.filter(node => /skill_anchor_route/.test([
    node.evidence_method,
    JSON.stringify(node.semantic_gate || ''),
    node.source_text,
    node.action_text
  ].join(' ')));
  const scriptRuntimeBlocks = nodes.filter(node => node.source_role === 'runtime_implementation' || /script_flow_runtime_block/.test(JSON.stringify(node)));
  const templatePlaceholders = nodes.filter(node => /assets[\\/]+SKILL-TEMPLATE\.md/i.test(node.file) && /\b(helper|validate)\.sh\b/i.test(`${node.name} ${node.source_text} ${node.action_text}`));
  return {
    rule_trigger_policy_count: ruleTriggerPolicy.length,
    skill_anchor_route_count: skillAnchorRoutes.length,
    script_runtime_block_count: scriptRuntimeBlocks.length,
    template_placeholder_count: templatePlaceholders.length,
    observation_count_below_rule_baseline_899: observations.length < 899,
    notes: [
      ruleTriggerPolicy.length ? 'rule.trigger/policy nodes still exist' : 'no rule.trigger/rule.policy pseudo nodes found',
      skillAnchorRoutes.length ? 'SKILL.md anchor route nodes found' : 'no SKILL.md anchor route nodes found',
      scriptRuntimeBlocks.length ? 'script runtime semantic blocks found' : 'no script runtime semantic blocks found',
      templatePlaceholders.length ? 'template placeholder command nodes found' : 'no template placeholder command nodes found'
    ]
  };
}

function renderMarkdown(report) {
  const lines = [];
  lines.push('# FCG Node and Observation Report');
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  for (const [key, value] of Object.entries(report.summary || {})) {
    lines.push(`- ${key}: ${value}`);
  }
  lines.push('');
  lines.push('## Audit Notes');
  lines.push('');
  for (const note of report.audit?.notes || []) lines.push(`- ${note}`);
  lines.push('');
  lines.push('## Nodes');
  lines.push('');
  for (const node of report.nodes || []) {
    lines.push(`### ${escapeMarkdown(node.node_id)} ${escapeMarkdown(node.name)}`);
    lines.push(`- Source: ${escapeMarkdown([node.file, node.line].filter(Boolean).join(':'))}`);
    lines.push(`- Role: ${escapeMarkdown(node.source_role || '')}`);
    lines.push(`- Action: ${escapeMarkdown(node.action_text || '')}`);
    lines.push(`- Source text: ${escapeMarkdown(node.source_text || '')}`);
    lines.push(`- Inputs: ${escapeMarkdown(shortJson(node.inputs))}`);
    lines.push(`- Outputs: ${escapeMarkdown(shortJson(node.outputs))}`);
    lines.push(`- Targets: ${escapeMarkdown(shortJson(node.targets))}`);
    lines.push(`- Effects: ${escapeMarkdown(shortJson(node.effects))}`);
    lines.push('');
  }
  lines.push('## Observations');
  lines.push('');
  for (const observation of report.observations || []) {
    lines.push(`### ${escapeMarkdown(observation.observation_id)} ${escapeMarkdown(observation.node_name)}`);
    lines.push(`- Boundary: ${escapeMarkdown(observation.boundary_text)}`);
    lines.push(`- Source: ${escapeMarkdown([observation.source_file, observation.source_line].filter(Boolean).join(':'))}`);
    lines.push(`- Labels: ${escapeMarkdown((observation.labels || []).join(', '))}`);
    lines.push(`- Label flows: ${escapeMarkdown(String((observation.label_flow_ids || []).length))}`);
    lines.push(`- Summary: ${escapeMarkdown(observation.natural_language)}`);
    lines.push('');
  }
  return `${lines.join('\n')}\n`;
}

function boundaryText(boundary = {}) {
  return [
    boundary.trust_boundary || '',
    boundary.receiver_scope || '',
    boundary.data_surface || '',
    boundary.retention_scope || ''
  ].filter(Boolean).join(' / ') || 'local/internal boundary';
}

function isBoundaryLike(boundary = {}) {
  return /external|provider|persistent|user/i.test(Object.values(boundary).join(' '));
}

function shortJson(value) {
  const text = JSON.stringify(value || []);
  return text.length > 280 ? `${text.slice(0, 277)}...` : text;
}

function skillSlug(fcgPath) {
  return path.basename(fcgPath).replace(/-fcg\.json$/i, '').replace(/[^\w.-]+/g, '_');
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(file), 'utf-8'));
}

function escapeMarkdown(value) {
  return String(value || '').replace(/[<>]/g, '');
}

if (require.main === module) {
  const args = parseArgs(process.argv.slice(2));
  if (!args.fcg) {
    console.error('Usage: node fcg-node-observation-report.js --fcg <fcg.json> --output <dir>');
    process.exit(1);
  }
  const written = createFcgNodeObservationReport({ fcgPath: args.fcg, outputDir: args.output });
  console.log(`FCG node/observation report written: ${written.mdPath}`);
  console.log(`FCG node/observation JSON written: ${written.jsonPath}`);
}

function parseArgs(args) {
  const options = {};
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--fcg' && args[i + 1]) {
      options.fcg = args[i + 1];
      i += 1;
    } else if (args[i] === '--output' && args[i + 1]) {
      options.output = args[i + 1];
      i += 1;
    }
  }
  return options;
}

module.exports = {
  createFcgNodeObservationReport
};
