const test = require('node:test');
const assert = require('node:assert/strict');

const {
  getLabelOntology,
  getOntologyStats,
  classifyOntologyText,
  getAllowedLlmLabelMap,
  getOntologyVersion
} = require('../src/security/label-ontology');
const { buildDataProfile, classifyTextLabels } = require('../src/security/data-labeler');

test('label ontology v3 loads as a versioned unique label set with valid optional metadata', () => {
  const ontology = getLabelOntology();
  const stats = getOntologyStats();
  const labels = ontology.labels.map(entry => entry.label);

  assert.equal(ontology.version, 'label-ontology-v3');
  assert.equal(new Set(labels).size, labels.length);
  assert.equal(stats.label_ontology_version, ontology.version);
  assert.equal(stats.label_ontology_label_count, labels.length);
  assert.equal(stats.label_ontology_llm_allowed_count, ontology.llmAllowedLabels.length);
  assert.ok(labels.includes('credentials.service_account_key'));
  assert.ok(labels.includes('special_category.genetic_data'));
  assert.ok(labels.includes('ai_context.system_prompt'));
  assert.ok(labels.includes('unknown_sensitive.data'));

  for (const entry of ontology.labels) {
    assert.equal(entry.label, `${entry.category}.${entry.subtype}`);
    assert.equal(typeof entry.fallback, 'boolean');
    assert.equal(typeof entry.priority, 'number');
    assert.ok(Array.isArray(entry.supersedes));
    assert.ok(Array.isArray(entry.source_refs));
  }
});

test('deterministic labeler recognizes v3 fine-grained ontology labels', () => {
  const profile = buildDataProfile({
    id: 'node_001',
    name: 'read.secureProfile',
    output: {
      service_account_key: { type: 'string' },
      database_url: { type: 'string' },
      genetic_data: { type: 'object' },
      lab_result: { type: 'object' },
      iris_scan: { type: 'string' },
      system_prompt: { type: 'string' },
      training_data: { type: 'array' },
      audit_log: { type: 'string' }
    }
  }, { node_id: 'node_001', node_name: 'read.secureProfile' });
  const labels = profile.labels.map(label => label.label);

  assert.ok(labels.includes('credentials.service_account_key'));
  assert.ok(labels.includes('credentials.database_connection_string'));
  assert.ok(labels.includes('special_category.genetic_data'));
  assert.ok(labels.includes('health.lab_result'));
  assert.ok(labels.includes('biometric.iris'));
  assert.ok(labels.includes('ai_context.system_prompt'));
  assert.ok(labels.includes('enterprise.training_data'));
  assert.ok(labels.includes('security_data.audit_log'));
  assert.equal(profile.sensitivity, 'critical');
  assert.ok(profile.labels.every(label => label.ontology_version === getOntologyVersion()));
  assert.ok(profile.labels.every(label => label.ontology_label_id));
});

test('fallback labels are suppressed when explicit labels match', () => {
  const explicit = classifyOntologyText('payload contains email address', { includeFallback: true });
  const fallbackOnly = classifyOntologyText('payload metadata result', { includeFallback: true });
  const defaultExplicit = classifyTextLabels('payload contains email address');

  assert.ok(explicit.some(match => match.label === 'pii.email'));
  assert.ok(!explicit.some(match => match.label === 'generic_data.data'));
  assert.ok(fallbackOnly.some(match => match.label === 'generic_data.data'));
  assert.ok(defaultExplicit.some(match => match.label === 'pii.email'));
  assert.ok(!defaultExplicit.some(match => match.label === 'generic_data.data'));
});

test('supersedes removes less-specific matches for overlapping secret labels', () => {
  const clientSecret = classifyOntologyText('oauth client_secret for app credentials');
  const sessionCookie = classifyOntologyText('session_cookie contains cookie auth token');

  assert.ok(clientSecret.some(match => match.label === 'credentials.oauth_client_secret'));
  assert.ok(!clientSecret.some(match => match.label === 'credentials.secret'));
  assert.ok(sessionCookie.some(match => match.label === 'credentials.session_cookie'));
  assert.ok(!sessionCookie.some(match => match.label === 'browser_data.cookie'));
});

test('negative patterns prevent obvious deterministic false positives', () => {
  const tokenCountMatches = classifyOntologyText('token_count token budget prompt token usage');
  const eventHandlerMatches = classifyOntologyText('event_handler event listener event loop');
  const statusCodeMatches = classifyOntologyText('status_code error_code http_code');
  const publicKeyMatches = classifyOntologyText('public_key used for verification');
  const sourceCodeMatches = classifyTextLabels('source_code implementation file');

  assert.ok(!tokenCountMatches.some(match => match.category === 'credentials'));
  assert.ok(!eventHandlerMatches.some(match => match.label === 'communication.calendar_event'));
  assert.ok(!statusCodeMatches.some(match => match.label === 'file_content.source_code'));
  assert.ok(!publicKeyMatches.some(match => match.label === 'credentials.private_key'));
  assert.ok(sourceCodeMatches.some(match => match.label === 'file_content.source_code'));
});

test('LLM allowed label map is derived from ontology only', () => {
  const allowed = getAllowedLlmLabelMap();
  const ontology = getLabelOntology();

  assert.equal(allowed.size, ontology.llmAllowedLabels.length);
  assert.ok(allowed.has('pii.email'));
  assert.ok(allowed.has('ai_context.system_prompt'));
  assert.ok(allowed.has('unknown_sensitive.data'));
  for (const [label, entry] of allowed.entries()) {
    assert.equal(label, entry.label);
    assert.equal(entry.llm_allowed, true);
  }
});

test('file path metadata is medium sensitivity rather than high-risk content', () => {
  const ontology = getLabelOntology();
  const pathLabel = ontology.labels.find(entry => entry.label === 'file_content.path');

  assert.ok(pathLabel);
  assert.equal(pathLabel.subtype, 'path');
  assert.equal(pathLabel.sensitivity, 'medium');
});
