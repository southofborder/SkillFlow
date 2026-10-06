# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；没有未决项或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v2`；SHA-256：`12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。

求解状态：`complete`。

IR 记录覆盖：12 / 12。

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
      &quot;content&quot;: &quot;---\nname: catalog-query\ndescription: Query an index once using a supplied request and preserve optional-parameter semantics.\n---\n\n# Catalog Query\n\nFollow the requirements in [workflow instructions](references/workflow.md); this file is part of the current workflow.\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;60ab6f65755b224fc8f3b0b267f1e8f2e149b5fee87699d45e76842258ee7181&quot;
    },
    {
      &quot;content&quot;: &quot;missing_arguments:\n  from_date: omit\n  limit: omit\n&quot;,
      &quot;path&quot;: &quot;query.yaml&quot;,
      &quot;sha256&quot;: &quot;a8a3256dda0c39c5738829e27d79563ff50938a15ed5bae4389bcf481e477d42&quot;
    },
    {
      &quot;content&quot;: &quot;# Query workflow\n\n&gt; Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.\n\nRead the user-supplied request.json, which contains term and may contain from_date and limit.\n\nCall index.search exactly once, using request.term unchanged as its query argument.\n\n- Call argument requirements:\n  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.\n  - When from_date is missing, omit the from_date argument.\n  - When limit is present, pass its value unchanged as the limit argument.\n  - When limit is missing, omit the limit argument.\n\nApply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n\nDo not invoke index.delete anywhere in this workflow.\n\nParameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n\nAfter the search, write the response&#x27;s total value to local count.txt.\n\nReturn the search response&#x27;s items value unchanged.\n&quot;,
      &quot;path&quot;: &quot;references/workflow.md&quot;,
      &quot;sha256&quot;: &quot;923dc4fb2a2ca28fdbe2caa9b2f348573e4af50dad5c51b930f0c672d180a7e2&quot;
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
      &quot;end_line&quot;: 8,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_003&quot;,
      &quot;start_line&quot;: 8
    },
    {
      &quot;end_line&quot;: 3,
      &quot;file&quot;: &quot;query.yaml&quot;,
      &quot;id&quot;: &quot;src_004&quot;,
      &quot;start_line&quot;: 1
    },
    {
      &quot;end_line&quot;: 1,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_005&quot;,
      &quot;start_line&quot;: 1
    },
    {
      &quot;end_line&quot;: 3,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_006&quot;,
      &quot;start_line&quot;: 3
    },
    {
      &quot;end_line&quot;: 5,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_007&quot;,
      &quot;start_line&quot;: 5
    },
    {
      &quot;end_line&quot;: 7,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_008&quot;,
      &quot;start_line&quot;: 7
    },
    {
      &quot;end_line&quot;: 13,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_009&quot;,
      &quot;start_line&quot;: 9
    },
    {
      &quot;end_line&quot;: 15,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_010&quot;,
      &quot;start_line&quot;: 15
    },
    {
      &quot;end_line&quot;: 17,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_011&quot;,
      &quot;start_line&quot;: 17
    },
    {
      &quot;end_line&quot;: 19,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_012&quot;,
      &quot;start_line&quot;: 19
    },
    {
      &quot;end_line&quot;: 21,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_013&quot;,
      &quot;start_line&quot;: 21
    },
    {
      &quot;end_line&quot;: 23,
      &quot;file&quot;: &quot;references/workflow.md&quot;,
      &quot;id&quot;: &quot;src_014&quot;,
      &quot;start_line&quot;: 23
    }
  ],
  &quot;inventory&quot;: [
    {
      &quot;decoded_sha256&quot;: &quot;60ab6f65755b224fc8f3b0b267f1e8f2e149b5fee87699d45e76842258ee7181&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;raw_sha256&quot;: &quot;60ab6f65755b224fc8f3b0b267f1e8f2e149b5fee87699d45e76842258ee7181&quot;,
      &quot;size&quot;: 266
    },
    {
      &quot;decoded_sha256&quot;: &quot;a8a3256dda0c39c5738829e27d79563ff50938a15ed5bae4389bcf481e477d42&quot;,
      &quot;kind&quot;: &quot;text&quot;,
      &quot;path&quot;: &quot;query.yaml&quot;,
      &quot;raw_sha256&quot;: &quot;a8a3256dda0c39c5738829e27d79563ff50938a15ed5bae4389bcf481e477d42&quot;,
      &quot;size&quot;: 51
    },
    {
      &quot;decoded_sha256&quot;: &quot;923dc4fb2a2ca28fdbe2caa9b2f348573e4af50dad5c51b930f0c672d180a7e2&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;references/workflow.md&quot;,
      &quot;raw_sha256&quot;: &quot;923dc4fb2a2ca28fdbe2caa9b2f348573e4af50dad5c51b930f0c672d180a7e2&quot;,
      &quot;size&quot;: 1006
    }
  ],
  &quot;source_sha256&quot;: &quot;66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c&quot;
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
    &quot;ir_010&quot;: &quot;processed&quot;,
    &quot;ir_011&quot;: &quot;processed&quot;,
    &quot;ir_012&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_001 · read_request_json

