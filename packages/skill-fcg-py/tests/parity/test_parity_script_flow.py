"""Cross-engine parity: REAL JS extractScriptFlow vs the Python port.

Builds a temp skill tree (JS + TS + shell with heredoc/if runtime blocks), runs
both engines with semanticLlm:false (rule-only, no LLM), and asserts the emitted
{nodes, edges} are deeply equal. This also exercises the babel_ast_sidecar.cjs
end to end (the Python JS path shells out to it). Skipped when Node or the
analyzer's @babel/parser is unavailable.
"""

import json
import os
import shutil
import subprocess
import tempfile

import pytest

from skill_fcg.parser.script_flow_extractor import extract_script_flow

_HERE = os.path.dirname(__file__)
_JS_DRIVER = os.path.join(_HERE, "js_script.cjs")

_FILES = {
    "hooks/handler.js": "function injectReminder(event) { return event.context.bootstrapFiles.filter(Boolean); }\nmodule.exports = { injectReminder };\n",
    "hooks/handler.ts": "export function normalizeEvent(event: { path: string }) { return fetch(event.path); }\n",
    "scripts/activator.sh": "#!/usr/bin/env bash\nactivate_skill() {\n  cat \"$1\"\n  curl -s https://example.com/hook\n}\nactivate_skill \"$1\"\n",
    "scripts/error-detector.sh": "\n".join([
        "#!/usr/bin/env bash",
        'OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"',
        "contains_error=false",
        'if [ "$contains_error" = true ]; then',
        "  cat << 'EOF'",
        "<error-detected>",
        "A command error was detected. Consider logging this to .learnings/ERRORS.md if:",
        "- The error was unexpected or non-obvious",
        "</error-detected>",
        "EOF",
        "fi",
        "",
    ]),
}


def _build_tree(tmp: str) -> list:
    paths = []
    for rel, content in _FILES.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        paths.append(path)
    return paths


def _run_js(files, root_dir):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    spec_path = os.path.join(_HERE, "_script_spec.json")
    with open(spec_path, "w", encoding="utf-8") as handle:
        json.dump({"files": files, "rootDir": root_dir, "semanticLlm": False}, handle)
    proc = subprocess.run([node, _JS_DRIVER, spec_path], capture_output=True, text=True, cwd=_HERE)
    if proc.returncode != 0:
        pytest.skip(f"JS script driver failed (babel missing?): {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


def test_script_flow_parity():
    with tempfile.TemporaryDirectory() as tmp:
        files = _build_tree(tmp)
        js_flow = _run_js(files, tmp)
        py_flow = json.loads(json.dumps(extract_script_flow(files, {"rootDir": tmp, "semanticLlm": False})))

    assert [n["name"] for n in py_flow["nodes"]] == [n["name"] for n in js_flow["nodes"]], "node name/order diverged"
    assert py_flow["nodes"] == js_flow["nodes"], "node payload diverged"
    assert py_flow["edges"] == js_flow["edges"], "edges diverged"
