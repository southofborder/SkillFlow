const fs = require('fs');
const path = require('path');
const { buildSourceContext } = require('./document-context');

const TOOL_NAME_REGEX = /\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\b/g;
const TOOL_CALL_REGEX = /([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\s*\(/g;

/**
 * Extract tool calls from selected markdown extraction docs and JS files.
 *
 * @param {Object} skillData
 * @param {Object|null} readmeData
 * @param {Array<string>} scriptFiles
 * @returns {Array<Object>}
 */
function extractToolCalls(skillData, readmeData, scriptFiles, options = {}) {
  const tools = [];
  const markdownDocs = Array.isArray(options.markdownDocs)
    ? options.markdownDocs
    : [{
        file: 'SKILL.md',
        content: skillData.content,
        sections: skillData.sections || []
      }];

  for (const doc of markdownDocs) {
    if (isTemplateOrExampleMarkdown(doc.file || '', doc.content || '')) continue;
    tools.push(...extractFromMarkdown(doc.content, doc.sections || [], doc.file || 'SKILL.md'));
  }

  for (const scriptFile of scriptFiles) {
    if (!isJavaScriptLikeFile(scriptFile)) continue;
    tools.push(...extractFromJsFile(scriptFile, { rootDir: options.rootDir || skillData.skillRootDir }));
  }

  tools.push(createImplicitLlmNode());

  return assignCallSiteIdentity(deduplicateCallSites(tools));
}

/**
 * Extract tool calls from markdown content.
 *
 * @param {string} content
 * @param {Array} sections
 * @param {string} fileName
 * @returns {Array<Object>}
 */
function extractFromMarkdown(content, sections, fileName) {
  const tools = [];

  for (const block of extractJsonBlocks(content)) {
    tools.push(...extractToolsFromJsonBlock(block.content, block.line, fileName, sections, content));
  }

  for (const block of extractJsBlocks(content)) {
    tools.push(...extractToolsFromCode(block.content, block.line, fileName, sections, {
      sourceContent: content,
      sourceType: 'markdown_code_block'
    }));
  }

  tools.push(...extractToolsFromTables(content, fileName, sections));
  tools.push(...extractToolsFromInline(content, fileName, sections));

  return tools;
}

function createImplicitLlmNode() {
  return {
    name: 'llm.inference',
    action: 'inference',
    type: 'builtin_call',
    description: 'Implicit LLM call: Skill content (SKILL.md) is injected into LLM context when activated',
    input: {
      skill_content: { type: 'string', required: true, example: 'Full SKILL.md content' },
      user_query: { type: 'string', required: true },
      context: { type: 'string', required: false }
    },
    output: {
      response: { type: 'string' },
      actions: { type: 'array' }
    },
    location: {
      file: 'SKILL.md',
      line: 1,
      section: 'Implicit: OpenClaw Skill Activation'
    },
    isCritical: true
  };
}

function extractJsonBlocks(content) {
  const blocks = [];
  const regex = /```(?:json)?\s*\n([\s\S]*?)```/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const line = lineNumberAt(content, match.index);
    const parsed = tryParseJson(match[1]);
    if (parsed !== null) {
      blocks.push({ content: parsed, line });
    }
  }
  return blocks;
}

function extractJsBlocks(content) {
  const blocks = [];
  const regex = /```(?:javascript|js)\s*\n([\s\S]*?)```/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const line = lineNumberAt(content, match.index);
    blocks.push({ content: match[1], line });
  }
  return blocks;
}

/**
 * Extract tools from JSON-like structures by recursively scanning objects.
 *
 * @param {*} jsonValue
 * @param {number} line
 * @param {string} fileName
 * @param {Array} sections
 * @returns {Array<Object>}
 */
function extractToolsFromJsonBlock(jsonValue, line, fileName, sections, sourceContent = '') {
  const tools = [];
  walkJson(jsonValue, value => {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      return;
    }

    const toolName = inferToolNameFromJsonObject(value);
    if (!toolName) return;

    const action = getActionFromToolNameOrJson(toolName, value);
    const input = extractInputFromJsonObject(value);
    const output = inferOutputSignature(toolName, action);

    tools.push({
      name: toolName,
      canonical_name: toolName,
      action,
      type: 'tool_call',
      extraction_method: 'json_block',
      description: value.description || value.desc || '',
      input,
      output,
      location: {
        file: fileName,
        line,
        column: 0,
        section: findSectionForLine(sections, line)
      },
      source_context: buildToolSourceContext({
        content: sourceContent,
        fileName,
        line,
        section: findSectionForLine(sections, line),
        action,
        operationType: action,
        extractionMethod: 'json_block',
        trigger: toolName,
        actionSnippet: JSON.stringify(value).slice(0, 240),
        sourceType: 'markdown_json_block'
      })
    });
  });

  return tools;
}

