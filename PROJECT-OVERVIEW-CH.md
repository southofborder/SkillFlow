# SkillFlow 项目工作总览

> 目的:向协作者交代「我们到底在做什么、做到哪一步、每块的颗粒度如何」,用于对齐分工与写作粒度。
> 维护:本文件描述截至 2026-08 的状态,代码以 `packages/` 为准。英文版见 `PROJECT-OVERVIEW.md`。
> 引擎现状:**SFG(技能流图)已是 Python**(`packages/skill-sfg`),**DOE(数据过度暴露判定)仍是 JS**(`packages/skill-doe-analyzer`),编排脚本 `scripts/skillflow-pipeline.js` 调度两者。

---

## 1. 一句话定位

SkillFlow 是一套针对 **Agent Skill(ClawHub 上的可下载 skill 包)** 的**数据过度暴露(Data Over-Exposure, DOE)**静态分析流水线。
它回答的核心问题是:

> 一个 skill 在完成它声称的任务时,是否把**超出任务必要范围的敏感数据**送过了信任边界(发给外部 LLM、外部服务、持久化存储等)?

不是简单的"有没有敏感数据流出",而是**"这次流出对完成声称的任务是否必要"**——必要的暴露不算 DOE,不必要的才算。这是本工作区别于普通污点分析(taint analysis)的关键。

> **两轴正交**:一次跨边界既有 **exposure(暴露度,这次外泄本身多危险)**,又有 **necessity(必要性,这次外泄对完成任务多必要)**。DOE 正例 = **真外泄 ∧ 不必要**;真外泄(model_provider / 外部网络 / 第三方 / 持久化存储)不可豁免,喂 LLM 只降低必要性、不降低暴露度。这条正交性是 necessity 结构化重设计的地基(见 §4)。

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
| **DOE score** | `clamp(exposure × (1 - necessity) + baseline_adjustment)` —— 越高越是过度暴露 |
| **potential_doe(疑似过度暴露)** | `boundary_crossed ∧ necessity < 0.7` 的布尔标记(暴露∧不必要,`DEFAULT_NECESSITY_THRESHOLD=0.7`) |

暴露度(`exposure-scorer.js`):`exposure = boundary_crossed ? clamp(0.6·label_sensitivity + 0.4·boundary_risk) : 0`。`label_sensitivity` 由类目查 `CATEGORY_EXPOSURE`(credentials/secret 1.0、financial/health 0.9、pii 0.8…generic 0.3);`boundary_risk` 按信任/接收方/留存分层。**真外泄统一打 `high_sensitivity_egress` tier、不分档不可豁免**;只有停在 `user_visible`(回给用户、无其他外泄信号)才是 `local`。

必要性由 **3 个分量(component)** 构成,DOE 的必要性取这 3 项的**最小值**(短板决定,`COMPONENT_KEYS` 见 `necessity-baseline.js`)。**键名沿用旧设计,但内部已从词袋重设计为结构判据**(词袋只剩作抬地板的弱信号):

- **`action_input_need`**:这个动作的**输入**是否真的需要这个标签(局部)。主判据 = ① sink 对该标签施加了真实 transform(`transform_sig≠none`,权 0.9)② 该标签在 sink 的**声明输入 schema** 里(`schemaMember==1`,权 0.95)③ op 类型 baseline(`model_inference`/`external_egress` 等)。**结构负号**:声明了 schema 但标签不在其中且无 transform → 封顶 0.25。
- **`receiver_semantic_need`**:**接收方 × 标签类目相容矩阵**(`RECEIVER_CATEGORY_COMPAT`,按 `model_provider`/`third_party`/`first_party`/`local_runtime`)为底;外泄前有 reduction → 抬到 ≤0.6(**仍压在 0.70 阈值下**);`user_visible` 源 + 一方接收 → 抬到 0.6。
- **`task_need`**:`min(flow_path 声明覆盖率, boundary_node 声明信号)`。路径节点被任务声明/合成的比例越高越必要;通用汇点(webhook/analytics/telemetry/log 且未被任务点名)封顶 0.12。两个子信号仍在 `flow_path_signal`/`boundary_node_signal` 里透出供调试。

