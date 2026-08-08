const assert = require('node:assert/strict');
const { test } = require('node:test');

const { buildEvidencePack, buildSharedTaskMemory, createEvidencePackContext } = require('../src/evidence-pack');

// Shared fixture: a 2-node flow (script source -> weather sink) crossing an
// external boundary, with a redaction transform on the source node.
function buildFixtureFcg() {
  const scriptNode = {
    id: 'node_script',
    name: 'script.function.hooks_handler_ts.l1.normalizeevent',
    description: 'Function normalizeEvent in hooks/handler.ts',
    location: { file: 'hooks/handler.ts', line: 1, section: 'function normalizeEvent' },
    semanticKind: 'script_function',
    ownerScript: 'hooks/handler.ts',
    functionName: 'normalizeEvent',
    instructionText: 'normalizeEvent reads the event path',
    formal_semantics: { operation_type: 'read' }
  };
  const node = {
    id: 'node_weather',
    name: 'weather.api',
    description: 'Call weather API',
    location: { file: 'workflow.md', line: 12, section: 'Send weather' },
    semanticKind: 'doc_step',
    ownerDoc: 'workflow.md',
    instructionText: 'Call weather.api with city and return the forecast.',
    formal_semantics: { operation_type: 'external_egress' }
  };
  return {
    meta: { skill_name: 'weather', skill_version: '1.0.0' },
    skill: { description: 'A weather skill' },
    documentation_context: {
      skill_context: { file: 'SKILL.md', role: 'review_context', line_count: 120, preview: 'Weather skill.' }
    },
    nodes: [scriptNode, node],
    security_profile: {
      observations: [{ observation_id: 'obs_1', node_id: 'node_weather', node_name: 'weather.api', boundary: { trust_boundary: 'external_network', receiver_scope: 'third_party_service' }, label_flow_ids: ['lf_1'] }],
      node_profiles: [
        { node_id: 'node_script', node_name: 'script.function.hooks_handler_ts.l1.normalizeevent', node_roles: ['data_introduction'], operation_tags: ['redaction'],
          action_steps: [
            { step_id: 'node_script:step_001:read', order: 1, operation_type: 'read', operation_tags: [] },
            { step_id: 'node_script:step_002:transform', order: 2, operation_type: 'transform', operation_tags: ['redaction'] }
          ] },
        { node_id: 'node_weather', node_name: 'weather.api', node_roles: ['external_egress'], security_tags: ['network_egress'] }
      ],
      provenance_graph: {
        events: {
          filtering: [
            { event_id: 'filter_1', type: 'redact_drop', node_id: 'node_script', from_label: { label: 'location.city', category: 'location' } }
          ]
        }
      },
      label_flows: [{
        label_flow_id: 'lf_1',
        parent_label_flow_ids: [],
        flow_mode: 'definite_flow',
        current_node: 'node_weather',
        node_path: ['node_script', 'node_weather'],
        node_names: ['script.function.hooks_handler_ts.l1.normalizeevent', 'weather.api'],
        edge_path: ['edge_1'],
        local_filter_event_ids: ['filter_1'],
        filter_events: [],
        label: { label: 'location.city', category: 'location', subtype: 'city', sensitivity: 'medium', field_name: 'city' }
      }]
    }
  };
}

