# SkillFlow Sink 边界与固定分级

当前流程为：**完整 Skill 与既有 CFG → 一次联合标注 → 编译模型观察 → 程序生成 sink 类型和边界暴露等级 → 确定性传播**。本轮补齐接收方、共享范围和留存性质；DOE 的敏感性、必要性和综合判断由下一阶段完成。

模型识别边界语义并提供现有引文依据。程序根据类型、位置属性和实际传递操作生成清单与等级，保证它们一致；这不证明模型对位置属性的判断正确，也不证明行为已真实发生。规则权威来源是 [`runtime_contract.py`](../packages/skill-ir/src/skill_ir/runtime_contract.py)；固定分类和等级实现见 [`boundaries.py`](../packages/skill-ir/src/skill_ir/security_profile/boundaries.py)。

## 1. 模型声明与程序派生分开

```text
原始联合标注（一次模型调用）
├─ profiles[IR ID]
│  └─ operator / roles / effects / evidences   保持四字段
├─ locations[位置 ID]
│  ├─ kind                                    上下文、存储、模型、远端、工具或用户
│  ├─ name                                    稳定名称；与 kind 一起确定位置身份
│  ├─ operand_refs[]                          实际 IR 操作数关联，允许为空
│  ├─ access_scope                            task / recipient / shared / public
│  └─ retention                               task / persistent / null
├─ transfer_specs[IR ID]                       处理段、值关系、交付和写入
└─ location_evidences                         原有独立位置依据表

程序编译后的业务材料
├─ profiles / locations / transfer_specs
└─ sink_boundaries[]                          不由模型填写
   ├─ instruction_id                          属于哪个真实 IR
   ├─ event_index / op_index                  编译规格的事件、操作位置
   ├─ body_event_index / scope                单层 body 定位及固定 element；普通操作均为 null
   ├─ target                                 已声明位置 ID
   ├─ sink_type                              程序计算的边界类型
   └─ exposure_level                         程序计算的 1–3 级；0 级不进清单
```

`access_scope=task` 表示任务内部；`recipient` 表示另一个接收或处理主体；`shared` 表示跨主体共享；`public` 表示公开可读。位置类别本身不证明接收边界一定发生，仍须有实际交付或保存操作。

存储和上下文的 `retention` 必须非空：`task` 表示任务期限内，`persistent` 表示跨任务留存。模型、工具、远端和用户边界可以用 `null`，表示本分析没有建模其保存期限，不能据此断言接收方不保存内容。

原始模型响应不得包含 sink_boundaries、sink_type 或自由数字评分。编译后清单不重复保存 ValueRef、Data ID、参数或引文；已有操作负责保存具体值引用，位置依据仍旁置审计。

## 2. 默认和明确例外

| 位置 | 默认 | 明确例外与边界 |
|---|---|---|
| 工具 | recipient / null | 有依据的纯本地、任务内部工具可用 task；部署未说明按契约保留外部接收可能性，不补造 net_send |
| 运行时上下文 | task / task | 跨任务记忆使用 persistent；其他主体可读使用 shared 或 recipient；普通结果定义不自动成为上下文写入 |
| 文件／存储 | task / persistent | 有明确任务临时用途和清理机制时可用 task / task；名称含 temp 不构成充分例外 |
| 模型 | recipient / null | 已有观察仍属于处理主体边界；模型进程在本机不把观察降成普通内部赋值 |
| 远端、用户 | recipient / null | 有公开或共享依据时使用相应范围；不猜测后台日志、永久保存或执行成功 |

**网络机制与外部接收分开判断。** 网络通信须有源文、代码或接口支持的传输机制；工具名称、发送动词、接收对象或执行主体都不能单独证明网络。部署未说明的工具使用 tool/recipient/null，通过 external_tool 保留审计边界，而不是补造 net_send；明确网络交付仍只生成一次 network_send。

已有明确事实优先于默认。模型的理由须指出事实规定了什么访问或留存机制；默认规则引用对应 EM 编号并明确它是静态可能关系。内容尚未展开、部署未说明或后台留存未建模，不独自形成泛化未决。

普通上下文写入仍参与传播。task/task 的上下文保存不进入 DOE sink 清单；跨任务保存或扩大可读范围才进入。删除绑定不再次交付旧内容。

