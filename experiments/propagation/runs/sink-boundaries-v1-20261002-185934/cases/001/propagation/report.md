# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v4`；SHA-256：`1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66`。

求解状态：`complete`。

IR 记录覆盖：10 / 10。

[本地可视化审查](report.html) · [唯一业务结果](doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](audit/material.json)（execution_model）；逐项依据在下方审计区展开。

## 接收与保存边界

纳入清单 6 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。

等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。

| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |
|---|---|---|---|---|---|
| ir_001 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_003 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.候选组1.1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 同一元素 D004；0: D004 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.候选组1.3.1 | 纳入 | network_send / 2 | loc_notify_send · remote: notify.send · recipient / 未建模期限 | 同一元素 D004；0: D005; 1: D003 | 另一接收主体或跨主体共享；source/src_003, cfg/g_0021, execution_model/EM12, execution_model/EM12 |
| ir_007 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D006 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_009 / 1.1 | 纳入 | storage_write / 1 | loc_count_txt · storage: count.txt · task / persistent | 0: D001 | 任务内部、跨任务留存；source/src_003, cfg/g_0033, execution_model/EM12 |

<details><summary>完整源文</summary>

<pre>{
  &quot;boundaries&quot;: {
    &quot;binary_files&quot;: [],
    &quot;notice&quot;: &quot;提取和核对共享全部可读文件。二进制未进入文本语义核对；代码及嵌入内容不因此获得执行正确性或行为理解保证。&quot;,
    &quot;uninterpreted_code_files&quot;: []
  },
  &quot;files&quot;: [
    {
      &quot;content&quot;: &quot;---\nname: conditional-notification\ndescription: 根据事件记录的订阅状态、紧急标记和数值发送通知。\n---\n\n# 条件通知与数据发送\n\n1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。\n2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。\n3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。\n4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。\n5. notify.send 的 body 参数直接取该记录的 summary 字段原值。\n6. 未选中的记录不调用 notify.send。\n7. 整份流程禁止将 access_token 字段发送给任何接收对象。\n8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。\n9. 处理完成后，将处理条数写入本地 count.txt。\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;461270c7deec087306acf3473a0b276b72edd45811642c5da19482d35f5bcd3f&quot;
    }
  ],
  &quot;index&quot;: [
    {
      &quot;end_line&quot;: 4,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_001&quot;,
      &quot;start_line&quot;: 1
    },
    {
      &quot;end_line&quot;: 6,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_002&quot;,
      &quot;start_line&quot;: 6
    },
    {
      &quot;end_line&quot;: 16,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_003&quot;,
      &quot;start_line&quot;: 8
    }
  ],
  &quot;inventory&quot;: [
    {
      &quot;decoded_sha256&quot;: &quot;461270c7deec087306acf3473a0b276b72edd45811642c5da19482d35f5bcd3f&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;raw_sha256&quot;: &quot;461270c7deec087306acf3473a0b276b72edd45811642c5da19482d35f5bcd3f&quot;,
      &quot;size&quot;: 931
    }
  ],
  &quot;source_sha256&quot;: &quot;6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab&quot;
}</pre>

</details>

<details><summary>覆盖与诊断</summary>

