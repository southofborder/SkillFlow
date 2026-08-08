# Skill FCG Analyzer

`skill-fcg-analyzer` analyzes OpenClaw skills and produces a Function Call Graph (FCG) plus a security-oriented, instance-level data-flow profile. It is one of the packages under `packages/` and is normally used after skills have been downloaded and grouped by the pipeline.

The analyzer has two layers:

- FCG construction: parse skill files, extract tool/document nodes, infer may-flow edges, and build the graph.
- Security transfer analysis v4.5: profile each node, propagate field-level data as single-label `label_flow` facts, emit reference-only sink observations, and build a provenance graph that traces each observed label flow back to its origin, route, filters, and storage bridges.

## Requirements

- Node.js `>=18`
- Run commands from `packages/skill-fcg-analyzer` unless stated otherwise.

```powershell
cd D:\projects\SkillFlow\packages\skill-fcg-analyzer
npm install
```

## Quick Start

Analyze one skill zip. Markdown semantic gating runs by default and requires `LLM_API_KEY`:

```powershell
node src\index.js analyze "D:\path\skill.zip" --mode full --output results\skill-fcg.json
```

Analyze a directory containing a `SKILL.md`:

```powershell
node src\index.js analyze "D:\path\skill-dir" --mode full --output results\skill-fcg.json
```

Run the batch analyzer on a pipeline output root:

```powershell
node scripts\fcg-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k1000
```

Refresh existing FCG outputs:

```powershell
node scripts\fcg-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k1000 --refresh
```

## CLI

### Single Skill

```text
node src/index.js analyze <input> [--output <file>] [--mode <quick|full|deep>] [--llm-timeout <ms>] [--label-llm-assist] [--label-llm-concurrency <n>] [--label-llm-cache <file>] [--flowchart <file.md>]
```

Options:

- `--output <file>`: JSON output path. Parent directories are created automatically.
- `--mode quick|full|deep`: analysis mode.
- `quick`: type-based edge inference only. Fastest.
- `full`: type compatibility plus semantic edge validation. Uses LLM validation if configured, otherwise heuristic fallback.
- `deep`: `full` plus extra structural control-flow edges.
- `--label-llm-assist`: optional LLM assistance for low-confidence data labels only. Requires `LLM_API_KEY`.
- `--label-llm-concurrency <n>`: concurrency for label assistance. Default `2`.
- `--label-llm-cache <file>`: JSONL cache for label assistance results.
- `--llm-timeout <ms>`: network/LLM timeout. Default comes from `LLM_TIMEOUT` or `30000`.
- `--flowchart <file.md>`: custom Markdown report path. The `.mmd` Mermaid sibling is generated automatically.

Document-flow granularity:

- By default, explicit Markdown actions are emitted as `doc_step` FCG nodes.
- Step-level nodes preserve line, step index, action, target, instruction text, and `formal_semantics`.
- Sequential Markdown steps are connected by `control_flow` edges.
- Cross-document Markdown references jump from the current `doc_step` to the referenced document's first `doc_step`.
- Clear English compound actions such as `summarize ... and save ...`, `read ..., redact ..., and send ...`, and `extract ... and call ...` are split into ordered `doc_step` nodes.
- English LLM-consuming transforms (`summarize`, `classify`, `extract`, `parse`, `analyze`) are treated as model-context observation points.
- Non-read English actions that consume named data objects, such as `write the email content`, get a lightweight implicit read/source `doc_step` unless that object already has a prior producer in the same document.
- Legacy merged `doc_operation` helpers are not used as primary FCG nodes; `action_steps[]` remains the fallback for nodes that still contain multiple actions inside one graph node.

### Batch From Pipeline Results

```text
node scripts/fcg-batch.js --root <run-root> [--similarity-root <dir>] [--output <dir>] [--scope all|grouped|ungrouped] [--concurrency <n>] [--mode quick|full|deep] [--label-llm-assist] [--label-llm-concurrency <n>] [--label-llm-cache <file>] [--refresh]
```

Defaults:

