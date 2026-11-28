# Shared output grammar and bounded raw diagnostics

Implemented in `fragment_wire.py` and the new
`processing_wire_diagnostics.py`; fragment/prompt integration is owned separately
by the root agent. The accepted wire identity remains
`skillflow-processing-json-v1`, and the existing strict expansion language has
not changed.

`DEFINITION_NAME_PATTERN`, `WIRE_ROOT_FIELDS`, `WIRE_MARKERS` and
`valid_definition_name()` centralize existing grammar. `output_wire_instructions()`
now explicitly covers exact root/member uniqueness, one final definition table,
the exact vN identifier pattern, reference and literal escape forms, unused
definitions, finite acyclic expansion, independent copies and unchanged complete
coverage. Initial/full/revision fragments are distinguished from explicitly
requested complete local replacement objects and their post-merge coverage
checks. `output_wire_example()` returns a valid fresh payload-first object with
forward/nested references and a literal escape; its explanatory payload is not a
substitute for the required fragment schema. The same instruction function can
be appended to custom correction prompts without trusting marker text in source.

Integration API:

- `scan_processing_wire(raw) -> dict`: bounded supplemental evidence only. It
  returns no parsed candidate and makes no acceptance decision.
- `processing_wire_diagnostics(raw) -> list[dict]`: zero or one root-only
  `processing_wire_raw_diagnostics` row. Call only after strict processing
  parsing/expansion rejects the response; preserve the primary diagnostic first.
  Its `context.raw_wire_scan` carries grouped evidence and diagnostic coverage.
- Non-string inputs yield no supplemental diagnostic; no raw identity is
  invented by serializing a dictionary that has already lost duplicate members.

The reader keeps an ordered pair tree and bounded source positions, never a
last-wins or merged object. It checks JSON member duplicates and independent
local wire-shape facts. Only a unique supported format declaration enables wire
name/marker checks. Every actual definition-table occurrence is inspected
independently; no intended table is chosen. Literal pair keys remain data, while
their encoded values are checked. Reference resolution, cycle analysis, expanded
payload size, fragment/schema checks and semantic validation are deliberately
absent. A scan with no findings can still describe a response rejected by the
authoritative codec, for example a missing reference or cycle.

Reports bind exact raw text SHA-256 and zero-based, end-exclusive Unicode
code-point spans. Occurrence paths use object member indexes and one-based
same-key occurrence numbers, or array indexes. Duplicate examples also identify
the first occurrence span. These are raw-wire coordinates, never expanded IR
pointers. SHA-256 uses UTF-8, with explicitly labeled surrogate-pass handling for
an unpaired surrogate that cannot occur in ordinary valid UTF-8 delivery. The
original raw string is never mutated or included as a diagnostic replacement.

The diagnostic scan is capped at 2 Mi characters, 100,000 nodes and 96 nesting
levels before tree allocations. Every group has an exact complete-scan count,
at most three examples and an explicit undisplayed count; aggregate serialized
examples are capped at 12,000 characters. Long member previews are independently
bounded. The complete candidate/source belong to the existing correction prompt,
not these bounded examples. Invalid syntax or resource limits produce explicit
incomplete coverage and preserve the original strict rejection/full replacement.
An allocation failure in the supplemental parser cannot replace the primary
duplicate-key rejection. These limits affect diagnostics only, not the strict
acceptance grammar or any request budget.

The new synthetic regression file is
`tests/document_guided/test_processing_wire_raw_diagnostics.py`. It reproduces
the observed duplicate-table shape without importing or executing any historical
answer. It covers identical/disjoint/unequal duplicate tables, simultaneous name
and reference violations, exact Unicode/escaped-name occurrences, local marker
forms, literal escapes, unused definitions, no resolution/acceptance, bounded
counts/examples, malformed syntax, input/node/depth limits, resource failure and
the unchanged strict codec. Initial receipt `raw-wire-diagnostics-01.xml` passed
35 cases. `raw-wire-compatibility-01.xml` preserved 72 passes and one existing
assertion failure: a test expected the old custom-prompt suffix to stay exactly
equal, whereas the authorized integration intentionally appends the complete
wire grammar. The root owns its precise expectation update. Later receipts
provide final test totals; this note does not erase the original failure.

No model, Skill, historical replay or historical validation was invoked. The
prior closed run/report files remain outside these edits.
