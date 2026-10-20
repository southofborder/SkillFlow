# Accessibility the Designer Owns

Scope: the subset of WCAG that is decided in the design, not in the code. A full audit with automated sweeps, screen-reader passes and a remediation report is `accessibility-audit`; this is what must be right before the file leaves.

**Contents:** [Why Design Owns These](#why-design-owns-these) · [The Designer's Criteria](#the-designers-criteria) · [Focus](#focus) · [Keyboard and Order](#keyboard-and-order) · [Targets and Motor Access](#targets-and-motor-access) · [What the Screen Reader Needs From You](#what-the-screen-reader-needs-from-you) · [Cognitive Load](#cognitive-load) · [Annotating a Design](#annotating-a-design) · [The Design-Time Check](#the-design-time-check) · [Write It Down](#write-it-down)

**Before an accessibility pass**, read `## Findings` in `~/Clawic/data/designer/memory.md` and open any `artifacts/audit-*.md` its `## Boxes` index names. A previously fixed failure that has returned is a systems problem, not a screen problem.

## Why Design Owns These

Contrast, target size, focus order, reading order and reliance on color are decided by the mockup. Fixing them in code means changing the design, which is why they are the failures that survive to production: WebAIM's annual scan of a million home pages has found detectable WCAG failures on roughly 95% of them in every edition, with low-contrast text the single most common failure at around 80% of pages. That is not an engineering statistic.

With `a11y_posture: strict`, any AA failure — including non-text contrast and target size — blocks delivery, and the keyboard pass below runs on every review rather than at milestones.

## The Designer's Criteria

The WCAG success criteria a design can pass or fail on its own, with what to check:

| Criterion | What design must do | Check |
|---|---|---|
| 1.4.3 Contrast (AA) | Text ≥4.5:1, large text ≥3:1 | Computed, per surface, including hover and disabled-adjacent states (SKILL.md Rule 1) |
| 1.4.11 Non-text contrast | Icons, input borders, toggle tracks, focus rings ≥3:1 | Against every adjacent color they can sit on |
| 1.4.1 Use of color | Second cue on every status, link and required field | Grayscale the screen |
| 1.4.10 Reflow | No 2-axis scrolling at 320 CSS px | Design or annotate the 320px case |
| 1.4.12 Text spacing | Survives line-height 1.5, ¶ 2em, letter 0.12em, word 0.16em | No fixed-height text containers |
| 1.4.4 Resize text | Usable at 200% zoom | No `vw`-only type, no px-locked containers (`typography.md`) |
| 2.4.7 Focus visible | Every interactive element has a visible focus state | It is in the state matrix or it does not exist |
| 2.4.11 Focus not obscured (2.2) | Sticky headers, footers and cookie bars never cover the focused element | Tab through with the sticky bar present |
| 2.5.8 Target size minimum (2.2) | 24×24 CSS px floor, 44×44 default | Measure the *hit area*, not the icon |
| 2.5.5 Target size enhanced (AAA) | 44×44 | The design default anyway (SKILL.md Rule 7) |
| 1.3.2 Meaningful sequence | Visual order matches source order | Read the design top-to-bottom as a single column |
| 3.3.2 Labels or instructions | Visible label on every input | Placeholder is not a label (`components.md`) |
| 2.3.1 Three flashes | Nothing flashes more than 3×/second | Applies to loading and celebration effects (`motion.md`) |
| 1.4.13 Content on hover/focus | Hover content is dismissable, hoverable, persistent | Tooltips and popovers |
| 2.2.2 Pause, stop, hide | Anything auto-moving >5s has a control | Carousels, marquees, autoplay video |

## Focus

The most-skipped and most-noticed part of an interface for keyboard users:

- **Never remove the focus indicator without replacing it.** A stronger, on-brand ring is a legitimate design decision; no ring is a broken product.
- **Design one ring token and use it everywhere** (`color.md`). It must clear 3:1 against every surface it can land on, which usually means an inner + outer ring (light and dark) so it works on both.
- **Thickness and offset**: a solid perimeter of at least 2 CSS px, offset ~2px from the element, so it does not read as a border change. WCAG 2.2's Focus Appearance criterion is the reference for the geometry.
- **Focus-visible, not focus.** The ring should appear for keyboard interaction and not on every mouse click; that distinction is what makes teams stop deleting it.
- **Focus must be managed on every overlay**: into the dialog on open, trapped while open, returned to the trigger on close. Design it explicitly — it does not happen by default (`components.md`).
- **After a destructive or navigational action, focus goes somewhere sensible** — the next item, the list heading, the error summary — never to the top of the document silently.

## Keyboard and Order

- **Tab order follows source order**, and source order should follow the visual reading order. Any place the design visually reorders content is a place the keyboard user gets a different sequence.
- **Every interactive element is reachable and operable by keyboard.** Custom controls — drag handles, canvas elements, sliders, drag-and-drop — need a keyboard alternative designed, not retrofitted. Drag-and-drop with no keyboard path is the most common design-created barrier.
- **A skip link to main content** is a design element: visible on focus, first in the order, above everything sticky.
- **Escape closes the topmost layer** and only that one. Enter and Space activate; arrow keys move within a composite widget (menu, tabs, radio group), not between them.
- **The keyboard pass is 90 seconds**: unplug the mouse, tab through the whole flow, and confirm you always know where you are and can always get out.

## Targets and Motor Access

- **Measure the hit area, not the icon.** A 20px icon inside a 44px button passes; a 20px icon with 20px of padding-free space around it does not.
- **Spacing exception**: the 24px floor can be met by a smaller target with 24px of clear space around its centre, which is what makes dense toolbars legal — but it is a fallback, not a design goal.
- **Adjacent targets need separation.** Two 44px buttons touching each other produce mis-taps at the boundary; 8px between them removes most of it.
- **Do not require precision, hold, or double-tap** as the only way to do something. Every gesture needs a single-pointer alternative (WCAG 2.5.1), and a drag needs a click path.
- **Timeouts are a motor and cognitive barrier.** If a session or a flow expires, it must be extendable, and the design needs the warning and the extension control.

## What the Screen Reader Needs From You

A designer does not write the ARIA, but the design determines whether it can be written correctly:

- **Heading structure is a design decision.** One h1 per page, no skipped levels, and headings that describe the section rather than decorating it. A "heading" that is just big bold text is invisible to navigation.
- **Every icon-only control needs an accessible name** — provide the words in the spec, not `aria-label: TBD`.
- **Images need their purpose stated**: informative (needs alt text, which you should write), decorative (marked empty), or complex (needs a described alternative nearby). Alt text is content, and content is the designer's job when nobody else has claimed it.
- **Link text stands alone.** A screen-reader user can list every link on the page; twelve of them saying "Learn more" is a dead end (`copy.md`).
- **Announce dynamic changes.** A toast, an inline validation, a filtered result count and a loading completion all need to be announced — mark in the spec which region is live and how urgent.
- **Landmarks come from the layout**: header, nav, main, complementary, footer. If the design has no clear main region, neither will the build.

## Cognitive Load

Underspecified in WCAG and the most common real barrier:

- **Plain language at roughly grade 8-9**, front-loaded, one idea per sentence (`copy.md`).
- **Do not rely on memory across steps.** Show the values entered earlier at the confirmation step rather than making the user recall them (WCAG 3.3.7 covers the auto-fill case).
- **Consistency of position and naming** across pages: the same action in the same place with the same word. Novelty is expensive for everyone and disqualifying for some.
- **One task per screen** when the task is unfamiliar or high-stakes.
- **Errors must be recoverable without starting over** — the single biggest cognitive-accessibility failure in forms.

## Annotating a Design

Ship annotations with the design or the accessibility gets rebuilt by guesswork (`handoff.md`). Minimum set:

1. Heading levels on every text element that is a heading
2. Reading and tab order, numbered, wherever it is not obvious
3. Accessible names for every icon-only control, and alt text for every image
4. Focus behavior for overlays: where it goes on open, where it returns
5. Live regions: which areas announce, and whether politely or assertively
6. Landmark regions
7. The 320px reflow behavior and the 200% zoom behavior
8. Any keyboard alternative for a pointer-only interaction

## The Design-Time Check

Ten minutes, before anything is shown:

1. Grayscale the screen — does everything still parse? (1.4.1)
2. Compute contrast on text and on every meaningful border, icon and focus ring (1.4.3, 1.4.11)
3. Zoom the browser or scale the frame to 320px wide — anything cut off? (1.4.10)
4. Tab through with no mouse — can you see where you are, everywhere? (2.4.7, 2.4.11)
5. Measure the three smallest hit areas (2.5.8)
6. Read the screen top to bottom as a single column — does it still make sense? (1.3.2)
7. Check every input has a visible label and every icon-only control has a name (3.3.2)
8. Turn on reduced motion — does the feedback survive? (`motion.md`)

Anything that fails here fails cheaply. The same failure after implementation costs a sprint, and after launch it costs a legal letter.

## Write It Down

- **An audit and its severity-ranked findings** → `artifacts/audit-<surface>-<yyyy-mm>.md`, its own file from the first one, with its `## Boxes` line and a read condition naming the surface.
- **The audit event itself, with the date, scope and pass rate** → a row in `~/Clawic/data/designer/sessions/<year>.md`, so the trend is visible across audits.
- **A finding that changes a system-level decision** — a brand color that cannot clear 4.5:1, a component pattern that cannot be made keyboard-operable — → `## Findings` in `memory.md`, because it constrains every future design on that surface.
- **The re-audit cadence** → a row in `## Due`, with the cadence itself in `config.yaml` when the user declares it.
- **The user's posture** (`baseline` vs `strict`, a compliance regime, a VPAT obligation) → `config.yaml`, never re-asked.
