## Description:

Connects an agent to Gmail through Maton to read, send, and manage messages, threads, labels, and drafts.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams use this skill to work with an authorized Gmail account, including reading mail, preparing drafts, sending approved messages, and setting up explicitly requested email automations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Access to sensitive correspondence in the connected Gmail account.

Mitigation: Connect only the intended account, use the minimum necessary access, and prefer OAuth login over raw API keys.

Risk: Incorrect or unintended messages, edits, and deletions.

Mitigation: Confirm the exact account, recipient or target, content, and intended effect before every write or send.

Risk: Triggers and destinations can continuously disclose matching email data.

Mitigation: Approve each automation and destination separately; verify the host, minimize forwarded fields, and plan when to remove it.

## Reference(s):

- [Gmail skill release on ClawHub](https://clawhub.ai/byungkyu/skills/gmail)
- [Maton homepage](https://maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Gmail API overview](https://developers.google.com/gmail/api/reference/rest)
- [Gmail trigger reference](references/google-mail/triggers.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Guidance]

**Output Format:** [Text or Markdown with command and code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Mailbox actions and automations require an authorized account and explicit approval for changes.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
