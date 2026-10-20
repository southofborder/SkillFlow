## Description:

Clawdbot documentation expert with decision tree navigation, search scripts, doc fetching, version tracking, and config snippets for all Clawdbot features

This skill is ready for commercial/non-commercial use.

## Publisher:

[nicholasspisak](https://clawhub.ai/user/nicholasspisak)

### License/Terms of Use:

MIT

## Use Case:

Developers and operators use this skill to find, summarize, and apply Clawdbot documentation for setup, troubleshooting, provider configuration, automation, deployment, and common gateway patterns.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Copying the gateway example with host 0.0.0.0 can expose a local service if network controls are not in place.

Mitigation: Use 127.0.0.1 for local-only use, or require authentication, firewalling, and TLS or reverse-proxy controls for remote access.

## Reference(s):

- [Clawdbot documentation](https://docs.clawd.bot/)
- [Clawdbot Discord provider documentation](https://docs.clawd.bot/providers/discord)
- [Common Config Snippets](snippets/common-configs.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Full-text indexing guidance depends on qmd; other helper scripts are simple local shell commands.]

## Skill Version(s):

1.2.2 (source: package.json and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
