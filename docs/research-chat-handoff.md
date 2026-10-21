# SkillFlow research and conversation handoff

Updated: 2026-10-21. This is a structured reconstruction of the research discussion
and a read-only inspection of repository evidence, not a verbatim chat export,
an experiment authorization, or a claim that every local file has been uploaded.

## 1. Start here on the second computer

The user has chosen **GitHub plus a local checkout and this handoff**. Creating a
Codex Cloud environment is paused after unsuccessful setup attempts. No usable
Cloud environment or Linux Cloud verification has been established. The current
research pipeline is frozen for comparison: do not keep tuning prompts, redesign
the protocol, acquire more evaluation inputs, or dispatch model calls merely to
continue this handoff.

The current user request authorizes review and submission of two tracked research
files, the research/chat handoff, and a fast-forward of `codex/cloud-setup` into
`main`. It excludes the modified billing files and does not authorize experiments.
The package version `0.1.0` is not a research snapshot identifier; record the exact
Git revision with `git rev-parse HEAD`.

Read in this order:

1. [Repository instructions](../AGENTS.md) and this handoff.
2. [DOE goal baseline](doe/SkillFlow-DOE目标与设计原则.md).
3. [Current formal pipeline](doe/joint-pipeline.md).
4. [Constraint implementation and limits](doe/constraint-implementation.md).
5. [Comparison protocol and tools](../tools/doe/real_comparison/README.md).
6. [This submission's verification](research-handoff-verification.md) and
   [local-only material inventory](research-local-only-inventory.json).

The goal document establishes the research objective; its earlier introductory
version descriptions do not override the later constraint implementation.
Frozen reports describe their own runs, not the status of a newer implementation.

## 2. Research objective and unresolved contribution question

SkillFlow studies **task-related static data minimization for Agent Skills**.
It combines sensitive information, processing relationships, path conditions and
recipients to find unnecessary sensitive exposure. Both unnecessary actions and
surplus sensitive payloads inside necessary actions are in scope. A required
action does not make every carried value or sensitive field necessary.

An exposure boundary, a sensitive label, or a task-required action alone does not
establish DOE. The coverage objective is all unnecessary sensitive exposure; it
is not a demonstrated zero-miss guarantee. The implemented demand analysis keeps
functionality under the declared current relationships. It does not prove global
minimality, indispensability, or equivalence to every possible implementation.

The central open question is whether this structured analysis improves accuracy,
traceability and cost enough over a strong model reading the source directly,
or over a stronger taint/data-flow baseline with model assistance. The user and
advisor explicitly challenged whether the machinery makes the model's job harder.
No overall advantage over direct prompting or Semia has been established here.
Do not preserve complexity just because it exists; equally, do not discard the
implementation before the planned complex-Skill comparison supplies evidence.

The next research discussion should be driven by that comparison, not another
round of prompt additions based only on the three development cases.

## 3. Decisions carried forward from the conversation

| Topic | Current decision and important boundary |
|---|---|
| Graph | The three development-case pilots reused frozen CFGs. The formal same-model native comparison requires fresh graph construction under its protocol. Graph structure checks and controlled-text/Lean facts do not prove equivalence to natural-language intent. |
| Actual processing | Preserve whole values unless an actual selection, exclusion, replacement or other supported relation narrows them. A simple operation or absent LLM mention does not establish local isolation. |
| Default visibility | Apply the frozen runtime contract when mechanisms are unspecified. Explicit local execution and limited return mechanisms must be respected. Possible model observations are static relations, not observed execution. |
| Field identity | Explicit field selection, unchanged members, constructed payloads, computations and tool acquisition remain distinct. `possible` influence is not proof of literal content. |
| Conditional requests | Conditional build members preserve original values; absence controls are not payload fields. Paired request/response bindings preserve actual request identity. |
| Locations and sinks | Locations describe boundaries before Data is propagated. The program derives sink types and fixed exposure levels from operations and location properties. Level is boundary character, not sensitivity, authorization or risk. |
| Source evidence | Use frozen files and physical line ranges; the program extracts exact text. Line coverage proves references, not semantic completeness. Old paragraph indexes are retired from the active interface. |
| CFG evidence | Use real CFG identities and direct targets. A review target locates a candidate claim; it is not a CFG evidence address. CFG facts do not establish facts that exist only in the candidate or source. |
| Task | Extract and seal it independently from source plus an optional user request. Later annotation references that exact Task. Do not reconstruct purpose from the current graph's payloads. |
| Realization | State how each requirement is expressed, partly expressed, retained, or unmapped. A correct requirement does not imply all applicable receiver parameters have demand declarations. |
| Positive demands | Six properties: value, presence, cardinality, shape, truth and action. They are computational preservation starting points, not per-IR necessity scores. |
| Receiver demand | Required delivery content belongs at the actual receiving input and field range. An action or shape demand, or an upstream build/selection demand, cannot silently stand in for recipient content. |
| Reading versus requiring | Whole-value acquisition or observation does not justify a whole-value task demand. Narrow task demands do not retroactively narrow actual reading or visibility. |
| Backward demand | Trace actual inputs, outputs, versions, conditions and element scope. Downstream-required information cannot disappear and then be recovered from a global Data registry. Demands do not spread to unrelated recipients just because Data IDs match. |
| Sensitivity | Declare grounded information ranges on existing symbolic values; the program tracks them. No declaration does not mean no sensitive data. Derived/possible influence remains distinct from confirmed content. |
| Constraints | Check independently in the forward direction. A prohibition does not delete payload facts or become positive demand. Conditions/counts/order do not remove violating paths. |
| Reduction | Only supported `exclude_field` candidates are currently considered. Preserve positive requirements and separately justify relevant constraint preservation; keep original violations visible. |
| Review and repair | Independent four-axis review; one shared semantic repair budget. Task repair is isolated from graph/payload/free review text; annotation repair holds Task fixed. |
| Structural correction | Mechanical validation and semantic review remain separate. Production structural corrections have no count cap. Restricted JSON normalization preserves the original response and receipt. Transport/truncation/identity/implementation failures are not infinite semantic correction loops. |
| Language | Maintained prompts, synthetic examples, generated interpretations, diagnostics and new reports use English. Source text, user text, quotations and frozen historical artifacts retain their original language. |
| Accounting | Record logical requests, structural corrections, HTTP attempts, usage and elapsed time separately. Unknown usage stays unknown. Reasoning/cache details must not be added again to totals that already include them. |

The earlier idea of generating Task inside one joint response was superseded by
independent source-only Task extraction. The earlier proposal to add constraint
dependencies generally to backward demand was superseded by independent forward
constraint checks. Do not revive either design by following an old chat excerpt.

The former `doe-input.json` total bundle and separate Task/demand/sensitivity
experiment wrappers are retired from the active production chain. Do not rebuild
them as prerequisites or migrate frozen old records. Each stage stores its own
outputs, binds the actual upstream stage, and uses public verified loaders.

## 4. Current implemented flow and code ownership

```text
Frozen Skill + optional user request
    -> independent source-only Task extraction and seal
Existing CFG + frozen Task + source + runtime contract
    -> joint annotation of processing, boundaries, demands,
       realizations/constraints and sensitivity
    -> independent semantic review
       -> accept; or one annotation repair; or one isolated Task revision
          followed by new annotation
       -> independent re-review when repaired
    -> select the last legitimate candidate, retaining review status
    -> observation/sink compilation and forward propagation
    -> backward positive demand + sensitivity tracking
       + independent forward constraint checks
    -> sink comparisons and supported reduction-preservation evidence
```

The diagram starts at the downstream pipeline used by the development pilots.
The formal same-model native comparison also constructs its own fresh graph;
it must not import an old graph or a cross-repeat semantic cache.

Normal semantic paths use **3 / 5 / 6 calls** respectively. Structural correction
and HTTP retries are additional and separately counted. A structurally valid
candidate may still be diagnostically analyzed after review failure or a repair
limit; computational completion must not replace that status with semantic pass.

| Location | Responsibility |
|---|---|
| `src/skillflow/common/` | Frozen sources, references, strict JSON, model transport, call records and recovery |
| `src/skillflow/graph/` | CFG, construction, validation, source checking and bounded graph feedback |
| `src/skillflow/task/` | Independent Task extraction, sealing and isolated revision |
| `src/skillflow/propagation/` | Shared contracts, annotation/review/repair, observation compilation, Data and forward propagation |
| `src/skillflow/doe/` | Backward demands, information tracking, constraints, sink comparison and formal DOE runs |
| `tools/doe/real_comparison/` | Comparison preparation, calibration and execution orchestration; not core semantics |
| `formal/` | Existing Lean project and proof material |

Use `python -m skillflow --help` to inspect installed stage commands. The formal
entry points remain pipeline prepare/run/replay and the independent stages.
This handoff deliberately does not provide a dispatch command: preparation or
old recorded authorization is not permission to start an experiment now.

Current interface versions, verified against the implementation reference:

| Interface | Version |
|---|---|
| Task / Task reference | v3 / v1 |
| Runtime contract | v7 |
| Joint annotation profile | v15 |
| Processing compiler / mapping | v9 / v9 |
| Annotation run | v18 |
| Review response / review run / refinement run | v7 / v11 / v10 |
| Propagation run | v15 |
| Demand / sensitivity result | v4 / v4 |
| Formal DOE run / pipeline / three-case pilot | v5 / v7 / v8 |
| Structural correction protocol / Data | v5 / v4 |

Some run identity strings retain the historical `skill-ir-` prefix. This does not
restore an active `skill_ir` package. This handoff changes no business version.

The four constraint families use five bounded forms: `forbid_information`,
`only_if`, `at_most`, `requires_prior`, and `forbid_after`. They reuse Task evidence
and existing references. A constraint can be completely expressed while current
behavior potentially violates it. Unsupported scope, missing relationships and
incomplete coverage remain limitations. Neither restrictions nor their checking
dependencies are positive demand seeds.

## 5. Latest formal development-case evidence

The latest tracked three-case result is
[constraints-pipeline-v1-20261020-162606](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/index.html).
Read its [assistant review](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/assistant-review.md),
metrics and replay files together. The following is a research interpretation,
not an independent human gold standard:

| Case | Material outcome | Remaining substantive issue |
|---|---|---|
| 001 | No accepted annotation after final structural-correction transport failure; no DOE | Do not present an older successful DOE as this run's result. |
| 010 | Optional request construction preserved; diagnostic DOE is partial | Receiver-level absent-member demand attribution is incomplete, a deletion restriction remains unsupported, and no sensitivity declarations were supplied. Empty sensitive findings are not a safety claim. |
| 013 | Retry parameters and all four terminal status-write payload demands improved; semantic repair limit retained | Unsupported local transient classification, a late success-stop trigger and incomplete diagnostic prohibition receiver scope remain. Review also proposed a wrong operand change and duplicate sensitivity. |

Recorded totals are 17 logical calls, seven structural corrections and one
semantic repair, with 17 HTTP attempts and no HTTP retry. Reported usage is a
**1,065,598-token subtotal**, not a complete total: the final failed 001 request
has unknown usage. Zero-API replay preserved the saved decisions and failures.

010 has 12 sinks and two satisfied constraint checks. 013 has 16 sinks, 11
satisfied checks (10 structural) and five potential violations. Its 20
`no_excess_established` rows include duplicated sensitive declarations; they are
not 20 independently confirmed leaks. There were no supported field reductions.
The online runs therefore did **not** exercise a successful reduction-preservation
proof. Counts or an absence of reductions alone are not a quality evaluation.

Earlier prompt screens and the original 001/010/013 runs are development history.
They are not fresh held-out evidence after repeated prompt adjustment. Strict
replay may reject old producer identities; do not alter their hashes to obtain a
pass under current code.

## 6. Complex-Skill comparison: preparation versus execution

The intended comparison needs common inputs, clearly frozen task/evaluation
criteria, honest costs and comparable model access. Do not select easier inputs,
change thresholds after results, or treat assistant-authored semantic references
as independent human approvals. The current tools and recorded protocol, rather
than this narrative, govern any eventual authorized run.

There are three distinct preparation states:

1. **Tracked cloud-preparation snapshot.** The earlier source-selection report
   records 30 choices (24 selected plus six reserves) and 22 selected source
   clusters, pending root/human-reference checks. The cloud material audit's
   review counts and dependency seal describe that point in time.
2. **Newer local-only long preparation.**
   `experiments/doe/runs/real-same-model-long-v2-20261020-1340Z/` contains a separate
   source-selection seal and 30 offline-verified preparation packets; 65 source
   reviews were checked. Its state records **zero formal requests, zero human
   approvals, incomplete semantic references and dispatch disabled**. It is not
   included merely by committing this handoff's inventory.
3. **Newer local-only CLI v3 calibration.**
   `experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z/` records a calibration
   started after authorization in another conversation and then explicitly
   paused at `2026-10-20T14:14:15.778016+00:00`. The `gh-fix-ci` q001 attempt has no
   saved response or receipt and unverified usage. Processes were stopped and
   automatic dispatch is forbidden. **Do not resume it or delete locks.**

Thus the formal long comparison has not started, but it would be inaccurate to
say that no calibration attempt ever started. The older tracked CLI v2
calibration remains stopped after an execution-envelope mismatch and is not a
formal result. Cloud or another computer needs its own verified transport,
authentication and receipt behavior; do not copy Windows login files, inherit
Windows producer identity, or silently substitute a paid API.

The newer long bundles have reference sizes of 21,361-62,869 `o200k_base` tokens
(median 38,273; total 977,753). These are source size measurements from preparation,
not actual API usage or permission to dispatch. None is a measured strong-model
comparison result.

The reviewed selection helper now requires stronger evidence for an implicit
file connector. Some frozen older source reviews used directory-copy quotations.
Those records were not resealed or relabeled in this handoff. Before a future
selection verification or experiment, audit the evidence under the intended
implementation instead of relaxing the new guard or claiming historical success
automatically transfers to it.

## 7. What Git transfers, and what remains on the first computer

The prepared branch already contains current research implementation, tests,
documentation and the comparison materials enumerated by the
[cloud material audit](cloud-material-audit.md). The present submission reviews
and updates `long_selection.py` and its tests, then adds this handoff and its
verification/navigation. All previously tracked history remains intact.

The [local-only inventory](research-local-only-inventory.json) is metadata for
**1,054 files / 42,325,410 bytes** observed on 2026-10-21. It records exact relative
paths and hashes without submitting their contents:

| Local-only scope | Files | Bytes |
|---|---:|---:|
| Active CLI-v3/supervisor/preparation implementation, tests and docs | 15 | 241,428 |
| Long-cohort preparation | 785 | 34,106,614 |
| Paused CLI-v3 calibration | 230 | 2,347,116 |
| CLI-v3 proposal and adoption records | 17 | 75,847 |
| Supplemental selection audit | 7 | 5,554,405 |

This is an explicit scope inventory, not an inventory of all ignored files or all
historical experiments. Locks are presence metadata only, not resumable ownership.
These local-only source files require a separate review/submission or an explicitly
requested file transfer before the second computer can use that newer preparation.
If they are missing, stop that activity and report what is absent; do not synthesize
replacement receipts or recreate authorizations. The two requested tracked changes
must not be described as synchronizing this additional work.

The modified `output/pdf/bill-template.pdf` and `.tex` stay local and unchanged.
Their earlier tracked history is not rewritten. No credentials, authentication
files, virtual environments or account secrets are part of this handoff.

Keep `.gitattributes` byte-preservation rules. Frozen absolute report URLs may still
name the original Windows checkout. Use repository-relative navigation for new
work; do not rewrite frozen reports or producer manifests to hide the move. Move
an entire run with its explicit dependency closure, not isolated stage files.

## 8. Safe local setup and continuation

On the second Windows computer, install Git and a supported Python (3.10 or newer),
then use a short checkout path. After the main merge has been confirmed:

```powershell
git -c core.longpaths=true clone --branch main https://github.com/southofborder/SkillFlow.git
cd SkillFlow
git config core.longpaths true
git status --short
git rev-parse HEAD
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . pytest
.\.venv\Scripts\python.exe -m skillflow --help
```

Installation may download package dependencies; these commands do not authorize
or intentionally dispatch model work. For an existing checkout, inspect local
changes first, then `git fetch origin` and `git pull --ff-only`; do not overwrite
uncommitted work. Record the actual Python version and Git commit. Lean is optional
until a formal check is requested; its repository-pinned toolchain must be used.

Open this repository in Codex, read `AGENTS.md`, and start a new chat with the
message below. Git transfers committed files, **not the app's conversation**.
This document carries the important research context, decisions and exact places
to inspect. It does not preserve every chat turn or automatically migrate a live
task/session. If exact dialogue is needed, preserve it separately using the app's
available sharing/export facilities.

> Continue SkillFlow from this checkout. Read AGENTS.md and
> docs/research-chat-handoff.md before acting. Verify the current branch and Git
> revision, distinguish committed evidence from the local-only inventory, and
> summarize the research state and unresolved strong-model comparison. The
> pipeline is frozen: do not modify prompts or the research protocol, dispatch
> model calls, resume calibration, start long experiments, acquire new evaluation
> inputs, or reinterpret old run identities. The latest task is cross-computer
> research handoff. Ask for the specific next research decision after reporting
> available and missing materials. Do not treat absent local-only files as proof
> that preparation never occurred.

## 9. Decisions still needed before research execution resumes

- Review/transfer the 15 local-only implementation files and their required
  preparation materials if the newer CLI-v3 route is to be used.
- Resolve transport and receipt validity on the actual destination computer;
  prior authorization and old Windows identities do not settle this.
- Review the source-selection connector evidence affected by the tightened guard.
- Complete independent human reference/approval gates required by the comparison.
- Explicitly decide whether and how to resume the paused calibration, then the
  formal comparison. No permission is inferred from this list.
- Use the comparison to decide which semantic declarations help the model and
  backend, which can be generated deterministically, and which complexity should
  be removed. No redesign is prescribed by this handoff.

The immediate deliverable is a reviewed Git snapshot and a reliable continuation
record. Neither successful synchronization nor offline test completion establishes
semantic correctness, research superiority, or an absence of DOE.