- `--root`: defaults to the project `results/clawhub-top10000` if omitted.
- `--similarity-root`: `<root>/similarity`.
- `--output`: `<root>/fcg`.
- `--scope`: `all`. Other choices are `grouped` and `ungrouped`.
- `--concurrency`: `4`.
- `--mode`: `full`.
- `--label-llm-assist`: disabled by default and requires `LLM_API_KEY` when enabled.
- `--label-llm-cache`: defaults to `<root>/fcg/label-llm-cache.jsonl`.
- `--refresh`: re-run analysis even if an FCG JSON already exists.

Batch output layout:

```text
<root>/fcg/
  skills/
    <skill-id>-<skill-name>-fcg.json
    <skill-id>-<skill-name>-fcg.flow.md
    <skill-id>-<skill-name>-fcg.flow.mmd
  fcg-summary.json
  fcg-summary.md
```

## LLM Configuration

Environment variables:

- `LLM_API_KEY`: API key. Required for the default Markdown semantic gate, and for optional label LLM assist.
- `LLM_PROVIDER`: `openai` by default, or `dashscope`.
- `LLM_MODEL`: model name, default `gpt-5.5` in this package.
- `LLM_ENDPOINT`: optional OpenAI-compatible endpoint.
- `LLM_TIMEOUT`: request timeout in milliseconds.
- `DASHSCOPE_ENDPOINT`: optional DashScope-compatible endpoint override.
- `FCG_SEMANTIC_GATE_BATCH_SIZE`: Markdown semantic gate candidates per LLM request. Default `10`.
- `FCG_SEMANTIC_GATE_CONCURRENCY`: concurrent Markdown semantic gate batches. Default `4`.
- `FCG_SEMANTIC_GATE_MAX_BATCH_CHARS`: approximate max characters per Markdown semantic gate request. Default `60000`; oversized batches are split automatically.
- `FCG_SEMANTIC_GATE_CACHE`: optional JSONL cache path for Markdown semantic gate verdicts. By default production LLM runs use a temp-dir cache; set `0` to disable.

Important distinction:

- Tool-edge semantic validation in `full` / `deep` can use `LLM_API_KEY` if configured; otherwise it falls back to heuristics.
- Markdown semantic extraction is LLM-gated by default. Rules only produce candidates; the LLM decides whether a candidate is a runtime action, policy rule, definition, schema, example, template, description, or discard. Missing `LLM_API_KEY` fails public CLI/batch/pipeline preflight. Candidate review is batched and cached; failed or missing per-candidate verdicts become context-only `doc_review_error` nodes instead of strong action evidence.
- Test-only/internal `semanticLlm:false` keeps rule candidates, but they are low-confidence review evidence and are not equivalent to gated production output.
- Security labels are deterministic by default.
- With `--label-llm-assist`, LLMs may generate weak candidate labels only for low-confidence deterministic cases such as `generic_data.data`, ambiguous `payload/content/data` fields, `unknown_tail`, or evidence below `L2`.
- LLM-assisted labels are restricted to the closed ontology, confidence-capped, and marked `mode=llm_assisted`, `evidence_kind=llm_low_confidence_assist`, and `requires_review=true`.

## What The Analyzer Builds

### 1. FCG Graph

The top-level `nodes` and `edges` are the may-flow graph. They come from:

- JS/TS/SH executable-source extraction, including script entry, function, and call nodes.
- Markdown/tool-call extraction from selected soft-instruction files.
- Markdown soft-instruction files other than `SKILL.md` / `README.md`.
- `SKILL.md` only as a fallback node source when no other markdown soft-instruction or executable script source exists.
- `SKILL.md` and optional `README.md` as review/route context in `documentation_context`; `README.md` is never a node source.
- Type compatibility between node outputs and inputs.
- Optional semantic edge validation.
- Default document-flow extraction from Markdown soft instructions.

The FCG graph is intentionally broad. It answers: "Could data or control plausibly flow from this node to that node?" It is not yet a DOE verdict.

Document-source grounding:

