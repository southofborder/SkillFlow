const test = require('node:test');
const assert = require('node:assert/strict');

const { generateFCGJson } = require('../src/output/json-generator');
const { getOntologyVersion } = require('../src/security/label-ontology');

test('label flows keep at most one direct parent', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      sourceNode('node_002', 'read.api_key', { api_key: { type: 'string' } }),
      transformNode('node_003', 'mergeProfiles', {
        input: { left: { type: 'object' }, right: { type: 'object' } },
        output: { profile: { type: 'object' } }
      }),
      transformNode('node_004', 'countStats', {
        input: { profile: { type: 'object' } },
        output: { stats: { type: 'object' } }
      }),
      sinkNode('node_005', 'write.report.md', { content: { type: 'object' } }, false),
      sourceNode('node_006', 'read.report.md', { content: { type: 'object' } }),
      sinkNode('node_007', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_003', 'email', 'left'),
      edge('node_002', 'node_003', 'api_key', 'right'),
      edge('node_003', 'node_004', 'profile', 'profile'),
      edge('node_004', 'node_005', 'stats', 'content'),
      edge('node_006', 'node_007', 'content', 'payload')
    ]
  });

  assert.ok(result.security_profile.label_flows.length > 0);
  assert.ok(result.security_profile.label_flows.every(flow => (flow.parent_label_flow_ids || []).length <= 1));
  assert.ok(result.security_profile.provenance_graph.label_flow_nodes.every(flow => (flow.parent_label_flow_ids || []).length <= 1));
});
test('node profiles create multiple labels for one data-introduction node', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.userProfile', {
        email: { type: 'string' },
        phone: { type: 'string' },
        api_key: { type: 'string' }
      }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'profile', 'payload')]
  });

  const sourceProfile = profile(result, 'node_001');
  const labels = sourceProfile.data_profile.labels.map(label => label.label);

  assert.equal(result.security_profile.version, '5.1');
  assert.ok(sourceProfile.node_roles.includes('data_introduction'));
  assert.ok(labels.includes('credentials.api_key'));
  assert.ok(labels.includes('pii.email'));
  assert.ok(labels.includes('pii.phone'));
  assert.equal(sourceProfile.data_profile.sensitivity, 'critical');
  assert.ok(sourceProfile.data_profile.labels.every(label => label.ontology_version === getOntologyVersion()));
  assert.ok(result.security_profile.statistics.label_ontology_label_count > 0);
  assert.ok(result.security_profile.label_flows.some(instance => instance.current_node === 'node_001'));
});

test('mid-path data introduction keeps user query as trigger context without forwarding prompt payload', () => {
  const result = generateFixture({
    nodes: [
      userQueryNode('node_001'),
      sourceNode('node_002', 'read.api_key', { api_key: { type: 'string' } }),
      sinkNode('node_003', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'query_text', 'trigger'),
      edge('node_002', 'node_003', 'api_key', 'payload')
    ]
  });

  const webhookObservation = observations(result, 'node_003').find(obs => (
    hasObservationLabel(result, obs, 'credentials.api_key') &&
    observationFlows(result, obs).some(flow => (flow.trigger_context || []).some(context => context.node_name === 'user.query'))
  ));

  assert.ok(webhookObservation);
  assert.ok(observationFlows(result, webhookObservation).some(flow => flow.origin_node_name === 'read.api_key'));
  assert.ok(!hasObservationLabel(result, webhookObservation, 'user_prompt.query'));
  const apiKeyFlow = observationFlows(result, webhookObservation).find(flow => flow.label.label === 'credentials.api_key');
  assert.deepEqual(resolveFlowPath(result, apiKeyFlow).node_names, ['read.api_key', 'send.webhook']);
});

test('semantic derivation can extract credentials from user prompt on outgoing propagation', () => {
  const result = generateFixture({
    nodes: [
      userQueryNode('node_001'),
      transformNode('node_002', 'extract.api_key.from_prompt', {
        input: { query_text: { type: 'string' } },
        output: { api_key: { type: 'string' } }
      }),
      sinkNode('node_003', 'external.api.call', { api_key: { type: 'string' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'query_text', 'query_text'),
      edge('node_002', 'node_003', 'api_key', 'api_key')
    ]
  });

  const apiObservation = observations(result, 'node_003').find(obs => hasObservationLabel(result, obs, 'credentials.api_key'));
  const apiKeyLabel = observationLabels(result, apiObservation).find(label => label.label === 'credentials.api_key');

  assert.ok(apiObservation);
  assert.equal(apiKeyLabel.origin_node, 'node_001');
  assert.equal(apiKeyLabel.introduced_at, 'node_002');
  assert.ok(observationFlows(result, apiObservation).some(flow => (flow.trigger_context || []).some(context => context.node_name === 'user.query')));
  assert.ok(observationFlows(result, apiObservation).some(flow => flowHasFilterEventType(result, flow, 'semantic_derivation')));
  assert.ok(result.security_profile.provenance_graph.events.filtering.some(event => event.type === 'semantic_derivation'));
});

test('field slice filters labels for successors, not for the extracting node input', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.userProfile', {
        email: { type: 'string' },
        phone: { type: 'string' },
        city: { type: 'string' }
      }),
      transformNode('node_002', 'extractCity', {
        input: { profile: { type: 'object' } },
        output: { city: { type: 'string' } }
      }),
      sinkNode('node_003', 'weather.api', { city: { type: 'string' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'profile', 'profile'),
      edge('node_002', 'node_003', 'city', 'city')
    ]
  });

  const extractInstance = instancesAt(result, 'node_002').find(instance => hasInstanceLabel(instance, 'pii.email'));
  const weatherObservation = observations(result, 'node_003').find(obs => hasObservationLabel(result, obs, 'location.city'));

  assert.ok(extractInstance);
  assert.deepEqual(uniqueLabels(observationLabels(result, weatherObservation)), ['location.city']);
  assert.ok(observationFlows(result, weatherObservation).some(flow => flowHasFilterEventType(result, flow, 'field_slice_keep')));
});

