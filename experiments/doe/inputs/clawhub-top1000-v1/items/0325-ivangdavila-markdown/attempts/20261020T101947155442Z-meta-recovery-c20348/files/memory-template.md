# Working File Templates — Markdown

Read this file only when WRITING. `config.yaml` is what the user **declared**; `memory.md` and everything it indexes is what you **observed** or produced. An observation never overwrites a declaration.

## Where each thing goes

| Data | Home | How it grows |
|---|---|---|
| Declared preferences — Configuration table keys and preference areas alike | `~/Clawic/data/markdown/config.yaml` | Key by key, read-modify-write |
| Render targets, doc sets, house style, quirks, pain points, due dates, box index | `~/Clawic/data/markdown/memory.md` | Rewritten in place; stays small |
| Where their Markdown is published and what that parser does or refuses | `## Render Targets` in `memory.md`; `~/Clawic/data/markdown/targets.md` once it outgrows the section | One row per target |
| Documentation sets under management — repo, generator, lint state, owner | `## Doc Sets` in `memory.md`; `~/Clawic/data/markdown/docsets.md` once it outgrows the section | One row per doc set |
| Link checks, lint sweeps, accessibility passes and what they found | `~/Clawic/data/markdown/checks/<year>.md` | Append-only, cut by year |
| Things you produced that get re-read — a page or README template, a lint or CI config that finally passed, a pandoc recipe, a style guide, a docs-stack decision | `~/Clawic/data/markdown/artifacts/<kebab-name>.md` | Born as its own file, from the first one |
| The project a doc set belongs to | `~/Clawic/data/projects/<project>.md` (**shared**) | One file per project; named here, never copied |
| The person who owns or commissions a doc set | `~/Clawic/data/contacts/contacts.md` (**shared**) | One row per person; named here, never copied |
| **Anything durable this table does not name** | `~/Clawic/data/markdown/<plural-noun>.md`, or `artifacts/<kebab-name>.md` if it is a long text read whole | Name the file after what it holds, never after when it was made; add its `## Boxes` line in the same turn |
| Credentials of any kind | Nowhere under `~/Clawic/data/` | Pointer only — see Secrets |

Deciding where something unnamed goes, in this order: (1) would another skill want to read it — a project, a person, a host, a domain? Then it belongs in the shared box, not here. (2) Is it a text read whole when its subject comes up — a template, a config that took work to derive, a decision with its reasoning, a conversion recipe? Then `artifacts/`, its own file from the first one. (3) Is it one more row of something that accumulates? Then a section of `memory.md` until the split threshold.

## When to write

No permission needed; every write is announced in one line that names the file. Writes and deletions stay inside the paths declared in this skill's `configPaths`. A deletion is named in that same line, and in a shared box only rows this skill itself wrote are ever updated or removed.

| It happened | Write |
|---|---|
| A publishing destination was identified, or its parser refused something | `## Render Targets` |
| A repo, site or wiki of Markdown was worked on for the first time | `## Doc Sets` |
| A generator, theme, or plugin set was chosen or upgraded | The doc set's row, plus `## Quirks` if the upgrade changed behavior |
| A rendering difference cost time to find — an escape, an extension, a sanitizer, a slug rule | `## Quirks` |
| A convention was observed in their existing files (heading case, wrap, marker, table style) | `## House Style` |
| A lint, formatter, link-checker or CI config finally passed | `artifacts/`, with the rule exclusions and why each one is off |
| A pandoc or export invocation produced the right output | `artifacts/`, the exact command with its engine, filters and resource paths |
| A page, README, ADR or changelog shape got reused | `artifacts/`, as a template with its placeholders |
| A docs-stack or flavor decision was made | `artifacts/`, with what was rejected and why; one-line summary also to the shared project file |
| A link check, lint sweep or accessibility pass ran | A row in `checks/<year>.md`, and the date in `## Due` |
| The same render failure appeared twice | `## Pain Points`; the second occurrence earns a `## Quirks` line naming the target |
| The doc set belongs to a project or a client | The project file and the contacts row (shared), named here only |
| The user declared a preference | Its key in `config.yaml` |

## Start flat, split only when it hurts

Everything except artifacts, check logs and the shared boxes begins inside `memory.md`. Splitting is a procedure, not a suggestion:

1. Before appending to a section, count its entries.
2. If the append would take it past **~15 entries or ~40 lines of real content** — scaffolding, headings and comments do not count — then, in the same turn: create the new file in `~/Clawic/data/markdown/`, move the whole section into it, **delete the section from `memory.md`**, add its line to `## Boxes`, and append the new entry to the new file.
3. Keep the headings identical on both sides of the move, so the split is a copy-paste and never a rewrite.
4. Never leave a copy behind. If the same data ever appears in both places, the extracted file wins and the `memory.md` copy is deleted.

