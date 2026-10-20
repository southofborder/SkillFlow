# Structure — Blocks, Lists, Headings, and White Space

Ninety per cent of "Markdown is broken" is block parsing: the parser decided where a block starts and ends differently than you did. Block structure is decided **before** any inline parsing, which is why an indentation error can turn a table into a code block and an emphasis error can never turn a paragraph into a list.

**Contents:** [The Blank-Line Law](#the-blank-line-law) · [Lists: The Content Column](#lists-the-content-column) · [Loose vs Tight Lists](#loose-vs-tight-lists) · [Ordered Lists](#ordered-lists) · [Nesting Anything Inside a List Item](#nesting-anything-inside-a-list-item) · [Headings](#headings) · [Line Breaks and Paragraphs](#line-breaks-and-paragraphs) · [Blockquotes](#blockquotes) · [Thematic Breaks](#thematic-breaks) · [Emphasis and the Runaway Italic](#emphasis-and-the-runaway-italic) · [Invisible Characters](#invisible-characters)

## The Blank-Line Law

One blank line above and below every block-level construct: list, table, fence, blockquote, heading, HTML block. It is never wrong and it removes an entire class of bug.

Where it is strictly required, by parser:

| Construct | CommonMark / GFM | Python-Markdown, kramdown, legacy |
|---|---|---|
| List after a paragraph | Optional for `-` and `1.` | **Required** — without it the items join the paragraph |
| Table after a paragraph | **Required** | **Required** |
| Fence after a paragraph | Optional | Recommended |
| Heading after a paragraph | Optional (ATX) | **Required** in some |
| HTML block, then Markdown inside it | Blank line before the Markdown | Needs `markdown="1"` on the tag |

Two or more consecutive blank lines are never meaningful — inside a list they end the list only if the following block is not indented to the content column. Lint rule MD012 collapses them; nothing renders differently.

A line containing only spaces is a blank line for block purposes but survives in the file, so it breaks paragraphs invisibly and trips MD009/MD012. Trim trailing whitespace on save.

## Lists: The Content Column

The single number that governs list nesting.

```
- parent item          ← marker "- " is 2 chars wide → content column = 2
  nested content       ← indent 2  (≥ 2, < 6)  → belongs to the item
    - nested list      ← indent 4  (≥ 2, < 6)  → still the item: a sublist
      code?            ← indent 6  (≥ 2+4)     → indented CODE BLOCK inside the item
```

Formula: **content column = width of the marker plus the spaces after it.** `- ` → 2. `1. ` → 3. `10. ` → 4. `-   ` (three spaces) → 4.

A block indented from the item's own start by **≥ content column and < content column + 4** continues that item. At content column + 4 it becomes an indented code block. That is the whole rule, and it explains every "my sub-bullet turned into a grey box".

Consequences worth memorizing:

- 4 spaces is legal for both `- ` (window 2–5) and `1. ` (window 3–6), and is what Python-Markdown requires — the portable default, `list_indent`.
- 2 spaces under `1. ` is **below** the content column: the sublist becomes a sibling paragraph or a new list, depending on the parser.
- A list marker followed by 5+ spaces is parsed as "marker + indented code", not as a wide indent. Keep it to one space after the marker.
- Mixed markers (`-` then `*`) start a **new list** at the same level in CommonMark. Two lists that look like one, with the numbering restarting. Keep one marker per file (`list_marker`, lint rule MD004).

## Loose vs Tight Lists

A list is **loose** if any two of its items are separated by a blank line, or any item contains two blocks. Loose lists wrap every item in `<p>`, which is why spacing suddenly grows or shrinks after an edit — nothing about your CSS changed, the list changed category.

- Want tight: no blank lines anywhere inside the list.
- Want loose (items that hold paragraphs, code, or sublists that need air): a blank line between every item, not just some — mixed spacing is a diff that renders differently in different parsers.

## Ordered Lists

- The **first** number sets the start; every later number is ignored and the renderer counts. `1. 1. 1.` renders 1, 2, 3. So does `1. 7. 3.` — which is why a wrong number is invisible until someone reads the source.
- Only a list starting at `1.` may interrupt a paragraph in CommonMark, so a line "step 3." at the end of a sentence does not accidentally become a list, but "1." does.
- `)` is a valid delimiter (`1)`) and starts a different list than `1.` — switching delimiters mid-list splits it in two.
- Start at something other than 1 by writing that number (`5.`); HTML gets `start="5"`. Not supported by every legacy parser.
- Lazy numbering (all `1.`) versus real numbers is a genuine trade-off — see `SKILL.md` Where Experts Disagree.

## Nesting Anything Inside a List Item

The content column governs code, tables, blockquotes, and images alike:

````markdown
1. Install the dependency:

   ```bash
   npm install
   ```

2. Edit the config:

   | Key | Value |
   |-----|-------|
   | url | https://example.com |
````

Three spaces because `1. ` has content column 3. With 2 spaces the fence leaves the list; with 7 it becomes literal code text inside a code block. Fences inside list items are the most common place this goes wrong, because the fence hides the mistake — the content still renders, just outside the item.

## Headings

- ATX (`## Title`) needs the space after the hashes in CommonMark and GFM; `##Title` is a paragraph. Up to 6 levels; a 7th `#` is text.
- Up to 3 leading spaces are allowed before the `#`; a 4th makes it code.
- Closing hashes (`## Title ##`) are optional and stripped — harmless, and noise in a diff.
- Setext (`Title` over `===` or `---`) still works and creates a level-1/2 heading. The trap: a line of `---` directly under any paragraph turns that paragraph into an H2 instead of drawing a rule. Put a blank line before a thematic break, always.
- **One H1 per document** and no skipped levels: the sidebar, the on-page TOC, PDF bookmarks, and screen-reader navigation are all built from the heading tree (`accessibility.md`).
- Heading text is a URL (SKILL.md Rule 8). Rewording one is a breaking change — grep first, or pin the id where the target supports it (`links.md`).
- Duplicate heading text within one file produces `-1`, `-2` suffixes on the later anchors and trips lint rule MD024; `siblings_only` is the usual exception for pages that repeat `## Errors` under each endpoint.

## Line Breaks and Paragraphs

| Want | Write | Notes |
|---|---|---|
| New paragraph | Blank line | Always works, everywhere |
| Hard break inside a paragraph | `\` at end of line | The default: CommonMark, visible in the source, survives formatters (SKILL.md Rule 6) |
| Hard break, pre-CommonMark parser with no `\` | Two trailing spaces | The original Markdown.pl break and the only one those parsers have; invisible, stripped on save, flagged by MD009 |
| Hard break where even the spaces get stripped | `<br>` | Last resort; only if `raw_html` allows it |
| Soft wrap in the source, one line rendered | Just wrap | Markdown joins the lines with a space |

CJK text is the exception to the last row: joining two wrapped CJK lines inserts a space that should not be there. Some parsers strip it, most do not — for CJK content set `line_wrap: none`.

## Blockquotes

- `>` on every line is the safe form. "Lazy continuation" — omitting `>` on wrapped lines — is legal in CommonMark and breaks in enough dialects to be a bad habit.
- Nesting is `>>`, and each level needs its own marker on every line.
- A blank line **without** `>` ends the quote; a blank line **with** `>` keeps it open across paragraphs.
- Fences, lists, and tables nest inside quotes normally, indented after the `> `. GitHub alerts (`> [!NOTE]`) are blockquotes with a magic first line (`extensions.md`).

## Thematic Breaks

`---`, `***`, `___`, three or more, optionally spaced. Prefer `---` for consistency, and always with a blank line above it: without one it becomes a setext H2, and at the top of a file it becomes frontmatter (`frontmatter.md`). These three collisions are the reason a horizontal rule is worth thinking about at all.

## Emphasis and the Runaway Italic

- `*text*` italic, `**text**` bold, `***text***` both, `_` equivalent to `*` **except** inside a word: CommonMark allows intraword `*` and forbids intraword `_`. So `file_name_here` is safe, `2*3*4` italicizes the 3.
- One unbalanced `*` in prose can italicize everything to the next `*` in the document — often thousands of lines later. When a document goes italic from a point onward, search backward from that point for a lone asterisk or underscore.
- Escape with a backslash (`\*`) or, better, put the token in a code span: nothing inside backticks is parsed.
- Markers must hug the text: `** bold **` is literal asterisks with spaces, not bold.
- Nesting the same character (`**bold with *italic* inside**`) is fine; alternate the characters when the parser gets confused.

## Invisible Characters

Non-breaking spaces (from a word processor or a chat), zero-width joiners (from emoji handling), and BOMs (from Windows editors) all look like nothing and behave like content: a BOM before `---` stops frontmatter from parsing, and an NBSP after a list marker changes the content column. When a construct is unquestionably correct and still does not render, check the bytes before checking the rule (`security.md` covers the malicious version).

**When a structural rule turns out to differ in the target you are working against** — a parser that requires the blank line, a nesting depth it silently flattens, a heading level the theme steals — that is a quirk with a name: write one line in `## Quirks` of `~/Clawic/data/markdown/memory.md` naming the target, and update that target's `Confirmed refuses` column in `## Render Targets` (`memory-template.md`). Structural quirks are the ones that recur weekly; each one you record is a class of bug that stops coming back.
