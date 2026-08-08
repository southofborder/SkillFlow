# SkillFlow DOE Analyzer 中文说明

`skill-doe-analyzer` 是独立的 potential data over-exposure 分析器。它读取已有 FCG JSON，不修改 FCG 输出，并按 `(observation_id, label_flow_id)` 生成 DOE assessment。

DOE 输出是复核证据，不声称运行时已经确认泄露。

## 使用方式

分析单个 FCG 文件：

```powershell
cd D:\projects\SkillFlow\packages\skill-doe-analyzer
node src\index.js analyze --fcg D:\path\skill-fcg.json --out D:\path\skill-doe.json --pretty --llm-cache D:\path\doe-llm-cache.jsonl
```

批量分析 pipeline 生成的 FCG：

```powershell
node scripts\doe-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k100
```

把 DOE 路径还原成自然语言审计报告：

```powershell
node scripts\doe-path-report.js --root D:\projects\SkillFlow\results\clawhub-top-k100 --skill skill_0001
```

默认 DOE 使用 LLM necessity judge，需要配置 `LLM_API_KEY`。只有明确需要离线规则模式时，才传入 `--no-llm-judge`。

如果 OpenAI-compatible endpoint 会 reset 较大的 HTTP/1.1 请求，或者 DNS 轮询到不可达 IP，可以设置 `LLM_HTTP2=1`；必要时再设置 `LLM_ENDPOINT_RESOLVED_IP=<ip>` 固定底层连接 IP，同时仍使用原 endpoint host 进行 TLS/SNI。

## CLI 参数

单文件分析：

- `--fcg <file>`：必填，输入 FCG JSON。
- `--out <file>`：输出 DOE JSON；不传则写到 stdout。
- `--group-baseline <file>`：可选的同组行为基线。
- `--threshold <n>`：高分统计阈值，默认 `0.70`。
- `--pretty`：格式化 JSON。
- `--no-llm-judge`：关闭默认 LLM necessity judge，使用规则评分。
- `--llm-cache <file>`：LLM judge JSONL 缓存。
- `--llm-batch-size <n>`：每次 LLM 请求包含的 assessment unit 数，默认 `4`。
- `--llm-votes <n>`：首轮每个 assessment unit 的 LLM 投票数，默认 `1`。
- `--llm-concurrency <n>`：LLM judge 请求并发数，默认 `2`。
- `--llm-escalation-votes <n>`：高风险或不确定 unit 复判票数，默认 `3`。
- `--llm-escalation-policy <mode>`：`risk_or_uncertain`、`none` 或 `all`，默认 `risk_or_uncertain`。
- `--llm-max-batch-chars <n>`：单个 LLM batch 的近似字符预算，默认 `60000`。
- `--llm-model <name>`、`--llm-endpoint <url>`、`--llm-timeout <ms>`：覆盖对应环境变量。

批量分析：

- `--root <dir>`：包含 `fcg/skills` 的运行根目录。
- `--fcg-root <dir>`：默认 `<root>/fcg`。
- `--output <dir>`：默认 `<root>/doe`。
- `--concurrency <n>`：默认 `2`。
- `--threshold <n>`、`--llm-cache <file>`、`--llm-batch-size <n>`、`--llm-votes <n>`、`--llm-concurrency <n>`、`--llm-escalation-votes <n>`、`--llm-escalation-policy <mode>`、`--llm-max-batch-chars <n>`、`--refresh`。
- `--no-llm-judge`：显式规则模式批处理。

路径自然语言报告：

- `--root <dir>`：包含 `fcg/`、`doe/` 和 `zips/` 的运行根目录。
- `--fcg-root <dir>`、`--doe-root <dir>`、`--zips-root <dir>`：覆盖默认输入目录。
- `--output <path>`：输出目录或 `.md` / `.json` 文件路径，默认 `<root>/doe/reports`。
- `--skill <text>`：按 skill id、skill name 或输出文件名片段过滤。
- `--scope potential|boundary|all`：默认 `potential`，即导出 `potential_doe || requires_review`。
- `--format md|json|both`：默认 `both`。

## 方法

只有跨越 DOE observation boundary 的 observation 才会被报告为 potential DOE。边界来自 `observation.boundary`，包括外部网络、模型提供方、持久化留存、用户可见输出等信息可见域变化。`command_execution` 和 `destructive_operation` 不会因为角色本身被当作 DOE 边界。

```text
component_score = 0.7 * llm_component_score + 0.3 * rule_component_score
necessity_score = min(action_input_need, receiver_semantic_need, flow_path_task_need, boundary_node_task_need)
doe_score = clamp(exposure_score * (1 - necessity_score) + baseline_adjustment, 0, 1)
```

Evidence pack 分为 `boundary_evidence`、`local_action_receiver_evidence`、`flow_path_evidence`、`task_context_evidence` 和 `provenance_filter_storage_evidence`。全局必要性判断完整 `label_flow` 路径，而不是只看 label 名称。

Evidence pack 会保留 FCG 节点的 `source_context.action_evidence`、Markdown `semantic_gate` 语法/分类结论，以及 JS/TS/SH 脚本节点的 `ownerScript`、`functionName`、`callee` 等上下文。`doc_definition`、`doc_schema`、`doc_example` 等 context-only 节点可以作为任务语义证据，但不作为 label-flow path 节点。

LLM payload 会把重复的任务、文档和节点证据压缩到 `shared_context`；每个 assessment unit 只保留自己的 boundary、局部 action/receiver、完整 `label_flow` 路径和必要 provenance/filter/storage delta。默认策略是首轮全量单票 LLM，只有高风险或不确定项追加多票复判。

## 输出

输出版本为 `0.3`。单条 assessment 的核心字段包括：

- `boundary_crossed`、`boundary_basis`、`exposure_score`、`necessity_score`、`potential_doe`、`doe_score`。
- `local_necessity` 和 `global_necessity`。
- `rule_component_scores`、`component_scores`、`llm_necessity_score`。
- `llm_judge`：模型、prompt 版本、投票数、component evidence refs、短 reasoning、disagreement、stage 和是否 escalation。
- `statistics`：assessment 数、边界跨越数、potential DOE 数、review 数、LLM first-pass 数、escalated 数、timeout split 数、cache hit 数和 warning 数。

批量输出结构：

```text
<root>/doe/
  skills/
    <skill-id>-<skill-name>-doe.json
  doe-summary.json
  doe-summary.md
  doe-llm-cache.jsonl
  reports/
    doe-path-report.md
    doe-path-report.json
```

路径报告是只读审计辅助产物。它把 DOE assessment 还原成自然语言路径，优先从原始 zip 读取精确原文行，找不到时回退到 FCG 的 `source_context`。报告会添加 `template_or_example_source`、`path_label_metadata_only`、`model_context_expected_flow` 等 audit notes。

`label_subtype=path` 表示文件路径、文件名或类似路径的字符串，不是图路径，也不是 label flow path。
