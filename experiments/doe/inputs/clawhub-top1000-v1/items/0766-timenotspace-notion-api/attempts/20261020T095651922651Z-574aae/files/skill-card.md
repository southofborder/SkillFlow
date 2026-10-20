## Description:

Generic Notion API CLI (Node) for search, querying data sources (databases), and creating pages.

This skill is ready for commercial/non-commercial use.

## Publisher:

[timenotspace](https://clawhub.ai/user/timenotspace)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to search Notion, query Notion data sources, create pages, and inspect or edit blocks through a small Node CLI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: A Notion integration token may allow the agent to read or modify pages and databases shared with that integration.

Mitigation: Use a limited Notion integration, share only the required pages or databases, and prefer a test workspace for evaluation.

Risk: Block append and update commands can mutate Notion content immediately.

Mitigation: Review requested mutations before execution and confirm target block IDs and JSON bodies before running write commands.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/timenotspace/skills/notion-api)
- [Publisher profile](https://clawhub.ai/user/timenotspace)
- [Notion search API endpoint](https://api.notion.com/v1/search)
- [Notion pages API endpoint](https://api.notion.com/v1/pages)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell commands and JSON command output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Commands print JSON to stdout and require a Notion integration token via NOTION_KEY or a local key file.]

## Skill Version(s):

1.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
