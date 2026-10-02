# 013 / F01 来源范围、工具返回与模型观察：助手复核

**工程流程已完成，但本例尚未达到本轮核心语义目标。请求容器及其模型观察补齐了；环境来源却被标注模型无依据解释为“显式 key-only getter”，所以环境整体及其观察仍然缺失。** 工具返回已正确表达为新的工具来源，且请求参数与返回内容保持区别。另有普通 `return` 被确定为用户输出、明确 body 取值仍退化为不透明计算的问题需要保留。

本报告由助手对冻结原文、最终选图、原始标注依据及实际 Data/记录逐项检查形成，不是模型追加调用，不冒充人工确认。没有修改 CFG、模型响应、标注、传播事实或敏感性标签；下述建议不自动修复结果。这里判断的是记录是否符合源文及已声明分析假设，不判断 DOE、必要性或风险等级。

## 1. 审查对象与实际状态

- 原文：[冻结 SKILL.md](feedback/inputs/package/SKILL.md)，9 条流程要求，对应文件第 8–16 行。
- 最终图：[selected-analysis.json](selected-analysis.json)，本轮从源文重新提取的第 0 轮，核对状态 `audit_passed`，未进行语义修复或结构修复。
- 原始业务事实：[doe-input.json](propagation/doe-input.json)；可视化：[report.html](propagation/report.html)。
- 标注依据：[完整业务标注](propagation/audit/annotation.json)、[独立位置证据](propagation/audit/location-evidences.json)、[完整源文／CFG／执行规则](propagation/audit/material.json)。
- 标注状态 `complete`，传播状态 `complete`，26/26 条 IR 有记录，19 份 Data，程序输出 `unresolved=[]`、`diagnostics=[]`。
- 实际 1 次提取、1 次语义核对、1 次联合标注，共 3 次逻辑调用、3 次 HTTP 尝试；没有重试。请求模型为 `deepseek-v4-flash`，返回记录中的模型名为 `deepseek-flash`。

`complete` 表示记录契约、引文定位和求解完成；它没有证实模型理由正确。下述环境和用户输出问题都使用了真实引文，但从引文推出的解释没有充分依据。助手意见单独保存在本文件，不回写或伪装成模型原本报告的 `unresolved`。

## 2. 最重要的问题：环境整体仍未进入传播

原文第 8 行是 `read FAST_KEY from the environment`。新 CFG 的 `ir_003` 确实改好了来源入口：输入为 `context_key environment`，输出为 `result_002 / fast_key`。这比旧图直接从 `FAST_KEY` 入口开始更完整。

但联合标注在 `transfer_specs.ir_003.events[0].atomic_ops[0]` 中执行了：

```text
read runtime_context:environment.FAST_KEY → D009
output result_002 = D009
```

该操作证据引用 `src_003` 的真实原句，理由却写成 **“显式 key-only getter 读取 FAST_KEY 绑定。”** 独立位置表 `loc_fast_key` 的第二条依据还写 **“IR opcode 表明读取的是 FAST_KEY 而非整个环境。”** 原文没有给出 `getenv`、按键接口、凭据代理、模型不可见句柄或局部隔离实现；一个带目标字段名的 opcode 不能证明上述机制存在。

这直接违背当前 `wide-read-agent-v6` 的 EM01 和 EM03：自然语言要求从容器取得字段，不等于给出了仅获取该字段的机制；执行主体或 opcode 名称也不能证明模型不可见。

实际传播结果说明这不是显示层遗漏：

| 检查 | 实际结果 |
|---|---|
| `locations.loc_environment` | 有环境容器声明，关联 `ir_003.input[0]` |
| 对 `loc_environment` 的 `read` | 没有 |
| 初始或最终环境整体 Data | 没有 |
| D009 的获取来源 | `runtime_context:environment.FAST_KEY` |
| D009 的 `part_of / path` | 都是 `null` |
| `ir_003` 的效果 | 只有 `context_read` |
| 对环境整体或 D009 的模型观察 | 没有 |

仅声明了 `loc_environment`，不能认为已保留环境整体。种子建立本轮按实际使用的规格工作，不会因为有未使用的位置声明就自动补造内容；传播器忠实执行了错误收窄的标注。因此这个缺口归于**联合标注的语义推断**，不是传播器把已经存在的整体 Data 删除了。

建议的通用纠正关系是：在没有明确局部接口依据时，读取相关环境整体，按既定执行假设记录整体进入模型，再明确选择 `FAST_KEY` 作为 `result_002`。整体可保持未展开，不需编造其他密钥名称或环境文件路径。下游 fast 调用仍只接收选择后的密钥，archive 仍只接收 source_id；不能把修正观察范围变成发送整个环境。

