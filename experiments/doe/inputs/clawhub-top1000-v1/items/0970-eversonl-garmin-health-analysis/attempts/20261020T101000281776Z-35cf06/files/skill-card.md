## Description:

Garmin Health Analysis lets agents query Garmin Connect health and activity data, interpret recovery and sleep trends, download FIT/GPX files, and generate JSON responses or HTML dashboards.

This skill is ready for commercial/non-commercial use.

## Publisher:

[eversonl](https://clawhub.ai/user/eversonl)

### License/Terms of Use:

MIT

## Use Case:

External users and developers use this skill to query Garmin Connect health, recovery, sleep, workout, and activity-file data, then generate JSON answers or HTML dashboards for personal analysis. Outputs should be treated as informational health guidance, not medical advice.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill handles Garmin credentials and local session token material.

Mitigation: Use an isolated virtual environment with pinned dependencies, avoid command-line password entry and plaintext config files where possible, and protect or delete ~/.clawdbot/garmin token material when revoking access.

Risk: Generated outputs can contain sensitive health metrics and GPS route data.

Mitigation: Choose private output directories for downloaded activity files and dashboards, and avoid sharing generated files unless the data has been reviewed.

Risk: Generated dashboards load Chart.js from a third-party CDN.

Mitigation: Avoid dashboard generation or replace the CDN dependency with an approved local copy when third-party network exposure is not acceptable.

Risk: Health trend interpretations may be mistaken for medical advice.

Mitigation: Keep responses informational, include the documented medical-advice disclaimer, and recommend consulting a clinician for health concerns.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/eversonl/skills/garmin-health-analysis)
- [Garmin Health Analysis setup guide](SKILL.md)
- [README](README.md)
- [Garmin Connect API Reference](references/api.md)
- [Health Analysis Guide](references/health_analysis.md)
- [Extended Capabilities](references/extended_capabilities.md)
- [MCP Setup Redirect](references/mcp_setup.md)
- [python-garminconnect library](https://github.com/cyberjunky/python-garminconnect)
- [Garmin Connect](https://connect.garmin.com)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance, JSON, files]

**Output Format:** [Markdown guidance with inline shell commands; helper scripts emit JSON, downloaded activity files, and generated HTML dashboards.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Garmin credentials and local Python dependencies; chart generation may load Chart.js from a third-party CDN.]

## Skill Version(s):

1.2.2 (source: evidence.json release and SKILL.md frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
