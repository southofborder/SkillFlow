# 基础数据传播记录

执行状态：`complete`。

[本地可视化审查](report.html) · [完整记录](records.json) · [Data](data.json) · [冻结源文](../inputs/source.json)

D 编号对应本报告内稳定的数据短名。候选集合不表示同时发生；possible 依赖不表示明文完整包含。本轮不判断风险、必要性或 DOE。

## 覆盖与诊断

```json
{
  "coverage": {
    "ir_001": "processed",
    "ir_002": "processed",
    "ir_003": "processed",
    "ir_004": "processed",
    "ir_005": "processed",
    "ir_006": "processed",
    "ir_007": "processed",
    "ir_008": "processed",
    "ir_009": "processed",
    "ir_010": "processed",
    "ir_011": "processed",
    "ir_012": "processed",
    "ir_013": "processed",
    "ir_014": "processed",
    "ir_015": "processed",
    "ir_016": "processed",
    "ir_017": "processed",
    "ir_018": "processed"
  },
  "diagnostics": [
    {
      "code": "annotation_unresolved",
      "items": [
        {
          "field": "effects",
          "instruction_id": "ir_012",
          "reason": "普通 return 本身不足以证明面向用户输出；执行模型 EM06 指出 ordinary return 不证明 user-facing output，因此未断言 user_output，也无法确认无适用效果。"
        },
        {
          "field": "effects",
          "instruction_id": "ir_014",
          "reason": "普通 return 本身不足以证明面向用户输出；执行模型 EM06 指出 ordinary return 不证明 user-facing output，因此未断言 user_output，也无法确认无适用效果。"
        },
        {
          "field": "effects",
          "instruction_id": "ir_016",
          "reason": "普通 return 本身不足以证明面向用户输出；执行模型 EM06 指出 ordinary return 不证明 user-facing output，因此未断言 user_output，也无法确认无适用效果。"
        },
        {
          "field": "effects",
          "instruction_id": "ir_018",
          "reason": "普通 return 本身不足以证明面向用户输出；执行模型 EM06 指出 ordinary return 不证明 user-facing output，因此未断言 user_output，也无法确认无适用效果。"
        }
      ],
      "reason": "保留标注未决项；传播完成不表示未决已解决。"
    }
  ],
  "stats": {
    "block_evaluations": 14,
    "data_count": 18,
    "description_revision": 8,
    "record_count": 18
  }
}
```

## ir_001 · read_request_json

块：block_001；执行主体：agent_runtime；角色：source, transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: request.json | request_json_content: D006 |
| 2.1 | transform | compute | request_json_content: D006 | 依赖 ["derived"] | request_term: D016 |
| 2.2 | transform | compute | request_json_content: D006 | 依赖 ["derived"] | from_date_present: D002 |
| 2.3 | transform | compute | request_json_content: D006 | 依赖 ["derived"] | request_from_date: D001 |
| 2.4 | transform | compute | request_json_content: D006 | 依赖 ["derived"] | limit_present: D015 |
| 2.5 | transform | compute | request_json_content: D006 | 依赖 ["derived"] | request_limit: D013 |

入口／出口变化：

- `result:result_001`：未绑定 → D016
- `result:result_002`：未绑定 → D002
- `result:result_003`：未绑定 → D001
- `result:result_004`：未绑定 → D015
- `result:result_005`：未绑定 → D013

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_002 · dispatch

块：block_001；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_003 · index.search

块：block_002；执行主体：tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D016; input[2]: D001; input[3]: D013 | remote: index.search | — |
| 2.1 | net_receive | receive | input[1]: D016; input[2]: D001; input[3]: D013 | remote: index.search | search_response_both: D012 |
| 2.2 | net_receive | select_part | search_response_both: D012 | 选取 ["total"] | search_total_both: D004 |
| 2.3 | net_receive | select_part | search_response_both: D012 | 选取 ["items"] | search_items_both: D003 |
| 3.1 | model_observe | deliver | search_response_both: D012 | model_context: llm_context | — |

入口／出口变化：

- `result:result_006`：未绑定 → D004
- `result:result_007`：未绑定 → D003

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_004 · dispatch

块：block_002；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_005 · index.search

块：block_003；执行主体：tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D016; input[2]: D001 | remote: index.search | — |
| 2.1 | net_receive | receive | input[1]: D016; input[2]: D001 | remote: index.search | search_response_from_date: D009 |
| 2.2 | net_receive | select_part | search_response_from_date: D009 | 选取 ["total"] | search_total_from_date: D008 |
| 2.3 | net_receive | select_part | search_response_from_date: D009 | 选取 ["items"] | search_items_from_date: D011 |
| 3.1 | model_observe | deliver | search_response_from_date: D009 | model_context: llm_context | — |

入口／出口变化：

- `result:result_008`：未绑定 → D008
- `result:result_009`：未绑定 → D011

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_007 · index.search

