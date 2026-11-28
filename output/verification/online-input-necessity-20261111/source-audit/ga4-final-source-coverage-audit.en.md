# GA4 final source, coverage and correctness audit

**Closed result: failed during revision-processing; propagation and DOE did not run.**

The analysis ended at 20:02:05 China time on 2026-11-11, and the controller closed at 20:02:38 after its sole replay matched in 32.074 seconds with zero new native starts. That match reproduces the failed terminal result; it is not successful propagation or semantic validation.

## Selected artifacts and unfinished repair

| Artifact | Retained state | What it establishes |
|---|---|---|
| Initial Task | Selected; 61 declarations | Source-derived purpose artifact, with initial review objections |
| Initial CFG | Selected; 535 IR, 228 blocks, 206 edges | Source-corresponding representation only |
| Initial annotation | Selected diagnostic artifact; 531 modeled IR, 12 gaps including 4 unmodeled | Annotation content, not executed propagation |
| Initial necessity contracts | 45 compute, 0 tool; no output_parts | Submitted scope only; review marks 31 accepted, 5 rejected, 9 unresolved |
| Repaired Task | Completed but unselected; 68 declarations | Revised candidate only |
| Repaired CFG | Completed but unselected; 658 IR, 279 blocks, 259 edges | Repaired graph candidate only |
| Repaired processing | No complete answer; no accepted value | No completed repaired annotation or rereview |
| Propagation / demand / DOE | Not run | No processed-IR, boundary-demand, deletion or DOE result |

`selection.json` still identifies `task/task.json`, `graph/initial.json` and `annotation/manifest.json`. The selected graph is byte-identical to the initial graph. The repaired 658-IR graph must not be combined with the initial 531-entry annotation or described as 658 processed IR.

## Finite source coverage

Both the initial and repaired graphs represent all **13/13 explicit remote SDK call sites**, **25/25 saveResult call sites**, and **3/3 explicit URL loops** in the independently prepared original-source inventory. Mapped physical call lines match graph excerpts. All 25 internal save calls have no output, preserving the ignored helper return path. These counts exclude SDK internals, setup operations, arbitrary dynamic invocation counts and the unimplemented summary writer.

The initial crosswalk remains the selected graph crosswalk. Revised pointers are retained in their separate provisional file and apply only to the unselected wire graph. There is no propagation coverage denominator result: the engine was not run, so the report does not present an invented 0/535 or 658/658 completion score.

## Source-supported assessment

The initial representation preserves useful field relationships: separate dimensions/metrics projections; indexStatus-only consumption by the high-level status workflow; independent filename and saved-wrapper inputs; and validation truth tests rather than credential values. Those observations do not establish complete or minimum reverse demand. All remote calls lack input interface contracts in the selected initial annotation.

The initial review reports 39 findings and specifically rejects five supplied necessity claims: the original date label on a present object (two sites), a whole-array requirement for a variable slice, a whole URL value for its pathname, and a whole string for a leading-slash test. Nine contracts remain unresolved, including narrower Settings dependencies, error conversions and traversal relationships. The audit independently flagged the date-label and slice overstatements before reading that review. This provides traceable examples, not an accuracy rate or a complete contract audit.

The revised graph responds to source-review issues with explicit maps/filters, undefined predecessor values, module dependency entries, shell working-directory binding, and accumulator state inside protected URL updates. Its new analysis/save/read/Markdown nodes are explicitly documentary obligations. Because repaired processing failed, these changes have no completed annotation, propagation or final semantic review.

Actual source limitations remain unchanged: filters/orderBy are not applied; Search Console object endpoints pass through without calendar validation; ranking descriptions conflict; separate keyword/device reports do not establish a joint relation; bulk responses do not prove one row per supplied occurrence; operation matching is substring-based; and summary file/version selection and an implemented Markdown writer are absent or unspecified. Source-review repair changed analysis artifacts, not the Skill.

## Failure evidence and cost

The revision-processing native process reached the configured 2,700-second timeout with exit code 1 and no complete answer. The run recorded: `CLI produced no complete answer; this is not an eligible transient network retry`. Its public stdout contains four reconnect notices (2/5 through 5/5), including timeout, connection-reset and socket-access errors. The public cost audit records five reconnect notices across the entire run. These notices do not establish an exact internal HTTP-attempt count or the deeper network cause.

There were **12 native starts**: 7 normal, 2 structural corrections and 3 semantic-repair starts. Eleven requests have complete public counters totaling **1,919,852 known tokens** (1,649,821 input; 270,031 output). The failed revision-processing request has unknown usage, so this is not the complete token total or a provider bill. Outer retry starts were zero.

Frozen source, production snapshot, transport/helpers and executables passed the saved provenance checks; all original 16 source files remain unchanged. The independent cost audit is `../cost-provenance-audit/ga4-20261111T120314320227Z.json`.

## Evidence and boundary

`ga4-final-source-coverage-audit.json` contains the exact selected artifact hashes, source and graph crosswalks, failure receipt, known-cost fields and preserved provisional report hashes. Earlier audits remain unchanged.

This finite assistant-authored audit is not a human gold standard and supports no precision/recall, semantic-equivalence, complete DOE, minimality or absence-of-exposure claim. GA4 is closed and its sole replay is exhausted. The remaining authorized cases continue under the root-owned queue; no GA4 restart or production change is authorized by this report.
