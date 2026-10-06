# 基础数据传播记录

**以下记录为统一抽象运行时契约下的静态可能行为，不是运行日志。complete 只表示已在契约下完成求解，不证明模型实际观察了这些内容。默认补充的观察与明确例外共同约束分析范围；使用固定顺序或没有引用契约规则，都不能据此认定为确定执行事实。**

统一契约：`skillflow-abstract-runtime-v5`；SHA-256：`d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a`。

求解状态：`complete`。

IR 记录覆盖：26 / 26。

[本地可视化审查](report.html) · [唯一业务结果](../doe-input.json)

D 编号是报告内数据短名。行内输入／输出编号属于原子操作参数，不是原 IR 操作数编号。标为“控制”的槽只决定字段加入或观察是否发生，不属于该交付的载荷。候选集合不表示同时发生，possible 不表示明文完整包含。本轮不判断风险、必要性或 DOE。读取范围、模型观察、明确取值与实际传参分别审查；tool 边界不表示网络通信。

[冻结契约全文与标注输入](../audit/material.json)（execution_model）；逐项依据在下方审计区展开。

## 接收与保存边界

纳入清单 16 个操作位置；逐元素候选组分别显示参数，清单按既有作用域位置登记。

等级仅表示边界性质：0 任务内临时，1 任务内持久，2 另一主体／共享，3 公开。它不表示数据敏感度、必要性或最终风险。未求值操作由覆盖表指明；空参数不等于未建模内容不存在。

| IR / 步骤 | 纳入 | 类型 / 等级 | 目标、访问 / 留存 | 实际参数（逐位置） | 原因与属性依据 |
|---|---|---|---|---|---|
| ir_001 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D003 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_003 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D010 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_005 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D019 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_007 / 1.1 | 纳入 | external_tool / 2 | loc_fast_fetch_tool · tool: fast.fetch · recipient / 未建模期限 | 0: D014; 1: D019 | 另一接收主体或跨主体共享；cfg/g_0027, cfg/g_0039, source/src_003, execution_model/EM12, execution_model/EM06 |
| ir_007 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D008 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_009 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D008 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_011 / 1.1 | 纳入 | external_tool / 2 | loc_fast_fetch_tool · tool: fast.fetch · recipient / 未建模期限 | 0: D014; 1: D019 | 另一接收主体或跨主体共享；cfg/g_0027, cfg/g_0039, source/src_003, execution_model/EM12, execution_model/EM06 |
| ir_011 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_013 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D002 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_015 / 1.1 | 纳入 | external_tool / 2 | loc_archive_fetch_tool · tool: archive.fetch · recipient / 未建模期限 | 0: D014 | 另一接收主体或跨主体共享；cfg/g_0051, source/src_003, execution_model/EM12, execution_model/EM06 |
| ir_015 / 2.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D017 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_017 / 1.1 | 纳入 | model_observe / 2 | __compiled_model_context__ · model_context: 当前模型处理上下文 · recipient / 未建模期限 | 0: D017 | 另一接收主体或跨主体共享；execution_model/EM10, execution_model/EM12 |
| ir_019 / 1.1 | 纳入 | storage_write / 1 | loc_status_file · storage: status.txt · task / persistent | 0: D009 | 任务内部、跨任务留存；cfg/g_0063, source/src_003, execution_model/EM12 |
| ir_021 / 1.1 | 纳入 | storage_write / 1 | loc_status_file · storage: status.txt · task / persistent | 0: D013 | 任务内部、跨任务留存；cfg/g_0063, source/src_003, execution_model/EM12 |
| ir_023 / 1.1 | 纳入 | storage_write / 1 | loc_status_file · storage: status.txt · task / persistent | 0: D011 | 任务内部、跨任务留存；cfg/g_0063, source/src_003, execution_model/EM12 |
| ir_025 / 1.1 | 纳入 | storage_write / 1 | loc_status_file · storage: status.txt · task / persistent | 0: D011 | 任务内部、跨任务留存；cfg/g_0063, source/src_003, execution_model/EM12 |

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
| 1.1 | context_read | read | — | runtime_context: user_request | 0: D003 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D003 | model_context: 当前模型处理上下文 | — |
| 3.1 | transform | select_part | 0: D003 | — | 0: D014 |

入口／出口变化：

- `result: result_001`：未绑定 → D014

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;该指令输出语义名为 source_id，绑定刚选出的字段原值。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;source_id_value&quot;
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
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;该读取是 Skill 工作流中的运行时动作，由本地 agent 运行时执行；源文未提及模型或人工参与。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;该操作从用户请求引入 source_id 内容进入当前流程，符合 source 角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;从用户请求这一运行时上下文获取调用方输入，属于 context_read。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;context_read&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;源文只描述从用户请求读取 source_id，未规定模型处理或显式本地隔离与限定回传，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
        &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留请求整体作为可能获取范围。&quot;,
        &quot;ref_id&quot;: &quot;EM01&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;目标字段是既有的 source_id，按字段原值选出，不发明新值。&quot;,
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
          &quot;reason&quot;: &quot;从用户请求上下文容器获取内容，是 context_read 的实际读取操作。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;a natural-language request for a field from a container does not establish a key-only read mechanism&quot;,
          &quot;reason&quot;: &quot;仅需一个字段不构成键限读取机制，读取输出保留请求整体作为可能范围。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
          &quot;reason&quot;: &quot;源文只描述从用户请求读取 source_id，未规定模型处理或显式本地隔离与限定回传，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
          &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留请求整体作为可能获取范围。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
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
          &quot;reason&quot;: &quot;目标字段是既有的 source_id，按字段原值选出，不发明新值。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;user_request_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;source_id_value&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0010&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;词汇表内无适用 effect；该指令只改变控制流，不产生内容效应。&quot;,
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
| 1.1 | context_read | read | — | runtime_context: environment | 0: D010 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D010 | model_context: 当前模型处理上下文 | — |
| 3.1 | transform | select_part | 0: D010 | — | 0: D019 |

入口／出口变化：

- `result: result_002`：未绑定 → D019

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出语义名为 fast_key，绑定选出的环境值。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key_value&quot;
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
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;环境读取由工作流运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;从环境上下文引入 FAST_KEY 值进入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;读取环境上下文属于 context_read。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;context_read&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;源文只描述从环境读取 FAST_KEY，未规定模型处理或本地隔离与限定回传，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
        &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留环境上下文整体作为可能获取范围。&quot;,
        &quot;ref_id&quot;: &quot;EM01&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 2,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;目标值是环境中的 FAST_KEY，按原值选出。&quot;,
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
          &quot;reason&quot;: &quot;从环境上下文容器获取内容，是 context_read 的实际读取操作。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;a natural-language request for a field from a container does not establish a key-only read mechanism&quot;,
          &quot;reason&quot;: &quot;命名一个变量不构成键限读取机制，读取输出保留环境整体作为可能范围。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;源文只描述从环境读取 FAST_KEY，未规定模型处理或本地隔离与限定回传，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
          &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留环境上下文整体作为可能获取范围。&quot;,
          &quot;ref_id&quot;: &quot;EM01&quot;
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
          &quot;reason&quot;: &quot;目标值是环境中的 FAST_KEY，按原值选出。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;environment_content&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_key_value&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0016&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;词汇表内无适用 effect；该指令只改变控制流。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D019 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D019 | — | 0: D012 |

