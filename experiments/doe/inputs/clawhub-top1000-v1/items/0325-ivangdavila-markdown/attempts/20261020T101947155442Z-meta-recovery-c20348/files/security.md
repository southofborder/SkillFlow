# Rendering Markdown You Did Not Write

Markdown is a superset of HTML in most implementations, which makes "render this Markdown" equivalent to "render this HTML" — the exact operation every web security guide tells you not to perform on untrusted input. Any pipeline that renders user comments, issue bodies, scraped pages, or model output is in this file's scope.

**Contents:** [The Threat Model](#the-threat-model) · [Raw HTML](#raw-html) · [Link and Image Schemes](#link-and-image-schemes) · [Sanitize After Rendering](#sanitize-after-rendering) · [Parser Settings That Matter](#parser-settings-that-matter) · [MDX and Templates Are Code](#mdx-and-templates-are-code) · [Frontmatter Deserialization](#frontmatter-deserialization) · [Includes and Path Traversal](#includes-and-path-traversal) · [Invisible and Deceptive Characters](#invisible-and-deceptive-characters) · [Privacy Leaks in Documents](#privacy-leaks-in-documents) · [Secrets in Documents](#secrets-in-documents)

## The Threat Model

| Input | Risk |
|---|---|
| User comments, wiki edits, issue bodies | Stored XSS via raw HTML or a `javascript:` URL |
| Scraped or fetched pages converted to Markdown | Injected instructions and HTML carried through the conversion |
| Model or agent output rendered in a UI | Same as user input — it is untrusted text, whatever produced it |
| A repo's own docs, rendered by a build | Path traversal through includes; command execution through template engines |
| A document pasted in by the user for storage | Secrets, personal data, tracking pixels |

The last row is the one this skill hits daily, and it is the reason the Data rule in `SKILL.md` covers everything under `~/Clawic/data/`, not a list of files.

## Raw HTML

- CommonMark **passes raw HTML through by definition**. A renderer that does not sanitize will happily emit `<script>` from a comment body.
- GFM's spec disallows a handful of tags (`script`, `style`, `iframe`, `title`, `textarea`, `xmp`, `noembed`, `noframes`, `plaintext`); github.com applies a much stricter allowlist on top. The spec-level rule is not a security boundary on its own.
- Dangerous beyond `<script>`: `<style>` (exfiltration via CSS selectors, page defacement), `<iframe>`, `<object>`/`<embed>`, `<form>` (credential harvesting inside a trusted page), `<meta http-equiv="refresh">`, `<base>` (rewrites every relative link on the page), and **any event-handler attribute** (`onload`, `onerror`, `onmouseover`) on an otherwise harmless tag.
- `<img src=x onerror=…>` is the canonical payload: the tag is on every allowlist, the attribute is the problem. Sanitizers must filter attributes, not just tags.

## Link and Image Schemes

- `[text](javascript:alert(1))` is valid Markdown. CommonMark does not restrict schemes; it is the renderer's job.
- Allowlist schemes: `http`, `https`, `mailto`, and whatever the application genuinely needs. Block `javascript:`, `vbscript:`, `file:`, and `data:` — except, if you must, `data:image/*` for inline images.
- Obfuscation is routine: `java\tscript:`, `JaVaScRiPt:`, HTML entities inside the scheme, percent-encoding, and Unicode look-alikes. Normalize and parse the URL before comparing, never regex the raw string.
- Autolinking turns bare text into links, which extends the attack surface to anything that looks like a URL. Where content is untrusted, autolinking is a choice, not a default.
- Images fetch on render: an image URL in a comment is a tracking pixel that logs every reader's IP. GitHub proxies images through an anonymizing cache precisely for this; an application that renders untrusted Markdown should proxy too.

## Sanitize After Rendering

The order matters. Sanitizing Markdown **before** rendering is defeated by anything the parser reconstructs; sanitize the **HTML output**, with a mature library, against an allowlist.

1. Render Markdown to HTML with raw HTML disabled if the application does not need it.
2. Run the output through an HTML sanitizer (DOMPurify in the browser, a maintained server-side equivalent elsewhere) with an allowlist of tags **and attributes**.
3. Apply the URL-scheme allowlist to `href` and `src` after sanitizing.
4. Set a Content Security Policy — the layer that limits the damage when steps 1–3 have a gap. `script-src` without `unsafe-inline` neutralizes most injected payloads.
5. Never re-insert user HTML after sanitizing (a "highlight the search term" pass that runs afterwards is a favourite way to reintroduce the hole).

Allowlists beat denylists here without exception: the set of dangerous constructs grows with every browser release, the set of tags a comment needs does not.

## Parser Settings That Matter

| Parser | The setting |
|---|---|
| markdown-it | `html: false` (default in the library, often flipped on in wrappers); `linkify` extends autolinking; it ships a URL validator that blocks `javascript:`, `vbscript:` and non-image `data:` — do not disable it |
| marked | `sanitize` was removed; use an external sanitizer, as the project documents |
| cmark / cmark-gfm | `--unsafe` enables raw HTML and dangerous URLs; without it they are replaced with a comment |
| remark/rehype | `rehype-raw` re-enables HTML; pair it with `rehype-sanitize` and put sanitize last in the pipeline |
| Python-Markdown | No sanitizer; `bleach` or an equivalent afterwards |
| Goldmark (Hugo) | `unsafe: false` by default — the safest default in this list |

A wrapper library's defaults are not the underlying parser's defaults. Check the setting in the code, not in the parser's documentation.

## MDX and Templates Are Code

- **MDX compiles to JavaScript.** Rendering untrusted MDX is executing untrusted code — there is no sanitizer for it. Never accept MDX from users, and never let a build compile MDX from a source you do not control (`mdx.md`).
- Template layers run **before** Markdown: Liquid (Jekyll), Go templates (Hugo), Jinja (mkdocs-macros). User-supplied content that reaches them is server-side template injection, which is worse than XSS.
- A docs pipeline that builds pull requests from forks executes fork-supplied configuration and plugins. Build untrusted PRs in an isolated job without repository secrets.

## Frontmatter Deserialization

- YAML is not a data format, it is a serialization format: unsafe loaders instantiate objects. Use the safe loader (`yaml.safe_load`, `SafeConstructor`, the default in most modern libraries) for any frontmatter you did not write.
- Anchors and aliases allow exponential expansion (the "billion laughs" pattern) — a small file that exhausts memory at parse time. Cap input size and expansion depth for untrusted files.
- Unbounded key sets from user files leak into templates: allowlist the frontmatter keys the application reads.

## Includes and Path Traversal

- Include and snippet directives (`--8<--`, `{% include %}`, `{include}`) resolve a path from the document. Where the document is untrusted, `../../../../etc/passwd` is the obvious probe and reading a private file into a public page is the outcome.
- Restrict include roots in the generator's configuration, and never enable includes on a corpus that accepts contributions you do not review.
- The same applies to image and resource paths in a conversion pipeline (`--resource-path`, `conversion.md`): a build that embeds arbitrary local files into a PDF is an exfiltration primitive.

## Invisible and Deceptive Characters

- **Bidirectional control characters** (U+202E and friends) can make source code display in an order different from how it executes — the "trojan source" class. In documentation, they can make a command display as something other than what a reader copies.
- **Zero-width characters** hide content inside apparently normal text: watermarks, tracking, or a payload assembled after copy-paste.
- **Homoglyphs**: Cyrillic `а` in a domain name inside a link that looks legitimate.
- Detection: scan for characters outside the expected script ranges before rendering or storing. Any find is at minimum a paste artifact worth removing, and at worst deliberate (`structure.md` covers the accidental version).

## Privacy Leaks in Documents

- **Images fetch on render**, so an external image URL in a document reports each reader to its host.
- **Screenshots** carry more than intended: window titles, adjacent tabs, notification banners, staging URLs, real customer names in test data. Crop and review before committing.
- **Metadata** rides along in images (EXIF, including GPS) and in exported DOCX and PDF (author, path, revision history) — strip it on the way out (`conversion.md`).
- **Internal URLs** in a public README (staging hosts, admin paths, internal ticket links) map an organization's infrastructure for free.

## Secrets in Documents

Documentation is the densest source of credentials in a repository: quickstarts carry API keys, configuration pages carry connection strings, CI pages carry publish tokens, and a support transcript pasted into a troubleshooting page carries all three.

- **Placeholders must be obviously fake and structurally valid**: `<env:API_TOKEN>`, `sk_test_00000000000000000000`. A realistic-looking fake key gets copied into a real config; a real one gets scanned by bots within minutes of the push.
- **Scan the docs tree** with the same secret scanner CI runs over code — documentation is usually excluded from those globs by accident.
- **A leaked credential in a document is leaked**: the fix is rotation, not a commit that removes the line. Git history keeps it, and so do forks, mirrors, and the package tarball.
- **Nothing is written under `~/Clawic/data/` with a live value in it.** When the user pastes a document to keep, replace each secret with its `<kind>:<locator>` pointer **before** writing, and say in one line that you did (SKILL.md Data; the two lists of what counts as a secret in this domain are in `memory-template.md`).

**Write what the review established**: a sanitizer configuration, an allowlist, or a rendering pipeline that was reasoned through once is an `artifacts/` file with its `## Boxes` line in the same turn — including what was rejected and why, because "we tried allowing `<style>`" is exactly the decision that gets re-litigated. A leak or a near miss is a `## Pain Points` line with the date and what changed as a result (`memory-template.md`).
