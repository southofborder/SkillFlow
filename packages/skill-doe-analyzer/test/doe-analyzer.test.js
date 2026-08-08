const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { analyzeDoe, analyzeDoeAsync } = require('../src/doe-analyzer');

function runCase({ skillName, task, observation, flow, profile, extraNodes = [] }) {
  return analyzeDoe(fcg({
    skillName,
    task,
    observations: [observation],
    labelFlows: [flow],
    profiles: [profile],
    extraNodes
  })).assessments[0];
}

test('weather city flow to weather API is necessary, unrelated email is potential DOE', () => {
  const task = 'Use this skill to get weather for a city by calling the weather API with the city location.';
  const weatherProfile = profile('node_weather', 'call.weather.api', 'external_egress', 'Call the weather API with the city location', {
    inputs: [{ name: 'city', type: 'string' }],
    targets: [{ type: 'api', value: 'weather API city', raw: 'weather API city' }]
  });

  const city = runCase({
    skillName: 'weather lookup',
    task,
    observation: externalObs('obs_city', 'node_weather', ['lf_city'], 'first_party_service'),
    flow: flow('lf_city', 'location.city', { node_path: ['task_1', 'node_weather'], node_names: ['Weather task', 'call.weather.api'] }),
    profile: weatherProfile
  });
  const email = runCase({
    skillName: 'weather lookup',
    task,
    observation: externalObs('obs_email', 'node_weather', ['lf_email'], 'first_party_service'),
    flow: flow('lf_email', 'pii.email', { node_path: ['task_1', 'node_weather'], node_names: ['Weather task', 'call.weather.api'] }),
    profile: weatherProfile
  });

  assert.equal(city.boundary_crossed, true);
  assert.ok(city.necessity_score >= 0.65);
  assert.equal(city.potential_doe, false);
  assert.ok(city.doe_score < 0.3);
  assert.ok(email.necessity_score < 0.3);
  assert.equal(email.potential_doe, true);
  assert.ok(email.doe_score > 0.55);
});

test('task-relevant label on unnecessary analytics webhook path is potential DOE', () => {
  const task = 'Use this skill to get weather for a city by calling the weather API.';
  const analytics = profile('node_analytics', 'post.analytics.webhook', 'external_egress', 'Post payload to analytics webhook', {
    inputs: [{ name: 'payload', type: 'object' }],
    targets: [{ type: 'url', value: 'analytics webhook', raw: 'analytics webhook' }]
  });
  const assessment = runCase({
    skillName: 'weather lookup',
    task,
    observation: externalObs('obs_analytics', 'node_analytics', ['lf_city'], 'third_party_service'),
    flow: flow('lf_city', 'location.city', {
      node_path: ['task_1', 'node_analytics', 'node_weather'],
      node_names: ['Weather task', 'post.analytics.webhook', 'call.weather.api']
    }),
    profile: analytics
  });

  assert.equal(assessment.boundary_crossed, true);
  assert.ok(assessment.global_necessity.task_need <= 0.12);
  assert.equal(assessment.potential_doe, true);
  assert.ok(assessment.doe_score > 0.55);
});

test('generic webhook receiver does not prove credentials are needed', () => {
  const assessment = runCase({
    skillName: 'markdown formatter',
    task: 'Format user text into markdown.',
    observation: externalObs('obs_webhook', 'node_webhook', ['lf_key'], 'third_party_service'),
    flow: flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_webhook'], node_names: ['Format text', 'send.webhook'] }),
    profile: profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')
  });

  assert.equal(assessment.boundary_crossed, true);
  assert.ok(assessment.local_necessity.receiver_semantic_need < 0.2);
  assert.equal(assessment.potential_doe, true);
  assert.ok(assessment.doe_score > 0.8);
});

test('summarization model context is necessary but pre-redaction webhook is potential DOE', () => {
  const task = 'Summarize document content and save a short summary report.';
  const summary = runCase({
    skillName: 'document summarizer',
    task,
    observation: modelObs('obs_summary', 'node_summary', ['lf_doc']),
    flow: flow('lf_doc', 'file_content.document', { node_path: ['task_1', 'node_summary'], node_names: ['Summarize document content', 'llm.summary'] }),
    profile: profile('node_summary', 'summarize.document', 'transform', 'Summarize the document content', {
      inputs: [{ name: 'document_content', type: 'string' }],
      targets: [{ type: 'document', value: 'document content', raw: 'document content' }]
    }, ['summarization'])
  });
  const webhook = runCase({
    skillName: 'document summarizer',
    task,
    observation: externalObs('obs_webhook', 'node_webhook', ['lf_doc'], 'third_party_service'),
    flow: flow('lf_doc', 'file_content.document', {
      node_path: ['task_1', 'node_webhook', 'node_redact', 'node_summary'],
      node_names: ['Summarize document content', 'send.raw.webhook', 'redact', 'llm.summary'],
      filter_events: [{ event_id: 'filter_1', type: 'redaction', evidence: 'redact after webhook' }]
    }),
    profile: profile('node_webhook', 'send.raw.webhook', 'external_egress', 'Send raw document content to webhook')
  });

  assert.ok(summary.necessity_score >= 0.65);
  assert.equal(summary.potential_doe, false);
  assert.ok(summary.doe_score < 0.35);
  assert.equal(webhook.potential_doe, true);
  assert.ok(webhook.global_necessity.task_need <= 0.12);
});

test('persistent storage is low DOE only when the task flow declares the saved artifact', () => {
  const declared = runCase({
    skillName: 'summary saver',
    task: 'Summarize document content and save the summary report locally.',
    observation: storageObs('obs_save', 'node_save', ['lf_summary']),
    flow: flow('lf_summary', 'aggregate_data.summary', {
      node_path: ['task_1', 'node_summary', 'node_save'],
      node_names: ['Summarize document', 'create.summary', 'save.summary'],
      parent_label_flow_ids: ['lf_doc']
    }),
    profile: profile('node_save', 'save.summary.report', 'write', 'Save the summary report locally', {
      inputs: [{ name: 'summary', type: 'string' }],
      targets: [{ type: 'file', value: 'summary.md', raw: 'summary.md' }]
    })
  });
  const undeclared = runCase({
    skillName: 'markdown formatter',
    task: 'Format user text into markdown.',
    observation: storageObs('obs_write', 'node_write', ['lf_key']),
    flow: flow('lf_key', 'credentials.private_key', { node_path: ['task_1', 'node_write'], node_names: ['Format text', 'write.report.md'] }),
    profile: profile('node_write', 'write.report.md', 'write', 'Write report.md')
  });

  assert.equal(declared.boundary_crossed, true);
  assert.equal(declared.potential_doe, false);
  assert.ok(declared.doe_score < 0.35);
  assert.equal(undeclared.potential_doe, true);
  assert.ok(undeclared.doe_score > declared.doe_score);
});

