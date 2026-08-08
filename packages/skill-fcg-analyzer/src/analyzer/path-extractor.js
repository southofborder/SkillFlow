/**
 * Path Extractor
 * Extracts Source->Sink paths and provides semantic clustering.
 */

/**
 * Find BFS paths from start to end with length and count limits.
 *
 * @param {Object} graph
 * @param {string} startId
 * @param {string} endId
 * @param {number} maxPaths
 * @param {Object} options
 * @returns {Array}
 */
function findBFSPaths(graph, startId, endId, maxPaths = 500, options = {}) {
  const paths = [];
  const queue = [{ nodeId: startId, path: [startId] }];
  const maxPathLength = normalizeLimit(options.maxPathLength, 18);
  const maxStateExpansions = normalizeLimit(options.maxStateExpansions, 15000);
  let queueIndex = 0;
  let expansions = 0;

  while (queueIndex < queue.length && paths.length < maxPaths && expansions < maxStateExpansions) {
    const { nodeId, path } = queue[queueIndex++];
    expansions += 1;

    if (nodeId === endId) {
      paths.push(path);
      continue;
    }

    if (path.length >= maxPathLength) {
      continue;
    }

    const neighbors = graph.adjacencyList.get(nodeId) || [];
    for (const neighborId of neighbors) {
      if (!path.includes(neighborId)) {
        queue.push({ nodeId: neighborId, path: [...path, neighborId] });
      }
    }
  }

  return paths;
}

/**
 * Calculate risk level for a path.
 *
 * @param {Array} pathNodes
 * @param {Object} graph
 * @returns {string}
 */
function calculateRisk(pathNodes, graph) {
  let riskScore = 0;

  riskScore += pathNodes.length * 10;

  for (const nodeId of pathNodes) {
    const node = graph.getNode(nodeId);
    const lowerName = String(node?.name || '').toLowerCase();
    if (node && (lowerName.includes('exec') || lowerName.includes('send'))) {
      riskScore += 30;
    }
    if (node && node.isCritical) {
      riskScore += 50;
    }
  }

  const modules = new Set(pathNodes.map(id => {
    const node = graph.getNode(id);
    return node ? node.name.split('.')[0] : 'unknown';
  }));
  riskScore += modules.size * 15;

  if (riskScore >= 80) return 'critical';
  if (riskScore >= 50) return 'high';
  if (riskScore >= 20) return 'medium';
  return 'low';
}

/**
 * Analyze data flow along a path.
 *
 * @param {Array} pathNodes
 * @param {Object} graph
 * @returns {string}
 */
function analyzeDataFlow(pathNodes, graph) {
  const nodes = pathNodes.map(id => graph.getNode(id)).filter(Boolean);

  if (nodes.length < 2) return 'No data flow';

  const firstNode = nodes[0];
  const lastNode = nodes[nodes.length - 1];

  const sourceData = Object.keys(firstNode.output || {}).join(', ') || 'unknown';
  const sinkData = Object.keys(lastNode.input || {}).join(', ') || 'unknown';

  return `${sourceData} -> ${sinkData}`;
}

/**
 * Extract all reachable paths (not only source->sink) under global budget.
 *
 * @param {Object} graph
 * @param {Object} options
 * @returns {Array}
 */
function extractAllPaths(graph, options = {}) {
  const allPaths = [];
  const seen = new Set();
  const nodes = graph.getAllNodes();
  const maxAllPathsTotal = normalizeLimit(options.maxAllPathsTotal, 2000);
  const maxNeighborPaths = normalizeLimit(options.maxNeighborPaths, 1);
  const maxPathLength = normalizeLimit(options.maxPathLength, 12);
  const maxStateExpansionsPerSearch = normalizeLimit(options.maxStateExpansionsPerSearch, 1500);

  outer:
  for (const node of nodes) {
    const neighbors = graph.getNeighbors(node.id) || [];

    for (const neighborId of neighbors) {
      if (allPaths.length >= maxAllPathsTotal) break outer;

      const remaining = maxAllPathsTotal - allPaths.length;
      const paths = findBFSPaths(
        graph,
        node.id,
        neighborId,
        Math.min(maxNeighborPaths, remaining),
        { maxPathLength, maxStateExpansions: maxStateExpansionsPerSearch }
      );

      for (const p of paths) {
        const key = p.join('->');
        if (!seen.has(key)) {
          seen.add(key);
          allPaths.push(p);
        }
        if (allPaths.length >= maxAllPathsTotal) break;
      }
    }
  }

  return allPaths.map((path, index) => ({
    path_id: `all_path_${String(index + 1).padStart(3, '0')}`,
    nodes: path,
    length: path.length,
    has_source: graph.getNode(path[0])?.category === 'Source',
    has_sink: graph.getNode(path[path.length - 1])?.category === 'Sink',
    is_complete: graph.getNode(path[0])?.category === 'Source' &&
                 graph.getNode(path[path.length - 1])?.category === 'Sink'
  }));
}

