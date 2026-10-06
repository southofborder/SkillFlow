# c02 的独立助手方法复核

**助手静态复核；非用户人工确认，非模型自评，非语义等价证明。** 依据完整冻结源文、当前实际 CFG、已接受且通过程序校验的核对结果判断。不把部分 SSE 响应当作有效语义结论。

## 第 0 轮：密钥反例命中，反馈位置正确

- 图：`cases/c02/rounds/r000/cfg.json`，规范 SHA-256：`711db9aafc53a66091c5c1ab247863d1785d665ded8a93562a26147968700df1`。
- 核对记录：`cases/c02/rounds/r000/audit.json`，文件 SHA-256：`1b72bfcd9fab81feeaa4fbe77a219d81713de1231f908174ab0dc42fdee4f9f6`。
- 模型给出 1 个背景项、10 个业务项；业务项中 8 个 represented、1 个 unsupported_addition、1 个 internal_conflict，没有 unknown。停止决定为 `revise`。

**实际受控缺陷被命中，两个修改建议都准确定位到多余密钥输入，没有发现会驱动错误修复的额外误报。** 两项差异描述的是同一个注入缺陷的两个方面，应按“一个受控缺陷命中”记账，不能统计成独立发现了两个缺陷。

| 模型条目 | 原文与实际图证据 | 助手判断 |
| --- | --- | --- |
| `finding_6`，unsupported_addition | 源文第 12 行限定 archive 的唯一业务参数为 source_id，第 15 行禁止向 archive 或诊断输出传 FAST_KEY。当前 `/blocks/block_011/instructions/0/inputs/2` 明确为 `result_002/fast_key`；它对应 `/blocks/block_002/instructions/0/outputs/0` 从环境读取的 FAST_KEY。 | 命中真实额外密钥传入。模型区分了 `archive.fetch` 资源句柄与业务参数，没有把资源标识误报为第二个业务参数。 |
| `finding_7`，internal_conflict | `/constraints/0` 声明禁止传密钥，archive 操作级 `/blocks/block_011/instructions/0/constraints/1` 声明仅传 source_id，实际输入却包含同一个 `result_002`。 | 声明与实际操作输入的冲突成立；它是同一密钥缺陷的另一种描述，不是第二个独立缺陷。 |

两项建议的事实编号均为 `fact:/blocks/10/instructions/0/inputs/2`，程序映射均为 `/blocks/block_011/instructions/0/inputs/2`。实际位置存在且确实是密钥操作数。`finding_6` 直接要求删除这个密钥输入，保留 source_id 和资源定位符；`finding_7` 的“删除或修正”较宽，但随后明确只将 source_id 作为业务参数。未要求删除 fast 所需密钥，也未要求放宽源文禁传约束。

其余关键业务判断与先前独立基线复核一致：请求和环境来源、缺密钥绕过 fast、transient 首次失败才重试一次、三类 archive 入口、正确成功 body 身份、archive 失败返回错误、不再重试以及四类终态状态追加都仍然存在。额外密钥输入并没有被 `represented` 项掩盖；相关条目明确交叉引用 finding_6/7。

## 保留的一处说明文字定位错误

`finding_9.actual_representation` 写道：`block_010/instructions/0/constraints/2` 声明不重试 archive。该自然语言中的块 ID 不正确，真实位置应为 `/blocks/block_011/instructions/0/constraints/2`。模型引用的受控编号 `fact:/blocks/10/instructions/0/constraints/2` 和程序生成的图指针均正确；错误来自把受控文档的零基块序号 10 当成了原图块 ID 010。

因此这是一处**解释文字定位瑕疵**，不是关键密钥缺陷的误定位，也不改变 archive 失败终止要求的对应关系。该条目是 represented，没有生成定向反馈建议，本次修复不会使用这条错误的文字位置。报告仍应如实保留该问题，不能因为引用检查通过就声称模型全部解释可靠。

## 第 1 轮修复图：独立完整复核

本段在第 1 轮独立核对调用进行期间，直接阅读新图全部字段形成，**没有读取该轮模型核对结论**。

- 图：`cases/c02/rounds/r001/cfg.json`。
- 文件 SHA-256：`873aa7530d56365fba547a44713d6677911cff7971e34869347be7eabfb309f2`。
- 规范图 SHA-256：`771c3f7b3265b143a69d1f7589cfa20ce0d3aa102a2809375b0864f59f883f91`。
- 阅读范围仍为全部 14 个块、28 个操作、15 条控制边、全部操作数、三级约束与空 metadata。

**助手结论：图中原有额外密钥传入已删除，完整源文的 9 条关键要求仍有相应表达，未发现本次重新提取引入新的关键遗漏、错转或无依据操作。** 这是对当前图记录的独立审阅，不代表已经得到该轮核对器通过结果，也不证明实际运行无泄漏。

新图的块和指令顺序发生变化：transient 判定改为 `block_006`，重试改为 `block_007`，重试结果判定改为 `block_008`，首次成功终态改为 `block_009`。以下证据均按新图实际操作和引用重新定位。

