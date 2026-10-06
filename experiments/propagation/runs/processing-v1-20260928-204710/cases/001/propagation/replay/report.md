# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；没有未决项或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v2`；SHA-256：`12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。

求解状态：`complete`。

IR 记录覆盖：10 / 10。

[本地可视化审查](report.html) · [唯一业务结果](../doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](../audit/material.json)（execution_model）；逐项依据在下方审计区展开。

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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: 用户提供的 events.json | 0: D001 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D001 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;quote&quot;: &quot;event_records&quot;,
          &quot;reason&quot;: &quot;输出语义名为 event_records，绑定刚读取的整份文件内容，未做字段级替换。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_records&quot;
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
        &quot;reason&quot;: &quot;源文第1步要求读取用户提供的文件，属流程内本地动作，执行主体标注为 agent_runtime；源文未提及模型参与该读取。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
        &quot;reason&quot;: &quot;读取把该文件当前内容整体引入当前流程，充当 source；内容包含记录的全部字段，未做字段级加工。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_file&quot;,
        &quot;reason&quot;: &quot;该 IR 的 opcode 值为 read_file 且输入为文件资源，产生对文件内容的读取效果 fs_read。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;源文只规定读取该文件，没有规定模型处理，也没有隔离执行与受限回传机制，故按默认模式编译，returns 为空。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;For content acquired for the agent&#x27;s natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version.&quot;,
        &quot;reason&quot;: &quot;EM03：读取所得版本在无显式隔离或受限路由时保留被模型观察的可能；这是契约默认，不是实测事件。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read_file&quot;,
          &quot;reason&quot;: &quot;该 IR 的 opcode 值为 read_file，输入为文件资源，执行对文件内容的读取。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
          &quot;reason&quot;: &quot;EM01：未见键限定接口或机制限制，获取范围保留为文件整体内容，不用单个字段替代来源整体。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_events_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;event_records&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;源文只规定读取该文件，没有规定模型处理，也没有隔离执行与受限回传机制，故按默认模式编译，returns 为空。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;For content acquired for the agent&#x27;s natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version.&quot;,
          &quot;reason&quot;: &quot;EM03：读取所得版本在无显式隔离或受限路由时保留被模型观察的可能；这是契约默认，不是实测事件。&quot;,
          &quot;ref_id&quot;: &quot;EM03&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_records&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的 source/sink/transformer 角色标签，故为空。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只做控制流转移，不读取、不写入、不发送、不转换内容；词表内无适用效果，但控制转移本身仍影响后续执行顺序。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D001 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | filter_items | 0: D001 | — | 0: D002 |

入口／出口变化：

- `result: result_002`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;quote&quot;: &quot;selected_records&quot;,
          &quot;reason&quot;: &quot;该 IR 输出语义名为 selected_records，绑定筛选得到的记录集合。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;筛选步骤属于流程内的本地处理，源文与 CFG 均未指明模型执行，执行主体标注为 agent_runtime。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;该动作按条件处理输入记录集合并筛出子集，属 transformer；未把内容外发或写入存储。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;reason&quot;: &quot;源文给出筛选条件，但未规定模型执行，也未规定隔离执行与受限回传机制，因此按默认模式编译，returns 为空。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;EM10：默认模式下，筛选所依据的读取输出保留被模型观察的可能；本段未声称存在局部隔离。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;选中该记录&quot;,
        &quot;reason&quot;: &quot;按条件从集合中挑选元素属于选择/过滤类处理，词表下记 transform；被选中元素本身保持不变。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
          &quot;reason&quot;: &quot;源文给出筛选条件，但未规定模型执行，也未规定隔离执行与受限回传机制，因此按默认模式编译，returns 为空。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;EM10：默认模式下，筛选所依据的读取输出保留被模型观察的可能；本段未声称存在局部隔离。&quot;,
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
          &quot;reason&quot;: &quot;该条件作为筛选谓词记录；静态分析不执行自然语言谓词，只保留选择关系。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
          &quot;reason&quot;: &quot;EM11：筛选保留被选中元素原样，不对元素字段做改写。&quot;,
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身决定后续执行顺序。&quot;,
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

块：block_003；执行主体：agent_runtime, tool；角色：sink。

