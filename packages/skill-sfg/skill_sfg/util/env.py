"""Minimal .env loader — Python port of shared/load-env.cjs.

Loads the nearest .env (walking up from cwd / this file) into os.environ WITHOUT
overwriting variables already set in the environment, mirroring loadProjectEnv so
the standalone Python batch runner sees LLM_API_KEY / LLM_* exactly the way the
Node entrypoints do. When the Python engine is spawned as a child of the Node
pipeline the env is already inherited, so this is an idempotent no-op there.
"""

from __future__ import annotations

import os
import re

_cached = None


def load_project_env(start_dir=None, entry_file=None, force_reload=False):
    """Find + parse the nearest .env; set any keys not already in os.environ."""
    global _cached
    if _cached is not None and not force_reload:
        return _cached
    start_dirs = _unique_dirs([
        start_dir,
        os.getcwd(),
        os.path.dirname(os.path.abspath(entry_file)) if entry_file else "",
        os.path.dirname(os.path.abspath(__file__)),
    ])
    env_path = _find_nearest_env(start_dirs)
    result = {"loaded": False, "env_path": env_path or "", "values": {}}
    if not env_path:
        _cached = result
        return result
    with open(env_path, "r", encoding="utf-8") as fh:
        parsed = parse_env_file(fh.read())
    for key, value in parsed.items():
        if os.environ.get(key) is None:
            os.environ[key] = value
            result["values"][key] = value
    result["loaded"] = True
    _cached = result
    return result


_ENV_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")


def _find_nearest_env(start_dirs):
    visited = set()
    for base in start_dirs:
        current = os.path.abspath(base)
        while current not in visited:
            visited.add(current)
            candidate = os.path.join(current, ".env")
            if os.path.isfile(candidate):
                return candidate
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
    return ""


def parse_env_file(content):
    """Port of parseEnvFile — same quoting / inline-comment / escape rules."""
    values = {}
    for index, raw_line in enumerate((content or "").splitlines()):
        line_no = index + 1
        trimmed = raw_line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        match = _ENV_LINE.match(raw_line)
        if not match:
            raise ValueError(f"Malformed .env line {line_no}: {raw_line}")
        key = match.group(1)
        value = match.group(2)
        if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        else:
            comment_index = value.find(" #")
            if comment_index >= 0:
                value = value[:comment_index].rstrip()
        value = (value.replace("\\n", "\n").replace("\\r", "\r")
                 .replace("\\t", "\t").replace('\\"', '"').replace("\\'", "'"))
        values[key] = value
    return values


def _unique_dirs(values):
    seen = set()
    dirs = []
    for value in values:
        if not value:
            continue
        resolved = os.path.abspath(value)
        if resolved in seen:
            continue
        seen.add(resolved)
        dirs.append(resolved)
    return dirs
