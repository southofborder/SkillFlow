"""Six durable annotation chains comparing frozen and current prompt layouts.

Synthetic Task baselines are authored fixtures, not model extractions. Reference
candidates remain in audit only. This tool reuses the production recorder,
transport, validator and unlimited mechanical correction state machine.
"""
from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.llm.config import LlmConfig
from skillflow.common.recording import (
    SavedCallFailure, ResponseIntegrityError, canonical_sha256, implementation_provenance,
    injected_factory, now, sha_file, streaming_factory, validated_trace,
)
from skillflow.common.runs import exclusive_run
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import ResponseChain, ResponseChainError, chain_counts, correction_prompt
from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.config import annotation_public_config, annotation_config, PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.material import checked_material, model_material
from tools.doe.prompt_comparison_fixtures import evaluation_fixtures
from tools.doe.summarize_pipeline_run import sum_usage

IDENTITY = "skillflow-prompt-comparison-v1"
ARMS = ("old", "new")
CLAIM = "Structural validity is not semantic proof. Synthetic references are assistant-authored, not independent expert ground truth."

# Experiment-only display projection; the historical snapshot remains unchanged.
_OLD_REASON_TRANSLATIONS = {
    "只保持原文规定的这个值、条件或动作。": "Preserve only the value, condition, or action specified by the source.",
    "该目标是原文要求保持的真实 CFG 值位置。": "This target is the actual CFG value position that the source requires preserving.",
    "此独立示例原文明示所示关系；定位有效不证明其他任务中的相同解释成立。": "The source of this independent example explicitly states the illustrated relationship; valid references do not establish that the same interpretation holds for other tasks.",
}
_OLD_LANGUAGE = "Write interpretations, evidence explanations and failure reasons in Chinese; source text stays in its original language."
_NEW_LANGUAGE = "Write interpretations, evidence explanations and failure reasons in English; source text stays in its original language."
_OLD_EXAMPLE_MARKERS = {"ENDPOINT DEMAND EXAMPLES (SYNTHETIC, NOT INPUT DATA)", "BINDING_EXAMPLES"}


