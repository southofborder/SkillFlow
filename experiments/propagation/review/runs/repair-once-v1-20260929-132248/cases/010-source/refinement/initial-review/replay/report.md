# 联合标注聚焦审查

**有明确问题** · 执行状态：`complete`

聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

这是旁置模型审查；不修改原标注或传播结果。编号覆盖仅表示声明检查过，未发现实质问题不等于已证明语义正确。

## f\-ir007\-acquisition\-as\-compute · 问题

源文要求对 index\.search 发起一次调用并取其响应（src\_008；CFG 输出语义名 'index\.search response'），该响应属于新获取的工具内容。按 EM09，已知工具获取且无网络证据时，应以 tool 位置（loc\_index\_search）上的 receive、在 null\-effect 事件中表达，并保留实际请求输入与可能的依赖；工具返回内容的获取边界不能被查询输入穷尽，请求影响不能替代获取来源。但 transfer\_specs/ir\_007 的唯一原子操作是 op='compute'（inputs 1/2/4、dependencies='possible'、output='search\_response'），既未引用 loc\_index\_search，也未建立任何 receive/获取关系：响应被表示成仅由请求参数计算出的值，'新获取的工具内容'这一来源身份与获取边界被丢失；该 IR 的 profile 证据（ann\_0046）自称按 EM09 以 tool 位置 receive 表达，与实际 transfer\_specs 相互矛盾。连带影响是生成的模型观察 obs\_0005 把本段可能模型可见的版本绑定为请求参数（输入 1/2/4）；按 EM10，default 模式下可观察的是 read/receive 的输出，且不会仅因获取响应而观察 receive 的请求参数，因此修正获取表示后该绑定应落在获取到的响应版本（search\_response）上。受影响的数据关系是：搜索响应的来源（新获取 vs 由请求参数计算）以及该段模型可见版本的绑定。

定位：ann\_0165、ann\_0046、obs\_0005

修改建议：按 EM09 将 ir\_007 的原子操作改为 tool 位置 loc\_index\_search 上的 receive（null\-effect 事件），输出 search\_response，并把输入 1/2/4 保留为该获取的请求输入/可能依赖；相应按 EM10 让该段 default 模式的可能模型观察绑定到获取到的响应版本，而不是请求参数。

- source / src\_008：Call index\.search exactly once
- cfg / g\_0023：index\.search response
- execution\_model / EM09：returned tool or collection content has an acquisition boundary not exhausted by query inputs\. Preserve that boundary, actual request inputs, and possible dependencies\.
- execution\_model / EM09：known tool acquisition without established networking uses receive at a tool location in a null\-effect event
- execution\_model / EM10：Default mode retains possible observation of read/receive outputs and non\-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired\.

## 审计材料

声明检查的 IR：ir\_001、ir\_002、ir\_003、ir\_004、ir\_005、ir\_006、ir\_007、ir\_008、ir\_009、ir\_010、ir\_011、ir\_012

原始调用：[call.json](../calls/review/a001/call.json)；定位与材料：[material.json](../inputs/material.json)。

### 程序解析定位

```json
[
  {
    "id": "f-ir007-acquisition-as-compute",
    "target_ids": [
      "ann_0165",
      "ann_0046",
      "obs_0005"
    ],
    "status": "issue",
    "explanation": "源文要求对 index.search 发起一次调用并取其响应（src_008；CFG 输出语义名 'index.search response'），该响应属于新获取的工具内容。按 EM09，已知工具获取且无网络证据时，应以 tool 位置（loc_index_search）上的 receive、在 null-effect 事件中表达，并保留实际请求输入与可能的依赖；工具返回内容的获取边界不能被查询输入穷尽，请求影响不能替代获取来源。但 transfer_specs/ir_007 的唯一原子操作是 op='compute'（inputs 1/2/4、dependencies='possible'、output='search_response'），既未引用 loc_index_search，也未建立任何 receive/获取关系：响应被表示成仅由请求参数计算出的值，'新获取的工具内容'这一来源身份与获取边界被丢失；该 IR 的 profile 证据（ann_0046）自称按 EM09 以 tool 位置 receive 表达，与实际 transfer_specs 相互矛盾。连带影响是生成的模型观察 obs_0005 把本段可能模型可见的版本绑定为请求参数（输入 1/2/4）；按 EM10，default 模式下可观察的是 read/receive 的输出，且不会仅因获取响应而观察 receive 的请求参数，因此修正获取表示后该绑定应落在获取到的响应版本（search_response）上。受影响的数据关系是：搜索响应的来源（新获取 vs 由请求参数计算）以及该段模型可见版本的绑定。",
    "evidences": [
      {
        "basis": "source",
        "ref_id": "src_008",
        "quote": "Call index.search exactly once"
      },
      {
        "basis": "cfg",
        "ref_id": "g_0023",
        "quote": "index.search response"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM09",
        "quote": "returned tool or collection content has an acquisition boundary not exhausted by query inputs. Preserve that boundary, actual request inputs, and possible dependencies."
      },
      {
        "basis": "execution_model",
        "ref_id": "EM09",
        "quote": "known tool acquisition without established networking uses receive at a tool location in a null-effect event"
      },
      {
        "basis": "execution_model",
        "ref_id": "EM10",
        "quote": "Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired."
      }
    ],
    "suggestion": "按 EM09 将 ir_007 的原子操作改为 tool 位置 loc_index_search 上的 receive（null-effect 事件），输出 search_response，并把输入 1/2/4 保留为该获取的请求输入/可能依赖；相应按 EM10 让该段 default 模式的可能模型观察绑定到获取到的响应版本，而不是请求参数。",
    "targets": [
      {
        "id": "ann_0165",
        "kind": "annotation",
        "pointer": "/transfer_specs/ir_007/events/0/events/0/atomic_ops/0",
        "instruction_ids": [
          "ir_007"
        ],
        "value": {
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
      },
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
        "id": "obs_0005",
        "kind": "observation",
        "pointer": "/4",
        "instruction_ids": [
          "ir_007"
        ],
        "value": {
          "id": "obs_0005",
          "instruction_id": "ir_007",
          "mode": "default",
          "values": [
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
          "target": {
            "kind": "model_context",
            "name": "当前模型处理上下文"
          },
          "raw_target_id": "ann_0163",
          "processing_target_id": "ann_0161",
          "scope_target_ids": []
        }
      }
    ]
  }
]
```