function walkJson(value, visitor) {
  visitor(value);
  if (Array.isArray(value)) {
    for (const item of value) walkJson(item, visitor);
    return;
  }
  if (value && typeof value === 'object') {
    for (const v of Object.values(value)) walkJson(v, visitor);
  }
}

function inferToolNameFromJsonObject(json) {
  const candidates = [
    json.tool,
    json.tool_name,
    json.function,
    json.api,
    json.name
  ];

  for (const candidate of candidates) {
    const normalized = normalizeToolName(candidate);
    if (normalized) return normalized;
  }

  if (typeof json.action === 'string' && typeof json.module === 'string') {
    const normalized = normalizeToolName(`${json.module}.${json.action}`);
    if (normalized) return normalized;
  }

  return null;
}

function getActionFromToolNameOrJson(toolName, json = {}) {
  if (typeof json.action === 'string' && json.action.trim()) {
    return json.action.trim();
  }
  const parts = toolName.split('.');
  return parts[parts.length - 1] || 'unknown';
}

function extractInputFromJsonObject(json) {
  const ignored = new Set(['tool', 'tool_name', 'function', 'api', 'name', 'action', 'description', 'desc']);
  const input = {};
  for (const [key, value] of Object.entries(json)) {
    if (ignored.has(key)) continue;
    input[key] = {
      type: inferType(value),
      required: true,
      example: value
    };
  }
  return input;
}

function extractToolsFromCode(code, baseLine, fileName, sections, options = {}) {
  const tools = [];
  const sourceContent = options.sourceContent || code;
  const sourceType = options.sourceType || 'script';
  TOOL_CALL_REGEX.lastIndex = 0;

  let match;
  while ((match = TOOL_CALL_REGEX.exec(code)) !== null) {
    const toolName = normalizeToolName(match[1]);
    if (!toolName) continue;

    const line = baseLine + code.slice(0, match.index).split('\n').length - 1;
    const action = toolName.split('.').pop();
    const input = extractInputFromCall(code, match.index + match[0].length - 1);
    const output = inferOutputSignature(toolName, action);

    tools.push({
      name: toolName,
      canonical_name: toolName,
      action,
      type: 'tool_call',
      extraction_method: 'code_call',
      input,
      output,
      location: {
        file: fileName,
        line,
        column: columnNumberAt(code, match.index),
        section: findSectionForLine(sections, line)
      },
      source_context: buildToolSourceContext({
        content: sourceContent,
        fileName,
        line,
        column: columnNumberAt(code, match.index),
        section: findSectionForLine(sections, line),
        action,
        operationType: action,
        extractionMethod: 'code_call',
        trigger: match[0],
        actionSnippet: match[0],
        sourceType
      })
    });
  }

  return tools;
}

function extractToolsFromTables(content, fileName, sections) {
  const tools = [];
  const lines = content.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.includes('|')) continue;
    if (/^\s*\|?[-:\s|]+\|?\s*$/.test(line)) continue;
    if (isPlaceholderLine(line) || isTemplateOrExampleSection(sections, i + 1)) continue;

    TOOL_NAME_REGEX.lastIndex = 0;
    let match;
    while ((match = TOOL_NAME_REGEX.exec(line)) !== null) {
      const toolName = normalizeToolName(match[1]);
      if (!toolName) continue;

      const action = toolName.split('.').pop();
      tools.push({
        name: toolName,
        canonical_name: toolName,
        action,
        type: 'tool_call',
        extraction_method: 'table_ref',
        input: inferInputSignature(toolName, action),
        output: inferOutputSignature(toolName, action),
        location: {
          file: fileName,
          line: i + 1,
          column: match.index + 1,
          section: findSectionForLine(sections, i + 1)
        },
        source_context: buildToolSourceContext({
          content,
          fileName,
          line: i + 1,
          column: match.index + 1,
          section: findSectionForLine(sections, i + 1),
          action,
          operationType: action,
          extractionMethod: 'table_ref',
          trigger: match[0],
          actionSnippet: line.trim(),
          sourceType: 'markdown_table'
        })
      });
    }
  }

  return tools;
}

