# Handoff and Build Review

Scope: turning a design into something an engineer can build without guessing, and checking what came back. The async review rituals and redline conventions as a team process are `design-handoff`; this is the spec content and the review pass.

**Contents:** [What a Spec Contains](#what-a-spec-contains) · [Spec by Token, Not by Pixel](#spec-by-token-not-by-pixel) · [The Content Cases](#the-content-cases) · [Annotating Behavior](#annotating-behavior) · [Handoff Is a Conversation](#handoff-is-a-conversation) · [Reviewing the Build](#reviewing-the-build) · [Design Drift](#design-drift) · [When Reality Wins](#when-reality-wins) · [Write It Down](#write-it-down)

**Before writing a spec**, read `## Surfaces` and `## Token Sets` in `~/Clawic/data/designer/memory.md` and open any `artifacts/spec-*.md` the `## Boxes` index names for this component or surface. A spec that contradicts the existing one produces two implementations, and the second one is always the one that ships.

## What a Spec Contains

Anything absent is invented by whoever builds it, and they will invent it under time pressure:

1. **Purpose** — what this is for and when not to use it
2. **Anatomy** — the parts, named the way the component library names them
3. **Every state** from the matrix in `components.md`, or an explicit "n/a"
4. **Tokens** — every color, space, size, radius, shadow, duration and easing by token name
5. **Breakpoint behavior** — what changes and at which width, or which container width
6. **Content cases** — longest, shortest, empty, error, and a long-locale translation
7. **Motion** — trigger, property, duration, easing, reduced-motion alternative (`motion.md`)
8. **Accessibility annotations** — heading levels, reading and tab order, accessible names, alt text, focus behavior, live regions (`accessibility.md`)
9. **Copy** — the actual strings, including error and empty text (`copy.md`)
10. **Version and date**, plus the design-system version it was built against

A spec that fits on one page for a simple component is correct; length is not the measure. Completeness against this list is.

## Spec by Token, Not by Pixel

Redlining measurements is obsolete in any product with a token set, and actively harmful: an engineer given `#2563EB` will hardcode `#2563EB`, and that hex becomes technical debt the day the theme changes.

| Do not write | Write |
|---|---|
| `padding: 16px` | `space-md` |
| `#2563EB` | `color-action` |
| `18px, 600 weight` | `text-heading-sm` |
| `border-radius: 6px` | `radius-control` |
| `0 2px 8px rgba(0,0,0,0.12)` | `elevation-raised` |
| `300ms ease-in-out` | `motion-duration-standard`, `motion-ease-standard` |

Give the raw value **only** where no token exists — and then say so explicitly ("no token: one-off, do not reuse") or propose the new token (`tokens.md`). An unlabelled raw value is indistinguishable from an oversight.

Measurements still matter for **relationships the tokens do not encode**: which element is fixed and which is fluid, what stretches, what truncates, what wraps, what has a minimum or maximum width. That is the part engineers genuinely cannot infer.

## The Content Cases

The single highest-yield section of a spec, because a design is only ever drawn with one content length:

| Case | Question the spec must answer |
|---|---|
| Longest realistic string | Wrap, truncate with ellipsis, or expand the container? If truncate, is there a tooltip or a title? |
| Shortest / one character | Does the layout collapse or keep a minimum? |
| Empty | Which of the four empty states applies (`components.md`)? |
| Zero, one, many | `0 items`, `1 item`, `2 items` — all three exist |
| Very large numbers | `1,204,382` — does the column still fit? Is it abbreviated, and at what threshold? |
| Missing optional data | No avatar, no description, no date — is there a placeholder or does the row reshape? |
| Long unbroken string | A URL or a token with no spaces — the wrapping rule |
| Translated — short labels can run 1.5-2× longer (`copy.md`) | Which element absorbs the growth, and what gives way |
| RTL | Which elements mirror and which do not (`typography.md`) |
| Slow or failed load | Skeleton shape, error state, retry path |

Fill the design with the ugliest realistic data before handing it over. Real data is longer, emptier and stranger than any placeholder, and the mockup that only works with pretty data is a mockup that will be renegotiated during the build.

## Annotating Behavior

Static frames cannot express these, and they are always someone's assumption:

- **Focus order**, numbered, wherever it is not simply top-to-bottom
- **Scroll behavior**: what is sticky, what scrolls inside its own container, what happens at the top and bottom
- **Keyboard**: what Enter, Escape, Space and arrow keys do in composite widgets
- **Optimistic vs pending**: does the UI update before the server confirms, and what happens on failure (`components.md`)
- **Debounce and throttle** on search, autosave and validation, with the interval
- **Persistence**: what survives a refresh, what survives navigation, what is lost
- **Permissions**: what a user without a given right sees — hidden, disabled, or an explanation
- **Error recovery**: exactly what the user does after each error, including whether their input survives

## Handoff Is a Conversation

- **Involve engineering before the design is finished.** A feasibility objection raised at a sketch costs an hour; the same objection at handoff costs a redesign. This is the highest-return habit in the whole process.
- **Walk the spec together once**, live or recorded. Ten minutes of narration surfaces more misunderstandings than any document review.
- **Ask what is expensive.** Engineers routinely know that one detail costs three days and that an equivalent alternative costs three hours. You cannot make that trade if you never ask.
- **Name a single owner for questions during the build** and answer within a working day. An unanswered question becomes a decision made without you.
- **Version the spec, and mark changes visibly.** A silently edited spec means half the team builds the previous one.
- **The prototype is not the spec.** It shows intent; the written spec is the contract. Anything only visible in a prototype gets lost.

## Reviewing the Build

Review against the spec and the annotations, not against the pixels. Order matters — do the cheap structural checks first:

1. **Keyboard pass**, no mouse: reach everything, see focus everywhere, escape from everything (`accessibility.md`)
2. **Compute contrast** on the built product; implementations shift colors through opacity, overlays and theme layers
3. **Content cases**: paste the longest string, empty the list, force the error, switch the locale
4. **Responsive**: 320px, the widest supported, and the width between the two busiest breakpoints
5. **States**: hover, focus-visible, active, disabled, loading, error, selected — click into each
6. **Themes**: dark mode, and both at the OS font-scaling setting one step up
7. **Motion**: durations, reduced-motion preference, no animation on layout properties
8. **Only then** the visual comparison, at 100% zoom, against the spec's token values

Report as a severity-ranked list with the token or spec line each item violates — not a screenshot with red circles. `Critical / Serious / Moderate / Minor`, same scale as `research.md`, so the two feed one backlog.

## Design Drift

Every product diverges from its design. Drift is managed, not prevented:

- **Run the check on a cadence**, not on outrage. A quarterly pass over the main flows, recorded in `## Due`, catches drift while it is still cheap.
- **Count hardcoded values** in the codebase (`tokens.md`): the count going up is drift with a number attached, which is the only version anyone acts on.
- **Every deviation is either a bug or a decision.** Decide which, in writing. Undeclared deviations accumulate until the design file is fiction and everyone stops opening it.
- **A deviation that is better than the design becomes the design** — update the spec and the component, and say thank you.
- **A component that was detached in the design tool** is the same signal from the other direction: the library did not fit, and the reason is a real requirement (`tokens.md`).

## When Reality Wins

The build reveals things the design could not:

- **A performance cost** — an effect that is beautiful and drops frames. Take the cheaper effect; a smooth ordinary transition beats a stuttering exquisite one every time.
- **A platform constraint** — the OS control cannot be styled that way. Use the platform control (`mobile.md`); fighting it produces something that behaves wrongly in ways users notice and cannot name.
- **A data reality** — the field is 200 characters, not 40; the list is usually empty; the API cannot supply that value. Redesign for the data, not for the mock.
- **A timeline reality** — cut scope, not quality. Ship fewer states fully specified rather than all of them half-built, and write down what was deferred so it is a decision rather than an omission.

## Write It Down

- **The spec itself** → `artifacts/spec-<component-or-surface>.md`, its own file from the first version, with its `## Boxes` line and a read condition naming the component. Carry the version and date at the top; supersede in place rather than creating `spec-v2`.
- **The surface, its framework, who implements it, and the design-system version in force** → its row in `## Surfaces` of `~/Clawic/data/designer/memory.md`.
- **A build review and its severity-ranked result** → a row in `~/Clawic/data/designer/sessions/<year>.md`, with the drift count if one was measured; the full list goes in the spec artifact or its own `artifacts/review-<surface>-<yyyy-mm>.md`.
- **A deviation accepted as the new design** → update the spec artifact in the same turn, and note the change in `## Findings`. An accepted deviation that is not written back is drift with permission.
- **The drift-check cadence** → a row in `## Due`.
