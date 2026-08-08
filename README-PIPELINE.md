# SkillFlow One-Command Pipeline

Run the current SkillFlow pipeline from the repository root.

Default `all` flow:

1. List and download the top `k` ClawHub skill zip packages.
2. Run FCG analysis on the downloaded zips.
3. Run DOE analysis on the generated FCG JSON files.

Similarity grouping is optional and runs only when `--with-similarity` or `--phase download-group` is used.

## Quick Start

Create repo-root `.env` first. FCG Markdown semantic gating and DOE LLM judge run by default, so normal `all` runs require `LLM_API_KEY`.

```dotenv
LLM_API_KEY=<your-key>
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=30000
```

Then run:

```powershell
cd D:\projects\SkillFlow
node scripts\skillflow-pipeline.js --k 100
```

PowerShell wrapper:

```powershell
.\run-skillflow-pipeline.ps1 -K 100
```

Dry run prints resolved commands without requiring an LLM key:

```powershell
node scripts\skillflow-pipeline.js --k 100 --dry-run
```

## Output

The configured root prefix is:

```text
D:\projects\SkillFlow\results\clawhub-top
```

The actual output directory includes `k`:

```text
D:\projects\SkillFlow\results\clawhub-top-k100
```

Main outputs:

```text
<root>\zips\
<root>\fcg\skills\
<root>\fcg\fcg-summary.json
<root>\fcg\fcg-summary.md
<root>\doe\skills\
<root>\doe\doe-summary.json
<root>\doe\doe-summary.md
```

## Configuration

Advanced parameters live in:

```text
skillflow-pipeline.config.cjs
```

Common CLI options:

- `--root <dir>`: output root prefix or explicit `-k` root.
- `--phase download|fcg|doe|all|download-group`: run one part of the pipeline. Default `all` means download, FCG, then DOE.
- `--with-similarity`: run similarity grouping during the download phase. `download-group` is a compatibility phase alias.
- `--semantic-llm`: enable semantic LLM for similarity grouping only.
- `--dry-run`: print resolved config and child commands only.

FCG extraction first classifies each file (instruction docs vs non-instruction docs like changelog/license) and each content block (code/table/list/prose/disclaimer), then dispatches a matching rule-based strategy — shell code blocks emit a sink per command via the shared `shell-command-classifier`, script calls are role-classified (builtins dropped, unknown user functions kept), negations/disclaimers demote to guard/context, and lists are segmented into blocks (multi-line bullets folded, disclaimer lead-in scope inherited). Sequence edges between doc steps are same-section by default; set `FCG_SEQUENCE_EDGE_SCOPE=global` to restore legacy whole-document linking. On top of that, Markdown semantic extraction is LLM-gated by default: rules only produce candidates, and missing `LLM_API_KEY` fails FCG/pipeline preflight. The gate aims to review all document candidates; `FCG_MAX_DOC_FLOW_NODES` is unlimited by default and only acts as an explicit safety cap when set to a positive value. Tune throughput and reuse with `FCG_SEMANTIC_GATE_BATCH_SIZE`, `FCG_SEMANTIC_GATE_CONCURRENCY`, `FCG_SEMANTIC_GATE_MAX_BATCH_CHARS`, and `FCG_SEMANTIC_GATE_CACHE`.

The semantic-gate cache now persists with the run at `<root>/fcg/semantic-gate-cache.jsonl` (instead of a global temp file), so re-runs and other machines/CI reuse prior semantic decisions and skip the remote model for unchanged documents. Set `fcg.semanticGateCache` (or `--semantic-gate-cache`) to override the path, or `0`/`false` to disable. Semantic extraction itself is unchanged — a cache hit returns the exact decision the model produced for that node, so extraction quality is identical; only latency drops.

DOE LLM judge is enabled by default and requires `LLM_API_KEY` unless disabled in config or the DOE batch command. The default DOE strategy is one LLM first-pass judgement for every boundary assessment, then 3-vote median review only for high-risk or uncertain units. Tune it with `doe.llmConcurrency`, `doe.llmEscalationVotes`, `doe.llmEscalationPolicy`, and `doe.llmMaxBatchChars` in `skillflow-pipeline.config.cjs`.

To prevent context-overflow timeouts on skills with large evidence, DOE applies tiered, accuracy-preserving sizing to each evidence pack:

- Packs within `doe.evidenceMaxPackChars` (default 100000) are sent with full evidence — byte-identical to no sizing, so verdicts are unchanged.
- Large-but-sendable packs get a size-scaled request timeout (bounded by `doe.adaptiveTimeoutMaxMs`, default 4× base) so they complete with full fidelity rather than being trimmed.
- Only packs that still exceed the ceiling — which would otherwise overflow context, time out, and drop the whole skill's DOE output — are reduced: lossless cleanup first, then head/tail windowing of interior flow-path nodes (`doe.evidencePathNodeWindow`, default 4) while always keeping the boundary node and path endpoints, then text/array caps (`doe.evidenceMaxTextChars`, `doe.evidenceMaxArrayItems`). Such units are flagged `requires_review` and counted in `llm_fallback_count`. This only ever affects packs that are a total loss today, so accuracy never drops relative to current behavior.

If an LLM call still fails after budgeting and retries (e.g. a persistent timeout), that single unit degrades to rule-only scoring with `requires_review=true` instead of crashing the skill — see `statistics.llm_fallback_count` / `llm_fallback_units`.

Transient transport failures (request timeout, network reset/DNS, HTTP 429, HTTP 5xx) are retried with bounded exponential backoff + jitter, honoring `Retry-After`. Auth/4xx (except 429) and schema errors are not retried and fail fast. Tune with `LLM_MAX_RETRIES` (default 2), `LLM_RETRY_BASE_MS` (default 500), `LLM_RETRY_MAX_BACKOFF_MS` (default 8000).

If your OpenAI-compatible endpoint has unstable DNS or resets larger HTTP/1.1 requests, set `LLM_HTTP2=1` and, when needed, `LLM_ENDPOINT_RESOLVED_IP=<ip>` before running DOE or the full pipeline.

## Examples

Download zip packages only:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase download
```

Download, group by similarity, and stop before FCG:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase download-group
```

Run FCG on existing `<root>\zips` or similarity output:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase fcg
```

Run DOE on existing `<root>\fcg\skills`:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase doe
```

Run full pipeline with optional similarity grouping:

```powershell
node scripts\skillflow-pipeline.js --k 100 --with-similarity
```

Run direct FCG batch:

```powershell
node packages\skill-fcg-analyzer\scripts\fcg-batch.js --root results\clawhub-top-k100
```

Run direct DOE batch:

```powershell
node packages\skill-doe-analyzer\scripts\doe-batch.js --root results\clawhub-top-k100
```

## Test

```powershell
node --test "packages/*/test/**/*.test.js"
```

This runs the full 239-test suite (the project core). The repo-root `test/` folder holds only the pipeline/env transport tests:

```powershell
node --test "test/**/*.test.js"
```
