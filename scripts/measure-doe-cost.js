'use strict';
/**
 * Measure real DOE LLM-judge token/cost for a single skill FCG, without calling
 * the API. Uses the project's own pipeline (rule-only analysis + evidence-pack
 * build + budgeting + batching) and a mock llmClient that captures every payload
 * that WOULD be sent, then reports char/token/cost stats.
 */
const fs = require('fs');
const path = require('path');

const doeAnalyzer = require('../packages/skill-doe-analyzer/src/doe-analyzer');

const fcgPath = process.argv[2];
if (!fcgPath) {
  console.error('usage: node scripts/measure-doe-cost.js <fcg.json> [batchSize] [votes] [escalationVotes]');
  process.exit(1);
}

const batchSize = Number(process.argv[3] || 4);
const votes = Number(process.argv[4] || 1);
const escalationVotes = Number(process.argv[5] || 3);

// gpt-5.5 pricing placeholder (USD per 1M tokens). Override via env.
const PRICE_IN = Number(process.env.PRICE_IN || 1.25);   // input $/1M
const PRICE_OUT = Number(process.env.PRICE_OUT || 10.0); // output $/1M
const CHARS_PER_TOKEN = Number(process.env.CHARS_PER_TOKEN || 3.5); // mixed en/json/zh

console.error(`Reading FCG: ${fcgPath} ...`);
const raw = fs.readFileSync(fcgPath, 'utf-8');
console.error(`FCG bytes: ${raw.length.toLocaleString()}`);
const fcg = JSON.parse(raw);

// Capture every payload the judge would POST.
const sentPayloads = [];
let firstPassUnitCount = 0;
let escalationUnitCount = 0;

const llmClient = async ({ evidencePacks, payload, config }) => {
  const userContent = payload.messages.find(m => m.role === 'user')?.content || '';
  const sysContent = payload.messages.find(m => m.role === 'system')?.content || '';
  const chars = JSON.stringify(payload).length;
  // Break the user message into shared_context (task_memory, repeated every
  // request) vs evidence_packs (the actual per-unit payload).
  let sharedChars = 0;
  let packsChars = 0;
  try {
    const parsed = JSON.parse(userContent);
    sharedChars = JSON.stringify(parsed.shared_context || {}).length;
    packsChars = JSON.stringify(parsed.evidence_packs || []).length;
  } catch (_) {}
  sentPayloads.push({
    stage: config.stage,
    activeVotes: config.activeVotes,
    units: evidencePacks.length,
    userChars: userContent.length,
    sysChars: sysContent.length,
    sharedChars,
    packsChars,
    totalChars: chars
  });
  if (config.stage === 'escalation') escalationUnitCount += evidencePacks.length / Math.max(1, config.activeVotes);

  // Return a minimal valid assessment for every unit so the pipeline proceeds
  // (and escalation selection can run on real first-pass results).
  const assessments = evidencePacks.map(pack => ({
    unit_id: pack.unit_id,
    components: {
      action_input_need: { score: 0.5, status: 'insufficient', supporting_evidence_ids: ['boundary.observation'] },
      receiver_semantic_need: { score: 0.5, status: 'insufficient', supporting_evidence_ids: ['boundary.observation'] },
      task_need: { score: 0.5, status: 'insufficient', supporting_evidence_ids: ['boundary.observation'] }
    },
    necessity_level: 'medium',
    required_for_task: true,
    reasoning_summary: 'mock',
    supporting_evidence_ids: ['boundary.observation']
  }));
  // Mock output token estimate: a real judge reply is roughly this JSON.
  const replyChars = JSON.stringify({ assessments }).length;
  sentPayloads[sentPayloads.length - 1].replyChars = replyChars;
  return { assessments };
};

(async () => {
  console.error('Running rule-only + pack build + mock judge ...');
  const result = await doeAnalyzer.analyzeDoeAsync(fcg, {
    inputFcg: path.basename(fcgPath),
    llmJudge: true,
    llmClient,
    llmApiKey: 'mock',
    llmBatchSize: batchSize,
    llmVotes: votes,
    llmEscalationVotes: escalationVotes,
    llmEscalationPolicy: process.env.ESC_POLICY || 'risk_or_uncertain',
    llmConcurrency: 1
  });

  const stats = result.statistics;
  const firstPass = sentPayloads.filter(p => p.stage === 'first_pass');
  const escalation = sentPayloads.filter(p => p.stage === 'escalation');

  const sum = (arr, key) => arr.reduce((a, p) => a + (p[key] || 0), 0);
  const inputChars = sum(sentPayloads, 'totalChars');
  const outputChars = sum(sentPayloads, 'replyChars');
  const inputTokens = inputChars / CHARS_PER_TOKEN;
  const outputTokens = outputChars / CHARS_PER_TOKEN;
  const cost = (inputTokens / 1e6) * PRICE_IN + (outputTokens / 1e6) * PRICE_OUT;

  console.log('\n================ DOE LLM-judge cost measurement ================');
  console.log(`FCG file                 : ${path.basename(fcgPath)}`);
  console.log(`assessment_count (total) : ${stats.assessment_count?.toLocaleString()}`);
  console.log(`boundary_crossing_count  : ${stats.boundary_crossing_count?.toLocaleString()}`);
  console.log(`llm_eligible_count       : ${stats.llm_eligible_count?.toLocaleString()}  <- units actually sent`);
  console.log(`llm_skipped_count        : ${stats.llm_skipped_count?.toLocaleString()}`);
  console.log('');
  console.log(`config: batchSize=${batchSize} votes=${votes} escalationVotes=${escalationVotes}`);
  console.log(`first-pass requests      : ${firstPass.length}  (units*votes sent)`);
  console.log(`escalation requests      : ${escalation.length}`);
  console.log(`escalated units          : ~${Math.round(escalationUnitCount).toLocaleString()}`);
  console.log('');
  console.log(`avg payload chars/request: ${firstPass.length ? Math.round(sum(firstPass,'totalChars')/firstPass.length).toLocaleString() : 0}`);
  console.log(`  shared_context (repeated): ~${firstPass.length ? Math.round(sum(firstPass,'sharedChars')/firstPass.length).toLocaleString() : 0} chars/request`);
  console.log(`  evidence_packs (real)    : ~${firstPass.length ? Math.round(sum(firstPass,'packsChars')/firstPass.length).toLocaleString() : 0} chars/request`);
  console.log(`TOTAL shared_context chars : ${sum(sentPayloads,'sharedChars').toLocaleString()}  (${(100*sum(sentPayloads,'sharedChars')/inputChars).toFixed(1)}% of input)`);
  console.log(`TOTAL evidence_pack chars  : ${sum(sentPayloads,'packsChars').toLocaleString()}  (${(100*sum(sentPayloads,'packsChars')/inputChars).toFixed(1)}% of input)`);
  console.log('');
  console.log(`TOTAL input chars        : ${inputChars.toLocaleString()}`);
  console.log(`TOTAL output chars (est) : ${outputChars.toLocaleString()}`);
  console.log(`~input tokens            : ${Math.round(inputTokens).toLocaleString()}`);
  console.log(`~output tokens           : ${Math.round(outputTokens).toLocaleString()}`);
  console.log('');
  console.log(`pricing: $${PRICE_IN}/1M in, $${PRICE_OUT}/1M out, ${CHARS_PER_TOKEN} chars/token`);
  console.log(`>>> estimated cost (1 vote, no cache): $${cost.toFixed(2)} <<<`);
  console.log('=================================================================');
})().catch(err => {
  console.error('ERROR:', err.message);
  process.exit(1);
});
