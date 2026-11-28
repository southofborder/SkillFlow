# 审查纠错合并与共享修复路由

本报告记录唯一运行 `document-guided-ga4-runtime-locality-high-20261117-205158` 的初始审查纠错结果；共享修复仍在进行。只比对保存的 JSON、字节和哈希，没有运行语义阶段、校验器、后端、测试、模型、Skill 或重放，也没有修改冻结文件。

保存的 a002 校验为 **valid**，response chain 已选中 a002。它实际返回 **21 条既有 check 替换、0 条插入**，都在允许的 25 个记录槽内。将这些替换按原位置应用到 a001，逐项得到与保存的 merged-candidate 完全相同的对象，且哈希对应。其余 507 条 checks 不变；**19 条原始 findings 全部不变**，包括允许修改的四条 finding。义务 ID 和顺序也没有变化。

合并后的初始审查仍完整覆盖 **528 checks / 1735 scopes**：

- checks 为 503 accepted、25 rejected、0 unresolved。原先 23 条 rejected 均保留，另有 2 条 accepted 改为 rejected。
- scopes 为 1625 accepted、110 rejected。相对 a001 原文判断，80 个 accepted 改为 rejected，2 个 rejected 改为 accepted；其余 1623 个 accepted、30 个 rejected 状态不变。
- review 状态为 complete，但 diagnostic_only 为 true。这里“通过”表示结构、引用、覆盖与冲突检查通过，不能等同于全部语义判断已独立证实，也不表示原 CFG/annotation 已无问题。

最终供修复使用的 **44 条 findings** 来自 19 条未改的模型 finding，加上程序为 25 条 rejected contract check 分别生成的 processing finding；不是纠错模型又增加了 25 条 finding。路由分布为 Task 3、CFG 6、processing 32、task-correspondence 2、sensitivity 1。projection checks 和 typed source-input findings 都为 0，仅说明这些表未提供记录，不证明源文没有输入错误。

共享修复决策与此次完整审查、源文哈希绑定，以 reviewed_bundle 模式使用既有 **1 次修复轮次**，涉及 annotation、cfg、task，没有准入阻碍。当前 selection 仍是初始 Task、489IR CFG 和 annotation；不能把运行中的修订稿说成已经选中或修复正确。

实际 Task 修订 request 仅含原 Task 与 3 条源文异议，与保存审查逐项一致，不含 CFG/annotation。graph 修订反馈仅含 6 条 CFG findings 与原 489IR 图，flow 继续复用。既有依赖闭包要求先修 Task/graph，再基于修订图构建 processing；mapping 依赖修订 Task 与 processing，sensitivity 依赖 processing，之后 assembly 和重新绑定的 source re-review。初始审查不能直接作为新契约的审查凭据。

a002 模型文本为 34563 字符，JSON 容器 36859 字节；公开调用起止间隔 394.804739 秒，不是纯生成耗时，也不能据此概括普遍加速。完整源文、契约保留和 926055 字符纠错输入的证据见上一份 `source-review-a001-correction-audit.json`。本报告补充实际响应、合并与路由证据。

JSON：`source-review-merge-repair-audit.json`，SHA256 `49d9c097d71b6e6d19fc59e0579d6f9e95d9ecceeeb1c22a91b45e041e6f69db`。18 项只读身份和对象比较均通过；没有重新执行语义校验。最终源文正确性、边界覆盖与删除结论仍需等待修复及后端终态。
