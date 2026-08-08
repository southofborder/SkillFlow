# Skill FCG Analyzer 中文说明

`skill-fcg-analyzer` 用于分析 OpenClaw Skill，输出函数调用图（Function Call Graph, FCG）以及面向安全分析的实例级数据流画像。它位于项目的 `packages/` 目录下，通常在 pipeline 下载并分组 skills 之后运行。

分析器分为两层：

- FCG 建图层：解析 skill 文件，抽取工具节点和文档语义节点，推断 may-flow 边，并构建图。
- 安全传播分析 v4.5：为每个节点建立安全语义画像，优先使用 `doc_step` 级文档流节点，拆分明确英文复合动作，并补全英文隐式对象读取，以单标签 `label_flow` 为单位传播字段级数据，在汇点生成只引用 `label_flow_ids` 的 observation，并输出可从汇点反推回源点、路由、筛选和 storage bridge 的 provenance graph。

## 环境要求

- Node.js `>=18`
- 除非特别说明，命令都在 `packages/skill-fcg-analyzer` 下运行。

```powershell
cd D:\projects\SkillFlow\packages\skill-fcg-analyzer
npm install
```

## 快速开始

分析单个 skill zip。Markdown 语义门控默认运行，需要配置 `LLM_API_KEY`：

```powershell
node src\index.js analyze "D:\path\skill.zip" --mode full --output results\skill-fcg.json
```

分析包含 `SKILL.md` 的目录：

```powershell
node src\index.js analyze "D:\path\skill-dir" --mode full --output results\skill-fcg.json
```

对 pipeline 结果目录批量运行 FCG：

```powershell
node scripts\fcg-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k1000
```

强制刷新已有 FCG 结果：

```powershell
node scripts\fcg-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k1000 --refresh
```

## CLI

### 单个 Skill 分析

```text
node src/index.js analyze <input> [--output <file>] [--mode <quick|full|deep>] [--llm-timeout <ms>] [--label-llm-assist] [--label-llm-concurrency <n>] [--label-llm-cache <file>] [--flowchart <file.md>]
```

参数说明：

- `--output <file>`：JSON 输出路径，父目录会自动创建。
- `--mode quick|full|deep`：分析模式。
- `quick`：只做类型兼容边推断，速度最快。
- `full`：类型兼容 + 工具边语义校验。如果配置了 LLM 则可使用 LLM，否则使用启发式 fallback。
- `deep`：在 `full` 基础上额外加入结构化控制流边。
- `--label-llm-assist`：可选的低置信度标签 LLM 辅助生成，只在 deterministic 标签证据弱时触发，需要 `LLM_API_KEY`。
- `--label-llm-concurrency <n>`：标签辅助生成并发数，默认 `2`。
- `--label-llm-cache <file>`：标签辅助生成 JSONL 缓存文件。
- `--llm-timeout <ms>`：网络或 LLM 超时时间，默认来自 `LLM_TIMEOUT` 或 `30000`。
- `--flowchart <file.md>`：自定义 Markdown 报告路径，对应 `.mmd` Mermaid 文件会自动生成。

Document-flow 粒度：

- 默认情况下，Markdown 中显式动作会输出为 `doc_step` 级 FCG 节点。
- Step 节点保留行号、step index、动作、目标、指令文本和 `formal_semantics`。
- 连续 Markdown 步骤通过 `control_flow` 边连接。
- 跨文档 Markdown 引用从当前 `doc_step` 跳到目标文档的第一个 `doc_step`。
- legacy 的合并式 `doc_operation` 仅保留为内部辅助，不作为主 FCG 节点；`action_steps[]` 只作为单个图节点内部仍包含多个动作时的 fallback。

### Pipeline 结果批量分析

```text
node scripts/fcg-batch.js --root <run-root> [--similarity-root <dir>] [--output <dir>] [--scope all|grouped|ungrouped] [--concurrency <n>] [--mode quick|full|deep] [--label-llm-assist] [--label-llm-concurrency <n>] [--label-llm-cache <file>] [--refresh]
```

