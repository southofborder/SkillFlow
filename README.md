# SkillFlow

Static-analysis pipeline for **Data Over-Exposure (DOE)** in Agent Skills (downloadable skill packages on ClawHub).

The core question: when a skill performs the task it claims to perform, does it send **sensitive data beyond what the task actually needs** across a trust boundary (external LLM, external service, persistent storage)? Necessary exposure is not DOE; only unnecessary exposure is — this is what distinguishes SkillFlow from ordinary taint analysis.

> Chinese version: [`README-CH.md`](README-CH.md).

## Pipeline at a glance

```text
ClawHub top-k  ──▶  1. Download  ──▶  2. FCG flow graph  ──▶  3. DOE exposure scoring
   (by downloads)      zips/            fcg/skills/*.json       doe/skills/*.json
```

- **Download** — fetch the top-k ClawHub skill zips (`packages/skill-similarity-analyzer`, reused).
- **FCG (Flow-Control Graph)** — parse each skill into a directed flow graph and overlay a `security_profile` (labels, label flows, boundary observations). Extraction classifies each file and content block (code/table/list/prose/disclaimer) and dispatches a matching strategy, rule-first with LLM only for ambiguity. Edge connection balances recall (exhaustive type-compatible candidates) against precision (condition/guard routing). The sole input to DOE. See `packages/skill-fcg-analyzer`.
- **DOE (Data Over-Exposure)** — for each `(observation × label_flow)` assessment unit, score `exposure × (1 - necessity)` with a two-layer rule + LLM design. See `packages/skill-doe-analyzer`.

Optional similarity grouping (`packages/skill-similarity-analyzer`) is off by default.

## Quick start

Create a repo-root `.env` (FCG semantic gating and the DOE LLM judge run by default, so `LLM_API_KEY` is required):

```dotenv
LLM_API_KEY=<your-key>
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=30000
```

Then run the full pipeline:

```powershell
node scripts\skillflow-pipeline.js --k 100
```

Or a single stage:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase fcg
node scripts\skillflow-pipeline.js --k 100 --phase doe
```

Dry run (prints resolved commands, no LLM key needed):

```powershell
node scripts\skillflow-pipeline.js --k 100 --dry-run
```

## Packages

| Package | Role |
| --- | --- |
| `packages/skill-fcg-analyzer` | Build the flow-control graph + `security_profile` (stage 2, sole DOE input) |
| `packages/skill-doe-analyzer` | Score data over-exposure per assessment unit (stage 3, the project core) |
| `packages/skill-similarity-analyzer` | Download ClawHub zips; optional README/SKILL similarity grouping |

## Documentation

- [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) — full project overview: concepts, three-stage pipeline, the FCG↔DOE `security_profile` contract, DOE internals, robustness, cost. (Chinese: [`PROJECT-OVERVIEW-CH.md`](PROJECT-OVERVIEW-CH.md).)
- [`README-PIPELINE.md`](README-PIPELINE.md) — one-command pipeline reference: flags, phases, env vars, evidence budgeting. (Chinese: [`README-PIPELINE-CH.md`](README-PIPELINE-CH.md).)
- `skillflow-pipeline.config.cjs` — advanced configuration.

## Tests

```powershell
node --test "packages/*/test/**/*.test.js"
```

239 tests, all green. (The root `test/` folder holds only the pipeline/env transport tests; the core suite lives under `packages/*/test`.)
