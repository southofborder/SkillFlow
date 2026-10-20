## Description:

Helps agents retrieve and compare Chinese market data and investment research across stocks, funds, indices, financial statements, announcements, reports, and macroeconomic indicators.

This skill is ready for commercial/non-commercial use.

## Publisher:

[kenneth-bro](https://clawhub.ai/user/kenneth-bro)

### License/Terms of Use:

MIT-0

## Use Case:

Investors, analysts, and developers use this skill to retrieve, export, and compare Chinese financial-market data for research. It does not place trades or provide direct buy-or-sell recommendations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Investment documentation may be misleading or lack sufficient context for high-stakes decisions.

Mitigation: Treat outputs as research data, not trading advice; independently verify analyses, forecasts, timing signals, and endpoint semantics.

Risk: Using the skill requires an external CLI/API package, provider network access, and local API-key configuration.

Mitigation: Review the package and its configuration before installation, protect the API key, and confirm network access to the provider is acceptable.

## Reference(s):

- [InvestToday Finance Data release](https://clawhub.ai/kenneth-bro/skills/investoday-finance-data)
- [English endpoint reference index](docs/references-index.en.md)
- [Chinese endpoint reference index](docs/references-index.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Markdown with data summaries and optional CLI commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May summarize or compare retrieved data; coverage and availability depend on provider access.]

## Skill Version(s):

1.8.97 (source: release metadata and skill frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
