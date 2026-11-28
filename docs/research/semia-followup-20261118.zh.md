# Semia 首例跟进与剩余样本执行约定

用户在 2026-11-18 要求继续跟进 SEMIA，等首例跑完后分析结果和失败原因，再推进剩余样本的同模型、同输入对照。

**执行结果（2026-11-19）：四例均已终止，以下为本轮执行约定记录，不构成再次启动授权。** 首例分析完成后才启动010、013、GA4；010完成检测，另外三例未生成合法表示。最终结果、失败诊断和比较边界见[四样本汇总](semia-cohort-results-20261119.zh.md)。原始证据保留，没有自动实施修复变体或启动新一轮。

本轮观察已有 `pilot/001`，不会重复启动或改变其进行中的提示、校验及预算。首例终止后，依据原始回答、每份候选、校验结果、实际请求和公开用量完成分析；root 将终止回执 SHA 绑定到 `analysis/001-closeout.json` 后，后续入口才允许启动。首例失败也是有效的基线记录，不要求先修补到成功。

剩余顺序为 010、013、GA4，最多两个独立样本并发；每例只建立一个新输出目录 `comparison/<case>`。固定上游源码仍为 `379bc25fe99833eb185efe56a38fe15f0235799c`，原提示、结构校验、反馈和选择机制保持一致；此前发现的提示矛盾、计数反馈及未传回无效候选问题都保留在原版基线中，不将修订后的方法混入同一个分数。

为了达到用户选择的完整同输入条件，后续明确命名为 `Semia + controlled transport + complete source`。输入适配只在官方 prepare 期间允许清单中的 `package.json`、`package-lock.json` 纳入；保持官方渲染、源行映射、语义单元构建与提示模板，并核验每个源文件的正文及其在实际送模提示中的完整存在。001、010、013 无此过滤差异；GA4 从原版14文件变为完整16文件，语义单元从623增至3155，因此覆盖率分母和成本可能变化，不能把这一变体写成上游默认行为。

模型配置为 `gpt-6.1-sol / high / openai`，固定首例实际CLI路径与SHA，使用builtin检测后端。原生单请求截止为2700秒，保留5个合成iteration、3次结构重试、2次provider重试。上游默认还有检测报告后的recommendation模型请求；后续分别计数CGRS与recommendation，最坏原生启动上限为60+3=63。首例的冻结上限为60，其是否产生实际影响以最终是否触及上限为准。provider错误重试覆盖全部非配置类`LlmSynthesisError`；原生内部采样重连另外记录，未知用量不记零。

这是SEMIA侧的完整输入工程对照。历史SkillFlow结果保持旧版本和继承身份，本轮不自动重启或回放旧SkillFlow/GA4，也不宣称已完成统一当前实现版本的配对准确率实验。四个长期开发样本没有独立金标，精确率、召回率和方法优越性仍为未评估。

材料入口：[主协议](semia-comparison-protocol-20261118.zh.md)、[运行状态](../../experiments/baselines/semia-20261118/continuation-state.json)、[完整源离线预检](../../experiments/baselines/semia-20261118/analysis/full-source-preflight/manifest.json)、[首例分析](../../experiments/baselines/semia-20261118/analysis/001-failure-audit.zh.md)。
