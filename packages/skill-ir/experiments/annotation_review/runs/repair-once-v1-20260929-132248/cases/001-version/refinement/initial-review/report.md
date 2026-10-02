# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir005\_deliver\_body\_binding · 问题

源文第5步要求“notify\.send 的 body 参数直接取该记录的 summary 字段原值”，第7步禁止把 access\_token 发送给任何接收对象；REP03/EM11 要求投递边界的实际参数用显式字段选择的值引用来表示，select\_part 保留下来的精确字段才是被投递的内容。该实现确已为当前元素生成 select\_part\(path=\["summary"\]\)→summary\_value，但 deliver 的第二个（正文）输入却引用整个元素 record，而不是 summary\_value：summary\_value 成为未被任何后续操作消费的输出。投递边界的正文参数因此从“同一元素被显式选取的 summary 字段原值”变为“整个元素绑定”，该绑定在符号层面可覆盖 access\_token、opted\_out 等未选字段，使第5步的字段选择在边界处丢失，并无依据地扩大了投递参数所表示的内容范围，与第7步禁止项所约束的发送内容关系不一致。接收对象使用 recipient\_value、逐元素配对本身不受影响。

定位：ann\_0118、ann\_0120

修改建议：把 deliver 的第二个输入由 \{"kind":"local","name":"record"\} 改为前一步 select\_part 的输出 \{"kind":"local","name":"summary\_value"\}，第一个输入保持 recipient\_value，使接收对象与正文来自同一 record 元素绑定，且正文位置只承载被显式选取的 summary 字段原值；无需改动 CFG。

- source / src\_003：notify\.send 的 body 参数直接取该记录的 summary 字段原值。
- source / src\_003：整份流程禁止将 access\_token 字段发送给任何接收对象。
- cfg / g\_0021：notify\.send 的 body 参数直接取该记录的 summary 字段原值。
- execution\_model / EM11：Selecting an explicit field with select\_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged\.

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010

原始调用：[call.json](calls/review/a001/call.json)；定位与材料：[material.json](inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir005_deliver_body_binding",
    "target_ids": [
      "ann_0118",
      "ann_0120"
    ],
    "status": "issue",
    "explanation": "源文第5步要求“notify.send 的 body 参数直接取该记录的 summary 字段原值”，第7步禁止把 access_token 发送给任何接收对象；REP03/EM11 要求投递边界的实际参数用显式字段选择的值引用来表示，select_part 保留下来的精确字段才是被投递的内容。该实现确已为当前元素生成 select_part(path=[\"summary\"])→summary_value，但 deliver 的第二个（正文）输入却引用整个元素 record，而不是 summary_value：summary_value 成为未被任何后续操作消费的输出。投递边界的正文参数因此从“同一元素被显式选取的 summary 字段原值”变为“整个元素绑定”，该绑定在符号层面可覆盖 access_token、opted_out 等未选字段，使第5步的字段选择在边界处丢失，并无依据地扩大了投递参数所表示的内容范围，与第7步禁止项所约束的发送内容关系不一致。接收对象使用 recipient_value、逐元素配对本身不受影响。",
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
        "basis": "cfg",
        "ref_id": "g_0021",
        "quote": "notify.send 的 body 参数直接取该记录的 summary 字段原值。"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM11",
        "quote": "Selecting an explicit field with select_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged."
      }
    ],
    "suggestion": "把 deliver 的第二个输入由 {\"kind\":\"local\",\"name\":\"record\"} 改为前一步 select_part 的输出 {\"kind\":\"local\",\"name\":\"summary_value\"}，第一个输入保持 recipient_value，使接收对象与正文来自同一 record 元素绑定，且正文位置只承载被显式选取的 summary 字段原值；无需改动 CFG。",
    "targets": [
      {
        "id": "ann_0118",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/2/inputs",
        "instruction_ids": [
          "ir_005"
        ],
        "value": [
          {
            "kind": "local",
            "name": "recipient_value"
          },
          {
            "kind": "local",
            "name": "record"
          }
        ]
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
