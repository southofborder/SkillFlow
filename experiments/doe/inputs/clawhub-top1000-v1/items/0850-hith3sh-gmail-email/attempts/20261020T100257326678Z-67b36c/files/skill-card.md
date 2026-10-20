## Description:

Read, search, draft, reply to, and organize Gmail from chat via the Gmail API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hith3sh](https://clawhub.ai/user/hith3sh)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to connect a Gmail account through ClawLink and let an agent search, read, draft, send, reply to, forward, label, archive, trash, and retrieve Gmail content.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill asks users to trust a third-party hosted service and plugin with full Gmail mailbox access.

Mitigation: Install only if that access is acceptable, prefer a lower-risk Google account for testing, review Google's consent screen carefully, and revoke access from Google account permissions when no longer needed.

Risk: Write operations can send email, change labels, archive messages, move messages to trash, or permanently delete messages.

Mitigation: Preview write actions, get explicit user confirmation, and confirm recipients, subject, body, and destructive effects before execution.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/hith3sh/skills/gmail-email)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)
- [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=gmail-email)
- [ClawLink Docs](https://docs.claw-link.dev/openclaw)
- [Google Account Permissions](https://myaccount.google.com/permissions)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and JSON tool parameters]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include Gmail API-backed mailbox content and proposed write actions that require user confirmation before execution.]

## Skill Version(s):

1.0.9 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
