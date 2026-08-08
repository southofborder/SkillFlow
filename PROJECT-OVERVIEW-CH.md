# SkillFlow 项目工作总览

> 目的:向协作者交代「我们到底在做什么、做到哪一步、每块的颗粒度如何」,用于对齐分工与写作粒度。
> 维护:本文件描述截至 2026-07 的状态,代码以 `packages/` 为准。英文版见 `PROJECT-OVERVIEW.md`。

---

## 1. 一句话定位

SkillFlow 是一套针对 **Agent Skill(ClawHub 上的可下载 skill 包)** 的**数据过度暴露(Data Over-Exposure, DOE)**静态分析流水线。
它回答的核心问题是:

> 一个 skill 在完成它声称的任务时,是否把**超出任务必要范围的敏感数据**送过了信任边界(发给外部 LLM、外部服务、持久化存储等)?

不是简单的"有没有敏感数据流出",而是**"这次流出对完成声称的任务是否必要"**——必要的暴露不算 DOE,不必要的才算。这是本工作区别于普通污点分析(taint analysis)的关键。

---

## 2. 研究问题与核心概念

| 概念 | 含义 |
| --- | --- |
| **boundary observation(边界观测)** | 数据在某节点跨越信任边界的事件(如把数据交给 LLM 推理、发给外部 API、写入存储) |
| **label(标签)** | 数据的敏感性分类:`category.subtype` + `sensitivity`(low/medium/high/critical) |
| **label_flow(标签流)** | 被打标的数据在流图中走过的完整路径(**单流**:每条 flow 溯源到唯一真源,≤1 个父) |
| **assessment unit(评估单元)** | `(observation × label_flow)`,DOE 的最小判定粒度 |
| **exposure(暴露度)** | 这次跨边界本身有多"危险"(边界类型、接收方范围、敏感度) |
| **necessity(必要性)** | 这次暴露对完成 skill 声称任务有多"必要" |
| **DOE score** | `exposure × (1 - necessity) + baseline_adjustment` —— 越高越是过度暴露 |

必要性由 **3 个分量(component)** 构成,DOE 的必要性取这 3 项的**最小值**(短板决定,`COMPONENT_KEYS` 见 `necessity-baseline.js`):

- **`action_input_need`**:这个动作的**输入**是否真的需要这个标签的数据(局部)
- **`receiver_semantic_need`**:**接收方**的语义是否真的需要这个标签(局部)
- **`task_need`**:整条 label_flow 路径 + 边界节点是否属于完成声称任务所需(全局)

> **颗粒度提醒(2026-06 优化)**:`task_need` 是把旧的 `flow_path_task_need` + `boundary_node_task_need` 两个分量**合并**成的单一全局问题。规则层 `task_need = min(flow_path信号, boundary_node信号)`,因 `min(a,b,min(c,d)) ≡ min(a,b,c,d)`,**规则版 necessity_score 逐位不变**;两个子信号仍在 `global_necessity.{flow_path_signal, boundary_node_signal}` 里透出供调试。LLM 侧把它作为**一个问题**问,schema/输出减半,降成本降延迟。

---

## 3. 三阶段流水线(端到端)

入口:`scripts/skillflow-pipeline.js`,默认 `all` 流程。配置见 `skillflow-pipeline.config.cjs`,两份 pipeline README(`README-PIPELINE.md` / `README-PIPELINE-CH.md`)。

```text
                    ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐
ClawHub top-k  ───▶ │ 1. Download │──▶│ 2. FCG 流图分析   │──▶│ 3. DOE 过度暴露评分  │
   (按下载量)        └─────────────┘   └──────────────────┘   └─────────────────────┘
                          │                   │                        │
                    zips/ 下载          fcg/skills/*.json        doe/skills/*.json
                                        + flow.md / flow.mmd      + doe-summary.{json,md}
```

可选的 **similarity grouping**(相似 skill 聚类)默认关闭,只有 `--with-similarity`(或 `--phase download-group`)才跑。

### 阶段 1 — Download(`packages/skill-similarity-analyzer` 复用)

