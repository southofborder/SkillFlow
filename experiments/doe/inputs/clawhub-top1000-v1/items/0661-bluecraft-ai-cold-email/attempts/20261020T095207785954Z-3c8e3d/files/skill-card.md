## Description:

Build cold email campaigns and generate hyper-personalized email sequences with MachFive from lead data.

This skill is ready for commercial/non-commercial use.

## Publisher:

[bluecraft-ai](https://clawhub.ai/user/bluecraft-ai)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to set up MachFive cold-email campaigns, gather required generation settings, preview output, and generate single-lead or batch email sequences.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Lead data and sender signatures are shared with MachFive for outbound email generation.

Mitigation: Confirm the intended use and data-sharing posture before installation or execution, and only provide lead data and signatures approved for use with MachFive.

Risk: Preview, generation, enrichment, and batch workflows can consume MachFive credits.

Mitigation: Confirm credit costs before approving preview or generation, and review enrichment and batch settings before submitting jobs.

Risk: Asynchronous generation or campaign-build jobs can be left incomplete or reported from stale status.

Mitigation: Use the documented polling loop or notification email, and make a fresh status request before reporting completion.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/bluecraft-ai/skills/cold-email)
- [Publisher profile](https://clawhub.ai/user/bluecraft-ai)
- [MachFive API settings](https://app.machfive.io/settings)
- [MachFive app and API base URL](https://app.machfive.io)
- [MachFive website](https://machfive.io)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, API calls, guidance]

**Output Format:** [Markdown guidance with shell commands, JSON request bodies, and generated email text.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires MACHFIVE_API_KEY and uses MachFive API calls for campaign setup, previews, generation, polling, and export.]

## Skill Version(s):

1.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
