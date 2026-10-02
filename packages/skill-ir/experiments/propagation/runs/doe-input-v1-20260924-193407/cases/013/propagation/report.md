# 基础数据传播记录

执行状态：`complete`。

IR 记录覆盖：18 / 18。

[本地可视化审查](report.html) · [唯一业务结果](doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。

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
    &quot;ir_018&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: [
    {
      &quot;code&quot;: &quot;annotation_unresolved&quot;,
      &quot;items&quot;: [
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_012&quot;,
          &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_014&quot;,
          &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_016&quot;,
          &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_018&quot;,
          &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
        }
      ],
      &quot;reason&quot;: &quot;保留标注未决项；传播完成不表示未决已解决。&quot;
    }
  ]
}</pre>

</details>

**标注仍有未决，传播完成不消除这些未决。**

<details><summary>未决项</summary>

<pre>[
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_012&quot;,
    &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_014&quot;,
    &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_016&quot;,
    &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_018&quot;,
    &quot;reason&quot;: &quot;return 的目标未明确为最终用户或内部调用方；普通 return 本身不证明面向用户输出，因此无法确定应标为 user_output、model_observe 还是无适用效果。&quot;
  }
]</pre>

</details>

## ir_001 · read_source_id

块：block_001；执行主体：agent_runtime；角色：source。

IR 输入：0: source_id

IR 输出：0: result_001

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: source_id | 0: D018 |

入口／出口变化：

- `result: result_001`：未绑定 → D018

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;quote&quot;: &quot;result_001&quot;,
          &quot;reason&quot;: &quot;输出 result_001/source_id 绑定到读取得到的本地值，原样转发。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir001_source_id&quot;
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
        &quot;quote&quot;: &quot;read_source_id&quot;,
        &quot;reason&quot;: &quot;该 IR 是本地读取运行时上下文键的操作，由代理运行时执行，不是模型或工具。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;从用户请求/运行时上下文引入 source_id 到当前流程。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;输入类型 context_key 表明该操作获取运行时上下文内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;context_key&quot;,
          &quot;reason&quot;: &quot;读取运行时上下文键 source_id。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_rt_source_id&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;v_ir001_source_id&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
        &quot;reason&quot;: &quot;本地控制分发由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转，不引入、写出或转换内容数据，因此无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;控制流操作在给定效果词汇中没有适用项，不强制标记 transform。&quot;,
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

## ir_003 · read_fast_key

块：block_002；执行主体：agent_runtime；角色：source, transformer。

IR 输入：0: FAST_KEY

IR 输出：0: result_002, 1: result_003

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: FAST_KEY | 0: D008 |
| 2.1 | transform | compute | 0: D008 | — | 0: D006 |

入口／出口变化：

- `result: result_002`：未绑定 → D008
- `result: result_003`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;quote&quot;: &quot;result_002&quot;,
          &quot;reason&quot;: &quot;输出 fast_key 绑定到读取值，原样转发。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir003_fast_key&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_003&quot;,
          &quot;reason&quot;: &quot;输出 fast_key_present 绑定到派生的存在性结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir003_fast_key_present&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;context_read&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;read_fast_key&quot;,
        &quot;reason&quot;: &quot;该 IR 是本地读取环境/运行时上下文的操作，由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从环境读取 FAST_KEY，将凭据内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_key_present&quot;,
        &quot;reason&quot;: &quot;输出存在性布尔值，改变表示形式，属于本地转换。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;输入类型 context_key 表明读取运行时上下文/环境变量。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;context_read&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_key_present&quot;,
        &quot;reason&quot;: &quot;由读取的 FAST_KEY 派生 fast_key_present 布尔值。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;transform&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;source&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;context_key&quot;,
          &quot;reason&quot;: &quot;读取环境/运行时上下文中的 FAST_KEY。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_rt_FAST_KEY&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;v_ir003_fast_key&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_key_present&quot;,
          &quot;reason&quot;: &quot;由 FAST_KEY 派生存在性布尔值。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir003_fast_key&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir003_fast_key_present&quot;
    }
  ]
}</pre>

</details>

## ir_004 · dispatch

块：block_002；执行主体：agent_runtime；角色：[]。

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
        &quot;reason&quot;: &quot;本地控制分发由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅依据存在性结果进行控制跳转，不引入、写出或转换内容数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在给定效果词汇中没有适用项。&quot;,
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

## ir_005 · fast.fetch

