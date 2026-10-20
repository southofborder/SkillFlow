## Description:

Guides agents using MeiGen for image and video generation, dedicated image workflows, discovery, and optional creative planning while preserving the user's approved scope and budget.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jau123](https://clawhub.ai/user/jau123)

### License/Terms of Use:

MIT-0

## Use Case:

Creators and developers use this skill to guide authorized MeiGen image and video generation, product-image editing, inspiration discovery, and recovery of generation jobs within an existing workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompts, references, job details, and prepared media are sent to MeiGen or configured providers; prepared uploads may have public temporary URLs.

Mitigation: Review material and upload URLs before sending; avoid sensitive references unless the user accepts cloud processing and public-link exposure.

Risk: Account library and saved-character access exposes private content through OAuth permissions.

Mitigation: Review requested scopes and grant only intended access; access private collections only when relevant to the user's request.

Risk: Generation and dedicated image workflows may spend purchased credits, including on duplicate retries.

Mitigation: Check live prices and the approved budget; preserve request IDs and recover existing jobs rather than starting new paid attempts.

## Reference(s):

- [MeiGen OpenClaw integration](https://www.meigen.ai/mcp?tab=openclaw)
- [MeiGen ClawHub plugin](https://clawhub.ai/plugins/meigen-ai-design)
- [Providers and configuration](references/providers.md)
- [Troubleshooting](references/troubleshooting.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown guidance with tool calls, result URLs, and task handles]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Generated media are returned as URLs or saved paths when available; jobs may return status and recovery identifiers.]

## Skill Version(s):

3.2.0 (source: frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