function buildReverseAdjacency(edges) {
  const reverse = new Map();
  for (const edge of edges || []) {
    if (!edge?.source || !edge?.target) continue;
    if (!reverse.has(edge.target)) reverse.set(edge.target, []);
    reverse.get(edge.target).push(edge.source);
  }
  return reverse;
}

function traverseReachable(adjacency, starts) {
  const visited = new Set();
  const queue = [...(starts || [])];

  while (queue.length > 0) {
    const nodeId = queue.shift();
    if (!nodeId || visited.has(nodeId)) continue;
    visited.add(nodeId);

    const neighbors = adjacency.get(nodeId) || [];
    for (const next of neighbors) {
      if (!visited.has(next)) queue.push(next);
    }
  }

  return visited;
}

function buildRelevantSubgraph(graph, relevantNodes) {
  const outgoing = new Map();
  const incoming = new Map();
  const allEdges = graph.getAllEdges ? graph.getAllEdges() : [];

  for (const nodeId of relevantNodes) {
    outgoing.set(nodeId, []);
    incoming.set(nodeId, []);
  }

  for (const edge of allEdges) {
    if (!edge?.source || !edge?.target) continue;
    if (!relevantNodes.has(edge.source) || !relevantNodes.has(edge.target)) continue;
    outgoing.get(edge.source).push(edge.target);
    incoming.get(edge.target).push(edge.source);
  }

  return {
    nodes: relevantNodes,
    outgoing,
    incoming
  };
}

function identifyJunctionNodes(subgraph, sourceSet, sinkSet) {
  const junctions = new Set();

  for (const nodeId of subgraph.nodes) {
    const indegree = (subgraph.incoming.get(nodeId) || []).length;
    const outdegree = (subgraph.outgoing.get(nodeId) || []).length;

    if (sourceSet.has(nodeId) || sinkSet.has(nodeId) || indegree !== 1 || outdegree !== 1) {
      junctions.add(nodeId);
    }
  }

  return junctions;
}

function buildCompressionNodes(graph, junctions) {
  const nodes = [];
  for (const nodeId of junctions) {
    const node = graph.getNode(nodeId);
    nodes.push({
      id: `cnode_${nodeId}`,
      original_node_id: nodeId,
      original_name: node?.name || nodeId,
      member_node_ids: [nodeId],
      location: node?.location || { file: '', line: 0, section: '' }
    });
  }

  nodes.sort((a, b) => a.id.localeCompare(b.id));
  return nodes;
}

function buildCompressionEdges(subgraph, junctions) {
  const edges = [];
  const seen = new Set();
  const outgoing = subgraph.outgoing;

  for (const sourceJunction of junctions) {
    const neighbors = outgoing.get(sourceJunction) || [];
    for (const neighbor of neighbors) {
      const chain = [sourceJunction];
      const visitedInWalk = new Set([sourceJunction]);
      let current = neighbor;

      while (current && !junctions.has(current)) {
        if (visitedInWalk.has(current)) break;
        visitedInWalk.add(current);
        chain.push(current);

        const nexts = outgoing.get(current) || [];
        if (nexts.length !== 1) break;
        current = nexts[0];
      }

      if (!current) continue;
      if (!chain.includes(current)) {
        chain.push(current);
      }

      const targetJunction = chain[chain.length - 1];
      if (!junctions.has(targetJunction)) continue;

      const middle = chain.slice(1, -1);
      const key = `${sourceJunction}->${targetJunction}:${chain.join('>')}`;
      if (seen.has(key)) continue;
      seen.add(key);

      edges.push({
        id: `cedge_${String(edges.length + 1).padStart(4, '0')}`,
        source: sourceJunction,
        target: targetJunction,
        source_compression_node: `cnode_${sourceJunction}`,
        target_compression_node: `cnode_${targetJunction}`,
        member_node_ids: [...chain],
        middle_node_ids: middle,
        edge_count: chain.length - 1
      });
    }
  }

  return edges;
}

