# 交付物 1:SFG v6 传递给 DOE 的信息清单(逐字段标注下游用途)

> 目的:把 SFG(`security_profile.version == "6.0"`)**实际传出**的每个字段列全,并**点明每字段被 DOE 哪段代码消费、做什么用**,供审核是否存在**过度传递**(传了但没人读 / 传了只做溯源展示 / 传了下游忽略)。
>
> 权威来源:`packages/skill-sfg/skill_sfg/flood/public.py`(v6 装配器)真实产出 + DOE 侧 `doe-analyzer.js` / `necessity-baseline.js` / `exposure-scorer.js` / `evidence-pack.js` 的真实读取点。所有"消费者"都标了文件:行区间。
>
> 结论速览:**DOE 做"必要性/外泄"裁决实际只读极少数字段**;v6 里绝大多数体积是 `node_profiles`(节点原样透传)与 `observations`(判定摘要)。`flow_states` 已瘦身到只剩 DOE 读的 4 个 + 少量溯源字段;`label_flows` 已降到"兜底重建"最小集;`provenance_graph` 已只留真变换事件。下文逐块标注哪些是**裁决承重**、哪些是**溯源/审计留存**、哪些是**候选可再削**。

---

## 0. 顶层结构

`security_profile` 顶层键(`public.py:82-91`):

| 键 | 传什么 | DOE 消费者 | 定性 |
| --- | --- | --- | --- |
| `version` | `"6.0"` | 无(DOE 不读 `analyzer_version`,可自由 bump) | **零消费**,仅标识 |
| `node_profiles[]` | 每个图节点的完整画像(原样透传,未压缩) | 见 §1 | 部分承重、部分溯源 |
| `label_dictionary{}` | label_id → 压缩 label 对象的字典 | `doe-analyzer.js:94` `buildLabelDictionary` → `resolveLabel` 解引用 | **承重**(label 去重存储) |
| `label_flows[]` | 路径无关的最小流(单父链) | 见 §2 | 兜底重建承重 |
| `flow_states[]` | 判定单元表(去重后的状态) | 见 §3 | 4 字段承重 + 溯源 |
| `provenance_graph{}` | 只剩 `events.filtering` 真变换事件 | 见 §4 | 变换解析承重 |
| `observations[]` | 每个 (label,sink) 观测点 + 判定摘要 | 见 §5 | **裁决主入口** |
| `statistics{}` | 计数/可观测性 | 无裁决消费,仅 CLI/日志 | **零裁决消费** |

**DOE 分析的真正入口是 `observations[]`**(`doe-analyzer.js:119-120`:双层循环 `for observation → for label_flow_id`)。其余块都是被 observation 引用后按 id 拉取的。

---

## 1. `node_profiles[]` —— 节点画像(原样透传,最大体积块之一)

SFG 把每个节点的完整 profile 原样塞进 v6(`public.py:84` `"node_profiles": node_profiles`,**未做任何字段裁剪**)。字段全集(实测):
`node_id, node_name, node_roles, security_tags, operation_tags, data_surface, receiver_scope, retention_scope, trust_boundary, data_profile, action_steps, action_order_confidence, action_order_source, has_multi_action, ambiguous_action_order, produced_object_key/text, consumed_object_key/text, conditions, confidence, evidence, formal_semantics`。

DOE 侧真实读取点(`profileByNodeId` 建于 `doe-analyzer.js:103`):

