# Brand and Identity

Scope: the mark, the system around it, and the files everyone else will use. Strategy and positioning upstream of this belong to `branding`; this is the craft that turns a position into artwork that survives a 16px favicon and a one-color embroidery.

**Contents:** [Before Drawing Anything](#before-drawing-anything) · [The Mark](#the-mark) · [Tests a Mark Must Pass](#tests-a-mark-must-pass) · [Clear Space, Minimum Size, Misuse](#clear-space-minimum-size-misuse) · [Export Matrix](#export-matrix) · [Everything That Is Not the Logo](#everything-that-is-not-the-logo) · [Guidelines Document](#guidelines-document) · [Rebrands and Migrations](#rebrands-and-migrations) · [Write It Down](#write-it-down)

**Before proposing a mark, a color or a typeface**, read `## Brands` in `~/Clawic/data/designer/memory.md` and open any `artifacts/brand-*.md` its `## Boxes` index names. A brand already has answers; the expensive failure in this domain is inventing a fourth grey that contradicts a guideline written last quarter.

## Before Drawing Anything

Five inputs, and the mark is mostly determined by them:

1. **Where it appears smallest** — a 16px favicon and an app icon set the complexity ceiling before aesthetics get a vote.
2. **Where it appears in one color** — invoices, embroidery, laser etching, fax-grade PDFs, a customs form.
3. **Name length and shape** — a 14-character name cannot use the same lockup as a 4-character one.
4. **What must never be confused with it** — the two closest competitors, in silhouette.
5. **Who signs off, and against what** — see `critique.md`; an identity with no stated decider gets designed by committee and looks like it.

Trademark reality check before investment: a search of the national register plus a plain web and app-store search costs an hour and prevents the entire system being redrawn. A name available as a domain is not a name available as a mark. This is a search, not legal advice — clearance is a lawyer's signature.

## The Mark

| Type | Use when | Cost |
|---|---|---|
| Wordmark | The name is distinctive and ≤12 characters | No small-scale asset — needs a separate monogram for avatars |
| Lettermark / monogram | The name is long or an acronym | Says nothing about the product; leans entirely on repetition |
| Pictorial mark | The product has one concrete, ownable object | Recognition takes exposure most young brands do not have |
| Abstract mark | No concrete object fits, or the category is crowded | Means nothing until you spend to make it mean something |
| Combination | Default for almost everything | Two lockups to maintain plus the rules for when each applies |
| Emblem | Heritage, badge, physical product | Fails at small sizes almost by construction |

Default is a **combination mark**: a wordmark for wide contexts plus a mark that stands alone in a square. Escape hatch: pure wordmark when the brand will only ever appear in wide slots and someone else owns the avatar (rare — it is almost never true once a social profile exists).

Construction notes that separate a drawn mark from a typed one:
- **Optical, not mathematical.** A circle must overshoot a square by roughly 2-3% of its height to read as the same size; a triangle needs more. Same for the play triangle inside a circle: centred by bounding box, it looks left-shifted; shift it right by about a third of the difference between its geometric and visual centre.
- **Consistent curve logic.** One corner radius family, one terminal treatment, one stroke contrast across every element. Mixed logic is what reads as "made in a template".
- **Stroke weights that survive scaling.** A 1.5pt stroke at 200px is a sub-pixel line at 16px. Either build a simplified small-size variant or thicken until the smallest use holds.
- **Custom letterforms are edits, not drawings.** Start from a licensed typeface, adjust 2-3 letters, and check the licence permits modification — many display licences do not.

## Tests a Mark Must Pass

Run all seven before showing anything. Each has a binary answer.

| Test | Method | Pass |
|---|---|---|
| 16px | Render the favicon at actual size, not zoomed | Silhouette still identifiable |
| One color | Fill 100% black; then 100% white on black | No shape collapses, no counter fills in |
| Squint | Blur heavily, or view at 10% zoom | Overall shape reads before detail |
| Reverse | Place on the brand's darkest and lightest surfaces | No halo, no invisible edge, no shape inversion |
| Grayscale | Desaturate | Elements that were distinguished by hue still separate |
| Rotation and crop | Circle-crop for avatars, square-crop for app icons | Nothing critical is cut; the safe area holds |
| Ugly-context | Photocopy at 60%, print on a beige form, embroider at 30mm | Still recognisable |

A mark that needs a gradient to be legible has failed the one-color test — gradients are an enhancement layer, never load-bearing.

## Clear Space, Minimum Size, Misuse

- **Clear space**: define it in a unit derived from the mark itself so it scales — the x-height of the wordmark, or the width of the monogram's counter. Half that value is a common relaxation for dense UI headers, and it should be written down rather than improvised.
- **Minimum size**: state it separately for screen (px) and print (mm), and per lockup. Typical shape: full lockup 120px / 25mm wide, mark alone 24px / 8mm. Derive from the tests above, not from a template.
- **Misuse page**: eight forbidden operations, each shown once — stretch, recolor outside the palette, add effects, rotate, place on a busy photo without the required scrim, re-typeset the wordmark, alter spacing, and swap the lockup for a context it is not built for. A misuse page prevents more damage than any other page in the document.

## Export Matrix

Deliver all of it or the client's developer will regenerate it badly.

| Asset | Spec |
|---|---|
| Master | Layered source file plus flattened, outlined SVG per lockup and per color mode |
| Web logo | SVG with a `viewBox`, no embedded raster, IDs prefixed to avoid collisions on pages with two SVGs |
| Favicon | SVG favicon + a multi-size `.ico` containing 16 and 32 px; verify at 16px on both light and dark browser chrome |
| Apple touch icon | 180×180 PNG, no transparency, no rounded corners baked in (iOS masks it) |
| PWA icons | 192 and 512 PNG, plus a maskable variant whose content stays inside the central circle of 80% diameter |
| iOS app icon | 1024×1024 source, square, opaque, no alpha; the OS applies the mask (`mobile.md`) |
| Android adaptive | 108×108 dp foreground and background layers; only the central 72 dp is guaranteed visible, and the safe circle is 66 dp |
| Social | Square avatar (min 400px), plus per-network cover art; check the circular crop on every avatar |
| Print | Vector PDF/EPS in CMYK plus spot-color version with the Pantone references named (`print.md`) |
| One-color | Solid black and solid white versions of every lockup, as separate files |

Name files predictably: `<brand>-<lockup>-<color>-<size>.<ext>`. A folder where someone must open files to tell them apart is a folder that will be used wrongly.

## Everything That Is Not the Logo

Users recognise a brand from the system long before they parse the mark. Specify all six or the identity will not survive contact with a second designer:

- **Type** — display and text faces, weights actually licensed, the scale ratio (`typography.md`)
- **Color** — full ramps, not five swatches; the semantic assignments; behavior in dark mode (`color.md`)
- **Shape language** — corner radius scale, stroke weight, whether forms are geometric or organic
- **Space and rhythm** — the base unit and how generous the brand is with it; a "premium" feel is mostly whitespace
- **Imagery** — photography direction, illustration style, iconography weight (`icons.md`)
- **Motion** — the signature easing curve and one entrance behavior, so animation feels authored (`motion.md`)

Voice belongs to `copy.md` and, for positioning, to `branding` — but the guidelines document must contain it or the brand will sound like whoever typed last.

## Guidelines Document

Aim for the shortest document that prevents the misuse you can predict. Order matters: rules people need daily go first.

1. The mark, its lockups, and when each is used
2. Clear space, minimum sizes, misuse
3. Color: ramps, semantic roles, contrast pairs that are approved, dark-mode surfaces
4. Type: faces, licensed weights, the scale, and three worked examples (hero, body, caption)
5. Space, radius, elevation
6. Imagery and iconography direction, with three approved and three rejected examples
7. Voice: three adjectives, each with a "we say / we don't say" pair
8. Application examples: the five artifacts this brand actually produces, not a mug and a billboard
9. Where the files live and who to ask

Every rule states its *reason* in one line. A rule with no reason gets broken the first time it is inconvenient, and it deserves to be.

## Rebrands and Migrations

- **Inventory before design.** List every surface carrying the old mark — product UI, app icons and store listings, email templates and signatures, invoices and contracts, packaging, signage, social avatars, ad accounts, favicon, error pages, PDF exports, third-party profiles. The list is always longer than the estimate, and it is the actual scope.
- **Cut over the identity at once, the system gradually.** Two logos live simultaneously reads as an error; two spacing scales does not. Ship the mark everywhere in one window, then migrate tokens surface by surface (`tokens.md`).
- **Keep the equity you have.** The element with the most recognition — usually a color or a silhouette — should survive unless the point of the rebrand is to destroy it. Say explicitly which one is being kept and which is being dropped.
- **Freeze the old files, do not delete them.** Legal documents, archived campaigns and printed stock keep referring to them for years.
- **Physical stock has a burn-down.** Business cards, packaging and signage are budget and lead time, not design; get the reorder dates before promising a launch date.

## Write It Down

An identity that only exists in a chat gets re-derived by the next person at full cost (`memory-template.md`):

- **A new brand, or a change to its palette, type stack, logo rules or minimum sizes** → its row in `## Brands` of `~/Clawic/data/designer/memory.md`, with the pointer to where the source files live.
- **The guidelines themselves, and any identity decision with rejected alternatives** → `artifacts/brand-<name>.md`, born as its own file, with its `## Boxes` line and a read condition naming the brand.
- **A client or agency that owns the brand** → a row in the shared `~/Clawic/data/contacts/contacts.md`, referenced here by name only.
- **A paid typeface, icon set or stock licence** → a row in the shared `~/Clawic/data/finances/subscriptions.md` with its renewal date and seat count, and the renewal date also in `## Due`. A licence that lapses silently is a legal problem discovered by an invoice.