## 3. 固定等级和六种 sink

`exposure_level` 中文为**边界暴露等级**，只表示边界范围和留存程度。同一位置符合多项时取最高等级。

| 等级 | 固定条件 |
|---|---|
| 0 | 任务内部、任务期限内的流动或保存 |
| 1 | 任务内部持久留存 |
| 2 | 另一接收主体或跨主体共享 |
| 3 | 公开可读或公开发布 |

0 级没有独立 DOE sink；其数据关系和状态变化照常保留。级别不是数据敏感度、暴露必要性或最终风险：密钥写入私有文件与公开天气信息发送到远端，仍须在 DOE 阶段结合任务和内容判断。

| sink_type | 收集依据 |
|---|---|
| network_send | net_send 对应的实际交付 |
| storage_write | 非删除的存储写入，且等级大于 0 |
| context_save | 非删除的上下文写入，且等级大于 0 |
| model_observe | 编译后实际模型观察操作 |
| external_tool | tool 边界的实际交付，且等级大于 0；纯本地任务内调用通常为 task / null，等级 0 |
| user_output | 明确的用户交付 |

收集不依赖 profile.roles 中是否出现 sink。程序生成的观察不会机械修改执行主体或角色。相同 effect 的重复阶段、原数据与清理结果、逐元素作用域和重复参数保持各自身份。

## 4. 请求、响应、观察与保存

```text
请求内容进入模型          → model_observe：绑定实际请求版本
实际参数交付给工具        → deliver → tool：绑定具体参数
工具取得返回内容          → receive → tool：保留获取来源和请求依赖
返回内容进入模型          → 编译 model_observe：绑定返回版本
```

纯本地工具交付保留传播记录但不进入 sink 清单。已知工具交付而网络未确定时，允许 effect_index=null 的 deliver → tool；不能用 receive.inputs 代替交付，也不能将这种关系伪装为网络通信。明确网络请求使用 net_send，单个交付点不再生成等价的第二个工具 sink。

零参数工具交付可保留空 inputs。它表示没有已建模参数，不表示工具或返回内容不存在；内容未知仍使用合法的 opaque Data。其他已要求内容的交付保持非空参数校验。

覆盖和追加的 sink 绑定**本次实际写入参数**；原内容及保存后的版本继续在 changes 和 Data 关系中表达。delete 不生成内容保存 sink。普通 return 的身份从 CFG 输入读取，允许空 events 和 output_bindings，不虚构调用者位置、用户输出或公开结果。

## 5. 传播交付与审查

编译清单覆盖合法规格中的候选交互操作。传播后的 DOE 清单只引用实际形成记录的操作：逐元素清单保留 body 定位和同一元素作用域，参数 Data ID 从对应原子记录读取。尚未求值的部分由 status、coverage 和 diagnostics 标明，不凭空产生数据版本或空暴露结论。

主报告优先展示类型、等级、目标、对应数据版本及纳入／排除原因；证据在已有审计区展开。没有审计材料时也不得把静态可能行为写成执行日志。独立 DOE 加载验证清单与真实记录的坐标、目标、类型及等级；完整运行加载和离线重放再核验原始响应、编译来源和摘要。

当前版本为联合标注 v10、标注运行 v11、统一运行时 v5、表示契约 v3、处理编译器 v4、传播记录 v9、DOE 输入 v7、传播运行 v10；Data 保持 v4。新入口拒绝旧记录，不将默认补字段当作历史迁移。

离线验收覆盖：任务内部与外部工具、普通文件与有清理机制的临时文件、上下文共享及记忆、先观察后删减、请求与响应版本、重复阶段和逐元素配对、删除与追加、引文和属性冲突、程序派生清单篡改，以及零 API 重放。三例实测只复用冻结 Skill 与 CFG，逐例一次联合标注，不重新建图、不质量补跑，模型实际遵循情况另由助手复核报告。

可选参数只扩展构造操作与生成的观察，不增加边界字段或 Data 条件系统。具体说明及 DOE 新增字段见[Sink 标注收紧与可选参数](SkillFlow-Sink标注收紧与可选参数.md)。
