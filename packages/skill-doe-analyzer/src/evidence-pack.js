const { isTaskContextNode } = require('./necessity-baseline');
const { createFlowPathContext, resolveLabelFlowPath } = require('./flow-path-utils');
const { uniqueValues, categoryFromLabel, subtypeFromLabel, stableStringify } = require('./utils');
const { buildLabelDictionary, resolveLabel } = require('./label-resolver');
const crypto = require('crypto');

/*
 * Evidence pack 信息标准(flow-centric,v7)。
 *
 * 一个 unit = 一条 label 从源点到汇点的完整 flow。Pack 只承载判断 necessity
 * 真正需要的信息,组织成:
 *   label         — 这条数据是什么(纯语义,无内部 id)
 *   sink_boundary — 汇点跨越的数据边界(节点角色见 flow 里 role=sink 节点的 capabilities,
 *                    不再在此重复。单跨界不变量保证汇点唯一,故留顶层)
 *   flow[]        — 真源 -> 汇点 的完整节点序列,每个节点 {node_name, role, action, transform?}
 *                    sink/source_sink 节点额外带 sink_surface(汇出具体介质/通道)
 *
 * 全局任务声明(skill 名称/描述/文档来源/全 skill 任务节点)是 task_need 的判断
 * 基准,但它在一个 skill 内恒定,故不寄生在每个 pack 里,而由 buildSharedTaskMemory(fcg)
 * 在 skill 级聚合一次、batch 内共享。每个 pack 用 task_memory_evidence_ids 指向
 * 与本流路径相关的任务节点。
 *
 * grounding(每个结论必须引用证据)不再单列一份 evidence[] 索引——那是给结构里已有的
 * 东西编号,纯冗余。判据句柄直接用 pack 里已有的字段:flow 节点的 node_name、字面量
 * "label" / "sink_boundary",以及 task_memory_evidence_ids 里的任务节点 id。校验只看
 * 引用是否落在 pack 结构内(见 llm-judge.js 的 validEvidenceIdsForPack)。
 *
 * 设计依据(已用代码核实):
 *  - node_path 累积;空 parent = 真正的数据引入点(source_introduction),到此为止。
 *  - "节点对数据做了什么"(redact/slice/summarize/aggregate/pseudonymize/...)来自
 *    filter_events,是 necessity 的核心信号,必须保留。
 *  - 不再堆 task_context 全量节点 / provenance 全量事件(旧 pack 86% 体积)。
 */

// filter_event.type -> 人类可读的转换语义。覆盖 flow-instance-filter.js 全部 type。
const TRANSFORM_TYPE = {
  redact_drop: 'redacted (dropped)',
  field_slice_drop: 'field sliced (dropped)',
  field_slice_keep: 'field sliced (kept)',
  summarization: 'summarized',
  aggregate: 'aggregated',
  pseudonymize: 'pseudonymized',
  semantic_derivation: 'semantically derived',
  source_introduction: 'introduced as new source',
  artifact_production: 'produced as artifact',
  storage_read: 'read from storage',
  unknown_may_flow: 'passed through (no transform)'
};

function shortHash(value) {
  return crypto.createHash('sha1').update(String(value)).digest('hex').slice(0, 10);
}

function createEvidencePackContext(fcg = {}) {
  const security = fcg.security_profile || {};
  const nodeById = new Map((fcg.nodes || []).map(node => [node.id, node]));
  const profileByNodeId = new Map((security.node_profiles || []).map(p => [p.node_id, p]));
  // filter 事件本体集中存于 provenance_graph.events.filtering;flow 只存 id 引用,此处建索引供按 id 取回。
  const filterEventById = new Map(
    ((security.provenance_graph || {}).events?.filtering || []).map(e => [e.event_id, e])
  );
  // v6 flow_states carry the per-bucket reduction antichain (reduction_profile) — the
  // maximal, mutually-incomparable data reductions applied before egress. Indexed by
  // state_id so a label_flow resolves its own bucket via flow_state_id (same map the
  // necessity baseline uses). Lets sink_boundary name WHICH reductions ran, not just whether.
  const flowStateById = new Map((security.flow_states || []).map(s => [s.state_id, s]));
  const flowPathContext = createFlowPathContext(fcg);
  // 全 skill 任务节点候选,稳定排序。task_memory 与 per-unit 相关任务节点都从这里取。
  const taskContextCandidates = (fcg.nodes || [])
    .filter(isTaskContextNode)
    .sort((a, b) => {
      const af = String(a.location?.file || '');
      const bf = String(b.location?.file || '');
      if (af !== bf) return af.localeCompare(bf);
      return Number(a.location?.line || 0) - Number(b.location?.line || 0);
    });
  return {
    fcg,
    security,
    nodeById,
    profileByNodeId,
    filterEventById,
    flowStateById,
    taskContextCandidates,
    flowPathContext,
    labelDictionary: buildLabelDictionary(security)
  };
}

