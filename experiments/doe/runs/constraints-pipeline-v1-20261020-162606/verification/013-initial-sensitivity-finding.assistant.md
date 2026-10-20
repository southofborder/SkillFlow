# Initial 013 sensitivity finding: independent assistant assessment

This note audits the first semantic review only. It does not select, edit or predict the final repaired candidate. No model call or production change was made.

## Conclusion

The first finding is not substantiated as a missing sensitive-content route by the current backend. A declaration on a value obtained by an explicit `select_part` can already identify that exact field in the earlier observed parent. Adding a second declaration on the parent while retaining the selected-value declaration is therefore redundant in this case; it can duplicate declaration-specific result rows. This does not say that the original annotation is otherwise correct or that the credential exposure is excessive.

## Accepted inputs inspected

- [Initial review response](../cases/013/refinement/initial-review/calls/review/a001/response.json): first finding targets `ann_0062`, `ann_0087`, `ann_0088`, and `obs_0002`. It says that the existing selected-value declaration misses credential content in the earlier whole snapshot and requests an additional parent-field declaration.
- [Initial raw annotation](../cases/013/annotation/audit/raw-annotation.json), `/ir_semantics/ir_003`: `read` produces `environment_snapshot`; `select_part` selects `["FAST_KEY"]` into `fast_key`; the only sensitivity declaration binds `fast_key` at `path=[]` with category `credential`. The selection is explicit and retains the exact parent/part identity.

The source evidence can support classifying this field as a credential. It does not establish that two separate sensitivity declarations are required by the implementation.

## Backend evidence

- `src/skillflow/doe/sensitivity_engine.py:280`: known-part content creates both parent-to-part selection and part-to-parent embedding edges.
- `src/skillflow/doe/sensitivity_engine.py:289`: a selected Data value with `origin.part_of` also creates the reverse embedding edge to its exact parent.
- `src/skillflow/doe/sensitivity_engine.py:89`: `embed` prefixes the declared path and preserves the direct relationship; it does not expand the declaration to unrelated fields.
- `src/skillflow/doe/sensitivity_engine.py:44`: redundant routes of the same declaration can be suppressed, but distinct declarations are not merged.

A declaration is static analysis metadata, not a timed event that only becomes effective after its position in the response. The reverse embedding describes content identity in the original version; it is not a new model/tool read channel and does not authorize exposure of unrelated parent fields.

## Independent offline check

Used the existing synthetic helpers in `tests/doe/test_demand_engine.py:46` and `tests/doe/test_sensitivity_engine.py:12`, not a modified 013 candidate:

```python
values = fixture([
    {"op": "select_part", "input": inp(), "path": ["token"], "output": "token"}
], mode="model")
result = review(values, declarations((), value=local("token")))
```

The compiled record first observes the whole input at `op_ir_filter:e0:a0`, then selects the token at event 1. The single selected-value declaration produces one earlier whole-observation review with `path=["token"]`, `relation="direct"`, and an `embed` derivation. Its conclusion is `no_excess_established` because the independent fixture also retains the selected token through a task demand; this check concerns exposure coverage, not excess.

Adding a second declaration on the input at `["token"]` produced two rows at that same observed operation and same field, with distinct declaration IDs. Both were direct. This confirms the duplication risk of the review suggestion.

The pre-existing neutral-information regression `tests/doe/test_constraints_engine.py:549` separately covers a selected-child prohibition reaching an earlier whole model observation. It is supporting precedent, not the sensitivity-specific check above.

## Boundary of the assessment

This is a concrete counterexample to the reviewer's claimed omission mechanism. It does not downgrade the second finding about using a whole outcome reference as a transient Boolean classification, and does not claim a final 013 result. Any accepted repair, downstream demands, constraint checks and final DOE results must be assessed separately once saved. Historical responses and current accepted artifacts remain unchanged.