## 3. 已经补齐的请求范围与工具新来源

请求一侧已形成正确的三阶段关系：

```text
ir_001 / 事件 1：context_read → D015（user_request 整体）
ir_001 / 事件 2：model_observe(D015)
ir_001 / 事件 3：select_part(D015, ["source_id"]) → D012
result_001 = D012
```

D015 是 `known_parts`，只识别出 `source_id → D012`，`parts_complete=false`；D012 的 `part_of=D015`、`path=["source_id"]`。未知剩余内容没有被当前已知字段清单替代。后续调用参数使用 D012，没有错误发送整个 D015。

工具获取也按新契约成立：

| 当前动作 | 实际请求参数 | 返回 Data | `acquired_from` | 后续模型观察 |
|---|---|---|---|---|
| `ir_007` 首次 fast.fetch | D012 source_id、D009 FAST_KEY | D003 | `tool:fast.fetch` | `ir_009` 观察完整 D003 |
| `ir_011` 重试 fast.fetch | D012 source_id、D009 FAST_KEY | D005 | `tool:fast.fetch` | `ir_013` 观察完整 D005 |
| `ir_015` archive.fetch | 只有 D012 source_id | D004 | `tool:archive.fetch` | `ir_017` 观察完整 D004 |

三次获取都使用无标签 `receive`，没有凭工具名称添加 `net_send/net_receive`。`receive.inputs` 保留请求参数位置；返回 Data 具有独立获取边界，同时保留对这些参数的 `possible` 依赖，没有把返回内容当成查询参数的纯计算结果。

`tool` 不等于“已证实本地”，空 effects 也不证明“没有外部通信”。原始依据明确写网络未建立，审计者应保留这层边界，不能反向用空标签证明没有网络发送。工具返回的模型观察实际放在紧接着的分类 IR 中，观察版本是完整响应，不是提取后的 body；本例没有在获取和观察之间插入清理步骤，因此整条路径没有漏掉这些响应的模型可见范围。

## 4. 两项仍需保留的精度／边界问题

### 4.1 明确 body 取值被记成了不透明 `compute`

原文第 13 行要求返回成功响应的 `body` 值且保持不变。CFG 中首次、重试与 archive 的 body 输出身份都对应正确响应；最终 `return` 也没有再变换这些输出。

但是 `ir_009`、`ir_013`、`ir_017` 的传播规格把 body 提取记成 `compute(inputs=[response], dependencies=[derived])`。相应 D008、D018、D014 都是新 `opaque`，没有指向响应的 `part_of/path=["body"]`。archive error D002 也采用不透明派生。理由写“提取 body/error”，却没有通过已有的字段选取结构记录这个关系。

这保留了“来源于哪一次响应”，但没有精确保留“就是该响应中的这个值”。后续分析无法仅依靠 Data 结构区分 body 与响应其他字段。对原文明示的 body，可使用已有 `select_part` 并复用部分身份；状态分类仍可保留 `compute`。对于 error，应按原文及实际图中已确定的错误值关系表达，不能凭名称编造未规定的复杂响应格式。旧版同样主要使用不透明计算，这一精度缺口没有在本轮解决。

### 4.2 普通 `return` 被无依据确定为用户边界

`ir_020/022/024/026` 都标成 `user_output`，目标为 `loc_user`，理由把“return body/error”解释成“提供给用户”。源文没有说明返回调用方还是最终用户，也没有 UI 展示或交互协议依据；EM06 明确规定普通 return 不能单独证明面向用户输出。

因此这里应保留返回值身份，但不能宣称用户接收边界已证实。旧版对四个 return 都保存了 effects 未决；本版把它们变成确定的用户输出且 `unresolved=[]`，**不能把未决从 4 减少到 0 视为改善**。这属于边界推断过强，会给后续接收方审计带来误判。

## 5. 原有流程关键语义没有被本轮修正破坏

按最终 CFG 逐边枚举得到 8 条结构路径。这里核对的是已记录的控制结构与原文条件，不求解自然语言条件，也不证明每条路径在真实运行中可执行。

| 路径条件 | fast 调用次数 | archive 次数 | 返回值 | 最后追加状态的 IR |
|---|---:|---:|---|---|
| 有 key，首次 fast 成功 | 1 | 0 | `result_006`，首次响应 body | `ir_019` |
| 有 key，首次 transient，重试成功 | 2 | 0 | `result_009`，重试响应 body | `ir_021` |
| 有 key，首次 transient，重试失败，archive 成功 | 2 | 1 | `result_012`，archive body | `ir_023` |
| 有 key，首次 transient，重试失败，archive 失败 | 2 | 1 | `result_013`，archive error | `ir_025` |
| 有 key，首次 non-transient，archive 成功 | 1 | 1 | `result_012` | `ir_023` |
| 有 key，首次 non-transient，archive 失败 | 1 | 1 | `result_013` | `ir_025` |
| 无 key，archive 成功 | 0 | 1 | `result_012` | `ir_023` |
| 无 key，archive 失败 | 0 | 1 | `result_013` | `ir_025` |