// ---- label ----------------------------------------------------------------

function compactFlowLabel(label = {}) {
  const out = {
    category: label.category || categoryFromLabel(label.label) || '',
    subtype: label.subtype || subtypeFromLabel(label.label) || '',
    sensitivity: label.sensitivity || '',
    field_name: label.field_name || '',
    field_path: label.field_path || ''
  };
  // 影响下游送审的最小标志位。
  if (label.requires_review) out.requires_review = true;
  if (label.mode) out.mode = label.mode;
  return out;
}

// ---- sink boundary ---------------------------------------------------------

function dedup(arr) {
  return [...new Set((arr || []).filter(Boolean))];
}

// sink_surface:挂在 flow[] 的 sink/source_sink 节点上,表示本 label 在汇点的具体输出面/
// 落地面/执行面。比 sink_boundary 里的粗粒度字段(operation_type / data_surface /
// receiver_scope)更细,给 judge 看"这个 label 具体写到哪里/从哪里发出"。
// 读侧标签(file_read/database_read/...)对「是否过度暴露」无用,一律丢弃。
// network_egress / third_party_service 与 sink_boundary 的 data_surface / receiver_scope
// 完全重复,也丢弃——只保留真正提供增量信息的细粒度 surface。
const SINK_SURFACE_TAGS = new Set([
  // 网络外发面细分(比 external_egress 更细)
  'webhook_post', 'email_send', 'api_call',
  // 持久化面细分(比 local_persistence 更细)
  'file_write', 'database_write', 'memory_write', 'log_write', 'artifact_write',
  // 命令执行面(高危)
  'shell_exec'
]);

function sinkSurface(observation = {}, nodeProfile = {}) {
  const tags = dedup([...(observation.security_tags || []), ...(nodeProfile.security_tags || [])]);
  return tags.filter(t => SINK_SURFACE_TAGS.has(t));
}

function sinkBoundary(observation = {}, nodeProfile = {}, exposure = null, flowState = null) {
  const b = observation.boundary || {};
  const out = {
    node_name: observation.node_name || nodeProfile.node_name || '',
    operation_type: observation.operation_type || '',
    data_surface: b.data_surface || nodeProfile.data_surface || '',
    receiver_scope: b.receiver_scope || nodeProfile.receiver_scope || '',
    retention_scope: b.retention_scope || nodeProfile.retention_scope || '',
    trust_boundary: b.trust_boundary || nodeProfile.trust_boundary || '',
    // node_roles 已删:与 flow[] 中 sink 节点的 capabilities 完全重复。
    // sink_surface 已迁移到 flow[] 的 sink/source_sink 节点上。
    operation_tags: dedup(nodeProfile.operation_tags || [])
  };
  // 结构信号(N5):暴露等级标记。所有真外泄统一标 high_sensitivity_egress —— 让 judge
  // 知道这个边界是真实严重的外泄面(model_provider 与外部网络/第三方一视同仁),而非"可信内部"。
  if (exposure && exposure.exposure_tier) out.exposure_tier = exposure.exposure_tier;
  // 缓释结构信号(reduction antichain):本流在越界前实际施加的极大、互不可比的信息缩减
  // 类型集(redact_drop / field_slice_* / summarization / aggregate)。桶级同质(它是
  // flood dedup-key 分量),故一条流一个确定的集合,无 conservative-AND 模糊。给 judge
  // 看【具体做了哪种脱敏/缩减】而非仅"是否缩减"—— 由 judge 判这些缩减对本 receiver 是否
  // 充分到可豁免暴露,而非机械加分。空数组=越界前无任何缩减(原始数据外发)。
  const reductionProfile = (flowState && flowState.reduction_profile) || [];
  if (reductionProfile.length) out.reduction_before_egress = [...reductionProfile];
  return out;
}

