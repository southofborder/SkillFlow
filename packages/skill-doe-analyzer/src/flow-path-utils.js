function createFlowPathContext(fcg = {}) {
  const security = fcg.security_profile || {};
  return {
    flowById: new Map((security.label_flows || []).map(flow => [flow.label_flow_id, flow])),
    nodeById: new Map((fcg.nodes || []).map(node => [node.id, node]))
  };
}

function resolveLabelFlowPath(labelFlow = {}, context = {}) {
  const flowById = context.flowById || new Map();

  // FCG 不存 node_path/edge_path,DOE 端顺 parent 链重建。若上游已显式给了
  // node_path(罕见/测试 fixture),尊重之并按 origin_node 截前缀;否则用链重建。
  if (Array.isArray(labelFlow.node_path) && labelFlow.node_path.length) {
    return trimStoredPath(labelFlow, context);
  }

  // P1: 溯源到本 label 的真引入点即停。parent 链是 provenance 设计(parent 指回上游
  // 真源,见 FCG graph-transfer-analyzer 注释),当提取/概括/LLM 等步 source_introduction
  // 一个新 label 时,链会继续往上接到【上一段数据】的源。那段前缀对【本 label】而言
  // 不是它的流路径,必须裁掉,否则会把两条语义不同的流缝成一条(实测 42% 的 unit 受此影响,
  // 其中 82% label 真的换了身份)。origin_node 是 label 自带、100% 填充的真引入点。
  //
  // 在【链】层裁剪(而非裁好的 node_path/edge_path):node_path 会去重相邻重复节点、
  // edge_path 会跳过无 incoming_edge 的 flow,两者与 chain 都不是 1:1,各自按 node 下标
  // 切会错位。裁链后再由同一条裁好的链一致地重建两者,才对齐。
  const fullChain = rebuildFlowChain(labelFlow, flowById);
  const origin = labelFlow.origin_node || labelFlow.label?.origin_node || '';
  const chain = trimChainToOrigin(fullChain, origin);

  const nodePath = nodePathFromChain(chain);
  const edgePath = edgePathFromChain(chain);
  const nodeNames = nodePath.map(nodeId => context.nodeById?.get(nodeId)?.name || nodeId);

  return {
    node_path: nodePath,
    node_names: nodeNames,
    edge_path: edgePath,
    trimmed_prefix_count: fullChain.length - chain.length
  };
}

// 链裁剪到本 label 真引入点:沿 root->leaf 找到第一个 current_node === origin 的 flow
// (label 在该节点被引入,此处 current_node 与 origin_node 重合;此前的 flow 承载的是
// 上一段 label,丢弃)。注意必须按 current_node 匹配,不能按 flow.origin_node 字段——
// 引入点之后的 child flow 其 origin_node 仍指向 origin,会把停点错误后移。
function trimChainToOrigin(chain = [], origin = '') {
  if (!origin) return chain;
  const startIdx = chain.findIndex(flow => (flow.current_node || '') === origin);
  return startIdx > 0 ? chain.slice(startIdx) : chain;
}

function nodePathFromChain(chain = []) {
  const nodes = [];
  for (const flow of chain) {
    const nodeId = flow.current_node || '';
    if (!nodeId) continue;
    if (nodes[nodes.length - 1] !== nodeId) nodes.push(nodeId);
  }
  return nodes;
}

function edgePathFromChain(chain = []) {
  const edges = [];
  for (let i = 0; i < chain.length; i++) {
    // 第一个 flow 是路径起点;它的 incoming_edge 来自(已被裁掉的)上游前缀,连接的
    // 源节点不在 node_path 内,故跳过。edge_path 只含 node_path 内相邻节点之间的边。
    if (i === 0) continue;
    const flow = chain[i];
    const edgeId = flow.incoming_edge_id || flow.edge_id || '';
    if (edgeId) edges.push(edgeId);
  }
  return edges;
}

// 上游已显式提供 node_path 的回退路径(保持与旧行为兼容,仅追加 origin 截前缀)。
function trimStoredPath(labelFlow = {}, context = {}) {
  const fullNodePath = [...labelFlow.node_path];
  const fullEdgePath = Array.isArray(labelFlow.edge_path) ? [...labelFlow.edge_path] : [];
  const fullNodeNames = Array.isArray(labelFlow.node_names) && labelFlow.node_names.length
    ? [...labelFlow.node_names]
    : fullNodePath.map(nodeId => context.nodeById?.get(nodeId)?.name || nodeId);
  const origin = labelFlow.origin_node || labelFlow.label?.origin_node || '';
  const startIdx = origin ? fullNodePath.indexOf(origin) : -1;
  if (startIdx <= 0) {
    return { node_path: fullNodePath, node_names: fullNodeNames, edge_path: fullEdgePath, trimmed_prefix_count: 0 };
  }
  // edge_path 存储契约:edge[i] 连接 node[i]->node[i+1],故 len(edge)==len(node)-1
  // (全语料实测 100% 成立)。裁掉前 startIdx 个节点,等价于裁掉前 startIdx 条边——
  // 被裁的 node[0..startIdx-1] 恰好是 edge[0..startIdx-1] 的源端。这样裁完仍满足
  // len(edge)==len(node)-1,与 chain-rebuild 分支(edgePathFromChain 跳过首 flow)一致。
  // 只有当上游 edge_path 长度不符契约(len!=node-1)时才保守不切,避免错位。
  const edgeMatchesContract = fullEdgePath.length === fullNodePath.length - 1;
  return {
    node_path: fullNodePath.slice(startIdx),
    node_names: fullNodeNames.slice(startIdx),
    edge_path: edgeMatchesContract ? fullEdgePath.slice(startIdx) : fullEdgePath,
    trimmed_prefix_count: startIdx
  };
}

function rebuildFlowChain(labelFlow = {}, flowById = new Map()) {
  const chain = [];
  const seen = new Set();
  let current = labelFlow;
  while (current && typeof current === 'object') {
    const id = current.label_flow_id || current.representative_path_id || '';
    const key = id || `${current.current_node || ''}:${chain.length}`;
    if (!key || seen.has(key)) break;
    seen.add(key);
    chain.unshift(current);
    const parentId = (current.parent_label_flow_ids || [])[0] || '';
    if (!parentId) break;
    current = flowById.get(parentId);
  }
  return chain;
}

module.exports = {
  createFlowPathContext,
  resolveLabelFlowPath
};
