"""Batch FCG runner — Python port of scripts/fcg-batch.js.

Discovers skills (from similarity/grouping.json or <root>/zips), analyzes each
via the Python pipeline with the LLM semantic gate enabled, writes the v6 FCG
JSON plus flowchart artifacts, and emits fcg-summary.json / fcg-summary.md.
This replaces the JS batch runner as the production entry point.

Concurrency mirrors the JS async worker pool: a ThreadPoolExecutor drains the
skill list. Blocking urllib in transport.py releases the GIL on socket wait, so
LLM calls overlap. The babel AST sidecar is a per-call subprocess (isolated),
and the semantic-gate cache appends (concurrent-safe); the label-assist cache
full-rewrites but is opt-in and idempotent (a lost write only costs one
redundant LLM call), matching the JS worker-pool's own behavior.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import cmp_to_key

from .analyzer.pipeline import run_pipeline
from .output.json_generator import build_fcg_json
from .output.flowchart_generator import save_flowchart_artifacts, derive_flowchart_paths
from .util.locale import locale_compare

_HERE = os.path.abspath(__file__)
# skill_sfg/batch.py -> skill_sfg -> skill-sfg -> packages -> <project root>
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))


def parse_args(args):
    """Port of parseArgs — same flags, same 'Unknown argument' error."""
    options = {}
    i = 0
    n = len(args)
    while i < n:
        arg = args[i]
        if arg in ("--help", "-h"):
            options["help"] = True
        elif arg == "--root" and i + 1 < n:
            i += 1
            options["root"] = args[i]
        elif arg == "--similarity-root" and i + 1 < n:
            i += 1
            options["similarityRoot"] = args[i]
        elif arg == "--output" and i + 1 < n:
            i += 1
            options["output"] = args[i]
        elif arg == "--scope" and i + 1 < n:
            i += 1
            options["scope"] = args[i]
        elif arg == "--concurrency" and i + 1 < n:
            i += 1
            options["concurrency"] = float(args[i])
        elif arg == "--mode" and i + 1 < n:
            i += 1
            options["mode"] = args[i]
        elif arg == "--llm-timeout" and i + 1 < n:
            i += 1
            options["llmTimeout"] = float(args[i])
        elif arg == "--label-llm-assist":
            options["labelLlmAssist"] = True
        elif arg == "--label-llm-concurrency" and i + 1 < n:
            i += 1
            options["labelLlmConcurrency"] = float(args[i])
        elif arg == "--label-llm-cache" and i + 1 < n:
            i += 1
            options["labelLlmCache"] = args[i]
        elif arg == "--semantic-gate-cache" and i + 1 < n:
            i += 1
            options["semanticGateCache"] = args[i]
        elif arg == "--refresh":
            options["refresh"] = True
        elif arg == "--only" and i + 1 < n:
            i += 1
            options["only"] = args[i]
        else:
            raise ValueError(f"Unknown argument: {arg}")
        i += 1
    return options


def _resolve_semantic_gate_cache_option(value, root):
    """Port of resolveSemanticGateCacheOption. Returns False (disabled) or an
    absolute path. '0'/'false' disable; explicit path honored; default under
    <root>/fcg."""
    if value is False:
        return False
    text = value.strip() if isinstance(value, str) else ""
    if text == "0" or text.lower() == "false":
        return False
    if text:
        return os.path.abspath(text)
    return os.path.join(root, "fcg", "semantic-gate-cache.jsonl")


def resolve_options(options=None):
    """Port of resolveOptions — same defaults + env fallbacks + validation."""
    options = options or {}
    if options.get("help"):
        return {"help": True}
    root = os.path.abspath(
        options.get("root") or os.path.join(_PROJECT_ROOT, "results", "clawhub-top10000")
    )

    def _num(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    resolved = {
        "root": root,
        "similarityRoot": os.path.abspath(
            options.get("similarityRoot") or os.path.join(root, "similarity")
        ),
        "output": os.path.abspath(options.get("output") or os.path.join(root, "fcg")),
        "scope": options.get("scope") or "all",
        "concurrency": int(_num(options.get("concurrency", 4), 4)),
        "mode": options.get("mode") or "full",
        "labelLlmAssist": bool(options.get("labelLlmAssist")),
        "labelLlmConcurrency": int(_num(options.get("labelLlmConcurrency", 2), 2)),
        "labelLlmCache": os.path.abspath(
            options.get("labelLlmCache") or os.path.join(root, "fcg", "label-llm-cache.jsonl")
        ),
        "dependencyLlmCache": os.path.abspath(
            options.get("dependencyLlmCache")
            or os.path.join(root, "fcg", "dependency-llm-cache.jsonl")
        ),
        "semanticGateCache": _resolve_semantic_gate_cache_option(
            options.get("semanticGateCache"), root
        ),
        "refresh": bool(options.get("refresh")),
        "only": options["only"].strip() if isinstance(options.get("only"), str) else "",
        "llmProvider": options.get("llmProvider") or os.environ.get("LLM_PROVIDER") or "openai",
        "llmModel": options.get("llmModel") or os.environ.get("LLM_MODEL") or "gpt-5.5",
        "llmApiKey": options["llmApiKey"] if "llmApiKey" in options else (os.environ.get("LLM_API_KEY") or ""),
        "llmEndpoint": options.get("llmEndpoint") or os.environ.get("LLM_ENDPOINT") or "",
        "llmTimeout": int(_num(options.get("llmTimeout") or os.environ.get("LLM_TIMEOUT") or 180000, 180000)),
    }
    validate_options(resolved)
    return resolved


def validate_options(options):
    """Port of validateOptions — same messages, same LLM_API_KEY requirement."""
    if options["scope"] not in ("all", "grouped", "ungrouped"):
        raise ValueError("--scope must be all, grouped, or ungrouped")
    if options["mode"] not in ("quick", "full", "deep"):
        raise ValueError("--mode must be quick, full, or deep")
    if not isinstance(options["concurrency"], int) or options["concurrency"] <= 0:
        raise ValueError("--concurrency must be a positive integer")
    if options["labelLlmAssist"] and not str(options.get("llmApiKey") or "").strip():
        raise ValueError("LLM_API_KEY is required when --label-llm-assist is enabled")
    if not str(options.get("llmApiKey") or "").strip():
        raise ValueError("LLM_API_KEY is required for FCG Markdown semantic gate")


def discover_skills(root, similarity_root, scope="all"):
    """Port of discoverSkills — grouping.json takes priority over <root>/zips."""
    grouping_path = os.path.join(similarity_root, "grouping.json")
    if os.path.exists(grouping_path):
        return discover_skills_from_grouping(grouping_path, scope)
    return discover_skills_from_zips(os.path.join(root, "zips"), scope)


def discover_skills_from_grouping(grouping_path, scope="all"):
    """Port of discoverSkillsFromGrouping."""
    with open(grouping_path, "r", encoding="utf-8") as fh:
        grouping = json.load(fh)

    group_by_skill_id = {}
    for group in grouping.get("groups") or []:
        for member in group.get("members") or []:
            if member.get("skill_id"):
                group_by_skill_id[member["skill_id"]] = group.get("group_id") or ""

    ungrouped_ids = {
        item.get("skill_id")
        for item in (grouping.get("ungrouped") or [])
        if item.get("skill_id")
    }

    base_dir = os.path.dirname(grouping_path)
    skills = []
    for index, skill in enumerate(grouping.get("skills") or []):
        group_id = group_by_skill_id.get(skill.get("id")) or ""
        is_ungrouped = (skill.get("id") in ungrouped_ids) or not group_id
        skills.append({
            "skill_id": skill.get("id") or f"skill_{index + 1}",
            "skill_name": skill.get("skill_name") or skill.get("name") or skill.get("id") or f"skill_{index + 1}",
            "zip_path": _resolve_zip_path(skill.get("zip_path"), base_dir),
            "zip_name": skill.get("zip_name") or os.path.basename(skill.get("zip_path") or ""),
            "group_id": group_id,
            "is_ungrouped": is_ungrouped,
            "readme_missing": bool(skill.get("readme_missing")),
        })
    return filter_by_scope(skills, scope)


def discover_skills_from_zips(zips_dir, scope="all"):
    """Port of discoverSkillsFromZips — skill_NNNN zero-padded, localeCompare sort."""
    if scope == "grouped":
        return []
    if not os.path.exists(zips_dir):
        raise ValueError(f"Neither grouping.json nor zips directory found: {zips_dir}")
    names = [n for n in os.listdir(zips_dir) if re.search(r"\.zip$", n, re.IGNORECASE)]
    names.sort(key=cmp_to_key(locale_compare))
    skills = []
    for index, name in enumerate(names):
        skills.append({
            "skill_id": f"skill_{index + 1:04d}",
            "skill_name": re.sub(r"\.zip$", "", name, flags=re.IGNORECASE),
            "zip_path": os.path.join(zips_dir, name),
            "zip_name": name,
            "group_id": "",
            "is_ungrouped": True,
            "readme_missing": False,
        })
    return skills


def filter_by_scope(skills, scope):
    """Port of filterByScope."""
    if scope == "grouped":
        return [s for s in skills if not s["is_ungrouped"]]
    if scope == "ungrouped":
        return [s for s in skills if s["is_ungrouped"]]
    return skills


def apply_only_filter(skills, only):
    """Port of applyOnlyFilter — comma tokens, lowercase substring match on
    '<skill_id> <skill_name> <zip_name>', AFTER numbering. Empty = no-op."""
    tokens = [t.strip().lower() for t in str(only or "").split(",")]
    tokens = [t for t in tokens if t]
    if not tokens:
        return skills
    out = []
    for skill in skills:
        hay = f"{skill.get('skill_id') or ''} {skill.get('skill_name') or ''} {skill.get('zip_name') or ''}".lower()
        if any(t in hay for t in tokens):
            out.append(skill)
    return out


def _resolve_zip_path(zip_path, base_dir):
    """Port of resolveZipPath."""
    if not zip_path:
        return ""
    if os.path.isabs(zip_path):
        return os.path.abspath(zip_path)
    return os.path.abspath(os.path.join(base_dir, zip_path))


def _find_skill_root(base_dir):
    """Return the dir directly containing SKILL.md (base or one level down)."""
    if os.path.isfile(os.path.join(base_dir, "SKILL.md")):
        return base_dir
    for entry in sorted(os.listdir(base_dir)):
        candidate = os.path.join(base_dir, entry)
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "SKILL.md")):
            return candidate
    return base_dir


def analyze_zip(zip_path, options):
    """Python equivalent of analyzer.analyze(zip_path): extract → pipeline → v6 JSON.

    Threads LLM credentials into run_pipeline (disableLlm=False + semantic gate)
    and label-assist options into build_fcg_json. input_source is the zip path,
    matching the JS analyzer which records the archive as the source.
    """
    pipeline_options = {
        "mode": options["mode"],
        "cycle_expand": True,
        "disableLlm": False,
        "semanticLlm": True,
        "llmProvider": options["llmProvider"],
        "llmModel": options["llmModel"],
        "llmApiKey": options["llmApiKey"],
        "llmEndpoint": options["llmEndpoint"],
        "llmTimeout": options["llmTimeout"],
        "semanticGateCache": options["semanticGateCache"],
    }
    json_options = {
        "labelLlmAssist": options["labelLlmAssist"],
        "llmProvider": options["llmProvider"],
        "llmModel": options["llmModel"],
        "llmApiKey": options["llmApiKey"],
        "llmEndpoint": options["llmEndpoint"],
        "llmTimeout": options["llmTimeout"],
        "labelLlmConcurrency": options["labelLlmConcurrency"],
        "labelLlmCache": options["labelLlmCache"],
    }
    with tempfile.TemporaryDirectory(prefix="skill-sfg-") as tmp:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)
        skill_root = _find_skill_root(tmp)
        result = run_pipeline(skill_root, pipeline_options)
        return build_fcg_json(result, input_source=zip_path, options=json_options)


def analyze_or_reuse_skill(skill, options):
    """Port of analyzeOrReuseSkill — reuse existing JSON unless --refresh."""
    output_path = build_fcg_output_path(skill, options["output"])
    try:
        zip_path = skill.get("zip_path")
        if not zip_path or not os.path.exists(zip_path):
            raise ValueError(f"Skill zip not found: {zip_path or '<empty>'}")

        if not options["refresh"] and os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as fh:
                fcg_json = json.load(fh)
            ensure_flowchart_artifacts(fcg_json, output_path)
            return build_result(skill, output_path, True, fcg_json)

        fcg_json = analyze_zip(zip_path, options)
        _save_json(output_path, fcg_json)
        ensure_flowchart_artifacts(fcg_json, output_path)
        return build_result(skill, output_path, False, fcg_json)
    except Exception as error:  # noqa: BLE001 — mirror JS: any failure → error record
        return {
            "error": {
                "skill_id": skill.get("skill_id"),
                "skill_name": skill.get("skill_name"),
                "zip_path": skill.get("zip_path"),
                "fcg_path": output_path,
                "message": str(error),
            }
        }


def ensure_flowchart_artifacts(fcg_json, output_path):
    """Port of ensureFlowchartArtifacts."""
    flow_paths = derive_flowchart_paths(output_path)
    save_flowchart_artifacts(fcg_json, flow_paths["markdown_path"], flow_paths["mermaid_path"])


def build_result(skill, output_path, reused, fcg_json):
    """Port of buildResult. v6 security_profile has no top-level sources/sinks,
    so source_count/sink_count fall through to 0 and flow_count = observations —
    matching the JS fallback chain against a v6 envelope."""
    security = fcg_json.get("security_profile") or {}
    source_sink = fcg_json.get("source_sink") or {}
    paths = fcg_json.get("paths") or {}
    return {
        "skill_id": skill.get("skill_id"),
        "skill_name": skill.get("skill_name"),
        "group_id": skill.get("group_id"),
        "is_ungrouped": skill.get("is_ungrouped"),
        "zip_path": skill.get("zip_path"),
        "fcg_path": output_path,
        "reused": reused,
        "source_count": len(security.get("sources") or source_sink.get("sources") or []),
        "sink_count": len(security.get("sinks") or source_sink.get("sinks") or []),
        "flow_count": len(
            security.get("observations")
            or security.get("flows")
            or paths.get("source_to_sink_paths")
            or []
        ),
    }


def build_fcg_output_path(skill, output_dir):
    """Port of buildFcgOutputPath — <output>/skills/<id>-<name>-sfg.json (≤180)."""
    skills_dir = os.path.join(output_dir, "skills")
    base = f"{safe_base_name(skill.get('skill_id'))}-{safe_base_name(skill.get('skill_name') or skill.get('zip_name') or 'skill')}"[:180]
    return os.path.join(skills_dir, f"{base}-sfg.json")


def safe_base_name(value):
    """Port of safeBaseName — strip .zip, sanitize, collapse whitespace, ≤160."""
    text = str(value if value is not None else "skill") or "skill"
    text = re.sub(r"\.zip$", "", text, flags=re.IGNORECASE)
    text = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:160] or "skill"


def run_fcg_batch(options):
    """Port of runFcgBatch — discover → worker-pool analyze → summary.

    JS spins `workerCount` async workers each draining a shared queue; here a
    ThreadPoolExecutor with the same worker count drains the skill list. The
    Python pipeline is self-contained per call (no persistent analyzer to
    create/cleanup — babel is a per-call subprocess), so submitting each skill
    as a task is the faithful equivalent. Results are gathered then sorted by
    skill_id, so completion order does not affect the summary."""
    if options.get("help"):
        print_usage()
        return None

    skills = apply_only_filter(
        discover_skills(options["root"], options["similarityRoot"], options["scope"]),
        options["only"],
    )
    skills_dir = os.path.join(options["output"], "skills")
    os.makedirs(skills_dir, exist_ok=True)

    worker_count = min(max(1, options["concurrency"]), len(skills) or 1)
    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        for outcome in executor.map(lambda s: analyze_or_reuse_skill(s, options), skills):
            if outcome.get("error"):
                errors.append(outcome["error"])
            else:
                results.append(outcome)

    summary = build_summary(options, skills, results, errors)
    _save_json(os.path.join(options["output"], "fcg-summary.json"), summary)
    with open(os.path.join(options["output"], "fcg-summary.md"), "w", encoding="utf-8") as fh:
        fh.write(render_summary_markdown(summary))
    return summary


def build_summary(options, skills, results, errors):
    """Port of buildSummary — results/errors sorted by skill_id via localeCompare."""
    sorted_results = sorted(results, key=cmp_to_key(lambda a, b: locale_compare(a["skill_id"], b["skill_id"])))
    sorted_errors = sorted(errors, key=cmp_to_key(lambda a, b: locale_compare(str(a["skill_id"]), str(b["skill_id"]))))
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "root": options["root"],
        "similarity_root": options["similarityRoot"],
        "output": options["output"],
        "scope": options["scope"],
        "mode": options["mode"],
        "total_skills": len(skills),
        "success_count": len(sorted_results),
        "reused_count": sum(1 for r in sorted_results if r["reused"]),
        "analyzed_count": sum(1 for r in sorted_results if not r["reused"]),
        "error_count": len(sorted_errors),
        "results": sorted_results,
        "errors": sorted_errors,
    }


def render_summary_markdown(summary):
    """Port of renderSummaryMarkdown — Errors table + Outputs table, slice 100."""
    lines = []
    lines.append("# FCG Batch Summary")
    lines.append("")
    lines.append(f"- Generated: {summary['generated_at']}")
    lines.append(f"- Root: {summary['root']}")
    lines.append(f"- Scope: {summary['scope']}")
    lines.append(f"- Total skills: {summary['total_skills']}")
    lines.append(f"- Success: {summary['success_count']}")
    lines.append(f"- Reused: {summary['reused_count']}")
    lines.append(f"- Analyzed: {summary['analyzed_count']}")
    lines.append(f"- Errors: {summary['error_count']}")
    lines.append("")

    if summary["errors"]:
        lines.append("## Errors")
        lines.append("")
        lines.append("| Skill | Message |")
        lines.append("| --- | --- |")
        for error in summary["errors"][:100]:
            lines.append(f"| {_escape_pipe(error.get('skill_name') or error.get('skill_id'))} | {_escape_pipe(error.get('message'))} |")
        lines.append("")

    lines.append("## Outputs")
    lines.append("")
    lines.append("| Skill | Sources | Sinks | Flows | Reused | FCG JSON |")
    lines.append("| --- | ---: | ---: | ---: | --- | --- |")
    for result in summary["results"][:100]:
        reused = "yes" if result["reused"] else "no"
        lines.append(
            f"| {_escape_pipe(result['skill_name'])} | {result['source_count']} "
            f"| {result['sink_count']} | {result['flow_count']} | {reused} "
            f"| {_escape_pipe(result['fcg_path'])} |"
        )
    return "\n".join(lines)


def print_usage():
    """Port of printUsage."""
    print("Usage:")
    print("  python -m skill_sfg.batch --root <clawhub-run-root> [options]")
    print("")
    print("Options:")
    print("  --root <dir>                 Run root containing zips/ or similarity/grouping.json")
    print("  --similarity-root <dir>      Default <root>/similarity")
    print("  --output <dir>               Default <root>/fcg")
    print("  --scope all|grouped|ungrouped  Default all")
    print("  --concurrency <n>            Default 4")
    print("  --mode quick|full|deep       Default full")
    print("  --label-llm-assist          Enable low-confidence label LLM assist")
    print("  --label-llm-concurrency <n> Default 2")
    print("  --label-llm-cache <file>    Default <root>/fcg/label-llm-cache.jsonl")
    print("  --semantic-gate-cache <file> Default <root>/fcg/semantic-gate-cache.jsonl (0/false to disable)")
    print("  --refresh                    Re-run FCG when JSON exists")


def _save_json(file_path, value):
    """Port of saveJson — mkdir -p then pretty-print JSON."""
    resolved = os.path.abspath(file_path)
    parent = os.path.dirname(resolved)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(value, ensure_ascii=False, indent=2))


def _escape_pipe(value):
    """Port of escapePipe — escape | and flatten newlines to a space."""
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\r\n", " ").replace("\n", " ")


def main(argv=None):
    import sys
    from .util.env import load_project_env

    load_project_env(entry_file=_HERE)
    if argv is None:
        argv = sys.argv[1:]
    try:
        options = resolve_options(parse_args(argv))
        summary = run_fcg_batch(options)
        if summary is None:
            return 0
        print(f"FCG batch completed: {summary['success_count']} succeeded, {summary['error_count']} failed")
        print(f"Summary: {os.path.join(options['output'], 'fcg-summary.json')}")
        return 0
    except Exception as error:  # noqa: BLE001 — mirror JS fatal handler
        sys.stderr.write(f"Fatal error: {error}\n")
        print_usage()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
