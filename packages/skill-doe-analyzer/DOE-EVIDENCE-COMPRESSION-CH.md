# DOE LLM Judge — Evidence Pack 压缩机制与成本分析

> **历史文档(2026-06-14 时点)**:本文记录当时的 v3 prompt(`doe-llm-judge-v3-shared-task-memory`)、旧版 5-section evidence pack 与 4 分量必要性,是彼时的成本测量快照,**刻意不回填到当前 v7 结构**(回填会篡改记录)。图引擎现已更名为 SFG(Skill Flow Graph),DOE(Data Over-Exposure)沿用原名;包内 `fcg`/`doe` 内部标识按镜像规则保留不变。
>
> 适用版本:`packages/skill-doe-analyzer`(prompt_version `doe-llm-judge-v3-shared-task-memory`)
> 测量基准:`skill_0001 self-improving-agent 3.0.21`(SFG JSON 117 MB)
> 模型:gpt-5.5;价格为占位值,见末尾「价格假设」。

---

## 1. 数据流总览(一个 unit 如何变成一次 API 调用)

```
SFG JSON
  └─ analyzeDoeRuleOnly()                      doe-analyzer.js
        每个 (observation × label_flow) → 1 个 assessment
        shouldJudgeAssessmentWithLlm() 门控:                    ← 第一道减量
          只有 boundary_crossed && sensitivity≥high && boundary_risk≥0.75
          的 unit 才 eligible,才会 buildEvidencePack()
  └─ buildEvidencePack()                       evidence-pack.js
        构造 5 个 section 的「完整」证据 pack(无裁剪)
  └─ judgeEvidencePacks()                      llm-judge.js
        ├─ compactPackForPrompt()   去掉 task_context_evidence,加 evidence 索引
        ├─ budgetPackIfNeeded()     ← 分层压缩(本文重点),evidence-budget.js
        ├─ chunkJudgePacks()        按 batchSize / maxBatchChars 打包
        └─ buildJudgePayload()      每个 batch 拼 system + schema + shared_context + packs
                                    → POST 到模型
```

关键点:**压缩只发生在 `budgetPackIfNeeded`,且只压缩单个 evidence pack。** 而每次请求里体积最大的部分——`shared_context.task_memory`——完全不经过压缩(见 §4)。

---

## 2. 门控:大部分 unit 根本不送模型