IR 输入：0: notify.send, 1: result_002, 2: &quot;recipient&quot;, 3: &quot;summary&quot;

IR 输出：[]

逐元素作用域 1：集合候选 D002。以下各候选组单独绑定同一个元素，不能跨组组合参数；不是实际执行次数。

- 候选组 1：集合 D002 → 元素 D006。

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.候选组1.1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 1.候选组1.2.1 | net_send | select_part | 0: D006 | — | 0: D003 |
| 1.候选组1.2.2 | net_send | select_part | 0: D006 | — | 0: D004 |
| 1.候选组1.2.3 | net_send | deliver | 0: D003; 1: D004 | remote: notify.send | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
      &quot;net_send&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;源文要求流程对每条选中记录发起该调用，调用由本地运行流程编排执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;notify.send&quot;,
        &quot;reason&quot;: &quot;该 IR 的外部资源操作数指明具体通知服务 notify.send，实际发送动作由该工具/服务执行；不是仅凭 opcode 名称推断执行主体。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;调用使记录中的 recipient 与 summary 值到达外部接收对象，属 sink；未加入加工角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;逐元素段未见模型处理或局部隔离、受限回传机制，按默认模式编译；returns 为空。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;,
        &quot;reason&quot;: &quot;源文否定摘要生成与格式转换，本段只做字段选择与投递。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;源文明确向记录中的接收对象发送内容，具备通信证据，属远程发送 net_send；发送内容为选中记录的字段值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Model observation, network delivery, and user output are separate boundaries.&quot;,
        &quot;reason&quot;: &quot;EM06：网络投递与用户输出是分开的边界；此处按通信证据只记 net_send，未据此推断用户可见输出。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;逐元素段未见模型处理或局部隔离、受限回传机制，按默认模式编译；returns 为空。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;,
          &quot;reason&quot;: &quot;源文否定摘要生成与格式转换，本段只做字段选择与投递。&quot;,
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
          &quot;reason&quot;: &quot;源文明确接收对象取当前记录的 recipient 字段，属于对同一元素的显式字段选取。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
          &quot;reason&quot;: &quot;EM11：在同一元素绑定上选择字段，保证 recipient 与 summary 来自同一条记录。&quot;,
          &quot;ref_id&quot;: &quot;EM11&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
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
          &quot;reason&quot;: &quot;源文明确 body 参数直接取 summary 原值，是字段选择而非摘要生成或内容改写。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
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
          &quot;reason&quot;: &quot;投递实参仅为同一条记录选出的 recipient 与 summary，顺序对应接收对象与 body；未加入 access_token 等其它字段。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
          &quot;reason&quot;: &quot;该禁止限定投递内容不得包含 access_token；这里只记录实际绑定的两个值，没有把禁止项当成已执行的防护动作。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;delivery must retain actual selected values, input order, result identities, and explicit prohibitions&quot;,
          &quot;reason&quot;: &quot;EM06：投递需保留实际选中的值与明确禁止项，参数范围不因容器整体被保留而扩大。&quot;,
          &quot;ref_id&quot;: &quot;EM06&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D002 | — | 0: D005 |

入口／出口变化：

