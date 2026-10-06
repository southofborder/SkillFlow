# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v5`；SHA-256：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

求解状态：`complete`。

IR 记录覆盖：10 / 10。

[本地可视化审查](report.html) · [唯一业务结果](../doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。标为“控制”的槽只决定字段加入或观察是否发生，不属于该交付的载荷。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](../audit/material.json)（execution_model）；逐项依据在下方审计区展开。

## 接收与保存边界

纳入清单 6 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。

等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。

| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |
|---|---|---|---|---|---|
| ir_001 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_003 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.候选组1.1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 同一元素 D006；0: D006 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.候选组1.3.1 | 纳入 | external_tool / 2 | loc_notify_send · tool: notify.send · recipient / 未建模期限 | 同一元素 D006；0: D005; 1: D003 | 另一接收主体或跨主体共享；source/src_003, execution_model/EM12, execution_model/EM06 |
| ir_007 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D004 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_009 / 1.1 | 纳入 | storage_write / 1 | loc_count_file · storage: count.txt · task / persistent | 0: D001 | 任务内部、跨任务留存；source/src_003, execution_model/EM12 |

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
| 1.1 | fs_read | read | — | storage: events.json | 0: D002 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
          &quot;quote&quot;: &quot;result_001&quot;,
          &quot;reason&quot;: &quot;CFG 公开结果 result_001 绑定为读取得到的整体内容符号值，属未改动转发。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;events_content&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;源文规定由本流程读取该文件，执行者是本地 agent 运行时；未提及模型、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;读取把用户提供文件的内容引入当前流程，构成 source 角色；按 EM01 保留该文件整体为可能的获取范围。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;读取本地文件内容属于 fs_read；没有网络接收或直接用户输出证据。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_file&quot;,
        &quot;reason&quot;: &quot;CFG 指令操作码为 read_file，与源文读取步骤一致。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;源文只规定读取该文件；未规定模型处理，也未规定本地隔离执行及其限定回传边界，因此按默认模式声明该处理边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
        &quot;reason&quot;: &quot;对已存在的读取动作，默认规则只提供可能的分析事件，不虚构额外的获取或保护动作；获取版本的后续观察由编译器按模式编译。&quot;,
        &quot;ref_id&quot;: &quot;EM05&quot;,
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
          &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;读取对象是源文指定的用户提供文件，目标值为其内容符号值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
          &quot;reason&quot;: &quot;没有显式接口或机制限制读取或返回内容，按 EM01 保留该文件整体为可能的获取范围，不假设键级读取。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_events_file&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;events_content&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;源文只规定读取该文件；未规定模型处理，也未规定本地隔离执行及其限定回传边界，因此按默认模式声明该处理边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
          &quot;reason&quot;: &quot;对已存在的读取动作，默认规则只提供可能的分析事件，不虚构额外的获取或保护动作；获取版本的后续观察由编译器按模式编译。&quot;,
          &quot;ref_id&quot;: &quot;EM05&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;events_content&quot;
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
| 2.1 | transform | filter_items | 0: D002 | — | 0: D004 |

入口／出口变化：

