const assert = require('node:assert/strict');
const { test } = require('node:test');

const { resolveLabelFlowPath, createFlowPathContext } = require('../src/flow-path-utils');

// P1: 溯源到本 label 的真引入点(origin_node)即停。parent 链是 provenance(指回上游
// 真源),当某步 source_introduction 一个新 label 时,链会继续接到上一段数据的源。
// 那段前缀对本 label 不是它的流路径,必须裁掉。
//
// Fixture: 用户提问(user.query, node_001)经 condition(node_268)后,llm.inference
// (node_002)source_introduction 出 file_content;file_content 再流到 write(node_381)。
// leaf 的 origin_node = node_002,resolved path 应从 node_002 起,丢弃 node_001/node_268。
function buildChainFcg() {
  const mk = (id, name) => ({ id, name, description: name });
  return {
    nodes: [
      mk('node_001', 'user.query'),
      mk('node_268', 'doc.step.condition'),
      mk('node_002', 'llm.inference'),
      mk('node_381', 'doc.step.write.skill')
    ],
    security_profile: {
      label_flows: [
        // 上一段:user_prompt 从 node_001 引入,流到 node_268
        { label_flow_id: 'lf_a', parent_label_flow_ids: [], current_node: 'node_001',
          origin_node: 'node_001', flow_mode: 'source_introduction',
          label: { label: 'ai_context.user_prompt', category: 'ai_context' } },
        { label_flow_id: 'lf_b', parent_label_flow_ids: ['lf_a'], current_node: 'node_268',
          incoming_edge_id: 'e_ab', origin_node: 'node_001', flow_mode: 'definite_flow',
          label: { label: 'ai_context.user_prompt', category: 'ai_context' } },
        // 引入点:file_content 在 node_002 被 source_introduction(current===origin)
        { label_flow_id: 'lf_c', parent_label_flow_ids: ['lf_b'], current_node: 'node_002',
          incoming_edge_id: 'e_bc', origin_node: 'node_002', flow_mode: 'source_introduction',
          label: { label: 'file_content.document', category: 'file_content' } },
        // 本 label 继续流到 sink
        { label_flow_id: 'lf_d', parent_label_flow_ids: ['lf_c'], current_node: 'node_381',
          incoming_edge_id: 'e_cd', origin_node: 'node_002', flow_mode: 'definite_flow',
          label: { label: 'file_content.document', category: 'file_content' } }
      ]
    }
  };
}

test('P1: resolved path is trimmed to the label origin_node (drops upstream prefix)', () => {
  const fcg = buildChainFcg();
  const ctx = createFlowPathContext(fcg);
  const leaf = ctx.flowById.get('lf_d');
  const r = resolveLabelFlowPath(leaf, ctx);

  // full chain is node_001 -> node_268 -> node_002 -> node_381 (4),
  // but file_content's true source is node_002, so prefix [node_001, node_268] is dropped.
  assert.deepEqual(r.node_path, ['node_002', 'node_381']);
  assert.deepEqual(r.node_names, ['llm.inference', 'doc.step.write.skill']);
  assert.equal(r.trimmed_prefix_count, 2);
  // edge_path aligns with the trimmed chain (e_cd only; e_bc belonged to the prefix hop into origin).
  assert.deepEqual(r.edge_path, ['e_cd']);
});

test('P1: no trim when origin_node is the chain root (well-formed single-source flow)', () => {
  const fcg = buildChainFcg();
  const ctx = createFlowPathContext(fcg);
  // lf_b: user_prompt, origin node_001 is the root — nothing to trim.
  const r = resolveLabelFlowPath(ctx.flowById.get('lf_b'), ctx);
  assert.deepEqual(r.node_path, ['node_001', 'node_268']);
  assert.equal(r.trimmed_prefix_count, 0);
});

test('P1: single-node introduced-and-here flow stays single node', () => {
  const fcg = buildChainFcg();
  const ctx = createFlowPathContext(fcg);
  // lf_c: file_content introduced at node_002, current === origin === node_002.
  const r = resolveLabelFlowPath(ctx.flowById.get('lf_c'), ctx);
  assert.deepEqual(r.node_path, ['node_002']);
  assert.equal(r.trimmed_prefix_count, 2);
});
