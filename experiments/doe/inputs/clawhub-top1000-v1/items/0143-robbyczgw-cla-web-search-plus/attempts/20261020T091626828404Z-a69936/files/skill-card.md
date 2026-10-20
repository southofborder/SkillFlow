## Description:

Search the web across multiple providers and extract page text from URLs, returning ranked sources with freshness filters and research options.

This skill is ready for commercial/non-commercial use.

## Publisher:

[robbyczgw-cla](https://clawhub.ai/user/robbyczgw-cla)

### License/Terms of Use:

MIT

## Use Case:

Developers and other agent users search multiple web providers for ranked sources, extract page text, and compile source-grounded research.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries and extraction URLs are sent to external providers, including fallback providers.

Mitigation: Avoid sensitive queries and private URLs; choose a provider explicitly or use a self-hosted SearXNG instance for sensitive work.

Risk: Local caching can retain search queries and extracted page text.

Mitigation: Use --no-cache or WSP_DISABLE_CACHE=1 when needed, and clear stored answers after sensitive work.

Risk: Provider credentials may be stored in local configuration files.

Mitigation: Protect config.json and .env files containing API keys.

## Reference(s):

- [Web Search Plus on ClawHub](https://clawhub.ai/robbyczgw-cla/skills/web-search-plus)

## Skill Output:

**Output Type(s):** [Text, Markdown]

**Output Format:** [JSON search results and extracted page text]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Ranked source links and per-URL extraction results; no model-written answers.]

## Skill Version(s):

5.0.1 (source: ClawHub release, skill frontmatter, package.json, CHANGELOG)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