- `documentation_context` records review-only `SKILL.md` / `README.md` context and the extraction source policy. It does not count as graph nodes or edges.
- Extracted doc/tool/rule/script nodes preserve `source_context` with file, line, section, local snippet, source type, and action evidence.
- Markdown candidates include `semantic_gate` when reviewed. Runtime actions become `doc_step` / rule nodes; definitions, schemas, examples, templates, and descriptive prose become context-only nodes such as `doc_definition`, `doc_schema`, or `doc_example` with `excludeFromFlow=true`.
- Node actions such as `docAction`, `operationType`, `instructionText`, and `formal_semantics.operation_type` should be grounded in the local `source_context`; weak or ungrounded action evidence is marked for review instead of being treated as strong support.
- Edges created from document flow or semantic-rule extraction may include `source_context` / `edge_evidence` explaining the local evidence for the dependency.

### Dependency Candidate Validation

FCG keeps fine-grained nodes, but dependency validation is sparse by default. Extractor-provided structural edges are preserved, context-only documentation nodes are excluded from dependency candidates, and generic `tool x tool` / `script_call x script_call` pairwise expansion is not used as the default graph builder.

Only high-value candidates use dependency LLM review: boundary-impact candidates that may change DOE observations, and global-route candidates that bridge files or stages. Review is batched per skill and capped by `FCG_DEPENDENCY_LLM_MAX_PAIRS` (default `32`) and `FCG_DEPENDENCY_LLM_BATCH_SIZE` (default `16`). `FCG_DEPENDENCY_LLM_POLICY=high_value|off|all` defaults to `high_value`; `all` is for debugging only. Cache can be controlled with `FCG_DEPENDENCY_LLM_CACHE`.

Statistics include `dependency_candidate_count`, `dependency_candidate_pruned_count`, `dependency_llm_candidate_count`, `dependency_llm_validated_count`, and `dependency_llm_cache_hit_count`. Dependency edges use `validation_method` values such as `dependency_structural`, `dependency_rule`, and `dependency_llm_high_value`.

### 2. Node Profiles

After FCG construction, every node receives a `node_profile` under `security_profile.node_profiles`. This is a second semantic layer over the raw graph node.

Coarse `node_roles`:

- `data_introduction`: introduces data into the flow, such as user prompt, file read, API response, memory read, database query, environment read.
- `transform`: transforms, slices, summarizes, redacts, formats, aggregates, or merges data.
- `control_context`: controls activation or routing, such as `user.query` or trigger nodes.
- `decision`: guard, policy, routing, or condition node.
- `model_inference`: LLM/model context or completion node.
- `tool_invocation`: external or internal tool invocation.
- `external_egress`: network, webhook, API, upload, email, or third-party transfer.
- `local_persistence`: file/memory/database/log/artifact write.
- `command_execution`: shell/process execution.
- `destructive_operation`: delete/remove/drop/wipe style operation.

Fine-grained `security_tags` include:

- Input/read tags: `user_input`, `tool_response`, `file_read`, `memory_read`, `database_read`, `env_read`, `credential_read`, `browser_read`, `network_read`, `email_read`, `calendar_read`, `contact_read`.
- Egress/write tags: `network_egress`, `email_send`, `webhook_post`, `api_call`, `third_party_service`, `model_context`, `file_write`, `memory_write`, `database_write`, `log_write`, `artifact_write`, `shell_exec`.

Fine-grained `operation_tags` include:

- `field_slice`: extracts or selects a subset of fields.
- `semantic_extraction`: derives a concrete value from another label, such as extracting an API key from user prompt text.
- `summarization`: summarizes input.
- `aggregation`: converts raw records into aggregate output.
- `redaction`: removes sensitive fields.
- `pseudonymization`: masks, hashes, anonymizes, or de-identifies.
- `format_conversion`: converts or serializes format.
- `merge_join`: explicitly combines multiple inputs.
- `routing_decision`: chooses branches.
- `policy_guard`: allow/deny/guard rule.

Boundary metadata:

