const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');

const {
  createDoePathReport,
  renderPathReportMarkdown,
  writeDoePathReport,
  recoverSourceQuote,
  readZipTextEntry
} = require('../src/path-report');

test('DOE path report naturalizes scoped paths with zip source lines and grouped markdown', () => {
  const root = makeRunRoot();
  const zipPath = path.join(root, 'zips', '00001-self.zip');
  writeStoredZip(zipPath, {
    'assets/LEARNINGS.md': [
      '# Learnings',
      'Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md',
      'Extracted as a reusable skill'
    ].join('\n')
  });
  const fcgPath = path.join(root, 'fcg', 'skills', 'skill_0001-00001-self-fcg.json');
  const doePath = path.join(root, 'doe', 'skills', 'skill_0001-00001-self-doe.json');
  fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg(zipPath)), 'utf8');
  fs.writeFileSync(doePath, JSON.stringify(minimalDoe()), 'utf8');

  const report = createDoePathReport({ root });
  const markdown = renderPathReportMarkdown(report);

  assert.equal(report.summary.path_count, 2);
  assert.equal(report.paths.some(item => item.assessment_id === 'doe_000003'), false);
  assert.equal(report.paths[0].source_quote.source, 'zip');
  assert.equal(report.paths[0].source_quote.text, 'Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md');
  assert.ok(report.paths.find(item => item.label_subtype === 'path').audit_notes.includes('path_label_metadata_only'));
  assert.ok(report.paths[0].audit_notes.includes('model_context_expected_flow'));
  assert.match(markdown, /label_subtype=path/);
  assert.match(markdown, /doe_000001/);
  assert.match(markdown, /doe_000002/);
  assert.match(markdown, /2 assessments/);

  const written = writeDoePathReport(report, {
    output: path.join(root, 'doe', 'reports', 'self-report.md'),
    format: 'both'
  });
  assert.ok(fs.existsSync(written.markdown));
  assert.ok(fs.existsSync(written.json));
  assert.equal(path.extname(written.markdown), '.md');
  assert.equal(path.extname(written.json), '.json');
});

test('source recovery falls back to FCG context when zip line is unavailable', () => {
  const quote = recoverSourceQuote({
    zipPath: '',
    node: {
      location: { file: 'missing.md', line: 9 },
      source_context: { source_line: 'Fallback source context line' },
      instructionText: 'Instruction fallback'
    }
  });

  assert.equal(quote.source, 'fcg');
  assert.equal(quote.text, 'Fallback source context line');
});

test('zip text reader resolves absolute extracted paths by suffix', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'doe-path-zip-'));
  try {
    const zipPath = path.join(root, 'skill.zip');
    writeStoredZip(zipPath, {
      'references/hooks-setup.md': 'line 1\nCreate `.codex/settings.json`:'
    });
    const text = readZipTextEntry(zipPath, 'C:/Temp/skill/references/hooks-setup.md');
    assert.match(text, /settings\.json/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

function makeRunRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'doe-path-report-'));
  fs.mkdirSync(path.join(root, 'fcg', 'skills'), { recursive: true });
  fs.mkdirSync(path.join(root, 'doe', 'skills'), { recursive: true });
  fs.mkdirSync(path.join(root, 'zips'), { recursive: true });
  return root;
}

function minimalFcg(zipPath) {
  return {
    meta: {
      skill_name: 'self-improvement',
      input_source: zipPath
    },
    nodes: [{
      id: 'node_1',
      name: 'doc.step.assets_learnings.l2.read.agents',
      location: { file: 'assets/LEARNINGS.md', line: 2, section: 'Status Definitions' },
      instructionText: 'AGENTS.md',
      source_context: {
        file: 'assets/LEARNINGS.md',
        line: 2,
        source_line: 'Embedded fallback line',
        action_evidence: {
          action: 'read',
          operation_type: 'read',
          snippet: 'AGENTS.md',
          trigger: 'AGENTS.md',
          grounded: true
        }
      }
    }],
    security_profile: {
      label_flows: [
        labelFlow('lf_doc', 'file_content.document', 'document'),
        labelFlow('lf_path', 'file_content.path', 'path')
      ],
      observations: [{
        observation_id: 'obs_1',
        node_id: 'node_1',
        node_name: 'doc.step.assets_learnings.l2.read.agents',
        boundary: {
          data_surface: 'llm_context',
          receiver_scope: 'model_provider',
          retention_scope: 'transient',
          trust_boundary: 'model_provider'
        },
        label_flow_ids: ['lf_doc', 'lf_path']
      }]
    }
  };
}

function labelFlow(id, label, subtype) {
  return {
    label_flow_id: id,
    current_node: 'node_1',
    node_path: ['node_1'],
    node_names: ['doc.step.assets_learnings.l2.read.agents'],
    label: {
      label,
      category: label.split('.')[0],
      subtype
    }
  };
}

function minimalDoe() {
  return {
    statistics: {
      assessment_count: 3,
      potential_doe_count: 1,
      requires_review_count: 2
    },
    assessments: [
      assessment('doe_000001', 'lf_doc', 'file_content.document', 'document', true, true),
      assessment('doe_000002', 'lf_path', 'file_content.path', 'path', false, true),
      assessment('doe_000003', 'lf_doc', 'file_content.document', 'document', false, false)
    ]
  };
}

function assessment(id, flowId, label, subtype, potentialDoe, requiresReview) {
  return {
    assessment_id: id,
    observation_id: 'obs_1',
    label_flow_id: flowId,
    label,
    label_category: label.split('.')[0],
    label_subtype: subtype,
    observation_node_id: 'node_1',
    observation_node_name: 'doc.step.assets_learnings.l2.read.agents',
    boundary_crossed: true,
    doe_score: potentialDoe ? 0.62 : 0.2,
    exposure_score: 0.9,
    necessity_score: 0.55,
    rule_necessity_score: 0.55,
    local_necessity: { action_input_need: 0.95, receiver_semantic_need: 0.55 },
    global_necessity: { task_need: 1 },
    necessity_basis: 'receiver_semantic_need',
    potential_doe: potentialDoe,
    requires_review: requiresReview
  };
}

function writeStoredZip(zipPath, entries) {
  const chunks = [];
  for (const [entryName, content] of Object.entries(entries)) {
    const name = Buffer.from(entryName, 'utf8');
    const data = Buffer.from(content, 'utf8');
    const header = Buffer.alloc(30);
    header.writeUInt32LE(0x04034b50, 0);
    header.writeUInt16LE(20, 4);
    header.writeUInt16LE(0, 6);
    header.writeUInt16LE(0, 8);
    header.writeUInt32LE(0, 10);
    header.writeUInt32LE(0, 14);
    header.writeUInt32LE(data.length, 18);
    header.writeUInt32LE(data.length, 22);
    header.writeUInt16LE(name.length, 26);
    header.writeUInt16LE(0, 28);
    chunks.push(header, name, data);
  }
  fs.writeFileSync(zipPath, Buffer.concat(chunks));
}
