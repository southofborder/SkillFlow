# Accessibility — What Markdown Decides for Screen Readers

Markdown produces HTML, and the HTML it produces is what assistive technology navigates. Most accessibility failures in documentation are made in the Markdown source and are invisible in the rendered page: a skipped heading level, an image with no alt text, a link that says "here".

**Contents:** [Headings Are the Navigation](#headings-are-the-navigation) · [Alt Text](#alt-text) · [Link Text](#link-text) · [Tables](#tables) · [Lists and Structure](#lists-and-structure) · [Code Blocks](#code-blocks) · [Emoji and Symbols](#emoji-and-symbols) · [Colour, Callouts, and Meaning](#colour-callouts-and-meaning) · [Language and Reading Order](#language-and-reading-order) · [What to Check](#what-to-check)

## Headings Are the Navigation

Screen reader users navigate long documents by jumping between headings; a heading list is the table of contents whether or not the page has one.

- **One H1**, matching the page title.
- **No skipped levels.** `##` → `####` tells a screen reader a level is missing and breaks the outline; it also breaks generated sidebars and PDF bookmarks (`structure.md`).
- Headings are for structure, not emphasis. A bold line used as a section break is invisible to heading navigation; a heading used to make text big is a phantom section.
- Do not put images, emoji, or code spans in a heading you will link to — they mangle the slug and are read aloud in the outline (`links.md`).
- Empty headings (a `##` with a bold line under it doing the real work) appear in the outline as nothing.

## Alt Text

`![alt](path)` — the alt text is what is announced, and what renders when the image fails to load.

| Image | Alt text |
|---|---|
| A screenshot demonstrating a step | What the reader should conclude: `![The settings page with Enable API checked]` |
| A diagram | The relationship, not the shapes: `![Requests flow from the client through the API to the queue]` — and put the full description in the surrounding prose if it carries real information |
| A badge | What it reports: `![build status]`, `![npm version]` |
| A logo | The organization name: `![Acme]` |
| Pure decoration | Empty, deliberately: `![](divider.png)` — announced as nothing rather than as a filename |
| A chart with data that matters | The takeaway, plus the data in a table below it — no alt text can carry a chart |

Anti-patterns: the file name (`![screenshot-2026-07-26.png]`), the word "image", a caption duplicated from the line above (announced twice), and a paragraph of description where a sentence would do. Lint rule MD045 catches missing alt text and nothing catches bad alt text — that one is a review item.

## Link Text

- Screen readers can list every link on a page, out of context. "Click here", "read more", "this" and a bare URL are useless in that list; a long raw URL is read character by character in some configurations.
- Write the destination into the text: `[the installation guide](…)`, not `see [here](…)`.
- Two links with the same text pointing to different places are a genuine confusion; two with different text pointing to the same place are fine.
- A link that opens something unusual (a PDF, a download, an external site in a new tab) says so in the text.

## Tables

- A GFM table gives you exactly one thing: a header row (`<th>` with `scope="col"`). That is enough for simple data.
- **Row headers, captions, merged cells and multi-level headers do not exist** in pipe tables. Data that needs them needs an HTML table with `<caption>` and `<th scope="row">` — and then `raw_html` and the target's sanitizer decide whether it survives (`tables.md`).
- A table used for layout is announced as a table, cell by cell. Do not use one for side-by-side prose.
- Never leave the header row empty to get a headerless look: the reader gets a table of unlabelled columns.
- ASCII tables inside code fences are read as code — a wall of pipes and dashes. Where the audience may include screen reader users, that is a last resort, and the data belongs in prose or a real table.

## Lists and Structure

- Use real list syntax. A paragraph of lines starting with `-` that failed to parse (missing blank line, `structure.md`) is announced as one long sentence, and the reader loses the item count that a real list gives them up front.
- Loose vs tight changes the announcement slightly but not the structure; nesting depth beyond three levels is hard to follow aurally.
- Task lists are announced as checkboxes with their state — good in issues, meaningless in a document where nothing is checkable.
- Blockquotes are announced as quotes; do not use one as a visual box for something that is not a quotation. Where the target has callouts, use those (`extensions.md`).

## Code Blocks

- Always tag the language (`code.md`): some readers announce it, and syntax highlighting is a visual cue that needs a non-visual equivalent.
- Long code blocks are read line by line; a short prose summary before a long sample ("this configures two workers and a health check") is worth more than any markup.
- Never put prose the reader must not miss inside a code block for styling reasons — it is announced as code, character by character in verbose modes.

## Emoji and Symbols

- Emoji are announced by their full CLDR name: `✅` is "check mark button", `🚀` is "rocket". A heading decorated with three emoji is three extra spoken phrases every time the outline is read.
- Never let an emoji carry meaning on its own — `✅` versus `❌` in a table column needs the words "yes" and "no" too, or the column is inaccessible and untranslatable.
- Mid-word or repeated emoji (`🎉🎉🎉`) are read out repeatedly. One, at the end, or none.
- Arrows and mathematical symbols in prose (`→`, `≥`) are usually announced correctly; ASCII art is not.

## Colour, Callouts, and Meaning

- Markdown has no colour, which is an accessibility advantage: the only colour is what the theme applies to callouts, code, and links.
- A callout's type (warning versus note) is communicated by colour **and** by its label in every implementation worth using — check the target actually renders the label, not just a coloured bar (`extensions.md`).
- Do not rely on the reader seeing a diff's red and green; say what changed.

## Language and Reading Order

- Set the document language where the target supports it (frontmatter `lang`, Pandoc `-V lang`, the site config). A screen reader with the wrong language pronounces everything wrong.
- Inline foreign phrases need `<span lang="fr">` to be pronounced correctly — HTML, so `raw_html` decides.
- RTL content mixed with LTR needs explicit direction marks; Markdown offers nothing, so those documents need HTML or a target that handles it.
- Reading order is source order. Anything positioned by CSS or by a component is read in source order regardless of where it appears (`mdx.md`).

## What to Check

A short pass that catches most of it, in order of value:

1. Every image has alt text, and none of it is a file name (MD045 automates the first half).
2. No heading level is skipped, and there is exactly one H1 (MD001, MD025).
3. No link text is "here", "this", "read more", or a bare URL.
4. Every table has a real header row, and no table is doing layout.
5. Emoji and colour never carry meaning alone.
6. The document language is set.

**Write the result of a pass**: a row in `~/Clawic/data/markdown/checks/<year>.md` with the scope, what was found, what was fixed and what was left — accessibility findings are the ones most likely to be partially fixed, and the `Left` column is what makes the remainder visible next quarter. An agreed accessibility bar (alt text required, whether HTML tables are permitted for complex data) is a declared preference: it goes in `config.yaml` under `accessibility`, and the recurring pass becomes a `## Due` row (`memory-template.md`).
