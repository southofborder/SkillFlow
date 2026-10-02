# 026 playwright｜语义评审

样例：**R02**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/026-playwright.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/026-playwright.png)。

CLI 优先、npx 前提和首次快照到交互的数据链保留；动态交互恢复和配置来源不完整，部分条件被压成无条件顺序。

## 需修改或注意的问题

1. **部分保留：重拍条件与新 refs 消费不完整。** [SKILL.md:65](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:65)至第 69 行要求用最新快照交互，并在导航或明显 DOM 变化后重拍。实际 `ir_011 → ir_013` 使用初始 refs，但 `block_007 → block_008` 无条件重拍，新的 `result_005` 不再供交互消费。建议保留何时需要重拍以及使用新 refs 继续工作的关系，不能只靠块名描述循环。

2. **遗漏控制关系：ref 失败后重拍再重试。** [references/workflows.md:93](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:93)的规则在 Skill 约束中有文字，实际图没有从失败交互到重拍再回到交互的恢复路径。建议仅为 ref 失效添加相应恢复，不扩大成所有错误都重试。产物捕获同样是 when useful，当前 `block_008 → block_009` 无条件，宜明确适用范围。

3. **内容遗漏：配置文件来源和显式覆盖。** [references/workflows.md:74](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:74)的当前目录 playwright-cli.json 默认读取及 --config 指定文件规则未进入结果。建议至少保留配置来源、覆盖条件与 CLI 的关联；示例 headless=false 和 1280×720 不能固化为全部任务的默认参数。

4. **独立 wrapper 组件的调用关系需澄清。** `block_010/ir_019 → block_011/ir_021` 保存参数、会话和 wrapper 执行，却从主入口不可达。主流程已经用 wrapper 资源执行 open/snapshot/interaction，需明确独立组件是其调用定义，还是漏了调用关系；不要直接串到流程末尾再次执行。依据 [SKILL.md:124](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:124)，也不应把 wrapper 内部逻辑重复展开为每个主步骤。

5. **来源条件的差异应保留。** [SKILL.md:56](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:56)允许用户偏好全局安装，[SKILL.md:130](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:130)允许仓库已有全局标准，而 [references/cli.md:3](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/cli.md:3)措辞更宽。当前约束主要只保留“已全局安装”。建议记录这些不同来源的条件，不把安装存在性当作唯一选择依据；该项是来源范围表达不足。

## 已保留的关键内容

npx 不可用时提示安装并停止，有效时继续；未擅自转成 Playwright 测试工程。示例 URL、元素编号、表单数据没有被硬编码为当前任务。会话优先级在 wrapper 原代码中可查，PNG 不展示它不代表提取丢失。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/R02.json)的全部 9 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **R02-F01｜部分保留**：默认优先 bundled wrapper；仓库已采用全局安装标准或用户偏好全局安装时，可以使用全局 CLI。用户没有明确要求测试文件时，不切换到 @playwright/test。 原文：[SKILL.md:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:9)、[SKILL.md:122](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:122)、[SKILL.md:57](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:57)；CFG：`skill.constraints`、`block_005.constraints`。

- **R02-F02｜保留**：提出命令前检查 npx；缺失则暂停并让用户安装 Node.js/npm，提供原文安装步骤；npx 存在后继续 wrapper，全局安装为可选。 原文：[SKILL.md:12](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:12)；CFG：`ir_001`、`ir_003`、`ir_004`、`edge_1`、`edge_2`。

- **R02-F03｜部分保留**：打开目标页面后 snapshot 获取元素引用，交互消费最新 snapshot 的引用；导航或显著 DOM 变化后重新 snapshot。 原文：[SKILL.md:63](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:63)；CFG：`ir_009`、`ir_011`、`ir_013`、`ir_015`、`edge_5`、`edge_6`、`edge_7`。

- **R02-F04｜部分保留**：引用丢失或过期导致命令失败时，重新 snapshot 后重试；该恢复规则只针对引用失效，不能扩展为任意失败都重试。原文未规定最大重试次数，不能凭空增加次数上限。 原文：[SKILL.md:80](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:80)、[SKILL.md:132](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:132)、[references/workflows.md:91](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:91)；CFG：`skill.constraints`、`ir_013`、`ir_015`。

- **R02-F05｜保留**：尚无新 snapshot 时只能使用 eX 等占位引用并解释；禁止通过 run-code 绕过引用。eval/run-code 仅在需要时使用，不能当作默认动作。 原文：[SKILL.md:139](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:139)；CFG：`skill.constraints`。

- **R02-F06｜保留**：wrapper 使用 npx 启动 @playwright/cli 并透传调用参数；只有调用未显式给 --session 且环境变量非空时，才注入 PLAYWRIGHT_CLI_SESSION。 原文：[SKILL.md:124](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:124)、[scripts/playwright_cli.sh:9](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/scripts/playwright_cli.sh:9)；CFG：`ir_019`、`ir_021`。

- **R02-F07｜保留**：CLI reference 按 Core / Navigation / Keyboard 等列出的命令是可用调用形式；不能把 open、close、全部点击与键盘命令接成一次无条件流程。 原文：[SKILL.md:132](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:132)、[references/cli.md:19](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/cli.md:19)；CFG：`diagnostics`、`ir_009`、`ir_013`。

- **R02-F08｜保留**：仓库中捕获的产物放 output/playwright/；workflow 对此补充以 output/playwright/<label>/ 为工作目录保持产物集中。 原文：[SKILL.md:146](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:146)、[SKILL.md:132](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:132)、[references/workflows.md:3](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:3)；CFG：`skill.constraints`、`block_009.constraints`。

- **R02-F09｜部分保留**：playwright-cli.json 默认从当前目录读取，--config 可覆盖路径；后接 JSON 标为 Minimal example，不能把 headless=false 或 1280×720 视作每次执行的固定参数。 原文：[SKILL.md:132](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/SKILL.md:132)、[references/workflows.md:72](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:72)；CFG：`diagnostics`。

## 复核边界

只评当前抽象流程，不要求把每种 CLI 命令示例都变成任务。没有显式循环不自动构成错误；这里指出的是已产生的新 refs 未被使用以及原文明确的失败恢复关系未表达。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R02/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
