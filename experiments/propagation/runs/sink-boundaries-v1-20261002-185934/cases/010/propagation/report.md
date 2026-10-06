# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v4`；SHA-256：`1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66`。

求解状态：`complete`。

IR 记录覆盖：12 / 12。

[本地可视化审查](report.html) · [唯一业务结果](doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](audit/material.json)（execution_model）；逐项依据在下方审计区展开。

## 接收与保存边界

纳入清单 10 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。

等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。

| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |
|---|---|---|---|---|---|
| ir_001 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D009 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_003 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D009 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_004 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D009 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D009 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D005; 1: D006; 2: D007; 3: D010 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 2.2 | 纳入 | external_tool / 2 | loc_index_search · tool: index.search · recipient / 未建模期限 | 0: D001; 1: D003 | 另一接收主体或跨主体共享；source/src_008, cfg/g_0023, execution_model/EM12 |
| ir_007 / 3.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_009 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_010 / 1.1 | 纳入 | storage_write / 1 | loc_count_txt · storage: count.txt · task / persistent | 0: D008 | 任务内部、跨任务留存；source/src_013, cfg/g_0030, execution_model/EM12 |
| ir_011 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |

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
| 1.1 | fs_read | read | — | storage: request.json | 0: D009 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D009 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D009

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定读取得到的 request.json 内容。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_json_contents&quot;
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
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;源文指示工作流读取 request.json，该动作由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;读取操作将 request.json 内容引入当前流程，作为数据源。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read_request_json&quot;,
        &quot;reason&quot;: &quot;CFG 操作码表明读取外部文件内容，对应 fs_read。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 EM10 默认模式处理，读取输出按契约可能被模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
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
          &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
          &quot;reason&quot;: &quot;读取整个 request.json 内容；源文未提供 key-only 读取接口，按 EM01 保留整体读取。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_request_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;request_json_contents&quot;
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
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 EM10 默认模式处理，读取输出按契约可能被模型观察。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_json_contents&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D009 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D009 | — | 0: D001 |

入口／出口变化：

- `result: result_002`：未绑定 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定选出的 term 字段值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;提取 query term 是工作流中由 agent runtime 执行的步骤。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;which contains term&quot;,
        &quot;reason&quot;: &quot;从请求容器中选出 term 字段，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文只规定字段选择关系，未声明模型处理或本地隔离，按 default 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;字段选择/提取是 transform 效果，且保持原值。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文只规定字段选择关系，未声明模型处理或本地隔离，按 default 模式。&quot;,
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
          &quot;quote&quot;: &quot;using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;明确选出已有 term 字段并保持原值，符合 select_part。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D009 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D009 | — | 0: D005 |
| 2.2 | transform | compute | 0: D009 | — | 0: D006 |

入口／出口变化：

- `result: result_003`：未绑定 → D005
- `result: result_004`：未绑定 → D006

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定 from_date 值。&quot;,
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
          &quot;reason&quot;: &quot;公开输出绑定存在性标志。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;reason&quot;: &quot;提取可选 from_date 参数由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
        &quot;reason&quot;: &quot;从请求中提取可选字段并判断存在性，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged;&quot;,
        &quot;reason&quot;: &quot;字段提取及存在性判断是 transform 效果。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
          &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged;&quot;,
          &quot;reason&quot;: &quot;明确选出已有 from_date 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
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
          &quot;reason&quot;: &quot;存在性标志由请求容器是否含 from_date 推导；使用 compute 表示该判断。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D009 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D009 | — | 0: D007 |
| 2.2 | transform | compute | 0: D009 | — | 0: D010 |

入口／出口变化：

- `result: result_005`：未绑定 → D007
- `result: result_006`：未绑定 → D010

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定 limit 值。&quot;,
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
          &quot;reason&quot;: &quot;公开输出绑定存在性标志。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;提取可选 limit 参数由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
        &quot;reason&quot;: &quot;从请求中提取可选字段并判断存在性，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;字段提取及存在性判断是 transform 效果。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
          &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
          &quot;reason&quot;: &quot;明确选出已有 limit 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
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
          &quot;quote&quot;: &quot;When limit is present&quot;,
          &quot;reason&quot;: &quot;存在性标志由请求容器是否含 limit 推导；使用 compute 表示该判断。&quot;,
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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

