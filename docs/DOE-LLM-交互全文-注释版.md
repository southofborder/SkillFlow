# 交付物 2:判断 flow 是否 DOE —— 完整真实 LLM 交互全文(逐属性注释)

> **命名说明**:图引擎已更名为 SFG(Skill Flow Graph);DOE(Data Over-Exposure)沿用原名。本文散文层已同步;但**发给 LLM 的 prompt 原文按镜像规则保持不变**——`prompt_version` 仍是 `doe-llm-judge-v5-structural-evidence`,pack 里的 `question` 字面量仍写 "Judge DOE necessity"(下文原样贴出,不改),内部脚本名/字段名(`doe-analyzer.js`、`analyzeDoe`、`classifyDoeBoundary` 等)一律保留。
>
> 目的:把"判定一条 flow 是否 DOE"实际发给 LLM 的**完整 message 原文**贴出来(system + user),逐属性注释含义,供审核**是否还有冗余属性**。
>
> 全文**非杜撰**:由 `packages/skill-doe-analyzer/.m4tmp/dump-judge-payload.js` 加载真实 v6(`v6_00002_skill-vetter`),跑规则期 DOE、选一条送审代表 pack,调真实的 `buildSharedTaskMemory` + `buildJudgePayload` dump 得到。原始 JSON 在 `packages/skill-doe-analyzer/.m4tmp/judge-payload.dump.json`。

---

## ✅ 已实施的瘦身(2026-07-24)

本文最初标出的一批冗余候选**已删/已处理**,下文正文与汇总表已同步为改后状态。这轮改动全在 **prompt 组装层**(`buildJudgePromptBody` / `buildSharedTaskMemory` 输出),**不碰规则裁决**(规则走 `analyzeDoe` rule-only,读 SFG 原始字段,不经此 prompt),56/56 测试绿,dump 实测符合预期。

| 字段 | 处置 | 依据 |
| --- | --- | --- |
| `shared_context.evidence: []` | **已删** | 恒空旧壳;`shared_context` 现只剩 `task_memory` 一个键 |
| `task_memory.task_evidence_ids[]` | **已删** | 全仓库零消费,== `evidence[].evidence_id` 去重复制 |
| `task_memory.task_context_node_count` / `documentation_source_count` | **prompt 里删、stats 留** | 对 LLM 判定无信息量;`buildSharedTaskMemory` 仍产出供 `llm-judge.js:51-52` 观测读,进 prompt 前由 `trimTaskMemoryForPrompt` 剔除 |
| `task_memory.evidence[].evidence_id` / pack `task_memory_evidence_ids` | **保留(活的 grounding 锚点)** | `validEvidenceIdsForPack` 的合法引用集;LLM 判 task_need 必须 cite,cite 不上进 `invalid_evidence_ids` 触发 escalation |

下面标 `~~删除线~~ → 已删` 的是本轮处理掉的;仍标 `⚠️` 的是**尚未动、待你定夺**的候选(主要在 pack 层:`observation_id/label_flow_id`、`field_name`、`question`、`data.evidence_id`、`instructionText↔source_line` 等 —— 它们要动 pack 结构 + `validEvidenceIdsForPack` + normalizer,风险高于这轮,单独评估)。

---

## 先澄清:你说的"三次 llm" —— 实际链路只有 1 种 prompt

审核前必须对齐一个事实,否则会找错"冗余":

**整条"判 flow 是否 DOE"的链路里,只有一个 LLM prompt 模板**(`llm-judge.js:355` `buildJudgePayload`),它在一次调用里同时判 3 个必要性分量。所谓"多次"是同一 prompt 的**重复投票**,不是三种不同 prompt。三种可能被叫作"三次"的东西,含义完全不同:

