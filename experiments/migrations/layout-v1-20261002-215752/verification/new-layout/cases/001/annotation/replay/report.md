# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v5`；摘要：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [Sink 边界](sink-boundaries.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "a34a7d130c77e406a2cb47ce32c68d4a17605c8c8b5386f0ace1bd590bed6a4e",
  "observed": false,
  "requests": [],
  "transport": "injected"
}
```

没有记录执行问题；不等于模型标注已经人工确认。

## Sink 边界与固定等级

类型和等级由程序按位置属性和具体交付／写入操作生成；等级仅表达边界访问及留存，不表示敏感度、危险程度、任务必要性或 DOE 结论。标注阶段关联符号操作，传播后由同一操作关联实际数据版本。

| IR / 事件 / 操作 | 边界 | 类型 | 等级 | 访问范围 / 留存 | 作用域 |
|---|---|---|---|---|---|
| ir_001 / 1 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_003 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_005 / 0.0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | element |
| ir_005 / 0.2 / 0 | loc_notify_send · tool / notify.send | external_tool | 2 | recipient / None | element |
| ir_007 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | loc_count_file · storage / count.txt | storage_write | 1 | task / persistent | — |

任务内部且任务期限内的流动仍保留在传播说明中，等级 0 不进入 Sink 清单；删除绑定不交付旧内容。未进入清单不等于已证明没有数据风险。

## 按块查看

### block_001 · 读取用户提供的 events.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_file | agent_runtime | source | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_002 · 根据 opted_out、urgent 和 value 条件选中记录

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | select_notifiable_events | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_003 · 对每条选中记录调用 notify.send

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | notify.send | agent_runtime, tool | sink, transformer | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_004 · 统计已处理条数

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | count_processed_records | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

### block_005 · 将处理条数写入本地 count.txt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | write_file | agent_runtime | sink | 1. fs_write |
| ir_010 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合动作与绑定） |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)

- 位置 `loc_events_file`：`storage` / `events.json`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_count_file`：`storage` / `count.txt`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_notify_send`：`tool` / `notify.send`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_file", "output": "events_content"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "events_content"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "events_content"}`

### ir_002 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "filter_items", "input": {"kind": "input", "index": 0}, "predicate": "opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100", "output": "selected_records"}`
- output[0] ← `{"kind": "local", "name": "selected_records"}`

### ir_004 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

次序：`fixed`；编译因果约束：4 项。

- 逐元素作用域 0：集合 `{"kind": "input", "index": 1}`，元素绑定 `event_record`。同一元素的字段保持配对；不表示真实集合长度或实际调用次数。
- 事件 0.0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "event_record"}], "target": "__compiled_model_context__"}`
- 事件 0.1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "event_record"}, "path": ["recipient"], "output": "recipient_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "local", "name": "event_record"}, "path": ["summary"], "output": "summary_value"}`
- 事件 0.2：无安全标签的数据关系。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "recipient_value"}, {"kind": "local", "name": "summary_value"}], "target": "loc_notify_send"}`

### ir_006 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "processed_count"}`
- output[0] ← `{"kind": "local", "name": "processed_count"}`

### ir_008 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_file", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文规定由本流程读取该文件，执行者是本地 agent 运行时；未提及模型、工具或人工执行者。

> 读取用户提供的 events.json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取把用户提供文件的内容引入当前流程，构成 source 角色；按 EM01 保留该文件整体为可能的获取范围。

> 读取用户提供的 events.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `source`，位置 `src_003`。
  理由：读取本地文件内容属于 fs_read；没有网络接收或直接用户输出证据。

> 读取用户提供的 events.json

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：CFG 指令操作码为 read_file，与源文读取步骤一致。

> read_file

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只规定读取该文件；未规定模型处理，也未规定本地隔离执行及其限定回传边界，因此按默认模式声明该处理边界。

> 读取用户提供的 events.json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM05`。
  理由：对已存在的读取动作，默认规则只提供可能的分析事件，不虚构额外的获取或保护动作；获取版本的后续观察由编译器按模式编译。

> Contract defaults may supply possible analysis events for an existing action

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：筛选指令由本地 agent 运行时的流程执行；源文未提及模型或人工参与选择。

> select_notifiable_events

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：按条件从集合中选择记录属于对内容的处理，构成 transformer；选中记录本身保持原样。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文给出显式逐条筛选条件且不要求改写记录；未规定模型处理或本地隔离与限定回传，因此按默认模式。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM05`。
  理由：默认规则只对已存在动作提供可能的分析事件，不把筛选谓词变成额外的保护动作。

> Contract defaults may supply possible analysis events for an existing action

- `effects` / 步骤 2（索引 1） / `transform`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM04`。
  理由：条件筛选属于选择类处理，按 EM04 记为 transform。

> Selection, masking, encryption, and summarization use transform when supported

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：源文明确按条件选中记录，对应效应词汇表中的选择类处理。

> 选中该记录

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：逐条构造并发出工具调用由本地 agent 运行时执行；源文未提及模型参与。

> 对每条选中记录调用一次 notify.send

- `operator` / `tool`；依据 `source`，位置 `src_003`。
  理由：notify.send 是执行通知发送动作的工具执行者，工具名称保留在 IR 与位置名称中。

> 调用一次 notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：内容经该调用送达接收对象，构成 sink 角色；没有网络传输机制证据，按 EM13 以工具边界表示而不是 net_send。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：逐条记录选取 recipient 与 summary 字段构造请求参数，属于对内容的处理与选择，构成 transformer；取值保持原值。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM05`。
  理由：默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。

> Contract defaults may supply possible analysis events for an existing action

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：选取已有字段用于请求参数属于选择类处理；投递本身在无网络证据下由零效应 deliver 表示，不并入 net_send。

> 接收对象取该记录的 recipient 字段

- `effects` / 步骤 2（索引 1） / `transform`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM04`。
  理由：逐条字段选择按 EM04 记为 transform。

> Selection, masking, encryption, and summarization use transform when supported

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：计数步骤在流程内由本地 agent 运行时执行；无模型或人工执行证据。

> count_processed_records

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：由已选记录集合计算处理条数属于内容计算，构成 transformer。

> 将处理条数写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文要求统计处理条数；未规定模型处理或本地隔离执行及限定回传，按默认模式。

> 将处理条数写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM05`。
  理由：默认规则只对已有计数动作给出可能的分析事件，不虚构额外外部来源。

> Contract defaults may supply possible analysis events for an existing action

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：计数是计算操作，按效应词汇表记为 transform。

> count_processed_records

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：源文要求得到处理条数，对应计算类处理。

> 处理条数

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：写文件动作由本地 agent 运行时执行；无模型或人工写入证据。

> write_file

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：内容到达本地存储位置，构成 sink 角色；写入值为计数结果原值，无额外转换。

> 将处理条数写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：创建或修改本地文件内容属于 fs_write；文件写入不自动附加 context_write。

> 将处理条数写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：CFG 写文件操作码支持 fs_write 标注。

> write_file

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：返回终结由本地 agent 运行时执行控制流结束。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：该终结指令没有 CFG 输入和公开输出，不引入、处理或外送内容，因此没有可适用的角色标签。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回不构成用户输出或任何交付；不虚构 user_output、网络投递或其他效应标签。

> return

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