块：block_003；执行主体：agent_runtime, tool；角色：source, sink, transformer。

IR 输入：0: index.search, 1: result_002, 2: result_003, 3: result_004, 4: result_005, 5: result_006

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
        &quot;op_index&quot;: 2
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D005; 1: D006; 2: D007; 3: D010 | model_context: 当前模型处理上下文 | — |
| 2.1 | 无标签数据操作 | compute | 0: D005; 1: D006; 2: D007; 3: D010 | — | 0: D003 |
| 2.2 | 无标签数据操作 | deliver | 0: D001; 1: D003 | tool: index.search | — |
| 2.3 | 无标签数据操作 | receive | 0: D001; 1: D005; 2: D006; 3: D007; 4: D010 | tool: index.search | 0: D002 |
| 3.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_007`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定工具获取的搜索响应。&quot;,
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
      &quot;model_observe&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;工作流指令由 agent runtime 发起对工具的调用。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;CFG 操作码表明工具 index.search 执行搜索动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value&quot;,
        &quot;reason&quot;: &quot;工具返回搜索响应，将内容引入当前流程，作为 source。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;请求参数被交付到 index.search 工具边界，作为 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search supports fuzzy matching&quot;,
        &quot;reason&quot;: &quot;该能力说明 index.search 对查询进行匹配处理，作为 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_006&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
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
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        }
      ],
      &quot;inputs&quot;: [
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
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;,
        &quot;possible&quot;,
        &quot;possible&quot;,
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
          &quot;reason&quot;: &quot;可选参数按存在性条件传入；用 compute 保守组合，所有依赖均为 possible，不声称精确原值传递。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        }
      ],
      &quot;inputs&quot;: [
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
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;optional_search_args&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;将 query term 原值和条件组合的可选参数交付到 index.search 工具边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;optional_search_args&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_index_search&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
          &quot;reason&quot;: &quot;从 index.search 工具边界获取搜索响应，并记录实际请求值依赖。&quot;,
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
      &quot;location&quot;: &quot;loc_index_search&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;search_response&quot;
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
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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
| 2.1 | transform | select_part | 0: D002 | — | 0: D008 |

入口／出口变化：

- `result: result_008`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定选出的 total 值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value&quot;,
        &quot;reason&quot;: &quot;提取响应 total 由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
        &quot;reason&quot;: &quot;从响应中选出 total 字段，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
        &quot;reason&quot;: &quot;字段选择是 transform 效果。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
          &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
          &quot;reason&quot;: &quot;明确选出响应中的 total 字段并保持原值。&quot;,
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

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D008 | storage: count.txt | storage: count.txt: 未绑定 → D008 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;工作流指令由 agent runtime 执行写文件。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;将内容写入本地文件存储，作为 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;创建或修改文件内容，对应 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
          &quot;reason&quot;: &quot;将 total 值写入 count.txt；未说明追加，按普通写入替换处理。&quot;,
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
| 2.1 | transform | select_part | 0: D002 | — | 0: D004 |

入口／出口变化：

- `result: result_009`：未绑定 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;reason&quot;: &quot;公开输出绑定选出的 items 值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;提取响应 items 由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;从响应中选出 items 字段，属于处理内容。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
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
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
        &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;字段选择是 transform 效果。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
          &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
          &quot;reason&quot;: &quot;明确选出响应中的 items 字段并保持原值。&quot;,
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;普通返回由 agent runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;普通返回不引入新源、不写入存储、不执行变换，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;普通返回不是用户输出或网络发送，且没有适用的效果词汇；按 REP02 事件和绑定可为空。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
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
| D001 | data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f | opaque |
| D002 | data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed | known_parts |
| D003 | data_406509840d11b3b634632e2692c06e2b374dca295f1ca0196b7a0fff3fcaee5b | opaque |
| D004 | data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87 | opaque |
| D005 | data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940 | opaque |
| D006 | data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12 | opaque |
| D007 | data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968 | opaque |
| D008 | data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676 | opaque |
| D009 | data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f | known_parts |
| D010 | data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425 | opaque |

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
  &quot;id&quot;: &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
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
        &quot;data&quot;: &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 2]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;,
      &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
      &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;,
      &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
      &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
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
  &quot;id&quot;: &quot;data_406509840d11b3b634632e2692c06e2b374dca295f1ca0196b7a0fff3fcaee5b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
      &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;,
      &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
      &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;
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
  &quot;id&quot;: &quot;data_44ea2041db49126ba9e1749bc3c7f2a271c686c9d7e3fafdbdb65dc6c28c1c87&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
  &quot;id&quot;: &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
    &quot;path&quot;: [
      &quot;from_date&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_52adb8c949ee26744bdcb8c2b03860cd5edbc00cbce915e515aa74ae7b1e5e12&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_004&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
  &quot;id&quot;: &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
    &quot;path&quot;: [
      &quot;limit&quot;
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
  &quot;id&quot;: &quot;data_e225a9bfe0dd90f6064f81f84e0107642ab4949b8ad734b49525fe2422fe8676&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_2ac73168c3c33c5688ed325921049de4b956fdf6faaa105ecfc57385387662ed&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_20f875e27003617f160e472f78c67f9453e1a4f3b0990c5faed994700b2ccd2f&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_4a37f3fa2ceb2ea963089f5c4923113e02c3b31b885f4b1691cb4af8d6232940&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_d8efa3e3de6b172c9a64ad6e677d67b417db9b4ad309635f91fc561a5f16b968&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
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
  &quot;id&quot;: &quot;data_e48537e769e7f39ef93772c3969149842143b82a23c81d8b6b676e6c1c1d4425&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_e41628913b11a2a50bcde52c67e54ee42fec0a1ae17d52193f060dbb3a2de71f&quot;
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
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
    &quot;loc_count_txt&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;源文标识本地 count.txt 文件为写入目标。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;CFG 外部资源标识符确认存储位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention;&quot;,
        &quot;reason&quot;: &quot;按 EM12 默认属性声明 task 访问和 persistent 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_index_search&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;源文定义 index.search 工具调用边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;CFG 外部资源标识符确认工具边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
        &quot;reason&quot;: &quot;未说明本地部署，按 EM12 保守声明 recipient 访问、retention 为 null，且不声称网络通信。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_request_json&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;reason&quot;: &quot;源文标识 request.json 为用户提供的本地文件；按 EM12 文件默认属性声明访问范围和保留。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;request.json&quot;,
        &quot;reason&quot;: &quot;CFG 外部资源标识符确认该存储位置。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention;&quot;,
        &quot;reason&quot;: &quot;按 EM12 默认属性声明 task 访问和 persistent 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 10,
    &quot;data_count&quot;: 10,
    &quot;description_revision&quot;: 5,
    &quot;record_count&quot;: 12
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;473100570ed68856bd1fdc2d9de059b8dba374cfc488786dc5c72b6b2fb29e8d&quot;,
    &quot;mapping_sha256&quot;: &quot;788a9448151a7fc287c5568e723aafd29e707ee2ac8b7e8a819a4d09a664cba6&quot;,
    &quot;raw_sha256&quot;: &quot;0397fd20169213540b4f24eeeacc2bb6470bee147b32de9f3d9b661c0ffe23f3&quot;,
    &quot;sink_boundaries_sha256&quot;: &quot;298f39af069bfb678e6b403372c253e2c6a7e6c9e8539bc8076e81f21205839a&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v3&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;473100570ed68856bd1fdc2d9de059b8dba374cfc488786dc5c72b6b2fb29e8d&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v3&quot;,
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
          3
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
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          2,
          3
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
      &quot;sha256&quot;: &quot;1393ccf7e8e2143eb17ab3bff6bd595cc35bd8fbcdc2aed9056b1a87f1264d66&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v4&quot;
    },
    &quot;raw_sha256&quot;: &quot;0397fd20169213540b4f24eeeacc2bb6470bee147b32de9f3d9b661c0ffe23f3&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v3&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_txt&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
          &quot;reason&quot;: &quot;源文标识本地 count.txt 文件为写入目标。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count.txt&quot;,
          &quot;reason&quot;: &quot;CFG 外部资源标识符确认存储位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0030&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention;&quot;,
          &quot;reason&quot;: &quot;按 EM12 默认属性声明 task 访问和 persistent 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_index_search&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
          &quot;reason&quot;: &quot;源文定义 index.search 工具调用边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;index.search&quot;,
          &quot;reason&quot;: &quot;CFG 外部资源标识符确认工具边界。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
          &quot;reason&quot;: &quot;未说明本地部署，按 EM12 保守声明 recipient 访问、retention 为 null，且不声称网络通信。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_request_json&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
          &quot;reason&quot;: &quot;源文标识 request.json 为用户提供的本地文件；按 EM12 文件默认属性声明访问范围和保留。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;request.json&quot;,
          &quot;reason&quot;: &quot;CFG 外部资源标识符确认该存储位置。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention;&quot;,
          &quot;reason&quot;: &quot;按 EM12 默认属性声明 task 访问和 persistent 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_count_txt&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;count.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_010&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;loc_index_search&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;index.search&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      },
      &quot;loc_request_json&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;request.json&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
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
            &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
            &quot;reason&quot;: &quot;源文指示工作流读取 request.json，该动作由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
            &quot;reason&quot;: &quot;读取操作将 request.json 内容引入当前流程，作为数据源。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read_request_json&quot;,
            &quot;reason&quot;: &quot;CFG 操作码表明读取外部文件内容，对应 fs_read。&quot;,
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
            &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;提取 query term 是工作流中由 agent runtime 执行的步骤。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;which contains term&quot;,
            &quot;reason&quot;: &quot;从请求容器中选出 term 字段，属于处理内容。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;字段选择/提取是 transform 效果，且保持原值。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;提取可选 from_date 参数由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
            &quot;reason&quot;: &quot;从请求中提取可选字段并判断存在性，属于处理内容。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged;&quot;,
            &quot;reason&quot;: &quot;字段提取及存在性判断是 transform 效果。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;提取可选 limit 参数由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;may contain from_date and limit&quot;,
            &quot;reason&quot;: &quot;从请求中提取可选字段并判断存在性，属于处理内容。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;字段提取及存在性判断是 transform 效果。&quot;,
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
            &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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
            &quot;reason&quot;: &quot;工作流指令由 agent runtime 发起对工具的调用。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;index.search&quot;,
            &quot;reason&quot;: &quot;CFG 操作码表明工具 index.search 执行搜索动作。&quot;,
            &quot;ref_id&quot;: &quot;g_0023&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value&quot;,
            &quot;reason&quot;: &quot;工具返回搜索响应，将内容引入当前流程，作为 source。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;请求参数被交付到 index.search 工具边界，作为 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;index.search supports fuzzy matching&quot;,
            &quot;reason&quot;: &quot;该能力说明 index.search 对查询进行匹配处理，作为 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_006&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
            &quot;reason&quot;: &quot;未提供网络通信证据，不声明 net_send/net_receive；工具请求与获取以 null-effect 事件表达，无可套用的效果标签。&quot;,
            &quot;ref_id&quot;: &quot;EM06&quot;,
            &quot;value&quot;: null
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;roles&quot;: [
          &quot;source&quot;,
          &quot;sink&quot;,
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
            &quot;reason&quot;: &quot;该指令为控制流分发，由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;dispatch 是纯控制操作，不引入、加工或送出数据，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作不在效果词汇表内，无适用效果，不能强制 transform。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value&quot;,
            &quot;reason&quot;: &quot;提取响应 total 由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
            &quot;reason&quot;: &quot;从响应中选出 total 字段，属于处理内容。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
            &quot;reason&quot;: &quot;字段选择是 transform 效果。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;工作流指令由 agent runtime 执行写文件。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;将内容写入本地文件存储，作为 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;创建或修改文件内容，对应 fs_write。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;提取响应 items 由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;从响应中选出 items 字段，属于处理内容。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;字段选择是 transform 效果。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;普通返回由 agent runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;普通返回不引入新源、不写入存储、不执行变换，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;普通返回不是用户输出或网络发送，且没有适用的效果词汇；按 REP02 事件和绑定可为空。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
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
                        &quot;quote&quot;: &quot;Read the user-supplied request.json&quot;,
                        &quot;reason&quot;: &quot;读取整个 request.json 内容；源文未提供 key-only 读取接口，按 EM01 保留整体读取。&quot;,
                        &quot;ref_id&quot;: &quot;src_007&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_request_json&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;request_json_contents&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 EM10 默认模式处理，读取输出按契约可能被模型观察。&quot;,
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
                &quot;quote&quot;: &quot;request.json contents&quot;,
                &quot;reason&quot;: &quot;公开输出绑定读取得到的 request.json 内容。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;request_json_contents&quot;
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
                        &quot;quote&quot;: &quot;using request.term unchanged as its query argument.&quot;,
                        &quot;reason&quot;: &quot;明确选出已有 term 字段并保持原值，符合 select_part。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文只规定字段选择关系，未声明模型处理或本地隔离，按 default 模式。&quot;,
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
                &quot;quote&quot;: &quot;request.term&quot;,
                &quot;reason&quot;: &quot;公开输出绑定选出的 term 字段值。&quot;,
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
                        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged;&quot;,
                        &quot;reason&quot;: &quot;明确选出已有 from_date 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
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
                        &quot;reason&quot;: &quot;存在性标志由请求容器是否含 from_date 推导；使用 compute 表示该判断。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
                &quot;quote&quot;: &quot;request.from_date&quot;,
                &quot;reason&quot;: &quot;公开输出绑定 from_date 值。&quot;,
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
                &quot;reason&quot;: &quot;公开输出绑定存在性标志。&quot;,
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
                        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                        &quot;reason&quot;: &quot;明确选出已有 limit 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
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
                        &quot;quote&quot;: &quot;When limit is present&quot;,
                        &quot;reason&quot;: &quot;存在性标志由请求容器是否含 limit 推导；使用 compute 表示该判断。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
                &quot;quote&quot;: &quot;request.limit&quot;,
                &quot;reason&quot;: &quot;公开输出绑定 limit 值。&quot;,
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
                &quot;reason&quot;: &quot;公开输出绑定存在性标志。&quot;,
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
                      &quot;possible&quot;,
                      &quot;possible&quot;,
                      &quot;possible&quot;,
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                        &quot;reason&quot;: &quot;可选参数按存在性条件传入；用 compute 保守组合，所有依赖均为 possible，不声称精确原值传递。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
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
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;optional_search_args&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                        &quot;reason&quot;: &quot;将 query term 原值和条件组合的可选参数交付到 index.search 工具边界。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;optional_search_args&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;loc_index_search&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
                        &quot;reason&quot;: &quot;从 index.search 工具边界获取搜索响应，并记录实际请求值依赖。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;工具调用未声明模型处理或本地隔离边界，按 default 模式；接收输出按 EM10 可能被模型观察。&quot;,
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
                &quot;quote&quot;: &quot;index.search response&quot;,
                &quot;reason&quot;: &quot;公开输出绑定工具获取的搜索响应。&quot;,
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
                        &quot;quote&quot;: &quot;write the response&#x27;s total value&quot;,
                        &quot;reason&quot;: &quot;明确选出响应中的 total 字段并保持原值。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
                &quot;quote&quot;: &quot;search response total&quot;,
                &quot;reason&quot;: &quot;公开输出绑定选出的 total 值。&quot;,
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
                        &quot;quote&quot;: &quot;write the response&#x27;s total value to local count.txt.&quot;,
                        &quot;reason&quot;: &quot;将 total 值写入 count.txt；未说明追加，按普通写入替换处理。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，写文件按 default 模式。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
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
                        &quot;reason&quot;: &quot;明确选出响应中的 items 字段并保持原值。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs;&quot;,
                &quot;reason&quot;: &quot;源文未声明模型处理或本地隔离边界，按 default 模式。&quot;,
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
                &quot;quote&quot;: &quot;search response items&quot;,
                &quot;reason&quot;: &quot;公开输出绑定选出的 items 值。&quot;,
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
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      }
    }
  }
}</pre>

</details>

