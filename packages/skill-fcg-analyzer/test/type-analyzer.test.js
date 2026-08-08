const test = require('node:test');
const assert = require('node:assert/strict');

const {
  analyzeTypeCompatibility,
  isContextOnlyNode,
  isDependencyCandidateNode,
  isBoundaryLikeNode
} = require('../src/parser/type-analyzer');

test('context-only documentation nodes are excluded from dependency candidates', () => {
  const contextNode = {
    name: 'doc.context.memory.l3.definition',
    semanticKind: 'doc_definition',
    excludeFromFlow: true,
    operationType: 'context'
  };
  const actionNode = {
    name: 'doc.step.memory.l8.write.memory',
    semanticKind: 'doc_step',
    excludeFromTypeAnalysis: true,
    input: { payload: { type: 'object' } },
    output: { result: { type: 'object' } },
    location: { file: 'memory.md', line: 8 },
    formal_semantics: {
      operation_type: 'write',
      targets: [{ type: 'file', value: 'memory.md', raw: 'memory.md' }]
    }
  };

  assert.equal(isContextOnlyNode(contextNode), true);
  assert.equal(isDependencyCandidateNode(contextNode), false);
  assert.equal(isDependencyCandidateNode(actionNode), true);
});

test('sparse dependency analysis avoids low-value script_call cross product', () => {
  const calls = Array.from({ length: 20 }, (_, index) => ({
    name: `script.call.handler.l${index + 1}.c1.helper_${index}`,
    semanticKind: 'script_call',
    input: { context: { type: 'object' } },
    output: { result: { type: 'object' } },
    location: { file: 'hooks/handler.js', line: index + 1 },
    formal_semantics: {
      operation_type: 'transform',
      targets: [{ type: 'function', value: `helper_${index}`, raw: `helper_${index}` }]
    }
  }));

  const candidates = analyzeTypeCompatibility(calls, { maxCandidates: 500 });

  assert.equal(candidates.length, 0);
  assert.ok(candidates.statistics.dependency_candidate_pruned_count > 0);
});

test('boundary-impact and global-route candidates are marked high value', () => {
  const docStep = {
    name: 'doc.step.workflow.l10.invoke.weather_api',
    semanticKind: 'doc_step',
    input: { context: { type: 'object' } },
    output: { payload: { type: 'object' } },
    location: { file: 'workflow.md', line: 10 },
    instructionText: 'Call the weather API with the city.',
    formal_semantics: {
      operation_type: 'external_egress',
      targets: [{ type: 'api', value: 'weather_api', raw: 'weather API' }]
    }
  };
  const scriptEntry = {
    name: 'script.entry.scripts_weather_sh',
    semanticKind: 'script_entry',
    input: { payload: { type: 'object' } },
    output: { result: { type: 'object' } },
    location: { file: 'scripts/weather.sh', line: 1 },
    formal_semantics: {
      operation_type: 'invoke_tool',
      targets: [{ type: 'script', value: 'weather_api', raw: 'weather_api' }]
    }
  };
  const webhook = {
    name: 'script.call.scripts_weather_sh.l4.c1.curl',
    semanticKind: 'script_call',
    input: { payload: { type: 'object' } },
    output: { result: { type: 'object' } },
    location: { file: 'scripts/weather.sh', line: 4 },
    formal_semantics: {
      operation_type: 'external_egress',
      targets: [{ type: 'url', value: 'https://api.weather.example', raw: 'curl https://api.weather.example' }]
    }
  };

  assert.equal(isBoundaryLikeNode(webhook), true);

  const candidates = analyzeTypeCompatibility([docStep, scriptEntry, webhook], { maxCandidates: 20 });
  const highValue = candidates.filter(candidate => candidate.high_value);

  assert.ok(highValue.some(candidate => candidate.high_value_reasons.includes('boundary-impact')));
  assert.ok(highValue.some(candidate => candidate.high_value_reasons.includes('global-route')));
});
