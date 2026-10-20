# Editing Existing Files — Diffs, Renames, Migrations

Writing Markdown from scratch is the easy half. Most work is changing files somebody else owns, in a repo with conventions nobody wrote down, where a 3-line fix that arrives as a 300-line diff will not be reviewed.

**Before editing an inherited file**, read `## House Style` in `~/Clawic/data/markdown/memory.md` — what their files already do — and the doc set's row in `## Doc Sets` for the generator and the lint state. Declared preferences in `config.yaml` outrank observed style; observed style outranks your defaults.

**Contents:** [Match the File, Not Your Defaults](#match-the-file-not-your-defaults) · [The Diff Is the Deliverable](#the-diff-is-the-deliverable) · [Wrapping Strategies](#wrapping-strategies) · [Renaming and Moving](#renaming-and-moving) · [Splitting a Page](#splitting-a-page) · [Migrating Between Flavors](#migrating-between-flavors) · [Bulk Edits](#bulk-edits) · [Reviewing Someone Else's Markdown](#reviewing-someone-elses-markdown) · [Generated and Vendored Files](#generated-and-vendored-files)

## Match the File, Not Your Defaults

Read ten lines before writing one. What to detect, in order of how badly a mismatch shows up in the diff:

| Detect | How |
|---|---|
| Wrapping | Are paragraphs one long line, wrapped at a column, or one sentence per line? |
| List marker and indent | First bullet character; count the spaces on a nested item |
| Heading case | Sentence case or Title Case; whether headings end with a colon |
| Table style | Padded to align, or compact |
| Emphasis markers | `*` or `_` for italic; `**` or `__` for bold |
| Link style | Inline, or reference definitions at the bottom |
| Code fences | Backticks or tildes; whether language tags are always present |
| Frontmatter | Present, and which keys are always there |

A file that mixes two conventions is telling you the last two authors each imposed their own. Match the dominant one and note it; do not "fix" it as part of an unrelated change.

## The Diff Is the Deliverable

- **Change only what the task names.** Reflowing a paragraph you did not edit, re-padding a table, or swapping bullet characters buries the actual change.
- **Run a formatter only when its config is committed.** A repo with `.prettierrc` expects Prettier output; a repo without one expects your keystrokes and nothing else (SKILL.md Rule 9).
- **Autofix the reported lines, not the file.** `--fix` on a whole file mixes a semantic fix with a hundred whitespace changes.
- **Separate mechanical from semantic in commits.** Formatting-only commits should be exactly that, so they can be listed in a blame-ignore file and skipped by `git blame`.
- **Watch for invisible changes**: line-ending conversion (CRLF ↔ LF), a stripped or added final newline, trailing whitespace removal on save. Each shows up as "every line changed" and is usually an editor setting, not an edit.

## Wrapping Strategies

| Strategy | Diff behavior | Best for |
|---|---|---|
| No hard wrap (`line_wrap: none`) | One paragraph = one changed line; word-level diffs are unreadable in plain `git diff` | Files edited in an editor that soft-wraps; CJK content |
| Fixed column (80, 100) | Every edit reflows the rest of the paragraph | Terminal-first repos, older projects |
| One sentence per line (`sentence`) | Only the changed sentence shows; moving a sentence is a one-line move | Prose reviewed line by line in pull requests |

Semantic line breaks (one sentence, or one clause, per line) render identically to a wrapped paragraph — Markdown joins soft-wrapped lines with a space. The cost is a source file that looks unusual; the benefit is review comments that land on a sentence instead of a paragraph. Choose one per repo and write it into `## House Style` in `~/Clawic/data/markdown/memory.md` — or into `line_wrap` in `config.yaml` if the user stated it: mixing two is worse than either.

## Renaming and Moving

A heading rename or a file move breaks links that no build necessarily checks:

1. Compute the old and new slug or path.
2. Grep the repo for the old form — links, the TOC, the nav config, code comments, tests.
3. Check external inbound links where the page is public; leave a stub anchor or a redirect (`links.md`).
4. Update the nav or sidebar config: filesystem-driven generators pick the move up, config-driven ones do not (`docs-sites.md`).
5. Use `git mv` so history follows the file, and keep the move in its own commit — a move plus edits in one commit defeats rename detection and the diff shows the whole file as new.

## Splitting a Page

Split by **task**, not by length: one page answers one question a reader arrived with. The observable signal is a `##` section that a reader would reach from a different search than the page title — that section is a page.

When splitting: move the section verbatim first, commit, then edit it in place. Moving and rewriting in one step makes the diff unreviewable and loses paragraphs. Leave a link where the section was if anything pointed at it, and update the nav in the same commit as the move.

## Migrating Between Flavors

The general procedure, whatever the direction:

1. **Inventory the constructs** with grep, not by reading: `<!--`, `{{`, `<`, `{`, `:::`, `!!!`, `[!NOTE]`, `[[`, `~~~`, footnote refs, HTML tags. The counts are the migration estimate.
2. **Map each construct** to its equivalent in the destination, and mark the ones with no equivalent — those need a decision, not a rewrite.
3. **Convert mechanically** where a rule exists (Obsidian wikilinks → relative links, `!!! note` → `:::note`), with a script, so the transformation is reproducible.
4. **Build with strict mode** and fix top to bottom; errors cascade.
5. **Spot-check rendering** on the pages with the most constructs, not on the first page alphabetically.

Common directions and their sharp edge: Obsidian → docs site (wikilinks, embeds, and the slug rule for every filename); GitHub wiki → docs site (wikilinks again, plus flat namespace to a tree); docs site → MDX (`mdx.md`); anything → Confluence (one-way, `chat-platforms.md`).

## Bulk Edits

- Scripted rewrites over Markdown are safe only outside code fences. A naive `sed` that renames a term will also rename it inside every code sample and every URL.
- Prefer an AST tool (remark, a Pandoc Lua filter) when the change is structural — heading levels, link rewriting, frontmatter keys. Text tools for text, AST tools for structure.
- Always run the transform on a branch, build, and diff a sample of pages by eye before committing. The failure mode of a bulk edit is uniform, quiet damage.
- Keep the script as an `~/Clawic/data/markdown/artifacts/<what-it-rewrites>.md` file, with its `## Boxes` line written in the same turn. A migration that ran once will run again on a folder somebody missed.

## Reviewing Someone Else's Markdown

What is worth a comment, in order:

1. Does it render in the target — fences closed, tables valid, links resolvable?
2. Is the heading tree sane, one H1, no skipped levels?
3. Do the code samples run, and do they contain a real credential?
4. Is any of it an untested claim about a parser ("this works everywhere")?
5. Only then style, and only if the repo enforces that style.

Reviewing the rendered page, not just the diff, catches the whole first class. A comment about a bullet character while an unclosed fence goes unnoticed is a review that cost more than it returned.

## Generated and Vendored Files

- Generated Markdown (API references, CLI docs, changelogs from commits) must be edited at its **source**; an edit in the output survives until the next build and then confuses everyone.
- Mark them: a header comment (`<!-- generated by X; edit src/… -->`), an entry in `.prettierignore` and the lint ignore list, and a CODEOWNERS rule if the repo has one.
- Vendored docs (a copy of an upstream project's guide) are the same case: patch upstream, re-vendor, never hand-edit.

**Write what you learned about how they work**: conventions inferred from their files go in `## House Style` of `~/Clawic/data/markdown/memory.md` — and the moment the user *states* one, it is a declaration and moves to `config.yaml` instead. A migration procedure or a bulk-edit script worth reusing is an `artifacts/` file with its `## Boxes` line in the same turn; a rename that broke inbound links is a `## Pain Points` line, because that is the class of mistake that repeats (`memory-template.md`).
