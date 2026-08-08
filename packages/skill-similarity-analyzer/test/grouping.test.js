const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const childProcess = require('child_process');
const AdmZip = require('adm-zip');

const {
  analyzeSimilarity,
  parseSkillZip,
  buildDocumentProfile,
  buildTfidfVectors,
  buildPairScores,
  buildStreamingPairIndex,
  pairKey,
  normalizeLlmSimilarityResult
} = require('../src/grouping');

function makeTempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'skill-similarity-'));
}

function createSkillZip(root, fileName, { name, description, body, readme = '', includeSkill = true }) {
  const zip = new AdmZip();
  if (includeSkill) {
    zip.addFile('skill/SKILL.md', Buffer.from(`---
name: ${name}
description: ${description}
---

${body}
`, 'utf-8'));
  }
  if (readme !== null) {
    zip.addFile('skill/README.md', Buffer.from(readme, 'utf-8'));
  }
  const zipPath = path.join(root, fileName);
  zip.writeZip(zipPath);
  return zipPath;
}

function namesByGroup(result) {
  return result.groups
    .map(group => group.members.map(member => member.skill_name).sort())
    .sort((a, b) => a[0].localeCompare(b[0]));
}

function scoreProfiles(profileA, profileB) {
  const vectors = buildTfidfVectors([profileA.textTokens, profileB.textTokens]);
  profileA.tfidfVector = vectors[0];
  profileB.tfidfVector = vectors[1];
  return buildPairScores([
    { id: 'skill_0001', profile: profileA },
    { id: 'skill_0002', profile: profileB }
  ])[0];
}

