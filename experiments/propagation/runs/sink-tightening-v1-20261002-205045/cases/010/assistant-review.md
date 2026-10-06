# 010／Q04 助手复核：可选参数原值、出现条件与请求绑定已分开

本次标注和传播均为 `complete`，12 条真实 IR 全部形成记录，传播诊断为空。本例生成 12 个 sink：10 个模型观察、1 个外部工具交付、1 个持久文件写入；前 11 项等级为 2，文件写入等级为 1。

这份意见是助手对冻结源文、实际 CFG、原始标注、编译结果及 DOE 文件的静态复核，不是人工确认或动态执行验证。本次没有修改标注、图或 DOE 文件，没有补跑模型。

## 1. 上轮两项核心问题已得到实际修正

上轮将可选字段值与存在性旗标合成为 `compute → optional_search_args`；工具交付只使用 term 和该不透明结果，而 `receive.inputs` 又改用另一份五参数列表。新版实际使用以下关系：

```text
request.json 整体
├─ term 原字段 → result_002
├─ from_date 原字段 → result_003
├─ from_date 存在性布尔 → result_004
├─ limit 原字段 → result_005
└─ limit 存在性布尔 → result_006
                     ↓
build request
├─ query = term 原字段，无条件
├─ from_date = from_date 原字段，when = from_date_present
└─ limit = limit 原字段，when = limit_present
                     ↓
deliver([request], tool/index.search)
                     ↓
receive(tool/index.search, [同一个 request]) → response
```

| 检查项 | 实际材料 | 助手判断 |
|---|---|---|
| query 原值 | `ir_003` 用 `select_part(["term"])`；build 的 query 成员引用 `ir_007.input[1]` | 直接保留原字段身份，没有查询词改写、扩展或规范化 |
| from_date 原值 | `ir_004` 的字段选择与存在性计算分别输出；build 成员 `value=input[2]、when=input[3]` | 值与控制没有再合成为不透明参数 |
| limit 原值 | `ir_005` 的字段选择与存在性计算分别输出；build 成员 `value=input[4]、when=input[5]` | 值与控制分开，原值身份保持 |
| 缺失时省略 | build 的成员使用各自 when；实际求解得到四种完整请求形状 | 没有用 null、旗标或 opaque 占位代替被省略参数 |
| 旗标不成为请求字段 | 四份请求 Data 的完整组成只有 query、适用的 from_date／limit | 两个存在性 Data 不在请求的 `content.parts` 中 |
| 交付与获取一致 | 最终 `ir_007.events[4].atomic_ops[0].inputs` 与 `events[5].atomic_ops[0].inputs` 完全相同 | receive 复用了实际交付请求候选，未另列一份控制／参数混合列表 |

原始标注的定位为 `/transfer_specs/ir_007/events/0/events/0/atomic_ops/0`（build）、后续两个原始 null-effect 事件分别是 deliver 与 receive。所有关系引用同一个 local `request`。这里的请求对象是参数分析表示，不表示源文规定了 JSON 网络序列化。

## 2. DOE 新增信息可以直接审计

实际 build 位于 `/records/ir_007/events/3/atomic_ops/0`，`inputs` 的五个位置依次是：

```text
0：term 原字段
1：from_date 存在性控制
2：from_date 原字段
3：limit 存在性控制
4：limit 原字段
```

新增的 `members` 映射为：

| 字段 path | value_input_index | when_input_index |
|---|---:|---:|
| query | 0 | null |
| from_date | 2 | 1 |
| limit | 4 | 3 |

四种输出形状为 `{query}`、`{query,from_date}`、`{query,limit}`、`{query,from_date,limit}`。每个出现的成员都引用同一个对应原字段 Data；没有把两个存在性旗标作为业务字段传出。

这些是未知实际请求内容下的静态候选，不表示执行了四次搜索。本例只有一个外部工具交付操作和一个工具获取操作。相比上轮的 10 份 Data，新版有 22 份 Data，主要增加了四份请求形状、各自响应及其 total／items 部分。其用途是保持参数原值和请求—响应关系，不是新增业务动作。

请求 Data 的 `origin.inputs` 和依赖仍可能包含控制，因为控制影响请求形状。**依赖中出现控制不等于控制明文出现在请求中。** 下一阶段检查内容应同时阅读 `content.parts` 与成员映射，不能把整条来源依赖自动当成明文包含。

## 3. 观察、返回来源与保存边界保持正确

| 边界／版本 | 实际绑定 | 助手判断 |
|---|---|---|
| 来源整体 | `ir_001` 读取 `storage/request.json`；原整体保留未知剩余，term／from_date／limit 登记为其部分 | 没有改成三个没有父容器的独立来源 |
| 已有整体观察 | 读取后及后续字段处理阶段仍观察 request 整体 | 参数省略没有撤销此前整体观察 |
| 构造前的必要观察 | `ir_007.events[0]` 使用 term 与两个控制；events[1]／[2] 对应 from_date／limit 的条件观察 | 控制与成员值分开，成员观察沿用该成员自己的条件 |
| 条件观察载荷 | 两项条件观察的 `when_input_index=1`，其 inputs[0] 为字段值、inputs[1] 为控制 | 第二槽位是控制，不应被当成该观察的附加载荷；控制另在前一个必要观察中出现 |
| 工具接收 | `tool/index.search`、recipient/null、`external_tool` 等级 2 | 使用未说明部署的契约默认，没有 net_send 或 net_receive |
| 工具返回来源 | 四个响应候选均 `acquired_from="tool:index.search"`，各自 `origin.inputs` 只含一个实际交付的请求 Data | 获取来源与请求影响保持分开；响应没有退化为只由请求计算的新值 |
| 返回内容观察 | `ir_007.events[6]` 观察 events[5] 的四个响应候选 | 观察的是取得的响应版本，不是请求或控制旗标 |
| total 原字段 | `ir_009` 选择每个响应的 total；`ir_010` 只写 total 候选到 count.txt | 没有把整个响应写入文件；storage_write 等级 1 |
| items 原字段 | `ir_011` 选择每个响应的 items；CFG 的 `ir_012` 返回 result_009 | 保持原字段及普通返回身份，没有虚构用户输出或调用者位置 |

模型观察由当前 default 处理段及编译器产生，属于统一契约下的可能行为。它们不是实际发生的请求日志，也不证明工具或模型后台保存期限。sink 等级只描述边界访问／留存性质。

## 4. 剩余边界与结论

本次未发现会改变上述参数范围、原值身份、请求绑定或交互边界的新实质标注问题。上轮可选参数降精度和交付／获取列表不一致已在实际结果中修正。

保留下列可计算近似：两个存在性结果由 `compute` 表达且为 opaque，程序将其作为抽象布尔保留四种请求形状；本轮没有具体请求实例，不能断言哪种形状实际发生。不同请求对应的响应及字段分别保留，候选集合不表示它们同时出现。source 或依赖关系也不证明所有上游明文仍存在于结果。

相较上轮，sink 数从 10 增为 12，增量主要来自可选成员的两项独立条件观察。工具类型及等级保持 external_tool／2，文件保持 storage_write／1。没有新增网络断言，没有 index.delete，没有格式校验／归一化业务步骤。

本例 DOE 输入已经能区分原字段、控制、请求形状和返回获取来源。敏感性、必要性与 DOE 结论仍由下一阶段判断；本意见不将程序完成或助手未发现问题称为已证明语义正确。
