# 线 B 方案:SFG `security_profile` 精简(接口契约变更,待对齐)

> **历史文档(2026-06 时点)**:本文记录 `label_dictionary` + `label_id` 去重契约落地时的状态与实测数据。彼时 SFG 产出端为 JS(`transfer-analysis.js` / `graph-transfer-analyzer.js`、`security_profile.version 5.0`),现已整体重写为 Python(包 `skill-sfg`);DOE 读取端仍为 JS。文中大写引擎名已更新为 SFG(Skill Flow Graph)/ DOE(Data Over-Exposure),但**内部标识符(`doe-analyzer.js`、`label-resolver.js`、`security_profile`、`label_flows`/`flow_states`/`label_id`/`label_dictionary` 等字段名、往返测试名)按镜像规则保留不变**,且旧 JS 文件路径与版本号作为历史记录不回填。
>
> 状态:**全链路已实现(SFG 产出端 + DOE 读取端),190 测试全绿**。
> SFG 现产出 `security_profile.version: "5.0"` + 顶层 `label_dictionary`,`label_flows[]`/`flow_states[]` 用 `label_id` 引用(无 id 的 label 仍内联,无损)。DOE 透明读两种格式。
> 数据基准:`results/ab-sample` 三个真实 skill(2026-06 实测)。

## 0. 已完成 vs 待办(对齐用)

| 部分 | 状态 | 负责 |
|---|---|---|
| DOE 读取端兼容层 `label-resolver.js`(`resolveLabel` / `buildLabelDictionary`) | ✅ 已实现 | 我 |
| DOE 边界统一规范化(`doe-analyzer.js` labelFlowById,下游 scorer 零改动) | ✅ 已实现 | 我 |
| 悬空 `label_id` 显式告警(`label_dictionary.miss`,不静默缺省) | ✅ 已实现 | 我 |
| **SFG 产出 `label_dictionary` + `label_id`** | ✅ 已实现(`transfer-analysis.js`) | 我 |
| SFG `security_profile.version` 4.9→5.0 + schema + statistics.label_dictionary_count | ✅ 已实现 | 我 |
| 新旧格式判定一致性 + 告警 + SFG 往返测试 | ✅ 192 全绿 | 我 |
| `filter_event_dictionary`(§3.2,可选,收益小) | ⬜ 暂缓 | 后续评估 |
| `provenance_graph` 精简(§3.3,仅省延迟) | ⬜ 暂缓 | 后续评估 |

**实测收益(label 去重)**:label_flows 体积省 17-20%(polymarket 213K→170K);DOE 判定零 mismatch、零 miss warning。

---

## 1. 背景:为什么要做线 B

线 A(DOE 构造期 task_context 去重)已无损完成,把 DOE 侧的构造浪费砍掉 ~70%。但那是 DOE 内部。线 B 处理的是**上游 SFG 产出本身的结构冗余**——它影响:

- **磁盘体积**(skill_0001 的 SFG 达 117 MB);
- **解析延迟**(DOE 每次要 `JSON.parse` 整个 SFG);
- 间接影响 DOE 构造(读取冗余字段)。

注意:线 B **不直接降 LLM token**——下面会解释为什么。

---

## 2. 实测:`security_profile` 的冗余分布

| skill | security_profile | label 冗余 | filter_events 冗余 | provenance_graph 占比 |
|---|---|---|---|---|
| polymarket | 613 KB | 100 flow / **22 distinct** → 省 77% | 224/100 distinct → 省 14.7K | **43%**(不进 pack) |
| github | 154 KB | 18 / **6 distinct** → 省 66% | 36/18 → 省 2.1K | 35%(不进 pack) |
| nano-banana | 643 KB | 100 / **37 distinct** → 省 60% | 163/100 → 省 7.6K | 31%(不进 pack) |

三个结论:

1. **`label_flows[].label` 内联重复严重**:每个 label_flow 内联一份完整 label 对象(~600 字符,含 id/category/subtype/sensitivity/field_name/field_path/origin_node/introduced_at/mode/...),但实际只有 6-37 种不同的 label。**60-77% 是重复**。
2. **`filter_events` 重复**:跨 flow 大量相同事件被各自内联。
3. **`provenance_graph` 占 security_profile 的 31-43%,但它不直接进 LLM pack**(DOE 只通过 `prov.events.*` 取相关事件)。所以精简它省的是磁盘/解析延迟,不是 token。

---

## 3. 方案:引用 + 去重表

核心思想:把"每个 flow 内联完整对象"改为"flow 持 id 引用 + 顶层一张去重表"。

### 3.1 `label` 去重(收益最大,优先)

**现状**(`graph-transfer-analyzer.js` 产出,`transfer-analysis.js: compactPublicLabelFlow` 透出):

```jsonc
label_flows: [
  { label_flow_id: "lf_1", label: { id:"label_3f4d...", category:"ai_context", subtype:"user_prompt", sensitivity:"medium", field_name:"query_text", field_path:"...", origin_node:"...", ... }, ... },
  { label_flow_id: "lf_2", label: { /* 完全相同的对象再来一遍 */ }, ... }
]
```

**方案**:

```jsonc
security_profile: {
  label_dictionary: {                      // 新增:去重表
    "label_3f4d...": { id:"label_3f4d...", category:"ai_context", subtype:"user_prompt", sensitivity:"medium", field_name:"query_text", ... }
  },
  label_flows: [
    { label_flow_id:"lf_1", label_id:"label_3f4d...", ... },   // 改:label -> label_id 引用
    { label_flow_id:"lf_2", label_id:"label_3f4d...", ... }
  ]
}
```

