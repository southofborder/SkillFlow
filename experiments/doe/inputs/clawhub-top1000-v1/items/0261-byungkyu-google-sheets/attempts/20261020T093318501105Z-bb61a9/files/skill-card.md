## Description:

Helps agents read, update, and format Google Sheets spreadsheets through a user-authorized Maton connection.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams use this skill to retrieve and edit spreadsheet values, create sheets, apply formatting, and configure approved automations using their connected account.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Spreadsheet writes or new connections may affect the wrong account or data.

Mitigation: Confirm the connection, target, intended changes, and user authorization before proceeding; prefer read-only access where possible.

Risk: Hosted functions and persistent triggers may run later or send data to an unintended destination.

Mitigation: Require explicit approval of each deployment, trigger, and destination, and review what data will be shared.

Risk: Fallback API keys and spreadsheet responses can expose sensitive information.

Mitigation: Prefer CLI-based authentication; avoid logging credentials or raw responses, and use API keys only when the CLI is unavailable.

## Reference(s):

- [ClawHub Google Sheets skill](https://clawhub.ai/byungkyu/skills/google-sheets)
- [Maton](https://maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Google Sheets API reference](https://developers.google.com/workspace/sheets/api/reference/rest)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Guidance]

**Output Format:** [Text and Markdown with command or code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include spreadsheet results and instructions for user-approved actions.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
