"""Tool-call extraction — faithful port of src/parser/tool-extractor.js.

Scans the selected markdown extraction docs (JSON blocks, JS blocks, tables,
inline code) and JS/TS files for ``a.b.c(...)``-style tool references, then
deduplicates by call-site and assigns per-call-site identities
(``name#call_NNN``). Output node dicts keep the exact JS keys so downstream
parity diffs are structural.

Fidelity note: JS ``String.localeCompare`` (used only as a last-resort sort
tie-break when file+line+column are all equal) is approximated here with
Python code-point comparison. Distinct call-sites differ by line/column, so the
tie-break rarely fires; the golden parity harness will flag any ordering drift.
"""

from __future__ import annotations

import functools
import json
import os
import re

from .document_context import build_source_context, normalize_doc_path

TOOL_NAME_REGEX = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\b")
TOOL_CALL_REGEX = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\s*\(")

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)
_JS_BLOCK_RE = re.compile(r"```(?:javascript|js)\s*\n(.*?)```", re.DOTALL)
_INLINE_RE = re.compile(r"`([^`]+)`")

_MD_FILE_REF_RE = re.compile(r"\.(md|txt|json|yaml|yml)$", re.IGNORECASE)
_TOOL_NAME_FULL_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+$")
_KEY_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def extract_tool_calls(skill_data: dict, readme_data: dict | None,
                       script_files: list, options: dict | None = None) -> list:
    """Port of extractToolCalls (tool-extractor.js:16-39)."""
    options = options or {}
    tools: list = []
    markdown_docs = options.get("markdownDocs")
    if not isinstance(markdown_docs, list):
        markdown_docs = [{
            "file": "SKILL.md",
            "content": skill_data.get("content"),
            "sections": skill_data.get("sections") or [],
        }]

    for doc in markdown_docs:
        if _is_template_or_example_markdown(doc.get("file") or "", doc.get("content") or ""):
            continue
        tools.extend(extract_from_markdown(
            doc.get("content"), doc.get("sections") or [], doc.get("file") or "SKILL.md"))

    root_dir = options.get("rootDir") or skill_data.get("skillRootDir")
    for script_file in script_files:
        if not _is_javascript_like_file(script_file):
            continue
        tools.extend(_extract_from_js_file(script_file, root_dir))

    tools.append(_create_implicit_llm_node())

    return _assign_call_site_identity(deduplicate_call_sites(tools))


def extract_from_markdown(content, sections, file_name) -> list:
    """Port of extractFromMarkdown (tool-extractor.js:49-67)."""
    content = content or ""
    tools: list = []

    for block in _extract_json_blocks(content):
        tools.extend(_extract_tools_from_json_block(
            block["content"], block["line"], file_name, sections, content))

    for block in _extract_js_blocks(content):
        tools.extend(_extract_tools_from_code(
            block["content"], block["line"], file_name, sections,
            source_content=content, source_type="markdown_code_block"))

    tools.extend(_extract_tools_from_tables(content, file_name, sections))
    tools.extend(_extract_tools_from_inline(content, file_name, sections))

    return tools


def _create_implicit_llm_node() -> dict:
    """Port of createImplicitLlmNode (tool-extractor.js:69-91)."""
    return {
        "name": "llm.inference",
        "action": "inference",
        "type": "builtin_call",
        "description": "Implicit LLM call: Skill content (SKILL.md) is injected into LLM context when activated",
        "input": {
            "skill_content": {"type": "string", "required": True, "example": "Full SKILL.md content"},
            "user_query": {"type": "string", "required": True},
            "context": {"type": "string", "required": False},
        },
        "output": {
            "response": {"type": "string"},
            "actions": {"type": "array"},
        },
        "location": {
            "file": "SKILL.md",
            "line": 1,
            "section": "Implicit: OpenClaw Skill Activation",
        },
        "isCritical": True,
    }


def _extract_json_blocks(content: str) -> list:
    """Port of extractJsonBlocks (tool-extractor.js:93-105)."""
    blocks = []
    for match in _JSON_BLOCK_RE.finditer(content):
        line = _line_number_at(content, match.start())
        parsed = _try_parse_json(match.group(1))
        if parsed is not None:
            blocks.append({"content": parsed, "line": line})
    return blocks


