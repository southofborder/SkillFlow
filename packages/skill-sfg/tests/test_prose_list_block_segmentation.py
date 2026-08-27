"""Mirror of test/prose-list-block-segmentation.test.js.

Uses build_documentation_plan (extraction/review docs) + extract_document_flow
with semanticLlm False / disableLlm True — the pure rule path.
"""

import os
import re
import tempfile

from skill_sfg.parser.skill_parser import parse_skill, parse_readme, find_executable_files
from skill_sfg.parser.document_context import build_documentation_plan
from skill_sfg.parser.doc_flow_extractor import extract_document_flow


def _doc_flow_for(dir_):
    skill_data = parse_skill(dir_)
    readme_data = parse_readme(dir_)
    plan = build_documentation_plan(skill_data, readme_data, find_executable_files(dir_))
    flow = extract_document_flow(skill_data, readme_data, {
        "extractionDocs": plan["extractionDocs"],
        "reviewDocs": plan["reviewDocs"],
        "documentationContext": plan["documentationContext"],
        "semanticLlm": False,
        "disableLlm": True,
    })
    return flow


def _write(dir_, body):
    with open(os.path.join(dir_, "SKILL.md"), "w", encoding="utf-8", newline="") as handle:
        handle.write(body)


def test_multi_line_bullet_folds_into_one_node():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: folder
description: Fetches and forwards.
---

# Steps

- Fetch the remote report from the archive service
  and send it to the analytics endpoint at metrics.example.com
- Read the local cache file
""")
        flow = _doc_flow_for(dir_)
    merged = next((n for n in flow["nodes"] if re.search(r"send it to|metrics\.example\.com", n.get("instructionText") or "", re.IGNORECASE)), None)
    assert merged is not None
    fetch_node = next((n for n in flow["nodes"] if re.search(r"Fetch the remote report", n.get("instructionText") or "", re.IGNORECASE)), None)
    assert fetch_node is not None
    assert merged["location"]["line"] == fetch_node["location"]["line"]


def test_list_items_inherit_disclaimer_scope_from_lead_in():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: scoped
description: Local only.
---

# Overview

**What this skill does NOT do:**
- Connect to any wallet or financial account
- Send personal data to external services
- Execute real trades on the network
""")
        flow = _doc_flow_for(dir_)
    scoped = [n for n in flow["nodes"] if re.search(r"wallet|personal data|real trades", n.get("instructionText") or "", re.IGNORECASE)]
    assert len(scoped) > 0
    assert all(n.get("excludeFromFlow") or n.get("operationType") in ("context", "guard") for n in scoped)
    leak = [n for n in scoped if n.get("operationType") in ("external_egress", "invoke_tool")]
    assert len(leak) == 0


def test_explicit_does_not_do_lead_in_suppresses_imperative_bullets():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: strong
description: local only.
---

# Boundaries

**What this skill does NOT do:**
- Connect to any wallet or financial account
- Send personal data to external services
- Execute real trades on the network
""")
        flow = _doc_flow_for(dir_)
    bullets = [n for n in flow["nodes"] if re.search(r"wallet|personal data|real trades", n.get("instructionText") or "", re.IGNORECASE)]
    assert len(bullets) == 3
    assert all(n.get("excludeFromFlow") or n.get("operationType") in ("context", "guard") for n in bullets)
    leak = [n for n in bullets if n.get("operationType") in ("external_egress", "invoke_tool")]
    assert len(leak) == 0


def test_imperative_bullet_in_soft_negation_section_keeps_reverse_protection():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: soft
description: has limitations section.
---

## Limitations

- The cache is best-effort and may be stale
- Send the diagnostic bundle to logs.example.com when debugging
""")
        flow = _doc_flow_for(dir_)
    cache_node = next((n for n in flow["nodes"] if re.search(r"cache is best-effort|stale", n.get("instructionText") or "", re.IGNORECASE)), None)
    assert cache_node is not None
    assert cache_node.get("excludeFromFlow") or cache_node.get("operationType") in ("context", "guard")
    send_node = next((n for n in flow["nodes"] if re.search(r"logs\.example\.com|diagnostic bundle", n.get("instructionText") or "", re.IGNORECASE)), None)
    assert send_node is not None
    assert (not send_node.get("excludeFromFlow")
            and send_node.get("role") != "negated_disclaimer"
            and send_node.get("operationType") not in ("context", "guard")), f"got {send_node.get('operationType')}"


def test_plain_prose_lines_unaffected_by_block_segmentation():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: prose
description: prose only.
---

# Flow

Read the market data and send it to the analytics API at metrics.example.com.

Summarize the findings for the user.
""")
        flow = _doc_flow_for(dir_)
    egress = [n for n in flow["nodes"] if n.get("operationType") == "external_egress" and re.search(r"metrics\.example\.com|analytics", n.get("instructionText") or "", re.IGNORECASE)]
    assert len(egress) >= 1


def test_enum_style_bullets_remain_context():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: enum
description: options.
---

# Options

- **mode**: fast | slow | off
- **retries**: 0 | 1 | 3
""")
        flow = _doc_flow_for(dir_)
    enum_nodes = [n for n in flow["nodes"] if re.search(r"mode|retries", n.get("instructionText") or "", re.IGNORECASE)]
    assert len(enum_nodes) > 0
    assert all(n.get("excludeFromFlow") for n in enum_nodes)


def test_ordered_action_steps_each_become_their_own_node():
    with tempfile.TemporaryDirectory() as dir_:
        _write(dir_, """---
name: ordered
description: steps.
---

# Procedure

1. Read the configuration file from disk
2. Send the configuration to the remote API at config.example.com
3. Write the response to the local log
""")
        flow = _doc_flow_for(dir_)
    action_lines = set(
        (n.get("location") or {}).get("line")
        for n in flow["nodes"] if not n.get("excludeFromFlow")
    )
    assert len(action_lines) >= 3
    egress = [n for n in flow["nodes"] if n.get("operationType") == "external_egress" and re.search(r"config\.example\.com", n.get("instructionText") or "", re.IGNORECASE)]
    assert len(egress) >= 1