// ---- flow nodes ------------------------------------------------------------

// role(流上角色) vs capabilities(节点能力)是两个不同的范畴,必须分开:
//
//   - capabilities = 节点的 node_roles,即这个节点"一辈子可能做的所有动作"的并集
//     (跨所有 label、所有路径聚合)。一个节点具备 sink-like 能力 ≠ 它在这条流上
//     就 sink 了这个 label —— 它的 sink 能力可能冲着别的数据去。
//   - role = 节点在【这一条 label 流】上对【这个 label】扮演的角色,由【位置】决定,
//     不读全局 capabilities:
//       * 首节点(空 parent 的真源引入点)                = source
//       * 末节点(observation 边界节点,本流唯一的汇点)    = sink
//       * 首末同一节点(单点即引入即外发,一个动作既 source 又 sink) = source_sink
//       * 其余中间节点                                     = transform
//
// 关键:一条 source→sink 的溯源 unit 里【有且只有一个 sink】(末端那个 observation
// 边界)。若同一 label 在中途某节点也跨了边界,那是【另一个 observation、另一个 unit】,
// 其末端才是那个节点。所以中间节点对本 label 只能是 source / transform,绝不是"另一个
// sink"——之前用全局 node_roles 给中间节点贴 sink 是范畴错误。节点的多重能力不丢,
// 放在每个节点的 capabilities 字段里供 judge 参考。
function flowRole({ isSource, isSink }) {
  if (isSource && isSink) return 'source_sink';
  if (isSink) return 'sink';
  if (isSource) return 'source';
  return 'transform';
}

// 节点能力 = node_roles,但剔除无信息量的 'transform' 占位 role(它只是 profiler 的
// 兜底,不代表真实能力)。空则不附 capabilities 字段,避免冗余。
function nodeCapabilities(nodeRoles = []) {
  return dedup(nodeRoles).filter(r => r && r !== 'transform');
}

// "这步在干嘛":operation_type 揉进 instructionText/description 文本(非单列字段),
// 既保留打分信号又维持 {node_name, role, action, transform} 的干净结构。
function nodeAction(node = {}) {
  const s = node.formal_semantics || {};
  const op = s.operation_type || node.operationType || '';
  const text = node.instructionText || node.description || '';
  return [op, text].filter(Boolean).join(': ');
}

// 只暴露与数据脱敏/切片相关的 transform tag(顺序即执行顺序的判断信号),其余 tag 不进 pack。
const OPERATION_TRANSFORM_TAGS = new Set([
  'field_slice', 'redaction', 'semantic_extraction', 'aggregation', 'pseudonymization'
]);

// 多动作节点:把 profile.action_steps 压成有序 operations 序列 [{op, tags?}]。
// 顺序 = 执行顺序,让 judge 能读出"脱敏发生在外发之前还是之后"。单动作节点返回 null(沿用 action)。
function nodeOperations(profile = {}) {
  const steps = profile.action_steps || [];
  if (steps.length <= 1) return null;
  return steps
    .slice()
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map(step => {
      const entry = { op: step.operation_type || '' };
      const tags = (step.operation_tags || []).filter(t => OPERATION_TRANSFORM_TAGS.has(t));
      if (tags.length) entry.tags = tags;
      return entry;
    });
}

function labelText(l) {
  if (!l) return '';
  if (typeof l === 'string') return l;
  return l.label || [l.category, l.subtype].filter(Boolean).join('.') || '';
}

function summarizeTransform(ev = {}) {
  const type = ev.type || '';
  if (!type) return null;
  const from = labelText(ev.from_label || ev.dropped_label || ev.context_label || ev.kept_label);
  const to = labelText(ev.introduced_label || ev.kept_label);
  const out = { type, effect: TRANSFORM_TYPE[type] || type };
  if (from) out.from_label = from;
  if (to && to !== from) out.to_label = to;
  return out;
}

