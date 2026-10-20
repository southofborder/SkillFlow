## Description:

Query the DeepWiki MCP server for GitHub repository documentation, wiki structure, and AI-powered questions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[arun-8687](https://clawhub.ai/user/arun-8687)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to query DeepWiki for public GitHub repository documentation, wiki structure, and topic-specific answers.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Repository names, questions, and requested wiki paths are sent to the DeepWiki service.

Mitigation: Use this skill only for public repository lookups and avoid entering private repository details, credentials, or sensitive internal information.

## Reference(s):

- [DeepWiki MCP documentation](https://docs.devin.ai/work-with-devin/deepwiki-mcp)
- [DeepWiki MCP server](https://mcp.deepwiki.com/mcp)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Markdown or plain text returned from DeepWiki, with shell commands used to invoke repository documentation queries.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Queries are scoped to public GitHub repositories and do not require authentication.]

## Skill Version(s):

1.0.0 (source: server release evidence, released 2026-01-11)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
