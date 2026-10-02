# 013 / F01：本轮助手复核

本轮核心修改在 013 上得到实际体现：三个成功分支的 `body` 均使用 `select_part`，状态分类仍使用 `compute`；请求、环境整体与目标字段保持关联；三个工具调用分别取得自己的响应，并由程序生成相应的可能观察。**三个 body 原值关系缺口已经修复；archive 错误值却被具体化为 `["error"]` 字段路径，这一路径仍缺少明确依据，需要保留为标注审查问题。**以下是助手对保存材料的复核，不是独立模型审查，也不是人工确认或语义等价证明。

标注与传播状态均为 `complete`，覆盖 **26 / 26 条 IR、20 份 Data**，保存的 `unresolved` 与传播 `diagnostics` 均为空。13 个非空处理段全部采用 `default`，没有把“简单操作”或“本地文件目标”当成本地隔离机制。观察编译生成了 9 个 `model_observe` 阶段；该数量是静态阶段记录数，不是测得的模型请求次数。

材料入口：[完整源文](annotation/inputs/package/SKILL.md) · [冻结 CFG](selected-analysis.json) · [CFG 图及动作详情](cfg-review.md) · [传播审查页](propagation/report.html) · [DOE 输入](propagation/doe-input.json)

审计入口：[原始处理段](annotation/audit/raw-annotation.json) · [编译后规格](annotation/audit/compiled-response.json) · [编译映射](annotation/audit/compilation-map.json) · [标注结果与请求校验](annotation/result.json) · [本次调用](annotation/calls/annotation/a001/call.json)

## 1. 本轮已经核对成立的关系

### 来源整体、读取、观察与目标字段分开

| 位置 | 原始标注 | 编译及传播事实 | 复核结论 |
|---|---|---|---|
| `ir_001` | `default` 段：读取 `loc_user_request`，再 `select_part(["source_id"])` | 读取请求整体 D002；事件 1 观察 D002；选出的 D017 绑定 `result_001` | 没有把请求整体替换成独立的 source_id 来源 |
| `ir_003` | `default` 段：读取 `loc_environment`，再 `select_part(["FAST_KEY"])` | 读取环境整体 D004；事件 1 观察 D004；选出的 D009 绑定 `result_002` | 没有把环境整体缩成 FAST_KEY，也没有生成没有父容器的重复密钥来源 |

这里的 D 编号只是本次报告短名，完整 ID 见 DOE 和报告映射。请求与环境均为 `known_parts`、`parts_complete=false`，只登记原文明示的目标字段，未知剩余仍保留；没有编造其他密钥名称、文件路径或不相关来源。

