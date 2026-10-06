# 安全语义标注：012

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`1f999bebb7d9886521f135638917d87f569bb8046eb96d975610fe30348c820c`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Extract the request term and check whether from_date is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | 未接受 | 未接受 | 未接受 |
| ir_004 | check_from_date_presence | 未接受 | 未接受 | 未接受 |
| ir_005 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Extract the from_date value when it is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_006 | extract_from_date_value | 未接受 | 未接受 | 未接受 |
| ir_007 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Check whether the limit parameter is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | check_limit_presence | 未接受 | 未接受 | 未接受 |
| ir_009 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Use the request's limit value unchanged

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | extract_request_limit | 未接受 | 未接受 | 未接受 |
| ir_011 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Use the default limit value 10

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | use_default_limit | 未接受 | 未接受 | 未接受 |
| ir_013 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Resolve the final limit argument

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | resolve_limit_argument | 未接受 | 未接受 | 未接受 |
| ir_015 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Call index.search exactly once with the resolved arguments

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | index.search | 未接受 | 未接受 | 未接受 |
| ir_017 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Write the search response total to count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | extract_search_total | 未接受 | 未接受 | 未接受 |
| ir_019 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_020 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Return the search response items unchanged

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | extract_search_items | 未接受 | 未接受 | 未接受 |
| ir_022 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
