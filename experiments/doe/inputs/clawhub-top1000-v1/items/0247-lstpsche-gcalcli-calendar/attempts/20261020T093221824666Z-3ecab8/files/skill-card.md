## Description:

Google Calendar via gcalcli: today-only agenda by default, bounded meaning-first lookup via agenda scans, and fast create/delete with verification--optimized for low tool calls and minimal output.

This skill is ready for commercial/non-commercial use.

## Publisher:

[lstpsche](https://clawhub.ai/user/lstpsche)

### License/Terms of Use:

MIT

## Use Case:

External users and personal-assistant agents use this skill to read, search, create, and delete Google Calendar events through a locally authenticated gcalcli setup. It is optimized for concise calendar management with bounded lookup windows, overlap checks, disambiguation for uncertain matches, and post-delete verification.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can delete or edit Google Calendar events without a second confirmation when a match is considered unambiguous.

Mitigation: Require confirmation before every destructive action, or limit use to trusted personal calendars where the user accepts the faster action policy.

Risk: Calendar titles, calendar names, and queries may be interpolated into shell command templates.

Mitigation: Pass gcalcli arguments as structured argv where possible and avoid using untrusted calendar text in raw shell command strings.

Risk: ICS content for imports can be malformed or unsafe if event fields are not escaped correctly.

Mitigation: Escape ICS fields before import and review recurrence or transparency changes before execution.

Risk: The skill uses the local gcalcli OAuth profile to read and modify calendars.

Mitigation: Install only on machines with an intended gcalcli profile and Google Calendar account scope.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/lstpsche/skills/gcalcli-calendar)
- [gcalcli project](https://github.com/insanum/gcalcli)
- [Google Calendar API endpoint](https://www.googleapis.com/calendar/)
- [Google OAuth2 endpoint](https://oauth2.googleapis.com/)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Concise natural-language responses with optional markdown and gcalcli shell commands when requested.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The skill relies on a local gcalcli installation and OAuth profile; event creation, deletion, and lookup behavior is constrained by the user's configured Google Calendar access.]

## Skill Version(s):

3.0.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
