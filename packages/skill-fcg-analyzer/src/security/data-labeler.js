const crypto = require('crypto');
const {
  DEFAULT_EVIDENCE_CAPS,
  classifyOntologyText,
  getEvidenceCap,
  getLabelSensitivity,
  getOntologyVersion,
  getOntologyStats,
  getLabelDefinition,
  normalizeSecurityText
} = require('./label-ontology');

const EVIDENCE_CONFIDENCE = DEFAULT_EVIDENCE_CAPS;

function buildDataProfile(node = {}, sourceInfo = {}) {
  const labels = [];
  const originNode = sourceInfo.node_id || node.id || '';
  const originNodeName = node.canonical_name || node.name || sourceInfo.node_name || originNode;

  if (isUserQueryNode(node)) {
    labels.push(createLabel({
      category: 'user_prompt',
      subtype: 'query',
      fieldName: 'query_text',
      fieldPath: 'signature.output.query_text',
      originNode,
      originNodeName,
      evidenceLevel: 'L4',
      evidenceKind: 'builtin_user_query',
      evidenceText: node.canonical_name || node.name || 'user.query'
    }));
  }

  if (isProducedArtifactNode(node)) {
    addLabelsFromProducedArtifact(labels, node, originNode, originNodeName);
  }

  addLabelsFromFields(labels, collectSchemaFields(getSignatureOutput(node), 'signature.output'), originNode, originNodeName, 'output_field', 'L4');
  if (!isProducedArtifactNode(node)) {
    addLabelsFromFields(labels, collectSchemaFields(getSignatureInput(node), 'signature.input'), originNode, originNodeName, 'input_field', 'L4');
  }
  addLabelsFromTargets(labels, node.formal_semantics?.targets, originNode, originNodeName);
  if (!isProducedArtifactNode(node)) {
    addLabelsFromInstruction(labels, collectInstructionText(node), originNode, originNodeName);
  }
  addLabelsFromText(labels, [sourceInfo.data_type, sourceInfo.reason, node.canonical_name, node.name, node.description].filter(Boolean).join(' '), {
    originNode,
    originNodeName,
    fieldName: '',
    fieldPath: '',
    evidenceLevel: 'L1',
    evidenceKind: 'name_or_data_type'
  });

  const deduped = dedupeLabels(labels);
  const finalLabels = deduped.length > 0
    ? deduped
    : [createLabel({
        category: 'generic_data',
        subtype: 'data',
        fieldName: 'data',
        fieldPath: '',
        originNode,
        originNodeName,
        evidenceLevel: 'L0',
        evidenceKind: 'fallback',
        evidenceText: sourceInfo.data_type || node.canonical_name || node.name || 'data'
      })];

  const primaryCategory = choosePrimaryCategory(finalLabels);
  return {
    primary_category: primaryCategory,
    sensitivity: maxSensitivity(finalLabels),
    labels: finalLabels,
    alternatives: [],
    unknown_tail: finalLabels.some(label => label.evidence_level === 'L0' || label.label === 'generic_data.data')
  };
}

function isProducedArtifactNode(node = {}) {
  return String(node.formal_semantics?.operation_type || node.operationType || '').toLowerCase() === 'produce_artifact';
}

function addLabelsFromProducedArtifact(labels, node, originNode, originNodeName) {
  const evidence = node.formal_semantics?.evidence || {};
  const producedText = [
    evidence.produced_object_text,
    evidence.produced_object_key,
    ...(node.formal_semantics?.outputs || []).map(output => [output.name, output.type].filter(Boolean).join(' ')),
    ...(node.formal_semantics?.targets || []).map(target => [target.type, target.value, target.raw].filter(Boolean).join(' '))
  ].filter(Boolean).join(' ');

  addLabelsFromText(labels, producedText, {
    originNode,
    originNodeName,
    fieldName: String(evidence.produced_object_text || evidence.produced_object_key || 'artifact'),
    fieldPath: 'formal_semantics.produced_object',
    evidenceLevel: 'L3',
    evidenceKind: 'produced_artifact'
  });
}

function classifyTextLabels(text, options = {}) {
  return classifyOntologyText(text, options);
}

