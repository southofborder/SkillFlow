## Description:

Post to X (Twitter) using the official API with OAuth 1.0a. Use when you need to tweet, post updates, or publish content. Bypasses rate limits and bot detection that affect cookie-based approaches like bird CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[lobstergeneralintelligence](https://clawhub.ai/user/lobstergeneralintelligence)

### License/Terms of Use:

MIT

## Use Case:

Developers and agents use this skill to publish posts to X through the official API when cookie-based posting tools are unreliable. It is suited for posting updates or multi-line tweets after credentials and write permissions are configured.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill uses write-capable X credentials and can publish live posts.

Mitigation: Use a dedicated or low-risk X app token and review post text before running the command.

Risk: Global npm installation and unpinned dependency resolution can increase dependency exposure.

Mitigation: Avoid global npm installation when possible and prefer pinned dependencies with a lockfile.

## Reference(s):

- [X Developer Portal](https://developer.x.com/en/portal/dashboard)
- [X Developer Platform](https://developer.x.com)
- [bird CLI](https://github.com/steipete/bird)
- [ClawHub skill page](https://clawhub.ai/lobstergeneralintelligence/skills/x-api)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and plain-text command output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Successful posting returns an X status URL; failures return diagnostic text from the command or API.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
