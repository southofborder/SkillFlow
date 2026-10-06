# 安全语义标注：010

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`f83140faa06b5affcb00d1f1e8444317eb6f7a29581d65f6e4614d43cce080ce`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Extract term and check optional parameter presence

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | 未接受 | 未接受 | 未接受 |
| ir_004 | check_from_date_present | 未接受 | 未接受 | 未接受 |
| ir_005 | check_limit_present | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Extract present from_date and limit values

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_from_date_value | 未接受 | 未接受 | 未接受 |
| ir_008 | extract_limit_value | 未接受 | 未接受 | 未接受 |
| ir_009 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Call index.search with term, from_date, and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | index.search | 未接受 | 未接受 | 未接受 |
| ir_011 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_013 | return | 未接受 | 未接受 | 未接受 |

### block_006 · Extract present from_date value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | extract_from_date_value | 未接受 | 未接受 | 未接受 |
| ir_015 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Call index.search with term and from_date

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | index.search | 未接受 | 未接受 | 未接受 |
| ir_017 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_019 | return | 未接受 | 未接受 | 未接受 |

### block_009 · Extract present limit value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | extract_limit_value | 未接受 | 未接受 | 未接受 |
| ir_021 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Call index.search with term and limit

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | index.search | 未接受 | 未接受 | 未接受 |
| ir_023 | dispatch | 未接受 | 未接受 | 未接受 |

### block_011 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_024 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_025 | return | 未接受 | 未接受 | 未接受 |

### block_012 · Call index.search with term only

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_026 | index.search | 未接受 | 未接受 | 未接受 |
| ir_027 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_028 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_029 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