- `data_surface`: `user_prompt`, `llm_context`, `tool_io`, `local_file`, `memory_store`, `database`, `network`, `browser`, `runtime_env`, `document`, `unknown`.
- `receiver_scope`: `self`, `same_skill`, `local_runtime`, `model_provider`, `first_party_service`, `third_party_service`, `public_network`, `user_recipient`, `unknown`.
- `retention_scope`: `transient`, `session`, `persistent`, `external`, `unknown`.
- `trust_boundary`: `none`, `local_process`, `model_provider`, `external_network`, `persistent_storage`, `user_visible`, `unknown`.

Each profile also contains `confidence` and `evidence[]`, so downstream tools can see which rule or text fragment caused the role/tag decision.

Action-step metadata retained as a v4.5 fallback:

- `action_steps[]`: ordered operations inferred inside a node when the FCG cannot safely split them into explicit `doc_step` nodes.
- `action_order_confidence`: confidence in the internal order.
- `action_order_source`: `member_steps`, `formal_semantics`, `doc_actions`, `text_order`, `heuristic`, or `unknown`.
- `has_multi_action`: true when a node contains more than one action step.
- `ambiguous_action_order`: true when filter and sink-like actions coexist but order is not reliable.

Each action step carries `step_id`, `order`, `operation_type`, step-level roles/tags, boundary metadata, targets, evidence, and confidence. Observations include `action_step_id`, `operation_type`, `order`, `order_confidence`, and `ambiguous_action_order`, while still only referencing `label_flow_ids` for flow facts.

### 3. Field-Level Data Labels

For `data_introduction` nodes, the profiler builds `data_profile.labels`. A single source can introduce multiple labels.

Label fields:

- `label`: canonical label, for example `credentials.api_key`.
- `category`: high-level category, for example `credentials` or `pii`.
- `subtype`: detailed subtype, for example `api_key`, `email`, `city`.
- `field_name`: matched field name.
- `field_path`: schema or evidence path.
- `origin_node`: node where this data originally came from.
- `origin_node_name`: readable origin name.
- `introduced_at`: node where this label was introduced or derived.
- `mode`: `definite` or `derived`.
- `confidence`: deterministic confidence score.
- `evidence_level`: evidence strength, from `L4` strongest to `L0` fallback.
- `evidence_kind`: why the label was created, such as `output_field`, `input_field`, `formal_target`, `instruction_text`, `semantic_derivation`, `fallback`.
- `evidence_text`: short evidence text.

Built-in label families:

- `credentials.api_key`, `credentials.token`, `credentials.password`, `credentials.secret`.
- `pii.email`, `pii.phone`, `pii.address`, `pii.name`, `pii.user_id`.
- `file_content.document`, `file_content.path`.
- `browser_data.cookie`, `browser_data.history`.
- `database_record.record`.
- `location.city`, `location.geo`.
- `financial.payment`.
- `user_prompt.query`.
- `generic_data.data` fallback.
- Transfer-derived labels such as `aggregate_data.summary` and `pseudonymous_data.protected`.

The labeler is evidence-first and deterministic by default. It uses names, schemas, OpenAPI-like input/output fields, `formal_semantics.targets`, instruction text, and node evidence. If `--label-llm-assist` is enabled, the LLM can add low-confidence candidate labels only when deterministic evidence is weak. These labels propagate like normal labels but remain explicitly marked as weak evidence.

## Security Transfer Analysis v4.5

Version `4.5` uses a single-label data-flow model, prefers explicit Markdown `doc_step` FCG nodes for ordered document instructions, splits clear English compound actions into ordered steps, and inserts lightweight implicit object-read steps when non-read actions consume a named data object. English LLM-consuming transforms such as summarize/classify/extract/parse/analyze are modeled as model-context observations; `action_steps` remain as a fallback for non-step nodes that still contain multiple actions. The smallest semantic unit is a `label_flow`: one label, one current node, one provenance history. A node can contain many label flows at the same time; that node-level set represents the data available at that point.

Main output fields:

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

### Label Flow Model

A `label_flow` means: one concrete propagated data-label hypothesis at one current node.