Artifacts are the exception: a template, a working config, a conversion recipe or a decision is born as its own file whatever its size, because it is read whole and only when its subject comes up.

## Secrets

Nothing under `~/Clawic/data/` ever holds a secret value — not the files named here, not files you create, not the document the user pastes in and asks you to keep. **A document is the densest source of secrets in this catalog**: quickstarts carry API keys, configuration pages carry connection strings, CI pages carry publish tokens, and a "here is my README, fix it" paste carries all three. Strip each value **before** writing and leave its pointer where the value was, in this shape: `<kind>:<locator>`.

`env:NPM_TOKEN` · `env:GITHUB_TOKEN` · `keychain:docs-deploy` · `1password:Work/Docs/confluence` · `bitwarden:CI/pypi` · `vault:secret/ci/docs` · `file:~/.netrc` · `file:~/.npmrc`

In a text, the pointer goes where the value was: `Authorization: Bearer <env:API_TOKEN>` and `https://<env:CI_USER>:<env:CI_TOKEN>@git.example.com/acme/docs.git`. Say in one line that you did it.

In this domain — **not secrets, keep them**: repository, package and site names, file paths, page slugs and anchor ids, public documentation and badge URLs, heading text, generator, theme and plugin versions, lint rule ids and config keys, environment *variable names*, image paths, port numbers in examples, usernames and handles.

**Secrets, strip them**: API keys and tokens inside code samples or curl lines, `.env` values, npm/PyPI/crates/registry publish tokens, CI secret values pasted from a settings page, connection strings carrying a password, basic-auth URLs (`https://user:token@host/…`), presigned or signed URLs (the signature is the credential), Slack/Discord/Teams webhook URLs, Confluence/Notion/Contentful API tokens, TLS and SSH private keys and passphrases, session cookies in a pasted HAR or log, license keys.

