# 安全语义标注：027

状态：**调用执行错误**（`execution_error`）

IncompleteRead(0 bytes read)

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`55d555b1539a27b59e6ef2e354cbb51098911e48613fc611d71b24054c1b7123`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- IncompleteRead(0 bytes read)

## 按块查看

### block_001 · Read skill inputs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_skill_inputs | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Verify gh authentication

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | check_gh_auth_status | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Ask user to authenticate

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | ask_user_to_run_gh_auth_login | 未接受 | 未接受 | 未接受 |
| ir_006 | return | 未接受 | 未接受 | 未接受 |

### block_004 · Choose inspection method

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | select_inspection_method | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Run bundled inspect_pr_checks.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_inspect_pr_checks_script | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Run manual gh commands to inspect failing checks

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | inspect_pr_checks_manually | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Check whether failing checks were found

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Report no failing checks

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | return | 未接受 | 未接受 | 未接受 |

### block_009 · Summarize failures for the user

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | summarize_failure_context | 未接受 | 未接受 | 未接受 |
| ir_016 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Create a fix plan

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | draft_fix_plan | 未接受 | 未接受 | 未接受 |
| ir_018 | request_plan_approval | 未接受 | 未接受 | 未接受 |
| ir_019 | dispatch | 未接受 | 未接受 | 未接受 |

### block_011 · Read user approval

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | read_user_approval | 未接受 | 未接受 | 未接受 |
| ir_021 | dispatch | 未接受 | 未接受 | 未接受 |

### block_012 · Implement approved fix plan

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | implement_fix_plan | 未接受 | 未接受 | 未接受 |
| ir_023 | summarize_diffs_and_tests | 未接受 | 未接受 | 未接受 |
| ir_024 | ask_about_opening_pr | 未接受 | 未接受 | 未接受 |
| ir_025 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Suggest rechecking status

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_026 | suggest_rechecking_tests_and_checks | 未接受 | 未接受 | 未接受 |
| ir_027 | return | 未接受 | 未接受 | 未接受 |

### block_014 · Return without implementing

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_028 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
