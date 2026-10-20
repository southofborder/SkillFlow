# SkillFlow

Cross-computer development: start with the
[research handoff](docs/cloud-research-handoff.md) and
[offline cloud setup](tools/cloud/README.md). Environment setup does not
authorize model experiments; the formal long comparison has not started.

SkillFlow develops task-related static data minimization analysis for Agent Skills.
**SkillFlow** implements graph construction, controlled source comparison, bounded
CFG feedback, joint security and transfer annotation, focused review with one
annotation repair, and deterministic data propagation.

A source-only Task extraction now establishes the preservation baseline before
receiving a CFG, annotation, payload or DOE result. The grounded annotation
references that exact sealed Task revision and declares realizations, positive
demands, expressions, processing and sensitivity. A full-source review must
account for every source range, Task requirement, demand seed and actual IR.
[The recorded pipeline](docs/doe/joint-pipeline.md) supports one semantic repair
round: annotation-only repair keeps Task immutable; Task errors use an isolated
source-only revision followed by a fresh complete annotation and review.

The normal path has three semantic calls, annotation repair five, and Task
revision plus rebuilding six. Structural correction is recorded separately.
The deterministic backend traces each seed to its derivations and every sink.
Unexpressed constraints remain visible limitations; they are not executable
checks or proof of necessity. Propagation facts and historical runs remain
immutable. Engineering tests and real-model error-detection experiments are
reported separately; neither parsing nor review acceptance proves completeness.
Conservative retention is not indispensability; supported local reductions do
not establish global minimality. The [sink preparation guide](docs/doe/SkillFlow-DOE离线切片与审查材料.md)
describes the retained internal read-only association algorithm.
The legacy SFG/FCG engine, DOE scorer, and their pipeline were removed on 2026-09-15.
There is no compatibility entry point.

The [field-tightening guide](docs/architecture/field-tightening.md) documents the single `ir_semantics` contract, shared evidence extraction, compact model requests and derivation-backed DOE result rows. Audit identities, data versions and all preservation demands remain available. This is an offline engineering change; historical model results are not migrated.

[中文说明](README-CH.md) · [Representation guidance and one repair](docs/propagation/SkillFlow-表示契约与一次标注修复.md) · [Documentation](docs/README.md)

The [architecture and migration acceptance guide](docs/architecture/SkillFlow-架构与迁移验收.md) explains the current layout and historical identity boundaries. The [migration review page](experiments/migrations/layout-v1-20261002-215752/index.html) links the three unchanged DOE files and new-layout offline acceptance. The migration-time full regression passed: 2509 tests, with no failures, errors, or skips; see the [test receipt](experiments/migrations/layout-v1-20261002-215752/verification/python-tests.json).

## Current workflow

```text
Skill directory / ZIP
  → model-assisted extraction and deterministic CFG compilation
  → structural and reference validation
  → Lean-generated controlled retelling with actual-text roundtrip checks
  → one model comparison of complete source and controlled text
  → bounded CFG feedback for explicit differences
  → independent source-only Task extraction and sealed baseline
  → Task realizations, demands, processing, and sensitivity
  → compiled observations and sink boundaries
  → source / requirement / seed / IR review
  → one repair round; isolated Task revision and rebuilding when needed
  → deterministic propagation: data.json / records.json / sinks.json
  → evidenced Task goals, backward information demands, and sink comparisons
  → sensitivity tracking and deterministic sink-specific DOE comparisons
```

Structural acceptance does not prove source coverage or execution safety.
Retelling proofs preserve explicit graph records; they do not prove extraction,
model judgments, or execution semantics. CFG feedback performs full re-extraction;
annotation repair creates a new candidate without rewriting frozen graphs or history.

## Start

Use Python 3.10 or newer. From the repository root:

