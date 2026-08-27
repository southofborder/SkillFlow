"""Script-flow extraction — port of src/parser/script-flow-extractor.js.

Turns executable files into script entry/function/call nodes + control-flow
edges. The shell path is pure-rule Python (heredoc/if runtime blocks, shell
functions, command classification via the shared shell-command-classifier).
The JS/TS path delegates ONLY the babel AST parse to babel_ast_sidecar.cjs
(returns raw function/call positions+names); all classification, identity and
node-shape are rebuilt here in Python, shared with the shell path.

The live shell semantic-gate LLM path is ported (transport-backed), but the
rule-only and injectable-refiner paths cover the deterministic behavior the
tests and golden oracle exercise.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time

from ..llm.normalizers import normalize_assistant_content, parse_loose_json
from ..llm.transport import post_json_with_timeout
from .document_context import build_source_context, normalize_source_path
from .shell_command_classifier import classify_shell_command_line

JS_EXTENSIONS = {".js", ".mjs", ".cjs", ".ts", ".tsx"}
SHELL_EXTENSIONS = {".sh", ".bash"}
SCRIPT_SEMANTIC_PROMPT_VERSION = "fcg-script-runtime-semantic-v1"
DEFAULT_SCRIPT_SEMANTIC_RETRIES = 2

_SIDECAR = os.path.join(os.path.dirname(__file__), "babel_ast_sidecar.cjs")


# --- entry point ----------------------------------------------------------

def extract_script_flow(script_files: list | None = None, options: dict | None = None) -> dict:
    """Port of extractScriptFlow (script-flow-extractor.js:17-37)."""
    options = options or {}
    nodes: list = []
    edges: list = []
    root_dir = options.get("rootDir") or ""

    for file_path in script_files or []:
        ext = os.path.splitext(str(file_path or ""))[1].lower()
        rel_path = normalize_source_path(root_dir, file_path)
        flow = None
        if ext in JS_EXTENSIONS:
            flow = _extract_javascript_flow(file_path, rel_path)
        elif ext in SHELL_EXTENSIONS or _is_shell_script(file_path):
            flow = _extract_shell_flow(file_path, rel_path, options)
        if not flow:
            continue
        nodes.extend(flow["nodes"])
        edges.extend(flow["edges"])

    return {"nodes": _dedupe_by_name(nodes), "edges": _dedupe_edges(edges)}


# --- JavaScript/TypeScript path (babel sidecar) ---------------------------

def _run_babel_sidecar(content: str, rel_path: str) -> dict | None:
    """Invoke babel_ast_sidecar.cjs; return {functions, calls} or {parseError}."""
    try:
        # Force UTF-8 decode: the sidecar emits UTF-8 JSON, but text=True alone
        # decodes with the OS locale (GBK/cp936 on zh-Windows), which raises
        # UnicodeDecodeError on non-GBK bytes and leaves stdout None. errors=
        # "replace" keeps a stray byte from killing the whole analysis.
        proc = subprocess.run(
            ["node", _SIDECAR],
            input=json.dumps({"content": content, "relPath": rel_path}),
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
    except (OSError, ValueError):
        return None
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return {"parseError": (proc.stderr or "sidecar produced no output").strip()[:500]}
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"parseError": "sidecar returned invalid JSON"}


def _extract_javascript_flow(file_path: str, rel_path: str) -> dict | None:
    """Port of extractJavaScriptFlow (script-flow-extractor.js:39-86)."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError:
        print(f"Warning: Could not read script file: {file_path}")
        return None

    result = _run_babel_sidecar(content, rel_path)
    if result is None or result.get("parseError") is not None:
        return _fallback_script_entry(content, rel_path, "javascript_parse_error")

    file_slug = _stable_slug(rel_path)
    functions = [
        {
            "name": fn["name"],
            "nodeName": f"script.function.{file_slug}.l{fn['line']}.{_stable_slug(fn['name'])}",
            "line": fn["line"],
            "column": fn.get("column") or 0,
            "start": fn.get("start") or 0,
            "end": fn.get("end") or fn.get("start") or 0,
            "snippet": fn.get("snippet") or "",
            "operationType": _infer_operation_type(f"{fn['name']}\n{fn.get('snippet') or ''}"),
            "target": fn["name"],
        }
        for fn in result.get("functions", [])
    ]

    raw_calls = []
    for c in result.get("calls", []):
        callee = c["callee"]
        snippet = c.get("snippet") or ""
        classification = _classify_script_call(callee, snippet)
        if classification["noise"]:
            continue
        owner = _find_owner_function(c.get("start") or 0, functions)
        raw_calls.append({
            "callee": callee,
            "line": c["line"],
            "column": c.get("column") or 0,
            "snippet": snippet,
            "operationType": classification["operationType"],
            "scriptRole": classification["role"],
            "ownerNodeName": owner["nodeName"] if owner else "",
            "target": callee,
        })
    calls = [
        {**call, "nodeName": f"script.call.__FILE__.l{call['line']}.c{index + 1}.{_stable_slug(call['callee'])}"}
        for index, call in enumerate(raw_calls)
    ]

    nodes = [_create_script_entry_node(content, rel_path, "javascript", 1)]
    edges: list = []

    for fn in functions:
        nodes.append(_create_script_function_node(content, rel_path, "javascript", fn))
        edges.append(_create_script_edge(nodes[0]["name"], fn["nodeName"], len(edges), "script_declares_function"))

    owner_last_call: dict = {}
    for call in calls:
        nodes.append(_create_script_call_node(content, rel_path, "javascript", call))
        owner = call.get("ownerNodeName") or nodes[0]["name"]
        edges.append(_create_script_edge(owner, call["nodeName"], len(edges), "script_invokes_call"))
        prior = owner_last_call.get(owner)
        if prior:
            edges.append(_create_script_edge(prior, call["nodeName"], len(edges), "script_call_sequence"))
        owner_last_call[owner] = call["nodeName"]

    return {"nodes": nodes, "edges": edges}


def _find_owner_function(position: int, functions: list) -> dict | None:
    """Port of findOwnerFunction (script-flow-extractor.js:632-636)."""
    candidates = [fn for fn in functions if int(fn.get("start") or 0) <= position <= int(fn.get("end") or 0)]
    candidates.sort(key=lambda fn: (int(fn.get("end") or 0) - int(fn.get("start") or 0)))
    return candidates[0] if candidates else None


# --- shell path (pure rule) -----------------------------------------------