| node_profile 字段 | DOE 消费者 | 用途 | 定性 |
| --- | --- | --- | --- |
| `node_id` | 全程索引键 | observation/flow_state/label 用它回指 profile | **承重** |
| `formal_semantics.inputs[]` | `necessity-baseline.js` `schemaInputMembership` / `pathDeclarationCoverage`;`evidence-pack.js` `schemaDeclaresInput` | 判 sink 的声明输入是否含**本 label** → action_input_need 硬信号 + pack 的 `schema_declares_input` | **承重(action_input_need)** |
| `node_roles` | `necessity-baseline.js` `isTransformLike`;`evidence-pack.js` `flowRole` 定位 | 判节点是不是变换节点 / 定位 source·sink·transform | **承重** |
| `operation_tags` | `necessity-baseline.js` `isTransformLike`;`evidence-pack.js` `OPERATION_TRANSFORM_TAGS`→ pack 的 `operations[].tags` | 判该节点声明的操作里有无 field_slice/redaction/… | **承重(缓解识别)** |
| `semanticKind` / `type`(=builtin_call) | `necessity-baseline.js` `pathDeclarationCoverage` | task_need 里"路径节点是否被文档声明覆盖" | **承重(task_need)** |
| `receiver_scope, retention_scope, trust_boundary, data_surface, operation_type` | 经 observation.boundary 间接进裁决(见 §5);pack 的 `sink_boundary` 也来自这里 | 外泄判定 + LLM 出口面 | **承重(经 observation)** |
| `name, action_steps(op 串), produced/consumed_object_text` | `evidence-pack.js` 组 pack 的 `action` / `operations[]` 摘要串 | 只进 LLM 证据文本,不进规则分 | **LLM 证据(承重于 LLM)** |
| `data_profile, security_tags, confidence, evidence, action_order_*, has_multi_action, ambiguous_action_order, conditions, produced/consumed_object_key` | **DOE 侧无读取点** | —— | ⚠️ **候选过度传递**:node_profiles 整块原样透传,这些字段无 DOE 消费者,只是没单独裁 |

> **审核要点(§1)**:`node_profiles` 是"原样透传、未裁剪"的块。真正被 DOE 读的只有上表前 6 类。`data_profile/security_tags/evidence/confidence/action_order_*/conditions/*_object_key` 等在 DOE 端**零读取**。是否值得像 flow_state 那样给 node_profile 也做一次投影裁剪,是一个明确的可优化点(但注意:node_profiles 也可能被 SFG 自己的下游或调试消费,裁剪前需全仓确认)。

---

## 2. `label_flows[]` —— 路径无关最小流(兜底重建用)

v6 已把每条流从"全路径"压到"单父 + 本跳"(`public.py:169-194` `_compact_public_label_flow`)。真实字段与消费:

| 字段 | DOE 消费者 | 用途 | 定性 |
| --- | --- | --- | --- |
| `label_flow_id` | `doe-analyzer.js:96` 建 `labelFlowById`;observation 用 `label_flow_ids[]` 引它 | 主键 | **承重** |
| `parent_label_flow_ids[]`(单父) | `evidence-pack.js` `transformsByNode` 顺 `[0]` 上溯父链 | **兜底重建变换序列/flow[]** | **承重(兜底)** |
| `current_node` / `current_node_name` | `evidence-pack.js` flow[] 定位、`flow-path-utils.js` `resolveLabelFlowPath` | 重建节点路径 | **承重(兜底)** |
| `incoming_edge_id` | `flow-path-utils.js` 重建 edge_path | 兜底路径 | 承重(兜底) |
| `origin_node` | `doe-analyzer.js` `originClass` / P1 溯源裁剪 | 去重键 origin 分量、裁到 origin | **承重(去重键)** |
| `local_filter_event_ids[]` | `evidence-pack.js:259` 取本跳的真变换事件(join `provenance_graph.events.filtering`) | **本跳变换解析** | **承重** |
| `flow_state_id` | `necessity-baseline.js` `sinkTransformedLabel`/`scoreReceiverSemanticNeed` 回查 flow_state | 连到判定单元的 transform_sig/reduction | **承重** |
| `flow_mode` | `necessity-baseline.js` / 置信度 | may_flow vs must_flow 影响保守度 | 承重(轻) |
| `confidence` | `assessmentConfidence` | 评估置信度 | 承重(轻) |
| `label` / `label_id`(二选一,字典引用) | `resolveLabel` 解引用 → 全下游读 `labelFlow.label` | **数据敏感类目** | **承重** |
| `truncated` | `doe-analyzer.js:152` `flowRequiresReview` | 触发人工复核标 | 承重(轻) |
| `cycle_handling` | pack 的 `cycle_handling` 透传给 LLM;periodic/collapse 语义 | 环处理标注 | 承重(轻,LLM) |
| `terminated, termination_reason, storage_key, merge_group_ids, label_fingerprint, introduced_at` | **DOE 侧无裁决读取点**(storage_key 只在去重键历史里,现从 observation 摘要走) | —— | ⚠️ **候选过度传递** |

