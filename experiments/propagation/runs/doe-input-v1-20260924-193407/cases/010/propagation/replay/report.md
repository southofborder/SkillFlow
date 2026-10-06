# 基础数据传播记录

执行状态：`complete`。

IR 记录覆盖：18 / 18。

[本地可视化审查](report.html) · [唯一业务结果](../doe-input.json)

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
          &quot;instruction_id&quot;: &quot;ir_001&quot;,
          &quot;reason&quot;: &quot;已确认 fs_read 与 transform；读取的 request.json 是否进入 LLM 上下文缺少直接证据，EM02 仅覆盖工具返回，故 model_observe 是否适用未决。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_003&quot;,
          &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_005&quot;,
          &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
        },
        {
          &quot;field&quot;: &quot;effects&quot;,
          &quot;instruction_id&quot;: &quot;ir_009&quot;,
          &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
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
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;reason&quot;: &quot;已确认 fs_read 与 transform；读取的 request.json 是否进入 LLM 上下文缺少直接证据，EM02 仅覆盖工具返回，故 model_observe 是否适用未决。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
  },
  {
    &quot;field&quot;: &quot;effects&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;reason&quot;: &quot;已确认 transform 与 model_observe；但 index.search 是否涉及远程 net_send 或 net_receive 无法仅凭工具名确定，EM06 要求单独评估通信证据，故网络效果未决。&quot;
  }
]</pre>

</details>

## ir_001 · read_request_json

块：block_001；执行主体：agent_runtime；角色：source, transformer。

IR 输入：0: request.json

IR 输出：0: result_001, 1: result_002, 2: result_003, 3: result_004, 4: result_005

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: request.json | 0: D014 |
| 2.1 | transform | select_part | 0: D014 | — | 0: D012 |
| 2.2 | transform | compute | 0: D014 | — | 0: D011 |
| 2.3 | transform | select_part | 0: D014 | — | 0: D009 |
| 2.4 | transform | compute | 0: D014 | — | 0: D005 |
| 2.5 | transform | select_part | 0: D014 | — | 0: D016 |

入口／出口变化：

