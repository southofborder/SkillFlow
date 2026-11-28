# Proposed bounded diagnostics for rejected processing wire JSON

Proposal only, based on current-run processing a001. No implementation, test,
validator, replay or additional model request was performed for this note.

Yes: a read-only, lossless object-pair diagnostic pass can report the duplicate
tables and independent wire grammar violations together, within the existing
single-correction budget. It must enrich rejection evidence, never create an
alternative accepted candidate.

The actual a001 has one supported format declaration, two root `shared_values`
members, 266 and 310 mnemonic definition names, and 81 unequal values among their
241 overlapping names. The current strict parser stops at the first duplicate
member. Consequently a002 receives that one error without the already observable
identifier mismatch. A pair-preserving scan could expose both error families in
that same correction request, without deciding which table the model intended.

The narrow proposed flow is:

1. Keep the ordinary strict parser and its primary rejection authoritative.
   For a rejected response with a uniquely identifiable supported processing
   envelope, optionally scan the same immutable raw text into bounded ordered
   object pairs with raw character spans. No dictionary conversion, last-wins
   choice, table merging, name rewriting or reference expansion is allowed.
2. Check only facts independent of choosing between duplicate values: duplicate
   object members and their occurrences; each actual definition name against
   `v(?:0|[1-9][0-9]*)`; locally malformed reference/escape marker shapes; and
   reference-name syntax implied by that same identifier grammar. Reuse the
   codec's grammar declarations so these checks cannot define a competing wire
   language. Respect the literal-object grammar when examining encoded children.
3. Attach supplemental raw-wire diagnostics to the original rejection. Identify
   each table by root-member occurrence plus raw span, not merely the ambiguous
   pointer `/shared_values`. Bind locations to the raw-response hash and declare
   their offset unit. Keep the logical diagnostic path at the rejected root;
   raw-wire locations are context, not IR pointers or record-replacement targets.
4. Request one complete replacement with the original complete source, CFG,
   runtime contract and exact rejected raw candidate. Continue the same strict
   parser, expansion and ordinary validators for the replacement. There is no
   extra model call, correction allowance, worker or semantic-review stage.

For this response the grouped correction could say: “Root `shared_values`
occurs twice; return exactly one table. The first table has 266 invalid definition
names and the second has 310; all names and their references must use the explicit
`vN` grammar. Representative raw locations follow. The complete original response
is below. Return a complete valid replacement; the program has not selected or
merged either table.” It may also give a few exact invalid-reference examples.
These counts include separate occurrences in both rejected tables, not 576
distinct definitions in an accepted fragment.

Bound the scanner's raw length, nodes, nesting and work before allocating a full
tree; never expand references. Bound displayed diagnostic families and example
locations, with deterministic ordering, exact counts and an explicit indication
of how much raw text was scanned. On scan limits or unrecoverable JSON syntax,
retain the primary error, state the precise diagnostic-coverage limit and use the
unchanged full replacement fallback. Do not infer that unscanned content is
valid. The complete raw candidate and complete source remain in correction input;
bounded diagnostic examples do not truncate either. A bounded local inventory
may preserve additional locations in the audit without sending thousands of
repeated errors to the model.

Do not run fragment/schema/contract validation against this ambiguous tree, or
claim resolved references, field coverage, expansion size, cyclicity or semantic
sufficiency. In particular, membership in a union of the two tables does not
establish a valid reference. Checks that require one intended definition graph
must wait for a strict, unique replacement. The scan must not invoke salvage or
enable local record correction for the invalid envelope.

This complements centralized complete grammar and payload-first/single-final-
table guidance. Guidance prevents foreseeable mistakes before generation and
should be used in initial, local correction, full fallback and revision prompts.
The diagnostic pass helps the one allowed correction repair multiple definite
representation mistakes at once. Neither guarantees semantic acceptance or less
elapsed time. The simpler priority is explicit shared grammar and generation
order; add the bounded pass only with offline tests proving strict rejection,
raw immutability, occurrence-accurate locations, deterministic grouping, limit
fallback, literal escaping, and unchanged call counts and validation boundaries.
