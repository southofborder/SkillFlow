# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v5`；SHA-256：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

求解状态：`complete`。

IR 记录覆盖：12 / 12。

[本地可视化审查](report.html) · [唯一业务结果](../doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。标为“控制”的槽只决定字段加入或观察是否发生，不属于该交付的载荷。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](../audit/material.json)（execution_model）；逐项依据在下方审计区展开。

## 接收与保存边界

纳入清单 12 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。

等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。

| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |
|---|---|---|---|---|---|
| ir_001 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D014 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_003 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D014 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_004 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D014 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D014 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D011; 1: D015; 2: D008 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 3.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D007 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 5.1 | 纳入 | external_tool / 2 | loc_index_search · tool: index.search · recipient / 未建模期限 | 0: D001, D012, D013, D017 | 另一接收主体或跨主体共享；cfg/g_0023, source/src_008, execution_model/EM06, execution_model/EM12 |
| ir_007 / 7.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D004, D018, D019, D021 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_009 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D004, D018, D019, D021 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_010 / 1.1 | 纳入 | storage_write / 1 | loc_count_txt · storage: count.txt · task / persistent | 0: D006, D009, D010, D016 | 任务内部、跨任务留存；source/src_013, cfg/g_0030, execution_model/EM12 |
| ir_011 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D004, D018, D019, D021 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |

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
| 1.1 | fs_read | read | — | storage: request.json | 0: D014 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D014 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_001`：未绑定 → D014

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示 request.json 内容，绑定到读取局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_content&quot;
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
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;该工作流指令要求读取用户提供的文件，由本地 agent_runtime 执行；未指定模型或工具参与读取。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;读取将 request.json 内容引入当前流程，属于 source 角色。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;该指令读取文件 request.json 内容，符合 fs_read。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
        &quot;value&quot;: &quot;fs_read&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，按默认模式分析读取输出。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;源文只要求读取文件，未说明本地或模型处理边界。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;,
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
          &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
          &quot;reason&quot;: &quot;读取 request.json 当前内容到局部值 request_content。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
          &quot;reason&quot;: &quot;没有显式 key-only 读取机制，保留整个文件作为可能获取范围。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_request_json&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;request_content&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，按默认模式分析读取输出。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
          &quot;reason&quot;: &quot;源文只要求读取文件，未说明本地或模型处理边界。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_content&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
        &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D014 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D014 | — | 0: D011 |

入口／出口变化：

- `result: result_002`：未绑定 → D011

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示 request.term，绑定到选出的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;term&quot;
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
        &quot;reason&quot;: &quot;该字段提取指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;选择并保留 request.term 字段，处理内容，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，字段提取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;该指令从输入容器选择显式 term 字段并保持原值，属于 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，字段提取按默认模式分析。&quot;,
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
          &quot;reason&quot;: &quot;明确从输入选择 request.term 字段并保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;term&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D014 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D014 | — | 0: D002 |
| 2.2 | transform | compute | 0: D014 | — | 0: D015 |

入口／出口变化：

- `result: result_003`：未绑定 → D002
- `result: result_004`：未绑定 → D015

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示 from_date 值，绑定到选出的局部值。&quot;,
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
          &quot;reason&quot;: &quot;CFG 输出表示存在性布尔，绑定到计算的局部值。&quot;,
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
        &quot;reason&quot;: &quot;该可选字段提取与存在性判断指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;reason&quot;: &quot;提取可选值并计算其存在性，处理内容，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;reason&quot;: &quot;提取可选 from_date 原值并计算存在性，属于 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
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
          &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
          &quot;reason&quot;: &quot;存在时保留 from_date 原值。&quot;,
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
          &quot;quote&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
          &quot;reason&quot;: &quot;需要判断 from_date 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
          &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;,
          &quot;ref_id&quot;: &quot;EM14&quot;
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D014 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D014 | — | 0: D007 |
| 2.2 | transform | compute | 0: D014 | — | 0: D008 |

入口／出口变化：

- `result: result_005`：未绑定 → D007
- `result: result_006`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示 limit 值，绑定到选出的局部值。&quot;,
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
          &quot;reason&quot;: &quot;CFG 输出表示存在性布尔，绑定到计算的局部值。&quot;,
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
        &quot;reason&quot;: &quot;该可选字段提取与存在性判断指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0017&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;提取可选 limit 值并计算其存在性，处理内容，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;reason&quot;: &quot;提取可选 limit 原值并计算存在性，属于 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
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
          &quot;reason&quot;: &quot;存在时保留 limit 原值。&quot;,
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
          &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
          &quot;reason&quot;: &quot;需要判断 limit 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
          &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;,
          &quot;ref_id&quot;: &quot;EM14&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
        &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0018&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
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
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 5,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 5,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 6,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 5,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D011; 1: D015; 2: D008 | model_context: 当前模型处理上下文 | — |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D002; 1（控制）: D015；条件：保留加入与省略的可能 | model_context: 当前模型处理上下文 | — |
| 3.1 | model_observe（程序生成，静态可能） | deliver | 0: D007; 1（控制）: D008；条件：保留加入与省略的可能 | model_context: 当前模型处理上下文 | — |
| 4.1 | transform | build | 0: D011; 1（控制）: D015; 2: D002; 3（控制）: D008; 4: D007 | — | 0: D001, D012, D013, D017 |
| 4.1 · 成员 | — | [   &quot;query&quot; ] | 原值槽 0；条件槽 None | — | 加入原值 |
| 4.1 · 成员 | — | [   &quot;from_date&quot; ] | 原值槽 2；条件槽 1 | — | 加入／省略两种候选 |
| 4.1 · 成员 | — | [   &quot;limit&quot; ] | 原值槽 4；条件槽 3 | — | 加入／省略两种候选 |
| 5.1 | 无标签数据操作 | deliver | 0: D001, D012, D013, D017 | tool: index.search | — |
| 6.1 | 无标签数据操作 | receive | 0: D001, D012, D013, D017 | tool: index.search | 0: D004, D018, D019, D021 |
| 7.1 | model_observe（程序生成，静态可能） | deliver | 0: D004, D018, D019, D021 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_007`：未绑定 → D004, D018, D019, D021

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示 index.search 响应，绑定到 receive 获得的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
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
      &quot;model_observe&quot;,
      &quot;model_observe&quot;,
      &quot;model_observe&quot;,
      &quot;transform&quot;,
      &quot;model_observe&quot;
    ],
    &quot;evidences&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;工作流运行时构造并调度该调用；未指定 LLM 参与。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;CFG 将 index.search 标为外部资源操作码，实际搜索动作由该工具执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;index.search response&quot;,
        &quot;reason&quot;: &quot;调用返回搜索响应，将结果引入当前流程，属于 source。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;实际参数被送到 index.search 工具边界，内容到达该边界，属于 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
        &quot;reason&quot;: &quot;该 IR 组合 query 与可选参数构造请求，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 3,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;reason&quot;: &quot;将 term 及可选 from_date/limit 组合为调用参数对象，属于组合/表示转换；网络传输未建立，获取响应用 null-effect 事件表示。&quot;,
        &quot;ref_id&quot;: &quot;src_009&quot;,
        &quot;value&quot;: &quot;transform&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 4,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 4,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 4,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
        &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 3,
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
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;,
      &quot;when&quot;: {
        &quot;index&quot;: 3,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 4,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;,
      &quot;when&quot;: {
        &quot;index&quot;: 5,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;container&quot;: &quot;object&quot;,
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
          &quot;reason&quot;: &quot;query 成员来自当前 IR 的查询词输入，保持原值。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
          &quot;reason&quot;: &quot;from_date 成员在存在时包含原值，并由存在性布尔控制。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
          &quot;reason&quot;: &quot;limit 成员在存在时包含原值，并由存在性布尔控制。&quot;,
          &quot;ref_id&quot;: &quot;src_009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
          &quot;reason&quot;: &quot;from_date 与 limit 用各自存在性布尔作为 when；存在性标志不作为 payload。&quot;,
          &quot;ref_id&quot;: &quot;EM14&quot;
        }
      ],
      &quot;op&quot;: &quot;build&quot;,
      &quot;output&quot;: &quot;request&quot;,
      &quot;parts&quot;: [
        {
          &quot;path&quot;: [
            &quot;query&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        },
        {
          &quot;path&quot;: [
            &quot;from_date&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 2,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: {
            &quot;index&quot;: 3,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        {
          &quot;path&quot;: [
            &quot;limit&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 4,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: {
            &quot;index&quot;: 5,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request.&quot;,
          &quot;reason&quot;: &quot;未发现实际网络机制，将实际请求参数投递到 index.search 工具边界，记为 null-effect deliver。&quot;,
          &quot;ref_id&quot;: &quot;EM13&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;该指令确实把构造的参数对象交给 index.search。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_index_search&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event.&quot;,
          &quot;reason&quot;: &quot;index.search 返回内容有获取边界，但未建立网络传输，故在工具位置用 null-effect receive 获取。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;响应来自这次实际调用；请求依赖为同一 request 对象。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request&quot;
        }
      ],
      &quot;location&quot;: &quot;loc_index_search&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
          &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;response&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
        &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
        &quot;ref_id&quot;: &quot;g_0024&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D004, D018, D019, D021 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D004, D018, D019, D021 | — | 0: D006, D009, D010, D016 |

入口／出口变化：

- `result: result_008`：未绑定 → D006, D009, D010, D016

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示响应 total，绑定到选出的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0029&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;total&quot;
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
        &quot;reason&quot;: &quot;该响应字段提取指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0029&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;从搜索响应中选出 total 字段，处理内容，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;选择响应 total 原值，属于 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
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
          &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
          &quot;reason&quot;: &quot;明确从搜索响应选择 total 原值。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;total&quot;,
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
| 1.1 | fs_write | write | 0: D006, D009, D010, D016 | storage: count.txt | storage: count.txt: 未绑定 → D006, D009, D010, D016 (strong) |

入口／出口变化：

- `storage: count.txt`：未绑定 → D006, D009, D010, D016

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
        &quot;reason&quot;: &quot;该文件写入指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;将 total 写入本地 count.txt 存储位置，内容到达该位置，属于 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;写入文件 count.txt，符合 fs_write。&quot;,
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
          &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
          &quot;reason&quot;: &quot;将当前 IR 输入中的 total 值写入 count.txt；未说明追加，按 replace 表示写文件内容。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D004, D018, D019, D021 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | select_part | 0: D004, D018, D019, D021 | — | 0: D003, D005, D020, D022 |

入口／出口变化：

- `result: result_009`：未绑定 → D003, D005, D020, D022

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
          &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
          &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
          &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;reason&quot;: &quot;CFG 输出表示响应 items，绑定到选出的局部值。&quot;,
          &quot;ref_id&quot;: &quot;g_0031&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;items&quot;
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
        &quot;reason&quot;: &quot;该响应字段提取指令由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0031&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;选择响应 items 字段，处理内容，属于 transformer。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;transformer&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
        &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
        &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;选择 items 原值，属于 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
          &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
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
          &quot;reason&quot;: &quot;明确从搜索响应选择 items 原值。&quot;,
          &quot;ref_id&quot;: &quot;src_014&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;items&quot;,
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
          &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
          &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
          &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
          &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
          &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
          &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
          &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
          &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
          &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
          &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
          &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
          &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
        &quot;reason&quot;: &quot;该普通 return 由 agent_runtime 执行。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;普通 return 仅标识返回输入，不建立用户输出、网络交付或调用方位置，roles 无适用标签。&quot;,
        &quot;ref_id&quot;: &quot;src_014&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
        &quot;reason&quot;: &quot;普通返回不一定是用户输出，也未建立其他词汇内 effect；空 effects 不表示无返回。&quot;,
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
| D001 | data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb | known_parts |
| D002 | data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6 | opaque |
| D003 | data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5 | opaque |
| D004 | data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7 | known_parts |
| D005 | data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce | opaque |
| D006 | data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169 | opaque |
| D007 | data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f | opaque |
| D008 | data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4 | opaque |
| D009 | data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594 | opaque |
| D010 | data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9 | opaque |
| D011 | data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f | opaque |
| D012 | data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c | known_parts |
| D013 | data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2 | known_parts |
| D014 | data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7 | known_parts |
| D015 | data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d | opaque |
| D016 | data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a | opaque |
| D017 | data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383 | known_parts |
| D018 | data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d | known_parts |
| D019 | data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50 | known_parts |
| D020 | data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a | opaque |
| D021 | data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b | known_parts |
| D022 | data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4 | opaque |

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
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;from_date&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
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
  &quot;id&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
    &quot;path&quot;: [
      &quot;from_date&quot;
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
  &quot;id&quot;: &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
        &quot;data&quot;: &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 5, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;
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
  &quot;id&quot;: &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
  &quot;id&quot;: &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
  &quot;id&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
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
  &quot;id&quot;: &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
  &quot;id&quot;: &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
  &quot;id&quot;: &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
  &quot;id&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
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
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;limit&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;from_date&#x27;], [&#x27;limit&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
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
  &quot;id&quot;: &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_004&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
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
  &quot;id&quot;: &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
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
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;,
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;,
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 5, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 5, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;
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
  &quot;id&quot;: &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
  }
}</pre>

</details>

<details><summary>D021：完整 Data 内容、来源与依赖</summary>

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
        &quot;data&quot;: &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 5, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D022：完整 Data 内容、来源与依赖</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
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
        &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
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
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
        &quot;reason&quot;: &quot;源文明确将 total 写入本地 count.txt 文件。&quot;,
        &quot;ref_id&quot;: &quot;src_013&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;count.txt&quot;,
        &quot;reason&quot;: &quot;CFG 输入将 count.txt 标为外部资源操作数，操作数指向该文件容器。&quot;,
        &quot;ref_id&quot;: &quot;g_0030&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name.&quot;,
        &quot;reason&quot;: &quot;没有临时清理机制证据，按文件默认 task/persistent。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_index_search&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;index.search&quot;,
        &quot;reason&quot;: &quot;CFG 输入将 index.search 标为外部资源操作数，形成工具内容获取/投递边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0023&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
        &quot;reason&quot;: &quot;源文要求调用该具名工具。&quot;,
        &quot;ref_id&quot;: &quot;src_008&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
        &quot;reason&quot;: &quot;仅工具名不证明网络通信，因此不声明 remote。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
        &quot;reason&quot;: &quot;未说明部署，按 EM12 保留外部接收方可能，access_scope=recipient，retention=null。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_request_json&quot;: [
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
        &quot;reason&quot;: &quot;源文明确读取用户提供的 request.json 文件内容，位置类别为 storage。&quot;,
        &quot;ref_id&quot;: &quot;src_007&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;request.json&quot;,
        &quot;reason&quot;: &quot;CFG 输入将 request.json 标为外部资源操作数，操作数指向该文件容器。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name.&quot;,
        &quot;reason&quot;: &quot;没有临时使用和清理机制证据，按文件默认 task/persistent。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 10,
    &quot;data_count&quot;: 22,
    &quot;description_revision&quot;: 11,
    &quot;record_count&quot;: 12
  }
}</pre>

</details>

<details><summary>编译审计：模型原始处理段与程序生成位置映射</summary>

<pre>{
  &quot;compilation&quot;: {
    &quot;compiled_sha256&quot;: &quot;f3c6cbf77a40287c333d2d7498a28991aac135e0408cb44beb29433238578171&quot;,
    &quot;mapping_sha256&quot;: &quot;b0183ca29c675318f8fe5a688d1795f27ad6d1d705789daccf32517683c96f7e&quot;,
    &quot;raw_sha256&quot;: &quot;6f8d0ac85c4f43e4fe901ad472ee2f7351f0160554c990723ae01067db92dc9d&quot;,
    &quot;sink_boundaries_sha256&quot;: &quot;f8193730ec81e41c951bee40462d1471973971fc117dff067b2288c0a232cba5&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v4&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;f3c6cbf77a40287c333d2d7498a28991aac135e0408cb44beb29433238578171&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v4&quot;,
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
          2
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
          3
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
          4
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
          1
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          5
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
          2
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;transfer_specs&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          6
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
          2
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
      &quot;sha256&quot;: &quot;d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v5&quot;
    },
    &quot;raw_sha256&quot;: &quot;6f8d0ac85c4f43e4fe901ad472ee2f7351f0160554c990723ae01067db92dc9d&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v4&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_count_txt&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
          &quot;reason&quot;: &quot;源文明确将 total 写入本地 count.txt 文件。&quot;,
          &quot;ref_id&quot;: &quot;src_013&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;count.txt&quot;,
          &quot;reason&quot;: &quot;CFG 输入将 count.txt 标为外部资源操作数，操作数指向该文件容器。&quot;,
          &quot;ref_id&quot;: &quot;g_0030&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name.&quot;,
          &quot;reason&quot;: &quot;没有临时清理机制证据，按文件默认 task/persistent。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_index_search&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;index.search&quot;,
          &quot;reason&quot;: &quot;CFG 输入将 index.search 标为外部资源操作数，形成工具内容获取/投递边界。&quot;,
          &quot;ref_id&quot;: &quot;g_0023&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call index.search exactly once&quot;,
          &quot;reason&quot;: &quot;源文要求调用该具名工具。&quot;,
          &quot;ref_id&quot;: &quot;src_008&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
          &quot;reason&quot;: &quot;仅工具名不证明网络通信，因此不声明 remote。&quot;,
          &quot;ref_id&quot;: &quot;EM06&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution.&quot;,
          &quot;reason&quot;: &quot;未说明部署，按 EM12 保留外部接收方可能，access_scope=recipient，retention=null。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_request_json&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
          &quot;reason&quot;: &quot;源文明确读取用户提供的 request.json 文件内容，位置类别为 storage。&quot;,
          &quot;ref_id&quot;: &quot;src_007&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;request.json&quot;,
          &quot;reason&quot;: &quot;CFG 输入将 request.json 标为外部资源操作数，操作数指向该文件容器。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name.&quot;,
          &quot;reason&quot;: &quot;没有临时使用和清理机制证据，按文件默认 task/persistent。&quot;,
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
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;该工作流指令要求读取用户提供的文件，由本地 agent_runtime 执行；未指定模型或工具参与读取。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;读取将 request.json 内容引入当前流程，属于 source 角色。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;该指令读取文件 request.json 内容，符合 fs_read。&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
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
            &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
            &quot;reason&quot;: &quot;该字段提取指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0015&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;选择并保留 request.term 字段，处理内容，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;该指令从输入容器选择显式 term 字段并保持原值，属于 transform。&quot;,
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
            &quot;reason&quot;: &quot;该可选字段提取与存在性判断指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;提取可选值并计算其存在性，处理内容，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;提取可选 from_date 原值并计算存在性，属于 transform。&quot;,
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
            &quot;reason&quot;: &quot;该可选字段提取与存在性判断指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0017&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;提取可选 limit 值并计算其存在性，处理内容，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;提取可选 limit 原值并计算存在性，属于 transform。&quot;,
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
            &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0018&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
        &quot;effects&quot;: [
          &quot;transform&quot;
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;工作流运行时构造并调度该调用；未指定 LLM 参与。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;index.search&quot;,
            &quot;reason&quot;: &quot;CFG 将 index.search 标为外部资源操作码，实际搜索动作由该工具执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0023&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;index.search response&quot;,
            &quot;reason&quot;: &quot;调用返回搜索响应，将结果引入当前流程，属于 source。&quot;,
            &quot;ref_id&quot;: &quot;g_0023&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;实际参数被送到 index.search 工具边界，内容到达该边界，属于 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;该 IR 组合 query 与可选参数构造请求，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;将 term 及可选 from_date/limit 组合为调用参数对象，属于组合/表示转换；网络传输未建立，获取响应用 null-effect 事件表示。&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;value&quot;: &quot;transform&quot;
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
            &quot;reason&quot;: &quot;该控制转移指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;仅控制转移，不引入、到达或处理内容，roles 无适用标签。&quot;,
            &quot;ref_id&quot;: &quot;g_0024&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制操作，在本词汇下无适用 effect；这不表示该 IR 是空操作。&quot;,
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
            &quot;reason&quot;: &quot;该响应字段提取指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0029&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;从搜索响应中选出 total 字段，处理内容，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;选择响应 total 原值，属于 transform。&quot;,
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
            &quot;reason&quot;: &quot;该文件写入指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0030&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;将 total 写入本地 count.txt 存储位置，内容到达该位置，属于 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;写入文件 count.txt，符合 fs_write。&quot;,
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
            &quot;reason&quot;: &quot;该响应字段提取指令由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0031&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;选择响应 items 字段，处理内容，属于 transformer。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;选择 items 原值，属于 transform。&quot;,
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
            &quot;reason&quot;: &quot;该普通 return 由 agent_runtime 执行。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;普通 return 仅标识返回输入，不建立用户输出、网络交付或调用方位置，roles 无适用标签。&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;普通返回不一定是用户输出，也未建立其他词汇内 effect；空 effects 不表示无返回。&quot;,
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
                        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
                        &quot;reason&quot;: &quot;读取 request.json 当前内容到局部值 request_content。&quot;,
                        &quot;ref_id&quot;: &quot;src_007&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
                        &quot;reason&quot;: &quot;没有显式 key-only 读取机制，保留整个文件作为可能获取范围。&quot;,
                        &quot;ref_id&quot;: &quot;EM01&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_request_json&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;request_content&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，按默认模式分析读取输出。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
                &quot;reason&quot;: &quot;源文只要求读取文件，未说明本地或模型处理边界。&quot;,
                &quot;ref_id&quot;: &quot;src_007&quot;
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
                &quot;reason&quot;: &quot;CFG 输出表示 request.json 内容，绑定到读取局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;request_content&quot;
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
                        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                        &quot;reason&quot;: &quot;明确从输入选择 request.term 字段并保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;term&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，字段提取按默认模式分析。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示 request.term，绑定到选出的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0015&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;term&quot;
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
                        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                        &quot;reason&quot;: &quot;存在时保留 from_date 原值。&quot;,
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
                        &quot;quote&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
                        &quot;reason&quot;: &quot;需要判断 from_date 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                        &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;,
                        &quot;ref_id&quot;: &quot;EM14&quot;
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示 from_date 值，绑定到选出的局部值。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示存在性布尔，绑定到计算的局部值。&quot;,
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
                        &quot;reason&quot;: &quot;存在时保留 limit 原值。&quot;,
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
                        &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
                        &quot;reason&quot;: &quot;需要判断 limit 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                        &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;,
                        &quot;ref_id&quot;: &quot;EM14&quot;
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示 limit 值，绑定到选出的局部值。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示存在性布尔，绑定到计算的局部值。&quot;,
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
                    &quot;container&quot;: &quot;object&quot;,
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                        &quot;reason&quot;: &quot;query 成员来自当前 IR 的查询词输入，保持原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                        &quot;reason&quot;: &quot;from_date 成员在存在时包含原值，并由存在性布尔控制。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                        &quot;reason&quot;: &quot;limit 成员在存在时包含原值，并由存在性布尔控制。&quot;,
                        &quot;ref_id&quot;: &quot;src_009&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                        &quot;reason&quot;: &quot;from_date 与 limit 用各自存在性布尔作为 when；存在性标志不作为 payload。&quot;,
                        &quot;ref_id&quot;: &quot;EM14&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;build&quot;,
                    &quot;output&quot;: &quot;request&quot;,
                    &quot;parts&quot;: [
                      {
                        &quot;path&quot;: [
                          &quot;query&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      },
                      {
                        &quot;path&quot;: [
                          &quot;from_date&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: {
                          &quot;index&quot;: 3,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;path&quot;: [
                          &quot;limit&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 4,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: {
                          &quot;index&quot;: 5,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
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
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request.&quot;,
                        &quot;reason&quot;: &quot;未发现实际网络机制，将实际请求参数投递到 index.search 工具边界，记为 null-effect deliver。&quot;,
                        &quot;ref_id&quot;: &quot;EM13&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                        &quot;reason&quot;: &quot;该指令确实把构造的参数对象交给 index.search。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;request&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;loc_index_search&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event.&quot;,
                        &quot;reason&quot;: &quot;index.search 返回内容有获取边界，但未建立网络传输，故在工具位置用 null-effect receive 获取。&quot;,
                        &quot;ref_id&quot;: &quot;EM09&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                        &quot;reason&quot;: &quot;响应来自这次实际调用；请求依赖为同一 request 对象。&quot;,
                        &quot;ref_id&quot;: &quot;src_008&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;request&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;loc_index_search&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;response&quot;
                  }
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;,
                &quot;ref_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;,
                &quot;ref_id&quot;: &quot;src_008&quot;
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
                &quot;reason&quot;: &quot;CFG 输出表示 index.search 响应，绑定到 receive 获得的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0023&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response&quot;
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
                        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                        &quot;reason&quot;: &quot;明确从搜索响应选择 total 原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_013&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;total&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示响应 total，绑定到选出的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0029&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;total&quot;
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
                        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                        &quot;reason&quot;: &quot;将当前 IR 输入中的 total 值写入 count.txt；未说明追加，按 replace 表示写文件内容。&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，文件写入按默认模式分析。&quot;,
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
                        &quot;reason&quot;: &quot;明确从搜索响应选择 items 原值。&quot;,
                        &quot;ref_id&quot;: &quot;src_014&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;items&quot;,
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
                &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
                &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;,
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
                &quot;reason&quot;: &quot;CFG 输出表示响应 items，绑定到选出的局部值。&quot;,
                &quot;ref_id&quot;: &quot;g_0031&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;items&quot;
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

