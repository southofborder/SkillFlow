# Source-established missing whole input: frozen implementation gap audit

The frozen implementation detects a missing field within an actual input, an invalid field selector, and existing expected-relation mismatches. It does **not** currently carry a source-established missing entire argument into a typed `missing_input` finding. A reviewer can describe the omission in prose, but the stored demand/report path treats a rejected contract as a contract limitation instead of a known Skill error.

This is a real gap against the approved requirement to report known missing necessary inputs separately from unresolved semantics. It does not justify inferring an intended argument from an unfamiliar API or an unknown runtime value. The example here explicitly supplies the interface obligation and the actual omission in its source.

## Frozen-code evidence

| Location | Current behavior | Consequence |
|---|---|---|
| `src/skillflow/propagation/contracts/input_requirements.py:85` and `:216` | Contract input indexes must equal `range(len(actual_operation.inputs))` exactly. | A second required argument cannot be represented as an extra actual slot when the call has one input. This invariant should remain. |
| `src/skillflow/propagation/contracts/input_requirements.py:61` and `:129` | An input requirement addresses an actual `input_index`; the tool contract has actual rows, reason and evidence. | There is no separate typed absent-argument obligation. |
| `src/skillflow/doe/input_contract_review.py:22` | A check has `contract_id`, accepted/rejected/unresolved status, reason and evidence. | Source error versus annotation/contract error is not a typed distinction. |
| `src/skillflow/document_guided/source_review.py:49` and `:98` | Findings target CFG, Task or annotation, with an annotation repair owner. | No typed source-input error channel identifies an already-faithful representation of a defective Skill. |
| `src/skillflow/document_guided/source_review.py:557` | Each nonaccepted contract check becomes a processing-owned repair finding. | A true source omission is not distinguished from a repairable semantic-annotation omission. |
| `src/skillflow/doe/input_contracts.py:89` | A rejected check produces `input_contract_rejected`. | The cause remains a conservative dependency limitation. |
| `src/skillflow/doe/demand_engine.py:248` | Missing/invalid checks examine each required path in recorded existing input slots. | Known absence inside a supplied object and invalid object access are supported; absent whole slots are not inspected. |
| `src/skillflow/doe/input_assessments.py:366` | Only expected-relation errors, excluded requirements, `input_contract_missing_input` and `input_contract_wrong_input` map to typed input findings. | The source-established omission recorded only in a rejected-check reason yields no `missing_input` finding. |

## Isolated offline reproduction

The source is deliberately explicit:

> The documented Service.fetch interface requires both a and b as arguments. The actual workflow calls Service.fetch(a) with only a, omitting b, and returns its response.

The synthetic forward call and response each keep one real input. Two source-backed rejected contract checks explain that argument `b` is absent. The reproduction uses the current deterministic compiler/propagator and an injected review receipt; it makes no model request and executes no Skill.

Observed result in `result.json`:

- Adding a contract row for nonexistent index 1 is rejected with `Input requirements must account for every actual input index exactly once`.
- The demand result is `partial` with diagnostic code `input_contract_rejected`.
- `known_missing_or_wrong_input_findings` is empty.
- Both real request/response input counts remain 1 and the forward record digest is unchanged.

The preservation behavior is correct. The missing feature is the typed known-error report and its distinction from repairable annotation mistakes, not permission to append argument `b` to the actual CFG or synthesize its value.

To reproduce from the repository root, use the isolated test interpreter with `-c "import runpy; runpy.run_path('output/verification/input-necessity-20261111/missing-slot-audit/reproduce.py', run_name='__main__')"`. The initial direct script invocation failed solely because its import path did not include the repository test helpers; the root-based invocation completed all assertions. No current or historical online analysis was replayed.

## Smallest necessary correction after all four runs and their sole replays close

Keep the exact actual-input coverage invariant. Add one explicit, source-backed **known source-input mismatch** channel to the existing seventh-step review and its sealed receipt. It must distinguish a faithful representation of defective source from a CFG/annotation representation defect; existing generic rejected-check text is insufficient.

For a missing argument, the typed record needs the existing operation/contract coordinate, the source-established argument identity or position, the affected output/action obligation, exact interface/source evidence, and why the actual call lacks that input. An absent actual slot remains `null`/absent; do not assign it a fabricated CFG input index. A parameter name is valid only if source/interface evidence supplies it.

Consume that reviewed record deterministically as a localized `missing_input` semantic finding, retaining its receipt/source references and the actual forward call unchanged. Block only conclusions that require the unattainable output or action; do not create demand nodes or value data for the missing input. Existing supplied fields can retain independently established demands. The same typed channel can distinguish source-established wrong bindings, without converting every rejected contract into a source error.

Routing must preserve the existing repair distinction: a representation omission can be fixed by processing/CFG repair; an argument actually omitted by the Skill must remain omitted and be reported. Repair may make the annotation faithful to that error, but must not silently implement the missing argument. This stays within the existing seven requests, workers and repair budget.

Minimum post-batch regressions:

1. The explicit two-required/one-actual tool example produces `missing_input` with source/interface evidence, one real input, no synthetic missing value, and no generic uncertainty replacing the known error.
2. A known missing compute input is scoped to the affected output relation; an independent output remains assessable.
3. An argument absent only from the annotation, but present in the source call, routes to representation repair instead of a source-error verdict.
4. An unfamiliar/undocumented interface does not establish that any argument is missing.
5. The source-error receipt cannot be reused after source, CFG, annotation or review repair; report loading preserves the typed finding and exact provenance.

This recommendation is additional to the separately recorded mandatory tool-contract presence check. No production, prompt, tool, renderer, source-package or online-run artifact was changed during this audit.
