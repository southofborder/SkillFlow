# 基础数据传播记录

执行状态：`complete`。

IR 记录覆盖：13 / 13。

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
      &quot;content&quot;: &quot;# 离线传播示例\n\n所有动作与传播说明均由示例作者提供。此文不是模型实测。\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;87d2b9f1448113cfe46f4cdeebe91d79c13cb5fa77c185de9758433e4b647165&quot;
    }
  ],
  &quot;index&quot;: [
    {
      &quot;end_line&quot;: 1,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_001&quot;,
      &quot;start_line&quot;: 1
    },
    {
      &quot;end_line&quot;: 3,
      &quot;file&quot;: &quot;SKILL.md&quot;,
      &quot;id&quot;: &quot;src_002&quot;,
      &quot;start_line&quot;: 3
    }
  ],
  &quot;inventory&quot;: [
    {
      &quot;decoded_sha256&quot;: &quot;87d2b9f1448113cfe46f4cdeebe91d79c13cb5fa77c185de9758433e4b647165&quot;,
      &quot;kind&quot;: &quot;markdown&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;raw_sha256&quot;: &quot;87d2b9f1448113cfe46f4cdeebe91d79c13cb5fa77c185de9758433e4b647165&quot;,
      &quot;size&quot;: 104
    }
  ],
  &quot;source_sha256&quot;: &quot;07a5c00db58fe54e25e970f300a2913cbdd22a33ec0aa84a2651a79159308261&quot;
}</pre>

</details>

<details><summary>覆盖与诊断</summary>

<pre>{
  &quot;coverage&quot;: {
    &quot;ir_append&quot;: &quot;processed&quot;,
    &quot;ir_build&quot;: &quot;processed&quot;,
    &quot;ir_copy&quot;: &quot;processed&quot;,
    &quot;ir_delete&quot;: &quot;processed&quot;,
    &quot;ir_local_filter&quot;: &quot;processed&quot;,
    &quot;ir_model_filter&quot;: &quot;processed&quot;,
    &quot;ir_network&quot;: &quot;processed&quot;,
    &quot;ir_opaque&quot;: &quot;processed&quot;,
    &quot;ir_read&quot;: &quot;processed&quot;,
    &quot;ir_return&quot;: &quot;processed&quot;,
    &quot;ir_save&quot;: &quot;processed&quot;,
    &quot;ir_source_end&quot;: &quot;processed&quot;,
    &quot;ir_update&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_read · read

块：source；执行主体：agent_runtime；角色：source。

IR 输入：0: document

IR 输出：0: B

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: document | 0: D012 |

入口／出口变化：

- `result: B`：未绑定 → D012

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;read&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0007&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;b&quot;
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
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时从 document 上下文取得原始整体 B，承担数据引入角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时从 document 上下文取得原始整体 B，承担数据引入角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。从 document 取得完整候选 B；尚未选取或删除字段。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;,
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
          &quot;quote&quot;: &quot;read&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0007&quot;
        }
      ],
      &quot;location&quot;: &quot;document&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;b&quot;
    }
  ]
}</pre>

</details>

## ir_source_end · dispatch

块：source；执行主体：agent_runtime；角色：[]。

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
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时执行控制转移；没有在此动作中引入、交付或变换数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时执行控制转移；没有在此动作中引入、交付或变换数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0008&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时执行控制转移；没有在此动作中引入、交付或变换数据。&quot;,
        &quot;ref_id&quot;: &quot;g_0008&quot;,
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

## ir_model_filter · model_filter

块：main；执行主体：llm；角色：sink, transformer。

IR 输入：0: B

IR 输出：0: model_clean

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe | deliver | 0: D012 | model_context: assistant | — |
| 2.1 | transform | exclude_parts | 0: D012 | — | 0: D008 |
| 3.1 | model_observe | deliver | 0: D008 | model_context: assistant | — |

入口／出口变化：

- `result: model_clean`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;model_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;clean&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [
      &quot;model_observe&quot;,
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定由模型先读取原始 B，再删除 api_key，并观察清理结果；模型既接收内容也参与变换。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定由模型先读取原始 B，再删除 api_key，并观察清理结果；模型既接收内容也参与变换。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定由模型先读取原始 B，再删除 api_key，并观察清理结果；模型既接收内容也参与变换。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。模型首先观察原始 B，此时 api_key 尚未删除。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。模型在观察 B 之后删除 api_key，产生不同数据版本 clean。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;model_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。模型随后观察 clean；这次观察不会撤销先前对 B 的观察。&quot;,
        &quot;ref_id&quot;: &quot;g_0011&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;llm&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;model_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;model&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;model_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;exclude_parts&quot;,
      &quot;output&quot;: &quot;clean&quot;,
      &quot;paths&quot;: [
        [
          &quot;api_key&quot;
        ]
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;model_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0011&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;clean&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;model&quot;
    }
  ]
}</pre>

