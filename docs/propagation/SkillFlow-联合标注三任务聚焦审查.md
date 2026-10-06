# 联合标注聚焦审查 v2 与一次修复

本规范对应 `annotation-review-v2`、`skill-ir-annotation-review-v4` 和 `skill-ir-annotation-refinement-v3`。初审与复审各自为独立的一次整图审查；仅在初审合法且提出具体问题时，允许一次完整联合标注修复。源文与 CFG 不变，不实施 DOE 判断。

历史 v1 七例结果保留在 [原始综合报告](../../experiments/propagation/review/runs/focused-v1-20260929-121534/assistant-review.md)，不重新解释原响应。历史的 `uncertain` 记录不是 v2 的合法输入。

## 1. 表示职责先于语义判断

唯一权威表示契约为 `skillflow-representation-contract-v1`，定义在 `skillflow.propagation.contracts.representation_contract`。完整契约与运行时契约共同冻结在材料中，由标注、审查和修复提示词使用，不由各角色维护不同副本。

| 关系 | 承载位置 |
|---|---|
| 操作数、定义、控制、条件、约束及普通 return 的返回值身份 | CFG |
| 读取范围、明确字段、筛选成员、处理依赖、位置更新、实际交互参数 | 传递规格 |
| 模型观察的数据版本 | 原始处理段及编译观察 |
| 普通调用者内部接收状态、未说明的网络机制、执行成功 | 当前材料不能自动推出的边界 |

普通 return 没有公开结果时，允许空 `events` 和 `output_bindings`。不得为它虚构 output[0]、user_output 或无标签 deliver。审查仍须查看实际 return 输入；错误返回值不会因为空事件合法而变正确。

空 effects 不代表 NOP。已知工具获取允许 receive/tool，不需要制造网络效果。明确字段原值不能退化成 opaque compute；约束、名称及 metadata 不能代替实际缺失关系。仅有措辞不准确、但数据范围和身份并未变化的情况，不触发修复。

## 2. 一次审查的材料与结果

三个阅读任务仍为：范围是否无依据收窄、数据关系是否丢失或虚构、观察与交付是否绑定正确。不要求逐 IR 写通过表，不要求每项发现只属于一类。

模型业务输入只有完整可读 Skill、实际 CFG、统一运行时契约、表示契约、原始标注、程序生成且经过映射完整性核验的观察清单，以及程序定位索引。没有传播后 Data、DOE 输入、助手意见、上轮判断、反例标签或答案。

```text
正常响应
├─ outcome: completed
├─ reviewed_ir_ids: 所有真实 IR，恰好一次
└─ findings[]: 可为空
   ├─ id: 唯一编号
   ├─ target_ids: 已有定位编号
   ├─ status: issue
   ├─ explanation: 原要求、当前表示、差异及其数据关系影响
   ├─ evidences[]: basis / ref_id / quote
   └─ suggestion: 有依据的完整修改建议

任务无法完成响应
├─ outcome: cannot_assess
└─ failure
   ├─ reason: 具体必要判断为何无法完成
   ├─ target_ids: 已有定位
   └─ evidences[]: 真实依据
```

两分支互斥。失败分支不得携带 findings 或假装正常空清单。程序核验引用、引文、完整覆盖及严格结构；`SemanticFailure` 仅在失败记录本身通过校验后产生。其运行状态为 `semantic_failure`，与格式错误和网络错误区分。

原始 `unknown、unknown_reason、uncertain、unresolved` 不再是正常出口。未知容器内容、possible 依赖、适用默认规则、可计算部分顺序、来源候选和未承诺执行成功，本身均不构成无法判断。确实缺少必要材料、必要关系冲突或超出表示能力时明确失败。失败理由仍是模型判断，程序不冒充已证明其充分性。

缺失动作可以定位已有父容器；JSON Pointer 和原值由程序解析，模型不自行编写深层路径。引文真实不代表推断必然正确。正常空 findings 只称为“本次未发现实质问题”。

