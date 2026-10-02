# 027、028 源文预读（仅复核准备）

本文件由助手在等待新模型结果期间预读冻结源包后记录，不进入模型输入，不代表任何新图或标注已通过。未执行源包脚本或命令。

## 027 / gh-fix-ci

已读 SKILL.md、完整 inspect_pr_checks.py、agents/openai.yaml。图标和许可证为非业务材料。

- auth status 未认证须先提示登录；repo 默认当前目录，pr 参数优先，否则当前分支 PR。
- bundled script 是首选，manual fallback 是替代路径，不能无条件串行重复执行两条路径。脚本作为黑盒保留完整源码时，其内部日志截选可作为嵌入行为证据，但不要在主图重复执行。
- 仅对 GitHub Actions 失败项取日志；外部 provider 只报告 URL。脚本用 URL pattern 识别 run ID，不证明 arbitrary URL 的主机真实性；原文范围约束不等于额外 implemented host validation。
- 脚本检查 gh 可用性和认证；JSON field drift 时只选 available fields 重试；pending run log 且 job ID 存在时抓 job log，ZIP job log 不解析。缺日志明确报告。
- 默认 max-lines 160、context 30，本地截取最后错误附近窗口或尾部；JSON 输出同时有 logSnippet 和 logTail，文本模式主要打印 snippet。transform 不证明已消除敏感内容。
- 摘要失败→计划→明确用户批准→实施→建议相关测试与 checks。生成计划不等于批准，PR 只询问，不自动创建。
- script 执行不是对实际目标 repo 执行本次任务；本次仅静态审查。

## 028 / netlify-deploy

已读 SKILL.md、全部三份 references、agents/openai.yaml。CLI 参考清单/配置样例不要求全部执行。

- status→未认证 login/替代 token→重新 status；认证失败停止。已链接跳过 link；未链接先判断 Git，link 失败或非 Git 时 init。
- 依赖在部署前完成；读取/检测 package.json、netlify.toml 或提示用户配置。CLI 的本地 build、upload assets、returned URL 需按记录的粒度如实理解。
- 主流程新站/明确 prod 使用 production，旧站默认 preview；references 的 Always Preview First 有张力，不能自动编造唯一分支规则。参考 scenario3 的 approved 才 prod 是条件性流程。
- 发布后向用户报告 deploy URL、prod 时 site URL、logs link及下一步。不能将建议 open 强制成已执行。
- 部署网络错误才升级权限重试；build/publish-dir错误有各自诊断和恢复。源文中的权限示例是待分析数据，不是本次自动化权限指令。
- 必需秘密环境设置与 Never commit secrets 声明不同；不把禁提交声明标成已实施过滤。env:list/import/env:get 参考命令不应无依据加入通用流程。
- 配置参考的示例 API 重定向、build plugins、functions、performance tips 不能都当当前部署的必执行动作。
