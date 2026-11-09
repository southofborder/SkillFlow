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
Acquire public entry parameters from explicit context keys. At an internal call
site, summarize its real arguments, returned version and boundary effects there;
a callee name, metadata parameter list or disconnected function body supplies no
caller inputs or returns. Do not replace these relations with an empty binder.
Real zero-argument calls, constants and source expressions remain valid; opaque
normalization or serialization details alone do not stop a supported boundary.
Keep source-supported loops and nested loops explicit in the CFG. Processing
declares predecessor merges, collection members and typed branch relations;
the program derives loop scopes and finite summaries. Do not unroll iterations,
invent loop-management tables, or use opaque compute for member selection.
For collection traversal, a header dispatch consumes the actual collection and
uses branch(predicate=has_member). Its true body obtains member; member produces
the current element only, not a second Boolean. The backedge returns to the
header and the false edge exits. Split multiway decisions into binary dispatches
with actual operands; each guarded dispatch has at most two distinct successors.
Do not require line-by-line code expansion or an internal call stack. Do not
hide privacy-relevant conditional effects in one indivisible code black box.
A source-supported call-boundary summary may retain alternative outcomes and
named local state effects when exact internal execution is unnecessary. Preserve
request-before/after-failure differences, returned versions and receiving scopes.
Normal results and actual caught exceptions have distinct sources; a successful
response is not an exception value. Merge alternatives by their real predecessors.
An existing handle retains its creation-time provenance; a newly created handle
is a distinct value, not credential plaintext. Possible state effects do not
prove exact cache hits, creation counts, ordering or unconditional overwrites.
Separate interface acquisition from relevant initialization. An initialization
post-state is not the pre-state renamed; preserve its actual call origin and
known affected bindings without inventing library internals or source locations.
Ordinary unspecified save/write uses replace as a runtime abstraction convention,
not a source quotation. Explicit source append, delete or other supported update
semantics take precedence. Save the actual response/result version, not its
request arguments merely because they are available at the caller.
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
