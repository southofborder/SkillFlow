## Description:

Context7 MCP provides intelligent documentation search and context retrieval for libraries.

This skill is ready for commercial/non-commercial use.

## Publisher:

[thesethrose](https://clawhub.ai/user/thesethrose)

### License/Terms of Use:

MIT

## Use Case:

Developers and agents use Context7 MCP to search library documentation, retrieve LLM-reranked context snippets, and select version-aware documentation for implementation tasks.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill uses a Context7 API key and sends library names and search queries to Context7.

Mitigation: Keep CONTEXT7_API_KEY scoped to this service and avoid sending sensitive library names, repository identifiers, or query text.

Risk: Dependency hygiene issues may affect install consistency or maintenance.

Mitigation: Prefer deterministic installs from the included package-lock.json and review or remove unused dependencies before deployment.

Risk: Returned documentation context can be incomplete, stale, or mismatched to the intended library version.

Mitigation: Use specific library IDs and versioned identifiers where available, and verify important implementation guidance against the cited source URLs.

## Reference(s):

- [Context7 Documentation](https://context7.com/docs)
- [Context7 API Search Endpoint](https://context7.com/api/v2/libs/search)
- [Context7 API Context Endpoint](https://context7.com/api/v2/context)
- [Context7 llms.txt](https://context7.com/docs/llms.txt)
- [Context7 Dashboard](https://context7.com/dashboard)
- [ClawHub Skill Page](https://clawhub.ai/thesethrose/skills/context7)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown and terminal text from CLI commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Node.js, npm dependencies, network access to Context7, and a CONTEXT7_API_KEY.]

## Skill Version(s):

1.0.3 (source: skill metadata, server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
