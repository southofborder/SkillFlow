# DOE 送审 dedup 键完备化方案(origin_class + transform_seq)

> **历史文档(点时方案)**:本文是 dedup 键设计阶段的提案快照。其核心提议——把 **transform_seq(有序 transform 前缀)加入去重键**——在后续实现中被**推翻**:实测该分量是唯一无界驱动、会造成状态空间爆炸,已从键中移除(键回退为 JS-8 + `origin_class` 的有界元组,顺序信息改由单父链在传递层重建);`reduction_applied` 则以反链值形式进键。详见记忆 [[flood-transform-sig-dekey]] / [[flood-key-origin-node-explosion-fix]] / [[reduction-antichain-key-component]]。**本文刻意不回填这些后续结论**,仅更新品牌名与失效路径。图引擎已更名为 SFG(Skill Flow Graph),DOE(Data Over-Exposure)沿用原名;包内 `doe-analyzer.js` 等内部标识符按镜像规则保留不变。

## 0. 背景与决策依据

**问题**:当前送审去重键 = `observation_id | label | transform_set`,其中 `transform_set` 是 transform 类型的**无序去重集合**。这个键在两个维度上**不健全**(unsound),会把 necessity 判定其实不同的流错误合并、只送一条代表:

1. **transform 顺序/次数**:`redact→send` 与 `send→redact`、单次 vs 多次脱敏,necessity 不同,但集合签名相同 → 错误合并。
2. **origin(数据来源)**:同一汇点、同 label、同 transform 集合,但来源信任类不同(如"用户自己的输入回给用户" vs "第三方抓取的数据发同一汇点"),necessity 不同,但键里无 origin → 错误合并。

**决策定性(已与用户确认)**:这是**键完备性 / 逻辑自洽**问题,不是成本/收益权衡。判据:*dedup 键必须是 necessity 判定的充分统计量——凡 necessity 可能依赖的维度都必须进键*。某维度在当前语料里"暂未观测到翻转"不构成省略理由(小语料 = 证据不足,非安全证明)。故 **origin_class 与 transform_seq 两者都加**。

**送审量代价**(20-skill / 4336 gated 单元实测,组数 = 送审次数):

| 键 | 组数 | vs 基线 | vs gated 仍省 |
| --- | --- | --- | --- |
| 基线 `obs\|label\|transform_set` | 1464 | — | 66.2% |
| +origin_class | 2179 | +48.8% | 49.7% |
| transform_seq 替换 set | 2901 | +98.2% | 33.1% |
| **全加(本方案)** | **3354** | **+129.1%** | **22.6%** |

代价是"正确键的真实成本",此前的低组数是错键的假节省。全加后仍保有 22.6% 送审压缩。

> 注:早期方案稿曾引用一版更低的数字(基线 944、全加 2879、省 33.6%)。那来自探针的一个 label 维度 bug —— 把 assessment 顶层的字符串 `label` 传给 `labelKey`(该函数期望 label 对象),导致镜像键的 label 段恒为空、组数被系统性低估。实现时已修正(探针改用 `labelFlow.label` 对象),并加了"生产 `_dedup_key` 组数 == 探针镜像"的一致性断言锁死。上表为修正后的真实值。

---

## 1. "origin_node → trust_class 粗化"是什么意思

`origin_node` 是节点 **id**(如 `node_017`),全语料几百上千个不同值。若直接把 id 进键 → 每个来源节点自成一组,dedup 退化到接近无去重(与之前 flow_mode 进 flow_state_key 导致 116→297 分裂同类错误)。

**粗化 = 不进 origin 的身份,进 origin 的"安全语义等价类"**。两个来源节点若安全语义等价,则它们引入的数据对 necessity 而言可互换,应留在同一 dedup 组。等价类由 origin 节点的 `node_profile` 决定:

```text
origin_class = `${trust_boundary}/${surfaceClass}`
```

- `trust_boundary`:实测全语料仅 5 个值 —— `model_provider` / `user_visible` / `local_process` / `persistent_storage` / `external_network`。这是"数据从哪个信任域进入"的核心语义,直接决定 receiver/necessity 的判断基调。
- `surfaceClass`:`data_surface` 归一(`llm_context` / `local_file` / `runtime_env` / `network` / ...),补充"以什么形态进入"。

**不纳入 node_roles**:实测 node_roles 组合噪声大(95 个 distinct 签名多因 roles 排列),且 role 是"节点能做什么"的全局能力,非"本 label 从此处进入"的来源语义,纳入会过度切分。origin 的 necessity 相关投影 = trust_boundary + surface,足矣。

**回退**:origin_node 缺失或 profile 查不到时,`origin_class = 'unknown'`(而非 node_id,避免退化)。origin_node 实测 100% 填充,回退仅防御。

---

## 2. "transform_seq"是什么

替换现有无序集合签名 `transformSignature`,改为**有序 + 计次**签名:

```text
transform_seq = 沿 resolved node_path 顺序,
  逐节点展开该节点上发生的 real transform 类型(不去重、不排序),
  join('>')  ;  空 = 'none'
```

- 复用生产 `transformsByNode(labelFlow, flowById, filterEventById)` 拿到 `node_id -> [transform...]`,再用 `resolveLabelFlowPath` 的 `node_path` 定序。
- 顺序天然区分"脱敏在外发前 vs 后";不去重天然区分"脱敏一次 vs 多次"。
- 与当前 `transformSet` 相比,只在"同类型集合、但顺序或次数不同"时产生新分组,其余完全一致(集合相同且顺序相同的流仍合并)。

---

## 3. 改动清单(全部在 `packages/skill-doe-analyzer/src/doe-analyzer.js`)

去重逻辑与键构造已全部集中在此文件,SFG / evidence-pack / necessity / exposure **零改动**。

