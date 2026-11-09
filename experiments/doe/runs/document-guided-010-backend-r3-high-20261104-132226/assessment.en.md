# 010 catalog-query: backend-r3 online assessment

Propagation completed for all 21 generated IR. The request, call, actual total save and complete items-return relationships are recorded and source-supported. DOE computes useful payload-to-demand support but remains partial because two constraint references failed and other requirement/boundary limits remain. Zero sensitive-data comparisons is consistent with the available source, not an annotation failure by itself and not proof of safety.

The fresh run used `gpt-6.1-sol / high / openai`, two workers and the same three frozen source files. It selected the initial CFG and assembled annotation, with no semantic repair. Its controller and sole zero-call replay have closed; the replay matched.

## Coverage and correctness

| Source relationship | Saved result |
|---|---|
| Acquire request.json | `ir_001`; original request identity retained |
| Call index.search with original term and present optional fields | `ir_016`; four correlated argument candidates |
| Save actual response.total to count.txt | `ir_018` selection, `ir_019` write; actual response field, not request parameters |
| Return complete response.items unchanged | `ir_020` selection, `ir_021` return operand; same paired response |

All four inspected source relationships are present. The source does not specify a return recipient, so return-value correspondence is established without inventing a user/network output sink. Generated coverage is 21/21 processed, with no cutoff, blocked, not-reached or not-solved IR. The 16 saved sink positions comprise 14 contract-default model observations, one tool boundary and one storage write. These counts are distinct from source-site counts and dynamic invocations.

The four argument field sets are exactly `{query}`, `{query, limit}`, `{query, from_date}`, and `{query, from_date, limit}`. Query and each optional value preserve their original request-field identities. Each argument remains paired with its response, that response's total write and its complete items return. Missing fields are omitted, not replaced by null or fabricated defaults. Presence tests use normalized `present(field(...))` expressions that distinguish absence from present-null. These are static candidate relations, not four executed requests or proof that every candidate is feasible.

The write uses `replace` under the public default for an ordinary unspecified write. This is a runtime abstraction, not a claim that the source explicitly says overwrite. No source append instruction was replaced. Unknown serialization did not block the write or return. The return's projected empty exit state does not mean the returned items were erased: the operand and operation evidence are saved.

The [independent source audit](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/010-source-audit/assessment.en.md) and [exact evidence](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/010-source-audit/evidence.json) record field identities, candidate bindings and source lines. These assistant criteria are not human gold or a general accuracy denominator.

## Remaining interface and DOE limitations

The first task-correspondence answer used `retained_only` for R8 without a required gap. The one structural correction repaired that row. The corrected response then exposed two further reference errors: R4/R6 `only_if` conditions target compute **output** slots at `ir_005` and `ir_010`, while the actual normalized presence expressions target those operations' **self** slots. The expressions exist; their target slots do not match. The two realization rows became explicit validation gaps after the correction budget was consumed. Separate valid operation-level demands remained available.

Final requirement expression status is six expressed, three partial and one retained-only. Thirteen applicable seed goals across nine requirements have nonempty derivation references. The tool has search-action, query and optional-field demands; the count write has both action and exact actual-total value demands. Two supported constraints, `at_most` and `requires_prior`, report satisfied within this declared model. Opaque response dependence does not establish that all request plaintext is contained in the response.

R8's deletion prohibition lacks an encoded constraint, although the selected graph independently contains no index.delete call. R10's returned value is preserved but its recipient is unspecified. Processing also retains source-unspecified deployment/transport and failure-path limits. These limits are not established source violations. The source review returned empty findings/objections, but the result remains diagnostic-only with incomplete annotation review; empty review findings do not remove the deterministic gaps.

There are zero sensitivity declarations and zero data comparisons. The frozen source supplies no affirmative sensitive category that this audit can show was omitted. Accordingly, zero comparisons is an allowed outcome for this source, while the sensitivity of unspecified concrete runtime values remains unestablished. There is no supported excess finding, contradicted excess finding, unresolved sensitive comparison or actionable reduction to count. That absence is not a no-excess verdict. The main residual layers are task-correspondence reference/constraint resolution and unspecified receiving boundaries, not propagation convergence or result publication.

## Actual calls, public tokens and time

| Call group | Starts | Input | Cached input subset | Output | Total |
|---|---:|---:|---:|---:|---:|
| Normal semantic stages | 7 | 154,187 | 86,016 | 18,718 | 172,905 |
| Structural corrections | 2 | 43,658 | 24,576 | 569 | 44,227 |
| Total | 9 | 197,845 | 110,592 | 19,287 | 217,132 |

Corrections were CFG and task-correspondence. Semantic repair requests and extra transport attempts were both zero. All nine final answers have complete public usage with distinct public thread/turn-or-order identities; unknown and partial final-response usage counts are zero. Provider-internal HTTP attempts and unreported internal failed-attempt usage remain unknown. Cached input is already included in input.

| Timing | Seconds |
|---|---:|
| Main analysis | 574.691 (9 min 34.69 s) |
| Public native start-to-finish span | 566.007 |
| Propagation compute / save / total | 0.367 / 1.690 / 2.739 |
| DOE load / compute / post-compute publication | 1.210 / 1.750 / 0.937 |
| DOE total | 4.059 |
| Sole matched replay, zero new starts | 21.729 |
| Controller wall including replay | 597.670 |

Component intervals are nested and nonadditive. Detailed observed stage intervals and category token costs are in [run-summary.json](run-summary.json). Parallel stages overlap. No monetary amount or hidden computation cost is inferred.

## Scope-aware comparison and receipts

Old v8 010 processed 19/23 generated IR, reached request/search, and blocked the count save and items return. It used 13 starts, 334,706 public tokens and 914.983 s. This fresh run reaches the save and return relationships with 9 starts, 217,132 tokens and 574.691 s. It is a broader and cheaper observed result for this sample; different generated graphs, fewer repair calls and partial DOE prevent assigning the change entirely to r3 or claiming a same-work backend speedup. Paused v9 has no terminal online result.

- [Structured assessment](run-summary.json), [mechanical evidence](mechanical-evidence.json).
- [Propagation records](propagation/records.json), [DOE result](doe/doe-result.json), [review](review/result.json).
- [Public metrics](metrics.json), [component timing](component-timing.json), [replay receipt](replay-check.json).

Implementation remained unchanged: r3 Python SHA `5ccbc1941be908ff20b15d7a56a631e678285b42a255031d29505ec6a0495637`, broader SHA `9ae31392bf97b0ae8c5ae75c48d1994e8b303b68cda6d532eb4b96f508c56703`. Source SHA is `66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c`. This report adds no calls, modified candidate, replay or Skill execution.
