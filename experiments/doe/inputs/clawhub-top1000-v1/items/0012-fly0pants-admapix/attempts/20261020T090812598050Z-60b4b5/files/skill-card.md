## Description:

AdMapix is a data-layer skill that turns English or Chinese ad and app intelligence requests into AdMapix read API calls and returns raw structured JSON for ad creatives, apps, rankings, download and revenue estimates, distribution, and market metadata.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fly0pants](https://clawhub.ai/user/fly0pants)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to retrieve raw AdMapix API data for ad creative search, app intelligence, rankings, download and revenue estimates, distribution, and market analysis. The calling agent is responsible for composing multi-step workflows and any analysis or presentation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The documented install command uses an unpinned npx package path that can execute mutable remote installer code.

Mitigation: Use a pinned, trusted ClawHub or OpenClaw installer version, or another integrity-checked install flow, before deployment.

Risk: The skill requires an AdMapix API key for third-party API calls.

Mitigation: Store ADMAPIX_API_KEY in the host secret store and keep it out of chat, logs, screenshots, generated output, and URLs.

Risk: Download and revenue outputs are third-party estimates rather than official app-store figures.

Mitigation: Preserve the estimate status when presenting results and avoid treating these values as audited official metrics.

## Reference(s):

- [AdMapix Skill Instructions](artifact/SKILL.md)
- [AdMapix README](artifact/README.md)
- [Creative Search API](artifact/references/api-creative.md)
- [Product & Company API](artifact/references/api-product.md)
- [Ranking API](artifact/references/api-ranking.md)
- [Download & Revenue API](artifact/references/api-download-revenue.md)
- [App Distribution API](artifact/references/api-distribution.md)
- [Market Analysis API](artifact/references/api-market.md)
- [Parameter Mapping Reference](artifact/references/param-mappings.md)
- [AdMapix Website](https://www.admapix.com)
- [AdMapix API](https://api.admapix.com)
- [ClawHub Skill Page](https://clawhub.ai/fly0pants/skills/admapix)

## Skill Output:

**Output Type(s):** [json, shell commands, configuration, guidance]

**Output Format:** [Raw structured JSON, with short setup or error guidance when credentials are missing or invalid.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Passes through API field names and values without renaming, summarizing, ranking, or hiding records; download and revenue values are third-party estimates.]

## Skill Version(s):

1.0.30 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
