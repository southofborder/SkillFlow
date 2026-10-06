# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir007\_missing\_receive · 问题

源文要求调用 index\.search 一次，其响应随后被用于写出 total 并返回 items（src\_008）；CFG 把该调用的输出命名为 “index\.search response”（g\_0023），EM09 要求对这种已知工具内容获取保留获取边界，并以 tool 位置的 receive（null\-effect 事件）表示返回内容。annotation 在 ir\_007 的 profile 证据（ann\_0046）中声称已按 EM09 用 tool 位置的 receive 表达该获取，但其 transfer\_specs 的处理事件（ann\_0161）里唯一原子操作（ann\_0163）是以输入 1、2、4 为 possible 依赖、输出 search\_response 的 compute，没有任何 receive 操作。compute 可以记录请求参数的可能依赖，但不能替代获取来源；该表示把响应写成请求输入的计算结果，丢失了 EM09 要求在表示中保留的获取边界（编译器据此生成的 obs\_0005 也只把请求参数列为该段模型可见值，获取版本未以 receive 输出形式出现）。

定位：ann\_0046、ann\_0161、ann\_0163

修改建议：建议按 EM09 在 ir\_007 的 null\-effect 处理事件中补记对 loc\_index\_search 的 receive 操作（输出获取到的响应版本 search\_response），并把 term/from\_date/limit 保留为该调用的实际输入与可能依赖，使获取边界不再由请求输入的依赖关系替代。

- source / src\_008：Call index\.search exactly once, using request\.term unchanged as its query argument\.
- cfg / g\_0023：index\.search response
- execution\_model / EM09：returned tool or collection content has an acquisition boundary not exhausted by query inputs
- execution\_model / EM09：known tool acquisition without established networking uses receive at a tool location in a null\-effect event

## f\_ir012\_missing\_return\_forwarding · 问题

源文要求把检索响应的 items 原样返回调用方（src\_014），CFG 中 ir\_012 的输入即 response\_items（g\_0032）；这是工作流出口处的值转发关系，按 EM06 交付应保留实际取值与结果身份。annotation 在 ir\_012 的 profile 证据（ann\_0071）中声称“其未变更的值转发关系在 transfer\_specs 中按输入操作数保留”，但 transfer\_specs\.ir\_012 的 events（ann\_0226）实际为空，没有任何引用输入操作数（response\_items）的转发操作。具体差异是：源文要求的返回转发关系在表示中并不存在，而证据声称已保留；受影响的数据关系是该 IR 的返回/交付边界——items 以未变更身份交回调用方这一关系无法从注释的 transfer\_specs 中读出。

定位：ann\_0071、ann\_0226

修改建议：建议在 ir\_012 的 transfer\_specs 中补记 response\_items 原样返回调用方的转发操作（保持未变更的取值与身份），使该返回转发关系与 src\_014 的要求及证据中“已在 transfer\_specs 中保留”的声称一致。

- source / src\_014：Return the search response's items value unchanged\.
- cfg / g\_0032：response\_items
- execution\_model / EM06：delivery must retain actual selected values, input order, result identities, and explicit prohibitions

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012

