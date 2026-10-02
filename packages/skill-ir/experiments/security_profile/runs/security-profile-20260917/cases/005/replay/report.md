# 安全语义标注：005

状态：**调用执行错误**（`execution_error`）

IncompleteRead(0 bytes read)

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`ae559ebb1cab8c191397594ec2611eef76464711ddbc9bdd65f724c92aae04a4`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- IncompleteRead(0 bytes read)

## 按块查看

### block_001 · Read the user-provided events.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_events_json | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Get next event record and check whether more records remain

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | get_next_event_record | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Evaluate whether the current event is selected

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_event_selection_fields | 未接受 | 未接受 | 未接受 |
| ir_006 | check_event_selection | 未接受 | 未接受 | 未接受 |
| ir_007 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Send notification for the selected event

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | extract_event_notification_fields | 未接受 | 未接受 | 未接受 |
| ir_009 | notify_send | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Finish after all event records are processed

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
