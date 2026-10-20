## Description:

Check Google Calendar calendars, find free time, schedule meetings, and update events via the Google Calendar API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hith3sh](https://clawhub.ai/user/hith3sh)

### License/Terms of Use:

MIT-0

## Use Case:

OpenClaw users use this skill to inspect Google Calendar availability, search and review events, find free meeting slots, and create or update calendar events after confirmation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs and allowlists an unpinned third-party plugin that handles OAuth-backed calendar access.

Mitigation: Review the ClawLink plugin source, publisher, version, and verification status before installing, and revoke the OAuth connection or remove the plugin when it is no longer needed.

Risk: Calendar writes, deletions, moves, and sharing changes can affect events, attendees, or calendar access.

Mitigation: Use the smallest practical Google Calendar permission scope and confirm every calendar write, destructive action, or sharing change before execution.

Risk: Event creation does not perform conflict checking by default.

Mitigation: Check availability with free/busy or free-slot tools before creating meetings where conflicts matter.

## Reference(s):

- [Google Calendar API Overview](https://developers.google.com/workspace/calendar/api/guides/overview)
- [Google Calendar API Reference](https://developers.google.com/workspace/calendar/api/reference/rest)
- [Google Calendar Event Resource](https://developers.google.com/workspace/calendar/api/reference/rest/v3/events)
- [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=google-calendar-scheduling)
- [ClawLink OpenClaw Docs](https://docs.claw-link.dev/openclaw)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and JSON tool-call examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes Google Calendar API tool names, OAuth setup steps, and confirmation guidance for write operations.]

## Skill Version(s):

1.0.9 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
