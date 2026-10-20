# Working File Templates — Designer

Read this file only when WRITING. `config.yaml` is what the user **declared**; `memory.md` and everything it indexes is what you **observed** or produced. An observation never overwrites a declaration.

## Where each thing goes

| Data | Home | How it grows |
|---|---|---|
| Declared preferences — Configuration table keys and preference areas alike | `~/Clawic/data/designer/config.yaml` | Key by key, read-modify-write |
| Brands, surfaces, token sets, findings, source locations, pain points, due dates, box index | `~/Clawic/data/designer/memory.md` | Rewritten in place; stays small |
| Long-form brand constraints the user wrote or dictated | `~/Clawic/data/designer/<name>.md`, pointed at by `brand_file` | One file, replaced when the user restates it |
| A brand: palette, type stack, icon set, logo rules, where the files live | `## Brands` in `memory.md`; `~/Clawic/data/designer/brands.md` once it outgrows the section | One row per brand |
| A surface being designed: platform, grid, breakpoints, framework, implementer | `## Surfaces` in `memory.md`; `~/Clawic/data/designer/surfaces.md` once it outgrows the section | One row per surface |
| Token sets in force: naming convention, source of truth, version, adoption | `## Token Sets` in `memory.md`; `~/Clawic/data/designer/token-sets.md` once it outgrows the section | One row per set |
| Research findings, test results and audit outcomes that changed a decision | `## Findings` in `memory.md`; `~/Clawic/data/designer/findings.md` once it outgrows the section | One line per finding |
| Usability sessions, design reviews, build reviews, accessibility audits | `~/Clawic/data/designer/sessions/<year>.md` | Append-only, cut by year |
| Things you produced that get re-read — brand guidelines, a component or handoff spec, a voice guide, an imagery brief, a decision with its rejected alternatives, a printer's spec sheet, an audit or research report, an email template that finally rendered | `~/Clawic/data/designer/artifacts/<kebab-name>.md` | Born as its own file, from the first one |
| People: clients, stakeholders, print vendors, collaborators | `~/Clawic/data/contacts/contacts.md` (**shared**) | One row per person, every skill's contacts in one file |
| A named engagement: brief, scope, rounds, milestones, decisions, estimate vs actual | `~/Clawic/data/projects/<project>.md` (**shared**) | One file per project |
| Font, icon, stock and tool licences; retainers — anything with a renewal date | `~/Clawic/data/finances/subscriptions.md` (**shared**) | One row per subscription |
| **Anything durable this table does not name** | `~/Clawic/data/designer/<plural-noun>.md`, or `artifacts/<kebab-name>.md` if it is a long text read whole | Name the file after what it holds, never after when it was made; add its `## Boxes` line in the same turn |
| Credentials of any kind | Nowhere under `~/Clawic/data/` | Pointer only — see Secrets |

Deciding where something unnamed goes, in this order: (1) would another skill want to read or write it — a person, a project, a subscription? Then it belongs in the shared box, not here. (2) Is it a text read whole when its subject comes up — a guideline, a spec, a decision with its reasoning, a report, a template? Then `artifacts/`, its own file from the first one. (3) Is it one more row of something that accumulates? Then a section of `memory.md` until the split threshold.

## When to write

No permission needed; every write is announced in one line that names the file. Writes and deletions stay inside the paths declared in this skill's `configPaths`. A deletion is named in that same line, and in a shared box only rows this skill itself wrote are ever updated or removed.

