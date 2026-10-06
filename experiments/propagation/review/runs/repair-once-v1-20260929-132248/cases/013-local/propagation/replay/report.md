# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v3`；SHA-256：`26cd7f0d607b13377dc5d93546b9844b02f37db89b8dd8554613ea60e5b878ce`。

求解状态：`complete`。

IR 记录覆盖：26 / 26。

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
      &quot;content&quot;: &quot;---\nname: source-fetch-with-fallback\ndescription: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.\n---\n\n# Source Fetch With Fallback\n\n1. Read source_id from the user&#x27;s request and read FAST_KEY from the environment.\n2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.\n3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.\n4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.\n5. Call archive.fetch at most once and pass source_id as its only argument.\n6. On either tool&#x27;s success, return that successful response&#x27;s body value unchanged and make no further fetch calls.\n7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.\n8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.\n9. Before returning from every success or failure path, append the final status to local status.txt.\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495&quot;
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
      &quot;decoded_sha256&quot;: &quot;90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;raw_sha256&quot;: &quot;90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495&quot;,
      &quot;size&quot;: 1115
    }
  ],
  &quot;source_sha256&quot;: &quot;fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da&quot;
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
    &quot;ir_012&quot;: &quot;processed&quot;,
    &quot;ir_013&quot;: &quot;processed&quot;,
    &quot;ir_014&quot;: &quot;processed&quot;,
    &quot;ir_015&quot;: &quot;processed&quot;,
    &quot;ir_016&quot;: &quot;processed&quot;,
    &quot;ir_017&quot;: &quot;processed&quot;,
    &quot;ir_018&quot;: &quot;processed&quot;,
    &quot;ir_019&quot;: &quot;processed&quot;,
    &quot;ir_020&quot;: &quot;processed&quot;,
    &quot;ir_021&quot;: &quot;processed&quot;,
    &quot;ir_022&quot;: &quot;processed&quot;,
    &quot;ir_023&quot;: &quot;processed&quot;,
    &quot;ir_024&quot;: &quot;processed&quot;,
    &quot;ir_025&quot;: &quot;processed&quot;,
    &quot;ir_026&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_001 · read_source_id_from_user_request

块：block_001；执行主体：agent_runtime；角色：source。

IR 输入：0: user_request

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
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: user_request | 0: D012 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D012 | model_context: 当前模型处理上下文 | — |
| 3.1 | transform | select_part | 0: D012 | — | 0: D008 |

入口／出口变化：

- `result: result_001`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;source_id&quot;,
          &quot;reason&quot;: &quot;IR 输出 result_001 的语义名是 source_id，绑定刚选出的 source_id 局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;source_id&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;context_read&quot;,
      &quot;model_observe&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
        &quot;reason&quot;: &quot;源文要求执行读取动作；该动作由运行 Skill 的 agent runtime 承担，未出现 LLM 或工具参与读取的证据。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
        &quot;reason&quot;: &quot;从用户请求引入 source_id 到当前流程，属于数据来源角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
        &quot;reason&quot;: &quot;从上下文键 user_request 读取用户请求内容，符合 context_read。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;context_read&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
        &quot;reason&quot;: &quot;源文只规定从用户请求读取 source_id，没有本地隔离或受限返回机制，按契约默认模式处理；读取范围保留 user_request 整体。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;从读取到的用户请求内容中选出明确字段 source_id，保持原值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
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
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
          &quot;reason&quot;: &quot;源文明确从用户请求读取；按 EM01 不建立 key-only 读取，保留整个 user_request 作为读取范围。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_user_request&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;user_request_content&quot;
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
          &quot;reason&quot;: &quot;源文只规定从用户请求读取 source_id，没有本地隔离或受限返回机制，按契约默认模式处理；读取范围保留 user_request 整体。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;user_request_content&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
          &quot;reason&quot;: &quot;从读取到的用户请求内容中选出明确字段 source_id，保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;user_request_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;source_id&quot;,
      &quot;path&quot;: [
        &quot;source_id&quot;
      ]
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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;该指令是控制流分派，由运行 Skill 的 agent runtime 执行；未涉及内容处理。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该分派不引入、输出或转换数据，无适用 source/sink/transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派，在 effects 词表中无适用效果；不强制标为 transform。&quot;,
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

## ir_003 · read_fast_key_from_environment

块：block_002；执行主体：agent_runtime；角色：source。

IR 输入：0: environment

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
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: environment | 0: D001 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D001 | model_context: 当前模型处理上下文 | — |
| 3.1 | transform | select_part | 0: D001 | — | 0: D006 |

入口／出口变化：