> **group baseline 是独立的加性项**(`group-baseline.js`),`baseline_adjustment ∈ {-0.08, +0.08, +0.12, 0}`,**加在最终 DOE score 上、不折进 necessity**;无 groupBaseline 时恒 0(默认)。

---

## 3. 三阶段流水线(端到端)

入口:`scripts/skillflow-pipeline.js`(JS 编排器),默认 `all` 流程。它把 SFG 阶段派发给 Python(`python -m skill_sfg.batch`,cwd=`packages/skill-sfg`),把 DOE 阶段派发给 JS(`node scripts/doe-batch.js`,cwd=`packages/skill-doe-analyzer`)。配置见 `skillflow-pipeline.config.cjs`,两份 pipeline README(`README-PIPELINE.md` / `README-PIPELINE-CH.md`)。

```text
                    ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐
ClawHub top-k  ───▶ │ 1. Download │──▶│ 2. SFG 流图分析   │──▶│ 3. DOE 暴露判定     │
   (按下载量)        └─────────────┘   └──────────────────┘   └─────────────────────┘
                          │                   │                        │
                    zips/ 下载        fcg/skills/*-sfg.json      doe/skills/*-doe.json
                                        + flow.md / flow.mmd      + doe-summary.{json,md}
```

> **命名说明**:图引擎品牌层已更名(FCG→**SFG**),但运行时**保留**了内部选择器与目录以免破坏契约:`--phase fcg`/`--phase doe` 选择器、输出目录 `fcg/`/`doe/`、汇总文件 `fcg-summary.*`/`doe-summary.*`、连接契约 CLI(`--fcg`/`--fcg-root`)一律不变;SFG 侧单 skill 文件后缀改成 `-sfg.json`、环境变量前缀改成 `SFG_*`;DOE 侧后缀 `-doe.json`、前缀 `DOE_*` 与包目录 `skill-doe-analyzer` 均保持原样。

可选的 **similarity grouping**(相似 skill 聚类)默认关闭,只有 `--with-similarity`(或 `--phase download-group`)才跑。

### 阶段 1 — Download(`packages/skill-similarity-analyzer` 复用)

按 `downloads` 排序抓 ClawHub 前 k 个 skill zip。带并发、重试、超时。

### 阶段 2 — SFG(Skill Flow Graph,`packages/skill-sfg`,**Python**)

> SFG 是整条链路里代码量最大的一块,也是 DOE 的唯一输入来源。**该阶段已整体从 JS 重写为 Python**:包 `skill-sfg`,入口 `python -m skill_sfg.batch`,批处理 CLI `skill-sfg analyze`;模块按 `parser/ → analyzer/ → classifier/ → security/ + flood/ → output/` 分层。
> 这一节按「编排流程 → 输出接口 schema → LLM 介入点」三层展开,供和 DOE 的输入契约对齐。

#### 2.1 它在做什么

把一个 skill 包(`SKILL.md` + README + 脚本 + 其他文档)解析成一张**有向流图**,并在图上叠加一层**安全语义画像(security_profile)**。

- 图(`nodes` / `edges`):谁把数据传给了谁。
- 安全画像(`security_profile`):每个节点处理什么敏感数据(label)、数据沿什么路径流动(label_flow)、在哪里跨越了信任边界(observation)。

DOE 阶段**只读 `meta` / `nodes` / `documentation_context` / `security_profile`**(security_profile 里用到 observations / label_flows / node_profiles / provenance_graph / label_dictionary / flow_states),图的边与 nodes 主要供人读报告与调试。这是两阶段之间的接口边界。