function buildCompressionAdjacency(compressionEdges) {
  const adj = new Map();
  for (const edge of compressionEdges || []) {
    if (!adj.has(edge.source)) adj.set(edge.source, []);
    adj.get(edge.source).push(edge.id);
  }
  return adj;
}

function topoSortCompression(compressionNodes, compressionEdges) {
  const indegree = new Map();
  const outgoing = new Map();

  for (const node of compressionNodes || []) {
    indegree.set(node.original_node_id, 0);
    outgoing.set(node.original_node_id, []);
  }

  for (const edge of compressionEdges || []) {
    if (!indegree.has(edge.source)) {
      indegree.set(edge.source, 0);
      outgoing.set(edge.source, []);
    }
    if (!indegree.has(edge.target)) {
      indegree.set(edge.target, 0);
      outgoing.set(edge.target, []);
    }

    indegree.set(edge.target, (indegree.get(edge.target) || 0) + 1);
    outgoing.get(edge.source).push(edge.target);
  }

  const queue = Array.from(indegree.entries())
    .filter(([, deg]) => deg === 0)
    .map(([nodeId]) => nodeId);

  const order = [];
  while (queue.length > 0) {
    const nodeId = queue.shift();
    order.push(nodeId);

    for (const next of outgoing.get(nodeId) || []) {
      const deg = (indegree.get(next) || 0) - 1;
      indegree.set(next, deg);
      if (deg === 0) queue.push(next);
    }
  }

  // Fallback for disconnected/cycle remnants.
  if (order.length < indegree.size) {
    for (const nodeId of indegree.keys()) {
      if (!order.includes(nodeId)) order.push(nodeId);
    }
  }

  return order;
}

function computeSourceSinkPairCounts(compressionNodes, compressedAdj, topo, sources, sinks, compressionEdgeById) {
  const sinkSet = new Set(sinks || []);
  const nodeSet = new Set((compressionNodes || []).map(n => n.original_node_id));
  const pairs = [];

  for (const source of sources || []) {
    if (!nodeSet.has(source)) continue;

    const dp = new Map();
    dp.set(source, 1);

    for (const nodeId of topo) {
      const current = dp.get(nodeId) || 0;
      if (current <= 0) continue;

      for (const edgeId of compressedAdj.get(nodeId) || []) {
        const edge = compressionEdgeById.get(edgeId);
        if (!edge) continue;
        const nextCount = safeAddCount(dp.get(edge.target) || 0, current);
        dp.set(edge.target, nextCount);
      }
    }

    for (const sink of sinkSet) {
      if (source === sink) continue;
      const count = dp.get(sink) || 0;
      if (count <= 0) continue;
      pairs.push({
        source_node: source,
        sink_node: sink,
        path_count: count
      });
    }
  }

  return pairs;
}

function findRepresentativeCompressedPath(sourceNode, sinkNode, compressedAdj, compressionEdgeById) {
  const queue = [{ node: sourceNode, edgePath: [] }];
  const visited = new Set([sourceNode]);
  let queueIndex = 0;

  while (queueIndex < queue.length) {
    const { node, edgePath } = queue[queueIndex++];
    if (node === sinkNode) {
      return edgePath;
    }

    for (const edgeId of compressedAdj.get(node) || []) {
      const edge = compressionEdgeById.get(edgeId);
      if (!edge) continue;
      if (visited.has(edge.target)) continue;
      visited.add(edge.target);
      queue.push({
        node: edge.target,
        edgePath: [...edgePath, edgeId]
      });
    }
  }

  return [];
}

