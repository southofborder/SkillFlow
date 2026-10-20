## Description:

Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Agents assisting developers and workspace operators use this skill to authenticate the gog CLI and run Google Workspace tasks across Gmail, Calendar, Drive, Contacts, Sheets, and Docs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The gog CLI can access selected Google Workspace services through user-provided OAuth credentials.

Mitigation: Grant only the services needed during OAuth setup and review account selection before running commands.

Risk: Commands can send email, create calendar events, or change and clear Sheets or Drive content.

Mitigation: Require explicit confirmation before taking write actions in Gmail, Calendar, Sheets, or Drive.

## Reference(s):

- [Gog homepage](https://gogcli.sh)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/gog)
- [Publisher profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the local gog binary and user-configured OAuth credentials; gog commands can emit JSON when requested.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
