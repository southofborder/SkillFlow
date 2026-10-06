# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir009\_body\_lost\_select\_part\_identity · 问题

源文要求成功响应返回其显式 body 字段的原值（"return that successful response's body value unchanged"）；REP03/EM11 要求显式字段值保留 select\_part 身份，compute 只记录依赖、不能证明字段被原样传递。注解在 transfer\_specs\.ir\_009 的第二个原子操作中却把 fast\_fetch\_first\_body 表示为 compute（inputs: input index 0，dependencies: \["possible"\]），而完全同构的 ir\_013、ir\_017 对相同 CFG 输出使用了 select\_part 且 path 为 \["body"\]，注解自身的 profile 理由也写作“选出 body 字段”，与实际转移操作不一致。具体差异：第一条 fast\.fetch 成功路径的响应体 result\_006（由 ir\_020 返回）从“响应中精确 body 字段、原值不变”被降为“不透明计算、可能依赖”；这可改变返回边界所携带内容与其工具响应字段之间的数据关系，使被返回的值不再能追溯到明确的 body 字段身份。

定位：ann\_0248、ann\_0249

修改建议：将 ir\_009 的第二个原子操作改为 select\_part：input 为 input index 0（本次响应），path 为 \["body"\]，output 保持 fast\_fetch\_first\_body，与 ir\_013/ir\_017 的表示保持一致，以保留该显式字段的原值与身份，并据此复核该段输出绑定与引用关系。

- source / src\_003：return that successful response's body value unchanged
- execution\_model / EM11：Selecting an explicit field with select\_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged\.
- cfg / g\_0033：fast\_fetch\_first\_body

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012、ir\_013、ir\_014、ir\_015、ir\_016、ir\_017、ir\_018、ir\_019、ir\_020、ir\_021、ir\_022、ir\_023、ir\_024、ir\_025、ir\_026

原始调用：[call.json](../calls/review/a001/call.json)；定位与材料：[material.json](../inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir009_body_lost_select_part_identity",
    "target_ids": [
      "ann_0248",
      "ann_0249"
    ],
    "status": "issue",
    "explanation": "源文要求成功响应返回其显式 body 字段的原值（\"return that successful response's body value unchanged\"）；REP03/EM11 要求显式字段值保留 select_part 身份，compute 只记录依赖、不能证明字段被原样传递。注解在 transfer_specs.ir_009 的第二个原子操作中却把 fast_fetch_first_body 表示为 compute（inputs: input index 0，dependencies: [\"possible\"]），而完全同构的 ir_013、ir_017 对相同 CFG 输出使用了 select_part 且 path 为 [\"body\"]，注解自身的 profile 理由也写作“选出 body 字段”，与实际转移操作不一致。具体差异：第一条 fast.fetch 成功路径的响应体 result_006（由 ir_020 返回）从“响应中精确 body 字段、原值不变”被降为“不透明计算、可能依赖”；这可改变返回边界所携带内容与其工具响应字段之间的数据关系，使被返回的值不再能追溯到明确的 body 字段身份。",
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
      }
    ],
    "suggestion": "将 ir_009 的第二个原子操作改为 select_part：input 为 input index 0（本次响应），path 为 [\"body\"]，output 保持 fast_fetch_first_body，与 ir_013/ir_017 的表示保持一致，以保留该显式字段的原值与身份，并据此复核该段输出绑定与引用关系。",
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
