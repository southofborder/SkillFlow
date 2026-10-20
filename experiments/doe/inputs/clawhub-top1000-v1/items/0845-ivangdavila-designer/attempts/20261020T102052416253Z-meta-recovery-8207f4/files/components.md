# Components, States and Patterns

Scope: the parts of an interface and every condition each one can be in. Most design debt is not a missing screen — it is a missing state.

**Contents:** [The State Matrix](#the-state-matrix) · [Buttons and Actions](#buttons-and-actions) · [Forms](#forms) · [Validation Timing](#validation-timing) · [Empty States](#empty-states) · [Loading](#loading) · [Errors](#errors) · [Tables and Lists](#tables-and-lists) · [Overlays](#overlays) · [Navigation](#navigation) · [Destructive Actions](#destructive-actions) · [Write It Down](#write-it-down)

**Before designing a component**, read `## Surfaces` and `## Token Sets` in `~/Clawic/data/designer/memory.md`, and open any `artifacts/spec-*.md` the `## Boxes` index names for it. Redesigning a component that already has a spec produces two components.

## The State Matrix

Every interactive component ships with all of these or the implementer invents them:

| State | Trigger | Must be true |
|---|---|---|
| Default | — | Clears contrast floors on every surface it can sit on |
| Hover | Pointer only | Never the only way to discover an action; absent on touch |
| Focus-visible | Keyboard | Ring ≥3:1 against adjacent colors, never removed, visible on every surface (`accessibility.md`) |
| Active / pressed | During press | Distinct from hover — feedback within 100ms |
| Disabled | Precondition unmet | Above 3:1, explains itself, and is not the only feedback (see Forms) |
| Loading | Async in flight | The control is inert, keeps its width, and says what is happening |
| Error | Validation or request failed | Icon + text + color, never color alone (SKILL.md Rule 6) |
| Success | Operation confirmed | Visible without a color-only cue; persistent enough to be read |
| Selected / checked | Multi-state controls | Distinguishable from hover and from focus at a glance |
| Read-only | Value shown, not editable | Visually different from disabled — it is informational, not blocked |
| Empty | No content yet | Its own design (see Empty States) |
| Skeleton | Content pending | Matches the real content's shape and dimensions |
| RTL and long-content | Locale and data | Survives a translated label 1.5-2× longer and a right-to-left mirror (`typography.md`) |
| Dark | Theme | Re-derived from dark tokens, not inverted (`color.md`) |

Not every component needs all fourteen. Every component needs a decision about all fourteen, and the ones that do not apply are marked "n/a" in the spec rather than left blank — a blank is indistinguishable from an oversight.

## Buttons and Actions

- **One primary per view** (SKILL.md Rule 2). Hierarchy: primary (filled) → secondary (outline or tonal) → tertiary (text) → link. Four levels is the maximum anyone can tell apart.
- **Label with verb + object**: `Save changes`, `Delete project`, `Send invite`. `Submit`, `OK` and `Yes` fail because they force the user back to the question (`copy.md`).
- **Width**: pad to content with a minimum width, so `OK` is not a square. In a group, either all buttons match the widest or all size to content — mixing is what reads as sloppy.
- **Placement**: primary action on the right in LTR dialogs on the web and Windows, on the right in iOS alerts too; consistency inside one product beats platform trivia, so pick a rule and put it in the spec.
- **Icon-only buttons need an accessible name and a tooltip**, and they need the 44px target even when the icon is 20px.
- **Loading buttons keep their width** — swapping `Save` for a spinner reflows the row. Reserve the width, replace the label in place, and disable re-submission.
- **Destructive actions are never the default focus target** and are visually separated from the safe path.

## Forms

- **One column.** Multi-column forms cause skipped fields and ambiguous tab order. Exceptions are genuinely paired fields: city/postcode, expiry/CVC.
- **Label above the field**, always visible. Placeholder-as-label disappears at the moment of typing, fails contrast at most placeholder greys, and destroys the ability to check what was entered.
- **Field width signals expected input.** A postcode field the width of an address field is a question the user has to answer twice.
- **Mark optional fields, not required ones**, when most are required — and vice versa. Marking every field with an asterisk conveys nothing.
- **Group into fieldsets of 3-7** with a heading; forms over ~10 fields split into steps with visible progress.
- **Input type drives the mobile keyboard.** Email, tel, number and URL types are a design decision with a large usability effect, and they belong in the spec.
- **Autofill support is design work**: standard field ordering and standard names let the browser fill the form, which beats every micro-optimisation of the layout.
- **Never disable paste.** It breaks password managers, which makes credentials worse, not better.
- **Help text lives above the input** (read before typing); **error text below** (read after failing). Reserve the space for the error, or the layout jumps.

## Validation Timing

The rule that resolves most form arguments:

| Moment | Do | Do not |
|---|---|---|
| On keypress | Only relax an existing error as it becomes valid, and update live counters | Never raise a new error mid-typing — it tells people they are wrong before they finish |
| On blur | Validate that field | Validate fields the user has not reached |
| On submit | Validate everything, show a summary, and move focus to the first invalid field | Rely on the summary alone with no per-field markers |
| After a server error | Preserve every entered value | Clear the form — the single most damaging form bug there is |

**Keep the submit button enabled.** A disabled submit gives no reason and no target; the user cannot ask why. Enabled + submit-time validation + focus to the first error tells them exactly what is wrong. This is a change in feedback, not in permissiveness.

## Empty States

Four different situations, four different designs. Using one for all four is a common and expensive shortcut:

| Kind | User's question | Content |
|---|---|---|
| First run (nothing ever existed) | "What is this for?" | One line of value, one primary action, optionally sample data |
| Cleared (user emptied it) | "Did I break it?" | Confirmation that this is expected, plus the way back |
| No results (filter or search) | "Did I search wrong?" | Echo the query, offer to relax the filter, suggest an alternative |
| Error (load failed) | "Is it me or you?" | What failed, whether it is retryable, and a retry control (see Errors) |

A first-run empty state is seen by 100% of new users and is often the most-viewed screen in the product. Illustration is optional; a working next action is not.

## Loading

- **Under ~1s: nothing, or a spinner.** Skeletons that flash for 200ms add flicker and read as jank.
- **1-10s: a skeleton that matches the real layout** — same block sizes, same number of rows. A skeleton that does not match causes a second visible reflow when content lands.
- **Over 10s: determinate progress with a real estimate**, plus what is happening. Nielsen's 10s limit is where attention leaves; a percentage is what keeps it.
- **Optimistic UI where reversal is cheap** (likes, reorders, toggles): apply immediately, reconcile silently, and show a clear, undoable failure. Never optimistic for payments, deletions, or anything the user cannot undo.
- **Preserve layout during load.** Reserve the space; a spinner that collapses to content of a different size is a CLS event.
- **Every async control needs its own loading state**, not just the page. A page spinner over a form the user can still type into is a race condition made visible.

## Errors

Structure, in this order: **what happened → why (if known) → what to do next**. Three components:

- **Inline** for field-level problems, adjacent to the field, persistent.
- **Contextual banner** for section- or page-level problems, at the top of the affected region.
- **Toast** only for transient, non-blocking outcomes — never for anything the user must act on, because it disappears.

Rules: no error codes without human text (an error id can be *included* for support); no blame (`Invalid input` says nothing, `Enter a date after today` says everything); never lose the user's work; and an error that cannot be acted on should have been prevented at design time. Full wording guidance is in `copy.md`.

## Tables and Lists

- **Tabular figures on every numeric column** (`typography.md`), right-aligned; text left-aligned; headers match their column's alignment.
- **Sticky header** past ~10 rows; sticky first column when horizontal scrolling is unavoidable.
- **Row height comes from density** (`layout.md`), not from the tallest content — truncate with a tooltip or wrap deliberately, but pick one per column.
- **Zebra striping is not the default.** It is useful for wide tables scanned across rows; for narrow ones it is noise. Row hover and a light divider usually beat it.
- **Sorting, filtering and pagination each need an empty result state** and a visible indication of what is currently applied. A filtered table that looks identical to an unfiltered one causes real data mistakes.
- **Bulk selection** needs a persistent count, a clear-all, and a select-all that says whether it means the page or the whole set — the ambiguity here deletes things.
- **On mobile, a table becomes a list of cards or a horizontal scroll container** — decide which in the spec, because leaving it produces both.

## Overlays

- **Modal only when the flow genuinely cannot continue**: a blocking decision, or a destructive confirmation. Everything else is a page, a drawer, or an inline expansion.
- **Non-negotiables**: focus moves in on open, is trapped inside, and returns to the trigger on close; Escape closes; the background does not scroll; the title is the accessible name.
- **Never a modal from a modal.** Two stacked modals mean the first one should have been a page.
- **Drawers/sheets** for supporting content and multi-step side tasks; mobile sheets need a drag affordance and a size that does not cover the context they refer to.
- **Tooltips are not for essential information** — they do not exist on touch and vanish on scroll. They must be reachable on keyboard focus, dismissable, and hoverable (WCAG 1.4.13).
- **Popovers close on outside click and on Escape**, and they never contain the only copy of something the user typed.

## Navigation

- **The top 3-5 destinations are always visible.** Hiding primary navigation behind a menu reliably lowers discovery of what is hidden (SKILL.md Where Experts Disagree).
- **Current location is always indicated**, and by more than color.
- **Hick's law sets the menu length**: `RT = a + b·log₂(n + 1)`. Going from 4 to 8 items costs about one extra unit of decision time, not double — which means grouping into two menus of 8 is usually worse than one clear menu of 16 with headings. Miller's 7±2 is about recall of unrelated items and does not apply to a visible list.
- **Breadcrumbs earn their place at three levels or more**; below that they are decoration.
- **Mobile bottom navigation caps at 5 items** and uses labels with the icons; icon-only bars are learned by nobody (`mobile.md`).
- **Search is navigation** in any product with more than a few hundred objects, and it needs its own empty, loading, no-result and error states.

## Destructive Actions

- **Confirm only what is irreversible.** A confirmation dialog on a reversible action trains people to click through, which is what makes the irreversible one dangerous.
- **Undo beats confirm** wherever it can be built: an action with a 5-10s undo window is faster and safer than a dialog.
- **The confirmation names the object and the consequence**: `Delete "Q3 Report" and its 14 revisions?` with the button labelled `Delete report`, never `Yes`.
- **Type-to-confirm** (retyping the name) is reserved for the genuinely unrecoverable — deleting a workspace, dropping a dataset. Used casually, it is theatre.
- **The destructive button is never the focus default**, and it is separated from the safe action by more than the standard gap.

## Write It Down

- **A new component or a change to its state matrix, once agreed** → `artifacts/spec-<component>.md`, its own file from the first one, with its `## Boxes` line and a read condition naming the component.
- **A pattern decision made once and applied everywhere** — validation timing, confirmation policy, table-on-mobile strategy — → `artifacts/pattern-<name>.md`, with what was rejected.
- **The surface the component belongs to, and who implements it** → `## Surfaces` in `~/Clawic/data/designer/memory.md`.
- **A component name that entered the token set** → `## Token Sets`, so the next designer finds it before inventing a synonym.
