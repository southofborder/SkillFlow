#!/usr/bin/env node
// 只读探针:量化 DOE 送审 dedup 的粒度是否够。不改任何生产代码,复用 doe-analyzer
// 规则层 + flow-path-utils + evidence-pack 判据。对每个 skill 的【gated dedup 宇宙】
// (带 _evidence_pack 的 assessment,即真正会送审、参与 dedup 的单元)输出三张表:
//
//   ① 路径咬人比例:necessity 被 flow_path_signal 卡住的组占比。这是路径耦合损失的上限
//      —— 只有 necessity_basis==task_need 且 flow_path_signal<boundary_node_signal 的组,
//      组内路径变化才可能翻转最终 necessity。比例≈0 则现有粗键已安全。
//   ② 组内异质:在①暴露的组里,origin_class / path_purpose_sig 是否恒定。哪个维度不恒定,
//      哪个才值得进键。
//   ③ 压缩机会:多少 observation_id 在 boundary 元组下可被合并(免费压缩上限)。
//
// 用法:node scripts/dedup-granularity-probe.js [fcgDir]
//   fcgDir 默认 results/debug-k20-c8/fcg/skills

const path = require('path');
const nodefs = require('fs');
const { analyzeDoe } = require('../packages/skill-doe-analyzer/src/doe-analyzer');
const { createFlowPathContext, resolveLabelFlowPath } = require('../packages/skill-doe-analyzer/src/flow-path-utils');
const { createEvidencePackContext, transformsByNode } = require('../packages/skill-doe-analyzer/src/evidence-pack');

const FCG_DIR = process.argv[2] || 'results/debug-k20-c8/fcg/skills';

// ---- 复用生产判据(本地镜像,与 evidence-pack.js 保持一致)----
const LINK_PLACEHOLDER_PARAMS = new Set(['', 'state', 'context']);
function edgeCarriesData(edge = {}) {
  if ((edge.type || edge.edge_type) !== 'control_flow') return true;
  const df = edge.data_flow || {};
  return !(LINK_PLACEHOLDER_PARAMS.has(df.from_param || '') && LINK_PLACEHOLDER_PARAMS.has(df.to_param || ''));
}

// 节点用途类:transform / model / storage / external / local / user_visible / source / other
// 来自 node_profile.node_roles(剔除 transform 占位后的能力),用于中粒度 path_purpose_sig。
function nodePurposeToken(roles = []) {
  const s = new Set(roles || []);
  if (s.has('model_inference')) return 'model';
  if (s.has('external_egress')) return 'external';
  if (s.has('local_persistence')) return 'storage';
  if (s.has('command_execution')) return 'exec';
  if (s.has('transform')) return 'transform';
  if (s.has('data_introduction')) return 'source';
  if (s.has('tool_invocation')) return 'tool';
  return 'other';
}

function boundaryTuple(boundary = {}, nodeId = '') {
  const b = boundary || {};
  return [nodeId, b.data_surface || '', b.receiver_scope || '', b.retention_scope || '', b.trust_boundary || ''].join('~');
}

// origin 信任类:粗化 origin_node 为其节点的安全语义等价类,避免用原始 id 过度切分。
// 与生产 doe-analyzer.originClass 一致:`${trust_boundary}/${data_surface}`(不含 node_roles)。
function originClass(originNodeId, profileByNode) {
  const p = profileByNode.get(originNodeId);
  if (!p) return 'unknown';
  return `${p.trust_boundary || 'unknown'}/${p.data_surface || 'unknown'}`;
}

// path_purpose_sig(中粒度):从 origin 起,沿 data_flow 跳(丢 order_only 跳)的有序序列,
// 每跳 = node_purpose_token。这是路径的 necessity 相关投影,不是原始路径 hash。
function pathPurposeSig(labelFlow, flowCtx, edgeById, profileByNode) {
  const resolved = resolveLabelFlowPath(labelFlow, flowCtx);
  const nodePath = resolved.node_path || [];
  const edgePath = resolved.edge_path || [];
  const tokens = [];
  // 首节点(origin)总入序
  if (nodePath.length) tokens.push(nodePurposeToken((profileByNode.get(nodePath[0]) || {}).node_roles));
  for (let i = 1; i < nodePath.length; i++) {
    const edge = edgeById.get(edgePath[i - 1]);
    if (edge && !edgeCarriesData(edge)) continue; // 丢 order_only 跳
    tokens.push(nodePurposeToken((profileByNode.get(nodePath[i]) || {}).node_roles));
  }
  return tokens.join('>') || 'empty';
}