块：block_003；执行主体：tool, llm；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_004, 1: result_005, 2: result_006

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | 0: D018; 1: D008 | remote: fast.fetch | — |
| 2.1 | net_receive | receive | 0: D018; 1: D008 | remote: fast.fetch | 0: D010 |
| 2.2 | net_receive | compute | 0: D010 | — | 0: D009 |
| 2.3 | net_receive | compute | 0: D010 | — | 0: D005 |
| 2.4 | net_receive | compute | 0: D010 | — | 0: D016 |
| 3.1 | model_observe | deliver | 0: D010 | model_context: LLM context | — |

入口／出口变化：

- `result: result_004`：未绑定 → D009
- `result: result_005`：未绑定 → D005
- `result: result_006`：未绑定 → D016

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;输出 body 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir005_body&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_error&quot;,
          &quot;reason&quot;: &quot;输出 error 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir005_error&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_status&quot;,
          &quot;reason&quot;: &quot;输出 status 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir005_status&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;net_send&quot;,
      &quot;net_receive&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;fast.fetch 工具执行该抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，模型参与结果观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
        &quot;reason&quot;: &quot;接收远程响应体，将外部内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;将请求参数发送到远程 fast.fetch，形成接收方边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;向 fast.fetch 发送 source_id 和 FAST_KEY 请求参数。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
        &quot;reason&quot;: &quot;该调用接收远程响应体、错误和状态。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;net_receive&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文，形成模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;tool&quot;,
      &quot;llm&quot;
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
          &quot;reason&quot;: &quot;将 source_id 与 FAST_KEY 作为请求参数发送到远程 fast.fetch。&quot;,
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
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_remote_fast_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;接收 fast.fetch 返回的响应内容。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
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
      &quot;location&quot;: &quot;loc_remote_fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;v_ir005_result&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 body 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir005_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir005_body&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_error&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 error 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir005_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir005_error&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_status&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 status 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir005_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir005_status&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir005_result&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_006

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
        &quot;reason&quot;: &quot;本地控制分发由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅依据状态结果进行控制跳转，不引入、写出或转换内容数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在给定效果词汇中没有适用项。&quot;,
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

块：block_004；执行主体：tool, llm；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_007, 1: result_008, 2: result_009

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | 0: D018; 1: D008 | remote: fast.fetch | — |
| 2.1 | net_receive | receive | 0: D018; 1: D008 | remote: fast.fetch | 0: D002 |
| 2.2 | net_receive | compute | 0: D002 | — | 0: D003 |
| 2.3 | net_receive | compute | 0: D002 | — | 0: D020 |
| 2.4 | net_receive | compute | 0: D002 | — | 0: D011 |
| 3.1 | model_observe | deliver | 0: D002 | model_context: LLM context | — |

入口／出口变化：

- `result: result_007`：未绑定 → D003
- `result: result_008`：未绑定 → D020
- `result: result_009`：未绑定 → D011

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;输出重试 body 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir007_body&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_error&quot;,
          &quot;reason&quot;: &quot;输出重试 error 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir007_error&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_status&quot;,
          &quot;reason&quot;: &quot;输出重试 status 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir007_status&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;net_send&quot;,
      &quot;net_receive&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;fast.fetch 工具执行该重试抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，模型参与结果观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
        &quot;reason&quot;: &quot;接收远程重试响应体，将外部内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once&quot;,
        &quot;reason&quot;: &quot;重试调用向远程 fast.fetch 发送请求参数，形成接收方边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_key&quot;,
        &quot;reason&quot;: &quot;重试 IR 输入包含 fast_key 以及 source_id，并作为 fast.fetch 请求参数发送。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
        &quot;reason&quot;: &quot;该重试调用接收远程响应体、错误和状态。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;net_receive&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文，形成模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;tool&quot;,
      &quot;llm&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_key&quot;,
          &quot;reason&quot;: &quot;重试 IR 输入包含 fast_key 以及 source_id，并作为 fast.fetch 请求参数发送。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
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
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_remote_fast_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;接收 fast.fetch 重试返回的响应内容。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
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
      &quot;location&quot;: &quot;loc_remote_fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;v_ir007_result&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;从重试工具响应中保守派生 body 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir007_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir007_body&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_error&quot;,
          &quot;reason&quot;: &quot;从重试工具响应中保守派生 error 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir007_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir007_error&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_status&quot;,
          &quot;reason&quot;: &quot;从重试工具响应中保守派生 status 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir007_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir007_status&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir007_result&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
        &quot;reason&quot;: &quot;本地控制分发由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅依据重试状态进行控制跳转，不引入、写出或转换内容数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在给定效果词汇中没有适用项。&quot;,
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

