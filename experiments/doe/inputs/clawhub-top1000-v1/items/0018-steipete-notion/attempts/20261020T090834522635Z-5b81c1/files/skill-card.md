## Description:

Notion API for creating and managing pages, databases, and blocks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and workspace operators use this skill to guide Notion API requests for creating, reading, querying, and updating pages, data sources, and blocks.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: A Notion API key may grant access to workspace content if exposed.

Mitigation: Store the token with owner-only permissions, avoid logging or screenshotting it, and grant the integration access only to required pages or data sources.

Risk: POST and PATCH examples can create or modify live Notion content.

Mitigation: Run write examples only when intentional and test them on non-production pages before using them on important workspace content.

## Reference(s):

- [Notion API Documentation](https://developers.notion.com)
- [Notion Integration Setup](https://notion.so/my-integrations)
- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/notion)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, API calls]

**Output Format:** [Markdown with inline bash and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses Notion API examples that may create or modify live workspace content when executed.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
