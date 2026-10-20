# Print and Physical Production

Scope: anything that leaves the screen — stationery, collateral, packaging, signage, merchandise, large format. The failure mode here is different from screen work: mistakes cost money and lead time, and they are discovered after 5,000 copies exist.

**Contents:** [Get the Spec Before Designing](#get-the-spec-before-designing) · [Document Setup](#document-setup) · [Resolution](#resolution) · [Color for Press](#color-for-press) · [Ink Limits and Black](#ink-limits-and-black) · [Type in Print](#type-in-print) · [Paper and Finishing](#paper-and-finishing) · [Packaging](#packaging) · [Signage and Large Format](#signage-and-large-format) · [Proofing and Preflight](#proofing-and-preflight) · [Handoff to the Printer](#handoff-to-the-printer) · [Write It Down](#write-it-down)

**Before setting up a print document**, read `## Brands` in `~/Clawic/data/designer/memory.md` for the CMYK and spot equivalents of the palette, and open any `artifacts/print-*.md` its `## Boxes` index names for the vendor's specifications from last time. Printer specs vary; the last job's spec sheet is worth more than any general rule below.

## Get the Spec Before Designing

Ask the printer these eight things first. Designing before you have them is how a job gets remade:

1. Flat size and finished size, and the fold or die layout
2. Bleed and safety margins they require
3. Color process: 4-color, spot, or a combination, and how many spots
4. Their preferred ICC profile and total ink limit
5. Substrate: stock, weight, coating, and whether it is uncoated (which changes everything about color)
6. File format and how they want fonts and images handled
7. Proof type and whether it is included
8. Lead time and the deadline for changes

The answers change the design, not just the export. An uncoated stock absorbs ink and shifts color noticeably; a die-cut changes the safety margin; a single spot color makes half the palette unavailable.

## Document Setup

| Setting | Default | Note |
|---|---|---|
| Bleed | 3mm (0.125in) on every edge | Anything touching the trim extends into bleed; nothing important sits in it |
| Safety margin | 3-5mm inside trim | Cutting tolerance is real; text at 2mm from the edge will be trimmed unevenly across the run |
| Fold safety | Larger than flat safety | Folds shift; keep content away from the fold line and account for creep in multi-page work |
| Units | mm or inches, matching the printer | Never px |
| Color mode | CMYK working space, with the printer's profile | See below |
| Page setup | Single pages, reader spreads only if asked | Printers impose; supplying imposed files usually causes an error |

**Perfect-bound and saddle-stitched work needs creep and gutter allowance**: inner pages of a thick booklet lose visible width toward the spine, and a spread crossing the gutter will not align.

## Resolution

- **300 ppi at final printed size** is the standard for photographic content. The phrase "at final size" is the whole rule: a 300 ppi image scaled up 200% in the layout is a 150 ppi image.
- **Line art and logos: vector, always.** A rasterised logo shows its edges on press.
- **Rasterised effects** (shadows, transparency flattening) should be at 300 ppi minimum; some printers ask for 600 ppi for fine line work.
- **Large format is the exception**: a billboard viewed from 30m can be 20-50 ppi at final size because the viewing distance does the work. Ask the printer for their ppi-at-size figure rather than assuming.
- **Never upscale to reach 300.** Interpolated pixels print as softness; the image is either large enough or it needs replacing.

## Color for Press

- **CMYK is subtractive and smaller than sRGB.** Saturated screen blues, greens, oranges and any neon will print duller. Convert early and design against the converted values, or the first proof is a shock.
- **Convert with the printer's profile**, not with a generic default. Coated and uncoated profiles differ enough to change a brand color's identity.
- **Spot colors (Pantone) for brand-critical elements**: an exact, repeatable color, matched across print runs and substrates, at the cost of an extra plate per spot. A logo on stationery is the classic case for a spot; a photo-heavy brochure is not.
- **Specify the spot's CMYK and RGB equivalents in the brand guidelines** (`brand.md`), because the same brand will be printed digitally, on screen, and on merchandise where spots are unavailable.
- **Look at a physical swatch book under the actual lighting.** No monitor shows a Pantone accurately, and metamerism means two colors that match under one light differ under another.
- **Registration**: elements built from multiple plates can shift a fraction of a millimetre. Avoid fine multi-color details and thin knockout type where a slight misregistration would be visible.

## Ink Limits and Black

- **Total Area Coverage** — the sum of C+M+Y+K at any point — has a ceiling, commonly around **300%** for coated web offset and lower for uncoated and newsprint. Over the limit, ink does not dry, sets off onto the next sheet and can block the press. The printer's number wins.
- **Rich black for large areas**: 100% K alone prints as a washed dark grey over a large field. A common recipe is around C60 M40 Y40 K100 — total 240% — but printers publish their own, and it must fit under their TAC.
- **Plain 100% K for body text**, always. Rich black text shows registration fringing at small sizes.
- **Never build black from a converted RGB black**: an unmanaged conversion produces a four-color black in body text, which prints fuzzy.
- **Reverse (knockout) type on a dark field needs weight.** Thin white type on rich black fills in; go a weight heavier and avoid fine serifs.

## Type in Print

- **Body text 9-11pt** for most printed matter; below 8pt is hard for many readers and impossible for some.
- **Hairlines: nothing thinner than 0.25pt.** A "hairline" width set in a design tool can render as a sub-device-pixel line that either disappears or prints unpredictably.
- **Print takes tighter leading than screen** — 1.2-1.4 is normal for body copy, where a screen would use 1.5.
- **Hyphenation and justification are usable in print** in a way they rarely are on screen, because the column width is fixed and can be tuned.
- **Outline or embed fonts on export**, and check the licence permits it (`typography.md`). Outlining is irreversible — keep an editable master.
- **Check for text on the fold** and text within the safety margin as a final pass; these are the two most common trim casualties.

## Paper and Finishing

- **Weight** in gsm: ~90-120 for letterheads and pages, ~250-350 for cards and covers. Heavier reads as more premium and costs more to post.
- **Coated stock** holds ink on the surface: sharper, more saturated, higher contrast. **Uncoated** absorbs: softer, duller, warmer, and it makes fine type feel heavier. This is a design decision, not a procurement one — choose it before finalising the palette.
- **Finishes** — spot UV, foil, emboss/deboss, die-cut, edge painting — each add a plate, a pass, cost, and lead time, and each needs its own artwork layer, usually a 100% spot named to the printer's convention.
- **Foil and emboss need minimum sizes and clearances**; fine detail fills in. Ask for the vendor's minimum stroke width before designing the artwork.
- **Ask for a paper dummy** for anything with volume: weight and opacity are physical properties that cannot be judged from a screen or a swatch.

## Packaging

- **Start from the dieline, always.** The printer or the converter supplies it; design inside it, on its own locked layer, and never move it.
- **Panels are separate designs that must work independently**: the front sells, the back informs, the side is what is visible on a shelf, and the top is what is seen in a bin.
- **Legally mandated content varies by product and market** — ingredients, allergens, weights, warnings, recycling marks, barcodes — and it usually has a minimum size requirement. Get the list before laying out; it is never small.
- **Barcodes need their quiet zone and their minimum size**, and they must be tested. A barcode scaled to fit is a barcode that fails at the till.
- **Substrate is not white.** Kraft, metallised film and clear plastic all change every color, and white ink may be needed as a base layer — which is another plate and another artwork layer.
- **Wrap and seam**: a design that crosses a seam will not align perfectly. Plan for it rather than discovering it.

## Signage and Large Format

- **Legibility scales with distance**: roughly **1 inch (~25mm) of cap height per 10 feet (~3m)** of viewing distance for comfortable reading, more for moving viewers and low light. Every sign starts with the distance, then the cap height, then the layout.
- **Fewer words at greater distances.** A sign read from a moving vehicle carries one message; a wayfinding sign at walking distance can carry a short list.
- **Contrast beats color** at distance, and dark-on-light generally outperforms light-on-dark in daylight.
- **Mounting height, viewing angle and glare** determine finish: matte for anything under lighting, and consider what will be reflected in a gloss panel.
- **Materials have their own color behavior**: vinyl, fabric, acrylic, powder-coated metal and direct-to-substrate printing each shift color differently. Get a material proof for anything expensive.
- **ADA-style and local accessibility regulations** may govern contrast, character height, tactile lettering and Braille on permanent room identification. Check the jurisdiction; this is a compliance requirement, not a preference.

## Proofing and Preflight

Preflight checklist before anything goes out:

1. Bleed present on every edge that needs it; nothing important inside the safety margin
2. All images ≥300 ppi at final size, all links embedded or packaged
3. Color mode correct, no stray RGB or unnamed spot colors, spots named exactly as the printer expects
4. Total ink under the printer's TAC; black text is 100% K only
5. Fonts embedded or outlined, with an editable master kept separately
6. Overprint settings checked — an unintended overprint makes white objects vanish, and it is invisible on screen
7. Transparency flattening previewed if the workflow requires it
8. Dielines and finish layers on their own layers, set to overprint, and excluded from the printed output
9. Page count correct and divisible by the binding's requirement
10. A separations preview inspected plate by plate

**Then get a proof.** A soft proof catches structure and content; a hard proof — printed on the actual stock — is the only thing that catches color, and it is the only proof worth signing. Sign it in writing, and keep it: it is the reference if the run is wrong.

## Handoff to the Printer

Package: press-ready PDF (their preferred standard, commonly a PDF/X flavour), a separate low-resolution PDF for approval, the editable source with fonts and links, and a spec sheet stating quantity, size, stock, colors, finishes, binding, delivery date and address. Name files so a stranger can identify them without opening anything.

The printer is a collaborator with more information than you have about their press. Send the file early enough for them to raise problems while there is still time to fix them, and treat their preflight report as authoritative.

## Write It Down

- **The printer or vendor** → a row in the shared `~/Clawic/data/contacts/contacts.md` (`Role: print vendor`), with their preferred contact channel; referenced elsewhere by name only.
- **Their specifications — bleed, profile, TAC, rich-black recipe, file format, lead time, minimum finish sizes** → `artifacts/print-<vendor>.md`, its own file, with its `## Boxes` line and a read condition naming the vendor. This artifact pays for itself on the second job.
- **The job itself — quantity, stock, finishes, cost, and what went wrong** → `artifacts/print-<job>.md`, or a row in the project file at `~/Clawic/data/projects/<project>.md` when the print run belongs to a tracked engagement.
- **A color that could not be matched in CMYK, or a stock that changed the palette** → `## Findings` in `memory.md`, because it constrains every future physical piece for that brand.
- **A reprint or stock reorder date** → a row in `## Due`.
