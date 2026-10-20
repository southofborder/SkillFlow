## Description:

Decomposes complex user requests into executable subtasks, identifies required capabilities, searches for existing skills at skills.sh, and creates new skills when no solution exists.

This skill is ready for commercial/non-commercial use.

## Publisher:

[10e9928a](https://clawhub.ai/user/10e9928a)

### License/Terms of Use:

MIT

## Use Case:

Developers, automation builders, and agent operators use this skill to break complex multi-step requests into atomic subtasks, map each subtask to required capabilities, search for matching skills, and plan new skill creation when gaps remain.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The security summary reports that the skill repeatedly encourages unpinned, auto-confirmed global installation of third-party skills, which can change the user's agent environment beyond the immediate task.

Mitigation: Review the skill source before installation, replace auto-confirmed global installs with pinned immutable revisions and local or sandboxed installs, and require explicit approval before installing third-party skills.

Risk: Generated workflows may request credentials for Slack, email, Notion, GitHub, or other services before the target skill and its permissions have been reviewed.

Mitigation: Do not expose credentials to generated workflows until each target skill, permission scope, and execution environment has been reviewed.

Risk: Generated skills and execution plans may introduce incorrect guidance or unsafe automation steps.

Mitigation: Require user review before generated skill creation, scan generated skill artifacts, and verify each execution step before deployment.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/10e9928a/skills/task-decomposer)
- [skills.sh](https://skills.sh/)
- [Universal Capability Types Reference](artifact/references/capability_types.md)

## Skill Output:

**Output Type(s):** [analysis, markdown, shell commands, configuration, guidance, code]

**Output Format:** [Markdown with structured task decomposition reports, execution plans, YAML examples, and inline shell command blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include proposed third-party skill installation commands and generated skill templates for user review.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
