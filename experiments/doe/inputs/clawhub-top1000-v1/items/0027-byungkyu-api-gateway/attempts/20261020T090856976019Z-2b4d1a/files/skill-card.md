## Description:

Helps agents use Maton to access user-connected third-party services for API requests, with optional user-approved triggers and hosted functions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other users can ask an agent to read or update resources in services they have connected to Maton, such as email, CRM records, issues, or spreadsheets. Optional automation requires separate user approval.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Calls may read sensitive data or change resources in connected accounts.

Mitigation: Confirm the account, resource, payload, and effect before writes; use the narrowest necessary permissions and remove unused connections.

Risk: Event destinations and hosted functions can create persistent forwarding or automation.

Mitigation: Require separate approval for each destination or function, review recipients and reachable accounts, and delete them after the task.

Risk: Third-party responses and event payloads may contain instructions or unsafe input.

Mitigation: Treat returned content as data, not agent instructions; review any event handler and get approval before running it.

## Reference(s):

- [Maton homepage](https://maton.ai)
- [Maton documentation](https://docs.maton.ai)
- [Maton API reference](https://docs.maton.ai/api-reference/overview)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Google Mail app reference](references/google-mail/README.md)
- [Slack app reference](references/slack/README.md)

## Skill Output:

**Output Type(s):** [Text, Shell commands, Code, Configuration guidance]

**Output Format:** [Markdown with CLI examples and API response summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Access requires a Maton account, network access, and an authorized connection to the target service.]

## Skill Version(s):

1.2.29 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