默认值：

- `--root`：如果省略，默认使用项目内 `results/clawhub-top10000`。
- `--similarity-root`：`<root>/similarity`。
- `--output`：`<root>/fcg`。
- `--scope`：默认 `all`，也可以是 `grouped` 或 `ungrouped`。
- `--concurrency`：默认 `4`。
- `--mode`：默认 `full`。
- `--label-llm-assist`：默认关闭；开启时必须配置 `LLM_API_KEY`。
- `--label-llm-cache`：默认使用 `<root>/fcg/label-llm-cache.jsonl`。
- `--refresh`：即使已有 FCG JSON，也重新分析。

批量输出结构：

```text
<root>/fcg/
  skills/
    <skill-id>-<skill-name>-fcg.json
    <skill-id>-<skill-name>-fcg.flow.md
    <skill-id>-<skill-name>-fcg.flow.mmd
  fcg-summary.json
  fcg-summary.md
```

## LLM 配置

环境变量：

- `LLM_API_KEY`：模型 API Key。默认 Markdown 语义门控和可选标签 LLM 辅助都需要。
- `LLM_PROVIDER`：默认 `openai`，也可以是 `dashscope`。
- `LLM_MODEL`：模型名，本包默认 `gpt-5.5`。
- `LLM_ENDPOINT`：可选的 OpenAI-compatible endpoint。
- `LLM_TIMEOUT`：请求超时时间，单位毫秒。
- `DASHSCOPE_ENDPOINT`：可选的 DashScope-compatible endpoint 覆盖。
- `FCG_SEMANTIC_GATE_BATCH_SIZE`：Markdown 语义门控每次 LLM 请求包含的候选数，默认 `10`。
- `FCG_SEMANTIC_GATE_CONCURRENCY`：Markdown 语义门控批次并发数，默认 `4`。
- `FCG_SEMANTIC_GATE_MAX_BATCH_CHARS`：每个 Markdown 语义门控请求的近似字符预算，默认 `60000`；超出预算会自动拆分。
- `FCG_SEMANTIC_GATE_CACHE`：Markdown 语义门控 verdict 的 JSONL 缓存路径。生产 LLM 路径默认使用临时目录缓存；设为 `0` 可关闭。

重要区别：

- `full` / `deep` 的工具边语义校验在配置了 `LLM_API_KEY` 时可以使用 LLM；否则会回退到启发式规则。
- Markdown 语义抽取默认由 LLM 强门控。规则只生成候选，LLM 判断候选是运行时动作、policy rule、definition、schema、example、template、description 还是 discard。公共 CLI/batch/pipeline 缺少 `LLM_API_KEY` 时会预检失败。候选复核会批量提交并缓存；单个候选缺失或无效会降级为 context-only 的 `doc_review_error`，不会变成强 action 证据。
- 测试或内部模式 `semanticLlm:false` 会保留规则候选，但这些只是低置信、需复核的证据，不等价于生产默认门控结果。
- 当前 v3.0 安全传播画像中的数据标签默认是 deterministic 生成的。
- 开启 `--label-llm-assist` 后，LLM 只会在 `generic_data.data`、`payload/content/data` 等模糊字段、`unknown_tail` 或证据低于 `L2` 的场景生成弱候选标签。
- LLM 辅助标签必须来自封闭 ontology，并会被标记为 `mode=llm_assisted`、`evidence_kind=llm_low_confidence_assist`、`requires_review=true`，且置信度有上限。

## 分析器到底构建了什么

### 1. FCG 图

顶层 `nodes` 和 `edges` 是 may-flow 图，来源包括：

