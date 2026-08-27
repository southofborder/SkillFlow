# SkillFlow

Static-analysis pipeline for **Data Over-Exposure (DOE)** in Agent Skills (downloadable skill packages on ClawHub).

The core question: when a skill performs the task it claims to perform, does it send **sensitive data beyond what the task actually needs** across a trust boundary (external LLM, external service, persistent storage)? Necessary exposure is not a finding; only unnecessary exposure is — this is what distinguishes SkillFlow from ordinary taint analysis.

> **Naming note**: the graph brand layer was renamed (FCG→**SFG**), but the runtime **keeps** the internal selectors and directories to avoid breaking contracts — the `--phase fcg`/`--phase doe` selectors, output dirs `fcg/`/`doe/`, and the join-contract CLI (`--fcg`/`--fcg-root`) are unchanged; on the SFG side the per-skill file suffix is `-sfg.json` and the env-var prefix `SFG_*`, while the DOE side keeps its original `-doe.json` suffix and `DOE_*` prefix. Package layout: SFG is now **Python** (`packages/skill-sfg`, run via `python -m skill_sfg.batch`); DOE stays **JS** (`packages/skill-doe-analyzer`).
>
> Chinese version: [`README-CH.md`](README-CH.md).

## Pipeline at a glance

```text
ClawHub top-k  ──▶  1. Download  ──▶  2. SFG flow graph  ──▶  3. DOE exposure scoring
   (by downloads)      zips/            fcg/skills/*-sfg.json   doe/skills/*-doe.json
```

- **Download** — fetch the top-k ClawHub skill zips (`packages/skill-similarity-analyzer`, reused).
- **SFG (Skill Flow Graph)** — parse each skill into a directed flow graph and overlay a `security_profile` (labels, label flows, boundary observations). Extraction classifies each file and content block (code/table/list/prose/disclaimer) and dispatches a matching strategy, rule-first with LLM only for ambiguity. Edge connection balances recall (exhaustive type-compatible candidates) against precision (condition/guard routing). The sole input to DOE. See `packages/skill-sfg` (Python).
- **DOE (Data Over-Exposure)** — for each `(observation × label_flow)` assessment unit, score `exposure × (1 - necessity)` with a two-layer rule + LLM design. See `packages/skill-doe-analyzer` (JS).

Optional similarity grouping (`packages/skill-similarity-analyzer`) is off by default.

## Quick start

Create a repo-root `.env` (SFG semantic gating and the DOE LLM judge run by default, so `LLM_API_KEY` is required):

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
| `packages/skill-sfg` (Python) | Build the skill flow graph + `security_profile` (stage 2, sole DOE input) |
| `packages/skill-doe-analyzer` (JS) | Score data over-exposure per assessment unit (stage 3, the project core) |
| `packages/skill-similarity-analyzer` (JS) | Download ClawHub zips; optional README/SKILL similarity grouping |

## Documentation

- [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) — full project overview: concepts, three-stage pipeline, the SFG↔DOE `security_profile` contract, DOE internals, robustness, cost. (Chinese: [`PROJECT-OVERVIEW-CH.md`](PROJECT-OVERVIEW-CH.md).)
- [`README-PIPELINE.md`](README-PIPELINE.md) — one-command pipeline reference: flags, phases, env vars, evidence budgeting. (Chinese: [`README-PIPELINE-CH.md`](README-PIPELINE-CH.md).)
- `skillflow-pipeline.config.cjs` — advanced configuration.

## Tests

```powershell
# SFG is Python (135 pytest):
python -m pytest packages/skill-sfg/tests
# DOE + similarity stay JS (58 + 20):
node --test "packages/skill-doe-analyzer/test/**/*.test.js" "packages/skill-similarity-analyzer/test/**/*.test.js"
```

213 tests, all green (SFG 135 + DOE 58 + similarity 20). The repo-root `test/` folder holds only the pipeline/env transport tests; the core suites live under each package.