test('evidence pack is flow-centric: label + sink_boundary + source-to-sink flow with transforms', () => {
  const fcg = buildFixtureFcg();
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({
    fcg,
    observation: sec.observations[0],
    labelFlow: sec.label_flows[0],
    nodeProfile: sec.node_profiles[1],
    context: ctx
  });

  // label: pure semantics, no internal ids
  assert.equal(pack.label.category, 'location');
  assert.equal(pack.label.subtype, 'city');
  assert.equal(pack.label.sensitivity, 'medium');
  assert.equal(pack.label.field_name, 'city');
  assert.equal(pack.label.label_flow_id, undefined);

  // sink_boundary: boundary + short enum tags
  assert.equal(pack.sink_boundary.node_name, 'weather.api');
  assert.equal(pack.sink_boundary.trust_boundary, 'external_network');
  assert.equal(pack.sink_boundary.receiver_scope, 'third_party_service');
  // node_roles removed from sink_boundary: the sink role now lives on the flow
  // sink node's capabilities (single-crossing invariant makes the sink unique).
  assert.equal(pack.sink_boundary.node_roles, undefined);
  assert.ok(pack.flow[pack.flow.length - 1].capabilities.includes('external_egress'));
  // sink_surface: on the sink flow node (not on sink_boundary)
  assert.equal(pack.sink_boundary.sink_surface, undefined);
  assert.equal(pack.sink_boundary.security_tags, undefined);

  // flow: source -> sink, with the redaction transform on the source node
  assert.equal(pack.flow.length, 2);
  assert.equal(pack.flow[0].role, 'source');
  assert.equal(pack.flow[1].role, 'sink');
  assert.equal(pack.flow[0].node_name, 'script.function.hooks_handler_ts.l1.normalizeevent');
  assert.equal(pack.flow[1].node_name, 'weather.api');
  // action text carries operation_type + instruction
  assert.ok(pack.flow[1].action.includes('weather.api'));
  assert.ok(pack.flow[1].action.startsWith('external_egress'));
  // transform on source node
  assert.equal(pack.flow[0].transform.type, 'redact_drop');
  assert.equal(pack.flow[0].transform.from_label, 'location.city');

  // multi-action source node: operations sequence with ordered ops + shaping tags
  assert.deepEqual(pack.flow[0].operations, [
    { op: 'read' },
    { op: 'transform', tags: ['redaction'] }
  ]);
  // single-action sink node keeps action, no operations
  assert.equal(pack.flow[1].operations, undefined);

  // No separate evidence[] index: grounding handles are the pack's own fields
  // (flow node_names + literal label/sink_boundary), not a redundant id list.
  assert.equal(pack.evidence, undefined);

  // task_memory_evidence_ids: identity + this flow's task nodes
  assert.ok(pack.task_memory_evidence_ids.includes('task.memory.identity'));
});

test('sink_boundary.reduction_before_egress surfaces the flow_state reduction antichain', () => {
  const fcg = buildFixtureFcg();
  const sec = fcg.security_profile;
  // Attach a v6 flow_state carrying a reduction antichain, and point the flow at it.
  sec.flow_states = [{ state_id: 'st_1', reduction_applied: true, reduction_profile: ['aggregate', 'summarization'] }];
  sec.label_flows[0].flow_state_id = 'st_1';

  const ctx = createEvidencePackContext(fcg);
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });

  // The specific reductions applied before egress are surfaced verbatim (not just a bool),
  // as a citable field on sink_boundary so the LLM judge sees WHICH reductions ran.
  assert.deepEqual(pack.sink_boundary.reduction_before_egress, ['aggregate', 'summarization']);
});

test('sink_boundary omits reduction_before_egress when the flow_state has no reduction', () => {
  const fcg = buildFixtureFcg();
  const sec = fcg.security_profile;
  // A flow_state that ran no reduction: raw data crossed the boundary -> field absent.
  sec.flow_states = [{ state_id: 'st_1', reduction_applied: false, reduction_profile: [] }];
  sec.label_flows[0].flow_state_id = 'st_1';

  const ctx = createEvidencePackContext(fcg);
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });

  assert.equal(pack.sink_boundary.reduction_before_egress, undefined);
  // A flow with no flow_state_id at all also omits it (no crash).
  const fcg2 = buildFixtureFcg();
  const ctx2 = createEvidencePackContext(fcg2);
  const pack2 = buildEvidencePack({ fcg: fcg2, observation: fcg2.security_profile.observations[0], labelFlow: fcg2.security_profile.label_flows[0], nodeProfile: fcg2.security_profile.node_profiles[1], context: ctx2 });
  assert.equal(pack2.sink_boundary.reduction_before_egress, undefined);
});

test('operations sequence preserves execution order so shaping-before-egress is visible', () => {
  const fcg = buildFixtureFcg();
  // Give the sink node a multi-step plan where slice happens BEFORE egress:
  // judge must be able to read this order from operations[].
  fcg.security_profile.node_profiles[1].action_steps = [
    { step_id: 'node_weather:step_001:transform', order: 1, operation_type: 'transform', operation_tags: ['field_slice'] },
    { step_id: 'node_weather:step_002:external_egress', order: 2, operation_type: 'external_egress', operation_tags: [] }
  ];
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });

  assert.deepEqual(pack.flow[1].operations, [
    { op: 'transform', tags: ['field_slice'] },
    { op: 'external_egress' }
  ]);
  // sink still keeps a human-readable action summary alongside operations
  assert.ok(pack.flow[1].action.length > 0);
});