| It happened | Write |
|---|---|
| A brand was defined, or its palette, type stack, icon set or logo rules changed | Its row in `## Brands` |
| The guidelines, a colour or type decision, or a rejected direction came out of the session | `artifacts/` (`brand.md`, `color.md`, `typography.md`) |
| A surface got a grid, breakpoints, density, platform strategy or an implementer | Its row in `## Surfaces` |
| A token set was created, renamed, versioned, or its adoption was measured | Its row in `## Token Sets` |
| A component spec, handoff spec, voice guide, imagery brief or email template was agreed | `artifacts/` |
| A decision was made in a review that will constrain future work | `artifacts/decision-<topic>.md`, with what was rejected |
| A usability test, design review, build review or accessibility audit ran | A row in `sessions/<year>.md` |
| Any of those produced a finding that changed a decision | `## Findings` |
| The same finding appeared a second time, or the same objection keeps returning | `## Pain Points` — it is a systems problem now |
| A locale overflowed, a colour would not print, a technique was vetoed | `## Pain Points`, because it constrains every future design on that surface |
| A client, stakeholder or print vendor entered the picture | Their row in `contacts.md` (shared) |
| An engagement started, changed scope, or closed | Its file in `projects/` (shared) |
| A font, icon, stock or tool licence was bought or renewed | A row in `subscriptions.md` (shared), plus its renewal in `## Due` |
| Design files moved, or an export location was agreed | `## Source Files` |
| A recurring check was scheduled or run — re-audit, drift check, brand sweep, licence review | `## Due` |
| The user declared a preference | Its key in `config.yaml` |

## Start flat, split only when it hurts

Everything except artifacts, session logs and the shared boxes begins inside `memory.md`. Splitting is a procedure, not a suggestion:

1. Before appending to a section, count its entries.
2. If the append would take it past **~15 entries or ~40 lines of real content** — scaffolding, headings and comments do not count — then, in the same turn: create the new file in `~/Clawic/data/designer/`, move the whole section into it, **delete the section from `memory.md`**, add its line to `## Boxes`, and append the new entry to the new file.
3. Keep the headings identical on both sides of the move, so the split is a copy-paste and never a rewrite.
4. Never leave a copy behind. If the same data ever appears in both places, the extracted file wins and the `memory.md` copy is deleted.

Artifacts are the exception: a guideline, a spec, a report or a decision is born as its own file whatever its size, because it is read whole and only when its subject comes up.

## Secrets

Nothing under `~/Clawic/data/` ever holds a secret value — not the files named here, not files you create, not text the user pastes in and asks you to keep. A pasted licence email, a CMS or plugin config, an invoice, a contract or a deploy note is dense in credentials: strip each value **before** writing and leave its pointer in place, in this shape: `<kind>:<locator>`.

`env:FIGMA_TOKEN` · `keychain:adobe-id` · `1password:Work/Foundry/licence` · `bitwarden:Design/Stock` · `vault:secret/design/cms` · `profile:client-sftp` · `file:~/.config/fonts/licence.txt`

In a text, the pointer goes where the value was: `api_key: <env:FIGMA_TOKEN>`. Say in one line that you did it.

In this domain — **not secrets, keep them**: brand and product names, hex and OKLCH values, token names, typeface and foundry names, licence tier and seat counts, file paths and design-file URLs, component and surface names, breakpoint values, printer and vendor company names, project names, WCAG criteria and measured ratios, participant counts and audience segments.

**Secrets, strip them**: design-tool and CMS API tokens, font-foundry account passwords and download keys, stock-library account credentials, client SFTP/CMS logins, plugin licence keys and activation codes, invoice payment links carrying a token, bank details and tax identifiers, anything in a `.env` a client pastes, and any personally identifying detail of a research participant — names, emails, recordings and attributable quotes are never written at all, not even as a pointer.

