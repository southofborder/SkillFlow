## Description:

Send messages, reply to messages, and search message history in Discord channels using the message tool.

This skill is ready for commercial/non-commercial use.

## Publisher:

[bowenqt](https://clawhub.ai/user/bowenqt)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to let an agent communicate in Discord channels, search message history, and manage channel interactions through configured Discord bot permissions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can perform live Discord operations, including message edits, message deletion, channel edits, channel moves, and channel/category deletion.

Mitigation: Install only for agents that need Discord operations, use least-privilege bot roles, and require explicit confirmation before edit, delete, move, or channel/category actions.

Risk: Discord bot tokens and webhook secrets can grant broad access if exposed.

Mitigation: Store tokens and webhook secrets in environment variables or secret management, avoid placing secrets in URLs, and rotate credentials immediately if exposed.

Risk: Channel and category deletion actions can permanently remove Discord resources.

Mitigation: Restrict delete permissions to trusted workflows and confirm target IDs, channel names, and audit-log reasons before executing deletion commands.

## Reference(s):

- [Discord Channel Management](references/CHANNELS.md)
- [Discord Bot Configuration](references/CONFIG.md)
- [Discord Search Patterns](references/SEARCH.md)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord Permissions Documentation](https://discord.com/developers/docs/topics/permissions)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell command examples and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces Discord message, search, reaction, moderation, and channel-management command guidance for an agent.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