**Contents:** [config.yaml](#configyaml) · [memory.md](#memorymd) · [shared project and contact boxes](#shared-project-and-contact-boxes) · [artifacts/](#artifacts) · [checks/](#checks) · [split-out files](#split-out-files)

## config.yaml

Keys come from the Configuration table in `SKILL.md`, plus free-form keys nested under a preference area. Write a key only when the user states the preference.

**Writing is read-modify-write**: load the existing file, set or replace only the key just declared, keep every other key byte for byte. Never emit a `config.yaml` from this template — the template shows shape, not content. Create `~/Clawic/data/markdown/` if it does not exist.

```yaml
target_flavor: gfm
docs_generator: mkdocs-material
lint_tool: markdownlint
line_wrap: sentence
list_indent: 4
list_marker: "-"
raw_html: avoid
frontmatter_format: yaml
link_style: inline
table_style: compact

# Preference areas — free-form keys added as the user reveals them.
# A preference the user states is a declaration and belongs here, never in memory.md.
conventions:
  heading_case: sentence
  toc_depth: 3
  code_fence: backtick
tooling:
  link_checker: lychee
  format_on_save: true
  ci_blocks: false
accessibility:
  alt_text: required
localization:
  locale: en-GB
  smart_quotes: false
cadence:
  link_check: monthly
  lint_sweep: monthly
```

If you find a preference recorded in `memory.md`, move it here and note the move.

## memory.md

Write only the sections you have content for — a heading with nothing under it is noise, and it inflates the line count that decides a split. Never copy these hints into the user's file. `## Boxes` is the one section that is never dropped when `memory.md` is rewritten: deleting a line there orphans a file forever. This is what a populated file looks like:

```markdown
# Markdown Memory

## Status
status: ongoing
last: 2026-07-26

## Boxes
- Render targets and their quirks (17) → `targets.md`; read before writing or fixing any document
- Link and lint sweeps (2026) → `checks/2026.md`; read before a release or a docs audit
- Handbook mkdocs.yml that finally built → `artifacts/mkdocs-yml-handbook.md`; read before touching the handbook build
- Pandoc recipe for the client PDF → `artifacts/pandoc-pdf-client-report.md`; read when a PDF export is requested
- Page template for API reference pages → `artifacts/template-api-page.md`; read before adding a reference page

## Due
| What | Every | Last run | Next due |
|------|-------|----------|----------|
| Link check across docs/ | month | 2026-07-02 | 2026-08-02 |
| Lint sweep (markdownlint-cli2) | month | 2026-07-02 | 2026-08-02 |
| README badge and version refresh | quarter | 2026-05-10 | 2026-08-10 |
| Stale-page review (untouched 12 months) | quarter | 2026-04-18 | 2026-07-18 |

## Render Targets
| Target | Parser / flavor | Where it renders | Confirmed refuses | Notes |
|---|---|---|---|---|
| github.com README | GFM | repo front page | `{#id}`, `<style>`, `:emoji:` outside GitHub | alerts `> [!NOTE]` work |
| npmjs.com package page | GFM, own sanitizer | published package | repo-relative images | raw URLs pinned to the tag |
| handbook site | mkdocs-material | docs.acme.com | `> [!NOTE]`, `$…$` without arithmatex | `!!! note`, `--8<--` includes |
| Slack #eng | mrkdwn | messages | headings, tables, images | `*bold*` single asterisk, `<url\|text>` |

## Doc Sets
| Doc set | Repo / location | Generator | Lint | Pages | Project | Owner |
|---|---|---|---|---|---|---|
| Handbook | acme/handbook `docs/` | mkdocs-material 9.x | markdownlint-cli2, CI warns | 84 | handbook-2026 | Dana (see contacts) |
| SDK README set | acme/sdk-js | none | prettier only | 6 | — | — |

## House Style
Observed in acme/handbook: sentence-case headings, one sentence per line, `-` bullets at 4 spaces, tables unpadded, no emoji in headings.

## Quirks
mkdocs-material: admonition body must be indented 4 spaces or it silently leaves the block.
Jekyll site: `{{` inside a fence is still consumed by Liquid — needs `{% raw %}`.
GitHub: duplicate `## Configuration` headings produce `#configuration-1`; the handbook TOC generator does not know that.

## Pain Points
2026-05: a heading rename broke 12 inbound anchors from the marketing site. Stub anchors added; renames now grep first.
2026-06: prettier reformatted every table in one PR; review was unreadable. `table_style: compact` since.

## How They Work
Docs in the repo, reviewed in pull requests. Wants the corrected file, not an explanation. Will not accept a formatter that touches lines outside the change.

---
*Updated: 2026-07-26*
```

Rules that keep this readable next month:

- **`## Boxes`**: one line per file that exists — `<what> (<volume>) → <file>; read when <condition>`. Written in the same turn the file is created. Never delete a line without deleting the file it points to. A box with no index line does not exist.
- **`## Due`**: check it against today's date at the start of a session and state any overdue item in one line — a statement, not a question. Cadences the user has declared come from `cadence` in `config.yaml`; anything this skill schedules lands here.
- **`## Render Targets`**: `Confirmed refuses` is the column that pays for the table — it holds only things that were **observed** failing in that target, never things assumed from the Support Matrix. One row per destination, including chat and ticket systems: they are targets even though nobody calls them that.
- **`## Doc Sets`**: `Pages` is an approximate count with the date it was taken if it matters. `Project` and `Owner` are names pointing at the shared boxes, never copies of the records.
- **`## House Style`**: what their files already do, not what they should do. When the user *states* a convention it is a declaration and moves to `config.yaml`; this section holds what was inferred from reading their repo, and inferences yield to declarations.
- **`## Quirks`**: one line each, every line naming its target. A quirk with no target named is unusable — it is exactly the ambiguity that made it cost time the first time.
- `## Render Targets` and `## Quirks` are the headings `targets.md` gets, and `## Doc Sets` is the heading `docsets.md` gets, so each split stays a copy-paste.

| Status | Meaning |
|-------|---------|
| `ongoing` | Still learning their targets and house style |
| `complete` | Know where they publish, what each target refuses, and how they like files edited |

## Shared project and contact boxes

Documentation almost always belongs to something bigger. Those records live in shared boxes at `~/Clawic/data/projects/` and `~/Clawic/data/contacts/`, shared with every other Clawic skill — the user may have none of them installed, so the format and the protocol travel with this skill.

**Projects** — one file per project, `~/Clawic/data/projects/<project>.md`, from the first one. Identity is the file name (kebab-case project name). Read it before writing: if the file exists, append to it and update fields in place, never create a second file with a variant name. What this skill contributes is one section, and only when a docs decision has consequences outside the docs:

```markdown
## Documentation
Doc set: acme/handbook `docs/`, mkdocs-material, published at docs.acme.com.
2026-07-26 — decision: MkDocs Material over Docusaurus (no React need, search matters). Full reasoning: markdown artifacts/decision-docs-stack.md.
```

Closing a project is `status: done | cancelled — <date>` inside the file; never delete it, it is the record of what was delivered. Past roughly 20 closed projects they move to `projects/archive/<project>.md` without being renamed.

**Contacts** — `~/Clawic/data/contacts/contacts.md`, a single table:

```markdown
| Name | Key | Role | Preferred channel | Context | Last contact | File |
|------|-----|------|-------------------|---------|--------------|------|
| Dana Ruiz | dana@acme.com | handbook owner | email | approves docs structure changes | 2026-07-24 | — |
```

- **Identity is the `Key` column**: lowercase email, else the handle, else `<kebab-name>` plus a stable disambiguator. Read the file before adding and search for that key. If it is there, update the row in place — a second row for the same person is the failure this box exists to prevent.
- `Preferred channel` is the *kind* of channel (email, Slack, phone), not the address, so it can never serve as the key.
- **Scale cut**: one row per person while there are ≤15, or until one no longer fits its row. Past that, one file per person at `~/Clawic/data/contacts/<name>.md` and `contacts.md` becomes the index, keeping the `File` pointer column. If the folder already looks like that, follow it — never start a parallel `contacts.md`.
- **Foreign columns win.** If either shared file already exists with different columns, match what is there and add anything missing as a trailing note. Never rewrite a header you did not write.
- Only ever update rows this skill wrote. Removing a person is deleting their row and noting the date in `## Pain Points` of `memory.md`; leaving stale people in an inventory is how it stops being trusted.
- Never a credential in either box — an access reference is a pointer (`1password:Work/Docs/confluence`), never the value.

## artifacts/

One file per thing, at `~/Clawic/data/markdown/artifacts/<kebab-name>.md`, created the first time it exists. Canonical types here: **a template** (page, README, ADR, changelog, issue), **a lint/format/CI config that finally passed**, **a conversion recipe**, **a style guide**, **a docs-stack or flavor decision**. Every artifact opens with when to read it, and gets its `## Boxes` line in the same turn. Every secret inside it is already a pointer.

```markdown
# Template — API reference page
*Read before adding or reviewing a reference page in the handbook. Working as of 2026-07-26.*

Why it is shaped this way: parameters as a table because the site's search indexes table cells;
one H1 and no skipped levels because the sidebar is generated from the heading tree;
examples in fences with a language tag because the copy button needs one.

...the template, placeholders in <angle brackets>...
```

```markdown
# Config — markdownlint-cli2 for the handbook
*Read before changing lint rules or debugging a CI failure. Passing as of 2026-07-26.*

MD013 off for tables and code, on at 100 for prose — every URL was failing it.
MD033 allows details, summary, img, picture — the dark-mode logo needs picture.
MD024 siblings_only, because every endpoint page repeats "## Errors".
...the config file...
```

```markdown
# Recipe — client report PDF
*Read whenever a PDF export is asked for. Verified 2026-07-26.*

pandoc invocation, engine, fonts, resource path, filters, and what each flag is fixing.
Rejected: pdflatex — died on the emoji in the status column; weasyprint renders them.
```

```markdown
# Decision — MkDocs Material over Docusaurus
*Read before proposing a docs-stack change. 2026-07-26.*

Decision: ...one sentence...
Rejected: Docusaurus — MDX v3 would have made every existing page a build risk, no React components needed.
Cost: no component embedding; interactive demos link out.
Revisit when: the docs need versioned React components, or search stops being adequate.
```

The one-line summary of a decision also belongs in the shared `~/Clawic/data/projects/<project>.md`, with the full reasoning staying here and referenced by file name.

## checks/

The audit trail for sweeps. Append-only, one file per year, never rewritten. Its point is the delta: a link check with no previous run is a number, a link check with one is a trend.

```markdown
# Checks — 2026

| Date | Kind | Scope | Tool | Found | Fixed | Left |
|------|------|-------|------|-------|-------|------|
| 2026-07-02 | links | acme/handbook docs/ | lychee | 14 dead, 3 redirects | 14 | 3 redirects, upstream |
| 2026-07-02 | lint | acme/handbook docs/ | markdownlint-cli2 | 61 (52 MD013) | 9 | MD013 scoped off for tables |
| 2026-06-14 | a11y | docs/ images | manual | 22 images without alt | 22 | — |
```

- `Left` is the honest column: what was not fixed and why. A sweep log where everything is always fixed is a sweep log nobody believes.
- Recurring external breakage (a vendor that keeps moving its docs) earns a line in `## Quirks` naming the target, so the next sweep does not re-diagnose it.

## Split-out files

Created only by the split procedure above, never on day one. Each keeps the exact headings it had inside `memory.md`.

`targets.md` — `## Render Targets` and `## Quirks`. This is the file that answers "will this construct survive where we are publishing" without another round of trial and error, which is why the quirks live beside the targets rather than in a general notes pile.

`docsets.md` — `## Doc Sets`, with one `## <repo>` heading per repository once more than one is in play. It answers "what do we maintain, what builds it, and who owns it" before anyone opens a repo.