**Contents:** [config.yaml](#configyaml) · [memory.md](#memorymd) · [shared contacts](#shared-contacts) · [shared projects](#shared-projects) · [shared subscriptions](#shared-subscriptions) · [artifacts/](#artifacts) · [sessions/](#sessions) · [split-out files](#split-out-files)

## config.yaml

Keys come from the Configuration table in `SKILL.md`, plus free-form keys nested under a preference area. Write a key only when the user states the preference.

**Writing is read-modify-write**: load the existing file, set or replace only the key just declared, keep every other key byte for byte. Never emit a `config.yaml` from this template — the template shows shape, not content. Create `~/Clawic/data/designer/` if it does not exist.

```yaml
design_tool: figma
target_platforms: [web, ios]
spacing_base_px: 8
type_scale_ratio: 1.25
min_body_px: 16
contrast_target: aa
a11y_posture: strict
color_notation: oklch
token_naming: semantic-only
css_framework: css-vars
brand_file: acme-brand.md
pricing_model: fixed

# Preference areas — free-form keys added as the user reveals them.
# A preference the user states is a declaration and belongs here, never in memory.md.
tooling:
  icon_set: lucide
  font_source: self-hosted
conventions:
  breakpoints: {sm: 640, md: 768, lg: 1024, xl: 1280}
  component_naming: "PascalCase, one word per concept"
platform:
  density: comfortable
  locales_that_must_fit: [de, fi]
  rtl: true
constraints:
  banned: [carousels, scroll-jacking, parallax]
cadence:
  a11y_audit: quarter
  drift_check: quarter
  licence_review: year
```

If you find a preference recorded in `memory.md`, move it here and note the move.

## memory.md

Write only the sections you have content for — a heading with nothing under it is noise, and it inflates the line count that decides a split. Never copy these hints into the user's file. `## Boxes` is the one section that is never dropped when `memory.md` is rewritten: deleting a line there orphans a file forever. This is what a populated file looks like:

```markdown
# Designer Memory

## Status
status: ongoing
last: 2026-07-26

## Boxes
- Acme brand guidelines → `artifacts/brand-acme.md`; read before any Acme visual decision
- Acme voice and terminology → `artifacts/voice-acme.md`; read before writing any interface or marketing copy
- Data-table spec → `artifacts/spec-data-table.md`; read before changing any table
- Navigation decision, Jan 2027 → `artifacts/decision-navigation.md`; read whenever navigation is questioned again
- Printer spec, Nord Press → `artifacts/print-nord-press.md`; read before setting up any print document
- Accessibility audit, web app 2026-06 → `artifacts/audit-webapp-2026-06.md`; read before the next audit or any contrast change
- Sessions and reviews (2026) → `sessions/2026.md`; read before planning research or claiming something was tested

## Due
| What | Every | Last run | Next due |
|------|-------|----------|----------|
| Accessibility re-audit, web app | quarter | 2026-06-11 | 2026-09-11 |
| Design-vs-build drift check | quarter | 2026-05-02 | 2026-08-02 |
| Brand consistency sweep across surfaces | half-year | 2026-02-20 | 2026-08-20 |
| Font licence renewal (Söhne, 3 seats) | year | 2026-03-01 | 2027-03-01 |

## Brands
| Brand | Owner | Palette | Type stack | Icon set | Guidelines |
|---|---|---|---|---|---|
| Acme | Acme (see contacts) | oklch ramps, action = blue-600 #2563EB | Söhne display / Inter text, 1.25 | lucide, 1.5px @24 | `artifacts/brand-acme.md` |
| Personal | us | neutral-only, single accent #0F766E | Inter, 1.2 | lucide | — |

## Surfaces
| Surface | Platform | Grid / breakpoints | Density | Framework | Implemented by | Notes |
|---|---|---|---|---|---|---|
| Web app | web | 12-col, 640/768/1024/1280 | compact | React + CSS vars | in-house | dark mode required |
| Marketing site | web | 12-col, same set | comfortable | Astro | agency | LCP budget 200KB hero |
| iOS app | ios | 4-col, safe areas | comfortable | SwiftUI | in-house | brand-consistent, not platform-native |

## Token Sets
| Set | Naming | Source of truth | Consumed by | Version | Hardcoded values left | Measured |
|---|---|---|---|---|---|---|
| acme-core | semantic-only | design-tool variables → DTCG JSON | web app, marketing, iOS | 2.3.0 | 41 | 2026-07-12 |

## Source Files
Design files: shared team space, project "Acme 2026". Exports: `~/Work/acme/exports/`.
Print masters kept with the vendor's job number in the filename.

## Findings
| Date | Surface | Finding | Evidence | What changed |
|---|---|---|---|---|
| 2026-06-11 | Web app | Filter state invisible after applying; users re-filtered | 4/5 sessions | Persistent filter chips + result count |
| 2026-05-04 | Marketing | Hero claim not understood in 5s by 3/5 | five-second test, n=5 | Headline rewritten to the outcome |
| 2026-06-11 | All | Brand green cannot clear 4.5:1 on white at any usable step | computed | Green demoted to accent-only; action stays blue |

## Pain Points
2026-04: German labels overflow every fixed-width button on the marketing site. All buttons now size to content with a min-width.
2026-02: The same "make the logo bigger" objection in three consecutive reviews — brand presence, not logo size; resolved by moving it into the sticky header.

## How They Work
Solo designer, two clients plus a personal product. Wants the artifact, not the reasoning, unless asked. Strict on accessibility. Will not accept stock photography.

---
*Updated: 2026-07-26*
```

Rules that keep this readable next month:

- **`## Boxes`**: one line per file that exists — `<what> (<volume>) → <file>; read when <condition>`. Written in the same turn the file is created. Never delete a line without deleting the file it points to. A box with no index line does not exist.
- **`## Due`**: check it against today's date at the start of a session and state any overdue item in one line — a statement, not a question. Every recurring thing this skill schedules belongs here, and the cadences come from `cadence` in `config.yaml` when the user has declared them.
- **`## Brands`**: one row per brand, however small. `Guidelines` points at the artifact; the row itself carries only what is needed to *avoid re-deriving* — palette anchor, type stack, icon set. Never paste the full palette here; that is what the artifact is for.
- **`## Surfaces`**: `Implemented by` is what makes handoff and drift questions answerable. When a surface belongs to a client engagement, name the project and let `~/Clawic/data/projects/<project>.md` hold the commercial detail.
- **`## Token Sets`**: `Hardcoded values left` is the adoption metric (`tokens.md`) and it is meaningless without `Measured` — a single undated number is not a trend.
- **`## Findings`**: date, surface, finding, evidence, what changed. **Evidence is mandatory**: `4/5 sessions`, `computed`, `A/B n=4,200`. A finding without evidence is an opinion that has been promoted by being written down, and it will outrank real evidence later.
- **`## Source Files`**: locations only — a folder, a workspace name, a job number. Never a URL carrying a token, never a login.
- **`## Pain Points`**: one line each, dated. This is the section that stops the same locale overflow, the same unprintable colour and the same recurring objection from being rediscovered.
- These headings are exactly the ones `brands.md`, `surfaces.md`, `token-sets.md` and `findings.md` get when their sections outgrow this file, so each split stays a copy-paste.

| Status | Meaning |
|-------|---------|
| `ongoing` | Still learning their brands, surfaces and standards |
| `complete` | Know their systems, constraints and register well |

## Shared contacts

Lives at `~/Clawic/data/contacts/contacts.md` and is shared with every other skill that deals with people — the user may not have any of them installed, so the format travels with this skill.

```markdown
# Contacts

| Name | Key | Role | Preferred channel | Context | Last contact | File |
|------|-----|------|-------------------|---------|--------------|------|
| Marta Ruiz | marta@acme.example | client, decides on brand | email | Acme rebrand; approves in writing, slow in August | 2026-07-18 | — |
| Nord Press | hello@nordpress.example | print vendor | email | Coated stock, TAC 300%, 5-day lead | 2026-06-30 | — |
```

- **Identity is the `Key` column**: the lowercase email, else a handle, else `<kebab-name>` plus a stable disambiguator. It is a column of the row, never implicit and never delegated to a per-person file — `Preferred channel` is the *type* of channel, not an address, so it cannot serve as the key.
- **Read the file before adding.** If the key is already there, update that row in place — never append a second row for the same person. Only add a row when the key is absent.
- **Update and retire only your own rows.** A row written by another skill is left alone; add what you know as a trailing note rather than rewriting their columns.
- **Retirement is part of the inventory.** When a relationship ends, delete the row and note the date in `## Pain Points` or the project file. An inventory that only grows stops being an inventory.
- **Scale cut**: one row per person while there are ≤15. Past that, or as soon as one person does not fit in a row, create `~/Clawic/data/contacts/<name>.md` per person and leave `contacts.md` as the index with the `File` pointer. If you arrive and the folder already looks like that, follow it — do not start a parallel `contacts.md`.
- **Foreign columns win.** If `contacts.md` already exists with a different column set, match its columns and add anything missing as a trailing note. Never rewrite its header.
- Never a password, a client portal login, or a research participant. Participants are recorded as a count and a segment, never as people (`research.md`).

## Shared projects

Lives at `~/Clawic/data/projects/<project>.md`, one file per engagement from the first one, shared with every skill that tracks work.

```markdown
# Acme rebrand

status: active
client: Marta Ruiz (see contacts)
started: 2026-05-04
fee: 14,000 EUR fixed, 50% deposit paid 2026-05-06

## Scope
Identity, guidelines, marketing site design. 2 concepts, 2 revision rounds. Copy supplied by client.
Out of scope: implementation, photography, print production management.

## Milestones
| Date | Milestone | Status |
|---|---|---|
| 2026-06-02 | Concepts presented | done — direction B chosen |
| 2026-07-15 | Guidelines delivered | done |
| 2026-08-30 | Marketing site design | in progress |

## Decisions
2026-06-02 — Direction B. Rejected A (too close to a competitor's silhouette). See `designer/artifacts/decision-identity-acme.md`.

## Rounds
Contracted 2. Used 1. Round 2 opened 2026-07-20.

## Estimate vs actual
Estimated 22 days. Logged 19 at 2026-07-26.
```

- **Identity is the project name**, which is the filename slug. Read the folder before creating a file: an engagement that already has one gets updated, never duplicated.
- **Baja is a status, not a deletion**: `status: done | cancelled — <date>` inside the file. It is the record of what was delivered and the basis of the next estimate. Past roughly 20 closed projects, move them to `projects/archive/<project>.md` without renaming.
- **People are referenced by name only**, and live in `contacts.md`. Money with a renewal date lives in `subscriptions.md`. Duplicating either here is how two skills start contradicting each other.
- **Amounts carry their currency in the value** (`14,000 EUR`), and an estimate carries the date it was made.
- **Foreign structure wins.** If the file already exists with different headings, add to what is there rather than reorganising it.

## Shared subscriptions

Lives at `~/Clawic/data/finances/subscriptions.md` and is shared with every skill that touches recurring money.

```markdown
# Subscriptions

| Name | What for | Amount | Cycle | Renews | Seats / cap | Reference |
|------|----------|--------|-------|--------|-------------|-----------|
| Söhne (Klim) | Brand display typeface, web + desktop | 480 EUR | one-off, web tier | — | 3 seats, 250k pageviews | `1password:Work/Klim` |
| Design tool team plan | Design files | 45 EUR | month | 2026-08-14 | 3 editors | `1password:Work/Design tool` |
| Acme retainer | Ongoing design, 3 days/month | 1,200 EUR | month | 2027-01-01 | — | project: Acme rebrand |
```

- **Identity is the `Name`.** Read the file before adding; if the name is there, update in place. Only the absence of the name justifies a new row.
- **`subscriptions.md` is a single table and is not split** — it stays small because a cancellation deletes the row. Note the cancellation date in `## Pain Points` or the project file, not as a lingering row.
- **Amounts carry their currency in the value** (`480 EUR`), because rows from other skills are in other currencies and someone will add the column up.
- **`Reference` is a pointer, never a key or a card number.** A licence key is a credential.
- **Every row with a `Renews` date also gets a row in `## Due`** of `memory.md`, or the renewal is invisible until the invoice.
- **Foreign columns win.** Match the header that is already there and add what is missing as a trailing note.

## artifacts/

One file per thing, at `~/Clawic/data/designer/artifacts/<kebab-name>.md`, created the first time it exists. Canonical types here: **brand guidelines**, **a colour or type decision with what it rejected**, **a component or handoff spec**, **a voice and terminology guide**, **an imagery brief** (illustration style, photography direction, and the provenance of every generated image — tool, model or version, prompt, seed, where it is used), **a printer's spec sheet**, **an accessibility audit or research report**, **an email template that finally rendered everywhere**, **a design decision from a review**. Every artifact opens with when to read it, and gets its `## Boxes` line in the same turn. Every secret inside is already a pointer.

```markdown
# Brand guidelines — Acme
*Read before any Acme visual decision. Current as of 2026-07-15.*

Mark: combination; wordmark for wide slots, monogram for square.
Clear space: one monogram counter width. Minimum: lockup 120px / 25mm, mark 24px / 8mm.
Palette: full ramps, semantic assignments, approved contrast pairs.
Type: Söhne display / Inter text, ratio 1.25, licensed weights 400 and 600 only.
Rejected: the green as an action colour — cannot clear 4.5:1 on white at any usable step.
```

```markdown
# Spec — data table
*Read before changing any table. v1.4, 2026-07-20, against acme-core 2.3.0.*

Anatomy · every state · tokens by name · breakpoint behavior · content cases
(longest, empty, zero/one/many, 1,204,382, long-locale, RTL) · motion · a11y annotations · copy.
```

```markdown
# Decision — bottom navigation on iOS, not a drawer
*Read whenever navigation is questioned again. 2026-01-14.*

Decision: ...one sentence...
Who decided: Marta Ruiz, on the tree-test result.
Rejected: drawer — tree test, 30 participants, 41% found the settings path versus 78%.
Revisit when: destinations exceed five.
```

If the work belongs to a tracked engagement, the one-line decision summary also belongs in `~/Clawic/data/projects/<project>.md`, with the full artifact staying here and referenced by name.

## sessions/

Everything with a date and people in it: usability tests, design reviews, build reviews, accessibility audits. Append-only, one file per year, never rewritten.

```markdown
# Sessions — 2026

| Date | Type | Surface | Who | Method / scope | Outcome |
|------|------|---------|-----|----------------|---------|
| 2026-05-04 | usability | Marketing | 5 prospects | five-second test | Hero claim missed by 3/5 → rewritten |
| 2026-06-11 | a11y audit | Web app | solo | AA, design-time check + keyboard pass | 2 critical, 6 serious → `artifacts/audit-webapp-2026-06.md` |
| 2026-07-02 | build review | Web app | with engineering | spec v1.3, all states | 1 serious (focus lost on modal close), 4 minor; 41 hardcoded values |
| 2026-07-20 | design review | iOS app | Marta + eng lead | direction sign-off | Approved; logo size objection resolved |
```

- **Participants are a count and a segment**, never names, contact details, recordings or attributable quotes (`research.md`).
- **`Outcome` names the destination** when it produced one: the artifact, or the `## Findings` line. A session row with no outcome is a diary entry.
- Drift counts recorded here are the same number tracked in `## Token Sets`; write it in both, identically, or the trend is unreadable.

## Split-out files

Created only by the split procedure above, never on day one. Each keeps the exact headings it had inside `memory.md`.

`brands.md` — `## Brands`, one `## <brand>` subsection below the table once a brand needs more than a row. This is the file that answers "what are we allowed to use" without opening a guidelines document.

`surfaces.md` — `## Surfaces`, plus `## Source Files` if that section moves with it. The file that answers "who builds this and against which system version".

`token-sets.md` — `## Token Sets`, same columns. Once split, the table stops being one row per set and becomes one row per *measurement*, so the adoption trend accumulates in place: that trend is the reason this file exists, because a single undated count proves nothing and the curve is the only argument that keeps a system funded.

`findings.md` — `## Findings`, chronological, newest last. The file that turns "I think users prefer" into a lookup with evidence attached.
