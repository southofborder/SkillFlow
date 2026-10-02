# 001 / N01：助手复核

这是一份针对本轮实际材料的助手复核，不是人工确认，也不是 DOE 判断。标注记录完整，传播完成，10 条 IR 均形成记录；独立 DOE 加载和完整传播运行加载均通过。实际结果仍有一项需要保留的标注问题：**工具交付被无充分依据地确定为网络发送。**

复核材料为本目录的冻结源文与选定 CFG、[原始联合标注](annotation/audit/raw-annotation.json)、[编译结果](annotation/audit/compiled-response.json)及[实际 DOE 输入](propagation/doe-input.json)。没有修改这些材料，没有重新调用模型。

## 1. 需要修改：网络分类过强，但交付并未遗漏

具体位置：

- 原始标注 `profiles.ir_005.effects[1]` 为 `net_send`。
- 原始位置 `locations.loc_notify_send.kind` 为 `remote`，访问范围为 `recipient`，留存期限为 `null`。
- 原始规格 `transfer_specs.ir_005.events[0].body[0].events[1].atomic_ops[0]` 是向该位置交付两个参数。
- DOE sink 定位为 `ir_005 / event[0] / body_event[2] / op[0] / scope=element`，类型为 `network_send`，等级为 2。

原文只明确：

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

这段原文说明了工具调用、接收对象和交付关系，没有规定网络协议、远程部署或明确非本地通信。CFG 也没有增加这样的机制。标注中的理由“发送给 notify.send，构成对外发送的 net_send”把交付和网络通信合并判断了；位置理由也把外部接收边界直接称为 `remote`。

按本轮统一契约，在部署未说明时应保留 **`tool / recipient / null` 的可能外部接收**，使用无网络断言的工具交付；sink 类型应为 `external_tool`。只有进一步存在明确网络依据时，才使用 `net_send` 与 `network_send`。

这个修正不应删除交付、不应把工具降成任务内部，也不应改变当前参数绑定。固定等级 2 仍然合理：它说明另一接收主体的边界性质，不说明网络已经发生，也不说明最终风险。当前程序根据模型已经填写的 `remote/net_send` 一致地产生了 `network_send`；结构校验能够验证它们相容，不能证明网络推断有充分语义依据。

本轮按“不因质量补跑”的规则保留实际结果，未自动修复此项。

## 2. 范围、处理模式与模型观察

本轮没有重现“因为筛选或计数很容易本地实现，就直接判定本地隔离”的问题：

| 动作 | 原始处理模式及关系 | 实际编译与传播 |
| --- | --- | --- |
| `ir_001` 读取事件文件 | `default`，读取 `loc_events_json` 整体 | 先 `fs_read`，再记录整体的契约可能模型观察 |
| `ir_003` 筛选 | `default`，使用 `filter_items` | 先观察输入整体，再形成原集合的 `subset_view` |
| `ir_005` 准备并逐条交付字段 | `default`，单层 `for_each` | 先观察当前元素，再分别选取字段，再交付 |
| `ir_007` 计数 | `default`，`compute` + `derived` | 先观察选中集合，再计算计数结果 |

这些观察由编译器依据处理模式和统一契约生成，**不是实际运行日志**。原文没有明确隔离机制，因此按契约保留观察可能性，不因此中断传播。读取整体、观察整体与最终只交付两个字段在本轮结果中保持分开。

数据组成仍是开放描述：源集合及元素 `parts_complete=false`。后来登记 recipient 和 summary 没有把原集合缩小为这两个字段，也没有证明其他字段不存在。后续 DOE 阶段还需要结合完整源文识别敏感内容；当前敏感性标签和依据数组为空，不代表这些数据不敏感。

## 3. 字段原值与同一元素配对保持

`ir_003` 的筛选谓词保留 opted_out、urgent 与 value 的原文条件；它产生 `subset_view`，没有用不透明计算替代集合筛选。求解器不执行自然语言谓词，也没有宣称某一真实记录一定被选中。

