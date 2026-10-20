## Description:

Get current weather and forecasts (no API key required).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to look up current weather, compact weather summaries, and forecasts from public weather services without managing API credentials.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Requested locations or coordinates may be sent to public weather services.

Mitigation: Use only locations or coordinates you are comfortable sharing with wttr.in or Open-Meteo.

Risk: Weather results depend on public service availability and response accuracy.

Mitigation: Cross-check important forecasts with an authoritative weather source before relying on them for operational decisions.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/weather)
- [Publisher Profile](https://clawhub.ai/user/steipete)
- [wttr.in Help](https://wttr.in/:help)
- [Open-Meteo Forecast API](https://open-meteo.com/en/docs)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline bash code blocks and weather service URLs]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires curl; does not require API keys.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
