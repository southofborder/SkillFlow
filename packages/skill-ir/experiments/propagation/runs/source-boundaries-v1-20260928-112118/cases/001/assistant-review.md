# 001 / N01 助手复核：整体观察已补到，字段交付仍有精度损失

本文件是助手对已保存材料的复核，不是人工确认，不改写模型响应、核对结论或传播事实。审查对象为本次重新提取的第 2 次语义修复图，图摘要 `494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`；源文摘要 `6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab`。

**主要结论：本轮确实补上了整个 events.json 进入模型上下文的记录。但逐记录的 summary 原值与 recipient 关联没有形成细粒度 Data 关系，仍被不透明计算和符号边界概括；不能把本轮称为整体准确性已经提升并验收。**

## 1. 执行结果与提交状态

| 项目 | 实际结果 |
|---|---|
| 建图与语义反馈 | 第 0 轮 revise，第 1 轮 revise，第 2 轮 audit_passed |
| 反馈调用 | 4 次提取、3 个语义核对逻辑单元；1 次结构修复、2 次语义修复 |
| 唯一联合标注 | complete；1 次逻辑调用，1 次 HTTP 尝试；模型未填写 unresolved |
| 传播计算 | 独立读取的 DOE 文件为 complete，4 份 Data，10/10 条 IR 有记录，无动态诊断 |
| 原传播运行提交 | **未提交**：报告渲染在处理 literal 的 `identifier=null` 时发生 TypeError，原目录没有 manifest.json |
| 总调用 | 8 个计划内逻辑调用；9 次 HTTP 尝试，其中 1 次为传输重试；没有质量补跑标注 |

原始 [doe-input.json](propagation/doe-input.json) 通过独立业务结构校验，这不等于原传播运行完整加载通过。报告保存错误和未提交状态必须保留；后续若按离线恢复工具另建修复后传播运行，应查看 `offline-recovery` 的新清单与回执，不能回填原目录的成功身份。

请求模型名是 `deepseek-v4-flash`；本例实际记录的返回名是 `deepseek-flash`，不据此自行证明服务别名关系。原始调用和用量见 [反馈结果](feedback/result.json) 与 [联合标注结果](annotation/result.json)。

## 2. 按五个问题看当前记录

下面 E、S、P、C 只是本报告的阅读简称，真实 ID 不改写：

| 简称 | 实际 Data ID | 目前表达的关系 |
|---|---|---|
| E | `data_8b7068d560cdbe2f08e34d69a05ffb064e41c2ec0049ad88b4b54cc730f7de7a` | 来源 `storage:用户提供的 events.json`，整个内容为 opaque |
| S | `data_4dc4fd4f8f21d1cd82389aacb344828f1528dfcb596cebac38ef90787aa2275b` | 从 E 派生的 opaque 选中记录 |
| P | `data_4c1deeb27379880d1e4c1acae0211535d72ca2ff98e633f5150f0f8691cff75a` | 从选中记录派生的 opaque 载荷；规格理由称为逐记录 summary 原值 |
| C | `data_daa6710664ccff46b5be2e463aaff9746830ef51d2c19cb6d70e5d08c69a0bc7` | 从选中记录派生的 opaque 处理条数 |

```text
来源与读取
  用户提供的 events.json → read → E（整个来源，未按字段收窄）

模型观察
  E → model_observe → agent_llm_context

选中与取值
  E → compute(derived) → S
  S → compute(derived) → P
  S → compute(derived) → C

交付
  P → net_send → symbolic:notify.send.recipient
  C → fs_write(replace) → count.txt
```

1. **来源是什么？** `ir_001` 仍是外部文件读取，没有改成请求上下文或工具网络响应。源文件的“用户提供”文字进入了资源标识，位置是具体 storage 身份；文件内容未知没有被误写成未知地址。
2. **读取范围是什么？** `read` 取得 E 整体，没有只读 recipient/summary，也没有编造排除 access_token 的处理。源文列出字段不代表传播已实例化实际记录；保留 opaque 整体在本阶段合法。
3. **模型观察哪个版本？** `ir_001` 的第二个事件将同一 E 交付模型上下文，依据为固定执行规则 EM03。这修复了上一轮完全没有 model_observe 的主要覆盖缺口。它是公开静态执行假设，不是真实运行轨迹的观测。
4. **最终取出什么？** 模型理由说 S 经筛选、P 为 summary 原值，但两项都用 compute + derived + opaque。程序没有记录 P 是 S 中某记录 summary 的同值部分，也没有字段选择路径。该关系不能仅由局部名称或解释理由升级为已经验证的精确取值。
5. **实际传给谁？** 原子记录只交付 P，没有把 E 或 S 直接作为外发载荷；接收方用 `symbolic:notify.send.recipient` 表示动态远端边界。实际 recipient 字段没有单独解析成 Data，也没有保存“该记录的 recipient 与该记录的 summary”配对关系。

