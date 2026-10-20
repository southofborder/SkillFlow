# Icons, Illustration and Imagery

Scope: the non-typographic visual layer — icon sets, illustration style, photography direction, and the licensing that governs all three. Implementing icons in code (sizing, color inheritance, sprite performance) is `icons`; this is the design and art-direction side.

**Contents:** [Buy or Draw](#buy-or-draw) · [The Icon Grid](#the-icon-grid) · [Optical Equality](#optical-equality) · [Icons That Communicate](#icons-that-communicate) · [Sizing and Pixel Snapping](#sizing-and-pixel-snapping) · [Illustration Style](#illustration-style) · [Photography Direction](#photography-direction) · [Generated Imagery](#generated-imagery) · [Licensing](#licensing) · [Write It Down](#write-it-down)

**Before choosing an icon set or an illustration style**, read `## Brands` in `~/Clawic/data/designer/memory.md`: the set may be chosen and licensed, and mixing two icon families is one of the most visible inconsistencies a product can have.

## Buy or Draw

| Approach | Take it when | Cost |
|---|---|---|
| Established open set (single family) | Almost always, especially before product-market fit | Your product looks like the other products using it |
| Open set + 10-30 custom icons | The domain has concepts no general set covers | The custom ones must match the set's grid, stroke and terminals exactly, or they look broken |
| Fully custom set | The icons are a brand asset and the set exceeds ~60 glyphs | Weeks of work, plus permanent maintenance as the product grows |
| Two sets mixed | Never | Two stroke weights and two corner logics on one screen |

Default: one open family, extended carefully. The extension work is the part people underestimate — a custom icon that is 0.5px off the family's stroke weight is visible in a row of eight.

## The Icon Grid

Standard system, and the reason most sets look coherent:

- **24×24 canvas** with a **2px live-area padding**, so artwork occupies a 20×20 area. This padding is what stops icons touching their container and what makes them optically consistent with text.
- **Stroke weight 1.5-2px at 24px.** Below 1.5 the icon disappears in light-on-dark; above 2 it competes with body text weight. Whatever is chosen, it is the same on every icon in the set.
- **Keyline shapes** define optical size across different geometries: square ~18×18, circle ~20 diameter, portrait rectangle ~16×20, landscape ~20×16. Icons built to these read as one size even though their bounding boxes differ.
- **Corner radius, terminals and joins are a single decision** across the set: rounded or square caps, one join style, one radius family. This consistency is 80% of what makes a set look professional.
- **Align to the pixel grid** — strokes on whole or half-pixel boundaries depending on stroke weight, so the icon renders crisply rather than blurred.

## Optical Equality

Mathematically identical is visually wrong. The adjustments are small, consistent, and what separates a drawn set from a traced one:

- A **circle overshoots a square** by roughly 2-3% of the height to look the same size (`layout.md`).
- A **triangle needs more** overshoot again, and its optical centre sits toward its base — a play triangle inside a circle shifts right by about a third of the difference between geometric and visual centre.
- **Diagonals read lighter than verticals** at the same stroke weight; some sets thicken diagonals marginally to compensate.
- **Dense icons look darker.** A settings gear against an outline arrow needs either fewer details or a slightly lighter treatment to carry equal weight in a toolbar.
- **Every icon is checked in a row with its neighbours**, at the size it ships. Icons approved one at a time never sit right together.

## Icons That Communicate

- **Only three categories of icon are universally understood**: interface conventions with decades of exposure (magnifier = search, X = close, hamburger = menu), real-world objects (printer, calendar, camera), and symbols the user's own domain uses. Everything else is learned or guessed.
- **Icon + label by default.** Icon-only is legitimate only for the universally understood set, in a repeated location, at a size with the target to match. Every icon-only control still needs an accessible name (`accessibility.md`).
- **A metaphor that needs an explanation has failed.** The floppy-disk save icon survives because of exposure, not because it communicates; a novel metaphor will not get that exposure.
- **Never encode state in color alone** (SKILL.md Rule 6): a filled/outline pair, a badge, or a word.
- **Filled vs outline as a state pair** is a strong and cheap convention — outline for inactive, filled for active — and it is far more legible than a color shift.
- **Do not reuse one icon for two meanings** anywhere in the product; the second use silently poisons the first.

## Sizing and Pixel Snapping

| Size | Use | Note |
|---|---|---|
| 16px | Inline with body text, dense tables | Needs a simplified variant of complex icons — detail vanishes |
| 20px | Compact UI, secondary controls | Common in dense products |
| 24px | Default UI size, the design grid | What the set is drawn at |
| 32-48px | Empty states, feature callouts | Can carry more detail |
| 64px+ | Illustration territory, not icons | Use an illustration instead |

An icon drawn at 24 and rendered at 16 is a 0.67× scale that lands strokes on fractional pixels and blurs. Sets with a genuine 16px variant redraw it; sets without one need their smallest use tested before adoption. **Icons scale with their text**, so size them in the same relative unit as the label they sit beside.

## Illustration Style

Define the style once, in five parameters, or every new illustration is a negotiation:

1. **Line vs fill** — outlined, flat-filled, or line-and-fill hybrid
2. **Palette scope** — the brand palette only, or a wider illustrative set (state it: an illustration palette that is not derived from the brand ramp is how a product ends up with a second visual identity)
3. **Perspective** — flat/front-on, isometric, or loose 3D. Isometric is expensive to extend and hard to keep consistent across contributors
4. **People** — abstract, stylised, photographic, or absent. Representation is a brand decision, and "no people" is also a decision
5. **Complexity budget** — how much detail an illustration is allowed, which is what keeps a set coherent when three people draw it

Then: **spot illustrations for empty states and features, one hero illustration maximum per page**, and every illustration must work on both themes — a line illustration with a hardcoded dark stroke disappears in dark mode. Provide either theme-aware colors or two variants (`color.md`).

## Photography Direction

An art-direction brief that a photographer or a stock searcher can execute has six fields:

| Field | Example |
|---|---|
| Subject | Real practitioners at work, never posed groups at a whiteboard |
| Environment | Actual workspaces, natural clutter kept |
| Light | Soft daylight, single direction, no hard flash |
| Color | Cool neutrals; the brand accent appears once as a physical object |
| Framing | Wide with negative space on the left for the headline |
| Post | Low contrast, slight desaturation, no heavy filters |

Practical constraints on top: **crop safety** (specify the focal point so responsive crops do not decapitate anyone), **text overlay** requires either a scrim of a stated opacity or a designated empty region (`color.md`), and **file budgets are design constraints** — a hero image is the usual LCP element, so its weight belongs in the spec, not in a later optimisation pass (`marketing.md`).

Stock photography tells: extreme smiling in an office, handshakes, glowing blue technology abstractions, and any image where nobody is doing a real task. If the alternative is bad stock, use an illustration or a screenshot of the actual product.

## Generated Imagery

- **Treat it as a source, not as a deliverable.** Generated output needs the same crop, color, and consistency work as stock, plus a check for artefacts at final size.
- **Consistency across a set is the hard part**, not any single image. Fix seed, style description and framing before generating a set, and expect to hand-correct.
- **Never generate a logo, an icon set or anything with text in it** for production: letterforms and glyph consistency fail, and a mark must be vector-native (`brand.md`).
- **Check the licence and the provenance terms** of the tool for commercial use, and record the tool, the model or version, the prompt and the seed against each image in `artifacts/imagery-<brand>.md` — an image whose rights cannot be established is a liability during any acquisition or funding review.
- **Disclose when the context requires it** (editorial, journalistic, or anywhere the audience would reasonably assume a photograph).

## Licensing

- **Icon sets**: check whether attribution is required, whether modification is permitted, and whether the licence covers use inside a product being sold. Some popular sets require a paid tier for commercial or for specific weights.
- **Stock**: standard licences typically exclude use in a logo, in merchandise for sale, and in anything implying endorsement by a depicted person. Editorial-only assets cannot be used commercially at all.
- **Model and property releases** are required for recognisable people and some buildings and artworks in commercial use.
- **Illustration commissioned from a freelancer**: rights transfer only if the contract says so (`clients.md`) — the default in many jurisdictions is that the creator retains copyright and grants a licence.
- Every paid asset licence becomes a row in the shared `~/Clawic/data/finances/subscriptions.md` with its renewal date and scope.

## Write It Down

- **The icon set chosen, its licence tier, and the stroke/grid parameters custom icons must match** → the row in `## Brands` of `~/Clawic/data/designer/memory.md`.
- **The illustration style definition, the photography brief, and the provenance of every generated image** (tool, model or version, prompt, seed, where it is used) → `artifacts/imagery-<brand>.md`, its own file, with its `## Boxes` line and a read condition naming the brand — this is the artifact that stops style drift when a second person contributes, and the only record that establishes rights later.
- **Where source and export files live** → `## Source Files` in `memory.md`, as locations only, never credentials.
- **An asset licence with a renewal, a seat cap or a usage restriction** → the shared `~/Clawic/data/finances/subscriptions.md`, plus a `## Due` row for the renewal.
