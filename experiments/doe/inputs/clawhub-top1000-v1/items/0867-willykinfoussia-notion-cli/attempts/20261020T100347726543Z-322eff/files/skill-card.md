## Description:

Notion CLI for creating and managing pages, databases, and blocks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[willykinfoussia](https://clawhub.ai/user/willykinfoussia)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to operate Notion workspaces through notion-cli and the Notion API, including searching, reading, creating, updating, and querying pages, databases, and blocks.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill asks users to install an unpinned global npm package.

Mitigation: Pin and verify the npm package version where possible, and consider installing it in an isolated environment instead of globally.

Risk: The skill uses a Notion token and suggests storing it in a plaintext file.

Mitigation: Store NOTION_TOKEN in a secure credential store or a file with restrictive permissions such as chmod 600.

Risk: The skill can modify live Notion pages and databases.

Mitigation: Use a minimally scoped Notion integration and share only the specific pages or databases needed.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/willykinfoussia/skills/notion-cli)
- [GitHub Notion CLI](https://github.com/litencatt/notion-cli)
- [Notion API documentation](https://developers.notion.com)
- [Notion integrations](https://notion.so/my-integrations)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands, JSON request examples, and Notion API guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires a NOTION_TOKEN environment variable and access to Notion pages or databases shared with the integration.]

## Skill Version(s):

0.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
