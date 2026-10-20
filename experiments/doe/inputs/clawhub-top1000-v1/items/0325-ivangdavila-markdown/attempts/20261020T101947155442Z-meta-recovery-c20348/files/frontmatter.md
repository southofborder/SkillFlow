# Frontmatter — Metadata That Either Parses or Renders

Frontmatter is not Markdown. It is a foreign block that a host application agrees to strip before the Markdown parser sees the file. Two failure modes follow: the host does not strip it (it renders), or the host strips it and rejects the contents (the build fails).

**Contents:** [Placement Rules](#placement-rules) · [Formats](#formats) · [YAML Traps That Cost Hours](#yaml-traps-that-cost-hours) · [Who Consumes It](#who-consumes-it) · [Field Sets Worth Standardizing](#field-sets-worth-standardizing) · [Multiline Values](#multiline-values) · [Debugging](#debugging)

## Placement Rules

1. The opening delimiter must be on **line 1, column 1**. Not after a blank line, not after a comment, not after a BOM — a UTF-8 BOM before `---` is the classic invisible cause of "the site says this page has no title".
2. The closing delimiter is a line with exactly the delimiter, nothing else. A trailing space is tolerated by most parsers and not all.
3. Content starts on the line after the closing delimiter. A blank line there is conventional and harmless.
4. Exactly one block, at the top. A second `---` block further down is a thematic break, or a setext heading if a paragraph precedes it (`structure.md`).

Where a target does **not** consume frontmatter, `---\ntitle: x\n---` renders as a horizontal rule, then `title: x` as a paragraph or an H2 — the visual signature of frontmatter arriving somewhere it was not expected. GitHub is the special case: it renders YAML frontmatter in `.md` files as a small table, which looks intentional and is usually not.

## Formats

| Format | Delimiters | Used by | Notes |
|---|---|---|---|
| YAML | `---` … `---` | Jekyll, Hugo, Docusaurus, MkDocs (with `meta`), Obsidian, Astro, most CMSs | The default; `frontmatter_format: yaml` |
| TOML | `+++` … `+++` | Hugo (native), Zola | No type coercion surprises; verbose for nested data |
| JSON | `{` … `}` at the top, or `---json` | Hugo, some Gatsby setups | Machine-friendly, unpleasant to hand-edit |
| MultiMarkdown | `Key: value` lines, blank line, no delimiters | MultiMarkdown, some Pandoc setups | No delimiters means no reliable detection — avoid |
| None | — | Plain READMEs, chat, issues | Metadata goes in an HTML comment or a bold first line |

Pandoc reads YAML metadata blocks anywhere in the file, not only at the top, and merges multiple blocks — useful for `conversion.md`, confusing when the same file also feeds a site that requires exactly one at the top.

## YAML Traps That Cost Hours

- **Unquoted colons**: `title: Setup: the fast path` is a YAML syntax error or a nested map. Quote any value containing `: ` — and any value at all in generated frontmatter, which costs nothing.
- **YAML 1.1 booleans**: `yes`, `no`, `on`, `off`, `y`, `n` parse as booleans in Ruby's Psych (Jekyll) and in several other loaders. A page with `draft: no` is not draft; a page with `country: NO` is `country: false`. Quote them.
- **Version strings**: `version: 1.10` is the float 1.1. `version: "1.10"` is what you meant.
- **Leading zeros**: `id: 007` is 7 in YAML 1.1 (and octal in some loaders). Quote identifiers, always.
- **Dates**: unquoted `2026-07-26` becomes a date object with the loader's timezone assumptions; a mismatch shifts published dates by a day. Quote it, or set the timezone explicitly in the site config.
- **Tabs are illegal** in YAML indentation. An editor configured for tabs produces a parse error that points at the wrong line.
- **`#` starts a comment** unless quoted: `tags: #announcements` is a null value with a comment.
- **Empty value is null, not empty string**: `description:` gives `None`/`nil`, which templates often print as the literal word.
- **Duplicate keys**: last one wins in most loaders, silently. A merge conflict resolved badly produces exactly this.
- **Long strings wrap wrong**: a plain scalar folded across lines joins with spaces and drops the indentation. Use a block scalar (below).

## Who Consumes It

| Consumer | Requires | Ignores unknown keys |
|---|---|---|
| Jekyll | Any frontmatter at all — a file without it is not processed | Yes, exposed as `page.*` |
| Hugo | `title`, `date` in practice; `draft: true` hides the page | Yes, exposed as `.Params` |
| Docusaurus | Optional; `id`, `title`, `sidebar_position`, `slug`, `tags` are meaningful | Yes, warns on some |
| MkDocs | Only with the `meta` extension; `title` overrides the H1 in the nav | Yes |
| Obsidian | `tags`, `aliases`, `cssclasses` have behavior; the rest is properties | Yes |
| Pandoc | `title`, `author`, `date`, `bibliography`, plus template variables | Yes, available to templates |
| GitHub | Nothing — it renders the block as a table | — |
| npm / PyPI | Nothing; the block renders as text or a rule | — |

The last two rows are the reason a README should almost never have frontmatter.

## Field Sets Worth Standardizing

A doc set benefits from a fixed, small schema, enforced by lint or a build script rather than by convention:

- `title` — required, quoted, sentence case unless the house style says otherwise. It is the `<title>`, the sidebar label, and the search result.
- `description` — required for anything public: it is the meta description and the search snippet. One sentence, under ~155 characters, or the search engine truncates it.
- `date` / `updated` — quoted ISO 8601. `updated` is what makes a stale-page review possible.
- `tags` — a closed list, validated in CI. Free-form tags become a hundred tags with one page each.
- `draft` / `published` — one flag, one meaning, quoted booleans.
- `sidebar_position` or `weight` — ordering, when the generator uses it. Leave gaps (10, 20, 30) so an insertion does not renumber the folder.

When a schema is agreed, it is an artifact: the field list, which fields are required, the allowed values, and what breaks when each is missing.

## Multiline Values

```yaml
description: >-
  Folded: newlines become spaces, and the trailing newline is stripped.
  Right for prose that must not contain line breaks.

body: |
  Literal: newlines preserved exactly.
  Right for snippets, addresses, and anything with meaningful lines.
```

`>` folds, `|` keeps. The `-` chomps the trailing newline, `+` keeps it all. Prose fields want `>-`; anything a machine will re-emit wants `|`. Never embed unescaped Markdown syntax in a plain scalar — a leading `-`, `#`, `*`, `[`, or `{` at the start of an unquoted value changes its YAML type.

## Debugging

1. Is it byte 1 of the file? Check for a BOM (`file` reports "with BOM"; a hex dump shows `EF BB BF`).
2. Do both delimiters match the format the consumer expects (`---` vs `+++`)?
3. Does the YAML parse at all? Run it through any YAML loader on its own before blaming the site.
4. Are the failing values quoted? Re-read the traps list — booleans, versions, colons account for most of them.
5. Does the consumer actually read frontmatter (table above)? If not, the fix is deleting the block, not fixing it.

**When a target's frontmatter schema is established** — the required fields, the allowed tag values, the field the theme actually reads — write it to `~/Clawic/data/markdown/artifacts/frontmatter-<docset>.md` with its `## Boxes` line in the same turn, and note the generator in that doc set's row in `## Doc Sets` of `memory.md` (`memory-template.md`). Schemas are derived by trial against a build; re-deriving one costs the same hour every time. If the block held a token — some CMS integrations put one there — strip it to its pointer before the file is written anywhere under `~/Clawic/data/`.
