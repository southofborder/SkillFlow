# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；没有未决项或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v2`；SHA-256：`12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。

求解状态：`complete`。

IR 记录覆盖：5 / 5。

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
      &quot;content&quot;: &quot;# 人工构造的离线示范\n读取 records 文件。模型按 enabled 条件筛选，成员内容不变。\n对每个选中元素，原样取 recipient 与 summary，作为同一请求的两个参数发送。\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;ac9897961ad778b6a678239942b1ca02d2a5177e2ce3b208c8dee3a781fb7036&quot;
    }
  ],
  &quot;index&quot;: [
    {
      &quot;end_line&quot;: 3,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_001&quot;,
      &quot;start_line&quot;: 1
    }
  ],
  &quot;inventory&quot;: [
    {
      &quot;decoded_sha256&quot;: &quot;ac9897961ad778b6a678239942b1ca02d2a5177e2ce3b208c8dee3a781fb7036&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;raw_sha256&quot;: &quot;ac9897961ad778b6a678239942b1ca02d2a5177e2ce3b208c8dee3a781fb7036&quot;,
      &quot;size&quot;: 210
    }
  ],
  &quot;source_sha256&quot;: &quot;a51dbeefde743a180ccc9e49240b309a3df4bd9c426ed4ad49c16593bd975b68&quot;
}</pre>

</details>

<details><summary>覆盖与诊断</summary>