test('redaction removes credential labels before local persistence observation', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.configFile', {
        api_key: { type: 'string' },
        content: { type: 'string' }
      }),
      transformNode('node_002', 'redactSecrets', {
        input: { content: { type: 'string' } },
        output: { safe_content: { type: 'string' } }
      }),
      sinkNode('node_003', 'write.report', { safe_content: { type: 'string' } }, false)
    ],
    edges: [
      edge('node_001', 'node_002', 'content', 'content'),
      edge('node_002', 'node_003', 'safe_content', 'safe_content')
    ]
  });

  const reportObservation = observations(result, 'node_003')[0];

  assert.ok(reportObservation);
  assert.ok(!observationLabels(result, reportObservation).some(label => label.category === 'credentials'));
  assert.ok(result.security_profile.provenance_graph.events.filtering.some(event => event.type === 'redact_drop'));
  assert.ok(instancesAt(result, 'node_001').some(instance => hasInstanceLabel(instance, 'credentials.api_key')));
});

test('step-level doc flow order applies redaction before write observation', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.configFile', {
        api_key: { type: 'string' },
        content: { type: 'string' }
      }),
      docStepNode('node_002', 'doc.step.skill.l10.s1.transform.report', 'transform', 'Redact api_key from report.md'),
      docStepNode('node_003', 'doc.step.skill.l11.s2.write.report_md', 'write', 'Write report.md')
    ],
    edges: [
      edge('node_001', 'node_002', 'content', 'context'),
      edge('node_002', 'node_003', 'safe_content', 'content')
    ]
  });

  const writeObservation = observations(result, 'node_003')[0];

  assert.ok(writeObservation);
  assert.equal(writeObservation.operation_type, 'write');
  assert.ok(!hasObservationLabel(result, writeObservation, 'credentials.api_key'));
});

test('step-level doc flow order observes write before later redaction', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.configFile', {
        api_key: { type: 'string' },
        content: { type: 'string' }
      }),
      docStepNode('node_002', 'doc.step.skill.l10.s1.write.report_md', 'write', 'Write report.md'),
      docStepNode('node_003', 'doc.step.skill.l11.s2.transform.report', 'transform', 'Redact api_key from report.md')
    ],
    edges: [
      edge('node_001', 'node_002', 'content', 'content'),
      edge('node_002', 'node_003', 'content', 'context')
    ]
  });

  const writeObservation = observations(result, 'node_002')[0];

  assert.ok(writeObservation);
  assert.equal(writeObservation.operation_type, 'write');
  assert.ok(hasObservationLabel(result, writeObservation, 'credentials.api_key'));
});

test('LLM-consuming summarization observes raw email and propagates summary only', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email_message: { type: 'string' } }),
      docStepNode('node_002', 'doc.step.skill.l10.s1.transform.email', 'transform', 'Summarize the email content'),
      docStepNode('node_003', 'doc.step.skill.l11.s2.write.summary', 'write', 'Save the summary locally')
    ],
    edges: [
      edge('node_001', 'node_002', 'email_message', 'context'),
      edge('node_002', 'node_003', 'summary', 'content')
    ]
  });

  const summarizeObservation = observations(result, 'node_002').find(obs => obs.operation_type === 'transform');
  const writeObservation = observations(result, 'node_003')[0];

  assert.ok(summarizeObservation);
  assert.ok(hasObservationLabel(result, summarizeObservation, 'communication.email_message'));
  assert.ok(writeObservation);
  assert.ok(hasObservationLabel(result, writeObservation, 'aggregate_data.summary'));
  assert.ok(!hasObservationLabel(result, writeObservation, 'communication.email_message'));
});