test('sink_surface on sink flow node keeps output-surface tags and drops read-side noise', () => {
  const fcg = buildFixtureFcg();
  // sink node has both read-side and write-side security_tags;
  // sink_surface must appear on the sink flow node, not on sink_boundary,
  // and only output/persistence/exec surface tags survive.
  fcg.security_profile.node_profiles[1].security_tags = ['api_call', 'webhook_post', 'database_write', 'file_read', 'database_read', 'network_egress'];
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });

  // sink_surface on the sink node (last in flow)
  const sinkNode = pack.flow[pack.flow.length - 1];
  assert.equal(sinkNode.role, 'sink');
  const surface = sinkNode.sink_surface;
  assert.ok(surface.includes('api_call'));
  assert.ok(surface.includes('webhook_post'));
  assert.ok(surface.includes('database_write'));
  // read-side tags dropped
  assert.ok(!surface.includes('file_read'));
  assert.ok(!surface.includes('database_read'));
  // network_egress / third_party_service dropped (redundant with boundary fields)
  assert.ok(!surface.includes('network_egress'));
  // sink_boundary has no sink_surface
  assert.equal(pack.sink_boundary.sink_surface, undefined);
});

test('transform resolves from provenance_graph via local_filter_event_ids (not inline filter_events)', () => {
  const fcg = buildFixtureFcg();
  // filter_events on the flow is [] (post-serialization); the event body lives
  // in provenance_graph.events.filtering and is linked by local_filter_event_ids.
  assert.deepEqual(fcg.security_profile.label_flows[0].filter_events, []);
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });
  assert.equal(pack.flow[0].transform.type, 'redact_drop');
});

test('shared task memory is FCG-driven and every pack ref resolves into it', () => {
  const fcg = buildFixtureFcg();
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], nodeProfile: sec.node_profiles[1], context: ctx });

  const tm = buildSharedTaskMemory(fcg, ctx);
  assert.equal(tm.memory_type, 'extractive_shared_task_context');
  assert.equal(tm.skill_name, 'weather');
  assert.ok(tm.evidence.some(item => item.evidence_id === 'task.memory.identity'));
  assert.equal(tm.evidence.find(item => item.evidence_id === 'task.memory.identity').data.description, 'A weather skill');

  // No dangling task_memory references. (task_evidence_ids 已删,直接用 evidence[] 的 id 集校验)
  const tmIds = new Set(tm.evidence.map(item => item.evidence_id));
  for (const id of pack.task_memory_evidence_ids) {
    assert.ok(tmIds.has(id), `task_memory ref ${id} must resolve into shared memory`);
  }
});

test('a node that both introduces data and is its sink is marked source_sink', () => {
  const fcg = buildFixtureFcg();
  // Make the boundary node BOTH a data_introduction point and an egress sink:
  // one action that both introduces the label and sends it over the boundary.
  // Role is derived from node_roles (the node's own actions), so role must
  // capture both via source_sink.
  fcg.security_profile.node_profiles[1].node_roles = ['data_introduction', 'external_egress'];
  fcg.security_profile.label_flows.push({
    label_flow_id: 'lf_root',
    parent_label_flow_ids: [],
    flow_mode: 'source_introduction',
    current_node: 'node_weather',
    node_path: ['node_weather'],
    node_names: ['weather.api'],
    edge_path: [],
    filter_events: [],
    label: { label: 'location.city', category: 'location', subtype: 'city' }
  });
  fcg.security_profile.observations[0].label_flow_ids.push('lf_root');
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[1], nodeProfile: sec.node_profiles[1], context: ctx });
  // Single node whose own roles include both data_introduction and a sink-like role.
  assert.equal(pack.flow.length, 1);
  assert.equal(pack.flow[0].role, 'source_sink');
});

test('interior node with sink-like capability is role=transform (not a second sink), capability is preserved', () => {
  const fcg = buildFixtureFcg();
  // Insert a 3rd interior node that HAS a sink-like capability (command_execution)
  // but is not the flow's boundary node. role must be transform on this label flow;
  // its capability must surface separately so the judge can still see it.
  const interior = {
    id: 'node_mid',
    name: 'script.run.helper',
    description: 'Helper shell step',
    location: { file: 'scripts/helper.sh', line: 5 },
    semanticKind: 'script_call',
    instructionText: 'run helper',
    formal_semantics: { operation_type: 'invoke_tool' }
  };
  fcg.nodes.splice(1, 0, interior);
  fcg.security_profile.node_profiles.splice(1, 0, {
    node_id: 'node_mid',
    node_name: 'script.run.helper',
    node_roles: ['command_execution', 'tool_invocation']
  });
  const lf = fcg.security_profile.label_flows[0];
  lf.node_path = ['node_script', 'node_mid', 'node_weather'];
  lf.node_names = ['script.function.hooks_handler_ts.l1.normalizeevent', 'script.run.helper', 'weather.api'];

  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: lf, nodeProfile: sec.node_profiles[2], context: ctx });

  assert.equal(pack.flow.length, 3);
  assert.equal(pack.flow[0].role, 'source');
  // interior node: role is transform even though it CAN command_execute,
  assert.equal(pack.flow[1].role, 'transform');
  assert.deepEqual(pack.flow[1].capabilities, ['command_execution', 'tool_invocation']);
  // exactly one sink in the whole flow: the boundary node at the end.
  assert.equal(pack.flow[2].role, 'sink');
  assert.equal(pack.flow.filter(n => n.role === 'sink' || n.role === 'source_sink').length, 1);
});

