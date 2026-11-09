# Independent review of offline material reuse

Date: 2026-11-02. Reviewer: `/root/material_reuse_review`.

**No unresolved blocking regression was found in the reviewed changes after the partial-mapping correction below.** This is a focused review of reuse and publication behavior, not a claim that the underlying semantic analysis is complete or that the real GA4 run is faster. The parent owner still performs the integration acceptance.

## Scope and baseline

The comparison used the exact pre-edit files under `output/verification/material-reuse-20261102/before/`, not Git HEAD. The nine reviewed production files are recorded with before/after SHA-256 values in `independent-reviewed-files.json`:

- `document_guided/fragments.py`, `annotation_wire.py`, and `online.py`;
- `propagation/contracts/references.py`, `propagation/runner.py`, and `propagation/loading.py`;
- `doe/formal_runner.py`, `demand_material.py`, and `sensitivity_material.py`.

The reviewer made no production edits. Verification used newly created synthetic material and injected clients. No real model call, Skill execution, historical run load, historical compilation, or historical replay was performed.

## Finding resolved during review

The initial saved-step reader required a nonempty `validation_gaps` value for every partial result. That rejected a legitimate partial task-correspondence result: removing an invalid demand can place the unresolved requirement gap in `realizations` while returning `validation_gaps: []`. The earlier loader accepted that result because it compared the stored list with the actual salvage result, rather than requiring truthiness.

The concrete synthetic example changes a correspondence record's operation path to `['segments', 99, 'ops', 0]`. Salvage retains a valid fragment with a requirement gap and an empty validation-gap list. The implementation owner corrected the saved-step check to require a list, including an empty list, while retaining the terminal structural-invalid and accepted-call consistency checks.

The reviewer added `tests/document_guided/test_partial_mapping_reuse.py`. It prepares a fresh source, sealed Task, processing step, and mapping step with injected clients. A zero-correction fixture budget triggers the terminal salvage directly. Both ordinary loading and explicit recomputation return the same partial mapping, preserve its requirement gap, and make no additional client call.

## Reuse boundaries checked

- Ordinary guided reads use saved compiled artifacts and their bound inputs, manifests, request artifacts, and dependencies. Explicit recomputation still reconstructs the response decisions and compilation. The legacy standalone path retains its validation behavior.
- Program assembly still binds all three semantic owners to the same source and CFG and binds task correspondence to the expected sealed Task and processing version. Projection reuse remains local to one assembly; there is no global or persistent cache.
- Sensitivity lowering retains the existing alias and candidate lowering logic. Reused scopes are derived from the same processing expansion; the comparison tests cover member/case scopes and summary aliases.
- Propagation publication reuses the already checked owner. The private annotation-reuse flag is not the default for raw callers; raw public material construction still compiles and checks correspondence. Publication still checks upstream identity and changed files.
- `_with_manifest` shares privately owned facts while all public mutable component properties continue returning detached values. It does not introduce a public mutable alias to data, records, receivers, or diagnostics.
- DOE publication returns its already computed and validated review. Ordinary external saved-result loading still validates its artifact and upstream bindings. Demand-material reuse checks canonical identity with the propagation owner's annotation, including type-sensitive changes such as `false` versus `0`.
- Target-index reuse is scoped to the current validation call. CFG target construction preserves the existing target entries while avoiding repeated global IR scans. No loop, data-version, receiver, occurrence, local-return, or demand-solving semantics were intentionally changed by these edits.

## Independent verification

The reviewer ran these five files together:

```text
tests/document_guided/test_partial_mapping_reuse.py
tests/document_guided/test_saved_material_reuse.py
tests/document_guided/test_fragment_reuse.py
tests/propagation/annotation/test_reference_index_reuse.py
tests/doe/test_verified_material_reuse.py
```

**23 tests passed in 58.54 seconds**, recorded in `independent-review-tests.xml`. The isolated partial-mapping regression also passed, recorded in `review-partial-mapping-test-v2.xml`.

For transparency, `review-partial-mapping-test.xml` preserves an earlier test-construction error: the first draft omitted the required prepared context. It failed before reaching the product behavior under review. The completed fixture uses real fresh preparation and passed; the setup failure was not deleted or presented as a product regression.

The focused tests check artifact/dependency mutation rejection, ordinary-read reuse, explicit reconstruction, fresh seven-call execution and zero-client-call replay, projection equivalence, retained local-scope diagnostics, raw-factory compilation, changed-upstream commit rejection, demand-candidate substitution rejection, and target-index reuse. These checks support the reviewed reuse change. They do not establish a new real-run speedup, coverage improvement, or accuracy gain.

## Supplement: legacy commit identity check

After the initial review, the implementation owner supplied one narrow correction in `propagation/runner.py`. The save path now passes the already loaded complete `upstream_identity` into `_check_annotation_unchanged`; the existing legacy branch compares that identity as well as the manifest and accepted-response hash. This restores detection of byte changes such as whitespace appended to legacy `result.json`, whose parsed semantic value may remain equal.

The reviewer checked the exact three changed locations. Reversing just these changes, with the original CRLF endings, reproduces the previously reviewed file SHA-256 exactly. The new reviewed SHA-256 is `adb83f6808f99711662acf61974bb96f5f731802a95f60b79743a537a32d5484`; both identities are retained in `independent-reviewed-files.json`.

This correction introduces no additional load, compilation, or semantic computation. The legacy branch already loaded the annotation for its commit check; it now compares one more field from that existing load. The guided branch is unchanged. Agent B's recorded `guided-legacy-commit-recheck.xml` was inspected: all eight tests passed, including six whitespace-mutation cases, the upstream-call commit check, and the guided reuse/load-count test. These eight results are attributed to Agent B and are separate from the reviewer's earlier 23-test execution. No further issue was found in this supplement.