| 你可能指的"三次" | 真相 | 出处 |
| --- | --- | --- |
| **① 三个 necessity 分量** | ✅ **最可能是这个**。一次 LLM 调用里 judge 同时对 `action_input_need`、`receiver_semantic_need`、`task_need` 三个分量各出一份 {score,status,reasoning}。这是"三"的真实来源——但它们在**同一次 prompt 里**判,不是三次请求。 | `output_schema`(user 消息)要求每个 unit 返回这 3 个 component |
| **② first_pass + escalation 两阶段投票** | 同一个 prompt。first_pass 默认 1 票(`DEFAULT_VOTES=1`);高风险/不确定的 unit 升级再投 `DEFAULT_ESCALATION_VOTES=3` 票,多数表决。**prompt 逐字节相同**,只是跑 N 遍取共识。 | `llm-judge.js:32` `judgeEvidencePacks` → `judgePackStage(first_pass)` → `judgePackStage(escalation)` |
| **③ exposure(外泄)判定** | ❌ **根本不过 LLM**。外泄是**纯规则**(`exposure-scorer.js` `classifyDoeBoundary`,只读 observation.boundary)。LLM system prompt 明确写 `Do not decide exposure or final risk`。 | `exposure-scorer.js` |

**DOE = 外泄 ∧ 不必要**(两轴正交,见 [[exposure-necessity-orthogonality]])。外泄由规则定,LLM **只判必要性**(3 分量),最终 `potential_doe = 跨边界 ∧ necessity < 0.7` 由规则合成。

所以:**要审"冗余属性",审的是下面这一个 prompt 的 system + user 两条 message**。同一份内容会被复用于 first_pass 和 escalation(投票),不存在第二、第三种 prompt。

---

## 一次 LLM 调用的两条 message

`buildJudgePayload` 产出 `{ model, temperature:0, messages:[system, user] }`。缓存友好设计:**system + user.shared_context.task_memory 是 skill 级恒定前缀**(batch 内所有 unit 共享,~95% 缓存命中);只有 `evidence_packs[]` 逐 unit 变。

---

### message[0] — system(judge 的角色与判定纪律,恒定)

```text
You are a security evidence judge for potential data over-exposure analysis.
Judge layered necessity for each boundary observation and label_flow.
Local necessity has two components: action_input_need and receiver_semantic_need.
Global necessity is a single component, task_need: whether the full label_flow path
belongs to the data/control flow needed for the declared skill task AND the boundary
node is necessary in that path. Both must hold for task_need to be high.
Do not decide exposure or final risk. Do not lower necessity merely because a label is sensitive.
A flow reaches you ONLY because it crosses a real exposure boundary.
sink_boundary.exposure_tier=='high_sensitivity_egress' means the data genuinely leaves
the local process or is retained — this covers model providers, external networks,
third-party AND first-party services, webhooks, and persistent storage ALIKE.
Treat EVERY high_sensitivity_egress as a real, severe leak; none of them is a
trusted-internal sink. In particular a model provider (the LLM itself) is a real egress,
not an insider — do NOT raise receiver_semantic_need merely because the model needs the
data to reason. For every such receiver, judge whether it semantically needs THIS specific
label by the same standard you would apply to any external receiver.
First read shared_context.task_memory as the global task memory, then judge each unit with
its unit-local evidence.
Use task_memory evidence only when the unit lists that id in task_memory_evidence_ids.
Every conclusion must cite evidence handles that exist in the pack: the literal strings
"label" or "sink_boundary", a flow[] node's node_name, or a task_memory id listed in
task_memory_evidence_ids.
Return strict JSON only.
```

**逐句用途注释:**

- `layered necessity … two components (action_input_need, receiver_semantic_need) … single component task_need` —— 定义 LLM 要打的 3 个分量。**这就是"三"的来源**。
- `Do not decide exposure or final risk` —— 明确外泄/最终风险不归 LLM(规则的活)。**排除了你"三次"里的 exposure 那次**。
- `Do not lower necessity merely because a label is sensitive` —— 防"敏感=不必要"混淆(必要性与敏感度正交)。
- `high_sensitivity_egress … Treat EVERY … as a real, severe leak … a model provider … is a real egress, not an insider` —— [[n5-structural-evidence-and-egress-tier]] 的锚点:所有真外泄一视同仁,禁止把"模型需要数据推理"当成 receiver 语义必要。
- `cite evidence handles … "label"/"sink_boundary"/flow[] node_name/task_memory id` —— 约束引用句柄合法集(`validEvidenceIdsForPack`,`llm-judge.js:456` 校验)。
- `Return strict JSON only` —— 输出契约。