可直接展开 [请求整体 D002](propagation/report.html#data-D002)、[环境整体 D004](propagation/report.html#data-D004)、[FAST_KEY 部分 D009](propagation/report.html#data-D009)。两个部分的 `origin.part_of / path` 均指向正确来源整体。

读取范围和模型观察属于统一抽象运行时契约的保守结果，不能据此宣称真实 Agent 必然把全部环境读入模型。源文没有提供明确局部 getter、本地隔离或凭据代理，本次采用 `default` 有据可循。

### 状态计算与 body 原值取得已区分

本轮原始规格在以下位置均写成“先计算分类，再取得已有字段”。原始路径为 `transfer_specs.<IR>.events[0].events[0].atomic_ops`；编译后前面增加观察阶段，因此在 DOE 中对应 `records.<IR>.events[1].atomic_ops`。

| 分类 IR | `atomic_ops[0]` | `atomic_ops[1]` | 公开结果与返回位置 |
|---|---|---|---|
| `ir_009`，首次 fast 响应 | `compute(response) → first_outcome` | `select_part(response,["body"]) → first_body` | `result_006` 是 D018 的 body 部分 D010；`ir_020` 返回它 |
| `ir_013`，重试 fast 响应 | `compute(response) → retry_outcome` | `select_part(response,["body"]) → retry_body` | `result_009` 是 D001 的 body 部分 D005；`ir_022` 返回它 |
| `ir_017`，archive 响应 | `compute(response) → archive_outcome` | `select_part(response,["body"]) → archive_body` | `result_012` 是 D006 的 body 部分 D015；`ir_024` 返回它 |

`ir_017.atomic_ops[2]` 另以 `select_part(response,["error"])` 表达 archive 错误，绑定 `result_013`，由 `ir_026` 返回 D012。这里的返回身份对应正确，但 `["error"]` 字面路径的依据不足，不能与三个 body 一起判为精确关系已验证，详见下节。三个 body 都有明确 `origin.part_of` 和 `path=["body"]`，没有被降为依赖响应的独立 opaque 计算结果。

body 自身的内容仍是 `opaque`，表示其具体内容未知；其**身份关系已经精确到父响应的 body 部分**。这与“compute 产生一个不透明派生值”有实质区别，不应仅看到 `opaque` 一词就判为仍未修复。

### 工具来源、参数和不同响应身份保持正确

| 调用位置 | 实际请求输入 | 获取来源 | 返回数据与程序观察 |
|---|---|---|---|
| `ir_007` 首次 fast | source_id D017、FAST_KEY D009，顺序保持 | `tool:fast.fetch` | 新响应 D018，事件 1 观察 D018 |
| `ir_011` 重试 fast | source_id D017、FAST_KEY D009，顺序保持 | `tool:fast.fetch` | 独立响应 D001，事件 1 观察 D001 |
| `ir_015` archive | 只有 source_id D017 | `tool:archive.fetch` | 独立响应 D006，事件 1 观察 D006 |

这三次 `receive` 均保留 `acquired_from`、实际请求输入和 `possible` 依赖。请求会影响响应，不被解释为响应完全由请求参数产生。首取与重试虽然使用同一工具和相同参数，仍有不同静态调用位置及响应 Data ID，后续 body 没有串用。

源文未明确网络实现，因而这里使用 `tool` 边界和无标签 `receive`，没有凭 `.fetch` 名称制造 `net_send/net_receive`。无标签获取后，编译器观察的是工具返回值，不是把请求参数冒充响应内容。

### 禁传与终态顺序没有被本轮修改破坏

- `archive.fetch` 的实际请求列表只有 source_id，没有 FAST_KEY，也没有整个 request/environment。
- `ir_019 / ir_021 / ir_023 / ir_025` 均为 `write(mode="append")`，当前追加参数分别是首次分类、重试分类、archive 分类、archive 分类；未把 FAST_KEY 或环境整体作为写入参数。
- 原 CFG 的四个终态块都先追加状态，再执行 `return`；本次没有改变 CFG 或新增获取步骤。
- `ir_020 / ir_022 / ir_024 / ir_026` 的实际输入结果分别是首次 body、重试 body、archive body、archive error。对应入口状态解析到的 Data 身份一致。
- 普通 `return` 没有被无依据扩大成 `user_output`，记录保留完整入口与出口，空 `events` 不表示可以忽略该终态。

## 2. 仍需标注审查的具体问题：错误值不必等于 error 字段

定位：原始 `transfer_specs.ir_017.events[0].events[0].atomic_ops[2]`；编译后及 DOE 的 `ir_017.events[1].atomic_ops[2]`。

原文是 `return its error`，而不是“返回响应对象的 error 字段”。当前 CFG 的输出语义标签为 `archive_fetch_error`，但这条 IR 的 constraints 为空、metadata 为空，也没有代码或接口结构给出字面键名 `error`。标注理由却写成“从失败响应中选出已有 error 字段并保持原值”。真实引文能支持“需要返回该错误”，不能单独证明响应使用这个具体字段。

因此，本次发现的是**可能将语义对象过度具体化为字段路径**，不是已证实真实返回值错误。路径必须另有源文、代码、接口或实际图的明确结构依据，不能只从输出标签推导。这正好说明操作选择规则需要双向约束：明确字段不得退化成 compute；没有明确字段时，也不能为了使用 select_part 而猜路径。

建议后续聚焦审查将这一个位置列为需纠正或说明的项目，要求区分“响应携带的错误值”和“键名恰好为 error”。本轮保留原始输出，未自动修改 Data、回退成 compute 或改写结果状态。

## 3. 契约补充和保守范围

本次标注没有原始 `model_observe` 效果。观察均来自编译器：请求／环境获取后观察整体，工具获取后观察对应返回值，存在性与结果分类处理前观察实际输入。编译映射中这些条目的 `kind="observation"`、`mode="default"` 清楚区分了程序生成与模型原始操作。

同一个响应可能在获取阶段和后续分类阶段各有一条观察记录。这是跨阶段保留，不表示已测得发生两次 LLM API 调用，也不应按阶段数量直接计算泄露次数。

源文只说本地 `status.txt`，没有说状态追加的处理过程与模型隔离。此次这四个段仍采用 `default`，没有把存储目标的本地性偷换为处理隔离。编译器按现有规则执行文件写入，不因此新增一份凭空的模型观察承诺。

## 4. 仍未证明、但没有隐藏掉的边界

1. **禁传要求的运行保证未证明。**本次确实未将密钥直接绑定到 archive 请求或诊断追加参数；但响应内容、分类实现和实际文件写入未经执行。fast 响应仍保留请求参数的 `possible` 依赖；分类结果再依赖响应。这不等于状态里包含密钥明文，也不能据此证明完全不受密钥影响。后续 DOE 不能把粗粒度依赖当成明文包含，也不能把约束声明当成自动清洗。
2. **路径条件没有被求解。**CFG 保留密钥存在、首次瞬态失败、重试成功、archive 失败等条件，传播按 may 分析合并候选。archive 入口可能保留先前 fast 的结果绑定，不代表某条真实路径一定执行过 fast；也不代表这些旧值被当作 archive 参数。
3. **字段的出现条件没有做路径特化。**archive 响应的 body 与 error 都是已识别的可能部分，`parts_complete=false`。它们不会因此被宣称每次同时存在；实际选择哪个返回值仍由 CFG 终态及条件决定。
4. **模型判断未由本轮工程校验证明。**所有处理段采用 default 与当前源文一致，但本轮只是一份三例实验中的助手复核，没有独立标注审查模型，也不能外推成所有 Skill 都会正确选择处理模式。

## 5. 执行与复核记录

本例只有 **1 次逻辑模型调用、1 次 HTTP 尝试**，请求 `deepseek-v4-flash`，返回名称记录为 `deepseek-flash`。实际请求参数包含 `response_format={"type":"json_object"}`，与冻结配置一致；本次响应通过严格 JSON、结构、覆盖、引文和请求身份校验。已知用量为输入 19,602、输出 51,663、合计 71,265 tokens。

助手使用零 API 的完整运行加载，重新编译已保存原始规格并逐项比较编译结果／映射；另检查了来源父子关系、9 个观察绑定、三个响应身份、四个返回结果、四个追加参数。上述程序比较成立，但不能补足 error 字段路径的语义依据。批次正式重放已匹配，见 [传播重放摘要](propagation/replay/summary.json)。

本次只新增此复核文档，没有修补模型响应、修改原 CFG、修改 Data 或补跑选优。结论是：**013 上一轮的 body 原值关系缺口已在本次实际输出中修复，来源范围与观察改善保住了；error 字段路径的具体化仍需审查，契约推断和 may 传播也不能直接视为实际执行。**