- JS/TS/SH 可执行源抽取，包括 script entry、function 和 call 节点。
- 从选定 Markdown 软指令文件中抽取 tool-call。
- 除 `SKILL.md` / `README.md` 之外的 Markdown 软指令文件。
- 只有在不存在其他 Markdown 软指令或可执行脚本来源时，`SKILL.md` 才作为 fallback 节点来源。
- `SKILL.md` 和可选 `README.md` 作为 `documentation_context` 中的复核/路线上下文；`README.md` 永远不作为节点来源。
- 节点输出到节点输入的类型兼容分析。
- 可选的语义边校验。
- 默认运行的 Markdown 文档流程抽取。

FCG 图故意保持偏宽松。它回答的是：“数据或控制是否有可能从这个节点流到那个节点？” 它本身不是 DOE 结论。

文档来源 grounding：

- `documentation_context` 记录 review-only 的 `SKILL.md` / `README.md` 上下文和提取源选择策略，不计入图节点或边。
- 抽取出的 doc/tool/rule/script 节点保留 `source_context`，包含文件、行号、section、局部片段、来源类型和 action evidence。
- 经过复核的 Markdown 候选会带 `semantic_gate`。运行时动作生成 `doc_step` / rule 节点；术语定义、字段 schema、示例、模板和描述性文本会生成 `doc_definition`、`doc_schema`、`doc_example` 等 context-only 节点，并设置 `excludeFromFlow=true`。
- 节点动作，例如 `docAction`、`operationType`、`instructionText`、`formal_semantics.operation_type`，应能在局部 `source_context` 中找到依据；动作证据弱或无法 grounding 时会标记 review，而不是作为强证据静默接受。
- 文档流或语义规则产生的边可带 `source_context` / `edge_evidence`，说明依赖边的局部证据。

### 数据依赖候选验证

FCG 保留细粒度节点，但数据依赖验证默认改为稀疏候选。Extractor 已经给出的结构边会保留；context-only 文档节点不参与 dependency candidate；默认不再做全局 `tool x tool` 或 `script_call x script_call` 式 pairwise 展开。

只有 high-value 候选会使用 dependency LLM：一类是可能改变 DOE observation 的 boundary-impact 候选，另一类是跨文件或跨阶段的 global-route 候选。LLM 复核按 skill 批量执行，并由 `FCG_DEPENDENCY_LLM_MAX_PAIRS`（默认 `32`）和 `FCG_DEPENDENCY_LLM_BATCH_SIZE`（默认 `16`）限制。`FCG_DEPENDENCY_LLM_POLICY=high_value|off|all` 默认是 `high_value`；`all` 只用于调试。缓存可用 `FCG_DEPENDENCY_LLM_CACHE` 控制。

输出统计包含 `dependency_candidate_count`、`dependency_candidate_pruned_count`、`dependency_llm_candidate_count`、`dependency_llm_validated_count`、`dependency_llm_cache_hit_count`。Dependency 边使用 `dependency_structural`、`dependency_rule`、`dependency_llm_high_value` 等 `validation_method`。

### 2. Node Profile 节点画像

FCG 建好后，每个节点都会在 `security_profile.node_profiles` 中得到一个 `node_profile`。这是覆盖在原始图节点之上的第二层安全语义。

粗粒度 `node_roles`：

- `data_introduction`：把数据引入图，例如用户 prompt、文件读取、API 响应、memory 读取、数据库查询、环境变量读取。
- `transform`：转换、切片、总结、脱敏、格式化、聚合或合并数据。
- `control_context`：控制触发或路由，例如 `user.query` 或 trigger 节点。
- `decision`：guard、policy、routing 或 condition 节点。
- `model_inference`：LLM / 模型上下文或推理节点。
- `tool_invocation`：内部或外部工具调用。
- `external_egress`：网络、webhook、API、上传、邮件、第三方发送等外传。
- `local_persistence`：文件、memory、数据库、日志、artifact 写入。
- `command_execution`：shell 或进程执行。
- `destructive_operation`：delete、remove、drop、wipe 等破坏性操作。

细粒度 `security_tags` 包括：

