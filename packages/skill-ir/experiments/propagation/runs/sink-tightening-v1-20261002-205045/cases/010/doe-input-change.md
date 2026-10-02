# DOE 变化对照：010 / Q04

本页只比较实际事实文件。历史文件按原始 JSON 只读查看，不用新版加载器迁移；数据按来源和关系对应，不要求跨运行 ID 相同。

## 文件结构

```text
DOE 顶层业务区：保持不变
locations：继续保留 access_scope、retention
sink_boundaries：继续保留操作坐标、目标、类型和固定等级
records[IR].events[].atomic_ops[]
├─ build.members[]
│  ├─ path：原业务字段位置
│  ├─ value_input_index：原值输入槽；确定省略时 null
│  └─ when_input_index：控制槽；无条件时 null
└─ 条件 model_observe.when_input_index：控制槽，不能计入观察载荷
```

这些字段只出现在适用操作。Data 保持 v4 的四个外层字段；证据链不进入 DOE。

## 边界及记录变化

| 项目 | 上轮 | 本轮 |
|---|---|---|
| DOE 版本 | skillflow-doe-input-v6 | skillflow-doe-input-v7 |
| 传播状态 | complete | complete |
| Data 数量 | 10 | 22 |
| sink 类型数量 | {'model_observe': 8, 'external_tool': 1, 'storage_write': 1} | {'model_observe': 10, 'external_tool': 1, 'storage_write': 1} |

| IR / 操作坐标 | 目标 | 类型 | 等级 |
|---|---|---|---|
| ir_001 / 1.0 | __compiled_model_context__ | model_observe | 2 |
| ir_003 / 0.0 | __compiled_model_context__ | model_observe | 2 |
| ir_004 / 0.0 | __compiled_model_context__ | model_observe | 2 |
| ir_005 / 0.0 | __compiled_model_context__ | model_observe | 2 |
| ir_007 / 0.0 | __compiled_model_context__ | model_observe | 2 |
| ir_007 / 1.0 | __compiled_model_context__ | model_observe | 2 |
| ir_007 / 2.0 | __compiled_model_context__ | model_observe | 2 |
| ir_007 / 4.0 | loc_index_search | external_tool | 2 |
| ir_007 / 6.0 | __compiled_model_context__ | model_observe | 2 |
| ir_009 / 0.0 | __compiled_model_context__ | model_observe | 2 |
| ir_010 / 0.0 | loc_count_txt | storage_write | 1 |
| ir_011 / 0.0 | __compiled_model_context__ | model_observe | 2 |

## 实际构造与控制关系

下表槽位来自新 DOE 本身；参数原值与存在性控制分开。抽象布尔保留出现／省略候选，不表示所有候选同时发出。

| IR / 操作 | 字段 | 原值槽及关系 | 条件槽及关系 |
|---|---|---|---|
| ir_007 / 3.0 | [&quot;query&quot;] | 0：原部分 [&quot;term&quot;] | null |
| ir_007 / 3.0 | [&quot;from_date&quot;] | 2：原部分 [&quot;from_date&quot;] | 1：opaque |
| ir_007 / 3.0 | [&quot;limit&quot;] | 4：原部分 [&quot;limit&quot;] | 3：opaque |

程序生成的条件观察记录：2 项。只有载荷槽进入 sink；确定省略时不生成实际 sink。

## 请求交付与响应获取

| IR | 交付参数关系 | 获取请求关系 | 是否复用同一实际绑定 |
|---|---|---|---|
| ir_007 | 0: known_parts、known_parts、known_parts、known_parts | 同左 | 是 |

## 仍需注意

文件加载、编译和传播一致不证明模型关系判断正确。具体漏标、误标及本轮剩余问题见 [助手复核](assistant-review.md)。

[新 DOE 原始文件](propagation/doe-input.json) · [数据与边界审查](propagation/report.html)