入口／出口变化：

- `result: result_003`：未绑定 → D012

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出语义名为 fast_key_present，绑定计算所得的存在性布尔值。&quot;,
          &quot;ref_id&quot;: &quot;g_0021&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key_present_value&quot;
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
        &quot;reason&quot;: &quot;存在性检查由运行时在工作流中执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;对 FAST_KEY 值做存在性判定并产生新的布尔状态，属于对内容的处理。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;存在性判定没有模型处理或本地隔离证据，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留非隔离转换输入的可能观察。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
        &quot;reason&quot;: &quot;计算存在性布尔是对输入值的计算，属 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
          &quot;reason&quot;: &quot;存在性判定没有模型处理或本地隔离证据，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留非隔离转换输入的可能观察。&quot;,
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
          &quot;reason&quot;: &quot;对 FAST_KEY 值计算存在性布尔，结果派生依赖该输入。&quot;,
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
      &quot;output&quot;: &quot;fast_key_present_value&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;依据存在性标志的控制分支由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0022&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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

块：block_004；执行主体：agent_runtime, tool；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_004

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
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
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | deliver | 0: D014; 1: D019 | tool: fast.fetch | — |
| 1.2 | 无标签数据操作 | receive | 0: D014; 1: D019 | tool: fast.fetch | 0: D008 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D008 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_004`：未绑定 → D008

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出绑定本次获取的响应值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;运行时发起 fast.fetch 调用并传递实际参数。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;指令以 fast.fetch 为外部资源，由该工具执行抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
        &quot;reason&quot;: &quot;该调用返回的响应内容进入当前流程，符合 source 角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;source_id 与 FAST_KEY 作为参数被送达 fast.fetch 边界，内容可能到达外部接收方。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
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
        &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求；未见隔离或限定路由机制，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;fast.fetch 是已知工具但无网络传输机制证据，响应按工具边界获取。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
          &quot;reason&quot;: &quot;把 source_id 与 FAST_KEY 按输入顺序作为实际参数送达 fast.fetch 边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
          &quot;reason&quot;: &quot;无网络传输证据，请求送达以工具边界 null-effect deliver 表示，不声明 net_send。&quot;,
          &quot;ref_id&quot;: &quot;EM13&quot;
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
      &quot;target&quot;: &quot;loc_fast_fetch_tool&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
          &quot;reason&quot;: &quot;该调用输出为 fast.fetch 响应，响应内容在工具边界被获取。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
          &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序参数引用，形成唯一配对，获取跟随送达之后。&quot;,
          &quot;ref_id&quot;: &quot;EM15&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求；未见隔离或限定路由机制，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;fast.fetch 是已知工具但无网络传输机制证据，响应按工具边界获取。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0028&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D008 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D008 | — | 0: D009 |
| 2.2 | transform | select_part | 0: D008 | — | 0: D015 |

入口／出口变化：

- `result: result_005`：未绑定 → D009
- `result: result_006`：未绑定 → D015

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出语义名为 fast_fetch_first_outcome，绑定分类计算结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_outcome_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
          &quot;reason&quot;: &quot;输出语义名为 fast_fetch_first_body，绑定选出的 body 字段原值。&quot;,
          &quot;ref_id&quot;: &quot;g_0033&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_body_value&quot;
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
        &quot;reason&quot;: &quot;对首次响应做结果分类由运行时执行，用于区分成功、瞬时失败与非瞬时失败。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;对响应内容分类并选出 body 字段，属于对内容的处理。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;对首次响应分类的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留响应版本的可能观察。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;分类响应结果的计算属 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;对首次响应分类的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留响应版本的可能观察。&quot;,
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;分类需要区分成功、瞬时失败与非瞬时失败，属对响应输入的计算。&quot;,
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
      &quot;output&quot;: &quot;fast_fetch_first_outcome_value&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;源文明确 body 字段按原值返回，用 select_part 保持字段同一性，而非不透明计算。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_body_value&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;依据分类结果的控制分支由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0034&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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

块：block_006；执行主体：agent_runtime, tool；角色：source, sink。

IR 输入：0: fast.fetch, 1: result_001, 2: result_002

IR 输出：0: result_007

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
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
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | deliver | 0: D014; 1: D019 | tool: fast.fetch | — |
| 1.2 | 无标签数据操作 | receive | 0: D014; 1: D019 | tool: fast.fetch | 0: D002 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_007`：未绑定 → D002

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出绑定本次重试获取的响应值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;运行时按约束发起一次重试调用并传递参数。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;重试由 fast.fetch 工具执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
        &quot;reason&quot;: &quot;重试响应内容进入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;重试仍以 source_id 与 FAST_KEY 为参数送达 fast.fetch 边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
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
        &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
        &quot;reason&quot;: &quot;重试返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;fast.fetch 为已知工具但无网络传输机制证据，重试响应按工具边界获取。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
          &quot;reason&quot;: &quot;重试仍调用 fast.fetch，并以 source_id 与 FAST_KEY 作为参数送达同一工具边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
          &quot;reason&quot;: &quot;无网络传输证据，重试请求送达以工具边界 null-effect deliver 表示。&quot;,
          &quot;ref_id&quot;: &quot;EM13&quot;
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
      &quot;target&quot;: &quot;loc_fast_fetch_tool&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
          &quot;reason&quot;: &quot;该调用输出为重试响应，内容在工具边界被获取。&quot;,
          &quot;ref_id&quot;: &quot;g_0039&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
          &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序参数引用，形成唯一配对。&quot;,
          &quot;ref_id&quot;: &quot;EM15&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
          &quot;reason&quot;: &quot;重试返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;fast.fetch 为已知工具但无网络传输机制证据，重试响应按工具边界获取。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0040&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D002 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D002 | — | 0: D013 |
| 2.2 | transform | select_part | 0: D002 | — | 0: D007 |

入口／出口变化：

- `result: result_008`：未绑定 → D013
- `result: result_009`：未绑定 → D007

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出语义名为 fast_fetch_retry_outcome，绑定分类结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_outcome_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
          &quot;reason&quot;: &quot;输出语义名为 fast_fetch_retry_body，绑定选出的 body 原值。&quot;,
          &quot;ref_id&quot;: &quot;g_0045&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_body_value&quot;
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
        &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;对重试响应分类由运行时执行，用于判断成功或转入 archive.fetch 路径。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;对重试响应分类并选出 body 字段，属内容处理。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;对重试响应分类的处理无模型或本地隔离证据，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
        &quot;reason&quot;: &quot;识别重试结果为瞬时或非瞬时需要计算响应输入，属 transform。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
          &quot;reason&quot;: &quot;对重试响应分类的处理无模型或本地隔离证据，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
          &quot;reason&quot;: &quot;分类重试响应的成功/失败结果，依赖响应输入。&quot;,
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
      &quot;output&quot;: &quot;fast_fetch_retry_outcome_value&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;重试响应的 body 字段按原值选出，保持字段同一性。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_body_value&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;依据重试分类结果的控制分支由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0046&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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

