## Description:

Google Maps API helps agents use fetcher.sh's Google Maps and Places API alternative to search places, fetch place details, retrieve reviews, and configure prepaid or x402 payment.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fetcher-sh](https://clawhub.ai/user/fetcher-sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent builders use this skill to guide agents through local business discovery, point-of-interest lookup, store-locator inputs, and review monitoring through fetcher.sh's Google Maps-style API.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries, location coordinates, and API use are sent to fetcher.sh.

Mitigation: Confirm the publisher and service are trusted for the intended data before installing or using the skill.

Risk: Calls use a paid service with disclosed per-call pricing and no-refund behavior on upstream failures.

Mitigation: Review the $0.005-per-call cost model and payment method before enabling automated calls.

Risk: FETCHER_API_KEY is a paid service credential.

Mitigation: Store the key securely, avoid committing it to source control, and rotate it if exposed.

## Reference(s):

- [Server-resolved GitHub provenance](https://github.com/fetcher-sh/fetcher-skills/tree/main/skills/google-maps)
- [ClawHub skill page](https://clawhub.ai/fetcher-sh/skills/google-maps-api)
- [Full agent setup](https://google-maps.fetcher.sh/skill.md)
- [OpenAPI 3.1 contract](https://google-maps.fetcher.sh/openapi.json)
- [Condensed catalog](https://google-maps.fetcher.sh/llms.txt)
- [Site](https://google-maps.fetcher.sh)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, code]

**Output Format:** [Markdown with inline bash and JSON code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes endpoint guidance, authentication examples, MCP configuration, and error-handling notes.]

## Skill Version(s):

0.1.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
