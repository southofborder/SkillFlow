#!/usr/bin/env node

require('../../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');
const { SkillFCGAnalyzer } = require('../src/index');
const { saveToJson } = require('../src/output/json-generator');
const { saveFlowchartArtifacts, deriveFlowchartPaths } = require('../src/output/flowchart-generator');
const { createFcgNodeObservationReport } = require('./fcg-node-observation-report');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const ZIP = path.join(ROOT, 'results', 'debug-k20-c8', 'zips', '00001_self-improving-agent_3.0.21.zip');
const OUT = path.join(ROOT, 'results', 'debug-k20-c8', 'fcg', 'skills', 'skill_0001-00001_self-improving-agent_3.0.21-fcg.json');
const REPORT_DIR = path.join(ROOT, 'results', 'debug-k20-c8', 'fcg', 'reports', 'skill_0001');

async function main() {
  if (!fs.existsSync(ZIP)) throw new Error(`Zip not found: ${ZIP}`);
  if (!String(process.env.LLM_API_KEY || '').trim()) throw new Error('LLM_API_KEY not found in environment or .env');
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.mkdirSync(REPORT_DIR, { recursive: true });

  const timing = createTimingCapture();
  const restore = timing.install();
  const started = Date.now();
  let result = null;
  try {
    const analyzer = new SkillFCGAnalyzer({
      mode: 'full',
      semanticLlm: true,
      llmApiKey: process.env.LLM_API_KEY || '',
      llmProvider: process.env.LLM_PROVIDER || 'openai',
      llmModel: process.env.LLM_MODEL || 'gpt-5.5',
      llmEndpoint: process.env.LLM_ENDPOINT || '',
      llmTimeout: 60000
    });
    result = await analyzer.analyze(ZIP);
  } finally {
    restore();
  }

  const flowPaths = deriveFlowchartPaths(OUT, '');
  saveToJson(result, OUT);
  saveFlowchartArtifacts(result, flowPaths.markdownPath, flowPaths.mermaidPath);
  const reportWritten = createFcgNodeObservationReport({ fcgPath: OUT, outputDir: REPORT_DIR });

  const summary = buildSummary(result, {
    wall_ms: Date.now() - started,
    stages: timing.stages,
    output_path: OUT,
    flow_markdown_path: flowPaths.markdownPath,
    flow_mermaid_path: flowPaths.mermaidPath,
    report_markdown_path: reportWritten.mdPath,
    report_json_path: reportWritten.jsonPath
  });
  const timingPath = path.join(REPORT_DIR, 'fcg-llm-timing.json');
  fs.writeFileSync(timingPath, `${JSON.stringify(summary, null, 2)}\n`, 'utf-8');
  console.log(JSON.stringify(summary, null, 2));
}

function createTimingCapture() {
  const originalLog = console.log;
  const originalWarn = console.warn;
  const start = Date.now();
  const entries = [];
  let last = start;
  function record(kind, args) {
    const message = args.map(arg => typeof arg === 'string' ? arg : JSON.stringify(arg)).join(' ');
    const now = Date.now();
    entries.push({
      kind,
      message,
      elapsed_ms: now - start,
      delta_ms: now - last
    });
    last = now;
  }
  return {
    stages: entries,
    install() {
      console.log = (...args) => {
        record('log', args);
        originalLog(...args);
      };
      console.warn = (...args) => {
        record('warn', args);
        originalWarn(...args);
      };
      return () => {
        console.log = originalLog;
        console.warn = originalWarn;
      };
    }
  };
}

function buildSummary(result, meta = {}) {
  const jsonBytes = Buffer.byteLength(JSON.stringify(result));
  const security = result.security_profile || {};
  const nodes = result.nodes || [];
  const labelFlows = security.label_flows || [];
  return {
    generated_at: new Date().toISOString(),
    wall_seconds: round(meta.wall_ms / 1000),
    stages: meta.stages,
    output_path: meta.output_path,
    report_markdown_path: meta.report_markdown_path,
    report_json_path: meta.report_json_path,
    flow_markdown_path: meta.flow_markdown_path,
    flow_mermaid_path: meta.flow_mermaid_path,
    size_mb: round(jsonBytes / 1024 / 1024),
    section_size_mb: {
      nodes: jsonMb(result.nodes),
      edges: jsonMb(result.edges),
      label_flows: jsonMb(security.label_flows),
      flow_states: jsonMb(security.flow_states),
      provenance_store: jsonMb(security.provenance_store),
      provenance_graph: jsonMb(security.provenance_graph),
      observations: jsonMb(security.observations)
    },
    statistics: {
      nodes: result.statistics?.total_nodes || 0,
      edges: result.statistics?.total_edges || 0,
      observations: security.statistics?.observation_count || 0,
      label_flows: security.statistics?.label_flow_count || 0,
      truncated: Boolean(security.statistics?.truncated),
      dependency_candidates: result.statistics?.dependency_candidate_count || 0,
      dependency_llm_candidates: result.statistics?.dependency_llm_candidate_count || 0,
      dependency_llm_cache_hits: result.statistics?.dependency_llm_cache_hit_count || 0
    },
    audit: {
      rule_trigger_policy_nodes: nodes.filter(node => /^rule\.(trigger|policy)\./.test(node.name || '')).length,
      skill_anchor_routes: nodes.filter(node => String(node.formal_semantics?.evidence?.method || '').includes('skill_anchor_route')).length,
      script_runtime_blocks: nodes.filter(node => node.source_context?.action_evidence?.extraction_method === 'script_flow_runtime_block').length,
      label_flows_with_full_path_fields: labelFlows.filter(flow => flow.node_path || flow.node_names || flow.edge_path).length
    }
  };
}

function jsonMb(value) {
  return round(Buffer.byteLength(JSON.stringify(value || null)) / 1024 / 1024);
}

function round(value) {
  return Number(value.toFixed(2));
}

if (require.main === module) {
  main().catch(error => {
    console.error(error && error.stack || error);
    process.exit(1);
  });
}

module.exports = {
  main,
  buildSummary
};