## ir_009 · archive.fetch

块：block_005；执行主体：tool, llm；角色：source, sink。

IR 输入：0: archive.fetch, 1: result_001

IR 输出：0: result_010, 1: result_011, 2: result_012

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | 0: D018 | remote: archive.fetch | — |
| 2.1 | net_receive | receive | 0: D018 | remote: archive.fetch | 0: D015 |
| 2.2 | net_receive | compute | 0: D015 | — | 0: D014 |
| 2.3 | net_receive | compute | 0: D015 | — | 0: D004 |
| 2.4 | net_receive | compute | 0: D015 | — | 0: D012 |
| 3.1 | model_observe | deliver | 0: D015 | model_context: LLM context | — |

入口／出口变化：

- `result: result_010`：未绑定 → D014
- `result: result_011`：未绑定 → D004
- `result: result_012`：未绑定 → D012

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;quote&quot;: &quot;archive_body&quot;,
          &quot;reason&quot;: &quot;输出 archive body 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir009_body&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_error&quot;,
          &quot;reason&quot;: &quot;输出 archive error 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir009_error&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_status&quot;,
          &quot;reason&quot;: &quot;输出 archive status 绑定到工具响应派生结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;v_ir009_status&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;net_send&quot;,
      &quot;net_receive&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;archive.fetch 工具执行该抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，模型参与结果观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;archive_body&quot;,
        &quot;reason&quot;: &quot;接收 archive.fetch 响应体，将外部内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;pass source_id as its only argument&quot;,
        &quot;reason&quot;: &quot;将 source_id 发送到远程 archive.fetch，形成接收方边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;pass source_id as its only argument&quot;,
        &quot;reason&quot;: &quot;archive.fetch 请求只发送 source_id 作为参数，不发送 FAST_KEY。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;archive_body&quot;,
        &quot;reason&quot;: &quot;接收 archive.fetch 的响应体、错误和状态。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;net_receive&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文，形成模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;tool&quot;,
      &quot;llm&quot;
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
          &quot;quote&quot;: &quot;pass source_id as its only argument&quot;,
          &quot;reason&quot;: &quot;archive.fetch 请求只发送 source_id 作为参数，不发送 FAST_KEY。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_remote_archive_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_body&quot;,
          &quot;reason&quot;: &quot;接收 archive.fetch 返回的响应内容。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_remote_archive_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;v_ir009_result&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_body&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 body 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir009_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir009_body&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_error&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 error 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir009_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir009_error&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_status&quot;,
          &quot;reason&quot;: &quot;从工具响应中保守派生 status 输出，不声明精确字段路径。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir009_result&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;v_ir009_status&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 处理上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;v_ir009_result&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_model_context&quot;
    }
  ]
}</pre>

</details>

## ir_010 · dispatch

块：block_005；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_012

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
        &quot;reason&quot;: &quot;本地控制分发由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅依据 archive 状态进行控制跳转，不引入、写出或转换内容数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在给定效果词汇中没有适用项。&quot;,
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

## ir_011 · append_status_to_local_file

块：block_006；执行主体：agent_runtime；角色：sink。

IR 输入：0: local status.txt, 1: result_006

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D016 | storage: local status.txt | storage: local status.txt: D019 → D013 (strong) |

入口／出口变化：

- `storage: local status.txt`：D019 → D013

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b4e7c9efa470d7fbc9e0c1cef027be085421832ee72cc3d2e58ae2a5f5f710b6&quot;
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
        &quot;quote&quot;: &quot;append_status_to_local_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;将状态内容写入本地存储位置，形成存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加内容，属于文件写入。&quot;,
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
          &quot;reason&quot;: &quot;将状态追加到本地 status.txt，不读取旧内容也不覆盖。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_storage_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_012 · return

块：block_006；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_004

IR 输出：[]

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b4e7c9efa470d7fbc9e0c1cef027be085421832ee72cc3d2e58ae2a5f5f710b6&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b4e7c9efa470d7fbc9e0c1cef027be085421832ee72cc3d2e58ae2a5f5f710b6&quot;
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
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;本地返回控制由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将成功响应体交给调用方，形成可见性边界；未证明直接面向用户。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_013 · append_status_to_local_file

块：block_007；执行主体：agent_runtime；角色：sink。

