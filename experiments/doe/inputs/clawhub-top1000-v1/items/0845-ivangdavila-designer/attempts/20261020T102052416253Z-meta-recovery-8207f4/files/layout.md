# Layout, Grid and Space

Scope: where things sit, how far apart, and what happens at every width. This is where most "it looks off" complaints are actually resolved.

**Contents:** [The Spacing Scale](#the-spacing-scale) · [Grouping Is Distance](#grouping-is-distance) · [Grids](#grids) · [Responsive Without Device Breakpoints](#responsive-without-device-breakpoints) · [Optical Alignment](#optical-alignment) · [Hierarchy Beyond Size](#hierarchy-beyond-size) · [Density](#density) · [Elevation and Z-Order](#elevation-and-z-order) · [Layout Failures](#layout-failures) · [Write It Down](#write-it-down)

**Before setting a grid or a breakpoint**, read `## Surfaces` in `~/Clawic/data/designer/memory.md`: the surface may already have a column count, a container width and a set of named breakpoints that the codebase enforces.

## The Spacing Scale

`space_n = spacing_base_px × n`, with `n ∈ {0.5, 1, 2, 3, 4, 6, 8, 12, 16}`. At the default base of 8: **4, 8, 16, 24, 32, 48, 64, 96, 128**.

- **Why a scale at all**: consistency is not aesthetic here — it is what makes a layout composable. Arbitrary values force every future component to negotiate with its neighbours.
- **4px is the sub-step, not a free value.** It exists for icon insets and tight text offsets. If it is appearing in section spacing, the base is wrong.
- **The scale is non-linear on purpose.** Small gaps need fine control (4/8/16); large gaps do not (48/64/96). Linear scales produce nine values in the 40-80 range that nobody can tell apart.
- **A base of 4** suits data-dense tools and native mobile; **8** is the default; larger bases exist but stop mapping cleanly onto text metrics.
- **Optical exceptions are allowed and must be named.** A button's optical vertical padding is usually 1-2px less than its horizontal for the same visual weight, because letterforms do not fill their line box. Record it as the token value, not as a per-instance nudge.

## Grouping Is Distance

SKILL.md Rule 4 in practice, because this is the single highest-leverage move in layout:

| Relationship | Gap | Example at base 8 |
|---|---|---|
| Inside a unit (label → its input) | 0.5-1 unit | 4-8px |
| Between units in a group (fields in a fieldset) | 2 units | 16px |
| Between groups (fieldset → fieldset) | 4-6 units | 32-48px |
| Between sections | 8-12 units | 64-96px |

Two consequences people miss: **a label closer to the field below it than to its own field is an actual usability bug**, and **every divider line is a candidate for deletion** — if the group gap is right, the line adds noise; if the line is load-bearing, the spacing is wrong. Remove all lines first, then add back only the ones that are still missed.

## Grids

- **Columns are for aligning content, not for placing boxes.** A 12-column grid is useful because 12 divides by 2, 3, 4 and 6; the grid earns its keep only if the layout actually uses those divisions.
- **Typical shape**: 12 columns desktop, 8 tablet, 4 mobile. Gutter = 2-3 space units; margin ≥ gutter (a margin smaller than the gutter makes the page look like it is falling off the edge).
- **Container max-width is set by the measure, not by the monitor.** A single text column stops at 45-75 characters (`typography.md`) no matter how wide the screen; wide containers are for multi-column layouts, tables and dashboards.
- **Baseline grids are usually a trap on the web.** Genuine baseline alignment requires controlling every line box, which components and dynamic content break. Align to the space scale, and reserve baseline grids for print and controlled editorial layouts.
- **The rule of thirds is a composition heuristic for images and heroes**, not a layout system. Off-centre placement adds tension; it does not replace a grid.

## Responsive Without Device Breakpoints

- **Breakpoints come from content, not devices.** Resize until the layout breaks — the measure gets too long, the columns get too narrow, the nav wraps — and put the breakpoint there. Device widths change every year; the width at which a 3-column card grid stops working does not.
- **Three to five breakpoints is plenty.** More produces states nobody tests.
- **Prefer intrinsic layout over breakpoints entirely** where possible: a grid with `repeat(auto-fit, minmax(<min>, 1fr))` reflows continuously with no breakpoint at all, and it cannot be wrong at a width you forgot to check.
- **Container queries change the unit of responsiveness** from the viewport to the component's own box, which is what a component in a sidebar actually needs. Specify component behavior in terms of its own available width, and the same card works in a full-width grid and in a 320px rail.
- **Mobile first is about source order**, not about starting small in a canvas. The order the content appears in the DOM is the order a screen reader and a narrow viewport get it; a desktop-first design that visually reorders columns often reads scrambled on a phone.
- **WCAG 1.4.10 (Reflow)**: no two-axis scrolling at 320 CSS px width — equivalent to a 1280px viewport at 400% zoom. Horizontal scrolling is permitted only for content that genuinely requires it, like a wide data table, and then only inside its own scroll container.
- **Test the two ends and one middle**: 320px, the widest supported, and the width just below your busiest breakpoint. That is where layouts break.

## Optical Alignment

Mathematical alignment is often visually wrong. The fixes are small, specific and constant:

- **Icon + text**: align optical centres, not bounding boxes. Most icon sets need a 1px vertical nudge against text; a right-pointing arrow in a button needs slightly less trailing space than a symmetric icon.
- **Punctuation hangs.** Opening quotes, bullets and dashes at the start of a line should sit outside the text column, or the paragraph edge looks indented.
- **Circular avatars and round buttons overshoot.** A 40px circle beside a 40px square looks smaller; scale the circle 2-3% larger to match.
- **Text in a circular or pill container** sits ~1px above the mathematical centre, because descenders occupy space the eye discounts.
- **Weight balance beats symmetry.** A heavy element on one side needs more space around it than a light one; identical padding on both sides of an asymmetric composition reads as an error.
- **Centre by optical mass in logos and hero compositions** (`brand.md`), never by the bounding box of the artwork.

## Hierarchy Beyond Size

When something must stand out, reach for these in order — size is the most expensive and least precise instrument:

1. **Space** — isolation makes an element important without changing it at all
2. **Weight** — one weight step, visible (`typography.md`)
3. **Color** — text-primary vs text-secondary, or the single accent
4. **Position** — top-left in LTR reading order is the strongest slot on the page
5. **Size** — a full step of the type scale
6. **Case, container, or elevation** — the loudest options, and the easiest to overuse

Anything above the fourth position on this list, applied to three elements at once, cancels out — that is the mechanism behind "nothing stands out".

## Density

A single density is a decision to serve one user well and the other badly. Two modes are usually enough:

| Mode | Row height (base 8) | Fits |
|---|---|---|
| Comfortable | 48-56px | Consumer, occasional use, touch |
| Compact | 32-40px | Data tools, expert users, keyboard-driven |

Density changes spacing and row height. It must **not** change font size below `min_body_px`, and it must not drop targets below the 24px floor (SKILL.md Rule 7). Expose it as a user preference in data-heavy products; the users who want compact want it badly.

## Elevation and Z-Order

- **A named scale, not arbitrary integers.** Five layers cover almost everything: base (0), raised card (1), sticky header (2), dropdown/popover (3), modal (4), toast (5). Values like `z-index: 9999` are the symptom of a missing scale.
- **Shadows encode height and must be consistent**: one light source (from above), blur growing with elevation, and opacity that rises far more slowly than the blur. Two shadows with different directions on one screen read as broken rendering.
- **In dark mode, elevation is lightness, not shadow** (`color.md`).
- **Overlay hierarchy is a system, not per-component**: modal over drawer over popover over tooltip, and a toast above all of them. Decide once; every violation becomes a bug report about "the dropdown behind the modal".

## Layout Failures

| Symptom | Cause | Fix |
|---|---|---|
| Content touches the edge on mobile | Container padding applied at a breakpoint above 320 | Padding is a base style, overridden upward |
| Cards of different heights look broken | Content varies and nothing stretches | Equal-height rows with content aligned top, actions pinned bottom |
| The page jumps as it loads | Images and embeds without reserved space | Aspect-ratio boxes on every media element; CLS ≤0.1 |
| A long word or URL breaks the layout | No wrapping strategy on user content | Overflow-wrap on every field that can hold user input |
| Sticky header covers the anchor target | Scroll offset not accounted for | Scroll-margin equal to header height on every anchor |
| Two-column layout collapses in the wrong order | Visual order diverged from source order | Fix source order; reordering is for tuning, not for structure |
| Buttons of different widths in a row | Text-width buttons with unequal labels | Equal widths in a group, or all sized to content — never mixed |
| Fine at every breakpoint, broken between them | Only breakpoint widths were checked | Test the widths *between* breakpoints, where fluid values are at their extremes |

## Write It Down

- **A surface's grid, container width, named breakpoints, density mode or base unit** → its row in `## Surfaces` of `~/Clawic/data/designer/memory.md`, in the same turn it is decided.
- **The spacing scale, radius scale and elevation scale once implemented** → `## Token Sets`, with the names the codebase uses.
- **A base unit or breakpoint set the user declares as their standing preference** → its key in `config.yaml`, not `memory.md`.
- **A layout pattern that took real work to derive** — a responsive table strategy, a dashboard shell, a print-and-screen dual layout — → `artifacts/<kebab-name>.md` with its `## Boxes` line.