按 `downloads` 排序抓 ClawHub 前 k 个 skill zip。带并发、重试、超时。

### 阶段 2 — FCG(Flow-Control Graph,`packages/skill-fcg-analyzer`)

> FCG 是整条链路里代码量最大的一块(`src/` 约 1.5 万行),也是 DOE 的唯一输入来源。
> 这一节按「编排流程 → 输出接口 schema → LLM 介入点」三层展开,供和 DOE 的输入契约对齐。

#### 2.1 它在做什么

把一个 skill 包(`SKILL.md` + README + 脚本 + 其他文档)解析成一张**有向流图**,并在图上叠加一层**安全语义画像(security_profile)**。

- 图(`nodes` / `edges`):谁把数据传给了谁。
- 安全画像(`security_profile`):每个节点处理什么敏感数据(label)、数据沿什么路径流动(label_flow)、在哪里跨越了信任边界(observation)。

DOE 阶段**只读 `security_profile`**(observations / label_flows / node_profiles / provenance_store / provenance_graph / label_dictionary),图本身(nodes/edges/paths)主要供人读报告与调试。这是两阶段之间的接口边界。

> **提取粒度:块分类 + 策略派发(2026-07 重写)**。提取不再"一律按行跑关键词",而是**先判文件类型,再判内容块类型,再派发对应策略**:
>
> - **文件类型**:指令文档(SKILL.md/README)vs 非指令文档(changelog/license/notice/contributing 等,`document-context.js` 的 `NON_INSTRUCTION_MD` 挡掉,不产动作节点)vs 脚本(js/py/sh)。
> - **内容块类型**:代码块 / 表格 / 列点 / 散文 / 免责声明。shell 代码块与脚本里的 shell 命令**共用 `shell-command-classifier.js`**(确定性白名单:egress/exec/read/write + URL/host/重定向识别),逐命令建 sink(`curl`/`wget` 等外泄是最强 sink 证据,以前整块被丢);散文里的否定与免责声明("does not send…"、"What this skill does NOT do")识别后降为 `guard`/`context`,不再被反转成外泄动作;表格里的 condition 保留为边连接判据。
> - **列表块结构化(`segmentMarkdownBlocks`,2026-07)**:提取前先把散文/列点切成块。**多行 bullet**(续行缩进 ≥ 标记列)合并成一条,不再被拆成碎节点;**列表块继承 lead-in 免责作用域**——`**What this skill does NOT do:**` 下方 bullet 即使不重复否定词也整块降为 context;**反向保护**:软否定小节(如 `## Limitations`)里明确 imperative 指令不被压掉(weather `- PNG: curl … -o` sink 守住)。散文仍逐行(真实语料里"段落"多为整行多句,逐行≈逐段),不做跨行合并。
> - **脚本调用**:按角色分类(sink/source/sanitizer/noise)。语言内建(`push`/`map`/`console.log`/`Array.isArray` 等)作为噪声丢弃,**未知用户函数保留**(不猜为噪声),避免脚本节点爆炸。
> - 这层是**规则优先、LLM 只兜底歧义**,保住了默认零 LLM 的 token 成本。详见 §2.5 的语义门控。
>
> **连边的两股力(recall vs precision)**:type-analyzer 用**穷举候选 + 类型/签名兼容**保证"该连的连上"(防少连,跨块/跨节复杂数据流靠它);routing 层(`flow-instance-router`)用**条件/guard 语义**收紧"不该连的别连"(防多连)。抽取到的 `formal_semantics.conditions`(`when/if/unless/without` 等)经 node-profiler 透到 profile、进 `buildRouteText`;明确否定条件("unless redacted"、"only if not")把本会 definite 的 sink 路由**降级为 may_route**(不删边、不硬 block、无条件时维持现状,故不伤 recall)。

#### 2.2 编排流程(`src/index.js` 的 Phase)

入口类 `SkillFCGAnalyzer.analyze(inputPath)`,日志里每个 `[ok] ...` 对应一步:

