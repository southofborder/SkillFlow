# Initial 001 constraint-reference audit

This is an assistant's read-only audit of the first three completed annotation responses and subsequent transport failure for case 001 in `constraints-pipeline-v1-20261020-162606`. Case 001 has now stopped without a valid selected annotation. This is not a semantic gold standard or a completed three-case assessment. No candidate, frozen input, production source, prompt, or running protocol was changed. No additional model call was made for this audit.

## Observed responses

| Call | Candidate location | Actual reference and rejection |
|---|---|---|
| [a001](../cases/001/annotation/calls/annotation/a001/response.json) | `/realizations/4/constraints/0/condition` | The `operation_path` ended in `atomic_ops, 0, expression, expression`. The path points inside the expression wrapper and AST, not to an indexed operation target. The validator reported `constraint_reference` and `constraint_expression`. |
| [a002](../cases/001/annotation/calls/annotation/a002/response.json) | `/realizations/4/constraints/0/condition` | The replacement removed one suffix, leaving `atomic_ops, 0, expression`. This still is not an indexed operation target. The same two diagnostics remained. |
| [a003](../cases/001/annotation/calls/annotation/a003/response.json) | `/expressions/0/target` and `/realizations/4/constraints/0/condition` | The replacement copied the predicate to a top-level expression attached to the entire `ir_003` and referenced that IR. The validator reported unsupported expression-target capability and an element-scope mismatch. |

Exact saved diagnostics:

- [a001 validation](../cases/001/annotation/calls/annotation/a001/validation.json)
- [a002 validation](../cases/001/annotation/calls/annotation/a002/validation.json)
- [a003 validation](../cases/001/annotation/calls/annotation/a003/validation.json)

## Reference rule and the separate scope issue

An attached compute/filter expression is normalized under the **owning atomic operation's target**, with `slot={"kind":"self"}`. Its target is not the address of `expression` or its nested AST. This follows the operation-expression extraction in [joint.py](../../../../../src/skillflow/propagation/contracts/joint.py), particularly the `operation_target(ir_id, path)` assignment, and the actual indexed coordinates in [demand_index.py](../../../../../src/skillflow/propagation/contracts/demand_index.py).

For a001 and a002, removing the trailing `expression` components in memory resolves the owning `ir_003` filter operation. This observation is only a reference check; it does **not** produce a valid replacement constraint:

- The constraint declares element scope `ir_005`, `scope_path=["events",0]`.
- Its event is a delivery in that scope.
- The referenced predicate belongs to a different IR, `ir_003`, outside that element scope.
- [validate_constraints](../../../../../src/skillflow/propagation/contracts/constraints.py) requires the referenced event/expression to belong to the declared element scope. Merely correcting the path suffix therefore leaves a separate scope failure.

The a003 replacement does not solve that scope mismatch. In addition, [build_demand_target_index](../../../../../src/skillflow/propagation/contracts/demand_index.py) enables top-level CFG expression targets for actual control positions; an arbitrary whole non-dispatch IR does not become an expression target because it contains a filter in the annotation.

These are supported structural rejections. This audit found no evidence that these three particular responses were rejected because of a validator false positive. It also does not establish whether the underlying restriction can be represented completely within the current cross-scope capabilities.

## Prompt and diagnostic contribution

The [actual a001 prompt](../cases/001/annotation/calls/annotation/a001/prompt.txt) contains:

- `OnlyIf` and `OperationTarget` format entries at lines 45 and 48.
- The compute/filter expression-wrapper and top-level control distinction at line 100.
- The instruction that `only_if` references an existing condition expression at line 135.
- A complete `forbid_information` lesson starting at line 154.

It does not provide a concrete `only_if.condition` example showing the owner-operation target and the compatible element scope. The compact schema lists allowed target shapes, but cannot by itself communicate which target is the normalized expression owner.

The [a002 correction prompt](../cases/001/annotation/calls/annotation/a002/prompt.txt), line 147, sends both diagnostics but has `format_examples=[]`. The diagnostics contain the rejected candidate path and general messages; they do not include the current target, available expression-owner coordinates, or the scope distinction. Thus the model received insufficiently specific guidance to distinguish an AST address, its wrapper address, the owning atomic operation, and a top-level control target.

The observed failure sequence is consistent with both model reference misuse and an instructional/diagnostic gap. It does not support blaming JSON parsing or claiming that prompt length alone caused the errors.

## Actual recorded cost so far

These are provider-reported token totals for the three completed requests, each with one observed HTTP attempt and no missing usage. Output tokens include provider reasoning; reasoning is not added again.

| Call | Prompt characters / UTF-8 bytes | Input tokens | Output tokens | Total tokens | Call wall seconds |
|---|---:|---:|---:|---:|---:|
| a001, initial annotation | 89,198 / 89,198 | 20,541 | 60,666 | 81,207 | 322.109513 |
| a002, structural correction | 86,293 / 86,293 | 19,927 | 35,423 | 55,350 | 196.365179 |
| a003, structural correction | 86,280 / 86,280 | 19,925 | 23,960 | 43,885 | 124.971138 |

The two completed corrections alone account for 99,235 reported tokens and 321.336317 seconds of call wall time. This is not the completed case cost: the failed a004 request has no reported usage, and Task extraction and local stage work are outside this subtotal. The formal metrics collector remains authoritative for the final run totals and replay integrity.

## Subsequent a004 transport failure

[The case result](../cases/001/result.json) records `status=failed`, `stage=annotation`, and `Joint annotation failed: IncompleteRead(0 bytes read)`. There is no selected annotation, review, propagation, or DOE result.

The distinction is:

- **Three completed, structurally invalid annotation responses:** initial a001, correction a002, correction a003.
- **Three structural-correction requests:** a002, a003, a004. Only the first two completed with a candidate and reported usage.
- **a004 execution failure:** an HTTP 200 response began streaming, but ended with `IncompleteRead` before any complete JSON candidate was accepted. The recorded stream has no final content, finish reason, or completion marker. This is a transport failure, not a fourth observed structural error or a semantic-review rejection.
- a004 has one observed HTTP attempt, no HTTP retry, and 112.646723 seconds of call wall time. Its provider usage is absent and remains **unknown**, not zero. Stream bytes and events do not supply a token estimate.

The whole case records five logical calls: one completed Task extraction and four annotation-stage requests, including the three correction requests. It correctly stopped rather than selecting an invalid response or falling back to a historical successful analysis.

## Execution boundary

The existing unlimited structural-correction protocol was not capped or changed; its independent transport-failure stopping rule ended case 001. Case 010 subsequently started. This audit does not auto-correct the reference, move expressions, change scope, remove the constraint, or supply a semantic answer to a running model. Any later experiment requires its own explicit execution identity; this failed case has no final accepted material to semantically assess.