test('aggregation downgrades raw labels into aggregate_data', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.databaseRecords', {
        email: { type: 'string' },
        record_id: { type: 'string' }
      }),
      transformNode('node_002', 'countStats', {
        input: { records: { type: 'array' } },
        output: { count: { type: 'number' } }
      }),
      sinkNode('node_003', 'llm.inference', { stats: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'records', 'records'),
      edge('node_002', 'node_003', 'count', 'stats')
    ]
  });

  const llmObservation = observations(result, 'node_003').find(obs => hasObservationLabel(result, obs, 'aggregate_data.summary'));

  assert.ok(llmObservation);
  assert.deepEqual(uniqueLabels(observationLabels(result, llmObservation)), ['aggregate_data.summary']);
  const summaryFlows = observationFlows(result, llmObservation).filter(flow => flow.label.label === 'aggregate_data.summary');
  assert.ok(summaryFlows.length >= 1);
  assert.ok(summaryFlows.every(flow => flow.parent_label_flow_ids.length === 1));
  assert.ok(summaryFlows.every(flow => flowHasFilterEventType(result, flow, 'aggregate')));
  assert.ok(summaryFlows.some(flow => Number(flow.merged_path_count || 1) >= 2));
});

test('intermediate sink creates an observation before downstream transformation', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.userProfile', {
        email: { type: 'string' },
        city: { type: 'string' }
      }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } }),
      transformNode('node_003', 'redactEmail', {
        input: { payload: { type: 'object' } },
        output: { city: { type: 'string' } }
      }),
      sinkNode('node_004', 'llm.inference', { city: { type: 'string' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'profile', 'payload'),
      edge('node_002', 'node_003', 'payload', 'payload'),
      edge('node_003', 'node_004', 'city', 'city')
    ]
  });

  const webhookObservation = observations(result, 'node_002').find(obs => hasObservationLabel(result, obs, 'pii.email'));
  const llmObservation = observations(result, 'node_004').find(obs => hasObservationLabel(result, obs, 'location.city'));

  assert.ok(webhookObservation);
  assert.ok(hasObservationLabel(result, webhookObservation, 'pii.email'));
  assert.ok(hasObservationLabel(result, webhookObservation, 'location.city'));
  assert.ok(llmObservation);
  assert.ok(!hasObservationLabel(result, llmObservation, 'pii.email'));
});

test('plain join keeps incoming label flows separate and does not union labels', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.city', { city: { type: 'string' } }),
      sourceNode('node_002', 'get.email', { email: { type: 'string' } }),
      transformNode('node_003', 'normalizePayload', {
        input: { value: { type: 'object' } },
        output: { value: { type: 'object' } }
      }),
      sinkNode('node_004', 'llm.inference', { value: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_003', 'city', 'value'),
      edge('node_002', 'node_003', 'email', 'value'),
      edge('node_003', 'node_004', 'value', 'value')
    ]
  });

  const joinedInstances = instancesAt(result, 'node_003');
  const llmObservations = observations(result, 'node_004');

  assert.equal(joinedInstances.filter(instance => hasInstanceLabel(instance, 'location.city')).length, 1);
  assert.equal(joinedInstances.filter(instance => hasInstanceLabel(instance, 'pii.email')).length, 1);
  const llmObservation = llmObservations[0];
  assert.ok(observationFlows(result, llmObservation).some(flow => flow.label.label === 'location.city'));
  assert.ok(observationFlows(result, llmObservation).some(flow => flow.label.label === 'pii.email'));
  assert.ok(observationFlows(result, llmObservation).every(flow => flow.label.label === 'location.city' || flow.label.label === 'pii.email'));
});

test('path-aggregated propagation merges equivalent paths without losing label binding', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      transformNode('node_002', 'normalizeEmailA', {
        input: { email: { type: 'string' } },
        output: { email: { type: 'string' } }
      }),
      transformNode('node_003', 'normalizeEmailB', {
        input: { email: { type: 'string' } },
        output: { email: { type: 'string' } }
      }),
      sinkNode('node_004', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'email', 'email'),
      edge('node_001', 'node_003', 'email', 'email'),
      edge('node_002', 'node_004', 'email', 'payload'),
      edge('node_003', 'node_004', 'email', 'payload')
    ]
  });

  const webhookObservation = observations(result, 'node_004')[0];
  const webhookFlows = observationFlows(result, webhookObservation)
    .filter(flow => flow.label.label === 'pii.email');
  const flowStates = result.security_profile.flow_states || [];
  const webhookStates = flowStates.filter(state =>
    state.node_id === 'node_004' &&
    state.label?.label === 'pii.email'
  );

  assert.equal(webhookFlows.length, 1);
  assert.equal(webhookStates.length, 1);
  assert.ok(webhookStates[0].merged_path_count >= 2);
  assert.equal(webhookFlows[0].flow_state_id, webhookStates[0].state_id);
  assert.ok((webhookFlows[0].representative_path_ids || []).length > 0);
  assert.ok(hasObservationLabel(result, webhookObservation, 'pii.email'));
});

