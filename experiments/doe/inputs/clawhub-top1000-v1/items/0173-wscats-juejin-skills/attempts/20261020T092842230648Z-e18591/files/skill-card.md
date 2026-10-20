## Description:

A Juejin community operations skill for querying hot article rankings, publishing Markdown articles as drafts by default, and downloading Juejin articles as Markdown.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to interact with juejin.cn from an agent: inspect Juejin hot article rankings, prepare Markdown articles for draft publication, and save explicit Juejin article links to local Markdown files.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill stores a Juejin session cookie locally, and that cookie can act as the user's logged-in Juejin account while it remains valid.

Mitigation: Install only when the publisher is trusted, use a personal machine instead of shared or CI environments, and delete ~/.juejin_cookie.json after use.

Risk: Publishing workflows can affect a public Juejin account if public publication is intentionally enabled.

Mitigation: Keep the default draft-only posture unless the user explicitly confirms public publishing through the documented confirmation gates.

Risk: Download workflows write article content and optional images to local files, and the security summary flags file-write behavior for careful review.

Mitigation: Use the default ./output location or a deliberate JUEJIN_OUTPUT_ROOT, review requested download targets, and avoid exposing the lower-level Python API to untrusted callers.

Risk: The security guidance identifies unresolved lower-level API concerns, including URL validation, cookie-path constraints, redirect handling, and a vulnerable lxml pin.

Mitigation: Treat the lower-level API as unsafe for untrusted callers until those issues are fixed and rely on the narrower documented agent workflows.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/wscats/skills/juejin-skills)
- [Publisher profile](https://clawhub.ai/user/wscats)
- [Project homepage from ClawHub metadata](https://github.com/wscats/juejin)
- [Juejin target site](https://juejin.cn/)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown, JSON-like results, local Markdown files, and shell command guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May create or read local session-cookie and article files when the user explicitly invokes authenticated publishing or article download workflows.]

## Skill Version(s):

1.0.8 (source: server release metadata and skill frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
