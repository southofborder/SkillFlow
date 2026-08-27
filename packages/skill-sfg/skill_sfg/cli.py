"""skill-sfg CLI (rule-only Python SFG analyzer — Skill Flow Graph).

Usage:
    skill-sfg analyze <input> [--output <file>] [--mode quick|full|deep]
                               [--no-cycle-expand]

<input> is a skill directory (containing SKILL.md) or a .zip of one. Produces the
v6 SFG JSON on stdout (or --output). RULE-ONLY: no LLM calls — this is the
deterministic, network-free path the M4 verdict-equivalence oracle uses.

Declared as the `skill-sfg` console entry in pyproject.toml.
"""

import argparse
import json
import os
import sys
import tempfile
import zipfile

from .analyzer.pipeline import run_pipeline
from .output.json_generator import build_fcg_json


def _find_skill_root(base_dir):
    """Return the directory that directly contains SKILL.md (base or one level
    down — zips often wrap the skill in a top folder)."""
    if os.path.isfile(os.path.join(base_dir, "SKILL.md")):
        return base_dir
    for entry in sorted(os.listdir(base_dir)):
        candidate = os.path.join(base_dir, entry)
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "SKILL.md")):
            return candidate
    return base_dir


def _analyze(input_path, mode, cycle_expand, input_source):
    """Resolve input (dir or zip) → run pipeline → build v6 JSON."""
    if os.path.isdir(input_path):
        skill_root = _find_skill_root(input_path)
        result = run_pipeline(skill_root, {"mode": mode, "cycle_expand": cycle_expand})
        return build_fcg_json(result, input_source=input_source)

    if zipfile.is_zipfile(input_path):
        with tempfile.TemporaryDirectory(prefix="skill-sfg-") as tmp:
            with zipfile.ZipFile(input_path) as zf:
                zf.extractall(tmp)
            skill_root = _find_skill_root(tmp)
            result = run_pipeline(skill_root, {"mode": mode, "cycle_expand": cycle_expand})
            return build_fcg_json(result, input_source=input_source)

    raise SystemExit(f"Input is neither a directory nor a zip: {input_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="skill-sfg", description="Rule-only Python SFG analyzer (v6 output).")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a skill directory or zip → v6 SFG JSON.")
    analyze.add_argument("input", help="Skill directory (with SKILL.md) or .zip of one.")
    analyze.add_argument("--output", "-o", default=None, help="Write JSON here instead of stdout.")
    analyze.add_argument("--mode", default="full", choices=["quick", "full", "deep"], help="Analysis mode.")
    analyze.add_argument("--no-cycle-expand", dest="cycle_expand", action="store_false",
                         help="Disable real-cycle expansion in the transfer layer.")
    analyze.set_defaults(cycle_expand=True)

    args = parser.parse_args(argv)
    if args.command != "analyze":
        parser.error(f"unknown command: {args.command}")

    input_path = os.path.abspath(args.input)
    fcg = _analyze(input_path, args.mode, args.cycle_expand, input_source=input_path)
    text = json.dumps(fcg, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
        sys.stderr.write(f"[ok] wrote {args.output}\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
