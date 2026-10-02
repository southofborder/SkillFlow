"""Explicit bounded semantic feedback CLI; the single-analysis CLI is unchanged."""

from __future__ import annotations

import argparse
from pathlib import Path


PUBLIC_CONFIG_FIELDS = (
    "endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
    "retry_base_ms", "retry_max_backoff_ms",
)


def _nonnegative(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("修复次数必须为非负整数")
    return parsed


def main(argv=None):
    parser = argparse.ArgumentParser(description="CFG 语义反馈闭环 v4：统一解释契约、语义覆盖核对、证据校验及有界修复")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="开始或恢复同一身份的运行；不自动重发不确定请求")
    run.add_argument("--input", type=Path, required=True, help="Skill 目录或 ZIP")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--initial-analysis", type=Path, help="包含有效 cfg 的已有 analysis.json")
    run.add_argument("--max-semantic-revisions", type=_nonnegative, default=3)
    run.add_argument("--max-structural-repairs", type=_nonnegative, default=3)
    run.add_argument("--max-audit-execution-retries", type=int, choices=range(6), default=2,
                     help="每轮核对暂态通信失败的额外执行重试次数（0–5；默认 2），不重试完整响应")
    run.add_argument("--env-file", type=Path)
    run.add_argument("--renderer", type=Path, help="Lean 受控打印器可执行文件")
    replay = commands.add_parser("replay", help="离线重走保存响应的解析、编译、保真及核对，零 API")
    replay.add_argument("--run-dir", type=Path, required=True)
    replay.add_argument("--renderer", type=Path)
    args = parser.parse_args(argv)

    # In particular, replay neither loads credentials nor constructs a client.
    from .runner import refine_skill, replay_run
    if args.command == "replay":
        result = replay_run(args.run_dir, renderer=args.renderer)
    else:
        from skill_ir.llm.config import LlmConfig
        from skill_ir.recording import streaming_factory
        llm_config = LlmConfig.from_env(env_file=args.env_file)
        config = {field: getattr(llm_config, field) for field in PUBLIC_CONFIG_FIELDS}
        factory, secrets = streaming_factory(config, env_file=args.env_file)
        result = refine_skill(
            args.input, run_dir=args.run_dir, initial_analysis=args.initial_analysis,
            max_semantic_revisions=args.max_semantic_revisions,
            max_structural_repairs=args.max_structural_repairs,
            max_audit_execution_retries=args.max_audit_execution_retries,
            extraction_factory=factory, audit_factory=factory,
            config=config, secrets=secrets, renderer=args.renderer,
            progress=lambda message: print(message, flush=True),
        )
    print(f"{result['status']}；{result.get('reason', '')}；{args.run_dir.resolve()}", flush=True)
    return 0 if result["status"] == "audit_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
