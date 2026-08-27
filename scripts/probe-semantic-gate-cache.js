#!/usr/bin/env node
// Probe: does the semantic-gate endpoint already prefix-cache the constant system prompt?
// Sends the SAME batch 3x back-to-back and reports usage.cached_tokens each call.
// If cached_tokens jumps on call 2/3, the stable system prefix is ALREADY being cached
// with zero code change — and a prompt restructure would be premature.

const fs = require('fs');
const path = require('path');
const { postJsonWithTimeout } = require('../shared/llm-utils.cjs');

const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const m = /^([A-Z_]+)=(.*)$/.exec(line);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}
const ENDPOINT = process.env.LLM_ENDPOINT;
const MODEL = process.env.LLM_MODEL || 'gpt-5.5';
const KEY = process.env.LLM_API_KEY;
const TIMEOUT = Number(process.env.LLM_TIMEOUT || 180000);

function systemPrompt() {
  return [
    'You gate Markdown soft-instruction candidates before they become FCG action nodes.',
    'Return strict JSON only: {"results":[{...}]}. Each result must include the candidate id.',
    'First classify each source as one of: workflow_instruction, policy_rule, definition, schema, example, template, description, discard.',
    'Analyze English grammar: fragment, SVC, SVO, passive, imperative, table_row, heading, list_item.',
    'For fragments, reconstruct the missing subject or predicate before deciding actionability.',
    'For passive clauses, identify the patient/theme and only infer a runtime producer or consumer if the sentence commands an agent action.',
    'Table definitions, examples, templates, field schemas, and descriptive prose are not runtime actions unless the text explicitly instructs the agent to do something at runtime.',
    'Allowed operation_type values: trigger, condition, decision, read, write, transform, invoke_tool, verify, review, produce_artifact, guard.',
    'Allowed effects: read_context, persist_state, call_tool, update_memory, summarize, validate, branch.',
    'confidence must be a number from 0 to 1.',
    'Set actionability to runtime_action only when this candidate should become a flow node.',
    'Treat SKILL.md as the highest-priority semantic anchor for declared task, trigger conditions, route rules, policy rules, and workflow steps.',
    'For SKILL.md Situation->Action table rows, judge the whole row: put the situation in conditions and the action receiver/target in targets/effects.',
    'Do not split a Situation->Action row into fake standalone trigger or policy nodes.',
    'Never infer trigger/policy nodes from headings, file names, directory trees, template placeholders, or example error text.',
    'If a title or file description only names a log/template/example, classify it as description/template/example context_only.',
    'NEGATION HANDLING: a negated sentence is NOT automatically a disclaimer. Set negation_kind to disclaimer, constraint, or null.',
    'A genuine DISCLAIMER states a capability the skill does not have ("does not connect to a wallet", "does not send data externally"): negation_kind=disclaimer, classification=description, actionability=context_only.',
    'A PROHIBITIVE CONSTRAINT forbids or orders a runtime action ("never install a skill without vetting it first", "never delete without asking", "never overwrite existing files", "do not log secrets unless the user asks"): negation_kind=constraint, classification=policy_rule, actionability=runtime_action.',
    'For a constraint set constraint_edge to {kind:"ordering"|"guard", before_action, after_action, guarded_action, note}. ordering: before_action must precede after_action (e.g. before="vet skill", after="install skill"). guard: guarded_action is the forbidden/conditional action (e.g. guarded="overwrite existing files"); leave before_action/after_action null.',
    'If the candidate is not a negation, set negation_kind=null and constraint_edge=null.',
    'Do not create graph edges or path relationships.'
  ].join(' ');
}
function userPrompt(records) {
  return [
    'Gate each Markdown candidate independently.',
    'Return JSON with this shape:',
    '{"results":[{"id":"c1","classification":"workflow_instruction|policy_rule|definition|schema|example|template|description|discard","actionability":"runtime_action|context_only","grammar":"...","completed_sentence":"...","operation_type":"read|write|transform|invoke_tool|verify|review|produce_artifact|guard|condition|decision|trigger","targets":[],"conditions":[],"effects":[],"confidence":0.0,"reason":"..."}]}',
    'Use the exact candidate id. Do not omit a candidate. Do not infer graph edges.',
    '',
    'Candidates:',
    JSON.stringify(records, null, 2)
  ].join('\n');
}
function fullRecord(candidate) {
  const node = candidate.node || {};
  return {
    id: candidate.id, node: node.name || '',
    document: node.ownerDoc || node.location?.file || '',
    line: node.location?.line || 0, section: node.location?.section || '',
    source_role: node.source_context?.source_role || '',
    instruction: node.instructionText || node.formal_semantics?.evidence?.text || '',
    source_line: node.source_context?.source_line || node.formal_semantics?.evidence?.source_line || '',
    current_formal_semantics: node.formal_semantics || {}
  };
}

async function call(records) {
  const res = await postJsonWithTimeout(ENDPOINT, {
    model: MODEL, temperature: 0,
    messages: [
      { role: 'system', content: systemPrompt() },
      { role: 'user', content: userPrompt(records) }
    ]
  }, { timeoutMs: TIMEOUT, headers: { Authorization: `Bearer ${KEY}` } });
  const u = res?.usage || {};
  return {
    prompt_tokens: Number(u.prompt_tokens || u.input_tokens || 0),
    completion_tokens: Number(u.completion_tokens || u.output_tokens || 0),
    cached_tokens: Number(u.prompt_tokens_details?.cached_tokens ?? u.cached_tokens ?? u.prompt_cache_hit_tokens ?? 0),
    raw_usage_keys: Object.keys(u)
  };
}

(async () => {
  const skillFile = process.argv[2] || 'results/review-30/fcg/skills/skill_0002-00002_skill-vetter_1.0.0-sfg.json';
  const n = Number(process.argv[3] || 8);
  const d = JSON.parse(fs.readFileSync(skillFile, 'utf8'));
  const candidates = (d.nodes || []).slice(0, n).map((node, i) => ({ id: 'c' + (i + 1), node }));
  const records = candidates.map(fullRecord);

  console.log(`probe: same batch x3, ${candidates.length} candidates, model ${MODEL}`);
  console.log(`system prefix: ${systemPrompt().length} chars (constant)\n`);
  for (let i = 1; i <= 3; i++) {
    const u = await call(records);
    const ratio = u.prompt_tokens ? (u.cached_tokens / u.prompt_tokens) : 0;
    console.log(`call ${i}: prompt_tokens=${u.prompt_tokens}  cached_tokens=${u.cached_tokens}  cache_hit=${(ratio * 100).toFixed(1)}%  completion=${u.completion_tokens}`);
    if (i === 1) console.log(`         (usage fields returned: ${u.raw_usage_keys.join(', ') || 'NONE'})`);
  }
  console.log('\n如果 call 2/3 的 cached_tokens 明显>0,说明恒定 system 前缀已被自动缓存,无需重构 prompt。');
})();
