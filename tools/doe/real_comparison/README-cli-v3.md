# Prospective option-A CLI-v3 engineering transport

This implementation is reviewable and tested offline. It does not adopt an
authorization, prepare an actual run, or dispatch a model request on import.
The stopped CLI-v2 run and its failed q001 remain unchanged. A new explicit
user decision is required before preparation.

The isolated `cli_adapter_v3.py` originally copied the v2 transport with a new
schema and one changed expected developer-input hash. As authorized on
2026-10-26, newly prepared requests also use `max` effort. Historical CLI-v2
implementation bytes and Ultra run records remain unchanged. The inventory at developer
message 0, part 3 must exactly match
`6a3705d1e55677d8620575fbe1ca0969b1e5e6e877f8ae56bc5766fc9f979372`,
the observed catalog including GitHub. The old 15-entry catalog is rejected.
There is no inventory normalization and no added CLI feature flag. The pinned
executable, base instructions, other developer segments, non-effort argv, complete stdin,
fresh-process requirements, usage accounting, budgets and stopping rules remain.

The separate `cli_amendment_v3.py` binds only v3 adapter/orchestration modules
and uses `calibration_cli_v3_` workflow identities. It preserves the earlier
v1 history and every existing file hash in the identified stopped v2 run. It
also checks that both original CLI-v2 implementation files retain their exact
bytes. No previous target response, workflow, formal approval or source-reference
confirmation is imported as a v3 result or authorization.

## Required new authorization

An actual adoption record must already exist before `prepare` is called. This
implementation validates and copies that record; it never generates a human
statement. A v2 adoption record is rejected even if it says `user_authorized`.

| Field | Required value |
|---|---|
| `schema_version` | `skillflow-real-comparison-cli-v3-authorization` |
| `state` | `adopted` |
| `user_authorized` | `true` |
| `selected_option` | `A_fixed_observed_inventory` |
| `proposal_sha256` | `777b2aa0a9335c5c37fe1e21b6f38c38af35fc8f5e501bb0d52fc0810a6ef85e` |
| `prior_dispatch_stop_sha256` | `482e051c7eae591cac61728279b48ee47a9f99e5cf4aee0d09c7f48aed9f2706` |
| `calibration_only` | `true` |
| `formal_dispatch_permitted` | `false` |
| `automatic_retry` | `false` |
| `user_confirmation.quotation` | The actual new explicit user confirmation |
| `user_confirmation.conversation_reference` | A reference locating that confirmation |

The supplied proposal and prior v2 dispatch-stop bytes must also match those
hashes. Missing or mismatched authorization is rejected before any new run
directory or calibration plan is created. These fields are a record-validation
contract, not independent proof that a supplied statement came from a human;
the supervising chat must ground the record in the real conversation.

Only after that new authorization may preparation copy the three complete
familiar source packages and freeze three fresh native workflow plans:
`gh-fix-ci`, `netlify-deploy`, and `transcribe`. Preparation makes zero target
calls. A future authorized invocation uses:

```text
python -m tools.doe.real_comparison.cli_amendment_v3 prepare --run-dir NEW_V3_RUN --original-run FROZEN_V1_RUN --prior-cli-run STOPPED_V2_RUN --proposal EXACT_REVIEWED_PROPOSAL_JSON --decision-record NEW_ACTUAL_USER_ADOPTION_JSON --executable INSPECTED_CODEX_EXE
```

The `worker`, `pending`, `dispatch-next`, `verify`, `summary`, and `replay`
commands retain the v2 command semantics in the new v3 module. Only an explicit
`dispatch-next` can start a target process. Every request is attempted once;
failure, unknown usage, drift or timeout retains the evidence and closes all
further dispatch. An existing workflow cannot be retried or replaced.

This run remains permanently calibration-only. Even a separate `gate.json`
claiming approval cannot permit formal dispatch. Technical conformance does
not establish semantic quality, DOE accuracy, or equivalence with the historical
harness. Any formal comparison still needs a separately frozen long-source
cohort, source references, real independent human confirmations and a formal
adapter/gate.

## Offline validation

```text
python -m pytest tests/doe/test_real_comparison_cli_adapter_v3.py tests/doe/test_real_comparison_cli_amendment_v3.py -q
```

The tests use fictional receipts, temporary source packages and explicit fake
process objects. They preserve multilingual input/reference coverage, prohibit
real subprocess/model calls, reject the old inventory and old authorization,
check exact history preservation, and exercise permanent formal/stop/no-retry
guards. Their fictional authorization records are never actual user consent.