test('explicit merge_join records related single-label flows without creating multi-label flows', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'get.city', { city: { type: 'string' } }),
      sourceNode('node_002', 'get.email', { email: { type: 'string' } }),
      transformNode('node_003', 'mergeProfiles', {
        input: { left: { type: 'object' }, right: { type: 'object' } },
        output: { profile: { type: 'object' } }
      }),
      sinkNode('node_004', 'llm.inference', { profile: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_003', 'city', 'left'),
      edge('node_002', 'node_003', 'email', 'right'),
      edge('node_003', 'node_004', 'profile', 'profile')
    ]
  });

  const mergeEvents = result.security_profile.provenance_graph.events.merge.filter(event => event.type === 'merge_join');
  const nodeFlows = instancesAt(result, 'node_003');
  const cityFlow = nodeFlows.find(flow => hasInstanceLabel(flow, 'location.city'));
  const emailFlow = nodeFlows.find(flow => hasInstanceLabel(flow, 'pii.email'));
  const llmObservations = observations(result, 'node_004');

  assert.ok(cityFlow);
  assert.ok(emailFlow);
  assert.ok(mergeEvents.length > 0);
  assert.ok(cityFlow.related_label_flow_id_count > 0);
  assert.ok(emailFlow.related_label_flow_id_count > 0);
  assert.ok(mergeEvents.some(event => (event.label_flow_ids || []).includes(cityFlow.label_flow_id)));
  assert.ok(mergeEvents.some(event => (event.label_flow_ids || []).includes(emailFlow.label_flow_id)));
  assert.ok(cityFlow.parent_label_flow_ids.length <= 1);
  assert.ok(emailFlow.parent_label_flow_ids.length <= 1);
  assert.ok(cityFlow.parent_label_flow_ids.length <= 1);
  assert.ok(emailFlow.parent_label_flow_ids.length <= 1);
  const llmObservation = llmObservations[0];
  assert.ok(observationFlows(result, llmObservation).some(flow => flow.label.label === 'location.city'));
  assert.ok(observationFlows(result, llmObservation).some(flow => flow.label.label === 'pii.email'));
  assert.ok(observationFlows(result, llmObservation).every(flow => Number(flow.merge_group_id_count || 0) > 0));
});

test('fine-grained ontology labels propagate into instances and observations', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.secureArtifacts', {
        private_key: { type: 'string' },
        session_cookie: { type: 'string' },
        passport_number: { type: 'string' },
        calendar_event: { type: 'object' },
        ip_address: { type: 'string' },
        source_code: { type: 'string' },
        medical_record: { type: 'object' }
      }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'payload', 'payload')]
  });

  const expected = [
    'credentials.private_key',
    'credentials.session_cookie',
    'pii.passport_number',
    'communication.calendar_event',
    'device_data.ip_address',
    'file_content.source_code',
    'health.medical_record'
  ];
  const sourceLabels = profile(result, 'node_001').data_profile.labels.map(label => label.label);
  const webhookObservation = observations(result, 'node_002')[0];
  const observedLabels = observationLabels(result, webhookObservation).map(label => label.label);

  for (const label of expected) {
    assert.ok(sourceLabels.includes(label), `${label} should be in source profile`);
    assert.ok(observedLabels.includes(label), `${label} should propagate to observation`);
  }
  assert.ok(observationLabels(result, webhookObservation).every(label => label.ontology_version === getOntologyVersion()));
});

test('v3 ontology labels propagate into instances and observations', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.v3SensitiveBundle', {
        service_account_key: { type: 'string' },
        database_url: { type: 'string' },
        genetic_data: { type: 'object' },
        lab_result: { type: 'object' },
        iris_scan: { type: 'string' },
        system_prompt: { type: 'string' },
        training_data: { type: 'array' },
        audit_log: { type: 'string' }
      }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'payload', 'payload')]
  });

  const expected = [
    'credentials.service_account_key',
    'credentials.database_connection_string',
    'special_category.genetic_data',
    'health.lab_result',
    'biometric.iris',
    'ai_context.system_prompt',
    'enterprise.training_data',
    'security_data.audit_log'
  ];
  const sourceLabels = profile(result, 'node_001').data_profile.labels.map(label => label.label);
  const webhookObservation = observations(result, 'node_002')[0];
  const observedLabels = observationLabels(result, webhookObservation).map(label => label.label);

  for (const label of expected) {
    assert.ok(sourceLabels.includes(label), `${label} should be in source profile`);
    assert.ok(observedLabels.includes(label), `${label} should propagate to observation`);
  }
});

test('produce_artifact with object context preserves original label flow and records production', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      produceArtifactNode('node_002', 'Generate a report about the email', {
        producedObject: 'report',
        consumedObject: 'email'
      }),
      sinkNode('node_003', 'upload.report.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'email', 'context', 'doc_flow_object_context'),
      edge('node_002', 'node_003', 'report', 'payload')
    ]
  });

  const generateProfile = profile(result, 'node_002');
  const generatedFlows = result.security_profile.label_flows.filter(flow => (
    flow.label.label === 'file_content.document' &&
    flow.label.origin_node === 'node_002'
  ));
  const uploadObservation = observations(result, 'node_003').find(obs => hasObservationLabel(result, obs, 'pii.email'));
  const artifactEvents = result.security_profile.provenance_graph.events.filtering.filter(event => (
    event.type === 'artifact_production' &&
    event.node_id === 'node_002'
  ));

  assert.ok(generateProfile.node_roles.includes('data_introduction'));
  assert.ok(generateProfile.node_roles.includes('local_persistence'));
  assert.equal(generatedFlows.length, 0);
  assert.ok(uploadObservation);
  assert.ok(hasObservationLabel(result, uploadObservation, 'pii.email'));
  assert.ok(artifactEvents.length > 0);
  assert.ok(artifactEvents.every(event => event.produced_object_text === 'report'));
});