test('groups similar database and visualization skills while leaving unrelated skill ungrouped', async () => {
  const tempDir = makeTempDir();
  try {
    createSkillZip(tempDir, 'db-query.zip', {
      name: 'database-query-helper',
      description: 'Query and analyze SQL database tables',
      body: 'Use when users need to inspect database schemas, write SQL queries, validate rows, and summarize table records.',
      readme: '# Database query helper\nAnalyze SQL database schemas, inspect tables, generate queries, and report records from MySQL or PostgreSQL.'
    });
    createSkillZip(tempDir, 'db-design.zip', {
      name: 'database-schema-designer',
      description: 'Design and analyze SQL database schemas',
      body: 'Use when users need database schema modeling, SQL migration design, table validation, and record analysis.',
      readme: '# Database schema designer\nDesign SQL schemas, inspect database tables, generate migration reports, and validate records.'
    });
    createSkillZip(tempDir, 'chart-maker.zip', {
      name: 'chart-dashboard-maker',
      description: 'Generate charts and dashboards from data tables',
      body: 'Use when users need visualizations, charts, plots, dashboards, and reports from CSV or spreadsheet data.',
      readme: '# Chart dashboard maker\nVisualize CSV and spreadsheet data, generate charts, plot graphs, and build dashboard reports.'
    });
    createSkillZip(tempDir, 'chart-report.zip', {
      name: 'data-visualization-reporter',
      description: 'Visualize data with charts and dashboard reports',
      body: 'Use when users need chart reports, graph rendering, dashboard summaries, and spreadsheet visualization.',
      readme: '# Data visualization reporter\nGenerate charts, dashboards, plots, and report summaries from table data and CSV files.'
    });
    createSkillZip(tempDir, 'poetry.zip', {
      name: 'poetry-polisher',
      description: 'Rewrite and polish poems',
      body: 'Use when users need creative writing, poetry revision, metaphor polishing, and literary style edits.',
      readme: '# Poetry polisher\nRewrite poems, polish literary language, and improve creative writing style.'
    });

    const outputDir = path.join(tempDir, 'out');
    const result = await analyzeSimilarity([tempDir], { output: outputDir, threshold: 0.5, topK: 3 });
    const groups = namesByGroup(result);

    assert.equal(result.statistics.group_count, 2);
    assert.deepEqual(groups, [
      ['chart-dashboard-maker', 'data-visualization-reporter'],
      ['database-query-helper', 'database-schema-designer']
    ]);
    assert.deepEqual(result.ungrouped.map(item => item.skill_name), ['poetry-polisher']);
    assert.ok(fs.existsSync(path.join(outputDir, 'grouping.json')));
    assert.ok(fs.existsSync(path.join(outputDir, 'grouping.md')));
    assert.ok(fs.existsSync(path.join(outputDir, 'groups', 'group_001', 'group_manifest.json')));
    assert.ok(fs.existsSync(path.join(outputDir, 'ungrouped', 'poetry.zip')));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('missing README is accepted and marked on the skill profile', async () => {
  const tempDir = makeTempDir();
  try {
    const zipPath = createSkillZip(tempDir, 'no-readme.zip', {
      name: 'no-readme-skill',
      description: 'Analyze text data',
      body: 'Use when users need text analysis and summary reports.',
      readme: null
    });

    const parsed = parseSkillZip(zipPath);
    assert.equal(parsed.error, undefined);
    assert.equal(parsed.skill.readme_missing, true);

    const result = await analyzeSimilarity([zipPath], { output: path.join(tempDir, 'out') });
    assert.equal(result.skills[0].readme_missing, true);
    assert.equal(result.statistics.ungrouped_skill_count, 1);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('zip without SKILL.md is reported as an error and excluded from grouping', async () => {
  const tempDir = makeTempDir();
  try {
    createSkillZip(tempDir, 'valid.zip', {
      name: 'valid-skill',
      description: 'Analyze files',
      body: 'Use when users need file analysis.',
      readme: '# Valid skill\nAnalyze files.'
    });
    createSkillZip(tempDir, 'invalid.zip', {
      name: 'invalid-skill',
      description: 'Missing skill',
      body: '',
      readme: '# Invalid',
      includeSkill: false
    });

    const result = await analyzeSimilarity([tempDir], { output: path.join(tempDir, 'out') });
    assert.equal(result.statistics.valid_skills, 1);
    assert.equal(result.errors.length, 1);
    assert.match(result.errors[0].reason, /SKILL\.md not found/);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('semantic scorer refines only candidate pairs and falls back on failure', async () => {
  const tempDir = makeTempDir();
  try {
    const zipA = createSkillZip(tempDir, 'a.zip', {
      name: 'alpha-data-tool',
      description: 'Analyze structured data',
      body: 'Analyze structured data and generate reports.',
      readme: '# Alpha\nAnalyze structured data and report insights.'
    });
    const zipB = createSkillZip(tempDir, 'b.zip', {
      name: 'beta-data-tool',
      description: 'Analyze structured datasets',
      body: 'Analyze datasets and generate reports.',
      readme: '# Beta\nAnalyze structured datasets and report insights.'
    });
    const zipC = createSkillZip(tempDir, 'c.zip', {
      name: 'gamma-image-tool',
      description: 'Render image assets',
      body: 'Render image assets and visual previews.',
      readme: '# Gamma\nRender image assets and visual previews.'
    });

    let calls = 0;
    const result = await analyzeSimilarity([zipA, zipB, zipC], {
      output: path.join(tempDir, 'out'),
      threshold: 0.8,
      topK: 1,
      semanticLlm: true,
      semanticScorer: async (a, b) => {
        calls += 1;
        if (a.name.includes('gamma') || b.name.includes('gamma')) {
          throw new Error('stub failure');
        }
        return { similarity: 1, reason: 'same data reporting capability' };
      }
    });

    assert.ok(calls > 0);
    const refined = result.similarity_pairs.find(pair =>
      pair.source_name === 'alpha-data-tool' && pair.target_name === 'beta-data-tool'
    );
    assert.equal(refined.llm_score, 1);
    assert.ok(result.errors.some(error => String(error.reason).includes('stub failure')));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('normalizeLlmSimilarityResult accepts gpt-style textual scales and boolean strings', () => {
  const result = normalizeLlmSimilarityResult('{"similarity":"high","reason":"Same capability","has_contradiction":"no","contradiction_reason":""}');
  assert.equal(result.similarity, 0.8);
  assert.equal(result.has_contradiction, false);
});

test('normalizeLlmSimilarityResult accepts numeric strings and fenced json', () => {
  const result = normalizeLlmSimilarityResult('```json\n{"similarity":"0.95","reason":"Close match","has_contradiction":"false","contradiction_reason":""}\n```');
  assert.equal(result.similarity, 0.95);
  assert.equal(result.has_contradiction, false);
});

test('polarity penalty lowers high-overlap opposite preference text', () => {
  const positive = buildDocumentProfile({
    skillName: 'tv-positive',
    description: 'I like watching TV',
    skillContent: 'Use when the user likes watching TV shows.',
    readmeContent: '# TV preference\nI like watching TV and recommend television shows.'
  });
  const negative = buildDocumentProfile({
    skillName: 'tv-negative',
    description: 'I do not like watching TV',
    skillContent: 'Use when the user does not like watching TV shows.',
    readmeContent: '# TV preference\nI do not like watching TV and avoid television shows.'
  });

  const pair = scoreProfiles(positive, negative);
  assert.ok(pair.base_rule_score > pair.rule_score);
  assert.ok(pair.components.contradiction_penalty >= 0.35);
  assert.ok(pair.components.polarity_conflicts.some(conflict =>
    conflict.shared_objects.includes('tv') || conflict.shared_actions.includes('watch')
  ));
});

test('external send versus do-not-send does not form a group', async () => {
  const tempDir = makeTempDir();
  try {
    createSkillZip(tempDir, 'send-files.zip', {
      name: 'file-sender',
      description: 'Send files to an external API',
      body: 'Use when users need to send files to an external API and upload file data.',
      readme: '# File sender\nSend files to an external API and upload file data for processing.'
    });
    createSkillZip(tempDir, 'local-files.zip', {
      name: 'local-file-handler',
      description: 'Do not send files to an external API',
      body: 'Use when users must not send files externally and should avoid uploading file data.',
      readme: '# Local file handler\nDo not send files to an external API. Avoid uploading file data.'
    });

    const result = await analyzeSimilarity([tempDir], { output: path.join(tempDir, 'out'), threshold: 0.5, topK: 2 });
    assert.equal(result.statistics.group_count, 0);
    const pair = result.similarity_pairs.find(item =>
      item.source_name === 'file-sender' || item.target_name === 'file-sender'
    );
    assert.ok(pair);
    assert.ok(pair.components.contradiction_penalty >= 0.5);
    assert.equal(pair.components.polarity_conflicts[0].shared_actions.includes('send'), true);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('Chinese credential allow versus forbid creates a high-risk polarity conflict', () => {
  const allow = buildDocumentProfile({
    skillName: 'credential-reader',
    description: '读取用户凭据',
    skillContent: '当任务需要读取用户凭据和令牌时使用。',
    readmeContent: '# 凭据读取\n读取用户凭据、密钥和令牌。'
  });
  const forbid = buildDocumentProfile({
    skillName: 'credential-guard',
    description: '禁止读取用户凭据',
    skillContent: '禁止读取用户凭据和令牌，不得访问密钥。',
    readmeContent: '# 凭据保护\n禁止读取用户凭据、密钥和令牌。'
  });

  const pair = scoreProfiles(allow, forbid);
  assert.ok(pair.components.contradiction_penalty >= 0.5);
  assert.ok(pair.components.polarity_conflicts.some(conflict =>
    conflict.shared_actions.includes('read') &&
    (conflict.shared_objects.includes('credential') || conflict.shared_objects.includes('user_info'))
  ));
});

test('LLM contradiction flag applies an extra penalty and prevents grouping', async () => {
  const tempDir = makeTempDir();
  try {
    const zipA = createSkillZip(tempDir, 'api-upload.zip', {
      name: 'api-upload',
      description: 'Upload files to API',
      body: 'Upload files to an API for analysis.',
      readme: '# API upload\nUpload files to API for analysis.'
    });
    const zipB = createSkillZip(tempDir, 'api-local.zip', {
      name: 'api-local',
      description: 'Upload files to API',
      body: 'Upload files to an API for analysis.',
      readme: '# API upload\nUpload files to API for analysis.'
    });

    const result = await analyzeSimilarity([zipA, zipB], {
      output: path.join(tempDir, 'out'),
      threshold: 0.8,
      topK: 1,
      semanticLlm: true,
      semanticScorer: async () => ({
        similarity: 1,
        reason: 'Textually similar',
        has_contradiction: true,
        contradiction_reason: 'Stubbed contradiction'
      })
    });

    assert.equal(result.statistics.group_count, 0);
    const pair = result.similarity_pairs[0];
    assert.equal(pair.llm_has_contradiction, true);
    assert.equal(pair.llm_contradiction_reason, 'Stubbed contradiction');
    assert.equal(pair.components.llm_contradiction_penalty, 0.35);
    assert.ok(pair.similarity_score < 0.8);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('CLI writes grouping outputs for zip directory input', () => {
  const tempDir = makeTempDir();
  try {
    createSkillZip(tempDir, 'db-a.zip', {
      name: 'db-a',
      description: 'Query SQL database',
      body: 'Query SQL database tables and analyze records.',
      readme: '# DB A\nQuery SQL database tables and analyze records.'
    });
    createSkillZip(tempDir, 'db-b.zip', {
      name: 'db-b',
      description: 'Analyze SQL database',
      body: 'Analyze SQL database tables and query records.',
      readme: '# DB B\nAnalyze SQL database tables and query records.'
    });

    const outputDir = path.join(tempDir, 'cli-out');
    childProcess.execFileSync(
      process.execPath,
      [path.join(__dirname, '..', 'src', 'index.js'), 'group', tempDir, '--output', outputDir, '--threshold', '0.5'],
      { cwd: path.join(__dirname, '..') }
    );

    const grouping = JSON.parse(fs.readFileSync(path.join(outputDir, 'grouping.json'), 'utf-8'));
    assert.equal(grouping.statistics.group_count, 1);
    assert.ok(fs.existsSync(path.join(outputDir, 'groups', 'group_001', 'db-a.zip')));
    assert.ok(fs.existsSync(path.join(outputDir, 'groups', 'group_001', 'db-b.zip')));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('streaming pair index keeps threshold edges and per-skill TopK without retaining every pair', () => {
  const profiles = [
    buildDocumentProfile({
      skillName: 'database-query',
      description: 'Query SQL database',
      skillContent: 'Query SQL database tables and analyze records.',
      readmeContent: '# DB query'
    }),
    buildDocumentProfile({
      skillName: 'database-design',
      description: 'Design SQL database',
      skillContent: 'Design SQL database schemas and analyze records.',
      readmeContent: '# DB design'
    }),
    buildDocumentProfile({
      skillName: 'poetry',
      description: 'Polish poems',
      skillContent: 'Rewrite poetry and polish metaphors.',
      readmeContent: '# Poetry'
    })
  ];
  const vectors = buildTfidfVectors(profiles.map(profile => profile.textTokens));
  profiles.forEach((profile, index) => {
    profile.tfidfVector = vectors[index];
  });

  const skills = profiles.map((profile, index) => ({
    id: `skill_000${index + 1}`,
    profile
  }));

  const index = buildStreamingPairIndex(skills, { threshold: 0.5, topK: 1 });
  assert.equal(index.pairCount, 3);
  assert.equal(index.allPairs, null);
  assert.ok(index.candidatePairs.length <= 3);
  for (const pairs of index.topKBySkill.values()) {
    assert.ok(pairs.length <= 1);
  }
  assert.ok(index.thresholdPairKeys.size >= 1);
});

test('candidate pair index avoids exhaustive scoring while retaining clear feature matches', () => {
  const definitions = [
    ['sql-query-alpha', 'Query SQL database tables and analyze records.'],
    ['sql-query-beta', 'Query SQL database records and generate reports.'],
    ['browser-alpha', 'Search webpages with Playwright and collect links.'],
    ['browser-beta', 'Search browser pages with Playwright and fetch links.'],
    ['poetry', 'Rewrite poems and polish metaphors for writers.'],
    ['music', 'Compose melodies and arrange audio tracks.']
  ];
  const profiles = definitions.map(([skillName, body]) => buildDocumentProfile({
    skillName,
    description: body,
    skillContent: body,
    readmeContent: `# ${skillName}\n${body}`
  }));
  const vectors = buildTfidfVectors(profiles.map(profile => profile.textTokens));
  profiles.forEach((profile, index) => {
    profile.tfidfVector = vectors[index];
  });
  const skills = profiles.map((profile, index) => ({
    id: `skill_000${index + 1}`,
    skill_name: definitions[index][0],
    zip_name: `${definitions[index][0]}.zip`,
    profile
  }));

  const index = buildStreamingPairIndex(skills, {
    threshold: 0.5,
    topK: 2,
    pairStrategy: 'candidate',
    fallbackNeighborWindow: 0
  });
  const candidateKeys = new Set(index.candidatePairs.map(pairKey));

  assert.equal(index.strategy, 'candidate');
  assert.ok(index.scoredPairCount < 15);
  assert.ok(index.candidateStats.featureCount > 0);
  assert.ok(candidateKeys.has('skill_0001::skill_0002'));
  assert.ok(candidateKeys.has('skill_0003::skill_0004'));
});

test('semantic cache prevents repeated scorer calls across runs', async () => {
  const tempDir = makeTempDir();
  try {
    const zipA = createSkillZip(tempDir, 'a.zip', {
      name: 'alpha-data-tool',
      description: 'Analyze structured data',
      body: 'Analyze structured data and generate reports.',
      readme: '# Alpha\nAnalyze structured data and report insights.'
    });
    const zipB = createSkillZip(tempDir, 'b.zip', {
      name: 'beta-data-tool',
      description: 'Analyze structured datasets',
      body: 'Analyze datasets and generate reports.',
      readme: '# Beta\nAnalyze structured datasets and report insights.'
    });
    const cachePath = path.join(tempDir, 'semantic-cache.jsonl');
    let calls = 0;
    const options = {
      output: path.join(tempDir, 'out'),
      threshold: 0.8,
      topK: 1,
      semanticLlm: true,
      semanticCachePath: cachePath,
      semanticScorer: async () => {
        calls += 1;
        return { similarity: 1, reason: 'same data reporting capability' };
      }
    };

    await analyzeSimilarity([zipA, zipB], options);
    await analyzeSimilarity([zipA, zipB], { ...options, output: path.join(tempDir, 'out2') });

    assert.equal(calls, 1);
    assert.ok(fs.existsSync(cachePath));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
