# 基础数据传播记录

执行状态：`complete`。

IR 记录覆盖：26 / 26。

[本地可视化审查](report.html) · [唯一业务结果](doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

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

块：block_001；执行主体：agent_runtime, llm；角色：source, sink, transformer。

IR 输入：0: user_request

IR 输出：0: result_001

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: user_request | 0: D015 |
| 2.1 | model_observe | deliver | 0: D015 | model_context: agent_model_context | — |
| 3.1 | transform | select_part | 0: D015 | — | 0: D012 |

入口／出口变化：

- `result: result_001`：未绑定 → D012

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_001 的 semantic_name 为 source_id，绑定到本地选择值。&quot;,
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;read_source_id_from_user_request&quot;,
        &quot;reason&quot;: &quot;该读取动作由本地代理运行时从 user_request 上下文发起。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;For content acquired for the agent&#x27;s natural-language processing, assume that content enters model processing&quot;,
        &quot;reason&quot;: &quot;用户请求用于自然语言提取 source_id，LLM 参与处理。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;读取用户请求并把内容引入当前流程，承担 source。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;assume that content enters model processing&quot;,
        &quot;reason&quot;: &quot;请求内容进入模型处理上下文，构成至模型可见边界的 sink。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read_source_id_from_user_request&quot;,
        &quot;reason&quot;: &quot;从请求容器中选出 source_id，承担 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;读取 user_request 运行时上下文内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;context_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;assume that content enters model processing&quot;,
        &quot;reason&quot;: &quot;自然语言请求容器按 EM03 进入模型处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;source_id&quot;,
        &quot;reason&quot;: &quot;在观察后从请求容器中显式选择 source_id，属于 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;llm&quot;
    ],
    &quot;roles&quot;: [
      &quot;source&quot;,
      &quot;sink&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;read_source_id_from_user_request&quot;,
          &quot;reason&quot;: &quot;从 user_request 上下文读取请求容器。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_user_request&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;user_request_container&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;assume that content enters model processing&quot;,
          &quot;reason&quot;: &quot;按自然语言处理假设，请求容器进入模型上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM03&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;user_request_container&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;source_id&quot;,
          &quot;reason&quot;: &quot;从请求容器中显式选择 source_id。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;user_request_container&quot;
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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: environment.FAST_KEY | 0: D009 |

入口／出口变化：

- `result: result_002`：未绑定 → D009

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_002 绑定到读取的 FAST_KEY。&quot;,
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
      &quot;context_read&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;read_fast_key_from_environment&quot;,
        &quot;reason&quot;: &quot;环境变量读取由本地代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从环境读取 FAST_KEY 并引入当前流程，承担 source。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;读取运行时环境上下文中的 FAST_KEY 绑定。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
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
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;显式 key-only getter 读取 FAST_KEY 绑定。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_fast_key&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;fast_key&quot;
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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D009 | — | 0: D019 |

入口／出口变化：

- `result: result_003`：未绑定 → D019

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_003 绑定到存在性布尔值。&quot;,
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
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;check_fast_key_presence&quot;,
        &quot;reason&quot;: &quot;存在性检查由本地代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;check_fast_key_presence&quot;,
        &quot;reason&quot;: &quot;将 FAST_KEY 转换为存在性布尔结果，承担 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_key_present&quot;,
        &quot;reason&quot;: &quot;计算 FAST_KEY 是否存在的布尔结果，属于 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;check_fast_key_presence&quot;,
          &quot;reason&quot;: &quot;计算 FAST_KEY 是否存在并输出布尔结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | receive | 0: D012; 1: D009 | tool: fast.fetch | 0: D003 |

入口／出口变化：

- `result: result_004`：未绑定 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_004 绑定为 fast.fetch 首次响应。&quot;,
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
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;fast.fetch 工具执行该抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;该调用在工具边界获取 fast.fetch 响应，承担 source。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;source_id 与 FAST_KEY 作为请求参数到达 fast.fetch 工具边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。&quot;,
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
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;工具获取以 null-effect receive 表示，并记录实际请求参数 source_id 与 FAST_KEY。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
      &quot;location&quot;: &quot;loc_fast_fetch_tool&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_response&quot;
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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

块：block_005；执行主体：agent_runtime；角色：sink, transformer。

IR 输入：0: result_004

IR 输出：0: result_005, 1: result_006

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe | deliver | 0: D003 | model_context: agent_model_context | — |
| 2.1 | transform | compute | 0: D003 | — | 0: D010 |
| 2.2 | transform | compute | 0: D003 | — | 0: D008 |

入口／出口变化：

- `result: result_005`：未绑定 → D010
- `result: result_006`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_005 绑定到分类 outcome。&quot;,
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
          &quot;reason&quot;: &quot;IR 输出 result_006 绑定到提取的 body。&quot;,
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;分类提取由本地代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具响应进入模型上下文，构成至模型可见边界的 sink。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;从响应中分类并提取 outcome/body，承担 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;fast.fetch 返回内容按工具结果假设进入模型处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
        &quot;reason&quot;: &quot;对已观察响应进行分类并提取 outcome 与 body，属于 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;首次 fast.fetch 响应进入模型上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
          &quot;reason&quot;: &quot;分类首次响应得到 outcome。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;从首次响应中提取 body。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_body&quot;
    }
  ]
}</pre>

