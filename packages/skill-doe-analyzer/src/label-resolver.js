'use strict';

/**
 * Centralized label resolution for the DOE analyzer.
 *
 * Background: FCG security_profile may carry per-flow labels in one of two
 * shapes, and DOE must read both during the schema migration (FCG version
 * 4.9 -> 5.0):
 *
 *   - INLINE (legacy, <= 4.9): labelFlow.label is the full label object.
 *   - REFERENCED (new, >= 5.0): labelFlow.label_id points into a top-level
 *     security_profile.label_dictionary; the inline label is omitted.
 *
 * We verified on real data that label.id -> label content is strictly 1:1
 * (same id always means byte-identical label, including field_name/field_path),
 * so dictionary dereference is lossless.
 *
 * Design goals (explicitly addressing "could this make the data flow unclear or
 * silently default?"):
 *   1. SINGLE entry point. Every label read in DOE goes through resolveLabel /
 *      the context-cached labelByFlow — no scattered `labelFlow.label || dict[id]`.
 *   2. EXPLICIT miss handling. A label_id that resolves to nothing is recorded
 *      (onMiss callback) instead of silently becoming {}. The data flow stays
 *      traceable.
 *   3. BACKWARD/FORWARD compatible. Inline label wins when present; otherwise
 *      the dictionary is consulted. Old and new FCG both work, enabling a
 *      gradual migration without a flag day.
 */

/**
 * Build the label dictionary from a security_profile. Returns an empty Map for
 * legacy (inline-only) profiles, which is the signal that dereference is a no-op.
 */
function buildLabelDictionary(securityProfile = {}) {
  const raw = securityProfile.label_dictionary;
  const dict = new Map();
  if (raw && typeof raw === 'object') {
    for (const [id, label] of Object.entries(raw)) {
      if (label && typeof label === 'object') dict.set(id, label);
    }
  }
  return dict;
}

/**
 * Resolve a single label_flow's label.
 *
 * @param {object} labelFlow    the flow (may carry inline `label` or `label_id`)
 * @param {Map}    dictionary   label_id -> label object (empty for legacy data)
 * @param {function} [onMiss]   called with { label_flow_id, label_id } when a
 *                              label_id is present but missing from the dict.
 * @returns {object} the label object, or {} if genuinely absent.
 */
function resolveLabel(labelFlow = {}, dictionary = new Map(), onMiss = null) {
  // Inline label is authoritative when present (legacy data, or new data that
  // chose to inline). This is the only place precedence is decided.
  const inline = labelFlow.label;
  if (inline && typeof inline === 'object' && Object.keys(inline).length > 0) {
    return inline;
  }

  const labelId = labelFlow.label_id || inline?.id || '';
  if (labelId && dictionary.has(labelId)) {
    return dictionary.get(labelId);
  }

  // A label_id was declared but not found: surface it rather than silently
  // returning {}. Callers without onMiss still get {} (same as the old
  // `labelFlow.label || {}` behavior) so nothing crashes.
  if (labelId && typeof onMiss === 'function') {
    onMiss({ label_flow_id: labelFlow.label_flow_id || '', label_id: labelId });
  }
  return inline && typeof inline === 'object' ? inline : {};
}

module.exports = {
  buildLabelDictionary,
  resolveLabel
};
