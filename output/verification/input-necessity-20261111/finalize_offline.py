"""Publish the completed offline receipt and current-workflow navigation."""
import json
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]


def main():
    accepted = json.loads((DIRECTORY / "offline-acceptance.json").read_text(encoding="utf-8"))
    if accepted["status"] != "passed":
        raise ValueError("Unresolved offline failures cannot be published as acceptance")
    totals = accepted["distinct_latest_test_outcomes"]
    passed, skipped = totals.get("passed", 0), totals.get("skipped", 0)
    digest = accepted["implementation_sha256"]
    initial = [(r["path"], r["outcomes"]) for r in accepted["receipts"] if r["outcomes"].get("failed")]
    lines = ["# 字段级输入必要性：离线验收", "", "状态：**通过**。", "",
        f"当前保存收据按测试标识去重、按测试进程启动时间选择最新结果：**{passed} 项通过，{skipped} 项跳过，0 项未解决失败**。这不是一次全仓全绿执行。",
        "较早启动的长测试在修正复验之后才结束，不会覆盖较晚启动的新进程复验结果。所有初次失败收据仍然保留。", "",
        "## 交付行为", "",
        "- processing 生成 Task 隔离的字段级输出—输入契约，末尾源文审查逐契约确认，程序据所需输出确定性回传需求。",
        "- 无需求范围在完成语义核验及适用限制保持检查后判为可删除；覆盖非敏感输入，保留实际前向读取、来源和观察。",
        "- 工具接口必需范围与额外实参分开；整值要求保持整值，可选字段保留存在性及存在时的值。",
        "- 删除影响与反向需求使用同一契约；同一字段的其他输出、控制及消费者需求会汇总保留。",
        "- 所选 source、CFG、annotation、review 与审查回执绑定；旧回执不可用于修复后的契约。",
        "- 多余、错误、缺失输入独立列示；未决保留具体受影响范围、缺失关系及证据。", "",
        "## 验收证据", "",
        "逐项对应见 [coverage matrix](input-necessity-coverage.md) 和 [machine-readable receipt](offline-acceptance.json)。", "",
        "主要覆盖三输入主例、部分字段及整槽删除、不同输出的需求组合、条件及成员关系、工具整值/可选/额外字段、错误和缺失字段、限制保持、局部缺口、旧审查身份拒绝、FIFO/LIFO 一致性，以及注入七答复的保存/修复/重放流程。", "",
        "## 保留的失败与修正", "",
        "初始集成检查包含环境依赖缺失、旧协议断言和在并行修改期间触发的实现身份差异。真实实现问题包括跨循环推导的缺口传播、局部契约诊断影响范围，以及新版 JSON schema 的 propertyNames 渲染；均有专项修正与复验。",
        "冻结后的集成检查为 1,777 通过、16 失败、1 跳过；16 项分别是 12 项 tokenizer 版本不符及 4 项旧无契约用例仍期待完整结果，已在相应范围复验通过。生产代码没有为消除这些预期差异而放宽契约检查。", "",
        "| 保留收据 | 通过 | 失败 | 跳过 |", "| --- | ---: | ---: | ---: |"]
    lines += [f"| `{name}` | {counts.get('passed', 0)} | {counts.get('failed', 0)} | {counts.get('skipped', 0)} |" for name, counts in initial]
    lines += ["", "## 实现与边界", "", f"实现 SHA-256：`{digest}`。",
        f"Python 源文件集合 SHA-256：`{accepted['python_source_sha256']}`。", "",
        "正常七次语义请求、两个 worker、现有结构修正和共享修复预算保持；Task 职责不变。身份升级覆盖 annotation、编译映射、source review、guided run、demand 和 DOE。历史产物未迁移或重写。", "",
        "语义正确性仍依赖源文及独立审查，不是自然语言等价或全局最小性的形式化证明。错误字段的意图不能凭变量名猜测；没有表达的接口裁剪能力不能被推定。数组重索引、未支持限制及真实源文缺口保留边界。系统不自动改写或执行 Skill。", "",
        "离线验收期间没有真实模型请求、Skill 执行或历史运行重放。用户已另行授权在此后启动唯一的新 GA4 → 001 → 010 → 013 批次；新目录及实际结果记录在相邻的 online-input-necessity-20261111 目录。", ""]
    (DIRECTORY / "assessment.zh.md").write_text("\n".join(lines), encoding="utf-8")
    (DIRECTORY / "assessment.en.md").write_text(
        "# Field-level input necessity: offline acceptance\n\n"
        f"Passed: {passed} distinct latest scoped test identities; {skipped} skips; zero unresolved failures. "
        "This is not one all-green whole-repository run. Earlier failures and exact corrective receipts remain archived. "
        "Later-started fresh-process retests supersede earlier-started overlapping runs.\n\n"
        "Processing authors Task-independent output/input contracts, the existing source review checks every contract, "
        "and deterministic demand plus influence analysis consume the bound accepted table. Actual forward inputs and observations remain unchanged. "
        "Completed no-demand ranges are deletable, including nonsensitive inputs; required tool whole values and optional presence remain retained. "
        "Reports distinguish excessive, wrong and missing inputs from specifically evidenced local uncertainty.\n\n"
        "The frozen integrated run had 1,777 passes, 16 failures and one skip. Twelve failures were the temporary environment's tokenizer version "
        "rather than the reference protocol's pinned version; four were obsolete no-contract fixture expectations. Corrective scoped runs passed. "
        "See offline-acceptance.json for every preserved receipt and input-necessity-coverage.md for acceptance mapping.\n\n"
        f"Implementation SHA-256: `{digest}`.\n\n"
        "Seven normal semantic requests, two workers and existing repair/transport budgets remain unchanged. "
        "No real model, Skill execution or historical replay occurred during this acceptance. "
        "Semantic review is not a formal proof of natural-language equivalence or global minimality. No analyzed Skill is rewritten.\n", encoding="utf-8")
    state_path = DIRECTORY / "continuation-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update(status="offline_accepted", implementation_status="implemented_and_offline_accepted", implementation_sha256=digest)
    state["offline_acceptance"].update(status="passed", aggregate_accepted_count=passed, skipped=skipped, pending=[],
        receipt="output/verification/input-necessity-20261111/offline-acceptance.json", whole_repository_all_green_claim=False)
    state["online_authorization"]["status"] = "authorized_after_offline_acceptance_ready_to_prepare"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    agent_path = ROOT / "AGENTS.md"
    text = agent_path.read_text(encoding="utf-8")
    text = text.replace("OFFLINE ACCEPTANCE IN PROGRESS.",
        f"OFFLINE ACCEPTANCE COMPLETE: {passed} distinct latest scoped cases passed, {skipped} skipped, zero unresolved failures; not one whole-repository all-green execution. Accepted implementation SHA {digest}. See output/verification/input-necessity-20261111/offline-acceptance.json.", 1)
    agent_path.write_text(text, encoding="utf-8")
    current = ROOT / "docs/current-version.md"
    text = current.read_text(encoding="utf-8").replace("necessity; OFFLINE ACCEPTANCE IN PROGRESS", "necessity; OFFLINE ACCEPTANCE COMPLETE", 1)
    current.write_text(text, encoding="utf-8")
    design = ROOT / "docs/doe/input-necessity.zh.md"
    text = design.read_text(encoding="utf-8")
    text = text.replace("**OFFLINE ACCEPTANCE IN PROGRESS（离线验收进行中）**。\n本轮实现已经进入当前工作树，尚未宣布整体验收完成，尚未在本页宣称已准备或启动新的真实运行。",
        f"**OFFLINE ACCEPTANCE COMPLETE（离线验收通过）**。\n最新去重收据 {passed} 项通过、{skipped} 项跳过、0 项未解决失败；完整记录见[离线验收](../../output/verification/input-necessity-20261111/assessment.zh.md)。这不是一次全仓全绿执行。")
    begin = text.index("本轮仅进行针对实现的离线检查与注入式工作流验证。")
    end = text.index("当前用户授权：", begin)
    text = text[:begin] + f"离线检查与注入式工作流验证已经完成：{passed} 项最新去重测试通过、{skipped} 项跳过，0 项未解决失败。初始失败及针对性修正均保留在[验收记录](../../output/verification/input-necessity-20261111/assessment.zh.md)。\n\n" + text[end:]
    design.write_text(text, encoding="utf-8")
    print(json.dumps({"status": "offline_accepted", "passed": passed, "skipped": skipped, "implementation_sha256": digest}))


if __name__ == "__main__":
    main()
