# Typography

Scope: choosing faces, building the scale, setting text so it reads, and shipping fonts without breaking the page. Deep type-setting craft for print and editorial extends into `typography`; this is what a designer owns on a product and a brand.

**Contents:** [Choosing and Pairing](#choosing-and-pairing) · [The Scale Is a Formula](#the-scale-is-a-formula) · [Setting Text That Reads](#setting-text-that-reads) · [Fluid Type](#fluid-type) · [Weight, Width, Optical Size](#weight-width-optical-size) · [Loading Fonts Without Breaking the Page](#loading-fonts-without-breaking-the-page) · [Numerals and Data](#numerals-and-data) · [Beyond Latin](#beyond-latin) · [Licensing](#licensing) · [Write It Down](#write-it-down)

**Before choosing a typeface**, read `## Brands` in `~/Clawic/data/designer/memory.md`: the type stack may already be decided and licensed, and a second face is a cost, not a decision.

## Choosing and Pairing

Judge a face by the three things that actually matter at body size:

1. **x-height relative to cap height.** A large x-height reads bigger at the same point size and holds up small; a small x-height needs 1-2px more to match. This — not the nominal size — is why two 16px settings look different.
2. **Character disambiguation.** Set `Il1 O0 rn` and look. In interfaces with IDs, codes, or passwords, an ambiguous `l/I` is a support ticket.
3. **Weight range actually needed.** Two weights cover most products (regular + semibold/bold). If a face's semibold is its only usable emphasis, that is the face's real range.

Pairing rules, in order of usefulness:
- **One face is a valid answer.** A single well-drawn family with a real weight range beats a mediocre pair. Take this default unless the brand needs the contrast.
- **Contrast by category, not by degree.** Serif + sans, or geometric sans + humanist serif. Two similar sans faces read as a mistake, because the eye registers the difference without being able to justify it.
- **Match x-heights when mixing**, or the pair looks like a rendering bug rather than a decision.
- **Superfamilies are the safe pair** (same skeleton, serif and sans cuts): guaranteed harmony, no risk, slightly less character.
- **Cap the system at two families and one accent use.** A third face needs to earn its place in the licence, the loading budget, and the guidelines.

## The Scale Is a Formula

`size_n = min_body_px × type_scale_ratio ^ n`, rounded to whole pixels. Body sits at n=0; captions at n=−1.

| Ratio | Name | Character | Fits |
|---|---|---|---|
| 1.125 | Major second | Very tight | Dense dashboards, data tools |
| 1.2 | Minor third | Tight | Product UI with many levels |
| 1.25 | Major third | Balanced — the default | Most products and marketing |
| 1.333 | Perfect fourth | Expressive | Editorial, marketing sites |
| 1.5 | Perfect fifth | Dramatic | Landing pages with few levels |
| 1.618 | Golden | Very dramatic | Posters, hero-only work |

At 16px and 1.25: **13, 16, 20, 25, 31, 39, 49**. Two rules keep it usable:
- **Round, then freeze.** Rounded values are the scale; nobody recomputes ratios at build time.
- **Cap at five sizes in a product.** More than five means the hierarchy is being carried by size instead of by weight, color and space — the exact cause of "looks amateur" (SKILL.md It Looks Off).

A dense UI needs a *tighter* ratio than a landing page, so a product with a marketing site legitimately runs two ratios: `1.2` for app, `1.333` for marketing. Record both in `## Token Sets`, because a designer who assumes one will produce headings that look broken in the other context.

## Setting Text That Reads

| Control | Value | Reason |
|---|---|---|
| Measure | 45-75 characters, ~65ch target | Longer loses the return sweep; shorter breaks reading rhythm |
| Line height, body | 1.4-1.6 (unitless) | Rises with measure: 45ch tolerates 1.4, 75ch needs 1.6 |
| Line height, display | 1.05-1.25 | Leading ratio falls as size rises; 32px+ at 1.5 looks disconnected |
| Paragraph spacing | 0.75-1.0× the line height | Below that, paragraphs merge; above, the column fragments |
| Letter spacing, body | 0 | Text faces are already spaced for their size |
| Letter spacing, display | −1% to −3% | Large type is over-spaced by default |
| Letter spacing, all-caps and small sizes | +2% to +8% | Uppercase and small text need loosening |
| Alignment | Left (or start) for body | Justified text without hyphenation opens rivers; centred body over 3 lines slows reading |
| Widows and orphans | Never a single word alone on the last line of a heading | Use a non-breaking space between the last two words |

Unitless line-height only. A `line-height: 24px` on a component that later renders at 20px produces overlap; `1.5` scales with it.

Body text must survive the WCAG 1.4.12 stress test: line-height 1.5, paragraph spacing 2em, letter spacing 0.12em, word spacing 0.16em, with nothing clipped or overlapping. Fixed-height text containers are what fail it.

## Fluid Type

Interpolate between two known sizes instead of stepping at breakpoints:

```
slope     = (max_px − min_px) / (max_vw − min_vw)
intercept = min_px − slope × min_vw
font-size: clamp(<min>rem, <intercept/16>rem + <slope × 100>vw, <max>rem);
```

Worked: 16px at 360px viewport → 20px at 1280px. `slope = 4/920 = 0.00435`; `intercept = 16 − 0.00435 × 360 = 14.43px`. Result: `clamp(1rem, 0.902rem + 0.435vw, 1.25rem)`.

Two constraints: always include the `rem` term so the value still responds to the user's browser font-size setting (a pure `vw` size breaks zoom and violates 1.4.4), and clamp *every* step of the scale with the same min and max viewport, or the ratio drifts between steps and the hierarchy inverts at some width.

## Weight, Width, Optical Size

- **Never fake it.** Synthetic bold and oblique (the browser smearing or slanting a regular) destroy the letterforms and shift metrics. Ship the real weight or do not use it.
- **Weight steps must be visible.** 400 → 500 is imperceptible in most families at body size; 400 → 600 reads. Use two clearly separated weights rather than four adjacent ones.
- **Optical size is not the same as scale.** Faces with an `opsz` axis draw thinner strokes and tighter spacing at display sizes; using the text cut at 60px looks clumsy and the display cut at 14px looks fragile. If a face offers both, set the axis rather than the size alone.
- **Variable fonts pay off once you need three or more weights, or an axis** (weight + optical size + italic). Below that, a subset static file is usually smaller. Verify against the actual files, not the marketing claim, and remember every axis position you *can* use is not one you *should* — pick fixed instances and name them as tokens.

## Loading Fonts Without Breaking the Page

Type is the most common cause of CLS, and CLS is a Core Web Vital (≤0.1).

- **woff2 only**, and typically about 30% smaller than woff. Older formats are dead weight.
- **Subset** to the character sets actually used; a full multilingual face can be several times the size of a Latin subset. `unicode-range` lets the browser fetch only the ranges a page needs.
- **`font-display`**: `swap` shows fallback text immediately then swaps (guarantees text, risks a shift); `optional` never swaps after a short block period (guarantees no shift, risks the wrong font on first visit). Body text → `swap` with matched metrics; a display face on a marketing hero → `optional` is often the better trade.
- **Match fallback metrics** so the swap does not move anything: `size-adjust`, `ascent-override`, `descent-override` and `line-gap-override` on a `@font-face` block pointing at the local fallback. This is what turns a visible reflow into an invisible one.
- **Preload only the fonts above the fold**, and only the exact files — preloading four weights delays the one that matters.
- **Self-host by default.** Third-party font CDNs add a connection, a privacy question and a dependency; caches are no longer shared across sites, so the historic argument for them is gone.
- **System stack is a legitimate choice** for tools and dashboards: zero bytes, zero shift, native feel — at the cost of a brand voice in type.

## Numerals and Data

- **Tabular figures** (`font-variant-numeric: tabular-nums`) in every table, price column, timer and counter. Proportional figures make columns jitter and totals misalign; this is the single highest-value typographic setting in a data UI.
- **Lining vs old-style**: lining figures for UI and data, old-style only inside running editorial prose.
- **Right-align numbers, left-align text**, and align on the decimal separator when precision varies.
- **Currency and units** in a lighter weight or smaller size than the number keeps the value dominant without changing its size.
- **Never let a font's default kerning near-space a range**: `12–15` needs an en dash with no spaces, `12 - 15` reads as subtraction.

## Beyond Latin

- **Translated UI strings expand.** The W3C's guidance puts the worst expansion on the shortest strings: under 10 characters can grow 100-200%, 11-20 characters 80-100%, 30-50 characters 40-60%, and long paragraphs around 30%. Button labels are therefore the most dangerous strings in the interface, not the safest.
- **Line height must rise for scripts with tall ascenders and marks** — Devanagari, Thai, Vietnamese, Arabic diacritics — typically 1.6-1.8 where Latin sits at 1.5. A single global 1.4 clips them.
- **CJK has no word spaces**, breaks anywhere, and needs its own font stack; Latin type set inside CJK usually needs a different size to match apparent weight.
- **RTL is a mirror of layout, not of everything.** Flip the layout, icons that indicate direction, and progress; do not flip logos, clocks, or images of real objects. Numbers stay LTR.
- **Test with a real translation, not padded lorem.** The German or Finnish string is the honest stress test, and it is where fixed-width buttons die.

## Licensing

Type licences are the most commonly violated part of a brand system, and the violation surfaces during due diligence:

- **Desktop, web, app, and broadcast are separate grants.** A desktop licence does not permit `@font-face` hosting; a web licence is usually capped by monthly pageviews.
- **Embedding in an app** or in a PDF for distribution typically needs its own licence tier.
- **Modification** — including outlining letterforms for a logo — is forbidden by many licences and explicitly permitted by others. Read before drawing.
- **Open-source faces still have terms** (attribution, reserved names, no sale of the font itself). "Free" is not "unconditional".
- Every paid licence becomes a row in the shared `~/Clawic/data/finances/subscriptions.md` with its renewal date, tier and seat/pageview cap.

## Write It Down

- **A type stack chosen or changed for a brand** → the type columns of its row in `## Brands` of `~/Clawic/data/designer/memory.md`.
- **A scale (`min_body_px`, ratio, the rounded steps) once implemented** → `## Token Sets`, and the ratio itself in `config.yaml` when the user declares it as their standing preference.
- **The reasoning behind a face choice, with the faces rejected and why** → `artifacts/type-decision-<brand>.md`, with its `## Boxes` line. This is the decision most likely to be re-litigated by the next designer.
- **A font licence with a renewal date, tier or cap** → a row in the shared `~/Clawic/data/finances/subscriptions.md`, plus a `## Due` row for the renewal.