- 输入和读取类：`user_input`、`tool_response`、`file_read`、`memory_read`、`database_read`、`env_read`、`credential_read`、`browser_read`、`network_read`、`email_read`、`calendar_read`、`contact_read`。
- 外传和写入类：`network_egress`、`email_send`、`webhook_post`、`api_call`、`third_party_service`、`model_context`、`file_write`、`memory_write`、`database_write`、`log_write`、`artifact_write`、`shell_exec`。

细粒度 `operation_tags` 包括：

- `field_slice`：抽取或选择字段子集。
- `semantic_extraction`：从一种标签中派生出另一种具体值，例如从用户输入中抽取 API key。
- `summarization`：摘要。
- `aggregation`：把原始记录转成聚合结果。
- `redaction`：移除敏感字段。
- `pseudonymization`：掩码、哈希、匿名化、去标识化。
- `format_conversion`：格式转换或序列化。
- `merge_join`：显式合并多个输入。
- `routing_decision`：选择分支。
- `policy_guard`：allow / deny / guard 规则。

边界元数据：

- `data_surface`：`user_prompt`、`llm_context`、`tool_io`、`local_file`、`memory_store`、`database`、`network`、`browser`、`runtime_env`、`document`、`unknown`。
- `receiver_scope`：`self`、`same_skill`、`local_runtime`、`model_provider`、`first_party_service`、`third_party_service`、`public_network`、`user_recipient`、`unknown`。
- `retention_scope`：`transient`、`session`、`persistent`、`external`、`unknown`。
- `trust_boundary`：`none`、`local_process`、`model_provider`、`external_network`、`persistent_storage`、`user_visible`、`unknown`。

每个 profile 还包含 `confidence` 和 `evidence[]`，用于解释角色和标签是由哪些规则、字段或文本触发的。

v4.5 中作为 fallback 保留的 action-step 元数据：

- `action_steps[]`：当 FCG 无法安全拆成显式 `doc_step` 节点时，用于表达节点内部有序动作序列。
- `action_order_confidence`：内部动作顺序置信度。
- `action_order_source`：`member_steps`、`formal_semantics`、`doc_actions`、`text_order`、`heuristic` 或 `unknown`。
- `has_multi_action`：该节点是否包含多个动作。
- `ambiguous_action_order`：当 filter 和 sink-like 动作共存但顺序不可靠时为 true。

每个 action step 包含 `step_id`、`order`、`operation_type`、step 级 roles/tags、boundary metadata、targets、evidence 和 confidence。Observation 会包含 `action_step_id`、`operation_type`、`order`、`order_confidence`、`ambiguous_action_order`，但仍然只通过 `label_flow_ids` 引用 flow 事实。

### 3. 字段级数据标签

对于 `data_introduction` 节点，profiler 会生成 `data_profile.labels`。一个 source 可以同时引入多个 label。

label 字段：

- `label`：规范标签，例如 `credentials.api_key`。
- `category`：大类，例如 `credentials` 或 `pii`。
- `subtype`：细分类，例如 `api_key`、`email`、`city`。
- `field_name`：命中的字段名。
- `field_path`：schema 或证据路径。
- `origin_node`：数据最初来自哪个节点。
- `origin_node_name`：可读源点名称。
- `introduced_at`：该标签在哪个节点被引入或派生。
- `mode`：`definite` 或 `derived`。
- `confidence`：确定性置信度。
- `evidence_level`：证据强度，`L4` 最强，`L0` 为 fallback。
- `evidence_kind`：标签生成原因，例如 `output_field`、`input_field`、`formal_target`、`instruction_text`、`semantic_derivation`、`fallback`。
- `evidence_text`：简短证据文本。

内置标签族：

- `credentials.api_key`、`credentials.token`、`credentials.password`、`credentials.secret`。
- `pii.email`、`pii.phone`、`pii.address`、`pii.name`、`pii.user_id`。
- `file_content.document`、`file_content.path`。
- `browser_data.cookie`、`browser_data.history`。
- `database_record.record`。
- `location.city`、`location.geo`。
- `financial.payment`。
- `user_prompt.query`。
- `generic_data.data` fallback。
- 传播过程中派生出的 `aggregate_data.summary`、`pseudonymous_data.protected`。

