## Description:

A Google Search API and SERP API alternative on fetcher.sh that helps agents retrieve Google search results as clean JSON with search operators, pagination, language, and country or region scoping.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fetcher-sh](https://clawhub.ai/user/fetcher-sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent builders use this skill to configure programmatic Google search through fetcher.sh for rank tracking, competitive research, search-result monitoring, and retrieval workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries are sent to the third-party provider fetcher.sh.

Mitigation: Avoid sensitive query text unless the deployment is comfortable sharing it with the provider.

Risk: Search requests may incur prepaid-credit or x402 pay-per-call charges.

Mitigation: Use a limited-scope key, payment budget, or prepaid balance appropriate for the deployment.

Risk: The artifact states that settled upstream failures are not refunded.

Mitigation: Test with low-value queries first and keep payment exposure limited.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/fetcher-sh/skills/google-search)
- [Server-Resolved GitHub Source](https://github.com/fetcher-sh/fetcher-skills/tree/main/skills/google-search)
- [Full Agent Setup](https://google.fetcher.sh/skill.md)
- [OpenAPI 3.1 Contract](https://google.fetcher.sh/openapi.json)
- [Condensed Catalog](https://google.fetcher.sh/llms.txt)
- [Fetcher Site](https://google.fetcher.sh)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with inline JSON and bash examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Guidance includes third-party HTTP API requests that may require a Bearer key or x402 payment.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