test('identical transforms on one node are deduped into a single entry with count', () => {
  // 同一节点上多个无法区分的 filter 事件(同 type、无 from/to)摘要成相同 transform 对象。
  // 展示侧应合并计次,而非满屏重复。跨节点顺序由 dedup 键的 transform_seq 承载,与此无关。
  const fcg = {
    nodes: [{ id: 'n0', name: 'read.src' }, { id: 'n1', name: 'send.api' }],
    edges: [{ id: 'e1', source: 'n0', target: 'n1', type: 'data_dependency', data_flow: { from_param: 'a', to_param: 'b' } }],
    security_profile: {
      observations: [{ observation_id: 'o', node_id: 'n1', node_name: 'send.api', boundary: {}, label_flow_ids: ['lf'] }],
      node_profiles: [{ node_id: 'n0', node_roles: ['data_introduction'] }, { node_id: 'n1', node_roles: ['external_egress'] }],
      label_flows: [{
        label_flow_id: 'lf', parent_label_flow_ids: [], flow_mode: 'definite_flow',
        current_node: 'n1', origin_node: 'n0',
        node_path: ['n0', 'n1'], node_names: ['read.src', 'send.api'],
        edge_path: ['e1'], local_filter_event_ids: ['f1', 'f2', 'f3'], filter_events: [],
        label: { label: 'file_content.document', category: 'file_content', subtype: 'document' }
      }],
      provenance_graph: {
        events: {
          filtering: [
            { event_id: 'f1', node_id: 'n0', type: 'field_slice_keep' },
            { event_id: 'f2', node_id: 'n0', type: 'field_slice_keep' },
            { event_id: 'f3', node_id: 'n0', type: 'field_slice_keep' }
          ]
        }
      }
    }
  };
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], context: ctx });
  // 3 个相同事件 -> 单条 transform 带 count:3(不再是 transforms[3])
  assert.equal(pack.flow[0].transforms, undefined);
  assert.equal(pack.flow[0].transform.type, 'field_slice_keep');
  assert.equal(pack.flow[0].transform.count, 3);
});

test('a single transform on a node carries no count field (avoid count:1 noise)', () => {
  const fcg = {
    nodes: [{ id: 'n0', name: 'read.src' }, { id: 'n1', name: 'send.api' }],
    edges: [{ id: 'e1', source: 'n0', target: 'n1', type: 'data_dependency', data_flow: { from_param: 'a', to_param: 'b' } }],
    security_profile: {
      observations: [{ observation_id: 'o', node_id: 'n1', node_name: 'send.api', boundary: {}, label_flow_ids: ['lf'] }],
      node_profiles: [{ node_id: 'n0', node_roles: ['data_introduction'] }, { node_id: 'n1', node_roles: ['external_egress'] }],
      label_flows: [{
        label_flow_id: 'lf', parent_label_flow_ids: [], flow_mode: 'definite_flow',
        current_node: 'n1', origin_node: 'n0',
        node_path: ['n0', 'n1'], node_names: ['read.src', 'send.api'],
        edge_path: ['e1'], local_filter_event_ids: ['f1'], filter_events: [],
        label: { label: 'file_content.document', category: 'file_content', subtype: 'document' }
      }],
      provenance_graph: { events: { filtering: [{ event_id: 'f1', node_id: 'n0', type: 'field_slice_keep' }] } }
    }
  };
  const ctx = createEvidencePackContext(fcg);
  const sec = fcg.security_profile;
  const pack = buildEvidencePack({ fcg, observation: sec.observations[0], labelFlow: sec.label_flows[0], context: ctx });
  assert.equal(pack.flow[0].transform.type, 'field_slice_keep');
  assert.equal(pack.flow[0].transform.count, undefined);
});