</details>

## ir_010 · dispatch

块：block_005；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_005

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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | receive | 0: D012; 1: D009 | tool: fast.fetch | 0: D005 |

入口／出口变化：

- `result: result_007`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_007 绑定为 fast.fetch 重试响应。&quot;,
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
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;fast.fetch 工具执行重试抓取。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;重试调用在工具边界获取 fast.fetch 响应，承担 source。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_key&quot;,
        &quot;reason&quot;: &quot;重试调用同样以 source_id 和 FAST_KEY 为参数到达 fast.fetch 工具边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。&quot;,
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
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;重试工具获取以 null-effect receive 表示，并记录实际请求参数 source_id 与 FAST_KEY。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
      &quot;location&quot;: &quot;loc_fast_fetch_tool&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
    }
  ]
}</pre>

</details>

## ir_012 · dispatch

块：block_006；执行主体：agent_runtime；角色：[]。

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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

块：block_007；执行主体：agent_runtime；角色：sink, transformer。

IR 输入：0: result_007

IR 输出：0: result_008, 1: result_009

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe | deliver | 0: D005 | model_context: agent_model_context | — |
| 2.1 | transform | compute | 0: D005 | — | 0: D016 |
| 2.2 | transform | compute | 0: D005 | — | 0: D018 |

入口／出口变化：

- `result: result_008`：未绑定 → D016
- `result: result_009`：未绑定 → D018

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_008 绑定到重试分类 outcome。&quot;,
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
          &quot;reason&quot;: &quot;IR 输出 result_009 绑定到重试提取的 body。&quot;,
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;重试响应分类由本地代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0045&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;重试工具响应进入模型上下文，构成至模型可见边界的 sink。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;从重试响应中分类并提取 outcome/body，承担 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0045&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;fast.fetch 重试返回内容按工具结果假设进入模型处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
        &quot;reason&quot;: &quot;对已观察重试响应进行分类并提取 outcome 与 body，属于 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0045&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;fast.fetch 重试响应进入模型上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;classify_fast_fetch_outcome&quot;,
          &quot;reason&quot;: &quot;分类重试响应得到 outcome。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;从重试响应中提取 body。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_body&quot;
    }
  ]
}</pre>

</details>

## ir_014 · dispatch

块：block_007；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_008

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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | receive | 0: D012 | tool: archive.fetch | 0: D004 |

入口／出口变化：

