const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { createFlowPathContext, resolveLabelFlowPath } = require('./flow-path-utils');
const { stableStringify } = require('./utils');

const DEFAULT_SCOPE = 'potential';
const DEFAULT_FORMAT = 'both';
const ZIP_CACHE = new Map();

function createDoePathReport(options = {}) {
  const root = path.resolve(options.root || process.cwd());
  const fcgRoot = path.resolve(options.fcgRoot || path.join(root, 'fcg'));
  const doeRoot = path.resolve(options.doeRoot || path.join(root, 'doe'));
  const zipsRoot = path.resolve(options.zipsRoot || path.join(root, 'zips'));
  const scope = normalizeScope(options.scope || DEFAULT_SCOPE);
  const doeFiles = discoverDoeFiles(doeRoot);
  const summaryMap = loadDoeSummaryMap(doeRoot);
  const skills = [];
  const paths = [];
  const errors = [];

  for (const doePath of doeFiles) {
    const match = resolveSkillInputs({ doePath, fcgRoot, zipsRoot, summaryMap });
    if (!match.fcgPath || !fs.existsSync(match.fcgPath)) {
      errors.push({ doe_path: doePath, message: `FCG JSON not found for ${doePath}` });
      continue;
    }
    const fcg = readJson(match.fcgPath);
    const doe = readJson(doePath);
    const skillId = skillIdFromPath(doePath);
    const skillName = fcg.meta?.skill_name || doe.skill_name || skillId;
    if (options.skill && !matchesSkillFilter(options.skill, { skillId, skillName, fcgPath: match.fcgPath, doePath })) {
      continue;
    }

    const context = buildSkillContext({ fcg, doe, fcgPath: match.fcgPath, doePath, zipPath: match.zipPath });
    const skillPaths = [];
    for (const assessment of doe.assessments || []) {
      if (!assessmentInScope(assessment, scope)) continue;
      const item = naturalizeAssessment({ assessment, context });
      skillPaths.push(item);
      paths.push(item);
    }

    skills.push({
      skill_id: skillId,
      skill_name: skillName,
      fcg_path: match.fcgPath,
      doe_path: doePath,
      zip_path: match.zipPath || '',
      path_count: skillPaths.length,
      assessment_count: Number(doe.statistics?.assessment_count || 0),
      potential_doe_count: skillPaths.filter(item => item.potential_doe).length,
      requires_review_count: skillPaths.filter(item => item.requires_review).length
    });
  }

  return {
    generated_at: new Date().toISOString(),
    root,
    scope,
    summary: buildReportSummary({ skills, paths, errors, scope }),
    skills,
    paths,
    errors
  };
}

