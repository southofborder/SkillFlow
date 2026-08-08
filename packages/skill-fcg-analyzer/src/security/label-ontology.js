const ontology = require('./label-ontology.json');

const DEFAULT_EVIDENCE_CAPS = {
  L4: 0.95,
  L3: 0.85,
  L2: 0.7,
  L1: 0.55,
  L0: 0.3
};

const DEFAULT_CATEGORY_SENSITIVITY = {
  credentials: 'critical',
  financial: 'critical',
  health: 'critical',
  biometric: 'critical',
  pii: 'high',
  communication: 'high',
  file_content: 'high',
  browser_data: 'high',
  device_data: 'high',
  database_record: 'high',
  location: 'high',
  enterprise: 'high',
  unknown_sensitive: 'high',
  special_category: 'critical',
  personal_record: 'high',
  ai_context: 'high',
  security_data: 'high',
  network_data: 'medium',
  secret_material: 'critical',
  user_prompt: 'medium',
  aggregate_data: 'medium',
  pseudonymous_data: 'medium',
  generic_data: 'low'
};

let compiledOntology;

function getLabelOntology() {
  if (!compiledOntology) compiledOntology = compileOntology(ontology);
  return compiledOntology;
}

function compileOntology(raw) {
  if (!raw || typeof raw !== 'object') {
    throw new Error('Invalid label ontology: expected object');
  }
  if (!raw.version || typeof raw.version !== 'string') {
    throw new Error('Invalid label ontology: missing version');
  }
  if (!Array.isArray(raw.labels)) {
    throw new Error('Invalid label ontology: labels must be an array');
  }

  const byLabel = new Map();
  const labels = raw.labels.map((entry, index) => compileEntry(entry, index));
  for (const label of labels) {
    if (byLabel.has(label.label)) {
      throw new Error(`Invalid label ontology: duplicate label ${label.label}`);
    }
    byLabel.set(label.label, label);
  }

  return {
    version: raw.version,
    labels,
    byLabel,
    llmAllowedLabels: labels.filter(label => label.llm_allowed)
  };
}

function compileEntry(entry, index) {
  for (const field of ['label', 'category', 'subtype', 'sensitivity']) {
    if (!entry[field] || typeof entry[field] !== 'string') {
      throw new Error(`Invalid label ontology entry at ${index}: missing ${field}`);
    }
  }
  const expectedLabel = `${entry.category}.${entry.subtype}`;
  if (entry.label !== expectedLabel) {
    throw new Error(`Invalid label ontology entry ${entry.label}: expected ${expectedLabel}`);
  }

  return {
    label: entry.label,
    category: entry.category,
    subtype: entry.subtype,
    sensitivity: entry.sensitivity,
    patterns: compilePatterns(entry.patterns, entry.label, 'patterns'),
    negative_patterns: compilePatterns(entry.negative_patterns || [], entry.label, 'negative_patterns'),
    aliases: normalizeStringArray(entry.aliases),
    examples: normalizeStringArray(entry.examples),
    llm_allowed: Boolean(entry.llm_allowed),
    evidence_caps: { ...DEFAULT_EVIDENCE_CAPS, ...(entry.evidence_caps || {}) },
    fallback: Boolean(entry.fallback),
    priority: normalizeNumber(entry.priority, 0),
    supersedes: normalizeStringArray(entry.supersedes),
    source_refs: normalizeStringArray(entry.source_refs)
  };
}

function compilePatterns(patterns, label, field) {
  if (!Array.isArray(patterns)) {
    throw new Error(`Invalid label ontology entry ${label}: ${field} must be an array`);
  }
  return patterns.map((pattern, index) => {
    try {
      return new RegExp(pattern, 'i');
    } catch (error) {
      throw new Error(`Invalid regex for ${label}.${field}[${index}]: ${error.message}`);
    }
  });
}

function normalizeStringArray(value) {
  return Array.isArray(value) ? value.map(item => String(item || '')).filter(Boolean) : [];
}

