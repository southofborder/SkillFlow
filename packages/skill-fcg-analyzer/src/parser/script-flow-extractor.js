const fs = require('fs');
const path = require('path');
const parser = require('@babel/parser');
const {
  normalizeAssistantContent,
  parseLooseJson,
  postJsonWithTimeout
} = require('../../../../shared/llm-utils.cjs');
const { buildSourceContext, normalizeSourcePath } = require('./document-context');
const { classifyShellCommandLine } = require('./shell-command-classifier');

const JS_EXTENSIONS = new Set(['.js', '.mjs', '.cjs', '.ts', '.tsx']);
const SHELL_EXTENSIONS = new Set(['.sh', '.bash']);
const SCRIPT_SEMANTIC_PROMPT_VERSION = 'fcg-script-runtime-semantic-v1';
const DEFAULT_SCRIPT_SEMANTIC_RETRIES = 2;

async function extractScriptFlow(scriptFiles = [], options = {}) {
  const nodes = [];
  const edges = [];
  const rootDir = options.rootDir || '';

  for (const filePath of scriptFiles || []) {
    const ext = path.extname(String(filePath || '')).toLowerCase();
    const relPath = normalizeSourcePath(rootDir, filePath);
    let flow = null;
    if (JS_EXTENSIONS.has(ext)) {
      flow = extractJavaScriptFlow(filePath, relPath);
    } else if (SHELL_EXTENSIONS.has(ext) || isShellScript(filePath)) {
      flow = await extractShellFlow(filePath, relPath, options);
    }
    if (!flow) continue;
    nodes.push(...flow.nodes);
    edges.push(...flow.edges);
  }

  return { nodes: dedupeByName(nodes), edges: dedupeEdges(edges) };
}

function extractJavaScriptFlow(filePath, relPath) {
  let content = '';
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (error) {
    console.warn(`Warning: Could not read script file: ${filePath}`);
    return null;
  }

  let ast = null;
  try {
    ast = parser.parse(content, {
      sourceType: 'unambiguous',
      errorRecovery: true,
      plugins: jsParserPlugins(relPath)
    });
  } catch (error) {
    console.warn(`Warning: Could not parse script file: ${relPath}: ${error.message}`);
    return fallbackScriptEntry(content, relPath, 'javascript_parse_error');
  }

  const fileSlug = stableSlug(relPath);
  const functions = collectJavaScriptFunctions(ast, content)
    .map(fn => ({ ...fn, nodeName: `script.function.${fileSlug}.l${fn.line}.${stableSlug(fn.name)}` }));
  const calls = collectJavaScriptCalls(ast, content, functions);
  const nodes = [createScriptEntryNode({ content, relPath, language: 'javascript', line: 1 })];
  const edges = [];

  for (const fn of functions) {
    nodes.push(createScriptFunctionNode({ content, relPath, language: 'javascript', fn }));
    edges.push(createScriptEdge(nodes[0].name, fn.nodeName, edges.length, 'script_declares_function'));
  }

  const ownerLastCall = new Map();
  for (const call of calls) {
    nodes.push(createScriptCallNode({ content, relPath, language: 'javascript', call }));
    const owner = call.ownerNodeName || nodes[0].name;
    edges.push(createScriptEdge(owner, call.nodeName, edges.length, 'script_invokes_call'));

    const prior = ownerLastCall.get(owner);
    if (prior) {
      edges.push(createScriptEdge(prior, call.nodeName, edges.length, 'script_call_sequence'));
    }
    ownerLastCall.set(owner, call.nodeName);
  }

  return { nodes, edges };
}

async function extractShellFlow(filePath, relPath, options = {}) {
  let content = '';
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (error) {
    console.warn(`Warning: Could not read shell file: ${filePath}`);
    return null;
  }

  const lines = content.split(/\r?\n/);
  const fileSlug = stableSlug(relPath);
  const functions = collectShellFunctions(lines, relPath)
    .map(fn => ({ ...fn, nodeName: `script.function.${fileSlug}.l${fn.line}.${stableSlug(fn.name)}` }));
  const runtimeBlocks = await refineShellSemanticBlocks(collectShellSemanticBlocks(lines, functions, relPath), options);
  const calls = [
    ...collectShellCommands(lines, functions, relPath),
    ...runtimeBlocks
  ].sort((a, b) => {
    if (a.line !== b.line) return a.line - b.line;
    return Number(a.semanticBlock ? 1 : 0) - Number(b.semanticBlock ? 1 : 0);
  });
  const nodes = [createScriptEntryNode({ content, relPath, language: 'shell', line: 1 })];
  const edges = [];

  for (const fn of functions) {
    nodes.push(createScriptFunctionNode({ content, relPath, language: 'shell', fn }));
    edges.push(createScriptEdge(nodes[0].name, fn.nodeName, edges.length, 'script_declares_function'));
  }

  const ownerLastCall = new Map();
  for (const call of calls) {
    nodes.push(createScriptCallNode({ content, relPath, language: 'shell', call }));
    const owner = call.ownerNodeName || nodes[0].name;
    edges.push(createScriptEdge(owner, call.nodeName, edges.length, 'script_invokes_command'));
    const prior = ownerLastCall.get(owner);
    if (prior) {
      edges.push(createScriptEdge(prior, call.nodeName, edges.length, 'script_command_sequence'));
    }
    ownerLastCall.set(owner, call.nodeName);
  }

  return { nodes, edges };
}

function collectJavaScriptFunctions(ast, content) {
  const functions = [];
  traverse(ast, {
    enter(node, parent) {
      const name = functionName(node, parent);
      if (!name) return;
      const line = node.loc?.start?.line || 1;
      const snippet = sourceForNode(content, node);
      const slug = stableSlug(name);
      const fileSlug = stableSlug('');
      functions.push({
        name,
        nodeName: '',
        line,
        column: node.loc?.start?.column || 0,
        start: node.start || 0,
        end: node.end || node.start || 0,
        snippet,
        operationType: inferOperationType(`${name}\n${snippet}`),
        target: name,
        fileSlug
      });
    }
  });

  return functions;
}

