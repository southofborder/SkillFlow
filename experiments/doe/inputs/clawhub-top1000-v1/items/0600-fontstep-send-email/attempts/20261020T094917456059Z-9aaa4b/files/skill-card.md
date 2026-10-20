## Description:

Send emails via SMTP using environment-injected configuration.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fontstep](https://clawhub.ai/user/fontstep)

### License/Terms of Use:


## Use Case:

Agents use this skill to send SMTP email messages for users, including optional file attachments, after the user has configured provider credentials through injected environment variables.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can send email and arbitrary attachments using stored SMTP credentials.

Mitigation: Use a limited SMTP app password, restrict permitted recipients and attachments, and require user confirmation before sending.

Risk: The security review notes missing TLS safeguards before trusting the skill with valuable mail credentials.

Mitigation: Update the SMTP script to use a verifying TLS context before using high-value accounts or sensitive email content.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/fontstep/skills/send-email)

## Skill Output:

**Output Type(s):** [shell commands, configuration, text]

**Output Format:** [Command-line invocation and SMTP send status text]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Supports recipient, subject, body, and optional attachment path; uses SMTP settings from injected environment variables.]

## Skill Version(s):

1.0.1 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
