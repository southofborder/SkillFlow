# 027 首轮复核准备（非终态结论）

已读完整 frozen SKILL.md、inspect_pr_checks.py、openai.yaml；已读 r000 非 represented 核对项与相关实际块。最终评审必须绑定终态图，不能把本笔记作为最终通过结论。

- finding_9 要求显式保留手动 fallback，具有源文依据：首选脚本不等于外层 manual fallback 已被表达。脚本内部 field drift / job-log fallback 的嵌入源码不能自动覆盖手动替代执行路径。
- finding_5 要求 repo 默认 `.` 与 pr 可选/当前分支明确，但其“后续解析或源码不能替代读取点声明”的严格性需结合全图判断，不能假设只能在读取点表示默认。
- finding_11 把名为 inspection_report 的 result_006 认定为失败报告，可能过度依赖 semantic_name。实际 run_inspect_pr_checks 产生同一 result_006 和 exit_code result_007；exit0 时 source 脚本 stdout 就是 no failing checks 消息，return result_006 未必返回了错误身份。图未规定 stdout/完整工具响应对应关系，宜标为解释边界，不能仅凭标签断言错转。
- finding_16 指未批准时 return fix_plan 是新增。需区分 IR 内部返回与额外向用户输出：前一步 request_plan_approval 已经接收 fix_plan，空返回或计划返回在源文未明确指定，停止执行的控制边界本身有依据。保留疑似过严反馈边界，不擅自改模型判定。