<pre>{
  &quot;coverage&quot;: {
    &quot;ir_001&quot;: &quot;processed&quot;,
    &quot;ir_002&quot;: &quot;processed&quot;,
    &quot;ir_003&quot;: &quot;processed&quot;,
    &quot;ir_004&quot;: &quot;processed&quot;,
    &quot;ir_005&quot;: &quot;processed&quot;,
    &quot;ir_006&quot;: &quot;processed&quot;,
    &quot;ir_007&quot;: &quot;processed&quot;,
    &quot;ir_008&quot;: &quot;processed&quot;,
    &quot;ir_009&quot;: &quot;processed&quot;,
    &quot;ir_010&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_001 · read_file

块：block_001；执行主体：agent_runtime；角色：source。

IR 输入：0: 用户提供的 events.json

IR 输出：0: result_001

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: 用户提供的 events.json | 0: D002 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read_file&quot;,
          &quot;reason&quot;: &quot;该指令的公开输出是读取结果，直接绑定到刚读取的本地值 events_raw。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;events_raw&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;fs_read&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;read_file&quot;,
        &quot;reason&quot;: &quot;该指令为本地文件读取操作，执行主体是流程运行时 agent_runtime；源文未指定模型或外部工具参与。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
        &quot;reason&quot;: &quot;该指令从外部文件引入事件记录到当前流程，扮演数据引入的 source 角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_file&quot;,
        &quot;reason&quot;: &quot;读取事件文件内容属于 fs_read；未发生网络发送、用户输出或上下文写入。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;源文未规定本地隔离、限定回传或模型处理接口，读取事件文件的处理按 default 模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;source&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
          &quot;reason&quot;: &quot;读取整个 events.json 文件内容；源文没有字段级接口或只读取特定字段的机制，故保留整个文件读取范围。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_events_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;events_raw&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;源文未规定本地隔离、限定回传或模型处理接口，读取事件文件的处理按 default 模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;events_raw&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_002 · dispatch

块：block_001；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_003 · select_notifiable_events

块：block_002；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_001

IR 输出：0: result_002

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | filter_items | 0: D002 | — | 0: D006 |

入口／出口变化：

- `result: result_002`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;select_notifiable_events&quot;,
          &quot;reason&quot;: &quot;该指令的公开输出是筛选后的记录集合，绑定到 filter_items 产生的本地值 selected_records。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;selected_records&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;select_notifiable_events&quot;,
        &quot;reason&quot;: &quot;该指令是流程运行时执行的记录筛选，未指定 LLM 或外部工具参与。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;该指令按条件挑选记录并改变集合组成，扮演 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;源文未规定筛选在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;条件筛选属于 transform；未产生文件、网络或用户输出边界效果。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;源文未规定筛选在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
          &quot;reason&quot;: &quot;按源文给出的布尔与数值条件筛选记录，保留选中元素本身不变；未执行额外摘要或改写。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
          &quot;reason&quot;: &quot;该操作对应带谓词的集合筛选，保留每个选中元素的原值。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;filter_items&quot;,
      &quot;output&quot;: &quot;selected_records&quot;,
      &quot;predicate&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;
    }
  ]
}</pre>

</details>

## ir_004 · dispatch

块：block_002；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_005 · notify.send

块：block_003；执行主体：agent_runtime, tool；角色：transformer, sink。

IR 输入：0: notify.send, 1: result_002, 2: &quot;recipient&quot;, 3: &quot;summary&quot;

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: 1,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: 0,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: 1,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: 1,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: 2,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: 1,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: 2,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: 1,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

逐元素作用域 1：集合候选 D006。以下各候选组单独绑定同一个元素，不能跨组组合参数；不是实际执行次数。

