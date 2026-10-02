# SkillFlow Sink 标注收紧与可选参数

本轮收紧的是三个独立问题：**网络分类需要通信机制依据；可选参数保留原字段与出现条件；完整 JSON 输出仍接受严格校验。** Data 的类型和四个外层字段不变，不新增 DOE 判断、模型角色或传播期间模型调用。

## 1. 已有字段足以区分网络与工具交付

`deliver` 描述“数据交给谁”，`net_send` 描述有依据的网络效果，`sink_type` 是程序根据真实操作和位置属性生成的审计分类。这三个概念不合并。

| 已有事实 | 声明与编译结果 |
|---|---|
| 源文、代码或接口规定网络传输 | remote 边界及对应 net_send／net_receive；交付形成 network_send |
| 已知工具调用，部署未说明 | tool / recipient / null；无标签 deliver／receive，交付形成 external_tool |
| 明确本地、任务内部的机制 | tool / task 及有依据的留存属性；等级 0 交付仍参与传播，不收集为 DOE sink |

工具名称、发送动词、接收对象和主体标签不能单独证明网络。默认外部接收可能性也不能写成已测得的网络执行。等级仍由已有 access_scope／retention 规则计算，不由模型自由打分。一次交付不会同时复制为 network_send 与 external_tool。

## 2. 可选字段的条件只属于构造操作

```text
BuildOp
├─ container                       object 或 list
├─ parts[]
│  └─ BuildMember
│     ├─ path                      明确字段路径
│     ├─ value                     原字段值的 ValueRef
│     └─ when                      可选 Boolean ValueRef；省略或 null 表示无条件
└─ output                          当前 IR 的局部结果名
```

`update_fields` 继续使用原来的无条件更新成员类型。可选条件仅支持对象的字符串字段路径，不支持列表下标、任意条件表达式或 Data 条件体系。

下面只示意业务参数，正式规格仍需真实 evidences：

```json
{
  "op": "build",
  "container": "object",
  "parts": [
    {"path": ["query"], "value": {"kind": "local", "name": "term"}},
    {"path": ["cutoff"], "value": {"kind": "local", "name": "cutoff_value"},
     "when": {"kind": "local", "name": "has_cutoff"}}
  ],
  "output": "request"
}
```

`has_cutoff` 决定 cutoff 是否出现，不是 cutoff 的原值，不自动成为请求成员。true 加入原值；false 完全省略该成员，也不解析或消费其值；抽象布尔保留出现与省略两种候选。相同符号条件控制的多个成员共用一次决定，不产生一个出现、另一个省略的伪组合。明确的数字、字符串、null 等非布尔值不能通过隐式真假转换。

如果 true 仍可能发生但原值没有候选，记录绑定问题，不能只保留省略分支。请求形状与实际有序输入参与结果身份，同一静态组合重算复用身份。候选超过既有 100,000 上限明确失败，不截断。

## 3. 条件消费、观察和请求绑定一致

程序使用同一值消费结构区分 control 与 value，并将成员的 when 传给生成的模型观察。控制本身需要参与模型处理时仍被观察；成员值只有可能消费时才被观察。条件为 false 且值不存在不会提前产生观察或绑定错误。先前对来源整体的观察不被后续字段省略撤销；条件观察不能吞掉后续无条件观察。

原始模型只填写 BuildMember.when，不填写 model_observe、DeliverOp.when、记录输入索引或第二份观察列表。这些都由编译器派生。理由、执行机制和引用是否语义正确仍须模型及助手复核；程序保证已声明关系的结构一致性。

```text
build(实际原字段 + 存在条件) → request
                                 ├─ deliver([request], tool_boundary)
                                 └─ receive(tool_boundary, [request]) → response
```

这是一份参数分析对象，不承诺工具采用 JSON 作为线上序列化格式。两项操作在同一 IR／逐元素作用域／边界内使用完全相同的有序请求引用。唯一匹配后，获取阶段复用交付的实际 Data 绑定，并保持交付先于获取。一个交付最多对应一个返回；歧义不按名称、最近位置或 FIFO 猜测。无请求的外部获取和明确零参数工具调用保持现有表示。

## 4. DOE 主文件的实际增量

不增加新的顶层业务区或证据链。locations 的访问／留存属性和 sink_boundaries 继续使用上一轮结构。Data 内容仍仅在 data 数组保存一份。

```text
build 的原子操作记录
├─ inputs[]                         实际值／控制候选，保留参数顺序
├─ outputs[]                        构造出的请求候选
└─ members[]
   ├─ path                          请求字段路径
   ├─ value_input_index             引用 inputs；确定省略时为 null
   └─ when_input_index              引用控制 inputs；无条件时为 null

程序生成的条件观察记录
└─ when_input_index                 指向控制 inputs，不属于观察载荷
```

记录索引不复制 Data ID，也不把控制输入误读为工具请求参数。sink 清单、报告和独立 DOE 校验共用载荷解析：确定不执行的条件观察不形成实际 sink，可能执行的观察保留。操作输入或依赖中有存在性旗标，不表示它明文出现在请求对象中。

每例报告按源文动作、数据内容和交付关系对照，不要求新旧 Data ID 相同。对照分别列出结构增量、类型／等级变化、原字段身份、出现条件、已保留观察和剩余问题。

## 5. 运行与版本

当前版本：联合标注 v10、标注运行 v11、运行时契约 v5、表示契约 v3、编译器 v4、传播记录 v9、DOE 输入 v7、传播运行 v10；审查运行 v4、一次修复运行 v3，审查结果仍为 v2，Data 仍为 v4。新入口拒绝旧格式，不迁移或重写历史响应。

新版三例实验复用冻结源文与 CFG，每例一次联合标注，随后离线编译、传播和零 API 重放。不重新建图、不开展真实自动修复、不质量择优。API JSON Output 与提示词唯一对象要求共同使用；多余括号、重复键、完整但非法对象和截断继续严格拒绝，不剪裁或接受部分内容。

规则权威来源为[统一运行时契约](../packages/skill-ir/src/skill_ir/runtime_contract.py)和[表示契约](../packages/skill-ir/src/skill_ir/representation_contract.py)。工程验收保证类型、引用、控制／载荷、编译与重放一致；实际网络分类、原字段关系和局部机制是否标对，以实测及助手复核为准。

可运行离线示例：`PYTHONPATH=packages/skill-ir/src python packages/skill-ir/examples/optional_request_demo.py`。它只构造人工分析记录并向标准输出打印 DOE JSON，没有模型、工具或真实 Skill 执行；其中存在旗标 false 时请求保留 query、完全省略 cutoff。
