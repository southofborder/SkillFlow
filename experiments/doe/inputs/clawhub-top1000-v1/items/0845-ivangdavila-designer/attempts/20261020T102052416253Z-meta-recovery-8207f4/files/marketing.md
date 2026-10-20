# Marketing Surfaces

Scope: pages, ads, decks and emails — the design work whose success is measured by a number someone else is watching. Conversion copywriting and funnel strategy are `landing-page` and `copywriting`; this is the design craft and the production constraints.

**Contents:** [Landing Pages](#landing-pages) · [Above the Fold](#above-the-fold) · [Page Structure](#page-structure) · [Performance Is Design](#performance-is-design) · [Ads and Social Formats](#ads-and-social-formats) · [Presentations](#presentations) · [Email](#email) · [Measuring It](#measuring-it) · [Write It Down](#write-it-down)

**Before designing a marketing surface**, read `## Brands` in `~/Clawic/data/designer/memory.md` and any `artifacts/voice-*.md` its `## Boxes` index names. Marketing is where a brand's voice and palette are most visible and most often improvised.

## Landing Pages

- **One page, one action.** The primary CTA repeats down the page — typically in the hero, after the proof section, and at the end — but it is the same action every time. A page with "Start free trial" and "Book a demo" competing equally converts worse than either alone.
- **The page answers three questions before anything else**: what is this, who is it for, why should I care. If a visitor cannot answer all three in five seconds, nothing below matters (`research.md` has the five-second test).
- **Design the page around the strongest true claim**, not around a layout. If the strongest claim is a number, the number is the hero; if it is the product itself, a real screenshot beats an abstract illustration.
- **Real product imagery beats stock and beats abstraction.** A cropped, legible screenshot with one thing highlighted outperforms a 3D render of nothing.
- **Every section earns its scroll.** Cut any section that does not add proof, remove an objection, or advance the action.

## Above the Fold

The fold is not a fixed line, but the first viewport is real. It contains, at minimum:

| Element | Requirement |
|---|---|
| Headline | The claim, in the visitor's words, ≤10 words |
| Subhead | Who it is for and the mechanism, one sentence |
| Primary CTA | Verb + object, visually dominant, above the fold on mobile too |
| Proof or product | One screenshot, one number, or one recognisable customer — not all three |

Two constraints people miss: **on a phone the first viewport is roughly 360×600 CSS px minus browser chrome**, which is far less than a desktop mock suggests — check the hero at that size before anything else; and **a full-viewport hero image pushes the actual content below the fold**, which is a decision to make deliberately rather than by template.

## Page Structure

A structure that works for most products, in order — deviate with a reason:

1. Hero (above)
2. Social proof strip — logos, a number, or a rating; small, immediately after the claim
3. The problem, stated in the visitor's language, so they recognise themselves
4. How it works — three steps maximum, each with a visual
5. Proof in depth — one case with a specific outcome beats five vague testimonials
6. Objection handling — pricing clarity, security, migration, "what if it doesn't work"
7. FAQ — the actual questions sales gets, not invented ones
8. Final CTA, with the same action and no new information

**Mobile source order is the real order** (`layout.md`): whatever the desktop grid does visually, the phone gets the DOM sequence, so design the single-column narrative first.

## Performance Is Design

Marketing pages are judged by Core Web Vitals and abandoned by slow loads, and almost every cause is a design decision:

| Metric | Good | The design decision behind it |
|---|---|---|
| LCP | ≤2.5s | The hero image or heading is usually the LCP element; its weight, format and priority are yours to budget |
| INP | ≤200ms | Heavy scroll effects and animation-on-scroll libraries are what blow this |
| CLS | ≤0.1 | Images without reserved space, late-loading fonts, and banners injected above content |

Practical budget: **hero image under ~200KB** in a modern format, correctly sized for the largest layout slot rather than the original export; **fonts subset and preloaded** with matched fallback metrics (`typography.md`); **no animation on the hero that delays its paint**; and **every image and embed gets an aspect-ratio box**. A design that specifies a 4MB hero photo has specified a failing LCP, regardless of who implements it.

## Ads and Social Formats

- **Design the smallest placement first.** A concept that survives a 320×50 banner and a square feed thumbnail will adapt upward; the reverse fails.
- **Aspect ratios worth designing as a set**: 1:1 (feed), 4:5 (feed, taller and higher-attention on mobile), 9:16 (stories and vertical video), 16:9 (video and wide placements), plus a 2:1-ish link preview. One layout stretched across all five is visibly wrong in at least three.
- **Assume no sound and no autoplay-with-audio.** Video needs burned-in or rendered captions and must communicate silently.
- **Safe zones**: story and reel formats have UI overlays at the top and bottom — keep text and logos well inside the centre band, and check each platform's current safe area before final export.
- **Text-in-image is deprioritised or restricted** by several ad platforms. Prefer a strong image plus platform text fields.
- **Link previews are designed assets**: a specific card image at the platform's ratio, the title, and the description. Left to chance, the platform crops the hero badly and picks the first paragraph.
- **Produce a variant set, not a single ad.** One concept in three visual treatments gives the media buyer something to test; a single execution gives them nothing.

## Presentations

- **One idea per slide, stated in the slide's title.** A title that is a sentence ("Churn is concentrated in month two") beats a label ("Churn") — the audience reads the title first and can then stop listening.
- **The 10/20/30 rule (Kawasaki)** is a useful discipline for a pitch: about 10 slides, 20 minutes, and nothing below 30pt. The type floor is the load-bearing part — it is what forces content out of the slide and into the speech.
- **Two documents, not one.** The presented deck is visual and sparse; the leave-behind is dense and readable alone. A deck that serves both does neither, and this is the most common deck failure.
- **Contrast for the worst room.** Projectors crush blacks and wash out lights; a palette that works on a laptop can be unreadable on a screen in daylight. Test at high ambient light and avoid thin type.
- **Build complex diagrams progressively**, one element per step, rather than revealing a finished diagram the audience then reads instead of listening.
- **Data slides state the takeaway in the title**, label directly instead of using a legend, and show one comparison (`data-visualization-design`).
- **16:9 by default**; check the actual display before designing 4:3 out of habit.

## Email

The most constrained surface in modern design, and the one most often designed as if it were a web page:

- **Table-based layout, inline styles.** Several major clients — Outlook on Windows above all — render with an engine that ignores modern CSS layout. Flexbox and grid are not available in practice.
- **600px content width** is the durable convention; wider is clipped or scaled in several clients.
- **Single column.** Multi-column email is where the rendering differences become visible.
- **Images are blocked by default in many clients.** The email must communicate with images off: real text for the message, alt text with styling on every image, and never an image-only email.
- **Web fonts are unreliable.** Specify a stack with a real fallback and design against the fallback, not the ideal.
- **Dark mode inverts unpredictably.** Some clients force-invert colors, some respect a media query, some do neither. Test the logo (transparent PNG with dark artwork disappears), the text colors and any near-white backgrounds.
- **Buttons are bulletproof tables**, not styled links, or they collapse in Outlook.
- **44px tap targets and 16px body minimum** — email is read on phones more than anywhere else.
- **Subject line and preheader are design surface**: the preheader is the visible continuation of the subject in most inboxes, and leaving it unset shows the first line of hidden text.
- **Test on real clients before sending.** Rendering differences are not predictable from the code.

## Measuring It

Design work on these surfaces has an outcome number attached, so state it up front:

- **Name the metric before designing** — signups, qualified demos, click-through, reply rate. "Looks better" is not an outcome and cannot be defended in the next review.
- **One change at a time when testing.** A redesigned page that changes the headline, the layout and the CTA teaches nothing about which one moved the number.
- **Small samples lie loudly.** A conversion difference on a few hundred visits is usually noise; the interval is wide (`research.md`).
- **Preference is not performance** — an A/B result outranks the whole review meeting, and the review meeting outranks nobody's taste.

## Write It Down

- **The page or campaign, its metric, and the result** → `## Findings` in `~/Clawic/data/designer/memory.md`, one line per test: what changed, what it moved, over what sample.
- **The page spec — structure, image budget, breakpoints, CTA rules, the variant set** → `artifacts/spec-<page>.md`, with its `## Boxes` line, so the next campaign starts from the version that worked.
- **The email template that finally rendered correctly everywhere**, with the client-specific hacks and why each is there → `artifacts/email-template-<name>.md`. This is the highest-value artifact in the domain: nobody rediscovers Outlook's behavior cheaply.
- **A client or stakeholder who owns the campaign** → the shared `~/Clawic/data/contacts/contacts.md`, by name only; the campaign itself, if it is a tracked engagement, → `~/Clawic/data/projects/<project>.md`.