// 同一节点内完全相同的 transform 合并为一条并计次(count 仅在 >1 时附加)。
// 同节点内的重复来自多个无法区分的 filter 事件(action_step/from/to 均空),对 judge 无
// 增量、纯刷屏(实测占 pack 体积约 8%)。计次保留"发生过几次"这一弱信号。
// 注意:跨节点的顺序/计次由 dedup 键的 transform_seq(沿 node_path 展开)承载,与此无关,
// 本合并只作用于单节点内、不改变任何流路径顺序,故不影响 dedup。
function dedupeTransforms(transforms = []) {
  const order = [];
  const byKey = new Map();
  for (const t of transforms) {
    const key = JSON.stringify(t);
    if (byKey.has(key)) {
      byKey.get(key).count += 1;
    } else {
      const entry = { ...t, count: 1 };
      byKey.set(key, entry);
      order.push(entry);
    }
  }
  return order.map(entry => (entry.count > 1 ? entry : (delete entry.count, entry)));
}

// 真正改变数据的 transform 事件类型(引入/纯透传不算)。source_introduction 只是标签引入,
// unknown_may_flow 明确"无 transform",都不进 pack,避免刷屏。
const REAL_TRANSFORM_TYPES = new Set([
  'redact_drop', 'field_slice_drop', 'field_slice_keep',
  'summarization', 'aggregate', 'pseudonymize', 'semantic_derivation'
]);

// 顺 parent 链收集本流路径上发生过的所有 transform,按 node_id 归组。
// 序列化后 flow.filter_events 恒为 [],真身集中存于 provenance_graph.events.filtering;
// 每条 flow 只带 local_filter_event_ids(本跳产生的 id),故需顺 parent 链累积再按 id 取本体。
function transformsByNode(labelFlow = {}, flowById = new Map(), filterEventById = new Map()) {
  const byNode = new Map();
  const seenEvent = new Set();
  const seenFlow = new Set();
  let current = labelFlow;
  while (current && typeof current === 'object') {
    if (seenFlow.has(current.label_flow_id)) break;
    seenFlow.add(current.label_flow_id);
    for (const eventId of current.local_filter_event_ids || []) {
      if (seenEvent.has(eventId)) continue;
      seenEvent.add(eventId);
      const ev = filterEventById.get(eventId);
      if (!ev || !ev.node_id || !REAL_TRANSFORM_TYPES.has(ev.type)) continue;
      const t = summarizeTransform(ev);
      if (!t) continue;
      if (!byNode.has(ev.node_id)) byNode.set(ev.node_id, []);
      byNode.get(ev.node_id).push(t);
    }
    const parentId = (current.parent_label_flow_ids || [])[0] || '';
    if (!parentId) break;
    current = flowById.get(parentId);
  }
  return byNode;
}

// ---- structural signals (N5) ----------------------------------------------
//
// 结构事实喂给 LLM 当硬证据(不喂规则预算分)。挂在相关 flow[] 节点上:
//   sink 节点   -> schema_declares_input:该 label 是否在 sink 声明的 input schema 里
//                  (action_input_need 的硬依据;true/false/null=未声明 schema)
//   source 节点 -> origin_trust:数据引入点的信任边界(receiver 相容判断的硬依据;
//                  user_visible 的数据回给用户 ≠ external_network 抓来的数据)
// 二者都读已有数据,不新造:schema 读 sink 节点 formal_semantics.inputs;origin_trust
// 读 source 节点 profile 的 trust_boundary。

// 该 label 是否落在 sink 节点声明的 input schema 里。逻辑与 necessity-baseline 的
// schemaInputMembership 对齐(1→true / 0.2→false / null→未声明),但读 pack 自己的
// nodeById,不耦合 necessity context。
function schemaDeclaresInput(sinkNode = {}, label = {}) {
  const inputs = (sinkNode.formal_semantics || {}).inputs || [];
  if (!inputs.length) return null; // sink 未声明 input schema —— 无从判断
  const needles = [label.field_name, label.field_path, label.subtype, label.category, label.label]
    .filter(Boolean)
    .map(s => String(s).toLowerCase());
  const hay = inputs.map(i => `${i.name || ''} ${i.type || ''}`).join(' ').toLowerCase();
  return needles.some(n => n && (hay.includes(n) || n.split(/\s+/).some(t => t && hay.includes(t))));
}