- `result: result_001`：未绑定 → D012
- `result: result_002`：未绑定 → D011
- `result: result_003`：未绑定 → D009
- `result: result_004`：未绑定 → D005
- `result: result_005`：未绑定 → D016

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;reason&quot;: &quot;CFG 输出 result_001 对应 request.term，绑定到本地 request_term。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_term&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_002&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_002 对应 from_date present，绑定到本地 from_date_present。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_003&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_003 对应 request.from_date，绑定到本地 request_from_date。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_from_date&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_004&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_004 对应 limit present，绑定到本地 limit_present。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 3,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_005&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_005 对应 request.limit，绑定到本地 request_limit。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 4,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_limit&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;fs_read&quot;,
      &quot;transform&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;read_request_json&quot;,
        &quot;reason&quot;: &quot;该指令由本地运行时执行读取 request.json 的操作。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;读取用户提供的 request.json，将文件内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;which contains term and may contain from_date and limit&quot;,
        &quot;reason&quot;: &quot;从请求内容中取得 term、from_date、limit 及存在标志，属于字段选择与解析转换。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;该动作读取文件内容。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;result_001&quot;,
        &quot;reason&quot;: &quot;该指令输出多个请求字段和存在标志，存在本地解析与字段选择转换。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
          &quot;reason&quot;: &quot;源要求读取 request.json，因此读操作以该文件为位置。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_request_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;request_json_content&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;which contains term&quot;,
          &quot;reason&quot;: &quot;request.json 包含 term，选择该字段作为 request.term。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_json_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;request_term&quot;,
      &quot;path&quot;: [
        &quot;term&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
          &quot;reason&quot;: &quot;根据请求内容计算 from_date 是否存在，依赖可能来自请求内容。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_json_content&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;from_date_present&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
          &quot;reason&quot;: &quot;选择可选字段 from_date 作为 request.from_date。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_json_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;request_from_date&quot;,
      &quot;path&quot;: [
        &quot;from_date&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
          &quot;reason&quot;: &quot;根据请求内容计算 limit 是否存在，依赖可能来自请求内容。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_json_content&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;limit_present&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
          &quot;reason&quot;: &quot;选择可选字段 limit 作为 request.limit。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_json_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;request_limit&quot;,
      &quot;path&quot;: [
        &quot;limit&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_002 · dispatch

块：block_001；执行主体：agent_runtime；角色：[]。

IR 输入：0: result_002, 1: result_004

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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该控制分派由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅根据存在标志选择后续路径，不引入、接收、转换或输出内容，未识别 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派，未识别本词汇表中的适用效果，故 effects 为空。&quot;,
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

## ir_003 · index.search

块：block_002；执行主体：agent_runtime, tool, llm；角色：source, sink, transformer。

IR 输入：0: index.search, 1: result_001, 2: result_003, 3: result_005

IR 输出：0: result_006, 1: result_007

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D012; 1: D009; 2: D016 | — | 0: D017 |
| 1.2 | transform | select_part | 0: D017 | — | 0: D003 |
| 1.3 | transform | select_part | 0: D017 | — | 0: D010 |
| 2.1 | model_observe | deliver | 0: D017 | model_context: LLM context | — |

入口／出口变化：

- `result: result_006`：未绑定 → D003
- `result: result_007`：未绑定 → D010

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;quote&quot;: &quot;result_006&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_006 对应 search response total，绑定到本地 search_total。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_total&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_007&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_007 对应 search response items，绑定到本地 search_items。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_items&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流运行时发起对 index.search 的调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;具体工具 index.search 执行该搜索动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，因此模型参与返回内容处理。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;search response total&quot;,
        &quot;reason&quot;: &quot;工具返回搜索响应内容，将新内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;查询参数传递到 index.search 工具，使内容到达该工具边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;index.search 对查询参数执行检索计算并生成搜索响应。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;该调用以 term 及可选参数计算搜索响应，属于转换阶段。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;搜索响应作为工具返回内容默认进入 LLM 上下文。&quot;,
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
      &quot;sink&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;,
        &quot;derived&quot;,
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;以 term、from_date、limit 为输入计算搜索响应。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
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
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 total 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 items 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;index.search 工具返回内容按固定执行模型默认进入 LLM 上下文。&quot;,
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
      &quot;target&quot;: &quot;loc_model_context&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该控制分派由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅进行路径分派，不引入、接收、转换或输出内容，未识别 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派，未识别本词汇表中的适用效果，故 effects 为空。&quot;,
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

## ir_005 · index.search

块：block_003；执行主体：agent_runtime, tool, llm；角色：source, sink, transformer。

IR 输入：0: index.search, 1: result_001, 2: result_003

IR 输出：0: result_008, 1: result_009

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D012; 1: D009 | — | 0: D004 |
| 1.2 | transform | select_part | 0: D004 | — | 0: D018 |
| 1.3 | transform | select_part | 0: D004 | — | 0: D006 |
| 2.1 | model_observe | deliver | 0: D004 | model_context: LLM context | — |

入口／出口变化：

- `result: result_008`：未绑定 → D018
- `result: result_009`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;reason&quot;: &quot;CFG 输出 result_008 对应 search response total，绑定到本地 search_total。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_total&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_009&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_009 对应 search response items，绑定到本地 search_items。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_items&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流运行时发起对 index.search 的调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;具体工具 index.search 执行该搜索动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，因此模型参与返回内容处理。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;search response total&quot;,
        &quot;reason&quot;: &quot;工具返回搜索响应内容，将新内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged&quot;,
        &quot;reason&quot;: &quot;from_date 参数传递到 index.search 工具，使内容到达该工具边界。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;index.search 对查询参数执行检索计算并生成搜索响应。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;该调用以 term 与 from_date 计算搜索响应，属于转换阶段。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;搜索响应作为工具返回内容默认进入 LLM 上下文。&quot;,
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
      &quot;sink&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;,
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;以 term 与 from_date 为输入计算搜索响应。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
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
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 total 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 items 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;index.search 工具返回内容按固定执行模型默认进入 LLM 上下文。&quot;,
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
      &quot;target&quot;: &quot;loc_model_context&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该控制分派由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅进行路径分派，不引入、接收、转换或输出内容，未识别 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派，未识别本词汇表中的适用效果，故 effects 为空。&quot;,
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

## ir_007 · index.search

块：block_004；执行主体：agent_runtime, tool, llm；角色：source, sink, transformer。

IR 输入：0: index.search, 1: result_001, 2: result_005

IR 输出：0: result_010, 1: result_011

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D012; 1: D016 | — | 0: D002 |
| 1.2 | transform | select_part | 0: D002 | — | 0: D001 |
| 1.3 | transform | select_part | 0: D002 | — | 0: D008 |
| 2.1 | model_observe | deliver | 0: D002 | model_context: LLM context | — |

入口／出口变化：

- `result: result_010`：未绑定 → D001
- `result: result_011`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;quote&quot;: &quot;result_010&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_010 对应 search response total，绑定到本地 search_total。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_total&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_011&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_011 对应 search response items，绑定到本地 search_items。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_items&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流运行时发起对 index.search 的调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;具体工具 index.search 执行该搜索动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，因此模型参与返回内容处理。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;search response total&quot;,
        &quot;reason&quot;: &quot;工具返回搜索响应内容，将新内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;limit 参数传递到 index.search 工具，使内容到达该工具边界。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;index.search 对查询参数执行检索计算并生成搜索响应。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;该调用以 term 与 limit 计算搜索响应，属于转换阶段。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;搜索响应作为工具返回内容默认进入 LLM 上下文。&quot;,
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
      &quot;sink&quot;,
      &quot;transformer&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;,
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;以 term 与 limit 为输入计算搜索响应。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
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
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 total 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 items 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;index.search 工具返回内容按固定执行模型默认进入 LLM 上下文。&quot;,
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
      &quot;target&quot;: &quot;loc_model_context&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该控制分派由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅进行路径分派，不引入、接收、转换或输出内容，未识别 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派，未识别本词汇表中的适用效果，故 effects 为空。&quot;,
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

## ir_009 · index.search

块：block_005；执行主体：agent_runtime, tool, llm；角色：source, sink, transformer。

IR 输入：0: index.search, 1: result_001

IR 输出：0: result_012, 1: result_013

**效果存在未决；位置用于对应记录，不能当作已确认的完整执行顺序。**

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | 0: D012 | — | 0: D007 |
| 1.2 | transform | select_part | 0: D007 | — | 0: D013 |
| 1.3 | transform | select_part | 0: D007 | — | 0: D015 |
| 2.1 | model_observe | deliver | 0: D007 | model_context: LLM context | — |

入口／出口变化：

- `result: result_012`：未绑定 → D013
- `result: result_013`：未绑定 → D015

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;quote&quot;: &quot;result_012&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_012 对应 search response total，绑定到本地 search_total。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_total&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;result_013&quot;,
          &quot;reason&quot;: &quot;CFG 输出 result_013 对应 search response items，绑定到本地 search_items。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_items&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流运行时发起对 index.search 的调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;具体工具 index.search 执行该搜索动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认进入 LLM 上下文，因此模型参与返回内容处理。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;search response total&quot;,
        &quot;reason&quot;: &quot;工具返回搜索响应内容，将新内容引入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;term 参数传递到 index.search 工具，使内容到达该工具边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;index.search 对查询参数执行检索计算并生成搜索响应。&quot;,
        &quot;ref_id&quot;: &quot;g_0033&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;该调用以 term 计算搜索响应，属于转换阶段。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;搜索响应作为工具返回内容默认进入 LLM 上下文。&quot;,
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
      &quot;sink&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;以 term 为输入计算搜索响应。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 total 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
          &quot;reason&quot;: &quot;从搜索响应中选择 items 字段。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;search_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
          &quot;reason&quot;: &quot;index.search 工具返回内容按固定执行模型默认进入 LLM 上下文。&quot;,
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
      &quot;target&quot;: &quot;loc_model_context&quot;
    }
  ]
}</pre>

