# 028 netlify-deploy｜语义评审

样例：**R04**；选定轮次：**第 1 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包](D:/projects/SkillFlow/dataset/skills/028-netlify-deploy.zip) · [PNG 实际 CFG](D:/projects/SkillFlow/result/ir-IPP/028-netlify-deploy.png)。

认证、关联、部署的主分支已建立，但多处汇合输入不成立，认证终止和场景限制不完整；原文自身的预览/生产规则冲突也应保留。

## 需修改或注意的问题

1. **优先修正：多处互斥结果无选择绑定。** [SKILL.md:78](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:78)允许已关联直接继续；`ir_025` 却同时使用仅 link 与 init 分支产生的 `result_007/result_008`，已关联路径两个都不产生。`ir_035/ir_039` 又同时要求 preview、production、escalated 三种部署的日志/URL。建议各阶段只汇合当前路径的有效结果，不能通过执行所有分支来补齐数据。

2. **关键恢复遗漏：认证失败终止与 token 替代。** [SKILL.md:32](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:32)要求认证无法建立时合理失败，[SKILL.md:62](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:62)允许浏览器认证不可用时用 token。实际 `block_003 → block_001` 只返回重查，持续未认证将反复 login；token 只在全局文字。建议明确停止/返回及条件替代，保留等待用户完成登录的限制，不编造固定重试次数。

3. **来源限制扩大：静态站点也必读 package.json。** [SKILL.md:161](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:161)支持静态 HTML，[SKILL.md:163](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:163)仅要求 if possible 检测。实际 `ir_017/ir_019` 位于所有关联成功路径上，没有文件缺失边界。[SKILL.md:154](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:154)所述配置文件或用户回复也没有实际来源绑定到部署。建议给可检测条件及配置来源，保留无构建命令的静态站点，不默认每站点都有 package.json。

4. **部署过程和分类恢复表达不足。** [SKILL.md:138](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:138)要求配置、构建、上传及 URL 关系；实际部署调用主要只列 CLI 资源，缺少明确配置与构建产物流。[SKILL.md:202](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:202)与 [SKILL.md:207](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:207)有不同故障条件，`block_017/ir_033–ir_036` 却在所有 other failure 路径依次执行全部检查。建议保留高层部署操作可以封装内部过程，但其来源、产物和恢复适用条件必须清楚。

5. **源文冲突：不要自行选定发布政策。** [SKILL.md:130](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:130)允许新站生产部署，[SKILL.md:233](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:233)及 [references/deployment-patterns.md:171](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/references/deployment-patterns.md:171)又要求先预览；测试场景还有预览验证再发布要求。当前 `ir_025` 采用新站直接生产，未保留冲突。建议列出两处规则和场景差异待明确，不凭默认值裁决；预览获批再生产的可选后续也需表达。

6. **环境变量只留下提示，配置去向不足。** [SKILL.md:227](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:227)至第 229 行说明禁入 Git、在 Netlify 设置及构建读取。全局约束保留文字，但没有所需值到 Netlify 配置的实际关系。建议对需要环境变量的场景明确该流向；无需将 env:import 示例变成每次必执行动作。

## 已保留的关键内容

预览与生产是互斥选择，没有无条件连续发布两次；非 Git 项目的 init 路径保留，网络失败才进入提升权限的重跑路径；Never commit secrets 全局禁令保留。

## 逐项核对

以下对照[外置事实标注](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/annotations/R04.json)的全部 10 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。

- **R04-F01｜部分保留**：检查 Netlify 登录状态；未认证时指导 OAuth 登录并等待用户完成，再查 status；浏览器认证不可用可改用 NETLIFY_AUTH_TOKEN，仍不能建立认证时结束。 原文：[SKILL.md:30](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:30)、[SKILL.md:52](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:52)；CFG：`ir_001`、`ir_003`、`ir_005`、`block_003.constraints`、`edge_3`、`edge_4`、`skill.constraints`、`diagnostics`。

