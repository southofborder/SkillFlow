// Full-pipeline parity driver (M1 acceptance). Replays the REAL JS
// SkillFCGAnalyzer.analyze() sequence (index.js:156-452) on a real skill
// directory in RULE-ONLY mode (disableLlm=true, semanticLlm=false), then prints a
// normalized snapshot of the built+split graph. Paired with
// test_parity_pipeline.py. LLM is fully disabled so JS and Python are
// deterministic and bit-comparable on node ids / edges / crossing violations.
const path = require('path');
const ANALYZER = path.resolve(__dirname, '../../../skill-fcg-analyzer/src');

const { parseSkill, parseReadme, findExecutableFiles } = require(path.join(ANALYZER, 'parser/skill-parser'));
const { extractToolCalls } = require(path.join(ANALYZER, 'parser/tool-extractor'));
const {
  extractDocumentFlow, resolvePendingConstraints, newSemanticGateUsage, summarizeSemanticGateUsage
} = require(path.join(ANALYZER, 'parser/doc-flow-extractor'));
const { extractScriptFlow } = require(path.join(ANALYZER, 'parser/script-flow-extractor'));
const { buildDocumentationPlan } = require(path.join(ANALYZER, 'parser/document-context'));
const { analyzeTypeCompatibility } = require(path.join(ANALYZER, 'parser/type-analyzer'));
const { validatePairs } = require(path.join(ANALYZER, 'analyzer/llm-validator'));
const { buildFCG, removeDuplicateEdges } = require(path.join(ANALYZER, 'analyzer/fcg-builder'));
const { removeCycles, detectAndTagCycles, breakOnlyFake } = require(path.join(ANALYZER, 'analyzer/cycle-remover'));
const { classifyFeedbackEdges, resolveFeedbackLlmReview } = require(path.join(ANALYZER, 'analyzer/feedback-edge-classifier'));
const { splitGraphNodes, findCrossingViolations } = require(path.join(ANALYZER, 'analyzer/node-splitter'));
const { buildCallSiteMediation, buildEndpointMaps, expandAndMapEdges } = require(path.join(ANALYZER, 'analyzer/callsite-expander'));
const { createUserQuerySource } = require(path.join(ANALYZER, 'classifier/source-sink'));
const { buildNodeProfiles } = require(path.join(ANALYZER, 'security/node-profiler'));

// index.js private helpers (not exported) — replicated verbatim for fidelity.
function shouldAddImplicitToolToLlmEdge(tool) {
  if (!tool || !tool.name) return false;
  if (tool.callsite_id) return false;
  if (tool.excludeFromImplicitLlmEdge) return false;
  if (tool.excludeFromTypeAnalysis) return false;
  if (tool.name.startsWith('doc.')) return false;
  if (tool.name.startsWith('rule.')) return false;
  return true;
}
function limitDocumentFlow(documentFlow = {}, maxNodes = 80) {
  const nodes = documentFlow.nodes || [];
  const edges = documentFlow.edges || [];
  if (!Number.isInteger(maxNodes) || maxNodes <= 0 || nodes.length <= maxNodes) {
    return { nodes, edges, truncated: false };
  }
  const keptNodes = nodes.slice(0, maxNodes);
  const allowed = new Set();
  for (const node of keptNodes) { if (node.id) allowed.add(node.id); if (node.name) allowed.add(node.name); }
  allowed.add('user.query'); allowed.add('llm.inference');
  return { nodes: keptNodes, edges: edges.filter(e => allowed.has(e.source) && allowed.has(e.target)), truncated: true };
}
function limitMediation(mediation = {}, existingTools = [], maxNodes = 0) {
  const nodes = mediation.nodes || [];
  const edges = mediation.edges || [];
  if (!Number.isInteger(maxNodes) || maxNodes <= 0 || nodes.length <= maxNodes) {
    return { nodes, edges, truncated: false };
  }
  const keptNodes = nodes.slice(0, maxNodes);
  const allowed = new Set((existingTools || []).map(t => t.name).filter(Boolean));
  for (const node of keptNodes) { if (node.name) allowed.add(node.name); }
  return { nodes: keptNodes, edges: edges.filter(e => allowed.has(e.source) && allowed.has(e.target)), truncated: true };
}

function adjacencySnapshot(graph) {
  const out = {};
  for (const [k, v] of graph.adjacencyList.entries()) out[k] = v.slice();
  return out;
}

