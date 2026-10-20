## Description:

Connects an agent to Google Meet through Maton to manage meeting spaces and retrieve conference and participant information.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams use this skill to create or manage Google Meet spaces and review conference records, participants, recordings, and transcripts through an authorized account. Optional hosted functions and triggers support explicitly approved automations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Google Meet access may expose meeting and participant information beyond what the task requires.

Mitigation: Review OAuth scopes, connect only the needed account, and limit shared results to the requested fields.

Risk: Writes and hosted functions can change meeting resources or run actions without a new interactive request.

Mitigation: Obtain separate user approval for connections, writes, function deployments, and invocations; restrict each function to the needed connections.

Risk: Triggers and destinations can forward future event data continuously, including to external hosts.

Mitigation: Approve each trigger and destination separately, disclose what data flows and how often, and avoid third-party forwarding unless the user trusts the named host.

Risk: Long-lived API keys can increase credential exposure.

Mitigation: Prefer Maton OAuth and avoid exposing credentials in commands, logs, or output.

## Reference(s):

- [Google Meet API reference](https://developers.google.com/meet/api/reference/rest)
- [Maton documentation](https://docs.maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Maton homepage](https://maton.ai)
- [Google Meet skill release](https://clawhub.ai/byungkyu/skills/google-meet)
- [Time trigger reference](references/time/triggers.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Guidance]

**Output Format:** [Markdown with CLI commands and API examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Responses may contain personal meeting and participant information; share only fields needed for the task.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
