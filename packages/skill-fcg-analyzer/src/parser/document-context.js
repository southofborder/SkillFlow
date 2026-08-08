const fs = require('fs');
const path = require('path');
const { extractSections } = require('./skill-parser');

function buildDocumentationPlan(skillData = {}, readmeData = null, executableFiles = []) {
  const skillDoc = {
    file: 'SKILL.md',
    content: String(skillData.content || ''),
    sections: skillData.sections || []
  };
  const readmeDoc = readmeData && readmeData.exists
    ? {
        file: 'README.md',
        content: String(readmeData.content || ''),
        sections: extractSections(String(readmeData.content || ''))
      }
    : null;
  const allMarkdownDocs = findMarkdownFiles(skillData.skillRootDir)
    .map(filePath => readMarkdownDoc(skillData.skillRootDir, filePath))
    .filter(Boolean)
    .filter(doc => !isEntryMarkdown(doc.file));
  // Defect (4) fix: changelog / release-history / license files record past
  // events, not runtime actions. Keep them for review context but never treat
  // them as extraction sources (multi-search-engine was emitting
  // doc.context.changelog action nodes).
  const markdownDocs = allMarkdownDocs.filter(doc => !isNonInstructionMarkdown(doc.file));
  const nonInstructionDocs = allMarkdownDocs.filter(doc => isNonInstructionMarkdown(doc.file));
  const executableSourceFiles = (executableFiles || [])
    .map(filePath => normalizeSourcePath(skillData.skillRootDir, filePath))
    .filter(Boolean);
  const hasPrimaryExtractionSource = markdownDocs.length > 0 || executableSourceFiles.length > 0;
  const extractionDocs = dedupeDocs([
    { ...skillDoc, source_role: 'semantic_anchor' },
    ...markdownDocs.map(doc => ({ ...doc, source_role: 'extraction_source' }))
  ]);
  const reviewDocs = [skillDoc, readmeDoc, ...nonInstructionDocs].filter(Boolean);
  const sourcePolicy = {
    semantic_review_default_enabled: true,
    semantic_review_missing_key_behavior: 'rule_fallback_warning',
    skill_md_role: hasPrimaryExtractionSource ? 'semantic_anchor' : 'semantic_anchor_fallback',
    readme_md_role: readmeDoc ? 'review_only' : 'absent',
    extraction_doc_files: extractionDocs.map(doc => doc.file),
    executable_source_files: executableSourceFiles
  };

  return {
    extractionDocs,
    reviewDocs,
    sourcePolicy,
    documentationContext: {
      source_policy: sourcePolicy,
      skill_context: compactDocContext(skillDoc, sourcePolicy.skill_md_role),
      readme_context: readmeDoc ? compactDocContext(readmeDoc, 'review_only') : null,
      extraction_contexts: extractionDocs.map(doc => compactDocContext(doc, doc.source_role || 'extraction_source'))
    }
  };
}

function dedupeDocs(docs = []) {
  const byFile = new Map();
  for (const doc of docs || []) {
    const file = normalizeDocPath(doc.file || '');
    if (!file || byFile.has(file)) continue;
    byFile.set(file, { ...doc, file });
  }
  return Array.from(byFile.values());
}

function buildSourceContext(config = {}) {
  const content = String(config.content || '');
  const lines = content.split(/\r?\n/);
  const lineNumber = Number(config.line || 0);
  const lineIndex = Math.max(0, lineNumber - 1);
  const sourceLine = String(config.sourceText || lines[lineIndex] || '').trim();
  const before = lines.slice(Math.max(0, lineIndex - 2), lineIndex).map(line => line.trim()).filter(Boolean);
  const after = lines.slice(lineIndex + 1, lineIndex + 3).map(line => line.trim()).filter(Boolean);
  const grounded = config.grounded !== false;

  return {
    source_role: config.sourceRole || 'extraction_source',
    source_type: config.sourceType || 'markdown',
    file: normalizeDocPath(config.file || ''),
    line: lineNumber,
    column: Number(config.column || 0),
    section: config.section || '',
    source_line: sourceLine,
    before,
    after,
    action_evidence: {
      action: config.action || '',
      operation_type: config.operationType || '',
      snippet: String(config.actionSnippet || sourceLine || '').trim(),
      trigger: config.trigger || '',
      extraction_method: config.extractionMethod || '',
      grounded,
      derived: Boolean(config.derived),
      requires_review: !grounded || Boolean(config.requiresReview)
    }
  };
}

function findMarkdownFiles(rootDir) {
  const result = [];
  const ignoredDirs = new Set(['node_modules', '.git', '.svn', '.hg', 'dist', 'build', 'coverage']);
  if (!rootDir || !fs.existsSync(rootDir)) return result;

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (ignoredDirs.has(entry.name)) continue;
        walk(fullPath);
      } else if (entry.name.toLowerCase().endsWith('.md')) {
        result.push(fullPath);
      }
    }
  }

  walk(rootDir);
  return result;
}

function readMarkdownDoc(rootDir, filePath) {
  try {
    const relPath = normalizeDocPath(path.relative(rootDir, filePath));
    const content = fs.readFileSync(filePath, 'utf-8');
    return {
      file: relPath,
      content,
      sections: extractSections(content)
    };
  } catch (_) {
    return null;
  }
}

function compactDocContext(doc = {}, role = '') {
  const content = String(doc.content || '');
  return {
    file: normalizeDocPath(doc.file || ''),
    role,
    line_count: content ? content.split(/\r?\n/).length : 0,
    sections: (doc.sections || []).slice(0, 24).map(section => ({
      title: section.title || '',
      level: section.level || 0,
      startLine: section.startLine || 0,
      endLine: section.endLine || 0
    })),
    preview: truncate(content, 1600)
  };
}

function isEntryMarkdown(file = '') {
  const base = path.basename(normalizeDocPath(file)).toLowerCase();
  return base === 'skill.md' || base === 'readme.md';
}

// Markdown files that record history/metadata rather than runtime instructions.
// Matched on the file name stem so both CHANGELOG.md and docs/CHANGES.md hit.
const NON_INSTRUCTION_MD = /(^|[/_-])(changelog|change-log|changes|history|releases?|release-notes|news|license|licence|notice|authors|contributors|contributing|code-of-conduct)(\.[a-z]+)?$/i;

function isNonInstructionMarkdown(file = '') {
  const norm = normalizeDocPath(file);
  const base = path.basename(norm).toLowerCase().replace(/\.md$/, '');
  return NON_INSTRUCTION_MD.test(base) || NON_INSTRUCTION_MD.test(norm.toLowerCase());
}

function normalizeDocPath(fileRef) {
  return String(fileRef || '')
    .trim()
    .replace(/^['"`\s]+|['"`\s]+$/g, '')
    .replace(/[),.;:!?]+$/g, '')
    .replace(/\\/g, '/')
    .replace(/^\.\/+/, '')
    .replace(/\/+/g, '/');
}

function normalizeSourcePath(rootDir, filePath) {
  if (!filePath) return '';
  const raw = String(filePath || '');
  const relative = rootDir && path.isAbsolute(raw)
    ? path.relative(rootDir, raw)
    : raw;
  return normalizeDocPath(relative);
}

function truncate(value, max) {
  const text = String(value || '');
  return text.length > max ? `${text.slice(0, max)}...` : text;
}

module.exports = {
  buildDocumentationPlan,
  buildSourceContext,
  normalizeDocPath,
  normalizeSourcePath,
  findMarkdownFiles,
  isEntryMarkdown,
  isNonInstructionMarkdown
};