标签生成默认是证据优先、确定性的。它使用节点名、schema、类似 OpenAPI 的输入输出字段、`formal_semantics.targets`、指令文本和节点证据。如果开启 `--label-llm-assist`，LLM 只在 deterministic 证据弱时补充低置信候选标签。这些标签会参与后续传播，但始终保留弱证据标记。

## 安全传播分析 v4.5

`4.5` 使用单标签数据流模型，优先把 Markdown 中的显式步骤提升为 `doc_step` 级 FCG 节点，会把明确的英文复合动作拆成有序 steps，并在非 read 动作消费命名数据对象时插入轻量 implicit object-read step。英文 summarize/classify/extract/parse/analyze 等 LLM-consuming transform 会作为 model-context observation；`action_steps` 仍作为 fallback，用于无法拆成 step 节点但内部包含多个动作的节点。最小语义单元是 `label_flow`：一个标签、一个当前节点、一条 provenance 历史。一个节点上可以同时存在多条 label flows；这些 flows 的集合表示该节点处可观察到的数据集合。

主输出结构：

```json
{
  "security_profile": {
    "version": "4.5",
    "node_profiles": [],
    "label_flows": [],
    "node_flow_sets": [],
    "provenance_graph": {},
    "observations": [],
    "statistics": {}
  }
}
```

### Label Flow 模型

一个 `label_flow` 表示：某个当前节点处，一条具体传播出来的单标签数据流假设。

每条 label flow 携带：

- `label_flow_id`。
- `parent_label_flow_id` 和 `parent_label_flow_ids`：直接上游 flow。普通边传播时就是上一跳；语义派生、聚合、伪匿名化和 storage read 时指向贡献当前 flow 的上游 flow。
- `current_node` 和 `current_node_name`。
- `node_path` 和 `node_names`。
- `edge_path`。
- `label`：且只有一个数据标签对象，例如 `pii.email` 或 `credentials.api_key`。
- `origin_node`、`origin_node_name` 和 `introduced_at`。
- `trigger_context`：控制上下文，例如用户 prompt 或规则触发器。
- `route_history`：这条 label flow 路径上的路由判断。
- `filter_events`：source introduction、field slicing、redaction、derivation、aggregation、pseudonymization、storage read 或 unknown-flow 事件。
- `flow_mode`：`source_introduction`、`may_flow`、`definite_flow`、`derived_flow` 或 `storage_read`。
- `confidence`。
- `terminated`、`termination_reason` 和 `truncated`。
- `merge_group_ids` 和 `related_label_flow_ids`：只表示解释关系，不会把 labels 合并。
- `storage_key`：可选持久化对象键，例如 `local_file:report.md`、`memory_store:user`、`database:orders`。

不存在多标签 flow。如果 `read_profile` 引入 `pii.email`、`pii.phone` 和 `location.city`，分析器会创建三条独立 label flows。

### 路由原则

路由只判断一条单标签 flow 是否能沿某条 FCG 出边继续传播。路由不判断携带哪些 labels，因为每条 flow 已经只包含一个 label。

路由状态：

- `definite_route`：边有强支持，例如 control-flow 边或目标是 sink-like 节点。
- `may_route`：默认保守状态，表示边有可能成立但不确定。
- `blocked`：显式阻断、环路、缺失目标或超过最大深度。

默认策略是保守 flooding：只要路由不是 `blocked`，label flow 就继续传播。

重要含义：

- 普通 transform、tool invocation、sink-like 节点默认不会阻止后续传播。
- decision 和 policy 节点在有 allow / deny / route / branch 证据时可以产生更精确的路由判断。
- cycle 和 depth 控制用于防止无限扩张。

