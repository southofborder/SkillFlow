#!/usr/bin/env node
/**
 * Babel AST sidecar for the Python FCG rewrite.
 *
 * The Python port owns ALL judgment (operation-type classification, noise
 * dropping), identity (node-name/file-slug construction) and node shape. The
 * ONE thing pure Python cannot faithfully reproduce is babel's AST for modern
 * JS/TS/JSX — so this sidecar does exactly that and nothing more: parse, walk,
 * and emit the raw structural facts (function/call names + source positions +
 * snippets) that `collectJavaScriptFunctions` / `collectJavaScriptCalls` in the
 * JS baseline extract. Everything downstream is rebuilt in Python.
 *
 * Protocol: read {content, relPath} as JSON on stdin, write
 * {functions:[...], calls:[...]} or {parseError:"..."} as JSON on stdout.
 *
 * The traverse / functionName / calleeName / propertyName / identifierName /
 * sourceForNode helpers below MIRROR script-flow-extractor.js:551-630,1252-1255
 * verbatim so AST-fact extraction is byte-identical to the JS pipeline. Only
 * @babel/parser is required (reused from the analyzer's node_modules during the
 * transition; the package will vendor its own later).
 */

const path = require('path');
const parser = require(resolveBabelParser());

function resolveBabelParser() {
  // During the JS→Python transition the analyzer package still ships babel.
  try {
    return require.resolve('@babel/parser');
  } catch (_) {
    return require.resolve(
      path.join(__dirname, '..', '..', '..', 'skill-fcg-analyzer', 'node_modules', '@babel', 'parser')
    );
  }
}

function jsParserPlugins(relPath) {
  const ext = path.extname(relPath).toLowerCase();
  const plugins = [
    'asyncGenerators', 'classProperties', 'classPrivateProperties', 'dynamicImport',
    'importMeta', 'objectRestSpread', 'optionalCatchBinding', 'optionalChaining', 'topLevelAwait'
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

function sourceForNode(content, node) {
  if (!node || typeof node.start !== 'number' || typeof node.end !== 'number') return '';
  return String(content || '').slice(node.start, node.end);
}

function extract(content, relPath) {
  let ast;
  try {
    ast = parser.parse(content, {
      sourceType: 'unambiguous',
      errorRecovery: true,
      plugins: jsParserPlugins(relPath)
    });
  } catch (error) {
    return { parseError: String(error && error.message || error) };
  }

  const functions = [];
  traverse(ast, {
    enter(node, parent) {
      const name = functionName(node, parent);
      if (!name) return;
      functions.push({
        name,
        line: node.loc?.start?.line || 1,
        column: node.loc?.start?.column || 0,
        start: node.start || 0,
        end: node.end || node.start || 0,
        snippet: sourceForNode(content, node)
      });
    }
  });

  const calls = [];
  traverse(ast, {
    enter(node) {
      if (node.type !== 'CallExpression' && node.type !== 'NewExpression') return;
      const callee = calleeName(node.callee);
      if (!callee) return;
      calls.push({
        callee,
        line: node.loc?.start?.line || 1,
        column: node.loc?.start?.column || 0,
        start: node.start || 0,
        end: node.end || node.start || 0,
        snippet: sourceForNode(content, node).slice(0, 500)
      });
    }
  });

  return { functions, calls };
}

let raw = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', chunk => { raw += chunk; });
process.stdin.on('end', () => {
  let out;
  try {
    const { content, relPath } = JSON.parse(raw);
    out = extract(String(content || ''), String(relPath || ''));
  } catch (error) {
    out = { parseError: `sidecar failure: ${String(error && error.message || error)}` };
  }
  process.stdout.write(JSON.stringify(out));
});
