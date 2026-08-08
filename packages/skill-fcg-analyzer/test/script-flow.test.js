const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { SkillFCGAnalyzer } = require('../src/index');
const { findExecutableFiles } = require('../src/parser/skill-parser');
const { extractScriptFlow } = require('../src/parser/script-flow-extractor');

test('executable discovery and script flow cover JS, TS, and shell functions', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-script-flow-'));
  try {
    fs.mkdirSync(path.join(tempDir, 'hooks'), { recursive: true });
    fs.mkdirSync(path.join(tempDir, 'scripts'), { recursive: true });
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: script-flow-skill
description: Test script source extraction.
version: 0.1.0
---

Use the bundled scripts.
`,
      'utf-8'
    );
    fs.writeFileSync(
      path.join(tempDir, 'hooks', 'handler.js'),
      'function injectReminder(event) { return event.context.bootstrapFiles.filter(Boolean); }\nmodule.exports = { injectReminder };\n',
      'utf-8'
    );
    fs.writeFileSync(
      path.join(tempDir, 'hooks', 'handler.ts'),
      'export function normalizeEvent(event: { path: string }) { return fetch(event.path); }\n',
      'utf-8'
    );
    fs.writeFileSync(
      path.join(tempDir, 'scripts', 'activator.sh'),
      '#!/usr/bin/env bash\nactivate_skill() {\n  cat "$1"\n  curl -s https://example.com/hook\n}\nactivate_skill "$1"\n',
      'utf-8'
    );

    const executableFiles = findExecutableFiles(tempDir);
    assert.equal(executableFiles.length, 3);

    const scriptFlow = await extractScriptFlow(executableFiles, { rootDir: tempDir, semanticLlm: false });
    const names = scriptFlow.nodes.map(node => node.name);
    const files = new Set(scriptFlow.nodes.map(node => node.location?.file));

    assert.ok(files.has('hooks/handler.js'));
    assert.ok(files.has('hooks/handler.ts'));
    assert.ok(files.has('scripts/activator.sh'));
    assert.ok(names.some(name => name.includes('script.function.hooks_handler_js') && name.includes('injectreminder')));
    assert.ok(names.some(name => name.includes('script.function.hooks_handler_ts') && name.includes('normalizeevent')));
    assert.ok(names.some(name => name.includes('script.function.scripts_activator_sh') && name.includes('activate_skill')));
    assert.ok(scriptFlow.nodes.some(node => node.semanticKind === 'script_call' && node.callee === 'fetch'));
    assert.ok(scriptFlow.nodes.some(node => node.semanticKind === 'script_call' && node.callee === 'curl'));
    assert.ok(scriptFlow.edges.some(edge => edge.validation_method === 'script_flow'));

    const analyzer = new SkillFCGAnalyzer({ mode: 'quick', semanticLlm: false });
    const fcg = await analyzer.analyze(tempDir);
    assert.ok(fcg.documentation_context.source_policy.executable_source_files.includes('hooks/handler.ts'));
    assert.ok(fcg.documentation_context.source_policy.executable_source_files.includes('scripts/activator.sh'));
    assert.equal(
      fcg.documentation_context.source_policy.executable_source_files.some(file => path.isAbsolute(file)),
      false
    );
    assert.ok(fcg.nodes.some(node => node.semanticKind === 'script_function' && node.location.file === 'hooks/handler.ts'));
    assert.ok(fcg.nodes.some(node => node.semanticKind === 'script_call' && node.location.file === 'scripts/activator.sh'));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('shell runtime blocks model heredoc reminders and conditions as grounded semantic nodes', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-shell-runtime-'));
  try {
    fs.mkdirSync(path.join(tempDir, 'scripts'), { recursive: true });
    fs.writeFileSync(
      path.join(tempDir, 'scripts', 'error-detector.sh'),
      [
        '#!/usr/bin/env bash',
        'OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"',
        'contains_error=false',
        'if [ "$contains_error" = true ]; then',
        "  cat << 'EOF'",
        '<error-detected>',
        'A command error was detected. Consider logging this to .learnings/ERRORS.md if:',
        '- The error was unexpected or non-obvious',
        '</error-detected>',
        'EOF',
        'fi',
        ''
      ].join('\n'),
      'utf-8'
    );

    const executableFiles = findExecutableFiles(tempDir);
    const scriptFlow = await extractScriptFlow(executableFiles, { rootDir: tempDir, semanticLlm: false });
    const runtimeNodes = scriptFlow.nodes.filter(node =>
      node.location?.file === 'scripts/error-detector.sh' &&
      node.source_context?.action_evidence?.extraction_method === 'script_flow_runtime_block'
    );
    const reminder = runtimeNodes.find(node => node.source_context.action_evidence.snippet.includes('<error-detected>'));
    const condition = runtimeNodes.find(node => node.source_context.action_evidence.snippet.includes('contains_error'));

    assert.ok(reminder);
    assert.ok(condition);
    assert.equal(reminder.source_context.source_role, 'runtime_implementation');
    assert.ok(reminder.formal_semantics.targets.some(target => target.value.includes('.learnings/ERRORS.md')));
    assert.ok(condition.formal_semantics.conditions.some(item => item.text.includes('contains_error')));
    assert.equal(reminder.semantic_gate.method, 'script_rule_candidate_gate');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('shell runtime semantic gate keeps context-only blocks out of flow analysis', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-shell-runtime-context-'));
  try {
    fs.mkdirSync(path.join(tempDir, 'scripts'), { recursive: true });
    fs.writeFileSync(
      path.join(tempDir, 'scripts', 'notes.sh'),
      [
        '#!/usr/bin/env bash',
        "cat << 'EOF'",
        'Example output only. Do not infer a runtime route from this template.',
        'EOF',
        ''
      ].join('\n'),
      'utf-8'
    );

    const executableFiles = findExecutableFiles(tempDir);
    const scriptFlow = await extractScriptFlow(executableFiles, {
      rootDir: tempDir,
      semanticLlm: true,
      scriptSemanticRefiner: async () => ({
        classification: 'context_only',
        actionability: 'context_only',
        grammar: 'heredoc example text',
        operation_type: 'write',
        targets: [],
        conditions: [],
        effects: [],
        confidence: 0.9,
        reason: 'Template text, not runtime behavior.'
      })
    });
    const contextNode = scriptFlow.nodes.find(node =>
      node.location?.file === 'scripts/notes.sh' &&
      node.source_context?.action_evidence?.extraction_method === 'script_flow_runtime_block'
    );

    assert.ok(contextNode);
    assert.equal(contextNode.operationType, 'context');
    assert.equal(contextNode.excludeFromFlow, true);
    assert.equal(contextNode.excludeFromTypeAnalysis, true);
    assert.equal(contextNode.semantic_gate.actionability, 'context_only');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('shell runtime semantic gate failures become review context nodes', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-shell-runtime-error-'));
  try {
    fs.mkdirSync(path.join(tempDir, 'scripts'), { recursive: true });
    fs.writeFileSync(
      path.join(tempDir, 'scripts', 'reminder.sh'),
      [
        '#!/usr/bin/env bash',
        'if [ "$contains_error" = true ]; then',
        "  cat << 'EOF'",
        'Consider logging this to .learnings/ERRORS.md.',
        'EOF',
        'fi',
        ''
      ].join('\n'),
      'utf-8'
    );

    const executableFiles = findExecutableFiles(tempDir);
    const scriptFlow = await extractScriptFlow(executableFiles, {
      rootDir: tempDir,
      semanticLlm: true,
      llmApiKey: 'test-key',
      scriptSemanticRefiner: async () => {
        throw new Error('upstream 500');
      }
    });
    const errorNodes = scriptFlow.nodes.filter(node =>
      node.location?.file === 'scripts/reminder.sh' &&
      node.semantic_gate?.method === 'script_semantic_llm_error'
    );

    assert.ok(errorNodes.length > 0);
    assert.ok(errorNodes.every(node => node.excludeFromFlow === true));
    assert.ok(errorNodes.every(node => node.source_context.action_evidence.extraction_method === 'script_flow_runtime_block'));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
