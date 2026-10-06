# 安全语义标注：annotation

状态：**调用执行错误**（`execution_error`）

本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。

统一抽象运行时契约：`skillflow-abstract-runtime-v1`；摘要：`d11080a8cf7879c3a0d01d6bf9b403f8fb0ed4ef4d16d5ed49b88bd2333712c0`。

LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`

[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_user_request | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_presence | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Classify the first fast.fetch attempt

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_009 | classify_fast_fetch_outcome | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_011 | fast.fetch | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Classify the fast.fetch retry

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_013 | classify_fast_fetch_outcome | 未接受 | 未接受 | 未接受 |
| ir_014 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Call archive.fetch with source_id only

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_015 | archive.fetch | 未接受 | 未接受 | 未接受 |
| ir_016 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Classify the archive.fetch result

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_017 | classify_fetch_outcome | 未接受 | 未接受 | 未接受 |
| ir_018 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Append status and return the first fast.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_local_status_file | 未接受 | 未接受 | 未接受 |
| ir_020 | return | 未接受 | 未接受 | 未接受 |

### block_011 · Append status and return the fast.fetch retry body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_021 | append_final_status_to_local_status_file | 未接受 | 未接受 | 未接受 |
| ir_022 | return | 未接受 | 未接受 | 未接受 |

### block_012 · Append status and return the archive.fetch body

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_023 | append_final_status_to_local_status_file | 未接受 | 未接受 | 未接受 |
| ir_024 | return | 未接受 | 未接受 | 未接受 |

### block_013 · Append status and return the archive.fetch error

| IR | 动作 | 执行主体（operator） | roles | effects |
|---|---|---|---|---|
| ir_025 | append_final_status_to_local_status_file | 未接受 | 未接受 | 未接受 |
| ir_026 | return | 未接受 | 未接受 | 未接受 |

## 符号传播说明

以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。


## 标注依据

## 分析边界

这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。
effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。
context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。
空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