Each label flow carries:

- `label_flow_id`.
- `parent_label_flow_id` and `parent_label_flow_ids`: direct upstream flow(s). For ordinary edge propagation this is the previous hop; for semantic derivation, aggregation, pseudonymization, and storage reads it points to the contributing upstream flow(s).
- `current_node` and `current_node_name`.
- `node_path` and `node_names`.
- `edge_path`.
- `label`: exactly one data label object, such as `pii.email` or `credentials.api_key`.
- `origin_node`, `origin_node_name`, and `introduced_at`.
- `trigger_context`: control context such as user prompt or rule trigger.
- `route_history`: route decisions along this label flow path.
- `filter_events`: source introduction, field slicing, redaction, derivation, aggregation, pseudonymization, storage read, or unknown-flow events.
- `flow_mode`: `source_introduction`, `may_flow`, `definite_flow`, `derived_flow`, or `storage_read`.
- `confidence`.
- `terminated`, `termination_reason`, and `truncated`.
- `merge_group_ids` and `related_label_flow_ids`: explanatory relationships only; they do not merge labels.
- `storage_key`: optional persisted object key, such as `local_file:report.md`, `memory_store:user`, or `database:orders`.

There is no multi-label flow. If `read_profile` introduces `pii.email`, `pii.phone`, and `location.city`, the analyzer creates three independent label flows.

### Routing Principle

Routing decides only whether a single label flow can continue along an outgoing FCG edge. It does not decide which labels are carried, because each flow already contains exactly one label.

Route states:

- `definite_route`: the edge is strongly supported, such as control-flow edges or sink-like targets.
- `may_route`: the default conservative state when the edge is plausible but not certain.
- `blocked`: explicit block, cycle, missing target, or max-depth stop.

Default policy: conservative flooding. If the route is not `blocked`, the label flow propagates.

Important implications:

- Ordinary transforms, tool invocations, and sink-like nodes do not stop propagation by default.
- Decision and policy nodes may produce more precise routing decisions when evidence contains allow/deny/route/branch semantics.
- Cycle and depth controls prevent infinite expansion.

Current internal hard limits:

- `maxLabelFlows = 8000`.
- `maxEvents = 20000`.
- `maxDepth = 12`.
- `maxBranchesPerNode = 64`.
- `maxMergeParents = 6`.

When a limit is hit, `statistics.truncated = true`; generated label flows are retained and marked rather than silently discarded.

### Filtering Principle

Filtering decides whether the current single label survives after a node processes data, or whether it is replaced by a derived single label. Filtering does not decide whether a successor is reachable.

Filtering is applied when a label flow leaves the current node for the next edge. This is deliberate:

- The current node observation sees what the node received.
- Successors see what the node emitted after slicing/redaction/aggregation/etc.
- If `A -> webhook -> redact -> model`, the webhook observation still references label flows received by the webhook. The later redaction does not erase that observation.

Transfer functions:

- `unknown_may_flow`: default pass-through, keeps the current label.
- `source_introduction`: when a data-introduction node is reached mid-path, upstream labels may become `trigger_context` and the node introduces its own labels as new label flows.
- `semantic_derivation`: derives a concrete label from another label, for example user enters an API key and `extract_api_key` produces `credentials.api_key` with origin still at `user.query` and `introduced_at` at the extractor node.
- `field_slice`: keeps the current label if it matches the slice intent; otherwise terminates that label flow and records `field_slice_drop`.
- `redact`: terminates matching sensitive label flows.
- `aggregate`: replaces raw label flows with derived `aggregate_data.summary` label flows, with `parent_label_flow_ids` pointing to contributing flows.
- `pseudonymize`: replaces raw label flows with `pseudonymous_data.protected` label flows.

### Flooding, Join, and Merge

Default flooding is intentionally conservative: no clear blocker means the data-flow hypothesis is kept.

Plain join behavior:

- If `A(email) -> C` and `B(city) -> C`, C contains two separate label flows.
- C does not automatically union `email + city` into one payload.
- If C fans out to D and E, each incoming label flow branches independently and keeps its own provenance.

