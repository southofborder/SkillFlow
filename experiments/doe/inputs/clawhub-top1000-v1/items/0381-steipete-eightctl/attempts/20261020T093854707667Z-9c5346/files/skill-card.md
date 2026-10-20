## Description:

Control Eight Sleep pods (status, temperature, alarms, schedules).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and external users use this skill to operate Eight Sleep pods through the eightctl CLI, including status checks, temperature changes, alarms, schedules, audio, and base position controls.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs eightctl from a mutable latest reference.

Mitigation: Use a pinned and reviewed eightctl version before deployment.

Risk: The CLI uses Eight Sleep account credentials and local configuration.

Mitigation: Protect the config file and EIGHTCTL_* environment variables.

Risk: Commands can change temperature, alarms, schedules, power state, audio, or base position.

Mitigation: Require explicit confirmation before executing state-changing commands.

Risk: The Eight Sleep API used by the CLI is unofficial and rate-limited.

Mitigation: Avoid repeated logins and excessive command retries.

## Reference(s):

- [Eightctl homepage](https://eightctl.sh)
- [ClawHub Eightctl skill page](https://clawhub.ai/steipete/skills/eightctl)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and configuration references]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the eightctl CLI and Eight Sleep authentication; commands that alter temperature, alarms, schedules, power, audio, or base position should require explicit confirmation.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
