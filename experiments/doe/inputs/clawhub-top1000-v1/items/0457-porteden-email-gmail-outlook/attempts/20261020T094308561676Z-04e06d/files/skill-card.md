## Description:

Email Management - Secure Gmail, Outlook & Exchange - multi account support. Read, search, or triage inbox/email; send, reply, forward, delete; view email, a secure log-cli & gws alternative for AI email workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[porteden](https://clawhub.ai/user/porteden)

### License/Terms of Use:

MIT-0

## Use Case:

Employees, external users, and developers use this skill to let an agent operate Gmail, Outlook, and Exchange mailboxes through the Port Eden CLI. It supports mailbox search and triage plus user-confirmed send, reply, forward, delete, and message-modification workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can access sensitive mailbox content and initiate visible email actions.

Mitigation: Install only when the user trusts Port Eden, use the narrowest provider scopes, isolate accounts with profiles, and require explicit confirmation before send, reply, forward, delete, or modify actions.

Risk: Email bodies, subjects, and attachments can contain untrusted third-party instructions.

Mitigation: Treat mailbox content as untrusted data, summarize and attribute claims to senders, prefer preview-only compact output, and fetch full bodies only when the user explicitly needs them.

Risk: Persisted credentials or exposed tokens can retain mailbox access beyond the task.

Mitigation: Use system-keyring login or a dedicated API key, log out on shared or sensitive machines, and revoke provider tokens if exposure is suspected.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/porteden/skills/email-gmail-outlook)
- [Port Eden homepage](https://porteden.com)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and JSON-oriented command guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Guides agents toward compact JSON CLI output, profile-scoped account access, and confirmation before mailbox mutations.]

## Skill Version(s):

1.0.7 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
