# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`eb42bbe46e259c5d763583fa32da1a06aa52e10dfa955b71fc8b512b7f96037c`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read workflow inputs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_workflow_inputs | agent_runtime | source | context_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Verify GitHub CLI authentication

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | check_gh_auth_status | tool | source | context_read, model_observe |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Ask user to authenticate GitHub CLI

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | ask_user_to_run_gh_auth_login | llm | sink | user_output |
| ir_006 | return | agent_runtime | [] | [] |

### block_004 · Resolve the pull request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | resolve_pull_request | tool | source, sink, transformer | net_send, net_receive, transform, model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Run bundled inspect_pr_checks script

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_inspect_pr_checks | tool | source, sink, transformer | net_send, net_receive, transform, model_observe |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Report no failing checks and finish

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | return | agent_runtime | [] | [] |

### block_007 · Report script error and stop

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_012 | return | agent_runtime | [] | [] |

### block_008 · Inspect failing checks manually

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | inspect_pr_checks_manually | tool, llm | source, sink, transformer | net_send, net_receive, fs_write, transform, model_observe |
| ir_014 | dispatch | agent_runtime | [] | [] |

### block_009 · Scope non-GitHub Actions checks

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | scope_non_github_actions_checks | llm | transformer | transform, model_observe |
| ir_016 | dispatch | agent_runtime | [] | [] |

### block_010 · Summarize failures for the user

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | summarize_failure_context | llm | transformer | transform, model_observe |
| ir_018 | dispatch | agent_runtime | [] | [] |

### block_011 · Create a concise fix plan

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | create_fix_plan | llm | transformer | transform, model_observe |
| ir_020 | dispatch | agent_runtime | [] | [] |

### block_012 · Request explicit approval of the fix plan

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | request_plan_approval | llm | sink | user_output, model_observe |
| ir_022 | dispatch | agent_runtime | [] | [] |

### block_013 · Stop without implementing

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_023 | return | agent_runtime | [] | [] |

### block_014 · Implement the approved plan and report

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_024 | apply_approved_plan | llm | sink, transformer | fs_write, transform, model_observe |
| ir_025 | summarize_diffs_and_tests | llm | transformer | transform, model_observe |
| ir_026 | ask_about_opening_pull_request | llm | sink | user_output, model_observe |
| ir_027 | dispatch | agent_runtime | [] | [] |

### block_015 · Suggest rechecking tests and PR checks

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_028 | suggest_recheck_tests_and_gh_pr_checks | llm | sink, transformer | user_output, transform, model_observe |
| ir_029 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 从工作流上下文读取输入，属于本地代理运行时执行。

> read_workflow_inputs

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：把 repo/pr 输入引入当前过程。

> read_workflow_inputs

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取运行时调用者输入。

> read_workflow_inputs

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：通过 gh 工具检查认证状态。

> check_gh_auth_status

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：将认证状态引入当前过程。

> check_gh_auth_status

- `effects` / `context_read`；依据 `source`，位置 `src_044`。
  理由：检查运行环境中的 GitHub CLI 认证上下文。

> gh auth status

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果按执行模型默认回传模型上下文。

> 默认进入 LLM 上下文

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_005

- `actor` / `llm`；依据 `cfg`，位置 `g_0021`。
  理由：该动作由模型生成并发出对用户的请求。

> ask_user_to_run_gh_auth_login

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：请求内容到达用户可见边界。

> ask the user to run `gh auth login`

- `effects` / `user_output`；依据 `source`，位置 `src_044`。
  理由：直接向用户展示操作请求。

> ask the user to run `gh auth login`

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：return 是运行时控制流操作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：普通 return 未记录引入、外发、存储或变换内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：普通 return 不证明用户输出或其他词表效果。

> return

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：使用 gh 工具解析 PR。

> resolve_pull_request

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：取得 PR 信息并引入当前过程。

> resolve_pull_request

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：查询请求到达远端 GitHub。

> gh pr view --json number,url

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：选择或解析出 resolved_pr。

> resolve_pull_request

- `effects` / `net_send`；依据 `source`，位置 `src_044`。
  理由：gh pr view 会向 GitHub 发送查询请求。

> gh pr view --json number,url

- `effects` / `net_receive`；依据 `source`，位置 `src_044`。
  理由：同一查询接收 PR 信息。