块：block_001；执行主体：agent_runtime；角色：source。

IR 输入：0: request.json

IR 输出：0: result_001

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: request.json | 0: D006 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;request.json contents&quot;,
          &quot;reason&quot;: &quot;该 IR 的首个输出即读取得到的 request.json 内容，绑定为读取操作的局部值 request_data。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_data&quot;
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
        &quot;quote&quot;: &quot;read_request_json&quot;,
        &quot;reason&quot;: &quot;CFG 以读取类 opcode 表示该步骤；源文未指定 LLM、工具或人工执行者，读取 request.json 由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;该读取把 request.json 的内容带入当前流程，是数据引入点，故为 source。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_request_json&quot;,
        &quot;reason&quot;: &quot;该指令读取外部资源 request.json 并把文件内容作为首个输出，符合读取文件内容的 fs_read。&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;源文没有写明本地隔离执行及受限回传机制，也没有针对该文件读取的接口说明，因此不能按 local 处理；按决策顺序使用 default。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;no explicit isolation or restricted routing&quot;,
        &quot;reason&quot;: &quot;该读取为后续代理处理获取内容，源文未规定隔离或受限路由，故保留所得版本可能被模型观察的默认可能，而非声称已经发生观察。&quot;,
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
          &quot;quote&quot;: &quot;read_request_json&quot;,
          &quot;reason&quot;: &quot;该指令从 storage 边界 request.json 读取当前文件内容，并作为局部值 request_data 输出；源文未提供仅键读取或限定范围的接口证据，故保留整体内容为可能的获取范围。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_request_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;request_data&quot;
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
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;源文没有写明本地隔离执行及受限回传机制，也没有针对该文件读取的接口说明，因此不能按 local 处理；按决策顺序使用 default。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;no explicit isolation or restricted routing&quot;,
          &quot;reason&quot;: &quot;该读取为后续代理处理获取内容，源文未规定隔离或受限路由，故保留所得版本可能被模型观察的默认可能，而非声称已经发生观察。&quot;,
          &quot;ref_id&quot;: &quot;EM03&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_data&quot;
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
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令也没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
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

## ir_003 · extract_query_term

块：block_002；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_001

IR 输出：0: result_002

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D006 | — | 0: D004 |

入口／出口变化：

- `result: result_002`：未绑定 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;request.term&quot;,
          &quot;reason&quot;: &quot;该 IR 的输出语义名即 request.term，绑定为选出的局部值 query_term。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;query_term&quot;
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
        &quot;quote&quot;: &quot;extract_query_term&quot;,
        &quot;reason&quot;: &quot;字段提取由本地运行时执行；源文未提及 LLM、工具或人工参与。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_query_term&quot;,
        &quot;reason&quot;: &quot;该指令对请求数据做字段选择处理，属于对内容的加工，故为 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
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
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，按契约使用 default；选择结果按默认模式可能被后续处理观察到。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;从请求数据中选出已有 term 值并保持不变，符合 transform 的选择语义。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
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
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，按契约使用 default；选择结果按默认模式可能被后续处理观察到。&quot;,
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
          &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
          &quot;reason&quot;: &quot;源文明确使用 request.term 原样作为查询参数，因此直接选出输入容器中的 term 字段并保持原值，而不是替换为独立字段来源或做生成式转换。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;query_term&quot;,
      &quot;path&quot;: [
        &quot;term&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_004 · extract_optional_from_date

块：block_002；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_001

IR 输出：0: result_003, 1: result_004

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D006 | — | 0: D001 |
| 2.2 | transform | compute | 0: D006 | — | 0: D009 |

入口／出口变化：

- `result: result_003`：未绑定 → D001
- `result: result_004`：未绑定 → D009

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;request.from_date&quot;,
          &quot;reason&quot;: &quot;第一个输出是选出的可选字段值，绑定为局部值 from_date_value。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;whether request.from_date is present&quot;,
          &quot;reason&quot;: &quot;第二个输出表示该字段是否存在，绑定为派生布尔局部值 from_date_present。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
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
        &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
        &quot;reason&quot;: &quot;可选字段取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
        &quot;reason&quot;: &quot;该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
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
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;reason&quot;: &quot;源文要求存在时原样传值，本指令据此提取已有 from_date 字段值并派生存在性判断，符合 transform。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
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
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
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
          &quot;quote&quot;: &quot;pass its value unchanged&quot;,
          &quot;reason&quot;: &quot;源文要求存在时原样传值，因此直接选出容器中的 from_date 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
          &quot;reason&quot;: &quot;源文明确参数描述不指示预校验或归一化，因此对该字段只做原样选择，不添加格式转换。&quot;,
          &quot;ref_id&quot;: &quot;src_012&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;from_date_value&quot;,
      &quot;path&quot;: [
        &quot;from_date&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When from_date is present&quot;,
          &quot;reason&quot;: &quot;存在性判断是对同一请求容器输入的派生计算，并非独立数据来源；源文只以该条件控制参数是否传入。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;from_date_present&quot;
    }
  ]
}</pre>

