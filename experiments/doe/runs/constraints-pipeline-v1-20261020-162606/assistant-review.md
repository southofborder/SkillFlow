# Constraint-enabled formal pipeline: semantic assessment

This execution does not establish that the three Skills have faithful, complete constraints or that their sensitive information is all necessary. Case 001 failed before accepting an annotation. Cases 010 and 013 produced diagnostic analyses. No supported field reduction was produced, so this experiment did not exercise an approved constraint-preservation proof.

The assessment below was written after the calls, from the accepted artifacts and original inputs. It was not supplied to any production model request and is not an independent human gold standard. No accepted response was edited.

## Execution and cost

| Case | Outcome | Logical calls | Structural corrections | Semantic repair | Reported input tokens | Reported output tokens | Reported total tokens | Whole-case time |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 001 | Annotation failed; no DOE | 5 | 3 | 0 | 62,074 subtotal | 130,280 subtotal | 192,354 subtotal | 13m 39.3s |
| 010 | Initial review passed; DOE partial | 4 | 1 | 0 | 88,793 | 154,436 | 243,229 | 16m 11.5s |
| 013 | Fixed-Task repair; `repair_limit`; diagnostic DOE | 8 | 3 | 1 | 307,544 | 322,471 | 630,015 | 45m 55.0s |

There were **17 logical calls, seven structural corrections, 17 HTTP attempts, zero HTTP retries, zero JSON normalizations, one annotation repair, and no Task revisions**. The requested model was `deepseek-v4-flash`; the provider reported `deepseek-flash`.

The API-reported subtotal is **1,065,598 tokens**: 458,411 input and 607,187 output. Reasoning accounts for 507,117 of the output tokens and is not added again. The failed 001 request returned no usage, so the complete token total is **unknown**, not 1,065,598. No monetary price estimate is substituted.

The initial online process ran from **2026-10-20 08:26:50.474354 UTC to 09:42:41.464005 UTC**, or **75m 51.0s**. Recorded call-wall time totals 50m 30.3s. Whole-case time also includes compilation, propagation, DOE, validation and reporting; it must not be added to call time. These clocks were frozen before replay.

All three initial Task responses were structurally valid. **None of the three initial joint annotations was valid on its first response.** The seven corrections concern references, scope, expression ownership and realization consistency, not merely surplus JSON punctuation. This small run therefore does not demonstrate that structural correction costs have been solved.

The seven structural-correction requests alone have a **327,329-token reported subtotal**, with one request missing usage, and **14m 33.3s** of recorded call-wall time. They are included in the totals above; these figures are not additional consumption.

See [per-request metrics](metrics.md) and [machine-readable measurements](metrics.json).

## Constraint fidelity and separation from demands

### 001: no accepted constraint-bearing annotation

The new Task preserves the principal filtering, delivery, original-value, prohibition and count-save requirements. Annotation attempts successively used an expression's internal AST as a condition target, then an unsupported whole-IR target and an incompatible element scope. The final correction request ended with `IncompleteRead(0 bytes read)` and no complete response. The pipeline correctly stopped; it did not use an old successful annotation.

There is no propagation, sensitive-information result or constraint-preservation conclusion to inspect. Neither Task extraction nor the existence of a partial model stream establishes end-to-end coverage.

Evidence: [001 assessment](cases/001/assistant-review.md), [structural reference audit](verification/structural-reference-audit.assistant.md), [Task report](cases/001/task/report.md), [terminal result](cases/001/result.json).

### 010: correct actual request shapes, incomplete omission attribution

Actual conditional construction preserves the original optional values, omits absent members, and keeps the Boolean controls out of the request payload. The paired delivery and receive use the same request. Required query and optional-value demands reach the actual delivery; the total-save content and original-items return are also represented.

However, the separate absent-member requirements were structurally accounted for by adding presence demands on the build output. Their derivations do not establish those requirements at the external-tool receiver. This is a demand-attribution gap, not evidence that the propagated request contains a missing parameter. Redundant unconditional `expected` references on optional delivery demands also retain the source values independently of the build condition. The initial model review reported no finding on these distinctions.

The no-index-deletion requirement remains an explicit unsupported gap rather than a fabricated event target. The resulting global conservative block is visible, so formal DOE remains partial.

Two constraints were checked: a single search invocation and search-before-save. The acyclic CFG supports both structural results. Ten real positive demand seeds drive 231 derivations; the constraint declarations do not create additional positive seeds.

There are 12 sinks but no sensitivity declarations and no data-review rows or reductions. This means that the current declaration set offers no sensitive scope to assess; it does not prove that all content is non-sensitive or that no DOE exists.

Evidence: [010 assessment](cases/010/assistant-review.md), [initial annotation audit](verification/010-initial-annotation-audit.assistant.md), [Task report](cases/010/task/report.md), [DOE result](cases/010/doe/doe-result.json).

