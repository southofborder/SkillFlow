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
  "diagnostics": [],
  "stats": {
    "block_evaluations": 12,
    "data_count": 20,
    "description_revision": 0,
    "record_count": 18
  }
}
```

## ir_001 · read_source_id

块：block_001；执行主体：agent_runtime；角色：source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: source_id | ir_001_source_id: D001 |

入口／出口变化：

- `result:result_001`：未绑定 → D001

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_002 · dispatch

块：block_001；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_003 · read_fast_key

块：block_002；执行主体：agent_runtime；角色：source。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: FAST_KEY | ir_003_fast_key: D020 |
| 1.2 | context_read | compute | ir_003_fast_key: D020 | 依赖 ["derived"] | ir_003_fast_key_present: D003 |

入口／出口变化：

- `result:result_002`：未绑定 → D020
- `result:result_003`：未绑定 → D003

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_004 · dispatch

块：block_002；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_005 · fast.fetch

块：block_003；执行主体：agent_runtime, tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D001; input[2]: D020 | remote: fast.fetch | — |
| 2.1 | net_receive | receive | input[1]: D001; input[2]: D020 | remote: fast.fetch | ir_005_response: D013 |
| 2.2 | net_receive | compute | ir_005_response: D013 | 依赖 ["possible"] | ir_005_body: D009 |
| 2.3 | net_receive | compute | ir_005_response: D013 | 依赖 ["possible"] | ir_005_error: D019 |
| 2.4 | net_receive | compute | ir_005_response: D013 | 依赖 ["derived"] | ir_005_status: D007 |
| 3.1 | model_observe | deliver | ir_005_body: D009; ir_005_error: D019; ir_005_status: D007 | model_context: symbolic:llm_context | — |

入口／出口变化：

- `result:result_004`：未绑定 → D009
- `result:result_005`：未绑定 → D019
- `result:result_006`：未绑定 → D007

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_006 · dispatch

块：block_003；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_007 · fast.fetch

块：block_004；执行主体：agent_runtime, tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D001; input[2]: D020 | remote: fast.fetch | — |
| 2.1 | net_receive | receive | input[1]: D001; input[2]: D020 | remote: fast.fetch | ir_007_response: D014 |
| 2.2 | net_receive | compute | ir_007_response: D014 | 依赖 ["possible"] | ir_007_body: D017 |
| 2.3 | net_receive | compute | ir_007_response: D014 | 依赖 ["possible"] | ir_007_error: D015 |
| 2.4 | net_receive | compute | ir_007_response: D014 | 依赖 ["derived"] | ir_007_status: D006 |
| 3.1 | model_observe | deliver | ir_007_body: D017; ir_007_error: D015; ir_007_status: D006 | model_context: symbolic:llm_context | — |

入口／出口变化：

- `result:result_007`：未绑定 → D017
- `result:result_008`：未绑定 → D015
- `result:result_009`：未绑定 → D006

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_008 · dispatch

块：block_004；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_009 · archive.fetch

块：block_005；执行主体：agent_runtime, tool；角色：source, sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | net_send | deliver | input[1]: D001 | remote: archive.fetch | — |
| 2.1 | net_receive | receive | input[1]: D001 | remote: archive.fetch | ir_009_response: D010 |
| 2.2 | net_receive | compute | ir_009_response: D010 | 依赖 ["possible"] | ir_009_body: D008 |
| 2.3 | net_receive | compute | ir_009_response: D010 | 依赖 ["possible"] | ir_009_error: D012 |
| 2.4 | net_receive | compute | ir_009_response: D010 | 依赖 ["derived"] | ir_009_status: D005 |
| 3.1 | model_observe | deliver | ir_009_body: D008; ir_009_error: D012; ir_009_status: D005 | model_context: symbolic:llm_context | — |

入口／出口变化：

- `result:result_010`：未绑定 → D008
- `result:result_011`：未绑定 → D012
- `result:result_012`：未绑定 → D005

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_010 · dispatch

块：block_005；执行主体：agent_runtime；角色：[]。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_011 · append_status_to_local_file

块：block_006；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D007 | storage: local status.txt；写入方式 append | storage:local status.txt D002 → D016 (strong) |

入口／出口变化：

- `storage:local status.txt`：D002 → D016

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_012 · return

块：block_006；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_013 · append_status_to_local_file

块：block_007；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D006 | storage: local status.txt；写入方式 append | storage:local status.txt D002 → D018 (strong) |

入口／出口变化：

- `storage:local status.txt`：D002 → D018

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_014 · return

块：block_007；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_015 · append_status_to_local_file

块：block_008；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D005 | storage: local status.txt；写入方式 append | storage:local status.txt D002 → D011 (strong) |

入口／出口变化：

- `storage:local status.txt`：D002 → D011

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_016 · return

块：block_008；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_017 · append_status_to_local_file

块：block_009；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | input[1]: D005 | storage: local status.txt；写入方式 append | storage:local status.txt D002 → D004 (strong) |

入口／出口变化：

- `storage:local status.txt`：D002 → D004

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## ir_018 · return

块：block_009；执行主体：agent_runtime；角色：sink。

| 顺序 | 效果 | op | 输入 | 字段或边界 | 输出或状态变化 |
|---|---|---|---|---|---|
| — | 无效果事件 | — | — | 空效果不等于空操作 | 查看输出绑定和状态变化 |

入口／出口变化：

- 位置绑定没有变化；不代表没有观察或发送。

公开 IR 输出绑定及逐项证据见 HTML 展开区。

## 数据索引

| 短名 | 完整 ID | 内容形态 |
|---|---|---|
| D001 | `data_00303bbeee4faf1adef603d3c382dbacfb4d5cc8c8b071dc45ed0a31e20a7239` | opaque |
| D002 | `data_15ff76462c1eb2101d45d079afd9c667e6c39564e7490cc5bfb3024030d27980` | opaque |
| D003 | `data_23118ddf12af608f1fa33b434d820ba8cf2525e716b40fb7238c4d1bad57f791` | opaque |
| D004 | `data_3ac8c7de410ad3d845de5518ba62476ffccae44814d9a174df9b9e7830045826` | opaque |
| D005 | `data_4aff3e078fdffc9f086331fb49249eec4640fc040790bff02d25f12a80ad7b26` | opaque |
| D006 | `data_4f6533609710c4cf543566aa9daa2e95f1d3330f9fb8a7679bea43ea65c92419` | opaque |
| D007 | `data_69fcf882823b33334b2d629c6ad4939cd1aa6677b3ed704d8219248ba7692e79` | opaque |
| D008 | `data_6d81cc251196a9db60cd53c9cfc3fcfb7fec84b87661dba493f04d30dea2484a` | opaque |
| D009 | `data_7cf9d5a3a40d973009d558eeefb9652caafadae6145567940020ab5d8171828c` | opaque |
| D010 | `data_b8db9e967f88003732b85f7f85ba1aa085d2500abb67c8f2c1cb71cd219f73ba` | opaque |
| D011 | `data_bed39de58979155708cba4992d26c117095ead44dd84d429a6d200588cccb682` | opaque |
| D012 | `data_d76fe0dfa1aa9c9328e3f78515c5fa875fe7c10df8003a4ea45f197d609b219e` | opaque |
| D013 | `data_df764fe4928e22adb695865c88c204db9a80b69ef7c717135b9406820382ce35` | opaque |
| D014 | `data_e0a7436ad4b963986a0716c1682e8d4ea3488837e19d67f6b8f1e74ece45fd54` | opaque |
| D015 | `data_ead5158f8a1a1e533b7452a6a5bbf10c06a070a1f4eacf831332395a1e7f441d` | opaque |
| D016 | `data_ec9873e232269c02d622947e12a5dfaf92cf406ba0977ae1b1f0802c82640740` | opaque |
| D017 | `data_eec090b646688f24ffb61710ac4773d44ac1ce5595c1750f3b945d8f2e9ec1fb` | opaque |
| D018 | `data_efeee10d53ba60b9f3bf9a5d477a6d359c8585c0de4c5a88872d8cc8b4431048` | opaque |
| D019 | `data_f4c24d9806e544277b276cab890311f6e30f117143e1cb3cc2d8c30fa685b27f` | opaque |
| D020 | `data_fb114ad51b4b3298540944e139b4ccc001b5aad2f58c9e01f9d808d90fa8a00f` | opaque |