- `result: result_002`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_key&quot;,
          &quot;reason&quot;: &quot;IR 输出 result_002 的语义名是 fast_key，绑定选出的 FAST_KEY 局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;context_read&quot;,
      &quot;model_observe&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
        &quot;reason&quot;: &quot;读取环境变量的动作由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从环境引入 FAST_KEY 到当前流程，属于数据来源角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从运行时上下文环境读取 FAST_KEY，符合 context_read。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;context_read&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;源文只规定从环境读取 FAST_KEY，没有给出显式本地隔离、受限返回或凭据代理机制，因此不能据此声明 local 模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
        &quot;reason&quot;: &quot;按 EM10，缺少显式本地执行及返回边界证据时采用 default 模式，读取输出 environment_content 保留为可能被模型观察的版本，而不是把可见版本收窄为单一键值。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从环境内容中选出明确字段 FAST_KEY，保持原值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;transform&quot;
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
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;源文明确从环境读取；按 EM01 不建立 key-only 读取，保留整个 environment 作为读取范围。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_environment&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;environment_content&quot;
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;源文只规定从环境读取 FAST_KEY，没有给出显式本地隔离、受限返回或凭据代理机制，因此不能据此声明 local 模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
          &quot;reason&quot;: &quot;按 EM10，缺少显式本地执行及返回边界证据时采用 default 模式，读取输出 environment_content 保留为可能被模型观察的版本，而不是把可见版本收窄为单一键值。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;environment_content&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;从环境内容中选出明确字段 FAST_KEY，保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;environment_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_key&quot;,
      &quot;path&quot;: [
        &quot;FAST_KEY&quot;
      ]
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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;控制流分派由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无数据来源、去向或转换，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派，无适用效果。&quot;,
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

## ir_005 · check_fast_key_presence

块：block_003；执行主体：agent_runtime；角色：transformer。

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
| 2.1 | transform | compute | 0: D006 | — | 0: D007 |

入口／出口变化：

- `result: result_003`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_key_present&quot;,
          &quot;reason&quot;: &quot;IR 输出 result_003 的语义名是 fast_key_present，绑定计算出的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key_present&quot;
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
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;判断 FAST_KEY 是否存在的动作由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;根据 FAST_KEY 计算存在性布尔值，处理并改变表示，属于转换角色。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;源文说明检查 FAST_KEY 是否存在；未规定本地隔离或模型处理，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;计算 FAST_KEY 存在性，属于计算/转换效果。&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
          &quot;reason&quot;: &quot;源文说明检查 FAST_KEY 是否存在；未规定本地隔离或模型处理，按默认模式。&quot;,
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
          &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
          &quot;reason&quot;: &quot;根据 FAST_KEY 计算存在性布尔值，属于转换。&quot;,
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
      &quot;output&quot;: &quot;fast_key_present&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_003

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分支分派由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;分派仅控制流向，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派，无适用效果。&quot;,
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

## ir_007 · fast.fetch

块：block_004；执行主体：tool；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_004

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
| 1.1 | 无标签数据操作 | receive | 0: D008; 1: D006 | tool: fast.fetch | 0: D005 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_004`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
          &quot;reason&quot;: &quot;IR 输出 result_004 的语义名是 fast_fetch_first_response，绑定工具返回的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_response&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;IR 操作码为 fast.fetch，实际抓取动作由该工具执行，工具是参与执行者。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;fast.fetch 返回响应内容，为当前流程引入外部数据，属 source。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;调用时把 source_id 与 FAST_KEY 作为参数交给 fast.fetch 工具，使内容到达工具这一接收边界，属 sink。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;源文规定首次调用 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式保留可能的后续模型可见性。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
          &quot;reason&quot;: &quot;fast.fetch 是工具获取边界；返回内容来自该工具，请求参数为 source_id 与 FAST_KEY；未建立网络传输证据，因此使用工具位置接收而非 remote/net_receive。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
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
        }
      ],
      &quot;location&quot;: &quot;loc_fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_response&quot;
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
          &quot;reason&quot;: &quot;源文规定首次调用 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式保留可能的后续模型可见性。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;控制流分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
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

## ir_009 · classify_fast_fetch_outcome

块：block_005；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_004

IR 输出：0: result_005, 1: result_006

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
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D005 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D005 | — | 0: D009 |
| 2.2 | transform | select_part | 0: D005 | — | 0: D017 |

入口／出口变化：

- `result: result_005`：未绑定 → D009
- `result: result_006`：未绑定 → D017

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_first_outcome&quot;,
          &quot;reason&quot;: &quot;输出 result_005 绑定分类结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;输出 result_006 绑定选出的 body 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_body&quot;
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
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;分类与字段选取由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;对工具响应进行分类并选出 body 字段，处理内容表示，属于转换角色。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;源文说明对成功响应分类并返回 body 原值；未规定本地隔离或模型处理，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;需要根据响应计算成功/失败分类，属于转换效果。&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;源文说明对成功响应分类并返回 body 原值；未规定本地隔离或模型处理，按默认模式。&quot;,
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
          &quot;quote&quot;: &quot;first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;源文区分首次尝试的瞬态失败，需要根据响应计算结果分类。&quot;,
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
      &quot;output&quot;: &quot;fast_fetch_first_outcome&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;从响应中选出已有 body 字段并保持原值，不是生成新内容。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_010 · dispatch

块：block_005；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_005

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
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

## ir_011 · fast.fetch

块：block_006；执行主体：tool；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_007

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
| 1.1 | 无标签数据操作 | receive | 0: D008; 1: D006 | tool: fast.fetch | 0: D010 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D010 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_007`：未绑定 → D010

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
          &quot;reason&quot;: &quot;IR 输出 result_007 的语义名是 fast_fetch_retry_response，绑定重试工具返回的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0039&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;重试同样由 fast.fetch 工具执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;重试返回响应内容，引入外部数据，属 source。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;重试再次把 source_id 与 FAST_KEY 交给 fast.fetch，属 sink。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;源文规定条件重试 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;fast.fetch 重试仍是工具获取边界；请求参数为 source_id 与 FAST_KEY；无网络传输证据，使用工具位置接收。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
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
        }
      ],
      &quot;location&quot;: &quot;loc_fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;源文规定条件重试 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_012 · dispatch

