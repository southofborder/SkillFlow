# SkillFlow 传播记录结构与更新规则

当前记录身份为 `skillflow-propagation-record-v11`，传播运行是 `skill-ir-propagation-v14`。联合标注 v13／运行 v16，Data 保持 v4。上游源文、CFG、规则和接受响应由明确运行引用关联，不复制进传播产物；当前完整版本见[字段收紧规范](../architecture/field-tightening.md)。旧格式不自动迁移。

传播算法和模型规格见 [传播算法与 IR 传递规格](SkillFlow-传播算法与IR传递规格.md)。本规范只说明程序算出的记录、分阶段保存与恢复方式。

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

`FlowState` 内存形式为 `FlowLocation(kind,name) → frozenset[Data ID]`，JSON 使用 `bindings` 列表，每项为 `location` 和非空 `data_ids`。位置类别包括 result、runtime_context、storage、model_context、remote、tool、user、intermediate，同名跨类别不合并。

完整入口／出口状态不是 IR 操作数列表，也不是当前动作使用了所有已知数据的证明。未展开内容登记 opaque Data；明确空值登记 literal。没有已记录绑定时省略位置，`get` 返回 None；空状态不证明不可达。尚未提交的 IR 记录与提交空状态不同。

`StateChange` 保留 `location、before、after、update`。更新前后集合可为空，表示该位置没有绑定；这不是未知内容。update 为 strong、weak 或 delete。删除绑定不删除原 Data，也不会撤销过去的观察。

read 的 inputs 可以为空：来源在 endpoints，取得的内容在 outputs。write 只记录明确写入参数；append 所使用的旧内容在 changes.before 与新 Data.origin.inputs 中。write 没有局部 output，新存储版本在 changes.after。deliver 可以不改变状态，IN 与 OUT 相同不代表没有发送或观察。

## 3. 有序效果与部分顺序

普通规格事件恰好对应一项普通记录，逐元素规格对应一个作用域记录，作用域内按候选元素分别保存事件。有标签事件保持编译后 ir_semantics.events 中的出现顺序；null 标签事件承载保守 compute 或 tool 边界的 receive/deliver。空 effects 不等于空操作：原样传递可以改变公开结果绑定而没有效果事件。

观察先绑定当时的数据版本；后续缩减不能回写为之前已观察的是干净版本。主文件每条记录保存 `order` 和 `precedence`；partial 中数组位置只用于审计对应，不构成完全确定先后的声明。保守安排的可能性由实际候选集合表达，解释边界在集中诊断和报告中说明。

## 4. 分阶段事实文件与恢复

传播只保存自己生成的业务事实，不再生成 `doe-input.json`、record-materials 封套或完整上游副本：

```text
propagation/
├─ data.json                 Data[]；最终 Data 内容各一份
├─ records.json              IR ID → IRFlowRecord；没有摘要外壳
├─ sinks.json                SinkBoundary[]；实际形成记录的边界
├─ manifest.json             版本、上游引用、状态、覆盖、诊断、各文件摘要
├─ audit/
│  ├─ requested-data.json / requested-state.json  调用方原始种子
│  ├─ initial-data.json / initial-state.json      实际求解初始版本
│  ├─ data-identities.json                        最终登记身份，不复制内容
│  └─ stats.json                                 技术统计
├─ report.md / report.html
└─ replay/summary.json        重新求解比较的结果；不复制最终 Data
```

`manifest.upstream = {path, manifest_sha256}` 指向本次真正的标注运行。地址相对于当前阶段，身份由摘要校验；不按相似目录名寻找材料。整棵运行目录可以搬迁；丢失上游时明确失败。源文、CFG、位置、operator、规则和原始／编译标注从上游读取，传播不维护 actions 等第二份投影。

`PropagationRecords` 是内存记录容器。`records_dict()` 导出纯记录；`from_records(records, cfg=..., annotation=..., data_registry=..., initial_data=..., initial_state=...)` 用调用方明确提供的材料重建并校验。旧 `to_dict/from_dict/to_json/from_json` 快照封套已删除。公开 `load_propagation_materials(run_dir)` 返回校验后的 `PropagationMaterials` 内存组件，不提供再次序列化为总包的入口。

最终 Data 与初始 Data 是不同描述版本，不能为去重而混为一份。原始种子与有效种子也保留区别。登记身份必须与最终 Data 对应；加载同时验证接受响应、编译结果、原始映射、请求链、记录及 sink 覆盖。

## 5. Sink 与参数

`sinks.json` 从已形成记录的交付和保存操作重建：普通操作用 IR/event/op 坐标；逐元素操作增加 body_event_index 和 scope=element。只存目标、类型和固定等级，实际 Data 参数从该操作记录读取，候选实例保持原配对。原始编译 sink 模板保留在上游，不冒充实际求值清单。

条件观察及 build 的控制槽使用共同载荷解析函数；控制旗标不因为出现在 inputs 中就成为交付明文。删除不产生内容保存 sink。覆盖／追加保留本次载荷与写后版本的区别。未形成记录的 IR 由 manifest 的 coverage/diagnostics 明确说明。

## 6. 保存、重放和报告

正式保存先验证阶段文件，最后提交 manifest。普通读取检查内容和上游身份；重新计算还要求实现身份一致。`run_propagation(annotation_run, run_dir=...)` 使用严格加载的标注，`replay_propagation(run_dir)` 零 API 重算并比较 data、records、sinks、覆盖及诊断。不能仅改摘要绕过接受响应或调用记录。

Markdown 和 HTML 共用 `PropagationMaterials` 展示模型，默认显示数据、效果、参数、状态变化和边界。上游证据可以展开审计；这不会使记录变成执行日志。普通 return 仍从 CFG 输入保留返回身份，没有虚构输出或接收方。

## 7. 示例与验收

```powershell
python examples/propagation/propagation_demo.py
python examples/propagation/propagation_demo.py --records-only
python examples/propagation/propagation_demo.py --output path/to/new-authored-demo
python -m skillflow.propagation replay --run-dir path/to/new-authored-demo
```

原 propagation_record_demo.py 已删除，所有用途合并到主示例。工具 render_demo 也仅委托同一保存入口，不捕获或拼装另一套示例材料。

验收覆盖重复参数、事件时序、前后 Data 版本、输入输出数量、显式材料恢复、保存隔离、重复文件清理、HTML 转义与零 API 重放。字段一致、求解完成与模型标注正确是不同结论。历史 v1–v4 记录、旧快照和已有 30 例产物保留原样，不能视为新格式的实测结果。

## 可选成员的紧凑记录

build 记录增加 `members`：每项只保存 path、value_input_index、when_input_index；索引指向原操作 inputs，不复制 Data ID。无条件的 when_input_index 为 null，确定省略的 value_input_index 为 null。编译生成的条件观察记录使用 when_input_index 指向控制槽位；它不属于观察载荷。记录不增加平行证据链。

载荷解析由统一函数供 sink 清单、报告和公共材料加载使用。控制输入仍保留其操作依赖，但不机械成为工具收到的参数。确定不发生的条件观察不收集为实际 sink；可能发生的观察保留。完整说明见[可选参数主规范](SkillFlow-Sink标注收紧与可选参数.md)。