> **提取粒度:块分类 + 策略派发(2026-07 重写)**。提取不再"一律按行跑关键词",而是**先判文件类型,再判内容块类型,再派发对应策略**:
>
> - **文件类型**:指令文档(SKILL.md/README)vs 非指令文档(changelog/license/notice/contributing 等,`parser/document_context.py` 的 `_NON_INSTRUCTION_MD` 挡掉,不产动作节点)vs 脚本(js/py/sh)。
> - **内容块类型**:代码块 / 表格 / 列点 / 散文 / 免责声明。shell 代码块与脚本里的 shell 命令**共用 `parser/shell_command_classifier.py`**(确定性白名单:egress/exec/read/write + URL/host/重定向识别),逐命令建 sink(`curl`/`wget` 等外泄是最强 sink 证据,以前整块被丢);散文里的否定与免责声明("does not send…"、"What this skill does NOT do")识别后降为 `guard`/`context`,不再被反转成外泄动作;表格里的 condition 保留为边连接判据。
> - **列表块结构化(`segment_markdown_blocks`,2026-07)**:提取前先把散文/列点切成块。**多行 bullet**(续行缩进 ≥ 标记列)合并成一条,不再被拆成碎节点;**列表块继承 lead-in 免责作用域**——`**What this skill does NOT do:**` 下方 bullet 即使不重复否定词也整块降为 context;**反向保护**:软否定小节(如 `## Limitations`)里明确 imperative 指令不被压掉(weather `- PNG: curl … -o` sink 守住)。散文仍逐行(真实语料里"段落"多为整行多句,逐行≈逐段),不做跨行合并。
> - **脚本调用**:按角色分类(sink/source/sanitizer/noise)。语言内建(`push`/`map`/`console.log`/`Array.isArray` 等)作为噪声丢弃,**未知用户函数保留**(不猜为噪声),避免脚本节点爆炸。
> - 这层是**规则优先、LLM 只兜底歧义**,保住了默认零 LLM 的 token 成本。详见 §2.5 的语义门控。
>
> **连边的两股力(recall vs precision)**:`analyzer/type_analyzer.py` 用**穷举候选 + 类型/签名兼容**保证"该连的连上"(防少连,跨块/跨节复杂数据流靠它);routing 层(`flood/router.py`)用**条件/guard 语义**收紧"不该连的别连"(防多连)。抽取到的 `formal_semantics.conditions`(`when/if/unless/without` 等)经 `security/node_profiler.py` 透到 profile、进 `build_route_text`;明确否定条件("unless redacted"、"only if not")把本会 definite 的 sink 路由**降级为 may_route**(不删边、不硬 block、无条件时维持现状,故不伤 recall)。

#### 2.2 编排流程(`analyzer/pipeline.py` 的 Phase)

入口 `run_pipeline(skill_root_dir, options)`(移植自旧 JS 的 `SkillFCGAnalyzer.analyze`),返回 `{graph, tools, semantic_gate_usage, mode, cycle_expand, skill_data, readme_data, documentation_context}`;**JSON/security_profile 生成不在这里**,由 `batch.py` 拿到 `run_pipeline` 结果后调 `output/json_generator.py::build_fcg_json` 完成:

| Phase | 步骤 | 模块 | 产物 |
| --- | --- | --- | --- |
| 1 | 解压/定位 skill 根目录 | `batch.py` | skill_root_dir |
| 2 | 解析 skill 文件 + README + 可执行文件清单 + 文档计划 | `parser/skill_parser.py`, `parser/document_context.py`(`parse_skill` / `parse_readme` / `find_executable_files` / `build_documentation_plan`) | skill_data / readme_data / documentation_context |
| 3a | 抽工具调用 | `parser/tool_extractor.py`(`extract_tool_calls`) | tool 节点 |
| 3b | 抽脚本数据流(JS/PY 等):调用按角色分类(sink/source/sanitizer/noise),内建噪声丢弃、未知用户函数保留;shell 命令走共享分类器 | `parser/script_flow_extractor.py`(`extract_script_flow`), `parser/shell_command_classifier.py` | script flow 节点+边 |
| 3c | 抽文档数据流:**先判文件类型(指令 md vs changelog/license 等非指令文档),再按块分类(代码块/表格/列点/散文/免责声明)派发提取策略**;列表块结构化(多行 bullet 合并、lead-in 免责作用域继承);shell 代码块逐命令建 sink,否定/免责声明降为 guard/context;顺序边默认**同节内**连(`SFG_SEQUENCE_EDGE_SCOPE=global` 可回退) | `parser/doc_flow_extractor.py`(最大,`extract_document_flow` / `resolve_pending_constraints`), `parser/document_context.py`, `parser/shell_command_classifier.py` | doc flow 节点+边 |
| 3d | 注入隐式 `user.query` 源 + `llm.inference` 边;调用点中介(`build_call_site_mediation`) | `classifier/source_sink.py`(`create_user_query_source`), `analyzer/callsite_expander.py` | 激活流 / skill 内容→全局 LLM 边 |
| 4 | 稀疏类型兼容性分析(候选依赖边)+ 结构依赖边(user.query→llm.inference、skill 内容→全局 LLM) | `analyzer/type_analyzer.py`(`analyze_type_compatibility`) | dependency candidates |
| 5 | 依赖边校验:`full` 走 `high_value` 策略 LLM 校验(`validation_method=dependency_llm_high_value`),`quick` 直接映射候选,`deep` 额外加 control_flow 顺序边(`build_deep_mode_edges`) | `analyzer/llm_validator.py` | validated edges |
| 6 | 建图 + 去重边 | `analyzer/fcg_builder.py`(`build_fcg` / `remove_duplicate_edges`) | graph(nodes/edges) |
| 6b | 去环:`cycle_expand` 时 `detect_and_tag_cycles` 标记 feedback 边(不删),否则 `remove_cycles`;再 `classify_feedback_edges`(回边合理性)→ `break_only_fake` | `analyzer/cycle_remover.py`, `analyzer/feedback_edge_classifier.py` | 去环/标环后的 graph |
| 6c | **单跨界拆分**(连边后确定性拆分,每节点≤1数据跨界;child 继承父边、synthetic builtin 豁免) | `analyzer/node_splitter.py`(`split_graph_nodes`) | 拆分后的 graph |
| — | 生成 v6 JSON + **security_profile** + flowchart(`run_pipeline` 之外,`batch.py` 调用) | `output/json_generator.py`(`build_fcg_json`), `output/flowchart_generator.py`, `security/` + `flood/` | `*-sfg.json` / `.flow.md` / `.flow.mmd` |

