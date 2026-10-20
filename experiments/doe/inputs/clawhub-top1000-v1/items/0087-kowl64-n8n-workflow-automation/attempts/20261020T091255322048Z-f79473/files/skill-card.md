## Description:

Designs and outputs n8n workflow JSON with robust triggers, idempotency, error handling, logging, retries, and human-in-the-loop review queues.

This skill is ready for commercial/non-commercial use.

## Publisher:

[kowl64](https://clawhub.ai/user/kowl64)

### License/Terms of Use:


## Use Case:

Developers and operations teams use this skill to design auditable n8n automations for cron, webhook, or manual workflows with explicit data contracts, retry behavior, logging, and review queues.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Generated workflow JSON may contain incorrect nodes, unsafe write targets, excessive API scopes, or retry behavior that causes duplicate records if imported without review.

Mitigation: Review n8n nodes, credential references, API scopes, write targets, schedules, deduplication keys, and retry behavior before importing or activating the workflow.

Risk: Secrets could be exposed if users paste credentials into generated workflow files.

Mitigation: Use credential names or environment variable references only; do not place secrets in workflow JSON or runbooks.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/kowl64/skills/n8n-workflow-automation)
- [Runbook template](artifact/assets/runbook-template.md)

## Skill Output:

**Output Type(s):** [guidance, markdown, code, configuration]

**Output Format:** [Markdown design specs and optional n8n workflow JSON plus runbook Markdown]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Workflow JSON is inactive by default and should reference credential names or environment variables, not secrets.]

## Skill Version(s):

1.0.0 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