- `result: result_002`：未绑定 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
          &quot;quote&quot;: &quot;result_002&quot;,
          &quot;reason&quot;: &quot;CFG 公开结果 result_002 绑定筛选输出。&quot;,
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
        &quot;reason&quot;: &quot;筛选指令由本地 agent 运行时的流程执行；源文未提及模型或人工参与选择。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;按条件从集合中选择记录属于对内容的处理，构成 transformer；选中记录本身保持原样。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;源文给出显式逐条筛选条件且不要求改写记录；未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
        &quot;reason&quot;: &quot;默认规则只对已存在动作提供可能的分析事件，不把筛选谓词变成额外的保护动作。&quot;,
        &quot;ref_id&quot;: &quot;EM05&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Selection, masking, encryption, and summarization use transform when supported&quot;,
        &quot;reason&quot;: &quot;条件筛选属于选择类处理，按 EM04 记为 transform。&quot;,
        &quot;ref_id&quot;: &quot;EM04&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;选中该记录&quot;,
        &quot;reason&quot;: &quot;源文明确按条件选中记录，对应效应词汇表中的选择类处理。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
          &quot;reason&quot;: &quot;源文给出显式逐条筛选条件且不要求改写记录；未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
          &quot;reason&quot;: &quot;默认规则只对已存在动作提供可能的分析事件，不把筛选谓词变成额外的保护动作。&quot;,
          &quot;ref_id&quot;: &quot;EM05&quot;
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
          &quot;reason&quot;: &quot;谓词取自源文条件；选中的记录元素保持原样，未选中的元素保持排除，未改写任何记录内容。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
          &quot;reason&quot;: &quot;说明谓词中 opted_out 条件与 urgent/value 门槛的关系：urgent 不豁免 opted_out，条件保持合取。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
          &quot;reason&quot;: &quot;按 EM11 用 filter_items 表示元素筛选，静态分析只记录谓词而不执行它。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;filter_items&quot;,
      &quot;output&quot;: &quot;selected_records&quot;,
      &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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

块：block_003；执行主体：agent_runtime, tool；角色：sink, transformer。

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

逐元素作用域 1：集合候选 D004。以下各候选组单独绑定同一个元素，不能跨组组合参数；不是实际执行次数。

