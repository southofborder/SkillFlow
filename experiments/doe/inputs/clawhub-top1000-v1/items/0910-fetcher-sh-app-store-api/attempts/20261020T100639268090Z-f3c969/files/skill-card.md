## Description:

Provides agent-ready guidance for using fetcher.sh's paid Apple App Store API to search apps and bundles, retrieve details, reviews, similar items, and developer catalogs across country storefronts.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fetcher-sh](https://clawhub.ai/user/fetcher-sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to integrate paid Apple App Store data retrieval through HTTP GET endpoints or MCP, without Apple Developer Program access. It supports app discovery, ASO research, competitor monitoring, localized storefront comparison, reviews analysis, and developer catalog lookup.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Repeated or automated use may spend funds through x402 payments or prepaid credits.

Mitigation: Confirm intent before repeated calls, monitor credit balance, and treat FETCHER_API_KEY as a payment credential.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/fetcher-sh/skills/app-store-api)
- [Server-resolved GitHub provenance](https://github.com/fetcher-sh/fetcher-skills/tree/main/skills/app-store)
- [Full agent setup](https://appstore.fetcher.sh/skill.md)
- [OpenAPI 3.1 contract](https://appstore.fetcher.sh/openapi.json)
- [Condensed catalog](https://appstore.fetcher.sh/llms.txt)
- [API site](https://appstore.fetcher.sh)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with curl examples, endpoint descriptions, and MCP JSON configuration]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include paid API calls that require prepaid credits or x402 payment handling.]

## Skill Version(s):

0.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
