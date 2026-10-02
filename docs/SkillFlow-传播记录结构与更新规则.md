# SkillFlow 传播记录结构与更新规则

当前记录为 `skillflow-propagation-record-v9`，绑定 `security-profile-v10` 和 `skillflow-data-v4`；对外业务文件为 `skillflow-doe-input-v7`，运行身份为 `skill-ir-propagation-v10`（格式 10），上游标注运行为 `skill-ir-security-profile-v11`（格式 11）。所有 Skill 共用[抽象运行时契约](SkillFlow-统一抽象运行时契约.md)，DOE 顶层 execution_model 绑定其版本与摘要，完整规则仍放在已有审计材料。旧版本明确拒绝，不自动迁移或重写历史产物。

传播算法和模型规格见 [传播算法与 IR 传递规格](SkillFlow-传播算法与IR传递规格.md)。本规范只说明程序算出的记录、交付与恢复方式。

tool 边界允许无标签 receive 和 deliver，分别表达工具返回获取和实际参数交付；effect=null 不自动表示计算。任务内部工具不单列暴露 sink，网络未知的外部工具交付仍保留边界；见[Sink 边界与固定分级](SkillFlow-Sink边界与固定分级.md)。

## 1. 紧凑 IR 记录

```text
records[IR ID]
├─ order: fixed / partial
├─ precedence[]: before / after 原子操作位置
├─ entry_state: FlowState
├─ events[]
│  ├─ effect: 固定标签/null
│  └─ atomic_ops[]
│     ├─ op: 十种抽象操作之一（含 filter_items）
│     ├─ inputs: list[frozenset[Data ID]]
│     ├─ outputs: list[frozenset[Data ID]]
│     ├─ endpoints: FlowLocation[]
│     └─ changes: StateChange[]
└─ exit_state: FlowState
```

每条 IR 保存最终静态分析结论。重新求值替换整份记录，不把求解迭代追加为真实执行日志。数组位置是稳定审计索引；fixed 使用完整顺序，partial 使用必要先后约束，不再复制 `effect_index`、`op_index`；每次重复 effect 仍保留自己的事件，不能去重。

`events` 也可以包含单层逐元素记录：

```text
kind: for_each
collections                 实际集合候选，包含明确空集合
instances[]                 候选实例，不是实际执行次数
├─ collection: Data ID      本次对应的集合候选，可能为 subset_view
├─ element: Data ID         该集合中同一个元素的稳定身份
└─ body[]                   同一元素内的有序 effect / atomic_ops
```

接收者和正文必须在同一个 instance 中求值，不能把不同 instance 的字段集合重新作笛卡尔积。
未知长度集合使用有身份的抽象元素，不伪造真实第零项。空的已知列表得到空 instances。
本版不支持嵌套遍历、跨作用域输出、跨迭代共享状态修改；作用域内也不支持获取／共享状态读写。
范围超限在规格校验阶段明确拒绝。部分顺序保留候选安排和编译后的必要先后约束。

原模型处理段、编译后的规格和位置映射分别保存于审计材料。最终记录中的 `model_observe`
由编译器按处理段和统一契约生成；它表示静态观察边界，不能视为运行日志。详见
[字段关系与观察编译](SkillFlow-字段关系与观察编译.md)。

`inputs/outputs` 直接存实际 Data 候选集合，JSON 是二维数组。例如 `[["D_A","D_B"],["D_A"]]` 表示第一个参数可能使用 A 或 B，第二个参数再次使用 A。参数顺序和重复出现保留；只有单个候选集合内部可排序。候选不是内容拼接，也不表示同时存在。

记录不再复制符号 `ref` 或逐步 `notes`。引用来自已核验的 `IRTransferSpec`，需要审计时按 `IR ID → events位置 → atomic_ops位置` 查回；程序仍校验操作类型、输入数量、输出数量、边界、Data 引用和覆盖，不把字段删除等于检查删除。