## 3. 一次完整修复

```text
冻结候选 → 初审
  ├─ 合法且无问题：结束
  ├─ 明确问题：完整修复一次 → 严格校验与观察编译 → 独立复审 → 结束
  └─ 任务失败／格式错误／调用失败：结束，不猜测修复
```

修复请求使用统一标注 Prompt 的显式 repair 类型，冻结同一源文、CFG、契约、上一份实际原始标注、合法初审、程序解析目标及原值。请求上下文在 `inputs/repair-context.json` 保存并绑定摘要，使用同一构建器验证；不通过临时客户端包装追加隐藏文本。

修复输出是完整新版联合标注，不是 patch。原文与契约优先于建议；不能为满足错误建议制造字段、局部隔离、保护、网络或用户输出，也允许保留有依据的原表示。复审重新生成当前候选的编号和观察，只看当前完整材料，不接收初审意见或修复提示。

| 状态 | 含义 |
|---|---|
| review_passed | 初审或一次修复后的复审未提出实质问题，不是等价证明 |
| repair_limit | 一次修复后仍有问题或引入新问题，不继续循环 |
| semantic_failure | 合法的 cannot_assess，不能计通过 |
| invalid_response | JSON、编号、引文、覆盖或规格不合法 |
| execution_error / input_error | 调用或材料执行问题 |
| interrupted | 保留已开始调用，恢复不重发已接受响应 |

最后有效候选在结果中明确为 original 或 repair。修复失败时不能把旧成功传播称为新修复成功；合法候选即使复审有问题也可诊断性传播，但必须保留审查状态。

## 4. API、记录、恢复和重放

```python
review_annotation(material, raw_annotation, *, client)
refine_annotation(material, raw_annotation, *, review_client, repair_client)
```

持久运行使用 `prepare_candidate_run` 或 `prepare_run` 准备一次审查；`prepare_refinement_run(input, analysis, material, raw_annotation, *, run_dir, provenance, ...)` 准备有界修复。显式候选入口要求外置来源说明，不将实验重建伪装成历史模型接受响应。

```powershell
python -m skillflow.propagation.review prepare --annotation-run <当前完成标注> --run-dir <审查目录>
python -m skillflow.propagation.review run --run-dir <审查目录> --env-file .env
python -m skillflow.propagation.review refine --annotation-run <当前完成标注> --run-dir <修复目录> --env-file .env
python -m skillflow.propagation.review refine --run-dir <修复目录> --env-file .env
python -m skillflow.propagation.review replay --run-dir <审查或修复目录>
```

`replay` 按当前明确身份分派一次审查或完整修复重放，不支持旧格式。单案例最多三次逻辑调用，HTTP 暂态重试另计。完整但无效响应不补跑，失败不自动降级。每阶段均复用既有 JSON Output、SSE、配置摘要、脱敏、互斥锁和接受响应记录。

修复目录包含根级冻结源包、候选与来源说明，以及 initial-review、repair、final-review 三个按需创建的阶段。保存实际请求、原始响应、编译、判断及停止原因。离线重放不创建在线客户端，逐阶段验证请求与输入并恢复相同决定。只读完成材料可以跨新增代码检查；继续执行和重放仍严格绑定源码身份。

## 5. 验收与实验解释

离线集中覆盖：普通 return 职责、旧字段拒绝、真实证据、候选篡改、正常空清单与任务失败、一次／三次调用、修复失败停止、复审新增问题、独立上下文、请求上下文身份、中断后不重发及零 API 重放。源文、CFG、原始历史记录不改写。

本轮三原候选和四受控候选先显式重建，初审和按需修复／复审最多 21 次；三张既有 CFG 的独立新版源文核对另计三次，不重新建图。报告分别展示工程结果、真实标注修复表现和源文核对表现。是否真正修复仍由外置预期与助手逐条复核，不以模型最终空清单代替标准答案。