</details>

## ir_local_filter · local_filter

块：main；执行主体：agent_runtime, llm；角色：transformer, sink。

IR 输入：0: B

IR 输出：0: local_clean

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | exclude_parts | 0: D012 | — | 0: D002 |
| 2.1 | model_observe | deliver | 0: D002 | model_context: assistant | — |

入口／出口变化：

- `result: local_clean`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;local_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0012&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;clean&quot;
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
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。本示范规定运行时先在本地删除 api_key，再将清理结果交给模型；执行主体列表自身不表达时序。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时首先在本地删除 B.api_key，产生 clean。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;local_filter&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。仅将本地清理后的 clean 提供给模型，不把原始 B 作为本次观察输入。&quot;,
        &quot;ref_id&quot;: &quot;g_0012&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;llm&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;local_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0012&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;exclude_parts&quot;,
      &quot;output&quot;: &quot;clean&quot;,
      &quot;paths&quot;: [
        [
          &quot;api_key&quot;
        ]
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;local_filter&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0012&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;clean&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;model&quot;
    }
  ]
}</pre>

</details>

## ir_update · update

块：main；执行主体：agent_runtime；角色：transformer。

IR 输入：0: B

IR 输出：0: updated

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | update_fields | 0: D012; 1: D011 | — | 0: D004 |

入口／出口变化：

- `result: updated`：未绑定 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;update&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0013&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;changed&quot;
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
        &quot;quote&quot;: &quot;update&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时以明确字面值覆盖 api_key 字段，其余原整体内容保留；未声明模型参与处理。&quot;,
        &quot;ref_id&quot;: &quot;g_0013&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;update&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时以明确字面值覆盖 api_key 字段，其余原整体内容保留；未声明模型参与处理。&quot;,
        &quot;ref_id&quot;: &quot;g_0013&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;update&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。将 B.api_key 覆盖为 [redacted]，产生字段覆盖结果。&quot;,
        &quot;ref_id&quot;: &quot;g_0013&quot;,
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
          &quot;quote&quot;: &quot;update&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;update_fields&quot;,
      &quot;output&quot;: &quot;changed&quot;,
      &quot;updates&quot;: [
        {
          &quot;path&quot;: [
            &quot;api_key&quot;
          ],
          &quot;value&quot;: {
            &quot;kind&quot;: &quot;literal&quot;,
            &quot;value&quot;: &quot;[redacted]&quot;
          }
        }
      ]
    }
  ]
}</pre>

</details>

## ir_build · build

块：main；执行主体：agent_runtime；角色：transformer。

IR 输入：0: updated, 1: local_clean

IR 输出：0: combined

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | build | 0: D004; 1: D002 | — | 0: D005 |

入口／出口变化：

- `result: combined`：未绑定 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;build&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0014&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;built&quot;
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
        &quot;quote&quot;: &quot;build&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时将 updated 和 local_clean 组成一个新对象，不引入新的外部来源。&quot;,
        &quot;ref_id&quot;: &quot;g_0014&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;build&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时将 updated 和 local_clean 组成一个新对象，不引入新的外部来源。&quot;,
        &quot;ref_id&quot;: &quot;g_0014&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;build&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。以 updated 和 local_clean 为两个组成部分构造新对象。&quot;,
        &quot;ref_id&quot;: &quot;g_0014&quot;,
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
      &quot;container&quot;: &quot;object&quot;,
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;build&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0014&quot;
        }
      ],
      &quot;op&quot;: &quot;build&quot;,
      &quot;output&quot;: &quot;built&quot;,
      &quot;parts&quot;: [
        {
          &quot;path&quot;: [
            &quot;updated&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        {
          &quot;path&quot;: [
            &quot;clean&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      ]
    }
  ]
}</pre>

</details>

## ir_opaque · opaque

块：main；执行主体：agent_runtime；角色：[]。

IR 输入：0: combined

IR 输出：0: computed

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签计算 | compute | 0: D005 | — | 0: D007 |

入口／出口变化：

- `result: computed`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;opaque&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;unknown&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;opaque&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记未解释的结果关系；仅有可能依赖不能证明另有数据引入、边界交付或实际变换动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;opaque&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记未解释的结果关系；仅有可能依赖不能证明另有数据引入、边界交付或实际变换动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;opaque&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记未解释的结果关系；仅有可能依赖不能证明另有数据引入、边界交付或实际变换动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: null
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;roles&quot;: []
  },
  &quot;steps&quot;: [
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;opaque&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;unknown&quot;
    }
  ]
}</pre>

