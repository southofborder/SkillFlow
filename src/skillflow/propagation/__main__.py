"""Offline propagation command; it never creates a model client."""
from __future__ import annotations

import argparse
from pathlib import Path

from skillflow.propagation.runner import replay_propagation
from skillflow.propagation.runner import run_propagation


def main(argv=None):
    parser = argparse.ArgumentParser(description="离线执行基础数据传播或重放已保存记录")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="读取新版标注并执行离线传播")
    run.add_argument("--annotation-run", type=Path, required=True)
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--seed-data", type=Path)
    run.add_argument("--seed-state", type=Path, help="可选 FlowState JSON；显式空状态不会替换为自动来源")
    replay = commands.add_parser("replay", help="校验保存输入并零 API 重新求解")
    replay.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (run_propagation(args.annotation_run, run_dir=args.run_dir, seed_data=args.seed_data,
                                  initial_state=args.seed_state)
                  if args.command == "run" else replay_propagation(args.run_dir))
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + "\n")
    print(result["status"])
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
