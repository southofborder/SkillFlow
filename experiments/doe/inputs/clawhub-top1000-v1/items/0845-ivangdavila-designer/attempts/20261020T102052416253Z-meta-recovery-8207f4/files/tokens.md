# Design Tokens and Systems

Scope: naming, structuring, theming, versioning and governing the values a product is built from. Pipeline mechanics from a design tool into platform code are `design-tokens`; deep component-library architecture is `design-system`. This is the layer a designer owns and is judged on.

**Contents:** [Three Tiers](#three-tiers) · [Naming](#naming) · [What Deserves a Token](#what-deserves-a-token) · [Theming](#theming) · [Format](#format) · [Versioning and Deprecation](#versioning-and-deprecation) · [Adoption Is the Only Metric](#adoption-is-the-only-metric) · [Governance](#governance) · [When Not to Build a System](#when-not-to-build-a-system) · [Write It Down](#write-it-down)

**Before creating a token**, read `## Token Sets` in `~/Clawic/data/designer/memory.md` and open whatever file its `## Boxes` line points to. Almost every "we need a token for this" is a token that exists under a name the asker did not think of, and duplicates are permanent.

## Three Tiers

| Tier | Example | Who may reference it | Changes when |
|---|---|---|---|
| Primitive (global) | `blue-600: #2563EB` | Only the semantic tier | The palette is regenerated |
| Semantic (alias) | `color-action: {blue-600}` | Components, and product code | The meaning is reassigned |
| Component | `button-primary-bg: {color-action}` | Only that component | The component's design changes |

**The rule that makes the system work: components consume semantic tokens only, never primitives.** A component referencing `blue-600` cannot be themed, cannot go dark, and cannot survive a rebrand — the tier structure exists exactly to make one value change propagate correctly.

The component tier is optional and often skipped in small systems. Skip it when a component uses fewer than about three distinct values that no other component shares; add it when a component's values need to vary independently of the semantic layer.

## Naming

Shape: `category-property-variant-state`, most-general to most-specific, always in that direction. `button-bg-primary-hover`, not `hover-primary-bg-button`. Sorting alphabetically then groups the family, which is the whole point.

- **`token_naming: semantic-only`** (default): names describe role — `color-text-secondary`, `space-inset-md`, `radius-control`.
- **`tier-prefixed`**: `global-blue-600`, `alias-color-action`, `cmp-button-bg`. Verbose, unambiguous, useful in large multi-brand systems.
- **`framework`**: follow the utility framework's names so designers and engineers speak one language, at the cost of leaking implementation into the design vocabulary.

Rules:
- **Never name after appearance.** `color-blue-primary` dies the day the brand goes green, and `space-16` dies the day the base unit changes.
- **Never name after a place.** `sidebar-bg` becomes wrong the moment a second surface uses it; `surface-raised` does not.
- **Use t-shirt sizes for scales** (`xs, sm, md, lg, xl`) or numeric steps (`100…900`) — pick one per category and never mix. Numeric is better for long ramps, t-shirt for short ones.
- **Same word, same meaning, everywhere.** If `subtle` means "low emphasis" in color, it cannot mean "small" in spacing.
- **No abbreviations that are not universal.** `bg` and `fg` are fine; `sec` (secondary? seconds?) is not.

## What Deserves a Token

| Tokenise | Do not tokenise |
|---|---|
| Color, in ramps and semantic roles | A value used exactly once, forever |
| Spacing scale, radius scale, border widths | Layout decisions specific to one page |
| Type sizes, weights, line heights, families, letter spacing | Content-driven measures |
| Elevation and shadow steps | An animation choreographed for one hero |
| Motion durations and easing curves | Magic numbers whose meaning nobody can name |
| Breakpoint values, container widths | — |
| Z-index layers | — |
| Opacity steps for overlays and disabled states | — |

The test: **if the value changing in two places at once would be a bug, it is one token; if changing it in two places independently is correct, it is two values.** A token created "for consistency" that nobody references is not free — it is a name someone else now cannot use.

## Theming

- **Theming swaps the semantic layer**, and only that layer. Primitives are the same set of colors; components are untouched. If a theme requires editing components, the tier boundaries were violated.
- **Two themes minimum from day one**, even if one ships later: building light-only guarantees a rewrite. Prove the structure with light and dark before adding brands (`color.md`).
- **Multi-brand adds a third dimension**, not a third tier: brand × theme × density. Each combination must be generatable, and the count is why the semantic layer must be small — 6 semantic color roles × 2 themes × 3 brands is manageable; 60 is not.
- **Nesting themes** (a dark card inside a light page) requires the semantic tokens to be scoped rather than global. Decide this early; retrofitting scope into a flat token set touches everything.
- **A theme is not a skin.** If a brand needs different spacing, radius and type, that is a second system that shares primitives, and calling it a theme sets an expectation nobody can meet.

## Format

The W3C Design Tokens Community Group format is the interchange standard worth targeting: each token is an object with `$value` and `$type`, references use `{group.token}` braces, and groups nest.

```json
{
  "color": {
    "blue": { "600": { "$value": "#2563EB", "$type": "color" } },
    "action": { "$value": "{color.blue.600}", "$type": "color" }
  },
  "space": {
    "md": { "$value": "16px", "$type": "dimension" }
  }
}
```

Two practical notes: **references, not copied values** — a copied hex is a token that will drift; and **one source of truth**, with every platform generated from it. If the design tool and the codebase both hold hand-maintained token lists, they are already different.

## Versioning and Deprecation

- **Semver, and a rename is a major.** Adding a token is a minor; changing a token's *value* within its meaning is a patch; changing its meaning or its name is breaking. Teams that treat renames as cosmetic are the reason design systems get abandoned.
- **Deprecate with an alias, never with a deletion.** The old name points at the new one for at least one minor version, with a deprecation note and a removal date.
- **Announce value changes that cross a threshold.** Changing `color-text-secondary` by one ramp step can move a screen from passing to failing contrast; publish the before/after ratio.
- **Changelog in the users' language**, per release: what changed, what breaks, what to do. A commit log is not a changelog.
- **The system has its own version in every spec** (`handoff.md`), so a bug can be traced to the version the screen was designed against.

## Adoption Is the Only Metric

A system nobody uses is a cost centre with good documentation. Track, in order of usefulness:

1. **Hardcoded values remaining** in the product code — count of raw hex values, raw px spacing, raw font sizes. This number falling is the system working; nothing else is evidence.
2. **Component coverage** — share of screens built from library components rather than local ones.
3. **Detached and one-off components** in the design files — every one is a vote against the library, and the reason it was detached is a bug report.
4. **Time to first component** for a new contributor.

Publish the first number. A system that cannot state how much of the product it covers is asking for trust it has not earned.

## Governance

- **One owner, or the system diverges.** The owner is not a committee; the committee reviews, the owner decides.
- **Contribution path in writing**: how to propose, who reviews, what the bar is, how long it takes. Without it, teams build locally and the system fossilises.
- **The third instance justifies the abstraction.** The first is a one-off, the second is a coincidence, the third is a pattern (SKILL.md Where Experts Disagree).
- **Document *when* to use a component, not just how it looks.** "Use for the primary action on a page; never more than one" prevents more misuse than any amount of anatomy diagram.
- **Every component page carries: purpose, when not to use it, all states, accessibility notes, and the tokens it consumes.** Missing the second item is why libraries fill with near-duplicate components.

## When Not to Build a System

Genuinely valid answers:
- **One product, one designer, under ~20 screens** — a token file and a component library in the design tool is the whole system; documentation is overhead.
- **The product's shape is still changing weekly** — abstractions extracted from a moving target get rewritten twice.
- **A campaign, a microsite, a pitch** — consistency with the brand matters, internal reuse does not.

In all three, still define **tokens** (colors, space, type) — that part is nearly free and prevents the fourth grey. It is the component library, documentation site and governance process that are premature.

## Write It Down

- **A token set created or restructured** → `## Token Sets` in `~/Clawic/data/designer/memory.md`: the naming convention in force, where the source of truth lives, which platforms consume it, and its current version.
- **A rename, deprecation or breaking change** → the same row, plus the migration note in `artifacts/tokens-<system>.md` — this is the record that stops the same rename being proposed again.
- **The full naming rules, tier boundaries and contribution path** → `artifacts/tokens-<system>.md`, its own file, with its `## Boxes` line and a read condition naming the system.
- **The adoption number and the date it was measured** → `## Token Sets`, refreshed each time it is measured; a single undated number is not a trend.
- **The user's standing naming preference** → `token_naming` in `config.yaml`, not in memory.
