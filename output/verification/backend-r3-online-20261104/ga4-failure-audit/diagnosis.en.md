# GA4 processing failure: omitted optional case segments

The immediate trigger is a **program defect handling a permitted optional-field omission**. The processing answer omits `segments` in three error candidates. The emitted schema permits this, but the expansion code later indexes that missing key directly. This finding does **not** establish that the entire raw answer would compile or pass later reference, semantic or source checks after that defect is corrected.

The audited run is `experiments/doe/runs/document-guided-ga4-backend-r3-high-20261104-132226`. It closed failed at processing with `KeyError: 'segments'`. The processing response chain records one `execution_error` attempt, no accepted processing answer, and an unspent limit of one processing correction. Propagation and DOE were not reached. The already recorded replay matched that failed outcome with zero new native starts; this audit did not execute another replay.

## Exact answer shape

Of 22 bounded case candidates in the saved processing answer, three omit `segments`:

- `/ir_semantics/ir_027/segments/0/cases/2`
- `/ir_semantics/ir_029/segments/0/cases/2`
- `/ir_semantics/ir_031/segments/0/cases/2`

The first exact case excerpt is:

```json
{
  "name": "failure",
  "phase": "local_error",
  "disposition": "throw",
  "condition": "On a cache miss, validation or construction throws; no successful new-handle assignment follows."
}
```

This is an excerpt of the answer, not a standalone complete processing response. Its containing `ir_027` summary has two returning candidates and output `handle`; the throwing candidate has no normal yield. The IR supplies inherited source evidence from `skill/scripts/src/core/client.ts`, lines 23-42. The other two omissions have the same local-error/throw shape.

The saved processing prompt at line 5062 marks the field as `"segments"?`. In the frozen source, `ProcessingCase.segments` is `Field(default_factory=list)` at `document_guided/fragments.py:70-72`. Its base `FlatCase.segments` at `document_guided/annotation_wire.py:132-133` explicitly documents that it may be omitted or supplied as an empty list. Therefore this omission is not itself malformed model output.

## Source-derived failure path

`online.validate_step` at `online.py:202-207` delegates processing to `fragments.validate_fragment`. The fragment parser validates the typed form but preserves the submitted dictionary at `fragments.py:179-186`. Processing validation then enters the flat expansion, either through the direct branch at `fragments.py:380` or the diagnostic projection at `fragments.py:396`.

Inside `annotation_wire._expand`, each typed IR is serialized with `exclude_unset=True` at `annotation_wire.py:493`. That serialization removes defaulted fields that the answer did not explicitly supply, so the case's typed empty-list default is absent again. The nested `model_evidence` traversal then executes `case["segments"]` at **`annotation_wire.py:501`**. It encounters an omitted key before the later case-emission logic. This is the source-derived failure location; the saved execution-error receipt contains the exception type/message rather than a Python traceback, and no production function was re-executed during this audit.

The same assumption also appears in case emission at `annotation_wire.py:536`, `:541`, and `:552`. Fixing only the first traversal would expose another direct-key read. The fixture/projection helper `fragments.split_fragments` repeats it at `fragments.py:520`, although that helper is not the current processing-stage failure path.

All four relevant source files—`annotation_wire.py`, `fragments.py`, `online.py`, and `common/structural_correction.py`—are byte-identical among the current workspace, this run's frozen implementation, and the paused v9 implementation snapshot. In particular, `fragments.py` has SHA-256 `fa91135cbcb24d2dda3d7de9bf8e1258b20370b55c019c89fedbc9aa34dab64c` in all three. This is a pre-existing interface-handling defect exposed by the new answer, rather than a changed r3 propagation/DOE implementation path.

## Why processing correction was not used

`ResponseChain.run` invokes the validator at `common/structural_correction.py:528`. Only `StructuralValidationError` enters the bounded correction branch at lines 529-541. A `KeyError` instead enters the generic exception branch at lines 546-549, which records `execution_error`, finalizes the response chain, and rethrows. The saved `steps/processing/calls/a001/validation.json` and `chain.json` show exactly that outcome.

The one correction reported for the run belongs to Task: Task attempt 1 was structurally invalid and attempt 2 was accepted. Correction limits are per stage; that Task correction did not consume processing's allowance. `online._run_candidate` only attempts partial-record salvage after `StructuralCorrectionLimitReached` (`online.py:152-165`), so it does not salvage this implementation exception either. Treating arbitrary implementation errors as model-correction requests would be the wrong ownership change.

## Minimal future correction and evidence limit

After the active frozen batch is closed and a code change is authorized, honor the existing empty default at every case-segment consumer in the expansion path. Preserve the original submitted answer and its omission; normalize only the program-owned working view or use the field's empty default consistently when reading. Apply the same handling to `split_fragments`. There is no need to change the model schema, spend another model request to insert `[]`, or broaden the generic correction catch.

Focused future checks should cover omitted versus explicit-empty segments for both returning-existing-value and throwing candidates, at top level and inside `for_each`, and confirm that separate genuine validation errors still reach the existing structural-correction path. The current interface test at `tests/document_guided/test_interface_contract.py:23-37` checks explicit-empty segments with `FlatCase.model_validate`; it does not exercise omitted segments through this expander. No tests were added or run in this audit.

`evidence.json` preserves the exact three excerpts, emitted schema line, response hashes, source comparisons and saved processing failure chain. `minimal-raw-case.json` contains the first excerpt and its JSON pointer. Only those separate audit files were written; production code, prompts and run artifacts remain untouched.
