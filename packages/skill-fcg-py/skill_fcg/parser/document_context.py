"""Documentation planning + source-context — port of src/parser/document-context.js.

``build_source_context`` is the shared grounding record every extracted node
carries (file/line/section + action_evidence). ``build_documentation_plan``
decides which markdown files are extraction sources vs review-only context
(the defect-4 changelog/license exclusion lives here).
"""

from __future__ import annotations

import os
import posixpath
import re

from .skill_parser import extract_sections


def build_documentation_plan(skill_data: dict | None = None,
                             readme_data: dict | None = None,
                             executable_files: list | None = None) -> dict:
    """Port of buildDocumentationPlan (document-context.js:5-57)."""
    skill_data = skill_data or {}
    executable_files = executable_files or []

    skill_doc = {
        "file": "SKILL.md",
        "content": str(skill_data.get("content") or ""),
        "sections": skill_data.get("sections") or [],
    }
    readme_doc = None
    if readme_data and readme_data.get("exists"):
        readme_content = str(readme_data.get("content") or "")
        readme_doc = {
            "file": "README.md",
            "content": readme_content,
            "sections": extract_sections(readme_content),
        }

    root_dir = skill_data.get("skillRootDir")
    all_markdown_docs = [
        doc for doc in (
            _read_markdown_doc(root_dir, file_path)
            for file_path in find_markdown_files(root_dir)
        )
        if doc and not is_entry_markdown(doc["file"])
    ]
    # Defect (4): changelog / release-history / license record past events, not
    # runtime actions. Keep for review context but never extract from them.
    markdown_docs = [d for d in all_markdown_docs if not is_non_instruction_markdown(d["file"])]
    non_instruction_docs = [d for d in all_markdown_docs if is_non_instruction_markdown(d["file"])]

    executable_source_files = [
        norm for norm in (
            normalize_source_path(root_dir, file_path) for file_path in executable_files
        )
        if norm
    ]
    has_primary_extraction_source = bool(markdown_docs) or bool(executable_source_files)

    extraction_docs = _dedupe_docs([
        {**skill_doc, "source_role": "semantic_anchor"},
        *({**doc, "source_role": "extraction_source"} for doc in markdown_docs),
    ])
    review_docs = [d for d in [skill_doc, readme_doc, *non_instruction_docs] if d]
    source_policy = {
        "semantic_review_default_enabled": True,
        "semantic_review_missing_key_behavior": "rule_fallback_warning",
        "skill_md_role": "semantic_anchor" if has_primary_extraction_source else "semantic_anchor_fallback",
        "readme_md_role": "review_only" if readme_doc else "absent",
        "extraction_doc_files": [doc["file"] for doc in extraction_docs],
        "executable_source_files": executable_source_files,
    }

    return {
        "extractionDocs": extraction_docs,
        "reviewDocs": review_docs,
        "sourcePolicy": source_policy,
        "documentationContext": {
            "source_policy": source_policy,
            "skill_context": _compact_doc_context(skill_doc, source_policy["skill_md_role"]),
            "readme_context": _compact_doc_context(readme_doc, "review_only") if readme_doc else None,
            "extraction_contexts": [
                _compact_doc_context(doc, doc.get("source_role") or "extraction_source")
                for doc in extraction_docs
            ],
        },
    }


def _dedupe_docs(docs: list) -> list:
    """Port of dedupeDocs (document-context.js:59-67) — first file wins."""
    by_file: dict[str, dict] = {}
    for doc in docs or []:
        file = normalize_doc_path(doc.get("file") or "")
        if not file or file in by_file:
            continue
        by_file[file] = {**doc, "file": file}
    return list(by_file.values())


def build_source_context(config: dict | None = None) -> dict:
    """Port of buildSourceContext (document-context.js:69-100)."""
    config = config or {}
    content = str(config.get("content") or "")
    lines = re.split(r"\r?\n", content)
    line_number = int(config.get("line") or 0)
    line_index = max(0, line_number - 1)
    source_line = str(config.get("sourceText") or _at(lines, line_index) or "").strip()
    before = [s for s in (l.strip() for l in lines[max(0, line_index - 2):line_index]) if s]
    after = [s for s in (l.strip() for l in lines[line_index + 1:line_index + 3]) if s]
    grounded = config.get("grounded") is not False

    return {
        "source_role": config.get("sourceRole") or "extraction_source",
        "source_type": config.get("sourceType") or "markdown",
        "file": normalize_doc_path(config.get("file") or ""),
        "line": line_number,
        "column": int(config.get("column") or 0),
        "section": config.get("section") or "",
        "source_line": source_line,
        "before": before,
        "after": after,
        "action_evidence": {
            "action": config.get("action") or "",
            "operation_type": config.get("operationType") or "",
            "snippet": str(config.get("actionSnippet") or source_line or "").strip(),
            "trigger": config.get("trigger") or "",
            "extraction_method": config.get("extractionMethod") or "",
            "grounded": grounded,
            "derived": bool(config.get("derived")),
            "requires_review": (not grounded) or bool(config.get("requiresReview")),
        },
    }


