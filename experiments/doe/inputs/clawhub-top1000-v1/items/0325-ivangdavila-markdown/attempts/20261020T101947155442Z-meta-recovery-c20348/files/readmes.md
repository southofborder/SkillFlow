# READMEs and Package Pages — One File, Several Renderers

A README is the only Markdown file that is rendered by strangers' infrastructure. The same bytes go to the forge, to a package registry, to a mirror, and into search results, each with its own sanitizer and its own idea of where a relative path points. Write for the strictest of them.

**Contents:** [Who Renders It](#who-renders-it) · [Absolute, Pinned URLs](#absolute-pinned-urls) · [The First Screen](#the-first-screen) · [Structure That Works](#structure-that-works) · [Badges](#badges) · [Tables of Contents](#tables-of-contents) · [Images and Demos](#images-and-demos) · [Code Samples in a README](#code-samples-in-a-readme) · [Keeping It True](#keeping-it-true) · [Special Files](#special-files)

## Who Renders It

| Surface | Parser | Relative links | Raw HTML |
|---|---|---|---|
| github.com repo page | GFM + alerts, Mermaid, math | Resolved against the repo at that ref | Allowlist-sanitized |
| GitLab / Gitea / Codeberg | GFM-ish, each with extras | Resolved | Sanitized, different allowlists |
| npmjs.com package page | GFM subset, own sanitizer | **Not reliable** | Restricted |
| PyPI project page | CommonMark + GFM tables via readme_renderer | **Not resolved** | Strict allowlist; `long_description_content_type` must say `text/markdown` or the page shows raw text |
| crates.io | CommonMark + GFM | Not resolved | Sanitized |
| pkg.go.dev | Its own subset | Partially | Very restricted |
| Search engines / social cards | None — plain text | — | — |
| A terminal (`cat README.md`) | None | — | — |

The rule that follows: **the README is written to the intersection**, and anything richer belongs in the docs site the README links to.

## Absolute, Pinned URLs

- Repo-relative images (`![](docs/img/demo.png)`) render on the forge and break on npm and PyPI.
- The fix is an absolute raw URL: `https://raw.githubusercontent.com/<org>/<repo>/<tag>/docs/img/demo.png`.
- **Pin to a tag or a commit, never to a branch.** A `main` URL points at whatever that path becomes later — a rename or a redesign silently changes or breaks every published version's README, including releases from two years ago.
- Same rule for links into the repo: absolute and pinned, or the reader on the package page lands on a 404.
- The cost is a release step: bump the tag in the README URLs at release time, or generate the README from a template with the version substituted (an `artifacts/` template).

## The First Screen

Assume the reader sees roughly the first 20 lines before deciding. In order:

1. **Name and one sentence** that says what it is and for whom — not a tagline, a description. This line is also what search engines show.
2. **Badges**, one row, only the ones that inform a decision (below).
3. **The smallest thing that works**: install command plus a five-line example that produces visible output. Nothing before it.
4. **A link to the real documentation**, if there is a docs site.

Anything else — philosophy, comparison tables, sponsors, a table of contents for a short file — pushes the example below the fold and costs readers.

## Structure That Works

`Name → what it is → install → minimal example → configuration → common tasks → troubleshooting → contributing → license`

- One H1 (the project name), `##` for the sections above, no skipped levels (`structure.md`).
- Keep the README under roughly two screens of scrolling once the example is in. When it outgrows that, the overflow becomes `docs/` and the README links to it: a README nobody finishes is worse than a short one plus a link.
- Contributing, code of conduct, security policy and changelog are **separate files** the forge already links automatically (`CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`).
- The license goes in `LICENSE`; the README states which one in a line.

## Badges

- Every badge is an HTTP request on page load; a dead badge service leaves a broken image on the project's front page indefinitely.
- Useful: build status, current published version, license, and (sometimes) coverage. Everything else is decoration that pushes the example down.
- Badge images are cached by the forge's image proxy, so a stale badge is often a caching artifact, not a broken pipeline — check the underlying service before debugging the badge.
- Badges are images: give each one alt text (`![build status](…)`), or a screen reader announces a row of unnamed graphics (`accessibility.md`).

## Tables of Contents

- Only worth it above roughly five `##` sections; below that it costs more space than it saves.
- Anchors must be **derived** from the target's slug rule, including the `-1` suffix on duplicated headings (`links.md`). Hand-written TOCs rot within two edits.
- Generate it (a lint plugin, a pre-commit hook, or the generator's own TOC) and keep the generation step in CI, or accept that it will drift.
- GitHub renders an automatic outline from the heading tree in its own sidebar, which makes an in-file TOC redundant on that surface — but not on npm or PyPI.

## Images and Demos

- SVG for diagrams (crisp, small, theme-friendly), PNG for screenshots, animated GIF only when motion is the point — and then keep it short and under a few hundred KB, because it loads before anything else on the page.
- Dark mode: neutral images, or `<picture>` with `prefers-color-scheme` where HTML survives (`links.md`).
- A terminal recording is more convincing than a screenshot and is usually a GIF or an SVG player embed; the SVG player is a script in most implementations, so it is stripped by every sanitizer except the forge's.
- Every image needs alt text describing what it demonstrates, because it is missing on npm and PyPI more often than you think.

## Code Samples in a README

- The first example must be **copy-pasteable and complete** — imports included, no ellipses, no placeholder that fails at runtime. A sample that errors on paste is the fastest way to lose a reader.
- Language tag on every fence (`code.md`); the package page's highlighter uses it.
- No real credentials, ever, and no realistic-looking fake ones either: use `<env:API_TOKEN>` or an obviously synthetic value. A README key gets copied into production and a real one gets scanned by bots within minutes of the push.
- Show the output where it is short. "Prints `3`" saves the reader from running it.
- Pin versions in install commands only where the sample depends on them, and say which version the sample was verified against.

## Keeping It True

The README is the most-read and least-maintained file in a repo. Two mechanisms keep it honest:

- **Test the examples.** Extract the fenced blocks and run them in CI, or keep them in a tested example file and include it. Any README example not executed by something will eventually be wrong.
- **A refresh cadence** for badges, version numbers, pinned URLs and the install command — quarterly is the usual default, and it belongs in the `## Due` table rather than in someone's memory.

## Special Files

- `README.md` is rendered from the repo root, `docs/`, or `.github/` — the first one found.
- A profile README (a repo named after the user or org) renders on the profile page with a stricter feel; the same portability rules apply.
- `.github/` also holds issue and PR templates: Markdown with YAML frontmatter that GitHub consumes (`frontmatter.md`). Their frontmatter breaks silently on a typo, so validate before relying on them.
- Monorepos: each package needs its own README, because each package page renders its own file — a root README does not travel to the registry.

**Write what you standardize**: a README shape that gets reused, a badge set, or the release step that re-pins URLs is a template in `~/Clawic/data/markdown/artifacts/`, with its `## Boxes` line in the same turn. Every registry the project publishes to is a row in `## Render Targets` of `memory.md` with what it refused — npm and PyPI each have their own sanitizer, and finding out which one dropped the `<details>` block is exactly the work that should never be repeated (`memory-template.md`). A badge or version refresh gets scheduled as a `## Due` row.