块：block_004；执行主体：tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D016; input[2]: D013 | remote: index.search | — |
| 2.1 | net_receive | receive | input[1]: D016; input[2]: D013 | remote: index.search | search_response_limit: D007 |
| 2.2 | net_receive | select_part | search_response_limit: D007 | 选取 ["total"] | search_total_limit: D010 |
| 2.3 | net_receive | select_part | search_response_limit: D007 | 选取 ["items"] | search_items_limit: D014 |
| 3.1 | model_observe | deliver | search_response_limit: D007 | model_context: llm_context | — |

入口／出口变化：

- `result:result_010`：未绑定 → D010
- `result:result_011`：未绑定 → D014

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_008 · dispatch

块：block_004；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_009 · index.search

块：block_005；执行主体：tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D016 | remote: index.search | — |
| 2.1 | net_receive | receive | input[1]: D016 | remote: index.search | search_response_neither: D017 |
| 2.2 | net_receive | select_part | search_response_neither: D017 | 选取 ["total"] | search_total_neither: D005 |
| 2.3 | net_receive | select_part | search_response_neither: D017 | 选取 ["items"] | search_items_neither: D018 |
| 3.1 | model_observe | deliver | search_response_neither: D017 | model_context: llm_context | — |

入口／出口变化：

- `result:result_012`：未绑定 → D005
- `result:result_013`：未绑定 → D018

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_010 · dispatch

块：block_005；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_011 · write_total_to_count_file

块：block_006；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D004 | storage: count.txt；写入方式 replace | storage:count.txt 未绑定 → D004 (strong) |

入口／出口变化：

- `storage:count.txt`：未绑定 → D004

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_012 · return

块：block_006；执行主体：agent_runtime；角色：sink。

**效果顺序未确定；编号只用于定位。**

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_013 · write_total_to_count_file

块：block_007；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D008 | storage: count.txt；写入方式 replace | storage:count.txt 未绑定 → D008 (strong) |

入口／出口变化：

- `storage:count.txt`：未绑定 → D008

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_014 · return

块：block_007；执行主体：agent_runtime；角色：sink。

**效果顺序未确定；编号只用于定位。**

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_015 · write_total_to_count_file

块：block_008；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D010 | storage: count.txt；写入方式 replace | storage:count.txt 未绑定 → D010 (strong) |

入口／出口变化：

- `storage:count.txt`：未绑定 → D010

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_016 · return

块：block_008；执行主体：agent_runtime；角色：sink。

**效果顺序未确定；编号只用于定位。**

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_017 · write_total_to_count_file

块：block_009；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D005 | storage: count.txt；写入方式 replace | storage:count.txt 未绑定 → D005 (strong) |

入口／出口变化：

- `storage:count.txt`：未绑定 → D005

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_018 · return

块：block_009；执行主体：agent_runtime；角色：sink。

**效果顺序未确定；编号只用于定位。**

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | `data_17cfa780c5989f0837b84ed6914eb263eb2aca66b587d495eaa61163fea733ba` | opaque |
| D002 | `data_1a305adf192d32d3dff61766b2838299de342fada0ba573a357cca51ea049747` | opaque |
| D003 | `data_34332745759e79cae6fef2cdea6dd9c1029e9f00a762f972c05977c85007f1b0` | opaque |
| D004 | `data_3b892784afd205310b81349ab77e9224eb869d9a8004aa29e085b4d0b4482928` | opaque |
| D005 | `data_478667479da93edd6f9ed12b0806a3a725ada3365f2103b6add92c8c417b3be4` | opaque |
| D006 | `data_496f884198eb899926835ce499abf0b2f1e661b3c9c8a27752f37767ecea0a3b` | opaque |
| D007 | `data_4b1752501fd327d43c433e03a89435cdac7e24804cd8294a77d8f38a1351c58f` | known_parts |
| D008 | `data_89de780f8770bd59d5fcfdc1d7d54f1433c72860695620f366596a33b84bbdc8` | opaque |
| D009 | `data_a96867dfe377b30fc64babd36f3642cea020043351e81b97b172d03ac6eba035` | known_parts |
| D010 | `data_c0e3c1ab85491bd47fd750c703bbb51592150c68ad465244f4220770eb3a3ae8` | opaque |
| D011 | `data_c64a8e1ead775bd5a531a15ce83aec9e3592717d40f491a193fe1f5e6d0a5379` | opaque |
| D012 | `data_c99d51bb3c30a7404c18f211c3513def788cd1c4cd63d3a6a77198003aa78d07` | known_parts |
| D013 | `data_cc1585740dc4d48a93244161cc073284f36e6d2245db7d3b7e65bfdd6fddae6d` | opaque |
| D014 | `data_d87a16b7c513e090eff289f982901d575ac714161582b4876342dbfd11f10a75` | opaque |
| D015 | `data_e4e4ac2f6f76350e0bfe0aff9b98f8f1dc66939f8e4fe1929a55870101c708fa` | opaque |
| D016 | `data_f86940c3a2196e18041deeaa7d670c5c993526fbd04df0df7aaae8d57c99ea5b` | opaque |
| D017 | `data_f88b517f80bb0af70946ae05d51915611bd46d751c79e2a0f278975cdf71c7f0` | known_parts |
| D018 | `data_f9bddbb188771a831913f601582d63c8374f794f982b8e49f2bab72bc7cb2477` | opaque |
