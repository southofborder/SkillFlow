# 安全语义标注：018

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`38f2dc7c372deae5b83832754fdf413362767a925b8f4ca90448283e5d8c13c9`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

## 按块查看

### block_001 · Read source_id from the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_source_id_from_user_request | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Read FAST_KEY from the environment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_fast_key_from_environment | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Check whether FAST_KEY is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | check_fast_key_present | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Try fast.fetch with source_id and FAST_KEY

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | fast.fetch | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Retry fast.fetch once after a transient first failure

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | fast.fetch | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Call archive.fetch with source_id

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | archive.fetch | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Append final status and return fast.fetch summary

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | append_final_status_to_local_status_txt | 未接受 | 未接受 | 未接受 |
| ir_014 | return | 未接受 | 未接受 | 未接受 |

### block_008 · Append final status and return retry fast.fetch summary

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | append_final_status_to_local_status_txt | 未接受 | 未接受 | 未接受 |
| ir_016 | return | 未接受 | 未接受 | 未接受 |

### block_009 · Append final status and return archive.fetch summary

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | append_final_status_to_local_status_txt | 未接受 | 未接受 | 未接受 |
| ir_018 | return | 未接受 | 未接受 | 未接受 |

### block_010 · Append final status and return archive.fetch error

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | append_final_status_to_local_status_txt | 未接受 | 未接受 | 未接受 |
| ir_020 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
