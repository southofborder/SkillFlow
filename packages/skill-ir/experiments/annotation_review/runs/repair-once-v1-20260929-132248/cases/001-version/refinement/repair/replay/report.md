# 安全语义标注：repair

状态：**标注记录完整**（`complete`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v3`；摘要：`26cd7f0d607b13377dc5d93546b9844b02f37db89b8dd8554613ea60e5b878ce`。

标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [校验记录](validation.json) · [完整结果](result.json)

## 执行问题与能力边界


请求身份核验（不表示标注语义正确）：

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "5e37636de60e1aea4108dc4e1c3eafeaa904ffe55e3987c1f37315b3294f6f2e",
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
      "request_body_sha256": "2658c4815fad789e9c8c20fe7af22df4385ec1e43198a6aca9ac2960f27393c8"
    }
  ],
  "transport": "http"
}
```

没有记录执行问题；不等于模型标注已经人工确认。

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
| ir_005 | notify.send | agent_runtime, tool | sink | 1. model_observe<br>2. net_send |
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

- 位置 `loc_events_json`：`storage` / `用户提供的 events.json`。
- 位置 `loc_count_txt`：`storage` / `count.txt`。
- 位置 `loc_notify_send`：`remote` / `notify.send`。
- 位置 `__compiled_model_context__`：`model_context` / `当前模型处理上下文`。

### ir_001 · 事件与公开结果

次序：`fixed`；编译因果约束：1 项。

- 事件 0：效果索引 0。
  - 操作 0：`{"op": "read", "location": "loc_events_json", "output": "event_records"}`
- 事件 1：效果索引 1。
  - 操作 0：`{"op": "deliver", "inputs": [{"kind": "local", "name": "event_records"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "event_records"}`

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
  - 操作 0：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["recipient"], "output": "recipient_value"}`
  - 操作 1：`{"op": "select_part", "input": {"kind": "local", "name": "record"}, "path": ["summary"], "output": "summary_value"}`
  - 操作 2：`{"op": "deliver", "inputs": [{"kind": "local", "name": "recipient_value"}, {"kind": "local", "name": "summary_value"}], "target": "loc_notify_send"}`

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

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文第1步要求读取用户提供的文件，属于流程内的本地读取动作；源文未提及模型参与，故参与执行主体标注为 agent_runtime。

> 读取用户提供的 events.json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取把该文件的当前内容整体引入当前流程，充当 source；记录含多个字段，本注解未做字段级加工，也未用单个字段替换来源整体。

> 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。

- `effects` / 步骤 1（索引 0） / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 的 opcode 值为 read_file 且输入为文件资源操作数，执行的是对文件内容的读取，产生 fs_read 效果。

> read_file

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只规定读取该文件；没有模型处理说明，也没有隔离执行与受限回传机制，故按默认模式编译，returns 为空。

> 读取用户提供的 events.json

- `effects` / 步骤 2（索引 1） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM03`。
  理由：EM03：无显式隔离或受限路由时，读取所得版本保留被模型观察的可能；这是契约默认可能行为，不是实测事件。

> For content acquired for the agent's natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version.

### ir_002

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的 source/sink/transformer 角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 只做控制流转移，不读取、不写入、不发送、不转换内容；词表内无适用效果，但空效果列表不表示无操作，跳转仍影响后续执行顺序。

> dispatch

### ir_003

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：筛选步骤属于流程内处理，源文与 CFG 均未指明模型执行，执行主体标注为 agent_runtime。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `roles` / `transformer`；依据 `source`，位置 `src_003`。
  理由：该动作按条件处理输入记录集合并产出子集，充当 transformer；未把内容外发或写入存储。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只给出筛选条件，未规定模型执行，也无隔离执行与受限回传机制，故按默认模式编译，returns 为空。

> 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：EM10：默认模式下筛选所依据的非隔离输入保留被模型观察的可能；本段未声称存在局部隔离。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `transform`；依据 `source`，位置 `src_003`。
  理由：按条件从集合中挑选元素属于选择类处理，词表下记为 transform；被选中元素本身保持不变。

> 选中该记录

### ir_004

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 只做控制流转移；词表内无适用效果，但跳转本身决定后续执行顺序，空列表不表示无操作。

> dispatch

### ir_005

- `operator` / `agent_runtime`；依据 `source`，位置 `src_003`。
  理由：源文要求流程对每条选中记录发起该调用，调用由本地运行流程编排执行。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `operator` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 的外部资源操作数指明具体通知服务 notify.send，实际发送由该工具执行；判断依据操作数上下文而非仅 opcode 名称。

> notify.send

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：调用使被选记录的字段值到达外部接收对象，属 sink；sink 是中性角色，不构成披露判断。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM05`。
  理由：EM05：禁止发送某字段与字段取值指令属于限制声明，本身不实现隔离或键限定接口；源文未给出模型执行或局部受限回传机制，故按默认模式编译。

> a prohibition or instruction to use only a specified field does not itself implement filtering, masking, isolation, or a key-only interface

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：EM10：默认模式下本段所处理的非隔离输入保留被模型观察的可能；returns 为空，不声称受限回传。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `net_send`；依据 `source`，位置 `src_003`。
  理由：源文明确向记录中的接收对象调用发送服务，具备通信证据，属 net_send；发送内容由后续字段选择与投递操作限定。

> 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。

- `effects` / 步骤 2（索引 1） / `net_send`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：EM06：网络投递与用户输出是不同边界；此处仅按通信证据记 net_send，未据此推断面向用户的输出。

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

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `source`，位置 `src_003`。
  理由：源文只说明产出处理条数，未规定执行方式；仅因计数确定或易于脚本化，不足以声称本地隔离，故按默认模式编译，returns 为空。

> 处理完成后，将处理条数写入本地 count.txt。

- `effects` / 步骤 1（索引 0） / `model_observe`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM10`。
  理由：EM10：默认模式下本段的非隔离输入保留被模型观察的可能；未声称存在局部隔离。

> Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs

- `effects` / 步骤 2（索引 1） / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：该指令对输入记录集合计数并输出 processed_count，属实际计算，词表下记为 transform；不产生读取、写入或外发效果。

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

> 将处理条数写入本地 count.txt

- `effects` / 步骤 1（索引 0） / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 的 opcode 值为 write_file 且目标为本地文件资源，产生 fs_write 效果。

> write_file

### ir_010

- `operator` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：该指令结束流程，由运行流程执行返回控制。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回不引入、送达或加工内容，无适用角色标签，故为空。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：普通返回没有公开输出，其 CFG 输入为空，词表内无适用效果；空效果列表不表示无操作。

> return

- `effects` / `空数组说明`；依据 `execution_model`（契约依据，非实测；结合适用对象和明确例外理解），位置 `EM06`。
  理由：EM06：普通返回不等于面向用户的输出，因此不添加 user_output 等效果。

> ordinary return does not prove user-facing output

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