</details>

## ir_copy · copy

块：main；执行主体：agent_runtime；角色：[]。

IR 输入：0: computed

IR 输出：0: alias

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | — | 仍保留入口、出口与结果绑定 |

入口／出口变化：

- `result: alias`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;copy&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0016&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      }
    }
  ],
  &quot;profile&quot;: {
    &quot;effects&quot;: [],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;copy&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记已有值的结果别名，不生成新数据，也没有额外的引入、边界交付或变换。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;copy&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记已有值的结果别名，不生成新数据，也没有额外的引入、边界交付或变换。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;copy&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时登记已有值的结果别名，不生成新数据，也没有额外的引入、边界交付或变换。&quot;,
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

## ir_save · save

块：main；执行主体：agent_runtime；角色：sink。

IR 输入：0: alias

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | 0: D007 | runtime_context: cache | runtime_context: cache: 未绑定 → D007 (strong) |

入口／出口变化：

- `runtime_context: cache`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
      &quot;context_write&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;save&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时将已有数据原样写入 cache 上下文边界，保存本身不改变内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;save&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时将已有数据原样写入 cache 上下文边界，保存本身不改变内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;save&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。将 alias 原样写入运行时 cache，供后续状态读取。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;context_write&quot;
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;save&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0017&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;replace&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;cache&quot;
    }
  ]
}</pre>

</details>

## ir_append · append

块：main；执行主体：agent_runtime；角色：sink。

IR 输入：0: local_clean

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D002 | storage: journal | storage: journal: D006 → D009 (strong) |

入口／出口变化：

- `storage: journal`：D006 → D009

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
        &quot;quote&quot;: &quot;append&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时把清理结果追加到 journal 文件边界；追加状态由传递规格记录。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时把清理结果追加到 journal 文件边界；追加状态由传递规格记录。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;append&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。向 journal 追加 local_clean；旧文件内容和追加参数均保留派生关系。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
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
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;append&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0018&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;journal&quot;
    }
  ]
}</pre>

</details>

## ir_delete · delete

块：main；执行主体：agent_runtime；角色：[]。

IR 输入：[]

IR 输出：[]

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | — | runtime_context: cache | runtime_context: cache: D007 → 未绑定 (delete) |

入口／出口变化：

- `runtime_context: cache`：D007 → 未绑定

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
      &quot;context_write&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;delete&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时只删除 cache 绑定，不读取或交付原内容；不能因发生状态修改就补贴内容变换角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0019&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;delete&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时只删除 cache 绑定，不读取或交付原内容；不能因发生状态修改就补贴内容变换角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0019&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;delete&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。只移除运行时 cache 绑定，不以原内容作为读取或观察输入。&quot;,
        &quot;ref_id&quot;: &quot;g_0019&quot;,
        &quot;value&quot;: &quot;context_write&quot;
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
          &quot;quote&quot;: &quot;delete&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0019&quot;
        }
      ],
      &quot;input&quot;: null,
      &quot;mode&quot;: &quot;delete&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;cache&quot;
    }
  ]
}</pre>

</details>

## ir_network · network

块：main；执行主体：agent_runtime, tool, llm；角色：sink, source。

IR 输入：0: local_clean

IR 输出：0: response

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | 0: D002 | remote: example-service | — |
| 2.1 | net_receive | receive | 0: D002 | remote: example-service | 0: D001 |
| 3.1 | model_observe | deliver | 0: D001 | model_context: assistant | — |

入口／出口变化：

- `result: response`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;response&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
          &quot;quote&quot;: &quot;network&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0020&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response&quot;
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
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;llm&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时调用网络工具发送清理请求并取得外部响应，随后模型读取响应；该动作同时涉及交付与引入。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。网络工具先把 local_clean 请求发送至 example-service。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;net_send&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。网络工具随后取得 response；请求的可能依赖不等于响应含请求明文。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;net_receive&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;network&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。工具响应回传后进入模型上下文，模型此时观察 response。&quot;,
        &quot;ref_id&quot;: &quot;g_0020&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;,
      &quot;llm&quot;
    ],
    &quot;roles&quot;: [
      &quot;sink&quot;,
      &quot;source&quot;
    ]
  },
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;network&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0020&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;service&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;network&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0020&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;service&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;network&quot;,
          &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
          &quot;ref_id&quot;: &quot;g_0020&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;model&quot;
    }
  ]
}</pre>

