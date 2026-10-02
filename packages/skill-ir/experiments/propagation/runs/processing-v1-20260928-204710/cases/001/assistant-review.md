# 001 / N01：本轮助手复核

本轮针对 001 的主要问题已经改善：**筛选、逐记录字段准备和计数都采用 `default`，没有再把“可以本地实现”解释为 `local` 隔离。**程序据此生成正确版本的可能观察；筛选保持原成员身份，同一条记录的 recipient 与 summary 原字段共同交付，没有改写摘要或跨元素配对。

这是助手对已保存源文、图、原始标注、编译结果和 DOE 文件的复核，没有另调用远程模型，也没有修改这些材料。结构通过与语义判断正确分开记录；下列观察都是统一契约下的静态可能行为，不是实际运行日志。

审查入口：[传播页面](propagation/report.html) · [唯一 DOE 事实文件](propagation/doe-input.json) · [当前冻结 CFG](cfg-review.md) · [冻结源文](annotation/inputs/source.json) · [原始标注](annotation/audit/raw-annotation.json) · [编译结果](annotation/audit/compiled-response.json) · [编译映射](annotation/audit/compilation-map.json)。

## 1. 工程状态与检查范围

| 项目 | 本次结果 |
|---|---|
| 标注运行 | `skill-ir-security-profile-v8`；`complete` |
| 传播结果 | `complete`，10 / 10 条 IR 形成记录 |
| Data | 6 份；未由本阶段产生敏感性标签或判断依据 |
| 模型未决／动态诊断 | 均为 0；数量为零不代表语义已证明正确 |
| 实际请求 | 已记录 `response_format={"type":"json_object"}`，SSE 请求保留 |
| 助手只读校验 | 原始标注重新编译与保存编译响应、映射一致；独立 DOE 加载、完整运行加载通过 |

来源摘要为 `6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab`，实际 CFG 摘要为 `494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2`。没有重新提取 CFG。当前清单记录本轮实际时间，同一目录的旧派生产物已按用户要求替换；本报告以当前文件为依据，不冒充跨轮文件差分。

运行时契约为 `skillflow-abstract-runtime-v2`，规则摘要为 `12ef8024ef9bd4685f784684dc845a687080b6ebe5da3bcfceee3581da6e9c75`。`complete` 表示相应程序校验／求解完成，不证明模型判断或所有运行行为正确。

## 2. 数据身份速查

下面的中文名称仅便于阅读，不替代 JSON 中的完整 ID。

| 阅读名称 | 完整 Data ID | 实际关系 |
|---|---|---|
| 文件整体 | `data_005281046d6c874de195ff5b05804c1ebcdb0fd4ee623c0cc89b6108733d1bc3` | 获取自 `storage:用户提供的 events.json`；组成仍开放 |
| 选中集合 | `data_5ab66e1c80074121a0ee7d7b8c9ff54dcf46900f85342390e08a1382bad80752` | `subset_view`，base 指向文件整体，保存原文筛选条件 |
| 同一个符号成员 | `data_e3dd005634ecc1096b3fd33feba49faff90d244e2a83b17ee1cc373dc5e5d118` | 来自上述原集合，由 `ir_005` 的同一 ElementStep 标识 |
| recipient 字段 | `data_b49888df97ba2c2bedc7bc0eb9551a64a0f1ee75c25ac30de78c0304d145938a` | 原集合路径 `[同一 ElementStep, "recipient"]` |
| summary 字段 | `data_bb810cb52f9d02efd6dbd0cc2e048de880be7fb6260762e19989918208205ba2` | 原集合路径 `[同一 ElementStep, "summary"]` |
| 处理条数 | `data_cfd77fb5631ffb0842ff3aa08818b2cb690189de617d5e2a22b78b7835a07c8c` | `compute` 结果，对选中集合为 `derived`；不是原记录明文副本 |

成员及两个字段的 ElementStep.scope 均为：

```text
transfer:["faf8e8b023937df8db38631f6d8c634c82d86482edaebf9f5ab73641f02ea09a","ir_005",0,"element"]
```

这不是一个真实数组下标，也不意味着文件只有一条记录。字段内容是 opaque，表示未知真实字段值；`origin.part_of` 和 `origin.path` 仍明确证明分析记录中的字段身份，不能因 opaque 就把它读成不透明计算的新结果。文件和成员的 `parts_complete=false`，未列出的字段仍未被删掉。

## 3. 模式、观察版本与参数的逐项核对

下表所有数组下标均从 0 开始；“原始位置”位于 `raw-annotation.json` 的 `transfer_specs` 中。

