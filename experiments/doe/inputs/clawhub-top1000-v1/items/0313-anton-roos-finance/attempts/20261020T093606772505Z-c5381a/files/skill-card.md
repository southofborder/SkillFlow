## Description:

Track stocks, ETFs, indices, crypto where available, and FX pairs with caching and provider fallbacks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[anton-roos](https://clawhub.ai/user/anton-roos)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to fetch market quotes, generate stock or ETF series, maintain a local watchlist, and summarize finance data with provider caveats.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Third-party market providers may rate-limit requests, change behavior, or provide delayed data.

Mitigation: Use the skill's cache and throttling guidance, report provider caveats in summaries, and avoid claiming real-time data unless the provider supports it.

Risk: Dependency versions are ranges rather than locked versions.

Mitigation: Install in an isolated Python virtual environment and pin or lock dependencies before operational use.

Risk: Crypto coverage, provider fallbacks, and historical FX series are limited or may be inaccurate.

Mitigation: Treat these capabilities as best-effort, explain unsupported historical FX requests, and add a suitable paid provider before relying on high-frequency or historical FX workflows.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/anton-roos/skills/finance)
- [Publisher profile](https://clawhub.ai/user/anton-roos)
- [providers.md](providers.md)
- [ExchangeRate-API Open Access endpoint](https://open.er-api.com/v6/latest/<BASE>)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands; helper scripts emit JSON or CSV.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses local cache and watchlist files; quote freshness depends on upstream providers.]

## Skill Version(s):

1.1.2 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
