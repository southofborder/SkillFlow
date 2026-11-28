# 工单状态卡的带任务要求的标注 CFG

本例的目标是向共享看板发布一张工单状态卡。调用方提供工单编号 `ticket_id`、状态 `status` 和私人联系邮箱 `requester_email`。接口要求前两个字段，并向看板成员展示调用方传入的所有字段。源包指定的调用为 `status_board.publish(card=ticket)`。

本次线上审计选中了两个基本块、四条 IR。四条指令均完成前向传播，反向需求分析和 DOE 均已完成。下表中的模型观察遵循运行时契约，整份结果来自静态审计。[原始 Skill](../../../../examples/doe/ticket-status-card/SKILL.md) · [组会完整图](annotated-cfg-with-task-requirements.svg) · [逐条原始标注](annotations.html)

## 1. 指令与边

| 基本块 | 指令 | 输入端口 | 输出端口 | 语义 |
|---|---|---|---|---|
| `block_001` · entry | `ir_001 receive` | `input[0] = context_key(ticket)` | `output[0] = result_001`，语义名 `ticket_incoming` | 读取调用方给出的完整工单。 |
| `block_001` · entry | `ir_002 dispatch` | 无 | 无 | 无条件进入发布块。 |
| `block_002` · publish | `ir_003 call` | `input[0] = external_resource(status_board.publish)`，`input[1] = result_001` | 无 | 将整份工单作为参数 `card` 交给看板。工具无业务返回内容。 |
| `block_002` · publish | `ir_004 return` | 无 | 无 | 结束此次 Skill 调用。 |

- **控制边**为 `block_001 → block_002`，条件为空。块内依次执行表中指令。
- **数据依赖**为 `ir_001.output[0] → result_001 → ir_003.input[1]`。发布指令的第一个端口标识工具，第二个端口携带工单。进入发布操作后，`deliver.inputs[0]` 就是这份工单。

## 2. 语义与敏感标注

| IR | 源动作与原始处理标注的绑定 | 编译后实际记录的操作 |
|---|---|---|
| `ir_001` | `receive_ticket → segments[0].ops[0], output_bindings[0]`。读取 `ticket_context` 为局部值 `incoming_ticket`，将此值绑定到 `output[0]`。 | `e0:a0 read` 读取工单，`e1:a0 deliver` 按契约将读取的同一工单交付模型上下文。 |
| `ir_002` | `exit → terminator` | 执行无条件分派。 |
| `ir_003` | `publish_ticket → segments[0].ops[0], segments[0].ops[1]`。前者向 `status_board` 交付 `input[1]`，后者接收同一次调用的完成值 `publish_completion`。 | `e0:a0 deliver` 向工具交付工单，`e1:a0 receive` 记录该次调用完成，`e2:a0 deliver` 按契约将完成值交付模型上下文。 |
| `ir_004` | `exit → terminator` | 返回，无返回端口或后继。 |

`eN:aM` 表示该 IR 的前向执行记录中第 N 个事件里的第 M 个原子操作，索引从 0 开始。发布侧的 `deliver` 和 `receive` 属于同一次调用。

两项敏感声明都位于 `ir_001`。一项标记 `input[0].requester_email`，另一项标记局部读取值 `incoming_ticket.requester_email`。两者的路径都是 `["requester_email"]`，属性均为 `value`，标签均为 `private_contact_address`。它们共同指向源包第 8 行描述的私人联系邮箱，因此下文每个边界各有两项比较。

## 3. 任务绑定与反向需求

| 提取的任务要求（原文） | 绑定到 CFG 的位置 |
|---|---|
| **R1** · Show the supplied ticket's ticket ID and current status to board members. | `ir_003.input[1]`，即实际展示内容的来源。 |
| **R2** · Publish the card exactly once using status_board.publish. | `ir_003` 整条指令，绑定路径 `[]`。 |
| **R3** · Use the entire incoming ticket record as the card argument, preserving its ticket_id, status, and requester_email values. | `ir_001.output[0]` 与 `ir_003.input[1]`。任务提取把源包第 12–15 行指定的整条记录传参方式列为保持要求。 |

反向分析从发布操作 `op_ir_003:e0:a0` 的四个需求起点出发。

| 要求 | 需求目标 | 保持属性与路径 |
|---|---|---|
| R1 | `deliver.input[0]` | 保持 `value`，路径 `["ticket_id"]`。 |
| R1 | `deliver.input[0]` | 保持 `value`，路径 `["status"]`。 |
| R2 | `deliver.self` | 保持 `action`，即执行发布。 |
| R3 | `deliver.input[0]` | 保持 `value`，路径 `[]`，覆盖整条记录。 |

对 R2，求解器根据已复核的接口要求，将发布动作所需的 `ticket_id` 和 `status` 推导为输入需求，规则为 `reviewed_input_contract`。R2 另有一项任务级计数约束 `at_most(1 attempt)`，作用于相同发布操作，检查结果为 `satisfied`。发布动作必须执行和最多尝试一次共同表达了“恰好一次”。

沿 `result_001` 回溯到 `ir_001.output[0]` 时，R1 和 R2 需要编号、状态两个字段，R3 仍需要整条工单。因此邮箱在接口上可省略，但在本轮自动提取的任务基准下被要求保留。

## 4. 数据版本与边界结论

三个比较位置涉及两个数据版本。

- **工单版本** `data_581b7cb76554df670f5a32a6b4f30b5dabb118a6dd3540821bbdbd0bf1b8f29d`。从 `runtime_context:ticket` 读入，在 `ir_001` 被模型观察，又在 `ir_003` 原样交给看板。
- **调用完成值版本** `data_7bd2b9f68e297dd785aa08935cd61ad02a8f37fcba46a2d777a95bdb9d99fdad`。由 `ir_003:e1:a0` 产生，供默认模型观察。接口声明工具不返回业务内容。

| 实际比较位置 | 接收方与数据 | DOE 结论 |
|---|---|---|
| `op_ir_001:e1:a0` | 模型上下文，工单版本的 `requester_email`，直接关系 | 2 × `no_excess_established`。整条记录的保留需求覆盖邮箱。 |
| `op_ir_003:e0:a0` | `status_board.publish`，同一工单版本的 `requester_email`，直接关系 | 2 × `no_excess_established`。邮箱确实到达共享看板，R3 使分析无法为此边界给出删减建议。 |
| `op_ir_003:e2:a0` | 模型上下文，调用完成值的整体，路径 `[]`，与原敏感数据为可能关系 | 2 × `possible_excess`。该记录没有证明完成值实际包含邮箱原值。 |

三个边界共六项比较，均未生成删减建议。[完整需求与比较证据](annotations.html) · [原始 DOE 结果](../../../../experiments/doe/runs/document-guided-ticket-status-card-high-20261125-220629/doe/doe-result.json)