test('produce_artifact without object context emits unparented generated source flow', () => {
  const result = generateFixture({
    nodes: [
      produceArtifactNode('node_001', 'Generate a report about current AI', {
        producedObject: 'report',
        consumedObject: ''
      }),
      sinkNode('node_002', 'upload.report.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'report', 'payload')]
  });

  const generateProfile = profile(result, 'node_001');
  const generateFlows = result.security_profile.label_flows.filter(flow => (
    flow.label.label === 'file_content.document' &&
    flow.label.origin_node === 'node_001'
  ));

  assert.ok(generateProfile.node_roles.includes('data_introduction'));
  assert.ok(generateFlows.some(flow => (flow.parent_label_flow_ids || []).length === 0));
});

test('write node does not become generated data source', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      docStepNode('node_002', 'doc.step.skill.l10.s1.write.report', 'write', 'Write the email content to a local file')
    ],
    edges: [edge('node_001', 'node_002', 'email', 'content')]
  });

  const writeProfile = profile(result, 'node_002');
  const writeFlows = instancesAt(result, 'node_002');

  assert.ok(!writeProfile.node_roles.includes('data_introduction'));
  assert.ok(writeFlows.every(flow => flow.label.label !== 'file_content.document'));
});


function labelFlowMap(result) {
  return new Map(result.security_profile.label_flows.map(flow => [flow.label_flow_id, flow]));
}

function resolveFlowPath(result, flow = {}) {
  if (Array.isArray(flow.node_path) && flow.node_path.length) {
    return {
      node_path: flow.node_path,
      node_names: flow.node_names || flow.node_path,
      edge_path: flow.edge_path || []
    };
  }
  const byId = labelFlowMap(result);
  const nodeById = new Map(result.nodes.map(node => [node.id, node]));
  const chain = [];
  const seen = new Set();
  let current = flow;
  while (current && typeof current === 'object') {
    const id = current.label_flow_id || current.representative_path_id || `${current.current_node || ''}:${chain.length}`;
    if (!id || seen.has(id)) break;
    seen.add(id);
    chain.unshift(current);
    const parentId = (current.parent_label_flow_ids || [])[0] || '';
    current = parentId ? byId.get(parentId) : null;
  }
  const node_path = [];
  const edge_path = [];
  for (const item of chain) {
    if (item.current_node && node_path[node_path.length - 1] !== item.current_node) node_path.push(item.current_node);
    if (item.incoming_edge_id) edge_path.push(item.incoming_edge_id);
  }
  return {
    node_path,
    node_names: node_path.map(nodeId => nodeById.get(nodeId)?.name || nodeId),
    edge_path
  };
}

function flowHasFilterEventType(result, flow = {}, type = '') {
  const eventsById = new Map((result.security_profile.provenance_graph.events.filtering || [])
    .map(event => [event.event_id, event]));
  for (const eventId of flow.local_filter_event_ids || []) {
    if (eventsById.get(eventId)?.type === type) return true;
  }
  for (const event of flow.filter_events || []) {
    if (event.type === type) return true;
  }
  const byId = labelFlowMap(result);
  const seen = new Set();
  let current = flow;
  while (current && typeof current === 'object') {
    const flowId = current.label_flow_id || '';
    if (!flowId || seen.has(flowId)) break;
    seen.add(flowId);
    if ((result.security_profile.provenance_graph.events.filtering || [])
      .some(event => event.label_flow_id === flowId && event.type === type)) {
      return true;
    }
    const parentId = (current.parent_label_flow_ids || [])[0] || '';
    current = parentId ? byId.get(parentId) : null;
  }
  return false;
}

function observationFlows(result, observation) {
  const byId = labelFlowMap(result);
  return (observation?.label_flow_ids || []).map(id => byId.get(id)).filter(Boolean);
}

function observationLabels(result, observation) {
  return observationFlows(result, observation).map(flow => flow.label).filter(Boolean);
}

function hasObservationLabel(result, observation, label) {
  return observationFlows(result, observation).some(flow => flow.label?.label === label);
}


