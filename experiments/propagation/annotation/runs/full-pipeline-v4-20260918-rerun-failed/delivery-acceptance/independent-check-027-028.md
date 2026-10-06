# 027 / 028 助手意见独立核实

本记录仅核对外置助手意见的关键结论，未改原始结果、模型响应或实验状态，未调用 API。复核者为助手，不是用户人工确认。

- **027 返回层次问题有依据。**实际脚本 `main()` 无失败时向 stdout 打印消息、返回整数 0，并经 `SystemExit(main())` 作为进程退出码。第 1 轮 finding_7 明确用“脚本 main 只返回 0”要求从外层 CFG return 移除 inspection_output，这跨越了工具进程与 Skill 返回接口。外层允许返回工具输出还是退出码必须先固定；当前助手意见使用“可能过严”而未断言哪个抽象必然正确，措辞适当。
- **027 ir_017 用户输出疑似漏标有源文支持。**SKILL.md 工作流第 5 步明文 `Summarize failures for the user.`；末图 block_010 有摘要操作和结果，但 ir_017 profile 只有 transformer、transform/model_observe。可以列为优先核实的边界遗漏，不能仅凭块标题宣称一定执行了用户展示。
- **已收紧一处相近问题。**ir_025 的 implementation_report 实际流向 ir_026，而 ir_026 已标 user_output。已修改外置 027 评审相应一句，说明用户展示可能由后续询问操作承担，不能直接把 ir_025 本身没有 user_output 判成漏标。模型原始记录保持不变。
- **028 package.json 检测遗漏有依据。**源文要求尽可能从 package.json 检测框架并建议设置；实际 ir_020 只记录 CLI 从 netlify.toml/提示取得设置、构建和上传。其余操作、约束与 metadata 没有 package.json 框架检测记录。这不是把某个隐式工具内部保证当成缺陷，而是源文额外明确要求没有进入现有记录。
- **028 部署错误恢复缺口有依据。**主源文 Error Handling 有 Build failed 与 Publish directory not found 下的检查步骤；末图部署块仅有成功和 network error 出口，图中未记录这些恢复动作或相应条件声明。仍应保持这些动作的条件性，不把它们加入所有成功路径。
- **028 API Key 替代仅声明有依据。**NETLIFY_AUTH_TOKEN 可选设置存在 graph.constraints[8]，但实际 unauthenticated 路径只有 netlify_login，再次认证失败则 return；没有 token 设置/用户指导的可选入口。应明确是否将其视为当前主流程外的选项，不能把图级声明误读为已运行设置。

**025 多子图的简短建议：**结构合法只说明记录满足当前 CFG 的良序规则，不保证唯一 entry 能覆盖 Skill 的所有使用场景。先列清每个独立场景及其启动条件，确定传播分析的根集合或有原文依据的调度入口；不要为“全图可达”自动串联或强连所有节点，否则会增加原文没有的执行顺序和行为。