### 3.1 新增 `originClass(labelFlow, context)` 辅助函数

- 从 `context.evidencePackContext.profileByNodeId`(已存在,见 `createEvidencePackContext`)取 origin 节点 profile。
- 无 context 时退化到直接从 `fcgJson.security_profile.node_profiles` 建的临时索引(保持纯函数可测)。
- 返回 `${trust_boundary}/${surfaceClass}`,缺失回退 `'unknown'`。
- `surfaceClass` 用一个小归一表,未知 surface 原样透传。

### 3.2 用 `transformSequence(labelFlow, context)` 替换现有 `transformSignature`

- **函数已重命名** `transformSignature` → `transformSequence`(旧名描述无序集合签名,与有序计次语义不符,遂改名以名副其实;调用点仅 3.3 一处)。
- 内部:`transformsByNode` + `resolveLabelFlowPath(node_path)` 定序展开;`byNode` 为空直接返回 `'none'`(省一次路径解析)。
- 注意 `transformsByNode` 已顺 parent 链累积,`node_path` 已按 P1 裁到 origin —— 两者对齐,不会把裁掉的前缀 transform 带进来(已验证:只展开 node_path 内节点的 transform;order 单测确认 redact_drop>summarization ≠ summarization>redact_drop)。

### 3.3 改 `_dedup_key` 构造(doe-analyzer.js:208)

```js
// 旧:
_dedup_key: `${obs}|${label}|${transformSignature(labelFlow, ctx)}`
// 新:
_dedup_key: `${obs}|${label}|${transformSequence(labelFlow, ctx)}|${originClass(labelFlow, ctx)}`
```

键顺序:obs、label、transform_seq、origin_class。四段用 `|` 分隔,各段内部已无 `|` 冲突(origin_class 用 `/`,transform_seq 用 `>`)。

### 3.4 dedup 溯源字段扩充

- `assessment.llm_judge.dedup` 已记 `{role, representative_unit_id, group_size}`。
- 新增 `dedup.key = {transform_seq, origin_class}`(由 `dedupKeyBreakdown` 从 `_dedup_key` 拆解;obs/label 已是 assessment 顶层字段,不重复),便于审计"为何这几条被合并"。
- `stripInternalFields` 保持清 `_dedup_*`;`dedup.key` 是 `llm_judge` 下的公开字段(非 `_` 内部字段),不受 strip 影响。无新增内部字段。

---

## 4. 无损 / 健全性验证(实现后必须跑)

### 4.1 单元测试(新增到 `doe-analyzer.test.js`)

1. **transform 顺序分组**:构造两条同 (obs,label)、transform 类型集合相同但顺序相反(redact→send vs send→redact)的流 → 断言落入**不同** dedup 组、各自送审。
2. **transform 次数分组**:同类型出现 1 次 vs 2 次 → 不同组。
3. **origin_class 分组**:两条同 (obs,label,transform_seq)、但 origin 节点 trust_boundary 不同(model_provider vs external_network)→ 不同组。
4. **origin_class 合并**:两条 origin 节点不同 id 但 trust_boundary+surface 相同 → **同组**(验证粗化生效,未过度切分)。
5. **回退**:origin_node 缺失 → origin_class='unknown',不崩、不各自成组。
6. **等价保持**:完全相同的两条流(obs/label/seq/origin 全同)→ 仍合并送 1(回归旧行为)。

### 4.2 语料级验证(扩展现有探针 `scripts/dedup-granularity-probe.js`)

- 跑全 20 skill,确认新键组数 = 2879(与预测一致),无异常膨胀(防止实现 bug 把 origin_node id 带进键)。
- 抽样:打印若干多成员组,人工确认组内成员的 origin_class 与 transform_seq 确实一致(键健全性肉眼校验)。

### 4.3 回归

- `node --test "packages/skill-doe-analyzer/test/**/*.test.js"`(当时 49 全绿)
- SFG 侧回归(应不受影响)。历史注:此方案落笔时 SFG 尚为 JS,原文写 `node --test "packages/skill-fcg-analyzer/test/**/*.test.js"`(当时 109 全绿);SFG 现已整体重写为 Python,回归改跑 `python -m pytest packages/skill-sfg/tests`。
- 规则分 / necessity 三分量 / exposure **必须逐位不变**(本改动只动送审分组,不动任何打分)。

---

## 5. 明确不做

- **不改门控** `shouldJudgeAssessmentWithLlm`(仍 sensitivity≥high && boundary_risk≥0.75)。
- **不改 ③ observation_id→boundary 元组合并**:那是往"更多合并"方向、风险方向,与本方案(往更细、更健全方向)相反,放弃。
- **不改 SFG / evidence-pack / necessity-baseline / exposure-scorer**:键完备化是纯 DOE 送审侧逻辑。
- **不加开关**:直接替换(遵循既往 DOE 重构惯例)。

---

## 6. PROMPT_VERSION

`_dedup_key` 不进 LLM prompt 内容(只决定送谁),故**不需要 bump PROMPT_VERSION**——同一 pack 的 prompt 文本与缓存键不变。确认 llm-judge 缓存键基于 pack 内容而非 dedup_key 后落定(实现时核对)。

---

## 7. 一个诚实的保留

本方案的**代价**(送审 +129%、组数 3354)在小语料上可靠。但 origin_class / transform_seq 的**收益**(实际挡下多少 necessity 误判)在这 20-skill 语料上仍是 0 可观测——因为门控后路径耦合样本稀少。加这两维的正当性来自**键的逻辑完备性**(necessity 依赖它们 ⇒ 键必须含它们),而非语料收益。这一点在实现后、更大语料可用时应复测收益,以确认代价换到了真实精度。
