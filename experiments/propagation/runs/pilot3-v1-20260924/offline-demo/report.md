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

## ir_read · read

块：source；执行主体：agent_runtime；角色：source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: document | b: D010 |

入口／出口变化：

- `result:B`：未绑定 → D010

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
| 1.1 | model_observe | deliver | input[0]: D010 | model_context: assistant | — |
| 2.1 | transform | exclude_parts | input[0]: D010 | 排除 [["api_key"]] | clean: D009 |
| 3.1 | model_observe | deliver | clean: D009 | model_context: assistant | — |

入口／出口变化：

- `result:model_clean`：未绑定 → D009

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_local_filter · local_filter

块：main；执行主体：agent_runtime, llm；角色：transformer, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | exclude_parts | input[0]: D010 | 排除 [["api_key"]] | clean: D002 |
| 2.1 | model_observe | deliver | clean: D002 | model_context: assistant | — |

入口／出口变化：

- `result:local_clean`：未绑定 → D002

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_update · update

块：main；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | update_fields | input[0]: D010; 字面值 "[redacted]": D012 | 更新 [["api_key"]] | changed: D001 |

入口／出口变化：

- `result:updated`：未绑定 → D001

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_build · build

块：main；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | build | input[0]: D001; input[1]: D002 | 组成 [["updated"], ["clean"]] | built: D008 |

入口／出口变化：

- `result:combined`：未绑定 → D008

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_opaque · opaque

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | 无标签计算 | compute | input[0]: D008 | 依赖 ["possible"] | unknown: D011 |

入口／出口变化：

- `result:computed`：未绑定 → D011

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_copy · copy

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- `result:alias`：未绑定 → D011

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_save · save

块：main；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | input[0]: D011 | runtime_context: cache；写入方式 replace | runtime_context:cache 未绑定 → D011 (strong) |

入口／出口变化：

- `runtime_context:cache`：未绑定 → D011

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_append · append

块：main；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[0]: D002 | storage: journal；写入方式 append | storage:journal D003 → D004 (strong) |

入口／出口变化：

- `storage:journal`：D003 → D004

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_delete · delete

块：main；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_write | write | — | runtime_context: cache；写入方式 delete | runtime_context:cache D011 → 未绑定 (delete) |

入口／出口变化：

- `runtime_context:cache`：D011 → 未绑定

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_network · network

块：main；执行主体：agent_runtime, tool, llm；角色：sink, source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[0]: D002 | remote: example-service | — |
| 2.1 | net_receive | receive | input[0]: D002 | remote: example-service | response: D006 |
| 3.1 | model_observe | deliver | response: D006 | model_context: assistant | — |

入口／出口变化：

- `result:response`：未绑定 → D006

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
| D001 | `data_22ecded345e9937715e0ad8b3b5669d9a5b1476fe686e499d7da1d68b9b2a7db` | field_updates |
| D002 | `data_35020d476eb0e04fb17f0d849cadee48b2d01ca04045b5a0f9421e2cd31a06c8` | whole_except |
| D003 | `data_37a2739af271b64cdcae2f0921bb1731e2c2d5b56195a83600b21ce8e6c3336f` | literal |
| D004 | `data_3c041a0597a6fec1abf77eb230d2690d62ae5ddc627af853e781c32a49ee2d5f` | opaque |
| D005 | `data_6b9b193c6cff2ef3c565fd87576f8ddc1181d6f83e12b94e2bc275cea7d81fc3` | opaque |
| D006 | `data_75c6f31dc261eba6def7fe91ed1c61b10d7962ffbf9541cb0c613ed8abbd73ce` | opaque |
| D007 | `data_78e8cfafce4eeea6d14661a2b78012b3b54a2e34a30829cddd0d0af6ce504d39` | opaque |
| D008 | `data_8ea091db2baddffa178e2486fd10a148b601311ae18a75d1ad34ecbc3c9cf629` | known_parts |
| D009 | `data_a2f39bb42ba1f9c5d00d6840616a30fbf29b82793285df37b6b46b136a2d13fb` | whole_except |
| D010 | `data_bc8e0ebc286a5b9638e5d38f33f5f3f9d9842e5fccb315e546ca3673287c8b82` | known_parts |
| D011 | `data_c462bcfda4f1600587a70603121764519a0f92a4ed27de632cad4ff5ac25d348` | opaque |
| D012 | `data_f4a5fa21fae65f138c63a58067625d93d4a993c95a247f4ca56eafffce38eedf` | literal |
