# 001 / N01 助手复核

本文件是助手对本次冻结材料的只读语义复核，不是用户人工确认，也不是动态执行结果。复核未调用模型、未执行 Skill、未修改 CFG、标注或传播材料。

## 结论

本例正确保留了 `events.json` 整体，并在筛选之前记录了对该整体的可能模型观察。标注明确引用统一抽象运行时契约 EM03，并写明“可能”“不是已观测事实”，没有将整体观察等同于整个文件作为通知参数发送。这符合本轮契约的主要目标。

仍有三类边界需要保留：通知动作的网络属性证据不足；筛选与计数的执行主体归属包含未经支持的本地实现推断；`recipient` 和 `summary` 被表达为不透明派生结果，尚不能从 Data 关系证明逐条字段原值及二者配对。最后一项是实际 DOE 精度缺口，不应因 `complete` 或 `unresolved=[]` 消失。

## 本次材料与工程状态

- 原文：[冻结 SKILL.md](annotation/inputs/package/SKILL.md)，第 8–16 行；源文单元 `src_003`。
- 图：[冻结 CFG](annotation/inputs/cfg.json)。图摘要 `494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`。
- 图来自已选定的既有反馈结果，选择记录为 revision 2 / `audit_passed`；本轮没有重新提取 CFG。这个历史状态不能证明本轮安全标注正确。
- 契约：`skillflow-abstract-runtime-v1`，摘要 `d11080a8cf7879c3a0d01d6bf9b403f8fb0ed4ef4d16d5ed49b88bd2333712c0`；全文在 [标注材料](annotation/inputs/material.json) 的 `/execution_model`。
- [标注结果](annotation/result.json)：`complete`，10 条 IR、10 份 profile、10 份传递规格、4 个位置、8 个原子操作；`unresolved=[]`，程序验证通过。
- [DOE 输入](propagation/doe-input.json)：`complete`，10 条 IR 均为 `processed`，7 份 Data，`diagnostics=[]`。这些是程序记录状态，不是语义保真或安全结论。

## 1. 整体读取与可能模型观察保留正确

原文第 8 行要求读取用户提供的 `events.json`，并列出记录内的七个字段，包括 `access_token`。没有规定只返回其中一个字段、先本地筛选后返回，或模型不可见的读取机制。

本次关系为：

```text
storage / 用户提供的 events.json
    → ir_001 / event 0 / read → E（整个来源，opaque）
    → ir_001 / event 1 / model_observe(E)
    → ir_003 / compute(E) → R（筛选后的记录，不透明派生）
```

E 的完整 ID 为 `data_c403550da08486fc2be861568d405988967cee23d801b11546d9481fd58414de`。来源没有被替换为 `summary` 或某个独立字段。模型观察与读取输出使用同一个 E；后续筛选没有回写或替换此前观察的数据版本。

证据定位：

- [profiles.json](annotation/profiles.json)：`/ir_001/effects` 为 `fs_read, model_observe`；`/ir_001/evidences/5` 引用 `execution_model / EM03`，理由为“合同默认下，读取返回的 event_records 无显式隔离，可能进入模型请求并被观察；不是已观测事实。”
- [transfer-specs.json](annotation/transfer-specs.json)：`/ir_001/events/0/atomic_ops/0` 读取 `loc_events_json`；`/ir_001/events/1/atomic_ops/0` 将同一局部值 `event_records_read` 交付到模型上下文。
- DOE：`/records/ir_001/events/0/atomic_ops/0/outputs/0` 与 `/records/ir_001/events/1/atomic_ops/0/inputs/0` 均绑定 E。

**助手判断：符合统一契约。**这里只能说契约下保留了整个来源可能进入模型的情况，不能说真实 Agent 已经读取或观察了所有字段，更不能说模型已经实际泄露 `access_token`。原文声明字段存在，但当前 Data 仍是 opaque，未展开字段，也未生成敏感性判断。

## 2. 观察整体没有被自动变成通知参数整体

`ir_005` 先得到两个独立的派生值，再将它们按两个参数位置交付：

```text
R + literal("recipient") → T
R + literal("summary")   → B
deliver([T, B], remote / notify.send)
```

T 为 `data_de27aab6c8c854489837ec39711e68c2d08434c3c8167ad85a1b48f7f2cf8801`，B 为 `data_69d4fe86b0d4046047111b5176fc614b8dd9be66a8c16e644da829b59379faf5`。交付输入没有直接绑定整个 E 或 R；也没有增加 `access_token` 参数，没有凭禁止条款生成清洗操作。

证据定位：原文第 11–15 行；CFG `/blocks/block_003/instructions/0` 的 constraints 与 `metadata.per_record / recipient_field / body_field`；规格 `/ir_005/events/0/atomic_ops/0..2`；DOE `/records/ir_005/events/0/atomic_ops/2/inputs`。

**助手判断：整体观察与后续参数范围保持分开，参数顺序保留。**但这还不能证明 B 就是原始 summary 的原值，也不能证明通知载荷必然不含其他字段，原因如下。

