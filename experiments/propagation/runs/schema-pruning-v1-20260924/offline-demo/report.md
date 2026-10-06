# 基础数据传播记录：手工规格示例

这是手工编写的传播规格示例，用于检查程序和审查方式；不是模型实测，不计入三例真实标注结果。未调用 LLM，未执行 Skill 或其工具。

执行状态：`complete`。

[本地可视化审查](report.html) · [完整记录](records.json) · [Data](data.json) · [冻结源文](inputs/source.json)

D 编号对应本报告内稳定的数据短名。候选集合不表示同时发生；possible 依赖不表示明文完整包含。本轮不判断风险、必要性或 DOE。

## 覆盖与诊断

```json
{
  "coverage": {
    "ir_append": "processed",
    "ir_build": "processed",
    "ir_copy": "processed",
    "ir_delete": "processed",
    "ir_local_filter": "processed",
    "ir_model_filter": "processed",
    "ir_network": "processed",
    "ir_opaque": "processed",
    "ir_read": "processed",
    "ir_return": "processed",
    "ir_save": "processed",
    "ir_source_end": "processed",
    "ir_update": "processed"
  },
  "diagnostics": [],
  "stats": {
    "block_evaluations": 2,
    "data_count": 12,
    "description_revision": 0,
    "record_count": 13
  }
}
```

<details><summary>位置身份依据（独立审计材料）</summary>

**document · runtime_context / document**

- cfg / g_0007：read；离线示例显式指定此关系；真实定位校验不等于语义正确性证明。

**model · model_context / assistant**

- cfg / g_0007：read；离线示例显式指定此关系；真实定位校验不等于语义正确性证明。

**cache · runtime_context / cache**

- cfg / g_0007：read；离线示例显式指定此关系；真实定位校验不等于语义正确性证明。

**journal · storage / journal**

- cfg / g_0007：read；离线示例显式指定此关系；真实定位校验不等于语义正确性证明。

**service · remote / example-service**

- cfg / g_0007：read；离线示例显式指定此关系；真实定位校验不等于语义正确性证明。

</details>

## ir_read · read

块：source；执行主体：agent_runtime；角色：source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: document | b: D012 |

入口／出口变化：

- `result:B`：未绑定 → D012

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_source_end · dispatch

块：source；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_model_filter · model_filter

块：main；执行主体：llm；角色：sink, transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | model_observe | deliver | input[0]: D012 | model_context: assistant | — |
| 2.1 | transform | exclude_parts | input[0]: D012 | 排除 [["api_key"]] | clean: D008 |
| 3.1 | model_observe | deliver | clean: D008 | model_context: assistant | — |

入口／出口变化：

- `result:model_clean`：未绑定 → D008

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_local_filter · local_filter

块：main；执行主体：agent_runtime, llm；角色：transformer, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | exclude_parts | input[0]: D012 | 排除 [["api_key"]] | clean: D002 |
| 2.1 | model_observe | deliver | clean: D002 | model_context: assistant | — |

入口／出口变化：

- `result:local_clean`：未绑定 → D002

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_update · update

块：main；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | update_fields | input[0]: D012; 字面值 "[redacted]": D011 | 更新 [["api_key"]] | changed: D004 |

入口／出口变化：

- `result:updated`：未绑定 → D004

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_build · build

块：main；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | build | input[0]: D004; input[1]: D002 | 组成 [["updated"], ["clean"]] | built: D005 |

入口／出口变化：

- `result:combined`：未绑定 → D005

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_opaque · opaque

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签计算 | compute | input[0]: D005 | 依赖 ["possible"] | unknown: D007 |

入口／出口变化：

- `result:computed`：未绑定 → D007

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_copy · copy

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- `result:alias`：未绑定 → D007

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_save · save

块：main；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | input[0]: D007 | runtime_context: cache；写入方式 replace | runtime_context:cache 未绑定 → D007 (strong) |

入口／出口变化：

- `runtime_context:cache`：未绑定 → D007

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_append · append

块：main；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[0]: D002 | storage: journal；写入方式 append | storage:journal D006 → D009 (strong) |

入口／出口变化：

- `storage:journal`：D006 → D009

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_delete · delete

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | — | runtime_context: cache；写入方式 delete | runtime_context:cache D007 → 未绑定 (delete) |

入口／出口变化：

- `runtime_context:cache`：D007 → 未绑定

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_network · network

块：main；执行主体：agent_runtime, tool, llm；角色：sink, source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[0]: D002 | remote: example-service | — |
| 2.1 | net_receive | receive | input[0]: D002 | remote: example-service | response: D001 |
| 3.1 | model_observe | deliver | response: D001 | model_context: assistant | — |

入口／出口变化：

- `result:response`：未绑定 → D001

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_return · return

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | `data_0e0d28063b13073ca4fef5c67cbc7f0af06158792b083b640f07c7f0ebb67581` | opaque |
| D002 | `data_1bc973207343bdbbb286581a8458be953f2bf21ddb0094f6d8b92054f75fdadd` | whole_except |
| D003 | `data_29534fa30e39c594466448f724032afb36d740efc22cb2a7c804c1a60677b139` | opaque |
| D004 | `data_2cdfa171326140c5e07a5c10b57fe7593344f160f36d659bfdbd594c97b36b9d` | field_updates |
| D005 | `data_450a30350d658d58a1307f1aabc2c9394432bc13ca03239f8a56082ad4e1c443` | known_parts |
| D006 | `data_483e69dd7899402d25abbcdd11ea0819cea035f5e791493b219fa7f255782381` | literal |
| D007 | `data_4958158b7bd278ce1a1c3b3a1f248555a0e2f7d555473ca204789a1dbf3a4bbd` | opaque |
| D008 | `data_4fd35989e692fd6187b86d350907d3a8c6dec68710832e3a6a818674525d31c2` | whole_except |
| D009 | `data_573d0a2a78dedbc515b77abae45aa5821a6d930197610471f55cc6ee77bde137` | opaque |
| D010 | `data_61c28fc40a4f85bef586fba58f779b1276f13ef01df9366b219bcaec68e56e02` | opaque |
| D011 | `data_d7e76248e297a19cf58c12547c177f1e0d13fe99dfd513b2cd29f1c9ad1a9382` | literal |
| D012 | `data_e98301ad91963546fbd2bc805093570337434dd4e1b9881054d3451f6560129d` | known_parts |