function expandRepresentativePathNodes(edgeIds, compressionEdges) {
  if (!Array.isArray(edgeIds) || edgeIds.length === 0) return [];
  const edgeMap = new Map((compressionEdges || []).map(edge => [edge.id, edge]));
  const expanded = [];

  for (const edgeId of edgeIds) {
    const edge = edgeMap.get(edgeId);
    if (!edge) continue;
    const members = edge.member_node_ids || [];
    for (let i = 0; i < members.length; i++) {
      const nodeId = members[i];
      if (expanded.length > 0 && expanded[expanded.length - 1] === nodeId) continue;
      expanded.push(nodeId);
    }
  }

  return expanded;
}

function safeAddCount(a, b) {
  const sum = Number(a || 0) + Number(b || 0);
  if (!Number.isFinite(sum)) return Number.MAX_SAFE_INTEGER;
  return Math.min(Number.MAX_SAFE_INTEGER, sum);
}

/**
 * Cluster Source->Sink paths by semantic workflow template.
 *
 * @param {Array} sourceToSinkPaths
 * @param {Object} graph
 * @returns {Array}
 */
function clusterSourceToSinkPaths(sourceToSinkPaths, graph) {
  const clusters = new Map();

  for (const pathItem of sourceToSinkPaths || []) {
    const nodeIds = pathItem.nodes || [];
    const nodeInfos = nodeIds.map(nodeId => graph.getNode(nodeId) || { id: nodeId, name: nodeId });
    const nodeNames = nodeInfos.map(node => node.name || node.id || 'unknown');
    const semanticRoles = nodeNames.map(name => semanticRoleForNodeName(name));
    const template = semanticRoles.join(' -> ');

    if (!clusters.has(template)) {
      clusters.set(template, createClusterRecord(template));
    }

    const cluster = clusters.get(template);
    updateClusterRecord(cluster, pathItem, nodeIds, nodeNames, nodeInfos);
  }

  return Array.from(clusters.values())
    .sort((a, b) => {
      if (b.path_count !== a.path_count) return b.path_count - a.path_count;
      if (a.semantic_template !== b.semantic_template) {
        return a.semantic_template.localeCompare(b.semantic_template);
      }
      return a.representative_path_id.localeCompare(b.representative_path_id);
    })
    .map((cluster, index) => finalizeClusterRecord(cluster, index + 1));
}

function createClusterRecord(template) {
  return {
    semantic_template: template,
    path_count: 0,
    risk_distribution: {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    },
    path_ids: [],
    representative_path_id: '',
    representative_path_nodes: [],
    representative_path_names: [],
    source_nodes_set: new Set(),
    sink_nodes_set: new Set(),
    source_names_set: new Set(),
    sink_names_set: new Set(),
    modules_set: new Set(),
    triggers_set: new Set(),
    policies_set: new Set(),
    docs_set: new Set()
  };
}

function updateClusterRecord(cluster, pathItem, nodeIds, nodeNames, nodeInfos) {
  cluster.path_count += 1;
  cluster.path_ids.push(pathItem.path_id);

  const risk = String(pathItem.risk_level || 'low').toLowerCase();
  if (Object.prototype.hasOwnProperty.call(cluster.risk_distribution, risk)) {
    cluster.risk_distribution[risk] += 1;
  } else {
    cluster.risk_distribution.low += 1;
  }

  const sourceId = String(pathItem.source_node || '');
  const sinkId = String(pathItem.sink_node || '');
  const sourceName = nodeNames[0] || sourceId;
  const sinkName = nodeNames[nodeNames.length - 1] || sinkId;

  if (sourceId) cluster.source_nodes_set.add(sourceId);
  if (sinkId) cluster.sink_nodes_set.add(sinkId);
  if (sourceName) cluster.source_names_set.add(sourceName);
  if (sinkName) cluster.sink_names_set.add(sinkName);

  for (let i = 0; i < nodeNames.length; i++) {
    const nodeInfo = nodeInfos[i] || {};
    const nodeName = nodeNames[i];
    const normalized = String(nodeName || '');
    const moduleName = normalized.split('.')[0] || 'unknown';
    cluster.modules_set.add(moduleName);

    if (normalized.startsWith('rule.trigger.')) cluster.triggers_set.add(normalized);
    if (normalized.startsWith('rule.policy.')) cluster.policies_set.add(normalized);

    const docRef = String(nodeInfo.docRef || '').trim();
    if (docRef) {
      cluster.docs_set.add(docRef);
      continue;
    }

    if (normalized.startsWith('doc.file.') || normalized.startsWith('doc.step.') || normalized.startsWith('doc.op.')) {
      cluster.docs_set.add(normalized);
    }
  }

  const shouldReplaceRepresentative =
    !cluster.representative_path_id ||
    nodeIds.length < cluster.representative_path_nodes.length ||
    (
      nodeIds.length === cluster.representative_path_nodes.length &&
      String(pathItem.path_id || '').localeCompare(String(cluster.representative_path_id || '')) < 0
    );

  if (shouldReplaceRepresentative) {
    cluster.representative_path_id = pathItem.path_id || '';
    cluster.representative_path_nodes = [...nodeIds];
    cluster.representative_path_names = [...nodeNames];
  }
}

