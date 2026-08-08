// Parity driver: read a JSON array of shell lines from argv[2], run the REAL JS
// classifyShellCommandLine on each, print [[descriptors]] to stdout. Paired with
// test_parity_shell_classifier.py to lock the regex-heavy segment/target logic.
const fs = require('fs');
const { classifyShellCommandLine } = require('../../../skill-fcg-analyzer/src/parser/shell-command-classifier');

const lines = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
process.stdout.write(JSON.stringify(lines.map(classifyShellCommandLine)));
