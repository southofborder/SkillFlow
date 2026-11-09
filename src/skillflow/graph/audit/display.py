"""Compact, read-only display of certified graph facts, not a new certificate.

The full Lean document remains the audit authority. This view removes its
record grammar and repeated labels, retaining existing fact IDs and locations.
"""
from __future__ import annotations

import json
from typing import Any

from skillflow.common.source_evidence import source_lines


def _term(text: str) -> list:
    """Decode the quoted-string/list grammar used by certified atomic units."""
    decoder = json.JSONDecoder()
    cursor = 0

    def read():
        nonlocal cursor
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text):
            raise ValueError("Incomplete controlled display record")
        if text[cursor] == '[':
            cursor += 1
            result = []
            while True:
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
                if cursor < len(text) and text[cursor] == ']':
                    cursor += 1
                    return result
                result.append(read())
        value, end = decoder.raw_decode(text, cursor)
        if type(value) is not str:
            raise ValueError("Controlled display atoms must be strings")
        cursor = end
        return value

    result = read()
    if type(result) is not list or text[cursor:].strip():
        raise ValueError("Invalid controlled display record")
    return result


def _optional(value):
    if value == ["未记录"]:
        return None
    if isinstance(value, list) and len(value) == 2 and value[0] == "记录值":
        return value[1]
    return value


def _value(record: list) -> Any:
    body = record[3:]
    if len(body) == 1:
        optional = record[2].endswith(("/source", "/identifier", "/semantic_name", "/literal_json", "/draft", "/condition"))
        value = _optional(body[0]) if optional else body[0]
        if record[2].endswith(("/metadata_json", "/literal_json")) and value is not None:
            return json.loads(value)
        return value
    names = {"kind": "type", "literal_json": "literal_value", "draft": "draft_instruction_id"}
    result = {}
    for child in body:
        if not isinstance(child, list) or len(child) < 4 or not isinstance(child[2], str):
            raise ValueError("Unsupported controlled display field")
        name = child[2].rsplit('/', 1)[-1]
        name = names.get(name, name)
        if name in result:
            raise ValueError("Duplicate controlled display field")
        result[name] = _value(child)
    return result


def _source_copy(text: Any, source: dict) -> dict | None:
    """Replace only an exact whole-line code copy, never infer a source link."""
    if not isinstance(text, str) or not text:
        return None
    for item in source["files"]:
        lines = source_lines(item["content"])
        offset = 0
        for start, line in enumerate(lines, 1):
            if item["content"].startswith(text, offset):
                joined = ""
                for end in range(start, len(lines) + 1):
                    joined += lines[end - 1]
                    if joined == text:
                        return {"file": item["path"], "start_line": start, "end_line": end}
                    if len(joined) >= len(text):
                        break
            offset += len(line)
    return None


def compact_facts(source: dict, document: dict) -> list[dict]:
    """Each displayed fact keeps its certified ID; no graph facts are inferred."""
    facts = []
    links = {link["use_ref"]: link for link in document.get("derived_links", [])}
    for unit in document["units"]:
        location = unit["graph_refs"]
        if unit["id"].endswith(":link") and len(location) == 1 and location[0] in links:
            value = links[location[0]]
        elif unit["text"].lstrip().startswith('['):
            record = _term(unit["text"])
            if len(record) < 4 or record[1] != unit["id"]:
                raise ValueError("Controlled display identity mismatch")
            value = _value(record)
            if record[2].endswith("/metadata_json") and isinstance(value, dict):
                span = _source_copy(value.get("script_content"), source)
                if span is not None:
                    value = dict(value)
                    value["script_content"] = {"exact_source_copy": span}
        else:
            # Non-Lean injected service fixtures still display their exact text.
            # Production controlled documents must use the certified grammar.
            if document.get("method") == "controlled":
                raise ValueError("Unsupported certified controlled display grammar")
            value = unit["text"]
        facts.append({"id": unit["id"], "basis": unit["basis"], "value": value})
    return facts


def audit_display(source: dict, document: dict) -> dict:
    return {
        "source_files": [{"path": item["path"], "lines": [
            [number, line] for number, line in enumerate(source_lines(item["content"]), 1)]}
            for item in source["files"]],
        "controlled_facts": compact_facts(source, document),
    }