- **R04-F02｜保留**：从 status 输出取得站点关联状态；已关联则跳过关联步骤，未关联且为 Git 仓库则读取 origin remote URL 传给 netlify link --git-remote-url，关联失败时 init。 原文：[SKILL.md:70](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:70)；CFG：`ir_007`、`ir_009`、`ir_011`、`ir_013`、`ir_015`、`edge_5`、`edge_8`、`edge_11`。

- **R04-F03｜部分保留**：按需引用 deployment-patterns 的决策树后，未关联且非 Git 仓库时直接 init；新站或首次发布与已有站点分别选择生产发布和预览发布。 原文：[SKILL.md:243](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:243)、[references/deployment-patterns.md:5](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/references/deployment-patterns.md:5)；CFG：`ir_015`、`ir_025`、`ir_025.constraints`、`edge_9`、`edge_17`、`edge_18`、`diagnostics`。

- **R04-F04｜部分保留**：已有站点默认 preview；新站或明确生产请求采用 --prod；预览测试场景的参考流程要求预览获批后才生产发布，不能把两个 deploy 命令无条件串联。 原文：[SKILL.md:118](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:118)、[SKILL.md:243](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:243)、[references/deployment-patterns.md:70](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/references/deployment-patterns.md:70)；CFG：`ir_025`、`ir_027`、`ir_029`、`edge_17`、`edge_18`、`edge_19`、`diagnostics`。

- **R04-F05｜部分保留**：发布前确保项目依赖已安装并根据包管理器选命令；发布读取构建设置，在本地构建并上传构建产物至 Netlify，取得并向用户报告部署 URL、适用的生产 URL 和日志链接。 原文：[SKILL.md:106](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:106)、[SKILL.md:138](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:138)；CFG：`ir_017`、`ir_019`、`ir_021`、`ir_027`、`ir_029`、`ir_031`、`ir_039`、`ir_040`。

- **R04-F06｜部分保留**：已有 netlify.toml 由 CLI 自动使用；缺失时询问 build command 和 publish directory，可读 package.json 判断框架并建议值。参考 TOML 的 command/publish/base 属构建配置，不能把所有示例配置同时执行。 原文：[SKILL.md:152](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:152)、[SKILL.md:243](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:243)、[references/netlify-toml.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/references/netlify-toml.md:13)；CFG：`skill.constraints`、`ir_017`、`ir_019`、`ir_025`、`ir_027`、`ir_029`。

- **R04-F07｜部分保留**：构建失败时检查构建命令、发布目录、依赖和日志；publish directory 不存在时验证构建已成功以及目录路径。保留这些特定故障条件。 原文：[SKILL.md:192](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:192)；CFG：`ir_033`、`ir_034`、`ir_035`、`ir_036`、`edge_21`、`edge_24`、`edge_26`。

- **R04-F08｜保留**：网络超时、DNS 错误、连接重置或沙箱阻断出站请求时，上游文档要求以 escalated permissions 重跑部署；这是样例实际提出的有条件要求，静态分析应保留其范围，不在语料复核中执行。 原文：[SKILL.md:213](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:213)；CFG：`ir_031`、`block_016.constraints`、`skill.constraints`、`edge_20`、`edge_23`。

- **R04-F09｜部分保留**：“Never commit secrets to Git”约束整份部署流程；需要环境秘密时写入 Netlify 配置并由构建访问。CLI reference 中 env:import .env 只是能力条目，不能凭此制造每次自动导入。 原文：[SKILL.md:223](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:223)、[SKILL.md:243](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:243)、[references/cli-commands.md:82](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/references/cli-commands.md:82)；CFG：`skill.constraints`。

- **R04-F10｜保留**：References 中的 Netlify 官网文档仅提供 URL，包内 Bundled References 才作为已提供文本；不得把未下载外链文档的隐含步骤补入本轮输入。 原文：[SKILL.md:238](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:238)；CFG：`diagnostics`、`block_001`、`block_005`、`block_009`。

## 复核边界

本意见仅静态检查当前 CFG，并不执行部署、认证或发布。源文互相冲突时应保留不确定性，不借评审替用户作发布决策；额外配置示例不应全部自动执行。

本次同时核对了[选定 analysis.json](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R04/deepseek-v4-flash-max/1/analysis.json)中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。

这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。