</details>

## ir_return · return

块：main；执行主体：agent_runtime；角色：[]。

IR 输入：0: response

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
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;response&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;B&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;alias&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;combined&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;computed&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;local_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;model_clean&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;response&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;updated&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;document&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;journal&quot;
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
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时结束流程并返回已有 response；未声明直接向用户展示，不补造用户输出。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时结束流程并返回已有 response；未声明直接向用户展示，不补造用户输出。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return&quot;,
        &quot;reason&quot;: &quot;人工编写的综合示例规格，并非模型标注或语义证明。运行时结束流程并返回已有 response；未声明直接向用户展示，不补造用户输出。&quot;,
        &quot;ref_id&quot;: &quot;g_0021&quot;,
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
| D001 | data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581 | opaque |
| D002 | data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd | whole_except |
| D003 | data_29534fa30e39c594466448f724032afb36d740efc22cb2a7c804c1a60677b139 | opaque |
| D004 | data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d | field_updates |
| D005 | data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443 | known_parts |
| D006 | data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381 | literal |
| D007 | data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd | opaque |
| D008 | data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2 | whole_except |
| D009 | data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137 | opaque |
| D010 | data_61c28fc40a4f85bef586fba58f779b1276f13ef01df9366b219bcaec68e56e02 | opaque |
| D011 | data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382 | literal |
| D012 | data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d | known_parts |

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
  &quot;id&quot;: &quot;data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;remote:example-service&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_network&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
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
    &quot;base&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
    &quot;excluded_parts&quot;: [
      [
        &quot;api_key&quot;
      ]
    ],
    &quot;form&quot;: &quot;whole_except&quot;
  },
  &quot;id&quot;: &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_local_filter&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
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
  &quot;id&quot;: &quot;data_29534fa30e39c594466448f724032afb36d740efc22cb2a7c804c1a60677b139&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
    &quot;path&quot;: [
      &quot;owner&quot;
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
    &quot;base&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
    &quot;form&quot;: &quot;field_updates&quot;,
    &quot;updates&quot;: [
      {
        &quot;data&quot;: &quot;data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382&quot;,
        &quot;path&quot;: [
          &quot;api_key&quot;
        ]
      }
    ]
  },
  &quot;id&quot;: &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_update&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
      &quot;data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;,
        &quot;path&quot;: [
          &quot;updated&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;,
        &quot;path&quot;: [
          &quot;clean&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_build&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d&quot;,
      &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
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
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: []
  },
  &quot;id&quot;: &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:journal&quot;,
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
  &quot;id&quot;: &quot;data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_opaque&#x27;, 0, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443&quot;
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
    &quot;base&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
    &quot;excluded_parts&quot;: [
      [
        &quot;api_key&quot;
      ]
    ],
    &quot;form&quot;: &quot;whole_except&quot;
  },
  &quot;id&quot;: &quot;data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_model_filter&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;
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
  &quot;id&quot;: &quot;data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_append&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;journal&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381&quot;,
      &quot;data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd&quot;
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
  &quot;id&quot;: &quot;data_61c28fc40a4f85bef586fba58f779b1276f13ef01df9366b219bcaec68e56e02&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
    &quot;path&quot;: [
      &quot;api_key&quot;
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
    &quot;form&quot;: &quot;literal&quot;,
    &quot;value&quot;: &quot;[redacted]&quot;
  },
  &quot;id&quot;: &quot;data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_update&#x27;, 0, 0], &#x27;input&#x27;, 1]&quot;,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_61c28fc40a4f85bef586fba58f779b1276f13ef01df9366b219bcaec68e56e02&quot;,
        &quot;path&quot;: [
          &quot;api_key&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_29534fa30e39c594466448f724032afb36d740efc22cb2a7c804c1a60677b139&quot;,
        &quot;path&quot;: [
          &quot;owner&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:document&quot;,
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
    &quot;cache&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;
      }
    ],
    &quot;document&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;
      }
    ],
    &quot;journal&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;
      }
    ],
    &quot;model&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;
      }
    ],
    &quot;service&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;read&quot;,
        &quot;reason&quot;: &quot;离线示例显式指定此关系；真实定位校验不等于语义正确性证明。&quot;,
        &quot;ref_id&quot;: &quot;g_0007&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 2,
    &quot;data_count&quot;: 12,
    &quot;description_revision&quot;: 0,
    &quot;record_count&quot;: 13
  }
}</pre>

</details>