test('storage bridge reintroduces labels from a persisted file read', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.userProfile', { email: { type: 'string' } }),
      sinkNode('node_002', 'write.report.md', { content: { type: 'object' } }, false),
      sourceNode('node_003', 'read.report.md', { content: { type: 'object' } }),
      sinkNode('node_004', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'email', 'content'),
      edge('node_003', 'node_004', 'content', 'payload')
    ]
  });

  const webhookObservation = observations(result, 'node_004')[0];
  const webhookFlows = observationFlows(result, webhookObservation);
  const emailFlow = webhookFlows.find(flow => flow.label.label === 'pii.email');

  assert.ok(emailFlow);
  assert.equal(emailFlow.storage_key, 'local_file:report.md');
  assert.ok(emailFlow.parent_label_flow_ids.length > 0);
  const parentFlow = labelFlowMap(result).get(emailFlow.parent_label_flow_ids[0]);
  assert.equal(parentFlow.current_node, 'node_003');
  assert.equal(parentFlow.parent_label_flow_ids.length, 1);
  const writtenFlow = labelFlowMap(result).get(parentFlow.parent_label_flow_ids[0]);
  assert.equal(writtenFlow.current_node, 'node_002');

  // 存储读跳无图边,但 edge_path 必须补合成哨兵边以维持位置契约 len(edge)==len(node)-1
  // (下游 DOE 按 edge[i] 连 node[i]->node[i+1] 消费;缺一条会让后续 link 错位一格)。
  assert.equal(parentFlow.flow_mode, 'storage_read');
  assert.equal(parentFlow.edge_path.length, parentFlow.node_path.length - 1);
  assert.ok(parentFlow.edge_path[parentFlow.edge_path.length - 1].startsWith('storage_read:'));
});

test('storage merge relates multiple labels written to the same persisted file', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      sourceNode('node_002', 'read.api_key', { api_key: { type: 'string' } }),
      sinkNode('node_003', 'write.report.md', { content: { type: 'object' } }, false),
      sourceNode('node_004', 'read.report.md', { content: { type: 'object' } }),
      sinkNode('node_005', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_003', 'email', 'content'),
      edge('node_002', 'node_003', 'api_key', 'content'),
      edge('node_004', 'node_005', 'content', 'payload')
    ]
  });

  const webhookObservation = observations(result, 'node_005')[0];
  const flows = observationFlows(result, webhookObservation);
  const emailFlow = flows.find(flow => flow.label.label === 'pii.email');
  const keyFlow = flows.find(flow => flow.label.label === 'credentials.api_key');
  const storageMerge = result.security_profile.provenance_graph.events.merge.find(event => event.type === 'storage_merge');

  assert.ok(emailFlow);
  assert.ok(keyFlow);
  assert.equal(emailFlow.storage_key, 'local_file:report.md');
  assert.equal(keyFlow.storage_key, 'local_file:report.md');
  assert.ok(storageMerge);
  assert.equal(storageMerge.storage_key, 'local_file:report.md');
  assert.ok(Number(emailFlow.merge_group_id_count || 0) > 0);
  assert.ok(Number(keyFlow.merge_group_id_count || 0) > 0);
  assert.ok(Number(storageMerge.label_flow_id_count || 0) >= 2);
  assert.equal(emailFlow.parent_label_flow_ids.length, 1);
  assert.equal(keyFlow.parent_label_flow_ids.length, 1);
  assert.notEqual(emailFlow.parent_label_flow_ids[0], keyFlow.parent_label_flow_ids[0]);
  assert.ok(flows.every(flow => !Array.isArray(flow.label)));
});

test('storage bridge does not connect different persisted files', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      sinkNode('node_002', 'write.report.md', { content: { type: 'object' } }, false),
      sourceNode('node_003', 'read.other.md', { content: { type: 'object' } }),
      sinkNode('node_004', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'email', 'content'),
      edge('node_003', 'node_004', 'content', 'payload')
    ]
  });

  const webhookObservation = observations(result, 'node_004')[0];
  const flows = observationFlows(result, webhookObservation);

  assert.ok(!flows.some(flow => flow.label.label === 'pii.email' && flow.storage_key === 'local_file:report.md'));
});

test('node profiles expose ordered action steps from member_steps', () => {
  const result = generateFixture({
    nodes: [
      {
        id: 'node_001',
        name: 'doc.op.multi',
        type: 'custom_func',
        category: 'Intermediate',
        input: { content: { type: 'string' } },
        output: { safe_content: { type: 'string' } },
        member_steps: [
          { line: 10, operation_type: 'read', instruction: 'Read report.md' },
          { line: 11, operation_type: 'transform', instruction: 'Redact secrets from report.md' },
          { line: 12, operation_type: 'write', instruction: 'Write report.md' }
        ]
      }
    ],
    edges: []
  });

  const nodeProfile = profile(result, 'node_001');

  assert.equal(nodeProfile.has_multi_action, true);
  assert.equal(nodeProfile.action_order_source, 'member_steps');
  assert.deepEqual(nodeProfile.action_steps.map(step => step.operation_type), ['read', 'transform', 'write']);
  assert.equal(nodeProfile.ambiguous_action_order, false);
});

test('observation records action step context without copying flow facts', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      sinkNode('node_002', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [edge('node_001', 'node_002', 'email', 'payload')]
  });

  const webhookObservation = observations(result, 'node_002')[0];

  assert.ok(webhookObservation.action_step_id);
  assert.equal(webhookObservation.operation_type, 'external_egress');
  assert.equal(typeof webhookObservation.order_confidence, 'number');
  assert.ok(Array.isArray(webhookObservation.label_flow_ids));
  assert.equal(Object.hasOwn(webhookObservation, 'observed_label_flows'), false);
  assert.equal(Object.hasOwn(webhookObservation, 'received_labels'), false);
});

