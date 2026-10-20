## Description:

Crypto Market Data Skill provides no-key-required cryptocurrency and stock market data access for real-time prices, company profiles, global analytics, discovery, and historical charts using Node.js with zero external dependencies.

This skill is ready for commercial/non-commercial use.

## Publisher:

[liam8](https://clawhub.ai/user/liam8)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to retrieve cryptocurrency and stock market prices, asset metadata, charts, market rankings, and global market statistics without configuring an API key.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill contacts api.igent.net for market data and can be redirected through API_BASE_URL.

Mitigation: Allow network egress only to trusted HTTPS endpoints and avoid setting API_BASE_URL unless the endpoint is trusted.

Risk: The client caches a temporary service token locally for reuse.

Mitigation: Restrict access to the skill workspace and token file, and clear cached tokens before sharing the environment.

## Reference(s):

- [ClawHub skill listing](https://clawhub.ai/liam8/skills/crypto-market-data)
- [Market data API base URL](https://api.igent.net/api)

## Skill Output:

**Output Type(s):** [JSON, Shell commands, Guidance]

**Output Format:** [JSON responses from Node.js command-line tools, with Markdown usage guidance in the skill documentation]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [No external npm dependencies; scripts fetch temporary service tokens and may cache a local .token file.]

## Skill Version(s):

1.0.2 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