// APPEND-MARKER-1

// ---- pack builder ----------------------------------------------------------

function unitId(observation = {}, labelFlow = {}) {
  return `${observation.observation_id || 'obs'}::${labelFlow.label_flow_id || 'flow'}`;
}

// 本流路径节点中,属于任务节点的那些 -> 共享 task_memory 节点 id(同一套 shortHash)。
// 让 LLM 只取与本流相关的任务节点判断全局必要性,而非整张 skill 任务表。
function taskMemoryEvidenceIds(nodePath = [], nodeById = new Map()) {
  const ids = ['task.memory.identity'];
  for (const nodeId of nodePath) {
    const node = nodeById.get(nodeId);
    if (!node || !isTaskContextNode(node)) continue;
    const key = node.id || `${node.location?.file || ''}:${node.location?.line || ''}:${node.name || ''}`;
    if (key) ids.push(`task.memory.node.${shortHash(key)}`);
  }
  return uniqueValues(ids);
}

function buildEvidencePack({ fcg = {}, observation = {}, labelFlow = {}, nodeProfile = {}, exposure = null, context = null }) {
  const ctx = context || createEvidencePackContext(fcg);
  const flowPathContext = ctx.flowPathContext || createFlowPathContext(fcg);
  const nodeById = ctx.nodeById || new Map((fcg.nodes || []).map(n => [n.id, n]));
  const profileByNodeId = ctx.profileByNodeId || new Map(((fcg.security_profile || {}).node_profiles || []).map(p => [p.node_id, p]));
  const filterEventById = ctx.filterEventById
    || new Map((((fcg.security_profile || {}).provenance_graph || {}).events?.filtering || []).map(e => [e.event_id, e]));
  const flowById = flowPathContext.flowById || new Map();
  const label = labelFlow.label || {};

  const resolvedPath = resolveLabelFlowPath(labelFlow, flowPathContext);
  const nodePath = resolvedPath.node_path || [];
  const nodeNames = resolvedPath.node_names || [];
  const sinkNodeId = observation.node_id || labelFlow.current_node || nodePath[nodePath.length - 1] || '';
  const transforms = transformsByNode(labelFlow, flowById, filterEventById);
  // 本流所属的 flood 桶(flow_state):承载 reduction_profile 缩减集。用与 necessity
  // baseline 相同的 flow_state_id → flowStateById 解析路径,保证两侧读到同一事实。
  const flowStateById = ctx.flowStateById || new Map();
  const flowState = labelFlow.flow_state_id ? flowStateById.get(labelFlow.flow_state_id) : null;

  const flow = nodePath.map((nodeId, index) => {
    const node = nodeById.get(nodeId) || {};
    const profile = profileByNodeId.get(nodeId) || {};
    const caps = nodeCapabilities(profile.node_roles || node.node_roles || []);
    // role 由【位置】决定,不读全局能力:
    //   首节点 = 真源引入点 => source;末节点(汇点)在下方单独处理;其余 = transform。
    //   特例:首末同一节点(单点流)在下方按 source_sink 处理。
    const isSinkNode = nodeId === sinkNodeId;
    const isFirst = index === 0;
    const role = isSinkNode
      ? flowRole({ isSource: isFirst, isSink: true })  // 末节点;若同时是首节点则 source_sink
      : flowRole({ isSource: isFirst, isSink: false }); // 首节点=source,中间=transform
    const nodeTransforms = transforms.get(nodeId) || [];
    const entry = {
      node_name: node.name || nodeNames[index] || nodeId,
      role,
      action: nodeAction(node)
    };
    // 多动作节点:action 留整节点总述,operations 给有序动作序列(op+脱敏/切片 tag)。
    const operations = nodeOperations(profile);
    if (operations) entry.operations = operations;
    // 节点的多重能力单列(role≠能力):让 judge 看到中间节点"其实也具备 X 能力",
    // 但不把它误判成本流的 sink。
    if (caps.length) entry.capabilities = caps;
    // sink_surface:仅 sink/source_sink 节点附加。表示本 label 在汇点的具体输出面/
    // 落地面/执行面,是 sink_boundary 粗粒度字段的细分补充。
    if (isSinkNode) {
      const surface = sinkSurface(observation, profile);
      if (surface.length) entry.sink_surface = surface;
      // 结构信号(N5):该 label 是否在 sink 声明的 input schema 里 —— action_input_need 硬依据。
      const declaresInput = schemaDeclaresInput(node, label);
      if (declaresInput !== null) entry.schema_declares_input = declaresInput;
    }
    // 结构信号(N5):source / source_sink 节点标 origin_trust(数据引入点的信任边界)。
    if (isFirst) {
      const originTrust = profile.trust_boundary || node.trust_boundary || '';
      if (originTrust) entry.origin_trust = originTrust;
    }
    const dedupedTransforms = dedupeTransforms(nodeTransforms);
    if (dedupedTransforms.length === 1) entry.transform = dedupedTransforms[0];
    else if (dedupedTransforms.length > 1) entry.transforms = dedupedTransforms;
    return entry;
  });

  // 汇点不在 node_path 末尾(罕见:溯源断点)时补一个 sink 条目,保证本流唯一的 sink 不丢。
  const sinkNode = nodeById.get(sinkNodeId) || {};
  if (!nodePath.length || nodePath[nodePath.length - 1] !== sinkNodeId) {
    const sinkProfile = profileByNodeId.get(sinkNodeId) || nodeProfile || {};
    const sinkCaps = nodeCapabilities(sinkProfile.node_roles || sinkNode.node_roles || []);
    const entry = {
      node_name: sinkNode.name || observation.node_name || sinkNodeId,
      role: nodePath.length === 0 ? 'source_sink' : 'sink',
      action: nodeAction(sinkNode)
    };
    const sinkOperations = nodeOperations(sinkProfile);
    if (sinkOperations) entry.operations = sinkOperations;
    if (sinkCaps.length) entry.capabilities = sinkCaps;
    const fallbackSurface = sinkSurface(observation, sinkProfile);
    if (fallbackSurface.length) entry.sink_surface = fallbackSurface;
    // 结构信号(N5):sink 的 schema 归属;单点流(source_sink)另标 origin_trust。
    const declaresInput = schemaDeclaresInput(sinkNode, label);
    if (declaresInput !== null) entry.schema_declares_input = declaresInput;
    if (entry.role === 'source_sink') {
      const originTrust = sinkProfile.trust_boundary || sinkNode.trust_boundary || '';
      if (originTrust) entry.origin_trust = originTrust;
    }
    const sinkTransforms = transforms.get(sinkNodeId) || [];
    const dedupedSinkTransforms = dedupeTransforms(sinkTransforms);
    if (dedupedSinkTransforms.length === 1) entry.transform = dedupedSinkTransforms[0];
    else if (dedupedSinkTransforms.length > 1) entry.transforms = dedupedSinkTransforms;
    flow.push(entry);
  }

  const pack = {
    unit_id: unitId(observation, labelFlow),
    observation_id: observation.observation_id || '',
    label_flow_id: labelFlow.label_flow_id || '',
    question: [
      'Judge DOE necessity for this label flowing from its source to this sink.',
      'Local necessity: do the sink action input and receiver semantics need this label?',
      'Global necessity (task_need): does the whole source-to-sink path belong to the data/control flow needed for the declared skill task, AND is the sink (boundary) node necessary in that path?'
    ].join(' '),
    label: compactFlowLabel(label),
    sink_boundary: sinkBoundary(observation, nodeProfile, exposure, flowState),
    flow
  };
  // Periodic leak: this sink sits inside a real cycle and re-emits the same class
  // of data every loop iteration. Surface leak_type/severity so the judge weighs a
  // repeating leak above a one-shot one (amplifying/mutating > steady).
  if (observation.leak_type) {
    pack.leak_type = observation.leak_type;
    if (observation.leak_severity) pack.leak_severity = observation.leak_severity;
  }
  // Flow reached this sink by collapsing through a real cycle (enter -> one lap ->
  // exit). Mark it so the judge knows the path traversed a loop but leaks outside.
  if (labelFlow.cycle_handling === 'collapse') {
    pack.cycle_handling = 'collapse';
  }
  pack.task_memory_evidence_ids = taskMemoryEvidenceIds(nodePath, nodeById);
  return pack;
}