- `result: result_010`：未绑定 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_010 绑定为 archive.fetch 响应。&quot;,
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
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;archive.fetch 工具执行该抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;该调用在工具边界获取 archive.fetch 响应，承担 source。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;仅 source_id 作为参数到达 archive.fetch 工具边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;未建立远程网络证据，工具获取以 null-effect receive 表示，effects 无适用枚举值。&quot;,
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
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;use receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;archive.fetch 工具获取以 null-effect receive 表示，并记录实际请求参数 source_id。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_archive_fetch_tool&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;archive_fetch_response&quot;
    }
  ]
}</pre>

</details>

## ir_016 · dispatch

块：block_008；执行主体：agent_runtime；角色：[]。

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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

块：block_009；执行主体：agent_runtime；角色：sink, transformer。

IR 输入：0: result_010

IR 输出：0: result_011, 1: result_012, 2: result_013

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe | deliver | 0: D004 | model_context: agent_model_context | — |
| 2.1 | transform | compute | 0: D004 | — | 0: D001 |
| 2.2 | transform | compute | 0: D004 | — | 0: D014 |
| 2.3 | transform | compute | 0: D004 | — | 0: D002 |

入口／出口变化：

- `result: result_011`：未绑定 → D001
- `result: result_012`：未绑定 → D014
- `result: result_013`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
          &quot;reason&quot;: &quot;IR 输出 result_011 绑定到 archive.fetch 分类 outcome。&quot;,
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
          &quot;reason&quot;: &quot;IR 输出 result_012 绑定到 archive.fetch body。&quot;,
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
          &quot;reason&quot;: &quot;IR 输出 result_013 绑定到 archive.fetch error。&quot;,
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;classify_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;archive.fetch 响应分类由本地代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0057&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;archive.fetch 响应进入模型上下文，构成至模型可见边界的 sink。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;classify_fetch_outcome&quot;,
        &quot;reason&quot;: &quot;分类并提取 outcome/body/error，承担 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0057&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;archive.fetch 返回内容按工具结果假设进入模型处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;archive_fetch_body&quot;,
        &quot;reason&quot;: &quot;对已观察响应进行分类并提取 outcome、body 与 error，属于 transform。&quot;,
        &quot;ref_id&quot;: &quot;g_0057&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;archive.fetch 响应进入模型上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;classify_fetch_outcome&quot;,
          &quot;reason&quot;: &quot;分类 archive.fetch 响应得到 outcome。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_body&quot;,
          &quot;reason&quot;: &quot;从 archive.fetch 响应中提取 body。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;archive_fetch_body&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_error&quot;,
          &quot;reason&quot;: &quot;从 archive.fetch 响应中提取 error。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;archive_fetch_error&quot;
    }
  ]
}</pre>

</details>

## ir_018 · dispatch

块：block_009；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_011

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
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;reason&quot;: &quot;dispatch 由本地代理运行时执行控制转移。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派不引入、传递或转换内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不属于 effects 词汇，未发现适用效果；这不表示 IR 可跳过。&quot;,
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

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D010 | storage: local status.txt | storage: local status.txt: D007 → D006 (strong) |

入口／出口变化：

- `storage: local status.txt`：D007 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;quote&quot;: &quot;append_final_status_to_local_status_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0063&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;最终状态内容到达本地文件存储位置，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加内容，属于 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;向本地 status.txt 追加最终状态。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_file&quot;
    }
  ]
}</pre>

</details>

## ir_020 · return

块：block_010；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_006

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D008 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
      &quot;user_output&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;返回操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0064&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将成功响应 body 提供给用户可见输出边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;该最终返回将 body 提供给用户，属于 user_output。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;user_output&quot;
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
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;将首次 fast.fetch 成功响应 body 提供给用户。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_021 · append_final_status_to_local_status_file

块：block_011；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_008

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D016 | storage: local status.txt | storage: local status.txt: D007 → D011 (strong) |

入口／出口变化：

- `storage: local status.txt`：D007 → D011

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;quote&quot;: &quot;append_final_status_to_local_status_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0069&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;重试最终状态内容到达本地文件存储位置，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加内容，属于 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;向本地 status.txt 追加重试最终状态。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_file&quot;
    }
  ]
}</pre>

</details>