块：block_006；执行主体：agent_runtime；角色：[]。

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
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

## ir_013 · classify_fast_fetch_outcome

块：block_007；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_007

IR 输出：0: result_008, 1: result_009

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
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D010 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D010 | — | 0: D014 |
| 2.2 | transform | select_part | 0: D010 | — | 0: D011 |

入口／出口变化：

- `result: result_008`：未绑定 → D014
- `result: result_009`：未绑定 → D011

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_retry_outcome&quot;,
          &quot;reason&quot;: &quot;输出 result_008 绑定重试分类结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;输出 result_009 绑定选出的重试 body。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_body&quot;
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
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;重试响应的分类由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;对重试响应分类并选出 body，属转换。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;源文说明重试后仍需判断结果；未规定本地隔离或模型处理，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;需要分类并选取字段，属转换效果。&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;源文说明重试后仍需判断结果；未规定本地隔离或模型处理，按默认模式。&quot;,
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
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;根据重试响应计算成功或失败分类。&quot;,
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
      &quot;output&quot;: &quot;fast_fetch_retry_outcome&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;从重试响应中选出已有 body 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_014 · dispatch

块：block_007；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_008

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
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

## ir_015 · archive.fetch

块：block_008；执行主体：tool；角色：source, sink。

IR 输入：0: archive.fetch, 1: result_001