当前内部硬上限：

- `maxLabelFlows = 8000`。
- `maxEvents = 20000`。
- `maxDepth = 12`。
- `maxBranchesPerNode = 64`。
- `maxMergeParents = 6`。

当触发上限时，`statistics.truncated = true`。已生成的 label flows 会保留并标记，不会静默丢弃。

### 筛选原则

筛选只判断当前单个 label 在节点处理后是否还能继续传播，或者是否被替换为新的派生单标签。筛选不判断后继是否可达。

筛选发生在 label flow 从当前节点离开、准备沿下一条边传播时。这样设计是为了保证：

- 当前节点的 observation 看到的是该节点实际收到的数据。
- 后继节点看到的是当前节点处理后的输出。
- 如果 `A -> webhook -> redact -> model`，webhook observation 仍然引用 webhook 已经收到的 label flows；后面的 redaction 不会抹掉已经发生的 webhook observation。

传播函数：

- `unknown_may_flow`：默认透传，保留当前 label。
- `source_introduction`：当中途到达新的 data-introduction 节点时，上游标签可能转为 `trigger_context`，该节点引入自己的真实数据标签作为新的 label flows。
- `semantic_derivation`：从一种标签中派生具体标签，例如用户输入 API key，`extract_api_key` 产生 `credentials.api_key`，origin 仍是 `user.query`，`introduced_at` 是抽取节点。
- `field_slice`：如果当前 label 匹配字段切片意图则保留，否则终止该 label flow 并记录 `field_slice_drop`。
- `redact`：终止匹配的敏感 label flows。
- `aggregate`：把原始 label flows 替换成派生的 `aggregate_data.summary` label flows，`parent_label_flow_ids` 指向贡献来源。
- `pseudonymize`：把原始 label flows 替换成 `pseudonymous_data.protected` label flows。

### 泛洪、汇聚和合并

默认 flooding 是保守的：没有明确阻断，就保留这个数据流假设。

普通汇聚点行为：

- 如果 `A(email) -> C` 且 `B(city) -> C`，C 会包含两条独立 label flows。
- C 不会自动把 `email + city` 合成一个 payload。
- 如果 C 继续分叉到 D 和 E，每条上游 label flow 会独立分叉，并保留自己的 provenance。

显式合并行为：

- 只有被标记为 `merge_join` 或 `aggregation` 的节点，或者 storage write/read bridge，才会建立合并关系。
- `merge_join` 创建 `merge` 事件，并给参与的单标签 flows 添加 `merge_group_ids` / `related_label_flow_ids`。
- `aggregation` 可以创建新的单标签派生 flow，例如 `aggregate_data.summary`。
- merge 是解释事件，不是静默压缩，也不会创建多标签 flow。

这个设计避免普通汇聚点发生标签污染，同时允许真正的 combine / aggregate 操作被表达出来。

### 轻量 Storage Bridge

`4.5` 保留轻量 storage bridge，用于表达“写入同一个持久化对象，之后又被读取”的 provenance，不引入复杂的 `storage_objects` 顶层 schema。

行为：

- 当 label flow 到达持久化写节点时，分析器把它记录到内部 `storageState[storage_key]`。
- 当后续出现相同 `storage_key` 的持久化读节点时，分析器在读节点创建新的单标签 flows。
- 新 flow 继承写入 flow 的 `label` 和原始 `origin_node`。
- 新 flow 的 `introduced_at` 设置为当前 read 节点。
- 新 flow 的 `parent_label_flow_ids` 指向对应写入 flow。
- 新 flow 携带相同 `storage_key`。
- 如果同一个 storage key 被写入两条或更多 label flows，`provenance_graph.events.merge[]` 会记录 `storage_merge` 事件，相关 flows 会得到相同的 `merge_group_ids`。

`storage_key` 只从已有证据中推断：