> **审核要点(§2)**:`parent_label_flow_ids + current_node + local_filter_event_ids` 三件套是 DOE **兜底重建** flow[]/transform_seq 的原料(当 observation 摘要不足时)。若确认 M4 后 DOE 已完全改吃 observation 摘要、不再走 parent 链兜底,则这三件套连同 `incoming_edge_id` 可考虑再削。`terminated/termination_reason/storage_key/merge_group_ids/label_fingerprint/introduced_at` 目前**无 DOE 消费者**。

---

## 3. `flow_states[]` —— 判定单元表(已瘦身)

v6 已删掉 ~41% 字节的死字段(`public.py:200-227` 注释列明)。**DOE 从 flow_state 只读 4 个字段**(全仓 grep 证实):

| 字段 | DOE 消费者 | 用途 | 定性 |
| --- | --- | --- | --- |
| `state_id` | 索引键(`flowStateById`) | flow_state 主键 | **承重(索引)** |
| `transform_sig` | `necessity-baseline.js` `sinkTransformedLabel`(判 `!== 'none'`) | 送出前是否发生过变换 → receiver_semantic_need | **承重** |
| `reduction_applied` | `necessity-baseline.js:345` `scoreReceiverSemanticNeed` | "送出前已减量"+0.2 加成(v6 才修好,原来恒失效) | **承重** |
| `origin_boundary.trust_boundary` | `necessity-baseline.js` `scoreReceiverSemanticNeed` | 来源信任语义 | **承重** |
| ↑以上 4 个是全部裁决消费 | | | |
| `representative_label_flow_id, node_id, node_name, transform_digest, origin_node, origin_boundary.data_surface, label/label_id` | **无裁决读取**,保留作**溯源/审计**(`transform_digest` 是 `reduction_applied` 的前像,可人工审) | 审计可读性 | **溯源留存(设计上有意保留)** |

> **审核要点(§3)**:这块已是"最小裁决集 + 明确标注的溯源留存"。`transform_digest` 保留是**有意的**(让人能审 reduction_applied 怎么来的),不是遗漏。若要极致瘦身可删溯源字段,但会牺牲可审计性——建议保留。

---

## 4. `provenance_graph` —— 只剩真变换事件

v6 只保 `events.filtering` 且只保 `REAL_TRANSFORM_TYPES` 事件(`public.py:242-273`,polymarket 从 16462 条降到 474 条)。

| 字段 | DOE 消费者 | 用途 | 定性 |
| --- | --- | --- | --- |
| `events.filtering[].event_id` | `evidence-pack.js` `filterEventById`(被 `local_filter_event_ids` 引) | 事件主键 | **承重** |
| `.type` | `evidence-pack.js` `summarizeTransform` + `REAL_TRANSFORM_TYPES` 过滤 | 变换类型(redact_drop/…) | **承重** |
| `.from_label, .dropped_label, .context_label, .kept_label, .introduced_label` | `evidence-pack.js` `summarizeTransform` 派生 `from_label`/`to_label` | pack 里 transform 的前后 label | **承重(LLM 证据)** |
| `.node_id, .node_name` | 变换定位 | 挂到 flow[] 节点 | 承重(轻) |
| `.propagated_label, .storage_key` | 保留(`public.py:269-270`)但 DOE `summarizeTransform` 未读 | —— | ⚠️ **候选过度传递(轻)** |
| `statistics.filter_event_count/total/dropped_nonreal` | 无裁决消费,可观测性 | —— | 零裁决消费(留观测) |

> **审核要点(§4)**:这块已激进瘦身。剩下的 `propagated_label/storage_key` 两字段 `summarizeTransform` 实际没读(它只读 from/dropped/context/kept/introduced),是可再削的轻量候选。

---

## 5. `observations[]` —— DOE 裁决主入口(判定摘要)

**这是 DOE 分析的真正入口**(`doe-analyzer.js:119`)。每个 observation = 一个 (label,sink) 观测点,自带 M3 判定摘要。实测字段:
`observation_id, node_id, node_name, node_roles, security_tags, boundary{}, action_step_id, operation_type, order, order_confidence, ambiguous_action_order, leak_type, leak_severity, label_flow_ids[], transform_digest, transform_sig, word_set, origin_node, origin_boundary, meaningful_steps, reduction_applied, reduction_applied_all`。

