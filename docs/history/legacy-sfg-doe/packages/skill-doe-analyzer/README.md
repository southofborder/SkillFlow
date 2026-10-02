# SkillFlow DOE Analyzer

Independent data over-exposure scorer for SkillFlow SFG JSON files.

The assessment unit is one observed label flow: `(observation_id, label_flow_id)`. The analyzer does not claim runtime-confirmed leakage; it produces review evidence for potential over-exposure.

> Naming: the graph engine is **SFG** (Skill Flow Graph) and this verdict engine is **DOE** (Data Over-Exposure). Internal identifiers keep their historical `fcg`/`doe` spelling by design — join-contract flags `--fcg`/`--fcg-root`/`--doe-root`, output dirs `fcg/`/`doe/`, summary files `doe-summary.*`, LLM cache `doe-llm-cache.jsonl`, batch script `doe-batch.js`, and the emitted `doe_score`/`potential_doe` fields are unchanged. Per-skill graph inputs carry the `-sfg.json` suffix and per-skill verdict outputs the `-doe.json` suffix.

## Usage

Single SFG file:

```powershell
cd packages\skill-doe-analyzer
node src\index.js analyze --fcg D:\path\skill-sfg.json --out D:\path\skill-doe.json --pretty --llm-cache D:\path\doe-llm-cache.jsonl
```

Batch over SFG pipeline output:

```powershell
node scripts\doe-batch.js --root D:\projects\SkillFlow\results\clawhub-top-k100
```

Naturalize potential over-exposure paths for audit:

```powershell
node scripts\doe-path-report.js --root D:\projects\SkillFlow\results\clawhub-top-k100 --skill skill_0001
```

By default, DOE uses the LLM necessity judge and requires `LLM_API_KEY`. Use `--no-llm-judge` only for explicit offline rule-only scoring.

For OpenAI-compatible endpoints that reset larger HTTP/1.1 requests or have unstable DNS, set `LLM_HTTP2=1` and optionally `LLM_ENDPOINT_RESOLVED_IP=<ip>` to force HTTP/2 and pin DNS while keeping the original endpoint host for TLS/SNI.

## CLI

Single-file options:

- `--fcg <file>`: required input SFG JSON (flag name kept as the SFG↔DOE join contract).
- `--out <file>`: optional output path. If omitted, JSON is printed to stdout.
- `--group-baseline <file>`: optional group behavior baseline JSON.
- `--threshold <n>`: high-score threshold, default `0.70`.
- `--pretty`: pretty-print JSON.
- `--no-llm-judge`: disable the default LLM necessity judge.
- `--llm-cache <file>`: JSONL cache for LLM judge results.
- `--llm-batch-size <n>`: assessment units per LLM request, default `4`.
- `--llm-votes <n>`: first-pass LLM votes per assessment unit, default `1`.
- `--llm-concurrency <n>`: concurrent LLM judge requests, default `2`.
- `--llm-escalation-votes <n>`: votes for escalated high-risk or uncertain units, default `3`.
- `--llm-escalation-policy <mode>`: `risk_or_uncertain`, `none`, or `all`; default `risk_or_uncertain`.
- `--llm-max-batch-chars <n>`: approximate max characters per LLM batch, default `60000`.
- `--llm-model <name>`, `--llm-endpoint <url>`, `--llm-timeout <ms>`: override environment defaults.

Batch options:

- `--root <dir>`: run root containing `fcg/skills`.
- `--fcg-root <dir>`: defaults to `<root>/fcg`.
- `--output <dir>`: defaults to `<root>/doe`.
- `--concurrency <n>`: default `2`.
- `--threshold <n>`, `--llm-cache <file>`, `--llm-batch-size <n>`, `--llm-votes <n>`, `--llm-concurrency <n>`, `--llm-escalation-votes <n>`, `--llm-escalation-policy <mode>`, `--llm-max-batch-chars <n>`, `--refresh`.
- `--no-llm-judge`: explicit rule-only batch mode.

Path report options:

- `--root <dir>`: run root containing `fcg/`, `doe/`, and `zips/`.
- `--fcg-root <dir>`, `--doe-root <dir>`, `--zips-root <dir>`: override default input roots.
- `--output <path>`: output directory or `.md` / `.json` file path. Default `<root>/doe/reports`.
- `--skill <text>`: filter by skill id, skill name, or output filename fragment.
- `--scope potential|boundary|all`: default `potential`, meaning `potential_doe || requires_review`.
- `--format md|json|both`: default `both`.

## Method

Potential over-exposure is reported only for boundary-crossing observations. Boundaries come from `observation.boundary` and include information visibility changes such as external network receivers, model providers, persistent retention, and user-visible surfaces. `command_execution` and `destructive_operation` are not exposure boundaries by role alone.

```text
component_score = 0.7 * llm_component_score + 0.3 * rule_component_score
necessity_score = min(action_input_need, receiver_semantic_need, task_need)
doe_score = clamp(exposure_score * (1 - necessity_score) + baseline_adjustment, 0, 1)
potential_doe = boundary_crossed && necessity_score < necessity_threshold   // default threshold 0.70
```

Necessity is a three-component minimum. `action_input_need` reflects whether the label actually participates in the sink action's input (transform participation `sinkTransformedLabel`, schema membership `schemaInputMembership`); `receiver_semantic_need` scores receiver×category compatibility against `RECEIVER_CATEGORY_COMPAT`; `task_need = min(flow_path_signal, boundary_node_signal)` folds the former separate flow-path and boundary-node task signals into one component, backed by declaration coverage (`pathDeclarationCoverage`). Exposure and necessity are orthogonal axes: feeding the LLM never lowers exposure, and a flow is only flagged when it is both exposed **and** unnecessary.

The evidence pack is flow-centric (v7): the unit is one label's full source→sink flow. Each pack carries `label` (semantic descriptor, no internal ids), `sink_boundary` (with an exposure tier), and `flow[]` — an ordered list of nodes `{node_name, role, action, transform?}` where sink nodes add `sink_surface`. Packs also carry `task_memory_evidence_ids`, and optional `leak_type` / `leak_severity` / `cycle_handling`. Global necessity is judged over the whole flow, not just the label name.

Context-only documentation nodes such as `doc_definition`, `doc_schema`, and `doc_example` may support task semantics but are not treated as label-flow path nodes. LLM payloads compact the repeated task/ontology prefix into a `shared_context` block that stays byte-identical across a batch so the OpenAI-compatible endpoint's prompt cache is hit on every unit after the first.

## Output

The analyzer emits `version: "0.3"` with:

- `boundary_crossed`, `boundary_basis`, `exposure_score`, `necessity_score`, `potential_doe`, `doe_score`.
- `local_necessity` and `global_necessity` component objects.
- `rule_component_scores`, `component_scores`, and `llm_necessity_score`.
- `llm_judge`: model, prompt version, vote count, component evidence refs, short reasoning, and disagreement.
- `statistics`: assessment counts, boundary crossings, potential over-exposure count, review count, LLM first-pass count, escalated count, timeout split count, cache hits, warning count, and `llm_token_usage` with a prompt-cache `cache_hit_ratio`.

Batch output layout (internal `doe/` dir name and `doe-*` filenames kept; only per-skill outputs use the `-doe.json` suffix):

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

The path report is a read-only audit aid. It reconstructs natural-language paths from DOE assessments, prefers exact source lines from the original zip, falls back to SFG `source_context`, and adds audit notes such as `template_or_example_source`, `path_label_metadata_only`, and `model_context_expected_flow`. `label_subtype=path` means a file path, file name, or path-like string; it is not the graph path.
