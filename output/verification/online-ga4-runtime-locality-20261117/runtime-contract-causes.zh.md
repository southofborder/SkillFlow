# 运行时契约与当前局部未完成的原因

**反复出现 `partial`，不能统一归因于运行时契约不完整。** 本轮同时出现了表示与证据不合规、具体源文行为的表达缺口，以及任务义务尚未充分实现。源文审查仍在运行，这份说明只解释已保存的生成及校验材料，不是最终执行覆盖、字段必要性或 DOE 结论。快照及引用文件摘要见同目录 [runtime-contract-causes.snapshot.json](runtime-contract-causes.snapshot.json)。

本轮沿用完整 16 文件源文与所选 489 IR CFG，冻结实现为 `3ebfb40a0053f0e3dc84aa4c7877b116445749b478b912910b8a9d192d787af6`。七阶段中的前三阶段继承，四阶段重新请求；两个 worker 与纠错、共享修复、超时预算不变。离线验收为 6,023 项最新独立测试通过、3 项有说明的跳过，并非一次全仓库全绿执行。[离线验收说明](../runtime-locality-20261117/offline-assessment.zh.md)

## 有限运行时契约现在保证什么

运行时契约 v12 明确列出 14 种原子操作：`read`、`receive`、`deliver`、`write`、`select_part`、`exclude_parts`、`update_fields`、`build`、`compute`、`filter_items`、`merge`、`member`、`branch`、`append`；另有配对请求／响应的 `call`、三种结构 `processing`／`for_each`／`cases`，以及 14 种结构化表达式。清单与类型 schema 核对，并说明输入域、身份与别名、效果、失败及证据要求。

这保证了**系统支持词汇的边界可检查**，不保证模型选对操作，也不代表所有 JavaScript、外部工具或任意 Skill 的语义都已覆盖。工具输入必要性仍须由接口依据支撑；一次操作实际读取了某字段，不足以证明该字段对于任务输出必要。源文行为确实不能表达时，必须留下具体范围与依据。[设计说明](../../../docs/doe/runtime-locality.zh.md)

本轮 processing 确实收到完整新版契约、全部源文和逻辑 CFG；源文审查输入也保留了完整源文、annotation 与契约。不能把当前问题归因于这次投递遗漏了新版操作清单。[processing 输入核对](processing-input-v12-audit.zh.md)、[审查输入核对](source-review-input-v12-audit.zh.md)

## 未知值、未知地址与失败隔离

“不知道一个变量或异常的内容”不等于“不知道它属于哪个位置”。已知调用槽、异常槽或成员身份默认使用 `identified` 地址；只有地址关系本身无法确定时，才使用带具体原因和源文依据的 `unidentified`。真正未知的同类地址仍保留保守别名与弱写入。名称前缀不再决定地址是否相同，严格对象／集合域检查也没有放宽。

离线实现还保证：已知类型的操作数或集合域错误保留准确的 IR、操作、输入 Data、原始错误和成功前缀观察；失败 IR 的修改回滚，输出及可能写入位置标记不可用，再沿真实值、状态、成员及控制依赖传播阻断。独立部分可以继续，未知程序错误或完整性错误仍然致命。尚未执行不等于已证明不可达，也不能据此判定输入可删。**这些是实现和离线证据；此刻尚不能声称新 GA4 已验证了多少独立路径成功继续。**[设计与验收](../runtime-locality-20261117/offline-assessment.zh.md)

## 当前材料能够区分的原因

| 现象 | 已有依据与边界 |
| --- | --- |
| `ir_001` 被局部隔离 | a002 的 `/ir_semantics/ir_001/output_bindings/0/value` 报 `resource identity is not a data payload; use an evidenced literal or read`。该记录在 a001、a002 完全相同，原来的覆盖／证据错误先阻止了深层校验，所以不是纠错引入的新错误。原 CFG 将 `settings.ts:5` 的 `import { config } from 'dotenv'` 表为接口获取并产生 `result_001`；当前 processing 的数据绑定不合规。该错误不能证明 Skill 本身写错，也尚不足以确定应采用哪种源文忠实的模块／可调用值抽象。 |
| 首轮 14 条 processing 诊断 | 一条覆盖错误涉及 `ir_011`／`ir_436` 同时被列为 modeled 与 unmodeled；另外 13 条仅引运行时规则，缺少具体操作的源文或 CFG 机制依据。这些错误在 a002 已清除，随后才暴露 `ir_001`；不能继续把原 14 条算作当前残留。 |
| 四条源文声明的 unmodeled IR | `ir_011`、`ir_436` 声称缺少与模型观察、用户接收和文件边界相区别的本地 console 流；`ir_289`、`ir_295` 指出源文活对象中的 JavaScript `undefined` 自有字段不能用 JSON `null`、空对象或删字段等价替换。其依据分别定位到 `index.ts:364–405`／`355–362` 与 `api/indexing.ts:174–179`／`180–186`。这些是具体边界／值域问题，不是泛称“值未知”；但它们仍是模型提出、尚待独立源文审查的能力缺口。 |
| 19 条 processing gaps | 除上述 unmodeled 范围，还涉及可选值与序列化的差别、稀疏数组、条件时钟与异常后状态、源文排序要求冲突、存储路径与调用归属，以及未实现的后续总结义务。它们混合了表达能力、接口或源文关系不足及任务实现缺口，不能全部记为同一种运行时失败，也不能与四条 unmodeled 简单相加。 |
| 任务对应和敏感性纠错 | 任务对应首次有五条“未完成 realization 缺少剩余 limitation”错误；敏感性首次有一条资源身份被当作敏感内容的错误。两阶段均在 a002 通过结构校验，当前阶段状态为 complete。映射中仍有 27 条 retained_only、13 条 partial、9 条 expressed；这是对 49 项任务义务的表达分类，不是 49 项任务执行完成证明。 |

processing 最终保留 **484 条 modeled、4 条源文 unmodeled，以及 1 条程序校验隔离**，覆盖所选 489 个 IR 的记录状态。保留产物只排除了无效 `ir_001`，没有用空操作代替它，也没有让一个局部错误废弃所有其他记录。这个数是**生成和保留记录数**，不是传播成功数。[a002 保留审计](processing-a002-retention-audit.zh.md)、[实际 processing 结果](../../../experiments/doe/runs/document-guided-ga4-runtime-locality-high-20261117-205158/steps/processing/result.json)

## 字段级必要性仍须等待哪些证据

当前源文审查收到 **528 项义务、1,735 个范围**，其中有 89 项 compute 契约。现有 compute 规则均使用整体输出选择器；在标量输出上可以合理，但不能自动当作复合输出任意子字段的精确依赖规则。任务对应已包含字段路径需求，因此审查仍需检查“所需输出字段 → 必需输入字段”的精度、充分性和必要性，不能把整体输入并集直接称为字段级核验成功。获取端没有声明 projection 能力，也不等于已证明接口不支持裁剪。[审查材料核对](source-review-input-v12-audit.zh.md)

快照中 `review` 仍为 `running`，尚无已选最终 annotation，也没有本说明可据以报告的最终传播、输入删除或 DOE 结果。下一步应依据实际审查及后续执行，分别判断哪些表示错误获得修正、哪些源文缺口成立，以及错误是否沿实际依赖局部阻断。本说明不预先归因模型输出预算、宣布运行时已完整覆盖任意 Skill，或提出自动放宽校验、增加调用和再跑一轮。
