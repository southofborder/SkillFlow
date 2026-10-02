"""One-off, offline acceptance of the completed thirty-case rerun.

This file lives outside the sealed implementation.  Merely importing it does not
inspect a run.  The terminal gate always precedes reading any call artifacts.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TOOLS = ROOT / "packages/skill-ir/experiments/security_profile/tools"
RUN = ROOT / "packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed"
PROTECTION = ROOT / "tmp/full-pipeline-v4-20260918/delivery-before.json"
DEFAULT_OUTPUT = HERE.parent / "replay-acceptance"
IDENTITY = "skill-ir-thirty-case-final-replay-acceptance-v1"
PROTECTED_ROOTS = ("dataset/skills", "dataset/unzipped", "result/ir-IPP", "result/suggestions", "result/advice_for_doe")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


costs = load_module("_final_replay_costs", TOOLS / "summarize_rerun_costs.py")
prep = costs._prepare
read_json, write_json = prep.read_json, prep.write_json
sha_file, digest = prep.sha_file, prep.canonical_sha256


def checked_inventory(directory):
    """No links and no exclusions: used for protected and replay-derived files."""
    directory = Path(directory)
    prep.no_link(directory)
    result = {}
    for current, directories, files in os.walk(directory, followlinks=False):
        directories.sort()
        for name in directories:
            prep.no_link(Path(current) / name)
        for name in sorted(files):
            path = Path(current) / name
            prep.no_link(path)
            if not path.is_file():
                raise ValueError("Unsupported non-regular artifact")
            result[path.relative_to(directory).as_posix()] = sha_file(path)
    return dict(sorted(result.items()))


def protected_inventory():
    expected = read_json(PROTECTION)
    if not isinstance(expected, dict) or len(expected) != 203:
        raise ValueError("Expected the sealed 203-file delivery inventory")
    actual = {}
    for relative in PROTECTED_ROOTS:
        directory = prep.safe_child(ROOT, relative)
        actual.update({relative + "/" + path: value for path, value in checked_inventory(directory).items()})
    if actual != expected:
        raise ValueError("Protected delivery set or file bytes changed before publication")
    return actual


def summaries(outcome):
    result = {}
    for identifier, row in sorted(outcome["cases"].items()):
        result[identifier] = {
            "feedback_status": row["feedback"]["status"],
            "feedback_reason": row["feedback"].get("reason"),
            "annotation_status": row["annotation"]["status"],
            "annotation_reason": row["annotation"].get("reason"),
            "selection": row["selection"], "counts": row["counts"],
            "rounds": [{"revision": item["revision"], "status": item["status"],
                        "graph_sha256": item["graph_sha256"], "decision": item["decision"],
                        "audit_sha256": digest(item["audit"]),
                        "audit_execution_sha256": digest(item["audit_execution"])}
                       for item in row["feedback"].get("rounds", [])],
            "profiles_sha256": digest(row["annotation"].get("profiles", {})),
            "unresolved_sha256": digest(row["annotation"].get("unresolved", [])),
            "scheduler_error": row["scheduler_error"],
        }
    return result


def source_identity():
    return {path.relative_to(ROOT).as_posix(): sha_file(path) for path in (
        HERE, TOOLS / "summarize_rerun_costs.py", TOOLS / "prepare_failed_case_rerun.py",
        TOOLS / "run_full_pipeline.py")}


def seal(value, field="snapshot_sha256"):
    return {**value, field: digest(value)}


def assert_seal(value, field="snapshot_sha256"):
    if value.get(field) != digest({key: item for key, item in value.items() if key != field}):
        raise ValueError("Acceptance evidence seal mismatch")


def snapshot(directory):
    directory = Path(directory).resolve()
    if directory != RUN.resolve():
        raise ValueError("This one-off acceptance only targets the explicitly named child run")
    # Deliberately first: no calls, transport, progress, or directory-wide scan
    # occurs until all thirty saved results agree with the final aggregate.
    manifest, outcome = costs.terminal_material(directory)
    if outcome.get("mode") != "run":
        raise ValueError("The original aggregate must be an online-run terminal record")
    provenance, parent, _, _ = costs.verify_lineage(directory, manifest)
    if len(provenance["parent_run"]["files"]) != 1398:
        raise ValueError("Unexpected sealed parent inventory size")
    original_files = prep.inventory(directory)
    call_files = costs.call_files(directory, costs.CASES)
    if not call_files:
        raise ValueError("A completed real batch cannot have an empty call inventory")
    terminal_files = {f"cases/{identifier}/result.json": original_files[f"cases/{identifier}/result.json"]
                      for identifier in sorted(costs.CASES)}
    protected = protected_inventory()
    value = {"schema_version": 1, "identity": IDENTITY, "phase": "before_replay",
        "run_path": str(directory), "run_id": directory.name,
        "parent_path": str(parent), "parent_run_id": parent.name,
        "provenance_sha256": provenance["provenance_sha256"],
        "parent_files": provenance["parent_run"]["files"],
        "parent_files_sha256": provenance["parent_run"]["files_sha256"],
        "protected_files": protected, "protected_files_sha256": digest(protected),
        "protection_manifest_sha256": sha_file(PROTECTION),
        "child_files": original_files, "child_files_sha256": digest(original_files),
        "call_files": call_files, "call_files_sha256": digest(call_files),
        "terminal_result_files": terminal_files,
        "root_result_sha256": sha_file(directory / "experiment-result.json"),
        "case_summaries": summaries(outcome), "summary": outcome["summary"],
        "implementation_files": source_identity(),
        "excluded_from_run_inventories": ["**/replay/**", "**/.runner.lock"],
        "scope": "三十例终态和全部调用记录；不判定源文与图语义等价或标注正确。"}
    return seal(value)


def assert_snapshot_current(value):
    assert_seal(value)
    if (value.get("schema_version") != 1 or value.get("identity") != IDENTITY
            or value.get("phase") != "before_replay" or Path(value["run_path"]).resolve() != RUN.resolve()):
        raise ValueError("Acceptance snapshot identity mismatch")
    if source_identity() != value["implementation_files"]:
        raise ValueError("Acceptance script or offline helper identity changed after snapshot")
    # Re-run the terminal gate before the post-run call inventory too.
    _, outcome = costs.terminal_material(RUN)
    if summaries(outcome) != value["case_summaries"] or outcome["summary"] != value["summary"]:
        raise ValueError("Original terminal decisions/rounds/counts changed")
    if sha_file(RUN / "experiment-result.json") != value["root_result_sha256"]:
        raise ValueError("Original root result bytes changed")
    if prep.inventory(RUN) != value["child_files"]:
        raise ValueError("Original child run gained/lost files or changed bytes outside replay/locks")
    if costs.call_files(RUN, costs.CASES) != value["call_files"]:
        raise ValueError("Original model request/response/call/transport bytes changed")
    if prep.inventory(Path(value["parent_path"])) != value["parent_files"]:
        raise ValueError("Sealed parent 1398-file inventory changed")
    if sha_file(PROTECTION) != value["protection_manifest_sha256"] or protected_inventory() != value["protected_files"]:
        raise ValueError("Protected 203-file inventory changed")
    return outcome


def compare_json(original, replayed, label):
    if original != replayed:
        raise ValueError("Offline replay JSON differs: " + label)


def check_derived_file(original, replayed):
    if not replayed.is_file():
        raise ValueError("Missing replay-derived artifact: " + str(replayed))
    prep.no_link(replayed)
    if original.suffix == ".json":
        compare_json(read_json(original), read_json(replayed), str(original))
    elif original.read_bytes() != replayed.read_bytes():
        raise ValueError("Replay-derived text bytes differ: " + str(original))


def stage_derived_files(stage, role):
    files = prep.inventory(stage)
    if role == "feedback":
        allowed = {"result.json", "report.md", "last-valid-cfg.json", "passed-cfg.json"}
        return {path: value for path, value in files.items() if path in allowed or path.startswith("rounds/")}
    allowed = {"result.json", "profiles.json", "unresolved.json", "validation.json", "report.md"}
    return {path: value for path, value in files.items() if path in allowed}


def verify_replay(value):
    outcome = assert_snapshot_current(value)
    actual = read_json(RUN / "replay/experiment-result.json")
    expected = {**outcome, "mode": "replay"}
    compare_json(expected, actual, "root experiment-result: only mode may differ")
    compare_json(outcome["cases"], read_json(RUN / "replay/progress.json"), "root final replay progress")
    root_files = checked_inventory(RUN / "replay")
    if set(root_files) != {"experiment-result.json", "progress.json", "report.md"}:
        raise ValueError("Unexpected root replay artifact set")
    verified = {}
    derived = {"replay/" + path: value for path, value in root_files.items()}
    for identifier in sorted(costs.CASES):
        root = RUN / "cases" / identifier
        saved = read_json(root / "result.json")
        compare_json(saved, read_json(root / "replay/result.json"), identifier + " full terminal result")
        case_files = checked_inventory(root / "replay")
        if set(case_files) != {"result.json"}:
            raise ValueError("Unexpected case replay artifact set: " + identifier)
        derived.update({f"cases/{identifier}/replay/{path}": item for path, item in case_files.items()})
        stages = {}
        for role in ("feedback", "annotation"):
            stage = root / role
            if not (stage / "manifest.json").is_file():
                if saved[role]["status"] != "not_run" or (stage / "replay").exists():
                    raise ValueError("Missing stage provenance or unexpected replay stage")
                stages[role] = {"status": "not_run", "artifacts": 0}
                continue
            source_files = stage_derived_files(stage, role)
            replay_files = checked_inventory(stage / "replay")
            if set(source_files) != set(replay_files):
                raise ValueError("Derived stage artifact set differs: " + identifier + "/" + role)
            for path in source_files:
                check_derived_file(stage / path, stage / "replay" / path)
            compare_json(saved[role], read_json(stage / "replay/result.json"), identifier + " " + role)
            derived.update({f"cases/{identifier}/{role}/replay/{path}": item for path, item in replay_files.items()})
            stages[role] = {"status": saved[role]["status"], "artifacts": len(replay_files),
                            "counts": saved[role].get("counts", {})}
        verified[identifier] = {"status": "passed", "selection": saved["selection"],
                                "counts": saved["counts"], "stages": stages}
    return {"cases": verified, "derived_files": dict(sorted(derived.items())),
            "derived_files_sha256": digest(derived), "summary": outcome["summary"]}


@contextmanager
def offline_guard():
    """Any DNS/socket/online-client attempt fails and is counted, even if caught."""
    import skill_ir.recording as recording
    import skill_ir.llm.client as llm
    attempts = []
    def forbidden(*args, **kwargs):
        attempts.append("forbidden_online_entry")
        raise RuntimeError("Offline acceptance forbids network and online model clients")
    with patch.object(socket, "getaddrinfo", forbidden), patch.object(socket, "create_connection", forbidden), \
         patch.object(socket.socket, "connect", forbidden), patch.object(socket.socket, "connect_ex", forbidden), \
         patch.object(recording, "streaming_factory", forbidden), patch.object(llm.LlmClient, "complete", forbidden):
        yield attempts


def fresh_output(output):
    output = Path(output).resolve()
    if not output.is_relative_to(HERE.parent) or output == HERE.parent:
        raise ValueError("Acceptance output must be a new child of this tmp task directory")
    if output.exists():
        raise ValueError("Acceptance output already exists; do not overwrite evidence")
    output.mkdir(parents=True)
    return output


def create_snapshot(output):
    value = snapshot(RUN)  # Do not even create output if the batch is pending.
    output = fresh_output(output)
    write_json(output / "before.json", value)
    return value, output


def report(result):
    lines = ["# 三十例离线重放验收", "", f"状态：`{result['status']}`。", "",
             "仅核验工程重放、记录不变性与判定再现，不把重放通过解释为语义正确。", ""]
    for name, check in result.get("checks", {}).items():
        lines.append(f"- {name}：{check}")
    for error in result.get("errors", []):
        lines.append(f"- 失败：{error}")
    lines += ["", "原始提示词、响应、调用和 transport 记录逐文件 SHA-256 对照；JSON 判定、轮次、计数及图/证据逐字段对照，不使用时间戳推断。", ""]
    return "\n".join(lines)


def execute_acceptance(output, *, prepared=False):
    output = Path(output).resolve()
    if prepared:
        value = read_json(output / "before.json")
        if (output / "validation.json").exists() or (output / "replay.log").exists():
            raise ValueError("This acceptance already started; use verify instead of rerunning")
        assert_snapshot_current(value)
    else:
        value, output = create_snapshot(output)
    if any("replay" in path.parts for path in RUN.rglob("replay")):
        raise ValueError("Child already contains replay outputs; inspect them instead of overwriting")
    result = {"schema_version": 1, "identity": IDENTITY, "run_id": RUN.name,
              "snapshot_sha256": value["snapshot_sha256"], "status": "failed", "checks": {}, "errors": []}
    from contextlib import redirect_stdout, redirect_stderr
    attempts = []
    try:
        driver = load_module("_final_existing_replay_driver", TOOLS / "run_full_pipeline.py")
        with (output / "replay.log").open("x", encoding="utf-8") as log:
            with redirect_stdout(log), redirect_stderr(log), offline_guard() as attempts:
                driver.execute(RUN, mode="replay")
        result["checks"]["online_entries"] = len(attempts)
        if attempts:
            raise ValueError("An online entry was attempted during replay")
        verified = verify_replay(value)
        result.update(status="passed", **verified)
        result["checks"].update({"terminal_cases": 30, "full_case_json_equal": True,
            "rounds_and_decisions_equal": True, "counts_equal": True, "call_files_unchanged": len(value["call_files"]),
            "all_original_child_files_unchanged": len(value["child_files"]),
            "parent_files_unchanged": 1398, "protected_files_unchanged": 203})
    except BaseException as error:
        result["errors"].append(type(error).__name__ + ": " + str(error))
        result["checks"]["online_entries"] = len(attempts)
        # Even a failed/interrupted replay must report any original-file damage.
        try:
            assert_snapshot_current(value)
            result["checks"]["original_records_unchanged_despite_failure"] = True
        except Exception as integrity_error:
            result["errors"].append(type(integrity_error).__name__ + ": " + str(integrity_error))
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            result["status"] = "interrupted"
            write_json(output / "validation.json", seal(result, "validation_sha256"))
            (output / "report.md").write_text(report(result), encoding="utf-8")
            raise
    write_json(output / "validation.json", seal(result, "validation_sha256"))
    (output / "report.md").write_text(report(result), encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "run", "run-prepared", "verify"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        value, output = create_snapshot(args.output_dir)
        print(json.dumps({"status": "snapshot_saved", "path": str(output), "sha256": value["snapshot_sha256"]}))
        return 0
    if args.command == "verify":
        value = read_json(args.output_dir / "before.json")
        result = verify_replay(value)
        print(json.dumps({"status": "passed", "cases": len(result["cases"]), "derived_sha256": result["derived_files_sha256"]}))
        return 0
    result = execute_acceptance(args.output_dir, prepared=args.command == "run-prepared")
    print(json.dumps({"status": result["status"], "checks": result["checks"], "errors": result["errors"]}, ensure_ascii=False))
    return int(result["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