原子操作的输入位置与 IR 操作数位置不同。例如 `update_fields` 的实际输入包括原整体及各替换值，不能把第 1 个参数机械读成 IR.inputs[1]。局部输出也不是公开 IR output；后者由原规格 `output_bindings` 登记，并反映在出口的 result 位置中。

## 2. FlowState 与 StateChange

`FlowState` 内存形式为 `FlowLocation(kind,name) → frozenset[Data ID]`，JSON 使用 `bindings` 列表，每项为 `location` 和非空 `data_ids`。位置类别包括 result、runtime_context、storage、model_context、remote、user、intermediate，同名跨类别不合并。

完整入口／出口状态不是 IR 操作数列表，也不是当前动作使用了所有已知数据的证明。未展开内容登记 opaque Data；明确空值登记 literal。没有已记录绑定时省略位置，`get` 返回 None；空状态不证明不可达。尚未提交的 IR 记录与提交空状态不同。

`StateChange` 保留 `location、before、after、update`。更新前后集合可为空，表示该位置没有绑定；这不是未知内容。update 为 strong、weak 或 delete。删除绑定不删除原 Data，也不会撤销过去的观察。

read 的 inputs 可以为空：来源在 endpoints，取得的内容在 outputs。write 只记录明确写入参数；append 所使用的旧内容在 changes.before 与新 Data.origin.inputs 中。write 没有局部 output，新存储版本在 changes.after。deliver 可以不改变状态，IN 与 OUT 相同不代表没有发送或观察。

## 3. 有序效果与部分顺序

普通规格事件恰好对应一项普通记录，逐元素规格对应一个作用域记录，作用域内按候选元素分别保存事件。有标签事件与编译后的 profile.effects 顺序一致；null 标签事件承载保守 compute 或 tool 边界的 receive。空 effects 不等于空操作：原样传递可以改变公开结果绑定而没有效果事件。

观察先绑定当时的数据版本；后续缩减不能回写为之前已观察的是干净版本。主文件每条记录保存 `order` 和 `precedence`；partial 中数组位置只用于审计对应，不构成完全确定先后的声明。保守安排的可能性由实际候选集合表达，解释边界在集中诊断和报告中说明。

## 4. 唯一 DOE 业务结果

新运行只保存一份 `doe-input.json`：

```text
schema_version
source                 完整可读源文、引用索引、文件清单和理解边界
cfg                    原 CFG；包括原输入输出、路径条件及限制
locations              kind/name/operand_refs
actions[IR ID]        operator、roles
data: Data[]          扁平目录，只含正式 Data 记录
records[IR ID]         紧凑 IRFlowRecord
status
coverage
diagnostics
```

actions 不再复制 effects：实际标签已在 events。主文件不包含 profiles 长证据、transfer_specs、注册表身份键、源码摘要或求解统计。这些信息另存 audit，主文件仍足以独立检查来源、Data 内容关系、控制条件和实际接收边界；尚未实现 DOE 判断。

source 不只保存摘录。可读文件保留原文与文本摘要，index 提供行号定位，inventory 保存文件字节／文本信息，boundaries 保留二进制和未解释脚本边界。缺少可读正文的文件不会被冒充已理解。

## 5. 容器与显式恢复

`PropagationRecords` 保留单一活动 DataRegistry，CFG 和标注隔离复制，查询和导出返回隔离副本。

```python
records.put(ir_id, record)                 # 先完整验证，成功后原子替换
record = records.get(ir_id)                # 无记录时 KeyError
records.validate(require_complete=True)    # 覆盖所有真实 IR，含 dispatch/return
snapshot = records.to_dict()               # 只有版本、记录、完整标志和材料摘要
restored = PropagationRecords.from_dict(
    snapshot,
    cfg=cfg,
    annotation=annotation,
    data_registry=registry,
    initial_data=initial_data,
    initial_state=initial_state,
)
```