- `formal_semantics.targets`。
- 节点名，例如 `write.report.md` 或 `read.report.md`。
- edge `data_flow` 字段。
- 节点 `security_tags`，例如 `file_write`、`memory_write`、`database_write`。

示例：

- `write.report.md` / `read.report.md` -> `local_file:report.md`。
- `write.memory.user` / `read.memory.user` -> `memory_store:user`。
- `insert.orders` / `query.orders` -> `database:orders`。
- unknown fallback 只在同类 storage 内保守桥接，例如 `local_file:unknown`，不会跨 file / memory / database surface 桥接。

### Observations：汇点观察

Observation 是 sink-like 节点处的快照。它只包含节点上下文和 label flow 引用，不复制 flow 级事实。

sink-like roles：

- `external_egress`
- `model_inference`
- `local_persistence`
- `command_execution`
- `destructive_operation`
- `tool_invocation`

Observation schema：

```json
{
  "observation_id": "obs_000001",
  "node_id": "node_webhook",
  "node_name": "send.webhook",
  "node_roles": ["external_egress"],
  "security_tags": ["network_egress", "webhook_post"],
  "boundary": {
    "data_surface": "network",
    "receiver_scope": "third_party_service",
    "retention_scope": "external",
    "trust_boundary": "external_network"
  },
  "label_flow_ids": ["lf_000001", "lf_000002"]
}
```

如果要查看 labels、origins、trigger context、route history、filter history、confidence 或 paths，需要用 `observation.label_flow_ids[]` 回查 `security_profile.label_flows[]`。

分析器会为每个收到至少一条 label flow 的 sink-like 节点生成一个 observation。同一 sink 处的多个 labels 用多条被引用的 label flows 表示，而不是把 flow 字段复制进 observation。

### Provenance Graph：从汇点反推源点

v4.5 的 provenance graph 以 `label_flow_id` 为主键。

`security_profile.provenance_graph` 包含：

- `label_flow_nodes`：每条 label flow 的紧凑视图。
- `propagation_edges`：父 flow 到子 flow 的传播边。
- `observation_links`：observation 到 label flow 的链接。
- `events.routing`：路由判断事件。
- `events.filtering`：source introduction、field slicing、redaction、derivation、aggregation、pseudonymization、storage read、unknown-flow 等事件。
- `events.merge`：显式 `merge_join`、`aggregate` 和 `storage_merge` 事件。
- `events.truncation`：规模上限截断事件。

从汇点反推源点的步骤：

1. 从 `observations[].label_flow_ids[]` 开始。
2. 在 `security_profile.label_flows[]` 或 `provenance_graph.label_flow_nodes[]` 中找到对应 flow。
3. 查看它的 `label`、`node_path`、`edge_path`、`origin_node`、`introduced_at`、`trigger_context`、`route_history`、`filter_events`、`storage_key` 和 `confidence`。
4. 沿 `parent_label_flow_ids` 或 `provenance_graph.propagation_edges` 反向追踪，直到 source-introduction flows。
5. 使用 filtering、routing 和 merge events 解释标签为什么被保留、删除、派生、路由或经由 storage bridge 传播。

这是一张用于解释和回溯的 provenance graph，不是压缩后的路径列表。不同标签、不同分支、不同触发上下文和 storage bridge 都会保留。

## 输出文件

当使用 `--output results/skill-fcg.json` 时，会生成：

```text
results/skill-fcg.json
results/skill-fcg.flow.md
results/skill-fcg.flow.mmd
```

主 JSON 字段：

- `meta`：skill 名称、版本、分析器元数据。
- `nodes`：FCG 节点。
- `edges`：FCG 边。
- `documentation_context`：review-only 文档上下文和来源选择策略。
- `source_sink`：legacy/debug 字段；新的下游消费者应优先读取 `security_profile`。
- `paths`：采样/debug 路径和压缩元数据。
- `statistics`：图级统计。
- `risks`：legacy 路径风险输出。
- `security_profile`：v4.5 单标签安全传播画像，包含 step 级文档流、英文复合动作拆分和隐式对象读取。

