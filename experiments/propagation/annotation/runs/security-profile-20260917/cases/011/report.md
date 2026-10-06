# 安全语义标注：011

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`98b06262b8dee415afcb2e957df248f55d3e72264f5537099bd3582ddb14543e`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_file | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Inspect request fields and optional-parameter presence

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_request_term | 未接受 | 未接受 | 未接受 |
| ir_004 | check_from_date_present | 未接受 | 未接受 | 未接受 |
| ir_005 | check_limit_present | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Extract from_date because it is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | extract_from_date_value | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Omit from_date argument because it is missing

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Check whether limit is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Extract limit because it is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | extract_limit_value | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Omit limit argument because it is missing

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Call index.search with the request term and optional parameters

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | index.search | 未接受 | 未接受 | 未接受 |
| ir_015 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Return the search response's items value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | extract_search_response_items | 未接受 | 未接受 | 未接受 |
| ir_017 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
