# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir009\_body\_identity\_lost · 问题

源文要求 'On either tool's success, return that successful response's body value unchanged'：首次 fast\.fetch 成功后返回的应是成功响应中已有的 body 值并保持原值，这属于显式字段的身份关系；EM11 规定显式字段应以 select\_part 保留该部分，compute 只记录依赖、不能证明字段被原样转发。但注释在 ir\_009 的第二个原子操作（fast\_fetch\_first\_body）使用 compute 且 dependencies 仅为 \['possible'\]，而操作码、输入（input index 0）、源文依据完全相同的 ir\_013（重试分类）以及 ir\_017（archive\.fetch 分类）却用 select\_part 加 path \['body'\]/\['error'\] 表达同一关系。该差异把首次成功路径的 body 由'原值字段'降级为'可能依赖'，使经 ir\_020 返回给调用方的内容不再被断言为响应 body 原值，改变了显式字段身份以及该路径后续交付的数据关系，并与同一注释对同一源文要求的其他表示互相矛盾。

定位：ann\_0248、ann\_0249

修改建议：建议把 ir\_009 中 fast\_fetch\_first\_body 的原子操作改为与 ir\_013 一致的 select\_part 表示（沿用 input index 0 与现有输出名，仅恢复对显式 body 字段的身份保留），使三条成功路径对同一源文要求的表示保持一致；若确需区分首次响应与重试响应在该字段上的处理，应先给出源文或接口层面的依据，而不是仅保留 possible 依赖。

- source / src\_003：return that successful response's body value unchanged
- execution\_model / EM11：Selecting an explicit field with select\_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged\.
- cfg / g\_0033：fast\_fetch\_first\_body
- cfg / g\_0045：fast\_fetch\_retry\_body

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012、ir\_013、ir\_014、ir\_015、ir\_016、ir\_017、ir\_018、ir\_019、ir\_020、ir\_021、ir\_022、ir\_023、ir\_024、ir\_025、ir\_026

原始调用：[call.json](calls/review/a001/call.json)；定位与材料：[material.json](inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir009_body_identity_lost",
    "target_ids": [
      "ann_0248",
      "ann_0249"
    ],
    "status": "issue",
    "explanation": "源文要求 'On either tool's success, return that successful response's body value unchanged'：首次 fast.fetch 成功后返回的应是成功响应中已有的 body 值并保持原值，这属于显式字段的身份关系；EM11 规定显式字段应以 select_part 保留该部分，compute 只记录依赖、不能证明字段被原样转发。但注释在 ir_009 的第二个原子操作（fast_fetch_first_body）使用 compute 且 dependencies 仅为 ['possible']，而操作码、输入（input index 0）、源文依据完全相同的 ir_013（重试分类）以及 ir_017（archive.fetch 分类）却用 select_part 加 path ['body']/['error'] 表达同一关系。该差异把首次成功路径的 body 由'原值字段'降级为'可能依赖'，使经 ir_020 返回给调用方的内容不再被断言为响应 body 原值，改变了显式字段身份以及该路径后续交付的数据关系，并与同一注释对同一源文要求的其他表示互相矛盾。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_003",
        "quote": "return that successful response's body value unchanged"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM11",
        "quote": "Selecting an explicit field with select_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged."
      },
      {
        "basis": "cfg",
        "ref_id": "g_0033",
        "quote": "fast_fetch_first_body"
      },
      {
        "basis": "cfg",
        "ref_id": "g_0045",
        "quote": "fast_fetch_retry_body"
      }
    ],
    "suggestion": "建议把 ir_009 中 fast_fetch_first_body 的原子操作改为与 ir_013 一致的 select_part 表示（沿用 input index 0 与现有输出名，仅恢复对显式 body 字段的身份保留），使三条成功路径对同一源文要求的表示保持一致；若确需区分首次响应与重试响应在该字段上的处理，应先给出源文或接口层面的依据，而不是仅保留 possible 依赖。",
    "targets": [
      {
        "id": "ann_0248",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_009/events/0/events/0/atomic_ops/1",
        "instruction_ids": [
          "ir_009"
        ],
        "value": {
          "evidences": [
            {
              "basis": "source",
              "ref_id": "src_003",
              "quote": "return that successful response's body value unchanged",
              "reason": "响应提供输出正文的内容依据，记录正文输出对本次响应的可能依赖。"
            }
          ],
          "op": "compute",
          "inputs": [
            {
              "kind": "input",
              "index": 0
            }
          ],
          "dependencies": [
            "possible"
          ],
          "output": "fast_fetch_first_body"
        }
      },
      {
        "id": "ann_0249",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_009/events/0/events/0/atomic_ops/1/dependencies",
        "instruction_ids": [
          "ir_009"
        ],
        "value": [
          "possible"
        ]
      }
    ]
  }
]
```
