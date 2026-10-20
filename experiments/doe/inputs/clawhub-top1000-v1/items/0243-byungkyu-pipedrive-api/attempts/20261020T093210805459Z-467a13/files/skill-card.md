## Description:

Guides agents in using a Maton-connected Pipedrive account to manage deals, contacts, organizations, activities, and pipelines.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

Sales teams and developers use this skill to retrieve and, with approval, update Pipedrive CRM records through their connected account. It also describes optional Maton automations for approved workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: CRM writes or new connections can change records or expand account access.

Mitigation: Start with read-only calls and obtain explicit approval for each write or connection creation.

Risk: Deployed functions, triggers, or destinations can create ongoing actions or data flows.

Mitigation: Review the function, trigger, destination, and intended effects separately before enabling them.

Risk: Pipedrive contact data may be disclosed to an external destination.

Mitigation: Obtain explicit approval for the specific transfer and destination before forwarding contact data.

## Reference(s):

- [Pipedrive skill release](https://clawhub.ai/byungkyu/skills/pipedrive-api)
- [Maton](https://maton.ai)
- [Maton documentation](https://docs.maton.ai)
- [Pipedrive API documentation](https://developers.pipedrive.com/docs/api/v1)

## Skill Output:

**Output Type(s):** [Text, Shell commands, Code, Guidance]

**Output Format:** [Markdown with command, code, and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Actions require a connected account and its authorized access; writes and automation require user approval.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
