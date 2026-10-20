## Description:

Control Home Assistant smart home devices, run automations, and receive webhook events.

This skill is ready for commercial/non-commercial use.

## Publisher:

[iahmadzain](https://clawhub.ai/user/iahmadzain)

### License/Terms of Use:


## Use Case:

Developers and smart-home operators use this skill to inspect Home Assistant entity state, control devices, activate scenes and scripts, trigger automations, and receive webhook-driven events.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can issue broad smart-home control actions and uses long-lived Home Assistant credentials.

Mitigation: Use a dedicated least-privilege Home Assistant account or token, prefer HTTPS or wss endpoints, and restrict local config file permissions.

Risk: Commands may affect sensitive devices such as locks, alarms, garage doors, covers, climate systems, scripts, or automations.

Mitigation: Require explicit confirmation before executing services that affect safety, security, access, or unattended automation.

Risk: Webhook payloads may expose sensitive room, occupancy, or household activity data.

Mitigation: Avoid sending sensitive room or occupancy data to external webhooks and keep webhook authorization secrets scoped and protected.

## Reference(s):

- [Home Assistant REST API Reference](references/api.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and JSON/YAML configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires curl and jq; uses a Home Assistant URL and long-lived access token supplied by config file or environment variables.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