function collectJavaScriptCalls(ast, content, functions) {
  const calls = [];
  traverse(ast, {
    enter(node) {
      if (node.type !== 'CallExpression' && node.type !== 'NewExpression') return;
      const callee = calleeName(node.callee);
      if (!callee) return;
      const line = node.loc?.start?.line || 1;
      const owner = findOwnerFunction(node.start || 0, functions);
      const snippet = sourceForNode(content, node).slice(0, 500);
      const classification = classifyScriptCall(callee, snippet);
      // Defect (3) fix: drop pure language/runtime builtins so they never
      // become FCG nodes.
      if (classification.noise) return;
      calls.push({
        callee,
        line,
        column: node.loc?.start?.column || 0,
        snippet,
        operationType: classification.operationType,
        scriptRole: classification.role,
        ownerNodeName: owner?.nodeName || '',
        target: callee
      });
    }
  });

  return calls.map((call, index) => ({
    ...call,
    nodeName: `script.call.__FILE__.l${call.line}.c${index + 1}.${stableSlug(call.callee)}`
  }));
}

function collectShellFunctions(lines, relPath) {
  const functions = [];
  let active = null;
  let braceDepth = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = stripShellComment(line).trim();
    const fnMatch = trimmed.match(/^(?:function\s+)?([A-Za-z_][A-Za-z0-9_-]*)\s*(?:\(\))?\s*\{/);
    if (!active && fnMatch) {
      active = {
        name: fnMatch[1],
        line: i + 1,
        column: line.indexOf(fnMatch[1]),
        startLine: i + 1,
        endLine: i + 1,
        body: [line]
      };
      braceDepth = countChar(trimmed, '{') - countChar(trimmed, '}');
      if (braceDepth <= 0) {
        functions.push(finalizeShellFunction(active));
        active = null;
      }
      continue;
    }
    if (!active) continue;
    active.body.push(line);
    active.endLine = i + 1;
    braceDepth += countChar(trimmed, '{') - countChar(trimmed, '}');
    if (braceDepth <= 0) {
      functions.push(finalizeShellFunction(active));
      active = null;
    }
  }

  return functions.map(fn => ({
    ...fn,
    target: fn.name,
    operationType: inferOperationType(`${fn.name}\n${fn.snippet}`)
  }));
}