doc/tool/rule 节点可能包含 `source_context`；文档来源的边可能包含 `source_context` 或 `edge_evidence`。

为了支持批量分析，`security_profile.label_flows` 是有界展开；达到 transfer 上限时会通过 `security_profile.statistics.truncated` 和 `truncation_events` 标记，不表示已经穷尽枚举所有可能路径。Transfer 展开会优先选择到达 observation boundary 的边，然后再做普通中间传播。默认 transfer 上限为分析级别（`maxLabelFlows=5000`、`maxEvents=30000`、`maxDepth=12`、`maxBranchesPerNode=48`），也可通过 `FCG_SECURITY_MAX_LABEL_FLOWS`、`FCG_SECURITY_MAX_EVENTS`、`FCG_SECURITY_MAX_DEPTH`、`FCG_SECURITY_MAX_BRANCHES_PER_NODE`、`FCG_SECURITY_MAX_MERGE_PARENTS`、`FCG_SECURITY_MAX_RELATED_FLOWS`、`FCG_SECURITY_MAX_MERGE_GROUPS_PER_FLOW` 调整。
`full` 模式仍会限制部分大型中间展开，但 Markdown 文档语义抽取默认不再设置硬上限。只有在需要显式安全阈值时才把 `FCG_MAX_DOC_FLOW_NODES` 设为正整数；未设置或设为 `0` 表示 unlimited。其他内部展开宽度可用 `FCG_MAX_CALLSITE_MEDIATION_NODES` 或 `FCG_DEPENDENCY_MAX_CANDIDATES` 调整。Markdown 门控吞吐和复用可用 `FCG_SEMANTIC_GATE_BATCH_SIZE`、`FCG_SEMANTIC_GATE_CONCURRENCY`、`FCG_SEMANTIC_GATE_MAX_BATCH_CHARS` 或 `FCG_SEMANTIC_GATE_CACHE` 调整。

Markdown 报告包含：

- Mermaid 图。
- FCG 统计。
- path/debug 摘要。
- Markdown formal semantics。
- security transfer analysis 摘要。
- observations 表。
- 节点、边、路径、风险和 security profile 的有界 JSON 预览；完整机器可读输出以 `.json` 文件为准。

## ClawHub 辅助脚本

旧的 URL 列表辅助脚本仍可使用：

```text
node scripts/analyze-clawhub.js --url <skill_url> [--url <skill_url> ...] [--results <dir>] [--llm-timeout <ms>] [--skip-existing]
node scripts/analyze-clawhub.js --list <urls.txt> [--results <dir>] [--llm-timeout <ms>] [--skip-existing]
```

当前完整 pipeline 更推荐使用仓库根目录的一键 pipeline 或本包的 `scripts/fcg-batch.js`。

## 测试

```powershell
cd D:\projects\SkillFlow\packages\skill-fcg-analyzer
npm test
```

根目录 pipeline 测试：

```powershell
cd D:\projects\SkillFlow
node --test "test/**/*.test.js"
```

## 面向后续 DOE 分析的说明

- FCG 边是 may-flow candidate，不是最终 DOE 证明。
- `security_profile.observations` 是 DOE evidence 的最佳入口，因为它说明了哪些 sink-like 节点观察到了哪些 `label_flow_ids`。
- 通过 `label_flow_ids` 回查 `security_profile.label_flows[]`，再使用 `provenance_graph` 解释源点链路、筛选、路由、合并和 storage bridge。
- `node_profiles` 用于理解节点的 source/sink 语义和信任边界。
- DOE 通常应按每条被观察到的 `label_flow` 独立评估；merge 和 storage 关系只是解释字段，不是去重规则。

## 项目结构

```text
skill-fcg-analyzer/
  src/
    analyzer/
    classifier/
    output/
    parser/
    security/
  scripts/
  templates/
  test/
  package.json
  README.md
  README-CH.md
```

## License

MIT




