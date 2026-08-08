"""SKILL.md / README parsing — port of src/parser/skill-parser.js.

Mirrors ``parseSkill`` / ``extractSections`` / ``parseReadme`` /
``findExecutableFiles`` exactly. JS uses gray-matter (v4), which wraps js-yaml,
for the YAML front matter. We reproduce gray-matter's *body split* semantics
(so line numbers match) and parse the front-matter block with PyYAML —
js-yaml and PyYAML agree on the flat scalars skill front matter uses
(name/description/version). YAML 1.1 corner cases (e.g. ``yes``→bool) could in
principle differ; front-matter values here are strings, so it does not bite.
"""

from __future__ import annotations

import os
import re

import yaml

# gray-matter's ``content`` is everything after the closing ``---`` delimiter,
# with exactly one leading newline (and an optional preceding CR) stripped.
# Anchored, DOTALL between the delimiters. Delimiters must sit on their own line.
_FRONT_MATTER_RE = re.compile(r"^---[^\S\r\n]*\r?\n(.*?)\r?\n---[^\S\r\n]*(?:\r?\n|$)", re.DOTALL)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

EXECUTABLE_EXTENSIONS = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh", ".bash"}

_IGNORED_DIRS = {"node_modules", ".git", ".svn", ".hg", "dist", "build", "coverage"}

_SHEBANG_RE = re.compile(r"^#!.*\b(?:node|bash|sh)\b")


def parse_skill(skill_root_dir: str) -> dict:
    """Port of parseSkill (skill-parser.js:10-36)."""
    skill_md_path = os.path.join(skill_root_dir, "SKILL.md")
    if not os.path.exists(skill_md_path):
        raise FileNotFoundError(f"SKILL.md not found at: {skill_md_path}")

    with open(skill_md_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    data, body = _split_front_matter(content)

    # gray-matter itself does not validate; the JS parseSkill does.
    if not data.get("name") or not data.get("description"):
        raise ValueError('SKILL.md must have front matter with "name" and "description" fields')

    sections = extract_sections(body)

    return {
        "name": data["name"],
        "description": data["description"],
        "version": data.get("version") or "1.0.0",
        "content": body,
        "sections": sections,
        "skillRootDir": skill_root_dir,
    }


def _split_front_matter(text: str) -> tuple[dict, str]:
    """Split gray-matter-style YAML front matter from the body.

    Fidelity notes vs gray-matter v4:
    - Front matter is recognized only when the string opens with ``---`` on its
      own line and a matching closing ``---`` line exists.
    - ``content`` is the slice after the closing delimiter's trailing newline —
      i.e. gray-matter strips exactly one newline after ``---``. Line numbers in
      ``extract_sections`` are relative to this body, matching JS.
    - The front-matter block is parsed with PyYAML (js-yaml equivalent); an
      empty/``null`` document yields ``{}``.
    """
    if not text.startswith("---"):
        return {}, text

    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    front = match.group(1)
    body = text[match.end():]
    # gray-matter feeds js-yaml the block between the delimiters. Our regex
    # consumes the newline before the closing ``---``; restore it so PyYAML's
    # block-scalar chomping (folded ``>`` / literal ``|``) matches js-yaml,
    # which keeps the clip trailing newline.
    data = yaml.safe_load(front + "\n")
    if not isinstance(data, dict):
        data = {}
    return data, body


def extract_sections(content: str) -> list:
    """Port of extractSections (skill-parser.js:43-86)."""
    lines = content.split("\n")
    sections: list = []
    current_section: dict | None = None
    current_content: list[str] = []

    for i, line in enumerate(lines):
        heading = _HEADING_RE.match(line)
        if heading:
            if current_section is not None:
                sections.append({
                    **current_section,
                    "content": "\n".join(current_content),
                    "endLine": i,
                })
            current_section = {
                "title": heading.group(2).strip(),
                "level": len(heading.group(1)),
                "startLine": i + 1,
            }
            current_content = []
        elif current_section is not None:
            current_content.append(line)

    if current_section is not None:
        sections.append({
            **current_section,
            "content": "\n".join(current_content),
            "endLine": len(lines),
        })

    return sections


def parse_readme(skill_root_dir: str) -> dict | None:
    """Port of parseReadme (skill-parser.js:93-105)."""
    readme_path = os.path.join(skill_root_dir, "README.md")
    if not os.path.exists(readme_path):
        return None
    with open(readme_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    return {"content": content, "exists": True}


def find_executable_files(skill_root_dir: str) -> list:
    """Port of findExecutableFiles (skill-parser.js:114-145)."""
    executable_files: list[str] = []

    def walk_dir(directory: str) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                full_path = os.path.join(directory, entry.name)
                if entry.is_dir():
                    if entry.name in _IGNORED_DIRS:
                        continue
                    walk_dir(full_path)
                elif _is_executable_source_file(full_path):
                    executable_files.append(full_path)

    walk_dir(skill_root_dir)
    return executable_files


def _is_executable_source_file(file_path: str) -> bool:
    """Port of isExecutableSourceFile (skill-parser.js:147-156)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in EXECUTABLE_EXTENSIONS:
        return True
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            first_line = handle.readline().rstrip("\n").rstrip("\r")
    except OSError:
        return False
    return bool(_SHEBANG_RE.match(first_line))