test('destructive local-process observation is not DOE boundary by role alone', () => {
  const assessment = runCase({
    skillName: 'cleanup',
    task: 'Delete temporary build files.',
    observation: localDestructiveObs('obs_delete', 'node_delete', ['lf_path']),
    flow: flow('lf_path', 'file_content.path', { node_path: ['task_1', 'node_delete'], node_names: ['Cleanup task', 'delete.temp'] }),
    profile: profile('node_delete', 'delete.temp', 'destructive_operation', 'Delete temporary files')
  });

  assert.equal(assessment.boundary_crossed, false);
  assert.equal(assessment.potential_doe, false);
  assert.equal(assessment.doe_score, 0);
});

test('LLM judge emits component scores and lowers DOE for supported components', async () => {
  const result = await analyzeDoeAsync(fcg({
    skillName: 'auth lookup',
    task: 'Use this skill to send an API key to the first-party auth API.',
    observations: [externalObs('obs_key', 'node_auth', ['lf_key'], 'first_party_service')],
    labelFlows: [flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_auth'], node_names: ['Auth task', 'call.auth.api'] })],
    profiles: [profile('node_auth', 'call.auth.api', 'external_egress', 'Call the auth API with API key', {
      inputs: [{ name: 'api_key', type: 'string' }]
    })]
  }), {
    llmClient: scriptedLlmClient({
      lf_key: [
        componentScores(0.95, 0.9, 0.9, 0.9),
        componentScores(0.9, 0.9, 0.85, 0.9),
        componentScores(0.95, 0.95, 0.9, 0.9)
      ]
    })
  });

  const assessment = result.assessments[0];
  assert.equal(result.statistics.llm_judge_enabled, true);
  assert.ok(assessment.llm_necessity_score >= 0.85);
  assert.ok(assessment.component_scores.action_input_need >= 0.9);
  assert.equal(assessment.potential_doe, false);
  assert.equal(Object.hasOwn(assessment.llm_judge, 'component_scores'), true);
  assert.equal(Object.keys(assessment).some(key => key.includes('justification')), false);
  assert.equal(Object.keys(assessment.llm_judge).some(key => key.includes('justification')), false);
});

test('LLM judge rejects legacy-only necessity responses', async () => {
  await assert.rejects(
    () => analyzeDoeAsync(fcg({
      task: 'Send API key to the auth API.',
      observations: [externalObs('obs_key', 'node_auth', ['lf_key'], 'first_party_service')],
      labelFlows: [flow('lf_key', 'credentials.api_key')],
      profiles: [profile('node_auth', 'call.auth.api', 'external_egress', 'Call auth API with API key')]
    }), {
      llmClient: ({ evidencePacks }) => batchResponse(evidencePacks, () => ({
        ['justification' + '_score']: 0.9,
        supporting_evidence_ids: ['label'],
        reasoning_summary: 'legacy only'
      }))
    }),
    /component scores are required/
  );
});

test('LLM judge falls back to rule-only (not crash) when a unit keeps timing out', async () => {
  const llmClient = () => {
    const error = new Error('HTTP request timed out after 30000ms');
    error.code = 'LLM_TIMEOUT';
    throw error;
  };
  const result = await analyzeDoeAsync(fcg({
    skillName: 'auth lookup',
    task: 'Send an API key to the first-party auth API.',
    observations: [externalObs('obs_key', 'node_auth', ['lf_key'], 'first_party_service')],
    labelFlows: [flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_auth'], node_names: ['Auth task', 'call.auth.api'] })],
    profiles: [profile('node_auth', 'call.auth.api', 'external_egress', 'Call the auth API with API key')]
  }), {
    llmClient,
    llmEscalationPolicy: 'none'
  });

  // The skill still produces output rather than throwing.
  assert.equal(result.assessments.length, 1);
  const assessment = result.assessments[0];
  // The timed-out unit degrades to rule-only scoring and is flagged for review.
  assert.equal(assessment.requires_review, true);
  assert.equal(result.statistics.llm_fallback_count, 1);
  assert.ok(Array.isArray(result.statistics.llm_fallback_units));
  assert.equal(result.statistics.llm_fallback_units[0].reason, 'llm_timeout');
});

test('LLM judge still throws fast on a terminal (non-transient) error', async () => {
  const llmClient = () => {
    throw new Error('HTTP 401: invalid api key');
  };
  await assert.rejects(
    () => analyzeDoeAsync(fcg({
      skillName: 'auth lookup',
      task: 'Send an API key to the first-party auth API.',
      observations: [externalObs('obs_key', 'node_auth', ['lf_key'], 'first_party_service')],
      labelFlows: [flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_auth'], node_names: ['Auth task', 'call.auth.api'] })],
      profiles: [profile('node_auth', 'call.auth.api', 'external_egress', 'Call the auth API with API key')]
    }), { llmClient, llmEscalationPolicy: 'none' }),
    /HTTP 401/
  );
});

test('LLM judge records invalid refs, disagreement, and cache hits', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-doe-llm-cache-'));
  try {
    const cachePath = path.join(dir, 'judge-cache.jsonl');
    let calls = 0;
    const llmClient = ({ evidencePacks }) => {
      calls += 1;
      const score = calls === 1 ? 0.1 : calls === 2 ? 0.9 : 0.5;
      return batchResponse(evidencePacks, pack => ({
        components: makeComponentResponse(componentScores(score, score, score, score), {
          supporting: ['label', 'missing.evidence'],
          contradicting: ['sink_boundary']
        }),
        required_for_task: score > 0.7,
        necessity_level: score > 0.7 ? 'high' : 'low',
        reasoning_summary: `vote ${calls}`,
        supporting_evidence_ids: ['label', 'missing.evidence'],
        contradicting_evidence_ids: ['sink_boundary']
      }));
    };
    const input = fcg({
      skillName: 'webhook sender',
      task: 'Send a public summary to webhook.',
      observations: [externalObs('obs_webhook', 'node_webhook', ['lf_key'], 'third_party_service')],
      labelFlows: [flow('lf_key', 'credentials.api_key', {
        node_path: ['task_1', 'node_webhook'],
        node_names: ['Send summary', 'send.webhook'],
        filter_events: [{ event_id: 'filter_1', type: 'redaction', evidence: 'redact email' }]
      })],
      profiles: [profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')]
    });

    const first = await analyzeDoeAsync(input, {
      llmClient,
      llmCache: cachePath,
      llmVotes: 3,
      llmEscalationPolicy: 'none'
    });
    const second = await analyzeDoeAsync(input, {
      llmClient,
      llmCache: cachePath,
      llmVotes: 3,
      llmEscalationPolicy: 'none'
    });

    assert.equal(calls, 3);
    assert.equal(first.assessments[0].llm_necessity_score, 0.5);
    assert.equal(first.assessments[0].llm_judge.disagreement, 0.8);
    assert.equal(first.assessments[0].requires_review, true);
    assert.ok(first.warnings.some(item => item.kind === 'llm_judge.invalid_evidence_refs'));
    assert.equal(second.statistics.llm_cache_hit_count, 1);
    assert.equal(second.assessments[0].llm_judge.cache_hit, true);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('LLM judge aggregates endpoint token usage and computes prompt cache hit ratio', async () => {
  let calls = 0;
  // Client returns a usage-bearing envelope alongside assessments (mirrors the
  // OpenAI-compatible response). Two calls (first pass + escalation) so we can
  // confirm the accumulator sums across calls and computes the cache ratio.
  const llmClient = ({ evidencePacks }) => {
    calls += 1;
    const score = calls === 1 ? 0.1 : 0.9;
    const batch = batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(score, score, score, score)),
      required_for_task: score >= 0.7,
      necessity_level: score >= 0.7 ? 'high' : 'low',
      reasoning_summary: `call ${calls}`,
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
    // First call is a cold cache; second call re-bills the stable prefix at a hit.
    batch.usage = {
      prompt_tokens: 1000,
      completion_tokens: 50,
      total_tokens: 1050,
      prompt_tokens_details: { cached_tokens: calls === 1 ? 0 : 900 }
    };
    return batch;
  };

  const result = await analyzeDoeAsync(fcg({
    skillName: 'webhook sender',
    task: 'Send a public summary to webhook.',
    observations: [externalObs('obs_webhook', 'node_webhook', ['lf_key'], 'third_party_service')],
    labelFlows: [flow('lf_key', 'credentials.api_key', {
      node_path: ['task_1', 'node_webhook'],
      node_names: ['Send summary', 'send.webhook']
    })],
    profiles: [profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')]
  }), { llmClient });

  const usage = result.statistics.llm_token_usage;
  assert.ok(usage, 'llm_token_usage present');
  assert.equal(usage.calls, calls, 'one usage entry per model call');
  assert.equal(usage.prompt_tokens, 1000 * calls);
  assert.equal(usage.completion_tokens, 50 * calls);
  assert.equal(usage.cached_tokens, 900 * (calls - 1)); // only escalation calls hit
  // ratio = cached / prompt across the whole run, rounded to 3 dp
  const expectedRatio = Math.round((900 * (calls - 1)) / (1000 * calls) * 1000) / 1000;
  assert.equal(usage.prompt_cache_hit_ratio, expectedRatio);
});

test('LLM judge omits token usage when the client returns no usage envelope', async () => {
  const llmClient = ({ evidencePacks }) => batchResponse(evidencePacks, () => ({
    components: makeComponentResponse(componentScores(0.9, 0.9, 0.9, 0.9)),
    required_for_task: true,
    necessity_level: 'high',
    reasoning_summary: 'no usage',
    supporting_evidence_ids: ['label'],
    contradicting_evidence_ids: []
  }));
  const result = await analyzeDoeAsync(fcg({
    skillName: 'weather lookup',
    task: 'Get weather for a city.',
    observations: [externalObs('obs_city', 'node_api', ['lf_city'], 'first_party_service')],
    labelFlows: [flow('lf_city', 'location.city', { node_path: ['task_1', 'node_api'], node_names: ['task', 'weather.api'] })],
    profiles: [profile('node_api', 'weather.api', 'external_egress', 'Call weather API')]
  }), { llmClient, llmEscalationPolicy: 'none' });
  assert.equal(result.statistics.llm_token_usage, undefined, 'no usage stat without an envelope');
});

test('LLM judge defaults to single full pass and escalates risky or uncertain units', async () => {
  let calls = 0;
  const llmClient = ({ evidencePacks }) => {
    calls += 1;
    const score = calls === 1 ? 0.1 : 0.82;
    return batchResponse(evidencePacks, pack => ({
      components: makeComponentResponse(componentScores(score, score, score, score)),
      required_for_task: score >= 0.7,
      necessity_level: score >= 0.7 ? 'high' : 'low',
      reasoning_summary: `call ${calls}`,
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
  };
  const result = await analyzeDoeAsync(fcg({
    skillName: 'webhook sender',
    task: 'Send a public summary to webhook.',
      observations: [externalObs('obs_webhook', 'node_webhook', ['lf_key'], 'third_party_service')],
      labelFlows: [flow('lf_key', 'credentials.api_key', {
        node_path: ['task_1', 'node_webhook'],
        node_names: ['Send summary', 'send.webhook']
      })],
    profiles: [profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')]
  }), { llmClient });

  assert.equal(calls, 4);
  assert.equal(result.statistics.llm_first_pass_count, 1);
  assert.equal(result.statistics.llm_escalated_count, 1);
  assert.equal(result.statistics.llm_votes, 1);
  assert.equal(result.statistics.llm_escalation_votes, 3);
  assert.equal(result.assessments[0].llm_judge.vote_count, 3);
  assert.equal(result.assessments[0].llm_judge.escalated, true);
});

test('LLM judge sends task context once as shared memory and accepts task memory refs', async () => {
  let capturedPayload = null;
  const llmClient = ({ evidencePacks, payload }) => {
    capturedPayload = payload;
    const prompt = JSON.parse(payload.messages[1].content);
    const memoryRef = prompt.evidence_packs[0].task_memory_evidence_ids.find(id => id.startsWith('task.memory.'));
    return batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(0.9, 0.9, 0.9, 0.9), {
        supporting: ['label', memoryRef],
        contradicting: []
      }),
      required_for_task: true,
      necessity_level: 'high',
      reasoning_summary: 'task memory supports the route',
      supporting_evidence_ids: ['label', memoryRef],
      contradicting_evidence_ids: []
    }));
  };

  const result = await analyzeDoeAsync(fcg({
    skillName: 'auth lookup',
    task: 'Use this skill to send API keys to the first-party auth API.',
    observations: [
      externalObs('obs_key', 'node_auth', ['lf_key'], 'first_party_service'),
      externalObs('obs_key_2', 'node_auth', ['lf_key_2'], 'first_party_service')
    ],
    labelFlows: [
      flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_auth'], node_names: ['Auth task', 'call.auth.api'] }),
      flow('lf_key_2', 'credentials.api_key', { node_path: ['task_1', 'node_auth'], node_names: ['Auth task', 'call.auth.api'] })
    ],
    profiles: [profile('node_auth', 'call.auth.api', 'external_egress', 'Call the auth API with API key', {
      inputs: [{ name: 'api_key', type: 'string' }]
    })]
  }), {
    llmClient,
    llmBatchSize: 2,
    llmEscalationPolicy: 'none'
  });

  const prompt = JSON.parse(capturedPayload.messages[1].content);
  assert.equal(prompt.shared_context.task_memory.skill_name, 'auth lookup');
  assert.ok(prompt.shared_context.task_memory.evidence.some(item => item.evidence_id === 'task.memory.identity'));
  assert.equal(prompt.evidence_packs.length, 2);
  for (const pack of prompt.evidence_packs) {
    // Flow-centric packs never carry task context inline; it lives only in shared memory.
    assert.equal(Object.hasOwn(pack, 'sections'), false);
    assert.ok(Array.isArray(pack.flow), 'pack carries a flow array');
    assert.ok(pack.task_memory_evidence_ids.includes('task.memory.identity'));
  }
  assert.equal(result.statistics.llm_task_memory_node_count >= 1, true);
  assert.equal(result.assessments[0].llm_judge.evidence_refs.invalid.length, 0);
});

test('LLM gate (recall-first): high-sensitivity sent unconditionally, necessary medium flow skipped', async () => {
  let judgedUnits = 0;
  const llmClient = ({ evidencePacks }) => {
    judgedUnits += evidencePacks.length;
    return batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(0.2, 0.2, 0.2, 0.2)),
      required_for_task: false,
      necessity_level: 'low',
      reasoning_summary: 'sensitive high-risk unit judged',
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
  };

  const result = await analyzeDoeAsync(fcg({
    skillName: 'mixed outbound',
    task: 'Send weather city to weather API and never send secrets to webhooks.',
    observations: [
      externalObs('obs_city', 'node_api', ['lf_city'], 'first_party_service'),
      externalObs('obs_key', 'node_webhook', ['lf_key'], 'third_party_service')
    ],
    labelFlows: [
      flow('lf_city', 'location.city', {
        node_path: ['task_1', 'node_api'],
        node_names: ['Task', 'weather.api'],
        sensitivity: 'medium'
      }),
      flow('lf_key', 'credentials.api_key', {
        node_path: ['task_1', 'node_webhook'],
        node_names: ['Task', 'send.webhook'],
        sensitivity: 'critical'
      })
    ],
    profiles: [
      profile('node_api', 'weather.api', 'external_egress', 'Call weather API with city'),
      profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')
    ]
  }), {
    llmClient,
    llmEscalationPolicy: 'none'
  });

  const city = result.assessments.find(item => item.label_flow_id === 'lf_city');
  const key = result.assessments.find(item => item.label_flow_id === 'lf_key');
  // Recall-first gate: the medium-sensitivity city→weather-API flow is NOT sent —
  // not because it is medium (the old rule), but because the recall-first rules
  // score it necessary (city IS the weather API's declared input, task-declared)
  // so it is not potential_doe. The critical api_key→webhook flow is sent by the
  // high-sensitivity backstop.
  assert.equal(judgedUnits, 1);
  assert.equal(result.statistics.llm_eligible_count, 1);
  assert.equal(result.statistics.llm_skipped_count, 1);
  assert.equal(city.llm_judge.skipped, true);
  assert.match(city.llm_judge.skip_reason, /medium_sensitivity_not_potential_doe/);
  assert.equal(key.llm_judge.skipped, undefined);
  assert.equal(key.llm_necessity_score, 0.2);
});

test('LLM gate (recall-first): suspicious medium + all high-sensitivity sent, necessary medium skipped', async () => {
  let judgedUnits = 0;
  const llmClient = ({ evidencePacks }) => {
    judgedUnits += evidencePacks.length;
    return batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(0.25, 0.25, 0.25, 0.25)),
      required_for_task: false,
      necessity_level: 'low',
      reasoning_summary: 'high risk sensitive unit judged',
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
  };

  const result = await analyzeDoeAsync(fcg({
    skillName: 'mixed risk',
    task: 'Send an API key to auth, write report paths locally, and store summaries when needed.',
    observations: [
      externalObs('obs_path', 'node_webhook', ['lf_path'], 'third_party_service'),
      externalObs('obs_key', 'node_webhook', ['lf_key'], 'third_party_service'),
      storageObs('obs_store', 'node_store', ['lf_doc'])
    ],
    labelFlows: [
      flow('lf_path', 'file_content.path', {
        node_path: ['task_1', 'node_webhook'],
        node_names: ['Task', 'send.webhook']
      }),
      flow('lf_key', 'credentials.api_key', {
        node_path: ['task_1', 'node_webhook'],
        node_names: ['Task', 'send.webhook']
      }),
      flow('lf_doc', 'file_content.document', {
        node_path: ['task_1', 'node_store'],
        node_names: ['Task', 'store.document']
      })
    ],
    profiles: [
      profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook'),
      profile('node_store', 'store.document', 'write', 'Store document locally')
    ]
  }), {
    llmClient,
    llmEscalationPolicy: 'none'
  });

  const pathAssessment = result.assessments.find(item => item.label_flow_id === 'lf_path');
  const keyAssessment = result.assessments.find(item => item.label_flow_id === 'lf_key');
  const storageAssessment = result.assessments.find(item => item.label_flow_id === 'lf_doc');
  // Recall-first gate outcomes: all three cross a boundary and the recall-first
  // rules flag each potential_doe (path+doc are medium file_content routed to an
  // undeclared third-party / bare storage with weak task grounding; key is
  // critical). Medium+potential_doe and high-sensitivity are both eligible, so all
  // three are sent — the LLM makes the real call. This is the recall-first intent:
  // suspicious sensitive flows are handed to the LLM rather than rule-finalized.
  assert.equal(result.statistics.assessment_count, 3);
  assert.equal(result.statistics.llm_eligible_count, 3);
  assert.equal(result.statistics.llm_skipped_count, 0);
  assert.equal(result.statistics.llm_eligible_count + result.statistics.llm_skipped_count, result.statistics.assessment_count);
  assert.equal(judgedUnits, 3);
  assert.equal(pathAssessment.llm_judge.skipped, undefined);
  assert.equal(keyAssessment.llm_judge.skipped, undefined);
  assert.equal(storageAssessment.llm_judge.skipped, undefined);
});

test('sink-confidence dedup: same (observation,label,transform) sends one representative, members reuse it', async () => {
  let judgedFlowIds = [];
  const llmClient = ({ evidencePacks }) => {
    judgedFlowIds.push(...evidencePacks.map(p => p.label_flow_id));
    return batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(0.2, 0.2, 0.2, 0.2)),
      required_for_task: false,
      necessity_level: 'low',
      reasoning_summary: 'representative judged',
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
  };

  // One observation (one sink), one critical label, three label_flows:
  //  - lf_hi / lf_lo: same transform signature (none), different confidence -> dedup to 1
  //  - lf_redacted: different transform (redact_drop) -> sent separately
  const result = await analyzeDoeAsync(fcg({
    skillName: 'webhook sender',
    task: 'Send a short status to a webhook.',
    observations: [
      externalObs('obs_hook', 'node_webhook', ['lf_hi', 'lf_lo', 'lf_redacted'], 'third_party_service')
    ],
    labelFlows: [
      flow('lf_hi', 'credentials.api_key', { node_path: ['task_1', 'node_a', 'node_webhook'], node_names: ['Task', 'a', 'send.webhook'], sensitivity: 'critical', confidence: 0.95 }),
      flow('lf_lo', 'credentials.api_key', { node_path: ['task_1', 'node_b', 'node_webhook'], node_names: ['Task', 'b', 'send.webhook'], sensitivity: 'critical', confidence: 0.4 }),
      flow('lf_redacted', 'credentials.api_key', { node_path: ['task_1', 'node_c', 'node_webhook'], node_names: ['Task', 'c', 'send.webhook'], sensitivity: 'critical', confidence: 0.9,
        filter_events: [{ event_id: 'filter_redact_1', local_event_key: 'redact:node_c:credentials.api_key', type: 'redact_drop', node_id: 'node_c', from_label: { label: 'credentials.api_key' } }] })
    ],
    profiles: [
      profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')
    ],
    extraNodes: [
      { id: 'node_a', name: 'a', type: 'custom_func', formal_semantics: {} },
      { id: 'node_b', name: 'b', type: 'custom_func', formal_semantics: {} },
      { id: 'node_c', name: 'c', type: 'custom_func', formal_semantics: {} }
    ]
  }), { llmClient, llmEscalationPolicy: 'none' });

  // 3 eligible units, but only 2 representatives sent (the none-transform pair collapses to 1).
  assert.equal(result.statistics.llm_dedup_units_total, 3);
  assert.equal(result.statistics.llm_dedup_units_sent, 2);
  assert.equal(result.statistics.llm_dedup_saved, 1);
  // Exactly 2 packs reached the client; the redacted flow is one of them, plus one of hi/lo.
  assert.equal(judgedFlowIds.length, 2);
  assert.ok(judgedFlowIds.includes('lf_redacted'));
  assert.ok(judgedFlowIds.includes('lf_hi')); // hi confidence wins over lo as representative

  // All three assessments get an LLM judgement (no missing_result), necessity applied.
  const byId = Object.fromEntries(result.assessments.map(a => [a.label_flow_id, a]));
  for (const id of ['lf_hi', 'lf_lo', 'lf_redacted']) {
    assert.equal(byId[id].llm_judge.skipped, undefined, `${id} should be judged`);
    assert.equal(byId[id].llm_necessity_score, 0.2, `${id} reuses/has judgement`);
  }
  // The deduped member points at the representative; representative points at itself.
  assert.equal(byId['lf_lo'].llm_judge.dedup.role, 'member');
  assert.equal(byId['lf_hi'].llm_judge.dedup.role, 'representative');
  assert.equal(byId['lf_lo'].llm_judge.dedup.group_size, 2);
  // No missing-result warning for the deduped member.
  assert.equal(result.warnings.filter(w => w.kind === 'llm_judge.missing_result').length, 0);
});

// --- dedup key completeness: transform_seq (order + count) + origin_class ---
// Helper: run the standard critical-label / third-party-webhook gated setup with a
// custom set of label_flows + profiles, recording which flows reached the LLM.
function dedupCase({ labelFlows, profiles = [], extraNodes = [] }) {
  const judgedFlowIds = [];
  const llmClient = ({ evidencePacks }) => {
    judgedFlowIds.push(...evidencePacks.map(p => p.label_flow_id));
    return batchResponse(evidencePacks, () => ({
      components: makeComponentResponse(componentScores(0.2, 0.2, 0.2, 0.2)),
      required_for_task: false,
      necessity_level: 'low',
      reasoning_summary: 'representative judged',
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    }));
  };
  const promise = analyzeDoeAsync(fcg({
    skillName: 'webhook sender',
    task: 'Send a short status to a webhook.',
    observations: [
      externalObs('obs_hook', 'node_webhook', labelFlows.map(f => f.label_flow_id), 'third_party_service')
    ],
    labelFlows,
    profiles: [profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook'), ...profiles],
    extraNodes
  }), { llmClient, llmEscalationPolicy: 'none' });
  return promise.then(result => ({ result, judgedFlowIds }));
}

// A real transform event body on a given node (fixture entry point; helper derives
// the local_filter_event_ids reference + provenance body, see flow()).
function transformEvent(eventId, nodeId, type) {
  return { event_id: eventId, local_event_key: `${type}:${nodeId}`, type, node_id: nodeId, from_label: { label: 'credentials.api_key' } };
}

test('dedup: same transform set in different order lands in different groups (redact>summarize vs summarize>redact)', async () => {
  // Both flows carry {redact_drop, summarization}; only the ORDER along node_path differs.
  // Unordered set would merge them; ordered transform_seq must separate — redact-before-send
  // is a materially different necessity story than send-before-redact.
  const { result, judgedFlowIds } = await dedupCase({
    labelFlows: [
      flow('lf_rs', 'credentials.api_key', { node_path: ['task_1', 'node_x', 'node_y', 'node_webhook'], sensitivity: 'critical',
        filter_events: [transformEvent('ev_rs_1', 'node_x', 'redact_drop'), transformEvent('ev_rs_2', 'node_y', 'summarization')] }),
      flow('lf_sr', 'credentials.api_key', { node_path: ['task_1', 'node_x', 'node_y', 'node_webhook'], sensitivity: 'critical',
        filter_events: [transformEvent('ev_sr_1', 'node_x', 'summarization'), transformEvent('ev_sr_2', 'node_y', 'redact_drop')] })
    ],
    extraNodes: [
      { id: 'node_x', name: 'x', type: 'custom_func', formal_semantics: {} },
      { id: 'node_y', name: 'y', type: 'custom_func', formal_semantics: {} }
    ]
  });
  assert.equal(result.statistics.llm_dedup_units_total, 2);
  assert.equal(result.statistics.llm_dedup_units_sent, 2, 'different transform order must not merge');
  assert.equal(judgedFlowIds.length, 2);
});

test('dedup: same transform type at different counts lands in different groups (1x vs 2x redact)', async () => {
  const { result } = await dedupCase({
    labelFlows: [
      flow('lf_1x', 'credentials.api_key', { node_path: ['task_1', 'node_x', 'node_webhook'], sensitivity: 'critical',
        filter_events: [transformEvent('ev_1x', 'node_x', 'redact_drop')] }),
      flow('lf_2x', 'credentials.api_key', { node_path: ['task_1', 'node_x', 'node_y', 'node_webhook'], sensitivity: 'critical',
        filter_events: [transformEvent('ev_2x_1', 'node_x', 'redact_drop'), transformEvent('ev_2x_2', 'node_y', 'redact_drop')] })
    ],
    extraNodes: [
      { id: 'node_x', name: 'x', type: 'custom_func', formal_semantics: {} },
      { id: 'node_y', name: 'y', type: 'custom_func', formal_semantics: {} }
    ]
  });
  assert.equal(result.statistics.llm_dedup_units_total, 2);
  assert.equal(result.statistics.llm_dedup_units_sent, 2, 'different transform count must not merge');
});

test('dedup: same (obs,label,transform) but different origin trust class lands in different groups', async () => {
  // Both flows: no transform, same critical label, same sink. Only origin differs —
  // one enters from a model-provider surface, one from an external-network surface.
  const { result } = await dedupCase({
    labelFlows: [
      flow('lf_model', 'credentials.api_key', { origin_node: 'node_model', node_path: ['node_model', 'node_webhook'], sensitivity: 'critical' }),
      flow('lf_ext', 'credentials.api_key', { origin_node: 'node_ext', node_path: ['node_ext', 'node_webhook'], sensitivity: 'critical' })
    ],
    profiles: [
      profile('node_model', 'llm.call', 'transform', 'Model call'),        // model_provider / llm_context
      profile('node_ext', 'fetch.remote', 'external_egress', 'Fetch remote') // external_network / network
    ]
  });
  assert.equal(result.statistics.llm_dedup_units_total, 2);
  assert.equal(result.statistics.llm_dedup_units_sent, 2, 'different origin trust class must not merge');
});

test('dedup: different origin node ids with same trust class + surface merge (coarsening works, no over-split)', async () => {
  // Two distinct origin node IDs, both model_provider / llm_context -> same origin_class.
  // Coarsening must collapse them (else origin_node id would degrade dedup to near-identity).
  const { result } = await dedupCase({
    labelFlows: [
      flow('lf_m1', 'credentials.api_key', { origin_node: 'node_model_a', node_path: ['node_model_a', 'node_webhook'], sensitivity: 'critical', confidence: 0.9 }),
      flow('lf_m2', 'credentials.api_key', { origin_node: 'node_model_b', node_path: ['node_model_b', 'node_webhook'], sensitivity: 'critical', confidence: 0.4 })
    ],
    profiles: [
      profile('node_model_a', 'llm.call.a', 'transform', 'Model call A'),
      profile('node_model_b', 'llm.call.b', 'transform', 'Model call B')
    ]
  });
  assert.equal(result.statistics.llm_dedup_units_total, 2);
  assert.equal(result.statistics.llm_dedup_units_sent, 1, 'same trust class + surface must merge');
  assert.equal(result.statistics.llm_dedup_saved, 1);
});

test('dedup: missing origin profile falls back to unknown without crashing or self-splitting', async () => {
  // origin_node points at a node with no profile -> origin_class = 'unknown' for both.
  // Must not crash and must not force each flow into its own group.
  const { result } = await dedupCase({
    labelFlows: [
      flow('lf_u1', 'credentials.api_key', { origin_node: 'node_ghost_1', node_path: ['node_ghost_1', 'node_webhook'], sensitivity: 'critical', confidence: 0.9 }),
      flow('lf_u2', 'credentials.api_key', { origin_node: 'node_ghost_2', node_path: ['node_ghost_2', 'node_webhook'], sensitivity: 'critical', confidence: 0.4 })
    ]
  });
  assert.equal(result.statistics.llm_dedup_units_total, 2);
  assert.equal(result.statistics.llm_dedup_units_sent, 1, 'both fall back to unknown -> one group');
  // dedup traceability surfaces the coarsened origin class.
  const member = result.assessments.find(a => a.llm_judge?.dedup?.role === 'member');
  assert.equal(member.llm_judge.dedup.key.origin_class, 'unknown');
  assert.equal(member.llm_judge.dedup.key.transform_seq, 'none');
});

// --- Line B: FCG label_dictionary (referenced labels) compatibility ---
// Convert an inline-label fcg() result into the new >=5.0 shape: hoist each
// distinct label into security_profile.label_dictionary and replace the flow's
// inline label with a label_id reference.
function toDictionaryForm(fcgJson) {
  const clone = JSON.parse(JSON.stringify(fcgJson));
  const sec = clone.security_profile;
  sec.version = '5.1';
  const dict = {};
  let counter = 0;
  for (const flow of sec.label_flows || []) {
    const lab = flow.label || {};
    const id = lab.id || `lbl_${++counter}`;
    dict[id] = { id, ...lab };
    delete flow.label;
    flow.label_id = id;
  }
  sec.label_dictionary = dict;
  return clone;
}

test('Line B: dictionary-referenced labels produce identical verdicts to inline labels', () => {
  const base = fcg({
    skillName: 'mixed outbound',
    task: 'Send weather city to weather API and store a summary.',
    observations: [
      externalObs('obs_city', 'node_api', ['lf_city'], 'first_party_service'),
      externalObs('obs_key', 'node_webhook', ['lf_key'], 'third_party_service')
    ],
    labelFlows: [
      flow('lf_city', 'location.city', { node_path: ['task_1', 'node_api'], node_names: ['Task', 'weather.api'], sensitivity: 'medium' }),
      flow('lf_key', 'credentials.api_key', { node_path: ['task_1', 'node_webhook'], node_names: ['Task', 'send.webhook'], sensitivity: 'critical' })
    ],
    profiles: [
      profile('node_api', 'weather.api', 'external_egress', 'Call weather API with city'),
      profile('node_webhook', 'send.webhook', 'external_egress', 'Post payload to webhook')
    ]
  });
  const dictForm = toDictionaryForm(base);

  const inlineResult = analyzeDoe(base, {});
  const dictResult = analyzeDoe(dictForm, {});

  // Strip nondeterministic/id-only fields and compare the substantive verdicts.
  const project = (r) => r.assessments.map(a => ({
    observation_id: a.observation_id,
    label_flow_id: a.label_flow_id,
    label: a.label,
    label_category: a.label_category,
    label_subtype: a.label_subtype,
    exposure_score: a.exposure_score,
    necessity_score: a.necessity_score,
    component_scores: a.component_scores,
    doe_score: a.doe_score,
    boundary_crossed: a.boundary_crossed,
    potential_doe: a.potential_doe
  })).sort((x, y) => x.label_flow_id.localeCompare(y.label_flow_id));

  assert.deepEqual(project(dictResult), project(inlineResult));
  // No miss warnings when every reference resolves.
  assert.equal(dictResult.warnings.filter(w => w.kind === 'label_dictionary.miss').length, 0);
});

test('Line B: a dangling label_id is surfaced as a warning, never silently dropped', () => {
  const base = fcg({
    skillName: 'dangling ref',
    task: 'Send city to weather API.',
    observations: [externalObs('obs_city', 'node_api', ['lf_city'], 'first_party_service')],
    labelFlows: [flow('lf_city', 'location.city', { node_path: ['task_1', 'node_api'], sensitivity: 'medium' })],
    profiles: [profile('node_api', 'weather.api', 'external_egress', 'Call weather API with city')]
  });
  const broken = toDictionaryForm(base);
  // Remove the dictionary entry the flow points at -> dangling reference.
  broken.security_profile.label_dictionary = {};

  const result = analyzeDoe(broken, {});
  const misses = result.warnings.filter(w => w.kind === 'label_dictionary.miss');
  assert.equal(misses.length, 1);
  assert.equal(misses[0].label_flow_id, 'lf_city');
  // Still produces an assessment (degraded to empty label) rather than crashing.
  assert.equal(result.assessments.length, 1);
});

function fcg({ skillName = 'test skill', task = '', observations = [], labelFlows = [], profiles = [], extraNodes = [] }) {
  const taskNode = task ? {
    id: 'task_1',
    name: 'task.declared',
    type: 'custom_func',
    description: task,
    location: { file: 'SKILL.md', line: 1, section: 'Description' },
    semanticKind: 'doc_step',
    instructionText: task,
    formal_semantics: {
      operation_type: 'trigger',
      inputs: [],
      outputs: [],
      targets: [{ type: 'instruction', value: task, raw: task }],
      effects: ['branch'],
      evidence: { text: task, source_line: task }
    },
    signature: { input: {}, output: {} }
  } : null;
  const profileNodes = profiles.map(profile => ({
    id: profile.node_id,
    name: profile.node_name,
    type: 'custom_func',
    description: profile.formal_semantics?.evidence?.text || profile.node_name,
    location: { file: 'SKILL.md', line: 2, section: 'Steps' },
    instructionText: profile.formal_semantics?.evidence?.text || '',
    formal_semantics: profile.formal_semantics || {},
    signature: {
      input: Object.fromEntries((profile.formal_semantics?.inputs || []).map(item => [item.name || item.value || 'input', item])),
      output: Object.fromEntries((profile.formal_semantics?.outputs || []).map(item => [item.name || item.value || 'output', item]))
    }
  }));
  // 汇总各 flow 的 filter 事件本体到 provenance_graph(镜像序列化后的真实存储:
  // flow 仅存 local_filter_event_ids,本体集中存于此),并清理临时字段。
  const filtering = [];
  for (const lf of labelFlows) {
    for (const ev of lf._filter_event_bodies || []) filtering.push(ev);
    delete lf._filter_event_bodies;
  }
  return {
    meta: { skill_name: skillName, skill_version: '0.1.0' },
    nodes: [taskNode, ...profileNodes, ...extraNodes].filter(Boolean),
    edges: [],
    security_profile: {
      version: '4.9',
      node_profiles: profiles,
      label_flows: labelFlows,
      observations,
      provenance_graph: { events: { filtering } }
    }
  };
}

function flow(id, labelName, options = {}) {
  const [category, subtype] = labelName.split('.');
  const filterEvents = options.filter_events || [];
  return {
    label_flow_id: id,
    current_node: options.current_node || (options.node_path || [])[((options.node_path || []).length - 1)] || 'node_current',
    current_node_name: options.current_node_name || '',
    origin_node: options.origin_node || '',
    node_path: options.node_path || ['task_1', 'node_current'],
    node_names: options.node_names || ['task', 'current'],
    edge_path: options.edge_path || [],
    parent_label_flow_ids: options.parent_label_flow_ids || [],
    // 序列化后真实形态:flow 只保留 local_filter_event_ids 引用,事件本体在
    // provenance_graph.events.filtering(见 fcg())。inline filter_events 仅为
    // 测试便利入口,helper 据此派生引用 id 并置空本体。
    filter_events: [],
    local_filter_event_ids: filterEvents.map(ev => ev.event_id).filter(Boolean),
    _filter_event_bodies: filterEvents,
    route_history: options.route_history || [],
    flow_mode: options.flow_mode || 'may_flow',
    storage_key: options.storage_key || '',
    confidence: options.confidence || 0.9,
    label: {
      label: labelName,
      category,
      subtype,
      sensitivity: options.sensitivity || undefined,
      confidence: options.labelConfidence || 0.9,
      ...options.labelExtras
    }
  };
}

function profile(nodeId, nodeName, operationType, instruction, semantics = {}, operationTags = []) {
  const boundary = boundaryForOperation(operationType);
  return {
    node_id: nodeId,
    node_name: nodeName,
    node_roles: roleForOperation(operationType),
    security_tags: tagsForOperation(operationType, nodeName),
    operation_tags: operationTags,
    data_surface: boundary.data_surface,
    receiver_scope: boundary.receiver_scope,
    retention_scope: boundary.retention_scope,
    trust_boundary: boundary.trust_boundary,
    formal_semantics: {
      operation_type: operationType,
      inputs: semantics.inputs || [],
      outputs: semantics.outputs || [],
      targets: semantics.targets || [],
      effects: operationTags,
      evidence: { text: instruction, source_line: instruction }
    }
  };
}

function externalObs(id, nodeId, labelFlowIds, receiverScope) {
  return {
    observation_id: id,
    node_id: nodeId,
    node_name: nodeId,
    node_roles: ['external_egress'],
    security_tags: ['network_egress', receiverScope === 'third_party_service' ? 'third_party_service' : 'api_call'],
    boundary: {
      data_surface: 'network',
      receiver_scope: receiverScope,
      retention_scope: 'external',
      trust_boundary: 'external_network'
    },
    operation_type: 'external_egress',
    label_flow_ids: labelFlowIds
  };
}

function modelObs(id, nodeId, labelFlowIds) {
  return {
    observation_id: id,
    node_id: nodeId,
    node_name: nodeId,
    node_roles: ['model_inference'],
    security_tags: ['model_context'],
    boundary: {
      data_surface: 'llm_context',
      receiver_scope: 'model_provider',
      retention_scope: 'transient',
      trust_boundary: 'model_provider'
    },
    operation_type: 'transform',
    label_flow_ids: labelFlowIds
  };
}

function storageObs(id, nodeId, labelFlowIds) {
  return {
    observation_id: id,
    node_id: nodeId,
    node_name: nodeId,
    node_roles: ['local_persistence'],
    security_tags: ['file_write'],
    boundary: {
      data_surface: 'local_file',
      receiver_scope: 'local_runtime',
      retention_scope: 'persistent',
      trust_boundary: 'persistent_storage'
    },
    operation_type: 'write',
    label_flow_ids: labelFlowIds
  };
}

function localDestructiveObs(id, nodeId, labelFlowIds) {
  return {
    observation_id: id,
    node_id: nodeId,
    node_name: nodeId,
    node_roles: ['destructive_operation'],
    security_tags: [],
    boundary: {
      data_surface: 'runtime_env',
      receiver_scope: 'local_runtime',
      retention_scope: 'transient',
      trust_boundary: 'local_process'
    },
    operation_type: 'destructive_operation',
    label_flow_ids: labelFlowIds
  };
}

function boundaryForOperation(operationType) {
  if (operationType === 'write') {
    return { data_surface: 'local_file', receiver_scope: 'local_runtime', retention_scope: 'persistent', trust_boundary: 'persistent_storage' };
  }
  if (operationType === 'transform') {
    return { data_surface: 'llm_context', receiver_scope: 'model_provider', retention_scope: 'transient', trust_boundary: 'model_provider' };
  }
  if (operationType === 'destructive_operation') {
    return { data_surface: 'runtime_env', receiver_scope: 'local_runtime', retention_scope: 'transient', trust_boundary: 'local_process' };
  }
  return { data_surface: 'network', receiver_scope: 'third_party_service', retention_scope: 'external', trust_boundary: 'external_network' };
}

function roleForOperation(operationType) {
  if (operationType === 'write') return ['local_persistence'];
  if (operationType === 'transform') return ['model_inference', 'transform'];
  if (operationType === 'destructive_operation') return ['destructive_operation'];
  return ['external_egress'];
}

function tagsForOperation(operationType, nodeName) {
  if (operationType === 'write') return ['file_write'];
  if (operationType === 'transform') return ['model_context'];
  if (operationType === 'destructive_operation') return [];
  return ['network_egress', /webhook|analytics/i.test(nodeName) ? 'third_party_service' : 'api_call'];
}

function componentScores(action, receiver, flowPath, boundaryNode) {
  // Global necessity is now a single component task_need = min(flow, boundary).
  // Accepts the legacy 4-arg form (flowPath, boundaryNode) and folds it down,
  // or a 3-arg form where flowPath already is the task_need value.
  const taskNeed = boundaryNode === undefined ? flowPath : Math.min(flowPath, boundaryNode);
  return {
    action_input_need: action,
    receiver_semantic_need: receiver,
    task_need: taskNeed
  };
}

function makeComponentResponse(scores, options = {}) {
  return Object.fromEntries(Object.entries(scores).map(([key, score]) => [key, {
    score,
    status: score >= 0.7 ? 'supporting' : 'insufficient',
    supporting_evidence_ids: options.supporting || ['label'],
    contradicting_evidence_ids: options.contradicting || [],
    reasoning_summary: `${key} score ${score}`
  }]));
}

function scriptedLlmClient(scoresByFlowId) {
  const voteIndexByFlowId = new Map();
  return ({ evidencePacks }) => batchResponse(evidencePacks, pack => {
    const flowId = pack.label_flow_id;
    const scores = scoresByFlowId[flowId] || [componentScores(0.1, 0.1, 0.1, 0.1)];
    const index = voteIndexByFlowId.get(flowId) || 0;
    voteIndexByFlowId.set(flowId, index + 1);
    const component = scores[Math.min(index, scores.length - 1)];
    return {
      components: makeComponentResponse(component),
      required_for_task: Math.min(...Object.values(component)) >= 0.7,
      necessity_level: Math.min(...Object.values(component)) >= 0.7 ? 'high' : 'low',
      reasoning_summary: 'mock layered necessity',
      supporting_evidence_ids: ['label'],
      contradicting_evidence_ids: []
    };
  });
}

function batchResponse(evidencePacks, build) {
  return {
    assessments: evidencePacks.map(pack => ({
      unit_id: pack.unit_id,
      ...build(pack)
    }))
  };
}
