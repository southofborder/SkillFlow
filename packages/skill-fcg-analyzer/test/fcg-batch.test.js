const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  discoverSkills,
  runFcgBatch,
  buildFcgOutputPath,
  resolveOptions
} = require('../scripts/fcg-batch');

test('discovers grouped and ungrouped skills from similarity grouping', () => {
  const tmp = makeRunRoot();
  const all = discoverSkills(tmp.root, path.join(tmp.root, 'similarity'), 'all');
  const grouped = discoverSkills(tmp.root, path.join(tmp.root, 'similarity'), 'grouped');
  const ungrouped = discoverSkills(tmp.root, path.join(tmp.root, 'similarity'), 'ungrouped');

  assert.equal(all.length, 2);
  assert.equal(grouped.length, 1);
  assert.equal(ungrouped.length, 1);
  assert.equal(grouped[0].skill_id, 'skill_a');
  assert.equal(ungrouped[0].skill_id, 'skill_b');
});

test('runFcgBatch writes summary and uses skills output layout', async () => {
  const tmp = makeRunRoot();
  const options = {
    root: tmp.root,
    similarityRoot: path.join(tmp.root, 'similarity'),
    output: path.join(tmp.root, 'fcg'),
    scope: 'all',
    concurrency: 2,
    mode: 'full',
    refresh: false
  };

  const summary = await runFcgBatch(options, {
    analyzeSkill: async (skill, batchOptions) => {
      const fcgPath = buildFcgOutputPath(skill, batchOptions.output);
      fs.mkdirSync(path.dirname(fcgPath), { recursive: true });
      fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg(skill.skill_name), null, 2));
      return {
        skill_id: skill.skill_id,
        skill_name: skill.skill_name,
        group_id: skill.group_id,
        is_ungrouped: skill.is_ungrouped,
        zip_path: skill.zip_path,
        fcg_path: fcgPath,
        reused: false,
        source_count: 0,
        sink_count: 0,
        flow_count: 0
      };
    }
  });

  assert.equal(summary.total_skills, 2);
  assert.equal(summary.success_count, 2);
  assert.ok(fs.existsSync(path.join(options.output, 'fcg-summary.json')));
  assert.ok(fs.existsSync(path.join(options.output, 'fcg-summary.md')));
  assert.ok(summary.results.every(result => result.fcg_path.includes(`${path.sep}fcg${path.sep}skills${path.sep}`)));
});

test('runFcgBatch reuses existing FCG JSON when refresh is false', async () => {
  const tmp = makeRunRoot();
  const options = {
    root: tmp.root,
    similarityRoot: path.join(tmp.root, 'similarity'),
    output: path.join(tmp.root, 'fcg'),
    scope: 'grouped',
    concurrency: 1,
    mode: 'full',
    refresh: false
  };
  const skill = discoverSkills(tmp.root, options.similarityRoot, 'grouped')[0];
  const fcgPath = buildFcgOutputPath(skill, options.output);
  fs.mkdirSync(path.dirname(fcgPath), { recursive: true });
  fs.writeFileSync(fcgPath, JSON.stringify(minimalFcg(skill.skill_name), null, 2));

  const summary = await runFcgBatch(options, {
    createAnalyzer: () => ({
      analyze: async () => {
        throw new Error('analyzer should not be called');
      },
      cleanup: () => {}
    })
  });

  assert.equal(summary.success_count, 1);
  assert.equal(summary.reused_count, 1);
  assert.equal(summary.analyzed_count, 0);
});

test('batch resolve requires API key for default Markdown semantic gate', () => {
  const tmp = makeRunRoot();
  assert.throws(() => resolveOptions({
    root: tmp.root,
    llmApiKey: ''
  }), /LLM_API_KEY is required for FCG Markdown semantic gate/);

  const options = resolveOptions({
    root: tmp.root,
    llmApiKey: 'test-key'
  });
  assert.equal(options.root, tmp.root);
});

function makeRunRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'fcg-batch-'));
  const zips = path.join(root, 'zips');
  const similarity = path.join(root, 'similarity');
  fs.mkdirSync(zips, { recursive: true });
  fs.mkdirSync(similarity, { recursive: true });
  const zipA = path.join(zips, '00001_skill-a.zip');
  const zipB = path.join(zips, '00002_skill-b.zip');
  fs.writeFileSync(zipA, 'zip-a');
  fs.writeFileSync(zipB, 'zip-b');
  fs.writeFileSync(path.join(similarity, 'grouping.json'), JSON.stringify({
    skills: [
      { id: 'skill_a', skill_name: 'skill-a', zip_path: zipA, zip_name: path.basename(zipA) },
      { id: 'skill_b', skill_name: 'skill-b', zip_path: zipB, zip_name: path.basename(zipB) }
    ],
    groups: [
      { group_id: 'group_001', members: [{ skill_id: 'skill_a', skill_name: 'skill-a' }] }
    ],
    ungrouped: [
      { skill_id: 'skill_b', skill_name: 'skill-b' }
    ]
  }, null, 2));
  return { root };
}

function minimalFcg(skillName) {
  return {
    meta: { skill_name: skillName },
    nodes: [],
    edges: [],
    source_sink: { sources: [], sinks: [] },
    paths: { source_to_sink_paths: [], path_compression: { source_sink_pairs: [] } },
    statistics: {},
    security_profile: { sources: [], sinks: [], flows: [] }
  };
}