| observation 字段 | DOE 消费者 | 用途 | 定性 |
| --- | --- | --- | --- |
| `observation_id` | `doe-analyzer.js:169`;去重键第 1 段;pack unit_id | 观测点主键 | **承重** |
| `label_flow_ids[]` | `doe-analyzer.js:120` 内层循环 | 该观测点绑定的流集 | **承重** |
| **`boundary{trust_boundary, receiver_scope, retention_scope, data_surface}`** | `exposure-scorer.js` `classifyDoeBoundary`(**外泄判定唯一输入**)+ `necessity-baseline.js` action_input/receiver | 外泄轴 + 局部必要性 + pack.sink_boundary | **承重(外泄裁决核心)** |
| `security_tags` | `exposure-scorer.js` `classifyDoeBoundary` 读 | 外泄证据标 | **承重(外泄)** |
| `node_id / node_name / node_roles` | profile 回指 + pack 组装 | 定位 sink 节点 | 承重 |
| `operation_type` | necessity action_input(op 语义基线)+ pack.sink_boundary.operation_type | 操作语义(model_inference/external_egress/…) | **承重(action_input_need)** |
| `transform_digest / transform_sig` | pack 组装(优先读 observation 摘要,而非 walk parent);去重键 transform_seq | LLM 证据 + 去重键 | **承重** |
| `reduction_applied` | pack + necessity(经 flow_state 亦有) | 减量标 | 承重 |
| `origin_node / origin_boundary` | 去重键 origin_class + pack | 来源信任等价类 | **承重(去重键)** |
| `meaningful_steps[]` | pack 的 flow[] 由它构造(source+变换节点+sink) | LLM 证据路径 | **承重(LLM 证据)** |
| `word_set` | ⚠️ **DOE 不逐字读**(`task_need` 用 labelTerms/taskText/flowText 规则派生) | —— | ⚠️ **候选过度传递**(见 [[v6-flowstate-slimming-and-reduction-fix]] 备注:word_set 在 observation 上亦是死字段) |
| `leak_type / leak_severity` | pack 可选透传给 LLM;`cycle_handling` 同 | 环/周期泄露标注 | 承重(轻,LLM) |
| `action_step_id, order, order_confidence, ambiguous_action_order, reduction_applied_all` | **DOE 侧无裁决读取点** | —— | ⚠️ **候选过度传递** |

> **审核要点(§5)**:observation 是入口,大部分字段承重。但 **`word_set` 明确是死字段**(DOE task_need 不逐字消费,见记忆),`action_step_id/order/order_confidence/ambiguous_action_order/reduction_applied_all` 也无裁决消费——这几个是 observation 块里最实的过度传递候选。

---

## 6. 过度传递候选汇总(供你重点审核)

按"传了但 DOE 裁决完全不读"归拢,风险从高到低仅指"删了最省字节":

| 位置 | 字段 | 现状 | 建议 |
| --- | --- | --- | --- |
| observation | `word_set` | 死字段(task_need 规则派生,不逐字读) | **可删**(记忆已标) |
| observation | `action_step_id, order, order_confidence, ambiguous_action_order, reduction_applied_all` | 无裁决消费 | 可删(先确认无 SFG 自身下游/调试依赖) |
| node_profiles | `data_profile, security_tags, evidence, confidence, action_order_*, conditions, produced/consumed_object_key, has_multi_action` | 整块原样透传,无 DOE 消费者 | 可投影裁剪(收益最大,但需全仓确认无其它消费者) |
| label_flows | `terminated, termination_reason, storage_key, merge_group_ids, label_fingerprint, introduced_at` | 无裁决消费 | 可删 |
| label_flows | `parent_label_flow_ids, current_node, incoming_edge_id, local_filter_event_ids` | 仅"兜底重建"用 | 若确认 DOE 已全吃 observation 摘要、不再兜底,可删 |
| provenance_graph | `propagated_label, storage_key`(事件内) | `summarizeTransform` 未读 | 可删(轻) |
| flow_states | `transform_digest, origin_node, node_name, representative_label_flow_id, label` | 溯源留存(**有意保留**) | 建议保留(可审计性) |

> 注:上表"可删"均指 **DOE 裁决路径无消费**;删除前须 grep 确认 SFG 自身/pipeline runner/调试工具无其它读点。`transform_digest`(flow_state 上)是有意的审计留存,不建议删。