function allDistinct(values) {
  return new Set(values).size <= 1;
}

// ---- 候选键构造:量各维度对 dedup 组数的放大(= 送审量代价)----
// 当前键(基线):observation_id | label | transform_set(无序去重)
function labelKey(label = {}) {
  return label.label || [label.category, label.subtype].filter(Boolean).join('.');
}

// transform_set:旧无序去重签名(基线对照用;生产已换为下面的 transformSeq 有序计次)。
function transformSet(labelFlow, flowById, filterEventById) {
  const byNode = transformsByNode(labelFlow, flowById, filterEventById);
  const types = new Set();
  for (const list of byNode.values()) for (const t of list) if (t && t.type) types.add(t.type);
  return types.size ? [...types].sort().join(',') : 'none';
}

// transform_seq:有序 + 计次。沿路径节点顺序展开每节点的 transform 类型序列(不去重、不排序),
// 天然把"先脱敏后发"vs"发后脱敏"、以及 transform 次数不同的流分开。
function transformSeq(labelFlow, flowCtx, flowById, filterEventById) {
  const byNode = transformsByNode(labelFlow, flowById, filterEventById);
  const resolved = resolveLabelFlowPath(labelFlow, flowCtx);
  const seq = [];
  for (const nodeId of resolved.node_path || []) {
    const list = byNode.get(nodeId) || [];
    for (const t of list) if (t && t.type) seq.push(t.type);
  }
  return seq.length ? seq.join('>') : 'none';
}