> gh pr view --json number,url

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：解析或选择 PR 表示。

> resolve_pull_request

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传模型上下文。

> 默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：运行脚本工具检查 PR checks。

> run_inspect_pr_checks

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：取得检查与日志内容。

> run_inspect_pr_checks

- `roles` / `sink`；依据 `source`，位置 `src_047`。
  理由：向 GitHub 发送检查或日志请求。

> Fetch failing PR checks, pull GitHub Actions logs

- `roles` / `transformer`；依据 `source`，位置 `src_047`。
  理由：解析并提取失败片段。

> extract a failure snippet

- `effects` / `net_send`；依据 `source`，位置 `src_047`。
  理由：拉取日志会向远端发起请求。

> Fetch failing PR checks, pull GitHub Actions logs

- `effects` / `net_receive`；依据 `source`，位置 `src_047`。
  理由：接收 GitHub Actions 日志或检查数据。

> Fetch failing PR checks, pull GitHub Actions logs

- `effects` / `transform`；依据 `source`，位置 `src_047`。
  理由：提取或组合失败片段。

> extract a failure snippet

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本输出默认回传模型上下文。

> 默认进入 LLM 上下文

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：return 是运行时控制流操作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0039`。
  理由：普通 return 未记录引入、外发、存储或变换内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0039`。
  理由：普通 return 不证明用户输出或其他词表效果。

> return

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0044`。
  理由：return 是运行时控制流操作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0044`。
  理由：普通 return 未记录引入、外发、存储或变换内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0044`。
  理由：普通 return 不证明用户输出或其他词表效果。

> return

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0049`。
  理由：使用 gh 工具执行手动检查命令。

> gh

- `actor` / `llm`；依据 `cfg`，位置 `g_0049`。
  理由：手动检查并生成报告需要模型读取日志或元数据。

> inspect_pr_checks_manually

- `roles` / `source`；依据 `cfg`，位置 `g_0049`。
  理由：取得手动检查报告内容。

> inspect_pr_checks_manually

- `roles` / `sink`；依据 `cfg`，位置 `g_0049`。
  理由：可能将日志写入本地路径，也使命令请求到达远端。

> > "<path>"

- `roles` / `transformer`；依据 `cfg`，位置 `g_0049`。
  理由：提取运行 ID 或日志并生成报告。

> inspect_pr_checks_manually

- `effects` / `net_send`；依据 `source`，位置 `src_044`。
  理由：执行 gh 命令向 GitHub 请求日志。

> gh run view <run_id> --log

- `effects` / `net_receive`；依据 `source`，位置 `src_044`。
  理由：接收运行日志。

> gh run view <run_id> --log

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0049`。
  理由：重定向输出到路径会写入文件内容。

> > "<path>"

- `effects` / `transform`；依据 `cfg`，位置 `g_0049`。
  理由：提取或整理检查信息为报告。

> inspect_pr_checks_manually

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：手动检查时模型读取日志或元数据并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0050`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0050`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0050`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_015

- `actor` / `llm`；依据 `cfg`，位置 `g_0055`。
  理由：分类或标注外部检查需要模型处理。

> scope_non_github_actions_checks

- `roles` / `transformer`；依据 `cfg`，位置 `g_0055`。
  理由：筛选或分类检查来源。

> scope_non_github_actions_checks

- `effects` / `transform`；依据 `cfg`，位置 `g_0055`。
  理由：选择并分类 GitHub Actions 与外部检查。

> scope_non_github_actions_checks

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取检查输出并判断范围。

> 模型实际读取内容并处理时还标注 model_observe

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0056`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0056`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0056`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_017

- `actor` / `llm`；依据 `cfg`，位置 `g_0061`。
  理由：摘要失败上下文由模型执行。

> summarize_failure_context

- `roles` / `transformer`；依据 `cfg`，位置 `g_0061`。
  理由：对失败信息进行摘要或组合。

> summarize_failure_context

- `effects` / `transform`；依据 `cfg`，位置 `g_0061`。
  理由：生成 failure_summary 表示。

> summarize_failure_context

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取失败上下文并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_018

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0062`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0062`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0062`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_019

- `actor` / `llm`；依据 `cfg`，位置 `g_0067`。
  理由：创建修复计划由模型生成。

