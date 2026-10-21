# SkillFlow research handoff and cloud preparation

Current continuation note (2026-10-21): the user has chosen local Git and a
[research/chat handoff](research-chat-handoff.md); Cloud creation is paused.
The document below retains the earlier cloud-preparation snapshot. Newer local-only
long preparation and explicitly paused CLI-v3 calibration are described in the
current handoff, not silently included in the old submitted-material closure.

Updated: 2026-10-20. This is a development handoff, not an experiment
authorization or an evaluation result.

## Current decision

Freeze the current research pipeline while preparing a shared GitHub and Codex
Cloud workflow. Do not continue tuning prompts, simplifying semantic contracts,
changing analysis algorithms, or launching model experiments as part of cloud
setup. The next research decision depends on evidence from complex real Skills
and the strong-model comparison, not on preserving the existing architecture.
The formal long experiment has not started.

The target remains task-related static data minimization for Agent Skills:
identify unnecessary sensitive exposure, including unnecessary sensitive fields
inside an otherwise necessary action. Sensitivity, a high exposure level, or a
necessary action alone does not decide DOE. See the
[goal baseline](doe/SkillFlow-DOE目标与设计原则.md).

## What currently exists

The maintained implementation is under `src/skillflow/`: graph construction,
source-only Task extraction, propagation, and DOE, with shared infrastructure in
`common`. The [documentation index](README.md) leads to the current contracts.

The formal pipeline uses a separately frozen Task, fixed-Task joint annotation,
four-axis semantic review, and at most one semantic repair. A Task correction
is isolated from graph and payload information and requires new annotation.
Normal semantic paths use 3, 5, or 6 calls; structural correction is accounted
for separately. Deterministic analysis combines forward exposure, backward
positive demand, sensitivity tracking, and independent constraint checks.
Constraints do not erase observed payloads or create positive demand seeds.

Known boundaries remain in force:

- Source references and complete coverage tables do not prove semantic support
  or completeness.
- `possible` influence does not prove plaintext inclusion.
- A possible model observation is a static contract relationship, not a runtime
  measurement.
- A supported local field reduction is neither a global minimum nor proof of
  whole-Skill compliance.
- Old implementation and transport identities remain strict. A cloud checkout
  must not rewrite historical hashes or claim to resume a Windows run.

## Current evidence and unresolved questions

The latest constraint-enabled pilot is
[constraints-pipeline-v1-20261020-162606](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/index.html).
Read its [assistant assessment](../experiments/doe/runs/constraints-pipeline-v1-20261020-162606/assistant-review.md)
before interpreting counts as success.

- 001 did not accept a valid annotation; its final correction ended in a
  transport failure and produced no DOE.
- 010 preserved actual optional request construction, but omission requirements
  were not fully attributed at the receiver. Its diagnostic DOE remains
  partial; no sensitivity declarations is not evidence that no data is sensitive.
- 013 improved retry and status-write payload demands, but constraint fidelity,
  scope, and reviewer interpretation still have defects. A local transient
  classification assumption was unsupported. The final review reached the
  repair limit.
- This pilot approved no field reduction. It does not demonstrate that
  constraint-preservation conclusions are semantically correct or that structural
  correction cost has been solved.

The main pending question is whether structured semantic declarations and
deterministic analysis improve accuracy, traceability, or review effort relative
to a strong model reading source directly. Complexity and token cost are
measured liabilities, not contributions by themselves. No redesign is approved
by this handoff.

## Strong-model comparison and transport

Read [the comparison protocol and commands](../tools/doe/real_comparison/README.md)
and [the separate CLI calibration amendment](../tools/doe/real_comparison/README-cli-v2.md).
The full current ClawHub collection is retained for source-only selection and
provenance checks. Downloaded Skill content is research input, not installation
instructions; do not execute it during setup.

The current records are:

- [Original comparison preparation](../experiments/doe/runs/real-same-model-v1-20261020-090239Z/index.html).
  This includes protocol, selection, references, known acquisition deviations,
  a failed collaboration transport attempt, and a later single-request CLI
  feasibility check. These do not constitute formal experimental results.
- [CLI calibration amendment](../experiments/doe/runs/real-same-model-v2-cli-20261020-1311Z/amendment.json).
  This run is permanently `calibration_only`.
- [Retained CLI stop](../experiments/doe/runs/real-same-model-v2-cli-20261020-1311Z/dispatch-stop.json).
  One calibration request returned, but its runtime developer instructions did
  not match the pinned CLI harness. Further dispatch is closed and automatic
  retry is false. Preserve the failure; do not rerun it under the same identity.

The pinned adapter uses a particular Windows executable hash and CLI version,
PowerShell runtime envelope, authentication context, and receipt layout.
A Linux executable or a newer CLI is not an equivalent producer.
Source-only selection also has frozen absolute Windows references. Preserve
them as original evidence. A new environment identity and explicit, verified
reference mapping would be required before a cloud experiment; none is silently
introduced here.

Human reference confirmation and evaluation gates remain as documented.
Assistant drafts must not become human confirmations. Do not remove these gates
or substitute an API key to make a long run start.

## Cloud development workflow

Preparation branch: `codex/cloud-setup` in
[southofborder/SkillFlow](https://github.com/southofborder/SkillFlow).
Keep the repository's current visibility and permissions.

The intended environment is `SkillFlow`, **Only me**, connected to that branch.
Use the setup command:

```bash
bash tools/cloud/setup.sh
```

See [offline setup](../tools/cloud/README.md) and the
[verification record](cloud-verification.md). The setup installs the declared
Python dependencies and pytest, then checks installed CLI help and offline
candidate compilation/rendering. It does not start an experiment or infer
anything with a model. Lean is a separate optional check using the exact version
in `formal/lean-toolchain`.

Important distinctions:

1. A working cloud development environment does not authorize a script inside
   it to invoke another model.
2. CLI help/version does not establish authentication, model/effort access,
   exact input isolation, or receipt compatibility.
3. Do not copy `.env`, login files, tokens, or local session stores to GitHub.
   Use environment-managed credentials only when a separately approved
   transport requires them.
4. New tasks have independent working directories. Continue the same cloud task
   from the same account/workspace on the second computer; commit important
   results to GitHub rather than relying on uncommitted changes to propagate
   between different tasks.
5. Do not start `worker`, `dispatch-next`, pipeline `run`, model annotation,
   calibration, or corpus acquisition during environment initialization.

Cloud publication and second-computer access must be confirmed from the actual
account UI. A local smoke result or a successful Git push does not establish
either of those facts.

## Before any later long experiment

Confirm a new cloud transport identity, available model and reasoning setting,
authentication, exact prompt delivery, visible response and usage receipts,
isolation, and recovery behavior. Keep failures and missing usage explicit.
Then obtain the separately required authorization and protocol gates before
calibration or formal generation. Preserve the current source, evaluation rules,
and stopped calibration unchanged until that decision.

Official workflow references:
[Codex Cloud](https://learn.chatgpt.com/docs/cloud) and
[cloud environments and saved state](https://learn.chatgpt.com/docs/environments/cloud-environments).