- 候选组 1：集合 D004 → 元素 D006。

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.候选组1.1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 1.候选组1.2.1 | transform | select_part | 0: D006 | — | 0: D005 |
| 1.候选组1.2.2 | transform | select_part | 0: D006 | — | 0: D003 |
| 1.候选组1.3.1 | 无标签数据操作 | deliver | 0: D005; 1: D003 | tool: notify.send | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send&quot;,
        &quot;reason&quot;: &quot;逐条构造并发出工具调用由本地 agent 运行时执行；源文未提及模型参与。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;调用一次 notify.send&quot;,
        &quot;reason&quot;: &quot;notify.send 是执行通知发送动作的工具执行者，工具名称保留在 IR 与位置名称中。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;内容经该调用送达接收对象，构成 sink 角色；没有网络传输机制证据，按 EM13 以工具边界表示而不是 net_send。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
        &quot;reason&quot;: &quot;逐条记录选取 recipient 与 summary 字段构造请求参数，属于对内容的处理与选择，构成 transformer；取值保持原值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
        &quot;reason&quot;: &quot;逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
        &quot;reason&quot;: &quot;默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。&quot;,
        &quot;ref_id&quot;: &quot;EM05&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
        &quot;reason&quot;: &quot;选取已有字段用于请求参数属于选择类处理；投递本身在无网络证据下由零效应 deliver 表示，不并入 net_send。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Selection, masking, encryption, and summarization use transform when supported&quot;,
        &quot;reason&quot;: &quot;逐条字段选择按 EM04 记为 transform。&quot;,
        &quot;ref_id&quot;: &quot;EM04&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
          &quot;reason&quot;: &quot;逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
          &quot;reason&quot;: &quot;默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。&quot;,
          &quot;ref_id&quot;: &quot;EM05&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_record&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
          &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;recipient_value&quot;,
      &quot;path&quot;: [
        &quot;recipient&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
          &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;summary_value&quot;,
      &quot;path&quot;: [
        &quot;summary&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
          &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;,
          &quot;ref_id&quot;: &quot;EM13&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
          &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
          &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;,
          &quot;ref_id&quot;: &quot;EM05&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;recipient_value&quot;
        },
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;summary_value&quot;
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D004 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D004 | — | 0: D001 |

入口／出口变化：

- `result: result_003`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
          &quot;quote&quot;: &quot;result_003&quot;,
          &quot;reason&quot;: &quot;CFG 公开结果 result_003 绑定计数计算输出。&quot;,
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
        &quot;reason&quot;: &quot;计数步骤在流程内由本地 agent 运行时执行；无模型或人工执行证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;reason&quot;: &quot;由已选记录集合计算处理条数属于内容计算，构成 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;reason&quot;: &quot;源文要求统计处理条数；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
        &quot;reason&quot;: &quot;默认规则只对已有计数动作给出可能的分析事件，不虚构额外外部来源。&quot;,
        &quot;ref_id&quot;: &quot;EM05&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;count_processed_records&quot;,
        &quot;reason&quot;: &quot;计数是计算操作，按效应词汇表记为 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;处理条数&quot;,
        &quot;reason&quot;: &quot;源文要求得到处理条数，对应计算类处理。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
          &quot;reason&quot;: &quot;源文要求统计处理条数；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
          &quot;reason&quot;: &quot;默认规则只对已有计数动作给出可能的分析事件，不虚构额外外部来源。&quot;,
          &quot;ref_id&quot;: &quot;EM05&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count_processed_records&quot;,
          &quot;reason&quot;: &quot;指令对输入集合计数，结果由该集合派生；计数为不透明计算，只声明依赖。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理条数&quot;,
          &quot;reason&quot;: &quot;源文要求得到处理条数，来源为该流程已选中并处理的记录集合。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;write_file&quot;,
        &quot;reason&quot;: &quot;写文件动作由本地 agent 运行时执行；无模型或人工写入证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;reason&quot;: &quot;内容到达本地存储位置，构成 sink 角色；写入值为计数结果原值，无额外转换。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;reason&quot;: &quot;创建或修改本地文件内容属于 fs_write；文件写入不自动附加 context_write。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;fs_write&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write_file&quot;,
        &quot;reason&quot;: &quot;CFG 写文件操作码支持 fs_write 标注。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
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
          &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
          &quot;reason&quot;: &quot;写入目标为本地 count.txt，写入内容为当前指令的条数操作数；源文未说明追加语义，按一次写入（替换）表示；文件写入不自动附加 context_write。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;write_file&quot;,
          &quot;reason&quot;: &quot;CFG 操作码为 write_file，与源文写入步骤一致。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;replace&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_count_file&quot;
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
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;events.json&quot;
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
        &quot;reason&quot;: &quot;返回终结由本地 agent 运行时执行控制流结束。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;该终结指令没有 CFG 输入和公开输出，不引入、处理或外送内容，因此没有可适用的角色标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通返回不构成用户输出或任何交付；不虚构 user_output、网络投递或其他效应标签。&quot;,
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
| D001 | data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d | opaque |
| D002 | data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7 | known_parts |
| D003 | data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b | opaque |
| D004 | data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc | subset_view |
| D005 | data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c | opaque |
| D006 | data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a | known_parts |

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
  &quot;id&quot;: &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
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
        &quot;data&quot;: &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;,
        &quot;path&quot;: [
          {
            &quot;kind&quot;: &quot;element&quot;,
            &quot;scope&quot;: &quot;transfer:[\&quot;af8576ecf9827310e8a3d2d7b77fc57186203fee50f78bf643425d95ceea55c8\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
          }
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:events.json&quot;,
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
  &quot;id&quot;: &quot;data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af8576ecf9827310e8a3d2d7b77fc57186203fee50f78bf643425d95ceea55c8\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
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
    &quot;base&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
    &quot;form&quot;: &quot;subset_view&quot;,
    &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;
  },
  &quot;id&quot;: &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_003&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af8576ecf9827310e8a3d2d7b77fc57186203fee50f78bf643425d95ceea55c8\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c&quot;,
        &quot;path&quot;: [
          &quot;recipient&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b&quot;,
        &quot;path&quot;: [
          &quot;summary&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af8576ecf9827310e8a3d2d7b77fc57186203fee50f78bf643425d95ceea55c8\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      }
    ]
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;__compiled_model_context__&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
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
    &quot;loc_count_file&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;reason&quot;: &quot;源文指定本地 count.txt 为写入目标，构成具体文件资源身份。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
        &quot;reason&quot;: &quot;本地文件采用默认 task 访问与 persistent 保留；没有临时使用与清理机制证据。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_events_file&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;源文明确该文件为用户提供的事件文件并被读取，构成具体文件资源身份。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
        &quot;reason&quot;: &quot;源文未说明临时使用与清理机制或跨任务共享，按 EM12 文件默认取 task 访问与 persistent 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_notify_send&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;源文指定调用工具 notify.send 并给出接收对象，构成工具投递边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
        &quot;reason&quot;: &quot;源文未说明该工具的部署与传输机制，按 EM12 对未说明部署的工具保留外部接收方可能性，访问范围取 recipient、保留为 null，不虚构网络效应。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
        &quot;reason&quot;: &quot;工具名中的 send 一词不构成网络通信机制证据，因此该位置按工具边界而非 remote 建模。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;
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
    &quot;compiled_sha256&quot;: &quot;4e0485bde6394b241fd9a8444d1a012ddc95e3c44887d29d0a4823f8046d7b85&quot;,
    &quot;mapping_sha256&quot;: &quot;036b1d5bfe71e4e4d82579de64b06495c98761755b73abc6437d9271a9627ea8&quot;,
    &quot;raw_sha256&quot;: &quot;d304fe6a3a6d8aac92a4e44a1e8e2a7c7c540efb307049992071d3d9fb013a13&quot;,
    &quot;sink_boundaries_sha256&quot;: &quot;0e9d8b1f1168565d87fa2cf986d449ff2bc4e96e69f5e6361722819fe2ec1a6a&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v4&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;4e0485bde6394b241fd9a8444d1a012ddc95e3c44887d29d0a4823f8046d7b85&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v4&quot;,
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
      &quot;sha256&quot;: &quot;d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v5&quot;
    },
    &quot;raw_sha256&quot;: &quot;d304fe6a3a6d8aac92a4e44a1e8e2a7c7c540efb307049992071d3d9fb013a13&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v4&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_file&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
          &quot;reason&quot;: &quot;源文指定本地 count.txt 为写入目标，构成具体文件资源身份。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
          &quot;reason&quot;: &quot;本地文件采用默认 task 访问与 persistent 保留；没有临时使用与清理机制证据。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_events_file&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;源文明确该文件为用户提供的事件文件并被读取，构成具体文件资源身份。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
          &quot;reason&quot;: &quot;源文未说明临时使用与清理机制或跨任务共享，按 EM12 文件默认取 task 访问与 persistent 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_notify_send&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;源文指定调用工具 notify.send 并给出接收对象，构成工具投递边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
          &quot;reason&quot;: &quot;源文未说明该工具的部署与传输机制，按 EM12 对未说明部署的工具保留外部接收方可能性，访问范围取 recipient、保留为 null，不虚构网络效应。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
          &quot;reason&quot;: &quot;工具名中的 send 一词不构成网络通信机制证据，因此该位置按工具边界而非 remote 建模。&quot;,
          &quot;ref_id&quot;: &quot;EM06&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_count_file&quot;: {
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
      &quot;loc_events_file&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;events.json&quot;,
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
        &quot;kind&quot;: &quot;tool&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;reason&quot;: &quot;源文规定由本流程读取该文件，执行者是本地 agent 运行时；未提及模型、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;reason&quot;: &quot;读取把用户提供文件的内容引入当前流程，构成 source 角色；按 EM01 保留该文件整体为可能的获取范围。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;reason&quot;: &quot;读取本地文件内容属于 fs_read；没有网络接收或直接用户输出证据。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;fs_read&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read_file&quot;,
            &quot;reason&quot;: &quot;CFG 指令操作码为 read_file，与源文读取步骤一致。&quot;,
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
            &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
            &quot;reason&quot;: &quot;筛选指令由本地 agent 运行时的流程执行；源文未提及模型或人工参与选择。&quot;,
            &quot;ref_id&quot;: &quot;g_0015&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;按条件从集合中选择记录属于对内容的处理，构成 transformer；选中记录本身保持原样。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Selection, masking, encryption, and summarization use transform when supported&quot;,
            &quot;reason&quot;: &quot;条件筛选属于选择类处理，按 EM04 记为 transform。&quot;,
            &quot;ref_id&quot;: &quot;EM04&quot;,
            &quot;value&quot;: &quot;transform&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;选中该记录&quot;,
            &quot;reason&quot;: &quot;源文明确按条件选中记录，对应效应词汇表中的选择类处理。&quot;,
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
            &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send&quot;,
            &quot;reason&quot;: &quot;逐条构造并发出工具调用由本地 agent 运行时执行；源文未提及模型参与。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;调用一次 notify.send&quot;,
            &quot;reason&quot;: &quot;notify.send 是执行通知发送动作的工具执行者，工具名称保留在 IR 与位置名称中。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;内容经该调用送达接收对象，构成 sink 角色；没有网络传输机制证据，按 EM13 以工具边界表示而不是 net_send。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;reason&quot;: &quot;逐条记录选取 recipient 与 summary 字段构造请求参数，属于对内容的处理与选择，构成 transformer；取值保持原值。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
            &quot;reason&quot;: &quot;选取已有字段用于请求参数属于选择类处理；投递本身在无网络证据下由零效应 deliver 表示，不并入 net_send。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transform&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Selection, masking, encryption, and summarization use transform when supported&quot;,
            &quot;reason&quot;: &quot;逐条字段选择按 EM04 记为 transform。&quot;,
            &quot;ref_id&quot;: &quot;EM04&quot;,
            &quot;value&quot;: &quot;transform&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;sink&quot;,
          &quot;transformer&quot;
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
            &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
            &quot;reason&quot;: &quot;计数步骤在流程内由本地 agent 运行时执行；无模型或人工执行证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;由已选记录集合计算处理条数属于内容计算，构成 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;count_processed_records&quot;,
            &quot;reason&quot;: &quot;计数是计算操作，按效应词汇表记为 transform。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;transform&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;处理条数&quot;,
            &quot;reason&quot;: &quot;源文要求得到处理条数，对应计算类处理。&quot;,
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
            &quot;reason&quot;: &quot;调度指令由本地 agent 运行时执行控制流转移，无模型、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流调度不引入、处理或外送内容，没有可适用的 source、sink 或 transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效应词汇表内，不强制标注 transform，也不表示该指令是无操作。&quot;,
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
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;write_file&quot;,
            &quot;reason&quot;: &quot;写文件动作由本地 agent 运行时执行；无模型或人工写入证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0033&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;内容到达本地存储位置，构成 sink 角色；写入值为计数结果原值，无额外转换。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;创建或修改本地文件内容属于 fs_write；文件写入不自动附加 context_write。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;fs_write&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;write_file&quot;,
            &quot;reason&quot;: &quot;CFG 写文件操作码支持 fs_write 标注。&quot;,
            &quot;ref_id&quot;: &quot;g_0033&quot;,
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
            &quot;reason&quot;: &quot;返回终结由本地 agent 运行时执行控制流结束。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;该终结指令没有 CFG 输入和公开输出，不引入、处理或外送内容，因此没有可适用的角色标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通返回不构成用户输出或任何交付；不虚构 user_output、网络投递或其他效应标签。&quot;,
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
                        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
                        &quot;reason&quot;: &quot;读取对象是源文指定的用户提供文件，目标值为其内容符号值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
                        &quot;reason&quot;: &quot;没有显式接口或机制限制读取或返回内容，按 EM01 保留该文件整体为可能的获取范围，不假设键级读取。&quot;,
                        &quot;ref_id&quot;: &quot;EM01&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_events_file&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;events_content&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
                &quot;reason&quot;: &quot;源文只规定读取该文件；未规定模型处理，也未规定本地隔离执行及其限定回传边界，因此按默认模式声明该处理边界。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                &quot;reason&quot;: &quot;对已存在的读取动作，默认规则只提供可能的分析事件，不虚构额外的获取或保护动作；获取版本的后续观察由编译器按模式编译。&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;
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
                &quot;quote&quot;: &quot;result_001&quot;,
                &quot;reason&quot;: &quot;CFG 公开结果 result_001 绑定为读取得到的整体内容符号值，属未改动转发。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;events_content&quot;
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
                        &quot;reason&quot;: &quot;谓词取自源文条件；选中的记录元素保持原样，未选中的元素保持排除，未改写任何记录内容。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
                        &quot;reason&quot;: &quot;说明谓词中 opted_out 条件与 urgent/value 门槛的关系：urgent 不豁免 opted_out，条件保持合取。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
                        &quot;reason&quot;: &quot;按 EM11 用 filter_items 表示元素筛选，静态分析只记录谓词而不执行它。&quot;,
                        &quot;ref_id&quot;: &quot;EM11&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;filter_items&quot;,
                    &quot;output&quot;: &quot;selected_records&quot;,
                    &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                &quot;reason&quot;: &quot;源文给出显式逐条筛选条件且不要求改写记录；未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                &quot;reason&quot;: &quot;默认规则只对已存在动作提供可能的分析事件，不把筛选谓词变成额外的保护动作。&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;
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
                &quot;quote&quot;: &quot;result_002&quot;,
                &quot;reason&quot;: &quot;CFG 公开结果 result_002 绑定筛选输出。&quot;,
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
                            &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
                            &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;event_record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;recipient_value&quot;,
                        &quot;path&quot;: [
                          &quot;recipient&quot;
                        ]
                      },
                      {
                        &quot;evidences&quot;: [
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                            &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;event_record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;summary_value&quot;,
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
                            &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                            &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;,
                            &quot;ref_id&quot;: &quot;EM13&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
                            &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
                            &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;,
                            &quot;ref_id&quot;: &quot;EM05&quot;
                          }
                        ],
                        &quot;inputs&quot;: [
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;recipient_value&quot;
                          },
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;summary_value&quot;
                          }
                        ],
                        &quot;op&quot;: &quot;deliver&quot;,
                        &quot;target&quot;: &quot;loc_notify_send&quot;
                      }
                    ],
                    &quot;effect_index&quot;: null
                  }
                ],
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                    &quot;reason&quot;: &quot;逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                    &quot;reason&quot;: &quot;默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。&quot;,
                    &quot;ref_id&quot;: &quot;EM05&quot;
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
                &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send&quot;,
                &quot;reason&quot;: &quot;源文规定对已选记录逐条调用一次，按逐元素作用域建模，并在每次处理中保持同一记录的元素身份。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
                &quot;reason&quot;: &quot;用共享元素绑定保证接收对象与正文选择来自同一条记录；这是分析作用域，不是虚构的 CFG 循环或测量出的调用次数。&quot;,
                &quot;ref_id&quot;: &quot;EM11&quot;
              }
            ],
            &quot;item&quot;: &quot;event_record&quot;,
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
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;count_processed_records&quot;,
                        &quot;reason&quot;: &quot;指令对输入集合计数，结果由该集合派生；计数为不透明计算，只声明依赖。&quot;,
                        &quot;ref_id&quot;: &quot;g_0027&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;处理条数&quot;,
                        &quot;reason&quot;: &quot;源文要求得到处理条数，来源为该流程已选中并处理的记录集合。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
                &quot;reason&quot;: &quot;源文要求统计处理条数；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                &quot;reason&quot;: &quot;默认规则只对已有计数动作给出可能的分析事件，不虚构额外外部来源。&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;
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
                &quot;quote&quot;: &quot;result_003&quot;,
                &quot;reason&quot;: &quot;CFG 公开结果 result_003 绑定计数计算输出。&quot;,
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
                        &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
                        &quot;reason&quot;: &quot;写入目标为本地 count.txt，写入内容为当前指令的条数操作数；源文未说明追加语义，按一次写入（替换）表示；文件写入不自动附加 context_write。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;write_file&quot;,
                        &quot;reason&quot;: &quot;CFG 操作码为 write_file，与源文写入步骤一致。&quot;,
                        &quot;ref_id&quot;: &quot;g_0033&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;replace&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_count_file&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
                &quot;reason&quot;: &quot;源文规定把条数写入本地文件；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                &quot;reason&quot;: &quot;默认规则只对已有写入动作提供可能的分析事件，不虚构额外保护动作。&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;
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

