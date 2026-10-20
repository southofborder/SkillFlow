## Description:

Search GIF providers with CLI/TUI, download results, and extract stills/sheets.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers, content creators, and communication teams use this skill to find GIFs from Tenor or Giphy, preview and download results, and extract still frames or contact sheets for review, documentation, pull requests, or chat.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs gifgrep from third-party sources, including an unpinned Go @latest path and a third-party Homebrew tap.

Mitigation: Pin or independently verify the installed gifgrep source before use, especially in managed or production environments.

Risk: The skill can use GIPHY_API_KEY and TENOR_API_KEY with external GIF providers.

Mitigation: Provide API keys only when approved for this CLI and avoid exposing them in logs, shared shell history, or committed configuration.

## Reference(s):

- [Gifgrep homepage](https://gifgrep.com)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/gifgrep)
- [Publisher profile](https://clawhub.ai/user/steipete)
- [Go module install source](https://github.com/steipete/gifgrep/tree/main/cmd/gifgrep)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with inline shell commands and CLI examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Commands may return URLs, JSON search results, downloaded GIF files, or PNG stills/contact sheets when executed with gifgrep.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