function extractToolsFromInline(content, fileName, sections) {
  const tools = [];
  const regex = /`([^`]+)`/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const candidate = normalizeToolName(match[1]);
    if (!candidate) continue;

    const line = lineNumberAt(content, match.index);
    if (isPlaceholderLine(lineAt(content, line)) || isTemplateOrExampleSection(sections, line)) continue;
    const action = candidate.split('.').pop();
    tools.push({
      name: candidate,
      canonical_name: candidate,
      action,
      type: 'tool_call',
      extraction_method: 'inline_ref',
      input: inferInputSignature(candidate, action),
      output: inferOutputSignature(candidate, action),
      location: {
        file: fileName,
        line,
        column: columnNumberAt(content, match.index),
        section: findSectionForLine(sections, line)
      },
      source_context: buildToolSourceContext({
        content,
        fileName,
        line,
        column: columnNumberAt(content, match.index),
        section: findSectionForLine(sections, line),
        action,
        operationType: action,
        extractionMethod: 'inline_ref',
        trigger: match[0],
        actionSnippet: match[0],
        sourceType: 'markdown_inline'
      })
    });
  }
  return tools;
}

function isTemplateOrExampleMarkdown(fileName = '', content = '') {
  const file = normalizePathForOutput(fileName).toLowerCase();
  if (/\b(template|example|sample|fixture)\b/.test(file)) return true;
  const firstLines = String(content || '').split(/\r?\n/).slice(0, 24).join('\n').toLowerCase();
  return /\b(template|example|sample)\b/.test(firstLines) &&
    /\b(placeholders?|replace|what it does|example output)\b/.test(firstLines);
}

function isTemplateOrExampleSection(sections = [], line = 0) {
  const title = String(findSectionForLine(sections, line) || '').toLowerCase();
  return /\b(template|example|sample|placeholder)\b/.test(title);
}

function isPlaceholderLine(line = '') {
  const text = String(line || '').toLowerCase();
  return /\[[^\]]*(what it does|description|purpose|tool|command|todo|replace)[^\]]*\]/.test(text) ||
    /\b(example|sample|template|placeholder)\b/.test(text);
}

/**
 * Extract tool calls from JS/TS files.
 *
 * @param {string} filePath
 * @returns {Array<Object>}
 */
function extractFromJsFile(filePath, options = {}) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return extractToolsFromCode(content, 1, normalizePathForOutput(filePath, options.rootDir), [], {
      sourceContent: content,
      sourceType: 'script'
    });
  } catch (error) {
    console.warn(`Warning: Could not read JS file: ${filePath}`);
    return [];
  }
}

function buildToolSourceContext({
  content,
  fileName,
  line,
  column = 0,
  section = '',
  action,
  operationType,
  extractionMethod,
  trigger,
  actionSnippet,
  sourceType
}) {
  return buildSourceContext({
    content,
    file: fileName,
    line,
    column,
    section,
    action,
    operationType,
    extractionMethod,
    trigger,
    actionSnippet,
    sourceType,
    grounded: Boolean(actionSnippet || trigger)
  });
}

function extractInputFromCall(code, openParenIndex) {
  const input = {};
  const objectLiteral = extractFirstObjectLiteralArg(code, openParenIndex);
  if (!objectLiteral) return input;

  const pairs = parseObjectLiteralPairs(objectLiteral);
  for (const pair of pairs) {
    input[pair.key] = {
      type: pair.type,
      required: true,
      example: pair.example
    };
  }
  return input;
}

function extractFirstObjectLiteralArg(code, openParenIndex) {
  let i = openParenIndex + 1;
  while (i < code.length && /\s/.test(code[i])) i++;
  if (code[i] !== '{') return null;

  let depth = 0;
  let inSingle = false;
  let inDouble = false;
  let inTemplate = false;
  let escaped = false;

  for (let start = i; i < code.length; i++) {
    const ch = code[i];

    if (escaped) {
      escaped = false;
      continue;
    }
    if (ch === '\\') {
      escaped = true;
      continue;
    }

    if (!inDouble && !inTemplate && ch === '\'' && !escaped) {
      inSingle = !inSingle;
      continue;
    }
    if (!inSingle && !inTemplate && ch === '"' && !escaped) {
      inDouble = !inDouble;
      continue;
    }
    if (!inSingle && !inDouble && ch === '`' && !escaped) {
      inTemplate = !inTemplate;
      continue;
    }
    if (inSingle || inDouble || inTemplate) continue;

    if (ch === '{') depth++;
    if (ch === '}') {
      depth--;
      if (depth === 0) {
        return code.slice(start, i + 1);
      }
    }
  }

  return null;
}

