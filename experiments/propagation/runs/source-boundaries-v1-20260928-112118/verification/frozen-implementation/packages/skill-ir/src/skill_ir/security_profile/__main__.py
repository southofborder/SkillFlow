"""Prepare, annotate once, or replay an independent security-profile run."""
from __future__ import annotations

import argparse
from pathlib import Path

PUBLIC_CONFIG_FIELDS = ("endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
                        "retry_base_ms", "retry_max_backoff_ms")


def main(argv=None):
    parser = argparse.ArgumentParser(description="完整 Skill 与原始 CFG 的独立安全语义标注；不执行传播或风险判断")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="离线冻结输入、校验图并准备一次标注")
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--analysis", type=Path, required=True)
    prepare.add_argument("--run-dir", type=Path, required=True)
    prepare.add_argument("--env-file", type=Path, help="只读取公开配置用于绑定；不发起 API")
    run = sub.add_parser("run", help="执行或恢复唯一的模型标注调用")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--env-file", type=Path)
    replay = sub.add_parser("replay", help="仅重放已保存响应，零 API")
    replay.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    from .runner import prepare_run, run_annotation, replay_run
    if args.command == "replay":
        result = replay_run(args.run_dir)
    else:
        from skill_ir.llm.config import LlmConfig
        config = LlmConfig.from_env(env_file=args.env_file)
        public = {key: getattr(config, key) for key in PUBLIC_CONFIG_FIELDS}
        secrets = (config.api_key,) if config.api_key else ()
        if args.command == "prepare":
            manifest = prepare_run(args.input, args.analysis, run_dir=args.run_dir, config=public, secrets=secrets)
            print(f"{manifest['preparation_status']}；{args.run_dir.resolve()}")
            return 0 if manifest["preparation_status"] == "ready" else 1
        from skill_ir.recording import streaming_factory
        # Binding is checked before an online client is instantiated by its factory.
        factory, secrets = streaming_factory(public, env_file=args.env_file)
        result = run_annotation(args.run_dir, client_factory=factory, config=public, secrets=secrets,
                                progress=lambda text: print(text, flush=True))
    print(f"{result['status']}；{result['reason']}；{args.run_dir.resolve()}", flush=True)
    return 0 if result["status"] in {"complete", "incomplete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