</details>

## ir_010 · dispatch

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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该控制分派由本地 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅进行路径分派，不引入、接收、转换或输出内容，未识别 source、sink 或 transformer 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分派，未识别本词汇表中的适用效果，故 effects 为空。&quot;,
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

## ir_011 · write_total_to_count_file

块：block_006；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_006

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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;quote&quot;: &quot;write_total_to_count_file&quot;,
        &quot;reason&quot;: &quot;该本地文件写入动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;total 值被写入 count.txt，内容到达存储位置边界。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;该动作创建或修改本地文件 count.txt 的内容。&quot;,
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
          &quot;reason&quot;: &quot;将搜索响应的 total 写入 count.txt，未说明追加，按替换或创建写入处理。&quot;,
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

## ir_012 · return

块：block_006；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_007

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D010 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该返回动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;items 值被提供给调用方或用户边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;工作流最终返回 items，向调用方或用户提供内容。&quot;,
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
          &quot;reason&quot;: &quot;将 items 值返回给调用方或用户边界。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_013 · write_total_to_count_file

块：block_007；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_008

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D018 | storage: count.txt | storage: count.txt: 未绑定 → D018 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D018

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;quote&quot;: &quot;write_total_to_count_file&quot;,
        &quot;reason&quot;: &quot;该本地文件写入动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0045&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;total 值被写入 count.txt，内容到达存储位置边界。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;该动作创建或修改本地文件 count.txt 的内容。&quot;,
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
          &quot;reason&quot;: &quot;将搜索响应的 total 写入 count.txt，未说明追加，按替换或创建写入处理。&quot;,
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

