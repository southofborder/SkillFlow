# 026-playwright · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：R02；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_error；原因：source quote does not match specified lines: src_105
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：e90cb6ac662842e7465769f697da4308338388b9d67b7ca2d0624926a24a210a；源文 SHA-256：75246c04d327e94088e962e48d5321c7dda2d8194f54da044a1d5b7b95d08f5d

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/026/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/026/annotation/result.json>)；本地审查页也可展开全文。

当前所选图没有合法的完整语义核对记录。不能由结构有效或其他轮次的发现推定通过。

## 安全标注未决

- {"instruction_id": "ir_019", "field": "effects", "reason": "IR只记录click/type/press/fill，未指明是否提交表单或触发远端请求，无法确定net_send/net_receive是否发生。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：e90cb6ac662842e7465769f697da4308338388b9d67b7ca2d0624926a24a210a

助手复核：核对响应因错误引文被拒绝，保留最后有效图和含未决的标注；暂停与可选场景覆盖仍需复核，非人工确认。

- 运行事实：第 0 轮提出 5 项差异；第 1 轮 CFG 通过结构及受控文本保真检查，但语义核对停止为 audit_error。最终图 14 块、18 边、27 IR，安全标注 27 份、1 条 unresolved，因此为 incomplete。本意见为助手复核，未经人工确认，不能把本图称为核对器通过图。
- audit_error 具体原因是已完整返回的核对响应引文校验失败，并非网络超时：r001/audit/a001 的 finding_12 将 PLAYWRIGHT_CLI_SESSION 引到 src_105（references/cli.md 第 111 行），该行实际为 Or set an environment variable once:，不包含该变量。程序拒绝整份核对结果符合契约；没有擅改引用、追认结论或对该完整响应自动重发。原始响应 finding_5 另提出参考文件并用路径问题，仅作为未通过校验的原始模型意见保留。
- 相对第 0 轮，逐字安装说明的注释和空行已补回 ir_003；block_005–007 新增按需读取两个参考指南，block_012–013 新增 artifacts useful 守卫，原来无源文依据的完成字符串已删除，wrapper 已全局安装的例外补入图级声明。open→snapshot→最新 refs 交互→必要时重 snapshot 的环路及禁止 run-code 绕过 refs 保留。
- 仍需确认暂停语义：源文 SKILL.md 第 20 行 pause and ask the user to install Node.js/npm。block_002 只有 ask_user_to_install_nodejs 与 dispatch，/edges/2 为 null 条件直接返回检查；无显式暂停/等待用户完成约束。第 0 轮 finding_5 已提醒这一点，第 1 轮只修复说明字面值而未补等待语义；原始第 1 轮 finding_3 却称全部保留。null 边不等于立即执行，开放 ask 也可能隐含交互等待，因此应称暂停约束未显式保留，而不是断言已形成忙循环。
- 参考选择新增后，block_006 与 block_007 分别直接汇入 block_008，没有同一路线读取两者的连接。Open only what you need 不要求二者互斥，两个都需要时的可达流程未明确；单个 needed_reference 结果本身不能证明它只有一个值，更不能仅靠边标签推出逻辑互斥。建议确认按需访问的组合语义，避免为补两次读取反而加上无依据的互斥限制。
- 通用交互只概括成 click/type/press/fill，产物操作概括成 screenshot/pdf/traces。参考中的上传、eval、trace-start→交互→trace-stop 等是可选能力/场景，不能要求每条示例无条件执行；但若宣称覆盖完整可选场景，当前图不能区分其内容输入、外部效果与开始/停止次序。尤其 trace 仅放在交互结束后的 capture 摘要中，不足以表达需提前开始的调试场景。传播前应明确这是主流程抽象还是完整能力覆盖。
- wrapper 源码被完整嵌入 5 个调用操作 metadata；--session 参数优先于非空 PLAYWRIGHT_CLI_SESSION 的条件、npx 缺失 stderr/exit 1 均在源码中存在。原图主层未显式展开这些内部控制是约定的不透明边界，不能据此声称已计算脚本内部传播，也不能把引用 metadata 当作源码已执行。
- 唯一 unresolved 在 ir_019.effects：click/type/press/fill 是否提交表单/触发远端请求无法由该粗粒度动作确定，因此 net_send/net_receive 未决合理，不应靠工具名强行消除。ir_015 的网络双向标注引用真实 https URL 示例，有条件的远端浏览场景依据；但它不能证明每个 target_webpage 都是远端目标。snapshot 的页面状态经 EM02 进入模型，和浏览器仅加载页面但未回传全页内容应分开。
- 安全标注中 ir_011/013/017/019 仅由 EM02 的结果进入模型推断 actor=llm，仍有把接收者当执行者的问题。ir_021 被解释为 LLM 判断 interaction_result 是否需重 snapshot，却以 EM03“调度不等于观察”给出 effects=[]；它实际有内容输入和判断输出，若该 actor 解释成立，应讨论 model_observe/transform，不能用纯调度边界排除所有内容处理。ir_025 捕获落盘但没有返回全部文件内容，不能把无 model_observe 解释成已证明文件隔离。
- 视觉复核：实际查看完整 1801×8869 PNG 与 5 处细节，标题 026/R02/r1 正确保留 audit_error/incomplete，npx 回边、参考分支、重 snapshot 环路、artifact 条件与 return 均可见，长文本换行且无明显字形、节点边界或画布裁切问题。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