test('explicit redact before write prevents redacted credentials from storage observation', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.config', { api_key: { type: 'string' }, content: { type: 'string' } }),
      {
        id: 'node_002',
        name: 'redact.then.write.report.md',
        type: 'custom_func',
        category: 'Sink',
        input: { content: { type: 'string' } },
        output: { safe_content: { type: 'string' } },
        member_steps: [
          { line: 1, operation_type: 'transform', instruction: 'Redact api_key from content' },
          { line: 2, operation_type: 'write', instruction: 'Write report.md' }
        ]
      }
    ],
    edges: [edge('node_001', 'node_002', 'content', 'content')]
  });

  const writeObservation = observations(result, 'node_002').find(obs => obs.operation_type === 'write');

  assert.ok(writeObservation);
  assert.ok(!hasObservationLabel(result, writeObservation, 'credentials.api_key'));
});

test('ambiguous sink and filter node emits conservative pre-action observation', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      {
        id: 'node_002',
        name: 'redactEmailAndSendWebhook',
        type: 'custom_func',
        category: 'Sink',
        input: { payload: { type: 'object' } },
        output: { payload: { type: 'object' } }
      }
    ],
    edges: [edge('node_001', 'node_002', 'email', 'payload')]
  });

  const nodeProfile = profile(result, 'node_002');
  const webhookObservation = observations(result, 'node_002').find(obs => obs.ambiguous_action_order === true);

  assert.equal(nodeProfile.ambiguous_action_order, true);
  assert.ok(webhookObservation);
  assert.ok(hasObservationLabel(result, webhookObservation, 'pii.email'));
  assert.ok(result.security_profile.provenance_graph.events.observation.some(event => event.reason === 'pre_action_observation'));
});

test('public security profile keeps representative path and provenance id bindings lossless', () => {
  const result = generateFixture({
    nodes: [
      sourceNode('node_001', 'read.email', { email: { type: 'string' } }),
      transformNode('node_002', 'normalizeEmailA', {
        input: { email: { type: 'string' } },
        output: { email: { type: 'string' } }
      }),
      transformNode('node_003', 'normalizeEmailB', {
        input: { email: { type: 'string' } },
        output: { email: { type: 'string' } }
      }),
      sinkNode('node_004', 'send.webhook', { payload: { type: 'object' } })
    ],
    edges: [
      edge('node_001', 'node_002', 'email', 'email'),
      edge('node_001', 'node_003', 'email', 'email'),
      edge('node_002', 'node_004', 'email', 'payload'),
      edge('node_003', 'node_004', 'email', 'payload')
    ]
  });
  const observation = observations(result, 'node_004').find(obs => hasObservationLabel(result, obs, 'pii.email'));
  const flow = observationFlows(result, observation).find(item => item.label.label === 'pii.email');
  const state = result.security_profile.flow_states.find(item => item.state_id === flow.flow_state_id);
  const representativePaths = result.security_profile.provenance_store.representative_paths.filter(path => (
    (flow.representative_path_ids || []).includes(path.representative_path_id)
  ));

  assert.ok(flow);
  assert.ok(state);
  assert.equal(state.merged_path_count >= 2, true);
  assert.deepEqual(flow.representative_path_ids, state.representative_path_ids);
  assert.equal(representativePaths.length, flow.representative_path_ids.length);
  assert.ok(representativePaths.every(path => resolveFlowPath(result, path).node_path.length >= 3));
  assert.ok(state.provenance_event_id_count > 0);
  assert.equal(flow.provenance_event_id_count, state.provenance_event_id_count);
  assert.deepEqual(flow.provenance_event_ids, []);
  assert.equal(flow.merge_group_ids_truncated, false);
  assert.equal(flow.related_label_flow_ids_truncated, false);
});

function generateFixture({ nodes, edges }) {
  const result = generateFCGJson({
    skillData: { name: 'fixture-skill', version: '1.0.0' },
    graph: {
      getAllNodes() {
        return nodes;
      },
      getAllEdges() {
        return edges;
      }
    },
    sourceSink: { sources: [], sinks: [] },
    paths: [],
    allPaths: [],
    pathClusters: [],
    mode: 'full',
    inputSource: 'fixture.zip'
  });
  return rehydrateLabels(result);
}

// security_profile >= 5.0 emits labels by reference (label_id -> label_dictionary)
// instead of inline. These tests assert on label semantics (flow.label.category,
// state.label, ...), so resolve references back inline once here. This also acts
// as a round-trip lossless check: every label_id must resolve.
function rehydrateLabels(result) {
  const sp = result.security_profile || {};
  const dict = sp.label_dictionary || {};
  const resolve = (holder) => {
    if (holder && holder.label_id && !holder.label) {
      const full = dict[holder.label_id];
      if (!full) throw new Error(`dangling label_id in fixture: ${holder.label_id}`);
      holder.label = full;
    }
  };
  for (const flow of sp.label_flows || []) resolve(flow);
  for (const state of sp.flow_states || []) resolve(state);
  return result;
}

