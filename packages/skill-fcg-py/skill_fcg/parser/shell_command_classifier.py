"""Shared shell-command classifier — port of src/parser/shell-command-classifier.js.

Deterministic, rule-only. Both the markdown code-block path and the script/tool
paths use this so command-level operation typing never drifts. Given a raw
shell line it splits compound commands and classifies each segment into an FCG
operation_type with concrete targets (egress hosts, r/w file paths).

Fidelity: the JS regexes use ASCII ``\\w``/``\\b``/``\\d`` semantics, so the
ported patterns carry ``re.ASCII`` to avoid Python's default Unicode widening.
"""

from __future__ import annotations

import re

# Command-name based classification. Ordered by specificity.
EGRESS_COMMANDS = {"curl", "wget", "http", "https", "httpie", "nc", "ncat",
                   "telnet", "ssh", "scp", "rsync", "ftp", "sftp"}
EXEC_COMMANDS = {"bash", "sh", "zsh", "node", "python", "python3", "ruby", "perl",
                 "php", "deno", "bun", "npx", "pnpm", "yarn", "npm", "pip", "pip3",
                 "make", "docker", "kubectl", "git"}
READ_COMMANDS = {"cat", "less", "more", "head", "tail", "grep", "rg", "find",
                 "ls", "stat", "read", "awk", "sed", "jq"}
WRITE_COMMANDS = {"tee", "touch", "mkdir", "cp", "mv", "rm", "chmod", "chown", "ln", "dd"}

_URL_RE = re.compile(r"\bhttps?://[^\s\"'`)]+", re.IGNORECASE | re.ASCII)
_BARE_HOST_RE = re.compile(
    r"[\"']?([a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+)(?:/[^\s\"'`]*)?[\"']?",
    re.IGNORECASE | re.ASCII)
_REDIRECT_FILE_RE = re.compile(
    r">>?\s*(\"?[~./\w-]+(?:/[~./\w-]+)*\.\w+\"?|\"?/dev/[\w/]+\"?)", re.ASCII)
_FILE_PATH_RE = re.compile(
    r"(\"?(?:\.{0,2}/)?[\w-]+(?:/[\w.-]+)*\.[a-z0-9]{1,6}\"?)", re.IGNORECASE | re.ASCII)

_HOST_FILE_EXT_RE = re.compile(r"\.(?:md|json|txt|log|sh|js|ts|png|jpg|csv|yml|yaml)$", re.IGNORECASE)
_HOST_FROM_URL_RE = re.compile(r"^https?://([^/\s\"'`]+)", re.IGNORECASE)

_SEGMENT_SPLIT_RE = re.compile(r"\|{1,2}|&&|;|\band\b(?=\s)", re.ASCII)
_CONTROL_KW_RE = re.compile(r"^(?:if|then|do|while|until|for|else|elif)\s+")
_VAR_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S*)\s+")
_WRAPPER_RE = re.compile(r"^(?:sudo|command|builtin|exec|time|env)$")
_QUOTE_EDGE_RE = re.compile(r"^['\"]|['\"]$")

_COMMENT_RE = re.compile(r"^#")
_SHEBANG_RE = re.compile(r"^#!")
_TERMINATOR_RE = re.compile(r"^(?:then|do|fi|done|else|elif|esac|;;)\b")
_FUNCTION_DEF_RE = re.compile(r"^(?:function\s+)?[A-Za-z_][A-Za-z0-9_-]*\s*(?:\(\))?\s*\{")
_BARE_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_ASSIGN_HAS_CMD_RE = re.compile(r"[|&;<>()]|\$\(")
_REDIRECT_WRITE_RE = re.compile(r">>?\s*[^&\s]")
_TEE_RE = re.compile(r"\btee\b")
_NOOP_CMD_RE = re.compile(r"^(?:echo|printf|true|false|cd|export|set|unset|local|return|exit|shift|eval|source|\.)$")


def split_command_segments(line: str) -> list:
    """Port of splitCommandSegments (shell-command-classifier.js:33-38)."""
    return [seg for seg in (s.strip() for s in _SEGMENT_SPLIT_RE.split(str(line or ""))) if seg]


