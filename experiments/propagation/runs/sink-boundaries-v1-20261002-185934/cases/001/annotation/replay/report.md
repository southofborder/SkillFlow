# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v4`；摘要：`1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66`。

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
  "prompt_sha256": "496e899b67b01fb7e6561a29ccc1c009199177efee4a7c2a4edf5c96994e8aad",
  "observed": true,
  "requests": [
    {
      "request_parameters": {
        "model": "deepseek-v4-flash",
        "reasoning_effort": "max",
        "response_format": {
          "type": "json_object"
        },
        "stream": true,
        "stream_options": {
          "include_usage": true
        }
      },
      "request_body_sha256": "530016c9f96800c08dbef34bc6a20dbc09885fa6ac45f3ffa25e24e499dfef7a"
    }
  ],
  "transport": "http"
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
| ir_005 / 0.2 / 0 | loc_notify_send · remote / notify.send | network_send | 2 | recipient / None | element |
| ir_007 / 0 / 0 | __compiled_model_context__ · model_context / 当前模型处理上下文 | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | loc_count_txt · storage / count.txt | storage_write | 1 | task / persistent | — |

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
| ir_005 | notify.send | agent_runtime, tool | transformer, sink | 1. model_observe<br>2. transform<br>3. net_send |
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

- 位置 `loc_events_json`：`storage` / `用户提供的 events.json`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_notify_send`：`remote` / `notify.send`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `loc_count_txt`：`storage` / `count.txt`；访问范围 `task`，留存 `persistent`。位置依据见独立审计表，默认属性不冒充真实运行事实。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`；访问范围 `recipient`，留存 `None`。位置依据见独立审计表，默认属性不冒充真实运行事实。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "events_raw"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "events_raw"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "events_raw"}`

### ir_002 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "filter_items", "input": {"kind": "input", "index": 0}, "predicate": "仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。", "output": "selected_records"}`
- output[0] ← `{"kind": "local", "name": "selected_records"}`

### ir_004 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

次序：`fixed`；编译因果约束：4 项。

- 逐元素作用域 0：集合 `{"kind": "input", "index": 1}`，元素绑定 `record`。同一元素的字段保持配对；不表示真实集合长度或实际调用次数。
- 事件 0.0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "record"}], "target": "__compiled_model_context__"}`
- 事件 0.1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["recipient"], "output": "record_recipient"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["summary"], "output": "record_summary"}`
- 事件 0.2：效果索引 2。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "record_recipient"}, {"kind": "local", "name": "record_summary"}], "target": "loc_notify_send"}`

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
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_010 · 事件与公开结果

次序：`fixed`；编译因果约束：0 项。

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该指令为本地文件读取操作，执行主体是流程运行时 agent_runtime；源文未指定模型或外部工具参与。

> read_file

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该指令从外部文件引入事件记录到当前流程，扮演数据引入的 source 角色。

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取事件文件内容属于 fs_read；未发生网络发送、用户输出或上下文写入。

> read_file

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未规定本地隔离、限定回传或模型处理接口，读取事件文件的处理按 default 模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该指令是流程运行时执行的记录筛选，未指定 LLM 或外部工具参与。

> select_notifiable_events

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该指令按条件挑选记录并改变集合组成，扮演 transformer 角色。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未规定筛选在隔离本地执行或由模型处理，按 default 模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：条件筛选属于 transform；未产生文件、网络或用户输出边界效果。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：流程运行时按选中记录组织并调用 notify.send，传入接收对象和 body 参数，故 agent_runtime 参与执行。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `operator` / `tool`；依据 `source`，位置 `src_003`。
  理由：notify.send 是实际执行发送的工具/端点，故 tool 参与执行。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该指令从每条记录中选取 recipient 与 summary 字段并组织成通知参数，属于选择/转换，扮演 transformer。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该指令使通知内容到达记录中的接收对象，扮演 sink。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未规定逐条发送在隔离本地执行或由模型处理，按 default 模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文规定逐条选中记录执行一次发送，因此用 for_each 绑定当前记录元素。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：先从当前记录选取 recipient 和 summary 原值，属于字段选择转换，且不生成摘要或改写。

> notify.send 的 body 参数直接取该记录的 summary 字段原值。

- `effects` / 步骤 3（索引 2） / `net_send`；依据 `source`，位置 `src_003`。
  理由：随后把同一记录的接收对象和 summary 参数发送给 notify.send，构成对外发送的 net_send 效果。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：该指令是流程运行时执行的计数计算，未指定 LLM 或外部工具参与。

> count_processed_records

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该指令计算已处理记录条数，属于统计转换，扮演 transformer。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：源文未规定计数在隔离本地执行或由模型处理，按 default 模式分析。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：统计已选记录数量属于 transform 计算；未产生文件或网络边界动作。

> 处理完成后，将处理条数写入本地 count.txt。

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地文件写入由流程运行时执行，未指定 LLM 或外部工具。

> 处理完成后，将处理条数写入本地 count.txt。

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：把处理条数写入 count.txt 存储位置，使内容到达存储边界，扮演 sink。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `source`，位置 `src_003`。
  理由：创建或修改本地文件内容属于 fs_write；该文件写入不自动构成 context_write。

> 处理完成后，将处理条数写入本地 count.txt。

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回是流程运行时的控制返回操作，执行者为 agent_runtime。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回不属于所列效果词汇，也不表示用户输出、网络发送或上下文写入。

> return

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
