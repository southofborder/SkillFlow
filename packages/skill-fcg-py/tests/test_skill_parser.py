"""Mirror key behaviors of src/parser/skill-parser.js (front-matter split, sections)."""

import os
import tempfile

import pytest

from skill_fcg.parser.skill_parser import (
    extract_sections,
    find_executable_files,
    parse_skill,
)


def _write_skill(tmp: str, body: str) -> str:
    with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8") as handle:
        handle.write(body)
    return tmp


def test_parse_skill_splits_front_matter_and_body():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, "---\nname: demo\ndescription: A demo skill\nversion: 2.1.0\n---\n# Intro\nhello\n")
        parsed = parse_skill(tmp)

    assert parsed["name"] == "demo"
    assert parsed["description"] == "A demo skill"
    assert parsed["version"] == "2.1.0"
    # Body starts after the closing delimiter's newline (gray-matter semantics).
    assert parsed["content"].startswith("# Intro")
    assert len(parsed["sections"]) == 1
    assert parsed["sections"][0]["title"] == "Intro"
    assert parsed["sections"][0]["startLine"] == 1


def test_parse_skill_requires_name_and_description():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, "---\nname: only-name\n---\nbody\n")
        with pytest.raises(ValueError):
            parse_skill(tmp)


def test_parse_skill_defaults_version():
    with tempfile.TemporaryDirectory() as tmp:
        _write_skill(tmp, "---\nname: n\ndescription: d\n---\nbody\n")
        parsed = parse_skill(tmp)
    assert parsed["version"] == "1.0.0"


def test_extract_sections_line_numbers():
    content = "# A\nbody a\n## B\nbody b\n"
    sections = extract_sections(content)
    assert [s["title"] for s in sections] == ["A", "B"]
    assert sections[0]["startLine"] == 1
    assert sections[0]["endLine"] == 2  # line index where B's heading appears
    assert sections[1]["startLine"] == 3


def test_find_executable_files_by_extension_and_shebang():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "node_modules"))
        with open(os.path.join(tmp, "run.sh"), "w", encoding="utf-8") as handle:
            handle.write("echo hi\n")
        with open(os.path.join(tmp, "tool.py"), "w", encoding="utf-8") as handle:
            handle.write("#!/usr/bin/env node\nconsole.log(1)\n")
        with open(os.path.join(tmp, "notes.txt"), "w", encoding="utf-8") as handle:
            handle.write("just text\n")
        with open(os.path.join(tmp, "node_modules", "dep.js"), "w", encoding="utf-8") as handle:
            handle.write("module.exports = {}\n")

        found = {os.path.basename(p) for p in find_executable_files(tmp)}

    assert "run.sh" in found          # extension match
    assert "tool.py" in found          # shebang match
    assert "notes.txt" not in found    # neither
    assert "dep.js" not in found       # inside ignored node_modules
