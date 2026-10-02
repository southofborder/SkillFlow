# SkillFlow

SkillFlow develops task-related static data minimization analysis for Agent Skills.
**Skill-IR** implements graph construction, controlled source comparison, bounded
CFG feedback, joint security and transfer annotation, focused review with one
annotation repair, and deterministic data propagation.

**Sensitivity, task necessity, and Data Over-Exposure (DOE) judgment are the next
stage.** Propagation exports factual `doe-input.json` files without DOE conclusions.
The legacy SFG/FCG engine, DOE scorer, and their pipeline were removed on 2026-09-15.
There is no compatibility entry point.

[中文说明](README-CH.md) · [Representation contract and one repair](docs/SkillFlow-表示契约与一次标注修复.md) · [Documentation](docs/README.md)

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
python -m pip install -e packages/skill-ir pytest
python -m skill_ir --help
python -m skill_ir.backtrace --help
python -m skill_ir.feedback --help
python -m skill_ir.security_profile --help
python -m skill_ir.annotation_review --help
python -m skill_ir.propagation --help
python -m skill_ir analyze --input examples/simple_skill --output tmp/analysis.json
python -m skill_ir render --input tmp/analysis.json --output tmp/graph.mmd
```

`analyze` calls the configured model unless `--candidate` supplies an offline
candidate; `render` is offline. Supply local credentials using the
[.env.example](.env.example) template. The project configuration uses the official
DeepSeek endpoint and requests `deepseek-v4-flash`; actual response model names
are recorded separately. See the [package guide](packages/skill-ir/README.md).

The independent controlled-retelling experiment requires the pinned Lean printer:

```powershell
# In packages/skill-ir/formal, using the pinned Lean toolchain:
lake build
lake env lean ProofAudit.lean
# From the repository root; prepare is offline:
python -m skill_ir.backtrace prepare --run-dir tmp/backtrace-review
```

`run` performs five model comparisons for F01 and its four controlled variants;
`replay` parses saved current-version responses offline. The early
[F01 acceptance report](packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v2-f01-20260914T142804Z/acceptance.md)
remains a historical record. The latest experiment reviews seven annotation candidates
with at most one repair each and audits the existing 001, 010, and 013 CFGs once;
see the [assistant assessment](packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/assistant-review.md).
Earlier 30-case results retain their own protocol identities and are not automatically
accepted under the latest workflow.

## Layout and verification

| Path | Purpose |
| --- | --- |
| `packages/skill-ir/` | Current implementation, proofs, tests, and experiment tools |
| `dataset/skills/` | 30 frozen evaluation input ZIPs |
| `result/ir-IPP/` | 30 matching CFG PNGs; model outputs, not ground truth |
| `result/suggestions/`, `result/advice_for_doe/` | Existing per-sample and condensed reviews; the latter's historical name does not mean a DOE analyzer is implemented |
| `packages/skill-similarity-analyzer/` | Independent ClawHub downloading and grouping utility, outside the semantic audit workflow |
| `shared/`, `test/` | JavaScript support and tests used by that utility |
| `docs/`, `experiments/legacy_sfg_doe/` | Current specifications and preserved historical records |

Frozen sources, external annotations, raw model calls, and PDF generators remain
in the Skill-IR experiments. Annotations are not included in Skill inputs.

These checks do not call a remote model or execute Skill contents:

```powershell
python -B -X utf8 -m pytest packages/skill-ir/tests -q -p no:cacheprovider
python -B -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/export_review_set.py --check
node --test "test/*.test.js" "packages/skill-similarity-analyzer/test/*.test.js"
```

See [document navigation](docs/README.md), [formal verification](packages/skill-ir/formal/README.md),
and [controlled-text guarantees](packages/skill-ir/formal/CONTROLLED_RETELLING.md).
Old pipeline documentation is [historical material](docs/history/legacy-sfg-doe/README.md).