function parseObjectLiteralPairs(objectLiteral) {
  const inner = objectLiteral.replace(/^\{|\}$/g, '');
  const parts = splitTopLevel(inner, ',');
  const pairs = [];

  for (const part of parts) {
    const index = findTopLevelColon(part);
    if (index === -1) continue;

    const rawKey = part.slice(0, index).trim().replace(/^['"]|['"]$/g, '');
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(rawKey)) continue;

    const rawValue = part.slice(index + 1).trim();
    const normalized = normalizeExample(rawValue);
    pairs.push({
      key: rawKey,
      type: inferTypeFromCode(rawValue),
      example: normalized
    });
  }

  return pairs;
}

function splitTopLevel(value, separatorChar) {
  const result = [];
  let current = '';
  let depthParen = 0;
  let depthBrace = 0;
  let depthBracket = 0;
  let inSingle = false;
  let inDouble = false;
  let inTemplate = false;
  let escaped = false;

  for (let i = 0; i < value.length; i++) {
    const ch = value[i];

    if (escaped) {
      current += ch;
      escaped = false;
      continue;
    }
    if (ch === '\\') {
      current += ch;
      escaped = true;
      continue;
    }

    if (!inDouble && !inTemplate && ch === '\'' && !escaped) inSingle = !inSingle;
    else if (!inSingle && !inTemplate && ch === '"' && !escaped) inDouble = !inDouble;
    else if (!inSingle && !inDouble && ch === '`' && !escaped) inTemplate = !inTemplate;

    if (!inSingle && !inDouble && !inTemplate) {
      if (ch === '(') depthParen++;
      else if (ch === ')') depthParen--;
      else if (ch === '{') depthBrace++;
      else if (ch === '}') depthBrace--;
      else if (ch === '[') depthBracket++;
      else if (ch === ']') depthBracket--;

      if (ch === separatorChar && depthParen === 0 && depthBrace === 0 && depthBracket === 0) {
        result.push(current);
        current = '';
        continue;
      }
    }

    current += ch;
  }

  if (current.trim()) result.push(current);
  return result;
}

function findTopLevelColon(part) {
  let depthParen = 0;
  let depthBrace = 0;
  let depthBracket = 0;
  let inSingle = false;
  let inDouble = false;
  let inTemplate = false;
  let escaped = false;

  for (let i = 0; i < part.length; i++) {
    const ch = part[i];

    if (escaped) {
      escaped = false;
      continue;
    }
    if (ch === '\\') {
      escaped = true;
      continue;
    }

    if (!inDouble && !inTemplate && ch === '\'' && !escaped) inSingle = !inSingle;
    else if (!inSingle && !inTemplate && ch === '"' && !escaped) inDouble = !inDouble;
    else if (!inSingle && !inDouble && ch === '`' && !escaped) inTemplate = !inTemplate;

    if (inSingle || inDouble || inTemplate) continue;

    if (ch === '(') depthParen++;
    else if (ch === ')') depthParen--;
    else if (ch === '{') depthBrace++;
    else if (ch === '}') depthBrace--;
    else if (ch === '[') depthBracket++;
    else if (ch === ']') depthBracket--;
    else if (ch === ':' && depthParen === 0 && depthBrace === 0 && depthBracket === 0) {
      return i;
    }
  }

  return -1;
}

function normalizeToolName(candidate) {
  if (typeof candidate !== 'string') return null;
  const cleaned = candidate.trim().replace(/^`|`$/g, '');
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+$/.test(cleaned)) {
    return null;
  }

  const terminal = cleaned.split('.').pop();
  if (!terminal) return null;

  // Filter obvious markdown/file references.
  if (/\.(md|txt|json|yaml|yml)$/i.test(cleaned)) return null;
  return cleaned;
}