> 模式 `mode`:`quick`(跳过 Phase 5 的 LLM 依赖校验)/ `full`(默认)/ `deep`(额外加结构化 control_flow 顺序边)。旧 JS 的 Phase 7 路径抽取(`path-extractor`,`O(V!)` 且仅调试用)**未移植进 Python**——v6 输出不含 `paths`。

#### 2.3 安全画像生成(`build_fcg_json` 内部,`security/` + `flood/` 两个子系统)

`output/json_generator.py::build_fcg_json` → `security/transfer_analysis.py::build_transfer_security_profile`(薄包装:在活跃边集上先建节点画像)→ 委托给 `flood/public.py::build_transfer_security_profile_v6`。旧 JS 的扁平四段链(node-profiler → graph-transfer-analyzer → observation-analyzer → provenance-extractor)在 Python 里**拆成 `security/` 打画像、`flood/` 做传播两块**:

1. `security/node_profiler.py`(`build_node_profiles` / `build_node_profiles_with_options`)— 给每个节点打 **label**(category.subtype + sensitivity)、operation_type、data_surface、receiver_scope、trust_boundary 等画像。可选 `security/label_llm_assistant.py` 对低置信标签做 LLM 辅助。
2. `flood/analyzer.py::analyze_graph_transfers` — 在图上做**标签传播**,产出 `label_flows`(标签流,含 `node_path`/`node_names`/`edge_path`)、`flow_states`、各类事件(route/filter/merge)。
3. `flood/observations.py::build_observations` — 把跨边界事件归纳成 **observations(边界观测)**。
4. `flood/public.py::_build_provenance_graph_v6` — 建 `provenance_graph`(只留真变换/过滤事件),记录数据来源谱系;label 去重进顶层 `label_dictionary`,label_flows/flow_states 压成 public 版。**v6 已删 `provenance_store`**(origins/path_classes/representative_paths 不再落盘)。

#### 2.4 输出接口 schema(`*-sfg.json`,与 DOE 的契约)

顶层字段(`output/json_generator.py::build_fcg_json` 组装,`analyzer_version: "6.0.0"`)。**v6 envelope 比旧 JS 精简**:调试用的 `source_sink` / `paths` / `risks` 三块**已去掉**(无判定依赖、`run_pipeline` 也不再计算):

