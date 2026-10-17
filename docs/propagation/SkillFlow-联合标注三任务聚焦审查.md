# Joint annotation review v5 and one repair

本规范对应 `annotation-review-v5`、`skill-ir-annotation-review-v9` 和 `skill-ir-annotation-refinement-v8`。初审与复审各自为独立的一次整图审查；仅在初审合法且提出具体问题时，允许一次完整联合标注修复。源文与 CFG 不变，不实施 DOE 判断。

历史 v1 七例结果保留在 [原始综合报告](../../experiments/propagation/review/runs/focused-v1-20260929-121534/assistant-review.md)，不重新解释原响应。历史的 `uncertain` 记录不是当前契约的合法输入。

## 1. 表示职责先于语义判断

表示职责来自严格 Schema 和共用 `format_instructions()`；不再为每份 Skill 冻结第二份表示契约。运行默认仍只由 `runtime_contract` 定义。直接引用形状和当前字段见[字段收紧规范](../architecture/field-tightening.md)。

| 关系 | 承载位置 |
|---|---|
| 操作数、定义、控制、条件、约束及普通 return 的返回值身份 | CFG |
| 读取范围、明确字段、筛选成员、处理依赖、位置更新、实际交互参数 | 传递规格 |
| 模型观察的数据版本 | 原始处理段及编译观察 |
| 普通调用者内部接收状态、未说明的网络机制、执行成功 | 当前材料不能自动推出的边界 |

普通 return 没有公开结果时，允许空 `events` 和 `output_bindings`。不得为它虚构 output[0]、user_output 或无标签 deliver。审查仍须查看实际 return 输入；错误返回值不会因为空事件合法而变正确。

空 effects 不代表 NOP。已知工具获取允许 receive/tool，不需要制造网络效果。明确字段原值不能退化成 opaque compute；约束、名称及 metadata 不能代替实际缺失关系。仅有措辞不准确、但数据范围和身份并未变化的情况，不触发修复。

### Binding coordinates used by the reviewer

The reviewer must resolve the enclosing object before interpreting an input index. These are distinct coordinates, even when they happen to contain the same integer:

| Representation | Meaning |
|---|---|
| `Task.bindings[].target` | General correspondence to a directly referenced CFG object |
| Top-level `demands[].target` | A CFG position capable of carrying the stated demand |
| `operation.demands[].target = {"kind":"input","index":k}` | The atomic operation's consumed input slot `k` |
| A `ValueRef` with `kind="input"` | The enclosing IR's actual CFG operand |
| Finding `target_ids` | Claims or generated observations under review, not demand targets |

For example, `deliver.inputs=[{"kind":"input","index":2}]` has **one** consumed slot: operation slot `0`, referring to IR input `2`. Its attached goal can correctly target slot `0` with `expected={"kind":"input","index":2}`. Replacing that target with slot `2` would introduce an invalid operation reference. The same IR interpretation of `ValueRef` applies to `expected`, member values, member conditions and expression references; expressions do not switch to operation-slot coordinates.

The existing `value_uses()` contract determines consumed slots. Ordered `inputs` are preserved for compute, delivery and acquisition. Single-input operations use slot `0`; field updates use the original base followed by update values. Construction visits members in declared order: an unconditional member contributes its value, while a conditional member contributes its control followed by its value. Repeated references and controls retain separate slots. A false condition does not renumber these static targets, and a control slot is not payload.

The review Prompt now includes two compact, independent calibration examples: one delivery and one conditional record construction. Their exact operations are compiled in offline tests against their own synthetic source and CFG; the examples are kept outside actual review material. They contain no evaluated Skill examples. The tests also retain a deliberately wrong but structurally valid goal, demonstrating that coordinate validity does not establish semantic correctness. A reviewer should compare the resolved value, property and source requirement before proposing any change; it must not remove a supported goal simply because IR and operation indexes differ.

## 2. 一次审查的材料与结果

The same review also checks Task purpose and requirements, demand target/value relationships, supported expressions, sensitivity scope and evidence, and cross-item consistency. It does not compute final DOE. A repair cannot erase valid sensitivity or broaden Task requirements to conceal an issue.

三个阅读任务仍为：范围是否无依据收窄、数据关系是否丢失或虚构、观察与交付是否绑定正确。不要求逐 IR 写通过表，不要求每项发现只属于一类。

