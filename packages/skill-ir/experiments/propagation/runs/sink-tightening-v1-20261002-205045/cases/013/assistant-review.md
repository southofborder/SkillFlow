# 013／F01：本轮助手复核

这是助手对已保存源文、CFG、原始标注、编译材料及 DOE 文件的只读复核，不是用户人工确认或实际 Agent 执行验证。未修改标注、图、传播事实或历史记录，也没有额外调用模型。

本轮得到合法标注并完成传播：26／26 条 IR 形成记录，动态诊断为空，20 份 Data，16 个 sink 模板位置。关键目标——来源整体、工具获取来源、字段原值、首次／重试身份及终态追加——均得到保留，本次未发现需要修复的实质标注关系问题。

上一轮 `sink-boundaries-v1-20261002-185934` 的 013 是完整响应格式失败，未形成合法传播或 DOE 文件。本轮是新的完整实验，不能把对照说成“上轮没有 sink”，也不能据两轮差异独立证明某条 Prompt 的因果效果。

## 1. 来源整体、取值与模型观察已分开

以下 D 编号仅用于本例报告，不是跨运行身份。

| 源文动作与记录位置 | 读取／观察的版本 | 最终取得的值 | 复核意见 |
|---|---|---|---|
| `ir_001` 从用户请求取得 source_id；`records.ir_001.events[0..2]` | 先读取 D003 请求整体，再观察 D003 | `select_part(D003,[source_id])→D014`，绑定 result_001 | 没有把 source_id 的需求误当成键限读取或只观察字段。 |
| `ir_003` 从环境取得 FAST_KEY；`records.ir_003.events[0..2]` | 先读取 D010 环境整体，再观察 D010 | `select_part(D010,[FAST_KEY])→D019`，绑定 result_002 | 环境整体不再被 FAST_KEY 叶子来源替代；没有编造环境文件或其他密钥名称。 |
| `ir_005` 检查凭据存在性；`records.ir_005.events[0..1]` | default 处理观察 D019 | `compute(D019)→D012`，绑定 result_003 | 存在性是派生布尔计算；未作为凭据原值或调用参数。 |

D003、D010 的 `parts_complete=false`。登记 source_id 或 FAST_KEY 只是细化整体描述，不将整体范围缩小为这两个已知字段。原始处理段引用 EM01、EM10，并使用 `default`，没有以“读某字段”推定显式 getter、本地隔离或凭据代理。

这些整体观察是统一运行时契约下保留的可能性，不是测得的运行事实。如果真实工具只回传目标字段，那属于需要明确实现机制支持的例外；本例源文未提供该机制。

## 2. 三次工具获取保留来源与实际请求

| 操作位置 | 实际交付参数 | 本次新取得的内容 | 后续观察 |
|---|---|---|---|
| `ir_007.events[0].atomic_ops[0..1]` 首次 fast.fetch | D014 source_id、D019 FAST_KEY | D008；`acquired_from=tool:fast.fetch`，origin.inputs 为同一有序参数 | `ir_007.events[1]` 观察 D008 |
| `ir_011.events[0].atomic_ops[0..1]` 重试 fast.fetch | D014 source_id、D019 FAST_KEY | D002；`acquired_from=tool:fast.fetch`，与首次响应保持不同身份 | `ir_011.events[1]` 观察 D002 |
| `ir_015.events[0].atomic_ops[0..1]` archive.fetch | 仅 D014 source_id | D017；`acquired_from=tool:archive.fetch`，origin.inputs 仅 source_id | `ir_015.events[1]` 观察 D017 |

三个接收操作均与此前交付使用相同的有序引用，传播结果也保留相同的实际输入 Data。响应没有被改成仅由请求参数产生的计算结果；请求可能影响响应的关系为 `possible`，不是“请求参数明文全部包含在响应中”。

