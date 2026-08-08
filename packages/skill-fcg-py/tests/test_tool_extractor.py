"""Mirror of test/tool-extractor.test.js — locks the Python port to the JS spec.

Each test corresponds 1:1 to a node:test case in the JS suite so a green run
here means the extractor produces the same node set/shape on the same input.
"""

from skill_fcg.parser.tool_extractor import extract_from_markdown, extract_tool_calls


def test_extract_from_markdown_extracts_calls_and_ignores_md_refs():
    markdown = "\n".join([
        "# Scenario",
        "",
        "Use `setup.md` for setup notes.",
        "Use `feishu_task_task.create` to create a task.",
        "",
        "| Intent | Tool |",
        "| --- | --- |",
        "| create app | feishu_bitable_app.create |",
        "",
        "```js",
        "feishu_bitable_app_table_field.list({",
        '  app_token: "app_xxx",',
        '  table_id: "tbl_xxx"',
        "});",
        "```",
    ])

    tools = extract_from_markdown(markdown, [], "SKILL.md")
    names = {t["name"] for t in tools}

    assert "setup.md" not in names
    assert "feishu_task_task.create" in names
    assert "feishu_bitable_app.create" in names
    assert "feishu_bitable_app_table_field.list" in names

    list_tool = next(t for t in tools if t["name"] == "feishu_bitable_app_table_field.list")
    assert list_tool
    assert "app_token" in list_tool["input"]
    assert "table_id" in list_tool["input"]
    assert list_tool["source_context"]["action_evidence"]["grounded"] is True
    assert list_tool["source_context"]["action_evidence"]["extraction_method"] == "code_call"


def test_extract_tool_calls_preserves_repeated_call_sites():
    skill_data = {
        "content": "\n".join([
            "# Scenario",
            "",
            "Call `gmail.message.get` first.",
            "Then call `webhook.post`.",
            "Call `gmail.message.get` again for verification.",
        ]),
        "sections": [],
    }

    tools = extract_tool_calls(skill_data, None, [])
    gmail_calls = [t for t in tools if t["canonical_name"] == "gmail.message.get"]
    webhook_calls = [t for t in tools if t["canonical_name"] == "webhook.post"]

    assert len(gmail_calls) == 2
    assert len(webhook_calls) == 1
    assert gmail_calls[0]["name"] != gmail_calls[1]["name"]
    assert all(__import__("re").fullmatch(r"gmail\.message\.get#call_\d{3}", t["name"]) for t in gmail_calls)
    assert all(t.get("callsite_id") and isinstance(t.get("callsite_order"), int) for t in gmail_calls)
    assert gmail_calls[0]["callsite_order"] < gmail_calls[1]["callsite_order"]
    assert len([t for t in tools if t["name"] == "llm.inference"]) == 1
    assert all(t.get("source_context", {}).get("action_evidence", {}).get("snippet") for t in gmail_calls)


def test_extract_tool_calls_readme_is_review_only():
    skill_data = {
        "content": "\n".join(["# Scenario", "", "Call `gmail.message.get` first."]),
        "sections": [],
    }
    readme_data = {"exists": True, "content": "Call `webhook.post` from README only."}

    tools = extract_tool_calls(skill_data, readme_data, [])
    names = {t.get("canonical_name") or t.get("name") for t in tools}

    assert "gmail.message.get" in names
    assert "webhook.post" not in names


def test_extract_tool_calls_ignores_template_placeholder_examples():
    skill_data = {"content": "Call `gmail.message.get` first.", "sections": []}
    markdown_docs = [
        {"file": "SKILL.md", "content": "Call `gmail.message.get` first.", "sections": []},
        {
            "file": "assets/SKILL-TEMPLATE.md",
            "content": "\n".join([
                "# Skill Template",
                "",
                "## Quick Reference",
                "",
                "| Command | Purpose |",
                "|---------|---------|",
                "| `./scripts/helper.sh` | [What it does] |",
                "| `scripts/validate.sh` | Validation checker |",
            ]),
            "sections": [{"title": "Quick Reference", "startLine": 3, "endLine": 8}],
        },
    ]

    tools = extract_tool_calls(skill_data, None, [], {"markdownDocs": markdown_docs})
    names = {t.get("canonical_name") or t.get("name") for t in tools}

    assert "gmail.message.get" in names
    assert "helper.sh" not in names
    assert "validate.sh" not in names


def test_extract_tool_calls_same_tool_different_lines_distinct_call_sites():
    skill_data = {
        "content": "\n".join([
            "# Scenario",
            "",
            "| Intent | Tool |",
            "| --- | --- |",
            "| read | gmail.message.get |",
            "| read duplicate | gmail.message.get |",
        ]),
        "sections": [],
    }

    tools = extract_tool_calls(skill_data, None, [])
    gmail_calls = [t for t in tools if t["canonical_name"] == "gmail.message.get"]

    assert len(gmail_calls) == 2
    assert gmail_calls[0]["name"] != gmail_calls[1]["name"]