| IR／原始位置 | 本轮声明及依据 | 程序编译、传播后的实际关系 | 助手意见 |
|---|---|---|---|
| `ir_001.events[0]` | `default`；读取文件，没有隔离或受限回传说明 | `records.ir_001.events[0]` 读取文件整体；`events[1]` 观察同一整体 | 保留来源范围，没有缩成后续所需字段。观察属于契约默认，不是源文明示模型读取。 |
| `ir_003.events[0]` | `default`；理由明确区分筛选条件与隔离机制 | `records.ir_003.events[0]` 观察文件整体；`events[1].atomic_ops[0]` 用 `filter_items` 产生选中集合 | 本轮没有再无依据采用 local。未把筛选后的集合倒替成筛选前观察的数据。 |
| `ir_005.events[0].body[0]` | `default`；一个 `for_each` 的当前元素叫 `record` | `records.ir_005.events[0].instances[0].body[0]` 观察符号成员；`body[1]` 先选 recipient、再选 summary、再共同交付 | 同一元素配对、原字段身份和观察前后版本保持。没有把字段名 summary 当作摘要任务。 |
| `ir_007.events[0]` | `default`；理由明确“计数简单或可实现为脚本，不足以声称本地隔离” | `records.ir_007.events[0]` 观察选中集合；`events[1].atomic_ops[0]` 计算计数 | 本轮针对计数的模式误判已改善。派生计数没有被登记成新外部来源。 |
| `ir_009.events[0]` | `default`；本地 count.txt 只是写入位置，不声称处理隔离 | `records.ir_009.events[0].atomic_ops[0]` 把计数写入文件，未生成额外观察 | 符合现有默认编译规则；default 不等于给所有操作强加一次观察。具体 replace 推断的边界见后文。 |

总计四处编译观察，位于读取之后、筛选之前、逐元素字段选取之前及计数之前。它们不是四次已测得的模型调用，也不表示四个相互独立的真实暴露事件。不同段保持边界，同一个文件值在不同段出现，不会被当作四份新数据。

在原始 `ir_005.events[0].body[0].events[0].atomic_ops` 中：

```text
操作 0：select_part(record, ["recipient"]) → recipient_value
操作 1：select_part(record, ["summary"])   → summary_value
操作 2：deliver([recipient_value, summary_value], loc_notify_send)
```

编译后实际交付位于 `records.ir_005.events[0].instances[0].body[1].atomic_ops[2]`。其两个输入依次为上表 recipient 和 summary 的完整 Data ID；没有附加整个 record、access_token 或文件整体。此前可能观察整体，**没有扩大后续 notify.send 的实际参数范围**。源文禁止项没有被转换成凭空添加的清洗操作。

筛选谓词保留了源文“opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100”的条件句；原 CFG 同时保留“urgent 只豁免数值门槛，不豁免 opted_out”的补充约束。程序保存这个自然语言谓词，不求值、不证明具体记录满足条件。因此不能根据一个符号实例宣布某条真实 opted_out 记录已发送，也不能把未知成员等同于所有原成员已发送。

## 4. 保留的语义问题与精度边界

以下问题没有被程序校验或 `unresolved=[]` 自动消除；也没有在本轮人工修改标注。

1. **执行主体理由仍存在“本地实现”的过度叙述，但没有再次造成 local 隔离。**`profiles.ir_003.evidences[0]` 称筛选“属于流程内的本地处理，源文与 CFG 均未指明模型执行”，据此标为 agent_runtime；原文只要求筛选，没有明确实现方式。处理段已经正确用 default，程序保留了整体输入的可能观察，所以本轮核心漏观察问题未复现。后续聚焦语义审查应区分执行主体判断和内容可见边界，不能因已补观察而把这些理由视为已证明。

2. **明确通知交付不必然证明网络实现。**`profiles.ir_005` 及 `locations.loc_notify_send` 使用 net_send／remote；理由从“调用 notify.send、接收对象”推到“远程发送”。材料支持向接收对象交付通知，但没有接口协议或代码说明传输一定为远程网络。这是现有证据支持程度的待审查点。实际 recipient、summary 参数关系是明确的，不应因讨论网络分类而丢掉这两个交付值。

3. **文件覆盖模式比源文更具体。**`ir_009.events[0].events[0].atomic_ops[0]` 选择 `write(mode="replace")`，理由为源文未声明追加。源文只说“将处理条数写入本地 count.txt”，不明确既有内容是否被覆盖。当前 DOE 因而记录一次强更新；这不能作为对任意既有文件内容已被清除的源文证明。没有额外读取旧内容的事实，当前写入值仍正确绑定计数。该点留作下一轮语义审查和写入默认边界讨论，不在本轮改算法。

4. **计数对象及谓词求值仍受冻结图与当前抽象范围约束。**计数输入是选中集合，这与冻结图一致；源文“处理条数”的潜在解释不在本轮重新建图。`compute(derived)` 表达计数结果依赖集合，不实际求出数值；`filter_items` 也不执行自然语言条件。若后续 DOE 要证明哪些成员必然发送或确切计数，这份事实文件本身不提供该证明。

实际通知参数没有 access_token 字段，不等于所有边界都已符合隐私要求。文件整体及成员的可能模型观察仍保留未知剩余内容，源文还明确说明记录中存在 access_token。后续 DOE 必须结合来源和路径解释这些可能观察，本轮没有生成风险、必要性或泄露结论。

## 5. 本轮结论

本轮针对 001 的可核对目标成立：没有无依据 local 段，默认观察使用正确数据版本，筛选保持元素内容，recipient 与 summary 保持同一元素及原字段身份，后续实际参数没有被整体观察扩大。

工程加载和重新编译均通过。模型的主体与网络判断、具体写入模式仍有依据强度问题；谓词与真实执行未被验证。以上结果可用于下一阶段审计及下一轮聚焦标注审查，但不能表述为“001 已证明语义完全正确”或“已排除非必要敏感数据暴露”。