function collectShellCommands(lines, functions) {
  const calls = [];
  const heredocRanges = collectHeredocRanges(lines);
  for (let i = 0; i < lines.length; i++) {
    if (isLineInRanges(i + 1, heredocRanges, { includeStart: false, includeEnd: true })) continue;
    const raw = lines[i];
    const line = stripShellComment(raw).trim();
    if (!line || /^#!|^\}|^(?:then|do|fi|done|else|elif\b)/.test(line)) continue;
    if (/^(?:function\s+)?[A-Za-z_][A-Za-z0-9_-]*\s*(?:\(\))?\s*\{/.test(line)) continue;
    if (/^[A-Za-z_][A-Za-z0-9_]*=.*$/.test(line) && !/[|&;<>()]/.test(line)) continue;

    // Defect (3) fix: route through the shared shell classifier, which returns
    // nothing for echo/exit/set/shift, control terminators (esac/;;), case
    // patterns and bare assignments. Only security-relevant commands (network,
    // exec, file IO) survive as nodes — this is what collapsed self-improving's
    // shell scripts from hundreds of noise nodes.
    const classified = classifyShellCommandLine(line);
    if (!classified.length) continue;
    const owner = functions.find(fn => i + 1 > fn.startLine && i + 1 < fn.endLine);
    for (const cmd of classified) {
      calls.push({
        callee: cmd.command,
        line: i + 1,
        column: Math.max(0, raw.indexOf(cmd.command)),
        snippet: line.slice(0, 500),
        operationType: cmd.operationType,
        targets: cmd.targets && cmd.targets.length ? cmd.targets : undefined,
        ownerNodeName: owner?.nodeName || '',
        target: cmd.targets && cmd.targets[0] ? cmd.targets[0].value : cmd.command
      });
    }
  }

  return calls.map((call, index) => ({
    ...call,
    nodeName: `script.call.__FILE__.l${call.line}.c${index + 1}.${stableSlug(call.callee)}`
  }));
}

function collectShellSemanticBlocks(lines, functions, relPath) {
  const blocks = [
    ...collectHeredocBlocks(lines, functions),
    ...collectShellIfBlocks(lines, functions)
  ];
  return blocks.map((block, index) => ({
    callee: block.callee,
    line: block.line,
    column: block.column || 0,
    snippet: block.snippet,
    operationType: block.operationType,
    ownerNodeName: block.ownerNodeName || '',
    target: block.target || block.callee,
    semanticBlock: true,
    semanticGate: block.semanticGate,
    conditions: block.conditions || [],
    targets: block.targets || [],
    effects: block.effects || [],
    inputs: block.inputs || [],
    outputs: block.outputs || [],
    confidence: block.confidence,
    action: block.action,
    extractionMethod: block.extractionMethod,
    sourceRole: 'runtime_implementation',
    nodeName: `script.call.__FILE__.l${block.line}.csemantic${index + 1}.${stableSlug(block.callee || block.operationType || 'runtime_block')}`
  }));
}

function collectHeredocBlocks(lines, functions) {
  const blocks = [];
  const ranges = collectHeredocRanges(lines);
  for (const range of ranges) {
    const bodyLines = lines.slice(range.startLine, range.endLine - 1);
    const snippet = [lines[range.startLine - 1], ...bodyLines, lines[range.endLine - 1] || '']
      .filter(line => line !== undefined)
      .join('\n')
      .trim();
    const text = bodyLines.join('\n').trim();
    if (!text) continue;
    const owner = functions.find(fn => range.startLine > fn.startLine && range.startLine < fn.endLine);
    blocks.push({
      kind: 'heredoc',
      callee: inferHeredocCallee(text),
      line: range.startLine,
      column: Math.max(0, lines[range.startLine - 1].indexOf('cat')),
      snippet,
      text,
      operationType: 'write',
      action: 'write',
      ownerNodeName: owner?.nodeName || '',
      extractionMethod: 'script_flow_runtime_block'
    });
  }
  return blocks;
}

function collectShellIfBlocks(lines, functions) {
  const blocks = [];
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = stripShellComment(raw).trim();
    if (!/^(?:if|elif)\b/.test(line)) continue;
    const endLine = findShellBlockEnd(lines, i + 1, 'fi');
    const body = lines.slice(i, Math.max(i + 1, endLine)).join('\n').trim();
    const owner = functions.find(fn => i + 1 > fn.startLine && i + 1 < fn.endLine);
    blocks.push({
      kind: 'if',
      callee: 'shell.condition',
      line: i + 1,
      column: Math.max(0, raw.indexOf(line.replace(/^\s+/, ''))),
      snippet: body,
      text: body,
      operationType: 'guard',
      action: 'guard',
      ownerNodeName: owner?.nodeName || '',
      extractionMethod: 'script_flow_runtime_block'
    });
  }
  return blocks;
}

function createScriptEntryNode({ content, relPath, language, line }) {
  const fileSlug = stableSlug(relPath);
  const nodeName = `script.entry.${fileSlug}`;
  return {
    name: nodeName,
    action: 'run',
    type: 'custom_func',
    description: `Script entry for ${relPath}`,
    input: {
      environment: { type: 'object', required: false },
      arguments: { type: 'array', required: false }
    },
    output: {
      result: { type: 'object' }
    },
    location: { file: relPath, line, section: 'script entry' },
    ownerScript: relPath,
    operationType: 'invoke_tool',
    formal_semantics: buildScriptSemantics({
      operationType: 'invoke_tool',
      action: 'run',
      relPath,
      line,
      language,
      text: `Script entry for ${relPath}`,
      target: relPath
    }),
    source_context: buildScriptSourceContext({
      content,
      relPath,
      line,
      language,
      action: 'run',
      operationType: 'invoke_tool',
      snippet: firstNonEmptyLine(content) || relPath,
      trigger: 'script_entry',
      extractionMethod: 'script_flow_entry'
    }),
    excludeFromImplicitLlmEdge: true,
    semanticKind: 'script_entry'
  };
}

function createScriptFunctionNode({ content, relPath, language, fn }) {
  const name = fn.nodeName;
  const operationType = fn.operationType || 'transform';
  return {
    name,
    action: operationAction(operationType),
    type: 'custom_func',
    description: `Function ${fn.name} in ${relPath}`,
    input: { arguments: { type: 'object', required: false } },
    output: { result: { type: 'object' } },
    location: { file: relPath, line: fn.line, column: fn.column || 0, section: `function ${fn.name}` },
    ownerScript: relPath,
    functionName: fn.name,
    operationType,
    formal_semantics: buildScriptSemantics({
      operationType,
      action: operationAction(operationType),
      relPath,
      line: fn.line,
      language,
      text: fn.snippet || fn.name,
      target: fn.target || fn.name
    }),
    source_context: buildScriptSourceContext({
      content,
      relPath,
      line: fn.line,
      column: fn.column || 0,
      language,
      action: operationAction(operationType),
      operationType,
      snippet: firstLine(fn.snippet) || fn.name,
      trigger: fn.name,
      extractionMethod: 'script_flow_function'
    }),
    excludeFromImplicitLlmEdge: true,
    semanticKind: 'script_function'
  };
}

function createScriptCallNode({ content, relPath, language, call }) {
  const fileSlug = stableSlug(relPath);
  const name = call.nodeName.replace('__FILE__', fileSlug);
  call.nodeName = name;
  const operationType = call.operationType || 'invoke_tool';
  const action = call.action || operationAction(operationType);
  return {
    name,
    canonical_name: call.callee,
    action,
    type: 'custom_func',
    description: `Script call ${call.callee} in ${relPath}`,
    input: { context: { type: 'object', required: false } },
    output: { result: { type: 'object' } },
    location: { file: relPath, line: call.line, column: call.column || 0, section: 'script call' },
    ownerScript: relPath,
    callee: call.callee,
    operationType,
    formal_semantics: buildScriptSemantics({
      operationType,
      action,
      relPath,
      line: call.line,
      language,
      text: call.snippet || call.callee,
      target: call.target || call.callee,
      conditions: call.conditions || [],
      targets: call.targets || [],
      effects: call.effects || [],
      inputs: call.inputs || [],
      outputs: call.outputs || [],
      confidence: call.confidence
    }),
    source_context: buildScriptSourceContext({
      content,
      relPath,
      line: call.line,
      column: call.column || 0,
      language,
      action,
      operationType,
      snippet: call.snippet || call.callee,
      trigger: call.callee,
      extractionMethod: call.extractionMethod || 'script_flow_call',
      sourceRole: call.sourceRole || ''
    }),
    excludeFromImplicitLlmEdge: call.excludeFromImplicitLlmEdge ?? true,
    excludeFromTypeAnalysis: Boolean(call.excludeFromTypeAnalysis),
    excludeFromFlow: Boolean(call.excludeFromFlow),
    semantic_gate: call.semanticGate || undefined,
    semanticKind: 'script_call'
  };
}

function buildScriptSemantics({ operationType, action, relPath, line, language, text, target, conditions = [], targets = [], effects = [], inputs = [], outputs = [], confidence }) {
  const normalizedTargets = targets.length ? targets : [{ type: targetType(operationType, target), value: target, raw: target }];
  return {
    operation_type: operationType,
    actor: language === 'shell' ? 'shell' : 'runtime',
    inputs: inputs.length ? inputs : buildScriptInputs(operationType, target),
    outputs: outputs.length ? outputs : buildScriptOutputs(operationType, target),
    targets: normalizedTargets,
    conditions,
    effects: effects.length ? effects : operationEffects(operationType),
    confidence: typeof confidence === 'number' ? confidence : 0.82,
    evidence: {
      text,
      source_line: text,
      file: relPath,
      line,
      section: language,
      method: 'script_flow'
    },
    action
  };
}

function buildScriptSourceContext({ content, relPath, line, column = 0, language, action, operationType, snippet, trigger, extractionMethod, sourceRole = '' }) {
  return buildSourceContext({
    content,
    file: relPath,
    line,
    column,
    section: language,
    sourceText: lineAt(content, line) || snippet,
    action,
    operationType,
    actionSnippet: snippet,
    trigger,
    extractionMethod,
    sourceRole: sourceRole || (language === 'shell' ? 'runtime_implementation' : 'extraction_source'),
    sourceType: language === 'shell' ? 'shell_script' : 'script',
    grounded: Boolean(snippet)
  });
}

function createScriptEdge(source, target, index, reason) {
  return {
    id: `script_flow_${index + 1}`,
    source,
    target,
    type: 'control_flow',
    confidence: 0.86,
    validation_method: 'script_flow',
    data_flow: {
      from_param: 'context',
      to_param: 'context',
      data_type: 'object'
    },
    semantic_reason: reason
  };
}

function jsParserPlugins(relPath) {
  const ext = path.extname(relPath).toLowerCase();
  const plugins = [
    'asyncGenerators',
    'classProperties',
    'classPrivateProperties',
    'dynamicImport',
    'importMeta',
    'objectRestSpread',
    'optionalCatchBinding',
    'optionalChaining',
    'topLevelAwait'
  ];
  if (ext === '.ts' || ext === '.tsx') plugins.push('typescript');
  if (ext === '.tsx' || ext === '.jsx') plugins.push('jsx');
  return plugins;
}

function traverse(root, visitor, parent = null) {
  if (!root || typeof root !== 'object') return;
  if (visitor.enter) visitor.enter(root, parent);
  for (const key of Object.keys(root)) {
    if (key === 'loc' || key === 'start' || key === 'end') continue;
    const value = root[key];
    if (Array.isArray(value)) {
      for (const item of value) {
        if (item && typeof item.type === 'string') traverse(item, visitor, root);
      }
    } else if (value && typeof value.type === 'string') {
      traverse(value, visitor, root);
    }
  }
}

function functionName(node, parent) {
  if (!node || typeof node.type !== 'string') return '';
  if (node.type === 'FunctionDeclaration') return node.id?.name || '';
  if ((node.type === 'FunctionExpression' || node.type === 'ArrowFunctionExpression') && parent?.type === 'VariableDeclarator') {
    return identifierName(parent.id);
  }
  if ((node.type === 'FunctionExpression' || node.type === 'ArrowFunctionExpression') && parent?.type === 'AssignmentExpression') {
    return calleeName(parent.left);
  }
  if (node.type === 'ObjectMethod' || node.type === 'ClassMethod' || node.type === 'ClassPrivateMethod') {
    return propertyName(node.key);
  }
  return '';
}

function calleeName(callee) {
  if (!callee) return '';
  if (callee.type === 'Identifier') return callee.name || '';
  if (callee.type === 'ThisExpression') return 'this';
  if (callee.type === 'Super') return 'super';
  if (callee.type === 'PrivateName') return propertyName(callee.id);
  if (callee.type === 'StringLiteral' || callee.type === 'NumericLiteral') return String(callee.value);
  if (callee.type === 'MemberExpression' || callee.type === 'OptionalMemberExpression') {
    const object = calleeName(callee.object);
    const property = propertyName(callee.property);
    return [object, property].filter(Boolean).join('.');
  }
  if (callee.type === 'CallExpression') return calleeName(callee.callee);
  return '';
}

function identifierName(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name || '';
  if (node.type === 'ObjectPattern') return 'object_pattern';
  if (node.type === 'ArrayPattern') return 'array_pattern';
  return '';
}

function propertyName(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name || '';
  if (node.type === 'PrivateName') return propertyName(node.id);
  if (node.type === 'StringLiteral' || node.type === 'NumericLiteral') return String(node.value);
  return '';
}

function findOwnerFunction(position, functions) {
  return [...functions]
    .filter(fn => Number(fn.start || 0) <= position && position <= Number(fn.end || 0))
    .sort((a, b) => (Number(a.end || 0) - Number(a.start || 0)) - (Number(b.end || 0) - Number(b.start || 0)))[0] || null;
}

// Defect (3) fix: script-call whitelist. Pure language/runtime builtins carry
// no security-relevant data flow (a `.push` or `Array.isArray` is not a sink),
// yet one-node-per-call blew self-improving-agent up to 584 nodes. We classify
// each call into a taint role and drop `noise`. Unknown identifiers (likely the
// skill's own functions) are KEPT — we never guess a user function is noise.
//
// Matched against the LAST segment of a member expression callee (e.g. the
// `push` in `arr.push`), so `fs.push` would still be caught, but real IO
// like `fs.writeFileSync` / `res.json` is preserved by the sink/source lists.
const NOISE_CALL_METHODS = new Set([
  // Array / collection manipulation (no IO)
  'push', 'pop', 'shift', 'unshift', 'slice', 'splice', 'concat', 'flat', 'flatmap',
  'map', 'filter', 'reduce', 'reduceright', 'foreach', 'find', 'findindex', 'findlast',
  'some', 'every', 'includes', 'indexof', 'lastindexof', 'join', 'reverse', 'fill',
  'keys', 'values', 'entries', 'isarray', 'from', 'of',
  // String manipulation (no IO)
  'split', 'trim', 'trimstart', 'trimend', 'padstart', 'padend', 'tolowercase',
  'touppercase', 'replace', 'replaceall', 'substring', 'substr', 'charat', 'charcodeat',
  'startswith', 'endswith', 'match', 'matchall', 'repeat', 'normalize', 'tostring',
  'tofixed', 'toprecision',
  // Object / JSON in-memory (parse/stringify are transforms, not sinks)
  'assign', 'freeze', 'keys', 'values', 'entries', 'fromentries', 'hasownproperty',
  'getownpropertynames', 'defineproperty', 'create', 'getprototypeof',
  // Number / Math / type coercion
  'parseint', 'parsefloat', 'isnan', 'isfinite', 'abs', 'floor', 'ceil', 'round',
  'min', 'max', 'random', 'pow', 'sqrt', 'boolean', 'number', 'string', 'symbol',
  // Promise / control (no external effect on their own)
  'then', 'catch', 'finally', 'resolve', 'reject', 'all', 'allsettled', 'race',
  // Timers / no-op logging
  'settimeout', 'setinterval', 'cleartimeout', 'clearinterval', 'now'
]);

const NOISE_CALL_FULL = new Set([
  'console.log', 'console.error', 'console.warn', 'console.info', 'console.debug',
  'array.isarray', 'array.from', 'array.of', 'object.assign', 'object.keys',
  'object.values', 'object.entries', 'object.freeze', 'object.create',
  'json.stringify', 'math.floor', 'math.ceil', 'math.round', 'math.max', 'math.min',
  'math.abs', 'math.random', 'date.now', 'number.parseint', 'number.parsefloat',
  'process.exit', 'this', 'super'
]);

// Constructor names that are pure runtime values, not effects.
const NOISE_CONSTRUCTORS = new Set([
  'error', 'typeerror', 'rangeerror', 'syntaxerror', 'referenceerror',
  'map', 'set', 'weakmap', 'weakset', 'array', 'object', 'date', 'regexp',
  'promise', 'string', 'number', 'boolean'
]);

/**
 * Decide whether a script call is security-relevant or pure noise.
 * @param {string} callee - dotted callee name, e.g. "fs.writeFileSync" or "arr.push"
 * @param {string} snippet - source text of the call
 * @returns {{role: string, operationType: string, noise: boolean}}
 */
function classifyScriptCall(callee, snippet = '') {
  const full = String(callee || '').toLowerCase();
  const last = full.split('.').pop() || full;
  const text = `${full} ${String(snippet || '')}`.toLowerCase();

  // Sinks / sources / exec take priority — never treat these as noise even if
  // a method name collides with the noise list.
  if (/\b(fetch|axios|got|superagent|node-fetch)\b/.test(full) ||
      /\b(http|https)\.(request|get|post)\b/.test(full) ||
      /\.(post|put|patch|upload|send|sendmessage|publish)\b/.test(full) && /\b(url|http|api|webhook|endpoint|client|axios|request)\b/.test(text)) {
    return { role: 'sink', operationType: 'external_egress', noise: false };
  }
  if (/\b(exec|execsync|spawn|spawnsync|execfile|execfilesync|fork)\b/.test(full) ||
      /child_process/.test(text)) {
    return { role: 'sink', operationType: 'invoke_tool', noise: false };
  }
  if (/\b(writefile|writefilesync|appendfile|appendfilesync|createwritestream|mkdir|mkdirsync|rmsync|unlinksync|copyfile|rename)\b/.test(full)) {
    return { role: 'sink', operationType: 'write', noise: false };
  }
  if (/\b(readfile|readfilesync|createreadstream|readdir|readdirsync)\b/.test(full) ||
      /process\.env/.test(text) || /\bargv\b/.test(full)) {
    return { role: 'source', operationType: 'read', noise: false };
  }
  if (/\b(redact|mask|sanitize|scrub|encrypt|hash|escape)\b/.test(full)) {
    return { role: 'sanitizer', operationType: 'transform', noise: false };
  }
  if (last === 'parse' && /json/.test(full)) {
    return { role: 'propagator', operationType: 'transform', noise: false };
  }

  // Noise: pure language/runtime builtins with no IO.
  if (NOISE_CALL_FULL.has(full)) return { role: 'noise', operationType: 'noise', noise: true };
  if (NOISE_CONSTRUCTORS.has(full)) return { role: 'noise', operationType: 'noise', noise: true };
  if (NOISE_CALL_METHODS.has(last) && !full.includes('fs.') && !/\b(client|api|db|store|repo)\b/.test(full)) {
    return { role: 'noise', operationType: 'noise', noise: true };
  }

  // Unknown — likely a user-defined function. Keep it; let the operation-type
  // inference and downstream LLM gate decide. Never drop on a name guess.
  return { role: 'unknown', operationType: inferOperationType(text), noise: false };
}

function inferOperationType(text) {
  const value = String(text || '').toLowerCase();
  if (/\b(fetch|axios|http\.request|https\.request|request|curl|wget|webhook|post|upload)\b/.test(value)) return 'external_egress';
  if (/\b(exec|execsync|spawn|spawnsync|execfile|child_process|bash|sh|powershell|cmd\.exe)\b/.test(value)) return 'invoke_tool';
  if (/\b(readfilesync|readfile|createreadstream|cat|grep|sed|awk|head|tail)\b/.test(value)) return 'read';
  if (/\b(writefilesync|writefile|appendfile|createwritestream|echo\b.*>|tee|touch|mkdir|cp|mv)\b/.test(value)) return 'write';
  if (/\b(json\.parse|map|filter|reduce|sort|split|join|replace|parse|extract|transform|sanitize|redact)\b/.test(value)) return 'transform';
  if (/\b(if|case|test|\[\[|\bdecide|validate|ensure|check)\b/.test(value)) return 'verify';
  return 'invoke_tool';
}

function operationAction(operationType) {
  if (operationType === 'context') return 'context';
  if (operationType === 'condition') return 'condition';
  if (operationType === 'read') return 'read';
  if (operationType === 'write') return 'write';
  if (operationType === 'transform') return 'transform';
  if (operationType === 'verify') return 'verify';
  if (operationType === 'guard') return 'guard';
  return 'run';
}

function operationEffects(operationType) {
  if (operationType === 'context') return [];
  if (operationType === 'read') return ['read_context'];
  if (operationType === 'write') return ['persist_state'];
  if (operationType === 'transform') return ['summarize'];
  if (operationType === 'external_egress') return ['network_egress'];
  if (operationType === 'verify') return ['validate'];
  if (operationType === 'guard') return ['validate', 'branch'];
  return ['call_tool'];
}

function buildScriptInputs(operationType, target) {
  if (operationType === 'context') return [];
  if (operationType === 'read') return [{ name: target, type: targetType(operationType, target) }];
  return [{ name: 'context', type: 'object' }];
}

function buildScriptOutputs(operationType, target) {
  if (operationType === 'context') return [];
  if (operationType === 'write' || operationType === 'external_egress' || operationType === 'invoke_tool') {
    return [{ name: 'result', type: 'object' }];
  }
  if (operationType === 'read') return [{ name: 'content', type: 'string' }];
  return [{ name: target || 'result', type: 'object' }];
}

function targetType(operationType, target = '') {
  const value = String(target || '').toLowerCase();
  if (operationType === 'external_egress' || /\b(fetch|http|curl|wget|webhook|api)\b/.test(value)) return 'external';
  if (/\b(env|process\.env)\b/.test(value)) return 'object';
  if (/\b(file|path|fs\.|\.md|\.json|\.txt|\.log)\b/.test(value)) return 'file';
  if (operationType === 'invoke_tool') return 'command';
  return 'object';
}

async function refineShellSemanticBlocks(blocks = [], options = {}) {
  if (!blocks.length) return [];
  if (options.semanticLlm === false || options.disableLlm) {
    return blocks.map(block => applyShellSemanticRefinement(block, null, false));
  }
  if (typeof options.scriptSemanticRefiner === 'function') {
    return Promise.all(blocks.map(async block => {
      try {
        const raw = await options.scriptSemanticRefiner(buildShellRuntimeCandidate(block));
        return applyShellSemanticRefinement(block, raw, true);
      } catch (error) {
        return applyShellSemanticError(block, error);
      }
    }));
  }
  if (typeof options.scriptSemanticBatchRefiner === 'function') {
    const candidates = blocks.map(buildShellRuntimeCandidate);
    try {
      const raw = await options.scriptSemanticBatchRefiner(candidates);
      const byId = normalizeShellBatchResult(raw);
      return blocks.map(block => {
        const candidate = buildShellRuntimeCandidate(block);
        const verdict = byId.get(candidate.id);
        return verdict
          ? applyShellSemanticRefinement(block, verdict, true)
          : applyShellSemanticError(block, new Error(`Missing shell semantic result for ${candidate.id}`));
      });
    } catch (error) {
      return blocks.map(block => applyShellSemanticError(block, error));
    }
  }
  const apiKey = String(options.llmApiKey || process.env.LLM_API_KEY || '').trim();
  if (!apiKey) return blocks.map(block => applyShellSemanticRefinement(block, null, false));
  return resolveShellSemanticBlocksWithRetry(blocks, { ...options, llmApiKey: apiKey });
}

async function resolveShellSemanticBlocksWithRetry(blocks = [], options = {}) {
  try {
    const raw = await callShellSemanticModelWithRetry(blocks.map(buildShellRuntimeCandidate), options);
    const byId = normalizeShellBatchResult(raw);
    return blocks.map(block => {
      const candidate = buildShellRuntimeCandidate(block);
      const verdict = byId.get(candidate.id);
      return verdict
        ? applyShellSemanticRefinement(block, verdict, true)
        : applyShellSemanticError(block, new Error(`Missing shell semantic result for ${candidate.id}`));
    });
  } catch (error) {
    if (blocks.length <= 1) {
      return blocks.map(block => applyShellSemanticError(block, error));
    }
    const midpoint = Math.ceil(blocks.length / 2);
    const left = await resolveShellSemanticBlocksWithRetry(blocks.slice(0, midpoint), options);
    const right = await resolveShellSemanticBlocksWithRetry(blocks.slice(midpoint), options);
    return [...left, ...right];
  }
}

async function callShellSemanticModelWithRetry(candidates, options = {}) {
  const attempts = Math.max(1, Number(options.scriptSemanticRetries || DEFAULT_SCRIPT_SEMANTIC_RETRIES) || DEFAULT_SCRIPT_SEMANTIC_RETRIES);
  let lastError = null;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await callShellSemanticModel(candidates, options);
    } catch (error) {
      lastError = error;
      if (attempt < attempts) await sleep(250 * attempt);
    }
  }
  throw lastError || new Error('Shell semantic LLM request failed');
}

function applyShellSemanticRefinement(block, rawVerdict = null, llmAttempted = false) {
  const candidate = buildShellRuntimeCandidate(block);
  const verdict = normalizeShellSemanticVerdict(rawVerdict) || inferShellSemanticVerdict(candidate);
  const actionability = verdict.actionability === 'context_only' ? 'context_only' : 'runtime_action';
  const operationType = actionability === 'context_only'
    ? 'context'
    : (normalizeRuntimeOperationType(verdict.operation_type) || block.operationType || 'guard');
  const action = actionability === 'context_only' ? 'context' : operationAction(operationType);
  const classification = normalizeRuntimeClassification(verdict.classification);
  const normalizedClassification = classification ||
    (actionability === 'context_only' ? 'context_only' : (operationType === 'guard' ? 'condition' : 'emit_reminder'));
  const targets = normalizeRuntimeTargets(verdict.targets);
  const conditions = normalizeRuntimeConditions(verdict.conditions);
  const effects = normalizeRuntimeEffects(verdict.effects);
  const confidence = Number.isFinite(Number(verdict.confidence)) ? clamp(Number(verdict.confidence), 0, 1) : 0.68;

  return {
    ...block,
    operationType,
    action,
    target: targets[0]?.value || block.target || block.callee,
    targets,
    conditions,
    effects,
    inputs: buildRuntimeBlockInputs(operationType, conditions, candidate),
    outputs: buildRuntimeBlockOutputs(operationType, targets),
    confidence,
    excludeFromFlow: actionability === 'context_only',
    excludeFromTypeAnalysis: actionability === 'context_only',
    excludeFromImplicitLlmEdge: actionability === 'context_only',
    semanticGate: {
      classification: normalizedClassification,
      actionability,
      grammar: verdict.grammar || candidate.syntax,
      completed_sentence: verdict.completed_sentence || '',
      reason: verdict.reason || 'Shell runtime block semantic candidate',
      confidence,
      method: rawVerdict ? 'script_semantic_llm_gate' : 'script_rule_candidate_gate',
      ...(llmAttempted && !rawVerdict ? { requires_review: true } : {})
    }
  };
}

function applyShellSemanticError(block, error) {
  const reason = String(error?.message || error || 'Shell semantic LLM gate failed').slice(0, 500);
  return {
    ...block,
    operationType: 'context',
    action: 'context',
    target: block.target || block.callee,
    targets: [],
    conditions: [],
    effects: [],
    inputs: [],
    outputs: [],
    confidence: 0.25,
    excludeFromFlow: true,
    excludeFromTypeAnalysis: true,
    excludeFromImplicitLlmEdge: true,
    semanticGate: {
      classification: 'context_only',
      actionability: 'context_only',
      grammar: block.kind === 'if' ? 'shell conditional block' : 'shell output block',
      completed_sentence: '',
      reason,
      confidence: 0.25,
      method: 'script_semantic_llm_error',
      requires_review: true
    }
  };
}

async function callShellSemanticModel(candidates, options) {
  const endpoint = resolveScriptSemanticLlmEndpoint(options);
  const model = options.llmModel || process.env.LLM_MODEL || 'gpt-5.5';
  const payload = await postJsonWithTimeout(endpoint, {
    model,
    temperature: 0,
    messages: [
      {
        role: 'system',
        content: [
          'You classify shell runtime implementation blocks for FCG.',
          'Return strict JSON only: {"results":[...]} with one result per candidate id.',
          'Classify actual runtime semantics: condition, guard, emit_reminder, route_to_file, write_artifact, read_env, external_call, context_only.',
          'Analyze shell syntax and the emitted natural-language text together.',
          'For heredoc/echo reminders, identify conditions, route targets, receivers, and whether the block emits a reminder rather than executing the suggested action.',
          'Do not invent routes from comments, headings, templates, or examples.',
          'Each runtime_action must be grounded in the candidate source span.'
        ].join(' ')
      },
      {
        role: 'user',
        content: JSON.stringify({
          prompt_version: SCRIPT_SEMANTIC_PROMPT_VERSION,
          output_schema: {
            results: [{
              id: 'candidate id',
              classification: 'condition|guard|emit_reminder|route_to_file|write_artifact|read_env|external_call|context_only',
              actionability: 'runtime_action|context_only',
              grammar: 'shell syntax and English grammar summary',
              completed_sentence: 'normalized sentence',
              operation_type: 'condition|guard|write|read|transform|invoke_tool|external_egress|verify|produce_artifact',
              targets: [{ type: 'file|artifact|object|external|command', value: '...', raw: '...' }],
              conditions: [{ type: '...', text: '...' }],
              effects: ['validate|branch|persist_state|read_context|call_tool|network_egress|summarize'],
              confidence: 0.0,
              reason: 'short grounded reason'
            }]
          },
          candidates
        })
      }
    ]
  }, {
    timeoutMs: Number(options.llmTimeout || 180000),
    headers: { Authorization: `Bearer ${options.llmApiKey}` }
  });
  return normalizeAssistantContent(payload?.choices?.[0]?.message?.content);
}

function resolveScriptSemanticLlmEndpoint(options = {}) {
  if (options.llmEndpoint || process.env.LLM_ENDPOINT) return options.llmEndpoint || process.env.LLM_ENDPOINT;
  const provider = String(options.llmProvider || process.env.LLM_PROVIDER || 'openai').toLowerCase();
  if (provider === 'dashscope') {
    return process.env.DASHSCOPE_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
  }
  return 'https://api.openai.com/v1/chat/completions';
}

function normalizeShellBatchResult(raw) {
  const parsed = parseLooseJson(raw);
  const results = Array.isArray(parsed?.results) ? parsed.results : (Array.isArray(parsed) ? parsed : []);
  const byId = new Map();
  for (const result of results) {
    const id = String(result?.id || '').trim();
    if (id) byId.set(id, result);
  }
  return byId;
}

function buildShellRuntimeCandidate(block) {
  return {
    id: `shell:${block.line}:${block.kind}`,
    kind: block.kind,
    line: block.line,
    syntax: block.kind === 'if' ? 'shell conditional block' : 'shell heredoc/output block',
    source: block.snippet || block.text || '',
    output_text: block.kind === 'heredoc' ? block.text || '' : '',
    condition_text: block.kind === 'if' ? firstLine(block.text || '') : '',
    prompt: [
      'Classify this shell runtime block for FCG.',
      'Return JSON: classification, actionability, grammar, completed_sentence, operation_type, targets, conditions, effects, confidence, reason.',
      'Allowed classification: condition, guard, emit_reminder, route_to_file, write_artifact, read_env, external_call, context_only.',
      'Only runtime actions should be actionability=runtime_action.'
    ].join(' ')
  };
}

function normalizeShellSemanticVerdict(raw) {
  if (!raw) return null;
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }
  return typeof raw === 'object' ? raw : null;
}