def _extract_js_blocks(content: str) -> list:
    """Port of extractJsBlocks (tool-extractor.js:107-116)."""
    blocks = []
    for match in _JS_BLOCK_RE.finditer(content):
        line = _line_number_at(content, match.start())
        blocks.append({"content": match.group(1), "line": line})
    return blocks


def _extract_tools_from_json_block(json_value, line, file_name, sections, source_content="") -> list:
    """Port of extractToolsFromJsonBlock (tool-extractor.js:127-172)."""
    tools: list = []

    def visitor(value):
        if not value or not isinstance(value, dict):
            return
        tool_name = _infer_tool_name_from_json_object(value)
        if not tool_name:
            return
        action = _get_action_from_tool_name_or_json(tool_name, value)
        input_sig = _extract_input_from_json_object(value)
        output = infer_output_signature(tool_name, action)
        section = _find_section_for_line(sections, line)

        tools.append({
            "name": tool_name,
            "canonical_name": tool_name,
            "action": action,
            "type": "tool_call",
            "extraction_method": "json_block",
            "description": value.get("description") or value.get("desc") or "",
            "input": input_sig,
            "output": output,
            "location": {
                "file": file_name,
                "line": line,
                "column": 0,
                "section": section,
            },
            "source_context": _build_tool_source_context(
                content=source_content, file_name=file_name, line=line, section=section,
                action=action, operation_type=action, extraction_method="json_block",
                trigger=tool_name,
                action_snippet=json.dumps(value, separators=(",", ":"), ensure_ascii=False)[:240],
                source_type="markdown_json_block"),
        })

    _walk_json(json_value, visitor)
    return tools


def _walk_json(value, visitor) -> None:
    """Port of walkJson (tool-extractor.js:174-183)."""
    visitor(value)
    if isinstance(value, list):
        for item in value:
            _walk_json(item, visitor)
        return
    if isinstance(value, dict):
        for v in value.values():
            _walk_json(v, visitor)


def _infer_tool_name_from_json_object(json_obj: dict) -> str | None:
    """Port of inferToolNameFromJsonObject (tool-extractor.js:185-205)."""
    candidates = [
        json_obj.get("tool"),
        json_obj.get("tool_name"),
        json_obj.get("function"),
        json_obj.get("api"),
        json_obj.get("name"),
    ]
    for candidate in candidates:
        normalized = _normalize_tool_name(candidate)
        if normalized:
            return normalized

    if isinstance(json_obj.get("action"), str) and isinstance(json_obj.get("module"), str):
        normalized = _normalize_tool_name(f"{json_obj['module']}.{json_obj['action']}")
        if normalized:
            return normalized

    return None


def _get_action_from_tool_name_or_json(tool_name: str, json_obj: dict | None = None) -> str:
    """Port of getActionFromToolNameOrJson (tool-extractor.js:207-213)."""
    json_obj = json_obj or {}
    action = json_obj.get("action")
    if isinstance(action, str) and action.strip():
        return action.strip()
    parts = tool_name.split(".")
    return parts[-1] or "unknown"


def _extract_input_from_json_object(json_obj: dict) -> dict:
    """Port of extractInputFromJsonObject (tool-extractor.js:215-227)."""
    ignored = {"tool", "tool_name", "function", "api", "name", "action", "description", "desc"}
    input_sig: dict = {}
    for key, value in json_obj.items():
        if key in ignored:
            continue
        input_sig[key] = {"type": _infer_type(value), "required": True, "example": value}
    return input_sig


