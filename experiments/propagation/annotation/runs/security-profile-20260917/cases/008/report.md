# 安全语义标注：008

状态：**调用执行错误**（`execution_error`）

LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`72a5cb3a4185174407fd2344b1dc0c6147b91b997a3691c614a9f97d52c40848`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed>

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Parse request fields and presence flags

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | parse_request_json | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Check whether from_date is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Extract the from_date value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_006 | extract_request_from_date | 未接受 | 未接受 | 未接受 |
| ir_007 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Check whether limit is present

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Extract the limit value

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | extract_request_limit | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Call index.search with the request parameters

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | index.search | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Write total to count.txt and return items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | extract_response_total | 未接受 | 未接受 | 未接受 |
| ir_014 | extract_response_items | 未接受 | 未接受 | 未接受 |
| ir_015 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_016 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