function normalizeNumber(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function getOntologyVersion() {
  return getLabelOntology().version;
}

function getOntologyStats() {
  const current = getLabelOntology();
  return {
    label_ontology_version: current.version,
    label_ontology_label_count: current.labels.length,
    label_ontology_llm_allowed_count: current.llmAllowedLabels.length
  };
}

function getLabelDefinition(label) {
  return getLabelOntology().byLabel.get(label) || null;
}

function getLabelSensitivity(labelOrCategory) {
  const definition = getLabelDefinition(labelOrCategory);
  if (definition) return definition.sensitivity;
  return DEFAULT_CATEGORY_SENSITIVITY[labelOrCategory] || 'low';
}

function getEvidenceCap(labelOrCategory, evidenceLevel) {
  const definition = getLabelDefinition(labelOrCategory);
  const caps = definition?.evidence_caps || DEFAULT_EVIDENCE_CAPS;
  return Number(caps[evidenceLevel] ?? DEFAULT_EVIDENCE_CAPS[evidenceLevel] ?? DEFAULT_EVIDENCE_CAPS.L0);
}

function getAllowedLlmLabelMap() {
  const map = new Map();
  for (const entry of getLabelOntology().llmAllowedLabels) {
    map.set(entry.label, entry);
  }
  return map;
}

function listAllowedLlmLabels() {
  return getLabelOntology().llmAllowedLabels.map(entry => ({
    label: entry.label,
    category: entry.category,
    subtype: entry.subtype,
    sensitivity: entry.sensitivity,
    aliases: entry.aliases,
    examples: entry.examples,
    fallback: entry.fallback
  }));
}

function classifyOntologyText(text, options = {}) {
  const normalized = normalizeSecurityText(text);
  if (!normalized) return [];
  const includeFallback = options.includeFallback === true || options.includeGeneric === true;
  let matches = [];

  for (const entry of getLabelOntology().labels) {
    if (!includeFallback && entry.fallback) continue;
    if (!entry.patterns.some(pattern => pattern.test(normalized))) continue;
    if (entry.negative_patterns.some(pattern => pattern.test(normalized))) continue;
    matches.push(entry);
  }

  matches = applyMatchPostProcessing(matches, { includeFallback, includeSuppressedFallbacks: Boolean(options.includeSuppressedFallbacks) });
  return matches.map(entry => ({
    label: entry.label,
    category: entry.category,
    subtype: entry.subtype,
    sensitivity: entry.sensitivity,
    ontology_version: getOntologyVersion(),
    ontology_label_id: entry.label,
    fallback: entry.fallback,
    priority: entry.priority
  }));
}

function applyMatchPostProcessing(matches, { includeFallback, includeSuppressedFallbacks }) {
  let output = [...matches];
  if ((!includeFallback || !includeSuppressedFallbacks) && output.some(entry => !entry.fallback)) {
    output = output.filter(entry => !entry.fallback);
  }

  const superseded = new Set();
  for (const entry of output) {
    for (const label of entry.supersedes || []) {
      superseded.add(label);
    }
  }
  output = output.filter(entry => !superseded.has(entry.label));

  output.sort((a, b) => {
    const priorityDelta = Number(b.priority || 0) - Number(a.priority || 0);
    if (priorityDelta !== 0) return priorityDelta;
    const sensitivityDelta = sensitivityRank(b.sensitivity) - sensitivityRank(a.sensitivity);
    if (sensitivityDelta !== 0) return sensitivityDelta;
    return a.label.localeCompare(b.label);
  });
  return output;
}

function sensitivityRank(sensitivity) {
  const ranks = { low: 1, medium: 2, high: 3, critical: 4 };
  return ranks[sensitivity] || 1;
}

function normalizeSecurityText(text) {
  return String(text || '')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[._/-]+/g, ' ');
}

module.exports = {
  DEFAULT_EVIDENCE_CAPS,
  DEFAULT_CATEGORY_SENSITIVITY,
  getLabelOntology,
  getOntologyVersion,
  getOntologyStats,
  getLabelDefinition,
  getLabelSensitivity,
  getEvidenceCap,
  getAllowedLlmLabelMap,
  listAllowedLlmLabels,
  classifyOntologyText,
  normalizeSecurityText
};


