# 原文 → Task → demands 审查：两例真实调用的探索性记录

2026-10-15，Asia/Shanghai。本记录由 Codex 助手逐证据复核，`oracle_origin = assistant_authored_synthetic`，`human_expert_confirmation = not_established`。参考案例和本次裁定均未经独立人类专家确认，不能作为人类金标准上的性能评估。

本轮对两个与提示词教学例分离的合成候选进行了真实远程审查。两次调用均完成了四轴响应的类型、引用和覆盖检查。助手复核确认模型分别指出了预置的“漏掉禁止事项”和“字段需求扩大为整对象”问题；第一例还出现两条需要复核基准的额外意见，因此不计算整体检出率、误报率或准确率。

## 实际调用与协议结果

请求配置中的模型名为 `deepseek-v4-flash`，接口返回的模型名为 `deepseek-flash`，`reasoning_effort = max`。以下 token 数来自保存的接口 usage，输出 token 数包含接口计入的推理 token。

| 案例 | 植入问题 | 真实逻辑调用 / HTTP 尝试 | 结构纠正 / JSON 规范化 / HTTP 重试 | 输入 token | 输出 token（其中推理） | 请求耗时 |
| --- | --- | --- | --- | --- | --- | --- |
| sr001 | 同一源行中的禁止事项在 Task 与源文处置中同时漏掉 | 1 / 1 | 0 / 0 / 0 | 11,136 | 35,501（33,701） | 216.7 秒 |
| sr002 | 只需 title，却在上游完整 notice 输入上播种整值需求 | 1 / 1 | 0 / 0 / 0 | 11,152 | 50,680（49,684） | 307.2 秒 |

合计 2 次逻辑调用、2 次 HTTP 尝试，记录输入 22,288 token，输出 86,181 token，其中推理 83,385 token。请求时间段分别为北京时间 15:40:40–15:44:17、15:44:19–15:49:26；表中耗时只对应保存的请求开始与结束时间，不包含本地材料验证和复核时间。大部分输出 token 是接口记录的内部推理，不能用最终 JSON 文本长度代替这些 usage 数。

模型生成了真实审查响应；四轴通过仅表明记录完整、位置和引用可解析，不证明语义判断正确或限制已经穷尽。本次没有调用 Task 提取、Task 修订、标注修复或最终 DOE 裁决模型，也没有测量这些阶段的成功率。

## 逐条助手复核

| 案例 / finding | 助手裁定 | 证据与限定 |
| --- | --- | --- |
| sr001 / F001 | 匹配预置 O1 | 源文同一行写明 `Return notice.title unchanged and never return notice.layout_hint.`；Task 和处置记录只有返回 title 的 R1，没有禁止项。模型以 `domain=task`、真实源范围和 `missing_requirement` 对此登记，能够路由到隔离的 Task 修订阶段。 |
| sr001 / F002 | `needs_baseline_review` | 模型质疑精确 `select_part(input[0], [title])` 的根据，并指出候选还包含一个源文未命名的归档 notice 输入。原合成参考只标注了遗漏禁止项，没有充分处理“要求文字是否同时支持当前选择机制”和额外输入身份的歧义。该意见可能揭示参考材料说明不足，不能因为原 oracle 未列出就强记为误报。 |
| sr001 / F003 | `needs_baseline_review` | 模型把 `expected=null` 和空 bindings 视为原值关系不足。当前协议允许在真实返回结果播种并沿已声明的 `select_part` 反推，不要求所有这种关系都重复填写 `expected`；`ir_return` 也无法直接引用前一 IR 的输入。这有过严要求的迹象，但意见又依赖 F002 对选择语义的质疑，当前不做独立的确定误报裁定。 |
| sr002 / F001 | 匹配预置 O1 | 源文只要求返回 title，并明确把整对象读取描述为当前实现路径；需求却以 `preserve=value`、`path=[]` 指向上游完整 notice 输入。模型识别了字段范围扩大和过早播种位置，并建议改在真实 title 结果处建立需求。该 finding 附带提到 `expected` 为空，不意味着本复核认可“所有已知字段关系都必须重复 expected”。 |

第一例保留为 `oracle_gap`：预置遗漏确有对应发现，但其他意见尚待基准复核，整例不进入确定的 TP/FN/FP 汇总。第二例在助手裁定下有一项匹配、零项已确定漏检、零项已确定误报；这仅是一个合成候选的结果，不能外推总体表现。其余六个独立案例未运行，真实全值需求、不透明处理的保守依赖、错误版本和接收方等场景仍没有本轮真实模型证据。

## 已保存的材料和计数规则

- [原始参考案例登记](oracle.json)保持准备时的原样，包括当时的 `model_experiment=not_run` 准备状态；实际调用另存于 [experiment.json](experiment.json)，没有改写原始基准或受审候选。
- [助手逐项裁定](adjudication.assistant.json)引用每份已校验 review 的精确摘要，并明确 `reviewer_kind=assistant`。
- [助手裁定汇总](score.assistant.json)将第一例列为 `oracle_gap`、第二例列为 `adjudicated`，其余六例列为 `not_run`；待复核项既不当作检出，也不强行当作误报。
- [sr001 审查报告](runs/sr001/report.html)和 [sr002 审查报告](runs/sr002/report.html)保留全部四轴记录、问题、真实源证据及原始 demand 到 goal 的解析关系。对应目录中的 `inputs/candidate.json`、`calls/review/a001/response.json`、`validation.json` 与 `transport.json`保存受审输入、原始响应、程序校验和接口 usage。

首批 v1 运行准备时尚未将 oracle 摘要加入候选 manifest。本次评分因此显式传入原始 `oracle.json`，核对其中的案例内容、材料摘要和提示词字节摘要，并在结果中标记 `oracle_binding=explicit_external_baseline`；没有补写或加强旧 manifest 的保证。后来准备的新评测候选会在 manifest 的外部 provenance 中记录 oracle 摘要，oracle 内容仍不进入模型提示词。

工程模拟不计入真实模型效果。评分器会将没有观察到真实请求参数的注入式调用单列为 `engineering_simulation`，并拒绝把这类记录作为在线效果样本；已有工程测试通过也不代表模型检出了问题。

## 后续需要解决的证据缺口

下一轮应另建版本，明确区分功能要求、当前字段选择机制和每个输入的身份，再加入“已知字段选择后在返回结果播种、无需冗余 expected”的正例控制。保留本轮 v1 候选、响应与未决意见，不能为了让模型判断符合预期而回写本轮基准。

还需由独立人类专家确认参考义务、植入缺陷及额外发现，扩大真实全值、不透明依赖、条件、次数、顺序、版本和接收方的正反例，并单独测试实际 Task 提取与一轮修复。本轮只说明这份新审查协议在两个具体样本上可以发现预置问题，同时也暴露了基准歧义和审查过严的可能性；它没有证明语义完整、全局最小、所有路径可行或不存在 DOE。
