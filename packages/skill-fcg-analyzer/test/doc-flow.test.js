const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { SkillFCGAnalyzer } = require('../src/index');
const { parseSkill } = require('../src/parser/skill-parser');
const { extractDocumentFlow } = require('../src/parser/doc-flow-extractor');

test('doc-flow switch adds document-flow nodes and doc_instruction edges', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: doc-flow-skill
description: Use when command fails or user corrects you.
version: 0.1.0
---

When user corrects you, read \`memory.md\` and update \`memory.md\`.
Read \`memory.md\`.
Open \`memory.md\`.
After 3x repeated pattern, promote to HOT in \`memory.md\`.
Read \`setup.md\` first, then log to \`corrections.md\`.
Decide whether to promote the lesson to HOT memory.
Periodically review MEMORY.md and summarize stale lessons.
`,
      'utf-8'
    );

    fs.writeFileSync(path.join(tempDir, 'setup.md'), '# setup\nRun `details.md` before finalizing.\n', 'utf-8');
    fs.writeFileSync(path.join(tempDir, 'details.md'), '# details\nRead details and write final notes.\n', 'utf-8');
    fs.writeFileSync(path.join(tempDir, 'memory.md'), '# memory\n', 'utf-8');
    fs.writeFileSync(path.join(tempDir, 'corrections.md'), '# corrections\n', 'utf-8');

    const analyzer = new SkillFCGAnalyzer({
      mode: 'quick',
      semanticLlm: false
    });

    const result = await analyzer.analyze(tempDir);
    const nodeNames = result.nodes.map(node => node.name);
    const docEdges = result.edges.filter(edge => edge.type === 'doc_instruction');
    const semanticEdges = result.edges.filter(edge => edge.type === 'semantic');
    const controlFlowEdges = result.edges.filter(edge => edge.type === 'control_flow');

    const nodeById = new Map(result.nodes.map(node => [node.id, node.name]));
    const llmId = result.nodes.find(node => node.name === 'llm.inference')?.id || '';
    const semanticNodes = result.nodes.filter(node => node.formal_semantics);
    const docStepNodes = result.nodes.filter(node => node.semanticKind === 'doc_step');
    const docOperationNodes = result.nodes.filter(node => node.semanticKind === 'doc_operation');
    const semanticTypes = new Set(semanticNodes.map(node => node.formal_semantics.operation_type));

    assert.ok(nodeNames.includes('llm.inference'));
    assert.ok(nodeNames.some(name => name.startsWith('doc.step.') && name.includes('.setup')));
    assert.ok(nodeNames.some(name => name.startsWith('doc.step.') && name.includes('.details')));
    assert.ok(nodeNames.some(name => name.startsWith('doc.step.') && name.includes('.memory')));
    assert.ok(nodeNames.some(name => name.startsWith('doc.step.') && name.includes('.corrections')));
    assert.equal(docOperationNodes.length, 0);
    assert.ok(docStepNodes.length >= 4);
    assert.ok(docStepNodes.every(node => Number.isInteger(node.stepIndex)));
    assert.equal(nodeNames.some(name => name.startsWith('rule.trigger.')), false);
    assert.equal(nodeNames.some(name => name.startsWith('rule.policy.')), false);
    assert.ok(result.nodes.some(node =>
      node.location?.file === 'SKILL.md' &&
      node.source_context?.source_role === 'semantic_anchor' &&
      node.instructionText.includes('log to `corrections.md`')
    ));
    assert.ok(docEdges.length >= 4);
    assert.equal(semanticEdges.length, 0);
    assert.ok(controlFlowEdges.some(edge => (edge.semantic_reason || '').includes('Markdown reference jump')));
    assert.ok(semanticNodes.length > 0);
    assert.ok(semanticTypes.has('trigger'));
    assert.ok(semanticTypes.has('decision'));
    assert.ok(semanticTypes.has('write'));

    // SKILL.md is an extraction semantic anchor now, but it must not create
    // placeholder action nodes for missing external markdown files.
    assert.equal(result.nodes.some(node => node.ownerDoc === 'EXTERNAL'), false);
    assert.ok(docEdges.some(edge => {
      const targetName = nodeById.get(edge.target) || '';
      return edge.validation_method === 'doc_flow' && targetName.includes('.setup');
    }));

    // Ensure setup step jumps into details step through control flow.
    const hasSetupToDetailsJump = controlFlowEdges.some(edge => {
      const sourceName = nodeById.get(edge.source) || '';
      const targetName = nodeById.get(edge.target) || '';
      return sourceName.includes('.setup') && targetName.includes('.details');
    });
    assert.equal(hasSetupToDetailsJump, true);

    const hasStepSequence = controlFlowEdges.some(edge => {
      const sourceName = nodeById.get(edge.source) || '';
      const targetName = nodeById.get(edge.target) || '';
      return sourceName.startsWith('doc.step.') &&
        targetName.startsWith('doc.step.') &&
        (edge.semantic_reason || '').includes('Sequential markdown steps');
    });
    assert.equal(hasStepSequence, true);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('README is review-only while extraction docs provide grounded nodes', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-readme-review-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: readme-review-skill
description: Use workflow.md for the actual workflow.
version: 0.1.0
---

Follow \`workflow.md\`.
`,
      'utf-8'
    );
    fs.writeFileSync(
      path.join(tempDir, 'README.md'),
      'README says to call `webhook.post`, but this is review context only.\n',
      'utf-8'
    );
    fs.writeFileSync(
      path.join(tempDir, 'workflow.md'),
      '# workflow\nCall `weather.api` and save the weather report.\n',
      'utf-8'
    );

    const analyzer = new SkillFCGAnalyzer({
      mode: 'quick',
      semanticLlm: false
    });
    const result = await analyzer.analyze(tempDir);
    const nodeFiles = new Set(result.nodes.map(node => node.location?.file || ''));
    const names = new Set(result.nodes.map(node => node.canonical_name || node.name));
    const extractedNode = result.nodes.find(node => node.location?.file === 'workflow.md' && node.source_context);

    assert.equal(nodeFiles.has('README.md'), false);
    assert.equal(names.has('webhook.post'), false);
    assert.equal(names.has('weather.api'), true);
    assert.equal(result.documentation_context.source_policy.readme_md_role, 'review_only');
    assert.ok(result.documentation_context.readme_context.preview.includes('webhook.post'));
    assert.ok(extractedNode);
    assert.equal(extractedNode.source_context.action_evidence.grounded, true);
    assert.ok(extractedNode.source_context.action_evidence.snippet.includes('weather.api') ||
      extractedNode.source_context.source_line.includes('weather.api'));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('doc-flow splits English compound actions into ordered doc_step nodes', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-compound-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: english-compound-skill
description: Test English compound action splitting.
version: 0.1.0
---

- Summarize the email content and save it locally.
- Read customer records, redact secrets, and send a summary to the model.
- Extract the city from the profile and call the weather API.
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, { semanticLlm: false });
    const steps = result.nodes.filter(node => node.semanticKind === 'doc_step');
    const operationTexts = steps.map(node => `${node.formal_semantics.operation_type}:${node.instructionText}`);

    assert.ok(operationTexts.some(text => text.includes('transform:Summarize the email content')));
    assert.ok(operationTexts.some(text => text.includes('write:save it locally')));
    assert.ok(operationTexts.some(text => text.includes('read:Read customer records')));
    assert.ok(operationTexts.some(text => text.includes('transform:redact secrets')));
    assert.ok(operationTexts.some(text => text.includes('model_inference:send a summary to the model')));
    assert.ok(operationTexts.some(text => text.includes('transform:Extract the city from the profile')));
    assert.ok(operationTexts.some(text => text.includes('external_egress:call the weather API')));

    const sequenceEdges = result.edges.filter(edge => edge.type === 'control_flow');
    assert.ok(sequenceEdges.length >= 5);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('doc-flow adds implicit object reads and reuses prior object producers', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-implicit-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: implicit-object-skill
description: Test implicit object reads.
version: 0.1.0
---

- Write the email content to a local file.
- Read email content and write it to a local file.
- Write the report to a file, then upload the report.
- Write the analysis result to a local file.
- Generate a report and upload the report.
- Generate a report about the email.
- Generate a report about current AI.
- Create the analysis result and save it locally.
- Summarize the email content and save the summary.
- Read the email and write it to a file.
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, { semanticLlm: false });
    const steps = result.nodes.filter(node => node.semanticKind === 'doc_step');
    const implicitReads = steps.filter(node => node.formal_semantics?.evidence?.method === 'implicit_object_read');
    const emailImplicitReads = implicitReads.filter(node => node.name.includes('email_content'));
    const emailObjectImplicitReads = implicitReads.filter(node => node.name.includes('semantic_email') && !node.name.includes('email_content'));
    const writeIt = steps.find(node => node.instructionText === 'write it to a local file.');
    const explicitReadEmail = steps.find(node => node.instructionText === 'Read email content');
    const uploadReport = steps.find(node => node.instructionText === 'upload the report.');
    const writeReport = steps.find(node => node.instructionText === 'Write the report to a file');
    const generatedReport = steps.find(node => node.instructionText === 'Generate a report');
    const generatedReportAboutEmail = steps.find(node => node.instructionText === 'Generate a report about the email.');
    const generatedReportAboutAi = steps.find(node => node.instructionText === 'Generate a report about current AI.');
    const uploadGeneratedReport = steps.find(node =>
      node.instructionText === 'upload the report.' &&
      node.objectProducer === generatedReport?.name
    );
    const createdAnalysis = steps.find(node => node.instructionText === 'Create the analysis result');
    const saveCreatedAnalysis = steps.find(node =>
      node.instructionText === 'save it locally.' &&
      node.objectProducer === createdAnalysis?.name
    );
    const summarizeEmail = steps.find(node => node.instructionText === 'Summarize the email content');
    const saveSummary = steps.find(node => node.instructionText === 'save the summary.');
    const explicitReadTheEmail = steps.find(node => node.instructionText === 'Read the email');
    const writePronounEmail = steps.find(node =>
      node.instructionText === 'write it to a file.' &&
      node.objectProducer === explicitReadTheEmail?.name
    );
    const objectEdges = result.edges.filter(edge => edge.validation_method === 'doc_flow_object_context');
    const implicitReadToLlm = result.edges.find(edge =>
      edge.source === emailImplicitReads[0].name &&
      edge.target === 'llm.inference'
    );

    assert.equal(emailImplicitReads.length, 1);
    assert.equal(emailObjectImplicitReads.length, 1);
    assert.equal(implicitReads.filter(node => node.name.includes('summary')).length, 0);
    assert.ok(implicitReadToLlm);
    assert.ok(writeIt);
    assert.ok(explicitReadEmail);
    assert.equal(writeIt.objectProducer, explicitReadEmail.name);
    assert.ok(uploadReport);
    assert.ok(writeReport);
    assert.equal(uploadReport.objectProducer, writeReport.name);
    assert.ok(generatedReport);
    assert.ok(generatedReportAboutEmail);
    assert.equal(generatedReportAboutEmail.objectProducer, emailObjectImplicitReads[0].name);
    assert.ok(generatedReportAboutAi);
    assert.equal(generatedReportAboutAi.objectProducer, undefined);
    assert.equal(implicitReads.filter(node => node.name.includes('current_ai')).length, 0);
    assert.ok(uploadGeneratedReport);
    assert.equal(uploadGeneratedReport.objectProducer, generatedReport.name);
    assert.ok(createdAnalysis);
    assert.ok(saveCreatedAnalysis);
    assert.ok(summarizeEmail);
    assert.ok(saveSummary);
    assert.equal(saveSummary.objectProducer, summarizeEmail.name);
    assert.ok(explicitReadTheEmail);
    assert.ok(writePronounEmail);
    assert.ok(objectEdges.some(edge => edge.source === emailImplicitReads[0].name && edge.semantic_reason.includes('email_content')));
    assert.ok(objectEdges.some(edge => edge.source === explicitReadEmail.name && edge.target === writeIt.name));
    assert.ok(objectEdges.some(edge => edge.source === writeReport.name && edge.target === uploadReport.name));
    assert.ok(objectEdges.some(edge => edge.source === generatedReport.name && edge.target === uploadGeneratedReport.name));
    assert.ok(objectEdges.some(edge => edge.source === createdAnalysis.name && edge.target === saveCreatedAnalysis.name));
    assert.ok(objectEdges.some(edge => edge.source === summarizeEmail.name && edge.target === saveSummary.name));
    assert.ok(objectEdges.some(edge => edge.source === explicitReadTheEmail.name && edge.target === writePronounEmail.name));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('doc-flow classifies readable, abstract, and artifact-like objects for implicit reads', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-object-class-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: object-classification-skill
description: Test implicit object classification.
version: 0.1.0
---

- Upload the report.
- Save the analysis result locally.
- Generate a report about the email.
- Generate a report from customer records.
- Write the chat history to a file.
- Upload the invoice PDF.
- Generate a report about current AI.
- Generate a report about current task.
- Generate a report about assistant behavior.
- Generate a report about this skill.
- Generate a report and upload the report.
- Create the analysis result and save it locally.
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, { semanticLlm: false });
    const steps = result.nodes.filter(node => node.semanticKind === 'doc_step');
    const implicitReads = steps.filter(node => node.formal_semantics?.evidence?.method === 'implicit_object_read');
    const implicitReadNames = implicitReads.map(node => node.name);
    const implicitReadKeys = implicitReads.map(node => node.formal_semantics?.evidence?.object_key || '');
    const implicitReadText = implicitReads
      .map(node => node.formal_semantics?.evidence?.object_key || node.instructionText || '')
      .join(' ');
    const generatedReport = steps.find(node => node.instructionText === 'Generate a report');
    const uploadGeneratedReport = steps.find(node =>
      node.instructionText === 'upload the report.' &&
      node.objectProducer === generatedReport?.name
    );
    const standaloneUploadReport = steps.find(node =>
      node.instructionText === 'Upload the report.' &&
      node.objectProducer &&
      node.objectProducer !== generatedReport?.name
    );
    const createdAnalysis = steps.find(node => node.instructionText === 'Create the analysis result');
    const saveCreatedAnalysis = steps.find(node =>
      node.instructionText === 'save it locally.' &&
      node.objectProducer === createdAnalysis?.name
    );
    const standaloneSaveAnalysis = steps.find(node =>
      node.instructionText === 'Save the analysis result locally.' &&
      node.objectProducer &&
      node.objectProducer !== createdAnalysis?.name
    );

    assert.ok(implicitReadNames.some(name => name.includes('semantic_email')));
    assert.ok(implicitReadNames.some(name => name.includes('customer_records')));
    assert.ok(implicitReadNames.some(name => name.includes('chat_history')));
    assert.ok(implicitReadNames.some(name => name.includes('invoice_pdf')));
    assert.ok(implicitReadKeys.includes('report'));
    assert.ok(implicitReadKeys.includes('analysis_result'));
    assert.equal(/\bcurrent_ai\b/.test(implicitReadText), false);
    assert.equal(/\bcurrent_task\b/.test(implicitReadText), false);
    assert.equal(/\bassistant_behavior\b/.test(implicitReadText), false);
    assert.equal(/\bthis_skill\b/.test(implicitReadText), false);
    assert.ok(uploadGeneratedReport);
    assert.ok(standaloneUploadReport);
    assert.ok(saveCreatedAnalysis);
    assert.ok(standaloneSaveAnalysis);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('FCG expands repeated tool call-sites and inserts ordered LLM mediation', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-callsite-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: callsite-skill
description: Test repeated tool call-sites.
version: 0.1.0
---

Use \`gmail.message.get\` to read the email.
Use \`webhook.post\` to send the email.
Use \`gmail.message.get\` again to verify the email.
`,
      'utf-8'
    );

    const analyzer = new SkillFCGAnalyzer({
      mode: 'quick',
      semanticLlm: false
    });
    const result = await analyzer.analyze(tempDir);
    const gmailNodes = result.nodes.filter(node => node.canonical_name === 'gmail.message.get');
    const webhookNode = result.nodes.find(node => node.canonical_name === 'webhook.post');
    const mediationNodes = result.nodes.filter(node =>
      node.canonical_name === 'llm.inference' &&
      /^llm\.inference#(?:before|after)_call_\d{3}$/.test(node.name)
    );
    const edgeByName = result.edges.map(edge => ({
      source: result.nodes.find(node => node.id === edge.source)?.name || edge.source,
      target: result.nodes.find(node => node.id === edge.target)?.name || edge.target,
      method: edge.validation_method
    }));

    assert.equal(result.security_profile.version, '5.1');
    assert.equal(gmailNodes.length, 2);
    assert.ok(webhookNode);
    assert.notEqual(gmailNodes[0].name, gmailNodes[1].name);
    assert.ok(gmailNodes.every(node => node.callsite_id && Number.isInteger(node.callsite_order)));
    assert.equal(mediationNodes.length, 6);
    assert.ok(result.nodes.some(node => node.name === `llm.inference#before_${gmailNodes[0].callsite_id}`));
    assert.ok(result.nodes.some(node => node.name === `llm.inference#after_${gmailNodes[0].callsite_id}`));
    assert.ok(edgeByName.some(edge =>
      edge.source === `llm.inference#before_${gmailNodes[0].callsite_id}` &&
      edge.target === gmailNodes[0].name &&
      edge.method === 'callsite_mediation'
    ));
    assert.ok(edgeByName.some(edge =>
      edge.source === gmailNodes[0].name &&
      edge.target === `llm.inference#after_${gmailNodes[0].callsite_id}` &&
      edge.method === 'callsite_mediation'
    ));
    assert.equal(edgeByName.some(edge =>
      edge.source === gmailNodes[0].name &&
      edge.target === 'llm.inference' &&
      edge.method === 'type_check'
    ), false);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('FCG does not cap call-site mediation nodes by default', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-callsite-unlimited-'));

  try {
    const calls = Array.from({ length: 12 }, (_, index) =>
      `Use \`gmail.message.get\` for email step ${index + 1}.`
    ).join('\n');
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: callsite-unlimited-skill
description: Test uncapped call-sites.
version: 0.1.0
---

${calls}
`,
      'utf-8'
    );

    const analyzer = new SkillFCGAnalyzer({
      mode: 'quick',
      semanticLlm: false
    });
    const result = await analyzer.analyze(tempDir);
    const toolCallsites = result.nodes.filter(node => node.canonical_name === 'gmail.message.get');
    const mediationNodes = result.nodes.filter(node =>
      node.canonical_name === 'llm.inference' &&
      /^llm\.inference#(?:before|after)_call_\d{3}$/.test(node.name)
    );

    assert.equal(toolCallsites.length, 12);
    assert.equal(mediationNodes.length, 24);
    assert.ok(result.nodes.some(node => node.name === 'llm.inference#after_call_012'));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('doc-flow treats table definitions and passive fragments as context, not action flow', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-definition-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: definition-skill
description: Test definition gating.
version: 0.1.0
---

| Status | Meaning |
|--------|---------|
| \`promoted\` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |

When a lesson is ready, write the lesson to \`memory.md\`.
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, { semanticLlm: false });
    const actionSteps = result.nodes.filter(node => node.semanticKind === 'doc_step');
    const contexts = result.nodes.filter(node => node.semanticKind === 'doc_definition');

    assert.ok(contexts.some(node => node.instructionText.includes('Elevated to CLAUDE.md')));
    assert.equal(actionSteps.some(node => node.instructionText.includes('AGENTS.md')), false);
    assert.equal(actionSteps.some(node => node.instructionText.includes('copilot-instructions.md')), false);
    assert.ok(actionSteps.some(node => node.formal_semantics?.operation_type === 'write' && node.instructionText.includes('write the lesson')));
    assert.equal(
      result.edges.some(edge => edge.source.includes('promoted') || edge.target.includes('promoted')),
      false
    );
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('SKILL.md semantic anchor keeps Situation to Action table rows as grounded route nodes', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-skill-anchor-route-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: skill-anchor-route
description: Test SKILL route extraction.
version: 0.1.0
---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to \`.learnings/ERRORS.md\` |
| User corrects you | Log to \`.learnings/LEARNINGS.md\` with category \`correction\` |
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, { semanticLlm: false });
    const routeNodes = result.nodes.filter(node =>
      node.location?.file === 'SKILL.md' &&
      node.source_context?.source_role === 'semantic_anchor' &&
      node.formal_semantics?.evidence?.method?.includes('skill_anchor_route')
    );

    assert.equal(result.nodes.some(node => node.name.startsWith('rule.trigger.')), false);
    assert.equal(result.nodes.some(node => node.name.startsWith('rule.policy.')), false);
    assert.ok(routeNodes.some(node =>
      node.instructionText.includes('Command/operation fails') &&
      node.formal_semantics.conditions.some(condition => condition.text === 'Command/operation fails') &&
      node.formal_semantics.targets.some(target => target.value === '.learnings/ERRORS.md')
    ));
    assert.ok(routeNodes.every(node => node.semanticKind === 'doc_step'));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('semantic LLM gate can convert a candidate into context-only node without flow edges', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-doc-flow-llm-context-'));

  try {
    fs.writeFileSync(
      path.join(tempDir, 'SKILL.md'),
      `---
name: llm-context-gate-skill
description: Test LLM context-only gate.
version: 0.1.0
---

Read \`memory.md\`.
`,
      'utf-8'
    );

    const skillData = parseSkill(tempDir);
    const result = await extractDocumentFlow(skillData, null, {
      semanticLlm: true,
      semanticRefiner: async () => JSON.stringify({
        classification: 'definition',
        actionability: 'context_only',
        grammar: 'SVC description of a referenced document, not an imperative runtime action',
        completed_sentence: 'The referenced item is memory.md.',
        confidence: 0.88,
        reason: 'The test refiner marked this as documentation context.'
      })
    });

    const contextNode = result.nodes.find(node => node.semanticKind === 'doc_definition');
    assert.ok(contextNode);
    assert.equal(contextNode.excludeFromFlow, true);
    assert.equal(contextNode.semantic_gate.actionability, 'context_only');
    assert.equal(result.nodes.some(node => node.semanticKind === 'doc_step'), false);
    assert.equal(
      result.edges.some(edge => edge.source === contextNode.name || edge.target === contextNode.name),
      false
    );
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
