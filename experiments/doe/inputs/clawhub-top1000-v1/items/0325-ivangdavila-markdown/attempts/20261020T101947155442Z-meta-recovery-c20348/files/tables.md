# Tables — The Construct Most Likely to Break

Pipe tables are not in CommonMark. They arrived with GFM and were then re-implemented by every other parser with slightly different rules, so a table is the construct most likely to render in one place and not another. Check the Support Matrix in `SKILL.md` before writing one for an unfamiliar target.

**Contents:** [The Minimum Valid Table](#the-minimum-valid-table) · [Cell Counting](#cell-counting) · [Escaping Inside Cells](#escaping-inside-cells) · [What Cannot Go In a Cell](#what-cannot-go-in-a-cell) · [Alignment and Width](#alignment-and-width) · [Padding vs Compact](#padding-vs-compact) · [When to Abandon the Table](#when-to-abandon-the-table) · [Converting Into a Table](#converting-into-a-table) · [Per-Target Notes](#per-target-notes)

## The Minimum Valid Table

```markdown
| Header | Header |
|---|---|
| cell | cell |
```

Requirements, all mandatory in GFM:

1. A **header row**. There is no headerless pipe table; an empty header row (`| | |`) is the only workaround and it renders an empty band.
2. A **delimiter row** immediately below, no blank line between them.
3. A **blank line above** the table. Without it, most parsers treat the whole thing as a paragraph of literal pipes — the number one cause of "my table shows as text".
4. Leading and trailing pipes are optional in GFM but required by several other parsers. Always write them.

The delimiter row needs at least one `-` per cell; `|-|-|` is valid. Longer runs are cosmetic.

## Cell Counting

The **delimiter row decides the column count**. In GFM:

- A body row with more cells than the header: the extras are **silently dropped**.
- A body row with fewer: the missing cells render empty.
- A header row whose cell count differs from the delimiter row: **the whole table is not a table** and renders as a paragraph.

So "my last column disappeared" is a cell-count bug, and "my table renders as text" is a header/delimiter mismatch. Count pipes before debugging anything else. An unescaped pipe inside a cell inflates that row's count and produces both symptoms at once.

## Escaping Inside Cells

GFM splits rows into cells **before** inline parsing. Consequences:

- A literal pipe needs `\|` — **including inside a code span**. `` `a|b` `` breaks the cell; `` `a\|b` `` renders `a|b` in code.
- The backslash escape is the only mechanism: `&#124;` works in some renderers, and is invisible junk in the source of the rest.
- Backslashes at end of cell content need doubling (`\\`) or they escape the pipe that follows.
- Inline code, links, emphasis, and images all work inside cells; block constructs do not (below).

## What Cannot Go In a Cell

| Wanted | Reality | Do instead |
|---|---|---|
| Multiple lines / paragraphs | A row is one source line, full stop | `<br>` if `raw_html` allows, otherwise split into two rows or move the content out |
| A fenced code block | Cannot exist inside a cell | Inline code span, or a fence below the table with a row pointing at it |
| A bullet list | Not a block context | `<br>` separated items, or a sub-section |
| A merged cell (`colspan`) | No pipe-table syntax anywhere | HTML table, if every target renders HTML — otherwise restructure |
| A caption | Not in GFM; Pandoc and kramdown have one | A bold line above the table, or Pandoc's `: caption` |
| A blank line inside the table | Ends the table | Keep every row contiguous |

`<br>` inside a cell is the standard escape hatch and it is HTML: it is stripped by Hugo's default config, by PyPI's sanitizer in some contexts, and re-parsed as JSX in MDX (where it must be `<br />`). Check `raw_html` before reaching for it.

## Alignment and Width

Colons live in the delimiter row: `:---` left, `:---:` center, `---:` right, `---` default (left in every common renderer).

- Alignment is per column, applied to the whole column including the header.
- There is **no width control** in Markdown. Column widths are chosen by the renderer from the content. To force one, either pad a cell with `&nbsp;` (ugly, portable) or use an HTML table (fragile, target-dependent).
- Very wide tables scroll horizontally on GitHub and get cut off in PDF exports (`conversion.md`). Above roughly six columns of prose, consider a definition-style list of sub-sections instead: the reader is scrolling either way, and headings are linkable.

## Padding vs Compact

Both render identically. The difference is diffs, and it is a real cost:

```markdown
| Name | Description | Default |    ← padded: every cell space-filled to the column width
|------|-------------|---------|
| url  | Endpoint    | none    |

| Name | Description | Default |    ← compact: one space each side, pipes wherever they fall
|---|---|---|
| url | Endpoint | none |
```

Padded tables read better in the raw file and are what Prettier produces. Their cost: widening one cell rewrites **every row** in the table, so a one-word change shows up as a 30-line diff and reviewers stop reading. `table_style: compact` for files edited by many people or reviewed line by line; `padded` for files one person owns. Do not mix within a repo — the formatter will flip them back and forth in alternating commits.

## When to Abandon the Table

Reach for an alternative when any of these is true: merged cells are required; a cell needs more than one paragraph; the target is Slack, Teams, or plain-text email (no tables at all, `chat-platforms.md`); or the table is a layout device rather than data.

Alternatives in order of portability: a definition-style list (`**term** — description`), a series of `###` sub-sections, a fenced block containing a fixed-width ASCII table (renders everywhere, unusable for screen readers, `accessibility.md`), and last an HTML table.

## Converting Into a Table

- **From a spreadsheet**: paste is tab-separated. Replace tabs with ` | `, escape any `|` in the data, add the header and delimiter rows, and check for cells containing newlines — those are the rows that will break.
- **From CSV**: same, plus unquote the fields; commas inside quotes are the ones that ruin a naive split.
- **From HTML**: `pandoc -f html -t gfm` handles `colspan` by flattening it, which is the moment to notice the table needed merged cells (`conversion.md`).
- **From JSON**: derive the header from the union of the keys, not from the first object — the object that is missing a key is why a column is silently empty.

Whatever the source, the last step is the same: render it once in the real target before shipping it.

## Per-Target Notes

- **GitHub**: tables render in files, issues, PRs, and comments; wide ones scroll. Alerts and Mermaid do not work inside cells.
- **MkDocs Material**: needs the `tables` extension (default in Material); `md_in_html` is required to nest Markdown inside HTML tables.
- **MDX**: pipe tables need `remark-gfm`; a JSX component in a cell works, a multi-line component does not.
- **Pandoc**: pipe tables plus three richer table syntaxes (grid, multiline, simple). Grid tables are the only Markdown-family syntax with real multi-line cells — worth it when the destination is PDF or DOCX and the source is only ever read by pandoc.
- **Slack/Discord/Teams**: no tables. A fenced block with aligned columns is the only thing that survives.
- **Confluence/Jira**: the editor converts a pasted pipe table into a native table, and then it is no longer Markdown — round-tripping it back out loses the formatting.

**When a table trap is target-specific** — a sanitizer that eats `<br>`, a parser that requires outer pipes, an editor that converts on paste — add the line to `## Quirks` in `~/Clawic/data/markdown/memory.md` naming the target, and the construct to that target's `Confirmed refuses` column (`memory-template.md`). If the fix was a whole table shape worth reusing (a parameter table, a compatibility matrix), it is a template in `artifacts/` with its `## Boxes` line in the same turn.
