# 受控语义回述 v2：工程、证明与首次方法验收

本轮已完成重构、实际文本保真检查、五次官方 DeepSeek 核对及离线重放。唯一模型任务是**完整原文与受控文本核对**。本报告中的方法复核由助手完成，尚未经用户确认。

运行编号：`controlled-v2-f01-20260914T142804Z`。先阅读本页；需要证据时再打开[逐项助手复核](assistant_review.md)、[原始模型报告](report.md)或[完整运行 JSON](report.json)。本轮没有生成 PDF。

## 首次实测差异

| 案例 | 固定输入 | 模型实际结果 | 助手事后复核 |
| --- | --- | --- | --- |
| c01 | F01 原图，013/第 1 轮 | 17 项业务保留，无业务差异或未决 | 四组关键要求已核对；finding_18 有一处块编号说明错误。 |
| c02 | archive 额外接收 FAST_KEY | finding_6 错转；finding_7 内部冲突 | 同一密钥输入缺陷的两个方面，计 1 个目标命中。 |
| c03 | 删除失败出口状态追加 | finding_10 遗漏 | 正确区分残留标题/约束与实际操作清单；建议补在现有 return 前。 |
| c04 | 重试成功返回首次 body | finding_7b 错转 | 正确识别 result_004 与 result_008；finding_2 另有读取顺序的过度解读。 |
| c05 | 额外等待 2 秒 | finding_5 无依据新增 | 正确识别等待；另有检查/返回位置描述不严谨及操作层引证不足。 |

在本次助手复核范围内，四个预设缺陷均命中，未观察到目标漏报或额外业务缺陷误报；模型没有给出 unknown，执行错误为 0。**这不是方法正确率估计**，也不说明核对文本完全正确：三处解释不准确和一处操作层引证不足完整记录在 [assistant_review.md](assistant_review.md) 与 [method_review.json](method_review.json)。自动评测只生成证据区域匹配候选，助手复核也不冒充用户确认。

逐条原始修改建议：[c01](suggestions/c01.md)、[c02](suggestions/c02.md)、[c03](suggestions/c03.md)、[c04](suggestions/c04.md)、[c05](suggestions/c05.md)。建议只存档，没有自动改图。派生链接及操作清单应在 CFG 修改后重新生成，不能单独修改；c04 的修复需要更改实际 identifier 及相应语义标签，不能只改块名。

## 工程与证明结果

| 验收项 | 实际结果 | 记录 |
| --- | --- | --- |
| Lean 构建 | 成功；唯一实际打印器和解析器参与转换 | [证明说明](../../../../formal/CONTROLLED_RETELLING.md) |
| 公理审计 | 16 个主定理，其中新增 11 个；没有 sorry、占位公理或绕过内核检查 | [审计输出](verification/proof-audit.txt) |
| 固定图离线转换 | 30 原图 + F01 四反例，34 个不同输入全部通过实际文本解析与逐字段恢复比较 | [30 图清单](verification/review30.json)、inputs/c01–c05 |
| 回归测试 | 860 项通过，退出码 0 | [完整输出](verification/pytest-full.txt) |
| 模型输入绑定 | 五份实际正文摘要均与转换证书一致，输入允许字段固定 | [输入隔离检查](verification/payload-isolation.json) |
| 真实调用 | 5 个独立逻辑调用，5 次 HTTP 请求，每案例一次；没有修复或补跑 | calls/ 及 report.json |
| 离线重放 | 0 客户端创建、0 凭据读取、0 网络尝试；核对、评测与调用汇总一致 | [重放验收](verification/replay.json) |
| 已有材料保护 | 对 1,616 个保护文件逐文件验摘要，变化 0；新运行无配置凭据内容 | [最终保护检查](verification/protected-final.json) |

生产 Prompt、IR 字段、提取 pipeline、结构校验、冻结输入、ZIP、PNG、既有评审和历史实验记录未变。旧要求提取、自由回译、多方向模型核对、旧分阶段调度、Python 回述打印器及专属诊断工具均已移除。v1 历史记录保留，v2 入口明确拒绝将其运行或重放。

## 证明具体保证什么

形式化输入是完整的 RichGraph：不仅包含控制结构，也保留实际 opcode、所有操作数、标识、语义标签、字面值、draft ID、三级约束、上下文、顺序、完整 metadata 和控制边。literal/metadata 以规范 JSON 字符串保持，未解释嵌入源码行为。

已证明的核心关系为 `parseGraph(renderGraph(g)) = some g`：只读取真正打印出来的受控文本，即可恢复原来的富记录图。相关定理同时保持分类、作用域、位置、记录顺序和结果定义链接。正式解析入口还核对整份规范重印文本，不能只保留一个隐藏载荷却允许可见事实被篡改。

Python 每次都调用该 Lean 实现，从实际文本恢复规范 CFG，与输入逐字段比较，并绑定原图、正文、证据单元、链接、源码和可执行文件摘要。模型收到的就是已核验的原文本体；恢复失败或摘要不符时禁止该案例调用模型，不回退旧实现。

证明的公理基础明确包括 Lean 标准的 `propext`、`Quot.sound`，部分文本定理还使用 `Classical.choice`，不是“完全无公理”。Python Schema、JSON 规范化、JSONL 进程传输、编译器/可执行文件及模型请求封装仍属工程信任边界；本轮以实际往返、哈希绑定与回归测试验证这些边界，没有给出它们的全链路形式证明。

这不证明源文到图正确、模型说明正确、条件实现正确、所有路径可执行、文件写入成功、开放操作无隐藏副作用或自由中文的理解正确。没有 unknown 条目也不能消除这些未证明事项。

## 实际调用记录与效率边界

请求配置为官方 `deepseek-v4-flash`，API 实际返回名称均为 `deepseek-flash`；二者分别存档，没有强行改写成同一个名称。API 报告总用量：输入 178,878 tokens，完成 253,019 tokens，总计 431,897 tokens，其中 reasoning 为 195,728 tokens（属于完成用量）。没有估算费用。

当前受控文本强调完整记录、固定标签、块内清单与证据定位；F01 单份正文约 6.4–6.7 万字符，实际请求约 3.5–3.6 万输入 tokens。它是严格受控的结构化记录语言，仍然冗长。本轮没有做与直接读图的对照，不能宣称已证明降低认知负担、成本或提高泛化准确率。

## 复现与入口

使用固定 Lean 工具链在 `packages/skill-ir/formal` 下执行 `lake build` 和 `lake env lean ProofAudit.lean`。在仓库根目录创建新的运行目录，然后分别执行：

```powershell
python -m skill_ir.backtrace prepare --run-dir <新运行目录>
python -m skill_ir.backtrace run --run-dir <新运行目录>
python -m skill_ir.backtrace replay --run-dir <已有v2运行目录>
```

prepare 和 replay 不调用 API；run 按案例调用一次。已有接受的响应不会自动重发。完整使用说明见[实验 README](../../README.md)，当前流程规格见[受控语义回述与源文核对规范](../../../../../../docs/Skill-IR受控语义回述与源文核对规范.md)。