</details>

## ir_005 · extract_optional_limit

块：block_002；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_001

IR 输出：0: result_005, 1: result_006

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D006 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D006 | — | 0: D008 |
| 2.2 | transform | compute | 0: D006 | — | 0: D003 |

入口／出口变化：

- `result: result_005`：未绑定 → D008
- `result: result_006`：未绑定 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;request.limit&quot;,
          &quot;reason&quot;: &quot;第一个输出是选出的可选字段值，绑定为局部值 limit_value。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;whether request.limit is present&quot;,
          &quot;reason&quot;: &quot;第二个输出表示该字段是否存在，绑定为派生布尔局部值 limit_present。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
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
        &quot;quote&quot;: &quot;extract_optional_limit&quot;,
        &quot;reason&quot;: &quot;可选 limit 取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_optional_limit&quot;,
        &quot;reason&quot;: &quot;该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
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
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;源文要求存在时原样传值，本指令据此提取已有 limit 字段值并派生存在性判断，符合 transform。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
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
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
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
          &quot;quote&quot;: &quot;pass its value unchanged as the limit argument&quot;,
          &quot;reason&quot;: &quot;源文要求存在时原样传值，因此直接选出容器中的 limit 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
          &quot;reason&quot;: &quot;源文明确参数描述不指示预校验或归一化，因此对该字段只做原样选择，不添加格式转换。&quot;,
          &quot;ref_id&quot;: &quot;src_012&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;limit_value&quot;,
      &quot;path&quot;: [
        &quot;limit&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
          &quot;reason&quot;: &quot;存在性判断是对同一请求容器输入的派生计算，用于控制该参数是否传入，并非独立数据来源。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;limit_present&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

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
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
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

## ir_007 · index.search

块：block_003；执行主体：agent_runtime, tool；角色：source, sink。

IR 输入：0: index.search, 1: result_002, 2: result_003, 3: result_004, 4: result_005, 5: result_006

IR 输出：0: result_007

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | receive | 0: D004; 1: D001; 2: D008 | tool: index.search | 0: D005 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_007`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;index.search response&quot;,
          &quot;reason&quot;: &quot;该 IR 的输出是 index.search 的响应内容，绑定为获取得到的局部值 search_response。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流由本地 agent runtime 执行，并据此发起这次调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;CFG 把 index.search 作为被调用的外部资源，实际执行检索的工具参与该动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search response&quot;,
        &quot;reason&quot;: &quot;该调用把检索响应作为新内容引入当前流程，充当 source。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;请求参数被交给 index.search 这一接收边界，内容到达接收方，充当 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
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
        &quot;reason&quot;: &quot;该段获取检索响应；源文未规定隔离或受限路由，按 default 其获取结果可能在获取后进入模型可见范围。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认可能进入下一次模型请求；源文没有提供内容路由或隔离机制来限制它，因此使用 default 而不选 local。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
    ],
    &quot;roles&quot;: [
      &quot;source&quot;,
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;返回内容来自 tool 边界 index.search 的实际获取，不是对入参计算的结果；源文与 CFG 未建立网络通信证据，故在 null-effect 事件中以 receive 表达该获取。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
          &quot;reason&quot;: &quot;调用依赖 query_term（操作数 1）；from_date 与 limit 仅在存在时按原值传入（src_009），存在性标志（操作数 3、5）只控制是否传入，不构成本身的内容值。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
          &quot;reason&quot;: &quot;limit 值在存在时原样作为参数传入，因此作为该请求的参数依赖记录；能力说明不请求模糊扩展，本动作也不添加扩展、预校验或归一化操作。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 4,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_index_search&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;search_response&quot;
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
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;该段获取检索响应；源文未规定隔离或受限路由，按 default 其获取结果可能在获取后进入模型可见范围。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认可能进入下一次模型请求；源文没有提供内容路由或隔离机制来限制它，因此使用 default 而不选 local。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;search_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

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
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
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

## ir_009 · extract_response_total

块：block_004；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_007

IR 输出：0: result_008

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D005 | — | 0: D002 |

入口／出口变化：

- `result: result_008`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;search response total&quot;,
          &quot;reason&quot;: &quot;该 IR 的输出语义名即检索响应的 total，绑定为选出的局部值 response_total。&quot;,
          &quot;ref_id&quot;: &quot;g_0029&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response_total&quot;
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
        &quot;quote&quot;: &quot;extract_response_total&quot;,
        &quot;reason&quot;: &quot;从检索响应中取出 total 由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_response_total&quot;,
        &quot;reason&quot;: &quot;该指令对响应内容做字段选择处理，属于内容加工。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
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
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;该取值没有本地隔离或限定回传的接口证据，按决策顺序使用 default。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;the response&#x27;s total value&quot;,
        &quot;reason&quot;: &quot;源文明确要处理的是响应中已有 total 值，本指令只是把它取出，符合 transform 的选择语义。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
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
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;该取值没有本地隔离或限定回传的接口证据，按决策顺序使用 default。&quot;,
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
          &quot;quote&quot;: &quot;the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;源文明确要使用的是响应中已有的 total 值，因此直接选出该字段并保持原值，而不是把 total 当作新生成的结果。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;response_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_010 · write_count_file

块：block_004；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_008

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D002 | storage: count.txt | storage: count.txt: 未绑定 → D002 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;quote&quot;: &quot;write_count_file&quot;,
        &quot;reason&quot;: &quot;写本地文件由运行时执行；源文未指定 LLM、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;total 值被写入储存位置 count.txt，内容到达存储边界，充当 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;该指令把 total 值写入本地文件 count.txt，创建/修改文件内容，符合 fs_write；写入本身不自动构成 transform。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
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
          &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
          &quot;reason&quot;: &quot;该指令把 total 值写入本地文件 count.txt；源文只描述这一次写入，故按 replace 表示文件内容被写入该值，输入是 IR 的操作数 1（total 值），而不是外部资源操作数，且写入未变更内容不添加 transform。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
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

## ir_011 · extract_response_items

块：block_004；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_007

IR 输出：0: result_009

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D005 | — | 0: D007 |

入口／出口变化：

- `result: result_009`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
          &quot;quote&quot;: &quot;search response items&quot;,
          &quot;reason&quot;: &quot;该 IR 的输出语义名即响应 items，绑定为选出的局部值 response_items。&quot;,
          &quot;ref_id&quot;: &quot;g_0031&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response_items&quot;
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
        &quot;quote&quot;: &quot;extract_response_items&quot;,
        &quot;reason&quot;: &quot;从响应中取出 items 由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_response_items&quot;,
        &quot;reason&quot;: &quot;该指令对响应内容做字段选择处理，属于内容加工。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
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
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，使用 default。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;源文明确 items 是响应中已有字段且原样返回，本指令只是选出该字段，符合 transform 的选择语义。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
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
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，使用 default。&quot;,
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
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;源文明确 items 是响应中已有字段并要求原样返回，因此直接选出该字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;response_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_012 · return

块：block_004；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_009

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
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;返回动作由本地运行时执行；源文未提及 LLM、工具或人工执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0032&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;该指令只是把 items 原样交回调用方，源文未指明接收方或可见性边界，普通返回不证明面向用户的输出，因此没有已证据化的角色标签。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;依据同一规则，交回已有值不构成 user_output，也不属于其他效果类别；其未变更的值转发关系在 transfer_specs 中按输入操作数保留。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;,
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
| D001 | data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2 | opaque |
| D002 | data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543 | opaque |
| D003 | data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5 | opaque |
| D004 | data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123 | opaque |
| D005 | data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14 | known_parts |
| D006 | data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95 | known_parts |
| D007 | data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70 | opaque |
| D008 | data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7 | opaque |
| D009 | data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859 | opaque |

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
  &quot;id&quot;: &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
    &quot;path&quot;: [
      &quot;from_date&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_3180a79100efe4d418c4cc071920b6d446eac0146e58e403aab0d7948fcf45f5&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
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
  &quot;id&quot;: &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
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
        &quot;data&quot;: &quot;data_2e08dec0373eef711f8b6ea047e736b9851f790ec32a4254e8e359e9f1f53543&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;,
      &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;,
      &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;
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
        &quot;data&quot;: &quot;data_33c78672feaa9190b8e5819e8f7f0cae756752513f8896202c4dd5708a062123&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_0203f5d222354465b537e8a00156500810c1fe782ec0d383859fb4c6e04ee9c2&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:request.json&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D007：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_a3e0000ec12d7a8850424920af663d4f89719e9bef583141d8e7b52b1dec1e70&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_82feada70b97b5d54248adefc0ee1327d5ce2fd44394d93ca0d8a0024c47ae14&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
  }
}</pre>

</details>

<details><summary>D008：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_b41516473c1997cda9c782059916447b51a4576f38a91d118bc7e0bb2493c1d7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
    &quot;path&quot;: [
      &quot;limit&quot;
    ]
  }
}</pre>

</details>

<details><summary>D009：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_d873b0b9edd2e9417df389958479f82a5ce191aec029a76467fb306d4a225859&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_004&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_86fb8355060ffe52f02b705dafec593ec711183237b34cc3b372b311910e7a95&quot;
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. Unresolved effect order remains unresolved.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;
      }
    ],
    &quot;loc_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;该操作数标识写入目标本地文件 count.txt，属 storage 边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;local count.txt&quot;,
        &quot;reason&quot;: &quot;源文称其为 local count.txt，支持其为本地储存位置的身份。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;
      }
    ],
    &quot;loc_index_search&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;该操作数把 index.search 标识为内容获取边界；CFG 未提供网络地址或远程协议证据，故为 tool 而非 remote。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;源文把 index.search 作为被调用的检索工具，支持该 tool 边界身份。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;
      }
    ],
    &quot;loc_request_json&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;request.json&quot;,
        &quot;reason&quot;: &quot;该操作数标识外部资源 request.json，其身份是本地文件内容边界，属 storage。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;源文明确读取该用户提供的文件，支持该 storage 位置身份及其内容边界。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 10,
    &quot;data_count&quot;: 9,
    &quot;description_revision&quot;: 5,
    &quot;record_count&quot;: 12
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;37fd54e86df2569e370087915ffbb6375317918cb36665a3a708aec026c0bbcc&quot;,
    &quot;mapping_sha256&quot;: &quot;78b3996f93f18d638274dfbf9f5d3fbf7fe79d43b5298aebe21c501e02b95b56&quot;,
    &quot;raw_sha256&quot;: &quot;ac2824e5d36785e60a601dc906a0ddca25b9e0b6f2dea8d5615263751d34b3a1&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v1&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;37fd54e86df2569e370087915ffbb6375317918cb36665a3a708aec026c0bbcc&quot;,
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
          &quot;ir_004&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_004&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_004&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_004&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_004&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_004&quot;,
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
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
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
          &quot;ir_007&quot;,
          &quot;events&quot;,
          1
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
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_009&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
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
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          1
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
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_010&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_010&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_011&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_011&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_011&quot;,
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
    &quot;raw_sha256&quot;: &quot;ac2824e5d36785e60a601dc906a0ddca25b9e0b6f2dea8d5615263751d34b3a1&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v1&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_txt&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count.txt&quot;,
          &quot;reason&quot;: &quot;该操作数标识写入目标本地文件 count.txt，属 storage 边界。&quot;,
          &quot;ref_id&quot;: &quot;g_0030&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;local count.txt&quot;,
          &quot;reason&quot;: &quot;源文称其为 local count.txt，支持其为本地储存位置的身份。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;loc_index_search&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;index.search&quot;,
          &quot;reason&quot;: &quot;该操作数把 index.search 标识为内容获取边界；CFG 未提供网络地址或远程协议证据，故为 tool 而非 remote。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
          &quot;reason&quot;: &quot;源文把 index.search 作为被调用的检索工具，支持该 tool 边界身份。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;loc_request_json&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;request.json&quot;,
          &quot;reason&quot;: &quot;该操作数标识外部资源 request.json，其身份是本地文件内容边界，属 storage。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
          &quot;reason&quot;: &quot;源文明确读取该用户提供的文件，支持该 storage 位置身份及其内容边界。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
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
            &quot;instruction_id&quot;: &quot;ir_010&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_index_search&quot;: {
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;index.search&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_request_json&quot;: {
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;request.json&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
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
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;read_request_json&quot;,
            &quot;reason&quot;: &quot;CFG 以读取类 opcode 表示该步骤；源文未指定 LLM、工具或人工执行者，读取 request.json 由本地 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0009&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;该读取把 request.json 的内容带入当前流程，是数据引入点，故为 source。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read_request_json&quot;,
            &quot;reason&quot;: &quot;该指令读取外部资源 request.json 并把文件内容作为首个输出，符合读取文件内容的 fs_read。&quot;,
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
            &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令也没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
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
            &quot;quote&quot;: &quot;extract_query_term&quot;,
            &quot;reason&quot;: &quot;字段提取由本地运行时执行；源文未提及 LLM、工具或人工参与。&quot;,
            &quot;ref_id&quot;: &quot;g_0015&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;extract_query_term&quot;,
            &quot;reason&quot;: &quot;该指令对请求数据做字段选择处理，属于对内容的加工，故为 transformer。&quot;,
            &quot;ref_id&quot;: &quot;g_0015&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;从请求数据中选出已有 term 值并保持不变，符合 transform 的选择语义。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
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
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
            &quot;reason&quot;: &quot;可选字段取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
            &quot;reason&quot;: &quot;该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;源文要求存在时原样传值，本指令据此提取已有 from_date 字段值并派生存在性判断，符合 transform。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
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
      &quot;ir_005&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;extract_optional_limit&quot;,
            &quot;reason&quot;: &quot;可选 limit 取值及其存在性判断由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0017&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;extract_optional_limit&quot;,
            &quot;reason&quot;: &quot;该指令从请求数据中选出可选字段并派生存在性判断，属于内容处理。&quot;,
            &quot;ref_id&quot;: &quot;g_0017&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;源文要求存在时原样传值，本指令据此提取已有 limit 字段值并派生存在性判断，符合 transform。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
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
      &quot;ir_006&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
            &quot;reason&quot;: &quot;工作流由本地 agent runtime 执行，并据此发起这次调用。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;index.search&quot;,
            &quot;reason&quot;: &quot;CFG 把 index.search 作为被调用的外部资源，实际执行检索的工具参与该动作。&quot;,
            &quot;ref_id&quot;: &quot;g_0023&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;index.search response&quot;,
            &quot;reason&quot;: &quot;该调用把检索响应作为新内容引入当前流程，充当 source。&quot;,
            &quot;ref_id&quot;: &quot;g_0023&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;请求参数被交给 index.search 这一接收边界，内容到达接收方，充当 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
            &quot;reason&quot;: &quot;源文与 CFG 只给出工具调用与取值关系，没有网络地址、协议或远程传输证据，工具名本身不证明网络通信，故不标注 net_send/net_receive；该调用是已知的工具内容获取，按 EM09 用 tool 位置的 receive 在 null-effect 事件中表达。&quot;,
            &quot;ref_id&quot;: &quot;EM09&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;,
          &quot;sink&quot;
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
            &quot;reason&quot;: &quot;该指令是控制流转移，由本地运行时执行；源文与 CFG 未涉及 LLM、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;该指令 inputs 与 outputs 均为空，不引入、转换或交付任何内容，没有适用的角色标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不属于效果词汇表任何类别，该指令没有内容操作数；这是对已知控制行为的边界说明，不代表该指令无副作用、可跳过或前后状态相同。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
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
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;extract_response_total&quot;,
            &quot;reason&quot;: &quot;从检索响应中取出 total 由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0029&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;extract_response_total&quot;,
            &quot;reason&quot;: &quot;该指令对响应内容做字段选择处理，属于内容加工。&quot;,
            &quot;ref_id&quot;: &quot;g_0029&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;the response&#x27;s total value&quot;,
            &quot;reason&quot;: &quot;源文明确要处理的是响应中已有 total 值，本指令只是把它取出，符合 transform 的选择语义。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
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
      &quot;ir_010&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;write_count_file&quot;,
            &quot;reason&quot;: &quot;写本地文件由运行时执行；源文未指定 LLM、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0030&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
            &quot;reason&quot;: &quot;total 值被写入储存位置 count.txt，内容到达存储边界，充当 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
            &quot;reason&quot;: &quot;该指令把 total 值写入本地文件 count.txt，创建/修改文件内容，符合 fs_write；写入本身不自动构成 transform。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
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
      &quot;ir_011&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;extract_response_items&quot;,
            &quot;reason&quot;: &quot;从响应中取出 items 由本地运行时执行；无 LLM、工具或人工执行者证据。&quot;,
            &quot;ref_id&quot;: &quot;g_0031&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;extract_response_items&quot;,
            &quot;reason&quot;: &quot;该指令对响应内容做字段选择处理，属于内容加工。&quot;,
            &quot;ref_id&quot;: &quot;g_0031&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;源文明确 items 是响应中已有字段且原样返回，本指令只是选出该字段，符合 transform 的选择语义。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
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
      &quot;ir_012&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;返回动作由本地运行时执行；源文未提及 LLM、工具或人工执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0032&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;该指令只是把 items 原样交回调用方，源文未指明接收方或可见性边界，普通返回不证明面向用户的输出，因此没有已证据化的角色标签。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;依据同一规则，交回已有值不构成 user_output，也不属于其他效果类别；其未变更的值转发关系在 transfer_specs 中按输入操作数保留。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
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
                        &quot;quote&quot;: &quot;read_request_json&quot;,
                        &quot;reason&quot;: &quot;该指令从 storage 边界 request.json 读取当前文件内容，并作为局部值 request_data 输出；源文未提供仅键读取或限定范围的接口证据，故保留整体内容为可能的获取范围。&quot;,
                        &quot;ref_id&quot;: &quot;g_0009&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_request_json&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;request_data&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;源文没有写明本地隔离执行及受限回传机制，也没有针对该文件读取的接口说明，因此不能按 local 处理；按决策顺序使用 default。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;no explicit isolation or restricted routing&quot;,
                &quot;reason&quot;: &quot;该读取为后续代理处理获取内容，源文未规定隔离或受限路由，故保留所得版本可能被模型观察的默认可能，而非声称已经发生观察。&quot;,
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
                &quot;quote&quot;: &quot;request.json contents&quot;,
                &quot;reason&quot;: &quot;该 IR 的首个输出即读取得到的 request.json 内容，绑定为读取操作的局部值 request_data。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;request_data&quot;
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
                        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                        &quot;reason&quot;: &quot;源文明确使用 request.term 原样作为查询参数，因此直接选出输入容器中的 term 字段并保持原值，而不是替换为独立字段来源或做生成式转换。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;query_term&quot;,
                    &quot;path&quot;: [
                      &quot;term&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，按契约使用 default；选择结果按默认模式可能被后续处理观察到。&quot;,
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
                &quot;quote&quot;: &quot;request.term&quot;,
                &quot;reason&quot;: &quot;该 IR 的输出语义名即 request.term，绑定为选出的局部值 query_term。&quot;,
                &quot;ref_id&quot;: &quot;g_0015&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;query_term&quot;
            }
          }
        ]
      },
      &quot;ir_004&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;pass its value unchanged&quot;,
                        &quot;reason&quot;: &quot;源文要求存在时原样传值，因此直接选出容器中的 from_date 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
                        &quot;reason&quot;: &quot;源文明确参数描述不指示预校验或归一化，因此对该字段只做原样选择，不添加格式转换。&quot;,
                        &quot;ref_id&quot;: &quot;src_012&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;from_date_value&quot;,
                    &quot;path&quot;: [
                      &quot;from_date&quot;
                    ]
                  },
                  {
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When from_date is present&quot;,
                        &quot;reason&quot;: &quot;存在性判断是对同一请求容器输入的派生计算，并非独立数据来源；源文只以该条件控制参数是否传入。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;from_date_present&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
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
                &quot;quote&quot;: &quot;request.from_date&quot;,
                &quot;reason&quot;: &quot;第一个输出是选出的可选字段值，绑定为局部值 from_date_value。&quot;,
                &quot;ref_id&quot;: &quot;g_0016&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;from_date_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;whether request.from_date is present&quot;,
                &quot;reason&quot;: &quot;第二个输出表示该字段是否存在，绑定为派生布尔局部值 from_date_present。&quot;,
                &quot;ref_id&quot;: &quot;g_0016&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;from_date_present&quot;
            }
          }
        ]
      },
      &quot;ir_005&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;pass its value unchanged as the limit argument&quot;,
                        &quot;reason&quot;: &quot;源文要求存在时原样传值，因此直接选出容器中的 limit 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
                        &quot;reason&quot;: &quot;源文明确参数描述不指示预校验或归一化，因此对该字段只做原样选择，不添加格式转换。&quot;,
                        &quot;ref_id&quot;: &quot;src_012&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;limit_value&quot;,
                    &quot;path&quot;: [
                      &quot;limit&quot;
                    ]
                  },
                  {
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
                        &quot;reason&quot;: &quot;存在性判断是对同一请求容器输入的派生计算，用于控制该参数是否传入，并非独立数据来源。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;limit_present&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;源文只规定传参条件，没有规定本地隔离执行与受限回传机制，因此使用 default。&quot;,
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
                &quot;quote&quot;: &quot;request.limit&quot;,
                &quot;reason&quot;: &quot;第一个输出是选出的可选字段值，绑定为局部值 limit_value。&quot;,
                &quot;ref_id&quot;: &quot;g_0017&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;limit_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;whether request.limit is present&quot;,
                &quot;reason&quot;: &quot;第二个输出表示该字段是否存在，绑定为派生布尔局部值 limit_present。&quot;,
                &quot;ref_id&quot;: &quot;g_0017&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;limit_present&quot;
            }
          }
        ]
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
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
                        &quot;reason&quot;: &quot;返回内容来自 tool 边界 index.search 的实际获取，不是对入参计算的结果；源文与 CFG 未建立网络通信证据，故在 null-effect 事件中以 receive 表达该获取。&quot;,
                        &quot;ref_id&quot;: &quot;EM09&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                        &quot;reason&quot;: &quot;调用依赖 query_term（操作数 1）；from_date 与 limit 仅在存在时按原值传入（src_009），存在性标志（操作数 3、5）只控制是否传入，不构成本身的内容值。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                        &quot;reason&quot;: &quot;limit 值在存在时原样作为参数传入，因此作为该请求的参数依赖记录；能力说明不请求模糊扩展，本动作也不添加扩展、预校验或归一化操作。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 4,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_index_search&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;search_response&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;该段获取检索响应；源文未规定隔离或受限路由，按 default 其获取结果可能在获取后进入模型可见范围。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
                &quot;reason&quot;: &quot;工具返回内容默认可能进入下一次模型请求；源文没有提供内容路由或隔离机制来限制它，因此使用 default 而不选 local。&quot;,
                &quot;ref_id&quot;: &quot;EM02&quot;
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
                &quot;quote&quot;: &quot;index.search response&quot;,
                &quot;reason&quot;: &quot;该 IR 的输出是 index.search 的响应内容，绑定为获取得到的局部值 search_response。&quot;,
                &quot;ref_id&quot;: &quot;g_0023&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;search_response&quot;
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
                        &quot;quote&quot;: &quot;the response&#x27;s total value&quot;,
                        &quot;reason&quot;: &quot;源文明确要使用的是响应中已有的 total 值，因此直接选出该字段并保持原值，而不是把 total 当作新生成的结果。&quot;,
                        &quot;ref_id&quot;: &quot;src_013&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;response_total&quot;,
                    &quot;path&quot;: [
                      &quot;total&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;该取值没有本地隔离或限定回传的接口证据，按决策顺序使用 default。&quot;,
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
                &quot;quote&quot;: &quot;search response total&quot;,
                &quot;reason&quot;: &quot;该 IR 的输出语义名即检索响应的 total，绑定为选出的局部值 response_total。&quot;,
                &quot;ref_id&quot;: &quot;g_0029&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response_total&quot;
            }
          }
        ]
      },
      &quot;ir_010&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
                        &quot;reason&quot;: &quot;该指令把 total 值写入本地文件 count.txt；源文只描述这一次写入，故按 replace 表示文件内容被写入该值，输入是 IR 的操作数 1（total 值），而不是外部资源操作数，且写入未变更内容不添加 transform。&quot;,
                        &quot;ref_id&quot;: &quot;src_013&quot;
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
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;该段是文件写入，输入是已取出的 total 值；源文没有规定本地隔离执行与限定回传的接口机制，因此按决策顺序使用 default。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;output_bindings&quot;: []
      },
      &quot;ir_011&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
                        &quot;reason&quot;: &quot;源文明确 items 是响应中已有字段并要求原样返回，因此直接选出该字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_014&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;response_items&quot;,
                    &quot;path&quot;: [
                      &quot;items&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;该字段选择没有本地隔离或限定回传的接口证据，使用 default。&quot;,
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
                &quot;quote&quot;: &quot;search response items&quot;,
                &quot;reason&quot;: &quot;该 IR 的输出语义名即响应 items，绑定为选出的局部值 response_items。&quot;,
                &quot;ref_id&quot;: &quot;g_0031&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response_items&quot;
            }
          }
        ]
      },
      &quot;ir_012&quot;: {
        &quot;events&quot;: [],
        &quot;output_bindings&quot;: []
      }
    },
    &quot;unresolved&quot;: []
  }
}</pre>

</details>