| 冻结原文要求 | 第 1 轮新图实际证据 | 助手判断 |
| --- | --- | --- |
| 第 1 条：请求 source_id、环境 FAST_KEY | `block_001/ir_001` 和 `block_002/ir_003` 分别读取相应上下文键，产出 `result_001` 与 `result_002`；开放操作名仍标明 request/environment。 | 保留。 |
| 第 2 条：有 key 先 fast，无 key 直接 archive | `block_003` 消费 `result_002` 判断存在；`/edges/2` 进入首次 fast，`/edges/3` 直接到 archive。首次调用 `block_004/ir_007` 仍消费 `result_001` 和 `result_002`。 | 保留；修复没有误删 fast 所需密钥，也没有新增缺密钥时的 fast 调用。 |
| 第 3 条：首次 transient 失败才恰好重试一次 | `block_005` 先判断首次成功；其失败边进入新 `block_006`，`ir_011` 使用首次错误 `result_005`；transient 边进入唯一重试 `block_007/ir_013`。重试仍使用 `result_001`、`result_002`，并保留原次数约束。 | 保留；非 transient 不重试，无返回重试块的循环边。 |
| 第 4 条：非 transient 首次失败或任意重试失败后 archive | `/edges/8` 从 `block_006` 的 non-transient 分支进入 archive；`/edges/11` 从 `block_008` 的 retry failed 分支进入 archive。缺 key 的独立入口也仍存在。 | 保留；没有新增只接受某种重试失败的限制。 |
| 第 5 条：archive 最多一次，唯一业务参数 source_id | `block_011/ir_021` 仅有两个输入：工具资源 `archive.fetch` 和原始请求值 `result_001`。图中只有这一 archive 调用，无回边；操作约束保持。 | **目标缺陷已修复**；额外 `result_002` 输入消失，资源句柄与唯一业务参数均正确。 |
| 第 6 条：成功返回该次 body 原值，之后不 fetch | 首次成功到新 `block_009/ir_018` 返回首次输出 `result_004`；重试成功到 `block_010/ir_020` 返回重试输出 `result_008`；archive 成功到 `block_013/ir_026` 返回 `result_011`。对应终态没有出边，也没有包装、转换或新获取操作。 | 三种返回绑定均保留，没有将重试成功误绑到首次 body。 |
| 第 7 条：archive 失败停止、返回其 error、不重试 | `block_012` 使用 archive 输出 `result_012` 判断结果，失败边到 `block_014`；`ir_028` 直接返回同一错误 `result_012`，没有后继。 | 保留。 |
| 第 8 条：key 禁止传 archive 或诊断输出 | 新 `/constraints/1` 保留原文完整禁传声明；archive 无 key 输入；状态追加操作只有文件资源和状态字面值；没有额外诊断输出操作。 | 保留并消除了原声明—输入冲突；没有为消除冲突而删除或放宽约束。 |
| 第 9 条：全部终态返回前追加最终状态到本地 status.txt | 首次、重试、archive 成功与 archive 失败四个终态块分别为 `block_009`、`block_010`、`block_013`、`block_014`；各自第一条是真实追加操作，第二条为 return。新 `/constraints/2` 明确保留 local status.txt。 | 全部保留；不存在只改标题、仅补声明或把追加放到 return 后的情况。 |

新图还改变了一些 draft ID、语义标签和全局约束存储次序；这些变化没有替代实际结果引用。状态资源的 semantic_name 从 `local status.txt` 缩为 `status.txt`，但资源 identifier 未变，全局约束仍明确其 local 属性，本次不将这项标签精简视为关键语义丢失。所有脚本 metadata 仍为空；没有新增等待、脱敏、错误吞并、重复抓取或状态文件恢复操作。

## 最终模型状态与独立审阅对照

完成上述独立图审阅后，再查看第 1 轮有效核对记录及运行结果：

- `cases/c02/rounds/r001/audit.json` 文件 SHA-256：`f5ed4a1946531ebded6275e05939d0d294c138dc2a2cea2fbe3f628c296a2bc5`。
- 共 **10 个条目：1 个 context、9 个 semantic**；9 个业务项全部为 represented，没有明确差异或 unknown。
- 程序停止状态为 **`audit_passed`**。共执行 1 次语义修复、1 次提取调用与 2 次核对调用；结构修复 0 次；HTTP 尝试 3 次、重试 0 次；记录实际返回模型名为 `deepseek-flash`。
- 最终核对明确检查了 archive 只有 source_id、FAST_KEY 不进入 archive 或状态追加、三种 body 返回身份、archive 错误返回及四类终态状态追加，与此前独立图审阅一致。

在本例冻结源文与实际第 1 轮图的明确事实范围内，**未发现核对器假通过的迹象**：助手独立检查确认目标输入缺陷已消失，其余关键行为没有明显退化。这个结论不是对潜在工具内部副作用、实际运行无泄漏或其他 Skill 的核对可靠性保证；也没有消除第 0 轮解释文字中的定位瑕疵。方法结果可记为“一个受控缺陷经一次完整重新提取修复，核对器通过，助手独立复核未发现关键误改”。

另：c01 的本次在线响应发生不完整传输，没有有效核对结果，不能用其部分响应作方法判断；`source-baseline.md` 是此前直接阅读原图形成的独立助手意见，不代表 c01 在线核对器通过。
