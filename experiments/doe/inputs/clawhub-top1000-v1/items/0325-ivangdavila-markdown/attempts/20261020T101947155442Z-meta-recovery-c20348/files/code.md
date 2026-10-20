# Code Blocks, Code Spans, and Escaping

Code is the only place in Markdown where nothing is parsed, which makes it both the safest place to put difficult characters and the easiest construct to break: one miscounted backtick and the rest of the document is a code block.

**Contents:** [Fences](#fences) · [Fences Inside Fences](#fences-inside-fences) · [Indented Code](#indented-code) · [Language Tags](#language-tags) · [Code Spans](#code-spans) · [Escaping Outside Code](#escaping-outside-code) · [Code Inside Other Blocks](#code-inside-other-blocks) · [Highlighting Extras](#highlighting-extras) · [Code Samples That Have to Keep Working](#code-samples-that-have-to-keep-working)

## Fences

- Three or more backticks, or three or more tildes. Backticks are conventional; tildes are useful precisely because content rarely contains them.
- **The closing fence must be at least as long as the opening one** and use the same character. `````` ```` `````` opened, ` ``` ` closed → the block never ends, and everything to the end of the file is code.
- The opening fence may be indented up to 3 spaces, and **that same indentation is stripped from every content line**. A 4th space makes the fence itself part of an indented code block.
- No blank line is required before a fence in CommonMark, but write one anyway (`structure.md`).
- The info string (everything after the opening fence) must not contain a backtick when the fence is backticks — a common break when someone writes ``` ```js `x` ``` ```.
- An unclosed fence at end of file is auto-closed by CommonMark. Lint rule MD040/MD046 and a preview catch it; a diff will not.

## Fences Inside Fences

To show a fenced block inside a fenced block, the outer fence is longer:

````markdown
```python
print("hello")
```
````

That example is wrapped in four backticks. For three levels, five. The alternative is the tilde fence for the outer block, which keeps every inner backtick count intact:

```
~~~markdown
```js
console.log(1)
```
~~~
```

Documentation about Markdown, CI YAML containing shell heredocs, and prompt files are where this comes up. Count the longest backtick run in the content and add one.

## Indented Code

Four spaces from the current content column makes an indented code block. Two consequences:

- Inside a list item, "four spaces" means content column + 4, not 4 from the margin (`structure.md`).
- Indented code has **no language tag**, so no highlighting and no copy button in most themes. MDX does not support indented code at all.

Use fences. The only reason to keep indented code is a legacy parser that has nothing else.

## Language Tags

Always write one — highlighting, copy buttons, line numbering, and doc-site code tabs all key off it. When the content is not a language, say so: `text`, `plain`, `console`, `diff`.

| Content | Tag | Why not the obvious one |
|---|---|---|
| Shell commands only | `bash` / `sh` | — |
| Commands **and** their output | `console` or `text` | `bash` highlights the output as code and misleads |
| A terminal session with prompts | `console` | Keeps `$` visible without breaking copy-paste conventions |
| A patch | `diff` | Renders `+`/`-` in colour |
| JSON with comments | `jsonc` | Plain `json` marks every comment as an error in strict themes |
| Environment file | `dotenv` or `ini` | — |
| A Dockerfile, Makefile, nginx conf | `dockerfile`, `makefile`, `nginx` | — |
| Unknown or mixed | `text` | An unrecognized tag falls back to plain in most highlighters; a few log a build warning |

Highlighter support differs: GitHub uses Linguist's alias list, docs sites usually use Prism or Shiki, each with its own aliases. A tag that works on GitHub can emit a build warning on the site (`docs-sites.md`).

## Code Spans

- Backticks around the text. To include a backtick, use a longer run and pad with one space at each end: `` `` `code` `` `` renders `` `code` ``.
- The padding spaces are stripped by CommonMark only when there is one at **each** end; asymmetric padding renders literally.
- Nothing inside a code span is parsed — no emphasis, no links, no HTML. **Except in a GFM table cell**, where a pipe must still be escaped because cells are split before inline parsing (`tables.md`).
- A newline inside a code span becomes a space. Multi-line content needs a fence.
- Code spans are the correct home for: file names with underscores, glob patterns, regexes, anything containing `<`, and any string a reader will copy.

## Escaping Outside Code

Backslash-escapable in CommonMark: ``\ ` * _ { } [ ] ( ) # + - . ! | < > " $ %`` and the other ASCII punctuation. A backslash before a non-punctuation character is a literal backslash.

The ones that actually bite:

| Character | When it needs escaping |
|---|---|
| `*` `_` | In prose beside a word: `2*3`, `__init__` in a non-code context |
| `[` `]` | Text that looks like a link label, e.g. `[WIP] title` |
| `<` | Anything resembling a tag: `<name>`, `<3`, generics like `List<T>` |
| `&` | Only when it would form an entity: `&amp;`, `&copy;`, `&#65;` |
| `#` | At line start only (would become a heading) |
| `\|` | Inside table cells, always (`tables.md`) |
| `!` | Only before `[` (would become an image) |
| `~` | Where strikethrough is enabled and you mean a literal tilde |

The general rule: if the token is code, put it in a code span and escape nothing. Escaping is for prose that happens to contain punctuation.

## Code Inside Other Blocks

- **In a list item**: indent the fence to the item's content column (`structure.md`).
- **In a blockquote**: prefix every line, fences included, with `> `.
- **In a table cell**: impossible — code spans only.
- **In HTML**: inside a `<details>` block, leave a blank line after `<summary>` or the Markdown inside is not parsed (`extensions.md`).
- **In MDX**: fences work; indented code does not; `{` inside a fence is safe, `{` outside is an expression (`mdx.md`).

## Highlighting Extras

Non-standard, per-target, and worth knowing because they appear in files you inherit:

- **Line highlighting**: ` ```js {2,4-6} ` in Docusaurus, `hl_lines="2 4-6"` in MkDocs Material, `#!` comment-based in some themes.
- **Titles**: ` ```js title="src/index.js" ` (Docusaurus), `title=` in Material.
- **Diff overlays**: `// highlight-next-line` comments in Docusaurus, `+`/`-` with the `diff` language elsewhere.
- **Copy button**: automatic in most doc themes, absent on GitHub, and absent for indented code everywhere.
- **Shiki vs Prism**: Shiki (VitePress, newer Docusaurus) uses TextMate grammars and fails closed on unknown languages during the build; Prism falls back silently. A tag typo is a broken build in one and a plain block in the other.

None of these render on GitHub — they appear as part of the info string or as literal comments. Keep them out of files that also render on the forge.

## Code Samples That Have to Keep Working

- **No smart quotes, no em-dash autocorrect** inside samples. A word processor or a chat client turns `"` into `"` and `--` into `—`, and the copied command fails with a syntax error the reader cannot see.
- **Secrets never appear literally**, even as examples: write `<env:API_TOKEN>` or an obviously fake, structurally valid placeholder. A realistic-looking key gets copied into a real config, and a real one gets committed (SKILL.md Data).
- **Prompts**: showing `$ ` before a command breaks copy-paste in every renderer without a copy button that strips it. Either omit the prompt, or use `console` and accept it.
- **Long lines**: code blocks scroll horizontally rather than wrapping, and PDF export truncates them (`conversion.md`). Break commands with `\` continuations at ~80 columns when the destination might be paper.
- **Version drift**: a sample pinned to a version rots. State the version the sample was verified against in a line above it, so the reader can judge the age.

**Write what the target turned out to accept**: a language tag its highlighter rejected or aliases differently, a fence style it requires, a code-block attribute syntax that works — one line in `## Quirks` of `~/Clawic/data/markdown/memory.md` naming the target, plus the construct in that target's `Confirmed refuses` column in `## Render Targets`. A fence convention observed across their files (tilde vs backtick, always-tagged) belongs in `## House Style`, and a sample block shaped for reuse — a standard install snippet, a standard config example — is a template in `artifacts/` with its `## Boxes` line in the same turn (`memory-template.md`).
