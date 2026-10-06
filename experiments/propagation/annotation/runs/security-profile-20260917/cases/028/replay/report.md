# 安全语义标注：028

状态：**响应无效**（`invalid_response`）

evidence quote does not match source location src_062

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`0fa8b5562c1ad1c3156881b9e9e1d8718cca0aaf707c8fb1627921b499b16bd1`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- evidence quote does not match source location src_062

## 按块查看

### block_001 · Check Netlify CLI authentication status

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | run_netlify_status | 未接受 | 未接受 | 未接受 |
| ir_002 | dispatch | 未接受 | 未接受 | 未接受 |

### block_002 · Determine whether Netlify CLI is authenticated

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | check_netlify_authentication | 未接受 | 未接受 | 未接受 |
| ir_004 | dispatch | 未接受 | 未接受 | 未接受 |

### block_003 · Guide user through Netlify login

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | run_netlify_login | 未接受 | 未接受 | 未接受 |
| ir_006 | dispatch | 未接受 | 未接受 | 未接受 |

### block_004 · Detect site link status from Netlify status output

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | determine_site_link_status | 未接受 | 未接受 | 未接受 |
| ir_008 | dispatch | 未接受 | 未接受 | 未接受 |

### block_005 · Read Git remote origin

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | git_remote_show_origin | 未接受 | 未接受 | 未接受 |
| ir_010 | dispatch | 未接受 | 未接受 | 未接受 |

### block_006 · Extract Git remote URL and determine if project is Git-based

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | extract_git_remote_url | 未接受 | 未接受 | 未接受 |
| ir_012 | dispatch | 未接受 | 未接受 | 未接受 |

### block_007 · Link project to existing Netlify site by Git remote URL

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | netlify_link_git_remote | 未接受 | 未接受 | 未接受 |
| ir_014 | dispatch | 未接受 | 未接受 | 未接受 |

### block_008 · Create and link new Netlify site interactively

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | run_netlify_init | 未接受 | 未接受 | 未接受 |
| ir_016 | dispatch | 未接受 | 未接受 | 未接受 |

### block_009 · Read project package.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | read_project_package_json | 未接受 | 未接受 | 未接受 |
| ir_018 | dispatch | 未接受 | 未接受 | 未接受 |

### block_010 · Detect framework and package manager from package.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | detect_framework_and_package_manager | 未接受 | 未接受 | 未接受 |
| ir_020 | dispatch | 未接受 | 未接受 | 未接受 |

### block_011 · Install project dependencies

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | install_project_dependencies | 未接受 | 未接受 | 未接受 |
| ir_022 | dispatch | 未接受 | 未接受 | 未接受 |

### block_012 · Read user request for deployment context

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_023 | read_user_request | 未接受 | 未接受 | 未接受 |
| ir_024 | dispatch | 未接受 | 未接受 | 未接受 |

### block_013 · Choose preview or production deployment

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_025 | determine_deployment_type | 未接受 | 未接受 | 未接受 |
| ir_026 | dispatch | 未接受 | 未接受 | 未接受 |

### block_014 · Deploy preview to Netlify

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_027 | run_netlify_deploy | 未接受 | 未接受 | 未接受 |
| ir_028 | dispatch | 未接受 | 未接受 | 未接受 |

### block_015 · Deploy to production on Netlify

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_029 | run_netlify_deploy_prod | 未接受 | 未接受 | 未接受 |
| ir_030 | dispatch | 未接受 | 未接受 | 未接受 |

### block_016 · Rerun deployment with escalated network permissions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_031 | run_netlify_deploy_escalated | 未接受 | 未接受 | 未接受 |
| ir_032 | dispatch | 未接受 | 未接受 | 未接受 |

### block_017 · Handle deployment failure

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_033 | check_build_configuration | 未接受 | 未接受 | 未接受 |
| ir_034 | verify_dependencies | 未接受 | 未接受 | 未接受 |
| ir_035 | review_build_logs | 未接受 | 未接受 | 未接受 |
| ir_036 | verify_publish_directory | 未接受 | 未接受 | 未接受 |
| ir_037 | format_deployment_error_report | 未接受 | 未接受 | 未接受 |
| ir_038 | return | 未接受 | 未接受 | 未接受 |

### block_018 · Report deployment results to user

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_039 | format_deployment_report | 未接受 | 未接受 | 未接受 |
| ir_040 | return | 未接受 | 未接受 | 未接受 |

## 标注依据

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
