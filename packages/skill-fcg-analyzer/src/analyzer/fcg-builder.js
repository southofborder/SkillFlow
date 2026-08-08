/**
 * Function Call Graph (FCG) Builder
 * Constructs a directed graph from validated dependency edges
 */

class FunctionCallGraph {
  constructor() {
    this.nodes = new Map();  // node_id → node
    this.edges = [];         // [{ source, target, confidence, ... }]
    this.adjacencyList = new Map();  // node_id → [neighbor_ids]
  }

  /**
   * Add a node to the graph
   * @param {Object} node - Node object
   */
  addNode(node) {
    this.nodes.set(node.id, node);
    if (!this.adjacencyList.has(node.id)) {
      this.adjacencyList.set(node.id, []);
    }
  }

  /**
   * Add an edge to the graph
   * @param {Object} edge - Edge object
   */
  addEdge(edge) {
    this.edges.push(edge);
    if (!this.adjacencyList.has(edge.source)) {
      this.adjacencyList.set(edge.source, []);
    }
    this.adjacencyList.get(edge.source).push(edge.target);
  }

  /**
   * Get all nodes
   * @returns {Array} Array of nodes
   */
  getAllNodes() {
    return Array.from(this.nodes.values());
  }

  /**
   * Get all edges
   * @returns {Array} Array of edges
   */
  getAllEdges() {
    return this.edges;
  }

  /**
   * Get neighbors of a node
   * @param {string} nodeId - Node ID
   * @returns {Array} Array of neighbor node IDs
   */
  getNeighbors(nodeId) {
    return this.adjacencyList.get(nodeId) || [];
  }

  /**
   * Get node by ID
   * @param {string} nodeId - Node ID
   * @returns {Object|null} Node object or null
   */
  getNode(nodeId) {
    return this.nodes.get(nodeId) || null;
  }

  /**
   * Get statistics about the graph
   * @returns {Object} Graph statistics
   */
  getStatistics() {
    return {
      total_nodes: this.nodes.size,
      total_edges: this.edges.length
    };
  }
}

/**
 * Build FCG from validated edges
 * @param {Array} tools - Array of extracted tools
 * @param {Array} validatedEdges - Array of validated dependency edges
 * @returns {FunctionCallGraph} Built graph
 */
function buildFCG(tools, validatedEdges) {
  const graph = new FunctionCallGraph();
  
  // Add all tools as nodes with IDs
  for (let i = 0; i < tools.length; i++) {
    const tool = tools[i];
    const node = {
      ...tool,
      id: `node_${String(i + 1).padStart(3, '0')}`
    };
    graph.addNode(node);
  }
  
  // Add all validated edges
  for (const edge of validatedEdges) {
    graph.addEdge(edge);
  }
  
  return graph;
}

/**
 * Remove duplicate edges from graph
 * Keeps the edge with highest confidence
 * @param {FunctionCallGraph} graph - Graph to deduplicate
 * @returns {FunctionCallGraph} Deduplicated graph
 */
function removeDuplicateEdges(graph) {
  const edgeMap = new Map();
  
  for (const edge of graph.edges) {
    const key = `${edge.source}->${edge.target}:${edge.type || 'data_dependency'}`;
    
    if (!edgeMap.has(key)) {
      edgeMap.set(key, edge);
    } else {
      // Merge: keep the one with higher confidence
      const existing = edgeMap.get(key);
      if (edge.confidence > existing.confidence) {
        edgeMap.set(key, edge);
      }
    }
  }
  
  // Rebuild edges and adjacency list
  graph.edges = Array.from(edgeMap.values());
  graph.adjacencyList = new Map();
  
  for (const nodeId of graph.nodes.keys()) {
    graph.adjacencyList.set(nodeId, []);
  }
  
  for (const edge of graph.edges) {
    graph.adjacencyList.get(edge.source).push(edge.target);
  }
  
  return graph;
}

module.exports = {
  FunctionCallGraph,
  buildFCG,
  removeDuplicateEdges
};
