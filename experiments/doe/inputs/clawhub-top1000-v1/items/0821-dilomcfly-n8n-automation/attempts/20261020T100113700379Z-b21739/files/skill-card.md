## Description:

Manage n8n workflows from OpenClaw via the n8n REST API for listing, creating, triggering, activating, deactivating, and debugging automations on n8n Cloud or self-hosted instances.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dilomcfly](https://clawhub.ai/user/dilomcfly)

### License/Terms of Use:


## Use Case:

Developers and automation operators use this skill to administer n8n workflows and executions through REST API calls, including health checks, failed-execution debugging, webhook triggering, and workflow lifecycle actions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can trigger live production webhooks and perform administrative workflow actions.

Mitigation: Prefer test webhooks before production and require explicit confirmation plus backups before delete, deactivate, transfer, or credential-related actions.

Risk: An n8n API key may grant broad access to workflows, executions, credentials, tags, and users.

Mitigation: Use a least-privilege API key where possible and scope agent use to the intended n8n instance and workflows.

## Reference(s):

- [n8n REST API Endpoint Reference](references/api-endpoints.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline bash, curl, and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include API endpoint paths, JSON payload snippets, environment variable setup, and operational guidance.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