- 候选组 1：集合 D006 → 元素 D004。

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.候选组1.1.1 | model_observe（程序生成，静态可能） | deliver | 0: D004 | model_context: 当前模型处理上下文 | — |
| 1.候选组1.2.1 | transform | select_part | 0: D004 | — | 0: D005 |
| 1.候选组1.2.2 | transform | select_part | 0: D004 | — | 0: D003 |
| 1.候选组1.3.1 | net_send | deliver | 0: D005; 1: D003 | remote: notify.send | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;,
      &quot;transform&quot;,
      &quot;net_send&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;流程运行时按选中记录组织并调用 notify.send，传入接收对象和 body 参数，故 agent_runtime 参与执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;notify.send 是实际执行发送的工具/端点，故 tool 参与执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
        &quot;reason&quot;: &quot;该指令从每条记录中选取 recipient 与 summary 字段并组织成通知参数，属于选择/转换，扮演 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;该指令使通知内容到达记录中的接收对象，扮演 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;源文未规定逐条发送在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;源文规定逐条选中记录执行一次发送，因此用 for_each 绑定当前记录元素。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
        &quot;reason&quot;: &quot;先从当前记录选取 recipient 和 summary 原值，属于字段选择转换，且不生成摘要或改写。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;随后把同一记录的接收对象和 summary 参数发送给 notify.send，构成对外发送的 net_send 效果。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
    ],
    &quot;roles&quot;: [
      &quot;transformer&quot;,
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;源文未规定逐条发送在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;源文规定逐条选中记录执行一次发送，因此用 for_each 绑定当前记录元素。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;record&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;明确选取当前记录的 recipient 字段原值作为接收对象。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;record_recipient&quot;,
      &quot;path&quot;: [
        &quot;recipient&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
          &quot;reason&quot;: &quot;明确选取当前记录的 summary 字段原值作为 body，不生成摘要。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Selecting an explicit field with select_part preserves that exact part&quot;,
          &quot;reason&quot;: &quot;源文要求取原值，因此使用 select_part 保持字段值不变。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;record_summary&quot;,
      &quot;path&quot;: [
        &quot;summary&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;将同一记录的接收对象和 summary 原值作为请求参数发送给 notify.send；recipient 是参数而不是目标位置本身。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
          &quot;reason&quot;: &quot;在同一元素作用域内选取并发送两个字段，保持它们来自同一记录。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;record_recipient&quot;
        },
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;record_summary&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_notify_send&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_007 · count_processed_records

块：block_004；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_002

IR 输出：0: result_003

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D006 | — | 0: D001 |

入口／出口变化：

- `result: result_003`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count_processed_records&quot;,
          &quot;reason&quot;: &quot;该指令的公开输出是处理条数，绑定到 compute 产生的本地值 processed_count。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;processed_count&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;count_processed_records&quot;,
        &quot;reason&quot;: &quot;该指令是流程运行时执行的计数计算，未指定 LLM 或外部工具参与。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;该指令计算已处理记录条数，属于统计转换，扮演 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;源文未规定计数在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;统计已选记录数量属于 transform 计算；未产生文件或网络边界动作。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;源文未规定计数在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;对已选记录集合计算处理条数，结果依赖输入集合的数量。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;compute only records dependence and never proves a field was forwarded unchanged&quot;,
          &quot;reason&quot;: &quot;计数是统计计算结果，不能用字段选择表示；此处记录对输入集合的依赖。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;processed_count&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

块：block_004；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_009 · write_file

块：block_005；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_003

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D001 | storage: count.txt | storage: count.txt: 未绑定 → D001 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;fs_write&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;本地文件写入由流程运行时执行，未指定 LLM 或外部工具。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;把处理条数写入 count.txt 存储位置，使内容到达存储边界，扮演 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;创建或修改本地文件内容属于 fs_write；该文件写入不自动构成 context_write。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;fs_write&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;把处理条数写入本地 count.txt；源文未说明追加，按写入/替换文件内容建模。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;replace&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_count_txt&quot;
    }
  ]
}</pre>

</details>

## ir_010 · return

块：block_005；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;用户提供的 events.json&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>原标注审计：profile、步骤参数、输出绑定与依据</summary>

<pre>{
  &quot;output_bindings&quot;: [],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通返回是流程运行时的控制返回操作，执行者为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通返回不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通返回不属于所列效果词汇，也不表示用户输出、网络发送或上下文写入。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: []
}</pre>

</details>

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d | opaque |
| D002 | data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a | known_parts |
| D003 | data_759080b2119f28c08b35b09cc7a04c29f8905b313695499e65eeea5e26116042 | opaque |
| D004 | data_8acb5cae833f9574e91c31ad2cbcfed377de7c74c758aed2715c7a7588dbbe63 | known_parts |
| D005 | data_8e797e6d862284eab160a4f794cce400ff18776f3687dee8449c17010f22cdf4 | opaque |
| D006 | data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d | subset_view |

