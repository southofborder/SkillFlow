# 安全语义标注：annotation

状态：**调用执行错误**（`execution_error`）

IncompleteRead(0 bytes read)

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`7f279b8a538fe90b7270ad0f98a2254a4b1787df96e459d9df8926cb2b50a832`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- IncompleteRead(0 bytes read)

## 按块查看

### block_001 · Read the user's request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_user_request | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Check whether Linear MCP is already configured

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_linear_mcp_configuration_status | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Add the Linear MCP server

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | add_linear_mcp_server | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Choose how to enable the remote MCP client

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Enable remote MCP client in config.toml

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_008 | set_config_toml_rmcp_client_true | 未接受 | 未接受 | 未接受 |
| ir_009 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Enable remote MCP client with Codex CLI

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_010 | run_codex_enable_rmcp_client | 未接受 | 未接受 | 未接受 |
| ir_011 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Log in to Linear MCP with OAuth

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | login_linear_mcp_oauth | 未接受 | 未接受 | 未接受 |
| ir_013 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Tell the user to restart Codex after successful login

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_014 | return | 未接受 | 未接受 | 未接受 |

### block_009 · Clarify the user's goal and scope

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | clarify_linear_goal_and_scope | 未接受 | 未接受 | 未接受 |
| ir_016 | confirm_linear_scope_details | 未接受 | 未接受 | 未接受 |
| ir_017 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Select the Linear workflow and identify required MCP tools

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_018 | select_linear_workflow | 未接受 | 未接受 | 未接受 |
| ir_019 | identify_linear_mcp_tools | 未接受 | 未接受 | 未接受 |
| ir_020 | confirm_linear_identifiers | 未接受 | 未接受 | 未接受 |
| ir_021 | dispatch | 未接受 | 未接受 | 未接受 |

### block_011 · Read Linear context with MCP read tools

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_022 | call_linear_mcp_read_tools | 未接受 | 未接受 | 未接受 |
| ir_023 | dispatch | 未接受 | 未接受 | 未接受 |

### block_012 · Check whether the apply step is a bulk operation

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_024 | check_bulk_operation | 未接受 | 未接受 | 未接受 |
| ir_025 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Explain grouping logic for bulk operations

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_026 | explain_grouping_logic | 未接受 | 未接受 | 未接受 |
| ir_027 | dispatch | 未接受 | 未接受 | 未接受 |

### block_014 · Create or update Linear entities with MCP write tools

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_028 | call_linear_mcp_write_tools | 未接受 | 未接受 | 未接受 |
| ir_029 | dispatch | 未接受 | 未接受 | 未接受 |

### block_015 · Summarize results, call out gaps, and propose next actions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_030 | summarize_linear_workflow_results | 未接受 | 未接受 | 未接受 |
| ir_031 | identify_remaining_gaps_or_blockers | 未接受 | 未接受 | 未接受 |
| ir_032 | propose_next_actions | 未接受 | 未接受 | 未接受 |
| ir_033 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
