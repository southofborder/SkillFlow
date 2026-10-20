## Description:

Read and send email via IMAP/SMTP. Check for new/unread messages, fetch content, search mailboxes, mark as read/unread, and send emails with attachments. Supports multiple accounts. Works with any IMAP/SMTP server including Gmail, Outlook, 163.com, vip.163.com, 126.com, vip.126.com, 188.com, and vip.188.com.

This skill is ready for commercial/non-commercial use.

## Publisher:

[gzlicanyi](https://clawhub.ai/user/gzlicanyi)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and email automation users use this skill to configure IMAP/SMTP accounts, inspect and search mailboxes, fetch messages, manage read state, download attachments, and send email from an agent workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can access mailbox contents and send email on the user's behalf.

Mitigation: Use app-specific passwords when available, keep credentials scoped to the intended account, and review outgoing email commands before execution.

Risk: Attachment reads and downloads can expose or write local files if directory allowlists are too broad.

Mitigation: Keep ALLOWED_READ_DIRS and ALLOWED_WRITE_DIRS narrow, and avoid symlinked download directories.

Risk: The dependency and install chain needs review before use.

Mitigation: Install from trusted registries and update or pin dependencies before deployment.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/gzlicanyi/skills/imap-smtp-email)
- [Google App Passwords](https://myaccount.google.com/apppasswords)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration, JSON, Text, Markdown]

**Output Format:** [Markdown guidance with shell commands and JSON command results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Email commands can read mailbox content, send mail, mark messages, and read or write attachment files within configured directory allowlists.]

## Skill Version(s):

0.0.19 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