<details><summary>D001：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_13150dd05121beb990fad5dcf5d2fe82eb9b5cc0822fee68b9d3e76c454c159d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D002：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_8acb5cae833f9574e91c31ad2cbcfed377de7c74c758aed2715c7a7588dbbe63&quot;,
        &quot;path&quot;: [
          {
            &quot;kind&quot;: &quot;element&quot;,
            &quot;scope&quot;: &quot;transfer:[\&quot;f62bec93bdcdcf30016bffab7709e8973e5874c9c8748702fbbcb268a8aea550\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
          }
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:用户提供的 events.json&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D003：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_759080b2119f28c08b35b09cc7a04c29f8905b313695499e65eeea5e26116042&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;f62bec93bdcdcf30016bffab7709e8973e5874c9c8748702fbbcb268a8aea550\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;summary&quot;
    ]
  }
}</pre>

</details>

<details><summary>D004：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_8e797e6d862284eab160a4f794cce400ff18776f3687dee8449c17010f22cdf4&quot;,
        &quot;path&quot;: [
          &quot;recipient&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_759080b2119f28c08b35b09cc7a04c29f8905b313695499e65eeea5e26116042&quot;,
        &quot;path&quot;: [
          &quot;summary&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_8acb5cae833f9574e91c31ad2cbcfed377de7c74c758aed2715c7a7588dbbe63&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;f62bec93bdcdcf30016bffab7709e8973e5874c9c8748702fbbcb268a8aea550\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      }
    ]
  }
}</pre>

</details>

<details><summary>D005：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8e797e6d862284eab160a4f794cce400ff18776f3687dee8449c17010f22cdf4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;f62bec93bdcdcf30016bffab7709e8973e5874c9c8748702fbbcb268a8aea550\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;recipient&quot;
    ]
  }
}</pre>

</details>

