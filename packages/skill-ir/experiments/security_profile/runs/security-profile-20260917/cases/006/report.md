# 安全语义标注：006

状态：**调用执行错误**（`execution_error`）

IncompleteRead(0 bytes read)

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`4e7688fa5cd486d5f92a0f6edb3c3be4b95a6f070811e7624daaf419d0fdf533`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- IncompleteRead(0 bytes read)

## 按块查看

### block_001 · Read events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Select records eligible for notification

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | select_notifiable_records | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Extract notification payloads

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_notification_payloads | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Send notifications for selected records

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | notify_send_for_selected_records | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Count processed records

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | count_processed_records | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Write processed count to count.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | write_count_file | 未接受 | 未接受 | 未接受 |
| ir_012 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