| Phase | 步骤 | 模块 | 产物 |
| --- | --- | --- | --- |
| 1 | 解压/定位 skill 根目录 | `index.js` | skillRootDir |
| 2 | 解析 skill 文件 + 文档计划 | `parser/skill-parser`, `parser/document-context` | skillData / readme / 可执行文件清单 |
| 3a | 抽工具调用 | `parser/tool-extractor` | tool 节点 |
| 3b | 抽脚本数据流(JS/PY 等):调用按角色分类(sink/source/sanitizer/noise),内建噪声丢弃、未知用户函数保留;shell 命令走共享分类器 | `parser/script-flow-extractor`, `parser/shell-command-classifier` | script flow 节点+边 |
| 3c | 抽文档数据流:**先判文件类型(指令 md vs changelog/license 等非指令文档),再按块分类(代码块/表格/列点/散文/免责声明)派发提取策略**;列表块结构化(多行 bullet 合并、lead-in 免责作用域继承);shell 代码块逐命令建 sink,否定/免责声明降为 guard/context;顺序边默认**同节内**连(`FCG_SEQUENCE_EDGE_SCOPE=global` 可回退) | `parser/doc-flow-extractor`(最大), `parser/document-context`, `parser/shell-command-classifier` | doc flow 节点+边 |
| 3d | 注入隐式 `user.query` 源 + `llm.inference` 边 | `classifier/source-sink` | 激活流 / skill 内容→全局 LLM 边 |
| 4 | 稀疏类型兼容性分析(候选依赖边) | `parser/type-analyzer` | dependency candidates |
| 5 | 高价值依赖边 LLM 校验 | `analyzer/llm-validator` | validated edges |
| 6 | 建图 + 去重边 + 去环 | `analyzer/fcg-builder`, `analyzer/cycle-remover` | graph(nodes/edges) |
| 6b | **单跨界拆分**(连边后确定性拆分,每节点≤1数据跨界;child 继承父边、synthetic builtin 豁免) | `analyzer/node-splitter` | 拆分后的 graph |
| 7 | 路径抽取(调试用,上限 1500 条/长度 12) | `analyzer/path-extractor` | all_paths |
| 9 | 生成 JSON + **security_profile** + flowchart | `output/json-generator`, `security/*` | `*-fcg.json` / `.flow.md` / `.flow.mmd` |

> 模式 `mode`:`quick`(跳过 Phase 5 的 LLM 依赖校验)/ `full`(默认)/ `deep`(额外加结构化 control_flow 顺序边)。

#### 2.3 安全画像生成(Phase 9 内部,`security/` 子系统)

`generateFCGJson(Async)` → `buildTransferSecurityProfile`,在已建好的图上依次跑:

1. `node-profiler` — 给每个节点打 **label**(category.subtype + sensitivity)、operation_type、data_surface、receiver_scope、trust_boundary 等画像。可选 `label-llm-assistant` 对低置信标签做 LLM 辅助。
2. `graph-transfer-analyzer` — 在图上做**标签传播**,产出 `label_flows`(标签流,含 `node_path`/`node_names`/`edge_path`)、`flow_states`、`transitions`、各类事件(route/filter/merge/observation)。
3. `observation-analyzer` — 把跨边界事件归纳成 **observations(边界观测)**。
4. `provenance-extractor` — 建 `provenance_graph` / `provenance_store`(origins / path_classes / representative_paths),记录数据来源谱系。

#### 2.4 输出接口 schema(`*-fcg.json`,与 DOE 的契约)

顶层字段(schema 定义在 `output/json-generator.js` 的 `fcgSchema`):

```text
{
  meta:                { skill_name, skill_version, analysis_timestamp,
                         analyzer_version, input_source, analysis_mode }
  nodes:               [ ... ]           ← 图节点(见下)
  edges:               [ ... ]           ← 图边(见下)
  source_sink:         { sources[], sinks[] }
  paths:               { all_paths[], source_to_sink_paths[],
                         path_clusters[], path_compression{} }   ← 调试/人读用
  statistics:          { total_nodes, total_edges, source_count, sink_count, ... }
  risks:               [ ... ]           ← 规则版风险提示(非 DOE 判定)
  security_profile:    { ... }           ← ★ DOE 实际消费的部分
  documentation_context:{ ... }
}
```

