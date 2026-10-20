## Description:

Browse and summarize websites, extract content from URLs, and search the web for information.

This skill is ready for commercial/non-commercial use.

## Publisher:

[tankebuaa](https://clawhub.ai/user/tankebuaa)

### License/Terms of Use:

MIT-0

## Use Case:

External users, developers, and agents use this skill to search the web, fetch provided URLs, extract page content, and summarize current or page-specific information.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can fetch arbitrary URLs from the agent's network, including private or internal addresses.

Mitigation: Use only with trusted URLs and enforce outbound network controls, private-network blocking, URL validation, and redirect revalidation.

Risk: Search terms and provided URLs may be sent to external services.

Mitigation: Do not use secrets, private URLs, credentials in query strings, or sensitive personal data; add a clear privacy disclosure before broad deployment.

Risk: Remote pages may create excessive download or processing exposure.

Mitigation: Apply request timeouts and explicit download or response-size limits before treating the skill as low-risk.

## Reference(s):

- [Web Browsing Usage Guide](references/usage-guide.md)
- [ClawHub Skill Page](https://clawhub.ai/tankebuaa/skills/web-browsing)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, guidance]

**Output Format:** [Markdown or JSON-like structured results containing URLs, titles, snippets, summaries, and code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Fetched page content is truncated to the first 5000 characters by the bundled script.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