- `result: result_003`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;quote&quot;: &quot;processed_count&quot;,
          &quot;reason&quot;: &quot;该 IR 输出语义名为 processed_count，绑定本段计算得到的计数值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;源文把处理条数作为流程内部产出的数值，未见模型处理说明；该统计由 agent_runtime 在流程内执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;处理条数由对选中记录集合的统计加工得到，该步骤充当 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;本段没有模型执行证据，也没有局部隔离与受限回传机制，按默认模式编译；returns 为空。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;源文只说明产出计数结果，未规定执行方式；仅因计数简单或可实现为脚本，不足以声称本地隔离。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;count_processed_records&quot;,
        &quot;reason&quot;: &quot;对输入集合计数是实际计算，属 transform；不产生读取、写入或外发效果。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;本段没有模型执行证据，也没有局部隔离与受限回传机制，按默认模式编译；returns 为空。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;源文只说明产出计数结果，未规定执行方式；仅因计数简单或可实现为脚本，不足以声称本地隔离。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
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
          &quot;reason&quot;: &quot;源文要求产出处理条数；该数值由选中记录集合计数得到，输入依赖记为 derived。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;An explicitly pure calculation remains compute; an opaque computation preserves possible dependencies without inventing a new external source.&quot;,
          &quot;reason&quot;: &quot;EM09：计数是纯计算，保留对输入集合的依赖，不新增外部来源。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D005 | storage: count.txt | storage: count.txt: 未绑定 → D005 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;本地写文件步骤由 agent_runtime 执行；源文未提及模型或外部工具参与。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;写入使内容到达本地存储位置，属 sink；写入内容为计数值本身。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write_file&quot;,
        &quot;reason&quot;: &quot;该 IR 的 opcode 值为 write_file 且目标为本地文件，产生 fs_write 效果。&quot;,
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
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;写入内容为处理条数本身；源文只表达把该值写入文件，按 replace 语义记录，未声明追加，也未读取旧内容。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;File writes and model observation do not automatically imply context_write; each effect requires its own evidence.&quot;,
          &quot;reason&quot;: &quot;EM07：文件写入不自动扩展为 context_write；本 IR 未声明运行时上下文键。&quot;,
          &quot;ref_id&quot;: &quot;EM07&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
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
        &quot;reason&quot;: &quot;该指令结束流程，由运行流程执行返回控制。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;结束控制不引入、送达或加工内容，无适用角色标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通返回只是控制结束，词表内无适用效果；它也不等于面向用户的输出。&quot;,
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
| D001 | data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3 | known_parts |
| D002 | data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752 | subset_view |
| D003 | data_b49888df97ba2c2bedc7bc0eb9551a64a0f1ee75c25ac30de78c0304d145938a | opaque |
| D004 | data_bb810cb52f9d02efd6dbd0cc2e048de880be7fb6260762e19989918208205ba2 | opaque |
| D005 | data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c | opaque |
| D006 | data_e3dd005634ecc1096b3fd33feba49faff90d244e2a83b17ee1cc373dc5e5d118 | known_parts |