def find_markdown_files(root_dir: str | None) -> list:
    """Port of findMarkdownFiles (document-context.js:102-122)."""
    result: list[str] = []
    ignored = {"node_modules", ".git", ".svn", ".hg", "dist", "build", "coverage"}
    if not root_dir or not os.path.exists(root_dir):
        return result

    def walk(directory: str) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                full_path = os.path.join(directory, entry.name)
                if entry.is_dir():
                    if entry.name in ignored:
                        continue
                    walk(full_path)
                elif entry.name.lower().endswith(".md"):
                    result.append(full_path)

    walk(root_dir)
    return result


def _read_markdown_doc(root_dir: str, file_path: str) -> dict | None:
    """Port of readMarkdownDoc (document-context.js:124-136)."""
    try:
        rel_path = normalize_doc_path(os.path.relpath(file_path, root_dir))
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        return {"file": rel_path, "content": content, "sections": extract_sections(content)}
    except OSError:
        return None


def _compact_doc_context(doc: dict | None, role: str = "") -> dict:
    """Port of compactDocContext (document-context.js:138-152)."""
    doc = doc or {}
    content = str(doc.get("content") or "")
    return {
        "file": normalize_doc_path(doc.get("file") or ""),
        "role": role,
        "line_count": len(re.split(r"\r?\n", content)) if content else 0,
        "sections": [
            {
                "title": section.get("title") or "",
                "level": section.get("level") or 0,
                "startLine": section.get("startLine") or 0,
                "endLine": section.get("endLine") or 0,
            }
            for section in (doc.get("sections") or [])[:24]
        ],
        "preview": _truncate(content, 1600),
    }


def is_entry_markdown(file: str = "") -> bool:
    """Port of isEntryMarkdown (document-context.js:154-157)."""
    base = posixpath.basename(normalize_doc_path(file)).lower()
    return base in ("skill.md", "readme.md")


# Markdown files that record history/metadata rather than runtime instructions.
_NON_INSTRUCTION_MD = re.compile(
    r"(^|[/_-])(changelog|change-log|changes|history|releases?|release-notes|news|"
    r"license|licence|notice|authors|contributors|contributing|code-of-conduct)(\.[a-z]+)?$",
    re.IGNORECASE,
)


def is_non_instruction_markdown(file: str = "") -> bool:
    """Port of isNonInstructionMarkdown (document-context.js:163-167)."""
    norm = normalize_doc_path(file)
    base = re.sub(r"\.md$", "", posixpath.basename(norm).lower())
    return bool(_NON_INSTRUCTION_MD.search(base) or _NON_INSTRUCTION_MD.search(norm.lower()))


def normalize_doc_path(file_ref) -> str:
    """Port of normalizeDocPath (document-context.js:169-177)."""
    text = str(file_ref or "").strip()
    text = re.sub(r"^['\"`\s]+|['\"`\s]+$", "", text)
    text = re.sub(r"[),.;:!?]+$", "", text)
    text = text.replace("\\", "/")
    text = re.sub(r"^\./+", "", text)
    text = re.sub(r"/+", "/", text)
    return text


def normalize_source_path(root_dir: str, file_path: str) -> str:
    """Port of normalizeSourcePath (document-context.js:179-186)."""
    if not file_path:
        return ""
    raw = str(file_path or "")
    relative = os.path.relpath(raw, root_dir) if (root_dir and os.path.isabs(raw)) else raw
    return normalize_doc_path(relative)


def _truncate(value: str, maximum: int) -> str:
    text = str(value or "")
    return f"{text[:maximum]}..." if len(text) > maximum else text


def _at(seq: list, index: int) -> str:
    return seq[index] if 0 <= index < len(seq) else ""
