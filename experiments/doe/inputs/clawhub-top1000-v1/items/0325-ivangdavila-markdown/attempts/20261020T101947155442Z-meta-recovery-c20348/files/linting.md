# Linting, Formatting, and CI

Two different jobs, and most repository pain comes from giving them to the same tool: a **formatter** owns whitespace and normalizes it without asking; a **linter** owns semantics and reports what a human must decide. Configure both to agree on that boundary and the fights stop.

**Before changing rules or debugging CI**, read the doc set's row in `## Doc Sets` of `~/Clawic/data/markdown/memory.md` for the tool in force, and check `## Boxes` for a stored config in `artifacts/` — the exclusions in it were paid for once already.

**Contents:** [The Ownership Split](#the-ownership-split) · [markdownlint](#markdownlint) · [Rules Worth Configuring](#rules-worth-configuring) · [Prettier](#prettier) · [remark](#remark) · [Making Them Coexist](#making-them-coexist) · [Link and Spell Checking](#link-and-spell-checking) · [CI Design](#ci-design) · [Adopting Lint on an Existing Repo](#adopting-lint-on-an-existing-repo)

## The Ownership Split

| Concern | Owner | Why |
|---|---|---|
| Bullet character, indent width, table padding, blank-line counts, trailing whitespace, final newline | Formatter | Mechanical, no judgement, fixable everywhere |
| Heading hierarchy, duplicate headings, missing alt text, bare URLs, inline HTML policy, line length in prose | Linter | Needs a decision; autofix would change meaning |
| Broken links and anchors | Link checker | Needs the network or the built site |
| Spelling and terminology | Spell checker with a project dictionary | Needs a word list, not a rule |

When both tools claim a concern, **disable it in the linter**, not in the formatter: the formatter runs on save and wins by default anyway, and a rule that fires on every save is a rule everyone learns to ignore.

## markdownlint

The default choice (`lint_tool: markdownlint`). Rules are numbered `MD001`–`MD05x` with readable aliases, and configuration lives in `.markdownlint-cli2.jsonc` (or `.markdownlint.jsonc`) at the repo root.

- `markdownlint-cli2` is the current CLI: faster, config-driven globs, `--fix` for the mechanically fixable rules.
- Inline control: `<!-- markdownlint-disable MD013 -->` … `<!-- markdownlint-enable MD013 -->`, or `<!-- markdownlint-disable-next-line MD033 -->`. Every inline disable should carry a reason in the comment; an unexplained one becomes permanent.
- `--fix` is safe for whitespace-class rules and unsafe for anything structural. Fix the reported lines rather than the file (SKILL.md Rule 9).

## Rules Worth Configuring

| Rule | Default | The usual decision |
|---|---|---|
| MD013 line-length | 80 | The most-argued rule. Either off, or on for prose with `tables: false`, `code_blocks: false`, `headings: false` and a wider limit — a URL alone can exceed 80 |
| MD033 no-inline-html | all HTML flagged | Set `allowed_elements` to the ones the target actually renders (`details`, `summary`, `img`, `picture`, `br`) rather than turning the rule off |
| MD024 no-duplicate-heading | strict | `siblings_only: true` for reference docs that repeat `## Errors` under each endpoint |
| MD041 first-line-heading | on | Off for files with frontmatter that supplies the title, and for partials/includes |
| MD029 ol-prefix | `one_or_ordered` | Pick `one` (lazy numbering) or `ordered` and enforce it — this is the setting behind the numbering debate |
| MD004 ul-style | consistent | Set it to the `list_marker` value so the formatter and the linter agree |
| MD007 ul-indent | 2 | Must equal `list_indent`; a mismatch here is the classic formatter-versus-linter loop |
| MD046 code-block-style | consistent | `fenced` — indented code has no language tag (`code.md`) |
| MD040 fenced-code-language | on | Keep it on; it is the rule that buys highlighting and copy buttons |
| MD045 no-alt-text | on | Keep it on; it is the only automated accessibility check in the set (`accessibility.md`) |
| MD034 no-bare-urls | on | Keep it on where the target lacks autolink literals; off for GFM-only repos that prefer bare URLs |
| MD012 multiple-blanks / MD009 trailing-spaces / MD047 final-newline | on | Hand them to the formatter and disable them here |

## Prettier

- Formats Markdown with `proseWrap: "preserve"` by default — it does not rewrap prose unless told. `"always"` wraps at `printWidth`; `"never"` unwraps paragraphs to one line each. This setting must match `line_wrap`, or every save fights the house style.
- It normalizes bullets to `-`, ordered lists, emphasis markers, table padding (always aligned), blank-line counts, and escaping. Table alignment is not configurable — if aligned tables produce unacceptable diffs, Prettier is not the right formatter for that repo (`tables.md`).
- Embedded code in fences is formatted by the matching Prettier parser when one exists; `embeddedLanguageFormatting: "off"` stops it from reformatting samples that were written to look a specific way.
- `.prettierignore` for generated files, vendored docs, and anything with intentional formatting (ASCII diagrams, fixtures).

## remark

The programmable option (`lint_tool: remark`): a plugin pipeline over the Markdown AST, configured in `.remarkrc`.

- `remark-preset-lint-recommended` and `-consistent` are the usual starting points; individual rules are packages.
- Its advantage over markdownlint is **transformation**: the same pipeline can enforce and rewrite — normalize link references, generate a TOC (`remark-toc`), validate internal links (`remark-validate-links`), check frontmatter against a schema.
- Its cost is a Node dependency chain and slower runs. Worth it for a large doc set with custom conventions; overkill for a repo with six files.
- Where the site already uses remark (Docusaurus, MDX), the linter and the renderer share a parser — the strongest argument for it.

## Making Them Coexist

1. Choose the formatter (Prettier, or `--fix` from markdownlint, not both).
2. Set `MD004`/`MD007`/`MD029` in the linter to exactly what the formatter produces.
3. Disable the whitespace-class rules in the linter (MD009, MD012, MD047, MD030, MD046 if the formatter enforces it).
4. Run the formatter first, the linter second, in the same CI job — otherwise a formatter change re-triggers lint failures in a later job and the report contradicts itself.
5. Verify with one deliberately messy file: format, lint, and confirm the result is stable across two runs. Instability here is a loop that will hit someone at 6pm on a Friday.

## Link and Spell Checking

- **Internal links and anchors**: check on every commit, they are free and they break constantly (`links.md`).
- **External links**: check on a cadence, not per commit — rate limits, flaky sites, and 403s to bots make a per-commit external check a permanently red job.
- **Spelling**: `cspell` or `codespell` with a committed project dictionary. The dictionary is the deliverable: without one, the check is noise and gets disabled within a week.
- **Terminology**: a rule set of banned or preferred terms (`vale` is the common tool) catches "e-mail vs email" drift that a spell checker cannot.

## CI Design

- **Block on what is objectively broken**: build failure, broken internal links, missing alt text, unclosed fences. **Warn on style**: line length, prose rules, external links.
- Run on changed files for speed on pull requests and on the whole tree on a schedule; a full-tree run on every PR gets skipped by whoever is in a hurry.
- Annotate the diff rather than dumping a log: reviewers fix what is pointed at, not what is buried on line 400 of a job output.
- Pin the tool versions. A linter that auto-upgrades turns an unrelated PR red and the team learns to merge past red.
- One job, ordered: format check → lint → internal links → build. Fail fast; the later steps are meaningless if the file does not parse.

## Adopting Lint on an Existing Repo

The mistake is enabling everything and opening a 4,000-error pull request nobody can review.

1. Run with defaults, count violations **per rule**. Usually two or three rules produce 90% of them (MD013 and MD033 almost always).
2. Decide those two or three deliberately — off, scoped, or accepted — before touching any file.
3. Autofix the whitespace class in **one commit that changes nothing else**, so it can be skipped in `git blame` with a blame-ignore file.
4. Fix the remaining semantic violations in small batches, by section.
5. Only then turn the job from warning to blocking. Enabling the gate before the backlog is cleared teaches everyone to bypass it.

**Write the outcome**: the config that finally passed goes to `~/Clawic/data/markdown/artifacts/lint-<docset>.md` — the file itself plus **one line per exclusion explaining why it is off**, which is the part that stops the next person re-enabling it — with its `## Boxes` line in the same turn. The tool and whether CI blocks or warns go in that doc set's row in `## Doc Sets` of `memory.md`, each sweep gets a row in `checks/<year>.md`, and an agreed cadence becomes a `## Due` row (`memory-template.md`).