## ir_022 · return

块：block_011；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_009

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D018 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
      &quot;user_output&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;返回操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0070&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将重试成功响应 body 提供给用户可见输出边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;该最终返回将 body 提供给用户，属于 user_output。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;user_output&quot;
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
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;将 fast.fetch 重试成功响应 body 提供给用户。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_023 · append_final_status_to_local_status_file

块：block_012；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_011

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D001 | storage: local status.txt | storage: local status.txt: D007 → D017 (strong) |

入口／出口变化：

- `storage: local status.txt`：D007 → D017

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;quote&quot;: &quot;append_final_status_to_local_status_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0075&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;archive.fetch 成功状态内容到达本地文件存储位置，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加内容，属于 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;向本地 status.txt 追加 archive.fetch 成功状态。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_file&quot;
    }
  ]
}</pre>

</details>

## ir_024 · return

块：block_012；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_012

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D014 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
      &quot;user_output&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;返回操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0076&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将 archive.fetch 成功响应 body 提供给用户可见输出边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;该最终返回将 body 提供给用户，属于 user_output。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;user_output&quot;
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
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;将 archive.fetch 成功响应 body 提供给用户。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_025 · append_final_status_to_local_status_file

块：block_013；执行主体：agent_runtime；角色：sink。

IR 输入：0: status.txt, 1: result_011

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D001 | storage: local status.txt | storage: local status.txt: D007 → D013 (strong) |

入口／出口变化：

- `storage: local status.txt`：D007 → D013

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
        &quot;quote&quot;: &quot;append_final_status_to_local_status_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0081&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;archive.fetch 失败状态内容到达本地文件存储位置，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加内容，属于 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;向本地 status.txt 追加 archive.fetch 失败状态。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_status_file&quot;
    }
  ]
}</pre>

</details>

## ir_026 · return

块：block_013；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_013

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D002 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment.FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;local status.txt&quot;
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
      &quot;user_output&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;返回操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0082&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return its error&quot;,
        &quot;reason&quot;: &quot;将 archive.fetch 错误提供给用户可见输出边界，承担 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return its error&quot;,
        &quot;reason&quot;: &quot;该最终返回将错误提供给用户，属于 user_output。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;user_output&quot;
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
          &quot;quote&quot;: &quot;return its error&quot;,
          &quot;reason&quot;: &quot;将 archive.fetch 错误提供给用户。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411 | opaque |
