# iOS and Android

Scope: what changes when the design leaves the browser. Platform conventions, safe areas, icon and store assets, and the divergences worth honouring.

**Contents:** [Honour the Platform or Own the Divergence](#honour-the-platform-or-own-the-divergence) · [Divergence Table](#divergence-table) · [Safe Areas and Screen Geometry](#safe-areas-and-screen-geometry) · [Units and Density](#units-and-density) · [Dynamic Type and Scaling](#dynamic-type-and-scaling) · [Touch Reality](#touch-reality) · [Navigation Models](#navigation-models) · [Permissions and Interruptions](#permissions-and-interruptions) · [App Icons](#app-icons) · [Store Assets](#store-assets) · [Mobile Web](#mobile-web) · [Write It Down](#write-it-down)

**Before designing a mobile surface**, read `## Surfaces` in `~/Clawic/data/designer/memory.md`: the platform, minimum OS version and framework decide half the constraints below, and a cross-platform framework changes which divergences are even available.

## Honour the Platform or Own the Divergence

Two coherent strategies, and one incoherent one:

- **Platform-native** — each platform's own patterns, navigation, controls and typography. Best learnability, two designs to maintain.
- **Brand-consistent** — one design system on both, with platform behavior only where violating it breaks the OS contract (back gesture, share sheet, permissions, text selection). Cheaper, and correct for products whose identity matters more than platform familiarity.
- **Accidental hybrid** — iOS patterns on Android because the designer works on a Mac. This is the failure mode: Android users get a back button that does nothing familiar and a bottom sheet that ignores the system gesture.

Pick one, record it in `## Surfaces`, and make every divergence deliberate.

## Divergence Table

| Concern | iOS | Android |
|---|---|---|
| Back | No system back button; in-app back at top-left, plus edge-swipe | System back gesture/button that must always work — an app that traps it is broken |
| Primary navigation | Tab bar at the bottom, ≤5 items | Bottom navigation ≤5, or navigation drawer for many destinations |
| Screen title | Large title collapsing to inline on scroll | Top app bar, optionally collapsing |
| Destructive confirm | Action sheet from the bottom | Dialog, centred |
| Sharing | System share sheet | System share sheet (different shape, same role) |
| Date and time entry | Wheel or inline calendar | Material picker dialog |
| Switch vs checkbox | Switch applies immediately | Switch applies immediately; checkboxes are common in forms |
| Typography | SF Pro; 17pt body default | Roboto; 16sp body default |
| Elevation | Blur, translucency, hairline separators | Shadow and tonal elevation surfaces |
| Haptics | Fine-grained system haptics | Coarser, device-dependent — never the only feedback |
| Text selection and context menus | System behavior; do not reimplement | System behavior; do not reimplement |

The three that are non-negotiable on Android: the back action, the share sheet, and the system font scale. The two on iOS: the safe areas and the home-indicator gesture region.

## Safe Areas and Screen Geometry

- **Content lives inside the safe area; backgrounds extend beyond it.** A background that stops at the safe-area edge leaves a visible band; content that ignores it gets covered by the notch or the home indicator.
- **The bottom inset is real estate you do not have.** The home indicator region needs roughly 34pt of clearance on gesture-navigation iPhones, and Android gesture navigation reserves its own strip. A button flush to the bottom edge is either unreachable or triggers the system gesture.
- **The keyboard is a viewport change, not an overlay.** Design the keyboard-open state for every screen with an input: what scrolls, what stays pinned, and whether the submit button is still reachable. This is the single most-skipped mobile state.
- **Landscape and tablet are not the phone stretched.** Decide explicitly: lock orientation, adapt, or use a split layout. "It reflows" is not a decision.
- **Foldables and floating windows** produce widths a phone design never sees; the intrinsic layout advice in `layout.md` handles most of it.

## Units and Density

- **pt (iOS) and dp (Android) are density-independent units**; 1pt/1dp ≈ 1 CSS px for design purposes. Design in these, never in device pixels.
- **Export raster assets at 1×, 2×, 3×** (iOS) and mdpi through xxxhdpi (Android), or ship vectors — SVG-derived vector drawables on Android, PDF/SF Symbols on iOS. Vectors remove the whole export matrix for icons.
- **The 8pt grid applies**, with 4pt sub-steps, exactly as on web (`layout.md`).
- **Hairlines are 1 physical pixel**, which is 0.33pt on a 3× display — specify "hairline", not "1pt", or the divider looks heavy.

## Dynamic Type and Scaling

- **System font scaling is a user accessibility setting and must be honoured.** iOS Dynamic Type reaches very large accessibility sizes; Android font scale goes well past 100%. A layout that only works at the default size fails a large share of older users.
- **Design three sizes**: default, one step up, and the largest accessibility size. What breaks: fixed-height rows, side-by-side labels, tab bars, and any button with a fixed width.
- **At the largest sizes, layouts should reflow to a single column** and horizontal pairs should stack. Design that reflow rather than letting text truncate.
- **Never disable scaling** to preserve a layout. Truncated text at the default size is a design bug; truncated text at 200% is an accessibility failure.
- **Icons scale with their labels**, or the row falls apart.

## Touch Reality

- **44pt (iOS) / 48dp (Android) minimum targets** (SKILL.md Rule 7), measured as the hit area.
- **The thumb reaches the bottom two-thirds comfortably**; the top corners of a large phone need a second hand. Primary actions belong at the bottom; destructive actions do not belong under the thumb's resting position.
- **Gestures need a visible alternative.** Swipe-to-delete, long-press menus and pull-to-refresh are discovered by a minority; every one of them needs a button path (and that path is what keyboard and switch-control users get).
- **No hover.** Anything the web design revealed on hover must be visible or reachable by tap on mobile.
- **Fingers cover the screen.** Confirmation and feedback should not appear directly under the point of contact; toasts near the bottom edge are hidden by the hand that just tapped.

## Navigation Models

- **Tabs for 2-5 parallel destinations** that users switch between frequently. Labels always; icon-only tab bars are not learned.
- **Stack navigation** for hierarchy: each push has a title and a back, and the back always returns where the user came from — never to a "home" they did not come from.
- **Modal for a self-contained task** with a clear cancel and a clear commit. On mobile, a modal is a full screen or a sheet, not a small centred box.
- **Drawers hide navigation** and should be reserved for genuinely secondary destinations (`components.md`).
- **Deep links must land in a coherent state.** A deep link into a detail screen needs a defined back destination, or the user hits the system back and leaves the app.

## App Icons

| Platform | Spec |
|---|---|
| iOS | 1024×1024 PNG source, square, fully opaque, no alpha, no pre-rounded corners — the OS masks it. Design inside the mask, not to the edge |
| Android adaptive | Two 108×108 dp layers (foreground + background); only the central 72 dp is guaranteed visible, and the safe circle inside is 66 dp — anything outside can be masked away by the launcher's shape |
| Android legacy | 512×512 for the store listing |
| Web / PWA | 192 and 512 PNG plus a maskable variant with content inside the central 80%-diameter circle (`brand.md`) |

Test every icon at its smallest real appearance (search results, notification, settings list), on a busy wallpaper, in a folder, and in dark mode. Text in an app icon fails at all of those; the only exception is a single letterform.

## Store Assets

- **Screenshots are marketing, not documentation.** The first two are what most people see: lead with the strongest value claim, use large legible captions, and show one idea per shot.
- **Required device classes change**; check the current requirements before producing the set, and produce the largest sizes first so smaller ones can be derived.
- **Localise the captions** — a screenshot set in one language for a multi-language listing wastes the highest-attention asset in the store.
- **The subtitle/short description is read more than the description.** Treat it as copy work (`copy.md`).
- **A feature graphic and a preview video** have their own specs per store; both are optional and both meaningfully affect conversion.
- **Every store submission is a review with rejection criteria**: privacy labels, permission justifications, and screenshots matching actual functionality. A screenshot showing a feature that does not exist is a rejection.

## Mobile Web

Distinct from native and frequently confused with it:

- **Inputs below 16px trigger zoom on focus** in mobile Safari; this is why `min_body_px` has a floor.
- **`100vh` does not match the visible viewport** while browser chrome is showing or hiding; use dynamic viewport units or accept the jump.
- **The address bar appears and disappears on scroll**, changing the viewport mid-interaction. Sticky bottom bars must survive it.
- **Tap highlight, overscroll and pull-to-refresh are browser behaviors** the design inherits; suppressing them removes feedback the user relies on.
- **Add-to-home-screen turns a site into an app** with no browser chrome — which means no back button, so the design must supply one.

## Write It Down

- **The platform strategy (native vs brand-consistent), the target platforms, minimum OS versions, and the framework** → the surface's row in `## Surfaces` of `~/Clawic/data/designer/memory.md`.
- **A deliberate divergence from a platform convention, and why** → `artifacts/spec-<surface>.md`, because it will be questioned in every review until it is written down.
- **The icon and screenshot export matrix actually produced** → the same spec artifact; the next release regenerates from it.
- **A store rejection and its cause** → `## Pain Points` in `memory.md`, and the resubmission cadence in `## Due` if one applies.