## 3. 影响后续 DOE 的保留问题

**字段交付精度发生退化。** 最终 CFG 用一个整批 `selected_records` 输入和 `per_record` metadata 概括逐条发送。联合标注再把“逐条取得 summary”表达成不透明计算，而不是同值部分引用。Data 中只剩 S 对 E、P 对 S 的派生关系。这既不能证明 access_token 已被发送，也不能据此证明载荷严格只保留 summary。后续 DOE 若粗暴沿所有来源依赖回溯，可能把不透明派生当作明文包含而误报；若完全信任理由中的“summary 原值”，又会绕过当前机器可分析事实。

此问题来自集合／逐记录取值的规格表达与实际标注选择，不应仅按案例字段名补一条规则。现有文件依然保留完整源文、CFG 约束和审计理由，方便定位缺口，但这些信息没有自动变成更精确的传播内容关系。助手不修改模型原来的 `unresolved=[]`，此处另行记录方法局限。

**整体观察与外发是两个边界。** E 整体进入模型意味着应保留其中 access_token 被模型接触的可能性；这不等于该字段经 notify.send 发给 recipient。源文的禁传声明仍保留，但没有被伪造为一次清洗操作，也不是程序已经证明的运行保证。

**筛选条件仍主要保存在 CFG 约束中。** opted_out、urgent、value 规则没有消失，程序没有求解这些自然语言条件。S 是筛选动作的派生结果，不是已验证的实际样本集合。静态事件也不等于实际通知次数。

## 4. 反馈修复中不能忽略的两点

| 轮次 | 核对器判断 | 助手复核 |
|---|---|---|
| 第 0 轮 finding_6 | 全部 event_records 计数被判为错转，要求改成 selected_records 计数 | 原文仅说“处理条数”，没有明确界定为选中数或发送数。所有经过检查的记录也可能被称为处理过。这里是解释收窄，可能误修；不能将后续通过当作旧图错误的证明。 |
| 第 1 轮 finding_3 | “用户提供”只在块名称出现，判为来源遗漏 | 同一表示在第 0 轮 finding_2 被接受。核对器跨轮采用的标准不一致。第 2 轮把信息写进输入资源标识更明确，但不消除此前核对不稳定。 |

最终图仍使用文件来源，没有为了满足反馈把文件误改成 context_key。第 2 轮另外增加了 recipient、summary 字段名的 literal 输入；它们是字段名称，不是实际接收对象和正文。联合标注没有把这两个字面字符串直接发送出去，这一点正确。

## 5. 与旧结果的对照及审查结论

旧三例运行 `doe-input-v1-20260924-193407` 中，001 没有模型观察事件，逐记录 recipient/summary 则有显式部分关系。本轮新增整体文件观察，但重建图从逐记录表示变为整批动作后，字段交付退化为 opaque 派生。两次结果的图不同，不能只凭 model_observe 增加就宣称所有精度都改善，更不能把改善全部归因于一处提示词。

当前可肯定的变化是**未收窄的文件来源进入模型观察记录**。仍需保留的主要问题是**集合内字段原值与接收方配对表达不足、处理条数的解释歧义，以及核对器跨轮标准不一致**。模型标注 complete、核对器 audit_passed 和独立传播事实 complete，均不消除这些问题；原报告保存失败也单独保留为工程状态。

材料入口：[冻结源文](source/inputs/package/SKILL.md)、[实际选图](selected-analysis.json)、[逐轮反馈](feedback/report.md)、[联合规格](annotation/transfer-specs.json)、[未提交的原始 DOE 事实](propagation/doe-input.json)、[报告保存错误](driver-error.json)。
