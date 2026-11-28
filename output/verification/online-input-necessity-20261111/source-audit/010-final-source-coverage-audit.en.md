# 010 closed source, coverage and necessity audit

The controller closed **partial** on 2026-11-11 at 20:34 China time. All **20/20 generated IRs** propagated. The selected annotation is `revision/annotation`; Task and CFG remain the initial versions. Demand and DOE are partial. The finite source comparison establishes a source-review error concerning `if_present`; it does not establish a defect in the source Skill.

This audit reads the original three-file source package, its byte-identical staged copy, the nine prewritten source expectations, final selected materials and frozen implementation. No model, Skill, replay or propagation was run, and no running pipeline received audit feedback.

## Source and generated coverage

The selected CFG has 20 instructions, eight blocks and nine edges. Each of its four normal paths contains one `index.search`, one write of `response.total` to `count.txt`, and one return of the complete `response.items`. The source requires unchanged query and optional values, independent omission of absent `from_date` and `limit`, no normalization/validation step, and no `index.delete` call. These sites remain represented in selected processing. All 20 entries are modeled, with no processing gap. The two computations have exact expressions; there is one authored tool contract compiled into its paired delivery and acquisition contracts.

The complete items field is an explicit output obligation, so item-member narrowing is not supported by this source. The other output uses only total. No server-side projection capability is established. No actual request.json instance is provided, so the audit establishes no concrete missing or mistyped field.

## Incorrect rejection of optional fields

Both selected contracts require `value/query`, `value/from_date` with `if_present=true`, and `value/limit` with `if_present=true`, with an independent remainder. Their physical evidence is `references/workflow.md:7-19` and `query.yaml:1-3`. The final review rejects both on the claim that the contracts do not preserve optional presence or absence (`revision/review/result.json`, `/review/findings/0` and `/review/input_contract_checks/0-1`). The initial review contains the same objection; all original review and repair materials remain preserved.

That objection conflicts with the frozen implementation. In `implementation-snapshot/src/skillflow/doe/demand_engine.py:248-252`, `if_present` adds a presence demand before skipping a value known absent. Lines 253-257 avoid reporting an absent optional value as missing required input. The frozen processing instructions explicitly state this meaning in `implementation-snapshot/src/skillflow/document_guided/annotation_wire.py:50-51`. A separate presence selector is redundant for this flag. The rejection is an independent review error, not evidence that the Skill or these optional-field declarations are wrong.

The actual run honors the rejected receipt. It produces five `input_contract_rejected` diagnostics across the search action and the total/items response obligations. It does not apply the accepted optional-field transfer for these rejected contracts. This audit does not approve the receipt retroactively or calculate a hypothetical corrected result.

## Receipt and necessity result

All selected file pins, canonical source/CFG/annotation/contract bindings, receipt and review checksums, exact two-contract check coverage, and the demand-to-receipt link match. The DOE receipt copy is byte-identical. These checks establish provenance, not correct review reasoning. The receipt identity is `eeb06d6c7896218f97404272bd9cf913ee4fc47c4b29c004de97262550086db9`.

The saved demand has 67 input assessments (38 operation inputs, 27 IR inputs and two acquisition outputs), containing **340 required, 201 unresolved and zero deletable range rows**. These are contextual records, not distinct-field counts. Zero deletable rows is not proof that every input is necessary. In addition to the five rejected-contract diagnostics, the source prohibition of `index.delete` has `unbound_requirement` and `requirement_expression_gap`: the supported mapping cannot bind a zero-attempt constraint to an absent event and retains a global limitation. Correcting the review alone is therefore not shown to make this result complete.

All 15 modeled sink positions are covered. The 135 data comparisons report `no_excess_established` with unresolved-analysis reasons; that is not a safe verdict or evidence of removable content. The two optional-inclusion constraints return `potential_violation` in the abstract model; their own reasons explicitly deny an assertion of feasibility or actual execution. The source and generated branches retain presence guards, so these statuses do not establish a source violation. The single-call and write-after-response constraints are satisfied within the supported model.

## Closure and cost

The controller took 923.444475 seconds for analysis. Its sole replay matched in 6.738536 seconds with zero new native starts. The independent saved cost audit is verified: **11 native starts** (seven normal plus four semantic repair), all 11 with complete public usage; **316,571 public tokens** (284,886 input and 31,685 output). One internal reconnect notice was observed, with zero outer network retry launches. Public counters do not establish internal HTTP-attempt counts or provider billing.

The JSON companion contains the nine-expectation crosswalk, exact graph/processing/review pointers, physical source references, receipt checks, full diagnostics and SHA-256 hashes for every cited material. This finite audit establishes source-site representation and one review error. It does not establish general DOE accuracy, absence of excess, or complete semantic equivalence.

## Selected artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| `task/task.json` | `d9205a1bc51bc3234757605817f724dae13beff45bc6f5fa50a25a8ef37c936d` |
| `graph/initial.json` | `c4e570d16c7f95d8e3cc4f8f6c76443e1048f0b48595262f0d78247a6c972e44` |
| `steps/revision-processing/value.json` | `644bb8b0aa3b71c2f0b21452166a7591b3b8b21ea3d518cee35eacdad0178065` |
| `revision/annotation/audit/compiled-response.json` | `1cc2b974eeb997c1b4c1591877fbfc8c46839ca84ee0139f5b3dd5fa947b8f4d` |
| `revision/review/result.json` | `95a4e536b68c3cddbce5baa2cb80836789b6ecd62904cafb543aca4c121dae74` |
| `audit/input-contract-review.json` | `1ef386e5c6f481accdca70bac88b7957075f180dbb9c473bed8ad9d9cd5e5113` |
| `propagation/records.json` | `9b242e979ef87b10330d8f2b0ba853293efc23cce730b4d2b8392826f776a8a0` |
| `doe/audit/demand-support.json` | `55c44c03afae434f1c400702536ab6f380c3aae31f94015bda80dcbcf7ec8870` |
| `doe/doe-result.json` | `512769998d785736527014de8222bc02372f3c7c78d0470a7e9f458786ec5705` |

The JSON audit SHA-256 is `3073ea86dec1b0631eab20f46c0ab3a40f81f49d3d0a71810d006254afdcfdd8`. Original provisional files and run records were not changed.