> **审核点(system)**:全是判定纪律,无数据属性,无冗余候选。

---

### message[1] — user(结构化 JSON,含指令 + 共享上下文 + 本 unit 证据)

user.content 是一个 JSON 字符串(瘦身后本例 19259 字符,瘦身前 20157),顶层 6 个键。下面**逐键 + 逐属性注释**,`⚠️` 标记的是**冗余候选**。

#### 1) `prompt_version`

```json
"prompt_version": "doe-llm-judge-v5-structural-evidence"
```

版本串,进缓存键辅助失效。**非冗余**(轻量)。

#### 2) `output_schema`

```json
"output_schema": "Return {\"assessments\":[...]} only. Each item: unit_id;
 components for action_input_need, receiver_semantic_need, task_need.
 Each component has score [0,1], status supporting|contradicting|insufficient,
 supporting_evidence_ids, contradicting_evidence_ids, reasoning_summary.
 Also include required_for_task, necessity_level none|low|medium|high|critical,
 reasoning_summary, supporting_evidence_ids, contradicting_evidence_ids."
```

规定回包结构。**这里再次坐实"三分量在一次调用里判"**——一个 assessment 同时要 3 个 component。**非冗余**(是契约)。

#### 3) `scoring_guidance[]`(打分锚点)

```json
[
 "Score action input need, receiver semantic need, and overall task need
  (full flow-path plus boundary-node necessity, conjunction).",
 "0.95 explicit proof; 0.75 strong support; 0.45 weak/broad support;
  0.10 insufficient; 0 unrelated or contradicted.",
 "Cite evidence handles only: \"label\", \"sink_boundary\", a flow[] node_name,
  or a task_memory id."
]
```

分档锚 + 引用约束。第 3 条与 system 末句**语义重复**(引用句柄约束说了两遍)——⚠️ **轻度冗余候选**(可接受的强调,但确实重复)。

#### 4) `judgement_flow[]`(怎么用证据的操作指南,9 条)

每条对应一个证据字段怎么读。注释:

- 用 `shared_context.task_memory` 做 skill 级任务/路由上下文 → **task_need**。
- 用 pack `label` + `sink_boundary` 做局部必要性(action_input / receiver)。
- `flow[] sink 节点的 sink_surface[]`:具体出口通道(webhook_post/api_call/…),比 sink_boundary 的 operation_type 更细。
- `flow[] sink 的 schema_declares_input`(true/false):sink 声明输入 schema 是否含**本 label** → action_input_need 硬信号。`source 的 origin_trust`:数据引入处信任。
- `sink_boundary` 描述 sink 节点跨的**唯一**边界(每节点构造上至多跨一界)。
- 用 `flow[]`(source→sink 逐节点变换)+ task_memory 判 task_need。
- flow[] 里 role 是**位置性**的(source/sink/transform);`capabilities[]` 是"能做什么"而非"对本 label 做了什么"。
- 节点有 `action`(单操作串)**或** `operations[]`(有序多步);step 的 `tags[]` 标数据整形步(field_slice/redaction/…);**顺序攸关**:脱敏在 egress 前=缓解,之后=不缓解。
- `transform/transforms` 字段报传播中实际观测到的 label 变化;当作已实现的缓解,并与 operations[] 对齐。

> **审核点(judgement_flow)**:9 条各绑一个 pack 字段,无孤立指令。**非冗余**(但依赖对应字段真出现;下面 evidence pack 里若某字段从不出现,则对应指令是空转——见文末交叉表)。

#### 5) `shared_context`(batch 共享,恒定前缀,缓存命中主体)

```json
"shared_context": {
  "task_memory": { … }    // ← skill 级任务记忆,batch 内所有 unit 共享(现在是唯一键)
}
```

