# 027 gh-fix-ci｜语义评审

样例：**R03**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/027-gh-fix-ci.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/027-gh-fix-ci.png)。

批准后实施的关键限制保留，但脚本/手工路径汇合存在真实数据依赖缺口，手工回退的 PR 来源和异常处理粒度不足。

## 需修改或注意的问题

1. **优先修正：互斥分支结果被同时要求。** [SKILL.md:36](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:36)与 [SKILL.md:39](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:39)是首选脚本及手工回退。图在 `block_004` 二选一，但 `ir_013` 同时要求 `result_006/result_008`，`ir_015` 又同时要求 `result_005/result_007`。每条路径只产生其中一组。建议分别将当前分支的检查状态和结果绑定后汇合，不让读者假设另一分支已经执行，也不强制固定合流操作名。

2. **手工路径的 PR 与日志来源未完整落实。** [SKILL.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:19)及 [SKILL.md:33](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:33)允许 PR 缺省并取当前分支；`ir_011` 手工操作直接消费可缺省 pr_input，没有该路径的解析生产者。[SKILL.md:42](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:42)至第 46 行要求提取 run/job 信息及按日志状态回退，手工命令仍有占位符。建议补出这些命令所需标识的来源及适用条件。脚本 `ir_009` 原代码已处理相应逻辑，不应据手工缺口判脚本分支也丢失。

3. **字段降级与外部服务范围主要留在文字中。** [SKILL.md:41](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:41)要求字段被拒绝时按可用字段重跑，[SKILL.md:48](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:48)限定外部检查只报告 URL。手工块约束有意图，但没有字段结果/重跑关系，也无实际 external 分类对后续日志查询的限制。建议在手工操作中明确这些条件和输出，避免把全部失败都送入 GitHub Actions 日志处理。

4. **面向用户的失败摘要表达较弱。** [SKILL.md:50](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:50)要求提供摘要，`ir_015` 生成 failure_summary 后只供计划生成使用；单独的摘要交付没有明确输出。建议让向用户展示检查名、URL、日志片段和缺日志说明成为可追踪的结果。实际批准门控存在，不能将本项误写成未经批准就实施。

## 已保留的关键内容

`ir_017/ir_018` 生成计划并请求批准，`ir_020` 的批准与未批准分支决定是否到实施 `ir_022`，关键授权限制有实际控制作用。认证失败停止、外部服务不调查、脚本原码保存及修改后复查建议均可见。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/R03.json)的全部 9 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **R03-F01｜保留**：先在仓库验证 gh auth status；未认证时请用户登录且具备所需 scope，之后才继续。 原文：[SKILL.md:29](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:29)；CFG：`ir_003`、`ir_005`、`edge_2`、`edge_3`。

- **R03-F02｜部分保留**：用户提供的 PR 号或 URL 直接作为 PR 标识；省略时读取当前分支 PR，后续 failing-check 查询消费这个解析结果。 原文：[SKILL.md:16](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:16)、[SKILL.md:32](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:32)；CFG：`ir_001`、`ir_009`、`ir_011`、`edge_4`、`edge_5`。

- **R03-F03｜保留**：首选运行 bundled inspect_pr_checks.py 取得失败检查、GitHub Actions 日志和失败片段；可通过 --json 获取供总结的机器输出，脚本作为一个调用边界保留。 原文：[SKILL.md:35](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:35)、[SKILL.md:60](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:60)；CFG：`block_004.constraints`、`ir_009`。

- **R03-F04｜部分保留**：手动回退查询若 JSON 字段被 gh 拒绝，按 gh 返回的可用字段重试；脚本同样用 available_fields 筛选 fallback_fields，无可用字段或再失败则返回。 原文：[SKILL.md:39](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:39)、[scripts/inspect_pr_checks.py:182](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py:182)；CFG：`ir_009`、`ir_011`、`block_006.constraints`、`diagnostics`。

- **R03-F05｜部分保留**：从失败检查的 detailsUrl 提取 run id 并读取对应 run 元信息和日志；run 日志报告仍在运行中且有 job id 时回退至 job logs。手动 gh api 回退将日志重定向写入指定的 <path>；脚本回退返回内存中的日志内容及状态，失败或尚未完成分别保留状态。 原文：[SKILL.md:42](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:42)、[scripts/inspect_pr_checks.py:333](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py:333)、[scripts/inspect_pr_checks.py:366](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py:366)；CFG：`ir_009`、`ir_011`、`block_006.constraints`、`diagnostics`。

- **R03-F06｜部分保留**：非 GitHub Actions 检查标为 external，只报告 URL；禁止进入 Buildkite 等外部供应商的调查，不能把供应商能力说明转换成调用。 原文：[SKILL.md:47](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:47)、[scripts/inspect_pr_checks.py:244](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py:244)；CFG：`ir_009`、`ir_011`、`skill.constraints`、`block_006.constraints`、`block_009.constraints`。

- **R03-F07｜部分保留**：向用户汇报失败检查名、run URL 和简短日志片段，缺失日志必须显式标出；之后提出修复计划，获得明确批准后才应用计划。 原文：[SKILL.md:50](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:50)；CFG：`ir_015`、`block_009.constraints`、`ir_017`、`ir_018`、`ir_020`、`ir_022`、`edge_12`、`edge_13`。

- **R03-F08｜保留**：修复后原文只要求建议重跑相关测试和 gh pr checks；不能把该建议或询问开 PR 改写成已自动运行测试或已打开 PR。 原文：[SKILL.md:55](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:55)；CFG：`ir_024`、`ir_026`、`block_013`。

- **R03-F09｜保留**：脚本检测不到失败检查时打印消息并以 0 退出；存在失败检查时输出结果后以 1 退出。非零返回码不能直接被理解为没有产生可用分析结果。 原文：[SKILL.md:64](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:64)、[scripts/inspect_pr_checks.py:110](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/scripts/inspect_pr_checks.py:110)；CFG：`ir_009`、`block_005.constraints`、`ir_013`、`ir_015`、`edge_8`、`edge_9`。

## 复核边界

源文没有定义失败时强制无限重试；不要用脚本正确实现来替手工路径补缺失证据。图不显示原码、日志样例和 metadata 是展示选择，不能据此判脚本逻辑遗漏。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R03/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
