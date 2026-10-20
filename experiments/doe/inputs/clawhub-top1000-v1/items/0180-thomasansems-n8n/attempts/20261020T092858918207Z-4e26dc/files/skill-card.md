## Description:

Manage n8n workflows and automations via API, including listing workflows, activating or deactivating them, checking execution status, manually triggering workflows, and debugging automation issues.

This skill is ready for commercial/non-commercial use.

## Publisher:

[thomasansems](https://clawhub.ai/user/thomasansems)

### License/Terms of Use:


## Use Case:

Developers and automation engineers use this skill to create, validate, execute, monitor, debug, and optimize n8n workflows through the n8n REST API.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Dry-run, test-suite, and manual execution paths can trigger real workflows and affect connected systems.

Mitigation: Use a test or staging n8n instance first and treat these commands as live workflow execution.

Risk: High-impact n8n actions can create, activate, deactivate, delete, or execute workflows through an API key.

Mitigation: Set N8N_BASE_URL to a trusted HTTPS n8n host and use a least-privilege API key.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/thomasansems/skills/n8n)
- [n8n API Reference](references/api.md)
- [n8n Docs](https://docs.n8n.io)
- [n8n API Docs](https://docs.n8n.io/api/)
- [n8n Community Forum](https://community.n8n.io)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell commands, Python examples, JSON API responses, validation reports, and optimization reports]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires N8N_API_KEY and N8N_BASE_URL for live n8n API operations.]

## Skill Version(s):

2.0.0 (source: server release metadata and user-provided changelog, released 2026-02-10)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
