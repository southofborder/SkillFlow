# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir005\_deliver\_body\_argument · 问题

源文与 CFG 约束要求 notify\.send 的 body 参数直接取当前记录（for\_each 当前元素）的 summary 字段原值，投递实参应保留 select\_part 选出的显式字段值，并保留“禁止将 access\_token 发送给任何接收对象”这一显式限制（EM06；EM11）。本注解在同一元素段内已用 select\_part 从 record 取出 recipient 与 summary，分别得到 recipient\_value 与 summary\_value，但 deliver 的第二个实参（ann\_0120）却绑定整个元素 record：summary\_value 在投递参数中完全未被引用，deliver 自身的证据也只论证了接收对象与当前元素的配对，未支持以整条记录充当正文实参。该差异把被投递正文的身份和范围由显式的 summary 字段值扩大为整个记录元素；逐元素配对虽未被破坏，但投递内容的表示范围随之覆盖记录中的其他字段（含源文禁止发送的 access\_token），既与显式禁止约束不一致，也使 summary 字段在投递处丢失其 select\_part 身份。

定位：ann\_0116、ann\_0120

修改建议：将 deliver 的第二个输入从 \{kind: local, name: record\} 改为引用同一元素绑定上 select\_part 选出的 summary\_value（保持 recipient\_value 与 summary\_value 同源自 for\_each 的 record 元素），使投递正文保留 summary 字段的显式选择身份，并与其“禁止发送 access\_token”的约束保持一致。

- source / src\_003：notify\.send 的 body 参数直接取该记录的 summary 字段原值。
- source / src\_003：整份流程禁止将 access\_token 字段发送给任何接收对象。
- execution\_model / EM06：delivery must retain actual selected values, input order, result identities, and explicit prohibitions
- execution\_model / EM11：Selecting an explicit field with select\_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged\.

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010

原始调用：[call.json](../calls/review/a001/call.json)；定位与材料：[material.json](../inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir005_deliver_body_argument",
    "target_ids": [
      "ann_0116",
      "ann_0120"
    ],
    "status": "issue",
    "explanation": "源文与 CFG 约束要求 notify.send 的 body 参数直接取当前记录（for_each 当前元素）的 summary 字段原值，投递实参应保留 select_part 选出的显式字段值，并保留“禁止将 access_token 发送给任何接收对象”这一显式限制（EM06；EM11）。本注解在同一元素段内已用 select_part 从 record 取出 recipient 与 summary，分别得到 recipient_value 与 summary_value，但 deliver 的第二个实参（ann_0120）却绑定整个元素 record：summary_value 在投递参数中完全未被引用，deliver 自身的证据也只论证了接收对象与当前元素的配对，未支持以整条记录充当正文实参。该差异把被投递正文的身份和范围由显式的 summary 字段值扩大为整个记录元素；逐元素配对虽未被破坏，但投递内容的表示范围随之覆盖记录中的其他字段（含源文禁止发送的 access_token），既与显式禁止约束不一致，也使 summary 字段在投递处丢失其 select_part 身份。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_003",
        "quote": "notify.send 的 body 参数直接取该记录的 summary 字段原值。"
      },
      {
        "basis": "source",
        "ref_id": "src_003",
        "quote": "整份流程禁止将 access_token 字段发送给任何接收对象。"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM06",
        "quote": "delivery must retain actual selected values, input order, result identities, and explicit prohibitions"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM11",
        "quote": "Selecting an explicit field with select_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged."
      }
    ],
    "suggestion": "将 deliver 的第二个输入从 {kind: local, name: record} 改为引用同一元素绑定上 select_part 选出的 summary_value（保持 recipient_value 与 summary_value 同源自 for_each 的 record 元素），使投递正文保留 summary 字段的显式选择身份，并与其“禁止发送 access_token”的约束保持一致。",
    "targets": [
      {
        "id": "ann_0116",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/2",
        "instruction_ids": [
          "ir_005"
        ],
        "value": {
          "evidences": [
            {
              "basis": "source",
              "ref_id": "src_003",
              "quote": "对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。",
              "reason": "接收对象来自当前元素的 recipient，正文位置关联同一个当前元素，保持逐元素配对。"
            }
          ],
          "op": "deliver",
          "inputs": [
            {
              "kind": "local",
              "name": "recipient_value"
            },
            {
              "kind": "local",
              "name": "record"
            }
          ],
          "target": "loc_notify_send"
        }
      },
      {
        "id": "ann_0120",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/2/inputs/1",
        "instruction_ids": [
          "ir_005"
        ],
        "value": {
          "kind": "local",
          "name": "record"
        }
      }
    ]
  }
]
```