### 013: payload binding improved, constraint semantics and reviewer reasoning remain unreliable

The selected repair preserves the parameters of both preferred-service calls, source-only fallback parameters, branch-specific return identities, and both action and content demands for all four status appends. Forward propagation confirms distinct first-call, retry and fallback versions. The prohibitions do not become positive payload-demand seeds: all 24 positive seeds remain separately traceable through 1,068 combined derivations.

Three constraint concerns remain:

1. **Transient retry condition.** The initial annotation used a plain reference to an outcome as the transient predicate. The review correctly challenged that. The accepted repair instead tests a `transient` member of a locally computed outcome, but no producer relationship, source requirement or CFG representation defines that local member. This is an unsupported local representation assumption, not a demonstrated external API response schema and not a proved transient classifier.
2. **No calls after success.** The prohibition is triggered at terminal return operations, later than the success boundary stated by the source. The three late-trigger checks pass for their declared relation, which is weaker than the source requirement.
3. **Diagnostic prohibition scope.** The declaration covers the status-file receiver, without fully accounting for the extent of diagnostic outputs. A successful check of that chosen receiver could not prove complete coverage of the source restriction.

There were also two unsupported model-review findings:

- The initial review claimed that a sensitivity declaration on the selected key could not cover its earlier parent-environment observation. An offline check of the existing identity/part relation shows that it can. The repair retained the child declaration and added a parent-path declaration, yielding duplicate assessments of the same sensitive range rather than establishing a previously absent exposure route.
- The final review claimed the four write IRs had no `input[1]`. All four actual CFG instructions have `input[0]` for the file and `input[1]` for the matching outcome. The atomic write's `ValueRef input[1]` and its demand's operation-payload `input[0]` are both correct coordinates in different reference systems. The proposed change would have selected the file identifier. It was not executed because the one semantic repair had already been used.

The final model finding therefore leaves `repair_limit`, but the finding itself is not a trustworthy proof of the alleged operand error. Other substantive issues above remain unreported by that review.

Evidence: [013 detailed assessment](cases/013/assistant-review.md), [sensitivity finding audit](verification/013-initial-sensitivity-finding.assistant.md), [Task report](cases/013/task/report.md), [selected annotation](cases/013/refinement/repair/audit/raw-annotation.json), [final review](cases/013/refinement/final-review/report.html).

## What the final DOE results establish

| Case | Actual sinks | Constraint checks | Sensitive-range comparisons | Approved reductions |
|---|---:|---|---|---:|
| 001 | Not computed | Not computed | Not computed | Not computed |
| 010 | 12 | 2 satisfied under the declared model | No declared sensitive scopes | 0 |
| 013 | 16 | 11 satisfied; 5 potential violations | 20 `no_excess_established` rows | 0 |

For 013, ten of the eleven satisfied checks have structural grounds. Four potential violations concern conditional execution: the annotation does not provide the normalized control-edge associations needed to establish the specified condition along every abstract path. Those witnesses are static possibilities, not measured executions. The fifth potential violation concerns possible/derived credential influence on status outputs; it does not establish plaintext credential inclusion.

The 20 sensitive-information rows are ten operation/range assessments represented for two declarations of the same credential scope: eight direct-content rows and twelve possible-influence rows. They are not 20 independent leaks. `no_excess_established` means the analysis did not establish a supported excess conclusion; it does not prove indispensability.

The saved constraint-preservation and forward-influence proof maps are empty. **There is no approved reduction whose preservation proof can be endorsed from this online run.** Frontend fidelity issues must remain visible even where deterministic calculation reports complete. Prohibitions have not removed fields from actual propagation, and the constraint checks have not manufactured positive demand seeds.

See [010 DOE](cases/010/doe/doe-result.json) and [013 DOE](cases/013/doe/doe-result.json).

## Verification and next priorities

The run uses the verified existing CFGs and audited English source projection, newly extracts each Task, and preserves the original accepted request/response chains. Historical inputs are read-only. [Zero-API replay](replay-summary.json) completed with identical case decisions, including the 001 failure, and no new API calls. The [completion receipt](verification/completion.json) confirms unchanged call files, historical inputs, implementation identities and original online clocks. The [validation record](validation.md) explains these checks and their limits.

The next engineering priorities indicated by these observations are narrowly defined:

- Make the already-supported condition-owner, data-version, element-scope and control-edge association rules directly usable in generation and structural diagnostics.
- Prevent the reviewer from rejecting correct IR-input versus operation-slot bindings or proposing duplicate sensitivity declarations when existing part relationships already cover the scope.
- Review restriction event boundaries and applicable receivers against the source, independently of whether the declared relation passes a backend check.
- Keep optional endpoint obligations distinct from upstream construction and conservative `expected` dependencies.

These are proposed follow-up priorities, not changes made to the production implementation or to this experiment's accepted annotations.
