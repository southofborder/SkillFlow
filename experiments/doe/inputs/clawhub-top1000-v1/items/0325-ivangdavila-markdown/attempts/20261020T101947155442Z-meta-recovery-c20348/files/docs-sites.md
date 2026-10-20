# Documentation Sites — Generator-Specific Markdown

A static site generator is a second parser wrapped around the first. It rewrites links, consumes frontmatter, adds its own block syntax, and often preprocesses the file before Markdown ever sees it. The same `.md` renders one way on the forge and another on the site — by design.

**Before working on a doc set**, read `## Doc Sets` in `~/Clawic/data/markdown/memory.md` (or `docsets.md` if `## Boxes` points there) for the generator, the version and the lint state, and `## Quirks` for what that generator has already been observed doing.

**Contents:** [What Every Generator Changes](#what-every-generator-changes) · [Docusaurus](#docusaurus) · [MkDocs Material](#mkdocs-material) · [Jekyll](#jekyll) · [Hugo](#hugo) · [Sphinx / MyST](#sphinx--myst) · [VitePress, Astro Starlight, Quarto](#vitepress-astro-starlight-quarto) · [Includes and Reuse](#includes-and-reuse) · [Versioned Docs](#versioned-docs) · [Debugging a Build](#debugging-a-build)

## What Every Generator Changes

| Layer | What to check first |
|---|---|
| Link rewriting | Does `./page.md` become `/section/page`? Does the `.md` extension survive? Do anchors get re-slugified? |
| Frontmatter | Which keys are required, which are meaningful, which are silently ignored (`frontmatter.md`) |
| Preprocessing | Template languages that run **before** Markdown: Liquid (Jekyll), Go templates (Hugo shortcodes), Jinja (mkdocs-macros) |
| Block extensions | Admonition syntax, tabs, code-block attributes (`extensions.md`) |
| Sanitizer | Whether raw HTML survives — Hugo drops it by default |
| Navigation | Whether the sidebar comes from the filesystem, a config file, or frontmatter weights |
| Base URL | Whether absolute site links need a prefix (project sites served from `/repo/`) |

The first two account for most "it works on GitHub but not on the site".

## Docusaurus

- MDX for `.mdx`, CommonMark for `.md` in v3 — the escape hatch that saves a migration (`mdx.md`).
- Links: relative `.md` links are resolved and rewritten to routes, so `[setup](./setup.md)` works both on GitHub and on the site. That is the one generator where the ideal case is achieved.
- Frontmatter: `id`, `title`, `slug`, `sidebar_position`, `sidebar_label`, `tags`, `pagination_*`. Sidebar comes from `sidebars.js` or from the filesystem plus positions.
- Callouts `:::note Title` … `:::`; tabs via `<Tabs>`/`<TabItem>` components; code-block attributes `title=` and `{1,3-5}`.
- Heading ids can be pinned with `{#custom-id}` — use it for anything linked from outside (`links.md`).
- Broken-link checking is built in and fails the build by default (`onBrokenLinks: 'throw'`). Anchors are checked separately (`onBrokenAnchors`) and default to a warning.
- Versioned docs copy the whole tree into `versioned_docs/` — a fix applied only to `docs/` never reaches published versions.

## MkDocs Material

- Python-Markdown underneath: 4-space list nesting, extensions declared in `mkdocs.yml` under `markdown_extensions`.
- Links: relative `.md` paths are rewritten; a link to a file not in `nav` still builds unless `strict: true` (which is the right setting for CI).
- Admonitions `!!! note "Title"` with the body indented **exactly 4 spaces**; collapsible variant `???`. A 3-space body silently drops out of the block.
- Content tabs `=== "Tab"`, code annotations, `pymdownx.superfences` for Mermaid and nested fences, `pymdownx.snippets` for includes (`--8<-- "file.md"`).
- `attr_list` gives `{: .class }` on blocks and `{: #id }` for stable anchors; `md_in_html` is required for Markdown inside `<div>`.
- `mkdocs build --strict` turns warnings (missing nav entries, unresolved links) into failures — the single highest-value CI flag in this generator.

## Jekyll

- kramdown plus **Liquid**, and Liquid runs first. `{{` and `{%` are consumed **even inside fenced code blocks** — the classic break when documenting a template language. Wrap those blocks in `{% raw %}` … `{% endraw %}`.
- Frontmatter is mandatory: a file without it is copied verbatim, not processed. An empty block (`---\n---`) is the idiom.
- kramdown IALs: `{: .warning}` after a block, `{#id}` on a heading, `{:target="_blank"}` on a link.
- Relative links between `.md` files do not resolve to URLs automatically; use `{{ site.baseurl }}` or the `link` tag. This is why forked Jekyll sites so often have broken navigation.
- GitHub Pages runs a pinned, restricted Jekyll with a fixed plugin allowlist — a site that builds locally can fail there. Building with the `github-pages` gem locally is the only reliable check.

## Hugo

- Goldmark. **Raw HTML is dropped by default** (`markup.goldmark.renderer.unsafe: false`) — the most surprising default in this list. A page with `<details>` or `<img width>` silently loses it.
- Shortcodes `{{< name >}}` (rendered as HTML) and `{{% name %}}` (contents parsed as Markdown). They run before Markdown and are the sanctioned escape from the HTML restriction.
- Frontmatter in TOML (`+++`), YAML, or JSON; `draft: true` excludes from production builds and is the usual cause of "my page did not publish".
- Link resolution is by `relref`/`ref` shortcodes for build-time checking; bare relative `.md` links do not resolve.
- Page bundles: `index.md` inside a folder makes the folder the page and its images page resources — the tidiest way to keep images beside their page.

## Sphinx / MyST

- MyST is Markdown with directives: ```` ```{note} ```` and roles `` {ref}`label` ``. Everything Sphinx does — cross-references, autodoc, intersphinx — is reachable from Markdown.
- Directive bodies are indented and fence-delimited; the colon-fence form (`:::{note}`) is friendlier for nesting.
- Cross-references by label are the point of Sphinx: `(my-label)=` above a heading, then `` {ref}`my-label` `` — links that break the build when the target disappears, which no other generator in this list gives you for free.
- Builds are slow and warnings are the quality gate: `-W` turns them into errors, and a doc set without it accumulates broken references silently.

## VitePress, Astro Starlight, Quarto

- **VitePress**: markdown-it, Vue components in Markdown, `:::tip` containers, frontmatter drives layout. Anything in `{{ }}` is a Vue expression — the Jekyll trap in a different language.
- **Astro Starlight**: MDX-capable, component-driven, frontmatter schema is validated by Zod — a schema violation is a build error naming the field, which is a feature.
- **Quarto**: Pandoc under the hood plus executable code cells (`{r}`, `{python}`). Output documents are Pandoc's, so `conversion.md` applies directly; the same source produces HTML, PDF, and DOCX.

## Includes and Reuse

Every generator solves the "one paragraph in five pages" problem differently, and none of them is Markdown:

| Generator | Mechanism |
|---|---|
| MkDocs Material | `pymdownx.snippets`: `--8<-- "shared/warning.md"` |
| Docusaurus | Import a partial `.mdx` (conventionally `_name.mdx`) and render it as a component |
| Jekyll | `{% include file.md %}` from `_includes/` |
| Hugo | `{{< readfile >}}`-style shortcodes, or page resources |
| Sphinx/MyST | ```` ```{include} ```` directive |

Two rules regardless: an included file must not render on its own as a stray page (prefix it, or keep it out of `nav`), and includes break the forge view — the fragment shows as literal syntax on GitHub. Reuse text this way only for content that is genuinely identical everywhere; near-duplicates are better kept separate and reviewed.

## Versioned Docs

- Versioning copies the tree; from then on a fix has to be applied to every version the team supports, or backported deliberately.
- Decide the support window explicitly (current + previous major is the common default) and delete older versions from the build, or the sidebar becomes an archive nobody prunes.
- Links between versions must be absolute, or a reader silently jumps versions mid-journey.

## Debugging a Build

1. Reproduce locally with the same generator **version** as CI — most surprises are version differences, not content.
2. Turn on strict mode (`--strict`, `onBrokenLinks: throw`, `-W`). A build that only warns is a build whose warnings are already ignored.
3. Bisect the page: half the content, rebuild, repeat. Faster than reading the stack trace of a template engine.
4. Check the preprocessing layer before blaming Markdown — Liquid, shortcodes and Vue expressions run first, and their errors point at Markdown lines.
5. Compare against a page that works. In a doc set with one broken page, the diff between it and its neighbor is the answer.

**Write what the build taught you**: the generator, its major version and the strict-mode setting go in that doc set's row in `## Doc Sets` of `~/Clawic/data/markdown/memory.md`; every generator-specific behavior that cost time — the Liquid fence, the 4-space admonition body, the dropped HTML — goes in `## Quirks` naming the target; and a config that finally built (a `mkdocs.yml`, a `docusaurus.config.js` fragment, a CI job) is an `artifacts/` file with its `## Boxes` line in the same turn (`memory-template.md`).