function deduplicateCallSites(tools) {
  const byCallSite = new Map();

  for (const tool of tools) {
    const canonicalName = normalizeToolName(tool.canonical_name || tool.name);
    const name = normalizeToolName(tool.name) || canonicalName;
    if (!name && !canonicalName) continue;
    if (name === 'llm.inference' || tool.type === 'builtin_call') {
      byCallSite.set(`builtin:${name}`, {
        ...tool,
        name,
        canonical_name: tool.canonical_name || name,
        type: tool.type || 'builtin_call',
        input: tool.input || {},
        output: tool.output || inferOutputSignature(name, tool.action || name.split('.').pop())
      });
      continue;
    }

    const normalized = {
      ...tool,
      name,
      canonical_name: canonicalName || name,
      type: tool.type || 'tool_call',
      input: tool.input || {},
      output: tool.output || inferOutputSignature(name, tool.action || name.split('.').pop())
    };
    const key = callSiteDuplicateKey(normalized);

    if (!byCallSite.has(key)) {
      byCallSite.set(key, normalized);
      continue;
    }

    const existing = byCallSite.get(key);
    byCallSite.set(key, mergeToolMetadata(existing, normalized));
  }

  return Array.from(byCallSite.values());
}

function deduplicateTools(tools) {
  return deduplicateCallSites(tools);
}

function mergeToolMetadata(a, b) {
  const mergedInput = { ...a.input, ...b.input };
  const mergedOutput = { ...a.output, ...b.output };

  const description = (b.description && b.description.length > a.description?.length) ? b.description : a.description;
  const location = preferLocation(a.location, b.location);

  return {
    ...a,
    ...b,
    description: description || '',
    input: mergedInput,
    output: mergedOutput,
    location,
    isCritical: a.isCritical || b.isCritical || false
  };
}

function assignCallSiteIdentity(tools) {
  const sorted = [...tools].sort(compareToolLocation);
  let callsiteIndex = 0;

  return sorted.map(tool => {
    if (tool.type === 'builtin_call' || tool.name === 'llm.inference') {
      return {
        ...tool,
        canonical_name: tool.canonical_name || tool.name
      };
    }

    callsiteIndex += 1;
    const canonicalName = normalizeToolName(tool.canonical_name || tool.name) || tool.name;
    const callsiteId = `call_${String(callsiteIndex).padStart(3, '0')}`;

    return {
      ...tool,
      name: `${canonicalName}#${callsiteId}`,
      canonical_name: canonicalName,
      callsite_id: callsiteId,
      callsite_order: callsiteIndex,
      callsite_role: 'tool_call'
    };
  });
}

function compareToolLocation(a, b) {
  const fileA = String(a.location?.file || '');
  const fileB = String(b.location?.file || '');
  if (fileA !== fileB) {
    if (fileA === 'SKILL.md') return -1;
    if (fileB === 'SKILL.md') return 1;
    if (fileA === 'README.md') return -1;
    if (fileB === 'README.md') return 1;
    return fileA.localeCompare(fileB);
  }

  const lineDelta = Number(a.location?.line || 0) - Number(b.location?.line || 0);
  if (lineDelta !== 0) return lineDelta;

  const columnDelta = Number(a.location?.column || 0) - Number(b.location?.column || 0);
  if (columnDelta !== 0) return columnDelta;

  return String(a.canonical_name || a.name || '').localeCompare(String(b.canonical_name || b.name || ''));
}

function callSiteDuplicateKey(tool) {
  return [
    tool.canonical_name || tool.name || '',
    tool.location?.file || '',
    Number(tool.location?.line || 0),
    Number(tool.location?.column || 0),
    tool.extraction_method || ''
  ].join('|');
}

function preferLocation(a = {}, b = {}) {
  if (!a.file) return b;
  if (!b.file) return a;
  if (a.file === 'SKILL.md' && b.file !== 'SKILL.md') return a;
  if (b.file === 'SKILL.md' && a.file !== 'SKILL.md') return b;
  return (a.line || Number.MAX_SAFE_INTEGER) <= (b.line || Number.MAX_SAFE_INTEGER) ? a : b;
}