(async () => {
  const skillRootDir = process.argv[2];
  const mode = process.argv[3] || 'full';
  const cycleExpand = process.argv[4] !== '0';
  const maxDocFlowNodes = 0, maxCallsiteMediationNodes = 0, maxDependencyCandidates = 2000;
  const llmCfg = { disableLlm: true, semanticLlm: false };

  const skillData = parseSkill(skillRootDir);
  const readmeData = parseReadme(skillRootDir);
  const executableFiles = findExecutableFiles(skillRootDir);
  const documentationPlan = buildDocumentationPlan(skillData, readmeData, executableFiles);

  const tools = extractToolCalls(skillData, readmeData, executableFiles, {
    markdownDocs: documentationPlan.extractionDocs, rootDir: skillRootDir
  });

  const scriptFlow = await extractScriptFlow(executableFiles, {
    rootDir: skillRootDir, semanticLlm: false, disableLlm: true
  });
  if (scriptFlow.nodes.length > 0) tools.push(...scriptFlow.nodes);

  let documentFlowEdges = [...scriptFlow.edges];
  let semanticGateUsage = null;
  {
    const documentFlow = await extractDocumentFlow(skillData, readmeData, {
      extractionDocs: documentationPlan.extractionDocs,
      reviewDocs: documentationPlan.reviewDocs,
      documentationContext: documentationPlan.documentationContext,
      semanticLlm: false, disableLlm: true, maxDocFlowNodes
    });
    const limited = limitDocumentFlow(documentFlow, maxDocFlowNodes);
    if (limited.nodes.length > 0) tools.push(...limited.nodes);
    documentFlowEdges.push(...limited.edges);
    semanticGateUsage = documentFlow.semantic_gate_usage || null;
  }

  const userQueryNode = createUserQuerySource();
  tools.unshift(userQueryNode);

  const mediation = buildCallSiteMediation(tools);
  const limitedMediation = limitMediation(mediation, tools, maxCallsiteMediationNodes);
  if (limitedMediation.nodes.length > 0) { tools.push(...limitedMediation.nodes); documentFlowEdges.push(...limitedMediation.edges); }

  {
    const constraintGateUsage = newSemanticGateUsage();
    const resolved = await resolvePendingConstraints(tools, {
      disableLlm: true, semanticGateUsage: constraintGateUsage
    });
    if (resolved.addedNodes.length > 0) tools.push(...resolved.addedNodes);
    if (resolved.edges.length > 0) documentFlowEdges.push(...resolved.edges);
  }

  const dependencyCandidates = analyzeTypeCompatibility(tools, { maxCandidates: maxDependencyCandidates });

  const structuralDependencyEdges = [];
  const llmNodeIndex = tools.findIndex(t => t.name === 'llm.inference');
  if (llmNodeIndex !== -1) {
    structuralDependencyEdges.push({
      source: userQueryNode.name, target: tools[llmNodeIndex].name, type: 'data_dependency',
      confidence: 1.0, validation_method: 'dependency_structural',
      data_flow: { from_param: 'query_text', to_param: 'user_query', data_type: 'string' },
      semantic_reason: 'Implicit OpenClaw activation query flows to LLM inference'
    });
  }
  if (llmNodeIndex !== -1) {
    const llmNode = tools[llmNodeIndex];
    for (let i = 1; i < tools.length; i++) {
      if (i === llmNodeIndex) continue;
      const tool = tools[i];
      if (tool.name === 'llm.inference') continue;
      if (!shouldAddImplicitToolToLlmEdge(tool)) continue;
      const exists = structuralDependencyEdges.some(e => e.source === tool.name && e.target === llmNode.name);
      if (!exists) {
        structuralDependencyEdges.push({
          source: tool.name, target: llmNode.name, type: 'data_dependency',
          confidence: 0.9, validation_method: 'dependency_structural',
          data_flow: { from_param: 'skill_content', to_param: 'skill_content', data_type: 'string' },
          semantic_reason: 'Skill content is available to the global LLM context'
        });
      }
    }
  }

  let validatedEdges = [];
  if (mode !== 'quick') {
    validatedEdges = await validatePairs(dependencyCandidates, { disableLlm: true });
  } else {
    validatedEdges = dependencyCandidates.map((pair, index) => ({
      id: `edge_${String(index + 1).padStart(3, '0')}`,
      source: pair.source.name, target: pair.target.name, type: 'data_dependency',
      confidence: pair.confidence, validation_method: 'dependency_rule',
      data_flow: {
        from_param: pair.compatibleParams[0]?.fromParam || 'unknown',
        to_param: pair.compatibleParams[0]?.toParam || 'unknown',
        data_type: pair.compatibleParams[0]?.fromType || 'string'
      },
      semantic_reason: pair.candidate_reason || 'Sparse dependency rule'
    }));
  }
  validatedEdges = [...validatedEdges, ...structuralDependencyEdges];

  let deepModeEdges = [];
  // deep mode not exercised (mode is full/quick in the harness)

  const endpointMaps = buildEndpointMaps(tools);
  validatedEdges = expandAndMapEdges(validatedEdges, endpointMaps);
  deepModeEdges = expandAndMapEdges(deepModeEdges, endpointMaps);
  documentFlowEdges = expandAndMapEdges(documentFlowEdges, endpointMaps);

  let graph = buildFCG(tools, [...validatedEdges, ...deepModeEdges, ...documentFlowEdges]);
  graph = removeDuplicateEdges(graph);
  if (cycleExpand) graph = detectAndTagCycles(graph); else graph = removeCycles(graph);

  await classifyFeedbackEdges(graph, {
    disableLlm: true, feedbackLlmReview: resolveFeedbackLlmReview(undefined)
  });

  if (cycleExpand) graph = breakOnlyFake(graph);

  graph = splitGraphNodes(graph);

  const profiles = buildNodeProfiles(Array.from(graph.nodes.values()), graph.edges);
  const violations = findCrossingViolations(profiles, graph.nodes);

  process.stdout.write(JSON.stringify({
    node_count: graph.nodes.size,
    edge_count: graph.edges.length,
    node_ids: Array.from(graph.nodes.keys()),
    id_to_name: Object.fromEntries(Array.from(graph.nodes.values()).map(n => [n.id, n.name])),
    split_children: Array.from(graph.nodes.values())
      .filter(n => n.split_from)
      .map(n => ({ id: n.id, name: n.name, op: n.operationType, split_from: n.split_from })),
    edges: graph.edges.map(e => ({
      source: e.source, target: e.target, type: e.type,
      validation_method: e.validation_method,
      is_feedback_edge: Boolean(e.is_feedback_edge)
    })),
    adjacency: adjacencySnapshot(graph),
    crossing_violations: violations
  }));
})().catch(err => { process.stderr.write(String(err && err.stack || err)); process.exit(1); });