## 3. 明确字段与逐条配对仍未成为可计算的内容关系

筛选结果 R、通知接收参数 T、通知正文 B 都是 `content.form=opaque`，只有 `origin.inputs` 与 `derived` 依赖；没有 `part_of/path` 或其他明确内容组成关系。

R 的完整 ID 为 `data_ded05d5f83d8b70deeaf8a42b4fd4de48ffffec3dc2f8b47c395fabac3c839e7`。规格对 recipient/summary 使用 `compute`；字段名称只是实际输入中的字面值 Data，不是解释器能够执行的逐记录选取规则。因此传播器不能仅靠 `compute` 的中文理由恢复“每条记录的 summary 原值”，也不能恢复每份正文与同一条记录 recipient 的配对。

证据定位：规格 `/ir_003/events/0/atomic_ops/0`、`/ir_005/events/0/atomic_ops/0`、`/ir_005/events/0/atomic_ops/1`；DOE 中 R/T/B 对应 Data 的 `/content`、`/origin/part_of`、`/origin/path`、`/origin/dependencies`。

**助手判断：这是表示精度缺口，不是已证明的实际错误发送。**`derived` 表示派生关系，不能解释成输入全部明文仍在输出中；另一方面，“从 summary 派生”也不等于“证明仅包含 summary 原值”。现有批量 IR 和原子操作没有展开逐记录映射，本轮不能简单要求给所有记录使用一个固定 `select_part` 路径来假装解决。后续若要检查精确载荷及接收者配对，需要先处理这一通用表达能力，不能由 DOE 根据名字补造结构。

## 4. `net_send` / `remote` 的依据不足，不能作为已知网络事实

标注对 `ir_005` 使用 `net_send`，位置 `loc_notify_remote` 为 `remote / notify.send`。效果证据引用“调用一次 notify.send”，理由为“该 IR 调用外部通知工具发送内容，属于 net_send。”位置证据引用工具调用和 `recipient` 字段。

证据定位：profile `/ir_005/evidences/3`；[独立位置证据](annotation/audit/location-evidences.json) `/loc_notify_remote`；规格 `/ir_005/events/0/atomic_ops/2/target`；契约 EM06。

原文支持“向接收对象发送通知”，但没有提供协议、URL、工具实现或其他明确网络传输机制。`external_resource` 也不是网络证明。因此，这里把接收者边界进一步确定为远端网络边界的依据不充分。

**助手判断：相对于 EM06 的边界标准，这是标注证据不足。**不能由此断言真实 notify.send 一定是本地或没有网络，也不能删掉源文明示的发送行为。需要区分“发送存在”和“传输方式已知”；本例未在 `unresolved` 中反映该区别。

## 5. 不能从未提及 LLM 推导明确本地处理

`ir_003` 的 operator 证据理由为：“该 IR 执行条件筛选，未显示 LLM 或其他外部工具参与，由 agent_runtime 处理。”`ir_007` 也仅凭计数 opcode 称为“本地统计操作”。

证据定位：profile `/ir_003/evidences/0`、`/ir_007/evidences/0`；原文第 9–10、16 行；契约 EM03–EM04。

源文没有规定筛选和计数的执行主体。选择 runtime 实现是可能的，但“未显示 LLM”不能证明本地隔离或模型不可见。此类理由仍把一种实现推测写得过于确定。

**助手判断：执行者归属依据不足，实际实现方式未确定。**不过，E 已在 `ir_001` 记录可能模型观察，因此不能仅因 `ir_003` 没有第二次观察，就宣布遗漏了另一份敏感数据暴露；契约也禁止无依据重复观察次数。本次能够确认的是理由过强，而不是证明漏掉了一个真实发生的第二次模型请求。

## 6. 其他保留关系与无法证明的事实

- `ir_009` 写入计数结果，不是原始文件或通知正文；写入目标为本地 `count.txt`。证据：DOE `/records/ir_009/events/0/atomic_ops/0`。计数 Data 为 `data_01d0894a241f0db2c94f3e1e249d27f44f63a77387de6be47c17788a4595d2cf`。
- `ir_010` 的空返回没有被补成 `user_output`；控制 IR 仍有 profile 与记录。
- `notify.send` 没有 CFG 输出，也未凭空增加一个被获取或观察的返回值。
- 通知是否真实发送、接收者是否确为外部网络端点、模型真实收到了哪些字节、文件写入是否成功，均没有动态证据。
- `unresolved=[]` 与 `diagnostics=[]` 仅反映模型声明及程序执行。本文件指出的证据不足和表示精度问题不能被这两个空列表覆盖。

本例支持的结论是：统一契约的默认观察已经被模型以正确的可能性措辞引用，整体来源与观察版本得以保存；它没有证明标注全面正确，也没有完成非必要敏感数据暴露判断。010 与 013 本轮因调用失败没有新语义结果，不能从 001 推广为三例全部改善。
