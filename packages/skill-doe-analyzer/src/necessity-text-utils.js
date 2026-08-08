const fs = require('fs');
const path = require('path');
const { round3 } = require('./utils');

const STOPWORDS = new Set([
  'a', 'an', 'the', 'to', 'into', 'in', 'on', 'for', 'from', 'of', 'and', 'or', 'then', 'with',
  'by', 'as', 'it', 'this', 'that', 'these', 'those', 'locally', 'local', 'file', 'data', 'value',
  'content', 'context', 'input', 'output', 'result', 'results', 'use', 'using', 'send', 'write', 'read'
]);

const LABEL_TERM_OVERRIDES = {
  'pii.email': ['email', 'email address', 'recipient', 'sender', 'mail'],
  'pii.phone': ['phone', 'phone number', 'mobile', 'telephone'],
  'pii.name': ['name', 'full name', 'first name', 'last name'],
  'pii.address': ['address', 'postal address', 'street address'],
  'location.city': ['city', 'location', 'weather location'],
  'location.postal_address': ['address', 'postal address', 'location'],
  'location.precise_geo': ['gps', 'geo', 'latitude', 'longitude', 'coordinates'],
  'credentials.api_key': ['api key', 'access key', 'provider key', 'credential', 'authorization'],
  'credentials.access_token': ['access token', 'token', 'bearer token', 'authorization'],
  'credentials.refresh_token': ['refresh token', 'token', 'credential'],
  'credentials.jwt': ['jwt', 'json web token', 'token'],
  'credentials.password': ['password', 'passwd', 'credential'],
  'credentials.secret': ['secret', 'credential'],
  'credentials.private_key': ['private key', 'secret key', 'key material'],
  'credentials.session_cookie': ['session cookie', 'cookie', 'session'],
  'communication.email_message': ['email content', 'email body', 'message body', 'mail content', 'email message', 'message'],
  'communication.chat_message': ['chat message', 'message', 'conversation'],
  'communication.contact_list': ['contacts', 'contact list', 'address book'],
  'file_content.document': ['document', 'file content', 'document content', 'report'],
  'file_content.source_code': ['source code', 'code', 'repository'],
  'file_content.path': ['path', 'file path', 'directory'],
  'browser_data.cookie': ['cookie', 'browser cookie', 'session cookie'],
  'browser_data.history': ['history', 'browser history'],
  'database_record.record': ['record', 'database record', 'row'],
  'database_record.query_result': ['query result', 'database result', 'records'],
  'financial.card': ['card', 'credit card', 'payment card'],
  'financial.payment': ['payment', 'billing', 'checkout'],
  'aggregate_data.summary': ['summary', 'digest', 'brief', 'abstract']
};

let ontologyCache = null;

function buildLabelTerms(label = {}) {
  const labelName = label.label || [label.category, label.subtype].filter(Boolean).join('.');
  const terms = new Set(LABEL_TERM_OVERRIDES[labelName] || []);
  addTermVariants(terms, labelName);
  addTermVariants(terms, label.category);
  addTermVariants(terms, label.subtype);
  addTermVariants(terms, label.field_name);
  for (const alias of ontologyAliases(labelName)) addTermVariants(terms, alias);
  return Array.from(terms).filter(Boolean);
}

function overlapScore(labelTerms = [], text = '') {
  const normalized = normalizeText(text);
  if (!normalized || !labelTerms.length) return 0;
  let best = 0;
  const tokens = new Set(normalized.split(/\s+/).filter(Boolean));
  for (const term of labelTerms) {
    const phrase = normalizeText(term);
    if (!phrase) continue;
    if (phrase.includes(' ') && normalized.includes(phrase)) best = Math.max(best, 1);
    const termTokens = phrase.split(/\s+/).filter(token => token && !STOPWORDS.has(token));
    if (!termTokens.length) continue;
    const hits = termTokens.filter(token => tokens.has(token) || normalized.includes(token)).length;
    best = Math.max(best, hits / termTokens.length);
  }
  return round3(Math.min(1, best));
}

function normalizeText(value) {
  return String(value || '')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .toLowerCase()
    .replace(/[_\-.\/]+/g, ' ')
    .replace(/[^a-z0-9\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function addTermVariants(set, value) {
  const normalized = normalizeText(value);
  if (!normalized) return;
  set.add(normalized);
  const withoutStops = normalized.split(/\s+/).filter(token => token && !STOPWORDS.has(token)).join(' ');
  if (withoutStops) set.add(withoutStops);
}

function ontologyAliases(labelName) {
  const ontology = loadOntology();
  const entry = ontology?.byLabel?.get(labelName);
  return entry?.aliases || [];
}

function loadOntology() {
  if (ontologyCache !== null) return ontologyCache;
  try {
    const ontologyPath = path.resolve(__dirname, '..', '..', 'skill-fcg-analyzer', 'src', 'security', 'label-ontology.json');
    const raw = JSON.parse(fs.readFileSync(ontologyPath, 'utf-8'));
    ontologyCache = {
      byLabel: new Map((raw.labels || []).map(entry => [entry.label, entry]))
    };
  } catch (_) {
    ontologyCache = { byLabel: new Map() };
  }
  return ontologyCache;
}

module.exports = {
  buildLabelTerms,
  overlapScore,
  normalizeText
};