- ~~`shared_context.evidence: []`~~ → **已删**:曾是 `buildJudgePromptBody` 硬编码的恒空数组(旧 5-section 残留),真实 evidence 全在 `task_memory.evidence`。改后 `shared_context` 只剩 `task_memory` 一个键。

**`task_memory` 内部**(本例 `skill-vetter`,改后进 prompt 的形态):

```json
{
  "memory_type": "extractive_shared_task_context",
  "skill_name": "skill-vetter",              // skill 身份
  "skill_version": "1.0.0",
  "evidence": [ … 27 条 … ],                 // 见下(每条的 evidence_id 是 grounding 锚点,保留)
  "use_for_components": ["task_need"],        // 提示这块只服务 task_need
  "note": "This is shared global task memory. Cite only task memory evidence IDs listed by the assessment unit."
  // ↑ task_evidence_ids / task_context_node_count / documentation_source_count 已不在 prompt 里
}
```

- ~~`task_evidence_ids[]`~~ → **已删**:它 == `evidence[].map(e=>e.evidence_id)`,与 evidence 数组里的 id 完全重复,且全仓库零消费。LLM 从 `evidence[]` 直接读每条 id 即可。
- ~~`task_context_node_count` / `documentation_source_count`~~ → **prompt 里已删、stats 留**:纯计数对 LLM 判定无信息量。`buildSharedTaskMemory` 仍产出这两个字段供 `llm-judge.js:51-52` 的 stats 观测读,`trimTaskMemoryForPrompt` 在进 prompt 前把它们剔除。
- `note` / `use_for_components` —— 给 LLM 的用法提示,轻量,**保留**。

**`task_memory.evidence[]`** 三类条目:

(a) **身份条目**(1 条):

```json
{ "evidence_id": "task.memory.identity", "type": "skill_evidence",
  "data": { "skill_name":"skill-vetter", "skill_version":"1.0.0",
            "description":"", "readme_preview":"" } }
```

- `data.skill_name/skill_version` —— **⚠️ 与外层 task_memory.skill_name/skill_version 重复**。
- `description:""` / `readme_preview:""` —— 本例**恒空**(该 skill 无 description);空串仍占位传出。⚠️ 空值可省。

(b) **文档预览条目**(1 条,`task.memory.doc.*`):

```json
{ "evidence_id":"task.memory.doc.55b84175e7", "type":"skill_evidence",
  "data": { "file":"SKILL.md", "role":"semantic_anchor_fallback",
            "line_count":134, "preview":"<SKILL.md 前若干字符…>" } }
```

- `preview` —— SKILL.md 正文前缀(本例数百字符)。task_need 判"路径是否属于声明任务"要靠它。**非冗余**(但体积大,靠缓存摊销)。
- `line_count` / `role` —— 轻量元数据,可留。

(c) **任务节点条目**(本例 25 条,`task.memory.node.*`),典型:

```json
{ "evidence_id":"task.memory.node.a7220bc6a5", "type":"skill_evidence",
  "data": {
    "evidence_id":"task.memory.node.a7220bc6a5",   // ⚠️ 与外层 evidence_id 重复
    "node_id":"node_005",
    "name":"doc.step.skill.l4.s1.guard.skill",       // slug 已内含 l4.s1(行4步1)
    "semanticKind":"doc_step",
    "operation_type":"guard",
    "instructionText":"Security-first vetting protocol …",  // ≈ source_line
    "location":{ "file":"SKILL.md", "line":4, "section":"Skill Vetter 🔒" },
    "source_line":"Security-first vetting protocol …"       // ⚠️ ≈ instructionText
  } }
```

逐属性:

