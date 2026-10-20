## Description:

Interact with Google Calendar via the Google Calendar API – list upcoming events, create new events, update or delete them.

This skill is ready for commercial/non-commercial use.

## Publisher:

[adrianmiller99](https://clawhub.ai/user/adrianmiller99)

### License/Terms of Use:


## Use Case:

Developers and OpenClaw users use this skill to inspect upcoming Google Calendar events and manage calendar entries from an agent workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: OAuth credentials and access tokens may be handled or stored insecurely, including plaintext token storage by the refresh-token helper.

Mitigation: Use the minimum Google Calendar OAuth scope needed and store credentials in OpenClaw secrets or an operating-system credential store instead of plaintext files.

Risk: Calendar add, update, and delete commands can change live calendar data immediately.

Mitigation: Review command arguments before execution and prefer read-only use unless the intended calendar mutation is clear.

## Reference(s):

- [Google Calendar API reference](https://developers.google.com/calendar/api/v3/reference)
- [OAuth 2.0 for installed apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [ClawHub skill page](https://clawhub.ai/adrianmiller99/skills/google-calendar)

## Skill Output:

**Output Type(s):** [JSON, API Calls, Shell commands, Configuration instructions]

**Output Format:** [JSON responses from command-line operations, with setup guidance in Markdown and shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Commands can read, create, update, and delete live calendar data when valid Google Calendar credentials are configured.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
