# Conversion — Markdown In, Something Else Out (and Back)

Conversion is where Markdown meets formats with a real layout model, and where every ambiguity you got away with becomes visible. Pandoc is the general answer; the work is in the flags, and the flags are worth writing down once.

**Before building an export**, check `## Boxes` in `~/Clawic/data/markdown/memory.md` for a stored recipe in `artifacts/`: a working pandoc invocation is a derived artifact, not a command anyone remembers.

**Contents:** [Pandoc's Model](#pandocs-model) · [To PDF](#to-pdf) · [To DOCX](#to-docx) · [To HTML](#to-html) · [To Slides and Everything Else](#to-slides-and-everything-else) · [HTML Back to Markdown](#html-back-to-markdown) · [Other Sources](#other-sources) · [What Never Survives](#what-never-survives) · [Building a Repeatable Pipeline](#building-a-repeatable-pipeline)

## Pandoc's Model

Source → AST → target. Anything with no representation in the AST, or none in the target, is dropped — silently, unless you ask for warnings.

- Name the input dialect explicitly: `-f gfm` (or `commonmark_x`, `markdown` for Pandoc's own superset, `markdown_strict` for Markdown.pl behavior). The default is Pandoc's own, which enables extensions your source may not intend.
- Extensions attach to the format: `-f gfm+footnotes-hard_line_breaks`. `+` enables, `-` disables. This is how you turn on exactly what the source uses.
- `--standalone` produces a complete document with a header; without it you get a fragment (correct for embedding, wrong for a file you open).
- `--wrap=none|auto|preserve` and `--columns=N` control line wrapping in **text** outputs. `--wrap=none` is right for anything a diff will see.
- `--resource-path=.:img:docs` tells Pandoc where to find relative images; an image it cannot find is dropped from PDF and DOCX with a warning most people never read. Add `--fail-if-warnings` in CI.
- `--metadata title="…"` supplies what frontmatter would; missing metadata is the usual cause of an empty title page.

## To PDF

PDF goes through an engine, and the engine choice decides more than the flags.

| Engine | Strengths | Fails on |
|---|---|---|
| `pdflatex` | Fast, ubiquitous | **Unicode and emoji** — the classic "Missing character" failure |
| `xelatex` / `lualatex` | Full Unicode with `-V mainfont`, CJK with the right font | Slow; needs a LaTeX install |
| `weasyprint` | CSS layout, no LaTeX, renders emoji, easy page headers | Weak on complex math |
| `typst` | Fast, modern, no LaTeX install | Younger ecosystem, fewer templates |
| `wkhtmltopdf` | HTML fidelity | Old WebKit; unmaintained rendering quirks |

Practical notes:

- Emoji in a status column is the most common reason a PDF build dies with `pdflatex`. Switch engine before switching content.
- `-V geometry:margin=1in`, `-V fontsize=11pt`, `--toc --toc-depth=3`, `--number-sections` cover most of what a report needs.
- Code blocks do not wrap in PDF: long lines are clipped at the margin. Break them at ~80 columns in the source, or pass a highlighting style that wraps.
- Wide tables overflow the page. Reduce columns, rotate the page for that section, or accept that a wide table wants HTML.
- Page breaks: a raw `\newpage` (LaTeX engines) or a CSS `page-break-before` rule (weasyprint). Both are engine-specific and belong in the recipe, not in the source, unless the source only ever becomes a PDF.

## To DOCX

- `--reference-doc=reference.docx` is the whole game: Pandoc reads the **styles** from that file and applies them. Generate a starting point with `pandoc -o reference.docx --print-default-data-file reference.docx`, restyle it in Word, and commit it.
- Styles map by name (`Heading 1`, `Source Code`, `Table`). A style renamed in the reference doc stops being applied — silently.
- Images are embedded; sizes come from the source attributes or the image DPI. A 3000-pixel screenshot arrives full-page.
- Tracked changes, comments and complex layout are one-way: the round trip back is lossy, and the destination for that work is `word-docx`.
- For a document that will be edited in Word by other people, deliver the DOCX as the artifact and keep the Markdown as the source of truth only if you own every future edit. Two sources of truth is how the versions diverge.

## To HTML

- `--standalone --css=style.css --self-contained` (older Pandoc) or `--embed-resources --standalone` (current) produces a single portable file with images and CSS inlined — the right shape for an email attachment or an offline report.
- `--toc` builds a table of contents; `--section-divs` wraps sections for styling; `--highlight-style=…` sets code colours (`--no-highlight` to disable).
- `--mathjax` or `--katex` for math; without one, `$…$` arrives as literal text (`extensions.md`).
- Mermaid needs a filter (`mermaid-filter`) or pre-rendered SVGs — Pandoc has no diagram engine.
- For email, inline the CSS (email clients strip `<style>` in many cases) and expect tables to be the only reliable layout primitive.

## To Slides and Everything Else

- `-t revealjs -s` (HTML slides), `-t beamer` (PDF slides), `-t pptx`. Slide boundaries come from heading levels — `--slide-level=2` is the usual choice, and horizontal rules also break slides.
- `-t man` for manual pages, `-t rst`/`-t asciidoc`/`-t org` for other markup families, `-t ipynb` for notebooks, `-t json` for the AST when you need to script something Pandoc has no flag for.
- `--lua-filter` is the extension point for everything else; a filter is easier to maintain than a chain of `sed` calls, and it operates on the AST rather than the text.

## HTML Back to Markdown

- `pandoc -f html -t gfm --wrap=none` is the baseline. Add `--strip-comments`.
- Expect: `colspan`/`rowspan` flattened, nested tables mangled, styling lost, and `<div>` soup reduced to paragraphs. That loss is usually the point.
- **Turndown** (JavaScript) is the better tool when the source is a live DOM (a scraped page, a rich-text editor) because it sees the rendered tree, not the served HTML.
- Always clean afterwards: collapse the blank-line storms, re-fence code that came through as indented, and re-check every link — relative URLs in the source HTML resolve against the original site, not your repo (`links.md`).
- Round-tripping HTML → Markdown → HTML is never lossless. Convert once, edit the Markdown, and delete the HTML.

## Other Sources

- **DOCX in**: `pandoc -f docx -t gfm --extract-media=img` pulls images out to a folder; without it they are lost. Tracked changes come in as `--track-changes=accept|reject|all`.
- **Notebooks**: `-f ipynb` keeps outputs by default; `--to markdown-raw_html` strips the HTML that notebook outputs are full of.
- **Google Docs / Confluence exports**: export to DOCX or HTML first, then convert; their Markdown exports are dialect-specific and usually worse than the round trip.

## What Never Survives

Regardless of tooling: interactive components (MDX), Mermaid without a filter, math without an engine flag, generator shortcodes (Liquid, Hugo, Docusaurus tabs), collapsible `<details>` in PDF, task-list interactivity, and image sizing expressed in non-standard syntax. Check the document for these **before** promising an export, not after the build.

## Building a Repeatable Pipeline

A one-off invocation becomes a permanent obligation the moment someone likes the output.

1. Put the invocation in a `Makefile`, a script, or a CI job — never in chat history.
2. Pin the Pandoc major version and the engine; output changes across versions.
3. Commit the reference doc, the CSS, the template and the filters beside the source.
4. Build in CI on every change to the source, and publish the artifact, so nobody has to reproduce a local toolchain.
5. Add `--fail-if-warnings` once the warnings are clean: that flag is what turns "the image quietly disappeared" into a red build.

**Write the recipe**: the exact command, the engine, the fonts, the resource path, each filter and **what each unusual flag is fixing**, in `~/Clawic/data/markdown/artifacts/pandoc-<purpose>.md`, with its `## Boxes` line in the same turn (`memory-template.md`). Note what was rejected and why — "pdflatex died on the emoji, weasyprint renders them" is the line that stops the next person from re-testing four engines. If the pipeline runs against a client or project deliverable, name the project in the shared `~/Clawic/data/projects/<project>.md` and keep the recipe here.