- `data.evidence_id` —— **⚠️ 冗余**:与该条目外层 `evidence_id` 逐字相同(一条 evidence 带了两份自己的 id)。
- `node_id` —— 溯源到 SFG 节点,轻量,可留。
- `name`(slug)—— 已内含 `l4.s1`(行/步)+ operation_type + 语义类;与 `location.line`、`operation_type` **部分重复**。⚠️ 中度冗余候选。
- `semanticKind` / `operation_type` —— 给 LLM 判该 doc step 的作用,**非冗余**。
- `instructionText` vs `source_line` —— **⚠️ 高度重复**:本例这两个字段绝大多数条目**逐字相同**(见 node_005/006/008…)。少数条目 instructionText 是截断/拼接版(如 node_019 的 external_egress 把 curl 命令重复三遍),但语义仍是同一行。**留一个即可**。
- `location{file,line,section}` —— 定位,轻量,可留(但 `line` 与 slug 里的 `l4` 重复)。

#### 6) `evidence_packs[]`(本 unit 的局部证据 —— 逐 unit 变的唯一部分)

本例仅 1 个 pack(送审时 batch 默认 4 个):

```json
{
  "unit_id": "obs_000003::lf_000022",       // = observation_id::label_flow_id
  "question": "Judge DOE necessity for this label flowing from its source to this sink. …",
  "observation_id": "obs_000003",            // ⚠️ 已含在 unit_id 前半
  "label_flow_id": "lf_000022",              // ⚠️ 已含在 unit_id 后半
  "label": {
    "category":"database_record",            // 数据类目 → 全分量
    "subtype":"query",
    "sensitivity":"high",                    // 敏感度(system 明令不得据此降必要性)
    "field_name":"query_text",               // ⚠️ ⊂ field_path 末段
    "field_path":"signature.output.query_text",
    "mode":"definite"                        // definite/…(标签确定性)
  },
  "sink_boundary": {                          // sink 跨的唯一边界 → 外泄面 + 局部必要性
    "node_name":"llm.inference",
    "operation_type":"model_inference",       // ⚠️ 与 flow[] sink 的 operations[].op 重复
    "data_surface":"llm_context",
    "receiver_scope":"model_provider",
    "retention_scope":"transient",
    "trust_boundary":"model_provider",
    "operation_tags":["routing_decision"],
    "exposure_tier":"high_sensitivity_egress" // 真外泄标(system 说所有这标一视同仁)
  },
  "flow": [                                    // source→sink 路径,逐节点摘要 → task_need + 缓解
    { "node_name":"user.query", "role":"source",
      "action":"User query that triggers Skill activation",
      "capabilities":["control_context","data_introduction"],
      "origin_trust":"user_visible" },        // 来源信任
    { "node_name":"llm.inference", "role":"sink",  // ⚠️ node_name/role 与 sink_boundary 重复
      "action":"Implicit LLM call: Skill content (SKILL.md) is injected into LLM context when activated",
      "operations":[ {"op":"model_inference"}, {"op":"decision"} ],  // ⚠️ model_inference 第 3 次出现
      "capabilities":["model_inference"] } ], // ⚠️ model_inference 第 4 次出现
  "task_memory_evidence_ids": ["task.memory.identity"]  // 本 unit 可引的 task_memory id 白名单
}
```

**pack 逐属性冗余审核:**

- `observation_id` / `label_flow_id` —— **⚠️ 冗余**:`unit_id === observation_id + "::" + label_flow_id`,两个分量已完全嵌在 unit_id 里,又单列。(注:DOE 回填靠 unit_id,这俩纯给 LLM 阅读——可省。)
- `label.field_name` —— **⚠️ 冗余**:`field_name` == `field_path` 的末段(`query_text` ⊂ `signature.output.query_text`)。
- `label.mode` —— 标签确定性(definite/inferred);LLM 用作证据强度,**非冗余**。
- `sink_boundary.operation_type` (`model_inference`) 与 `flow[] sink.operations[].op` (`model_inference`) —— **⚠️ 重复**:同一 op 语义两处表达。本例 `model_inference` 在一个 pack 里出现 **4 次**(sink_boundary.operation_type、operations[0].op、capabilities[0],加 node_name 语义)。
- `flow[] sink.node_name` / `role` —— **⚠️ 与 sink_boundary 重复**:judgement_flow 已声明"sink_boundary 描述 sink 节点跨的边界,sink 节点的 role/capabilities 在 flow[] 上",故两处都出现 sink 节点是**设计上的分工**,但 `node_name` 确实两处都有。
- `capabilities[]` —— judgement_flow 明说是"能做什么,非对本 label 做了什么";与 `operations[]`(实际做了什么)语义不同,**非冗余**,但 sink 的 `capabilities:["model_inference"]` 与 `operations:[{op:"model_inference"}]` 在本例**恰好同值**,观感像重复。
- `question` —— 每个 pack 一份**几乎恒定**的长问句(只有 label 名不同);~250 字符 × N packs。⚠️ **可抽到 shared_context 说一次**的候选(现在每 pack 重复)。
- `task_memory_evidence_ids` —— 本 unit 允许引用的 task_memory id 白名单,**非冗余**(约束引用)。

