# 010-source：助手复核

本文件是助手对本次实际材料的复核，不是人工确认，也不替代原始模型响应。复核只读取现有初审、修复调用状态和诊断性传播结果，没有新增模型调用，没有修改候选或重放材料。

## 结论

**受控缺陷已被初审准确发现，但本轮没有完成修复。** 初审指出 `ir_007` 把工具获取结果写成仅依赖请求参数的 `compute`，丢失了工具返回的获取来源，并使该阶段的模型观察绑定到了请求参数。随后的一次完整修复遭遇流式传输中断，没有获得可接受的完整新标注，因此没有启动独立复审。

当前选中材料仍是 `original`，即带有该受控缺陷的实验候选。其传播状态为 `complete`，仅表示程序按这份候选完成了求解；**不能将该 DOE 文件视为修复成功的结果。**

| 项目 | 实际结果 |
|---|---|
| 初审 | `completed`，1 项实质问题 |
| 修复 | `execution_error`，`IncompleteRead(0 bytes read)` |
| 独立复审 | 未启动 |
| 最后选中候选 | `original` |
| 逻辑调用 | 2 次：初审 1 次、修复 1 次 |
| HTTP 尝试／重试 | 2 次尝试，0 次重试 |
| 诊断性传播 | `complete`，12/12 条 IR 有记录，无求解诊断 |
| 已保存离线重放 | `matched`，0 次模型调用，差异为空 |

## 初审为什么成立

源文 `src_008` 要求调用 `index.search`，CFG `g_0023` 将其输出标为 `index.search response`。这支持“取得工具响应”，并不支持“响应内容完全由查询参数计算而来”。运行时规则 EM09 明确要求保留获取边界、实际请求输入及可能依赖；在没有明确网络依据时，可以使用 `tool` 位置上的无标签 `receive`，无需猜测网络通信。

当前候选的 `ir_007` 却只记录了：

```text
compute(term, from_date, limit) → search_response
```

它没有以 `receive` 引用已有的 `loc_index_search` 工具边界。初审发现 `f-ir007-acquisition-as-compute` 引用 `ann_0165`、`ann_0046` 与 `obs_0005`，同时指出 profile 依据声称已经按 EM09 表达了获取，而实际传递规格没有该关系。这些定位与差异是一致的。

初审关于观察版本的判断也成立。当前 `default` 计算段使编译器观察计算输入，即请求参数；正确的工具获取段应在获取完成后观察其返回版本。这里应修正的是**获取阶段的来源关系与观察绑定**。不能把该问题夸大为“响应在全图中从未被观察”：后续处理仍可能观察这个被错误建成计算结果的值。

建议将该操作替换为工具边界上的 `receive`，保留原有请求参数次序和 `search_response` 局部输出，再由编译器重新生成获取后观察。无需额外添加网络标签、第二份响应或虚构公开输出。普通 `return` 的实际返回值仍由 CFG 承载；本次没有因空事件／空公开输出而误报返回遗漏。

这个案例验证了审查器命中当前受控缺陷，其中也包含 profile 与规格之间的内部矛盾线索；不能据此宣称对所有同步改写了说明与关系的错误候选都具有相同检出率。

## 修复失败属于执行问题

修复调用记录显示 HTTP 已返回 `200`，已取得实际模型名称 `deepseek-flash`，随后以 `IncompleteRead(0 bytes read)` 结束。请求模型为 `deepseek-v4-flash`，实际请求携带 JSON Output 和流式参数。没有完整接受的响应，也没有可进入解析、证据校验与编译的新候选；修复结果的校验状态为 `not_run`。

因此，该错误不说明修复模型已经提出错误修改，也不说明服务完全没有响应。异常文字中的 `0 bytes read` 不能解释为整次调用没有收到任何字节。本次只能确认响应传输未完整结束，修复内容不可作为完成结果采用。

本轮遵守一次修复上限和中断记录策略，没有自动重发这次请求，没有为获得成功结果而补跑，也没有伪造独立复审结论。

## 现有 DOE 文件仍保留原缺陷

已核对传播审计中的原始标注与 `refinement/inputs/candidate.json` 一致。下列 `Dxxx` 是报告展示别名，真实标识仍以 DOE 文件为准。

```text
ir_007 / 事件 0：model_observe
    使用 D001(term)、D008(from_date)、D005(limit)
    交付到模型上下文

ir_007 / 事件 1：无标签
    compute(D001, D008, D005) → D003(search_response)
    endpoints = []

D003.origin.acquired_from = null
D003.origin.inputs = [D001, D008, D005]
D003.origin.dependencies = 对三个输入的 possible 依赖
```

后续 `total`、`items` 仍能作为 D003 的组成部分被登记，这没有恢复已丢失的外部获取来源。`source` 等角色标签也不能代替实际的 `receive` 与获取边界。此处 `possible` 仅表示潜在影响，不表示查询参数全部明文包含在响应中。

已有重放回执与 DOE 摘要一致，说明这份**原候选诊断结果**可以重复求得，不证明原候选正确。下一轮若获授权继续修复，应保留本次失败记录，并作为显式的新执行处理；本文件没有启动该动作。

## 可直接核对的材料

- [初审问题与证据](refinement/initial-review/report.html)
- [本轮停止状态](refinement/result.json)
- [修复阶段报告](refinement/repair/report.md)
- [修复调用状态](refinement/repair/calls/annotation/a001/call.json)
- [修复传输状态](refinement/repair/calls/annotation/a001/transport.json)
- [原候选诊断性 DOE 输入](propagation/doe-input.json)
- [原候选诊断性传播页面](propagation/report.html)
- [已保存的零 API 重放回执](propagation/replay/summary.json)

本复核没有给出敏感性、必要性或 DOE 结论。