块：block_008；执行主体：agent_runtime, tool；角色：source, sink。

IR 输入：0: archive.fetch, 1: result_001

IR 输出：0: result_010

<details><summary>顺序及必要先后约束</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
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
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| 位置 | 效果 | op | 实际输入数据 | 交互边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签数据操作 | deliver | 0: D014 | tool: archive.fetch | — |
| 1.2 | 无标签数据操作 | receive | 0: D014 | tool: archive.fetch | 0: D017 |
| 2.1 | model_observe（程序生成，静态可能） | deliver | 0: D017 | model_context: 当前模型处理上下文 | — |

入口／出口变化：

- `result: result_010`：未绑定 → D017

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出绑定本次获取的响应值。&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;运行时发起 archive.fetch 调用。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;由 archive.fetch 工具执行抓取。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;,
        &quot;value&quot;: &quot;tool&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;archive_fetch_response&quot;,
        &quot;reason&quot;: &quot;archive.fetch 的响应内容进入当前流程。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;,
        &quot;value&quot;: &quot;source&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument&quot;,
        &quot;reason&quot;: &quot;source_id 作为唯一实参送达 archive.fetch 边界。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
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
        &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
        &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
        &quot;ref_id&quot;: &quot;EM02&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
        &quot;reason&quot;: &quot;archive.fetch 部署方式未说明且无网络传输证据，响应按工具边界获取。&quot;,
        &quot;ref_id&quot;: &quot;EM09&quot;,
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
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument&quot;,
          &quot;reason&quot;: &quot;只将 source_id 作为唯一实参送达 archive.fetch 边界。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow&quot;,
          &quot;reason&quot;: &quot;源文禁止传递 FAST_KEY，deliver 输入仅保留 source_id。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
          &quot;reason&quot;: &quot;无网络传输证据，请求送达以工具边界 null-effect deliver 表示。&quot;,
          &quot;ref_id&quot;: &quot;EM13&quot;
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;loc_archive_fetch_tool&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_response&quot;,
          &quot;reason&quot;: &quot;该调用输出为 archive.fetch 响应，内容在工具边界被获取。&quot;,
          &quot;ref_id&quot;: &quot;g_0051&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
          &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序请求引用 source_id，形成唯一配对。&quot;,
          &quot;ref_id&quot;: &quot;EM15&quot;
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
          &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
          &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
          &quot;ref_id&quot;: &quot;EM02&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
          &quot;reason&quot;: &quot;archive.fetch 部署方式未说明且无网络传输证据，响应按工具边界获取。&quot;,
          &quot;ref_id&quot;: &quot;EM09&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容。&quot;,
        &quot;ref_id&quot;: &quot;g_0052&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
| 1.1 | model_observe（程序生成，静态可能） | deliver | 0: D017 | model_context: 当前模型处理上下文 | — |
| 2.1 | transform | compute | 0: D017 | — | 0: D011 |
| 2.2 | transform | select_part | 0: D017 | — | 0: D006 |
| 2.3 | transform | select_part | 0: D017 | — | 0: D018 |

入口／出口变化：

- `result: result_011`：未绑定 → D011
- `result: result_012`：未绑定 → D006
- `result: result_013`：未绑定 → D018

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;reason&quot;: &quot;输出语义名为 archive_fetch_outcome，绑定分类计算结果。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_outcome_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_body&quot;,
          &quot;reason&quot;: &quot;输出语义名为 archive_fetch_body，绑定选出的 body 原值。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_body_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive_fetch_error&quot;,
          &quot;reason&quot;: &quot;输出语义名为 archive_fetch_error，绑定选出的 error 值。&quot;,
          &quot;ref_id&quot;: &quot;g_0057&quot;
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_error_value&quot;
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
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;运行时对 archive.fetch 响应做成功/失败分类并提取对应值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;对响应分类并区分 body/error 输出，属内容处理。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;对响应分类与提取的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
        &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
        &quot;ref_id&quot;: &quot;EM10&quot;,
        &quot;value&quot;: &quot;model_observe&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 1,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;分类计算与字段选取属 transform；body 与 error 按原值选取。&quot;,
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
          &quot;quote&quot;: &quot;Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator or sink to roles; retain the independently evidenced action labels. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.&quot;,
          &quot;reason&quot;: &quot;程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。&quot;,
          &quot;ref_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
          &quot;reason&quot;: &quot;对响应分类与提取的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
          &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
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
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
          &quot;reason&quot;: &quot;需要把响应分类为成功或失败，属对响应的计算。&quot;,
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
      &quot;output&quot;: &quot;archive_fetch_outcome_value&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
          &quot;reason&quot;: &quot;成功响应的 body 字段按原值返回，用 select_part 保持字段同一性。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_body_value&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
          &quot;reason&quot;: &quot;失败时返回该响应的 error 部分；作为响应已有组成部分选取，未发明转换。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_error_value&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
        &quot;reason&quot;: &quot;依据 archive 分类结果的控制分支由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;g_0058&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;dispatch&quot;,
        &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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
| 1.1 | fs_write | write | 0: D009 | storage: status.txt | storage: status.txt: D016 → D004 (strong) |

入口／出口变化：

- `storage: status.txt`：D016 → D004

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43e3a41eabf729165e7c5a8be7eddb3344c3c09ee5baf1dcda3c5036aede61d9&quot;
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
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;状态内容写入本地存储位置，内容到达存储边界，符合 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;向本地文件追加内容属 fs_write；写入输入状态原值，未添加 transform。&quot;,
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
          &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;以追加模式把输入状态原值写入 status.txt；追加不同于替换，不读取旧内容。&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43e3a41eabf729165e7c5a8be7eddb3344c3c09ee5baf1dcda3c5036aede61d9&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_43e3a41eabf729165e7c5a8be7eddb3344c3c09ee5baf1dcda3c5036aede61d9&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回不引入、转换内容或使其到达接收/存储边界；源文未说明用户直接展示，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回不代表用户输出或网络送达，词汇表内无适用 effect；返回身份由 CFG 输入保留。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
| 1.1 | fs_write | write | 0: D013 | storage: status.txt | storage: status.txt: D016 → D005 (strong) |

入口／出口变化：

