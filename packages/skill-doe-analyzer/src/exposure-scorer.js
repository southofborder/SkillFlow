const fs = require('fs');
const path = require('path');
const { round3, clamp } = require('./utils');

const SENSITIVITY_SCORES = {
  low: 0.2,
  medium: 0.45,
  high: 0.8,
  critical: 1.0
};

const CATEGORY_SENSITIVITY = {
  credentials: 'critical',
  secret_material: 'critical',
  financial: 'critical',
  health: 'critical',
  biometric: 'critical',
  special_category: 'critical',
  security_data: 'high',
  pii: 'high',
  browser_data: 'high',
  enterprise: 'high',
  personal_record: 'high',
  database_record: 'high',
  communication: 'medium',
  file_content: 'medium',
  location: 'medium',
  ai_context: 'high',
  unknown_sensitive: 'high',
  device_data: 'medium',
  network_data: 'medium',
  user_prompt: 'medium',
  aggregate_data: 'medium',
  pseudonymous_data: 'medium',
  generic_data: 'low'
};

const CATEGORY_EXPOSURE = {
  credentials: 1.0,
  secret_material: 1.0,
  health: 0.9,
  biometric: 0.9,
  special_category: 0.9,
  financial: 0.9,
  security_data: 0.9,
  pii: 0.8,
  browser_data: 0.8,
  enterprise: 0.8,
  personal_record: 0.8,
  unknown_sensitive: 0.85,
  communication: 0.55,
  file_content: 0.55,
  database_record: 0.55,
  location: 0.55,
  device_data: 0.5,
  network_data: 0.5,
  ai_context: 0.75,
  user_prompt: 0.45,
  aggregate_data: 0.35,
  pseudonymous_data: 0.35,
  generic_data: 0.3
};

function scoreExposure({ labelFlow = {}, observation = {} }) {
  const label = labelFlow.label || {};
  const category = label.category || categoryFromLabel(label.label);
  const sensitivity = resolveLabelSensitivity(label);
  const labelSensitivity = CATEGORY_EXPOSURE[category] ?? SENSITIVITY_SCORES[sensitivity] ?? 0.3;
  const boundary = classifyDoeBoundary(observation);
  const boundaryRisk = scoreBoundaryRisk(observation, boundary);
  const exposureScore = boundary.boundary_crossed
    ? clamp(round3((0.6 * labelSensitivity) + (0.4 * boundaryRisk)))
    : 0;

  return {
    exposure_score: exposureScore,
    label_sensitivity: round3(labelSensitivity),
    boundary_risk: round3(boundaryRisk),
    boundary_crossed: boundary.boundary_crossed,
    boundary_basis: boundary.boundary_basis,
    exposure_tier: boundary.exposure_tier,
    evidence: [
      evidence('exposure.label_sensitivity', labelSensitivity, `category=${category}; sensitivity=${sensitivity}`),
      evidence('exposure.boundary_risk', boundaryRisk, boundarySummary(observation)),
      {
        kind: 'exposure.boundary_crossed',
        score: boundary.boundary_crossed ? 1 : 0,
        reason: boundary.boundary_basis.length ? boundary.boundary_basis.join('; ') : 'no DOE exposure boundary crossed'
      },
      {
        kind: 'exposure.tier',
        score: boundary.exposure_tier === 'high_sensitivity_egress' ? 1 : 0,
        reason: boundary.exposure_tier === 'high_sensitivity_egress'
          ? 'data genuinely leaves the local process or is retained — a real, severe egress'
          : 'data stays local (returned to the user / local process), not a real egress'
      }
    ]
  };
}

function resolveLabelSensitivity(label = {}) {
  const category = label.category || categoryFromLabel(label.label);
  return normalizeSensitivity(
    label.sensitivity ||
    ontologyLabelSensitivity(label.ontology_label_id || label.label) ||
    CATEGORY_SENSITIVITY[category] ||
    'low'
  );
}

let ontologySensitivityByLabel = null;

function ontologyLabelSensitivity(labelName = '') {
  if (!labelName) return '';
  if (!ontologySensitivityByLabel) ontologySensitivityByLabel = loadOntologySensitivity();
  return ontologySensitivityByLabel.get(labelName) || '';
}