> create_fix_plan

- `roles` / `transformer`；依据 `cfg`，位置 `g_0067`。
  理由：基于失败摘要生成计划。

> create_fix_plan

- `effects` / `transform`；依据 `cfg`，位置 `g_0067`。
  理由：生成 fix_plan 表示。

> create_fix_plan

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取 failure_summary 并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_020

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0068`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0068`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0068`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_021

- `actor` / `llm`；依据 `cfg`，位置 `g_0073`。
  理由：向用户请求批准由模型生成。

> request_plan_approval

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：请求内容到达用户可见边界。

> request approval

- `effects` / `user_output`；依据 `source`，位置 `src_044`。
  理由：直接向用户请求批准。

> request approval

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取 fix_plan 以形成批准请求。

> 模型实际读取内容并处理时还标注 model_observe

### ir_022

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0074`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0074`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0074`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_023

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0079`。
  理由：return 是运行时控制流操作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0079`。
  理由：普通 return 未记录引入、外发、存储或变换内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0079`。
  理由：普通 return 不证明用户输出或其他词表效果。

> return

### ir_024

- `actor` / `llm`；依据 `cfg`，位置 `g_0084`。
  理由：应用已批准计划由模型或代理执行。

> apply_approved_plan

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：应用计划会修改或存储文件内容。

> Apply the approved plan

- `roles` / `transformer`；依据 `cfg`，位置 `g_0084`。
  理由：按计划改变代码内容。

> apply_approved_plan

- `effects` / `fs_write`；依据 `source`，位置 `src_044`。
  理由：实施代码修改会写入文件。

> Apply the approved plan

- `effects` / `transform`；依据 `cfg`，位置 `g_0084`。
  理由：按计划改变代码表示或内容。

> apply_approved_plan

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取计划与批准结果并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_025

- `actor` / `llm`；依据 `cfg`，位置 `g_0085`。
  理由：总结 diffs 和 tests 由模型完成。

> summarize_diffs_and_tests

- `roles` / `transformer`；依据 `cfg`，位置 `g_0085`。
  理由：摘要或组合实现信息。

> summarize_diffs_and_tests

- `effects` / `transform`；依据 `cfg`，位置 `g_0085`。
  理由：生成 implementation_report。

> summarize_diffs_and_tests

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取实现摘要并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_026

- `actor` / `llm`；依据 `cfg`，位置 `g_0086`。
  理由：询问用户是否开 PR 由模型生成。

> ask_about_opening_pull_request

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：询问内容到达用户可见边界。

> ask about opening a PR

- `effects` / `user_output`；依据 `source`，位置 `src_044`。
  理由：直接向用户提问。

> ask about opening a PR

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取 implementation_report 以形成询问。

> 模型实际读取内容并处理时还标注 model_observe

### ir_027

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0087`。
  理由：dispatch 是运行时控制流操作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0087`。
  理由：仅控制流转，不引入、外发、存储或变换内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0087`。
  理由：纯控制操作，无词表效果。

> dispatch

### ir_028

- `actor` / `llm`；依据 `cfg`，位置 `g_0092`。
  理由：生成复查建议由模型完成。

> suggest_recheck_tests_and_gh_pr_checks

- `roles` / `sink`；依据 `source`，位置 `src_044`。
  理由：建议到达用户可见边界。

> suggest re-running the relevant tests and `gh pr checks`

- `roles` / `transformer`；依据 `cfg`，位置 `g_0092`。
  理由：组合信息为复查建议。

> suggest_recheck_tests_and_gh_pr_checks

- `effects` / `user_output`；依据 `source`，位置 `src_044`。
  理由：直接向用户提供建议。

> suggest re-running the relevant tests and `gh pr checks`

- `effects` / `transform`；依据 `cfg`，位置 `g_0092`。
  理由：生成或组合建议表示。

> suggest_recheck_tests_and_gh_pr_checks

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取实现报告或上下文并处理。

> 模型实际读取内容并处理时还标注 model_observe

### ir_029

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0093`。
  理由：return 是运行时控制流操作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0093`。
  理由：普通 return 未记录引入、外发、存储或变换内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0093`。
  理由：普通 return 不证明用户输出或其他词表效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
