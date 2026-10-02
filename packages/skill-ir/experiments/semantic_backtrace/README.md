# 受控语义回述与完整源文核对（v5）

当前流程只有一项模型任务：比较完整原文与经 Lean 生成、解析和恢复检查的受控文本。模型不读原始图，不生成回述，不另行提取要求列表。规范见 [受控语义回述与源文核对](../../../../docs/Skill-IR受控语义回述与源文核对规范.md)。

v5 按 [统一解释契约与阅读检查点](../../../../docs/Skill-IR解释契约与逐项语义核对规范.md) 核对语义，由模型组织相关要求；取消强制类别与精度分类，仅在适用时记录保守依赖说明。未填写该说明不代表精确。保守候选不等于实际同时传递，也不豁免动作遗漏、错误绑定或禁止事项。运行记录绑定契约版本及摘要，程序验证记录与证据，不证明模型语义判断。

固定材料保留在 `f01/`：manifest 绑定 013/F01/第1轮原始 analysis 与完整 Skill 包；oracle 是外置人工预期，只在核对之后用于评测；examples 是历史人工规格示例，不作为模型实测结果或新版输入。历史运行目录保持原样，旧运行、重放及诊断导出代码已删除，当前入口不支持旧版记录。

先在 `packages/skill-ir/formal` 使用固定 Lean 工具链构建 `lake build` 并执行 `lake env lean ProofAudit.lean`。生产提取无需 Lean；独立受控回述实验需要构建后的打印器。

从仓库根目录运行：

```powershell
python -m skill_ir.backtrace prepare --suite semantics-v5-seven --run-dir packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v5-seven
python -m skill_ir.backtrace run --run-dir packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v5-seven --env-file .env
python -m skill_ir.backtrace replay --run-dir packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v5-seven
```

prepare 默认核验30个固定原图及F01四个反例，不联网。默认套件 `f01-five` 包含5例；`semantics-v5-seven` 增加暂停批次001、010第0轮图与同轮冻结源文，共7次逻辑核对。使用官方 DeepSeek 固定模型，600秒连接/阻塞读取超时；明确暂态传输失败最多额外执行重试2次，完整响应中的格式或语义问题不补跑。`--renderer` 指定打印器；`run --env-file` 指定环境文件；`--workers` 控制案例并发。不中途修改提示词、不截断、不择优，不自动重发不确定请求，单例错误不阻断其余案例。

新运行目录包含 `inputs/`、`verification/`、`calls/`、`parsed/`、`suggestions/` 与 `report.md/json`。模型看到的受控文本就是证书绑定的文本；原图只供生成、往返检查与最终定位。replay 不创建API客户端，不读取凭据，结果写入 `replay/`，原始调用记录不改写。源码或打印器变化后不得沿用原在线运行身份。

受控事实保持证明不能替代原文转换正确性、模型核对正确性、路径可执行性或运行安全保证。证据区域匹配仅生成复核候选，无法完成必要判断及执行错误不算通过。验收报告分别记录工程与方法结果，助手复核不冒充用户确认。

v4 七例实测见 [实施与复测报告](runs/controlled-v4-seven-20260918/acceptance.md)：7 次逻辑调用、7 次执行、7 次 HTTP 尝试，4 例合法核对记录，2 例本地流式记录失败，1 例完整响应引用非法事实编号。两个有效反例报告目标缺陷；001、010 均无未决，010 明确记录合流的保守依赖。1264 项回归、30 图及七例转换检查、Lean 构建与公理审计通过，离线重放保持相同结果。逐例助手复核保留顺序解释过强、自由文字块号错误与判断边界；[运行诊断](runs/controlled-v4-seven-20260918/runtime_diagnostics.md)记录本轮未修复的本地保存问题。未恢复暂停批次、未重新提取或执行安全标注。

历史 v2 实测见 [当时的中文验收报告](runs/controlled-v2-f01-20260914T142804Z/acceptance.md)。其结果按当时契约解释，不能作为 v4 实测；历史报告与调用原件保持不变。新版结果以独立运行目录为准。

历史 v3 七例结果见 [实施及七例验收](runs/controlled-v3-seven-20260918/acceptance.md)：7次逻辑核对、9次执行，5例合法响应、2例输出协议错误；未因坏JSON或缺字段补跑。001、010分别得到精确保留和含保守依赖的保留记录，三个有效反例命中目标缺陷，失败出口缺追加的反例响应无效，不计有效命中。逐例说明与剩余判断边界见同目录 `assistant_review.md`，这些是助手复核而非用户确认。