def segment_command_name(segment: str) -> str:
    """Port of segmentCommandName (shell-command-classifier.js:46-62)."""
    rest = str(segment or "").strip()
    rest = _CONTROL_KW_RE.sub("", rest, count=1)
    while _VAR_ASSIGN_RE.match(rest):
        rest = _VAR_ASSIGN_RE.sub("", rest, count=1)
    parts = [p for p in re.split(r"\s+", rest) if p]
    if not parts:
        return ""
    idx = 0
    while idx < len(parts) and _WRAPPER_RE.match(parts[idx]):
        idx += 1
    name = parts[idx] if idx < len(parts) else ""
    name = _QUOTE_EDGE_RE.sub("", name)
    return re.sub(r"^\\", "", name)


def extract_command_targets(segment: str, operation_type: str) -> list:
    """Port of extractCommandTargets (shell-command-classifier.js:70-120)."""
    text = str(segment or "")
    targets: list = []
    seen: set = set()

    def push(kind: str, value, raw) -> None:
        cleaned = _QUOTE_EDGE_RE.sub("", str(value or "")).strip()
        if not cleaned:
            return
        key = f"{kind}:{cleaned}"
        if key in seen:
            return
        seen.add(key)
        targets.append({"type": kind, "value": cleaned, "raw": str(raw if raw is not None else cleaned).strip()})

    if operation_type == "external_egress":
        matched_url = False
        for m in _URL_RE.finditer(text):
            matched_url = True
            push("url", host_from_url(m.group(0)), m.group(0))
        if not matched_url:
            for m in _BARE_HOST_RE.finditer(text):
                host = m.group(1)
                if _HOST_FILE_EXT_RE.search(host):
                    continue
                push("url", host, m.group(0))

    if operation_type == "write":
        for m in _REDIRECT_FILE_RE.finditer(text):
            push("file", m.group(1), m.group(0))

    if operation_type in ("read", "write"):
        for m in _FILE_PATH_RE.finditer(text):
            push("file", m.group(1), m.group(1))

    return targets


def host_from_url(url: str) -> str:
    """Port of hostFromUrl (shell-command-classifier.js:122-125)."""
    match = _HOST_FROM_URL_RE.match(str(url or ""))
    return match.group(1) if match else str(url or "")


def classify_shell_command_line(line: str) -> list:
    """Port of classifyShellCommandLine (shell-command-classifier.js:135-161)."""
    raw = str(line or "")
    trimmed = strip_inline_comment(raw).strip()
    if not trimmed:
        return []
    if _COMMENT_RE.match(trimmed) or _SHEBANG_RE.match(raw.strip()):
        return []
    if _TERMINATOR_RE.match(trimmed):
        return []
    if _FUNCTION_DEF_RE.match(trimmed):
        return []
    if _BARE_ASSIGN_RE.match(trimmed) and not _ASSIGN_HAS_CMD_RE.search(trimmed):
        return []

    results = []
    for segment in split_command_segments(trimmed):
        command = segment_command_name(segment)
        if not command:
            continue
        operation_type = classify_command_name(command, segment)
        if not operation_type:
            continue
        results.append({
            "command": command,
            "operationType": operation_type,
            "targets": extract_command_targets(segment, operation_type),
            "segment": segment,
        })
    return results


def classify_command_name(command: str, segment: str) -> str:
    """Port of classifyCommandName (shell-command-classifier.js:170-187)."""
    name = str(command or "").lower()
    base = name.split("/")[-1]
    text = str(segment or "").lower()

    if base in EGRESS_COMMANDS:
        return "external_egress"
    if _REDIRECT_WRITE_RE.search(text) or base in WRITE_COMMANDS or _TEE_RE.search(text):
        return "write"
    if base in EXEC_COMMANDS:
        return "invoke_tool"
    if base in READ_COMMANDS:
        return "read"
    if _NOOP_CMD_RE.match(base):
        return ""
    if _URL_RE.search(text):
        return "external_egress"
    return ""


def strip_inline_comment(line: str) -> str:
    """Port of stripInlineComment (shell-command-classifier.js:189-202)."""
    value = str(line or "")
    in_single = False
    in_double = False
    for i, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double and (i == 0 or value[i - 1].isspace()):
            return value[:i]
    return value


_SHELL_FENCE_LANGS = {"bash", "sh", "shell", "console", "zsh", "ksh", "shell-session", "shellsession"}


def is_shell_fence_lang(lang: str) -> bool:
    """Port of isShellFenceLang (shell-command-classifier.js:211-213)."""
    return str(lang or "").strip().lower() in _SHELL_FENCE_LANGS
