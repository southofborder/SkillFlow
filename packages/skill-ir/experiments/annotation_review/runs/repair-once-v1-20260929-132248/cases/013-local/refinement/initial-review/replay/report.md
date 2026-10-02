# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\_ir003\_unsupported\_local\_mode · 问题

源文（src\_003）只要求“Read source\_id from the user's request and read FAST\_KEY from the environment\.”，并未给出任何显式本地隔离、受限返回或凭据代理机制；按 EM10，local 模式必须有显式的 source 或 code/interface 证据并给出显式 returns，EM02 也要求这类例外必须有受支持的证据，而不能来自执行者标签或一厢情愿的实现选择。ir\_003 的处理段却被声明为 mode=local 并把返回限定为 returns=\[fast\_key\]，其理由（“段内完成取值后只向 Agent 返回 fast\_key，环境其余内容留在本地处理范围”）只是实现设想而非证据。具体差异与影响：该段读取 loc\_environment 得到 environment\_content（按 EM01 保留整个 environment 为可能读取范围），在契约默认模式下这一读取输出本应保留为可能被模型观察的版本（EM10: “Default mode retains possible observation of read/receive outputs and non\-isolated transformation inputs”）；当前声明使编译观察 obs\_0002 只携带 fast\_key，把模型可见版本从整个环境读取输出收窄为单个键值，可能掩盖环境其余内容进入后续模型请求的可能性，并错误地收紧受限返回边界；同类上下文读取 ir\_001 采用 default 模式，也进一步表明 ir\_003 的 local 声明缺少一致依据。

定位：ann\_0178、ann\_0189、obs\_0002

修改建议：按 EM02/EM10 重新评估 ir\_003 的处理模式：在缺少显式 source/code/interface 隔离证据时，应使用契约默认（default）模式并保留环境读取输出（environment\_content）作为可能被模型观察的版本，而不是用 local\+returns=\[fast\_key\] 把模型可见内容收窄为单个键值；若确实存在本地凭据读取或受限返回机制，需补充对应的 source 或 code/interface 证据。

- source / src\_003：Read source\_id from the user's request and read FAST\_KEY from the environment\.
- execution\_model / EM10：Local mode requires explicit source or code/interface evidence and an explicit returns list
- execution\_model / EM02：Such exceptions require supported source, code, or interface evidence, not executor labels or wishful implementation choices\.
- execution\_model / EM10：Default mode retains possible observation of read/receive outputs and non\-isolated transformation inputs

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012、ir\_013、ir\_014、ir\_015、ir\_016、ir\_017、ir\_018、ir\_019、ir\_020、ir\_021、ir\_022、ir\_023、ir\_024、ir\_025、ir\_026

原始调用：[call.json](../calls/review/a001/call.json)；定位与材料：[material.json](../inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f_ir003_unsupported_local_mode",
    "target_ids": [
      "ann_0178",
      "ann_0189",
      "obs_0002"
    ],
    "status": "issue",
    "explanation": "源文（src_003）只要求“Read source_id from the user's request and read FAST_KEY from the environment.”，并未给出任何显式本地隔离、受限返回或凭据代理机制；按 EM10，local 模式必须有显式的 source 或 code/interface 证据并给出显式 returns，EM02 也要求这类例外必须有受支持的证据，而不能来自执行者标签或一厢情愿的实现选择。ir_003 的处理段却被声明为 mode=local 并把返回限定为 returns=[fast_key]，其理由（“段内完成取值后只向 Agent 返回 fast_key，环境其余内容留在本地处理范围”）只是实现设想而非证据。具体差异与影响：该段读取 loc_environment 得到 environment_content（按 EM01 保留整个 environment 为可能读取范围），在契约默认模式下这一读取输出本应保留为可能被模型观察的版本（EM10: “Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs”）；当前声明使编译观察 obs_0002 只携带 fast_key，把模型可见版本从整个环境读取输出收窄为单个键值，可能掩盖环境其余内容进入后续模型请求的可能性，并错误地收紧受限返回边界；同类上下文读取 ir_001 采用 default 模式，也进一步表明 ir_003 的 local 声明缺少一致依据。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_003",
        "quote": "Read source_id from the user's request and read FAST_KEY from the environment."
      },
      {
        "basis": "execution_model",
        "ref_id": "EM10",
        "quote": "Local mode requires explicit source or code/interface evidence and an explicit returns list"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM02",
        "quote": "Such exceptions require supported source, code, or interface evidence, not executor labels or wishful implementation choices."
      },
      {
        "basis": "execution_model",
        "ref_id": "EM10",
        "quote": "Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs"
      }
    ],
    "suggestion": "按 EM02/EM10 重新评估 ir_003 的处理模式：在缺少显式 source/code/interface 隔离证据时，应使用契约默认（default）模式并保留环境读取输出（environment_content）作为可能被模型观察的版本，而不是用 local+returns=[fast_key] 把模型可见内容收窄为单个键值；若确实存在本地凭据读取或受限返回机制，需补充对应的 source 或 code/interface 证据。",
    "targets": [
      {
        "id": "ann_0178",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_003/events/0",
        "instruction_ids": [
          "ir_003"
        ],
        "value": {
          "kind": "processing",
          "mode": "local",
          "events": [
            {
              "effect_index": 0,
              "atomic_ops": [
                {
                  "evidences": [
                    {
                      "basis": "source",
                      "ref_id": "src_003",
                      "quote": "read FAST_KEY from the environment",
                      "reason": "源文明确从环境读取；按 EM01 不建立 key-only 读取，保留整个 environment 作为读取范围。"
                    }
                  ],
                  "op": "read",
                  "location": "loc_environment",
                  "output": "environment_content"
                },
                {
                  "evidences": [
                    {
                      "basis": "source",
                      "ref_id": "src_003",
                      "quote": "read FAST_KEY from the environment",
                      "reason": "从环境内容中选出明确字段 FAST_KEY，保持原值。"
                    }
                  ],
                  "op": "select_part",
                  "input": {
                    "kind": "local",
                    "name": "environment_content"
                  },
                  "path": [
                    "FAST_KEY"
                  ],
                  "output": "fast_key"
                }
              ]
            }
          ],
          "returns": [
            {
              "kind": "local",
              "name": "fast_key"
            }
          ],
          "evidences": [
            {
              "basis": "source",
              "ref_id": "src_003",
              "quote": "Read source_id from the user's request and read FAST_KEY from the environment.",
              "reason": "由环境取得凭据，段内完成取值后只向 Agent 返回 fast_key，环境其余内容留在本地处理范围。"
            }
          ]
        }
      },
      {
        "id": "ann_0189",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_003/events/0/returns",
        "instruction_ids": [
          "ir_003"
        ],
        "value": [
          {
            "kind": "local",
            "name": "fast_key"
          }
        ]
      },
      {
        "id": "obs_0002",
        "kind": "observation",
        "pointer": "/1",
        "instruction_ids": [
          "ir_003"
        ],
        "value": {
          "id": "obs_0002",
          "instruction_id": "ir_003",
          "mode": "local",
          "values": [
            {
              "kind": "local",
              "name": "fast_key"
            }
          ],
          "target": {
            "kind": "model_context",
            "name": "当前模型处理上下文"
          },
          "raw_target_id": "ann_0189",
          "processing_target_id": "ann_0178",
          "scope_target_ids": []
        }
      }
    ]
  }
]
```