IR 输出：0: result_010

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
| 1.1 | 无标签数据操作 | receive | 0: D008 | tool: archive.fetch | 0: D018 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D018 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_010`：未绑定 → D018

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;archive_fetch_response&quot;,
          &quot;reason&quot;: &quot;输出 result_010 绑定 archive.fetch 返回的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0051&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_response&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;archive.fetch 工具执行回退抓取。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;返回响应，引入外部数据，属 source。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument.&quot;,
        &quot;reason&quot;: &quot;把 source_id 作为唯一参数交给 archive.fetch，属 sink；FAST_KEY 未被传入。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;源文规定调用 archive.fetch；未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument.&quot;,
          &quot;reason&quot;: &quot;archive.fetch 是工具获取边界；仅传入 source_id，未传入 FAST_KEY；未建立网络传输证据，使用工具位置接收。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_archive_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;archive_fetch_response&quot;
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
          &quot;reason&quot;: &quot;源文规定调用 archive.fetch；未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_016 · dispatch

块：block_008；执行主体：agent_runtime；角色：[]。

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
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

## ir_017 · classify_fetch_outcome

块：block_009；执行主体：agent_runtime；角色：transformer。

IR 输入：0: result_010

IR 输出：0: result_011, 1: result_012, 2: result_013

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
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 2
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D018 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D018 | — | 0: D016 |
| 2.2 | transform | select_part | 0: D018 | — | 0: D004 |
| 2.3 | transform | select_part | 0: D018 | — | 0: D020 |

入口／出口变化：

- `result: result_011`：未绑定 → D016
- `result: result_012`：未绑定 → D004
- `result: result_013`：未绑定 → D020

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
          &quot;quote&quot;: &quot;archive_fetch_outcome&quot;,
          &quot;reason&quot;: &quot;输出 result_011 绑定分类结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_body&quot;,
          &quot;reason&quot;: &quot;输出 result_012 绑定选出的 body。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_body&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_error&quot;,
          &quot;reason&quot;: &quot;输出 result_013 绑定选出的 error。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_error&quot;
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
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error; do not retry archive.fetch.&quot;,
        &quot;reason&quot;: &quot;对 archive.fetch 响应分类并选取字段由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;分类并选出 body/error，属转换。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error; do not retry archive.fetch.&quot;,
        &quot;reason&quot;: &quot;源文说明对 archive.fetch 结果区分成功与失败并返回 body 或 error；未规定本地隔离，按默认模式。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails&quot;,
        &quot;reason&quot;: &quot;根据响应判断成功/失败并提取字段，属转换效果。&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error; do not retry archive.fetch.&quot;,
          &quot;reason&quot;: &quot;源文说明对 archive.fetch 结果区分成功与失败并返回 body 或 error；未规定本地隔离，按默认模式。&quot;,
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
          &quot;quote&quot;: &quot;If archive.fetch fails&quot;,
          &quot;reason&quot;: &quot;根据响应判断 archive.fetch 成功或失败，需要计算分类结果。&quot;,
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
      &quot;output&quot;: &quot;archive_fetch_outcome&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;从成功响应中选出已有 body 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return its error&quot;,
          &quot;reason&quot;: &quot;从失败响应中选出已有 error 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_error&quot;,
      &quot;path&quot;: [
        &quot;error&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_018 · dispatch

块：block_009；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_011

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流分派。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
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

## ir_019 · append_final_status_to_local_status_file

块：block_010；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_005

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D009 | storage: status.txt | storage: status.txt: D015 → D003 (strong) |

入口／出口变化：

- `storage: status.txt`：D015 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3285fd23a5b4fbf0a00cc79a95362d25c616498c588b1061134665caae546225&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;追加状态到本地文件由运行 Skill 的 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;把最终状态写入 status.txt，使内容到达存储位置，属 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;向本地文件追加内容，符合 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;将 fast_fetch_first_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_020 · return

块：block_010；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_006

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3285fd23a5b4fbf0a00cc79a95362d25c616498c588b1061134665caae546225&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3285fd23a5b4fbf0a00cc79a95362d25c616498c588b1061134665caae546225&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0064&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通内部返回，未规定用户输出或存储/接收边界，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0064&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果；按 EM06 不推断 user_output。&quot;,
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

## ir_021 · append_final_status_to_local_status_file

块：block_011；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_008

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D014 | storage: status.txt | storage: status.txt: D015 → D013 (strong) |

入口／出口变化：

- `storage: status.txt`：D015 → D013

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e16d0cb0abbfa008c1833b3acba40aa75aaad52349624a448590773578e3081&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;重试成功路径的追加由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;把重试最终状态写入 status.txt，属 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;将 fast_fetch_retry_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_022 · return

块：block_011；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_009

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e16d0cb0abbfa008c1833b3acba40aa75aaad52349624a448590773578e3081&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8e16d0cb0abbfa008c1833b3acba40aa75aaad52349624a448590773578e3081&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0070&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0070&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
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

## ir_023 · append_final_status_to_local_status_file

块：block_012；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_011

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D016 | storage: status.txt | storage: status.txt: D015 → D002 (strong) |

入口／出口变化：

- `storage: status.txt`：D015 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1144c4f46554f45db0680eff853e5d2df802e9f8f9139ccff55c63dc474b1867&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;archive.fetch 成功路径的追加由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;把 archive.fetch 成功状态写入 status.txt，属 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;将 archive_fetch_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_024 · return

块：block_012；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_012

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1144c4f46554f45db0680eff853e5d2df802e9f8f9139ccff55c63dc474b1867&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1144c4f46554f45db0680eff853e5d2df802e9f8f9139ccff55c63dc474b1867&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0076&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0076&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
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

## ir_025 · append_final_status_to_local_status_file

块：block_013；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_011

IR 输出：[]

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D016 | storage: status.txt | storage: status.txt: D015 → D019 (strong) |

入口／出口变化：

- `storage: status.txt`：D015 → D019

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e67f492e1fdb8d41d4f73112b080a817638acb7fc3df509ec50b27f2bab1f8dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;archive.fetch 失败路径的追加由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;把 archive.fetch 失败状态写入 status.txt，属 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
        &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;将 archive_fetch_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_026 · return

块：block_013；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_013

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
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e67f492e1fdb8d41d4f73112b080a817638acb7fc3df509ec50b27f2bab1f8dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e67f492e1fdb8d41d4f73112b080a817638acb7fc3df509ec50b27f2bab1f8dd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
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
        &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0082&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0082&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
        &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
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
| D001 | data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef | known_parts |
| D002 | data_1144c4f46554f45db0680eff853e5d2df802e9f8f9139ccff55c63dc474b1867 | opaque |
| D003 | data_3285fd23a5b4fbf0a00cc79a95362d25c616498c588b1061134665caae546225 | opaque |
| D004 | data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4 | opaque |
| D005 | data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4 | known_parts |
| D006 | data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a | opaque |
| D007 | data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921 | opaque |
| D008 | data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4 | opaque |
| D009 | data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80 | opaque |
| D010 | data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab | known_parts |
| D011 | data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3 | opaque |
| D012 | data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24 | known_parts |
| D013 | data_8e16d0cb0abbfa008c1833b3acba40aa75aaad52349624a448590773578e3081 | opaque |
| D014 | data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a | opaque |
| D015 | data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a | opaque |
| D016 | data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19 | opaque |
| D017 | data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe | opaque |
| D018 | data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2 | known_parts |
| D019 | data_e67f492e1fdb8d41d4f73112b080a817638acb7fc3df509ec50b27f2bab1f8dd | opaque |
| D020 | data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7 | opaque |

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
        &quot;data&quot;: &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;,
        &quot;path&quot;: [
          &quot;FAST_KEY&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:environment&quot;,
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_1144c4f46554f45db0680eff853e5d2df802e9f8f9139ccff55c63dc474b1867&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_023&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
      &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
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
  &quot;id&quot;: &quot;data_3285fd23a5b4fbf0a00cc79a95362d25c616498c588b1061134665caae546225&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_019&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
      &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;
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
  &quot;id&quot;: &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
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
        &quot;data&quot;: &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
      &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef&quot;,
    &quot;path&quot;: [
      &quot;FAST_KEY&quot;
    ]
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
  &quot;id&quot;: &quot;data_54db8d633a2320f47061755959a3ebead605b5431d63d60bbb231331f1815921&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;,
    &quot;path&quot;: [
      &quot;source_id&quot;
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
  &quot;id&quot;: &quot;data_5f6260ce74f355a572d45fb9377314f0f913e7b86fb6025888d5b7a6a32e0d80&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D010：完整 Data 内容、来源与依赖</summary>

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
        &quot;data&quot;: &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_011&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
      &quot;data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D011：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_79829392a70aff759b22bbe0d8b63334e92018a42b9745e5a751c1dfa67096f3&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
    ]
  }
}</pre>

</details>

<details><summary>D012：完整 Data 内容、来源与依赖</summary>

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
        &quot;data&quot;: &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
        &quot;path&quot;: [
          &quot;source_id&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_87454b1e36cfeac04b42e8408f1a44a1c8d9ab1423d99565336f2e166fef9f24&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:user_request&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D013：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8e16d0cb0abbfa008c1833b3acba40aa75aaad52349624a448590773578e3081&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_021&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
      &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D014：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_9c6cbdf4e08142831afd55e2a9e2161f16991aae61e3eca3afd89a3541750d2a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_013&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_7025042c810e28e3e51bcfe325a6eff20fa203af3d0ed4f89220173a693df9ab&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D015：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:status.txt&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D016：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D017：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_d497142d1997e7a5806b3abfd58b89697aa56ac0fbb60eae38acf32255bb59fe&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_3dab72e881be8bc19388c5c046677660419191ebf7c1238ca86880838c9d33e4&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
    ]
  }
}</pre>

</details>

<details><summary>D018：完整 Data 内容、来源与依赖</summary>

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
        &quot;data&quot;: &quot;data_37b643adcaa5e00debf547fde24a6afb7e01e36ad5b2b4106022ee435a5fcab4&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;,
        &quot;path&quot;: [
          &quot;error&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:archive.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_015&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5f4ad235630d52d1212fe6107ccf5df0e20015f440cc837a65b39dc9aa6024a4&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D019：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_e67f492e1fdb8d41d4f73112b080a817638acb7fc3df509ec50b27f2bab1f8dd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_025&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_af263fb654dc2592af756a78e490b0cc68214fa0fa80c7e6a40e9157eb15d70a&quot;,
      &quot;data_b9035be64a8a10a0e6a4fae365fe0589bca6463f055cb3c271dbd19f2c48ee19&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D020：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_f937c437145a16296306f6e7e038eb719de40a8b88ff7015aaccad2685f04ac7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e3c67c93fd47eb463adf2abd53310db706672d17b7cf8faf0eb043e4099955b2&quot;,
    &quot;path&quot;: [
      &quot;error&quot;
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;
      }
    ],
    &quot;loc_archive_fetch&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;源文说明调用 archive.fetch 工具，支持该位置为工具获取边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;CFG 中 ir_015 的 external_resource 标识为 archive.fetch，支持工具身份。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;
      }
    ],
    &quot;loc_environment&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;environment&quot;,
        &quot;reason&quot;: &quot;CFG 中该指令的输入类型为 context_key 且标识为 environment，属于运行时上下文位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;源文说明从环境读取 FAST_KEY，支持该位置为环境上下文。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ],
    &quot;loc_fast_fetch&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;源文说明调用 fast.fetch 工具，支持该位置为工具获取边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;CFG 中 ir_007 的 external_resource 标识为 fast.fetch，支持工具身份。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;
      }
    ],
    &quot;loc_status_txt&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;源文说明将状态追加到本地 status.txt，支持该位置为本地文件存储。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;status.txt&quot;,
        &quot;reason&quot;: &quot;CFG 中 ir_019 的 external_resource 标识为 status.txt，支持同一文件资源。&quot;,
        &quot;ref_id&quot;: &quot;g_0063&quot;
      }
    ],
    &quot;loc_user_request&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;user_request&quot;,
        &quot;reason&quot;: &quot;CFG 中该指令的输入类型为 context_key 且标识为 user_request，属于运行时上下文位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;源文说明从用户请求读取 source_id，支持该位置为用户请求上下文。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 35,
    &quot;data_count&quot;: 20,
    &quot;description_revision&quot;: 6,
    &quot;record_count&quot;: 26
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;1c0e50b831c2c1362f24d14d2e26644c666a3e216e3a9105671a6c617c3648c2&quot;,
    &quot;mapping_sha256&quot;: &quot;59832b2155dce09d589d3fdb49b579eacfbf88ce744b87bb5b347137187c047c&quot;,
    &quot;raw_sha256&quot;: &quot;4bdfe08555c7003d150893e78010f1343e0b0b7b7dd90f9cae25c97a55a8e123&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v2&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;1c0e50b831c2c1362f24d14d2e26644c666a3e216e3a9105671a6c617c3648c2&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v2&quot;,
    &quot;events&quot;: [
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;slice&quot;,
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
          &quot;ir_001&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;slice&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          1,
          2
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
        &quot;kind&quot;: &quot;slice&quot;,
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
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;slice&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          1,
          2
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
          2
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
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0
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
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          1
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
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_015&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_015&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          3
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_019&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_021&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_021&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_021&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_023&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_023&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_023&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_025&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_025&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_025&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      }
    ],
    &quot;execution_model&quot;: {
      &quot;sha256&quot;: &quot;26cd7f0d607b13377dc5d93546b9844b02f37db89b8dd8554613ea60e5b878ce&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v3&quot;
    },
    &quot;raw_sha256&quot;: &quot;4bdfe08555c7003d150893e78010f1343e0b0b7b7dd90f9cae25c97a55a8e123&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v2&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_archive_fetch&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
          &quot;reason&quot;: &quot;源文说明调用 archive.fetch 工具，支持该位置为工具获取边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive.fetch&quot;,
          &quot;reason&quot;: &quot;CFG 中 ir_015 的 external_resource 标识为 archive.fetch，支持工具身份。&quot;,
          &quot;ref_id&quot;: &quot;g_0051&quot;
        }
      ],
      &quot;loc_environment&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;environment&quot;,
          &quot;reason&quot;: &quot;CFG 中该指令的输入类型为 context_key 且标识为 environment，属于运行时上下文位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;源文说明从环境读取 FAST_KEY，支持该位置为环境上下文。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;loc_fast_fetch&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
          &quot;reason&quot;: &quot;源文说明调用 fast.fetch 工具，支持该位置为工具获取边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast.fetch&quot;,
          &quot;reason&quot;: &quot;CFG 中 ir_007 的 external_resource 标识为 fast.fetch，支持工具身份。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;loc_status_txt&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;源文说明将状态追加到本地 status.txt，支持该位置为本地文件存储。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;status.txt&quot;,
          &quot;reason&quot;: &quot;CFG 中 ir_019 的 external_resource 标识为 status.txt，支持同一文件资源。&quot;,
          &quot;ref_id&quot;: &quot;g_0063&quot;
        }
      ],
      &quot;loc_user_request&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;user_request&quot;,
          &quot;reason&quot;: &quot;CFG 中该指令的输入类型为 context_key 且标识为 user_request，属于运行时上下文位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
          &quot;reason&quot;: &quot;源文说明从用户请求读取 source_id，支持该位置为用户请求上下文。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_archive_fetch&quot;: {
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;archive.fetch&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_015&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_environment&quot;: {
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;environment&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_003&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_fast_fetch&quot;: {
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;fast.fetch&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_011&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_status_txt&quot;: {
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;status.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_019&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_021&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_023&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_025&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      },
      &quot;loc_user_request&quot;: {
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;user_request&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ]
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;profiles&quot;: {
      &quot;ir_001&quot;: {
        &quot;effects&quot;: [
          &quot;context_read&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
            &quot;reason&quot;: &quot;源文要求执行读取动作；该动作由运行 Skill 的 agent runtime 承担，未出现 LLM 或工具参与读取的证据。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
            &quot;reason&quot;: &quot;从用户请求引入 source_id 到当前流程，属于数据来源角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
            &quot;reason&quot;: &quot;从上下文键 user_request 读取用户请求内容，符合 context_read。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;context_read&quot;
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
            &quot;reason&quot;: &quot;该指令是控制流分派，由运行 Skill 的 agent runtime 执行；未涉及内容处理。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;该分派不引入、输出或转换数据，无适用 source/sink/transformer 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派，在 effects 词表中无适用效果；不强制标为 transform。&quot;,
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
          &quot;context_read&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
            &quot;reason&quot;: &quot;读取环境变量的动作由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
            &quot;reason&quot;: &quot;从环境引入 FAST_KEY 到当前流程，属于数据来源角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
            &quot;reason&quot;: &quot;从运行时上下文环境读取 FAST_KEY，符合 context_read。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;context_read&quot;
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;
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
            &quot;reason&quot;: &quot;控制流分派由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无数据来源、去向或转换，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派，无适用效果。&quot;,
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
            &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
            &quot;reason&quot;: &quot;判断 FAST_KEY 是否存在的动作由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
            &quot;reason&quot;: &quot;根据 FAST_KEY 计算存在性布尔值，处理并改变表示，属于转换角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
            &quot;reason&quot;: &quot;计算 FAST_KEY 存在性，属于计算/转换效果。&quot;,
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
      &quot;ir_006&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分支分派由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派仅控制流向，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派，无适用效果。&quot;,
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
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;fast.fetch&quot;,
            &quot;reason&quot;: &quot;IR 操作码为 fast.fetch，实际抓取动作由该工具执行，工具是参与执行者。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
            &quot;reason&quot;: &quot;fast.fetch 返回响应内容，为当前流程引入外部数据，属 source。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
            &quot;reason&quot;: &quot;调用时把 source_id 与 FAST_KEY 作为参数交给 fast.fetch 工具，使内容到达工具这一接收边界，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
            &quot;reason&quot;: &quot;源文只表明调用 fast.fetch 工具，未提供网络通信证据，因此不归为 net_send/net_receive；工具获取在 effects 词表中无直接对应效果，空效果列表符合 EM09 的 null-effect 工具接收。&quot;,
            &quot;ref_id&quot;: &quot;EM09&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
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
            &quot;reason&quot;: &quot;控制流分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
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
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;分类与字段选取由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;对工具响应进行分类并选出 body 字段，处理内容表示，属于转换角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;需要根据响应计算成功/失败分类，属于转换效果。&quot;,
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
      &quot;ir_010&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_011&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;fast.fetch&quot;,
            &quot;reason&quot;: &quot;重试同样由 fast.fetch 工具执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0039&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;重试返回响应内容，引入外部数据，属 source。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;重试再次把 source_id 与 FAST_KEY 交给 fast.fetch，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
            &quot;reason&quot;: &quot;重试调用仍无网络传输证据，按工具位置接收，effects 无适用网络效果。&quot;,
            &quot;ref_id&quot;: &quot;EM09&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;,
          &quot;sink&quot;
        ]
      },
      &quot;ir_012&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0040&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0040&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
            &quot;ref_id&quot;: &quot;g_0040&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_013&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;重试响应的分类由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;对重试响应分类并选出 body，属转换。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;需要分类并选取字段，属转换效果。&quot;,
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
      &quot;ir_014&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0046&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0046&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
            &quot;ref_id&quot;: &quot;g_0046&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_015&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;archive.fetch&quot;,
            &quot;reason&quot;: &quot;archive.fetch 工具执行回退抓取。&quot;,
            &quot;ref_id&quot;: &quot;g_0051&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
            &quot;reason&quot;: &quot;返回响应，引入外部数据，属 source。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument.&quot;,
            &quot;reason&quot;: &quot;把 source_id 作为唯一参数交给 archive.fetch，属 sink；FAST_KEY 未被传入。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
            &quot;reason&quot;: &quot;仅有工具调用，无网络证据，按工具接收边界处理，effects 为空。&quot;,
            &quot;ref_id&quot;: &quot;EM09&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;,
          &quot;sink&quot;
        ]
      },
      &quot;ir_016&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0052&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0052&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
            &quot;ref_id&quot;: &quot;g_0052&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_017&quot;: {
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error; do not retry archive.fetch.&quot;,
            &quot;reason&quot;: &quot;对 archive.fetch 响应分类并选取字段由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;分类并选出 body/error，属转换。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails&quot;,
            &quot;reason&quot;: &quot;根据响应判断成功/失败并提取字段，属转换效果。&quot;,
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
      &quot;ir_018&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分派由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0058&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0058&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制流分派。&quot;,
            &quot;ref_id&quot;: &quot;g_0058&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_019&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;追加状态到本地文件由运行 Skill 的 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;把最终状态写入 status.txt，使内容到达存储位置，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;向本地文件追加内容，符合 fs_write。&quot;,
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
      &quot;ir_020&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0064&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通内部返回，未规定用户输出或存储/接收边界，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0064&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果；按 EM06 不推断 user_output。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_021&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;重试成功路径的追加由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;把重试最终状态写入 status.txt，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
      &quot;ir_022&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0070&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0070&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_023&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;archive.fetch 成功路径的追加由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;把 archive.fetch 成功状态写入 status.txt，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
      &quot;ir_024&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0076&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0076&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;roles&quot;: []
      },
      &quot;ir_025&quot;: {
        &quot;effects&quot;: [
          &quot;fs_write&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;archive.fetch 失败路径的追加由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;把 archive.fetch 失败状态写入 status.txt，属 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
            &quot;reason&quot;: &quot;追加写入本地文件，符合 fs_write。&quot;,
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
      &quot;ir_026&quot;: {
        &quot;effects&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;返回指令由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0082&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return&quot;,
            &quot;reason&quot;: &quot;普通内部返回，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0082&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;ordinary return does not prove user-facing output&quot;,
            &quot;reason&quot;: &quot;普通返回不是必然的用户输出，也无其他词表效果。&quot;,
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
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
                        &quot;reason&quot;: &quot;源文明确从用户请求读取；按 EM01 不建立 key-only 读取，保留整个 user_request 作为读取范围。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_user_request&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;user_request_content&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
                        &quot;reason&quot;: &quot;从读取到的用户请求内容中选出明确字段 source_id，保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;user_request_content&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;source_id&quot;,
                    &quot;path&quot;: [
                      &quot;source_id&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request and read FAST_KEY from the environment.&quot;,
                &quot;reason&quot;: &quot;源文只规定从用户请求读取 source_id，没有本地隔离或受限返回机制，按契约默认模式处理；读取范围保留 user_request 整体。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;source_id&quot;,
                &quot;reason&quot;: &quot;IR 输出 result_001 的语义名是 source_id，绑定刚选出的 source_id 局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;source_id&quot;
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
                        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
                        &quot;reason&quot;: &quot;源文明确从环境读取；按 EM01 不建立 key-only 读取，保留整个 environment 作为读取范围。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_environment&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;environment_content&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
                        &quot;reason&quot;: &quot;从环境内容中选出明确字段 FAST_KEY，保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;environment_content&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_key&quot;,
                    &quot;path&quot;: [
                      &quot;FAST_KEY&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
                &quot;reason&quot;: &quot;源文只规定从环境读取 FAST_KEY，没有给出显式本地隔离、受限返回或凭据代理机制，因此不能据此声明 local 模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs&quot;,
                &quot;reason&quot;: &quot;按 EM10，缺少显式本地执行及返回边界证据时采用 default 模式，读取输出 environment_content 保留为可能被模型观察的版本，而不是把可见版本收窄为单一键值。&quot;,
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
                &quot;quote&quot;: &quot;fast_key&quot;,
                &quot;reason&quot;: &quot;IR 输出 result_002 的语义名是 fast_key，绑定选出的 FAST_KEY 局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0015&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key&quot;
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
                        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
                        &quot;reason&quot;: &quot;根据 FAST_KEY 计算存在性布尔值，属于转换。&quot;,
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
                    &quot;output&quot;: &quot;fast_key_present&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
                &quot;reason&quot;: &quot;源文说明检查 FAST_KEY 是否存在；未规定本地隔离或模型处理，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;fast_key_present&quot;,
                &quot;reason&quot;: &quot;IR 输出 result_003 的语义名是 fast_key_present，绑定计算出的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0021&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key_present&quot;
            }
          }
        ]
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
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
                        &quot;reason&quot;: &quot;fast.fetch 是工具获取边界；返回内容来自该工具，请求参数为 source_id 与 FAST_KEY；未建立网络传输证据，因此使用工具位置接收而非 remote/net_receive。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
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
                      }
                    ],
                    &quot;location&quot;: &quot;loc_fast_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_response&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
                &quot;reason&quot;: &quot;源文规定首次调用 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式保留可能的后续模型可见性。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
                &quot;reason&quot;: &quot;IR 输出 result_004 的语义名是 fast_fetch_first_response，绑定工具返回的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0027&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_response&quot;
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
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;first attempt fails with a transient error&quot;,
                        &quot;reason&quot;: &quot;源文区分首次尝试的瞬态失败，需要根据响应计算结果分类。&quot;,
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
                    &quot;output&quot;: &quot;fast_fetch_first_outcome&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;从响应中选出已有 body 字段并保持原值，不是生成新内容。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;On either tool&#x27;s success, return that successful response&#x27;s body value unchanged&quot;,
                &quot;reason&quot;: &quot;源文说明对成功响应分类并返回 body 原值；未规定本地隔离或模型处理，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;fast_fetch_first_outcome&quot;,
                &quot;reason&quot;: &quot;输出 result_005 绑定分类结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0033&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
                &quot;reason&quot;: &quot;输出 result_006 绑定选出的 body 字段。&quot;,
                &quot;ref_id&quot;: &quot;g_0033&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_body&quot;
            }
          }
        ]
      },
      &quot;ir_010&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
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
                        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
                        &quot;reason&quot;: &quot;fast.fetch 重试仍是工具获取边界；请求参数为 source_id 与 FAST_KEY；无网络传输证据，使用工具位置接收。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
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
                      }
                    ],
                    &quot;location&quot;: &quot;loc_fast_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
                &quot;reason&quot;: &quot;源文规定条件重试 fast.fetch；工具获取未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
                &quot;reason&quot;: &quot;IR 输出 result_007 的语义名是 fast_fetch_retry_response，绑定重试工具返回的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0039&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
            }
          }
        ]
      },
      &quot;ir_012&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_013&quot;: {
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
                        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
                        &quot;reason&quot;: &quot;根据重试响应计算成功或失败分类。&quot;,
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
                    &quot;output&quot;: &quot;fast_fetch_retry_outcome&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;从重试响应中选出已有 body 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
                &quot;reason&quot;: &quot;源文说明重试后仍需判断结果；未规定本地隔离或模型处理，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;fast_fetch_retry_outcome&quot;,
                &quot;reason&quot;: &quot;输出 result_008 绑定重试分类结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0045&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
                &quot;reason&quot;: &quot;输出 result_009 绑定选出的重试 body。&quot;,
                &quot;ref_id&quot;: &quot;g_0045&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_body&quot;
            }
          }
        ]
      },
      &quot;ir_014&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_015&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument.&quot;,
                        &quot;reason&quot;: &quot;archive.fetch 是工具获取边界；仅传入 source_id，未传入 FAST_KEY；未建立网络传输证据，使用工具位置接收。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_archive_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;archive_fetch_response&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
                &quot;reason&quot;: &quot;源文规定调用 archive.fetch；未建立网络传输证据，按工具获取边界接收；未规定本地隔离，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;archive_fetch_response&quot;,
                &quot;reason&quot;: &quot;输出 result_010 绑定 archive.fetch 返回的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0051&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_response&quot;
            }
          }
        ]
      },
      &quot;ir_016&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_017&quot;: {
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
                        &quot;quote&quot;: &quot;If archive.fetch fails&quot;,
                        &quot;reason&quot;: &quot;根据响应判断 archive.fetch 成功或失败，需要计算分类结果。&quot;,
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
                    &quot;output&quot;: &quot;archive_fetch_outcome&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;从成功响应中选出已有 body 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return its error&quot;,
                        &quot;reason&quot;: &quot;从失败响应中选出已有 error 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_error&quot;,
                    &quot;path&quot;: [
                      &quot;error&quot;
                    ]
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error; do not retry archive.fetch.&quot;,
                &quot;reason&quot;: &quot;源文说明对 archive.fetch 结果区分成功与失败并返回 body 或 error；未规定本地隔离，按默认模式。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
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
                &quot;quote&quot;: &quot;archive_fetch_outcome&quot;,
                &quot;reason&quot;: &quot;输出 result_011 绑定分类结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;archive_fetch_body&quot;,
                &quot;reason&quot;: &quot;输出 result_012 绑定选出的 body。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_body&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;archive_fetch_error&quot;,
                &quot;reason&quot;: &quot;输出 result_013 绑定选出的 error。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_error&quot;
            }
          }
        ]
      },
      &quot;ir_018&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_019&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
                        &quot;reason&quot;: &quot;将 fast_fetch_first_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_status_txt&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
                &quot;reason&quot;: &quot;源文要求追加最终状态到本地文件；未规定本地隔离或模型处理，按默认模式。&quot;,
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
      &quot;ir_020&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_021&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
                        &quot;reason&quot;: &quot;将 fast_fetch_retry_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_status_txt&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
                &quot;reason&quot;: &quot;源文要求重试成功路径返回前追加最终状态；未规定本地隔离或模型处理，按默认模式。&quot;,
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
      &quot;ir_022&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_023&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
                        &quot;reason&quot;: &quot;将 archive_fetch_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_status_txt&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
                &quot;reason&quot;: &quot;源文要求 archive.fetch 成功路径返回前追加最终状态；未规定本地隔离或模型处理，按默认模式。&quot;,
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
      &quot;ir_024&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      },
      &quot;ir_025&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
                        &quot;reason&quot;: &quot;将 archive_fetch_outcome 状态追加到本地 status.txt，属于文件写入；状态值保持不变。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;loc_status_txt&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt.&quot;,
                &quot;reason&quot;: &quot;源文要求 archive.fetch 失败路径返回前追加最终状态；未规定本地隔离或模型处理，按默认模式。&quot;,
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
      &quot;ir_026&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      }
    }
  }
}</pre>

</details>