**node(节点)关键字段**(`buildNodeJson`):

| 字段 | 含义 |
| --- | --- |
| `id` / `name` | 节点唯一 id / 规范名(如 `llm.inference`、`user.query`) |
| `type` | `tool_call` / `builtin_call` / `custom_func` |
| `category` | `Source` / `Sink` / `Intermediate` |
| `is_critical` | 是否关键 sink(数据外泄风险点) |
| `location` | `{ file, line, section }` 溯源位置 |
| `semanticKind` | `doc_step` / `doc_operation` / 脚本节点等 |
| `formal_semantics` | `{ operation_type, inputs[], outputs[], targets[], effects[], conditions[], evidence{} }` |
| `semantic_gate` | LLM 语义门控判定结果(见 2.5) |
| `instructionText` / `source_context` / `action_evidence` | 抽取到的原文与证据 |

**edge(边)关键字段**:`{ id, source, target, type, confidence, validation_method, data_flow{from_param,to_param,data_type}, semantic_reason }`,其中 `type ∈ {data_dependency, control_flow, semantic, doc_instruction}`,`validation_method` 标明是规则(`dependency_structural`/`dependency_rule`)还是 LLM 校验(`dependency_llm`)得来的。

**security_profile(★ DOE 输入)关键字段**(`security/transfer-analysis.js`,当前 `version: 5.1`):

| 字段 | 含义 | DOE 用途 |
| --- | --- | --- |
| `node_profiles[]` | 每节点的安全画像(label/operation/data_surface/receiver_scope/trust_boundary) | local 必要性 |
| `label_flows[]` | 标签流:`{ label_flow_id, label{...} 或 label_id, current_node, node_path, node_names, edge_path, flow_mode, confidence, origin_ids, parent_label_flow_ids[], path_class_ids, ... }` | 全局必要性、路径证据 |
| `label_dictionary` | 顶层去重 label 表(v5.0 起):`label_flows[].label_id` 引用它 | 解引用得到 label |
| `observations[]` | 边界观测:`{ observation_id, node_id, operation_type, boundary{trust_boundary,receiver_scope}, label_flow_ids[], ... }` | assessment unit 的 observation 侧 |
| `flow_states[]` | 标签流聚合状态 | 聚合证据 |
| `provenance_store` | `{ origins[], path_classes[], representative_paths[] }` | provenance 证据 |
| `provenance_graph` | 数据传播谱系(events) | filter/storage 证据 |
| `statistics` | `observation_count` / `label_flow_count` / `label_dictionary_count` / ... | 规模与日志 |

> **对齐要点 1**:DOE 的最小判定单元 `(observation × label_flow)` 直接来自这里——`observations[].label_flow_ids` 笛卡尔展开成 assessment unit。师兄若要替换/改 FCG,只要保证 `security_profile` 的这几个数组字段契约不变,DOE 侧无需改动。
>
> **对齐要点 2(v5.1 契约)**:label_flow 现在**自带 `node_path`/`node_names`/`edge_path`**(以前 DOE 靠 parent 链重建)。`edge_path` 遵守**位置契约** `len(edge_path) == len(node_path) - 1`(edge[i] 连 node[i]→node[i+1])。删掉了冗余的单数 `parent_label_flow_id`,统一读复数 `parent_label_flow_ids[0]`;每条 flow 是**单流**(≤1 父),父指针用于**溯源**(让 `source_introduction` 提取/概括步不被误判为源点),不是记合并。GNN/序列建模可直接消费 node_path,无需重建。
>
> **对齐要点 3(label_dictionary,v5.0 起)**:label 去重进顶层 `label_dictionary`,flow 用 `label_id` 引用;DOE 在唯一边界 `analyzeDoeRuleOnly` 的 `labelFlowById` 处解引用一次(内联优先,否则查字典,悬空 id 显式报 `label_dictionary.miss` warning),下游全部零改动。**这只省 FCG 磁盘/解析延迟,不省 LLM token。**

