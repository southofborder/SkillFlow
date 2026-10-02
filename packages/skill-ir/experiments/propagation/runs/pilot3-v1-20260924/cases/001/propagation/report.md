# 基础数据传播记录

执行状态：`complete`。

[本地可视化审查](report.html) · [完整记录](records.json) · [Data](data.json) · [冻结源文](inputs/source.json)

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
    "ir_012": "processed"
  },
  "diagnostics": [],
  "stats": {
    "block_evaluations": 15,
    "data_count": 7,
    "description_revision": 2,
    "record_count": 12
  }
}
```

## ir_001 · read_events_json

块：block_001；执行主体：agent_runtime；角色：source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: events.json | event_records: D002 |

入口／出口变化：

- `result:result_001`：未绑定 → D002

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_002 · dispatch

块：block_001；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_003 · get_next_event_record

块：block_002；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | input[0]: D002 | 依赖 ["derived"] | current_record: D005 |
| 1.2 | transform | compute | input[0]: D002 | 依赖 ["derived"] | has_more_records: D007 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_004 · dispatch

块：block_002；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_005 · evaluate_event_record_selection

块：block_003；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | input[0]: D005 | 依赖 ["derived"] | is_selected: D004 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_007 · extract_event_notification_fields

块：block_004；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | select_part | input[0]: D005 | 选取 ["recipient"] | recipient: D006 |
| 1.2 | transform | select_part | input[0]: D005 | 选取 ["summary"] | summary: D003 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_008 · notify_send

块：block_004；执行主体：tool；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D006; input[2]: D003 | remote: notify.send | — |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_009 · dispatch

块：block_004；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_010 · count_processed_event_records

块：block_005；执行主体：agent_runtime；角色：transformer。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | transform | compute | input[0]: D002 | 依赖 ["derived"] | processed_count: D001 |

入口／出口变化：

- `result:result_007`：未绑定 → D001

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_011 · write_count_to_file

块：block_005；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D001 | storage: count.txt；写入方式 replace | storage:count.txt 未绑定 → D001 (strong) |

入口／出口变化：

- `storage:count.txt`：未绑定 → D001

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_012 · return

块：block_005；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | `data_0d5071c96f66deffefce13ac7ce37604480ca98416651e79c1788977bf53c463` | opaque |
| D002 | `data_2beee1cd2a15bf4ffd9bfa3bb3834a1cedb5e15efb6574ad0c020e0a42ce2d96` | opaque |
| D003 | `data_497f9282a8622482c9292ed108376d3a501a6421cbbf925377c27bd57ba2ddf1` | opaque |
| D004 | `data_a2f96810ebcdc961e70f1d0d46106803a8c97f56727d6cf45c079d834c5de55d` | opaque |
| D005 | `data_c18cad85edaea683919553424e10ff7f5831f7ee7e9ad762ad05a687ee526370` | known_parts |
| D006 | `data_ea87d8c27b73e9d497f38ddc1ae6f39e92bfd9f080e7d377897fcd3b3ab651aa` | opaque |
| D007 | `data_f4b041c608fa005e9a1059322574f8b6522e3c2d9b45d5c3ff21239c6bbb5d65` | opaque |
