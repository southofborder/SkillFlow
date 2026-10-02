# 安全语义标注：029

状态：**响应无效**（`invalid_response`）

evidence quote does not match source location src_047

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`7a3d418576071d8fc03384dc7efd65c49a9024f8ef47b7b4764c5e47e91030a4`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- evidence quote does not match source location src_047

## 按块查看

### block_001 · Check Linear MCP connection

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | check_linear_mcp_connection | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Set up Linear MCP

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | add_linear_mcp_server | 未接受 | 未接受 | 未接受 |
| ir_004 | enable_codex_remote_mcp_client | 未接受 | 未接受 | 未接受 |
| ir_005 | login_linear_oauth | 未接受 | 未接受 | 未接受 |
| ir_006 | return | 未接受 | 未接受 | 未接受 |

### block_003 · Read the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | read_user_request | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Clarify the user's goal and scope

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | clarify_user_goal_and_scope | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Confirm identifiers and select the Linear workflow

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | confirm_required_linear_identifiers | 未接受 | 未接受 | 未接受 |
| ir_012 | select_linear_workflow_and_tools | 未接受 | 未接受 | 未接受 |
| ir_013 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · List open issues for the target team

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | list_open_issues_for_team | 未接受 | 未接受 | 未接受 |
| ir_015 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Pick top issues and create a cycle with assignments

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_016 | pick_top_issues_by_priority | 未接受 | 未接受 | 未接受 |
| ir_017 | create_linear_cycle | 未接受 | 未接受 | 未接受 |
| ir_018 | assign_issues_to_cycle | 未接受 | 未接受 | 未接受 |
| ir_019 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · List critical and high-priority bugs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_020 | list_critical_high_priority_bugs | 未接受 | 未接受 | 未接受 |
| ir_021 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Rank bugs and move top items to In Progress

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | rank_bugs_by_user_impact | 未接受 | 未接受 | 未接受 |
| ir_023 | move_top_bugs_to_in_progress | 未接受 | 未接受 | 未接受 |
| ir_024 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Search Linear documentation

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_025 | search_linear_documentation | 未接受 | 未接受 | 未接受 |
| ir_026 | dispatch | 未接受 | 未接受 | 未接受 |

### block_011 · Analyze gaps and open documentation issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_027 | analyze_documentation_gaps | 未接受 | 未接受 | 未接受 |
| ir_028 | create_documentation_issues | 未接受 | 未接受 | 未接受 |
| ir_029 | dispatch | 未接受 | 未接受 | 未接受 |

### block_012 · List active issues for workload balance

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_030 | list_active_issues | 未接受 | 未接受 | 未接受 |
| ir_031 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Group issues by assignee and suggest redistributions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_032 | group_active_issues_by_assignee | 未接受 | 未接受 | 未接受 |
| ir_033 | flag_high_load_assignees | 未接受 | 未接受 | 未接受 |
| ir_034 | suggest_or_apply_redistributions | 未接受 | 未接受 | 未接受 |
| ir_035 | dispatch | 未接受 | 未接受 | 未接受 |

### block_014 · Create release project, milestones, and issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_036 | create_linear_project | 未接受 | 未接受 | 未接受 |
| ir_037 | create_project_milestones | 未接受 | 未接受 | 未接受 |
| ir_038 | create_release_issues_with_estimates | 未接受 | 未接受 | 未接受 |
| ir_039 | dispatch | 未接受 | 未接受 | 未接受 |

### block_015 · Find blocked issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_040 | find_blocked_issues | 未接受 | 未接受 | 未接受 |
| ir_041 | dispatch | 未接受 | 未接受 | 未接受 |

### block_016 · Identify blockers and create linked issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_042 | identify_blockers | 未接受 | 未接受 | 未接受 |
| ir_043 | create_linked_issues_if_missing | 未接受 | 未接受 | 未接受 |
| ir_044 | dispatch | 未接受 | 未接受 | 未接受 |

### block_017 · Find my issues with stale updates

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_045 | list_my_issues_with_stale_updates | 未接受 | 未接受 | 未接受 |
| ir_046 | dispatch | 未接受 | 未接受 | 未接受 |

### block_018 · Add status comments based on current state and blockers

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_047 | compute_status_comments | 未接受 | 未接受 | 未接受 |
| ir_048 | create_issue_comments | 未接受 | 未接受 | 未接受 |
| ir_049 | dispatch | 未接受 | 未接受 | 未接受 |

### block_019 · List unlabeled issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_050 | list_unlabeled_issues | 未接受 | 未接受 | 未接受 |
| ir_051 | dispatch | 未接受 | 未接受 | 未接受 |

### block_020 · Analyze labels, apply labels, and create missing categories

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_052 | analyze_unlabeled_issues_for_labels | 未接受 | 未接受 | 未接受 |
| ir_053 | apply_labels_to_issues | 未接受 | 未接受 | 未接受 |
| ir_054 | create_missing_label_categories | 未接受 | 未接受 | 未接受 |
| ir_055 | dispatch | 未接受 | 未接受 | 未接受 |

### block_021 · Get the last completed cycle

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_056 | get_last_completed_cycle | 未接受 | 未接受 | 未接受 |
| ir_057 | dispatch | 未接受 | 未接受 | 未接受 |

### block_022 · Generate retrospective report and open discussion issues

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_058 | generate_sprint_retrospective_report | 未接受 | 未接受 | 未接受 |
| ir_059 | open_discussion_issues_for_patterns | 未接受 | 未接受 | 未接受 |
| ir_060 | dispatch | 未接受 | 未接受 | 未接受 |

### block_023 · Summarize results and propose next actions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_061 | summarize_linear_workflow_results | 未接受 | 未接受 | 未接受 |
| ir_062 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
