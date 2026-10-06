# 基础数据传播记录

执行状态：`complete`。

IR 记录覆盖：12 / 12。

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

块：block_001；执行主体：agent_runtime, llm；角色：source。

IR 输入：0: request.json

IR 输出：0: result_001

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: request.json | 0: D008 |
| 2.1 | model_observe | deliver | 0: D008 | model_context: agent_model_context | — |

入口／出口变化：

- `result: result_001`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_001&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_001 绑定为读取到的 request.json 内容。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_001_request_contents&quot;
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
        &quot;reason&quot;: &quot;该指令由本地代理运行时执行文件读取。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content enters model processing&quot;,
        &quot;reason&quot;: &quot;读取的 request.json 用于自然语言处理，模型参与观察该内容。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;该操作从外部文件引入请求数据到当前流程。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_request_json&quot;,
        &quot;reason&quot;: &quot;指令读取 request.json 文件内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content enters model processing&quot;,
        &quot;reason&quot;: &quot;读取内容用于自然语言工作流，按执行模型进入模型处理上下文，位置在文件读取之后、字段选择之前。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;llm&quot;
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
          &quot;reason&quot;: &quot;该指令读取外部资源 request.json 的内容，因此读取位置为 request.json。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;location&quot;: &quot;L_request_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;ir_001_request_contents&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content enters model processing&quot;,
          &quot;reason&quot;: &quot;读取的 request.json 内容用于自然语言工作流处理，按固定执行模型送入模型上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM03&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;ir_001_request_contents&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;L_model_context&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
        &quot;reason&quot;: &quot;dispatch 是本地控制流跳转，由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令无输入输出内容，不充当 source、sink 或 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流跳转不属于本词汇表效果。&quot;,
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
| 1.1 | transform | select_part | 0: D008 | — | 0: D002 |

入口／出口变化：

- `result: result_002`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_002&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_002 绑定为选出的 term 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_003_term&quot;
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
        &quot;quote&quot;: &quot;extract_query_term&quot;,
        &quot;reason&quot;: &quot;本地运行时执行字段提取。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_query_term&quot;,
        &quot;reason&quot;: &quot;从容器中选择 term 字段，属于处理或转换内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;extract_query_term&quot;,
        &quot;reason&quot;: &quot;选择 term 字段改变内容表示或选择结果。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;extract_query_term&quot;,
          &quot;reason&quot;: &quot;从输入容器中选择 term 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;ir_003_term&quot;,
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
| 1.1 | transform | select_part | 0: D008 | — | 0: D001 |
| 1.2 | transform | compute | 0: D008 | — | 0: D007 |

入口／出口变化：

- `result: result_003`：未绑定 → D001
- `result: result_004`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_003&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_003 绑定为选出的 from_date 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_004_from_date_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_004&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_004 绑定为 from_date 是否存在的结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_004_from_date_present&quot;
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
        &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
        &quot;reason&quot;: &quot;本地运行时执行可选字段提取。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
        &quot;reason&quot;: &quot;选择可选 from_date 并计算存在性，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
        &quot;reason&quot;: &quot;选择可选字段并计算存在性，改变内容表示。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;extract_optional_from_date&quot;,
          &quot;reason&quot;: &quot;从输入容器中选择可选 from_date 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;ir_004_from_date_value&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;whether request.from_date is present&quot;,
          &quot;reason&quot;: &quot;计算 from_date 是否存在，作为可选参数控制结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;ir_004_from_date_present&quot;
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
| 1.1 | transform | select_part | 0: D008 | — | 0: D004 |
| 1.2 | transform | compute | 0: D008 | — | 0: D009 |

入口／出口变化：