#### 2.5 LLM 在 FCG 里的 3 个介入点(都可关、都有缓存)

FCG 不是"一次大 LLM 调用",而是 3 个**独立、可分别开关**的 LLM 介入点:

1. **Markdown 语义门控 semantic gate(默认开,强门控)** — `doc-flow-extractor` + `script-flow-extractor`。规则只产候选节点,**LLM 判定每个候选的 actionability/classification/operation_type**,结果写进节点的 `semantic_gate`。缺 `LLM_API_KEY` 时 FCG 预检直接失败。这是 FCG 精度的主来源,也是耗时主来源。缓存:`<root>/fcg/semantic-gate-cache.jsonl`(跨运行/CI 持久)。
2. **依赖边校验(默认 `high_value` 策略)** — Phase 5 `analyzer/llm-validator`。只对高价值候选依赖对做 LLM 确认,产出 `validation_method=dependency_llm` 的边。`quick` 模式跳过。可调 `FCG_DEPENDENCY_LLM_*`。
3. **标签 LLM 辅助(默认关)** — `security/label-llm-assistant`。仅对 generic/低证据标签生成弱证据候选标签,标 `mode=llm_assisted`、`requires_review=true`,供 DOE 区分强弱证据。

> 关键性质:LLM 命中缓存 = 返回当初同一判定,**抽取质量完全一致,只降延迟**。这是"鲁棒性硬化不降准"约束在 FCG 侧的体现。

### 阶段 3 — DOE(`packages/skill-doe-analyzer`)

吃 FCG JSON,产出每个 assessment unit 的 DOE 判定。详见 §4。

---

## 4. DOE 分析器内部结构(本项目的核心,颗粒度最细)

源码:`packages/skill-doe-analyzer/src/`

| 文件 | 职责 |
| --- | --- |
| `doe-analyzer.js` | 主编排:rule-only 评分 → 选出该送 LLM 的 unit → 调 LLM judge → 融合 |
| `exposure-scorer.js` | 暴露度评分(边界是否跨越、边界风险、敏感度) |
| `necessity-baseline.js` | 规则版必要性评分(3 分量的 baseline,`COMPONENT_KEYS`) |
| `necessity-text-utils.js` | 必要性文本信号抽取辅助 |
| `group-baseline.js` | 同组 skill 的基线调整 |
| `label-resolver.js` | `resolveLabel` / `buildLabelDictionary`:兼容内联 label 与 `label_id` 引用 |
| `flow-path-utils.js` | label_flow 路径解析(自带 node_path 走快路径,否则按 parent 链重建) |
| `evidence-pack.js` | 把一个 unit 打包成 **flow-centric** evidence pack + 聚合 shared task_memory |
| `evidence-budget.js` | evidence pack 的分层压缩(防止上下文超长/超时) |
| `llm-judge.js` | LLM judge:打包 prompt、批处理、投票、升级复判、缓存、容错 |
| `path-report.js` | 人读报告生成 |

### 4.1 两层评分:规则 + LLM 融合

1. **规则层(rule-only,确定性、免费、离线)**:每个 unit 都先算一遍 exposure 与 3 分量 necessity baseline。规则打分器直接吃 FCG 对象、**不读 evidence pack**,故 pack 重构不影响规则分。
2. **LLM 门控**:`shouldJudgeAssessmentWithLlm` 只放行 `boundary_crossed && sensitivity≥high && boundary_risk≥0.75` 的 unit 去问 LLM。其余只用规则分。
3. **LLM judge**:对放行的 unit,LLM 基于 evidence pack 给 3 分量打分(PROMPT_VERSION `doe-llm-judge-v4-merged-task-need`)。
4. **融合**:`component = llmWeight·llm + (1-llmWeight)·rule`(默认 `llmWeight=0.7`),必要性取 3 分量最小值,再算 DOE score。

### 4.2 投票与升级(accuracy 取向)

