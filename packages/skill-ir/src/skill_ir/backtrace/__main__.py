"""CLI kept separate from all production Skill-IR entry points."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from skill_ir.recording import streaming_factory
from .runner import EXPERIMENT_ROOT, SUITES, execute_run, prepare_run, public_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="受控语义回述与完整源文核对 v5：语义比较与事实校验，每案例一次逻辑调用")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "run", "replay"):
        command = commands.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=name == "replay")
        command.add_argument("--renderer", type=Path, help="已证明的 Lean 受控打印器可执行文件")
        if name != "replay":
            command.add_argument("--suite", choices=tuple(SUITES), default=None,
                                 help="默认 f01-five；semantics-v5-seven 加入暂停批次 001、010 第0轮原图")
            command.add_argument("--max-audit-execution-retries", type=int, default=None)
        if name == "run":
            command.add_argument("--env-file", type=Path)
            command.add_argument("--workers", type=int, default=2)
    args = parser.parse_args(argv)
    directory = args.run_dir or EXPERIMENT_ROOT / "runs" / ("controlled-v5-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if args.command == "prepare":
        manifest = prepare_run(directory, executable=args.renderer, suite=args.suite or "f01-five",
                               max_audit_execution_retries=2 if args.max_audit_execution_retries is None else args.max_audit_execution_retries)
        print(f"离线准备完成：{directory.resolve()}", flush=True)
        from .runner import read_json
        review = read_json(directory / "verification/review30.json")
        return 0 if all(c["fidelity_status"] == "passed" for c in manifest["cases"]) and all(s["status"] == "passed" for s in review["samples"]) else 1
    if args.command == "replay":
        result = execute_run(directory, replay=True, executable=args.renderer, progress=lambda value: print(value, flush=True))
    else:
        if not (directory / "manifest.json").exists():
            prepare_run(directory, executable=args.renderer, suite=args.suite or "f01-five",
                        max_audit_execution_retries=2 if args.max_audit_execution_retries is None else args.max_audit_execution_retries)
        from .runner import verify_run
        manifest = verify_run(directory, live=True)
        if args.suite is not None and manifest["suite"] != args.suite:
            parser.error("--suite differs from the prepared run")
        if args.max_audit_execution_retries is not None and manifest["policy"]["max_audit_execution_retries"] != args.max_audit_execution_retries:
            parser.error("--max-audit-execution-retries differs from the prepared run")
        factory, secrets = streaming_factory(public_config(), env_file=args.env_file)
        result = execute_run(directory, client_factory=factory, secrets=secrets, workers=args.workers, executable=args.renderer,
                             progress=lambda value: print(value, flush=True))
    print(f"{result['execution_status']}；已记录 {result['recorded_logical_calls']}/{result['planned_logical_calls']} 次逻辑调用；"
          f"{result['recorded_execution_calls']} 次执行，{result['http_attempts']} 次 HTTP 尝试；{directory.resolve()}", flush=True)
    return 0 if result["execution_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