// ---- 主流程 ----
function probeSkill(fcgJson) {
  const sp = fcgJson.security_profile || {};
  const flowCtx = createFlowPathContext(fcgJson);
  const packCtx = createEvidencePackContext(fcgJson);
  const filterEventById = packCtx.filterEventById;
  const edgeById = new Map((fcgJson.edges || []).map(e => [e.id, e]));
  const profileByNode = new Map((sp.node_profiles || []).map(p => [p.node_id, p]));
  const flowById = new Map((sp.label_flows || []).map(f => [f.label_flow_id, f]));
  const obsById = new Map((sp.observations || []).map(o => [o.observation_id, o]));

  const result = analyzeDoe(fcgJson, { keepInternal: true });

  // gated 宇宙 = 带 _evidence_pack 的 assessment
  const gated = result.assessments.filter(a => a._evidence_pack && a._evidence_pack.unit_id);

  // 按当前 _dedup_key 分组
  const groups = new Map();
  for (const a of gated) {
    const key = a._dedup_key || a._evidence_pack.unit_id;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(a);
  }

  let groupsTotal = 0, groupsMulti = 0;
  let pathBinding = 0;            // ① necessity 被 flow_path_signal 卡住的组数
  let pathBindingMulti = 0;      // ①且组内多成员(才有合并损失风险)
  let heteroOrigin = 0;          // ② 暴露组里 origin_class 不恒定
  let heteroPathSig = 0;         // ② 暴露组里 path_purpose_sig 不恒定
  let exposedGroups = 0;

  for (const [, members] of groups) {
    groupsTotal++;
    if (members.length > 1) groupsMulti++;

    // 组代表判定路径耦合:用任一成员的分量(同键成员 obs+label+transform 同,分量近似)
    const rep = members[0];
    const gn = rep.global_necessity || {};
    const isTaskBound = rep.necessity_basis === 'task_need';
    const flowIsArgmin = Number(gn.flow_path_signal) < Number(gn.boundary_node_signal);
    const pathMatters = isTaskBound && flowIsArgmin;

    if (pathMatters) {
      pathBinding++;
      if (members.length > 1) {
        pathBindingMulti++;
        exposedGroups++;
        // ② 组内异质:计算每个成员的 origin_class / path_purpose_sig
        const origins = [], sigs = [];
        for (const m of members) {
          const lf = flowById.get(m.label_flow_id);
          if (!lf) continue;
          origins.push(originClass(lf.origin_node || '', profileByNode));
          sigs.push(pathPurposeSig(lf, flowCtx, edgeById, profileByNode));
        }
        if (!allDistinct(origins)) heteroOrigin++;
        if (!allDistinct(sigs)) heteroPathSig++;
      }
    }
  }

  // ③ 压缩机会:同 boundary 元组的不同 observation_id 可合并
  const obsByBoundary = new Map();
  for (const a of gated) {
    const obs = obsById.get(a.observation_id);
    if (!obs) continue;
    const bt = boundaryTuple(obs.boundary, obs.node_id);
    if (!obsByBoundary.has(bt)) obsByBoundary.set(bt, new Set());
    obsByBoundary.get(bt).add(a.observation_id);
  }
  let mergeableObs = 0, distinctBoundaries = 0;
  for (const set of obsByBoundary.values()) {
    distinctBoundaries++;
    if (set.size > 1) mergeableObs += (set.size - 1); // 每个多余 obs 可并
  }
  const distinctObs = new Set(gated.map(a => a.observation_id)).size;

  // ---- 候选键组数对比:每种键在 gated 宇宙下产生多少组 ----
  // 组数越多 = 送审越多。基线是当前生产键。看加维度把组数放大多少。
  const keyGroups = {
    base: new Set(),              // obs | label | transform_set  (当前生产)
    plus_origin: new Set(),       // + origin_class
    plus_seq: new Set(),          // obs | label | transform_seq(有序计次)
    plus_origin_seq: new Set()    // + origin_class + transform_seq
  };
  for (const a of gated) {
    const lf = flowById.get(a.label_flow_id);
    if (!lf) continue;
    const obs = obsById.get(a.observation_id);
    const oid = a.observation_id || '';
    const lk = labelKey(lf.label || {});
    const tset = transformSet(lf, flowById, filterEventById);
    const tseq = transformSeq(lf, flowCtx, flowById, filterEventById);
    const oc = originClass(lf.origin_node || '', profileByNode);
    keyGroups.base.add(`${oid}|${lk}|${tset}`);
    keyGroups.plus_origin.add(`${oid}|${lk}|${tset}|${oc}`);
    keyGroups.plus_seq.add(`${oid}|${lk}|${tseq}`);
    keyGroups.plus_origin_seq.add(`${oid}|${lk}|${tseq}|${oc}`);
  }

  // 生产键健全性校验:直接数 doe-analyzer 挂在 assessment 上的真实 _dedup_key。
  //  - prodGroups 应与 plus_origin_seq(探针镜像)一致 → 证明镜像 == 生产。
  //  - node_id 泄漏检测:origin_class 段(第 4 段)若出现 node_ 前缀,说明实现误把节点 id
  //    带进键(过度切分),报警。origin_class 只应是 `${trust_boundary}/${data_surface}`。
  const prodGroups = new Set();
  let nodeIdLeak = 0;
  for (const a of gated) {
    const key = a._dedup_key || a._evidence_pack.unit_id;
    prodGroups.add(key);
    const originSeg = String(key).split('|')[3] || '';
    if (/(^|\/)node_/.test(originSeg)) nodeIdLeak++;
  }

  return {
    gated: gated.length,
    groupsTotal,
    groupsMulti,
    pathBinding,
    pathBindingMulti,
    exposedGroups,
    heteroOrigin,
    heteroPathSig,
    distinctObs,
    distinctBoundaries,
    mergeableObs,
    kBase: keyGroups.base.size,
    kOrigin: keyGroups.plus_origin.size,
    kSeq: keyGroups.plus_seq.size,
    kOriginSeq: keyGroups.plus_origin_seq.size,
    kProd: prodGroups.size,
    nodeIdLeak
  };
}

