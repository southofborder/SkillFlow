# 021–030 助手复核准备笔记

此文件只是冻结源文预读笔记，不是模型输入、评测答案或当前图已通过的结论。未运行任何 Skill 脚本。真正逐例意见必须等该例 `cases/NNN/result.json` 落盘后，再绑定实际轮次与图摘要保存到 `assistant-reviews/NNN.json`。

- 021 / D03：表格主流程是有效要求。读取 manifest.paths、output_dir、delivery_path；逐文档转换且绑定 stdout 为产物路径；脚本作为单次黑盒调用，不把脚本内部再次执行为主图步骤。标题保持仅作用于转换；生成 bundle.zip 后交付 delivery_path，还要独立写 receipt.txt。全局禁止改输入原文及外部上传；“必要时保留原顺序”是带条件的备注，不能无依据变成绝对排序或新步骤。
- 022 / D04：SKILL.md 明确把 references/workflow.md 纳入必须执行流程；不能只审短主文件而漏掉转换、打包、交付、receipt 及全局限制。脚本内容与 021 相同。
- 023 / D05：receipt.txt 是“历史示例（当前流程不执行）”，不能补进当前操作清单。其他转换和打包返回绑定仍有效。
- 024 / D06：原文第 1 步读 output_dir、delivery_path，第 6 步却明确交付到 archive_path。不能为了对齐来源名称把 archive_path 改回 delivery_path；需区分未明述取值来源与目标本身的明确要求。
- 025 / R01 pdf：按读/生成/审阅任务选择操作。真实必需过程是渲染后视觉检查、每次重要修改后重新渲染、最新 PNG 无格式缺陷才交付。文本提取不能替代布局校验。依赖缺失才安装；不能安装时告知用户。写 output/pdf/ 与临时文件清理、可读字形与表格/分页等约束要保留。没有脚本，许可证/图标不是业务步骤。
- 026 / R02 playwright：npx 前置检查失败要暂停并提示安装，成功才使用 wrapper。最新 snapshot 的 refs 是操作前提，导航/显著 DOM 变化或 ref 失效后重拍；不能凭过期 refs 或 run-code 绕过。CLI 参考是能力清单而不是全都顺序执行。wrapper 仅在没有显式 --session 且环境变量非空时补 session，保留全部其他参数；调用 npx CLI 后按工具返回处理，不能默认整个浏览器状态都已经进入模型。
- 027 / R03 gh-fix-ci：仅 GitHub Actions 取日志；外部 provider 只报告 URL，不继续分析。auth 缺失先请用户登录；PR 参数或当前分支 PR 的选择要保留。检查字段拒绝时使用可用字段重试；运行日志 pending 且有 job ID 时才直接取 job log。缺日志要明确报告。关键治理条件是先概述并取得明确批准，再实施计划；不能将“计划已经生成”当成批准。脚本已有本地 log snippet 截选，不意味着完整日志在本地已经脱敏。
- 028 / R04 netlify-deploy：auth/链接/初始化/依赖/部署/报告的控制先后与失败分支重要。新站默认 prod、已有站默认 preview、明确生产请求的选择要保留。源文自身又有 Always Preview First 和源码示例/可选参考，两者可能需要报告张力，不能掩盖成统一无歧义流程。环境设置/部署发送/返回 URL 分开，不把配置中的 secrets 禁提交声明当作已实施滤除；不要把 CLI 命令清单所有动作都强制执行。
- 029 / R05 linear：用户目标和范围→确认标识和工具→先读后写的逻辑批次→汇总缺口。设置 MCP 仅在未连接时；成功 OAuth 后要求重启并结束本次回复，再继续步骤 1。批量修改前解释分组。实践工作流和可用工具列表是按需求选择，不应把所有场景依次执行。确认对象、远程读取/写入、面向用户总结必须分清。
- 030 / R06 transcribe：默认 mini 模型+text；用户要求说话人/分离才选择 diarize+diarized_json；长音频保留 auto；API key 缺失只让用户本地配置，禁止贴全密钥。脚本约束：diarize 不支持 prompt，diarized_json 要匹配 diarize；多文件不允许 --out 或 --stdout；--stdout 不可与 --out/--out-dir 混用。25MB 实际脚本仅 warn 而不终止。known speaker 读取引用音频并转 data URL，最多四个；dry-run 打印 payload 而不调用 API。常规写文件后 stdout 只是 Wrote 路径，不能据此断言完整转录已经回给 Agent；后续质量检查若另行读取文本，应按实际图操作判断。

安全 profile 复核共同边界：actor 是执行参与者而非数据来源/接收方；LLM 调度本身不支持 model_observe。EM02 支持默认返回内容观察，但不自动证明文件全部内容进入模型。网络发送与接收可同属一个动作；transform（筛选、打包、摘要等）不证明敏感数据消除；隐私声明不产生真实保护动作。完整记录状态与语义/标注正确性分开。
