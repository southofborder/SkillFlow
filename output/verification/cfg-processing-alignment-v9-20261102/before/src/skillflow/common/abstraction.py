"""Shared source-action granularity, without adding runtime observations."""

BOUNDARY_GRANULARITY = """SHARED ABSTRACTION GRANULARITY
Pure local calculations may remain opaque with their real inputs and possible
dependencies. Unknown input values, API content or computation details are not
by themselves unrepresentable behavior. Acquired content has its actual source;
it is not a calculation exhausted by request parameters.
Expose source-supported conditions that change acquisition, delivery, saving,
returned content or state versions. Prefer existing CFG branches for ordinary
conditional reads, optional saves, empty-input returns and conditional output.
Branch conditions consume actual operands; prose constraints do not execute them.
Keep source-supported loops and nested loops explicit in the CFG. Processing
declares predecessor merges, collection members and typed branch relations;
the program derives loop scopes and finite summaries. Do not unroll iterations,
invent loop-management tables, or use opaque compute for member selection.
Do not require line-by-line code expansion or an internal call stack. Do not
hide privacy-relevant conditional effects in one indivisible code black box.
A source-supported call-boundary summary may retain alternative outcomes and
named local state effects when exact internal execution is unnecessary. Preserve
request-before/after-failure differences, returned versions and receiving scopes.
An existing handle retains its creation-time provenance; a newly created handle
is a distinct value, not credential plaintext. Possible state effects do not
prove exact cache hits, creation counts, ordering or unconditional overwrites.
Separate interface acquisition from relevant initialization. An initialization
post-state is not the pre-state renamed; preserve its actual call origin and
known affected bindings without inventing library internals or source locations.
Keep genuine missing provenance local. Adjacency, filenames and shared labels
do not connect a saved result to an analysis invocation.
"""

NECESSITY_EXAMPLE = """RECEIVER-SPECIFIC NECESSITY EXAMPLE
A source returns and saves {rows, debugLog}, while its declared purpose requires
a table of row counts. Preserve both fields in actual returned/saved propagation.
Do not seed whole-input value solely because the implementation reads or returns
the object. Ground the table's required fields and structure at its own receiver.
If the source independently requires saving the complete raw response, retain
that whole-value requirement at that storage receiver. It does not transfer to
the summary receiver. An explicit complete-metadata requirement remains whole.
If the required field relation is absent, record that specific relation as a gap;
do not invent a selection operation or assert every opaque member is necessary.
"""
