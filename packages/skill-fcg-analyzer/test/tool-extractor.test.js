const test = require('node:test');
const assert = require('node:assert/strict');

const { extractFromMarkdown, extractToolCalls } = require('../src/parser/tool-extractor');

test('extractFromMarkdown extracts tool calls and ignores markdown file refs', () => {
  const markdown = [
    '# Scenario',
    '',
    'Use `setup.md` for setup notes.',
    'Use `feishu_task_task.create` to create a task.',
    '',
    '| Intent | Tool |',
    '| --- | --- |',
    '| create app | feishu_bitable_app.create |',
    '',
    '```js',
    'feishu_bitable_app_table_field.list({',
    '  app_token: "app_xxx",',
    '  table_id: "tbl_xxx"',
    '});',
    '```'
  ].join('\n');

  const tools = extractFromMarkdown(markdown, [], 'SKILL.md');
  const names = new Set(tools.map(t => t.name));

  assert.equal(names.has('setup.md'), false);
  assert.equal(names.has('feishu_task_task.create'), true);
  assert.equal(names.has('feishu_bitable_app.create'), true);
  assert.equal(names.has('feishu_bitable_app_table_field.list'), true);

  const listTool = tools.find(t => t.name === 'feishu_bitable_app_table_field.list');
  assert.ok(listTool);
  assert.ok(listTool.input.app_token);
  assert.ok(listTool.input.table_id);
  assert.equal(listTool.source_context.action_evidence.grounded, true);
  assert.equal(listTool.source_context.action_evidence.extraction_method, 'code_call');
});

test('extractToolCalls preserves repeated tool call-sites with canonical names', () => {
  const skillData = {
    content: [
      '# Scenario',
      '',
      'Call `gmail.message.get` first.',
      'Then call `webhook.post`.',
      'Call `gmail.message.get` again for verification.'
    ].join('\n'),
    sections: []
  };

  const tools = extractToolCalls(skillData, null, []);
  const gmailCalls = tools.filter(tool => tool.canonical_name === 'gmail.message.get');
  const webhookCalls = tools.filter(tool => tool.canonical_name === 'webhook.post');

  assert.equal(gmailCalls.length, 2);
  assert.equal(webhookCalls.length, 1);
  assert.notEqual(gmailCalls[0].name, gmailCalls[1].name);
  assert.ok(gmailCalls.every(tool => /^gmail\.message\.get#call_\d{3}$/.test(tool.name)));
  assert.ok(gmailCalls.every(tool => tool.callsite_id && Number.isInteger(tool.callsite_order)));
  assert.ok(gmailCalls[0].callsite_order < gmailCalls[1].callsite_order);
  assert.equal(tools.filter(tool => tool.name === 'llm.inference').length, 1);
  assert.ok(gmailCalls.every(tool => tool.source_context?.action_evidence?.snippet));
});

test('extractToolCalls treats README as review-only and not a node source', () => {
  const skillData = {
    content: [
      '# Scenario',
      '',
      'Call `gmail.message.get` first.'
    ].join('\n'),
    sections: []
  };
  const readmeData = {
    exists: true,
    content: 'Call `webhook.post` from README only.'
  };

  const tools = extractToolCalls(skillData, readmeData, []);
  const names = new Set(tools.map(tool => tool.canonical_name || tool.name));

  assert.equal(names.has('gmail.message.get'), true);
  assert.equal(names.has('webhook.post'), false);
});

test('extractToolCalls ignores template markdown placeholder tool examples', () => {
  const skillData = {
    content: 'Call `gmail.message.get` first.',
    sections: []
  };
  const markdownDocs = [
    {
      file: 'SKILL.md',
      content: 'Call `gmail.message.get` first.',
      sections: []
    },
    {
      file: 'assets/SKILL-TEMPLATE.md',
      content: [
        '# Skill Template',
        '',
        '## Quick Reference',
        '',
        '| Command | Purpose |',
        '|---------|---------|',
        '| `./scripts/helper.sh` | [What it does] |',
        '| `scripts/validate.sh` | Validation checker |'
      ].join('\n'),
      sections: [{ title: 'Quick Reference', startLine: 3, endLine: 8 }]
    }
  ];

  const tools = extractToolCalls(skillData, null, [], { markdownDocs });
  const names = new Set(tools.map(tool => tool.canonical_name || tool.name));

  assert.equal(names.has('gmail.message.get'), true);
  assert.equal(names.has('helper.sh'), false);
  assert.equal(names.has('validate.sh'), false);
});

test('extractToolCalls keeps same tool on different lines as distinct call-sites', () => {
  const skillData = {
    content: [
      '# Scenario',
      '',
      '| Intent | Tool |',
      '| --- | --- |',
      '| read | gmail.message.get |',
      '| read duplicate | gmail.message.get |'
    ].join('\n'),
    sections: []
  };

  const tools = extractToolCalls(skillData, null, []);
  const gmailCalls = tools.filter(tool => tool.canonical_name === 'gmail.message.get');

  assert.equal(gmailCalls.length, 2);
  assert.notEqual(gmailCalls[0].name, gmailCalls[1].name);
});