- `result: result_005`：未绑定 → D004
- `result: result_006`：未绑定 → D009

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_005&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_005 绑定为选出的 limit 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_005_limit_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_006&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_006 绑定为 limit 是否存在的结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_005_limit_present&quot;
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
        &quot;quote&quot;: &quot;extract_optional_limit&quot;,
        &quot;reason&quot;: &quot;本地运行时执行可选字段提取。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_optional_limit&quot;,
        &quot;reason&quot;: &quot;选择可选 limit 并计算存在性，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;extract_optional_limit&quot;,
        &quot;reason&quot;: &quot;选择可选字段并计算存在性，改变内容表示。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;extract_optional_limit&quot;,
          &quot;reason&quot;: &quot;从输入容器中选择可选 limit 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;ir_005_limit_value&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;whether request.limit is present&quot;,
          &quot;reason&quot;: &quot;计算 limit 是否存在，作为可选参数控制结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;ir_005_limit_present&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
        &quot;reason&quot;: &quot;dispatch 是本地控制流跳转，由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令无输入输出内容，不充当 source、sink 或 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流跳转不属于本词汇表效果。&quot;,
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

块：block_003；执行主体：agent_runtime, tool, llm；角色：source, sink。

IR 输入：0: index.search, 1: result_002, 2: result_003, 3: result_004, 4: result_005, 5: result_006

IR 输出：0: result_007

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | receive | 0: D002; 1: D001; 2: D007; 3: D004; 4: D009 | tool: index.search | 0: D005 |
| 2.1 | model_observe | deliver | 0: D005 | model_context: agent_model_context | — |

入口／出口变化：

- `result: result_007`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_007&quot;,
          &quot;reason&quot;: &quot;该调用的输出 result_007 绑定为 index.search 响应。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_007_search_response&quot;
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
        &quot;reason&quot;: &quot;工作流要求执行该调用，代理运行时发起调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;该外部资源作为工具执行搜索。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容进入 LLM 上下文，模型参与观察。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search response&quot;,
        &quot;reason&quot;: &quot;该调用获取搜索响应，引入新内容到当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;查询参数被传到 index.search 工具边界，形成 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;搜索响应作为工具返回内容进入模型处理上下文，位置在工具接收之后。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
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
          &quot;quote&quot;: &quot;index.search response&quot;,
          &quot;reason&quot;: &quot;该调用获取 index.search 返回内容；网络传输未证实，因此按工具内容获取边界接收。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;if tool content is acquired but networking is unknown or explicitly local, use receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;网络未知时使用工具位置的 receive 保留获取边界。&quot;,
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
        },
        {
          &quot;index&quot;: 3,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 4,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 5,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;L_index_search&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;ir_007_search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;index.search 返回内容按工具返回假设进入 LLM 上下文。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;ir_007_search_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;L_model_context&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
        &quot;reason&quot;: &quot;dispatch 是本地控制流跳转，由代理运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;该指令无输入输出内容，不充当 source、sink 或 transformer。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制流跳转不属于本词汇表效果。&quot;,
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
| 1.1 | transform | select_part | 0: D005 | — | 0: D003 |

入口／出口变化：

- `result: result_008`：未绑定 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_008&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_008 绑定为选出的 total 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0029&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_009_total&quot;
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
        &quot;quote&quot;: &quot;extract_response_total&quot;,
        &quot;reason&quot;: &quot;本地运行时提取响应中的 total。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_response_total&quot;,
        &quot;reason&quot;: &quot;从搜索响应中选择 total 字段，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;extract_response_total&quot;,
        &quot;reason&quot;: &quot;选择 total 字段并改变内容表示。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;extract_response_total&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 total 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0029&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;ir_009_total&quot;,
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
| 1.1 | fs_write | write | 0: D003 | storage: count.txt | storage: count.txt: 未绑定 → D003 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D003

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
        &quot;reason&quot;: &quot;本地运行时执行文件写入。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;内容写入文件存储，形成 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;创建或修改 count.txt 文件内容。&quot;,
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
          &quot;reason&quot;: &quot;将 total 值写入 count.txt 文件；未说明追加，按替换或创建写入。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;write_count_file&quot;,
          &quot;reason&quot;: &quot;该指令为文件写入操作。&quot;,
          &quot;ref_id&quot;: &quot;g_0030&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;replace&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;L_count_txt&quot;
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
| 1.1 | transform | select_part | 0: D005 | — | 0: D006 |

入口／出口变化：

- `result: result_009`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;quote&quot;: &quot;result_009&quot;,
          &quot;reason&quot;: &quot;该指令的输出 result_009 绑定为选出的 items 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0031&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;ir_011_items&quot;
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
        &quot;quote&quot;: &quot;extract_response_items&quot;,
        &quot;reason&quot;: &quot;本地运行时提取响应中的 items。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;extract_response_items&quot;,
        &quot;reason&quot;: &quot;从搜索响应中选择 items 字段，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;extract_response_items&quot;,
        &quot;reason&quot;: &quot;选择 items 字段并改变内容表示。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;extract_response_items&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 items 字段。&quot;,
          &quot;ref_id&quot;: &quot;g_0031&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;ir_011_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_012 · return

块：block_004；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_009

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D006 | user: requesting_user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
      &quot;user_output&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;代理运行时执行最终返回。&quot;,
        &quot;ref_id&quot;: &quot;g_0032&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;将 items 提供给用户或调用方，形成输出边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;最终返回 items，结合用户提供请求的场景，视为向用户直接提供内容。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
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
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;将 items 值作为最终返回内容提供给用户侧。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;L_user&quot;
    }
  ]
}</pre>