<pre>{
  &quot;coverage&quot;: {
    &quot;ir_dispatch&quot;: &quot;processed&quot;,
    &quot;ir_filter&quot;: &quot;processed&quot;,
    &quot;ir_read&quot;: &quot;processed&quot;,
    &quot;ir_return&quot;: &quot;processed&quot;,
    &quot;ir_send&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_read · read records

块：load；执行主体：agent_runtime；角色：[]。

IR 输入：0: records

IR 输出：0: records

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: records | 0: D005 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: records`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
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
          &quot;quote&quot;: &quot;read records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0006&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;all&quot;
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
        &quot;quote&quot;: &quot;read records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0006&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0006&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0006&quot;,
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0006&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0006&quot;
        }
      ],
      &quot;location&quot;: &quot;records&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;all&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0006&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;all&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_dispatch · dispatch

块：load；执行主体：agent_runtime；角色：[]。

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
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
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
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
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

## ir_filter · filter enabled records

块：use；执行主体：llm；角色：[]。

IR 输入：0: records

IR 输出：0: selected

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | filter_items | 0: D005 | — | 0: D003 |

入口／出口变化：

- `result: selected`：未绑定 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;selected&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
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
          &quot;quote&quot;: &quot;filter enabled records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0010&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;selected&quot;
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
        &quot;quote&quot;: &quot;filter enabled records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;filter enabled records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;filter enabled records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;filter enabled records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;llm&quot;
    ],
    &quot;roles&quot;: []
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;filter enabled records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0010&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;filter enabled records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0010&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;filter_items&quot;,
      &quot;output&quot;: &quot;selected&quot;,
      &quot;predicate&quot;: &quot;enabled&quot;
    }
  ]
}</pre>

</details>

## ir_send · send recipient and summary for each record

块：use；执行主体：agent_runtime；角色：[]。

IR 输入：0: selected

IR 输出：[]

逐元素作用域 1：集合候选 D003。以下各候选组单独绑定同一个元素，不能跨组组合参数；不是实际执行次数。

- 候选组 1：集合 D003 → 元素 D002。

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.候选组1.1.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |
| 1.候选组1.2.1 | transform | select_part | 0: D002 | — | 0: D004 |
| 1.候选组1.2.2 | transform | select_part | 0: D002 | — | 0: D001 |
| 1.候选组1.3.1 | net_send | deliver | 0: D004; 1: D001 | remote: notify | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;selected&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;selected&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: null
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;recipient&quot;,
      &quot;path&quot;: [
        &quot;recipient&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;record&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;summary&quot;,
      &quot;path&quot;: [
        &quot;summary&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;recipient&quot;
        },
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;summary&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;notify&quot;
    }
  ]
}</pre>

</details>

## ir_return · return

块：use；执行主体：agent_runtime；角色：[]。

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
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;selected&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;records&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;selected&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;records&quot;
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
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
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
| D001 | data_429ed59c3bce53f58c8f8aaec10abd095ed619956717b2409c5968adbaa3f3e3 | opaque |
| D002 | data_5d652cff5404e767539aa96a1397c0613681252658fe083a6bdd874fd97cc440 | known_parts |
| D003 | data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb | subset_view |
| D004 | data_d1ba6ff733ae299244977e92a5c78310e3350d80f6aa1ffcb8bee544fec33b52 | opaque |
| D005 | data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306 | known_parts |

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
  &quot;id&quot;: &quot;data_429ed59c3bce53f58c8f8aaec10abd095ed619956717b2409c5968adbaa3f3e3&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af463ce84298b9180a71bb7604f540f9a41d54766450a6a150f7aa46003bc5b9\&quot;,\&quot;ir_send\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;summary&quot;
    ]
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
        &quot;data&quot;: &quot;data_d1ba6ff733ae299244977e92a5c78310e3350d80f6aa1ffcb8bee544fec33b52&quot;,
        &quot;path&quot;: [
          &quot;recipient&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_429ed59c3bce53f58c8f8aaec10abd095ed619956717b2409c5968adbaa3f3e3&quot;,
        &quot;path&quot;: [
          &quot;summary&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_5d652cff5404e767539aa96a1397c0613681252658fe083a6bdd874fd97cc440&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af463ce84298b9180a71bb7604f540f9a41d54766450a6a150f7aa46003bc5b9\&quot;,\&quot;ir_send\&quot;,0,\&quot;element\&quot;]&quot;
      }
    ]
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
    &quot;base&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
    &quot;form&quot;: &quot;subset_view&quot;,
    &quot;predicate&quot;: &quot;enabled&quot;
  },
  &quot;id&quot;: &quot;data_9564e5433eb4d8d27f01ff67d25533941aa4c36430a70403ad2da81d2297bedb&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_filter&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_d1ba6ff733ae299244977e92a5c78310e3350d80f6aa1ffcb8bee544fec33b52&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
    &quot;path&quot;: [
      {
        &quot;kind&quot;: &quot;element&quot;,
        &quot;scope&quot;: &quot;transfer:[\&quot;af463ce84298b9180a71bb7604f540f9a41d54766450a6a150f7aa46003bc5b9\&quot;,\&quot;ir_send\&quot;,0,\&quot;element\&quot;]&quot;
      },
      &quot;recipient&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_5d652cff5404e767539aa96a1397c0613681252658fe083a6bdd874fd97cc440&quot;,
        &quot;path&quot;: [
          {
            &quot;kind&quot;: &quot;element&quot;,
            &quot;scope&quot;: &quot;transfer:[\&quot;af463ce84298b9180a71bb7604f540f9a41d54766450a6a150f7aa46003bc5b9\&quot;,\&quot;ir_send\&quot;,0,\&quot;element\&quot;]&quot;
          }
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_e43bc108c8bdd88c48eaebcf3f1b85e5c4768acf22908a6b602ef0d8ec4b2306&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:records&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;
      }
    ],
    &quot;notify&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;
      }
    ],
    &quot;records&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read records&quot;,
        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0006&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 4,
    &quot;data_count&quot;: 5,
    &quot;description_revision&quot;: 3,
    &quot;record_count&quot;: 5
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;8b65b118a9c39e7487dea6f382baf41e15f6a9aaf69cdb426b4c6689a9df4750&quot;,
    &quot;mapping_sha256&quot;: &quot;b25490d75d476e9ba6823f569500481859d71b4b2ed278e210d6a123c4a8c4c9&quot;,
    &quot;raw_sha256&quot;: &quot;e0c505ef484bddbd8696eac59757a307d24878eece7a9e870ef4722a7525ea96&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v1&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;8b65b118a9c39e7487dea6f382baf41e15f6a9aaf69cdb426b4c6689a9df4750&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v1&quot;,
    &quot;events&quot;: [
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_read&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_read&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_read&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_read&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_read&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_read&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_filter&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_filter&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;model&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_filter&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_filter&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_filter&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;model&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_filter&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_send&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_send&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_send&quot;,
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
          &quot;ir_send&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_send&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_send&quot;,
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
          &quot;ir_send&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_send&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_send&quot;,
          &quot;events&quot;,
          0,
          &quot;body&quot;,
          0,
          &quot;events&quot;,
          1
        ]
      }
    ],
    &quot;execution_model&quot;: {
      &quot;sha256&quot;: &quot;12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v2&quot;
    },
    &quot;raw_sha256&quot;: &quot;e0c505ef484bddbd8696eac59757a307d24878eece7a9e870ef4722a7525ea96&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v1&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;notify&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;records&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read records&quot;,
          &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
          &quot;ref_id&quot;: &quot;g_0006&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;notify&quot;: {
        &quot;kind&quot;: &quot;remote&quot;,
        &quot;name&quot;: &quot;notify&quot;,
        &quot;operand_refs&quot;: []
      },
      &quot;records&quot;: {
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;records&quot;,
        &quot;operand_refs&quot;: []
      }
    },
    &quot;profiles&quot;: {
      &quot;ir_dispatch&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0007&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0007&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0007&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_filter&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;filter enabled records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;llm&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;filter enabled records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;filter enabled records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;transform&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;llm&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_read&quot;: {
        &quot;effects&quot;: [
          &quot;fs_read&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;read records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0006&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;read records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0006&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read records&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0006&quot;,
            &quot;value&quot;: &quot;fs_read&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_return&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0012&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0012&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0012&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_send&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;,
          &quot;net_send&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0011&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0011&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0011&quot;,
            &quot;value&quot;: &quot;transform&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 1,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0011&quot;,
            &quot;value&quot;: &quot;net_send&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      }
    },
    &quot;transfer_specs&quot;: {
      &quot;ir_dispatch&quot;: {
        &quot;events&quot;: [],
        &quot;output_bindings&quot;: []
      },
      &quot;ir_filter&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;filter enabled records&quot;,
                        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                        &quot;ref_id&quot;: &quot;g_0010&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;filter_items&quot;,
                    &quot;output&quot;: &quot;selected&quot;,
                    &quot;predicate&quot;: &quot;enabled&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;filter enabled records&quot;,
                &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                &quot;ref_id&quot;: &quot;g_0010&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;model&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;filter enabled records&quot;,
                &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                &quot;ref_id&quot;: &quot;g_0010&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;selected&quot;
            }
          }
        ]
      },
      &quot;ir_read&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;read records&quot;,
                        &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                        &quot;ref_id&quot;: &quot;g_0006&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;records&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;all&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;read records&quot;,
                &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                &quot;ref_id&quot;: &quot;g_0006&quot;
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
                &quot;quote&quot;: &quot;read records&quot;,
                &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                &quot;ref_id&quot;: &quot;g_0006&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;all&quot;
            }
          }
        ]
      },
      &quot;ir_return&quot;: {
        &quot;events&quot;: [],
        &quot;output_bindings&quot;: []
      },
      &quot;ir_send&quot;: {
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
                            &quot;basis&quot;: &quot;cfg&quot;,
                            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
                            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                            &quot;ref_id&quot;: &quot;g_0011&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;recipient&quot;,
                        &quot;path&quot;: [
                          &quot;recipient&quot;
                        ]
                      },
                      {
                        &quot;evidences&quot;: [
                          {
                            &quot;basis&quot;: &quot;cfg&quot;,
                            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
                            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                            &quot;ref_id&quot;: &quot;g_0011&quot;
                          }
                        ],
                        &quot;input&quot;: {
                          &quot;kind&quot;: &quot;local&quot;,
                          &quot;name&quot;: &quot;record&quot;
                        },
                        &quot;op&quot;: &quot;select_part&quot;,
                        &quot;output&quot;: &quot;summary&quot;,
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
                            &quot;basis&quot;: &quot;cfg&quot;,
                            &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
                            &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                            &quot;ref_id&quot;: &quot;g_0011&quot;
                          }
                        ],
                        &quot;inputs&quot;: [
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;recipient&quot;
                          },
                          {
                            &quot;kind&quot;: &quot;local&quot;,
                            &quot;name&quot;: &quot;summary&quot;
                          }
                        ],
                        &quot;op&quot;: &quot;deliver&quot;,
                        &quot;target&quot;: &quot;notify&quot;
                      }
                    ],
                    &quot;effect_index&quot;: 1
                  }
                ],
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;cfg&quot;,
                    &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
                    &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                    &quot;ref_id&quot;: &quot;g_0011&quot;
                  }
                ],
                &quot;kind&quot;: &quot;processing&quot;,
                &quot;mode&quot;: &quot;default&quot;,
                &quot;returns&quot;: []
              }
            ],
            &quot;collection&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;send recipient and summary for each record&quot;,
                &quot;reason&quot;: &quot;作者明确指定的离线示例；并非模型判断或真实执行。&quot;,
                &quot;ref_id&quot;: &quot;g_0011&quot;
              }
            ],
            &quot;item&quot;: &quot;record&quot;,
            &quot;kind&quot;: &quot;for_each&quot;
          }
        ],
        &quot;output_bindings&quot;: []
      }
    },
    &quot;unresolved&quot;: []
  }
}</pre>

</details>