label 对象已有稳定 `id` 字段,直接用作字典 key,无需新造。

### 3.2 `filter_events` 去重(同模式)

`filter_events` 已有 `event_id`。顶层加 `filter_event_dictionary: { event_id -> event }`,flow 内只留 `filter_event_ids: []`(现在其实已有这个数组,只是同时又内联了完整 `filter_events`——可直接去掉内联,保留 id 数组 + 顶层字典)。

### 3.3 `provenance_graph`(可选,仅省磁盘/延迟)

优先级低。它不进 pack,精简只对超大 skill(skill_0001)的解析延迟有意义。可作为后续单独评估。

---

## 4. 影响面:两边都要改

### 4.1 SFG 侧 —— ✅ 已实现

| 文件 | 实际改动 |
|---|---|
| `security/transfer-analysis.js` | 新增 `createLabelDictionary()`(去重收集器)+ `emitLabelRef(label, dict)`(产出 `{label_id}` 或无 id 时回退 `{label}` 内联) |
| `security/transfer-analysis.js: compactPublicLabelFlow` / `compactPublicFlowState` | 内联 `label: compactPublicLabel(...)` → `...emitLabelRef(...)`,二者共享同一字典 |
| `security/transfer-analysis.js: buildProfileFromNodeProfiles` | 建共享 `labelDictionary`,输出顶层 `label_dictionary`;`version` 4.9→**5.0**;statistics 加 `label_dictionary_count` |
| `output/json-generator.js: fcgSchema` | security_profile 加 `label_dictionary` 字段 |

**无损保证**:label 有稳定 `id` 字段(实测 id→内容严格 1:1)。无 `id` 的 label **保持内联**(`emitLabelRef` 回退),不进字典 → 不会丢。DOE 端 `resolveLabel` 内联优先,两种都正确读。SFG 测试用 `rehydrateLabels` 把引用解析回内联做断言,本身即往返无损校验。

### 4.2 DOE 侧 —— ✅ 已实现

实际落地的设计比原计划更干净:**不在各 scorer 散落 `resolveLabel`**(那会让数据流模糊),而是在**唯一边界**统一规范化一次。

| 文件 | 实际改动 |
|---|---|
| `label-resolver.js`(新增) | `resolveLabel(labelFlow, dict, onMiss)` + `buildLabelDictionary(securityProfile)`。单一解引用入口 |
| `doe-analyzer.js: analyzeDoeRuleOnly` (L58-66) | 在 `labelFlowById` 这个**唯一边界**处把每个 flow 的 label 规范化(内联优先,否则查字典)。下游 exposure/necessity/group/evidence-pack/confidence **全部零改动**——它们继续读 `labelFlow.label`,数据流与改造前完全相同 |
| `doe-analyzer.js` warnings (L74-80) | 悬空 `label_id` → push `{kind:'label_dictionary.miss', label_flow_id, label_id}`,**显式可追溯,绝不静默缺省** |
| `evidence-pack.js: createEvidencePackContext` | context 挂 `labelDictionary`,供 `flow_states[].label`(非边界规范化路径)解引用 |

**为什么这样不会"数据流不清晰/缺省"**(直接回应该顾虑):

1. **解引用只发生在一个地方**(边界 labelFlowById),不是散落各处的 `|| dict[id]`。
2. **缺省显式报警**——找不到的 `label_id` 进 warnings,不会悄悄变 `{}`。
3. **`label.id → 内容严格 1:1` 已实测验证**(3 skill 零冲突),含 `field_name`/`field_path`,所以按 id 去重无损。
4. **新旧格式判定逐字段一致**已由测试 `Line B: dictionary-referenced labels produce identical verdicts` 证明。

> 兼容策略(已实现):内联 `label` 优先,无则查 `label_dictionary[label_id]`。新旧 SFG 都能读,师兄改 SFG 期间 DOE 不崩。等全部 SFG 重跑为 5.0 后,可选地移除内联分支。

---

## 5. 收益与代价权衡

| 项 | 收益 | 代价 |
|---|---|---|
| label 去重 | security_profile 省 ~30-40%(label 占大头);磁盘/解析延迟同比降 | 改接口 schema;两边代码 + 测试;一次性 SFG 重跑 |
| filter_events 去重 | 再省 ~2-15K/skill | 同上,较小 |
| provenance_graph | 仅超大 skill 延迟 | 改动复杂,优先级低 |

**不省 LLM token**:因为 pack 里的 label 来自 `label.main`(每 unit 一份,本就是按需取的),去重表是 security_profile 内部的存储优化,不改变"每个 pack 携带它自己那份 label"。token 优化已在线 A/B/C/D 做完。

**结论建议**:label 去重值得做(收益明确、模式干净);filter_events 顺带做;provenance_graph 暂缓。**前提是先确认 DOE 侧 `resolveLabel` 兼容层 + 师兄同步改 SFG,且 `version` bump 到 5.0 让两边显式对齐。**

---

## 6. 待确认问题(对齐时讨论)

1. 去重表放 `security_profile` 顶层(`label_dictionary`)还是放 SFG 根级?建议前者,与现有 `provenance_store` 同级。
2. 旧 SFG 数据(`results/clawhub-top-k10000` 等)要不要重跑?还是靠 `resolveLabel` 兼容层永久兼容?
3. `version` bump 到 5.0 后,DOE 是否要拒绝读 < 5.0 的数据(强一致),还是兼容读(渐进)?我倾向兼容读。
4. 线 B 做完后是否值得再花时间做 provenance_graph?取决于是否要常态化跑 skill_0001 这类超大 skill。