function writeDoePathReport(report, options = {}) {
  const format = normalizeFormat(options.format || DEFAULT_FORMAT);
  const output = path.resolve(options.output || path.join(report.root, 'doe', 'reports'));
  const written = {};
  if (format === 'json' || format === 'both') {
    const jsonPath = outputPathFor(output, 'doe-path-report.json', '.json');
    saveText(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
    written.json = jsonPath;
  }
  if (format === 'md' || format === 'both') {
    const mdPath = outputPathFor(output, 'doe-path-report.md', '.md');
    saveText(mdPath, renderPathReportMarkdown(report));
    written.markdown = mdPath;
  }
  return written;
}

function renderPathReportMarkdown(report = {}) {
  const lines = [];
  lines.push('# DOE Naturalized Path Report');
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push(`- Generated: ${report.generated_at || ''}`);
  lines.push(`- Scope: ${report.scope || ''}`);
  lines.push(`- Skills: ${report.summary?.skill_count || 0}`);
  lines.push(`- Paths: ${report.summary?.path_count || 0}`);
  lines.push(`- Potential DOE: ${report.summary?.potential_doe_count || 0}`);
  lines.push(`- Requires review: ${report.summary?.requires_review_count || 0}`);
  lines.push(`- Zip source recovered: ${report.summary?.zip_source_count || 0}`);
  lines.push(`- Fallback source used: ${report.summary?.fallback_source_count || 0}`);
  lines.push('');
  lines.push('### Boundary Counts');
  lines.push('');
  for (const [boundary, count] of Object.entries(report.summary?.boundary_counts || {})) {
    lines.push(`- ${boundary}: ${count}`);
  }
  lines.push('');
  lines.push('## Legend');
  lines.push('');
  lines.push('- `label_subtype=path` means a file path, file name, or path-like string, not the graph path or label flow path.');
  lines.push('- `template_or_example_source` means the source line appears to come from template/example documentation and may be a false positive execution step.');
  lines.push('- `path_label_metadata_only` means the label likely exposes path metadata rather than raw file contents.');
  lines.push('- `model_context_expected_flow` means the boundary is model-provider LLM context; this may be expected for ordinary skill activation and should be judged with task necessity.');
  lines.push('- `zip_source_missing_fallback_used` means the report could not recover the exact zip line and used FCG embedded context instead.');
  lines.push('');
  lines.push('## Naturalized Paths');
  lines.push('');

  const pathsBySkill = groupBy(report.paths || [], item => item.skill_id);
  for (const skill of report.skills || []) {
    const skillPaths = pathsBySkill.get(skill.skill_id) || [];
    if (!skillPaths.length) continue;
    lines.push(`### ${escapeMarkdown(skill.skill_id)} - ${escapeMarkdown(skill.skill_name)}`);
    lines.push('');
    lines.push(`- FCG: \`${skill.fcg_path}\``);
    lines.push(`- DOE: \`${skill.doe_path}\``);
    if (skill.zip_path) lines.push(`- Zip: \`${skill.zip_path}\``);
    lines.push('');

    const groups = groupPathAssessments(skillPaths);
    for (const group of groups) {
      lines.push(`#### ${escapeMarkdown(group.title)}`);
      lines.push('');
      lines.push(`- Source: ${sourceQuoteMarkdown(group.source_quote)}`);
      lines.push(`- Boundary: ${escapeMarkdown(group.boundary_text)}`);
      lines.push(`- Node path: ${escapeMarkdown(group.node_path_text.join(' -> '))}`);
      lines.push(`- Audit notes: ${group.audit_notes.length ? group.audit_notes.map(item => `\`${item}\``).join(', ') : 'none'}`);
      lines.push('');
      lines.push(group.natural_language);
      lines.push('');
      lines.push('| Assessment | Label | Subtype | Necessity | Weakest | Potential | Review |');
      lines.push('| --- | --- | --- | ---: | --- | --- | --- |');
      for (const item of group.items) {
        lines.push([
          item.assessment_id,
          item.label,
          item.label_subtype,
          formatNumber(item.scores.necessity_score),
          item.scores.necessity_basis || '',
          item.potential_doe ? 'yes' : 'no',
          item.requires_review ? 'yes' : 'no'
        ].map(escapePipe).join(' | ').replace(/^/, '| ').replace(/$/, ' |'));
        if (item.judge_mode === 'rule_only' && item.llm_skip_reason) {
          lines.push(`  - ${escapeMarkdown(item.assessment_id)} judge: rule_only (${escapeMarkdown(item.llm_skip_reason)})`);
        } else if (item.judge_mode === 'llm_judged') {
          lines.push(`  - ${escapeMarkdown(item.assessment_id)} judge: llm_judged; weakest=${escapeMarkdown(item.scores.necessity_basis || '')}`);
        }
      }
      lines.push('');
    }
  }

  if ((report.errors || []).length) {
    lines.push('## Errors');
    lines.push('');
    for (const error of report.errors) {
      lines.push(`- ${escapeMarkdown(error.doe_path || '')}: ${escapeMarkdown(error.message || '')}`);
    }
    lines.push('');
  }

  return `${lines.join('\n')}\n`;
}

function naturalizeAssessment({ assessment, context }) {
  const labelFlow = context.labelFlowById.get(assessment.label_flow_id) || {};
  const observation = context.observationById.get(assessment.observation_id) || {};
  const resolvedPath = resolveLabelFlowPath(labelFlow, context.flowPathContext || {});
  const pathNodes = (resolvedPath.node_path || []).map(nodeId => context.nodeById.get(nodeId)).filter(Boolean);
  const boundaryNode = context.nodeById.get(observation.node_id || assessment.observation_node_id) ||
    context.nodeById.get(labelFlow.current_node) ||
    pathNodes[pathNodes.length - 1] ||
    {};
  const sourceQuote = recoverSourceQuote({ zipPath: context.zipPath, node: boundaryNode });
  const boundary = observation.boundary || boundaryFromAssessment(assessment);
  const boundaryText = boundaryPhrase(boundary);
  const nodePathText = pathNodes.length
    ? pathNodes.map(node => nodeDisplayText(node))
    : [nodeDisplayText(boundaryNode)];
  const auditNotes = auditNotesFor({ assessment, boundary, sourceQuote, node: boundaryNode });
  const naturalLanguage = buildNaturalLanguage({
    assessment,
    sourceQuote,
    boundaryText,
    nodePathText,
    auditNotes
  });

  return {
    skill_id: context.skillId,
    skill_name: context.skillName,
    assessment_id: assessment.assessment_id || '',
    observation_id: assessment.observation_id || '',
    label_flow_id: assessment.label_flow_id || '',
    label: assessment.label || '',
    label_category: assessment.label_category || '',
    label_subtype: assessment.label_subtype || '',
    boundary,
    boundary_text: boundaryText,
    natural_language: naturalLanguage,
    source_quote: sourceQuote,
    node_path_text: nodePathText,
    scores: {
      doe_score: assessment.doe_score,
      exposure_score: assessment.exposure_score,
      necessity_score: assessment.necessity_score,
      rule_necessity_score: assessment.rule_necessity_score,
      llm_necessity_score: assessment.llm_necessity_score,
      local_necessity: assessment.local_necessity || {},
      global_necessity: assessment.global_necessity || {},
      necessity_basis: assessment.necessity_basis || ''
    },
    judge_mode: resolveJudgeMode(assessment),
    llm_skip_reason: assessment.llm_judge?.skipped ? assessment.llm_judge.skip_reason || '' : '',
    audit_notes: auditNotes,
    potential_doe: Boolean(assessment.potential_doe),
    requires_review: Boolean(assessment.requires_review),
    high_score: Boolean(assessment.high_score),
    llm_judge: assessment.llm_judge || null,
    fcg_path: context.fcgPath,
    doe_path: context.doePath,
    zip_path: context.zipPath || ''
  };
}

function resolveJudgeMode(assessment = {}) {
  if (assessment.llm_judge?.skipped) return 'rule_only';
  if (assessment.llm_judge && assessment.llm_judge.skipped !== true) return 'llm_judged';
  return 'rule_only';
}

function buildSkillContext({ fcg, doe, fcgPath, doePath, zipPath }) {
  const skillId = skillIdFromPath(doePath);
  return {
    skillId,
    skillName: fcg.meta?.skill_name || doe.skill_name || skillId,
    fcgPath,
    doePath,
    zipPath,
    nodeById: new Map((fcg.nodes || []).map(node => [node.id, node])),
    labelFlowById: new Map((fcg.security_profile?.label_flows || []).map(flow => [flow.label_flow_id, flow])),
    flowPathContext: createFlowPathContext(fcg),
    observationById: new Map((fcg.security_profile?.observations || []).map(observation => [observation.observation_id, observation]))
  };
}

function buildNaturalLanguage({ assessment, sourceQuote, boundaryText, nodePathText, auditNotes }) {
  const source = sourceQuote.text
    ? `${sourceQuote.file || 'unknown file'}:${sourceQuote.line || '?'} "${sourceQuote.text}"`
    : 'an unresolved source line';
  const label = `${assessment.label || 'unknown label'}${assessment.label_subtype ? ` (subtype=${assessment.label_subtype})` : ''}`;
  const status = assessment.potential_doe
    ? 'potential DOE'
    : (assessment.requires_review ? 'requires review' : 'non-potential DOE');
  const weakest = assessment.necessity_basis || 'unknown necessity component';
  const notes = auditNotes.length ? ` Audit notes: ${auditNotes.join(', ')}.` : '';
  return `Source ${source} was identified as ${label}; the label flow follows ${nodePathText.join(' -> ')} and crosses ${boundaryText}. The DOE assessment is ${status} because the weakest necessity component is ${weakest}.${notes}`;
}

function recoverSourceQuote({ zipPath, node = {}, contextLines = 1 }) {
  const location = node.location || {};
  const sourceContext = node.source_context || {};
  const file = location.file || sourceContext.file || '';
  const line = Number(location.line || sourceContext.line || 0);
  if (zipPath && file && line > 0) {
    try {
      const zipText = readZipTextEntry(zipPath, file);
      if (zipText) {
        const lines = zipText.split(/\r?\n/);
        const index = line - 1;
        if (index >= 0 && index < lines.length) {
          return {
            source: 'zip',
            file: normalizeDisplayFile(file, zipPath),
            line,
            text: String(lines[index] || '').trim(),
            before: lines.slice(Math.max(0, index - contextLines), index).map(item => item.trim()),
            after: lines.slice(index + 1, index + 1 + contextLines).map(item => item.trim())
          };
        }
      }
    } catch {
      // fall back to embedded FCG evidence below
    }
  }

  const fallback = sourceContext.source_line ||
    node.instructionText ||
    node.formal_semantics?.evidence?.text ||
    node.description ||
    '';
  return {
    source: fallback ? 'fcg' : 'none',
    file: file || sourceContext.file || '',
    line: line || sourceContext.line || null,
    text: String(fallback || '').trim(),
    before: [],
    after: []
  };
}

function auditNotesFor({ assessment, boundary = {}, sourceQuote = {}, node = {} }) {
  const notes = [];
  const file = String(sourceQuote.file || node.location?.file || node.source_context?.file || '');
  const section = String(node.location?.section || node.source_context?.section || '');
  const text = String(sourceQuote.text || node.source_context?.source_line || node.instructionText || '');
  if (/skill-template|references\/examples|\\references\\examples|template|example/i.test(`${file} ${section}`)) {
    notes.push('template_or_example_source');
  }
  if (String(assessment.label_subtype || '').toLowerCase() === 'path') {
    notes.push('path_label_metadata_only');
  }
  if (boundary.trust_boundary === 'model_provider' ||
      boundary.receiver_scope === 'model_provider' ||
      boundary.data_surface === 'llm_context') {
    notes.push('model_context_expected_flow');
  }
  if (sourceQuote.source !== 'zip') {
    notes.push('zip_source_missing_fallback_used');
  }
  if (/^\s*(good|bad):/i.test(text) || /copy and customize/i.test(text)) {
    addUnique(notes, 'template_or_example_source');
  }
  return notes;
}

function groupPathAssessments(paths = []) {
  const grouped = groupBy(paths, item => [
    item.observation_id,
    item.node_path_text.join('>'),
    stableStringify(item.boundary)
  ].join('::'));
  return [...grouped.values()].map(items => {
    const first = items[0];
    return {
      title: `${first.observation_id || 'observation'} (${items.length} assessment${items.length === 1 ? '' : 's'})`,
      source_quote: first.source_quote,
      boundary_text: first.boundary_text,
      node_path_text: first.node_path_text,
      natural_language: first.natural_language,
      audit_notes: unique(items.flatMap(item => item.audit_notes || [])),
      items
    };
  });
}

function assessmentInScope(assessment = {}, scope = DEFAULT_SCOPE) {
  if (scope === 'all') return true;
  if (scope === 'boundary') return Boolean(assessment.boundary_crossed);
  return Boolean(assessment.potential_doe || assessment.requires_review);
}

function discoverDoeFiles(doeRoot) {
  const root = path.resolve(doeRoot);
  const skillsDir = path.join(root, 'skills');
  const searchDir = fs.existsSync(skillsDir) && fs.statSync(skillsDir).isDirectory() ? skillsDir : root;
  if (!fs.existsSync(searchDir)) return [];
  return fs.readdirSync(searchDir)
    .filter(name => name.endsWith('-doe.json'))
    .map(name => path.join(searchDir, name))
    .sort((a, b) => a.localeCompare(b));
}

function loadDoeSummaryMap(doeRoot) {
  const summaryPath = path.join(doeRoot, 'doe-summary.json');
  const map = new Map();
  if (!fs.existsSync(summaryPath)) return map;
  try {
    const summary = readJson(summaryPath);
    for (const result of summary.results || []) {
      if (result.doe_path) map.set(path.resolve(result.doe_path), result);
    }
  } catch {
    return map;
  }
  return map;
}

function resolveSkillInputs({ doePath, fcgRoot, zipsRoot, summaryMap }) {
  const summary = summaryMap.get(path.resolve(doePath)) || {};
  const fcgPath = summary.fcg_path && fs.existsSync(summary.fcg_path)
    ? path.resolve(summary.fcg_path)
    : resolveFcgPathFromDoe(doePath, fcgRoot);
  let zipPath = '';
  if (fcgPath && fs.existsSync(fcgPath)) {
    try {
      const fcg = readJson(fcgPath);
      if (fcg.meta?.input_source && fs.existsSync(fcg.meta.input_source)) {
        zipPath = path.resolve(fcg.meta.input_source);
      }
    } catch {
      zipPath = '';
    }
  }
  if (!zipPath) {
    zipPath = resolveZipPathFromFcg(fcgPath, zipsRoot);
  }
  return { fcgPath, zipPath };
}

function resolveFcgPathFromDoe(doePath, fcgRoot) {
  const base = path.basename(doePath).replace(/-doe\.json$/i, '-sfg.json');
  const skillsPath = path.join(fcgRoot, 'skills', base);
  if (fs.existsSync(skillsPath)) return skillsPath;
  const rootPath = path.join(fcgRoot, base);
  if (fs.existsSync(rootPath)) return rootPath;
  return skillsPath;
}

function resolveZipPathFromFcg(fcgPath, zipsRoot) {
  if (!fcgPath || !fs.existsSync(zipsRoot)) return '';
  const base = path.basename(fcgPath)
    .replace(/-sfg\.json$/i, '')
    .replace(/^skill_\d+-/, '');
  const match = fs.readdirSync(zipsRoot)
    .filter(name => /\.zip$/i.test(name))
    .find(name => path.basename(name, '.zip') === base || path.basename(name, '.zip').endsWith(base));
  return match ? path.join(zipsRoot, match) : '';
}

function readZipTextEntry(zipPath, entryName) {
  const entries = readZipEntries(zipPath);
  const resolved = resolveZipEntryName(entries, entryName);
  if (!resolved) return '';
  return entries.get(resolved).toString('utf8');
}

function readZipEntries(zipPath) {
  const key = path.resolve(zipPath);
  if (ZIP_CACHE.has(key)) return ZIP_CACHE.get(key);
  const buffer = fs.readFileSync(key);
  const entries = new Map();
  let offset = 0;
  while (offset + 30 <= buffer.length) {
    const signature = buffer.readUInt32LE(offset);
    if (signature !== 0x04034b50) {
      offset += 1;
      continue;
    }
    const flags = buffer.readUInt16LE(offset + 6);
    const method = buffer.readUInt16LE(offset + 8);
    const compressedSize = buffer.readUInt32LE(offset + 18);
    const fileNameLength = buffer.readUInt16LE(offset + 26);
    const extraLength = buffer.readUInt16LE(offset + 28);
    const nameStart = offset + 30;
    const nameEnd = nameStart + fileNameLength;
    const dataStart = nameEnd + extraLength;
    const dataEnd = dataStart + compressedSize;
    if (dataEnd > buffer.length || compressedSize === 0xffffffff || (flags & 0x08)) {
      offset = nameEnd;
      continue;
    }
    const name = buffer.toString('utf8', nameStart, nameEnd).replace(/\\/g, '/');
    const raw = buffer.subarray(dataStart, dataEnd);
    if (!name.endsWith('/')) {
      if (method === 0) entries.set(name, Buffer.from(raw));
      else if (method === 8) entries.set(name, zlib.inflateRawSync(raw));
    }
    offset = dataEnd;
  }
  ZIP_CACHE.set(key, entries);
  return entries;
}

function resolveZipEntryName(entries, requestedName) {
  const normalized = normalizeEntryLikePath(requestedName);
  if (entries.has(normalized)) return normalized;
  const names = [...entries.keys()];
  const suffix = `/${normalized}`;
  const suffixMatch = names.find(name => name.endsWith(suffix) || normalized.endsWith(`/${name}`));
  if (suffixMatch) return suffixMatch;
  const base = path.posix.basename(normalized);
  const baseMatches = names.filter(name => path.posix.basename(name) === base);
  return baseMatches.length === 1 ? baseMatches[0] : '';
}

function normalizeEntryLikePath(value) {
  let text = String(value || '').replace(/\\/g, '/');
  text = text.replace(/^[A-Za-z]:\//, '');
  const markers = ['/assets/', '/hooks/', '/references/', '/scripts/'];
  for (const marker of markers) {
    const index = text.lastIndexOf(marker);
    if (index >= 0) return text.slice(index + 1);
  }
  const skillIndex = text.lastIndexOf('/SKILL.md');
  if (skillIndex >= 0) return 'SKILL.md';
  const readmeIndex = text.lastIndexOf('/README.md');
  if (readmeIndex >= 0) return 'README.md';
  return text.replace(/^\/+/, '');
}

function buildReportSummary({ skills, paths, errors, scope }) {
  const boundaryCounts = {};
  for (const item of paths) {
    const key = boundaryKey(item.boundary);
    boundaryCounts[key] = (boundaryCounts[key] || 0) + 1;
  }
  return {
    scope,
    skill_count: skills.filter(skill => skill.path_count > 0).length,
    path_count: paths.length,
    potential_doe_count: paths.filter(item => item.potential_doe).length,
    requires_review_count: paths.filter(item => item.requires_review).length,
    zip_source_count: paths.filter(item => item.source_quote?.source === 'zip').length,
    fallback_source_count: paths.filter(item => item.source_quote?.source !== 'zip').length,
    boundary_counts: sortObject(boundaryCounts),
    error_count: errors.length
  };
}

function normalizeScope(value) {
  const scope = String(value || DEFAULT_SCOPE).toLowerCase();
  if (['potential', 'boundary', 'all'].includes(scope)) return scope;
  throw new Error('--scope must be potential, boundary, or all');
}

function normalizeFormat(value) {
  const format = String(value || DEFAULT_FORMAT).toLowerCase();
  if (['md', 'json', 'both'].includes(format)) return format;
  throw new Error('--format must be md, json, or both');
}

function boundaryFromAssessment(assessment = {}) {
  return {
    basis: assessment.boundary_basis || []
  };
}

function boundaryPhrase(boundary = {}) {
  const parts = [
    boundary.trust_boundary && `trust=${boundary.trust_boundary}`,
    boundary.receiver_scope && `receiver=${boundary.receiver_scope}`,
    boundary.retention_scope && `retention=${boundary.retention_scope}`,
    boundary.data_surface && `surface=${boundary.data_surface}`
  ].filter(Boolean);
  return parts.length ? parts.join(', ') : 'an unspecified boundary';
}

function boundaryKey(boundary = {}) {
  return [
    boundary.trust_boundary || 'unknown_trust',
    boundary.receiver_scope || 'unknown_receiver',
    boundary.retention_scope || 'unknown_retention',
    boundary.data_surface || 'unknown_surface'
  ].join('/');
}

function nodeDisplayText(node = {}) {
  const location = node.location || {};
  const file = location.file || node.source_context?.file || '';
  const line = location.line || node.source_context?.line || '';
  const text = node.instructionText || node.source_context?.source_line || node.description || node.name || node.id || '';
  const ref = [file, line].filter(Boolean).join(':');
  return `${ref || node.id || node.name || 'node'} ${quoteShort(text)}`.trim();
}

function sourceQuoteMarkdown(source = {}) {
  const ref = [source.file, source.line].filter(Boolean).join(':') || 'unknown source';
  const text = source.text ? ` "${escapeMarkdown(source.text)}"` : '';
  return `${escapeMarkdown(ref)}${text} (${source.source || 'unknown'})`;
}

function normalizeDisplayFile(file, zipPath) {
  const normalized = normalizeEntryLikePath(file);
  if (zipPath) {
    const entries = readZipEntries(zipPath);
    return resolveZipEntryName(entries, normalized) || normalized;
  }
  return normalized;
}

function matchesSkillFilter(filter, skill) {
  const text = String(filter || '').toLowerCase();
  return [
    skill.skillId,
    skill.skillName,
    path.basename(skill.fcgPath || ''),
    path.basename(skill.doePath || '')
  ].some(value => String(value || '').toLowerCase().includes(text));
}

function skillIdFromPath(filePath) {
  const base = path.basename(filePath).replace(/-(doe|sfg)\.json$/i, '');
  const match = base.match(/^(skill_\d+)/i);
  return match ? match[1] : base;
}

function outputPathFor(output, fileName, extension) {
  if (/\.(md|json)$/i.test(output)) {
    return output.replace(/\.(md|json)$/i, extension);
  }
  return path.join(output, fileName);
}

function groupBy(items, getKey) {
  const map = new Map();
  for (const item of items) {
    const key = getKey(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return map;
}

function sortObject(value = {}) {
  return Object.fromEntries(Object.entries(value).sort((a, b) => a[0].localeCompare(b[0])));
}

function unique(values = []) {
  return [...new Set(values.filter(Boolean))];
}

function addUnique(values, value) {
  if (!values.includes(value)) values.push(value);
}

function quoteShort(value, max = 120) {
  const text = String(value || '').trim().replace(/\s+/g, ' ');
  return text ? `"${text.length > max ? `${text.slice(0, max)}...` : text}"` : '';
}

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(3).replace(/0+$/, '').replace(/\.$/, '') : '';
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function saveText(filePath, content) {
  fs.mkdirSync(path.dirname(path.resolve(filePath)), { recursive: true });
  fs.writeFileSync(filePath, content, 'utf8');
}

function escapeMarkdown(value) {
  return String(value ?? '').replace(/\r?\n/g, ' ');
}

function escapePipe(value) {
  return String(value ?? '').replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

module.exports = {
  createDoePathReport,
  writeDoePathReport,
  renderPathReportMarkdown,
  naturalizeAssessment,
  recoverSourceQuote,
  readZipTextEntry,
  readZipEntries,
  assessmentInScope,
  normalizeScope,
  normalizeFormat
};