`ir_005` 的 `for_each` 使用公开输入 1，也就是选中集合。两条 `select_part` 都从同一个局部元素 `record` 取值，分别使用路径 `["recipient"]` 与 `["summary"]`。实际记录的交付输入仍是两个有序参数：

```text
同一元素
├─ recipient 原字段 → 参数 0
└─ summary 原字段   → 参数 1
```

本轮没有将 body 改成整个元素，没有重新生成摘要，没有把两个独立候选集合做跨元素组合。Data 中 recipient 与 summary 的 `origin.path` 共享同一个抽象元素选择步，进一步保留了配对关系。

用于查看实际数据身份的短名只在本复核中使用，不改写原始 ID：

| 短名 | 实际 Data ID | 关系 |
| --- | --- | --- |
| 事件整体 | `data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a` | 来自 events.json，开放组成 |
| 选中集合 | `data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d` | 事件整体的子集视图 |
| 当前元素 | `data_8acb5cae833f9574e91c31ad2cbcfed377de7c74c758aed2715c7a7588dbbe63` | 同一逐元素作用域中的抽象成员 |
| 接收者 | `data_8e797e6d862284eab160a4f794cce400ff18776f3687dee8449c17010f22cdf4` | 当前元素 recipient 原字段 |
| 正文 | `data_759080b2119f28c08b35b09cc7a04c29f8905b313695499e65eeea5e26116042` | 当前元素 summary 原字段 |
| 计数 | `data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d` | 对选中集合的 derived 计算结果，内容仍 opaque |

## 4. 位置性质与 sink 纳入情况

当前 DOE 文件有 6 个 sink，全部对应已经形成的实际记录；没有为尚未求值的操作伪造数据绑定。

| IR / 记录位置 | 接收边界 | 当前类型 | 等级 | 绑定数据 |
| --- | --- | --- | --- | --- |
| `ir_001 / event[1] / op[0]` | 模型上下文，recipient/null | model_observe | 2 | 事件整体 |
| `ir_003 / event[0] / op[0]` | 模型上下文，recipient/null | model_observe | 2 | 事件整体 |
| `ir_005 / event[0] / body_event[0] / op[0]` | 模型上下文，recipient/null | model_observe | 2 | 当前元素 |
| `ir_005 / event[0] / body_event[2] / op[0]` | notify.send，recipient/null | network_send，分类依据不足 | 2 | 接收者、正文两个原字段 |
| `ir_007 / event[0] / op[0]` | 模型上下文，recipient/null | model_observe | 2 | 选中集合 |
| `ir_009 / event[0] / op[0]` | count.txt，task/persistent | storage_write | 1 | 计数 |

events.json 的声明是 task/persistent；它只是既有读取来源，没有因此新增保存 sink。count.txt 没有明确临时使用与清理机制，按普通文件默认 task/persistent 生成等级 1，符合本轮规则。模型边界由编译器生成 recipient/null，未推断后台日志或永久留存。普通 `return` 没有虚构用户输出或调用者位置；控制 IR 仍在覆盖表中。

## 5. 禁传、记录完整性与结论边界

CFG 保留“整份流程禁止将 access_token 字段发送给任何接收对象”及禁止摘要、改写的限制。实际 notify.send 参数只有 recipient 和 summary 原字段，标注没有为满足禁传限制补造字段删除、清洗或遮蔽操作。

模型观察当前元素仍保留元素的未知其余内容；本轮不能将原文禁传声明自动当作已经实施的模型隔离保证，也没有据此生成“没有暴露”的结论。禁传声明、契约可能观察与最终必要性／敏感性分析之间的关系应由下一阶段综合判断，不能由固定 sink 等级代替。

独立业务加载与完整运行加载均通过；DOE 状态为 `complete`，覆盖 10/10 条 IR，6 份 Data，动态 diagnostics 为空。实际标注只有 1 次逻辑调用、1 次 HTTP 尝试、0 次传输重试，请求模型为 `deepseek-v4-flash`，返回模型名为 `deepseek-flash`。

工程上，模式、观察编译、配对、数据绑定和 sink 清单彼此一致。方法上，本轮明确保留工具交付的网络分类过强问题；不能以传播完成或格式校验通过替代模型标注正确性的结论。
