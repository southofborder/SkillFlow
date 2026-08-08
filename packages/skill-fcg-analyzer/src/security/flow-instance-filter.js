const {
  classifyTextLabels,
  createDerivedLabel,
  createSyntheticLabel,
  shortHash
} = require('./data-labeler');

function applyLabelFlowFilter({ labelFlow = {}, currentProfile = {}, edge = {} }) {
  const profileTags = new Set(currentProfile.operation_tags || []);
  const inputLabel = cloneLabel(labelFlow.label);
  const events = [];
  const nextTriggerContext = [...(labelFlow.trigger_context || [])];
  let sourceIntroAppliedNodes = [...(labelFlow.source_intro_applied_nodes || [])];
  let flowMode = labelFlow.flow_mode || 'may_flow';
  let confidenceMultiplier = 1;

  if (!inputLabel) {
    return buildResult({ branches: [], events, sourceIntroAppliedNodes, terminated: true, terminationReason: 'filtered_out' });
  }

  if (isProducedArtifactProfile(currentProfile)) {
    const key = `artifact:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'artifact_production',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      from_label: compactLabel(inputLabel),
      produced_object_key: currentProfile.produced_object_key || '',
      produced_object_text: currentProfile.produced_object_text || '',
      evidence: filterEvidence(currentProfile, edge)
    });
    return buildResult({
      branches: [{
        label: inputLabel,
        flow_mode: flowMode === 'source_introduction' ? 'may_flow' : flowMode,
        confidence_multiplier: 0.95,
        trigger_context: nextTriggerContext,
        source_intro_applied_nodes: sourceIntroAppliedNodes,
        parent_label_flow_ids: [labelFlow.label_flow_id],
        filter_event_keys: [key]
      }],
      events,
      sourceIntroAppliedNodes
    });
  }

  if (shouldIntroduceSource(currentProfile, labelFlow)) {
    const introduced = compactLabels(currentProfile.data_profile?.labels || []);
    mergeTriggerContextInto(nextTriggerContext, labelToTriggerContext(inputLabel, 'upstream_context_triggers_source_introduction'));
    if (!sourceIntroAppliedNodes.includes(currentProfile.node_id)) {
      sourceIntroAppliedNodes.push(currentProfile.node_id);
    }
    const branches = introduced.map(label => {
      const key = `source:${currentProfile.node_id}:${label.label}:${label.origin_node}:${label.introduced_at}`;
      events.push({
        local_event_key: key,
        type: 'source_introduction',
        node_id: currentProfile.node_id,
        node_name: currentProfile.node_name,
        introduced_label: compactLabel(label),
        introduced_labels: [compactLabel(label)],
        context_label: compactLabel(inputLabel),
        evidence: 'data_introduction node emits its own data label'
      });
      return {
        label,
        flow_mode: 'source_introduction',
        confidence_multiplier: 1,
        trigger_context: nextTriggerContext,
        source_intro_applied_nodes: sourceIntroAppliedNodes,
        parent_label_flow_ids: [labelFlow.label_flow_id],
        filter_event_keys: [key]
      };
    });
    return buildResult({ branches, events, sourceIntroAppliedNodes });
  }

  if (profileTags.has('redaction') && shouldRedactLabel(inputLabel, currentProfile)) {
    const key = `redact:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'redact_drop',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      dropped_label: compactLabel(inputLabel),
      dropped_labels: [compactLabel(inputLabel)],
      evidence: filterEvidence(currentProfile, edge)
    });
    return buildResult({ branches: [], events, sourceIntroAppliedNodes, terminated: true, terminationReason: 'filtered_out' });
  }


  if (profileTags.has('aggregation')) {
    const aggregate = createSummaryLabel(inputLabel, currentProfile, edge, 'aggregate');
    const key = `aggregate:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'aggregate',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      from_label: compactLabel(inputLabel),
      introduced_label: compactLabel(aggregate),
      introduced_labels: [compactLabel(aggregate)],
      dropped_label: compactLabel(inputLabel),
      dropped_labels: [compactLabel(inputLabel)],
      evidence: filterEvidence(currentProfile, edge)
    });
    return buildResult({
      branches: [{
        label: aggregate,
        flow_mode: 'derived_flow',
        confidence_multiplier: 1,
        trigger_context: nextTriggerContext,
        source_intro_applied_nodes: sourceIntroAppliedNodes,
        parent_label_flow_ids: [labelFlow.label_flow_id],
        filter_event_keys: [key]
      }],
      events,
      sourceIntroAppliedNodes
    });
  }

  if (profileTags.has('summarization') && !shouldPreserveRawAfterSummary(currentProfile, edge)) {
    const summary = createSummaryLabel(inputLabel, currentProfile, edge, 'summarization');
    const key = `summary:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'summarization',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      from_label: compactLabel(inputLabel),
      introduced_label: compactLabel(summary),
      introduced_labels: [compactLabel(summary)],
      dropped_label: compactLabel(inputLabel),
      dropped_labels: [compactLabel(inputLabel)],
      evidence: filterEvidence(currentProfile, edge)
    });
    return buildResult({
      branches: [{
        label: summary,
        flow_mode: 'derived_flow',
        confidence_multiplier: 1,
        trigger_context: nextTriggerContext,
        source_intro_applied_nodes: sourceIntroAppliedNodes,
        parent_label_flow_ids: [labelFlow.label_flow_id],
        filter_event_keys: [key]
      }],
      events,
      sourceIntroAppliedNodes
    });
  }

  if (profileTags.has('pseudonymization')) {
    const pseudo = createSyntheticLabel({
      category: 'pseudonymous_data',
      subtype: 'protected',
      originNode: inputLabel.origin_node || currentProfile.node_id,
      originNodeName: inputLabel.origin_node_name || currentProfile.node_name || currentProfile.node_id,
      introducedAt: currentProfile.node_id,
      evidenceKind: 'pseudonymize',
      evidenceText: filterEvidence(currentProfile, edge),
      confidence: Math.min(0.8, Number(inputLabel.confidence || 0.7))
    });
    const key = `pseudonymize:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'pseudonymize',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      from_label: compactLabel(inputLabel),
      introduced_label: compactLabel(pseudo),
      introduced_labels: [compactLabel(pseudo)],
      evidence: filterEvidence(currentProfile, edge)
    });
    return buildResult({
      branches: [{
        label: pseudo,
        flow_mode: 'derived_flow',
        confidence_multiplier: 1,
        trigger_context: nextTriggerContext,
        source_intro_applied_nodes: sourceIntroAppliedNodes,
        parent_label_flow_ids: [labelFlow.label_flow_id],
        filter_event_keys: [key]
      }],
      events,
      sourceIntroAppliedNodes
    });
  }

  if (profileTags.has('semantic_extraction')) {
    const derived = deriveSemanticLabels(inputLabel, currentProfile, edge);
    if (derived.length > 0) {
      const branches = derived.map(label => {
        const key = `derive:${currentProfile.node_id}:${inputLabel.label}:${label.label}`;
        events.push({
          local_event_key: key,
          type: 'semantic_derivation',
          node_id: currentProfile.node_id,
          node_name: currentProfile.node_name,
          from_label: compactLabel(inputLabel),
          introduced_label: compactLabel(label),
          introduced_labels: [compactLabel(label)],
          evidence: filterEvidence(currentProfile, edge)
        });
        return {
          label,
          flow_mode: 'derived_flow',
          confidence_multiplier: 1,
          trigger_context: mergeTriggerContexts(nextTriggerContext, labelToTriggerContext(inputLabel, 'semantic_extraction_source_context')),
          source_intro_applied_nodes: sourceIntroAppliedNodes,
          parent_label_flow_ids: [labelFlow.label_flow_id],
          filter_event_keys: [key]
        };
      });
      return buildResult({ branches, events, sourceIntroAppliedNodes });
    }
  }

  if (profileTags.has('field_slice')) {
    const result = sliceLabel(inputLabel, currentProfile, edge);
    if (result.applied && !result.keep) {
      const key = `slice_drop:${currentProfile.node_id}:${inputLabel.label}`;
      events.push({
        local_event_key: key,
        type: 'field_slice_drop',
        node_id: currentProfile.node_id,
        node_name: currentProfile.node_name,
        dropped_label: compactLabel(inputLabel),
        dropped_labels: [compactLabel(inputLabel)],
        evidence: result.evidence
      });
      return buildResult({ branches: [], events, sourceIntroAppliedNodes });
    }
    if (result.applied && result.keep) {
      const key = `slice_keep:${currentProfile.node_id}:${inputLabel.label}`;
      events.push({
        local_event_key: key,
        type: 'field_slice_keep',
        node_id: currentProfile.node_id,
        node_name: currentProfile.node_name,
        kept_label: compactLabel(inputLabel),
        kept_labels: [compactLabel(inputLabel)],
        evidence: result.evidence
      });
      flowMode = 'definite_flow';
    }
  }

  if (events.length === 0) {
    confidenceMultiplier = 0.95;
    const key = `unknown:${currentProfile.node_id}:${inputLabel.label}`;
    events.push({
      local_event_key: key,
      type: 'unknown_may_flow',
      node_id: currentProfile.node_id,
      node_name: currentProfile.node_name,
      propagated_label: compactLabel(inputLabel),
      propagated_labels: [compactLabel(inputLabel)],
      evidence: filterEvidence(currentProfile, edge)
    });
    if (flowMode !== 'derived_flow') flowMode = 'may_flow';
  }

  return buildResult({
    branches: [{
      label: inputLabel,
      flow_mode: flowMode,
      confidence_multiplier: confidenceMultiplier,
      trigger_context: nextTriggerContext,
      source_intro_applied_nodes: sourceIntroAppliedNodes,
      parent_label_flow_ids: [labelFlow.label_flow_id],
      filter_event_keys: events.map(event => event.local_event_key)
    }],
    events,
    sourceIntroAppliedNodes
  });
}

function shouldIntroduceSource(profile = {}, labelFlow = {}) {
  if (!profile.node_roles?.includes('data_introduction')) return false;
  if (isProducedArtifactProfile(profile)) return false;
  if (isPureControlSource(profile)) return false;
  if ((labelFlow.source_intro_applied_nodes || []).includes(profile.node_id)) return false;
  return (profile.data_profile?.labels || []).length > 0;
}

function isProducedArtifactProfile(profile = {}) {
  return profile.operation_type === 'produce_artifact' ||
    (profile.evidence || []).some(item => item.kind === 'formal_semantics.produce_artifact') ||
    (profile.action_steps || []).some(step => step.operation_type === 'produce_artifact');
}

function isPureControlSource(profile = {}) {
  const labels = profile.data_profile?.labels || [];
  const onlyPrompt = labels.length > 0 && labels.every(label => label.category === 'user_prompt');
  return profile.node_roles?.includes('control_context') && onlyPrompt;
}

function deriveSemanticLabels(label, profile, edge) {
  const text = filterEvidence(profile, edge);
  const matches = classifyTextLabels(text).filter(match => !['user_prompt', 'generic_data'].includes(match.category));
  if (matches.length === 0 || label.category !== 'user_prompt') return [];

  const derived = matches.map(match => createDerivedLabel({
    fromLabel: label,
    category: match.category,
    subtype: match.subtype,
    fieldName: match.subtype,
    fieldPath: '',
    introducedAt: profile.node_id,
    evidenceText: text,
    confidence: Math.min(0.8, Number(label.confidence || 0.7))
  }));
  return dedupeLabels(derived);
}

function sliceLabel(label, profile, edge) {
  const text = sliceIntentText(profile, edge);
  const matches = classifyTextLabels(text).filter(match => !['user_prompt', 'generic_data'].includes(match.category));
  if (matches.length === 0) return { applied: false, keep: true, evidence: text };
  return {
    applied: true,
    keep: matches.some(match => labelsMatch(label, match)),
    evidence: text
  };
}

function shouldRedactLabel(label, profile) {
  const text = filterEvidence(profile, null);
  const matches = classifyTextLabels(text).filter(match => match.category !== 'user_prompt');
  const redactsSpecificPii = /(email|phone|address|profile|pii|personal)/i.test(text);
  const specificPiiSubtype = specificPiiRedactionSubtype(text);
  const credentialRedaction = /secret|credential|api[_\-\s]?key|token|password|private[_\-\s]?key/i.test(text);
  const piiRedaction = redactsSpecificPii;
  if (credentialRedaction && label.category === 'credentials') return true;
  if (specificPiiSubtype) return label.category === 'pii' && label.subtype === specificPiiSubtype;
  if (piiRedaction && label.category === 'pii') return true;
  if (matches.length === 0) return label.category === 'credentials';
  if (/redact|mask|sanitize|scrub|strip|remove/i.test(text) && matches.every(match => ['file_content', 'generic_data'].includes(match.category))) {
    return label.category === 'credentials';
  }
  if (/redact|mask|sanitize|scrub|strip|remove/i.test(text) && !redactsSpecificPii && label.category !== 'credentials') {
    return false;
  }
  return matches.some(match => label.category === match.category || labelsMatch(label, match));
}

function createSummaryLabel(inputLabel, currentProfile, edge, evidenceKind) {
  return createSyntheticLabel({
    category: 'aggregate_data',
    subtype: 'summary',
    originNode: inputLabel.origin_node || currentProfile.node_id,
    originNodeName: inputLabel.origin_node_name || currentProfile.node_name || currentProfile.node_id,
    introducedAt: currentProfile.node_id,
    evidenceKind,
    evidenceText: filterEvidence(currentProfile, edge),
    confidence: Math.min(0.75, Number(inputLabel.confidence || 0.7))
  });
}

function shouldPreserveRawAfterSummary(profile = {}, edge = {}) {
  const text = filterEvidence(profile, edge);
  return /\b(raw|original|full|verbatim|complete|unmodified)\b/i.test(text);
}

function specificPiiRedactionSubtype(text = '') {
  const value = String(text || '');
  if (/(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(email|mail)|redactEmail|maskEmail|removeEmail/i.test(value)) return 'email';
  if (/(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(phone|mobile)|redactPhone|maskPhone|removePhone/i.test(value)) return 'phone';
  if (/(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(address)|redactAddress|maskAddress|removeAddress/i.test(value)) return 'address';
  if (/(redact|mask|sanitize|scrub|strip|remove)[A-Za-z0-9_.\-\s]*(profile)|redactProfile|maskProfile|removeProfile/i.test(value)) return 'profile';
  return '';
}

function labelsMatch(label, match) {
  if (!label || !match) return false;
  if (label.label === match.label) return true;
  return label.category === match.category && (!match.subtype || label.subtype === match.subtype);
}

function filterEvidence(profile = {}, edge = {}) {
  return [
    profile.node_name,
    profile.security_tags?.join(' '),
    profile.operation_tags?.join(' '),
    profile.evidence?.map(item => item.text).join(' '),
    edge?.data_flow?.from_param,
    edge?.data_flow?.to_param,
    edge?.data_flow?.data_type,
    edge?.semantic_reason
  ].filter(Boolean).join(' ');
}

function sliceIntentText(profile = {}, edge = {}) {
  return [
    profile.node_name,
    profile.evidence?.map(item => item.text).join(' '),
    edge?.data_flow?.from_param,
    edge?.data_flow?.to_param,
    edge?.data_flow?.data_type,
    edge?.semantic_reason
  ].filter(Boolean).join(' ');
}

function buildResult({ branches, events, sourceIntroAppliedNodes, terminated = false, terminationReason = '' }) {
  return {
    branches: branches || [],
    terminated,
    termination_reason: terminationReason,
    filter_events: (events || []).map(event => ({
      event_id: `filter_${shortHash([event.type, event.node_id, JSON.stringify(event)].join('|'))}`,
      ...event
    })),
    source_intro_applied_nodes: sourceIntroAppliedNodes || []
  };
}

function labelToTriggerContext(label, reason) {
  const nodeId = label?.origin_node || '';
  if (!nodeId) return [];
  return [{
    node_id: nodeId,
    node_name: label.origin_node_name || nodeId,
    reason
  }];
}

function mergeTriggerContextInto(target, additions) {
  const seen = new Set(target.map(item => item.node_id || item.node_name).filter(Boolean));
  for (const item of additions || []) {
    const key = item.node_id || item.node_name;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    target.push(item);
  }
}

function mergeTriggerContexts(a = [], b = []) {
  const result = [...a];
  mergeTriggerContextInto(result, b);
  return result;
}

function compactLabels(labels) {
  return dedupeLabels(labels).map(compactLabel);
}

function compactLabel(label = {}) {
  if (!label) return null;
  return {
    id: label.id,
    label: label.label,
    category: label.category,
    subtype: label.subtype,
    sensitivity: label.sensitivity,
    field_name: label.field_name,
    field_path: label.field_path,
    origin_node: label.origin_node,
    origin_node_name: label.origin_node_name,
    introduced_at: label.introduced_at,
    mode: label.mode,
    confidence: roundConfidence(label.confidence),
    evidence_level: label.evidence_level,
    evidence_kind: label.evidence_kind,
    evidence_text: label.evidence_text,
    ontology_version: label.ontology_version,
    ontology_label_id: label.ontology_label_id,
    requires_review: Boolean(label.requires_review),
    llm_review: label.llm_review || undefined,
    uncertainty: label.uncertainty || '',
    reason: label.reason || ''
  };
}

function dedupeLabels(labels) {
  const byKey = new Map();
  for (const label of labels || []) {
    if (!label) continue;
    const key = [
      label.label,
      label.origin_node,
      label.introduced_at || label.origin_node
    ].join('|');
    const existing = byKey.get(key);
    if (!existing || labelRank(label) > labelRank(existing)) {
      byKey.set(key, { ...label });
    }
  }
  return Array.from(byKey.values()).sort((a, b) => String(a.label).localeCompare(String(b.label)));
}

function labelRank(label = {}) {
  const level = { L4: 4, L3: 3, L2: 2, L1: 1, L0: 0 }[label.evidence_level] || 0;
  return level * 10 + Number(label.confidence || 0);
}

function cloneLabel(label) {
  return label ? { ...label } : null;
}

function roundConfidence(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0.3;
  return Math.max(0, Math.min(1, Math.round(n * 1000) / 1000));
}

module.exports = {
  applyLabelFlowFilter,
  compactLabels,
  compactLabel,
  dedupeLabels,
  mergeTriggerContextInto
};
