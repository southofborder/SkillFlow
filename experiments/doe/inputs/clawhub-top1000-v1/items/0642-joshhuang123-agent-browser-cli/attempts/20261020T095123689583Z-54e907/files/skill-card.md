## Description:

Agent Browser CLI helps agents use the agent-browser CLI for browser automation tasks such as check-ins, form filling, screenshots, and webpage content collection.

This skill is ready for commercial/non-commercial use.

## Publisher:

[joshhuang123](https://clawhub.ai/user/joshhuang123)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to drive browser sessions through agent-browser commands for navigation, element interaction, screenshots, and lightweight web research workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Browser automation can submit forms, click account-changing controls, or use existing browser sessions in ways that affect real accounts.

Mitigation: Run the skill in a limited environment, avoid sensitive browser profiles and stored sessions, and confirm every submission or account-changing click.

Risk: The artifact recommends installing a mutable global CLI with npm.

Mitigation: Prefer a pinned or isolated local installation of agent-browser instead of a global latest-version install.

Risk: Automated scripts may handle credentials or private form data.

Mitigation: Do not paste real passwords into scripts and review commands before execution.

## Reference(s):


## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include command examples for browser navigation, interaction, data extraction, screenshots, cron-based check-ins, and local installation.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
