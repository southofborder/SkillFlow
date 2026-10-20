## Description:

Safe Notion API access for pages, databases, and blocks: schema diffs before structural changes, append-first writes, and personal/work profile switching.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dimagious](https://clawhub.ai/user/dimagious)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, operators, and external users use this skill to search, read, create, and update Notion pages, databases, and blocks through the official API. It emphasizes safer workflows for shared workspaces, including resolving IDs before acting, appending instead of replacing content, and reviewing schema diffs before structural changes.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The profile-selection snippet can read an unintended local key file and send that value to Notion as an API token.

Mitigation: Review or patch the profile-selection snippet before installing; prefer NOTION_API_KEY directly or restrict NOTION_PROFILE to known names such as personal and work.

Risk: A Notion integration token can access every page or database shared with that integration.

Mitigation: Store tokens in a secret manager where possible and share the integration only with the pages and databases needed for the task.

Risk: Schema changes and content replacement can cause data loss in a Notion workspace.

Mitigation: Use the skill's append-first behavior, fetch current schemas, present diffs, and require explicit confirmation before destructive writes or structural changes.

## Reference(s):

- [Notion Developers](https://developers.notion.com)
- [Notion integrations setup](https://www.notion.so/my-integrations)
- [ClawHub Notion skill page](https://clawhub.ai/dimagious/skills/notion-skill)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline bash and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires a Notion integration token via NOTION_API_KEY or a profile key file; uses curl and jq with no Notion CLI.]

## Skill Version(s):

2.0.0 (source: release evidence and README.md)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
