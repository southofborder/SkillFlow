## Description:

Manage notes, tasks, calendars, files, contacts, and Deck boards in a Nextcloud account.

This skill is ready for commercial/non-commercial use.

## Publisher:

[keithvassallomt](https://clawhub.ai/user/keithvassallomt)

### License/Terms of Use:

MIT-0

## Use Case:

OpenClaw users and developers use this skill to organize and update their Nextcloud notes, tasks, calendar events, files, contacts, and Kanban boards.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: An account-level Nextcloud app password grants broad access to account data.

Mitigation: Use a dedicated, revocable app password, try a test account first, and keep the Nextcloud connection on HTTPS.

Risk: Delete commands and file uploads can permanently remove or overwrite data.

Mitigation: Confirm the exact operation and target with the user before execution; use the required confirmation token for irreversible commands.

Risk: Public share links may expose files outside the account or grant edit access.

Mitigation: Confirm the path and permissions before sharing; prefer read-only links and consider a password and expiry.

## Reference(s):

- [ClawHub skill listing](https://clawhub.ai/keithvassallomt/skills/openclaw-nextcloud)
- [Project homepage (declared in skill metadata)](https://github.com/keithvassallomt/openclaw-nextcloud)

## Skill Output:

**Output Type(s):** [Text, Shell commands, JSON]

**Output Format:** [Natural-language responses and structured JSON command output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Account changes take effect immediately; operations may not be reversible.]

## Skill Version(s):

0.8.0 (source: server-resolved release, package.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