**pack 里跨全语料才出现的可选字段**(本例 skill-vetter 未全触发,polymarket 1331 packs 实测全集):
`flow[]` 节点可选:`operations[]`(含 `tags[]`)、`sink_surface[]`、`schema_declares_input`、`origin_trust`、`transform`;pack 可选:`cycle_handling`、`leak_type`、`leak_severity`。这些是**条件出现**的承重证据,不是恒冗余。

---

## 冗余属性汇总(供你勾选)

按"确定冗余 → 可能冗余"排序:

**已处理(2026-07-24,shared_context / task_memory 层):**

| 冗余属性 | 位置 | 为何冗余 | 处置 |
| --- | --- | --- | --- |
| `shared_context.evidence: []` | user 顶层 | 恒空,旧结构残留(真 evidence 在 task_memory.evidence) | ✅ **已删** |
| `task_memory.task_evidence_ids[]` | shared_context | == evidence[].evidence_id,逐个重复,零消费 | ✅ **已删** |
| `task_context_node_count / documentation_source_count` | task_memory | 纯计数,LLM 不判需 | ✅ **prompt 删、stats 留** |

**待定夺(pack 层,风险高于上一轮,需动 pack 结构 + `validEvidenceIdsForPack` + normalizer,单独评估):**

| 冗余属性 | 位置 | 为何冗余 | 建议 |
| --- | --- | --- | --- |
| `data.evidence_id` | 每条 evidence 内 | == 外层同条目 evidence_id | 删内层(注意勿动外层 evidence_id 锚点) |
| `instructionText` ↔ `source_line` | 每个 node 条目 | 绝大多数逐字相同 | 留一个 |
| `evidence_packs[].observation_id / label_flow_id` | 每个 pack | 已嵌在 unit_id 里 | 可删(纯 LLM 阅读) |
| `label.field_name` | 每个 pack | ⊂ field_path 末段 | 可删 |
| `identity.data.skill_name/version` | 身份条目 | 与外层 task_memory 同名字段重复 | 可删内层 |
| `question` | 每个 pack | 近恒定长句,每 pack 重复 | 可抽到 shared_context 说一次 |
| `name`(doc slug) | 每个 node 条目 | 内含 line/op,与 location.line + operation_type 部分重复 | 可评估精简 |
| `scoring_guidance[2]` 引用约束 | user | 与 system 末句重复 | 轻度,可留作强调 |
| `sink_boundary.operation_type` vs `flow[].operations[].op` | pack | 同 op 两处;`model_inference` 单 pack 出现 4 次 | 设计分工,观感重复,建议保留但知悉 |

> 说明:上表"删/可删"仅指**给 LLM 的 user 消息**里的呈现冗余,删除只改 `evidence-pack.js`/`llm-judge.js` 的 pack/prompt 组装,**不影响规则裁决**(规则读的是 SFG 原始字段,不读这份 prompt)。真要删需同步 `validEvidenceIdsForPack` 的引用句柄集与 normalizer,并跑裁决等价回归。
>
> 关联:[[doe-flow-centric-evidence-pack]] [[doe-prompt-caching-and-usage-tracking]] [[n5-structural-evidence-and-egress-tier]] [[exposure-necessity-orthogonality]]。