function inferInputSignature(toolName, action) {
  const input = {};
  const lowerName = toolName.toLowerCase();
  const lowerAction = (action || '').toLowerCase();

  if (lowerName.includes('app') && !lowerAction.includes('create')) {
    input.app_token = { type: 'app_token', required: true };
  }
  if (lowerName.includes('table') && !lowerAction.includes('create')) {
    input.table_id = { type: 'table_id', required: true };
  }
  if (lowerAction.match(/create|update|write|insert|send|post/)) {
    input.payload = { type: 'object', required: true };
  }
  if (lowerAction.match(/get|list|search|query|fetch|read/)) {
    if (!Object.keys(input).length) {
      input.filter = { type: 'object', required: false };
    }
  }

  return input;
}

function inferOutputSignature(toolName, action) {
  const output = {};
  const lowerName = toolName.toLowerCase();
  const lowerAction = (action || '').toLowerCase();

  if (lowerAction.match(/get|read|fetch|query|find|retrieve/)) {
    output.data = { type: 'object' };
  }
  if (lowerAction.match(/list|search/)) {
    output.items = { type: 'array' };
  }
  if (lowerAction.match(/create|add|insert/)) {
    output.success = { type: 'boolean' };
    output.id = { type: 'string' };
  }
  if (lowerAction.match(/update|write|delete|remove|send|post|publish/)) {
    output.success = { type: 'boolean' };
  }

  if (lowerName.includes('app') && lowerAction.includes('create')) {
    output.app_token = { type: 'app_token' };
  }
  if (lowerName.includes('table') && lowerAction.includes('create')) {
    output.table_id = { type: 'table_id' };
  }
  if (lowerName.includes('record') && lowerAction.includes('create')) {
    output.record_id = { type: 'record_id' };
  }

  return output;
}

function inferType(value) {
  if (value === null) return 'object';
  if (Array.isArray(value)) return 'array';
  const t = typeof value;
  if (t === 'string' || t === 'number' || t === 'boolean' || t === 'object') return t;
  return 'string';
}

function inferTypeFromCode(value) {
  const v = value.trim();
  if (!v) return 'string';
  if (v.startsWith('"') || v.startsWith("'") || v.startsWith('`')) return 'string';
  if (/^(true|false)\b/.test(v)) return 'boolean';
  if (/^[+-]?\d+(\.\d+)?\b/.test(v)) return 'number';
  if (v.startsWith('{')) return 'object';
  if (v.startsWith('[')) return 'array';
  return 'string';
}

function normalizeExample(rawValue) {
  const trimmed = rawValue.trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  if (/^(true|false)$/.test(trimmed)) return trimmed === 'true';
  if (/^[+-]?\d+(\.\d+)?$/.test(trimmed)) return Number(trimmed);
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) return trimmed;
  return trimmed;
}

function tryParseJson(value) {
  try {
    return JSON.parse(value);
  } catch (error) {
    return null;
  }
}

function lineNumberAt(content, index) {
  return content.slice(0, index).split('\n').length;
}

function lineAt(content, line) {
  return String(content || '').split(/\r?\n/)[Math.max(0, Number(line || 1) - 1)] || '';
}

function columnNumberAt(content, index) {
  const previousNewline = content.lastIndexOf('\n', Math.max(0, index - 1));
  return index - previousNewline;
}

function normalizePathForOutput(filePath, rootDir = '') {
  const outputPath = rootDir && path.isAbsolute(filePath)
    ? path.relative(rootDir, filePath)
    : filePath;
  return outputPath.split(path.sep).join('/');
}

function isJavaScriptLikeFile(filePath) {
  return ['.js', '.mjs', '.cjs', '.ts', '.tsx'].includes(path.extname(String(filePath || '')).toLowerCase());
}

function findSectionForLine(sections, line) {
  for (const section of sections) {
    if (line >= section.startLine && line <= section.endLine) {
      return section.title;
    }
  }
  return null;
}

module.exports = {
  extractToolCalls,
  extractFromMarkdown,
  extractFromJsFile,
  deduplicateCallSites,
  deduplicateTools,
  inferOutputSignature,
  inferInputSignature,
  isJavaScriptLikeFile
};