</details>

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8 | opaque |
| D002 | data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370 | opaque |
| D003 | data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6 | opaque |
| D004 | data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad | opaque |
| D005 | data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2 | known_parts |
| D006 | data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624 | opaque |
| D007 | data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6 | opaque |
| D008 | data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06 | known_parts |
| D009 | data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4 | opaque |

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
  &quot;id&quot;: &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
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
  &quot;id&quot;: &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
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
  &quot;id&quot;: &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
  &quot;id&quot;: &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
    &quot;path&quot;: [
      &quot;limit&quot;
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
        &quot;data&quot;: &quot;data_383139e44922a61ac1d860e2f49d2ea0146d670c669c21a160c93fa71438dae6&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;,
      &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;,
      &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;,
      &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;,
      &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;
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
  &quot;id&quot;: &quot;data_6a55694bfa19ab7b626f0d0791847db427a94b4d5b33c0d9a8ea2b5ed704f624&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_44c78a9cc64e00a80b7ba3a4af6281614b1d504ad40927dc47a1c3b4ef3455f2&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
  &quot;id&quot;: &quot;data_cf6f1f78a067249a4a06ee6026e265cfdd8d97237042511c17837e25186259f6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_004&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_2bc1c452f407472fce27604521c027325bc9046e58494bb3244ac85e8f9a8370&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_10f2299d0e2783e7ff58e13dbc313c528935d03f4c92720e9caac89c7be12ab8&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_3a4c4fb4694021b634814b840f367c369c7b5e6fbb5d8093e5e81bd28bf690ad&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
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
  &quot;id&quot;: &quot;data_fa63a0e41237bb511b79f42fe3f30f32676c2886ecd15702ed180d3a245847d4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_f58214b8cc5b55257c0cc8d5a4423e70acf8258f79789afca639b3fce8623a06&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;L_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;该指令写入外部文件 count.txt。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;local count.txt&quot;,
        &quot;reason&quot;: &quot;工作流要求写入本地 count.txt。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;
      }
    ],
    &quot;L_index_search&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;该指令以 index.search 作为外部资源调用，作为工具获取边界；未证明为远程传输。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流要求调用 index.search。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;
      }
    ],
    &quot;L_model_context&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;content enters model processing&quot;,
        &quot;reason&quot;: &quot;自然语言处理获取的内容默认进入模型处理上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM03&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;
      }
    ],
    &quot;L_request_json&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;request.json&quot;,
        &quot;reason&quot;: &quot;该指令的输入外部资源标识为 request.json，表示文件存储位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;工作流读取用户提供的 request.json 文件。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      }
    ],
    &quot;L_user&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;user-supplied&quot;,
        &quot;reason&quot;: &quot;请求由用户提供，存在用户侧边界。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;最终返回 items 给调用方，作为用户输出边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;
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