- `storage: status.txt`：D016 → D005

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_474dd77f7578c92e1d18a488ba3c1f120dde4ece7bf2ca5385dde04eba9726ed&quot;
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
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;追加写文件属 fs_write；写入原值。&quot;,
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
          &quot;reason&quot;: &quot;把重试结果状态以追加方式写入本地文件；写入原值。&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_474dd77f7578c92e1d18a488ba3c1f120dde4ece7bf2ca5385dde04eba9726ed&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_474dd77f7578c92e1d18a488ba3c1f120dde4ece7bf2ca5385dde04eba9726ed&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回未说明用户展示或外发，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回无词汇表内 effect；返回身份由 CFG 输入保留。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
| 1.1 | fs_write | write | 0: D011 | storage: status.txt | storage: status.txt: D016 → D001 (strong) |

入口／出口变化：

- `storage: status.txt`：D016 → D001

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_004dbc0bd0f1f3f291b588088db2724210b37ab7537b0944056832bbd2d95dfb&quot;
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
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;追加写文件属 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;把 archive.fetch 结果状态以追加方式写入本地文件；写入原值。&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_004dbc0bd0f1f3f291b588088db2724210b37ab7537b0944056832bbd2d95dfb&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_004dbc0bd0f1f3f291b588088db2724210b37ab7537b0944056832bbd2d95dfb&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回未说明用户展示或外发，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
        &quot;reason&quot;: &quot;普通返回无词汇表内 effect。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
| 1.1 | fs_write | write | 0: D011 | storage: status.txt | storage: status.txt: D016 → D020 (strong) |

入口／出口变化：

- `storage: status.txt`：D016 → D020

