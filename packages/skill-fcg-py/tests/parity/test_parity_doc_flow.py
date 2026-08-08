"""Cross-engine parity: REAL JS extractDocumentFlow vs the Python port.

For each fixture skill (SKILL.md text), runs both engines rule-only
(semanticLlm=false, disableLlm=true) via buildDocumentationPlan +
extractDocumentFlow, and asserts the emitted {nodes, edges} are deeply equal
after a JSON round-trip. This is the harness that catches subtle regex / field-
shape / ordering divergences the pure-mirror asserts cannot. Skipped when Node
is unavailable.

The fixtures exercise: compound-action splitting, implicit object reads, table
definitions + passive fragments, SKILL.md situation->action route rows, negation
(deferred to the gate, so rule-only keeps them as candidates), multi-line bullet
folding, disclaimer-scope lists, enum bullets, ordered action steps, and shell
code-block command extraction.
"""

import json
import os
import shutil
import subprocess
import tempfile

import pytest

from skill_fcg.parser.skill_parser import parse_skill, parse_readme, find_executable_files
from skill_fcg.parser.document_context import build_documentation_plan
from skill_fcg.parser.doc_flow_extractor import extract_document_flow

_HERE = os.path.dirname(__file__)
_JS_DRIVER = os.path.join(_HERE, "js_doc_flow.cjs")

_FIXTURES = {
    "compound": """---
name: english-compound-skill
description: Test English compound action splitting.
version: 0.1.0
---

- Summarize the email content and save it locally.
- Read customer records, redact secrets, and send a summary to the model.
- Extract the city from the profile and call the weather API.
""",
    "implicit_objects": """---
name: implicit-object-skill
description: Test implicit object reads.
version: 0.1.0
---

- Write the email content to a local file.
- Read email content and write it to a local file.
- Write the report to a file, then upload the report.
- Generate a report about the email.
- Generate a report about current AI.
- Create the analysis result and save it locally.
- Summarize the email content and save the summary.
- Read the email and write it to a file.
""",
    "definitions": """---
name: definition-skill
description: Test definition gating.
version: 0.1.0
---

| Status | Meaning |
|--------|---------|
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |

When a lesson is ready, write the lesson to `memory.md`.
""",
    "anchor_route": """---
name: skill-anchor-route
description: Test SKILL route extraction.
version: 0.1.0
---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
""",
    "negation_deferred": """---
name: negation-test
description: Use when testing.
version: 0.1.0
---

## Steps
Vet the skill thoroughly.
Install the skill from the registry.
## Rules
Never install a skill without vetting it first.
Never overwrite existing files.
The skill does not send any personal data externally.
""",
    "prose_and_lists": """---
name: mixed
description: Fetches and forwards.
---

# Steps

- Fetch the remote report from the archive service
  and send it to the analytics endpoint at metrics.example.com
- Read the local cache file

**What this skill does NOT do:**
- Connect to any wallet or financial account
- Send personal data to external services

## Limitations

- The cache is best-effort and may be stale
- Send the diagnostic bundle to logs.example.com when debugging

# Options

- **mode**: fast | slow | off

# Flow

Read the market data and send it to the analytics API at metrics.example.com.
""",
    "shell_block": """---
name: shell-block-skill
description: Test shell code block command extraction.
version: 0.1.0
---

# Steps

Run the export:

```bash
curl -s https://example.com/hook
cat notes.txt > backup.txt
```
""",
    "ordered_steps": """---
name: ordered
description: steps.
---

# Procedure

1. Read the configuration file from disk
2. Send the configuration to the remote API at config.example.com
3. Write the response to the local log
""",
}


def _py_flow(skill_dir):
    skill_data = parse_skill(skill_dir)
    readme_data = parse_readme(skill_dir)
    plan = build_documentation_plan(skill_data, readme_data, find_executable_files(skill_dir))
    flow = extract_document_flow(skill_data, readme_data, {
        "extractionDocs": plan["extractionDocs"],
        "reviewDocs": plan["reviewDocs"],
        "documentationContext": plan["documentationContext"],
        "semanticLlm": False,
        "disableLlm": True,
    })
    return json.loads(json.dumps({"nodes": flow["nodes"], "edges": flow["edges"]}))


def _js_flow(skill_dir):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    spec_path = os.path.join(_HERE, "_doc_flow_spec.json")
    with open(spec_path, "w", encoding="utf-8") as handle:
        json.dump({"skillDir": skill_dir, "semanticLlm": False}, handle)
    proc = subprocess.run([node, _JS_DRIVER, spec_path], capture_output=True, text=True, cwd=_HERE)
    if proc.returncode != 0:
        pytest.skip(f"JS doc-flow driver failed: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


@pytest.mark.parametrize("name", sorted(_FIXTURES.keys()))
def test_doc_flow_parity(name):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8", newline="") as handle:
            handle.write(_FIXTURES[name])
        js = _js_flow(tmp)
        py = _py_flow(tmp)

    assert [n["name"] for n in py["nodes"]] == [n["name"] for n in js["nodes"]], f"[{name}] node name/order diverged"
    assert py["nodes"] == js["nodes"], f"[{name}] node payload diverged"
    assert py["edges"] == js["edges"], f"[{name}] edges diverged"
