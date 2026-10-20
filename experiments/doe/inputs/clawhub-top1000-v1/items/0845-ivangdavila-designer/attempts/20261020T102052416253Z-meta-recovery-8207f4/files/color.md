# Color

Scope: building a palette that survives contrast checks, dark mode, colorblind users and a CMYK press. Color-space theory in depth lives in `color`; this is what a designer must get right to ship.

**Contents:** [Contrast Is Computed](#contrast-is-computed) · [Building the Palette](#building-the-palette) · [Ramps That Are Actually Usable](#ramps-that-are-actually-usable) · [Semantic Assignment](#semantic-assignment) · [Dark Mode Is Designed, Not Inverted](#dark-mode-is-designed-not-inverted) · [Color Vision Deficiency](#color-vision-deficiency) · [Gamut, Profiles and Where Color Breaks](#gamut-profiles-and-where-color-breaks) · [Write It Down](#write-it-down)

**Before generating a palette**, read `## Brands` and `## Token Sets` in `~/Clawic/data/designer/memory.md`. Most "we need a palette" requests are really "we need the existing palette applied", and a second set of greys is the most common permanent damage a designer does to a product.

## Contrast Is Computed

The formula and the floors are SKILL.md Rule 1. What that rule leaves out:

- **Contrast is computed against the actual adjacent color**, which for text on a translucent overlay is the composited result, not the token. Flatten first, then measure.
- **Text over images always fails somewhere.** The fix is a scrim (a solid or gradient layer of known opacity) or a text container, so the measured pair is deterministic. "Darken the photo" is not a spec; `rgba(0,0,0,0.55)` under the text block is.
- **Disabled elements are exempt from 1.4.3**, which is a conformance fact, not a licence: disabled text at 2:1 is invisible to a lot of people. Keep disabled states above 3:1 and rely on shape and position to signal state.
- **Placeholders are not exempt** — they are text. Most default placeholder greys fail, which is one more reason the label lives above the field (`components.md`).
- **Focus rings, input borders, toggle tracks, chart series, icons that carry meaning**: 3:1 against *both* neighbours (WCAG 1.4.11). A 1px light-grey border on white is the most common failure in otherwise careful systems.
- **Never state a contrast figure you have not computed.** A wrong ratio is worse than no ratio, because it stops anyone else from checking.

## Building the Palette

Order of construction — this order makes contrast solvable instead of a fight:

1. **Neutrals first.** Products are 80-95% neutral. Build the grey ramp, prove text pairs against every surface, and only then add hue. A palette that starts with the brand color ends up with unusable greys.
2. **One brand hue**, plus at most one secondary. `color-accent` is a role, not a shelf of options.
3. **Four semantic hues**: success, warning, danger, info. Danger and warning must be distinguishable without color (Rule 6) — in practice that means different icons and different text, always.
4. **Tint the neutrals with the brand hue** at very low chroma (a few percent). Perfectly neutral greys look sterile next to a saturated brand color; heavily tinted greys look muddy and break in dark mode.

## Ramps That Are Actually Usable

Generate a ramp by holding hue and stepping lightness — in a perceptual space, not in HSL. HSL lightness is not perceived lightness: `hsl(60 100% 50%)` (yellow) and `hsl(240 100% 50%)` (blue) are nominally identical and differ by roughly an order of magnitude in luminance. That single fact is why HSL ramps produce a yellow that fails contrast at the same step where blue passes.

With `color_notation: oklch`, generate in OKLCH: hold `H`, step `L` evenly, and **taper `C` at both ends** — maximum chroma is only available in the mid-lightness range, and a flat chroma produces steps that clip out of gamut at the top and bottom.

Practical ramp shape, 11 steps (0-1000 or 50-950, pick one and never mix):

| Step | Lightness | Typical role |
|---|---|---|
| 50 | ~0.98 | Page background (light) |
| 100-200 | 0.94-0.88 | Surfaces, hover fills, subtle borders |
| 300-400 | 0.80-0.70 | Borders, disabled fills, dividers |
| 500 | ~0.60 | The "brand" step; rarely usable for text on white |
| 600-700 | 0.52-0.44 | Text-safe on light surfaces; primary button fill |
| 800-900 | 0.35-0.25 | Body text, dark surfaces |
| 950 | ~0.18 | Highest-contrast text; dark-mode page background |

Two invariants make a ramp trustworthy: **the same step number means the same lightness across every hue**, and **contrast between two steps is predictable** — a gap of 5 steps clears 4.5:1 and a gap of 3 clears 3:1 across the whole ramp. Verify the pairs and publish them as an approved-pairs table; a ramp nobody has contrast-checked just moves the guessing later.

## Semantic Assignment

Primitives are never used directly (SKILL.md Rule 8, `tokens.md`). The semantic layer is the palette people actually consume:

| Semantic token | Light | Dark | Note |
|---|---|---|---|
| `surface-page` | neutral-50 | neutral-950 | Never pure white or pure black by default |
| `surface-raised` | white | neutral-900 | In dark mode, elevation goes *up* in lightness |
| `border-subtle` / `border-strong` | neutral-200 / neutral-400 | neutral-800 / neutral-600 | `border-strong` must clear 3:1 where it means something |
| `text-primary` / `text-secondary` | neutral-900 / neutral-600 | neutral-50 / neutral-400 | Secondary still clears 4.5:1 — it is text, not decoration |
| `action` / `action-hover` | brand-600 / brand-700 | brand-400 / brand-300 | The dark-mode pair is a *different step*, not the same one |
| `danger` / `warning` / `success` / `info` | -600 steps | -400 steps | Each pairs with an icon and a word |

Two rules that prevent the usual mess: **states are steps of the same ramp** (hover = one step darker in light mode, one step lighter in dark), and **there is exactly one focus-ring token**, used everywhere, 3:1 against every surface it can land on.

## Dark Mode Is Designed, Not Inverted

| Light-mode habit | What happens on dark | Do instead |
|---|---|---|
| Elevation by shadow | Shadows are invisible on dark surfaces | Elevate by raising surface lightness: page 950 → card 900 → popover 800 |
| Full-saturation brand color | Vibrates and blooms against dark backgrounds | Drop chroma ~20-40% and move up 2 ramp steps |
| Pure white text on pure black | Halation: the text smears for many readers, and OLED adds motion smearing | Surface ~`#121212`-ish, text ~neutral-50, target 12-16:1 rather than the full 21:1 |
| Same image assets | Bright photos become the only light source on the screen | Reduce image brightness slightly, or provide dark variants for illustrations and logos |
| Same semantic hues | Yellow and cyan get too bright; deep blue disappears | Re-derive every semantic pair from the dark steps and re-check contrast |
| Inverting the whole theme | Every shadow, border, and overlay inverts wrongly | Two token sets, one component layer |

Overlays and scrims invert too: a white scrim at 8% opacity is the dark-mode equivalent of a black one at 6%, not of a white one at the same value.

## Color Vision Deficiency

- Around **8% of men and 0.5% of women** of northern-European descent have a color-vision deficiency; deuteranomaly (reduced green sensitivity) is the most common by a wide margin, which is exactly why red/green is the worst possible pairing for status.
- **Simulate all three types** (deuteranopia, protanopia, tritanopia) plus grayscale. Grayscale catches most of it in one second and needs no plugin.
- **Vary lightness, not just hue**, between any two things that must be told apart. Two colors with the same luminance are the same color to a monochromat and nearly the same to everyone in a bright room.
- **Status without color**: an icon shape per state, plus the word. A red dot and a green dot are the same dot to a meaningful share of users.
- **Sequential data**: vary lightness monotonically; **categorical data**: cap at 6-8 hues, then switch to labels or shape (`data-visualization-design`).

## Gamut, Profiles and Where Color Breaks

- **sRGB is the safe floor**; Display-P3 covers noticeably more saturated greens and reds. Author in sRGB and treat P3 as an enhancement layer via a wide-gamut media query, unless every target device is known.
- **A hex value is only defined inside a profile.** The same `#FF3B30` shifts between an sRGB browser, a P3 display and a print profile. Screenshots exchanged between designers are the usual source of "the color changed".
- **Saturated screen blues, greens and oranges are unreachable in CMYK** and will come back duller. Choose a brand color you can hit on press, or accept and specify the print substitute — as a Pantone reference, not as a hope (`print.md`).
- **Do not sample brand colors from a JPEG or a screenshot.** Compression shifts values; take them from the source or the guidelines.
- **Ambient conditions destroy careful work**: outdoor, low-brightness and dark-room viewing all crush low-contrast pairs. Design at the floor, then check on a phone at 40% brightness — the condition most of your users are actually in.

## Write It Down

- **A palette created or changed for a brand** → the palette columns of its row in `## Brands` of `~/Clawic/data/designer/memory.md`, with the notation stated (`hex`, `oklch`).
- **The ramps and semantic assignments once implemented** → `## Token Sets`, naming where they live in code.
- **Why a hue was chosen, and what was rejected** — including a brand color abandoned for being unprintable or failing contrast — → `artifacts/color-decision-<brand>.md`, with its `## Boxes` line and a read condition naming the brand.
- **An approved-pairs contrast table** is a long text read whole → `artifacts/` as its own file, never a paragraph in `memory.md`.