function profile(result, nodeId) {
  return result.security_profile.node_profiles.find(item => item.node_id === nodeId);
}

function observations(result, nodeId) {
  return result.security_profile.observations.filter(item => item.node_id === nodeId);
}

function instancesAt(result, nodeId) {
  return result.security_profile.label_flows.filter(item => item.current_node === nodeId);
}

function hasInstanceLabel(instance, label) {
  return instance?.label?.label === label;
}

function uniqueLabels(labels) {
  return Array.from(new Set((labels || []).map(label => label.label))).sort();
}

function userQueryNode(id) {
  return {
    id,
    name: 'user.query',
    type: 'builtin_call',
    category: 'Source',
    output: { query_text: { type: 'string' } }
  };
}

function sourceNode(id, name, output) {
  return {
    id,
    name,
    type: 'tool_call',
    category: 'Source',
    input: {},
    output
  };
}

function transformNode(id, name, { input = {}, output = {} }) {
  return {
    id,
    name,
    type: 'custom_func',
    category: 'Intermediate',
    input,
    output
  };
}

function docStepNode(id, name, operationType, instruction) {
  const action = operationType === 'write' ? 'write' : operationType;
  return {
    id,
    name,
    type: 'custom_func',
    category: operationType === 'write' ? 'Sink' : 'Intermediate',
    input: operationType === 'write' ? { content: { type: 'string' } } : { context: { type: 'string' } },
    output: operationType === 'write' ? { success: { type: 'boolean' } } : { safe_content: { type: 'string' } },
    semanticKind: 'doc_step',
    ownerDoc: 'SKILL.md',
    docRef: operationType === 'write' ? 'report.md' : 'semantic/report',
    docAction: action,
    docActions: [action],
    operationType,
    stepIndex: Number((name.match(/\.s(\d+)\./) || [])[1] || 1),
    instructionText: instruction,
    formal_semantics: {
      operation_type: operationType,
      actor: 'llm',
      inputs: operationType === 'write' ? [{ name: 'llm_context', type: 'context' }] : [{ name: 'context', type: 'string' }],
      outputs: operationType === 'write' ? [{ name: 'report.md', type: 'file' }] : [{ name: 'safe_content', type: 'string' }],
      targets: operationType === 'write'
        ? [{ type: 'file', value: 'report.md', raw: 'report.md' }]
        : [{ type: 'artifact', value: 'report', raw: 'report' }],
      conditions: [],
      effects: operationType === 'write' ? ['persist_state'] : ['summarize'],
      confidence: 0.9,
      evidence: {
        text: instruction,
        source_line: instruction,
        file: 'SKILL.md',
        line: 10,
        section: '',
        method: 'fixture'
      },
      action
    },
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true
  };
}

function produceArtifactNode(id, instruction, { producedObject = 'report', consumedObject = '' } = {}) {
  const evidence = {
    text: instruction,
    source_line: instruction,
    file: 'SKILL.md',
    line: 10,
    section: '',
    method: 'fixture',
    produced_object_key: producedObject.replace(/\s+/g, '_').toLowerCase(),
    produced_object_text: producedObject
  };
  if (consumedObject) {
    evidence.consumed_object_key = consumedObject.replace(/\s+/g, '_').toLowerCase();
    evidence.consumed_object_text = consumedObject;
  }
  return {
    id,
    name: `doc.step.skill.${id}.produce_artifact.${producedObject.replace(/\s+/g, '_').toLowerCase()}`,
    type: 'custom_func',
    category: 'Intermediate',
    input: { context: { type: 'string' } },
    output: { [producedObject.replace(/\s+/g, '_').toLowerCase()]: { type: 'string' } },
    semanticKind: 'doc_step',
    ownerDoc: 'SKILL.md',
    docRef: `semantic/${producedObject.replace(/\s+/g, '_').toLowerCase()}`,
    docAction: 'write',
    docActions: ['write'],
    operationType: 'produce_artifact',
    stepIndex: 1,
    instructionText: instruction,
    formal_semantics: {
      operation_type: 'produce_artifact',
      actor: 'llm',
      inputs: [{ name: 'llm_context', type: 'context' }],
      outputs: [{ name: producedObject, type: 'artifact' }],
      targets: [{ type: 'artifact', value: producedObject, raw: producedObject }],
      conditions: [],
      effects: ['persist_state'],
      confidence: 0.9,
      evidence,
      action: 'write'
    },
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true
  };
}

function sinkNode(id, name, input, critical = true) {
  return {
    id,
    name,
    type: 'tool_call',
    category: 'Sink',
    isCritical: critical,
    input,
    output: {}
  };
}

function edge(source, target, fromParam, toParam, validationMethod = 'fixture') {
  return {
    source,
    target,
    type: 'data_dependency',
    confidence: 0.9,
    validation_method: validationMethod,
    data_flow: {
      from_param: fromParam,
      to_param: toParam,
      data_type: 'string'
    }
  };
}