// APPEND-MARKER-2

// ---- shared task memory (skill 级,batch 内共享) ---------------------------

// 直接从 FCG 聚合全 skill 任务声明:skill identity + 文档来源 + 全 skill 任务节点。
// 这是 task_need 的判断基准,在一个 skill 内恒定,故 skill 级构造一次、batch 内共享。
// 每个 pack 用 task_memory_evidence_ids 指向与本流相关的子集。
function buildSharedTaskMemory(fcg = {}, context = null) {
  const ctx = context || createEvidencePackContext(fcg);
  const candidates = ctx.taskContextCandidates || [];

  const skillIdentity = {
    skill_name: fcg.meta?.skill_name || fcg.skill?.name || '',
    skill_version: fcg.meta?.skill_version || '',
    description: String(fcg.skill?.description || fcg.description || ''),
    readme_preview: String(fcg.readme || fcg.readmeText || '')
  };

  const docSources = new Map();
  collectDocumentationSources(docSources, fcg.documentation_context || {});

  const byNodeKey = new Map();
  for (const node of candidates) {
    const key = node.id || `${node.location?.file || ''}:${node.location?.line || ''}:${node.name || ''}`;
    if (!key || byNodeKey.has(key)) continue;
    byNodeKey.set(key, {
      evidence_id: `task.memory.node.${shortHash(key)}`,
      node_id: node.id || '',
      name: node.name || '',
      semanticKind: node.semanticKind || '',
      operation_type: node.formal_semantics?.operation_type || node.operationType || '',
      instructionText: String(node.instructionText || node.description || ''),
      location: node.location || {},
      source_line: String(node.source_context?.source_line || node.formal_semantics?.evidence?.source_line || '')
    });
  }
  const taskNodes = Array.from(byNodeKey.values());

  const docSourceItems = Array.from(docSources.values())
    .sort((a, b) => String(a.file || '').localeCompare(String(b.file || '')))
    .map(item => ({ evidence_id: `task.memory.doc.${shortHash(item.file || '')}`, ...item }));

  const evidence = [
    { evidence_id: 'task.memory.identity', type: 'skill_evidence', data: skillIdentity },
    ...docSourceItems.map(item => ({
      evidence_id: item.evidence_id,
      type: 'skill_evidence',
      data: { file: item.file, role: item.role, line_count: item.line_count, preview: item.preview }
    })),
    ...taskNodes.map(node => ({ evidence_id: node.evidence_id, type: 'skill_evidence', data: node }))
  ];

  return {
    memory_type: 'extractive_shared_task_context',
    skill_name: skillIdentity.skill_name,
    skill_version: skillIdentity.skill_version,
    evidence,
    // task_context_node_count / documentation_source_count 仅供 stats 观测(llm-judge.js),
    // 不进 prompt(见 buildJudgePromptBody 的 trimTaskMemoryForPrompt)——对 LLM 判定几乎
    // 无信息量的规模计数。task_evidence_ids 已删:全仓库零消费,== evidence[].evidence_id 去重。
    task_context_node_count: taskNodes.length,
    documentation_source_count: docSourceItems.length,
    use_for_components: ['task_need'],
    note: 'This is shared global task memory. Cite only task memory evidence IDs listed by the assessment unit.'
  };
}

function collectDocumentationSources(target, documentationContext = {}) {
  for (const context of [
    documentationContext.skill_context,
    documentationContext.readme_context,
    ...(documentationContext.extraction_contexts || [])
  ]) {
    if (!context?.file) continue;
    if (!target.has(context.file)) {
      target.set(context.file, {
        file: context.file,
        role: context.role || '',
        line_count: context.line_count,
        preview: String(context.preview || '')
      });
    }
  }
}

module.exports = {
  createEvidencePackContext,
  buildEvidencePack,
  buildSharedTaskMemory,
  unitId,
  stableStringify,
  nodeOperations,
  transformsByNode,
  TRANSFORM_TYPE
};



