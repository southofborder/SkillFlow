#!/usr/bin/env node
// Pre-implementation probe: can the LLM reliably distinguish a genuine
// disclaimer ("skill does NOT do X") from a PROHIBITIVE CONSTRAINT that implies
// an ordering/guard edge — and extract the constraint tuple — when we ask it to?
// If it can't, the whole negation-reclassification design is unsound.
//
// We feed real negated_disclaimer lines from the corpus and ask the gate,
// augmented with negation-handling instructions + a constraint_edge output slot.

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

// Augmented system prompt: the existing gate rules PLUS explicit negation handling.
function systemPrompt() {
  return [
    'You gate Markdown soft-instruction candidates before they become FCG action nodes.',
    'Return strict JSON only: {"results":[{...}]}. Each result must include the candidate id.',
    'Classify each source as one of: workflow_instruction, policy_rule, definition, schema, example, template, description, discard.',
    'NEGATION HANDLING (important): a negated sentence is NOT automatically a disclaimer.',
    ' - A genuine DISCLAIMER states a capability the skill does not have ("does not connect to a wallet", "does not send data externally"). classification=description, actionability=context_only, negation_kind=disclaimer.',
    ' - A PROHIBITIVE CONSTRAINT forbids or orders a runtime action ("never install a skill without vetting it first", "never delete without asking", "never overwrite existing files", "do not log secrets unless the user asks"). It implies a REQUIRED relationship between actions. classification=policy_rule, actionability=runtime_action, negation_kind=constraint.',
    'For a constraint, set constraint_edge to {kind:"ordering"|"guard", before_action, after_action, guarded_action, note}. ordering: before_action must precede after_action (e.g. before="vet skill", after="install skill"). guard: guarded_action is forbidden/conditional (e.g. guarded="overwrite existing files"). Leave unused fields null.',
    'If the line is not a negation, negation_kind=null and constraint_edge=null.',
    'Allowed operation_type values: trigger, condition, decision, read, write, transform, invoke_tool, verify, review, produce_artifact, guard.',
    'Return strict JSON only.'
  ].join(' ');
}

function userPrompt(cases) {
  return [
    'Gate each candidate independently. For each, decide negation_kind (disclaimer|constraint|null) and, if constraint, extract constraint_edge.',
    'Return JSON: {"results":[{"id","classification","actionability","operation_type","negation_kind","constraint_edge","reason"}]}',
    '',
    'Candidates:',
    JSON.stringify(cases.map((c, i) => ({ id: 'c' + (i + 1), section: c.section, instruction: c.text })), null, 2)
  ].join('\n');
}

// Real corpus lines + expected label (for scoring). Mix of both classes.
const CASES = [
  { text: 'Never install a skill without vetting it first.', section: 'Skill Vetter', expect: 'constraint' },
  { text: 'Never delete without asking', section: 'Rules', expect: 'constraint' },
  { text: 'Never overwrite existing files. This is a no-op if `.learnings/` is already initialised.', section: 'Init', expect: 'constraint' },
  { text: 'Do not log secrets, tokens, private keys unless the user explicitly asks.', section: 'Security', expect: 'constraint' },
  { text: 'Never delete data, empty files, or overwrite uncertain text', section: 'Rules', expect: 'constraint' },
  { text: 'Does not connect to any wallet or financial account', section: 'Limitations', expect: 'disclaimer' },
  { text: 'Does not execute real trades or transactions', section: 'Limitations', expect: 'disclaimer' },
  { text: 'Does not send any personal data externally', section: 'Limitations', expect: 'disclaimer' },
  { text: 'Does not require or handle any credentials or API keys', section: 'Limitations', expect: 'disclaimer' },
  { text: 'Never infer from silence alone', section: 'Guidelines', expect: 'constraint' }
];

(async () => {
  const res = await postJsonWithTimeout(ENDPOINT, {
    model: MODEL, temperature: 0,
    messages: [
      { role: 'system', content: systemPrompt() },
      { role: 'user', content: userPrompt(CASES) }
    ]
  }, { timeoutMs: TIMEOUT, headers: { Authorization: `Bearer ${KEY}` } });

  const content = res?.choices?.[0]?.message?.content || '';
  let parsed;
  try { parsed = JSON.parse(content.replace(/```json\s*|\s*```/g, '').trim()); }
  catch (e) { console.log('PARSE ERROR:', e.message, '\nRAW:', content.slice(0, 800)); return; }

  const byId = {};
  for (const r of (parsed.results || [])) byId[r.id] = r;

  let correct = 0;
  console.log('=== LLM 否定句分类实测 ===\n');
  CASES.forEach((c, i) => {
    const r = byId['c' + (i + 1)] || {};
    const got = r.negation_kind || 'null';
    const ok = got === c.expect;
    if (ok) correct++;
    console.log(`${ok ? '✓' : '✗'} [expect ${c.expect} / got ${got}] ${JSON.stringify(c.text.slice(0, 70))}`);
    if (r.negation_kind === 'constraint' && r.constraint_edge) {
      const e = r.constraint_edge;
      console.log(`     constraint_edge: kind=${e.kind} before=${JSON.stringify(e.before_action)} after=${JSON.stringify(e.after_action)} guarded=${JSON.stringify(e.guarded_action)}`);
    }
  });
  console.log(`\n=== 准确率: ${correct}/${CASES.length} (${Math.round(100 * correct / CASES.length)}%) ===`);
  const u = res?.usage || {};
  console.log(`usage: prompt=${u.prompt_tokens || 0} completion=${u.completion_tokens || 0} cached=${u.prompt_tokens_details?.cached_tokens ?? 0}`);
})();