## ir_014 · return

块：block_007；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_009

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D006 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该返回动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;items 值被提供给调用方或用户边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;工作流最终返回 items，向调用方或用户提供内容。&quot;,
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
          &quot;reason&quot;: &quot;将 items 值返回给调用方或用户边界。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_015 · write_total_to_count_file

块：block_008；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_010

IR 输出：[]

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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;quote&quot;: &quot;write_total_to_count_file&quot;,
        &quot;reason&quot;: &quot;该本地文件写入动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;total 值被写入 count.txt，内容到达存储位置边界。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;该动作创建或修改本地文件 count.txt 的内容。&quot;,
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
          &quot;reason&quot;: &quot;将搜索响应的 total 写入 count.txt，未说明追加，按替换或创建写入处理。&quot;,
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

## ir_016 · return

块：block_008；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_011

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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该返回动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;items 值被提供给调用方或用户边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;工作流最终返回 items，向调用方或用户提供内容。&quot;,
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
          &quot;reason&quot;: &quot;将 items 值返回给调用方或用户边界。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## ir_017 · write_total_to_count_file

块：block_009；执行主体：agent_runtime；角色：sink。

IR 输入：0: count.txt, 1: result_012

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D013 | storage: count.txt | storage: count.txt: 未绑定 → D013 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D013

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;quote&quot;: &quot;write_total_to_count_file&quot;,
        &quot;reason&quot;: &quot;该本地文件写入动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0057&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;total 值被写入 count.txt，内容到达存储位置边界。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;该动作创建或修改本地文件 count.txt 的内容。&quot;,
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
          &quot;reason&quot;: &quot;将搜索响应的 total 写入 count.txt，未说明追加，按替换或创建写入处理。&quot;,
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

## ir_018 · return

块：block_009；执行主体：agent_runtime；角色：sink。

IR 输入：0: result_013

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | user_output | deliver | 0: D015 | user: user | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
          &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
        &quot;reason&quot;: &quot;该返回动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;items 值被提供给调用方或用户边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;工作流最终返回 items，向调用方或用户提供内容。&quot;,
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
          &quot;reason&quot;: &quot;将 items 值返回给调用方或用户边界。&quot;,
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
      &quot;target&quot;: &quot;loc_user&quot;
    }
  ]
}</pre>

