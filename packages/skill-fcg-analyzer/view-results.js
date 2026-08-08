#!/usr/bin/env node

require('../../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const fs = require('fs');
const path = require('path');

/**
 * View analysis results from:
 * - FCG JSON (.json)
 * - Human-readable flow report (.flow.md / .md)
 * - Mermaid graph source (.flow.mmd / .mmd)
 *
 * Usage:
 *   node view-results.js [inputFile]
 *
 * Default:
 *   ./fcg.json
 */

function main() {
  const inputArg = process.argv[2] || 'fcg.json';
  const inputPath = path.resolve(inputArg);

  if (!fs.existsSync(inputPath)) {
    fail(`File not found: ${inputPath}`);
  }

  const ext = path.extname(inputPath).toLowerCase();
  const content = fs.readFileSync(inputPath, 'utf8');

  if (ext === '.json') {
    const fcg = JSON.parse(content);
    printFromJson(fcg, inputPath);
    return;
  }

  if (ext === '.md') {
    printFromFlowMarkdown(content, inputPath);
    return;
  }

  if (ext === '.mmd') {
    printFromMermaid(content, inputPath);
    return;
  }

  fail(`Unsupported file type: ${ext}. Use .json, .md, or .mmd`);
}

function printFromJson(fcg, inputPath) {
  console.log('=== Analysis Result (JSON) ===');
  console.log('File:', inputPath);
  console.log('Skill:', safe(fcg.meta?.skill_name));
  console.log('Version:', safe(fcg.meta?.skill_version));
  console.log('Mode:', safe(fcg.meta?.analysis_mode));
  console.log('Timestamp:', safe(fcg.meta?.analysis_timestamp));
  console.log('Nodes:', Number(fcg.statistics?.total_nodes || 0));
  console.log('Edges:', Number(fcg.statistics?.total_edges || 0));
  console.log('Source:', Number(fcg.statistics?.source_count || 0));
  console.log('Sink:', Number(fcg.statistics?.sink_count || 0));
  console.log('Source->Sink Paths:', Number(fcg.statistics?.source_to_sink_paths || 0));
  console.log('High Risk Paths:', Number(fcg.statistics?.high_risk_paths || 0));
  console.log('Source->Sink Paths (exact):', Number(fcg.paths?.source_to_sink_path_count_exact || fcg.paths?.path_compression?.exact_path_count || 0));

  const nodeById = new Map((fcg.nodes || []).map(node => [node.id, node]));

  console.log('\n=== Source Nodes ===');
  for (const source of fcg.source_sink?.sources || []) {
    const node = nodeById.get(source.node_id);
    console.log(`  ${source.node_id}: ${safe(node?.name)} | ${safe(source.reason)}`);
  }

  console.log('\n=== Sink Nodes ===');
  for (const sink of fcg.source_sink?.sinks || []) {
    const node = nodeById.get(sink.node_id);
    const critical = sink.is_critical ? ' | critical=true' : '';
    console.log(`  ${sink.node_id}: ${safe(node?.name)} | ${safe(sink.reason)}${critical}`);
  }

  console.log('\n=== Sample Edges (Top 10) ===');
  for (const edge of (fcg.edges || []).slice(0, 10)) {
    const src = nodeById.get(edge.source)?.name || edge.source;
    const tgt = nodeById.get(edge.target)?.name || edge.target;
    console.log(`  ${src} -> ${tgt} | type=${edge.type} | confidence=${formatNum(edge.confidence)}`);
  }

  console.log('\n=== Sample Paths (Top 5) ===');
  for (const pathItem of (fcg.paths?.source_to_sink_paths || []).slice(0, 5)) {
    const names = (pathItem.nodes || []).map(id => nodeById.get(id)?.name || id).join(' -> ');
    console.log(`  ${pathItem.path_id}: ${names} | risk=${safe(pathItem.risk_level)}`);
  }

  const clusters = fcg.paths?.path_clusters || [];
  console.log('\n=== Path Clusters (Top 10) ===');
  console.log(`Total clusters: ${clusters.length}`);
  for (const cluster of clusters.slice(0, 10)) {
    console.log(`  ${cluster.cluster_id}: count=${Number(cluster.path_count || 0)} | template=${safe(cluster.semantic_template)}`);
    console.log(`    representative=${safe(cluster.representative_path_id)} | docs=${summarize(cluster.involved_documents)} | triggers=${summarize(cluster.involved_triggers)} | policies=${summarize(cluster.involved_policies)}`);
  }

  const compression = fcg.paths?.path_compression || {};
  const pairSummary = compression.source_sink_pairs || [];
  console.log('\n=== Path Compression (Top 10 pairs) ===');
  console.log(`Compression nodes: ${Number((compression.compression_nodes || []).length)}`);
  console.log(`Compression edges: ${Number((compression.compression_edges || []).length)}`);
  console.log(`Source/Sink pairs: ${pairSummary.length}`);
  for (const pair of pairSummary.slice(0, 10)) {
    console.log(`  ${safe(pair.source_node)} -> ${safe(pair.sink_node)} | count=${Number(pair.path_count || 0)} | representative_len=${Number((pair.representative_path_nodes || []).length)}`);
  }

  console.log('\n=== Risks (Top 5) ===');
  for (const risk of (fcg.risks || []).slice(0, 5)) {
    console.log(`  ${risk.risk_id}: ${safe(risk.type)} | severity=${safe(risk.severity)}`);
    console.log(`    ${safe(risk.description)}`);
    if (risk.suggestion) {
      console.log(`    suggestion: ${safe(risk.suggestion)}`);
    }
  }

  const siblingFlowMd = inputPath.replace(/\.json$/i, '.flow.md');
  const siblingFlowMmd = inputPath.replace(/\.json$/i, '.flow.mmd');
  if (fs.existsSync(siblingFlowMd) || fs.existsSync(siblingFlowMmd)) {
    console.log('\n=== Related Flow Files ===');
    if (fs.existsSync(siblingFlowMd)) console.log(`  Markdown: ${siblingFlowMd}`);
    if (fs.existsSync(siblingFlowMmd)) console.log(`  Mermaid: ${siblingFlowMmd}`);
  }
}

function printFromFlowMarkdown(content, inputPath) {
  console.log('=== Analysis Result (Flow Markdown) ===');
  console.log('File:', inputPath);

  const skill = firstCapture(content, /- Skill:\s*\*\*(.+?)\*\*/);
  const version = firstCapture(content, /- Version:\s*\*\*(.+?)\*\*/);
  const mode = firstCapture(content, /- Analysis Mode:\s*\*\*(.+?)\*\*/);
  const generatedAt = firstCapture(content, /- Generated At:\s*\*\*(.+?)\*\*/);
  const analyzerTs = firstCapture(content, /- Analyzer Timestamp:\s*\*\*(.+?)\*\*/);

  if (skill) console.log('Skill:', skill);
  if (version) console.log('Version:', version);
  if (mode) console.log('Mode:', mode);
  if (generatedAt) console.log('Generated At:', generatedAt);
  if (analyzerTs) console.log('Analyzer Timestamp:', analyzerTs);

  const statsBlock = extractSectionJsonBlock(content, '## Statistics');
  if (statsBlock) {
    console.log('\n=== Statistics ===');
    try {
      const stats = JSON.parse(statsBlock);
      console.log(`Nodes: ${Number(stats.total_nodes || 0)}`);
      console.log(`Edges: ${Number(stats.total_edges || 0)}`);
      console.log(`Source: ${Number(stats.source_count || 0)}`);
      console.log(`Sink: ${Number(stats.sink_count || 0)}`);
      console.log(`Source->Sink Paths: ${Number(stats.source_to_sink_paths || 0)}`);
      console.log(`High Risk Paths: ${Number(stats.high_risk_paths || 0)}`);
    } catch (error) {
      console.log('Could not parse statistics JSON block.');
    }
  }

  const compressionTableLines = extractMarkdownTable(content, '## Path Compression Summary');
  if (compressionTableLines.length > 0) {
    console.log('\n=== Path Compression (Table Preview) ===');
    for (const line of compressionTableLines.slice(0, 8)) {
      console.log(`  ${line}`);
    }
  }

  const tableLines = extractMarkdownTable(content, '## Top Source->Sink Paths');
  if (tableLines.length > 0) {
    console.log('\n=== Top Source->Sink Paths (Table Preview) ===');
    for (const line of tableLines.slice(0, 8)) {
      console.log(`  ${line}`);
    }
  }

  const clusterTableLines = extractMarkdownTable(content, '## Path Clusters (Semantic Groups)');
  if (clusterTableLines.length > 0) {
    console.log('\n=== Path Clusters (Table Preview) ===');
    for (const line of clusterTableLines.slice(0, 8)) {
      console.log(`  ${line}`);
    }
  }

  const nodesBlock = extractSectionJsonBlock(content, '### Nodes');
  const edgesBlock = extractSectionJsonBlock(content, '### Edges');
  const pathsBlock = extractSectionJsonBlock(content, '### Paths');
  const risksBlock = extractSectionJsonBlock(content, '### Risks');

  console.log('\n=== Full Detail Blocks ===');
  console.log(`Nodes block: ${nodesBlock ? 'yes' : 'no'}`);
  console.log(`Edges block: ${edgesBlock ? 'yes' : 'no'}`);
  console.log(`Paths block: ${pathsBlock ? 'yes' : 'no'}`);
  console.log(`Risks block: ${risksBlock ? 'yes' : 'no'}`);

  const mermaidPath = inputPath.replace(/\.md$/i, '.mmd');
  if (fs.existsSync(mermaidPath)) {
    console.log('\nRelated Mermaid file:', mermaidPath);
  }
}

function printFromMermaid(content, inputPath) {
  console.log('=== Analysis Result (Mermaid) ===');
  console.log('File:', inputPath);

  const lines = content.split('\n');
  const nodeDefs = lines.filter(line => /^\s*node_[A-Za-z0-9_]+\["/.test(line));
  const edgeDefs = lines.filter(line => /node_[A-Za-z0-9_]+\s+[-=.]+>/.test(line));
  const sourceClasses = lines.filter(line => /^\s*class\s+node_[A-Za-z0-9_]+\s+source;/.test(line));
  const sinkClasses = lines.filter(line => /^\s*class\s+node_[A-Za-z0-9_]+\s+sink;/.test(line));
  const criticalClasses = lines.filter(line => /^\s*class\s+node_[A-Za-z0-9_]+\s+critical;/.test(line));

  console.log('Node definitions:', nodeDefs.length);
  console.log('Edge definitions:', edgeDefs.length);
  console.log('Source class count:', sourceClasses.length);
  console.log('Sink class count:', sinkClasses.length);
  console.log('Critical class count:', criticalClasses.length);

  console.log('\n=== Mermaid Preview (Top 30 Lines) ===');
  for (const line of lines.slice(0, 30)) {
    console.log(line);
  }

  const markdownPath = inputPath.replace(/\.mmd$/i, '.md');
  if (fs.existsSync(markdownPath)) {
    console.log('\nRelated Markdown report:', markdownPath);
  }
}

function extractSectionJsonBlock(markdown, heading) {
  const escaped = escapeRegex(heading);
  const sectionRegex = new RegExp(`${escaped}[\\s\\S]*?\\n\\n\\\`\\\`\\\`json\\n([\\s\\S]*?)\\n\\\`\\\`\\\``, 'm');
  const match = markdown.match(sectionRegex);
  return match ? match[1] : '';
}

function extractMarkdownTable(markdown, heading) {
  const escaped = escapeRegex(heading);
  const sectionRegex = new RegExp(`${escaped}[\\s\\S]*?(\\|.+\\|[\\s\\S]*?)(?:\\n\\n|$)`, 'm');
  const match = markdown.match(sectionRegex);
  if (!match) return [];
  return match[1]
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.startsWith('|'));
}

function firstCapture(text, regex) {
  const match = text.match(regex);
  return match ? match[1].trim() : '';
}

function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function formatNum(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '0.00';
  return n.toFixed(2);
}

function safe(value) {
  return String(value ?? '');
}

function summarize(values, limit = 2) {
  const list = Array.isArray(values) ? values : [];
  if (list.length === 0) return '-';
  if (list.length <= limit) return list.join(', ');
  return `${list.slice(0, limit).join(', ')} ... (+${list.length - limit})`;
}

function fail(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

main();