function loadOntologySensitivity() {
  try {
    const ontologyPath = path.resolve(__dirname, '..', '..', 'skill-fcg-analyzer', 'src', 'security', 'label-ontology.json');
    const raw = JSON.parse(fs.readFileSync(ontologyPath, 'utf-8'));
    return new Map((raw.labels || []).map(entry => [entry.label, entry.sensitivity]));
  } catch {
    return new Map();
  }
}

function classifyDoeBoundary(observation = {}) {
  const boundary = observation.boundary || {};
  const trust = String(boundary.trust_boundary || '').toLowerCase();
  const receiver = String(boundary.receiver_scope || '').toLowerCase();
  const retention = String(boundary.retention_scope || '').toLowerCase();
  const surface = String(boundary.data_surface || '').toLowerCase();
  const basis = [];

  if (['external_network', 'model_provider', 'persistent_storage', 'user_visible'].includes(trust)) {
    basis.push(`trust_boundary.${trust}`);
  }
  if (['model_provider', 'first_party_service', 'third_party_service', 'public_network', 'user_recipient'].includes(receiver)) {
    basis.push(`receiver_scope.${receiver}`);
  }
  if (['persistent', 'external'].includes(retention)) {
    basis.push(`retention_scope.${retention}`);
  }
  if (['network', 'llm_context'].includes(surface)) {
    basis.push(`data_surface.${surface}`);
  }

  const uniqueBasis = Array.from(new Set(basis));
  const boundaryCrossed = uniqueBasis.length > 0;
  // 语义分类维度(不改任何分数,只给下游/LLM 一个可引用的标签):所有真外泄——数据真正
  // 离开本地进程或被留痕的每一档——统一标 high_sensitivity_egress,不分档降格。model_provider
  // 与 external_network/third_party/first_party/public/webhook/persistent_storage 一视同仁,
  // 都是真实且严重的外泄面,无一是"可信内部"。
  // 唯一例外:数据仅"回给用户自己"(trust_boundary.user_visible)且无其它外发/留痕信号——
  // 数据未真正离开,归 local(boundary_risk 亦仅 0.2)。凡存在任一非 user_visible 的 basis
  // 信号即为真外泄。
  const egressSignal = uniqueBasis.some(b => b !== 'trust_boundary.user_visible');
  return {
    boundary_crossed: boundaryCrossed,
    boundary_basis: uniqueBasis,
    exposure_tier: egressSignal ? 'high_sensitivity_egress' : 'local'
  };
}

function scoreBoundaryRisk(observation = {}, boundaryClassification = null) {
  const boundary = observation.boundary || {};
  const tags = new Set(observation.security_tags || []);
  const trust = String(boundary.trust_boundary || '').toLowerCase();
  const receiver = String(boundary.receiver_scope || '').toLowerCase();
  const retention = String(boundary.retention_scope || '').toLowerCase();
  const crossed = boundaryClassification || classifyDoeBoundary(observation);

  if (!crossed.boundary_crossed) return 0.1;
  if (trust === 'external_network' || receiver === 'third_party_service' || receiver === 'public_network' || tags.has('webhook_post')) return 0.95;
  if (trust === 'model_provider' || receiver === 'model_provider') return 0.9;
  if (receiver === 'first_party_service' || retention === 'external') return 0.75;
  if (trust === 'persistent_storage' || retention === 'persistent') return 0.55;
  if (trust === 'user_visible' || trust === 'local_process') return 0.2;
  return 0.35;
}

// exposure-scorer keeps its own categoryFromLabel: it falls back to
// 'generic_data' (not '') so sensitivity/exposure map lookups always hit a key.
function categoryFromLabel(label = '') {
  const [category] = String(label || '').split('.');
  return category || 'generic_data';
}

function normalizeSensitivity(value) {
  const normalized = String(value || '').toLowerCase();
  return Object.hasOwn(SENSITIVITY_SCORES, normalized) ? normalized : 'low';
}

function boundarySummary(observation = {}) {
  const b = observation.boundary || {};
  return [
    `roles=${(observation.node_roles || []).join(',')}`,
    `trust=${b.trust_boundary || ''}`,
    `receiver=${b.receiver_scope || ''}`,
    `retention=${b.retention_scope || ''}`,
    `operation=${observation.operation_type || ''}`
  ].join('; ');
}

function evidence(kind, score, reason) {
  return { kind, score: round3(score), reason };
}

module.exports = {
  scoreExposure,
  scoreBoundaryRisk,
  classifyDoeBoundary,
  resolveLabelSensitivity,
  CATEGORY_SENSITIVITY,
  CATEGORY_EXPOSURE
};