<details><summary>D001：完整 Data 内容、来源与依赖</summary>

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
        &quot;data&quot;: &quot;data_e3dd005634ecc1096b3fd33feba49faff90d244e2a83b17ee1cc373dc5e5d118&quot;,
        &quot;path&quot;: [
          {
            &quot;kind&quot;: &quot;element&quot;,
            &quot;scope&quot;: &quot;transfer:[\&quot;faf8e8b023937df8db38631f6d8c634c82d86482edaebf9f5ab73641f02ea09a\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
          }
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
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

<details><summary>D002：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;base&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
    &quot;form&quot;: &quot;subset_view&quot;,
    &quot;predicate&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;
  },
  &quot;id&quot;: &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_003&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;
    ],
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
  &quot;id&quot;: &quot;data_b49888df97ba2c2bedc7bc0eb9551a64a0f1ee75c25ac30de78c0304d145938a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;faf8e8b023937df8db38631f6d8c634c82d86482edaebf9f5ab73641f02ea09a\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;recipient&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_bb810cb52f9d02efd6dbd0cc2e048de880be7fb6260762e19989918208205ba2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;faf8e8b023937df8db38631f6d8c634c82d86482edaebf9f5ab73641f02ea09a\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;summary&quot;
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
  &quot;id&quot;: &quot;data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
        &quot;data&quot;: &quot;data_b49888df97ba2c2bedc7bc0eb9551a64a0f1ee75c25ac30de78c0304d145938a&quot;,
        &quot;path&quot;: [
          &quot;recipient&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_bb810cb52f9d02efd6dbd0cc2e048de880be7fb6260762e19989918208205ba2&quot;,
        &quot;path&quot;: [
          &quot;summary&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_e3dd005634ecc1096b3fd33feba49faff90d244e2a83b17ee1cc373dc5e5d118&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;faf8e8b023937df8db38631f6d8c634c82d86482edaebf9f5ab73641f02ea09a\&quot;,\&quot;ir_005\&quot;,0,\&quot;element\&quot;]&quot;
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;
      }
    ],
    &quot;loc_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
        &quot;reason&quot;: &quot;源文明确写入目标为本地文件 count.txt。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;写文件指令的输入操作数标识该本地文件。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;
      }
    ],
    &quot;loc_events_json&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;源文第1步表明该文件由用户提供并被流程读取，是本地文件存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;用户提供的 events.json&quot;,
        &quot;reason&quot;: &quot;该 IR 的输入操作数标识同一外部文件资源。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      }
    ],
    &quot;loc_notify_send&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;notify.send&quot;,
        &quot;reason&quot;: &quot;该 IR 的外部资源操作数标识被调用的通知服务，构成远程发送边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;reason&quot;: &quot;源文表明内容被发送给记录中的接收对象，支持远程边界而非本地存储。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
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
    &quot;compiled_sha256&quot;: &quot;3c254c180309f9a7d4f61122cb8a6a59408017c9fe750561285298869edb6ea5&quot;,
    &quot;mapping_sha256&quot;: &quot;57cb1a41fdc3b985e8e0c4a0a59b4a00e24964aae0d5ec9aa007638dee2e72d6&quot;,
    &quot;raw_sha256&quot;: &quot;bc519bff1a4a9e4a328db5098f7953fd2b08da9f4e5e77b48a40ed8ea4a9b437&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v1&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;3c254c180309f9a7d4f61122cb8a6a59408017c9fe750561285298869edb6ea5&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v1&quot;,
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
          3
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
      &quot;sha256&quot;: &quot;12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v2&quot;
    },
    &quot;raw_sha256&quot;: &quot;bc519bff1a4a9e4a328db5098f7953fd2b08da9f4e5e77b48a40ed8ea4a9b437&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v1&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_txt&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
          &quot;reason&quot;: &quot;源文明确写入目标为本地文件 count.txt。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count.txt&quot;,
          &quot;reason&quot;: &quot;写文件指令的输入操作数标识该本地文件。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;loc_events_json&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;源文第1步表明该文件由用户提供并被流程读取，是本地文件存储边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;用户提供的 events.json&quot;,
          &quot;reason&quot;: &quot;该 IR 的输入操作数标识同一外部文件资源。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;loc_notify_send&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;notify.send&quot;,
          &quot;reason&quot;: &quot;该 IR 的外部资源操作数标识被调用的通知服务，构成远程发送边界。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;reason&quot;: &quot;源文表明内容被发送给记录中的接收对象，支持远程边界而非本地存储。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_count_txt&quot;: {
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;count.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_009&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_events_json&quot;: {
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;用户提供的 events.json&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_notify_send&quot;: {
        &quot;kind&quot;: &quot;remote&quot;,
        &quot;name&quot;: &quot;notify.send&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_005&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      }
    },
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
            &quot;reason&quot;: &quot;源文第1步要求读取用户提供的文件，属流程内本地动作，执行主体标注为 agent_runtime；源文未提及模型参与该读取。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
            &quot;reason&quot;: &quot;读取把该文件当前内容整体引入当前流程，充当 source；内容包含记录的全部字段，未做字段级加工。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read_file&quot;,
            &quot;reason&quot;: &quot;该 IR 的 opcode 值为 read_file 且输入为文件资源，产生对文件内容的读取效果 fs_read。&quot;,
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
            &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的 source/sink/transformer 角色标签，故为空。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只做控制流转移，不读取、不写入、不发送、不转换内容；词表内无适用效果，但控制转移本身仍影响后续执行顺序。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;筛选步骤属于流程内的本地处理，源文与 CFG 均未指明模型执行，执行主体标注为 agent_runtime。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;该动作按条件处理输入记录集合并筛出子集，属 transformer；未把内容外发或写入存储。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;选中该记录&quot;,
            &quot;reason&quot;: &quot;按条件从集合中挑选元素属于选择/过滤类处理，词表下记 transform；被选中元素本身保持不变。&quot;,
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
            &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身决定后续执行顺序。&quot;,
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
          &quot;net_send&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;源文要求流程对每条选中记录发起该调用，调用由本地运行流程编排执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;notify.send&quot;,
            &quot;reason&quot;: &quot;该 IR 的外部资源操作数指明具体通知服务 notify.send，实际发送动作由该工具/服务执行；不是仅凭 opcode 名称推断执行主体。&quot;,
            &quot;ref_id&quot;: &quot;g_0021&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;调用使记录中的 recipient 与 summary 值到达外部接收对象，属 sink；未加入加工角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;源文明确向记录中的接收对象发送内容，具备通信证据，属远程发送 net_send；发送内容为选中记录的字段值。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;net_send&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Model observation, network delivery, and user output are separate boundaries.&quot;,
            &quot;reason&quot;: &quot;EM06：网络投递与用户输出是分开的边界；此处按通信证据只记 net_send，未据此推断用户可见输出。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: &quot;net_send&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
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
            &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;源文把处理条数作为流程内部产出的数值，未见模型处理说明；该统计由 agent_runtime 在流程内执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;处理条数由对选中记录集合的统计加工得到，该步骤充当 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;count_processed_records&quot;,
            &quot;reason&quot;: &quot;对输入集合计数是实际计算，属 transform；不产生读取、写入或外发效果。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
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
            &quot;reason&quot;: &quot;该指令是无输入输出的控制转移，由本地运行流程执行跳转，未涉及其他执行主体。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;控制跳转不引入、送达或加工内容，没有可支持的角色标签，故为空。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 只做控制流转移；词表内无适用效果，但跳转本身仍影响后续执行顺序。&quot;,
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
            &quot;reason&quot;: &quot;本地写文件步骤由 agent_runtime 执行；源文未提及模型或外部工具参与。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
            &quot;reason&quot;: &quot;写入使内容到达本地存储位置，属 sink；写入内容为计数值本身。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;write_file&quot;,
            &quot;reason&quot;: &quot;该 IR 的 opcode 值为 write_file 且目标为本地文件，产生 fs_write 效果。&quot;,
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
            &quot;reason&quot;: &quot;该指令结束流程，由运行流程执行返回控制。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;结束控制不引入、送达或加工内容，无适用角色标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通返回只是控制结束，词表内无适用效果；它也不等于面向用户的输出。&quot;,
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
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;read_file&quot;,
                        &quot;reason&quot;: &quot;该 IR 的 opcode 值为 read_file，输入为文件资源，执行对文件内容的读取。&quot;,
                        &quot;ref_id&quot;: &quot;g_0009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
                        &quot;reason&quot;: &quot;EM01：未见键限定接口或机制限制，获取范围保留为文件整体内容，不用单个字段替代来源整体。&quot;,
                        &quot;ref_id&quot;: &quot;EM01&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_events_json&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;event_records&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
                &quot;reason&quot;: &quot;源文只规定读取该文件，没有规定模型处理，也没有隔离执行与受限回传机制，故按默认模式编译，returns 为空。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;For content acquired for the agent&#x27;s natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version.&quot;,
                &quot;reason&quot;: &quot;EM03：读取所得版本在无显式隔离或受限路由时保留被模型观察的可能；这是契约默认，不是实测事件。&quot;,
                &quot;ref_id&quot;: &quot;EM03&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;event_records&quot;,
                &quot;reason&quot;: &quot;输出语义名为 event_records，绑定刚读取的整份文件内容，未做字段级替换。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;event_records&quot;
            }
          }
        ]
      },
      &quot;ir_002&quot;: {
        &quot;events&quot;: [],
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
                        &quot;reason&quot;: &quot;该条件作为筛选谓词记录；静态分析不执行自然语言谓词，只保留选择关系。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
                        &quot;reason&quot;: &quot;EM11：筛选保留被选中元素原样，不对元素字段做改写。&quot;,
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
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                &quot;reason&quot;: &quot;源文给出筛选条件，但未规定模型执行，也未规定隔离执行与受限回传机制，因此按默认模式编译，returns 为空。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;EM10：默认模式下，筛选所依据的读取输出保留被模型观察的可能；本段未声称存在局部隔离。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;selected_records&quot;,
                &quot;reason&quot;: &quot;该 IR 输出语义名为 selected_records，绑定筛选得到的记录集合。&quot;,
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
                            &quot;reason&quot;: &quot;源文明确接收对象取当前记录的 recipient 字段，属于对同一元素的显式字段选取。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
                            &quot;reason&quot;: &quot;EM11：在同一元素绑定上选择字段，保证 recipient 与 summary 来自同一条记录。&quot;,
                            &quot;ref_id&quot;: &quot;EM11&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
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
                            &quot;reason&quot;: &quot;源文明确 body 参数直接取 summary 原值，是字段选择而非摘要生成或内容改写。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
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
                            &quot;reason&quot;: &quot;投递实参仅为同一条记录选出的 recipient 与 summary，顺序对应接收对象与 body；未加入 access_token 等其它字段。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;source&quot;,
                            &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
                            &quot;reason&quot;: &quot;该禁止限定投递内容不得包含 access_token；这里只记录实际绑定的两个值，没有把禁止项当成已执行的防护动作。&quot;,
                            &quot;ref_id&quot;: &quot;src_003&quot;
                          },
                          {
                            &quot;basis&quot;: &quot;execution_model&quot;,
                            &quot;quote&quot;: &quot;delivery must retain actual selected values, input order, result identities, and explicit prohibitions&quot;,
                            &quot;reason&quot;: &quot;EM06：投递需保留实际选中的值与明确禁止项，参数范围不因容器整体被保留而扩大。&quot;,
                            &quot;ref_id&quot;: &quot;EM06&quot;
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
                    &quot;effect_index&quot;: 0
                  }
                ],
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                    &quot;reason&quot;: &quot;逐元素段未见模型处理或局部隔离、受限回传机制，按默认模式编译；returns 为空。&quot;,
                    &quot;ref_id&quot;: &quot;EM10&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;quote&quot;: &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;,
                    &quot;reason&quot;: &quot;源文否定摘要生成与格式转换，本段只做字段选择与投递。&quot;,
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
                &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send&quot;,
                &quot;reason&quot;: &quot;源文规定对每条选中记录各执行一次调用，用 for_each 表达逐元素分析作用域。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;未选中的记录不调用 notify.send。&quot;,
                &quot;reason&quot;: &quot;作用域集合仅包含已选中记录，未选中元素不进入该作用域。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;It is an analysis scope, not an invented CFG loop or one measured call.&quot;,
                &quot;reason&quot;: &quot;EM11：该作用域是分析绑定，不是新增 CFG 循环，也不代表被测量的调用次数。&quot;,
                &quot;ref_id&quot;: &quot;EM11&quot;
              }
            ],
            &quot;item&quot;: &quot;record&quot;,
            &quot;kind&quot;: &quot;for_each&quot;
          }
        ],
        &quot;output_bindings&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;events&quot;: [],
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
                        &quot;reason&quot;: &quot;源文要求产出处理条数；该数值由选中记录集合计数得到，输入依赖记为 derived。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;An explicitly pure calculation remains compute; an opaque computation preserves possible dependencies without inventing a new external source.&quot;,
                        &quot;reason&quot;: &quot;EM09：计数是纯计算，保留对输入集合的依赖，不新增外部来源。&quot;,
                        &quot;ref_id&quot;: &quot;EM09&quot;
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
                &quot;reason&quot;: &quot;本段没有模型执行证据，也没有局部隔离与受限回传机制，按默认模式编译；returns 为空。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
                &quot;reason&quot;: &quot;源文只说明产出计数结果，未规定执行方式；仅因计数简单或可实现为脚本，不足以声称本地隔离。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;processed_count&quot;,
                &quot;reason&quot;: &quot;该 IR 输出语义名为 processed_count，绑定本段计算得到的计数值。&quot;,
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
                        &quot;reason&quot;: &quot;写入内容为处理条数本身；源文只表达把该值写入文件，按 replace 语义记录，未声明追加，也未读取旧内容。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;File writes and model observation do not automatically imply context_write; each effect requires its own evidence.&quot;,
                        &quot;reason&quot;: &quot;EM07：文件写入不自动扩展为 context_write；本 IR 未声明运行时上下文键。&quot;,
                        &quot;ref_id&quot;: &quot;EM07&quot;
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
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;本段没有模型处理或隔离回传证据，按默认模式编译；returns 为空。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
                &quot;reason&quot;: &quot;源文未规定模型执行或隔离机制，写入值不做格式转换。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: []
      },
      &quot;ir_010&quot;: {
        &quot;events&quot;: [],
        &quot;output_bindings&quot;: []
      }
    },
    &quot;unresolved&quot;: []
  }
}</pre>

</details>