| D002 | data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f | opaque |
| D003 | data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551 | opaque |
| D004 | data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927 | opaque |
| D005 | data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296 | opaque |
| D006 | data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c | opaque |
| D007 | data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7 | opaque |
| D008 | data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d | opaque |
| D009 | data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971 | opaque |
| D010 | data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d | opaque |
| D011 | data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e | opaque |
| D012 | data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe | opaque |
| D013 | data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a | opaque |
| D014 | data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83 | opaque |
| D015 | data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61 | known_parts |
| D016 | data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b | opaque |
| D017 | data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9 | opaque |
| D018 | data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99 | opaque |
| D019 | data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e | opaque |

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
  &quot;id&quot;: &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_23741b2953e432341b6c9a18f83638d6360b21db92228652428aacb0e8c5a29f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 2]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
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
  &quot;id&quot;: &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
      &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
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
  &quot;id&quot;: &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:archive.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_015&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;
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
  &quot;id&quot;: &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_011&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
      &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
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
  &quot;id&quot;: &quot;data_464932bbbb48673a5e668eb6a044c70911e9ef909c1bd11dd9ca5819d1794e7c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_019&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
      &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;
    ],
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
  &quot;id&quot;: &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:local status.txt&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
  &quot;id&quot;: &quot;data_53c370964b1730441fa638564cf1ae8701ecaff45443951ab92fda255347de1d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:environment.FAST_KEY&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_651a9e0e5025ef4b652c346020bbaf1a5dc10236c3c5acbc5705fc530775997d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_247a439fbcc7f37406fdbe6cfd5c9cd447dc82777a348c0644a35ff4d6ef0551&quot;
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
  &quot;id&quot;: &quot;data_66da031549e737720dcb57d4cea1bef618482f1795d8faa756afcce01e5e628e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_021&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
      &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;,
    &quot;path&quot;: [
      &quot;source_id&quot;
    ]
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
  &quot;id&quot;: &quot;data_69bf7d747704dfcc9c7424c16fb0798fe3a44f9704679c46abd3a37c3bf8e15a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_025&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
      &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
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
  &quot;id&quot;: &quot;data_6cfe5f432cf90889b2903af8f7479bfd238db387692ed73b2a7e314e2f048a83&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_3469a4cab63348bb797207c263062ca8370e59ef32bab47cbe7c517762cf7927&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_698c3ad5c43f686a9469de371d3c5e49f7bb05478b07b27459556ebb17dc5abe&quot;,
        &quot;path&quot;: [
          &quot;source_id&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_7470120887249282c40b77cce8c265a5e995b5d35496532c7f4181d0f61cbf61&quot;,
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
  &quot;id&quot;: &quot;data_929975bd2e8b46601be8307976e245cf3cd1aad56372385cc71e98e205bd9b1b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_013&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
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
  &quot;id&quot;: &quot;data_9bb19fbc4fdcafc0245fdeea0904f0ac2ab525da01f060d1bb2f96ac699d40d9&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_023&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4aa347f8e214eeeb106b47a66a83dc2703d3aea1e1a8269bc74d07fc46487ee7&quot;,
      &quot;data_04b7eceb5e8e9e65b749e6eb903dbe097cb8fb10ff61a4cffbeb5396b29e3411&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_ba2eb99184c139da2d730834d090cbd0d134be63c1ca6573268b7e6cd48f7b99&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_013&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_34ff83244c19b77be7b619036490f7c42b022389bf696a9da0b09651e1273296&quot;
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
  &quot;id&quot;: &quot;data_ddb76a9d5a281ea48b2bc0697873d1a9a6429f4f2a452b5fd844f0fc5fe6900e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5f3d5eb95ee85fd2a5e6eb520ce33acda2e9c6f299bcc341af080098f2822971&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;loc_archive_fetch_tool&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;archive.fetch 是备用工具抓取边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;IR 外部资源标识为 archive.fetch。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;
      }
    ],
    &quot;loc_environment&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;环境上下文是 FAST_KEY 的来源容器。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;environment&quot;,
        &quot;reason&quot;: &quot;ir_003 输入 context_key 标识为 environment。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      }
    ],
    &quot;loc_fast_fetch_tool&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;fast.fetch 是工具抓取边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;IR 外部资源标识为 fast.fetch。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;
      }
    ],
    &quot;loc_fast_key&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;显式 key-only getter 获取环境变量 FAST_KEY 绑定。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read_fast_key_from_environment&quot;,
        &quot;reason&quot;: &quot;IR opcode 表明读取的是 FAST_KEY 而非整个环境。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      }
    ],
    &quot;loc_model_context&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;模型上下文是工具返回内容默认进入的处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;assume that content enters model processing&quot;,
        &quot;reason&quot;: &quot;自然语言处理内容按固定模型进入模型上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;
      }
    ],
    &quot;loc_status_file&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;本地 status.txt 是状态追加的存储位置。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;status.txt&quot;,
        &quot;reason&quot;: &quot;IR 外部资源标识为 status.txt。&quot;,
        &quot;ref_id&quot;: &quot;g_0063&quot;
      }
    ],
    &quot;loc_user&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;最终返回内容面向发起请求的用户。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ],
    &quot;loc_user_request&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;该位置是用户请求容器，ir_001 从其中读取 source_id。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;user_request&quot;,
        &quot;reason&quot;: &quot;IR 输入 context_key 标识为 user_request。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 22,
    &quot;data_count&quot;: 19,
    &quot;description_revision&quot;: 1,
    &quot;record_count&quot;: 26
  }
}</pre>

</details>