- 首轮每个 unit **1 票**(保证至少被 LLM 看一次)。
- 高风险/不确定/票差大的 unit **升级到 3 票取中位数**(`risk_or_uncertain` 策略)。
- 目的:把 LLM 调用花在真正不确定的判定上。

### 4.3 Evidence pack:flow-centric 结构(2026-06-30 重写)

`buildEvidencePack` 为每个 unit(= 一条 label 从源点到汇点的完整 flow)组装。**旧的 5-section 结构已整体替换**,无开关:

- `label` — `{ category, subtype, sensitivity, field_name, field_path }`(纯语义,无内部 id)
- `sink_boundary` — 汇点跨越的数据边界:`{ node_name, operation_type, data_surface, receiver_scope, retention_scope, trust_boundary, operation_tags }`(**node_roles 已删**,与 flow 中 role=sink 节点的 `capabilities` 重复;**sink_surface 已迁移到 sink flow 节点**;单跨界不变量保证每 unit 汇点唯一,sink_boundary 留顶层)
- `flow[]` — 逐节点:`{ node_name, role(source/transform/sink/source_sink), action, capabilities?, transform?{type,from_label,to_label,count?}, sink_surface?[] }` — `sink_surface` 仅挂在 role=sink/source_sink 节点上,列出具体输出介质/通道标签(如 `webhook_post`、`api_call`、`file_write`、`database_write`、`shell_exec`),比 `sink_boundary` 粗粒度字段更细
- `evidence[]` — 扁平引用索引(`label.main` / `sink.boundary` / `flow.node.{i}`),供 LLM grounding + 裁剪重建
- `task_memory_evidence_ids` — 指向 skill 级共享 `task_memory` 中与本流相关的任务节点

> **关键设计**:
>
> - **role ≠ capability**:`role` 是节点在【这一条 label 流】上的**位置角色**(首=source、末=sink、首末同点=source_sink、其余=transform);一条 source→sink unit **有且只有一个汇点**。`capabilities` 才是节点的全局能力(node_roles)。曾误用全局 node_roles 当 role 导致一条流冒 8 个 sink,已修。
> - **transform 来自 filter_events**(redact_drop/summarization/pseudonymize/unknown_may_flow 等),是 necessity 核心信号,必须保留;同节点内完全相同的 transform 去重合并,>1 次带 `count`(单次不带,避免 count:1 增噪)。跨节点顺序/计次由 dedup 键的 `transform_seq` 承载,**展示层去重不影响它**。
> - **shared task_memory**:全局任务声明(skill identity + 文档 + 全 skill 任务节点)由 `buildSharedTaskMemory(fcg)` 从 FCG 聚合**一次**、skill 级共享,不再寄生每个 pack。
> - **信息保真**:重构后核心语义 token 覆盖 98.7%,丢的全是 JSON 键名/event_id 噪声 + 有意砍的字段;单 pack 体积 ~50 万字符 → ~1.4 千(skill_0001)。

---

## 5. 鲁棒性 / 工程硬化

为在**真实的、不稳定的、配额受限的**远程 API 上跑大规模 skill,做了一轮硬化,**前提约束:语义抽取与 DOE 判定精度不可下降**。已落地(239 测试全绿):

1. **FCG 语义门控缓存** 落到 `<root>/fcg/semantic-gate-cache.jsonl`(跨运行/CI 持久化)。命中 = 同一抽取结果,只降延迟。
2. **DOE evidence 分层预算**(`evidence-budget.js`):
   - Tier 0(默认):≤ 上限(默认 100K 字符)的 pack **逐字节原样发**,判定与不压缩完全一致。
   - Tier 2(兜底):仅超限 pack 才压(否则会超长超时、丢掉整个 skill)。无损精简 → flow 路径节点开窗(留边界+首尾)→ 文本/数组裁剪 → 丢聚合证据 → provenance 截断 → 硬上限兜底。所有 evidence_id 保留,被压单元标 `requires_review`。