def _old_prefix_projection(snapshot):
    """Project only frozen teaching reasons and output language; never input data."""
    def digest(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    normalized = snapshot.replace("\r\n", "\n")
    lines = normalized.splitlines(keepends=True)
    changes = []
    for index, line in enumerate(lines):
        if _OLD_LANGUAGE in line:
            if line.count(_OLD_LANGUAGE) != 1:
                raise ValueError("Ambiguous old output-language instruction")
            lines[index] = line.replace(_OLD_LANGUAGE, _NEW_LANGUAGE)
            changes.append({"kind": "output_language", "line": index + 1,
                            "before": _OLD_LANGUAGE, "after": _NEW_LANGUAGE})
        if not index or lines[index - 1].strip() not in _OLD_EXAMPLE_MARKERS:
            continue
        block = lines[index - 1].strip()
        before = json.loads(line)
        expected = deepcopy(before)
        block_changes = []
        def visit(value, path=()):
            if isinstance(value, list):
                for item_index, item in enumerate(value):
                    visit(item, (*path, item_index))
            elif isinstance(value, dict):
                for key, item in value.items():
                    if key == "reason" and isinstance(item, str) and re.search(r"[\u4e00-\u9fff]", item):
                        if item not in _OLD_REASON_TRANSLATIONS:
                            raise ValueError("Unknown historical teaching reason; no automatic translation")
                        translated = _OLD_REASON_TRANSLATIONS[item]
                        value[key] = translated
                        block_changes.append({"kind": "teaching_reason", "block": block,
                            "path": list((*path, key)), "before": item, "after": translated})
                    else:
                        visit(item, (*path, key))
        visit(expected)
        replacement_counts = {}
        for old, translated in _OLD_REASON_TRANSLATIONS.items():
            pattern = r'("reason"\s*:\s*)' + re.escape(_json(old))
            line, count = re.subn(pattern, lambda match: match.group(1) + _json(translated), line)
            replacement_counts[old] = count
        if json.loads(line) != expected or any(replacement_counts[text] != sum(row["before"] == text for row in block_changes)
                                              for text in _OLD_REASON_TRANSLATIONS):
            raise ValueError("Historical teaching projection changed non-reason content")
        lines[index] = line
        changes.extend(block_changes)
    projected = "".join(lines)
    if re.search(r"[\u4e00-\u9fff]", projected):
        raise ValueError("Unrecognized non-English historical prompt text")
    if "in Chinese" in projected:
        raise ValueError("Unrecognized historical output-language instruction")
    receipt = {"identity": "skillflow-comparison-english-projection-v1",
        "raw_sha256": digest(snapshot), "normalized_sha256": digest(normalized),
        "projected_sha256": digest(projected), "crlf_replacements": snapshot.count("\r\n"),
        "changes": changes, "scope": "Frozen prompt prefix only; common model input is appended unchanged."}
    return projected, receipt


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _read(path):
    return _json_object(Path(path).read_bytes().decode("utf-8"))


def _safe(path):
    path = Path(path)
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            if part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400:
                raise ValueError("Comparison paths cannot contain links or reparse points")
    return path.resolve()


def _seal(value):
    return {**value, "manifest_sha256": canonical_sha256(value)}


def _unseal(value):
    raw = deepcopy(value)
    digest = raw.pop("manifest_sha256", None)
    if canonical_sha256(raw) != digest:
        raise ValueError("Comparison manifest identity mismatch")
    return raw


def _implementation():
    tools = (Path(__file__), Path(__file__).with_name("prompt_comparison_fixtures.py"),
             Path(__file__).with_name("summarize_pipeline_run.py"))
    return {"production": implementation_provenance(), "tools": {path.name: sha_file(path) for path in tools}}


def _old_correction_snapshot(source):
    """Extract literal old instructions with AST, never execute historical code."""
    tree = ast.parse(source)
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "correction_prompt")
    returning = next(node.value for node in function.body if isinstance(node, ast.Return))
    def prefix(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return prefix(node.left) + prefix(node.right)
        if isinstance(node, ast.Name):
            return "" if node.id == "base_prompt" else constants[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "dumps":
            return ""
        raise ValueError("Unsupported frozen correction builder; do not guess historical behavior")
    return {"version": constants["VERSION"], "prefix": prefix(returning)}


def _old_builder(snapshot):
    def build(base_prompt, response, diagnostics):
        return base_prompt + snapshot["prefix"] + _json({"protocol": snapshot["version"], "candidate": response, "diagnostics": diagnostics})
    return build


def _prompt_sizes(prompt, material, arm):
    """Measured model-visible sections, never approximate tokenizer counts."""
    def size(text):
        return {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}
    actual_input = _json(model_material(material))
    if actual_input not in prompt:
        raise ValueError("Frozen prompt does not contain the exact common input")
    if arm == "old":
        instructions, rest = prompt.split("\nENDPOINT DEMAND EXAMPLES (SYNTHETIC, NOT INPUT DATA)\n", 1) if "\nENDPOINT DEMAND EXAMPLES (SYNTHETIC, NOT INPUT DATA)\n" in prompt else (prompt.split("\nINPUT_JSON\n", 1)[0], "")
        examples, format_text = (rest.split("\nRESPONSE_JSON_SCHEMA\n", 1) if "\nRESPONSE_JSON_SCHEMA\n" in rest else (rest, ""))
        format_text = format_text.split("\nINPUT_JSON\n", 1)[0]
    else:
        import re
        blocks = dict(re.findall(r"<!-- SKILLFLOW_PROMPT:([A-Z_]+):BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:\1:END -->", prompt, flags=re.S))
        # The production marker is shared with structure v4; fail rather than guess a section.
        if not blocks:
            blocks = dict(re.findall(r"<([A-Z_]+)>\n(.*?)\n</\1>", prompt, flags=re.S))
        examples = blocks.get("EXAMPLES", "")
        format_text = blocks.get("FORMAT", "")
        instructions = "\n".join(value for key, value in blocks.items() if key not in {"INPUT", "FORMAT", "EXAMPLES"})
        if not blocks:
            raise ValueError("Unknown new prompt sections")
    static = prompt.replace(actual_input, "", 1)
    return {"total": size(prompt), "input": size(actual_input), "static": size(static),
            "instructions": size(instructions), "format": size(format_text), "examples": size(examples)}


def prepare_comparison(run_dir, *, baseline_dir, config):
    """Freeze three inputs, six exact prompts and external reference fixtures."""
    directory, baseline = _safe(run_dir), _safe(baseline_dir)
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Prepare requires a new empty comparison directory")
    if set(config) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Only public request configuration can be frozen")
    config = annotation_config(config)
    receipt = _read(baseline / "baseline.json")
    old_path = baseline / "annotation-prefix.txt"
    if sha_file(old_path) != receipt["annotation_prefix_sha256"]:
        raise ValueError("Frozen baseline annotation prefix differs")
    correction_path = baseline / "src/skillflow/common/structural_correction.py"
    if sha_file(correction_path) != receipt["files"]["src/skillflow/common/structural_correction.py"]:
        raise ValueError("Frozen baseline correction source differs")
    prefix_snapshot = old_path.read_bytes().decode("utf-8")
    # The exported Windows baseline file has CRLF; the original Python builder
    # emitted LF. Preserve the exported bytes and record this display projection.
    prefix, projection = _old_prefix_projection(prefix_snapshot)
    if not prefix.endswith("\nINPUT_JSON\n"):
        raise ValueError("Old annotation prefix must end at the input marker")
    old_correction = _old_correction_snapshot(correction_path.read_bytes().decode("utf-8"))
    writer = ArtifactWriter(())
    with exclusive_run(directory):
        writer.text(directory / "audit/old-prefix.txt", prefix_snapshot)
        writer.json(directory / "audit/old-prefix-projection.json", projection)
        writer.json(directory / "audit/old-correction.json", old_correction)
        writer.json(directory / "audit/baseline-receipt.json", receipt)
        cases = []
        for fixture in evaluation_fixtures():
            case = fixture["name"]
            material = example_material(fixture)
            # These checks validate references and compilation, not the assistant's interpretation.
            compile_response(fixture["annotation"], material)
            compile_response(fixture["contrast"], material)
            writer.json(directory / f"cases/{case}/material.json", material)
            writer.json(directory / f"audit/fixtures/{case}.json", {"provenance": "assistant_authored_fixture", **fixture})
            for arm, prompt in (("old", prefix + _json(model_material(material))), ("new", build_prompt(material))):
                writer.text(directory / f"cases/{case}/{arm}/base-prompt.txt", prompt)
                writer.json(directory / f"cases/{case}/{arm}/prompt-sizes.json", _prompt_sizes(prompt, material, arm))
            cases.append(case)
        files = {path.relative_to(directory).as_posix(): sha_file(path)
                 for path in sorted(directory.rglob("*")) if path.is_file() and path.name != ".runner.lock"}
        manifest = {"identity": IDENTITY, "created_at": now(), "cases": cases, "arms": list(ARMS),
                    "config": config, "implementation": _implementation(), "files": files,
                    "task_provenance": "assistant_authored_fixture", "semantic_gold_standard": False,
                    "policy": {"structural_attempt_limit": None, "semantic_review_calls": 0, "semantic_repairs": 0,
                               "task_extraction_calls": 0, "quality_reruns": 0,
                               "old_prefix_projection": "Explicit CRLF-to-LF and English teaching/output-policy projection; original bytes retained"}, "claim": CLAIM}
        writer.json(directory / "manifest.json", _seal(manifest))
    return manifest


def load_comparison(run_dir, *, check_implementation=False):
    directory = _safe(run_dir)
    manifest = _unseal(_read(directory / "manifest.json"))
    if manifest["identity"] != IDENTITY or manifest["arms"] != list(ARMS):
        raise ValueError("Unsupported prompt comparison run")
    for relative, digest in manifest["files"].items():
        path = _safe(directory / relative)
        if not path.is_relative_to(directory) or sha_file(path) != digest:
            raise ValueError("Frozen comparison input changed: " + relative)
    if check_implementation and manifest["implementation"] != _implementation():
        raise ValueError("Comparison implementation differs; no silent replay or resume")
    return manifest


def _call_details(directory):
    rows = []
    for path in sorted(directory.glob("calls/annotation/a*/call.json")):
        call = _read(path)
        traces = validated_trace(path.parent / "transport.json")
        attempts = [attempt for trace in traces for attempt in trace.get("http_attempts", [])]
        usages = [attempt.get("usage") for attempt in attempts]
        token_usage = sum_usage([{**attempt, "usage": attempt.get("usage")} for attempt in attempts])
        def total(names, nested=None):
            values = []
            for usage in usages:
                source = usage.get(nested, {}) if isinstance(usage, dict) and nested else usage
                if isinstance(source, dict):
                    value = next((source[key] for key in names if type(source.get(key)) is int), None)
                    if value is not None:
                        values.append(value)
            return sum(values) if values else None
        elapsed = None
        if call.get("finished_at") and call.get("started_at"):
            elapsed = (datetime.fromisoformat(call["finished_at"]) - datetime.fromisoformat(call["started_at"])).total_seconds()
        prompt = call["prompt"]
        rows.append({"call": path.parent.name, "status": call["status"], "elapsed_seconds": elapsed,
            "prompt_characters": len(prompt), "prompt_bytes": len(prompt.encode("utf-8")),
            "http_attempts": len(attempts), "usage_complete": token_usage["total_tokens"]["total"] is not None,
            "token_usage": token_usage,
            "returned_models": sorted({row["returned_model"] for row in [*traces, *attempts] if row.get("returned_model")}),
            "input_tokens": total(("input_tokens", "prompt_tokens")), "output_tokens": total(("output_tokens", "completion_tokens")),
            "total_tokens": total(("total_tokens",)), "reasoning_tokens": total(("reasoning_tokens",), "completion_tokens_details")})
    return rows


def _execute(directory, manifest, case, arm, *, writer, client=None, client_factory=None,
             stop_event=None, replay=False, progress=None):
    stage = directory / "cases" / case / arm
    material = checked_material(_read(directory / "cases" / case / "material.json"))
    prompt = (stage / "base-prompt.txt").read_bytes().decode("utf-8")
    if arm == "new" and prompt != build_prompt(material):
        raise ValueError("Current prompt differs from prepared comparison")
    if arm == "old":
        prefix, projection = _old_prefix_projection((directory / "audit/old-prefix.txt").read_bytes().decode("utf-8"))
        if projection != _read(directory / "audit/old-prefix-projection.json"):
            raise ValueError("Historical prompt projection receipt differs")
        if prompt != prefix + _json(model_material(material)):
            raise ValueError("Frozen baseline prompt differs from common input")
    existing = _unseal(_read(stage / "result.json")) if (stage / "result.json").is_file() else None
    if replay and existing is None:
        raise ValueError("Comparison replay requires a saved stage result")
    chain = ResponseChain(stage, prefix="calls/annotation", base_prompt=prompt,
        request_kind="prompt_comparison_" + arm, config=manifest["config"], writer=writer,
        validate=lambda response: compile_response(response, material),
        client_factory=client_factory or (injected_factory(client) if client is not None else None),
        stop_event=stop_event, replay=replay, read_only=replay, progress=progress,
        interruption=existing.get("cursor") if replay and existing["status"] == "interrupted" else None,
        correction_builder=_old_builder(_read(directory / "audit/old-correction.json")) if arm == "old" else correction_prompt)
    result = {"case": case, "arm": arm, "status": "complete", "error": None,
              "compilation_sha256": None, "artifacts": {}, "semantic_acceptance": "not_assessed"}
    try:
        compilation = chain.run()
        result["compilation_sha256"] = canonical_sha256(compilation)
        for name, value in zip(("raw-annotation.json", "compiled-annotation.json", "mapping.json"), compilation):
            path = stage / name
            if path.exists():
                if canonical_sha256(_read(path)) != canonical_sha256(value):
                    raise ResponseIntegrityError("Saved comparison compilation changed")
            elif replay:
                raise ResponseIntegrityError("Missing saved comparison compilation")
            else:
                writer.json(path, value)
            result["artifacts"][name] = sha_file(path)
    except (ResponseIntegrityError, ResponseChainError):
        raise
    except SemanticFailure as error:
        result.update(status="semantic_failure", error=error.failure)
    except KeyboardInterrupt:
        result.update(status="interrupted", error="Execution interrupted; no later request started.")
    except Exception as error:
        kind = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
        if kind == "KeyboardInterrupt":
            result.update(status="interrupted", error="Execution interrupted; no later request started.")
        else:
            result.update(status="execution_error", error={"type": kind, "message": writer.clean(str(error))})
    result.update(accepted_call=chain.accepted_call, response_chain=chain.snapshot(),
                  counts=chain_counts(stage, "calls/annotation"), calls=_call_details(stage), cursor=chain.cursor)
    result["call_files"] = {path.relative_to(stage).as_posix(): sha_file(path)
                           for path in sorted((stage / "calls").rglob("*")) if path.is_file()}
    if existing and (replay or existing["status"] != "interrupted") and result != existing:
        raise ResponseIntegrityError("Comparison stage differs from accepted decision")
    if not replay:
        writer.json(stage / "result.json", _seal(result))
    return result


def _reports(directory, summary, writer):
    lines = ["# Prompt comparison", "", CLAIM, "", "Each case shares one frozen source, CFG, and assistant-authored Task. Both arms use identical validation and diagnostics.", "",
             "The old arm uses a language-aligned frozen old layout with an audited English projection of teaching reasons and output-language policy. Historical bytes are preserved; this is not a byte-identical rerun of the original prompt.", "",
             "| Case | Prompt | Status | Logical calls | Structural corrections | Known total tokens |", "|---|---|---|---:|---:|---:|"]
    for row in summary["results"]:
        counts = row["counts"]
        known = [call["total_tokens"] for call in row["calls"] if call["total_tokens"] is not None]
        usage = str(sum(known)) if known else "Unknown"
        if known and not all(call["usage_complete"] for call in row["calls"]):
            usage += " (incomplete)"
        lines.append(f"| {row['case']} | {row['arm']} | {row['status']} | {counts['logical_calls']} | {counts['structural_corrections']} | {usage} |")
    lines += ["", "Structural validity, cost, and semantic assessment are reported separately. No Task extraction or semantic review model calls were made.", "",
              "## Static prompt sizes", "", "Characters / UTF-8 bytes. These are not estimated tokens; section sizes and wrapper markers are not double-counted.", "",
              "| Case / arm | Full prompt | Input | Static content | Instructions | Format | Examples |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for case in summary["cases"]:
        for arm in ARMS:
            sizes = _read(directory / "cases" / case / arm / "prompt-sizes.json")
            values = [str(sizes[key]["characters"]) + " / " + str(sizes[key]["utf8_bytes"]) for key in ("total", "input", "static", "instructions", "format", "examples")]
            lines.append(f"| {case} / {arm} | " + " | ".join(values) + " |")
    lines += ["", "## Actual request usage", "", "Reasoning tokens are an output breakdown, not an additional total. Missing usage from any HTTP attempt leaves only a known subtotal.", "",
              "| Case / arm / call | Input | Output | Reasoning breakdown | Total | Call seconds |",
              "|---|---:|---:|---:|---:|---:|"]
    for row in summary["results"]:
        for call in row["calls"]:
            usage = call["token_usage"]
            def display(name):
                item = usage[name]
                return str(item["total"]) if item["total"] is not None else "Unknown" if item["reported_subtotal"] is None else str(item["reported_subtotal"]) + " (known subtotal)"
            reason = usage["api_reported_fields"].get("completion_tokens_details.reasoning_tokens")
            reason = "Unknown" if reason is None else str(reason["reported_subtotal"]) + (" (incomplete)" if reason["attempts_missing_value"] else "")
            lines.append(f"| {row['case']} / {row['arm']} / {call['call']} | {display('input_tokens')} | {display('output_tokens')} | {reason} | {display('total_tokens')} | {call['elapsed_seconds']} |")
    lines += ["", "## Saved materials", "", "[Historical English projection audit](audit/old-prefix-projection.json)", ""]
    for case in summary["cases"]:
        lines.append(f"- [{case} frozen material](cases/{case}/material.json) · [Assistant reference and contrast](audit/fixtures/{case}.json)")
        for arm in ARMS:
            record = f"[{arm} record](cases/{case}/{arm}/result.json)" if (directory / "cases" / case / arm / "result.json").exists() else "Not executed"
            lines.append(f"  - [{arm} prompt](cases/{case}/{arm}/base-prompt.txt) · {record}")
    writer.text(directory / "report.md", "\n".join(lines) + "\n")
    # Use the same content model; no semantic observations are inferred from validation.
    import markdown_it
    html = markdown_it.MarkdownIt("commonmark").enable("table").render("\n".join(lines))
    document = "<!doctype html><html lang='en'><meta charset='utf-8'><title>Prompt comparison</title><style>body{max-width:1100px;margin:2rem auto;font:16px/1.6 system-ui}td,th{padding:.4rem;border:1px solid #ccc}table{border-collapse:collapse}</style>" + html + "</html>"
    writer.text(directory / "index.html", document)
    writer.text(directory / "report.html", document)


def run_comparison(run_dir, *, env_file=None, clients=None, client_factory=None, stop_event=None,
                   replay=False, progress=None):
    directory = _safe(run_dir)
    stopping = stop_event or Event()
    if replay and (clients is not None or client_factory is not None):
        raise ValueError("Replay cannot receive a live client")
    if clients is not None and client_factory is not None:
        raise ValueError("Choose injected clients or one factory")
    manifest = load_comparison(directory, check_implementation=True)
    writer = ArtifactWriter(())
    if not replay and clients is None and client_factory is None:
        client_factory, secrets = streaming_factory(manifest["config"], env_file=env_file)
        writer = ArtifactWriter(secrets)
    if writer.clean(manifest) != manifest:
        raise ValueError("Credential overlaps frozen comparison material")
    summary = {"identity": IDENTITY, "cases": manifest["cases"], "results": [], "claim": CLAIM}
    with exclusive_run(directory):
        for case in manifest["cases"]:
            for arm in ARMS:
                if stopping.is_set():
                    break
                stage_result = directory / "cases" / case / arm / "result.json"
                if replay and not stage_result.exists():
                    continue
                client = None if clients is None else clients[(case, arm)]
                row = _execute(directory, manifest, case, arm, writer=writer, client=client,
                    client_factory=client_factory, stop_event=stopping, replay=replay, progress=progress)
                summary["results"].append(row)
                if row["status"] == "interrupted" and not replay:
                    stopping.set()
            if stopping.is_set():
                break
        summary["status"] = "interrupted" if stopping.is_set() else "complete" if len(summary["results"]) == len(manifest["cases"]) * 2 else "partial"
        if replay:
            prior = _read(directory / "summary.json")
            # Replayed interrupted request chains retain their original aggregate state.
            if any(row["status"] == "interrupted" for row in summary["results"]) or (prior["status"] == "interrupted" and not summary["results"]):
                summary["status"] = "interrupted"
            if summary != prior:
                raise ResponseIntegrityError("Comparison summary differs on zero-API replay")
            receipt = {"status": "matched", "summary_sha256": canonical_sha256(summary), "api_calls": 0}
            writer.json(directory / "replay.json", receipt)
            return receipt
        writer.json(directory / "summary.json", summary)
        _reports(directory, summary, writer)
    return summary


def replay_comparison(run_dir):
    return run_comparison(run_dir, replay=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--run-dir", required=True)
    prep.add_argument("--baseline-dir", required=True)
    prep.add_argument("--env-file")
    run = commands.add_parser("run")
    run.add_argument("--run-dir", required=True)
    run.add_argument("--env-file")
    replay = commands.add_parser("replay")
    replay.add_argument("--run-dir", required=True)
    screen_prep = commands.add_parser("screen-prepare", help="Freeze eight one-shot annotation/review requests; no correction chains")
    screen_prep.add_argument("--run-dir", required=True)
    screen_prep.add_argument("--baseline-dir", required=True)
    screen_prep.add_argument("--env-file")
    screen_run = commands.add_parser("screen-run")
    screen_run.add_argument("--run-dir", required=True)
    screen_run.add_argument("--env-file")
    screen_replay = commands.add_parser("screen-replay")
    screen_replay.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    if args.command.startswith("screen-"):
        from tools.doe.prompt_screen import prepare_screen, run_screen, replay_screen
        if args.command == "screen-prepare":
            result = prepare_screen(args.run_dir, baseline_dir=args.baseline_dir,
                config=annotation_public_config(LlmConfig.from_env(env_file=args.env_file)))
            print(_json({"identity": result["identity"], "cases": result["cases"]}))
        else:
            result = replay_screen(args.run_dir) if args.command == "screen-replay" else run_screen(args.run_dir, env_file=args.env_file, progress=print)
            print(_json({"status": result["status"]}))
    elif args.command == "prepare":
        result = prepare_comparison(args.run_dir, baseline_dir=args.baseline_dir,
            config=annotation_public_config(LlmConfig.from_env(env_file=args.env_file)))
        print(_json({"identity": result["identity"], "cases": result["cases"]}))
    else:
        result = run_comparison(args.run_dir, env_file=getattr(args, "env_file", None), replay=args.command == "replay", progress=print)
        print(_json({"status": result["status"]}))


if __name__ == "__main__":
    main()