function finalizeClusterRecord(cluster, clusterNumber) {
  return {
    cluster_id: `cluster_${String(clusterNumber).padStart(3, '0')}`,
    semantic_template: cluster.semantic_template,
    path_count: cluster.path_count,
    risk_distribution: cluster.risk_distribution,
    representative_path_id: cluster.representative_path_id,
    representative_path_nodes: cluster.representative_path_nodes,
    representative_path_names: cluster.representative_path_names,
    source_nodes: Array.from(cluster.source_nodes_set).sort(),
    sink_nodes: Array.from(cluster.sink_nodes_set).sort(),
    source_names: Array.from(cluster.source_names_set).sort(),
    sink_names: Array.from(cluster.sink_names_set).sort(),
    involved_modules: Array.from(cluster.modules_set).sort(),
    involved_triggers: Array.from(cluster.triggers_set).sort(),
    involved_policies: Array.from(cluster.policies_set).sort(),
    involved_documents: Array.from(cluster.docs_set).sort(),
    path_ids: [...cluster.path_ids]
  };
}

function semanticRoleForNodeName(nodeName) {
  const normalized = String(nodeName || '').toLowerCase();
  if (!normalized) return 'unknown';

  if (normalized === 'user.query') return 'user.query';
  if (normalized === 'llm.inference') return 'llm.inference';
  if (normalized.startsWith('rule.trigger.')) return 'rule.trigger';
  if (normalized.startsWith('rule.policy.')) return 'rule.policy';
  if (normalized.startsWith('doc.op.')) return 'doc.op';
  if (normalized.startsWith('doc.step.')) return 'doc.step';
  if (normalized.startsWith('doc.file.')) return 'doc.file';
  if (normalized.startsWith('doc.')) return 'doc';

  const parts = normalized.split('.');
  if (parts.length >= 2) return `${parts[0]}.${parts[1]}`;
  return parts[0];
}

function buildCandidatePairs(sources, sinks, preferredPairs) {
  const pairs = [];
  const seen = new Set();

  if (Array.isArray(preferredPairs) && preferredPairs.length > 0) {
    for (const pair of preferredPairs) {
      const source = String(pair?.source || pair?.source_node || '').trim();
      const sink = String(pair?.sink || pair?.sink_node || '').trim();
      if (!source || !sink || source === sink) continue;

      const key = `${source}->${sink}`;
      if (seen.has(key)) continue;
      seen.add(key);
      pairs.push({ source, sink });
    }

    if (pairs.length > 0) {
      return pairs;
    }
  }

  for (const source of sources || []) {
    for (const sink of sinks || []) {
      if (!source || !sink || source === sink) continue;
      const key = `${source}->${sink}`;
      if (seen.has(key)) continue;
      seen.add(key);
      pairs.push({ source, sink });
    }
  }

  return pairs;
}

function normalizeLimit(value, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0) return fallback;
  return Math.floor(n);
}

module.exports = {
  findBFSPaths,
  calculateRisk,
  analyzeDataFlow,
  extractAllPaths,
  clusterSourceToSinkPaths
};