原始调用：[call.json](calls/review/a001/call.json)；定位与材料：[material.json](inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir007_missing_receive",
    "target_ids": [
      "ann_0046",
      "ann_0161",
      "ann_0163"
    ],
    "status": "issue",
    "explanation": "源文要求调用 index.search 一次，其响应随后被用于写出 total 并返回 items（src_008）；CFG 把该调用的输出命名为 “index.search response”（g_0023），EM09 要求对这种已知工具内容获取保留获取边界，并以 tool 位置的 receive（null-effect 事件）表示返回内容。annotation 在 ir_007 的 profile 证据（ann_0046）中声称已按 EM09 用 tool 位置的 receive 表达该获取，但其 transfer_specs 的处理事件（ann_0161）里唯一原子操作（ann_0163）是以输入 1、2、4 为 possible 依赖、输出 search_response 的 compute，没有任何 receive 操作。compute 可以记录请求参数的可能依赖，但不能替代获取来源；该表示把响应写成请求输入的计算结果，丢失了 EM09 要求在表示中保留的获取边界（编译器据此生成的 obs_0005 也只把请求参数列为该段模型可见值，获取版本未以 receive 输出形式出现）。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_008",
        "quote": "Call index.search exactly once, using request.term unchanged as its query argument."
      },
      {
        "basis": "cfg",
        "ref_id": "g_0023",
        "quote": "index.search response"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM09",
        "quote": "returned tool or collection content has an acquisition boundary not exhausted by query inputs"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM09",
        "quote": "known tool acquisition without established networking uses receive at a tool location in a null-effect event"
      }
    ],
    "suggestion": "建议按 EM09 在 ir_007 的 null-effect 处理事件中补记对 loc_index_search 的 receive 操作（输出获取到的响应版本 search_response），并把 term/from_date/limit 保留为该调用的实际输入与可能依赖，使获取边界不再由请求输入的依赖关系替代。",
    "targets": [
      {
        "id": "ann_0046",
        "kind": "annotation",
        "pointer": "/profiles/ir_007/evidences",
        "instruction_ids": [
          "ir_007"
        ],
        "value": [
          {
            "field": "operator",
            "value": "agent_runtime",
            "basis": "source",
            "ref_id": "src_008",
            "quote": "Call index.search exactly once",
            "reason": "工作流由本地 agent runtime 执行，并据此发起这次调用。",
            "effect_index": null
          },
          {
            "field": "operator",
            "value": "tool",
            "basis": "cfg",
            "ref_id": "g_0023",
            "quote": "index.search",
            "reason": "CFG 把 index.search 作为被调用的外部资源，实际执行检索的工具参与该动作。",
            "effect_index": null
          },
          {
            "field": "roles",
            "value": "source",
            "basis": "cfg",
            "ref_id": "g_0023",
            "quote": "index.search response",
            "reason": "该调用把检索响应作为新内容引入当前流程，充当 source。",
            "effect_index": null
          },
          {
            "field": "roles",
            "value": "sink",
            "basis": "source",
            "ref_id": "src_008",
            "quote": "using request.term unchanged as its query argument",
            "reason": "请求参数被交给 index.search 这一接收边界，内容到达接收方，充当 sink。",
            "effect_index": null
          },
          {
            "field": "effects",
            "value": null,
            "basis": "execution_model",
            "ref_id": "EM09",
            "quote": "known tool acquisition without established networking uses receive at a tool location in a null-effect event",
            "reason": "源文与 CFG 只给出工具调用与取值关系，没有网络地址、协议或远程传输证据，工具名本身不证明网络通信，故不标注 net_send/net_receive；该调用是已知的工具内容获取，按 EM09 用 tool 位置的 receive 在 null-effect 事件中表达。",
            "effect_index": null
          }
        ]
      },
      {
        "id": "ann_0161",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_007/events/0",
        "instruction_ids": [
          "ir_007"
        ],
        "value": {
          "kind": "processing",
          "mode": "default",
          "events": [
            {
              "effect_index": null,
              "atomic_ops": [
                {
                  "evidences": [
                    {
                      "basis": "source",
                      "ref_id": "src_008",
                      "quote": "using request.term unchanged as its query argument",
                      "reason": "响应随查询参数变化，保留正文对原始查询和可选参数的可能依赖。"
                    },
                    {
                      "basis": "source",
                      "ref_id": "src_009",
                      "quote": "When limit is present, pass its value unchanged as the limit argument.",
                      "reason": "limit 值在存在时原样作为参数传入，因此作为该请求的参数依赖记录；能力说明不请求模糊扩展，本动作也不添加扩展、预校验或归一化操作。"
                    }
                  ],
                  "op": "compute",
                  "inputs": [
                    {
                      "kind": "input",
                      "index": 1
                    },
                    {
                      "kind": "input",
                      "index": 2
                    },
                    {
                      "kind": "input",
                      "index": 4
                    }
                  ],
                  "dependencies": [
                    "possible",
                    "possible",
                    "possible"
                  ],
                  "output": "search_response"
                }
              ]
            }
          ],
          "returns": [],
          "evidences": [
            {
              "basis": "execution_model",
              "ref_id": "EM10",
              "quote": "Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs",
              "reason": "本段以请求参数为输入形成响应局部值，未规定隔离机制，使用 default 处理。"
            }
          ]
        }
      },
      {
        "id": "ann_0163",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_007/events/0/events/0",
        "instruction_ids": [
          "ir_007"
        ],
        "value": {
          "effect_index": null,
          "atomic_ops": [
            {
              "evidences": [
                {
                  "basis": "source",
                  "ref_id": "src_008",
                  "quote": "using request.term unchanged as its query argument",
                  "reason": "响应随查询参数变化，保留正文对原始查询和可选参数的可能依赖。"
                },
                {
                  "basis": "source",
                  "ref_id": "src_009",
                  "quote": "When limit is present, pass its value unchanged as the limit argument.",
                  "reason": "limit 值在存在时原样作为参数传入，因此作为该请求的参数依赖记录；能力说明不请求模糊扩展，本动作也不添加扩展、预校验或归一化操作。"
                }
              ],
              "op": "compute",
              "inputs": [
                {
                  "kind": "input",
                  "index": 1
                },
                {
                  "kind": "input",
                  "index": 2
                },
                {
                  "kind": "input",
                  "index": 4
                }
              ],
              "dependencies": [
                "possible",
                "possible",
                "possible"
              ],
              "output": "search_response"
            }
          ]
        }
      }
    ]
  },
  {
    "id": "f_ir012_missing_return_forwarding",
    "target_ids": [
      "ann_0071",
      "ann_0226"
    ],
    "status": "issue",
    "explanation": "源文要求把检索响应的 items 原样返回调用方（src_014），CFG 中 ir_012 的输入即 response_items（g_0032）；这是工作流出口处的值转发关系，按 EM06 交付应保留实际取值与结果身份。annotation 在 ir_012 的 profile 证据（ann_0071）中声称“其未变更的值转发关系在 transfer_specs 中按输入操作数保留”，但 transfer_specs.ir_012 的 events（ann_0226）实际为空，没有任何引用输入操作数（response_items）的转发操作。具体差异是：源文要求的返回转发关系在表示中并不存在，而证据声称已保留；受影响的数据关系是该 IR 的返回/交付边界——items 以未变更身份交回调用方这一关系无法从注释的 transfer_specs 中读出。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_014",
        "quote": "Return the search response's items value unchanged."
      },
      {
        "basis": "cfg",
        "ref_id": "g_0032",
        "quote": "response_items"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM06",
        "quote": "delivery must retain actual selected values, input order, result identities, and explicit prohibitions"
      }
    ],
    "suggestion": "建议在 ir_012 的 transfer_specs 中补记 response_items 原样返回调用方的转发操作（保持未变更的取值与身份），使该返回转发关系与 src_014 的要求及证据中“已在 transfer_specs 中保留”的声称一致。",
    "targets": [
      {
        "id": "ann_0071",
        "kind": "annotation",
        "pointer": "/profiles/ir_012/evidences",
        "instruction_ids": [
          "ir_012"
        ],
        "value": [
          {
            "field": "operator",
            "value": "agent_runtime",
            "basis": "cfg",
            "ref_id": "g_0032",
            "quote": "return",
            "reason": "返回动作由本地运行时执行；源文未提及 LLM、工具或人工执行者。",
            "effect_index": null
          },
          {
            "field": "roles",
            "value": null,
            "basis": "execution_model",
            "ref_id": "EM06",
            "quote": "ordinary return does not prove user-facing output",
            "reason": "该指令只是把 items 原样交回调用方，源文未指明接收方或可见性边界，普通返回不证明面向用户的输出，因此没有已证据化的角色标签。",
            "effect_index": null
          },
          {
            "field": "effects",
            "value": null,
            "basis": "execution_model",
            "ref_id": "EM06",
            "quote": "ordinary return does not prove user-facing output",
            "reason": "依据同一规则，交回已有值不构成 user_output，也不属于其他效果类别；其未变更的值转发关系在 transfer_specs 中按输入操作数保留。",
            "effect_index": null
          }
        ]
      },
      {
        "id": "ann_0226",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_012/events",
        "instruction_ids": [
          "ir_012"
        ],
        "value": []
      }
    ]
  }
]
```