def _extract_shell_flow(file_path: str, rel_path: str, options: dict) -> dict | None:
    """Port of extractShellFlow (script-flow-extractor.js:88-130)."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError:
        print(f"Warning: Could not read shell file: {file_path}")
        return None

    lines = re.split(r"\r?\n", content)
    file_slug = _stable_slug(rel_path)
    functions = [
        {**fn, "nodeName": f"script.function.{file_slug}.l{fn['line']}.{_stable_slug(fn['name'])}"}
        for fn in _collect_shell_functions(lines, rel_path)
    ]
    runtime_blocks = _refine_shell_semantic_blocks(
        _collect_shell_semantic_blocks(lines, functions, rel_path), options)
    calls = sorted(
        [*_collect_shell_commands(lines, functions), *runtime_blocks],
        key=lambda c: (c["line"], 1 if c.get("semanticBlock") else 0),
    )
    nodes = [_create_script_entry_node(content, rel_path, "shell", 1)]
    edges: list = []

    for fn in functions:
        nodes.append(_create_script_function_node(content, rel_path, "shell", fn))
        edges.append(_create_script_edge(nodes[0]["name"], fn["nodeName"], len(edges), "script_declares_function"))

    owner_last_call: dict = {}
    for call in calls:
        nodes.append(_create_script_call_node(content, rel_path, "shell", call))
        owner = call.get("ownerNodeName") or nodes[0]["name"]
        edges.append(_create_script_edge(owner, call["nodeName"], len(edges), "script_invokes_command"))
        prior = owner_last_call.get(owner)
        if prior:
            edges.append(_create_script_edge(prior, call["nodeName"], len(edges), "script_command_sequence"))
        owner_last_call[owner] = call["nodeName"]

    return {"nodes": nodes, "edges": edges}


_SHELL_FN_RE = re.compile(r"^(?:function\s+)?([A-Za-z_][A-Za-z0-9_-]*)\s*(?:\(\))?\s*\{")


def _collect_shell_functions(lines: list, rel_path: str) -> list:
    """Port of collectShellFunctions (script-flow-extractor.js:193-233)."""
    functions: list = []
    active: dict | None = None
    brace_depth = 0

    for i, line in enumerate(lines):
        trimmed = _strip_shell_comment(line).strip()
        fn_match = _SHELL_FN_RE.match(trimmed)
        if active is None and fn_match:
            active = {
                "name": fn_match.group(1),
                "line": i + 1,
                "column": line.find(fn_match.group(1)),
                "startLine": i + 1,
                "endLine": i + 1,
                "body": [line],
            }
            brace_depth = _count_char(trimmed, "{") - _count_char(trimmed, "}")
            if brace_depth <= 0:
                functions.append(_finalize_shell_function(active))
                active = None
            continue
        if active is None:
            continue
        active["body"].append(line)
        active["endLine"] = i + 1
        brace_depth += _count_char(trimmed, "{") - _count_char(trimmed, "}")
        if brace_depth <= 0:
            functions.append(_finalize_shell_function(active))
            active = None

    return [
        {**fn, "target": fn["name"], "operationType": _infer_operation_type(f"{fn['name']}\n{fn['snippet']}")}
        for fn in functions
    ]


_SHELL_CMD_SKIP_RE = re.compile(r"^#!|^\}|^(?:then|do|fi|done|else|elif\b)")
_SHELL_CMD_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")
_SHELL_CMD_ASSIGN_HASCMD_RE = re.compile(r"[|&;<>()]")


def _collect_shell_commands(lines: list, functions: list) -> list:
    """Port of collectShellCommands (script-flow-extractor.js:235-272)."""
    calls: list = []
    heredoc_ranges = _collect_heredoc_ranges(lines)
    for i, raw in enumerate(lines):
        if _is_line_in_ranges(i + 1, heredoc_ranges, include_start=False, include_end=True):
            continue
        line = _strip_shell_comment(raw).strip()
        if not line or _SHELL_CMD_SKIP_RE.match(line):
            continue
        if _SHELL_FN_RE.match(line):
            continue
        if _SHELL_CMD_ASSIGN_RE.match(line) and not _SHELL_CMD_ASSIGN_HASCMD_RE.search(line):
            continue

        classified = classify_shell_command_line(line)
        if not classified:
            continue
        owner = next((fn for fn in functions if i + 1 > fn["startLine"] and i + 1 < fn["endLine"]), None)
        for cmd in classified:
            targets = cmd["targets"] if cmd.get("targets") else None
            calls.append({
                "callee": cmd["command"],
                "line": i + 1,
                "column": max(0, raw.find(cmd["command"])),
                "snippet": line[:500],
                "operationType": cmd["operationType"],
                "targets": targets,
                "ownerNodeName": owner["nodeName"] if owner else "",
                "target": cmd["targets"][0]["value"] if (cmd.get("targets") and cmd["targets"]) else cmd["command"],
            })

    return [
        {**call, "nodeName": f"script.call.__FILE__.l{call['line']}.c{index + 1}.{_stable_slug(call['callee'])}"}
        for index, call in enumerate(calls)
    ]


def _collect_shell_semantic_blocks(lines: list, functions: list, rel_path: str) -> list:
    """Port of collectShellSemanticBlocks (script-flow-extractor.js:274-300)."""
    blocks = [*_collect_heredoc_blocks(lines, functions), *_collect_shell_if_blocks(lines, functions)]
    return [
        {
            "callee": block["callee"],
            "line": block["line"],
            "column": block.get("column") or 0,
            "snippet": block["snippet"],
            "operationType": block["operationType"],
            "ownerNodeName": block.get("ownerNodeName") or "",
            "target": block.get("target") or block["callee"],
            "semanticBlock": True,
            "semanticGate": block.get("semanticGate"),
            "conditions": block.get("conditions") or [],
            "targets": block.get("targets") or [],
            "effects": block.get("effects") or [],
            "inputs": block.get("inputs") or [],
            "outputs": block.get("outputs") or [],
            "confidence": block.get("confidence"),
            "action": block.get("action"),
            "extractionMethod": block.get("extractionMethod"),
            "sourceRole": "runtime_implementation",
            # NB: JS collectShellSemanticBlocks does NOT carry `kind`/`text` onto
            # the mapped block. Downstream buildShellRuntimeCandidate therefore
            # sees kind=undefined → grammar/syntax defaults to the heredoc/output
            # form and output_text/condition_text stay empty. Dropping them here
            # keeps that (quirky) behavior byte-identical.
            "nodeName": f"script.call.__FILE__.l{block['line']}.csemantic{index + 1}."
                        f"{_stable_slug(block.get('callee') or block.get('operationType') or 'runtime_block')}",
        }
        for index, block in enumerate(blocks)
    ]


def _collect_heredoc_blocks(lines: list, functions: list) -> list:
    """Port of collectHeredocBlocks (script-flow-extractor.js:302-328)."""
    blocks = []
    for rng in _collect_heredoc_ranges(lines):
        start_line, end_line = rng["startLine"], rng["endLine"]
        body_lines = lines[start_line:end_line - 1]
        snippet = "\n".join(
            [_at(lines, start_line - 1), *body_lines, _at(lines, end_line - 1)]
        ).strip()
        text = "\n".join(body_lines).strip()
        if not text:
            continue
        owner = next((fn for fn in functions if start_line > fn["startLine"] and start_line < fn["endLine"]), None)
        blocks.append({
            "kind": "heredoc",
            "callee": _infer_heredoc_callee(text),
            "line": start_line,
            "column": max(0, _at(lines, start_line - 1).find("cat")),
            "snippet": snippet,
            "text": text,
            "operationType": "write",
            "action": "write",
            "ownerNodeName": owner["nodeName"] if owner else "",
            "extractionMethod": "script_flow_runtime_block",
        })
    return blocks


_SHELL_IF_RE = re.compile(r"^(?:if|elif)\b")


def _collect_shell_if_blocks(lines: list, functions: list) -> list:
    """Port of collectShellIfBlocks (script-flow-extractor.js:330-353)."""
    blocks = []
    for i, raw in enumerate(lines):
        line = _strip_shell_comment(raw).strip()
        if not _SHELL_IF_RE.match(line):
            continue
        end_line = _find_shell_block_end(lines, i + 1, "fi")
        body = "\n".join(lines[i:max(i + 1, end_line)]).strip()
        owner = next((fn for fn in functions if i + 1 > fn["startLine"] and i + 1 < fn["endLine"]), None)
        blocks.append({
            "kind": "if",
            "callee": "shell.condition",
            "line": i + 1,
            "column": max(0, raw.find(re.sub(r"^\s+", "", line))),
            "snippet": body,
            "text": body,
            "operationType": "guard",
            "action": "guard",
            "ownerNodeName": owner["nodeName"] if owner else "",
            "extractionMethod": "script_flow_runtime_block",
        })
    return blocks


# --- node builders (shared JS + shell) ------------------------------------

def _create_script_entry_node(content: str, rel_path: str, language: str, line: int) -> dict:
    """Port of createScriptEntryNode (script-flow-extractor.js:355-396)."""
    file_slug = _stable_slug(rel_path)
    node_name = f"script.entry.{file_slug}"
    return {
        "name": node_name,
        "action": "run",
        "type": "custom_func",
        "description": f"Script entry for {rel_path}",
        "input": {
            "environment": {"type": "object", "required": False},
            "arguments": {"type": "array", "required": False},
        },
        "output": {"result": {"type": "object"}},
        "location": {"file": rel_path, "line": line, "section": "script entry"},
        "ownerScript": rel_path,
        "operationType": "invoke_tool",
        "formal_semantics": _build_script_semantics(
            operation_type="invoke_tool", action="run", rel_path=rel_path, line=line,
            language=language, text=f"Script entry for {rel_path}", target=rel_path),
        "source_context": _build_script_source_context(
            content=content, rel_path=rel_path, line=line, language=language, action="run",
            operation_type="invoke_tool", snippet=_first_non_empty_line(content) or rel_path,
            trigger="script_entry", extraction_method="script_flow_entry"),
        "excludeFromImplicitLlmEdge": True,
        "semanticKind": "script_entry",
    }


def _create_script_function_node(content: str, rel_path: str, language: str, fn: dict) -> dict:
    """Port of createScriptFunctionNode (script-flow-extractor.js:398-436)."""
    name = fn["nodeName"]
    operation_type = fn.get("operationType") or "transform"
    return {
        "name": name,
        "action": _operation_action(operation_type),
        "type": "custom_func",
        "description": f"Function {fn['name']} in {rel_path}",
        "input": {"arguments": {"type": "object", "required": False}},
        "output": {"result": {"type": "object"}},
        "location": {"file": rel_path, "line": fn["line"], "column": fn.get("column") or 0,
                     "section": f"function {fn['name']}"},
        "ownerScript": rel_path,
        "functionName": fn["name"],
        "operationType": operation_type,
        "formal_semantics": _build_script_semantics(
            operation_type=operation_type, action=_operation_action(operation_type), rel_path=rel_path,
            line=fn["line"], language=language, text=fn.get("snippet") or fn["name"],
            target=fn.get("target") or fn["name"]),
        "source_context": _build_script_source_context(
            content=content, rel_path=rel_path, line=fn["line"], column=fn.get("column") or 0,
            language=language, action=_operation_action(operation_type), operation_type=operation_type,
            snippet=_first_line(fn.get("snippet")) or fn["name"], trigger=fn["name"],
            extraction_method="script_flow_function"),
        "excludeFromImplicitLlmEdge": True,
        "semanticKind": "script_function",
    }


def _create_script_call_node(content: str, rel_path: str, language: str, call: dict) -> dict:
    """Port of createScriptCallNode (script-flow-extractor.js:438-490)."""
    file_slug = _stable_slug(rel_path)
    name = call["nodeName"].replace("__FILE__", file_slug)
    call["nodeName"] = name
    operation_type = call.get("operationType") or "invoke_tool"
    action = call.get("action") or _operation_action(operation_type)
    node = {
        "name": name,
        "canonical_name": call["callee"],
        "action": action,
        "type": "custom_func",
        "description": f"Script call {call['callee']} in {rel_path}",
        "input": {"context": {"type": "object", "required": False}},
        "output": {"result": {"type": "object"}},
        "location": {"file": rel_path, "line": call["line"], "column": call.get("column") or 0,
                     "section": "script call"},
        "ownerScript": rel_path,
        "callee": call["callee"],
        "operationType": operation_type,
        "formal_semantics": _build_script_semantics(
            operation_type=operation_type, action=action, rel_path=rel_path, line=call["line"],
            language=language, text=call.get("snippet") or call["callee"],
            target=call.get("target") or call["callee"], conditions=call.get("conditions") or [],
            targets=call.get("targets") or [], effects=call.get("effects") or [],
            inputs=call.get("inputs") or [], outputs=call.get("outputs") or [],
            confidence=call.get("confidence")),
        "source_context": _build_script_source_context(
            content=content, rel_path=rel_path, line=call["line"], column=call.get("column") or 0,
            language=language, action=action, operation_type=operation_type,
            snippet=call.get("snippet") or call["callee"], trigger=call["callee"],
            extraction_method=call.get("extractionMethod") or "script_flow_call",
            source_role=call.get("sourceRole") or ""),
        "excludeFromImplicitLlmEdge": call["excludeFromImplicitLlmEdge"]
            if call.get("excludeFromImplicitLlmEdge") is not None else True,
        "excludeFromTypeAnalysis": bool(call.get("excludeFromTypeAnalysis")),
        "excludeFromFlow": bool(call.get("excludeFromFlow")),
        "semanticKind": "script_call",
    }
    # JS: `semantic_gate: call.semanticGate || undefined` — undefined is dropped
    # by JSON.stringify, so only emit the key when the gate is truthy.
    if call.get("semanticGate"):
        node["semantic_gate"] = call["semanticGate"]
    return node


def _build_script_semantics(*, operation_type, action, rel_path, line, language, text, target,
                            conditions=None, targets=None, effects=None, inputs=None, outputs=None,
                            confidence=None) -> dict:
    """Port of buildScriptSemantics (script-flow-extractor.js:492-513)."""
    conditions = conditions or []
    targets = targets or []
    effects = effects or []
    inputs = inputs or []
    outputs = outputs or []
    normalized_targets = targets if targets else [
        {"type": _target_type(operation_type, target), "value": target, "raw": target}]
    return {
        "operation_type": operation_type,
        "actor": "shell" if language == "shell" else "runtime",
        "inputs": inputs if inputs else _build_script_inputs(operation_type, target),
        "outputs": outputs if outputs else _build_script_outputs(operation_type, target),
        "targets": normalized_targets,
        "conditions": conditions,
        "effects": effects if effects else _operation_effects(operation_type),
        "confidence": confidence if isinstance(confidence, (int, float)) and not isinstance(confidence, bool) else 0.82,
        "evidence": {
            "text": text,
            "source_line": text,
            "file": rel_path,
            "line": line,
            "section": language,
            "method": "script_flow",
        },
        "action": action,
    }


def _build_script_source_context(*, content, rel_path, line, column=0, language, action,
                                 operation_type, snippet, trigger, extraction_method, source_role="") -> dict:
    """Port of buildScriptSourceContext (script-flow-extractor.js:515-532)."""
    return build_source_context({
        "content": content,
        "file": rel_path,
        "line": line,
        "column": column,
        "section": language,
        "sourceText": _line_at(content, line) or snippet,
        "action": action,
        "operationType": operation_type,
        "actionSnippet": snippet,
        "trigger": trigger,
        "extractionMethod": extraction_method,
        "sourceRole": source_role or ("runtime_implementation" if language == "shell" else "extraction_source"),
        "sourceType": "shell_script" if language == "shell" else "script",
        "grounded": bool(snippet),
    })


def _create_script_edge(source: str, target: str, index: int, reason: str) -> dict:
    """Port of createScriptEdge (script-flow-extractor.js:534-549)."""
    return {
        "id": f"script_flow_{index + 1}",
        "source": source,
        "target": target,
        "type": "control_flow",
        "confidence": 0.86,
        "validation_method": "script_flow",
        "data_flow": {"from_param": "context", "to_param": "context", "data_type": "object"},
        "semantic_reason": reason,
    }


# --- call classification (rule tables) ------------------------------------

_NOISE_CALL_METHODS = {
    "push", "pop", "shift", "unshift", "slice", "splice", "concat", "flat", "flatmap",
    "map", "filter", "reduce", "reduceright", "foreach", "find", "findindex", "findlast",
    "some", "every", "includes", "indexof", "lastindexof", "join", "reverse", "fill",
    "keys", "values", "entries", "isarray", "from", "of",
    "split", "trim", "trimstart", "trimend", "padstart", "padend", "tolowercase",
    "touppercase", "replace", "replaceall", "substring", "substr", "charat", "charcodeat",
    "startswith", "endswith", "match", "matchall", "repeat", "normalize", "tostring",
    "tofixed", "toprecision",
    "assign", "freeze", "fromentries", "hasownproperty",
    "getownpropertynames", "defineproperty", "create", "getprototypeof",
    "parseint", "parsefloat", "isnan", "isfinite", "abs", "floor", "ceil", "round",
    "min", "max", "random", "pow", "sqrt", "boolean", "number", "string", "symbol",
    "then", "catch", "finally", "resolve", "reject", "all", "allsettled", "race",
    "settimeout", "setinterval", "cleartimeout", "clearinterval", "now",
}

_NOISE_CALL_FULL = {
    "console.log", "console.error", "console.warn", "console.info", "console.debug",
    "array.isarray", "array.from", "array.of", "object.assign", "object.keys",
    "object.values", "object.entries", "object.freeze", "object.create",
    "json.stringify", "math.floor", "math.ceil", "math.round", "math.max", "math.min",
    "math.abs", "math.random", "date.now", "number.parseint", "number.parsefloat",
    "process.exit", "this", "super",
}

_NOISE_CONSTRUCTORS = {
    "error", "typeerror", "rangeerror", "syntaxerror", "referenceerror",
    "map", "set", "weakmap", "weakset", "array", "object", "date", "regexp",
    "promise", "string", "number", "boolean",
}


def _classify_script_call(callee: str, snippet: str = "") -> dict:
    """Port of classifyScriptCall (script-flow-extractor.js:692-732)."""
    full = str(callee or "").lower()
    last = full.split(".")[-1] or full
    text = f"{full} {str(snippet or '')}".lower()

    if (re.search(r"\b(fetch|axios|got|superagent|node-fetch)\b", full) or
            re.search(r"\b(http|https)\.(request|get|post)\b", full) or
            (re.search(r"\.(post|put|patch|upload|send|sendmessage|publish)\b", full) and
             re.search(r"\b(url|http|api|webhook|endpoint|client|axios|request)\b", text))):
        return {"role": "sink", "operationType": "external_egress", "noise": False}
    if (re.search(r"\b(exec|execsync|spawn|spawnsync|execfile|execfilesync|fork)\b", full) or
            re.search(r"child_process", text)):
        return {"role": "sink", "operationType": "invoke_tool", "noise": False}
    if re.search(r"\b(writefile|writefilesync|appendfile|appendfilesync|createwritestream|mkdir|mkdirsync|rmsync|unlinksync|copyfile|rename)\b", full):
        return {"role": "sink", "operationType": "write", "noise": False}
    if (re.search(r"\b(readfile|readfilesync|createreadstream|readdir|readdirsync)\b", full) or
            re.search(r"process\.env", text) or re.search(r"\bargv\b", full)):
        return {"role": "source", "operationType": "read", "noise": False}
    if re.search(r"\b(redact|mask|sanitize|scrub|encrypt|hash|escape)\b", full):
        return {"role": "sanitizer", "operationType": "transform", "noise": False}
    if last == "parse" and re.search(r"json", full):
        return {"role": "propagator", "operationType": "transform", "noise": False}

    if full in _NOISE_CALL_FULL:
        return {"role": "noise", "operationType": "noise", "noise": True}
    if full in _NOISE_CONSTRUCTORS:
        return {"role": "noise", "operationType": "noise", "noise": True}
    if last in _NOISE_CALL_METHODS and "fs." not in full and not re.search(r"\b(client|api|db|store|repo)\b", full):
        return {"role": "noise", "operationType": "noise", "noise": True}

    return {"role": "unknown", "operationType": _infer_operation_type(text), "noise": False}


def _infer_operation_type(text: str) -> str:
    """Port of inferOperationType (script-flow-extractor.js:734-743)."""
    value = str(text or "").lower()
    if re.search(r"\b(fetch|axios|http\.request|https\.request|request|curl|wget|webhook|post|upload)\b", value):
        return "external_egress"
    if re.search(r"\b(exec|execsync|spawn|spawnsync|execfile|child_process|bash|sh|powershell|cmd\.exe)\b", value):
        return "invoke_tool"
    if re.search(r"\b(readfilesync|readfile|createreadstream|cat|grep|sed|awk|head|tail)\b", value):
        return "read"
    if re.search(r"\b(writefilesync|writefile|appendfile|createwritestream|echo\b.*>|tee|touch|mkdir|cp|mv)\b", value):
        return "write"
    if re.search(r"\b(json\.parse|map|filter|reduce|sort|split|join|replace|parse|extract|transform|sanitize|redact)\b", value):
        return "transform"
    if re.search(r"\b(if|case|test|\[\[|\bdecide|validate|ensure|check)\b", value):
        return "verify"
    return "invoke_tool"


def _operation_action(operation_type: str) -> str:
    """Port of operationAction (script-flow-extractor.js:745-754)."""
    return {
        "context": "context", "condition": "condition", "read": "read", "write": "write",
        "transform": "transform", "verify": "verify", "guard": "guard",
    }.get(operation_type, "run")


def _operation_effects(operation_type: str) -> list:
    """Port of operationEffects (script-flow-extractor.js:756-765)."""
    return {
        "context": [], "read": ["read_context"], "write": ["persist_state"],
        "transform": ["summarize"], "external_egress": ["network_egress"],
        "verify": ["validate"], "guard": ["validate", "branch"],
    }.get(operation_type, ["call_tool"])


def _build_script_inputs(operation_type: str, target: str) -> list:
    """Port of buildScriptInputs (script-flow-extractor.js:767-771)."""
    if operation_type == "context":
        return []
    if operation_type == "read":
        return [{"name": target, "type": _target_type(operation_type, target)}]
    return [{"name": "context", "type": "object"}]


def _build_script_outputs(operation_type: str, target: str) -> list:
    """Port of buildScriptOutputs (script-flow-extractor.js:773-780)."""
    if operation_type == "context":
        return []
    if operation_type in ("write", "external_egress", "invoke_tool"):
        return [{"name": "result", "type": "object"}]
    if operation_type == "read":
        return [{"name": "content", "type": "string"}]
    return [{"name": target or "result", "type": "object"}]


def _target_type(operation_type: str, target: str = "") -> str:
    """Port of targetType (script-flow-extractor.js:782-789)."""
    value = str(target or "").lower()
    if operation_type == "external_egress" or re.search(r"\b(fetch|http|curl|wget|webhook|api)\b", value):
        return "external"
    if re.search(r"\b(env|process\.env)\b", value):
        return "object"
    if re.search(r"\b(file|path|fs\.|\.md|\.json|\.txt|\.log)\b", value):
        return "file"
    if operation_type == "invoke_tool":
        return "command"
    return "object"


# --- shell semantic-gate refinement ---------------------------------------

def _refine_shell_semantic_blocks(blocks: list | None = None, options: dict | None = None) -> list:
    """Port of refineShellSemanticBlocks (script-flow-extractor.js:791-825).

    Python refiners are plain callables (the JS async refiner/batch-refiner map
    to sync callables; concurrency is a speed detail, not a correctness one).
    """
    blocks = blocks or []
    options = options or {}
    if not blocks:
        return []
    if options.get("semanticLlm") is False or options.get("disableLlm"):
        return [_apply_shell_semantic_refinement(block, None, False) for block in blocks]
    if callable(options.get("scriptSemanticRefiner")):
        refiner = options["scriptSemanticRefiner"]
        out = []
        for block in blocks:
            try:
                raw = refiner(_build_shell_runtime_candidate(block))
                out.append(_apply_shell_semantic_refinement(block, raw, True))
            except Exception as error:  # noqa: BLE001 — mirror JS catch-all
                out.append(_apply_shell_semantic_error(block, error))
        return out
    if callable(options.get("scriptSemanticBatchRefiner")):
        candidates = [_build_shell_runtime_candidate(block) for block in blocks]
        try:
            raw = options["scriptSemanticBatchRefiner"](candidates)
            by_id = _normalize_shell_batch_result(raw)
            out = []
            for block in blocks:
                candidate = _build_shell_runtime_candidate(block)
                verdict = by_id.get(candidate["id"])
                out.append(_apply_shell_semantic_refinement(block, verdict, True) if verdict
                           else _apply_shell_semantic_error(block, ValueError(f"Missing shell semantic result for {candidate['id']}")))
            return out
        except Exception as error:  # noqa: BLE001
            return [_apply_shell_semantic_error(block, error) for block in blocks]
    api_key = str(options.get("llmApiKey") or os.environ.get("LLM_API_KEY") or "").strip()
    if not api_key:
        return [_apply_shell_semantic_refinement(block, None, False) for block in blocks]
    return _resolve_shell_semantic_blocks_with_retry(blocks, {**options, "llmApiKey": api_key})


def _resolve_shell_semantic_blocks_with_retry(blocks: list, options: dict) -> list:
    """Port of resolveShellSemanticBlocksWithRetry (script-flow-extractor.js:827-847)."""
    try:
        raw = _call_shell_semantic_model_with_retry([_build_shell_runtime_candidate(b) for b in blocks], options)
        by_id = _normalize_shell_batch_result(raw)
        out = []
        for block in blocks:
            candidate = _build_shell_runtime_candidate(block)
            verdict = by_id.get(candidate["id"])
            out.append(_apply_shell_semantic_refinement(block, verdict, True) if verdict
                       else _apply_shell_semantic_error(block, ValueError(f"Missing shell semantic result for {candidate['id']}")))
        return out
    except Exception as error:  # noqa: BLE001
        if len(blocks) <= 1:
            return [_apply_shell_semantic_error(block, error) for block in blocks]
        midpoint = (len(blocks) + 1) // 2
        left = _resolve_shell_semantic_blocks_with_retry(blocks[:midpoint], options)
        right = _resolve_shell_semantic_blocks_with_retry(blocks[midpoint:], options)
        return [*left, *right]


def _call_shell_semantic_model_with_retry(candidates: list, options: dict):
    """Port of callShellSemanticModelWithRetry (script-flow-extractor.js:849-861)."""
    attempts = max(1, int(options.get("scriptSemanticRetries") or DEFAULT_SCRIPT_SEMANTIC_RETRIES) or DEFAULT_SCRIPT_SEMANTIC_RETRIES)
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return _call_shell_semantic_model(candidates, options)
        except Exception as error:  # noqa: BLE001
            last_error = error
            if attempt < attempts:
                time.sleep(0.25 * attempt)
    raise last_error or RuntimeError("Shell semantic LLM request failed")


def _apply_shell_semantic_refinement(block: dict, raw_verdict=None, llm_attempted: bool = False) -> dict:
    """Port of applyShellSemanticRefinement (script-flow-extractor.js:863-904)."""
    candidate = _build_shell_runtime_candidate(block)
    verdict = _normalize_shell_semantic_verdict(raw_verdict) or _infer_shell_semantic_verdict(candidate)
    actionability = "context_only" if verdict.get("actionability") == "context_only" else "runtime_action"
    operation_type = ("context" if actionability == "context_only"
                      else (_normalize_runtime_operation_type(verdict.get("operation_type"))
                            or block.get("operationType") or "guard"))
    action = "context" if actionability == "context_only" else _operation_action(operation_type)
    classification = _normalize_runtime_classification(verdict.get("classification"))
    normalized_classification = classification or (
        "context_only" if actionability == "context_only"
        else ("condition" if operation_type == "guard" else "emit_reminder"))
    targets = _normalize_runtime_targets(verdict.get("targets"))
    conditions = _normalize_runtime_conditions(verdict.get("conditions"))
    effects = _normalize_runtime_effects(verdict.get("effects"))
    conf = _to_number(verdict.get("confidence"))
    confidence = _clamp(conf, 0, 1) if conf is not None else 0.68

    result = {
        **block,
        "operationType": operation_type,
        "action": action,
        "target": (targets[0]["value"] if targets else None) or block.get("target") or block.get("callee"),
        "targets": targets,
        "conditions": conditions,
        "effects": effects,
        "inputs": _build_runtime_block_inputs(operation_type, conditions, candidate),
        "outputs": _build_runtime_block_outputs(operation_type, targets),
        "confidence": confidence,
        "excludeFromFlow": actionability == "context_only",
        "excludeFromTypeAnalysis": actionability == "context_only",
        "excludeFromImplicitLlmEdge": actionability == "context_only",
        "semanticGate": {
            "classification": normalized_classification,
            "actionability": actionability,
            "grammar": verdict.get("grammar") or candidate["syntax"],
            "completed_sentence": verdict.get("completed_sentence") or "",
            "reason": verdict.get("reason") or "Shell runtime block semantic candidate",
            "confidence": confidence,
            "method": "script_semantic_llm_gate" if raw_verdict else "script_rule_candidate_gate",
        },
    }
    if llm_attempted and not raw_verdict:
        result["semanticGate"]["requires_review"] = True
    return result


def _apply_shell_semantic_error(block: dict, error) -> dict:
    """Port of applyShellSemanticError (script-flow-extractor.js:906-933)."""
    reason = str(getattr(error, "args", None) and error.args[0] if getattr(error, "args", None) else (error or "Shell semantic LLM gate failed"))[:500]
    return {
        **block,
        "operationType": "context",
        "action": "context",
        "target": block.get("target") or block.get("callee"),
        "targets": [],
        "conditions": [],
        "effects": [],
        "inputs": [],
        "outputs": [],
        "confidence": 0.25,
        "excludeFromFlow": True,
        "excludeFromTypeAnalysis": True,
        "excludeFromImplicitLlmEdge": True,
        "semanticGate": {
            "classification": "context_only",
            "actionability": "context_only",
            "grammar": "shell conditional block" if block.get("kind") == "if" else "shell output block",
            "completed_sentence": "",
            "reason": reason,
            "confidence": 0.25,
            "method": "script_semantic_llm_error",
            "requires_review": True,
        },
    }


_SCRIPT_SEMANTIC_SYSTEM = " ".join([
    "You classify shell runtime implementation blocks for FCG.",
    'Return strict JSON only: {"results":[...]} with one result per candidate id.',
    "Classify actual runtime semantics: condition, guard, emit_reminder, route_to_file, write_artifact, read_env, external_call, context_only.",
    "Analyze shell syntax and the emitted natural-language text together.",
    "For heredoc/echo reminders, identify conditions, route targets, receivers, and whether the block emits a reminder rather than executing the suggested action.",
    "Do not invent routes from comments, headings, templates, or examples.",
    "Each runtime_action must be grounded in the candidate source span.",
])


def _call_shell_semantic_model(candidates: list, options: dict):
    """Port of callShellSemanticModel (script-flow-extractor.js:935-982)."""
    endpoint = _resolve_script_semantic_llm_endpoint(options)
    model = options.get("llmModel") or os.environ.get("LLM_MODEL") or "gpt-5.5"
    user_payload = {
        "prompt_version": SCRIPT_SEMANTIC_PROMPT_VERSION,
        "output_schema": {
            "results": [{
                "id": "candidate id",
                "classification": "condition|guard|emit_reminder|route_to_file|write_artifact|read_env|external_call|context_only",
                "actionability": "runtime_action|context_only",
                "grammar": "shell syntax and English grammar summary",
                "completed_sentence": "normalized sentence",
                "operation_type": "condition|guard|write|read|transform|invoke_tool|external_egress|verify|produce_artifact",
                "targets": [{"type": "file|artifact|object|external|command", "value": "...", "raw": "..."}],
                "conditions": [{"type": "...", "text": "..."}],
                "effects": ["validate|branch|persist_state|read_context|call_tool|network_egress|summarize"],
                "confidence": 0.0,
                "reason": "short grounded reason",
            }],
        },
        "candidates": candidates,
    }
    payload = post_json_with_timeout(endpoint, {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": _SCRIPT_SEMANTIC_SYSTEM},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    }, {
        "timeout_ms": int(options.get("llmTimeout") or 180000),
        "headers": {"Authorization": f"Bearer {options.get('llmApiKey')}"},
    })
    choices = (payload or {}).get("choices") or []
    message = choices[0].get("message") if choices else {}
    return normalize_assistant_content((message or {}).get("content"))


def _resolve_script_semantic_llm_endpoint(options: dict) -> str:
    """Port of resolveScriptSemanticLlmEndpoint (script-flow-extractor.js:984-991)."""
    if options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT"):
        return options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT")
    provider = str(options.get("llmProvider") or os.environ.get("LLM_PROVIDER") or "openai").lower()
    if provider == "dashscope":
        return os.environ.get("DASHSCOPE_ENDPOINT") or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    return "https://api.openai.com/v1/chat/completions"


def _normalize_shell_batch_result(raw) -> dict:
    """Port of normalizeShellBatchResult (script-flow-extractor.js:993-1002)."""
    parsed = parse_loose_json(raw)
    if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
        results = parsed["results"]
    elif isinstance(parsed, list):
        results = parsed
    else:
        results = []
    by_id = {}
    for result in results:
        rid = str((result or {}).get("id") or "").strip() if isinstance(result, dict) else ""
        if rid:
            by_id[rid] = result
    return by_id


def _build_shell_runtime_candidate(block: dict) -> dict:
    """Port of buildShellRuntimeCandidate (script-flow-extractor.js:1004-1020)."""
    return {
        "id": f"shell:{block['line']}:{block.get('kind')}",
        "kind": block.get("kind"),
        "line": block["line"],
        "syntax": "shell conditional block" if block.get("kind") == "if" else "shell heredoc/output block",
        "source": block.get("snippet") or block.get("text") or "",
        "output_text": block.get("text") or "" if block.get("kind") == "heredoc" else "",
        "condition_text": _first_line(block.get("text")) if block.get("kind") == "if" else "",
        "prompt": " ".join([
            "Classify this shell runtime block for FCG.",
            "Return JSON: classification, actionability, grammar, completed_sentence, operation_type, targets, conditions, effects, confidence, reason.",
            "Allowed classification: condition, guard, emit_reminder, route_to_file, write_artifact, read_env, external_call, context_only.",
            "Only runtime actions should be actionability=runtime_action.",
        ]),
    }


def _normalize_shell_semantic_verdict(raw):
    """Port of normalizeShellSemanticVerdict (script-flow-extractor.js:1022-1032)."""
    if not raw:
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except ValueError:
            return None
    return raw if isinstance(raw, dict) else None


_MD_FILE_TARGET_RE = re.compile(r"(?:^|[\s`'\"])([./~A-Za-z0-9_-]+(?:/[A-Za-z0-9_.-]+)*\.md)\b")


def _infer_shell_semantic_verdict(candidate: dict | None = None) -> dict:
    """Port of inferShellSemanticVerdict (script-flow-extractor.js:1034-1074)."""
    candidate = candidate or {}
    text = f"{candidate.get('source') or ''}\n{candidate.get('output_text') or ''}"
    lower = text.lower()
    targets = []
    for match in _MD_FILE_TARGET_RE.finditer(text):
        value = re.sub(r"^['\"`\s]+", "", match.group(1)).strip()
        targets.append({"type": "file", "value": value, "raw": value})
    if re.search(r"skill extraction|extract.*skill|consider skill extraction", lower):
        targets.append({"type": "artifact", "value": "skill_extraction", "raw": "skill extraction"})
    conditions = []
    if re.search(r"contains_error", lower):
        conditions.append({"type": "error_detected", "text": "contains_error is true"})
    if re.search(r"\bif yes\b", lower):
        conditions.append({"type": "affirmative_learning_candidate", "text": "If yes"})
    if re.search(r"high-value|recurring|broadly applicable", lower):
        conditions.append({"type": "high_value_learning", "text": "high-value, recurring, or broadly applicable"})
    if re.search(r"claude_tool_output", lower):
        targets.append({"type": "object", "value": "CLAUDE_TOOL_OUTPUT", "raw": "CLAUDE_TOOL_OUTPUT"})
    operation_type = "guard" if (candidate.get("kind") == "if" or conditions) else "write"
    return {
        "classification": "emit_reminder" if re.search(
            r"<[^>]+>|reminder|detected|consider logging|log to|consider skill extraction", lower)
            else ("condition" if candidate.get("kind") == "if" else "context_only"),
        "actionability": "runtime_action" if re.search(
            r"<[^>]+>|reminder|detected|consider logging|log to|consider skill extraction|contains_error", lower)
            else "context_only",
        "grammar": candidate.get("syntax"),
        "operation_type": operation_type,
        "targets": targets,
        "conditions": conditions,
        "effects": ["validate", "branch"] if operation_type == "guard" else ["persist_state"],
        "confidence": 0.62,
        "reason": "Rule candidate for shell runtime block; LLM semantic gate can refine this.",
    }


_RUNTIME_OP_TYPES = {"condition", "guard", "write", "read", "transform", "invoke_tool",
                     "external_egress", "verify", "produce_artifact", "context"}
_RUNTIME_CLASSIFICATIONS = {"condition", "guard", "emit_reminder", "route_to_file",
                            "write_artifact", "read_env", "external_call", "context_only"}
_RUNTIME_EFFECTS_ALLOWED = {"read_context", "persist_state", "call_tool", "update_memory",
                            "summarize", "validate", "branch", "network_egress"}


def _normalize_runtime_operation_type(value) -> str:
    text = str(value or "").strip()
    return text if text in _RUNTIME_OP_TYPES else ""


def _normalize_runtime_classification(value) -> str:
    text = str(value or "").strip()
    return text if text in _RUNTIME_CLASSIFICATIONS else ""


def _normalize_runtime_targets(targets=None) -> list:
    """Port of normalizeRuntimeTargets (script-flow-extractor.js:1090-1100)."""
    mapped = []
    for target in (targets if isinstance(targets, list) else []):
        if not isinstance(target, dict):
            continue
        type_ = str(target.get("type") or "").strip() or "object"
        value = str(target.get("value") or "").strip()
        if not value:
            continue
        mapped.append({"type": type_, "value": value, "raw": str(target.get("raw") or value)})
    return _dedupe_objects(mapped, lambda item: f"{item['type']}:{item['value']}")


def _normalize_runtime_conditions(conditions=None) -> list:
    """Port of normalizeRuntimeConditions (script-flow-extractor.js:1102-1111)."""
    mapped = []
    for condition in (conditions if isinstance(conditions, list) else []):
        if not isinstance(condition, dict):
            continue
        text = str(condition.get("text") or "").strip()
        if not text:
            continue
        mapped.append({"type": str(condition.get("type") or "condition").strip() or "condition", "text": text})
    return _dedupe_objects(mapped, lambda item: f"{item['type']}:{item['text']}")


def _normalize_runtime_effects(effects=None) -> list:
    """Port of normalizeRuntimeEffects (script-flow-extractor.js:1113-1118)."""
    seen = []
    for effect in (effects if isinstance(effects, list) else []):
        e = str(effect or "").strip()
        if e in _RUNTIME_EFFECTS_ALLOWED and e not in seen:
            seen.append(e)
    return seen


def _build_runtime_block_inputs(operation_type: str, conditions: list, candidate: dict) -> list:
    """Port of buildRuntimeBlockInputs (script-flow-extractor.js:1120-1129)."""
    if operation_type == "context":
        return []
    inputs = []
    if conditions or []:
        inputs.append({"name": "condition_signal", "type": "condition"})
    if re.search(r"CLAUDE_TOOL_OUTPUT", candidate.get("source") or "", re.IGNORECASE):
        inputs.append({"name": "CLAUDE_TOOL_OUTPUT", "type": "env"})
    if not inputs and operation_type in ("guard", "verify", "write", "transform"):
        inputs.append({"name": "runtime_context", "type": "context"})
    return inputs


def _build_runtime_block_outputs(operation_type: str, targets: list) -> list:
    """Port of buildRuntimeBlockOutputs (script-flow-extractor.js:1131-1136)."""
    if operation_type == "context":
        return []
    if operation_type in ("guard", "condition"):
        return [{"name": "branch_state", "type": "object"}]
    if targets or []:
        return [{"name": t["value"], "type": t.get("type") or "object"} for t in targets]
    return [{"name": "runtime_output", "type": "string"}]


# --- heredoc / block scanning ---------------------------------------------

_HEREDOC_RE = re.compile(r"<<\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")


def _collect_heredoc_ranges(lines: list) -> list:
    """Port of collectHeredocRanges (script-flow-extractor.js:1138-1156)."""
    ranges = []
    i = 0
    n = len(lines)
    while i < n:
        line = str(lines[i] or "")
        match = _HEREDOC_RE.search(line)
        if not match:
            i += 1
            continue
        marker = match.group(1)
        end_line = i + 1
        for j in range(i + 1, n):
            if str(lines[j] or "").strip() == marker:
                end_line = j + 1
                break
        ranges.append({"startLine": i + 1, "endLine": end_line})
        i = max(i, end_line - 1)
        i += 1
    return ranges


def _is_line_in_ranges(line: int, ranges: list, *, include_start: bool = True, include_end: bool = True) -> bool:
    """Port of isLineInRanges (script-flow-extractor.js:1158-1164)."""
    for rng in ranges or []:
        start = rng["startLine"] + 1 if include_start is False else rng["startLine"]
        end = rng["endLine"] - 1 if include_end is False else rng["endLine"]
        if start <= line <= end:
            return True
    return False


def _find_shell_block_end(lines: list, start_line: int, terminal: str) -> int:
    """Port of findShellBlockEnd (script-flow-extractor.js:1166-1171)."""
    for i in range(start_line, len(lines)):
        if str(lines[i] or "").strip() == terminal:
            return i + 1
    return min(len(lines), start_line + 1)


def _infer_heredoc_callee(text: str) -> str:
    """Port of inferHeredocCallee (script-flow-extractor.js:1173-1178)."""
    lower = str(text or "").lower()
    if "error-detected" in lower:
        return "shell.emit_error_reminder"
    if "self-improvement-reminder" in lower:
        return "shell.emit_self_improvement_reminder"
    return "shell.emit_heredoc"


# --- small helpers --------------------------------------------------------

def _dedupe_objects(items: list, key_fn) -> list:
    """Port of dedupeObjects (script-flow-extractor.js:1180-1190)."""
    seen = set()
    result = []
    for item in items or []:
        key = key_fn(item)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def _fallback_script_entry(content: str, rel_path: str, method: str) -> dict:
    """Port of fallbackScriptEntry (script-flow-extractor.js:1200-1206)."""
    node = _create_script_entry_node(content, rel_path, "script", 1)
    node["formal_semantics"]["confidence"] = 0.35
    node["formal_semantics"]["evidence"]["method"] = method
    node["source_context"]["action_evidence"]["requires_review"] = True
    return {"nodes": [node], "edges": []}


def _finalize_shell_function(active: dict) -> dict:
    """Port of finalizeShellFunction (script-flow-extractor.js:1208-1218)."""
    snippet = "\n".join(active.get("body") or [])[:800]
    return {
        "name": active["name"],
        "line": active["line"],
        "column": active["column"],
        "startLine": active["startLine"],
        "endLine": active["endLine"],
        "snippet": snippet,
    }


def _strip_shell_comment(line: str) -> str:
    """Port of stripShellComment (script-flow-extractor.js:1230-1241)."""
    value = str(line or "")
    in_single = False
    in_double = False
    for i, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        if ch == '"' and not in_single:
            in_double = not in_double
        if ch == "#" and not in_single and not in_double:
            return value[:i]
    return value


def _is_shell_script(file_path: str) -> bool:
    """Port of isShellScript (script-flow-extractor.js:1243-1250)."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            first_line = handle.readline().rstrip("\n").rstrip("\r")
    except OSError:
        return False
    return bool(re.match(r"^#!.*\b(?:bash|sh)\b", first_line))