IR 输入：0: local status.txt, 1: result_009

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D011 | storage: local status.txt | storage: local status.txt: D019 → D017 (strong) |

入口／出口变化：

- `storage: local status.txt`：D019 → D017

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d7e6ffcf906083fa53c19a391d8c4f87a95a4dafcbc77484073659b57391e062&quot;
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
        &quot;quote&quot;: &quot;append_status_to_local_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0045&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;将重试成功状态写入本地存储位置，形成存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加重试成功状态，属于文件写入。&quot;,
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
          &quot;reason&quot;: &quot;将重试成功状态追加到本地 status.txt。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_storage_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_014 · return

块：block_007；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_007

IR 输出：[]

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d7e6ffcf906083fa53c19a391d8c4f87a95a4dafcbc77484073659b57391e062&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d7e6ffcf906083fa53c19a391d8c4f87a95a4dafcbc77484073659b57391e062&quot;
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
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;本地返回控制由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将重试成功响应体交给调用方，形成可见性边界；未证明直接面向用户。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_015 · append_status_to_local_file

块：block_008；执行主体：agent_runtime；角色：sink。

IR 输入：0: local status.txt, 1: result_012

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D012 | storage: local status.txt | storage: local status.txt: D019 → D007 (strong) |

入口／出口变化：

- `storage: local status.txt`：D019 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_85648753082bfab23e17d655f48fd93b64fa1a46eb1922aee745ce68c2ff0370&quot;
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
        &quot;quote&quot;: &quot;append_status_to_local_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;将 archive 成功状态写入本地存储位置，形成存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加 archive 成功状态，属于文件写入。&quot;,
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
          &quot;reason&quot;: &quot;将 archive 成功状态追加到本地 status.txt。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_storage_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_016 · return

块：block_008；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_010

IR 输出：[]

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_85648753082bfab23e17d655f48fd93b64fa1a46eb1922aee745ce68c2ff0370&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_85648753082bfab23e17d655f48fd93b64fa1a46eb1922aee745ce68c2ff0370&quot;
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
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;本地返回控制由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;将 archive 成功响应体交给调用方，形成可见性边界；未证明直接面向用户。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: []
}</pre>

</details>

## ir_017 · append_status_to_local_file

块：block_009；执行主体：agent_runtime；角色：sink。

IR 输入：0: local status.txt, 1: result_012

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D012 | storage: local status.txt | storage: local status.txt: D019 → D001 (strong) |

入口／出口变化：

- `storage: local status.txt`：D019 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_086cbad9d94893b89cc8860645bb3552b5449d9fc46c924d72710ca03c1f0ef6&quot;
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
        &quot;quote&quot;: &quot;append_status_to_local_file&quot;,
        &quot;reason&quot;: &quot;本地文件追加操作由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0057&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;将 archive 失败状态写入本地存储位置，形成存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地 status.txt 追加 archive 失败状态，属于文件写入。&quot;,
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
          &quot;reason&quot;: &quot;将 archive 失败状态追加到本地 status.txt。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;loc_storage_status_txt&quot;
    }
  ]
}</pre>

</details>

## ir_018 · return

块：block_009；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_011

IR 输出：[]

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_086cbad9d94893b89cc8860645bb3552b5449d9fc46c924d72710ca03c1f0ef6&quot;
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
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;FAST_KEY&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_086cbad9d94893b89cc8860645bb3552b5449d9fc46c924d72710ca03c1f0ef6&quot;
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
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;本地返回控制由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return its error&quot;,
        &quot;reason&quot;: &quot;将 archive 错误交给调用方，形成可见性边界；未证明直接面向用户。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;
    ]
  },
  &quot;steps&quot;: []
}</pre>