工具部署未说明，原始位置依据引用 EM06、EM12、EM13，采用 `tool/recipient/null`。三次交付都形成 `external_tool`／2，没有无依据添加 net_send 或 net_receive。响应取得与参数交付是分开的操作，receive.inputs 没有被拿来代替请求交付。

本例没有可选参数，直接保留 source_id／FAST_KEY 的有序原值引用，不需要凭空构造请求对象或增加条件成员。

## 3. 原值返回、分类与终态追加未混淆

| 成功／失败出口 | 分类数据 | 明确字段数据 | CFG 普通返回身份 | 返回前追加 |
|---|---|---|---|---|
| 首次 fast.fetch 成功 | D009，由首次响应 D008 派生 | D015＝D008.body | `ir_020` 输入 result_006→D015 | `ir_019` 追加 D009 |
| fast.fetch 重试成功 | D013，由重试响应 D002 派生 | D007＝D002.body | `ir_022` 输入 result_009→D007 | `ir_021` 追加 D013 |
| archive.fetch 成功 | D011，由归档响应 D017 派生 | D006＝D017.body | `ir_024` 输入 result_012→D006 | `ir_023` 追加 D011 |
| archive.fetch 失败 | D011，由归档响应 D017 派生 | D018＝D017 的 error 部分 | `ir_026` 输入 result_013→D018 | `ir_025` 追加 D011 |

body 字段采用 `select_part`，而状态分类采用 `compute(derived)`，不再把两者合成一个不透明结果。首次、重试和归档返回对象及其 body 身份分开，没有用首次 body 替代重试成功的 body。

四个普通 return 均为 `events=[]、output_bindings=[]`。返回哪个值由 CFG 输入承载，没有虚构公开输出、调用者位置或 user_output。原图的控制边仍保留 FAST_KEY 在／不在、首次成功／瞬时失败／非瞬时失败、重试成功／失败及归档成功／失败条件；本轮未重新建图或修改这些条件。

四条终态写入均为 `write(mode=append)`，目标 `status.txt` 为 `task/persistent`，各形成 storage_write／1。sink 的本次载荷仅是相应状态数据；旧文件 D016 不作为本次追加参数再次交付。追加后的新文件 Data 保留旧文件与状态值的依赖，入口／出口状态未错误写成直接覆盖文件内容。

archive.fetch 的实际参数只有 source_id，状态写入也没有直接使用 FAST_KEY；没有补造脱敏动作来满足禁传声明。工具响应或派生状态的可能依赖仍保留，这不能解释为已经证明含有 FAST_KEY 明文，也不能据此宣布任何真实执行都满足禁传约束。

## 4. Sink 数量与正常保守边界

| 类型 | 等级 | 本轮模板位置数 |
|---|---:|---:|
| model_observe | 2 | 9 |
| external_tool | 2 | 3 |
| storage_write | 1 | 4 |
| 合计 | — | 16 |

9 个模型观察分别对应请求整体、环境整体、凭据存在性处理输入、3 次工具返回及3 次响应分类输入。同一响应在取得阶段和后续分类阶段被观察属于不同处理阶段；这些不是工作队列重复迭代追加的运行事件。

16 个位置也不是单次执行必然发生 16 次交付：控制分支仍在 CFG 中，传播采用 may 分析且不求解自然语言条件；一个真实终态只经过自己的追加与返回出口。源文未规定状态文本格式或物理响应序列化格式，当前使用逻辑 body／error 组成和 opaque 分类结果，不宣称具体哪些字段每次同时存在。文件追加成功、工具调用成功和实际模型可见范围也未经运行验证。

本例没有条件 build，因此 DOE 文件没有凭空增加 members 或 when_input_index。数据未自动生成敏感性标签、必要性或 DOE 结论。

材料链接：[本轮 DOE 原始事实](propagation/doe-input.json) · [本轮可视化报告](propagation/report.html) · [模型原始联合标注](annotation/audit/raw-annotation.json) · [编译位置映射](annotation/audit/compilation-map.json)。
