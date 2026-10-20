## Description:

Real-time search engine supporting web search, vertical domain search, parallel batch search, and URL content extraction.

This skill is ready for commercial/non-commercial use.

## Publisher:

[anysearch-ai](https://clawhub.ai/user/anysearch-ai)

### License/Terms of Use:

Apache 2.0

## Use Case:

Developers and agents use AnySearch to retrieve current web information, fact-check claims, run vertical-domain searches, batch multiple searches, and extract supported URL content.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The security evidence reports that clients can be redirected to send API keys and queries to an unexpected endpoint.

Mitigation: Review before installing, ensure ANYSEARCH_API_BASE_URL is unset, and confirm no skill-local .env file can override the expected endpoint before authenticated searches.

Risk: Search queries, extracted URLs, and API keys may be sent to the AnySearch service.

Mitigation: Use anonymous mode or a low-privilege AnySearch key, prefer environment-variable or protected secret storage, avoid --api_key for keys, and do not use the skill with sensitive queries.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/anysearch-ai/skills/anysearch)
- [Publisher Profile](https://clawhub.ai/user/anysearch-ai)
- [README](artifact/README.md)
- [Security Policy](artifact/SECURITY.md)
- [AnySearch API](https://api.anysearch.com)
- [AnySearch API Keys](https://anysearch.com/console/api-keys)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown and command-line guidance with search or extraction results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Extracted HTML and plain-text content may be truncated at 50,000 characters; unsupported binary formats return errors.]

## Skill Version(s):

3.1.1 (source: frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
