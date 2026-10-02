# 当前运行接续信息

- 用户授权：覆盖 result/ir-IPP 与 result/suggestions；新增 result/security-profiles 与 result/review；dataset ZIP、旧实验和 advice_for_doe 不改。
- 最新明确指令：失败的全部重跑一下。新 run `full-pipeline-v4-20260918-rerun-failed` 完整重跑 008、009、018–030，15 例；001–007、010–017 原样复用，含 incomplete-only。
- 后台进程 exec session 35658；log `tmp/full-pipeline-v4-20260918-rerun-failed/run.log`。只读日志与终态 cases/NNN/result.json，不读取活动 call/transport/progress。
- 命令为原 sealed run_full_pipeline.py run，官方 DeepSeek 配置，600000ms timeout，workers=3，既定修复与重试预算。不要启动重复批次。
- 父批次 `full-pipeline-v4-20260918` 已完整离线 replay，30 例状态一致。父 93 执行、128 HTTP，受 rerun-provenance 中1398文件摘要保护，从现在起不要向父run新增或改任何文件（replay与锁除外）。
- 新批次全结束后离线 replay，再执行 summarize_rerun_costs.py --run-dir <新run>；合并成本为父全部+子重跑15新增，复用不再收费计数。
- tmp新目录 assistant-reviews：15复用意见已验证相同并带继承说明；008/009/018/020新复核已完成；019在runner代理审，021在core代理审。实际以文件存在和hash绑定为准。
- 后续分工：core审021–024；runner审019/025/026；root审027/028（完整业务源文已读，见source-preread-027-028.md）；feedback审029/030（源文已读）及展示工具。
- 静态视觉：新15复用、新008/009、新018、新020已实际查看并有visual-review*.json，分别preview-reused-15、preview-008-009、preview-018、preview-020。不能把旧008/009/018/019/020的图当新图。
- 内置浏览器曾明确阻止 file://，不可绕过localhost/另一浏览器/CDP；只用既有SVG→PNG artifact renderer与view_image静态检查。离线UI测试已有通过，最终须如实说明未用内置浏览器交互检查30例真实页面。
- sealed src/**/*.py、正式driver、Lean及传输源均不得在运行期间改。新exporter/UI/tests/tools不在源指纹内可修改。
- 未发布正式结果：最终还需所有30终态、独立助手复核、offline replay、正式export+review index、30PNG完整性/视觉核验、跨run成本、中文验收报告，再仅覆盖确认四个目录。旧交付已备份 tmp/full-pipeline-v4-20260918/delivery-backup，before摘要 delivery-before.json。
- 重要实际方法问题：复用015状态append实参为body/error却无明确状态转换（不能直接断言泄露）；新009 user-supplied来源遗漏被auditor放过；014/016/017等工具网络效果猜测；actor/隐含model_observe推断口径尚不一致；新018旧context/environment误报消失，summary与success/failure绑定正确。
- 校验：既有全量1307 passed；交付最新40 passed/1浏览器 deselected；prepare9、lineage11、底层恢复56（有重叠，不简单相加）；Lean16定理公理审计通过，未重链打印器。以最终日志补更新。