<details><summary>完整入口与出口</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f28017aeb9046907e2f7fcdd2438ab49359b0c36659bf78144489dc1f747f440&quot;
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
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;sink&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: 0,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;追加写文件属 fs_write。&quot;,
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
          &quot;reason&quot;: &quot;把 archive.fetch 结果状态以追加方式写入本地文件；写入原值。&quot;,
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f28017aeb9046907e2f7fcdd2438ab49359b0c36659bf78144489dc1f747f440&quot;
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
          &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f28017aeb9046907e2f7fcdd2438ab49359b0c36659bf78144489dc1f747f440&quot;
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
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;operator&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;失败路径的普通返回由运行时执行。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;roles&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;停止并返回错误属普通返回，未见用户直接展示或外发，无适用角色。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
        &quot;value&quot;: null
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;effect_index&quot;: null,
        &quot;field&quot;: &quot;effects&quot;,
        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
        &quot;reason&quot;: &quot;错误返回不产生词汇表内 effect；CFG 输入标识返回的错误值。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;,
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
| D001 | data_004dbc0bd0f1f3f291b588088db2724210b37ab7537b0944056832bbd2d95dfb | opaque |
| D002 | data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d | known_parts |
| D003 | data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9 | known_parts |
| D004 | data_43e3a41eabf729165e7c5a8be7eddb3344c3c09ee5baf1dcda3c5036aede61d9 | opaque |
| D005 | data_474dd77f7578c92e1d18a488ba3c1f120dde4ece7bf2ca5385dde04eba9726ed | opaque |
| D006 | data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e | opaque |
| D007 | data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379 | opaque |
| D008 | data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746 | known_parts |
| D009 | data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270 | opaque |
| D010 | data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9 | known_parts |
| D011 | data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba | opaque |
| D012 | data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a | opaque |
| D013 | data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6 | opaque |
| D014 | data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884 | opaque |
| D015 | data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67 | opaque |
| D016 | data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5 | opaque |
| D017 | data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234 | known_parts |
| D018 | data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929 | opaque |
| D019 | data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765 | opaque |
| D020 | data_f28017aeb9046907e2f7fcdd2438ab49359b0c36659bf78144489dc1f747f440 | opaque |

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
  &quot;id&quot;: &quot;data_004dbc0bd0f1f3f291b588088db2724210b37ab7537b0944056832bbd2d95dfb&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_023&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
      &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_011&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
      &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
        &quot;path&quot;: [
          &quot;source_id&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;,
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
  &quot;id&quot;: &quot;data_43e3a41eabf729165e7c5a8be7eddb3344c3c09ee5baf1dcda3c5036aede61d9&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_019&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
      &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;
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
  &quot;id&quot;: &quot;data_474dd77f7578c92e1d18a488ba3c1f120dde4ece7bf2ca5385dde04eba9726ed&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_021&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
      &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;
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
  &quot;id&quot;: &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
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
  &quot;id&quot;: &quot;data_57eed2f8ed0ec66e37e3b8d44b3e8e47487e31ba4915b627c18d89fa50037379&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
      &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
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
  &quot;id&quot;: &quot;data_5c0d244c89a5becb6d09b581613bf4b0342098206998f55f96fd2c0c9763c270&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;
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
        &quot;data&quot;: &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;,
        &quot;path&quot;: [
          &quot;FAST_KEY&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;,
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
  &quot;id&quot;: &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;
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
  &quot;id&quot;: &quot;data_78cd588086dbf4357b328aa11991bf099bf2a9c49efb99e4e679715cc051536a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;
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
  &quot;id&quot;: &quot;data_9247d7949d84faea7faed9f934d5e1712473f780870e0a52b37f280052b152d6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_013&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_0870b3045aa00f2d717dd4a594aff9b78329ab3638bd8e9f25b43db505b28e7d&quot;
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
  &quot;id&quot;: &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_1dabfaf49cf4e220c1f399bbfd8c854a4221d919653a55e0f1c75f3534bc20e9&quot;,
    &quot;path&quot;: [
      &quot;source_id&quot;
    ]
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
  &quot;id&quot;: &quot;data_9edb4ba96e784ab4f0476f092243da3c23c7caf6c9972111dfe0800c64c2ce67&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_5852fdeb812a866a87982a50ed2b41df41f9120a77b2b42388d6267891bd3746&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
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
  &quot;id&quot;: &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
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
        &quot;data&quot;: &quot;data_4811521434feae899bfaedecd1c80bf46119cede43e74c8b99758e54cbd8119e&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;,
        &quot;path&quot;: [
          &quot;error&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:archive.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_015&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_961fd44e4b0945471a2de2004e8c91fbfec15cf2b94381c397567d66cc62d884&quot;
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
  &quot;id&quot;: &quot;data_bec066f955f3f7b537e0c1a01bfaca96c6a3415407e6f5f053d45d9302cdf929&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_b02055374db2a6e88eb59d6fe51b48f4b99944e3c55aef40725c9abc5c4b1234&quot;,
    &quot;path&quot;: [
      &quot;error&quot;
    ]
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
  &quot;id&quot;: &quot;data_ee8bd15d4e256aeb18bee426e237c4a90742ba5cdce1a57b3803ae680bce7765&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_6abc5e89a301d00c512248e663a322d0887829907156e711756b6e9124a82ce9&quot;,
    &quot;path&quot;: [
      &quot;FAST_KEY&quot;
    ]
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
  &quot;id&quot;: &quot;data_f28017aeb9046907e2f7fcdd2438ab49359b0c36659bf78144489dc1f747f440&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_025&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ab86567f04aa6b66a691f6c0d8fbade1a5bef5aab51bac8bc420cde445aa08d5&quot;,
      &quot;data_6b12861d70a067fcc9b6b657d105f9938ecd9280bb984cc667c7a1fe11b8d7ba&quot;
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
    &quot;loc_archive_fetch_tool&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;archive.fetch&quot;,
        &quot;reason&quot;: &quot;指令以 archive.fetch 为 external_resource，构成工具边界身份。&quot;,
        &quot;ref_id&quot;: &quot;g_0051&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
        &quot;reason&quot;: &quot;源文要求调用 archive.fetch 执行抓取。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility&quot;,
        &quot;reason&quot;: &quot;未说明部署方式，保守保留外部接收方可能。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
        &quot;reason&quot;: &quot;无网络机制证据，位置种类为 tool 而非 remote。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;
      }
    ],
    &quot;loc_environment&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;environment&quot;,
        &quot;reason&quot;: &quot;该指令的 context_key 标识为 environment，环境是运行时上下文容器。&quot;,
        &quot;ref_id&quot;: &quot;g_0015&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
        &quot;reason&quot;: &quot;源文从环境读取变量，确认该上下文来源。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Runtime context defaults to task access and task retention&quot;,
        &quot;reason&quot;: &quot;运行时上下文默认 task 访问与 task 保留。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_fast_fetch_tool&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;指令以 fast.fetch 为 external_resource，构成工具边界身份。&quot;,
        &quot;ref_id&quot;: &quot;g_0027&quot;
      },
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;fast.fetch&quot;,
        &quot;reason&quot;: &quot;重试指令同样引用该 fast.fetch 工具边界。&quot;,
        &quot;ref_id&quot;: &quot;g_0039&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
        &quot;reason&quot;: &quot;源文指定该工具承担抓取动作。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility&quot;,
        &quot;reason&quot;: &quot;未说明部署方式，保守保留外部接收方可能，采用 recipient 访问。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
        &quot;reason&quot;: &quot;无网络机制证据，位置种类为 tool 而非 remote。&quot;,
        &quot;ref_id&quot;: &quot;EM06&quot;
      }
    ],
    &quot;loc_status_file&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;status.txt&quot;,
        &quot;reason&quot;: &quot;external_resource 标识本地状态文件。&quot;,
        &quot;ref_id&quot;: &quot;g_0063&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
        &quot;reason&quot;: &quot;源文规定向本地 status.txt 追加状态。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
        &quot;reason&quot;: &quot;文件默认 task 访问与 persistent 保留；未见临时使用与清理机制。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;loc_user_request&quot;: [
      {
        &quot;basis&quot;: &quot;cfg&quot;,
        &quot;quote&quot;: &quot;user_request&quot;,
        &quot;reason&quot;: &quot;该指令的 context_key 标识为 user_request，用户请求是运行时上下文容器。&quot;,
        &quot;ref_id&quot;: &quot;g_0009&quot;
      },
      {
        &quot;basis&quot;: &quot;source&quot;,
        &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
        &quot;reason&quot;: &quot;源文从用户请求读取内容，确认该上下文来源。&quot;,
        &quot;ref_id&quot;: &quot;src_003&quot;
      },
      {
        &quot;basis&quot;: &quot;execution_model&quot;,
        &quot;quote&quot;: &quot;Runtime context defaults to task access and task retention&quot;,
        &quot;reason&quot;: &quot;运行时上下文默认 task 访问与 task 保留，未见跨任务共享证据。&quot;,
        &quot;ref_id&quot;: &quot;EM12&quot;
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
    &quot;compiled_sha256&quot;: &quot;75baefbdcdca5cbe2bb2daf704516256f4a29923484d1f57e39f271a78e53adc&quot;,
    &quot;mapping_sha256&quot;: &quot;cb01fcb6ff3f3ccddc63460a7493b21397c619be9f2022416c105794d6ac0cf9&quot;,
    &quot;raw_sha256&quot;: &quot;df78ddd79227682adbf7745acdd8e769e53d13a6a09362daa5af739bddab0031&quot;,
    &quot;sink_boundaries_sha256&quot;: &quot;2d1a840f1c123e9fdc69a7e5c6b3aa93d447f8f381616d85f953dd1cda4b4eb2&quot;,
    &quot;version&quot;: &quot;skillflow-processing-compiler-v4&quot;
  },
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;75baefbdcdca5cbe2bb2daf704516256f4a29923484d1f57e39f271a78e53adc&quot;,
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
          2
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
          1,
          2
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
          2
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
          1,
          2
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
          2
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
          1,
          2
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
      &quot;sha256&quot;: &quot;d88526a10df7dcc14e82547ae50b7d9f9b3f83c802f348267296f13929394f4a&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v5&quot;
    },
    &quot;raw_sha256&quot;: &quot;df78ddd79227682adbf7745acdd8e769e53d13a6a09362daa5af739bddab0031&quot;,
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v4&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;location_evidences&quot;: {
      &quot;loc_archive_fetch_tool&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;archive.fetch&quot;,
          &quot;reason&quot;: &quot;指令以 archive.fetch 为 external_resource，构成工具边界身份。&quot;,
          &quot;ref_id&quot;: &quot;g_0051&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
          &quot;reason&quot;: &quot;源文要求调用 archive.fetch 执行抓取。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility&quot;,
          &quot;reason&quot;: &quot;未说明部署方式，保守保留外部接收方可能。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
          &quot;reason&quot;: &quot;无网络机制证据，位置种类为 tool 而非 remote。&quot;,
          &quot;ref_id&quot;: &quot;EM06&quot;
        }
      ],
      &quot;loc_environment&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;environment&quot;,
          &quot;reason&quot;: &quot;该指令的 context_key 标识为 environment，环境是运行时上下文容器。&quot;,
          &quot;ref_id&quot;: &quot;g_0015&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
          &quot;reason&quot;: &quot;源文从环境读取变量，确认该上下文来源。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Runtime context defaults to task access and task retention&quot;,
          &quot;reason&quot;: &quot;运行时上下文默认 task 访问与 task 保留。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_fast_fetch_tool&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast.fetch&quot;,
          &quot;reason&quot;: &quot;指令以 fast.fetch 为 external_resource，构成工具边界身份。&quot;,
          &quot;ref_id&quot;: &quot;g_0027&quot;
        },
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;fast.fetch&quot;,
          &quot;reason&quot;: &quot;重试指令同样引用该 fast.fetch 工具边界。&quot;,
          &quot;ref_id&quot;: &quot;g_0039&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
          &quot;reason&quot;: &quot;源文指定该工具承担抓取动作。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Unspecified tool deployment conservatively retains an external recipient possibility&quot;,
          &quot;reason&quot;: &quot;未说明部署方式，保守保留外部接收方可能，采用 recipient 访问。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
          &quot;reason&quot;: &quot;无网络机制证据，位置种类为 tool 而非 remote。&quot;,
          &quot;ref_id&quot;: &quot;EM06&quot;
        }
      ],
      &quot;loc_status_file&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;status.txt&quot;,
          &quot;reason&quot;: &quot;external_resource 标识本地状态文件。&quot;,
          &quot;ref_id&quot;: &quot;g_0063&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
          &quot;reason&quot;: &quot;源文规定向本地 status.txt 追加状态。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Files default to task access and persistent retention&quot;,
          &quot;reason&quot;: &quot;文件默认 task 访问与 persistent 保留；未见临时使用与清理机制。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ],
      &quot;loc_user_request&quot;: [
        {
          &quot;basis&quot;: &quot;cfg&quot;,
          &quot;quote&quot;: &quot;user_request&quot;,
          &quot;reason&quot;: &quot;该指令的 context_key 标识为 user_request，用户请求是运行时上下文容器。&quot;,
          &quot;ref_id&quot;: &quot;g_0009&quot;
        },
        {
          &quot;basis&quot;: &quot;source&quot;,
          &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
          &quot;reason&quot;: &quot;源文从用户请求读取内容，确认该上下文来源。&quot;,
          &quot;ref_id&quot;: &quot;src_003&quot;
        },
        {
          &quot;basis&quot;: &quot;execution_model&quot;,
          &quot;quote&quot;: &quot;Runtime context defaults to task access and task retention&quot;,
          &quot;reason&quot;: &quot;运行时上下文默认 task 访问与 task 保留，未见跨任务共享证据。&quot;,
          &quot;ref_id&quot;: &quot;EM12&quot;
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;loc_archive_fetch_tool&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;archive.fetch&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_015&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      },
      &quot;loc_environment&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;environment&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_003&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
      },
      &quot;loc_fast_fetch_tool&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
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
        ],
        &quot;retention&quot;: null
      },
      &quot;loc_status_file&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
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
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;loc_user_request&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;user_request&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
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
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
            &quot;reason&quot;: &quot;该读取是 Skill 工作流中的运行时动作，由本地 agent 运行时执行；源文未提及模型或人工参与。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
            &quot;reason&quot;: &quot;该操作从用户请求引入 source_id 内容进入当前流程，符合 source 角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
            &quot;reason&quot;: &quot;从用户请求这一运行时上下文获取调用方输入，属于 context_read。&quot;,
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
            &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0010&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;词汇表内无适用 effect；该指令只改变控制流，不产生内容效应。&quot;,
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
            &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
            &quot;reason&quot;: &quot;环境读取由工作流运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
            &quot;reason&quot;: &quot;从环境上下文引入 FAST_KEY 值进入当前流程。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;read FAST_KEY from the environment&quot;,
            &quot;reason&quot;: &quot;读取环境上下文属于 context_read。&quot;,
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
            &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0016&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;词汇表内无适用 effect；该指令只改变控制流。&quot;,
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
            &quot;reason&quot;: &quot;存在性检查由运行时在工作流中执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
            &quot;reason&quot;: &quot;对 FAST_KEY 值做存在性判定并产生新的布尔状态，属于对内容的处理。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
            &quot;reason&quot;: &quot;计算存在性布尔是对输入值的计算，属 transform。&quot;,
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
            &quot;reason&quot;: &quot;依据存在性标志的控制分支由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0022&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
            &quot;reason&quot;: &quot;运行时发起 fast.fetch 调用并传递实际参数。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;fast.fetch&quot;,
            &quot;reason&quot;: &quot;指令以 fast.fetch 为外部资源，由该工具执行抓取动作。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
            &quot;reason&quot;: &quot;该调用返回的响应内容进入当前流程，符合 source 角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;try fast.fetch first with source_id and FAST_KEY&quot;,
            &quot;reason&quot;: &quot;source_id 与 FAST_KEY 作为参数被送达 fast.fetch 边界，内容可能到达外部接收方。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
            &quot;reason&quot;: &quot;工具名不证明网络传输且无通信机制证据，不声明 net_send/net_receive；请求送达与响应获取在工具边界以 null-effect 事件表达。&quot;,
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
            &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0028&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;对首次响应做结果分类由运行时执行，用于区分成功、瞬时失败与非瞬时失败。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;对响应内容分类并选出 body 字段，属于对内容的处理。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;分类响应结果的计算属 transform。&quot;,
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
            &quot;reason&quot;: &quot;依据分类结果的控制分支由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0034&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;运行时按约束发起一次重试调用并传递参数。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;fast.fetch&quot;,
            &quot;reason&quot;: &quot;重试由 fast.fetch 工具执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0039&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
            &quot;reason&quot;: &quot;重试响应内容进入当前流程。&quot;,
            &quot;ref_id&quot;: &quot;g_0039&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;重试仍以 source_id 与 FAST_KEY 为参数送达 fast.fetch 边界。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
            &quot;reason&quot;: &quot;无网络传输机制证据，不声明 net_send/net_receive；送达与获取在工具边界以 null-effect 事件表达。&quot;,
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
            &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0040&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容。&quot;,
            &quot;ref_id&quot;: &quot;g_0040&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
            &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
            &quot;reason&quot;: &quot;对重试响应分类由运行时执行，用于判断成功或转入 archive.fetch 路径。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;对重试响应分类并选出 body 字段，属内容处理。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
            &quot;reason&quot;: &quot;识别重试结果为瞬时或非瞬时需要计算响应输入，属 transform。&quot;,
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
            &quot;reason&quot;: &quot;依据重试分类结果的控制分支由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0046&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0046&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;call archive.fetch with source_id&quot;,
            &quot;reason&quot;: &quot;运行时发起 archive.fetch 调用。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;archive.fetch&quot;,
            &quot;reason&quot;: &quot;由 archive.fetch 工具执行抓取。&quot;,
            &quot;ref_id&quot;: &quot;g_0051&quot;,
            &quot;value&quot;: &quot;tool&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;archive_fetch_response&quot;,
            &quot;reason&quot;: &quot;archive.fetch 的响应内容进入当前流程。&quot;,
            &quot;ref_id&quot;: &quot;g_0051&quot;,
            &quot;value&quot;: &quot;source&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument&quot;,
            &quot;reason&quot;: &quot;source_id 作为唯一实参送达 archive.fetch 边界。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;tool names and LLM participation do not prove network communication&quot;,
            &quot;reason&quot;: &quot;无网络传输机制证据，不声明 net_send/net_receive；送达与获取在工具边界以 null-effect 事件表达。&quot;,
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
            &quot;reason&quot;: &quot;控制跳转指令由 agent 运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0052&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制跳转不引入、转换或送达内容。&quot;,
            &quot;ref_id&quot;: &quot;g_0052&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;词汇表内无适用 effect。&quot;,
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
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;运行时对 archive.fetch 响应做成功/失败分类并提取对应值。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;对响应分类并区分 body/error 输出，属内容处理。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;transformer&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;分类计算与字段选取属 transform；body 与 error 按原值选取。&quot;,
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
            &quot;reason&quot;: &quot;依据 archive 分类结果的控制分支由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;g_0058&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;分支跳转不改变内容，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;g_0058&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;dispatch&quot;,
            &quot;reason&quot;: &quot;纯控制分支无词汇表内 effect。&quot;,
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
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;状态内容写入本地存储位置，内容到达存储边界，符合 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;向本地文件追加内容属 fs_write；写入输入状态原值，未添加 transform。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回不引入、转换内容或使其到达接收/存储边界；源文未说明用户直接展示，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回不代表用户输出或网络送达，词汇表内无适用 effect；返回身份由 CFG 输入保留。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
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
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;追加写文件属 fs_write；写入原值。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回未说明用户展示或外发，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回无词汇表内 effect；返回身份由 CFG 输入保留。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
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
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;追加写文件属 fs_write。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回未说明用户展示或外发，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
            &quot;reason&quot;: &quot;普通返回无词汇表内 effect。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
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
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;本地文件追加由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;状态内容写入本地存储位置，符合 sink。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;sink&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: 0,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
            &quot;reason&quot;: &quot;追加写文件属 fs_write。&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;operator&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;失败路径的普通返回由运行时执行。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;roles&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;停止并返回错误属普通返回，未见用户直接展示或外发，无适用角色。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;value&quot;: null
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;effect_index&quot;: null,
            &quot;field&quot;: &quot;effects&quot;,
            &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
            &quot;reason&quot;: &quot;错误返回不产生词汇表内 effect；CFG 输入标识返回的错误值。&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
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
                        &quot;reason&quot;: &quot;从用户请求上下文容器获取内容，是 context_read 的实际读取操作。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;a natural-language request for a field from a container does not establish a key-only read mechanism&quot;,
                        &quot;reason&quot;: &quot;仅需一个字段不构成键限读取机制，读取输出保留请求整体作为可能范围。&quot;,
                        &quot;ref_id&quot;: &quot;EM01&quot;
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
                        &quot;reason&quot;: &quot;目标字段是既有的 source_id，按字段原值选出，不发明新值。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;user_request_content&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;source_id_value&quot;,
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
                &quot;quote&quot;: &quot;Read source_id from the user&#x27;s request&quot;,
                &quot;reason&quot;: &quot;源文只描述从用户请求读取 source_id，未规定模型处理或显式本地隔离与限定回传，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
                &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留请求整体作为可能获取范围。&quot;,
                &quot;ref_id&quot;: &quot;EM01&quot;
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
                &quot;reason&quot;: &quot;该指令输出语义名为 source_id，绑定刚选出的字段原值。&quot;,
                &quot;ref_id&quot;: &quot;g_0009&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;source_id_value&quot;
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
                        &quot;reason&quot;: &quot;从环境上下文容器获取内容，是 context_read 的实际读取操作。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;a natural-language request for a field from a container does not establish a key-only read mechanism&quot;,
                        &quot;reason&quot;: &quot;命名一个变量不构成键限读取机制，读取输出保留环境整体作为可能范围。&quot;,
                        &quot;ref_id&quot;: &quot;EM01&quot;
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
                        &quot;reason&quot;: &quot;目标值是环境中的 FAST_KEY，按原值选出。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;environment_content&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_key_value&quot;,
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
                &quot;reason&quot;: &quot;源文只描述从环境读取 FAST_KEY，未规定模型处理或本地隔离与限定回传，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
                &quot;reason&quot;: &quot;无显式接口限制读取或返回范围，保留环境上下文整体作为可能获取范围。&quot;,
                &quot;ref_id&quot;: &quot;EM01&quot;
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
                &quot;reason&quot;: &quot;输出语义名为 fast_key，绑定选出的环境值。&quot;,
                &quot;ref_id&quot;: &quot;g_0015&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key_value&quot;
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
                        &quot;reason&quot;: &quot;对 FAST_KEY 值计算存在性布尔，结果派生依赖该输入。&quot;,
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
                    &quot;output&quot;: &quot;fast_key_present_value&quot;
                  }
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;If FAST_KEY is present&quot;,
                &quot;reason&quot;: &quot;存在性判定没有模型处理或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留非隔离转换输入的可能观察。&quot;,
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
                &quot;quote&quot;: &quot;fast_key_present&quot;,
                &quot;reason&quot;: &quot;输出语义名为 fast_key_present，绑定计算所得的存在性布尔值。&quot;,
                &quot;ref_id&quot;: &quot;g_0021&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key_present_value&quot;
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
                        &quot;reason&quot;: &quot;把 source_id 与 FAST_KEY 按输入顺序作为实际参数送达 fast.fetch 边界。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                        &quot;reason&quot;: &quot;无网络传输证据，请求送达以工具边界 null-effect deliver 表示，不声明 net_send。&quot;,
                        &quot;ref_id&quot;: &quot;EM13&quot;
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
                    &quot;target&quot;: &quot;loc_fast_fetch_tool&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;fast_fetch_first_response&quot;,
                        &quot;reason&quot;: &quot;该调用输出为 fast.fetch 响应，响应内容在工具边界被获取。&quot;,
                        &quot;ref_id&quot;: &quot;g_0027&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
                        &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序参数引用，形成唯一配对，获取跟随送达之后。&quot;,
                        &quot;ref_id&quot;: &quot;EM15&quot;
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
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
                &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求；未见隔离或限定路由机制，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;EM02&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
                &quot;reason&quot;: &quot;fast.fetch 是已知工具但无网络传输机制证据，响应按工具边界获取。&quot;,
                &quot;ref_id&quot;: &quot;EM09&quot;
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
                &quot;reason&quot;: &quot;输出绑定本次获取的响应值。&quot;,
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
                        &quot;quote&quot;: &quot;Retry fast.fetch exactly once only when its first attempt fails with a transient error&quot;,
                        &quot;reason&quot;: &quot;分类需要区分成功、瞬时失败与非瞬时失败，属对响应输入的计算。&quot;,
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
                    &quot;output&quot;: &quot;fast_fetch_first_outcome_value&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;源文明确 body 字段按原值返回，用 select_part 保持字段同一性，而非不透明计算。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_body_value&quot;,
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
                &quot;reason&quot;: &quot;对首次响应分类的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式；默认模式保留响应版本的可能观察。&quot;,
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
                &quot;quote&quot;: &quot;fast_fetch_first_outcome&quot;,
                &quot;reason&quot;: &quot;输出语义名为 fast_fetch_first_outcome，绑定分类计算结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0033&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_outcome_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;fast_fetch_first_body&quot;,
                &quot;reason&quot;: &quot;输出语义名为 fast_fetch_first_body，绑定选出的 body 字段原值。&quot;,
                &quot;ref_id&quot;: &quot;g_0033&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_body_value&quot;
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
                        &quot;reason&quot;: &quot;重试仍调用 fast.fetch，并以 source_id 与 FAST_KEY 作为参数送达同一工具边界。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                        &quot;reason&quot;: &quot;无网络传输证据，重试请求送达以工具边界 null-effect deliver 表示。&quot;,
                        &quot;ref_id&quot;: &quot;EM13&quot;
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
                    &quot;target&quot;: &quot;loc_fast_fetch_tool&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;fast_fetch_retry_response&quot;,
                        &quot;reason&quot;: &quot;该调用输出为重试响应，内容在工具边界被获取。&quot;,
                        &quot;ref_id&quot;: &quot;g_0039&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
                        &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序参数引用，形成唯一配对。&quot;,
                        &quot;ref_id&quot;: &quot;EM15&quot;
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
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
                &quot;reason&quot;: &quot;重试返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
                &quot;ref_id&quot;: &quot;EM02&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
                &quot;reason&quot;: &quot;fast.fetch 为已知工具但无网络传输机制证据，重试响应按工具边界获取。&quot;,
                &quot;ref_id&quot;: &quot;EM09&quot;
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
                &quot;reason&quot;: &quot;输出绑定本次重试获取的响应值。&quot;,
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
                        &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
                        &quot;reason&quot;: &quot;分类重试响应的成功/失败结果，依赖响应输入。&quot;,
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
                    &quot;output&quot;: &quot;fast_fetch_retry_outcome_value&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;重试响应的 body 字段按原值选出，保持字段同一性。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_body_value&quot;,
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
                &quot;quote&quot;: &quot;After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id&quot;,
                &quot;reason&quot;: &quot;对重试响应分类的处理无模型或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
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
                &quot;quote&quot;: &quot;fast_fetch_retry_outcome&quot;,
                &quot;reason&quot;: &quot;输出语义名为 fast_fetch_retry_outcome，绑定分类结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0045&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_outcome_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;fast_fetch_retry_body&quot;,
                &quot;reason&quot;: &quot;输出语义名为 fast_fetch_retry_body，绑定选出的 body 原值。&quot;,
                &quot;ref_id&quot;: &quot;g_0045&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_body_value&quot;
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
                        &quot;quote&quot;: &quot;Call archive.fetch at most once and pass source_id as its only argument&quot;,
                        &quot;reason&quot;: &quot;只将 source_id 作为唯一实参送达 archive.fetch 边界。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow&quot;,
                        &quot;reason&quot;: &quot;源文禁止传递 FAST_KEY，deliver 输入仅保留 source_id。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                        &quot;reason&quot;: &quot;无网络传输证据，请求送达以工具边界 null-effect deliver 表示。&quot;,
                        &quot;ref_id&quot;: &quot;EM13&quot;
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;loc_archive_fetch_tool&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;cfg&quot;,
                        &quot;quote&quot;: &quot;archive_fetch_response&quot;,
                        &quot;reason&quot;: &quot;该调用输出为 archive.fetch 响应，内容在工具边界被获取。&quot;,
                        &quot;ref_id&quot;: &quot;g_0051&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;quote&quot;: &quot;define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs&quot;,
                        &quot;reason&quot;: &quot;deliver 与 receive 使用同一有序请求引用 source_id，形成唯一配对。&quot;,
                        &quot;ref_id&quot;: &quot;EM15&quot;
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
                ],
                &quot;effect_index&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it&quot;,
                &quot;reason&quot;: &quot;工具返回内容默认可能进入后续模型请求，未见隔离或限定路由机制。&quot;,
                &quot;ref_id&quot;: &quot;EM02&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event&quot;,
                &quot;reason&quot;: &quot;archive.fetch 部署方式未说明且无网络传输证据，响应按工具边界获取。&quot;,
                &quot;ref_id&quot;: &quot;EM09&quot;
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
                &quot;reason&quot;: &quot;输出绑定本次获取的响应值。&quot;,
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
                        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
                        &quot;reason&quot;: &quot;需要把响应分类为成功或失败，属对响应的计算。&quot;,
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
                    &quot;output&quot;: &quot;archive_fetch_outcome_value&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;return that successful response&#x27;s body value unchanged&quot;,
                        &quot;reason&quot;: &quot;成功响应的 body 字段按原值返回，用 select_part 保持字段同一性。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_body_value&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
                        &quot;reason&quot;: &quot;失败时返回该响应的 error 部分；作为响应已有组成部分选取，未发明转换。&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_error_value&quot;,
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
                &quot;quote&quot;: &quot;If archive.fetch fails, stop and return its error&quot;,
                &quot;reason&quot;: &quot;对响应分类与提取的处理没有模型或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据，不能声明 local 模式。&quot;,
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
                &quot;quote&quot;: &quot;archive_fetch_outcome&quot;,
                &quot;reason&quot;: &quot;输出语义名为 archive_fetch_outcome，绑定分类计算结果。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_outcome_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;archive_fetch_body&quot;,
                &quot;reason&quot;: &quot;输出语义名为 archive_fetch_body，绑定选出的 body 原值。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_body_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;quote&quot;: &quot;archive_fetch_error&quot;,
                &quot;reason&quot;: &quot;输出语义名为 archive_fetch_error，绑定选出的 error 值。&quot;,
                &quot;ref_id&quot;: &quot;g_0057&quot;
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_error_value&quot;
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
                        &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
                        &quot;reason&quot;: &quot;以追加模式把输入状态原值写入 status.txt；追加不同于替换，不读取旧内容。&quot;,
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
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
                &quot;reason&quot;: &quot;文件追加没有模型处理或本地隔离与限定回传证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据；写入内容按不变值处理，未添加 transform。&quot;,
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
                        &quot;reason&quot;: &quot;把重试结果状态以追加方式写入本地文件；写入原值。&quot;,
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
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
                &quot;reason&quot;: &quot;文件追加没有模型处理或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据。&quot;,
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
                        &quot;reason&quot;: &quot;把 archive.fetch 结果状态以追加方式写入本地文件；写入原值。&quot;,
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
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
                &quot;reason&quot;: &quot;文件追加没有模型处理或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据。&quot;,
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
                        &quot;reason&quot;: &quot;把 archive.fetch 结果状态以追加方式写入本地文件；写入原值。&quot;,
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
                ],
                &quot;effect_index&quot;: 0
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;quote&quot;: &quot;Before returning from every success or failure path, append the final status to local status.txt&quot;,
                &quot;reason&quot;: &quot;失败路径的文件追加没有模型处理或本地隔离证据，按默认模式标注。&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;quote&quot;: &quot;Local mode requires explicit source or code/interface evidence and an explicit returns list&quot;,
                &quot;reason&quot;: &quot;缺少本地隔离机制证据。&quot;,
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
      &quot;ir_026&quot;: {
        &quot;events&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: []
      }
    }
  }
}</pre>

</details>