```powershell
python -m pip install -e . pytest
python -m skillflow --help
python -m skillflow.graph.audit --help
python -m skillflow.graph.feedback --help
python -m skillflow.propagation.annotation --help
python -m skillflow.propagation.review --help
python -m skillflow.propagation --help
python -m skillflow.doe --help
python -m skillflow pipeline --help
python -m skillflow analyze --input examples/graph/simple_skill --output tmp/analysis.json
python -m skillflow render --input tmp/analysis.json --output tmp/graph.mmd
```

`analyze` calls the configured model unless `--candidate` supplies an offline
candidate; `render` is offline. Supply local credentials using the
[.env.example](.env.example) template. The project configuration uses the official
DeepSeek endpoint and requests `deepseek-v4-flash`; actual response model names
are recorded separately. See the [package guide](docs/architecture/implementation.md).

The independent controlled-retelling experiment requires the pinned Lean printer:

```powershell
# In formal, using the pinned Lean toolchain:
lake build
lake env lean ProofAudit.lean
# From the repository root; prepare is offline:
python -m skillflow.graph.audit prepare --run-dir tmp/backtrace-review
```

`run` performs five model comparisons for F01 and its four controlled variants;
`replay` parses saved current-version responses offline. The early
[F01 acceptance report](experiments/graph/audit/runs/controlled-v2-f01-20260914T142804Z/acceptance.md)
remains a historical record. A preserved experiment reviews seven annotation candidates
with at most one repair each and audits the existing 001, 010, and 013 CFGs once;
see the [assistant assessment](experiments/propagation/review/runs/repair-once-v1-20260929-132248/assistant-review.md).
Earlier 30-case results retain their own protocol identities and are not automatically
accepted under the latest workflow.

## Layout and verification

Task v3 contains source-only requirements and complete physical-line accounting.
Graph bindings belong to realizations, and compiled goals preserve per-seed
provenance. Instructions are English; explanations and reports are Chinese.
See [Task evidence and isolation](docs/doe/task-evidence.md).

```shell
python -m skillflow pipeline prepare --input path/to/skill --analysis path/to/analysis.json --run-dir new-run
python -m examples.doe.joint_analysis_demo --show annotation
```

| Path | Purpose |
| --- | --- |
| `src/skillflow/` | graph, propagation, deterministic DOE analysis, and common responsibilities |
| `formal/`, `tests/`, `tools/` | Proofs, regression tests, and repository experiment tools |
| `dataset/skills/` | 30 frozen evaluation input ZIPs |
| `result/ir-IPP/` | 30 matching CFG PNGs; model outputs, not ground truth |
| `result/suggestions/`, `result/advice_for_doe/` | Existing per-sample and condensed reviews; these historical files are not current deterministic DOE outputs |
| `packages/skill-similarity-analyzer/` | Independent ClawHub downloading and grouping utility, outside the semantic audit workflow |
| `shared/`, `test/` | JavaScript support and tests used by that utility |
| `docs/`, `experiments/legacy_sfg_doe/` | Current specifications and preserved historical records |

Frozen sources, external annotations, and raw model calls remain in `experiments/`.
Current PDF tools live in `tools/corpus/`. Annotations are not included in Skill inputs.

These checks do not call a remote model or execute Skill contents:

```powershell
python -B -X utf8 -m pytest tests -q -p no:cacheprovider
python -B -X utf8 -m tools.graph.baseline.export_review_set --check
node --test "test/*.test.js" "packages/skill-similarity-analyzer/test/*.test.js"
```

See [document navigation](docs/README.md), [formal verification](formal/README.md),
and [controlled-text guarantees](formal/CONTROLLED_RETELLING.md).
Old pipeline documentation is [historical material](docs/history/legacy-sfg-doe/README.md).

Installed production commands can run from another working directory. Repository experiment tools run from the project root with `python -m tools.<area>.<module>`; they are not installed as production APIs. Historical bytes and exact old-address mappings are verified through `experiments/migrations/` ledgers. No `skill_ir` compatibility module is supplied.
