## Description:

Connects agents to CellCog for research and the creation of multimedia, documents, dashboards, and code through a Python SDK or MCP connector.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cellcog](https://clawhub.ai/user/cellcog)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other agents use this skill to delegate research, analysis, and creation of documents, media, and code to CellCog, then retrieve responses and generated files.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Files referenced for analysis are uploaded to an external service.

Mitigation: Share only intended files; exclude secrets, credentials, and private directories.

Risk: Connected SaaS tools and real browser profiles can expose accounts and data.

Mitigation: Select only task-specific tools and use browser profiles only when necessary.

Risk: Broad or long-running tasks can continue without clear boundaries and write generated files locally.

Mitigation: Set narrow task instructions, monitor ongoing work, and specify task-specific output folders.

## Reference(s):

- [CellCog skill on ClawHub](https://clawhub.ai/cellcog/skills/cellcog)
- [CellCog website](https://cellcog.ai)
- [CellCog MCP connector](https://cellcog.ai/mcp)
- [CellCog Python SDK package](https://pypi.org/project/cellcog/)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Files, Guidance]

**Output Format:** [Text or Markdown responses with code examples and file paths; generated files in requested formats]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Tasks may complete asynchronously; generated files can be saved to specified output folders.]

## Skill Version(s):

2.0.24 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