function createDerivedLabel({ fromLabel, category, subtype, fieldName, fieldPath, introducedAt, evidenceText, confidence }) {
  const originNode = fromLabel?.origin_node || '';
  const originNodeName = fromLabel?.origin_node_name || originNode;
  return createLabel({
    category,
    subtype,
    fieldName: fieldName || subtype,
    fieldPath: fieldPath || '',
    originNode,
    originNodeName,
    introducedAt,
    mode: 'derived',
    confidence: confidence || Math.min(0.8, Number(fromLabel?.confidence || 0.7)),
    evidenceLevel: 'L2',
    evidenceKind: 'semantic_derivation',
    evidenceText
  });
}

function createSyntheticLabel({ category, subtype, originNode, originNodeName, introducedAt, evidenceKind, evidenceText, confidence }) {
  return createLabel({
    category,
    subtype,
    fieldName: subtype || category,
    fieldPath: '',
    originNode,
    originNodeName,
    introducedAt,
    mode: 'derived',
    confidence: confidence || EVIDENCE_CONFIDENCE.L2,
    evidenceLevel: 'L2',
    evidenceKind: evidenceKind || 'synthetic_transfer',
    evidenceText: evidenceText || ''
  });
}

function maxSensitivity(labelsOrCategories) {
  const rank = { low: 1, medium: 2, high: 3, critical: 4 };
  let selected = 'low';
  for (const item of labelsOrCategories || []) {
    const sensitivity = typeof item === 'string'
      ? getLabelSensitivity(item)
      : getLabelSensitivity(item?.label || item?.category || '');
    if (rank[sensitivity] > rank[selected]) selected = sensitivity;
  }
  return selected;
}

function addLabelsFromFields(labels, fields, originNode, originNodeName, evidenceKind, evidenceLevel) {
  for (const field of fields) {
    const text = [field.name, field.path, field.type, field.description].filter(Boolean).join(' ');
    addLabelsFromText(labels, text, {
      originNode,
      originNodeName,
      fieldName: field.name,
      fieldPath: field.path,
      evidenceLevel,
      evidenceKind
    });
  }
}

function addLabelsFromTargets(labels, targets, originNode, originNodeName) {
  for (const target of Array.isArray(targets) ? targets : []) {
    const text = [target.type, target.value, target.raw].filter(Boolean).join(':');
    addLabelsFromText(labels, text, {
      originNode,
      originNodeName,
      fieldName: String(target.value || target.raw || target.type || ''),
      fieldPath: `formal_semantics.targets.${String(target.type || 'target')}`,
      evidenceLevel: 'L3',
      evidenceKind: 'formal_target'
    });
  }
}

function addLabelsFromInstruction(labels, instruction, originNode, originNodeName) {
  addLabelsFromText(labels, instruction, {
    originNode,
    originNodeName,
    fieldName: '',
    fieldPath: 'instruction',
    evidenceLevel: 'L2',
    evidenceKind: 'instruction_text'
  });
}

function addLabelsFromText(labels, text, context) {
  const matches = classifyTextLabels(text);
  for (const match of matches) {
    labels.push(createLabel({
      ...match,
      fieldName: context.fieldName,
      fieldPath: context.fieldPath,
      originNode: context.originNode,
      originNodeName: context.originNodeName,
      evidenceLevel: context.evidenceLevel,
      evidenceKind: context.evidenceKind,
      evidenceText: text
    }));
  }
}

function createLabel({
  category,
  subtype,
  fieldName = '',
  fieldPath = '',
  originNode = '',
  originNodeName = '',
  introducedAt = originNode,
  mode = 'definite',
  confidence,
  evidenceLevel = 'L0',
  evidenceKind = 'fallback',
  evidenceText = '',
  requiresReview = false,
  llmReview = null,
  uncertainty = '',
  reason = '',
  ontologyVersion = getOntologyVersion(),
  ontologyLabelId = ''
}) {
  const label = `${category}.${subtype || 'data'}`;
  const definition = getLabelDefinition(label);
  const value = {
    id: '',
    label,
    category,
    subtype: subtype || 'data',
    sensitivity: definition?.sensitivity || getLabelSensitivity(label),
    field_name: String(fieldName || subtype || category || ''),
    field_path: String(fieldPath || ''),
    origin_node: originNode,
    origin_node_name: originNodeName || originNode,
    introduced_at: introducedAt || originNode,
    mode,
    confidence: roundConfidence(confidence ?? getEvidenceCap(label, evidenceLevel)),
    evidence_level: evidenceLevel,
    evidence_kind: evidenceKind,
    evidence_text: String(evidenceText || '').slice(0, 300),
    ontology_version: ontologyVersion,
    ontology_label_id: ontologyLabelId || definition?.label || label
  };
  if (requiresReview) value.requires_review = true;
  if (llmReview && typeof llmReview === 'object') value.llm_review = llmReview;
  if (uncertainty) value.uncertainty = String(uncertainty || '').slice(0, 200);
  if (reason) value.reason = String(reason || '').slice(0, 240);
  value.id = `label_${shortHash([
    value.ontology_version,
    value.label,
    value.field_name,
    value.field_path,
    value.origin_node,
    value.introduced_at,
    value.evidence_kind
  ].join('|'))}`;
  return value;
}