<details><summary>D006：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;base&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
    &quot;form&quot;: &quot;subset_view&quot;,
    &quot;predicate&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;
  },
  &quot;id&quot;: &quot;data_d9960bce976da02704974ad1032b175c8029f6d017b2c96e4fec611e7f84157d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_003&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_43d511530fe2d88e48a4c6a21fe612d3a5609a48a3b09d361de235d47fde800a&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;__compiled_model_context__&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Boundary properties and defaults: access_scope is task, recipient, shared, or public; retention is task, persistent, or null when a receiving boundary&#x27;s retention is not modeled. Storage and runtime-context locations require non-null retention. A task-internal tool requires supported local execution and task-internal receiving scope; explicitly nonlocal tools use recipient. Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution. Runtime context defaults to task access and task retention; explicit cross-task memory or cross-subject sharing changes the respective property. Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name. Model, remote, and user boundaries default to recipient access, with null retention unless explicit retention is supported. A locally hosted model remains a content-processing recipient. Public access and sharing require source, code, interface, or supported contract evidence. Null retention does not establish no saving, logging, or future reuse; do not invent unmentioned backend persistence. These properties characterize static boundaries, not sensitivity, necessity, risk, or execution success.&quot;,
        &quot;reason&quot;: &quot;程序生成的模型接收边界使用 recipient；未建模保存期限保持 null，不声明服务端不保存。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;源文明确 count.txt 是本地写入文件，属于 storage 位置。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识此文件位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
        &quot;reason&quot;: &quot;未提供跨任务共享、公开或临时清理机制，按文件默认 task 访问和 persistent 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_events_json&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
        &quot;reason&quot;: &quot;源文明确 events.json 是读取的文件输入，属于 storage 位置。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识此文件位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
        &quot;reason&quot;: &quot;未提供跨任务共享、公开或临时清理机制，按文件默认 task 访问和 persistent 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_notify_send&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;notify.send 是把通知内容发送到接收对象的外部边界，属于 remote 位置。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;notify.send&quot;,
        &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识 notify.send 发送端点。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;explicitly nonlocal tools use recipient&quot;,
        &quot;reason&quot;: &quot;该发送端点面向记录中的接收对象，不是任务内部存储，按 recipient 访问范围。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Model, remote, and user boundaries default to recipient access, with null retention unless explicit retention is supported.&quot;,
        &quot;reason&quot;: &quot;未提供远程端保留或保存证据，按 remote 默认 null retention。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 8,
    &quot;data_count&quot;: 6,
    &quot;description_revision&quot;: 3,
    &quot;record_count&quot;: 10
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;c7980df2424f7dbb62f7dedb079cf73e2b1805428befba166b3ccac83f4d7838&quot;,
    &quot;mapping_sha256&quot;: &quot;fed9b1c630f9879634480bfdffc7bd57d1ffcba4f65ad4a8acee436ab4152a27&quot;,
    &quot;raw_sha256&quot;: &quot;af69bb81300e8ff22bb794a04a7098ad4c536197965a0f2f6a581888a1b17608&quot;,
    &quot;sink_boundaries_sha256&quot;: &quot;f958181f5bd4f62248c0756be2635dd42be82f3c2eac3f716716eacd339463fb&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v3&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;c7980df2424f7dbb62f7dedb079cf73e2b1805428befba166b3ccac83f4d7838&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v3&quot;,
    &quot;events&quot;: [
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0,
          &quot;events&quot;,
          1
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_009&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      }
    ],
    &quot;execution_model&quot;: {
      &quot;sha256&quot;: &quot;1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v4&quot;
    },
    &quot;raw_sha256&quot;: &quot;af69bb81300e8ff22bb794a04a7098ad4c536197965a0f2f6a581888a1b17608&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v3&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_txt&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;源文明确 count.txt 是本地写入文件，属于 storage 位置。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count.txt&quot;,
          &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识此文件位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
          &quot;reason&quot;: &quot;未提供跨任务共享、公开或临时清理机制，按文件默认 task 访问和 persistent 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_events_json&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
          &quot;reason&quot;: &quot;源文明确 events.json 是读取的文件输入，属于 storage 位置。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识此文件位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
          &quot;reason&quot;: &quot;未提供跨任务共享、公开或临时清理机制，按文件默认 task 访问和 persistent 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_notify_send&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;notify.send 是把通知内容发送到接收对象的外部边界，属于 remote 位置。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;notify.send&quot;,
          &quot;reason&quot;: &quot;该 IR 的输入 external_resource 标识 notify.send 发送端点。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;explicitly nonlocal tools use recipient&quot;,
          &quot;reason&quot;: &quot;该发送端点面向记录中的接收对象，不是任务内部存储，按 recipient 访问范围。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Model, remote, and user boundaries default to recipient access, with null retention unless explicit retention is supported.&quot;,
          &quot;reason&quot;: &quot;未提供远程端保留或保存证据，按 remote 默认 null retention。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_count_txt&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;count.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_009&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;loc_events_json&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;用户提供的 events.json&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;loc_notify_send&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;remote&quot;,
        &quot;name&quot;: &quot;notify.send&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_005&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;profiles&quot;: {
      &quot;ir_001&quot;: {
        &quot;effects&quot;: [
          &quot;fs_read&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;read_file&quot;,
            &quot;reason&quot;: &quot;该指令为本地文件读取操作，执行主体是流程运行时 agent_runtime；源文未指定模型或外部工具参与。&quot;,
            &quot;ref_id&quot;: &quot;g_0009&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
            &quot;reason&quot;: &quot;该指令从外部文件引入事件记录到当前流程，扮演数据引入的 source 角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read_file&quot;,
            &quot;reason&quot;: &quot;读取事件文件内容属于 fs_read；未发生网络发送、用户输出或上下文写入。&quot;,
            &quot;ref_id&quot;: &quot;g_0009&quot;,
            &quot;value&quot;: &quot;fs_read&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;
        ]
      },
      &quot;ir_002&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_003&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;select_notifiable_events&quot;,
            &quot;reason&quot;: &quot;该指令是流程运行时执行的记录筛选，未指定 LLM 或外部工具参与。&quot;,
            &quot;ref_id&quot;: &quot;g_0015&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;该指令按条件挑选记录并改变集合组成，扮演 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;条件筛选属于 transform；未产生文件、网络或用户输出边界效果。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transform&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: [
          &quot;transformer&quot;
        ]
      },
      &quot;ir_004&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_005&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;,
          &quot;net_send&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;流程运行时按选中记录组织并调用 notify.send，传入接收对象和 body 参数，故 agent_runtime 参与执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;notify.send 是实际执行发送的工具/端点，故 tool 参与执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;reason&quot;: &quot;该指令从每条记录中选取 recipient 与 summary 字段并组织成通知参数，属于选择/转换，扮演 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;该指令使通知内容到达记录中的接收对象，扮演 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;reason&quot;: &quot;先从当前记录选取 recipient 和 summary 原值，属于字段选择转换，且不生成摘要或改写。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transform&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 1,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;随后把同一记录的接收对象和 summary 参数发送给 notify.send，构成对外发送的 net_send 效果。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;net_send&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;transformer&quot;,
          &quot;sink&quot;
        ]
      },
      &quot;ir_006&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;count_processed_records&quot;,
            &quot;reason&quot;: &quot;该指令是流程运行时执行的计数计算，未指定 LLM 或外部工具参与。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;该指令计算已处理记录条数，属于统计转换，扮演 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;统计已选记录数量属于 transform 计算；未产生文件或网络边界动作。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transform&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: [
          &quot;transformer&quot;
        ]
      },
      &quot;ir_008&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是流程运行时的控制转移指令，执行者为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制转移不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只改变后续控制流，不属于所列效果词汇；控制转移本身保持在该词汇边界之外。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_009&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;本地文件写入由流程运行时执行，未指定 LLM 或外部工具。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;把处理条数写入 count.txt 存储位置，使内容到达存储边界，扮演 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;创建或修改本地文件内容属于 fs_write；该文件写入不自动构成 context_write。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;fs_write&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: [
          &quot;sink&quot;
        ]
      },
      &quot;ir_010&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通返回是流程运行时的控制返回操作，执行者为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通返回不引入、不输出也不转换内容，因此没有适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通返回不属于所列效果词汇，也不表示用户输出、网络发送或上下文写入。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      }
    },
    &quot;transfer_specs&quot;: {
      &quot;ir_001&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
                        &quot;reason&quot;: &quot;读取整个 events.json 文件内容；源文没有字段级接口或只读取特定字段的机制，故保留整个文件读取范围。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_events_json&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;events_raw&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;源文未规定本地隔离、限定回传或模型处理接口，读取事件文件的处理按 default 模式分析。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;read_file&quot;,
                &quot;reason&quot;: &quot;该指令的公开输出是读取结果，直接绑定到刚读取的本地值 events_raw。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;events_raw&quot;
            }
          }
        ]
      },
      &quot;ir_002&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_003&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                        &quot;reason&quot;: &quot;按源文给出的布尔与数值条件筛选记录，保留选中元素本身不变；未执行额外摘要或改写。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
                        &quot;reason&quot;: &quot;该操作对应带谓词的集合筛选，保留每个选中元素的原值。&quot;,
                        &quot;ref_id&quot;: &quot;EM11&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;filter_items&quot;,
                    &quot;output&quot;: &quot;selected_records&quot;,
                    &quot;predicate&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;源文未规定筛选在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;select_notifiable_events&quot;,
                &quot;reason&quot;: &quot;该指令的公开输出是筛选后的记录集合，绑定到 filter_items 产生的本地值 selected_records。&quot;,
                &quot;ref_id&quot;: &quot;g_0015&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;selected_records&quot;
            }
          }
        ]
      },
      &quot;ir_004&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_005&quot;: {
        &quot;events&quot;: [
          {
            &quot;body&quot;: [
              {
                &quot;events&quot;: [
                  {
                    &quot;atomic_ops&quot;: [
                      {
                        &quot;evidences&quot;: [
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段。&quot;,
                            &quot;reason&quot;: &quot;明确选取当前记录的 recipient 字段原值作为接收对象。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;record_recipient&quot;,
                        &quot;path&quot;: [
                          &quot;recipient&quot;
                        ]
                      },
                      {
                        &quot;evidences&quot;: [
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                            &quot;reason&quot;: &quot;明确选取当前记录的 summary 字段原值作为 body，不生成摘要。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;Selecting an explicit field with select_part preserves that exact part&quot;,
                            &quot;reason&quot;: &quot;源文要求取原值，因此使用 select_part 保持字段值不变。&quot;,
                            &quot;ref_id&quot;: &quot;EM11&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;record_summary&quot;,
                        &quot;path&quot;: [
                          &quot;summary&quot;
                        ]
                      }
                    ],
                    &quot;effect_index&quot;: 0
                  },
                  {
                    &quot;atomic_ops&quot;: [
                      {
                        &quot;evidences&quot;: [
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                            &quot;reason&quot;: &quot;将同一记录的接收对象和 summary 原值作为请求参数发送给 notify.send；recipient 是参数而不是目标位置本身。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
                            &quot;reason&quot;: &quot;在同一元素作用域内选取并发送两个字段，保持它们来自同一记录。&quot;,
                            &quot;ref_id&quot;: &quot;EM11&quot;
                          }
                        ],
                        &quot;inputs&quot;: [
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;record_recipient&quot;
                          },
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;record_summary&quot;
                          }
                        ],
                        &quot;op&quot;: &quot;deliver&quot;,
                        &quot;target&quot;: &quot;loc_notify_send&quot;
                      }
                    ],
                    &quot;effect_index&quot;: 1
                  }
                ],
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                    &quot;reason&quot;: &quot;源文未规定逐条发送在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
                    &quot;ref_id&quot;: &quot;EM10&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                    &quot;reason&quot;: &quot;源文规定逐条选中记录执行一次发送，因此用 for_each 绑定当前记录元素。&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;
                  }
                ],
                &quot;kind&quot;: &quot;processing&quot;,
                &quot;mode&quot;: &quot;default&quot;,
                &quot;returns&quot;: []
              }
            ],
            &quot;collection&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                &quot;reason&quot;: &quot;源文明确逐条处理选中记录，因此该 IR 的发送事件用 for_each 作用域表达。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
                &quot;reason&quot;: &quot;该作用域保证 recipient 与 summary 的字段选择来自同一记录元素。&quot;,
                &quot;ref_id&quot;: &quot;EM11&quot;
              }
            ],
            &quot;item&quot;: &quot;record&quot;,
            &quot;kind&quot;: &quot;for_each&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
                        &quot;reason&quot;: &quot;对已选记录集合计算处理条数，结果依赖输入集合的数量。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;compute only records dependence and never proves a field was forwarded unchanged&quot;,
                        &quot;reason&quot;: &quot;计数是统计计算结果，不能用字段选择表示；此处记录对输入集合的依赖。&quot;,
                        &quot;ref_id&quot;: &quot;EM11&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;processed_count&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;源文未规定计数在隔离本地执行或由模型处理，按 default 模式分析。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;count_processed_records&quot;,
                &quot;reason&quot;: &quot;该指令的公开输出是处理条数，绑定到 compute 产生的本地值 processed_count。&quot;,
                &quot;ref_id&quot;: &quot;g_0027&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;processed_count&quot;
            }
          }
        ]
      },
      &quot;ir_008&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_009&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
                        &quot;reason&quot;: &quot;把处理条数写入本地 count.txt；源文未说明追加，按写入/替换文件内容建模。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;replace&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_count_txt&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
                &quot;reason&quot;: &quot;该段是本地文件写入，不是模型处理或隔离本地处理，按 default 模式记录写入效果。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_010&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      }
    }
  }
}</pre>

</details>