function main() {
  const files = nodefs.readdirSync(FCG_DIR).filter(f => f.endsWith('-sfg.json')).sort();
  const rows = [];
  const tot = { gated: 0, groupsTotal: 0, groupsMulti: 0, pathBinding: 0, pathBindingMulti: 0,
    exposedGroups: 0, heteroOrigin: 0, heteroPathSig: 0, distinctObs: 0, distinctBoundaries: 0, mergeableObs: 0,
    kBase: 0, kOrigin: 0, kSeq: 0, kOriginSeq: 0, kProd: 0, nodeIdLeak: 0 };

  for (const file of files) {
    let r;
    try {
      const j = JSON.parse(nodefs.readFileSync(path.join(FCG_DIR, file), 'utf8'));
      r = probeSkill(j);
    } catch (e) {
      console.error(`SKIP ${file}: ${e.message}`);
      continue;
    }
    const skill = file.replace('-sfg.json', '').replace(/^skill_\d+-\d+_/, '');
    rows.push({ skill: skill.slice(0, 28), ...r });
    for (const k of Object.keys(tot)) tot[k] += r[k];
  }

  const pct = (n, d) => d ? `${(100 * n / d).toFixed(1)}%` : '—';

  console.log('\n=== ① 路径咬人 & ② 组内异质(gated dedup 宇宙)===');
  console.log('skill'.padEnd(28), 'gated'.padStart(6), 'grps'.padStart(5), 'multi'.padStart(6),
    'pathBind'.padStart(9), 'exposed'.padStart(8), 'hetOrig'.padStart(8), 'hetSig'.padStart(7));
  for (const r of rows) {
    console.log(
      r.skill.padEnd(28),
      String(r.gated).padStart(6),
      String(r.groupsTotal).padStart(5),
      String(r.groupsMulti).padStart(6),
      String(r.pathBinding).padStart(9),
      String(r.exposedGroups).padStart(8),
      String(r.heteroOrigin).padStart(8),
      String(r.heteroPathSig).padStart(7));
  }
  console.log('-'.repeat(90));
  console.log('TOTAL'.padEnd(28),
    String(tot.gated).padStart(6),
    String(tot.groupsTotal).padStart(5),
    String(tot.groupsMulti).padStart(6),
    String(tot.pathBinding).padStart(9),
    String(tot.exposedGroups).padStart(8),
    String(tot.heteroOrigin).padStart(8),
    String(tot.heteroPathSig).padStart(7));

  console.log('\n=== 汇总解读 ===');
  console.log(`路径咬人组占比(pathBinding/groupsTotal): ${pct(tot.pathBinding, tot.groupsTotal)}`);
  console.log(`  其中多成员(真有合并损失风险): ${tot.pathBindingMulti} 组`);
  console.log(`② 暴露组中 origin_class 不恒定: ${tot.heteroOrigin}/${tot.exposedGroups} (${pct(tot.heteroOrigin, tot.exposedGroups)}) → origin 是否值得进键`);
  console.log(`② 暴露组中 path_purpose_sig 不恒定: ${tot.heteroPathSig}/${tot.exposedGroups} (${pct(tot.heteroPathSig, tot.exposedGroups)}) → 路径签名是否值得进键`);

  console.log('\n=== ③ 压缩机会(observation_id → boundary 元组)===');
  console.log(`distinct observation_id: ${tot.distinctObs}, distinct boundary 元组: ${tot.distinctBoundaries}`);
  console.log(`可合并 obs 数(免费压缩上限): ${tot.mergeableObs} (${pct(tot.mergeableObs, tot.distinctObs)} of distinct obs)`);

  console.log('\n=== 候选键送审量代价(gated 宇宙组数;组数=送审次数)===');
  console.log(`基线 base (obs|label|transform_set):        ${tot.kBase} 组`);
  console.log(`+origin_class:                              ${tot.kOrigin} 组  (+${tot.kOrigin - tot.kBase}, +${pct(tot.kOrigin - tot.kBase, tot.kBase)})`);
  console.log(`transform_seq(有序计次) 替换 set:           ${tot.kSeq} 组  (+${tot.kSeq - tot.kBase}, +${pct(tot.kSeq - tot.kBase, tot.kBase)})`);
  console.log(`+origin_class +transform_seq(全加):         ${tot.kOriginSeq} 组  (+${tot.kOriginSeq - tot.kBase}, +${pct(tot.kOriginSeq - tot.kBase, tot.kBase)})`);
  console.log(`\n注:基线 ${tot.kBase} 组 vs gated 单元 ${tot.gated} → 当前省 ${pct(tot.gated - tot.kBase, tot.gated)};`);
  console.log(`全加后 ${tot.kOriginSeq} 组 → 仍省 ${pct(tot.gated - tot.kOriginSeq, tot.gated)}。加维度换精度,看还剩多少节省。`);

  console.log('\n=== 生产键健全性校验(真实 _dedup_key)===');
  const match = tot.kProd === tot.kOriginSeq ? 'OK(镜像==生产)' : `MISMATCH(生产 ${tot.kProd} != 镜像 ${tot.kOriginSeq})`;
  console.log(`生产 _dedup_key 组数: ${tot.kProd}  vs 探针镜像 plus_origin_seq: ${tot.kOriginSeq} → ${match}`);
  console.log(`origin_class 段 node_id 泄漏计数(应为 0): ${tot.nodeIdLeak} ${tot.nodeIdLeak === 0 ? 'OK' : '!! 实现把 node_id 带进了键'}`);
}

main();