```text
{
  meta:                { skill_name, skill_version, analysis_timestamp,
                         analyzer_version="6.0.0", input_source, analysis_mode }
  nodes:               [ ... ]           ← 图节点(见下)
  edges:               [ ... ]           ← 图边(见下,忠实保留 SFG 图形状)
  statistics:          { total_nodes, total_edges, ..., feedback_edge_count,
                         semantic_gate_llm_usage? }
  documentation_context:{ ... }
  security_profile:    { ... }           ← ★ DOE 实际消费的部分(v6.0)
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

**security_profile(★ DOE 输入)关键字段**(`flood/public.py::build_transfer_security_profile_v6`,当前 `version: "6.0"`):

| 字段 | 含义 | DOE 用途 |
| --- | --- | --- |
| `node_profiles[]` | 每节点的安全画像(label/operation/data_surface/receiver_scope/trust_boundary) | local 必要性 |
| `label_flows[]` | 标签流(public 压缩版):`{ label_flow_id, label_id 或内联 label, current_node, node_path, node_names, edge_path, flow_mode, confidence, origin_ids, parent_label_flow_ids[], ... }` | 全局必要性、路径证据 |
| `label_dictionary` | 顶层去重 label 表:`label_flows[].label_id` 引用它 | 解引用得到 label |
| `observations[]` | 边界观测:`{ observation_id, node_id, operation_type, boundary{trust_boundary,receiver_scope}, label_flow_ids[], ... }` | assessment unit 的 observation 侧 |
| `flow_states[]` | 标签流聚合状态(v6 已瘦身,只留判定所需字段) | 聚合证据、reduction 契约 |
| `provenance_graph` | 数据传播谱系(events,只留真变换/过滤事件) | filter/storage 证据 |
| `statistics` | `observation_count` / `label_flow_count` / `label_dictionary_count` / `node_flow_set_count` / ... | 规模与日志 |

> **对齐要点 1**:DOE 的最小判定单元 `(observation × label_flow)` 直接来自这里——`observations[].label_flow_ids` 笛卡尔展开成 assessment unit。要替换/改 SFG,只要保证 `security_profile` 的这几个数组字段契约不变,DOE 侧无需改动。
>
> **对齐要点 2(node_path 契约)**:label_flow 现在**自带 `node_path`/`node_names`/`edge_path`**(以前 DOE 靠 parent 链重建)。`edge_path` 遵守**位置契约** `len(edge_path) == len(node_path) - 1`(edge[i] 连 node[i]→node[i+1])。只留复数 `parent_label_flow_ids`;每条 flow 是**单流**(≤1 父),父指针用于**溯源**(让 `source_introduction` 提取/概括步不被误判为源点),不是记合并。GNN/序列建模可直接消费 node_path,无需重建。
>
> **对齐要点 3(label_dictionary)**:label 去重进顶层 `label_dictionary`,flow 用 `label_id` 引用;DOE 解引用一次(内联优先,否则查字典,悬空 id 显式报 `label_dictionary.miss` warning),下游全部零改动。**这只省 SFG 磁盘/解析延迟,不省 LLM token。**
>
> **对齐要点 4(v6 瘦身)**:相比 v5.1,v6 删掉了 `provenance_store`(origins/path_classes/representative_paths)、`node_flow_sets` 明细(只留 statistics 计数),`flow_states` 砍掉死字段、`provenance_graph` 只留真变换/过滤事件。DOE 只从 `flow_states` 读 4 个字段。

#### 2.5 LLM 在 SFG 里的 3 个介入点(都可关、都有缓存)

SFG 不是"一次大 LLM 调用",而是 3 个**独立、可分别开关**的 LLM 介入点:

1. **Markdown 语义门控 semantic gate(默认开,强门控)** — `parser/doc_flow_extractor.py` + `parser/script_flow_extractor.py`。规则只产候选节点,**LLM 判定每个候选的 actionability/classification/operation_type**,结果写进节点的 `semantic_gate`。缺 `LLM_API_KEY` 时 SFG 预检直接失败。这是 SFG 精度的主来源,也是耗时主来源。缓存:`<root>/fcg/semantic-gate-cache.jsonl`(`SFG_SEMANTIC_GATE_CACHE` 可调,跨运行/CI 持久)。
2. **依赖边校验(默认 `high_value` 策略)** — Phase 5 `analyzer/llm_validator.py`。只对高价值候选依赖对做 LLM 确认,产出 `validation_method=dependency_llm_high_value` 的边。`quick` 模式跳过。可调 `SFG_DEPENDENCY_*`。
3. **标签 LLM 辅助(默认关)** — `security/label_llm_assistant.py`。仅对 generic/低证据标签生成弱证据候选标签,标 `mode=llm_assisted`、`requires_review=true`,供 DOE 区分强弱证据。

> 关键性质:LLM 命中缓存 = 返回当初同一判定,**抽取质量完全一致,只降延迟**。这是"鲁棒性硬化不降准"约束在 SFG 侧的体现。

### 阶段 3 — DOE(`packages/skill-doe-analyzer`,**JS**)

吃 SFG JSON,产出每个 assessment unit 的 DOE 判定。详见 §4。

---

## 4. DOE 分析器内部结构(本项目的核心,颗粒度最细)

源码:`packages/skill-doe-analyzer/src/`(DOE 仍是 **JS**,内部标识符与文件名保留 `doe-*` 未改,只换了品牌名与包目录)

| 文件 | 职责 |
| --- | --- |
| `doe-analyzer.js` | 主编排:rule-only 评分 → 选出该送 LLM 的 unit → 调 LLM judge → 融合 |
| `exposure-scorer.js` | 暴露度评分(边界是否跨越、边界风险、敏感度) |
| `necessity-baseline.js` | 规则版必要性评分(3 分量的 baseline,`COMPONENT_KEYS = ['action_input_need','receiver_semantic_need','task_need']`) |
| `necessity-text-utils.js` | 必要性文本信号抽取辅助 |
| `group-baseline.js` | 同组 skill 的基线调整 |
| `label-resolver.js` | `resolveLabel` / `buildLabelDictionary`:兼容内联 label 与 `label_id` 引用 |
| `flow-path-utils.js` | label_flow 路径解析(自带 node_path 走快路径,否则按 parent 链重建) |
| `evidence-pack.js` | 把一个 unit 打包成 **flow-centric** evidence pack + 聚合 shared task_memory |
| `evidence-budget.js` | evidence pack 的分层压缩(防止上下文超长/超时) |
| `llm-judge.js` | LLM judge:打包 prompt、批处理、投票、升级复判、缓存、容错 |
| `path-report.js` | 人读报告生成 |

### 4.1 两层评分:规则 + LLM 融合

1. **规则层(rule-only,确定性、免费、离线)**:每个 unit 都先算一遍 exposure 与 3 分量 necessity baseline。规则打分器直接吃 SFG 对象与 `flow_states` 摘要、**不读 evidence pack**,故 pack 重构不影响规则分。
2. **LLM 门控(敏感度驱动,非 boundary_risk 阈值)**:`shouldJudgeAssessmentWithLlm` 放行条件是 `boundary_crossed && (highSensitive || (mediumSensitive && potential_doe))` —— high 敏感度一律送审(reason `high_sensitivity_backstop`),medium 敏感度只在同时 `potential_doe`(= 越界且 necessity<0.7)时送审(reason `medium_sensitivity_potential_doe`)。`boundary_risk` 仍在返回值里做透明度展示,但**不再参与门控**。送审前先按 `(observation | label | transform_seq | origin_class)` 去重,把数千个越界 unit 塌成代表单元,成员复用代表的判定。
3. **LLM judge**:对放行的 unit,LLM 基于 evidence pack 给 3 分量打分(PROMPT_VERSION `doe-llm-judge-v6-reduction-antichain`)。
4. **融合**:`component = llmWeight·llm + (1-llmWeight)·rule`(默认 `llmWeight=0.7`),必要性取 3 分量最小值,再算 DOE score。

### 4.2 投票与升级(accuracy 取向)

- 首轮每个 unit **1 票**(保证至少被 LLM 看一次)。
- 高风险/不确定/票差大的 unit **升级到 3 票取中位数**(`risk_or_uncertain` 策略)。
- 目的:把 LLM 调用花在真正不确定的判定上。

### 4.3 Evidence pack:flow-centric 结构(2026-06-30 重写为 flow-centric,现为 v7,带结构信号)

`buildEvidencePack` 为每个 unit(= 一条 label 从源点到汇点的完整 flow)组装。**旧的 5-section 结构已整体替换**,无开关。当前 v7 每个 pack:

- `unit_id` / `observation_id` / `label_flow_id` — 判定单元标识
- `question` — 内嵌的判定提问(local necessity:sink 的 action input 与 receiver 语义是否需要该 label;global `task_need`:整条源→汇路径是否属于声明任务所需的数据/控制流,且汇点是否为该路径所必需)
- `label` — `{ category, subtype, sensitivity, field_name, field_path }`(纯语义,无内部 id;必要时带 `requires_review` / `mode` 标志位)
- `sink_boundary` — 汇点跨越的数据边界:`{ node_name, operation_type, data_surface, receiver_scope, retention_scope, trust_boundary, operation_tags }`,加 **N5 结构信号**:`exposure_tier`(所有真外泄统一 `high_sensitivity_egress`)、`reduction_before_egress`(越界前实际施加的极大互不可比缩减类型集 = reduction antichain,空数组 = 原始数据外发)。(**node_roles 已删**,与 flow 中 role=sink 节点的 `capabilities` 重复;**sink_surface 已迁移到 sink flow 节点**;单跨界不变量保证每 unit 汇点唯一,sink_boundary 留顶层)
- `flow[]` — 逐节点:`{ node_name, role(source/transform/sink/source_sink), action, operations?, capabilities?, transform?/transforms?, sink_surface?[] }`,加 **N5 结构信号**:sink/source_sink 节点标 `schema_declares_input`(该 label 是否在汇点声明的 input schema 里 —— `action_input_need` 硬依据),source/source_sink 节点标 `origin_trust`(数据引入点信任边界 —— receiver 相容判断硬依据)。`sink_surface` 仅挂 role=sink/source_sink 节点,列出具体输出介质/通道标签(`webhook_post`/`api_call`/`file_write`/`database_write`/`shell_exec` 等),比 `sink_boundary` 粗粒度字段更细
- `leak_type` / `leak_severity` / `cycle_handling` — 仅当本流经真环(周期性泄露 / collapse 出环)时附加,让 judge 对重复泄露加权
- `task_memory_evidence_ids` — 指向 skill 级共享 `task_memory` 中与本流相关的任务节点

> **关键设计**:
>
> - **无 per-unit `evidence[]` 索引**:grounding 不再单列一份扁平 evidence 索引 —— 结构里已有的 `label` / `sink_boundary` / `flow[].node.{i}` 就是引用锚点;只有 skill 级共享 `task_memory` 保留 `evidence[]`(供 `task_memory_evidence_ids` 引用)。
> - **role ≠ capability**:`role` 是节点在【这一条 label 流】上的**位置角色**(首=source、末=sink、首末同点=source_sink、其余=transform);一条 source→sink unit **有且只有一个汇点**。`capabilities` 才是节点的全局能力(node_roles)。曾误用全局 node_roles 当 role 导致一条流冒 8 个 sink,已修。
> - **transform 来自 filter_events**(redact_drop/summarization/pseudonymize/unknown_may_flow 等),是 necessity 核心信号,必须保留;同节点内完全相同的 transform 去重合并,>1 次带 `count`(单次不带,避免 count:1 增噪)。跨节点顺序/计次由 dedup 键的 `transform_seq` 承载,**展示层去重不影响它**。
> - **shared task_memory**:全局任务声明(skill identity + 文档 + 全 skill 任务节点)由 `buildSharedTaskMemory(fcg)` 从 SFG 聚合**一次**、skill 级共享,不再寄生每个 pack。
> - **信息保真**:重构后核心语义 token 覆盖 98.7%,丢的全是 JSON 键名/event_id 噪声 + 有意砍的字段;单 pack 体积 ~50 万字符 → ~1.4 千(skill_0001)。

---

## 5. 鲁棒性 / 工程硬化

为在**真实的、不稳定的、配额受限的**远程 API 上跑大规模 skill,做了一轮硬化,**前提约束:语义抽取与 DOE 判定精度不可下降**。已落地(213 测试全绿:SFG 135 pytest + DOE 58 + similarity 20):

1. **SFG 语义门控缓存** 落到 `<root>/fcg/semantic-gate-cache.jsonl`(输出目录名 `fcg/` 保留未改;跨运行/CI 持久化)。命中 = 同一抽取结果,只降延迟。
2. **DOE evidence 分层预算**(`evidence-budget.js`):
   - Tier 0(默认):≤ 上限(默认 100K 字符)的 pack **逐字节原样发**,判定与不压缩完全一致。
   - Tier 2(兜底):仅超限 pack 才压(否则会超长超时、丢掉整个 skill)。无损精简 → flow 路径节点开窗(留边界+首尾)→ 文本/数组裁剪 → 丢聚合证据 → provenance 截断 → 硬上限兜底。所有 evidence_id 保留,被压单元标 `requires_review`。
3. **自适应超时**:按 payload 体积放大请求超时(默认上限 4×)。
4. **逐单元优雅降级**:单个 pack 持续瞬时失败 → 该 unit 退回 rule-only + `requires_review`,**不再让整个 skill 崩溃**(见 `statistics.llm_fallback_count` / `llm_fallback_units`)。
5. **传输层重试**:DOE 侧 `shared/llm-utils.cjs`、SFG 侧 `skill_sfg/llm/transport.py`,429/5xx/网络/超时按指数退避+抖动重试,遵守 `Retry-After`;鉴权/4xx/schema 错误快速失败。
6. **配置贯通**:`doe.evidence*`、`fcg.semanticGateCache` 等配置键(键名保留 `fcg`/`doe`)从 config → pipeline → batch CLI 全程可调,两份 pipeline README 同步。

---

## 6. 成本现状(一个已知的待解决问题)

对超大 skill(如 `skill_0001 self-improving-agent`,SFG 上百 MB、数千 eligible unit),用 gpt-5.5 跑一次 DOE 的成本仍然偏高。

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
| `results/clawhub-top-k10000/` | 万级 skill 的下载/分组/SFG 产物(最大规模实跑;磁盘目录名仍为 `fcg/`) |
| `results/sample-skill1/` | 单个超大 skill(skill_0001)的 SFG,用于压力测试 |
| `results/ab-sample/` | DOE 预算开/关的 A/B 对照(验证"压缩不降准") |
| `results/debug-k20-c8/` | 小批量调试 |
| `results/run-logs/` | 各次实跑日志(含 SFG/DOE 耗时、配额错误) |
| `paper/` | 论文草稿(sections / tables / figures) |

---

## 8. 当前状态小结(给协作者对齐用)

- **已完成且稳定**:三阶段 pipeline、SFG 语义门控 + 缓存、DOE 两层评分 + 投票升级、flow-centric evidence pack/预算、传输鲁棒性。SFG 已全量 Python 化(跨引擎逐字节 parity 冻结);万级 skill 与单个超大 skill 都实跑验证过。
- **已知约束/未决**:LLM 调用成本(尤其大 skill);测试 API 账户配额有限,超大 skill 无法跑满。
- **建议对齐的颗粒度**:
  - 写作/汇报时,**assessment unit = (observation × label_flow)** 是最小判定粒度,DOE score 公式与 **3 分量**必要性是核心贡献点。
  - 区分清楚 **exposure(危险度)** 与 **necessity(必要性)** —— 两轴正交:`potential_doe = boundary_crossed ∧ necessity<0.7`,真外泄(如 model_provider)不可豁免、只由必要性定去留;本工作的新意在 necessity 的 LLM 判定,而非 exposure 检测本身。
  - SFG 与 DOE 是**两个独立可替换的阶段**:SFG 负责"流图怎么建"(Python),DOE 负责"暴露必要不必要"(JS),对齐分工时按 `security_profile` 契约(§2.4)这条边界切。

---

## 9. 复现入口

```powershell
# 完整 pipeline（需要 .env 里的 LLM_API_KEY）
node scripts\skillflow-pipeline.js --k 100

# 只跑某阶段（phase 选择器名保留 fcg/doe，未随品牌改）
node scripts\skillflow-pipeline.js --k 100 --phase fcg   # SFG（Python 引擎）
node scripts\skillflow-pipeline.js --k 100 --phase doe   # DOE（JS 引擎）

# 测试（213 全绿）
#   SFG（Python）：135 pytest
cd packages\skill-sfg; python -m pytest -q; cd ..\..
#   DOE + similarity（JS）：58 + 20
node --test "packages/skill-doe-analyzer/test/**/*.test.js"
node --test "packages/skill-similarity-analyzer/test/**/*.test.js"
```

详细参数见 `README-PIPELINE-CH.md` 与 `skillflow-pipeline.config.cjs`。