def _extract_tools_from_code(code, base_line, file_name, sections,
                             source_content=None, source_type=None) -> list:
    """Port of extractToolsFromCode (tool-extractor.js:229-276)."""
    tools: list = []
    source_content = code if source_content is None else source_content
    source_type = source_type or "script"

    for match in TOOL_CALL_REGEX.finditer(code):
        tool_name = _normalize_tool_name(match.group(1))
        if not tool_name:
            continue

        line = base_line + code[:match.start()].count("\n")
        action = tool_name.split(".")[-1]
        input_sig = _extract_input_from_call(code, match.end() - 1)
        output = infer_output_signature(tool_name, action)
        column = _column_number_at(code, match.start())
        section = _find_section_for_line(sections, line)

        tools.append({
            "name": tool_name,
            "canonical_name": tool_name,
            "action": action,
            "type": "tool_call",
            "extraction_method": "code_call",
            "input": input_sig,
            "output": output,
            "location": {
                "file": file_name,
                "line": line,
                "column": column,
                "section": section,
            },
            "source_context": _build_tool_source_context(
                content=source_content, file_name=file_name, line=line, column=column,
                section=section, action=action, operation_type=action,
                extraction_method="code_call", trigger=match.group(0),
                action_snippet=match.group(0), source_type=source_type),
        })

    return tools


def _extract_tools_from_tables(content, file_name, sections) -> list:
    """Port of extractToolsFromTables (tool-extractor.js:278-327)."""
    tools: list = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        if re.match(r"^\s*\|?[-:\s|]+\|?\s*$", line):
            continue
        if _is_placeholder_line(line) or _is_template_or_example_section(sections, i + 1):
            continue

        for match in TOOL_NAME_REGEX.finditer(line):
            tool_name = _normalize_tool_name(match.group(1))
            if not tool_name:
                continue
            action = tool_name.split(".")[-1]
            section = _find_section_for_line(sections, i + 1)
            tools.append({
                "name": tool_name,
                "canonical_name": tool_name,
                "action": action,
                "type": "tool_call",
                "extraction_method": "table_ref",
                "input": infer_input_signature(tool_name, action),
                "output": infer_output_signature(tool_name, action),
                "location": {
                    "file": file_name,
                    "line": i + 1,
                    "column": match.start() + 1,
                    "section": section,
                },
                "source_context": _build_tool_source_context(
                    content=content, file_name=file_name, line=i + 1, column=match.start() + 1,
                    section=section, action=action, operation_type=action,
                    extraction_method="table_ref", trigger=match.group(0),
                    action_snippet=line.strip(), source_type="markdown_table"),
            })

    return tools


def _extract_tools_from_inline(content, file_name, sections) -> list:
    """Port of extractToolsFromInline (tool-extractor.js:329-370)."""
    tools: list = []
    for match in _INLINE_RE.finditer(content):
        candidate = _normalize_tool_name(match.group(1))
        if not candidate:
            continue
        line = _line_number_at(content, match.start())
        if _is_placeholder_line(_line_at(content, line)) or _is_template_or_example_section(sections, line):
            continue
        action = candidate.split(".")[-1]
        column = _column_number_at(content, match.start())
        section = _find_section_for_line(sections, line)
        tools.append({
            "name": candidate,
            "canonical_name": candidate,
            "action": action,
            "type": "tool_call",
            "extraction_method": "inline_ref",
            "input": infer_input_signature(candidate, action),
            "output": infer_output_signature(candidate, action),
            "location": {
                "file": file_name,
                "line": line,
                "column": column,
                "section": section,
            },
            "source_context": _build_tool_source_context(
                content=content, file_name=file_name, line=line, column=column,
                section=section, action=action, operation_type=action,
                extraction_method="inline_ref", trigger=match.group(0),
                action_snippet=match.group(0), source_type="markdown_inline"),
        })
    return tools


def _is_template_or_example_markdown(file_name: str = "", content: str = "") -> bool:
    """Port of isTemplateOrExampleMarkdown (tool-extractor.js:372-378)."""
    file = _normalize_path_for_output(file_name).lower()
    if re.search(r"\b(template|example|sample|fixture)\b", file):
        return True
    first_lines = "\n".join(re.split(r"\r?\n", str(content or ""))[:24]).lower()
    return bool(re.search(r"\b(template|example|sample)\b", first_lines) and
                re.search(r"\b(placeholders?|replace|what it does|example output)\b", first_lines))


def _is_template_or_example_section(sections=None, line: int = 0) -> bool:
    """Port of isTemplateOrExampleSection (tool-extractor.js:380-383)."""
    title = str(_find_section_for_line(sections or [], line) or "").lower()
    return bool(re.search(r"\b(template|example|sample|placeholder)\b", title))