`shouldJudgeAssessmentWithLlm`([doe-analyzer.js:400](packages/skill-doe-analyzer/src/doe-analyzer.js#L400)):

```js
const sensitive       = sensitivityRank >= SENSITIVITY_RANK.high; // high/critical
const highRiskBoundary = boundaryRisk >= 0.75;
const eligible = Boolean(boundaryCrossed && sensitive && highRiskBoundary);
```

skill_0001 实测:

| 指标 | 数量 |
|---|---|
| assessment 总数 | 10,269 |
| boundary_crossing | 8,133 |
| **llm_eligible(实际送模型)** | **3,403** |
| llm_skipped | 6,866 |

即门控已经先砍掉了 ~67% 的 boundary-crossing unit。剩下 3,403 个是成本来源。

---

## 3. Evidence Pack 的分层压缩(`evidence-budget.js`)

入口 `budgetPackIfNeeded(pack, options)`([evidence-budget.js:88](packages/skill-doe-analyzer/src/evidence-budget.js#L88))。
准确性契约:**≤ 上限的 pack 逐字节原样透传(Tier 0),只有超限的才压(Tier 2)。**

默认参数([DEFAULT_LIMITS](packages/skill-doe-analyzer/src/evidence-budget.js#L20)):

| 参数 | 默认 | 含义 |
|---|---|---|
| `maxPackChars` | 100,000 | pack 字符上限;超过才触发压缩 |
| `pathNodeWindow` | 4 | 压缩时 flow 路径首尾各保留的完整节点数 |
| `maxTextChars` | 2,000 | 长文本字段裁剪上限 |
| `maxArrayItems` | 40 | 冗长数组裁剪上限 |

`NOTE_RESERVE = 1200`:为最终追加的 `budget.note` 预留头寸,保证 finalize 后仍 ≤ 上限。

### 压缩按顺序逐步施加,达标即停:

**Step 0 — Tier 0 透传**(L91)
`estimatePackChars(pack) <= maxPackChars` → 直接返回原 pack。判定与不压缩完全一致。

**Step 1 — 无损精简 `losslessReduce`**(L99 / [L251](packages/skill-doe-analyzer/src/evidence-budget.js#L251))
深拷贝后归一化空白:`[ \t]+\n→\n`、`\n{3,}→\n\n`、`[ \t]{2,}→ `。不删语义,只压空白。

**Step 2 — flow 路径节点开窗 `windowFlowPathNodes`**(L106 / [L288](packages/skill-doe-analyzer/src/evidence-budget.js#L288))
对 `flow.path_node.*` 证据项:保留首 `window` 个 + 尾 `window` 个 + 边界节点,其余替换为 `stubPathNode`(只留 `evidence_id / id / name / semanticKind / operation_type / location` + `summarized:true`)。引用 id 保持有效。
触发条件:路径节点数 > `window*2+1`(默认 > 9 才开窗)。

**Step 3 — 文本/数组裁剪 `clampTextAndArrays`**(L117 / [L340](packages/skill-doe-analyzer/src/evidence-budget.js#L340))
- 仅 `TEXT_FIELDS`(description / instructionText / evidence_text / snippet / reason …)超 `maxTextChars` 时做 `headTailWindow`(保头尾,中间标 `…[trimmed N chars]…`)。
- 仅 `CAPPABLE_ARRAY_FIELDS`(member_steps / sections / effects / conditions / inputs / outputs …)超 `maxArrayItems` 时截断并记 `_omitted_count`。
- **结构字段(ids / names / node_path / edge_path / location)永不裁剪。**

**Step 4 — 丢弃聚合 flow 证据 `dropAggregatedFlowEvidence`**(L124 / [L380](packages/skill-doe-analyzer/src/evidence-budget.js#L380))
删除 `flow.state` / `flow.origin.*` / `flow.path_class.*` / `flow.representative_path.*`(辅助上下文,非边界/标签/核心路径)。

**Step 5 — 截断 provenance 大段 `capSectionItems`**(L137 / [L176](packages/skill-doe-analyzer/src/evidence-budget.js#L176))
`provenance_filter_storage_evidence` 只留前 `maxArrayItems` 条,记 dropped 数。

**Step 6 — 硬上限兜底 `enforceHardCeiling`**(L147 / [L188](packages/skill-doe-analyzer/src/evidence-budget.js#L188))
- 先 `reindexEvidence`:重建 `evidence` 索引以匹配存活项,`task_memory_evidence_ids` 截到 40(它会列出每个原始 id,本身可能撑爆 pack)。
- 再按优先级 `provenance → flow_path`(flow_path 至少留 1)批量丢尾部项,用平均项大小估算丢弃数避免 O(n²)。
- 边界证据、local action/receiver 证据**永不丢**。

最后 `finalizeBudgetedPack`(L218)打上 `_budgeted / _budget_notes / _original_chars / _budgeted_chars`,并向 `boundary_evidence` 追加一条 `budget.note`,显式告诉模型「上下文被压过,缺失视为未知」。该 unit 下游标记 `requires_review` 并计入 `llm_fallback_count`。

> **实测**:skill_0001 的 eligible pack 平均约 **74 K 字符**,在 100 K 上限以下 → 绝大多数走 Tier 0 透传,Step 1–6 基本不触发。所以「pack 压缩」对这个 skill 几乎没省钱——成本不在这里。

---

## 4. 真正的成本大头:`shared_context.task_memory` 被每个请求重复携带

`buildJudgePayload`([llm-judge.js:309](packages/skill-doe-analyzer/src/llm-judge.js#L309))每个 batch 的 user message 结构:

```
{ prompt_version, output_schema, scoring_guidance, judgement_flow,
  shared_context: { task_memory: {...}, evidence: [] },   ← 重复,未压缩
  evidence_packs: [ ...budgeted packs... ] }              ← 已压缩
```

`shared_context.task_memory` 由 `buildSharedTaskMemory`([llm-judge.js:368](packages/skill-doe-analyzer/src/llm-judge.js#L368))生成,内容是**全 skill 的 task context 节点 + 文档来源 + readme**。它**对每个 batch 重新构建并完整发送**,且**不经过 `budgetPackIfNeeded`**。

### skill_0001 单请求字符拆分(batchSize=4, votes=1)

| 组成 | 平均 chars/请求 | 占总输入 |
|---|---|---|
| **shared_context(task_memory,重复)** | **~382,841** | **75.9%** |
| evidence_packs(真实 per-unit) | ~74,056 | 14.7% |
| system + schema + guidance | ~小 | 其余 |
| 合计 | ~504,492 | 100% |

因为单 pack evidence(~74 K)已逼近 `maxBatchChars=60000`,`chunkJudgePacks` 实际几乎 **1 unit/请求**(3,403 unit → 3,366 请求)。于是那 ~383 K 的 task_memory **被原样重发了 3,366 次**。

> **这是当前最大的、且尚未触碰的压缩机会**:task_memory 在一个 skill 内是恒定的,却没有走任何缩减或跨请求复用。

---

## 5. 成本估算(skill_0001,gpt-5.5)

价格假设见 §7。token 估算 `3.5 chars/token`。

| 场景 | 请求数 | 输入 tokens | 输出 tokens | **估算成本** |
|---|---|---|---|---|
| **首轮 1 票,无升级**(下限) | 3,366 | ~485 M | ~0.63 M | **~$613** |
| 默认策略,全部升级到 3 票(上限) | 13,464 | ~1,941 M | ~2.5 M | **~$2,451** |

- 真实成本落在两者之间,取决于有多少 unit 命中 `shouldEscalatePack`(高风险/不确定/票差≥0.35)。
- 缓存全命中 → $0(`doe-llm-cache.jsonl`),但首次跑必须付首轮这一档。
- 输出成本占比极小(<2%),**成本几乎全在输入**,这进一步说明削减重复输入(task_memory)是关键杠杆。

**一句话**:skill_0001 首次完整跑一遍,gpt-5.5 下大约 **$600(仅首轮)到 $2400(全升级)**;其中约 **3/4 的钱花在重复发送 task_memory**。

---

## 6. 进一步压缩的可行方向(按性价比排序)

1. **task_memory 去重 / 瘦身(预计省 ~70% 输入,最高优先级)**
   - 让 task_memory 也过一遍预算裁剪:`instructionText`/`preview`/`readme` 套用 `maxTextChars`,task_context_nodes 按与本 unit 路径相关性筛选而非全量塞入。
   - 真正按 batch 复用:既然几乎 1 unit/请求,可只发该 unit `task_memory_evidence_ids` 引用到的节点子集,而不是整个 skill 的节点表。
   - 若 endpoint 支持 prompt caching,把 shared_context 放在固定前缀以命中缓存。

2. **提高每请求装载的 unit 数**:当前 `maxBatchChars=60000` < 单 pack 字符,导致批根本装不下 2 个,task_memory 摊销不掉。先做 (1) 把 pack 和 shared 都压下来,再调大 batch,让 task_memory 在多 unit 间摊薄。

3. **降低 eligible 基数**:门控 3,403 仍偏多。可对同一 (node, label) 的近似重复 unit 去重后只判一次,或对 boundary_risk 阈值做更细分层。

4. **pack 内常驻冗余**:`fullFormalSemantics` / `fullNodeForEvidence` 会把空字段也补全展开([evidence-pack.js:257](packages/skill-doe-analyzer/src/evidence-pack.js#L257))。可在 compact 阶段剔除全空字段(无损),对 74 K 的 pack 能再挤几个百分点。

> 注意:(1)(2) 会改变发送内容,需按你「准确性不可降」的约束做 A/B 验证(参照 `results/ab-sample` 的做法);(3)(4) 中无损部分可直接上。

---

## 7. 价格假设(请按实际 endpoint 校准)

本文成本用占位价:**输入 $1.25 / 1M tokens,输出 $10 / 1M tokens,3.5 chars/token**。

实际请替换为你所用 endpoint(xiaomuai / echoflow / 官方)的 gpt-5.5 真实单价 —— 成本与单价成正比,把上表的输入 token 数(485 M / 1,941 M)乘以你的真实 $/1M 即可。

复现命令:

```bash
# 首轮下限
ESC_POLICY=none node --max-old-space-size=8192 \
  scripts/measure-doe-cost.js \
  results/sample-skill1/fcg/skills/skill_0001-00001_self-improving-agent_3.0.21-fcg.json 4 1 3

# 改价:PRICE_IN / PRICE_OUT / CHARS_PER_TOKEN 环境变量
```

测量脚本:[scripts/measure-doe-cost.js](scripts/measure-doe-cost.js)(用 mock client 拦截 payload,不消耗真实配额)。

---

## 8. 已落地优化(2026-06-14,§3-6 之后的实际改动)

本节记录在上面分析之后**真正实施并验证**的优化。约束:规则版判定数值不下降(已数学证明 + 端到端验证)。

### Part B — 必要性 4 分量 → 3 分量
`flow_path_task_need` + `boundary_node_task_need` 合并为单一 `task_need = min(两个子信号)`。因 `min(a,b,min(c,d)) ≡ min(a,b,c,d)`,规则版 `necessity_score` 逐位不变(3 个 skill × 160 unit 实测 0 mismatch)。收益:LLM 输出 schema 从 4 分量降到 3,prompt 更短、judge 推理更聚焦。详见 [[doe-necessity-3component-optimization]] 记忆。

### Part C — `flow.path_node.*` 去重
路径节点证据从完整对象(`fullNodeForEvidence`)降为精简 stub(id/name/semanticKind/operation_type/instructionText/location)。实测路径节点与 shared task_memory 节点 **100% 重复**(nano-banana 7/7、polymarket 20/20),完整细节仍在 `task_context_evidence` 保留,故无损。

### Part D — `task_memory` 自重复字段删除(本节核心)
`buildSharedTaskMemory` 旧返回里有 ~40% 的结构性自重复:
- `task_context_nodes[]` 是 `evidence[]` 中 node 项的镜像;
- `documentation_sources[]` 是 doc 项的镜像;
- 顶层 `description` / `readme_preview` 重复 `evidence[0].data`。

LLM 只能引用 `evidence[]` 里的 evidence_id(经 `taskMemoryEvidenceIdsForPack` 只取 `evidence`),这些并列字段对模型零价值。已删除,仅保留 `task_context_node_count` / `documentation_source_count` 供统计。**纯无损**,task_memory 单份从 ~51 K → ~28.7 K(降 ~44%)。

### Part E — 按引用裁剪 task 节点(评估后**不做**)
设想:每请求只发该 batch 引用到的 task 节点。实测每个 unit 实际引用了几乎全部节点(49.2/50、25.8/27),因为单 pack 的 `task_context_evidence` 已含路径节点 + 全 skill `taskContextCandidates`。裁剪只省 1-3% 且有损,不值得。

### 实测收益(官方 gpt-5.5 价,首轮 1 票)

| skill | eligible | 优化前 shared 占比 | 优化后 shared 占比 | 优化后单 skill 成本 |
|---|---|---|---|---|
| nano-banana | 20 | ~76% (单份 ~51K/请求) | 30.2% (单份 ~28K) | ~$0.92 |
| polymarket | 36 | — | 20.8% | ~$1.47 |
| github | 12 | — | 13.2% | ~$0.42 |

> **结论**:无损优化(B/C/D)已挖到顶。shared_context 占比从 ~76% 降到 13-30%,大头转移到 evidence_packs 本身。再往下削减 evidence_packs 或 task 节点都是**有损**的,需按「准确性不可降」做 A/B 验证后才能上;**最大的剩余非代码杠杆是 endpoint 的 prompt caching**(shared_context 内容在一个 skill 内恒定,天然适合缓存前缀)。

---

## 9. 第三轮:task_context 构造期去重(线 A,2026-06,无损)

§8 之后又发现一个量级更大的浪费,但它在**构造期(内存/延迟)**而非最终 token——因为 `task_context_evidence` 在 prompt 阶段已被 `compactSectionsForPrompt` 剥离合并。

**问题**:`evidence-pack.js: addTaskContextEvidence` 给**每个 pack** 都用 `fullNodeForEvidence`(~20 字段完整对象)展开了全 skill 的候选节点。但唯一的消费者 `buildSharedTaskMemory` 只读其中 **7 个字段**(id/name/semanticKind/operation_type/instructionText/location/source_line),其余十几个字段(semantic_gate、action_evidence、member_steps、ownerScript、docActions、完整 formal_semantics)**构造出来就被丢弃**。

实测构造-vs-发送浪费比:**polymarket 466×、nano 147×**(每 pack 建 73~116K task_context,最终只发一份 14~28K)。

**改法**(`taskContextNodeForEvidence`):task_context 节点只产出消费者实际读的 7 字段投影。对发送给 LLM 的 shared task_memory **逐字节无损**(消费者本就只取这 7 字段,已验证 25/25、48/48 节点全字段填充一致)。

**收益**:task_context_evidence 构造体积 polymarket **6.76M → 2.05M(−70%)**、nano **4.18M → 1.41M(−66%)**。最终 LLM token 不变(本就不发完整版),省的是**内存峰值与 pack 构造延迟**——这正是 skill_0001(3403 unit × 全节点完整展开)DOE 慢的一个根因。

**边界**:边界节点(observation 节点)的完整细节仍在 `local_action_receiver_evidence`(`local.action_text` / `local.formal_semantics`)原样保留;被精简的是 task_context 里非边界路径节点的、从未发给 LLM 的重字段。

> 下一步(线 B,需改 `security_profile` schema,涉及 SFG/DOE 接口契约,**先出方案文档与师兄对齐再动**):SFG 侧 `label_flows[].label` 内联重复(实测 100 flow / 22 distinct,4.3×)、`filter_events`(224/100 distinct)用「id 引用 + 去重表」替代。这主要省**磁盘 + 解析延迟**(provenance_graph 占 security_profile 43% 但不直接进 pack),需同步改 evidence-pack 读取端。