3. **自适应超时**:按 payload 体积放大请求超时(默认上限 4×)。
4. **逐单元优雅降级**:单个 pack 持续瞬时失败 → 该 unit 退回 rule-only + `requires_review`,**不再让整个 skill 崩溃**(见 `statistics.llm_fallback_count` / `llm_fallback_units`)。
5. **传输层重试**(`shared/llm-utils.cjs`):429/5xx/网络/超时按指数退避+抖动重试,遵守 `Retry-After`;鉴权/4xx/schema 错误快速失败。
6. **配置贯通**:`doe.evidence*`、`fcg.semanticGateCache` 等从 config → pipeline → batch CLI 全程可调,两份 pipeline README 同步。

---

## 6. 成本现状(一个已知的待解决问题)

对超大 skill(如 `skill_0001 self-improving-agent`,FCG 上百 MB、数千 eligible unit),用 gpt-5.5 跑一次 DOE 的成本仍然偏高。

**已做的无损优化**(实测定位于 `scripts/measure-doe-cost.js`):

- 必要性 4→3 分量,LLM 输出减半。
- flow-centric pack + shared task_memory 聚合一次不再寄生每个 pack;task_memory 自重复字段裁剪。
- 实测:`skill_0001` 首轮估算 **$2,445 → $1,492**(input token 485M→296M,降 39%,官方 gpt-5.5 单价)。

**剩余大头**已转移到 evidence_packs 本身,再削减都是有损、需 A/B。最大剩余非代码杠杆 = **endpoint prompt caching**(shared_context 在单 skill 内恒定,适合缓存前缀)。

> 现状:导师认为单 skill 成本仍偏高,进一步优化**暂缓**,根因与方向已记录在案(prompt caching、调大 batch 摊销)。注意 `measure-doe-cost.js` 内置占位价与官方单价可能不同,跨文档比成本务必统一单价。

---

## 7. 数据与产物

| 路径 | 内容 |
| --- | --- |
| `results/clawhub-top-k10000/` | 万级 skill 的下载/分组/FCG 产物(最大规模实跑) |
| `results/sample-skill1/` | 单个超大 skill(skill_0001)的 FCG,用于压力测试 |
| `results/ab-sample/` | DOE 预算开/关的 A/B 对照(验证"压缩不降准") |
| `results/debug-k20-c8/` | 小批量调试 |
| `results/run-logs/` | 各次实跑日志(含 FCG/DOE 耗时、配额错误) |
| `paper/` | 论文草稿(sections / tables / figures) |

---

## 8. 当前状态小结(给协作者对齐用)

- **已完成且稳定**:三阶段 pipeline、FCG 语义门控 + 缓存、DOE 两层评分 + 投票升级、flow-centric evidence pack/预算、传输鲁棒性。万级 skill 与单个超大 skill 都实跑验证过。
- **已知约束/未决**:LLM 调用成本(尤其大 skill);测试 API 账户配额有限,超大 skill 无法跑满。
- **建议对齐的颗粒度**:
  - 写作/汇报时,**assessment unit = (observation × label_flow)** 是最小判定粒度,DOE score 公式与 **3 分量**必要性是核心贡献点。
  - 区分清楚 **exposure(危险度)** 与 **necessity(必要性)** —— 本工作的新意在 necessity 的 LLM 判定,而非 exposure 检测本身。
  - FCG 与 DOE 是**两个独立可替换的阶段**:FCG 负责"流图怎么建",DOE 负责"暴露必要不必要",对齐分工时按 `security_profile` 契约(§2.4)这条边界切。

---

## 9. 复现入口

```powershell
# 完整 pipeline（需要 .env 里的 LLM_API_KEY）
node scripts\skillflow-pipeline.js --k 100

# 只跑某阶段
node scripts\skillflow-pipeline.js --k 100 --phase fcg
node scripts\skillflow-pipeline.js --k 100 --phase doe

# 测试（239 全绿；核心用例在 packages 下）
node --test "packages/*/test/**/*.test.js"
```

详细参数见 `README-PIPELINE-CH.md` 与 `skillflow-pipeline.config.cjs`。