Explicit merge behavior:

- Only nodes tagged `merge_join` or `aggregation`, or storage write/read bridges, create merge relationships.
- `merge_join` creates a `merge` event and adds `merge_group_ids` / `related_label_flow_ids` to the participating single-label flows.
- `aggregation` may create a new single-label derived flow such as `aggregate_data.summary`.
- Merge is explanatory, not silent compression, and it does not create a multi-label flow.

This design prevents label pollution at convergence points while still representing real combine/aggregate operations.

### Lightweight Storage Bridge

Version `4.5` keeps the lightweight bridge for persistent storage without introducing a separate `storage_objects` schema.

Behavior:

- When a label flow reaches a persistent write node, the analyzer records it in an internal `storageState` under a `storage_key`.
- When a persistent read node with the same `storage_key` is seen, the analyzer creates new single-label flows at the read node.
- The new flow inherits the written flow's `label` and original `origin_node`.
- The new flow sets `introduced_at` to the read node.
- The new flow sets `parent_label_flow_ids` to the written flow.
- The new flow carries the same `storage_key`.
- If two or more label flows are written to the same storage key, `provenance_graph.events.merge[]` records a `storage_merge` event and the involved flows receive the same `merge_group_ids` entry.

Storage keys are inferred from existing evidence only:

- `formal_semantics.targets`.
- node names such as `write.report.md` or `read.report.md`.
- edge `data_flow` fields.
- node `security_tags` such as `file_write`, `memory_write`, or `database_write`.

Examples:

- `write.report.md` / `read.report.md` -> `local_file:report.md`.
- `write.memory.user` / `read.memory.user` -> `memory_store:user`.
- `insert.orders` / `query.orders` -> `database:orders`.
- Unknown fallbacks stay within the same storage class, such as `local_file:unknown`; they are not bridged across file, memory, and database surfaces.

### Observations

An observation is a sink-like node snapshot. It contains node context and references to label flows; it does not copy flow-level facts.

Sink-like roles:

- `external_egress`
- `model_inference`
- `local_persistence`
- `command_execution`
- `destructive_operation`
- `tool_invocation`

Observation schema:

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

To inspect labels, origins, trigger context, route history, filter history, confidence, or paths, resolve `observation.label_flow_ids[]` against `security_profile.label_flows[]`.

The analyzer emits one observation per sink-like node that receives at least one label flow. Multiple labels at the same sink are represented by multiple referenced label flows, not by duplicated flow fields inside the observation.

### Provenance Graph: Tracing Sink Observations Back To Sources

The v4.5 provenance graph is keyed by `label_flow_id`.

`security_profile.provenance_graph` contains:

- `label_flow_nodes`: compact view of every label flow.
- `propagation_edges`: parent-to-child label-flow transitions.
- `observation_links`: observation-to-label-flow links.
- `events.routing`: route decisions.
- `events.filtering`: source introduction, field slicing, redaction, derivation, aggregation, pseudonymization, storage read, and unknown-flow events.
- `events.merge`: explicit `merge_join`, `aggregate`, and `storage_merge` events.
- `events.truncation`: scale-limit events.

To trace an observation back to sources:

1. Start with `observations[].label_flow_ids[]`.
2. Find the matching entry in `security_profile.label_flows[]` or `provenance_graph.label_flow_nodes[]`.
3. Read its `label`, `node_path`, `edge_path`, `origin_node`, `introduced_at`, `trigger_context`, `route_history`, `filter_events`, `storage_key`, and `confidence`.
4. Follow `parent_label_flow_ids` or `provenance_graph.propagation_edges` backward until source-introduction flows are reached.
5. Use filtering, routing, and merge events to explain why the label was kept, dropped, derived, routed, or bridged through storage.

This is a source-recovery explanation graph, not a compressed path list. Different labels, branches, trigger contexts, and storage bridges stay visible.

## Output Files

When `--output results/skill-fcg.json` is used, the analyzer writes:

```text
results/skill-fcg.json
results/skill-fcg.flow.md
results/skill-fcg.flow.mmd
```