def _first_non_empty_line(content: str) -> str:
    """Port of firstNonEmptyLine (script-flow-extractor.js:1257-1259)."""
    for line in re.split(r"\r?\n", str(content or "")):
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _first_line(value) -> str:
    """Port of firstLine (script-flow-extractor.js:1261-1263)."""
    return re.split(r"\r?\n", str(value or ""))[0].strip()


def _line_at(content: str, line) -> str:
    """Port of lineAt (script-flow-extractor.js:1265-1267)."""
    parts = re.split(r"\r?\n", str(content or ""))
    idx = max(0, int(line or 1) - 1)
    return parts[idx] if idx < len(parts) else ""


def _count_char(value: str, char: str) -> int:
    """Port of countChar (script-flow-extractor.js:1269-1271)."""
    return str(value or "").count(char)


def _stable_slug(value) -> str:
    """Port of stableSlug (script-flow-extractor.js:1273-1281)."""
    text = str(value if value not in (None, "") else "script")
    slug = re.sub(r"^_+|_+$", "", re.sub(r"[^a-zA-Z0-9]+", "_", text.replace("\\", "/"))).lower()
    return slug or "script"


def _dedupe_by_name(nodes: list) -> list:
    """Port of dedupeByName (script-flow-extractor.js:1283-1293)."""
    seen = set()
    result = []
    for node in nodes or []:
        key = node.get("name") or ""
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(node)
    return result


def _dedupe_edges(edges: list) -> list:
    """Port of dedupeEdges (script-flow-extractor.js:1295-1305)."""
    seen = set()
    result = []
    for edge in edges or []:
        key = f"{edge['source']}->{edge['target']}:{edge.get('semantic_reason') or edge.get('type')}"
        if key in seen:
            continue
        seen.add(key)
        result.append({**edge, "id": f"script_flow_{len(result) + 1}"})
    return result


def _to_number(value):
    """JS Number(x) for a finite value, else None (mirrors Number.isFinite guard)."""
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    if n != n or n in (float("inf"), float("-inf")):
        return None
    return n


def _at(seq: list, index: int) -> str:
    return seq[index] if 0 <= index < len(seq) else ""
