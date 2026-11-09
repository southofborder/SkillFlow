# Current SkillFlow version

Documentation updated 2026-11-09; implementation and latest closed validation:
**interface-r4, 2026-11-04**. This page identifies the current repository workflow.
Earlier README sections and experiment reports retain their original protocol
identities and do not supersede this status.

SkillFlow analyzes task-related static data minimization for Agent Skills. Its
scope includes unnecessary actions and unnecessary sensitive payloads in necessary
actions. Sensitive data reaching a sink does not by itself establish Data
Over-Exposure (DOE). See the [goal and design principles](doe/SkillFlow-DOE目标与设计原则.md).

## Implementation and workflow

The current working tree is `D:/projects/SkillFlow`, on `main`. The separately
registered `D:/projects/SkillFlow-staged` / `codex/staged-analysis` worktree is
historical staged work; it is not the current implementation or an integration
source for this documentation update. Source code lives under `src/skillflow/`;
the repository analysis entry is `tools.doe.document_guided_pilot`.

The [document-guided entry](doe/document-guided-analysis.md) uses seven normal
semantic requests with two dependency-aware workers:

| Stage | Responsibility and input boundary |
| --- | --- |
| Task | Read only the complete frozen Skill; seal its declared purposes, requirements, and issues. No external task, CFG, payload, sensitivity, or DOE input. |
| flow | Describe source-backed entry points, data flow, conditions, versions, and recipients. |
| CFG | Build one complete graph from source and flow; it does not wait for Task. |
| processing | Describe processing facts for the CFG from source and the runtime contract. |
| task correspondence | Map the sealed Task to demands and supported constraints using source, CFG, and processing. |
| sensitivity | Declare source-supported sensitivity from CFG and processing; it receives neither Task nor task correspondence. |
| source review | Review the complete source against the actual Task, CFG, and assembled annotation; report concrete findings. |

Before review, the program assembles processing, task-correspondence, and
sensitivity fragments and validates explicit references. This assembly makes no
model call. Deterministic propagation and DOE then use the selected materials.
One structural correction per stage and one shared semantic repair round remain
bounded; actual corrections, repair requests, and transport attempts are counted
separately from the seven normal requests. Review findings follow their actual
object owner and dependency closure. Task revision remains isolated from free-text
review advice and downstream materials.

[Finite loop summaries](doe/general-loop-analysis.md) support explicit and common
nested loops, predecessor merges, and nested member demands. They retain member,
occurrence, candidate, receiver, and version relationships; they do not establish
exact arbitrary arrays, iteration counts, or path feasibility. Real local modeling
gaps remain explicit and can stop affected propagation while independent branches
continue.

The [sparse backend](propagation/backend-computation-contract.md) reuses accepted
materials, schedules actual dependency partitions, projects live locations, and
joins compatible relation rows without inventing cross-pairings. Projected
record snapshots do not mean omitted locations are empty or safe. Forward
constraint checks neither prune propagation facts nor create positive demand
seeds. No generic call-stack, exception executor, or persistent cache engine was
added.

[Interface-r4](doe/online-interface-r4.zh.md) fixes optional empty case-body
defaults, unnecessary public outputs for storage writes, task-correspondence
expression references, and source-review ownership. It retains the seven-call
workflow, fragment isolation, two workers, and existing budgets.

## Latest closed validation

The batch `interface-r4-high-20261104-173522` ran GA4, 001, 010, and 013 in that
order, with `gpt-6.1-sol / high / openai` and each case's complete frozen source
package. All controllers closed on 2026-11-04. Each sole zero-call replay matched;
the batch is delivered and its launch authorization is exhausted.

| Case | Generated IR processed | Saved DOE result |
| --- | ---: | --- |
| GA4 | 369/369 | Partial; all 250 sensitive comparisons unresolved, no reduction. |
| 001 | 13/13 | Partial; all 5 comparisons unresolved; a possible model-observation constraint warning remains. |
| 010 | 19/19 | Partial; no source-supported sensitive declarations, hence 0 sensitive comparisons; constraint limitations remain. |
| 013 | 31/31 | Partial; all 15 comparisons unresolved; all four terminal append/return paths computed. |

These are generated-IR denominators, not whole-source semantic coverage. The
finite GA4 source audit found representation and computation records for 13/13
listed API sites, 25/25 saveResult sites, and 3/3 explicit loops. State/file identity,
task-demand applicability, condition precision, and some candidate relationships
remain limited or unresolved. All four semantic DOE results are partial; neither
complete propagation nor zero comparisons establishes safety or complete DOE.
The audits are assistant source checks, not a human gold standard or a basis for
general precision/recall or superiority claims.

The batch recorded 43 actual native model starts (28 normal, 8 structural
corrections, 7 repair requests) and 3,486,080 public tokens. All 43 final usage
receipts were available; outer transport retries were zero. Provider-internal
HTTP attempts and unreported usage remain unknown. The four replays added zero
model calls and tokens. No currency cost is inferred.

Offline interface-r4 acceptance covers 591 distinct latest scoped XML cases with
no unresolved failures, after generated-sample synchronization and correction of
six obsolete full-snapshot assertions. The original 583-pass/8-fail receipt is
preserved. This is a union of scoped receipts, not one all-green whole-repository
execution.

Evidence: [delivered continuation state](../output/verification/online-interface-r4-20261104/continuation-state.json),
[four-run summary](../output/verification/online-interface-r4-20261104/four-run-summary.json),
[source coverage, correctness, and full available cost assessment](../output/verification/online-interface-r4-20261104/assessment.zh.md),
and [offline assessment](../output/verification/online-interface-r4-20261104/offline-assessment.zh.md).
The closed batch froze Python SHA
`b2d1966997e43b78f3a12c3afceb8e81e560137d619596af015238ee75333376`
and broader provenance SHA
`889d202b5e65dcd3bbee478580ac2dd46af0da278cf19b32cee7803733a5932f`.
These identify the archived batch, not a claim that later documentation is byte-identical.

## Manual entry

There is no automatic analysis launch on checkout or installation. Read
[AGENTS.md](../AGENTS.md) and the
[research handoff](research-chat-handoff.md) before continuing work. The commands
below document a future, explicitly authorized fresh run; they are not an
instruction to execute a new batch now:

```powershell
# From the repository root; prepare freezes a NEW source package without model calls.
python -m tools.doe.document_guided_pilot prepare --input path/to/skill --run-dir path/to/new-run --effort high
# Only after explicit authorization for that fresh run; this makes model calls.
python -m tools.doe.document_guided_pilot run --run-dir path/to/new-run
```

Preparation defaults to `max` unless `--effort high` is explicitly supplied; the
closed interface-r4 batch used `high`. The saved configuration controls execution.
The `replay` subcommand rebuilds from recorded responses with zero model calls,
but that does not authorize additional historical replays: each interface-r4
controller has already consumed its sole replay.

Preserve frozen source packages, raw model responses, failure receipts, results,
and their protocol/configuration identities. Do not overwrite them with current
code output or resume old controllers. The old v9 run remains paused. This
documentation and repository publication authorize no new model calls, probes,
Skill execution, resampling, historical replay, or staged-worktree integration.
