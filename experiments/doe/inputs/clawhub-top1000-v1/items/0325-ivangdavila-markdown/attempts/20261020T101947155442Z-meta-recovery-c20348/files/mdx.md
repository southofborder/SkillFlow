# MDX — Markdown That Is Also JavaScript

MDX compiles Markdown to a JavaScript component. That single fact explains every difference: `<` opens JSX, `{` opens an expression, HTML comments are not valid syntax, and a build error is a compiler error with a line number rather than a page that renders wrong. It is the strictest target in this skill, and the only one where a mistake fails loudly.

**Contents:** [Which Version Are You On](#which-version-are-you-on) · [What Breaks Coming From Markdown](#what-breaks-coming-from-markdown) · [Expressions and Escaping](#expressions-and-escaping) · [Components](#components) · [Interleaving Markdown and JSX](#interleaving-markdown-and-jsx) · [`.md` vs `.mdx`](#md-vs-mdx) · [Reading Compiler Errors](#reading-compiler-errors) · [Migrating a Doc Set Into MDX](#migrating-a-doc-set-into-mdx)

## Which Version Are You On

- **MDX v1** — loose, HTML-comment tolerant, ad-hoc JSX detection. Long superseded; still found in old Gatsby sites.
- **MDX v2 (2022)** — the rewrite: strict JSX, expressions with `{}`, `{/* */}` comments, ESM `import`/`export` only.
- **MDX v3 (2023)** — v2 syntax plus newer JS support; the breaking change most people meet is arriving from v1, or from a Docusaurus v2 → v3 upgrade that swapped the compiler under thousands of pages.

Check `package.json` (`@mdx-js/*`, `@docusaurus/core` major) before touching syntax. Docusaurus v3 ships MDX v3.

## What Breaks Coming From Markdown

| Markdown that is fine | In MDX | Fix |
|---|---|---|
| `<!-- a comment -->` | Syntax error | `{/* a comment */}` |
| `<br>`, `<img src=x>` | Unclosed tag error | `<br />`, `<img src="x" />` |
| `class="x"`, `for="y"` | Ignored or warned | `className="x"`, `htmlFor="y"` |
| `style="color: red"` | Type error | `style={{color: 'red'}}` |
| A bare `<` in prose (`a < b`) | Tries to parse a tag | `\<`, or `{'<'}`, or a code span |
| `{` in prose (`use {name}`) | Evaluated as an expression | `\{`, or `{'{'}`, or a code span |
| Four-space indented code | Not code — parsed as text/JSX | Fenced code block |
| `<https://example.com>` autolink | Parsed as a JSX tag | `[https://example.com](https://example.com)` |
| An unknown tag `<Foo />` | "Foo is not defined" at build or render | Import it, or lowercase it into an HTML element |
| Emoji shortcodes, GitHub alerts | Literal text | The site's own components (`:::note` in Docusaurus) |

Two of these — the bare `<` and the bare `{` — are why a Markdown file full of code examples in prose fails to compile after a migration. Both are safe inside code spans and fences, which is where they usually belong anyway.

## Expressions and Escaping

- `{expression}` is evaluated JavaScript in MDX. `{2 + 2}` renders `4`; `{user.name}` renders whatever is in scope, or fails.
- To print a literal brace: `\{` or `{'{'}`. The second is uglier and survives more tooling.
- Inside a fenced code block, braces and angle brackets are **inert** — no escaping needed. This is the single most useful fact when migrating: move the offending text into a fence and the problem disappears.
- Inside an inline code span, MDX v2+ also leaves braces alone.
- Expressions can appear in attribute position (`<Foo bar={1} />`) and in text position, but not inside a code span, which is the boundary people expect to be able to cross.

## Components

```mdx
import Chart from '@site/src/components/Chart';

# Latency

<Chart data={latency} />
```

- Imports go at the top, ESM only; `require` does not work. Exports work too: `export const meta = {...}`.
- Components are resolved from scope; a typo becomes a runtime error in the browser, not a build error, on some setups.
- The site can inject components globally (Docusaurus `MDXComponents`), which is why a page can use `<Tabs>` with no import in one repo and not in another.
- Frontmatter is available as exports; in Docusaurus it also drives sidebar and routing (`frontmatter.md`).
- Components make a page unportable: the same file on GitHub shows raw JSX. Keep component use out of any page that also has to render on the forge.

## Interleaving Markdown and JSX

The rule: **Markdown is parsed inside a JSX block only when the content is separated by blank lines**, and indentation inside JSX is not Markdown indentation.

```mdx
<Callout type="warning">

This **is** parsed as Markdown, because of the blank lines.

</Callout>
```

Without the blank lines the content is JSX children — text renders, but `**bold**` shows as asterisks. Nested indentation inside a JSX block does not create code blocks; it is ignored, which is the opposite of Markdown and the cause of "my indented code vanished".

## `.md` vs `.mdx`

Docusaurus v3 and several other tools process `.md` with the CommonMark parser and `.mdx` with the MDX compiler — an important escape hatch. A page full of angle brackets, braces, and no components should be `.md`; only pages that need components need `.mdx`. Renaming is the cheapest fix for a page that will not compile, and it costs nothing but the components that page does not use.

Check the site config: some setups force MDX for both extensions (`format: 'mdx'`), in which case the escape hatch is not available and every page pays MDX's strictness.

## Reading Compiler Errors

| Error | Means |
|---|---|
| `Could not parse expression with acorn` | A `{` that is not valid JavaScript — usually a literal brace in prose |
| `Unexpected character before name` | A `<` followed by something that is not a tag name — a literal `<` in prose |
| `Expected a closing tag for <x>` | An HTML-style void tag; self-close it |
| `Unexpected end of file in expression` | An unbalanced `{` — often much earlier than the reported line |
| `X is not defined` | A component used without an import, or a typo in a global |
| `Unexpected token` in a code fence | The fence is not closed, so the compiler is reading code as MDX (`code.md`) |

The reported line is where the parser gave up, not always where the mistake is: unbalanced delimiters report late. Bisect the file rather than staring at the line.

## Migrating a Doc Set Into MDX

1. Inventory the constructs: grep for `<!--`, bare `<` in prose, `{`, indented code blocks, `class=`, unclosed void tags. That grep is the whole migration cost estimate.
2. Decide per page whether it needs to be `.mdx` at all — most do not.
3. Convert comments, self-close tags, fence anything with braces or angle brackets.
4. Build with the compiler in strict mode and fix top to bottom; errors cascade, so re-run after every few fixes rather than collecting a list.
5. Check the pages that also render on the forge: components and `:::` callouts do not.

**Write the outcome**: the MDX version and the site's `format` setting go in that doc set's row in `## Doc Sets` of `~/Clawic/data/markdown/memory.md`; each construct the compiler rejected goes in `## Quirks` naming the target; and a migration that produced a repeatable procedure or a component wrapper is an `artifacts/` file with its `## Boxes` line in the same turn (`memory-template.md`). The grep list from step 1 is worth keeping verbatim — it is the checklist for the next page anyone adds.
