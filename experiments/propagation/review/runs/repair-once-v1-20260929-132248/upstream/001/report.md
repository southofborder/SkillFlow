# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v2`；摘要：`12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "a43cf21d4c84a5291aa42145f503996e5158e677bf561f838d4be1745ba26c5f",
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
      "request_body_sha256": "337591804558b3a64fc0b04faef05e10165884ed22791a2b65e827298965d10f"
    }
  ],
  "transport": "http"
}
```

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · 读取用户提供的 events.json

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_file | agent_runtime | source | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_002 · 根据 opted_out、urgent 和 value 条件选中记录

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | select_notifiable_events | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_004 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_003 · 对每条选中记录调用 notify.send

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | notify.send | agent_runtime, tool | sink | 1. model_observe<br>2. net_send |
| ir_006 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_004 · 统计已处理条数

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | count_processed_records | agent_runtime | transformer | 1. model_observe<br>2. transform |
| ir_008 | dispatch | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

### block_005 · 将处理条数写入本地 count.txt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | write_file | agent_runtime | sink | 1. fs_write |
| ir_010 | return | agent_runtime | [] | []（无已记录效果；不等于空操作，请结合证据与未决项） |

## 符号传播说明

以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。

[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)

- 位置 `loc_events_json`：`storage` / `用户提供的 events.json`。
- 位置 `loc_count_txt`：`storage` / `count.txt`。
- 位置 `loc_notify_send`：`remote` / `notify.send`。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`。

### ir_001 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "event_records"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "event_records"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "event_records"}`

### ir_002 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_003 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "filter_items", "input": {"kind": "input", "index": 0}, "predicate": "仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。", "output": "selected_records"}`
- output[0] ← `{"kind": "local", "name": "selected_records"}`

### ir_004 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_005 · 事件与公开结果

- 逐元素作用域 0：集合 `{"kind": "input", "index": 1}`，元素绑定 `record`。同一元素的字段保持配对；不表示真实集合长度或实际调用次数。
- 事件 0.0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "record"}], "target": "__compiled_model_context__"}`
- 事件 0.1：效果索引 1。
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["recipient"], "output": "recipient_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["summary"], "output": "summary_value"}`
  - 操作 2：`{"op": "deliver", "inputs": [{"kind": "local", "name": "recipient_value"}, {"kind": "local", "name": "summary_value"}], "target": "loc_notify_send"}`

### ir_006 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_007 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "processed_count"}`
- output[0] ← `{"kind": "local", "name": "processed_count"}`

### ir_008 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

### ir_009 · 事件与公开结果

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "write", "target": "loc_count_txt", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_010 · 事件与公开结果

- 事件为空；仍须保留下面的结果绑定。

## 标注依据

### ir_001

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文第1步要求读取用户提供的文件，属流程内本地动作，执行主体标注为 agent_runtime；源文未提及模型参与该读取。

> 读取用户提供的 events.json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取把该文件当前内容整体引入当前流程，充当 source；内容包含记录的全部字段，未做字段级加工。

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 的 opcode 值为 read_file 且输入为文件资源，产生对文件内容的读取效果 fs_read。

> read_file

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只规定读取该文件，没有规定模型处理，也没有隔离执行与受限回传机制，故按默认模式编译，returns 为空。

> 读取用户提供的 events.json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM03`。
  理由：EM03：读取所得版本在无显式隔离或受限路由时保留被模型观察的可能；这是契约默认，不是实测事件。

> For content acquired for the agent's natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version.

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的 source/sink/transformer 角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 只做控制流转移，不读取、不写入、不发送、不转换内容；词表内无适用效果，但控制转移本身仍影响后续执行顺序。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：筛选步骤属于流程内的本地处理，源文与 CFG 均未指明模型执行，执行主体标注为 agent_runtime。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该动作按条件处理输入记录集合并筛出子集，属 transformer；未把内容外发或写入存储。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文给出筛选条件，但未规定模型执行，也未规定隔离执行与受限回传机制，因此按默认模式编译，returns 为空。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：EM10：默认模式下，筛选所依据的读取输出保留被模型观察的可能；本段未声称存在局部隔离。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：按条件从集合中挑选元素属于选择/过滤类处理，词表下记 transform；被选中元素本身保持不变。

> 选中该记录

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 只做控制流转移；词表内无适用效果，但跳转本身决定后续执行顺序。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文要求流程对每条选中记录发起该调用，调用由本地运行流程编排执行。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `operator` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 的外部资源操作数指明具体通知服务 notify.send，实际发送动作由该工具/服务执行；不是仅凭 opcode 名称推断执行主体。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：调用使记录中的 recipient 与 summary 值到达外部接收对象，属 sink；未加入加工角色。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：逐元素段未见模型处理或局部隔离、受限回传机制，按默认模式编译；returns 为空。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文否定摘要生成与格式转换，本段只做字段选择与投递。

> 字段取值要求不包含摘要生成、内容改写或额外格式转换。

- `effects` / 步骤 2（索引 1） / `net_send`；依据 `source`，位置 `src_003`。
  理由：源文明确向记录中的接收对象发送内容，具备通信证据，属远程发送 net_send；发送内容为选中记录的字段值。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 2（索引 1） / `net_send`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：EM06：网络投递与用户输出是分开的边界；此处按通信证据只记 net_send，未据此推断用户可见输出。

> Model observation, network delivery, and user output are separate boundaries.

### ir_006

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。

> dispatch

### ir_007

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文把处理条数作为流程内部产出的数值，未见模型处理说明；该统计由 agent_runtime 在流程内执行。

> 处理完成后，将处理条数写入本地 count.txt。

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：处理条数由对选中记录集合的统计加工得到，该步骤充当 transformer。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：本段没有模型执行证据，也没有局部隔离与受限回传机制，按默认模式编译；returns 为空。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只说明产出计数结果，未规定执行方式；仅因计数简单或可实现为脚本，不足以声称本地隔离。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：对输入集合计数是实际计算，属 transform；不产生读取、写入或外发效果。

> count_processed_records

### ir_008

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。

> dispatch

### ir_009

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：本地写文件步骤由 agent_runtime 执行；源文未提及模型或外部工具参与。

> 处理完成后，将处理条数写入本地 count.txt。

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：写入使内容到达本地存储位置，属 sink；写入内容为计数值本身。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 的 opcode 值为 write_file 且目标为本地文件，产生 fs_write 效果。

> write_file

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：该指令结束流程，由运行流程执行返回控制。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：结束控制不引入、送达或加工内容，无适用角色标签。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回只是控制结束，词表内无适用效果；它也不等于面向用户的输出。

> return

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
