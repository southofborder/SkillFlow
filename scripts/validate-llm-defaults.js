#!/usr/bin/env node

require('../shared/load-env.cjs').loadProjectEnv({ entryFile: __filename });

const {
  normalizeSimilarityResult,
  normalizeValidationResult,
  normalizeReviewResult
} = require('../shared/llm-utils.cjs');

const ENDPOINT = process.env.LLM_ENDPOINT || 'https://xiaomuai.cn/v1/chat/completions';
const API_KEY = String(process.env.LLM_API_KEY || '').trim();
const PRIMARY_MODEL = String(process.env.LLM_MODEL || 'gpt-5.5').trim();
const FALLBACK_MODEL = 'deepseek-v4-pro';

async function main() {
  if (!API_KEY) throw new Error('LLM_API_KEY is required');

  const gate = await runStabilityGate(PRIMARY_MODEL, 10);
  const selectedDefaultModel = gate.ok ? PRIMARY_MODEL : FALLBACK_MODEL;
  const schemaChecks = await runSchemaChecks(selectedDefaultModel);

  console.log(JSON.stringify({
    checked_at: new Date().toISOString(),
    endpoint: ENDPOINT,
    primary_model: PRIMARY_MODEL,
    fallback_model: FALLBACK_MODEL,
    stability_gate: gate,
    selected_default_model: selectedDefaultModel,
    schema_checks: schemaChecks
  }, null, 2));

  if (!gate.ok) process.exitCode = 2;
}

async function runStabilityGate(model, runs) {
  const attempts = [];
  let ok = true;

  for (let index = 0; index < runs; index++) {
    try {
      const content = await callModel(model, [
        {
          role: 'system',
          content: 'Return strict JSON only in English with keys: similarity, reason, has_contradiction, contradiction_reason. similarity must be a number from 0 to 1. has_contradiction must be true or false.'
        },
        {
          role: 'user',
          content: 'Tool A summarizes PDFs. Tool B summarizes PDFs. Return a plausible JSON object only.'
        }
      ]);
      const normalized = normalizeSimilarityResult(content);
      const pass = Boolean(normalized && typeof normalized.similarity === 'number' && typeof normalized.has_contradiction === 'boolean');
      attempts.push({ run: index + 1, pass, normalized });
      if (!pass) ok = false;
    } catch (error) {
      ok = false;
      attempts.push({ run: index + 1, pass: false, error: error.message });
    }
  }

  return {
    ok,
    required_passes: runs,
    passed: attempts.filter(item => item.pass).length,
    attempts
  };
}

async function runSchemaChecks(model) {
  return {
    similarity: normalizeSimilarityResult(await callModel(model, [
      {
        role: 'system',
        content: 'Return strict JSON only in English with keys: similarity, reason, has_contradiction, contradiction_reason. similarity must be a number from 0 to 1. has_contradiction must be true or false.'
      },
      {
        role: 'user',
        content: 'Tool A summarizes PDFs. Tool B summarizes PDFs. Return a plausible JSON object only.'
      }
    ])),
    validation: normalizeValidationResult(await callModel(model, [
      {
        role: 'system',
        content: 'Return strict JSON only in English with keys: is_compatible, confidence, reason, data_flow_description. is_compatible must be true or false. confidence must be a number from 0 to 1.'
      },
      {
        role: 'user',
        content: 'Function A returns {"app_token":"abc"}. Function B accepts {"app_token":"string"}. Return JSON only.'
      }
    ])),
    review: normalizeReviewResult(await callModel(model, [
      {
        role: 'system',
        content: 'Return strict JSON only in English with keys: agrees, confidence, reason, suggested_severity. agrees must be true or false. confidence must be a number from 0 to 1. suggested_severity must be one of low, medium, high, critical.'
      },
      {
        role: 'user',
        content: 'Review a finding where one skill uniquely sends credentials to an external API. Return JSON only.'
      }
    ]))
  };
}

async function callModel(model, messages) {
  const response = await fetch(ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}`
    },
    body: JSON.stringify({ model, messages, temperature: 0 })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  const payload = await response.json();
  const content = payload?.choices?.[0]?.message?.content;
  if (!content) throw new Error('Empty model content');
  return content;
}

main().catch(error => {
  console.error(`LLM validation failed: ${error.message}`);
  process.exit(1);
});