Main JSON fields:

- `meta`: skill name, version, analyzer metadata.
- `nodes`: FCG nodes.
- `edges`: FCG edges.
- `documentation_context`: review-only documentation context and source-selection policy.
- `source_sink`: legacy/debug field; new consumers should use `security_profile`.
- `paths`: sampled/debug graph paths and compression metadata.
- `statistics`: graph-level counts.
- `risks`: legacy path-risk output.
- `security_profile`: v4.5 single-label security transfer profile with step-level document flow, English compound-action splitting, and implicit object reads.

For batch feasibility, `security_profile.label_flows` is a bounded expansion. When the transfer limit is reached, `security_profile.statistics.truncated` and `truncation_events` identify that the graph was capped rather than exhaustively enumerated. Transfer expansion prioritizes edges that reach observation boundaries before ordinary intermediate propagation. Default transfer limits are analysis-grade (`maxLabelFlows=5000`, `maxEvents=30000`, `maxDepth=12`, `maxBranchesPerNode=48`) and can be tuned with `FCG_SECURITY_MAX_LABEL_FLOWS`, `FCG_SECURITY_MAX_EVENTS`, `FCG_SECURITY_MAX_DEPTH`, `FCG_SECURITY_MAX_BRANCHES_PER_NODE`, `FCG_SECURITY_MAX_MERGE_PARENTS`, `FCG_SECURITY_MAX_RELATED_FLOWS`, and `FCG_SECURITY_MAX_MERGE_GROUPS_PER_FLOW`.
`full` mode caps some large intermediate expansions, but Markdown document semantic extraction is not hard-capped by default. Set `FCG_MAX_DOC_FLOW_NODES` to a positive value only when you need an explicit safety limit; `0` or an unset value means unlimited. Set `FCG_MAX_CALLSITE_MEDIATION_NODES` or `FCG_DEPENDENCY_MAX_CANDIDATES` to adjust other internal breadth. Set `FCG_SEMANTIC_GATE_BATCH_SIZE`, `FCG_SEMANTIC_GATE_CONCURRENCY`, `FCG_SEMANTIC_GATE_MAX_BATCH_CHARS`, or `FCG_SEMANTIC_GATE_CACHE` to tune Markdown gate throughput and reuse.

Doc/tool/rule nodes may include `source_context`; document-derived edges may include `source_context` or `edge_evidence`.

The Markdown report includes:

- Mermaid graph.
- FCG statistics.
- path/debug summaries.
- formal Markdown semantics.
- security transfer analysis summary.
- observations table.
- bounded JSON previews for nodes, edges, paths, risks, and the security profile. The `.json` file remains the complete machine-readable output.

## ClawHub Helper Script

The older helper remains available for URL lists:

```text
node scripts/analyze-clawhub.js --url <skill_url> [--url <skill_url> ...] [--results <dir>] [--llm-timeout <ms>] [--skip-existing]
node scripts/analyze-clawhub.js --list <urls.txt> [--results <dir>] [--llm-timeout <ms>] [--skip-existing]
```

For the current full pipeline, prefer the root pipeline command or `scripts/fcg-batch.js` over this legacy helper.

## Testing

```powershell
cd D:\projects\SkillFlow\packages\skill-fcg-analyzer
npm test
```

Root pipeline tests:

```powershell
cd D:\projects\SkillFlow
node --test "test/**/*.test.js"
```

## Notes For Downstream DOE Work

- FCG edges are may-flow candidates, not final proof of unnecessary data exposure.
- `security_profile.observations` is the best starting point for DOE evidence because it states which sink-like nodes observed which `label_flow_ids`.
- Resolve `label_flow_ids` through `security_profile.label_flows[]`, then use `provenance_graph` to explain source chains, filters, routes, merges, and storage bridges.
- Use `node_profiles` to reason about source/sink semantics and trust boundaries.
- DOE should normally assess each observed `label_flow` independently; merge and storage relationships are explanation fields, not deduplication rules.

## Project Structure

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




