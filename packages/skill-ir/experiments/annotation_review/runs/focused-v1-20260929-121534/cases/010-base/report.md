# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir012\_return\_forwarding\_claim\_unsupported · 问题

源文与 CFG 要求把 search response 的 items 原样交回调用方（ir\_012 以 result\_009 为输入执行 return），这构成一条未变更的值转发/交付关系，涉及接收方边界。raw annotation 在 /profiles/ir\_012/effects 的说明中声称“其未变更的值转发关系在 transfer\_specs 中按输入操作数保留”，但 /transfer\_specs/ir\_012 的 events 与 output\_bindings 均为空，没有任何以输入操作数表示的转发/交付记录（对比 ir\_010 的 write 事件保留了输入操作数 1，可见该位置本可记录此类关系）。同时，该说明所引用的 EM06 引文只能支持“普通 return 不构成面向用户的输出”，并不能支持“转发关系已被保留”的推断。具体差异是：注释声称已保留的 items→调用方交付关系在注释内容中实际不存在。可影响的数据关系：response\_items 交回调用方的交付/转发关系（接收方边界及值同一性）会从 transfer\_specs 中缺失，下游依据该注释读取时看不到 items 被交回调用方这一关系。

定位：ann\_0071、ann\_0224、ann\_0225、ann\_0226

修改建议：建议在 /transfer\_specs/ir\_012 中按输入操作数保留 response\_items 交回调用方的未变更转发/交付关系（在 events 或相应绑定中表达），或删除 /profiles/ir\_012 说明中“已在 transfer\_specs 中按输入操作数保留”的断言，使说明与实际内容一致。

- source / src\_014：Return the search response's items value unchanged\.
- cfg / g\_0032：Return the search response's items value unchanged\.
- execution\_model / EM06：ordinary return does not prove user\-facing output

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012

原始调用：[call.json](calls/review/a001/call.json)；定位与材料：[material.json](inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir012_return_forwarding_claim_unsupported",
    "target_ids": [
      "ann_0071",
      "ann_0224",
      "ann_0225",
      "ann_0226"
    ],
    "status": "issue",
    "explanation": "源文与 CFG 要求把 search response 的 items 原样交回调用方（ir_012 以 result_009 为输入执行 return），这构成一条未变更的值转发/交付关系，涉及接收方边界。raw annotation 在 /profiles/ir_012/effects 的说明中声称“其未变更的值转发关系在 transfer_specs 中按输入操作数保留”，但 /transfer_specs/ir_012 的 events 与 output_bindings 均为空，没有任何以输入操作数表示的转发/交付记录（对比 ir_010 的 write 事件保留了输入操作数 1，可见该位置本可记录此类关系）。同时，该说明所引用的 EM06 引文只能支持“普通 return 不构成面向用户的输出”，并不能支持“转发关系已被保留”的推断。具体差异是：注释声称已保留的 items→调用方交付关系在注释内容中实际不存在。可影响的数据关系：response_items 交回调用方的交付/转发关系（接收方边界及值同一性）会从 transfer_specs 中缺失，下游依据该注释读取时看不到 items 被交回调用方这一关系。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_014",
        "quote": "Return the search response's items value unchanged."
      },
      {
        "basis": "cfg",
        "ref_id": "g_0032",
        "quote": "Return the search response's items value unchanged."
      },
      {
        "basis": "execution_model",
        "ref_id": "EM06",
        "quote": "ordinary return does not prove user-facing output"
      }
    ],
    "suggestion": "建议在 /transfer_specs/ir_012 中按输入操作数保留 response_items 交回调用方的未变更转发/交付关系（在 events 或相应绑定中表达），或删除 /profiles/ir_012 说明中“已在 transfer_specs 中按输入操作数保留”的断言，使说明与实际内容一致。",
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
        "id": "ann_0224",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_012",
        "instruction_ids": [
          "ir_012"
        ],
        "value": {
          "events": [],
          "output_bindings": []
        }
      },
      {
        "id": "ann_0225",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_012/events",
        "instruction_ids": [
          "ir_012"
        ],
        "value": []
      },
      {
        "id": "ann_0226",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_012/output_bindings",
        "instruction_ids": [
          "ir_012"
        ],
        "value": []
      }
    ]
  }
]
```