</details>

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771 | opaque |
| D002 | data_24c9ed3679406222d320368fb6975c894175976cbf82818630572205dac6fc80 | known_parts |
| D003 | data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7 | opaque |
| D004 | data_3482304f01e661f48598f6274ec6ef83afb5a0daa0b31fa9d04cf3c46455f975 | known_parts |
| D005 | data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b | opaque |
| D006 | data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326 | opaque |
| D007 | data_520ebc7705c72f97c4e62bcb0afdbd5db8a44aab4a33a1f6436c4823682cd820 | known_parts |
| D008 | data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b | opaque |
| D009 | data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d | opaque |
| D010 | data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da | opaque |
| D011 | data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26 | opaque |
| D012 | data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21 | opaque |
| D013 | data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f | opaque |
| D014 | data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e | known_parts |
| D015 | data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766 | opaque |
| D016 | data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418 | opaque |
| D017 | data_d7f75409cfb212dd3daf3f33a08e49447b1ce05985d6e83423d7cb7c9390fa01 | known_parts |
| D018 | data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40 | opaque |

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
  &quot;id&quot;: &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_24c9ed3679406222d320368fb6975c894175976cbf82818630572205dac6fc80&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
        &quot;data&quot;: &quot;data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_24c9ed3679406222d320368fb6975c894175976cbf82818630572205dac6fc80&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
      &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
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
  &quot;id&quot;: &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_d7f75409cfb212dd3daf3f33a08e49447b1ce05985d6e83423d7cb7c9390fa01&quot;,
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_3482304f01e661f48598f6274ec6ef83afb5a0daa0b31fa9d04cf3c46455f975&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
      &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;
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
  &quot;id&quot;: &quot;data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_001&#x27;, 1, 3]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
  &quot;id&quot;: &quot;data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_3482304f01e661f48598f6274ec6ef83afb5a0daa0b31fa9d04cf3c46455f975&quot;,
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_520ebc7705c72f97c4e62bcb0afdbd5db8a44aab4a33a1f6436c4823682cd820&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;
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
  &quot;id&quot;: &quot;data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_24c9ed3679406222d320368fb6975c894175976cbf82818630572205dac6fc80&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
  &quot;id&quot;: &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
    &quot;path&quot;: [
      &quot;from_date&quot;
    ]
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
  &quot;id&quot;: &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_d7f75409cfb212dd3daf3f33a08e49447b1ce05985d6e83423d7cb7c9390fa01&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
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
  &quot;id&quot;: &quot;data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_001&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;
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
  &quot;id&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
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
  &quot;id&quot;: &quot;data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_520ebc7705c72f97c4e62bcb0afdbd5db8a44aab4a33a1f6436c4823682cd820&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
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
  &quot;id&quot;: &quot;data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_520ebc7705c72f97c4e62bcb0afdbd5db8a44aab4a33a1f6436c4823682cd820&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
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
  &quot;id&quot;: &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e&quot;,
    &quot;path&quot;: [
      &quot;limit&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_d7f75409cfb212dd3daf3f33a08e49447b1ce05985d6e83423d7cb7c9390fa01&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_003&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21&quot;,
      &quot;data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d&quot;,
      &quot;data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418&quot;
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
  &quot;id&quot;: &quot;data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_3482304f01e661f48598f6274ec6ef83afb5a0daa0b31fa9d04cf3c46455f975&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
  }
}</pre>

</details>


<details><summary>独立审计材料：位置依据与求解统计</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;loc_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt&quot;,
        &quot;reason&quot;: &quot;源明确写入本地 count.txt，标识该文件存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;CFG 写入指令的 external_resource 标识符为 count.txt。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;
      }
    ],
    &quot;loc_model_context&quot;: [
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;content returned by an agent tool enters the LLM context by default&quot;,
        &quot;reason&quot;: &quot;固定执行模型规定工具返回内容默认进入 LLM 上下文，作为模型上下文边界。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;search response total&quot;,
        &quot;reason&quot;: &quot;index.search 指令输出搜索响应内容，是进入模型上下文的证据之一。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      }
    ],
    &quot;loc_request_json&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;源明确读取用户提供的 request.json，标识该文件存储边界。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;request.json&quot;,
        &quot;reason&quot;: &quot;CFG 中该指令的输入 external_resource 标识符为 request.json。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      }
    ],
    &quot;loc_user&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;工作流最终返回 items，标识调用方或用户输出边界。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;CFG 中 return 指令将内容提供给外部调用边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 15,
    &quot;data_count&quot;: 18,
    &quot;description_revision&quot;: 11,
    &quot;record_count&quot;: 18
  }
}</pre>

</details>

