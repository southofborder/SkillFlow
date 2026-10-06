# 安全语义标注：013

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`0d9ebf8762a201c2abf693071b0e77f6b6a6e72ec846eb36e6f514633730431c`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_request | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_presence | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | call_fast_fetch | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Check whether the first fast.fetch attempt succeeded

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | check_fast_fetch_success | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Append success status and return the first fast.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | append_final_status_to_status_file | 未接受 | 未接受 | 未接受 |
| ir_012 | return | 未接受 | 未接受 | 未接受 |

### block_007 · Check whether the first fast.fetch failure was transient

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | check_transient_error | 未接受 | 未接受 | 未接受 |
| ir_014 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Retry fast.fetch once

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | retry_fast_fetch | 未接受 | 未接受 | 未接受 |
| ir_016 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Check whether the fast.fetch retry succeeded

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | check_fast_fetch_success | 未接受 | 未接受 | 未接受 |
| ir_018 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Append success status and return the fast.fetch retry response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_status_file | 未接受 | 未接受 | 未接受 |
| ir_020 | return | 未接受 | 未接受 | 未接受 |

### block_011 · Call archive.fetch once with source_id

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | call_archive_fetch | 未接受 | 未接受 | 未接受 |
| ir_022 | dispatch | 未接受 | 未接受 | 未接受 |

### block_012 · Check whether archive.fetch succeeded

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_023 | check_archive_fetch_success | 未接受 | 未接受 | 未接受 |
| ir_024 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Append success status and return the archive.fetch response body

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_025 | append_final_status_to_status_file | 未接受 | 未接受 | 未接受 |
| ir_026 | return | 未接受 | 未接受 | 未接受 |

### block_014 · Append failure status and return the archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_027 | append_final_status_to_status_file | 未接受 | 未接受 | 未接受 |
| ir_028 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