function inferShellSemanticVerdict(candidate = {}) {
  const text = `${candidate.source || ''}\n${candidate.output_text || ''}`;
  const lower = text.toLowerCase();
  const targets = [];
  for (const file of text.match(/(?:^|[\s`'"])([./~A-Za-z0-9_-]+(?:\/[A-Za-z0-9_.-]+)*\.md)\b/g) || []) {
    const value = file.replace(/^['"`\s]+/, '').trim();
    targets.push({ type: 'file', value, raw: value });
  }
  if (/skill extraction|extract.*skill|consider skill extraction/.test(lower)) {
    targets.push({ type: 'artifact', value: 'skill_extraction', raw: 'skill extraction' });
  }
  const conditions = [];
  if (/contains_error/.test(lower)) {
    conditions.push({ type: 'error_detected', text: 'contains_error is true' });
  }
  if (/\bif yes\b/.test(lower)) {
    conditions.push({ type: 'affirmative_learning_candidate', text: 'If yes' });
  }
  if (/high-value|recurring|broadly applicable/.test(lower)) {
    conditions.push({ type: 'high_value_learning', text: 'high-value, recurring, or broadly applicable' });
  }
  if (/claude_tool_output/.test(lower)) {
    targets.push({ type: 'object', value: 'CLAUDE_TOOL_OUTPUT', raw: 'CLAUDE_TOOL_OUTPUT' });
  }
  const operationType = candidate.kind === 'if' || conditions.length ? 'guard' : 'write';
  return {
    classification: /<[^>]+>|reminder|detected|consider logging|log to|consider skill extraction/.test(lower)
      ? 'emit_reminder'
      : (candidate.kind === 'if' ? 'condition' : 'context_only'),
    actionability: /<[^>]+>|reminder|detected|consider logging|log to|consider skill extraction|contains_error/.test(lower)
      ? 'runtime_action'
      : 'context_only',
    grammar: candidate.syntax,
    operation_type: operationType,
    targets,
    conditions,
    effects: operationType === 'guard' ? ['validate', 'branch'] : ['persist_state'],
    confidence: 0.62,
    reason: 'Rule candidate for shell runtime block; LLM semantic gate can refine this.'
  };
}

function normalizeRuntimeOperationType(value) {
  const text = String(value || '').trim();
  return ['condition', 'guard', 'write', 'read', 'transform', 'invoke_tool', 'external_egress', 'verify', 'produce_artifact', 'context'].includes(text)
    ? text
    : '';
}

function normalizeRuntimeClassification(value) {
  const text = String(value || '').trim();
  return ['condition', 'guard', 'emit_reminder', 'route_to_file', 'write_artifact', 'read_env', 'external_call', 'context_only'].includes(text)
    ? text
    : '';
}

function normalizeRuntimeTargets(targets = []) {
  return dedupeObjects((Array.isArray(targets) ? targets : [])
    .map(target => {
      if (!target || typeof target !== 'object') return null;
      const type = String(target.type || '').trim() || 'object';
      const value = String(target.value || '').trim();
      if (!value) return null;
      return { type, value, raw: String(target.raw || value) };
    })
    .filter(Boolean), item => `${item.type}:${item.value}`);
}

function normalizeRuntimeConditions(conditions = []) {
  return dedupeObjects((Array.isArray(conditions) ? conditions : [])
    .map(condition => {
      if (!condition || typeof condition !== 'object') return null;
      const text = String(condition.text || '').trim();
      if (!text) return null;
      return { type: String(condition.type || 'condition').trim() || 'condition', text };
    })
    .filter(Boolean), item => `${item.type}:${item.text}`);
}

function normalizeRuntimeEffects(effects = []) {
  const allowed = new Set(['read_context', 'persist_state', 'call_tool', 'update_memory', 'summarize', 'validate', 'branch', 'network_egress']);
  return Array.from(new Set((Array.isArray(effects) ? effects : [])
    .map(effect => String(effect || '').trim())
    .filter(effect => allowed.has(effect))));
}

function buildRuntimeBlockInputs(operationType, conditions, candidate) {
  if (operationType === 'context') return [];
  const inputs = [];
  if ((conditions || []).length) inputs.push({ name: 'condition_signal', type: 'condition' });
  if (/CLAUDE_TOOL_OUTPUT/i.test(candidate.source || '')) inputs.push({ name: 'CLAUDE_TOOL_OUTPUT', type: 'env' });
  if (!inputs.length && ['guard', 'verify', 'write', 'transform'].includes(operationType)) {
    inputs.push({ name: 'runtime_context', type: 'context' });
  }
  return inputs;
}

function buildRuntimeBlockOutputs(operationType, targets) {
  if (operationType === 'context') return [];
  if (operationType === 'guard' || operationType === 'condition') return [{ name: 'branch_state', type: 'object' }];
  if ((targets || []).length) return targets.map(target => ({ name: target.value, type: target.type || 'object' }));
  return [{ name: 'runtime_output', type: 'string' }];
}

function collectHeredocRanges(lines) {
  const ranges = [];
  for (let i = 0; i < lines.length; i++) {
    const line = String(lines[i] || '');
    const match = line.match(/<<\s*['"]?([A-Za-z_][A-Za-z0-9_]*)['"]?/);
    if (!match) continue;
    const marker = match[1];
    let endLine = i + 1;
    for (let j = i + 1; j < lines.length; j++) {
      if (String(lines[j] || '').trim() === marker) {
        endLine = j + 1;
        break;
      }
    }
    ranges.push({ startLine: i + 1, endLine });
    i = Math.max(i, endLine - 1);
  }
  return ranges;
}

function isLineInRanges(line, ranges, options = {}) {
  return (ranges || []).some(range => {
    const start = options.includeStart === false ? range.startLine + 1 : range.startLine;
    const end = options.includeEnd === false ? range.endLine - 1 : range.endLine;
    return line >= start && line <= end;
  });
}

function findShellBlockEnd(lines, startLine, terminal) {
  for (let i = startLine; i < lines.length; i++) {
    if (String(lines[i] || '').trim() === terminal) return i + 1;
  }
  return Math.min(lines.length, startLine + 1);
}

function inferHeredocCallee(text) {
  const lower = String(text || '').toLowerCase();
  if (lower.includes('error-detected')) return 'shell.emit_error_reminder';
  if (lower.includes('self-improvement-reminder')) return 'shell.emit_self_improvement_reminder';
  return 'shell.emit_heredoc';
}

function dedupeObjects(items, keyFn) {
  const seen = new Set();
  const result = [];
  for (const item of items || []) {
    const key = keyFn(item);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    result.push(item);
  }
  return result;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function fallbackScriptEntry(content, relPath, method) {
  const node = createScriptEntryNode({ content, relPath, language: 'script', line: 1 });
  node.formal_semantics.confidence = 0.35;
  node.formal_semantics.evidence.method = method;
  node.source_context.action_evidence.requires_review = true;
  return { nodes: [node], edges: [] };
}

function finalizeShellFunction(active) {
  const snippet = (active.body || []).join('\n').slice(0, 800);
  return {
    name: active.name,
    line: active.line,
    column: active.column,
    startLine: active.startLine,
    endLine: active.endLine,
    snippet
  };
}

function firstShellCommand(line) {
  const normalized = String(line || '')
    .replace(/^(?:if|then|do|while|until|for)\s+/, '')
    .trim();
  const parts = normalized.split(/\s+/);
  if (!parts.length) return '';
  const command = parts[0].replace(/^(?:sudo|command|builtin)$/, parts[1] || parts[0]);
  return command.replace(/['"]/g, '');
}

function stripShellComment(line) {
  const value = String(line || '');
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < value.length; i++) {
    const ch = value[i];
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    if (ch === '"' && !inSingle) inDouble = !inDouble;
    if (ch === '#' && !inSingle && !inDouble) return value.slice(0, i);
  }
  return value;
}

function isShellScript(filePath) {
  try {
    const firstLine = fs.readFileSync(filePath, 'utf-8').split(/\r?\n/, 1)[0] || '';
    return /^#!.*\b(?:bash|sh)\b/.test(firstLine);
  } catch (_) {
    return false;
  }
}

function sourceForNode(content, node) {
  if (!node || typeof node.start !== 'number' || typeof node.end !== 'number') return '';
  return String(content || '').slice(node.start, node.end);
}

function firstNonEmptyLine(content) {
  return String(content || '').split(/\r?\n/).map(line => line.trim()).find(Boolean) || '';
}

function firstLine(value) {
  return String(value || '').split(/\r?\n/, 1)[0].trim();
}

function lineAt(content, line) {
  return String(content || '').split(/\r?\n/)[Math.max(0, Number(line || 1) - 1)] || '';
}

function countChar(value, char) {
  return (String(value || '').match(new RegExp(`\\${char}`, 'g')) || []).length;
}

function stableSlug(value) {
  const text = String(value || 'script');
  const slug = text
    .replace(/\\/g, '/')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
  return slug || 'script';
}

function dedupeByName(nodes) {
  const seen = new Set();
  const result = [];
  for (const node of nodes || []) {
    const key = node.name || '';
    if (!key || seen.has(key)) continue;
    seen.add(key);
    result.push(node);
  }
  return result;
}

function dedupeEdges(edges) {
  const seen = new Set();
  const result = [];
  for (const edge of edges || []) {
    const key = `${edge.source}->${edge.target}:${edge.semantic_reason || edge.type}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push({ ...edge, id: `script_flow_${result.length + 1}` });
  }
  return result;
}

module.exports = {
  extractScriptFlow
};