def _is_placeholder_line(line: str = "") -> bool:
    """Port of isPlaceholderLine (tool-extractor.js:385-389)."""
    text = str(line or "").lower()
    return bool(
        re.search(r"\[[^\]]*(what it does|description|purpose|tool|command|todo|replace)[^\]]*\]", text) or
        re.search(r"\b(example|sample|template|placeholder)\b", text)
    )


def _extract_from_js_file(file_path: str, root_dir: str = "") -> list:
    """Port of extractFromJsFile (tool-extractor.js:397-408)."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        return _extract_tools_from_code(
            content, 1, _normalize_path_for_output(file_path, root_dir), [],
            source_content=content, source_type="script")
    except OSError:
        print(f"Warning: Could not read JS file: {file_path}")
        return []


def _build_tool_source_context(*, content, file_name, line, column=0, section="",
                               action, operation_type, extraction_method, trigger,
                               action_snippet, source_type) -> dict:
    """Port of buildToolSourceContext (tool-extractor.js:410-437)."""
    return build_source_context({
        "content": content,
        "file": file_name,
        "line": line,
        "column": column,
        "section": section,
        "action": action,
        "operationType": operation_type,
        "extractionMethod": extraction_method,
        "trigger": trigger,
        "actionSnippet": action_snippet,
        "sourceType": source_type,
        "grounded": bool(action_snippet or trigger),
    })


def _extract_input_from_call(code: str, open_paren_index: int) -> dict:
    """Port of extractInputFromCall (tool-extractor.js:439-453)."""
    input_sig: dict = {}
    object_literal = _extract_first_object_literal_arg(code, open_paren_index)
    if not object_literal:
        return input_sig
    for pair in _parse_object_literal_pairs(object_literal):
        input_sig[pair["key"]] = {
            "type": pair["type"],
            "required": True,
            "example": pair["example"],
        }
    return input_sig


def _extract_first_object_literal_arg(code: str, open_paren_index: int) -> str | None:
    """Port of extractFirstObjectLiteralArg (tool-extractor.js:455-502)."""
    i = open_paren_index + 1
    while i < len(code) and code[i].isspace():
        i += 1
    if i >= len(code) or code[i] != "{":
        return None

    depth = 0
    in_single = in_double = in_template = False
    escaped = False
    start = i

    while i < len(code):
        ch = code[i]

        if escaped:
            escaped = False
            i += 1
            continue
        if ch == "\\":
            escaped = True
            i += 1
            continue

        if not in_double and not in_template and ch == "'":
            in_single = not in_single
            i += 1
            continue
        if not in_single and not in_template and ch == '"':
            in_double = not in_double
            i += 1
            continue
        if not in_single and not in_double and ch == "`":
            in_template = not in_template
            i += 1
            continue
        if in_single or in_double or in_template:
            i += 1
            continue

        if ch == "{":
            depth += 1
        if ch == "}":
            depth -= 1
            if depth == 0:
                return code[start:i + 1]
        i += 1

    return None


def _parse_object_literal_pairs(object_literal: str) -> list:
    """Port of parseObjectLiteralPairs (tool-extractor.js:504-526)."""
    inner = re.sub(r"^\{|\}$", "", object_literal)
    parts = _split_top_level(inner, ",")
    pairs = []

    for part in parts:
        index = _find_top_level_colon(part)
        if index == -1:
            continue
        raw_key = re.sub(r"^['\"]|['\"]$", "", part[:index].strip())
        if not _KEY_RE.match(raw_key):
            continue
        raw_value = part[index + 1:].strip()
        pairs.append({
            "key": raw_key,
            "type": _infer_type_from_code(raw_value),
            "example": _normalize_example(raw_value),
        })

    return pairs


def _split_top_level(value: str, separator_char: str) -> list:
    """Port of splitTopLevel (tool-extractor.js:528-577)."""
    result = []
    current = ""
    depth_paren = depth_brace = depth_bracket = 0
    in_single = in_double = in_template = False
    escaped = False

    for ch in value:
        if escaped:
            current += ch
            escaped = False
            continue
        if ch == "\\":
            current += ch
            escaped = True
            continue

        if not in_double and not in_template and ch == "'":
            in_single = not in_single
        elif not in_single and not in_template and ch == '"':
            in_double = not in_double
        elif not in_single and not in_double and ch == "`":
            in_template = not in_template

        if not in_single and not in_double and not in_template:
            if ch == "(":
                depth_paren += 1
            elif ch == ")":
                depth_paren -= 1
            elif ch == "{":
                depth_brace += 1
            elif ch == "}":
                depth_brace -= 1
            elif ch == "[":
                depth_bracket += 1
            elif ch == "]":
                depth_bracket -= 1

            if ch == separator_char and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
                result.append(current)
                current = ""
                continue

        current += ch

    if current.strip():
        result.append(current)
    return result


def _find_top_level_colon(part: str) -> int:
    """Port of findTopLevelColon (tool-extractor.js:579-618)."""
    depth_paren = depth_brace = depth_bracket = 0
    in_single = in_double = in_template = False
    escaped = False

    for i, ch in enumerate(part):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue

        if not in_double and not in_template and ch == "'":
            in_single = not in_single
        elif not in_single and not in_template and ch == '"':
            in_double = not in_double
        elif not in_single and not in_double and ch == "`":
            in_template = not in_template

        if in_single or in_double or in_template:
            continue

        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        elif ch == ":" and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
            return i

    return -1


def _normalize_tool_name(candidate) -> str | None:
    """Port of normalizeToolName (tool-extractor.js:620-633)."""
    if not isinstance(candidate, str):
        return None
    cleaned = re.sub(r"^`|`$", "", candidate.strip())
    if not _TOOL_NAME_FULL_RE.match(cleaned):
        return None
    terminal = cleaned.split(".")[-1]
    if not terminal:
        return None
    if _MD_FILE_REF_RE.search(cleaned):
        return None
    return cleaned


def deduplicate_call_sites(tools: list) -> list:
    """Port of deduplicateCallSites (tool-extractor.js:635-674)."""
    by_call_site: dict = {}

    for tool in tools:
        canonical_name = _normalize_tool_name(tool.get("canonical_name") or tool.get("name"))
        name = _normalize_tool_name(tool.get("name")) or canonical_name
        if not name and not canonical_name:
            continue

        if name == "llm.inference" or tool.get("type") == "builtin_call":
            by_call_site[f"builtin:{name}"] = {
                **tool,
                "name": name,
                "canonical_name": tool.get("canonical_name") or name,
                "type": tool.get("type") or "builtin_call",
                "input": tool.get("input") or {},
                "output": tool.get("output") or infer_output_signature(
                    name, tool.get("action") or name.split(".")[-1]),
            }
            continue

        normalized = {
            **tool,
            "name": name,
            "canonical_name": canonical_name or name,
            "type": tool.get("type") or "tool_call",
            "input": tool.get("input") or {},
            "output": tool.get("output") or infer_output_signature(
                name, tool.get("action") or name.split(".")[-1]),
        }
        key = _call_site_duplicate_key(normalized)

        if key not in by_call_site:
            by_call_site[key] = normalized
            continue

        by_call_site[key] = _merge_tool_metadata(by_call_site[key], normalized)

    return list(by_call_site.values())


def _merge_tool_metadata(a: dict, b: dict) -> dict:
    """Port of mergeToolMetadata (tool-extractor.js:680-696)."""
    merged_input = {**a.get("input", {}), **b.get("input", {})}
    merged_output = {**a.get("output", {}), **b.get("output", {})}

    # JS: (b.description && b.description.length > a.description?.length) ? b : a.
    # When a.description is undefined, `len > undefined` is false, so a wins (and
    # then `|| ''` blanks it). Replicate that quirk exactly.
    a_desc = a.get("description")
    b_desc = b.get("description")
    if b_desc and a_desc is not None and len(b_desc) > len(a_desc):
        description = b_desc
    else:
        description = a_desc
    location = _prefer_location(a.get("location") or {}, b.get("location") or {})

    return {
        **a,
        **b,
        "description": description or "",
        "input": merged_input,
        "output": merged_output,
        "location": location,
        "isCritical": a.get("isCritical") or b.get("isCritical") or False,
    }


def _assign_call_site_identity(tools: list) -> list:
    """Port of assignCallSiteIdentity (tool-extractor.js:698-723)."""
    ordered = sorted(tools, key=functools.cmp_to_key(_compare_tool_location))
    callsite_index = 0
    result = []

    for tool in ordered:
        if tool.get("type") == "builtin_call" or tool.get("name") == "llm.inference":
            result.append({**tool, "canonical_name": tool.get("canonical_name") or tool.get("name")})
            continue

        callsite_index += 1
        canonical_name = _normalize_tool_name(tool.get("canonical_name") or tool.get("name")) or tool.get("name")
        callsite_id = f"call_{str(callsite_index).zfill(3)}"

        result.append({
            **tool,
            "name": f"{canonical_name}#{callsite_id}",
            "canonical_name": canonical_name,
            "callsite_id": callsite_id,
            "callsite_order": callsite_index,
            "callsite_role": "tool_call",
        })

    return result


def _compare_tool_location(a: dict, b: dict) -> int:
    """Port of compareToolLocation (tool-extractor.js:725-743)."""
    file_a = str((a.get("location") or {}).get("file") or "")
    file_b = str((b.get("location") or {}).get("file") or "")
    if file_a != file_b:
        if file_a == "SKILL.md":
            return -1
        if file_b == "SKILL.md":
            return 1
        if file_a == "README.md":
            return -1
        if file_b == "README.md":
            return 1
        return _locale_compare(file_a, file_b)

    line_delta = _int((a.get("location") or {}).get("line")) - _int((b.get("location") or {}).get("line"))
    if line_delta != 0:
        return line_delta

    column_delta = _int((a.get("location") or {}).get("column")) - _int((b.get("location") or {}).get("column"))
    if column_delta != 0:
        return column_delta

    return _locale_compare(
        str(a.get("canonical_name") or a.get("name") or ""),
        str(b.get("canonical_name") or b.get("name") or ""),
    )


def _call_site_duplicate_key(tool: dict) -> str:
    """Port of callSiteDuplicateKey (tool-extractor.js:745-753)."""
    location = tool.get("location") or {}
    return "|".join([
        str(tool.get("canonical_name") or tool.get("name") or ""),
        str(location.get("file") or ""),
        str(_int(location.get("line"))),
        str(_int(location.get("column"))),
        str(tool.get("extraction_method") or ""),
    ])


def _prefer_location(a: dict, b: dict) -> dict:
    """Port of preferLocation (tool-extractor.js:755-761)."""
    a = a or {}
    b = b or {}
    if not a.get("file"):
        return b
    if not b.get("file"):
        return a
    if a.get("file") == "SKILL.md" and b.get("file") != "SKILL.md":
        return a
    if b.get("file") == "SKILL.md" and a.get("file") != "SKILL.md":
        return b
    a_line = a.get("line") or _MAX_SAFE_INT
    b_line = b.get("line") or _MAX_SAFE_INT
    return a if a_line <= b_line else b


def infer_input_signature(tool_name: str, action: str) -> dict:
    """Port of inferInputSignature (tool-extractor.js:763-784)."""
    input_sig: dict = {}
    lower_name = tool_name.lower()
    lower_action = (action or "").lower()

    if "app" in lower_name and "create" not in lower_action:
        input_sig["app_token"] = {"type": "app_token", "required": True}
    if "table" in lower_name and "create" not in lower_action:
        input_sig["table_id"] = {"type": "table_id", "required": True}
    if re.search(r"create|update|write|insert|send|post", lower_action):
        input_sig["payload"] = {"type": "object", "required": True}
    if re.search(r"get|list|search|query|fetch|read", lower_action):
        if not input_sig:
            input_sig["filter"] = {"type": "object", "required": False}

    return input_sig


def infer_output_signature(tool_name: str, action: str) -> dict:
    """Port of inferOutputSignature (tool-extractor.js:786-816)."""
    output: dict = {}
    lower_name = tool_name.lower()
    lower_action = (action or "").lower()

    if re.search(r"get|read|fetch|query|find|retrieve", lower_action):
        output["data"] = {"type": "object"}
    if re.search(r"list|search", lower_action):
        output["items"] = {"type": "array"}
    if re.search(r"create|add|insert", lower_action):
        output["success"] = {"type": "boolean"}
        output["id"] = {"type": "string"}
    if re.search(r"update|write|delete|remove|send|post|publish", lower_action):
        output["success"] = {"type": "boolean"}

    if "app" in lower_name and "create" in lower_action:
        output["app_token"] = {"type": "app_token"}
    if "table" in lower_name and "create" in lower_action:
        output["table_id"] = {"type": "table_id"}
    if "record" in lower_name and "create" in lower_action:
        output["record_id"] = {"type": "record_id"}

    return output


def _infer_type(value) -> str:
    """Port of inferType (tool-extractor.js:818-824)."""
    if value is None:
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    return "string"


def _infer_type_from_code(value: str) -> str:
    """Port of inferTypeFromCode (tool-extractor.js:826-835)."""
    v = value.strip()
    if not v:
        return "string"
    if v.startswith('"') or v.startswith("'") or v.startswith("`"):
        return "string"
    if re.match(r"^(true|false)\b", v):
        return "boolean"
    if re.match(r"^[+-]?\d+(\.\d+)?\b", v):
        return "number"
    if v.startswith("{"):
        return "object"
    if v.startswith("["):
        return "array"
    return "string"


def _normalize_example(raw_value: str):
    """Port of normalizeExample (tool-extractor.js:837-846)."""
    trimmed = raw_value.strip()
    if (trimmed.startswith('"') and trimmed.endswith('"')) or \
       (trimmed.startswith("'") and trimmed.endswith("'")):
        return trimmed[1:-1]
    if re.match(r"^(true|false)$", trimmed):
        return trimmed == "true"
    if re.match(r"^[+-]?\d+(\.\d+)?$", trimmed):
        return _js_number(trimmed)
    return trimmed


def _try_parse_json(value: str):
    """Port of tryParseJson (tool-extractor.js:848-854)."""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None


def _line_number_at(content: str, index: int) -> int:
    """Port of lineNumberAt (tool-extractor.js:856-858)."""
    return content[:index].count("\n") + 1


def _line_at(content: str, line: int) -> str:
    """Port of lineAt (tool-extractor.js:860-862)."""
    parts = re.split(r"\r?\n", str(content or ""))
    idx = max(0, int(line or 1) - 1)
    return parts[idx] if idx < len(parts) else ""


def _column_number_at(content: str, index: int) -> int:
    """Port of columnNumberAt (tool-extractor.js:864-867)."""
    from_index = max(0, index - 1)
    previous_newline = content.rfind("\n", 0, from_index + 1)
    return index - previous_newline


def _normalize_path_for_output(file_path: str, root_dir: str = "") -> str:
    """Port of normalizePathForOutput (tool-extractor.js:869-874)."""
    if root_dir and os.path.isabs(file_path):
        output_path = os.path.relpath(file_path, root_dir)
    else:
        output_path = file_path
    return output_path.replace(os.sep, "/").replace("\\", "/")


def _is_javascript_like_file(file_path: str) -> bool:
    """Port of isJavaScriptLikeFile (tool-extractor.js:876-878)."""
    return os.path.splitext(str(file_path or ""))[1].lower() in (".js", ".mjs", ".cjs", ".ts", ".tsx")


def _find_section_for_line(sections, line):
    """Port of findSectionForLine (tool-extractor.js:880-887)."""
    for section in sections or []:
        if line >= section.get("startLine") and line <= section.get("endLine"):
            return section.get("title")
    return None


# --- small JS-semantics helpers -------------------------------------------

_MAX_SAFE_INT = 9007199254740991  # Number.MAX_SAFE_INTEGER


def _int(value) -> int:
    """JS ``Number(x || 0)`` for integer-valued location fields."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _js_number(text: str):
    """JS ``Number(text)``: integer if whole, else float."""
    number = float(text)
    return int(number) if number.is_integer() else number


def _locale_compare(a: str, b: str) -> int:
    """Faithful JS String.localeCompare (ICU-root ASCII). See util/locale.py."""
    from ..util.locale import locale_compare
    return locale_compare(a, b)
