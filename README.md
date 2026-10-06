# SkillFlow

SkillFlow develops task-related static data minimization analysis for Agent Skills.
**Skill-IR** implements graph construction, controlled source comparison, bounded
CFG feedback, joint security and transfer annotation, focused review with one
annotation repair, and deterministic data propagation.

**Sensitivity, task necessity, and Data Over-Exposure (DOE) judgment are the next
stage.** Propagation exports factual `doe-input.json` files without DOE conclusions.
The legacy SFG/FCG engine, DOE scorer, and their pipeline were removed on 2026-09-15.
There is no compatibility entry point.

[中文说明](README-CH.md) · [Representation contract and one repair](docs/propagation/SkillFlow-表示契约与一次标注修复.md) · [Documentation](docs/README.md)

The [architecture and migration acceptance guide](docs/architecture/SkillFlow-架构与迁移验收.md) explains the current layout and historical identity boundaries. The [migration review page](experiments/migrations/layout-v1-20261002-215752/index.html) links the three unchanged DOE files and new-layout offline acceptance. Final full regression passed: 2509 tests, with no failures, errors, or skips; see the [test receipt](experiments/migrations/layout-v1-20261002-215752/verification/python-tests.json).

## Current workflow

```text
Skill directory / ZIP
  → model-assisted extraction and deterministic CFG compilation
  → structural and reference validation
  → Lean-generated controlled retelling with actual-text roundtrip checks
  → one model comparison of complete source and controlled text
  → bounded CFG feedback for explicit differences
  → joint security and transfer annotation, with compiled observations
  → focused review; one full annotation repair and fresh review when needed
  → deterministic propagation and doe-input.json
  → DOE judgment (next stage)
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

| Path | Purpose |
| --- | --- |
| `src/skillflow/` | graph, propagation, and common responsibilities |
| `formal/`, `tests/`, `tools/` | Proofs, regression tests, and repository experiment tools |
| `dataset/skills/` | 30 frozen evaluation input ZIPs |
| `result/ir-IPP/` | 30 matching CFG PNGs; model outputs, not ground truth |
| `result/suggestions/`, `result/advice_for_doe/` | Existing per-sample and condensed reviews; the latter's historical name does not mean a DOE analyzer is implemented |
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
