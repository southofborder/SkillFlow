#!/usr/bin/env node
// A/B: does dropping current_formal_semantics from the semantic-gate input change LLM verdicts?
// A = full record (with current_formal_semantics). B = same records minus that field.
// Prints per-candidate verdict diff + input-size delta. Read-only; no source changes.

const fs = require('fs');
const path = require('path');
const { postJsonWithTimeout } = require('../shared/llm-utils.cjs');

// load .env (names only referenced; values never printed)
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
const TIMEOUT = Number(process.env.LLM_TIMEOUT || 120000);

// ---- verbatim system prompt (from doc-flow-extractor buildSemanticGateSystemPrompt) ----
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
    id: candidate.id,
    node: node.name || '',
    document: node.ownerDoc || node.location?.file || '',
    line: node.location?.line || 0,
    section: node.location?.section || '',
    source_role: node.source_context?.source_role || '',
    instruction: node.instructionText || node.formal_semantics?.evidence?.text || '',
    source_line: node.source_context?.source_line || node.formal_semantics?.evidence?.source_line || '',
    current_formal_semantics: node.formal_semantics || {}
  };
}

function leanRecord(candidate) {
  const r = fullRecord(candidate);
  delete r.current_formal_semantics; // the ONLY difference
  return r;
}

// D = judgment only: keep the rule's VERDICT (op_type/actor/role/confidence),
// drop all evidence prose and table-derived filler (inputs/outputs/effects/targets/...).
function judgmentRecord(candidate) {
  const r = fullRecord(candidate);
  const fs_ = r.current_formal_semantics || {};
  if (!fs_ || Object.keys(fs_).length === 0) {
    delete r.current_formal_semantics; // empty stays empty
    return r;
  }
  const ev = fs_.evidence || {};
  const j = {};
  if (fs_.operation_type) j.operation_type = fs_.operation_type;
  if (fs_.actor) j.actor = fs_.actor;
  if (ev.role) j.role = ev.role;                 // the rule's classification (e.g. negated_disclaimer)
  if (typeof fs_.confidence === 'number') j.confidence = fs_.confidence;
  r.current_formal_semantics = j;
  return r;
}

async function callGate(records) {
  const payload = {
    model: MODEL,
    temperature: 0,
    messages: [
      { role: 'system', content: systemPrompt() },
      { role: 'user', content: userPrompt(records) }
    ]
  };
  const res = await postJsonWithTimeout(ENDPOINT, payload, {
    timeoutMs: TIMEOUT,
    headers: { Authorization: `Bearer ${KEY}` }
  });
  const content = res?.choices?.[0]?.message?.content || '';
  const u = res?.usage || {};
  const usage = {
    prompt_tokens: Number(u.prompt_tokens || u.input_tokens || 0),
    completion_tokens: Number(u.completion_tokens || u.output_tokens || 0),
    cached_tokens: Number(u.prompt_tokens_details?.cached_tokens ?? u.cached_tokens ?? u.prompt_cache_hit_tokens ?? 0)
  };
  const inChars = systemPrompt().length + userPrompt(records).length;
  let parsed;
  try {
    const jsonText = content.replace(/```json\s*|\s*```/g, '').trim();
    parsed = JSON.parse(jsonText);
  } catch (e) {
    parsed = { _parse_error: e.message, _raw: content.slice(0, 500) };
  }
  return { parsed, inChars, outChars: content.length, usage };
}

function verdictMap(parsed) {
  const m = {};
  for (const r of (parsed.results || [])) {
    m[r.id] = {
      classification: r.classification,
      actionability: r.actionability,
      operation_type: r.operation_type
    };
  }
  return m;
}

(async () => {
  const skillFile = process.argv[2]
    || 'results/review-30/fcg/skills/skill_0002-00002_skill-vetter_1.0.0-fcg.json';
  const n = Number(process.argv[3] || 5);
  const d = JSON.parse(fs.readFileSync(skillFile, 'utf8'));
  const nodes = (d.nodes || []).slice(0, n);
  const candidates = nodes.map((node, i) => ({ id: 'c' + (i + 1), node }));

  console.log(`skill: ${path.basename(skillFile)}  candidates: ${candidates.length}  model: ${MODEL}`);
  console.log('running A  (full) ...');
  const A = await callGate(candidates.map(fullRecord));
  console.log('running A2 (full, repeat = noise baseline) ...');
  const A2 = await callGate(candidates.map(fullRecord));
  console.log('running D  (judgment-only formal_semantics) ...');
  const D = await callGate(candidates.map(judgmentRecord));

  const va = verdictMap(A.parsed);
  const va2 = verdictMap(A2.parsed);
  const vd = verdictMap(D.parsed);

  function diffReport(label, base, other) {
    console.log(`\n=== VERDICT DIFF ${label} ===`);
    let diffs = 0;
    for (const c of candidates) {
      const a = base[c.id] || {};
      const b = other[c.id] || {};
      for (const k of ['classification', 'actionability', 'operation_type']) {
        if (a[k] !== b[k]) {
          diffs++;
          console.log(`  ${c.id} (${c.node.name}): ${k}  "${a[k]}" -> "${b[k]}"`);
        }
      }
    }
    console.log(diffs === 0 ? '  (identical)' : `  ${diffs} field-level differences.`);
    return diffs;
  }

  console.log('\n=== INPUT SIZE ===');
  console.log(`  A  full:          ${A.inChars} chars in`);
  console.log(`  D  judgment-only: ${D.inChars} chars in`);
  const saved = A.inChars - D.inChars;
  console.log(`  input saved by judgment-only: ${saved} chars (${Math.round(100 * saved / A.inChars)}%)`);

  const noise = diffReport('A vs A2  (SAME input twice — pure model noise)', va, va2);
  const real = diffReport('A vs D   (full vs judgment-only)', va, vd);

  console.log('\n=== INTERPRETATION ===');
  console.log(`  model noise (A vs A2):    ${noise} diffs`);
  console.log(`  judgment-only (A vs D):   ${real} diffs`);
  if (real <= noise) console.log('  => D差异不超过噪声,瘦身安全。');
  else console.log('  => D差异超过噪声基线,瘦身真的改变了裁定。');

  for (const [lbl, r] of [['A', A.parsed], ['A2', A2.parsed], ['D', D.parsed]]) {
    if (r._parse_error) console.log(`  ${lbl} parse error:`, r._parse_error);
  }
})();