</details>

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | data_086cbad9d94893b89cc8860645bb3552b5449d9fc46c924d72710ca03c1f0ef6 | opaque |
| D002 | data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3 | opaque |
| D003 | data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b | opaque |
| D004 | data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287 | opaque |
| D005 | data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a | opaque |
| D006 | data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f | opaque |
| D007 | data_85648753082bfab23e17d655f48fd93b64fa1a46eb1922aee745ce68c2ff0370 | opaque |
| D008 | data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1 | opaque |
| D009 | data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e | opaque |
| D010 | data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa | opaque |
| D011 | data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379 | opaque |
| D012 | data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d | opaque |
| D013 | data_b4e7c9efa470d7fbc9e0c1cef027be085421832ee72cc3d2e58ae2a5f5f710b6 | opaque |
| D014 | data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52 | opaque |
| D015 | data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd | opaque |
| D016 | data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122 | opaque |
| D017 | data_d7e6ffcf906083fa53c19a391d8c4f87a95a4dafcbc77484073659b57391e062 | opaque |
| D018 | data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be | opaque |
| D019 | data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd | opaque |
| D020 | data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff | opaque |

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
  &quot;id&quot;: &quot;data_086cbad9d94893b89cc8860645bb3552b5449d9fc46c924d72710ca03c1f0ef6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_017&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
      &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
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
  &quot;id&quot;: &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
      &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
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
  &quot;id&quot;: &quot;data_4cfa6c303f741603d89d4d4a87599a17db8901fee98007739caa41ac9b749f2b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;
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
  &quot;id&quot;: &quot;data_614a29d9fde6d3591f9131931be94e68d0098e8593883ccef2f80170b0da6287&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 2]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;
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
  &quot;id&quot;: &quot;data_72d79f7dee0e5d20a3cad9fa8c360a99861cd301f09160dc5c42d170dd4da23a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 2]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;
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
  &quot;id&quot;: &quot;data_7fcd0bf467a3e88ad1b9d83577bf01b3094608100d8f85aafd0165639982309f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_003&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
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
  &quot;id&quot;: &quot;data_85648753082bfab23e17d655f48fd93b64fa1a46eb1922aee745ce68c2ff0370&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_015&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
      &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;
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
  &quot;id&quot;: &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:FAST_KEY&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
  &quot;id&quot;: &quot;data_93cb59a8378ee26b4535f6410218491ed9f10f58965c0c8ea329a3bbabf8302e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
      &quot;data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1&quot;
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
  &quot;id&quot;: &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 3]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;
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
  &quot;id&quot;: &quot;data_a3e63534007fb42d73cafaf2c29c43718701463c430a1696dd5950141e5a981d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 3]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;
    ],
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
  &quot;id&quot;: &quot;data_b4e7c9efa470d7fbc9e0c1cef027be085421832ee72cc3d2e58ae2a5f5f710b6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_011&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
      &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;
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
  &quot;id&quot;: &quot;data_bafb32b599f26c13d556afa210bd4b562c2c2607a6f2a290b892a5da738d1e52&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;
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
  &quot;id&quot;: &quot;data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:archive.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;
    ],
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
  &quot;id&quot;: &quot;data_d058f384828fc2172b1183cbf36943c79d3a74e40225ed45f5be48b212688122&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 3]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa&quot;
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
  &quot;id&quot;: &quot;data_d7e6ffcf906083fa53c19a391d8c4f87a95a4dafcbc77484073659b57391e062&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_013&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;local status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
      &quot;data_9fe65d98e7a824def2b65efe7cdb0725df750f75023cfe1282bf149a824ad379&quot;
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
  &quot;id&quot;: &quot;data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:source_id&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
  &quot;id&quot;: &quot;data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd&quot;,
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
  &quot;id&quot;: &quot;data_f2cb6459c3d425e708aad9c4453ebcae111a6641ce6a4995bf32f9c237de41ff&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 2]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;loc_model_context&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default.&quot;,
        &quot;reason&quot;: &quot;执行模型假设工具返回内容默认进入 LLM 上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;
      }
    ],
    &quot;loc_remote_archive_fetch&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;IR 操作码和外部资源标识为 archive.fetch。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument.&quot;,
        &quot;reason&quot;: &quot;源描述调用 archive.fetch。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ],
    &quot;loc_remote_fast_fetch&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;IR 操作码和外部资源标识为 fast.fetch。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;源描述通过 fast.fetch 进行抓取。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ],
    &quot;loc_rt_FAST_KEY&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;源步骤一从环境读取 FAST_KEY。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;CFG 输入类型为 context_key，标识运行时上下文位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      }
    ],
    &quot;loc_rt_source_id&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;源步骤一从用户请求读取 source_id。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;context_key&quot;,
        &quot;reason&quot;: &quot;CFG 输入类型为 context_key，标识运行时上下文位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      }
    ],
    &quot;loc_storage_status_txt&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;local status.txt&quot;,
        &quot;reason&quot;: &quot;IR 输入外部资源标识为 local status.txt。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;源要求将状态追加到本地 status.txt。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 12,
    &quot;data_count&quot;: 20,
    &quot;description_revision&quot;: 0,
    &quot;record_count&quot;: 18
  }
}</pre>

</details>