模型业务输入只有完整可读 Skill、可空 user_request、实际 CFG、统一运行时契约、原始标注、程序生成且经过映射完整性核验的观察清单，以及审查阶段自身的 ann/obs 定位索引。表示说明由 Schema 与共用 Prompt 函数提供，不再保存为另一份逐 Skill 材料。没有传播后 Data、DOE 输入、助手意见、上轮判断、反例标签或答案。

```text
正常响应
├─ outcome: completed
├─ reviewed_ir_ids: 所有真实 IR，恰好一次
└─ findings[]: 可为空
   ├─ target_ids: 已有定位编号
   ├─ explanation: 原要求、当前表示、差异及其数据关系影响
   ├─ evidences[]: file / start_line / end_line / reason；target / reason；rule_id / reason
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

Finding IDs are assigned by the program after parsing, and status is represented by the response branch. No model-filled finding ID or constant issue field remains.

缺失动作可以定位已有父容器；JSON Pointer 和原值由程序解析，模型不自行编写深层路径。引文真实不代表推断必然正确。正常空 findings 只称为“本次未发现实质问题”。

## 3. 一次完整修复

```text
冻结候选 → 初审
  ├─ 合法且无问题：结束
  ├─ 明确问题：完整修复一次 → 严格校验与观察编译 → 独立复审 → 结束
  └─ 任务失败／调用失败：结束，不猜测语义修复

各输出先经过程序结构校验；机械错误进入共用结构纠正请求链，次数不限。结构纠正不消耗一次语义修复次数。
```

修复请求使用统一标注 Prompt 的显式 repair 类型。`manifest.upstream` 精确引用 refinement 所有者，从同一冻结源文、CFG、契约、原候选及其固定 `initial-review` 阶段重建反馈；清单绑定上下文摘要，不再保存 `inputs/repair-context.json` 或候选、初审、解析目标的重复副本。实际发送的 Prompt 原样保存。恢复、只读加载和重放使用同一个重建器，不通过临时客户端包装追加隐藏文本；没有已核验所有者的持久修复入口明确拒绝。

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

`replay` 按当前明确身份分派一次审查或完整修复重放，不支持旧格式。单案例最多有初审、一次语义修复及复审三个语义阶段；各阶段的机械结构纠正没有次数上限，HTTP 暂态重试单独统计。受限 JSON 修整保留原始响应及审计；剩余机械错误通过新纠正请求处理，失败不自动降级。每阶段均复用既有 JSON Output、SSE、配置摘要、脱敏、互斥锁和接受响应记录。

正式修复目录以 manifest.upstream 引用原标注的输入所有者，只保存本轮来源说明；独立实验候选才保存自己的候选与一次输入分片。initial-review、repair、final-review 按需创建并引用已有材料，不再逐段复制源包或 material 总包。保存实际请求、原始响应、编译、判断及停止原因。离线重放不创建在线客户端，逐阶段验证请求与输入并恢复相同决定。只读完成材料可以跨新增代码检查；继续执行和重放仍严格绑定源码身份。

## 5. 验收与实验解释

离线集中覆盖：普通 return 职责、旧字段拒绝、真实证据、候选篡改、正常空清单与任务失败、一次／三次调用、修复失败停止、复审新增问题、独立上下文、请求上下文身份、中断后不重发及零 API 重放。源文、CFG、原始历史记录不改写。

本轮三原候选和四受控候选先显式重建，初审和按需修复／复审最多 21 次；三张既有 CFG 的独立新版源文核对另计三次，不重新建图。报告分别展示工程结果、真实标注修复表现和源文核对表现。是否真正修复仍由外置预期与助手逐条复核，不以模型最终空清单代替标准答案。


正常审查的 `inputs/` 仅保存 `targets.json`、`observations.json` 与实际 `prompt.txt`。原始候选及编译事实从已验证上游重建，编译证书由清单绑定。显式实验变体另保存 candidate/provenance，但不保存 source/CFG/规则的平行副本。公开 `load_prepared_review_material` 返回重建的内存视图；报告链接目标与观察文件，不以另一份总包作为输入。


审查 `result.json` 只保存原有审查发现及运行协议，不再持久化 `resolved_findings`。深层目标和值由已核验原候选及定位索引在内存重建；因此即使某项发现定位到标注根节点，也不会在结果文件再嵌入一整份原标注。报告仍展示解析后的目标。保存、只读加载和重放共用这一快照投影，并用规范 JSON 身份比较，拒绝将整数下标或计数替换成数值相等的浮点／布尔值。