function dedupeLabels(labels) {
  const byKey = new Map();
  for (const label of labels) {
    const key = [
      label.label,
      normalizeFieldName(label.field_name),
      label.field_path,
      label.origin_node,
      label.introduced_at
    ].join('|');
    const existing = byKey.get(key);
    if (!existing || evidenceRank(label.evidence_level) > evidenceRank(existing.evidence_level)) {
      byKey.set(key, label);
    }
  }
  return Array.from(byKey.values())
    .sort((a, b) => {
      const sensitivityDelta = sensitivityRank(b.label || b.category) - sensitivityRank(a.label || a.category);
      if (sensitivityDelta !== 0) return sensitivityDelta;
      const evidenceDelta = evidenceRank(b.evidence_level) - evidenceRank(a.evidence_level);
      if (evidenceDelta !== 0) return evidenceDelta;
      return a.label.localeCompare(b.label);
    })
    .slice(0, 24);
}

function choosePrimaryCategory(labels) {
  if (!Array.isArray(labels) || labels.length === 0) return 'generic_data';
  return [...labels].sort((a, b) => {
    const sensitivityDelta = sensitivityRank(b.label || b.category) - sensitivityRank(a.label || a.category);
    if (sensitivityDelta !== 0) return sensitivityDelta;
    const confidenceDelta = Number(b.confidence || 0) - Number(a.confidence || 0);
    if (confidenceDelta !== 0) return confidenceDelta;
    return a.label.localeCompare(b.label);
  })[0].category;
}

function collectSchemaFields(schema = {}, prefix = '') {
  const fields = [];
  for (const [name, spec] of Object.entries(schema || {})) {
    const path = prefix ? `${prefix}.${name}` : name;
    const field = {
      name,
      path,
      type: typeof spec === 'object' && spec ? spec.type || '' : String(spec || ''),
      description: typeof spec === 'object' && spec ? spec.description || '' : ''
    };
    fields.push(field);

    const properties = typeof spec === 'object' && spec ? spec.properties : null;
    if (properties && typeof properties === 'object') {
      fields.push(...collectSchemaFields(properties, path));
    }
  }
  return fields;
}

function collectInstructionText(node = {}) {
  const semantics = node.formal_semantics || {};
  const memberSteps = Array.isArray(node.member_steps)
    ? node.member_steps.map(step => step.instruction || step.text || '').join(' ')
    : '';
  return [
    node.instructionText,
    semantics.evidence?.text,
    Array.isArray(semantics.effects) ? semantics.effects.join(' ') : '',
    memberSteps
  ].filter(Boolean).join(' ');
}

function getSignatureInput(node = {}) {
  return node.signature?.input || node.input || {};
}

function getSignatureOutput(node = {}) {
  return node.signature?.output || node.output || {};
}

function isUserQueryNode(node = {}) {
  return String(node.name || '').toLowerCase() === 'user.query';
}

function normalizeFieldName(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '_');
}

function evidenceRank(level) {
  const ranks = { L0: 0, L1: 1, L2: 2, L3: 3, L4: 4 };
  return ranks[level] || 0;
}

function sensitivityRank(labelOrCategory) {
  const ranks = { low: 1, medium: 2, high: 3, critical: 4 };
  return ranks[getLabelSensitivity(labelOrCategory)] || 1;
}

function roundConfidence(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return EVIDENCE_CONFIDENCE.L0;
  return Math.max(0, Math.min(1, Math.round(n * 1000) / 1000));
}

function shortHash(value) {
  return crypto.createHash('sha1').update(String(value)).digest('hex').slice(0, 12);
}

module.exports = {
  buildDataProfile,
  classifyTextLabels,
  createLabel,
  createDerivedLabel,
  createSyntheticLabel,
  maxSensitivity,
  getOntologyVersion,
  getOntologyStats,
  normalizeSecurityText,
  shortHash
};

