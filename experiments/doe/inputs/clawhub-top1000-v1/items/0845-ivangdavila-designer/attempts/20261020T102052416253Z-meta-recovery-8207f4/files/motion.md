# Motion

Scope: how things move, how long, and when they must not. Motion is the cheapest way to make an interface feel authored and the cheapest way to make it feel slow.

**Contents:** [What Motion Is For](#what-motion-is-for) · [Duration](#duration) · [Easing](#easing) · [What to Animate](#what-to-animate) · [Continuity](#continuity) · [Reduced Motion](#reduced-motion) · [Feedback and Waiting](#feedback-and-waiting) · [Scroll and Parallax](#scroll-and-parallax) · [Specifying Motion](#specifying-motion) · [Write It Down](#write-it-down)

**Before specifying motion**, read `## Token Sets` and `## Brands` in `~/Clawic/data/designer/memory.md` — the durations and the signature curve may already be named; a second set is how a product ends up with eleven.

## What Motion Is For

Four jobs. Motion that does none of them is decoration and should be cut:

1. **Continuity** — showing where a thing came from and where it went, so the user does not re-orient
2. **Feedback** — confirming that an input was received, inside the perceptual window
3. **Attention** — directing the eye to a change the user did not cause
4. **Character** — a signature curve that makes the product feel like one product

The tell of decorative motion: remove it and nothing is harder to understand. Remove it.

## Duration

| Class | Range | Examples |
|---|---|---|
| Micro | 100-200ms | Hover, toggle, checkbox, button press, tooltip |
| Standard | 200-300ms | Dropdown, accordion, small panel, snackbar |
| Large | 300-500ms | Full-screen transition, sheet, page change |
| Ambient / looping | 800ms+ | Skeleton shimmer, progress indeterminate, background |

Two constraints on top of the bands:

- **Distance scales duration, but sub-linearly.** A card sliding 40px and a sheet travelling 600px should not share a value; roughly doubling the travel adds around half again to the duration, not double. A single global 300ms makes small things feel sluggish and large things feel abrupt.
- **Nothing an interaction depends on exceeds ~400ms** (Doherty threshold): past that the user has started waiting instead of acting. Exiting animations should be *faster* than entering ones — typically 0.7-0.8× — because the user has already decided.

## Easing

| Situation | Curve | Why |
|---|---|---|
| Entering the screen | ease-out, e.g. `cubic-bezier(0, 0, 0.2, 1)` | Fast start, soft landing — the element arrives and settles |
| Leaving the screen | ease-in, e.g. `cubic-bezier(0.4, 0, 1, 1)` | Accelerates away; nobody needs to watch an exit |
| Moving within the screen | ease-in-out, e.g. `cubic-bezier(0.4, 0, 0.2, 1)` | Both ends anchored to visible positions |
| Direct manipulation (drag, swipe follow) | linear, or a spring | The element must track the finger exactly |
| Emphasis / playful | overshoot or spring | Costs perceived speed; use once, as the signature |

**Never `ease` or `linear` as the default.** The CSS `ease` default is a weak in-out that reads as neither; `linear` reads mechanical because nothing physical moves at constant velocity. Pick one house curve for standard motion and one for entrance, name them as tokens, and let the exceptions be exceptions.

Springs are parameterised by stiffness and damping rather than duration, which makes them right for gesture-driven interfaces and awkward for coordinated sequences. Mixing spring and curve motion on the same screen reads as two products.

## What to Animate

- **Transform and opacity only** for anything that must be smooth. These are the properties that can be composited; animating width, height, top, left, margin or padding forces layout work on every frame and is what "janky" actually means.
- **To animate a size change**, animate a scale transform, or animate `grid-template-rows`/`max-height` knowing it is a layout animation and budgeting for it on a short distance.
- **Never animate anything on page load that blocks reading.** Content fading in after the paint is a self-inflicted delay measured by Core Web Vitals.
- **Cap concurrent animations at 2-3.** More reads as chaos regardless of individual quality.
- **Stagger lists at 20-50ms per item, capped at ~10 items**, then show the rest immediately. A 40-item stagger at 50ms takes two seconds and the user is already scrolling.

## Continuity

- **Shared-element transitions** are the highest-value motion in a product: the thumbnail becomes the header image, so the user never loses the object. Worth the cost when the same object appears on both screens.
- **Motion has direction and it must match the model.** Forward navigation enters from the trailing edge, back exits to the leading edge, and in RTL both mirror. A back transition that looks like a forward one silently breaks the user's map.
- **Overlays animate from their trigger** where possible: a menu that grows from the button it belongs to explains itself.
- **Dismissal reverses the entrance.** A sheet that slides up and fades out is two unrelated events.

## Reduced Motion

`prefers-reduced-motion: reduce` is set by users with vestibular disorders, migraine triggers and motion sensitivity, and it is a real request, not a preference to be second-guessed.

- **Replace, do not remove.** The feedback must survive: a 150ms opacity fade instead of a slide, an instant state change instead of a spring. Removing the transition entirely deletes the information that something changed.
- **What must go under reduced motion**: parallax, large translations, scale-and-rotate entrances, auto-playing loops, anything that moves across a large part of the viewport.
- **What may stay**: opacity fades, color transitions, small (<10px) movements, indeterminate progress that indicates work is happening.
- **Auto-playing media and carousels need a pause control regardless** of the media query, for anything that moves for more than five seconds (WCAG 2.2.2).
- **Nothing flashes more than three times per second** (WCAG 2.3.1). This is a seizure risk, not a style rule.

## Feedback and Waiting

Perceived speed is mostly about acknowledgement, not duration:

| Elapsed | What the interface owes the user |
|---|---|
| <100ms | Nothing — it reads as instant |
| 100ms-1s | Immediate visual acknowledgement of the input (pressed state); no spinner |
| 1-10s | A skeleton or spinner, and a statement of what is happening |
| >10s | Determinate progress, an estimate, and the ability to leave and come back |

- **Acknowledge the input within 100ms even when the result takes seconds.** The button press state is the acknowledgement; a control that does nothing for 400ms gets clicked twice.
- **Skeletons match the real layout** (`components.md`); a skeleton whose shape differs from the content causes a second visible reflow.
- **A progress bar that jumps to 90% and stalls is worse than none.** If real progress is unknown, use an indeterminate indicator and say what stage is running.
- **Front-load the perceived progress**: motion that starts fast and slows is perceived as shorter than the reverse for the same total time.

## Scroll and Parallax

- **Scroll-triggered reveals delay content and are a common accessibility complaint.** If used: trigger well before the element is in view, animate opacity and a small translation only, run once, and never gate essential content behind them.
- **Parallax is the highest-risk motion pattern for vestibular disorders.** It is also disabled by reduced-motion, so it can never carry meaning.
- **Scroll-jacking** — overriding the scroll speed or position — breaks keyboard, trackpad, screen readers and the user's expectations at once. There is no product case for it; there are occasional narrative-microsite cases, and they still need an escape.
- **Sticky elements must not consume more than ~20% of a small viewport.** A sticky header plus a sticky banner plus a cookie bar leaves a phone with a strip of content.

## Specifying Motion

A motion spec that an engineer can build has five fields, and no adjectives:

| Field | Example |
|---|---|
| Trigger | `Click on the row's expand control` |
| Property | `transform: translateY(-8px) → 0`, `opacity 0 → 1` |
| Duration | `200ms` (token `motion-duration-standard`) |
| Easing | `cubic-bezier(0, 0, 0.2, 1)` (token `motion-ease-entrance`) |
| Reduced-motion alternative | `opacity 0 → 1 over 150ms, no translation` |

Add stagger and delay when a sequence is involved. "Smooth", "snappy" and "delightful" are not specifications; they are the reason the built version does not match the prototype.

## Write It Down

- **Duration and easing values once agreed** → `## Token Sets` in `~/Clawic/data/designer/memory.md`, named (`motion-duration-micro`, `motion-ease-entrance`), because motion values scattered per component are how a product ends up with eleven of them.
- **The signature curve for a brand** → the row in `## Brands`, and the reasoning in `artifacts/brand-<name>.md` (`brand.md`).
- **A motion spec for a specific interaction** → the component's `artifacts/spec-<component>.md` alongside its state matrix, never as a separate orphan file.
- **A motion pattern the user rejected** — parallax, auto-play, scroll-jacking — → their constraints and exclusions key in `config.yaml`, so it is never proposed again.