`to_json/from_json` 使用同一结构。恢复的五项材料全部显式必填，并逐项核验摘要；不再从快照中自动恢复另一份 Data 权威。`records_dict()` 只返回按 IR 索引的记录，供业务投影使用。is_complete 只指全 IR 覆盖，与求解 status、固定或部分顺序分开。

注册表身份索引另存在 audit，恢复时配合主文件的扁平 Data 重建并核验；Data 不复制身份键。记录快照在 audit 保存为 `record-materials.json`，去掉其中 records，再使用主文件 records 显式接入恢复。不能仅重算摘要绕过原始接受响应的真实性检查。

## 6. 保存、重放和报告

正式模型标注与手工示例共用 `save_propagation_run`。该入口要求新／空目录，保存业务与审计材料后验证落盘内容，最后才提交 manifest。人工示例声明 `hand_authored_specification`；真实标注绑定实际接受响应，不伪造模型调用。

运行目录：

```text
run/
├─ doe-input.json
├─ manifest.json
├─ audit/
│  ├─ material.json / source-metadata.json
│  ├─ annotation.json / location-evidences.json
│  ├─ initial-data.json / initial-state.json
│  ├─ requested-data.json / requested-state.json
│  ├─ data-identities.json / record-materials.json
│  ├─ provenance.json / stats.json
│  └─ accepted-call/                    仅真实模型标注运行
├─ report.md / report.html
└─ replay/
   ├─ summary.json                      matched/mismatch、摘要与差异，零调用
   └─ report.md / report.html            链接原 doe-input.json
```

不再导出 result.json、data.json、records.json 或 resolved-seed.json；重放也不复制完整主结果。重放从保存材料离线重算、对比唯一主文件，错误保持为明确失败。

MD 与 HTML 共用 `build_view`。默认按 IR 展示业务效果、二维 Data 参数、边界、状态变化和可点击数据版本；完整源文也取自主文件。可选 audit 只在折叠区显示原规格参数、公开输出绑定、profile 证据、位置依据和技术统计。

DOE 顶层 sink_boundaries 从已形成的记录重建：普通操作用 IR/event/op 定位，逐元素操作增加 body_event_index 和 scope=element。它只引用已有目标、类型和固定等级，不再复制 Data 参数；同一作用域的实例参数在原记录中读取。独立读取核验这份清单，完整加载和重放进一步核验编译来源。缺失 IR 记录仍由 coverage 说明，不能因为清单为空就宣称无暴露。

## 7. 示例与验收

```powershell
python packages/skill-ir/examples/propagation_demo.py
python packages/skill-ir/examples/propagation_demo.py --records-only
python packages/skill-ir/examples/propagation_demo.py --output path/to/new-authored-demo
python -m skill_ir.propagation replay --run-dir path/to/new-authored-demo
```

原 propagation_record_demo.py 已删除，所有用途合并到主示例。工具 render_demo 也仅委托同一保存入口，不捕获或拼装另一套示例材料。

验收覆盖重复参数、事件时序、前后 Data 版本、输入输出数量、显式材料恢复、保存隔离、重复文件清理、HTML 转义与零 API 重放。字段一致、求解完成与模型标注正确是不同结论。历史 v1–v4 记录、旧快照和已有 30 例产物保留原样，不能视为新格式的实测结果。

## 可选成员的紧凑记录

build 记录增加 `members`：每项只保存 path、value_input_index、when_input_index；索引指向原操作 inputs，不复制 Data ID。无条件的 when_input_index 为 null，确定省略的 value_input_index 为 null。编译生成的条件观察记录使用 when_input_index 指向控制槽位；它不属于观察载荷。主文件不增加新的顶层区或证据链。

载荷解析由统一函数供 sink 清单、报告和独立 DOE 校验使用。控制输入仍保留其操作依赖，但不机械成为工具收到的参数。确定不发生的条件观察不收集为实际 sink；可能发生的观察保留。完整说明见[可选参数主规范](SkillFlow-Sink标注收紧与可选参数.md)。