没有重试 archive 的回边；重试 fast 只从首次 transient 失败分支进入；成功出口直接追加状态并返回，没有后续 fetch。首次和重试响应分别是 D003、D005，其返回值没有互换。

四个追加动作的实际写入参数分别为 D010（首次状态）、D016（重试状态）、D001（archive 状态，成功／失败两条路径）。原有 status.txt 是 D007；追加后的 D006、D011、D017、D013 都保留“原文件 + 当次状态”的依赖关系。记录中的 `update=strong` 表示确定替换该位置绑定为**追加后的新文件版本**，不表示把文件内容覆盖成单条状态。

archive 的实际参数里没有 D009，状态追加参数也没有直接传入 D009。FAST_KEY 仍出现在部分入口状态或 fast 响应的 `possible` 依赖中，不能据此直接断言密钥明文被发往 archive 或写进诊断文件。反过来，图中的禁传声明也不是已经执行了清洗或隔离的证明。此处保留声明、实参和依赖三者的区别，没有为满足禁传约束补造保护动作。

## 6. 与旧 DOE 输入的对应比较

旧对照为 `doe-input-v1-20260924-193407/cases/013/propagation/doe-input.json`。两次源文摘要完全一致；图是本轮重新生成，IR 数及 ID 变化，因此下面按动作关系比较，不按旧编号强行对应。

| 关系 | 旧结果 | 本轮结果 | 助手判断 |
|---|---|---|---|
| 请求来源 | 独立 source_id 来源 | user_request 整体 → 模型观察 → source_id 部分 | 改善 |
| 环境入口 CFG | 直接 FAST_KEY | environment → fast_key 结果 | 第一阶段改善 |
| 环境实际传播 | 独立 FAST_KEY 来源 | 独立 environment.FAST_KEY 来源，无父容器、无观察 | 核心问题仍在 |
| 工具返回来源 | remote 获取，强赋网络标签 | tool 获取，保留实际请求及 possible 依赖 | 新表达生效，未声称网络已排除 |
| 工具响应观察 | 完整响应进入模型 | 完整响应在随后分类时进入模型 | 保留 |
| 成功 body／失败 error | 同一次响应的不透明派生 | 同一次响应的不透明派生 | 响应身份保留，明确字段关系仍不充分 |
| 最终接收方 | 4 项普通 return 未决 | 4 项确定 user_output | 推断过强，未决消失不是改进 |
| 重试、回退、追加和禁传实参 | 已有主流程 | 主流程仍成立 | 未发现被改坏 |

本例不能宣称“来源范围问题已全部修复”，也不应宣布“没有非必要敏感数据暴露”。下一轮最优先核实的是：模型为何把自然语言目标字段误当成显式局部接口证据；其次是普通返回接收方和明确字段选取。报告提出的是通用规则执行问题，不建议添加针对 FAST_KEY、environment 或某个 IR 编号的程序特判。

## 7. 复核身份与 Data 短名

本报告 D 编号与本例 HTML 的按真实 ID 排序编号一致，仅方便阅读，不替换业务 ID。全部敏感性标签及敏感性依据仍为空；助手没有向 Data 添加敏感判断。

- 源文摘要：`fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da`。
- 最终 CFG 摘要：`47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`。
- 本次审查原 DOE 文件字节 SHA-256：`acbe13dc289a2e8700c74fd6f78ad5e8986dfeec9c7b4a4d717cdc12a5d499c4`。
- 本报告只针对这些事实材料；报告渲染修复或独立离线恢复不构成新增模型实测，若业务材料逐字段一致则本复核结论不变。

| 短名 | 真实 Data ID |
|---|---|
| D001 | `data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411` |
| D002 | `data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f` |
| D003 | `data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551` |
| D004 | `data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927` |
| D005 | `data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296` |
| D006 | `data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c` |
| D007 | `data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7` |
| D008 | `data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d` |
| D009 | `data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971` |
| D010 | `data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d` |
| D011 | `data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e` |
| D012 | `data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe` |
| D013 | `data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a` |
| D014 | `data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83` |
| D015 | `data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61` |
| D016 | `data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b` |
| D017 | `data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9` |
| D018 | `data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99` |
| D019 | `data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e` |
