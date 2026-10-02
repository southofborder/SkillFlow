# 029 linear｜语义评审

样例：**R05**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/029-linear.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/029-linear.png)。

九类工作流和多数先读后写步骤保留，但汇合结果、恢复流程及个别写入限制不完整；另发现 Smart Labeling 将可选应用标签变成必经写入。

## 需修改或注意的问题

1. **优先修正：九条互斥工作流被要求同时提供结果。** [SKILL.md:44](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:44)要求选合适工作流，[SKILL.md:53](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:53)要求总结。图在 `block_005` 九选一，`block_023/ir_061` 却同时消费九支的结果，当前路径无法产生全部输入。建议建立当前工作流结果的统一出口或条件绑定，再总结；不能执行其余工作流来补结果。

2. **新增错转：仅建议标签的选择丢失。** [SKILL.md:72](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:72)允许 suggest/apply labels。实际 Smart Labeling 经 `block_019 → block_020` 无条件执行 `ir_052` 建议标签、`ir_053 apply_labels_to_issues` 应用标签；应用操作及块的约束/metadata 均为空，没有仅建议后返回的选择。建议按请求意图保留“仅建议”与“应用”的边界。此项在旧十条事实之外单列，不伪装成旧事实已覆盖。

3. **关键限制弱化：Release 路径没有先读。** [SKILL.md:48](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:48)要求先 list/get/search，再创建。Release Planning 从 `block_005 → block_014` 直接进入 `ir_036` 创建项目，前面的确认标识不是读取现有工作区上下文。建议在写入前保留所需读取，不能只依赖全局 Read first 文本。

4. **文档审计内容遗漏。** [SKILL.md:67](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:67)要求 documentation 标签和详细修复内容。`ir_028` 创建 issue 只消费缺口与标识，前序 `ir_027` 只是缺口分析，输入/约束/metadata 没有标签与 detailed fixes。建议把两项绑定到创建操作，不能将发现缺口自动当作已经生成修复说明。

5. **分类恢复与连接恢复不完整。** [SKILL.md:24](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:24)适用于任一 MCP 调用因未连接失败；当前只在初始 `block_001` 检查，后续调用失败无恢复边。登录 `ir_005` 也无成功结果或条件就进入重启提示。[SKILL.md:84](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:84)至第 87 行的认证、工具调用、数据缺失、性能恢复没有分别保留。建议明确各类触发、动作及终止/继续关系，不把所有故障都重跑 OAuth。

6. **不要误判仍保留的条件抽象。** [SKILL.md:68](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:68)对应 `ir_034 suggest_or_apply_redistributions`，已经保留建议/应用选择；`ir_043 create_linked_issues_if_missing` 与 `ir_054 create_missing_label_categories` 也保留 missing 前提。Release 的估时在 `ir_038 create_release_issues_with_estimates` 中明确。这些不因没有独立分支或数值参数而判遗漏。

## 已保留的关键内容

目标范围澄清、必需标识确认以及八类工作流的读取阶段有实际操作。九个例子没有被无条件串行执行，报告和批次/缓存提示仍保留。配置示例中的 Windows/WSL 方案没有被变成全局必选环境。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/R05.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **R05-F01｜保留**：Linear MCP 必须已连接且经 OAuth 可访问，并确认相关 workspace/team/project 权限；主流程步骤按顺序执行，不能跳步。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:14)；CFG：`skill.constraints`、`ir_001`、`edge_1`、`edge_2`。

- **R05-F02｜部分保留**：任一 MCP 调用因未连接失败时暂停并配置连接：添加服务器、启用远程客户端、OAuth 登录；成功后告知重启 Codex并结束本次回答，后续从 Step 1 恢复。 原文：[SKILL.md:22](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:22)；CFG：`ir_001`、`ir_003`、`ir_004`、`ir_005`、`ir_006`、`edge_1`、`block_002.constraints`。

- **R05-F03｜保留**：Windows/WSL JSON 片段仅在 Windows 出现连接错误时作为尝试的配置分支；不应据此无条件启动 wsl 或建立第二个 MCP 会话。 原文：[SKILL.md:35](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:35)；CFG：`block_002.constraints`、`ir_003`、`edge_1`。

- **R05-F04｜部分保留**：先明确用户目标和范围以及所需 team/project 等字段，再选择适合工作流；调用前确认所选工具所需的标识（如 issue ID、project ID、team key），之后先 list/get/search 读取上下文，再创建或更新对象。 原文：[SKILL.md:40](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:40)；CFG：`ir_009`、`ir_011`、`ir_012`、`ir_036`、`edge_9`、`skill.constraints`。

- **R05-F05｜保留**：批量变更执行前解释分组逻辑；create/update 调用携带全部必填字段。这些要求作用于相应批处理和调用，不能据此凭空增加外部参数校验服务。 原文：[SKILL.md:46](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:46)；CFG：`skill.constraints`、`ir_017`、`ir_028`、`ir_036`。

- **R05-F06｜保留**：Available Tools 是能力清单，Step 2 才根据目标选择工具；不能把 list_issues、create_issue、update_issue 等全部生成无条件调用。 原文：[SKILL.md:43](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:43)、[SKILL.md:55](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:55)；CFG：`ir_012`、`edge_5`、`edge_7`、`edge_9`。

- **R05-F07｜部分保留**：Step 2 明确采用的 Practical Workflows 具有实际行为：例如文档审计先 search documentation，再为缺口或过期章节开带 documentation 标签及详细修复建议的 issue。仅被目标选中的流程进入执行路径。 原文：[SKILL.md:43](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:43)、[SKILL.md:63](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:63)；CFG：`edge_7`、`ir_025`、`ir_027`、`ir_028`。

- **R05-F08｜部分保留**：操作后总结结果，列出未解决缺口或阻碍并提出后续动作；大规模更新拆成较小批次以避免限流，频繁列举时可以缓存或复用筛选器。 原文：[SKILL.md:52](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:52)、[SKILL.md:75](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:75)；CFG：`block_023.constraints`、`ir_061`、`ir_062`、`skill.constraints`、`edge_15`、`edge_19`、`edge_22`。

- **R05-F09｜保留**：agents/openai.yaml 声明 Linear MCP 依赖、transport 和 URL，并给出 default_prompt；这是能力与接口元数据，不能单独制造一次远程调用或把 default_prompt 当成新用户任务。 原文：[SKILL.md:14](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:14)、[agents/openai.yaml:1](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/agents/openai.yaml:1)；CFG：`ir_001`、`ir_007`、`ir_012`、`skill.constraints`。

- **R05-F10｜遗漏**：故障恢复按类型分别适用：认证故障时清理浏览器 cookies、重新 OAuth、核查 workspace 权限和 API 访问是否启用；工具调用错误时确认模型支持多次工具调用、补齐必填字段并拆分复杂请求；数据缺失时刷新 token、核查 workspace 访问、归档项目及 team 选择；性能问题时考虑 API 限流，采用批处理、特定筛选器或缓存频繁查询。这些恢复操作仅属于相应故障分支，不能拼成所有任务都执行的步骤。 原文：[SKILL.md:82](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/linear/SKILL.md:82)；CFG：`skill.constraints`、`block_001`、`block_002`、`diagnostics`。

## 复核边界

原文叙述 create cycle，但工具目录仅列 list_cycles，这属于冻结来源中的能力边界，不替来源扩充真实工具列表。公开示例中的项目名等不应固化成每次真实操作值。这里的应用标签问题与仅保留高层操作名的等价表达分开判断。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R05/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
