# Chat, Tickets, and Wikis — Where Markdown Is a Subset or a Lie

Outside the forge and the docs site, "supports Markdown" means one of three things: a genuine subset, a different syntax that looks like Markdown, or an editor that converts what you type and then stores something else entirely. Sending GFM into these targets is the most common way a well-formed document arrives as noise.

**Before generating anything for one of these**, check that target's row in `## Render Targets` of `~/Clawic/data/markdown/memory.md`: the ones the user actually posts to are recorded there with what they were observed to refuse.

**Contents:** [Slack](#slack) · [Discord](#discord) · [Microsoft Teams](#microsoft-teams) · [Notion](#notion) · [Confluence](#confluence) · [Jira](#jira) · [Linear, GitHub and GitLab Issues](#linear-github-and-gitlab-issues) · [Reddit, Stack Overflow, Telegram, WhatsApp](#reddit-stack-overflow-telegram-whatsapp) · [Email and Plain Text](#email-and-plain-text) · [Choosing What to Send](#choosing-what-to-send)

## Slack

Slack's message format is `mrkdwn`, a different language with familiar characters:

| Want | Slack | Not |
|---|---|---|
| Bold | `*bold*` | `**bold**` renders with visible asterisks |
| Italic | `_italic_` | `*italic*` |
| Strike | `~strike~` | `~~strike~~` |
| Code | `` `code` ``, triple backtick block | — |
| Quote | `> quote` | — |
| Link | `<https://example.com\|text>` | `[text](url)` renders literally in API messages |
| List | Manual `•` or `-` plus line breaks | No real list semantics via the API |
| Heading, table, image | Not available in mrkdwn | Use Block Kit blocks, or send a file |

- The WYSIWYG composer accepts some standard Markdown as you type and converts it; the **API** does not. A bot posting `**bold**` shows asterisks, which is why agent-generated messages look broken.
- No tables at all. A fenced block with space-aligned columns is the only thing that survives, and it wraps badly on mobile.
- Long messages are truncated with a "show more" fold at roughly 4,000 characters per block; a long document belongs in a snippet or a file, not a message.

## Discord

- Closer to CommonMark than Slack: `**bold**`, `*italic*`, `__underline__`, `~~strike~~`, `` `code` ``, fenced blocks with language highlighting, `> quote`, `>>> ` for a multi-line quote.
- Headings (`#`, `##`, `###`), bullet and numbered lists, and `-# subtext` are supported in messages.
- Spoilers: `||hidden||`. Masked links `[text](url)` work in embeds and, on current clients, in messages from bots — not in plain user messages everywhere.
- No tables, no images from Markdown (upload or embed instead).
- 2,000-character limit per message (4,000 with Nitro); a longer answer must be split at block boundaries, never mid-fence.

## Microsoft Teams

- A limited subset in the composer: bold, italic, strikethrough, inline code, code blocks, bullet and numbered lists, quotes, links.
- No tables from Markdown; Adaptive Cards are the supported path for structured content, and they are JSON, not Markdown.
- Behavior differs between the desktop client, the web client, and messages posted by connectors — the same string can render three ways. Test in the surface that matters.

## Notion

- Pasting Markdown **converts** it into Notion blocks: headings, lists, quotes, code blocks and tables all survive; the file is no longer Markdown afterwards.
- Import (`.md` file) preserves more, including tables; paste is the lossy path for long documents.
- Typing Markdown works as input shortcuts (`# ` becomes a heading), which means literal Markdown syntax is hard to write in Notion at all — put it in a code block.
- Round-tripping out of Notion produces its own dialect (block ids in link URLs, `<!-- notionvc -->` comments in some exports). Export once, clean once, and keep the cleaned version as the source of truth.

## Confluence

- Cloud's editor is not Markdown. Pasting Markdown converts most constructs; typing Markdown triggers autoformat shortcuts.
- What converts reliably: headings, bold/italic, lists, links, inline code, fenced code (into a code macro), tables. What does not: footnotes, task list state, nested tables, raw HTML, callouts (they become quotes).
- Once converted, the content is stored as Confluence's own format — editing it later is editing Confluence, and "sync docs from the repo" projects that assume round-tripping fail here first.
- Server/Data Center versions still accept wiki markup (`h1.`, `{code}`) in some fields, which is a third, unrelated syntax.

## Jira

- Jira uses **wiki markup**, not Markdown: `h1. Title`, `*bold*`, `_italic_`, `{code:java}…{code}`, `||header||header||`, `# ` for ordered lists and `* ` for bullets.
- The Cloud editor autoformats a subset of Markdown as you type and converts pasted Markdown, so Markdown appears to work — until an integration writes the raw field and the wiki-markup renderer shows the asterisks.
- For anything written by a bot or an API call, generate wiki markup deliberately and test one issue before sending a hundred.

## Linear, GitHub and GitLab Issues

- The friendliest non-forge targets: GFM, including task lists, tables, fenced code, footnotes (GitHub), and Mermaid (GitHub).
- Task list state in issues is stored in the issue body — checking a box is an edit, so a bot rewriting the body clears the user's checkmarks.
- Autolinking is aggressive: `#123` becomes an issue link, `@name` a mention, `abc1234` a commit reference. Escape them (`\#123`) when they are literal, or a changelog fires notifications at strangers.
- Line length matters: issue bodies render in a narrow column, so wide tables scroll and long code lines are clipped.

## Reddit, Stack Overflow, Telegram, WhatsApp

- **Reddit**: its own renderer with tables, fenced code, spoilers (`>!text!<`), and superscript (`^text`). No images inline in most subreddits, and four-space indentation is still the reliable code form in old.reddit.
- **Stack Overflow**: CommonMark plus tables and a restricted HTML allowlist; four-space code indentation is idiomatic and fences are supported.
- **Telegram**: `MarkdownV2` requires escaping `_ * [ ] ( ) ~ \` > # + - = | { } . !` **everywhere** — an unescaped `.` or `-` is an API error, not a rendering glitch. Most bots use HTML mode precisely to avoid that list.
- **WhatsApp**: `*bold*`, `_italic_`, `~strike~`, triple backtick monospace. Nothing else.

## Email and Plain Text

- HTML email renders converted Markdown fine; plain-text email renders the syntax literally. Send both parts, generated from the same source (`conversion.md`).
- For a plain-text destination, the readable degradation is: headings as an underline of `=`/`-`, lists as `- `, emphasis as nothing (not asterisks), links as `text (https://url)`, tables as space-aligned columns in a fixed-width block.
- Line length matters again: hard wrap at 72–78 columns for plain-text mail, because the client will not wrap for you.

## Choosing What to Send

1. **Identify the surface** — API or composer, bot or human. Composers convert; APIs do not.
2. **Reduce to the target's subset** before generating, not afterwards. Downgrading a finished document loses structure invisibly.
3. **Move what does not fit out of the message**: a table, a long code sample, or a document belongs in a file, a snippet, or a link — every one of these platforms handles an attachment better than a 3,000-character wall.
4. **Test one message.** Every platform in this file has at least one surprise, and one test message costs less than a channel full of asterisks.

**Write the result**: each platform the user actually posts to is a row in `## Render Targets` of `~/Clawic/data/markdown/memory.md` — the flavor, the surface (API vs composer), and in `Confirmed refuses` what it was observed to mangle (`memory-template.md`). A message shape that works and gets reused — a release announcement, a status update, an incident notice — is a template in `artifacts/` with its `## Boxes` line in the same turn.
